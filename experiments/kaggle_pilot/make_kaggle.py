"""Shard a jobs file onto N private Kaggle CPU kernels (Claude 09-27). stdlib. Run from repo root:
python experiments/kaggle_pilot/make_kaggle.py <kaggle_user> <jobs.json> <tag> <nshards>
Writes experiments/kaggle_runs/<tag>/{dataset/, kernel0..N-1/, map.json}. Keys (vid|opp|seed|seat) are unchanged."""
import json,hashlib,shutil,sys,pathlib
user,jf,tag,n=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
R=pathlib.Path('experiments/kaggle_runs')/tag;D=R/'dataset'
if D.exists():shutil.rmtree(D)
D.mkdir(parents=True)
jobs=json.load(open(jf));flat={}
def put(p):
    if p not in flat:
        b=open(p,'rb').read();nm='f_'+hashlib.sha256(b).hexdigest()[:16]+'.py';(D/nm).write_bytes(b);flat[p]=nm
    return flat[p]
fj=[[v,put(p),o,put(op),s,t] for v,p,o,op,s,t in jobs]
shutil.copy('experiments/exp024_round2/run.py',D/'run_exp024.py')
for k in range(n):json.dump(fj[k::n],open(D/f'jobs-{k}.json','w'))
json.dump({'jobs':jf,'jobs_sha':hashlib.sha256(open(jf,'rb').read()).hexdigest(),'n':len(jobs),'map':flat},open(R/'map.json','w'),indent=1)
ds=f'{user}/kaggriculture-{tag}'
json.dump({'title':f'kaggriculture-{tag}','id':ds,'licenses':[{'name':'other'}]},open(D/'dataset-metadata.json','w'),indent=1)
tpl=open('experiments/kaggle_pilot/kernel/pilot_kernel.py').read()
assert "'jobs-pilot.json'" in tpl and "/kaggle/working/games-pilot.jsonl" in tpl and "/kaggle/input/**/jobs-pilot.json" in tpl
for k in range(n):
    K=R/f'kernel{k}';K.mkdir(exist_ok=True)
    code=tpl.replace("/kaggle/input/**/jobs-pilot.json","/kaggle/input/**/jobs-0.json").replace("'jobs-pilot.json'",f"'jobs-{k}.json'").replace('/kaggle/working/games-pilot.jsonl',f'/kaggle/working/games-{k}.jsonl')
    (K/'run_kernel.py').write_text(code)
    json.dump({'id':f'{user}/kaggriculture-{tag}-k{k}','title':f'kaggriculture-{tag}-k{k}','code_file':'run_kernel.py','language':'python',
               'kernel_type':'script','is_private':True,'enable_gpu':False,'enable_tpu':False,'enable_internet':True,
               'dataset_sources':[ds],'competition_sources':[],'kernel_sources':[]},open(K/'kernel-metadata.json','w'),indent=1)
print('jobs',len(jobs),'files',len(flat),'shards',n,'per_shard',[len(fj[k::n]) for k in range(n)])
