"""EXP-060 M2 builder (Claude 09-30 01:00 KST). PREREG: group top3 FM (M1 score, tie margin) + d157 + FM107; EXP-061 donor arms passing their screen join their group (max 5)."""
import json,hashlib
V=json.load(open('experiments/exp060_mbr/m1_verdict.json'))
man=json.load(open('experiments/exp060_mbr/manifest.json')); dman=json.load(open('experiments/exp061_donor/manifest.json'))
C=json.load(open('experiments/exp060_mbr/sets.json'))['confirm']
DN={'Y':['DN29','DN27'],'D':[],'S':[]}
arms={}
for g in ('Y','D','S'):
    a=list(dict.fromkeys(V[g]['top3']+['d157','FM107']))
    arms[g]=[(x,man[x]['path']) for x in a]+[(x,dman[x]['path']) for x in DN[g]]
jobs=[]
for g in ('Y','D','S'):
    for x in [c for c in C if c['group']==g]:
        for n,p in arms[g]: jobs.append([n,p,x['tape'].split('/')[-1][:-3],x['tape'],x['seed'],x['seat']])
jobs.sort(key=lambda j:(j[4],j[5],j[0]))
jk=[j for i,j in enumerate(jobs) if i%5<3]; jm=[j for i,j in enumerate(jobs) if i%5>=3]
json.dump(jk,open('experiments/exp060_mbr/jobs-m2-kaggle.json','w')); json.dump(jm,open('experiments/exp060_mbr/jobs-m2-mac.json','w'))
json.dump({g:[n for n,_ in arms[g]] for g in arms},open('experiments/exp060_mbr/m2_arms.json','w'))
print({g:[n for n,_ in arms[g]] for g in arms},'jobs',len(jobs),len(jk),len(jm))
