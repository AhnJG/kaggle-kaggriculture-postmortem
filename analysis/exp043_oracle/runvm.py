import sys,glob,os
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
sys.argv=[sys.argv[0]]+sys.argv[1:]
import runpy;runpy.run_path('experiments/exp024_round2/run.py',run_name='__main__')
