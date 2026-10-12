import json
import os
import subprocess
import hashlib
from pathlib import Path

def raw_read(path):
    if str(path).endswith('.gz'):
        import gzip
        with gzip.open(path, 'rt') as f:
            return json.load(f)
    with open(path, 'r') as f:
        return json.load(f)

with open('experiments/p4_20260926/episodes.json', 'r') as f:
    episodes = json.load(f)

with open('analysis/exp016_017_hosted_20260924/manifest.json', 'r') as f:
    manifest = json.load(f)
manifest_map = {m['id']: m for m in manifest}

os.makedirs('experiments/p4_20260926/tapes', exist_ok=True)
source_a = [e for e in episodes if e['source'] == 'A'][:10]

success = True
for ep in source_a:
    eid = ep['id']
    meta = manifest_map[eid]
    sub_label = meta['submission_label'].replace('-', '')
    candidate = f"experiments/search_20260925/historical/{sub_label}/main.py"
    
    our_seat = meta['seat']
    opp_seat = 1 - our_seat
    raw_path = meta['path']
    raw_sha = ep['raw_sha256']
    
    # Create tape
    tape_path = f"experiments/p4_20260926/tapes/{raw_sha[:20]}-{opp_seat}.py"
    if not os.path.exists(tape_path):
        raw_data = raw_read(raw_path)
        actions = [s[opp_seat]['action'] for s in raw_data['steps'][1:]]
        content = 'import copy\n_TAPE = ' + repr(actions) + '\ndef agent(obs, configuration=None):\n    return copy.deepcopy(_TAPE[int(obs["step"])])\n'
        with open(tape_path, 'w') as f:
            f.write(content)
            
    expected_our_reward = meta['our_reward']
    
    # Run closed
    closed_cmd = [
        "python3", "tools/dp_counterfactual.py",
        "--phase", "game",
        "--candidate", candidate,
        "--opponent", ep['opp_path'],
        "--seed", str(meta['seed']),
        "--seat", str(our_seat),
        "--output", f"experiments/p4_20260926/tmp_gate0_closed_{eid}.json"
    ]
    subprocess.run(closed_cmd, check=True)
    with open(f"experiments/p4_20260926/tmp_gate0_closed_{eid}.json", 'r') as f:
        res_closed = json.load(f)
    if res_closed['rewards'][our_seat] != expected_our_reward:
        print(f"Gate 0 FAIL closed mode for episode {eid}: expected {expected_our_reward}, got {res_closed['rewards'][our_seat]}")
        success = False
        break

    # Run open
    open_cmd = [
        "python3", "tools/dp_counterfactual.py",
        "--phase", "game",
        "--candidate", candidate,
        "--opponent", tape_path,
        "--seed", str(meta['seed']),
        "--seat", str(our_seat),
        "--output", f"experiments/p4_20260926/tmp_gate0_open_{eid}.json"
    ]
    subprocess.run(open_cmd, check=True)
    with open(f"experiments/p4_20260926/tmp_gate0_open_{eid}.json", 'r') as f:
        res_open = json.load(f)
    if res_open['rewards'][our_seat] != expected_our_reward:
        print(f"Gate 0 FAIL open mode for episode {eid}: expected {expected_our_reward}, got {res_open['rewards'][our_seat]}")
        success = False
        break

    print(f"Gate 0 PASS for episode {eid}")

if success:
    print("Gate 0 SUCCESS for all 10 episodes.")
    with open('experiments/p4_20260926/gate_0_result.txt', 'w') as f:
        f.write("PASS\n")
else:
    with open('experiments/p4_20260926/gate_0_result.txt', 'w') as f:
        f.write("FAIL\n")
