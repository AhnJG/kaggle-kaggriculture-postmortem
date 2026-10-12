#!/usr/bin/env python3
"""Kaggriculture 엔진 사실 검증 스크립트 (FACTS.md의 --cmd 원본).

사용:  pip install -U 'kaggle-environments==1.32.7' && python3 verify_engine_facts.py
이 파일이 출력한 숫자만 FACT로 인정한다. 여기 없는 숫자는 가설이다.
"""
import math
from kaggle_environments.envs.kaggriculture.kaggriculture import (
    MARKET_PARAMS, market_price, MARKET_I0, SHOPS, PRODUCTS, CROPS, ANIMALS,
    _fib, _hire_cost, TOWN_CENTER_PRODUCTS, MAX_SHOP_INSTANCES,
)

LAST_DAY = 29
line = lambda t: print("\n=== " + t + " ===")

line("1) 1회 덤핑 천장: I0에서 $1까지 연속 매도")
print(f"{'item':<11}{'base':>5}{'units_to_$1':>12}{'cum_revenue':>13}")
for it in PRODUCTS:
    inv, rev, n = MARKET_I0, 0, 0
    while n < 2_000_000:
        p = market_price(it, inv)
        if p <= 1:
            break
        rev += p; inv += 1; n += 1
    print(f"{it:<11}{MARKET_PARAMS[it]['base']:>5}{(n if n < 2_000_000 else -1):>12}{rev:>13,}")
print("(-1 = log 곡선이라 $1 바닥이 사실상 없음)")

line("2) 마을 수요 재생률 (상점 8개 전부 해금, 기대값)")
shop_day = {p: 0.0 for p in PRODUCTS}
for name, prods in SHOPS.items():
    mult = 2 if len(prods) == 1 else 1
    for p in prods:                      # 8회 복원추출 => 상점당 기대 인스턴스 1
        shop_day[p] += mult * 6 * 1.0    # 4턴마다 => 하루 6틱
print(f"{'item':<11}{'shops/day':>10}{'center/day':>11}{'total/day':>10}{'@base $/day':>12}")
for p in PRODUCTS:
    c = 1.0 if p in TOWN_CENTER_PRODUCTS else 0.0
    tot = shop_day[p] + c
    print(f"{p:<11}{shop_day[p]:>10.1f}{c:>11.1f}{tot:>10.1f}{tot*MARKET_PARAMS[p]['base']:>12,.0f}")

line("3) 품목별 수요 분산의 원인 (어느 상점이 사가나)")
for p in PRODUCTS:
    holders = [f"{n}{'(2x)' if len(v) == 1 else ''}" for n, v in sorted(SHOPS.items()) if p in v]
    print(f"{p:<11} {len(holders)}/8  {holders}")

line("4) 타일 수익률 (공식 yield/tile/day x base)")
ytd = {"WHEAT": .80, "CARROT": .75, "TOMATO": .33, "STRAWBERRY": .24, "MELON": .55}
for c, v in ytd.items():
    print(f"{c:<11}{v:>6.2f} u/tile/day x {MARKET_PARAMS[c]['base']:>3} = {v*MARKET_PARAMS[c]['base']:>7.1f} coin/tile/day  seed={CROPS[c]['seed']}")
for a, d in ANIMALS.items():
    r, prod = 1.0/d["interval"], d["product"]
    print(f"{a:<11}{r:>6.2f} u/tile/day x {MARKET_PARAMS[prod]['base']:>3} = {r*MARKET_PARAMS[prod]['base']:>7.1f} coin/tile/day  cost={d['cost']} (+비료 1/일)")

line("5) 일꾼 고용 누적비 (하루 k명)")
for k in (4, 8, 10, 13, 15, 18, 20):
    cum = sum(_hire_cost(i) for i in range(k))
    print(f"k={k:<3} cum={cum:>7,}  hand-actions/day={k*24:<5} coin/action={cum/(k*24):.2f}")

line("6) 마지막으로 심어도 되는 날")
for c, d in CROPS.items():
    if d["ongoing"]:
        ages = [d["first_yield_day"] + d["interval"]*i for i in range(d["max_yield"])]
        print(f"{c:<11} ongoing ages {ages} -> 전량 회수하려면 day {LAST_DAY-ages[-1]}까지 파종")
    else:
        print(f"{c:<11} one-time -> 만수확 day {LAST_DAY-d['max_yield_day']}까지 / 1개라도 day {LAST_DAY-d['first_yield_day']}까지")

line("7) 동물 원가 회수 마지노선 (base 가격 기준)")
for a, d in ANIMALS.items():
    base = MARKET_PARAMS[d["product"]]["base"]; need = d["cost"]/base
    for D in range(30):
        first = D + d["first_yield_day"]
        n = 0 if first > LAST_DAY else (LAST_DAY-first)//d["interval"] + 1
        if n < need:
            print(f"{a:<7} cost {d['cost']:>4} / base {base:>4} = {need:.1f}개 필요 -> day {D-1}까지 배치해야 회수")
            break

line("8) 비료를 밭에 쓸 때의 실제 이득")
for c in ("WHEAT", "CARROT", "MELON"):
    d = CROPS[c]; w = (d["max_yield_day"]+1)//2; days = d["max_yield_day"]-w+1
    unf, fer = min(d["max_yield"], 1+days), min(d["max_yield"], 1+2*days)
    print(f"  {c:<7} 물주기창 {days}일, cap {d['max_yield']}: 무비료 {unf} -> 비료 {fer} = +{fer-unf}개 x {MARKET_PARAMS[c]['base']}")
print("  TOMATO/STRAWBERRY: 예정 수확 1회당 1 -> 2 (물+비료 동시일 때만)")
print("  => 비료 판매가가 위 이득보다 높으면 밭에 쓰지 말고 팔아라.")

line("9) 아무도 안 팔면 가격은 오른다 (starter vs random, seed=7)")
from kaggle_environments import make
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 7})
env.run(["starter", "random"])
fin = env.steps[-1]
obs = fin[0].observation
print("최종 은행:", [round(s.reward) for s in fin])
print("마을 상점:", obs["town"]["unlocked_shops"])
print("시즌 총 흡수량(=I0-재고):", {k: 10000-v for k, v in obs["market"]["inventory"].items()})
print("최종 가격:", obs["market"]["prices"])
print("base 가격 :", {k: v["base"] for k, v in MARKET_PARAMS.items()})
