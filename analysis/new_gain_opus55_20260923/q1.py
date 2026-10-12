import json, collections, statistics as st
H=[json.loads(l) for l in open('resim_hosted.jsonl')]
L={tuple(json.loads(l)['pair']):json.loads(l) for l in open('exp17_local.jsonl')}
CROPS=["WHEAT","CARROT","STRAWBERRY","TOMATO","MELON"]; AN=["COW","SHEEP","GOOSE"]
def vec(snap):
    c=snap['crops']; a=snap['animals']
    return {**{k:c.get(k,0) for k in CROPS}, **{k:a.get(k,0) for k in AN}, 'hands':snap['hands'], 'quads':snap['quads'], 'money':snap['money']}
def first_big(dv, ev):
    for d in range(29):
        x,y=dv[d],ev[d]
        diffs=[]
        for k in CROPS:
            if abs(x[k]-y[k])>=4: diffs.append(f"{k} {x[k]}vs{y[k]}")
        for k in AN:
            if abs(x[k]-y[k])>=2: diffs.append(f"{k} {x[k]}vs{y[k]}")
        if abs(x['hands']-y['hands'])>=2: diffs.append(f"hands {x['hands']}vs{y['hands']}")
        if diffs: return d, diffs
    return None, []
rows=[]; agg=collections.defaultdict(list)
for r in H:
    if r['team']!='DSM': continue
    pair=tuple(r['shops']['6'][:2]) if '6' in r['shops'] else tuple(r['shops'][6][:2])
    e=L[pair]; s=r['seat']; es=e['exp17_seat']
    dv=[vec(r['snap'][d][str(s)]) for d in range(29)]
    ev=[vec(e['snap'][d][str(es)]) for d in range(29)]
    fd,diffs=first_big(dv,ev)
    rows.append(dict(ep=r['episode_id'],pair='+'.join(pair),res='W' if r['rewards'][s]>r['rewards'][1-s] else 'L',dsm=r['rewards'][s],e17=e['rewards'][es],first_day=fd,diffs=diffs,
                     shops_same_d24=r['shops'].get('24',r['shops'].get(24))==e['shops'].get('24',e['shops'].get(24))))
    for d in range(29):
        for k in dv[d]:
            agg[(d,k)].append((dv[d][k],ev[d][k]))
json.dump(dict(rows=rows),open('q1_rows.json','w'),indent=1)
fdc=collections.Counter(x['first_day'] for x in rows); print('first big-diff day distribution',sorted(fdc.items()))
dc=collections.Counter(tuple(sorted(set(t.split()[0] for t in x['diffs']))) for x in rows); print(dc.most_common(8))
print('day | '+' | '.join(f'{k} DSM/E17' for k in CROPS+AN+['hands']))
for d in [0,1,2,3,5,6,8,10,11,12,14,16,18,20,23,26,28]:
    print(d,'|',' | '.join(f"{st.mean(a for a,b in agg[(d,k)]):.1f}/{st.mean(b for a,b in agg[(d,k)]):.1f}" for k in CROPS+AN+['hands']))
for x in rows[:40]: print(x['ep'],x['pair'],x['res'],x['dsm'],x['e17'],x['first_day'],x['diffs'][:4])
