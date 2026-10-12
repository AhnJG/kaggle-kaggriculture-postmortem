"""EXP-060 M1 판정 (PREREG sha 137f92985e2f 규칙): 그룹별 FM 41 + d157 평균, 상위 3 route."""
import json,collections,hashlib
assert hashlib.sha256(open('experiments/exp060_mbr/PREREG.md','rb').read()).hexdigest().startswith('137f92985e2f')
S=json.load(open('experiments/exp060_mbr/sets.json'))['screen']
grp={(x['seed'],x['seat']):x['group'] for x in S}
G={}; bad=0
for f in ('experiments/exp060_mbr/games-m1-kaggle.jsonl','experiments/exp060_mbr/games-m1-mac.jsonl'):
    for l in open(f):
        r=json.loads(l)
        if r.get('err') or r.get('agent_errors') or r['statuses'][r['seat']]!='DONE': bad+=1; continue
        G[(r['vid'],r['seed'],r['seat'])]=r
print('rows',len(G),'bad',bad)
arms=sorted({k[0] for k in G})
out={}
for g in ('Y','D','S'):
    ks=[k for k,v in grp.items() if v==g]
    M={}
    for a in arms:
        v=[G[(a,)+k] for k in ks if (a,)+k in G]
        if len(v)==len(ks): M[a]=(sum(r['score'] for r in v)/len(v), sum(r['margin'] for r in v)/len(v))
    nat=M['d157']
    fm=sorted([(m[0],m[1],a) for a,m in M.items() if a.startswith('FM')],reverse=True)
    top3=[a for _,_,a in fm[:3]]
    out[g]={'n':len(ks),'d157':nat,'FM107':M.get('FM107'),'top3':top3,'top10':[(a,round(s,3),round(mg)) for s,mg,a in fm[:10]]}
    print(g,'n',len(ks),'d157',round(nat[0],3),'FM107',round(M['FM107'][0],3),'top10',out[g]['top10'])
json.dump(out,open('experiments/exp060_mbr/m1_verdict.json','w'),indent=1)
