import sys,json,time,io,contextlib,hashlib,os,traceback
from multiprocessing import Pool
OUT=os.environ.get('EXP023_OUT','games.jsonl')
def play(job):
    vid,path,opp,seed,seat=job
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
    t0=time.time();maxstep=0.0;acts=[];err=None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            me=get_last_callable(open(path).read(),path=path);op=get_last_callable(open(opp).read(),path=opp)
            def wrap(obs,cfg):
                nonlocal maxstep
                s=time.perf_counter();a=me(obs,cfg);d=time.perf_counter()-s
                if obs['step']>0:maxstep=max(maxstep,d)
                acts.append(json.dumps(a,sort_keys=True,default=str));return a
            env=make('kaggriculture',configuration={'episodeSteps':720,'seed':seed})
            env.run([wrap,op] if seat==0 else [op,wrap])
        last=env.steps[-1];rw=[s.reward for s in last];st=[s.status for s in last]
        m=rw[seat]-rw[1-seat] if None not in rw else None
        score=None if m is None else (1.0 if m>0 else 0.0 if m<0 else 0.5)
    except Exception as e:
        rw=st=m=score=None;err=traceback.format_exc()[-400:]
    return dict(key=f'{vid}|{seed}|{seat}',vid=vid,seed=seed,seat=seat,rewards=rw,statuses=st,margin=m,score=score,
                max_step=maxstep,act_sha=hashlib.sha256('\n'.join(acts).encode()).hexdigest()[:16],err=err,sec=round(time.time()-t0,1))
if __name__=='__main__':
    jobs=json.load(open(sys.argv[1]))
    done=set()
    if os.path.exists(OUT):done={json.loads(l)['key'] for l in open(OUT)}
    todo=[tuple(j) for j in jobs if f'{j[0]}|{j[3]}|{j[4]}' not in done]
    print('todo',len(todo),flush=True)
    with Pool(5) as p, open(OUT,'a') as f:
        for r in p.imap_unordered(play,todo):
            f.write(json.dumps(r)+'\n');f.flush()
