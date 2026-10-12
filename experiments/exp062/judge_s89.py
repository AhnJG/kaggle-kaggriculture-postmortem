# Claude-B 22:55 KST: generic per-cell + paired-diff judge for S8/S9. usage: python judge_s89.py games.jsonl REF [CANDS...]
import json,sys,random,collections
f,ref=sys.argv[1],sys.argv[2]
G=[json.loads(l) for l in open(f) if l.strip()]
err=[g for g in G if g.get('err') or g.get('agent_errors')]
print('games',len(G),'errors',len(err))
S={}
for g in G: S[(g['vid'],g['opponent'],g['seed'])]=g['score']
vids=sorted({k[0] for k in S}); opps=sorted({k[1] for k in S})
cands=sys.argv[3:] or vids
print('cell means (n):')
print('%-8s'%'opp'+''.join('%9s'%v for v in cands))
for o in opps:
    row='%-8s'%o
    for v in cands:
        xs=[s for (vv,oo,_),s in S.items() if vv==v and oo==o]
        row+='%9s'%('%.3f/%d'%(sum(xs)/len(xs),len(xs)) if xs else '-')
    print(row)
def boot(d,B=4000):
    seeds=list(d);random.seed(0);ms=[]
    for _ in range(B):
        smp=[random.choice(seeds) for _ in seeds];ms.append(sum(d[s] for s in smp)/len(smp))
    ms.sort();return sum(d.values())/len(d),ms[int(.05*B)],ms[int(.95*B)]
print('\npaired diff vs',ref,'(mean [90% CI]) per opp, and overall (excluding self cells):')
for v in cands:
    if v==ref: continue
    line=v+': '
    allp=collections.defaultdict(list)
    for o in opps:
        d={}
        for (vv,oo,s),x in S.items():
            if vv==v and oo==o and (ref,o,s) in S: d[s]=x-S[(ref,o,s)]
        if not d: continue
        m,lo,hi=boot(d);line+='%s %+.3f[%+.3f,%+.3f] '%(o,m,lo,hi)
        if o not in (v,ref):
            for s,x in d.items(): allp[s].append(x)
    ov={s:sum(x)/len(x) for s,x in allp.items()}
    m,lo,hi=boot(ov);print(line);print('   OVERALL(no self) %+.3f [%+.3f,%+.3f]'%(m,lo,hi))
