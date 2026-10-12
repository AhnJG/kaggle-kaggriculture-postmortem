#!/usr/bin/env python3
import os
import sys
import json
import time
import gzip
import shutil
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

import kaggle
from kagglesdk.competitions.types.competition_api_service import ApiGetEpisodeReplayRequest

OUT_DIR = "analysis/c26_hosted_20260929"
RAW_DIR = "private_artifacts/c26_hosted_20260929/raw"
os.makedirs(RAW_DIR, exist_ok=True)

episodes_path = os.path.join(OUT_DIR, "episodes_all.json")
if not os.path.exists(episodes_path):
    print(f"Error: {episodes_path} not found.")
    sys.exit(1)

with open(episodes_path, "r", encoding="utf-8") as f:
    episodes = json.load(f)

print(f"Loaded {len(episodes)} episodes to download and verify.")

def check_disk_space():
    total, used, free = shutil.disk_usage(RAW_DIR)
    free_gb = free / (1024 ** 3)
    if free_gb < 20.0:
        print(f"BLOCKED: Available disk space is {free_gb:.2f} GB (< 20 GB threshold)!")
        return False, free_gb
    return True, free_gb

ok, free_gb = check_disk_space()
if not ok:
    sys.exit(2)
print(f"Disk check: {free_gb:.2f} GB available.")

def download_replay_gzip(api, episode_id, retries=8):
    gz_path = os.path.join(RAW_DIR, f"{episode_id}.json.gz")
    if os.path.exists(gz_path) and os.path.getsize(gz_path) > 10_000:
        return episode_id, True, "cached", os.path.getsize(gz_path)

    tmp_path = os.path.join(RAW_DIR, f"{episode_id}.json.gz.tmp")
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(0.1, 0.25))
            with api.build_kaggle_client() as client:
                req = ApiGetEpisodeReplayRequest()
                req.episode_id = episode_id
                resp = client.competitions.competition_api_client.get_episode_replay(req)
                with gzip.open(tmp_path, "wb") as f_out:
                    for chunk in resp.iter_content(chunk_size=128 * 1024):
                        f_out.write(chunk)

            size = os.path.getsize(tmp_path)
            if size > 10_000:
                os.replace(tmp_path, gz_path)
                return episode_id, True, "downloaded", size
            else:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if "429" in str(e):
                backoff = 4.0 * (attempt + 1) + random.uniform(1.0, 3.0)
                time.sleep(backoff)
            else:
                time.sleep(1.0 + attempt)
            if attempt == retries - 1:
                return episode_id, False, str(e), 0
    return episode_id, False, "unknown error", 0

api = kaggle.api
ep_ids = [item["id"] for item in episodes]
unique_ep_ids = list(dict.fromkeys(ep_ids))
print(f"Unique episodes to ensure downloaded: {len(unique_ep_ids)}")

t0 = time.time()
downloaded_count = 0
failed_count = 0
cached_count = 0
total_bytes = 0

with ThreadPoolExecutor(max_workers=4) as executor:
    future_to_id = {executor.submit(download_replay_gzip, api, eid): eid for eid in unique_ep_ids}
    done_count = 0
    for future in as_completed(future_to_id):
        done_count += 1
        eid, success, status, size = future.result()
        if success:
            if status == "cached":
                cached_count += 1
            else:
                downloaded_count += 1
            total_bytes += size
        else:
            failed_count += 1
            print(f"Download failed for episode {eid}: {status}")

        if done_count % 50 == 0 or done_count == len(unique_ep_ids):
            ok, free_gb = check_disk_space()
            if not ok:
                print(f"Stopping downloads due to low disk space ({free_gb:.2f} GB)!")
                sys.exit(2)
            elapsed = time.time() - t0
            rate = done_count / max(1.0, elapsed)
            print(f"Progress: {done_count}/{len(unique_ep_ids)} (new: {downloaded_count}, cached: {cached_count}, failed: {failed_count}) in {elapsed:.1f}s ({rate:.1f} eps/s, disk: {free_gb:.1f} GB)")

print(f"\nReplay download complete:")
print(f"  Total: {len(unique_ep_ids)}")
print(f"  Newly downloaded: {downloaded_count}")
print(f"  Cached: {cached_count}")
print(f"  Failed: {failed_count}")
print(f"  Total size: {total_bytes / (1024*1024):.2f} MB")

# Verification step: verify seed, seat, reward against metadata
print("\nVerifying replays against metadata...")
mismatch_count = 0
missing_count = 0

for ep in episodes:
    eid = ep["id"]
    gz_path = os.path.join(RAW_DIR, f"{eid}.json.gz")
    if not os.path.exists(gz_path):
        ep["replay_missing"] = True
        missing_count += 1
        continue

    try:
        with gzip.open(gz_path, "rt", encoding="utf-8") as f:
            rdata = json.load(f)
    except Exception as e:
        ep["replay_corrupt"] = True
        missing_count += 1
        continue

    info = rdata.get("info", {})
    seed = info.get("seed")
    if seed is None:
        seed = rdata.get("configuration", {}).get("seed")
    ep["seed"] = seed

    team_names = info.get("TeamNames") or []
    rewards = rdata.get("rewards") or []
    seat = ep["our_seat"]

    mismatches = []
    # Verify seat / team if available
    if len(team_names) > seat and team_names[seat] != "Sian":
        mismatches.append(f"seat_team_mismatch: got {team_names[seat]}, expected Sian")

    # Verify rewards
    if len(rewards) > seat:
        if rewards[seat] != ep["our_reward"]:
            mismatches.append(f"reward_mismatch: got {rewards[seat]}, expected {ep['our_reward']}")
    else:
        mismatches.append("rewards_missing_or_short")

    if mismatches:
        ep["mismatch"] = mismatches
        mismatch_count += 1
        print(f"Episode {eid} mismatch: {mismatches}")
    else:
        ep["mismatch"] = None

with open(episodes_path, "w", encoding="utf-8") as f:
    json.dump(episodes, f, indent=2)

print(f"Updated {episodes_path} with seeds and verification results.")
print(f"Verification summary: total={len(episodes)}, missing={missing_count}, mismatches={mismatch_count}")
if len(episodes) > 0 and (mismatch_count / len(episodes)) >= 0.10:
    print(f"WARNING: Verification mismatch rate >= 10%! ({mismatch_count}/{len(episodes)})")
