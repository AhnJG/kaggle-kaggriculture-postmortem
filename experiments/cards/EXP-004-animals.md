# EXP-004 — 동물 레이어 (v2)

hypothesis_id: HYP-0004
test_id: TEST-0004

상태: **사전등록** (실행 전 작성, 2026-09-10) · 작성자 Claude (`experiments/cards/` 소유)
대응 브리프: `coordination/proposals/codex/BRIEF_exp004_animals.md`

## 공통

- parent: `experiments/candidates/v2c_c3_strawberry30.py`, sha256 `adf8e798…855`
  (고정하는 `main.py` sha256 `d6cdb83f…59`)
- engine: `kaggle-environments==1.32.7`, `kaggriculture.py` sha256
  `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- hypothesis `[HYPOTHESIS]` **H20**: PASTURE 기반 소·양을 도입하면 유휴 액션이
  MILK·WOOL·FERTILIZER 산출로 전환되어, 4봇 상대 평균 뱅크와 `pass_rate` 가 동시에 개선된다.
- **메커니즘 지표는 `pass_rate` 다.** 뱅크만 오르고 `pass_rate` 가 그대로면
  H20 이 맞아서 오른 것이 아니다. 결과를 `불확정` 으로 기록한다.
- forbidden: SE 구획 매입(K1), GOOSE·`BUILD_COOP`(K9), **MELON 타일 재배분(K10)**,
  작물 구성·전환일·토지 타이밍 변경, 결과 확인 후 시드 추가
- pilot: 시드 `1000..1019` × 양 좌석 = 40경기/비교
- promotion: 4봇 각 시드 `1000..1049` × 양 좌석 = 400경기
- primary metric: paired score 와 seed-level 95% CI
- **탐색 지표**(`AGENTS.md §7.1b`): 4봇 상대 우리 평균 뱅크 + `pass_rate`

## 왜 §1(MELON 수정)이 이 카드에 없는가

같은 parent·같은 변경·같은 `1000..1049` 로 **이미 실행되어 실패했다**
(KAGRI-016: 29,212.665 vs 29,310.670, **−98.005**). `evidence/KILLS.md` K10 에 등재했다.
현재 HARVEST 는 230회(전체 액션의 3.4%)로 묶여 있어 작물 구성이 총 산출을 바꾸지 못한다.
**재검토 조건은 액션 병목이 해소된 뒤다.** 이 카드에서 다시 시도하지 않는다.

## 선행 계측 (실험 아님 — stage A 전에 완료)

`tools/instrument.py` (Codex 소유) 에 추가:

| 카운터 | 정의 | gate |
|---|---|---|
| `harvest_blocked_by_shed` | `guard_shed_capacity` 가 HARVEST 를 PASS 로 바꾼 횟수 | **>0 → FAIL** |
| `unfed_animal_days` | 동물이 하루를 급여 없이 넘긴 횟수 | **>0 → FAIL** |
| `animals_lost` | 2일 연속 미급여 소실 동물 수 | **>0 → FAIL** |
| `shed_peak` | `sum(shed.values())` 최댓값 | 진단 |
| `pass_rate` | 전체 유닛 액션 중 PASS 비율 (전체 / day0-8 / day9-29) | **진단 · H20 판정용** |

계측 완료 후 parent 로 기준선을 1회 측정해 `experiments/results/v2n_baseline.json` 에 남긴다.
**이 기준선의 `pass_rate` 가 모든 stage 의 비교 대상이다.**

## 고정 pilot 순서 — 각 stage 는 정확히 한 factor

parent 의 `N_HANDS = 9` 를 **stage A 에서 바꾸지 않는다.** 동물과 일꾼을 동시에 바꾸면
어느 쪽 효과인지 분리할 수 없다(이전 브리프의 결함).

### stage A — 동물 도입 여부와 규모 (hands = 9 고정)

| 후보 | 구성 |
|---|---|
| A0 | 동물 없음 = parent (대조군) |
| A1 | COW 3 / SHEEP 1 |
| A2 | COW 5 / SHEEP 2 |
| A3 | COW 8 / SHEEP 4 |

round-robin 4후보 × 각 쌍 40경기. 비료는 전량 매도, FERTILIZE 미사용으로 고정.
**A0 을 반드시 포함한다** — 동물이 hands=9 에서 오히려 해로울 수 있다(급여 액션이 수확을 밀어낸다).

- 선택 규칙: paired score 합 최대.
- **A0 이 이기면 stage B 로 가지 말고 카드를 FAILURE 로 종료**하고,
  "hands=9 에서는 동물이 순손해" 를 보고한다. 그 경우 다음 카드는 hands 단독 증원이다.
- threshold: paired score 합 차이가 **0.20 미만이면 `불확정`** 으로 기록하고,
  tie-break (1) head-to-head (2) big-loss 적은 쪽 (3) mean bank (4) 마리 수 적은 쪽.

### stage B — 일꾼 수 (stage A 승자 구성 고정)

`N_HANDS` ∈ {9(=A승자 그대로), 12, 14, 16}. round-robin.
동일 threshold·tie-break. tie-break (4) 는 **일꾼 수 적은 쪽**.

### stage C — 동물 규모 재확대 (stage B 승자 고정, B 가 9를 골랐으면 stage C 생략)

stage A 에서 hands=9 제약으로 눌렸던 마리 수를 다시 연다.
`{A승자 그대로, COW 8/SHEEP 4, COW 10/SHEEP 4, COW 9/SHEEP 8}`.
뒤 세 조합은 Gemini KAGRI-006 이 실측한 공개 상위 봇 4종의 실제 구성이다.

### stage D — 비료 용도 (stage C 승자 고정)

| 후보 | 정의 (구현자 임의 해석 금지) |
|---|---|
| D1 | 보유 FERTILIZER 전량을 매도 큐에 올린다. `FERTILIZE` 를 발행하지 않는다 |
| D2 | `FERTILIZE` 만 쓴다. 매도하지 않는다. **대상 타일 = 그 유닛 담당 구역에서 `fertilized_until_day < day` 이면서 `_harvest_ready` 가 아닌 PLANT 타일 중 가장 가까운 것.** 대상이 없으면 그 유닛은 평소 로직대로 행동한다 |
| D3 | 하루 누적 5개까지 매도, 그 이후 획득분은 D2 규칙으로 `FERTILIZE` |

FERTILIZER 는 **타운 수요가 0** 이다(`ABSORPTION.md`). 상대의 `BUY_PRODUCT` 만이 재고를 내린다.
D1 이 이길 근거는 약하지만 대조군으로 반드시 돌린다.

### stage E — 승격 판정

4봇 각 50시드 × 양 좌석 = 400경기.

- **SUCCESS**: 선행 계측 gate 전부 CLEAN **且** 4봇 합산 95% CI 하한 > 0.5
  **且** 4종 중 3종 이상에서 개별 CI 하한 > 0.5
- **FAILURE**: gate 위반 또는 CI 상한 < 0.5 → parent 유지
- **UNCERTAIN**: CLEAN 이나 CI 가 0.5 포함 → 같은 시드 재튜닝 금지, 새 가설을 별도 카드로

`§7.1b` — 4봇 상대가 여전히 0/0/400 이면 페어드 점수는 정보가 없다.
그 경우 **탐색 지표(평균 뱅크 + `pass_rate`)** 로 후보를 고르고 **승격은 하지 않는다.**

## 예상 실패면

급여 액션이 수확을 밀어내 총 산출 감소 · 셰드 100 초과(현재도 피크 99) ·
미배치 동물이 셰드 점유 · `BUY_ANIMAL` 이 10슬롯을 먹어 BUY_SEED/HIRE 추가 절단 ·
초기 현금 부족으로 동물 구매 무음 취소 · 2일 미급여 소실 · 먼 PASTURE 왕복으로 이동 액션 증가

## 진단으로 반드시 기록

`pass_rate`(3구간) · 품목별 실현 총액과 실현 단가 · 판매량 ÷ 시즌 흡수량(초과 배수) ·
`shed_peak` · gate 카운터 4종 · 클램프 전후 주문 줄 수와 종류별 절단 개수 ·
액션 타입별 분포(WATER/HARVEST/PLANT/FEED/CARE/COLLECT_FERTILIZER/FERTILIZE/이동/PASS)
