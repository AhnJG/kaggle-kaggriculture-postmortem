import json, statistics as st, collections
H=[json.loads(l) for l in open('resim_hosted.jsonl')]
E=[json.loads(l) for l in open('exp17_local.jsonl')]
L={tuple(e['pair']):e for e in E}
SHOPS={"BAKERY":["EGG","WHEAT"],"PIZZA_SHOP":["MILK","TOMATO","WHEAT"],"BRUNCH_SPOT":["EGG","WHEAT","STRAWBERRY"],"YARN_STORE":["WOOL"],
"ICE_CREAM_SHOP":["STRAWBERRY","MILK","WHEAT"],"PET_CAFE":["CARROT"],"SMOOTHIE_SHOP":["STRAWBERRY","MILK"],"FARMERS_MARKET":["WHEAT","CARROT","TOMATO","STRAWBERRY"]}
SEED={'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}
def net(r,s,item):
    rv=sum(v for d,i,v in r['rev'][s] if i==item and 12<=d<=29)
    pl=sum(v for d,i,v in r['plant'][s] if i==item and 10<=d<=29)
    return rv-pl*SEED.get(item,0)
def b(r,item,day=12): return min(2,sum(item in SHOPS[x] for x in r['shops'][str(day)]))
D=[(r,r['seat']) for r in H if r['team']=='DSM']
P=[(L[tuple(r['shops']['6'][:2])],) for r,_ in D]
Pe=[(e,e['exp17_seat']) for (e,) in P]
res={}
for item in ['TOMATO','EGG','CARROT','STRAWBERRY']:
    gd=collections.defaultdict(list); ge=collections.defaultdict(list)
    for r,s in D: gd[b(r,item)].append(net(r,s,item))
    for e,s in Pe: ge[b(e,item)].append(net(e,s,item))
    w={k:len(v)/len(D) for k,v in gd.items()}
    gaps={k:st.mean(gd[k])-st.mean(ge[k]) for k in gd if k in ge}
    base=gaps.get(0,0)
    shop_part=sum(w[k]*(gaps[k]-base) for k in gaps if k>0)
    total=sum(w[k]*gaps[k] for k in gaps)
    res[item]=dict(base=round(base),shop_part=round(shop_part),total=round(total),
                   groups={k:(round(st.mean(gd[k])),len(gd[k]),round(st.mean(ge[k])) if k in ge else None,len(ge.get(k,[]))) for k in sorted(gd)})
    print(item,res[item])
json.dump(res,open('q2e.json','w'),indent=1)
print('sum shop_part',sum(v['shop_part'] for v in res.values()),'sum total',sum(v['total'] for v in res.values()))
