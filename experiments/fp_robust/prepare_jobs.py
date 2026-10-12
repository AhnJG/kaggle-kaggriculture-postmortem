"""Prepare immutable jobs from the preregistered episode/time split."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
freeze = json.loads((OUT / 'freeze.json').read_text())
meta = json.loads((ROOT / 'experiments/exp051_curpop/meta.json').read_text())
hold = set(freeze['holdout_episodes'])
cands = {x: f'experiments/fp_robust/variant_{x}.py' for x in ('a', 'b')}

def save(name, jobs):
    assert not any(9000 <= int(j[4]) <= 9599 for j in jobs)
    assert len(jobs) == len({(j[0], j[2], j[4], j[5]) for j in jobs})
    path = OUT / name
    assert not path.exists(), f'refuse overwrite {path}'
    path.write_text(json.dumps(jobs, separators=(',', ':')) + '\n')
    print(name, len(jobs), hashlib.sha256(path.read_bytes()).hexdigest())

def tape_job(vid, path, m):
    episode = m['episode']
    return [vid, path, f'C{episode}',
            f'experiments/exp051_curpop/tapes/C{episode}.py',
            int(m['seed']), int(m['seat'])]

save('jobs_smoke.json', [[v, p, 'D',
                          'releases/public-dpnew-55be5d5f-exact/main.py',
                          6001, seat] for v, p in cands.items() for seat in (0, 1)])
save('jobs_dev.json', [tape_job(v, p, m) for v, p in cands.items()
                       for m in meta if m['episode'] not in hold])
save('jobs_holdout.json', [tape_job(v, p, m) for v, p in cands.items()
                           for m in meta if m['episode'] in hold])

fresh = json.loads((ROOT / 'experiments/exp049_fresh/meta.json').read_text())
bad = {r[0] for r in map(json.loads, (ROOT / 'experiments/exp049_fresh/parity.jsonl').open()) if not r[1]}
save('jobs_fresh.json', [[v, p, f"F{m['episode']}",
                          f"experiments/exp049_fresh/tapes/F{m['episode']}.py",
                          int(m['seed']), int(m['our_seat'])]
                         for v, p in cands.items() for m in fresh if m['episode'] not in bad])

X = 'releases/public-dpnew-55be5d5f-exact/main.py'
Y = 'analysis/daily_scan/20260928/extracted/kaggriculture-harvest-ledger/main.py'
Z = 'analysis/daily_scan/20260928/extracted/2965-master-engine/main.py'
W = 'analysis/daily_scan/20260928/extracted/farmer-john-and-the-idle-seller/main.py'
family = [('D', X), ('HL63', Y), ('M2965', Z), ('FJ1010', W)]
paths = {**cands, 'd157': 'releases/exp035-d157/main.py',
         'c26': 'releases/exp039-c26/main.py'}
save('jobs_closed.json', [[v, p, o, op, seed, seat]
                          for v, p in paths.items() for o, op in family
                          for seed in freeze['closed_loop_seeds'] for seat in (0, 1)])
