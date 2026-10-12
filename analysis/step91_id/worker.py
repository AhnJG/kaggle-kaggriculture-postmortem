import os
import json
import csv
import hashlib
import glob
import time
import argparse
import sys
from kaggle_environments import make, agent

OUR_BOT_PATHS = {
    'EXP-016': 'releases/f0-c1-adv-exp016/main.py',
    'EXP-017': 'releases/f0-omw-adv-exp017/main.py'
}

RAW_REPLAY_DIR = 'private_artifacts/exp016_017_hosted_20260924/raw'

def get_candidates():
    scans = {}
    for dt in ['20260922', '20260924']:
        for fn in ['new.json', 'lineage.json', 'different.json']:
            p = f'analysis/daily_scan/{dt}/{fn}'
            if os.path.exists(p):
                with open(p) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            slug = item.get('slug') or item.get('kernel_slug') or item.get('title')
                            if slug:
                                scans[slug] = item

    files = glob.glob('analysis/daily_scan/20260922/extracted/*/main.py') + glob.glob('analysis/daily_scan/20260924/extracted/*/main.py')
    cl_candidates = {}
    for f in sorted(files):
        with open(f, 'rb') as fp:
            c = fp.read()
        if b'_CL_INSTALL' in c:
            norm_c = c.replace(b'\r\n', b'\n')
            sha = hashlib.sha256(norm_c).hexdigest()
            dir_name = os.path.basename(os.path.dirname(f))
            scan_info = scans.get(dir_name, {})
            author = scan_info.get('author') or scan_info.get('ref', '').split('/')[0] or 'unknown'
            if sha not in cl_candidates:
                cl_candidates[sha] = {
                    'sha': sha,
                    'path': f,
                    'dir_name': dir_name,
                    'author': author,
                    'kernel_ref': scan_info.get('ref', ''),
                    'version_number': scan_info.get('versionNumber') or scan_info.get('version_number') or 1
                }
    return cl_candidates

def get_hosted_actions(replay_path, op_seat):
    with open(replay_path, 'r') as f:
        rdata = json.load(f)
    steps = rdata.get('steps', [])
    actions = []
    for i in range(1, len(steps)):
        st = steps[i]
        if len(st) > op_seat:
            actions.append(st[op_seat].get('action'))
        else:
            actions.append(None)
    return actions

def get_target_episodes():
    csv_path = 'analysis/exp016_017_hosted_20260924/opponents.csv'
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r['prefix_len'] == '91']
    return rows

def test_match(seed, seat, our_callable, cand_callable, hosted_actions, max_steps):
    op_seat = 1 - seat
    env = make('kaggriculture', configuration={'episodeSteps': max_steps + 1, 'seed': seed})
    agents = [None, None]
    agents[seat] = our_callable
    agents[op_seat] = cand_callable
    env.run(agents)
    
    local_op_actions = [st[op_seat].get('action') for st in env.steps[1:]]
    match_len = 0
    limit = min(max_steps, len(local_op_actions), len(hosted_actions))
    for i in range(limit):
        if local_op_actions[i] == hosted_actions[i]:
            match_len += 1
        else:
            break
    return match_len

def run_worker(chunk_idx, num_chunks, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    candidates = get_candidates()
    episodes = get_target_episodes()
    
    # Assign episodes to this worker
    my_episodes = [ep for idx, ep in enumerate(episodes) if idx % num_chunks == chunk_idx]
    print(f"[Worker {chunk_idx}] Assigned {len(my_episodes)} episodes out of {len(episodes)} total.")
    
    # Pre-compile our bots
    our_callables = {}
    for name, path in OUR_BOT_PATHS.items():
        with open(path, 'r') as f:
            code = f.read()
        our_callables[name] = agent.get_last_callable(code, path=path)
        
    # Pre-compile candidate callables
    print(f"[Worker {chunk_idx}] Pre-compiling {len(candidates)} candidate callables...")
    cand_callables = {}
    cand_callable_names = {}
    for sha, cand in candidates.items():
        with open(cand['path'], 'r') as f:
            code = f.read()
        fn = agent.get_last_callable(code, path=cand['path'])
        cand_callables[sha] = fn
        cand_callable_names[sha] = getattr(fn, '__name__', str(fn))
    print(f"[Worker {chunk_idx}] Finished pre-compiling.")
    
    # Pre-cache hosted actions for assigned episodes
    ep_data = []
    for ep in my_episodes:
        ep_id = ep['episode']
        seed = int(ep['seed'])
        seat = int(ep['seat'])
        op_seat = 1 - seat
        sub_label = ep['submission_label']
        our_fn = our_callables[sub_label]
        replay_path = os.path.join(RAW_REPLAY_DIR, f"episode-{ep_id}-replay.json")
        hosted_actions = get_hosted_actions(replay_path, op_seat)
        ep_data.append({
            'episode': ep_id,
            'seed': seed,
            'seat': seat,
            'our_fn': our_fn,
            'hosted_actions': hosted_actions
        })
        
    results = {}
    for sha, cand in candidates.items():
        results[sha] = {
            'sha': sha,
            'dir_name': cand['dir_name'],
            'author': cand['author'],
            'path': cand['path'],
            'last_callable': cand_callable_names[sha],
            'matches_143': 0,
            'matches_400': 0,
            'matches_full': 0,
            'per_episode': {}
        }

    t0 = time.time()
    for ep_idx, ep in enumerate(ep_data):
        ep_t0 = time.time()
        ep_id = ep['episode']
        seed = ep['seed']
        seat = ep['seat']
        our_fn = ep['our_fn']
        hosted_actions = ep['hosted_actions']
        
        for cand_idx, (sha, cand) in enumerate(candidates.items()):
            cand_fn = cand_callables[sha]
            # Step 1: test 143 steps
            m143 = test_match(seed, seat, our_fn, cand_fn, hosted_actions, 143)
            
            is_143 = (m143 == 143)
            is_400 = False
            is_full = False
            
            if is_143:
                # Step 2: test 400 steps
                m400 = test_match(seed, seat, our_fn, cand_fn, hosted_actions, 400)
                if m400 == 400:
                    is_400 = True
                    # Step 3: test FULL 719 steps
                    mfull = test_match(seed, seat, our_fn, cand_fn, hosted_actions, 719)
                    if mfull == 719:
                        is_full = True
            
            if is_143:
                results[sha]['matches_143'] += 1
            if is_400:
                results[sha]['matches_400'] += 1
            if is_full:
                results[sha]['matches_full'] += 1
                
            results[sha]['per_episode'][ep_id] = {
                'match_143': is_143,
                'match_400': is_400,
                'match_full': is_full
            }
            
        elapsed = time.time() - t0
        ep_time = time.time() - ep_t0
        print(f"[Worker {chunk_idx}] Completed {ep_idx+1}/{len(ep_data)} episodes (last ep took {ep_time:.2f}s, total {elapsed:.1f}s).")
        
    out_file = os.path.join(out_dir, f"result_chunk_{chunk_idx}.json")
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[Worker {chunk_idx}] Saved chunk results to {out_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--chunk-idx', type=int, required=True)
    parser.add_argument('--num-chunks', type=int, required=True)
    parser.add_argument('--out-dir', type=str, default='analysis/step91_id')
    args = parser.parse_args()
    
    run_worker(args.chunk_idx, args.num_chunks, args.out_dir)
