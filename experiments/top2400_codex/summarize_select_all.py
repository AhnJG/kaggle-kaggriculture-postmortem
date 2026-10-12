"""Aggregate exact filled quantities in the 595 frozen select-team episodes."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def main():
    split = json.loads((ROOT / "experiments/exp041_top2400/team-split.json").read_text())
    select, holdout = set(split["select_teams"]), set(split["holdout_teams"])
    rows = [json.loads(line) for line in (OUT / "select_all_fills.jsonl").open()]
    assert len(rows) == 595 and len({r["episode"] for r in rows}) == 595
    assert all(r["team"] in select and r["team"] not in holdout and r["parity_mismatches"] == 0 for r in rows)
    groups = defaultdict(lambda: [0, 0, 0])
    by_team = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    for row in rows:
        target = row["target_seat"]
        requests = {(x["seat"], x["op"], x["item"]): x["units"] for x in row["requests"]}
        fills = defaultdict(lambda: [0, 0])
        for x in row["groups"]:
            g = fills[(x["seat"], x["op"], x["item"])]
            g[0] += x["units"]
            g[1] += x["cash"]
        for key in requests.keys() | fills.keys():
            seat, op, item = key
            side = "top" if seat == target else "field_opponent"
            index = (side, op, item)
            request = requests.get(key, 0)
            units, cash = fills[key]
            for table in (groups, by_team[row["team"]]):
                g = table[index]
                g[0] += request
                g[1] += units
                g[2] += cash
    def render(table):
        return [dict(side=side, op=op, item=item, requested=v[0], filled=v[1], cash=v[2],
                     fill_fraction=round(v[1]/v[0], 5) if v[0] else None,
                     mean_unit_price=round(v[2]/v[1], 3) if v[1] else None)
                for (side, op, item), v in sorted(table.items())]
    result = {"episodes": len(rows), "select_teams": len(select), "engine_parity": len(rows),
              "overall": render(groups), "by_team": {k: render(v) for k, v in sorted(by_team.items())}}
    (OUT / "select_all_summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    for x in result["overall"]:
        if x["side"] == "top" and x["item"] in ("WHEAT", "CARROT", "FERTILIZER", "MILK", "WOOL"):
            print(x)


if __name__ == "__main__":
    main()
