import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
O1 = ROOT / "releases/public-newmeta-127ed3e6-exact/main.py"
O2 = ROOT / "releases/mirror-screen-v171/main.py"
variants_path = HERE / "variants.json"
variants = json.loads(variants_path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert len(variants) == 186
assert sha(variants_path) == "61ef032436fa20bc2e2938bac552ea7efec66d8eb8ea4fbc3405e24dc277f8a1"

jobs = []
for variant in variants:
    path = ROOT / variant["path"]
    assert sha(path) == variant["sha256"]
    for opponent_id, opponent_path in (("O1-127ed3e6", O1), ("O2-v171", O2)):
        for seed in range(8000, 8005):
            for seat in (0, 1):
                jobs.append([variant["id"], str(path), opponent_id, str(opponent_path), seed, seat])

jobs_path = HERE / "jobs-screen.json"
jobs_path.write_text(json.dumps(jobs, indent=1) + "\n")
manifest = {
    "jobs": len(jobs),
    "workers": 5,
    "seeds": [8000, 8004],
    "seats": [0, 1],
    "opponents": ["O1-127ed3e6", "O2-v171"],
    "variants_sha256": sha(variants_path),
    "jobs_sha256": sha(jobs_path),
    "step0_summary_sha256": sha(HERE / "step0-summary.json"),
}
(HERE / "screen-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
