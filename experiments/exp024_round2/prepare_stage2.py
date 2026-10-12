import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
O1 = ROOT / "releases/public-newmeta-127ed3e6-exact/main.py"
O2 = ROOT / "releases/mirror-screen-v171/main.py"
variants_path = HERE / "variants.json"
variants = {item["id"]: item for item in json.loads(variants_path.read_text())}
screen_path = HERE / "screen-summary.json"
screen = json.loads(screen_path.read_text())
advance = screen["advance"]
assert 0 < len(advance) <= 8


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


agents = [("P", O2)] + [(vid, ROOT / variants[vid]["path"]) for vid in advance]
jobs = []
for vid, agent in agents:
    if vid != "P":
        assert sha(agent) == variants[vid]["sha256"]
    for opponent_id, opponent_path in (("O1-127ed3e6", O1), ("O2-v171", O2)):
        for seed in range(8100, 8130):
            for seat in (0, 1):
                jobs.append([vid, str(agent), opponent_id, str(opponent_path), seed, seat])

jobs_path = HERE / "jobs-stage2.json"
jobs_path.write_text(json.dumps(jobs, indent=1) + "\n")
manifest = {
    "candidates": advance,
    "includes_parent_baseline": True,
    "jobs": len(jobs),
    "workers": 5,
    "seeds": [8100, 8129],
    "seats": [0, 1],
    "opponents": ["O1-127ed3e6", "O2-v171"],
    "variants_sha256": sha(variants_path),
    "screen_summary_sha256": sha(screen_path),
    "jobs_sha256": sha(jobs_path),
}
(HERE / "stage2-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
