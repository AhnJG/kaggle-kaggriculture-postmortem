# Robust scenario orderer: the rival's order schedule is fixed for each
# scenario while candidate permutations change. This avoids treating a
# candidate's hypothetical order as though the rival copies it immediately.
import itertools as _FP_IT

_FP_A_PARENT = agent
_FP_A_REPORT = {'eligible': 0, 'changed': 0, 'errors': 0, 'calls': 0}

def _fp_a_value(ours, rival_scenarios, inv0, our_stock, params):
    values = []
    revenues = []
    for rival in rival_scenarios:
        me, opp = _v44y_lockstep(ours, rival, inv0, our_stock,
                                 {k: 1000 for k in our_stock}, params)
        values.append(me - opp)
        revenues.append(me)
    return (sum(values) / len(values) + min(values)) / 2, sum(revenues) / len(revenues)

def _fp_a_reorder(obs, action):
    step = int(obs.get('step', 0))
    if step < 192 or step > 696:
        return action
    original = [list(o) if isinstance(o, (list, tuple)) else o
                for o in (action.get('market') or [])]
    slots = [i for i, o in enumerate(original)
             if o and len(o) >= 3 and o[0] == 'SELL' and int(o[2]) > 0]
    if len(slots) < 2 or len(slots) > 4 or len(original) > 10:
        return action
    stock = {k: max(0, int(v)) for k, v in projected_shed(action, FarmView(obs)).items()}
    for i in slots:
        item = original[i][1]
        if stock.get(item, 0) < sum(int(original[j][2]) for j in slots if original[j][1] == item):
            return action
    params = _v44y_params(obs)
    inv0 = {k: int(v) for k, v in obs['market']['inventory'].items()}
    # Current-order, one-slot-later, one-slot-earlier and reversed-sale
    # scenarios. These are bounded uncertainty scenarios, not predictions.
    rival0 = [list(o) if o else [] for o in original]
    rival1 = [[]] + rival0[:-1]
    rival2 = rival0[1:] + [[]]
    rival3 = [list(o) if o else [] for o in original]
    for i, o in zip(slots, reversed([original[i] for i in slots])):
        rival3[i] = list(o)
    rivals = [rival0, rival1, rival2, rival3]
    base_value, base_revenue = _fp_a_value(original, rivals, inv0, stock, params)
    best_value = base_value
    best = None
    for perm in _FP_IT.permutations([original[i] for i in slots]):
        cand = [list(o) if o else [] for o in original]
        for i, o in zip(slots, perm):
            cand[i] = list(o)
        if cand == original:
            continue
        value, revenue = _fp_a_value(cand, rivals, inv0, stock, params)
        if revenue >= base_revenue - 2 and value > best_value + 1:
            best_value, best = value, cand
    _FP_A_REPORT['eligible'] += 1
    if best is None:
        return action
    _FP_A_REPORT['changed'] += 1
    return dict(action, market=best)

def agent(obs, configuration=None):
    if int(obs.get('step', 0)) == 0:
        _FP_A_REPORT.update(eligible=0, changed=0, errors=0, calls=0)
    _FP_A_REPORT['calls'] += 1
    action = _FP_A_PARENT(obs, configuration)
    try:
        out = _fp_a_reorder(obs, action)
        if out is not action:
            state = _RACE_STATE.get(int(obs['player']))
            if state is not None and state.get('step') == int(obs['step']) and state.get('prev_action') is not None:
                state['prev_action'] = out
        return out
    except Exception:
        _FP_A_REPORT['errors'] += 1
        return action

kaggle_submission_agent = agent

def fp_a_entry(obs, configuration=None):
    return agent(obs, configuration)
