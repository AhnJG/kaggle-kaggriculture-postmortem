import json,collections
rows={}
conflict=0
for src in ('games.jsonl',):
    for l in open(src):
        r=json.loads(l)
        if r['key'] in rows and rows[r['key']]['rewards']!=r['rewards']:conflict+=1
        rows.setdefault(r['key'],r)
jobs=json.load(open('jobs-screen.json'))
keys={f'{j[0]}|{j[3]}|{j[4]}' for j in jobs}
print('have',len(set(rows)&keys),'of',len(keys),'conflicts',conflict)
var={x['id']:x for x in json.load(open('variants.json'))}
by=collections.defaultdict(list)
for k in keys:by[rows[k]['vid']].append(rows[k])
P=by['P'];pscore=sum(x['score'] for x in P)/len(P)
pact={(x['seed'],x['seat']):x['act_sha'] for x in P}
print('baseline',pscore)
res=[]
for vid,g in by.items():
    if vid=='P':continue
    inv=sum(1 for x in g if x['err'] or x['statuses']!=['DONE','DONE'])
    sc=sum(x['score'] for x in g if x['score'] is not None)/len(g)
    mg=sum(x['margin'] or 0 for x in g)
    noeff=all(x['act_sha']==pact[(x['seed'],x['seat'])] for x in g)
    ms=max(x['max_step'] for x in g)
    res.append(dict(vid=vid,score=sc,margin=mg,invalid=inv,no_effect=noeff,max_step=ms,change=var[vid]['change']))
res.sort(key=lambda r:(r['score'],r['margin']),reverse=True)
dist=collections.Counter(round(r['score'],2) for r in res)
print('score dist',sorted(dist.items()))
print('no_effect',sum(r['no_effect'] for r in res),'invalid variants',sum(1 for r in res if r['invalid']))
adv=[r for r in res if r['score']>=0.70 and r['invalid']==0][:8]
for r in res[:20]:print(r['vid'],r['score'],r['margin'],r['no_effect'],round(r['max_step'],3),r['change'])
print('ADVANCE',[r['vid'] for r in adv])
json.dump(dict(baseline=pscore,results=res,advance=[r['vid'] for r in adv]),open('stage1-summary.json','w'),indent=1)
