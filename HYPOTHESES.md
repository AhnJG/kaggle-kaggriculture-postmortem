# HYPOTHESIS LEDGER — 공용 가설 원장

schema_version: 1

상태: **CANONICAL TOOL-MANAGED VIEW — 직접 편집 금지**

이 파일은 우리 실험과 공개 자료의 주장을 한곳에서 찾기 위한 색인이다. `쉬운 설명`은 비전공자가 읽는 한 줄이고, 상세 수치와 원자료는 `출처`와 `실험` 경로를 따른다. 공개 notebook이나 discussion의 자기보고는 여러 사람이 반복해도 `SOURCE_CLAIM`에서 자동 승격되지 않는다.

상태는 `SOURCE_CLAIM`, `PLANNED`, `ENGINE_CONFIRMED`, `LOCAL_SUPPORTED`, `LOCAL_FAILED`, `HOSTED_SUPPORTED`, `HOSTED_FAILED`, `INCONCLUSIVE`, `PENDING_HOSTED`, `RETRACTED`만 쓴다.

기존 ID 매핑: H1→HYP-0004, H2/H18→HYP-0003·HYP-0016, H3→HYP-0017, H4/H9→HYP-0016, H5→HYP-0008, H6→HYP-0023, H7→HYP-0024, H8→HYP-0020, H10→HYP-0025, H11→HYP-0026, H12→HYP-0021, H13→HYP-0015, H14→HYP-0001, H15/H20→HYP-0004, H16/H17→HYP-0002, H19-a/b→HYP-0022.

모든 `experiments/cards/EXP-*.md` 상단에는 `hypothesis_id: HYP-####`와 고유한 `test_id: TEST-####`를 넣는다. 같은 주장을 독립 검증할 때는 같은 HYP-ID와 별도 TEST-ID를 쓴다. 결과가 생기면 `tools/update_hypotheses.py`로 agent별 immutable event를 기록하면서 `로컬 결과`와 `상태`를 함께 바꾸고, 제출 결과를 인용할 때는 `Hosted 결과`에 8자리 submission ID를 적는다. agent는 이 파일을 직접 편집하지 않는다. 다음 명령이 통과해야 새 card·result·hosted 기록이 완료된 것으로 본다.

```bash
python3 tools/validate_hypotheses.py --strict
```

## HYP-0001
- 쉬운 설명: 땅과 일꾼을 늘리면 놀고 있던 시간을 생산에 쓸 수 있는지 확인한다.
- 주장: NW 25칸에서 NE와 SW로 확장하고 일꾼을 늘리면 v0보다 강해진다.
- 출처 수준: HYPOTHESIS,LOCAL
- 출처: experiments/cards/EXP-001-land.md; coordination/reports/codex/20260908-1656-KAGRI-012.md
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-001-land.md
- 로컬 결과: hands=9와 carrots=15를 선택했고 correctness gate PASS; hosted 우위는 미검증
- Hosted 결과: N/A
- 상태: LOCAL_SUPPORTED
- 유효 범위: EXP-001 고정 seed와 v0 계열의 로컬 비교에 한정
- 다음 행동: 다른 전략 계열의 hosted 우위 근거로 사용하지 않음

## HYP-0002
- 쉬운 설명: 밀과 당근 대신 멜론과 딸기를 늘리면 강한 상대에게도 나아지는지 확인한다.
- 주장: v1의 작물 구성을 MELON과 STRAWBERRY 중심으로 바꾸면 공개 상위 봇 상대 W/D/L이 개선된다.
- 출처 수준: HYPOTHESIS,LOCAL
- 출처: experiments/cards/EXP-002-crops.md; coordination/reports/codex/20260909-0156-KAGRI-015.md
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-002-crops.md
- 로컬 결과: parent 직접 대결 100-0이나 공개 4봇 상대 candidate와 parent 모두 0-400
- Hosted 결과: N/A
- 상태: LOCAL_FAILED
- 유효 범위: 시험한 crop schedule 구현만 실패; 넓은 작물 가설 전체의 실패가 아님
- 다음 행동: 같은 seed 재튜닝 금지; 새 구현은 새 HYP-ID 사용

## HYP-0003
- 쉬운 설명: 시장이 받아 줄 수 있는 양만 생산하고 나눠 팔면 손실이 줄어드는지 확인한다.
- 주장: MELON 과잉을 줄이고 판매를 실제 흡수량에 맞추면 final bank와 W/D/L이 개선된다.
- 출처 수준: ENGINE,HYPOTHESIS,LOCAL
- 출처: evidence/ABSORPTION.md; experiments/cards/EXP-003-absorption.md; coordination/reports/codex/20260909-1951-KAGRI-016.md
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-003-absorption.md
- 로컬 결과: MELON 30→3 correction의 기존 실패/CI 불확정은 유지. 20260923 EXP017 vs OMW seed2142 seat0: MELON 흡수30/판매72(+42), FERTILIZER 흡수0/판매332. 소비 tick 뒤 분산+최종 flush는 같은 수량 가격 계산에서 9품목 모두 상대 대비 순수입 악화. WOOL 우리 순수입 -7858, FERTILIZER -6229. 기존 full-engine 결과는 자금/shed 연쇄로 동일 수량을 보존하지 못해 별도 feasibility 진단으로만 기록. 검산6501 PASS; report coordination/reports/codex/20260923-ABSORPTION.md; manifest analysis/absorption_20260923/manifest.json.
- Hosted 결과: N/A
- 상태: INCONCLUSIVE
- 유효 범위: 기존 EXP003 correction 판정 보존. 추가 결론은 engine1.32.7 EXP017/OMW seed2142 seat0 실제 체결 및 특정 소비 pacing 규칙에 한정; 일반 timing 최적화나 생산 구성 전체 판정 아님.
- 다음 행동: 소비 cap runtime 후보 비추천. 판매 slot 대안은 HYP-0016 / TEST-ABSORPTION-WOOL-ORDER-20260923 초안으로 분리. Claude 보고 검토 및 BOARD/FACTS owner 인수. 생산 구성 권고·새 arena·제출·다운로드 없음.

## HYP-0004
- 쉬운 설명: 소와 양을 키우면 놀고 있는 일꾼과 비어 있는 수익원을 활용할 수 있는지 확인한다.
- 주장: PASTURE 기반 소·양과 비료 순환을 추가하면 유휴 action이 줄고 승률이 개선된다.
- 출처 수준: ENGINE,COMMUNITY,HYPOTHESIS
- 출처: evidence/ENGINE_ANIMALS.md; experiments/cards/EXP-004-animals.md
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-004-animals.md
- 로컬 결과: N/A
- Hosted 결과: N/A
- 상태: PLANNED
- 유효 범위: 선행 계측 gate가 구현된 뒤에만 실험 가능
- 다음 행동: 현재 tape 계열 baseline의 독립 요인으로만 시험

## HYP-0005
- 쉬운 설명: 로컬 tape 상대 점수가 실제 leaderboard 점수를 예측하는지 확인한다.
- 주장: 같은 artifact 가족의 로컬 tape-pool 점수 차이는 hosted rating 차이의 방향과 크기를 예측한다.
- 출처 수준: HYPOTHESIS,LOCAL
- 출처: experiments/cards/EXP-005-x1-probe.md; evidence/raw/EXP-005/verdict.json
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-005-x1-probe.md
- 로컬 결과: X1은 pool delta -0.1915였지만 discard와 종료 가축 gate 위반으로 제출 전 FAILURE
- Hosted 결과: N/A
- 상태: LOCAL_FAILED
- 유효 범위: hosted 예측 자체는 제출하지 않아 검증되지 않음
- 다음 행동: 안전 gate를 통과하는 한 요인 candidate에서 다시 사전등록

## HYP-0006
- 쉬운 설명: 나와 거의 같은 상대보다 한 턴 먼저 팔면 아주 근소한 승리를 만들 수 있는지 확인한다.
- 주장: clone 서명 거리 6 이하 상대의 다음 판매를 제한적으로 선점하면 clone 대결을 이기고 non-clone 승패는 보존한다.
- 출처 수준: COMMUNITY,HYPOTHESIS,LOCAL,HOSTED
- 출처: experiments/cards/EXP-006-clone-preempt.md; evidence/raw/EXP-006/verdict.json; evidence/HOSTED_LEDGER.md; experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json; coordination/reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md; experiments/results/p1_release_preflight/report.md; coordination/reports/codex/20260916-1919-P1B-ACTUAL-TAR-PREFLIGHT.md; coordination/reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md sha256 fc02423f9a4fbf66f23be56c3f454d051fa0c1e927100542be40c5ff8cb47ad5
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-006-clone-preempt.md; experiments/mirror_edge2_20260926/preregistration.json; TEST-EXP022-H2P-20260926
- 로컬 결과: parent 20-0-0; 공개봇 40-0-0; pool 승패 악화 0; hosted loss 108076177 frozen transcript를 양 좌석 exact reward로 재현, preempt 0회. P1b actual tar schema-3 preflight는 승인된 13/13 episode를 720-step DONE/DONE으로 완료했으나 gated parent 16/16 zero gate FAIL; Identity/Runtime/Isolation/License PASS, Schema FAIL; counter 합 noop_actions=3488, shed_discarded=482(16/16 nonzero), buy_failed=74, hire_failed=18, seed_blocked_plant=56, hands_length_mismatch=92, shed_unsold=0, orders_truncated=0, exceptions=0; sell_unfilled=1541806은 diagnostic. 독립 결과 검증 VERIFIED_LOCAL_FAILURE (Antigravity 2026-09-16, manifest sha256 46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c, 파일 불일치 0·계측 오류 0). EXP-022 H2-prime: unit 3/3 PASS; smoke seed6190 8/8 valid, errors0. O 양 좌석 expected cash -25 vs actual -28, frozen tolerance2 초과로 our_mirror 0/2; nonclone 6/6 our_mirror0. STOP before screen; hypothesis effect N/A. Engine diagnostic: per-unit lockstep makes unmatched fifth BUY_PRODUCT marginal quote28, not displayed q0=25. coordination/reports/codex/20260926-0133-EXP022-H2P.md
- Hosted 결과: submission 56165718 COMPLETE publicScore 1862.6 (2026-09-15 KST 직접 CLI, 완료시각 상한 01:13:12 KST); 공개 active UI와 대조. 이전 09-12 snapshot 1915.6 및 50판 41/0/9는 과거 window이며 새 episode 비교는 N/A. 출처 coordination/reports/codex/20260915-0115-KAGGLE-SNAPSHOT.md
- 상태: INCONCLUSIVE
- 유효 범위: artifact 1c478c24…9721과 submission 56165718의 관측에 한정; parent 56147691 은퇴로 clone-preempt causal effect는 판정 불가
- 다음 행동: EXP-022는 frozen smoke FAIL로 종료한다. candidate mirror 규칙 변경은 새 experiment ID, 새 preregistration, 사람 승인 없이는 실행하지 않는다. screen, release, E-5, D3 gate v2, submission은 N/A이며 현재 슬롯을 유지한다.

## HYP-0007
- 쉬운 설명: 서로 다른 두 tape를 함께 쓰면 한쪽이 지는 상대를 다른 쪽이 막아 줄 수 있는지 확인한다.
- 주장: thomas router는 exp006의 패배 셀 일부를 이겨 두 활성 슬롯의 실패가 덜 겹친다.
- 출처 수준: COMMUNITY,HYPOTHESIS,LOCAL,HOSTED
- 출처: experiments/cards/EXP-007-thomas-router.md; releases/public-thomas-replay-router-v2-exact/manifest.json; evidence/HOSTED_LEDGER.md; experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-007-thomas-router.md
- 로컬 결과: pool 0.9433; exp006 비승리 6셀 중 4셀 승; 사전 gate SUCCESS이나 독립 Reviewer는 제출 반대
- Hosted 결과: submission 56175620 COMPLETE publicScore 1635.9 (2026-09-15 KST 직접 CLI, 완료시각 상한 01:13:12 KST); 공개 active UI와 대조. 이전 09-12 snapshot 1819.8과 50판 21/9/20은 과거 window. 새 W/D/L 및 failure correlation N/A. 출처 coordination/reports/codex/20260915-0115-KAGGLE-SNAPSHOT.md
- 상태: INCONCLUSIVE
- 유효 범위: artifact 8031d51a…0180과 submission 56175620의 관측에 한정; 전체 상대 교집합도 3명이라 낮은 failure correlation의 증거가 아님
- 다음 행동: plan/CURRENT.md P1에서 새 고정 window를 수집. 보완성은 동일 opponent artifact/seed/seat에 대한 별도 사전등록 후 판단. 단일 신규 제출은 EXP-006을 먼저 은퇴시키므로 교체 전 FIFO pair 표와 사람 승인 필요.

## HYP-0008
- 쉬운 설명: 처음부터 규칙을 짜는 것보다 강한 720턴 계획을 재생하고 조금 고치는 편이 강한지 확인한다.
- 주장: tape replay와 얇은 guard 계열은 현재 우리 규칙형 executor보다 강하다.
- 출처 수준: COMMUNITY,LOCAL,HOSTED
- 출처: plan/kaggriculture_master_plan_claude-opus-5.md; releases/public-yhay81-shop-router-0909-exact/manifest.json; evidence/HOSTED_LEDGER.md
- 엔진: 1.32.7
- 실험: releases/v1-20260910/manifest.json; releases/public-yhay81-shop-router-0909-exact/manifest.json
- 로컬 결과: yhay81-exact tape pool 452-0-18; 우리 v1은 공개 4봇 0-400
- Hosted 결과: 같은 기록 시점 submission 56147691 2188.4 대 submission 56145245 343.9
- 상태: HOSTED_SUPPORTED
- 유효 범위: exact 두 artifact와 관측 창의 비교; 모든 runtime rule agent가 약하다는 뜻은 아님
- 다음 행동: 규칙은 safety와 좁은 반응 layer로 유지

## HYP-0009
- 쉬운 설명: 순수 RL은 게임이 너무 길고 복잡해 현재 자원으로 안정적으로 배우기 어렵다는 주장이다.
- 주장: end-to-end PPO는 719회 결정과 희소 보상 때문에 deterministic 또는 hybrid agent보다 학습이 어렵다.
- 출처 수준: COMMUNITY
- 출처: docs/discussion/738619_Learnings_from_PPO_to_80k_terminal_cash.md; https://www.kaggle.com/competitions/kaggriculture/discussion/734952
- 엔진: N/A
- 실험: N/A
- 로컬 결과: N/A
- Hosted 결과: N/A
- 상태: SOURCE_CLAIM
- 유효 범위: 참가자 자기보고; compute와 reward 설계가 다른 경우 일반화 금지
- 다음 행동: pure PPO를 당장 우선순위로 올리지 않음

## HYP-0010
- 쉬운 설명: 최신 강자 행동을 복제하면 leaderboard 중상위까지 빠르게 갈 수 있다는 주장이다.
- 주장: 최근 강한 공개 replay를 재생하면 top 10% 수준까지 도달할 수 있다.
- 출처 수준: COMMUNITY
- 출처: docs/discussion/740437_Your_opponents_are_probably_replaying_the_same_tapes_you_are_I_measured_it.md; https://www.kaggle.com/competitions/kaggriculture/discussion/739273
- 엔진: N/A
- 실험: N/A
- 로컬 결과: N/A
- Hosted 결과: N/A
- 상태: SOURCE_CLAIM
- 유효 범위: 저자 자기보고이며 donor artifact·기간·초기 매칭 운에 의존
- 다음 행동: 기존 5 unique episode의 descriptive/reproduction 증거는 유지한다. 2026-09-18 최소 다음 비교 proposal: coordination/proposals/codex/20260918-DONOR-MINIMUM-TRANSFER-CHECK.md. Majkel 109675071 seat0 단일 전체 tape와 parent를 Remielle frozen transcript/seed1125321547/양seat에서 비교하는 4셀 수치 초안이며 설계 BLOCKED: K3 전체 market 복사 적용, 재검토 조건은 —, 이를 충족하는 ENGINE/HOSTED 근거와 실행 artifact N/A. 원본 재현이나 donor 본인 승리로 K3를 해제하지 않는다. 별도 독립 평가 표본 미선정, P2 HOLD/release FAIL 유지. HIRE recovery·광범위 NOOP 진단·새 경기로 자동 전환하지 않는다. 기존 TEST-DONOR-ROUTES-20260917은 검토 context만 재사용하며 새 시험을 등록하지 않았다. 2026-09-18 Claude K3 범위 검토 proposal: coordination/proposals/claude/20260918-K3-SCOPE-REVIEW.md — K3 원출처(rayk cell48)는 market-only graft 정성 실패이며 전체 agent 복사 범위는 원문 N/A. 추천안(범위 한정+ENGINE/HOSTED 조건)은 사람 결정·독립 검토 전이므로 현행 K3 적용 유지, 해제 아님. 주의: rayk cell28 'Copying the whole irregular route did not transfer'(COMMUNITY, 수치 N/A). 2026-09-18 Claude(Coordinator) 최종 결정안: coordination/proposals/claude/20260918-K3-DONOR-FINAL-DECISION.md — K3 범위 정정만 승인 요청(market 기록을 다른 작업 경로에 graft하는 것으로 한정, 원출처 COMMUNITY 정성, 구현·엔진·표본·기제 N/A, 재검토 조건 미정의·§9 예외는 사람 결정). 같은 episode 전체 donor 재생은 K3 밖이나 허용 아님. Majkel 4셀 진단은 보류(결과가 현재 결정을 바꾸지 않음, 고정 tape·seed1·좌석 거울대칭으로 정보량 제한, P2 HOLD). 사람 승인·Antigravity 독립 검토 전이므로 현행 K3 문구 적용 유지. 주의(COMMUNITY): rayk cell53 field layer/isolated market tape 복사 not coherent, cell49 rival action reconstruction은 원 policy 분기를 다 드러내지 않을 수 있음; 반대 방향 cell8/13 exact full tape 채택 보고. HOSTED 성공 1건 조건은 기존 계약 아님.

## HYP-0011
- 쉬운 설명: 아무것도 바꾸지 않아도 다른 참가자가 강해지면 내 점수는 내려갈 수 있다.
- 주장: 고정 submission은 field와 meta가 강해지면서 rating과 순위가 하락한다.
- 출처 수준: COMMUNITY,HOSTED
- 출처: evidence/HOSTED_LEDGER.md; docs/discussion/740282_how_much_time_does_it_take_for_submission_to_converge.md
- 엔진: 1.32.7
- 실험: evidence/HOSTED_LEDGER.md
- 로컬 결과: N/A
- Hosted 결과: submission 56068891 동일 artifact가 2026-09-07~09 사이 337.2→330.6, 순위 264계단 하락
- 상태: HOSTED_SUPPORTED
- 유효 범위: 해당 2일 관측; 장기 선형 하락률로 외삽 금지
- 다음 행동: 최신 field 판독과 제출 age를 함께 기록

## HYP-0012
- 쉬운 설명: 내 주변의 로컬 상대를 이겨도 실제 leaderboard에서 강하다는 뜻은 아닐 수 있다.
- 주장: self-play와 좁은 공개봇 pool의 승률은 hosted strength를 안정적으로 대변하지 못한다.
- 출처 수준: COMMUNITY,LOCAL
- 출처: coordination/reports/codex/20260909-0156-KAGRI-015.md; docs/discussion/740847_My_Journey_So_Far__Mechanics_Breakdowns_and_Whats_Actually_Working.md; coordination/reports/codex/20260915-independent-review.md; coordination/reports/codex/20260916-VET-APPLY.md
- 엔진: 1.32.7
- 실험: coordination/proposals/claude/20260925-SEARCH-LOOP-CODEX.md; experiments/search_20260925/calibration-policy.json; TEST-SEARCH-20260925-CALIBRATION; coordination/reports/codex/20260929-1120-CALIB.md; TEST-CALIB-20260929
- 로컬 결과: candidate가 parent를 100-0으로 이겼지만 candidate와 parent 모두 공개 4봇에 0-400
- Hosted 결과: [HOSTED] 2026-09-29 02:13 UTC c26 119경기 90/3/26, d157 228경기 105/10/113; 두 제출의 공통 상대 submission ID 0. 같은 시각·상대의 hosted A/B가 없어 local 순위 보정 결과 UNSURE (experiments/calib/calibration.json, analysis/hosted_20260929b/episodes_all.json).
- 상태: LOCAL_SUPPORTED
- 유효 범위: 좁거나 포화된 상대 pool에 대한 경고; 모든 local 평가가 무의미하다는 뜻은 아님
- 다음 행동: CALIB 17h 판독에서 local 단독 d157 대체 기준 N/A; fresh 시간 분리 상대 submission 패널을 사전등록하고 후보를 d157/c26 모두와 비교하되 hosted 우위라 주장하지 말 것.

## HYP-0013
- 쉬운 설명: replay에서 행동을 한 칸 잘못 읽으면 전혀 다른 전략처럼 보일 수 있다.
- 주장: 초기화 step 때문에 action 추출은 실제 실행 시점과 한 칸 어긋날 수 있으며 자기 replay 100% 일치로 검증해야 한다.
- 출처 수준: COMMUNITY,ENGINE
- 출처: docs/discussion/740437_Your_opponents_are_probably_replaying_the_same_tapes_you_are_I_measured_it.md; kaggle-environments 1.32.7 replay schema
- 엔진: 1.32.7
- 실험: 자기 agent action과 자기 replay action의 100% parity fixture
- 로컬 결과: 2026-09-16 22:26 KST snapshot top 10·20 submission metadata 확보. 상위 2 donor 6 views=5 unique episode를 원래 seed/config/양측 action으로 재현: action 7190/7190, state projection 7200/7200, final rewards exact match 5/5 PASS. 기존 replay 106263397도 PASS. 개발 자료의 재현이며 unseen 상대 성능은 N/A. 근거 experiments/results/top10_donor_20260916/summary.json 및 donor_manifest.json; runner tools/reproduce_replay.py.
- Hosted 결과: N/A
- 상태: ENGINE_CONFIRMED
- 유효 범위: kaggle-environments 1.32.7 replay 형식
- 다음 행동: 이번 5경기는 development/reproduction으로 고정한다. donor별 route 차이와 state dependency를 분석하되 별도 opponent/seed 평가와 혼동하지 않는다. extraction negative tests와 engine lock을 유지한다.

## HYP-0014
- 쉬운 설명: 설명서보다 실제 게임 코드가 다를 수 있으므로 중요한 숫자는 코드로 다시 확인해야 한다.
- 주장: README의 수요·수명·가격 설명 일부는 shipped engine 동작과 다르다.
- 출처 수준: ENGINE,COMMUNITY
- 출처: docs/discussion/740087_Two_places_where_the_README_is_lossy_about_the_engine_yield_units_max_lifespan_step.md; evidence/FACTS.md; coordination/reports/codex/20260915-independent-review.md; coordination/reports/codex/20260916-VET-APPLY.md
- 엔진: 1.32.7
- 실험: scripts/verify_engine_facts.py
- 로컬 결과: 상점 해금·가격 갱신·수명 관련 source line과 재현 검증 기록 존재
- Hosted 결과: N/A
- 상태: ENGINE_CONFIRMED
- 유효 범위: 규칙은 OFFICIAL, 게임 동작은 고정 engine source가 우선
- 다음 행동: engine version 변경 시 재검증. 2026-09-16 R10 yield_units>0를 수확 가능으로 읽은 오류를 원래 제안·docs/code 정정문·현재 plan에 바로잡음(고정 1.32.7 MELON 초기 yield_units=1, first_yield_day=10). 과거 README 가설 상태 유지. coordination/reports/codex/20260916-VET-APPLY.md

## HYP-0015
- 쉬운 설명: 씨앗보다 많이 심으라고 하면 일부가 아니라 그 작물의 파종 전체가 취소된다.
- 주장: seed 부족 PLANT는 그 턴 해당 crop의 PLANT 전체를 PASS로 바꾼다.
- 출처 수준: ENGINE
- 출처: evidence/FACTS.md; kaggriculture.py:920-928
- 엔진: 1.32.7
- 실험: engine source와 부족 seed fixture
- 로컬 결과: engine branch 확인; 기존 일반 noop counter에 잡히지 않음
- Hosted 결과: N/A
- 상태: ENGINE_CONFIRMED
- 유효 범위: engine 1.32.7
- 다음 행동: 전용 counter와 seed guard 유지

## HYP-0016
- 쉬운 설명: 같은 물건도 언제 어떤 순서로 파느냐에 따라 실제로 받는 돈이 달라진다.
- 주장: 날짜 분산·시장 slot 순서·한 턴 선행이 유효한 판매 lever이고 WHEAT/FERTILIZER 선행은 불리할 수 있다.
- 출처 수준: ENGINE,COMMUNITY,HYPOTHESIS,LOCAL
- 출처: evidence/MARKET_EXECUTION.md; experiments/cards/EXP-003-absorption.md; experiments/cards/EXP-006-clone-preempt.md; coordination/reports/codex/20260915-independent-review.md; coordination/reports/codex/20260916-VET-APPLY.md; coordination/reports/codex/20260925-1340-DP-LOSS-CAUSE.md; experiments/results/dp_loss_cause_20260925/verification.json; analysis/exp018_panel/summary.json
- 엔진: 1.32.7
- 실험: EXP-003 stage B; experiments/cards/EXP-006-clone-preempt.md; experiments/cards/EXP-018-dp0924-single-factor.md (20260925 authorized Q2 then conditional Q4)
- 로컬 결과: 기존 clone 대상 제한 선행 20-0-0, 전체 sale rewrite EXP005 FAILURE는 유지. 20260923 baseline 진단: EXP017 seed2014/V53 양seat cash66185 대65595; seed2142/OMW seat0 cash104150 대104360. 후자는 모든 품목 판매 수량 동일, STRAWBERRY 수입차 -674. 고정 수확/소비/구매/town 조건부 상한244257, WHEAT/FERT 순수입 고정시210680; 달성 가능 cash·BT 효과 N/A. 2271 checks PASS. report coordination/reports/codex/20260923-FUNDAMENTAL-GAIN.md; raw analysis/fundamental_gain_20260923/manifest.json. 20260925 EXP018 DP0924 _V92_P_EVERY 3->2 (candidate f3e727b1...505052): Q2 fixed8 losses ->3 wins. Eligible FULL panel47 parent23/0/24 ->candidate28/0/19, delta0.10638298 SE0.04546036, new_losses0. Mandatory DP seeds2400..2439 both seats80:22W/34D/24L=0.4875<0.50. VERIFIED_NOT_ELIGIBLE_DP_FLOOR; panel-only SUCCESS is not final SUCCESS/B2. 47 parent action67586/state67680 exact; maxstep0.127132s, exceptions0. Card f2eaac36...c58686 unchanged; verifier2039 checks PASS. Report coordination/reports/codex/20260925-1340-DP-LOSS-CAUSE.md.
- Hosted 결과: PENDING
- 상태: INCONCLUSIVE
- 유효 범위: 좁은 clone-preempt와 전체 sale rewrite를 같은 효과로 해석 금지
- 다음 행동: 이전 STRAWBERRY 1turn 진단 초안은 미실행 상태로 보존. 추가 EXP018 WOOL_FIRST 0→1 SELL-prefix 순서 초안: seed2142 가격-only 순수입+83/margin+83으로 여전히 패배, FERTILIZER priority는 -382로 제외. report coordination/reports/codex/20260923-ABSORPTION.md. seeds2180..2219/양좌석/OMW·EXP016·V53·v13, parent/candidate패널640+직접80=720 한 arena. DRAFT_BLOCKED_PREFLIGHT: 같은 rating구간 EXP016/017 hosted weights manifest·candidate/runner SHA·runtime/isolation 미확정. E2 G>2SE, UNKNOWN>40% 판단금지, C1 가중치 대체금지. Claude 판정·Antigravity 실행, 이번에는 미실행. 20260925 DP-specific test: append _V92_P_EVERY 3->2 only, Q2 fixed 8 herd losses then conditional 47 eligible hosted panel + DP seeds2400..2439 both seats score>=0.50. No new sale layer, no K2 reopening; prior WOOL_FIRST draft stays unexecuted. Card and runner freeze before tests. RESULT: this exact refresh candidate is NOT ELIGIBLE (DP floor failed); no release/submission. Do not add seeds, relax floor, retune, or execute fallback to bypass the failed gate. Coordinator handoff only; broader timing hypothesis remains unsettled. Prior WOOL_FIRST EXP018 placeholder is historical draft, not this executed card.

## HYP-0017
- 쉬운 설명: 초반에 열린 상점 조합을 보고 준비된 720턴 계획 중 하나를 고르면 기본 경쟁력이 생긴다.
- 주장: shop-pair route 선택은 강한 baseline에 필요하지만 그 자체만으로 최상위 차별화는 아니다.
- 출처 수준: COMMUNITY,LOCAL,HOSTED
- 출처: releases/public-yhay81-shop-router-0909-exact/manifest.json; docs/code/yhay81_shop-router-0909.ipynb; evidence/HOSTED_LEDGER.md
- 엔진: 1.32.7
- 실험: releases/public-yhay81-shop-router-0909-exact/manifest.json
- 로컬 결과: 13개 route 로드·720 step 완주·tape pool 0.9617
- Hosted 결과: exact baseline submission 56147691 publicScore 2188.4 at recorded snapshot
- 상태: HOSTED_SUPPORTED
- 유효 범위: artifact 40d2bc39…d7791; 저자의 별도 live artifact와 동일하다는 증거는 아님
- 다음 행동: route 선택은 baseline으로 두고 새 alpha를 별도 HYP-ID로 시험

## HYP-0018
- 쉬운 설명: 안전하고 반복적인 일은 규칙이 맡고 큰 전략 선택만 모델이 맡는 혼합 방식이 현실적이라는 주장이다.
- 주장: deterministic executor와 좁은 learned policy의 hybrid가 pure rules 또는 pure RL보다 유리할 수 있다.
- 출처 수준: COMMUNITY
- 출처: https://www.kaggle.com/competitions/kaggriculture/discussion/738079; https://www.kaggle.com/competitions/kaggriculture/discussion/734952
- 엔진: N/A
- 실험: N/A
- 로컬 결과: N/A
- Hosted 결과: N/A
- 상태: SOURCE_CLAIM
- 유효 범위: 참가자 경험과 설계 제안; exact artifact 비교 없음
- 다음 행동: tape baseline 이후 market timing 한 변수에만 model 적용 검토

## HYP-0019
- 쉬운 설명: 남의 강한 행동 기록을 그대로 재생해도 원래 점수 대부분을 되찾을 수 있다는 주장이다.
- 주장: donor tape replay는 donor rating의 약 88%를 회수한다.
- 출처 수준: COMMUNITY
- 출처: docs/code/zhincez_replaying-someone-elses-tape-gets-you-88-percent.ipynb; evidence/FACTS.md
- 엔진: N/A
- 실험: N/A
- 로컬 결과: N/A
- Hosted 결과: N/A
- 상태: SOURCE_CLAIM
- 유효 범위: 자기보고 n=2; artifact·seed·engine 누락
- 다음 행동: 산출 경로 analysis/donor_tape_20260919/ + analysis/donor_tape_20260919/stage_bc/ 2026-09-19 F0 단계 B: 상위 1-60위 적격 52팀 최신 2경기 donor 행동 완전 일치 0/52(같은 turn 비율 중앙값 28.5%, 26팀이 turn 144-218 에서 분기). 단일 tape exact 재생 donor 없음 — 단계 C 종료, 다음 경로는 coordination/proposals/claude/20260919-F0-STAGE-B-RESULT-DECISION.md 사람 결정 대기. 상태·결과 칸은 88% 회수 주장 자체를 시험하지 않았으므로 불변.

## HYP-0020
- 쉬운 설명: 비료·동물 돌봄·마지막 판매는 조건을 정확히 맞춰야 헛수고를 피할 수 있다는 주장이다.
- 주장: 생산 직전 FERTILIZE, 급여한 날 CARE, day-28 이후 청산이 수익을 개선한다.
- 출처 수준: COMMUNITY
- 출처: docs/discussion/740847_My_Journey_So_Far__Mechanics_Breakdowns_and_Whats_Actually_Working.md
- 엔진: N/A
- 실험: N/A
- 로컬 결과: N/A
- Hosted 결과: N/A
- 상태: SOURCE_CLAIM
- 유효 범위: 저자 자기보고 +25% milk, +51% wool, 약 2.8k 회수; 우리 artifact 검증 없음
- 다음 행동: engine source로 조건 확인 후 각각 별도 한 요인 실험

## HYP-0021
- 쉬운 설명: 시장을 흔들면 상대 일꾼 행동까지 망가뜨릴 수 있다는 초기 생각은 측정 오류였다.
- 주장: 공유 시장 충격이 상대의 farm action budget을 직접 낭비시킨다.
- 출처 수준: LOCAL
- 출처: evidence/HYPOTHESES.md; evidence/KILLS.md
- 엔진: 1.32.7
- 실험: 계측기 귀속 버그 수정 후 starter 재측정
- 로컬 결과: 상대 noop 변화 0이고 BUY_SEED 가격은 고정이라 원 근거 무효
- Hosted 결과: N/A
- 상태: RETRACTED
- 유효 범위: 원 구현과 잘못된 계측 결과를 재사용 금지
- 다음 행동: 재제안 시 새 engine 또는 hosted 근거 필요

## HYP-0022
- 쉬운 설명: 일꾼이 노는 이유가 길 찾기나 돈 부족 때문이라는 두 설명은 모두 맞지 않았다.
- 주장: 높은 PASS 비율의 주원인은 routing 실패 또는 seed 구매 자금 부족이다.
- 출처 수준: HYPOTHESIS,LOCAL
- 출처: evidence/ACTION_BUDGET.md; evidence/PASS_DIAGNOSIS.md
- 엔진: 1.32.7
- 실험: evidence/PASS_DIAGNOSIS.md
- 로컬 결과: seed 부족 원인 1.3%; 담당 구역 routing 실패도 주원인이 아님
- Hosted 결과: N/A
- 상태: LOCAL_FAILED
- 유효 범위: 검사한 v1 계열 PASS 원인에 한정
- 다음 행동: 유휴 action을 실제 작업 생성량과 동물 layer에서 설명

## HYP-0023
- 쉬운 설명: 일꾼을 한꺼번에 너무 많이 고용하기보다 9~12명 수준으로 고르게 유지하는 편이 효율적인지 확인한다.
- 주장: hands 9~12 평탄화가 14명 spike보다 같은 경제 규모에서 유리하다.
- 출처 수준: COMMUNITY,HYPOTHESIS,LOCAL
- 출처: experiments/cards/EXP-001-land.md; coordination/reports/codex/20260908-1656-KAGRI-012.md
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-001-land.md
- 로컬 결과: EXP-001 round-robin에서 hands=9 선택; 독립 hosted 효과는 미검증
- Hosted 결과: N/A
- 상태: LOCAL_SUPPORTED
- 유효 범위: v1 규칙형 parent와 고정 seeds에 한정
- 다음 행동: tape 계획을 바꾸지 않는 한 요인으로만 재검증

## HYP-0024
- 쉬운 설명: 매일 셰드에서 다시 시작하므로 셰드 가까이에 중요한 시설을 두면 이동을 줄일 수 있다.
- 주장: shed 중심 동심원 배치가 원거리 배치보다 action budget을 절약한다.
- 출처 수준: ENGINE,HYPOTHESIS
- 출처: evidence/HYPOTHESES.md; plan/kaggriculture_master_plan_claude-opus-5.md
- 엔진: 1.32.7
- 실험: N/A
- 로컬 결과: N/A
- Hosted 결과: N/A
- 상태: PLANNED
- 유효 범위: 매일 unit respawn 동작이 유지되는 engine에 한정
- 다음 행동: 동일 생산 schedule의 배치만 바꾸는 A/B 필요

## HYP-0025
- 쉬운 설명: 밀을 직접 키우지 않고 사서 더 비싼 생산에 쓰는 편이 이득인지 확인한다.
- 주장: BUY_PRODUCT WHEAT의 현금 비용보다 premium tile의 기회가치가 커 순매수 전략이 성립한다.
- 출처 수준: ENGINE,HYPOTHESIS
- 출처: evidence/HYPOTHESES.md; evidence/FACTS.md
- 엔진: 1.32.7
- 실험: N/A
- 로컬 결과: N/A
- Hosted 결과: N/A
- 상태: PLANNED
- 유효 범위: 시장 재고·사료 수요·slot 경합을 함께 통제해야 함
- 다음 행동: 생산 tile 배분을 고정한 단일요인 실험

## HYP-0026
- 쉬운 설명: 다른 사람이 쉽게 읽지 못하는 시장 재고 신호로 route를 고르면 복제를 늦출 수 있는지 확인한다.
- 주장: market.inventory 기반 branch는 공개 fingerprint feature보다 판독 방어에 유리하다.
- 출처 수준: COMMUNITY,HYPOTHESIS
- 출처: evidence/HYPOTHESES.md; plan/kaggriculture_master_plan_claude-opus-5.md
- 엔진: 1.32.7
- 실험: N/A
- 로컬 결과: N/A
- Hosted 결과: N/A
- 상태: PLANNED
- 유효 범위: 공개 판독기 feature set이 바뀌면 가설도 무효화될 수 있음
- 다음 행동: 자기 submission x-ray에서 branch predictability 측정

## HYP-0027
- 쉬운 설명: tape의 판매 시점만 크게 바꾸면 나머지 720턴 계획까지 연쇄적으로 어긋날 수 있다.
- 주장: open-loop farm tape 위에서 market schedule만 광범위하게 바꾸면 cash·shed timing이 달라져 farm plan이 붕괴한다.
- 출처 수준: LOCAL
- 출처: evidence/FACTS.md; experiments/cards/EXP-005-x1-probe.md
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-005-x1-probe.md
- 로컬 결과: pool 0.9787→0.7872, candidate만 불리한 셀 54, discard 11032 대 1980
- Hosted 결과: N/A
- 상태: LOCAL_SUPPORTED
- 유효 범위: yhay81 open-loop tape와 X1 전체 매도 rewrite에 한정
- 다음 행동: 시장 수정은 좁고 되갚을 수 있는 변화만 사용

## HYP-0028
- 쉬운 설명: 사람이 만든 공개 code와 그 사람의 실제 제출 code는 같다고 가정하면 안 된다.
- 주장: 공개 notebook의 점수·제목은 우리가 재현한 exact artifact의 성능을 보증하지 않는다.
- 출처 수준: COMMUNITY,LOCAL
- 출처: releases/public-thomas-replay-router-v2-exact/manifest.json; releases/public-yhay81-shop-router-0909-exact/manifest.json
- 엔진: 1.32.7
- 실험: coordination/proposals/claude/20260925-SEARCH-LOOP-CODEX.md; TEST-SEARCH-20260925-EXACT; TEST-SEARCH-20260925-TOURNAMENT
- 로컬 결과: SEARCH v2.3 stage1: exact127ed3e6 CRLF preserved. DP80=66/0/14; panel47=42/0/5; fixed1000 runtime invalid0, max0.750587249873206s exceeds0.25s, maximum game-p990.04413941712118685s. 2094.187s sustained worker6; NOT_ELIGIBLE. coordination/reports/codex/20260925-1846-NEWMETA-EXACT.md. Earlier exact-source tests remain in immutable events.
- Hosted 결과: 우리 yhay81 exact submission 56147691만 2188.4로 연결; 저자 artifact identity는 N/A
- 상태: LOCAL_SUPPORTED
- 유효 범위: 공개 source claim과 exact uploaded artifact를 구분하는 운영 가설
- 다음 행동: Run1b all-source parent tournament; choose final parent only after calibration. No submission and no holdout accessed.

## HYP-0029
- 쉬운 설명: 실제 상대 대부분이 비슷한 tape를 쓰기 때문에 같은 계열끼리의 근소한 차이가 중요하다는 주장이다.
- 주장: leaderboard field의 큰 비율이 알려진 tape 계열이며 clone matchup이 rating 수렴을 좌우한다.
- 출처 수준: COMMUNITY
- 출처: docs/discussion/740437_Your_opponents_are_probably_replaying_the_same_tapes_you_are_I_measured_it.md; https://www.kaggle.com/competitions/kaggriculture/discussion/739273
- 엔진: N/A
- 실험: N/A
- 로컬 결과: N/A
- Hosted 결과: N/A
- 상태: SOURCE_CLAIM
- 유효 범위: 저자 26경기 중 25경기 match 및 다른 참가자 85% 추정; 전체 field census가 아님
- 다음 행동: 우리 submission 최근 episodes를 같은 fingerprint 방식으로 측정

## HYP-0030
- 쉬운 설명: 첫날 시장 거래에서 몇십 코인을 더 남기면 다음 날 일꾼을 고용하지 못해 농장 전체가 무너지는 일을 막을 수 있는지 확인한다.
- 주장: step 1 opening market schedule을 A에서 B로 바꾸면 WHEAT stock은 유지하면서 clone collision의 cash starvation과 day1 HIRE failure를 막는다.
- 출처 수준: ENGINE,HOSTED,HYPOTHESIS,LOCAL
- 출처: coordination/reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md; experiments/results/hosted_postmortem_108076177.json; coordination/proposals/codex/EXP-008-opening-liquidity.md; coordination/reports/codex/20260914-2025-EXP008-RESULT.md; evidence/raw/EXP-008/verdict.json sha256 9e8cabf4020607abf193ded71071807a8bc9165cba2a95c03180c8a291622d43
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-008-opening-liquidity.md (사전등록 2026-09-14 06:18 UTC, §C 정정 06:35 UTC, 중복 ID 제거 06:52 UTC, sha256 e0e93652991005514bb37f11cf9c69be6d07739594cfee4760ac8792ff30773a); 출처 제안 coordination/proposals/codex/EXP-008-opening-liquidity.md; 정정 coordination/proposals/codex/EXP-008-PREREG-TIMING-CORRECTION.md
- 로컬 결과: [LOCAL] FAILURE. card e0e93652...773a; candidate 930ed160...f079; parent baseline d4c7c9b1...14f0a recorded first. Target W/D/L 0/0/2 although both cells recovered step23 bank 26, step25 hands 3, step47 nonempty_tiles 25. Control 2/0/0; public 40/0/0; pool parent 276/0/6 -> candidate 274/0/8 with b=0 c=2. G4 had 72 regressions across 36 pool cells; G5 failed in 38 cells.
- Hosted 결과: N/A — episode 108076177은 가설 생성 근거이며 EXP-008 candidate 결과가 아님
- 상태: LOCAL_FAILED
- 유효 범위: step 1 opening schedule block 전체를 indivisible factor로 판정; order와 batch size의 개별 효과는 주장하지 않음
- 다음 행동: Registered next_if_failure 유지: exact B schedule 폐기, seeds 추가·cash-floor/order-only 분해 재해석 금지. plan/CURRENT.md의 최신 postmortem에서 새 근거를 찾는다. Claude는 coordination/proposals/codex/20260915-owner-record-sync.md에 따라 registry/결과 포인터만 반영.

## HYP-0031
- 쉬운 설명: 하루가 끝날 때 일꾼이 들고 있던 물건을 창고에 넣지 못하면 그대로 사라진다. 그 사라진 물건이 언제·누가·왜 생겼는지 먼저 정확히 세는 작업이다.
- 주장: P1b에서 관측된 parent A의 shed_discarded 482는 전부 engine의 _drop_inventories_to_shed(일일 종료 시 unit inventory -> shed 이월) 경로에서 shed 잔여 용량 부족으로 발생한 실제 자원 손실이며, 각 손실 단위는 day·unit·item·drop 직전 shed 점유량·해당 unit의 그날 마지막 action·shed 인접 여부로 유일하게 귀속할 수 있다.
- 출처 수준: ENGINE,LOCAL
- 출처: experiments/cards/EXP-011-shed-discard-attribution.md sha256 8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e (r2 as measured and pinned by freeze.json; current r4 8bb45236026aea64f942d796efccbb2e5492d6d0c90b6a911b676e87679b8b1b does not replace it; r3 52372d1411f79ba663312f26cae97c0cc19d3a42eb4e3e79e8f507e44c2e1b20; r1 daabcd0d1386b95559d3433bd410c8b06a09d37f6a1407a5427e2c8c2164ddf2); coordination/reports/codex/20260918-EXP011-AUTHORIZATION.md sha256 2c1820d204ffe94bc49e51aa9e77570ff14d7c93fed5f16784ba3c99b0ab5f18; coordination/reports/codex/20260918-EXP011-RESULT.md sha256 10f885923175559a535bc93f2300979e8d6188d32a85c45ba78c8d7d3d18f919; coordination/reports/antigravity/20260918-EXP011-REVIEW.md sha256 cb4f4c9e4b1171a0424b678eaef4d72d0d0993853d43d192c7ce0655ed689e1d; coordination/proposals/codex/20260918-EXP011-OWNER-CORRECTIONS.md sha256 bb86221cc7dfb5f5f251876a1f27cc1e6e8d9c11f1d68921c7f2a6612737148a; coordination/proposals/codex/20260918-EXP011-CLOSURE-PRIORITY.md sha256 b1ed06b777abc4841747a60b4328ad670638878f5bf87fc51e3f0649ca15d137; coordination/reports/claude/20260918-EXP011-REVIEW-ADJUDICATION.md sha256 ffe16ae31144574eec0797b3cf8c4d7310709eb6ebc2607c18acbb4f88e0539c; coordination/reports/claude/20260918-EXP011-CLOSURE-PRIORITY-ADJUDICATION.md sha256 3909891dcc4412c63b8802c5c9017545d5d8a35e2b695f4a7b09194b193d251c; coordination/proposals/claude/20260918-EXP011-verify-only-guard.md sha256 471af245c835d7621a5e62dc5c1c75871d756c80f0a9c7eb8cf2397f7fb0fb5f; experiments/results/p1_shed_attribution/aggregate.json sha256 22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba; experiments/results/p1_shed_attribution/allocation_audit.json sha256 66ed824393d41aaae507866f327f5f9ae8f8bfa7c46d7993b10e197e43011fa8; tools/instrument.py sha256 ca64256f941f2098cafc531fc422363c5757995f721b449369ce72877a33fe28 :46-49 _TILE_OPS, :299-307 _tile_sig and _inv_total, :537-541 noop rule; .venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py sha256 bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e :192-206 market_price, :344-355 DROP, :393-411 PLACE, :524-530 CARE, :843-856 _drop_inventories_to_shed, :866-878 _end_of_day, :915-931 atomic PLANT PASS substitution, :940-947 step order; evidence/FACTS.md F-T14 correction, F-T16 correction, F-T17 scope, F-T20, F-T21, F-T22; experiments/registry.csv EXP-011 row; freeze commit 0a4b10f; coordination/reports/codex/20260918-P1C-AUDIT-VERIFY-GUARD.md sha256 e75f45e39caaf9130a8946451593b53e31c51dde2941a3bf3cee0b6be1fc0f38; coordination/proposals/codex/20260918-P1C-GEMINI-CORRECTIONS.md sha256 599bfbe77937175e26113225dce21162e55398dc5e8c768e3423d7fbc1efee37; coordination/reports/claude/20260918-EXP011-VERIFY-GUARD-ACCEPTANCE.md sha256 a7ff3e60899d25ef9975af02acbb5b7e5ab0f75d2c8d0269a26c18d6e808db50; experiments/results/p1_shed_attribution/run.py sha256 883c4792d855dbed2fccfc0e16a83f608d820fc9a1d82c0489168d0df3d9de37 (current, read-only guard applied in commit 35e9f45; freeze.json still pins the pre-fix 20547a4ac8a47045b254bbe6534c2c543f052d2cf6c1f07ba1c21bf0066eefb8 and is not overwritten)
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-011-shed-discard-attribution.md (사전등록 2026-09-16 11:20 UTC r1, r2 범위 한정 2026-09-17, 실행 2026-09-18 Codex, 정정 이력 §G 2026-09-18 Claude; 측정 당시 sha256 8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e, 정정 이력 §G C-7 r4 2026-09-18 Claude; 현재 sha256 8bb45236026aea64f942d796efccbb2e5492d6d0c90b6a911b676e87679b8b1b — §A~§F 본문 23,587 bytes 불변)
- 로컬 결과: [LOCAL] EXP-011 attribution PASS (frozen card r2 8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e): 13/13 episodes, 16/16 gated records exact baseline rewards and 9 counters, D1-D4/R 1603 checks PASS, 482 units attributed, C*=ROOM_PARTIAL|REMOTE|NO_DEPOSIT_ATTEMPT S1 64/64=1.0 S2 416/418=0.9952 sole-top 16/16, card verdict REPAIR_AUTHORIZED preserved as measured. Independent Antigravity review COMPLETE (cb4f4c9e4b1171a0424b678eaef4d72d0d0993853d43d192c7ce0655ed689e1d): measurement PASS, causal narrative FAIL. Owner independent recomputation (scratch/claude_exp011_owner_20260918/, read-only, no new episodes, no file writes): D1-c vs P1b originals 26/26 player-records mismatch 0; all 44 gated loss events satisfy discarded_total == max(0, carried_total - room) with 0 violations and 0 events where carried<=room; random unit x item permutation 200 per event changes total discard in 0 events; class re-tally matches aggregate strata; in-day drop/place loss 0/0. Coin conversion of the 482 units is an ESTIMATE, not a ceiling: method A 43,977 vs method B 30,886 (A overstates 29.8 percent); strict upper bound N/A. REPRODUCE with the read-only scripts verify_d1c_vs_p1b.py and verify_order_invariance.py under scratch/claude_exp011_owner_20260918/. [2026-09-18 CORRECTION - pre-fix risk vs post-fix behaviour, commit 35e9f45] BEFORE THE FIX the warning was true and is preserved verbatim here: "DO NOT run run.py --verify-only in a live checkout: freeze.json inputs pin the r2 card SHA, the card now carries a section G correction history, and verify() writes aggregate.json, so a live run records card_verdict INVALID and destroys the measured artifact" - true for the pre-fix runner sha256 20547a4ac8a47045b254bbe6534c2c543f052d2cf6c1f07ba1c21bf0066eefb8, the value freeze.json pins. AFTER THE FIX that risk is gone: Codex applied the read-only guard, verify(*, persist=False), the aggregate.json write sits under if persist, and the --verify-only branch calls verify() with the default so it writes nothing; only the completed 13-cell batch path uses verify(persist=True). Current runner sha256 883c4792d855dbed2fccfc0e16a83f608d820fc9a1d82c0489168d0df3d9de37. Owner independent reproduction 2026-09-18 (read-only, no new episodes, no candidate, no submission): pytest tests/test_exp011_verify_readonly.py tests/test_audit_p1c_replays.py -q gives 3 passed, and a live run.py --verify-only gives exit 1 INVALID while aggregate.json 22ebb927, freeze.json 654e0bbb, commands.json aa3a1db6 and allocation_audit.json 66ed8243 are byte-identical before and after. THE LIVE INVALID IS PROVENANCE DRIFT, NOT INVALIDATION OR OVERWRITING OF THE PRESERVED HISTORICAL EXP-011 RESULT: exactly 2 of the 30 freeze inputs mismatch - this card (measurement-time r2 8736d403 vs the correction-history revision) and run.py itself - while every measurement input matches (engine kaggriculture.py and .json, tools/instrument.py, both tapes, P1b parent and all 13 cells, gate_contract.py), so only gate D1-a breaks and the other 1602 checks pass. freeze.json, the measurement-time SHAs, aggregate.json 22ebb927 and the PASS / REPAIR_AUTHORIZED verdicts with thresholds 0.80/0.80/14 are KEPT UNCHANGED and are not rewritten to current SHAs; SHA-matching full reproduction still requires a checkout or copy restored to freeze commit 0a4b10f. STILL UNGUARDED: experiments/results/p1_shed_attribution/check_allocation.py rewrites allocation_audit.json unconditionally - do not run it in a live checkout (Codex-owned; proposal in the acceptance report). Acceptance report coordination/reports/claude/20260918-EXP011-VERIFY-GUARD-ACCEPTANCE.md.
- Hosted 결과: N/A
- 상태: LOCAL_SUPPORTED
- 유효 범위: Attribution only, engine 1.32.7 and frozen P1b 13 episodes / 16 gated records. Card labels are descriptive; REPAIR_AUTHORIZED is design eligibility, not demonstrated repairability. The only confirmed negative result is scoped to the fixed end-of-day transfer ordering/clamp one_change; other shed interventions are unmeasured, not rejected. Coin values are estimates with no verified ceiling (strict bound N/A). Release zero gate remains FAIL and is not lowered; shed_discarded is not demoted to diagnostic. No candidate, no intervention, no hosted effect measured. In-day DROP/PLACE zero counts are limited to these 13 episodes and tapes. Measurement-time card r2 sha256 8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e, thresholds 0.80/0.80/14, 8 class definitions, strata S1 64 / S2 418 and section E acceptance are unchanged.
- 다음 행동: CONFIRMED SCOPE, one sentence only: the one_change that section D allows for ROOM_PARTIAL (changing the order or clamp of the fixed end-of-day _drop_inventories_to_shed transfer) cannot make all 16 gated records reach shed_discarded == 0, because engine deposit total = min(carried_total, room) is order-invariant (source) and 44 loss events x 200 random permutations changed the total in 0 cases (data). EXP-012 therefore is not preregistered. This does NOT reject other shed strategies (extra last-turn selling, deposit/sell scheduling, production or harvest throttling, item priority) - none of them were measured by this card. Coin conversion is an ESTIMATE with no verified ceiling: method A (episode-wide average realized price x discarded units) gives 43,977 over the gated 16 records, method B (each item's own realized price) gives 30,886, so A overstates by 29.8 percent because 61.4 percent of the discarded units (70.8 percent in the target record) are WHEAT with base price 25; a strict upper bound is N/A because per-step market inventory and price are not recorded in the artifact. The 12.8-17.6 percent of the 109295 target defeat margin is a static arithmetic scenario, not a causal effect, and the FACTS F-T17 '1 of 50 games' figure is likewise scenario-only. The earlier proposal to prioritise coin attribution of noop_actions is WITHDRAWN: 3488 is a count of unit-turn actions and 482 is a count of items, so their ratio is not a comparison of strategic value, and noop_actions is not a count of engine PASS substitutions (see FACTS F-T22). Next decision input is BOARD P1c - same latest window, defeats and draws linked to actual failures, with causal uncertainty marked. EXP-013 remains separate, unauthorised, and neither supported nor rejected by this card. CORRECTED 2026-09-18: the earlier WARNING - "do not run run.py --verify-only in a live checkout; verify() overwrites aggregate.json with INVALID" - applied to the pre-35e9f45 runner only and is kept as history, not deleted. The guard is applied, --verify-only is read-only, and a live INVALID is provenance drift, so the standing rule is now to KEEP freeze.json, the measurement-time card/runner SHAs and the existing results, thresholds and verdicts unchanged rather than to avoid the command, and never to rewrite freeze.json with the current card or runner SHA (evidence/FACTS.md F-T20, card section G C-7, coordination/reports/claude/20260918-EXP011-VERIFY-GUARD-ACCEPTANCE.md). P1c PRIORITY IS NOT FIXED: Codex recomputation refutes the P1c HIRE 100 percent failure claim (W 0/24, D 0/1, L 3/52, 13 unfilled HIRE orders; the 110024392 row2 example succeeded 0 to 5 hands) and the NOOP 100 percent claim is held pending a measurable definition and re-parse, while the close margins 0 / -10 / -92 / -422 have 0 unfilled HIRE and are not causal evidence, and sample provenance is unverified because episodes_{ID}_filtered.json is absent; therefore the HIRE, noop and close-margin paths are NOT ranked until Gemini corrections and sample provenance are confirmed. EXP-013 remains unauthorised and unimplemented, EXP-014 reserved, release zero gate FAIL.

## HYP-0032
- 쉬운 설명: 고용이 덜 됐을 때 실제 일꾼 수를 확인하고 부족한 고용과 작업을 복구한다.
- 주장: opening HIRE 부분 체결 후 actual len(hands)에 따른 state-conditioned recovery가 동일 parent fixed schedule보다 route desynchronization과 패배를 줄인다.
- 출처 수준: ENGINE,HOSTED,HYPOTHESIS,LOCAL
- 출처: experiments/cards/EXP-013-state-conditioned-hire-recovery.md sha256 dabe80a04f89a9f3bde9b8faff198a55108c1f4b1c4f1f809c3db2265ac0cd9f (r3; r2 38d11266ae10022fecddb3bfd3181c784d0e644f350cdab9a7e49199523ab266, r1 96f0278293d56fe50e639f273abe6eaf5f5987c334d9d037cde63c3874354fd6); coordination/proposals/codex/20260917-correctness-path/DECISION.md sha256 286c492fd46a731626d08131934f5ba7965fb5c90cb9c333182b37102858a95d; coordination/reports/codex/20260917-COORDINATOR-CORRECTNESS-PATH.md sha256 096a68ec665d19abbe4edb41cd8ae26e5b59dc20c1d7f769d607483865552274; experiments/cards/EXP-011-shed-discard-attribution.md sha256 8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e; coordination/proposals/codex/20260917-EXP013-CONTRACT-REVIEW.md sha256 54dcaf42541a3afbbb573e2c69dc3cb3d5c0ff7c0b47e77a0cedce742f63a2ef; coordination/proposals/codex/20260917-STATE-CONDITIONED-RECOVERY.md; coordination/reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md sha256 c77010549217d4f344c93336f890dd79bd1d91141f577192b279220c12d95613; experiments/results/p1_release_preflight/manifest.json sha256 46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c; coordination/proposals/claude/exp006/submission.tar.gz sha256 1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721 member main.py bba042e04cff32ab53be2c59c2f5cd9053c8de2bf31632e396ca8faa502896b2 :126-137, yh_base.py d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b :201-206 :84-100 :103-138 :183-191, actions.json 17d503f2fd20d59f9c0f14024d1e74a8add8bb9b5561d4d908b45deecb5495ef; .venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py sha256 bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e :132-135, :311-317, :323-331, :533-541, :657-684, :698-711, :866-884, :905-940; tools/instrument.py sha256 284dee4cdacfc56aab2125f8a92b41df53e14744cca7a8cafa10b853fb6d0629 :287-289, :423-450, :530-550
- 엔진: kaggle-environments==1.32.7
- 실험: experiments/cards/EXP-013-state-conditioned-hire-recovery.md (사전등록 2026-09-17 08:35 UTC, r2 계약 개정·r3 범위 개정 2026-09-17, Claude, sha256 dabe80a04f89a9f3bde9b8faff198a55108c1f4b1c4f1f809c3db2265ac0cd9f); 출처 제안 coordination/proposals/codex/20260917-STATE-CONDITIONED-RECOVERY.md; 검토서 coordination/proposals/codex/20260917-EXP013-CONTRACT-REVIEW.md; Coordinator 실행안 coordination/proposals/codex/20260917-correctness-path/DECISION.md
- 로컬 결과: N/A — candidate 미구현, 미실행. 사전 관측만: target replay 108076177 seat1에서 hands 불일치 46턴, 존재하지 않는 hand에 배정된 unit action 207건, hour12 미충원 인원 9명. r2에서 read-only 재계산: actions.json 13 tape x 30 day 390개 전부 T_first>=3 (0인 날 없음, 분포 3~10), day0 첫 HIRE는 step 1 나머지 날은 hour 0, 하루 안에서 T(s) 단조 비감소, hands 증가 hour는 {1,2,4,5}. replay seat1 PA 기준 첫 발화 턴은 day1 step34 (money 71, market 빈칸, 3건 비용 4) / day8 step193 (money 90, hires_today 2, 6건 비용 52). P1b gated parent target record는 noop_actions 1149·shed_discarded 209·buy_failed 34·hire_failed 9·seed_blocked_plant 16·hands_length_mismatch 46, 나머지 14 record는 hire_failed·hands_length_mismatch 모두 0.
- Hosted 결과: N/A — episode 108076177은 가설 생성 근거이며 candidate 결과가 아님. recovery candidate 미제출.
- 상태: PLANNED
- 유효 범위: first-wave opening HIRE 부분 체결의 복구만 판정. second-wave(hour 2/4/5) 고용·donor hidden policy 식별·EXP-008 opening schedule 부활은 범위 밖. target은 n=1 seed(양 좌석 거울상)이며 가설 생성 경기이므로 G4 통과는 EXP-014 사전등록 자격일 뿐 승격·제출·hosted 근거가 아님.
- 다음 행동: EXP-011 (HYP-0031) independent review is COMPLETE, but it is NOT evidence for this hypothesis and NOT execution approval. Per EXP-011 card section D-1 rationale 2, every EXP-011 output is computed only from shed-discard-unit attributes and yields no value for failure modes with zero discard units. EXP-013 still requires its own HIRE evidence (opening HIRE partial fill, target seat1 hands mismatch 46 turns, 9 unfilled hires), its own numeric gates and a separate human approval (EXP-013 section G, BOARD C1). WITHDRAWN as a confirmed basis: the earlier statement that the 209-unit shed loss caps at about 19200 coin, i.e. 17.6 percent of the 109295 target defeat margin, so shed cannot be the primary cause of that defeat. That conversion multiplied the episode-wide average realized price by the discarded unit count and is not a verified ceiling; using each item's own realized price gives about 13938 (12.8 percent), and a strict upper bound is N/A because per-step market inventory and price are not recorded. Either figure is a static arithmetic scenario, not a causal effect. EXP-011 therefore neither supports nor rejects this hypothesis, and the relative value of the HIRE path, the shed path and the draw-breaking path (HYP-0006) remains unmeasured. Next decision input is BOARD P1c - the same latest window with defeats and draws linked to actual failures. If a separate human instruction forces one card before P1c, EXP-013 is the review-priority candidate because it already has a hosted failure link and a concrete card, not because any effect is demonstrated. Card r3 dabe80a04f89a9f3bde9b8faff198a55108c1f4b1c4f1f809c3db2265ac0cd9f unchanged; implementation and execution remain unauthorized; EXP-014 stays reserved for the pool/public extension named in this card. P1c 2026-09-18 audit: 77 saved hosted replays yield W24/D1/L52; confirmed HIRE failure in 0/24 wins, 0/1 draws, 3/52 losses (13 orders). Gemini all-games failure claim is rejected. Exact collection-window/submission linkage and full noop reassessment remain pending; causal recovery effect remains N/A. See coordination/reports/codex/20260918-P1C-AUDIT-VERIFY-GUARD.md and experiments/results/p1c_20260918_audit/replay_audit.json. No EXP-013 implementation/execution authorized. BOUNDED REVIEW 2026-09-18: coordination/reports/codex/20260918-P1C-BOUNDED-EVIDENCE.md and experiments/results/p1c_20260918_audit/bounded_evidence_assertions.json record 32 passing assertions. Original HIRE counts and Codex examples independently confirmed; prevalence does not decide causal recovery value. Endgame PLACE MILK failure and final STRAWBERRY/WHEAT neglect are refuted; 109856629 immediate DROP alternative is unavailable at pre-state, and 109802471 was already behind before row718. Real final WOOL2 in 109831239 is observed but episode-seat to submission/source identity remains N/A. NOOP audit uses whole-turn projections and disagrees with its reported definition; no 77-game NOOP remeasurement. Decision: insufficient current evidence for a selected actionable modification; no proposal, candidate, new experiment ID or EXP-013 run. This updates supporting review context under existing TEST-0013 only, not its results or gates; HIRE, close-game and top-donor paths are not rejected.

## HYP-0033
- 쉬운 설명: 똑같은 코드를 쓰는 상대와 붙으면 비기는데, 그때만 비싼 물건을 한 턴 먼저 팔면 이길 수 있는지 확인한다.
- 주장: P2 위에서, turn 1-143 동안 두 농장의 공개 상태가 매 턴 완전히 같았던 경기에 한해 turn 144-717 의 고가 품목 SELL 을 한 턴 앞당기면 P2 의 정확한 복제본에게 무승부 대신 승리한다.
- 출처 수준: ENGINE,HOSTED,HYPOTHESIS
- 출처: evidence/FACTS.md 2026-09-20 시장 주문 체결 순서와 거울전 무승부; evidence/raw/p2_losses_20260920/features.csv; KILLS K2(1턴 선행이 정답)
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-014-mirror-sale-lead.md; experiments/cards/EXP-014R-mirror-sale-lead-replication.md
- 로컬 결과: EXP-014 (seed 3000대): INVALID, 수치 25/0/5·회귀 0. EXP-014R (seed 4000대, engine 1.32.7, arena): INCONCLUSIVE — 변형 vs P2 22/0/8 (22.0/30, 기준선 P2 vs P2 15.0, 무승부 28/30), 패널 100경기 회귀 0, 총점 92=92. analysis/exp014r/summary.json
- Hosted 결과: N/A
- 상태: INCONCLUSIVE
- 유효 범위: 정확한 복제 상대(무승부 7/112)에만 작동하도록 제한. 같은 가족의 다른 버전 상대에는 P2 와 동일 행동
- 다음 행동: 로컬 추가 seed 금지. hosted 시험은 fast lane 단계 F 조건(회귀 0) 충족 — 사람 결정 대기

## HYP-0034
- 쉬운 설명: 똑같은 코드를 쓰는 상대와 같은 턴에 같은 물건을 팔 때, 주문 순서를 맨 앞으로 옮겨 먼저 팔면 이길 수 있는지 확인한다.
- 주장: P2 위에서, turn 1-143 동안 두 농장의 공개 상태가 매 턴 완전히 같았던 경기에 한해 turn 144-717 의 고가 품목 SELL 을 그 턴 market 목록의 맨 앞 slot 으로 옮기면 P2 의 정확한 복제본에게 무승부 대신 승리한다.
- 출처 수준: ENGINE,HOSTED,HYPOTHESIS
- 출처: evidence/FACTS.md 2026-09-20 시장 주문 체결 순서와 거울전 무승부 (kaggriculture.py:544-628 slot 순서 lockstep; 무승부 경기에서 첫 고가 SELL 이 slot 0 이 아닌 턴 13/122)
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-015-mirror-slot-priority.md
- 로컬 결과: EXP-015: INVALID(기준선 무승부 24/30). 수치: 변형 vs P2 1/0/29, 패널 회귀 14/100(전부 alperen). failure 조건 두 개 모두 크게 초과
- Hosted 결과: N/A
- 상태: INCONCLUSIVE
- 유효 범위: 정확한 복제 상대에만 작동하도록 제한. 효과는 고가 SELL 이 slot 0 이 아닌 턴에만 생긴다
- 다음 행동: 폐기 권고 — 재현하지 않음. SELL 묶음 재정렬이 첫 SELL 을 쓰는 자금 규칙과 충돌했을 가능성 [INFERENCE], 미확인

## HYP-0035
- 쉬운 설명: C1 에 없는 판매 앞당김 층을 Ozer V53 에서 그대로 옮기면, V53 계열에 덜 지고 C1 복제본에게 무승부 대신 이기는지 본다.
- 주장: C1(827ddf29) 끝에 V53 의 EXP293 판매 앞당김+frontload 블록(main.py 3532-3629)을 그대로 붙이면, 새 seed 에서 C1 복제본 상대 순승 +10 이상이고 패널 상대 패배가 늘지 않는다.
- 출처 수준: LOCAL,ENGINE,INFERENCE
- 출처: coordination/reports/claude/20260922-C1-HB-ANALYSIS.md; releases/public-ozer-v53-exact/main.py:3532-3629; kaggriculture.py:728-748
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-016-c1-sale-advance.md
- 로컬 결과: EXP-016: INCONCLUSIVE. 거울 seed 순승 +23 (31/1/8), 패널 합산 패배 55 vs 63 (−8), 단 v13(C2) 상대 패배 10 vs 4 (+6, 기준 +2 초과). 예외 0
- Hosted 결과: N/A
- 상태: INCONCLUSIVE
- 유효 범위: C1(pipe16) 위, 표준 설정, turn 144-717
- 다음 행동: hosted 최대 패배원(step 53 분기 봇) 식별 후 그 상대로 재평가. 사람이 slot B hosted 실험으로 제출할지 결정

## HYP-0036
- 쉬운 설명: hosted 에서 C1 을 가장 많이 이긴 공개 봇(One More Wheat)에 EXP-016 의 판매 앞당김 층을 붙이면 두 장점을 다 갖는지 본다.
- 주장: OMW(10f58185) 끝에 V53 판매 앞당김 블록을 붙이면 새 seed 에서 OMW 상대 순승 +10 이상, EXP-016 상대 순승 0 이상, 패널 패배가 EXP-016 보다 늘지 않는다.
- 출처 수준: HOSTED,LOCAL,INFERENCE
- 출처: coordination/reports/antigravity/20260922-1716-C1-HOSTED-MAP.md; coordination/reports/antigravity/20260922-1737-STEP53-ID.md; coordination/reports/antigravity/20260922-1701-EXP016-RUN.md
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-017-omw-sale-advance.md
- 로컬 결과: EXP-017: SUCCESS. OMW 상대 59/0/21(순승 +38), EXP-016 상대 78/0/2(+76), 패널 패배 147 vs 155, 예외 0
- Hosted 결과: N/A
- 상태: LOCAL_SUPPORTED
- 유효 범위: OMW 위, 표준 설정, turn 144-717
- 다음 행동: 사람이 제출 (FIFO 로 C1 56426857 은퇴). hosted 24h 후 EXP-016 과 비교

## HYP-0037
- 쉬운 설명: 기존 CARROT 전환 기준 하나를 바꾸면 herd-safe 상대 패배를 줄이는지 확인한다.
- 주장: DP 0924의 기존 CARROT 전환 margin -5.0을 -15.0으로 바꾸면 반복된 CARROT 생산 부족과 herd-safe 패배를 줄이고 전체 패널 및 DP 하한을 만족한다.
- 출처 수준: HYPOTHESIS,ENGINE
- 출처: experiments/results/dp_loss_cause_20260925/q1_summary.json; coordination/proposals/claude/20260924-DP-LOSS-CAUSE-CODEX.md; parent main.py:4479,4666; herd-safe main.py:4475
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-018-dp0924-single-factor.md; TEST-DP-LOSS-CAUSE-20260925 fallback carrot
- 로컬 결과: N/A — fallback not executed: first refresh Q2 reached3 flips, so the preregistered fallback condition did not occur. Parent+append carrot artifact exists but has no measured performance.
- Hosted 결과: N/A
- 상태: PLANNED
- 유효 범위: Refresh candidate flips<3 only: fixed 9 hosted losses; no stacked changes or retuning; DP 0924 exact parent only. K10 RETRACTED; not MELON reallocating experiment.
- 다음 행동: No automatic execution. Refresh later failing DP80 does not reopen the Q2 fallback condition. A new Coordinator instruction/card would be required; source proposal and frozen EXP018 remain unchanged.

## HYP-0038
- 쉬운 설명: 막판에 한 번 더 판매 순서를 정리하면 내 현금을 늘리기보다 공유 market에서 상대의 판매 조건을 악화시켜 127 변형 패배를 줄일 수 있는지 본다.
- 주장: v074의 step 576 이후 fixed-sell closure 또는 WOOL 우선순위 단일 변경은 127 변형 tape에서 paired score를 개선하면서 기타 tape와 closed-loop 127/guard 성능을 사전등록 한도 안에 보존한다.
- 출처 수준: ENGINE,LOCAL,HYPOTHESIS
- 출처: experiments/late_0928/cause_table.json; coordination/proposals/claude/20260927-LATE-CODEX.md; releases/round2-v074/main.py; releases/exp035-d157/main.py
- 엔진: 1.32.7
- 실험: experiments/late_0928/prereg.json; TEST-LATE-0928-SCREEN
- 로컬 결과: LOCAL_FAILED. Frozen cause panel 14 pairs: d157 flipped 11 losses, own final cash delta -46.9 mean, opponent cash delta -1041.6 mean, margin +994.8, supporting opponent market suppression rather than own-cash recovery. Screen: l576_closure1 d127 0 lower95 0 other 0 effect1/205; l648_closure1 d127 0 lower95 0 other 0 effect2/205; l576_wool_first d127 -0.09375 lower95 -0.15179 other -0.06452 effect180/205. All invalid0 and 1-worker max<=0.0604s. coordination/reports/codex/20260927-2126-LATE.md
- Hosted 결과: N/A
- 상태: LOCAL_FAILED
- 유효 범위: v074 exact parent; step 576 이후; frozen 112 127_near tapes and 93 other tapes; closed-loop jobs only for exact 127, 23 guard bots, and 55be5d5f
- 다음 행동: Do not add passes, seeds, candidates, or relax thresholds. Do not run the prepared closed-loop jobs for these failed candidates. Move to a different preregistered mechanism; release and submission remain N/A.

## HYP-0039
- 쉬운 설명: 공개 자금·농장·시장 정보로 d157이 비공개 55be 변형에게 질 경기를 조기에 구분할 수 있는지 확인한다.
- 주장: 고정 6개 공개 관측 특징을 step 240·384·480·576·624에서 읽으면 비공개 55be 변형 상대 패배를 반복적으로 구분한다.
- 출처 수준: HOSTED,LOCAL,HYPOTHESIS
- 출처: analysis/c26_hosted_20260929/opponents.csv; coordination/reports/codex/20260929-1408-FP-PUBLIC-SIGNAL.md
- 엔진: 1.32.7
- 실험: experiments/fp_signal/PLAN.md; TEST-FP-PUBLIC-SIGNAL-20260929
- 로컬 결과: 43 eligible hosted-source development episodes, 25L/18W and 42 opponent submissions; 30 fixed checks, 0 pass and only 1 cell-size eligible. Step576 opponent-money lead 21L/1W versus 4L/17W is a late association, not causal. verdict sha256 ffacd2c8d9152abe740451f02a64e027d84ee50512aced134b1f93e44f4b1882.
- Hosted 결과: N/A — no candidate submission or hosted intervention; source episodes are hosted observations only
- 상태: INCONCLUSIVE
- 유효 범위: d157 submission 56607884 against non-full 55be-labelled hosted opponents in the 43 non-holdout W/L episodes; six features at five fixed steps only; one fingerprint-only difference remains; no causal conclusion
- 다음 행동: No candidate from this screen. Require a new independent holdout and a specific causal action mechanism before intervention; original FP holdout has three aggregate rows exposed.
