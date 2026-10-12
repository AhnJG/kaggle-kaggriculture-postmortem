import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
rows = [json.loads(line) for line in (HERE / "games.jsonl").read_text().splitlines() if line]
groups = defaultdict(list)
by_key = {}
for row in rows:
    groups[(row["arm"], row["opponent"])].append(row)
    by_key[(row["arm"], row["opponent"], row["seed"], row["seat"])] = row


def valid(row):
    return (row["err"] is None and not row["agent_errors"]
            and row["statuses"] == ["DONE", "DONE"] and row["action_count"] == 719
            and row["score"] is not None)


panels = {}
for opponent in ("O127", "PUB01", "PUB12", "D"):
    candidate = sorted(groups[("H1", opponent)], key=lambda row: (row["seed"], row["seat"]))
    parent = sorted(groups[("P", opponent)], key=lambda row: (row["seed"], row["seat"]))
    matching = []
    for row in candidate:
        peer = by_key[("P", opponent, row["seed"], row["seat"])]
        matching.append(row["act_sha"] == peer["act_sha"])
    panels[opponent] = {
        "games_per_arm": len(candidate),
        "valid_h1": sum(valid(row) for row in candidate),
        "valid_parent": sum(valid(row) for row in parent),
        "activation_h1": sum(int(row["telemetry"].get("activation", 0)) for row in candidate),
        "act_sha_equal": sum(matching),
        "score_h1": sum(row["score"] for row in candidate) / len(candidate),
        "score_parent": sum(row["score"] for row in parent) / len(parent),
        "paired_score_delta": sum(
            row["score"] - by_key[("P", opponent, row["seed"], row["seat"])]["score"]
            for row in candidate
        ) / len(candidate),
        "max_step_h1": max(row["max_step"] for row in candidate),
        "max_step_parent": max(row["max_step"] for row in parent),
    }

fp_opponents = ("O127", "PUB01", "PUB12")
fp_games = sum(panels[opponent]["games_per_arm"] for opponent in fp_opponents)
fp_activation = sum(panels[opponent]["activation_h1"] for opponent in fp_opponents)
fp_equal = sum(panels[opponent]["act_sha_equal"] for opponent in fp_opponents)
all_valid = all(panel["valid_h1"] == panel["games_per_arm"]
                and panel["valid_parent"] == panel["games_per_arm"]
                for panel in panels.values())
fp_pass = all_valid and fp_games == 24 and fp_activation == 0 and fp_equal == 24
effect = panels["D"]
effect_pass = (all_valid and effect["games_per_arm"] == 12
               and effect["activation_h1"] == 12
               and effect["paired_score_delta"] > 0)
summary = {
    "verdict": "PASS" if fp_pass and effect_pass else "FAIL",
    "frozen_prereg_sha256": hashlib.sha256((HERE / "prereg.json").read_bytes()).hexdigest(),
    "all_valid": all_valid,
    "fp_pass": fp_pass,
    "effect_pass": effect_pass,
    "fp_games": fp_games,
    "fp_activation": fp_activation,
    "fp_act_sha_equal": fp_equal,
    "panels": panels,
    "max_step_h1": max(panel["max_step_h1"] for panel in panels.values()),
    "max_step_parent": max(panel["max_step_parent"] for panel in panels.values()),
}
(HERE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))

