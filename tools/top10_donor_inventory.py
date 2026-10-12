#!/usr/bin/env python3
"""Read Kaggle top-ten provenance; freeze selection before downloading six replays."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path


def stamp():
    return datetime.now(timezone.utc).isoformat()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--raw', type=Path, required=True)
    args = parser.parse_args()
    if (args.output / 'inventory.json').exists():
        parser.error('use a new output directory to preserve the frozen snapshot')
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    args.raw.mkdir(parents=True, exist_ok=True)
    as_of = datetime.now(timezone.utc)
    cutoff = as_of - timedelta(hours=72)
    lb = [r.to_dict() for r in api.competition_leaderboard_view('kaggriculture', page_size=10)]
    write(args.output / 'leaderboard.json', {'as_of': as_of.isoformat(), 'rows': lb})
    inventory = {'as_of': as_of.isoformat(), 'cutoff': cutoff.isoformat(),
                 'selection': 'Ranks 1 and 2; highest-scoring returned submission; latest 3 completed public episodes within 72h; no reward selection.',
                 'teams': [], 'selected': [], 'errors': []}
    for rank, team in enumerate(lb, 1):
        entry = {'rank': rank, 'leaderboard': team, 'submissions': []}
        inventory['teams'].append(entry)
        try:
            subs = [s.to_dict() for s in api.competition_team_submissions(team['teamId'])]
            write(args.output / f"team-{team['teamId']}.json", {'queried_at': stamp(), 'submissions': subs})
            for sub in subs:
                eps = [e.to_dict() for e in api.competition_list_episodes(sub['id'])]
                write(args.output / f"submission-{sub['id']}.json", {'queried_at': stamp(), 'episodes': eps})
                valid = []
                for e in eps:
                    when = datetime.fromisoformat(e['createTime']).replace(tzinfo=timezone.utc)
                    ended = datetime.fromisoformat(e['endTime']).replace(tzinfo=timezone.utc) if e.get('endTime') else as_of + timedelta(days=1)
                    if cutoff <= when <= as_of and ended <= as_of and 'COMPLETED' in str(e.get('state')) and str(e.get('type')).endswith('EPISODE_TYPE_PUBLIC'):
                        valid.append(e)
                valid.sort(key=lambda e: (e['createTime'], e['id']), reverse=True)
                entry['submissions'].append({'submission': sub, 'eligible_count': len(valid), 'episodes': valid})
            if rank <= 2:
                chosen = max(entry['submissions'], key=lambda x: float(x['submission']['publicScore']))
                for e in chosen['episodes'][:3]:
                    inventory['selected'].append({'rank': rank, 'team_id': team['teamId'], 'team_name': team['teamName'],
                       'submission_id': chosen['submission']['id'], 'episode': e,
                       'source': f"https://www.kaggle.com/competitions/kaggriculture/submissions?dialog=episodes-submission-{chosen['submission']['id']}"})
            print(rank, team['teamName'], [(s['submission']['id'], s['eligible_count']) for s in entry['submissions']], flush=True)
        except Exception as exc:
            inventory['errors'].append({'team_id': team['teamId'], 'error_type': type(exc).__name__})
        write(args.output / 'inventory.json', inventory)
    # Immutable pre-download selection, independently of observed game rewards.
    write(args.output / 'selection.json', {'as_of': as_of.isoformat(), 'rule': inventory['selection'], 'selected': inventory['selected']})
    downloads = []
    for item in inventory['selected']:
        eid = item['episode']['id']
        p = args.raw / f'episode-{eid}-replay.json'
        try:
            if not p.exists():
                api.competition_episode_replay(eid, path=str(args.raw), quiet=True)
            replay = json.loads(p.read_text())
            assert replay['info']['EpisodeId'] == eid
            names = replay['info']['TeamNames']
            assert names.count(item['team_name']) == 1
            seat = names.index(item['team_name'])
            agents = item['episode']['agents']
            donor = next(a for a in agents if a['submissionId'] == item['submission_id'])
            assert donor['teamId'] == item['team_id'] and donor.get('index', 0) == seat
            other = next(a for a in agents if a.get('index', 0) == 1-seat)
            actions = [s[seat]['action'] for s in replay['steps'][1:]]
            downloads.append({**item, 'path': str(p), 'bytes': p.stat().st_size,
                 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'downloaded_at': stamp(),
                 'seat': seat, 'opponent': names[1-seat], 'engine': replay['module_version'],
                 'seed': replay['info'].get('seed'), 'rewards': replay['rewards'],
                 'configuration': replay['configuration'], 'steps': len(replay['steps']),
                 'action_sha256': hashlib.sha256(json.dumps(actions, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                 'episode_rating': 'N/A', 'opponent_submission_id': other['submissionId']})
            print('downloaded', eid, p.stat().st_size, flush=True)
        except Exception as exc:
            downloads.append({**item, 'error_type': type(exc).__name__})
        write(args.output / 'downloads.json', downloads)
    if inventory['errors'] or len(downloads) != 6 or any('error_type' in d for d in downloads):
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
