"""Slot race in hosted d157 games: for each step where both seats SELL the same item, compare the slot index (first SELL order of that item).
Engine: slot i of both players is processed together (per-unit lockstep); an item sold in an earlier slot is sold before the other seat's later slot."""
import json,gzip,csv,collections,statistics as st
R=[r for r in csv.DictReader(open('analysis/c26_hosted_20260929/opponents.csv'))]
PREM={'MILK','WOOL','STRAWBERRY','MELON','EGG','CARROT','TOMATO','WHEAT','FERTILIZER'}
def first_slot(a):
    d={}
    for i,o in enumerate(((a or {}).get('market') or [])[:10]):
        if isinstance(o,list) and len(o)>=3 and o[0]=='SELL' and o[1] not in d:
            try:
                if int(o[2])>0:d[o[1]]=i
            except:pass
    return d
out=collections.defaultdict(lambda:collections.Counter())
for r in R:
    raw=json.load(gzip.open(f"private_artifacts/c26_hosted_20260929/raw/{r['episode']}.json.gz"))
    s=int(r['seat']);fam='55be' if '55be' in r['label'] else 'other'
    c=collections.Counter()
    for t in range(1,len(raw['steps'])):
        us=first_slot(raw['steps'][t][s]['action']);th=first_slot(raw['steps'][t][1-s]['action'])
        for it in set(us)&set(th):
            k='us_first' if us[it]<th[it] else 'them_first' if th[it]<us[it] else 'same'
            c[k]+=1;c[f'{k}:{it}']+=1
    out[(r['submission_label'],fam,r['result'])]+=c
for k in sorted(out):
    c=out[k];n=c['us_first']+c['them_first']+c['same']
    if n:print(k,'contested item-steps',n,'us_first %.2f them_first %.2f same %.2f'%(c['us_first']/n,c['them_first']/n,c['same']/n),
              '| top them_first items',[(x.split(':')[1],v) for x,v in c.most_common() if x.startswith('them_first:')][:4])
