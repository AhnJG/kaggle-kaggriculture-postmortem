#!/usr/bin/env python3
"""Post-run arithmetic audit, not an EXP-011 preregistered gate or independent review."""
import copy
import hashlib
import json
from pathlib import Path

from kaggle_environments.envs.kaggriculture import kaggriculture as K

ROOT = Path('experiments/results/p1_shed_attribution')
checks=[]; records=[]
for path in sorted((ROOT/'cells').glob('*.json')):
    doc=json.loads(path.read_text()); r=doc['payload'][0]
    for pid in doc['gated_player_indices']:
        for e in r['players'][pid]['drop_events']:
            private={'shed':copy.deepcopy(e['shed_before']), 'inventories':copy.deepcopy(e['carried_before'])}
            carried=sum(sum(inv.values()) for inv in private['inventories'])
            room=max(0,e['shed_capacity']-sum(private['shed'].values()))
            K._drop_inventories_to_shed(private,e['shed_capacity'])
            moved={item:n-e['shed_before'].get(item,0) for item,n in private['shed'].items()
                   if n-e['shed_before'].get(item,0)}
            expected=max(0,carried-room)
            checks.append(dict(cell=path.name,player=pid,day=e['day'],
                               expected_loss=expected,actual_loss=e['discarded_total'],
                               expected_deposited=moved,actual_deposited=e['deposited'],
                               passed=(expected==e['discarded_total'] and moved==e['deposited'])))
            if e['discarded_total']:
                records.append(dict(cell=path.name,player=pid,day=e['day'],
                                    available_room=room,carried=carried,loss=expected))
result=dict(scope='Post-run ENGINE arithmetic audit; not an independent review or new success gate.',
            engine_sha256=hashlib.sha256(Path(K.__file__).read_bytes()).hexdigest(),
            passed=all(c['passed'] for c in checks), events=len(checks),positive_loss_events=len(records),
            total_loss=sum(r['loss'] for r in records),checks=checks,positive_events=records,
            interpretation='All observed loss equals aggregate carried minus available room. Reordering only the final transfer cannot reduce total units lost with fixed inventories and capacity; it can change which items are lost. Remote location is a class attribute, not proven causal.')
(ROOT/'allocation_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('allocation audit',result['passed'], 'events',len(checks),'loss events',len(records),'units',result['total_loss'])
raise SystemExit(0 if result['passed'] else 1)
