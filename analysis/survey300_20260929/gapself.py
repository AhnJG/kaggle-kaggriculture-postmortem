"""d157/c26 own hosted games vs top300 feature means + within own games (Claude 09-29)."""
import json,csv,collections,statistics as st,sys,random
sys.argv=[sys.argv[0]]
exec(open('analysis/survey300_20260929/an300.py').read().split("rows=[]")[0])  # reuse feats, rank, X(survey)
lab={r['episode']:r['submission_label'] for r in csv.DictReader(open('analysis/hosted_20260929b/opponents.csv'))}
S=[json.loads(l) for l in open('analysis/survey300_20260929/featself.jsonl')]
top=collections.defaultdict(list)
for x in X:
    for s in (0,1):
        rk=rank.get(x['teams'][s])
        if rk and rk<=300:top[x['teams'][s]].append(feats(x['seat'][str(s)],None))
K=list(next(iter(top.values()))[0].keys())
tm={k:st.mean(st.mean(f[k] for f in v) for v in top.values()) for k in K}
for L in ('d157','c26'):
    own=[];opp=[];res=[]
    for x in S:
        if lab.get(x['episode'])!=L:continue
        s=x['teams'].index('Sian');o=1-s
        a=feats(x['seat'][str(s)],None);b=feats(x['seat'][str(o)],None);own.append(a);opp.append(b)
        res.append(1 if x['rewards'][s]>x['rewards'][o] else 0 if x['rewards'][s]<x['rewards'][o] else .5)
    print(f'\n== {L} games {len(own)} score {st.mean(res):.3f}')
    print(f'{"feature":22s} {"own":>8s} {"opp":>8s} {"top300":>8s} | own-opp in W vs L')
    for k in K:
        w=[a[k]-b[k] for a,b,r in zip(own,opp,res) if r==1];l=[a[k]-b[k] for a,b,r in zip(own,opp,res) if r==0]
        print(f'{k:22s} {st.mean(f[k] for f in own):8.1f} {st.mean(f[k] for f in opp):8.1f} {tm[k]:8.1f} | W {st.mean(w) if w else 0:+8.1f}  L {st.mean(l) if l else 0:+8.1f}')
