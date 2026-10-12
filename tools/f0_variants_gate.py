#!/usr/bin/env python3
"""F0 LIVE-CLAIM-VARIANTS runner: loader-faithful 22-episode gate + fixed-seed diagnostics.

Work order: coordination/proposals/claude/20260920-F0-LIVE-CLAIM-VARIANTS-WORK-ORDER.md

Why this exists instead of calling ``tools/instrument.py`` on a path: ``instrument.load_agent`` returns the
module attribute ``agent``.  Kaggle's loader (and ``env.run("main.py")``) instead exec()s the file and takes the
LAST callable.  For P2-family files those are different objects (e.g. ``_y_agent_shopherd`` vs ``agent``) and
play differently, so a path-based instrument run does not measure what is submitted.  This runner reuses
``instrument.instrumented_run`` (same counters, same timing) but hands it the loader's entry point.
The tool-default (module ``agent``) runs are still recorded, under ``tool_default_entry/``, for comparability.

Seeds are fixed by the work order; there is intentionally no option to change them.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

GATE_SEEDS = list(range(1000, 1010))          # starter, both seats  -> 20 episodes
SELF_SEEDS = [1000, 1001]                     # self-play            -> 2 episodes
DIAG_SEEDS_START, DIAG_SEEDS_N = 2000, 10     # seed 2000-2009, seats alternate -> 20 games per pair
EPISODE_LIMIT_S = 1200.0
EPISODE_GATE_S = EPISODE_LIMIT_S * 0.8        # 960
AGENT_NOMINAL_S = 719 * 1.0 + 60.0            # 779 (AGENTS.md section 6)
AGENT_GATE_S = AGENT_NOMINAL_S * 0.8          # 623.2

CANDIDATES = {
    "v1": {
        "builder_key": "v1",
        "release": "releases/public-goodpjw2008-kaggriculture-melon-threshold-squeeze-2749-exact",
        "label": "V1 goodpjw2008 melon-threshold-squeeze",
    },
    "v2": {
        "builder_key": "v2",
        "release": "releases/public-seyitkaangunes-kaggriculture-2820-score-exact",
        "label": "V2 seyitkaangunes 2820-score (notebook default USE_CADENCE=True)",
    },
}
P2 = "releases/public-lynnsakurai-farming-score-v2-exact/main.py"
P1 = "releases/public-alperen-before-dawn-stock-cash-sales-exact/main.py"


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def loader_entrypoint(path):
    """Exactly what Kaggle / kaggle_environments does with a main.py: exec, take last callable."""
    from kaggle_environments.agent import get_last_callable
    return get_last_callable(Path(path).read_text(encoding="utf-8"), path=str(path))


def module_agent_name(path) -> str:
    env: dict = {}
    exec(compile(Path(path).read_text(encoding="utf-8"), str(path), "exec"), env)
    return getattr(env.get("agent"), "__name__", None)


# ---------------------------------------------------------------- identity / clean room
def identity(key: str) -> dict:
    import build_public_exact as builder
    info = CANDIDATES[key]
    rel = ROOT / info["release"]
    manifest = json.loads((rel / "manifest.json").read_text(encoding="utf-8"))
    tar_sha = sha256_file(rel / "submission.tar.gz")
    main_sha = sha256_file(rel / "main.py")
    with tarfile.open(rel / "submission.tar.gz", "r:gz") as tar:
        names = tar.getnames()
        member_sha = hashlib.sha256(tar.extractfile("main.py").read()).hexdigest()
    rebuilds = []
    for label in ("A", "B"):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            m = builder.build(info["builder_key"], ROOT, out)
            rebuilds.append({"build": label, "tar_sha256": m["artifact"]["sha256"]})
    ok = (
        names == ["main.py"] and member_sha == main_sha == manifest["artifact"]["members"]["main.py"]
        and tar_sha == manifest["artifact"]["sha256"] and all(r["tar_sha256"] == tar_sha for r in rebuilds)
        and all(manifest["notebook_expected_matches"].values())
    )
    return {"status": "PASS" if ok else "FAIL", "tar_sha256": tar_sha, "main_py_sha256": main_sha,
            "tar_members": names, "tar_member_main_sha256": member_sha,
            "manifest_expected": manifest["notebook_expected_sha256"],
            "manifest_expected_matches": manifest["notebook_expected_matches"],
            "rebuilds_in_runner": rebuilds, "release_build_sha256": tar_sha}


def isolation_probe_child(main_path: str, out_path: str) -> None:
    """Run inside a subprocess started in an empty clean-room dir (see isolation())."""
    import io
    from kaggle_environments import make
    phase = {"name": "load"}
    events: dict = {"load": [], "agent": []}
    opened: dict = {"load": [], "agent": []}
    imports: dict = {"load": set(), "agent": set()}

    def hook(event, args):
        name = phase["name"]
        if name not in events:
            return
        if event.startswith("socket.") or event in {"subprocess.Popen", "os.system", "os.exec", "os.posix_spawn",
                                                     "os.spawn", "os.fork", "ctypes.dlopen", "urllib.Request"}:
            events[name].append([event, repr(args)[:160]])
        elif event == "open":
            path = args[0]
            if isinstance(path, (str, bytes, os.PathLike)):
                opened[name].append(str(path))
        elif event == "import":
            imports[name].add(str(args[0]))

    sys.addaudithook(hook)
    raw = Path(main_path).read_text(encoding="utf-8")
    from kaggle_environments.agent import get_last_callable
    fn = get_last_callable(raw, path=main_path)

    def wrapper(obs, config=None):
        prev = phase["name"]
        phase["name"] = "agent"
        try:
            return fn(obs, config) if fn.__code__.co_argcount >= 2 else fn(obs)
        finally:
            phase["name"] = prev

    phase["name"] = "idle"
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 1000})
    env.run([wrapper, "starter"])
    final = env.steps[-1]
    result = {
        "entrypoint": getattr(fn, "__name__", None), "steps": len(env.steps),
        "statuses": [s.status for s in final],
        "network_or_process_events": events,
        "opens_during_agent_calls": sorted(set(opened["agent"])),
        "opens_during_load": sorted(set(opened["load"])),
        "modules_imported_during_load": sorted(imports["load"]),
        "modules_imported_during_agent_calls": sorted(imports["agent"]),
    }
    Path(out_path).write_text(json.dumps(result, indent=2), encoding="utf-8")


def isolation(key: str, py: str) -> dict:
    info = CANDIDATES[key]
    rel = ROOT / info["release"]
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean_room"
        clean.mkdir()
        with tarfile.open(rel / "submission.tar.gz", "r:gz") as tar:
            tar.extractall(clean)
        listing = sorted(p.name for p in clean.iterdir())
        imp = subprocess.run([py, "-c", "import main; print(callable(main.agent))"], cwd=clean,
                             capture_output=True, text=True, timeout=120)
        probe_out = Path(tmp) / "probe.json"
        probe = subprocess.run([py, str(Path(__file__).resolve()), "--isolation-child", str(clean / "main.py"),
                                str(probe_out)], cwd=clean, capture_output=True, text=True, timeout=170)
        detail = json.loads(probe_out.read_text()) if probe_out.exists() else {"error": probe.stderr[-800:]}
    net = detail.get("network_or_process_events", {})
    clean_events = not net.get("load") and not net.get("agent")
    no_file_opens = not detail.get("opens_during_agent_calls")
    ok = (listing == ["main.py"] and imp.returncode == 0 and imp.stdout.strip() == "True"
          and clean_events and no_file_opens and detail.get("steps") == 720
          and detail.get("statuses") == ["DONE", "DONE"])
    return {"status": "PASS" if ok else "FAIL", "clean_room_listing": listing,
            "import_main_ok": imp.returncode == 0 and imp.stdout.strip() == "True",
            "import_stderr": imp.stderr[-400:], "probe": detail}


# ---------------------------------------------------------------- gate
def gate_episode(main_path: str, seat: str, seed: int):
    import instrument
    cand_a = loader_entrypoint(main_path)
    if seat == "self":
        agents, timed = [cand_a, loader_entrypoint(main_path)], (0, 1)
    elif seat == "seat0":
        agents, timed = [cand_a, "starter"], (0,)
    else:
        agents, timed = ["starter", cand_a], (1,)
    return instrument.instrumented_run(agents, seed=seed, episode_steps=720, time_agent_indices=timed)


def run_gate(key: str, outdir: Path) -> dict:
    import instrument
    from gate_contract import document
    info = CANDIDATES[key]
    main_path = str(ROOT / info["release"] / "main.py")
    entry = loader_entrypoint(main_path).__name__
    plan = ([("seat0", s) for s in GATE_SEEDS] + [("seat1", s) for s in GATE_SEEDS]
            + [("self", s) for s in SELF_SEEDS])
    assert len(plan) == 22
    files = {"seat0": f"{key}_vs_starter.json", "seat1": f"starter_vs_{key}.json", "self": f"{key}_self.json"}
    reports: dict = {"seat0": [], "seat1": [], "self": []}
    for seat, seed in plan:
        rep = gate_episode(main_path, seat, seed)
        reports[seat].append(rep)
        print(f"[gate {key}] {seat} seed={seed} rewards={rep.rewards} statuses={rep.statuses} "
              f"steps={rep.steps} wall={rep.wall_seconds:.2f}s", flush=True)
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    engine_sha = hashlib.sha256(Path(K.__file__).read_bytes()).hexdigest()
    assert engine_sha == instrument.EXPECTED_ENGINE_SHA, "engine SHA differs from ENGINE_LOCK"
    cand_indices = {"seat0": (0,), "seat1": (1,), "self": (0, 1)}
    agg = {"episodes": 0, "candidate_player_runs": 0, "completed_720_done_done": 0, "exceptions": 0,
           "max_episode_wall_seconds": 0.0, "max_agent_total_seconds_per_player_episode": 0.0,
           "max_episode_p99_turn_ms": 0.0, "max_turn_ms": 0.0}
    counters = {k: 0 for k in ("noop_actions", "shed_discarded", "shed_unsold", "orders_truncated",
                               "sell_unfilled", "buy_failed", "hire_failed", "seed_blocked_plant",
                               "hands_length_mismatch_count")}
    results_vs_starter = {"W": 0, "D": 0, "L": 0}
    per_episode = []
    for seat, lst in reports.items():
        for rep in lst:
            agg["episodes"] += 1
            done = rep.steps == 720 and all(s == "DONE" for s in rep.statuses)
            agg["completed_720_done_done"] += int(done)
            agg["max_episode_wall_seconds"] = max(agg["max_episode_wall_seconds"], rep.wall_seconds)
            for pid in cand_indices[seat]:
                agg["candidate_player_runs"] += 1
                c = rep.players[pid]
                agg["exceptions"] += c.exceptions
                for k in counters:
                    counters[k] += getattr(c, k) if k != "sell_unfilled" else c.sell_unfilled
                m = rep.agent_ms_by_player[pid]
                agg["max_agent_total_seconds_per_player_episode"] = max(
                    agg["max_agent_total_seconds_per_player_episode"], m["total_s"])
                agg["max_episode_p99_turn_ms"] = max(agg["max_episode_p99_turn_ms"], m["p99"])
                agg["max_turn_ms"] = max(agg["max_turn_ms"], m["max"])
            if seat != "self":
                pid = cand_indices[seat][0]
                r = rep.rewards
                mine, theirs = r[pid], r[1 - pid]
                results_vs_starter["W" if mine > theirs else "L" if mine < theirs else "D"] += 1
            per_episode.append({"seat": seat, "seed": rep.seed, "rewards": rep.rewards, "statuses": rep.statuses,
                                "steps": rep.steps, "wall_seconds": round(rep.wall_seconds, 3)})
    schema_ok = agg["completed_720_done_done"] == 22 and agg["exceptions"] == 0
    runtime_ok = (agg["max_episode_wall_seconds"] <= EPISODE_GATE_S
                  and agg["max_agent_total_seconds_per_player_episode"] <= AGENT_GATE_S)
    verdict = "PASS" if schema_ok and runtime_ok else "FAIL"
    agg["max_episode_wall_seconds"] = round(agg["max_episode_wall_seconds"], 3)
    outdir.mkdir(parents=True, exist_ok=True)
    for seat, lst in reports.items():
        doc = document(
            verdict="PASS" if all(r.steps == 720 and all(s == "DONE" for s in r.statuses) for r in lst)
            else "INVALID",
            gate_passed=all(r.steps == 720 and all(s == "DONE" for s in r.statuses) for r in lst),
            reasons=["raw per-episode instrument reports; F0 gate verdict lives in gate_summary.json "
                     "(silent-failure counters recorded, not gating)"],
            engine_sha256=engine_sha,
            artifact_sha256={"candidate": sha256_file(main_path)},
            payload=[r.as_dict() for r in lst],
            extra={"entrypoint": "loader last callable", "entrypoint_name": entry, "seat": seat,
                   "runner": "tools/f0_variants_gate.py"})
        (outdir / files[seat]).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"verdict": verdict, "schema_ok": schema_ok, "runtime_ok": runtime_ok, "entrypoint_name": entry,
            "results_vs_starter_20": results_vs_starter, **agg, "silent_failure_counters": counters,
            "per_episode": per_episode, "raw_files": list(files.values()),
            "main_py_sha256": sha256_file(main_path), "engine_sha256": engine_sha}


# ---------------------------------------------------------------- diagnostics / tool-default runs
def diag_pairs():
    v1 = str(Path(CANDIDATES["v1"]["release"]) / "main.py")
    v2 = str(Path(CANDIDATES["v2"]["release"]) / "main.py")
    return [("v1_vs_p2", v1, P2), ("v2_vs_p2", v2, P2), ("v1_vs_p1_alperen", v1, P1),
            ("v2_vs_p1_alperen", v2, P1), ("v1_vs_v2", v1, v2)]


def run_arena(name: str, a: str, b: str, outdir: Path, py: str) -> dict:
    out = outdir / f"diag_{name}.json"
    cmd = [py, "tools/arena.py", "--a", a, "--b", b, "--seeds", str(DIAG_SEEDS_N),
           "--seed-start", str(DIAG_SEEDS_START), "--json", str(out)]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=3000,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    doc = json.loads(out.read_text(encoding="utf-8"))
    res = doc["payload"]
    return {"name": name, "a": a, "b": b, "exit": p.returncode, "verdict": doc.get("verdict"),
            "wins": res["wins"], "draws": res["draws"], "losses": res["losses"],
            "paired_score": res["paired_score"], "ci95": res["ci95"], "mean_margin": res["mean_margin"],
            "errors": res["errors"], "games": res["games"], "seed_values": res["seed_values"],
            "artifact_sha256": doc["artifact_sha256"], "engine_sha256": doc["engine_sha256"],
            "raw": out.name}


def run_tool_default(key: str, outdir: Path, py: str) -> dict:
    """The stock CLI (module ``agent``) exactly as the 09-19 gates ran it; recorded for comparability only."""
    main_path = str(Path(CANDIDATES[key]["release"]) / "main.py")
    seeds = [str(s) for s in GATE_SEEDS]
    runs = [("a", "b", f"{key}_vs_starter.json", main_path, "starter", seeds, "a"),
            ("b", "a", f"starter_vs_{key}.json", "starter", main_path, seeds, "b"),
            ("both", "both", f"{key}_self.json", main_path, main_path, [str(s) for s in SELF_SEEDS], "both")]
    outdir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for time_agent, gate_agent, fname, a, b, sd, _ in runs:
        cmd = [py, "tools/instrument.py", "--a", a, "--b", b, "--seeds", *sd, "--time-agent", time_agent,
               "--gate-agent", gate_agent, "--json", str(outdir / fname)]
        subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=3000,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        doc = json.loads((outdir / fname).read_text(encoding="utf-8"))
        summary[fname] = {"generic_verdict": doc["verdict"],
                          "episodes": len(doc["payload"]),
                          "completed_720_done_done": sum(1 for r in doc["payload"]
                                                        if r["steps"] == 720 and set(r["statuses"]) == {"DONE"}),
                          "rewards": [r["rewards"] for r in doc["payload"]]}
    return summary


def summarize(outdir: Path) -> None:
    """Merge per-candidate / per-pair partial results (each phase runs in its own <180 s shell call)."""
    def dump(name, obj):
        (outdir / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    gate = {k: json.loads((outdir / f"gate_{k}_summary.json").read_text()) for k in CANDIDATES
            if (outdir / f"gate_{k}_summary.json").exists()}
    if gate:
        dump("gate_summary.json", {
            "contract": "coordination/proposals/claude/20260920-F0-LIVE-CLAIM-VARIANTS-WORK-ORDER.md",
            "runner": "tools/f0_variants_gate.py (loader-faithful entry point: last callable, as Kaggle does)",
            "runtime_limits": {"episode_seconds": EPISODE_LIMIT_S,
                               "episode_gate_seconds_80_percent": EPISODE_GATE_S,
                               "per_agent_nominal_seconds": AGENT_NOMINAL_S,
                               "per_agent_gate_seconds_80_percent": AGENT_GATE_S},
            "silent_failure_policy": "recorded but excluded from F0 gate verdict",
            "candidates": gate})
    pairs = {}
    for name, _, _ in diag_pairs():
        f = outdir / f"diag_{name}.summary.json"
        if f.exists():
            pairs[name] = json.loads(f.read_text())
    if pairs:
        dump("diagnostic_summary.json", {"seeds": f"{DIAG_SEEDS_START}-{DIAG_SEEDS_START + DIAG_SEEDS_N - 1}",
                                         "seats": "alternating (both)", "games_per_pair": DIAG_SEEDS_N * 2,
                                         "pairs": pairs})
    td = {}
    for k in CANDIDATES:
        f = outdir / "tool_default_entry" / f"{k}_summary.json"
        if f.exists():
            td[k] = json.loads(f.read_text())
    if td:
        dump("tool_default_entry/summary.json", td)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", nargs="?", choices=["identity", "isolation", "gate", "diag", "tool-default", "summarize"])
    ap.add_argument("--outdir", default="experiments/results/f0_live_claim_variants_20260920")
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--isolation-child", nargs=2, metavar=("MAIN", "OUT"))
    ap.add_argument("--only", nargs="*", help="candidate keys (gate/tool-default) or pair names (diag)")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()
    if args.isolation_child:
        isolation_probe_child(*args.isolation_child)
        return
    if args.phase is None:
        ap.error("phase is required")
    outdir = ROOT / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    os.chdir(ROOT)
    t0 = time.time()

    def dump(name, obj):
        (outdir / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.phase == "identity":
        dump("identity_summary.json", {k: identity(k) for k in CANDIDATES})
    elif args.phase == "isolation":
        dump("isolation_summary.json", {k: isolation(k, args.python) for k in CANDIDATES})
    elif args.phase == "gate":
        for key in (args.only or list(CANDIDATES)):
            dump(f"gate_{key}_summary.json", run_gate(key, outdir))
    elif args.phase == "diag":
        wanted = args.only or [n for n, _, _ in diag_pairs()]
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futs = {pool.submit(run_arena, n, a, b, outdir, args.python): n for n, a, b in diag_pairs() if n in wanted}
            for fut in concurrent.futures.as_completed(futs):
                res = fut.result()
                dump(f"diag_{res['name']}.summary.json", res)
                print(f"diag {res['name']} W/D/L {res['wins']}/{res['draws']}/{res['losses']}", flush=True)
    elif args.phase == "tool-default":
        for key in (args.only or list(CANDIDATES)):
            dump(f"tool_default_entry/{key}_summary.json", run_tool_default(key, outdir / "tool_default_entry",
                                                                             args.python))
    if args.phase != "summarize":
        print(f"{args.phase} elapsed {time.time() - t0:.0f}s", flush=True)
    summarize(outdir)


if __name__ == "__main__":
    main()
