"""Build C_d / C_c from a group->route table. Usage: python make_cand.py <table.json> <tag>
table.json: {"Y": "DN29"|"FM110"|"native", ...}. native groups are left out of the table (base behaviour)."""
import json,sys,hashlib,gzip
T=json.load(open(sys.argv[1])); tag=sys.argv[2]
EFF=json.load(open('experiments/exp058_route/effective_route_by_pair.json'))
dman=json.load(open('experiments/exp061_donor/manifest.json'))
table={}; extra={}
for g,a in T.items():
    if a in ('native','d157','FM9'): continue
    if a.startswith('FM'): table[g]=int(a[2:])
    elif a.startswith('DN'):
        m=dman[a]; d=json.load(gzip.open(f"private_artifacts/survey300_20260929/raw/{m['episode']}.json.gz"))
        seat=[json.loads(l) for l in open('experiments/exp061_donor/scan.jsonl') if json.loads(l)['id']==m['episode']][0]['seat']
        extra[str(m['rid'])]=[d['steps'][k+1][seat]['action'] for k in range(len(d['steps'])-1)]; table[g]=m['rid']
layer=open('experiments/exp060_mbr/mbr_layer.py').read().replace('__TABLE__',repr(table)).replace('__EFF__',repr(EFF)).replace('__EXTRA__',repr(json.dumps(extra)))
B={'d':('releases/exp035-d157/main.py','94a46c11'),'c':('experiments/exp039_camargin/variants/c26.py','ff230c83')}
man={}
for b,(p,sh) in B.items():
    base=open(p).read(); assert hashlib.sha256(base.encode()).hexdigest().startswith(sh)
    src=base+layer; n=f'C{b}_{tag}'; q=f'experiments/exp060_mbr/cand/{n}.py'; open(q,'w').write(src)
    man[n]={'path':q,'table':table,'donor_rids':list(extra),'sha256':hashlib.sha256(src.encode()).hexdigest()}
json.dump(man,open(f'experiments/exp060_mbr/cand/manifest-{tag}.json','w'),indent=1); print(json.dumps(man,indent=0)[:600])
