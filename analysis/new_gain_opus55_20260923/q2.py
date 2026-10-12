import json, collections, statistics as st
SHOPS={"BAKERY":["EGG","WHEAT"],"PIZZA_SHOP":["MILK","TOMATO","WHEAT"],"BRUNCH_SPOT":["EGG","WHEAT","STRAWBERRY"],"YARN_STORE":["WOOL"],
"ICE_CREAM_SHOP":["STRAWBERRY","MILK","WHEAT"],"PET_CAFE":["CARROT"],"SMOOTHIE_SHOP":["STRAWBERRY","MILK"],"FARMERS_MARKET":["WHEAT","CARROT","TOMATO","STRAWBERRY"]}
ITEMS=["WHEAT","CARROT","STRAWBERRY","TOMATO","MELON","EGG","MILK","WOOL","FERTILIZER"]
WIN={'d0-11':(0,11),'d12-18':(12,18),'d19-29':(19,29)}
def shops_on(shops,day):
    k=str(day) if str(day) in shops else day
    if k in shops: return shops[k]
    ks=sorted(int(x) for x in shops); prev=[x for x in ks if x<=day]
    return shops[str(prev[-1]) if str(prev[-1]) in shops else prev[-1]] if prev else []
def demand(shops,item,d0,d1):
    tot=0
    for step in range(d0*24,(d1+1)*24):
        if step%4: continue
        for s in shops_on(shops,step//24):
            p=SHOPS[s]
            if item in p: tot+= 2 if len(p)==1 else 1
    return tot
def sums(lst,d0,d1):
    out=collections.Counter()
    for d,item,v in lst:
        if d0<=d<=d1: out[item]+=v
    return out
def game(r,seat):
    g={}
    for w,(a,b) in WIN.items():
        g[w]=dict(h=sums(r['harvest'][seat],a,b),s=sums(r['sell'][seat],a,b),rev=sums(r['rev'][seat],a,b),
                  dem={i:demand(r['shops'],i,a,b) for i in ITEMS})
    g['reward']=r['rewards'][seat]; g['opp']=r['rewards'][1-seat]
    return g
H=[json.loads(l) for l in open('resim_hosted.jsonl')]
L={tuple(json.loads(l)['pair']):json.loads(l) for l in open('exp17_local.jsonl')}
G=collections.defaultdict(list)
for r in H:
    G[r['team']].append(game(r,r['seat']))
    if r['team']=='DSM':
        pair=tuple(r['shops']['6'][:2]); e=L[pair]; G['E17(paired)'].append(game(e,e['exp17_seat']))
json.dump({k:v for k,v in G.items()},open('q2_games.json','w'))
teams=['DSM','Majkel1337','M & M & P & Q','E17(paired)']
for w in WIN:
    print('==',w,'  harvest u / sold u / revenue / avg price')
    for i in ITEMS:
        line=[]
        for t in teams:
            gs=G[t]; h=st.mean(g[w]['h'][i] for g in gs); s=st.mean(g[w]['s'][i] for g in gs); rv=st.mean(g[w]['rev'][i] for g in gs)
            line.append(f"{h:6.1f}/{s:6.1f}/{rv:8.0f}/{(rv/s if s else 0):5.1f}")
        print(f"{i:11s}",' | '.join(line))
    for t in teams:
        print('  total rev',t, round(st.mean(sum(g[w]['rev'].values()) for g in G[t])))
for t in teams: print('final',t,round(st.mean(g['reward'] for g in G[t])))
