"""EXP-049 fresh 2400+ tapes (Claude 09-29): same tape format as prep41, episodes after 2026-09-28T05:27Z. Team split = exp041's (not recomputed)."""
import json,gzip,os
SRC='analysis/top2400_fresh_20260929/';RAW='private_artifacts/top2400_fresh_20260929/raw/';OUT='experiments/exp049_fresh'
E=json.load(open(SRC+'episodes_all.json'));T=json.load(open(SRC+'targets.json'))
old={m['episode'] for m in json.load(open('experiments/exp041_top2400/meta.json'))}
H=set(json.load(open('experiments/exp041_top2400/team-split.json'))['holdout_teams'])
rows=[]
for e in E:
    if e['id'] in old:continue
    r=json.load(gzip.open(f"{RAW}{e['id']}.json.gz"));names=r['info']['TeamNames'];tn=T[str(e['submission_id'])]
    if len(r['steps'])<720 or tn not in names:continue
    ts=names.index(tn);os_=1-ts
    tape=[r['steps'][k+1][ts]['action'] for k in range(len(r['steps'])-1)]
    src='import json\nTAPE=json.loads('+repr(json.dumps(tape))+')\ndef tape_agent(obs, configuration=None):\n    s=int(obs["step"])\n    return TAPE[s] if s<len(TAPE) else {"farmer":["PASS"],"hands":[],"market":[]}\n'
    open(f"{OUT}/tapes/F{e['id']}.py",'w').write(src)
    rw=[r['steps'][-1][i]['reward'] for i in (0,1)]
    rows.append(dict(episode=e['id'],sub=e['submission_id'],team=tn,part='H' if tn in H else 'F',seed=int(r['info']['seed']),target_seat=ts,our_seat=os_,opp_team=names[os_],target_reward=rw[ts],opp_reward=rw[os_]))
json.dump(rows,open(f'{OUT}/meta.json','w'),indent=0,ensure_ascii=False)
import collections;print(len(rows),collections.Counter(r['part'] for r in rows),collections.Counter(r['team'] for r in rows if r['part']=='H'))
assert not any(9000<=r['seed']<9600 for r in rows)
