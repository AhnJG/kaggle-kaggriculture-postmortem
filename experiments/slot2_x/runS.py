"""python3 experiments/slot2_x/runS.py VARIANT N  (N=80 screen, 269 full). Resumable; call repeatedly under timeout."""
import sys,glob,os,json
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
v,N=sys.argv[1],int(sys.argv[2])
J=[j for j in json.load(open('experiments/exp051_curpop/jobs.json')) if j[0]=='d157'][:N]
jobs=[[v,f'experiments/slot2_x/variants/{v}.py']+j[2:] for j in J]
jp=f'experiments/slot2_x/jobs-{v}-{N}.json';json.dump(jobs,open(jp,'w'))
os.environ['EXP024_OUT']=f'experiments/slot2_x/games-{v}.jsonl'
sys.argv=['run.py',jp]
import runpy;runpy.run_path('experiments/exp024_round2/run.py',run_name='__main__')
