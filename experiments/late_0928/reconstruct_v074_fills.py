"""Reconstruct exact v074 SELL commits from the saved hosted replay, without a new game."""
import copy
import gzip
import json
import pathlib

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

HERE = pathlib.Path(__file__).resolve().parent
EPISODE = 114044162
SEAT = 0
RAW = HERE.parents[1] / "private_artifacts" / "v074_hosted_20260927" / "raw" / f"{EPISODE}.json.gz"
replay = json.load(gzip.open(RAW))
cfg = replay["configuration"]
board_size = int(cfg.get("boardSize", 10))
turns_per_day = int(cfg.get("turnsPerDay", 24))
shed_capacity = int(cfg.get("shedCapacity", 100))
max_orders = max(1, int(cfg.get("maxMarketOrdersPerTurn", 10)))
hire_mult = int(cfg.get("farmHandCostMult", engine.FARM_HAND_COST_MULT))
fills = []


def apply_units(farms, privates, actions, step):
    day = step // turns_per_day
    for player, action in enumerate(actions):
        farmer_action = action.get("farmer", ["PASS"]) if isinstance(action, dict) else ["PASS"]
        hand_actions = action.get("hands", []) if isinstance(action, dict) else []
        hand_actions = hand_actions if isinstance(hand_actions, list) else []
        unit_actions = [farmer_action, *hand_actions]
        demand = {}
        for unit_action in unit_actions:
            if isinstance(unit_action, list) and len(unit_action) >= 2 and unit_action[0] == "PLANT":
                demand[unit_action[1]] = demand.get(unit_action[1], 0) + 1
        seeds = privates[player].get("seeds", {})
        blocked = {crop for crop, n in demand.items() if n > seeds.get(crop, 0)}
        def allowed(unit_action):
            if isinstance(unit_action, list) and len(unit_action) >= 2 and unit_action[0] == "PLANT" and unit_action[1] in blocked:
                return ["PASS"]
            return unit_action
        engine._apply_unit_action(farms[player], privates[player], 0, allowed(farmer_action), board_size, day, turns_per_day, shed_capacity)
        for hand, unit_action in enumerate(hand_actions, 1):
            engine._apply_unit_action(farms[player], privates[player], hand, allowed(unit_action), board_size, day, turns_per_day, shed_capacity)


def process_market(farms, privates, market, actions, step):
    queues = []
    for action in actions:
        orders = action.get("market", []) if isinstance(action, dict) else []
        queues.append(list(orders)[:max_orders] if isinstance(orders, list) else [])
    for order_index in range(max((len(q) for q in queues), default=0)):
        states = [engine._parse_order(q[order_index]) if order_index < len(q) else None for q in queues]
        for player, state in enumerate(states):
            if state is None:
                continue
            if state["type"] == "HIRE":
                engine._do_hire(farms[player], privates[player], board_size, hire_mult)
                states[player] = None
            elif state["type"] == "BUY_LAND":
                engine._do_buy_land(farms[player], board_size)
                states[player] = None
        while True:
            quoted = [None, None]
            for player, state in enumerate(states):
                if state is None or state["remaining"] <= 0:
                    continue
                op, item = state["type"], state["item"]
                if op == "SELL" and item in engine.PRODUCTS:
                    quoted[player] = (op, item, engine.market_price(item, market["inventory"][item], market.get("params")), state)
                elif op == "BUY_PRODUCT" and item in ("WHEAT", "FERTILIZER"):
                    quoted[player] = (op, item, engine.market_price(item, market["inventory"][item] - 1, market.get("params")), state)
                elif op == "BUY_SEED" and item in engine.CROPS:
                    quoted[player] = (op, item, engine.CROPS[item]["seed"], state)
                elif op == "BUY_ANIMAL" and item in engine.ANIMALS:
                    quoted[player] = (op, item, engine.ANIMALS[item]["cost"], state)
                else:
                    states[player] = None
            if all(q is None for q in quoted):
                break
            committed = False
            for player, quote in enumerate(quoted):
                if quote is None:
                    continue
                op, item, price, state = quote
                before_shed = privates[player]["shed"].get(item, 0)
                ok = engine._commit_unit(op, item, price, farms[player], privates[player], market, shed_capacity)
                if ok:
                    state["remaining"] -= 1
                    committed = True
                    if op == "SELL" and player == SEAT:
                        fills.append({"step": step, "player": player, "item": item, "price": price,
                                      "shed_before": before_shed, "shed_after": privates[player]["shed"].get(item, 0)})
                else:
                    states[player] = None
            if not committed:
                break
        engine._refresh_prices(market)


for step in range(576, 719):
    before = replay["steps"][step]
    after = replay["steps"][step + 1]
    farms = copy.deepcopy(before[0]["observation"]["farms"])
    privates = [copy.deepcopy(before[player]["observation"]["private"]) for player in (0, 1)]
    market = copy.deepcopy(before[0]["observation"]["market"])
    actions = [copy.deepcopy(after[player]["action"]) for player in (0, 1)]
    apply_units(farms, privates, actions, step)
    process_market(farms, privates, market, actions, step)
    expected_money = [after[0]["observation"]["farms"][player]["money"] for player in (0, 1)]
    actual_money = [farms[player]["money"] for player in (0, 1)]
    assert actual_money == expected_money, (step, actual_money, expected_money)

out = {
    "episode": EPISODE,
    "seat": SEAT,
    "validated_steps": [576, 718],
    "validation": "post-market money exact at every step",
    "fills_after_575": fills,
}
(HERE / "cause_trace_v074_T114044162.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print("fills", len(fills), "revenue", sum(f["price"] for f in fills))
