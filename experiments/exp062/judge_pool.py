"""A6 pick: pooled S1+S2 P (55be pool L55, opponent-equal) vs d157, seed bootstrap. Claude-B 11:00 KST."""
import json,glob,collections,random,statistics as st
L55=['d157','D55','HL63','M2965','FJ1010','c26','X']
S1=set(json.load(open('experiments/exp062/s1_design.json'))['seeds']); S2=set(json.load(open('experiments/exp062/s2_design.json'))['seeds'])
S=collections.defaultdict(dict)
for f in glob.glob('experiments/exp062/games-*.jsonl'):
    for l in open(f):
        r=json.loads(l)
        if r.get('score') is None or (r['seed'] not in S1 and r['seed'] not in S2): continue
        S[r['vid']][(r['opponent'],r['seed'],r['seat'])]=r['score']
def base(k): return 0.5 if k[0]=='d157' else S['d157'].get(k)
for c in ['L3p','L4p','L6p']:
    byo=collections.defaultdict(list); bys=collections.defaultdict(list); n1=n2=0
    for k,v in S[c].items():
        if k[0] not in L55: continue
        b=base(k)
        if b is None: continue
        byo[k[0]].append(v-b); bys[k[1]].append(v-b)
        if k[1] in S1: n1+=1
        else: n2+=1
    P=st.mean(st.mean(v) for v in byo.values())
    rng=random.Random(7); ss=list(bys)
    bs=sorted(st.mean([x for s in [rng.choice(ss) for _ in ss] for x in bys[s]]) for _ in range(2000))
    print(f"{c} pooled P {P:+.3f} 90% [{bs[100]:+.3f},{bs[1900]:+.3f}] n_S1={n1} n_S2={n2}", {o:round(st.mean(v),3) for o,v in byo.items()})
