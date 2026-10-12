"""Reproduce selected saved d157 losses and record exact market commits."""
import contextlib
import csv
import gzip
import hashlib
import importlib
import io
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SPLIT = ROOT / "experiments/exp041_top2400/team-split.json"
META = ROOT / "analysis/d157_hosted_20260928/opponents.csv"
ENGINE_SHA = "bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e"

with contextlib.redirect_stdout(io.StringIO()):
    from kaggle_environments import make
    E = importlib.import_module("kaggle_environments.envs.kaggriculture.kaggriculture")


def run_one(row):
    eid = int(row["episode"])
    path = ROOT / f"private_artifacts/d157_hosted_20260928/raw/{eid}.json.gz"
    raw_bytes = path.read_bytes()
    raw = json.loads(gzip.decompress(raw_bytes))
    seed = int(row["seed"])
    our_seat = int(row["seat"])
    assert int(raw["info"]["seed"]) == seed
    assert seed not in range(9000, 9600)
    tape = [[step[s]["action"] for step in raw["steps"][1:]] for s in (0, 1)]
    assert len(tape[0]) == len(tape[1]) == 719
    commits = []
    ctx = {}
    original_market, original_commit = E._process_market, E._commit_unit

    def market(state, env):
        ctx["step"] = int(state[0].observation.step)
        ctx["farms"] = state[0].observation.farms
        return original_market(state, env)

    def commit(op, item, price, farm, private, book, shed_capacity=100):
        seat = 0 if farm is ctx["farms"][0] else 1
        ok = original_commit(op, item, price, farm, private, book, shed_capacity)
        if ok:
            commits.append((ctx["step"], seat, op, item, price))
        return ok

    E._process_market, E._commit_unit = market, commit
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
            env.run([lambda obs, cfg: tape[0][int(obs.step)],
                     lambda obs, cfg: tape[1][int(obs.step)]])
    finally:
        E._process_market, E._commit_unit = original_market, original_commit

    mismatch = []
    for k, (actual, expected) in enumerate(zip(env.steps, raw["steps"])):
        for s in (0, 1):
            for field in ("farms", "market", "private", "town"):
                value = expected[s]["observation"].get(field)
                if value is not None and actual[s].observation.get(field) != value:
                    mismatch.append((k, s, field))
    assert not mismatch, (eid, mismatch[:10])
    assert [x.status for x in env.steps[-1]] == ["DONE", "DONE"]
    assert [x.reward for x in env.steps[-1]] == [x["reward"] for x in raw["steps"][-1]]

    groups = defaultdict(lambda: [0, 0])
    by_step = defaultdict(lambda: [0, 0])
    requests = defaultdict(int)
    for seat in (0, 1):
        for step, action in enumerate(tape[seat]):
            for order in action.get("market", [])[:10]:
                if len(order) >= 3 and order[0] in ("SELL", "BUY_PRODUCT"):
                    requests[(seat, order[0], order[1])] += int(order[2])
    for step, seat, op, item, price in commits:
        quarter = min(3, step // 180)
        g = groups[(seat, quarter, op, item)]
        g[0] += 1
        g[1] += price
        g = by_step[(step, seat, op, item)]
        g[0] += 1
        g[1] += price
    return {
        "episode": eid, "team": row["op_team"], "seed": seed,
        "our_seat": our_seat, "result": row["result"],
        "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "engine_sha256": ENGINE_SHA, "parity_mismatches": 0,
        "rewards": [x.reward for x in env.steps[-1]],
        "groups": [{"seat": s, "quarter": q, "op": op, "item": item,
                    "units": value[0], "cash": value[1]}
                   for (s, q, op, item), value in sorted(groups.items())],
        "requests": [{"seat": s, "op": op, "item": item, "units": n}
                     for (s, op, item), n in sorted(requests.items())],
        "by_step": [{"step": step, "seat": seat, "op": op, "item": item,
                     "units": value[0], "cash": value[1]}
                    for (step, seat, op, item), value in sorted(by_step.items())],
    }


def main():
    assert hashlib.sha256(Path(E.__file__).read_bytes()).hexdigest() == ENGINE_SHA
    split = json.loads(SPLIT.read_text())
    select = set(split["select_teams"])
    holdout = set(split["holdout_teams"])
    assert not select & holdout and len(holdout) == 5
    rows = list(csv.DictReader(META.open()))
    chosen = [r for r in rows if r["submission_label"] == "d157"
              and r["result"] == "L" and 2400 <= float(r["op_lb_score"] or 0) < 2600
              and r["op_team"] in select]
    assert len(chosen) == 20
    with (OUT / "select_loss_fills.jsonl").open("w") as f:
        for row in chosen:
            result = run_one(row)
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
            f.flush()
            print(result["episode"], result["team"], "parity", result["parity_mismatches"], flush=True)


if __name__ == "__main__":
    main()
