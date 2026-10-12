"""Bounded constant/layer search and checkpoint-reserved holdout; offline only."""
from __future__ import annotations
import ast
import concurrent.futures
import csv
from datetime import datetime
import fcntl
import gzip
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import re
import statistics
import subprocess
import tarfile
import time
from zoneinfo import ZoneInfo
from search_loop import ROOT,OUT,sha,atomic,stamp,job_key,execute,append_game,read_journal
from search_stages import job,summary,all_rows,report,DP,NEW,source_gate,cleanroom
from search_calibration import frozen_batch

CP={'CP1':(datetime(2026,9,26,21,tzinfo=ZoneInfo('Asia/Seoul')).timestamp(),9000,9200),
    'CP2':(datetime(2026,9,28,21,tzinfo=ZoneInfo('Asia/Seoul')).timestamp(),9200,9400)}
END=CP['CP2'][0]


def verify_metric():
    path=OUT/'metric.json';pin=json.loads((OUT/'metric-sha256.json').read_text())['sha256']
    if sha(path)!=pin:raise RuntimeError('METRIC_CHANGED')
    m=json.loads(path.read_text())
    if json.loads((OUT/'calibration-summary.json').read_text())['status']!='PASS':raise RuntimeError('CALIBRATION_NOT_PASS')
    if m['tape']:
        raise RuntimeError('BLOCKED_TAPE_HOLDOUT_SEED_CONFLICT: recorded tape seed/seat cannot also be disjoint9000-9399; Coordinator definition required')
    return m,pin


def batch(name,jobs):
    return frozen_batch(name,jobs,extra=['tools/search_optimize.py','experiments/search_20260925/metric.json',
                                      'experiments/search_20260925/metric-sha256.json'])


def se(values):
    return statistics.stdev(values)/math.sqrt(len(values)) if len(values)>1 else None


def choose_parent(metric):
    saved=OUT/'parent.json'
    if saved.exists():return json.loads(saved.read_text())
    candidates=json.loads((OUT/'tournament-reconciled.json').read_text())['finalists']
    jobs=[job('parent-metric-'+x['sha256'][:12],x['path'],op,s,p) for x in candidates for op in metric['weights'] for s in range(2600,2620) for p in (0,1)]
    rows=batch('parent-metric',jobs);rank=[]
    for x in candidates:
        rs=[r for r in rows if r['job']['path']==x['path']];st=summary(rs)
        value=sum(w*statistics.mean(r['result']['score'] for r in rs if r['job']['opponent']==op) for op,w in metric['weights'].items())
        rank.append(dict(x,metric_score=value,metric_runtime=st))
    rank.sort(key=lambda x:(x['metric_runtime']['invalid']==0,x['metric_score'],x['confirmation_dp']['score'],x['sha256']),reverse=True)
    if not rank or rank[0]['metric_runtime']['invalid']:raise RuntimeError('NO_METRIC_PARENT')
    parent=rank[0];atomic(saved,parent);atomic(OUT/'parent-metric-ranking.json',rank)
    report('PARENT-METRIC','# PARENT-METRIC\n\n[LOCAL] Calibration으로 동결한 metric으로 상위5개를 채점했다. 부모 SHA `'+parent['sha256']+'`, metric score='+str(parent['metric_score'])+'. DP 직접 대결은 동률 처리에만 사용했다. 전체 순위는 `experiments/search_20260925/parent-metric-ranking.json`에 보존했다. 다른 계열 여부는 코드 메커니즘 검토 없이 SHA만으로 단정하지 않는다. 따라서 별도 슬롯 B exact 추천은 이 자동 보고에서 N/A다.\n\n다음 행동 두 가지: ① 같은 부모의 상수·층 제거만 탐색한다. ② 사람은 두 번째 후보의 메커니즘이 다른지 검토한다.\n')
    return parent


def mutation_specs(source):
    tree=ast.parse(source);constants={};aliases={};defs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    for n in tree.body:
        if not isinstance(n,ast.Assign) or len(n.targets)!=1 or not isinstance(n.targets[0],ast.Name):continue
        name=n.targets[0].id
        if isinstance(n.value,ast.Name) and name.endswith('_PARENT'):aliases[name]=n.value.id
        if not re.fullmatch(r'_?[A-Z][A-Z0-9_]{2,}',name):continue
        try:value=ast.literal_eval(n.value)
        except (ValueError,TypeError):continue
        if type(value) in (int,float) and math.isfinite(value):constants[name]=value
    # Fixed game constraints and KILL-related levers are not search parameters.
    excluded=re.compile(r'GOOSE|COOP|EGG|QUAD|LAND|ADV_LOOK|ADVANCE|LEAD|STARTER|PPO|CLEAN|WEED|TURNS_PER_DAY|LAST_STEP|MAX_ORDERS|SHED_CAP')
    specs=[]
    for name,value in constants.items():
        if excluded.search(name):continue
        step=1 if type(value)==int else abs(value)*.1 if value else .1
        for sign in (-1,1):specs.append(dict(kind='constant',target=name,old=value,new=value+sign*step))
    # Redirect the reference to one wrapper to that wrapper's own parent.
    for outer,fn in aliases.items():
        if fn not in defs:continue
        calls={n.func.id for n in ast.walk(defs[fn]) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id.endswith('_PARENT')}
        if len(calls)==1:
            inner=next(iter(calls))
            if inner in aliases and inner!=outer:specs.append(dict(kind='layer',target=outer,old=fn,new=inner))
    return specs


def build_variant(parent,changes,identifier):
    original=(ROOT/parent).read_bytes()
    text='\n# Frozen search wrapper; parent bytes above are unchanged.\n_SEARCH_ENTRY = [v for v in globals().values() if callable(v)][-1]\n'
    for c in changes:text+=c['target']+' = '+(repr(c['new']) if c['kind']=='constant' else c['new'])+'\n'
    text+='def search_entry(obs, configuration=None):\n    return _SEARCH_ENTRY(obs, configuration)\n'
    content=original+text.encode();path=OUT/'variants'/identifier/'main.py';path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes()!=content:raise RuntimeError('VARIANT_CHANGED')
    if not path.exists():path.write_bytes(content)
    compile(content,str(path),'exec')
    return dict(id=identifier,path=str(path.relative_to(ROOT)),sha256=sha(path),changes=changes,parent_sha256=hashlib.sha256(original).hexdigest(),
                git_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())


def variants(parent):
    saved=OUT/'variants.json'
    if saved.exists():return json.loads(saved.read_text())
    specs=mutation_specs((ROOT/parent).read_bytes())
    # Deterministic round-robin includes both constant and layer-off hypotheses.
    constants=[x for x in specs if x['kind']=='constant'];layers=[x for x in specs if x['kind']=='layer']
    ordered=[]
    for pair in itertools.zip_longest(constants,layers):ordered.extend(x for x in pair if x)
    if len(ordered)<150:raise RuntimeError('FEWER_THAN150_ADMISSIBLE_VARIANTS: do not invent extra levers')
    result=[build_variant(parent,[x],f'v{i:03}') for i,x in enumerate(ordered[:150])]
    atomic(saved,result);return result


def schedule(metric,pin,start):
    """Common-seed Monte Carlo estimator of the frozen weighted score rate."""
    cumulative=[];total=0
    for op,w in sorted(metric['weights'].items()):total+=w;cumulative.append((total,op))
    if abs(total-1)>1e-10:raise RuntimeError('INVALID_PUBLIC_WEIGHTS')
    result=[]
    for seed in range(start,start+500):
        u=int(hashlib.sha256((pin+':'+str(seed)).encode()).hexdigest(),16)/2**256
        op=next((op for cutoff,op in cumulative if u<cutoff),cumulative[-1][1])
        result.extend((seed,p,op) for p in (0,1))
    return result


def evaluated(variant,base_id,n,schedule):
    wanted={(s,p,op) for s,p,op in schedule[:n]};rs={};base={}
    for row in all_rows():
        j=row['job'];key=(j['seed'],j['seat'],j['opponent'])
        if key not in wanted:continue
        if j['variant']==variant['id']:rs[key]=row
        elif j['variant']==base_id:base[key]=row
    if len(rs)!=n or len(base)!=n:raise RuntimeError('INCOMPLETE_PAIRED_STAGE')
    stats=summary(list(rs.values()))
    if summary(list(base.values()))['invalid']:raise RuntimeError('INVALID_SEARCH_BASELINE')
    if stats['invalid']:
        return dict(variant,stage=n,n=n,delta=-1,paired_se_active=None,proxy=-1e30,activation_rate=0,
                    invalid=stats['invalid'],max_step=stats['max_step'],max_game_p99=stats['max_game_p99'],runtime_pass=False)
    delta=[];active=[];proxy=[];perseed={}
    for key in sorted(wanted):
        c=rs[key]['result'];p=base[key]['result'];d=c['score']-p['score']
        delta.append(d);perseed.setdefault(key[0],[]).append(d)
        activated=(c['action_sha256']!=p['action_sha256'] or c['rewards']!=p['rewards'])
        active.append(activated)
        proxy.append((c['margin']-p['margin'])/max(1,abs(p['rewards'][0])+abs(p['rewards'][1])))
    active_seed_values=[statistics.mean(v) for seed,v in perseed.items() if any(active[i] for i,k in enumerate(sorted(wanted)) if k[0]==seed)]
    result=dict(variant,stage=n,n=n,delta=statistics.mean(delta),paired_se_active=se(active_seed_values),
                proxy=statistics.mean(proxy),activation_rate=statistics.mean(active),**{k:stats[k] for k in ['invalid','max_step','max_game_p99']})
    result['runtime_pass']=stats['invalid']==0 and stats['max_step']<.25 and stats['max_game_p99']<.1
    return result


def leaderboard(records):
    path=OUT/'leaderboard.csv';tmp=path.with_suffix('.csv.tmp')
    git=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    fields=['id','diff','stage','seed_set','git_sha','sha256','n','delta','SE','activation_rate','exceptions','max_step']
    with tmp.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in records:w.writerow(dict(id=r['id'],diff=json.dumps(r['changes'],ensure_ascii=False),stage=r['stage'],seed_set=r['seed_set'],git_sha=r.get('git_sha',git),sha256=r['sha256'],n=r['n'],delta=r['delta'],SE=r['paired_se_active'],activation_rate=r['activation_rate'],exceptions=r['invalid'],max_step=r['max_step']))
    tmp.replace(path)


def halving(parent,items,metric,pin,start,label):
    saved=OUT/(label+'-results.json')
    if saved.exists():return json.loads(saved.read_text())
    if time.time()>=END:return dict(final=[],records=[])
    sched=schedule(metric,pin,start);baseid=label+'-parent'
    atomic(OUT/(label+'-schedule.json'),dict(metric_sha256=pin,schedule=sched,definition='hashed categorical sampling from frozen weights, paired seeds; same schedule for every variant'))
    batch(label+'-baseline',[job(baseid,parent,op,s,p) for s,p,op in sched])
    survivors=items;records=[];previous=0
    for n,keep in [(40,50),(120,15),(400,3),(1000,3)]:
        if time.time()>=END:break
        jobs=[job(x['id'],x['path'],op,s,p) for x in survivors for s,p,op in sched[previous:n]]
        # Use a conservative measured throughput budget before starting a stage.
        rate=min(json.loads((OUT/'stage1-summary.json').read_text())['throughput'][k] for k in ['initial_per_hour','late_per_hour'])/7200
        if time.time()+len(jobs)/rate>END:break
        batch(label+'-'+str(n),jobs)
        stage=[evaluated(x,baseid,n,sched) for x in survivors]
        for r in stage:r['seed_set']=f'{start}-{start+n//2-1} both'
        records.extend(stage)
        stage.sort(key=lambda r:(r['invalid']==0,r['delta'] if n==1000 else r['proxy'],r['id']),reverse=True)
        survivors=[x for x in stage if x['invalid']==0][:keep];previous=n
        atomic(OUT/(label+'-progress.json'),dict(stage=n,survivors=survivors,records=records));leaderboard(records)
        if not survivors:break
    final=[r for r in records if r['stage']==1000]
    result=dict(final=final,records=records);atomic(saved,result);return result


def combinations(parent,records):
    good=[r for r in records if r['runtime_pass'] and r['paired_se_active'] is not None and r['delta']>2*r['paired_se_active']]
    result=[]
    for n in (2,3):
        for group in itertools.combinations(good,n):
            changes=[c for x in group for c in x['changes']]
            if len({c['target'] for c in changes})!=len(changes):continue
            identifier='mix-'+'-'.join(x['id'] for x in group)
            result.append(build_variant(parent,changes,identifier))
    return result


def holdout_batch(cp,candidate,parent,pin,jobs):
    """Checkpoint claim is durable BEFORE any seed is evaluated; resume same claim only."""
    if time.time()<CP[cp][0]:raise RuntimeError('CHECKPOINT_NOT_DUE')
    if sha(OUT/'metric.json')!=pin:raise RuntimeError('HOLDOUT_METRIC_CHANGED')
    claim=dict(checkpoint=cp,candidate_sha256=candidate['sha256'],parent_sha256=sha(ROOT/parent),metric_sha256=pin,
               seed_start=CP[cp][1],seed_stop=CP[cp][2])
    claimpath=OUT/(cp+'-holdout-claim.json')
    manifestpath=OUT/(cp+'-holdout-manifest.json')
    with (OUT/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if claimpath.exists():
            if json.loads(claimpath.read_text())!=claim:raise RuntimeError('HOLDOUT_ALREADY_CLAIMED_FOR_DIFFERENT_CANDIDATE')
        else:atomic(claimpath,claim)
        paths={j[f] for j in jobs for f in ['path','opponent']}
        paths.update(['tools/search_loop.py','tools/search_optimize.py','tools/dp_counterfactual.py','tools/dp_loss_cause.py','tools/reproduce_replay.py','experiments/search_20260925/metric.json'])
        expected=dict(claim=claim,workers=6,jobs=jobs,sha256={p:sha(ROOT/p) for p in sorted(paths)})
        if manifestpath.exists():
            if json.loads(manifestpath.read_text())!=expected:raise RuntimeError('HOLDOUT_MANIFEST_CHANGED')
        else:atomic(manifestpath,expected)
        manifest_sha=sha(manifestpath);runner_sha=sha(ROOT/'tools/search_loop.py')
        if len({job_key(j) for j in jobs})!=len(jobs):raise RuntimeError('DUPLICATE_HOLDOUT_JOB')
        for j in jobs:
            if not CP[cp][1]<=j['seed']<CP[cp][2]:raise RuntimeError('HOLDOUT_SEED_OUTSIDE_CHECKPOINT')
            if j['sha256'] not in (candidate['sha256'],claim['parent_sha256']):raise RuntimeError('UNCLAIMED_CANDIDATE')
            if sha(ROOT/j['path'])!=j['sha256'] or sha(ROOT/j['opponent'])!=j['opponent_sha256']:raise RuntimeError('HOLDOUT_ARTIFACT_CHANGED')
        journal=read_journal(OUT/'games.jsonl');pending=[]
        for j in jobs:
            old=journal.get(job_key(j))
            if old and (old['manifest_sha256']!=manifest_sha or old['job']!=j):raise RuntimeError('HOLDOUT_RESUME_MISMATCH')
            if not old:pending.append(j)
        print(json.dumps(dict(event='holdout-resume',at=stamp(),checkpoint=cp,skipped=len(jobs)-len(pending),remaining=len(pending))),flush=True)
        count=len(jobs)-len(pending)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            todo=iter(pending);active={}
            for _ in range(6):
                j=next(todo,None)
                if j:active[pool.submit(execute,j)]=j
            while active:
                done,_=concurrent.futures.wait(active,return_when=concurrent.futures.FIRST_COMPLETED)
                for future in done:
                    active.pop(future);row=future.result();row.update(manifest_sha256=manifest_sha,runner_sha256=runner_sha)
                    append_game(OUT/'games.jsonl',row);journal[row['key']]=row
                    count+=1
                    atomic(OUT/'state.json',dict(batch=cp+'-holdout',status='RUNNING',updated_at=stamp(),total=len(jobs),completed=count,workers=6))
                    if row['result']['worker_peak_rss_bytes']*6>24*1024**3*.7:raise RuntimeError('HOLDOUT_MEMORY_BUDGET')
                    j=next(todo,None)
                    if j:active[pool.submit(execute,j)]=j
        atomic(OUT/'state.json',dict(batch=cp+'-holdout',status='COMPLETE',updated_at=stamp(),total=len(jobs),completed=len(jobs),workers=6))
        return [journal[job_key(j)] for j in jobs]


def panel(cp,candidate,parent):
    rows=json.loads((ROOT/'experiments/results/dp_loss_cause_20260925/freeze.json').read_text())['panel'];jobs=[]
    for x in rows:
        if x['eligible']:
            for label,path in [('parent',parent),('candidate',candidate['path'])]:jobs.append(job(cp+'-panel-'+label+'-'+x['episode'],path,x['opponent_path'],x['seed'],x['dp_seat'],episode=x['episode']))
    actual=batch(cp+'-panel',jobs);lookup={r['job']['variant']:r['result'] for r in actual}
    new_losses=sum(lookup[cp+'-panel-parent-'+x['episode']]['score']>0 and lookup[cp+'-panel-candidate-'+x['episode']]['score']==0 for x in rows if x['eligible'])
    return dict(new_losses=new_losses,invalid=summary(actual)['invalid'])


def checkpoint(cp,candidate,parent,metric,pin):
    resultpath=OUT/(cp+'-result.json')
    if resultpath.exists() and (OUT/('report-'+cp+'-HOLDOUT.json')).exists():return json.loads(resultpath.read_text())
    ops=sorted(set(metric['weights'])|{DP,NEW})
    jobs=[job(cp+'-'+label,path,op,s,p) for label,path in [('parent',parent),('candidate',candidate['path'])] for op in ops for s in range(CP[cp][1],CP[cp][2]) for p in (0,1)]
    rows=holdout_batch(cp,candidate,parent,pin,jobs);by={(r['job']['variant'],r['job']['opponent'],r['job']['seed'],r['job']['seat']):r['result']['score'] for r in rows}
    differences=[];op_delta={};scores={}
    for op in ops:
        scores[op]={label:[statistics.mean(by[(cp+'-'+label,op,s,p)] for p in (0,1)) for s in range(CP[cp][1],CP[cp][2])] for label in ('parent','candidate')}
        op_delta[op]=statistics.mean(scores[op]['candidate'])-statistics.mean(scores[op]['parent'])
    for i in range(200):differences.append(sum(w*(scores[op]['candidate'][i]-scores[op]['parent'][i]) for op,w in metric['weights'].items()))
    delta=statistics.mean(differences);error=se(differences)
    # 2.0 > t_(.975,199): conservative paired-seed 95% lower bound.
    lower={op:statistics.mean(scores[op]['candidate'])-2*se(scores[op]['candidate']) for op in (DP,NEW)}
    votes={}
    for p in (ROOT/'analysis/daily_scan').glob('2026092[2345]/lineage.json'):
        for x in json.loads(p.read_text()):
            h=x.get('main_sha256');votes[h]=max(votes.get(h,0),x.get('votes') or 0)
    guard=sorted(metric['weights'],key=lambda op:(votes.get(sha(ROOT/op),0),sha(ROOT/op)),reverse=True)[:15]
    regression=panel(cp,candidate,parent)
    stats=summary([r for r in all_rows() if r['result']['sha256']==candidate['sha256']])
    stats['scope']='All recorded games of these exact candidate bytes; later runs do not erase earlier runtime failures'
    passed=all([error is not None,delta>2*error,lower[NEW]>.50,lower[DP]>.45,
                regression['new_losses']==0,regression['invalid']==0,stats['invalid']==0,
                stats['max_step']<.25,stats['max_game_p99']<.1,all(op_delta[op]>=-.10-1e-12 for op in guard)])
    result=dict(checkpoint=cp,status='SUCCESS' if passed else 'FAIL',candidate=candidate,parent=parent,
                metric_sha256=pin,delta=delta,paired_se=error,lower95=lower,guard={op:op_delta[op] for op in guard},panel=regression,runtime=stats,
                ci_method='paired-seed mean minus2SE, conservative versus Student t(.975,199); both seats share seed cluster')
    atomic(resultpath,result)
    if passed:release(candidate,cp)
    report(cp+'-HOLDOUT','# '+cp+' HOLDOUT — '+result['status']+'\n\n[LOCAL] checkpoint마다 최상위1개만 고정하고 해당 seed를 한 번 사용했다. 재시작은 같은 claim의 미완료 경기만 이어간다. 결과는 `experiments/search_20260925/'+cp+'-result.json`에 원자료 key와 함께 보존했다. Δ='+str(delta)+', paired SE='+str(error)+', NEWMETA lower='+str(lower[NEW])+', DP lower='+str(lower[DP])+'. 제출하지 않았다.\n\n다음 행동 두 가지: ① gate별 결과와 exact SHA를 검토한다. ② SUCCESS release도 별도 사람 판단 전 제출하지 않는다.\n')
    return result


def release(candidate,cp):
    source=(ROOT/candidate['path']).read_bytes();directory=ROOT/'releases'/('search-'+cp.lower()+'-'+candidate['id']);directory.mkdir(exist_ok=True)
    gate=source_gate(candidate['path']);isolation=cleanroom(candidate['path'])
    if not gate['dependency_pass'] or not isolation['passed']:raise RuntimeError('RELEASE_ISOLATION_OR_DEPENDENCY_FAILED')
    path=directory/'main.py'
    if path.exists() and path.read_bytes()!=source:raise RuntimeError('RELEASE_ALREADY_DIFFERENT')
    path.write_bytes(source)
    with (directory/'submission.tar.gz').open('wb') as out:
        with gzip.GzipFile(fileobj=out,mode='wb',filename='',mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w') as tar:
                info=tarfile.TarInfo('main.py');info.size=len(source);info.mode=0o644;tar.addfile(info,io.BytesIO(source))
    atomic(directory/'gate.json',dict(Identity=sha(path)==candidate['sha256'],Schema='root main.py; actual last callable search_entry',Runtime='see checkpoint raw measurements',Isolation=isolation,License='parent notices retained; human review required',Ledger='N/A, no submission',main_sha256=sha(path),tar_sha256=sha(directory/'submission.tar.gz')))


def search():
    terminal=OUT/'search-terminal.json'
    if terminal.exists():return
    metric,pin=verify_metric();parent=choose_parent(metric);items=variants(parent['path'])
    first=halving(parent['path'],items,metric,pin,3000,'search-single')
    mixes=combinations(parent['path'],first['final'])
    second=halving(parent['path'],mixes,metric,pin,4000,'search-combination') if mixes else dict(final=[],records=[])
    all_final=first['final']+second['final'];leaderboard(first['records']+second['records'])
    eligible=[r for r in all_final if r['runtime_pass']]
    if not eligible:
        value=dict(status='NO_ELIGIBLE1000_GAME_CANDIDATE',at=stamp())
        atomic(terminal,value);atomic(OUT/'workflow-terminal.json',value)
        report('SEARCH-END','# SEARCH END — NO_ELIGIBLE1000_GAME_CANDIDATE\n\n고정 탐색을 수행했으나 1,000경기와 runtime 조건을 모두 만족하는 후보를 확보하지 못했다. Holdout은 사용하지 않았고 제출하지 않았다.\n\n다음 행동 두 가지: ① leaderboard.csv의 탈락 이유를 검토한다. ② 기존 활성 슬롯을 기준으로 사람 판단을 받는다.\n')
        return
    completed={}
    for row in all_rows():
        identifier=row['job']['variant']
        if identifier in {x['id'] for x in eligible}:
            completed[identifier]=max(completed.get(identifier,0),datetime.fromisoformat(row['completed_at']).timestamp())
    for cp,(when,_,_) in CP.items():
        at_checkpoint=[x for x in eligible if completed[x['id']]<=when]
        if not at_checkpoint:
            report(cp+'-HOLDOUT','# '+cp+' — NO_CANDIDATE_AT_CHECKPOINT\n\n해당 checkpoint 시각까지 1,000경기를 완료한 유효 후보가 없어 holdout을 사용하지 않았다. 나중에 얻은 탐색 결과를 이 시점의 후보로 소급하지 않는다.\n\n다음 행동 두 가지: ① 탐색 완료 시각을 확인한다. ② 다음 checkpoint는 별도 seed와 그 시점까지의 자료로 판단한다.\n')
            continue
        best=max(at_checkpoint,key=lambda x:(x['delta'],x['id']))
        atomic(OUT/(cp+'-selection.json'),dict(candidate=best,selection_source='training completed by checkpoint only, never holdout',selection_cutoff=when,metric_sha256=pin))
        while time.time()<when:
            atomic(OUT/'workflow-state.json',dict(status='WAITING_CHECKPOINT',checkpoint=cp,at=stamp(),candidate=best['id']))
            time.sleep(min(30,when-time.time()))
        checkpoint(cp,best,parent['path'],metric,pin)
    value=dict(status='COMPLETE_NO_SUBMISSION',at=stamp())
    atomic(terminal,value);atomic(OUT/'workflow-terminal.json',value)
