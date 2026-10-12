import json,collections,math
rows=[json.loads(l) for l in open('games-stage2.jsonl')]
by=collections.defaultdict(list)
for r in rows:by[r['vid']].append(r)
def wilson(p,n,z=1.96):
    d=1+z*z/n;c=p+z*z/(2*n);h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n));return (c-h)/d
v={x['id']:x for x in json.load(open('variants.json'))}
out=[]
for vid,g in sorted(by.items()):
    inv=sum(1 for x in g if x['err'] or x['statuses']!=['DONE','DONE'])
    sc=[x['score'] for x in g];n=len(sc);p=sum(sc)/n
    wl=collections.Counter(sc);lo=wilson(p,n)
    mg=sum(x['margin'] for x in g)/n
    ok= vid!='P' and inv==0 and lo>0.5 and p>=0.65
    out.append(dict(vid=vid,n=n,score=p,wilson95_lo=lo,W=wl[1.0],D=wl[0.5],L=wl[0.0],mean_margin=mg,invalid=inv,max_step=max(x['max_step'] for x in g),passed=ok,change=None if vid=='P' else v[vid]['change']))
for o in sorted(out,key=lambda o:-o['score']):print(o['vid'],o['n'],round(o['score'],3),round(o['wilson95_lo'],3),o['W'],o['D'],o['L'],round(o['mean_margin'],1),o['invalid'],round(o['max_step'],3),o['passed'],o['change'] and o['change']['target'])
json.dump(out,open('stage2-summary.json','w'),indent=1)
