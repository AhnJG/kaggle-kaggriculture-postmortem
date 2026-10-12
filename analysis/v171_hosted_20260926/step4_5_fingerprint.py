#!/usr/bin/env python3
import os
import sys
import glob
import json
import csv
import time
import gzip
import hashlib
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

from kaggle_environments import make, agent

OUT_DIR = "analysis/v171_hosted_20260926"
RAW_DIR = "private_artifacts/v171_hosted_20260926/raw"

V171_PATH = "releases/mirror-screen-v171/main.py"
V074_PATH = "releases/round2-v074/main.py"

episodes_path = os.path.join(OUT_DIR, "episodes_all.json")
if not os.path.exists(episodes_path):
    print(f"Error: {episodes_path} not found.")
    sys.exit(1)

with open(episodes_path, "r", encoding="utf-8") as f:
    episodes = json.load(f)

# Filter out missing/corrupted replays if any
valid_episodes = [ep for ep in episodes if ep.get("seed") is not None and not ep.get("replay_missing") and not ep.get("replay_corrupt")]
print(f"Loaded {len(valid_episodes)} valid episodes to fingerprint (out of {len(episodes)} total).")

# Build unique candidate refs
refs_defs = [
    # 17 refs
    ("C1", "releases/public-nathanjacob-pipe16-exact/main.py"),
    ("C2", "releases/public-thomastschinkel-metav4-v13-exact/main.py"),
    ("C3", "releases/public-thomastschinkel-2945-farm-exact/main.py"),
    ("C4", "releases/public-ozer-v53-exact/main.py"),
    ("C5", "releases/public-ozer-v51-exact/main.py"),
    ("P2", "releases/public-lynnsakurai-farming-score-v2-exact/main.py"),
    ("OMW", "releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py"),
    ("more-wheat-smarter-sales", "releases/public-dmitriigluzdov-kaggriculture-more-wheat-smarter-sales-exact/main.py"),
    ("7-turn-rescue", "releases/public-dmitriigluzdov-kaggriculture-7-turn-rescue-historical-lb-2800-exact/main.py"),
    ("a-smaller-market-shock", "releases/public-dmitriigluzdov-kaggriculture-a-smaller-market-shock-exact/main.py"),
    ("EXP-016", "releases/f0-c1-adv-exp016/main.py"),
    ("EXP-017", "releases/f0-omw-adv-exp017/main.py"),
    ("multi-route-0922", "analysis/daily_scan/20260922/extracted/kaggriculture-multi-route-farming-agent/main.py"),
    ("v56-smarter", "analysis/daily_scan/20260922/extracted/kaggriculture-v56-smarter-seeds-and-fertilizer/main.py"),
    ("harvest-ledger-0922", "analysis/daily_scan/20260922/extracted/kaggriculture-harvest-ledger/main.py"),
    ("order-book", "analysis/daily_scan/20260922/extracted/your-market-list-is-an-order-book/main.py"),
    ("farmer-john", "analysis/daily_scan/20260922/extracted/farmer-john-and-the-wheat-seller/main.py"),
    # 127ed3e6
    ("127ed3e6", "releases/public-newmeta-127ed3e6-exact/main.py"),
    # DP 0924 exact
    ("DP-0924", "releases/public-tetsutani-demand-preserving-0924-exact/main.py"),
    # 09-26 new files
    ("0926-song-ice-fire", "analysis/daily_scan/20260926/extracted/a-song-of-ice-and-fire-fixed-flexible/main.py"),
    ("0926-harvest-ledger", "analysis/daily_scan/20260926/extracted/kaggriculture-harvest-ledger/main.py"),
    ("0926-multi-route", "analysis/daily_scan/20260926/extracted/kaggriculture-multi-route-farming-agent/main.py"),
    ("0926-top2-v4", "analysis/daily_scan/20260926/extracted/kaggriculture-top-2-master-engine-v4/main.py"),
    ("0926-hack", "analysis/daily_scan/20260926/extracted/kaggriculture-hack/main.py"),
    # herd-safe-v3
    ("herd-safe-v3", "releases/public-herd-safe-v3-experimental-risk-aware-feed-exact/main.py")
]

with open("experiments/exp023_mirror_screen/stage3-opponents.json", "r", encoding="utf-8") as f:
    s3 = json.load(f)
for idx, p in enumerate(s3.get("public_top15", [])):
    dir_name = os.path.basename(os.path.dirname(p["path"]))
    refs_defs.append((f"stage3_{dir_name}", p["path"]))

by_sha = {}
for name, path in refs_defs:
    with open(path, "rb") as f:
        c = f.read().replace(b"\r\n", b"\n")
    sha = hashlib.sha256(c).hexdigest()
    if sha not in by_sha:
        by_sha[sha] = {"name": name, "path": path, "aliases": [name], "sha256": sha}
    else:
        by_sha[sha]["aliases"].append(name)

candidates_list = list(by_sha.values())
print(f"Total unique reference candidates collected: {len(candidates_list)}")

file_hashes_path = os.path.join(OUT_DIR, "file_hashes.json")
with open(file_hashes_path, "w", encoding="utf-8") as f:
    json.dump(by_sha, f, indent=2)

def worker_process_chunk(chunk_episodes, candidates_info, v171_path, v074_path, raw_dir):
    # Load our bots
    with open(v171_path, "r", encoding="utf-8") as f:
        v171_code = f.read()
    v171_fn = agent.get_last_callable(v171_code, path=v171_path)

    with open(v074_path, "r", encoding="utf-8") as f:
        v074_code = f.read()
    v074_fn = agent.get_last_callable(v074_code, path=v074_path)

    # Load candidate bots
    cand_fns = []
    for c_info in candidates_info:
        try:
            with open(c_info["path"], "r", encoding="utf-8") as f:
                c_code = f.read()
            fn = agent.get_last_callable(c_code, path=c_info["path"])
            cand_fns.append((c_info["name"], c_info["aliases"], c_info["sha256"], fn))
        except Exception as e:
            pass

    results = []
    for ep in chunk_episodes:
        eid = ep["id"]
        seat = int(ep["our_seat"])
        op_seat = 1 - seat
        seed = int(ep["seed"])
        sub_id = ep["submission_id"]

        our_fn = v171_fn if sub_id == 56567563 else v074_fn

        gz_path = os.path.join(raw_dir, f"{eid}.json.gz")
        if not os.path.exists(gz_path):
            continue

        try:
            with gzip.open(gz_path, "rt", encoding="utf-8") as f:
                rdata = json.load(f)
        except Exception as e:
            continue

        steps = rdata.get("steps", [])
        hosted_op_actions = [st[op_seat].get("action") for st in steps[1:]]
        total_steps = len(hosted_op_actions)

        best_prefix = -1
        best_cands = []
        is_full = False
        is_127ed3e6_family = False

        # Phase 1: 144 step screen (143 actions)
        full_check_candidates = []
        for c_name, c_aliases, sha, c_fn in cand_fns:
            env = make("kaggriculture", configuration={"episodeSteps": 144, "seed": seed})
            agents = [None, None]
            agents[seat] = our_fn
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
                full_check_candidates.append((c_name, c_aliases, sha, c_fn))

        # Phase 2: If 143 matched, run full 720 steps to check for FULL match
        if full_check_candidates:
            for c_name, c_aliases, sha, c_fn in full_check_candidates:
                env_full = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
                agents_full = [None, None]
                agents_full[seat] = our_fn
                agents_full[op_seat] = c_fn
                env_full.run(agents_full)

                local_full = [st[op_seat].get("action") for st in env_full.steps[1:]]
                limit_full = min(len(local_full), len(hosted_op_actions))
                full_match = 0
                for i in range(limit_full):
                    if local_full[i] == hosted_op_actions[i]:
                        full_match += 1
                    else:
                        break

                if full_match > best_prefix:
                    best_prefix = full_match
                    best_cands = [c_name]
                elif full_match == best_prefix and full_match > 143:
                    if c_name not in best_cands:
                        best_cands.append(c_name)

                if full_match >= total_steps or full_match >= 719:
                    is_full = True

        label = "UNKNOWN"
        cand_str = "|".join(best_cands) if best_cands else "none"
        if is_full:
            label = f"{cand_str} (FULL)"
        elif best_prefix == 143:
            label = f"{cand_str} (prefix 143)"
        elif best_prefix > 0:
            label = f"{cand_str} (prefix {best_prefix})"
        else:
            label = "UNKNOWN (prefix 0)"

        # Check 127ed3e6 family
        if "127ed3e6" in cand_str:
            is_127ed3e6_family = True

        results.append({
            "submission_id": sub_id,
            "submission_label": ep.get("submission_label"),
            "episode": eid,
            "seed": seed,
            "seat": seat,
            "result": ep.get("result"),
            "margin": ep.get("margin"),
            "our_reward": ep.get("our_reward"),
            "op_reward": ep.get("op_reward"),
            "op_team": ep.get("op_teamName"),
            "op_teamId": ep.get("op_teamId"),
            "op_submissionId": ep.get("op_submissionId"),
            "op_lb_score": ep.get("op_lb_score"),
            "endTime": ep.get("endTime"),
            "label": label,
            "prefix_len": 720 if is_full else best_prefix,
            "is_full": is_full,
            "is_127ed3e6": is_127ed3e6_family
        })

    return results

def main():
    # Split episodes into chunks for 5 workers
    num_workers = 5
    chunks = [[] for _ in range(num_workers)]
    for idx, ep in enumerate(valid_episodes):
        chunks[idx % num_workers].append(ep)

    print(f"Launching {num_workers} parallel workers on {len(valid_episodes)} episodes...")
    t_start = time.time()
    all_results = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(
                worker_process_chunk,
                chunks[i],
                candidates_list,
                V171_PATH,
                V074_PATH,
                RAW_DIR
            ): i for i in range(num_workers)
        }

        done_workers = 0
        for fut in as_completed(futures):
            w_idx = futures[fut]
            try:
                chunk_res = fut.result()
                all_results.extend(chunk_res)
                done_workers += 1
                print(f"Worker {w_idx} finished ({len(chunk_res)} episodes processed). Total done: {done_workers}/{num_workers}")
            except Exception as e:
                print(f"Worker {w_idx} failed with error: {e}")

    all_results.sort(key=lambda x: (x["submission_label"], x["endTime"]), reverse=True)
    print(f"Fingerprinting complete: {len(all_results)} episodes in {time.time() - t_start:.1f}s.")

    # Write opponents.csv
    csv_path = os.path.join(OUT_DIR, "opponents.csv")
    fieldnames = [
        "episode", "submission_id", "submission_label", "seed", "seat",
        "result", "margin", "our_reward", "op_reward", "op_team", "op_teamId",
        "op_submissionId", "op_lb_score", "label", "prefix_len", "is_full", "is_127ed3e6", "endTime"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    print(f"Saved {len(all_results)} rows to {csv_path}")

    # Step 5: Summary statistics
    # Overall W/D/L
    def calc_wdl(sub_list):
        w = sum(1 for x in sub_list if x["result"] == "W")
        d = sum(1 for x in sub_list if x["result"] == "D")
        l = sum(1 for x in sub_list if x["result"] == "L")
        tot = w + d + l
        win_rate = (w / tot) if tot > 0 else 0.0
        return {"W": w, "D": d, "L": l, "total": tot, "win_rate": round(win_rate, 4)}

    summary = {}

    # By submission (v171, v074)
    for sub_lbl in ["v171", "v074"]:
        sub_eps = [x for x in all_results if x["submission_label"] == sub_lbl]
        if not sub_eps:
            continue

        # LB bands: <2200 / 2200-2400 / 2400-2600 / 2600+
        def get_lb_band(score):
            if score is None:
                return "unknown"
            if score < 2200:
                return "<2200"
            elif score < 2400:
                return "2200-2400"
            elif score < 2600:
                return "2400-2600"
            else:
                return "2600+"

        lb_bands = defaultdict(list)
        for x in sub_eps:
            lb_bands[get_lb_band(x["op_lb_score"])].append(x)

        lb_summary = {band: calc_wdl(sub_list) for band, sub_list in sorted(lb_bands.items())}

        # By label
        by_label = defaultdict(list)
        for x in sub_eps:
            by_label[x["label"]].append(x)
        label_summary = {lbl: calc_wdl(sub_list) for lbl, sub_list in sorted(by_label.items(), key=lambda k: len(k[1]), reverse=True)}

        # FULL matches vs non-FULL
        full_eps = [x for x in sub_eps if x["is_full"]]
        non_full_eps = [x for x in sub_eps if not x["is_full"]]

        # 127ed3e6 family vs other
        family_127 = [x for x in sub_eps if x["is_127ed3e6"]]
        non_family_127 = [x for x in sub_eps if not x["is_127ed3e6"]]

        # Losses list
        losses = [
            {
                "episode": x["episode"],
                "op_team": x["op_team"],
                "op_lb_score": x["op_lb_score"],
                "label": x["label"],
                "prefix_len": x["prefix_len"],
                "margin": x["margin"],
                "seed": x["seed"],
                "seat": x["seat"]
            }
            for x in sub_eps if x["result"] == "L"
        ]

        summary[sub_lbl] = {
            "overall": calc_wdl(sub_eps),
            "by_lb_band": lb_summary,
            "full_match": calc_wdl(full_eps),
            "non_full_match": calc_wdl(non_full_eps),
            "127ed3e6_family": calc_wdl(family_127),
            "non_127ed3e6_family": calc_wdl(non_family_127),
            "by_label": label_summary,
            "loss_count": len(losses),
            "losses": losses
        }

    summary_path = os.path.join(OUT_DIR, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved summary to {summary_path}")

if __name__ == '__main__':
    main()
