"""Resume verification of saved analysis; no agent games or release writes."""
import hashlib
import json
from collections import Counter
from pathlib import Path

import analyze as A

H = Path(__file__).resolve().parent
checks = 0


def check(ok, label):
    global checks
    assert ok, label
    checks += 1


def read(name):
    return json.loads((H / name).read_text())


events = read('baseline_fills.json')
q1, q2 = read('q1.json'), read('q2_fixed_fills.json')
check([{k: v for k, v in e.items() if k != 'slot'} for e in events]
      == [e for e in A.OLD_EVENTS if not e['op'].startswith('_do_')], 'source fills')
check(A.DEMAND == read('demand.json'), 'demand snapshots')
unlock = []
previous = []
for t, states in enumerate(A.MARKETS):
    shops = states[0]['observation']['town']['unlocked_shops']
    if shops != previous:
        unlock.append(dict(step=t, shop=shops[-1], instances=len(shops)))
        previous = shops
    for item in A.K.PRODUCTS:
        if t + 1 < len(A.MARKETS):
            flow = sum((1 if e['price'] > 1 else 0) if e['op'] == 'SELL' else -1
                       for e in events if e['step'] == t and e['item'] == item
                       and e['op'] in ('SELL', 'BUY_PRODUCT'))
            before = states[0]['observation']['market']['inventory'][item]
            after = A.MARKETS[t+1][0]['observation']['market']['inventory'][item]
            check(after == before + flow - A.DEMAND[t][item], f'flow {t} {item}')
for row in q1:
    item = row['item']
    check(row['absorption'] == sum(d[item] for d in A.DEMAND), f'demand {item}')
    check(row['sales'] == [sum(e['seat'] == s and e['item'] == item and e['op'] == 'SELL'
                              for e in events) for s in (0, 1)], f'sales {item}')
print('Q1 VERIFIED', json.dumps(q1), flush=True)
for row in q2:
    for key, spread in [('actual', False), ('spread', True)]:
        check(A.isolated(row['item'], events, spread) == row[key], f'Q2 {key} {row["item"]}')


def fixed_market(priority=(), replace_melon=False):
    """Price-only replay: actual fill quantities; no storage/cash feasibility claim."""
    inv = dict.fromkeys(A.K.PRODUCTS, 10000)
    rev = [Counter(), Counter()]
    cost = [Counter(), Counter()]
    changed, quotes, remaining = 0, [], 42
    # Last 42 MELON units -> same-slot CARROT units: production estimate only.
    replacement = set()
    if replace_melon:
        for index in reversed(range(len(events))):
            e = events[index]
            if e['seat'] == 0 and e['op'] == 'SELL' and e['item'] == 'MELON' and remaining:
                replacement.add(index)
                remaining -= 1
    for t, states in enumerate(A.MARKETS):
        queues = []
        for seat in (0, 1):
            queues.append([[] for _ in states[seat]['action'].get('market', [])[:10]])
        for index, e in enumerate(events):
            if e['step'] == t and e['op'] in ('SELL', 'BUY_PRODUCT'):
                item = e['item']
                if index in replacement:
                    item = 'CARROT'
                queues[e['seat']][e['slot']].append((e['op'], item))
        native = states[0]['action'].get('market', [])[:10]
        # Reorder SELL-only prefix. Funding/buy/fixed-price order positions stay fixed.
        end = next((i for i, o in enumerate(native) if not o or o[0] != 'SELL'), len(native))
        buys = {o[1] for o in native if len(o) > 1 and o[0] == 'BUY_PRODUCT'}
        eligible = tuple(it for it in priority if it not in buys)
        order = sorted(range(end), key=lambda i: (eligible.index(native[i][1])
                       if len(native[i]) > 1 and native[i][1] in eligible else len(eligible), i))
        changed += order != list(range(end))
        queues[0] = [queues[0][i] for i in order] + queues[0][end:]
        for slot in range(max(map(len, queues), default=0)):
            pair = [q[slot] if slot < len(q) else [] for q in queues]
            for u in range(max(map(len, pair), default=0)):
                prices = [A.K.market_price(o[u][1], inv[o[u][1]] - (o[u][0] == 'BUY_PRODUCT'))
                          if u < len(o) else None for o in pair]
                for seat, price in enumerate(prices):
                    if price is None:
                        continue
                    op, item = pair[seat][u]
                    quotes.append((t, slot, seat, op, item, price))
                    if op == 'SELL':
                        rev[seat][item] += price
                        inv[item] += price > 1
                    else:
                        cost[seat][item] += price
                        inv[item] -= 1
        for item in inv:
            inv[item] -= A.DEMAND[t][item]
    if not priority and not replace_melon:
        check(quotes == [(e['step'], e['slot'], e['seat'], e['op'], e['item'], e['price'])
                         for e in events if e['op'] in ('SELL', 'BUY_PRODUCT')], 'independent prices')
    return dict(revenue=list(map(dict, rev)), costs=list(map(dict, cost)), changed_turns=changed,
                net=[sum(rev[s].values()) - sum(cost[s].values()) for s in (0, 1)])


base = fixed_market()
diagnostics = []
for priority in [('WOOL',), ('FERTILIZER',), ('WOOL', 'FERTILIZER')]:
    out = fixed_market(priority)
    out.update(priority=priority, net_delta=out['net'][0] - base['net'][0],
               margin_delta=out['net'][0] - out['net'][1] - base['net'][0] + base['net'][1])
    diagnostics.append(out)
production = fixed_market(replace_melon=True)
production.update(net_delta=production['net'][0] - base['net'][0],
                  margin_delta=production['net'][0] - production['net'][1] - base['net'][0] + base['net'][1])
summary = dict(checks=checks, unlocks=unlock, priority_diagnostics=diagnostics,
               production_price_only=production,
               note='Existing full_engine.json retained; no games rerun; price-only estimates are not legal policies.')
(H / 'verification.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary), flush=True)
print(f'PASS: {checks} checks', flush=True)
