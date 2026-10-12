# S4~S7 실행 결과 (2026-09-06)

> ⚠️ **2026-09-06 정정**: 아래 "발견 1"과 "발견 2"는 **계측기 귀속 버그의 산물이었다.**
> `id(farm)` 기반 귀속이 틀렸고(엔진이 매 스텝 관측 객체를 새로 만들고 id 를 재활용한다),
> 상대의 무음 실패가 P0 버킷으로 샜다. 계측기는 호출 순서 기반으로 수정됐다.
> **정정된 사실: `starter` 의 무음 실패는 상대와 무관하게 0 이다.** 147~167 은 `random` 의 것이었다.
> 상세는 `evidence/FACTS.md` "계측기 귀속 버그" 항목. S4·S7 결과 자체는 영향 없다.

실행 환경: Python 3.11.15 · `kaggle-environments==1.32.7`
엔진 해시 검증: `kaggriculture.py` sha256 = `bc8a5487…653e` — **ENGINE_LOCK 과 일치**

---

## S4 — 공식 3봇 양 좌석 720턴 완주  ✅ PASS

`python3 tools/smoke.py --outdir private_artifacts/replays`

| A | B | steps | rewards | status |
|---|---|---:|---|---|
| pass | pass | 720 | 3000 / 3000 | DONE / DONE |
| pass | random | 720 | 3000 / 0 | DONE / DONE |
| random | pass | 720 | 0 / 3000 | DONE / DONE |
| pass | starter | 720 | 3000 / 3421 | DONE / DONE |
| starter | pass | 720 | 3421 / 3000 | DONE / DONE |
| random | random | 720 | 0 / 0 | DONE / DONE |
| starter | random | 720 | 3431 / 0 | DONE / DONE |
| random | starter | 720 | 0 / 3641 | DONE / DONE |
| starter | starter | 720 | 3507 / 3507 | DONE / DONE |

전 조합 720스텝 완주, 예외 0, 리플레이 저장 확인.

**읽을 것**
- `random`은 **항상 0으로 끝난다.** 무작위 매수로 3,000을 전부 소진한다. 상대로서 정보가치가 없다.
- `pass`는 3,000 그대로. 즉 **아무것도 안 하는 것이 무작위로 움직이는 것보다 낫다.**
- `starter`는 3,421~3,641. 30일 순익 약 400~640. 상위권 90~95k 대비 **1/150 수준.**

---

## S6 — 무음 실패 계측기  ✅ 동작 확인

`python3 tools/instrument.py --a <A> --b <B> --seeds <...> [--time-agent a]`

네 가지를 센다. **전부 예외를 내지 않는 손실이다.**

| 카운터 | 무엇 |
|---|---|
| `noop_actions` | 발행했는데 타일도 인벤토리도 안 바뀐 유닛 액션 (턴 낭비) |
| `shed_discarded` | 셰드 100칸 초과로 소멸한 품목 수 |
| `orders_truncated` | 11번째부터 잘린 시장 주문 수 |
| `sell_unfilled` | SELL 요청 수량 − 실제 체결 수량 |
| (참고) `blocked_moves` `buy_failed` `exceptions` | |

### 발견 1 — 공식 `starter`는 액션의 약 20%를 버린다

`starter` vs `random`, seed 7:
```
P0 starter  noop=147   PLANT:70  WATER:41  HARVEST:36
P1 random   noop=165   PLANT:93  HARVEST:38 WATER:34
```
`starter`는 720턴 중 **147턴이 무효**다. 우리 v0의 기준선이 여기다.

### 발견 2 — **상대가 공유 시장을 통해 우리 액션을 낭비시킬 수 있다**

같은 `starter`인데 상대에 따라 무음 실패가 달라진다:

| 대진 | starter 의 noop |
|---|---:|
| starter vs **starter** | **0** |
| starter vs **random** | **147** |

미러전에서는 0인데 `random` 상대로는 147이다.
원인: `random`이 무작위로 씨앗을 사면서 **공유 시장 가격을 흔들고**, 그 결과 `starter`가
씨앗을 못 사서 `PLANT`가 조용히 실패한다. 시장은 두 플레이어가 공유하므로
**상대의 매수 패턴이 우리 액션 예산을 갉아먹는다.**

→ 이건 `[LOCAL]` 관측이고, "상대의 시장 조작으로 상대 액션을 낭비시킬 수 있는가"라는
가설(HYPOTHESES H12)로 승격 대상이다. 그리고 우리 봇은 **씨앗 부족 시 PLANT를 발행하지
않도록** 방어해야 한다(같은 턴 같은 작물 PLANT 유닛 수 ≤ 보유 씨앗).

### 계측기 자체의 함정 (기록해 둠)
`K.interpreter = ...` 로 패치해도 **소용없다.** kaggle-environments 레지스트리가 모듈 로드
시점의 함수 객체를 이미 잡고 있다. 대신 그 interpreter 가 매 스텝 **모듈 전역 이름으로**
호출하는 `_initialize` / `_process_market` / `_apply_unit_action` /
`_drop_inventories_to_shed` / `_commit_unit` 을 감싸야 한다.
좌석 교체 테스트로 귀속이 맞는지 반드시 검증할 것 (`--a X --b Y` 와 `--a Y --b X`).

---

## S7 — 페어드 아레나  ✅ 동작 확인

`python3 tools/arena.py --a <A> --b <B> --seeds 200 --seed-file configs/paired_seeds.txt`

같은 시드마다 **양 좌석을 모두** 돌리고, **시드 단위**로 묶어 신뢰구간을 낸다.
(경기 단위로 묶으면 좌석 상관을 이중계산한다.)

검증 실행 `starter` vs `random`, 시드 20개 / 40판:
```
페어드 점수 1.0000  95% CI [1.0000, 1.0000]
W/D/L 40/0/0   마진 평균 3,594   대패(>10k) 0   에러 0   75.0s
판정: A 우세 (CI 하한 1.000 > 0.5)
```

**처리량**: 경기당 약 1.8초 → **200시드(400판)에 약 12분**. 승격 판정에 충분히 실용적이다.

---

## 다음 (S8~S11)
v0 최소 봇을 만들고 위 게이트를 통과시킨다.
- 예외 0 **그리고** 무음 실패 4종 0
- `--time-agent a` 로 턴당 p99 측정 (vCPU 1.6 가정, 스레드 1로 고정)
- self-play 3판 완주 (공식 validation 과 동일 조건)
