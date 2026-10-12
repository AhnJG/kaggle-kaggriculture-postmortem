"""Read-only public 55be action fingerprint on recorded survey observations.

Uses one available public episode per target team. This is a lineage diagnostic,
not a candidate bot or an intervention test.
"""
import contextlib
import copy
import gzip
import io
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

from kaggle_environments.utils import structify

PARENT = "releases/public-dpnew-55be5d5f-exact/main.py"
RAW = "private_artifacts/survey300_20260929/raw"
OUT = "experiments/fp_survey300/lineage.jsonl"


def normalized(action):
    action = action or {}
    return json.dumps({"farmer": action.get("farmer"), "hands": action.get("hands") or [],
                       "market": (action.get("market") or [])[:10]}, sort_keys=True)


def one(job):
    team_id, team_name, episode, seat = job
    begin = time.time()
    with gzip.open(f"{RAW}/{episode}.json.gz", "rt", encoding="utf-8") as stream:
        replay = json.load(stream)
    if replay["info"].get("TeamNames", [None, None])[seat] != team_name:
        return {"team_id": team_id, "episode": episode, "error": "team_name_mismatch"}
    seed = replay["info"].get("seed")
    if isinstance(seed, int) and 9000 <= seed <= 9599:
        return {"team_id": team_id, "episode": episode, "error": "forbidden_seed"}
    namespace = {"__name__": "survey_public_55be"}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(open(PARENT, encoding="utf-8").read(), PARENT, "exec"), namespace)
    agent = namespace.get("kaggle_submission_agent")
    if not callable(agent):
        return {"team_id": team_id, "episode": episode, "error": "no_entrypoint"}
    cfg = structify(replay["configuration"])
    differences = 0
    first = None
    failures = 0
    for step in range(len(replay["steps"]) - 1):
        observation = copy.deepcopy(replay["steps"][step][seat]["observation"])
        shared = replay["steps"][step][0]["observation"]
        for key in ("step", "farms", "market", "town"):
            if key not in observation:
                observation[key] = copy.deepcopy(shared[key])
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                predicted = agent(structify(observation), cfg)
        except Exception:
            predicted = None
            failures += 1
        actual = replay["steps"][step + 1][seat]["action"]
        if normalized(predicted) != normalized(actual):
            differences += 1
            if first is None:
                first = step
    return {"team_id": team_id, "team": team_name, "episode": episode,
            "first_diff": first, "different_steps": differences,
            "agent_errors": failures, "elapsed_s": round(time.time() - begin, 3)}


def jobs():
    targets = json.load(open("analysis/survey300_20260929/targets.json", encoding="utf-8"))
    episodes = json.load(open("analysis/survey300_20260929/episodes_all.json", encoding="utf-8"))
    by_submission = {}
    for episode in episodes:
        if episode.get("replay_missing"):
            continue
        by_submission.setdefault(episode["submission_id"], []).append(episode)
    selected = []
    for target in targets:
        options = sorted(by_submission.get(target["id"], []), key=lambda x: x["id"])
        if options:
            selected.append((target["team_id"], target["team"], options[0]["id"], options[0]["our_seat"]))
    return selected


def main():
    all_jobs = jobs()
    done = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as stream:
            done = {json.loads(line)["team_id"] for line in stream}
    todo = [job for job in all_jobs if job[0] not in done]
    print(f"teams_with_raw={len(all_jobs)} todo={len(todo)}", flush=True)
    with ProcessPoolExecutor(max_workers=4) as pool, open(OUT, "a", encoding="utf-8") as output:
        for i, result in enumerate(pool.map(one, todo), 1):
            output.write(json.dumps(result, separators=(",", ":")) + "\n")
            if i % 20 == 0 or i == len(todo):
                output.flush()
                print(f"processed={i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--single":
        print(json.dumps(one(jobs()[0]), ensure_ascii=False))
    else:
        main()
