"""SLOT2-R judge: S-a, S-b overall + parity halves + bootstrap (reference)."""
import sys,json,os,random
base={}
for l in open('experiments/exp051_curpop/games.jsonl'):
    g=json.loads(l)
    if g['vid']=='d157':base[g['opponent']]=g['score']
for v in sys.argv[1:]:
    p=f'experiments/slot2_x/games-{v}.jsonl'
    if not os.path.exists(p):p=f'experiments/slot2_x/gamesC-{v}.jsonl'
    G={}
    for l in open(p):
        g=json.loads(l)
        if g['err'] or g['agent_errors']:continue
        G[g['opponent']]=g['score']
    def stat(ks):
        n=len(ks);L=[k for k in ks if base[k]<1]
        return (sum(G[k]-base[k] for k in ks)/n, sum(G[k]-base[k] for k in L)/max(1,len(L)), n, len(L))
    ks=list(G);a=stat(ks);h0=stat([k for k in ks if int(k[1:])%2==0]);h1=stat([k for k in ks if int(k[1:])%2==1])
    rnd=random.Random(0);bs=[]
    for _ in range(2000):
        s=[rnd.choice(ks) for _ in ks];bs.append(stat(s)[1])
    bs.sort()
    ok=a[0]>=-0.03 and a[1]>=0.15 and all(h[1]>=0.10 and h[0]>=-0.06 for h in (h0,h1))
    print(f"{v:10s} n={a[2]} S-a={a[0]:+.3f} S-b={a[1]:+.3f} | even n={h0[2]} {h0[0]:+.3f}/{h0[1]:+.3f} | odd n={h1[2]} {h1[0]:+.3f}/{h1[1]:+.3f} | S-b boot5%={bs[100]:+.3f} | ELIGIBLE={ok and a[2]==269}")
