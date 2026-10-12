"""EXP-062: first divergence of band 55be-variant opponents vs public 55be (closed-loop re-sim with our bot, same seed/seat)."""
import sys,os,json,gzip,csv,contextlib,io
from multiprocessing import Pool
BOT={'d157':'releases/exp035-d157/main.py','d157r':'releases/exp035-d157/main.py','X':'releases/slot2r-Rc26_107/main.py','c26':'releases/exp039-c26/main.py'}
D55='releases/public-dpnew-55be5d5f-exact/main.py'
RAWS=['hosted_0930c','hosted_x0930','hosted_20260930','hosted_20260929b','hosted_20260929pm','c26_hosted_20260929','d157_hosted_20260928']
def rawpath(e):
    for d in RAWS:
        p=f"private_artifacts/{d}/raw/{e}.json.gz"
        if os.path.exists(p): return p
def one(r):
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
    p=int(r['prefix_len']); s=int(r['seat']); o=1-s
    raw=json.load(gzip.open(rawpath(r['episode'])))
    rec=[st[o]['action'] for st in raw['steps'][1:]]
    recme=[st[s]['action'] for st in raw['steps'][1:]]
    with contextlib.redirect_stdout(io.StringIO()):
        me=get_last_callable(open(BOT[r['submission_label']]).read(),path=BOT[r['submission_label']])
        op=get_last_callable(open(D55).read(),path=D55)
        acts=[]
        def wrap(obs,cfg):
            a=op(obs,cfg); acts.append(a); return a
        env=make('kaggriculture',configuration={'episodeSteps':p+2,'seed':int(raw['info']['seed'])})
        env.run([me,wrap] if s==0 else [wrap,me])
    out={'episode':r['episode'],'sub':r['submission_label'],'result':r['result'],'margin':int(r['margin']),'prefix':p,'op_lb':r['op_lb_score'],'op':r['op_team'],
         'pub55':acts[p] if p<len(acts) else None,'var':rec[p] if p<len(rec) else None,'me_at':recme[p] if p<len(recme) else None,
         'var_next':rec[p+1:p+4],'pub_next':acts[p+1:p+4]}
    return out
if __name__=='__main__':
    rows={}
    for d in ['hosted_20260929pm','hosted_20260929b','hosted_20260930','hosted_x0930','hosted_0930c']:
        for r in csv.DictReader(open(f'analysis/{d}/opponents.csv')): rows[r['episode']]=r
    R=[r for r in rows.values() if 1750<=float(r['op_lb_score'] or 0)<2250 and '55be' in r['label'] and r['is_full']!='True' and int(r['prefix_len'])>0]
    O='experiments/exp062/loss/firstdiv62.jsonl'
    done={json.loads(l)['episode'] for l in open(O)} if os.path.exists(O) else set()
    todo=[r for r in R if r['episode'] not in done]
    print('todo',len(todo),flush=True)
    with Pool(7) as P,open(O,'a') as f:
        for x in P.imap_unordered(one,todo): f.write(json.dumps(x,default=str)+'\n'); f.flush()
