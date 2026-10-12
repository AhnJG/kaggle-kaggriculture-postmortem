"""Summarize exact selected-team trade fills without opening holdout data."""
import json
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent


def summarize(rows):
    counts = defaultdict(lambda: [0, 0, 0, 0])
    for row in rows:
        us = row["our_seat"]
        requests = {(x["seat"], x["op"], x["item"]): x["units"]
                    for x in row["requests"]}
        grouped = defaultdict(lambda: [0, 0])
        for x in row["groups"]:
            k = (x["seat"], x["op"], x["item"])
            grouped[k][0] += x["units"]
            grouped[k][1] += x["cash"]
        for k in requests.keys() | grouped.keys():
            seat, op, item = k
            g = counts[("d157" if seat == us else "opponent", op, item)]
            g[0] += requests.get(k, 0)
            g[1] += grouped[k][0]
            g[2] += grouped[k][1]
            g[3] += 1
    return [dict(side=side, op=op, item=item, requested=v[0], filled=v[1],
                 cash=v[2], episodes=v[3], fill_rate=round(v[1]/v[0], 4) if v[0] else None,
                 unit_price=round(v[2]/v[1], 2) if v[1] else None)
            for (side, op, item), v in sorted(counts.items())]


def main():
    rows = [json.loads(line) for line in (OUT / "select_loss_fills.jsonl").open()]
    assert len(rows) == 20 and all(r["parity_mismatches"] == 0 for r in rows)
    all_summary = summarize(rows)
    by_team = {team: summarize([r for r in rows if r["team"] == team])
               for team in sorted({r["team"] for r in rows})}
    out = {"episodes": len(rows), "parity_episodes": len(rows),
           "overall": all_summary, "by_team": by_team}
    (OUT / "select_loss_summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    for x in all_summary:
        if x["item"] in ("WHEAT", "CARROT", "FERTILIZER", "MILK", "WOOL"):
            print(x)


if __name__ == "__main__":
    main()
