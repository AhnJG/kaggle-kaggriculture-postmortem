import json, statistics as st, collections
H=[json.loads(l) for l in open('resim_hosted.jsonl')]
L={tuple(json.loads(l)['pair']):json.loads(l) for l in open('exp17_local.jsonl')}
SHOPS={"BAKERY":["EGG","WHEAT"],"PIZZA_SHOP":["MILK","TOMATO","WHEAT"],"BRUNCH_SPOT":["EGG","WHEAT","STRAWBERRY"],"YARN_STORE":["WOOL"],
"ICE_CREAM_SHOP":["STRAWBERRY","MILK","WHEAT"],"PET_CAFE":["CARROT"],"SMOOTHIE_SHOP":["STRAWBERRY","MILK"],"FARMERS_MARKET":["WHEAT","CARROT","TOMATO","STRAWBERRY"]}
ITEMS=["WHEAT","CARROT","STRAWBERRY","TOMATO","MELON","EGG","MILK","WOOL","FERTILIZER"]
def rev(r,s,d0,d1): 
    c=collections.Counter()
    for d,i,v in r['rev'][s]:
        if d0<=d<=d1: c[i]+=v
    return c
gap=collections.defaultdict(list); fin=[]; tot=[]
per=[]
for r in H:
    if r['team']!='DSM': continue
    s=r['seat']; e=L[tuple(r['shops']['6'][:2])]; es=e['exp17_seat']
    a=rev(r,s,0,29); b=rev(e,es,0,29)
    for i in ITEMS: gap[i].append(a[i]-b[i])
    fin.append(r['rewards'][s]-e['rewards'][es]); tot.append(sum(a.values())-sum(b.values()))
    sh12=r['shops']['12']
    per.append(dict(ep=r['episode_id'],tom_b=sum('TOMATO' in SHOPS[x] for x in sh12),egg_b=sum('EGG' in SHOPS[x] for x in sh12),car_b=sum('CARROT' in SHOPS[x] for x in sh12),
                    g_tom=a['TOMATO']-b['TOMATO'],g_egg=a['EGG']-b['EGG'],g_car=a['CARROT']-b['CARROT'],g_tot=sum(a.values())-sum(b.values()),g_fin=fin[-1]))
n=len(fin)
def ci(x):
    m=st.mean(x); se=st.stdev(x)/len(x)**0.5; return f"{m:8.0f} ± {1.96*se:6.0f}"
print('n',n,'final cash gap DSM-E17', ci(fin),' revenue gap', ci(tot))
for i in ITEMS: print(f"{i:11s} rev gap {ci(gap[i])}")
sub=sum(st.mean(gap[i]) for i in ['TOMATO','CARROT','EGG'])
print('TOMATO+CARROT+EGG gap', round(sub), 'share of final gap', round(sub/st.mean(fin),2))
json.dump(per,open('q2_per.json','w'))
