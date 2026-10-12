"""Read-only exact-flow check on the existing parity-verified survey prefix.

The prefix is chronologically selected, so these estimates are supplementary.
No game, bot, or engine code is executed here.
"""
import csv
import json
import statistics as stats
import zipfile

FEAT = "analysis/survey300_20260929/feat300.jsonl"
LB = "analysis/survey300_20260929/kaggriculture.zip"
OUT = "experiments/fp_survey300/flows.json"
ITEMS = ("TOMATO", "STRAWBERRY", "CARROT", "WHEAT", "MELON",
         "MILK", "WOOL", "EGG", "FERTILIZER")


def value(seat, key, index):
    return seat["flows"].get(key, [0, 0])[index]


def main():
    with zipfile.ZipFile(LB) as archive:
        teams = list(csv.DictReader(archive.read(archive.namelist()[0]).decode("utf-8-sig").splitlines()))
    ranks = {team["TeamName"]: int(team["Rank"]) for team in teams}
    rows = [json.loads(line) for line in open(FEAT, encoding="utf-8")]
    assert all("error" not in row and row["parity"] for row in rows)
    records = []
    for row in rows:
        rank = [ranks.get(name) for name in row["teams"]]
        groups = ["top" if r is not None and r <= 300 else
                  "band" if r is not None and 600 <= r <= 1300 else "other" for r in rank]
        if sorted(groups) == ["band", "top"]:
            top = groups.index("top")
            records.append((row["seat"][str(top)], row["seat"][str(1 - top)]))

    result = {"prefix_rows": len(rows), "direct_games": len(records), "items": {}}
    for item in ITEMS:
        measures = {}
        for kind in ("SELL", "BUY_PRODUCT", "BUY_SEED"):
            key = f"{kind}|{item}"
            for index, label in ((0, "units"), (1, "coins")):
                a = [value(top, key, index) for top, _ in records]
                b = [value(band, key, index) for _, band in records]
                measures[f"{kind}_{label}"] = {
                    "top_mean": stats.mean(a), "band_mean": stats.mean(b),
                    "direct_mean_delta": stats.mean(x - y for x, y in zip(a, b)),
                    "direct_median_delta": stats.median(x - y for x, y in zip(a, b)),
                }
        net = lambda seat: value(seat, f"SELL|{item}", 1) - value(seat, f"BUY_PRODUCT|{item}", 1) - value(seat, f"BUY_SEED|{item}", 1)
        diff = [net(top) - net(band) for top, band in records]
        measures["net_sell_less_product_seed"] = {"direct_mean_delta": stats.mean(diff),
                                                 "direct_median_delta": stats.median(diff)}
        result["items"][item] = measures
    hire = [value(top, "HIRE|-", 1) - value(band, "HIRE|-", 1) for top, band in records]
    result["hire_cost"] = {"direct_mean_delta": stats.mean(hire),
                           "direct_median_delta": stats.median(hire)}
    with open(OUT, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({"prefix_rows": result["prefix_rows"], "direct_games": len(records),
                      "hire_cost": result["hire_cost"]}))
    for item in ("TOMATO", "STRAWBERRY", "WHEAT", "EGG"):
        print(item, json.dumps(result["items"][item]))


if __name__ == "__main__":
    main()
