"""Development-only within-game recurrence of rival market SELL schedules."""
import csv
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
hold = set(json.loads((OUT/'freeze.json').read_text())['holdout_episodes'])
rows = list(csv.DictReader((ROOT/'analysis/c26_hosted_20260929/opponents.csv').open()))
rows = [r for r in rows if r['episode'] not in hold and r['is_55be'] == 'True']
stat = {lag:{'n':0,'exact':0,'item_intersection':0,'item_union':0,'quantity_exact':0}
        for lag in (1,24,48)}
for row in rows:
    raw = json.load(gzip.open(ROOT/f"private_artifacts/c26_hosted_20260929/raw/{row['episode']}.json.gz"))
    seat = 1-int(row['seat'])
    schedules = []
    for step in range(719):
        action = raw['steps'][step+1][seat]['action'] or {}
        orders = action.get('market') or []
        sales = tuple((j,o[1],int(o[2])) for j,o in enumerate(orders)
                      if o and len(o)>=3 and o[0]=='SELL')
        schedules.append(sales)
    for lag,s in stat.items():
        for step in range(max(lag,144),719):
            now, past = schedules[step], schedules[step-lag]
            if not now and not past:
                continue
            s['n'] += 1
            s['exact'] += now == past
            ni,pi = {x[1] for x in now},{x[1] for x in past}
            s['item_intersection'] += len(ni & pi)
            s['item_union'] += len(ni | pi)
            s['quantity_exact'] += {x[1]:x[2] for x in now} == {x[1]:x[2] for x in past}
print(json.dumps(stat,indent=2))
(OUT/'sale_recurrence.json').write_text(json.dumps(stat,indent=2)+'\n')
