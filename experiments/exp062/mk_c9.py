# Claude-B 23:05 KST — C9 confirmation design (PREREG A12). usage: python3 mk_c9.py <W> <W_path>
import json,random,sys
W,WP=sys.argv[1],sys.argv[2]
s8=json.load(open('experiments/exp062/s8_design.json')); s9=json.load(open('experiments/exp062/s9_design.json'))
used=set(s8['seeds'])|set(s9['seeds'])
rng=random.Random(20260930+9); seeds=[]
while len(seeds)<60:
    s=rng.randrange(1,2**31-1)
    if s not in used and s not in seeds: seeds.append(s)
opp_ids=['D55','d157','L5p','VP','L6p','HL63x','M2965','c26','X','N127']
cands={W:WP,'L4p':'experiments/exp062/variants/L4p.py'}
jobs=[[c,p,o,s8['pool'][o],s,s%2] for c,p in cands.items() for o in opp_ids for s in seeds]
rng.shuffle(jobs)
json.dump(jobs,open('experiments/exp062/jobs-c9-kaggle.json','w'))
json.dump({'cands':cands,'opps':{o:s8['pool'][o] for o in opp_ids},'seeds':seeds,'note':'C9 (PREREG A12) winner confirmation, one seat per seed'},open('experiments/exp062/c9_design.json','w'),indent=1)
print('jobs',len(jobs))
