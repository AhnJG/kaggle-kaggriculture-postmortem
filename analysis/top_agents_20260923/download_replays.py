import subprocess
import json
import re
import sys
import time
from pathlib import Path

TEAMS = [
    {
        "name": "DSM",
        "teamId": 16732748,
        "subId": 56468867,
        "score": 3157.3
    },
    {
        "name": "Majkel1337",
        "teamId": 16718819,
        "subId": 56459657,
        "score": 3066.0
    },
    {
        "name": "M & M & P & Q",
        "teamId": 16681125,
        "subId": 56464621,
        "score": 3065.3
    }
]

RAW_DIR = Path("private_artifacts/top_agents_20260923/raw")
ANALYSIS_DIR = Path("analysis/top_agents_20260923")
EPISODES_JSON = ANALYSIS_DIR / "episodes.json"

def get_episodes_for_sub(sub_id):
    res = subprocess.run(['kaggle', 'competitions', 'episodes', str(sub_id), '--format', 'json'], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error getting episodes for sub {sub_id}: {res.stderr}")
        return []
    match = re.search(r'\[\s*\{.*\}\s*\]', res.stdout, re.DOTALL)
    if not match:
        return []
    data = json.loads(match.group(0))
    # Filter completed public episodes
    completed_public = [
        e for e in data
        if e.get('state') == 'EpisodeState.COMPLETED' and e.get('type') == 'EpisodeType.EPISODE_TYPE_PUBLIC'
    ]
    # Sort by createTime descending (latest first)
    completed_public.sort(key=lambda x: x.get('createTime', ''), reverse=True)
    return completed_public

def download_replay(ep_id):
    cand1 = RAW_DIR / f"episode-{ep_id}-replay.json"
    cand2 = RAW_DIR / f"{ep_id}.json"
    if cand1.exists() and cand1.stat().st_size > 1000:
        return cand1
    if cand2.exists() and cand2.stat().st_size > 1000:
        return cand2
    
    cmd = ['kaggle', 'competitions', 'replay', str(ep_id), '-p', str(RAW_DIR)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Failed to download episode {ep_id}: {res.stderr}")
        return None
    time.sleep(1.0) # rate limit delay
    if cand1.exists():
        return cand1
    if cand2.exists():
        return cand2
    # check any file with ep_id in RAW_DIR
    for p in RAW_DIR.glob(f"*{ep_id}*"):
        return p
    return None

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    episodes_meta = []
    total_target = 0
    
    for t in TEAMS:
        print(f"Fetching episodes for {t['name']} (sub {t['subId']})...")
        eps = get_episodes_for_sub(t['subId'])
        print(f"Found {len(eps)} completed public episodes for {t['name']}")
        selected_eps = eps[:40] # up to 40 per team
        total_target += len(selected_eps)
        
        for idx, ep in enumerate(selected_eps):
            ep_id = ep['id']
            print(f"[{idx+1}/{len(selected_eps)}] Downloading {t['name']} episode {ep_id}...")
            replay_path = download_replay(ep_id)
            if not replay_path:
                print(f"Warning: could not download {ep_id}")
                continue
                
            # Read replay to get seed, seat, opponent, result
            try:
                with open(replay_path, 'r', encoding='utf-8') as f:
                    rep = json.load(f)
            except Exception as e:
                print(f"Error loading {replay_path}: {e}")
                continue
                
            info = rep.get('info', {})
            team_names = info.get('TeamNames', [])
            rewards = rep.get('rewards', [0, 0])
            seed = info.get('seed')
            if seed is None and 'configuration' in rep:
                seed = rep['configuration'].get('seed')
                
            # Determine seat
            seat = None
            for s_idx, t_name in enumerate(team_names):
                if t_name == t['name']:
                    seat = s_idx
                    break
            if seat is None:
                # Fallback: check agent names
                agents = info.get('Agents', [])
                for s_idx, ag in enumerate(agents):
                    if ag.get('Name') == t['name']:
                        seat = s_idx
                        break
            if seat is None:
                # If team name not matched exactly, find the agent from submission or check which seat
                # For example, DSM might have member name or exact team name
                print(f"Note: team name '{t['name']}' not exact match in {team_names}")
                # We can check team names and fallback to seat 0 or check if one name contains team
                for s_idx, t_name in enumerate(team_names):
                    if t['name'].lower() in t_name.lower():
                        seat = s_idx
                        break
                if seat is None:
                    # Let's inspect team_names
                    print(f"Unmatched team names: {team_names}")
                    seat = 0 # fallback
                    
            opp_seat = 1 - seat
            opp_name = team_names[opp_seat] if len(team_names) > opp_seat else "Unknown"
            
            my_reward = rewards[seat] if len(rewards) > seat else 0
            opp_reward = rewards[opp_seat] if len(rewards) > opp_seat else 0
            
            if my_reward > opp_reward:
                result = "WIN"
            elif my_reward < opp_reward:
                result = "LOSS"
            else:
                result = "TIE"
                
            meta_entry = {
                "episode_id": ep_id,
                "team_name": t['name'],
                "team_id": t['teamId'],
                "submission_id": t['subId'],
                "result": result,
                "my_reward": my_reward,
                "opponent": opp_name,
                "opp_reward": opp_reward,
                "seed": seed,
                "seat": seat,
                "replay_path": str(replay_path)
            }
            episodes_meta.append(meta_entry)
            
    with open(EPISODES_JSON, 'w', encoding='utf-8') as f:
        json.dump(episodes_meta, f, indent=2, ensure_ascii=False)
        
    print(f"\nSaved {len(episodes_meta)}/{total_target} episodes metadata to {EPISODES_JSON}")

if __name__ == '__main__':
    main()
