"""Fingerprint hosted opponents (d157 games, 55be-labelled) against newer Step1009 public files: count steps where file's action != opponent action."""
import sys,glob,os,json,gzip,contextlib,io,csv
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from kaggle_environments.utils import structify
from multiprocessing import Pool
X='analysis/daily_scan/20260928/extracted/'
FILES={'M2965':X+'2965-master-engine/main.py','HL63':X+'kaggriculture-top-2-master-engine-v4/main.py','HL8c':X+'kaggriculture-harvest-ledger/main.py',
       'FJ1010':X+'farmer-john-and-the-idle-seller/main.py','D':'releases/public-dpnew-55be5d5f-exact/main.py'}
OUT='analysis/exp050_divergence/fp50.jsonl'
def norm(a):
    a=a or {};return json.dumps({'m':(a.get('market') or [])[:10],'f':a.get('farmer'),'h':a.get('hands') or []},sort_keys=True)
def one(job):
    r,name=job;path=FILES[name]
    raw=json.load(gzip.open(f"private_artifacts/c26_hosted_20260929/raw/{r['episode']}.json.gz"));s=1-int(r['seat']);ns={'__name__':'fp'}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(open(path).read(),path,'exec'),ns)
    ag=[v for v in ns.values() if callable(v)][-1] if 'kaggle_submission_agent' not in ns else ns['kaggle_submission_agent']
    cfg=structify(raw['configuration']);nd=0;first=None
    for t in range(len(raw['steps'])-1):
        o=json.loads(json.dumps(raw['steps'][t][s]['observation']))
        for k in ('step','farms','market','town'):
            if k not in o:o[k]=raw['steps'][t][0]['observation'][k]
        try:
            with contextlib.redirect_stdout(io.StringIO()):p=ag(structify(o),cfg)
        except Exception:p=None
        if norm(p)!=norm(raw['steps'][t+1][s]['action']):
            nd+=1;first=t if first is None else first
    return {'episode':r['episode'],'file':name,'result':r['result'],'op':r['op_team'],'ndiff':nd,'first':first}
if __name__=='__main__':
    R=[r for r in csv.DictReader(open('analysis/c26_hosted_20260929/opponents.csv')) if r['submission_label']=='d157' and '55be' in r['label'] and r['result']!='D']
    done={(x['episode'],x['file']) for x in map(json.loads,open(OUT))} if os.path.exists(OUT) else set()
    todo=[(r,n) for r in R for n in FILES if (r['episode'],n) not in done];print('todo',len(todo),flush=True)
    with Pool(4) as p,open(OUT,'a') as f:
        for x in p.imap_unordered(one,todo):f.write(json.dumps(x)+'\n');f.flush()
