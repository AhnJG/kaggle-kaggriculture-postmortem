import sys,glob,os,json
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
sys.path.insert(0,'experiments/exp062')
from multiprocessing import Pool
import run62
if __name__=='__main__':
    names=sys.argv[1].split(',');seed=int(sys.argv[2]) if len(sys.argv)>2 else 777
    jobs=[[n,f'experiments/exp062/variants/{n}.py' if n!='d157' else 'releases/exp035-d157/main.py','d157','releases/exp035-d157/main.py',seed,0] for n in names]
    with Pool(len(jobs)) as p:
        for r in p.imap_unordered(run62.play,[tuple(j) for j in jobs]):
            print(r['vid'],r['rewards'],r['score'],'maxstep',round(r['max_step'],3),'sec',r['sec'],'act',r['act_sha'][:10],'err',(r['err'] or '')[-200:],r['agent_errors'][:1])
