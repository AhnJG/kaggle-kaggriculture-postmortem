import json, instr
E17='K/releases/f0-omw-adv-exp017/main.py'; E16='K/releases/f0-c1-adv-exp016/main.py'
for seed,seat,pair in [(3000086,0,'BAKERY+BRUNCH'),(3000281,0,'BRUNCH+PIZZA')]:
    instr.WEEDLOG.clear()
    r=instr.run([E17,E16] if seat==0 else [E16,E17],seed)
    w=instr.WEEDLOG; mine=[w[2*d+seat] for d in range(len(w)//2)]
    print(pair,r['rewards'],'free(None) tiles at EOD by day:',mine)
    print('  quads by day',[x[str(seat)]['quads'] for x in r['snap']])
