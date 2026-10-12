import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta

out_dir = 'analysis/exp016_017_hosted_20260924'
csv_path = os.path.join(out_dir, 'opponents.csv')

if not os.path.exists(csv_path):
    print(f"Error: {csv_path} does not exist.")
    sys.exit(1)

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Loaded {len(rows)} rows from {csv_path}.")

# 1. Submission overall
sub_stats = defaultdict(lambda: {'total': 0, 'W': 0, 'L': 0, 'D': 0, 'mirror': 0})
for r in rows:
    sub = r['submission_label']
    res = r['result']
    sub_stats[sub]['total'] += 1
    sub_stats[sub][res] += 1
    if r['MIRROR_EXACT'] == 'True':
        sub_stats[sub]['mirror'] += 1

# 2. 12-hour intervals
# Parse endTime: e.g. "2026-09-24T06:55:50.411Z"
parsed_rows = []
for r in rows:
    et_str = r['endTime']
    # handle trailing Z
    et = datetime.fromisoformat(et_str.replace('Z', '+00:00'))
    parsed_rows.append((et, r))

parsed_rows.sort(key=lambda x: x[0])
min_time = parsed_rows[0][0]
max_time = parsed_rows[-1][0]

# Align start to 12-hour block (00:00 or 12:00 UTC)
start_block = min_time.replace(minute=0, second=0, microsecond=0)
if start_block.hour < 12:
    start_block = start_block.replace(hour=0)
else:
    start_block = start_block.replace(hour=12)

windows = []
curr_start = start_block
while curr_start <= max_time:
    curr_end = curr_start + timedelta(hours=12)
    windows.append((curr_start, curr_end))
    curr_start = curr_end

window_stats = []
for w_start, w_end in windows:
    w_label = f"{w_start.strftime('%m-%d %H:%M')} ~ {w_end.strftime('%m-%d %H:%M')} UTC"
    w_data = {'window': w_label, 'EXP-016': {'W': 0, 'L': 0, 'D': 0, 'total': 0}, 'EXP-017': {'W': 0, 'L': 0, 'D': 0, 'total': 0}}
    for dt, r in parsed_rows:
        if w_start <= dt < w_end:
            sub = r['submission_label']
            res = r['result']
            w_data[sub]['total'] += 1
            w_data[sub][res] += 1
    window_stats.append(w_data)

# 3. Label stats per submission
label_stats = {
    'EXP-016': defaultdict(lambda: {'count': 0, 'W': 0, 'L': 0, 'D': 0}),
    'EXP-017': defaultdict(lambda: {'count': 0, 'W': 0, 'L': 0, 'D': 0})
}

for r in rows:
    sub = r['submission_label']
    lbl = r['label']
    res = r['result']
    label_stats[sub][lbl]['count'] += 1
    label_stats[sub][lbl][res] += 1

# 4. Top 10 Opponent Teams among UNKNOWN that beat us
# For each submission and combined
def get_top_losses(sub_filter=None):
    team_losses = defaultdict(lambda: {'losses': 0, 'episodes': [], 'best_prefix': -1, 'closest_refs': set()})
    for r in rows:
        if sub_filter and r['submission_label'] != sub_filter:
            continue
        if r['label'].startswith('UNKNOWN') and r['result'] == 'L':
            team = r['op_team']
            team_losses[team]['losses'] += 1
            team_losses[team]['episodes'].append(r['episode'])
            p_len = int(r['prefix_len'])
            if p_len > team_losses[team]['best_prefix']:
                team_losses[team]['best_prefix'] = p_len
                # extract ref from label: UNKNOWN (XX with REFS)
                lbl = r['label']
                if 'with ' in lbl:
                    ref_part = lbl.split('with ')[1].rstrip(')')
                    team_losses[team]['closest_refs'] = {ref_part}
            elif p_len == team_losses[team]['best_prefix']:
                lbl = r['label']
                if 'with ' in lbl:
                    ref_part = lbl.split('with ')[1].rstrip(')')
                    team_losses[team]['closest_refs'].add(ref_part)
                    
    sorted_teams = sorted(team_losses.items(), key=lambda x: x[1]['losses'], reverse=True)
    return sorted_teams[:10]

top10_overall = get_top_losses(None)
top10_exp16 = get_top_losses('EXP-016')
top10_exp17 = get_top_losses('EXP-017')

# Save summary.json
summary_data = {
    "sub_stats": dict(sub_stats),
    "window_stats": window_stats,
    "top10_unknown_losses_overall": [
        {
            "team": team,
            "losses": data['losses'],
            "best_prefix": data['best_prefix'],
            "closest_refs": list(data['closest_refs'])
        }
        for team, data in top10_overall
    ]
}

with open(os.path.join(out_dir, 'summary_details.json'), 'w') as f:
    json.dump(summary_data, f, indent=2)

print("\n=== Submission Summary ===")
for sub, st in sub_stats.items():
    winrate = (st['W'] / st['total'] * 100) if st['total'] > 0 else 0
    ptrate = ((st['W'] + 0.5 * st['D']) / st['total'] * 100) if st['total'] > 0 else 0
    print(f"{sub}: Total={st['total']}, W={st['W']}, L={st['L']}, D={st['D']}, WinRate={winrate:.1f}%, PointRate={ptrate:.1f}%, Mirrors={st['mirror']}")

print("\n=== 12-Hour Window Stats ===")
for w in window_stats:
    print(f"[{w['window']}]")
    for sub in ['EXP-016', 'EXP-017']:
        d = w[sub]
        wr = (d['W'] / d['total'] * 100) if d['total'] > 0 else 0
        pr = ((d['W'] + 0.5 * d['D']) / d['total'] * 100) if d['total'] > 0 else 0
        print(f"  {sub}: Total={d['total']}, W={d['W']}, L={d['L']}, D={d['D']} (WinRate={wr:.1f}%, PointRate={pr:.1f}%)")

print("\n=== Top 10 UNKNOWN Teams that beat EXP-016 ===")
for team, data in top10_exp16:
    print(f"- {team}: {data['losses']} losses, prefix={data['best_prefix']}, refs={','.join(data['closest_refs'])}")

print("\n=== Top 10 UNKNOWN Teams that beat EXP-017 ===")
for team, data in top10_exp17:
    print(f"- {team}: {data['losses']} losses, prefix={data['best_prefix']}, refs={','.join(data['closest_refs'])}")
