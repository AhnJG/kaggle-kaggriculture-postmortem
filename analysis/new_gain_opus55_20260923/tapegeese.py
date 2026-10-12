import json
ns={'__name__':'e17'}
src=open('K/releases/f0-omw-adv-exp017/main.py').read()
exec(compile(src,'main.py','exec'),ns)
IMPL=ns['_IMPL']; routes=IMPL.chassis.routes
def tape_buys(route):
    out={}
    for t,a in enumerate(routes[route]):
        if not isinstance(a,dict): continue
        for o in a.get('market',[]) or []:
            if len(o)>=3 and o[0]=='BUY_ANIMAL': out.setdefault(o[1],[]).append((t,o[2]))
    return out
E=[json.loads(l) for l in open('exp17_local.jsonl')]
for e in E:
    shops=tuple(e['pair'])
    use_new=shops.count('YARN_STORE')<=0
    r=ns['_R108_SHOP_ROUTES'].get(shops,100) if use_new else ns['_R110_OLD_SHOPS'].get(shops,0)
    r=ns['_V92_TABLE'].get(shops,r)
    b=tape_buys(r); s=str(e['exp17_seat'])
    g=[x for x in b.get('GOOSE',[]) if x[0]>=144]
    real=max(x[s]['animals'].get('GOOSE',0) for x in e['snap'])
    realc=max(x[s]['animals'].get('COW',0) for x in e['snap']); reals=max(x[s]['animals'].get('SHEEP',0) for x in e['snap'])
    print('+'.join(shops), 'route',r, 'tape geese>=d6',sum(n for _,n in g), [t for t,_ in g][:3], 'tape cows',sum(n for t,n in b.get('COW',[]) if t>=144),'sheep',sum(n for t,n in b.get('SHEEP',[]) if t>=144),'| real max goose',real,'cow',realc,'sheep',reals)
