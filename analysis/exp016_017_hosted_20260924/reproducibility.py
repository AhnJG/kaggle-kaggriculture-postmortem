import json
import os
import sys
from kaggle_environments import make

out_dir = 'analysis/exp016_017_hosted_20260924'
manifest_path = os.path.join(out_dir, 'manifest.json')

if not os.path.exists(manifest_path):
    print("No manifest.json found.")
    sys.exit(1)

with open(manifest_path, 'r') as f:
    manifest = json.load(f)

# Split by submission
manifest_16 = [m for m in manifest if m.get('submission_label') == 'EXP-016']
manifest_17 = [m for m in manifest if m.get('submission_label') == 'EXP-017']

print(f"Manifest contains: {len(manifest_16)} EXP-016 episodes, {len(manifest_17)} EXP-017 episodes.")

class ReplayOpponent:
    def __init__(self, steps, op_seat):
        self.steps = steps
        self.op_seat = op_seat
    def __call__(self, obs, config=None):
        step = obs['step']
        next_step = step + 1
        if next_step < len(self.steps):
            act = self.steps[next_step][self.op_seat].get('action')
            return act or {}
        return {}

sub_configs = [
    {
        "label": "EXP-016",
        "episodes": manifest_16[:5],
        "path": "releases/f0-c1-adv-exp016/main.py"
    },
    {
        "label": "EXP-017",
        "episodes": manifest_17[:5],
        "path": "releases/f0-omw-adv-exp017/main.py"
    }
]

all_passed_replay = True
results = []

for sc in sub_configs:
    label = sc["label"]
    bot_path = sc["path"]
    test_eps = sc["episodes"]
    
    print(f"\n--- Testing Reproducibility for {label} (5 episodes) ---")
    for ep in test_eps:
        ep_id = ep['id']
        path = ep['path']
        seat = ep['seat']
        op_seat = 1 - seat
        seed = ep['seed']
        op_team = ep.get('op_teamName')
        
        with open(path, 'r') as f:
            rdata = json.load(f)
        
        hosted_actions = [st[seat].get('action') for st in rdata['steps'][1:144]]
        
        # Test 1: with ReplayOpponent (true hosted environment reproduction)
        op_agent = ReplayOpponent(rdata['steps'], op_seat)
        env_rep = make('kaggriculture', configuration={'episodeSteps': 144, 'seed': seed})
        agents = [None, None]
        agents[seat] = bot_path
        agents[op_seat] = op_agent
        env_rep.run(agents)
        local_rep_actions = [st[seat].get('action') for st in env_rep.steps[1:]]
        match_rep = (hosted_actions == local_rep_actions)
        
        # Test 2: self-play [bot, bot]
        env_self = make('kaggriculture', configuration={'episodeSteps': 144, 'seed': seed})
        env_self.run([bot_path, bot_path])
        local_self_actions = [st[seat].get('action') for st in env_self.steps[1:]]
        match_self = (hosted_actions == local_self_actions)
        
        print(f"[{label}] Ep {ep_id} (seed {seed}, seat {seat}, vs '{op_team}'): ReplayOpponent match={match_rep}, SelfPlay match={match_self}")
        
        if not match_rep:
            all_passed_replay = False
            for i in range(len(hosted_actions)):
                if hosted_actions[i] != local_rep_actions[i]:
                    print(f"  [ReplayOpponent Mismatch] Step {i+1}: hosted={hosted_actions[i]}, local={local_rep_actions[i]}")
                    break
        
        results.append({
            "submission": label,
            "episode": ep_id,
            "seed": seed,
            "seat": seat,
            "op_team": op_team,
            "replay_match": match_rep,
            "self_play_match": match_self,
            "matched_steps_replay": 143 if match_rep else None
        })

summary_report = {
    "all_passed": all_passed_replay,
    "total_tested": len(results),
    "replay_opponent_passed": sum(1 for r in results if r["replay_match"]),
    "self_play_passed": sum(1 for r in results if r["self_play_match"]),
    "checks": results
}

with open(os.path.join(out_dir, 'reproducibility.json'), 'w') as f:
    json.dump(summary_report, f, indent=2)

if not all_passed_replay:
    print("\nBLOCKED: replay not reproducible.")
    sys.exit(2)
else:
    print(f"\nREPRODUCIBILITY CHECK PASSED ({summary_report['replay_opponent_passed']}/{len(results)} with ReplayOpponent, {summary_report['self_play_passed']}/{len(results)} self-play).")
    sys.exit(0)
