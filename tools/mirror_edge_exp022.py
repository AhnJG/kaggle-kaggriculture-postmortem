#!/usr/bin/env python3
"""Frozen, restartable offline runner for EXP-022 H2-prime retest."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from scipy.stats import t as student_t


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/mirror_edge2_20260926"
PREREG = OUT / "preregistration.json"
OLD_OUT = ROOT / "experiments/mirror_edge_20260926"
OLD_VARIANT = OLD_OUT / "variants/H2prime/main.py"
VARIANT = OUT / "variants/H2prime/main.py"
PARENT = "analysis/daily_scan/20260925/extracted/kaggriculture/main.py"
OPPONENT = "releases/public-newmeta-127ed3e6-exact/main.py"
DP = "releases/public-tetsutani-demand-preserving-0924-exact/main.py"
WORKERS = 5
EXPECTED_OLD_VARIANT_SHA = "b75819d19e780805131314b57a5c6ae0d3c6c006edb28da1847e7a0920f08ff8"
IMPORT_LINE = "import json as _json\n"
MARKER = "# EXP-021 H2-prime frozen wrapper, approved 2026-09-26 00:40 KST.\n"

spec = importlib.util.spec_from_file_location("mirror_edge_exp021_base", ROOT / "tools/mirror_edge_exp021.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

B.OUT = OUT
B.PREREG = PREREG
B.PARENT = PARENT
B.OPPONENT = OPPONENT
B.DP = DP
B.WORKERS = WORKERS
_base_verify = B.verify_frozen_inputs


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_frozen_inputs():
    frozen = _base_verify()
    for item in (frozen["source_h2prime"], frozen["variant"]):
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"EXP022_SHA_MISMATCH {item['path']}")
    if frozen["source_h2prime"]["sha256"] != EXPECTED_OLD_VARIANT_SHA:
        raise RuntimeError("EXP021_H2PRIME_SOURCE_CHANGED")
    expected = OLD_VARIANT.read_text().replace(MARKER, MARKER + IMPORT_LINE, 1)
    if VARIANT.read_text() != expected:
        raise RuntimeError("EXP022_NOT_IMPORT_ONLY")
    return frozen


B.verify_frozen_inputs = verify_frozen_inputs


def prepare_variant():
    if sha(OLD_VARIANT) != EXPECTED_OLD_VARIANT_SHA:
        raise RuntimeError("EXP021_H2PRIME_SOURCE_CHANGED")
    old = OLD_VARIANT.read_text()
    if old.count(MARKER) != 1 or IMPORT_LINE in old[old.index(MARKER):old.index(MARKER) + len(MARKER) + len(IMPORT_LINE)]:
        raise RuntimeError("IMPORT_INSERTION_SITE_CHANGED")
    new = old.replace(MARKER, MARKER + IMPORT_LINE, 1)
    if new.replace(MARKER + IMPORT_LINE, MARKER, 1) != old:
        raise RuntimeError("NOT_IMPORT_ONLY")
    VARIANT.parent.mkdir(parents=True, exist_ok=True)
    if VARIANT.exists() and VARIANT.read_text() != new:
        raise RuntimeError("EXP022_VARIANT_CHANGED")
    if not VARIANT.exists():
        VARIANT.write_text(new)
    compile(new, str(VARIANT), "exec")
    result = {
        "path": str(VARIANT.relative_to(ROOT)),
        "sha256": sha(VARIANT),
        "source_path": str(OLD_VARIANT.relative_to(ROOT)),
        "source_sha256": sha(OLD_VARIANT),
        "only_change": IMPORT_LINE.rstrip(),
        "import_only_assertion": new.replace(MARKER + IMPORT_LINE, MARKER, 1) == old,
    }
    B.atomic(OUT / "variants/manifest.json", result)
    return result


def execute(job):
    started = B.stamp()
    command = [sys.executable, str(Path(__file__).resolve()), "--worker", json.dumps(job)]
    try:
        proc = subprocess.run(command, cwd=ROOT, env=dict(os.environ, **B.THREAD_ENV),
                              capture_output=True, text=True, timeout=1200)
        if proc.returncode:
            raise RuntimeError(proc.stderr[-2000:] or proc.stdout[-2000:])
        result = json.loads(proc.stdout)
    except subprocess.TimeoutExpired:
        result = {"candidate_timeout": True, "steps": 0, "statuses": ["TIMEOUT", "UNKNOWN"],
                  "exceptions": [[], []], "caught_errors": {"candidate": [], "opponent": []},
                  "telemetry": {"candidate": {}, "opponent": {}}, "timing_seconds": [[], []],
                  "rewards": [None, None], "margin": None, "score": None, "wall_seconds": 1200,
                  "stdout": "worker subprocess timeout", "worker_peak_rss_bytes": 0}
    return {"key": B.key(job), "job": job, "started_at": started,
            "completed_at": B.stamp(), "result": result}


B.execute = execute


def mutate_step0(action, observation):
    market = [list(order) for order in (action.get("market") or [])]
    chosen = None
    for index, order in enumerate(market):
        if len(order) >= 3 and order[0] == "SELL" and order[1] == "WHEAT" and int(order[2]) > 0:
            chosen = (index, "SELL_WHEAT_MINUS_1", 1.0)
            break
    if chosen is None:
        for index in range(len(market) - 1, -1, -1):
            order = market[index]
            if len(order) >= 3 and order[0] == "BUY_PRODUCT" and order[1] == "WHEAT" and int(order[2]) > 0:
                chosen = (index, "LAST_BUY_PRODUCT_WHEAT_MINUS_1", -1.0)
                break
    if chosen is None:
        raise AssertionError("NO_EXP021_DECISION2_MUTATION_TARGET")
    index, kind, sign = chosen
    before = int(market[index][2])
    market[index][2] = before - 1
    q0 = float(observation["market"]["prices"]["WHEAT"])
    return dict(action, market=market), {
        "order_index": index, "mutation_kind": kind, "before_quantity": before,
        "after_quantity": int(market[index][2]), "quantity_delta": int(market[index][2]) - before,
        "q0": q0, "expected_cash_difference": sign * q0,
    }


def unit_test():
    verify_frozen_inputs()
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable

    rows = []
    for seat in (0, 1):
        parent = get_last_callable((ROOT / PARENT).read_text(), path=str(ROOT / PARENT))
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 6190})
        env.reset(2)
        obs = dict(env.state[seat].observation)
        obs.setdefault("step", 0)
        original = parent(obs, env.configuration)
        modified, detail = mutate_step0(copy.deepcopy(original), obs)
        differing_orders = []
        for index, (left, right) in enumerate(zip(original.get("market", []), modified.get("market", []))):
            if left != right:
                differing_orders.append({"index": index, "before": left, "after": right})
        assert original.get("farmer") == modified.get("farmer")
        assert original.get("hands") == modified.get("hands")
        assert len(original.get("market", [])) == len(modified.get("market", []))
        assert len(differing_orders) == 1
        assert detail["quantity_delta"] == -1
        assert differing_orders[0]["before"][:2] == differing_orders[0]["after"][:2]
        rows.append({"seat": seat, "original": original, "modified": modified,
                     "difference": detail, "differing_orders": differing_orders})
    result = {"status": "PASS", "seed": 6190, "rows": rows,
              "assertion": "Exactly one WHEAT order quantity changed by -1; all other action fields are identical."}
    B.atomic(OUT / "unit-step0-action.json", result)
    return result


def me(row):
    return row["result"].get("telemetry", {}).get("candidate", {}).get("_ME_REPORT", {})


def opponent_race(row):
    return row["result"].get("telemetry", {}).get("opponent", {}).get("_RACE_REPORT", {})


def jobs(stage, agent, path, opponent, seeds):
    return [B.make_job(stage, agent, path, opponent, seed, seat)
            for seed in seeds for seat in (0, 1)]


def smoke():
    verify_frozen_inputs()
    frozen = json.loads(PREREG.read_text())
    o_jobs = jobs("smoke-o", "H2prime", frozen["variant"]["path"], OPPONENT, [6190])
    other_jobs = []
    for item in (frozen["inputs"]["dp_0924"], *frozen["smoke_public_two"]):
        other_jobs.extend(jobs("smoke-nonmirror", "H2prime", frozen["variant"]["path"], item["path"], [6190]))
    o_rows = B.run_jobs("smoke-o", o_jobs)
    other_rows = B.run_jobs("smoke-nonmirror", other_jobs)
    o_checks = []
    action_log = []
    for row in o_rows:
        report = me(row)
        race = opponent_race(row)
        check = (B.candidate_valid(row["result"]) and report.get("wrapper_errors") == 0
                 and abs(float(report.get("first_turn_cash_difference", 0))) >= 1
                 and report.get("our_mirror") == 1 and race.get("race_mirror") == 0)
        o_checks.append(check)
        action_log.append({"seat": row["job"]["seat"], "candidate": report,
                           "opponent_race_report": race, "opponent_step1_horizon": 8,
                           "horizon_basis": "frozen opponent _RACE_HORIZON_CLONE=8 and race_mirror=0"})
    nonmirror_checks = [(B.candidate_valid(row["result"]) and me(row).get("wrapper_errors") == 0
                         and me(row).get("our_mirror") == 0) for row in other_rows]
    result = {
        "status": "PASS" if all(o_checks) and all(nonmirror_checks) else "STOP",
        "o_checks": o_checks, "nonmirror_checks": nonmirror_checks,
        "o_action_log": action_log,
        "nonmirror_rows": [{"opponent": row["job"]["opponent"], "seat": row["job"]["seat"],
                            "valid": B.candidate_valid(row["result"]), "candidate": me(row)}
                           for row in other_rows],
        "runtime": B.runtime(o_rows + other_rows),
    }
    B.atomic(OUT / "smoke-gate.json", result)
    return result


def summarize(rows):
    return {**B.score_summary(rows), "runtime": B.runtime(rows)}


def screen():
    verify_frozen_inputs()
    if json.loads((OUT / "unit-step0-action.json").read_text())["status"] != "PASS":
        raise RuntimeError("UNIT_GATE_NOT_PASS")
    smoke_result = json.loads((OUT / "smoke-gate.json").read_text())
    if smoke_result["status"] != "PASS":
        return {"status": "STOP", "reason": "SMOKE_GATE_FAILED"}
    candidate_jobs = jobs("screen", "H2prime", str(VARIANT.relative_to(ROOT)), OPPONENT, range(6200, 6250))
    parent_jobs = jobs("screen", "P", PARENT, OPPONENT, range(6200, 6250))
    candidate = summarize(B.run_jobs("screen-candidate", candidate_jobs))
    parent = summarize(B.run_jobs("screen-parent", parent_jobs))
    baseline_ok = parent["invalid"] == 0 and 0.45 <= parent["score_rate"] <= 0.55
    candidate_ok = candidate["invalid"] == 0 and candidate["score_rate"] >= 0.60
    status = "PASS" if baseline_ok and candidate_ok else "STOP" if not baseline_ok else "FAIL"
    result = {"status": status, "baseline_ok": baseline_ok, "candidate_ok": candidate_ok,
              "candidate": candidate, "parent": parent}
    B.atomic(OUT / "screen-summary.json", result)
    return result


def wilson_lower(summary, z=2.576):
    n = summary["n"] - summary["invalid"]
    if n <= 0:
        return None
    p = (summary["wins"] + 0.5 * summary["draws"]) / n
    denominator = 1 + z * z / n
    centre = p + z * z / (2 * n)
    radius = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - radius) / denominator


def paired_lower(candidate_rows, parent_rows):
    def per_seed(rows):
        grouped = {}
        for row in rows:
            grouped.setdefault(row["job"]["seed"], []).append(row["result"].get("score"))
        return {seed: statistics.mean(values) for seed, values in grouped.items()
                if len(values) == 2 and all(value is not None for value in values)}
    left, right = per_seed(candidate_rows), per_seed(parent_rows)
    seeds = sorted(set(left) & set(right))
    deltas = [left[seed] - right[seed] for seed in seeds]
    if len(deltas) < 2:
        return {"n_seeds": len(deltas), "delta": None, "se": None, "lower95": None}
    mean = statistics.mean(deltas)
    se = statistics.stdev(deltas) / math.sqrt(len(deltas))
    lower = mean - float(student_t.ppf(0.975, len(deltas) - 1)) * se
    return {"n_seeds": len(deltas), "delta": mean, "se": se, "lower95": lower}


def activation_rate(rows):
    valid = [row for row in rows if B.candidate_valid(row["result"])]
    active = sum(int(me(row).get("our_mirror", 0) == 1) for row in valid)
    return {"games": len(valid), "activations": active,
            "rate": active / len(valid) if valid else None}


def confirmation():
    verify_frozen_inputs()
    frozen = json.loads(PREREG.read_text())
    variant = frozen["variant"]["path"]
    primary_rows = B.run_jobs("confirm-primary", jobs("confirm-primary", "H2prime", variant, OPPONENT, range(6250, 6450)))
    dp_candidate = B.run_jobs("confirm-dp-candidate", jobs("confirm-dp", "H2prime", variant, DP, range(6450, 6550)))
    dp_parent = B.run_jobs("confirm-dp-parent", jobs("confirm-dp", "P", PARENT, DP, range(6450, 6550)))
    guard_rows = {}
    all_guard_rows = []
    for index, item in enumerate(frozen["inputs"]["public_guard_15"]):
        candidate_rows = B.run_jobs(f"guard-{index}-candidate", jobs("guard", "H2prime", variant, item["path"], range(6550, 6560)))
        parent_rows = B.run_jobs(f"guard-{index}-parent", jobs("guard", "P", PARENT, item["path"], range(6550, 6560)))
        candidate_summary, parent_summary = summarize(candidate_rows), summarize(parent_rows)
        decline = parent_summary["score_rate"] - candidate_summary["score_rate"]
        guard_rows[item["path"]] = {"candidate": candidate_summary, "parent": parent_summary,
                                    "decline": decline, "regression_gt_0_10": decline > 0.10}
        all_guard_rows.extend(candidate_rows + parent_rows)
    primary = summarize(primary_rows)
    primary_lower = wilson_lower(primary)
    dp = {"candidate": summarize(dp_candidate), "parent": summarize(dp_parent),
          "paired": paired_lower(dp_candidate, dp_parent)}
    clone_shas = {frozen["inputs"]["opponent_o"]["sha256"], frozen["inputs"]["parent"]["sha256"]}
    nonclone_candidate = dp_candidate + [row for row in all_guard_rows
                                         if row["job"]["agent"] == "H2prime"
                                         and row["job"]["opponent_sha256"] not in clone_shas]
    activation = activation_rate(nonclone_candidate)
    all_rows = primary_rows + dp_candidate + dp_parent + all_guard_rows
    run = B.runtime(all_rows)
    regression_count = sum(item["regression_gt_0_10"] for item in guard_rows.values())
    checks = {
        "primary": primary["invalid"] == 0 and primary_lower is not None and primary_lower > 0.55,
        "dp": dp["candidate"]["invalid"] == 0 and dp["parent"]["invalid"] == 0
              and dp["paired"]["lower95"] is not None and dp["paired"]["lower95"] > -0.05,
        "guard": regression_count == 0 and all(not item["candidate"]["invalid"] and not item["parent"]["invalid"]
                                                for item in guard_rows.values()),
        "runtime": run["invalid_games"] == 0 and run["candidate_exceptions"] == 0
                   and run["candidate_caught_errors"] == 0 and run["max_step_seconds"] < 0.5
                   and run["p99_step_seconds"] < 0.10,
        "activation": activation["rate"] is not None and activation["rate"] <= 0.02,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
              "primary": primary, "primary_wilson99_lower": primary_lower, "dp": dp,
              "guard": guard_rows, "guard_regression_count": regression_count,
              "nonclone_activation": activation, "runtime": run}
    B.atomic(OUT / "confirmation-summary.json", result)
    return result


def final_confirmation():
    verify_frozen_inputs()
    frozen = json.loads(PREREG.read_text())
    rows = B.run_jobs("final-primary", jobs("final", "H2prime", frozen["variant"]["path"], OPPONENT, range(6600, 6800)))
    summary = summarize(rows)
    prior = json.loads((OUT / "confirmation-summary.json").read_text())
    drop = prior["primary"]["score_rate"] - summary["score_rate"]
    result = {"status": "PASS" if summary["invalid"] == 0 else "FAIL", "primary": summary,
              "point_estimate_drop": drop, "winner_curse_warning": drop > 0.05}
    B.atomic(OUT / "final-summary.json", result)
    return result


def aggregate_runtime():
    return B.runtime(list(B.read_rows().values()))


def write_report(verdict, reason=None):
    unit = json.loads((OUT / "unit-step0-action.json").read_text()) if (OUT / "unit-step0-action.json").exists() else None
    smoke_result = json.loads((OUT / "smoke-gate.json").read_text()) if (OUT / "smoke-gate.json").exists() else None
    screen_result = json.loads((OUT / "screen-summary.json").read_text()) if (OUT / "screen-summary.json").exists() else None
    confirm = json.loads((OUT / "confirmation-summary.json").read_text()) if (OUT / "confirmation-summary.json").exists() else None
    final = json.loads((OUT / "final-summary.json").read_text()) if (OUT / "final-summary.json").exists() else None
    frozen = json.loads(PREREG.read_text())
    runtime = aggregate_runtime()
    lines = [verdict, "", "1. 무엇을 시험했는가: EXP-021에서 wrapper import 오류로 시험되지 않은 H2′를 import 한 줄만 고쳐 새 seed로 재시험했다.",
             "2. 왜 하는가: 127ed3e6 exact 복제 상대의 native mirror 판정을 피하면서 우리만 horizon 24를 쓰는 비대칭이 승률을 높이는지 확인하기 위해서다.",
             f"3. 측정 결과: {reason or '아래 frozen gate 결과와 같다.'}",
             "4. 막힌 점과 다음 행동: 아래 판정과 gate 표를 따른다. 제출·Kaggle 다운로드는 실행하지 않았다.", "",
             "| gate | result | metric |", "|---|---|---|"]
    lines.append(f"| unit step-0 one-unit diff | {unit['status'] if unit else 'N/A'} | rows={len(unit['rows']) if unit else 0} |")
    lines.append(f"| seed 6190 smoke | {smoke_result['status'] if smoke_result else 'N/A'} | O={smoke_result.get('o_checks') if smoke_result else 'N/A'}; nonmirror={smoke_result.get('nonmirror_checks') if smoke_result else 'N/A'} |")
    if screen_result:
        lines.append(f"| screen H2′ | {screen_result['status']} | {screen_result['candidate']['wins']}/{screen_result['candidate']['draws']}/{screen_result['candidate']['losses']} score={screen_result['candidate']['score_rate']:.4f} |")
        lines.append(f"| screen parent | {'PASS' if screen_result['baseline_ok'] else 'STOP'} | {screen_result['parent']['wins']}/{screen_result['parent']['draws']}/{screen_result['parent']['losses']} score={screen_result['parent']['score_rate']:.4f} |")
    else:
        lines.extend(["| screen H2′ | N/A | N/A |", "| screen parent | N/A | N/A |"])
    if confirm:
        lines.append(f"| confirm vs O | {'PASS' if confirm['checks']['primary'] else 'FAIL'} | score={confirm['primary']['score_rate']:.4f}; Wilson99 lower={confirm['primary_wilson99_lower']:.4f} |")
        lines.append(f"| DP paired | {'PASS' if confirm['checks']['dp'] else 'FAIL'} | delta={confirm['dp']['paired']['delta']:.4f}; lower95={confirm['dp']['paired']['lower95']:.4f} |")
        lines.append(f"| public-15 guard | {'PASS' if confirm['checks']['guard'] else 'FAIL'} | regressions={confirm['guard_regression_count']} |")
        lines.append(f"| nonclone false mirror | {'PASS' if confirm['checks']['activation'] else 'FAIL'} | {confirm['nonclone_activation']['activations']}/{confirm['nonclone_activation']['games']}={confirm['nonclone_activation']['rate']:.4%} |")
    else:
        lines.extend(["| confirm vs O | N/A | N/A |", "| DP paired | N/A | N/A |",
                      "| public-15 guard | N/A | N/A |", "| nonclone false mirror | N/A | N/A |"])
    if final:
        lines.append(f"| final vs O | {final['status']} | {final['primary']['wins']}/{final['primary']['draws']}/{final['primary']['losses']} score={final['primary']['score_rate']:.4f}; drop={final['point_estimate_drop']:.4f}; warning={final['winner_curse_warning']} |")
    else:
        lines.append("| final vs O | N/A | N/A |")
    runtime_pass = (runtime["invalid_games"] == 0 and runtime["candidate_exceptions"] == 0
                    and runtime["candidate_caught_errors"] == 0 and runtime["max_step_seconds"] < 0.5
                    and runtime["p99_step_seconds"] < 0.10)
    lines.extend([f"| runtime all executed games | {'PASS' if runtime_pass else 'FAIL'} | invalid={runtime['invalid_games']}; exceptions={runtime['candidate_exceptions']}; caught={runtime['candidate_caught_errors']}; max={runtime['max_step_seconds']:.6f}s; p99={runtime['p99_step_seconds']:.6f}s |", "",
                  f"- Preregistration SHA-256: `{sha(PREREG)}`.",
                  f"- Candidate SHA-256: `{frozen['variant']['sha256']}`; source H2′ SHA-256: `{frozen['source_h2prime']['sha256']}`.",
                  f"- Journal: `experiments/mirror_edge2_20260926/games.jsonl`, rows={len(B.read_rows())}, SHA-256 `{sha(OUT / 'games.jsonl') if (OUT / 'games.jsonl').exists() else 'N/A'}`.",
                  "- 기존 EXP-021 결과·STOP 파일은 읽기만 했고 수정하지 않았다.",
                  "- 금지 확인: 제출·Kaggle 다운로드·holdout 9000–9599·search-loop write·engine/RNG 수정 없음.", "",
                  "다음 행동 2개:",
                  "1. SUCCESS이면 E-5와 D3 gate v2 결과까지 확인한 뒤 사람에게 DP 슬롯 은퇴를 포함한 제출 판단을 요청한다.",
                  "2. FAIL/STOP이면 seed·기준·wrapper를 바꾸지 않고 H2′ 재시험을 종료한다.", ""])
    stamp = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d-%H%M")
    path = ROOT / "coordination/reports/codex" / f"{stamp}-EXP022-H2P.md"
    path.write_text("\n".join(lines))
    B.atomic(OUT / "result.json", {"verdict": verdict, "reason": reason,
                                    "report": str(path.relative_to(ROOT)), "runtime": runtime})
    return {"verdict": verdict, "report": str(path.relative_to(ROOT)), "runtime": runtime}


def run_all():
    unit = unit_test()
    if unit["status"] != "PASS":
        return write_report("STOP", "unit gate FAIL")
    smoke_result = smoke()
    if smoke_result["status"] != "PASS":
        return write_report("STOP", "seed 6190 smoke gate FAIL")
    screen_result = screen()
    if screen_result["status"] != "PASS":
        reason = "parent baseline outside [0.45,0.55]" if not screen_result["baseline_ok"] else "H2′ screen score rate < 0.60"
        return write_report(screen_result["status"], reason)
    confirm = confirmation()
    if confirm["status"] != "PASS":
        return write_report("FAIL", "one or more confirmation gates failed")
    final = final_confirmation()
    if final["status"] != "PASS":
        return write_report("FAIL", "final confirmation contained invalid games")
    runtime = aggregate_runtime()
    runtime_ok = (runtime["invalid_games"] == 0 and runtime["candidate_exceptions"] == 0
                  and runtime["candidate_caught_errors"] == 0 and runtime["max_step_seconds"] < 0.5
                  and runtime["p99_step_seconds"] < 0.10)
    return write_report("SUCCESS" if runtime_ok else "FAIL",
                        "all statistical gates passed" if runtime_ok else "aggregate runtime gate failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=("prepare", "unit", "smoke", "screen", "confirm", "final", "run"))
    parser.add_argument("--worker")
    args = parser.parse_args()
    if args.worker:
        os.environ.update(B.THREAD_ENV)
        print(json.dumps(B.worker(json.loads(args.worker)), allow_nan=False))
    elif args.command == "prepare":
        print(json.dumps(prepare_variant(), indent=2))
    elif args.command == "unit":
        print(json.dumps(unit_test(), indent=2))
    elif args.command == "smoke":
        print(json.dumps(smoke(), indent=2))
    elif args.command == "screen":
        print(json.dumps(screen(), indent=2))
    elif args.command == "confirm":
        print(json.dumps(confirmation(), indent=2))
    elif args.command == "final":
        print(json.dumps(final_confirmation(), indent=2))
    elif args.command == "run":
        print(json.dumps(run_all(), indent=2))
    else:
        parser.error("choose a command")
