"""EXP-058 shared helpers (Claude 09-29, written before any Stage S result)."""
import json,gzip,glob,os
EFF={tuple(k.split('|')):v for k,v in json.load(open('experiments/exp058_route/effective_route_by_pair.json')).items()}
NATIVE={'Y':9,'D':105}
def group_of_pair(p):
    r=EFF.get(tuple(p))
    return None if r is None else 'Y' if r==9 else 'D' if r==105 else 'S'
_RAW=glob.glob('private_artifacts/*/raw/')
def shops_of_episode(ep):
    for p in _RAW:
        q=f'{p}{ep}.json.gz'
        if os.path.exists(q):
            r=json.load(gzip.open(q));return r['steps'][150][0]['observation']['town']['unlocked_shops'][:2]
    return None
RULES=[(g,r) for g in ('Y','D','S') for r in (105,9,107,103,0) if r!=NATIVE.get(g)]
assert len(RULES)==13
