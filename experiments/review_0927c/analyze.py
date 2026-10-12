"""Read-only recomputation for REVIEW-0927C; writes only its own JSON."""

import csv
import gzip
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "analysis/v074_hosted_20260927/opponents.csv"
RAW = ROOT / "private_artifacts/v074_hosted_20260927/raw"
OUT = ROOT / "experiments/review_0927c/analysis.json"


def score(rows):
    counts = Counter(row["result"] for row in rows)
    return {
        "n": len(rows),
        "W": counts["W"],
        "D": counts["D"],
        "L": counts["L"],
        "score": (counts["W"] + 0.5 * counts["D"]) / len(rows) if rows else None,
    }


rows = [row for row in csv.DictReader(CSV.open()) if row["submission_label"] == "v074"]
families = {
    "127_variant": lambda row: "127ed3e6" in row["label"] and row["is_full"] == "False",
    "127_exact": lambda row: "127ed3e6" in row["label"] and row["is_full"] == "True",
    "55be": lambda row: "55be5d5f" in row["label"],
    "DP": lambda row: row["label"].startswith("DP-0924"),
    "UNKNOWN": lambda row: row["label"].startswith("UNKNOWN"),
}
family_stats = {name: score([row for row in rows if predicate(row)]) for name, predicate in families.items()}
band = [row for row in rows if 2200 <= float(row["op_lb_score"]) < 2400]
band_stats = {name: score([row for row in band if predicate(row)]) for name, predicate in families.items()}

prefix_buckets = defaultdict(list)
for row in rows:
    if not families["127_variant"](row):
        continue
    prefix = int(row["prefix_len"])
    bucket = "0-99" if prefix < 100 else "100-199" if prefix < 200 else "200-399" if prefix < 400 else "400-719"
    prefix_buckets[bucket].append(row)

checkpoints = [96, 144, 288, 432, 576, 648, 672, 696, 712, 719]
cash_gaps = defaultdict(lambda: defaultdict(list))
sell_requests = defaultdict(Counter)
for row in rows:
    if not families["127_variant"](row):
        continue
    replay = json.load(gzip.open(RAW / f"{row['episode']}.json.gz", "rt"))
    seat = int(row["seat"])
    opponent = 1 - seat
    outcome = row["result"]
    for step in checkpoints:
        observation = replay["steps"][step][seat]["observation"]
        gap = observation["farms"][seat]["money"] - observation["farms"][opponent]["money"]
        cash_gaps[outcome][str(step)].append(gap)
    if outcome == "L":
        for step in replay["steps"][1:]:
            for who, sign in ((seat, -1), (opponent, 1)):
                for order in (step[who].get("action") or {}).get("market", []):
                    if len(order) >= 3 and order[0] == "SELL":
                        sell_requests["opponent_minus_ours"][order[1]] += sign * int(order[2])

cash_summary = {
    outcome: {
        step: {
            "n": len(values),
            "median": statistics.median(values),
            "mean": sum(values) / len(values),
        }
        for step, values in by_step.items()
    }
    for outcome, by_step in cash_gaps.items()
}

scenarios = {
    "legacy": (0.60, 0.10, 0.30),
    "transition": (0.40, 0.30, 0.30),
    "clone": (0.20, 0.60, 0.20),
    "diverse": (0.25, 0.25, 0.50),
}
panel = {
    "P": (0.88, 0.04, 0.9891304347826086),
    "d157": (0.86, 0.85, 0.8456521739130435),
}
scenario_scores = {}
for name, weights in scenarios.items():
    totals = {bot: sum(weight * value for weight, value in zip(weights, values)) for bot, values in panel.items()}
    scenario_scores[name] = {**totals, "botwise_max": max(totals.values())}

specialist_rows = [json.loads(line) for line in (ROOT / "experiments/exp032_specialist/games.jsonl").open()]
specialist_scores = {
    (row["vid"], row["opponent"], row["seed"], row["seat"]): row["score"] for row in specialist_rows
}
shared_keys = sorted(
    (row["opponent"], row["seed"], row["seat"])
    for row in specialist_rows
    if row["vid"] == "d157" and ("d053", row["opponent"], row["seed"], row["seat"]) in specialist_scores
)
d157_scores = [specialist_scores[("d157", *key)] for key in shared_keys]
d053_scores = [specialist_scores[("d053", *key)] for key in shared_keys]
d157_mean = sum(d157_scores) / len(d157_scores)
d053_mean = sum(d053_scores) / len(d053_scores)
correlation = sum((a - d157_mean) * (b - d053_mean) for a, b in zip(d157_scores, d053_scores)) / (
    sum((a - d157_mean) ** 2 for a in d157_scores) * sum((b - d053_mean) ** 2 for b in d053_scores)
) ** 0.5
same_family_correlation = {
    "n": len(shared_keys),
    "same_outcome": sum(a == b for a, b in zip(d157_scores, d053_scores)),
    "same_outcome_rate": sum(a == b for a, b in zip(d157_scores, d053_scores)) / len(shared_keys),
    "pearson_score_correlation": correlation,
}


def bootstrap_lower(values, seed, draws=2000):
    generator = random.Random(seed)
    size = len(values)
    samples = sorted(sum(values[generator.randrange(size)] for _ in values) / size for _ in range(draws))
    return samples[int(0.025 * draws)]


final_rows = {}
for line in (ROOT / "experiments/exp030_dpnew_bypass/games-final.jsonl").open():
    row = json.loads(line)
    final_rows[row["key"]] = row
final_jobs = json.load((ROOT / "experiments/exp030_dpnew_bypass/jobs-final.json").open())
expected_keys = {f"{job[0]}|{job[2]}|{job[4]}|{job[5]}" for job in final_jobs}
assert set(final_rows) == expected_keys
matrix = defaultdict(dict)
for row in final_rows.values():
    matrix[(row["vid"], row["opponent"])][(row["seed"], row["seat"])] = row


def paired_differences(candidate, opponent, base="D"):
    candidate_rows = matrix[(candidate, opponent)]
    base_rows = matrix[(base, opponent)]
    seeds = sorted({seed for seed, _ in base_rows})
    return [sum(candidate_rows[(seed, seat)]["score"] - base_rows[(seed, seat)]["score"] for seat in (0, 1)) / 2 for seed in seeds]


opponents = sorted({opponent for _, opponent in matrix})
guards = [opponent for opponent in opponents if opponent not in ("V074", "O127") and not opponent.startswith("H")]
hosted = sorted(opponent for opponent in opponents if opponent.startswith("H"))
candidate = "b020"
candidate_games = [row for (vid, _), group in matrix.items() if vid == candidate for row in group.values()]
invalid = sum(
    row["err"] is not None
    or row["statuses"] != ["DONE", "DONE"]
    or row["score"] is None
    or bool(row.get("agent_errors"))
    or row.get("action_count") != 719
    for row in candidate_games
)
v074_delta = paired_differences(candidate, "V074")
o127_delta = paired_differences(candidate, "O127")
guard_delta = []
per_guard = {}
for opponent in guards:
    values = paired_differences(candidate, opponent)
    guard_delta.extend(values)
    per_guard[opponent] = sum(values) / len(values)
hosted_delta = [
    list(matrix[(candidate, opponent)].values())[0]["score"] - list(matrix[("P", opponent)].values())[0]["score"]
    for opponent in hosted
]
b020_final = {
    "complete_rows": len(final_rows),
    "invalid": invalid,
    "max_step": max(row["max_step"] for row in candidate_games),
    "v074": [sum(v074_delta) / len(v074_delta), bootstrap_lower(v074_delta, 30001)],
    "o127": [sum(o127_delta) / len(o127_delta), bootstrap_lower(o127_delta, 30101)],
    "guard": [sum(guard_delta) / len(guard_delta), bootstrap_lower(guard_delta, 30201)],
    "worst_file": min(per_guard.items(), key=lambda item: item[1]),
    "hosted_vs_v074": [sum(hosted_delta) / len(hosted_delta), bootstrap_lower(hosted_delta, 30301)],
}
b020_final["pass"] = (
    b020_final["invalid"] == 0
    and b020_final["max_step"] < 0.8
    and b020_final["v074"][1] > -0.03
    and b020_final["o127"][1] > -0.03
    and b020_final["guard"][0] > 0
    and b020_final["guard"][1] >= 0
    and b020_final["worst_file"][1] >= -0.10
    and b020_final["hosted_vs_v074"][0] >= 0
    and b020_final["hosted_vs_v074"][1] > -0.03
)

output = {
    "v074_total": score(rows),
    "family_stats": family_stats,
    "band_2200_2400": {"total": score(band), **band_stats},
    "127_variant_prefix_buckets": {bucket: score(group) for bucket, group in sorted(prefix_buckets.items())},
    "127_variant_cash_gap_ours_minus_opponent": cash_summary,
    "127_variant_loss_requested_sell_units_opponent_minus_ours": sell_requests["opponent_minus_ours"],
    "scenario_botwise_scores_from_exp032_panels": scenario_scores,
    "exp032_d157_d053_same_family_correlation": same_family_correlation,
    "exp030_b020_frozen_final_recompute": b020_final,
}
OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
print(json.dumps(output, indent=2, sort_keys=True))
