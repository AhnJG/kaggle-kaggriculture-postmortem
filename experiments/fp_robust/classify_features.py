"""Read-only feature inventory on preregistered development episodes only."""
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[2]
F = Path(__file__).resolve().parent
hold = set(json.loads((F / 'freeze.json').read_text())['holdout_episodes'])
rows = list(csv.DictReader((R / 'analysis/c26_hosted_20260929/opponents.csv').open()))
out = defaultdict(list)
for row in rows:
    episode = row['episode']
    if episode in hold:
        continue
    raw = json.load(gzip.open(R / f'private_artifacts/c26_hosted_20260929/raw/{episode}.json.gz'))
    seat = 1 - int(row['seat'])
    o = raw['steps'][301][seat]['observation']
    rival = o['farms'][seat]
    counts = defaultdict(int)
    for line in rival['tiles']:
        for tile in line:
            if isinstance(tile, dict):
                counts[tile.get('crop') or tile.get('animal') or tile.get('kind')] += 1
    label = '55be' if row['is_55be'] == 'True' else 'other'
    out[label].append(dict(episode=episode, sheep=counts['SHEEP'], cow=counts['COW'],
                           melon=counts['MELON'], strawberry=counts['STRAWBERRY'],
                           wheat=counts['WHEAT'], hands=len(rival['hands'])))

def quant(vals):
    s = sorted(vals)
    return [s[int((len(s)-1)*q)] for q in (0, .25, .5, .75, 1)]

for label, records in out.items():
    print(label, 'n', len(records))
    for key in ('sheep', 'cow', 'melon', 'strawberry', 'wheat', 'hands'):
        print(key, quant([r[key] for r in records]))
    print('canonical', sum((r['sheep'],r['cow'],r['melon'],r['strawberry'],r['wheat']) == (2,4,12,4,3) for r in records))
