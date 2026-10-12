import json, statistics as st, collections
G=json.load(open('q2_games.json'))
H=[json.loads(l) for l in open('resim_hosted.jsonl')]
L={tuple(json.loads(l)['pair']):json.loads(l) for l in open('exp17_local.jsonl')}
SHOPS={"BAKERY":["EGG","WHEAT"],"PIZZA_SHOP":["MILK","TOMATO","WHEAT"],"BRUNCH_SPOT":["EGG","WHEAT","STRAWBERRY"],"YARN_STORE":["WOOL"],
"ICE_CREAM_SHOP":["STRAWBERRY","MILK","WHEAT"],"PET_CAFE":["CARROT"],"SMOOTHIE_SHOP":["STRAWBERRY","MILK"],"FARMERS_MARKET":["WHEAT","CARROT","TOMATO","STRAWBERRY"]}
def buyers(shops_list,item): return sum(1 for s in shops_list if item in SHOPS[s])
# shop list at day 12 (4 shops) and day 18 (6 shops) for each game
def shopsat(r,d):
    return r['shops'].get(str(d)) or r['shops'].get(d)
rows=collections.defaultdict(list)
for r in H:
    t=r['team']; s=r['seat']
    rows[t].append((r,s))
    if t=='DSM':
        e=L[tuple(r['shops']['6'][:2])]; rows['E17(paired)'].append((e,e['exp17_seat']))
def item_units(r,s,kind,item,d0,d1):
    return sum(v for d,i,v in r[kind][s] if i==item and d0<=d<=d1)
print('item | day-of-shop-check | group(n buyers) | team: mean harvest d12-29 / revenue d12-29 (n games)')
for item,dcheck in [('TOMATO',12),('CARROT',9),('EGG',9),('STRAWBERRY',6),('MILK',9),('WOOL',9)]:
    for team in ['DSM','Majkel1337','M & M & P & Q','E17(paired)']:
        grp=collections.defaultdict(list)
        for r,s in rows[team]:
            b=buyers(shopsat(r,dcheck),item); key=min(b,2)
            grp[key].append((item_units(r,s,'harvest',item,12,28),item_units(r,s,'rev',item,12,29)))
        print(item,dcheck,team,' | '.join(f"b={k}: {st.mean(x for x,_ in v):.0f}u/{st.mean(y for _,y in v):.0f}c (n={len(v)})" for k,v in sorted(grp.items())))
