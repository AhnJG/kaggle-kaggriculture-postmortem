"""Recompute accounting, conservation and conditional bounds from raw fills."""
import copy
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from kaggle_environments.envs.kaggriculture import kaggriculture as K

HERE = Path(__file__).resolve().parent
checks = 0
summaries = {}
for name in ('c1_2014', 'exp017_2014_s0', 'exp017_2014_s1', 'exp017_2142_omw'):
    r = json.loads((HERE / (name+'.json')).read_text())
    events = json.loads((HERE / (name+'.events.json')).read_text())
    markets = json.loads((HERE / (name+'.markets.json')).read_text())
    seat = r['seat']
    own = [e for e in events if e['seat'] == seat]
    net = sum(e['price'] if e['op']=='SELL' else -e['price'] for e in own)
    assert net+3000 == r['final_cash']; checks += 1
    assert r['runner_sha'] == hashlib.sha256((HERE/'bound.py').read_bytes()).hexdigest()
    checks += 1
    deltas = {}
    for row in r['products']:
        it = row['item']
        buys = sum(e['op']=='BUY_PRODUCT' and e['item']==it for e in own)
        assert row['harvested']+buys == row['sold']+row['used']+row['discarded']+row['terminal']
        initial_inventory = 10000-row['town_demand']-row['both_buy_units']
        inventory = initial_inventory
        value = 0
        for _ in range(row['sold']+row['discarded']+row['terminal']):
            price = K.market_price(it, inventory)
            value += price
            inventory += price > 1
        assert value == row['rescued_bound']
        checks += 2
        byseat = []
        for s in (seat, 1-seat):
            es = [e for e in events if e['seat']==s and e['item']==it]
            byseat.append(dict(sold=sum(e['op']=='SELL' for e in es),
                               revenue=sum(e['price'] for e in es if e['op']=='SELL'),
                               net=sum(e['price'] if e['op']=='SELL' else -e['price'] for e in es)))
        deltas[it] = dict(ours=byseat[0], rival=byseat[1], net_delta=byseat[0]['net']-byseat[1]['net'])
    physical_same = sum(all(s[0]['action'].get(k)==s[1]['action'].get(k)
                            for k in ('farmer', 'hands')) for s in markets)
    sales = [[e for e in events if e['seat']==s and e['op']=='SELL' and e['item']=='STRAWBERRY']
             for s in (seat, 1-seat)]
    rank_pairs = defaultdict(lambda: [0,0])
    if len(sales[0]) == len(sales[1]):
        for a,b in zip(*sales):
            key = 'earlier' if a['step']<b['step'] else 'later' if a['step']>b['step'] else 'same'
            rank_pairs[key][0] += 1
            rank_pairs[key][1] += a['price']-b['price']
    summaries[name] = dict(final_cash=r['final_cash'], rival_cash=r['rival_cash'],
                           physical_actions_equal=physical_same, physical_action_turns=len(markets),
                           deltas=deltas, strawberry_rank_pairs=dict(rank_pairs))

# Exhaustive small monotone-market check: town/buy withdrawals, own sales and rival sales
# in every ordering. Granting withdrawals first and deleting rival sales never lowers
# the own revenue ceiling, including the price-floor non-increment branch.
for start in (0, 3, 6):
    for seq in itertools.product('SOR', repeat=6):
        inv, actual = start, 0
        for op in seq:
            if op == 'R':
                inv -= 1
            else:
                price = max(1, 5-inv)
                if op == 'S': actual += price
                inv += price > 1
        inv = start-seq.count('R')
        upper = 0
        for _ in range(seq.count('S')):
            price = max(1, 5-inv)
            upper += price
            inv += price > 1
        assert actual <= upper
        checks += 1

a,b = [summaries[n] for n in ('exp017_2014_s0','exp017_2014_s1')]
assert a['final_cash']==b['final_cash'] and a['rival_cash']==b['rival_cash']
assert a['deltas']==b['deltas']; checks += 2
assert summaries['exp017_2142_omw']['physical_actions_equal']==719; checks += 1
assert sum(v['net_delta'] for v in summaries['exp017_2142_omw']['deltas'].values())==-210
checks += 1
result = dict(verdict='PASS', checks=checks, summaries=summaries)
(HERE/'verified_summary.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(dict(verdict='PASS', checks=checks)))
