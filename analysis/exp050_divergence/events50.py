"""Classify deviation events (opponent actual vs 55be-on-their-obs) in d157 hosted games vs 55be-labelled opponents."""
import sys,glob,os,json,gzip,contextlib,io,csv,collections
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from kaggle_environments.utils import structify
from multiprocessing import Pool
P='releases/public-dpnew-55be5d5f-exact/main.py';OUT='analysis/exp050_divergence/events50b.jsonl'
def mk(a):return [tuple(o) for o in ((a or {}).get('market') or [])[:10] if isinstance(o,list) and o]
def one(r):
    try:return _one(r)
    except Exception as ex:
        import traceback;return {'episode':r['episode'],'result':r['result'],'error':traceback.format_exc()[-300:],'events':[]}
def _one(r):
    raw=json.load(gzip.open(f"private_artifacts/c26_hosted_20260929/raw/{r['episode']}.json.gz"));s=1-int(r['seat']);ns={'__name__':'x'}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(open(P).read(),P,'exec'),ns)
    ag=ns['kaggle_submission_agent'];cfg=structify(raw['configuration']);ev=[]
    for t in range(len(raw['steps'])-1):
        o=json.loads(json.dumps(raw['steps'][t][s]['observation']))
        for k in ('step','farms','market','town'):
            if k not in o:o[k]=raw['steps'][t][0]['observation'][k]
        with contextlib.redirect_stdout(io.StringIO()):p=ag(structify(o),cfg) or {}
        a=raw['steps'][t+1][s]['action'] or {}
        pm,am=mk(p),mk(a);pu=[p.get('farmer')]+list(p.get('hands') or []);au=[a.get('farmer')]+list(a.get('hands') or [])
        if pm==am and pu==au:continue
        e={'t':t}
        if pm!=am:
            if sorted(pm)==sorted(am):
                e['kind']='reorder'
                pi={x:i for i,x in enumerate(pm)};moved=[(pi[x]-i,x) for i,x in enumerate(am) if x in pi]
                up=max(moved) if moved else (0,('',''));e['up']=list(up[1][:2]) if up[0]>0 else None;e['up_by']=up[0]
                e['us_item_sold_same_step']=None
            else:e['kind']='market_change';e['p']=pm;e['a']=am
        if pu!=au:e['units']=True
        # did the other seat (d157) sell the moved item this step, and at which slot?
        us=mk(raw['steps'][t+1][1-s]['action'])
        if e.get('up') and len(e['up'])==2:
            e['us_slot']=next((i for i,x in enumerate(us) if x[0]=='SELL' and x[1]==e['up'][1]),None)
            e['their_slot']=next((i for i,x in enumerate(am) if x[0]=='SELL' and x[1]==e['up'][1]),None)
        ev.append(e)
    return {'episode':r['episode'],'result':r['result'],'op':r['op_team'],'margin':float(r['margin']),'events':ev}
if __name__=='__main__':
    R=[r for r in csv.DictReader(open('analysis/c26_hosted_20260929/opponents.csv')) if r['submission_label']=='d157' and '55be' in r['label'] and r['result']!='D']
    done={json.loads(l)['episode'] for l in open(OUT)} if os.path.exists(OUT) else set()
    todo=[r for r in R if r['episode'] not in done];print('todo',len(todo),flush=True)
    with Pool(4) as p,open(OUT,'a') as f:
        for x in p.imap_unordered(one,todo):f.write(json.dumps(x)+'\n');f.flush()
