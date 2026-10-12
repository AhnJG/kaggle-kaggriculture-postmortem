import sys,glob,os,json,gzip,contextlib,io,csv
sys.path.append(glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[0])
from multiprocessing import Pool
P='releases/exp035-d157/main.py'
def one(r):
    ns={'__name__':'x'}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(open(P).read(),P,'exec'),ns)
    raw=json.load(gzip.open(f"private_artifacts/c26_hosted_20260929/raw/{r['episode']}.json.gz"));s=int(r['seat'])
    o=json.loads(json.dumps(raw['steps'][432][s]['observation']))
    for k in ('step','farms','market','town'):
        if k not in o:o[k]=raw['steps'][432][0]['observation'][k]
    f=o['farms'][s]
    return {'episode':r['episode'],'sub':r['submission_label'],'result':r['result'],'rev':round(ns['_cxtb_expected_revenue'](o)),
            'quads':sorted(f['unlocked_quadrants']),'money':f['money'],'se_locked':all(f['tiles'][y][x]=='LOCKED' for y in (5,6) for x in range(5,10)),
            'shops':sum(x in('PIZZA_SHOP','FARMERS_MARKET') for x in o['town']['unlocked_shops'])}
if __name__=='__main__':
    R=list(csv.DictReader(open('analysis/c26_hosted_20260929/opponents.csv')))
    with Pool(4) as p:X=p.map(one,R)
    json.dump(X,open('analysis/exp053_tomato/cxtb53.json','w'))
    import statistics as st,collections
    ok=[x for x in X if x['quads']==['NE','NW','SW'] and x['money']>=12000 and x['se_locked']]
    print('games',len(X),'structural conditions ok',len(ok),'| quads',collections.Counter(tuple(x['quads']) for x in X).most_common(3),'| money<12000',sum(x['money']<12000 for x in X))
    for th in (9000,8000,7000,6000,5000):print(f'  rev>={th}: {sum(x["rev"]>=th for x in ok)} / {len(ok)}')
    print('rev quantiles',[round(q) for q in st.quantiles([x['rev'] for x in ok],n=10)])
