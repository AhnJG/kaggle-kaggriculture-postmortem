"""EXP-025b re-verification (Claude). For every row: the non-nearclone seat must be 127ed3e6 exact for all 720 steps
(full_match -> None); also recompute the nearclone divergence step. Output analysis/exp025b_nearclone/tapes_verified.json."""
import json,os,sys
from multiprocessing import Pool
sys.path.insert(0,'experiments/exp025_recon')
from recon import full_match
F='releases/public-newmeta-127ed3e6-exact/main.py'
R='private_artifacts/exp025b_nearclone/raw/'
def f(x):
    p=R+f"{x['episode']}.json.gz";ns=x['nearclone_seat']
    try:
        a=full_match(p,1-ns,F);b=full_match(p,ns,F)
        # No seat swapping: the labelled nearclone seat must diverge (b>=1) and the other seat must be FULL 127ed3e6.
        return dict(x,opp_first_mismatch=a,divergence_step=b,valid=(a is None and b is not None and b>=1))
    except Exception as e:return dict(x,valid=False,err=repr(e)[:200])
if __name__=='__main__':
    rows=json.load(open('analysis/exp025b_nearclone/tapes.json'))
    with Pool(5) as p:out=list(p.imap(f,rows,chunksize=4))
    # result/margin are re-derived from raw for the (possibly swapped) nearclone seat
    import gzip
    for o in out:
        if o.get('valid'):
            raw=json.load(gzip.open(R+f"{o['episode']}.json.gz"));rw=[s['reward'] for s in raw['steps'][-1]];ns=o['nearclone_seat']
            m=rw[ns]-rw[1-ns];o['margin']=m;o['result']='W' if m>0 else 'L' if m<0 else 'D';o['seed']=int(raw['info']['seed'])
    json.dump(out,open('analysis/exp025b_nearclone/tapes_verified.json','w'),indent=1)
    v=[o for o in out if o.get('valid')]
    import collections
    print(json.dumps(dict(rows=len(out),valid=len(v),errors=sum('err' in o for o in out),
      results=dict(collections.Counter(o['result'] for o in v)),by_sub=dict(collections.Counter(o['nearclone_submission'] for o in v)))))
