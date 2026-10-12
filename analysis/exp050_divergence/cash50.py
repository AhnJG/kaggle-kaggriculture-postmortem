"""Exact per-item cash flows (both seats) by replaying hosted d157 games vs 55be-labelled opponents (recorded actions of both seats)."""
import sys,glob,os,json,gzip,contextlib,io,importlib,csv,collections
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from multiprocessing import Pool
def one(r):
    with contextlib.redirect_stdout(io.StringIO()):
        from kaggle_environments import make
        E=importlib.import_module("kaggle_environments.envs.kaggriculture.kaggriculture")
    raw=json.load(gzip.open(f"private_artifacts/c26_hosted_20260929/raw/{r['episode']}.json.gz"));s=int(r['seat'])
    tape=[[st[k]['action'] for st in raw['steps'][1:]] for k in (0,1)]
    C=collections.defaultdict(lambda:[0,0]);ctx={}
    om,oc,oh,ol=E._process_market,E._commit_unit,E._do_hire,E._do_buy_land
    def market(state,env):ctx['step']=int(state[0].observation.step);ctx['farms']=state[0].observation.farms;return om(state,env)
    def sd(farm):return 0 if farm is ctx['farms'][0] else 1
    def commit(op,item,price,farm,private,book,cap=100):
        ok=oc(op,item,price,farm,private,book,cap)
        if ok:g=C[(sd(farm),min(3,ctx['step']//180),op,item)];g[0]+=1;g[1]+=price
        return ok
    def hire(farm,*a,**k):
        b=farm['money'];x=oh(farm,*a,**k);g=C[(sd(farm),min(3,ctx['step']//180),'HIRE','-')];g[0]+=1;g[1]+=b-farm['money'];return x
    def land(farm,*a,**k):
        b=farm['money'];x=ol(farm,*a,**k);g=C[(sd(farm),min(3,ctx['step']//180),'LAND','-')];g[0]+=1;g[1]+=b-farm['money'];return x
    E._process_market,E._commit_unit,E._do_hire,E._do_buy_land=market,commit,hire,land
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(raw['info']['seed'])})
            env.run([lambda o,c:tape[0][int(o['step'])],lambda o,c:tape[1][int(o['step'])]])
    finally:E._process_market,E._commit_unit,E._do_hire,E._do_buy_land=om,oc,oh,ol
    ok=[x.reward for x in env.steps[-1]]==[raw['steps'][-1][i]['reward'] for i in (0,1)]
    return {'episode':r['episode'],'result':r['result'],'seat':s,'parity':ok,'groups':[[a,b,c,d,v[0],v[1]] for (a,b,c,d),v in C.items()]}
if __name__=='__main__':
    R=[r for r in csv.DictReader(open('analysis/c26_hosted_20260929/opponents.csv')) if r['submission_label']=='d157' and '55be' in r['label'] and r['result']!='D']
    O='analysis/exp050_divergence/cash50.jsonl';done={json.loads(l)['episode'] for l in open(O)} if os.path.exists(O) else set()
    with Pool(4) as p,open(O,'a') as f:
        for x in p.imap_unordered(one,[r for r in R if r['episode'] not in done]):f.write(json.dumps(x)+'\n');f.flush()
