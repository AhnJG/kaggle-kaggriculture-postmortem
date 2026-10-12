"""Build frozen EXP-045 v2 one-site variants and the Stage A job split."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/exp045_sale"
PARENT = ROOT / "releases/exp035-d157/main.py"
EXPECTED = "94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e"
assert hashlib.sha256(PARENT.read_bytes()).hexdigest() == EXPECTED
source = PARENT.read_text()


def insert_once(text: str, anchor: str, insertion: str) -> tuple[str, int]:
    assert text.count(anchor) == 1, (anchor[:100], text.count(anchor))
    at = text.index(anchor) + len(anchor)
    return text[:at] + insertion + text[at:], text[:at].count("\n") + 1


ABLATIONS = {
    "K1": ("    action = _OR2_PARENT(observation, configuration)\n", "    return action  # EXP045 K1: bypass OR2 apply\n"),
    "K2": ("def agent(observation, configuration=None):\n    player, step = int(observation[\"player\"]), int(observation[\"step\"])\n    st = _V9_RACE.get(player)\n", "    return _V9_RACE_PARENT(observation, configuration)  # EXP045 K2\n"),
    "K3": ("def _s758_apply(observation,action):\n", "    return action  # EXP045 K3\n"),
    "K4": ("def _s793_reorder(obs,action,_it=_S793_IT):\n", "    return action  # EXP045 K4\n"),
    "K5": ("_HP_WINDOW = 4\ndef _v92_predict(obs, action, st):\n", "    return action  # EXP045 K5\n"),
    "K6": ("def _s738_advance(obs,action):\n", "    return action  # EXP045 K6\n"),
    "K7": ("def _v44y_reorder(obs, action):\n", "    return action  # EXP045 K7\n"),
    "K8": ("    action = _S928_PARENT(observation, configuration)\n", "    return action  # EXP045 K8\n"),
}


COMMON = '''

# EXP-045 v2: one outer sale rule after the frozen d157 wrapper.
import statistics as _e45_statistics
_E45_PARENT = exp029_entry
_E45_STATE = {}
_E45_REPORT = {'calls': 0, 'changed': 0, 'held': 0, 'deferred': 0, 'errors': 0}

def _e45_rival_stock(obs, state):
    p = int(obs['player']); step = int(obs['step'])
    or2 = _OR2_STATE.get(p)
    if or2 is not None and or2.get('step') == step:
        return or2['stock']
    # Fallback when OR2 has not initialized: the same tile and market-flow
    # reconstruction as OR2, using public observations only.
    rival = obs['farms'][1 - p]
    tiles = _or2_tiles(rival)
    inv = {i: int(obs['market']['inventory'].get(i, 0)) for i in ('WOOL', 'MILK')}
    prev = state.get('rival_prev')
    stock = state.setdefault('rival_stock', {'WOOL': 0, 'MILK': 0})
    if prev and prev['step'] == step - 1:
        for pos, old in prev['tiles'].items():
            kind, item, born, yield_before = old
            if item not in stock or yield_before <= 0: continue
            after = tiles.get(pos)
            if after and after[0] == kind and after[1] == item and after[2] == born and after[3] < yield_before:
                stock[item] += yield_before - after[3]
        draw = _or2_draw(prev['shops'], prev['step'])
        for item in stock:
            sold = inv[item] - prev['inv'][item] + draw.get(item, 0) - prev['own'].get(item, 0)
            stock[item] = max(0, stock[item] - max(0, sold))
    state['rival_prev'] = {'step': step, 'tiles': tiles, 'inv': inv,
                           'shops': list((obs.get('town') or {}).get('unlocked_shops') or []),
                           'own': {}}
    return stock

def _e45_own_record(obs, action, state):
    p = int(obs['player']); step = int(obs['step'])
    available = projected_shed(action, FarmView(obs))
    own = {}
    for order in (action.get('market') or [])[:10]:
        if len(order) >= 3 and order[0] == 'SELL' and order[1] in ('WOOL', 'MILK'):
            item = order[1]
            q = min(max(0, int(order[2])), max(0, int(available.get(item, 0)) - own.get(item, 0)))
            own[item] = own.get(item, 0) + q
    prev = state.get('rival_prev')
    if prev is not None and prev['step'] == step:
        prev['own'] = own
    or2 = _OR2_STATE.get(p)
    if or2 is not None and or2.get('step') == step and or2.get('prev') is not None:
        for item in ('WOOL', 'MILK'):
            or2['prev']['own'][item] = own.get(item, 0)

def _e45_sync(obs, action):
    st = _RACE_STATE.get(int(obs['player']))
    if st is not None and st.get('prev_action') is not None and st.get('step') == int(obs['step']):
        st['prev_action'] = action

def _e45_price_after_consumption(obs, item):
    step = int(obs['step'])
    shops = list((obs.get('town') or {}).get('unlocked_shops') or [])
    inv = int(obs['market']['inventory'].get(item, 0))
    for t in range(step, min(719, step + 8)):
        inv = max(0, inv - _or2_draw(shops, t).get(item, 0))
    params = {k: dict(v) for k, v in _R37_MARKET_PARAMS.items()}
    for k, patch in (obs['market'].get('params') or {}).items():
        if k in params: params[k].update(patch)
    return _r37_market_price(item, inv, params)

def exp045_entry(obs, configuration=None):
    step = int(obs['step']); p = int(obs['player'])
    state = _E45_STATE.get(p)
    if state is None or step <= state['step']:
        state = _E45_STATE[p] = {'step': -1, 'prices': {'WOOL': [], 'MILK': []},
                                 'owed': {'WOOL': 0, 'MILK': 0}}
        if step == 0:
            _E45_REPORT.update(calls=0, changed=0, held=0, deferred=0, errors=0)
    _E45_REPORT['calls'] += 1
    action = _E45_PARENT(obs, configuration)
    try:
        return _e45_apply(obs, action, state)
    except Exception:
        _E45_REPORT['errors'] += 1
        return action

exp045_entry.telemetry = _E45_REPORT
'''


RULES = {
    "G_A": '''
def _e45_apply(obs, action, state):
    step = int(obs['step'])
    stock = _e45_rival_stock(obs, state)
    state['step'] = step
    if sum(int(v or 0) for v in obs['private']['shed'].values()) >= 92:
        _e45_own_record(obs, action, state)
        return action
    market = []
    held = 0
    for order in action.get('market') or []:
        item = order[1] if len(order) >= 2 else None
        if len(order) >= 3 and order[0] == 'SELL' and item in ('WOOL', 'MILK'):
            if step >= (684 if item == 'WOOL' else 696):
                market.append(order); continue
            rival_min, factor = (4, 1.15) if item == 'WOOL' else (5, 1.08)
            now = int(obs['market']['prices'].get(item, 0))
            if int(stock.get(item, 0)) >= rival_min and now < factor * _e45_price_after_consumption(obs, item):
                held += max(0, int(order[2])); continue
        market.append(order)
    result = dict(action, market=market) if held else action
    _E45_REPORT['held'] += held
    if held: _E45_REPORT['changed'] += 1; _e45_sync(obs, result)
    _e45_own_record(obs, result, state)
    return result
''',
    "G_B": '''
def _e45_apply(obs, action, state):
    step = int(obs['step'])
    stock = _e45_rival_stock(obs, state)
    state['step'] = step
    prices = obs['market']['prices']
    history = state['prices']
    full = sum(int(v or 0) for v in obs['private']['shed'].values()) >= 92
    market = []
    held = 0
    for order in action.get('market') or []:
        item = order[1] if len(order) >= 2 else None
        if not full and len(order) >= 3 and order[0] == 'SELL' and item in ('WOOL', 'MILK'):
            if step < (684 if item == 'WOOL' else 696) and int(stock.get(item, 0)) >= 4 and history[item]:
                factor = 1.15 if item == 'WOOL' else 1.08
                if int(prices.get(item, 0)) < factor * _e45_statistics.median(history[item][-24:]):
                    held += max(0, int(order[2])); continue
        market.append(order)
    for item in history:
        history[item].append(int(prices.get(item, 0)))
        if len(history[item]) > 24: del history[item][:-24]
    result = dict(action, market=market) if held else action
    _E45_REPORT['held'] += held
    if held: _E45_REPORT['changed'] += 1; _e45_sync(obs, result)
    _e45_own_record(obs, result, state)
    return result
''',
    "B6": '''
def _e45_apply(obs, action, state):
    step = int(obs['step']); state['step'] = step
    full = sum(int(v or 0) for v in obs['private']['shed'].values()) >= 92
    owed = state['owed']
    if full:
        owed.update(WOOL=0, MILK=0)
        return action
    market = [list(o) for o in (action.get('market') or [])]
    available = projected_shed(action, FarmView(obs))
    changed = False
    for item in ('WOOL', 'MILK'):
        if step >= (684 if item == 'WOOL' else 696):
            owed[item] = 0
            continue
        original = sum(max(0, int(o[2])) for o in market if len(o) >= 3 and o[:2] == ['SELL', item])
        requested = original + owed[item]
        capacity = min(6, max(0, int(available.get(item, 0))))
        allowed = min(requested, capacity)
        remaining = allowed
        new_market = []
        for order in market:
            if len(order) >= 3 and order[:2] == ['SELL', item]:
                take = min(max(0, int(order[2])), remaining)
                remaining -= take
                if take > 0:
                    order[2] = take; new_market.append(order)
                if take != int(order[2]) or take == 0: changed = True
            else:
                new_market.append(order)
        market = new_market
        if remaining > 0 and len(market) < 10:
            market.append(['SELL', item, remaining])
            changed = True
            remaining = 0
        owed[item] = max(0, requested - (allowed - remaining))
        if owed[item] > 0: _E45_REPORT['deferred'] += owed[item]
    if market != (action.get('market') or []): changed = True
    result = dict(action, market=market) if changed else action
    if changed: _E45_REPORT['changed'] += 1; _e45_sync(obs, result)
    if changed: _e45_own_record(obs, result, state)
    return result
''',
}

ENTRY = '''
def exp045_final_agent(observation, configuration=None):
    return exp045_entry(observation, configuration)
agent = exp045_final_agent
'''


def build() -> None:
    variants = OUT / "variants"
    variants.mkdir(parents=True, exist_ok=True)
    manifest = {"parent": str(PARENT.relative_to(ROOT)), "parent_sha256": EXPECTED,
                "variants": {}}
    for name, (anchor, addition) in ABLATIONS.items():
        code, line = insert_once(source, anchor, addition)
        path = variants / f"{name}.py"
        path.write_text(code)
        manifest["variants"][name] = {"path": str(path.relative_to(ROOT)),
                                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                      "changed_lines": len(addition.splitlines()),
                                      "location": f"{path.relative_to(ROOT)}:{line}"}
    for name, rule in RULES.items():
        code = source + COMMON + rule + ENTRY
        path = variants / f"{name}.py"
        path.write_text(code)
        line = source.count("\n") + 2
        manifest["variants"][name] = {"path": str(path.relative_to(ROOT)),
                                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                      "changed_lines": len((COMMON + rule + ENTRY).splitlines()),
                                      "location": f"{path.relative_to(ROOT)}:{line}"}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    meta = {m["episode"]: m for m in json.loads((ROOT / "experiments/exp041_top2400/meta.json").read_text())}
    split = json.loads((ROOT / "experiments/exp041_top2400/team-split.json").read_text())
    selected = sorted((m for m in meta.values() if m["team"] in split["select_teams"]), key=lambda m: m["episode"])
    assert len(selected) == 595 and not any(9000 <= m["seed"] <= 9599 for m in selected)
    jobs = [[name, manifest["variants"][name]["path"], f"X{m['episode']}",
             f"experiments/exp041_top2400/tapes/X{m['episode']}.py", m["seed"], m["our_seat"]]
            for m in selected for name in (*ABLATIONS, *RULES)]
    assert len(jobs) == 11 * 595 and len({(j[0], j[2], j[4], j[5]) for j in jobs}) == len(jobs)
    kaggle = [j for i, j in enumerate(jobs) if i % 5 < 3]
    mac = [j for i, j in enumerate(jobs) if i % 5 >= 3]
    for name, batch in (("kaggle", kaggle), ("mac", mac)):
        (OUT / f"jobs-A-{name}.json").write_text(json.dumps(batch, separators=(",", ":")) + "\n")
    print(len(jobs), len(kaggle), len(mac))


if __name__ == "__main__":
    build()
