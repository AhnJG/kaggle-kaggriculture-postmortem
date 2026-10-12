import kaggle
import json
import os
import time
import hashlib
from datetime import datetime, timezone

# 1. Setup
submissions = [
    {"id": 56458814, "label": "EXP-016", "cap": 200},
    {"id": 56490029, "label": "EXP-017", "cap": 200}
]

as_of_dt = datetime.now(timezone.utc)
as_of = as_of_dt.isoformat().replace('+00:00', 'Z')

out_dir = 'analysis/exp016_017_hosted_20260924'
raw_dir = 'private_artifacts/exp016_017_hosted_20260924/raw'
os.makedirs(out_dir, exist_ok=True)
os.makedirs(raw_dir, exist_ok=True)

all_filtered = []
summary_by_sub = {}

for sub_info in submissions:
    sub_id = sub_info["id"]
    sub_label = sub_info["label"]
    cap = sub_info["cap"]
    
    print(f"Fetching episodes for {sub_label} ({sub_id})...")
    api_episodes = kaggle.api.competition_list_episodes(sub_id)
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
            
        p1_agents = [a for a in agents if a.get('submissionId') == sub_id]
        if len(p1_agents) != 1:
            continue
            
        p1 = p1_agents[0]
        op = [a for a in agents if a.get('submissionId') != sub_id][0]
        
        p1_reward = p1.get('reward')
        op_reward = op.get('reward')
        if p1_reward is None or op_reward is None:
            continue
            
        res = 'D'
        if p1_reward > op_reward: res = 'W'
        elif p1_reward < op_reward: res = 'L'
        
        seat = p1.get('index', 0)
        
        ep_record = {
            'id': ep.get('id'),
            'createTime': ep.get('createTime'),
            'endTime': end_time_str,
            'submission_id': sub_id,
            'submission_label': sub_label,
            'our_seat': seat,
            'our_reward': p1_reward,
            'op_reward': op_reward,
            'margin': p1_reward - op_reward,
            'result': res,
            'op_teamId': op.get('teamId'),
            'op_teamName': op.get('teamName'),
            'op_submissionId': op.get('submissionId')
        }
        filtered.append(ep_record)
        
    filtered.sort(key=lambda x: x['endTime'], reverse=True)
    
    total_found = len(filtered)
    truncated = 0
    if len(filtered) > cap:
        truncated = len(filtered) - cap
        filtered = filtered[:cap]
        
    print(f"[{sub_label}] Found {total_found} public completed, keeping {len(filtered)} (truncated {truncated})")
    
    summary_by_sub[sub_label] = {
        "submission_id": sub_id,
        "total_public_completed": total_found,
        "selected_count": len(filtered),
        "truncated_count": truncated,
        "W": len([e for e in filtered if e['result'] == 'W']),
        "L": len([e for e in filtered if e['result'] == 'L']),
        "D": len([e for e in filtered if e['result'] == 'D'])
    }
    all_filtered.extend(filtered)

with open(os.path.join(out_dir, 'episodes_all.json'), 'w') as f:
    json.dump(all_filtered, f, indent=2)

print(f"Total episodes to download across both submissions: {len(all_filtered)}")

manifest = []
identity_mismatch_count = 0
total_bytes = 0

def get_replay(ep_id):
    path = f"{raw_dir}/episode-{ep_id}-replay.json"
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path
    for attempt in range(5):
        try:
            kaggle.api.competition_episode_replay(ep_id, path=raw_dir, quiet=True)
            if os.path.exists(path) and os.path.getsize(path) > 1000:
                return path
        except Exception as e:
            if '429' in str(e):
                print(f"429 Too Many Requests on episode {ep_id}, sleeping 5s...")
                time.sleep(5)
            else:
                print(f"Error downloading {ep_id} (attempt {attempt+1}): {e}")
                time.sleep(2)
    return None

dl_idx = 0
for ep in all_filtered:
    dl_idx += 1
    ep_id = ep['id']
    if dl_idx % 25 == 0 or dl_idx == len(all_filtered):
        print(f"Downloading replay {dl_idx}/{len(all_filtered)} (ID: {ep_id})...")
        
    path = get_replay(ep_id)
    if not path or not os.path.exists(path):
        print(f"Failed to get replay for {ep_id}")
        continue
        
    try:
        with open(path, 'r') as f:
            rdata = json.load(f)
    except Exception as e:
        print(f"Failed to parse json for {ep_id}: {e}")
        continue
        
    info = rdata.get('info', {})
    rep_ep_id = info.get('EpisodeId')
    team_names = info.get('TeamNames') or []
    seat = ep['our_seat']
    
    mismatch = False
    if rep_ep_id != ep_id:
        mismatch = True
    if len(team_names) > seat and team_names[seat] != 'Sian':
        mismatch = True
        
    rewards = rdata.get('rewards') or []
    if len(rewards) > seat:
        if rewards[seat] != ep['our_reward']:
            mismatch = True
            
    if mismatch:
        print(f"Identity mismatch on episode {ep_id}: team_names={team_names}, rewards={rewards}, expected={ep['our_reward']}")
        identity_mismatch_count += 1
        continue
        
    file_size = os.path.getsize(path)
    total_bytes += file_size
    with open(path, 'rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
        
    seed = info.get('seed')
    if seed is None:
        seed = rdata.get('configuration', {}).get('seed')
        
    manifest.append({
        "id": ep_id,
        "submission_id": ep['submission_id'],
        "submission_label": ep['submission_label'],
        "path": path,
        "sha256": sha256,
        "bytes": file_size,
        "seat": seat,
        "seed": seed,
        "engine_version": rdata.get('module_version', rdata.get('version')),
        "result": ep['result'],
        "margin": ep['margin'],
        "our_reward": ep['our_reward'],
        "op_reward": ep['op_reward'],
        "op_teamName": ep['op_teamName'],
        "op_teamId": ep['op_teamId'],
        "endTime": ep['endTime'],
        "createTime": ep['createTime']
    })

with open(os.path.join(out_dir, 'manifest.json'), 'w') as f:
    json.dump(manifest, f, indent=2)

file_hashes = {m['path']: m['sha256'] for m in manifest}
with open(os.path.join(out_dir, 'file_hashes.json'), 'w') as f:
    json.dump(file_hashes, f, indent=2)

summary = {
    "as_of": as_of,
    "summary_by_submission": summary_by_sub,
    "total_episodes_manifest": len(manifest),
    "identity_mismatch_count": identity_mismatch_count,
    "total_bytes": total_bytes
}

with open(os.path.join(out_dir, 'summary.json'), 'w') as f:
    json.dump(summary, f, indent=2)

print(f"Done collecting. Manifest count: {len(manifest)}, Mismatches: {identity_mismatch_count}, Total bytes: {total_bytes}")
