"""Run only the frozen 40-game smoke, serially."""
import hashlib
import json
from pathlib import Path

from experiments.exp024_round2.run import play

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PREREG_SHA = "578f171b6b14b22050f73c275666d901ac0bee97117f9f8aad33d052c008be8d"


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    assert sha("experiments/top2400_codex/prereg.json") == PREREG_SHA
    prereg = json.loads((OUT / "prereg.json").read_text())
    assert sha(prereg["parent"]) == prereg["parent_sha256"]
    assert sha(prereg["candidate"]) == prereg["candidate_sha256"]
    jobs = json.loads((OUT / "jobs-smoke.json").read_text())
    assert len(jobs) == 40 and len(jobs) <= 60
    assert sha("experiments/top2400_codex/jobs-smoke.json") == prereg["jobs_sha256"]["jobs-smoke.json"]
    done_path = OUT / "games-smoke.jsonl"
    done = {json.loads(line)["key"] for line in done_path.open()} if done_path.exists() else set()
    with done_path.open("a") as f:
        for job in jobs:
            key = f"{job[0]}|{job[2]}|{job[4]}|{job[5]}"
            if key in done:
                continue
            result = play(tuple(job))
            f.write(json.dumps(result) + "\n")
            f.flush()
            print(key, result["score"], result["action_count"], result["err"], flush=True)


if __name__ == "__main__":
    main()
