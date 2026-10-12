"""EXP-027 = EXP-026 Stage 3 (Claude). Closed-loop guards for near-clone-screen winners. Pure stdlib; run from repo root."""
import hashlib,json,os
from pathlib import Path
ROOT=Path('.');OUT=ROOT/'experiments/exp027_stage3';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
P='releases/round2-v074/main.py';assert sha(P)=='860a502c36f9a9f700c93125e6828f41378f50d74fa130f62a09f911316ea19c'
O1='releases/public-newmeta-127ed3e6-exact/main.py';assert sha(O1).startswith('127ed3e6')
DP='releases/public-tetsutani-demand-preserving-0924-exact/main.py';assert sha(DP).startswith('178ae0f7')
V={x['id']:x for x in json.load(open('experiments/exp026_nearclone/variants.json'))}
SINGLES=['w129','w060','w034','w067']
for s in SINGLES:assert sha(V[s]['path'])==V[s]['sha256'],s
# combo of the three low-risk winners (w067 excluded: same change as EXP-024 v111 which failed public/hosted guards)
src=Path(P).read_bytes()
txt='\n# Frozen EXP-027 wrapper; parent bytes above are unchanged.\n_EXP027_ENTRY = [v for v in globals().values() if callable(v)][-1]\n'
for s in ['w129','w060','w034']:c=V[s]['change'];txt+=f"{c['target']} = {c['new']!r}\n"
txt+='def exp027_entry(obs, configuration=None):\n    return _EXP027_ENTRY(obs, configuration)\n'
cp=OUT/'c3.py';cp.write_bytes(src+txt.encode())
CANDS=[(s,V[s]['path']) for s in SINGLES]+[('c3',str(cp))]
PAIRED=CANDS+[('P',P)]
st=json.load(open('experiments/exp023_mirror_screen/stage3-opponents.json'))
guard=[dict(id=f'PUB{i:02d}',path=x['path']) for i,x in enumerate(st['public_top15'][1:])]
G26=['a-song-of-ice-and-fire-fixed-flexible','kaggriculture-harvest-ledger','kaggriculture-multi-route-farming-agent','kaggriculture-top-2-master-engine-v4','kaggriculture-hack']
guard+=[dict(id=f'G26{i:02d}',path=f'analysis/daily_scan/20260926/extracted/{d}/main.py') for i,d in enumerate(G26)]
G27=['demand-preserving-turn-sale-timing','farmer-john-and-the-idle-seller','farmer-john-and-the-wheat-seller','kaggriculture-harvest-ledger','the-2965-master-hybrid-engine']
guard+=[dict(id=f'G27{i:02d}',path=f'analysis/daily_scan/20260927/extracted/{d}/main.py') for i,d in enumerate(G27)]
seen=set();g2=[]
for g in guard:
    h=sha(g['path']);g['sha256']=h
    if h in seen or h.startswith('127ed3e6'):continue
    seen.add(h);g2.append(g)
guard=g2
jobs=[]
def panel(agents,oid,op,seeds):
    for v,p in agents:
        for s in seeds:
            for t in (0,1):jobs.append([v,str(p),oid,str(op),s,t])
panel(PAIRED,'AP-O1',O1,range(11000,11200))
panel(PAIRED,'B-DP',DP,range(11200,11300))
for g in guard:panel(PAIRED,g['id'],g['path'],range(11300,11310))
eps=json.load(open('experiments/p4b_20260926/episodes.json'))
for i,e in enumerate(eps):
    assert not 9000<=e['seed']<=9599
    for v,p in PAIRED:jobs.append([v,str(p),f"H{i:03d}-E{e['id']}",e['opp_path'],e['seed'],e['seat']])
keys=[f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' for j in jobs];assert len(keys)==len(set(keys))
json.dump(jobs,open(OUT/'jobs-closed.json','w'))
# N panel: combo only, on the 160 EXP-026 stage2 tapes (open-loop), vs baseline already in games-stage2.jsonl
tv={x['episode']:x for x in json.load(open('analysis/exp025b_nearclone/tapes_verified.json'))}
n_eps=json.load(open('experiments/exp026_nearclone/tape-split.json'))['stage2']
json.dump([['c3',str(cp),e,tv[e]['nearclone_seat']] for e in n_eps],open(OUT/'jobs-n.json','w'))
man=dict(parent=P,candidates={v:sha(p) for v,p in CANDS},guard=guard,guard_n=len(guard),hosted_rows=len(eps),
         jobs_closed=len(jobs),jobs_n=len(n_eps),jobs_closed_sha=sha(OUT/'jobs-closed.json'),seeds=dict(AP=[11000,11199],B=[11200,11299],CD=[11300,11309]))
json.dump(man,open(OUT/'manifest.json','w'),indent=1)
print(json.dumps({k:v for k,v in man.items() if k!='guard'}))
