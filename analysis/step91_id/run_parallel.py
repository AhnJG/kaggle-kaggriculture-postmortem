import subprocess
import sys
import os
import time
import json

NUM_CHUNKS = 8
OUT_DIR = 'analysis/step91_id'
WORKER_SCRIPT = 'analysis/step91_id/worker.py'

def run():
    print(f"Starting {NUM_CHUNKS} parallel workers for step 91 bot identification...")
    t0 = time.time()
    processes = []
    for i in range(NUM_CHUNKS):
        cmd = [
            sys.executable,
            WORKER_SCRIPT,
            '--chunk-idx', str(i),
            '--num-chunks', str(NUM_CHUNKS),
            '--out-dir', OUT_DIR
        ]
        p = subprocess.Popen(cmd)
        processes.append((i, p))
        
    failed = False
    for i, p in processes:
        ret = p.wait()
        if ret != 0:
            print(f"Worker {i} failed with return code {ret}")
            failed = True
            
    if failed:
        print("Error: One or more workers failed!")
        sys.exit(1)
        
    t1 = time.time()
    print(f"All workers finished in {t1 - t0:.1f}s. Aggregating results...")
    
    # Merge results
    merged = {}
    for i in range(NUM_CHUNKS):
        chunk_file = os.path.join(OUT_DIR, f"result_chunk_{i}.json")
        with open(chunk_file, 'r') as f:
            chunk_data = json.load(f)
        for sha, data in chunk_data.items():
            if sha not in merged:
                merged[sha] = {
                    'sha': sha,
                    'dir_name': data['dir_name'],
                    'author': data['author'],
                    'path': data['path'],
                    'last_callable': data.get('last_callable', 'unknown'),
                    'matches_143': 0,
                    'matches_400': 0,
                    'matches_full': 0,
                    'per_episode': {}
                }
            merged[sha]['matches_143'] += data['matches_143']
            merged[sha]['matches_400'] += data['matches_400']
            merged[sha]['matches_full'] += data['matches_full']
            merged[sha]['per_episode'].update(data['per_episode'])
            
    summary_path = os.path.join(OUT_DIR, 'summary.json')
    with open(summary_path, 'w') as f:
        json.dump(merged, f, indent=2)
    print(f"Merged results saved to {summary_path}")
    
    # Print sorted table
    sorted_cands = sorted(merged.values(), key=lambda x: (x['matches_full'], x['matches_400'], x['matches_143']), reverse=True)
    
    print("\n" + "="*95)
    print(f"{'SHA':<12} | {'Matches 143':<12} | {'Matches 400':<12} | {'Matches FULL':<12} | {'Callable':<15} | {'Candidate Name'}")
    print("-" * 95)
    for c in sorted_cands:
        print(f"{c['sha'][:10]:<12} | {c['matches_143']:<12} | {c['matches_400']:<12} | {c['matches_full']:<12} | {c['last_callable']:<15} | {c['dir_name']} ({c['author']})")
    print("="*95)
    
if __name__ == '__main__':
    run()
