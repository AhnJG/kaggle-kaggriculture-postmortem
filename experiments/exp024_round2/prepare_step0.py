import hashlib
import json
from pathlib import Path

import kaggle_environments


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / "releases/mirror-screen-v171/main.py"
O1 = ROOT / "releases/public-newmeta-127ed3e6-exact/main.py"
PROPOSAL = ROOT / "coordination/proposals/claude/20260926-EXP024-ROUND2-CODEX.md"
ENGINE = Path(kaggle_environments.__file__).resolve().parent / "envs/kaggriculture/kaggriculture.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert kaggle_environments.__version__ == "1.32.7"
assert sha(PARENT) == "496460f81869ebbd1bf80f3dd3c9440ef72c41819a831ee39a16f180d7c0bd5d"
assert sha(O1) == "127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652"
assert sha(ENGINE) == "bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e"

jobs = []
for opponent_id, opponent_path in (("O1-127ed3e6", O1), ("O2-v171", PARENT)):
    for seed in range(8000, 8005):
        for seat in (0, 1):
            jobs.append(["P", str(PARENT), opponent_id, str(opponent_path), seed, seat])

jobs_path = HERE / "jobs-step0.json"
jobs_path.write_text(json.dumps(jobs, indent=1) + "\n")
freeze = {
    "approved": "human 09-26",
    "workers": 5,
    "submission": "forbidden",
    "proposal": {"path": str(PROPOSAL.relative_to(ROOT)), "sha256": sha(PROPOSAL)},
    "parent": {"path": str(PARENT.relative_to(ROOT)), "sha256": sha(PARENT)},
    "o1": {"path": str(O1.relative_to(ROOT)), "sha256": sha(O1)},
    "o2": {"path": str(PARENT.relative_to(ROOT)), "sha256": sha(PARENT)},
    "engine": {"version": kaggle_environments.__version__, "path": str(ENGINE), "sha256": sha(ENGINE)},
    "variants": {"path": "experiments/exp024_round2/variants.json", "sha256": sha(HERE / "variants.json")},
    "jobs_step0": {"path": "experiments/exp024_round2/jobs-step0.json", "sha256": sha(jobs_path)},
}
(HERE / "freeze.json").write_text(json.dumps(freeze, indent=2) + "\n")
print(json.dumps(freeze, indent=2))
