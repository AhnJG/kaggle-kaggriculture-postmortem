"""Recompute stage1 evidence without importing the execution controller."""
import hashlib,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/search_20260925'
rows=[json.loads(x) for x in (OUT/'games.jsonl').read_text().splitlines()]
runtime=[x for x in rows if x['job']['variant']=='newmeta-runtime']
extra=[x for x in rows if x['job']['variant'] in {'newmeta-direct','newmeta-e5','dp-regression','determinism-0','determinism-1','determinism-2'} or x['job']['variant'].startswith('newmeta-panel-')]
checks=0
def check(x):
 global checks
 assert x
 checks+=1
check(len(runtime)==1000)
check({(x['job']['seed'],x['job']['seat']) for x in runtime}=={(s,p) for s in range(10000,10500) for p in (0,1)})
check(len(extra)==151)
check(len({x['key'] for x in runtime+extra})==1151)
expected='127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652'
source=(ROOT/'releases/public-newmeta-127ed3e6-exact/main.py').read_bytes()
check(hashlib.sha256(source).hexdigest()==expected)
check(source.count(b'\r\n')==7482)
with tarfile.open(ROOT/'releases/public-newmeta-127ed3e6-exact/submission.tar.gz') as t:
 check(t.getnames()==['main.py']);check(t.extractfile('main.py').read()==source)
for x in runtime+extra:
 j=x['job'];r=x['result']
 check(hashlib.sha256((ROOT/j['path']).read_bytes()).hexdigest()==j['sha256']==r['sha256'])
 check(hashlib.sha256((ROOT/j['opponent']).read_bytes()).hexdigest()==j['opponent_sha256']==r['opponent_sha256'])
 check(j['seed']==r['seed'] and j['seat']==r['seat'])
 check(r['steps']==720 and r['statuses']==['DONE','DONE'])
 check(not any(r['exceptions']) and not r['caught_errors'])
 check(r['margin']==r['rewards'][j['seat']]-r['rewards'][1-j['seat']])
 check(r['score']==(1 if r['margin']>0 else 0 if r['margin']<0 else .5))
s=json.loads((OUT/'stage1-summary.json').read_text())
for label,selected in [('runtime',runtime),('direct',[r for r in extra if r['job']['variant']=='newmeta-direct']),('e5',[r for r in extra if r['job']['variant']=='newmeta-e5']),('panel',[r for r in extra if r['job']['variant'].startswith('newmeta-panel-')])]:
 scores=[r['result']['score'] for r in selected]
 check([scores.count(1),scores.count(.5),scores.count(0)]==[s[label]['wins'],s[label]['draws'],s[label]['losses']])
 check(max(r['result']['timing'][0]['max_seconds'] for r in selected)==s[label]['max_step'])
check(s['runtime']['max_step']>=.25 and s['verdict']=='NOT_ELIGIBLE')
(OUT/'stage1-games.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in runtime+extra))
v={'status':'PASS','checks':checks,'runtime_verdict':'NOT_ELIGIBLE','snapshot_sha256':hashlib.sha256((OUT/'stage1-games.jsonl').read_bytes()).hexdigest()}
(OUT/'stage1-verification.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v))
