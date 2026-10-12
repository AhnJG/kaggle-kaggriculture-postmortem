import json,os
from common26 import *
if __name__=='__main__':
    sel=json.load(open(OUT+'/screen-summary.json'))['selected'];assert sel,'NO_ADVANCE'
    v={x['id']:x for x in json.load(open(OUT+'/variants.json'))}
    tv={x['episode']:x for x in json.load(open('analysis/exp025b_nearclone/tapes_verified.json'))}
    eps=json.load(open(OUT+'/tape-split.json'))['stage2'];tapes=[(e,tv[e]['nearclone_seat']) for e in eps]
    jobs=[('P',PARENT,e,ns) for e,ns in tapes]+[(i,v[i]['path'],e,ns) for i in sel for e,ns in tapes]
    json.dump(jobs,open(OUT+'/jobs-stage2.json','w'));print('stage2 jobs',len(jobs),flush=True)
    run(jobs,OUT+'/games-stage2.jsonl',int(os.environ.get('W','5')))
