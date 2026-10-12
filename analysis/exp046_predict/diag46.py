"""EXP-046 diagnostic (Claude 09-28 23:50 KST): can public 55be5d5f predict top-team SELL decisions?
Feed the top team's own recorded observation (incl. private) to 55be each step; compare its market SELL orders
with the team's actual next action. Upper bound on predictability (we would not see their private shed in play)."""
import sys,glob,os,json,gzip,contextlib,io,collections
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from kaggle_environments.utils import structify
from multiprocessing import Pool
B='experiments/exp041_top2400/';BOT='releases/public-dpnew-55be5d5f-exact/main.py'
OUT=os.environ.get('OUT','analysis/exp046_predict/diag46.jsonl');MAXS=int(os.environ.get('MAXS','719'))
IT=('WOOL','MILK','STRAWBERRY','EGG','CARROT','TOMATO','WHEAT','FERTILIZER','MELON')
def sells(a):
    d=collections.Counter()
    for o in ((a or {}).get('market') or [])[:10]:
        if isinstance(o,list) and len(o)>=3 and o[0]=='SELL':
            try:d[o[1]]+=int(o[2])
            except:pass
    return d
def one(m):
    raw=json.loads(gzip.decompress(open(f"private_artifacts/top2400_20260928/raw/{m['episode']}.json.gz",'rb').read()))
    s=m['target_seat'];ns={'__name__':'p55'}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(open(BOT).read(),BOT,'exec'),ns)
    ag=ns.get('kaggle_submission_agent') or [v for v in ns.values() if callable(v)][-1]
    cfg=structify({k:v for k,v in raw['configuration'].items()})
    agree=collections.Counter();pred_u=collections.Counter();act_u=collections.Counter();both_u=collections.Counter();err=0
    for t in range(min(MAXS,len(raw['steps'])-1)):
        o=json.loads(json.dumps(raw['steps'][t][s]['observation']))
        for k in ('step','farms','market','town'):
            if k not in o and k in raw['steps'][t][0]['observation']:o[k]=raw['steps'][t][0]['observation'][k]
        obs=structify(o)
        try:
            with contextlib.redirect_stdout(io.StringIO()):p=sells(ag(obs,cfg))
        except Exception:err+=1;p=collections.Counter()
        a=sells(raw['steps'][t+1][s]['action'])
        for i in set(p)|set(a):
            pred_u[i]+=p[i];act_u[i]+=a[i];both_u[i]+=min(p[i],a[i])
            agree[(i,'both' if p[i] and a[i] else 'pred_only' if p[i] else 'act_only')]+=1
    return {'episode':m['episode'],'team':m['team'],'err':err,'pred_u':pred_u,'act_u':act_u,'both_u':both_u,
            'events':{f'{i}|{k}':v for (i,k),v in agree.items()}}
if __name__=='__main__':
    H=set(json.load(open(B+'team-split.json'))['holdout_teams'])
    M=[m for m in list({m['episode']:m for m in json.load(open(B+'meta.json'))}.values()) if m['team'] not in H]
    by=collections.defaultdict(list)
    for m in M:by[m['team']].append(m)
    N=int(sys.argv[1]);S=[]
    for k in range(N):
        for t in sorted(by):
            if k<len(by[t]):S.append(by[t][k])
    done=set(json.loads(l)['episode'] for l in open(OUT)) if os.path.exists(OUT) else set()
    todo=[m for m in S if m['episode'] not in done];print('todo',len(todo),flush=True)
    with Pool(4) as p,open(OUT,'a') as f:
        for r in p.imap_unordered(one,todo):f.write(json.dumps(r)+'\n');f.flush()
