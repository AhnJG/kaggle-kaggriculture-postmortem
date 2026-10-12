"""Frozen rules (Claude, 09-27 before results). Baseline P = v074.
A': vs 127ed3e6 paired dScore seed-bootstrap95 lower > -0.03
B : vs DP paired lower > -0.05
C : per guard file mean dScore >= -0.10
D : pooled (DP + all guard files) paired lower > -0.03
H : hosted 121 rows paired lower > -0.03
E : our invalid 0, max step < 0.5s
N : near-clone tape dScore vs v074: singles use EXP-026 stage2 (already passed); c3 must have episode-bootstrap95 lower > 0
Selection among passers: max expected gain = 0.22*N_dscore + 0.78*D_point  (0.22 = near-clone share of v171 hosted games)."""
import json,random,collections
OUT='experiments/exp027_stage3'
def boot(x,seed,B=2000):
    r=random.Random(seed);n=len(x);m=sorted(sum(x[r.randrange(n)] for _ in range(n))/n for _ in range(B));return m[int(.025*B)]
def inv(r):return r['err'] is not None or r['statuses']!=['DONE','DONE'] or r['score'] is None or bool(r.get('agent_errors')) or r.get('action_count')!=719
rows={};[rows.__setitem__(json.loads(l)['key'],json.loads(l)) for l in open(OUT+'/games-closed.jsonl')]
jobs=json.load(open(OUT+'/jobs-closed.json'));exp={f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' for j in jobs}
assert exp==set(rows),('missing',len(exp-set(rows)))
rows=list(rows.values());man=json.load(open(OUT+'/manifest.json'))
M=collections.defaultdict(dict)
for r in rows:M[(r['vid'],r['opponent'])][(r['seed'],r['seat'])]=r
def seed_deltas(v,opp):
    c=M[(v,opp)];p=M[('P',opp)];seeds=sorted({s for s,_ in p})
    return [sum(c[(s,t)]['score']-p[(s,t)]['score'] for t in (0,1))/2 for s in seeds]
s2={r['vid']:r for r in json.load(open('experiments/exp026_nearclone/stage2-summary.json'))['results']}
nrows={};[nrows.__setitem__(json.loads(l)['episode'],json.loads(l)) for l in open(OUT+'/games-n.jsonl')]
base={};[base.__setitem__(json.loads(l)['episode'],json.loads(l)) for l in open('experiments/exp026_nearclone/games-stage2.jsonl') if json.loads(l)['vid']=='P']
res=[]
for i,v in enumerate(man['candidates']):
    ap=seed_deltas(v,'AP-O1');b=seed_deltas(v,'B-DP')
    gd={};pool=list(b)
    for g in man['guard']:
        d=seed_deltas(v,g['id']);gd[g['id']]=sum(d)/len(d);pool+=d
    hosted=sorted({o for (vv,o) in M if vv=='P' and o.startswith('H')})
    h=[list(M[(v,o)].values())[0]['score']-list(M[('P',o)].values())[0]['score'] for o in hosted]
    mine=[r for r in rows if r['vid']==v];ninv=sum(inv(r) for r in mine);mx=max(r['max_step'] for r in mine)
    if v=='c3':
        nd=[nrows[e]['score']-base[e]['score'] for e in nrows if not inv(nrows[e])];nlo=boot(nd,27000);npt=sum(nd)/len(nd);ninv+=sum(inv(x) for x in nrows.values())
    else:npt=s2[v]['dscore'];nlo=s2[v]['dscore_lower95']
    g=dict(A_prime=boot(ap,27100+i)>-0.03,B=boot(b,27200+i)>-0.05,C=min(gd.values())>=-0.10,D=boot(pool,27300+i)>-0.03,
           H=boot(h,27400+i)>-0.03,E=ninv==0 and mx<0.5,N=nlo>0)
    res.append(dict(vid=v,A_prime=[sum(ap)/len(ap),boot(ap,27100+i)],B=[sum(b)/len(b),boot(b,27200+i)],C_worst=min(gd.items(),key=lambda x:x[1]),
        D=[sum(pool)/len(pool),boot(pool,27300+i)],H=[sum(h)/len(h),boot(h,27400+i)],E=[ninv,mx],N=[npt,nlo],gates=g,passed=all(g.values()),
        expected_gain=0.22*npt+0.78*sum(pool)/len(pool)))
ps=[r for r in res if r['passed']];ps.sort(key=lambda r:r['expected_gain'],reverse=True)
out=dict(verdict='SUCCESS' if ps else 'FAIL',selected=ps[0]['vid'] if ps else None,results=res)
json.dump(out,open(OUT+'/stage3-summary.json','w'),indent=1,default=str)
print(json.dumps(dict(verdict=out['verdict'],selected=out['selected'])))
for r in res:print(r['vid'],r['passed'],{k:(round(x[0],3),round(x[1],3)) if isinstance(x,list) and len(x)==2 and all(isinstance(y,(int,float)) for y in x) else x for k,x in r.items() if k in('A_prime','B','D','H','N','E','C_worst')},round(r['expected_gain'],3))
