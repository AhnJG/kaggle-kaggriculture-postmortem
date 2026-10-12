import json
from pathlib import Path


here = Path(__file__).resolve().parent
candidate = str((here.parents[1] / "releases/mirror-screen-v171/main.py").resolve())
opponent = str((here.parents[1] / "releases/public-newmeta-127ed3e6-exact/main.py").resolve())
jobs = [
    ["v171@E5", candidate, opponent, seed, seat]
    for seed in range(2300, 2310)
    for seat in (0, 1)
]
assert len(jobs) == 20
(here / "jobs-stage3-e5.json").write_text(json.dumps(jobs, indent=1) + "\n")
