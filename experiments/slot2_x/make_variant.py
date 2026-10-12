"""python3 experiments/slot2_x/make_variant.py NAME '{"K":10,"D0":9,"LAST":18,"FERT":1,"WBUY":0,"SELLH":13}'"""
import sys,json,hashlib
name,cfg=sys.argv[1],json.loads(sys.argv[2])
base=open('releases/exp035-d157/main.py').read()
assert hashlib.sha256(base.encode()).hexdigest().startswith('94a46c11'),'parent sha'
layer=open('experiments/slot2_x/tx_layer.py').read().replace('__TX_CFG__',repr(cfg))
src=base+layer; p=f'experiments/slot2_x/variants/{name}.py'; open(p,'w').write(src)
m='experiments/slot2_x/manifest.json'
try: M=json.load(open(m))
except Exception: M={}
M[name]={'path':p,'cfg':cfg,'sha256':hashlib.sha256(src.encode()).hexdigest()}; json.dump(M,open(m,'w'),indent=1); print(name,M[name]['sha256'][:12])
