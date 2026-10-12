"""KAGRI-016 local policy factory built on the immutable KAGRI-015 parent."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN_PATH = ROOT / "main.py"
MAIN_SHA256 = "d6cdb83ffdb27d2614330b20d438a6a20e82c7f4a72ead5ca8be897859de0b59"

SELL_CAPS = {
    "B2": {"WHEAT": 4, "STRAWBERRY": 3, "CARROT": 3, "MILK": 3,
           "TOMATO": 2, "EGG": 2, "WOOL": 2, "MELON": 1, "FERTILIZER": 1},
    "B3": {"WHEAT": 2, "STRAWBERRY": 1, "CARROT": 1, "MILK": 1,
           "TOMATO": 1, "EGG": 1, "WOOL": 1, "MELON": 1, "FERTILIZER": 1},
}
SELL_HOURS = {"B2": (1, 7, 13, 19), "B3": tuple(range(0, 24, 2))}
SAFETY_SHED_OCCUPANCY = 60


class _MarketPlan(list):
    def __init__(self, rows=(), *, safety_valve=False, deferred_sell_lines=0):
        super().__init__(rows)
        self.safety_valve = safety_valve
        self.deferred_sell_lines = deferred_sell_lines


def _load_parent():
    digest = hashlib.sha256(MAIN_PATH.read_bytes()).hexdigest()
    if digest != MAIN_SHA256:
        raise RuntimeError(f"main.py SHA mismatch: {digest} != {MAIN_SHA256}")
    spec = importlib.util.spec_from_file_location("_exp003_parent_policy", MAIN_PATH)
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    return policy


def build_agent(*, crop_counts, sell_mode="B1", slot_mode="C1", switch_day=2):
    """Return a KAGRI-016 policy with one predeclared crop/sell/slot configuration."""
    if sum(crop_counts.values()) != 75 or any(v < 0 for v in crop_counts.values()):
        raise ValueError(f"crop_counts must allocate exactly 75 tiles: {crop_counts}")
    if sell_mode not in ("B1", "B2", "B3"):
        raise ValueError(f"unknown sell_mode: {sell_mode}")
    if slot_mode not in ("C1", "C2", "C3"):
        raise ValueError(f"unknown slot_mode: {slot_mode}")

    policy = _load_parent()
    policy.CROPS["TOMATO"] = {
        "seed": 50, "first_yield_day": 8, "max_yield_day": 8,
    }
    crop_order = tuple((crop, int(crop_counts.get(crop, 0))) for crop in
                       ("MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"))

    def crop_of(i, day):
        if day < switch_day:
            return policy._base_crop_of(i)
        rank = policy._PREMIUM_RANK[i]
        boundary = 0
        for crop, count in crop_order:
            boundary += count
            if rank < boundary:
                return crop
        return "WHEAT"

    policy._crop_of = crop_of

    def seed_orders(tiles, seeds, day, budget, max_lines=None):
        need = {}
        for i in range(policy.N_TILES):
            crop = policy._crop_of(i, day)
            if not policy._can_plant_day(i, crop, day):
                continue
            tx, ty = policy.TILE_ORDER[i]
            tile = tiles[ty][tx]
            if tile is None or policy._is_weed(tile):
                need[crop] = need.get(crop, 0) + 1
            elif policy._is_plant(tile) and policy._harvest_ready(tile, day):
                need[crop] = need.get(crop, 0) + 1

        rows = []
        for crop in ("MELON", "STRAWBERRY", "TOMATO", "WHEAT", "CARROT"):
            if max_lines is not None and len(rows) >= max_lines:
                break
            want = need.get(crop, 0) - int(seeds.get(crop, 0) or 0)
            if want <= 0:
                continue
            price = policy.CROPS[crop]["seed"]
            want = min(want, int(budget // price))
            if want > 0:
                rows.append(["BUY_SEED", crop, want])
                budget -= want * price
        return rows, budget

    def hire_orders(farm, budget):
        hires_today = int(policy._get(farm, "hires_today", 0) or 0)
        rows = []
        for j in range(hires_today, policy.N_HANDS):
            if j >= len(policy.HIRE_FIB):
                break
            cost = policy.HIRE_FIB[j]
            if budget < cost:
                break
            budget -= cost
            rows.append(["HIRE"])
        return rows, budget

    def plan_market(obs, tiles, farm, private, unit_actions, day, hour):
        shed = policy._get(private, "shed", {}) or {}
        seeds = policy._get(private, "seeds", {}) or {}
        invs = policy._get(private, "inventories", []) or []
        prices = policy._get(policy._get(obs, "market", {}) or {}, "prices", {}) or {}
        money = float(policy._get(farm, "money", 0) or 0)
        sim_shed = policy._simulate_drops(shed, invs, unit_actions)
        is_final_step = day * policy.TURNS_PER_DAY + hour == policy.LAST_STEP

        safety = sell_mode in SELL_CAPS and sum(int(v or 0) for v in shed.values()) >= SAFETY_SHED_OCCUPANCY
        scheduled = sell_mode == "B1" or hour in SELL_HOURS[sell_mode]
        sell_rows = []
        if scheduled or safety or is_final_step:
            for item in policy.SELLABLE:
                n = int(sim_shed.get(item, 0) or 0)
                if n <= 0:
                    continue
                if sell_mode in SELL_CAPS and not safety and not is_final_step:
                    n = min(n, SELL_CAPS[sell_mode][item])
                if n > 0:
                    sell_rows.append((float(prices.get(item, 0) or 0), item, n))
        sell_rows.sort(reverse=True)

        deferred_sell_lines = 0
        if slot_mode == "C3" and not safety and not is_final_step:
            deferred_sell_lines = max(0, len(sell_rows) - 4)
            sell_rows = sell_rows[:4]
        orders = [["SELL", item, n] for _price, item, n in sell_rows]

        if day > policy.LAST_DAY:
            return _MarketPlan(orders, safety_valve=safety,
                               deferred_sell_lines=deferred_sell_lines)

        budget = money
        land_cost = policy._land_due(farm, day, hour)
        if land_cost is not None and budget >= land_cost:
            orders.append(["BUY_LAND"])
            budget -= land_cost

        if slot_mode == "C1":
            hires, budget = hire_orders(farm, budget)
            orders.extend(hires)
            buys, budget = seed_orders(tiles, seeds, day, budget)
            orders.extend(buys)
        else:
            max_seed_lines = 3 if slot_mode == "C3" else None
            buys, budget = seed_orders(tiles, seeds, day, budget, max_seed_lines)
            orders.extend(buys)
            hires, budget = hire_orders(farm, budget)
            orders.extend(hires)

        return _MarketPlan(orders, safety_valve=safety,
                           deferred_sell_lines=deferred_sell_lines)

    policy._plan_market = plan_market
    original_plan = policy.plan

    def plan(obs):
        action = original_plan(obs)
        market = action.get("market")
        action["__exp003_safety_valve"] = bool(getattr(market, "safety_valve", False))
        action["__exp003_deferred_sell_lines"] = int(
            getattr(market, "deferred_sell_lines", 0))
        return action

    policy.plan = plan

    def clamp_market(obs, action):
        market = action.get("market")
        rows = list(market) if isinstance(market, list) else []
        action["__exp003_pre_market"] = rows
        action["market"] = rows[:policy.MAX_MARKET_ORDERS]
        return action

    policy.clamp_market = clamp_market
    policy.GUARDS = tuple(clamp_market if guard.__name__ == "clamp_market" else guard
                          for guard in policy.GUARDS)
    return policy.agent
