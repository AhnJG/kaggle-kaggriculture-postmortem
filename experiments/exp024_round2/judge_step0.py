import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
jobs = json.loads((HERE / "jobs-step0.json").read_text())
rows = [json.loads(line) for line in (HERE / "games-step0.jsonl").read_text().splitlines() if line]
expected = {f"{j[0]}|{j[2]}|{j[4]}|{j[5]}" for j in jobs}
actual = {row["key"] for row in rows}
assert expected == actual, {"missing": sorted(expected - actual), "extra": sorted(actual - expected)}

by_opponent = defaultdict(list)
for row in rows:
    by_opponent[row["opponent"]].append(row)

summary = {
    "verdict": "PASS",
    "jobs": len(jobs),
    "workers": 5,
    "raw_sha256": hashlib.sha256((HERE / "games-step0.jsonl").read_bytes()).hexdigest(),
    "opponents": {},
}
for opponent, group in sorted(by_opponent.items()):
    invalid = sum(
        row["err"] is not None
        or row["statuses"] != ["DONE", "DONE"]
        or row.get("agent_errors")
        or row.get("action_count", 719) != 719
        for row in group
    )
    scores = [row["score"] for row in group if row["score"] is not None]
    summary["opponents"][opponent] = {
        "games": len(group),
        "wins": sum(score == 1.0 for score in scores),
        "draws": sum(score == 0.5 for score in scores),
        "losses": sum(score == 0.0 for score in scores),
        "score_rate": sum(scores) / len(scores),
        "invalid": invalid,
        "max_step": max(row["max_step"] for row in group),
    }
    if invalid:
        summary["verdict"] = "STOP"

if summary["opponents"]["O2-v171"]["score_rate"] != 0.5:
    summary["verdict"] = "STOP"

(HERE / "step0-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
