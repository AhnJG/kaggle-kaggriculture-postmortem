#!/usr/bin/env python3
"""Summarize a downloaded hosted replay without rerunning either agent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def market_orders(action: dict | None) -> list[list]:
    if not isinstance(action, dict):
        return []
    return [order for order in (action.get("market") or []) if order]


def farm_actions(action: dict | None) -> tuple[object, object]:
    if not isinstance(action, dict):
        return None, None
    return action.get("farmer"), action.get("hands")


def same_order_multiset(left: list[list], right: list[list]) -> bool:
    normalize = lambda rows: sorted(json.dumps(row, sort_keys=True) for row in rows)
    return normalize(left) == normalize(right)


def bank(step: list[dict], observer: int, player: int) -> float:
    return float(step[observer]["observation"]["farms"][player]["money"])


def daily_curve(replay: dict, target: int) -> list[dict]:
    opponent = 1 - target
    previous_gap = 0.0
    rows = []
    for day in range(len(replay["steps"]) // 24):
        step = (day + 1) * 24 - 1
        own = bank(replay["steps"][step], target, target)
        other = bank(replay["steps"][step], target, opponent)
        gap = own - other
        rows.append(
            {
                "day": day,
                "step": step,
                "target_bank": own,
                "opponent_bank": other,
                "gap": gap,
                "gap_change": gap - previous_gap,
            }
        )
        previous_gap = gap
    return rows


def durable_loss_day(curve: list[dict], threshold: float) -> dict | None:
    for index, row in enumerate(curve):
        if row["gap"] <= -threshold and all(future["gap"] <= -threshold for future in curve[index:]):
            return {"threshold": threshold, "day": row["day"], "step": row["step"], "gap": row["gap"]}
    return None


def analyze_replay(replay: dict, team: str, *, threshold: float, top: int) -> dict:
    teams = replay["info"]["TeamNames"]
    if team not in teams:
        raise ValueError(f"team {team!r} not found in {teams}")
    target = teams.index(team)
    opponent = 1 - target
    curve = daily_curve(replay, target)
    farm_diffs = []
    market_diffs = []
    reorder_steps = []
    step_rows = []
    previous_gap = 0.0

    for index, step in enumerate(replay["steps"]):
        own_action = step[target].get("action")
        opponent_action = step[opponent].get("action")
        own_market = market_orders(own_action)
        opponent_market = market_orders(opponent_action)
        if farm_actions(own_action) != farm_actions(opponent_action):
            farm_diffs.append(index)
        if own_market != opponent_market:
            market_diffs.append(index)
            if same_order_multiset(own_market, opponent_market):
                reorder_steps.append(index)
        own_bank = bank(step, target, target)
        opponent_bank = bank(step, target, opponent)
        gap = own_bank - opponent_bank
        step_rows.append(
            {
                "step": index,
                "day": index // 24,
                "hour": index % 24,
                "gap": gap,
                "gap_change": gap - previous_gap,
                "target_market": own_market,
                "opponent_market": opponent_market,
            }
        )
        previous_gap = gap

    pure_reorder_gap_change = sum(step_rows[index]["gap_change"] for index in reorder_steps)
    worst_steps = sorted(step_rows, key=lambda row: row["gap_change"])[:top]
    return {
        "episode_id": replay["info"]["EpisodeId"],
        "seed": replay["info"].get("seed"),
        "engine": replay.get("module_version"),
        "teams": teams,
        "target_team": team,
        "target_seat": target,
        "opponent": teams[opponent],
        "steps": len(replay["steps"]),
        "statuses": replay.get("statuses"),
        "rewards": replay.get("rewards"),
        "target_reward": replay["rewards"][target],
        "opponent_reward": replay["rewards"][opponent],
        "final_margin": replay["rewards"][target] - replay["rewards"][opponent],
        "daily_curve": curve,
        "durable_loss_day": durable_loss_day(curve, threshold),
        "worst_days": sorted(curve, key=lambda row: row["gap_change"])[:top],
        "action_comparison": {
            "farm_action_difference_count": len(farm_diffs),
            "farm_action_difference_steps": farm_diffs,
            "market_order_difference_count": len(market_diffs),
            "market_order_difference_steps": market_diffs,
            "same_multiset_different_order_count": len(reorder_steps),
            "same_multiset_different_order_steps": reorder_steps,
            "observed_gap_change_on_same_multiset_reorder_steps": pure_reorder_gap_change,
            "causal_warning": "The summed gap change is descriptive, not a causal estimate; game state already differs.",
        },
        "worst_steps": worst_steps,
    }


def own_action_difference(left: dict, right: dict, team: str) -> dict:
    left_seat = left["info"]["TeamNames"].index(team)
    right_seat = right["info"]["TeamNames"].index(team)
    differences = [
        index
        for index, (left_step, right_step) in enumerate(zip(left["steps"], right["steps"]))
        if left_step[left_seat].get("action") != right_step[right_seat].get("action")
    ]
    return {"count": len(differences), "steps": differences}


def step_snapshot(replay: dict, team: str, index: int) -> dict:
    target = replay["info"]["TeamNames"].index(team)
    opponent = 1 - target
    step = replay["steps"][index]

    def player_snapshot(seat: int) -> dict:
        farm = step[target]["observation"]["farms"][seat]
        tiles = farm.get("tiles") or []
        return {
            "bank": farm.get("money"),
            "hands": len(farm.get("hands") or []),
            "nonempty_tiles": sum(isinstance(tile, dict) for row in tiles for tile in row),
            "action": step[seat].get("action"),
        }

    return {
        "step": index,
        "day": index // 24,
        "hour": index % 24,
        "target": player_snapshot(target),
        "opponent": player_snapshot(opponent),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--team", required=True)
    parser.add_argument("--control-replay", type=Path)
    parser.add_argument("--durable-loss-threshold", type=float, default=5000)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--focus-steps", type=int, nargs="*", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    replay = json.loads(args.replay.read_text(encoding="utf-8"))
    result = analyze_replay(
        replay, args.team, threshold=args.durable_loss_threshold, top=args.top
    )
    result["source_replay"] = str(args.replay)
    result["focus_steps"] = [step_snapshot(replay, args.team, index) for index in args.focus_steps]
    if args.control_replay:
        control = json.loads(args.control_replay.read_text(encoding="utf-8"))
        result["control"] = {
            "source_replay": str(args.control_replay),
            "episode_id": control["info"]["EpisodeId"],
            "teams": control["info"]["TeamNames"],
            "rewards": control["rewards"],
            "same_team_action_difference": own_action_difference(replay, control, args.team),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "episode_id": result["episode_id"],
        "final_margin": result["final_margin"],
        "durable_loss_day": result["durable_loss_day"],
        "worst_days": result["worst_days"],
        "action_comparison": result["action_comparison"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
