
# ==== SLOT2-X TX layer (Claude 2026-09-29). d157 bytes above unchanged. ====
# Fritz-style: from day D0, K tiles that the parent tape uses for WHEAT become TOMATO tiles.
# Parent units that stand on a TX tile get tomato ops (plant/water/harvest/fertilize/dig weed);
# movement and shed/market logic stay the parent's. Optional wheat top-up buys keep feed stock.
_TX_PARENT = [v for v in globals().values() if callable(v)][-1]
_TX_CFG = __TX_CFG__
_TX_S = {'tiles': [], 'chosen': False, 'released': set()}
_TX_R = {'plant': 0, 'water': 0, 'harvest': 0, 'fert': 0, 'dig': 0, 'seedbuy': 0, 'wbuy': 0, 'sell': 0, 'err': 0}
_TX_TILEOPS = ('PLANT', 'WATER', 'HARVEST', 'FERTILIZE', 'DIG', 'PASS')
def _tx_g(o, k, d=None):
    return o.get(k, d) if isinstance(o, dict) else getattr(o, k, d)
def _tx_choose(fm):
    cand = []
    for y, row in enumerate(fm['tiles']):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get('kind') == 'PLANT' and t.get('crop') == 'WHEAT':
                cand.append((0, y, x))
    cand.sort()
    return [(x, y) for _, y, x in cand[:_TX_CFG['K']]]
def _tx_apply(obs, action):
    step = int(_tx_g(obs, 'step', 0)); day, hour = divmod(step, 24)
    seat = int(_tx_g(obs, 'player', 0)); fm = _tx_g(obs, 'farms')[seat]; pr = _tx_g(obs, 'private')
    if step == 0:
        _TX_S.update(tiles=[], chosen=False, released=set())
        for k in _TX_R: _TX_R[k] = 0
    if not _TX_S['chosen'] and day >= _TX_CFG['D0']:
        _TX_S['tiles'] = _tx_choose(fm); _TX_S['chosen'] = True
    T = [xy for xy in _TX_S['tiles'] if xy not in _TX_S['released']] if step < 700 else []
    action = dict(action); market = list(action.get('market') or [])
    cap = _TX_CFG.get('SHEEPCAP')
    if cap is not None and market:
        have = sum(1 for row in fm['tiles'] for t in row if isinstance(t, dict) and t.get('animal') == 'SHEEP') + int(_tx_g(pr, 'shed', {}).get('SHEEP', 0)) + sum(int(iv.get('SHEEP', 0)) for iv in _tx_g(pr, 'inventories', []))
        nm = []
        for o in market:
            if o and o[:2] == ['BUY_ANIMAL', 'SHEEP']:
                q = min(int(o[2]) if len(o) > 2 else 1, max(0, cap - have))
                if q <= 0: _TX_R['sheepcut'] = _TX_R.get('sheepcut', 0) + 1; continue
                have += q; o = ['BUY_ANIMAL', 'SHEEP', q]
            nm.append(o)
        market = nm
    seeds = int(_tx_g(pr, 'seeds', {}).get('TOMATO', 0)); invs = _tx_g(pr, 'inventories', [])
    units = [list(fm['farmer'])] + [list(h) for h in fm['hands']]
    cmds = [action.get('farmer', ['PASS'])] + list(action.get('hands') or [])
    tape_tom = sum(1 for c in cmds if isinstance(c, list) and c[:2] == ['PLANT', 'TOMATO'])
    avail = seeds - tape_tom; used = set(); changed = False
    tset = set(T)
    for i, pos in enumerate(units):
        if i >= len(cmds): break
        xy = (pos[0], pos[1])
        if xy not in tset or xy in used: continue
        c = cmds[i]
        if not isinstance(c, list) or not c or c[0] not in _TX_TILEOPS: continue
        t = fm['tiles'][xy[1]][xy[0]]; new = None
        if t is None:
            if day <= _TX_CFG['LAST'] and avail > 0: new = ['PLANT', 'TOMATO']; avail -= 1; _TX_R['plant'] += 1
            elif day > _TX_CFG['LAST']: _TX_S['released'].add(xy); continue
            else: continue
        elif isinstance(t, dict) and t.get('kind') == 'WEED':
            new = ['DIG']; _TX_R['dig'] += 1
        elif isinstance(t, dict) and t.get('kind') == 'PLANT' and t.get('crop') == 'TOMATO':
            y_u = int(t.get('yield_units', 0)); inv = invs[i] if i < len(invs) else {}
            if y_u >= 3 or (y_u > 0 and t.get('watered_today')): new = ['HARVEST']; _TX_R['harvest'] += 1
            elif not t.get('watered_today'): new = ['WATER']; _TX_R['water'] += 1
            elif _TX_CFG['FERT'] and inv.get('FERTILIZER', 0) > 0 and t.get('fertilized_until_day', -1) < day and day - t.get('planted_day', day) >= 6:
                new = ['FERTILIZE']; _TX_R['fert'] += 1
            elif y_u > 0: new = ['HARVEST']; _TX_R['harvest'] += 1
            else: new = ['PASS'] if c[0] in ('DIG', 'PLANT') else None
        else:
            continue
        if new is not None and new != c:
            cmds[i] = new; changed = True
        used.add(xy)
    if changed:
        action['farmer'] = cmds[0]; action['hands'] = cmds[1:]
    shed = _tx_g(pr, 'shed', {}); money = float(fm.get('money', 0))
    if day <= _TX_CFG['LAST'] and len(market) < 10:
        need = sum(1 for (x, y) in T if fm['tiles'][y][x] is None or (_TX_CFG.get('PREBUY', 1) and isinstance(fm['tiles'][y][x], dict) and fm['tiles'][y][x].get('crop') == 'WHEAT'))
        n = min(need - seeds, int((money - 300) // 50))
        if n > 0:
            market.append(['BUY_SEED', 'TOMATO', n]); _TX_R['seedbuy'] += n
    if _TX_CFG['WBUY'] and hour == 2 and len(market) < 10 and int(shed.get('WHEAT', 0)) < _TX_CFG['WBUY'] and money > 3000:
        market.append(['BUY_PRODUCT', 'WHEAT', _TX_CFG['WBUY'] - int(shed.get('WHEAT', 0))]); _TX_R['wbuy'] += 1
    if hour == _TX_CFG['SELLH'] and _TX_CFG.get('SELLFROM', 0) <= day <= _TX_CFG.get('SELLDAY', 99) and len(market) < 10 and int(shed.get('TOMATO', 0)) > 0 and not any(o and o[:2] == ['SELL', 'TOMATO'] for o in market):
        market.append(['SELL', 'TOMATO', int(shed.get('TOMATO', 0))]); _TX_R['sell'] += 1
    action['market'] = market
    return action
_TX_V219Q = globals().get('_v219_qualifies')
def _v219_qualifies(obs, native):
    if not _TX_CFG.get('V219FIX') or _TX_V219Q is None:
        return _TX_V219Q(obs, native)
    try:
        p = int(obs['player']); T = set(_TX_S['tiles'])
        farms = [dict(f) for f in obs['farms']]
        farms[p]['tiles'] = [[(None if ((x, y) in T and isinstance(t, dict) and t.get('crop') == 'TOMATO') else t) for x, t in enumerate(row)] for y, row in enumerate(obs['farms'][p]['tiles'])]
        pr = dict(obs['private']); pr['seeds'] = dict(pr['seeds']); pr['shed'] = dict(pr['shed'])
        pr['seeds']['TOMATO'] = 0; pr['shed']['TOMATO'] = 0
        o2 = dict(obs); o2['farms'] = farms; o2['private'] = pr
        return _TX_V219Q(o2, native)
    except Exception:
        _TX_R['err'] += 1
        return _TX_V219Q(obs, native)
def slot2x_entry(obs, configuration=None):
    action = _TX_PARENT(obs, configuration)
    try:
        return _tx_apply(obs, action)
    except Exception:
        _TX_R['err'] += 1
        return action
slot2x_entry.telemetry = _TX_R
