"""Frozen rules (Claude, before results).
screen: parent vs O1-self must be 0.40-0.60 else STOP. advance if invalid 0, not NO_EFFECT, vs O1 >= 0.70, vs O2 >= parent vs O2; top 8 by (O1, O2, margin).
stage2: pass if invalid 0, vs O1 Wilson95 lower > 0.50, vs O1 point >= 0.65, vs O2 point >= parent vs O2 - 0.02. rank by O1 lower."""
import json,sys,math,collections
OUT='experiments/exp029_dpnew_mirror'
def inv(r):return r['err'] is not None or r['statuses']!=['DONE','DONE'] or r['score'] is None or bool(r.get('agent_errors')) or r.get('action_count')!=719
def wl(p,n,z=1.96):d=1+z*z/n;c=p+z*z/(2*n);h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n));return (c-h)/d
st=sys.argv[1];rows={};[rows.__setitem__(json.loads(l)['key'],json.loads(l)) for l in open(f'{OUT}/games-{st}.jsonl')]
jobs=json.load(open(f'{OUT}/jobs-{st}.json'));assert {f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' for j in jobs}==set(rows),'INCOMPLETE'
G=collections.defaultdict(lambda:collections.defaultdict(list))
for r in rows.values():G[r['vid']][r['opponent']].append(r)
def sc(v,o):x=G[v][o];return sum(r['score'] for r in x if not inv(r))/len(x)
p1,p2=sc('P','O1-self'),sc('P','O2-127ed3e6')
if st=='screen' and not .40<=p1<=.60:print(json.dumps(dict(verdict='STOP',reason='parent self-play asymmetric',parent_o1=p1)));sys.exit()
pa={(r['opponent'],r['seed'],r['seat']):r['act_sha'] for o in G['P'] for r in G['P'][o]}
res=[]
for v in G:
    if v=='P':continue
    a=[r for o in G[v] for r in G[v][o]];iv=sum(inv(r) for r in a);ne=all(r['act_sha']==pa.get((r['opponent'],r['seed'],r['seat'])) for r in a)
    o1,o2=sc(v,'O1-self'),sc(v,'O2-127ed3e6');mg=sum(r['margin'] or 0 for r in a);n1=len(G[v]['O1-self'])
    r=dict(vid=v,o1=o1,o2=o2,margin=mg,invalid=iv,no_effect=ne,max_step=max(x['max_step'] for x in a))
    if st=='screen':r['ok']=iv==0 and not ne and o1>=.70 and o2>=p2
    else:r['o1_lower']=wl(o1,n1);r['ok']=iv==0 and r['o1_lower']>.50 and o1>=.65 and o2>=p2-.02
    res.append(r)
res.sort(key=lambda r:(r['ok'],r.get('o1_lower',r['o1']),r['o2'],r['margin']),reverse=True)
sel=[r['vid'] for r in res if r['ok']][:8 if st=='screen' else 99]
json.dump(dict(stage=st,parent_o1=p1,parent_o2=p2,advance=sel,results=res),open(f'{OUT}/{st}-summary.json','w'),indent=1)
print(json.dumps(dict(stage=st,parent_o1=p1,parent_o2=p2,advance=sel)));[print(r) for r in res[:10]]
