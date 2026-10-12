import collections
import hashlib
import json
import math
import random
from pathlib import Path


HERE = Path(__file__).resolve().parent
CANDIDATES = ("v111", "v169", "v074")
BOOTSTRAP_SEED = 23023
BOOTSTRAP_DRAWS = 2000


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson_lower(point, n, z):
    denominator = 1 + z * z / n
    center = point + z * z / (2 * n)
    half = z * math.sqrt(point * (1 - point) / n + z * z / (4 * n * n))
    return (center - half) / denominator


def bootstrap_lower(values, seed):
    rng = random.Random(seed)
    n = len(values)
    means = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(BOOTSTRAP_DRAWS))
    return means[int(0.025 * BOOTSTRAP_DRAWS)]


def is_invalid(row):
    return (
        row["err"] is not None
        or row["statuses"] != ["DONE", "DONE"]
        or row["score"] is None
        or bool(row.get("agent_errors"))
        or row.get("action_count") != 719
    )


manifest = json.loads((HERE / "stage3-manifest.json").read_text())
jobs = json.loads((HERE / "jobs-stage3.json").read_text())
expected = {f"{job[0]}|{job[2]}|{job[4]}|{job[5]}" for job in jobs}
rows = [json.loads(line) for line in (HERE / "games-stage3.jsonl").read_text().splitlines() if line.strip()]
by_key = collections.defaultdict(list)
for row in rows:
    by_key[row["key"]].append(row)
assert set(by_key) == expected, {"missing": len(expected - set(by_key)), "extra": len(set(by_key) - expected)}
assert all(len(group) == 1 for group in by_key.values()), "duplicate result keys"
rows = [group[0] for group in by_key.values()]


def panel_map(vid, opponent):
    return {(row["seed"], row["seat"]): row for row in rows if row["vid"] == vid and row["opponent"] == opponent}


def paired_seed_deltas(vid, opponent, seeds):
    candidate = panel_map(vid, opponent)
    parent = panel_map("P", opponent)
    assert len(candidate) == len(parent) == len(seeds) * 2
    return [
        sum(candidate[(seed, seat)]["score"] - parent[(seed, seat)]["score"] for seat in (0, 1)) / 2
        for seed in seeds
    ]


guard_ids = [item["id"] for item in manifest["guard"]]
# Parent has exactly one row per hosted panel; derive the IDs directly to preserve all 121 rows.
hosted_ids = sorted({row["opponent"] for row in rows if row["vid"] == "P" and row["opponent"].startswith("H")})
assert len(hosted_ids) == 121

results = []
for candidate_index, vid in enumerate(CANDIDATES):
    a = list(panel_map(vid, "A-O2").values())
    assert len(a) == 400
    a_scores = [row["score"] for row in a]
    a_point = sum(a_scores) / len(a_scores)
    a_lower = wilson_lower(a_point, len(a_scores), 2.576)
    counts = collections.Counter(a_scores)

    a_prime_deltas = paired_seed_deltas(vid, "AP-O1", range(8200, 8400))
    a_prime_point = sum(a_prime_deltas) / len(a_prime_deltas)
    a_prime_lower = bootstrap_lower(a_prime_deltas, BOOTSTRAP_SEED + candidate_index)

    b_deltas = paired_seed_deltas(vid, "B-DP", range(8400, 8500))
    b_point = sum(b_deltas) / len(b_deltas)
    b_lower = bootstrap_lower(b_deltas, BOOTSTRAP_SEED + 10 + candidate_index)

    guard_deltas = {}
    pooled = list(b_deltas)
    for opponent_index, opponent in enumerate(guard_ids):
        deltas = paired_seed_deltas(vid, opponent, range(8500, 8510))
        guard_deltas[opponent] = sum(deltas) / len(deltas)
        pooled.extend(deltas)
    c_bad = sorted(opponent for opponent, delta in guard_deltas.items() if delta < -0.10)
    d_point = sum(pooled) / len(pooled)
    d_lower = bootstrap_lower(pooled, BOOTSTRAP_SEED + 100 + candidate_index)

    h_deltas = []
    for opponent in hosted_ids:
        candidate = [row for row in rows if row["vid"] == vid and row["opponent"] == opponent]
        parent = [row for row in rows if row["vid"] == "P" and row["opponent"] == opponent]
        assert len(candidate) == len(parent) == 1
        h_deltas.append(candidate[0]["score"] - parent[0]["score"])
    h_point = sum(h_deltas) / len(h_deltas)
    h_lower = bootstrap_lower(h_deltas, BOOTSTRAP_SEED + 200 + candidate_index)

    candidate_rows = [row for row in rows if row["vid"] == vid]
    invalid = sum(is_invalid(row) for row in candidate_rows)
    max_step = max(row["max_step"] for row in candidate_rows)
    gates = {
        "A": a_lower > 0.55,
        "A_prime": a_prime_lower > -0.03,
        "B": b_lower > -0.05,
        "C": not c_bad,
        "D": d_lower > -0.03,
        "H": h_lower > -0.03,
        "E": invalid == 0 and max_step < 0.5,
    }
    results.append({
        "vid": vid,
        "A": {"n": 400, "W": counts[1.0], "D": counts[0.5], "L": counts[0.0], "score": a_point, "wilson99_lower": a_lower, "pass": gates["A"]},
        "A_prime": {"paired_games": 400, "seed_clusters": 200, "delta": a_prime_point, "bootstrap95_lower": a_prime_lower, "pass": gates["A_prime"]},
        "B": {"paired_games": 200, "seed_clusters": 100, "delta": b_point, "bootstrap95_lower": b_lower, "pass": gates["B"]},
        "C": {"files": 19, "deltas": guard_deltas, "bad_files": c_bad, "pass": gates["C"]},
        "D": {"paired_games": 580, "opponent_seed_clusters": 290, "delta": d_point, "bootstrap95_lower": d_lower, "pass": gates["D"]},
        "H": {"paired_episodes": 121, "delta": h_point, "bootstrap95_lower": h_lower, "pass": gates["H"]},
        "E": {"games": len(candidate_rows), "invalid": invalid, "max_step": max_step, "pass": gates["E"]},
        "passed": all(gates.values()),
    })

passed = [row for row in results if row["passed"]]
passed.sort(key=lambda row: (row["A"]["wilson99_lower"], row["D"]["delta"]), reverse=True)
summary = {
    "verdict": "SUCCESS" if passed else "FAIL",
    "selected": passed[0]["vid"] if passed else None,
    "bootstrap": {"draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED, "unit": "paired seed with both seats averaged; H uses hosted panel row"},
    "jobs_sha256": sha256(HERE / "jobs-stage3.json"),
    "games_sha256": sha256(HERE / "games-stage3.jsonl"),
    "results": results,
}
(HERE / "stage3-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
