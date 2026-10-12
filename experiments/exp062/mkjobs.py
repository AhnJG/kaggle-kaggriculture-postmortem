import json,sys,random
# usage: mkjobs.py out.json cands.json pool.json seed0 nseeds [opp_filter,...]
out,cf,pf,s0,ns=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5])
flt=sys.argv[6].split(',') if len(sys.argv)>6 else None
C=json.load(open(cf));P=json.load(open(pf))
J=[]
for v,vp in C.items():
    for o,op in P.items():
        if flt and o not in flt: continue
        for sd in range(s0,s0+ns):
            for seat in (0,1): J.append([v,vp,o,op,sd,seat])
random.Random(62).shuffle(J)
json.dump(J,open(out,'w'));print(out,len(J))
