"""SLOT2-R holdout verdict (PREREG_R rev3/rev4). python3 experiments/slot2_x/judgeH.py VARIANT"""
import sys,json,glob
v=sys.argv[1];D='experiments/slot2_x/holdout/'
def load(P,name):
    G={}
    for f in glob.glob(f'{D}games-{P}-{name}.jsonl')+glob.glob(f'{D}gamesC-{P}-{name}.jsonl'):
        for l in open(f):
            g=json.loads(l)
            if not g['err'] and not g['agent_errors']:G[g['opponent']]=g
    return G
res={}
for P in ('HF','HT'):
    d,c,x=load(P,'d157'),load(P,'c26'),load(P,v);ks=[k for k in x if k in d and k in c]
    n=len(ks);m=lambda G,S:sum(G[k]['score'] for k in S)/max(1,len(S))
    L=[k for k in ks if d[k]['score']<1];gate=[k for k in ks if x[k]['act_sha']!=c[k]['act_sha']]
    res[P]=dict(n=n,X=m(x,ks),d157=m(d,ks),c26=m(c,ks),Xd=m(x,ks)-m(d,ks),Xc=m(x,ks)-m(c,ks),nL=len(L),Ld=m(x,L)-m(d,L),Lc=m(c,L)-m(d,L),
        ngate=len(gate),gate_Xc=m(x,gate)-m(c,gate),port=sum(max(d[k]['score'],x[k]['score'])-max(d[k]['score'],c[k]['score']) for k in ks)/n,
        missing=len(x)-n)
    print(P,{k:(round(val,3) if isinstance(val,float) else val) for k,val in res[P].items()})
HF,HT=res['HF'],res['HT']
checks={'H-a HF X-d157>=-0.03':HF['Xd']>=-0.03,'H-b HF L X-d157>=+0.10':HF['Ld']>=0.10,'H-c HT X-d157>=-0.05':HT['Xd']>=-0.05,
        'H-d HF X-c26>=-0.03':HF['Xc']>=-0.03,'H-e HF gated X-c26>=-0.10':HF['gate_Xc']>=-0.10}
for k,ok in checks.items():print(('PASS ' if ok else 'FAIL ')+k)
print('ALL (excl. D3/closed-loop):','PASS' if all(checks.values()) else 'FAIL')
