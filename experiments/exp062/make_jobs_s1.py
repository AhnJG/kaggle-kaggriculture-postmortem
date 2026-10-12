import json,random,hashlib
POOL={'d157':'releases/exp035-d157/main.py','D55':'releases/public-dpnew-55be5d5f-exact/main.py',
 'HL63':'analysis/daily_scan/20260928/extracted/kaggriculture-harvest-ledger/main.py',
 'M2965':'analysis/daily_scan/20260928/extracted/2965-master-engine/main.py',
 'FJ1010':'analysis/daily_scan/20260928/extracted/farmer-john-and-the-idle-seller/main.py',
 'c26':'releases/exp039-c26/main.py','X':'releases/slot2r-Rc26_107/main.py',
 'N127':'releases/public-newmeta-127ed3e6-exact/main.py','DP24':'releases/public-tetsutani-demand-preserving-0924-exact/main.py'}
C={'d157':'releases/exp035-d157/main.py'}
for n in ['GMm15','GMm08','GMp08','GMp15','HZ08','HZ24','HZ64']: C[n]=f'experiments/exp062/variants/{n}.py'
for n in ['K1','K2','K3','K4','K5','K6','K7','K8','G_A','G_B','B6']: C['E45'+n]=f'experiments/exp045_sale/variants/{n}.py'
rng=random.Random(62001);SEEDS=[rng.randrange(1,2**31-1) for _ in range(20)]
J=[]
for s in SEEDS:
  for seat in (0,1):
    for o,op in POOL.items():
      for c,cp in C.items():
        if c=='d157' and o=='d157': continue
        J.append([c,cp,o,op,s,seat])
rng.shuffle(J)
k=[j for i,j in enumerate(J) if i%5 in (0,1)]; m=[j for i,j in enumerate(J) if i%5 not in (0,1)]
json.dump(J,open('experiments/exp062/jobs-s1-all.json','w'));json.dump(k,open('experiments/exp062/jobs-s1-kaggle.json','w'));json.dump(m,open('experiments/exp062/jobs-s1-mac.json','w'))
json.dump({'seeds':SEEDS,'pool':POOL,'cands':C},open('experiments/exp062/s1_design.json','w'),indent=1)
print(len(J),len(k),len(m),SEEDS[:3])
