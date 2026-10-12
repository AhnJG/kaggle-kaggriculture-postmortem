#!/usr/bin/env python3
"""병렬 풀 러너: candidate × opponents × seeds × both seats -> jsonl (sellaudit.run 재사용)."""
import argparse, json, glob, os, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def job(args):
    a, b, seed = args
    import sellaudit
    try:
        return sellaudit.run(a, b, seed)
    except Exception as e:
        return {"seed": seed, "agents": [a, b], "error": repr(e)}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", required=True)
    ap.add_argument("--opps", nargs="+", required=True)
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--seat0-only", action="store_true")
    args = ap.parse_args()
    jobs = []
    for o in args.opps:
        for sd in args.seeds:
            jobs.append((args.cand, o, sd))
            if not args.seat0_only: jobs.append((o, args.cand, sd))
    done = 0
    with ProcessPoolExecutor(args.workers) as ex, open(args.out, "a") as f:
        for fut in as_completed([ex.submit(job, j) for j in jobs]):
            r = fut.result(); f.write(json.dumps(r, ensure_ascii=False) + "\n"); f.flush(); done += 1
            if done % 20 == 0: print(done, "/", len(jobs), flush=True)
    print("ALLDONE", len(jobs))
