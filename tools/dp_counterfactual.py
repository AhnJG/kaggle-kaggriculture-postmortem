"""Serial frozen DP counterfactual runner. New module globals for every seat/game."""
import argparse
import contextlib
import copy
import hashlib
import io
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from dp_loss_cause import ROOT, OUT, PARENT, ENGINE_SHA, read_raw, save, sha


def score(margin):
    return 1.0 if margin > 0 else 0.0 if margin < 0 else 0.5


def run_game(path, opponent, seed, seat, replay=None, verify_identity=True):
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    from reproduce_replay import projection, first_difference
    assert sha(K.__file__) == ENGINE_SHA
    config=copy.deepcopy(replay['configuration']) if replay else {'episodeSteps':720}
    config['seed']=seed
    log=io.StringIO()
    functions=[]
    with contextlib.redirect_stdout(log):
        for p in (path,opponent):
            functions.append(get_last_callable(Path(p).read_text(),path=str(p)))
        cfg=make('kaggriculture',configuration=config)
        duration=[[],[]]
        exceptions=[[],[]]
        def timed(index):
            def agent(obs,config):
                start=time.perf_counter()
                try:
                    return functions[index](obs,config)
                except Exception as exc:
                    exceptions[index].append(repr(exc))
                    raise
                finally:
                    duration[index].append(time.perf_counter()-start)
            return agent
        agents=[None,None]
        agents[seat]=timed(0);agents[1-seat]=timed(1)
        start=time.perf_counter()
        cfg.run(agents)
        wall=time.perf_counter()-start
    rewards=[s.reward for s in cfg.steps[-1]]
    statuses=[s.status for s in cfg.steps[-1]]
    errors=[]
    for index,fn in enumerate(functions):
        for name,value in fn.__globals__.items():
            if isinstance(value,dict):
                for key,v in value.items():
                    if isinstance(key,str) and (key=='errors' or key.endswith('_errors')) and isinstance(v,(int,float)) and v:
                        errors.append(dict(agent=index,counter=f'{name}.{key}',value=v))
    identity=None
    if replay and verify_identity:
        action_count=state_count=0;diffs=[]
        for i,(expected,actual) in enumerate(zip(replay['steps'],cfg.steps)):
            for p in (0,1):
                if i:
                    equal=expected[p]['action']==actual[p]['action'];action_count+=equal
                    if not equal and len(diffs)<5:diffs.append(dict(step=i,seat=p,kind='action',expected=expected[p]['action'],actual=actual[p]['action']))
                diff=first_difference(projection(expected[p]),projection(actual[p]))
                state_count+=diff is None
                if diff and len(diffs)<5:diffs.append(dict(step=i,seat=p,kind='state',detail=diff))
        identity=dict(actions=action_count,states=state_count,differences=diffs,
                      passed=len(cfg.steps)==720 and action_count==1438 and state_count==1440)
    stats=[]
    for values in duration:
        v=sorted(values)
        stats.append(dict(calls=len(v),max_seconds=max(v,default=0),
                          p99_seconds=v[min(len(v)-1,int(len(v)*.99))] if v else None,
                          total_seconds=sum(v)))
    margin=rewards[seat]-rewards[1-seat] if all(v is not None for v in rewards) else None
    return dict(path=str(Path(path).resolve().relative_to(ROOT)) if Path(path).resolve().is_relative_to(ROOT) else str(Path(path).resolve()),sha256=sha(path),
                opponent=str(Path(opponent).resolve().relative_to(ROOT)) if Path(opponent).resolve().is_relative_to(ROOT) else str(Path(opponent).resolve()),opponent_sha256=sha(opponent),
                seed=seed,seat=seat,rewards=rewards,margin=margin,score=score(margin) if margin is not None else None,
                statuses=statuses,steps=len(cfg.steps),timing=stats,exceptions=exceptions,caught_errors=errors,
                identity=identity,wall_seconds=wall,stdout=log.getvalue()[-3000:],
                action_sha256=[hashlib.sha256(json.dumps([s[p]['action'] for s in cfg.steps[1:]],sort_keys=True).encode()).hexdigest() for p in (0,1)])


def check_freeze(freeze):
    for path,expected in freeze['sha256'].items():
        assert sha(ROOT/path)==expected,('SHA_MISMATCH',path)


def q2(freeze_path,candidate):
    freeze=json.loads(freeze_path.read_text());check_freeze(freeze)
    spec=freeze['candidates'][candidate]
    results=[]
    started=datetime.now(timezone.utc).isoformat()
    for eid in spec['q2_episodes']:
        row=next(r for r in freeze['panel'] if r['episode']==eid)
        replay=read_raw(eid)
        for name,path in [('parent',PARENT),(candidate,ROOT/spec['path'])]:
            out=OUT/'q2'/f'{eid}-{name}.json'
            if out.exists():
                value=json.loads(out.read_text())
                assert value['sha256']==sha(path)
            else:
                value=run_game(path,ROOT/row['opponent_path'],int(row['seed']),int(row['dp_seat']),
                               replay=replay,verify_identity=name=='parent')
                value.update(card_sha256=freeze['card_sha256'],freeze_sha256=sha(freeze_path),started_at=started)
                save(out,value)
            print(eid,name,value['margin'],value['timing'][0]['max_seconds'],flush=True)
            if name=='parent' and not value['identity']['passed']:
                raise RuntimeError(f'BLOCKED_PARENT_REPRODUCTION {eid}')
            if value['statuses']!=['DONE','DONE'] or value['steps']!=720 or any(value['exceptions']) or value['caught_errors']:
                raise RuntimeError(f'BLOCKED_EXECUTION {eid} {name}')
            if name=='parent':baseline=value
            else:results.append(dict(episode=eid,parent_margin=baseline['margin'],candidate_margin=value['margin'],
                                      margin_change=value['margin']-baseline['margin'],flipped=value['margin']>0))
    summary=dict(candidate=candidate,results=results,flipped=sum(r['flipped'] for r in results),
                 required_flips=3,card_sha256=freeze['card_sha256'],freeze_sha256=sha(freeze_path))
    save(OUT/f'q2_{candidate}_summary.json',summary)
    print(json.dumps(summary),flush=True)


def q4(freeze_path,candidate):
    freeze=json.loads(freeze_path.read_text());check_freeze(freeze)
    screening=json.loads((OUT/f'q2_{candidate}_summary.json').read_text())
    assert screening['flipped']>=3
    spec=freeze['candidates'][candidate]
    output=ROOT/'analysis/exp018_panel'
    assert not (output/'summary.json').exists()
    panel=[];runtime=[]
    weights=json.loads((OUT/'input_audit.json').read_text())['weights']
    for row in freeze['panel']:
        if not row['eligible']:continue
        eid=row['episode'];replay=read_raw(eid);values={}
        for name,path in [('parent',PARENT),(candidate,ROOT/spec['path'])]:
            old=OUT/'q2'/f'{eid}-{name}.json';new=output/'games'/f'{eid}-{name}.json'
            if old.exists():
                value=json.loads(old.read_text());assert value['sha256']==sha(path)
                assert value['freeze_sha256']==sha(freeze_path)
            elif new.exists():
                value=json.loads(new.read_text());assert value['sha256']==sha(path)
                assert value['freeze_sha256']==sha(freeze_path)
            else:
                value=run_game(path,ROOT/row['opponent_path'],int(row['seed']),int(row['dp_seat']),replay=replay,verify_identity=name=='parent')
                value.update(card_sha256=freeze['card_sha256'],freeze_sha256=sha(freeze_path),started_at=datetime.now(timezone.utc).isoformat())
                save(new,value)
            if name=='parent' and not value['identity']['passed']:
                raise RuntimeError(f'BLOCKED_PARENT_REPRODUCTION {eid}')
            values[name]=value
            print('panel',eid,name,value['margin'],flush=True)
        p,c=values['parent'],values[candidate]
        runtime.append(c)
        panel.append(dict(episode=eid,seed=int(row['seed']),seat=int(row['dp_seat']),family=row['closest_file'],
                          parent=p['score'],candidate=c['score'],delta=c['score']-p['score'],
                          new_loss=row['result']=='W' and c['score']==0,
                          flipped=row['result']=='L' and c['score']==1,
                          weight=weights[row['submission']] if row['result']=='W' else 1))
    assert len(panel)==47 and len({r['seed'] for r in panel})==47
    direct=[]
    for seed in range(2400,2440):
        for seat in (0,1):
            path=output/'direct'/f'{seed}-{seat}.json'
            if path.exists():
                value=json.loads(path.read_text());assert value['sha256']==spec['sha256']
                assert value['freeze_sha256']==sha(freeze_path)
            else:
                value=run_game(ROOT/spec['path'],PARENT,seed,seat)
                value.update(card_sha256=freeze['card_sha256'],freeze_sha256=sha(freeze_path),started_at=datetime.now(timezone.utc).isoformat())
                save(path,value)
            direct.append(value);runtime.append(value)
            print('DP80',seed,seat,value['margin'],flush=True)
    differences=[r['delta'] for r in panel]
    delta=statistics.mean(differences);se=statistics.stdev(differences)/len(panel)**.5
    dp_score=statistics.mean(r['score'] for r in direct)
    new_losses=sum(r['new_loss'] for r in panel);flips=sum(r['flipped'] for r in panel)
    max_step=max(r['timing'][0]['max_seconds'] for r in runtime)
    valid=all(r['steps']==720 and r['statuses']==['DONE','DONE'] and not r['exceptions'][0] and
              not any(e['agent']==0 for e in r['caught_errors']) for r in runtime)
    if delta<=0 or not valid or max_step>=.5:verdict='FAILURE'
    elif delta<=2*se:verdict='INCONCLUSIVE'
    elif new_losses<=flips/3:verdict='SUCCESS'
    else:verdict='BLOCKED_VERDICT_GAP'
    non_dp=[r for r in panel if r['family']!='DP-0924-exact']
    denom=sum(r['weight'] for r in non_dp)
    base=sum(r['weight']*r['parent'] for r in non_dp)/denom
    cand=sum(r['weight']*r['candidate'] for r in non_dp)/denom
    current=sum(r['weight'] for r in panel if r['family']=='DP-0924-exact')/sum(r['weight'] for r in panel)
    scenarios=[]
    for label,p in [('current_panel',current),('20%',.2),('40%',.4)]:
        a=(1-p)*base+p*.5;b=(1-p)*cand+p*dp_score
        scenarios.append(dict(label=label,dp_share=p,parent=a,candidate=b,delta=b-a))
    paired=[statistics.mean([r['score'] for r in direct if r['seed']==seed]) for seed in range(2400,2440)]
    summary=dict(panel=panel,n=47,delta=delta,paired_se=se,two_se=2*se,new_losses=new_losses,flipped_losses=flips,
                 panel_verdict=verdict,dp80_score=dp_score,dp_floor_pass=dp_score>=.5,
                 dp80_seed_paired_se=statistics.stdev(paired)/40**.5,dp80_seed_scores=paired,
                 eligible_success=verdict=='SUCCESS' and dp_score>=.5,
                 b2='N/A: separate B2/E2 evidence required',max_step_seconds=max_step,execution_valid=valid,
                 scenarios=scenarios,scenario_scope='eligible FULL sampled nondraw opponents only; not whole field prediction',
                 card_sha256=freeze['card_sha256'],freeze_sha256=sha(freeze_path))
    save(output/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['panel','dp80_seed_scores']}),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--freeze',type=Path)
    ap.add_argument('--candidate',required=True,help='Frozen candidate name, or arbitrary path for --phase game')
    ap.add_argument('--phase',choices=['q2','q4','game'],default='q2')
    ap.add_argument('--opponent',type=Path)
    ap.add_argument('--seed',type=int)
    ap.add_argument('--seat',type=int,choices=[0,1])
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    if args.phase=='game':
        if args.opponent is None or args.seed is None or args.seat is None or args.output is None:
            ap.error('game requires --opponent --seed --seat --output')
        save(args.output,run_game(Path(args.candidate).resolve(),args.opponent.resolve(),args.seed,args.seat))
    else:
        if args.freeze is None:
            ap.error('q2/q4 require --freeze')
        (q2 if args.phase=='q2' else q4)(args.freeze,args.candidate)
