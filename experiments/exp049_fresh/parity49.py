import sys,glob,os,json,gzip,contextlib,io
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from multiprocessing import Pool
def one(m):
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
    r=json.load(gzip.open(f"private_artifacts/top2400_fresh_20260929/raw/{m['episode']}.json.gz"))
    ot=[r['steps'][k+1][m['our_seat']]['action'] for k in range(719)]
    tp=get_last_callable(open(f"experiments/exp049_fresh/tapes/F{m['episode']}.py").read())
    op=lambda obs,cfg:ot[int(obs['step'])]
    with contextlib.redirect_stdout(io.StringIO()):
        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":m['seed']});env.run([op,tp] if m['our_seat']==0 else [tp,op])
    return m['episode'],[s.reward for s in env.steps[-1]]==[r['steps'][-1][i]['reward'] for i in (0,1)],[r['steps'][-1][i]['status'] for i in (0,1)]
if __name__=='__main__':
    M=json.load(open('experiments/exp049_fresh/meta.json'));O='experiments/exp049_fresh/parity.jsonl'
    done={json.loads(l)[0] for l in open(O)} if os.path.exists(O) else set()
    todo=[m for m in M if m['episode'] not in done]
    with Pool(4) as p,open(O,'a') as f:
        for x in p.imap_unordered(one,todo):f.write(json.dumps(x)+'\n');f.flush()
    R=[json.loads(l) for l in open(O)];bad=[x for x in R if not x[1]];print('parity',len(R)-len(bad),'/',len(R),'of',len(M));print(bad[:8])
