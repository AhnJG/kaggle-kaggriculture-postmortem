"""EXP-028 (Claude): 55be5d5f exact (D) vs v074 (P) on identical closed-loop panels. stdlib only; run from repo root."""
import hashlib,json
from pathlib import Path
OUT=Path('experiments/exp028_dpnew');OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
D='releases/public-dpnew-55be5d5f-exact/main.py';assert sha(D).startswith('55be5d5f')
P='releases/round2-v074/main.py';assert sha(P).startswith('860a502c')
O1='releases/public-newmeta-127ed3e6-exact/main.py';DP='releases/public-tetsutani-demand-preserving-0924-exact/main.py'
guard=[g for g in json.load(open('experiments/exp027_stage3/manifest.json'))['guard'] if not g['sha256'].startswith('55be5d5f')]
A=[('D',D),('P',P)];jobs=[]
def panel(oid,op,seeds):
    for v,p in A:
        for s in seeds:
            for t in (0,1):jobs.append([v,p,oid,op,s,t])
panel('O1-127ed3e6',O1,range(12000,12100));panel('DP-old',DP,range(12100,12150))
for g in guard:panel(g['id'],g['path'],range(12200,12210))
for i,e in enumerate(json.load(open('experiments/p4b_20260926/episodes.json'))):
    assert not 9000<=e['seed']<=9599
    for v,p in A:jobs.append([v,p,f"H{i:03d}-E{e['id']}",e['opp_path'],e['seed'],e['seat']])
panel('X-D-vs-P',P,range(12300,12350))  # direct: D vs v074 (only D row is meaningful; P row = v074 self-play)
json.dump(jobs,open(OUT/'jobs.json','w'));print(len(jobs),len(guard))
