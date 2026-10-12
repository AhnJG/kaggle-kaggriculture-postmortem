"""Frozen rules (Claude 09-27 16:40 KST, before any EXP-032 result). Purpose: pick a 55be-family SPECIALIST for slot 2,
while v074 (P) stays the generalist. Panels: s55=vs D(55be5d5f) seeds 14300-14349, s127=vs O127 14100-14149,
sother=23 guard files 14200-14209 (pooled), hosted=unique 120 replays (report only, plus floor).
Scenario proxy = w127*s127 + w55*s55 + wother*sother. Scenarios: legacy 60/10/30, transition 40/30/30, clone 20/60/20, diverse 25/25/50.
PASS: invalid 0 (719 actions, no agent_errors, DONE/DONE), max_step<0.8,
  transition: paired (cand-P) proxy diff, panel-wise seed bootstrap (B=2000), lower95 > 0;
  legacy: point diff >= -0.10;  hosted (cand-P) point >= -0.10.
Select: highest transition point diff among PASS. Optional argv: census weights "w127,w55,wother" -> reported, not used for PASS.
Inputs: games.jsonl (+ games-add.jsonl and EXP-030 games-final.jsonl for EXP-030 vids if present)."""
import json,sys,random,collections,os
OUT='experiments/exp032_specialist'
def inv(r):return r['err'] is not None or r['statuses']!=['DONE','DONE'] or r['score'] is None or bool(r.get('agent_errors')) or r.get('action_count')!=719
rows={}
for f in (f'{OUT}/games.jsonl',f'{OUT}/games-add.jsonl','experiments/exp030_dpnew_bypass/games-final.jsonl'):
    if os.path.exists(f):
        for l in open(f):r=json.loads(l);rows[r['key']]=r
jobs=json.load(open(f'{OUT}/jobs.json'));miss=[j for j in jobs if f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' not in rows];assert not miss,f'INCOMPLETE {len(miss)}'
M=collections.defaultdict(dict)
for r in rows.values():M[(r['vid'],r['opponent'])][(r['seed'],r['seat'])]=r
gids=sorted({o for (v,o) in M if v=='P' and o not in('D','O127') and not o.startswith('H')});H=sorted({o for (v,o) in M if v=='P' and o.startswith('H')})
assert len(gids)==23 and len(H)==120,(len(gids),len(H))
cands=sorted({v for (v,o) in M if o=='D' and v!='P'})
def diffs(c,o):
    a,b=M[(c,o)],M[('P',o)];ss=sorted({s for s,_ in b});return [sum(a[(s,t)]['score']-b[(s,t)]['score'] for t in (0,1))/2 for s in ss]
def mean(x):return sum(x)/len(x)
SC={'legacy':(.6,.1,.3),'transition':(.4,.3,.3),'clone':(.2,.6,.2),'diverse':(.25,.25,.5)}
if len(sys.argv)>1:SC['census']=tuple(float(x) for x in sys.argv[1].split(','))
res=[]
for i,c in enumerate(cands):
    if not all((c,o) in M and len(M[(c,o)])==len(M[('P',o)]) for o in ['D','O127']+gids+H):res.append(dict(vid=c,status='MISSING_PANELS'));continue
    a=[r for o in ['D','O127']+gids+H for r in M[(c,o)].values()]
    d55=diffs(c,'D');d127=diffs(c,'O127');dg=[x for g in gids for x in diffs(c,g)]
    h=[list(M[(c,o)].values())[0]['score']-list(M[('P',o)].values())[0]['score'] for o in H]
    abs_={'s55':mean([r['score'] for r in M[(c,'D')].values()]),'s127':mean([r['score'] for r in M[(c,'O127')].values()]),
          'sother':mean([r['score'] for g in gids for r in M[(c,g)].values()])}
    g=random.Random(32001+i);B=2000;bs={k:[] for k in SC}
    for _ in range(B):
        m55=mean([d55[g.randrange(len(d55))] for _ in d55]);m127=mean([d127[g.randrange(len(d127))] for _ in d127]);mg=mean([dg[g.randrange(len(dg))] for _ in dg])
        for k,(w1,w2,w3) in SC.items():bs[k].append(w1*m127+w2*m55+w3*mg)
    sc={k:[w1*mean(d127)+w2*mean(d55)+w3*mean(dg),sorted(bs[k])[int(.025*B)]] for k,(w1,w2,w3) in SC.items()}
    r=dict(vid=c,invalid=sum(inv(x) for x in a),max_step=max(x['max_step'] for x in a),abs=abs_,
           d55=mean(d55),d127=mean(d127),dguard=mean(dg),hosted_vs_P=mean(h),scen=sc)
    r['pass']=r['invalid']==0 and r['max_step']<.8 and sc['transition'][1]>0 and sc['legacy'][0]>=-.10 and r['hosted_vs_P']>=-.10
    res.append(r)
Pabs={'s55':mean([r['score'] for r in M[('P','D')].values()]),'s127':mean([r['score'] for r in M[('P','O127')].values()]),'sother':mean([r['score'] for g in gids for r in M[('P',g)].values()])}
ps=sorted([r for r in res if r.get('pass')],key=lambda r:r['scen']['transition'][0],reverse=True)
out=dict(verdict='SUCCESS' if ps else 'FAIL',selected=ps[0]['vid'] if ps else None,P_abs=Pabs,results=res)
json.dump(out,open(f'{OUT}/summary.json','w'),indent=1,default=str)
print(json.dumps({k:v for k,v in out.items() if k!='results'},default=str));[print(json.dumps(r,default=str)) for r in res]
