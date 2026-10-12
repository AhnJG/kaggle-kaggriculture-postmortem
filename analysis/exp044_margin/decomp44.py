import json,collections,statistics as st
R=[json.loads(l) for l in open('analysis/exp044_margin/d157.jsonl')]
R=[r for r in R if r['rewards']]
def terms(r,byq=False):
    s=r['our_seat'];T=collections.defaultdict(float)
    for se,q,op,it,u,c in r['groups']:
        v=(c if op=='SELL' else -c)*(1 if se==s else -1)
        k=(op,it,q) if byq else (op,it);T[k]+=v
    return T
L=[r for r in R if r['rewards'][r['our_seat']]<r['rewards'][1-r['our_seat']]]
W=[r for r in R if r['rewards'][r['our_seat']]>r['rewards'][1-r['our_seat']]]
mg=lambda r:r['rewards'][r['our_seat']]-r['rewards'][1-r['our_seat']]
print('n',len(R),'W',len(W),'L',len(L),'score',round((len(W)+0.5*(len(R)-len(W)-len(L)))/len(R),3))
print('margin median L',st.median(mg(r) for r in L),'W',st.median(mg(r) for r in W))
for byq in (False,True):
    K=set();[K.update(terms(r,byq)) for r in R]
    rows=[]
    for k in K:
        l=st.mean(terms(r,byq).get(k,0) for r in L);w=st.mean(terms(r,byq).get(k,0) for r in W)
        rows.append((l,w,k))
    rows.sort()
    print('\nterm (our-their net cash; SELL +, buys -) byq=%s: mean in LOSS | mean in WIN'%byq)
    for l,w,k in rows[:14]:print(f'{str(k):40s} {l:9.0f} {w:9.0f}')
    print('...top positive in loss');[print(f'{str(k):40s} {l:9.0f} {w:9.0f}') for l,w,k in rows[-5:]]
# units: sells per item our vs their
def units(r,op,it,side):
    s=r['our_seat'] if side=='us' else 1-r['our_seat']
    return sum(u for se,q,o,i,u,c in r['groups'] if se==s and o==op and i==it)
print('\nunits SELL (L: us/them | W: us/them)')
for it in ['WHEAT','STRAWBERRY','MELON','CARROT','MILK','WOOL','EGG','FERTILIZER','PUMPKIN','CORN','POTATO','TOMATO']:
    a=[st.mean(units(r,'SELL',it,x) for r in G) for G in (L,W) for x in ('us','them')]
    if sum(a)>0:print(f'{it:12s} L {a[0]:7.1f}/{a[1]:7.1f}  W {a[2]:7.1f}/{a[3]:7.1f}')
