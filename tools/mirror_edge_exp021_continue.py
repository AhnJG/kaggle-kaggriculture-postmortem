#!/usr/bin/env python3
"""Continue the independent four-arm EXP-021 v2 after frozen H2-prime STOP."""
from __future__ import annotations

import argparse
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/mirror_edge_20260926"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load("mirror_edge_exp021_base_continue", "tools/mirror_edge_exp021.py")
V = load("mirror_edge_exp021_v2_frozen", "tools/mirror_edge_exp021_v2.py")


def record_parent_step0():
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable

    source = (ROOT / B.PARENT).read_text()
    rows = []
    for seat in (0, 1):
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 5800})
        observation = copy.deepcopy(env.steps[0][seat].observation)
        observation["player"] = seat
        observation["step"] = 0
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            function = get_last_callable(source, path=B.PARENT)
            action = function(observation, env.configuration)
        rows.append({"seat": seat, "action": action})
    result = {
        "seed": 5800,
        "rows": rows,
        "reason_sell_absent": "_PIPE_MODE='EarlyCycle' calls _pipe_install, whose non-Original/non-HybridOpening branch overwrites tape[0].market with BUY_PRODUCT WHEAT 5 plus BUY_SEED WHEAT 1 before the appended wrapper receives the action (parent main.py:6344,6358-6360,6410-6418).",
    }
    B.atomic(OUT / "h2prime-parent-step0-actions.json", result)
    return result


def h2_stop():
    rows = [row for row in B.read_rows().values() if row["job"]["agent"] == "H2prime"]
    if len(rows) != 8:
        raise RuntimeError(f"H2PRIME_GATE_ROWS_EXPECTED_8 got={len(rows)}")
    result = {
        "status": "STOP",
        "reason": "FROZEN_WRAPPER_TELEMETRY_IMPLEMENTATION_ERROR",
        "detail": "The wrapper referenced undefined global _json while recording the parent step-0 action. Every gate game recorded _ME_REPORT.wrapper_errors=1, mutation_count=0, and is candidate-side invalid. Per the frozen gate, H2-prime is not modified or rerun.",
        "games": len(rows),
        "invalid": sum(not B.candidate_valid(row["result"]) for row in rows),
        "runtime": B.runtime(rows),
        "keys": [row["key"] for row in rows],
    }
    B.atomic(OUT / "h2prime-telemetry-gate.json", result)
    return result


def four_stage1():
    V.verify_v2()
    action_evidence = record_parent_step0()
    h2 = h2_stop()
    rows = B.run_jobs("stage1-v2-four", V.four_stage1_jobs())
    stats = V.grouped_summary(rows, ("P", *V.FOUR))
    baseline = stats["P"]["score_rate"]
    baseline_ok = stats["P"]["invalid"] == 0 and 0.45 <= baseline <= 0.55
    passing = [arm for arm in V.FOUR if stats[arm]["invalid"] == 0 and stats[arm]["score_rate"] >= 0.60] if baseline_ok else []
    verdict = "STOP" if not baseline_ok else "SUCCESS" if passing else "FAIL"
    result = {"verdict": verdict, "baseline_ok": baseline_ok, "passing_arms": passing,
              "arms": stats, "h2prime_gate": h2, "parent_step0": action_evidence,
              "v2_sha256": V.sha(V.V2), "h2prime_prereg_sha256": V.sha(V.H2_PREREG)}
    B.atomic(OUT / "stage1-v2-summary.json", result)
    write_report(result)
    return result


def write_report(result):
    lines = [result["verdict"], "", "[LOCAL] EXP-021 v2 Stage 1(4 arm)과 H2′ telemetry gate 결과.", "",
             "| arm | Stage 1 score rate | W/D/L | pass | activation | max step | p99 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    journal = B.read_rows()
    for agent in ("P", *V.FOUR):
        item = result["arms"][agent]
        relevant = [row for row in journal.values() if row["job"]["stage"] == "stage1" and row["job"]["agent"] == agent]
        activation_key = {"H1a": "mirror_detected_games", "H1b": "mirror_detected_games",
                          "H3": "escalated_32_set_count", "H4": "step717_liquidation_games"}.get(agent)
        activation = "N/A" if agent == "P" else f"{sum(B.telemetry_value(row, activation_key) for row in relevant) / len(relevant):.1%}"
        passed = result["baseline_ok"] if agent == "P" else agent in result["passing_arms"]
        run = item["runtime"]
        lines.append(f"| {agent} | {item['score_rate']:.4f} | {item['wins']}/{item['draws']}/{item['losses']} | {passed} | {activation} | {run['max_step_seconds']:.6f} | {run['p99_step_seconds']:.6f} |")
    h2run = result["h2prime_gate"]["runtime"]
    lines.extend([
        f"| H2′ | N/A | N/A | False | telemetry gate STOP (8/8 invalid) | {h2run['max_step_seconds']:.6f} | {h2run['p99_step_seconds']:.6f} |",
        "",
        "H2′ parent step-0 actual action, both seats: `BUY_PRODUCT WHEAT 5`, `BUY_SEED WHEAT 1`; see `experiments/mirror_edge_20260926/h2prime-parent-step0-actions.json`.",
        "SELL이 없었던 이유: `_PIPE_MODE='EarlyCycle'`의 `_pipe_install`이 wrapper 호출 전에 tape step 0 market을 위 두 주문으로 덮어쓴다 (`main.py:6344,6358-6360,6410-6418`).",
        "H2′ STOP 이유: frozen wrapper가 action 기록 중 존재하지 않는 `_json` global을 참조해 8/8 `wrapper_errors=1`, `mutation_count=0`; 규칙에 따라 수정·재실행하지 않았다.",
        f"v2 prereg SHA-256: `{result['v2_sha256']}`; H2′ prereg SHA-256: `{result['h2prime_prereg_sha256']}`.",
        "기존 v1 smoke 12행은 보존했고, P/H1a/H1b/H3/H4의 10행은 Stage 1에 포함했다. H2 두 행은 v2 판정에서 제외했다.",
        "Submission/Kaggle download/search-loop write/launchd change: none.", "",
        "다음 행동 2개:",
        "1. Stage 1 통과 arm만 frozen Stage 2 기준으로 실행한다.",
        "2. H2′는 새 승인과 새 preregistration 없이는 수정하거나 재실행하지 않는다.", "",
    ])
    path = B.report_path("STAGE1-V2")
    path.write_text("\n".join(lines))
    result["report"] = str(path.relative_to(ROOT))
    B.atomic(OUT / "stage1-v2-summary.json", result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("stage1",))
    args = parser.parse_args()
    print(json.dumps(four_stage1(), indent=2))
