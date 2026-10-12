import sys,glob,os,json,contextlib,io
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable
B='experiments/exp041_top2400/';P='releases/exp035-d157/main.py'
H=set(json.load(open(B+'team-split.json'))['holdout_teams'])
M=[m for m in list({m['episode']:m for m in json.load(open(B+'meta.json'))}.values()) if m['team'] not in H][:int(sys.argv[1])]
tot={}
for m in M:
    ns={'__name__':'d157'}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(open(P).read(),P,'exec'),ns)
        me=ns['kaggle_submission_agent'];o=f"X{m['episode']}";op=get_last_callable(open(B+f'tapes/{o}.py').read())
        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":m['seed']});s=m['our_seat']
        env.run([me,op] if s==0 else [op,me])
    for k,v in ns.items():
        if k.endswith('REPORT') and isinstance(v,dict):
            for kk,vv in v.items():
                if isinstance(vv,(int,float)):tot[(k,kk)]=tot.get((k,kk),0)+vv
for (k,kk),v in sorted(tot.items()):
    if v:print(k,kk,v)
