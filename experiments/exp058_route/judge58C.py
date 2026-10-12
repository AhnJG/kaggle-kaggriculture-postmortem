"""EXP-058 Stage C judge (Claude 09-29, written BEFORE any Stage C result). Rules: PREREG.md Stage C. Usage: python judge58C.py RG_<G><R>
H = X holdout 148 (baseline games42 d157/c26) + fresh part H 71 (baseline exp048B d157/c26); F = fresh part F 228 (baseline exp048B d157);
FAM = exp039 family 250, d157 self := 0.5 baseline; closed-loop = the 50 games vs d157. D3 is judged separately (gate-d3-result.json)."""
import json,collections,os,sys
v=sys.argv[1]
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
RB,_=load(['experiments/exp048_stageB/games-kaggle.jsonl','experiments/exp048_stageB/games-mac.jsonl'])
RC,badC=load(['experiments/exp058_route/gamesC-kaggle.jsonl','experiments/exp058_route/gamesC-mac.jsonl'])
F={f"F{m['episode']}":m for m in json.load(open('experiments/exp049_fresh/meta.json'))}
c=RC.get(v,{});mean=lambda x:sum(x)/len(x) if x else float('nan')
Hx=[k for k in c if k[0].startswith('X') and k in R42['d157'] and k in R42['c26']]
Hf=[k for k in c if k[0] in F and F[k[0]]['part']=='H' and k in RB['d157'] and k in RB['c26']]
Fk=[k for k in c if k[0] in F and F[k[0]]['part']=='F' and k in RB['d157']]
dH=[c[k]-R42['d157'][k] for k in Hx]+[c[k]-RB['d157'][k] for k in Hf]
dHc=[c[k]-R42['c26'][k] for k in Hx]+[c[k]-RB['c26'][k] for k in Hf]
dF=[c[k]-RB['d157'][k] for k in Fk]
FAMk=[k for k in c if k[0] in ('D','HL63','M2965','FJ1010','d157')]
dFAM=[c[k]-(0.5 if k[0]=='d157' else R39['d157'][k]) for k in FAMk if k[0]=='d157' or k in R39['d157']]
CL=[c[k] for k in FAMk if k[0]=='d157']
res=dict(invalid=badC[v],H=(round(mean(dH),4),round(mean(dHc),4),len(dH)),F=(round(mean(dF),4),len(dF)),HF=(round(mean(dH+dF),4),len(dH)+len(dF)),
         FAM=(round(mean(dFAM),4),len(dFAM)),closed_loop_vs_d157=(round(mean(CL),4),len(CL)))
res['local_pass']=(badC[v]==0 and len(dH)==219 and len(dF)==228 and len(dFAM)==250 and mean(dH+dF)>0 and mean(dH)>=-0.02 and mean(dF)>=-0.02
                   and mean(CL)>=0.5 and mean(dFAM)>=-0.02)
print(v,res);json.dump(res,open(f'experiments/exp058_route/verdictC-{v}.json','w'),indent=1)
