"""Post-gate diagnosis only: explain why a public-state screen found no mechanism."""
import collections
import hashlib
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
cohort = json.loads((HERE / "cohort.json").read_text())
ids = {row["episode"] for row in cohort["rows"]}
cash_path = ROOT / "analysis/exp050_divergence/cash50.jsonl"
events_path = ROOT / "analysis/exp050_divergence/events50b.jsonl"
def selected_rows(path):
    for line in path.open():
        match = re.search(r'"episode":\s*"(\d+)"', line)
        if match and match.group(1) in ids:
            yield json.loads(line)


cash = {x["episode"]: x for x in selected_rows(cash_path)}
events = {x["episode"]: x for x in selected_rows(events_path)}
assert set(cash) == ids and set(events) == ids
assert all(x["parity"] for x in cash.values())

summary = {"cash_source_sha256": hashlib.sha256(cash_path.read_bytes()).hexdigest(),
           "events_source_sha256": hashlib.sha256(events_path.read_bytes()).hexdigest(),
           "cohort_sha256": hashlib.sha256((HERE / "cohort.json").read_bytes()).hexdigest(),
           "all_cash_replays_reward_parity": True, "by_result": {}}
for result in ("L", "W"):
    subset = [row for row in cohort["rows"] if row["result"] == result]
    first = [events[row["episode"]]["events"][0] for row in subset
             if events[row["episode"]].get("events")]
    dominant = collections.Counter()
    means = collections.defaultdict(list)
    for row in subset:
        replay = cash[row["episode"]]
        own = int(row["seat"])
        item_cash = collections.defaultdict(lambda: [0.0, 0.0])
        for seat, _, op, item, _, amount in replay["groups"]:
            item_cash[item][seat] += (1 if op == "SELL" else -1) * amount
        delta = {item: v[1 - own] - v[own] for item, v in item_cash.items()}
        dominant[max(delta, key=delta.get)] += 1
        for item in ("WOOL", "MILK", "STRAWBERRY", "WHEAT", "FERTILIZER", "CARROT"):
            means[item].append(delta.get(item, 0))
    summary["by_result"][result] = {
        "n": len(subset),
        "n_with_material_action_divergence": len(first),
        "first_private_action_divergence_median_step": statistics.median(e["t"] for e in first) if first else None,
        "first_divergence_kind": dict(collections.Counter(e.get("kind", "units_only") for e in first)),
        "largest_opponent_net_cash_advantage_item": dict(dominant),
        "mean_opponent_minus_our_net_cash_by_item": {item: round(statistics.mean(vals), 2) for item, vals in means.items()},
    }

(HERE / "posthoc_cashflow.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary["by_result"], indent=2))
