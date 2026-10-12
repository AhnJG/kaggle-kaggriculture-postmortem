"""EXP-048 Stage B judge (Claude 09-29, written before any Stage B result). Rules: analysis/exp045/PREREG.md B1-B4 + PREREG_ADDENDUM.md A1(R2), A3.
Baselines: exp039 rows (d157, c26) for U/T/family/O127/V074; games42 rows for old holdout; this run's rows for fresh.
Bugfix after first run (KeyError): fresh tapes keyed by 'F'+episode collided with family opponent 'FJ1010'; membership test now uses the F dict. No criterion change.
Invalid: candidate agent errors count as invalid (disqualify); tape-loader failures that also fail for baselines are excluded for all."""
import json,collections,os
def load(files):
    R=collections.defaultdict(dict);bad=collections.Counter()
    for f in files:
        if not os.path.exists(f):continue
        for l in open(f):
            r=json.loads(l);k=(r['opponent'],r['seed'],r['seat'])
            if r['score'] is None or r['err'] or r['agent_errors'] or r['statuses']!=['DONE','DONE'] or r.get('action_count')!=719:bad[r['vid']]+=1;continue
            R[r['vid']][k]=r['score']
    return R,bad
R39,_=load(['experiments/exp039_camargin/games-kaggle.jsonl','experiments/exp039_camargin/games-mac.jsonl'])
R42,_=load(['experiments/exp041_top2400/games42-kaggle.jsonl','experiments/exp041_top2400/games42-mac.jsonl'])
RB,badB=load(['experiments/exp048_stageB/games-kaggle.jsonl','experiments/exp048_stageB/games-mac.jsonl'])
FAM=['D','HL63','M2965','FJ1010','d157']
B='experiments/exp041_top2400/';H=set(json.load(open(B+'team-split.json'))['holdout_teams'])
M41={f"X{m['episode']}":m for m in json.load(open(B+'meta.json'))}
F={f"F{m['episode']}":m for m in json.load(open('experiments/exp049_fresh/meta.json'))}
def mean(x):return sum(x)/len(x) if x else float('nan')
def panel(v,src,pred):
    return {k:s for k,s in src.get(v,{}).items() if pred(k[0])}
out={}
for v in ('hook','K3'):
    res={};cand=RB.get(v,{})
    # B1 U, T
    for name,pre in (('U','U'),('T','T')):
        ks=[k for k in R39['d157'] if k[0].startswith(pre) and k in R39['c26'] and k in cand]
        res[name]=(mean([cand[k] for k in ks]),mean([R39['d157'][k] for k in ks]),mean([R39['c26'][k] for k in ks]),len(ks))
    # B2 family paired vs d157 (d157 self := 0.5)
    ks=[k for k in cand if k[0] in FAM]
    dd=[cand[k]-(0.5 if k[0]=='d157' else R39['d157'].get(k,float('nan'))) for k in ks]
    res['FAM']=(mean(dd),len(ks))
    vsD=[cand[k]-R39['d157'][k] for k in cand if k[0]=='D' and k in R39['d157']];res['vsD']=(mean(vsD),len(vsD))
    # B3 O127, V074
    for o in ('O127','V074'):
        ks=[k for k in cand if k[0]==o and k in R39['d157']];res[o]=(mean([cand[k] for k in ks]),mean([R39['d157'][k] for k in ks]),len(ks))
    # B4 H = old holdout 148 + fresh holdout-team tapes ; F = fresh select-team tapes
    Hk=[k for k in cand if (k[0].startswith('X') and M41[k[0]]['team'] in H and k in R42['d157'] and k in R42['c26'])]
    Hf=[k for k in cand if k[0] in F and F[k[0]]['part']=='H' and k in RB['d157'] and k in RB['c26']]
    c=[cand[k] for k in Hk]+[cand[k] for k in Hf];d=[R42['d157'][k] for k in Hk]+[RB['d157'][k] for k in Hf];c2=[R42['c26'][k] for k in Hk]+[RB['c26'][k] for k in Hf]
    res['H']=(mean(c),mean(d),mean(c2),len(c))
    Fk=[k for k in cand if k[0] in F and F[k[0]]['part']=='F' and k in RB['d157']]
    res['F']=(mean([cand[k]-RB['d157'][k] for k in Fk]),len(Fk))
    strict=(badB[v]==0 and res['U'][0]>=max(res['U'][1],res['U'][2]) and res['T'][0]>=max(res['T'][1],res['T'][2]) and res['FAM'][0]>=0
            and res['O127'][0]>=res['O127'][1]-0.02 and res['V074'][0]>=res['V074'][1]-0.02
            and res['H'][0]>=max(res['H'][1],res['H'][2]) and res['H'][0]-res['H'][1]>0 and res['F'][0]>=0 and (v!='hook' or res['vsD'][0]>=0))
    r2=(badB[v]==0 and res['H'][0]-res['H'][1]>=0.02 and res['F'][0]>=0 and all(res[p][0]>=res[p][1]-0.02 for p in ('U','T','O127','V074')) and res['FAM'][0]>=-0.02
        and (v!='hook' or res['vsD'][0]>=-0.02))
    out[v]=dict(res=res,invalid=badB[v],strict=strict,r2_local=r2)
    print(v,'invalid',badB[v]);[print(' ',k,tuple(round(x,4) if isinstance(x,float) else x for x in val)) for k,val in res.items()]
    print('  STRICT',strict,'| R2 local conditions (R2-4 c26 hosted check separate)',r2)
json.dump(out,open('experiments/exp048_stageB/verdict.json','w'),indent=1,default=str)
