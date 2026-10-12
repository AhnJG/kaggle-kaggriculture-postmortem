import collections
import hashlib
import json
import math
import random
from pathlib import Path


HERE = Path(__file__).resolve().parent
CANDIDATES = ("v171", "v173", "v111", "v074")
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


jobs = json.loads((HERE / "jobs-stage3.json").read_text())
expected = {f"{job[0]}|{job[3]}|{job[4]}" for job in jobs}
rows = [json.loads(line) for line in (HERE / "games-stage3.jsonl").read_text().splitlines() if line.strip()]
by_key = collections.defaultdict(list)
for row in rows:
    by_key[row["key"]].append(row)
assert set(by_key) == expected, (len(set(by_key) - expected), len(expected - set(by_key)))
assert all(len(group) == 1 for group in by_key.values())
rows = [group[0] for group in by_key.values()]


def panel_rows(vid, panel):
    prefix = f"{vid}@{panel}"
    return [row for row in rows if row["vid"] == prefix]


def invalid(row):
    return row["err"] is not None or row["statuses"] != ["DONE", "DONE"] or row["score"] is None


results = []
for candidate_index, vid in enumerate(CANDIDATES):
    a = panel_rows(vid, "A")
    assert len(a) == 400
    a_scores = [row["score"] for row in a]
    a_point = sum(a_scores) / len(a_scores)
    a_lo = wilson_lower(a_point, len(a_scores), 2.576)
    counts = collections.Counter(a_scores)

    dp_candidate = {(row["seed"], row["seat"]): row for row in panel_rows(vid, "DP")}
    dp_parent = {(row["seed"], row["seat"]): row for row in panel_rows("P", "DP")}
    assert len(dp_candidate) == len(dp_parent) == 200
    dp_seed_delta = [
        sum(dp_candidate[(seed, seat)]["score"] - dp_parent[(seed, seat)]["score"] for seat in (0, 1)) / 2
        for seed in range(7400, 7500)
    ]
    b_point = sum(dp_seed_delta) / len(dp_seed_delta)
    b_lo = bootstrap_lower(dp_seed_delta, BOOTSTRAP_SEED + candidate_index)

    public_deltas = {}
    pooled_clusters = list(dp_seed_delta)
    for opponent_index in range(14):
        panel = f"PUB{opponent_index:02d}"
        candidate_rows = {(row["seed"], row["seat"]): row for row in panel_rows(vid, panel)}
        parent_rows = {(row["seed"], row["seat"]): row for row in panel_rows("P", panel)}
        assert len(candidate_rows) == len(parent_rows) == 20
        deltas = [candidate_rows[key]["score"] - parent_rows[key]["score"] for key in candidate_rows]
        public_deltas[panel] = sum(deltas) / len(deltas)
        for seed in range(7500, 7510):
            pooled_clusters.append(sum(candidate_rows[(seed, seat)]["score"] - parent_rows[(seed, seat)]["score"] for seat in (0, 1)) / 2)
    c_bad = sorted(panel for panel, delta in public_deltas.items() if delta < -0.10)
    d_point = sum(pooled_clusters) / len(pooled_clusters)
    d_lo = bootstrap_lower(pooled_clusters, BOOTSTRAP_SEED + 100 + candidate_index)

    candidate_rows = [row for row in rows if row["vid"].startswith(f"{vid}@")]
    e_invalid = sum(invalid(row) for row in candidate_rows)
    e_max_step = max(row["max_step"] for row in candidate_rows)
    gates = {
        "A": a_lo > 0.55,
        "B": b_lo > -0.05,
        "C": not c_bad,
        "D": d_lo > -0.03,
        "E": e_invalid == 0 and e_max_step < 0.5,
    }
    results.append({
        "vid": vid,
        "A": {"n": 400, "W": counts[1.0], "D": counts[0.5], "L": counts[0.0], "score": a_point, "wilson99_lower": a_lo, "pass": gates["A"]},
        "B": {"paired_games": 200, "seed_clusters": 100, "delta": b_point, "bootstrap95_lower": b_lo, "pass": gates["B"]},
        "C": {"files": 14, "deltas": public_deltas, "bad_files": c_bad, "pass": gates["C"]},
        "D": {"paired_games": 480, "opponent_seed_clusters": 240, "delta": d_point, "bootstrap95_lower": d_lo, "pass": gates["D"]},
        "E": {"games": len(candidate_rows), "invalid": e_invalid, "max_step": e_max_step, "pass": gates["E"]},
        "passed": all(gates.values()),
    })

passed = [row for row in results if row["passed"]]
passed.sort(key=lambda row: (row["A"]["wilson99_lower"], row["D"]["delta"]), reverse=True)
summary = {
    "verdict": "SUCCESS" if passed else "FAIL",
    "selected": passed[0]["vid"] if passed else None,
    "bootstrap": {"draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED, "unit": "opponent x seed, both seats averaged"},
    "jobs_sha256": sha256(HERE / "jobs-stage3.json"),
    "games_sha256": sha256(HERE / "games-stage3.jsonl"),
    "results": results,
}
(HERE / "stage3-summary.json").write_text(json.dumps(summary, indent=1) + "\n")
print(json.dumps(summary, indent=1))
