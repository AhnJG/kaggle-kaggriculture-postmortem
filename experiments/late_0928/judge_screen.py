"""Apply only the frozen LATE-0928 screen criteria."""
import collections
import json
import math
import pathlib
import random

HERE = pathlib.Path(__file__).resolve().parent
PRE = json.loads((HERE / "prereg.json").read_text())
META = {f"T{r['episode']}": r for r in json.loads((HERE.parents[0] / "exp033_tapes/meta.json").read_text())}


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


parents = {r["opponent"]: r for r in read_jsonl(HERE.parents[0] / "exp033_tapes/games-cloud.jsonl") if r["vid"] == "P"}
candidates = read_jsonl(HERE / "games-open.jsonl")
runtime = read_jsonl(HERE / "games-runtime.jsonl")
expected = json.loads((HERE / "jobs-open.json").read_text())
expected_keys = {f"{j[0]}|{j[2]}|{j[4]}|{j[5]}" for j in expected}
rows = {r["key"]: r for r in candidates}
assert set(rows) == expected_keys, (len(rows), len(expected_keys))


def invalid(row):
    return row["err"] is not None or row["statuses"] != ["DONE", "DONE"] or row["score"] is None or bool(row["agent_errors"]) or row["action_count"] != 719


def lower95(values, seed):
    rng = random.Random(seed)
    draws = []
    for _ in range(PRE["bootstrap"]["draws"]):
        draws.append(sum(values[rng.randrange(len(values))] for _ in values) / len(values))
    return sorted(draws)[int(0.025 * len(draws))]


runtime_by_vid = collections.defaultdict(list)
for row in runtime:
    runtime_by_vid[row["vid"]].append(row)
results = []
for index, candidate in enumerate(PRE["candidates"]):
    vid = candidate["id"]
    mine = [r for r in candidates if r["vid"] == vid]
    diffs = {"127_near": [], "other": []}
    for row in mine:
        family = META[row["opponent"]]["fam"]
        diffs[family].append(row["score"] - parents[row["opponent"]]["score"])
    rt = runtime_by_vid[vid]
    result = {
        "id": vid,
        "games": len(mine),
        "invalid": sum(invalid(r) for r in mine),
        "action_effect_games": sum(r["act_sha"] != parents[r["opponent"]]["act_sha"] for r in mine),
        "d127_point": sum(diffs["127_near"]) / len(diffs["127_near"]),
        "d127_lower95": lower95(diffs["127_near"], PRE["bootstrap"]["seed"] + index),
        "other_point": sum(diffs["other"]) / len(diffs["other"]),
        "runtime_games": len(rt),
        "runtime_invalid": sum(invalid(r) for r in rt),
        "runtime_max_step": max(r["max_step"] for r in rt),
    }
    result["open_runtime_pass"] = (
        result["invalid"] == 0
        and result["action_effect_games"] > 0
        and result["d127_lower95"] > PRE["thresholds"]["open_127_lower95_gt"]
        and result["other_point"] >= PRE["thresholds"]["open_other_point_ge"]
        and result["runtime_invalid"] == 0
        and result["runtime_max_step"] < PRE["thresholds"]["runtime_max_step_lt"]
    )
    result["verdict"] = "PENDING_CLOSED_LOOP" if result["open_runtime_pass"] else "FAIL"
    results.append(result)

out = {
    "verdict": "PENDING_CLOSED_LOOP" if any(r["open_runtime_pass"] for r in results) else "FAIL",
    "selected": None,
    "selection_rule": "No selection until frozen closed-loop jobs are complete; among full PASS candidates select highest d127 point.",
    "results": results,
}
(HERE / "screen_summary.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(json.dumps(out, indent=2, sort_keys=True))
