# Kaggriculture local-eval pilot (private). Reproduces 60 Mac games; aborts on engine mismatch.
import subprocess, sys, os, glob, shutil, json, hashlib, time, platform
t0 = time.time()
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'kaggle-environments==1.32.7'], check=True)
import kaggle_environments
eng = glob.glob(os.path.join(os.path.dirname(kaggle_environments.__file__), 'envs', 'kaggriculture', 'kaggriculture.py'))[0]
esha = hashlib.sha256(open(eng, 'rb').read()).hexdigest()
meta = {'engine_version': kaggle_environments.__version__, 'engine_sha': esha, 'cpu_count': os.cpu_count(),
        'python': platform.python_version()}
json.dump(meta, open('/kaggle/working/meta.json', 'w'))
print(meta, flush=True)
assert esha.startswith('bc8a5487'), 'ENGINE_MISMATCH'
src = [p for p in glob.glob('/kaggle/input/**/jobs-pilot.json', recursive=True)][0]
W = '/kaggle/working/run'; os.makedirs(W, exist_ok=True)
for f in glob.glob(os.path.join(os.path.dirname(src), '*')):
    shutil.copy(f, W)
os.chdir(W)
sys.path.insert(0, W)
import run_exp024 as R
from multiprocessing import Pool
jobs = [tuple(j) for j in json.load(open('jobs-pilot.json'))]
t1 = time.time()
with Pool(os.cpu_count()) as pool, open('/kaggle/working/games-pilot.jsonl', 'w') as out:
    for r in pool.imap_unordered(R.play, jobs):
        out.write(json.dumps(r) + '\n'); out.flush()
meta.update({'games': len(jobs), 'game_wall_sec': round(time.time() - t1, 1), 'total_sec': round(time.time() - t0, 1)})
json.dump(meta, open('/kaggle/working/meta.json', 'w'))
print('DONE', meta, flush=True)
