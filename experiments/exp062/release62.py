"""Release builder for EXP-062 winner. Usage: python release62.py <variant name>  -> releases/exp062-<name>/ (main.py, submission.tar.gz USTAR mtime0, NOTICE.txt, SHA256SUMS)"""
import sys,os,io,tarfile,hashlib,shutil,json,glob
v=sys.argv[1]; src=f'experiments/exp062/variants/{v}.py'; out=f'releases/exp062-{v}'; os.makedirs(out,exist_ok=True)
man={}
for f in glob.glob('experiments/exp062/variants/manifest_*.json'): man.update(json.load(open(f)))
b=open(src,'rb').read(); assert hashlib.sha256(b).hexdigest()==man[v]['sha256'],'sha mismatch vs manifest'
open(f'{out}/main.py','wb').write(b); shutil.copy('releases/exp035-d157/NOTICE.txt',f'{out}/NOTICE.txt')
with tarfile.open(f'{out}/submission.tar.gz','w:gz',format=tarfile.USTAR_FORMAT) as t:
    ti=tarfile.TarInfo('main.py');ti.size=len(b);ti.mtime=0;ti.mode=0o644;ti.uid=ti.gid=0;ti.uname=ti.gname='';t.addfile(ti,io.BytesIO(b))
S=[(hashlib.sha256(open(f'{out}/{f}','rb').read()).hexdigest(),f) for f in ('main.py','submission.tar.gz','NOTICE.txt')]
open(f'{out}/SHA256SUMS','w').write(''.join(f'{h}  {f}\n' for h,f in S)); print(open(f'{out}/SHA256SUMS').read())
# tar round-trip check
with tarfile.open(f'{out}/submission.tar.gz') as t:
    names=t.getnames(); data=t.extractfile('main.py').read()
assert names==['main.py'] and data==b, 'tar roundtrip failed'
print('tar ok', names, len(data))
