import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATES = ("v111", "v169", "v074")
PARENT = ROOT / "releases/mirror-screen-v171/main.py"
O1 = ROOT / "releases/public-newmeta-127ed3e6-exact/main.py"
DP = ROOT / "releases/public-tetsutani-demand-preserving-0924-exact/main.py"
P4B_EPISODES = ROOT / "experiments/p4b_20260926/episodes.json"
STAGE3_OPPONENTS = ROOT / "experiments/exp023_mirror_screen/stage3-opponents.json"
G26_PATHS = (
    "analysis/daily_scan/20260926/extracted/a-song-of-ice-and-fire-fixed-flexible/main.py",
    "analysis/daily_scan/20260926/extracted/kaggriculture-harvest-ledger/main.py",
    "analysis/daily_scan/20260926/extracted/kaggriculture-multi-route-farming-agent/main.py",
    "analysis/daily_scan/20260926/extracted/kaggriculture-top-2-master-engine-v4/main.py",
    "analysis/daily_scan/20260926/extracted/kaggriculture-hack/main.py",
)
EXPECTED_PARENT_SHA = "496460f81869ebbd1bf80f3dd3c9440ef72c41819a831ee39a16f180d7c0bd5d"
EXPECTED_O1_SHA = "127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652"
EXPECTED_DP_SHA = "178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_panel(jobs, agents, opponent_id, opponent_path, seeds):
    for vid, agent_path in agents:
        for seed in seeds:
            for seat in (0, 1):
                jobs.append([vid, str(agent_path), opponent_id, str(opponent_path), seed, seat])


variants = {row["id"]: row for row in json.loads((HERE / "variants.json").read_text())}
assert sha256(PARENT) == EXPECTED_PARENT_SHA
assert sha256(O1) == EXPECTED_O1_SHA
assert sha256(DP) == EXPECTED_DP_SHA

candidate_agents = []
for vid in CANDIDATES:
    path = ROOT / variants[vid]["path"]
    assert sha256(path) == variants[vid]["sha256"], (vid, "candidate sha mismatch")
    candidate_agents.append((vid, path))
paired_agents = candidate_agents + [("P", PARENT)]

opponent_manifest = json.loads(STAGE3_OPPONENTS.read_text())
assert opponent_manifest["public_top15"][0]["sha256"] == EXPECTED_O1_SHA
public_guard = []
for index, item in enumerate(opponent_manifest["public_top15"][1:]):
    path = ROOT / item["path"]
    assert sha256(path) == item["sha256"], (index, item["path"], "public opponent sha mismatch")
    public_guard.append({"id": f"PUB{index:02d}", "path": item["path"], "sha256": item["sha256"]})
assert len(public_guard) == 14

g26_guard = []
for index, relative in enumerate(G26_PATHS):
    path = ROOT / relative
    assert path.is_file(), relative
    g26_guard.append({"id": f"G26{index:02d}", "path": relative, "sha256": sha256(path)})
guard = public_guard + g26_guard
assert len(guard) == 19

episodes = json.loads(P4B_EPISODES.read_text())
assert len(episodes) == 121
hosted_opponents = []
for index, episode in enumerate(episodes):
    opponent_path = ROOT / episode["opp_path"]
    assert opponent_path.is_file(), (index, episode["opp_path"])
    actual_sha = sha256(opponent_path)
    hosted_opponents.append({
        "index": index,
        "episode": episode["id"],
        "path": episode["opp_path"],
        "recorded_sha256": episode["opp_sha256"],
        "actual_sha256": actual_sha,
        "recorded_sha_mismatch": actual_sha != episode["opp_sha256"],
    })
    assert not 9000 <= episode["seed"] <= 9599, (index, "forbidden holdout seed")

jobs = []
add_panel(jobs, candidate_agents, "A-O2", PARENT, range(8200, 8400))
add_panel(jobs, paired_agents, "AP-O1", O1, range(8200, 8400))
add_panel(jobs, paired_agents, "B-DP", DP, range(8400, 8500))
for item in guard:
    add_panel(jobs, paired_agents, item["id"], ROOT / item["path"], range(8500, 8510))
for index, episode in enumerate(episodes):
    opponent_id = f"H{index:03d}-E{episode['id']}"
    for vid, agent_path in paired_agents:
        jobs.append([
            vid,
            str(agent_path),
            opponent_id,
            str(ROOT / episode["opp_path"]),
            episode["seed"],
            episode["seat"],
        ])

assert len(jobs) == 5604
keys = [f"{job[0]}|{job[2]}|{job[4]}|{job[5]}" for job in jobs]
assert len(keys) == len(set(keys))

jobs_path = HERE / "jobs-stage3.json"
jobs_path.write_text(json.dumps(jobs, indent=1) + "\n")
manifest = {
    "candidates": list(CANDIDATES),
    "workers": 5,
    "jobs": len(jobs),
    "panels": {"A": 1200, "A_prime": 1600, "B": 800, "C_D": 1520, "H": 484},
    "seeds": {"A_A_prime": [8200, 8399], "B": [8400, 8499], "C_D": [8500, 8509]},
    "parent": {"path": str(PARENT.relative_to(ROOT)), "sha256": sha256(PARENT)},
    "o1": {"path": str(O1.relative_to(ROOT)), "sha256": sha256(O1)},
    "dp": {"path": str(DP.relative_to(ROOT)), "sha256": sha256(DP)},
    "candidates_sha256": {vid: variants[vid]["sha256"] for vid in CANDIDATES},
    "guard": guard,
    "hosted_rows": len(episodes),
    "hosted_unique_episode_ids": len({episode["id"] for episode in episodes}),
    "hosted_opponents": hosted_opponents,
    "hosted_recorded_sha_mismatches": sum(item["recorded_sha_mismatch"] for item in hosted_opponents),
    "p4b_episodes_sha256": sha256(P4B_EPISODES),
    "stage2_summary_sha256": sha256(HERE / "stage2-summary.claude.json"),
    "screen_summary_sha256": sha256(HERE / "screen-summary.claude-fixedjudge.json"),
    "jobs_sha256": sha256(jobs_path),
}
(HERE / "stage3-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
