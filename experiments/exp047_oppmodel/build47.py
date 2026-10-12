"""Build EXP-047 variant from frozen d157 and public 55be exact bytes."""
from pathlib import Path
import base64
import hashlib
import zlib

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "variants"
BASE = ROOT / "releases/exp035-d157/main.py"
SHADOW = ROOT / "releases/public-dpnew-55be5d5f-exact/main.py"
base = BASE.read_bytes()
shadow = SHADOW.read_bytes()
assert hashlib.sha256(base).hexdigest() == "94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e"
assert hashlib.sha256(shadow).hexdigest() == "55be5d5f124c8daaaa63c1a29ba4aab096004909666f04748007603c67b7d2a8"
payload = base64.b85encode(zlib.compress(shadow, 9)).decode("ascii")

addition = r'''

# EXP-047: separate exact 55be namespace, fed only public state and an OR2 shed estimate.
import base64 as _exp047_b64
import zlib as _exp047_zlib
_EXP047_SHADOW_BYTES = _exp047_zlib.decompress(_exp047_b64.b85decode(_EXP047_PAYLOAD))
_EXP047_SHADOW_NS = {'__name__': 'exp047_shadow'}
exec(compile(_EXP047_SHADOW_BYTES, '<55be-exact-shadow>', 'exec'), _EXP047_SHADOW_NS)
_EXP047_SHADOW_AGENT = _EXP047_SHADOW_NS['kaggle_submission_agent']
_EXP047_PARENT = agent
_EXP047_PLAN = [None] * 720
_IMPL.chassis.cfg['front_run'] = True
_IMPL.chassis.opponent_plan = _EXP047_PLAN
_EXP047_REPORT = {'predictions': 0, 'sell_events': 0, 'shadow_errors': 0,
                  'plan_steps': 0, 'hook_changed': 0, 'stock_errors': 0}
_EXP047_HOOK_ORIGINAL = _IMPL.chassis._front_run
def _exp047_counted_hook(action, view, projected, route, step, next_sup):
    before = tuple(tuple(o) for o in (action.get('market') or []))
    _EXP047_HOOK_ORIGINAL(action, view, projected, route, step, next_sup)
    _EXP047_REPORT['hook_changed'] += before != tuple(tuple(o) for o in (action.get('market') or []))
_IMPL.chassis._front_run = _exp047_counted_hook

def _exp047_stock_now(observation, seat, step):
    """Apply OR2's visible previous-to-current delta without mutating its state."""
    st = _OR2_STATE.get(seat)
    stock = dict(st['stock']) if st else {i: 0 for i in _OR2_ITEMS}
    if not st or step <= 0 or st.get('step') != step - 1:
        return stock
    prev = st.get('prev')
    if not prev or prev.get('step') != step - 1:
        return stock
    rival = observation['farms'][1 - seat]
    tiles = _or2_tiles(rival)
    inv_now = observation['market']['inventory']
    for pos, old in prev['tiles'].items():
        kind, item, born, y = old
        if y <= 0:
            continue
        new = tiles.get(pos)
        got = 0
        if kind == 'P' and item not in _OR2_ONGOING:
            if (new is None and not _OR2_WEED(rival, pos)) or (new is not None and new[2] != born):
                got = y
        elif new is not None and new[0] == kind and new[1] == item and new[2] == born and new[3] < y:
            if step % 24 != 0:
                got = y - new[3]
            elif new[3] == 0:
                got = y
        if got > 0:
            stock[item] = stock.get(item, 0) + got
    draw = _or2_draw(prev['shops'], prev['step'])
    for item in _OR2_ITEMS:
        if prev['prices'].get(item, 0) <= 1:
            continue
        moved = int(inv_now.get(item, 0)) - prev['inv'][item] + draw.get(item, 0) - prev['own'].get(item, 0)
        if moved > 0:
            stock[item] = max(0, stock.get(item, 0) - moved)
    return stock

def _exp047_predict(observation, configuration):
    step = int(observation['step'])
    seat = int(observation['player'])
    stock = _exp047_stock_now(observation, seat, step)
    rival = 1 - seat
    # One-step persistence: public farms/market/town and OR2 stock are held at step t;
    # only step/day/hour advance. No hidden seeds, worker cargo, or RNG is inferred.
    future = dict(observation)
    future.update(player=rival, step=step + 1, day=(step + 1) // 24,
                  hour=(step + 1) % 24,
                  private={'shed': stock, 'seeds': {},
                           'inventories': [{} for _ in range(1 + len(observation['farms'][rival]['hands']))]})
    predicted = _EXP047_SHADOW_AGENT(future, configuration)
    sells = [list(o) for o in (predicted.get('market') or [])[:10]
             if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == 'SELL'
             and o[1] in FRONT_RUN_ITEMS and int(o[2]) > 0]
    return {'farmer': ['PASS'], 'hands': [], 'market': sells}

def exp047_entry(observation, configuration=None):
    try:
        step = int(observation['step'])
        if step == 0:
            _EXP047_PLAN[:] = [None] * 720
            for k in _EXP047_REPORT:
                _EXP047_REPORT[k] = 0
            # Reset shadow's per-game state via its normal step-zero entry.
            zero = dict(observation)
            rival = 1 - int(observation['player'])
            zero.update(player=rival, private={'shed': {i: 0 for i in _OR2_ITEMS},
                                               'seeds': {},
                                               'inventories': [{} for _ in range(1 + len(observation['farms'][rival]['hands']))]})
            _EXP047_SHADOW_AGENT(zero, configuration)
        if 0 <= step < 718:
            try:
                _EXP047_PLAN[step + 1] = _exp047_predict(observation, configuration)
                _EXP047_REPORT['predictions'] += 1
                _EXP047_REPORT['sell_events'] += bool(_EXP047_PLAN[step + 1]['market'])
                _EXP047_REPORT['plan_steps'] += 1
            except Exception:
                _EXP047_PLAN[step + 1] = None
                _EXP047_REPORT['shadow_errors'] += 1
    except Exception:
        _EXP047_REPORT['stock_errors'] += 1
    action = _EXP047_PARENT(observation, configuration)
    return action

exp047_entry.telemetry = _EXP047_REPORT
agent = exp047_entry
kaggle_submission_agent = exp047_entry
'''

OUT.mkdir(exist_ok=True)
source = base + ("\n_EXP047_PAYLOAD = " + repr(payload) + "\n" + addition).encode()
target = OUT / "hook.py"
target.write_bytes(source)
compile(source, str(target), "exec")
print(target, hashlib.sha256(source).hexdigest(), len(source))
