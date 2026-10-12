"""D3 runtime gate v2 measurement (Claude, 2026-09-25). Offline, local only, no submission.

Why a separate script (not tools/search_loop.py --manifest):
  * search_loop.verify_manifest only accepts workers 5/6 (WORKER_CONTRACT) -> workers 1 impossible.
  * controller.lock is held by the running loop -> CONTROLLER_ALREADY_RUNNING.
  * tools/dp_counterfactual.run_game loads agent source (get_last_callable) BEFORE timing,
    so step-0 cold start (compile+exec of main.py) was never measured. The engine charges it to step 0.
This script runs each game in a FRESH python process, one at a time (single worker),
and charges source load time to the candidate's first call, as the engine does.

'Cold' = fresh process only; the OS file cache may be warm, so true disk-cold hosted start is not reproduced.
Gate v2 (human approved 2026-09-25): single-worker max step < 0.8s (step 0 incl. cold start < 0.8s),
cumulative agent time / game < 30s, 0 exceptions/invalid. 6-worker load < 1.0s comes from stage1 (0.7506s).
Usage (Mac, repo root):  python3 experiments/d3_gate_v2/measure_gate_v2.py
"""
import hashlib, json, math, os, subprocess, sys, time, glob
sys.path += glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[:1]  # VM copy (Claude 09-30)
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CAND = os.environ.get('D3_CAND', 'releases/public-newmeta-127ed3e6-exact/main.py')
DP = 'releases/public-tetsutani-demand-preserving-0924-exact/main.py'
CAND_SHA = os.environ.get('D3_CAND_SHA', '127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652')
DP_SHA = '178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a'
RESULT_NAME = os.environ.get('D3_RESULT', 'result.json')
ENGINE_SHA = 'bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e'  # tools/dp_loss_cause.py (kaggriculture.py, engine 1.32.7)
# Handoff D3 list + top-12 slowest candidate max-step games from stage1-games.jsonl (seed, seat).
JOBS = sorted({(10198,0),(10198,1),(10062,1),(10119,0),(10118,0),(10118,1),(10117,0),(10117,1),(10200,0),
               (10407,1),(10237,0),(10124,0),(10222,0),(10210,0),(10194,0)})

def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def one(seed, seat):
    import time
    t0 = time.perf_counter()
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    engine_sha = hashlib.sha256(Path(K.__file__).read_bytes()).hexdigest()
    from kaggle_environments.agent import get_last_callable
    engine_import = time.perf_counter() - t0
    fns, load = [], []
    for p in (CAND, DP):
        s = time.perf_counter()
        fns.append(get_last_callable((ROOT/p).read_text(), path=str(ROOT/p)))  # compile+exec = engine step-0 cost
        load.append(time.perf_counter() - s)
    env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed})
    dur = [[], []]; exc = [[], []]
    def timed(i):
        def agent(obs, config):
            s = time.perf_counter()
            try: return fns[i](obs, config)
            except Exception as e: exc[i].append(repr(e)); raise
            finally:
                d = time.perf_counter() - s
                if not dur[i]: d += load[i]          # engine charges source load to first call
                dur[i].append(d)
        return agent
    agents = [None, None]; agents[seat] = timed(0); agents[1-seat] = timed(1)
    env.run(agents)
    last = env.steps[-1]
    return dict(seed=seed, seat=seat, engine_sha=engine_sha, engine_import=engine_import, load=load,
                statuses=[s.status for s in last], rewards=[s.reward for s in last], steps=len(env.steps),
                exceptions=exc,
                cand=dict(step0=dur[0][0], max=max(dur[0]), max_after0=max(dur[0][1:]),
                          p99=sorted(dur[0])[math.ceil(0.99*len(dur[0]))-1], total=sum(dur[0]), calls=len(dur[0]),
                          overage=sum(max(0, d-1.0) for d in dur[0])),
                dp=dict(step0=dur[1][0], mean_after0=sum(dur[1][1:])/max(1,len(dur[1])-1), max=max(dur[1]), total=sum(dur[1])))

def main():
    if len(sys.argv) == 3:
        print(json.dumps(one(int(sys.argv[1]), int(sys.argv[2])))); return
    assert sha(CAND) == CAND_SHA and sha(DP) == DP_SHA, 'SHA_MISMATCH'
    import kaggle_environments; ver = getattr(kaggle_environments, '__version__', '?')
    loop_state = None
    st = ROOT/'experiments/search_20260925/state.json'
    if st.exists(): loop_state = json.loads(st.read_text()).get('status')
    rows = []
    for seed, seat in JOBS:
        p = subprocess.run([sys.executable, __file__, str(seed), str(seat)], cwd=ROOT,
                           capture_output=True, text=True, timeout=1200,
                           env=dict(__import__('os').environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1'))
        if p.returncode: rows.append(dict(seed=seed, seat=seat, error=p.stderr[-1500:])); print('ERROR', seed, seat); continue
        r = json.loads(p.stdout.strip().splitlines()[-1]); rows.append(r)
        print(f"{seed}/{seat} step0={r['cand']['step0']:.3f}s max={r['cand']['max']:.3f}s max_after0={r['cand']['max_after0']:.3f}s total={r['cand']['total']:.2f}s", flush=True)
    ok = [r for r in rows if 'error' not in r]
    valid = [r for r in ok if r['steps']==720 and r['statuses']==['DONE','DONE'] and not any(r['exceptions'])]
    g = dict(
        max_step_incl_step0=max(r['cand']['max'] for r in ok),
        max_step0=max(r['cand']['step0'] for r in ok),
        max_step_after0=max(r['cand']['max_after0'] for r in ok),
        max_p99_step=max(r['cand']['p99'] for r in ok),
        max_total_per_game=max(r['cand']['total'] for r in ok),
        max_overage_per_game=max(r['cand']['overage'] for r in ok),
        errors_or_invalid=len(rows)-len(valid),
        dp_mean_step_after0=sum(r['dp']['mean_after0'] for r in ok)/len(ok))
    g['pass_single_max_lt_0_8'] = g['max_step_incl_step0'] < 0.8
    g['pass_step0_lt_0_8'] = g['max_step0'] < 0.8
    g['pass_total_lt_30'] = g['max_total_per_game'] < 30
    g['pass_no_error'] = g['errors_or_invalid'] == 0
    g['pass_engine_sha'] = {r['engine_sha'] for r in ok} == {ENGINE_SHA}
    # 6-worker load leg of D3 is NOT re-run here: taken from stage1-summary.json (1000 games, 6 workers).
    s1 = json.loads((ROOT/'experiments/search_20260925/stage1-summary.json').read_text())['runtime']
    g['stage1_6worker_max_step'] = s1['max_step']; g['stage1_6worker_invalid'] = s1['invalid']
    g['pass_6worker_lt_1_0'] = (s1.get('max_step') is not None and s1['max_step'] < 1.0 and s1['invalid'] == 0) if s1 else None
    g['tolerable_hosted_slowdown_to_1s'] = 1.0 / g['max_step_incl_step0']
    g['verdict'] = 'PASS' if all(g[k] for k in g if k.startswith('pass_')) else 'FAIL'
    res = dict(at=time.strftime('%Y-%m-%dT%H:%M:%S%z'), engine_version=ver, python=sys.version,
               cand_sha=CAND_SHA, dp_sha=DP_SHA, script_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               concurrent_loop_status=loop_state,
               note='If concurrent_loop_status==RUNNING, measurements are under extra load (conservative). A FAIL under load is not conclusive; rerun with loop paused.',
               gate=g, games=rows)
    (OUT/RESULT_NAME).write_text(json.dumps(res, indent=1))
    print(json.dumps(g, indent=1)); print('wrote', OUT/RESULT_NAME)

if __name__ == '__main__': main()
