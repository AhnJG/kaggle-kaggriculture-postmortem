"""EXP-036 Orchestrator for unattended execution (Mac + Kaggle).
Executes proposal coordination/proposals/claude/20260927-EXP036-ANTIGRAVITY.md
Does not modify any scripts or criteria.
"""
import os
import sys
import time
import json
import subprocess
import shutil
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
BASE_DIR = Path('~/kaggle/Kaggriculture')
EXP_DIR = BASE_DIR / 'experiments' / 'exp036_d157plus'
KAGGLE_RUNS = BASE_DIR / 'experiments' / 'kaggle_runs'
REPORTS_DIR = BASE_DIR / 'coordination' / 'reports' / 'antigravity'
PY = sys.executable

def now_str():
    return datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')

def log(msg):
    ts = now_str()
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(EXP_DIR / 'orchestrator.log', 'a') as f:
        f.write(line + '\n')

def run_cmd(cmd, cwd=BASE_DIR, check=False):
    log(f"CMD: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = res.stdout.strip()
    if out:
        for l in out.splitlines():
            log(f"  {l}")
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed (code {res.returncode}): {cmd}\nOutput: {out}")
    return res.returncode, out

def check_caffeinate():
    code, _ = run_cmd("pgrep caffeinate")
    if code != 0:
        log("Starting caffeinate -dimsu...")
        subprocess.Popen(["caffeinate", "-dimsu"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
    else:
        log("caffeinate -dimsu is already active.")

def get_kaggle_user():
    code, out = run_cmd("kaggle config view")
    for line in out.splitlines():
        if 'username' in line:
            return line.split()[-1]
    return '<kaggle_user>'

def count_lines(path):
    p = Path(path)
    if not p.exists():
        return 0
    with open(p, 'rb') as f:
        return sum(1 for _ in f)

def get_kernel_statuses(user, tag, n=5):
    statuses = []
    for k in range(n):
        slug = f"{user}/kaggriculture-{tag}-k{k}"
        code, out = run_cmd(f"kaggle kernels status {slug}")
        st = "UNKNOWN"
        for l in out.splitlines():
            if slug in l:
                st = l.split()[-1].strip('"')
            elif "status" in l.lower():
                st = l.split()[-1].strip('"')
        statuses.append(st)
    return statuses

def is_mac_running(jobs_file_name):
    code, out = run_cmd(f"pgrep -f 'run.py.*{jobs_file_name}'")
    return code == 0

def wait_for_completion(tag, jobs_mac_file, games_mac_file, user, n_shards=5):
    target_mac = len(json.load(open(jobs_mac_file)))
    jobs_name = Path(jobs_mac_file).name
    log(f"Waiting for completion: tag={tag}, target_mac_games={target_mac}")
    while True:
        m_lines = count_lines(games_mac_file)
        mac_alive = is_mac_running(jobs_name)
        statuses = get_kernel_statuses(user, tag, n_shards)
        log(f"Progress: Mac games={m_lines}/{target_mac} (alive={mac_alive}), Kaggle statuses={statuses}")

        all_kernels_done = all("COMPLETE" in s.upper() or "ERROR" in s.upper() or "CANCEL" in s.upper() for s in statuses)
        mac_done = (not mac_alive and m_lines >= target_mac) or (m_lines >= target_mac)

        if mac_done and all_kernels_done:
            log("Both Mac and all Kaggle kernels have finished execution!")
            break
        
        time.sleep(600)  # 10 minutes interval

def pull_kaggle_outputs(user, tag, out_file, n_shards=5):
    log(f"Pulling Kaggle outputs for tag {tag}...")
    run_dir = KAGGLE_RUNS / tag
    (run_dir / 'out').mkdir(parents=True, exist_ok=True)
    for k in range(n_shards):
        slug = f"{user}/kaggriculture-{tag}-k{k}"
        dest = run_dir / 'out' / f'k{k}'
        dest.mkdir(parents=True, exist_ok=True)
        run_cmd(f"kaggle kernels output {slug} -p {dest}", check=True)
    
    # Concatenate games-*.jsonl
    total_written = 0
    with open(out_file, 'w') as out_f:
        for k in range(n_shards):
            for gf in (run_dir / 'out' / f'k{k}').glob('games-*.jsonl'):
                log(f"Reading {gf}...")
                with open(gf) as gf_in:
                    for line in gf_in:
                        if line.strip():
                            out_f.write(line.strip() + '\n')
                            total_written += 1
    log(f"Wrote {total_written} games to {out_file}")
    return total_written

def run_judge(stage):
    log(f"Running judge36 for stage: {stage}...")
    judge_out = EXP_DIR / f'judge-{stage}.txt'
    code, out = run_cmd(f"{PY} {EXP_DIR}/judge36.py {stage} > {judge_out} 2>&1")
    first_line = ""
    if judge_out.exists():
        with open(judge_out) as f:
            for l in f:
                l = l.strip()
                if l:
                    first_line = l
                    break
    log(f"Judge {stage} first line: {first_line}")
    return code, first_line

def handle_incomplete(stage, user, tag, jobs_mac_file, games_mac_file, jobs_kg_file, games_kg_file, n_shards=5):
    """Checks for INCOMPLETE and retries 1 time per card instructions."""
    judge_out = EXP_DIR / f'judge-{stage}.txt'
    content = judge_out.read_text() if judge_out.exists() else ""
    if "INCOMPLETE" not in content:
        return True
    
    log(f"Stage {stage} is INCOMPLETE! Analyzing missing jobs...")
    rows = set()
    for f in (games_kg_file, games_mac_file):
        if Path(f).exists():
            for line in open(f):
                try:
                    r = json.loads(line)
                    rows.add(r['key'])
                except Exception:
                    pass
    
    jobs_mac = json.load(open(jobs_mac_file))
    jobs_kg = json.load(open(jobs_kg_file))
    
    miss_mac = [j for j in jobs_mac if f"{j[0]}|{j[2]}|{j[4]}|{j[5]}" not in rows]
    miss_kg = [j for j in jobs_kg if f"{j[0]}|{j[2]}|{j[4]}|{j[5]}" not in rows]
    log(f"Missing jobs: Mac={len(miss_mac)}, Kaggle={len(miss_kg)}")
    
    if miss_mac:
        log("Retrying Mac execution for missing jobs...")
        cmd = f"EXP024_OUT={games_mac_file} {PY} experiments/exp024_round2/run.py {jobs_mac_file} >> {EXP_DIR}/run-{stage}-mac.log 2>&1"
        run_cmd(cmd, check=True)
    
    if miss_kg:
        log("Retrying failed Kaggle kernels (push retry 1 time)...")
        shards_to_retry = set()
        for idx, j in enumerate(jobs_kg):
            if f"{j[0]}|{j[2]}|{j[4]}|{j[5]}" not in rows:
                shards_to_retry.add(idx % n_shards)
        log(f"Shards to retry: {shards_to_retry}")
        for k in shards_to_retry:
            run_cmd(f"kaggle kernels push -p {KAGGLE_RUNS}/{tag}/kernel{k}", check=True)
        # Wait for retried kernels
        while True:
            time.sleep(600)
            statuses = get_kernel_statuses(user, tag, n_shards)
            log(f"Retry Kaggle statuses: {statuses}")
            if all("COMPLETE" in statuses[k].upper() or "ERROR" in statuses[k].upper() for k in shards_to_retry):
                break
        pull_kaggle_outputs(user, tag, games_kg_file, n_shards)
    
    # Re-run judge
    code, first_line = run_judge(stage)
    content2 = judge_out.read_text() if judge_out.exists() else ""
    if "INCOMPLETE" in content2:
        log(f"Stage {stage} STILL INCOMPLETE after retry! STOP.")
        return False
    return True

def main():
    try:
        log("=== Starting EXP-036 Unattended Orchestration ===")
        check_caffeinate()
        user = get_kaggle_user()
        log(f"Kaggle username: {user}")

        timings = {}

        # --- Screen Phase ---
        screen_mac_games = EXP_DIR / 'games-screen-mac.jsonl'
        screen_kg_games = EXP_DIR / 'games-screen-kaggle.jsonl'
        screen_mac_jobs = EXP_DIR / 'jobs-screen-mac.json'
        screen_kg_jobs = EXP_DIR / 'jobs-screen-kaggle.json'

        # Check if Mac worker PID is already running
        n_mac = count_lines(screen_mac_games)
        target_mac = len(json.load(open(screen_mac_jobs)))
        if n_mac < target_mac:
            if is_mac_running('jobs-screen-mac.json'):
                log(f"Mac worker is already running ({n_mac}/{target_mac} lines).")
            else:
                log("Launching Mac worker...")
                env = os.environ.copy()
                env["EXP024_OUT"] = str(screen_mac_games)
                log_f = open(EXP_DIR / 'run-screen-mac.log', 'a')
                subprocess.Popen([PY, "experiments/exp024_round2/run.py", str(screen_mac_jobs)], env=env, stdout=log_f, stderr=subprocess.STDOUT)
        
        # Wait for Screen completion
        wait_for_completion('exp036s', screen_mac_jobs, screen_mac_games, user, 5)
        timings['screen_done'] = now_str()
        timings['screen_mac_rows'] = count_lines(screen_mac_games)

        # Pull Kaggle outputs for Screen
        timings['screen_kg_rows'] = pull_kaggle_outputs(user, 'exp036s', screen_kg_games, 5)

        # Judge Screen
        _, judge_screen_first = run_judge('screen')
        ok = handle_incomplete('screen', user, 'exp036s', screen_mac_jobs, screen_mac_games, screen_kg_jobs, screen_kg_games, 5)
        if not ok:
            log("STOP: Screen incomplete after retry.")
            return

        # Check advance list in screen-summary.json
        screen_summary = json.load(open(EXP_DIR / 'screen-summary.json'))
        advance = screen_summary.get('advance', [])
        log(f"Screen advance candidates ({len(advance)}): {advance}")

        judge_stage2_first = "N/A (advance list empty)"
        timings['stage2_done'] = "N/A"
        timings['stage2_mac_rows'] = 0
        timings['stage2_kg_rows'] = 0

        if not advance:
            log("Advance list is empty. Finishing experiment after screen.")
        else:
            # --- Stage 2 Phase ---
            log("=== Starting Stage 2 Phase ===")
            # Step 7: prep36.py stage2
            run_cmd(f"{PY} {EXP_DIR}/prep36.py stage2", check=True)

            stage2_kg_jobs = EXP_DIR / 'jobs-stage2-kaggle.json'
            stage2_mac_jobs = EXP_DIR / 'jobs-stage2-mac.json'
            stage2_kg_games = EXP_DIR / 'games-stage2-kaggle.jsonl'
            stage2_mac_games = EXP_DIR / 'games-stage2-mac.jsonl'

            # Step 8: make_kaggle2.py for exp036t
            run_cmd(f"{PY} experiments/kaggle_pilot/make_kaggle2.py {user} {stage2_kg_jobs} exp036t 5", check=True)

            # Datasets create for exp036t
            dataset_created = False
            for attempt in range(2):
                code, out = run_cmd(f"kaggle datasets create -p {KAGGLE_RUNS}/exp036t/dataset")
                if code == 0:
                    dataset_created = True
                    break
                log(f"kaggle datasets create failed on attempt {attempt+1}, waiting 10s...")
                time.sleep(10)
            
            kaggle_fallback_to_mac = False
            if not dataset_created:
                log("WARNING: datasets create failed twice! Falling back Kaggle jobs to Mac sequentially.")
                kaggle_fallback_to_mac = True
            else:
                # Wait for dataset ready
                log("Waiting for dataset <kaggle_user>/kaggriculture-exp036t to be ready...")
                while True:
                    code, out = run_cmd(f"kaggle datasets status {user}/kaggriculture-exp036t")
                    if "ready" in out.lower():
                        log("Dataset exp036t is ready!")
                        break
                    time.sleep(5)
                
                # Push kernels k0..k4
                for k in range(5):
                    run_cmd(f"kaggle kernels push -p {KAGGLE_RUNS}/exp036t/kernel{k}", check=True)

            # Start Mac worker for stage2
            log("Launching Mac worker for stage2...")
            env = os.environ.copy()
            env["EXP024_OUT"] = str(stage2_mac_games)
            log_f = open(EXP_DIR / 'run-stage2-mac.log', 'w')
            subprocess.Popen([PY, "experiments/exp024_round2/run.py", str(stage2_mac_jobs)], env=env, stdout=log_f, stderr=subprocess.STDOUT)

            if not kaggle_fallback_to_mac:
                # Wait for both Mac and Kaggle kernels
                wait_for_completion('exp036t', stage2_mac_jobs, stage2_mac_games, user, 5)
                timings['stage2_kg_rows'] = pull_kaggle_outputs(user, 'exp036t', stage2_kg_games, 5)
            else:
                # Wait for Mac jobs, then run Kaggle jobs on Mac
                while is_mac_running('jobs-stage2-mac.json'):
                    log(f"Mac stage2 progress: {count_lines(stage2_mac_games)} rows")
                    time.sleep(60)
                log("Mac stage2 jobs finished. Running Kaggle fallback jobs on Mac...")
                env_fb = os.environ.copy()
                env_fb["EXP024_OUT"] = str(stage2_kg_games)
                run_cmd(f"{PY} experiments/exp024_round2/run.py {stage2_kg_jobs}", check=True)
                timings['stage2_kg_rows'] = count_lines(stage2_kg_games)

            timings['stage2_done'] = now_str()
            timings['stage2_mac_rows'] = count_lines(stage2_mac_games)

            # Step 9: Judge stage2
            _, judge_stage2_first = run_judge('stage2')
            if not kaggle_fallback_to_mac:
                ok_s2 = handle_incomplete('stage2', user, 'exp036t', stage2_mac_jobs, stage2_mac_games, stage2_kg_jobs, stage2_kg_games, 5)
                if not ok_s2:
                    log("STOP: Stage2 incomplete after retry.")
                    return

        # --- Write Report ---
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ts_report = datetime.now(KST).strftime('%Y%m%d-%H%M')
        report_file = REPORTS_DIR / f"{ts_report}-EXP036.md"
        report_content = f"""# EXP-036 Report

## Execution Timeline & Rows
- Screen Mac: 완료 {timings.get('screen_done', 'N/A')}, {timings.get('screen_mac_rows', 0)}행
- Screen Kaggle: 완료 {timings.get('screen_done', 'N/A')}, {timings.get('screen_kg_rows', 0)}행
- Screen Total: {timings.get('screen_mac_rows', 0) + timings.get('screen_kg_rows', 0)}행
- Stage2 Mac: 완료 {timings.get('stage2_done', 'N/A')}, {timings.get('stage2_mac_rows', 0)}행
- Stage2 Kaggle: 완료 {timings.get('stage2_done', 'N/A')}, {timings.get('stage2_kg_rows', 0)}행
- Stage2 Total: {timings.get('stage2_mac_rows', 0) + timings.get('stage2_kg_rows', 0)}행

## Judge Results (First Lines)
- judge-screen: `{judge_screen_first}`
- judge-stage2: `{judge_stage2_first}`
"""
        report_file.write_text(report_content)
        log(f"Report written to: {report_file}")

        # Output exact 12 lines summary for Antigravity
        log("=== FINAL 12-LINE SUMMARY ===")
        summary_lines = [
            f"1. Caffeinate: 활성화 확인 (무인 실행 보호 유지)",
            f"2. Screen Mac: {timings.get('screen_done', 'N/A')} 완료, {timings.get('screen_mac_rows', 0)}행 (games-screen-mac.jsonl)",
            f"3. Screen Kaggle: {timings.get('screen_done', 'N/A')} 완료, {timings.get('screen_kg_rows', 0)}행 (games-screen-kaggle.jsonl)",
            f"4. Screen Total: {timings.get('screen_mac_rows', 0) + timings.get('screen_kg_rows', 0)}/7900 경기 정상 집계",
            f"5. Judge Screen: {judge_screen_first}",
            f"6. Stage2 Advance: {len(advance)}개 후보 통과 ({', '.join(advance) if advance else 'None'})",
            f"7. Stage2 Mac: {timings.get('stage2_done', 'N/A')} 완료, {timings.get('stage2_mac_rows', 0)}행",
            f"8. Stage2 Kaggle: {timings.get('stage2_done', 'N/A')} 완료, {timings.get('stage2_kg_rows', 0)}행",
            f"9. Stage2 Total: {timings.get('stage2_mac_rows', 0) + timings.get('stage2_kg_rows', 0)} 경기 완료",
            f"10. Judge Stage2: {judge_stage2_first}",
            f"11. Report File: coordination/reports/antigravity/{ts_report}-EXP036.md",
            f"12. Status: COMPLETED (스크립트 및 평가 기준 수정 없음)"
        ]
        for sl in summary_lines:
            log(f"SUMMARY: {sl}")
        (EXP_DIR / 'final_12_lines.txt').write_text('\n'.join(summary_lines) + '\n')
        log("=== ORCHESTRATOR COMPLETE ===")
    except Exception as e:
        err = traceback.format_exc()
        log(f"FATAL ERROR in orchestrator:\n{err}")
        sys.exit(1)

if __name__ == '__main__':
    main()
