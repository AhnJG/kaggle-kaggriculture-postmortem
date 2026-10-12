"""EXP-061 donor scan (Claude 09-29 23:55 KST; Codex usage exhausted -> Claude runs it).
Top-100 (survey300 label R<rank>) winning seats whose farm at step 144 equals d157's farm when d157 plays the same seed/seat vs the other seat's recorded tape."""
import sys,glob,os,json,gzip,re
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
OUT='experiments/exp061_donor'
def key(f): return (f['tiles'],list(f['farmer']),[list(h) for h in f['hands']],list(f['unlocked_quadrants']))
def one(e):
    import contextlib,io
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
    p=f"private_artifacts/survey300_20260929/raw/{e['id']}.json.gz"
    rec={'id':e['id'],'label':e['submission_label'],'seat':e['our_seat'],'match':None,'err':None}
    try:
        d=json.load(gzip.open(p)); s=e['our_seat']; o=1-s; seed=int(d['info']['seed']); rec['seed']=seed
        opp=[d['steps'][k+1][o]['action'] for k in range(len(d['steps'])-1)]
        rec_farm=d['steps'][144][s]['observation']['farms'][s]
        rec['shops']=list((d['steps'][144][s]['observation']['town']['unlocked_shops'] or [])[:2])
        got={}
        with contextlib.redirect_stdout(io.StringIO()):
            me=get_last_callable(open('releases/exp035-d157/main.py').read(),path='releases/exp035-d157/main.py')
            def wrap(obs,cfg):
                if int(obs['step'])==144 and 'f' not in got: got['f']=obs['farms'][int(obs['player'])]
                return me(obs,cfg)
            def tape(obs,cfg=None):
                k=int(obs['step']); return opp[k] if k<len(opp) else {"farmer":["PASS"],"hands":[],"market":[]}
            env=make('kaggriculture',configuration={'episodeSteps':146,'seed':seed})
            env.run([wrap,tape] if s==0 else [tape,wrap])
        rec['match']=key(got['f'])==key(rec_farm)
    except Exception as ex: rec['err']=repr(ex)[:200]
    return rec
if __name__=='__main__':
    E=json.load(open('analysis/survey300_20260929/episodes_all.json'))
    def rank(l):
        m=re.match(r'R(\d+)_',l or ''); return int(m.group(1)) if m else 9999
    C=[e for e in E if rank(e.get('submission_label'))<=100 and e.get('result')=='W' and os.path.exists(f"private_artifacts/survey300_20260929/raw/{e['id']}.json.gz")]
    fn=f'{OUT}/scan.jsonl'; done=set()
    if os.path.exists(fn): done={json.loads(l)['id'] for l in open(fn)}
    todo=[e for e in C if e['id'] not in done]; print('cands',len(C),'todo',len(todo))
    from multiprocessing import Pool
    with Pool(4) as pl, open(fn,'a') as out:
        for r in pl.imap_unordered(one,todo,chunksize=2): out.write(json.dumps(r)+'\n'); out.flush()
