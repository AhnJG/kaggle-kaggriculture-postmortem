"""python3 experiments/slot2_x/judge.py V1 [V2 ...] -> S-a, S-b vs d157 on the games available."""
import sys,json,os
base={}
for l in open('experiments/exp051_curpop/games.jsonl'):
    g=json.loads(l)
    if g['vid']=='d157':base[(g['opponent'],g['seed'],g['seat'])]=g['score']
order=[(j[2],j[4],j[5]) for j in json.load(open('experiments/exp051_curpop/jobs.json')) if j[0]=='d157']
for v in sys.argv[1:]:
    p=f'experiments/slot2_x/games-{v}.jsonl'
    if not os.path.exists(p):print(v,'no games');continue
    G={};err=0
    for l in open(p):
        g=json.loads(l)
        if g['err'] or g['agent_errors']:err+=1;continue
        G[(g['opponent'],g['seed'],g['seat'])]=g['score']
    ks=[k for k in order if k in G];n=len(ks)
    if not n:print(v,'0 games');continue
    sa=sum(G[k]-base[k] for k in ks)/n
    L=[k for k in ks if base[k]<1];W=[k for k in ks if base[k]==1]
    sb=sum(G[k]-base[k] for k in L)/max(1,len(L));sw=sum(G[k]-base[k] for k in W)/max(1,len(W))
    flips=sum(G[k]!=base[k] for k in ks)
    print(f"{v:8s} n={n:3d} err={err} X={sum(G[k] for k in ks)/n:.3f} d157={sum(base[k] for k in ks)/n:.3f} S-a={sa:+.3f} S-b(L{len(L)})={sb:+.3f} W{len(W)}={sw:+.3f} changed={flips}")
