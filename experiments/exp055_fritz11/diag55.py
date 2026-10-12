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
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            me=get_last_callable(open(path).read());op=get_last_callable(open(f"experiments/exp051_curpop/tapes/C{m['episode']}.py").read())
            env=make("kaggriculture",configuration={"episodeSteps":720,"seed":m['seed']});env.run([me,op] if s==0 else [op,me])
    finally:E._process_market,E._commit_unit=om,oc
    return name,m['episode'],env.steps[-1][s].reward,{f'{k[0]}:{k[1]}':v for k,v in C.items()}
if __name__=='__main__':
    M=json.load(open('experiments/exp051_curpop/meta.json'))[:8]
    J=[(n,p,m) for m in M for n,p in (('c26','experiments/exp039_camargin/variants/c26.py'),('F11','experiments/exp055_fritz11/variants/F11.py'))]
    with Pool(4) as p:R=p.map(one,J)
    agg=collections.defaultdict(lambda:collections.defaultdict(float));rw=collections.defaultdict(list)
    for n,e,r,c in R:
        rw[n].append(r)
        for k,(u,cash) in c.items():agg[n][k+'|u']+=u/8;agg[n][k+'|c']+=cash/8
    print('mean reward',{n:round(sum(v)/len(v)) for n,v in rw.items()})
    ks=sorted(set(agg['c26'])|set(agg['F11']),key=lambda k:-abs(agg['F11'][k]-agg['c26'][k]))
    for k in ks[:16]:print(f'  {k:32s} c26 {agg["c26"][k]:9.0f}  F11 {agg["F11"][k]:9.0f}')
