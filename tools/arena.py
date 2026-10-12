#!/usr/bin/env python3
"""페어드 아레나 — 같은 시드, 양 좌석 교대.

이 대회의 레이팅은 승/무/패만 본다. 코인 격차는 반영되지 않는다.
따라서 비교는 항상 **같은 시드에서 양쪽 좌석을 모두 바꿔 본** 페어드 승률이어야 한다.
좌석은 유리/불리가 갈리고, 시드는 마을 상점 추첨을 바꾸므로 둘 다 통제해야 한다.

점수 정의
    한 시드마다 2경기 (A가 seat0 / A가 seat1).
    각 경기에서 A의 점수는 승 1.0 · 무 0.5 · 패 0.0.
    시드 점수 = 두 경기 평균  ->  시드 단위 표본으로 신뢰구간을 낸다.
    (경기 단위가 아니라 시드 단위로 묶어야 좌석 상관을 이중계산하지 않는다.)

사용:
    python3 tools/arena.py --a main.py --b starter --seeds 200
    python3 tools/arena.py --a main.py --b opponents/public/x.py --seed-file configs/paired_seeds.txt
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
import time
from pathlib import Path

from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as engine
try:
    from gate_contract import document, exit_code
except ModuleNotFoundError:  # package import (e.g. unit tests)
    from tools.gate_contract import document, exit_code

EXPECTED_ENGINE_SHA = "bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e"


def _sha256(path):
    """파일이면 SHA-256, builtin agent처럼 파일이 아니면 None."""
    p = Path(path)
    if not p.is_file():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def artifact_hashes(a, b):
    return {
        "parent_sha256": _sha256("main.py"),
        "agent_a_sha256": _sha256(a),
        "agent_b_sha256": _sha256(b),
        "engine_sha256": _sha256(engine.__file__),
    }


def play(a, b, seed, episode_steps=720):
    """A=seat0, B=seat1 로 한 경기. 보상·상태·실제 step 수를 반환."""
    env = make("kaggriculture", configuration={"episodeSteps": episode_steps, "seed": seed})
    env.run([a, b])
    final = env.steps[-1]
    return (final[0].reward or 0), (final[1].reward or 0), [s.status for s in final], len(env.steps)


def score(a_reward, b_reward):
    if a_reward > b_reward:
        return 1.0
    if a_reward < b_reward:
        return 0.0
    return 0.5


def t_crit(df):
    """95% 양측 t 임계값 근사 (표준 라이브러리만 사용)."""
    table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
             8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086,
             25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980}
    if df <= 0:
        return float("nan")
    keys = sorted(table)
    for k in keys:
        if df <= k:
            return table[k]
    return 1.960


def run(a, b, seeds, episode_steps=720, verbose=True):
    per_seed, wdl, big_loss, errors = [], [0, 0, 0], 0, 0
    margins, a_banks, b_banks, games = [], [], [], []
    t0 = time.perf_counter()

    for i, sd in enumerate(seeds, 1):
        s_sum = 0.0
        for swap in (False, True):
            x, y = (b, a) if swap else (a, b)
            r0, r1, st, steps = play(x, y, sd, episode_steps)
            ar, br = (r1, r0) if swap else (r0, r1)
            if steps != 720 or any(s != "DONE" for s in st):
                errors += 1
            sc = score(ar, br)
            s_sum += sc
            wdl[0 if sc == 1.0 else (1 if sc == 0.5 else 2)] += 1
            margins.append(ar - br)
            a_banks.append(ar)
            b_banks.append(br)
            games.append({"seed": sd, "a_seat": 1 if swap else 0,
                          "a_reward": ar, "b_reward": br,
                          "margin": ar - br, "statuses": st, "steps": steps})
            if ar - br < -10000:
                big_loss += 1
        per_seed.append(s_sum / 2.0)
        if verbose:
            m = statistics.fmean(per_seed)
            print(f"  [{i:>4}/{len(seeds)}] 누적 페어드 점수 {m:.3f}", flush=True)

    n = len(per_seed)
    mean = statistics.fmean(per_seed) if n else float("nan")
    sd_ = statistics.stdev(per_seed) if n > 1 else 0.0
    half = t_crit(n - 1) * sd_ / math.sqrt(n) if n > 1 else float("nan")
    loss_margins = [m for m in margins if m < 0]
    return {
        "a": a, "b": b, "seed_values": list(seeds), "seats": "both",
        "seeds": n, "games": n * 2, "per_seed_scores": per_seed,
        "paired_score": mean,
        "ci95": [mean - half, mean + half] if n > 1 else [float("nan")] * 2,
        "ci95_half_width": half,
        "wins": wdl[0], "draws": wdl[1], "losses": wdl[2],
        "win_rate": wdl[0] / max(1, sum(wdl)),
        "a_mean_bank": statistics.fmean(a_banks) if a_banks else 0.0,
        "b_mean_bank": statistics.fmean(b_banks) if b_banks else 0.0,
        "mean_margin": statistics.fmean(margins) if margins else 0.0,
        "median_margin": statistics.median(margins) if margins else 0.0,
        "loss_margin_variance": statistics.variance(loss_margins) if len(loss_margins) > 1 else 0.0,
        "big_losses_gt_10k": big_loss,
        "errors": errors,
        "games_detail": games,
        "wall_seconds": round(time.perf_counter() - t0, 1),
    }


def verdict(res, threshold=0.5):
    """CI 하한이 threshold 를 넘어야 '개선'으로 인정한다."""
    lo = res["ci95"][0]
    if res["errors"]:
        return "INVALID (에러 발생)"
    if math.isnan(lo):
        return "미측정 (시드 부족)"
    if lo > threshold:
        return f"A 우세 (CI 하한 {lo:.3f} > {threshold})"
    if res["ci95"][1] < threshold:
        return f"A 열세 (CI 상한 {res['ci95'][1]:.3f} < {threshold})"
    return "불확정 (CI 가 임계를 포함)"


def verdict_kind(res, threshold=0.5):
    if res.get("engine_sha256") != EXPECTED_ENGINE_SHA:
        return "ENGINE_MISMATCH"
    if res["errors"]:
        return "INVALID"
    lo = res["ci95"][0]
    if math.isnan(lo):
        return "INCONCLUSIVE"
    if lo > threshold:
        return "PASS"
    if res["ci95"][1] < threshold:
        return "FAILURE"
    return "INCONCLUSIVE"


def main():
    ap = argparse.ArgumentParser(description="페어드 아레나 (같은 시드, 양 좌석)")
    ap.add_argument("--a", required=True, help="평가 대상")
    ap.add_argument("--b", required=True, help="기준 상대")
    ap.add_argument("--seeds", type=int, default=50, help="시드 개수 (경기 수 = 2배)")
    ap.add_argument("--seed-start", type=int, default=1000)
    ap.add_argument("--seed-file", help="시드를 한 줄에 하나씩 담은 파일")
    ap.add_argument("--steps", type=int, default=720)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--json")
    ap.add_argument("--require-pass", action="store_true",
                    help="gate failure를 non-zero exit와 versioned JSON으로 강제")
    args = ap.parse_args()

    if args.seed_file:
        seeds = [int(l) for l in open(args.seed_file) if l.strip() and not l.startswith("#")]
    else:
        seeds = list(range(args.seed_start, args.seed_start + args.seeds))

    print(f"A={args.a}  vs  B={args.b}   시드 {len(seeds)}개 · 경기 {len(seeds)*2}판 (양 좌석)")
    hashes = artifact_hashes(args.a, args.b)
    run_error = None
    identity_changed = False
    try:
        res = run(args.a, args.b, seeds, args.steps)
    except SystemExit as exc:
        run_error = str(exc)
        res = None
    except Exception as exc:
        run_error = repr(exc)
        res = None
    current_hashes = artifact_hashes(args.a, args.b)
    if current_hashes != hashes:
        identity_changed = True
        run_error = "실행 중 artifact 또는 engine SHA-256이 바뀌어 결과를 저장하지 않습니다"
        res = None
    if res is None:
        kind = "IDENTITY_MISMATCH" if identity_changed else "INVALID"
        reasons = [run_error or "arena execution failed"]
        result = document(verdict=kind, gate_passed=False, reasons=reasons,
                          engine_sha256=hashes["engine_sha256"],
                          artifact_sha256={"a": hashes["agent_a_sha256"],
                                           "b": hashes["agent_b_sha256"]},
                          payload=None)
        if args.json:
            with open(args.json, "w") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        if args.require_pass:
            sys.exit(exit_code(kind))
        raise SystemExit(run_error or "arena execution failed")
    res.update(hashes)

    print(f"\n페어드 점수 {res['paired_score']:.4f}  "
          f"95% CI [{res['ci95'][0]:.4f}, {res['ci95'][1]:.4f}]  (±{res['ci95_half_width']:.4f})")
    print(f"W/D/L {res['wins']}/{res['draws']}/{res['losses']}  승률 {res['win_rate']:.3f}")
    print(f"평균 bank A={res['a_mean_bank']:,.0f}  B={res['b_mean_bank']:,.0f}")
    print(f"마진 평균 {res['mean_margin']:,.0f}  중앙 {res['median_margin']:,.0f}  "
          f"대패(>10k) {res['big_losses_gt_10k']}  에러 {res['errors']}")
    print(f"소요 {res['wall_seconds']}s")
    print(f"\n판정: {verdict(res, args.threshold)}")
    print("주의: 이 결과는 [LOCAL] 이다. hosted 우위를 주장할 수 없다.")

    if args.json:
        kind = verdict_kind(res, args.threshold)
        reasons = [] if kind == "PASS" else [verdict(res, args.threshold)]
        if kind == "ENGINE_MISMATCH":
            reasons = ["engine SHA-256 does not match ENGINE_LOCK"]
        result = document(verdict=kind, gate_passed=kind == "PASS",
                          reasons=reasons,
                          engine_sha256=res["engine_sha256"],
                          artifact_sha256={"a": res["agent_a_sha256"],
                                           "b": res["agent_b_sha256"]},
                          payload=res)
        with open(args.json, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"저장: {args.json}")
    if args.require_pass:
        sys.exit(exit_code(verdict_kind(res, args.threshold)))


if __name__ == "__main__":
    main()
