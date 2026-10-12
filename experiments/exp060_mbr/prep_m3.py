"""EXP-060 M3 + READOUT0930 jobs (Claude 09-30 01:30 KST, before collection). Usage: python prep_m3.py <cand_tag>
1) NEW panel: analysis/hosted_x0930 (X=56675447, d157r=56675458) -> tapes N<ep>.py + NEW.json
2) mirror flag for every HF/NEW tape (d157 to step 145, same test as m0)
3) jobs: {Cd,Cc,X,d157,c26} x (HF+NEW)  +  closed-loop {Cd,Cc,X} x {d157, 55be exact} x seeds 60000-60039 x seats"""
import sys,os,json,gzip,csv,glob
sys.path+=glob.glob(os.path.expanduser('~/mnt/Kaggriculture/.venv/lib/python3.13/site-packages'))[:1]  # Cowork VM; on the Mac the venv python already has it
def main():
    tag=sys.argv[1]; H='experiments/exp060_mbr/holdout'; os.makedirs(f'{H}/tapes',exist_ok=True)
    SRC=os.environ.get('M3_SRC','analysis/hosted_x0930'); RAW=os.environ.get('M3_RAW','private_artifacts/hosted_x0930/raw')
    MAP=json.loads(os.environ.get('M3_MAP','{"X":"X","d157r":"d157r"}')); LIM=int(os.environ.get('M3_LIMIT','100000'))
    NEW=[]
    for r in ([] if os.environ.get('M3_NONEW') else csv.DictReader(open(f'{SRC}/opponents.csv'))):
        if r['submission_label'] not in MAP or sum(1 for x in NEW if x['sub']==MAP[r['submission_label']])>=LIM: continue
        r['submission_label']=MAP[r['submission_label']]
        p=f"{RAW}/{r['episode']}.json.gz"
        if not os.path.exists(p): continue
        d=json.load(gzip.open(p)); s=int(r['seat']); o=1-s; seed=int(d['info']['seed'])
        tape=[d['steps'][k+1][o]['action'] for k in range(len(d['steps'])-1)]
        tp=f"{H}/tapes/N{r['episode']}.py"
        open(tp,'w').write('import json\nTAPE=json.loads('+repr(json.dumps(tape))+')\ndef tape_agent(obs, configuration=None):\n    s=int(obs["step"])\n    return TAPE[s] if s<len(TAPE) else {"farmer":["PASS"],"hands":[],"market":[]}\n')
        NEW.append({'opp':f"N{r['episode']}",'tape':tp,'seed':seed,'seat':s,'panel':'NEW','sub':r['submission_label'],'result':r['result'],
                    'margin':float(r['margin']),'op_sub':r['op_submissionId'],'op_lb':r['op_lb_score'],'fp':r['label'],'end':r['endTime'],'status':d['steps'][-1][s].get('status'),'rew':[d['steps'][-1][0].get('reward'),d['steps'][-1][1].get('reward')]})
    HF=[] if os.environ.get('M3_NOHF') else [{'opp':j[0],'tape':j[1],'seed':j[2],'seat':j[3],'panel':'HF','sub':j[5],'fp':j[6]} for j in json.load(open('experiments/slot2_x/holdout/HF.json'))]
    P=HF+NEW
    sys.path.insert(0,'experiments/exp060_mbr'); import m0_pool
    from multiprocessing import Pool
    with Pool(3) as pl: F=pl.map(m0_pool.one,[{'tape':x['tape'],'seed':x['seed'],'seat':x['seat']} for x in P])
    for x,f in zip(P,F): x['mirror']=f['mirror']; x['shops']=f['shops']; x['m0_err']=f['err']
    json.dump(P,open(f'{H}/panel-{tag}.json','w'),indent=0)
    man=json.load(open(f'experiments/exp060_mbr/cand/manifest-{tag}.json'))
    ARM={'Cd':man[f'Cd_{tag}']['path'],'Cc':man[f'Cc_{tag}']['path'],'X':'releases/slot2r-Rc26_107/main.py','d157':'releases/exp035-d157/main.py','c26':'experiments/exp039_camargin/variants/c26.py'}
    EX='experiments/exp060_mbr/cand/extra_arms.json'
    if os.path.exists(EX): ARM.update(json.load(open(EX)))  # A1 보충: 다른 팀 기록 없는 예비 후보 Cn (panel 만, closed-loop 은 따로)
    jobs=[[a,p,x['opp'],x['tape'],x['seed'],x['seat']] for x in P for a,p in ARM.items()]
    OPP={'d157':'releases/exp035-d157/main.py','D55':'releases/public-dpnew-55be5d5f-exact/main.py'}
    jobs+=[] if os.environ.get('M3_NOCLOSED') else [[a,ARM[a],o,op,sd,st] for a in ('Cd','Cc','X') for o,op in OPP.items() for sd in range(60000,60040) for st in (0,1)]
    jobs.sort(key=lambda j:(j[4],j[5],j[0]))
    jk=[j for i,j in enumerate(jobs) if i%5<3]; jm=[j for i,j in enumerate(jobs) if i%5>=3]
    json.dump(jk,open(f'experiments/exp060_mbr/jobs-m3-{tag}-kaggle.json','w')); json.dump(jm,open(f'experiments/exp060_mbr/jobs-m3-{tag}-mac.json','w'))
    print('HF',len(HF),'NEW',len(NEW),'NEW by sub',{s:sum(1 for x in NEW if x['sub']==s) for s in ('X','d157r')},'mirror',sum(1 for x in P if x['mirror']),'m0 err',sum(1 for x in P if x['m0_err']),'jobs',len(jobs),len(jk),len(jm))

if __name__=='__main__':
    main()