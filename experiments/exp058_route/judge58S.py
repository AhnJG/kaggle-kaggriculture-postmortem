"""EXP-058 Stage S judge (Claude 09-29, written BEFORE any Stage S result). Rules: PREREG.md (sha 75a8125e…).
Unit of bootstrap = tape (one hosted episode = one opponent submission game), as in EXP-056/057 (meta has no team name)."""
import json,collections,random,statistics as st,sys
sys.path.insert(0,'experiments/exp058_route');from common58 import RULES
BASE=collections.defaultdict(dict)
for l in open('experiments/exp051_curpop/games.jsonl'):
    r=json.loads(l);BASE[r['vid']][(r['opponent'],r['seed'],r['seat'])]=r['score']
FR=collections.defaultdict(dict);bad=collections.Counter()
for f in ('games-kaggle.jsonl','games-mac.jsonl'):
    try:L=open('experiments/exp058_route/'+f)
    except FileNotFoundError:continue
    for l in L:
        r=json.loads(l)
        if r['score'] is None or r['err'] or r['agent_errors'] or r['statuses']!=['DONE','DONE']:bad[r['vid']]+=1;continue
        FR[int(r['vid'][2:])][(r['opponent'],r['seed'],r['seat'])]=r['score']
keys=sorted(BASE['d157']);GC=json.load(open('experiments/exp058_route/groups_curpop.json'));grp={k:GC[k[0][1:]]['group'] for k in keys}
print('rows per arm',{R:len(v) for R,v in FR.items()},'invalid',dict(bad),'groups',collections.Counter(grp.values()))
out=[]
for G,R in RULES:
    ks=[k for k in keys if k in FR[R]]
    if len(ks)<len(keys):print('WARN incomplete arm',R,len(ks))
    if not ks:continue
    ing=[k for k in ks if grp[k]==G]
    d=[FR[R][k]-BASE['d157'][k] if grp[k]==G else 0.0 for k in ks]
    dc=[(FR[R][k] if grp[k]==G else BASE['d157'][k])-BASE['c26'][k] for k in ks]
    gi=[FR[R][k]-BASE['d157'][k] for k in ing]
    rng=random.Random(0);bs=sorted(st.mean(rng.choices(gi,k=len(gi))) for _ in range(2000)) if gi else [float('nan')]*2000
    row=dict(rule=f'{G}->{R}',n=len(ks),n_group=len(ing),delta=round(st.mean(d),4),delta_group=round(st.mean(gi),4) if gi else None,
             lb95_group=round(bs[50],4),delta_vs_c26=round(st.mean(dc),4),changed=sum(1 for k in ing if FR[R][k]!=BASE['d157'][k]))
    row['pass']=row['delta']>=0.02 and row['lb95_group']>0 and row['delta_vs_c26']>=0 and len(ks)==len(keys)
    out.append(row)
out.sort(key=lambda r:-r['delta'])
if not out:sys.exit('no Stage S rows yet')
for r in out:print(r)
best=out[0];print('SELECTED',best['rule'],'Stage S PASS' if best['pass'] else 'Stage S FAIL')
json.dump({'rules':out,'selected':best['rule'],'stageS_pass':best['pass'],'invalid':dict(bad)},open('experiments/exp058_route/verdictS.json','w'),indent=1)
