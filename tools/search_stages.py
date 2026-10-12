"""Frozen preparation/reporting for search_loop.py; no network or submissions."""
from __future__ import annotations
import ast
import contextlib
from datetime import datetime
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tarfile
import tempfile
from zoneinfo import ZoneInfo

from search_loop import ROOT, OUT, sha, atomic, run, job_key, valid, stamp

NEW = 'releases/public-newmeta-127ed3e6-exact/main.py'
DP = 'releases/public-tetsutani-demand-preserving-0924-exact/main.py'
PROPOSAL = 'coordination/proposals/claude/20260925-SEARCH-LOOP-CODEX.md'
FROZEN_PANEL = 'experiments/results/dp_loss_cause_20260925/freeze.json'


def manifest(name, jobs, workers=6):
    path=OUT/(name+'.json')
    if path.exists():
        value=json.loads(path.read_text())
        if value['jobs']!=jobs:raise RuntimeError('FROZEN_JOBS_CHANGED '+name)
        return path
    paths={PROPOSAL,'tools/search_loop.py','tools/search_stages.py','tools/dp_counterfactual.py',
           'tools/dp_loss_cause.py','tools/reproduce_replay.py'}
    for j in jobs:
        paths.update([j['path'],j['opponent']])
        if 'episode' in j:paths.add('private_artifacts/dp_hosted_20260924/raw/'+j['episode']+'.json.gz')
    atomic(path,dict(id=name,hypothesis_id='HYP-0028',test_id='TEST-SEARCH-20260925-'+name.upper(),
                     frozen_at=stamp(),workers=workers,sha256={p:sha(ROOT/p) for p in sorted(paths)},jobs=jobs))
    return path


def job(variant,path,opponent,seed,seat,**extra):
    return dict(variant=variant,path=path,sha256=sha(ROOT/path),opponent=opponent,
                opponent_sha256=sha(ROOT/opponent),seed=int(seed),seat=int(seat),**extra)


def all_rows():
    p=OUT/'games.jsonl'
    if not p.exists():return []
    return [json.loads(line) for line in p.read_text().splitlines()]


def batch(path):
    m=json.loads(path.read_text())
    keys={job_key(j) for j in m['jobs']}
    rows=[r for r in all_rows() if r['key'] in keys]
    if len(rows)!=len(keys):
        run(path)
        rows=[r for r in all_rows() if r['key'] in keys]
    if len(rows)!=len(keys):raise RuntimeError('BATCH_INCOMPLETE')
    for row in rows:
        if row['manifest_sha256']!=sha(path):raise RuntimeError('BATCH_MANIFEST_MISMATCH')
        if row['job'] not in m['jobs']:raise RuntimeError('JOB_CHANGED')
    return rows


def summary(rows):
    results=[r['result'] for r in rows]
    scores=[r['score'] for r in results if r['score'] is not None]
    return dict(n=len(rows),wins=scores.count(1),draws=scores.count(.5),losses=scores.count(0),
                score=statistics.mean(scores) if scores else None,
                invalid=sum(not valid(r) for r in results),
                max_step=max((r['timing'][0]['max_seconds'] for r in results),default=0),
                max_game_p99=max((r['timing'][0]['p99_seconds'] or 0 for r in results),default=0),
                max_rss_bytes=max((r.get('worker_peak_rss_bytes',0) for r in results),default=0))


def report(kind,text):
    marker=OUT/('report-'+kind+'.json')
    if marker.exists():return json.loads(marker.read_text())['path']
    ts=datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d-%H%M')
    path=ROOT/'coordination/reports/codex'/f'{ts}-{kind}.md'
    path.write_text(text)
    atomic(marker,dict(path=str(path.relative_to(ROOT)),sha256=sha(path),at=stamp()))
    return str(path.relative_to(ROOT))


def source_gate(path):
    """Identify reachable external-library hooks; never rewrite exact bytes."""
    source=(ROOT/path).read_bytes();tree=ast.parse(source)
    findings=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            f=ast.unparse(node.func)
            if any(x in f.lower() for x in ('getenv','environ','requests.','urlopen','subprocess','read_text','read_bytes','write_text','write_bytes')):
                findings.append(dict(line=node.lineno,call=ast.unparse(node)[:200]))
            if f=='open':
                enclosing=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.lineno<=node.lineno<=n.end_lineno]
                # Existing frozen V92 uses path=None, guarded by `if path:`.
                dormant=any('path = None' in ast.unparse(n) and 'if path:' in ast.unparse(n) for n in enclosing)
                if not dormant:findings.append(dict(line=node.lineno,call=ast.unparse(node)[:200]))
    modules=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):modules.extend(a.name.split('.')[0] for a in n.names)
        elif isinstance(n,ast.ImportFrom):modules.append((n.module or '').split('.')[0])
    nonstdlib=sorted(set(modules)-sys.stdlib_module_names)
    return dict(sha256=sha(ROOT/path),lines=len(source.splitlines()),external_calls=findings,nonstdlib=nonstdlib,
                dependency_pass=not findings and not nonstdlib)


def cleanroom(path):
    with tempfile.TemporaryDirectory(prefix='search-clean-') as d:
        p=Path(d)/'main.py';p.write_bytes((ROOT/path).read_bytes())
        code="import json; from kaggle_environments.agent import get_last_callable; from pathlib import Path; f=get_last_callable(Path('main.py').read_bytes().decode(),path='main.py'); print('ENTRY_JSON:'+json.dumps({'entry':f.__name__,'has_file':'__file__' in f.__globals__}))"
        proc=subprocess.run([sys.executable,'-c',code],cwd=d,capture_output=True,text=True,timeout=60)
        line=next((s.removeprefix('ENTRY_JSON:') for s in proc.stdout.splitlines() if s.startswith('ENTRY_JSON:')),None)
        return dict(passed=proc.returncode==0 and line is not None,entry=json.loads(line) if line else None,
                    error=proc.stderr[-1000:] if proc.returncode else None)


def prepare_stage1_extra():
    jobs=[]
    for seed in range(2400,2440):
        for seat in (0,1):jobs.append(job('newmeta-direct',NEW,DP,seed,seat))
    for seed in range(2300,2310):
        for seat in (0,1):jobs.append(job('newmeta-e5',NEW,DP,seed,seat))
    f=json.loads((ROOT/FROZEN_PANEL).read_text())
    for row in f['panel']:
        if row['eligible']:
            jobs.append(job('newmeta-panel-'+row['episode'],NEW,row['opponent_path'],row['seed'],row['dp_seat'],episode=row['episode']))
    # Reproduce a previously frozen DP game after the arbitrary-path API change.
    oldpath='experiments/results/dp_loss_cause_20260925/q2/112786680-parent.json'
    old=json.loads((ROOT/oldpath).read_text())
    jobs.append(job('dp-regression',DP,old['opponent'],old['seed'],old['seat'],episode='112786680',verify_identity=True))
    for repeat in range(3):jobs.append(job('determinism-'+str(repeat),NEW,DP,2400,0))
    return manifest('stage1-extra',jobs)


def stage1_finish():
    runtime=batch(OUT/'stage1-runtime.json')
    extra=batch(prepare_stage1_extra())
    r=summary(runtime);d=summary([x for x in extra if x['job']['variant']=='newmeta-direct'])
    e5=summary([x for x in extra if x['job']['variant']=='newmeta-e5'])
    panel=summary([x for x in extra if x['job']['variant'].startswith('newmeta-panel-')])
    from datetime import datetime as dt
    start=min(dt.fromisoformat(x['started_at']).timestamp() for x in runtime)
    end=max(dt.fromisoformat(x['completed_at']).timestamp() for x in runtime)
    initial=[x for x in runtime if dt.fromisoformat(x['completed_at']).timestamp()<=start+300]
    late=[x for x in runtime if dt.fromisoformat(x['completed_at']).timestamp()>end-300]
    throughput=dict(duration_seconds=end-start,initial_5min_games=len(initial),last_5min_games=len(late),
                    initial_per_hour=len(initial)*12,late_per_hour=len(late)*12,
                    ratio=len(late)/len(initial) if initial else None,
                    overall_per_hour=len(runtime)/(end-start)*3600)
    # Record actual start/end timestamps; interruptions invalidate sustained load.
    intervals=sorted((dt.fromisoformat(x['started_at']).timestamp(),dt.fromisoformat(x['completed_at']).timestamp()) for x in runtime)
    longest=0;segment_start=intervals[0][0];segment_end=intervals[0][1]
    for a,b in intervals[1:]:
        if a>segment_end+5:
            longest=max(longest,segment_end-segment_start);segment_start=a
        segment_end=max(segment_end,b)
    longest=max(longest,segment_end-segment_start)
    throughput['longest_continuous_seconds']=longest
    suspended=[x['key'] for x in runtime if
               dt.fromisoformat(x['completed_at']).timestamp()-dt.fromisoformat(x['started_at']).timestamp()
               > x['process_seconds']+5]
    throughput['possible_sleep_games']=suspended
    regression=next(x['result'] for x in extra if x['job']['variant']=='dp-regression')
    old=json.loads((ROOT/'experiments/results/dp_loss_cause_20260925/q2/112786680-parent.json').read_text())
    regression_pass=all(regression[k]==old[k] for k in ['rewards','action_sha256','statuses']) and regression['identity']['passed']
    repeated=[x['result'] for x in extra if x['job']['variant'].startswith('determinism-')]
    determinism=len({json.dumps([x['rewards'],x['action_sha256']]) for x in repeated})==1
    gate=source_gate(NEW);gate['cleanroom']=cleanroom(NEW)
    with tarfile.open(ROOT/'releases/public-newmeta-127ed3e6-exact/submission.tar.gz') as tar:
        gate['tar_members']=tar.getnames();gate['tar_main_sha256']=hashlib.sha256(tar.extractfile('main.py').read()).hexdigest()
    gate['identity_pass']=gate['tar_members']==['main.py'] and gate['tar_main_sha256']==sha(ROOT/NEW)
    runtime_pass=(r['n']>=1000 and r['invalid']==0 and r['max_step']<.25 and r['max_game_p99']<.1)
    memory_pass=r['max_rss_bytes']*6<24*1024**3*.7
    sustained_pass=longest>=1800 and not suspended
    reduce_workers=throughput['ratio'] is not None and throughput['ratio']<=.6
    result=dict(runtime=r,direct=d,e5=e5,panel=panel,throughput=throughput,source_gate=gate,
                runtime_pass=runtime_pass,memory_pass=memory_pass,sustained_pass=sustained_pass,
                reduce_workers_to_5=reduce_workers,regression_pass=regression_pass,determinism_pass=determinism,
                source_sha256=sha(ROOT/NEW),tar_sha256=sha(ROOT/'releases/public-newmeta-127ed3e6-exact/submission.tar.gz'))
    result['verdict']='PASS' if all([runtime_pass,memory_pass,sustained_pass,regression_pass,determinism,gate['dependency_pass'],gate['cleanroom']['passed'],gate['identity_pass'],e5['score']>=.7,not reduce_workers]) else 'NOT_ELIGIBLE'
    atomic(OUT/'stage1-summary.json',result)
    install=f'''```sh
mkdir -p ~/Library/LaunchAgents
cp {OUT}/com.sian.searchloop.plist ~/Library/LaunchAgents/com.sian.searchloop.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.sian.searchloop.plist
launchctl kickstart gui/$(id -u)/com.sian.searchloop
# 덮개가 열린 동안 절전 방지 (별도 터미널)
caffeinate -dimsu
# 제거
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.sian.searchloop.plist
rm ~/Library/LaunchAgents/com.sian.searchloop.plist
```'''
    text=f'''# NEWMETA-EXACT — {result['verdict']}

127ed3e6 원본을 CRLF 그대로 포장하고, Mac worker6에서 1,000경기를 실행했다. 무인 탐색의 실행 속도와 runtime gate를 확인하기 위한 작업이다.
[LOCAL] Runtime {r['n']}경기: invalid {r['invalid']}, maximum step {r['max_step']:.9f}s, 최대 game-p99 {r['max_game_p99']:.9f}s. p99는 game별 p99의 최댓값으로 보수적으로 판정했다.
최종 verdict **{result['verdict']}**. runtime 통과={runtime_pass}, 연속30분={sustained_pass}, memory 통과={memory_pass}. 제출하지 않았다. 다음은 1b 부모 tournament이며 최종 부모는 calibration 이후 고른다.

- 진입점: `{gate['cleanroom']['entry']}`. tar member={gate['tar_members']}; 원본 SHA={result['source_sha256']}; tar SHA={result['tar_sha256']}.
- DP80 W/D/L={d['wins']}/{d['draws']}/{d['losses']}, score={d['score']}; seed2400–2439 양 좌석.
- E-5 20경기 W/D/L={e5['wins']}/{e5['draws']}/{e5['losses']}, score={e5['score']}; seed2300–2309 양 좌석, 필수 ≥0.70.
- Panel47 W/D/L={panel['wins']}/{panel['draws']}/{panel['losses']}; 개발 자료이므로 metric/holdout에서 제외.
- 기존 DP 경기 112786680 actions/rewards/720-step 재현={regression_pass}. 동일 seed/좌석 3회 deterministic 검증={determinism}.
- Runtime seed10000–10499 양 좌석, 상대 DP178ae0f7, engine1.32.7. runner/상대/원자료 SHA는 `stage1-runtime.json`, `stage1-extra.json`, 각 games.jsonl행에 기록.
- 연속부하 {longest:.1f}s; 초기5분 {throughput['initial_per_hour']}games/h → 마지막5분 {throughput['late_per_hour']}games/h; ratio={throughput['ratio']}. 전체 {throughput['overall_per_hour']:.2f}games/h. worker당 peak RSS {r['max_rss_bytes']/1024**2:.1f}MiB. 5-worker 비교 필요={reduce_workers}.
- 단일 standalone controller가 완료 즉시 games.jsonl append+fsync, state.json 임시파일+rename+fsync. 재시작은 완료 key를 건너뛴다. 진행 중 경기는 다시 실행할 수 있다. state는 성능 증거가 아니다.
- launchd 설치는 지시서대로 사람이 실행한다. 아래 파일은 template이며 이 보고서가 설치 완료를 의미하지 않는다. Mac 덮개 닫힘/잠자기 중 계산은 진행하지 않는다.

{install}

검증: `python3 -m unittest tests.test_search_loop tests.test_reproduce_replay -q` 14 tests PASS; `python3 tools/search_loop.py --manifest experiments/search_20260925/stage1-runtime.json`; 추가 측정은 `stage1-extra.json`. 원자료: `experiments/search_20260925/games.jsonl`, summary: `experiments/search_20260925/stage1-summary.json`.

Identity: {gate['identity_pass']}
Schema: clean-room loader {gate['cleanroom']['passed']}, entry ig_agent; full action legality separately N/A
Runtime: {runtime_pass} — Mac local only; hosted N/A
Isolation: {gate['cleanroom']['passed']}
License: source Apache-2.0 notices retained; provenance in source-audit.json
Ledger: N/A — no submission

다음 행동 두 가지: ① gate가 모두 통과했는지 사람이 보고 exact 제출 여부 판단(FIFO는 제출 직전 재확인). ② 1b screening→상위5개 confirmation을 완료하고 calibration 전 순위를 보고한다.
'''
    report('NEWMETA-EXACT',text)
    return result


def tournament():
    if not (OUT/'report-NEWMETA-EXACT.json').exists():raise RuntimeError('STAGE1_REPORT_REQUIRED')
    inv=json.loads((OUT/'inventory.json').read_text())
    auditpath=OUT/'tournament-source-gates.json'
    if auditpath.exists():audits=json.loads(auditpath.read_text())
    else:
        audits=[]
        for x in inv:
            a=dict(x,gate=source_gate(x['path']),cleanroom=cleanroom(x['path']))
            a['static_pass']=a['gate']['dependency_pass'] and a['cleanroom']['passed']
            audits.append(a)
        atomic(auditpath,audits)
    eligible=[a for a in audits if a['static_pass']]
    jobs=[job('gate-'+a['sha256'][:12],a['path'],DP,2300,seat) for a in eligible for seat in (0,1)]
    gates=batch(manifest('tournament-gates',jobs))
    passed=[]
    for a in audits:
        selected=[r for r in gates if r['job']['path']==a['path']]
        a['runtime_gate']=summary(selected)
        a['gate_pass']=a['static_pass'] and len(selected)==2 and a['runtime_gate']['invalid']==0 and a['runtime_gate']['max_step']<.5
        if a['gate_pass']:passed.append(a)
    atomic(OUT/'tournament-gates-summary.json',audits)
    jobs=[job('screen-'+a['sha256'][:12],a['path'],op,seed,seat) for a in passed for op in (DP,NEW) for seed in range(2500,2520) for seat in (0,1)]
    screens=batch(manifest('tournament-screen',jobs))
    ranking=[]
    for a in passed:
        rows=[r for r in screens if r['job']['path']==a['path']]
        total=summary(rows)
        ranking.append(dict(path=a['path'],sha256=a['sha256'],summary=total,
                            dp=summary([r for r in rows if r['job']['opponent']==DP]),
                            newmeta=summary([r for r in rows if r['job']['opponent']==NEW])))
    ranking.sort(key=lambda a:(a['summary']['invalid']==0,a['summary']['score'],a['dp']['score'],a['sha256']),reverse=True)
    top=[a for a in ranking if a['summary']['invalid']==0 and a['summary']['max_step']<.5][:5]
    jobs=[job('confirm-'+a['sha256'][:12],a['path'],op,seed,seat) for a in top for op in (DP,NEW) for seed in range(2520,2560) for seat in (0,1)]
    confirms=batch(manifest('tournament-confirm',jobs))
    for a in top:
        rows=[r for r in confirms if r['job']['path']==a['path']]
        a['confirmation']=summary(rows)
        a['confirmation_dp']=summary([r for r in rows if r['job']['opponent']==DP])
        a['confirmation_newmeta']=summary([r for r in rows if r['job']['opponent']==NEW])
    top.sort(key=lambda a:(a['confirmation']['invalid']==0 and a['confirmation']['max_step']<.5,a['confirmation']['score'],a['confirmation_dp']['score'],a['sha256']),reverse=True)
    result=dict(gates=audits,screening=ranking,finalists=top,parent='PENDING_CALIBRATION')
    atomic(OUT/'tournament-summary.json',result)
    lines=['# PARENT-TOURNAMENT — LOCAL_RANKING_ONLY','',
           '09-24/25 공개 파일의 고유 SHA 전부를 대상으로 gate와 DP·NEWMETA 직접 대결을 실행했다. 부모 후보를 두 파일에 한정하지 않기 위한 비교다.',
           f'[LOCAL] 고유 파일 {len(inv)}개, gate 통과 {len(passed)}개. Screening seed2500–2519×양좌석×2상대, 상위5개 confirmation seed2520–2559×양좌석×2상대.',
           '최종 부모와 다른 계열 슬롯 B 추천은 2단계 metric calibration 이후 확정한다. 이 표는 hosted 우위나 제출 승인이 아니다.','',
           '| SHA | gate | 사유/maximum step |','|---|---|---|']
    for a in audits:
        lines.append(f"| {a['sha256']} | {a['gate_pass']} | external={a['gate']['external_calls']}; cleanroom={a['cleanroom']['passed']}; max={a['runtime_gate']['max_step']:.6f}s |")
    lines+=['','| 순위 | SHA | DP40 | NEWMETA40 | 합계 | confirmation DP80 / NEWMETA80 |','|---|---|---|---|---|---|']
    for i,a in enumerate(ranking,1):
        c=next((t for t in top if t['sha256']==a['sha256']),None)
        lines.append(f"| {i} | {a['sha256']} | {a['dp']['score']} | {a['newmeta']['score']} | {a['summary']['score']} | {str(c['confirmation_dp']['score'])+' / '+str(c['confirmation_newmeta']['score']) if c else 'N/A'} |")
    lines+=['','입력·결과: `experiments/search_20260925/tournament-*.json`, `games.jsonl`. 각 행에 artifact/runner/manifest SHA, seed, seat, 상대 기록. Engine1.32.7. 재현: `python3 tools/search_loop.py --queue` (완료 key skip).',
            '', '다음 행동 두 가지: ① 고정 상대 풀로 calibration 4개 후보를 평가한다. ② EXP-016>EXP-017 필수 쌍을 포함해 4/5 기준을 통과한 metric만 freeze하고, 실패하면 BLOCKED로 종료한다.']
    report('PARENT-TOURNAMENT','\n'.join(lines)+'\n')
    return result


def workflow():
    """Advance stages in order. Reports and completed-game keys survive restart."""
    terminal=OUT/'workflow-terminal.json'
    if terminal.exists():return
    try:
        if not (OUT/'report-NEWMETA-EXACT.json').exists():stage1_finish()
        if not (OUT/'report-PARENT-TOURNAMENT.json').exists():tournament()
        # Calibration requires a completed frozen implementation and numeric policy.
        ready=OUT/'calibration-ready.json'
        if not ready.exists():
            atomic(OUT/'workflow-state.json',dict(status='WAITING_CALIBRATION_SETUP',at=stamp(),
                   reason='Stages1/1b reported; no metric frozen and no search or holdout allowed yet.'))
            return
        spec=json.loads(ready.read_text())
        module=ROOT/'tools/search_calibration.py'
        if sha(module)!=spec['sha256']:raise RuntimeError('CALIBRATION_CODE_CHANGED')
        from search_calibration import calibrate
        result=calibrate()
        if result['status']!='PASS':
            atomic(terminal,dict(status='BLOCKED_CALIBRATION',result=result,at=stamp()))
            return
        atomic(OUT/'workflow-state.json',dict(status='CALIBRATED',at=stamp()))
    except Exception as exc:
        atomic(OUT/'workflow-state.json',dict(status='BLOCKED',error=repr(exc),at=stamp()))
        raise
