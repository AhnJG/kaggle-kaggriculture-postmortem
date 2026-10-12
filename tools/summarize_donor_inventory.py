#!/usr/bin/env python3
"""Validate frozen donor metadata and reproduction outputs; write compact evidence."""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    root = args.directory
    read = lambda name: json.loads((root / name).read_text())
    inv, selection, downloads = read('inventory.json'), read('selection.json'), read('downloads.json')
    assert not inv['errors'] and len(inv['teams']) == 10
    assert len(selection['selected']) == len(downloads) == 6
    as_of = datetime.fromisoformat(inv['as_of'])
    rows = []
    metadata_cells = 0
    excluded = []
    eligible_ids = set()
    for team in inv['teams']:
        episodes = []
        for sub in team['submissions']:
            assert sub['eligible_count'] == len(sub['episodes'])
            for e in sub['episodes']:
                if datetime.fromisoformat(e['endTime']) > as_of:
                    excluded.append({'submission_id': sub['submission']['id'], 'episode_id': e['id'], 'reason': 'completed after frozen snapshot'})
                    continue
                eligible_ids.add(e['id'])
                a = next(a for a in e['agents'] if a['submissionId'] == sub['submission']['id'])
                assert a['teamId'] == team['leaderboard']['teamId']
                episodes.append(e['id'])
        metadata_cells += len(episodes)
        rows.append({'rank': team['rank'], 'team': team['leaderboard']['teamName'],
                     'team_id': team['leaderboard']['teamId'], 'score': team['leaderboard']['score'],
                     'submissions': [{'id': s['submission']['id'], 'score': s['submission']['publicScore'],
                                      'eligible_episodes': sum(datetime.fromisoformat(e['endTime']) <= as_of for e in s['episodes'])} for s in team['submissions']],
                     'unique_episodes': len(set(episodes))})
    results, enriched = {}, []
    for selected, d in zip(selection['selected'], downloads):
        assert selected['episode']['id'] == d['episode']['id'] and selected['submission_id'] == d['submission_id']
        eid = d['episode']['id']
        raw = Path(d['path'])
        assert sha(raw) == d['sha256']
        assert datetime.fromisoformat(d['episode']['endTime']) <= as_of
        agents = d['episode']['agents']
        donor = next(a for a in agents if a['submissionId'] == d['submission_id'])
        other = next(a for a in agents if a.get('index', 0) != d['seat'])
        assert donor['teamId'] == d['team_id'] and donor.get('index', 0) == d['seat']
        result = read(f'reproduction/{eid}.json')
        assert result['replay_sha256'] == d['sha256'] and result['verdict'] == 'PASS'
        assert result['runner_sha256'] == sha(Path('tools/reproduce_replay.py'))
        results[eid] = result
        own, opp = d['rewards'][d['seat']], d['rewards'][1-d['seat']]
        enriched.append({**d, 'opponent_submission_id': other['submissionId'],
                         'result': 'W' if own > opp else 'D' if own == opp else 'L',
                         'reproduction_verdict': result['verdict'],
                         'allocation': 'development/reproduction; not independent holdout'})
    summary = {'verdict': 'PASS', 'as_of': inv['as_of'], 'cutoff': inv['cutoff'], 'teams': rows,
               'metadata_submission_episode_rows': metadata_cells, 'unique_inventory_episodes': len(eligible_ids), 'excluded_metadata_rows': excluded,
               'donor_views': len(enriched), 'unique_downloaded_episodes': len(results),
               'total_download_bytes': sum(Path(next(d['path'] for d in downloads if d['episode']['id'] == e)).stat().st_size for e in results),
               'action_matches': sum(r['action_matches'] for r in results.values()),
               'state_matches': sum(r['state_matches'] for r in results.values()),
               'reproduction_episodes': list(results), 'donor_outcomes': {},
               'limits': ['API-returned active submission histories, not all historical submissions.',
                          'Team snapshot and per-submission scores queried sequentially.',
                          'Original-game reproduction does not establish a donor policy or new-opponent performance.',
                          'Development episodes are not a held-out evaluation set.',
                          'Replay redistribution/license scope not independently established; raw files remain private.']}
    for name in sorted({d['team_name'] for d in enriched}):
        ds = [d for d in enriched if d['team_name'] == name]
        summary['donor_outcomes'][name] = {'wdl': dict(Counter(d['result'] for d in ds)),
                                        'exact_action_variants': len({d['action_sha256'] for d in ds})}
    for name, value in [('donor_manifest.json', enriched), ('summary.json', summary)]:
        (root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    paths = sorted(root.glob('*.json')) + sorted((root/'reproduction').glob('*.json'))
    manifest = {str(p): sha(p) for p in paths if p.name != 'file_hashes.json'}
    (root/'file_hashes.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['teams','limits']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
