"""EXP-032 (Claude 09-27 16:40 KST): 55be-family SPECIALIST gate for the 2nd slot. stdlib; run from repo root.
python experiments/exp032_specialist/prep32.py            -> jobs.json (d157, d053, P=v074 on all panels)
python experiments/exp032_specialist/prep32.py add b0xx.. -> jobs-add.json (EXP-030 finalists: vs-D panel only; other panels come from EXP-030 final)"""
import json,hashlib,sys
from pathlib import Path
OUT=Path('experiments/exp032_specialist');OUT.mkdir(parents=True,exist_ok=True)
D='releases/public-dpnew-55be5d5f-exact/main.py';P='releases/round2-v074/main.py';O2='releases/public-newmeta-127ed3e6-exact/main.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(D).startswith('55be5d5f') and sha(P).startswith('860a502c') and sha(O2).startswith('127ed3e6')
V29={v['id']:v for v in json.load(open('experiments/exp029_dpnew_mirror/variants.json'))}
C=[(k,V29[k]['path']) for k in ('d157','d053')]
for k,p in C:assert sha(p)==V29[k]['sha256']
guard=[g for g in json.load(open('experiments/exp027_stage3/manifest.json'))['guard'] if not g['sha256'].startswith('55be5d5f')]
def panel(jobs,agents,oid,op,seeds):
    for v,p in agents:
        for s in seeds:
            for t in (0,1):jobs.append([v,p,oid,op,s,t])
jobs=[]
if len(sys.argv)>1 and sys.argv[1]=='add':
    V30={v['id']:v for v in json.load(open('experiments/exp030_dpnew_bypass/variants.json'))}
    panel(jobs,[(k,V30[k]['path']) for k in sys.argv[2:]],'D',D,range(14300,14350))
    json.dump(jobs,open(OUT/'jobs-add.json','w'));print('add jobs',len(jobs));sys.exit()
A=C+[('P',P)]
panel(jobs,A,'D',D,range(14300,14350))
panel(jobs,C,'V074',P,range(14100,14150))
panel(jobs,A,'O127',O2,range(14100,14150))
for g in guard:panel(jobs,A,g['id'],g['path'],range(14200,14210))
eps=json.load(open('experiments/p4b_20260926/episodes.json'));seen=set()
for i,e in enumerate(eps):
    if e['id'] in seen:continue
    seen.add(e['id']);assert not 9000<=e['seed']<=9599
    for vv,pp in A:jobs.append([vv,pp,f"H{i:03d}-E{e['id']}",e['opp_path'],e['seed'],e['seat']])
json.dump(jobs,open(OUT/'jobs.json','w'));print('jobs',len(jobs),'guard',len(guard),'hosted',len(seen))
