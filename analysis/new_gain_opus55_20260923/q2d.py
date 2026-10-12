import json, statistics as st, collections
H=[json.loads(l) for l in open('resim_hosted.jsonl')]
E=[json.loads(l) for l in open('exp17_local.jsonl')]
L={tuple(e['pair']):e for e in E}
SHOPS={"BAKERY":["EGG","WHEAT"],"PIZZA_SHOP":["MILK","TOMATO","WHEAT"],"BRUNCH_SPOT":["EGG","WHEAT","STRAWBERRY"],"YARN_STORE":["WOOL"],
"ICE_CREAM_SHOP":["STRAWBERRY","MILK","WHEAT"],"PET_CAFE":["CARROT"],"SMOOTHIE_SHOP":["STRAWBERRY","MILK"],"FARMERS_MARKET":["WHEAT","CARROT","TOMATO","STRAWBERRY"]}
SEED={'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}
def shops_on(shops,day):
    ks=sorted(int(x) for x in shops); prev=[x for x in ks if x<=day]
    return shops[str(prev[-1])] if prev else []
def dem(shops,item,d0=12,d1=29):
    t=0
    for step in range(d0*24,(d1+1)*24,4):
        for s in shops_on(shops,step//24):
            p=SHOPS[s]
            if item in p: t+=2 if len(p)==1 else 1
    return t
def feats(r,s,item):
    rv=sum(v for d,i,v in r['rev'][s] if i==item and 12<=d<=29)
    hv=sum(v for d,i,v in r['harvest'][s] if i==item and 12<=d<=29)
    pl=sum(v for d,i,v in r['plant'][s] if i==item and 10<=d<=29)
    net=rv-pl*SEED.get(item,0)
    return dem(r['shops'],item), hv, net
def ols(xs,ys):
    mx,my=st.mean(xs),st.mean(ys); sxx=sum((x-mx)**2 for x in xs)
    b=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sxx; a=my-b*mx
    res=[y-a-b*x for x,y in zip(xs,ys)]; se=(sum(e*e for e in res)/(len(xs)-2)/sxx)**0.5
    return a,b,se
sets={'DSM':[(r,r['seat']) for r in H if r['team']=='DSM'],'Majkel1337':[(r,r['seat']) for r in H if r['team']=='Majkel1337'],
      'MMPQ':[(r,r['seat']) for r in H if r['team']=='M & M & P & Q'],'E17(31 local)':[(e,e['exp17_seat']) for e in E]}
out={}
for item in ['TOMATO','CARROT','EGG','STRAWBERRY','WHEAT','MILK','WOOL']:
    for k,v in sets.items():
        F=[feats(r,s,item) for r,s in v]; xs=[f[0] for f in F]
        a,b,se=ols(xs,[f[2] for f in F]); ah,bh,seh=ols(xs,[f[1] for f in F])
        out[(item,k)]=(a,b,se,ah,bh,seh,st.mean(xs))
        print(f"{item:10s} {k:14s} mean demand {st.mean(xs):6.1f} | net-rev = {a:7.0f} + {b:6.1f}*dem (se {se:5.1f}) | harvest = {ah:6.1f} + {bh:5.2f}*dem (se {seh:4.2f})")
