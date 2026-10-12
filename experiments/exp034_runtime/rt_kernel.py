# EXP-034 runtime probe (private). Sequential games, per-step wall time of OUR agent; hosted actTimeout=1s, overage 60s/game.
import subprocess, sys, os, glob, shutil, json, hashlib, time, io, contextlib
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'kaggle-environments==1.32.7'], check=True)
import kaggle_environments
eng = glob.glob(os.path.join(os.path.dirname(kaggle_environments.__file__), 'envs', 'kaggriculture', 'kaggriculture.py'))[0]
assert hashlib.sha256(open(eng, 'rb').read()).hexdigest().startswith('bc8a5487'), 'ENGINE_MISMATCH'
src = glob.glob('/kaggle/input/**/jobs-0.json', recursive=True)[0]
W = '/kaggle/working/run'; os.makedirs(W, exist_ok=True)
for f in glob.glob(os.path.join(os.path.dirname(src), '*')): shutil.copy(f, W)
os.chdir(W)
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable
out = open('/kaggle/working/rt.jsonl', 'w')
for vid, path, oid, opath, seed, seat in json.load(open('jobs-0.json')):
    with contextlib.redirect_stdout(io.StringIO()):
        t0 = time.perf_counter(); me = get_last_callable(open(path).read(), path=path); load = time.perf_counter() - t0
        op = get_last_callable(open(opath).read(), path=opath)
        ts = []
        def A(obs, cfg):
            s = time.perf_counter(); a = me(obs, cfg); ts.append(time.perf_counter() - s); return a
        env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed})
        env.run([A, op] if seat == 0 else [op, A])
    rw = [s.reward for s in env.steps[-1]]
    r = dict(vid=vid, opp=oid, seed=seed, seat=seat, load=round(load, 3), step0=round(ts[0], 3), max=round(max(ts), 3),
             n_over1=sum(t > 1.0 for t in ts), overage=round(sum(max(0, t - 1.0) for t in ts), 3), total=round(sum(ts), 2),
             statuses=[s.status for s in env.steps[-1]], rewards=rw)
    out.write(json.dumps(r) + '\n'); out.flush(); print(r, flush=True)
