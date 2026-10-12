"""Build SLOT2 holdout panels (Claude 09-29, before any candidate touches them).
HF: d157/c26 hosted episodes with endTime > 2026-09-28T17:27:08Z from analysis/hosted_20260929b (+ later collections passed as args).
HT: exp041 holdout-team tapes + exp049 fresh (parity-ok), excluding target team 'Fritz Cremer'.
Writes experiments/slot2_x/holdout/{HF,HT}.json as job templates [opp_id, opp_path, seed, seat, panel]."""
import json,gzip,csv,os,sys
T0='2026-09-28T17:27:08Z';out='experiments/slot2_x/holdout';HF=[];seen=set()
for src in ['analysis/hosted_20260929b']+sys.argv[1:]:
    raw=src.replace('analysis/','private_artifacts/')+'/raw'
    for r in csv.DictReader(open(f'{src}/opponents.csv')):
        if r['submission_label'] not in ('d157','c26') or r['endTime']<=T0 or r['episode'] in seen:continue
        p=f"{raw}/{r['episode']}.json.gz"
        if not os.path.exists(p):continue
        d=json.load(gzip.open(p));s=int(r['seat']);o=1-s;seed=int(d['info']['seed']);assert not 9000<=seed<9600
        tape=[d['steps'][k+1][o]['action'] for k in range(len(d['steps'])-1)]
        tp=f'{out}/tapes/H{r["episode"]}.py'
        open(tp,'w').write('import json\nTAPE=json.loads('+repr(json.dumps(tape))+')\ndef tape_agent(obs, configuration=None):\n    s=int(obs["step"])\n    return TAPE[s] if s<len(TAPE) else {"farmer":["PASS"],"hands":[],"market":[]}\n')
        HF.append([f"H{r['episode']}",tp,seed,s,'HF',r['submission_label'],r['label']]);seen.add(r['episode'])
B='experiments/exp041_top2400/';Hteams=set(json.load(open(B+'team-split.json'))['holdout_teams'])
M=list({m['episode']:m for m in json.load(open(B+'meta.json'))}.values())
HT=[[f"X{m['episode']}",B+f"tapes/X{m['episode']}.py",m['seed'],m['our_seat'],'HT',m['team'],''] for m in M if m['team'] in Hteams and m['team']!='Fritz Cremer']
F=json.load(open('experiments/exp049_fresh/meta.json'));bad=set(r[0] for r in map(json.loads,open('experiments/exp049_fresh/parity.jsonl')) if not r[1])
HT+=[[f"F{m['episode']}",f"experiments/exp049_fresh/tapes/F{m['episode']}.py",m['seed'],m['our_seat'],'HT',m['team'],''] for m in F if m['episode'] not in bad and m['team']!='Fritz Cremer']
assert not any(9000<=j[2]<9600 for j in HF+HT)
json.dump(HF,open(f'{out}/HF.json','w'));json.dump(HT,open(f'{out}/HT.json','w'))
print('HF',len(HF),'HT',len(HT),'fritz excluded',sum(1 for m in F if m['team']=='Fritz Cremer'))
