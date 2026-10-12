#!/usr/bin/env python3
"""무음 실패 계측기 — Kaggriculture.

이 게임에서 손실의 대부분은 예외를 내지 않는다:
  1. 불법/무효 유닛 액션   -> 조용한 no-op (턴 낭비)
  2. 셰드 100칸 초과       -> 물건이 조용히 소멸
  3. 시장 주문 11번째부터  -> 조용히 절삭
  4. SELL 요청량 > 재고    -> 진단용 미체결 수량 (phantom sentinel 포함)
  5. HIRE 자금 부족        -> 조용히 무시
  6. 작물별 씨앗 부족      -> 그 작물의 PLANT 요청 전부 PASS 치환

"예외 0"만 확인하고 넘어가면 위 여섯 종류가 전혀 보이지 않는다.

일반 release gate는 실제 손실(no-op, shed discard/unsold, order truncation,
BUY/HIRE/PLANT failure, exception)이 절대 0인지 본다. `sell_unfilled`는 요청량에서
체결량을 뺀 diagnostic일 뿐 gate를 실패시키지 않는다. EXP별 gate는 해당 card의
사전등록 기준만 적용하며, 일반 release gate가 이를 덮어쓰지 않는다. 예를 들어
EXP-008 G4는 다섯 counter의 cell별 candidate <= parent non-regression이다.

사용:
    python3 tools/instrument.py --a main.py --b starter --seeds 7 11 13
    python3 tools/instrument.py --a main.py --b starter --seeds 7 \
      --time-agent a --gate-agent a
    python3 tools/instrument.py --a main.py --b tape:path.json --seeds 7 \
      --focus-steps 23 25 47 --include-actions --json result.json
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path

try:
    from gate_contract import document, exit_code
except ModuleNotFoundError:  # package import (e.g. unit tests)
    from tools.gate_contract import document, exit_code

# 타일/인벤토리를 바꿔야 정상인 op. 이동·PASS 는 제외한다.
_TILE_OPS = {
    "PLANT", "WATER", "HARVEST", "FERTILIZE", "DIG", "BUILD_COOP", "BUILD_PASTURE",
    "FEED", "COLLECT_FERTILIZER", "CARE", "PICKUP", "PLACE", "DROP",
}
_MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
MAX_ORDERS = 10
EXPECTED_ENGINE_SHA = "bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e"
METRIC_SCHEMA_VERSION = 3


@dataclass
class Counters:
    noop_actions: int = 0
    noop_by_op: dict = field(default_factory=dict)
    blocked_moves: int = 0
    shed_discarded: int = 0
    shed_discarded_inday_drop: int = 0
    shed_discarded_inday_place: int = 0
    drop_events: list = field(default_factory=list)
    shed_unsold: int = 0
    orders_truncated: int = 0
    sell_requested: int = 0
    sell_filled: int = 0
    sell_revenue: float = 0.0
    sell_by_item: dict = field(default_factory=dict)
    buy_failed: int = 0
    hire_failed: int = 0
    seed_blocked_plant: int = 0
    seed_blocked_by_crop: dict = field(default_factory=dict)
    hands_length_mismatch_count: int = 0
    exceptions: int = 0
    market_issue_turns: int = 0
    sell_issue_turns: int = 0
    market_saturated_turns: int = 0
    sell_units_issued: int = 0
    sell_order_lines: int = 0
    pre_market_rows: int = 0
    post_market_rows: int = 0
    self_clamped_rows: int = 0
    self_clamped_by_op: dict = field(default_factory=dict)
    safety_valve_activations: int = 0
    deferred_sell_lines: int = 0
    daily_max_shed: list = field(default_factory=lambda: [0] * 30)

    @property
    def sell_unfilled(self) -> int:
        return max(0, self.sell_requested - self.sell_filled)

    def gate_reasons(self) -> list[str]:
        values = {
            "noop_actions": self.noop_actions,
            "shed_discarded": self.shed_discarded,
            "shed_unsold": self.shed_unsold,
            "orders_truncated": self.orders_truncated,
            "buy_failed": self.buy_failed,
            "hire_failed": self.hire_failed,
            "seed_blocked_plant": self.seed_blocked_plant,
            "hands_length_mismatch_count": self.hands_length_mismatch_count,
            "exceptions": self.exceptions,
        }
        return [f"{name}={value}" for name, value in values.items() if value]

    def gate_diagnostics(self) -> list[str]:
        """Return non-gating observations that remain useful for diagnosis."""
        return [f"sell_unfilled={self.sell_unfilled}"] if self.sell_unfilled else []

    def is_clean(self) -> bool:
        return (self.noop_actions == 0 and self.shed_discarded == 0
                and self.shed_unsold == 0 and self.orders_truncated == 0
                and self.buy_failed == 0 and self.hire_failed == 0
                and self.seed_blocked_plant == 0
                and self.hands_length_mismatch_count == 0
                and self.exceptions == 0)

    def as_dict(self) -> dict:
        realized = {}
        for item, row in sorted(self.sell_by_item.items()):
            units = int(row.get("units", 0))
            revenue = float(row.get("revenue", 0.0))
            realized[item] = {"units": units, "revenue": round(revenue, 3),
                              "avg_price": round(revenue / units, 3) if units else None}
        d = {"metric_schema_version": METRIC_SCHEMA_VERSION,
             "noop_actions": self.noop_actions, "blocked_moves": self.blocked_moves,
             "shed_discarded": self.shed_discarded, "shed_unsold": self.shed_unsold,
             "shed_discarded_inday_drop": self.shed_discarded_inday_drop,
             "shed_discarded_inday_place": self.shed_discarded_inday_place,
             "drop_events": self.drop_events,
             "drop_event_summary": drop_event_summary(self.drop_events),
             "orders_truncated": self.orders_truncated,
             "sell_requested": self.sell_requested, "sell_filled": self.sell_filled,
             "sell_unfilled": self.sell_unfilled, "buy_failed": self.buy_failed,
             "hire_failed": self.hire_failed,
             "seed_blocked_plant": self.seed_blocked_plant,
             "seed_blocked_by_crop": dict(sorted(self.seed_blocked_by_crop.items())),
             "hands_length_mismatch_count": self.hands_length_mismatch_count,
             "exceptions": self.exceptions, "realized_sell": realized,
             "market_issue_turns": self.market_issue_turns,
             "sell_issue_turns": self.sell_issue_turns,
             "market_saturated_turns": self.market_saturated_turns,
             "sell_units_issued": self.sell_units_issued,
             "sell_order_lines": self.sell_order_lines,
             "avg_sell_units_per_turn": (round(self.sell_units_issued / self.sell_issue_turns, 3)
                                         if self.sell_issue_turns else None),
             "pre_market_rows": self.pre_market_rows,
             "post_market_rows": self.post_market_rows,
             "self_clamped_rows": self.self_clamped_rows,
             "self_clamped_by_op": dict(sorted(self.self_clamped_by_op.items())),
             "safety_valve_activations": self.safety_valve_activations,
             "deferred_sell_lines": self.deferred_sell_lines,
             "daily_max_shed": list(self.daily_max_shed),
             "max_shed": max(self.daily_max_shed, default=0),
             "gate_passed": self.is_clean(),
             "gate_reasons": self.gate_reasons(),
             "gate_diagnostics": self.gate_diagnostics()}
        if self.noop_by_op:
            d["noop_by_op"] = dict(sorted(self.noop_by_op.items(), key=lambda kv: -kv[1]))
        return d


@dataclass
class Report:
    seed: int
    agents: list
    rewards: list
    statuses: list
    steps: int
    wall_seconds: float
    players: list
    daily_min_cash: list
    agent_ms_by_player: list = field(default_factory=list)
    combined_agent_cpu_seconds: float | None = None
    focus_steps: list = field(default_factory=list)
    action_streams: list = field(default_factory=list)

    def summary(self) -> str:
        out = [f"seed={self.seed} {self.agents} rewards={self.rewards} "
               f"status={self.statuses} steps={self.steps} wall={self.wall_seconds:.1f}s"]
        for pid, m in enumerate(self.agent_ms_by_player):
            if m:
                out.append(f"  P{pid} agent ms  first={m['first_call_ms']:.2f} "
                           f"p50={m['p50']:.2f} p95={m['p95']:.2f} "
                           f"p99={m['p99']:.2f} max={m['max']:.2f}  (한도 1000ms)")
        for i, c in enumerate(self.players):
            flag = "CLEAN" if c.is_clean() else "DIRTY"
            min_cash = min(self.daily_min_cash[i]) if self.daily_min_cash[i] else None
            out.append(f"  P{i} [{flag}] noop={c.noop_actions} blocked_move={c.blocked_moves} "
                       f"discard={c.shed_discarded} shed_unsold={c.shed_unsold} "
                       f"trunc={c.orders_truncated} "
                       f"sell_unfilled={c.sell_unfilled} buy_failed={c.buy_failed} "
                       f"hire_failed={c.hire_failed} seed_blocked={c.seed_blocked_plant} "
                       f"hands_mismatch={c.hands_length_mismatch_count} "
                       f"min_cash={min_cash} exc={c.exceptions}")
            out.append(f"       market_turns={c.market_issue_turns} sell_turns={c.sell_issue_turns} "
                       f"sat10={c.market_saturated_turns} avg_sell_units="
                       f"{(c.sell_units_issued / c.sell_issue_turns) if c.sell_issue_turns else 0:.2f} "
                       f"self_clamped={c.self_clamped_rows} safety={c.safety_valve_activations} "
                       f"max_shed={max(c.daily_max_shed, default=0)}")
            if c.noop_by_op:
                top = ", ".join(f"{k}:{v}" for k, v in
                                sorted(c.noop_by_op.items(), key=lambda kv: -kv[1])[:6])
                out.append(f"       noop 상위: {top}")
            if c.sell_by_item:
                prices = ", ".join(
                    f"{item}:{row['revenue'] / row['units']:.2f}({row['units']})"
                    for item, row in sorted(c.sell_by_item.items()) if row["units"] > 0)
                if prices:
                    out.append(f"       실현 SELL 평균가격(수량): {prices}")
        return "\n".join(out)

    def as_dict(self) -> dict:
        result = {"seed": self.seed, "agents": self.agents, "rewards": self.rewards,
                "statuses": self.statuses, "steps": self.steps,
                "wall_seconds": round(self.wall_seconds, 3),
                "agent_ms": next((m for m in self.agent_ms_by_player if m), None),
                "agent_ms_by_player": self.agent_ms_by_player,
                "combined_agent_cpu_seconds": self.combined_agent_cpu_seconds,
                "daily_min_cash": self.daily_min_cash,
                "players": [c.as_dict() for c in self.players]}
        if self.focus_steps:
            result["focus_steps"] = self.focus_steps
        if self.action_streams:
            result["action_streams"] = self.action_streams
        return result


def seed_blocked_plants(action, seeds) -> dict:
    """Return crop -> PLANT requests that the engine will atomically replace with PASS."""
    if not isinstance(action, dict):
        return {}
    farmer = action.get("farmer", ["PASS"])
    hands = action.get("hands", [])
    unit_actions = [farmer, *(hands if isinstance(hands, list) else [])]
    demand = {}
    for unit_action in unit_actions:
        if (isinstance(unit_action, list) and len(unit_action) >= 2
                and unit_action[0] == "PLANT"):
            crop = unit_action[1]
            demand[crop] = demand.get(crop, 0) + 1
    available = seeds if hasattr(seeds, "get") else {}
    return {crop: count for crop, count in demand.items()
            if count > int(available.get(crop, 0) or 0)}


def local_step_snapshot(steps, index: int) -> dict:
    """Read the observation stored at env.steps[index], matching hosted step_snapshot."""
    states = steps[index]
    observation = states[0].observation
    farms = observation["farms"]
    players = []
    for seat, farm in enumerate(farms):
        tiles = farm.get("tiles") or []
        players.append({
            "seat": seat,
            "bank": farm.get("money"),
            "hands": len(farm.get("hands") or []),
            "nonempty_tiles": sum(isinstance(tile, dict) for row in tiles for tile in row),
            "action": states[seat].action,
        })
    return {
        "step": index,
        "day": index // 24,
        "hour": index % 24,
        "players": players,
    }


def action_difference(left_stream: list, right_stream: list) -> dict:
    """Compare actions by recorded environment step."""
    left = {int(row["step"]): row.get("action") for row in left_stream}
    right = {int(row["step"]): row.get("action") for row in right_stream}
    steps = sorted(set(left) | set(right))
    different = [step for step in steps if left.get(step) != right.get(step)]
    unit_different = [
        step for step in steps
        if ((left.get(step) or {}).get("farmer"), (left.get(step) or {}).get("hands"))
        != ((right.get(step) or {}).get("farmer"), (right.get(step) or {}).get("hands"))
    ]
    market_different = [
        step for step in steps
        if (left.get(step) or {}).get("market") != (right.get(step) or {}).get("market")
    ]
    return {
        "different_steps": different,
        "farmer_or_hands_different_steps": unit_different,
        "market_different_steps": market_different,
    }


def action_stream_sha256(stream: list) -> str:
    payload = json.dumps(stream, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _tile_sig(farm, x, y):
    return json.dumps(farm["tiles"][y][x], sort_keys=True, default=str)


def _inv_total(private, idx):
    invs = private.get("inventories") or []
    if idx >= len(invs):
        return None
    return sum(int(v or 0) for v in invs[idx].values())


def drop_event_summary(events):
    counts = {}
    for event in events:
        for loss in event["losses"]:
            label = loss["class"]
            counts[label] = counts.get(label, 0) + loss["quantity"]
    return {"events": len(events), "discarded_total": sum(counts.values()),
            "class_counts": dict(sorted(counts.items()))}


def attribute_drop(private, capacity, *, player, day, step, positions, last_ops,
                   board_size, full_turns, sell_lines, sell_filled):
    """Replay only the engine's allocation arithmetic on a detached snapshot."""
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    shed = copy.deepcopy(private["shed"])
    carried = copy.deepcopy(private["inventories"])
    initial = sum(shed.values())
    deposited, discarded, by_unit, losses = {}, {}, [], []
    for idx, inv in enumerate(carried):
        lost_unit = 0
        for item, n in inv.items():
            if n <= 0:
                continue
            take = min(n, max(0, capacity - sum(shed.values())))
            if take:
                shed[item] = shed.get(item, 0) + take
                deposited[item] = deposited.get(item, 0) + take
            lost = n - take
            if lost:
                discarded[item] = discarded.get(item, 0) + lost
                lost_unit += lost
                adjacent = K._is_shed_adjacent(tuple(positions[idx]), board_size)
                label = "|".join(("ROOM_ZERO" if initial >= capacity else "ROOM_PARTIAL",
                                  "ADJACENT" if adjacent else "REMOTE",
                                  "DEPOSIT_ATTEMPTED" if last_ops[idx] in ("DROP", "PLACE")
                                  else "NO_DEPOSIT_ATTEMPT"))
                losses.append(dict(player=player, day=day, step=step, unit_index=idx,
                                   item=item, quantity=lost, shed_total_before=initial,
                                   unit_last_op=last_ops[idx], unit_shed_adjacent_at_drop=adjacent,
                                   **{"class": label}))
        by_unit.append(lost_unit)
    return dict(player=player, day=day, step=step, shed_capacity=capacity,
                shed_total_before=initial, shed_before=copy.deepcopy(private["shed"]),
                carried_before=carried, unit_last_op=list(last_ops),
                unit_pos_at_drop=copy.deepcopy(positions),
                unit_shed_adjacent_at_drop=[K._is_shed_adjacent(tuple(pos), board_size) for pos in positions],
                deposited=deposited, discarded=discarded, discarded_total=sum(by_unit),
                discarded_by_unit=by_unit, losses=losses, shed_full_turns_today=full_turns,
                market_sell_lines_last_turn=copy.deepcopy(sell_lines), sell_filled_last_turn=sell_filled)


class _Instrumentation:
    """엔진 모듈 함수를 감싼다. make() 호출 전에 install() 해야 한다."""

    def __init__(self):
        from kaggle_environments.envs.kaggriculture import kaggriculture as K
        self.K = K
        self.counters = [Counters(), Counters()]
        self.farm_pid = {}
        self.private_pid = {}
        self._orig = {}

    def _pid_of_farm(self, farm):
        return self.farm_pid.get(id(farm), 0)

    def install(self):
        """엔진의 모듈 전역 함수를 감싼다.

        주의: `K.interpreter` 를 재할당해도 소용없다. kaggle-environments 레지스트리가
        모듈 로드 시점의 함수 객체를 이미 잡고 있기 때문이다. 대신 그 interpreter 가
        매 스텝 모듈 전역 이름으로 호출하는 `_initialize` / `_process_market` 을 감싼다.
        """
        K = self.K
        self._orig = {"init": K._initialize,
                      "eod": K._end_of_day,
                      "market": K._process_market,
                      "unit": K._apply_unit_action,
                      "drop": K._drop_inventories_to_shed,
                      "commit": K._commit_unit,
                      "hire": K._do_hire}
        counters, farm_pid, private_pid = self.counters, self.farm_pid, self.private_pid
        orig = self._orig
        # ---- 호출 순서 기반 귀속 ----
        # id(farm) 로는 안 된다. kaggle-environments 는 매 스텝 관측 객체를 새로 만들고
        # id 가 재활용되기까지 한다. 게다가 인터프리터는 _apply_unit_action 을 전부 먼저
        # 돌린 뒤에야 _process_market 을 부르므로, market 단계에서 등록한 id 는 다음 스텝
        # 유닛 단계에서 이미 낡았다 -> 상대 카운터가 우리 버킷으로 샌다.
        # 인터프리터가 `for i, s in enumerate(state)` 로 플레이어 순서대로 돌고 각 플레이어마다
        # unit_index 0(농부) 부터 시작한다는 사실을 이용한다.
        cursor = {"unit": -1, "drop": -1}
        drop_context = {}
        last_ops = [{}, {}]
        full_turns = [{}, {}]
        last_sells = [[], []]
        last_fills = [0, 0]

        def _register(state):
            """farm / private 객체 id 를 플레이어 인덱스에 매핑한다."""
            try:
                farms = state[0].observation["farms"]
            except Exception:
                farms = getattr(state[0].observation, "farms", None)
            if farms:
                for i, f in enumerate(farms):
                    farm_pid[id(f)] = i
            for pid, s in enumerate(state):
                try:
                    pv = s.observation["private"]
                except Exception:
                    pv = getattr(s.observation, "private", None)
                if pv is not None:
                    private_pid[id(pv)] = pid

        def initialize(state, env):
            r = orig["init"](state, env)
            _register(state)
            return r

        def process_market(state, env):
            _register(state)          # 시장 단계에서는 같은 스텝의 객체이므로 id 가 유효하다
            cursor["unit"] = -1       # 유닛 단계 종료 -> 다음 스텝을 위해 리셋
            for pid, s in enumerate(state):
                act = s.action if isinstance(s.action, dict) else {}
                m = act.get("market") if isinstance(act, dict) else None
                if isinstance(m, list):
                    if m:
                        counters[pid].market_issue_turns += 1
                    if len(m) >= MAX_ORDERS:
                        counters[pid].market_saturated_turns += 1
                    if len(m) > MAX_ORDERS:
                        counters[pid].orders_truncated += len(m) - MAX_ORDERS
                    sells = [o for o in m[:MAX_ORDERS]
                             if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL"]
                    if sells:
                        counters[pid].sell_issue_turns += 1
                        counters[pid].sell_order_lines += len(sells)
                        for o in sells:
                            try:
                                counters[pid].sell_units_issued += max(0, int(o[2]))
                            except (TypeError, ValueError):
                                pass
                    for o in m[:MAX_ORDERS]:
                        if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                            try:
                                counters[pid].sell_requested += max(0, int(o[2]))
                            except (TypeError, ValueError):
                                pass
                    pre = act.get("__exp003_pre_market")
                    if isinstance(pre, list):
                        c = counters[pid]
                        c.pre_market_rows += len(pre)
                        c.post_market_rows += len(m)
                        cut = pre[len(m):] if pre[:len(m)] == m else []
                        c.self_clamped_rows += len(cut)
                        for o in cut:
                            op = o[0] if isinstance(o, list) and o else "MALFORMED"
                            c.self_clamped_by_op[op] = c.self_clamped_by_op.get(op, 0) + 1
                    if act.get("__exp003_safety_valve"):
                        counters[pid].safety_valve_activations += 1
                    try:
                        counters[pid].deferred_sell_lines += max(
                            0, int(act.get("__exp003_deferred_sell_lines", 0) or 0))
                    except (TypeError, ValueError):
                        pass
                try:
                    obs = state[pid].observation
                    day = int(obs["day"])
                    private = obs["private"]
                    occupancy = sum(int(v or 0) for v in (private["shed"] or {}).values())
                    if 0 <= day < len(counters[pid].daily_max_shed):
                        counters[pid].daily_max_shed[day] = max(
                            counters[pid].daily_max_shed[day], occupancy)
                except Exception:
                    pass
            before_fills = [c.sell_filled for c in counters]
            r = orig["market"](state, env)
            for pid, player_state in enumerate(state):
                obs = player_state.observation
                day = int(obs["day"])
                cap = int(K.get(env.configuration, "shedCapacity", 100))
                if sum(obs["private"]["shed"].values()) >= cap:
                    full_turns[pid][day] = full_turns[pid].get(day, 0) + 1
                action = player_state.action or {}
                last_sells[pid] = [copy.deepcopy(o) for o in action.get("market", [])[:MAX_ORDERS]
                                   if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL"]
                last_fills[pid] = counters[pid].sell_filled - before_fills[pid]
            return r

        def unit(farm, private, unit_index, action, board_size, day, turns_per_day, shed_capacity=100):
            if unit_index == 0:                       # 새 플레이어의 농부 -> 커서 전진
                cursor["unit"] += 1
            pid = min(max(0, cursor["unit"]), len(counters) - 1)
            c = counters[pid]
            if unit_index == 0:
                last_ops[pid] = {}
            op = action[0] if isinstance(action, (list, tuple)) and action else "PASS"
            pos = farm["farmer"] if unit_index == 0 else (
                farm["hands"][unit_index - 1] if unit_index - 1 < len(farm["hands"]) else None)
            before_pos = list(pos) if pos is not None else None
            if before_pos is not None:
                last_ops[pid][unit_index] = op
            transfer_before = None
            if before_pos is not None and op in ("DROP", "PLACE"):
                transfer_before = (_inv_total(private, unit_index), sum(private["shed"].values()),
                                   _tile_sig(farm, *before_pos))
            before_tile = before_inv = None
            if before_pos is not None and op in _TILE_OPS:
                before_tile = _tile_sig(farm, before_pos[0], before_pos[1])
                before_inv = _inv_total(private, unit_index)
            r = orig["unit"](farm, private, unit_index, action, board_size, day,
                             turns_per_day, shed_capacity)
            if transfer_before is not None:
                inv_before, shed_before, tile_before = transfer_before
                # PLACE of an animal changes the tile: it is not a discarded item.
                if _tile_sig(farm, *before_pos) == tile_before:
                    lost = max(0, inv_before - _inv_total(private, unit_index)
                               - (sum(private["shed"].values()) - shed_before))
                    if op == "DROP":
                        c.shed_discarded_inday_drop += lost
                    else:
                        c.shed_discarded_inday_place += lost
            if before_pos is not None:
                after_pos = farm["farmer"] if unit_index == 0 else (
                    farm["hands"][unit_index - 1] if unit_index - 1 < len(farm["hands"]) else None)
                if op in _MOVES:
                    if after_pos is not None and list(after_pos) == before_pos:
                        c.blocked_moves += 1
                elif op in _TILE_OPS:
                    if (_tile_sig(farm, before_pos[0], before_pos[1]) == before_tile
                            and _inv_total(private, unit_index) == before_inv):
                        c.noop_actions += 1
                        c.noop_by_op[op] = c.noop_by_op.get(op, 0) + 1
            return r

        def drop(private, capacity):
            cursor["drop"] += 1                        # _end_of_day 가 플레이어 순서대로 1회씩 부른다
            pid = min(max(0, cursor["drop"]), len(counters) - 1)
            carried = sum(sum(int(v or 0) for v in inv.values())
                          for inv in (private.get("inventories") or []))
            shed_before = sum(int(v or 0) for v in private["shed"].values())
            farm = drop_context["farms"][pid]
            positions = [farm["farmer"], *farm["hands"]]
            day = drop_context["day"]
            event = attribute_drop(private, capacity, player=pid, day=day,
                                   step=drop_context["step"], positions=positions,
                                   last_ops=[last_ops[pid].get(i, "NOT_CALLED") for i in range(len(positions))],
                                   board_size=drop_context["board_size"],
                                   full_turns=full_turns[pid].get(day, 0),
                                   sell_lines=last_sells[pid], sell_filled=last_fills[pid])
            r = orig["drop"](private, capacity)
            counters[pid].drop_events.append(event)
            moved = sum(int(v or 0) for v in private["shed"].values()) - shed_before
            lost = max(0, carried - moved)
            if lost:
                counters[pid].shed_discarded += lost
            return r

        def commit(op, item, price, farm, private, market, shed_capacity=100):
            ok = orig["commit"](op, item, price, farm, private, market, shed_capacity)
            c = counters[farm_pid.get(id(farm), private_pid.get(id(private), 0))]
            if op == "SELL":
                if ok:
                    c.sell_filled += 1
                    c.sell_revenue += float(price)
                    row = c.sell_by_item.setdefault(item, {"units": 0, "revenue": 0.0})
                    row["units"] += 1
                    row["revenue"] += float(price)
            elif not ok:
                c.buy_failed += 1
            return ok

        def hire(farm, private, board_size, mult=1):
            before = len(farm["hands"])
            result = orig["hire"](farm, private, board_size, mult)
            if len(farm["hands"]) == before:
                pid = farm_pid.get(id(farm), private_pid.get(id(private), 0))
                counters[pid].hire_failed += 1
            return result

        def end_of_day(state, env, day):
            cursor["drop"] = -1
            turns = max(1, int(K.get(env.configuration, "turnsPerDay", 24)))
            drop_context.update(farms=state[0].observation["farms"], day=day,
                                step=(day + 1) * turns - 1,
                                board_size=int(K.get(env.configuration, "boardSize", 10)))
            return orig["eod"](state, env, day)

        K._initialize = initialize
        K._end_of_day = end_of_day
        K._process_market = process_market
        K._apply_unit_action = unit
        K._drop_inventories_to_shed = drop
        K._commit_unit = commit
        K._do_hire = hire

    def uninstall(self):
        K = self.K
        K._initialize = self._orig["init"]
        K._end_of_day = self._orig["eod"]
        K._process_market = self._orig["market"]
        K._apply_unit_action = self._orig["unit"]
        K._drop_inventories_to_shed = self._orig["drop"]
        K._commit_unit = self._orig["commit"]
        K._do_hire = self._orig["hire"]


def load_agent(path):
    """파이썬 파일에서 진입점을 엔진과 같은 규칙으로 불러온다.

    Kaggle 로더와 ``env.run("main.py")`` 는 파일을 빈 dict 전역에서 exec 한 뒤 **전역의 마지막 callable**
    을 진입점으로 쓴다 (``kaggle_environments/agent.py`` 의 ``get_last_callable``).
    예전에는 모듈 속성 ``agent`` 를 골랐기 때문에, 마지막 callable 이 ``agent`` 가 아닌 파일
    (P2 계열 ``_e336_agent``, EXP-014/015 변형)에서는 제출물과 다른 함수를 측정했다.
    """
    from kaggle_environments.agent import get_last_callable
    from kaggle_environments.utils import read_file

    return get_last_callable(read_file(path), path=str(path))


def _timed(fn, bucket):
    def wrapper(obs, config=None):
        t = time.perf_counter()
        try:
            return fn(obs, config) if fn.__code__.co_argcount >= 2 else fn(obs)
        finally:
            bucket.append((time.perf_counter() - t) * 1000.0)
    return wrapper


def _audited(fn, counter, action_stream):
    def wrapper(obs, config=None):
        code = getattr(fn, "__code__", None)
        action = fn(obs, config) if code is not None and code.co_argcount >= 2 else fn(obs)
        try:
            player = int(obs["player"])
            expected_hands = len(obs["farms"][player].get("hands") or [])
            action_hands = action.get("hands") if isinstance(action, dict) else None
            if not isinstance(action_hands, list) or len(action_hands) != expected_hands:
                counter.hands_length_mismatch_count += 1
            private = obs["private"]
            blocked = seed_blocked_plants(action, private.get("seeds", {}))
            for crop, count in blocked.items():
                counter.seed_blocked_plant += count
                counter.seed_blocked_by_crop[crop] = counter.seed_blocked_by_crop.get(crop, 0) + count
            step = int(obs["step"]) + 1
            action_stream.append({"step": step, "action": copy.deepcopy(action)})
        except Exception:
            counter.exceptions += 1
        return action
    return wrapper


def _tape_agent(path):
    entries = json.loads(Path(path).read_text(encoding="utf-8"))
    bad_turns = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            bad_turns.append((index, None))
        elif entry.get("turn") != index or "action" not in entry:
            bad_turns.append((index, entry.get("turn")))
    if bad_turns:
        index, turn = bad_turns[0]
        raise ValueError(f"tape turn sequence invalid at index {index}: turn={turn!r}")
    actions = [entry["action"] for entry in entries]

    def agent(obs, config=None):
        index = int(obs["step"]) + 1
        if index < len(actions):
            return copy.deepcopy(actions[index])
        return {"farmer": ["PASS"], "hands": [], "market": []}
    return agent


def _resolve_agent(spec):
    if not isinstance(spec, str):
        return spec
    if spec.startswith("tape:"):
        return _tape_agent(spec[5:])
    if Path(spec).is_file() and spec.endswith(".py"):
        return load_agent(spec)
    return spec


def _timing_summary(bucket):
    if not bucket:
        return None
    ordered = sorted(bucket)
    q = lambda p: ordered[min(len(ordered) - 1, int(len(ordered) * p))]
    return {"n": len(bucket), "first_call_ms": bucket[0],
            "p50": q(.50), "p95": q(.95), "p99": q(.99), "max": ordered[-1],
            "total_s": sum(bucket) / 1000.0}


def instrumented_run(agents, seed=7, episode_steps=720, time_agent_index=None,
                     time_agent_indices=None, focus_steps=(), capture_actions=False):
    inst = _Instrumentation()
    inst.install()
    try:
        from kaggle_environments import make
        if time_agent_indices is None:
            timed_indices = (() if time_agent_index is None else (time_agent_index,))
        else:
            timed_indices = tuple(time_agent_indices)
        buckets = [[] for _ in agents]
        action_streams = [[], []]
        run_agents = []
        for pid, spec in enumerate(agents):
            fn = _resolve_agent(spec)
            if not isinstance(fn, str):
                if pid in timed_indices:
                    fn = _timed(fn, buckets[pid])
                fn = _audited(fn, inst.counters[pid], action_streams[pid])
            run_agents.append(fn)
        env = make("kaggriculture",
                   configuration={"episodeSteps": episode_steps, "seed": seed})
        t0 = time.perf_counter()
        env.run(run_agents)
        wall = time.perf_counter() - t0
    finally:
        inst.uninstall()

    final = env.steps[-1]
    for pid, s in enumerate(final):
        if s.status not in ("DONE", "ACTIVE"):
            inst.counters[pid].exceptions += 1
        try:
            shed = s.observation["private"]["shed"] or {}
            inst.counters[pid].shed_unsold = sum(
                max(0, int(shed.get(item, 0) or 0)) for item in inst.K.PRODUCTS)
        except Exception:
            inst.counters[pid].exceptions += 1

    agent_ms_by_player = [_timing_summary(bucket) for bucket in buckets]
    combined_agent_cpu_seconds = None
    if set(timed_indices) == set(range(len(agents))) and all(agent_ms_by_player):
        combined_agent_cpu_seconds = sum(m["total_s"] for m in agent_ms_by_player)

    daily = [[None] * 30 for _ in final]
    for step_i, states in enumerate(env.steps):
        try:
            farms = states[0].observation["farms"]
        except Exception:
            continue
        day = min(29, step_i // 24)
        for pid in range(min(len(final), len(farms))):
            money = round(float(farms[pid]["money"]), 3)
            current = daily[pid][day]
            daily[pid][day] = money if current is None else min(current, money)
    daily = [[v for v in row if v is not None] for row in daily]
    snapshots = [local_step_snapshot(env.steps, index) for index in focus_steps]

    return Report(seed=seed,
                  agents=[a if isinstance(a, str) else getattr(a, "__name__", "fn") for a in agents],
                  rewards=[round(s.reward or 0) for s in final],
                  statuses=[s.status for s in final],
                  steps=len(env.steps), wall_seconds=wall,
                  players=inst.counters, daily_min_cash=daily,
                  agent_ms_by_player=agent_ms_by_player,
                  combined_agent_cpu_seconds=combined_agent_cpu_seconds,
                  focus_steps=snapshots,
                  action_streams=action_streams if capture_actions else [])


def main():
    ap = argparse.ArgumentParser(description="Kaggriculture 무음 실패 계측기")
    ap.add_argument("--a", default="starter")
    ap.add_argument("--b", default="random")
    ap.add_argument("--seeds", type=int, nargs="+", default=[7])
    ap.add_argument("--steps", type=int, default=720)
    ap.add_argument("--time-agent", choices=["a", "b", "both"],
                    help="선택한 에이전트의 턴당 실행시간을 측정한다 (파이썬 파일이어야 함)")
    ap.add_argument("--gate-agent", choices=["a", "b", "both"], default="both",
                    help="합격 판정에 넣을 제출 에이전트; 양쪽 counter는 항상 기록한다")
    ap.add_argument("--json")
    ap.add_argument("--focus-steps", type=int, nargs="*", default=[],
                    help="env.steps[index] observation의 bank/hands/nonempty_tiles를 저장")
    ap.add_argument("--include-actions", action="store_true",
                    help="action stream을 JSON 결과에 포함")
    ap.add_argument("--require-pass", action="store_true",
                    help="gate failure를 non-zero exit와 versioned JSON으로 강제")
    args = ap.parse_args()

    timed_indices = {"a": (0,), "b": (1,), "both": (0, 1)}.get(args.time_agent, ())
    gated_indices = {"a": (0,), "b": (1,), "both": (0, 1)}[args.gate_agent]
    reports, gate, run_errors = [], True, []
    artifact_before = {}
    for label, path in (("a", args.a), ("b", args.b)):
        p = Path(path)
        artifact_before[label] = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    for sd in args.seeds:
        try:
            rep = instrumented_run([args.a, args.b], seed=sd,
                                   episode_steps=args.steps,
                                   time_agent_indices=timed_indices,
                                   focus_steps=args.focus_steps,
                                   capture_actions=args.include_actions)
        except Exception as exc:
            run_errors.append(f"seed {sd}: {exc!r}")
            continue
        print(rep.summary())
        statuses_ok = rep.steps == 720 and all(s == "DONE" for s in rep.statuses)
        gate = gate and statuses_ok and all(rep.players[i].is_clean()
                                             for i in gated_indices)
        reports.append(rep.as_dict())

    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    engine_sha = hashlib.sha256(Path(K.__file__).read_bytes()).hexdigest()
    artifact_sha = {}
    for label, path in (("a", args.a), ("b", args.b)):
        p = Path(path)
        artifact_sha[label] = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    if engine_sha != EXPECTED_ENGINE_SHA:
        verdict, reasons = "ENGINE_MISMATCH", ["engine SHA-256 does not match ENGINE_LOCK"]
    elif artifact_sha != artifact_before:
        verdict, reasons = "IDENTITY_MISMATCH", ["artifact SHA-256 changed during execution"]
    elif run_errors or len(reports) != len(args.seeds) or args.steps != 720:
        verdict, reasons = "INVALID", ["one or more runs did not complete 720 steps with DONE"]
        reasons.extend(run_errors)
    elif not gate:
        verdict, reasons = "FAILURE", ["silent-failure or exception counters are non-zero"]
    else:
        verdict, reasons = "PASS", []
    print(f"\n게이트(P0 기준, 무음 실패 counter + 예외 = 0): "
          f"{'PASS' if verdict == 'PASS' else 'FAIL'}")
    if args.json:
        result = document(verdict=verdict, gate_passed=verdict == "PASS",
                          reasons=reasons, engine_sha256=engine_sha,
                          artifact_sha256=artifact_sha, payload=reports,
                          extra={"metric_schema_version": METRIC_SCHEMA_VERSION,
                                 "gated_player_indices": list(gated_indices),
                                 "gate_verdict_by_player": {
                                     str(report["seed"]): [
                                         bool(c.get("gate_passed"))
                                         for c in report.get("players", [])
                                     ]
                                     for report in reports
                                 },
                                 "player_gate_reasons": {
                                     str(report["seed"]): [
                                         c.get("gate_reasons", [])
                                         for c in report.get("players", [])
                                     ]
                                     for report in reports
                                 },
                                 "player_gate_diagnostics": {
                                     str(report["seed"]): [
                                         c.get("gate_diagnostics", [])
                                         for c in report.get("players", [])
                                     ]
                                     for report in reports
                                 }})
        with open(args.json, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"저장: {args.json}")
    if args.require_pass:
        sys.exit(exit_code(verdict))


if __name__ == "__main__":
    main()
