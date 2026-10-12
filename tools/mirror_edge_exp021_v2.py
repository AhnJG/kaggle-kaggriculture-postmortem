#!/usr/bin/env python3
"""Approved v2 continuation for EXP-021 plus the separately seeded H2-prime arm."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/mirror_edge_20260926"
V2 = OUT / "preregistration-v2.json"
H2_PREREG = OUT / "preregistration-h2prime.json"

SPEC = importlib.util.spec_from_file_location("mirror_edge_exp021_base", ROOT / "tools/mirror_edge_exp021.py")
B = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(B)

FOUR = ("H1a", "H1b", "H3", "H4")
PUBLIC_GATE_TWO = (
    "analysis/daily_scan/20260925/extracted/kaggriculture-harvest-ledger/main.py",
    "analysis/daily_scan/20260924/extracted/kaggriculture-7-turn-rescue-historical-lb-2800/main.py",
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_v2():
    value = json.loads(V2.read_text())
    items = [value["inputs"][name] for name in ("parent", "opponent_o", "dp", "engine")]
    items.extend(value["inputs"]["arms"].values())
    items.extend(value["inputs"]["public_guard_15"])
    for item in items:
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"V2_SHA_MISMATCH {item['path']}")
    if value["workers"] != 5:
        raise RuntimeError("V2_WORKER_MISMATCH")
    return value


H2_WRAPPER = r'''
# EXP-021 H2-prime frozen wrapper, approved 2026-09-26 00:40 KST.
_ME_PARENT = [v for v in globals().values() if callable(v)][-1]
_ME_H2P = {}
_ME_REPORT = {'wrapper_calls': 0, 'wrapper_errors': 0, 'mutation_count': 0,
              'mutation_kind': '', 'q0': 0.0, 'expected_cash_difference': 0.0,
              'parent_step0_action_json': '', 'modified_step0_action_json': '',
              'first_turn_cash_difference': 0.0, 'native_race_mirror': 0,
              'our_mirror': 0, 'level24_set_count': 0}
def mirror_edge_h2prime_entry(observation, configuration=None):
    step = int(observation.get('step', 0))
    player = int(observation.get('player', 0))
    if step == 0:
        _ME_REPORT.update(wrapper_calls=0, wrapper_errors=0, mutation_count=0,
                          mutation_kind='', q0=0.0, expected_cash_difference=0.0,
                          parent_step0_action_json='', modified_step0_action_json='',
                          first_turn_cash_difference=0.0, native_race_mirror=0,
                          our_mirror=0, level24_set_count=0)
        _ME_H2P[player] = {'expected': None}
    _ME_REPORT['wrapper_calls'] += 1
    action = _ME_PARENT(observation, configuration)
    try:
        if step == 0:
            original = _json.dumps(action, sort_keys=True, separators=(',', ':'))
            market = [list(order) for order in (action.get('market') or [])]
            chosen = None
            for index, order in enumerate(market):
                if len(order) >= 3 and order[0] == 'SELL' and order[1] == 'WHEAT' and int(order[2]) > 0:
                    chosen = (index, 'SELL_WHEAT_MINUS_1', 1.0)
                    break
            if chosen is None:
                for index in range(len(market) - 1, -1, -1):
                    order = market[index]
                    if len(order) >= 3 and order[0] == 'BUY_PRODUCT' and order[1] == 'WHEAT' and int(order[2]) > 0:
                        chosen = (index, 'LAST_BUY_PRODUCT_WHEAT_MINUS_1', -1.0)
                        break
            if chosen is not None:
                index, kind, sign = chosen
                market[index][2] = int(market[index][2]) - 1
                q0 = float(observation['market']['prices']['WHEAT'])
                expected = sign * q0
                action = dict(action, market=market)
                _ME_H2P[player] = {'expected': expected}
                _ME_REPORT.update(mutation_count=1, mutation_kind=kind, q0=q0,
                                  expected_cash_difference=expected,
                                  parent_step0_action_json=original,
                                  modified_step0_action_json=_json.dumps(action, sort_keys=True, separators=(',', ':')))
        elif step == 1:
            farms = observation['farms']
            own = float(farms[player]['money'])
            rival = float(farms[1-player]['money'])
            actual = rival - own
            _ME_REPORT['first_turn_cash_difference'] = actual
            _ME_REPORT['native_race_mirror'] = int(_RACE_REPORT.get('race_mirror', 0))
            expected = (_ME_H2P.get(player) or {}).get('expected')
            if expected is not None and abs(actual - expected) <= 2:
                state = _RACE_STATE.get(player)
                if state is not None:
                    state['level'] = 24
                    _ME_REPORT['our_mirror'] = 1
                    _ME_REPORT['level24_set_count'] += 1
    except Exception:
        _ME_REPORT['wrapper_errors'] += 1
    return action
mirror_edge_h2prime_entry.telemetry = _ME_REPORT
'''


def prepare_h2prime():
    verify_v2()
    parent = (ROOT / B.PARENT).read_bytes()
    content = parent + b"\n" + H2_WRAPPER.encode()
    path = OUT / "variants" / "H2prime" / "main.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != content:
        raise RuntimeError("H2PRIME_VARIANT_CHANGED")
    if not path.exists():
        path.write_bytes(content)
    compile(content, str(path), "exec")
    result = {"path": str(path.relative_to(ROOT)), "sha256": sha(path),
              "parent_sha256": sha(ROOT / B.PARENT)}
    manifest = OUT / "h2prime-variant.json"
    if manifest.exists() and json.loads(manifest.read_text()) != result:
        raise RuntimeError("H2PRIME_MANIFEST_CHANGED")
    if not manifest.exists():
        B.atomic(manifest, result)
    return result


def verify_h2_prereg(variant):
    value = json.loads(H2_PREREG.read_text())
    if value["variant"] != variant:
        raise RuntimeError("H2PRIME_PREREG_VARIANT_MISMATCH")
    for item in (value["parent"], value["opponent_o"], value["dp"], *value["public_gate_two"]):
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"H2PRIME_INPUT_SHA_MISMATCH {item['path']}")
    return value


def four_stage1_jobs():
    variants = json.loads((OUT / "variants.json").read_text())["variants"]
    agents = {"P": B.PARENT, **{arm: variants[arm]["path"] for arm in FOUR}}
    return [B.make_job("stage1", agent, path, B.OPPONENT, seed, seat)
            for agent, path in agents.items() for seed in range(5000, 5050) for seat in (0, 1)]


def h2_gate_jobs(variant):
    o = [B.make_job("h2prime-stage1", "H2prime", variant["path"], B.OPPONENT, 5800, seat)
         for seat in (0, 1)]
    others = [B.make_job("h2prime-gate-nonmirror", "H2prime", variant["path"], opponent, 5800, seat)
              for opponent in (B.DP, *PUBLIC_GATE_TWO) for seat in (0, 1)]
    return o, others


def me_report(row):
    return row["result"].get("telemetry", {}).get("candidate", {}).get("_ME_REPORT", {})


def opponent_race_mirror(row):
    return row["result"].get("telemetry", {}).get("opponent", {}).get("_RACE_REPORT", {}).get("race_mirror")


def evaluate_h2_gate(o_rows, other_rows):
    o_checks = []
    for row in o_rows:
        report = me_report(row)
        o_checks.append(B.candidate_valid(row["result"])
                        and report.get("mutation_count") == 1
                        and abs(float(report.get("first_turn_cash_difference", 0))) >= 1
                        and report.get("our_mirror") == 1
                        and opponent_race_mirror(row) == 0)
    nonmirror_checks = [B.candidate_valid(row["result"]) and me_report(row).get("our_mirror") == 0
                        for row in other_rows]
    actions = [{"seat": row["job"]["seat"],
                "parent_step0_action": json.loads(me_report(row)["parent_step0_action_json"]),
                "modified_step0_action": json.loads(me_report(row)["modified_step0_action_json"]),
                "mutation_kind": me_report(row)["mutation_kind"], "q0": me_report(row)["q0"],
                "expected_cash_difference": me_report(row)["expected_cash_difference"],
                "actual_cash_difference": me_report(row)["first_turn_cash_difference"]}
               for row in o_rows]
    B.atomic(OUT / "h2prime-step0-actions.json", {"rows": actions})
    result = {"status": "PASS" if all(o_checks) and all(nonmirror_checks) else "STOP",
              "o_checks": o_checks, "nonmirror_checks": nonmirror_checks,
              "o_rows": [{"seat": row["job"]["seat"], "telemetry": me_report(row),
                           "opponent_race_mirror": opponent_race_mirror(row)} for row in o_rows],
              "other_rows": [{"opponent": row["job"]["opponent"], "seat": row["job"]["seat"],
                               "telemetry": me_report(row)} for row in other_rows],
              "runtime": B.runtime(o_rows + other_rows)}
    B.atomic(OUT / "h2prime-telemetry-gate.json", result)
    return result


def h2_screen_jobs(variant):
    return [B.make_job("h2prime-stage1", "H2prime", variant["path"], B.OPPONENT, seed, seat)
            for seed in range(5800, 5850) for seat in (0, 1)]


def grouped_summary(rows, agents):
    return {agent: {**B.score_summary(part := [row for row in rows if row["job"]["agent"] == agent]),
                    "runtime": B.runtime(part)} for agent in agents}


def stage1():
    verify_v2()
    variant = prepare_h2prime()
    verify_h2_prereg(variant)
    o_jobs, other_jobs = h2_gate_jobs(variant)
    o_rows = B.run_jobs("h2prime-gate-o", o_jobs)
    other_rows = B.run_jobs("h2prime-gate-nonmirror", other_jobs)
    gate = evaluate_h2_gate(o_rows, other_rows)
    four_rows = B.run_jobs("stage1-v2-four", four_stage1_jobs())
    four_stats = grouped_summary(four_rows, ("P", *FOUR))
    baseline = four_stats["P"]["score_rate"]
    baseline_ok = four_stats["P"]["invalid"] == 0 and 0.45 <= baseline <= 0.55
    four_passing = [arm for arm in FOUR if four_stats[arm]["invalid"] == 0
                    and four_stats[arm]["score_rate"] >= 0.60] if baseline_ok else []
    h2_rows = o_rows
    h2_stats = None
    h2_pass = False
    if gate["status"] == "PASS":
        h2_rows = B.run_jobs("h2prime-stage1", h2_screen_jobs(variant))
        h2_stats = {**B.score_summary(h2_rows), "runtime": B.runtime(h2_rows)}
        h2_pass = h2_stats["invalid"] == 0 and h2_stats["score_rate"] >= 0.60
    if not baseline_ok:
        verdict = "STOP"
    elif four_passing or h2_pass:
        verdict = "SUCCESS"
    else:
        verdict = "FAIL"
    result = {"verdict": verdict, "baseline_ok": baseline_ok, "four_passing": four_passing,
              "four": four_stats, "h2prime_gate": gate, "h2prime": h2_stats,
              "h2prime_passing": h2_pass, "v2_sha256": sha(V2),
              "h2prime_prereg_sha256": sha(H2_PREREG)}
    B.atomic(OUT / "stage1-v2-summary.json", result)
    write_report(result)
    return result


def write_report(result):
    lines = [result["verdict"], "", "[LOCAL] EXP-021 v2 Stage 1과 H2′ telemetry gate 결과.", "",
             "| arm | Stage 1 score rate | W/D/L | pass | activation | max step | p99 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    rows = B.read_rows()
    for agent in ("P", *FOUR):
        item = result["four"][agent]
        relevant = [row for row in rows.values() if row["job"]["stage"] == "stage1" and row["job"]["agent"] == agent]
        activation = "N/A" if agent == "P" else sum(
            B.telemetry_value(row, "mirror_detected_games") + B.telemetry_value(row, "escalated_32_set_count")
            + B.telemetry_value(row, "step717_liquidation_games") for row in relevant)
        passed = result["baseline_ok"] if agent == "P" else agent in result["four_passing"]
        run = item["runtime"]
        lines.append(f"| {agent} | {item['score_rate']:.4f} | {item['wins']}/{item['draws']}/{item['losses']} | {passed} | {activation} | {run['max_step_seconds']:.6f} | {run['p99_step_seconds']:.6f} |")
    if result["h2prime"]:
        item = result["h2prime"]
        lines.append(f"| H2′ | {item['score_rate']:.4f} | {item['wins']}/{item['draws']}/{item['losses']} | {result['h2prime_passing']} | gate PASS | {item['runtime']['max_step_seconds']:.6f} | {item['runtime']['p99_step_seconds']:.6f} |")
    else:
        lines.append("| H2′ | N/A | N/A | False | telemetry gate STOP | N/A | N/A |")
    first = result["h2prime_gate"]["o_rows"]
    kinds = sorted({row["telemetry"]["mutation_kind"] for row in first})
    lines.extend(["", f"H2′ telemetry gate: **{result['h2prime_gate']['status']}**; O checks={result['h2prime_gate']['o_checks']}; nonmirror checks={result['h2prime_gate']['nonmirror_checks']}.",
                  f"Parent step-0 actual-action finding: qualifying SELL WHEAT was absent, so frozen fallback `{', '.join(kinds)}` activated. The actual action had already been transformed from the route tape before the appended wrapper received it.",
                  "Step-0 action evidence: `experiments/mirror_edge_20260926/h2prime-step0-actions.json`.",
                  f"v2 prereg SHA-256: `{result['v2_sha256']}`; H2′ prereg SHA-256: `{result['h2prime_prereg_sha256']}`.",
                  "Submission/Kaggle download/search-loop write/launchd change: none.", "",
                  "다음 행동 2개:",
                  "1. Stage 1 통과 arm만 frozen Stage 2 기준으로 실행한다.",
                  "2. H2′가 gate 또는 screen에서 실패했으면 수정하지 않고 해당 arm만 종료한다.", ""])
    path = B.report_path("STAGE1-V2")
    path.write_text("\n".join(lines))
    result["report"] = str(path.relative_to(ROOT))
    B.atomic(OUT / "stage1-v2-summary.json", result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare-h2prime", "stage1"))
    args = parser.parse_args()
    if args.command == "prepare-h2prime":
        print(json.dumps(prepare_h2prime(), indent=2))
    else:
        print(json.dumps(stage1(), indent=2))
