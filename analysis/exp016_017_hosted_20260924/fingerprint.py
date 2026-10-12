import json
import os
import sys
import csv
import argparse
import time
import importlib.util
from kaggle_environments import make

out_dir = 'analysis/exp016_017_hosted_20260924'
raw_dir = 'private_artifacts/exp016_017_hosted_20260924/raw'

manifest_path = os.path.join(out_dir, 'manifest.json')
repro_path = os.path.join(out_dir, 'reproducibility.json')

refs = {
    'C1': 'releases/public-nathanjacob-pipe16-exact/main.py',
    'C2': 'releases/public-thomastschinkel-metav4-v13-exact/main.py',
    'C3': 'releases/public-thomastschinkel-2945-farm-exact/main.py',
    'C4': 'releases/public-ozer-v53-exact/main.py',
    'C5': 'releases/public-ozer-v51-exact/main.py',
    'P2': 'releases/public-lynnsakurai-farming-score-v2-exact/main.py',
    'OMW': 'releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py',
    'more-wheat-smarter-sales': 'releases/public-dmitriigluzdov-kaggriculture-more-wheat-smarter-sales-exact/main.py',
    '7-turn-rescue': 'releases/public-dmitriigluzdov-kaggriculture-7-turn-rescue-historical-lb-2800-exact/main.py',
    'a-smaller-market-shock': 'releases/public-dmitriigluzdov-kaggriculture-a-smaller-market-shock-exact/main.py',
    'EXP-016': 'releases/f0-c1-adv-exp016/main.py',
    'EXP-017': 'releases/f0-omw-adv-exp017/main.py',
    'multi-route': 'analysis/daily_scan/20260922/extracted/kaggriculture-multi-route-farming-agent/main.py',
    'v56-smarter': 'analysis/daily_scan/20260922/extracted/kaggriculture-v56-smarter-seeds-and-fertilizer/main.py',
    'harvest-ledger': 'analysis/daily_scan/20260922/extracted/kaggriculture-harvest-ledger/main.py',
    'order-book': 'analysis/daily_scan/20260922/extracted/your-market-list-is-an-order-book/main.py',
    'farmer-john': 'analysis/daily_scan/20260922/extracted/farmer-john-and-the-wheat-seller/main.py'
}

our_bot_paths = {
    'EXP-016': 'releases/f0-c1-adv-exp016/main.py',
    'EXP-017': 'releases/f0-omw-adv-exp017/main.py'
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

def run_chunk(chunk_idx, num_chunks):
    if not os.path.exists(repro_path):
        print(f"Error: {repro_path} does not exist. Run reproducibility check first.")
        sys.exit(1)
        
    with open(repro_path, 'r') as f:
        repro = json.load(f)
    if not repro.get('all_passed'):
        print("BLOCKED: reproducibility check did not pass.")
        sys.exit(2)
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    # Filter for chunk
    my_episodes = [ep for idx, ep in enumerate(manifest) if idx % num_chunks == chunk_idx]
    print(f"Chunk {chunk_idx}/{num_chunks}: Processing {len(my_episodes)} episodes (out of {len(manifest)} total)...")
    
    # Pre-load agents
    print("Pre-loading reference agents...")
    loaded_refs = {}
    for r_name, r_path in refs.items():
        if not os.path.exists(r_path):
            print(f"Warning: reference {r_name} ({r_path}) does not exist!")
            continue
        spec = importlib.util.spec_from_file_location(f"ref_{r_name}", r_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        loaded_refs[r_name] = mod.agent
        
    loaded_our_bots = {}
    for b_name, b_path in our_bot_paths.items():
        spec = importlib.util.spec_from_file_location(f"our_{b_name}", b_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        loaded_our_bots[b_name] = mod.agent
        
    results = []
    t_start = time.time()
    
    for count, ep in enumerate(my_episodes):
        ep_id = ep['id']
        sub_label = ep['submission_label']
        sub_id = ep['submission_id']
        seed = ep['seed']
        seat = ep['seat']
        op_seat = 1 - seat
        path = ep['path']
        res = ep['result']
        margin = ep['margin']
        op_team = ep.get('op_teamName', 'Unknown')
        end_time = ep.get('endTime')
        
        hosted_op_actions = get_hosted_actions(path, op_seat)
        our_agent = loaded_our_bots[sub_label]
        
        best_len = -1
        best_refs = []
        mirror_exact = False
        
        for r_name, r_agent in loaded_refs.items():
            env = make('kaggriculture', configuration={'episodeSteps': 144, 'seed': seed})
            agents = [None, None]
            agents[seat] = our_agent
            agents[op_seat] = r_agent
            env.run(agents)
            
            local_op_actions = [st[op_seat].get('action') for st in env.steps[1:]]
            
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
                
            # If match_len == 143 and r_name is our bot, check full 720 steps for MIRROR_EXACT
            if match_len == 143 and r_name == sub_label:
                env_720 = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed})
                env_720.run([our_agent, our_agent])
                local_op_720 = [st[op_seat].get('action') for st in env_720.steps[1:]]
                if local_op_720 == hosted_op_actions:
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
            'submission_id': sub_id,
            'submission_label': sub_label,
            'episode': ep_id,
            'seed': seed,
            'seat': seat,
            'result': res,
            'margin': margin,
            'op_team': op_team,
            'endTime': end_time,
            'label': label,
            'prefix_len': best_len,
            'MIRROR_EXACT': mirror_exact
        })
        
        if (count + 1) % 10 == 0 or (count + 1) == len(my_episodes):
            elapsed = time.time() - t_start
            rate = elapsed / (count + 1)
            remaining = rate * (len(my_episodes) - (count + 1))
            print(f"[Chunk {chunk_idx}] Done {count + 1}/{len(my_episodes)} in {elapsed:.1f}s (eta {remaining:.1f}s). Last label: {label}")
            
    part_path = os.path.join(out_dir, f"opponents_part_{chunk_idx}.json")
    with open(part_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Chunk {chunk_idx} complete. Saved {len(results)} rows to {part_path}.")

def merge_chunks(num_chunks):
    all_results = []
    for c in range(num_chunks):
        part_path = os.path.join(out_dir, f"opponents_part_{c}.json")
        if not os.path.exists(part_path):
            print(f"Error: missing part {part_path}")
            sys.exit(1)
        with open(part_path, 'r') as f:
            all_results.extend(json.load(f))
            
    # Sort by submission_label, endTime desc
    all_results.sort(key=lambda x: (x['submission_label'], x['endTime']), reverse=True)
    
    csv_path = os.path.join(out_dir, 'opponents.csv')
    fieldnames = ['submission_id', 'submission_label', 'episode', 'seed', 'seat', 'result', 'margin', 'op_team', 'endTime', 'label', 'prefix_len', 'MIRROR_EXACT']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
        
    print(f"Merged {len(all_results)} rows into {csv_path}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--chunk-idx', type=int, default=0)
    parser.add_argument('--num-chunks', type=int, default=1)
    parser.add_argument('--merge', action='store_true')
    args = parser.parse_args()
    
    if args.merge:
        merge_chunks(args.num_chunks)
    else:
        run_chunk(args.chunk_idx, args.num_chunks)
