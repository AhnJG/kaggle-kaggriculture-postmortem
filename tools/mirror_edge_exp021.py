#!/usr/bin/env python3
"""Frozen, restartable runner for EXP-021 MIRROR-EDGE. Offline only."""
from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import copy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/mirror_edge_20260926"
PREREG = OUT / "preregistration.json"
PARENT = "analysis/daily_scan/20260925/extracted/kaggriculture/main.py"
OPPONENT = "releases/public-newmeta-127ed3e6-exact/main.py"
DP = "releases/public-tetsutani-demand-preserving-0924-exact/main.py"
WORKERS = 5
THREAD_ENV = {key: "1" for key in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
)}


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def verify_frozen_inputs():
    frozen = json.loads(PREREG.read_text())
    checks = [frozen["card"], frozen["engine"]]
    checks.extend((frozen["inputs"][name] for name in ("parent", "opponent_o", "dp_0924")))
    checks.extend(frozen["inputs"]["public_guard_15"])
    for item in checks:
        path = ROOT / item["path"]
        if sha(path) != item["sha256"]:
            raise RuntimeError(f"FROZEN_INPUT_SHA_MISMATCH {item['path']}")
    if frozen["workers"] != WORKERS:
        raise RuntimeError("WORKER_CONTRACT_CHANGED")
    return frozen


WRAPPERS = {
    "H1a": r'''
# EXP-021 H1a frozen wrapper.
_ME_PARENT = [v for v in globals().values() if callable(v)][-1]
_RACE_HORIZON_MIRROR = 32
_ME_REPORT = {'wrapper_calls': 0, 'wrapper_errors': 0, 'mirror_detected_games': 0, 'horizon_32_turns': 0}
def mirror_edge_entry(observation, configuration=None):
    step = int(observation.get('step', 0))
    if step == 0:
        _ME_REPORT.update(wrapper_calls=0, wrapper_errors=0, mirror_detected_games=0, horizon_32_turns=0)
    _ME_REPORT['wrapper_calls'] += 1
    action = _ME_PARENT(observation, configuration)
    try:
        player = int(observation['player'])
        state = _RACE_STATE.get(player) or {}
        if step == 1 and int(_RACE_REPORT.get('race_mirror', 0)):
            _ME_REPORT['mirror_detected_games'] += 1
        if int(state.get('horizon', 0)) == 32:
            _ME_REPORT['horizon_32_turns'] += 1
    except Exception:
        _ME_REPORT['wrapper_errors'] += 1
    return action
mirror_edge_entry.telemetry = _ME_REPORT
''',
    "H1b": r'''
# EXP-021 H1b frozen wrapper.
_ME_PARENT = [v for v in globals().values() if callable(v)][-1]
_RACE_HORIZON_MIRROR = 40
_ME_REPORT = {'wrapper_calls': 0, 'wrapper_errors': 0, 'mirror_detected_games': 0, 'horizon_40_turns': 0}
def mirror_edge_entry(observation, configuration=None):
    step = int(observation.get('step', 0))
    if step == 0:
        _ME_REPORT.update(wrapper_calls=0, wrapper_errors=0, mirror_detected_games=0, horizon_40_turns=0)
    _ME_REPORT['wrapper_calls'] += 1
    action = _ME_PARENT(observation, configuration)
    try:
        player = int(observation['player'])
        state = _RACE_STATE.get(player) or {}
        if step == 1 and int(_RACE_REPORT.get('race_mirror', 0)):
            _ME_REPORT['mirror_detected_games'] += 1
        if int(state.get('horizon', 0)) == 40:
            _ME_REPORT['horizon_40_turns'] += 1
    except Exception:
        _ME_REPORT['wrapper_errors'] += 1
    return action
mirror_edge_entry.telemetry = _ME_REPORT
''',
    "H2": r'''
# EXP-021 H2 frozen wrapper.
_ME_PARENT = [v for v in globals().values() if callable(v)][-1]
_ME_H2 = {}
_ME_REPORT = {'wrapper_calls': 0, 'wrapper_errors': 0, 'step0_sell_units_removed': 0,
              'adjusted_mirror_detected_games': 0, 'first_turn_cash_difference': 0.0,
              'level24_set_count': 0}
def mirror_edge_entry(observation, configuration=None):
    step = int(observation.get('step', 0))
    player = int(observation.get('player', 0))
    if step == 0:
        _ME_REPORT.update(wrapper_calls=0, wrapper_errors=0, step0_sell_units_removed=0,
                          adjusted_mirror_detected_games=0, first_turn_cash_difference=0.0,
                          level24_set_count=0)
        _ME_H2[player] = {'quote': None}
    _ME_REPORT['wrapper_calls'] += 1
    action = _ME_PARENT(observation, configuration)
    try:
        if step == 0:
            market = [list(order) for order in (action.get('market') or [])]
            for order in market:
                if len(order) >= 3 and order[0] == 'SELL' and int(order[2]) > 0:
                    order[2] = int(order[2]) - 1
                    _ME_H2[player]['quote'] = float(observation['market']['prices'][order[1]])
                    _ME_REPORT['step0_sell_units_removed'] += 1
                    action = dict(action, market=market)
                    break
        elif step == 1:
            farms = observation['farms']
            own = float(farms[player]['money'])
            rival = float(farms[1-player]['money'])
            difference = abs(rival - own)
            _ME_REPORT['first_turn_cash_difference'] = difference
            quote = (_ME_H2.get(player) or {}).get('quote')
            if quote is not None and abs((rival - own) - quote) < 0.5:
                state = _RACE_STATE.get(player)
                if state is not None:
                    state['level'] = 24
                    _RACE_REPORT['race_mirror'] = 1
                    _ME_REPORT['adjusted_mirror_detected_games'] += 1
                    _ME_REPORT['level24_set_count'] += 1
    except Exception:
        _ME_REPORT['wrapper_errors'] += 1
    return action
mirror_edge_entry.telemetry = _ME_REPORT
''',
    "H3": r'''
# EXP-021 H3 frozen wrapper.
_ME_PARENT = [v for v in globals().values() if callable(v)][-1]
_RACE_HORIZON_ESCALATED = 32
_ME_REPORT = {'wrapper_calls': 0, 'wrapper_errors': 0, 'escalated_32_set_count': 0, 'horizon_32_turns': 0}
def mirror_edge_entry(observation, configuration=None):
    step = int(observation.get('step', 0))
    player = int(observation.get('player', 0))
    if step == 0:
        _ME_REPORT.update(wrapper_calls=0, wrapper_errors=0, escalated_32_set_count=0, horizon_32_turns=0)
    _ME_REPORT['wrapper_calls'] += 1
    before = int((_RACE_STATE.get(player) or {}).get('level', 0))
    action = _ME_PARENT(observation, configuration)
    try:
        state = _RACE_STATE.get(player) or {}
        if int(state.get('level', 0)) == 32 and before != 32:
            _ME_REPORT['escalated_32_set_count'] += 1
        if int(state.get('horizon', 0)) == 32:
            _ME_REPORT['horizon_32_turns'] += 1
    except Exception:
        _ME_REPORT['wrapper_errors'] += 1
    return action
mirror_edge_entry.telemetry = _ME_REPORT
''',
    "H4": r'''
# EXP-021 H4 frozen wrapper.
_ME_PARENT = [v for v in globals().values() if callable(v)][-1]
_ME_REPORT = {'wrapper_calls': 0, 'wrapper_errors': 0, 'mirror_detected_games': 0,
              'step717_liquidation_games': 0, 'step717_sell_units': 0}
def mirror_edge_entry(observation, configuration=None):
    step = int(observation.get('step', 0))
    if step == 0:
        _ME_REPORT.update(wrapper_calls=0, wrapper_errors=0, mirror_detected_games=0,
                          step717_liquidation_games=0, step717_sell_units=0)
    _ME_REPORT['wrapper_calls'] += 1
    action = _ME_PARENT(observation, configuration)
    try:
        if step == 1 and int(_RACE_REPORT.get('race_mirror', 0)):
            _ME_REPORT['mirror_detected_games'] += 1
        if step == 717 and int(_RACE_REPORT.get('race_mirror', 0)):
            projected = projected_shed(action, FarmView(observation))
            orders = [['SELL', item, qty] for item, qty in projected.items()
                      if qty > 0 and item in PRODUCTS][:_IMPL.chassis.cfg['max_orders']]
            action = dict(action, market=orders)
            _ME_REPORT['step717_liquidation_games'] += 1
            _ME_REPORT['step717_sell_units'] += sum(int(order[2]) for order in orders)
    except Exception:
        _ME_REPORT['wrapper_errors'] += 1
    return action
mirror_edge_entry.telemetry = _ME_REPORT
''',
}


def prepare_variants():
    verify_frozen_inputs()
    parent = (ROOT / PARENT).read_bytes()
    result = {}
    for arm, wrapper in WRAPPERS.items():
        content = parent + b"\n" + wrapper.encode()
        path = OUT / "variants" / arm / "main.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != content:
            raise RuntimeError(f"VARIANT_CHANGED {arm}")
        if not path.exists():
            path.write_bytes(content)
        compile(content, str(path), "exec")
        result[arm] = {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
    manifest = {"parent_sha256": sha(ROOT / PARENT), "variants": result}
    path = OUT / "variants.json"
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise RuntimeError("VARIANT_MANIFEST_CHANGED")
    if not path.exists():
        atomic(path, manifest)
    return result


def error_counters(function):
    found = []
    for name, value in function.__globals__.items():
        if not isinstance(value, dict):
            continue
        for key, count in value.items():
            if isinstance(key, str) and (key == "errors" or key.endswith("_errors")) \
                    and isinstance(count, (int, float)) and count:
                found.append({"counter": f"{name}.{key}", "value": count})
    return found


def telemetry(function):
    result = {}
    for name in ("_ME_REPORT", "_RACE_REPORT"):
        value = function.__globals__.get(name)
        if isinstance(value, dict):
            result[name] = {str(key): val for key, val in value.items()
                            if isinstance(val, (str, int, float, bool)) or val is None}
    return result


def worker(job):
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine

    frozen = verify_frozen_inputs()
    if sha(engine.__file__) != frozen["engine"]["sha256"]:
        raise RuntimeError("ENGINE_SHA_MISMATCH")
    for field, hash_field in (("path", "sha256"), ("opponent", "opponent_sha256")):
        if sha(ROOT / job[field]) != job[hash_field]:
            raise RuntimeError(f"JOB_SHA_MISMATCH {field}")
    log = io.StringIO()
    functions = []
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        for field in ("path", "opponent"):
            path = ROOT / job[field]
            functions.append(get_last_callable(path.read_text(), path=str(path)))
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": job["seed"]})
        durations = [[], []]
        exceptions = [[], []]

        def timed(index):
            def invoke(obs, config):
                start = time.perf_counter()
                try:
                    return functions[index](obs, config)
                except Exception as exc:
                    exceptions[index].append(repr(exc))
                    raise
                finally:
                    durations[index].append(time.perf_counter() - start)
            return invoke

        agents = [None, None]
        agents[job["seat"]] = timed(0)
        agents[1 - job["seat"]] = timed(1)
        started = time.perf_counter()
        env.run(agents)
        wall = time.perf_counter() - started
    rewards = [state.reward for state in env.steps[-1]]
    statuses = [state.status for state in env.steps[-1]]
    margin = rewards[job["seat"]] - rewards[1 - job["seat"]] \
        if all(value is not None for value in rewards) else None
    return {
        "rewards": rewards,
        "margin": margin,
        "score": 1.0 if margin is not None and margin > 0 else 0.0 if margin is not None and margin < 0 else 0.5 if margin == 0 else None,
        "statuses": statuses,
        "steps": len(env.steps),
        "exceptions": exceptions,
        "caught_errors": {"candidate": error_counters(functions[0]), "opponent": error_counters(functions[1])},
        "telemetry": {"candidate": telemetry(functions[0]), "opponent": telemetry(functions[1])},
        "timing_seconds": durations,
        "wall_seconds": wall,
        "stdout": log.getvalue()[-3000:],
        "worker_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024),
    }


def key(job):
    return "|".join(str(job[name]) for name in ("stage", "agent", "seed", "seat", "opponent_sha256"))


def read_rows():
    path = OUT / "games.jsonl"
    if not path.exists():
        return {}
    rows = {}
    for number, line in enumerate(path.read_text().splitlines(), 1):
        row = json.loads(line)
        if row["key"] in rows:
            raise RuntimeError(f"DUPLICATE_GAME_KEY line={number} key={row['key']}")
        rows[row["key"]] = row
    return rows


def append_row(row):
    with (OUT / "games.jsonl").open("a") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def candidate_valid(result):
    return result.get("steps") == 720 and result.get("statuses") == ["DONE", "DONE"] \
        and not result.get("candidate_timeout", False) \
        and not result.get("exceptions", [["missing"]])[0] \
        and not result.get("caught_errors", {}).get("candidate")


def execute(job):
    started = stamp()
    command = [sys.executable, str(Path(__file__).resolve()), "--worker", json.dumps(job)]
    try:
        proc = subprocess.run(command, cwd=ROOT, env=dict(os.environ, **THREAD_ENV),
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
    return {"key": key(job), "job": job, "started_at": started,
            "completed_at": stamp(), "result": result}


def make_job(stage, agent, path, opponent, seed, seat):
    return {"stage": stage, "agent": agent, "path": path, "sha256": sha(ROOT / path),
            "opponent": opponent, "opponent_sha256": sha(ROOT / opponent),
            "seed": int(seed), "seat": int(seat)}


def run_jobs(name, jobs):
    verify_frozen_inputs()
    rows = read_rows()
    if len({key(job) for job in jobs}) != len(jobs):
        raise RuntimeError("DUPLICATE_BATCH_KEY")
    for job in jobs:
        old = rows.get(key(job))
        if old and old["job"] != job:
            raise RuntimeError(f"RESUME_IDENTITY_MISMATCH {key(job)}")
    pending = [job for job in jobs if key(job) not in rows]
    print(json.dumps({"event": "resume", "batch": name, "skipped": len(jobs) - len(pending),
                      "remaining": len(pending), "workers": WORKERS}), flush=True)
    state = {"batch": name, "status": "RUNNING", "workers": WORKERS, "total": len(jobs),
             "preregistration_sha256": sha(PREREG), "updated_at": stamp()}

    def persist():
        state["completed"] = sum(key(job) in rows for job in jobs)
        state["updated_at"] = stamp()
        atomic(OUT / "state.json", state)

    persist()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            iterator = iter(pending)
            active = {}
            for _ in range(WORKERS):
                job = next(iterator, None)
                if job:
                    active[pool.submit(execute, job)] = job
            while active:
                done, _ = concurrent.futures.wait(active, return_when=concurrent.futures.FIRST_COMPLETED)
                for future in done:
                    job = active.pop(future)
                    row = future.result()
                    append_row(row)
                    rows[row["key"]] = row
                    persist()
                    print(json.dumps({"event": "game", "completed": state["completed"],
                                      "total": len(jobs), "key": row["key"],
                                      "valid": candidate_valid(row["result"])}), flush=True)
                    job = next(iterator, None)
                    if job:
                        active[pool.submit(execute, job)] = job
        state["status"] = "COMPLETE"
        persist()
    except BaseException as exc:
        state.update(status="BLOCKED", error=repr(exc))
        persist()
        raise
    return [rows[key(job)] for job in jobs]


def quantile(values, probability):
    ordered = sorted(values)
    if not ordered:
        return None
    return ordered[min(len(ordered) - 1, math.ceil(probability * len(ordered)) - 1)]


def runtime(rows):
    calls = [value for row in rows for value in row["result"].get("timing_seconds", [[], []])[0]]
    return {"games": len(rows), "calls": len(calls), "max_step_seconds": max(calls, default=0),
            "p99_step_seconds": quantile(calls, 0.99),
            "invalid_games": sum(not candidate_valid(row["result"]) for row in rows),
            "candidate_exceptions": sum(len(row["result"].get("exceptions", [[], []])[0]) for row in rows),
            "candidate_caught_errors": sum(len(row["result"].get("caught_errors", {}).get("candidate", [])) for row in rows),
            "opponent_caught_error_games": sum(bool(row["result"].get("caught_errors", {}).get("opponent")) for row in rows)}


def score_summary(rows):
    scores = [row["result"].get("score") for row in rows]
    usable = [value for value in scores if value is not None]
    return {"n": len(rows), "wins": usable.count(1.0), "draws": usable.count(0.5),
            "losses": usable.count(0.0), "score_rate": statistics.mean(usable) if usable else None,
            "invalid": sum(not candidate_valid(row["result"]) for row in rows)}


def report_path(suffix):
    now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d-%H%M")
    return ROOT / "coordination/reports/codex" / f"{now}-EXP021-{suffix}.md"


def telemetry_value(row, key_name):
    return row["result"].get("telemetry", {}).get("candidate", {}).get("_ME_REPORT", {}).get(key_name, 0)


def smoke_jobs(variants):
    agents = {"P": PARENT, **{arm: spec["path"] for arm, spec in variants.items()}}
    return [make_job("stage1", agent, path, OPPONENT, 5000, seat)
            for agent, path in agents.items() for seat in (0, 1)]


def check_smoke(rows):
    grouped = {agent: [row for row in rows if row["job"]["agent"] == agent]
               for agent in ("P", *WRAPPERS)}
    checks = {}
    for agent, part in grouped.items():
        ok = len(part) == 2 and all(candidate_valid(row["result"]) for row in part)
        if agent == "P":
            ok = ok and all("_RACE_REPORT" in row["result"]["telemetry"]["candidate"] for row in part)
        elif agent in ("H1a", "H1b"):
            key_name = "horizon_32_turns" if agent == "H1a" else "horizon_40_turns"
            ok = ok and sum(telemetry_value(row, "mirror_detected_games") for row in part) > 0 \
                and sum(telemetry_value(row, key_name) for row in part) > 0
        elif agent == "H2":
            ok = ok and all(telemetry_value(row, "step0_sell_units_removed") > 0 for row in part) \
                and all(telemetry_value(row, "adjusted_mirror_detected_games") > 0 for row in part) \
                and all(telemetry_value(row, "first_turn_cash_difference") >= 1 for row in part) \
                and all(telemetry_value(row, "level24_set_count") > 0 for row in part)
        elif agent == "H3":
            ok = ok and sum(telemetry_value(row, "escalated_32_set_count") for row in part) > 0 \
                and sum(telemetry_value(row, "horizon_32_turns") for row in part) > 0
        elif agent == "H4":
            ok = ok and sum(telemetry_value(row, "mirror_detected_games") for row in part) > 0 \
                and sum(telemetry_value(row, "step717_liquidation_games") for row in part) > 0 \
                and sum(telemetry_value(row, "step717_sell_units") for row in part) > 0
        checks[agent] = {"passed": ok, "runtime": runtime(part),
                         "telemetry": [row["result"]["telemetry"]["candidate"] for row in part]}
    result = {"status": "PASS" if all(item["passed"] for item in checks.values()) else "STOP",
              "checks": checks, "preregistration_sha256": sha(PREREG)}
    atomic(OUT / "telemetry-smoke.json", result)
    return result


def stage1_jobs(variants):
    agents = {"P": PARENT, **{arm: spec["path"] for arm, spec in variants.items()}}
    return [make_job("stage1", agent, path, OPPONENT, seed, seat)
            for agent, path in agents.items() for seed in range(5000, 5050) for seat in (0, 1)]


def write_stage1(rows, smoke):
    grouped = {agent: [row for row in rows if row["job"]["agent"] == agent]
               for agent in ("P", *WRAPPERS)}
    stats = {agent: {**score_summary(part), "runtime": runtime(part)} for agent, part in grouped.items()}
    baseline = stats["P"]["score_rate"]
    if smoke["status"] != "PASS" or stats["P"]["invalid"] or not 0.45 <= baseline <= 0.55:
        verdict = "STOP"
        passing = []
    else:
        passing = [arm for arm in WRAPPERS if stats[arm]["invalid"] == 0 and stats[arm]["score_rate"] >= 0.60]
        verdict = "SUCCESS" if passing else "FAIL"
    result = {"verdict": verdict, "baseline_score_rate": baseline, "passing_arms": passing,
              "arms": stats, "smoke": smoke, "preregistration_sha256": sha(PREREG)}
    atomic(OUT / "stage1-summary.json", result)
    lines = [verdict, "", "[LOCAL] EXP-021 Stage 1 screen. Submission/Kaggle download/search-loop write: none.", "",
             "| arm | score rate | W/D/L | pass | activation | max step | p99 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for agent in ("P", *WRAPPERS):
        item = stats[agent]
        activation = "N/A" if agent == "P" else str(sum(
            telemetry_value(row, "mirror_detected_games") + telemetry_value(row, "adjusted_mirror_detected_games")
            + telemetry_value(row, "escalated_32_set_count") + telemetry_value(row, "step717_liquidation_games")
            for row in grouped[agent]))
        passed = 0.45 <= item["score_rate"] <= 0.55 if agent == "P" else item["score_rate"] >= 0.60
        lines.append(f"| {agent} | {item['score_rate']:.4f} | {item['wins']}/{item['draws']}/{item['losses']} | {passed} | {activation} | {item['runtime']['max_step_seconds']:.6f} | {item['runtime']['p99_step_seconds']:.6f} |")
    lines.extend(["", f"Passing arms: {', '.join(passing) if passing else 'none'}.",
                  f"Opponent-side caught-error games were recorded but not invalidated: {sum(item['runtime']['opponent_caught_error_games'] for item in stats.values())}.",
                  "", "다음 행동 2개:", "1. SUCCESS이면 통과 arm만 frozen Stage 2로 진행한다.",
                  "2. FAIL/STOP이면 기준을 바꾸지 않고 EXP-021을 종료한다.", ""])
    path = report_path("STAGE1")
    path.write_text("\n".join(lines))
    result["report"] = str(path.relative_to(ROOT))
    atomic(OUT / "stage1-summary.json", result)
    return result


def do_smoke():
    variants = prepare_variants()
    return check_smoke(run_jobs("telemetry-smoke", smoke_jobs(variants)))


def write_smoke_stop(smoke):
    lines = [
        "STOP",
        "",
        "[LOCAL] EXP-021은 Stage 1 본 실행 전에 telemetry smoke에서 중단했다.",
        "",
        "- 무엇을 시험했는가: 부모와 H1a/H1b/H2/H3/H4를 seed 5000, 양 좌석으로 O(127ed3e6 exact)와 각 2경기 실행했다. 이 12경기는 사전등록상 Stage 1에 포함될 예정이었으나 이후 588경기는 실행하지 않았다.",
        "- 왜 멈췄는가: H2가 양 경기 모두 step-0 SELL 1단위 감소를 발동하지 못해 첫 턴 현금 차가 0이었다. 사전등록은 H2의 각 smoke 경기에서 현금 차 >= 1을 요구한다.",
        "- 측정 결과: 12/12 valid, candidate exception/caught error/timeout 0. H1a/H1b/H3/H4 telemetry는 양 좌석에서 발동했다.",
        "- 막힌 점: 카드의 H2는 step 0의 첫 SELL 주문을 1 줄이라고 지정하지만, 실제 부모 action에서는 줄일 qualifying SELL이 없었다. 다른 턴이나 다른 주문을 선택하는 것은 카드에 없는 판단이다.",
        "",
        "| arm | smoke | 핵심 telemetry seat0 / seat1 | max step (s) | p99 (s) |",
        "|---|---|---|---:|---:|",
    ]
    for agent in ("P", *WRAPPERS):
        item = smoke["checks"][agent]
        if agent == "P":
            detail = "race_mirror=1 / 1"
        else:
            reports = [entry.get("_ME_REPORT", {}) for entry in item["telemetry"]]
            if agent == "H1a":
                detail = f"horizon32={reports[0].get('horizon_32_turns')} / {reports[1].get('horizon_32_turns')}"
            elif agent == "H1b":
                detail = f"horizon40={reports[0].get('horizon_40_turns')} / {reports[1].get('horizon_40_turns')}"
            elif agent == "H2":
                detail = (f"removed={reports[0].get('step0_sell_units_removed')}/{reports[1].get('step0_sell_units_removed')}; "
                          f"cash_diff={reports[0].get('first_turn_cash_difference')}/{reports[1].get('first_turn_cash_difference')}")
            elif agent == "H3":
                detail = f"escalated32={reports[0].get('escalated_32_set_count')} / {reports[1].get('escalated_32_set_count')}"
            else:
                detail = f"step717_units={reports[0].get('step717_sell_units')} / {reports[1].get('step717_sell_units')}"
        run = item["runtime"]
        lines.append(f"| {agent} | {'PASS' if item['passed'] else 'FAIL'} | {detail} | {run['max_step_seconds']:.6f} | {run['p99_step_seconds']:.6f} |")
    lines.extend([
        "",
        f"Preregistration SHA-256: `{sha(PREREG)}`.",
        "Raw append-only journal: `experiments/mirror_edge_20260926/games.jsonl` (12 rows).",
        "Stage 1 score rate: N/A (600경기 screen 미실행). Stage 2/3/final/release: N/A.",
        "P4 panel: N/A; STOP 이전이므로 판정에 사용하지 않았다.",
        "Submission/Kaggle download/search-loop write/launchd change: none.",
        "",
        "다음 행동 2개:",
        "1. Coordinator가 H2의 정확한 대체 조작(턴·주문·현금 차 계산)을 새 카드로 발행할지 결정한다.",
        "2. H2를 제외하고 H1a/H1b/H3/H4만 진행하려면 표본을 보기 전 새 사전등록으로 별도 승인한다.",
        "",
    ])
    path = report_path("STAGE1")
    path.write_text("\n".join(lines))
    result = {"verdict": "STOP", "reason": "H2_TELEMETRY_NOT_ACTIVATED",
              "stage1_games_completed": 12, "stage1_games_planned": 600,
              "stage1_score_rate": None, "report": str(path.relative_to(ROOT)),
              "preregistration_sha256": sha(PREREG)}
    atomic(OUT / "stage1-summary.json", result)
    return result


def do_stage1():
    variants = prepare_variants()
    smoke = json.loads((OUT / "telemetry-smoke.json").read_text()) if (OUT / "telemetry-smoke.json").exists() else do_smoke()
    if smoke["status"] != "PASS":
        return write_smoke_stop(smoke)
    return write_stage1(run_jobs("stage1", stage1_jobs(variants)), smoke)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=("prepare", "smoke", "stage1"))
    parser.add_argument("--worker")
    args = parser.parse_args()
    if args.worker:
        os.environ.update(THREAD_ENV)
        print(json.dumps(worker(json.loads(args.worker)), allow_nan=False))
    elif args.command == "prepare":
        print(json.dumps(prepare_variants(), indent=2))
    elif args.command == "smoke":
        print(json.dumps(do_smoke(), indent=2))
    elif args.command == "stage1":
        print(json.dumps(do_stage1(), indent=2))
    else:
        parser.error("choose a command")
