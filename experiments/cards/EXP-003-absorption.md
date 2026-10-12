# EXP-003 — absorption-aligned crop, sale, and slot policy

hypothesis_id: HYP-0003
test_id: TEST-0003

상태: **CORRECTION GATE FAILURE** (2026-09-09). `[LOCAL]` 4봇 평균 final bank가 source parent보다 98.005 낮아 Stage A–D는 실행하지 않았다. 상세는 `experiments/results/v2a_correction_summary.json`.

> 이 카드는 correction 실행 전에 작성됐다. 실행 중 정본 brief가 다시 개정되어 고정 cap은 부록 B의 동적 cap으로 대체되고 `harvest_blocked_by_shed` 계측이 추가됐다. correction에서 이미 필수 bank gate를 실패했으므로 이전/새 cap으로 Stage B를 실행한 결과는 모두 없다.

## 공통

- source parent: KAGRI-015 `experiments/candidates/v2c_c3_strawberry30.py`, SHA-256 `adf8e798a11ec461f2d9c95aa0ed34927ebf0c122684ec94852b30f8ded37855`; 이 wrapper가 고정하는 `main.py` SHA-256 `d6cdb83ffdb27d2614330b20d438a6a20e82c7f4a72ead5ca8be897859de0b59`.
- correction: MELON 30 → 3, 회수한 27칸은 STRAWBERRY로 전환해 MELON 3 / STRAWBERRY 57 / WHEAT 15. 다른 factor는 source parent와 같다.
- engine: `kaggle-environments==1.32.7`, `kaggriculture.py` SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`.
- immutable policy helper: `experiments/candidates/exp003_policy.py`, SHA-256 `ea02c5ecfe66def23dc0f40303286e2e70bfd594e7047d9bfedb81e9e76c8665`. 모든 candidate wrapper가 이 SHA와 `main.py` SHA를 import 전에 확인한다.
- runner: `tools/arena.py` SHA-256 `e6da4580d72169f656329c62f1827fbf3796678b08beab60c4c9befa3422f936`; instrument: `tools/instrument.py` SHA-256 `e7d93c77d386889215deee3c5287e43efbf26634e43d90985ce7c87a9e732a6f`.
- correction/A wrappers: `v2a_parent.py` `753ef229d3a7b65c6068da6b132b4189bc37b3a0e543617aa66b3e0cb3120e02`; A1 `7c8056c438422fd46159f62edb3c3b8d578dc2612ae2d0a44f75f4edc332b770`; A2 `6a26a25ff8e8483d14c39897dd3be8e14fd578e5451de1a4761cbdff4bb378c1`; A3 `7a4d522c58db51cefba94042b716bbdf536ce93c249c38617a13e96f8d222834`.
- hypothesis `[HYPOTHESIS]`: 시즌 흡수량을 넘긴 MELON 생산을 STRAWBERRY와 흡수 가능한 보조 작물로 옮기고, 판매를 회복량에 맞게 분산하며 BUY_SEED/HIRE 경합을 줄이면 공개 상위 봇 상대 우리 평균 final bank가 증가하고 최종적으로 W/D/L이 개선된다.
- postmortem basis: `[LOCAL]` 아래 명령에서 source parent가 boatlee에 42,050 대 121,116으로 패했고, 돌아오지 못한 분기일은 day 1, gap 악화 최악은 day 20(-10,085)이었다. `evidence/ABSORPTION.md:31-59`는 이 parent가 seed 1000에서 시즌 흡수량 30인 MELON을 259개 팔고 STRAWBERRY는 102개만 판 것을 원인으로 좁힌다.

```bash
python3 tools/postmortem.py \
  --a experiments/candidates/v2c_c3_strawberry30.py \
  --b opponents/public/boatlee.py --seed 1000
```

- forbidden: SE purchase, animal/fertilizer action, hard-coded market price, 결과 확인 후 seed·기준 변경, `kaggle.json`, Kaggle submission.
- pilot: reused holdout `1000..1019`, 각 pair는 same seed × both seats = 40 games.
- correction/stage D: reused holdout `1000..1049`, 공개 봇별 same seed × both seats = 100 games, 4봇 합계 400 games.
- primary promotion metric: seed-level paired score와 95% CI. exploration metric은 4봇 상대 후보의 평균 final bank다. mean margin은 진단 전용이다.
- required diagnostics: W/D/L, loss count/variance, 품목별 판매량·실현 총액·평균 단가·흡수량 초과 배수, market/SELL 발행 턴, 평균 SELL 수량, 10-slot 포화 턴, 일별 최대 shed 점유, 안전밸브 횟수, pre/post-clamp 줄 수와 잘린 order type.

## 선행 correction gate

source parent의 MELON 30 / STRAWBERRY 30 / WHEAT 15에서 MELON 27칸만 STRAWBERRY로 바꾼 `v2a_parent.py`를 평가한다.

1. `v2a_parent.py` self-play를 `1000..1049`에서 실행한다. 양 player의 `noop_actions`, `blocked_moves`, `shed_discarded`, `orders_truncated`, `sell_unfilled`, `buy_failed`, `exceptions`가 모두 0이고 daily min cash가 0 이상이어야 한다.
2. source parent와 correction을 각각 공개 봇 4종에 `1000..1049` × both seats로 실행한다.
3. correction의 400-game 평균 final bank가 source parent 이상이면 PASS하여 SHA를 동결한다. 낮으면 FAILURE로 중단하고 source parent를 유지한다.

## 공통 hard gate

Stage A/B/C의 각 variant는 비교 전에 `1000..1019` self-play instrument gate를 통과해야 한다. 양 player silent-failure counter 7종과 daily min cash 기준은 correction gate와 같다. `shed_discarded >= 1`이면 즉시 FAIL이다. step 718 market은 SELL만 허용하고 전량 청산해야 한다.

## Stage A — crop allocation

correction parent의 sell/slot 동작을 고정하고 crop allocation 하나만 바꾼다.

- A1: MELON 3 / STRAWBERRY 45 / WHEAT 27
- A2: MELON 3 / STRAWBERRY 30 / TOMATO 12 / WHEAT 30
- A3: MELON 3 / STRAWBERRY 45 / CARROT 12 / WHEAT 15

## Stage B — sale schedule

Stage A winner의 생산 및 C1 slot 순서를 고정하고 schedule/cap profile 하나만 바꾼다.

- B1: current, cap 없음.
- B2: observation hour `1,7,13,19`; caps WHEAT 4, STRAWBERRY/CARROT/MILK 3, TOMATO/EGG/WOOL 2, MELON/FERTILIZER 1.
- B3: 짝수 observation hour 12개; caps WHEAT 2, 나머지 8품목 1.
- B2/B3 safety valve: 관측 shed 합계가 60 이상이면 그 turn은 cap을 무시하고 전량 SELL한다. step 718도 전량 SELL한다.

## Stage C — BUY_SEED/HIRE slot allocation

Stage A와 Stage B winner를 고정하고 market slot 순서 하나만 바꾼다.

- C1: SELL → BUY_LAND → HIRE → BUY_SEED.
- C2: SELL → BUY_LAND → BUY_SEED → HIRE.
- C3: SELL 최대 4줄 → BUY_LAND 최대 1줄 → BUY_SEED 최대 3줄 → HIRE remaining slots. Safety valve turn에는 SELL 4줄 제한을 해제한다.

## Pilot 선택 규칙

각 stage에서 clean variant끼리 3개 pairwise comparison을 모두 실행한다. variant의 pairwise paired-score 합이 가장 큰 것을 선택한다. 합이 같으면 (1) head-to-head paired score, (2) loss count, (3) loss-margin variance, (4) mean margin, (5) 더 단순한 profile 순이다. 단순성 순서는 A1→A3→A2, B1→B2→B3, C1→C2→C3으로 사전 고정한다. 그래도 같으면 UNCERTAIN으로 중단하며 seed를 추가하지 않는다.

## Stage D — promotion gate

Stage C winner를 공개 봇 4종에 `1000..1049` × both seats로 평가한다. 4봇 합산 seed-level paired-score score 95% CI 하한이 0.5를 넘고, 4종 중 3종 이상의 개별 CI 하한도 0.5를 넘으면 promotion SUCCESS다. hard gate 실패 또는 합산 CI 상한이 0.5 미만이면 FAILURE, 그 밖은 UNCERTAIN이다.

winner와 `v2a_parent.py`가 모두 0/0/400이면 W/D/L은 포화다. 이 경우 평균 final bank가 높은 clean candidate를 다음 card parent로 채택하되 promotion이나 `[HOSTED]` 우위를 주장하지 않는다. candidate-vs-parent direct match는 50 matched seeds로 실행하지만 진단 전용이다.

## Expected failure plane과 next

- B2/B3 cap으로 shed가 100에 도달해 product가 소멸한다.
- C2/C3 seed-first가 당일 hands 수를 줄여 crop care/harvest를 놓친다.
- TOMATO/STRAWBERRY ongoing crop이 action budget을 점유한다.
- self-clamp가 BUY_SEED 또는 HIRE를 계속 잘라 allocation change가 실제 생산으로 이어지지 않는다.
- 특정 공개 봇에서만 평균 bank가 오르고 다른 상대에 non-inferiority가 깨진다.
