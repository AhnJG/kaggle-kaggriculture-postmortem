"""Build the frozen open-loop, one-worker runtime, and closed-loop job lists."""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
PARENT = ("P", "releases/round2-v074/main.py")
CANDIDATES = [
    ("l576_closure1", "experiments/late_0928/candidates/l576_closure1.py"),
    ("l648_closure1", "experiments/late_0928/candidates/l648_closure1.py"),
    ("l576_wool_first", "experiments/late_0928/candidates/l576_wool_first.py"),
]

meta = json.loads((ROOT / "experiments/exp033_tapes/meta.json").read_text())
selected = sorted([r for r in meta if r["fam"] in ("127_near", "other")], key=lambda r: (r["fam"], int(r["episode"])))
assert sum(r["fam"] == "127_near" for r in selected) == 112
assert sum(r["fam"] == "other" for r in selected) == 93

open_jobs = []
for vid, path in CANDIDATES:
    for row in selected:
        episode = int(row["episode"])
        open_jobs.append([vid, path, f"T{episode}", f"experiments/exp033_tapes/tapes/T{episode}.py", int(row["seed"]), int(row["seat"])])

runtime_episodes = [113691353, 113708065, 113717551, 113734191, 113747263]
lookup = {int(r["episode"]): r for r in meta}
runtime_jobs = []
for vid, path in CANDIDATES:
    for episode in runtime_episodes:
        row = lookup[episode]
        runtime_jobs.append([vid, path, f"T{episode}", f"experiments/exp033_tapes/tapes/T{episode}.py", int(row["seed"]), int(row["seat"])])

guard = [g for g in json.loads((ROOT / "experiments/exp027_stage3/manifest.json").read_text())["guard"] if not g["sha256"].startswith("55be5d5f")]
assert len(guard) == 23
agents = [PARENT, *CANDIDATES]
closed_jobs = []
def panel(opponent_id, opponent_path, seeds):
    for vid, path in agents:
        for seed in seeds:
            for seat in (0, 1):
                closed_jobs.append([vid, path, opponent_id, opponent_path, seed, seat])
panel("O127", "releases/public-newmeta-127ed3e6-exact/main.py", range(14100, 14150))
for item in guard:
    panel(item["id"], item["path"], range(14200, 14205))
panel("D", "releases/public-dpnew-55be5d5f-exact/main.py", range(14300, 14325))

for name, jobs in (("jobs-open.json", open_jobs), ("jobs-runtime.json", runtime_jobs), ("jobs-closed-kaggle.json", closed_jobs)):
    text = json.dumps(jobs, separators=(",", ":")) + "\n"
    (HERE / name).write_text(text)
    print(name, len(jobs), hashlib.sha256(text.encode()).hexdigest())

guard_frozen = [{"id": g["id"], "path": g["path"], "sha256": g["sha256"]} for g in guard]
(HERE / "guard23.json").write_text(json.dumps(guard_frozen, indent=2, sort_keys=True) + "\n")
print("guard23.json", len(guard_frozen), hashlib.sha256((HERE / "guard23.json").read_bytes()).hexdigest())
