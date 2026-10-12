"""One process, one game at a time. Each call resets source globals; append-only outputs."""
import collections as C
import contextlib
import hashlib
import importlib
import io
import json
import math
import sys
import time
import traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def key(j):return f'{j[0]}|{j[2]}|{j[4]}|{j[5]}'

def play(job, prereg):
    vid,path,oid,op,seed,seat=job
    assert seed not in range(9000,9600)
    for p in [path,op]:assert sha(ROOT/p)==prereg['files'][p]
    with contextlib.redirect_stdout(io.StringIO()):
        from kaggle_environments import make
        from kaggle_environments.agent import get_last_callable
        E=importlib.import_module('kaggle_environments.envs.kaggriculture.kaggriculture')
    assert sha(E.__file__)==prereg['d3']['engine_sha256']
    started=time.time();dur=[];actions=[];exceptions=[];fills=C.defaultdict(lambda:[0,0]);silent=C.Counter();ctx={};trace=[]
    with contextlib.redirect_stdout(io.StringIO()):
        t=time.perf_counter();me=get_last_callable((ROOT/path).read_text(),path=str(ROOT/path));load=time.perf_counter()-t
        rival=get_last_callable((ROOT/op).read_text(),path=str(ROOT/op))
    old_market,old_commit,old_drop=E._process_market,E._commit_unit,E._drop_inventories_to_shed
    def market(state,env):
        ctx['farms']=state[0].observation.farms;ctx['privates']=[s.observation.private for s in state]
        return old_market(state,env)
    def commit(kind,item,price,farm,private,book,shed_capacity=100):
        ok=old_commit(kind,item,price,farm,private,book,shed_capacity)
        if farm is ctx['farms'][seat] and ok:
            fills[kind,item][0]+=1;fills[kind,item][1]+=price
        return ok
    def drop(private,capacity):
        before=sum(private['shed'].values())+sum(sum(x.values()) for x in private['inventories'])
        value=old_drop(private,capacity)
        after=sum(private['shed'].values())+sum(sum(x.values()) for x in private['inventories'])
        if private is ctx['privates'][seat]:silent['eod_discard_units']+=before-after
        return value
    def wrap(obs,cfg):
        t=time.perf_counter()
        try:action=me(obs,cfg)
        except Exception:
            exceptions.append(traceback.format_exc());raise
        finally:dur.append(time.perf_counter()-t+(load if not dur else 0))
        actions.append(json.dumps(action,sort_keys=True,default=str))
        farm=obs['farms'][seat];unit=[action.get('farmer')]+action.get('hands',[])
        silent['orders_truncated']+=max(0,len(action.get('market',[]))-10)
        silent['hands_mismatch']+=len(action.get('hands',[]))!=len(farm['hands'])
        plants=C.Counter(c[1] for c in unit if c and c[0]=='PLANT')
        silent['seed_blocked_turns']+=any(n>obs['private']['seeds'].get(item,0) for item,n in plants.items())
        if oid=='T114208752':
            trace.append(dict(step=int(obs['step']),action=action,positions=[farm['farmer']]+farm['hands'],private=obs['private']))
        return action
    E._process_market,E._commit_unit,E._drop_inventories_to_shed=market,commit,drop
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            env=make('kaggriculture',configuration={'episodeSteps':720,'seed':seed})
            env.run([wrap,rival] if seat==0 else [rival,wrap])
    finally:E._process_market,E._commit_unit,E._drop_inventories_to_shed=old_market,old_commit,old_drop
    final=env.steps[-1];rewards=[s.reward for s in final];margin=rewards[seat]-rewards[1-seat]
    own=final[0].observation.farms[seat]
    sheep=sum(isinstance(t,dict) and t.get('animal')=='SHEEP' for row in own['tiles'] for t in row)
    reports={k:v for k,v in me.__globals__.items() if k.endswith('_REPORT') and isinstance(v,dict)}
    errors={k:{a:b for a,b in v.items() if 'error' in a.lower() and isinstance(b,(int,float)) and b} for k,v in reports.items()}
    errors={k:v for k,v in errors.items() if v}
    result=dict(key=key(job),vid=vid,opponent=oid,seed=seed,seat=seat,rewards=rewards,statuses=[s.status for s in final],
                steps=len(env.steps),margin=margin,score=1 if margin>0 else 0 if margin<0 else .5,action_count=len(actions),exceptions=exceptions,
                act_sha=hashlib.sha256('\n'.join(actions).encode()).hexdigest(),max_step=max(dur),cold_step0=dur[0],p99=sorted(dur)[math.ceil(len(dur)*.99)-1],agent_total=sum(dur),load=load,
                fills=[dict(op=k[0],item=k[1],units=v[0],cash=v[1]) for k,v in sorted(fills.items())],silent=dict(silent),final_sheep=sheep,internal_errors=errors,
                telemetry=dict(reports.get('_HG2_REPORT',{})),source_sha256=prereg['files'][path],opponent_sha256=prereg['files'][op],runner_sha256=sha(__file__),seconds=time.time()-started)
    if trace:
        with (OUT/f'primary-{vid}.jsonl').open('w') as f:
            for r in trace:f.write(json.dumps(r)+'\n')
    return result

def main():
    jobs_path=Path(sys.argv[1]);output=Path(sys.argv[2]);prereg=json.loads((OUT/'prereg.json').read_text())
    jobs=json.loads(jobs_path.read_text())
    if jobs_path.name=='jobs-smoke.json':assert len(jobs)==26 and sha(jobs_path)==prereg['jobs_sha256']['jobs-smoke.json']
    done={r['key'] for r in map(json.loads,output.read_text().splitlines())} if output.exists() else set()
    assert len({key(j) for j in jobs})==len(jobs)
    for j in jobs:
        if key(j) in done:continue
        result=play(j,prereg)
        with output.open('a') as f:f.write(json.dumps(result)+'\n')
        print(result['key'],result['score'],result['margin'],result['telemetry'],flush=True)

if __name__=='__main__':main()
