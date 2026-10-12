"""python3 experiments/slot2_x/diag.py VARIANT N [offset]  -> per-item sold units/cash for d157 vs variant on S tapes."""
import sys,glob,os,json,contextlib,io,importlib,collections
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from multiprocessing import Pool
def one(job):
    name,path,m=job
    with contextlib.redirect_stdout(io.StringIO()):
        from kaggle_environments import make
        from kaggle_environments.agent import get_last_callable
        E=importlib.import_module("kaggle_environments.envs.kaggriculture.kaggriculture")
    C=collections.defaultdict(lambda:[0,0]);ctx={};s=m['seat']
    om,oc=E._process_market,E._commit_unit
    def market(state,env):ctx['farms']=state[0].observation.farms;return om(state,env)
    def commit(op,item,price,farm,private,book,cap=100):
        ok=oc(op,item,price,farm,private,book,cap)
        if ok and farm is ctx['farms'][s]:g=C[(op,item)];g[0]+=1;g[1]+=price
        return ok
    E._process_market,E._commit_unit=market,commit
    tel={}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            me=get_last_callable(open(path).read());op=get_last_callable(open(f"experiments/exp051_curpop/tapes/C{m['episode']}.py").read())
            env=make("kaggriculture",configuration={"episodeSteps":720,"seed":m['seed']});env.run([me,op] if s==0 else [op,me])
            tel=dict(getattr(me,'telemetry',{}) or {})
    finally:E._process_market,E._commit_unit=om,oc
    rw=[x.reward for x in env.steps[-1]]
    return name,m['episode'],rw[s],rw[s]-rw[1-s],{f'{k[0]}:{k[1]}':v for k,v in C.items()},tel
if __name__=='__main__':
    v=sys.argv[1];N=int(sys.argv[2]);off=int(sys.argv[3]) if len(sys.argv)>3 else 0
    M=json.load(open('experiments/exp051_curpop/meta.json'))
    M=[m for m in M if m['sub']=='d157'][off:off+N]
    P={'d157':'releases/exp035-d157/main.py',v:f'experiments/slot2_x/variants/{v}.py'}
    J=[(n,p,m) for m in M for n,p in P.items()]
    with Pool(4) as p:R=p.map(one,J)
    agg=collections.defaultdict(lambda:collections.defaultdict(float));rw=collections.defaultdict(list);mg={};tels=[]
    for n,e,r,g,c,t in R:
        rw[n].append(r);mg[(n,e)]=g
        if t:tels.append(t)
        for k,(u,cash) in c.items():agg[n][k+'|u']+=u/N;agg[n][k+'|c']+=cash/N
    print('mean reward',{n:round(sum(x)/len(x)) for n,x in rw.items()})
    eps=[m['episode'] for m in M]
    print('margin d157',[round(mg[('d157',e)]) for e in eps]);print('margin',v,[round(mg[(v,e)]) for e in eps])
    print('tel',tels[:3])
    ks=sorted(set(agg['d157'])|set(agg[v]),key=lambda k:-abs(agg[v][k]-agg['d157'][k]))
    for k in ks[:14]:print(f'  {k:28s} d157 {agg["d157"][k]:9.0f}  {v} {agg[v][k]:9.0f}')
