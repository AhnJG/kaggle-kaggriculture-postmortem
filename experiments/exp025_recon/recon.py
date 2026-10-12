"""Near-clone reconstruction: longest prefix where a candidate file reproduces the hosted opponent's actions.
Our side = our submitted bot (must reproduce exactly); opponent side = candidate. Stops at first opponent mismatch."""
import sys,json,gzip,io,contextlib
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable
class Diverged(Exception):pass
def norm(a):return json.dumps(a,sort_keys=True,default=str)
def prefix(replay_path,our_seat,our_file,cand_file):
    raw=json.load(gzip.open(replay_path)) if replay_path.endswith('.gz') else json.load(open(replay_path))
    seed=int(raw['info']['seed']);opp=1-our_seat
    tape={k:norm(raw['steps'][k+1][opp]['action']) for k in range(len(raw['steps'])-1)}
    mine={k:norm(raw['steps'][k+1][our_seat]['action']) for k in range(len(raw['steps'])-1)}
    st={'opp':None,'our':None}
    with contextlib.redirect_stdout(io.StringIO()):
        me=get_last_callable(open(our_file).read(),path=our_file);cd=get_last_callable(open(cand_file).read(),path=cand_file)
        def A(obs,cfg):
            a=me(obs,cfg);k=int(obs['step'])
            if st['our'] is None and norm(a)!=mine.get(k):st['our']=k
            return a
        def B(obs,cfg):
            k=int(obs["step"])
            try:a=cd(obs,cfg)
            except Exception:st["opp"]=k;raise Diverged()
            if norm(a)!=tape.get(k):st['opp']=k;raise Diverged()
            return a
        env=make('kaggriculture',configuration={'episodeSteps':720,'seed':seed})
        try:env.run([A,B] if our_seat==0 else [B,A])
        except Diverged:pass
    return dict(opp_prefix=st['opp'] if st['opp'] is not None else 720,our_first_mismatch=st['our'])
if __name__=='__main__':
    print(json.dumps(prefix(sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4])))

def full_match(replay_path,seat,file):
    """Is the player at `seat` exactly `file` for all 720 steps? The other side replays its recorded actions (tape),
    so divergence of the other side cannot stop the check. Returns first mismatch step or None."""
    raw=json.load(gzip.open(replay_path)) if replay_path.endswith('.gz') else json.load(open(replay_path))
    seed=int(raw['info']['seed']);other=1-seat
    mine={k:norm(raw['steps'][k+1][seat]['action']) for k in range(len(raw['steps'])-1)}
    tape=[raw['steps'][k+1][other]['action'] for k in range(len(raw['steps'])-1)]
    st={'first':None}
    with contextlib.redirect_stdout(io.StringIO()):
        me=get_last_callable(open(file).read(),path=file)
        def A(obs,cfg):
            a=me(obs,cfg);k=int(obs['step'])
            if st['first'] is None and norm(a)!=mine.get(k):st['first']=k;raise Diverged()
            return a
        def T(obs,cfg):return tape[int(obs['step'])]
        env=make('kaggriculture',configuration={'episodeSteps':720,'seed':seed})
        try:env.run([A,T] if seat==0 else [T,A])
        except Diverged:pass
    return st['first']
