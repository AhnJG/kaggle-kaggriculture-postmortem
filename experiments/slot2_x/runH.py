"""python3 experiments/slot2_x/runH.py VARIANT PANEL(HF|HT)  -> holdout/games-{PANEL}-{VARIANT}.jsonl (resumable). VARIANT 'd157' uses the release."""
import sys,glob,os,json
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
v,P=sys.argv[1],sys.argv[2]
path={'d157':'releases/exp035-d157/main.py','c26':'experiments/exp039_camargin/variants/c26.py'}.get(v,f'experiments/slot2_x/variants/{v}.py')
T=json.load(open(f'experiments/slot2_x/holdout/{P}.json'))
if len(sys.argv)>4:T=T[int(sys.argv[3]):int(sys.argv[4])]
jobs=[[v,path,t[0],t[1],t[2],t[3]] for t in T]
jp=f'experiments/slot2_x/holdout/jobs-{P}-{v}.json';json.dump(jobs,open(jp,'w'))
os.environ['EXP024_OUT']=f'experiments/slot2_x/holdout/games-{P}-{v}.jsonl'
sys.argv=['run.py',jp];import runpy;runpy.run_path('experiments/exp024_round2/run.py',run_name='__main__')
