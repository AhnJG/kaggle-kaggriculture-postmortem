#!/usr/bin/env python3
import os
import sys
import json
import time
import zipfile
import csv
from datetime import datetime, timezone
import kaggle

OUT_DIR = "analysis/top2400_fresh_20260929"
os.makedirs(OUT_DIR, exist_ok=True)

submissions = [
    {"id": 56461596, "label": "T56461596", "cap": 30},
    {"id": 56567596, "label": "T56567596", "cap": 30},
    {"id": 56584611, "label": "T56584611", "cap": 30},
    {"id": 56588821, "label": "T56588821", "cap": 30},
    {"id": 56602348, "label": "T56602348", "cap": 30},
    {"id": 56606525, "label": "T56606525", "cap": 30},
    {"id": 56608590, "label": "T56608590", "cap": 30},
    {"id": 56609277, "label": "T56609277", "cap": 30},
    {"id": 56609306, "label": "T56609306", "cap": 30},
    {"id": 56609503, "label": "T56609503", "cap": 30},
    {"id": 56610524, "label": "T56610524", "cap": 30},
    {"id": 56610781, "label": "T56610781", "cap": 30},
    {"id": 56610842, "label": "T56610842", "cap": 30},
    {"id": 56612072, "label": "T56612072", "cap": 30},
    {"id": 56612539, "label": "T56612539", "cap": 30},
    {"id": 56613024, "label": "T56613024", "cap": 30},
    {"id": 56613611, "label": "T56613611", "cap": 30},
    {"id": 56613976, "label": "T56613976", "cap": 30},
    {"id": 56614051, "label": "T56614051", "cap": 30},
    {"id": 56616709, "label": "T56616709", "cap": 30},
    {"id": 56619080, "label": "T56619080", "cap": 30},
    {"id": 56619267, "label": "T56619267", "cap": 30},
    {"id": 56621283, "label": "T56621283", "cap": 30},
    {"id": 56621434, "label": "T56621434", "cap": 30},
    {"id": 56623637, "label": "T56623637", "cap": 30}
]

as_of_dt = datetime.now(timezone.utc)
as_of = as_of_dt.isoformat().replace("+00:00", "Z")
with open(os.path.join(OUT_DIR, "as_of.txt"), "w", encoding="utf-8") as f:
    f.write(as_of)

print(f"As of: {as_of}")

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
        if ep.get("state") != "COMPLETED" or ep.get("type") != "EPISODE_TYPE_PUBLIC":
            continue

        end_time_str = ep.get("endTime")
        if end_time_str is None:
            continue
        try:
            if end_time_str > as_of:
                continue
            if end_time_str <= "2026-09-28T05:27:08.129599Z":  # FRESH: only games after the EXP-041 collection
                continue
        except:
            pass

        agents = ep.get("agents", [])
        if len(agents) != 2:
            continue

        if agents[0].get("teamId") == agents[1].get("teamId"):
            continue

        p1_agents = [a for a in agents if a.get("submissionId") == sub_id]
        if len(p1_agents) != 1:
            continue

        p1 = p1_agents[0]
        op = [a for a in agents if a.get("submissionId") != sub_id][0]

        p1_reward = p1.get("reward")
        op_reward = op.get("reward")
        if p1_reward is None or op_reward is None:
            continue

        res = "D"
        if p1_reward > op_reward:
            res = "W"
        elif p1_reward < op_reward:
            res = "L"

        seat = p1.get("index", 0)

        ep_record = {
            "id": ep.get("id"),
            "seed": None,  # Will be populated / verified from replay in Step 3
            "submission_id": sub_id,
            "submission_label": sub_label,
            "our_seat": seat,
            "our_reward": p1_reward,
            "op_reward": op_reward,
            "margin": p1_reward - op_reward,
            "result": res,
            "op_teamName": op.get("teamName"),
            "op_teamId": op.get("teamId"),
            "op_submissionId": op.get("submissionId"),
            "createTime": ep.get("createTime"),
            "endTime": end_time_str,
            "op_lb_score": None  # Will be populated in Step 2 below
        }
        filtered.append(ep_record)

    filtered.sort(key=lambda x: x["endTime"], reverse=True)
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
        "W": len([e for e in filtered if e["result"] == "W"]),
        "L": len([e for e in filtered if e["result"] == "L"]),
        "D": len([e for e in filtered if e["result"] == "D"])
    }
    all_filtered.extend(filtered)

print(f"Total filtered episodes: {len(all_filtered)}")

# Step 2: Download leaderboard snapshot and attach op_lb_score
print("Step 2: Downloading leaderboard snapshot...")
try:
    kaggle.api.competition_leaderboard_download("kaggriculture", path=OUT_DIR)
except Exception as e:
    print(f"Warning/Error downloading leaderboard: {e}")

lb_zip_path = os.path.join(OUT_DIR, "kaggriculture.zip")
if not os.path.exists(lb_zip_path):
    alt_zip = os.path.join(OUT_DIR, "leaderboard.zip")
    if os.path.exists(alt_zip):
        lb_zip_path = alt_zip

lb_by_team_id = {}
if os.path.exists(lb_zip_path):
    print(f"Reading leaderboard from {lb_zip_path}...")
    with zipfile.ZipFile(lb_zip_path, "r") as z:
        csv_files = [n for n in z.namelist() if n.endswith(".csv")]
        if csv_files:
            csv_content = z.read(csv_files[0]).decode("utf-8-sig")
            reader = csv.DictReader(csv_content.splitlines())
            for row in reader:
                try:
                    tid = int(row["TeamId"])
                    score = float(row["Score"])
                    lb_by_team_id[tid] = score
                except:
                    pass
    print(f"Loaded {len(lb_by_team_id)} teams from leaderboard snapshot.")
else:
    print("Warning: Leaderboard zip file not found!")

for ep in all_filtered:
    op_tid = ep.get("op_teamId")
    if op_tid is not None and op_tid in lb_by_team_id:
        ep["op_lb_score"] = lb_by_team_id[op_tid]
    else:
        ep["op_lb_score"] = None

episodes_all_path = os.path.join(OUT_DIR, "episodes_all.json")
with open(episodes_all_path, "w", encoding="utf-8") as f:
    json.dump(all_filtered, f, indent=2)

print(f"Saved {len(all_filtered)} episodes to {episodes_all_path}.")
