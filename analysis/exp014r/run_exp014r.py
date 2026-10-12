#!/usr/bin/env python3
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path("~/kaggle/Kaggriculture")
RAW_DIR = BASE_DIR / "analysis/exp014r/raw"
SUMMARY_PATH = BASE_DIR / "analysis/exp014r/summary.json"

EXPECTED_SHAS = {
    "experiments/cards/EXP-014R-mirror-sale-lead-replication.md": "73019a7a3abb78c7147eab54501dfc86c65c59b690f46a8a054a3f94b5c6309c",
    "releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz": "1178ffa0614673a58fb1ee5b2a44003eecd5640634d6f3471e84ac92c1fbf388",
    "releases/f0-mirror-lead-exp014/submission.tar.gz": "be529b5cce50c53e738b79094e41852d8195b4f03cb8a391fd1c9ddee1600d29",
    "releases/public-alperen-before-dawn-stock-cash-sales-exact/submission.tar.gz": "cce494e5419f06028fa3fd19ddf0f2400e661427132c895664469f4fe6c5a9ec",
    "releases/public-goodpjw2008-kaggriculture-melon-threshold-squeeze-2749-exact/submission.tar.gz": "cfdd7f6c9513155b960776311c7a12bd73ff2146f8f56498646ccfbcb2e27f63",
    "releases/public-seyitkaangunes-kaggriculture-2820-score-exact/submission.tar.gz": "f623578bdd7e62558626d4fdcc332060f8db1d1b06ee4e1ce34ff72ca82a9114",
    "releases/public-tetsutani-market-smart-farming-exact/submission.tar.gz": "f5e41bd0ddad50a109f12381cc532cdc10b9e9d93dd6c6ab37cff47dfbc4916e",
    "releases/public-yhay81-shop-router-0909-exact/submission.tar.gz": "40d2bc3986f4ed3e927c81842d399a58bf20b07b57858355da4b75c280fd7791",
}

PANEL_OPPONENTS = {
    "alperen": "releases/public-alperen-before-dawn-stock-cash-sales-exact/main.py",
    "goodpjw2008": "releases/public-goodpjw2008-kaggriculture-melon-threshold-squeeze-2749-exact/main.py",
    "seyitkaangunes": "releases/public-seyitkaangunes-kaggriculture-2820-score-exact/main.py",
    "tetsutani": "releases/public-tetsutani-market-smart-farming-exact/main.py",
    "yhay81": "releases/public-yhay81-shop-router-0909-exact/main.py",
}

P2_AGENT = "releases/public-lynnsakurai-farming-score-v2-exact/main.py"
VARIANT_AGENT = "releases/f0-mirror-lead-exp014/main.py"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def verify_input_shas():
    print("[1/3] Verifying input SHA-256 hashes...")
    for rel_path, expected in EXPECTED_SHAS.items():
        actual = sha256_file(BASE_DIR / rel_path)
        if actual != expected:
            raise RuntimeError(f"SHA mismatch for {rel_path}: expected {expected}, got {actual}")
        print(f"  OK: {rel_path} -> {actual}")
    print("All input SHA-256 hashes match.\n")


def run_matches():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    python_bin = sys.executable

    tasks = []

    # 1. B0R: P2 vs P2 (15 seeds = 30 games)
    tasks.append({
        "name": "b0r",
        "a": P2_AGENT,
        "b": P2_AGENT,
        "seeds": 15,
        "seed_start": 4000,
        "out": RAW_DIR / "b0r.json"
    })

    # 2. M14R: EXP-014 vs P2 (15 seeds = 30 games)
    tasks.append({
        "name": "m14r",
        "a": VARIANT_AGENT,
        "b": P2_AGENT,
        "seeds": 15,
        "seed_start": 4000,
        "out": RAW_DIR / "m14r.json"
    })

    # 3. NP2R: P2 vs panel 5 (10 seeds each = 100 games)
    for opp_name, opp_path in PANEL_OPPONENTS.items():
        tasks.append({
            "name": f"np2r_{opp_name}",
            "a": P2_AGENT,
            "b": opp_path,
            "seeds": 10,
            "seed_start": 4000,
            "out": RAW_DIR / f"np2r_{opp_name}.json"
        })

    # 4. N14R: EXP-014 vs panel 5 (10 seeds each = 100 games)
    for opp_name, opp_path in PANEL_OPPONENTS.items():
        tasks.append({
            "name": f"n14r_{opp_name}",
            "a": VARIANT_AGENT,
            "b": opp_path,
            "seeds": 10,
            "seed_start": 4000,
            "out": RAW_DIR / f"n14r_{opp_name}.json"
        })

    total_tasks = len(tasks)
    print(f"[2/3] Running {total_tasks} match sets (total 260 games)...")

    start_all = time.time()
    for idx, t in enumerate(tasks, 1):
        print(f"\n--- [{idx}/{total_tasks}] Task: {t['name']} (a={t['a']} vs b={t['b']}, seeds={t['seeds']}, seed_start={t['seed_start']}) ---")
        cmd = [
            python_bin,
            str(BASE_DIR / "tools/arena.py"),
            "--a", str(BASE_DIR / t["a"]),
            "--b", str(BASE_DIR / t["b"]),
            "--seeds", str(t["seeds"]),
            "--seed-start", str(t["seed_start"]),
            "--json", str(t["out"])
        ]
        t0 = time.time()
        res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True)
        dur = time.time() - t0
        if res.returncode != 0:
            print(f"FAILED (code {res.returncode}):")
            print(res.stdout)
            print(res.stderr)
            raise RuntimeError(f"Arena execution failed for task {t['name']}")
        print(f"Completed in {dur:.1f}s. Saved to {t['out'].name}")
        # Print summary line from arena stdout
        for line in res.stdout.strip().split("\n"):
            if "페어드 점수" in line or "W/D/L" in line or "평균 bank" in line or "에러" in line:
                print(" ", line)

    print(f"\nAll matches completed in {time.time() - start_all:.1f}s.\n")


def build_summary():
    print("[3/3] Aggregating results into summary.json...")

    # Load B0R
    with open(RAW_DIR / "b0r.json") as f:
        b0_data = json.load(f)["payload"]

    # Load M14R
    with open(RAW_DIR / "m14r.json") as f:
        m14_data = json.load(f)["payload"]

    # Load NP2R & N14R
    np2_data = {}
    n14_data = {}
    for opp in PANEL_OPPONENTS:
        with open(RAW_DIR / f"np2r_{opp}.json") as f:
            np2_data[opp] = json.load(f)["payload"]
        with open(RAW_DIR / f"n14r_{opp}.json") as f:
            n14_data[opp] = json.load(f)["payload"]

    # Aggregate NP2 total
    p2_games = sum(d["games"] for d in np2_data.values())
    p2_wins = sum(d["wins"] for d in np2_data.values())
    p2_draws = sum(d["draws"] for d in np2_data.values())
    p2_losses = sum(d["losses"] for d in np2_data.values())
    p2_total_score = p2_wins * 1.0 + p2_draws * 0.5
    p2_errors = sum(d["errors"] for d in np2_data.values())

    # Aggregate N14 total
    n14_games = sum(d["games"] for d in n14_data.values())
    n14_wins = sum(d["wins"] for d in n14_data.values())
    n14_draws = sum(d["draws"] for d in n14_data.values())
    n14_losses = sum(d["losses"] for d in n14_data.values())
    n14_total_score = n14_wins * 1.0 + n14_draws * 0.5
    n14_errors = sum(d["errors"] for d in n14_data.values())

    # Regressions: for same opponent, seed, seat: P2 score >= 0.5 but Variant score == 0.0
    regressions_detail = []
    for opp in PANEL_OPPONENTS:
        p2_details = {(g["seed"], g["a_seat"]): g for g in np2_data[opp]["games_detail"]}
        n14_details = {(g["seed"], g["a_seat"]): g for g in n14_data[opp]["games_detail"]}

        for key, p2_g in p2_details.items():
            seed, seat = key
            n14_g = n14_details[key]

            p2_sc = 1.0 if p2_g["a_reward"] > p2_g["b_reward"] else (0.5 if p2_g["a_reward"] == p2_g["b_reward"] else 0.0)
            n14_sc = 1.0 if n14_g["a_reward"] > n14_g["b_reward"] else (0.5 if n14_g["a_reward"] == n14_g["b_reward"] else 0.0)

            if p2_sc >= 0.5 and n14_sc == 0.0:
                regressions_detail.append({
                    "opponent": opp,
                    "seed": seed,
                    "seat": seat,
                    "p2_score": p2_sc,
                    "p2_margin": p2_g["margin"],
                    "variant_score": n14_sc,
                    "variant_margin": n14_g["margin"]
                })

    per_opponent_summary = {}
    for opp in PANEL_OPPONENTS:
        per_opponent_summary[opp] = {
            "p2": {
                "wdl": [np2_data[opp]["wins"], np2_data[opp]["draws"], np2_data[opp]["losses"]],
                "score": np2_data[opp]["wins"] * 1.0 + np2_data[opp]["draws"] * 0.5,
                "a_mean_bank": np2_data[opp]["a_mean_bank"],
                "b_mean_bank": np2_data[opp]["b_mean_bank"],
                "errors": np2_data[opp]["errors"]
            },
            "exp014r": {
                "wdl": [n14_data[opp]["wins"], n14_data[opp]["draws"], n14_data[opp]["losses"]],
                "score": n14_data[opp]["wins"] * 1.0 + n14_data[opp]["draws"] * 0.5,
                "a_mean_bank": n14_data[opp]["a_mean_bank"],
                "b_mean_bank": n14_data[opp]["b_mean_bank"],
                "errors": n14_data[opp]["errors"]
            }
        }

    raw_file_shas = {}
    for fpath in sorted(RAW_DIR.glob("*.json")):
        raw_file_shas[fpath.name] = sha256_file(fpath)

    summary = {
        "metadata": {
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
            "host_os": "macOS",
            "python_executable": sys.executable,
        },
        "input_shas": {k: sha256_file(BASE_DIR / k) for k in EXPECTED_SHAS},
        "raw_file_shas": raw_file_shas,
        "B0R": {
            "description": "P2 vs P2 baseline (seed 4000-4014, both seats)",
            "games": b0_data["games"],
            "wins": b0_data["wins"],
            "draws": b0_data["draws"],
            "losses": b0_data["losses"],
            "draw_rate": f"{b0_data['draws']}/{b0_data['games']}",
            "score": b0_data["wins"] * 1.0 + b0_data["draws"] * 0.5,
            "score_str": f"{b0_data['wins'] * 1.0 + b0_data['draws'] * 0.5}/{b0_data['games']}",
            "errors": b0_data["errors"],
            "games_detail": b0_data["games_detail"]
        },
        "M14R": {
            "description": "EXP-014 variant vs P2 mirror test (seed 4000-4014, both seats)",
            "games": m14_data["games"],
            "wins": m14_data["wins"],
            "draws": m14_data["draws"],
            "losses": m14_data["losses"],
            "wdl": [m14_data["wins"], m14_data["draws"], m14_data["losses"]],
            "score": m14_data["wins"] * 1.0 + m14_data["draws"] * 0.5,
            "score_str": f"{m14_data['wins'] * 1.0 + m14_data['draws'] * 0.5}/{m14_data['games']}",
            "paired_score": m14_data["paired_score"],
            "ci95": m14_data["ci95"],
            "errors": m14_data["errors"],
            "games_detail": m14_data["games_detail"]
        },
        "N": {
            "description": "Panel test (5 opponents x 10 seeds x both seats = 100 games)",
            "p2": {
                "games": p2_games,
                "total_score": p2_total_score,
                "score_str": f"{p2_total_score}/{p2_games}",
                "wdl": [p2_wins, p2_draws, p2_losses],
                "errors": p2_errors
            },
            "exp014r": {
                "games": n14_games,
                "total_score": n14_total_score,
                "score_str": f"{n14_total_score}/{n14_games}",
                "wdl": [n14_wins, n14_draws, n14_losses],
                "regressions_count": len(regressions_detail),
                "regressions_str": f"{len(regressions_detail)}/{n14_games}",
                "errors": n14_errors,
                "regressions_detail": regressions_detail
            },
            "per_opponent": per_opponent_summary
        },
        "total_errors": b0_data["errors"] + m14_data["errors"] + p2_errors + n14_errors
    }

    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Summary saved to {SUMMARY_PATH} (SHA-256: {sha256_file(SUMMARY_PATH)})")
    return summary


def main():
    verify_input_shas()
    run_matches()
    summary = build_summary()

    print("\n================== SUMMARY RESULTS ==================")
    print(f"B0R:  W/D/L {summary['B0R']['wins']}/{summary['B0R']['draws']}/{summary['B0R']['losses']}, "
          f"Score: {summary['B0R']['score_str']}, Draws: {summary['B0R']['draw_rate']}, Errors: {summary['B0R']['errors']}")
    print(f"M14R: W/D/L {summary['M14R']['wins']}/{summary['M14R']['draws']}/{summary['M14R']['losses']}, "
          f"Score: {summary['M14R']['score_str']}, Paired score: {summary['M14R']['paired_score']:.4f}, "
          f"CI95: [{summary['M14R']['ci95'][0]:.4f}, {summary['M14R']['ci95'][1]:.4f}], Errors: {summary['M14R']['errors']}")
    print(f"NP2R Total Score: {summary['N']['p2']['score_str']} (W/D/L {summary['N']['p2']['wdl'][0]}/{summary['N']['p2']['wdl'][1]}/{summary['N']['p2']['wdl'][2]}), Errors: {summary['N']['p2']['errors']}")
    print(f"N14R Total Score: {summary['N']['exp014r']['score_str']} (W/D/L {summary['N']['exp014r']['wdl'][0]}/{summary['N']['exp014r']['wdl'][1]}/{summary['N']['exp014r']['wdl'][2]}), "
          f"Regressions: {summary['N']['exp014r']['regressions_str']}, Errors: {summary['N']['exp014r']['errors']}")
    print(f"Total Errors: {summary['total_errors']}")
    print("=====================================================\n")


if __name__ == "__main__":
    main()
