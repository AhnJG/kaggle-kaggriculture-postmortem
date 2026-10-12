"""EXP-062 S1 judge (written before results were inspected). P = mean over 55be-lineage opponents of (cand - d157) paired by (opp,seed,seat); d157 vs d157 = 0.5."""
import json,glob,collections,random,statistics as st,sys
L55=['d157','D55','HL63','M2965','FJ1010','c26','X']; ALL=L55+['N127','DP24']
extra=sys.argv[1].split(',') if len(sys.argv)>1 else []
ALL=ALL+[o for o in extra if o]
SEEDSET=set(json.load(open('experiments/exp062/s1_design.json'))['seeds'])
rows={}
for f in glob.glob('experiments/exp062/games-s1*.jsonl'):
    for l in open(f):
        r=json.loads(l)
        if r.get('score') is None or r['seed'] not in SEEDSET: continue
        rows[r['key']]=r
err=sum(1 for r in rows.values() if r['err'] or r['agent_errors'])
S=collections.defaultdict(dict)  # cand -> (opp,seed,seat) -> score
for r in rows.values(): S[r['vid']][(r['opponent'],r['seed'],r['seat'])]=r['score']
seeds=sorted({k[1] for c in S for k in S[c]})
def base(k): return 0.5 if k[0]=='d157' else S['d157'].get(k)
def stat(c,opps):
    per=collections.defaultdict(list)   # seed -> diffs
    byopp=collections.defaultdict(list)
    for k,v in S[c].items():
        if k[0] not in opps: continue
        b=base(k)
        if b is None: continue
        per[k[1]].append(v-b); byopp[k[0]].append(v-b)
    if not byopp: return None
    # equal weight per opponent
    P=st.mean(st.mean(v) for v in byopp.values())
    ss=list(per); rng=random.Random(1); bs=[]
    for _ in range(400):
        smp=[rng.choice(ss) for _ in ss]; d=[x for s in smp for x in per[s]]
        bs.append(st.mean(d))
    bs.sort(); n=sum(len(v) for v in byopp.values())
    return P,bs[20],bs[380],n,{o:round(st.mean(v),3) for o,v in byopp.items()}
print('rows',len(rows),'errors',err)
res=[]
for c in S:
    if c=='d157': continue
    a=stat(c,L55); b=stat(c,ALL)
    if a: res.append((a[0],c,a,b))
res.sort(reverse=True)
for P,c,a,b in res:
    raw=st.mean(S[c].values())
    print(f"{c:10s} P {a[0]:+.3f} [{a[1]:+.3f},{a[2]:+.3f}] n={a[3]:4d} | aux {b[0]:+.3f} n={b[3]:4d} | raw {raw:.3f} | {a[4]} {'N127:'+str(b[4].get('N127')) if 'N127' in b[4] else ''} {'DP24:'+str(b[4].get('DP24')) if 'DP24' in b[4] else ''}")
db=collections.defaultdict(list)
for k,v in S['d157'].items(): db[k[0]].append(v)
print('d157 raw vs pool', {o:(round(st.mean(v),3),len(v)) for o,v in db.items()})
