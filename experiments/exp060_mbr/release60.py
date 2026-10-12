"""Release builder for the EXP-060 winner (Claude 09-30). Usage: python release60.py <cand name e.g. Cd_final> <tag>
Same format as releases/exp058-* : USTAR tar with main.py only (mtime 0, uid/gid 0), NOTICE.txt from d157 release, SHA256SUMS.
Then D3: D3_CAND=releases/exp060-<name>/main.py D3_CAND_SHA=<sha> D3_RESULT=../../releases/exp060-<name>/gate-d3-result.json python3 experiments/d3_gate_v2/measure_gate_v2_claude.py"""
import sys,os,io,tarfile,hashlib,shutil,json
v,tag=sys.argv[1],sys.argv[2]; man=json.load(open(f'experiments/exp060_mbr/cand/manifest-{tag}.json'))
src=man[v]['path']; out=f'releases/exp060-{v}'; os.makedirs(out,exist_ok=True)
b=open(src,'rb').read(); assert hashlib.sha256(b).hexdigest()==man[v]['sha256']
open(f'{out}/main.py','wb').write(b); shutil.copy('releases/exp035-d157/NOTICE.txt',f'{out}/NOTICE.txt')
with tarfile.open(f'{out}/submission.tar.gz','w:gz',format=tarfile.USTAR_FORMAT) as t:
    ti=tarfile.TarInfo('main.py');ti.size=len(b);ti.mtime=0;ti.mode=0o644;ti.uid=ti.gid=0;ti.uname=ti.gname='';t.addfile(ti,io.BytesIO(b))
S=[(hashlib.sha256(open(f'{out}/{f}','rb').read()).hexdigest(),f) for f in ('main.py','submission.tar.gz','NOTICE.txt')]
open(f'{out}/SHA256SUMS','w').write(''.join(f'{h}  {f}\n' for h,f in S)); print(open(f'{out}/SHA256SUMS').read())
