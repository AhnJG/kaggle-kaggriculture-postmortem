import json, sys, instr
ns={'__name__':'e17'}
exec(compile(open('K/releases/f0-omw-adv-exp017/main.py').read(),'main.py','exec'),ns)
agent=[v for v in ns.values() if callable(v)][-1]
E16='K/releases/f0-c1-adv-exp016/main.py'
for seed,seat in [(3000169,1),(3000281,0)]:
    agents=[agent,E16] if seat==0 else [E16,agent]
    r=instr.run(agents,seed)
    s=str(seat)
    print(seed, r['rewards'], 'goose',max(x[s]['animals'].get('GOOSE',0) for x in r['snap']))
    for k in ['_HD2_REPORT','_CS_REPORT','_Y_REPORT','_V9_HERD_REPORT','_VE_REPORT']:
        print('  ',k,ns.get(k))
