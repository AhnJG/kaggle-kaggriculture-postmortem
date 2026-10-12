import sys,glob,os,json,gzip,contextlib,io,csv
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from kaggle_environments.utils import structify
from multiprocessing import Pool
P='analysis/daily_scan/20260928/extracted/kaggriculture-top-2-master-engine-v4/main.py'
def norm(a):
    a=a or {};return {'m':(a.get('market') or [])[:10],'f':a.get('farmer'),'h':a.get('hands') or []}
def one(ep):
    r=[x for x in csv.DictReader(open('analysis/c26_hosted_20260929/opponents.csv')) if x['episode']==ep and x['submission_label']=='d157'][0]
    raw=json.load(gzip.open(f"private_artifacts/c26_hosted_20260929/raw/{ep}.json.gz"));s=1-int(r['seat']);ns={'__name__':'x'}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(open(P).read(),P,'exec'),ns)
    ag=ns['kaggle_submission_agent'];cfg=structify(raw['configuration']);out=[]
    for t in range(len(raw['steps'])-1):
        o=json.loads(json.dumps(raw['steps'][t][s]['observation']))
        for k in ('step','farms','market','town'):
            if k not in o:o[k]=raw['steps'][t][0]['observation'][k]
        with contextlib.redirect_stdout(io.StringIO()):p=norm(ag(structify(o),cfg))
        a=norm(raw['steps'][t+1][s]['action'])
        if p!=a:
            d={k:(p[k],a[k]) for k in p if p[k]!=a[k]}
            out.append((t,d))
    return ep,r['margin'],r['op_team'],out
if __name__=='__main__':
    R=[json.loads(l) for l in open('analysis/exp050_divergence/fp50.jsonl')]
    L=sorted([x for x in R if x['result']=='L' and x['file']=='HL63' and x['ndiff']<=8],key=lambda x:x['ndiff'])[:8]
    with Pool(4) as p:res=p.map(one,[x['episode'] for x in L])
    for ep,m,op,out in res:
        print('==',ep,op,'margin',m,'ndiff',len(out))
        for t,d in out[:6]:print('  t',t,json.dumps(d)[:330])
