"""EXP-062 v6 (Claude-B 21:35 KST): opponent-gated glut lead (Sol idea): lead only after d157's race detector saw the rival sell >=G turns before our planned sale. L-family: glut lead. Real-loss finding: vs private 55be variants, in glut (price<=base) the variant sells
the tape-planned lot 1 step early (mostly hour 0) while d157 follows the tape (hour 1); d157 never leads in glut
(RACEGATE blocks the reservation; native lead is off in 288-695 and skipped at step%4==0).
Change: after d157's own reservation, for glutted items in ITEMS, reserve the tape's planned sells of the next K steps now
(same debt/suppression ledger as _r36_reserve). d157 bytes unchanged; tail override only. Claude 2026-09-30."""
import hashlib,json,pathlib
BASE=pathlib.Path('releases/exp035-d157/main.py').read_text()
TAIL='''

# ==== EXP-062 {name}: glut lead K={K} items={items} thr={T} gate(rival lead>={G}) (Claude 2026-09-30). d157 bytes above unchanged. ====
_E62_PARENT = [v for v in globals().values() if callable(v)][-1]
_E62_K = {K}
_E62_GATE = {G}
_E62_ITEMS = {items}
_E62_FROM, _E62_TO = {lo}, {hi}
_E62_REPORT = dict(glut_lead_units=0, glut_leads=0, glut_errors=0)
_E62_RESERVE = _r36_reserve


def _e62_glut_lead(obs, action):
    step = int(obs["step"])
    if not _E62_FROM <= step < _E62_TO:
        return action
    prices = obs["market"]["prices"]
    items = [i for i in _E62_ITEMS
             if i in V9_RACEGATE_BASE and prices.get(i, 0) <= V9_RACEGATE_BASE[i] * {T} + V9_RACEGATE_MARGIN]
    if not items:
        return action
    _g = _V9_RACE.get(int(obs["player"]))
    if not _g or _g.get("lead", -99) < _E62_GATE:
        _E62_REPORT["gated"] = _E62_REPORT.get("gated", 0) + 1
        return action
    native = _IMPL.chassis.players[int(obs["player"])]
    tape = _IMPL.chassis.routes[native["route"]]
    commands = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
    view = FarmView(obs)
    if any(len(c) > 1 and c[0] == "PLACE" and c[1] in ANIMAL_STRUCTURE
           and view.inv(i).get(c[1], 0) > 0 for i, c in enumerate(commands[:len(view.positions)])):
        return action
    stock = projected_shed(action, view)
    market = action.get("market", [])
    blocked = {{o[1] for o in market if len(o) > 1 and o[0] in ("SELL", "BUY_PRODUCT")}}
    blocked.update(c[1] for c in commands if len(c) > 1 and c[0] == "PICKUP")
    blocked.update(c[1] for queue in native["pending"].values() for pos, c in queue
                   if len(c) > 1 and c[0] == "PICKUP")
    debts = native["sell_state"].setdefault("r36_debts", {{}})
    end = min(_E62_TO - 1, step + _E62_K)
    for item in items:
        if item in blocked or view.prices.get(item, 0) < 2:
            continue
        available = max(0, int(stock.get(item, 0)))
        if not available or len(market) >= 10:
            continue
        reservations = []
        for due_step in range(step + 1, end + 1):
            future = tape[due_step]
            work = [future.get("farmer") or ["PASS"], *(future.get("hands") or [])]
            if any(len(c) > 1 and c[:2] == ["PICKUP", item] for c in work):
                break
            if any(len(o) > 1 and o[:2] == ["BUY_PRODUCT", item] for o in future.get("market", [])):
                break
            planned = sum(max(0, int(o[2])) for o in future.get("market", [])
                          if len(o) >= 3 and o[:2] == ["SELL", item])
            amount = min(available, max(0, planned - debts.get(due_step, {{}}).get(item, 0)))
            if amount:
                reservations.append((due_step, amount))
                available -= amount
            if not available:
                break
        qty = sum(q for _, q in reservations)
        if qty:
            market.append(["SELL", item, qty])
            for due, q in reservations:
                debt = debts.setdefault(due, {{}})
                debt[item] = debt.get(item, 0) + q
            _E62_REPORT["glut_lead_units"] += qty
            _E62_REPORT["glut_leads"] += 1
    action["market"] = market
    return action


def _r36_reserve(obs, action):
    action = _E62_RESERVE(obs, action)
    try:
        return _e62_glut_lead(obs, action)
    except Exception:
        _E62_REPORT["glut_errors"] += 1
        return action


def exp062_entry(obs, configuration=None):
    if int(obs.get("step", 0)) == 0:
        _E62_REPORT.update(glut_lead_units=0, glut_leads=0, glut_errors=0)
    return _E62_PARENT(obs, configuration)
exp062_entry.telemetry = _E62_REPORT
'''
PREM=("MILK","WOOL","STRAWBERRY")
ALL=("MILK","WOOL","STRAWBERRY","EGG","CARROT","TOMATO","MELON")
V={}
for name,K,items,lo,hi,T,G in [('L5g',5,PREM,192,696,1.0,1),('L4g',4,PREM,192,696,1.0,1)]:
    p=pathlib.Path(f'experiments/exp062/variants/{name}.py');p.write_text(BASE+TAIL.format(name=name,K=K,items=repr(items),lo=lo,hi=hi,T=T,G=G))
    V[name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'K':K,'items':items,'window':[lo,hi],'thr':T,'gate_lead':G}
json.dump(V,open('experiments/exp062/variants/manifest_v6.json','w'),indent=1)
print({k:v['sha256'][:12] for k,v in V.items()})
