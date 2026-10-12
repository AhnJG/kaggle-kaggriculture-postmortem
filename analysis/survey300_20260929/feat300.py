"""SURVEY300 features per game & seat (Claude 09-29, per PLAN.md): exact replay with commit/hire/land hooks + tile snapshots."""
import sys,glob,os,json,gzip,contextlib,io,importlib,collections
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from multiprocessing import Pool
RAW='private_artifacts/survey300_20260929/raw/';OUT='analysis/survey300_20260929/feat300.jsonl'
def snap(f):
    c=collections.Counter()
    for row in f['tiles']:
        for t in row:
            if isinstance(t,dict):
                if t.get('crop'):c['C_'+t['crop']]+=1
                if t.get('animal'):c['A_'+t['animal']]+=1
    return dict(c)
def one(eid):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            from kaggle_environments import make
            E=importlib.import_module("kaggle_environments.envs.kaggriculture.kaggriculture")
        raw=json.load(gzip.open(f"{RAW}{eid}.json.gz"));st=raw['steps']
        tape=[[s[k]['action'] for s in st[1:]] for k in (0,1)]
        C=collections.defaultdict(lambda:[0,0]);ctx={}
        om,oc,oh,ol=E._process_market,E._commit_unit,E._do_hire,E._do_buy_land
        def market(state,env):ctx['step']=int(state[0].observation.step);ctx['farms']=state[0].observation.farms;return om(state,env)
        def sd(farm):return 0 if farm is ctx['farms'][0] else 1
        def commit(op,item,price,farm,private,book,cap=100):
            ok=oc(op,item,price,farm,private,book,cap)
            if ok:g=C[(sd(farm),op,item)];g[0]+=1;g[1]+=price
            return ok
        def hire(farm,*a,**k):
            b=farm['money'];x=oh(farm,*a,**k);g=C[(sd(farm),'HIRE','-')];g[0]+=1;g[1]+=b-farm['money'];return x
        def land(farm,*a,**k):
            b=farm['money'];x=ol(farm,*a,**k)
            if b!=farm['money']:C[(sd(farm),'LANDDAY',str(ctx.get('step',0)//24))][0]+=1
            return x
        E._process_market,E._commit_unit,E._do_hire,E._do_buy_land=market,commit,hire,land
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(raw['info']['seed'])})
                env.run([lambda o,c:tape[0][int(o['step'])],lambda o,c:tape[1][int(o['step'])]])
        finally:E._process_market,E._commit_unit,E._do_hire,E._do_buy_land=om,oc,oh,ol
        rw=[st[-1][i]['reward'] for i in (0,1)];par=[x.reward for x in env.steps[-1]]==rw
        out={'episode':eid,'parity':par,'rewards':rw,'teams':raw['info'].get('TeamNames'),'shops':st[-1][0]['observation']['town']['unlocked_shops'],'seat':{}}
        for s in (0,1):
            f={'snap288':snap(st[288][0]['observation']['farms'][s]),'snap576':snap(st[576][0]['observation']['farms'][s]),
               'flows':{f'{op}|{it}':v for (se,op,it),v in C.items() if se==s}}
            out['seat'][s]=f
        return out
    except Exception as e:return {'episode':eid,'error':repr(e)[:200]}
if __name__=='__main__':
    E=json.load(open('analysis/survey300_20260929/episodes_all.json'))
    ids=sorted({e['id'] for e in E if os.path.exists(f"{RAW}{e['id']}.json.gz")})
    done={json.loads(l)['episode'] for l in open(OUT)} if os.path.exists(OUT) else set()
    todo=[i for i in ids if i not in done];print('todo',len(todo),'of',len(ids),flush=True)
    with Pool(4) as p,open(OUT,'a') as f:
        for x in p.imap_unordered(one,todo):f.write(json.dumps(x)+'\n');f.flush()
