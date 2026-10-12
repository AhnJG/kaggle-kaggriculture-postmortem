#!/usr/bin/env python3
"""SELL 미체결 분해 계측기 (engine 1.32.7). 엔진 동작은 바꾸지 않고 관측만 한다.

미체결 units = Σ SELL n − 체결 units 를 다음으로 분해한다 (턴·플레이어·품목 단위):
  shed_unsold : 창고에 재고가 있었는데 안 팔린 units (엔진이 주문을 중도 abort 한 경우)
  carried     : 창고엔 없고 일꾼 인벤토리에 있던 units (DROP 안 된 재고)
  phantom     : 어디에도 재고가 없던 units (n=1000 같은 sentinel 과다요청)
  engine_trunc: 11번째 이후 주문 줄 수 (엔진 절삭)
  agent_trunc : 에이전트가 자기 [:10] 로 자른 SELL 줄 수 (yhay81 모듈 후킹)
실손 지표:
  discard_units/value : 일말 셰드 초과로 소멸
  end_units/value     : 종료 시점 셰드+인벤토리 잔여 (최종가 기준 상한)
  floor_units         : 가격 1 로 판 units (시장 공급 미증가, 사실상 0 가치)
"""
import argparse, collections, copy, importlib.util, json, sys, time
from kaggle_environments.envs.kaggriculture import kaggriculture as K
from kaggle_environments import make

C = collections.Counter

def load_module(path, tag):
    spec = importlib.util.spec_from_file_location(f"_m_{tag}", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

_TAPES = {}
def tape_agent(path):
    if path not in _TAPES:
        _TAPES[path] = [e["action"] for e in json.load(open(path))]
    acts = _TAPES[path]
    def agent(obs, config=None):
        i = int(obs["step"]) + 1
        return copy.deepcopy(acts[i]) if i < len(acts) else {"farmer": ["PASS"], "hands": [], "market": []}
    return agent

def hook_yhay(mod, bucket):
    orig = mod.advance_sales
    def adv(action, view, state, tape, step):
        r = orig(action, view, state, tape, step)
        m = action.get("market") or []
        if len(m) > mod.MAX_ORDERS:
            cut = m[mod.MAX_ORDERS:]
            bucket["agent_trunc_lines"] += len(cut)
            bucket["agent_trunc_sell_lines"] += sum(1 for o in cut if o and o[0] == "SELL")
        return r
    mod.advance_sales = adv

def _timed(fn, bucket):
    n = fn.__code__.co_argcount
    def wrapper(obs, config=None):
        t = time.perf_counter()
        try:
            return fn(obs, config) if n >= 2 else fn(obs)
        finally:
            bucket.append((time.perf_counter() - t) * 1000.0)
    return wrapper

def run(a_spec, b_spec, seed):
    stats = [C(), C()]
    per_item = [collections.defaultdict(C), collections.defaultdict(C)]
    agents = []
    mods = [None, None]
    times = [[], []]
    for pid, spec in enumerate((a_spec, b_spec)):
        if spec.startswith("tape:"):
            agents.append(tape_agent(spec[5:]))
        elif spec.endswith(".py"):
            mod = load_module(spec, f"{pid}_{seed}")
            if hasattr(mod, "advance_sales") and hasattr(mod, "SHOP_PLANS"):
                hook_yhay(mod, stats[pid])
            mods[pid] = mod
            agents.append(_timed(mod.agent, times[pid]))
        else:
            agents.append(spec)
    o_market, o_eod, o_drop = K._process_market, K._end_of_day, K._drop_inventories_to_shed
    o_commit = K._commit_unit
    o_unit = K._apply_unit_action
    cur = {"drop": -1, "market": None, "unit": -1}

    def unit(farm, private, idx, action, *a, **kw):
        if idx == 0:
            cur["unit"] += 1
        pid = min(max(0, cur["unit"]), 1)
        if isinstance(action, list) and action and action[0] == "DROP":
            inv = private["inventories"][idx] if idx < len(private["inventories"]) else {}
            before = sum(max(0, int(v)) for v in inv.values()) + sum(int(v) for v in private["shed"].values())
            prices = cur["market"]["prices"] if cur["market"] else {}
            snap = {k: int(v) for k, v in inv.items() if v > 0}
            shed_b = {k: int(v) for k, v in private["shed"].items()}
            r = o_unit(farm, private, idx, action, *a, **kw)
            inv2 = private["inventories"][idx] if idx < len(private["inventories"]) else {}
            after = sum(max(0, int(v)) for v in inv2.values()) + sum(int(v) for v in private["shed"].values())
            lost = before - after
            if lost > 0:
                stats[pid]["manual_drop_lost_units"] += lost
                for k, n in snap.items():
                    moved = int(private["shed"].get(k, 0)) - shed_b.get(k, 0)
                    stats[pid]["manual_drop_lost_value"] += max(0, n - moved - int(inv2.get(k, 0))) * prices.get(k, 0)
            return r
        return o_unit(farm, private, idx, action, *a, **kw)

    def process_market(state, env):
        max_orders = max(1, int(K.get(env.configuration, "maxMarketOrdersPerTurn", 10)))
        cur["market"] = state[0].observation.market
        cur["unit"] = -1
        snaps, pidmap = [], {}
        for pid, s in enumerate(state):
            act = s.action if isinstance(s.action, dict) else {}
            m = act.get("market", []) if isinstance(act, dict) else []
            q = list(m) if isinstance(m, list) else []
            st = stats[pid]
            st["engine_trunc_lines"] += max(0, len(q) - max_orders)
            try:
                fh = len(state[0].observation.farms[pid]["hands"])
                ah = len(act.get("hands") or []) if isinstance(act, dict) else 0
                if ah > fh: st["hands_extra_turns"] += 1
                elif ah < fh: st["hands_missing_turns"] += 1
            except Exception:
                st["hands_check_error"] += 1
            q = q[:max_orders]
            priv = s.observation.private
            pidmap[id(priv)] = pid
            shed = C({k: int(v) for k, v in priv["shed"].items()})
            carried = C()
            for inv in priv["inventories"]:
                for k, v in inv.items(): carried[k] += int(v)
            req = C()
            for o in q:
                po = K._parse_order(o)
                if po and po["type"] == "SELL":
                    st["sell_lines"] += 1
                    if po["remaining"] >= 100: st["sentinel_lines"] += 1
                    if po["item"] in K.PRODUCTS: req[po["item"]] += po["remaining"]
                    else: st["sell_invalid_item_lines"] += 1
            snaps.append((shed, carried, req))
        filled = [C(), C()]
        floor_item = cur.setdefault("floor_item", [C(), C()])
        def commit(op, item, price, farm, private, market, shed_capacity=100):
            ok = o_commit(op, item, price, farm, private, market, shed_capacity)
            pid = pidmap.get(id(private))
            if pid is None: return ok
            if op == "SELL" and ok:
                filled[pid][item] += 1
                stats[pid]["revenue"] += price
                if price <= 1:
                    stats[pid]["floor_units"] += 1
                    floor_item[pid][item] += 1
            elif op != "SELL" and not ok:
                stats[pid]["buy_failed"] += 1
            return ok
        K._commit_unit = commit
        try:
            r = o_market(state, env)
        finally:
            K._commit_unit = o_commit
        for pid, (shed, carried, req) in enumerate(snaps):
            st = stats[pid]
            for item, n in req.items():
                f = filled[pid][item]
                unf = max(0, n - f)
                shed_unsold = max(0, min(unf, shed[item] - f))
                rem = unf - shed_unsold
                car = min(rem, carried[item])
                ph = rem - car
                st["req_units"] += n; st["filled_units"] += f; st["unfilled_units"] += unf
                st["shed_unsold_units"] += shed_unsold; st["carried_units"] += car; st["phantom_units"] += ph
                pi = per_item[pid][item]
                pi["req"] += n; pi["filled"] += f; pi["phantom"] += ph; pi["carried"] += car; pi["shed_unsold"] += shed_unsold
        return r

    def end_of_day(state, env, day):
        cur["drop"] = -1
        return o_eod(state, env, day)

    def drop(private, capacity):
        cur["drop"] += 1
        pid = min(max(0, cur["drop"]), 1)
        carried = C()
        for inv in private["inventories"]:
            for k, v in inv.items():
                if v > 0: carried[k] += int(v)
        before = C({k: int(v) for k, v in private["shed"].items()})
        r = o_drop(private, capacity)
        after = C({k: int(v) for k, v in private["shed"].items()})
        mk = cur["market"]
        for k, n in carried.items():
            lost = n - max(0, after[k] - before[k])
            if lost > 0:
                stats[pid]["discard_units"] += lost
                if mk: stats[pid]["discard_value"] += mk["prices"].get(k, 0) * lost
        return r

    K._process_market, K._end_of_day, K._drop_inventories_to_shed = process_market, end_of_day, drop
    K._apply_unit_action = unit
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        t0 = time.perf_counter(); env.run(agents); wall = time.perf_counter() - t0
    finally:
        K._process_market, K._end_of_day, K._drop_inventories_to_shed = o_market, o_eod, o_drop
        K._apply_unit_action = o_unit
    final = env.steps[-1]
    prices = final[0].observation.market["prices"]
    for pid, s in enumerate(final):
        priv = s.observation.private
        left = C({k: int(v) for k, v in priv["shed"].items() if v > 0})
        for inv in priv["inventories"]:
            for k, v in inv.items():
                if v > 0: left[k] += int(v)
        stats[pid]["end_units"] = sum(n for k, n in left.items() if k in K.PRODUCTS)
        stats[pid]["end_animals"] = sum(n for k, n in left.items() if k in K.ANIMALS)
        stats[pid]["end_value"] = sum(prices.get(k, 0) * n for k, n in left.items() if k in K.PRODUCTS)
        stats[pid]["end_items"] = dict(left)
        if mods[pid] is not None and isinstance(getattr(mods[pid], "GUARD_COUNTS", None), dict):
            stats[pid]["guard_counts"] = dict(mods[pid].GUARD_COUNTS)
        if mods[pid] is not None and isinstance(getattr(mods[pid], "PREEMPT_COUNTS", None), dict):
            stats[pid]["preempt_counts"] = dict(mods[pid].PREEMPT_COUNTS)
        if times[pid]:
            b = sorted(times[pid])
            stats[pid]["agent_calls"] = len(b)
            stats[pid]["agent_cpu_s"] = round(sum(b) / 1000.0, 4)
            stats[pid]["turn_p99_ms"] = round(b[min(len(b) - 1, int(len(b) * 0.99))], 4)
            stats[pid]["turn_max_ms"] = round(b[-1], 3)
    return {"seed": seed, "agents": [a_spec, b_spec],
            "rewards": [round(s.reward or 0) for s in final],
            "status": [s.status for s in final], "wall": round(wall, 2), "engine_steps": len(env.steps),
            "players": [dict(st) for st in stats],
            "per_item": [{k: dict(v) for k, v in pi.items()} for pi in per_item],
            "floor_item": [dict(x) for x in cur.get("floor_item", [C(), C()])]}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True); ap.add_argument("--b", required=True)
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--both-seats", action="store_true")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    with open(args.out, "a") as f:
        for sd in args.seeds:
            pairs = [(args.a, args.b)] + ([(args.b, args.a)] if args.both_seats else [])
            for a, b in pairs:
                rec = run(a, b, sd)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
                print(sd, [x.split('/')[-1] for x in rec["agents"]], rec["rewards"], rec["wall"], flush=True)
