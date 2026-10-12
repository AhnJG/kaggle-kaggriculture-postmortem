"""EXP-033 (Claude 09-27 17:10 KST): open-loop TAPE field panel from EXP-031 hosted replays (v074+v171, 350 eps).
Each opponent tape -> tiny agent file; jobs in standard run.py format. stdlib; run from repo root."""
import json,gzip,csv,hashlib,os
OUT='experiments/exp033_tapes';RAW='private_artifacts/v074_hosted_20260927/raw/';os.makedirs(OUT+'/tapes',exist_ok=True)
eps=json.load(open('analysis/v074_hosted_20260927/episodes_all.json'))
lab={int(r['episode']):r for r in csv.DictReader(open('analysis/v074_hosted_20260927/opponents.csv'))}
def fam(r):
    l=r['label']
    if r['is_full']=='True' and '55be5d5f' in l:return '55be_full'
    if r['is_full']=='True' and '127ed3e6' in l:return '127_full'
    if '127ed3e6' in l:return '127_near'
    if '55be5d5f' in l or 'DP-0924' in l or 'a-smaller' in l:return 'dp_near'
    return 'other'
meta=[];jobs=[]
A=[('P','releases/round2-v074/main.py'),('V171','releases/mirror-screen-v171/main.py'),('D','releases/public-dpnew-55be5d5f-exact/main.py'),
   ('d157','experiments/exp029_dpnew_mirror/variants/d157.py'),('d053','experiments/exp029_dpnew_mirror/variants/d053.py')]
for e in eps:
    seed=int(e['seed']);us=int(e['our_seat']);ns=1-us;p=f"{OUT}/tapes/T{e['id']}.py"
    if not (os.path.exists(p) and os.path.getsize(p)>1000 and open(p).read().rstrip().endswith('configuration=None):\n    s=int(obs["step"])\n    return TAPE[s] if s<len(TAPE) else {"farmer":["PASS"],"hands":[],"market":[]}'.rstrip())):
      raw=json.load(gzip.open(f"{RAW}{e['id']}.json.gz"));assert int(raw['info']['seed'])==seed
      tape=[raw['steps'][k+1][ns]['action'] for k in range(len(raw['steps'])-1)]
      open(p,'w').write('TAPE='+json.dumps(tape)+'\ndef tape_agent(obs, configuration=None):\n    s=int(obs["step"])\n    return TAPE[s] if s<len(TAPE) else {"farmer":["PASS"],"hands":[],"market":[]}\n')
    r=lab[int(e['id'])];meta.append(dict(episode=e['id'],sub=e['submission_label'],seed=seed,seat=us,result=e['result'],fam=fam(r),label=r['label'],endTime=e['endTime'],op_lb=e.get('op_lb_score')))
    for v,ap in A:jobs.append([v,ap,f"T{e['id']}",p,seed,us])
order={'127_near':0,'dp_near':1,'55be_full':1,'other':2,'127_full':3}
fm={m['episode']:m['fam'] for m in meta}
jobs.sort(key=lambda j:(order[fm[int(j[2][1:])]],j[2],j[0]))
json.dump(meta,open(OUT+'/meta.json','w'),indent=1);json.dump(jobs,open(OUT+'/jobs.json','w'))
import collections;print('eps',len(meta),'jobs',len(jobs),collections.Counter(m['fam'] for m in meta))
