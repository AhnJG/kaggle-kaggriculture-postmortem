"""EXP-060 M1 builder (Claude 09-29, before results). Variants FM{r}, screen set, jobs."""
import json,hashlib,os,collections,zlib,base64
B='releases/exp035-d157/main.py'; base=open(B).read()
assert hashlib.sha256(base.encode()).hexdigest().startswith('94a46c11')
g={'json':json,'zlib':zlib,'base64':base64}
exec([l for l in base.split('\n') if l.startswith('_R108_DATA=')][0],g)
ROUTES=sorted(int(k) for k in g['_R108_DATA']['routes']); assert len(ROUTES)==41
layer=open('experiments/slot2_x/rg_layer.py').read()
os.makedirs('experiments/exp060_mbr/variants',exist_ok=True); man={}
for r in ROUTES:
    src=base+layer.replace('__R__',str(r)); p=f'experiments/exp060_mbr/variants/FM{r}.py'; open(p,'w').write(src)
    man[f'FM{r}']={'path':p,'route':r,'sha256':hashlib.sha256(src.encode()).hexdigest()}
man['d157']={'path':B,'sha256':hashlib.sha256(base.encode()).hexdigest()}
R=[x for x in json.load(open('experiments/exp060_mbr/m0_final.json')) if x['mirror'] and not x['err'] and x['group']]
R.sort(key=lambda x:(x['tape'].split('/')[1],x['tape'],x['seat']))
screen=[]
for grp in ('Y','D','S'):
    by=collections.defaultdict(list)
    for x in R:
        if x['group']==grp: by[x['tape'].split('/')[1]].append(x)
    pan=sorted(by); i=0; pick=[]
    while len(pick)<40:
        q=by[pan[i%len(pan)]]
        if q: pick.append(q.pop(0))
        i+=1
    screen+=pick
sk={(x['seed'],x['seat']) for x in screen}
confirm=[x for x in R if (x['seed'],x['seat']) not in sk]
json.dump({'screen':screen,'confirm':confirm},open('experiments/exp060_mbr/sets.json','w'))
jobs=[[v,m['path'],os.path.basename(x['tape'])[:-3],x['tape'],x['seed'],x['seat']] for v,m in man.items() for x in screen]
jobs.sort(key=lambda j:(j[4],j[5],j[0]))
jk=[j for i,j in enumerate(jobs) if i%5<3]; jm=[j for i,j in enumerate(jobs) if i%5>=3]
json.dump(jk,open('experiments/exp060_mbr/jobs-m1-kaggle.json','w')); json.dump(jm,open('experiments/exp060_mbr/jobs-m1-mac.json','w'))
json.dump(man,open('experiments/exp060_mbr/manifest.json','w'),indent=1)
print('screen',collections.Counter(x['group'] for x in screen),'confirm',collections.Counter(x['group'] for x in confirm),'jobs',len(jobs),len(jk),len(jm))
