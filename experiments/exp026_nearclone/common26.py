"""EXP-026 (Claude): v074 +-1 variants vs near-clone TAPES (open-loop). Run from repo root."""
import ast,re,math,json,hashlib,itertools,os,gzip,io,contextlib,time,traceback
ROOT='.'
PARENT='releases/round2-v074/main.py'
PARENT_SHA='860a502c36f9a9f700c93125e6828f41378f50d74fa130f62a09f911316ea19c'
OUT='experiments/exp026_nearclone'
RAW='private_artifacts/exp025b_nearclone/raw/'
def sha(p):return hashlib.sha256(open(p,'rb').read()).hexdigest()
def mutation_specs(source):
    tree=ast.parse(source);constants={};aliases={};defs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    for n in tree.body:
        if not isinstance(n,ast.Assign) or len(n.targets)!=1 or not isinstance(n.targets[0],ast.Name):continue
        name=n.targets[0].id
        if isinstance(n.value,ast.Name) and name.endswith('_PARENT'):aliases[name]=n.value.id
        if not re.fullmatch(r'_?[A-Z][A-Z0-9_]{2,}',name):continue
        try:value=ast.literal_eval(n.value)
        except (ValueError,TypeError):continue
        if type(value) in (int,float) and math.isfinite(value):constants[name]=value
    excluded=re.compile(r'GOOSE|COOP|EGG|QUAD|LAND|ADV_LOOK|ADVANCE|LEAD|STARTER|PPO|CLEAN|WEED|TURNS_PER_DAY|LAST_STEP|MAX_ORDERS|SHED_CAP')
    specs=[]
    for name,value in constants.items():
        if excluded.search(name):continue
        step=1 if type(value)==int else abs(value)*.1 if value else .1
        for sign in (-1,1):specs.append(dict(kind='constant',target=name,old=value,new=value+sign*step))
    return specs  # layer-off variants excluded (15/44 crashed in EXP-024; none advanced)
def gen():
    src=open(PARENT,'rb').read();assert hashlib.sha256(src).hexdigest()==PARENT_SHA
    specs=mutation_specs(src);os.makedirs(OUT+'/variants',exist_ok=True);out=[]
    for i,c in enumerate(specs):
        text='\n# Frozen EXP-026 wrapper; parent bytes above are unchanged.\n_EXP026_ENTRY = [v for v in globals().values() if callable(v)][-1]\n'
        text+=c['target']+' = '+repr(c['new'])+'\n'
        text+='def exp026_entry(obs, configuration=None):\n    return _EXP026_ENTRY(obs, configuration)\n'
        b=src+text.encode();p=f'{OUT}/variants/w{i:03}.py';open(p,'wb').write(b);compile(b,p,'exec')
        out.append(dict(id=f'w{i:03}',path=p,sha256=hashlib.sha256(b).hexdigest(),change=c))
    json.dump(out,open(OUT+'/variants.json','w'),indent=1);return out
def split():
    v=[x for x in json.load(open('analysis/exp025b_nearclone/tapes_verified.json')) if x.get('valid')]
    v.sort(key=lambda x:hashlib.sha256(str(x['episode']).encode()).hexdigest())
    s={'screen':v[:40],'stage2':v[40:200],'reserve':v[200:]}
    json.dump({k:[x['episode'] for x in w] for k,w in s.items()},open(OUT+'/tape-split.json','w'),indent=1);return s
def play(job):
    """job=(vid,path,episode,nearclone_seat). Our seat = 1-nearclone_seat. Near-clone side replays its recorded actions."""
    vid,path,ep,ns=job;from kaggle_environments import make;from kaggle_environments.agent import get_last_callable
    t0=time.time();acts=[];errs=[];maxs=0.0;err=None
    try:
        raw=json.load(gzip.open(f'{RAW}{ep}.json.gz'));seed=int(raw['info']['seed'])
        tape=[raw['steps'][k+1][ns]['action'] for k in range(len(raw['steps'])-1)]
        with contextlib.redirect_stdout(io.StringIO()):
            me=get_last_callable(open(path).read(),path=path)
            def A(obs,cfg):
                nonlocal maxs
                s=time.perf_counter()
                try:a=me(obs,cfg)
                except Exception:errs.append(traceback.format_exc()[-500:]);raise
                maxs=max(maxs,time.perf_counter()-s);acts.append(json.dumps(a,sort_keys=True,default=str));return a
            def T(obs,cfg):return tape[int(obs['step'])]
            env=make('kaggriculture',configuration={'episodeSteps':720,'seed':seed})
            env.run([T,A] if ns==0 else [A,T])
        last=env.steps[-1];rw=[s.reward for s in last];st=[s.status for s in last];me_=1-ns
        m=rw[me_]-rw[ns] if None not in rw else None;sc=None if m is None else (1.0 if m>0 else 0.0 if m<0 else 0.5)
    except Exception:rw=st=m=sc=None;err=traceback.format_exc()[-500:]
    return dict(key=f'{vid}|{ep}',vid=vid,episode=ep,rewards=rw,statuses=st,margin=m,score=sc,max_step=maxs,
                act_sha=hashlib.sha256('\n'.join(acts).encode()).hexdigest(),action_count=len(acts),agent_errors=errs,err=err,sec=round(time.time()-t0,2))
def invalid(r):return r['err'] is not None or r['statuses']!=['DONE','DONE'] or bool(r['agent_errors']) or r['action_count']!=719 or r['score'] is None
def run(jobs,out,workers=5):
    from multiprocessing import Pool
    done=set()
    if os.path.exists(out):done={json.loads(l)['key'] for l in open(out)}
    todo=[j for j in jobs if f'{j[0]}|{j[2]}' not in done]
    with Pool(workers) as p,open(out,'a') as f:
        for r in p.imap_unordered(play,todo):f.write(json.dumps(r)+'\n');f.flush()
