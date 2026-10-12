"""EXP-051 current-population tapes (Claude 09-29): opponents of d157/c26 in C26HOSTED (as_of 09-28 17:27 UTC). Tape = opponent's recorded actions."""
import json,gzip,csv
R=list(csv.DictReader(open('analysis/c26_hosted_20260929/opponents.csv')));rows=[];J=[]
B={'d157':'releases/exp035-d157/main.py','c26':'experiments/exp039_camargin/variants/c26.py'}
for r in R:
    raw=json.load(gzip.open(f"private_artifacts/c26_hosted_20260929/raw/{r['episode']}.json.gz"));s=int(r['seat']);o=1-s
    tape=[raw['steps'][k+1][o]['action'] for k in range(len(raw['steps'])-1)]
    src='import json\nTAPE=json.loads('+repr(json.dumps(tape))+')\ndef tape_agent(obs, configuration=None):\n    s=int(obs["step"])\n    return TAPE[s] if s<len(TAPE) else {"farmer":["PASS"],"hands":[],"market":[]}\n'
    open(f"experiments/exp051_curpop/tapes/C{r['episode']}.py",'w').write(src)
    seed=int(raw['info']['seed']);assert not 9000<=seed<9600
    rows.append(dict(episode=r['episode'],sub=r['submission_label'],seat=s,seed=seed,result=r['result'],op_lb=r['op_lb_score'],label=r['label']))
    for v,p in B.items():J.append([v,p,f"C{r['episode']}",f"experiments/exp051_curpop/tapes/C{r['episode']}.py",seed,s])
json.dump(rows,open('experiments/exp051_curpop/meta.json','w'));json.dump(J,open('experiments/exp051_curpop/jobs.json','w'));print(len(rows),len(J))
