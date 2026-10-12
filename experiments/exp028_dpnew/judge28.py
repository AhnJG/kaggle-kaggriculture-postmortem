"""EXP-028 report (Claude). Absolute score of D (55be5d5f) and P (v074) per panel + paired delta D-P (seed-bootstrap95).
Recommendation rule fixed before results: SUBMIT_D if pooled closed-loop delta (O1+DP+guard) point>0 AND hosted H delta lower95>-0.03 AND D invalid==0 AND D max_step<0.8."""
import json,random,collections
OUT='experiments/exp028_dpnew'
def boot(x,seed,B=2000):
    r=random.Random(seed);n=len(x);m=sorted(sum(x[r.randrange(n)] for _ in range(n))/n for _ in range(B));return m[int(.025*B)]
def inv(r):return r['err'] is not None or r['statuses']!=['DONE','DONE'] or r['score'] is None or bool(r.get('agent_errors')) or r.get('action_count')!=719
rows={};[rows.__setitem__(json.loads(l)['key'],json.loads(l)) for l in open(OUT+'/games.jsonl')]
jobs=json.load(open(OUT+'/jobs.json'));assert {f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' for j in jobs}==set(rows)
M=collections.defaultdict(dict)
for r in rows.values():M[(r['vid'],r['opponent'])][(r['seed'],r['seat'])]=r
opps=sorted({o for (_,o) in M})
def sd(o):
    d,p=M[('D',o)],M[('P',o)];seeds=sorted({s for s,_ in p});return [sum(d[(s,t)]['score']-p[(s,t)]['score'] for t in (0,1) if (s,t) in d)/2 for s in seeds]
out={};pool=[];H=[]
for o in opps:
    ds=sum(r['score'] for r in M[('D',o)].values())/len(M[('D',o)]);ps=sum(r['score'] for r in M[('P',o)].values())/len(M[('P',o)])
    out[o]=dict(D=round(ds,3),P=round(ps,3),n=len(M[('D',o)]))
    if o.startswith('H'):H.append(list(M[('D',o)].values())[0]['score']-list(M[('P',o)].values())[0]['score'])
    elif not o.startswith('X'):pool+=sd(o)
Drows=[r for (v,o),g in M.items() if v=='D' for r in g.values()]
res=dict(pooled_delta=[sum(pool)/len(pool),boot(pool,28001)],hosted_delta=[sum(H)/len(H),boot(H,28002)],
    hosted_abs=dict(D=sum(list(M[('D',o)].values())[0]['score'] for o in opps if o.startswith('H'))/len(H),P=sum(list(M[('P',o)].values())[0]['score'] for o in opps if o.startswith('H'))/len(H)),
    D_invalid=sum(inv(r) for r in Drows),D_max_step=max(r['max_step'] for r in Drows),direct_D_vs_v074=out.get('X-D-vs-P',{}).get('D'))
res['recommend']='SUBMIT_D' if res['pooled_delta'][0]>0 and res['hosted_delta'][1]>-0.03 and res['D_invalid']==0 and res['D_max_step']<0.8 else 'HOLD'
json.dump(dict(summary=res,panels=out),open(OUT+'/summary.json','w'),indent=1)
print(json.dumps(res));[print(o,v) for o,v in out.items() if not o.startswith('H')]
