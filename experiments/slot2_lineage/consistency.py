import json,gzip,collections,os,statistics,sys
def rows_for(team, pairs_list, limit=90):
    rows=[]
    for p,team_ in pairs_list:
        if len(rows)>=limit: break
        if not os.path.exists(p): continue
        r=json.load(gzip.open(p)); names=r['info']['TeamNames']
        if team not in names: continue
        seat=names.index(team); st=r['steps']
        shops=tuple(st[150][0]['observation']['town']['unlocked_shops'][:2])
        fa=[json.dumps(st[i][seat]['action'].get('farmer'))+json.dumps(st[i][seat]['action'].get('hands')) for i in range(1,719)]
        rows.append((shops,fa))
    return rows
def report(name,rows):
    by=collections.defaultdict(list)
    for s,fa in rows: by[s].append(fa)
    vals=[]
    for s,v in by.items():
        for i in range(len(v)):
            for j in range(i+1,len(v)):
                a,b=v[i],v[j]
                vals.append([sum(1 for t in range(lo,hi) if a[t]==b[t])/(hi-lo) for lo,hi in [(0,143),(143,431),(431,717)]])
    m=[round(statistics.mean(x[k] for x in vals),2) for k in range(3)] if vals else None
    print(name,'games',len(rows),'distinct pairs',len(by),'same-pair comparisons',len(vals),'identical share (<144 / 144-431 / 432+):',m, flush=True)
which=sys.argv[1]
if which=='fritz':
    E=json.load(open('analysis/top2400_20260928/episodes_all.json'))+json.load(open('analysis/top2400_fresh_20260929/episodes_all.json'))
    L=[]
    for e in E:
        if 'Fritz' in json.dumps(e):
            for d in ['private_artifacts/top2400_20260928/raw','private_artifacts/top2400_fresh_20260929/raw']:
                L.append((f"{d}/{e['id']}.json.gz",None))
    report('Fritz',rows_for('Fritz Cremer',L))
else:
    E=json.load(open('analysis/hosted_20260929b/episodes_all.json'))
    L=[(f"private_artifacts/hosted_20260929b/raw/{e['id']}.json.gz",None) for e in E if e['submission_label']=='d157']
    report('Sian d157',rows_for('Sian',L,limit=90))
