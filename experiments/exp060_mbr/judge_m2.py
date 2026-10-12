"""EXP-060 M2 판정 (PREREG 137f92985e2f). 그룹별: M2 arm 중 확인 집합 평균 최고 r*. r*!=기존(d157)이고
(r*-기존)>=+0.05, tape 단위 bootstrap 2000회 90% 구간 하한(5퍼센타일)>0 이면 채택, 아니면 기존.
동점: 기존 -> FM107 -> 번호 작은 순. FM9(Y 의 기존 route 와 같음)가 이기면 기존으로 본다."""
import json,random,hashlib
assert hashlib.sha256(open('experiments/exp060_mbr/PREREG.md','rb').read()).hexdigest().startswith('137f92985e2f')
A=json.load(open('experiments/exp060_mbr/m2_arms.json'))
C=json.load(open('experiments/exp060_mbr/sets.json'))['confirm']
G={}
for f in ('experiments/exp060_mbr/games-m2-kaggle.jsonl','experiments/exp060_mbr/games-m2-mac.jsonl'):
    for l in open(f):
        r=json.loads(l); G[(r['vid'],r['seed'],r['seat'])]=r
bad=sum(1 for r in G.values() if r.get('err') or r.get('agent_errors') or r['statuses'][r['seat']]!='DONE')
def order(a): return (0 if a=='d157' else 1 if a=='FM107' else 2, int(''.join(c for c in a if c.isdigit()) or 0))
out={'bad_rows':bad,'groups':{}}
for g,arms in A.items():
    ks=[(c['seed'],c['seat']) for c in C if c['group']==g]
    ok=[k for k in ks if all((a,)+k in G for a in arms)]
    S={a:[G[(a,)+k]['score'] for k in ok] for a in arms}
    mean={a:sum(v)/len(v) for a,v in S.items()}
    best=sorted(arms,key=lambda a:(-mean[a],order(a)))[0]
    d=[x-y for x,y in zip(S[best],S['d157'])]
    rng=random.Random(60); bs=sorted(sum(rng.choice(d) for _ in d)/len(d) for _ in range(2000))
    lo=bs[int(0.05*2000)]; diff=sum(d)/len(d)
    adopt= best not in ('d157','FM9') and diff>=0.05 and lo>0
    out['groups'][g]={'n':len(ok),'of':len(ks),'means':{a:round(m,3) for a,m in sorted(mean.items(),key=lambda x:-x[1])},
                      'best':best,'diff_vs_d157':round(diff,3),'lo90':round(lo,3),'adopt':adopt,'route':best if adopt else 'native'}
    print(g,out['groups'][g])
print('bad rows',bad)
json.dump(out,open('experiments/exp060_mbr/m2_verdict.json','w'),indent=1)
