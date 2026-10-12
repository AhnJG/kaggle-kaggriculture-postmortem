"""EXP-043b judge per PREREG_43b.md: full team score = loss tapes (games43) + d157-win tapes (games43b)."""
import json,collections
B='experiments/exp041_top2400/'
M={f"X{m['episode']}":m for m in json.load(open(B+'meta.json'))}
W=['juliencst','thisray','Hikaru Umeda','Shawn404','Fritz Cremer']
S=collections.defaultdict(dict)
for f in ('games42-kaggle.jsonl','games42-mac.jsonl'):
    for l in open(B+f):
        r=json.loads(l)
        if r['score'] is not None and r['vid'] in('d157','c26'):S[r['vid']][r['opponent']]=r['score']
bad=0;keys=set()
for f in (B+'games43-kaggle.jsonl',B+'games43-mac.jsonl','analysis/exp043_oracle/games43b.jsonl'):
    for l in open(f):
        r=json.loads(l)
        if r['score'] is None or r['err'] or r['agent_errors']:bad+=1;continue
        keys.add(r['key']);S[r['vid']][r['opponent']]=r['score']
clue=json.load(open('analysis/exp043_oracle/result43.json'))['clue']
print('bad(incl. G2600/G2602 260)',bad)
print('| bot | loss-tape wins | '+' | '.join(W)+' | all5 | lost d157-wins | verdict |')
out=[]
for v in ['d157','c26']+clue:
    per={};n_all=0;s_all=0;d_all=0;miss=0
    for t in W:
        O=[o for o in S['d157'] if M[o]['team']==t]
        miss+=sum(1 for o in O if o not in S[v])
        sv=sum(S[v].get(o,0) for o in O);sd=sum(S['d157'][o] for o in O)
        per[t]=(sv/len(O),(sv-sd)/len(O));n_all+=len(O);s_all+=sv;d_all+=sd
    wins=sum(1 for o in S['d157'] if M[o]['team'] in W and S['d157'][o]<1 and S[v].get(o)==1)
    lost=sum(1 for o in S['d157'] if M[o]['team'] in W and S['d157'][o]==1 and S[v].get(o,1)<1)
    ok=v not in('d157','c26') and wins>=10 and any(per[t][1]>=0.15 for t in W)
    print(f'| {v} | {wins} | '+' | '.join(f'{per[t][0]:.3f} ({per[t][1]:+.3f})' for t in W)+f' | {s_all/n_all:.3f} ({(s_all-d_all)/n_all:+.3f}) | {lost} | {"CLUE" if ok else "-"} |'+(f' miss={miss}' if miss else ''))
    if ok:out.append(v)
print('VERDICT_43b',out or 'NO CLUE')
