"""Same extractor as feat300 on our own hosted games (d157/c26), for gap-vs-top300 table (Claude 09-29)."""
import sys,os,json,glob
sys.argv=[sys.argv[0]]
import importlib.util
spec=importlib.util.spec_from_file_location('f3','analysis/survey300_20260929/feat300.py');f3=importlib.util.module_from_spec(spec);spec.loader.exec_module(f3)
f3.RAW='private_artifacts/hosted_20260929b/raw/'
OUT='analysis/survey300_20260929/featself.jsonl'
from multiprocessing import Pool
def one(e):return f3.one(e)
if __name__=='__main__':
    ids=sorted(os.path.basename(p)[:-8] for p in glob.glob(f3.RAW+'*.json.gz'))
    done={json.loads(l)['episode'] for l in open(OUT)} if os.path.exists(OUT) else set()
    todo=[i for i in ids if i not in done];print('todo',len(todo),flush=True)
    with Pool(4) as p,open(OUT,'a') as f:
        for x in p.imap_unordered(one,todo):f.write(json.dumps(x)+'\n');f.flush()
