"""EXP-005 probe X1 (team Sian, 2026-09-11). Our own file; the parent files are unmodified.

Parent: yhay81 "Shop Router 0909" (Apache-2.0, LICENSE.txt), loaded byte-identical from
yh_base.py (= parent main.py) and actions.json.
One change: for the non-input products below, the parent's SELL lines are replaced by a SELL of
the parent's projected shed stock on every turn (price >= 2), ordered by price*qty descending,
all market lines capped at 10. Step 718 keeps the parent's liquidation.
Guards never alter an action unless an exception occurs; each guard has its own counter.
"""
import importlib.util
from pathlib import Path

THIN = ("MELON", "WOOL", "MILK", "STRAWBERRY", "TOMATO", "EGG", "CARROT")
GUARD_COUNTS = {"base_raise": 0, "layer_raise": 0}
_STATE = {"base": None}
_PASS = {"farmer": ["PASS"], "hands": [], "market": []}


def _base():
    if _STATE["base"] is None:
        folder = Path(agent.__code__.co_filename).resolve().parent
        spec = importlib.util.spec_from_file_location("exp005_yh_base", folder / "yh_base.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _STATE["base"] = mod
    return _STATE["base"]


def _layer(base, observation, action):
    if int(observation["step"]) >= base.LAST_STEP:
        return action
    view = base.FarmView(observation)
    stock = base.projected_shed(action, view)
    keep = [o for o in action.get("market", [])
            if not (o and o[0] == "SELL" and len(o) > 1 and o[1] in THIN)]
    sells = [["SELL", it, stock.get(it, 0)] for it in THIN
             if stock.get(it, 0) > 0 and int(view.prices.get(it, 0)) >= 2]
    sells.sort(key=lambda o: -int(view.prices.get(o[1], 0)) * o[2])
    action["market"] = (keep + sells)[:base.MAX_ORDERS]
    return action


def agent(observation, configuration=None):
    try:
        base = _base()
        action = base.agent(observation, configuration)
    except Exception:
        GUARD_COUNTS["base_raise"] += 1
        return {"farmer": ["PASS"], "hands": [], "market": []}
    try:
        return _layer(base, observation, action)
    except Exception:
        GUARD_COUNTS["layer_raise"] += 1
        return action
