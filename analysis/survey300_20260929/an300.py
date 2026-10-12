"""SURVEY300 analysis per PLAN.md (paired within-game primary; team-level secondary with team-cluster bootstrap + BH-FDR)."""
import json,zipfile,csv,collections,random,statistics as st,math
X=[json.loads(l) for l in open('analysis/survey300_20260929/feat300.jsonl')];X=[x for x in X if 'error' not in x and x['parity']]
z=zipfile.ZipFile('analysis/survey300_20260929/kaggriculture.zip');L=list(csv.DictReader(z.read(z.namelist()[0]).decode('utf-8-sig').splitlines()))
rank={}
for r in L:rank.setdefault(r['TeamName'],int(r['Rank']))
ITEMS=['TOMATO','STRAWBERRY','MILK','WOOL','EGG','CARROT','WHEAT','FERTILIZER','MELON']
def feats(sd,other):
    f={}
    for k in ('288','576'):
        s=sd['snap'+k]
        for c in ('C_TOMATO','C_STRAWBERRY','C_CARROT','C_WHEAT','C_MELON','A_COW','A_SHEEP','A_GOOSE'):f[f'{c}@{k}']=s.get(c,0)
    fl=sd['flows'];days=sorted(int(k.split('|')[1]) for k in fl if k.startswith('LANDDAY'))
    for i in range(3):f[f'land{i+1}_day']=days[i] if len(days)>i else 30
    f['hires']=fl.get('HIRE|-',[0,0])[0];f['hire_cost']=fl.get('HIRE|-',[0,0])[1]
    for it in ITEMS:
        u,c=fl.get(f'SELL|{it}',[0,0]);f[f'sell_u_{it}']=u;f[f'sell_rev_{it}']=c
    f['buy_wheat_u']=fl.get('BUY_PRODUCT|WHEAT',[0,0])[0];f['buy_fert_u']=fl.get('BUY_PRODUCT|FERTILIZER',[0,0])[0]
    f['animals_cost']=sum(v[1] for k,v in fl.items() if k.startswith('BUY_ANIMAL'));f['seed_cost']=sum(v[1] for k,v in fl.items() if k.startswith('BUY_SEED'))
    return f
rows=[]
for x in X:
    t=x['teams'];r=[rank.get(t[0]),rank.get(t[1])];F=[feats(x['seat']['0'],None),feats(x['seat']['1'],None)]
    rows.append((x,t,r,F))
K=list(rows[0][3][0].keys())
def boot(vals,groups=None,n=1000):
    rng=random.Random(0)
    if groups is None:
        m=[st.mean(rng.choices(vals,k=len(vals))) for _ in range(n)]
    else:
        G=collections.defaultdict(list)
        for v,g in zip(vals,groups):G[g].append(v)
        ks=list(G);m=[]
        for _ in range(n):
            s=[v for k in rng.choices(ks,k=len(ks)) for v in G[k]];m.append(st.mean(s))
    m.sort();return m[int(.025*n)],m[int(.975*n)]
print('games (unique, parity ok):',len(rows))
# 1) within-game winner - loser
pairs=[(F[0],F[1]) if x['rewards'][0]>x['rewards'][1] else (F[1],F[0]) for x,t,r,F in rows if x['rewards'][0]!=x['rewards'][1]]
print('\n[1] within-game winner − loser (n=%d)'%len(pairs))
res1=[]
for k in K:
    d=[w[k]-l[k] for w,l in pairs];mu=st.mean(d);lo,hi=boot(d,n=500);sd=st.pstdev(d) or 1
    res1.append((abs(mu)/sd,k,mu,lo,hi))
for es,k,mu,lo,hi in sorted(res1,reverse=True)[:16]:print(f'  {k:22s} Δ {mu:+9.2f}  CI [{lo:+.2f},{hi:+.2f}]  effect {es:.2f}')
# 2) team-level top300 vs band600-1300
seatrows=[]
for x,t,r,F in rows:
    for s in (0,1):
        if r[s] is None:continue
        g='top' if r[s]<=300 else 'band' if 600<=r[s]<=1300 else None
        if g:seatrows.append((g,t[s],F[s]))
print('\n[2] team-level top300 vs band (seats: top %d, band %d; teams top %d, band %d)'%(sum(g=='top' for g,_,_ in seatrows),sum(g=='band' for g,_,_ in seatrows),len({n for g,n,_ in seatrows if g=='top'}),len({n for g,n,_ in seatrows if g=='band'})))
res2=[]
for k in K:
    tm=collections.defaultdict(list)
    for g,n,f in seatrows:tm[(g,n)].append(f[k])
    top=[st.mean(v) for (g,n),v in tm.items() if g=='top'];band=[st.mean(v) for (g,n),v in tm.items() if g=='band']
    if not top or not band:continue
    diff=st.mean(top)-st.mean(band)
    # bootstrap over teams
    rng=random.Random(1);bs=[]
    for _ in range(500):bs.append(st.mean(rng.choices(top,k=len(top)))-st.mean(rng.choices(band,k=len(band))))
    se=st.pstdev(bs) or 1e-9;z_=diff/se;p=math.erfc(abs(z_)/math.sqrt(2))
    res2.append((p,k,st.mean(top),st.mean(band),diff))
res2.sort();m=len(res2)
print('  feature                top300   band   diff   p   BH<0.1')
for i,(p,k,a,b,d) in enumerate(res2[:20]):print(f'  {k:22s} {a:8.2f} {b:8.2f} {d:+8.2f} {p:.4f} {"*" if p<=0.1*(i+1)/m else ""}')
