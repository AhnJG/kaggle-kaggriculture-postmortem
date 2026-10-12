"""Run the frozen late-game cause panel sequentially and trace actual SELL commits."""
import contextlib
import hashlib
import io
import json
import pathlib
import time
import traceback

from kaggle_environments import make
from kaggle_environments.agent import get_last_callable
from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / "cause_manifest.json").read_text())
OUT = HERE / "cause_games.jsonl"
CHECKPOINTS = (576, 648, 696, 719)


def load(path):
    path = ROOT / path
    with contextlib.redirect_stdout(io.StringIO()):
        return get_last_callable(path.read_text(), path=str(path))


def play(agent_id, agent_path, row):
    episode = int(row["episode"])
    seed = int(row["seed"])
    seat = int(row["seat"])
    tape_path = MANIFEST["tape_pattern"].format(episode=episode)
    me = load(agent_path)
    opponent = load(tape_path)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    fills = []
    actions = []
    errors = []
    max_step = 0.0
    original_commit = engine._commit_unit
    original_process_market = engine._process_market
    farm_players = {}
    current_step = -1

    def traced_process_market(state, run_env):
        farm_players.clear()
        for player, farm in enumerate(state[0].observation.farms):
            farm_players[id(farm)] = player
        return original_process_market(state, run_env)

    def traced_commit(op, item, price, farm, private, market, shed_capacity=100):
        before_money = farm.get("money", 0)
        before_shed = private.get("shed", {}).get(item, 0)
        ok = original_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and op == "SELL":
            player = farm_players.get(id(farm))
            fills.append({
                "step": current_step,
                "player": player,
                "item": item,
                "price": price,
                "money_delta": farm.get("money", 0) - before_money,
                "shed_before": before_shed,
                "shed_after": private.get("shed", {}).get(item, 0),
            })
        return ok

    def wrapped(obs, cfg):
        nonlocal max_step, current_step
        current_step = int(obs["step"])
        start = time.perf_counter()
        try:
            action = me(obs, cfg)
        except Exception:
            errors.append(traceback.format_exc()[-1000:])
            raise
        max_step = max(max_step, time.perf_counter() - start)
        actions.append(json.dumps(action, sort_keys=True, default=str))
        return action

    started = time.time()
    engine._commit_unit = traced_commit
    engine._process_market = traced_process_market
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            env.run([wrapped, opponent] if seat == 0 else [opponent, wrapped])
    finally:
        engine._commit_unit = original_commit
        engine._process_market = original_process_market

    final = env.steps[-1]
    rewards = [s.reward for s in final]
    snapshots = {}
    for checkpoint in CHECKPOINTS:
        state = env.steps[checkpoint][seat]
        snapshots[str(checkpoint)] = {
            "money": state.observation.farms[seat]["money"],
            "shed": dict(state.observation.private["shed"]),
        }
    return {
        "key": f"{agent_id}|T{episode}|{seed}|{seat}",
        "agent": agent_id,
        "agent_path": agent_path,
        "agent_sha256": hashlib.sha256((ROOT / agent_path).read_bytes()).hexdigest(),
        "episode": episode,
        "seed": seed,
        "seat": seat,
        "label": row["label"],
        "rewards": rewards,
        "statuses": [s.status for s in final],
        "score": 1.0 if rewards[seat] > rewards[1-seat] else 0.0 if rewards[seat] < rewards[1-seat] else 0.5,
        "margin": rewards[seat] - rewards[1-seat],
        "fills_after_575": [x for x in fills if x["player"] == seat and x["step"] >= 576],
        "snapshots": snapshots,
        "action_count": len(actions),
        "act_sha": hashlib.sha256("\n".join(actions).encode()).hexdigest(),
        "max_step": max_step,
        "agent_errors": errors,
        "seconds": round(time.time() - started, 3),
    }


def main():
    done = set()
    if OUT.exists():
        done = {json.loads(line)["key"] for line in OUT.read_text().splitlines() if line.strip()}
    with OUT.open("a") as output:
        for row in MANIFEST["episodes"]:
            for agent_id, agent_path in MANIFEST["agents"].items():
                key = f"{agent_id}|T{row['episode']}|{row['seed']}|{row['seat']}"
                if key in done:
                    continue
                result = play(agent_id, agent_path, row)
                output.write(json.dumps(result, sort_keys=True) + "\n")
                output.flush()
                print(key, result["rewards"], result["max_step"], flush=True)


if __name__ == "__main__":
    main()
