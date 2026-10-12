#!/bin/bash
# usage: vmrun.sh jobs.json out.jsonl  (runs <=168s, resumable)
cd $HOME/mnt/Kaggriculture
timeout 150 env EXP024_OUT=$2 python3 -c "
import sys,glob,os;sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0]);sys.argv=['run.py','$1'];import runpy;runpy.run_path('experiments/exp061_donor/run_vm.py',run_name='__main__')" 2>&1 | grep -v open_spiel | tail -1
wc -l < $2
