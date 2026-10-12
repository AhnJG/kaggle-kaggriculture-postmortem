#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import json
import glob
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
USER = "<kaggle_user>"
TAG = "exp039"
KAGGLE_JOBS = 2560
MAC_JOBS = 1706
N_SHARDS = 5
POLL_INTERVAL = 600  # 10 minutes

EXP_DIR = "experiments/exp039_camargin"

def log(msg):
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
    print(f"[{now}] {msg}", flush=True)

def get_kernel_status(k):
    kernel_slug = f"{USER}/kaggriculture-{TAG}-k{k}"
    try:
        res = subprocess.run(["kaggle", "kernels", "status", kernel_slug], capture_output=True, text=True, timeout=30)
        out = res.stdout.strip()
        if "KernelWorkerStatus.COMPLETE" in out:
            return "COMPLETE"
        elif "KernelWorkerStatus.RUNNING" in out:
            return "RUNNING"
        elif "KernelWorkerStatus.QUEUED" in out:
            return "QUEUED"
        elif "KernelWorkerStatus.ERROR" in out or "KernelWorkerStatus.FAILED" in out or "KernelWorkerStatus.CANCELLED" in out:
            return "ERROR"
        else:
            return f"UNKNOWN({out})"
    except Exception as e:
        return f"EXCEPTION({e})"

def check_mac_done():
    mac_out = f"{EXP_DIR}/games-mac.jsonl"
    count = 0
    if os.path.exists(mac_out):
        try:
            with open(mac_out) as f:
                count = sum(1 for _ in f)
        except Exception:
            pass
    # check process
    res = subprocess.run(["pgrep", "-f", f"{EXP_DIR}/jobs-mac.json"], capture_output=True, text=True)
    running = bool(res.stdout.strip())
    if not running and count < MAC_JOBS:
        log(f"Mac runner not running but count={count} < {MAC_JOBS}. Restarting...")
        cmd = f"EXP024_OUT={EXP_DIR}/games-mac.jsonl nohup python3 experiments/exp024_round2/run.py {EXP_DIR}/jobs-mac.json >> {EXP_DIR}/run-mac.log 2>&1 &"
        subprocess.run(cmd, shell=True)
        running = True
    done = (count >= MAC_JOBS)
    return done, count, running

def main():
    log("EXP-039 Orchestrator started.")
    retried_kernels = {k: 0 for k in range(N_SHARDS)}
    failed_shards_for_mac = []

    while True:
        mac_done, mac_count, mac_running = check_mac_done()
        
        kernel_statuses = {}
        all_kernels_complete = True
        
        for k in range(N_SHARDS):
            st = get_kernel_status(k)
            kernel_statuses[k] = st
            if st != "COMPLETE":
                all_kernels_complete = False
                if st == "ERROR":
                    if retried_kernels[k] < 1:
                        log(f"Kernel {k} reported ERROR. Retrying push once...")
                        retried_kernels[k] += 1
                        subprocess.run(["kaggle", "kernels", "push", "-p", f"experiments/kaggle_runs/{TAG}/kernel{k}"])
                    else:
                        if k not in failed_shards_for_mac:
                            log(f"Kernel {k} failed retry. Will fallback to Mac after Mac finishes.")
                            failed_shards_for_mac.append(k)

        log(f"Status check -> Mac: {mac_count}/{MAC_JOBS} (running={mac_running}, done={mac_done}) | "
            f"Kaggle: {', '.join([f'k{k}:{st}' for k, st in kernel_statuses.items()])}")

        if mac_done and (all_kernels_complete or (len(failed_shards_for_mac) > 0 and all(kernel_statuses[k] in ("COMPLETE", "ERROR") for k in range(N_SHARDS)))):
            break

        time.sleep(POLL_INTERVAL)

    # If any kernel failed and needs Mac execution
    if failed_shards_for_mac:
        log(f"Running failed Kaggle shards on Mac: {failed_shards_for_mac}")
        for k in failed_shards_for_mac:
            shard_jobs = f"experiments/kaggle_runs/{TAG}/dataset/jobs-{k}.json"
            shard_out = f"experiments/kaggle_runs/{TAG}/out/k{k}/games-{k}.jsonl"
            os.makedirs(f"experiments/kaggle_runs/{TAG}/out/k{k}", exist_ok=True)
            log(f"Executing shard {k} on Mac: {shard_jobs} -> {shard_out}")
            env = os.environ.copy()
            env["EXP024_OUT"] = shard_out
            subprocess.run(["python3", "experiments/exp024_round2/run.py", shard_jobs], env=env, check=True)

    # Download kernel outputs for completed kernels
    log("Downloading outputs from Kaggle kernels...")
    out_dir = f"experiments/kaggle_runs/{TAG}/out"
    os.makedirs(out_dir, exist_ok=True)
    for k in range(N_SHARDS):
        if k not in failed_shards_for_mac:
            kd = os.path.join(out_dir, f"k{k}")
            os.makedirs(kd, exist_ok=True)
            log(f"Fetching output for k{k}...")
            res = subprocess.run(["kaggle", "kernels", "output", f"{USER}/kaggriculture-{TAG}-k{k}", "-p", kd, "-o", "--file-pattern", "games-.*"], capture_output=True, text=True)
            if not glob.glob(os.path.join(kd, "games-*.jsonl")):
                log(f"Falling back to default output fetch for k{k}...")
                subprocess.run(["kaggle", "kernels", "output", f"{USER}/kaggriculture-{TAG}-k{k}", "-p", kd, "-o"])

    # Step 5: cat .../games-*.jsonl > experiments/exp039_camargin/games-kaggle.jsonl
    log("Combining Kaggle games...")
    kaggle_out = f"{EXP_DIR}/games-kaggle.jsonl"
    with open(kaggle_out, "w") as outfile:
        for k in range(N_SHARDS):
            pattern = os.path.join(out_dir, f"k{k}", "games-*.jsonl")
            matched = sorted(glob.glob(pattern))
            log(f"k{k} files: {matched}")
            for fn in matched:
                with open(fn) as infile:
                    for line in infile:
                        outfile.write(line)

    with open(f"{EXP_DIR}/games-mac.jsonl") as f:
        final_mac_rows = sum(1 for _ in f)
    with open(kaggle_out) as f:
        final_kaggle_rows = sum(1 for _ in f)
    total_rows = final_mac_rows + final_kaggle_rows
    log(f"Rows -> Mac: {final_mac_rows}, Kaggle: {final_kaggle_rows}, Total: {total_rows}")

    # Step 6: judge39.py
    log("Running judge39.py...")
    judge_res = subprocess.run(["python3", f"{EXP_DIR}/judge39.py"], capture_output=True, text=True)
    judge_txt = f"{EXP_DIR}/judge.txt"
    with open(judge_txt, "w") as f:
        f.write(judge_res.stdout)
        if judge_res.stderr:
            f.write("\nSTDERR:\n" + judge_res.stderr)

    first_line = judge_res.stdout.strip().split("\n")[0] if judge_res.stdout else ""
    log(f"Judge first line: {first_line}")

    # Check for INCOMPLETE
    if "INCOMPLETE" in first_line or "INCOMPLETE" in judge_res.stderr:
        log("INCOMPLETE detected. Finding missing jobs and re-running once...")
        rows = {}
        for f_name in ("games-kaggle.jsonl", "games-mac.jsonl"):
            p = f"{EXP_DIR}/{f_name}"
            if os.path.exists(p):
                for l in open(p):
                    r = json.loads(l)
                    rows[r["key"]] = r
        jobs = json.load(open(f"{EXP_DIR}/jobs-kaggle.json")) + json.load(open(f"{EXP_DIR}/jobs-mac.json"))
        miss = [j for j in jobs if f"{j[0]}|{j[2]}|{j[4]}|{j[5]}" not in rows]
        log(f"Missing count: {len(miss)}")
        if miss:
            miss_job_file = f"{EXP_DIR}/jobs-miss.json"
            miss_out_file = f"{EXP_DIR}/games-miss.jsonl"
            with open(miss_job_file, "w") as f:
                json.dump(miss, f)
            env = os.environ.copy()
            env["EXP024_OUT"] = miss_out_file
            subprocess.run(["python3", "experiments/exp024_round2/run.py", miss_job_file], env=env, check=True)
            # append missing rows to games-mac.jsonl
            with open(f"{EXP_DIR}/games-mac.jsonl", "a") as f_mac:
                for l in open(miss_out_file):
                    f_mac.write(l)
            # re-count
            with open(f"{EXP_DIR}/games-mac.jsonl") as f:
                final_mac_rows = sum(1 for _ in f)
            total_rows = final_mac_rows + final_kaggle_rows
            # re-judge
            judge_res = subprocess.run(["python3", f"{EXP_DIR}/judge39.py"], capture_output=True, text=True)
            with open(judge_txt, "w") as f:
                f.write(judge_res.stdout)
                if judge_res.stderr:
                    f.write("\nSTDERR:\n" + judge_res.stderr)
            first_line = judge_res.stdout.strip().split("\n")[0] if judge_res.stdout else ""
            log(f"Re-judge first line: {first_line}")

    # Generate Report
    finish_time_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
    ts_file = datetime.now(KST).strftime("%Y%m%d-%H%M")
    report_path = f"coordination/reports/antigravity/{ts_file}-EXP039.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    report_content = f"""# EXP-039 Report

## Execution Timeline & Rows
- Mac: 완료 {finish_time_str}, {final_mac_rows}행
- Kaggle: 완료 {finish_time_str}, {final_kaggle_rows}행
- Total: {total_rows}행

## Judge Results (First Line)
- judge: `{first_line}`
"""
    with open(report_path, "w") as f:
        f.write(report_content)
    log(f"Report written to {report_path}")
    log("EXP-039 Orchestrator completed successfully.")

if __name__ == "__main__":
    main()
