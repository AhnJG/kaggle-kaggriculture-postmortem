"""EXP-053 (Claude 09-29): tomato usage by 2400+ teams (exp041 raw, 750 games) and their opponents."""
import json,gzip,os,collections
from multiprocessing import Pool
RAW='private_artifacts/top2400_20260928/raw/';OUT='analysis/exp053_tomato/tom53.jsonl'
TS=('PIZZA_SHOP','FARMERS_MARKET')
def units(a):
    a=a or {};return [a.get('farmer')]+list(a.get('hands') or [])
def one(m):
    try:raw=json.load(gzip.open(f"{RAW}{m['episode']}.json.gz"))
    except Exception:return None
    st=raw['steps'];sh=st[-1][0]['observation']['town']['unlocked_shops']
    res={'episode':m['episode'],'team':m['team'],'ts18':sum(s in TS for s in sh[:6]),'ts_all':sum(s in TS for s in sh),'shops':sh}
    for side,s in (('top',m['target_seat']),('opp',m['our_seat'])):
        plants=[];seeds=0;land=[];tom_tiles=collections.Counter()
        for t in range(1,len(st)):
            a=st[t][s]['action'] or {}
            for u in units(a):
                if isinstance(u,list) and u[:2]==['PLANT','TOMATO']:plants.append(t)
            for o in (a.get('market') or [])[:10]:
                if isinstance(o,list) and o[:2]==['BUY_SEED','TOMATO'] and len(o)>2:seeds+=int(o[2])
                if isinstance(o,list) and o[:1]==['BUY_LAND']:land.append(t)
        for T in (360,480,576,648):
            f=st[T][0]['observation']['farms'][s]
            tom_tiles[T]=sum(1 for row in f['tiles'] for x in row if isinstance(x,dict) and x.get('crop')=='TOMATO')
        res[side]={'plants':len(plants),'first_plant':min(plants) if plants else None,'plant_days':sorted({p//24 for p in plants}),'seeds':seeds,'land':land,'tiles':dict(tom_tiles),'reward':st[-1][s]['reward']}
    p=st[-1][0]['observation']['market']['prices'];res['tomato_price_end']=p['TOMATO'];res['tomato_price_600']=st[600][0]['observation']['market']['prices']['TOMATO']
    return res
if __name__=='__main__':
    M=list({m['episode']:m for m in json.load(open('experiments/exp041_top2400/meta.json'))}.values())
    done={json.loads(l)['episode'] for l in open(OUT)} if os.path.exists(OUT) else set()
    todo=[m for m in M if m['episode'] not in done];print('todo',len(todo),flush=True)
    with Pool(4) as p,open(OUT,'a') as f:
        for x in p.imap_unordered(one,todo):
            if x:f.write(json.dumps(x)+'\n');f.flush()
