import contextlib
import hashlib
import io
import json
import sys
import time
import traceback
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def play(job):
    arm, relative_path, opponent_id, opponent_relative_path, seed, seat = job
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable

    path = ROOT / relative_path
    opponent_path = ROOT / opponent_relative_path
    started = time.time()
    max_step = 0.0
    actions = []
    agent_errors = []
    telemetry = {}
    err = None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            me = get_last_callable(path.read_text(), path=str(path))
            opponent = get_last_callable(opponent_path.read_text(), path=str(opponent_path))

            def wrapped(obs, cfg):
                nonlocal max_step
                before = time.perf_counter()
                try:
                    action = me(obs, cfg)
                except Exception:
                    agent_errors.append(traceback.format_exc()[-1000:])
                    raise
                max_step = max(max_step, time.perf_counter() - before)
                actions.append(json.dumps(action, sort_keys=True, separators=(",", ":"), default=str))
                return action

            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
            env.run([wrapped, opponent] if seat == 0 else [opponent, wrapped])
            raw_telemetry = getattr(me, "telemetry", {})
            telemetry = {key: value for key, value in raw_telemetry.items()
                         if isinstance(value, (type(None), bool, int, float, str))}
        final = env.steps[-1]
        rewards = [state.reward for state in final]
        statuses = [state.status for state in final]
        margin = rewards[seat] - rewards[1 - seat] if None not in rewards else None
        score = None if margin is None else (1.0 if margin > 0 else 0.0 if margin < 0 else 0.5)
    except Exception:
        rewards = statuses = margin = score = None
        err = traceback.format_exc()[-1000:]
    return {
        "key": f"{arm}|{opponent_id}|{seed}|{seat}",
        "arm": arm,
        "opponent": opponent_id,
        "seed": seed,
        "seat": seat,
        "rewards": rewards,
        "statuses": statuses,
        "margin": margin,
        "score": score,
        "max_step": max_step,
        "act_sha": hashlib.sha256("\n".join(actions).encode()).hexdigest(),
        "action_count": len(actions),
        "telemetry": telemetry,
        "agent_errors": agent_errors,
        "err": err,
        "sec": round(time.time() - started, 3),
    }


if __name__ == "__main__":
    jobs = json.loads((HERE / "jobs.json").read_text())
    output_path = HERE / "games.jsonl"
    done = set()
    if output_path.exists():
        done = {json.loads(line)["key"] for line in output_path.read_text().splitlines() if line}
    todo = [job for job in jobs if f"{job[0]}|{job[2]}|{job[4]}|{job[5]}" not in done]
    print(f"workers=1 todo={len(todo)}", flush=True)
    with output_path.open("a") as output:
        for index, job in enumerate(todo, 1):
            result = play(job)
            output.write(json.dumps(result) + "\n")
            output.flush()
            print(index, result["key"], result["score"], result["telemetry"].get("activation"), flush=True)

