# What was executed (inline) for the 31 EXP-017 local games: EXP-017 in DSM's seat vs EXP-016, seed chosen by shoppred so the first two shops equal the DSM game's.
import json, instr, time
plan=json.load(open('plan17.json'))
E17='K/releases/f0-omw-adv-exp017/main.py'; E16='K/releases/f0-c1-adv-exp016/main.py'
out=open('exp17_local.jsonl','w')
for p in plan:
    t0=time.time()
    agents=[E17,E16] if p['seat']==0 else [E16,E17]
    r=instr.run(agents,p['seed'])
    r.update(pair=p['pair'],exp17_seat=p['seat'],dsm_eps=p['dsm_eps'],secs=round(time.time()-t0,1))
    out.write(json.dumps(r)+'\n'); out.flush()
