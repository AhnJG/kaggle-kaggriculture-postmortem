import json,collections,statistics as st
M={f"C{m['episode']}":m for m in json.load(open('experiments/exp051_curpop/meta.json'))}
G=collections.defaultdict(dict);A=collections.defaultdict(dict);bad=collections.Counter()
for f in ('experiments/exp051_curpop/games.jsonl','experiments/exp054_tomgate/games-curpop.jsonl'):
    for l in open(f):
        r=json.loads(l)
        if r['score'] is None or r['err'] or r['agent_errors']:bad[r['vid']]+=1;continue
        G[r['vid']][r['opponent']]=r['score'];A[r['vid']][r['opponent']]=(r['act_sha'],r['margin'])
print('invalid',dict(bad))
def band(x):x=float(x or 0);return '<2000' if x<2000 else '2000-2200' if x<2200 else '2200-2400' if x<2400 else '2400+'
for v in ('X7','X6'):
    O=[o for o in G['c26'] if o in G[v]];d=[G[v][o]-G['c26'][o] for o in O]
    ch=[o for o in O if A[v][o][0]!=A['c26'][o][0]];dc=[G[v][o]-G['c26'][o] for o in ch]
    mg=[A[v][o][1]-A['c26'][o][1] for o in ch]
    mu=st.mean(d);se=(st.pvariance(d)/len(d))**.5
    print(f"{v}: n={len(O)} c26 {st.mean(G['c26'][o] for o in O):.3f} {v} {st.mean(G[v][o] for o in O):.3f} Δ {mu:+.4f} (SE {se:.4f}) | changed games {len(ch)} Δ(changed) {st.mean(dc) if dc else 0:+.3f} margin Δ median {st.median(mg) if mg else 0:+.0f} W→L/L→W {sum(x<0 for x in dc)}/{sum(x>0 for x in dc)}")
    for b in ('<2000','2000-2200','2200-2400','2400+'):
        S=[o for o in O if band(M[o]['op_lb'])==b]
        if S:print(f'    {b:10s} n={len(S):3d} Δ {st.mean(G[v][o]-G["c26"][o] for o in S):+.3f}')
    print('  STAGE1', 'PASS' if mu>0 and dc and st.mean(dc)>0 else 'FAIL')
