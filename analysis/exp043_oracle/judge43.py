"""EXP-043 oracle judge (Claude 09-28 19:20 KST). Rule fixed before viewing results (user 09-28):
CLUE if some bot flips >=10 d157-loss tapes (bot score==1 where d157<1) AND, for a team, bot team score - d157 team score >= +0.15.
Team score primary = over ALL of that team's EXP-042 tapes, with d157-win tapes assumed unchanged (optimistic upper bound;
bots were only run on the 130 loss tapes). Secondary = mean over that team's loss tapes only."""
import json,collections,statistics as st
B='experiments/exp041_top2400/'
M={f"X{m['episode']}":m for m in json.load(open(B+'meta.json'))}
W=['juliencst','thisray','Hikaru Umeda','Shawn404','Fritz Cremer']
d={}
for f in ('games42-kaggle.jsonl','games42-mac.jsonl'):
    for l in open(B+f):
        r=json.loads(l)
        if r['vid']=='d157' and r['score'] is not None:d[r['opponent']]=r['score']
Nteam=collections.Counter(M[o]['team'] for o in d if M[o]['team'] in W)
D157team={t:sum(s for o,s in d.items() if M[o]['team']==t)/Nteam[t] for t in W}
R={};bad=[];dup=0
for f in ('games43-kaggle.jsonl','games43-mac.jsonl'):
    for l in open(B+f):
        r=json.loads(l);k=(r['vid'],r['opponent'])
        if k in R:dup+=1
        if r['score'] is None or r['err'] or r['agent_errors'] or r['statuses']!=['DONE','DONE']:bad.append(r['key'])
        R[k]=r
T=sorted({o for _,o in R});A=sorted({v for v,_ in R})
assert all(d[o]<1 and M[o]['team'] in W for o in T)
print('rows',len(R),'dup',dup,'bad',len(bad),bad[:5],'tapes',len(T),'agents',len(A))
print('loss tapes per team',collections.Counter(M[o]['team'] for o in T),'team N',dict(Nteam))
print('d157 team score',{t:round(v,3) for t,v in D157team.items()},'d157 mean on loss tapes',round(st.mean(d[o] for o in T),3))
rows=[];clue=[]
for v in A:
    sc=[R[(v,o)]['score'] for o in T if (v,o) in R and R[(v,o)]['score'] is not None]
    wins=sum(1 for o in T if (v,o) in R and R[(v,o)]['score']==1)
    impr=sum(1 for o in T if (v,o) in R and (R[(v,o)]['score'] or 0)>d[o])
    per={}
    for t in W:
        To=[o for o in T if M[o]['team']==t and (v,o) in R and R[(v,o)]['score'] is not None]
        gain=sum(R[(v,o)]['score']-d[o] for o in To)
        per[t]=(gain/Nteam[t], st.mean(R[(v,o)]['score']-d[o] for o in To) if To else 0, sum(1 for o in To if R[(v,o)]['score']==1),len(To))
    best=max(W,key=lambda t:per[t][0])
    ok=wins>=10 and any(per[t][0]>=0.15 for t in W); ok2=wins>=10 and any(per[t][1]>=0.15 for t in W)
    rows.append((v,len(sc),st.mean(sc),wins,impr,per,best,ok,ok2))
    if ok:clue.append(v)
rows.sort(key=lambda x:-x[3])
print('\n| bot | n | mean | wins(flip) | improved | '+' | '.join(f'{t} Δteam/Δloss/w' for t in W)+' | primary | secondary |')
for v,n,m,w,i,per,best,ok,ok2 in rows:
    print(f'| {v} | {n} | {m:.3f} | {w} | {i} | '+' | '.join(f'{per[t][0]:+.3f}/{per[t][1]:+.2f}/{per[t][2]}' for t in W)+f' | {"CLUE" if ok else "-"} | {"CLUE" if ok2 else "-"} |')
# union oracle: tapes flipped by any bot
U=collections.Counter()
for o in T:
    n=sum(1 for v in A if (v,o) in R and R[(v,o)]['score']==1)
    U[n>0]+=1
print('\ntapes flipped by >=1 bot',U[True],'/',len(T))
hist=collections.Counter(sum(1 for v in A if (v,o) in R and R[(v,o)]['score']==1) for o in T);print('flip-count histogram',sorted(hist.items()))
print('VERDICT_PRIMARY',clue or 'NO CLUE')
json.dump({'clue':clue,'rows':[[v,n,m,w,i,per,ok,ok2] for v,n,m,w,i,per,best,ok,ok2 in rows]},open('analysis/exp043_oracle/result43.json','w'),indent=0)
