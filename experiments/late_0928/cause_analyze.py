"""Aggregate the frozen cause panel without changing its selection or criteria."""
import collections
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
rows = [json.loads(line) for line in (HERE / "cause_games.jsonl").read_text().splitlines() if line.strip()]
assert len(rows) == 28, len(rows)
assert len({r["key"] for r in rows}) == 28
assert all(r["statuses"] == ["DONE", "DONE"] and r["action_count"] == 719 and not r["agent_errors"] for r in rows)

by_agent = {a: [r for r in rows if r["agent"] == a] for a in ("v074", "d157")}
items = sorted({f["item"] for r in rows for f in r["fills_after_575"]})
item_table = []
for item in items:
    line = {"item": item}
    for agent in ("v074", "d157"):
        fills = [f for r in by_agent[agent] for f in r["fills_after_575"] if f["item"] == item]
        qty = len(fills)
        line[agent] = {
            "sold_units": qty,
            "revenue": sum(f["price"] for f in fills),
            "avg_fill_price": None if not qty else sum(f["price"] for f in fills) / qty,
            "first_step": None if not qty else min(f["step"] for f in fills),
            "last_step": None if not qty else max(f["step"] for f in fills),
            "final_shed_units": sum(r["snapshots"]["719"]["shed"].get(item, 0) for r in by_agent[agent]),
        }
    line["d157_minus_v074"] = {
        "sold_units": line["d157"]["sold_units"] - line["v074"]["sold_units"],
        "revenue": line["d157"]["revenue"] - line["v074"]["revenue"],
        "final_shed_units": line["d157"]["final_shed_units"] - line["v074"]["final_shed_units"],
    }
    item_table.append(line)

pairs = []
for episode in sorted({r["episode"] for r in rows}):
    p = next(r for r in rows if r["episode"] == episode and r["agent"] == "v074")
    d = next(r for r in rows if r["episode"] == episode and r["agent"] == "d157")
    pairs.append({
        "episode": episode,
        "label": p["label"],
        "v074_score": p["score"],
        "d157_score": d["score"],
        "score_delta": d["score"] - p["score"],
        "margin_delta": d["margin"] - p["margin"],
        "money_delta_576": d["snapshots"]["576"]["money"] - p["snapshots"]["576"]["money"],
        "money_delta_648": d["snapshots"]["648"]["money"] - p["snapshots"]["648"]["money"],
        "money_delta_696": d["snapshots"]["696"]["money"] - p["snapshots"]["696"]["money"],
        "money_delta_719": d["snapshots"]["719"]["money"] - p["snapshots"]["719"]["money"],
    })

summary = {
    "games": len(rows),
    "pairs": len(pairs),
    "valid": True,
    "score": {a: sum(r["score"] for r in by_agent[a]) / len(by_agent[a]) for a in by_agent},
    "paired_score_delta": sum(p["score_delta"] for p in pairs) / len(pairs),
    "mean_margin_delta": sum(p["margin_delta"] for p in pairs) / len(pairs),
    "mean_money_delta_by_step": {str(s): sum(p[f"money_delta_{s}"] for p in pairs) / len(pairs) for s in (576,648,696,719)},
    "item_table": item_table,
    "pairs_detail": pairs,
    "max_step": max(r["max_step"] for r in rows),
}
(HERE / "cause_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps({k: v for k, v in summary.items() if k not in ("item_table", "pairs_detail")}, indent=2))
for row in sorted(item_table, key=lambda x: x["d157_minus_v074"]["revenue"], reverse=True):
    print(row)
