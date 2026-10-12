# -*- coding: utf-8 -*-
"""Kaggriculture v1 — NW·NE·SW 3구획 작물 에이전트.

목적은 성능이 아니라 **무음 실패 0**이다. 이 게임의 손실은 대부분 예외를 내지 않는다:
    (a) 불법/무효 유닛 액션      -> 조용한 no-op (턴 낭비)
    (b) 씨앗보다 많은 PLANT       -> 그 턴 해당 작물 PLANT 전부 무효화 (engine: interpreter._allowed)
    (c) 시장 주문 11번째 이후     -> 조용히 절삭
    (d) SELL 재고 부족            -> 조용히 미체결
    (e) 셰드 100칸 초과           -> 물건이 조용히 소멸
    (f) 마지막 턴에 남은 재고     -> 점수는 은행 현금뿐이므로 전액 손실

설계 원칙
    * 상태를 들고 다니지 않는다(stateless). 매 턴 obs 만으로 전 계획을 재구성한다.
      - Kaggle 로더는 `__file__` 을 정의하지 않고, self-play 시 같은 모듈이 두 플레이어에게
        공유될 수 있다. 모듈 전역 가변 상태를 쓰면 그때 오염된다.
    * copy.deepcopy 금지(vCPU 1.6). 필요한 곳에서 작은 dict 얕은 복사만 한다.
    * 최외곽에서 절대 raise 하지 않는다.
    * 하드 제약은 "계획 단계"와 "가드 단계" 두 곳에서 이중으로 강제한다.
      계획이 옳으면 가드는 절대 발화하지 않아야 한다(가드 발화 = 계획 버그).

v1 정책
    * NE와 SW를 정해진 날에 순서대로 사서 75칸에서 밀/당근을 회전한다. SE는 사지 않는다.
    * 일꾼은 목표 수까지 하루 초반 여러 market turn에 나눠 고용한다.
    * land timing / 일꾼 수 / 당근 칸 수는 local wrapper가 한 요인씩 덮어쓸 수 있는 상수다.
"""

# ---------------------------------------------------------------------------
# 게임 상수 (engine: kaggriculture.py 에서 확인)
# ---------------------------------------------------------------------------
EPISODE_STEPS = 720
TURNS_PER_DAY = 24
BOARD_SIZE = 10
SHED_CAP = 100
MAX_MARKET_ORDERS = 10          # 하드 제약 2: 이 값으로 단 한 곳에서만 클램프한다
LAST_DAY = EPISODE_STEPS // TURNS_PER_DAY - 1                 # 29
# interpreter: `if step >= cfg.episodeSteps - 2: status=DONE`.
# 즉 액션이 실제로 반영되는 마지막 스텝은 718 (= day 29, hour 22).
LAST_STEP = EPISODE_STEPS - 2                                 # 718

CROPS = {
    "WHEAT":      {"seed": 10, "first_yield_day": 2, "max_yield_day": 4},
    "CARROT":     {"seed": 20, "first_yield_day": 2, "max_yield_day": 3},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10},
    "MELON":      {"seed": 80, "first_yield_day": 10, "max_yield_day": 12},
}
# 시장에서 팔 수 있는 품목(engine PRODUCTS). GOOSE/COW/SHEEP 은 셰드에 있어도
# SELL 대상이 아니다 -> 넣으면 sell_unfilled 가 된다.
SELLABLE = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
            "EGG", "MILK", "WOOL", "FERTILIZER")

MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
# 셰드 인접 4칸 (engine `_shed_access_tiles(10)`), (x, y). 3칸은 LOCKED 이지만
# 셰드 액션(PICKUP/DROP/PLACE)은 LOCKED 가드보다 먼저 해석되므로 사용 가능하다.
# 이 중 (4,4) 만 NW(=해금)이며, engine `_default_spawn` 에 따라 매일 아침
# 파머와 일꾼 전원이 (4,4) 로 리스폰된다. 하루 계획은 항상 여기서 시작한다.
SHED_TILES = ((4, 4), (5, 4), (4, 5), (5, 5))
LAND_PURCHASE_DAYS = (6, 10)   # NE, SW. SE는 정책상 절대 사지 않는다.
LAND_PURCHASE_HOURS = (0, 0)   # 주문 시각. 실제 unlock 관측은 다음 step(h1)이다.
LAND_QUADRANTS = ("NE", "SW")
LAND_COSTS = (1000, 2000)
N_HANDS = 9                     # EXP-001 stage 2 선택값
CARROT_TILES = 15               # pilot baseline; 나머지는 WHEAT
MELON_TILES = 0                 # EXP-002 wrapper가 한 축씩 덮어쓴다.
STRAWBERRY_TILES = 0
CROP_SWITCH_DAY = 30            # v1 parent에서는 season 밖이라 premium crop 비활성
HIRE_FIB = (1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610)

PASS = ["PASS"]
FALLBACK_HANDS = 0              # 폴백에서 hands 길이를 못 읽었을 때의 기본값


def _tile_order():
    """NW·NE·SW를 각 shed 인접 칸에서 바깥으로 뱀 모양으로 나열한다.

    연속한 두 칸이 항상 인접하므로, 이 리스트를 통째로 잘라 유닛에게 나눠주면
    같은 구획 안의 담당 구역이 공간적으로 이어진다. 구획 순서는 BUY_LAND 순서와 같다.
    """
    order = []
    # NW: (4,4)에서 북서쪽으로.
    for row, y in enumerate(range(4, -1, -1)):          # y = 4,3,2,1,0
        xs = range(4, -1, -1) if row % 2 == 0 else range(0, 5)
        for x in xs:
            order.append((x, y))
    # NE: (5,4)에서 북동쪽으로.
    for row, y in enumerate(range(4, -1, -1)):
        xs = range(5, 10) if row % 2 == 0 else range(9, 4, -1)
        for x in xs:
            order.append((x, y))
    # SW: (4,5)에서 남서쪽으로.
    for row, y in enumerate(range(5, 10)):
        xs = range(4, -1, -1) if row % 2 == 0 else range(0, 5)
        for x in xs:
            order.append((x, y))
    return tuple(order)


TILE_ORDER = _tile_order()      # 75칸; SE 25칸은 포함하지 않는다
N_TILES = len(TILE_ORDER)


def _base_crop_of(i):
    """v1의 CARROT/WHEAT 배치를 반환한다.

    밀은 과잉공급에 대한 가격 탄력이 매우 낮고(above_func=log, target 0.20),
    당근은 매우 높다(sqrt, 0.70). 그래서 밀 위주로 두고 당근은 소량만 돌린다.
    두 작물을 같이 쓰는 이유는 '작물별 씨앗 예산'(하드 제약 1)을 실제로 태우기 위해서다.
    """
    # Bucket boundary를 고르면 gcd(N_TILES, CARROT_TILES)와 무관하게 정확한 수가 나온다.
    # offset 2는 CARROT_TILES=15일 때 v0의 NW 배치(every fifth tile)를 보존한다.
    j = (i - 2) % N_TILES
    if CARROT_TILES > 0 and (j == 0 or
                             (j * CARROT_TILES) // N_TILES
                             != ((j - 1) * CARROT_TILES) // N_TILES):
        return "CARROT"
    return "WHEAT"


# 29와 75는 서로소다. 따라서 정확히 한 번씩 모든 칸을 방문하면서 premium crop을
# 밭 전체에 흩어 놓는다. MELON 구간 뒤에 STRAWBERRY를 배치해 stage C가 MELON 수를
# 바꾸지 않도록 한다.
_PREMIUM_ORDER = tuple((2 + 29 * k) % N_TILES for k in range(N_TILES))
_PREMIUM_RANK = {tile_i: rank for rank, tile_i in enumerate(_PREMIUM_ORDER)}


def _crop_of(i, day):
    """전환 전에는 v1, 전환 뒤에는 MELON/STRAWBERRY/WHEAT 구성을 반환한다."""
    if day < CROP_SWITCH_DAY:
        return _base_crop_of(i)
    rank = _PREMIUM_RANK[i]
    if rank < MELON_TILES:
        return "MELON"
    if rank < MELON_TILES + STRAWBERRY_TILES:
        return "STRAWBERRY"
    return "WHEAT"


def _phase_of(i):
    """첫 파종일을 4일에 걸쳐 분산시키는 위상.

    전 칸을 day 0 에 동시에 심으면 수확일이 겹쳐 한 유닛이 하루에
    5칸 x 4액션 = 20액션 + 이동을 감당해야 하고, 24턴 예산을 넘겨 수확을 놓친다.
    (놓치면 max_lifespan_step 이후 2스텝마다 yield 가 1씩 깎여 금방 잡초가 된다.)
    밀 주기는 4일이라 초기 위상차가 시즌 내내 유지된다.
    """
    return i % 4


def _chunks(n_units, active_indices=None):
    """현재 unlocked 칸만 유닛 수만큼 연속 슬라이스로 분할한다."""
    n_units = max(1, n_units)
    active = list(range(N_TILES)) if active_indices is None else list(active_indices)
    base, extra = divmod(len(active), n_units)
    out, start = [], 0
    for u in range(n_units):
        size = base + (1 if u < extra else 0)
        out.append(tuple(active[start:start + size]))
        start += size
    return out


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _step_toward(pos, target):
    """target 쪽으로 한 칸. 보드 밖으로 나가는 수는 절대 만들지 않는다.

    출발/도착이 모두 보드 안이면 거리를 줄이는 축 이동은 항상 보드 안이므로
    이 함수는 blocked_moves 를 구조적으로 0으로 만든다.
    """
    x, y = pos[0], pos[1]
    dx, dy = target[0] - x, target[1] - y
    cands = []
    if abs(dx) >= abs(dy):
        if dx:
            cands.append(("EAST" if dx > 0 else "WEST", x + (1 if dx > 0 else -1), y))
        if dy:
            cands.append(("SOUTH" if dy > 0 else "NORTH", x, y + (1 if dy > 0 else -1)))
    else:
        if dy:
            cands.append(("SOUTH" if dy > 0 else "NORTH", x, y + (1 if dy > 0 else -1)))
        if dx:
            cands.append(("EAST" if dx > 0 else "WEST", x + (1 if dx > 0 else -1), y))
    for op, nx, ny in cands:
        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            return [op]
    return None


# ---------------------------------------------------------------------------
# 타일 판정 — 전부 engine `_apply_unit_action` 의 조건을 그대로 옮긴 것이다.
# 여기서 True 인 액션만 발행하므로 noop_actions 가 0 이 된다.
# ---------------------------------------------------------------------------
def _is_plant(tile):
    return isinstance(tile, dict) and tile.get("kind") == "PLANT"


def _is_weed(tile):
    return isinstance(tile, dict) and tile.get("kind") == "WEED"


def _in_bonus_window(tile, day):
    """일회성 작물은 (max_yield_day+1)//2 ~ max_yield_day 사이에 물을 줄 때마다 +1 수확."""
    cd = CROPS.get(tile.get("crop"))
    if cd is None:
        return False
    age = day - tile.get("planted_day", day)
    return ((cd["max_yield_day"] + 1) // 2) <= age <= cd["max_yield_day"]


def _harvest_ready(tile, day):
    """engine HARVEST 조건 + '지금 걷는 게 이득인가' 판정."""
    cd = CROPS.get(tile.get("crop"))
    if cd is None:
        return False
    if tile.get("yield_units", 0) <= 0:              # engine: yield_units>0 필수
        return False
    age = day - tile.get("planted_day", day)
    if age < cd["first_yield_day"]:                  # engine: 미성숙이면 무효
        return False
    if age >= cd["max_yield_day"]:                   # 더 자라지 않는다 -> 지금 걷는다
        return True
    return day >= LAST_DAY                           # 마지막 날은 남은 것 전부 회수


def _can_plant_day(i, crop, day):
    """위상 분산 + '수확까지 살아남을 수 있는가' 컷오프."""
    if day < _phase_of(i):
        return False
    return day + CROPS[crop]["first_yield_day"] <= LAST_DAY


def _tile_job(tile, i, day, seed_budget, pending):
    """이 칸에서 지금 발행 가능한 '실제 효과가 있는' 액션 하나. 없으면 None.

    조건은 전부 engine 과 1:1 대응이며, 여기를 통과한 액션은 무음 no-op 이 될 수 없다.
    """
    if tile is None:
        crop = _crop_of(i, day)
        if not _can_plant_day(i, crop, day):
            return None
        if seed_budget.get(crop, 0) <= 0:            # 하드 제약 1: 예산이 없으면 발행 자체를 안 한다
            return None
        return ["PLANT", crop]

    if not isinstance(tile, dict):                   # "LOCKED" — 타일 액션 전부 무효
        return None

    if _is_weed(tile):
        # 다시 심을 수 없는 시기라면 파낼 이유가 없다.
        if not _can_plant_day(i, _crop_of(i, day), day):
            return None
        return ["DIG"]

    if not _is_plant(tile):                          # COOP/PASTURE/동물 — v0 은 만들지 않는다
        return None

    ready = _harvest_ready(tile, day)
    in_win = _in_bonus_window(tile, day)
    cu = tile.get("consecutive_unwatered", 0)
    if not tile.get("watered_today", False):
        # 물주기가 실제 효과를 내는 경우 두 가지:
        #   1) 보너스 창 안 -> yield +1
        #   2) cu>=1 -> 오늘 안 주면 내일 아침 잡초가 된다 (단, 오늘 수확할 거면 불필요)
        if in_win or (cu >= 1 and not ready):
            return ["WATER"]
    if ready:
        # 하드 제약: 셰드 100칸 초과분은 조용히 소멸한다. 넘칠 것 같으면 걷지 않는다.
        if pending + tile.get("yield_units", 0) > SHED_CAP:
            return None
        return ["HARVEST"]
    return None


# ---------------------------------------------------------------------------
# obs 접근 헬퍼 (obs 는 dict 를 상속한 Struct 이지만 방어적으로 읽는다)
# ---------------------------------------------------------------------------
def _get(d, key, default=None):
    try:
        v = d[key]
    except Exception:
        try:
            v = getattr(d, key)
        except Exception:
            return default
    return default if v is None else v


def _inv_of(invs, u):
    if isinstance(invs, list) and u < len(invs) and isinstance(invs[u], dict):
        return invs[u]
    return {}


def _inv_sum(inv):
    return sum(int(v or 0) for v in inv.values())


# ---------------------------------------------------------------------------
# 계획
# ---------------------------------------------------------------------------
def _plan_unit(pos, inv, tiles, chunk, day, step, seed_budget, pending):
    """유닛 하나의 액션. (action, pending_delta) 반환."""
    turns_left = LAST_STEP + 1 - step        # 이번 턴 포함, 남은 '반영되는' 턴 수

    # --- 엔드게임: 손에 든 것은 셰드에 넣지 않으면 0원이다 (하드 제약 3) ---
    # 마지막 날은 하루 끝 자동 드롭(_end_of_day)이 돌지 않는다. 직접 걸어가서 DROP 해야 한다.
    if day >= LAST_DAY:
        home_d, home = min((_dist(pos, t), t) for t in SHED_TILES)
        # 여유 2턴을 두는 이유(off-by-one 방지):
        #   gap = turns_left - home_d 라 하면, 한 턴에 gap 은 최대 2 줄어든다
        #   (셰드 반대쪽으로 한 칸 이동: turns_left -1, home_d +1).
        #   그래서 gap<=1 에서 발동하면 gap=2 인 턴에 멀어지는 순간 gap=0 이 되어
        #   'DROP 할 1턴'이 사라진다. gap<=2 에서 발동하면 최소 gap=1 이 보장된다.
        if turns_left <= home_d + 2:         # 이동 home_d 턴 + DROP 1턴 + 여유 1턴
            if home_d > 0:
                mv = _step_toward(pos, home)
                if mv is not None:
                    return mv, 0
                return PASS, 0
            # 셰드 인접 — 들고 있으면 내린다 (빈 손이면 DROP 은 no-op 이므로 발행 금지)
            if _inv_sum(inv) > 0:
                return ["DROP"], 0
            # 빈 손이면 서 있는 칸에 할 일이 있으면 한다. 단 수확물을 내릴 턴이
            # 최소 1턴 남아 있을 때만 (마지막 턴에 걷으면 손에 든 채 끝나 0원이 된다).
            if turns_left >= 2:
                for i in chunk:
                    tx, ty = TILE_ORDER[i]
                    if (tx, ty) == (pos[0], pos[1]):
                        job = _tile_job(tiles[ty][tx], i, day, seed_budget, pending)
                        if job is not None:
                            return job, _job_pending_delta(job, tiles[ty][tx])
            return PASS, 0

    # --- 통상: 담당 구역에서 가장 가까운 '유효한 할 일' 을 고른다 ---
    best_key = None
    best = None
    for i in chunk:
        tx, ty = TILE_ORDER[i]
        job = _tile_job(tiles[ty][tx], i, day, seed_budget, pending)
        if job is None:
            continue
        key = (_dist(pos, (tx, ty)), i)
        if best_key is None or key < best_key:
            best_key, best = key, (job, tx, ty)
    if best is None:
        return PASS, 0
    job, tx, ty = best
    if best_key[0] == 0:
        return job, _job_pending_delta(job, tiles[ty][tx])
    mv = _step_toward(pos, (tx, ty))
    return (mv if mv is not None else PASS), 0


def _job_pending_delta(job, tile):
    """이 액션이 '언젠가 셰드로 갈 물량'을 얼마나 늘리는가 (셰드 상한 관리용)."""
    if job and job[0] == "HARVEST" and isinstance(tile, dict):
        return int(tile.get("yield_units", 0) or 0)
    return 0


def _simulate_drops(shed, invs, unit_actions):
    """이번 턴 유닛 페이즈가 끝난 뒤의 셰드 보유량을 정확히 예측한다.

    engine 순서: 유닛 액션 전부 -> _process_market. 따라서 같은 턴에 DROP 한 물건도
    같은 턴 SELL 로 팔린다. 이 예측이 정확해야 sell_unfilled 가 0 이 된다.
    """
    out = {k: int(v or 0) for k, v in shed.items()}
    total = sum(out.values())
    for u, act in enumerate(unit_actions):
        if not (isinstance(act, list) and act and act[0] == "DROP"):
            continue
        inv = _inv_of(invs, u)
        for item, n in inv.items():                  # engine 과 같은 순회 순서
            n = int(n or 0)
            if n <= 0:
                continue
            room = max(0, SHED_CAP - total)
            take = min(n, room)
            if take > 0:
                out[item] = out.get(item, 0) + take
                total += take
    return out


def _land_due(farm, day, hour):
    """오늘 사야 하는 다음 구획의 가격. NE→SW까지만 허용하고 SE는 반환하지 않는다."""
    unlocked = set(_get(farm, "unlocked_quadrants", []) or [])
    for quadrant, buy_day, buy_hour, cost in zip(
            LAND_QUADRANTS, LAND_PURCHASE_DAYS, LAND_PURCHASE_HOURS, LAND_COSTS):
        if quadrant in unlocked:
            continue
        due = day > buy_day or (day == buy_day and hour >= buy_hour)
        return cost if due else None
    return None


def _plan_market(obs, tiles, farm, private, unit_actions, day, hour):
    shed = _get(private, "shed", {}) or {}
    seeds = _get(private, "seeds", {}) or {}
    invs = _get(private, "inventories", []) or []
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    money = float(_get(farm, "money", 0) or 0)

    sim_shed = _simulate_drops(shed, invs, unit_actions)

    # 1) SELL — 셰드에 있는(그리고 이번 턴 들어올) 판매가능 품목 전량.
    #    수량이 실제 보유량과 정확히 같으므로 미체결이 나올 수 없다.
    #    매 턴 비우므로 셰드가 100칸에 닿는 일도 없다.
    sells = []
    for item in SELLABLE:
        n = int(sim_shed.get(item, 0) or 0)
        if n > 0:
            sells.append((float(prices.get(item, 0) or 0), item, n))
    sells.sort(reverse=True)                          # 클램프될 때 비싼 것부터 살아남게
    orders = [["SELL", item, n] for _p, item, n in sells]

    if day > LAST_DAY:
        return orders

    # 2) BUY_LAND — NE, SW를 날짜가 되면 순서대로 한 번씩 산다. SE는 대상에 없다.
    #    land는 HIRE/BUY_SEED보다 앞에 두어 10-slot clamp에서도 구매 시점을 지킨다.
    budget = money
    land_cost = _land_due(farm, day, hour)
    if land_cost is not None and budget >= land_cost:
        orders.append(["BUY_LAND"])
        budget -= land_cost

    # 3) HIRE — 하루 끝에 전원 해고되므로 목표 수까지 다시 뽑는다.
    #    10-slot을 넘는 목표는 여러 market turn에 걸쳐 채운다. hires_today가 fib index다.
    hires_today = int(_get(farm, "hires_today", 0) or 0)
    hires = 0
    for j in range(hires_today, N_HANDS):
        if j >= len(HIRE_FIB):
            break
        c = HIRE_FIB[j]
        if budget - c < 0:
            break
        budget -= c
        hires += 1
    orders.extend([["HIRE"]] * hires)

    # 4) BUY_SEED — 현재 unlocked 칸에 필요한 수만큼만. 남으면 다음 날로 이월된다.
    #    씨앗은 시장 페이즈에서 들어오므로 '오늘 산 씨앗은 다음 턴부터' 쓸 수 있다.
    need = {}
    for i in range(N_TILES):
        crop = _crop_of(i, day)
        if not _can_plant_day(i, crop, day):
            continue
        tx, ty = TILE_ORDER[i]
        tile = tiles[ty][tx]
        if tile is None or _is_weed(tile):
            need[crop] = need.get(crop, 0) + 1
        elif _is_plant(tile) and _harvest_ready(tile, day):
            need[crop] = need.get(crop, 0) + 1        # 오늘 걷으면 그 칸이 비고, 곧 심는다
    for crop in ("MELON", "STRAWBERRY", "WHEAT", "CARROT"):
        want = need.get(crop, 0) - int(seeds.get(crop, 0) or 0)
        if want <= 0:
            continue
        price = CROPS[crop]["seed"]
        want = min(want, int(budget // price))        # 잔고 초과 매수는 buy_failed 가 된다
        if want > 0:
            orders.append(["BUY_SEED", crop, want])
            budget -= want * price
    return orders


def plan(obs):
    player = int(_get(obs, "player", 0) or 0)
    day = int(_get(obs, "day", 0) or 0)
    hour = int(_get(obs, "hour", 0) or 0)
    # obs["step"] 은 신뢰하지 않는다 (공식 예제도 여기서 버그가 났다). day/hour 로 재구성.
    step = day * TURNS_PER_DAY + hour

    farms = _get(obs, "farms", []) or []
    farm = farms[player]
    tiles = farm["tiles"]
    hands = _get(farm, "hands", []) or []
    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    seeds = _get(private, "seeds", {}) or {}
    invs = _get(private, "inventories", []) or []

    n_units = 1 + len(hands)
    active_indices = [i for i, (x, y) in enumerate(TILE_ORDER)
                      if tiles[y][x] != "LOCKED"]
    chunks = _chunks(n_units, active_indices)

    # 하드 제약 1 — 작물별 씨앗 예산. 이번 턴 발행할 PLANT 총수가 보유 씨앗을 넘으면
    # engine 이 그 작물의 PLANT 를 **전부** 무효화한다. 그래서 배정 단계에서 차감한다.
    seed_budget = {c: int(seeds.get(c, 0) or 0) for c in CROPS}
    # 하드 제약: 셰드 100칸. '언젠가 셰드로 흘러갈' 총량을 추적한다.
    pending = sum(int(v or 0) for v in shed.values())
    for u in range(n_units):
        pending += _inv_sum(_inv_of(invs, u))

    unit_actions = []
    for u in range(n_units):
        pos = farm["farmer"] if u == 0 else hands[u - 1]
        inv = _inv_of(invs, u)
        act, delta = _plan_unit(pos, inv, tiles, chunks[u], day, step,
                                seed_budget, pending)
        if act and act[0] == "PLANT":
            seed_budget[act[1]] = seed_budget.get(act[1], 0) - 1
        pending += delta
        unit_actions.append(act)

    market = _plan_market(obs, tiles, farm, private, unit_actions, day, hour)
    return {"farmer": unit_actions[0], "hands": unit_actions[1:], "market": market}


# ---------------------------------------------------------------------------
# 가드 — 전부 (obs, action) -> action 의 순수 함수. GUARDS 리스트에서 하나씩 끌 수 있다.
# 계획이 옳다면 1~3번 가드는 절대 발화하지 않는다(발화 = 계획 버그).
# ---------------------------------------------------------------------------
def _units_of(obs):
    player = int(_get(obs, "player", 0) or 0)
    farm = (_get(obs, "farms", []) or [])[player]
    hands = _get(farm, "hands", []) or []
    return farm, [farm["farmer"]] + list(hands)


def _iter_unit_actions(action):
    yield 0, action.get("farmer", PASS)
    for h, a in enumerate(action.get("hands", []) or []):
        yield h + 1, a


def _set_unit_action(action, u, new):
    if u == 0:
        action["farmer"] = new
    else:
        action["hands"][u - 1] = new


def guard_unit_ops(obs, action):
    """engine 조건을 다시 확인해 '효과 없는' 유닛 액션을 제거한다 (noop 방지 최종선)."""
    day = int(_get(obs, "day", 0) or 0)
    farm, positions = _units_of(obs)
    tiles = farm["tiles"]
    private = _get(obs, "private", {}) or {}
    invs = _get(private, "inventories", []) or []
    seeds = _get(private, "seeds", {}) or {}
    shed = _get(private, "shed", {}) or {}
    shed_total = sum(int(v or 0) for v in shed.values())

    for u, act in list(_iter_unit_actions(action)):
        if u >= len(positions):
            continue
        if not (isinstance(act, list) and act):
            _set_unit_action(action, u, PASS)
            continue
        op = act[0]
        if op == "PASS":
            continue
        x, y = positions[u][0], positions[u][1]
        if op in MOVES:
            dx, dy = MOVES[op]
            if not (0 <= x + dx < BOARD_SIZE and 0 <= y + dy < BOARD_SIZE):
                _set_unit_action(action, u, PASS)      # 보드 밖 = blocked_move
            continue
        tile = tiles[y][x]
        ok = False
        if op == "DROP":
            ok = ((x, y) in SHED_TILES and _inv_sum(_inv_of(invs, u)) > 0
                  and shed_total < SHED_CAP)
        elif op == "PLANT":
            ok = (len(act) >= 2 and tile is None
                  and int(seeds.get(act[1], 0) or 0) > 0)
        elif op == "WATER":
            ok = _is_plant(tile) and not tile.get("watered_today", False)
        elif op == "HARVEST":
            ok = isinstance(tile, dict) and _harvest_ready(tile, day)
        elif op == "DIG":
            ok = (tile is not None and isinstance(tile, dict)
                  and "animal" not in tile)
        if not ok:
            _set_unit_action(action, u, PASS)
    return action


def guard_plant_budget(obs, action):
    """하드 제약 1 — 작물별 PLANT 발행 수 <= 보유 씨앗. 초과분만 PASS 로 되돌린다.

    engine 은 초과 시 그 작물의 PLANT 를 '전부' 버리므로, 넘치면 아주 비싸다.
    """
    private = _get(obs, "private", {}) or {}
    seeds = _get(private, "seeds", {}) or {}
    left = {c: int(n or 0) for c, n in seeds.items()}
    for u, act in list(_iter_unit_actions(action)):
        if isinstance(act, list) and len(act) >= 2 and act[0] == "PLANT":
            crop = act[1]
            if left.get(crop, 0) <= 0:
                _set_unit_action(action, u, PASS)
            else:
                left[crop] -= 1
    return action


def guard_shed_capacity(obs, action):
    """하드 제약 — 셰드 100칸 초과분은 조용히 소멸한다. 넘칠 DROP/HARVEST 를 막는다."""
    farm, positions = _units_of(obs)
    tiles = farm["tiles"]
    private = _get(obs, "private", {}) or {}
    invs = _get(private, "inventories", []) or []
    shed = _get(private, "shed", {}) or {}
    total = sum(int(v or 0) for v in shed.values())
    for u in range(len(positions)):
        total += _inv_sum(_inv_of(invs, u))
    for u, act in list(_iter_unit_actions(action)):
        if not (isinstance(act, list) and act):
            continue
        if act[0] == "HARVEST" and u < len(positions):
            x, y = positions[u][0], positions[u][1]
            tile = tiles[y][x]
            add = int(tile.get("yield_units", 0) or 0) if isinstance(tile, dict) else 0
            if total + add > SHED_CAP:
                _set_unit_action(action, u, PASS)
            else:
                total += add
    return action


def guard_final_liquidation(obs, action):
    """하드 제약 3 — step 718 에 셰드 전량 SELL.

    점수는 은행 현금뿐이고 재고는 0원이다. $1 에 팔아도 시장 재고가 늘지 않으므로
    (engine `_commit_unit`: `if price > 1`) 손해가 없다.
    """
    day = int(_get(obs, "day", 0) or 0)
    hour = int(_get(obs, "hour", 0) or 0)
    if day * TURNS_PER_DAY + hour != LAST_STEP:
        return action
    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    invs = _get(private, "inventories", []) or []
    unit_actions = [a for _u, a in _iter_unit_actions(action)]
    sim = _simulate_drops(shed, invs, unit_actions)
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    rows = [(float(prices.get(i, 0) or 0), i, int(sim.get(i, 0) or 0)) for i in SELLABLE]
    rows = [r for r in rows if r[2] > 0]
    rows.sort(reverse=True)
    action["market"] = [["SELL", i, n] for _p, i, n in rows]
    return action


def guard_market_sell(obs, action):
    """하드 제약 — SELL 수량 <= 실제 보유량 (미체결 0). 예측 셰드로 상한을 건다."""
    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    invs = _get(private, "inventories", []) or []
    unit_actions = [a for _u, a in _iter_unit_actions(action)]
    avail = _simulate_drops(shed, invs, unit_actions)
    out = []
    for o in action.get("market", []) or []:
        if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
            item = o[1]
            if item not in SELLABLE:                  # 동물 등은 SELL 대상이 아니다
                continue
            n = min(int(o[2] or 0), int(avail.get(item, 0) or 0))
            if n <= 0:
                continue
            avail[item] = avail.get(item, 0) - n
            out.append(["SELL", item, n])
        else:
            out.append(o)
    action["market"] = out
    return action


def clamp_market(obs, action):
    """하드 제약 2 — 시장 주문은 **오직 여기서만** 10칸으로 자른다.

    HIRE / BUY_LAND 도 같은 10칸을 소비한다. plan 단계에서 SELL -> HIRE -> BUY_SEED
    순으로 쌓아 두었으므로, 잘릴 때는 가치가 낮은 매수부터 잘린다.
    """
    m = action.get("market")
    action["market"] = list(m)[:MAX_MARKET_ORDERS] if isinstance(m, list) else []
    return action


def align_hands(obs, action):
    """하드 제약 4 — hands 길이를 관측된 farm["hands"] 길이에 정확히 맞춘다.

    파이프라인의 **마지막** 단계여야 한다. 모자라면 PASS 로 채우고 넘치면 자른다.
    (일꾼은 하루 끝에 전원 해고되고, 고용은 시장 페이즈라 다음 턴부터 관측된다.
     즉 hands 길이는 하루 중에도 변한다.)
    """
    player = int(_get(obs, "player", 0) or 0)
    farm = (_get(obs, "farms", []) or [])[player]
    n = len(_get(farm, "hands", []) or [])
    hs = action.get("hands")
    hs = list(hs) if isinstance(hs, list) else []
    if len(hs) > n:
        hs = hs[:n]
    while len(hs) < n:
        hs.append(list(PASS))
    action["hands"] = hs
    if not isinstance(action.get("farmer"), list) or not action["farmer"]:
        action["farmer"] = list(PASS)
    if not isinstance(action.get("market"), list):
        action["market"] = []
    return action


# 순서가 중요하다: 유효성 -> 예산 -> 셰드 -> 청산 -> SELL 상한 -> 클램프 -> align_hands(마지막)
GUARDS = (
    guard_unit_ops,
    guard_plant_budget,
    guard_shed_capacity,
    guard_final_liquidation,
    guard_market_sell,
    clamp_market,
    align_hands,
)


def _fallback(obs):
    n = FALLBACK_HANDS
    try:
        player = int(obs["player"])
        n = len(obs["farms"][player]["hands"])
    except Exception:
        pass
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(n)], "market": []}


def agent(obs, config=None):
    """하드 제약 5 — 절대 raise 하지 않는다."""
    try:
        action = plan(obs)
        for guard in GUARDS:
            action = guard(obs, action)
        return action
    except Exception:
        try:
            return _fallback(obs)
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}
