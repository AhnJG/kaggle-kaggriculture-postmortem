"""EXP-043 (Claude 09-28 18:10 KST): ORACLE — which existing bot beats the 5 weakest 2400+ teams where d157 loses?
Tapes: select-team (not holdout) episodes of juliencst, thisray, Hikaru Umeda, Shawn404, Fritz Cremer where d157 scored <1 in EXP-042.
Agents: 23 guard public files (exp027 manifest) + D, HL63, M2965, FJ1010, O127, DP-0924, V171."""
import json,collections
M={f"X{m['episode']}":m for m in json.load(open('experiments/exp041_top2400/meta.json'))}
H=set(json.load(open('experiments/exp041_top2400/team-split.json'))['holdout_teams'])
W={'juliencst','thisray','Hikaru Umeda','Shawn404','Fritz Cremer'};assert not W&H
d={}
for f in ('games42-kaggle.jsonl','games42-mac.jsonl'):
    for l in open('experiments/exp041_top2400/'+f):
        r=json.loads(l)
        if r['vid']=='d157' and r['score'] is not None:d[r['opponent']]=r['score']
T=sorted(o for o,s in d.items() if s<1 and M[o]['team'] in W)
X='analysis/daily_scan/20260928/extracted/'
A=[(g['id'],g['path']) for g in json.load(open('experiments/exp027_stage3/manifest.json'))['guard'] if not g['sha256'].startswith('55be5d5f')]
A+=[('D','releases/public-dpnew-55be5d5f-exact/main.py'),('HL63',X+'kaggriculture-harvest-ledger/main.py'),('M2965',X+'2965-master-engine/main.py'),
    ('FJ1010',X+'farmer-john-and-the-idle-seller/main.py'),('O127','releases/public-newmeta-127ed3e6-exact/main.py'),
    ('DP0924','releases/public-tetsutani-demand-preserving-0924-exact/main.py'),('V171','releases/mirror-screen-v171/main.py')]
J=[[v,p,o,f"experiments/exp041_top2400/tapes/{o}.py",M[o]['seed'],M[o]['our_seat']] for o in T for v,p in A]
k=[j for i,j in enumerate(J) if i%5<3];m=[j for i,j in enumerate(J) if i%5>=3]
json.dump(k,open('experiments/exp041_top2400/jobs43-kaggle.json','w'));json.dump(m,open('experiments/exp041_top2400/jobs43-mac.json','w'))
print('tapes',len(T),collections.Counter(M[o]['team'] for o in T),'agents',len(A),'jobs',len(J))
