"""EXP-038 (Claude 09-28 12:30 KST): FAMILY ARENA for slot 2 — who is strongest inside the Step1009/1010 (55be-family) field
while keeping general strength. stdlib; repo root. -> experiments/exp038_family/{jobs-kaggle,jobs-mac}.json, tapes/, meta.json"""
import json,gzip,hashlib,os,csv
from pathlib import Path
OUT=Path('experiments/exp038_family');(OUT/'tapes').mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
X='analysis/daily_scan/20260928/extracted/'
V29={v['id']:v['path'] for v in json.load(open('experiments/exp029_dpnew_mirror/variants.json'))}
C=[('d157','releases/exp035-d157/main.py')]+[(k,V29[k]) for k in ('d053','d143','d093','d065','d064')]+\
  [('FJ1010',X+'farmer-john-and-the-idle-seller/main.py'),('M2965',X+'2965-master-engine/main.py')]
F=[('D','releases/public-dpnew-55be5d5f-exact/main.py'),('HL63',X+'kaggriculture-harvest-ledger/main.py'),
   ('M2965',X+'2965-master-engine/main.py'),('FJ1010',X+'farmer-john-and-the-idle-seller/main.py'),('d157','releases/exp035-d157/main.py')]
G=[('O127','releases/public-newmeta-127ed3e6-exact/main.py'),('V074','releases/round2-v074/main.py')]
for n,p in C+F+G:assert os.path.exists(p),p
exp={'d157':'94a46c11','D':'55be5d5f','HL63':'63dde9e4','M2965':'836cbfb6','FJ1010':'03165654','O127':'127ed3e6','V074':'860a502c'}
for n,p in C+F+G:
    if n in exp:assert sha(p).startswith(exp[n]),(n,sha(p)[:8])
jobs=[]
for c,cp in C:
    for o,op in F+G:
        if o==c:continue   # self-play is 0.5 by symmetry
        for s in range(15000,15025):
            for t in (0,1):jobs.append([c,cp,o,op,s,t])
# tapes: EXP-033 350 (v074/v171 era) + d157 hosted opponents (EXP-037)
meta=json.load(open('experiments/exp033_tapes/meta.json'))
for m in meta:
    for c,cp in C:jobs.append([c,cp,f"T{m['episode']}",f"experiments/exp033_tapes/tapes/T{m['episode']}.py",m['seed'],m['seat']])
lab={r['episode']:r for r in csv.DictReader(open('analysis/d157_hosted_20260928/opponents.csv'))}
nm=[]
for e in json.load(open('analysis/d157_hosted_20260928/episodes_all.json')):
    if e['submission_label']!='d157':continue
    raw=json.load(gzip.open(f"private_artifacts/d157_hosted_20260928/raw/{e['id']}.json.gz"));us=int(e['our_seat']);ns=1-us
    assert int(raw['info']['seed'])==int(e['seed'])
    tape=[raw['steps'][k+1][ns]['action'] for k in range(len(raw['steps'])-1)];p=OUT/'tapes'/f"U{e['id']}.py"
    p.write_text('TAPE='+json.dumps(tape)+'\ndef tape_agent(obs, configuration=None):\n    s=int(obs["step"])\n    return TAPE[s] if s<len(TAPE) else {"farmer":["PASS"],"hands":[],"market":[]}\n')
    r=lab[str(e['id'])];nm.append(dict(episode=e['id'],seed=int(e['seed']),seat=us,result=e['result'],label=r['label'],op_lb=e.get('op_lb_score')))
    for c,cp in C:jobs.append([c,cp,f"U{e['id']}",str(p),int(e['seed']),us])
json.dump(nm,open(OUT/'meta-d157.json','w'),indent=1)
k=[j for i,j in enumerate(jobs) if i%5<3];m=[j for i,j in enumerate(jobs) if i%5>=3]
json.dump(k,open(OUT/'jobs-kaggle.json','w'));json.dump(m,open(OUT/'jobs-mac.json','w'))
print('cands',len(C),'jobs',len(jobs),'kaggle',len(k),'mac',len(m),'d157 tapes',len(nm))
