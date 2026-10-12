import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CANDIDATES = ("v171", "v173", "v111", "v074")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((HERE / "stage3-opponents.json").read_text())
variants = {row["id"]: row for row in json.loads((HERE / "variants.json").read_text())}

for vid in CANDIDATES:
    path = HERE / variants[vid]["path"]
    assert sha256(path) == variants[vid]["sha256"], (vid, "variant sha mismatch")

parent = HERE / "parent.py"
opp127 = ROOT / "releases/public-newmeta-127ed3e6-exact/main.py"
assert sha256(parent) == "e496a4fe550d26533caa0c284c2915c680e8d339624a1b811165cc74f4c5235b"
assert sha256(opp127) == "127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652"

dp = ROOT / manifest["dp"]["path"]
assert sha256(dp) == manifest["dp"]["sha256"]
public = []
for index, item in enumerate(manifest["public_top15"][1:]):
    path = ROOT / item["path"]
    assert sha256(path) == item["sha256"], (index, item["path"], "opponent sha mismatch")
    public.append(path)
assert len(public) == 14

jobs = []
for vid in CANDIDATES:
    for seed in range(7200, 7400):
        for seat in (0, 1):
            jobs.append([f"{vid}@A", variants[vid]["path"], str(opp127), seed, seat])

for vid in (*CANDIDATES, "P"):
    agent = "parent.py" if vid == "P" else variants[vid]["path"]
    for seed in range(7400, 7500):
        for seat in (0, 1):
            jobs.append([f"{vid}@DP", agent, str(dp), seed, seat])

for opponent_index, opponent in enumerate(public):
    for vid in (*CANDIDATES, "P"):
        agent = "parent.py" if vid == "P" else variants[vid]["path"]
        for seed in range(7500, 7510):
            for seat in (0, 1):
                jobs.append([f"{vid}@PUB{opponent_index:02d}", agent, str(opponent), seed, seat])

assert len(jobs) == 4000
keys = [f"{job[0]}|{job[3]}|{job[4]}" for job in jobs]
assert len(keys) == len(set(keys))
(HERE / "jobs-stage3.json").write_text(json.dumps(jobs, indent=1) + "\n")
print(len(jobs), sha256(HERE / "jobs-stage3.json"))
