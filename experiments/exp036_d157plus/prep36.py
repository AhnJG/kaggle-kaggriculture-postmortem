"""EXP-036 (Claude 09-27 22:00 KST): +-1 constant screen on d157 (submitted 56607884) for the 2nd slot. stdlib; repo root.
python experiments/exp036_d157plus/prep36.py screen  -> variants, jobs-screen-{kaggle,mac}.json (tape panel, 50 tapes)
python experiments/exp036_d157plus/prep36.py stage2  -> jobs-stage2-{kaggle,mac}.json (top<=8: 300 held-out tapes + EXP-032 closed-loop panels)"""
import ast,re,math,json,hashlib,sys,random
from pathlib import Path
OUT=Path('experiments/exp036_d157plus');(OUT/'variants').mkdir(parents=True,exist_ok=True)
BASE='releases/exp035-d157/main.py';TD='experiments/exp033_tapes'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BASE).startswith('94a46c11')
meta={m['episode']:m for m in json.load(open(f'{TD}/meta.json'))}
d157={}
for l in open(f'{TD}/games-cloud.jsonl'):
    r=json.loads(l)
    if r['vid']=='d157':d157[int(r['opponent'][1:])]=r
assert len(d157)==350
def tapejob(v,p,e):m=meta[e];return [v,p,f'T{e}',f'{TD}/tapes/T{e}.py',m['seed'],m['seat']]
def split(jobs,name):
    k=[j for i,j in enumerate(jobs) if i%5<3];m=[j for i,j in enumerate(jobs) if i%5>=3]
    json.dump(k,open(OUT/f'jobs-{name}-kaggle.json','w'));json.dump(m,open(OUT/f'jobs-{name}-mac.json','w'));print(name,len(jobs),'kaggle',len(k),'mac',len(m))
# frozen screen tape set: d157 non-wins vs LB>=2200 opponents (<=35, by episode hash) + 15 wins vs LB>=2200
hi=[e for e,m in meta.items() if m['op_lb'] and float(m['op_lb'])>=2200]
H=lambda e:hashlib.sha256(f'exp036-{e}'.encode()).hexdigest()
nw=sorted([e for e in hi if d157[e]['score']<1],key=H)[:35];w=sorted([e for e in hi if d157[e]['score']==1],key=H)[:15]
SCREEN=sorted(nw+w);HOLD=sorted(e for e in meta if e not in SCREEN)
if sys.argv[1]=='screen':
    src=Path(BASE).read_bytes();t=ast.parse(src.decode());c={}
    for n in t.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and re.fullmatch(r'_?[A-Z][A-Z0-9_]{2,}',n.targets[0].id):
            try:v=ast.literal_eval(n.value)
            except Exception:continue
            if type(v) in (int,float) and math.isfinite(v):c[n.targets[0].id]=v
    ex=re.compile(r'GOOSE|COOP|EGG|QUAD|LAND|ADV_LOOK|ADVANCE|LEAD|STARTER|PPO|CLEAN|WEED|TURNS_PER_DAY|LAST_STEP|MAX_ORDERS|SHED_CAP')
    specs=[]
    for k,v in c.items():
        if ex.search(k):continue
        st=1 if type(v)==int else abs(v)*.1 if v else .1
        for s in (-1,1):specs.append(dict(target=k,old=v,new=v+s*st))
    vs=[]
    for i,cc in enumerate(specs):
        txt='\n# Frozen EXP-036 wrapper; parent (d157) bytes above are unchanged.\n_EXP036_ENTRY = [v for v in globals().values() if callable(v)][-1]\n'
        txt+=f"{cc['target']} = {cc['new']!r}\ndef exp036_entry(obs, configuration=None):\n    return _EXP036_ENTRY(obs, configuration)\n"
        b=src+txt.encode();p=OUT/'variants'/f'e{i:03}.py';p.write_bytes(b);compile(b,str(p),'exec')
        vs.append(dict(id=f'e{i:03}',path=str(p),sha256=hashlib.sha256(b).hexdigest(),change=cc))
    json.dump(vs,open(OUT/'variants.json','w'),indent=1);json.dump(dict(screen=SCREEN,holdout=HOLD),open(OUT/'tape-split.json','w'))
    split([tapejob(v['id'],v['path'],e) for v in vs for e in SCREEN],'screen');print('variants',len(vs),'screen tapes',len(SCREEN),'nonwin',len(nw))
else:
    sel=json.load(open(OUT/'screen-summary.json'))['advance'];assert sel,'NO_ADVANCE'
    V={v['id']:v for v in json.load(open(OUT/'variants.json'))};jobs=[]
    D='releases/public-dpnew-55be5d5f-exact/main.py';P='releases/round2-v074/main.py';O2='releases/public-newmeta-127ed3e6-exact/main.py'
    guard=[g for g in json.load(open('experiments/exp027_stage3/manifest.json'))['guard'] if not g['sha256'].startswith('55be5d5f')]
    for i in sel:
        p=V[i]['path'];jobs+=[tapejob(i,p,e) for e in HOLD]
        for oid,op,ss in (('V074',P,range(14100,14150)),('O127',O2,range(14100,14150)),('D',D,range(14300,14350))):
            jobs+=[[i,p,oid,op,s,t] for s in ss for t in (0,1)]
        for g in guard:jobs+=[[i,p,g['id'],g['path'],s,t] for s in range(14200,14210) for t in (0,1)]
    split(jobs,'stage2')
