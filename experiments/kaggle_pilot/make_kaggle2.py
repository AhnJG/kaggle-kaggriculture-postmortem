"""Like make_kaggle.py but ships agent/tape files as ONE bundle.tgz (avoids per-file upload failures seen in EXP-033).
python experiments/kaggle_pilot/make_kaggle2.py <kaggle_user> <jobs.json> <tag> <nshards>"""
import json,hashlib,shutil,sys,pathlib,tarfile
user,jf,tag,n=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
R=pathlib.Path('experiments/kaggle_runs')/tag;D=R/'dataset'
if D.exists():shutil.rmtree(D)
D.mkdir(parents=True)
jobs=json.load(open(jf));flat={}
def put(p):
    if p not in flat:flat[p]='f_'+hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]+'.py'
    return flat[p]
fj=[[v,put(p),o,put(op),s,t] for v,p,o,op,s,t in jobs]
with tarfile.open(D/'bundle.tgz','w:gz',format=tarfile.USTAR_FORMAT) as tf:
    for p,nm in flat.items():tf.add(p,arcname=nm)
shutil.copy('experiments/exp024_round2/run.py',D/'run_exp024.py')
for k in range(n):json.dump(fj[k::n],open(D/f'jobs-{k}.json','w'))
json.dump({'jobs':jf,'jobs_sha':hashlib.sha256(open(jf,'rb').read()).hexdigest(),'n':len(jobs),'map':flat},open(R/'map.json','w'),indent=1)
ds=f'{user}/kaggriculture-{tag}'
json.dump({'title':f'kaggriculture-{tag}','id':ds,'licenses':[{'name':'other'}]},open(D/'dataset-metadata.json','w'),indent=1)
tpl=open('experiments/kaggle_pilot/kernel/pilot_kernel.py').read()
old="for f in glob.glob(os.path.join(os.path.dirname(src), '*')):\n    shutil.copy(f, W)\n"
new=("import tarfile\nfor f in glob.glob('/kaggle/input/**/*', recursive=True):\n    if os.path.isfile(f):\n"
     "        if f.endswith('.tgz'):\n            tarfile.open(f).extractall(W)\n        else:\n            shutil.copy(f, os.path.join(W, os.path.basename(f)))\n")
assert old in tpl,'template changed'
for k in range(n):
    K=R/f'kernel{k}';K.mkdir(exist_ok=True)
    code=tpl.replace(old,new).replace("/kaggle/input/**/jobs-pilot.json","/kaggle/input/**/jobs-0.json").replace("'jobs-pilot.json'",f"'jobs-{k}.json'").replace('/kaggle/working/games-pilot.jsonl',f'/kaggle/working/games-{k}.jsonl')
    (K/'run_kernel.py').write_text(code)
    json.dump({'id':f'{user}/kaggriculture-{tag}-k{k}','title':f'kaggriculture-{tag}-k{k}','code_file':'run_kernel.py','language':'python',
               'kernel_type':'script','is_private':True,'enable_gpu':False,'enable_tpu':False,'enable_internet':True,
               'dataset_sources':[ds],'competition_sources':[],'kernel_sources':[]},open(K/'kernel-metadata.json','w'),indent=1)
print('jobs',len(jobs),'files',len(flat),'bundle MB',round((D/'bundle.tgz').stat().st_size/1e6,1),'shards',n,'per_shard',[len(fj[k::n]) for k in range(n)])
