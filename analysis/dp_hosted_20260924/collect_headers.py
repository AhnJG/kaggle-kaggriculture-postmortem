#!/usr/bin/env python3
"""Step 0 & Step 1 & Step 2: Collect hosted episodes and replay headers for DP 0924 submissions."""

import os
import sys
import json
import time
import random
import shutil
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import kaggle
from kagglesdk.competitions.types.competition_api_service import ApiGetEpisodeReplayRequest

TARGET_SUBMISSIONS = [
    {"id": 56486914, "team": "Taisei_Tsuneki"},
    {"id": 56488661, "team": "wennan cao"},
    {"id": 56481644, "team": "yaya__k"},
    {"id": 56502662, "team": "Yusaku Muroya"},
    {"id": 56506164, "team": "Dzmitry Pihulski"},
    {"id": 56506193, "team": "team_56506193"},  # Aoba Suzukaze
    {"id": 56507682, "team": "haseryooooo"},
    {"id": 56518910, "team": "Sian"}
]
TARGET_SUB_IDS = {sub["id"] for sub in TARGET_SUBMISSIONS}

OUT_DIR = "analysis/dp_hosted_20260924"
RAW_DIR = "private_artifacts/dp_hosted_20260924/raw"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

# Step 0: Fix as_of
as_of_path = os.path.join(OUT_DIR, "as_of.txt")
if os.path.exists(as_of_path):
    with open(as_of_path, "r", encoding="utf-8") as f:
        as_of = f.read().strip()
    print(f"Loaded existing as_of: {as_of}")
else:
    as_of = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    with open(as_of_path, "w", encoding="utf-8") as f:
        f.write(as_of)
    print(f"Fixed as_of timestamp: {as_of}")

# Check disk space
total, used, free = shutil.disk_usage(RAW_DIR)
free_gb = free / (1024 ** 3)
print(f"Disk space check: {free_gb:.2f} GB available in {RAW_DIR}")
if free_gb < 20.0:
    print(f"BLOCKED: Available disk space is {free_gb:.2f} GB, which is below 20 GB.")
    sys.exit(2)

def replay_header_from_response(response, max_bytes=2_000_000):
    data = bytearray()
    try:
        for chunk in response.iter_content(chunk_size=65_536):
            data.extend(chunk)
            marker = data.find(b'"steps":')
            if marker >= 0:
                return json.loads(bytes(data[:marker]) + b'"steps": null}')
            if len(data) > max_bytes:
                raise ValueError("replay header exceeded byte limit")
    finally:
        response.close()
    raise ValueError("replay did not contain steps field")

def fetch_header_with_retry(api, episode_id, retries=10):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(0.1, 0.25))
            with api.build_kaggle_client() as client:
                req = ApiGetEpisodeReplayRequest()
                req.episode_id = episode_id
                resp = client.competitions.competition_api_client.get_episode_replay(req)
                return replay_header_from_response(resp)
        except Exception as e:
            if "429" in str(e):
                backoff = 4.0 * (attempt + 1) + random.uniform(1.0, 3.0)
                time.sleep(backoff)
            else:
                time.sleep(1.0 + attempt)
            if attempt == retries - 1:
                print(f"Failed to fetch header for ep {episode_id} after {retries} attempts: {e}")
                return None
    return None

api = kaggle.api
all_episodes_list = []
total_candidates = 0

print("Step 1: Listing episodes for all 8 target submissions...")
for sub_info in TARGET_SUBMISSIONS:
    sub_id = sub_info["id"]
    team_label = sub_info["team"]
    
    print(f"Fetching episode list for submission {sub_id} ({team_label})...")
    api_eps = api.competition_list_episodes(sub_id)
    eps_dict = [ep.to_dict() for ep in api_eps]
    
    completed_eps = []
    for ep in eps_dict:
        if ep.get("state") != "COMPLETED":
            continue
        if ep.get("type") != "EPISODE_TYPE_PUBLIC":
            continue
        end_time = ep.get("endTime")
        if not end_time or end_time > as_of:
            continue
        
        agents = ep.get("agents", [])
        if len(agents) != 2:
            continue
        
        target_agents = [a for a in agents if a.get("submissionId") == sub_id]
        if len(target_agents) != 1:
            continue
        
        completed_eps.append(ep)
        
    print(f"  Submission {sub_id}: {len(eps_dict)} total, {len(completed_eps)} eligible completed public eps (<= {as_of})")
    all_episodes_list.append((sub_info, completed_eps))
    total_candidates += len(completed_eps)

print(f"Total eligible candidate episodes across 8 submissions: {total_candidates}")

unique_ep_ids = set()
for sub_info, eps in all_episodes_list:
    for ep in eps:
        unique_ep_ids.add(ep["id"])

print(f"Total unique episode IDs to fetch headers for: {len(unique_ep_ids)}")

header_cache_path = os.path.join(OUT_DIR, "header_cache.json")
header_cache = {}
if os.path.exists(header_cache_path):
    try:
        with open(header_cache_path, "r", encoding="utf-8") as f:
            header_cache = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded {len(header_cache)} headers from existing cache.")
    except Exception as e:
        print(f"Failed to load cache: {e}")

needed_ids = [eid for eid in sorted(unique_ep_ids) if eid not in header_cache]
print(f"Episodes needing header fetch: {len(needed_ids)}")

failed_header_ids = []
if needed_ids:
    t0 = time.time()
    batch_count = 0
    # Use max_workers=3 for polite throughput avoiding rate limit
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_id = {executor.submit(fetch_header_with_retry, api, eid): eid for eid in needed_ids}
        for future in as_completed(future_to_id):
            eid = future_to_id[future]
            batch_count += 1
            res = future.result()
            if res is not None:
                header_cache[eid] = {
                    "seed": res.get("info", {}).get("seed"),
                    "rewards": res.get("rewards"),
                    "team_names": res.get("info", {}).get("TeamNames")
                }
            else:
                failed_header_ids.append(eid)
            if batch_count % 25 == 0 or batch_count == len(needed_ids):
                elapsed = time.time() - t0
                print(f"Fetched {batch_count}/{len(needed_ids)} headers ({elapsed:.1f}s, {len(failed_header_ids)} failed)...")
                with open(header_cache_path, "w", encoding="utf-8") as f:
                    json.dump(header_cache, f)

    with open(header_cache_path, "w", encoding="utf-8") as f:
        json.dump(header_cache, f)

fail_rate = len(failed_header_ids) / max(1, len(unique_ep_ids))
print(f"Header fetch summary: {len(header_cache)} succeeded, {len(failed_header_ids)} failed (fail rate: {fail_rate*100:.2f}%)")
if fail_rate > 0.10:
    print(f"BLOCKED: Header parsing failure rate ({fail_rate*100:.2f}%) exceeds 10% threshold.")
    sys.exit(3)

# Build episodes_all records
episodes_all = []
submission_summaries = {}

for sub_info, eps in all_episodes_list:
    sub_id = sub_info["id"]
    team_label = sub_info["team"]
    
    sub_episodes = []
    for ep in eps:
        eid = ep["id"]
        if eid not in header_cache:
            continue
        h = header_cache[eid]
        agents = ep.get("agents", [])
        
        target_agent = [a for a in agents if a.get("submissionId") == sub_id][0]
        op_agent = [a for a in agents if a.get("submissionId") != sub_id][0]
        
        seat = target_agent.get("index")
        if seat is None:
            if ep["agents"][0].get("submissionId") == sub_id:
                seat = 0
            else:
                seat = 1
        seat = int(seat)
        op_seat = 1 - seat
        
        header_rewards = h.get("rewards")
        if header_rewards and len(header_rewards) == 2 and header_rewards[0] is not None:
            our_reward = float(header_rewards[seat])
            op_reward = float(header_rewards[op_seat])
        else:
            our_reward = float(target_agent.get("reward", 0))
            op_reward = float(op_agent.get("reward", 0))
            
        margin = our_reward - op_reward
        if margin > 0:
            result = "W"
        elif margin < 0:
            result = "L"
        else:
            result = "D"
            
        op_sub_id = op_agent.get("submissionId")
        op_team_id = op_agent.get("teamId")
        op_team_name = op_agent.get("teamName")
        
        is_mirror = (op_sub_id in TARGET_SUB_IDS)
        mirror_type = "MIRROR_KNOWN" if is_mirror else "NONE"
        
        record = {
            "id": eid,
            "createTime": ep.get("createTime"),
            "endTime": ep.get("endTime"),
            "submission_id": sub_id,
            "submission_team": team_label,
            "seed": h.get("seed"),
            "seat": seat,
            "our_reward": our_reward,
            "op_reward": op_reward,
            "margin": margin,
            "result": result,
            "op_teamId": op_team_id,
            "op_teamName": op_team_name,
            "op_submissionId": op_sub_id,
            "is_mirror": is_mirror,
            "mirror_type": mirror_type
        }
        sub_episodes.append(record)
        episodes_all.append(record)
        
    submission_summaries[sub_id] = {
        "team": team_label,
        "total": len(sub_episodes),
        "mirrors": sum(1 for e in sub_episodes if e["is_mirror"]),
        "non_mirror_w": sum(1 for e in sub_episodes if not e["is_mirror"] and e["result"] == "W"),
        "non_mirror_l": sum(1 for e in sub_episodes if not e["is_mirror"] and e["result"] == "L"),
        "non_mirror_d": sum(1 for e in sub_episodes if not e["is_mirror"] and e["result"] == "D")
    }

print("\n--- Summary by Submission ---")
for sub_id, s in submission_summaries.items():
    print(f"Sub {sub_id} ({s['team']}): Total {s['total']} | Mirrors: {s['mirrors']} | Non-mirror: W={s['non_mirror_w']} L={s['non_mirror_l']} D={s['non_mirror_d']}")

# Save episodes_all.json
episodes_all_path = os.path.join(OUT_DIR, "episodes_all.json")
with open(episodes_all_path, "w", encoding="utf-8") as f:
    json.dump(episodes_all, f, indent=2)
print(f"\nSaved {len(episodes_all)} records to {episodes_all_path}")

# Step 3 selection
random.seed(20260924)
download_manifest = []

for sub_info in TARGET_SUBMISSIONS:
    sub_id = sub_info["id"]
    sub_eps = [e for e in episodes_all if e["submission_id"] == sub_id and not e["is_mirror"]]
    
    losses = [e for e in sub_eps if e["result"] == "L"]
    wins = [e for e in sub_eps if e["result"] == "W"]
    
    losses.sort(key=lambda x: x["endTime"] or "", reverse=True)
    selected_losses = losses[:60]
    
    if len(wins) > 15:
        selected_wins = random.sample(wins, 15)
    else:
        selected_wins = list(wins)
        
    print(f"Sub {sub_id} ({sub_info['team']}): selected {len(selected_losses)} losses (out of {len(losses)}), {len(selected_wins)} wins (out of {len(wins)})")
    for e in selected_losses:
        e_copy = dict(e)
        e_copy["download_reason"] = "loss_sample"
        download_manifest.append(e_copy)
    for e in selected_wins:
        e_copy = dict(e)
        e_copy["download_reason"] = "win_sample"
        download_manifest.append(e_copy)

unique_download = {}
for item in download_manifest:
    eid = item["id"]
    if eid not in unique_download:
        unique_download[eid] = item

download_list = list(unique_download.values())
if len(download_list) > 600:
    print(f"Warning: download list {len(download_list)} exceeds 600, capping to 600.")
    download_list = download_list[:600]

manifest_path = os.path.join(OUT_DIR, "download_manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(download_list, f, indent=2)
print(f"Saved download manifest with {len(download_list)} episodes to {manifest_path}")
