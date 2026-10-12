"""EXP-060 M0 (Claude 09-29 23:20 KST, before any EXP-060 result): selection tape pool + mirror detection at step 144.
python3 experiments/exp060_mbr/m0_pool.py pool   -> pool.json (unique (seed,seat) tape jobs, HF excluded)
python3 experiments/exp060_mbr/m0_pool.py detect -> m0.jsonl (resumable)"""
import sys,glob,os,json
sys.path+=glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[:1]  # Cowork VM; on the Mac the venv python already has it
OUT='experiments/exp060_mbr'
def pool():
    hf=json.load(open('experiments/slot2_x/holdout/HF.json')); hfseeds={j[2] for j in hf}
    P={}
    for f in sorted(glob.glob('experiments/*/jobs*.json')+glob.glob('experiments/*/*/jobs*.json')):
        if '/slot2_x/holdout/' in f or '_dryrun' in f or 'invalid' in f: continue
        try: J=json.load(open(f))
        except Exception: continue
        if not isinstance(J,list): continue
        for j in J:
            if not (isinstance(j,list) and len(j)>=6 and isinstance(j[3],str) and '/tapes/' in j[3] and os.path.exists(j[3])): continue
            seed,seat=j[4],j[5]
            if not isinstance(seed,int) or seed in hfseeds: continue
            P.setdefault((seed,seat),{'tape':j[3],'seed':seed,'seat':seat,'src':f})
    for m in json.load(open('experiments/exp049_fresh/meta.json')):
        t=f"experiments/exp049_fresh/tapes/F{m['episode']}.py"
        if os.path.exists(t) and m['seed'] not in hfseeds: P.setdefault((m['seed'],m['our_seat']),{'tape':t,'seed':m['seed'],'seat':m['our_seat'],'src':'exp049_fresh/meta.json'})
    L=sorted(P.values(),key=lambda r:(r['tape'],r['seat']))
    json.dump(L,open(f'{OUT}/pool.json','w'),indent=0); print('pool',len(L))
def same(a,b):
    return (a['tiles']==b['tiles'] and list(a['farmer'])==list(b['farmer']) and [list(h) for h in a['hands']]==[list(h) for h in b['hands']]
            and list(a['unlocked_quadrants'])==list(b['unlocked_quadrants']) and abs(float(a['money'])-float(b['money']))<0.5)
def one(r):
    import contextlib,io
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
    rec=dict(r); rec.update(mirror=None,shops=None,err=None)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            me=get_last_callable(open('releases/exp035-d157/main.py').read(),path='releases/exp035-d157/main.py')
            op=get_last_callable(open(r['tape']).read(),path=r['tape'])
            def wrap(obs,cfg):
                if int(obs['step'])==144 and rec['mirror'] is None:
                    f=obs['farms'];p=int(obs['player'])
                    rec['mirror']=bool(same(f[p],f[1-p])); rec['shops']=list((obs['town']['unlocked_shops'] or [])[:2])
                return me(obs,cfg)
            env=make('kaggriculture',configuration={'episodeSteps':int(os.environ.get('M0_STEPS','146')),'seed':r['seed']})
            env.run([wrap,op] if r['seat']==0 else [op,wrap])
    except Exception as e: rec['err']=repr(e)[:300]
    return rec
def detect():
    from multiprocessing import Pool
    L=json.load(open(f'{OUT}/pool.json')); fn=f'{OUT}/m0.jsonl'
    done=set()
    if os.path.exists(fn):
        for l in open(fn): x=json.loads(l); done.add((x['seed'],x['seat']))
    todo=[r for r in L if (r['seed'],r['seat']) not in done][:int(os.environ.get('M0_N','100000'))]
    with Pool(int(os.environ.get('W','4'))) as p, open(fn,'a') as out:
        for rec in p.imap_unordered(one,todo,chunksize=2): out.write(json.dumps(rec)+'\n'); out.flush()
    print('done',len(todo))
if __name__=='__main__': {'pool':pool,'detect':detect}[sys.argv[1]]()
