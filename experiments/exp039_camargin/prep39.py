"""EXP-039 (Claude 09-28 14:30 KST): d157' = d157 + _CA_MARGIN grid (M2965 insight: -22 gave +0.023 on 390 hosted tapes).
Panels: all 136 d157-hosted opponent tapes (current rating band) + EXP-033 350 tapes + family arena (D,HL63,M2965,FJ1010,d157) + O127,V074.
stdlib; repo root. -> experiments/exp039_camargin/"""
import json,gzip,hashlib,os
from pathlib import Path
OUT=Path('experiments/exp039_camargin');(OUT/'tapes').mkdir(parents=True,exist_ok=True);(OUT/'variants').mkdir(exist_ok=True)
X='analysis/daily_scan/20260928/extracted/'
BASE='releases/exp035-d157/main.py';src=Path(BASE).read_bytes();assert hashlib.sha256(src).hexdigest().startswith('94a46c11')
C=[('d157',BASE)]
for m in (-18.0,-22.0,-26.0,-30.0):
    t=f"\n# Frozen EXP-039 wrapper; d157 bytes above unchanged.\n_EXP039_ENTRY = [v for v in globals().values() if callable(v)][-1]\n_CA_MARGIN = {m!r}\ndef exp039_entry(obs, configuration=None):\n    return _EXP039_ENTRY(obs, configuration)\n"
    b=src+t.encode();p=OUT/'variants'/f'c{int(-m)}.py';p.write_bytes(b);compile(b,str(p),'exec');C.append((f'c{int(-m)}',str(p)))
F=[('D','releases/public-dpnew-55be5d5f-exact/main.py'),('HL63',X+'kaggriculture-harvest-ledger/main.py'),('M2965',X+'2965-master-engine/main.py'),
   ('FJ1010',X+'farmer-john-and-the-idle-seller/main.py'),('d157',BASE),('O127','releases/public-newmeta-127ed3e6-exact/main.py'),('V074','releases/round2-v074/main.py')]
jobs=[]
for c,cp in C:
    for o,op in F:
        if o==c:continue
        for s in range(15000,15025):
            for t in (0,1):jobs.append([c,cp,o,op,s,t])
for m in json.load(open('experiments/exp033_tapes/meta.json')):
    for c,cp in C:jobs.append([c,cp,f"T{m['episode']}",f"experiments/exp033_tapes/tapes/T{m['episode']}.py",m['seed'],m['seat']])
nm=[]
for e in json.load(open('analysis/d157_hosted_20260928/episodes_all.json')):
    if e['submission_label']!='d157':continue
    p=OUT/'tapes'/f"U{e['id']}.py"
    if not p.exists():
        raw=json.load(gzip.open(f"private_artifacts/d157_hosted_20260928/raw/{e['id']}.json.gz"));us=int(e['our_seat']);ns=1-us
        assert int(raw['info']['seed'])==int(e['seed'])
        tape=[raw['steps'][k+1][ns]['action'] for k in range(len(raw['steps'])-1)]
        p.write_text('TAPE='+json.dumps(tape)+'\ndef tape_agent(obs, configuration=None):\n    s=int(obs["step"])\n    return TAPE[s] if s<len(TAPE) else {"farmer":["PASS"],"hands":[],"market":[]}\n')
    nm.append(dict(episode=e['id'],seed=int(e['seed']),seat=int(e['our_seat']),result=e['result'],op_lb=e.get('op_lb_score')))
    for c,cp in C+[('V074','releases/round2-v074/main.py')]:jobs.append([c,cp,f"U{e['id']}",str(p),int(e['seed']),int(e['our_seat'])])
json.dump(nm,open(OUT/'meta-u.json','w'),indent=1)
k=[j for i,j in enumerate(jobs) if i%5<3];m=[j for i,j in enumerate(jobs) if i%5>=3]
json.dump(k,open(OUT/'jobs-kaggle.json','w'));json.dump(m,open(OUT/'jobs-mac.json','w'))
print('cands',len(C),'jobs',len(jobs),'kaggle',len(k),'mac',len(m),'U tapes',len(nm))
