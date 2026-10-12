"""Serial four-game engine smoke, using the frozen jobs-smoke file."""
import json
from pathlib import Path

from experiments.exp024_round2.run import play

OUT = Path(__file__).resolve().parent
jobs = json.loads((OUT / "jobs-smoke.json").read_text())
assert len(jobs) == 4
with (OUT / "games-smoke.jsonl").open("w") as out:
    for job in jobs:
        result = play(tuple(job))
        out.write(json.dumps(result) + "\n")
        out.flush()
        print(result["key"], result["statuses"], result["action_count"],
              result["max_step"], result["err"], flush=True)
