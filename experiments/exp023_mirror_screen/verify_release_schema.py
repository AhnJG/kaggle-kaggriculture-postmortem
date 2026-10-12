import hashlib
import json
from pathlib import Path

from kaggle_environments import make
from kaggle_environments.agent import get_last_callable


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "releases/mirror-screen-v171/main.py"
OPPONENT = ROOT / "releases/public-newmeta-127ed3e6-exact/main.py"
expected_sha = "496460f81869ebbd1bf80f3dd3c9440ef72c41819a831ee39a16f180d7c0bd5d"
assert hashlib.sha256(CANDIDATE.read_bytes()).hexdigest() == expected_sha

rows = []
for seat in (0, 1):
    candidate = get_last_callable(CANDIDATE.read_text(), path=str(CANDIDATE))
    opponent = get_last_callable(OPPONENT.read_text(), path=str(OPPONENT))
    counts = {"calls": 0, "schema_errors": 0, "hands_length_mismatches": 0}

    def checked(obs, config):
        action = candidate(obs, config)
        counts["calls"] += 1
        if not isinstance(action, dict) or not {"farmer", "hands", "market"}.issubset(action):
            counts["schema_errors"] += 1
            return action
        expected_hands = len(obs["farms"][obs["player"]]["hands"])
        if len(action["hands"]) != expected_hands:
            counts["hands_length_mismatches"] += 1
        return action

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 2300})
    env.run([checked, opponent] if seat == 0 else [opponent, checked])
    rows.append({
        "seat": seat,
        **counts,
        "statuses": [state.status for state in env.steps[-1]],
        "steps": len(env.steps),
    })

result = {
    "candidate_sha256": expected_sha,
    "seed": 2300,
    "rows": rows,
    "calls": sum(row["calls"] for row in rows),
    "schema_errors": sum(row["schema_errors"] for row in rows),
    "hands_length_mismatches": sum(row["hands_length_mismatches"] for row in rows),
    "passed": all(row["statuses"] == ["DONE", "DONE"] for row in rows)
    and all(row["steps"] == 720 for row in rows)
    and not any(row["schema_errors"] or row["hands_length_mismatches"] for row in rows),
}
(Path(__file__).resolve().parent / "release-schema-gate.json").write_text(json.dumps(result, indent=1) + "\n")
print(json.dumps(result, indent=1))
