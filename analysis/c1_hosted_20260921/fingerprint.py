import json
import os
import sys
import csv
from collections import defaultdict
from kaggle_environments import make

out_dir = 'analysis/c1_hosted_20260921'
raw_dir = 'private_artifacts/c1_hosted_20260921/raw'

manifest_path = os.path.join(out_dir, 'manifest.json')
if not os.path.exists(manifest_path):
    print("No manifest.json found")
    sys.exit(1)

with open(manifest_path, 'r') as f:
    manifest = json.load(f)

if not manifest:
    print("Manifest is empty")
    sys.exit(1)

refs = {
    'C1': 'releases/public-nathanjacob-pipe16-exact/main.py',
    'C2': 'releases/public-thomastschinkel-metav4-v13-exact/main.py',
    'C3': 'releases/public-thomastschinkel-2945-farm-exact/main.py',
    'C4': 'releases/public-ozer-v53-exact/main.py',
    'C5': 'releases/public-ozer-v51-exact/main.py',
    'P2': 'releases/public-lynnsakurai-farming-score-v2-exact/main.py',
    'yhay81': 'releases/public-yhay81-shop-router-0909-exact/main.py'
}

# Ensure all refs exist
for k, v in refs.items():
    if not os.path.exists(v):
        print(f"Warning: reference {k} file {v} not found.")

def get_hosted_actions(replay_path, seat):
    with open(replay_path, 'r') as f:
        rdata = json.load(f)
    steps = rdata.get('steps', [])
    actions = []
    # steps[0] is initial state. steps[1] to steps[719] have actions.
    # We collect up to step 719 (719 actions).
    for i in range(1, len(steps)):
        st = steps[i]
        if len(st) > seat:
            actions.append(st[seat].get('action'))
        else:
            actions.append(None)
    return actions

print("1. Control Check (5 episodes C1 vs C1)")
# Select up to 5 episodes
test_episodes = manifest[:5]

c1_path = refs['C1']

for ep in test_episodes:
    ep_id = ep['id']
    seed = ep['seed']
    seat = ep['seat']
    path = ep['path']
    
    with open(path, 'r') as f:
        rdata = json.load(f)
    seed = rdata.get('info', {}).get('seed')
    
    print(f"Testing {ep_id} seed {seed} seat {seat}...")
    
    # Run locally C1 vs C1
    env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed})
    # To run identical seed correctly with agents
    # The environment will pass obs to agents
    env.run([c1_path, c1_path])
    
    local_actions = []
    for i in range(1, len(env.steps)):
        st = env.steps[i]
        local_actions.append(st[seat].get('action'))
        
    hosted_actions = get_hosted_actions(path, seat)
    
    # Compare step 1~143 (which is index 0~142 in actions list)
    min_len = min(143, len(local_actions), len(hosted_actions))
    for i in range(min_len):
        if local_actions[i] != hosted_actions[i]:
            print(f"BLOCKED: replay not reproducible. Mismatch at step {i+1} for episode {ep_id}")
            print(f"Local: {local_actions[i]}")
            print(f"Hosted: {hosted_actions[i]}")
            sys.exit(0) # We exit normally but with BLOCKED report later

print("Control Check Passed.")

# 2. Fingerprinting
print("2. Fingerprinting opponents...")
results = []

for ep in manifest:
    ep_id = ep['id']
    seed = ep['seed']
    seat = ep['seat']
    path = ep['path']
    result_code = ep['result']
    margin = ep.get('margin', 0)
    
    with open(path, 'r') as f:
        rdata = json.load(f)
    seed = rdata.get('info', {}).get('seed')

    # get opponent team name from episodes_all.json
    # We can just read episodes_all.json once, or do it here
    op_seat = 1 - seat
    hosted_op_actions = get_hosted_actions(path, op_seat)
    
    best_len = -1
    best_refs = []
    mirror_exact = False
    
    for r_name, r_path in refs.items():
        if not os.path.exists(r_path): continue
        if r_name == 'C1':
            env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed})
        else:
            env = make('kaggriculture', configuration={'episodeSteps': 144, 'seed': seed})
        agents = [None, None]
        agents[seat] = c1_path
        agents[op_seat] = r_path
        env.run(agents)
        
        local_op_actions = []
        for i in range(1, len(env.steps)):
            st = env.steps[i]
            local_op_actions.append(st[op_seat].get('action'))
            
        # find prefix length
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
            
        # Check MIRROR_EXACT
        if r_name == 'C1':
            all_match = True
            for i in range(min(719, len(local_op_actions), len(hosted_op_actions))):
                if local_op_actions[i] != hosted_op_actions[i]:
                    all_match = False
                    break
            if all_match and len(local_op_actions) == len(hosted_op_actions):
                mirror_exact = True

    label = "UNKNOWN"
    if best_len == 143:
        if len(best_refs) == 1:
            label = best_refs[0]
        else:
            label = "|".join(best_refs)
    else:
        label = f"UNKNOWN ({best_len} with {'|'.join(best_refs)})"
        
    results.append({
        'episode': ep_id,
        'seed': seed,
        'seat': seat,
        'result': result_code,
        'margin': margin,
        'label': label,
        'prefix_len': best_len,
        'MIRROR_EXACT': mirror_exact
    })
    
# Add op_team to results
with open(os.path.join(out_dir, 'episodes_all.json'), 'r') as f:
    episodes_all = json.load(f)
    ep_to_team = {ep['id']: ep.get('op_teamName', 'Unknown') for ep in episodes_all}

for r in results:
    r['op_team'] = ep_to_team.get(r['episode'], 'Unknown')

# Write to CSV
csv_path = os.path.join(out_dir, 'opponents.csv')
with open(csv_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['episode', 'seed', 'seat', 'result', 'margin', 'op_team', 'label', 'prefix_len', 'MIRROR_EXACT'])
    writer.writeheader()
    writer.writerows(results)

print("Done fingerprinting.")
