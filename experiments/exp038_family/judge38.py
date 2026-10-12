"""Frozen rules (Claude 09-28 12:30 KST, before any EXP-038 game). Baseline = d157 (active, 2393).
family score FS = mean score vs {D, HL63, M2965, FJ1010, d157} closed-loop (d157 vs itself := 0.5) + d157-hosted tapes whose label is 55be/DP family.
general GS = mean score on EXP-033 350 tapes + d157-hosted 40 tapes.
PASS (slot-2 candidate): invalid 0; FS - FS(d157) >= +0.05 with paired seed/episode bootstrap lower95 > 0;
  GS - GS(d157) >= -0.03; vs O127 and vs V074 each >= d157 - 0.05. Select max FS; tie GS.
Report every candidate's FS, GS, per-opponent table regardless of PASS (aggressive choice is the human's)."""
import json,collections,random,os
OUT='experiments/exp038_family'
def inv(r):return r['err'] is not None or r['statuses']!=['DONE','DONE'] or r['score'] is None or bool(r.get('agent_errors')) or r.get('action_count')!=719
rows={}
for f in ('games-kaggle.jsonl','games-mac.jsonl'):
    p=f'{OUT}/{f}'
    if os.path.exists(p):
        for l in open(p):r=json.loads(l);rows[r['key']]=r
jobs=json.load(open(f'{OUT}/jobs-kaggle.json'))+json.load(open(f'{OUT}/jobs-mac.json'))
miss=[j for j in jobs if f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' not in rows];assert not miss,f'INCOMPLETE {len(miss)}'
nm={f"U{m['episode']}":m for m in json.load(open(f'{OUT}/meta-d157.json'))}
famT=[k for k,m in nm.items() if any(x in m['label'] for x in ('55be5d5f','DP-0924','a-smaller'))]
FAM=['D','HL63','M2965','FJ1010','d157']
M=collections.defaultdict(dict)
for r in rows.values():M[r['vid']][(r['opponent'],r['seed'],r['seat'])]=r
def units(v):
    fam={};gen={}
    for (o,s,t),r in M[v].items():
        if o in FAM:fam[(o,s)]=fam.get((o,s),0)+r['score']/2
        if o.startswith('U') and o in famT:fam[(o,0)]=r['score']
        if o.startswith('T') or o.startswith('U'):gen[o]=r['score']
    if v in FAM:
        for s in range(15000,15025):fam[(v,s)]=0.5
    return fam,gen
def boot(d,seed,B=2000):
    g=random.Random(seed);n=len(d);return sorted(sum(d[g.randrange(n)] for _ in range(n))/n for _ in range(B))[int(.025*B)]
bf,bg=units('d157');res=[]
for i,v in enumerate(sorted(M)):
    f,g=units(v);iv=sum(inv(r) for r in M[v].values())
    df=[f[k]-bf[k] for k in bf if k in f];dg=[g[k]-bg[k] for k in bg if k in g]
    per={o:round(sum(r['score'] for (oo,_,_),r in M[v].items() if oo==o)/max(1,sum(1 for (oo,_,_) in M[v] if oo==o)),3) for o in FAM+['O127','V074']}
    FS=sum(f.values())/len(f);GS=sum(g.values())/len(g)
    r=dict(vid=v,invalid=iv,FS=round(FS,4),GS=round(GS,4),dFS=[round(sum(df)/len(df),4),round(boot(df,38001+i),4)] if v!='d157' else None,dGS=round(sum(dg)/len(dg),4),per=per)
    r['pass']=v!='d157' and iv==0 and r['dFS'][0]>=.05 and r['dFS'][1]>0 and r['dGS']>=-.03 and per['O127']>=M and False if False else (v!='d157' and iv==0 and r['dFS'][0]>=.05 and r['dFS'][1]>0 and r['dGS']>=-.03)
    res.append(r)
bp={o:[r for r in res if r['vid']=='d157'][0]['per'][o] for o in ('O127','V074')}
for r in res:
    if r['pass']:r['pass']=all(r['per'][o]>=bp[o]-.05 for o in ('O127','V074'))
ps=sorted([r for r in res if r['pass']],key=lambda r:(r['FS'],r['GS']),reverse=True)
out=dict(verdict='SUCCESS' if ps else 'FAIL',selected=ps[0]['vid'] if ps else None,results=sorted(res,key=lambda r:-r['FS']))
json.dump(out,open(f'{OUT}/summary.json','w'),indent=1)
print(json.dumps({k:v for k,v in out.items() if k!='results'}));[print(json.dumps(r)) for r in out['results']]
