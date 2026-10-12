"""Offline baseline accounting and conditional upper bounds; no candidate policy."""
import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as K
from tools.reproduce_replay import ENGINE_SHA, projection, tape_agent
from tools.postmortem import build_report

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--replay')
    p.add_argument('--seat', type=int, default=0)
    p.add_argument('--seed', type=int, default=2014)
    p.add_argument('--rival', default='releases/public-ozer-v53-exact/main.py')
    p.add_argument('--out', required=True)
    args = p.parse_args()
    assert sha(K.__file__) == ENGINE_SHA
    parent = 'releases/f0-omw-adv-exp017/main.py'
    rival = args.rival
    source = json.loads(Path(args.replay).read_text()) if args.replay else None
    seed = source['info']['seed'] if source else args.seed
    config = dict(source['configuration']) if source else {'episodeSteps': 720}
    config['seed'] = seed
    originals = {name: getattr(K, name) for name in (
        '_process_market', '_commit_unit', '_town_consume', '_do_hire', '_do_buy_land',
        '_apply_unit_action', '_drop_inventories_to_shed')}
    events, premarkets, demands = [], [], Counter()
    ctx = dict(unit_seat=-1, drop_seat=-1)
    production = [Counter(), Counter()]
    used = [Counter(), Counter()]
    discarded = [Counter(), Counter()]

    def stock(private):
        result = Counter(private['shed'])
        for inv in private['inventories']:
            result.update(inv)
        return result

    def unit(farm, private, idx, action, *rest):
        if idx == 0:
            ctx['unit_seat'] += 1
        seat = ctx['unit_seat']
        before = stock(private)
        result = originals['_apply_unit_action'](farm, private, idx, action, *rest)
        after = stock(private)
        op = action[0] if action else 'PASS'
        if op in ('HARVEST', 'COLLECT_FERTILIZER'):
            production[seat].update(after-before)
        elif op == 'DROP':
            discarded[seat].update(before-after)
        else:
            used[seat].update(before-after)
        return result

    def drop(private, capacity):
        ctx['drop_seat'] += 1
        before = stock(private)
        result = originals['_drop_inventories_to_shed'](private, capacity)
        discarded[ctx['drop_seat']].update(before-stock(private))
        return result

    def market(state, env):
        ctx.update(step=int(state[0].observation.step),
                   farms=state[0].observation.farms)
        premarkets.append(copy.deepcopy(state))
        ctx.update(unit_seat=-1, drop_seat=-1)
        return originals['_process_market'](state, env)

    def commit(op, item, price, farm, private, market, shed_capacity=100):
        seat = next(i for i, f in enumerate(ctx['farms']) if f is farm)
        ok = originals['_commit_unit'](op, item, price, farm, private, market, shed_capacity)
        if ok:
            events.append(dict(step=ctx['step'], seat=seat, op=op, item=item, price=price))
        return ok

    def atomic(name, farm, *rest):
        seat = next(i for i, f in enumerate(ctx['farms']) if f is farm)
        before = farm['money']
        result = originals[name](farm, *rest)
        if farm['money'] != before:
            events.append(dict(step=ctx['step'], seat=seat, op=name, item='',
                               price=before-farm['money']))
        return result

    def town(env, state, step):
        inv = state[0].observation.market['inventory']
        before = dict(inv)
        result = originals['_town_consume'](env, state, step)
        demands.update({it: before[it]-inv[it] for it in K.PRODUCTS})
        return result

    K._process_market = market
    K._commit_unit = commit
    K._town_consume = town
    K._apply_unit_action = unit
    K._drop_inventories_to_shed = drop
    K._do_hire = lambda farm, *rest: atomic('_do_hire', farm, *rest)
    K._do_buy_land = lambda farm, *rest: atomic('_do_buy_land', farm, *rest)
    env = make('kaggriculture', configuration=config)
    agents = [tape_agent(source, s) for s in (0, 1)] if source else [parent, rival]
    if not source and args.seat == 1:
        agents.reverse()
    try:
        env.run(agents)
    finally:
        for name, fn in originals.items():
            setattr(K, name, fn)
    assert len(env.steps) == 720
    assert [s.status for s in env.steps[-1]] == ['DONE', 'DONE']
    matches = None
    if source:
        matches = sum(projection(source['steps'][t][s]) == projection(env.steps[t][s])
                      for t in range(720) for s in (0, 1))
        assert matches == 1440, matches
    seat = args.seat
    own = [e for e in events if e['seat'] == seat]
    sales = [e for e in own if e['op'] == 'SELL']
    revenue = sum(e['price'] for e in sales)
    costs = Counter()
    for e in own:
        if e['op'] != 'SELL':
            costs[e['op']] += e['price']
    initial = env.steps[0][0].observation.farms[seat]['money']
    final = env.steps[-1][seat].reward
    assert initial + revenue - sum(costs.values()) == final
    all_buys = Counter(e['item'] for e in events if e['op'] == 'BUY_PRODUCT')
    own_buys = sum(e['op'] == 'BUY_PRODUCT' for e in own)
    rows = []
    terminal = stock(env.steps[-1][seat].observation.private)
    params = env.steps[0][0].observation.market.get('params', K.MARKET_PARAMS)
    for it in K.PRODUCTS:
        fills = [e for e in sales if e['item'] == it]
        n = len(fills)
        # All observed demand and BOTH players' purchases are granted up front.
        # Rival sales, production dates, shed cap, slots and cash constraints vanish.
        inventory = params[it]['I0'] - demands[it] - all_buys[it]
        unit_ceiling = K.market_price(it, inventory, params)
        integrated = 0
        for _ in range(n):
            price = K.market_price(it, inventory, params)
            integrated += price
            inventory += price > 1
        actual = sum(e['price'] for e in fills)
        recovered = discarded[seat][it] + terminal[it]
        rescued_bound = integrated
        for _ in range(recovered):
            price = K.market_price(it, inventory, params)
            rescued_bound += price
            inventory += price > 1
        rows.append(dict(item=it, sold=n, revenue=actual,
                         harvested=production[seat][it], used=used[seat][it],
                         discarded=discarded[seat][it], terminal=terminal[it],
                         rescued_bound=rescued_bound,
                         town_demand=demands[it], both_buy_units=all_buys[it],
                         unit_ceiling=unit_ceiling, envelope=n*unit_ceiling,
                         own_impact_bound=integrated, gap=integrated-actual))
    fixed_costs = sum(costs.values()) - costs['BUY_PRODUCT']
    # At least $1 per observed product purchase; don't freeze their original price.
    ceiling = initial + sum(r['own_impact_bound'] for r in rows) - fixed_costs - own_buys
    envelope = initial + sum(r['envelope'] for r in rows) - fixed_costs - own_buys
    cash_items = [r for r in rows if r['item'] not in ('WHEAT', 'FERTILIZER')]
    cash_only_bound = final + sum(r['rescued_bound']-r['revenue'] for r in cash_items)
    assert envelope >= ceiling >= final
    post = build_report(str(agents[0]), str(agents[1]), seed, env.steps, top_n=3)
    out = Path(args.out)
    result = dict(seed=seed, seat=seat, initial_cash=initial, final_cash=final,
                  rival_cash=env.steps[-1][1-seat].reward, revenue=revenue, costs=dict(costs),
                  own_buy_units=own_buys, bound=ceiling, gap=ceiling-final,
                  envelope_bound=envelope, products=rows, replay_projection_matches=matches,
                  cash_only_bound=cash_only_bound,
                  cash_only_gap=cash_only_bound-final,
                  harvested_fixed_bound=initial+sum(r['rescued_bound'] for r in rows)-fixed_costs-own_buys,
                  engine_sha=sha(K.__file__), runner_sha=sha(__file__),
                  source_sha=sha(args.replay) if source else None,
                  parent_sha=sha(parent), rival_sha=sha(rival),
                  parent_path=parent, rival_path=rival,
                  steps=720, statuses=['DONE', 'DONE'],
                  divergence_day=post['divergence_day'],
                  worst_days=[{k:v for k,v in d.items() if k!='actions'} for d in post['worst_days']])
    out.with_suffix('.events.json').write_text(json.dumps(events))
    out.with_suffix('.markets.json').write_text(json.dumps(premarkets))
    out.with_suffix('.postmortem.json').write_text(json.dumps(post, indent=2))
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)

if __name__ == '__main__':
    main()
