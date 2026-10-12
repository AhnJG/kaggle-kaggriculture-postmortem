import json,gzip,csv,collections,statistics as st,sys
from multiprocessing import Pool
IT=('TOMATO','CARROT','EGG','STRAWBERRY','MILK','WOOL','MELON','WHEAT')
def one(ep):
    raw=json.load(gzip.open(f"private_artifacts/c26_hosted_20260929/raw/{ep}.json.gz"))
    o=raw['steps'][-1][0]['observation'];sh=o['town']['unlocked_shops']
    out={'nt':sum(1 for x in sh if x in('PIZZA_SHOP','FARMERS_MARKET')),'shops':sh,'p':{},'d':{}}
    for T in (240,360,480,600,700):
        m=raw['steps'][T][0]['observation']['market'];out['p'][T]={i:m['prices'][i] for i in IT};out['d'][T]=10000-m['inventory']['TOMATO']
    return out
if __name__=='__main__':
    R=list(csv.DictReader(open('analysis/c26_hosted_20260929/opponents.csv')))[::3]
    with Pool(4) as p:X=p.map(one,[r['episode'] for r in R])
    json.dump(X,open('analysis/exp052_oracle/market52.json','w'))
    print('games',len(X),'tomato-shop instances',collections.Counter(x['nt'] for x in X))
    for it in IT:print(f'{it:10s}',{T:(round(st.median([x["p"][T][it] for x in X])),round(max(x["p"][T][it] for x in X))) for T in (240,360,480,600,700)},'(median,max)')
    for has in (0,1):
        G=[x for x in X if (x['nt']>0)==bool(has)]
        if G:print('has tomato shop' if has else 'no tomato shop',len(G),'TOMATO price median',{T:round(st.median(x['p'][T]['TOMATO'] for x in G)) for T in (360,480,600,700)},'deficit',{T:round(st.median(x['d'][T] for x in G)) for T in (360,600,700)})
