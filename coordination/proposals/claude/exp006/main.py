"""EXP-006 candidate - team Sian, 2026-09-11. This file is ours; the parent files are unmodified.

Parent: yhay81 "Shop Router 0909" (Apache-2.0, see LICENSE.txt), loaded byte-identical from
yh_base.py (= the parent's main.py) and actions.json.

Change: while the rival farm's public signature is within distance 6 of ours (a near-clone) and
120 <= step < 680, sell up to 30 units of STRAWBERRY / MELON / MILK / WOOL one turn before the
parent's own tape sells them. Only items the parent is not already selling this turn; never more
than the projected shed stock or the part of next turn's planned quantity the parent has not already
advanced. The amount is subtracted from next turn's tape SELL orders.
Idea credit: boatlee, "V14 Clone Preemption" (public Kaggle notebook). Implementation written here.
Guards return the parent's action on any exception; each guard has its own counter.
"""
import copy
import importlib.util
from pathlib import Path

PREMIUM = ("STRAWBERRY", "MELON", "MILK", "WOOL")
MAX_CLONE_DIST = 6
FRACTION = 2.0
MAX_BATCH = 30
MIN_FUTURE_QTY = 4
START, STOP = 120, 680
MAX_ORDERS = 10
SIGNATURE_KEYS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
                  "COW", "SHEEP", "GOOSE", "PASTURE", "COOP", "WEED")

GUARD_COUNTS = {"base_raise": 0, "layer_raise": 0}
PREEMPT_COUNTS = {"turns": 0, "units": 0}
_S = {"yh": None, "players": {}}


def _yh():
    if _S["yh"] is None:
        folder = Path(agent.__code__.co_filename).resolve().parent
        spec = importlib.util.spec_from_file_location("exp006_yh_base", folder / "yh_base.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _S["yh"] = mod
    return _S["yh"]


def _signature(farm):
    counts = {k: 0 for k in SIGNATURE_KEYS}
    for row in farm.get("tiles", []) or []:
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            for field in ("crop", "animal", "kind"):
                value = str(tile.get(field, "")).upper()
                if value in counts:
                    counts[value] += 1
                    break
    return (len(farm.get("hands", []) or []),
            len(farm.get("unlocked_quadrants", []) or []),
            tuple(counts[k] for k in sorted(counts)))


def _clone_distance(observation):
    farms = observation.get("farms", []) or []
    if len(farms) < 2:
        return 10 ** 9
    a, b = _signature(farms[0]), _signature(farms[1])
    return abs(a[0] - b[0]) + 3 * abs(a[1] - b[1]) + sum(abs(x - y) for x, y in zip(a[2], b[2]))


def _layer(yh, observation, action):
    step = int(observation["step"])
    player = int(observation["player"])
    action.setdefault("market", [])
    st = _S["players"].get(player)
    if st is None or step == 0 or step < st["last_step"]:
        st = _S["players"][player] = {"last_step": step, "due_step": -1, "due": {}}
    st["last_step"] = step

    if st["due_step"] == step:
        due = dict(st["due"])
        market = []
        for order in action["market"]:
            order = list(order)
            if len(order) >= 3 and order[0] == "SELL" and due.get(order[1], 0) > 0:
                cut = min(int(order[2]), due[order[1]])
                order[2] = int(order[2]) - cut
                due[order[1]] -= cut
                if order[2] <= 0:
                    continue
            market.append(order)
        action["market"] = market
        st["due_step"], st["due"] = -1, {}

    policy = yh._POLICY
    pstate = policy.players.get(player) if policy is not None else None
    if (pstate is not None and START <= step < STOP and not st["due"]
            and _clone_distance(observation) <= MAX_CLONE_DIST and step + 1 <= yh.LAST_STEP):
        nxt = step + 1
        planned = {}
        for order in policy.tapes[pstate.plan][nxt].get("market") or []:
            if order and order[0] == "SELL" and len(order) >= 3 and order[1] in PREMIUM:
                planned[order[1]] = planned.get(order[1], 0) + max(0, int(order[2]))
        advanced = dict(pstate.advanced_sales) if pstate.sale_due_step == nxt else {}
        selling_now = {o[1] for o in action["market"] if o and o[0] == "SELL" and len(o) >= 3}
        view = yh.FarmView(observation)
        stock = yh.projected_shed(action, view)
        due = {}
        for item in PREMIUM:
            if item in selling_now:
                continue
            remaining = max(0, planned.get(item, 0) - advanced.get(item, 0))
            if remaining < MIN_FUTURE_QTY:
                continue
            quantity = min(max(0, int(stock.get(item, 0))), remaining, MAX_BATCH,
                           max(1, round(remaining * FRACTION)))
            if quantity <= 0 or len(action["market"]) >= MAX_ORDERS:
                continue
            action["market"].append(["SELL", item, quantity])
            due[item] = due.get(item, 0) + quantity
        if due:
            st["due_step"], st["due"] = nxt, due
            PREEMPT_COUNTS["turns"] += 1
            PREEMPT_COUNTS["units"] += sum(due.values())

    action["market"] = action["market"][:MAX_ORDERS]
    return action


def agent(observation, configuration=None):
    try:
        yh = _yh()
        base_action = yh.agent(observation, configuration)
    except Exception:
        GUARD_COUNTS["base_raise"] += 1
        return {"farmer": ["PASS"], "hands": [], "market": []}
    try:
        return _layer(yh, observation, copy.deepcopy(base_action))
    except Exception:
        GUARD_COUNTS["layer_raise"] += 1
        return base_action
