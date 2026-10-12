import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent


def wilson_lower(point, n, z=1.96):
    denominator = 1 + z * z / n
    center = point + z * z / (2 * n)
    half = z * math.sqrt(point * (1 - point) / n + z * z / (4 * n * n))
    return (center - half) / denominator


manifest = json.loads((HERE / "stage2-manifest.json").read_text())
jobs = json.loads((HERE / "jobs-stage2.json").read_text())
rows = [json.loads(line) for line in (HERE / "games-stage2.jsonl").read_text().splitlines() if line]
expected = {f"{j[0]}|{j[2]}|{j[4]}|{j[5]}" for j in jobs}
actual = {row["key"] for row in rows}
assert len(rows) == len(actual), "duplicate result keys"
assert expected == actual, {"missing": len(expected - actual), "extra": len(actual - expected)}

groups = defaultdict(lambda: defaultdict(list))
for row in rows:
    groups[row["vid"]][row["opponent"]].append(row)

parent_o1_scores = [row["score"] for row in groups["P"]["O1-127ed3e6"]]
parent_o1 = sum(parent_o1_scores) / len(parent_o1_scores)
results = []
for vid in manifest["candidates"]:
    opponent_results = {}
    invalid = 0
    for opponent in ("O1-127ed3e6", "O2-v171"):
        group = groups[vid][opponent]
        scores = [row["score"] for row in group if row["score"] is not None]
        counts = Counter(scores)
        point = sum(scores) / len(scores)
        opponent_invalid = sum(
            row["err"] is not None
            or row["statuses"] != ["DONE", "DONE"]
            or row.get("agent_errors")
            or row.get("action_count") != 719
            for row in group
        )
        invalid += opponent_invalid
        opponent_results[opponent] = {
            "n": len(group),
            "wins": counts[1.0],
            "draws": counts[0.5],
            "losses": counts[0.0],
            "score_rate": point,
            "wilson95_lower": wilson_lower(point, len(scores)),
            "invalid": opponent_invalid,
            "mean_margin": sum(row["margin"] for row in group) / len(group),
            "max_step": max(row["max_step"] for row in group),
        }
    passed = (
        invalid == 0
        and opponent_results["O1-127ed3e6"]["wilson95_lower"] > 0.50
        and opponent_results["O2-v171"]["wilson95_lower"] > 0.50
        and opponent_results["O2-v171"]["score_rate"] >= 0.65
        and opponent_results["O1-127ed3e6"]["score_rate"] >= parent_o1 - 0.02
    )
    results.append({"vid": vid, "opponents": opponent_results, "invalid": invalid, "passed": passed})

passed = [row["vid"] for row in results if row["passed"]]
summary = {
    "verdict": "PASS" if passed else "FAIL",
    "parent_o1_score": parent_o1,
    "parent_o1_floor": parent_o1 - 0.02,
    "parent_o2_score": sum(row["score"] for row in groups["P"]["O2-v171"]) / len(groups["P"]["O2-v171"]),
    "jobs": len(jobs),
    "raw_sha256": hashlib.sha256((HERE / "games-stage2.jsonl").read_bytes()).hexdigest(),
    "passed": passed,
    "results": results,
}
(HERE / "stage2-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
