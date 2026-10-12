"""Stage C jobs for RG_<G><R> (Claude 09-29, before any result). Panels exactly as PREREG Stage C:
H = exp041 old holdout-team tapes + exp049 fresh part H (baselines: games42 / exp048B rows), F = exp049 fresh part F (baseline exp048B d157 rows),
FAM = exp039 family closed-loop 250 (D, HL63, M2965, FJ1010, d157; seeds 15000-15024 both seats; baseline exp039 d157 rows, d157 self := 0.5).
Usage: python prep58C.py G R"""
import sys,json,collections
G,R=sys.argv[1],int(sys.argv[2]);v=f'RG_{G}{R}';path=f'experiments/exp058_route/variants/{v}.py'
J=[]
B='experiments/exp041_top2400/';H=set(json.load(open(B+'team-split.json'))['holdout_teams'])
M=list({m['episode']:m for m in json.load(open(B+'meta.json'))}.values())
J+=[[v,path,f"X{m['episode']}",B+f"tapes/X{m['episode']}.py",m['seed'],m['our_seat']] for m in M if m['team'] in H]
F=json.load(open('experiments/exp049_fresh/meta.json'));bad=set(r[0] for r in map(json.loads,open('experiments/exp049_fresh/parity.jsonl')) if not r[1])
J+=[[v,path,f"F{m['episode']}",f"experiments/exp049_fresh/tapes/F{m['episode']}.py",m['seed'],m['our_seat']] for m in F if m['episode'] not in bad]
J39=json.load(open('experiments/exp039_camargin/jobs-kaggle.json'))+json.load(open('experiments/exp039_camargin/jobs-mac.json'))
J+=[[v,path]+j[2:] for j in J39 if j[0]=='c26' and j[2] in ('D','HL63','M2965','FJ1010','d157')]
assert not any(9000<=j[4]<9600 for j in J) and len({(j[2],j[4],j[5]) for j in J})==len(J)
k=[j for i,j in enumerate(J) if i%5<3];mm=[j for i,j in enumerate(J) if i%5>=3]
json.dump(k,open(f'experiments/exp058_route/jobsC-kaggle.json','w'));json.dump(mm,open(f'experiments/exp058_route/jobsC-mac.json','w'))
print(len(J),len(k),len(mm),collections.Counter('X' if j[2][0]=='X' else 'F' if j[2][0]=='F' and j[2]!='FJ1010' else 'FAM' for j in J))
