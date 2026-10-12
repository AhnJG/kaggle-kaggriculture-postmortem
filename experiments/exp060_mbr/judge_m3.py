"""READOUT0930 (plan sha a762337d68aa) + EXP-060 M3 판정 (PREREG 137f92985e2f). Usage: python judge_m3.py <tag>"""
import sys,json,random,collections
TAGS=sys.argv[1].split(','); tag='+'.join(TAGS); P=[x for tg in TAGS for x in json.load(open(f'experiments/exp060_mbr/holdout/panel-{tg}.json'))]
G={}
for f in [f'experiments/exp060_mbr/games-m3-{tg}-{w}.jsonl' for tg in TAGS for w in ('kaggle','mac')]:
    try:
        for l in open(f): r=json.loads(l); G[(r['vid'],r['opponent'],r['seed'],r['seat'])]=r
    except FileNotFoundError: pass
def v(a,x): r=G.get((a,x['opp'],x['seed'],x['seat'])); return None if r is None else r['score']
def real(x): return {'W':1.0,'L':0.0,'D':0.5}[x['result']]
def bs(d,seed=60,n=2000):
    if not d: return (None,None,None)
    rng=random.Random(seed); m=sum(d)/len(d); b=sorted(sum(rng.choice(d) for _ in d)/len(d) for _ in range(n))
    return (round(m,3),round(b[int(.05*n)],3),round(b[int(.95*n)-1],3))
R={'n_games':len(G),'bad_rows':sum(1 for r in G.values() if r.get('err') or r.get('agent_errors'))}
NEW=[x for x in P if x['panel']=='NEW']
# 0 validity
SR=[(x,G.get(('X' if x['sub']=='X' else 'd157',x['opp'],x['seed'],x['seat']))) for x in NEW]
R['selfrepro_mismatch']=[x['opp'] for x,g in SR if g is not None and g['margin']!=x['margin']]; R['selfrepro_notrun']=sum(1 for x,g in SR if g is None); R['selfrepro_ok']=sum(1 for x,g in SR if g is not None and g['margin']==x['margin']); R['our_status_not_done']=[x['opp'] for x in NEW if x.get('status')!='DONE']
# A/B readout
def delta(sub_mir=None):
    d1=[real(x)-v('d157',x) for x in NEW if x['sub']=='X' and v('d157',x) is not None and (sub_mir is None or x['mirror']==sub_mir)]
    d2=[v('X',x)-real(x) for x in NEW if x['sub']=='d157r' and v('X',x) is not None and (sub_mir is None or x['mirror']==sub_mir)]
    return {'n1':len(d1),'d1':bs(d1),'n2':len(d2),'d2':bs(d2),'pooled':bs(d1+d2),'d2_minus_d1':None if not d1 or not d2 else round(sum(d2)/len(d2)-sum(d1)/len(d1),3),'min':None if not d1 or not d2 else round(min(sum(d1)/len(d1),sum(d2)/len(d2)),3)}
R['A_all']=delta(); R['B_mirror']=delta(True); R['B_nonmirror']=delta(False)
R['mirror_rate']={s:round(sum(1 for x in NEW if x['sub']==s and x['mirror'])/max(1,sum(1 for x in NEW if x['sub']==s)),3) for s in ('X','d157r')}
# C common opponents
by=collections.defaultdict(lambda:{'X':[],'d157r':[]})
for x in NEW: by[x['op_sub']][x['sub']].append(real(x))
com=[(sum(a['X'])/len(a['X'])-sum(a['d157r'])/len(a['d157r'])) for a in by.values() if a['X'] and a['d157r']]
R['C_common']={'n_opp':len(com),'diff':bs(com)}
# M3 holdout (virtual, HF+NEW)
arms=('Cd','Cc','X','d157','c26')+(('Cn',) if any(k[0]=='Cn' for k in G) else ())
def panel(f):
    xs=[x for x in P if f(x) and all(v(a,x) is not None for a in arms)]
    out={'n':len(xs)}
    if xs: out.update({a:round(sum(v(a,x) for x in xs)/len(xs),3) for a in arms})
    out.update({f'{c}-X':bs([v(c,x)-v('X',x) for x in xs]) for c in ('Cd','Cc','Cn') if c in arms})
    out.update({f'{c}-d157':bs([v(c,x)-v('d157',x) for x in xs]) for c in ('Cd','Cc')})
    return out
R['M3_all']=panel(lambda x:True); R['M3_mirror']=panel(lambda x:x['mirror']); R['M3_nonmirror']=panel(lambda x:not x['mirror'])
R['M3_HF']=panel(lambda x:x['panel']=='HF'); R['M3_NEW']=panel(lambda x:x['panel']=='NEW')
# portfolio (Sol 2차 검토, ADDENDUM A1): max(d157,C) - max(d157,X), d157 패배판 C-X
def port(c,f):
    xs=[x for x in P if f(x) and all(v(a,x) is not None for a in (c,'X','d157'))]
    d=[max(v('d157',x),v(c,x))-max(v('d157',x),v('X',x)) for x in xs]
    lo=[v(c,x)-v('X',x) for x in xs if v('d157',x)<0.5]
    return {'n':len(xs),'port':bs(d),'d157loss_n':len(lo),'d157loss_C-X':bs(lo)}
for c in [c for c in ('Cd','Cc','Cn') if c in arms]:
    R[f'PORT_{c}']={nm:port(c,f) for nm,f in (('all',lambda x:True),('mirror',lambda x:x['mirror']),('nonmirror',lambda x:not x['mirror']),('NEW',lambda x:x['panel']=='NEW'),('NEW_mirror',lambda x:x['panel']=='NEW' and x['mirror']))}
    R[f'M3_NEWgroup_{c}']={}
EFFG=json.load(open('experiments/exp058_route/effective_route_by_pair.json'))
def grp(x):
    r=EFFG.get('|'.join(x.get('shops') or [])); return None if r is None else 'Y' if r==9 else 'D' if r==105 else 'S'
for c in [c for c in ('Cd','Cc','Cn') if c in arms]:
    R.setdefault(f'M3_NEWgroup_{c}',{})
    for g in ('Y','D','S'):
        xs=[x for x in P if x['mirror'] and grp(x)==g and v(c,x) is not None and v('X',x) is not None]
        R[f'M3_NEWgroup_{c}'][g]={'n':len(xs),'C-X':bs([v(c,x)-v('X',x) for x in xs])}
# closed-loop
CL={}
for r in G.values():
    if r['opponent'] in ('d157','D55'): CL.setdefault((r['vid'],r['opponent']),[]).append(r['score'])
R['closed']={f'{a}|{o}':(len(s),round(sum(s)/len(s),3)) for (a,o),s in sorted(CL.items())}
# decision helpers (PREREG)
nm=R['B_nonmirror']['pooled']; R['base_rule']='Cd' if (nm[2] is not None and nm[2]<0) else 'higher holdout mean (tie Cd)'
thr=0.0 if (R['B_mirror']['d2_minus_d1'] or 0)>0.10 else -0.03
for c in ('Cd','Cc'):
    cl=[R['closed'].get(f'{c}|{o}',(0,None))[1] for o in ('d157','D55')]; xl=[R['closed'].get(f'X|{o}',(0,None))[1] for o in ('d157','D55')]
    R[f'gate_{c}']={'1_all_C-X>=0':R['M3_all'].get(f'{c}-X',(None,))[0] is not None and R['M3_all'][f'{c}-X'][0]>=0,
                    '2_mirror_C-X>0':R['M3_mirror'].get(f'{c}-X',(None,))[0] is not None and R['M3_mirror'][f'{c}-X'][0]>0,
                    '3_closed':all(a is not None and b is not None and a>=b+thr for a,b in zip(cl,xl)),'closed_thr':thr}
json.dump(R,open(f'experiments/exp060_mbr/m3_verdict-{tag}.json','w'),indent=1); print(json.dumps(R,indent=1)[:4000])
