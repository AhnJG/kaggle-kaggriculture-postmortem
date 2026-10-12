import json, sys, time, instr
a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
instr.WEEDLOG.clear(); t0=time.time()
r = instr.run([a, b], seed)
print(json.dumps(dict(rewards=r['rewards'], statuses=r['statuses'], shops6=r['shops'].get(6), weedlog=instr.WEEDLOG[:12], secs=round(time.time()-t0,1))))
