"""EXP-062 loss analysis: exact per-step SELL units/revenue for both seats, replaying recorded hosted games (both seats' recorded actions)."""
import sys,glob,os,json,gzip,contextlib,io,importlib,csv,collections
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from multiprocessing import Pool
RAWS=['hosted_x0930','hosted_20260930','hosted_20260929b','hosted_20260929pm','c26_hosted_20260929','d157_hosted_20260928','hosted_0930c']
def rawpath(e):
    for d in RAWS:
        p=f"private_artifacts/{d}/raw/{e}.json.gz"
        if os.path.exists(p): return p
def one(r):
    with contextlib.redirect_stdout(io.StringIO()):
        from kaggle_environments import make
        E=importlib.import_module("kaggle_environments.envs.kaggriculture.kaggriculture")
    p=rawpath(r['episode'])
    if not p: return {'episode':r['episode'],'missing':True}
    raw=json.load(gzip.open(p));s=int(r['seat'])
    tape=[[st[k]['action'] for st in raw['steps'][1:]] for k in (0,1)]
    S=collections.defaultdict(lambda:[0,0]);ctx={};PR={}
    om,oc=E._process_market,E._commit_unit
    def market(state,env):
        ctx['step']=int(state[0].observation.step);ctx['farms']=state[0].observation.farms
        m=state[0].observation.market
        if ctx['step']%6==0: PR[ctx['step']]={k:m['prices'][k] for k in ('WOOL','MILK','STRAWBERRY','TOMATO','CARROT','EGG','MELON','WHEAT')}
        return om(state,env)
    def sd(farm):return 0 if farm is ctx['farms'][0] else 1
    def commit(op,item,price,farm,private,book,cap=100):
        ok=oc(op,item,price,farm,private,book,cap)
        if ok and op=='SELL':g=S[(sd(farm),ctx['step'],item)];g[0]+=1;g[1]+=price
        return ok
    E._process_market,E._commit_unit=market,commit
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(raw['info']['seed'])})
            env.run([lambda o,c:tape[0][int(o['step'])],lambda o,c:tape[1][int(o['step'])]])
    finally:E._process_market,E._commit_unit=om,oc
    ok=[x.reward for x in env.steps[-1]]==[raw['steps'][-1][i]['reward'] for i in (0,1)]
    return {'episode':r['episode'],'sub':r['submission_label'],'result':r['result'],'margin':int(r['margin']),'seat':s,'label':r['label'],'op_lb':r['op_lb_score'],'parity':ok,
            'sales':[[a,b,c,v[0],v[1]] for (a,b,c),v in S.items()],'prices':PR}
if __name__=='__main__':
    rows={}
    for d in ['hosted_20260929pm','hosted_20260929b','hosted_20260930','hosted_x0930']+(['hosted_0930c'] if os.path.exists('analysis/hosted_0930c/opponents.csv') else []):
        for r in csv.DictReader(open(f'analysis/{d}/opponents.csv')): rows[r['episode']]=r
    R=list(rows.values())
    O='experiments/exp062/loss/sales62.jsonl';done={json.loads(l)['episode'] for l in open(O)} if os.path.exists(O) else set()
    todo=[r for r in R if r['episode'] not in done and r['result']!='D']
    print('todo',len(todo),flush=True)
    with Pool(4) as p,open(O,'a') as f:
        for x in p.imap_unordered(one,todo):f.write(json.dumps(x)+'\n');f.flush()
