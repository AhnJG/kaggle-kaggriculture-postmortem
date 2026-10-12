"""EXP-029 (Claude): mirror knife-edge on 55be5d5f. stdlib; run from repo root.
python prep29.py screen   -> variants + jobs-screen.json
python prep29.py stage2   -> jobs-stage2.json from screen-summary.json"""
import ast,re,math,json,hashlib,sys
from pathlib import Path
OUT=Path('experiments/exp029_dpnew_mirror');(OUT/'variants').mkdir(parents=True,exist_ok=True)
PARENT='releases/public-dpnew-55be5d5f-exact/main.py';O1=PARENT;O2='releases/public-newmeta-127ed3e6-exact/main.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(PARENT).startswith('55be5d5f') and sha(O2).startswith('127ed3e6')
def specs(src):
    t=ast.parse(src);c={}
    for n in t.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and re.fullmatch(r'_?[A-Z][A-Z0-9_]{2,}',n.targets[0].id):
            try:v=ast.literal_eval(n.value)
            except Exception:continue
            if type(v) in (int,float) and math.isfinite(v):c[n.targets[0].id]=v
    ex=re.compile(r'GOOSE|COOP|EGG|QUAD|LAND|ADV_LOOK|ADVANCE|LEAD|STARTER|PPO|CLEAN|WEED|TURNS_PER_DAY|LAST_STEP|MAX_ORDERS|SHED_CAP')
    out=[]
    for k,v in c.items():
        if ex.search(k):continue
        st=1 if type(v)==int else abs(v)*.1 if v else .1
        for s in (-1,1):out.append(dict(target=k,old=v,new=v+s*st))
    return out
def panel(jobs,agents,oid,op,seeds):
    for v,p in agents:
        for s in seeds:
            for t in (0,1):jobs.append([v,p,oid,op,s,t])
if sys.argv[1]=='screen':
    src=Path(PARENT).read_bytes();vs=[]
    for i,c in enumerate(specs(src)):
        txt='\n# Frozen EXP-029 wrapper; parent bytes above are unchanged.\n_EXP029_ENTRY = [v for v in globals().values() if callable(v)][-1]\n'
        txt+=f"{c['target']} = {c['new']!r}\ndef exp029_entry(obs, configuration=None):\n    return _EXP029_ENTRY(obs, configuration)\n"
        b=src+txt.encode();p=OUT/'variants'/f'd{i:03}.py';p.write_bytes(b);compile(b,str(p),'exec')
        vs.append(dict(id=f'd{i:03}',path=str(p),sha256=hashlib.sha256(b).hexdigest(),change=c))
    json.dump(vs,open(OUT/'variants.json','w'),indent=1)
    jobs=[];ag=[('P',PARENT)]+[(v['id'],v['path']) for v in vs]
    panel(jobs,ag,'O1-self',O1,range(13000,13005));panel(jobs,ag,'O2-127ed3e6',O2,range(13000,13005))
    json.dump(jobs,open(OUT/'jobs-screen.json','w'));print('variants',len(vs),'jobs',len(jobs))
else:
    s=json.load(open(OUT/'screen-summary.json'));sel=s['advance'];assert sel,'NO_ADVANCE'
    v={x['id']:x for x in json.load(open(OUT/'variants.json'))};jobs=[];ag=[('P',PARENT)]+[(i,v[i]['path']) for i in sel]
    panel(jobs,ag,'O1-self',O1,range(13100,13130));panel(jobs,ag,'O2-127ed3e6',O2,range(13100,13130))
    json.dump(jobs,open(OUT/'jobs-stage2.json','w'));print('stage2 jobs',len(jobs))
