"""python3 experiments/slot2_x/trace.py VARIANT EPISODE -> daily money/quads/hands/tomato/sheep for d157 vs variant"""
import sys,glob,os,json,contextlib,io
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable
v,ep=sys.argv[1],sys.argv[2]
m=[m for m in json.load(open('experiments/exp051_curpop/meta.json')) if m['episode']==ep and m['sub']=='d157'][0];s=m['seat']
out={}
for name,p in (('d157','releases/exp035-d157/main.py'),(v,f'experiments/slot2_x/variants/{v}.py')):
    with contextlib.redirect_stdout(io.StringIO()):
        me=get_last_callable(open(p).read());op=get_last_callable(open(f"experiments/exp051_curpop/tapes/C{ep}.py").read())
        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":m['seed']});env.run([me,op] if s==0 else [op,me])
    rows=[]
    for d in range(1,30):
        o=env.steps[d*24][0].observation; fm=o.farms[s]
        cnt=lambda f:sum(1 for row in fm['tiles'] for t in row if isinstance(t,dict) and f(t))
        rows.append((d,int(fm['money']),len(fm['unlocked_quadrants']),len(fm['hands']),cnt(lambda t:t.get('crop')=='TOMATO'),cnt(lambda t:t.get('crop')=='WHEAT'),cnt(lambda t:t.get('animal')=='SHEEP'),cnt(lambda t:t.get('animal')=='COW')))
    out[name]=rows; print(name,'final',[x.reward for x in env.steps[-1]])
for a,b in zip(out['d157'],out[v]):
    if a[1:]!=b[1:]:print('day',a[0],'d157',a[1:],'|',v,b[1:])
