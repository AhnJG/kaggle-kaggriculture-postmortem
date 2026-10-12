"""EXP-057 Stage 1 judge per PREREG.md (sha b99f38d8…). Claude 09-29."""
import json,collections,random,statistics as st
B={}
for l in open('experiments/exp051_curpop/games.jsonl'):
    r=json.loads(l);B[(r['vid'],r['opponent'],r['seed'],r['seat'])]=r
D=collections.defaultdict(list)
for l in open('experiments/exp057_geese/games.jsonl'):
    r=json.loads(l)
    if r['err'] or r['agent_errors']:continue
    b=B[('d157',r['opponent'],r['seed'],r['seat'])];c=B[('c26',r['opponent'],r['seed'],r['seat'])]
    D[r['vid']].append((r['opponent'],r['score']-b['score'],r['score']-c['score'],r['rewards']!=b['rewards']))
out={}
for v,x in sorted(D.items()):
    rng=random.Random(0);bs=sorted(st.mean(rng.choices([a[1] for a in x],k=len(x))) for _ in range(2000))
    d=st.mean(a[1] for a in x);dc=st.mean(a[2] for a in x);ch=[a[1] for a in x if a[3]]
    out[v]=dict(n=len(x),delta_d157=round(d,4),lb95=round(bs[50],4),delta_c26=round(dc,4),changed=len(ch),delta_changed=round(st.mean(ch),4) if ch else None,
                stage1_pass=d>0.02 and bs[50]>0 and dc>=0)
    print(v,out[v])
json.dump(out,open('experiments/exp057_geese/verdict57.json','w'),indent=1)
