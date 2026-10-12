import json,sys,os,hashlib
from common26 import *
if __name__=='__main__':
    os.makedirs(OUT,exist_ok=True)
    v=gen();s=split()
    tapes=[(x['episode'],x['nearclone_seat']) for x in s['screen']]
    jobs=[('P',PARENT,e,ns) for e,ns in tapes]+[(x['id'],x['path'],e,ns) for x in v for e,ns in tapes]
    json.dump(jobs,open(OUT+'/jobs-screen.json','w'))
    print('variants',len(v),'screen tapes',len(tapes),'stage2 tapes',len(s['stage2']),'jobs',len(jobs),flush=True)
    run(jobs,OUT+'/games-screen.jsonl',int(os.environ.get('W','5')))
