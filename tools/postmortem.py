#!/usr/bin/env python3
"""포스트모템 — 한 에피소드 턴별 분기 리포트.

집계 승률(arena.py)은 "졌다"는 사실만 알려준다. 이 도구는 같은 시드로 A vs B 를
**1회** 재생하여 "어디서, 왜" 갈렸는지를 보여준다.

관측 필드 (kaggle-environments==1.32.7, kaggriculture, 2026-09-07 실측으로 확인):
    env.steps[i][p].observation['farms'][k]['money']
        - 플레이어 k(0 또는 1)의 현재 은행 잔고. **절대 인덱스**다 — 관측 주체(p)가
          누구든 farms[0]/farms[1] 은 항상 같은 실제 플레이어를 가리킨다(회전 없음).
        - env.steps[-1][k].reward 와 최종 스텝에서 정확히 일치함을 확인했다.
    env.steps[i][p].action == {'farmer': [OP, *args], 'hands': [[OP,*args], ...],
                                'market': [[OP,*args], ...]}
        - farmer: 그 스텝의 "농부" 유닛 액션 1개. 값이 없으면 빈 리스트(농부 미배치)
          이거나 엔진이 채운 ['PASS'].
        - hands: 고용된 일손(hand) 각각의 액션 리스트. HIRE 전에는 빈 리스트.
        - market: 그 스텝에 낸 시장 주문 리스트 (BUY_SEED/SELL/BUY_LAND/HIRE 등).
        - action 자체와 observation 자체 모두 kaggle_environments.utils.Struct 이며
          dict 서브클래스라 json.dumps 가 바로 먹는다(확인됨).
    env.steps[i][p].observation['day'] / ['hour'] / ['step']
        - step 은 0-base 전역 턴, day 는 0-base(0..29), hour 는 0..23.
          day*24+hour == step 을 실측으로 확인. **주의**: player-1의 관측 struct는
          짝수 글로벌 스텝(자기 차례가 아닌 스텝)에서 'step' 필드가 None으로 비는
          경우가 있었다 — day/hour 판단에 이 필드를 쓰지 말고 파이썬 루프 인덱스
          자체를 step 번호로 써라. money는 player 0 쪽 관측이 항상 채워져 있었으므로
          이를 우선 사용하고, 없으면 player 1 쪽으로 폴백한다.

사용:
    python3 tools/postmortem.py --a main.py --b opponents/public/boatlee.py --seed 1000
    python3 tools/postmortem.py --a main.py --b random --seed 1000 --out out.json --top 3
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter

from kaggle_environments import make

STEPS_PER_DAY = 24
RETURN_TOLERANCE = 0.20  # "20% 이내로 되돌아왔다" 판정 기준


# --------------------------------------------------------------------------
# 방어적 추출 헬퍼 — 절대 raise 하지 않는다. 실패하면 None/빈 값으로 폴백한다.
# --------------------------------------------------------------------------

def _op_of(item):
    """[OP, *args] 또는 'OP' 문자열에서 OP 문자열만 뽑는다."""
    if isinstance(item, (list, tuple)):
        if not item:
            return "?"
        op = item[0]
        return str(op) if op is not None else "?"
    if isinstance(item, str) and item:
        return item
    return "?"


def _fmt_item(item):
    """사람이 읽을 액션 1개 표기. ['PLANT','WHEAT'] -> 'PLANT WHEAT'."""
    if isinstance(item, (list, tuple)):
        if not item:
            return "?"
        return " ".join(str(x) for x in item)
    if item is None:
        return "PASS"
    return str(item)


def _extract_ops(action):
    """한 플레이어·한 스텝의 action dict에서 (farmer+hands+market) OP 문자열 리스트를 뽑는다.
    형태가 이상해도 절대 raise 하지 않는다 — 그냥 빈 리스트를 돌려준다."""
    ops = []
    if not isinstance(action, dict):
        return ops
    try:
        farmer = action.get("farmer")
    except Exception:
        farmer = None
    if isinstance(farmer, (list, tuple)) and farmer:
        ops.append(_op_of(farmer))
    elif isinstance(farmer, str) and farmer:
        ops.append(farmer)
    try:
        hands = action.get("hands") or []
    except Exception:
        hands = []
    if isinstance(hands, (list, tuple)):
        for h in hands:
            ops.append(_op_of(h))
    try:
        market = action.get("market") or []
    except Exception:
        market = []
    if isinstance(market, (list, tuple)):
        for m in market:
            ops.append(_op_of(m))
    return ops


def _farmer_present(action):
    """농부 액션 슬롯이 아예 비어있는지(=진짜 no-op turn) 판정."""
    if not isinstance(action, dict):
        return False
    try:
        f = action.get("farmer")
    except Exception:
        return False
    return bool(f)


def _fmt_action(action):
    if not isinstance(action, dict):
        return "?(malformed)"
    try:
        farmer = action.get("farmer")
        farmer_s = _fmt_item(farmer) if farmer else "PASS"
        hands = action.get("hands") or []
        hands_s = ",".join(_fmt_item(h) for h in hands) if hands else "-"
        market = action.get("market") or []
        market_s = ",".join(_fmt_item(m) for m in market) if market else "-"
        return f"farmer=[{farmer_s}] hands=[{hands_s}] market=[{market_s}]"
    except Exception:
        return "?(malformed)"


def _money(observation, idx):
    try:
        farms = observation["farms"]
        v = farms[idx]["money"]
        return float(v) if v is not None else None
    except Exception:
        return None


# --------------------------------------------------------------------------
# 리플레이 + 추출
# --------------------------------------------------------------------------

def replay(a, b, seed, episode_steps=720):
    env = make("kaggriculture", configuration={"episodeSteps": episode_steps, "seed": seed})
    env.run([a, b])
    return env.steps


def extract(steps):
    """env.steps 를 훑어서 스텝별 (bank, action) 및 전체 집계를 뽑는다.
    개별 스텝이 깨져 있어도 절대 죽지 않고 스킵 + 카운트만 한다."""
    n = len(steps)
    per_step_money = [None] * n          # (money_a, money_b) or None
    per_step_actions = [None] * n        # (action_a, action_b) as dict-or-None
    op_counts = [Counter(), Counter()]
    no_action_turns = [0, 0]
    status_anomalies = [0, 0]
    malformed_steps = 0

    for i in range(n):
        try:
            step = steps[i]
            p0, p1 = step[0], step[1]
        except Exception:
            malformed_steps += 1
            continue

        obs0 = getattr(p0, "observation", None)
        obs1 = getattr(p1, "observation", None)
        m0 = _money(obs0, 0) if obs0 is not None else None
        m1 = _money(obs0, 1) if obs0 is not None else None
        if m0 is None:
            m0 = _money(obs1, 0) if obs1 is not None else None
        if m1 is None:
            m1 = _money(obs1, 1) if obs1 is not None else None
        per_step_money[i] = (m0, m1)

        act_a = getattr(p0, "action", None)
        act_b = getattr(p1, "action", None)
        per_step_actions[i] = (act_a, act_b)

        for pi, act in enumerate((act_a, act_b)):
            try:
                for op in _extract_ops(act):
                    op_counts[pi][op] += 1
                if not _farmer_present(act):
                    no_action_turns[pi] += 1
            except Exception:
                malformed_steps += 1

        for pi, p in enumerate((p0, p1)):
            st = getattr(p, "status", None)
            if st not in ("DONE", "ACTIVE"):
                status_anomalies[pi] += 1

    return {
        "per_step_money": per_step_money,
        "per_step_actions": per_step_actions,
        "op_counts": op_counts,
        "no_action_turns": no_action_turns,
        "status_anomalies": status_anomalies,
        "malformed_steps": malformed_steps,
    }


# --------------------------------------------------------------------------
# 일별 격차 곡선 / 분기일 / 최악의 날
# --------------------------------------------------------------------------

def build_day_curve(per_step_money, n_steps):
    """게임-데이 1회(=24스텝 마지막 스텝, hour23)마다 한 번씩 샘플링."""
    n_days = n_steps // STEPS_PER_DAY
    rows = []
    prev_gap = 0.0  # 시작은 양쪽 동일 자본이므로 gap=0 이 자연스러운 기준선
    for d in range(n_days):
        idx = STEPS_PER_DAY * (d + 1) - 1
        if idx >= len(per_step_money) or per_step_money[idx] is None:
            rows.append({"day": d, "step": idx, "bank_a": None, "bank_b": None,
                         "gap": None, "delta": None})
            continue
        m0, m1 = per_step_money[idx]
        if m0 is None or m1 is None:
            rows.append({"day": d, "step": idx, "bank_a": m0, "bank_b": m1,
                         "gap": None, "delta": None})
            continue
        gap = m0 - m1
        delta = gap - prev_gap
        rows.append({"day": d, "step": idx, "bank_a": m0, "bank_b": m1,
                      "gap": gap, "delta": delta})
        prev_gap = gap
    return rows


def _within_tolerance(v, target, tol=RETURN_TOLERANCE):
    if target == 0:
        return v == 0
    return abs(v - target) <= tol * abs(target)


def find_divergence_day(day_curve):
    """되돌아오지 않게 된 첫 날 = '돌아올 수 없는 지점'.

    day d 이후(>d) 어떤 날의 gap도 gap[d] 의 20% 이내로 다시는 돌아오지 않는
    **가장 이른** d 를 찾는다. (마지막 날은 미래가 없으므로 공허하게 항상 참이라
    최소한 그 날은 항상 후보가 된다 — 즉 결과가 None 이 되는 경우는 없다.)
    """
    valid = [(r["day"], r["gap"]) for r in day_curve if r["gap"] is not None]
    for i, (d, g) in enumerate(valid):
        future = [gg for _, gg in valid[i + 1:]]
        if all(not _within_tolerance(gg, g) for gg in future):
            return {"day": d, "gap": g}
    return None


def find_worst_days(day_curve, top_n):
    """delta 오름차순(A 기준 gap이 가장 많이 나빠진 날) 상위 N개."""
    valid = [r for r in day_curve if r["delta"] is not None]
    ranked = sorted(valid, key=lambda r: r["delta"])
    return ranked[:max(0, top_n)]


# --------------------------------------------------------------------------
# 리포트 조립 / 출력
# --------------------------------------------------------------------------

def build_report(a, b, seed, steps, top_n=5):
    ex = extract(steps)
    n_steps = len(steps)

    final = steps[-1] if steps else None
    reward_a = reward_b = None
    if final is not None:
        try:
            reward_a = final[0].reward
            reward_b = final[1].reward
        except Exception:
            pass
    if reward_a is None or reward_b is None:
        # 폴백: 마지막 유효 스텝의 money
        for m in reversed(ex["per_step_money"]):
            if m is not None and m[0] is not None and m[1] is not None:
                reward_a, reward_b = m
                break
    reward_a = reward_a if reward_a is not None else float("nan")
    reward_b = reward_b if reward_b is not None else float("nan")
    if reward_a > reward_b:
        winner = "A"
    elif reward_b > reward_a:
        winner = "B"
    else:
        winner = "DRAW"

    day_curve = build_day_curve(ex["per_step_money"], n_steps)
    divergence = find_divergence_day(day_curve)
    worst_days = find_worst_days(day_curve, top_n)

    # 최악의 날 각각에 24스텝 전체 액션 로그를 붙인다 (요청된 유일한 verbose 섹션)
    worst_days_detail = []
    for r in worst_days:
        d = r["day"]
        lo, hi = STEPS_PER_DAY * d, STEPS_PER_DAY * d + STEPS_PER_DAY
        rows = []
        for s in range(lo, min(hi, n_steps)):
            act = ex["per_step_actions"][s]
            if act is None:
                rows.append({"step": s, "hour": s - lo, "a": "?(malformed)", "b": "?(malformed)"})
                continue
            act_a, act_b = act
            rows.append({"step": s, "hour": s - lo,
                         "a": _fmt_action(act_a), "b": _fmt_action(act_b)})
        worst_days_detail.append({**r, "actions": rows})

    op_a, op_b = ex["op_counts"]
    all_ops = sorted(set(op_a) | set(op_b), key=lambda k: -(op_a.get(k, 0) + op_b.get(k, 0)))

    return {
        "a": a, "b": b, "seed": seed, "steps": n_steps,
        "malformed_steps": ex["malformed_steps"],
        "status_anomalies": {"a": ex["status_anomalies"][0], "b": ex["status_anomalies"][1]},
        "final": {"bank_a": reward_a, "bank_b": reward_b, "winner": winner},
        "day_curve": day_curve,
        "divergence_day": divergence,
        "worst_days": worst_days_detail,
        "op_counts": {"a": dict(op_a), "b": dict(op_b)},
        "op_order": all_ops,
        "pass_counts": {"a": op_a.get("PASS", 0), "b": op_b.get("PASS", 0)},
        "no_action_turns": {"a": ex["no_action_turns"][0], "b": ex["no_action_turns"][1]},
    }


def print_report(rep, top_n):
    a, b, seed = rep["a"], rep["b"], rep["seed"]
    print(f"A={a}  vs  B={b}   seed={seed}   steps={rep['steps']}")
    if rep["malformed_steps"]:
        print(f"  경고: 깨진 스텝 {rep['malformed_steps']}개 스킵함")
    sa, sb = rep["status_anomalies"]["a"], rep["status_anomalies"]["b"]
    if sa or sb:
        print(f"  경고: 이상 status(ERROR 등) A={sa} B={sb}")

    f = rep["final"]
    print(f"\n최종 은행잔고  A={f['bank_a']:,.0f}  B={f['bank_b']:,.0f}  "
          f"승자={f['winner']}  (마진 {f['bank_a']-f['bank_b']:+,.0f})")

    print("\n[일별 은행잔고 격차 곡선] (day: A잔고 / B잔고 / gap=A-B / 전일 대비 변화)")
    print(f"{'day':>4} {'A':>12} {'B':>12} {'gap':>12} {'Δgap':>12}")
    for r in rep["day_curve"]:
        if r["gap"] is None:
            print(f"{r['day']:>4} {'?':>12} {'?':>12} {'?':>12} {'?':>12}")
            continue
        print(f"{r['day']:>4} {r['bank_a']:>12,.0f} {r['bank_b']:>12,.0f} "
              f"{r['gap']:>12,.0f} {r['delta']:>+12,.0f}")

    dv = rep["divergence_day"]
    print("\n[분기일 / 돌아올 수 없는 지점]")
    if dv is None:
        print("  판정 불가 (유효한 일별 데이터 없음)")
    else:
        print(f"  day {dv['day']}  (그날 gap={dv['gap']:+,.0f}) 이후로는 gap이 "
              f"그 값의 {int(RETURN_TOLERANCE*100)}% 이내로 다시 돌아오지 못했다.")

    print(f"\n[격차 악화 TOP {top_n}일] (A 기준, 그날 gap이 가장 많이 나빠진 순)")
    if not rep["worst_days"]:
        print("  (해당 없음)")
    for wd in rep["worst_days"]:
        print(f"\n  --- day {wd['day']}  gap={wd['gap']:+,.0f}  "
              f"Δgap(그날)={wd['delta']:+,.0f} ---")
        for row in wd["actions"]:
            print(f"    h{row['hour']:>2} (step {row['step']:>3})  "
                  f"A: {row['a']:<55} B: {row['b']}")

    print("\n[액션 타입 빈도] (farmer+hands+market 전체 합산)")
    print(f"{'op':<20} {'A':>8} {'B':>8}")
    oa, ob = rep["op_counts"]["a"], rep["op_counts"]["b"]
    for op in rep["op_order"]:
        print(f"{op:<20} {oa.get(op, 0):>8} {ob.get(op, 0):>8}")

    pc = rep["pass_counts"]
    na = rep["no_action_turns"]
    print(f"\nPASS 횟수            A={pc['a']:>6}  B={pc['b']:>6}")
    print(f"빈 액션(농부無) 턴수   A={na['a']:>6}  B={na['b']:>6}")


def main():
    ap = argparse.ArgumentParser(description="포스트모템 — 1경기 턴별 분기 리포트")
    ap.add_argument("--a", required=True, help="평가 대상 (경로 또는 builtin)")
    ap.add_argument("--b", required=True, help="상대 (경로 또는 builtin)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--steps", type=int, default=720, help="episodeSteps (기본 720 = 30일)")
    ap.add_argument("--out", help="JSON 저장 경로")
    ap.add_argument("--top", type=int, default=5, help="최악의 날 상위 N개 (기본 5)")
    args = ap.parse_args()

    t0 = time.perf_counter()
    try:
        steps = replay(args.a, args.b, args.seed, args.steps)
    except Exception as e:
        print(f"리플레이 실패: {e}", file=sys.stderr)
        sys.exit(1)
    wall = time.perf_counter() - t0

    rep = build_report(args.a, args.b, args.seed, steps, top_n=args.top)
    print_report(rep, args.top)
    print(f"\n소요 {wall:.1f}s")

    if args.out:
        with open(args.out, "w") as f:
            json.dump(rep, f, ensure_ascii=False, indent=2, default=str)
        print(f"저장: {args.out}")


if __name__ == "__main__":
    main()
