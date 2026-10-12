"""EXP-050 divergence (Claude 09-29): hosted d157 games vs 55be-labelled opponents. Feed the opponent's own recorded obs to 55be exact
each step; where the opponent's actual action differs, tally market (op,item) quantity differences and farmer/hand command differences."""
import sys,glob,os,json,gzip,contextlib,io,collections,csv
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from kaggle_environments.utils import structify
from multiprocessing import Pool
BOT='releases/public-dpnew-55be5d5f-exact/main.py';OUT='analysis/exp050_divergence/div50.jsonl'
def mk(a):
    d=collections.Counter()
    for o in ((a or {}).get('market') or [])[:10]:
        if isinstance(o,list) and o:
            if o[0] in('HIRE','BUY_LAND'):d[(o[0],'-')]+=1
            elif len(o)>=3:
                try:d[(o[0],o[1])]+=int(o[2])
                except:pass
    return d
def cmds(a):
    a=a or {};c=collections.Counter()
    for u in [a.get('farmer')]+list(a.get('hands') or []):
        if isinstance(u,list) and u:c[str(u[0])+(':'+str(u[1]) if len(u)>1 and u[0] in('PLANT','PICKUP','PLACE','BUILD_PASTURE','BUILD_COOP') else '')]+=1
    return c
def one(r):
    raw=json.load(gzip.open(f"private_artifacts/c26_hosted_20260929/raw/{r['episode']}.json.gz"))
    s=1-int(r['seat']);ns={'__name__':'p55'}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(open(BOT).read(),BOT,'exec'),ns)
    ag=ns['kaggle_submission_agent'];cfg=structify(raw['configuration'])
    md=collections.Counter();cd=collections.Counter();first=None;nd=0;err=0
    for t in range(len(raw['steps'])-1):
        o=json.loads(json.dumps(raw['steps'][t][s]['observation']))
        for k in ('step','farms','market','town'):
            if k not in o:o[k]=raw['steps'][t][0]['observation'][k]
        try:
            with contextlib.redirect_stdout(io.StringIO()):p=ag(structify(o),cfg)
        except Exception:err+=1;continue
        a=raw['steps'][t+1][s]['action']
        pm,am=mk(p),mk(a)
        if pm!=am or cmds(p)!=cmds(a):
            nd+=1;first=t if first is None else first
            q=min(3,t//180)
            for k in set(pm)|set(am):
                if am[k]!=pm[k]:md[f"{k[0]}|{k[1]}|Q{q}"]+=am[k]-pm[k]
            pc,ac=cmds(p),cmds(a)
            for k in set(pc)|set(ac):
                if ac[k]!=pc[k]:cd[f"{k}|Q{q}"]+=ac[k]-pc[k]
    return {'episode':r['episode'],'result':r['result'],'op':r['op_team'],'prefix':int(r['prefix_len']),'first':first,'ndiff':nd,'err':err,'mk':md,'cmd':cd,'margin':float(r['margin'])}
if __name__=='__main__':
    R=[r for r in csv.DictReader(open('analysis/c26_hosted_20260929/opponents.csv')) if r['submission_label']=='d157' and '55be' in r['label']]
    done={json.loads(l)['episode'] for l in open(OUT)} if os.path.exists(OUT) else set()
    todo=[r for r in R if r['episode'] not in done and int(r['episode']) not in done];print('todo',len(todo),flush=True)
    with Pool(4) as p,open(OUT,'a') as f:
        for x in p.imap_unordered(one,todo):f.write(json.dumps(x)+'\n');f.flush()
