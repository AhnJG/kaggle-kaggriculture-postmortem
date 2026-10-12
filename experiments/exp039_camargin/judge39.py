"""Frozen rules (Claude 09-28 14:30 KST, before any EXP-039 game; human rule 14:05 'd157' must be >= d157 on everything').
Baseline d157 (rows re-run in this experiment). d157' PASS iff: invalid 0;
 (1) all tapes (U 136 + T 350) paired diff point > 0 and episode-bootstrap lower95 >= 0;
 (2) U tapes (d157's own hosted opponents) diff point >= 0;
 (3) family FS (vs D,HL63,M2965,FJ1010,d157; d157 self := 0.5) paired diff point >= 0;
 (4) vs O127 and vs V074 each >= d157 - 0.02.  Select max (1) point; tie (3).
Also report: U-tape own-result reproduction for d157 (hosted W/D/L vs local), V074 on U tapes."""
import json,collections,random,os
OUT='experiments/exp039_camargin'
def inv(r):return r['err'] is not None or r['statuses']!=['DONE','DONE'] or r['score'] is None or bool(r.get('agent_errors')) or r.get('action_count')!=719
rows={}
for f in ('games-kaggle.jsonl','games-mac.jsonl'):
    p=f'{OUT}/{f}'
    if os.path.exists(p):
        for l in open(p):r=json.loads(l);rows[r['key']]=r
jobs=json.load(open(f'{OUT}/jobs-kaggle.json'))+json.load(open(f'{OUT}/jobs-mac.json'))
miss=[j for j in jobs if f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' not in rows];assert not miss,f'INCOMPLETE {len(miss)}'
M=collections.defaultdict(dict)
for r in rows.values():M[r['vid']][(r['opponent'],r['seed'],r['seat'])]=r
nm={f"U{m['episode']}":m for m in json.load(open(f'{OUT}/meta-u.json'))}
FAM=['D','HL63','M2965','FJ1010','d157']
def tap(v,pre):return {o:r['score'] for (o,_,_),r in M[v].items() if o[0] in pre}
def fam(v):
    f=collections.defaultdict(float)
    for (o,s,t),r in M[v].items():
        if o in FAM:f[(o,s)]+=r['score']/2
    if v=='d157':
        for s in range(15000,15025):f[('d157',s)]=.5
    return f
def per(v,o):x=[r['score'] for (oo,_,_),r in M[v].items() if oo==o];return sum(x)/len(x) if x else None
def boot(d,seed,B=2000):
    g=random.Random(seed);n=len(d);return sorted(sum(d[g.randrange(n)] for _ in range(n))/n for _ in range(B))[int(.025*B)]
bt=tap('d157','TU');bu=tap('d157','U');bf=fam('d157')
rep=sum(1 for o,s in bu.items() if s=={'W':1.0,'D':.5,'L':0.0}[nm[o]['result']]);vu=tap('V074','U')
res=[]
for i,v in enumerate(sorted(x for x in M if x not in('V074',))):
    t=tap(v,'TU');u=tap(v,'U');f=fam(v)
    if v!='d157':f[('d157',0)]=0  # placeholder removed below
    f.pop(('d157',0),None)
    dt=[t[o]-bt[o] for o in bt];du=[u[o]-bu[o] for o in bu];df=[f[k]-bf[k] for k in bf if k in f]
    r=dict(vid=v,invalid=sum(inv(x) for x in M[v].values()),tape=[round(sum(dt)/len(dt),4),round(boot(dt,39001+i),4)],tapeU=round(sum(du)/len(du),4),
           fam=round(sum(df)/max(1,len(df)),4),O127=per(v,'O127'),V074=per(v,'V074'),abs_tape=round(sum(t.values())/len(t),4),abs_U=round(sum(u.values())/len(u),4))
    res.append(r)
b=[r for r in res if r['vid']=='d157'][0]
for r in res:
    r['pass']=r['vid']!='d157' and r['invalid']==0 and r['tape'][0]>0 and r['tape'][1]>=0 and r['tapeU']>=0 and r['fam']>=0 and r['O127']>=b['O127']-.02 and r['V074']>=b['V074']-.02
ps=sorted([r for r in res if r['pass']],key=lambda r:(r['tape'][0],r['fam']),reverse=True)
out=dict(verdict='SUCCESS' if ps else 'FAIL',selected=ps[0]['vid'] if ps else None,d157_U_reproduce=f'{rep}/{len(bu)}',V074_on_U=round(sum(vu.values())/len(vu),4),results=res)
json.dump(out,open(f'{OUT}/summary.json','w'),indent=1)
print(json.dumps({k:v for k,v in out.items() if k!='results'}));[print(json.dumps(r)) for r in res]
