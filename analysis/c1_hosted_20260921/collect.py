import kaggle
import json
import os
import time
import hashlib
from datetime import datetime, timezone
import urllib.error

# 1. Setup
submission_id = 56426857
as_of_dt = datetime.now(timezone.utc)
as_of = as_of_dt.isoformat()
as_of = as_of.replace('+00:00', 'Z')

out_dir = 'analysis/c1_hosted_20260921'
raw_dir = 'private_artifacts/c1_hosted_20260921/raw'
os.makedirs(out_dir, exist_ok=True)
os.makedirs(raw_dir, exist_ok=True)

# Fetch all episodes
print("Fetching episodes...")
api_episodes = kaggle.api.competition_list_episodes(submission_id)
episodes = [json.loads(ep.to_json()) for ep in api_episodes]

filtered = []
for ep in episodes:
    if ep.get('state') != 'COMPLETED' or ep.get('type') != 'EPISODE_TYPE_PUBLIC':
        continue
    
    end_time_str = ep.get('endTime')
    if end_time_str is None:
        continue
    try:
        if end_time_str > as_of:
            continue
    except:
        pass
    
    agents = ep.get('agents', [])
    if len(agents) != 2:
        continue
        
    if agents[0].get('teamId') == agents[1].get('teamId'):
        continue
        
    p1_agents = [a for a in agents if a.get('submissionId') == submission_id]
    if len(p1_agents) != 1:
        continue
        
    p1 = p1_agents[0]
    op = [a for a in agents if a.get('submissionId') != submission_id][0]
    
    p1_reward = p1.get('reward')
    op_reward = op.get('reward')
    if p1_reward is None or op_reward is None:
        continue
        
    res = 'D'
    if p1_reward > op_reward: res = 'W'
    elif p1_reward < op_reward: res = 'L'
    
    ep['c1_result'] = res
    ep['c1_seat'] = p1.get('index', 0)
    ep['op_teamId'] = op.get('teamId')
    ep['op_teamName'] = op.get('teamName')
    ep['op_submissionId'] = op.get('submissionId')
    ep['c1_reward'] = p1_reward
    ep['op_reward'] = op_reward
    
    filtered.append(ep)

# Sort by endTime desc
filtered.sort(key=lambda x: x['endTime'], reverse=True)

# Truncate to 300
truncated_count = 0
if len(filtered) > 300:
    truncated_count = len(filtered) - 300
    filtered = filtered[:300]

with open(os.path.join(out_dir, 'episodes_all.json'), 'w') as f:
    json.dump(filtered, f, indent=2)

print(f"Total to download: {len(filtered)} (truncated: {truncated_count})")

manifest = []
identity_mismatch_count = 0
total_bytes = 0

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

for ep in filtered:
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
    seat = ep['c1_seat']
    
    mismatch = False
    if rep_ep_id != ep_id:
        mismatch = True
    if len(team_names) > seat and team_names[seat] != 'Sian':
        mismatch = True
        
    rewards = rdata.get('rewards') or []
    if len(rewards) > seat:
        if rewards[seat] != ep['c1_reward']:
            mismatch = True
            
    if mismatch:
        identity_mismatch_count += 1
        continue
        
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
        "result": ep['c1_result'],
        "margin": ep['c1_reward'] - ep['op_reward']
    })

with open(os.path.join(out_dir, 'manifest.json'), 'w') as f:
    json.dump(manifest, f, indent=2)

file_hashes = {m['path']: m['sha256'] for m in manifest}
with open(os.path.join(out_dir, 'file_hashes.json'), 'w') as f:
    json.dump(file_hashes, f, indent=2)

summary = {
    "total_episodes": len(filtered) + truncated_count,
    "downloaded_episodes": len(filtered),
    "W": len([e for e in filtered if e['c1_result'] == 'W']),
    "L": len([e for e in filtered if e['c1_result'] == 'L']),
    "D": len([e for e in filtered if e['c1_result'] == 'D']),
    "truncated_count": truncated_count,
    "identity_mismatch_count": identity_mismatch_count,
    "total_bytes": total_bytes
}

with open(os.path.join(out_dir, 'summary.json'), 'w') as f:
    json.dump(summary, f, indent=2)

print("Done collecting.")
