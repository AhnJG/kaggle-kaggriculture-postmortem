"""Frozen rules (Claude, 09-27 12:20 KST, before results; final per Codex REVIEW-0927B).
screen (parent D=55be5d5f): advance if invalid 0 (action_count 719, no agent_errors), max_step<0.8, not NO_EFFECT,
  vs V074 >= D-0.05, vs O127 >= D-0.05, GUARD4 (PUB01,PUB02,PUB06,PUB12) score > D's; rank GUARD4 score, GUARD4 margin; top 6.
final: pass if hard guards (invalid 0, max_step<0.8), paired (cand-D) seed-bootstrap95 lower > -0.03 vs V074 and vs O127,
  guard(23 files) paired (cand-D) point > 0 and lower95 >= 0, no single guard file worse than D by >0.10,
  hosted unique 120: (cand - v074) point >= 0 and lower95 > -0.03. Select: highest hosted (cand-v074) point, tie guard point."""
import json,sys,random,collections
OUT='experiments/exp030_dpnew_bypass'
def inv(r):return r['err'] is not None or r['statuses']!=['DONE','DONE'] or r['score'] is None or bool(r.get('agent_errors')) or r.get('action_count')!=719
def boot(x,seed,B=2000):
    g=random.Random(seed);n=len(x);m=sorted(sum(x[g.randrange(n)] for _ in range(n))/n for _ in range(B));return m[int(.025*B)]
st=sys.argv[1];rows={};[rows.__setitem__(json.loads(l)['key'],json.loads(l)) for l in open(f'{OUT}/games-{st}.jsonl')]
jobs=json.load(open(f'{OUT}/jobs-{st}.json'));assert {f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' for j in jobs}==set(rows),'INCOMPLETE'
M=collections.defaultdict(dict)
for r in rows.values():M[(r['vid'],r['opponent'])][(r['seed'],r['seat'])]=r
vids=sorted({v for v,_ in M if v not in('D','P')});opps=sorted({o for _,o in M})
def score(v,os_):x=[r for o in os_ for r in M[(v,o)].values()];return sum(r['score'] for r in x)/len(x),sum(r['margin'] or 0 for r in x)
def sd(v,o,base='D'):
    c,p=M[(v,o)],M[(base,o)];ss=sorted({s for s,_ in p});return [sum(c[(s,t)]['score']-p[(s,t)]['score'] for t in (0,1))/2 for s in ss]
res=[]
if st=='screen':
    G4=['PUB01','PUB02','PUB06','PUB12'];dv,_=score('D',['V074']);do,_=score('D',['O127']);dg,dgm=score('D',G4)
    pa={(o,s,t):r['act_sha'] for (v,o),g in M.items() if v=='D' for (s,t),r in g.items()}
    for v in vids:
        a=[r for o in opps for r in M[(v,o)].values()];iv=sum(inv(r) for r in a);mx=max(r['max_step'] for r in a)
        ne=all(r['act_sha']==pa[(o,s,t)] for o in opps for (s,t),r in M[(v,o)].items())
        sv,_=score(v,['V074']);so,_=score(v,['O127']);sg,sgm=score(v,G4)
        ok=iv==0 and mx<.8 and not ne and sv>=dv-.05 and so>=do-.05 and sg>dg
        res.append(dict(vid=v,v074=sv,o127=so,guard4=sg,guard4_margin=sgm,invalid=iv,max_step=mx,no_effect=ne,ok=ok))
    res.sort(key=lambda r:(r['ok'],r['guard4'],r['guard4_margin']),reverse=True);sel=[r['vid'] for r in res if r['ok']][:6]
    out=dict(stage=st,parent=dict(v074=dv,o127=do,guard4=dg,guard4_margin=dgm),advance=sel,results=res)
else:
    gids=[o for o in opps if o not in('V074','O127') and not o.startswith('H')];H=sorted(o for o in opps if o.startswith('H'))
    for i,v in enumerate(vids):
        a=[r for o in opps for r in M[(v,o)].values()];iv=sum(inv(r) for r in a);mx=max(r['max_step'] for r in a)
        x1=sd(v,'V074');x2=sd(v,'O127');pool=[];per={}
        for g in gids:d=sd(v,g);pool+=d;per[g]=sum(d)/len(d)
        h=[list(M[(v,o)].values())[0]['score']-list(M[('P',o)].values())[0]['score'] for o in H]
        r=dict(vid=v,invalid=iv,max_step=mx,v074=[sum(x1)/len(x1),boot(x1,30001+i)],o127=[sum(x2)/len(x2),boot(x2,30101+i)],
               guard=[sum(pool)/len(pool),boot(pool,30201+i)],worst_file=min(per.items(),key=lambda z:z[1]),hosted_vs_v074=[sum(h)/len(h),boot(h,30301+i)])
        r['pass']=iv==0 and mx<.8 and r['v074'][1]>-.03 and r['o127'][1]>-.03 and r['guard'][0]>0 and r['guard'][1]>=0 and r['worst_file'][1]>=-.10 and r['hosted_vs_v074'][0]>=0 and r['hosted_vs_v074'][1]>-.03
        res.append(r)
    ps=sorted([r for r in res if r['pass']],key=lambda r:(r['hosted_vs_v074'][0],r['guard'][0]),reverse=True)
    out=dict(stage=st,verdict='SUCCESS' if ps else 'FAIL',selected=ps[0]['vid'] if ps else None,results=res)
json.dump(out,open(f'{OUT}/{st}-summary.json','w'),indent=1,default=str)
print(json.dumps({k:v for k,v in out.items() if k!='results'},default=str));[print(r) for r in res[:10]]
