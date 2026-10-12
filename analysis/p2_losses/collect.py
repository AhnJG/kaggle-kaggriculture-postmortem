import kaggle
import json
import os
import time
import hashlib
from datetime import datetime, timezone
import urllib.error

# 1. Setup
submission_id = 56347732
as_of_dt = datetime.now(timezone.utc)
as_of = as_of_dt.isoformat()
# format string correctly if needed, kaggle uses "YYYY-MM-DDTHH:MM:SS.mmmZ"
as_of = as_of.replace('+00:00', 'Z')

out_dir = 'analysis/p2_losses_20260920'
raw_dir = 'private_artifacts/p2_losses_20260920/raw'
os.makedirs(out_dir, exist_ok=True)
os.makedirs(raw_dir, exist_ok=True)

# Fetch all episodes
print("Fetching episodes...")
api_episodes = kaggle.api.competition_list_episodes(submission_id)
episodes = [json.loads(ep.to_json()) for ep in api_episodes]

filtered = []
for ep in episodes:
    # Filter
    if ep.get('state') != 'COMPLETED' or ep.get('type') != 'EPISODE_TYPE_PUBLIC':
        continue
    
    end_time_str = ep.get('endTime')
    if end_time_str is None:
        continue
    # kaggle's Z might need to be parsed
    try:
        if end_time_str > as_of:
            continue
    except:
        pass
    
    agents = ep.get('agents', [])
    if len(agents) != 2:
        continue
        
    # Exclude validation (self-play). teamId should be different
    if agents[0].get('teamId') == agents[1].get('teamId'):
        continue
        
    p2_agents = [a for a in agents if a.get('submissionId') == submission_id]
    if len(p2_agents) != 1:
        continue
        
    p2 = p2_agents[0]
    op = [a for a in agents if a.get('submissionId') != submission_id][0]
    
    p2_reward = p2.get('reward')
    op_reward = op.get('reward')
    if p2_reward is None or op_reward is None:
        continue
        
    res = 'D'
    if p2_reward > op_reward: res = 'W'
    elif p2_reward < op_reward: res = 'L'
    
    ep['p2_result'] = res
    ep['p2_seat'] = p2.get('index', 0)
    ep['op_teamId'] = op.get('teamId')
    ep['op_teamName'] = op.get('teamName')
    ep['op_submissionId'] = op.get('submissionId')
    ep['p2_reward'] = p2_reward
    ep['op_reward'] = op_reward
    
    filtered.append(ep)

# Sort by endTime desc
filtered.sort(key=lambda x: x['endTime'], reverse=True)

W_list = [ep for ep in filtered if ep['p2_result'] == 'W']
A_list = [ep for ep in filtered if ep['p2_result'] in ('L', 'D')]

print(f"Total filtered: {len(filtered)} (W: {len(W_list)}, L+D: {len(A_list)})")

# Truncate A to 200
truncated_a_count = 0
if len(A_list) > 200:
    truncated_a_count = len(A_list) - 200
    A_list = A_list[:200]

# Match B from W
B_list = []
used_w = set()
shortfall_b_count = 0
same_opponent_count = 0

def parse_time(ts):
    # e.g., 2026-09-19T15:31:42.417Z
    return datetime.strptime(ts[:23], "%Y-%m-%dT%H:%M:%S.%f")

for a in A_list:
    a_time = parse_time(a['endTime'])
    
    best_w = None
    best_diff = None
    is_same = False
    
    # 1. same opponent
    for w in W_list:
        if w['id'] in used_w: continue
        if w['op_teamId'] == a['op_teamId']:
            diff = abs((parse_time(w['endTime']) - a_time).total_seconds())
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_w = w
                is_same = True
                
    # 2. any opponent
    if best_w is None:
        for w in W_list:
            if w['id'] in used_w: continue
            diff = abs((parse_time(w['endTime']) - a_time).total_seconds())
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_w = w
                is_same = False
                
    if best_w is not None:
        used_w.add(best_w['id'])
        if is_same: same_opponent_count += 1
        b_info = dict(best_w)
        b_info['matched_a_id'] = a['id']
        b_info['same_opponent_match'] = is_same
        B_list.append(b_info)
    else:
        shortfall_b_count += 1

selection = {
    "as_of": as_of,
    "rules": "P2(56347732) hosted episodes: L/D (max 200) + matching W. as_of = script start UTC.",
    "total_episodes_filtered": len(filtered),
    "W_count": len(W_list),
    "L_count": len([e for e in filtered if e['p2_result'] == 'L']),
    "D_count": len([e for e in filtered if e['p2_result'] == 'D']),
    "A_count": len(A_list),
    "B_count": len(B_list),
    "truncated_a_count": truncated_a_count,
    "shortfall_b_count": shortfall_b_count,
    "same_opponent_count": same_opponent_count,
    "A": A_list,
    "B": B_list
}

selection_path = os.path.join(out_dir, 'selection.json')
with open(selection_path, 'w') as f:
    json.dump(selection, f, indent=2)

print("Saved selection.json")

# Write episodes_all.json
with open(os.path.join(out_dir, 'episodes_all.json'), 'w') as f:
    json.dump(filtered, f, indent=2)

# Download and verify
manifest = []
identity_mismatch_count = 0
total_bytes = 0

episodes_to_download = A_list + B_list

print(f"Downloading {len(episodes_to_download)} replays...")

def get_replay(ep_id):
    path = f"{raw_dir}/episode-{ep_id}-replay.json"
    if os.path.exists(path):
        return path
    for attempt in range(5):
        try:
            kaggle.api.competition_episode_replay(ep_id, path=raw_dir, quiet=True)
            return path
        except Exception as e:
            if '429' in str(e):
                print("429 Too Many Requests, sleeping 5s...")
                time.sleep(5)
            else:
                print(f"Error downloading {ep_id}: {e}")
                time.sleep(2)
    return None

for ep in episodes_to_download:
    ep_id = ep['id']
    path = get_replay(ep_id)
    if not path or not os.path.exists(path):
        print(f"Failed to get replay for {ep_id}")
        continue
        
    with open(path, 'r') as f:
        try:
            rdata = json.load(f)
        except:
            print(f"Failed to parse json for {ep_id}")
            continue
            
    info = rdata.get('info', {})
    rep_ep_id = info.get('EpisodeId')
    team_names = info.get('TeamNames') or []
    seat = ep['p2_seat']
    
    mismatch = False
    if rep_ep_id != ep_id:
        mismatch = True
    if len(team_names) > seat and team_names[seat] != 'Sian':
        mismatch = True
        
    # Check rewards
    rewards = rdata.get('rewards') or []
    if len(rewards) > seat:
        if rewards[seat] != ep['p2_reward']:
            mismatch = True
            
    if mismatch:
        identity_mismatch_count += 1
        continue
        
    # File hash & size
    file_size = os.path.getsize(path)
    total_bytes += file_size
    with open(path, 'rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
        
    manifest.append({
        "id": ep_id,
        "path": path,
        "sha256": sha256,
        "bytes": file_size,
        "seat": seat,
        "seed": rdata.get('configuration', {}).get('seed'),
        "engine_version": rdata.get('module_version', rdata.get('version')),
        "result": ep['p2_result'],
        "matched_a_id": ep.get('matched_a_id'),
        "same_opponent_match": ep.get('same_opponent_match')
    })

with open(os.path.join(out_dir, 'manifest.json'), 'w') as f:
    json.dump(manifest, f, indent=2)

# File hashes
file_hashes = {m['path']: m['sha256'] for m in manifest}
with open(os.path.join(out_dir, 'file_hashes.json'), 'w') as f:
    json.dump(file_hashes, f, indent=2)

summary = {
    "total_filtered": len(filtered),
    "W": len(W_list),
    "L": selection["L_count"],
    "D": selection["D_count"],
    "A_count": len(A_list),
    "B_count": len(B_list),
    "same_opponent_count": same_opponent_count,
    "truncated_a_count": truncated_a_count,
    "identity_mismatch_count": identity_mismatch_count,
    "total_bytes": total_bytes
}

with open(os.path.join(out_dir, 'summary.json'), 'w') as f:
    json.dump(summary, f, indent=2)

print("Done collecting.")
