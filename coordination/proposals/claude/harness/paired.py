#!/usr/bin/env python3
"""parent vs candidate 페어드 비교 (같은 상대·시드·좌석 셀). 셀 결과: W/D/L 은 후보 기준 최종 뱅크 비교."""
import argparse, json, math, collections
from math import comb

def load(path, agent):
    cells = {}
    for l in open(path):
        r = json.loads(l)
        if "error" in r or agent not in r["agents"]:
            continue
        pid = r["agents"].index(agent)
        opp = r["agents"][1 - pid]
        a, b = r["rewards"][pid], r["rewards"][1 - pid]
        cells[(opp, r["seed"], pid)] = (a, b, r)
    return cells

def res(a, b):
    return 1.0 if a > b else (0.5 if a == b else 0.0)

def sign_p(b, c):
    n = b + c
    if n == 0: return 1.0
    return sum(comb(n, k) for k in range(b, n + 1)) / 2 ** n

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent-file"); ap.add_argument("--parent")
    ap.add_argument("--cand-file"); ap.add_argument("--cand")
    a = ap.parse_args()
    P = load(a.parent_file, a.parent); C = load(a.cand_file, a.cand)
    keys = sorted(set(P) & set(C), key=str)
    b = c = 0; ps = cs = 0.0; flips_up = []; flips_down = []; units = collections.defaultdict(lambda: [0.0, 0.0])
    for k in keys:
        pr = res(*P[k][:2]); cr = res(*C[k][:2]); ps += pr; cs += cr
        units[(k[0], k[1])][0] += pr; units[(k[0], k[1])][1] += cr
        if cr > pr: b += 1; flips_up.append((k[0].split('/')[-1][:40], k[1], k[2], P[k][0] - P[k][1], C[k][0] - C[k][1]))
        if cr < pr: c += 1; flips_down.append((k[0].split('/')[-1][:40], k[1], k[2], P[k][0] - P[k][1], C[k][0] - C[k][1]))
    ub = sum(1 for v in units.values() if v[1] > v[0]); uc = sum(1 for v in units.values() if v[1] < v[0])
    n = len(keys)
    print(f"paired cells {n}  parent score {ps/n:.4f}  cand score {cs/n:.4f}")
    print(f"cell discordant b(cand better)={b} c(parent better)={c} sign-p(one-sided b>c)={sign_p(b,c):.4f}")
    print(f"unit(opp,seed) discordant b={ub} c={uc} sign-p={sign_p(ub,uc):.4f}")
    md_p = [P[k][0]-P[k][1] for k in keys]; md_c = [C[k][0]-C[k][1] for k in keys]
    d = [x - y for x, y in zip(md_c, md_p)]
    print(f"mean margin parent {sum(md_p)/n:.0f} cand {sum(md_c)/n:.0f} mean delta {sum(d)/n:.0f} min delta {min(d)} max delta {max(d)}")
    print("UP  :", flips_up)
    print("DOWN:", flips_down)
