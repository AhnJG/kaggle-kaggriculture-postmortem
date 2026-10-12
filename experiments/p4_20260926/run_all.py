import json
import os
import subprocess
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor

def raw_read(path):
    if str(path).endswith('.gz'):
        import gzip
        with gzip.open(path, 'rt') as f:
            return json.load(f)
    with open(path, 'r') as f:
        return json.load(f)

with open('experiments/p4_20260926/episodes.json', 'r') as f:
    episodes = json.load(f)

# P and v000, v002, v004, v006, v008, v010
candidates = {
    'P': 'analysis/daily_scan/20260925/extracted/kaggriculture/main.py',
    'v000': 'experiments/exp023_mirror_screen/variants/v000.py',
    'v002': 'experiments/exp023_mirror_screen/variants/v002.py',
    'v004': 'experiments/exp023_mirror_screen/variants/v004.py',
    'v006': 'experiments/exp023_mirror_screen/variants/v006.py',
    'v008': 'experiments/exp023_mirror_screen/variants/v008.py',
    'v010': 'experiments/exp023_mirror_screen/variants/v010.py',
}

os.makedirs('experiments/p4_20260926/tapes', exist_ok=True)
os.makedirs('experiments/p4_20260926/tmp', exist_ok=True)

# Generate jobs
jobs = []
for ep in episodes:
    eid = ep['id']
    our_seat = ep['seat']
    opp_seat = 1 - our_seat
    seed = ep['seed']
    raw_sha = ep['raw_sha256']
    
    # Tape path
    tape_path = f"experiments/p4_20260926/tapes/{raw_sha[:20]}-{opp_seat}.py"
    if not os.path.exists(tape_path):
        raw_data = raw_read(ep['raw_path'])
        actions = [s[opp_seat]['action'] for s in raw_data['steps'][1:]]
        content = 'import copy\n_TAPE = ' + repr(actions) + '\ndef agent(obs, configuration=None):\n    return copy.deepcopy(_TAPE[int(obs["step"])])\n'
        with open(tape_path, 'w') as f:
            f.write(content)

    for cand_name, cand_path in candidates.items():
        # closed
        jobs.append({
            'episode': eid,
            'source': ep['source'],
            'candidate_name': cand_name,
            'mode': 'closed',
            'candidate': cand_path,
            'opponent': ep['opp_path'],
            'seed': seed,
            'seat': our_seat
        })
        # open
        jobs.append({
            'episode': eid,
            'source': ep['source'],
            'candidate_name': cand_name,
            'mode': 'open',
            'candidate': cand_path,
            'opponent': tape_path,
            'seed': seed,
            'seat': our_seat
        })

print(f"Total jobs generated: {len(jobs)}")

# Read already finished jobs to skip them
finished_keys = set()
games_file = 'experiments/p4_20260926/games.jsonl'
if os.path.exists(games_file):
    with open(games_file, 'r') as f:
        for line in f:
            if not line.strip(): continue
            try:
                data = json.loads(line)
                key = (data['episode'], data['candidate_name'], data['mode'])
                finished_keys.add(key)
            except Exception:
                pass
print(f"Already finished: {len(finished_keys)}")

jobs_to_run = [j for j in jobs if (j['episode'], j['candidate_name'], j['mode']) not in finished_keys]
print(f"Jobs to run: {len(jobs_to_run)}")

def run_job(j):
    out_path = f"experiments/p4_20260926/tmp/out_{j['episode']}_{j['candidate_name']}_{j['mode']}.json"
    cmd = [
        "python3", "tools/dp_counterfactual.py",
        "--phase", "game",
        "--candidate", j['candidate'],
        "--opponent", j['opponent'],
        "--seed", str(j['seed']),
        "--seat", str(j['seat']),
        "--output", out_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(out_path, 'r') as f:
            res = json.load(f)
        
        row = {
            'episode': j['episode'],
            'source': j['source'],
            'candidate_name': j['candidate_name'],
            'mode': j['mode'],
            'rewards': res['rewards'],
            'margin': res['margin'],
            'score': res['score'],
            'timing': res['timing'],
            'exceptions': res['exceptions']
        }
        # Append atomically to games.jsonl
        # Python's a+ with small write is mostly atomic on POSIX, but let's be careful.
        json_line = json.dumps(row) + "\n"
        with open(games_file, 'a') as f:
            f.write(json_line)
            
        os.remove(out_path)
    except Exception as e:
        print(f"Job failed: {j} with error: {e}")

# Run max 2 concurrently
with ThreadPoolExecutor(max_workers=2) as executor:
    list(executor.map(run_job, jobs_to_run))

print("All jobs completed.")
