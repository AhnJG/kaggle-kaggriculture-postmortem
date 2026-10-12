"""Frozen rules. screen: advance if mean dScore>=+0.05, mean dMargin>0, invalid 0, not NO_EFFECT; top 8 by (dScore,dMargin).
stage2: pass if episode-bootstrap95 lower of dScore > 0 and mean dMargin > 0 and invalid 0; rank by lower bound."""
import json,sys,random,collections
from common26 import *
def load(p):
    rows={};[rows.__setitem__(json.loads(l)['key'],json.loads(l)) for l in open(p)];return list(rows.values())
def deltas(rows):
    by=collections.defaultdict(dict)
    for r in rows:by[r['vid']][r['episode']]=r
    P=by.pop('P');out={}
    for vid,g in by.items():
        eps=sorted(set(g)&set(P))
        ds=[g[e]['score']-P[e]['score'] if not invalid(g[e]) else None for e in eps]
        dm=[g[e]['margin']-P[e]['margin'] if not invalid(g[e]) else None for e in eps]
        inv=sum(invalid(g[e]) for e in eps);ne=all(g[e]['act_sha']==P[e]['act_sha'] for e in eps)
        ok=[i for i,x in enumerate(ds) if x is not None]
        out[vid]=dict(n=len(eps),invalid=inv,no_effect=ne,dscore=[ds[i] for i in ok],dmargin=[dm[i] for i in ok],
                      score=sum(g[e]['score'] for e in eps if not invalid(g[e]))/max(1,len(ok)),max_step=max(g[e]['max_step'] for e in eps))
    return P,out
def boot_lower(x,seed=26026,B=2000):
    rng=random.Random(seed);n=len(x);m=sorted(sum(x[rng.randrange(n)] for _ in range(n))/n for _ in range(B));return m[int(.025*B)]
if __name__=='__main__':
    stage=sys.argv[1]
    P,d=deltas(load(f'{OUT}/games-{stage}.jsonl'))
    base=dict(score=sum(r['score'] for r in P.values())/len(P),margin=sum(r['margin'] for r in P.values())/len(P),n=len(P))
    res=[]
    for vid,x in d.items():
        mds=sum(x['dscore'])/len(x['dscore']) if x['dscore'] else 0;mdm=sum(x['dmargin'])/len(x['dmargin']) if x['dmargin'] else 0
        r=dict(vid=vid,n=x['n'],invalid=x['invalid'],no_effect=x['no_effect'],score=x['score'],dscore=mds,dmargin=mdm,max_step=x['max_step'])
        if stage=='screen':r['advance']=x['invalid']==0 and not x['no_effect'] and mds>=0.05 and mdm>0
        else:
            r['dscore_lower95']=boot_lower(x['dscore']) if x['dscore'] else None
            r['pass']=x['invalid']==0 and r['dscore_lower95'] is not None and r['dscore_lower95']>0 and mdm>0
        res.append(r)
    if stage=='screen':
        res.sort(key=lambda r:(r['advance'],r['dscore'],r['dmargin']),reverse=True);sel=[r['vid'] for r in res if r['advance']][:8]
    else:
        res.sort(key=lambda r:(r['pass'],r['dscore_lower95'] or -9,r['dmargin']),reverse=True);sel=[r['vid'] for r in res if r['pass']]
    json.dump(dict(stage=stage,baseline=base,selected=sel,results=res),open(f'{OUT}/{stage}-summary.json','w'),indent=1)
    print(json.dumps(dict(stage=stage,baseline=base,selected=sel)),flush=True)
    for r in res[:12]:print(r)
