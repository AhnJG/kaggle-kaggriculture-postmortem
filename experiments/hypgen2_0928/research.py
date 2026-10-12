"""Read-only research over saved results/replays; no agent calls or new games."""
import collections as C
import csv
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def wdl(a):
    return [sum(x==1 for x in a), sum(x==.5 for x in a), sum(x==0 for x in a)]
def tiles(f):
    return dict(C.Counter(t.get('crop',t.get('animal',t['kind'])) for row in f['tiles'] for t in row if isinstance(t,dict)))

def main():
    inputs={}
    def read(p):
        inputs[p]=sha(ROOT/p)
        return json.loads((ROOT/p).read_text())
    meta={str(m['episode']):m for m in read('experiments/exp033_tapes/meta.json')}
    matrices={}
    for exp in ['exp028_dpnew','exp032_specialist','exp033_tapes']:
        files=['games-cloud.jsonl','games-kaggle.jsonl'] if exp=='exp033_tapes' else ['games.jsonl']
        rows={}; duplicates=0; conflicts=[]
        for f in files:
            p=f'experiments/{exp}/{f}';inputs[p]=sha(ROOT/p)
            for line,txt in enumerate((ROOT/p).read_text().splitlines(),1):
                r=json.loads(txt);key=r['key'];r['_source']=f'{p}:{line}'
                assert r['seed'] not in range(9000,9600)
                if key in rows:
                    duplicates+=1
                    fields=['score','margin','rewards','act_sha','action_count','statuses','err','agent_errors']
                    diff=[k for k in fields if rows[key].get(k)!=r.get(k)]
                    if diff:conflicts.append([key,diff,rows[key]['_source'],r['_source']])
                    continue
                rows[key]=r
        groups=C.defaultdict(list)
        for r in rows.values():
            oid=meta[r['opponent'][1:]]['fam'] if exp=='exp033_tapes' else r['opponent']
            groups[(r['vid'],oid)].append(r['score'])
        summary=[dict(vid=k[0],opponent=k[1],n=len(v),wdl=wdl(v),score=sum(v)/len(v)) for k,v in sorted(groups.items())]
        matrices[exp]=dict(n=len(rows),duplicates=duplicates,conflicts=conflicts,groups=summary)
        if exp=='exp033_tapes':
            pairs=[]
            for eid,m in meta.items():
                rr={r['vid']:r for r in rows.values() if r['opponent']=='T'+eid}
                pairs.append(dict(meta=m,rows=rr))
            dump('tape_pairs.json',pairs)
        dump(exp+'_rows.json',list(rows.values()))
    dump('matrices.json',matrices)
    # A source episode can occur in both windows. Preserve origins, deduplicate episode.
    episodes={}
    for window in ['v074_hosted_20260927','d157_hosted_20260928']:
        p=f'analysis/{window}/opponents.csv';inputs[p]=sha(ROOT/p)
        for line,r in enumerate(csv.DictReader((ROOT/p).open()),2):
            eid=r['episode']
            if eid in episodes:
                episodes[eid]['origins'].append(f'{p}:{line}');continue
            rp=ROOT/f'private_artifacts/{window}/raw/{eid}.json.gz'
            assert int(r['seed']) not in range(9000,9600)
            raw=json.load(gzip.open(rp)); us=int(r['seat']); steps=raw['steps']
            assert len(steps)==720 and int(raw['info']['seed'])==int(r['seed'])
            side=[]
            for seat in [us,1-us]:
                requests=C.Counter();ops=C.Counter();first_sell={};farm_sha=hashlib.sha256()
                for step in range(1,len(steps)):
                    ac=steps[step][seat]['action'] or {}
                    farm_sha.update(json.dumps([ac.get('farmer'),ac.get('hands')],sort_keys=True).encode())
                    for order in ac.get('market',[]):
                        if len(order)>2 and isinstance(order[2],(int,float)):
                            requests[order[0]+' '+order[1]]+=order[2]
                            if order[0]=='SELL':first_sell.setdefault(order[1],step-1)
                    for a in [ac.get('farmer',[])]+ac.get('hands',[]):
                        if a:ops[' '.join(map(str,a))]+=1
                side.append(dict(seat=seat,requested=dict(requests),ops=dict(ops),first_sell=first_sell,farm_action_sha256=farm_sha.hexdigest(),checkpoints={str(k):dict(cash=steps[k][0]['observation']['farms'][seat]['money'],tiles=tiles(steps[k][0]['observation']['farms'][seat])) for k in [120,288,432,600,719]}))
            episodes[eid]=dict(metadata=r,origins=[f'{p}:{line}'],raw=str(rp.relative_to(ROOT)),raw_sha256=sha(rp),module_version=raw.get('module_version'),sides=side)
    with (OUT/'hosted_features.jsonl').open('w') as f:
        for e in episodes.values():f.write(json.dumps(e,ensure_ascii=False)+'\n')
    dump('input_sha256.json',inputs)
    print('matrices',[(k,v['n'],len(v['conflicts'])) for k,v in matrices.items()],'hosted',len(episodes))

if __name__=='__main__':main()
