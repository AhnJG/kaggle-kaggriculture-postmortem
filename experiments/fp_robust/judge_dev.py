"""Apply the frozen development gates without reading the time holdout."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
freeze = json.loads((OUT / 'freeze.json').read_text())
meta = json.loads((ROOT / 'experiments/exp051_curpop/meta.json').read_text())
hold = set(freeze['holdout_episodes'])
dev = {m['episode']: m for m in meta if m['episode'] not in hold}

def read_rows(path):
    out = {}
    for line in path.open():
        row = json.loads(line)
        if row['opponent'].startswith('C'):
            out[(row['vid'], row['opponent'][1:])] = row
    return out

old = read_rows(ROOT / 'experiments/exp051_curpop/games.jsonl')
new = read_rows(OUT / 'games_dev_v2.jsonl')

def valid(row):
    return (row['err'] is None and row['statuses'] == ['DONE', 'DONE']
            and row['action_count'] == 719 and not row['agent_errors']
            and row['score'] in (0.0, 0.5, 1.0))

def lower(values, salt):
    rng = random.Random(freeze['bootstrap_seed'] + salt)
    n = len(values)
    return sorted(sum(values[rng.randrange(n)] for _ in range(n))/n
                  for _ in range(10_000))[249]

result = {'freeze_sha256': __import__('hashlib').sha256((OUT/'freeze.json').read_bytes()).hexdigest(),
          'n_dev': len(dev), 'candidates': {}}
for ci, cand in enumerate(('a', 'b')):
    current = [new.get((cand, ep)) for ep in dev]
    missing = sum(r is None for r in current)
    invalid = sum(r is not None and not valid(r) for r in current)
    group = [ep for ep, m in dev.items()
             if m['label'].startswith('55be') and 2200 <= float(m['op_lb']) < 2400]
    x = {'missing': missing, 'invalid': invalid, 'n_target': len(group)}
    if not missing and not invalid:
        x['score'] = sum(new[(cand,ep)]['score'] for ep in dev)/len(dev)
        for bi, base in enumerate(('d157','c26')):
            d = [new[(cand,ep)]['score']-old[(base,ep)]['score'] for ep in dev]
            t = [new[(cand,ep)]['score']-old[(base,ep)]['score'] for ep in group]
            x[f'vs_{base}'] = {'point': sum(d)/len(d), 'lower95': lower(d,ci*10+bi),
                              'target_point': sum(t)/len(t) if t else None}
        x['different_actions_vs_c26'] = sum(new[(cand,ep)]['act_sha'] != old[('c26',ep)]['act_sha'] for ep in dev)
        x['pass_dev'] = all(x[f'vs_{b}']['point'] > .03 and x[f'vs_{b}']['lower95'] > 0
                            and (len(group) < 20 or x[f'vs_{b}']['target_point'] >= .05)
                            for b in ('c26','d157'))
    else:
        x['pass_dev'] = False
    result['candidates'][cand] = x
(OUT / 'dev_verdict.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
print(json.dumps(result, indent=2, sort_keys=True))
