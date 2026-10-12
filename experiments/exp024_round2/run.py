import contextlib
import hashlib
import io
import json
import os
import sys
import time
import traceback
from multiprocessing import Pool


WORKERS = 5
OUT = os.environ.get("EXP024_OUT", "games.jsonl")


def play(job):
    vid, path, opponent_id, opponent_path, seed, seat = job
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable

    started = time.time()
    max_step = 0.0
    actions = []
    agent_errors = []
    err = None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            me = get_last_callable(open(path).read(), path=path)
            opponent = get_last_callable(open(opponent_path).read(), path=opponent_path)

            def wrap(obs, cfg):
                nonlocal max_step
                before = time.perf_counter()
                try:
                    action = me(obs, cfg)
                except Exception:
                    agent_errors.append(traceback.format_exc()[-1000:])
                    raise
                elapsed = time.perf_counter() - before
                max_step = max(max_step, elapsed)
                actions.append(json.dumps(action, sort_keys=True, default=str))
                return action

            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
            env.run([wrap, opponent] if seat == 0 else [opponent, wrap])
        final = env.steps[-1]
        rewards = [s.reward for s in final]
        statuses = [s.status for s in final]
        margin = rewards[seat] - rewards[1 - seat] if None not in rewards else None
        score = None if margin is None else (1.0 if margin > 0 else 0.0 if margin < 0 else 0.5)
    except Exception:
        rewards = statuses = margin = score = None
        err = traceback.format_exc()[-1000:]
    key = f"{vid}|{opponent_id}|{seed}|{seat}"
    return {
        "key": key,
        "vid": vid,
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
        "agent_errors": agent_errors,
        "err": err,
        "sec": round(time.time() - started, 3),
    }


if __name__ == "__main__":
    jobs = json.load(open(sys.argv[1]))
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(line)["key"] for line in open(OUT)}
    todo = [tuple(job) for job in jobs if f"{job[0]}|{job[2]}|{job[4]}|{job[5]}" not in done]
    print(f"workers={WORKERS} todo={len(todo)}", flush=True)
    with Pool(WORKERS) as pool, open(OUT, "a") as output:
        for result in pool.imap_unordered(play, todo):
            output.write(json.dumps(result) + "\n")
            output.flush()
