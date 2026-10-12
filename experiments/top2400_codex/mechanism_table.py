"""Count observed WHEAT order cycles in parity-verified selected losses."""
import gzip
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def main():
    rows = [json.loads(line) for line in (OUT / "select_loss_fills.jsonl").open()]
    assert len(rows) == 20 and all(x["parity_mismatches"] == 0 for x in rows)
    cycles = []
    summary = defaultdict(lambda: [0, 0, 0, 0, 0])
    for row in rows:
        eid = row["episode"]
        raw = json.load(gzip.open(ROOT / f"private_artifacts/d157_hosted_20260928/raw/{eid}.json.gz"))
        by_step = {(x["step"], x["seat"], x["op"], x["item"]): x for x in row["by_step"]}
        for step in range(719):
            for seat in (0, 1):
                market = raw["steps"][step + 1][seat]["action"].get("market", [])[:10]
                wheat = [(i, x) for i, x in enumerate(market)
                         if len(x) >= 3 and x[:2] in (["SELL", "WHEAT"], ["BUY_PRODUCT", "WHEAT"])]
                sells = [(i, x) for i, x in wheat if x[0] == "SELL"]
                buys = [(i, x) for i, x in wheat if x[0] == "BUY_PRODUCT"]
                if not sells or not buys:
                    continue
                orientation = "SELL_THEN_BUY" if sells[0][0] < buys[0][0] else "BUY_THEN_SELL"
                sell = by_step.get((step, seat, "SELL", "WHEAT"), {"units": 0, "cash": 0})
                buy = by_step.get((step, seat, "BUY_PRODUCT", "WHEAT"), {"units": 0, "cash": 0})
                other_sell = by_step.get((step, 1 - seat, "SELL", "WHEAT"), {"units": 0})
                side = "d157" if seat == row["our_seat"] else "opponent"
                cycle = {"episode": eid, "team": row["team"], "step": step,
                         "side": side, "orientation": orientation,
                         "sell_requested": sum(int(x[2]) for _, x in sells),
                         "buy_requested": sum(int(x[2]) for _, x in buys),
                         "sell_filled": sell["units"], "buy_filled": buy["units"],
                         "net_cash": sell["cash"] - buy["cash"],
                         "other_wheat_sell_filled": other_sell["units"]}
                cycles.append(cycle)
                g = summary[(side, orientation)]
                g[0] += 1
                g[1] += sell["units"]
                g[2] += buy["units"]
                g[3] += sell["cash"] - buy["cash"]
                g[4] += int(other_sell["units"] > 0)
    (OUT / "wheat_cycles.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in cycles))
    out = {f"{side}:{direction}": {"steps": v[0], "sell_filled": v[1],
             "buy_filled": v[2], "net_cash": v[3], "concurrent_other_wheat_sell_steps": v[4]}
           for (side, direction), v in summary.items()}
    (OUT / "wheat_cycle_summary.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
