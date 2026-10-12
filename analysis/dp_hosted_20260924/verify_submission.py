#!/usr/bin/env python3
"""Step 4: Verify that each of the 8 submissions matches releases/public-tetsutani-demand-preserving-0924-exact/main.py exactly over 720 steps."""

import os
import sys
import json
import gzip
import time
from kaggle_environments import make

OUT_DIR = "analysis/dp_hosted_20260924"
RAW_DIR = "private_artifacts/dp_hosted_20260924/raw"
DP_PATH = "releases/public-tetsutani-demand-preserving-0924-exact/main.py"

manifest_path = os.path.join(OUT_DIR, "download_manifest.json")
if not os.path.exists(manifest_path):
    print(f"Error: {manifest_path} does not exist.")
    sys.exit(1)

with open(manifest_path, "r", encoding="utf-8") as f:
    download_list = json.load(f)

# Group episodes by submission_id
by_sub = {}
for ep in download_list:
    sid = ep["submission_id"]
    by_sub.setdefault(sid, []).append(ep)

class ReplayOpponent:
    def __init__(self, steps, op_seat):
        self.steps = steps
        self.op_seat = op_seat
        
    def __call__(self, obs, config=None):
        step = obs["step"]
        next_step = step + 1
        if next_step < len(self.steps):
            act = self.steps[next_step][self.op_seat].get("action")
            return act or {}
        return {}

def test_episode_reproducibility(ep_record):
    eid = ep_record["id"]
    seat = int(ep_record["seat"])
    op_seat = 1 - seat
    seed = int(ep_record["seed"])
    sub_id = ep_record["submission_id"]
    team = ep_record.get("submission_team")
    
    gz_path = os.path.join(RAW_DIR, f"{eid}.json.gz")
    if not os.path.exists(gz_path):
        return {
            "episode": eid,
            "status": "ERROR",
            "error": "replay file missing"
        }
        
    with gzip.open(gz_path, "rt", encoding="utf-8") as f:
        rdata = json.load(f)
        
    steps = rdata.get("steps", [])
    if len(steps) != 720:
        print(f"Warning: episode {eid} has {len(steps)} steps instead of 720.")
        
    # Hosted actions for target submission
    hosted_actions = [st[seat].get("action") for st in steps[1:]]
    
    op_agent = ReplayOpponent(steps, op_seat)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    agents = [None, None]
    agents[seat] = DP_PATH
    agents[op_seat] = op_agent
    
    t0 = time.time()
    env.run(agents)
    elapsed = time.time() - t0
    
    local_actions = [st[seat].get("action") for st in env.steps[1:]]
    
    match = (hosted_actions == local_actions)
    mismatch_step = None
    mismatch_detail = None
    
    if not match:
        limit = min(len(hosted_actions), len(local_actions))
        for step_idx in range(limit):
            if hosted_actions[step_idx] != local_actions[step_idx]:
                mismatch_step = step_idx + 1  # 1-based step
                mismatch_detail = {
                    "hosted": hosted_actions[step_idx],
                    "local": local_actions[step_idx]
                }
                break
                
    return {
        "episode": eid,
        "submission_id": sub_id,
        "submission_team": team,
        "seed": seed,
        "seat": seat,
        "steps_count": len(local_actions),
        "match": match,
        "mismatch_step": mismatch_step,
        "mismatch_detail": mismatch_detail,
        "run_time_sec": round(elapsed, 2)
    }

results_by_sub = {}
total_mismatch_subs = 0

print("Step 4: Running 720-step reproducibility checks for all submissions (3 episodes each)...")
for sid, eps in by_sub.items():
    team_name = eps[0].get("submission_team", str(sid))
    # Pick 3 episodes
    test_eps = eps[:3]
    print(f"\n--- Testing submission {sid} ({team_name}): {len(test_eps)} episodes ---")
    
    sub_results = []
    sub_all_match = True
    for ep in test_eps:
        res = test_episode_reproducibility(ep)
        sub_results.append(res)
        print(f"  Ep {res['episode']} (seed {res['seed']}, seat {res['seat']}): match={res['match']} (time: {res.get('run_time_sec')}s)")
        if not res["match"]:
            sub_all_match = False
            print(f"    MISMATCH at step {res['mismatch_step']}: hosted={res['mismatch_detail']['hosted']} vs local={res['mismatch_detail']['local']}")
            
    if not sub_all_match:
        total_mismatch_subs += 1
        
    results_by_sub[sid] = {
        "submission_id": sid,
        "submission_team": team_name,
        "verified_same": sub_all_match,
        "match_count": sum(1 for r in sub_results if r.get("match")),
        "test_count": len(sub_results),
        "episodes": sub_results
    }

verify_path = os.path.join(OUT_DIR, "submission_verify.json")
with open(verify_path, "w", encoding="utf-8") as f:
    json.dump(results_by_sub, f, indent=2)
print(f"\nSaved verification results to {verify_path}")

print("\n--- Summary of Step 4 Verification ---")
for sid, v in results_by_sub.items():
    status_str = "PASS (3/3 MATCH)" if v["verified_same"] else f"FAIL ({v['match_count']}/{v['test_count']} MATCH)"
    print(f"Sub {sid} ({v['submission_team']}): {status_str}")

print(f"\nTotal submissions with mismatches: {total_mismatch_subs} / {len(results_by_sub)}")
if total_mismatch_subs >= 3:
    print(f"BLOCKED: {total_mismatch_subs} submissions mismatched (>= 3 threshold)!")
    sys.exit(4)
