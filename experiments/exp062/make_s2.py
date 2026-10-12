"""S2 jobs: python make_s2.py name1,name2,name3  -> jobs-s2-{mac,kaggle}.json (closed-loop fresh seeds + VP proxy) and jobs-s2nm.json (non-mirror tapes)."""
import json,random,sys,os
D=json.load(open('experiments/exp062/s1_design.json'))
def path(n):
    if n=='d157': return 'releases/exp035-d157/main.py'
    for d in ('experiments/exp062/variants','experiments/exp045_sale/variants'):
        p=f'{d}/{n[3:] if n.startswith("E45") else n}.py'
        if os.path.exists(p): return p
    raise SystemExit('no '+n)
names=sys.argv[1].split(',')+['d157']
POOL=dict(D['pool']); POOL['VP']='experiments/exp062/variants/L1p.py'
rng=random.Random(62010);SEEDS=[rng.randrange(1,2**31-1) for _ in range(30)]
J=[[c,path(c),o,op,s,seat] for s in SEEDS for seat in (0,1) for o,op in POOL.items() for c in names if not (c=='d157' and o=='d157')]
rng.shuffle(J)
NM=json.load(open('experiments/exp062/panel_nm.json'))
T=[[c,path(c),x['tape'].split('/')[-1][:-3],x['tape'],x['seed'],x['seat']] for x in NM for c in names]
k=[j for i,j in enumerate(J) if i%2==0]; m=[j for i,j in enumerate(J) if i%2==1]+T
json.dump(k,open('experiments/exp062/jobs-s2-kaggle.json','w'));json.dump(m,open('experiments/exp062/jobs-s2-mac.json','w'))
json.dump({'names':names,'seeds':SEEDS,'pool':POOL,'n_closed':len(J),'n_nm':len(T)},open('experiments/exp062/s2_design.json','w'),indent=1)
print('closed',len(J),'nm',len(T),'kaggle',len(k),'mac',len(m))
