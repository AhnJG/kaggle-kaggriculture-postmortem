"""Stage A judge (Claude, written before results; rule = analysis/exp045/PREREG.md Stage A).
paired diff vs d157 (games42 rows) on select 595; keep point>0, top3 by point (tie: fewer changed-act games... approximated by fewer score flips).
Also prints c26 reference and team-cluster bootstrap (info only; not a gate because select is used for selection)."""
import json,collections,random,os
B='experiments/exp041_top2400/';H=set(json.load(open(B+'team-split.json'))['holdout_teams'])
M={f"X{m['episode']}":m for m in json.load(open(B+'meta.json'))}
base=collections.defaultdict(dict)
for f in ('games42-kaggle.jsonl','games42-mac.jsonl'):
    for l in open(B+f):
        r=json.loads(l)
        if r['score'] is not None:base[r['vid']][r['opponent']]=r['score']
R=collections.defaultdict(dict);bad=collections.Counter()
for f in ('experiments/exp048_stageA/games-kaggle.jsonl','experiments/exp048_stageA/games-mac.jsonl'):
    if not os.path.exists(f):continue
    for l in open(f):
        r=json.loads(l)
        if r['score'] is None or r['err'] or r['agent_errors'] or r['statuses']!=['DONE','DONE'] or r.get('action_count')!=719:bad[r['vid']]+=1;continue
        R[r['vid']][r['opponent']]=r['score']
T=[o for o in base['d157'] if M[o]['team'] not in H]
def boot(d,n=2000):
    teams=collections.defaultdict(list)
    for o,x in d.items():teams[M[o]['team']].append(x)
    ks=list(teams);rng=random.Random(0);v=[]
    for _ in range(n):
        s=[x for k in (rng.choice(ks) for _ in ks) for x in teams[k]];v.append(sum(s)/len(s))
    v.sort();return v[int(.025*n)]
print('select tapes',len(T),'d157',round(sum(base['d157'][o] for o in T)/len(T),3),'c26',round(sum(base['c26'][o] for o in T if o in base['c26'])/len(T),3))
rows=[]
for v in sorted(R):
    O=[o for o in T if o in R[v]];d={o:R[v][o]-base['d157'][o] for o in O}
    pt=sum(d.values())/len(O) if O else float('nan');fl=sum(1 for x in d.values() if x!=0)
    rows.append((pt,-fl,v,len(O),bad[v],fl,boot(d) if O else None,sum(R[v][o] for o in O)/len(O) if O else None))
rows.sort(reverse=True)
print('| variant | n | invalid | score | Δ vs d157 | flips | team-boot lo95 (info) |')
for pt,_,v,n,b,fl,lo,sc in rows:print(f'| {v} | {n} | {b} | {sc:.3f} | {pt:+.4f} | {fl} | {lo:+.4f} |')
inc=[r for r in rows if r[3]==len(T)]
sel=[r[2] for r in rows if r[0]>0 and r[3]==len(T) and r[4]==0][:3]
print('INCOMPLETE' if len(inc)<len(rows) else '', 'STAGE_B:',sel or 'LOCAL_FAILED (none > 0)')
