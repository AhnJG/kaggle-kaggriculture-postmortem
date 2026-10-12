"""Fixed-episode absorption accounting and explicitly constrained timing diagnostics."""
import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as K

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'fundamental_gain_20260923'
STEM = 'exp017_2142_omw'
MARKETS = json.loads((SOURCE / (STEM+'.markets.json')).read_text())
OLD_EVENTS = json.loads((SOURCE / (STEM+'.events.json')).read_text())
assert hashlib.sha256(Path(K.__file__).read_bytes()).hexdigest() == 'bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e'
DEMAND = []
for t, states in enumerate(MARKETS):
    d = Counter()
    if t % 4 == 0:
        for shop in states[0]['observation']['town']['unlocked_shops']:
            d.update({it: 2 if len(K.SHOPS[shop]) == 1 else 1 for it in K.SHOPS[shop]})
    if t % 24 == 0:
        d.update(K.TOWN_CENTER_PRODUCTS)
    DEMAND.append(d)

def tape(seat):
    return lambda obs, config=None: copy.deepcopy(MARKETS[int(obs['step'])][seat]['action'])

def replay(target=None, expected=None):
    original_market, original_commit = K._process_market, K._commit_unit
    events, pending, matching, max_shed, flush = [], 0, 0, 0, 0
    ctx = {}
    original_sales = Counter(e['step'] for e in OLD_EVENTS
                             if e['seat']==0 and e['op']=='SELL' and e['item']==target)
    def commit(op, item, price, farm, private, market, capacity=100):
        seat = next(s for s,f in enumerate(ctx['farms']) if f is farm)
        ok = original_commit(op,item,price,farm,private,market,capacity)
        if ok:
            events.append(dict(step=ctx['t'], slot=ctx['slot'], seat=seat,
                               op=op,item=item,price=price))
        return ok
    def market(states, env):
        nonlocal pending, matching, max_shed, flush
        t = int(states[0].observation.step)
        ctx.update(t=t, farms=states[0].observation.farms)
        fields = ('farms','private','market','town','day','hour')
        if all(all(states[s].observation[k] == MARKETS[t][s]['observation'][k]
                   for k in fields) for s in (0,1)):
            matching += 1
        actions = [copy.deepcopy(s.action) for s in states]
        queues = [list(a.get('market', []))[:10] for a in actions]
        if target:
            pending += original_sales[t]
            indices = [i for i,o in enumerate(queues[0]) if len(o)>1 and o[:2]==['SELL',target]]
            pos = indices[0] if indices else 0
            queues[0] = [o for i,o in enumerate(queues[0]) if i not in indices]
            capacity = DEMAND[t-1][target] if t else 0
            if t == 718: capacity = pending
            n = min(pending, capacity, states[0].observation.private['shed'].get(target,0))
            if n and len(queues[0]) < 10:
                queues[0].insert(min(pos,len(queues[0])), ['SELL',target,n])
                if t==718: flush=n
            else: n=0
        before = len(events)
        for slot in range(max(map(len,queues), default=0)):
            ctx['slot'] = slot
            for s in (0,1):
                states[s].action = dict(actions[s],market=[queues[s][slot]] if slot<len(queues[s]) else [])
            original_market(states, env)
        for s in (0,1): states[s].action=actions[s]
        if target:
            pending -= sum(e['seat']==0 and e['op']=='SELL' and e['item']==target for e in events[before:])
        max_shed = max(max_shed, sum(states[0].observation.private['shed'].values()))
    K._process_market, K._commit_unit = market, commit
    env=make('kaggriculture',configuration={'seed':2142,'episodeSteps':720})
    try: env.run([tape(0),tape(1)])
    finally: K._process_market,K._commit_unit=original_market,original_commit
    if not target:
        assert matching==719, matching
        assert [s.reward for s in env.steps[-1]]==[104150,104360]
        ref=[e for e in OLD_EVENTS if not e['op'].startswith('_do_')]
        assert [{k:v for k,v in e.items() if k!='slot'} for e in events]==ref
    quantity=Counter((e['seat'],e['op'],e['item']) for e in events)
    outcome=dict(target=target, cash=[s.reward for s in env.steps[-1]],
                 steps=len(env.steps), statuses=[s.status for s in env.steps[-1]],
                 premarket_matches=matching,pending=pending,final_flush=flush,max_shed=max_shed,
                 quantity_changes=[] if expected is None else
                 [dict(seat=k[0],op=k[1],item=k[2],delta=quantity[k]-expected[k])
                  for k in sorted(set(quantity)|set(expected)) if quantity[k]!=expected[k]])
    if target:
        outcome['target_sold']=quantity[(0,'SELL',target)]
        outcome['target_revenue']=sum(e['price'] for e in events if e['seat']==0 and e['op']=='SELL' and e['item']==target)
    return events, outcome

def isolated(item, events, spread):
    """Fixed actual fill quantities, unlimited storage/funding; replay slot price rule."""
    bystep=defaultdict(list)
    for e in events:
        if e['item']==item: bystep[e['step']].append(e)
    inv=10000; pending=0; sold=[0,0]; revenue=[0,0]; cost=[0,0]; max_pending=0
    forced=0; quotes=[]; max_shed=0; daily=[]
    for t in range(719):
        rows=bystep[t]
        queues=[]
        for s in (0,1):
            q=[None]*min(10,len(MARKETS[t][s]['action'].get('market',[])))
            counts=Counter((e['slot'],e['op']) for e in rows if e['seat']==s)
            for (slot,op),n in counts.items():
                if op in ('SELL','BUY_PRODUCT'):q[slot]=[op,n]
            queues.append(q)
        original_sold=sum(e['seat']==0 and e['op']=='SELL' for e in rows)
        if spread:
            previous=pending
            pending+=original_sold
            indices=[i for i,o in enumerate(queues[0]) if o and o[0]=='SELL']
            # Remove even unfilled SELL requests so native order indices shift correctly.
            indices=[i for i,o in enumerate(MARKETS[t][0]['action'].get('market',[])[:10])
                     if len(o)>1 and o[:2]==['SELL',item]]
            pos=indices[0] if indices else 0
            queues[0]=[o for i,o in enumerate(queues[0]) if i not in indices]
            capacity=DEMAND[t-1][item] if t else 0
            if t==718:capacity=pending
            n=min(pending,capacity) if len(queues[0])<10 else 0
            if n:queues[0].insert(min(pos,len(queues[0])),['SELL',n])
            if t==718:forced=n
            pending-=n
            max_pending=max(max_pending,pending)
            max_shed=max(max_shed,sum(MARKETS[t][0]['observation']['private']['shed'].values())+previous)
        for slot in range(max(map(len,queues),default=0)):
            qs=[queues[s][slot] if slot<len(queues[s]) else None for s in (0,1)]
            for u in range(max([o[1] if o else 0 for o in qs], default=0)):
                prices=[K.market_price(item,inv-(o[0]=='BUY_PRODUCT'))
                        if o and u<o[1] else None for o in qs]
                for s,o in enumerate(qs):
                    if prices[s] is None:continue
                    price=prices[s];quotes.append((t,slot,s,o[0],price))
                    if o[0]=='SELL':
                        sold[s]+=1;revenue[s]+=price;inv+=price>1
                    else:cost[s]+=price;inv-=1
        inv-=DEMAND[t][item]
        if t%24==23 or t==718:daily.append(dict(step=t,inventory=inv,price=K.market_price(item,inv)))
    if not spread:
        wanted=[(e['step'],e['slot'],e['seat'],e['op'],e['price']) for e in events
                if e['item']==item and e['op'] in ('SELL','BUY_PRODUCT')]
        assert quotes==wanted,(item,'quote mismatch')
    assert pending==0,(item,pending)
    return dict(item=item,sold=sold,revenue=revenue,buy_cost=cost,net=[revenue[s]-cost[s] for s in (0,1)],
                end_inventory=inv,final_flush=forced,max_pending=max_pending,
                virtual_shed_peak=max_shed,daily=daily)

def main():
    events, baseline=replay()
    totals=Counter()
    for d in DEMAND:totals.update(d)
    q1=[]; q2=[]; full=[]
    for item in K.PRODUCTS:
        rows=[e for e in events if e['item']==item]
        sells=[sum(e['seat']==s and e['op']=='SELL' for e in rows) for s in (0,1)]
        buys=sum(e['op']=='BUY_PRODUCT' for e in rows)
        floor=sum(e['op']=='SELL' and e['price']==1 for e in rows)
        q1.append(dict(item=item,absorption=totals[item],sales=sells,our_excess=sells[0]-totals[item],
                       both_excess=sum(sells)-totals[item],buys=buys,floor_sales=floor,
                       inventory_delta=sum(sells)-floor-buys-totals[item]))
        a=isolated(item,events,False);b=isolated(item,events,True)
        assert a['sold']==b['sold']
        assert a['end_inventory']-10000==q1[-1]['inventory_delta']
        q2.append(dict(item=item,actual=a,spread=b,revenue_delta=b['revenue'][0]-a['revenue'][0],
                       net_delta=b['net'][0]-a['net'][0],
                       margin_delta=(b['net'][0]-b['net'][1])-(a['net'][0]-a['net'][1])))
    (HERE/'q1.json').write_text(json.dumps(q1,indent=2)+'\n')
    (HERE/'q2_fixed_fills.json').write_text(json.dumps(q2,indent=2)+'\n')
    (HERE/'baseline_fills.json').write_text(json.dumps(events)+'\n')
    (HERE/'demand.json').write_text(json.dumps(DEMAND)+'\n')
    print('Q1',json.dumps(q1),flush=True)
    print('Q2',json.dumps([{k:v for k,v in x.items() if k not in ('actual','spread')} for x in q2]),flush=True)
    expected=Counter((e['seat'],e['op'],e['item']) for e in events)
    for item in K.PRODUCTS:
        _,out=replay(item,expected)
        full.append(out);print('FULL',json.dumps(out),flush=True)
    (HERE/'full_engine.json').write_text(json.dumps(dict(baseline=baseline,variants=full),indent=2)+'\n')

if __name__=='__main__':main()
