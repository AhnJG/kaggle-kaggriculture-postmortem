"""Kaggle notebook pilot builder (Claude 2026-09-27). stdlib. Run from repo root:
python experiments/kaggle_pilot/make_pilot.py <kaggle_username>
Selects 60 EXP-030 screen jobs already finished on Mac, flattens every referenced file into
experiments/kaggle_pilot/dataset/ (flat names, no subfolders), writes jobs-pilot.json with flat names,
dataset-metadata.json (private) and kernel/kernel-metadata.json (private)."""
import json, hashlib, shutil, sys, pathlib
user = sys.argv[1]
R = pathlib.Path('experiments/kaggle_pilot'); D = R / 'dataset'; K = R / 'kernel'
if D.exists(): shutil.rmtree(D)
D.mkdir(parents=True); K.mkdir(exist_ok=True)
jobs = json.load(open('experiments/exp030_dpnew_bypass/jobs-screen.json'))
done = {json.loads(l)['key'] for l in open('experiments/exp030_dpnew_bypass/games-screen.jsonl')}
fin = sorted([j for j in jobs if f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' in done], key=lambda j: f'{j[0]}|{j[2]}|{j[4]}|{j[5]}')
assert len(fin) >= 60, len(fin)
step = len(fin) // 60; sel = fin[::step][:60]
flat = {}
def put(p):
    if p not in flat:
        b = open(p, 'rb').read(); n = 'f_' + hashlib.sha256(b).hexdigest()[:16] + '.py'
        (D / n).write_bytes(b); flat[p] = n
    return flat[p]
pj = [[v, put(p), o, put(op), s, t] for v, p, o, op, s, t in sel]
shutil.copy('experiments/exp024_round2/run.py', D / 'run_exp024.py')
json.dump(pj, open(D / 'jobs-pilot.json', 'w'))
json.dump({'jobs_sha': hashlib.sha256(json.dumps(sel).encode()).hexdigest(), 'map': flat}, open(R / 'pilot-map.json', 'w'), indent=1)
json.dump({'title': 'kaggriculture-pilot-0927', 'id': f'{user}/kaggriculture-pilot-0927',
           'licenses': [{'name': 'other'}]}, open(D / 'dataset-metadata.json', 'w'), indent=1)
json.dump({'id': f'{user}/kaggriculture-pilot-0927-run', 'title': 'kaggriculture-pilot-0927-run',
           'code_file': 'pilot_kernel.py', 'language': 'python', 'kernel_type': 'script',
           'is_private': True, 'enable_gpu': False, 'enable_tpu': False, 'enable_internet': True,
           'dataset_sources': [f'{user}/kaggriculture-pilot-0927'], 'competition_sources': [],
           'kernel_sources': []}, open(K / 'kernel-metadata.json', 'w'), indent=1)
print('jobs', len(pj), 'files', len(flat), 'agents', sorted({j[0] for j in pj}), 'opps', sorted({j[2] for j in pj}))
