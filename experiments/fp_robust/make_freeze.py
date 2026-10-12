"""One-time FIRSTPRINCIPLES panel freeze. Never rerun after candidate results."""
import collections
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SRC = ROOT / "experiments/exp051_curpop"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


meta = json.loads((SRC / "meta.json").read_text())
groups = collections.defaultdict(list)
for row in meta:
    assert not 9000 <= int(row["seed"]) <= 9599
    groups[row["sub"]].append(row)
assert {k: len(v) for k, v in groups.items()} == {"d157": 187, "c26": 82}
holdout = []
for sub, rows in sorted(groups.items()):
    ordered = sorted(rows, key=lambda r: int(r["episode"]))
    holdout += [r["episode"] for r in ordered[-math.ceil(0.2 * len(rows)):]]
holdout = sorted(holdout, key=int)
assert len(holdout) == 55
payload = {
    "frozen_at_kst": "2026-09-29 08:43",
    "method": "Latest ceil(20%) episode IDs separately for d157 and c26; no candidate results inspected",
    "forward_holdout_after_utc": "2026-09-28T17:27:00Z",
    "source_sha256": {p.name: digest(p) for p in (SRC / "meta.json", SRC / "jobs.json", SRC / "games.jsonl")},
    "plan_sha256": digest(OUT / "PLAN.md"),
    "holdout_episodes": holdout,
    "closed_loop_seeds": list(range(6001, 6009)),
    "bootstrap_seed": 290929,
}
path = OUT / "freeze.json"
assert not path.exists(), "freeze is immutable"
path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
print("freeze", digest(path), "holdout", len(holdout), "development", len(meta) - len(holdout))
