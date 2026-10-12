#!/usr/bin/env python3
"""Offline, restartable frozen-batch executor for SEARCH-20260925.

One controller owns the journal. Completed games are durable before state updates;
state is derived from the journal, never used as evidence of a completed game.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import contextlib
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import resource
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/search_20260925'
THREAD_ENV = {k: '1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')}


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name+'.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
        d = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(d)
        finally: os.close(d)
    finally:
        if os.path.exists(name): os.unlink(name)


def read_journal(path):
    """Recover only a torn final append. Any corruption in a committed line blocks."""
    path = Path(path)
    if not path.exists(): return {}
    data = path.read_bytes(); rows = {}; offset = 0
    lines = data.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if not line.endswith(b'\n'):
            if i != len(lines)-1: raise RuntimeError('CORRUPT_JOURNAL')
            backup = path.with_name(path.name+'.torn-'+str(time.time_ns()))
            backup.write_bytes(line)
            with path.open('r+b') as f: f.truncate(offset); f.flush(); os.fsync(f.fileno())
            break
        row = json.loads(line)
        key = row['key']
        if key in rows: raise RuntimeError('DUPLICATE_GAME_KEY '+key)
        rows[key] = row; offset += len(line)
    return rows


def append_game(path, row):
    with Path(path).open('a') as f:
        f.write(json.dumps(row, ensure_ascii=False, allow_nan=False)+'\n')
        f.flush(); os.fsync(f.fileno())


def job_key(job):
    # The variant id includes the batch scope (runtime/direct/panel/calibration).
    return '|'.join(str(job[x]) for x in ('variant','seed','seat','opponent_sha256'))


def verify_manifest(manifest):
    if manifest['workers'] not in (5,6): raise RuntimeError('WORKER_CONTRACT')
    keys = set()
    for path, expected in manifest['sha256'].items():
        if sha(ROOT/path) != expected: raise RuntimeError('SHA_MISMATCH '+path)
    for job in manifest['jobs']:
        key = job_key(job)
        if key in keys: raise RuntimeError('DUPLICATE_MANIFEST_KEY '+key)
        keys.add(key)
        for field in ('path','opponent'):
            expected = job['sha256' if field=='path' else 'opponent_sha256']
            if manifest['sha256'].get(job[field]) != expected: raise RuntimeError('UNFROZEN_INPUT '+job[field])
        if 9000 <= job['seed'] <= 9599 and not manifest.get('holdout_checkpoint'):
            raise RuntimeError('HOLDOUT_SEED_LEAK')
    if manifest.get('holdout_checkpoint'):
        raise RuntimeError('HOLDOUT_REQUIRES_FROZEN_METRIC_AND_CHECKPOINT: not enabled before calibration')


def worker(job):
    os.environ.update(THREAD_ENV)
    sys.path.insert(0, str(ROOT/'tools'))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        from dp_counterfactual import run_game
        from dp_loss_cause import read_raw
        replay = read_raw(job['episode']) if 'episode' in job else None
        for field in ('path','opponent'):
            expected = job['sha256' if field=='path' else 'opponent_sha256']
            if sha(ROOT/job[field]) != expected: raise RuntimeError('WORKER_SHA_MISMATCH')
        result = run_game(ROOT/job['path'], ROOT/job['opponent'], job['seed'], job['seat'],
                          replay=replay, verify_identity=job.get('verify_identity',False))
    result['worker_peak_rss_bytes'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform != 'darwin': result['worker_peak_rss_bytes'] *= 1024
    return result


def execute(job):
    started = stamp(); start = time.monotonic()
    env = dict(os.environ, **THREAD_ENV)
    proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker', json.dumps(job)],
                          cwd=ROOT, env=env, capture_output=True, text=True, timeout=1200)
    if proc.returncode:
        raise RuntimeError('WORKER_FAILED '+job_key(job)+' '+proc.stderr[-2000:])
    result = json.loads(proc.stdout)
    return dict(key=job_key(job), job=job, started_at=started, completed_at=stamp(),
                process_seconds=time.monotonic()-start, result=result)


def valid(result):
    return (result['steps']==720 and result['statuses']==['DONE','DONE'] and
            not any(result['exceptions']) and not result['caught_errors'])


def run(manifest_path):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT/'controller.lock').open('a') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: raise RuntimeError('CONTROLLER_ALREADY_RUNNING')
        manifest = json.loads(manifest_path.read_text()); verify_manifest(manifest)
        manifest_sha = sha(manifest_path)
        runner_sha = sha(__file__)
        rows = read_journal(OUT/'games.jsonl')
        jobs = manifest['jobs']; pending = [j for j in jobs if job_key(j) not in rows]
        for j in jobs:
            old = rows.get(job_key(j))
            if old and (old['manifest_sha256'] != manifest_sha or old['job'] != j):
                raise RuntimeError('RESUME_IDENTITY_MISMATCH '+job_key(j))
        print(json.dumps(dict(event='resume',at=stamp(),batch=manifest['id'],skipped=len(jobs)-len(pending),remaining=len(pending))),flush=True)
        state = dict(batch=manifest['id'],manifest_sha256=manifest_sha,runner_sha256=runner_sha,
                     status='RUNNING',resumed_at=stamp(),workers=manifest['workers'],total=len(jobs))
        def persist():
            state.update(updated_at=stamp(),completed=sum(job_key(j) in rows for j in jobs))
            atomic(OUT/'state.json',state)
        persist()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=manifest['workers']) as pool:
                iterator = iter(pending); active = {}
                for _ in range(manifest['workers']):
                    j=next(iterator,None)
                    if j is not None: active[pool.submit(execute,j)] = j
                while active:
                    done,_ = concurrent.futures.wait(active,return_when=concurrent.futures.FIRST_COMPLETED)
                    for future in done:
                        job=active.pop(future); row=future.result()
                        row.update(manifest_sha256=manifest_sha,runner_sha256=runner_sha)
                        append_game(OUT/'games.jsonl',row);rows[row['key']]=row;persist()
                        print(json.dumps(dict(event='game',at=stamp(),completed=state['completed'],total=len(jobs),key=row['key'],valid=valid(row['result']),seconds=row['process_seconds'])),flush=True)
                        if row['result']['worker_peak_rss_bytes']*manifest['workers'] > 24*1024**3*.7:
                            raise RuntimeError('BLOCKED_MEMORY_BUDGET')
                        j=next(iterator,None)
                        if j is not None: active[pool.submit(execute,j)] = j
            state['status']='COMPLETE';persist()
        except BaseException as exc:
            state.update(status='BLOCKED',error=repr(exc));persist();raise


def launch_template():
    # User installs this template; no writes to ~/Library or sleep settings here.
    value=dict(Label='com.sian.searchloop',ProgramArguments=[str(Path(sys.executable).resolve()),str(Path(__file__).resolve()),'--queue'],
               WorkingDirectory=str(ROOT),RunAtLoad=True,KeepAlive=True,ThrottleInterval=60,
               EnvironmentVariables=THREAD_ENV,StandardOutPath=str(OUT/'launchd.stdout.log'),StandardErrorPath=str(OUT/'launchd.stderr.log'))
    (OUT/'com.sian.searchloop.plist').write_bytes(plistlib.dumps(value))


def queue():
    # Idle after terminal states; KeepAlive must not spin/re-run a used checkpoint.
    while True:
        qpath=OUT/'queue.json'
        if qpath.exists():
            q=json.loads(qpath.read_text())
            for item in q.get('batches',[]):
                path=ROOT/item
                donepath=OUT/('batch-'+path.stem+'.done.json')
                if donepath.exists():
                    if json.loads(donepath.read_text())['manifest_sha256'] != sha(path):
                        raise RuntimeError('COMPLETED_BATCH_CHANGED')
                    continue
                run(path)
                atomic(donepath,dict(manifest_sha256=sha(path),completed_at=stamp()))
        time.sleep(30)


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path)
    ap.add_argument('--worker')
    ap.add_argument('--queue',action='store_true')
    ap.add_argument('--launch-template',action='store_true')
    a=ap.parse_args()
    if a.worker:
        print(json.dumps(worker(json.loads(a.worker)),allow_nan=False))
    elif a.launch_template: launch_template()
    elif a.queue: queue()
    elif a.manifest: run(a.manifest.resolve())
    else: ap.error('choose --manifest, --queue or --launch-template')
