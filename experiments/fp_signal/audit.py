"""Audit fixed public-observation features against private-variant W/L."""
import collections
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
cohort = json.loads((HERE / "cohort.json").read_text())
STEPS = (240, 384, 480, 576, 624)
NAMES = ("opp_money_ahead", "opp_cow_sheep_ahead", "opp_straw_tomato_ahead",
         "wool_inv_gt_10000", "milk_inv_gt_10000", "straw_inv_gt_10000")


def tile_count(farm, field, values):
    return sum(tile.get(field) in values for row in farm["tiles"]
               for tile in row if isinstance(tile, dict))


def public_features(obs, seat):
    own, opp = obs["farms"][seat], obs["farms"][1 - seat]
    inventory = obs["market"]["inventory"]
    return {
        "opp_money_ahead": float(opp["money"]) > float(own["money"]),
        "opp_cow_sheep_ahead": tile_count(opp, "animal", {"COW", "SHEEP"}) > tile_count(own, "animal", {"COW", "SHEEP"}),
        "opp_straw_tomato_ahead": tile_count(opp, "crop", {"STRAWBERRY", "TOMATO"}) > tile_count(own, "crop", {"STRAWBERRY", "TOMATO"}),
        "wool_inv_gt_10000": int(inventory["WOOL"]) > 10000,
        "milk_inv_gt_10000": int(inventory["MILK"]) > 10000,
        "straw_inv_gt_10000": int(inventory["STRAWBERRY"]) > 10000,
    }


def fisher_two_sided(a, b, c, d):
    # a=L, feature true; b=W, feature true; c=L, false; d=W, false.
    n = a + b + c + d
    true_total, loss_total = a + b, a + c
    lo, hi = max(0, true_total - (n - loss_total)), min(true_total, loss_total)
    den = math.comb(n, true_total)
    def prob(x):
        return math.comb(loss_total, x) * math.comb(n - loss_total, true_total - x) / den
    observed = prob(a)
    return min(1.0, sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= observed + 1e-12))


def table(rows, name, step):
    t = collections.Counter((r["result"], r["features"][str(step)][name]) for r in rows)
    a, b, c, d = (t["L", True], t["W", True], t["L", False], t["W", False])
    rate_true = a / (a + b) if a + b else None
    rate_false = c / (c + d) if c + d else None
    return {"L_true": a, "W_true": b, "L_false": c, "W_false": d,
            "loss_rate_true": rate_true, "loss_rate_false": rate_false,
            "risk_difference": rate_true - rate_false if rate_true is not None and rate_false is not None else None,
            "fisher_two_sided": fisher_two_sided(a, b, c, d)}


data = []
for item in cohort["rows"]:
    path = ROOT / f"private_artifacts/c26_hosted_20260929/raw/{item['episode']}.json.gz"
    raw = json.load(gzip.open(path))
    seat = int(item["seat"])
    assert len(raw["steps"]) == 720
    feats = {}
    for step in STEPS:
        own_obs = raw["steps"][step][seat]["observation"]
        shared_obs = raw["steps"][step][0]["observation"]
        obs = {key: own_obs.get(key, shared_obs[key]) for key in ("farms", "market", "town", "step")}
        assert int(obs["step"]) == step
        feats[str(step)] = public_features(obs, seat)
        assert set(feats[str(step)]) == set(NAMES)
    data.append({"episode": item["episode"], "op_submissionId": item["op_submissionId"],
                 "result": item["result"], "features": feats})

half = len(data) // 2
checks = []
for step in STEPS:
    for name in NAMES:
        early = table(data[:half], name, step)
        late = table(data[half:], name, step)
        pooled = table(data, name, step)
        eligible = all(min(t[k] for k in ("L_true", "W_true", "L_false", "W_false")) >= 3
                       for t in (early, late))
        diff = (eligible and early["risk_difference"] is not None and late["risk_difference"] is not None
                and early["risk_difference"] * late["risk_difference"] > 0
                and abs(early["risk_difference"]) >= 0.20 and abs(late["risk_difference"]) >= 0.20)
        passed = bool(diff and pooled["fisher_two_sided"] < 0.01)
        checks.append({"step": step, "feature": name, "early": early, "late": late,
                       "pooled": pooled, "eligible": eligible, "pass": passed})

result = {
    "plan_sha256": hashlib.sha256((HERE / "PLAN.md").read_bytes()).hexdigest(),
    "cohort_sha256": hashlib.sha256((HERE / "cohort.json").read_bytes()).hexdigest(),
    "n": len(data), "half_n": [half, len(data) - half],
    "wdl": dict(collections.Counter(r["result"] for r in data)),
    "opponent_submissions": len(set(r["op_submissionId"] for r in data)),
    "checks": checks,
    "verdict": "REPEATED_SIGNAL" if any(c["pass"] for c in checks) else "NO_REPEATED_SIGNAL",
}
(HERE / "features.json").write_text(json.dumps(data, indent=2) + "\n")
(HERE / "verdict.json").write_text(json.dumps(result, indent=2) + "\n")
print("n", len(data), "WDL", result["wdl"], "submissions", result["opponent_submissions"])
print("eligible", sum(x["eligible"] for x in checks), "passing", sum(x["pass"] for x in checks), result["verdict"])
for x in checks:
    if x["eligible"] or x["pooled"]["fisher_two_sided"] < 0.05:
        print(x["step"], x["feature"], "early", x["early"]["risk_difference"],
              "late", x["late"]["risk_difference"], "p", x["pooled"]["fisher_two_sided"],
              "pass", x["pass"])
