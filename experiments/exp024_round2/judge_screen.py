import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
variants = {item["id"]: item for item in json.loads((HERE / "variants.json").read_text())}
jobs = json.loads((HERE / "jobs-screen.json").read_text())
rows = [json.loads(line) for line in (HERE / "games-screen.jsonl").read_text().splitlines() if line]
step0 = json.loads((HERE / "step0-summary.json").read_text())
parent_o1 = step0["opponents"]["O1-127ed3e6"]["score_rate"]

expected = {f"{j[0]}|{j[2]}|{j[4]}|{j[5]}" for j in jobs}
actual = {row["key"] for row in rows}
assert len(rows) == len(actual), "duplicate result keys"
assert expected == actual, {"missing": len(expected - actual), "extra": len(actual - expected)}

parent_actions = {}
for line in (HERE / "games-step0.jsonl").read_text().splitlines():
    row = json.loads(line)
    parent_actions[(row["opponent"], row["seed"], row["seat"])] = row["act_sha"]

groups = defaultdict(list)
for row in rows:
    groups[row["vid"]].append(row)

results = []
for vid, group in groups.items():
    by_opponent = defaultdict(list)
    for row in group:
        by_opponent[row["opponent"]].append(row)
    opponent_results = {}
    invalid = 0
    no_effect = True
    total_margin = 0
    max_step = 0.0
    for opponent, opponent_group in sorted(by_opponent.items()):
        scores = [row["score"] for row in opponent_group if row["score"] is not None]
        opponent_invalid = sum(
            row["err"] is not None
            or row["statuses"] != ["DONE", "DONE"]
            or row.get("agent_errors")
            or row.get("action_count") != 719
            for row in opponent_group
        )
        invalid += opponent_invalid
        total_margin += sum(row["margin"] or 0 for row in opponent_group)
        max_step = max(max_step, *(row["max_step"] for row in opponent_group))
        no_effect = no_effect and all(
            row["act_sha"] == parent_actions[(opponent, row["seed"], row["seat"])] for row in opponent_group
        )
        opponent_results[opponent] = {
            "wins": sum(score == 1.0 for score in scores),
            "draws": sum(score == 0.5 for score in scores),
            "losses": sum(score == 0.0 for score in scores),
            "score_rate": sum(scores) / len(scores),
            "margin": sum(row["margin"] or 0 for row in opponent_group),
            "invalid": opponent_invalid,
        }
    passed = (
        invalid == 0
        and opponent_results["O2-v171"]["score_rate"] >= 0.70
        and opponent_results["O1-127ed3e6"]["score_rate"] >= parent_o1
    )
    results.append({
        "vid": vid,
        "change": variants[vid]["change"],
        "sha256": variants[vid]["sha256"],
        "opponents": opponent_results,
        "invalid": invalid,
        "no_effect": no_effect,
        "total_margin": total_margin,
        "max_step": max_step,
        "passed": passed,
    })

results.sort(
    key=lambda row: (
        row["opponents"]["O2-v171"]["score_rate"],
        row["opponents"]["O1-127ed3e6"]["score_rate"],
        row["total_margin"],
    ),
    reverse=True,
)
advance = [row["vid"] for row in results if row["passed"]][:8]
summary = {
    "verdict": "PASS" if advance else "FAIL",
    "parent_o1_score": parent_o1,
    "parent_o2_score": step0["opponents"]["O2-v171"]["score_rate"],
    "jobs": len(jobs),
    "raw_sha256": hashlib.sha256((HERE / "games-screen.jsonl").read_bytes()).hexdigest(),
    "invalid": sum(row["invalid"] for row in results),
    "no_effect_variants": sum(row["no_effect"] for row in results),
    "advance": advance,
    "results": results,
}
(HERE / "screen-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({key: summary[key] for key in summary if key != "results"}, indent=2))
for row in results[:20]:
    print(row["vid"], row["opponents"]["O2-v171"]["score_rate"], row["opponents"]["O1-127ed3e6"]["score_rate"], row["total_margin"], row["no_effect"], row["change"])
