"""Release builder for the Stage C winner (Claude 09-29). Usage: python release58.py RG_<G><R>
Same format as releases/exp039-c26: USTAR tar with main.py only (mtime 0, uid/gid 0), NOTICE.txt copied from d157 release, SHA256SUMS.
Run D3 after this: D3_CAND=releases/exp058-<v>/main.py D3_CAND_SHA=<sha> D3_RESULT=../../releases/exp058-<v>/gate-d3-result.json python3 experiments/d3_gate_v2/measure_gate_v2_claude.py"""
import sys,os,io,tarfile,hashlib,shutil,json
v=sys.argv[1];src=f'experiments/exp058_route/variants/{v}.py';out=f'releases/exp058-{v}';os.makedirs(out,exist_ok=True)
b=open(src,'rb').read();assert hashlib.sha256(b).hexdigest()==json.load(open('experiments/exp058_route/manifest.json'))[v]['sha256']
open(f'{out}/main.py','wb').write(b);shutil.copy('releases/exp035-d157/NOTICE.txt',f'{out}/NOTICE.txt')
with tarfile.open(f'{out}/submission.tar.gz','w:gz',format=tarfile.USTAR_FORMAT) as t:
    ti=tarfile.TarInfo('main.py');ti.size=len(b);ti.mtime=0;ti.mode=0o644;ti.uid=ti.gid=0;ti.uname=ti.gname='';t.addfile(ti,io.BytesIO(b))
S=[(hashlib.sha256(open(f'{out}/{f}','rb').read()).hexdigest(),f) for f in ('main.py','submission.tar.gz','NOTICE.txt')]
open(f'{out}/SHA256SUMS','w').write(''.join(f'{h}  {f}\n' for h,f in S));print(open(f'{out}/SHA256SUMS').read())
