"""Per-game production features for one seat of a replay (Claude, SLOT2-X)."""
import json,gzip,collections
def feats(path, seat):
    r=json.load(gzip.open(path)); st=r['steps']; f=collections.Counter(); land=[]; hires=[]
    for t in range(1,len(st)):
        a=st[t][seat]['action'] or {}; day=(t-1)//24
        for m in a.get('market') or []:
            if not m: continue
            if m[0]=='BUY_LAND': land.append(day)
        units=[a.get('farmer')]+list(a.get('hands') or [])
        for u in units:
            if isinstance(u,list) and u and u[0]=='PLANT' and len(u)>1: f[f'plant_{u[1]}']+=1; f[f'plant_{u[1]}_d{day//6}']+=1
    # hands per day and quadrants/crop tiles at start of selected days
    for d in (5,8,11,14,17,20,23,26):
        o=st[d*24+1][0]['observation']; fm=o['farms'][seat]
        f[f'hands_d{d}']=len(fm['hands']); f[f'quad_d{d}']=len(fm['unlocked_quadrants'])
        for row in fm['tiles']:
            for tl in row:
                if isinstance(tl,dict) and tl.get('kind')=='PLANT': f[f'tile_{tl["crop"]}_d{d}']+=1
                if isinstance(tl,dict) and 'animal' in tl: f[f'ani_{tl["animal"]}_d{d}']+=1
    rw=[st[-1][i]['reward'] for i in (0,1)]
    f['money']=rw[seat]; f['margin']=rw[seat]-rw[1-seat]
    return dict(f), land
