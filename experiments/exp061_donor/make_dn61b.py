import json,gzip,hashlib
base=open('releases/exp035-d157/main.py').read(); assert hashlib.sha256(base.encode()).hexdigest().startswith('94a46c11')
layer=open('experiments/exp061_donor/dn_layer.py').read()
EFF=json.load(open('experiments/exp058_route/effective_route_by_pair.json'))
def grp(p):
    r=EFF.get('|'.join(p)); return None if r is None else 'Y' if r==9 else 'D' if r==105 else 'S'
R=[json.loads(l) for l in open('experiments/exp061_donor/scan61b.jsonl')]
R=[r for r in R if r['match'] and grp(r['shops'])=='Y']; R.sort(key=lambda r:(int(r['label'][1:].split('_')[0]),r['id']))
seen=set(); tp=set(); man={}; i=100
for r in R:
    if (r['label'],tuple(r['shops'])) in tp: continue
    d=json.load(gzip.open(f"private_artifacts/survey300_20260929/raw/{r['id']}.json.gz")); s=r['seat']
    tape=[d['steps'][k+1][s]['action'] for k in range(len(d['steps'])-1)]
    h=hashlib.sha256(json.dumps(tape[144:],sort_keys=True).encode()).hexdigest()
    if h in seen: continue
    seen.add(h); tp.add((r['label'],tuple(r['shops']))); i+=1; name=f'DN{i}'; rid=900+i
    src=base+layer.replace('__TAPE__',repr(json.dumps(tape))).replace('__RID__',str(rid)).replace('__G__',repr('Y')).replace('__EFF__',repr(EFF))
    p=f'experiments/exp061_donor/variants/{name}.py'; open(p,'w').write(src)
    man[name]={'path':p,'rid':rid,'group':'Y','shops':r['shops'],'episode':r['id'],'label':r['label'],'sha256':hashlib.sha256(src.encode()).hexdigest()}
json.dump(man,open('experiments/exp061_donor/manifest61b.json','w'),indent=1)
S=[x for x in json.load(open('experiments/exp060_mbr/sets.json'))['screen'] if x['group']=='Y'][:10]
jobs=[[n,m['path'],x['tape'].split('/')[-1][:-3],x['tape'],x['seed'],x['seat']] for n,m in man.items() for x in S]
json.dump(jobs,open('experiments/exp061_donor/jobs-dn61b-10.json','w')); print('donors',len(man),'jobs',len(jobs))
