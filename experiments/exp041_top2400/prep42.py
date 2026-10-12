"""EXP-042 (Claude 09-28 17:00 KST): 2400+ tape panel (750 tapes of 24 top teams; our bot takes their opponent's seat).
Candidates: d157, c26 (EXP-039), V074 (reference). Frozen use: panel baseline + c26 slot-2 check. Split: select vs holdout teams (team-split.json)."""
import json
M=list({m['episode']:m for m in json.load(open('experiments/exp041_top2400/meta.json'))}.values())  # dedupe: keep last (= tape file written last)
A=[('d157','releases/exp035-d157/main.py'),('c26','experiments/exp039_camargin/variants/c26.py'),('V074','releases/round2-v074/main.py')]
J=[[v,p,f"X{m['episode']}",f"experiments/exp041_top2400/tapes/X{m['episode']}.py",m['seed'],m['our_seat']] for m in M for v,p in A]
k=[j for i,j in enumerate(J) if i%5<3];mm=[j for i,j in enumerate(J) if i%5>=3]
json.dump(k,open('experiments/exp041_top2400/jobs42-kaggle.json','w'));json.dump(mm,open('experiments/exp041_top2400/jobs42-mac.json','w'));print(len(J),len(k),len(mm))
