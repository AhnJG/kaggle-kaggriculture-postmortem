import sys,json,hashlib
B={'d157':('releases/exp035-d157/main.py','94a46c11'),'c26':('experiments/exp039_camargin/variants/c26.py','ff230c83')}
M='experiments/slot2_x/manifest.json';man=json.load(open(M))
for b,(p,sh) in B.items():
    base=open(p).read();assert hashlib.sha256(base.encode()).hexdigest().startswith(sh),(p,hashlib.sha256(base.encode()).hexdigest()[:8])
    for r in (107,103,105,0):
        name=f'R{b}_{r}';src=base+open('experiments/slot2_x/rg_layer.py').read().replace('__R__',str(r))
        open(f'experiments/slot2_x/variants/{name}.py','w').write(src)
        man[name]={'path':f'experiments/slot2_x/variants/{name}.py','base':b,'route':r,'sha256':hashlib.sha256(src.encode()).hexdigest()};print(name,man[name]['sha256'][:12])
json.dump(man,open(M,'w'),indent=1)
