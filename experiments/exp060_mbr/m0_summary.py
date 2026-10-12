import json,collections,sys
sys.path.insert(0,'.')
EFF={tuple(k.split('|')):v for k,v in json.load(open('experiments/exp058_route/effective_route_by_pair.json')).items()}
def grp(p):
    r=EFF.get(tuple(p)) if p else None
    return None if r is None else 'Y' if r==9 else 'D' if r==105 else 'S'
R={}
for l in open('experiments/exp060_mbr/m0.jsonl'):
    x=json.loads(l); R[(x['seed'],x['seat'])]=x
R=list(R.values())
for x in R: x['group']=grp(x['shops'])
print('unique',len(R),'err',sum(1 for x in R if x['err']),'mirror',sum(1 for x in R if x['mirror']))
c=collections.Counter((x['tape'].split('/')[1],x['mirror'],x['group']) for x in R if not x['err'])
panels=sorted(set(k[0] for k in c))
for p in panels: print(p,{g:(c[(p,True,g)],c[(p,False,g)]) for g in ('Y','D','S',None)})
tot=collections.Counter((x['group']) for x in R if x['mirror']); print('mirror by group',tot)
json.dump(R,open('experiments/exp060_mbr/m0_final.json','w'))
# validation vs S panel act_sha-based flags
A={}
for f,v in (('experiments/exp051_curpop/games.jsonl','c26'),('experiments/slot2_x/games-Rc26_103.jsonl','R')):
    for l in open(f):
        r=json.loads(l)
        if r['vid'] in ('c26','Rc26_103'): A[(r['vid'],r['seed'],r['seat'])]=r['act_sha']
ok=bad=0
for x in R:
    if 'exp051_curpop' in x['tape'] and ('c26',x['seed'],x['seat']) in A and ('Rc26_103',x['seed'],x['seat']) in A:
        m2=A[('c26',x['seed'],x['seat'])]!=A[('Rc26_103',x['seed'],x['seat'])]
        ok+= (m2==x['mirror']); bad+=(m2!=x['mirror'])
print('S-panel agreement with act_sha flags',ok,'disagree',bad)
