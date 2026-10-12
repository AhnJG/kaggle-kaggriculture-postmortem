"""Replay the twelve preregistered EXP-028 diagnostic games with action traces.

This is intentionally single-process so it does not contend with EXP-030.
"""
import contextlib
import io
import json
import traceback
from pathlib import Path

from kaggle_environments import make
from kaggle_environments.agent import get_last_callable


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "experiments/exp028_dpnew/games.jsonl"
D_PATH = ROOT / "releases/public-dpnew-55be5d5f-exact/main.py"
P_PATH = ROOT / "releases/round2-v074/main.py"
OUT = ROOT / "experiments/hypgen_0927"

SELECTED = [
    # Largest D wins: the six largest-margin rows in EXP-028.
    (12311, 0), (12311, 1), (12328, 1), (12328, 0), (12310, 0), (12310, 1),
    # Narrowest D wins: the three smallest positive-margin rows.
    (12341, 0), (12341, 1), (12345, 0),
    # D losses: two largest losses plus the closest loss.
    (12331, 0), (12331, 1), (12326, 0),
]


def _plain(value):
    return json.loads(json.dumps(value, default=str))


def _route_state(agent, player):
    try:
        state = agent.__globals__["_IMPL"].chassis.players.get(player, {})
        return {
            "route": state.get("route"),
            "router_state": _plain(state.get("router_state", {})),
        }
    except Exception:
        return None


def _obs_summary(obs):
    farms = obs["farms"]
    return {
        "money": [farm["money"] for farm in farms],
        "unlocked_quadrants": [farm.get("unlocked_quadrants") for farm in farms],
        "shops": list((obs.get("town") or {}).get("unlocked_shops") or []),
        "market_inventory": dict(obs["market"]["inventory"]),
        "market_prices": dict(obs["market"]["prices"]),
    }


def _expected_rows():
    rows = {}
    for line in SOURCE.read_text().splitlines():
        row = json.loads(line)
        if row["vid"] == "D" and row["opponent"] == "X-D-vs-P":
            rows[(row["seed"], row["seat"])] = row
    return rows


def play(seed, seat, expected):
    calls = {"D": {}, "P": {}}
    errors = []
    with contextlib.redirect_stdout(io.StringIO()):
        d_agent = get_last_callable(D_PATH.read_text(), path=str(D_PATH))
        p_agent = get_last_callable(P_PATH.read_text(), path=str(P_PATH))

        def wrapped(label, agent):
            def call(obs, cfg):
                step = int(obs["step"])
                try:
                    action = agent(obs, cfg)
                    calls[label][step] = {
                        "player": int(obs["player"]),
                        "action": _plain(action),
                        "observation": _obs_summary(obs),
                        "route_state": _route_state(agent, int(obs["player"])),
                    }
                    return action
                except Exception:
                    errors.append({"label": label, "step": step, "traceback": traceback.format_exc()[-1000:]})
                    raise
            return call

        d_wrap, p_wrap = wrapped("D", d_agent), wrapped("P", p_agent)
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        env.run([d_wrap, p_wrap] if seat == 0 else [p_wrap, d_wrap])

    final = env.steps[-1]
    rewards = [s.reward for s in final]
    statuses = [s.status for s in final]
    if rewards != expected["rewards"] or statuses != expected["statuses"]:
        raise RuntimeError(
            f"EXP-028 mismatch seed={seed} seat={seat}: "
            f"expected {expected['rewards']}/{expected['statuses']}, got {rewards}/{statuses}"
        )
    trace_path = OUT / f"trace-{seed}-seat{seat}.jsonl"
    with trace_path.open("w") as handle:
        for step in range(719):
            handle.write(json.dumps({"step": step, "D": calls["D"].get(step), "P": calls["P"].get(step)}) + "\n")
    return {
        "seed": seed,
        "seat": seat,
        "rewards": rewards,
        "statuses": statuses,
        "D_margin": rewards[seat] - rewards[1 - seat],
        "D_calls": len(calls["D"]),
        "P_calls": len(calls["P"]),
        "errors": errors,
        "trace": str(trace_path.relative_to(ROOT)),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    expected = _expected_rows()
    results = []
    for seed, seat in SELECTED:
        results.append(play(seed, seat, expected[(seed, seat)]))
        print(json.dumps(results[-1]), flush=True)
    (OUT / "replay-verification.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
