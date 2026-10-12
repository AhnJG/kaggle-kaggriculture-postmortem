"""EXP-062 stage-1 variants: d157 bytes unchanged + tail override block. Claude 2026-09-30."""
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
for tag,m in [('GMm15',0.85),('GMm08',0.92),('GMp08',1.08),('GMp15',1.15)]:
    mk(tag,f"V9_RACEGATE_BASE = {{k: v * {m} for k, v in V9_RACEGATE_BASE.items()}}\nV9_RACEPX_BASE = {{k: v * {m} for k, v in V9_RACEPX_BASE.items()}}")
mk('HZ08','V9_RACE_DEFAULT = 8\nV9_RACE_MAX = 12')
mk('HZ24','V9_RACE_DEFAULT = 24\nV9_RACE_MAX = 32')
mk('HZ64','V9_RACE_DEFAULT = 64\nV9_RACE_MAX = 72')
json.dump(V,open('experiments/exp062/variants/manifest_v1.json','w'),indent=1)
print({k:v['sha256'][:12] for k,v in V.items()})
