import sys,glob,os,json,contextlib,io
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from multiprocessing import Pool
def one(a):
    name,seed,seat,opp=a
    with contextlib.redirect_stdout(io.StringIO()):
        from kaggle_environments import make
        from kaggle_environments.agent import get_last_callable
        p=f'experiments/exp062/variants/{name}.py'
        me=get_last_callable(open(p).read(),path=p)
        op=get_last_callable(open(opp).read(),path=opp)
        env=make('kaggriculture',configuration={'episodeSteps':720,'seed':seed})
        env.run([me,op] if seat==0 else [op,me])
    r=[s.reward for s in env.steps[-1]]
    return name,seed,seat,r,r[seat]-r[1-seat],dict(getattr(me,'telemetry',{}))
if __name__=='__main__':
    names=sys.argv[1].split(',');seeds=[int(x) for x in sys.argv[2].split(',')];opp=sys.argv[3] if len(sys.argv)>3 else 'releases/exp035-d157/main.py'
    J=[(n,s,t,opp) for n in names for s in seeds for t in (0,1)]
    with Pool(4) as p:
        for x in p.imap_unordered(one,J): print(x,flush=True)
