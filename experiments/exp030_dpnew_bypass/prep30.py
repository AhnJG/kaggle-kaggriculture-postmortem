"""EXP-030 (Claude, criteria per Codex REVIEW-0927B + general panel). stdlib; run from repo root.
python prep30.py screen | final"""
import ast,json,hashlib,sys
from pathlib import Path
OUT=Path('experiments/exp030_dpnew_bypass');(OUT/'variants').mkdir(parents=True,exist_ok=True)
D='releases/public-dpnew-55be5d5f-exact/main.py';P='releases/round2-v074/main.py';O2='releases/public-newmeta-127ed3e6-exact/main.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(D).startswith('55be5d5f') and sha(P).startswith('860a502c') and sha(O2).startswith('127ed3e6')
G=json.load(open('experiments/exp028_dpnew/prepare28.py'.replace('prepare28.py','summary.json')))  # sanity: EXP-028 exists
guard=[g for g in json.load(open('experiments/exp027_stage3/manifest.json'))['guard'] if not g['sha256'].startswith('55be5d5f')]
GUARD4=[g for g in guard if g['id'] in ('PUB01','PUB02','PUB06','PUB12')];assert len(GUARD4)==4
def panel(jobs,agents,oid,op,seeds):
    for v,p in agents:
        for s in seeds:
            for t in (0,1):jobs.append([v,p,oid,op,s,t])
if sys.argv[1]=='screen':
    src=Path(D).read_bytes();t=ast.parse(src.decode())
    defs={n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}
    al=[(n.targets[0].id,n.value.id) for n in t.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id.endswith('_PARENT') and isinstance(n.value,ast.Name)]
    ald=dict(al);specs=[]
    for outer,fn in al:
        if not outer.startswith('_S') or fn not in defs:continue
        calls={c.func.id for c in ast.walk(defs[fn]) if isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id.endswith('_PARENT')}
        if len(calls)==1:
            inner=next(iter(calls))
            if inner in ald and inner!=outer:specs.append(dict(kind='bypass',skip=fn,target=outer,new=inner))
    specs.append(dict(kind='bypass_final',skip='step1009_step1008_fortyfirst_final_fixedsell_closure_agent',target='ENTRY',new='_S1009_PARENT'))
    vs=[]
    for i,c in enumerate(specs):
        txt='\n# Frozen EXP-030 wrapper; parent bytes above are unchanged.\n'
        if c['kind']=='bypass':txt+=f"_EXP030_ENTRY = [v for v in globals().values() if callable(v)][-1]\n{c['target']} = {c['new']}\n"
        else:txt+=f"_EXP030_ENTRY = {c['new']}\n"
        txt+='def exp030_entry(obs, configuration=None):\n    return _EXP030_ENTRY(obs, configuration)\n'
        b=src+txt.encode();p=OUT/'variants'/f'b{i:03}.py';p.write_bytes(b);compile(b,str(p),'exec')
        vs.append(dict(id=f'b{i:03}',path=str(p),sha256=hashlib.sha256(b).hexdigest(),change=c))
    json.dump(vs,open(OUT/'variants.json','w'),indent=1)
    jobs=[];ag=[('D',D)]+[(v['id'],v['path']) for v in vs]
    panel(jobs,ag,'V074',P,range(14000,14005));panel(jobs,ag,'O127',O2,range(14000,14005))
    for g in GUARD4:panel(jobs,ag,g['id'],g['path'],range(14010,14015))
    json.dump(jobs,open(OUT/'jobs-screen.json','w'));print('variants',len(vs),'jobs',len(jobs))
else:
    sel=json.load(open(OUT/'screen-summary.json'))['advance'];assert sel,'NO_ADVANCE'
    v={x['id']:x for x in json.load(open(OUT/'variants.json'))};ag=[('D',D)]+[(i,v[i]['path']) for i in sel];jobs=[]
    panel(jobs,ag,'V074',P,range(14100,14150));panel(jobs,ag,'O127',O2,range(14100,14150))
    for g in guard:panel(jobs,ag,g['id'],g['path'],range(14200,14210))
    eps=json.load(open('experiments/p4b_20260926/episodes.json'));seen=set()
    for i,e in enumerate(eps):
        if e['id'] in seen:continue
        seen.add(e['id']);assert not 9000<=e['seed']<=9599
        for vv,pp in ag+[('P',P)]:jobs.append([vv,pp,f"H{i:03d}-E{e['id']}",e['opp_path'],e['seed'],e['seat']])
    json.dump(jobs,open(OUT/'jobs-final.json','w'));print('final jobs',len(jobs),'hosted unique',len(seen))
