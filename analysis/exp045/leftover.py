import sys,glob,os,json,contextlib,io,statistics as st
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from multiprocessing import Pool
B='experiments/exp041_top2400/'
def one(m):
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
    o=f"X{m['episode']}";s=m['our_seat']
    with contextlib.redirect_stdout(io.StringIO()):
        me=get_last_callable(open('releases/exp035-d157/main.py').read());op=get_last_callable(open(B+f'tapes/{o}.py').read())
        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":m['seed']});env.run([me,op] if s==0 else [op,me])
    fin=env.steps[-1];pr=fin[0].observation.market['prices'];pv=fin[s].observation.private
    v=sum(n*pr.get(i,0) for i,n in pv['shed'].items() if i in pr)+sum(n*pr.get(i,0) for d in pv['inventories'] for i,n in d.items() if i in pr)
    return v,{i:n for i,n in pv['shed'].items() if n and i in pr},fin[s].reward-fin[1-s].reward
H=set(json.load(open(B+'team-split.json'))['holdout_teams'])
M=[m for m in list({m['episode']:m for m in json.load(open(B+'meta.json'))}.values()) if m['team'] not in H][::20][:28]
with Pool(4) as p:R=p.map(one,M)
print('d157 final unsold value mean',round(st.mean(r[0] for r in R)),'max',max(r[0] for r in R),'games with >0',sum(r[0]>0 for r in R),'/',len(R))
print([ (r[1],r[2]) for r in R if r[0]>0][:6])
