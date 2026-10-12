"""Development-only check whether current-turn sale schedules can be predicted."""
import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
hold = set(json.loads((OUT/'freeze.json').read_text())['holdout_episodes'])
rows = list(csv.DictReader((ROOT/'analysis/c26_hosted_20260929/opponents.csv').open()))
rows = [r for r in rows if r['episode'] not in hold and r['is_55be'] == 'True']
steps = [385,457,481,577,600,601,624,668]
counts = defaultdict(Counter)
for row in rows:
    raw = json.load(gzip.open(ROOT/f"private_artifacts/c26_hosted_20260929/raw/{row['episode']}.json.gz"))
    seat = 1-int(row['seat'])
    for step in steps:
        action = raw['steps'][step+1][seat]['action'] or {}
        sales = tuple((j,o[1],int(o[2])) for j,o in enumerate(action.get('market') or [])
                      if o and len(o)>=3 and o[0]=='SELL')
        counts[step][sales] += 1
out = {str(step): {'n':sum(c.values()),'unique':len(c),
                   'top':[{'sale':k,'n':n} for k,n in c.most_common(5)]}
       for step,c in counts.items()}
(OUT/'sale_predictability.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
