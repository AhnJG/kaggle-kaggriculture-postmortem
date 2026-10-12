#!/usr/bin/env python3
"""Step 5, 6, 7: Opponent fingerprinting, Leaderboard score matching, opponents.csv and summary.json generation."""

import os
import sys
import glob
import json
import csv
import time
import gzip
import zipfile
import hashlib
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from concurrent.futures import ProcessPoolExecutor, as_completed

from kaggle_environments import make, agent

OUT_DIR = "analysis/dp_hosted_20260924"
RAW_DIR = "private_artifacts/dp_hosted_20260924/raw"
DP_PATH = "releases/public-tetsutani-demand-preserving-0924-exact/main.py"

manifest_path = os.path.join(OUT_DIR, "download_manifest.json")
if not os.path.exists(manifest_path):
    print(f"Error: {manifest_path} does not exist.")
    sys.exit(1)

with open(manifest_path, "r", encoding="utf-8") as f:
    download_list = json.load(f)

print(f"Total downloaded episodes to fingerprint: {len(download_list)}")

# 1. Build candidates list and file_hashes.json
def get_all_candidates():
    candidates = {}
    
    # 1.1 17 reference bots from 20260924-1610 report
    refs_17 = {
        "C1": "releases/public-nathanjacob-pipe16-exact/main.py",
        "C2": "releases/public-thomastschinkel-metav4-v13-exact/main.py",
        "C3": "releases/public-thomastschinkel-2945-farm-exact/main.py",
        "C4": "releases/public-ozer-v53-exact/main.py",
        "C5": "releases/public-ozer-v51-exact/main.py",
        "P2": "releases/public-lynnsakurai-farming-score-v2-exact/main.py",
        "OMW": "releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py",
        "more-wheat-smarter-sales": "releases/public-dmitriigluzdov-kaggriculture-more-wheat-smarter-sales-exact/main.py",
        "7-turn-rescue": "releases/public-dmitriigluzdov-kaggriculture-7-turn-rescue-historical-lb-2800-exact/main.py",
        "a-smaller-market-shock": "releases/public-dmitriigluzdov-kaggriculture-a-smaller-market-shock-exact/main.py",
        "EXP-016": "releases/f0-c1-adv-exp016/main.py",
        "EXP-017": "releases/f0-omw-adv-exp017/main.py",
        "multi-route": "analysis/daily_scan/20260922/extracted/kaggriculture-multi-route-farming-agent/main.py",
        "v56-smarter": "analysis/daily_scan/20260922/extracted/kaggriculture-v56-smarter-seeds-and-fertilizer/main.py",
        "harvest-ledger": "analysis/daily_scan/20260922/extracted/kaggriculture-harvest-ledger/main.py",
        "order-book": "analysis/daily_scan/20260922/extracted/your-market-list-is-an-order-book/main.py",
        "farmer-john": "analysis/daily_scan/20260922/extracted/farmer-john-and-the-wheat-seller/main.py"
    }
    for name, p in refs_17.items():
        if os.path.exists(p):
            with open(p, "rb") as fp:
                c = fp.read().replace(b"\r\n", b"\n")
            sha = hashlib.sha256(c).hexdigest()
            candidates[sha] = {
                "name": name,
                "path": p,
                "sha256": sha
            }

    # 1.2 DP 0924 exact itself
    if os.path.exists(DP_PATH):
        with open(DP_PATH, "rb") as fp:
            c = fp.read().replace(b"\r\n", b"\n")
        sha = hashlib.sha256(c).hexdigest()
        if sha not in candidates:
            candidates[sha] = {
                "name": "DP-0924-exact",
                "path": DP_PATH,
                "sha256": sha
            }

    # 1.3 Ahmed Berat Ozer V56 exact release if present
    v56_exact_path = "releases/public-ahmedberatozer-kaggriculture-v56-smarter-seeds-and-fertilizer-exact/main.py"
    if os.path.exists(v56_exact_path):
        with open(v56_exact_path, "rb") as fp:
            c = fp.read().replace(b"\r\n", b"\n")
        sha = hashlib.sha256(c).hexdigest()
        if sha not in candidates:
            candidates[sha] = {
                "name": "v56-exact",
                "path": v56_exact_path,
                "sha256": sha
            }

    # 1.4 Candidates with _CL_INSTALL from daily scans
    scan_files = glob.glob("analysis/daily_scan/20260922/extracted/*/main.py") + glob.glob("analysis/daily_scan/20260924/extracted/*/main.py")
    for p in sorted(scan_files):
        with open(p, "rb") as fp:
            raw = fp.read()
        if b"_CL_INSTALL" in raw:
            c = raw.replace(b"\r\n", b"\n")
            sha = hashlib.sha256(c).hexdigest()
            dir_name = os.path.basename(os.path.dirname(p))
            if sha not in candidates:
                candidates[sha] = {
                    "name": dir_name,
                    "path": p,
                    "sha256": sha
                }

    return candidates

candidates_dict = get_all_candidates()
print(f"Total unique reference candidates collected: {len(candidates_dict)}")

# Save file_hashes.json
file_hashes_path = os.path.join(OUT_DIR, "file_hashes.json")
with open(file_hashes_path, "w", encoding="utf-8") as f:
    json.dump(candidates_dict, f, indent=2)
print(f"Saved file hashes to {file_hashes_path}")

# 2. Load Leaderboard snapshot
def load_leaderboard():
    csv_candidates = glob.glob(os.path.join(OUT_DIR, "*leaderboard*.csv"))
    if csv_candidates:
        csv_path = csv_candidates[0]
        print(f"Loading leaderboard from local file: {csv_path}")
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            csv_content = f.read()
    else:
        lb_zip = os.path.join(OUT_DIR, "leaderboard.zip")
        if not os.path.exists(lb_zip):
            lb_zip = "/tmp/lb_test/kaggriculture.zip"
        if not os.path.exists(lb_zip):
            import kaggle
            os.makedirs("/tmp/lb_test", exist_ok=True)
            kaggle.api.competition_leaderboard_download("kaggriculture", path="/tmp/lb_test")
            lb_zip = "/tmp/lb_test/kaggriculture.zip"
        
        with zipfile.ZipFile(lb_zip, "r") as z:
            csv_names = [n for n in z.namelist() if n.endswith(".csv")]
            if not csv_names:
                raise FileNotFoundError("No CSV found in leaderboard zip")
            csv_content = z.read(csv_names[0]).decode("utf-8-sig")
    
    reader = csv.DictReader(csv_content.splitlines())
    lb_by_team_id = {}
    for r in reader:
        try:
            tid = int(r["TeamId"])
            lb_by_team_id[tid] = {
                "rank": int(r["Rank"]),
                "score": float(r["Score"]),
                "name": r["TeamName"]
            }
        except:
            pass
    return lb_by_team_id

lb_data = load_leaderboard()
print(f"Loaded {len(lb_data)} leaderboard team records.")

# 3. Parallel worker logic
def process_episode_batch(worker_idx, ep_batch, cand_items):
    # Pre-compile DP agent
    with open(DP_PATH, "r", encoding="utf-8") as f:
        dp_code = f.read()
    dp_fn = agent.get_last_callable(dp_code, path=DP_PATH)
    
    # Pre-compile candidates
    cand_fns = []
    for sha, c_info in cand_items:
        try:
            with open(c_info["path"], "r", encoding="utf-8") as f:
                c_code = f.read()
            fn = agent.get_last_callable(c_code, path=c_info["path"])
            cand_fns.append((sha, c_info["name"], fn))
        except Exception as e:
            pass

    batch_results = []
    for ep in ep_batch:
        eid = ep["id"]
        seat = int(ep["seat"])
        op_seat = 1 - seat
        seed = int(ep["seed"])
        
        gz_path = os.path.join(RAW_DIR, f"{eid}.json.gz")
        if not os.path.exists(gz_path):
            continue
        try:
            with gzip.open(gz_path, "rt", encoding="utf-8") as f:
                rdata = json.load(f)
        except Exception as e:
            continue
            
        steps = rdata.get("steps", [])
        hosted_op_actions = [st[op_seat].get("action") for st in steps[1:]]
        
        best_prefix = -1
        best_cands = []
        is_match_143 = False
        is_match_400 = False
        is_match_full = False
        
        for sha, c_name, c_fn in cand_fns:
            # 1. Test 143 steps
            env = make("kaggriculture", configuration={"episodeSteps": 144, "seed": seed})
            agents = [None, None]
            agents[seat] = dp_fn
            agents[op_seat] = c_fn
            env.run(agents)
            
            local_actions = [st[op_seat].get("action") for st in env.steps[1:]]
            limit = min(143, len(local_actions), len(hosted_op_actions))
            match_len = 0
            for i in range(limit):
                if local_actions[i] == hosted_op_actions[i]:
                    match_len += 1
                else:
                    break
                    
            if match_len > best_prefix:
                best_prefix = match_len
                best_cands = [c_name]
            elif match_len == best_prefix and match_len > 0:
                best_cands.append(c_name)
                
            if match_len == 143:
                is_match_143 = True
                # 2. Test 400 steps
                env_400 = make("kaggriculture", configuration={"episodeSteps": 401, "seed": seed})
                agents_400 = [None, None]
                agents_400[seat] = dp_fn
                agents_400[op_seat] = c_fn
                env_400.run(agents_400)
                local_400 = [st[op_seat].get("action") for st in env_400.steps[1:]]
                
                limit_400 = min(400, len(local_400), len(hosted_op_actions))
                m400 = 0
                for i in range(limit_400):
                    if local_400[i] == hosted_op_actions[i]:
                        m400 += 1
                    else:
                        break
                        
                if m400 == 400:
                    is_match_400 = True
                    # 3. Test FULL 719 steps
                    env_full = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
                    agents_full = [None, None]
                    agents_full[seat] = dp_fn
                    agents_full[op_seat] = c_fn
                    env_full.run(agents_full)
                    local_full = [st[op_seat].get("action") for st in env_full.steps[1:]]
                    
                    limit_full = min(719, len(local_full), len(hosted_op_actions))
                    mfull = 0
                    for i in range(limit_full):
                        if local_full[i] == hosted_op_actions[i]:
                            mfull += 1
                        else:
                            break
                    if mfull == 719:
                        is_match_full = True
                        best_prefix = 719
                        best_cands = [c_name]
                        break  # Found exact full match
        
        # Determine label and closest file
        closest_file = best_cands[0] if best_cands else "none"
        if is_match_full:
            match_col = "full"
            label = "|".join(sorted(set(best_cands)))
        elif is_match_400:
            match_col = "400"
            label = f"MATCH_400 ({'|'.join(sorted(set(best_cands)))})"
        elif is_match_143:
            match_col = "143"
            label = "|".join(sorted(set(best_cands)))
        else:
            match_col = "0"
            label = f"UNKNOWN ({best_prefix} with {'|'.join(sorted(set(best_cands)))})"
            
        batch_results.append({
            "episode": eid,
            "submission_id": ep["submission_id"],
            "seed": seed,
            "dp_seat": seat,
            "result": ep["result"],
            "margin": ep["margin"],
            "op_team": ep.get("op_teamName", "Unknown"),
            "op_teamId": ep.get("op_teamId"),
            "prefix_len": best_prefix,
            "label": label,
            "closest_file": closest_file,
            "match_col": match_col,
            "match_143": is_match_143,
            "match_400": is_match_400,
            "match_full": is_match_full
        })
    return batch_results

def run_all_fingerprinting():
    # Split download_list into batches for ProcessPoolExecutor
    cand_items = list(candidates_dict.items())
    num_workers = min(8, os.cpu_count() or 4)
    print(f"Starting parallel fingerprinting on {num_workers} processes...")
    
    batches = [[] for _ in range(num_workers)]
    for i, ep in enumerate(download_list):
        batches[i % num_workers].append(ep)
        
    t0 = time.time()
    all_results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_episode_batch, idx, b, cand_items) for idx, b in enumerate(batches)]
        for f in as_completed(futures):
            res = f.result()
            all_results.extend(res)
            print(f"Worker completed batch ({len(res)} episodes). Total done so far: {len(all_results)}/{len(download_list)}")
            
    print(f"Fingerprinting finished in {time.time() - t0:.1f}s.")
    return all_results

if __name__ == "__main__":
    results = run_all_fingerprinting()
    
    # Map Leaderboard scores
    opponents_rows = []
    for r in results:
        tid = r["op_teamId"]
        lb_info = lb_data.get(tid, {})
        op_lb_score = lb_info.get("score", "N/A")
        op_lb_rank = lb_info.get("rank", "N/A")
        
        opponents_rows.append({
            "submission": r["submission_id"],
            "episode": r["episode"],
            "seed": r["seed"],
            "dp_seat": r["dp_seat"],
            "result": r["result"],
            "margin": r["margin"],
            "op_team": r["op_team"],
            "op_teamId": r["op_teamId"],
            "op_lb_score": op_lb_score,
            "op_lb_rank": op_lb_rank,
            "label": r["label"],
            "prefix_len": r["prefix_len"],
            "match_143/400/full": r["match_col"],
            "closest_file": r["closest_file"],
            "match_143": r["match_143"],
            "match_400": r["match_400"],
            "match_full": r["match_full"]
        })
        
    opponents_csv_path = os.path.join(OUT_DIR, "opponents.csv")
    fieldnames = [
        "submission", "episode", "seed", "dp_seat", "result", "margin",
        "op_team", "op_teamId", "op_lb_score", "op_lb_rank", "label",
        "prefix_len", "match_143/400/full", "closest_file",
        "match_143", "match_400", "match_full"
    ]
    with open(opponents_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(opponents_rows)
    print(f"Saved {len(opponents_rows)} rows to {opponents_csv_path}")

    # Generate summary.json
    # 1. Total games and W/L/D (downloaded)
    total_downloaded = len(opponents_rows)
    w_count = sum(1 for r in opponents_rows if r["result"] == "W")
    l_count = sum(1 for r in opponents_rows if r["result"] == "L")
    d_count = sum(1 for r in opponents_rows if r["result"] == "D")
    
    # 2. Per submission breakdown (downloaded)
    by_sub = defaultdict(lambda: {"total": 0, "W": 0, "L": 0, "D": 0})
    for r in opponents_rows:
        sid = r["submission"]
        by_sub[sid]["total"] += 1
        by_sub[sid][r["result"]] += 1
        
    # 3. Label breakdown (downloaded)
    by_label = defaultdict(lambda: {"count": 0, "W": 0, "L": 0, "D": 0})
    by_label_by_sub = defaultdict(lambda: defaultdict(lambda: {"count": 0, "W": 0, "L": 0, "D": 0}))
    for r in opponents_rows:
        sid = r["submission"]
        lbl = r["label"]
        by_label[lbl]["count"] += 1
        by_label[lbl][r["result"]] += 1
        by_label_by_sub[sid][lbl]["count"] += 1
        by_label_by_sub[sid][lbl][r["result"]] += 1
        
    # 4. Top 15 opponents defeating DP
    losses_by_op = defaultdict(lambda: {
        "losses": 0, "wins": 0, "draws": 0, "teamId": None,
        "lb_score": None, "labels": set(), "prefixes": [], "closest_files": set()
    })
    for r in opponents_rows:
        op = r["op_team"]
        losses_by_op[op]["teamId"] = r["op_teamId"]
        losses_by_op[op]["lb_score"] = r["op_lb_score"]
        losses_by_op[op]["labels"].add(r["label"])
        losses_by_op[op]["prefixes"].append(int(r["prefix_len"]))
        losses_by_op[op]["closest_files"].add(r["closest_file"])
        if r["result"] == "L":
            losses_by_op[op]["losses"] += 1
        elif r["result"] == "W":
            losses_by_op[op]["wins"] += 1
        else:
            losses_by_op[op]["draws"] += 1

    top15_opponents = sorted(losses_by_op.items(), key=lambda x: x[1]["losses"], reverse=True)[:15]
    top15_list = []
    for op, data in top15_opponents:
        top15_list.append({
            "team_name": op,
            "teamId": data["teamId"],
            "lb_score": data["lb_score"],
            "dp_vs_op_record": f"{data['wins']}-{data['losses']}-{data['draws']}",
            "dp_losses": data["losses"],
            "labels": list(data["labels"]),
            "max_prefix_len": max(data["prefixes"]) if data["prefixes"] else 0,
            "closest_files": list(data["closest_files"])
        })

    # 5. Loss margin distribution
    loss_margins = [float(r["margin"]) for r in opponents_rows if r["result"] == "L"]
    loss_margins.sort()
    count_below_1000 = sum(1 for m in loss_margins if m < -1000)
    
    quartiles = {}
    if loss_margins:
        n = len(loss_margins)
        quartiles = {
            "min": round(loss_margins[0], 1),
            "q1": round(loss_margins[n // 4], 1),
            "median": round(loss_margins[n // 2], 1),
            "q3": round(loss_margins[(3 * n) // 4], 1),
            "max": round(loss_margins[-1], 1),
            "count": n,
            "count_below_neg_1000": count_below_1000
        }

    # 6. Overall stats from episodes_all.json (all 884 episodes)
    episodes_all_path = os.path.join(OUT_DIR, "episodes_all.json")
    with open(episodes_all_path, "r", encoding="utf-8") as f:
        episodes_all = json.load(f)

    # 12-hour window stats
    parsed_all = []
    for ep in episodes_all:
        et_str = ep.get("endTime") or ep.get("createTime")
        if et_str:
            dt = datetime.fromisoformat(et_str.replace("Z", "+00:00"))
            parsed_all.append((dt, ep))

    parsed_all.sort(key=lambda x: x[0])
    windows_stats = []
    if parsed_all:
        min_dt = parsed_all[0][0]
        max_dt = parsed_all[-1][0]
        # Align start to 12h block (00:00 or 12:00 UTC)
        cur = min_dt.replace(minute=0, second=0, microsecond=0)
        cur = cur.replace(hour=0 if cur.hour < 12 else 12)
        while cur <= max_dt:
            nxt = cur + timedelta(hours=12)
            w_label = f"{cur.strftime('%m-%d %H:%M')} ~ {nxt.strftime('%m-%d %H:%M')} UTC"
            
            sub_w = defaultdict(lambda: {"W": 0, "L": 0, "D": 0, "total": 0})
            tot_w = {"W": 0, "L": 0, "D": 0, "total": 0}
            
            for dt, ep in parsed_all:
                if cur <= dt < nxt:
                    sid = ep["submission_id"]
                    res = ep["result"]
                    sub_w[sid]["total"] += 1
                    sub_w[sid][res] += 1
                    tot_w["total"] += 1
                    tot_w[res] += 1
                    
            windows_stats.append({
                "window": w_label,
                "overall": tot_w,
                "win_rate_overall": round(tot_w["W"] / tot_w["total"] * 100, 1) if tot_w["total"] > 0 else None,
                "per_submission": dict(sub_w)
            })
            cur = nxt

    summary_data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "total_all_episodes": len(episodes_all),
        "total_downloaded_games": total_downloaded,
        "downloaded_overall_record": {"W": w_count, "L": l_count, "D": d_count},
        "downloaded_submission_breakdown": dict(by_sub),
        "label_breakdown": dict(by_label),
        "label_by_submission": {str(k): dict(v) for k, v in by_label_by_sub.items()},
        "top_15_opponents_defeating_dp": top15_list,
        "loss_margin_distribution": quartiles,
        "twelve_hour_windows": windows_stats
    }
    
    summary_path = os.path.join(OUT_DIR, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print(f"Saved summary to {summary_path}")
