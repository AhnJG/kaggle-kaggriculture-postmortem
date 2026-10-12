"""EXP-048 Stage B jobs (Claude 09-29, per PREREG + ADDENDUM). Candidates from Stage A: hook (+0.0109), K3 (+0.0042).
Panels: exp039 panel (U136+T350+family 250+O127 50+V074 50) for candidates; old holdout 148 (exp041) for candidates;
fresh exp049 (302 parity-ok tapes) for d157, c26, hook, K3."""
import json,collections
C={'hook':'experiments/exp047_oppmodel/variants/hook.py','K3':'experiments/exp045_sale/variants/K3.py'}
BASE={'d157':'releases/exp035-d157/main.py','c26':'experiments/exp039_camargin/variants/c26.py'}
J39=json.load(open('experiments/exp039_camargin/jobs-kaggle.json'))+json.load(open('experiments/exp039_camargin/jobs-mac.json'))
J=[]
for v,p in C.items():J+=[[v,p]+j[2:] for j in J39 if j[0]=='c26']
B='experiments/exp041_top2400/';H=set(json.load(open(B+'team-split.json'))['holdout_teams'])
M=list({m['episode']:m for m in json.load(open(B+'meta.json'))}.values())
for v,p in C.items():J+=[[v,p,f"X{m['episode']}",B+f"tapes/X{m['episode']}.py",m['seed'],m['our_seat']] for m in M if m['team'] in H]
F=json.load(open('experiments/exp049_fresh/meta.json'));bad=set(r[0] for r in map(json.loads,open('experiments/exp049_fresh/parity.jsonl')) if not r[1])
for v,p in {**BASE,**C}.items():J+=[[v,p,f"F{m['episode']}",f"experiments/exp049_fresh/tapes/F{m['episode']}.py",m['seed'],m['our_seat']] for m in F if m['episode'] not in bad]
assert not any(9000<=j[4]<9600 for j in J) and len({(j[0],j[2],j[4],j[5]) for j in J})==len(J)
k=[j for i,j in enumerate(J) if i%5<3];mm=[j for i,j in enumerate(J) if i%5>=3]
json.dump(k,open('experiments/exp048_stageB/jobs-kaggle.json','w'));json.dump(mm,open('experiments/exp048_stageB/jobs-mac.json','w'))
print(len(J),len(k),len(mm),collections.Counter(j[0] for j in J),'fresh bad excluded',len(bad))
