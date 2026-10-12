"""Read-only snapshot audit of collected public survey replays.

Reads replay observations, never imports or executes the game engine.
"""
import concurrent.futures
import glob
import gzip
import json
import os
import sys

RAW = "private_artifacts/survey300_20260929/raw"
OUT = "experiments/fp_survey300/snapshots.jsonl"


def snapshot(farm):
    counts = {}
    for row in farm["tiles"]:
        for tile in row:
            if isinstance(tile, dict):
                for field, prefix in (("crop", "C_"), ("animal", "A_")):
                    value = tile.get(field)
                    if value:
                        key = prefix + value
                        counts[key] = counts.get(key, 0) + 1
    return counts


def one(path):
    episode_id = int(os.path.basename(path).split(".")[0])
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        replay = json.load(stream)
    seed = replay.get("info", {}).get("seed")
    if isinstance(seed, int) and 9000 <= seed <= 9599:
        return {"episode": episode_id, "error": "forbidden_seed"}
    steps = replay["steps"]
    if len(steps) < 577 or len(replay.get("rewards", [])) != 2:
        return {"episode": episode_id, "error": "short_replay"}
    names = replay.get("info", {}).get("TeamNames", [])
    if len(names) != 2:
        return {"episode": episode_id, "error": "team_names"}
    snaps = {}
    for turn in (288, 576):
        farms = steps[turn][0]["observation"]["farms"]
        snaps[turn] = [snapshot(farm) for farm in farms]
    land = [[], []]
    max_hands = [[0] * 30 for _ in range(2)]
    previous_land = [1, 1]
    for turn, states in enumerate(steps):
        farms = states[0]["observation"]["farms"]
        day = min(turn // 24, 29)
        for seat, farm in enumerate(farms):
            count = len(farm["unlocked_quadrants"])
            if count > previous_land[seat]:
                land[seat].extend([max(0, (turn - 1) // 24)] * (count - previous_land[seat]))
                previous_land[seat] = count
            max_hands[seat][day] = max(max_hands[seat][day], len(farm["hands"]))
    return {
        "episode": episode_id, "teams": names, "rewards": replay["rewards"],
        "seed": seed,
        "seats": [{"snap288": snaps[288][i], "snap576": snaps[576][i],
                   "land_days": land[i], "hires_observed": sum(max_hands[i]),
                   "money288": steps[288][0]["observation"]["farms"][i]["money"],
                   "money576": steps[576][0]["observation"]["farms"][i]["money"]}
                  for i in (0, 1)],
    }


def main():
    paths = sorted(glob.glob(os.path.join(RAW, "*.json.gz")))
    print(f"raw={len(paths)}", flush=True)
    done = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as stream:
            done = {json.loads(line)["episode"] for line in stream}
    todo = [p for p in paths if int(os.path.basename(p).split(".")[0]) not in done]
    print(f"todo={len(todo)}", flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool, open(OUT, "a", encoding="utf-8") as out:
        for i, row in enumerate(pool.map(one, todo), 1):
            out.write(json.dumps(row, separators=(",", ":")) + "\n")
            if i % 100 == 0 or i == len(todo):
                out.flush()
                print(f"processed={i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
