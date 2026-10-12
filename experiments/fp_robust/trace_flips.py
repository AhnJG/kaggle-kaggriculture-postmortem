"""Development-only timing diagnosis; does not touch frozen holdout."""
import contextlib
import io
import json
from multiprocessing import Pool
from pathlib import Path

from kaggle_environments import make
from kaggle_environments.agent import get_last_callable

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
EPS = ['114272897','114264845','114262013','114260441','114255769',
       '114254546','114185274','114688502']
META = {r['episode']: r for r in json.loads((ROOT/'experiments/exp051_curpop/meta.json').read_text())}

def run(task):
    ep, vid = task
    row = META[ep]
    path = ROOT / ('releases/exp039-c26/main.py' if vid == 'c26'
                   else 'experiments/fp_robust/variant_a_v2.py')
    rival = ROOT / f'experiments/exp051_curpop/tapes/C{ep}.py'
    with contextlib.redirect_stdout(io.StringIO()):
        me = get_last_callable(path.read_text(), path=str(path))
        opp = get_last_callable(rival.read_text(), path=str(rival))
        actions = []
        def wrapped(obs, config):
            action = me(obs, config)
            actions.append(action)
            return action
        env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': int(row['seed'])})
        seat = int(row['seat'])
        env.run([wrapped,opp] if seat == 0 else [opp,wrapped])
    return ep, vid, actions

if __name__ == '__main__':
    tasks = [(ep, vid) for ep in EPS for vid in ('a','c26')]
    with Pool(4) as pool:
        records = {(ep, vid): actions for ep,vid,actions in pool.map(run,tasks)}
    out = {}
    for ep in EPS:
        aa, bb = records[(ep,'a')],records[(ep,'c26')]
        changed = [i for i,(a,b) in enumerate(zip(aa,bb)) if a != b]
        out[ep] = {'first': changed[:12], 'last': changed[-12:],
                   'n_changed_steps': len(changed),
                   'before576': sum(i < 576 for i in changed),
                   'after576': sum(i >= 576 for i in changed)}
    (OUT/'flip_timing.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
