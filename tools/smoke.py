#!/usr/bin/env python3
"""S4 스모크 — 공식 3봇이 양 좌석에서 720턴을 완주하는지 확인하고 리플레이를 저장한다.

이 단계의 목적은 성능이 아니라 **엔진과 러너가 우리 손에서 재현되는지** 확인하는 것이다.
여기서 막히면 그 뒤의 모든 측정이 무의미하다.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time
from kaggle_environments import make
try:
    from gate_contract import document, exit_code
except ModuleNotFoundError:  # package import (e.g. unit tests)
    from tools.gate_contract import document, exit_code

BUILTINS = ["pass", "random", "starter"]
EXPECTED_ENGINE_SHA = "bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e"


def run_pair(a, b, seed, steps, outdir):
    env = make("kaggriculture", configuration={"episodeSteps": steps, "seed": seed})
    t = time.perf_counter()
    env.run([a, b])
    wall = time.perf_counter() - t
    final = env.steps[-1]
    ok = len(env.steps) == steps and all(s.status == "DONE" for s in final)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        p = os.path.join(outdir, f"replay_{a}_vs_{b}_seed{seed}.json")
        with open(p, "w") as f:
            json.dump(env.toJSON(), f)
    return {"a": a, "b": b, "seed": seed, "steps": len(env.steps),
            "rewards": [round(s.reward or 0) for s in final],
            "statuses": [s.status for s in final],
            "wall_s": round(wall, 2), "ok": ok}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--steps", type=int, default=720)
    ap.add_argument("--outdir", default="private_artifacts/replays")
    ap.add_argument("--json")
    ap.add_argument("--require-pass", action="store_true",
                    help="gate failure를 non-zero exit와 versioned JSON으로 강제")
    args = ap.parse_args()

    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    src = os.path.join(os.path.dirname(K.__file__), "kaggriculture.py")
    digest = hashlib.sha256(open(src, "rb").read()).hexdigest()
    print(f"engine sha256 = {digest}")
    print(f"ENGINE_LOCK 기대값 = {EXPECTED_ENGINE_SHA}")
    print("일치" if digest == EXPECTED_ENGINE_SHA
          else "!!! 불일치 — 실험 중단하고 BOARD 에 BLOCK !!!")
    print()

    rows, all_ok, execution_errors = [], True, []
    for i, a in enumerate(BUILTINS):
        for b in BUILTINS[i:]:
            for x, y in ({(a, b), (b, a)}):
                try:
                    r = run_pair(x, y, args.seed, args.steps, args.outdir)
                except Exception as exc:  # require-pass에서 INVALID로 보고
                    r = {"a": x, "b": y, "seed": args.seed, "steps": 0,
                         "rewards": [], "statuses": [], "wall_s": None,
                         "error": repr(exc), "ok": False}
                    execution_errors.append(f"{x} vs {y}: {exc!r}")
                rows.append(r)
                all_ok = all_ok and r["ok"]
                mark = "OK " if r["ok"] else "FAIL"
                print(f"[{mark}] {x:>8} vs {y:<8} steps={r['steps']} "
                      f"rewards={r['rewards']} status={r['statuses']} {r['wall_s']}s")

    if digest != EXPECTED_ENGINE_SHA:
        verdict, reasons = "ENGINE_MISMATCH", ["engine SHA-256 does not match ENGINE_LOCK"]
    elif execution_errors or any(r.get("steps") != 720 or
                                 any(s != "DONE" for s in r.get("statuses", []))
                                 for r in rows):
        verdict, reasons = "INVALID", ["one or more runs did not complete 720 steps with DONE"]
        reasons.extend(execution_errors)
    elif not all_ok:
        verdict, reasons = "FAILURE", ["one or more builtin pairings failed"]
    else:
        verdict, reasons = "PASS", []
    print(f"\nS4 게이트: {'PASS' if verdict == 'PASS' else 'FAIL'}  (전 조합 720스텝 완주 + DONE)")
    if args.outdir:
        print(f"리플레이 저장: {args.outdir}/")
    if args.json:
        result = document(verdict=verdict, gate_passed=verdict == "PASS",
                          reasons=reasons, engine_sha256=digest,
                          artifact_sha256={f"builtin:{name}": None for name in BUILTINS},
                          payload=rows)
        with open(args.json, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    if args.require_pass:
        sys.exit(exit_code(verdict))


if __name__ == "__main__":
    main()
