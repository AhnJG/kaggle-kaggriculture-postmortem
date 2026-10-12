import hashlib,json,pathlib
BASE=pathlib.Path('releases/exp035-d157/main.py').read_text()
V={}
def mk(name,body):
    tail=f"""

# ==== EXP-062 {name} (Claude 2026-09-30). d157 bytes above unchanged. ====
_E62_PARENT = [v for v in globals().values() if callable(v)][-1]
{body}
def exp062_entry(obs, configuration=None):
    return _E62_PARENT(obs, configuration)
"""
    p=pathlib.Path(f'experiments/exp062/variants/{name}.py');p.write_text(BASE+tail)
    V[name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'override':body}
mk('HZ96','V9_RACE_DEFAULT = 96\nV9_RACE_MAX = 120')
mk('V92K2','_V92_P_K = 2')
mk('V92H96','_V92_P_H = 96')
mk('V92T3','_V92_P_TOP = 3')
json.dump(V,open('experiments/exp062/variants/manifest_v1b.json','w'),indent=1)
print({k:v['sha256'][:12] for k,v in V.items()})
