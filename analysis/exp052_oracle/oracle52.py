"""EXP-052 oracle (Claude 09-29): d157 with its existing _front_run hook fed the opponent's TRUE future actions (the tape itself).
Upper bound of the front-run mechanism against the current population (U' tapes of d157's hosted games vs 55be-labelled opponents)."""
import sys,glob,os,json,contextlib,io,csv
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from multiprocessing import Pool
P='releases/exp035-d157/main.py';OUT='analysis/exp052_oracle/oracle52.jsonl'
def one(job):
    r,mode=job
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
    tp=f"experiments/exp051_curpop/tapes/C{r['episode']}.py";tns={}
    exec(open(tp).read(),tns);TAPE=tns['TAPE']
    ns={'__name__':'d157o'}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(open(P).read(),P,'exec'),ns)
        if mode=='oracle':
            ns['_IMPL'].chassis.cfg['front_run']=True;ns['_IMPL'].chassis.opponent_plan=TAPE
        me=ns['kaggle_submission_agent'];op=get_last_callable(open(tp).read())
        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(r['seed'])});s=int(r['seat'])
        env.run([me,op] if s==0 else [op,me])
    rw=[x.reward for x in env.steps[-1]];m=rw[s]-rw[1-s]
    return {'episode':r['episode'],'mode':mode,'result':r['result'],'margin':m,'score':1.0 if m>0 else 0.0 if m<0 else 0.5}
if __name__=='__main__':
    meta={m['episode']:m for m in json.load(open('experiments/exp051_curpop/meta.json'))}
    R=[r for r in csv.DictReader(open('analysis/c26_hosted_20260929/opponents.csv')) if r['submission_label']=='d157' and '55be' in r['label']]
    J=[(dict(episode=r['episode'],seed=meta[r['episode']]['seed'],seat=r['seat'],result=r['result']),'oracle') for r in R]
    done={(x['episode'],x['mode']) for x in map(json.loads,open(OUT))} if os.path.exists(OUT) else set()
    todo=[j for j in J if (j[0]['episode'],j[1]) not in done];print('todo',len(todo),flush=True)
    with Pool(4) as p,open(OUT,'a') as f:
        for x in p.imap_unordered(one,todo):f.write(json.dumps(x)+'\n');f.flush()
