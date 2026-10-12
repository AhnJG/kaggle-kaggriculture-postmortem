"""Build the Stage C candidate RG_<G><R>.py from d157 (Claude 09-29, before any result). Usage: python build_rg.py G R
Only pairs of group G are remapped to route R via _V92_TABLE (applied last by the router); other pairs keep d157 behaviour."""
import sys,json,hashlib
sys.path.insert(0,'experiments/exp058_route');from common58 import EFF,group_of_pair
G,R=sys.argv[1],int(sys.argv[2])
pairs=sorted(p for p in EFF if group_of_pair(p)==G)
src=open('releases/exp035-d157/main.py').read()
assert hashlib.sha256(src.encode()).hexdigest().startswith('94a46c11')
s=src+f"""
# EXP-058 RG_{G}{R}: d157 bytes above unchanged. Group {G} ({len(pairs)} ordered first-two-shop pairs) -> route {R} at step 144.
# Pairs outside the group keep d157's router. Day-27 switch to route 2 and _V93 rival rule untouched. See experiments/exp058_route/PREREG.md.
_EXP058_PAIRS = {pairs!r}
for _p in _EXP058_PAIRS:
    _V92_TABLE[tuple(_p)] = {R}
_EXP058_ENTRY = exp029_entry
def exp058_entry(obs, configuration=None):
    return _EXP058_ENTRY(obs, configuration)
"""
p=f'experiments/exp058_route/variants/RG_{G}{R}.py';open(p,'w').write(s)
m=json.load(open('experiments/exp058_route/manifest.json'));m[f'RG_{G}{R}']={'path':p,'sha256':hashlib.sha256(s.encode()).hexdigest(),'pairs':len(pairs)}
json.dump(m,open('experiments/exp058_route/manifest.json','w'),indent=1);print(p,m[f'RG_{G}{R}'])
