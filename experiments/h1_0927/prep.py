import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


prereg = json.loads((HERE / "prereg.json").read_text())
for item in [prereg["parent"], *prereg["opponents"].values()]:
    path = ROOT / item["path"]
    assert sha(path) == item["sha256"], (path, sha(path), item["sha256"])

parent = ROOT / prereg["parent"]["path"]
variant = ROOT / prereg["variant_path"]
parent_bytes = parent.read_bytes()
assert variant.read_bytes().startswith(parent_bytes)
assert len(variant.read_bytes()) > len(parent_bytes)

jobs = []
for opponent_id in ("O127", "PUB01", "PUB12", "D"):
    seeds = prereg["seeds"] if opponent_id in ("O127", "D") else prereg["seeds"][:3]
    opponent_path = prereg["opponents"][opponent_id]["path"]
    for arm, agent_path in (("H1", prereg["variant_path"]), ("P", prereg["parent"]["path"])):
        for seed in seeds:
            for seat in prereg["seats"]:
                jobs.append([arm, agent_path, opponent_id, opponent_path, seed, seat])

(HERE / "jobs.json").write_text(json.dumps(jobs, indent=2) + "\n")
(HERE / "manifest.json").write_text(json.dumps({
    "prereg_sha256": sha(HERE / "prereg.json"),
    "parent_sha256": sha(parent),
    "variant_sha256": sha(variant),
    "parent_prefix_bytes": len(parent_bytes),
    "parent_prefix_exact": True,
    "jobs": len(jobs),
    "candidate_games": len(jobs) // 2,
    "parent_matched_games": len(jobs) // 2,
    "worker_count": 1,
}, indent=2) + "\n")

