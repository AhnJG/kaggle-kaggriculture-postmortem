import json
import os
import sys
import csv
from kaggle_environments import make

csv_path = 'analysis/c1_hosted_20260921/opponents.csv'
raw_dir = 'private_artifacts/c1_hosted_20260921/raw'

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    matches = [row for row in reader if row['prefix_len'] == '53' and 'C1' in row['label']]

print(f"Found {len(matches)} matches to check.")

refs = {
    'OneMoreWheat': 'releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py',
    'SmallerMarket': 'releases/public-dmitriigluzdov-kaggriculture-a-smaller-market-shock-exact/main.py',
    'SmarterSales': 'releases/public-dmitriigluzdov-kaggriculture-more-wheat-smarter-sales-exact/main.py',
    'HerdSafe': 'releases/public-dmitriigluzdov-kaggriculture-herd-safe-sale-window-lb-2700-exact/main.py',
    'TwoCoins': 'releases/public-dmitriigluzdov-kaggriculture-two-coins-one-sheep-lb-2600-exact/main.py',
    '7TurnRescue': 'releases/public-dmitriigluzdov-kaggriculture-7-turn-rescue-historical-lb-2800-exact/main.py',
}

def get_hosted_actions(replay_path, seat):
    with open(replay_path, 'r') as f:
        rdata = json.load(f)
    steps = rdata.get('steps', [])
    actions = []
    for i in range(1, len(steps)):
        st = steps[i]
        if len(st) > seat:
            actions.append(st[seat].get('action'))
        else:
            actions.append(None)
    return actions

results = []
c1_path = 'releases/public-nathanjacob-pipe16-exact/main.py'

for match in matches:
    ep_id = match['episode']
    seed = int(match['seed'])
    seat = int(match['seat'])
    
    # Path is usually in raw_dir
    replay_path = os.path.join(raw_dir, f"episode-{ep_id}-replay.json")
    if not os.path.exists(replay_path):
        print(f"Replay {replay_path} not found.")
        continue
        
    op_seat = 1 - seat
    hosted_op_actions = get_hosted_actions(replay_path, op_seat)
    
    best_len = -1
    best_refs = []
    
    for r_name, r_path in refs.items():
        if not os.path.exists(r_path):
            print(f"{r_path} not found")
            continue
            
        env = make('kaggriculture', configuration={'episodeSteps': 144, 'seed': seed})
        agents = [None, None]
        agents[seat] = c1_path
        agents[op_seat] = r_path
        env.run(agents)
        
        local_op_actions = []
        for i in range(1, len(env.steps)):
            st = env.steps[i]
            local_op_actions.append(st[op_seat].get('action'))
            
        match_len = 0
        min_steps = min(143, len(local_op_actions), len(hosted_op_actions))
        for i in range(min_steps):
            if local_op_actions[i] == hosted_op_actions[i]:
                match_len += 1
            else:
                break
                
        if match_len > best_len:
            best_len = match_len
            best_refs = [r_name]
        elif match_len == best_len:
            best_refs.append(r_name)
            
    print(f"Match {ep_id}: best prefix len {best_len} with {best_refs}")
    results.append({
        'episode': ep_id,
        'best_len': best_len,
        'best_refs': best_refs
    })

# Summary
print("\n--- Summary ---")
from collections import defaultdict
summary = defaultdict(int)
for r in results:
    if r['best_len'] == 143:
        for ref in r['best_refs']:
            summary[ref] += 1
for k, v in summary.items():
    print(f"{k}: {v} matches with 143 length")
