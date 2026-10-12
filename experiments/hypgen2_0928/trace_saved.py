"""Sequential replay of eleven frozen saved episodes, with exact-state parity."""
import collections as C
import contextlib
import gzip
import hashlib
import importlib
import io
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
with contextlib.redirect_stdout(io.StringIO()):
    from kaggle_environments import make
    from tools.postmortem import build_report
    E=importlib.import_module('kaggle_environments.envs.kaggriculture.kaggriculture')

def main():
    manifest=json.loads((OUT/'trace_manifest.json').read_text())
    assert len(manifest['episodes'])==11 and manifest['workers']==1
    engine_sha=hashlib.sha256(Path(E.__file__).read_bytes()).hexdigest()
    assert engine_sha=='bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e'
    done={r['episode'] for r in map(json.loads,(OUT/'trace_summary.jsonl').read_text().splitlines())} if (OUT/'trace_summary.jsonl').exists() else set()
    for item in manifest['episodes']:
        if item['episode'] in done:continue
        raw=json.load(gzip.open(ROOT/item['raw'])); seed=int(raw['info']['seed']);us=item['seat']
        assert seed not in range(9000,9600)
        tape=[[row[s]['action'] for row in raw['steps'][1:]] for s in [0,1]]
        commits=[];ctx={};original_commit=E._commit_unit;original_market=E._process_market
        def market(state,env):
            ctx['step']=int(state[0].observation.step)
            ctx['farms']=state[0].observation.farms
            return original_market(state,env)
        def commit(op,product,price,farm,private,book,shed_capacity=100):
            seat=0 if farm is ctx['farms'][0] else 1
            ok=original_commit(op,product,price,farm,private,book,shed_capacity)
            if ok:commits.append(dict(step=ctx['step'],seat=seat,op=op,item=product,price=price))
            return ok
        E._process_market=market;E._commit_unit=commit
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                env=make('kaggriculture',configuration={'episodeSteps':720,'seed':seed})
                env.run([lambda obs,cfg:tape[0][int(obs.step)],lambda obs,cfg:tape[1][int(obs.step)]])
        finally:E._process_market=original_market;E._commit_unit=original_commit
        mismatch=[]
        for k,(actual,expected) in enumerate(zip(env.steps,raw['steps'])):
            for s in [0,1]:
                for field in ['farms','market','private','town']:
                    # Shared observation fields can be null for seat 1 in serialized replays.
                    v=expected[s]['observation'].get(field)
                    if v is not None and actual[s].observation.get(field)!=v:mismatch.append([k,s,field])
        groups=C.defaultdict(lambda:[0,0])
        with (OUT/f"fills-{item['episode']}.jsonl").open('w') as f:
            for c in commits:
                f.write(json.dumps(c)+'\n');g=groups[(c['seat'],c['op'],c['item'])];g[0]+=1;g[1]+=c['price']
        post=build_report('saved-seat0','saved-seat1',seed,env.steps,top_n=3)
        (OUT/f"postmortem-{item['episode']}.json").write_text(json.dumps(post,ensure_ascii=False,indent=2,default=str)+'\n')
        result=dict(episode=item['episode'],seed=seed,our_seat=us,raw=item['raw'],raw_sha256=item['raw_sha256'],engine_sha256=engine_sha,
                    steps=len(env.steps),statuses=[s.status for s in env.steps[-1]],rewards=[s.reward for s in env.steps[-1]],parity_mismatches=len(mismatch),first_mismatches=mismatch[:10],
                    fills=[dict(seat=k[0],op=k[1],item=k[2],units=v[0],cash=v[1]) for k,v in sorted(groups.items())])
        with (OUT/'trace_summary.jsonl').open('a') as f:f.write(json.dumps(result)+'\n')
        print(item['episode'],result['rewards'],'mismatch',len(mismatch),flush=True)

if __name__=='__main__':main()
