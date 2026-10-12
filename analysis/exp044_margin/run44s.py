"""EXP-044s per-step SELL of 6 items (Claude 09-28 21:00 KST): margin decomposition. d157 in our_seat vs 2400+ select-team tapes (holdout excluded).
Hooks _commit_unit/_do_hire/_do_buy_land -> per (seat, quarter, op, item) units & cash. Reward = final money, so margin = sum of cash flows."""
import sys,glob,os,json,contextlib,io,importlib,time
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from collections import defaultdict
from multiprocessing import Pool
B='experiments/exp041_top2400/'
BOT=os.environ.get('BOT','releases/exp035-d157/main.py');OUT=os.environ.get('OUT','analysis/exp044_margin/d157_steps.jsonl')
def play(m):
    with contextlib.redirect_stdout(io.StringIO()):
        from kaggle_environments import make
        from kaggle_environments.agent import get_last_callable
        E=importlib.import_module("kaggle_environments.envs.kaggriculture.kaggriculture")
    o=f"X{m['episode']}";seat=m['our_seat'];C=defaultdict(lambda:[0,0]);ctx={}
    om,oc,oh,ol=E._process_market,E._commit_unit,E._do_hire,E._do_buy_land
    def market(state,env):
        ctx['step']=int(state[0].observation.step);ctx['farms']=state[0].observation.farms;return om(state,env)
    def sidx(farm):
        fs=ctx.get('farms');return 0 if fs is not None and farm is fs[0] else 1
    def commit(op,item,price,farm,private,book,shed_capacity=100):
        ok=oc(op,item,price,farm,private,book,shed_capacity)
        if ok and op=='SELL' and item in ('WOOL','MILK','STRAWBERRY','TOMATO','CARROT','EGG'):
            g=C[(sidx(farm),ctx['step'],op,item)];g[0]+=1;g[1]+=price
        return ok
    def hire(farm,*a,**k):
        b=farm['money'];r=oh(farm,*a,**k);g=C[(sidx(farm),min(3,ctx.get('step',0)//180),'HIRE','-')];g[0]+=1;g[1]+=b-farm['money'];return r
    def land(farm,*a,**k):
        b=farm['money'];r=ol(farm,*a,**k);g=C[(sidx(farm),min(3,ctx.get('step',0)//180),'LAND','-')];g[0]+=1;g[1]+=b-farm['money'];return r
    E._process_market,E._commit_unit,E._do_hire,E._do_buy_land=market,commit,hire,land
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            me=get_last_callable(open(BOT).read(),path=BOT);op=get_last_callable(open(B+f'tapes/{o}.py').read(),path=B+f'tapes/{o}.py')
            env=make("kaggriculture",configuration={"episodeSteps":720,"seed":m['seed']})
            env.run([me,op] if seat==0 else [op,me])
        rw=[s.reward for s in env.steps[-1]];err=None
    except Exception as e:
        rw=None;err=repr(e)[:300]
    finally:
        E._process_market,E._commit_unit,E._do_hire,E._do_buy_land=om,oc,oh,ol
    return {'tape':o,'team':m['team'],'seed':m['seed'],'our_seat':seat,'rewards':rw,'err':err,
            'groups':[[s,q,op_,it,v[0],v[1]] for (s,q,op_,it),v in sorted(C.items())]}
if __name__=='__main__':
    H=set(json.load(open(B+'team-split.json'))['holdout_teams'])
    M=list({m['episode']:m for m in json.load(open(B+'meta.json'))}.values())
    M=[m for m in M if m['team'] not in H]
    done=set(json.loads(l)['tape'] for l in open(OUT)) if os.path.exists(OUT) else set()
    todo=[m for m in M if f"X{m['episode']}" not in done];print('todo',len(todo),'of',len(M),flush=True)
    with Pool(4) as p,open(OUT,'a') as f:
        for r in p.imap_unordered(play,todo):f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush()
