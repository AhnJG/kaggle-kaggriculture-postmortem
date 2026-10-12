# 시즌 흡수량 — 이 게임의 실제 경제 지도 `[ENGINE]`

**개정 이력**
- 2026-09-06 최초 작성. `POSTMORTEM_4bots.md` §3 "MELON 최고 작물" 과
  `MARKET_EXECUTION.md` §3 "멜론 실행 개선 상한 38,164" 를 뒤집었다.
- **2026-09-09 정정 (cowork).** §1 의 상점 해금 주기가 틀렸다.
  `townShopSellInterval`(소비 4턴)과 `townShopUnlockInterval`(해금 3일)을 혼동해
  "4일마다 7개"로 계산했다. **엔진은 3일마다 8개**다. 시즌 흡수량 전체가
  **약 +28.8%** 상향된다. 순위와 전략 결론은 바뀌지 않는다. §6 참조.

---

## 1. 수요는 어디서 오는가 (kaggriculture.py:103-118, 728-749, 860-891)

시장 재고를 **끌어내리는**(= 가격을 올리는) 주체는 둘뿐이다.

| 주체 | 주기 | 대상 | 근거 |
|---|---|---|---|
| 타운센터 | **24턴**마다 각 1개 | `TOWN_CENTER_PRODUCTS` (FERTILIZER 제외 8종) | `:745` `townCenterSellInterval` default 24 |
| 상점 인스턴스 | **4턴**마다 | 그 상점의 품목. **단일품목 상점은 ×2** | `:733` `townShopSellInterval` default 4 |

**상점 해금은 소비 주기와 다른 값이다.**

| 항목 | 값 | 근거 |
|---|---|---|
| 해금 주기 | **3일** | `:867` `townShopUnlockInterval` default 3, `kaggriculture.json` |
| 해금 조건 | `next_day % 3 == 0` (하루 끝에 1개) | `:886` |
| 총 상한 | **8개** | `:118` `MAX_SHOP_INSTANCES = 8` |
| 실제 스케줄 | **day 3·6·9·12·15·18·21·24** → 24일차에 상한 도달 | 위 셋의 조합 |
| 추출 방식 | `rng.choice(sorted(SHOPS))` **복원추출** — 중복 가능, 각 인스턴스가 독립 소비 | `:891` |

시드는 관측에서 제거되어 **미래 해금은 예측 불가**다. 그러나
**현재 해금된 목록 `town.unlocked_shops` 는 관측 가능하고 양 플레이어가 공유한다.**
→ 매도 스케줄은 미래를 추측할 필요 없이 **지금 열린 상점만 보고** 정하면 된다(§5).

| 상점 | 소비 품목 | 배수 | w(가중 슬롯 수) |
|---|---|---|---|
| YARN_STORE | WOOL | **×2** | WOOL +2 |
| PET_CAFE | CARROT | **×2** | CARROT +2 |
| BAKERY | EGG, WHEAT | ×1 | 각 +1 |
| PIZZA_SHOP | MILK, TOMATO, WHEAT | ×1 | 각 +1 |
| BRUNCH_SPOT | EGG, WHEAT, STRAWBERRY | ×1 | 각 +1 |
| ICE_CREAM_SHOP | STRAWBERRY, MILK, WHEAT | ×1 | 각 +1 |
| SMOOTHIE_SHOP | STRAWBERRY, MILK | ×1 | 각 +1 |
| FARMERS_MARKET | WHEAT, CARROT, TOMATO, STRAWBERRY | ×1 | 각 +1 |

품목별 `w` (8개 상점 종류 기준): WHEAT 5 · STRAWBERRY 4 · MILK 3 · CARROT 3 ·
TOMATO 2 · EGG 2 · WOOL 2 · **MELON 0** · **FERTILIZER 0**

## 2. 시즌 흡수량과 가치 상한 (기댓값, 상점 균등추출 가정)

상점 인스턴스 소비 tick 합 = **792** (day 3 해금분 162 tick … day 24 해금분 42 tick).
타운센터 = 30 tick.

`시즌흡수량(X) = 792 × w(X)/8 + (FERTILIZER 면 0, 아니면 30)`

| 품목 | **시즌 흡수량** | base | **시즌 가치 상한** | (구 값) | 상점 등장 |
|---|---:|---:|---:|---:|---|
| **MILK** | **327** | 160 | **52,320** | 40,080 | PIZZA, ICE_CREAM, SMOOTHIE |
| **STRAWBERRY** | **426** | 120 | **51,120** | 38,880 | BRUNCH, ICE_CREAM, SMOOTHIE, FARMERS |
| **WOOL** | **228** | 200 | **45,600** | 35,400 | YARN_STORE (×2) |
| TOMATO | 228 | 60 | 13,680 | 10,620 | PIZZA, FARMERS |
| WHEAT | 525 | 25 | 13,125 | 9,938 | 5종 |
| CARROT | 327 | 35 | 11,445 | 8,768 | PET_CAFE(×2), FARMERS |
| EGG | 228 | 50 | 11,400 | 8,850 | BAKERY, BRUNCH |
| **MELON** | **30** | 250 | **7,500** | 7,500 | **없음 — 타운센터뿐** |
| FERTILIZER | **0** | 100 | **0** | 0 | **없음 — 타운 수요 자체가 없다** |
| **합계** | | | **206,190** | 160,035 | 두 플레이어가 나눠 갖는 전체 파이 |

재현:
```bash
python3 - <<'PY'
SHOPS={"BAKERY":["EGG","WHEAT"],"PIZZA_SHOP":["MILK","TOMATO","WHEAT"],
"BRUNCH_SPOT":["EGG","WHEAT","STRAWBERRY"],"YARN_STORE":["WOOL"],
"ICE_CREAM_SHOP":["STRAWBERRY","MILK","WHEAT"],"PET_CAFE":["CARROT"],
"SMOOTHIE_SHOP":["STRAWBERRY","MILK"],"FARMERS_MARKET":["WHEAT","CARROT","TOMATO","STRAWBERRY"]}
base={'MILK':160,'STRAWBERRY':120,'WOOL':200,'TOMATO':60,'WHEAT':25,'EGG':50,'CARROT':35,'MELON':250,'FERTILIZER':100}
w=lambda it: sum((2 if len(v)==1 else 1) for v in SHOPS.values() if it in v)
ticks=sum(len([s for s in range(d*24+1,721) if s%4==0]) for d in [3,6,9,12,15,18,21,24])
for it,b in sorted(base.items(), key=lambda kv:-(ticks*w(kv[0])/8+(0 if kv[0]=='FERTILIZER' else 30))*kv[1]):
    a=ticks*w(it)/8+(0 if it=='FERTILIZER' else 30); print(f"{it:<11}{a:7.0f}{a*b:10.0f}")
PY
```
검증: 위 값을 8개 상점 전부 열린 정상상태 일일 흡수율로 환산하면
딸기 25 · 우유 19 · 당근 19 · 밀 31 · 양털 13 · 토마토 13 · 달걀 13 · 멜론 1 · 비료 0 으로
**`FACTS.md` 의 `[ENGINE+계산]` 일일 흡수율표와 정확히 일치한다.**

## 3. 최초 작성 때 내가 틀린 부분 (2026-09-06)

**MELON 은 어느 상점 목록에도 없다.** 타운센터가 24턴마다 1개, 시즌 총 30개가 전부다.
단가 250 은 재고가 `I0` 근처일 때의 값이고, 그 상태는 30개까지만 유지된다.

- 나는 "한 턴 20개 투매 단가"로 작물을 순위매겼다. 그건 **순간 흡수력**이지 시즌 용량이 아니다.
- 그 결과 KAGRI-015 는 **시즌 수요가 30개인 작물에 75칸 중 30칸을 배정**했다.
- seed 1000 에서 우리는 **MELON 259개**를 팔았다. 흡수량의 8.6배다.
- `MARKET_EXECUTION.md` 의 "완전 분산 시 259개 × 250 = 64,750" 도 같은 이유로 틀렸다.

**교훈: 순간 단가가 아니라 `시즌 흡수량 × base` 가 작물·품목 선택의 지표다.**

## 4. 이것이 말해주는 것

| 블록 | 시즌 가치 | 전체 비중 | 필요한 것 |
|---|---:|---:|---|
| **MILK + WOOL** | **97,920** | **47.5%** | **동물 레이어** |
| STRAWBERRY | 51,120 | 24.8% | 작물 배분만 |
| 나머지 6종 | 57,150 | 27.7% | — |

우리 seed 1000 판매: MELON 259 (상한 30), WHEAT 314, STRAWBERRY 102 (상한 426), CARROT 6.
**우리는 상한 7,500 짜리 품목에 집중하고 52,320·51,120·45,600 짜리를 비워뒀다.**

boatlee 판매: MILK 320, STRAWBERRY 300, WOOL 154, WHEAT 479, MELON 126, FERTILIZER 300.
상위 3블록을 정확히 채운다. 멜론은 126개만 판다 — 초과분은 어차피 값이 안 나온다는 걸 안다.

## 5. ★ 흡수량은 상수가 아니다 — 매도 상한은 시간의 함수다

**시즌 총량을 30으로 나눈 평탄 상한은 모델 오류다.** 상점은 day 3 에 1개로 시작해
day 24 에 8개가 된다. 같은 품목의 일일 흡수량이 게임 후반에 **8배**가 된다.

관측 가능한 정확한 값(기댓값이 아니라 실현값):

```python
# turnsPerDay 24 / townShopSellInterval 4 -> 하루 6 tick
SHOP_PRODUCTS = {  # kaggriculture.py:103-112, 정적 상수
  "BAKERY":["EGG","WHEAT"], "PIZZA_SHOP":["MILK","TOMATO","WHEAT"],
  "BRUNCH_SPOT":["EGG","WHEAT","STRAWBERRY"], "YARN_STORE":["WOOL"],
  "ICE_CREAM_SHOP":["STRAWBERRY","MILK","WHEAT"], "PET_CAFE":["CARROT"],
  "SMOOTHIE_SHOP":["STRAWBERRY","MILK"],
  "FARMERS_MARKET":["WHEAT","CARROT","TOMATO","STRAWBERRY"],
}

def daily_absorption(item, unlocked_shops):
    """지금 열린 상점 목록 기준 하루 시장 흡수량. town.unlocked_shops 는 관측 가능."""
    per_tick = 0
    for name in unlocked_shops:                 # 중복 등장 가능 — 그대로 센다
        prods = SHOP_PRODUCTS[name]
        if item in prods:
            per_tick += 2 if len(prods) == 1 else 1
    return 6 * per_tick + (0 if item == "FERTILIZER" else 1)
```

- day 1~2 는 상점 0개다. **모든 품목의 일일 흡수량이 1**(타운센터뿐)이다.
  이 구간의 대량 매도는 시장을 초기부터 눌러 시즌 내내 손해다.
- 흡수량은 **양 플레이어가 나눠 갖는 전체 시장 값**이다. 상대도 같은 품목을 판다면
  우리 몫은 그 이하다. 상한을 쓸 때 share factor 를 함께 정의하라.
- FERTILIZER 는 타운 수요가 0이라 이 함수가 0을 준다. §6 의 제로섬 구조를 따로 본다.

## 6. FERTILIZER 예외

타운 수요가 0인데 boatlee 는 300개를 판다. 재고를 내리는 유일한 경로는
**상대의 `BUY_PRODUCT`** 다(boatlee 자신도 99회 매수). 즉 비료 시장은 두 플레이어 사이의
제로섬이며, 상대가 사주지 않으면 가격이 바닥으로 간다. `[HYPOTHESIS]` 로만 다룬다.

## 7. 2026-09-09 정정의 영향 범위

| 영향 | 판정 |
|---|---|
| 품목 순위 (MILK > STRAWBERRY > WOOL > …) | **불변** |
| MELON 30 상한, FERTILIZER 0 | **불변** |
| "MILK+WOOL 이 최대 레버" 결론 | **불변** (47% → 47.5%) |
| 시즌 흡수량 **절대값** | **+28.8%** — 매도 상한을 이 값에서 유도하던 곳 전부 수정 |
| `BRIEF_exp003_absorption.md` A-2 의 고정 cap 표 | **폐기** — §5 의 동적 함수로 대체 |
