"""Read frozen hosted records; reconstruct executed market trades with locked engine."""
import argparse
import copy
import csv
import gzip
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'analysis/dp_hosted_20260924'
OUT = ROOT / 'experiments/results/dp_loss_cause_20260925'
PARENT = ROOT / 'releases/public-tetsutani-demand-preserving-0924-exact/main.py'
ENGINE_SHA = 'bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def records():
    return list(csv.DictReader((SOURCE / 'opponents.csv').open()))


def read_raw(eid):
    path = ROOT / f'private_artifacts/dp_hosted_20260924/raw/{eid}.json.gz'
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def audit():
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    assert sha(K.__file__) == ENGINE_SHA
    rows = records()
    headers = json.loads((SOURCE / 'episodes_all.json').read_text())
    refs = json.loads((SOURCE / 'file_hashes.json').read_text())
    byname = {v['name']: v for v in refs.values()}
    wins = Counter(str(r['submission_id']) for r in headers if r['result'] == 'W')
    sampled = Counter(r['submission'] for r in rows if r['result'] == 'W')
    full = []
    for r in rows:
        if r['match_full'] != 'True':
            continue
        ref = byname[r['closest_file']]
        raw = (ROOT / ref['path']).read_bytes()
        assert hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() == ref['sha256']
        full.append(dict(r, opponent_path=ref['path'], opponent_raw_sha=sha(ROOT / ref['path']),
                         eligible=r['submission'] != '56502662'))
    assert len(rows) == len({r['episode'] for r in rows}) == 319
    assert len(full) == 59
    result = dict(parent_sha=sha(PARENT), engine_sha=sha(K.__file__),
                  engine_json_sha=sha(Path(K.__file__).with_suffix('.json')),
                  source_hashes={p.name: sha(p) for p in SOURCE.glob('*.json')},
                  opponents_sha=sha(SOURCE / 'opponents.csv'),
                  work_order_sha=sha(ROOT / 'coordination/proposals/claude/20260924-DP-LOSS-CAUSE-CODEX.md'),
                  weights={s: wins[s]/sampled[s] for s in sampled}, full_panel=full,
                  eligible_counts=dict(Counter(r['result'] for r in full if r['eligible'])),
                  excluded_counts=dict(Counter(r['result'] for r in full if not r['eligible'])))
    save(OUT / 'input_audit.json', result)
    print(json.dumps({k:result[k] for k in ['parent_sha','eligible_counts','excluded_counts']}, ensure_ascii=False))


def describe_episode(row):
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    from kaggle_environments.utils import structify
    from postmortem import build_report
    assert sha(K.__file__) == ENGINE_SHA
    replay = read_raw(row['episode'])
    steps = replay['steps']
    assert len(steps) == 720 and replay['module_version'] == '1.32.7'
    assert replay['info']['seed'] == int(row['seed'])
    seat = int(row['dp_seat'])
    cfg = replay['configuration']
    trades, purchases = [], []
    context = {}
    original = K._commit_unit

    def commit(op, item, price, farm, private, market, shed_capacity=100):
        ok = original(op, item, price, farm, private, market, shed_capacity)
        if ok:
            pid = context['farm_ids'][id(farm)]
            context['trades'][(pid, op, item)][0] += 1
            context['trades'][(pid, op, item)][1] += price
        return ok

    K._commit_unit = commit
    checked = 0
    try:
        for i in range(1, len(steps)):
            actions = [steps[i][p]['action'] or {} for p in (0, 1)]
            if not any(a.get('market') for a in actions):
                continue
            pre = steps[i-1]
            farms = copy.deepcopy(pre[0]['observation']['farms'])
            privates = [copy.deepcopy(pre[p]['observation']['private']) for p in (0, 1)]
            market = copy.deepcopy(pre[0]['observation']['market'])
            state = [SimpleNamespace(action=actions[p], observation=SimpleNamespace(
                farms=farms, private=privates[p], market=market)) for p in (0, 1)]
            step = i-1
            for p in (0, 1):
                units = [actions[p].get('farmer', ['PASS'])] + list(actions[p].get('hands') or [])
                demand = Counter(a[1] for a in units if isinstance(a, list) and len(a)>1 and a[0]=='PLANT')
                blocked = {c for c,n in demand.items() if n>privates[p]['seeds'].get(c,0)}
                for u,a in enumerate(units):
                    if isinstance(a,list) and len(a)>1 and a[0]=='PLANT' and a[1] in blocked:
                        a=['PASS']
                    K._apply_unit_action(farms[p],privates[p],u,a,cfg['boardSize'],step//24,24,cfg['shedCapacity'])
            before = [(len(f['hands']),len(f['unlocked_quadrants'])) for f in farms]
            context.update(farm_ids={id(f):p for p,f in enumerate(farms)}, trades=defaultdict(lambda:[0,0]))
            K._process_market(state, SimpleNamespace(configuration=cfg))
            for p in (0, 1):
                actual=steps[i][0]['observation']['farms'][p]['money']
                assert farms[p]['money']==actual, (row['episode'],i,p,farms[p]['money'],actual)
                checked+=1
                for name,delta in [('HIRE',len(farms[p]['hands'])-before[p][0]),('BUY_LAND',len(farms[p]['unlocked_quadrants'])-before[p][1])]:
                    if delta:purchases.append(dict(step=step,action_row=i,day=step//24,player=p,op=name,units=delta))
            for (p,op,item),(n,value) in context['trades'].items():
                event=dict(step=step,action_row=i,day=step//24,player=p,op=op,item=item,units=n,value=value)
                trades.append(event)
                if op=='BUY_ANIMAL':purchases.append(event)
    finally:
        K._commit_unit=original
    periods=[]
    for lo,hi,end in [(0,11,288),(12,18,456),(19,29,719)]:
        pstats=[]
        for p in (seat,1-seat):
            sold=defaultdict(lambda:[0,0])
            for t in trades:
                if t['player']==p and t['op']=='SELL' and lo<=t['day']<=hi:
                    sold[t['item']][0]+=t['units'];sold[t['item']][1]+=t['value']
            pstats.append({item:dict(units=n,revenue=v,avg_price=v/n) for item,(n,v) in sold.items()})
        cash=[steps[end][0]['observation']['farms'][p]['money'] for p in (seat,1-seat)]
        periods.append(dict(days=[lo,hi],dp_sales=pstats[0],op_sales=pstats[1],cash=cash,margin=cash[0]-cash[1]))
    # Existing postmortem helper is applied to recorded states, without a new game.
    report=build_report('seat0','seat1',int(row['seed']),structify(steps),top_n=3)
    cash=steps[-1][0]['observation']['farms']
    assert cash[seat]['money']-cash[1-seat]['money']==float(row['margin'])
    return dict(metadata=row,raw_sha=sha(ROOT / f"private_artifacts/dp_hosted_20260924/raw/{row['episode']}.json.gz"),
                checked_cash=checked,periods=periods,trades=trades,purchases=purchases,postmortem=report)


def describe(limit=None):
    rows=records()
    rows.sort(key=lambda r:(r['closest_file']!='herd-safe-v3-experimental-risk-aware-feed', r['episode']))
    if limit:rows=rows[:limit]
    for i,r in enumerate(rows):
        path=OUT / 'episodes' / f"{r['episode']}.json"
        if path.exists():
            print('preserve',r['episode'],flush=True);continue
        result=describe_episode(r)
        save(path,result)
        print(i+1,r['episode'],r['result'],[p['margin'] for p in result['periods']],flush=True)


def summarize():
    rows=records()
    data={r['episode']:json.loads((OUT/'episodes'/f"{r['episode']}.json").read_text()) for r in rows}
    audit=json.loads((OUT/'input_audit.json').read_text())
    groups=defaultdict(list)
    screening={'refresh':[],'carrot':[]}
    for r in rows:
        x=data[r['episode']]
        if r['result']!='L':continue
        herd=r['match_full']=='True' and r['closest_file']=='herd-safe-v3-experimental-risk-aware-feed'
        dp='DP-0924-exact' in r['label'] and int(r['prefix_len'])>=143
        tier='1-herd-full' if herd else '2-dp-prefix' if dp else '3-upset-lt2400' if r['op_lb_score'] and float(r['op_lb_score'])<2400 else '4-other'
        first=next((i for i,p in enumerate(x['periods']) if p['margin']<0),None)
        deficit=Counter()
        if first is not None:
            p=x['periods'][first]
            for k,v in p['op_sales'].items():deficit[k]+=v['revenue']
            for k,v in p['dp_sales'].items():deficit[k]-=v['revenue']
        item=max(deficit,key=deficit.get) if deficit and max(deficit.values())>0 else 'purchase-or-other'
        groups[(tier,str(first),item,r['submission']=='56502662')].append(r)
        if not herd or r['submission']=='56502662':continue
        last=x['periods'][2]
        dp_sale=last['dp_sales'].get('STRAWBERRY',{})
        op_sale=last['op_sales'].get('STRAWBERRY',{})
        if dp_sale.get('avg_price',0)<op_sale.get('avg_price',0):screening['refresh'].append(r['episode'])
        dp_qty=sum(p['dp_sales'].get('CARROT',{}).get('units',0) for p in x['periods'])
        op_qty=sum(p['op_sales'].get('CARROT',{}).get('units',0) for p in x['periods'])
        if dp_qty<op_qty:screening['carrot'].append(r['episode'])
    grouped=[]
    for (tier,period,item,excluded),rs in sorted(groups.items()):
        scores=[float(r['op_lb_score']) for r in rs if r['op_lb_score']]
        grouped.append(dict(tier=tier,first_negative_period=period,largest_sales_deficit_item=item,
                            excluded_submission=excluded,count=len(rs),margin_sum=sum(float(r['margin']) for r in rs),
                            median_op_lb=statistics.median(scores) if scores else None,episodes=sorted(r['episode'] for r in rs)))
    weights={r['episode']:audit['weights'][r['submission']] if r['result']=='W' else 1 for r in rows}
    denominators={name:sum(weights[r['episode']] for r in rows if name=='all' or r['submission']!='56502662') for name in ['all','eligible']}
    herd=[r for r in rows if r['match_full']=='True' and r['closest_file']=='herd-safe-v3-experimental-risk-aware-feed']
    dp=[r for r in rows if 'DP-0924-exact' in r['label'] and int(r['prefix_len'])>=143]
    field=dict(weighted_nondraw_denominators=denominators,unsampled_draw_headers=19,
               herd_share_all=sum(weights[r['episode']] for r in herd)/denominators['all'],
               herd_share_eligible=sum(weights[r['episode']] for r in herd if r['submission']!='56502662')/denominators['eligible'],
               dp_prefix_share_all=sum(weights[r['episode']] for r in dp)/denominators['all'],
               dp_prefix_share_eligible=sum(weights[r['episode']] for r in dp if r['submission']!='56502662')/denominators['eligible'])
    save(OUT/'q1_summary.json',dict(episodes=len(data),cash_checks=sum(x['checked_cash'] for x in data.values()),
                                  groups=grouped,screening={k:sorted(v) for k,v in screening.items()},field=field))
    print(json.dumps(dict(screening=screening,field=field),ensure_ascii=False))


def divergences():
    from kaggle_environments.agent import get_last_callable
    from kaggle_environments.utils import structify
    result=[]
    for r in sorted(records(),key=lambda r:r['episode']):
        if r['result']!='L' or 'DP-0924-exact' not in r['label'] or int(r['prefix_len'])<143:continue
        replay=read_raw(r['episode']);op=1-int(r['dp_seat'])
        fn=get_last_callable(PARENT.read_text(),path=str(PARENT))
        found=None
        for i in range(1,720):
            obs=copy.deepcopy(replay['steps'][i-1][op]['observation']);obs['step']=i-1
            predicted=fn(structify(obs),structify(replay['configuration']))
            actual=replay['steps'][i][op]['action']
            if predicted!=actual:
                found=dict(action_row=i,decision_step=i-1,dp_on_op_observation=predicted,hosted_op_action=actual)
                break
        result.append(dict(metadata=r,first_difference=found,kind='observed-state-policy-comparison',
                           note='Teacher-forced observations, not a causal counterfactual or source identity proof'))
        print(r['episode'],None if found is None else found['decision_step'],flush=True)
    save(OUT/'q1_dp_prefix_divergences.json',result)


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('mode',choices=['audit','describe','summarize','divergences'])
    ap.add_argument('--limit',type=int)
    args=ap.parse_args()
    if args.mode=='audit':audit()
    elif args.mode=='describe':describe(args.limit)
    elif args.mode=='summarize':summarize()
    else:divergences()
