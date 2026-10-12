#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

# Operations that mutate tiles or inventories
_TILE_OPS = {
    "PLANT", "WATER", "HARVEST", "FERTILIZE", "DIG", "BUILD_COOP", "BUILD_PASTURE",
    "FEED", "COLLECT_FERTILIZER", "CARE", "PICKUP", "PLACE", "DROP"
}
_MOVE_OPS = {"NORTH", "SOUTH", "EAST", "WEST"}

def audit_episode(replay_path):
    with open(replay_path, "rb") as f:
        raw = f.read()
    r = json.loads(raw)
    names = r["info"]["TeamNames"]
    assert names.count("Sian") == 1, f"Ambiguous Sian seat in {replay_path}"
    seat = names.index("Sian")
    margin = r["rewards"][seat] - r["rewards"][1 - seat]
    outcome = "W" if margin > 0 else "L" if margin < 0 else "D"

    hire_failed_total = 0
    true_noop_total = 0
    seed_blocked_total = 0
    noop_by_op = {}

    steps = r["steps"]
    for i in range(1, len(steps)):
        pre_step = steps[i - 1]
        cur_step = steps[i]

        pre_obs = pre_step[seat]["observation"]
        post_obs = cur_step[seat]["observation"]
        act_obj = cur_step[seat].get("action") or {}

        # 1. HIRE Audit
        orders = act_obj.get("market", [])
        if isinstance(orders, list):
            requested_hires = sum(
                isinstance(o, list) and len(o) > 0 and o[0] == "HIRE" for o in orders[:10]
            )
            if requested_hires > 0:
                if pre_obs["day"] == post_obs["day"]:
                    filled = post_obs["farms"][seat]["hires_today"] - pre_obs["farms"][seat]["hires_today"]
                    hire_failed_total += max(0, requested_hires - filled)

        # 2. Hand Actions Audit
        hand_actions = act_obj.get("hands", [])
        if not isinstance(hand_actions, list):
            continue

        pre_farm = pre_obs["farms"][seat]
        post_farm = post_obs["farms"][seat]
        pre_hands = pre_farm.get("hands", [])
        post_hands = post_farm.get("hands", [])

        pre_priv = pre_obs.get("private", {})
        post_priv = post_obs.get("private", {})
        pre_seeds = pre_priv.get("seeds", {})
        post_seeds = post_priv.get("seeds", {})
        pre_invs = pre_priv.get("inventories", [])
        post_invs = post_priv.get("inventories", [])

        # Plant demand this turn for atomic blocked plant detection (engine :920-933)
        farmer_act = act_obj.get("farmer", ["PASS"])
        unit_actions = [farmer_act] + hand_actions
        plant_demand = {}
        for ua in unit_actions:
            if isinstance(ua, (list, tuple)) and len(ua) >= 2 and ua[0] == "PLANT":
                c = ua[1]
                plant_demand[c] = plant_demand.get(c, 0) + 1

        for h_idx, h_act in enumerate(hand_actions):
            if not h_act:
                continue
            op = h_act[0] if isinstance(h_act, (list, tuple)) else str(h_act)
            if op == "PASS":
                continue

            if h_idx >= len(pre_hands) or h_idx >= len(post_hands):
                continue

            loc_before = pre_hands[h_idx]
            loc_after = post_hands[h_idx]

            # Check seed-blocked PLANT exclusion
            if op == "PLANT":
                crop = h_act[1] if isinstance(h_act, (list, tuple)) and len(h_act) > 1 else None
                avail_seed = pre_seeds.get(crop, 0) if crop else 0
                if crop and (avail_seed <= 0 or plant_demand.get(crop, 0) > avail_seed):
                    seed_blocked_total += 1
                    continue

            # Hand Inventory comparison
            inv_before = pre_invs[h_idx + 1] if h_idx + 1 < len(pre_invs) else {}
            inv_after = post_invs[h_idx + 1] if h_idx + 1 < len(post_invs) else {}

            # Tile comparison at hand location
            tx, ty = loc_before[0], loc_before[1]
            tile_before = pre_farm["tiles"][ty][tx]
            tile_after = post_farm["tiles"][ty][tx]

            # Check if any observable state changed
            loc_changed = (loc_before != loc_after)
            inv_changed = (inv_before != inv_after)
            tile_changed = (tile_before != tile_after)

            # Shed / seeds change (for DROP, PICKUP, PLACE, PLANT)
            shed_changed = (pre_priv.get("shed", {}) != post_priv.get("shed", {}))
            seeds_changed = (pre_seeds != post_seeds)

            state_changed = loc_changed or inv_changed or tile_changed or shed_changed or seeds_changed

            if not state_changed:
                true_noop_total += 1
                noop_by_op[op] = noop_by_op.get(op, 0) + 1

    return {
        "episode_id": r["info"]["EpisodeId"],
        "path": str(replay_path),
        "outcome": outcome,
        "margin": margin,
        "hire_failed": hire_failed_total,
        "true_noop": true_noop_total,
        "seed_blocked_plant": seed_blocked_total,
        "noop_by_op": noop_by_op,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="evidence/raw/p1c_replays")
    args = parser.parse_args()

    replays = sorted(Path(args.dir).glob("episode-*-replay.json"))
    assert len(replays) == 77, f"Expected 77 replays, found {len(replays)}"

    results = []
    summary = {
        "W": {"games": 0, "hire_failed_orders": 0, "true_noops": 0, "games_with_hire_fail": 0, "games_with_noop": 0},
        "D": {"games": 0, "hire_failed_orders": 0, "true_noops": 0, "games_with_hire_fail": 0, "games_with_noop": 0},
        "L": {"games": 0, "hire_failed_orders": 0, "true_noops": 0, "games_with_hire_fail": 0, "games_with_noop": 0},
    }
    aggregate_noop_ops = {}

    for p in replays:
        res = audit_episode(p)
        results.append(res)
        out = res["outcome"]
        summary[out]["games"] += 1
        summary[out]["hire_failed_orders"] += res["hire_failed"]
        summary[out]["true_noops"] += res["true_noop"]
        if res["hire_failed"] > 0:
            summary[out]["games_with_hire_fail"] += 1
        if res["true_noop"] > 0:
            summary[out]["games_with_noop"] += 1

        for op, cnt in res["noop_by_op"].items():
            aggregate_noop_ops[op] = aggregate_noop_ops.get(op, 0) + cnt

    output = {
        "unique_episodes": len(results),
        "summary": summary,
        "aggregate_noop_ops": dict(sorted(aggregate_noop_ops.items(), key=lambda x: -x[1])),
        "results": results,
    }

    out_path = Path("experiments/results/p1c_20260918_audit/noop_audit.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"unique_episodes": len(results), "summary": summary, "aggregate_noop_ops": aggregate_noop_ops}, indent=2))

if __name__ == "__main__":
    main()
