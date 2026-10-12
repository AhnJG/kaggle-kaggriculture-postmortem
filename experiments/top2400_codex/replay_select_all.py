"""Exact market fills for every selected TOP2400 replay; no holdout replay opened."""
import contextlib
import gzip
import hashlib
import importlib
import io
import json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ENGINE_SHA = "bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e"

with contextlib.redirect_stdout(io.StringIO()):
    from kaggle_environments import make
    E = importlib.import_module("kaggle_environments.envs.kaggriculture.kaggriculture")


def run_one(meta):
    eid = int(meta["episode"])
    raw_path = ROOT / f"private_artifacts/top2400_20260928/raw/{eid}.json.gz"
    raw_bytes = raw_path.read_bytes()
    raw = json.loads(gzip.decompress(raw_bytes))
    seed = int(meta["seed"])
    target_seat = int(meta["target_seat"])
    assert seed == int(raw["info"]["seed"])
    assert seed not in range(9000, 9600)
    tape = [[step[s]["action"] for step in raw["steps"][1:]] for s in (0, 1)]
    assert len(tape[0]) == len(tape[1]) == 719
    commits = defaultdict(lambda: [0, 0])
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
            q = min(3, ctx["step"] // 180)
            group = commits[(seat, q, op, item)]
            group[0] += 1
            group[1] += price
        return ok

    E._process_market, E._commit_unit = market, commit
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
            env.run([lambda obs, cfg: tape[0][int(obs.step)],
                     lambda obs, cfg: tape[1][int(obs.step)]])
    finally:
        E._process_market, E._commit_unit = original_market, original_commit

    mismatch = 0
    for actual, expected in zip(env.steps, raw["steps"]):
        for seat in (0, 1):
            for field in ("farms", "market", "private", "town"):
                value = expected[seat]["observation"].get(field)
                mismatch += int(value is not None and actual[seat].observation.get(field) != value)
    assert mismatch == 0, (eid, mismatch)
    assert [x.status for x in env.steps[-1]] == ["DONE", "DONE"]
    assert [x.reward for x in env.steps[-1]] == [x["reward"] for x in raw["steps"][-1]]
    requests = defaultdict(int)
    for seat in (0, 1):
        for action in tape[seat]:
            market = (action or {}).get("market", []) or []
            if not isinstance(market, list):
                continue
            for order in market[:10]:
                if isinstance(order, list) and len(order) >= 3 and order[0] in ("BUY_PRODUCT", "SELL"):
                    requests[(seat, order[0], order[1])] += int(order[2])
    return {"episode": eid, "team": meta["team"], "target_seat": target_seat,
            "seed": seed, "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "parity_mismatches": mismatch,
            "groups": [{"seat": s, "quarter": q, "op": op, "item": item,
                        "units": value[0], "cash": value[1]}
                       for (s, q, op, item), value in sorted(commits.items())],
            "requests": [{"seat": s, "op": op, "item": item, "units": n}
                         for (s, op, item), n in sorted(requests.items())]}


def main():
    assert hashlib.sha256(Path(E.__file__).read_bytes()).hexdigest() == ENGINE_SHA
    split = json.loads((ROOT / "experiments/exp041_top2400/team-split.json").read_text())
    select, holdout = set(split["select_teams"]), set(split["holdout_teams"])
    assert len(holdout) == 5 and not select & holdout
    meta = list({m["episode"]: m for m in json.loads((ROOT / "experiments/exp041_top2400/meta.json").read_text())}.values())
    chosen = [m for m in meta if m["team"] in select]
    assert len(chosen) == 595 and all(m["team"] not in holdout for m in chosen)
    output = OUT / "select_all_fills.jsonl"
    done = {json.loads(line)["episode"] for line in output.open()} if output.exists() else set()
    pending = [m for m in chosen if m["episode"] not in done]
    with ProcessPoolExecutor(max_workers=5) as pool, output.open("a") as f:
        for index, row in enumerate(pool.map(run_one, pending)):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            if index % 10 == 0:
                print(len(done) + index + 1, "/", len(chosen), row["episode"], flush=True)


if __name__ == "__main__":
    main()
