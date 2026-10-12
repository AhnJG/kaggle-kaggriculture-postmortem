"""EXP-041 (Claude 09-28 16:30 KST): 2400+ opponents (d157 losers-to, 25 submissions) -> behaviour features + tapes.
python prep41.py <start> <end>   (chunked; repo root)   ;  python prep41.py finalize"""
import json,gzip,sys,os,hashlib,collections
OUT='experiments/exp041_top2400';RAW='private_artifacts/top2400_20260928/raw/'
E=json.load(open('analysis/top2400_20260928/episodes_all.json'));T=json.load(open('analysis/top2400_20260928/targets.json'))
CK=[144,288,432,576,648,719]
def feats(r,seat):
    st=r['steps'];out={}
    for k in CK:
        o=st[min(k,len(st)-1)][seat]['observation'];f=o['farms'][seat] if 'farms' in o else st[min(k,len(st)-1)][0]['observation']['farms'][seat]
        out[f'money{k}']=f['money']
        if k in (288,576):
            a=collections.Counter();c=collections.Counter()
            for row in f['tiles']:
                for t in row:
                    if isinstance(t,dict):
                        if t.get('animal'):a[t['animal']]+=1
                        if t.get('crop'):c[t['crop']]+=1
            out[f'animals{k}']=dict(a);out[f'crops{k}']=dict(c);out[f'quads{k}']=len(f['unlocked_quadrants'])
    sell=collections.Counter();sellq=collections.defaultdict(lambda:[0,0,0,0])
    buy=collections.Counter()
    for k in range(1,len(st)):
        a=st[k][seat].get('action') or {}
        for m in a.get('market',[]) or []:
            if not isinstance(m,list) or len(m)<3:continue
            if m[0]=='SELL':sell[m[1]]+=int(m[2]);sellq[m[1]][min(3,(k-1)//180)]+=int(m[2])
            elif m[0] in('BUY_SEED','BUY_PRODUCT','BUY_ANIMAL'):buy[f'{m[0]}:{m[1]}']+=int(m[2]) if len(m)>2 else 1
    out['sell']=dict(sell);out['sellq']={k:v for k,v in sellq.items()};out['buy']=dict(buy);out['reward']=st[-1][seat]['reward']
    return out
if sys.argv[1]!='finalize':
    a,b=int(sys.argv[1]),int(sys.argv[2])
    with open(f'{OUT}/feat/f{a:04d}.jsonl','w') as w:
        for e in E[a:b]:
            p=f"{RAW}{e['id']}.json.gz"
            if not os.path.exists(p):continue
            try:
                r=json.load(gzip.open(p));names=r['info']['TeamNames'];tn=T[str(e['submission_id'])]
                assert len(r['steps'])>=720
            except Exception:continue
            if tn not in names:continue
            ts=names.index(tn);os_=1-ts
            tape=[r['steps'][k+1][ts]['action'] for k in range(len(r['steps'])-1)]
            open(f"{OUT}/tapes/X{e['id']}.py",'w').write('TAPE='+json.dumps(tape)+'\ndef tape_agent(obs, configuration=None):\n    s=int(obs["step"])\n    return TAPE[s] if s<len(TAPE) else {"farmer":["PASS"],"hands":[],"market":[]}\n')
            rw=[r['steps'][-1][i]['reward'] for i in (0,1)]
            w.write(json.dumps(dict(episode=e['id'],sub=e['submission_id'],team=tn,seed=int(r['info']['seed']),target_seat=ts,our_seat=os_,
                opp_team=names[os_],target_reward=rw[ts],opp_reward=rw[os_],target=feats(r,ts),opp=feats(r,os_)))+'\n')
    print('done',a,b)
else:
    rows=[json.loads(l) for f in sorted(os.listdir(f'{OUT}/feat')) for l in open(f'{OUT}/feat/{f}')]
    teams=sorted({r['team'] for r in rows});H=sorted(teams,key=lambda t:hashlib.sha256(f'exp041-{t}'.encode()).hexdigest())[:5]
    json.dump(dict(holdout_teams=H,select_teams=[t for t in teams if t not in H]),open(f'{OUT}/team-split.json','w'),indent=1,ensure_ascii=False)
    json.dump([{k:r[k] for k in ('episode','sub','team','seed','our_seat','target_seat','opp_team','target_reward','opp_reward')} for r in rows],open(f'{OUT}/meta.json','w'),indent=1,ensure_ascii=False)
    print('rows',len(rows),'teams',len(teams),'holdout',H)
