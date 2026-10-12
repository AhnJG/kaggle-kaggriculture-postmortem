"""Last-mile check: replay real hosted L4p games (both seats) locally — L4p in our seat, opponent = recorded actions — and compare our actions step by step."""
import sys,glob,os,json,gzip,contextlib,io
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable
eps=json.load(open('analysis/hosted_0930d/snap_1730/episodes_all.json'))
L=[e for e in eps if e['submission_label']=='L4p' and os.path.exists(f"private_artifacts/hosted_0930d/raw/{e['id']}.json.gz")]
pick=[e for e in L if e['our_seat']==0][:3]+[e for e in L if e['our_seat']==1][:3]
with contextlib.redirect_stdout(io.StringIO()):
    me=get_last_callable(open('releases/exp062-L4p/main.py').read(),path='L4p')
for e in pick:
    raw=json.load(gzip.open(f"private_artifacts/hosted_0930d/raw/{e['id']}.json.gz")); s=int(e['our_seat']); o=1-s
    rec_me=[st[s]['action'] for st in raw['steps'][1:]]; rec_op=[st[o]['action'] for st in raw['steps'][1:]]
    mine=[]
    def wrap(obs,cfg):
        a=me(obs,cfg); mine.append(a); return a
    tape=lambda obs,cfg: rec_op[int(obs['step'])]
    with contextlib.redirect_stdout(io.StringIO()):
        env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(raw['info']['seed'])})
        env.run([wrap,tape] if s==0 else [tape,wrap])
    first=next((i for i,(a,b) in enumerate(zip(mine,rec_me)) if json.dumps(a,sort_keys=True)!=json.dumps(b,sort_keys=True)),None)
    rew=[x.reward for x in env.steps[-1]]; real=[raw['steps'][-1][i]['reward'] for i in (0,1)]
    print(e['id'],'seat',s,'first action mismatch',first,'rewards match',rew==real, 'tel',getattr(me,'telemetry',None))
