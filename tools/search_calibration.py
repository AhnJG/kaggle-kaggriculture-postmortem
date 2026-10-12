"""Four preregistered metric candidates; fail closed, no submissions/holdout."""
from __future__ import annotations
import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import tarfile

from search_loop import ROOT,OUT,sha,atomic,stamp,job_key
from search_stages import job,batch,summary,source_gate,cleanroom,report,DP,NEW,all_rows

PAIRS=[('C1','EXP016'),('EXP017','EXP016'),('EXP017','DP'),('YHAY','P2'),('EXP007','EXP006')]
ARCHIVES={
 'C1':'releases/public-nathanjacob-pipe16-exact/submission_clean.tar.gz',
 'EXP016':'releases/f0-c1-adv-exp016/submission.tar.gz',
 'EXP017':'releases/f0-omw-adv-exp017/submission.tar.gz',
 'DP':'releases/public-tetsutani-demand-preserving-0924-exact/submission.tar.gz',
 'YHAY':'releases/public-yhay81-shop-router-0909-exact/submission.tar.gz',
 'P2':'releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz',
 'EXP007':'releases/public-thomas-replay-router-v2-exact/submission.tar.gz',
 'EXP006':'coordination/proposals/claude/exp006/submission.tar.gz'}


def preregister():
    path=OUT/'calibration-policy.json'
    value=dict(version=1,seed_start=2600,seed_stop=2620,seats=[0,1],
               pool_filter_parent='tournament confirmation highest valid combined score; freeze once before metric selection',
               pool_exclusion='provisional parent wins at least95percent; block if this removes an anchor required by fixed weights',
               weights={'a':{'newmeta':.30,'dp':.15,'rest':.55},'b':{'newmeta':.50,'dp':.15,'rest':.35},'c':'uniform',
                        'd':'0.60*a public + bins2200-2400:0.15,2400-2600:0.15,2600+:0.10'},
               tape_selection='first20 distinct episode IDs per target bin sorted numerically, exclude panel47 and known invalid DP submission56502662',
               bias_selection='first40 FULL-match step91 episodes sorted numerically; tournament first to second finalist delta; identical0/0 deltas excluded',
               bias_gate=.70,proxy_min_prefix=143,calibration_required=4,mandatory_pair=['EXP017','EXP016'],
               assumptions='Unspecified numerical defaults proposed before execution; user resumed task. Recorded as implementation assumptions, not retroactive Coordinator approval.',
               stage3_integer_step=1,stage3_float_relative_step=.1,stage3_zero_float_step=.1,
               scope='No holdout, no adaptive resampling, no threshold relaxation')
    if path.exists():
        if json.loads(path.read_text())!=value:raise RuntimeError('CALIBRATION_POLICY_CHANGED')
    else:atomic(path,value)
    return value


def frozen_batch(name,jobs,extra=()):
    path=OUT/(name+'.json')
    paths={'tools/search_loop.py','tools/search_stages.py','tools/search_calibration.py','tools/dp_counterfactual.py',
           'tools/dp_loss_cause.py','tools/reproduce_replay.py','experiments/search_20260925/calibration-policy.json'}
    paths.update(extra)
    for j in jobs:
        paths.update([j['path'],j['opponent']])
        for field in ('path','opponent'):
            # Freeze complete historical bundles, including actions.json/yh_base.py.
            p=ROOT/j[field]
            if 'historical' in p.parts:
                paths.update(str(x.relative_to(ROOT)) for x in p.parent.rglob('*') if x.is_file() and '__pycache__' not in x.parts)
    if path.exists():
        if json.loads(path.read_text())['jobs']!=jobs:raise RuntimeError('CALIBRATION_JOBS_CHANGED')
    else:atomic(path,dict(id=name,workers=6,hypothesis_id='HYP-0012',test_id='TEST-SEARCH-20260925-CALIBRATION',
                         frozen_at=stamp(),sha256={p:sha(ROOT/p) for p in sorted(paths)},jobs=jobs))
    return batch(path)


def historical():
    result={}
    for name,archive in ARCHIVES.items():
        directory=OUT/'historical'/name
        directory.mkdir(parents=True,exist_ok=True)
        members={}
        with tarfile.open(ROOT/archive) as tar:
            for member in tar.getmembers():
                if member.isdir():continue
                target=directory/member.name
                if not member.isfile() or not target.resolve().is_relative_to(directory.resolve()):raise RuntimeError('UNSAFE_TAR_MEMBER')
                b=tar.extractfile(member).read();target.parent.mkdir(parents=True,exist_ok=True)
                if target.exists() and target.read_bytes()!=b:raise RuntimeError('HISTORICAL_BUNDLE_CHANGED')
                if not target.exists():target.write_bytes(b)
                members[member.name]=hashlib.sha256(b).hexdigest()
        result[name]=str((directory/'main.py').relative_to(ROOT))
        atomic(directory/'bundle-identity.json',dict(archive=archive,sha256=sha(ROOT/archive),members=members))
    atomic(OUT/'historical-artifacts.json',result)
    return result


def public_pool(parent,policy):
    auditpath=OUT/'calibration-pool-audit.json'
    if auditpath.exists():audits=json.loads(auditpath.read_text())
    else:
        seen={}
        for day in range(22,26):
            for p in sorted((ROOT/f'analysis/daily_scan/202609{day}/extracted').glob('*/main.py')):
                h=sha(p)
                if h in seen:continue
                rel=str(p.relative_to(ROOT)); gate=source_gate(rel)
                loader=cleanroom(rel) if gate['dependency_pass'] else {'passed':False,'entry':None}
                seen[h]=dict(path=rel,sha256=h,source_gate=gate,loader=loader,eligible=gate['dependency_pass'] and loader['passed'])
        for rel in (DP,NEW):
            h=sha(ROOT/rel)
            seen[h]=dict(path=rel,sha256=h,eligible=True,anchor=True,
                         environment='V92_SELL_LIB absent; DP is a fixed baseline, not an external-dependency-free candidate')
        audits=list(seen.values());atomic(auditpath,audits)
    eligible=[x for x in audits if x['eligible']]
    jobs=[job('pool-filter',parent,x['path'],seed,seat) for x in eligible for seed in range(policy['seed_start'],policy['seed_stop']) for seat in (0,1)]
    rows=frozen_batch('calibration-pool-filter',jobs)
    selected=[];results=[]
    for x in eligible:
        s=summary([r for r in rows if r['job']['opponent']==x['path']])
        # Any invalid opponent is excluded; mandatory anchors must be valid.
        keep=s['invalid']==0 and s['wins']/s['n']<.95
        results.append(dict(x,filter=s,keep=keep))
        if keep:selected.append(x)
        elif x.get('anchor'):raise RuntimeError('ANCHOR_EXCLUDED: fixed weight definition conflicts with95percent filter or execution failed')
    atomic(OUT/'calibration-pool.json',dict(parent=parent,results=results,selected=selected))
    return selected


def weights(pool):
    anchors={sha(ROOT/NEW):'newmeta',sha(ROOT/DP):'dp'}
    rest=[x for x in pool if x['sha256'] not in anchors]
    if not rest:raise RuntimeError('NO_REST_POOL: cannot allocate55/35percent')
    out={}
    for key,new,remaining in [('a',.3,.55),('b',.5,.35)]:
        out[key]={x['path']:new if anchors.get(x['sha256'])=='newmeta' else .15 if anchors.get(x['sha256'])=='dp' else remaining/len(rest) for x in pool}
    out['c']={x['path']:1/len(pool) for x in pool}
    return out


def raw_read(path):
    if str(path).endswith('.gz'):
        with gzip.open(path,'rt') as f:return json.load(f)
    return json.loads(Path(path).read_text())


def tape_file(raw_path,seat,seed):
    raw=raw_read(ROOT/raw_path)
    if len(raw['steps'])!=720:raise RuntimeError('NON720_TAPE')
    if int(raw['info']['seed'])!=int(seed):raise RuntimeError('TAPE_SEED_IDENTITY')
    # Verify all game-rule config fields match the locked default, except seed.
    import contextlib,io
    with contextlib.redirect_stdout(io.StringIO()):
        from kaggle_environments import make
        default=dict(make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)}).configuration)
    # Engine reset consumes configuration.seed and writes it to info.seed.
    observed=dict(raw['configuration']);observed.pop('seed',None);default.pop('seed',None)
    if observed!=default:raise RuntimeError('TAPE_NONDEFAULT_CONFIGURATION '+raw_path)
    actions=[s[seat]['action'] for s in raw['steps'][1:]]
    h=sha(ROOT/raw_path);path=OUT/'tapes'/f'{h[:20]}-{seat}.py';path.parent.mkdir(exist_ok=True)
    content='import copy\n_TAPE = '+repr(actions)+'\ndef agent(obs, configuration=None):\n    return copy.deepcopy(_TAPE[int(obs["step"])])\n'
    if path.exists() and path.read_text()!=content:raise RuntimeError('TAPE_CHANGED')
    if not path.exists():path.write_text(content)
    return str(path.relative_to(ROOT)),int(seed)


def tape_inventory():
    path=OUT/'tape-inventory.json'
    if path.exists():return json.loads(path.read_text())
    excluded={r['episode'] for r in json.loads((ROOT/'experiments/results/dp_loss_cause_20260925/freeze.json').read_text())['panel'] if r['eligible']}
    rows=list(csv.DictReader((ROOT/'analysis/dp_hosted_20260924/opponents.csv').open()))
    selected=[]
    for lo,hi,label in [(2200,2400,'2200-2400'),(2400,2600,'2400-2600'),(2600,float('inf'),'2600+')]:
        candidates=[r for r in rows if r['episode'] not in excluded and r['submission']!='56502662' and r['op_lb_score'] and lo<=float(r['op_lb_score'])<hi]
        candidates.sort(key=lambda r:int(r['episode']))
        used=set()
        for r in candidates:
            if r['episode'] in used:continue
            used.add(r['episode'])
            raw=f"private_artifacts/dp_hosted_20260924/raw/{r['episode']}.json.gz"
            selected.append(dict(episode=r['episode'],seat=int(r['dp_seat']),seed=int(r['seed']),raw=raw,raw_sha256=sha(ROOT/raw),bin=label,
                                 team_lb_score=float(r['op_lb_score']),source='team highest LB, not opponent submission rating',
                                 prefix_len=int(r['prefix_len']),closest_file=r['closest_file']))
            if len(used)==20:break
    # FULL matches in the independent EXP016/017 dataset; panel47 excluded above.
    matches=json.loads((ROOT/'analysis/step91_id/summary.json').read_text())
    full={}
    for info in matches.values():
        for eid,v in info['per_episode'].items():
            if v['match_full'] and eid not in excluded:
                old=full.get(eid)
                if old is None or info['sha']<old['sha']:full[eid]=dict(path=info['path'],sha=info['sha'])
    meta={str(r['id']):r for r in json.loads((ROOT/'analysis/exp016_017_hosted_20260924/manifest.json').read_text())}
    bias=[]
    for eid in sorted(full,key=int):
        if eid not in meta:continue
        m=meta[eid];f=full[eid]
        if sha(ROOT/f['path'])!=f['sha']:raise RuntimeError('FULL_MATCH_SOURCE_CHANGED')
        if sha(ROOT/m['path'])!=m['sha256']:raise RuntimeError('FULL_MATCH_RAW_CHANGED')
        bias.append(dict(episode=eid,seat=int(m['seat']),seed=int(m['seed']),raw=m['path'],raw_sha256=m['sha256'],opponent=f['path']))
        if len(bias)==40:break
    result=dict(panel=selected,bias=bias,excluded_panel47=sorted(excluded),scope='Fixed DP snapshot for target bins; independent step91 FULL matches for bias; no new downloads')
    atomic(path,result);return result


def direction(x):return 1 if x>0 else -1 if x<0 else 0


def reconcile_tournament(t):
    """A short fresh gate cannot erase an already observed runtime violation."""
    saved=OUT/'tournament-reconciled.json'
    if saved.exists():return json.loads(saved.read_text())['finalists']
    known={}
    for row in all_rows():
        r=row['result'];h=r['sha256']
        known[h]=max(known.get(h,0),r['timing'][0]['max_seconds'])
    old={x['sha256']:x for x in t['finalists']};finalists=[];excluded=[]
    for item in t['screening']:
        h=item['sha256']
        if item['summary']['invalid'] or known[h]>=.5:
            excluded.append(dict(sha256=h,reason='invalid or previously observed E5 maximum step',maximum_step=known[h]));continue
        if h in old:
            candidate=old[h]
        else:
            jobs=[job('confirm-correction-'+h[:12],item['path'],op,seed,seat) for op in (DP,NEW) for seed in range(2520,2560) for seat in (0,1)]
            rows=frozen_batch('tournament-confirm-correction-'+h[:12],jobs)
            candidate=dict(item,confirmation=summary(rows),confirmation_dp=summary([r for r in rows if r['job']['opponent']==DP]),
                           confirmation_newmeta=summary([r for r in rows if r['job']['opponent']==NEW]))
        if candidate['confirmation']['invalid'] or candidate['confirmation']['max_step']>=.5:
            excluded.append(dict(sha256=h,reason='confirmation runtime gate failed'));continue
        finalists.append(candidate)
        if len(finalists)==5:break
    finalists.sort(key=lambda x:(x['confirmation']['score'],x['confirmation_dp']['score'],x['sha256']),reverse=True)
    atomic(saved,dict(finalists=finalists,excluded=excluded,reason='Honor all existing runtime evidence; never erase stage1 failure with a shorter later run'))
    if {x['sha256'] for x in finalists}!={x['sha256'] for x in t['finalists']}:
        report('PARENT-TOURNAMENT-GATE-CORRECTION',
               '# PARENT-TOURNAMENT gate correction\n\n짧은 새 gate가 과거 runtime 실패를 지우지 않도록 전체 기존 측정을 대조했다. NEWMETA의 stage1 최대0.750587초를 포함해 E5 최대0.5초 이상인 SHA는 부모 후보에서 제외한다. 기존 경기와 최초 보고는 보존했다. 다음 screening 순위에서 runtime gate를 만족하는 파일로 상위5개를 채웠으며, 추가 confirmation도 원래 seed2520–2559×양좌석×두 상대를 그대로 쓴다. 성능 미달을 이유로 표본을 늘리지 않았다.\n\n정본 후속 후보 목록: `experiments/search_20260925/tournament-reconciled.json`.\n\n다음 행동 두 가지: ① Coordinator는 첫 보고와 이 gate 정정을 함께 읽는다. ② calibration을 통과하기 전까지 부모 확정·탐색·holdout을 보류한다.\n')
    return finalists


def tape_metric(artifacts,finalists):
    inv=tape_inventory()
    if len(finalists)<2:return dict(available=False,reason='Need two gate-valid finalists for bias')
    parent,candidate=[x['path'] for x in finalists[:2]]
    jobs=[]
    for x in inv['bias']:
        tape,seed=tape_file(x['raw'],1-x['seat'],x['seed'])
        if seed!=x['seed']:raise RuntimeError('BIAS_SEED_MISMATCH')
        for label,path in [('parent',parent),('candidate',candidate)]:
            for mode,op in [('open',tape),('closed',x['opponent'])]:jobs.append(job('bias-'+x['episode']+'-'+label+'-'+mode,path,op,seed,x['seat']))
    if not jobs:return dict(available=False,reason='No independent FULL matched bias episodes')
    rows=frozen_batch('calibration-tape-bias',jobs,extra=[x['raw'] for x in inv['bias']])
    byid={r['job']['variant']:r['result'] for r in rows};comparisons=[]
    if summary(rows)['invalid']:return dict(available=False,reason='Bias game invalid')
    for x in inv['bias']:
        delta={}
        for mode in ['open','closed']:
            c=byid['bias-'+x['episode']+'-candidate-'+mode];p=byid['bias-'+x['episode']+'-parent-'+mode]
            delta[mode]=c['score']-p['score']
        informative=delta['open']!=0 or delta['closed']!=0
        comparisons.append(dict(episode=x['episode'],**delta,informative=informative,
                                direction_agrees=direction(delta['open'])==direction(delta['closed']),magnitude_difference=abs(delta['open']-delta['closed'])))
    informative=[x for x in comparisons if x['informative']]
    agreement=statistics.mean(x['direction_agrees'] for x in informative) if informative else None
    use_tape=agreement is not None and agreement>=.70
    # DP fingerprint inventory supplies the longest observed public-file prefix.
    refs=json.loads((ROOT/'analysis/dp_hosted_20260924/file_hashes.json').read_text())
    byname={x['name']:x['path'] for x in refs.values()}
    selected=[];excluded=[]
    for x in inv['panel']:
        if use_tape:
            op,seed=tape_file(x['raw'],1-x['seat'],x['seed'])
        elif x['prefix_len']>=143 and x['closest_file'] in byname:
            op=byname[x['closest_file']];seed=x['seed']
        else:excluded.append(x);continue
        selected.append(dict(x,opponent=op,seed=seed))
    info=dict(available=False,mode='tape' if use_tape else 'public-proxy',direction_agreement=agreement,
              informative_n=len(informative),bias_n=len(comparisons),comparisons=comparisons,excluded=excluded,
              exclusion_rate=len(excluded)/len(inv['panel']) if inv['panel'] else None,selected=selected)
    if any(not any(x['bin']==b for x in selected) for b in ['2200-2400','2400-2600','2600+']):
        info['reason']='Missing target bin after tape/proxy eligibility';atomic(OUT/'tape-bias-summary.json',info);return info
    jobs=[job('tape-cal-'+name+'-'+x['episode'],path,x['opponent'],x['seed'],x['seat']) for name,path in artifacts.items() for x in selected]
    rows=frozen_batch('calibration-tape-panel',jobs,extra=[x['raw'] for x in selected])
    if summary(rows)['invalid']:
        info['reason']='Tape/proxy calibration game invalid';atomic(OUT/'tape-bias-summary.json',info);return info
    values={}
    for name in artifacts:
        values[name]={}
        for b in ['2200-2400','2400-2600','2600+']:
            variants={'tape-cal-'+name+'-'+x['episode'] for x in selected if x['bin']==b}
            values[name][b]=statistics.mean(r['result']['score'] for r in rows if r['job']['variant'] in variants)
    info.update(available=True,values=values);atomic(OUT/'tape-bias-summary.json',info);return info


def _calibrate():
    saved=OUT/'calibration-summary.json'
    if saved.exists():
        previous=json.loads(saved.read_text())
        if previous['status']!='PASS' or all((OUT/p).exists() for p in ('metric.json','metric-sha256.json','report-METRIC-CALIBRATION.json')):
            return previous
    policy=preregister()
    if os.environ.get('V92_SELL_LIB'):raise RuntimeError('UNFROZEN_ENVIRONMENT_V92_SELL_LIB')
    t=json.loads((OUT/'tournament-summary.json').read_text())
    finalists=reconcile_tournament(t)
    if not finalists:raise RuntimeError('NO_VALID_FINALISTS')
    provisional=finalists[0]['path'];artifacts=historical()
    smoke=frozen_batch('calibration-historical-smoke',[job('cal-smoke-'+name,path,DP,2300,0) for name,path in artifacts.items()])
    if summary(smoke)['invalid']:raise RuntimeError('HISTORICAL_ARTIFACT_EXECUTION_FAILED')
    pool=public_pool(provisional,policy);ws=weights(pool)
    jobs=[job('cal-'+name,path,x['path'],seed,seat) for name,path in artifacts.items() for x in pool for seed in range(policy['seed_start'],policy['seed_stop']) for seat in (0,1)]
    rows=frozen_batch('calibration-public',jobs)
    scores={}
    invalid=summary(rows)['invalid']
    for label,w in ws.items():
        scores[label]={name:sum(weight*statistics.mean(r['result']['score'] for r in rows if r['job']['variant']=='cal-'+name and r['job']['opponent']==op) for op,weight in w.items()) for name in artifacts}
    tape=tape_metric(artifacts,finalists)
    if tape['available']:
        scores['d']={name:.6*scores['a'][name]+.15*tape['values'][name]['2200-2400']+.15*tape['values'][name]['2400-2600']+.10*tape['values'][name]['2600+'] for name in artifacts}
    verdicts={}
    for label,values in scores.items():
        order=[values[hi]>values[lo] and not math.isclose(values[hi],values[lo],rel_tol=0,abs_tol=1e-12) for lo,hi in PAIRS]
        verdicts[label]=dict(scores=values,pair_correct=order,correct=sum(order),passed=sum(order)>=4 and order[1] and invalid==0)
    if 'd' not in verdicts:verdicts['d']=dict(passed=False,status='N/A',reason=tape.get('reason'))
    passing=[k for k in verdicts if verdicts[k]['passed']]
    # Largest effective NEWMETA mass; d=0.60*a public (NEWMETA0.18).
    mass={k:v.get(NEW,0) for k,v in ws.items()};mass['d']=.18
    chosen=max(passing,key=lambda k:(mass[k],k)) if passing else None
    result=dict(status='PASS' if chosen else 'BLOCKED',chosen=chosen,verdicts=verdicts,invalid=invalid,
                pairs=PAIRS,provisional_parent=provisional,pool=pool,public_weights=ws,
                tape_summary='experiments/search_20260925/tape-bias-summary.json',policy_sha256=sha(OUT/'calibration-policy.json'))
    atomic(saved,result)
    if chosen:
        metric=dict(version=1,frozen_at=stamp(),chosen=chosen,weights=ws[chosen] if chosen!='d' else {k:v*.6 for k,v in ws['a'].items()},
                    tape=tape if chosen=='d' else None,calibration_sha256=sha(saved),policy_sha256=result['policy_sha256'],
                    provenance='LOCAL retrospective calibration, not independent hosted validation')
        if (OUT/'metric.json').exists():
            old=json.loads((OUT/'metric.json').read_text())
            if any(old[k]!=metric[k] for k in ('chosen','weights','tape','calibration_sha256','policy_sha256')):
                raise RuntimeError('METRIC_ALREADY_FROZEN_DIFFERENT_BYTES')
        else:atomic(OUT/'metric.json',metric)
        pin=OUT/'metric-sha256.json'
        if pin.exists() and json.loads(pin.read_text())['sha256']!=sha(OUT/'metric.json'):raise RuntimeError('METRIC_PIN_MISMATCH')
        if not pin.exists():atomic(pin,dict(sha256=sha(OUT/'metric.json')))
    lines=['# METRIC-CALIBRATION — '+result['status'],'',
           '고정 공개 상대 풀 및 tape/proxy 후보로 과거 같은 시점의 hosted 쌍 순서를 재현했다. 잘못된 지표를 무인 최적화하지 않기 위한 사전 확인이다.',
           f"[LOCAL] 선택={chosen}; mandatory EXP016>EXP017 포함4/5 통과 조건. 실행 이상={invalid}. 실패면 탐색·holdout을 실행하지 않는다.",'',
           '| 후보 | 맞힌 쌍 | mandatory pair | 판정 |','|---|---|---|---|']
    for k,v in verdicts.items():lines.append(f"| {k} | {v.get('correct','N/A')} | {v.get('pair_correct',[None,None])[1]} | {v['passed']} {v.get('reason','')} |")
    lines+=['',f"Tape 방향 일치율={tape.get('direction_agreement')}, informative N={tape.get('informative_n')}, 사용 mode={tape.get('mode')}; 양쪽 Δ=0은 방향 일치 증거에서 제외. 제외율={tape.get('exclusion_rate')}. 팀 LB는 실제 상대 submission rating과 다르다.",
            '', '세부 scores·정확한 artifact/pool/seed/seat/SHA는 `experiments/search_20260925/calibration-summary.json`, 각 calibration manifest와 games.jsonl에 보존. seed2600–2619×양좌석, 후보 가중치4개만 비교. Panel47 및 holdout9000–9599는 제외.',
            '', '다음 행동 두 가지: ① 실패했다면 Coordinator가 metric 가설을 다시 설계한다. ② 통과했다면 metric bytes를 동결하고 상위5개 부모를 그 metric으로 비교한 뒤에만 탐색한다.']
    report('METRIC-CALIBRATION','\n'.join(lines)+'\n')
    return result


def calibrate():
    try:result=_calibrate()
    except Exception as exc:
        result=dict(status='BLOCKED',reason=repr(exc),at=stamp(),metric_frozen=(OUT/'metric.json').exists())
        atomic(OUT/'calibration-summary.json',result)
        report('METRIC-CALIBRATION','# METRIC-CALIBRATION — BLOCKED\n\nCalibration을 유효하게 완료할 수 없어 탐색과 holdout을 시작하지 않았다. 사유: `'+repr(exc)+'`. 이미 완료된 경기와 입력은 보존했다.\n\n다음 행동 두 가지: ① Coordinator가 이 구체적 blocker를 확인한다. ② 해소 근거와 별도 재개 결정 후에만 진행하고 기준이나 기존 결과를 바꾸지 않는다.\n')
        return result
    if result['status']=='PASS':
        try:
            ready=OUT/'search-ready.json'
            if ready.exists():
                spec=json.loads(ready.read_text())
                if sha(ROOT/'tools/search_optimize.py')!=spec['sha256']:raise RuntimeError('SEARCH_CODE_CHANGED')
                from search_optimize import search
                search()
            else:atomic(OUT/'workflow-state.json',dict(status='WAITING_SEARCH_SETUP',at=stamp()))
        except Exception as exc:
            atomic(OUT/'workflow-terminal.json',dict(status='BLOCKED_SEARCH',reason=repr(exc),at=stamp()))
            report('SEARCH-BLOCKED','# SEARCH — BLOCKED\n\nCalibration 결과는 보존한다. 탐색 또는 holdout 단계 blocker: `'+repr(exc)+'`.\n\n다음 행동 두 가지: ① 원자료와 blocker를 검토한다. ② 별도 해소 결정 전 holdout·제출을 진행하지 않는다.\n')
    return result
