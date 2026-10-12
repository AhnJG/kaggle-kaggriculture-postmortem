"""EXP-056 Stage 1 judge per PREREG.md: bot - d157 paired on exp051 tapes; team-cluster bootstrap (Claude 09-29)."""
import json,collections,random,statistics as st
B={};T={}
meta=json.load(open('experiments/exp051_curpop/meta.json'))
for l in open('experiments/exp051_curpop/games.jsonl'):
    r=json.loads(l)
    if r['vid']=='d157':B[(r['opponent'],r['seed'],r['seat'])]=r['score']
def team(op):
    m=meta.get(op) if isinstance(meta,dict) else None
    return (m or {}).get('op_team') or (m or {}).get('team') or op
D=collections.defaultdict(dict)
for f in ('games-mac.jsonl','games-kaggle.jsonl'):
    for l in open('experiments/exp056_pubscreen/'+f):
        r=json.loads(l);k=(r['opponent'],r['seed'],r['seat'])
        if k in B and not r['err'] and not r['agent_errors']:D[r['vid']][k]=r['score']-B[k]
out={}
for v,d in sorted(D.items()):
    G=collections.defaultdict(list)
    for k,x in d.items():G[team(k[0])].append(x)
    ks=list(G);rng=random.Random(0);bs=[]
    for _ in range(2000):
        s=[x for g in rng.choices(ks,k=len(ks)) for x in G[g]];bs.append(st.mean(s))
    bs.sort();mu=st.mean(d.values());lo=bs[50]
    out[v]=dict(n=len(d),teams=len(ks),delta=round(mu,4),lb=round(lo,4),pass_=mu>0.02 and lo>0)
    print(v,out[v])
json.dump(out,open('experiments/exp056_pubscreen/verdict56.json','w'),indent=1)
