"""One-game, one-worker cProfile probe for REVIEW-0927C."""

import cProfile
import hashlib
import io
import json
import pstats
from pathlib import Path

from kaggle_environments import make
from kaggle_environments.agent import get_last_callable


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "experiments/exp029_dpnew_mirror/variants/d157.py"
OPPONENT = ROOT / "releases/public-newmeta-127ed3e6-exact/main.py"
OUTPUT = ROOT / "experiments/review_0927c/profile_d157.json"


def load(path):
    return get_last_callable(path.read_text(), path=str(path))


candidate = load(CANDIDATE)
opponent = load(OPPONENT)
profiler = cProfile.Profile()
durations = []


def measured(observation, configuration):
    import time

    start = time.perf_counter()
    profiler.enable()
    try:
        return candidate(observation, configuration)
    finally:
        profiler.disable()
        durations.append(time.perf_counter() - start)


environment = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 14100})
environment.run([measured, opponent])
cumulative_stream = io.StringIO()
own_time_stream = io.StringIO()
pstats.Stats(profiler, stream=cumulative_stream).strip_dirs().sort_stats("cumulative").print_stats(40)
pstats.Stats(profiler, stream=own_time_stream).strip_dirs().sort_stats("time").print_stats(40)
result = {
    "candidate_sha256": hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
    "opponent_sha256": hashlib.sha256(OPPONENT.read_bytes()).hexdigest(),
    "seed": 14100,
    "seat": 0,
    "calls": len(durations),
    "max_step_seconds": max(durations),
    "total_agent_seconds": sum(durations),
    "over_0_8": sum(value > 0.8 for value in durations),
    "over_1_0": sum(value > 1.0 for value in durations),
    "overage_seconds": sum(max(0.0, value - 1.0) for value in durations),
    "statuses": [agent.status for agent in environment.steps[-1]],
    "rewards": [agent.reward for agent in environment.steps[-1]],
    "profile_top40_cumulative": cumulative_stream.getvalue(),
    "profile_top40_own_time": own_time_stream.getvalue(),
}
OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: value for key, value in result.items() if not key.startswith("profile_top40_")}))
