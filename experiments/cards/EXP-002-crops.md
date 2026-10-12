# EXP-002 — v2 crop transition

hypothesis_id: HYP-0002
test_id: TEST-0002

상태: **사전등록** (실행 전 작성, 2026-09-08)

## 공통

- parent: KAGRI-012 v1 (`main.py` SHA-256 `d6cdb83ffdb27d2614330b20d438a6a20e82c7f4a72ead5ca8be897859de0b59`)
- parent policy: land day `(6,10)`, hands `9`, carrots `15`; crop pilot hook의 default는 season 밖(day 30)이라 v1 동작을 보존한다.
- engine: `kaggle-environments==1.32.7`, `kaggriculture.py` SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- runner: `tools/arena.py` SHA-256 `b3138a7279edde375c0bd66eb17d780d2b9c25eab20d894a41223d36b138f7d1`; `tools/instrument.py` SHA-256 `67c7014d620c9a99145348432553e77ddc5757b616ba1ade4f90ea9e218f53f8`
- hypothesis `[HYPOTHESIS]` H17: v1의 75칸 WHEAT/CARROT 구성을 MELON/STRAWBERRY 중심으로 바꾸면 새 action type 없이 공개 상위 봇 4종 상대 paired score가 개선된다.
- postmortem basis: `evidence/POSTMORTEM_4bots.md:46-62`에서 4개 봇 전원이 팔고 v1은 0인 순수 작물이 STRAWBERRY/MELON임을 확인했다. `:68-89`의 `[ENGINE]` 수치와 `[INFERENCE]` 자본 ramp가 전환 schedule의 근거다. `:91-100`이 NE h1/h17 비교 근거다.
- forbidden: SE purchase, animal/fertilizer action, market price hardcode, 결과 확인 후 seed/기준 변경, Kaggle submission.
- pilot: reused holdout `1000..1019`, 각 비교는 same seed × both seats = 40 games.
- stage D: reused holdout `1000..1049`, 공개 봇별 same seed × both seats = 100 games, 총 400 games.
- primary metric: seed-level paired score와 95% CI. diagnostics: W/D/L, loss count, loss-margin variance, mean/median margin, error, exact SHA, silent-failure counters, daily min cash, realized SELL price.

## 공통 hard gate

각 variant는 비교 전에 같은 20 seeds에서 self-play instrument gate를 실행한다. 양 player 모두 `noop_actions`, `blocked_moves`, `shed_discarded`, `orders_truncated`, `sell_unfilled`, `buy_failed`, `exceptions`가 0이고 daily min cash가 0 이상이어야 한다. 하나라도 위반하면 해당 variant는 즉시 FAIL이며 결과 선택에 쓰지 않는다.

추가 제약:

- 같은 turn의 crop별 PLANT 수는 관측 seed 수 이하.
- 마지막 action step 718의 market order는 SELL만 허용.
- MELON/STRAWBERRY 판단에서 market price를 상수로 쓰지 않는다.
- 예외 시 hands 수에 맞춘 PASS fallback을 반환한다.

## 고정 pilot 순서

각 stage는 앞 stage 선택값을 고정하고 정확히 한 factor만 바꾼다.

1. **stage A — MELON count**, switch day 4, STRAWBERRY 0, NE unlock 관측 h1:
   - A1 MELON 15 / A2 MELON 30 / A3 MELON 45; 나머지는 WHEAT.
2. **stage B-day — switch day**, stage A MELON count와 STRAWBERRY 0 고정, NE unlock 관측 h1:
   - B1 day 2 / B2 day 4 / B3 day 8.
3. **stage B-hour — NE purchase hour**, stage A+B-day 선택값 고정:
   - BH1 주문 h0 → unlock 관측 h1 / BH17 주문 h16 → unlock 관측 h17. SW는 주문 h0 고정.
4. **stage C — STRAWBERRY count**, stage A+B 선택값과 MELON count 고정:
   - C1 STRAWBERRY 0 / C2 STRAWBERRY 15 / C3 STRAWBERRY 30. STRAWBERRY는 남은 WHEAT를 대체하므로 MELON count는 변하지 않는다.
5. **stage D — promotion evaluation**:
   - stage C winner와 v1 parent를 각각 `opponents/public/` 4개 봇에 50 seeds × both seats로 평가한다.
   - stage C winner vs v1 직접 대결도 같은 50 seeds로 실행하되 진단으로만 기록한다.

## pilot 선택 규칙

stage 내 paired score 합이 가장 큰 clean variant를 선택한다. 합이 같으면 (1) head-to-head, (2) loss count가 적은 쪽, (3) loss-margin variance가 작은 쪽, (4) mean margin, (5) 비용이 낮은 쪽 순서다. 비용 tie-break는 MELON/STRAWBERRY 수가 적은 쪽, switch/land가 늦은 쪽이다. 여전히 같으면 `UNCERTAIN`으로 멈춘다.

`big_losses_gt_10k`는 backward-compatible diagnostic으로만 남기며 `AGENTS.md §7.2`에 따라 선택 근거로 쓰지 않는다.

## stage D 판정

- **SUCCESS**: hard gate CLEAN, 4-bot 합산 seed-level 95% CI 하한 > 0.5, 그리고 4종 중 3종 이상에서 개별 CI 하한 > 0.5.
- **FAILURE**: hard gate 위반 또는 4-bot 합산 CI 상한 < 0.5.
- **UNCERTAIN**: CLEAN이지만 CI가 0.5를 포함하거나 개별 3/4 조건을 충족하지 못함.
- 어떤 판정에서도 v2c vs v1 직접 대결은 promotion 근거가 아니다. `[LOCAL]` 결과는 `[HOSTED]` 우위를 증명하지 않는다.
- SUCCESS next: exact winner SHA와 registry를 기록하고 독립 검증 요청. 제출하지 않는다.
- FAILURE next: v1 유지, 실패를 이 crop schedule 구현 범위로 한정한다.
- UNCERTAIN next: 같은 seed에 재튜닝하지 않고 새 hypothesis/card를 제안한다.

## 공개 상대 동결

- `opponents/public/boatlee.py`: `f029fa0cb66a9eb509afbe44e3f59b800332d0419db91607183410e4089c4d19`
- `opponents/public/kaitofukami.py`: `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`
- `opponents/public/raykkretzschmar.py`: `489f5d197527f107027626cce79d850fd2ca90edd43d94384b849b6511e27bdb`
- `opponents/public/lynnsakurai.py`: `1dc166ae2bf0c56a44fac4482f469b8812968c4cb32459cb9860f5077897a7d4`

## Expected failure plane

초기 premium seed 구매가 land/crew budget을 잠식; late switch로 수확 주기 부족; ongoing STRAWBERRY가 action budget을 점유; shed overflow; seed 구매 실패; last-step order truncation; 특정 공개 봇에만 강한 overfit.
