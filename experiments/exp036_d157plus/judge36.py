"""Frozen rules (Claude 09-27 22:00 KST, before any EXP-036 game).
screen (50 frozen tapes, open-loop): valid = no err/agent_errors, DONE/DONE, 719 actions; NO_EFFECT = act_sha equal to d157 on all 50;
  pass = valid all, not NO_EFFECT, score50 > d157 score50 (strict). Rank score50, then sum margin. advance top 8.
stage2: pass = valid all; 300 held-out tapes paired (cand-d157) episode-bootstrap(B=2000) lower95 > 0;
  closed-loop vs V074 / O127 / D (EXP-032 seeds, d157 rows from experiments/exp032_specialist/games.jsonl) each paired point >= -0.03;
  guard 23 pooled paired point >= -0.02. Select highest 300-tape diff point. (Runtime: D3 v2 gate separately before release.)"""
import json,sys,random,collections,os
OUT='experiments/exp036_d157plus';TD='experiments/exp033_tapes';st=sys.argv[1]
def inv(r):return r['err'] is not None or r['statuses']!=['DONE','DONE'] or r['score'] is None or bool(r.get('agent_errors')) or r.get('action_count')!=719
rows={}
for f in (f'{OUT}/games-{st}-kaggle.jsonl',f'{OUT}/games-{st}-mac.jsonl'):
    if os.path.exists(f):
        for l in open(f):r=json.loads(l);rows[r['key']]=r
jobs=json.load(open(f'{OUT}/jobs-{st}-kaggle.json'))+json.load(open(f'{OUT}/jobs-{st}-mac.json'))
miss=[j for j in jobs if f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' not in rows];assert not miss,f'INCOMPLETE {len(miss)}'
base={}
for l in open(f'{TD}/games-cloud.jsonl'):
    r=json.loads(l)
    if r['vid']=='d157':base[r['opponent']]=r
for l in open('experiments/exp032_specialist/games.jsonl'):
    r=json.loads(l)
    if r['vid']=='d157':base[(r['opponent'],r['seed'],r['seat'])]=r
M=collections.defaultdict(dict)
for r in rows.values():M[r['vid']][(r['opponent'],r['seed'],r['seat'])]=r
res=[]
def boot(x,seed,B=2000):
    g=random.Random(seed);n=len(x);return sorted(sum(x[g.randrange(n)] for _ in range(n))/n for _ in range(B))[int(.025*B)]
for i,(v,g) in enumerate(sorted(M.items())):
    iv=sum(inv(r) for r in g.values())
    if st=='screen':
        b=[base[o] for (o,_,_) in g];s=sum(r['score'] for r in g.values());sb=sum(x['score'] for x in b)
        ne=all(r['act_sha']==base[o]['act_sha'] for (o,_,_),r in g.items())
        mg=sum((r['margin'] or 0) for r in g.values())
        res.append(dict(vid=v,n=len(g),score=s/len(g),base=sb/len(b),margin=mg,invalid=iv,no_effect=ne,ok=iv==0 and not ne and s>sb))
    else:
        tp=[(r['score']-base[o]['score']) for (o,_,_),r in g.items() if o.startswith('T')]
        cl={};
        for oid in ('V074','O127','D'):
            d=[r['score']-base[k]['score'] for k,r in g.items() if k[0]==oid];cl[oid]=sum(d)/len(d)
        gd=[r['score']-base[k]['score'] for k,r in g.items() if not k[0].startswith('T') and k[0] not in('V074','O127','D')]
        r=dict(vid=v,invalid=iv,tape=[sum(tp)/len(tp),boot(tp,36001+i)],n_tape=len(tp),closed=cl,guard=sum(gd)/len(gd),n_guard=len(gd))
        r['ok']=iv==0 and r['tape'][1]>0 and all(x>=-.03 for x in cl.values()) and r['guard']>=-.02
        res.append(r)
if st=='screen':
    res.sort(key=lambda r:(r['ok'],r['score'],r['margin']),reverse=True);out=dict(stage=st,advance=[r['vid'] for r in res if r['ok']][:8],results=res)
else:
    ps=sorted([r for r in res if r['ok']],key=lambda r:r['tape'][0],reverse=True);out=dict(stage=st,verdict='SUCCESS' if ps else 'FAIL',selected=ps[0]['vid'] if ps else None,results=res)
json.dump(out,open(f'{OUT}/{st}-summary.json','w'),indent=1,default=str)
print(json.dumps({k:v for k,v in out.items() if k!='results'},default=str));[print(json.dumps(r,default=str)) for r in res[:12]]
