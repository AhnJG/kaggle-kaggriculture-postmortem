"""EXP-062 v5 (Claude-B 20:00 KST): L5p + endgame hire cap (idea 1). Drops HIRE orders beyond a per-day cap on the last days.
Engine: hand commands for non-existent hands are no-ops (_farmer_position None). L5p bytes unchanged; tail override only."""
import hashlib,json,pathlib
BASE=pathlib.Path('experiments/exp062/variants/L5p.py').read_text()
TAIL='''

# ==== EXP-063 {name}: endgame hire cap {CAP} (Claude 2026-09-30). L5p bytes above unchanged. ====
_E63_PARENT = [v for v in globals().values() if callable(v)][-1]
_E63_CAP = {CAP}
_E63_REPORT = dict(hire_dropped=0, hire_errors=0)


def exp063_entry(obs, configuration=None):
    if int(obs.get("step", 0)) == 0:
        _E63_REPORT.update(hire_dropped=0, hire_errors=0)
    action = _E63_PARENT(obs, configuration)
    try:
        cap = _E63_CAP.get(int(obs["step"]) // 24)
        if cap is not None and isinstance(action, dict) and action.get("market"):
            me = obs["farms"][int(obs["player"])]
            allowed = max(0, cap - int(me.get("hires_today", 0)))
            kept = []
            for o in action["market"]:
                if isinstance(o, (list, tuple)) and len(o) >= 1 and o[0] == "HIRE":
                    if allowed > 0:
                        allowed -= 1
                        kept.append(o)
                    else:
                        _E63_REPORT["hire_dropped"] += 1
                else:
                    kept.append(o)
            action["market"] = kept
    except Exception:
        _E63_REPORT["hire_errors"] += 1
    return action
exp063_entry.telemetry = _E63_REPORT
'''
V={}
for name,CAP in [('L5H29c10',{29:10}),('L5H29c8',{29:8}),('L5H29c6',{29:6}),('L5H28c8',{28:8,29:8})]:
    p=pathlib.Path(f'experiments/exp062/variants/{name}.py');p.write_text(BASE+TAIL.format(name=name,CAP=repr(CAP)))
    V[name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'base':'L5p','cap':{str(k):v for k,v in CAP.items()}}
json.dump(V,open('experiments/exp062/variants/manifest_v5.json','w'),indent=1)
print({k:v['sha256'][:12] for k,v in V.items()})
