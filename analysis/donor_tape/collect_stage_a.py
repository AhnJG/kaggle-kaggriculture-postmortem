#!/usr/bin/env python3
"""Collect stage A donor metadata for top 100 teams without downloading replays."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

def stamp():
    return datetime.now(timezone.utc).isoformat()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + '\n')
    return path

def get_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def test_rules():
    def trunc1(f):
        s = str(float(f))
        return s[:s.find('.')+2] if '.' in s else s + '.0'

    lb_score = 2831.912
    subs = [
        {'id': 1, 'publicScore': '2831.90'},
        {'id': 2, 'publicScore': '2831.89'}, # Not matching 2831.9
        {'id': 3, 'publicScore': None}
    ]
    matches = [s for s in subs if s.get('publicScore') is not None and trunc1(s['publicScore']) == trunc1(lb_score)]
    assert len(matches) == 1
    assert matches[0]['id'] == 1

    # Test episode window (rule 2-3 to 2-5)
    target_sub_id = 1
    # 6 episodes
    episodes_meta = []
    for i in range(6):
        episodes_meta.append({
            'id': 100 - i,
            'createTime': f"2026-09-18T10:0{i}:00Z",
            'agents': [
                {'submissionId': target_sub_id, 'teamId': 10, 'index': i % 2}, # alternating seats 0 and 1
                {'submissionId': 999, 'teamId': 20 + i, 'index': 1 - (i % 2)} # 6 different opponents
            ]
        })
    
    # Sort
    episodes_meta.sort(key=lambda e: (e['createTime'], e['id']), reverse=True)
    
    opponents = set()
    donor_seats = set()
    for e_meta in episodes_meta:
        for a in e_meta['agents']:
            if a.get('submissionId') == target_sub_id:
                donor_seats.add(a.get('index', 0))
            else:
                opponents.add(a.get('teamId'))
    
    assert len(opponents) >= 4
    assert 0 in donor_seats and 1 in donor_seats

    print("Test passed.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Run tests and exit')
    args = parser.parse_args()

    if args.test:
        test_rules()
        return 0

    out_dir = Path("analysis/donor_tape_20260919")
    if out_dir.exists():
        print(f"Directory {out_dir} already exists. Aborting.")
        return 1
    out_dir.mkdir(parents=True)

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    as_of = datetime.now(timezone.utc)
    
    import time
    try:
        lb_raw = api.competition_leaderboard_view('kaggriculture', page_size=100)
    except Exception:
        print("Rate limit on GetLeaderboard. Waiting 30s...")
        time.sleep(30)
        lb_raw = api.competition_leaderboard_view('kaggriculture', page_size=100)
        
    lb = [r.to_dict() for r in lb_raw][:100]
    
    write(out_dir / 'leaderboard.json', {'as_of': as_of.isoformat(), 'rows': lb})
    
    inventory = {
        'as_of': as_of.isoformat(),
        'teams': []
    }
    
    summary = {
        'status_counts': {},
        'eligible_1_60': 0,
        'estimated_stageB_replays': 0,
        'errors': []
    }
    
    eligible_1_60_teams = []
    reserve_61_100_teams = []
    
    for rank, team_dict in enumerate(lb, 1):
        teamId = team_dict['teamId']
        teamName = team_dict['teamName']
        score = float(team_dict['score'])
        
        entry = {
            'rank': rank,
            'team_id': teamId,
            'team_name': teamName,
            'score': score,
            'status': '',
            'target_submission': None,
            'episodes_window': []
        }
        
        if teamId == 16668610:
            entry['status'] = 'our_team'
            inventory['teams'].append(entry)
            summary['status_counts']['our_team'] = summary['status_counts'].get('our_team', 0) + 1
            print(f"Skipping our team rank {rank}")
            continue
            
        import time
        try:
            time.sleep(1) # delay to avoid rate limit
            try:
                subs_raw = api.competition_team_submissions(teamId)
            except Exception:
                # Retry once
                time.sleep(30)
                subs_raw = api.competition_team_submissions(teamId)
            
            subs = [s.to_dict() for s in subs_raw]
            write(out_dir / f"team-{teamId}.json", {'queried_at': stamp(), 'submissions': subs})
            
            def trunc1(f):
                s = str(float(f))
                return s[:s.find('.')+2] if '.' in s else s + '.0'

            target_subs = []
            for sub in subs:
                try:
                    if sub.get('publicScore') is not None:
                        sub_score = float(sub['publicScore'])
                        if trunc1(sub_score) == trunc1(score):
                            target_subs.append(sub)
                except (ValueError, TypeError):
                    pass
            
            if len(target_subs) != 1:
                entry['status'] = 'ambiguous_submission'
                inventory['teams'].append(entry)
                summary['status_counts']['ambiguous_submission'] = summary['status_counts'].get('ambiguous_submission', 0) + 1
                print(f"[{rank}] ambiguous_submission: len={len(target_subs)}")
                continue
                
            target_sub = target_subs[0]
            entry['target_submission'] = target_sub['id']
            
            try:
                time.sleep(1)
                eps_raw = api.competition_list_episodes(target_sub['id'])
            except Exception:
                time.sleep(30)
                eps_raw = api.competition_list_episodes(target_sub['id'])
                
            eps = [e.to_dict() for e in eps_raw]
            write(out_dir / f"submission-{target_sub['id']}.json", {'queried_at': stamp(), 'episodes': eps})
            
            valid_eps = []
            for e in eps:
                if 'COMPLETED' in str(e.get('state')) and str(e.get('type')).endswith('EPISODE_TYPE_PUBLIC'):
                    valid_eps.append(e)
            
            valid_eps.sort(key=lambda e: (e['createTime'], e['id']), reverse=True)
            
            latest_12 = valid_eps[:12]
            
            episodes_metadata = []
            for e in latest_12:
                agents = e.get('agents', [])
                meta = {
                    'id': e['id'],
                    'createTime': e['createTime'],
                    'endTime': e.get('endTime'),
                    'agents': []
                }
                for a in agents:
                    meta['agents'].append({
                        'submissionId': a.get('submissionId'),
                        'teamId': a.get('teamId'),
                        'teamName': a.get('teamName'),
                        'index': a.get('index', 0),
                        'reward': a.get('reward')
                    })
                episodes_metadata.append(meta)
                
            window_6 = episodes_metadata[:6]
            entry['episodes_window'] = window_6
            
            if len(window_6) < 6:
                entry['status'] = 'insufficient_episodes'
                inventory['teams'].append(entry)
                summary['status_counts']['insufficient_episodes'] = summary['status_counts'].get('insufficient_episodes', 0) + 1
                print(f"[{rank}] insufficient_episodes")
                continue
                
            opponents = set()
            donor_seats = set()
            for e_meta in window_6:
                for a in e_meta['agents']:
                    if a.get('submissionId') == target_sub['id']:
                        donor_seats.add(a.get('index', 0))
                    else:
                        opponents.add(a.get('teamId'))
            
            if len(opponents) >= 4 and 0 in donor_seats and 1 in donor_seats:
                entry['status'] = 'eligible'
                if rank <= 60:
                    eligible_1_60_teams.append(entry)
                else:
                    reserve_61_100_teams.append(entry)
                print(f"[{rank}] eligible")
            else:
                entry['status'] = 'ineligible_diversity'
                entry['diversity_actual'] = {'opponents_count': len(opponents), 'donor_seats': list(donor_seats)}
                print(f"[{rank}] ineligible_diversity: ops={len(opponents)}, seats={list(donor_seats)}")
                
            inventory['teams'].append(entry)
            summary['status_counts'][entry['status']] = summary['status_counts'].get(entry['status'], 0) + 1
            
        except Exception as exc:
            entry['status'] = 'error'
            entry['error_msg'] = str(exc)
            inventory['teams'].append(entry)
            summary['status_counts']['error'] = summary['status_counts'].get('error', 0) + 1
            summary['errors'].append({'team_id': teamId, 'error_type': type(exc).__name__, 'msg': str(exc)})
            print(f"[{rank}] error: {exc}")
            
    selection = {
        'as_of': as_of.isoformat(),
        'rule': 'Select top 60 eligible teams. If <5, add from reserve_61_100. Select latest 2 episodes from the 6-episode window.',
        'selected_teams': [],
        'added_from_reserve': False,
        'reserve_added_teams': []
    }
    
    selected_teams_pool = eligible_1_60_teams.copy()
    if len(selected_teams_pool) < 5:
        selection['added_from_reserve'] = True
        needed = 5 - len(selected_teams_pool)
        added = reserve_61_100_teams[:needed]
        selected_teams_pool.extend(added)
        selection['reserve_added_teams'] = [t['team_id'] for t in added]
        
    for t in selected_teams_pool:
        selection['selected_teams'].append({
            'rank': t['rank'],
            'team_id': t['team_id'],
            'target_submission': t['target_submission'],
            'episodes': t['episodes_window'][:2]
        })
        
    summary['eligible_1_60'] = len(eligible_1_60_teams)
    summary['estimated_stageB_replays'] = sum(len(t['episodes']) for t in selection['selected_teams'])
    
    assert summary['estimated_stageB_replays'] <= 120, "Too many replays selected"
    
    for st in selection['selected_teams']:
        team_entry = next(t for t in inventory['teams'] if t['team_id'] == st['team_id'])
        assert st['episodes'] == team_entry['episodes_window'][:2]
        
    write(out_dir / 'inventory.json', inventory)
    write(out_dir / 'selection_stageB.json', selection)
    write(out_dir / 'summary.json', summary)
    
    hashes = {}
    for p in out_dir.iterdir():
        if p.is_file() and p.name != 'file_hashes.json':
            hashes[p.name] = get_hash(p)
            
    write(out_dir / 'file_hashes.json', hashes)
    print("Done. summary:", summary)
    return 0

if __name__ == '__main__':
    exit(main())
