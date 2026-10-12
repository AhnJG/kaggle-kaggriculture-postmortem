# BOARD — 지금 무엇이 중요한가

**갱신 2026-09-28 23:30 KST · Claude (Coordinator).** 09-25판 이후 제출 4회(v171, v074, d157, c26)를 반영했다. 정본 순서: 이 BOARD 현재 절 → [HANDOFF-20260928-CLAUDE.md](HANDOFF-20260928-CLAUDE.md) → [HOSTED_LEDGER](../evidence/HOSTED_LEDGER.md). "이전 기록" 절은 역사이며 지시가 아니다.
코디네이터만 수정한다. 2일 이상 갱신되지 않았으면 AGENTS §11에 따라 먼저 현재 상태를 재확인한다.

## 현재 상태 (09-28 23:30 KST)

| 항목 | 값 | 근거 |
|---|---|---|
| 최종 제출 마감 | **09-30 23:59 UTC = 10-01 08:59 KST**. 마지막 제출 시한(잠정) **09-30 21:00 KST** | HANDOFF-20260928 §1 |
| **활성 슬롯 (FIFO 순서)** | **① d157 56607884** (55be5d5f + `_S1002_PASSES` 35, main 94a46c11…, tar 4281ea3c…; 09-28 18시 2345.7, 136경기 0.640) → **② c26 56635330** (d157 + `_CA_MARGIN` −26, main ff230c83…, tar 8961e03e…; 09-28 08:45 UTC 제출) | HANDOFF-20260928, HOSTED_LEDGER 09-28 |
| **다음 제출이 은퇴시키는 것** | **d157 56607884** | FIFO |
| 사전등록 | analysis/exp045/PREREG.md + PREREG_ADDENDUM.md (R2 완화, A2 hook 진단, A3 holdout, A4 두 번 제출 허용) | 사람 승인 09-29 |
| 마감 시간표 (09-29 확정 제안) | 새 개입 실험 시작 마감 **09-30 09:00 KST** → 후보 판정(holdout·D3·릴리스까지 완료) **09-30 18:00** → 사람 제출 시한 **09-30 21:00**. 통과 후보 없음 시의 행동은 사람 결정 대기(아래 방침 문구와 충돌) | Claude 09-29 |
| 방침 | 개선 후보를 계속 만든다(bronze 도 보장되지 않음). 통과 후보가 없으면 제출하지 않고 d157 + c26 을 유지한다(사람 09-29, 선택지 A). 비교 기준은 **d157**(현재 주력, 다음 제출이 은퇴시킴). c26 은 실전에서 더 약할 가능성(정정 문서 45). 후보는 모든 panel 에서 max(d157, c26) 이상이어야 제출(사람 09-28 14:05) | 사람 결정 |
| 핵심 사실 | 2400+ 상위 팀 상대 d157 0.40(tape). margin 은 WHEAT 와 무관하고 WOOL/MILK 판매 단가에서 갈린다(EXP-044). d157 은 이미 상대 수거·판매를 추적하는 판매 모듈을 여럿 가진다 | analysis/exp044_margin/FINDINGS.md |
| 엔진 | kaggle-environments 1.32.7 (bc8a5487…) | FACTS |

## 다음 작업

| 순위 | 작업 | 담당 | 지시서 | 상태 |
|---|---|---|---|---|
| **0** | FIRSTPRINCIPLES: 비공개 55be 변형 집단을 이기고 2300+ 로 가는 방법을 처음부터 탐색 (자유도 높음) | Codex | [20260929-FIRSTPRINCIPLES-CODEX.md](proposals/claude/20260929-FIRSTPRINCIPLES-CODEX.md) | 발행 09-29 · 중간 22:00 · 최종 09-30 15:00 |
| **0b** | HOSTEDPM: d157·c26 최신 실전 전적 수집 | Antigravity | [20260929-HOSTEDPM-ANTIGRAVITY.md](proposals/claude/20260929-HOSTEDPM-ANTIGRAVITY.md) | 발행 09-29 |
| **1** | EXP-045 v2: 판매 모듈 ablation 8 + 규칙 3 = 변형 11개 구현·smoke·jobs-A (실행 안 함) | Codex | [20260928-EXP045v2-CODEX.md](proposals/claude/20260928-EXP045v2-CODEX.md), 사전등록 analysis/exp045/PREREG.md | DONE (보고 20260928-2132, IMPLEMENTED_SMOKE_PASS, Claude 표본 검증 PASS) |
| **2** | EXP-048 Stage A 실행 = EXP-045 11 변형 + EXP-047 hook (12 × 595 = 7,140경기, Kaggle 5 + Mac) | Antigravity | [20260929-EXP048A-ANTIGRAVITY.md](proposals/claude/20260929-EXP048A-ANTIGRAVITY.md) | DONE (보고 20260929-0140) → 판정: Stage B 진출 hook, K3 (reports/claude/20260929-EXP048A-VERDICT.md) |
| 완료 | EXP-047 shadow 55be → _front_run hook 구현 (PREPARED_DIAGNOSTIC_WEAK: 추정 precision 0.11) | Codex | [20260929-EXP047-CODEX.md](proposals/claude/20260929-EXP047-CODEX.md) | DONE (보고 20260928-2133) |
| **2b** | FRESH2400: 2400+ 25 submission 의 09-28 05:27 UTC 이후 새 경기 수집(새 holdout) | Antigravity | [20260929-FRESH2400-ANTIGRAVITY.md](proposals/claude/20260929-FRESH2400-ANTIGRAVITY.md) | DONE (보고 20260928-2248, 305경기) → exp049_fresh tape 302 |
| **2c** | EXP-048 Stage B 실행 (hook·K3 × exp039 panel + holdout 148 + fresh; 3,164경기) | Antigravity | [20260929-EXP048B-ANTIGRAVITY.md](proposals/claude/20260929-EXP048B-ANTIGRAVITY.md) | DONE → FAIL(hook, K3 불통과) reports/claude/20260929-EXP048B-C26HOSTED.md |
| **3** | c26·d157 hosted 성적 수집 | Antigravity | [20260929-C26HOSTED-ANTIGRAVITY.md](proposals/claude/20260929-C26HOSTED-ANTIGRAVITY.md) | DONE: c26 은 아직 상승 중(약하다는 증거 없음), d157 은 55be 계열 상대 증가로 하락 |
| 4 | Stage A 판정 → Stage B jobs 작성 → 최종 판정·release·D3 | Claude | analysis/exp045/PREREG.md | 대기 |
| 5 | 제출 (PASS 시) | 사람 | — | 대기 |
| 완료 | EXP-043 oracle(NO CLUE), EXP-044 margin 분해 | Claude | reports/claude/20260928-2010-EXP043-VERDICT.md | 종료 |
| **0c** | EXP-058 route 그룹 재배정: Stage S (route 강제 5 arm × 269, 1,345경기) | Antigravity | [20260929-EXP058S-ANTIGRAVITY.md](proposals/claude/20260929-EXP058S-ANTIGRAVITY.md), 사전등록 experiments/exp058_route/PREREG.md (75a8125e…) | DONE → Stage S FAIL (reports/claude/20260929-1650-EXP058S-VERDICT.md). 최선 S->107 Δ+0.024, 하한 −0.013, c26 대비 −0.006 |
| 완료 | EXP-056 공개 Step1009 7종 screen · EXP-057 거위 확대 3변형 | Claude/Antigravity | reports/claude/20260929-1330-EXP056-057-VERDICT.md | FAIL (전부 d157 보다 낮음) |

## 제출 운영 (현재)
- 최신 2개만 활성, 새 제출은 먼저 올린 것(d157)을 은퇴시킨다. 제출은 사람만 한다.
- 금지: 엔진·RNG 수정, holdout seed 9000–9599·holdout 5팀 사전 개봉, 결과 본 뒤 기준 변경.

---

## 이전 기록 (09-25판 보존 — 지시 아님)

### (과거·09-25판) 현재 상태

| 항목 | 값 | 근거 |
|---|---|---|
| 최종 제출 마감 | **09-30 23:59 UTC**. 마지막 실험 제출 **09-30 12:00 UTC**. 신규 전략 마감 **09-27 00:00 KST** (이후 슬롯 B 실험만, 정책 B-4) | CANDIDATE-POLICY B-4·E-4 |
| 최종 순위 | 두 활성 봇 각자 BT 중 높은 쪽. BT 는 두 봇 모두 활성인 경기만 → 마감 후 약 2주가 핵심 | 사람 확인, 정책 E-1 |
| **활성 슬롯 (FIFO 순서)** | **① demand-preserving 0924 exact 56518910 (09-24 10:26 UTC, 2191.6 @약 27h) → ② 127ed3e6 exact 56549720 (09-25 11:48 UTC, 2165.6 @제출 직후)** — EXP-017 56490029 은퇴. 09-25 22:40 KST 사람 보고 | HOSTED_LEDGER 09-25 |
| **다음 제출이 은퇴시키는 것** | **DP 0924 56518910** (anchor 를 바꾸려면 재제출 절차 B-5 먼저 판단) | FIFO |
| 메달 경계 | 동 약 995위 2289.7 (09-24 저녁) · 은 약 500위 ≈ 2492 (09-24 LB 500위 2492.3) | HOSTED_LEDGER 09-24 |
| DP 기대 수준 | ~~2450~2550~~ **폐기** (상대 강도를 팀 LB 로 잰 오류). 실제 hosted 2191.6 → **동메달 경계 아래(−98)**. 정정 자료 대기 | HOSTED_LEDGER 09-25 |
| 목표 | **동메달 복귀 우선** (09-25 14:20 재설정, 은 구간 도전은 보류) | CANDIDATE-POLICY F-2 |
| 팀 | 솔로 "Sian". 병합 검토 안 함 | 사람 결정 |
| 엔진 | kaggle-environments 1.32.7 | FACTS |

### (과거·09-25판) 다음 작업

| 순위 | 작업 | 담당 | 지시서 | 상태 |
|---|---|---|---|---|
| **1** | **자율 탐색 루프 v2** — 1단계 127ed3e6 exact 준비(≤3h) → 2단계 metric calibration·동결 → 3단계 무인 탐색(CP1 09-26 21:00, 종료 09-28 21:00 KST) → 4단계 disjoint holdout 확인 | Codex | [20260925-SEARCH-LOOP-CODEX.md](proposals/claude/20260925-SEARCH-LOOP-CODEX.md) | 사람 승인 완료 09-25 14:33 · 발행 (사람 전송 대기) |
| **2** | 127ed3e6 exact 슬롯 B 제출 — 1단계 보고(NEWMETA-EXACT) 직후 사람 판단. EXP-017 은퇴 | 사람 | 1단계 보고 | 대기 |
| 완료 | DP 레이팅 확인 — API 에 submission 점수 없음 (BLOCKED), 127ed3e6 재지문 표본 1–2 | Antigravity | [보고](reports/antigravity/20260925-1425-DP-RATING-CHECK.md) | 종료 |
| 대체 | EXP-020 / EXP-019 / EXP-018 슬롯 B 예외 | — | 탐색 루프로 흡수. EXP-018 은 NOT_ELIGIBLE 유지 | 종료 |
| 4 | 09-30 최종 scan (+ 상성 파일 확산 확인) | Antigravity | [20260923-FINAL-SCAN-ANTIGRAVITY.md](proposals/claude/20260923-FINAL-SCAN-ANTIGRAVITY.md) | 09-30 09:00 KST 알림 예약 |
| 완료 | EXP-018 DP 패배 원인·refresh 3→2 | Codex | [20260924-DP-LOSS-CAUSE-CODEX.md](proposals/claude/20260924-DP-LOSS-CAUSE-CODEX.md) | VERIFIED_NOT_ELIGIBLE_DP_FLOOR (09-25 13:40) |
| 종료 | Astra LOSS-DIVERGENCE / Opus 5.5 PREFIX0 | — | EXP-018 로 대체·흡수 | 종료 |

### (과거·09-25판) 제출 운영
- 최신 2개만 활성, 새 제출은 먼저 올린 것을 은퇴시킨다. 매 제출 전 위 "다음 제출이 은퇴시키는 것" 줄을 확인한다. 제출은 사람만 한다.
- 슬롯 역할·조건은 CANDIDATE-POLICY B·E (슬롯 A = hosted 24h 이상 검증된 최고 파일, 슬롯 B = 실험 1개).
- 슬롯 B 후보(EXP-018 예외 또는 EXP-019)를 올리면 EXP-017 이 은퇴한다. **그 뒤 FIFO 는 DP 가 먼저** → 슬롯 B 를 다시 바꾸려면 DP 동일 바이트 재제출 → 새 후보 제출 (2회, 정책 B-5). DP 교체는 후보가 hosted 24h 이상에서 DP 보다 확실히 높을 때만.
- 09-30 긴급 경로는 정책 E-5.

---

## 이전 기록 (09-20판 보존 — 지시 아님)

**현재 계획: [plan/CURRENT.md](../plan/CURRENT.md) → [마감까지의 계획](../plan/kaggriculture_deadline_plan_20260915.md).**

1. 무엇을 하는가: 목표를 순위 상승(동메달 942위·2395.3)으로 전환. 상위 donor tape exact 재생 → 개선 1개씩 hosted 시험(fast lane F0). correctness 경로(C0/C1)는 아래에 보존.
2. 왜 하는가: 자체 계열 1487–1638로 동메달까지 약 757점 부족. P1b zero gate FAIL 은 hosted 강도의 검증된 예측자가 아니다(yhay81-exact 는 FAIL 상태로 2188.4) `[INFERENCE]`.
3. 측정 결과: `[HOSTED]` 09-18 Sian 2,201위/9,423팀. yhay81-exact 재제출 56330776 1538.9(44분, 수렴 전), EXP-007 1489.0, EXP-006 은퇴(1638.3). donor 재생 결과 N/A. 이전 `[LOCAL]` P1b FAIL·EXP-011 PASS 기록은 유지.
4. 다음: F0 전환 — 상위 60위 donor 중 고정 tape 0/52라 단일 tape 재생 경로 종료. 09-16 이후 공개 notebook 3개(alperen·lynnsakurai·tetsutani) exact 재현·gate(Codex) → 사람 제출. mzcao7 은 외부 dataset 의존으로 출처 확인(Antigravity) 후. yhay81-exact 재제출 14h 1515.3. 비재생 새 전략 P2 HOLD 유지.

### (과거·09-20판) 현재 상태

| 항목 | 값 | 근거 |
|---|---|---|
| 공식 최종 제출 | **09-30 23:59 UTC = 10-01 08:59 KST** | 09-15 직접 읽은 공식 Timeline, 아래 snapshot |
| 공식 참가·팀병합 | **09-23 23:59 UTC = 09-24 08:59 KST** | 동 |
| 제출 기록 | **5건**, 모두 COMPLETE 표시 | 이번 CLI 조회 |
| 활성 슬롯 | **EXP-017 56490029 (09-23, 2100.2) / demand-preserving 0924 exact 56518910 (09-24 10:26 UTC)**. EXP-016 은퇴. 다음 제출은 EXP-017 을 은퇴시킨다 | 사람 제공 ID |
| 최신 hosted 점수 | **P2 2421.6**(11h, 수렴 전) · yhay81 1483.8 | 09-19 15:20 UTC UI, [HOSTED_LEDGER](../evidence/HOSTED_LEDGER.md) |
| Sian 순위 / 메달 경계 | **949위 / 9,550팀 (BRONZE 표시)** · 동 955위 **2418.9**(여유 +2.7) · 은 477위 2652.6 · 금 29위 2913.5 | 09-19 15:20 UTC leaderboard API |
| 팀 | 공개 UI Sian, member `<kaggle_user>` 1명 확인 | 비공개 초대·합병 상태 N/A, 기본 계획은 솔로 유지 |
| 잠정 incumbent | **P2** (56347732 은퇴 전 2410.4 @1d). EXP-014 는 hosted 판독 대기 | HOSTED_LEDGER 09-20 |
| 최신 완료 작업 | **EXP-011 attribution PASS / 독립 검토 완료** | [결과](reports/codex/20260918-EXP011-RESULT.md). EXP-008 전략 실험은 FAILURE 유지 |
| 엔진 | **kaggle-environments 1.32.7**, 설치 Python/JSON SHA lock 일치 | 이번 read-only 해시 확인; hosted 최신 module_version N/A |
| 현재 Python | **3.13.14** | `python3 --version` |
| release 계측 | **schema 3 · P1b FAIL** | 실제 parent tar 고정13경기, 독립검증 VERIFIED_LOCAL_FAILURE. 새 candidate preflight는 N/A |

최신 직접 조회 정본: [20260915-0115-KAGGLE-SNAPSHOT.md](reports/codex/20260915-0115-KAGGLE-SNAPSHOT.md).
09-18 갱신은 P1b 후속 판정과 correctness 실행 경로만 반영한다. 위 hosted 수치는 과거 snapshot이며 새 조회가 아니다.
(09-20 당시 기준) [evidence/HOSTED_LEDGER.md](../evidence/HOSTED_LEDGER.md)는 09-14 이전 snapshot까지이며 Claude owner의 새 행 반영을 기다린다. 날짜가 다른 두 값을 같은 시점 값처럼 비교하지 않는다. 이 BOARD는 더 최신인 위 직접 조회를 명시적으로 인용한다.

### (과거·09-20판) 다음 작업 — 우선순위와 종료 조건

| 순위 | 작업 | 담당 | 종료 조건 |
|---|---|---|---|
| **P0** | EXP-008 결과·registry·hosted 원장 동기화 | Claude | [owner 이관안](proposals/codex/20260915-owner-record-sync.md) 반영. EXP-008 frozen card는 보존하고 결과 보고서로 연결 |
| **P1a** | 공개 notebook/discussion inventory·변경분·정정 댓글 판독 | Gemini 단일 writer / Claude 판독 / Codex 원장 | 09-16 18:00 KST까지 계획 §5.1의 source SHA·채택/보류/기각·owner 인수 표. 이후 09-26까지 매일 변경분; 미확인 claim은 보류 |
| **P1b** | actual parent A release preflight | Codex / 독립 검증자 | **VERIFIED_LOCAL_FAILURE**: 13/13 완료, parent16/16 zero gate FAIL. 정본 report와 후속 독립검증 참조. 새 전략 HOLD 유지; 아래 C0/C1 경로 준비 |
| **P1c** | 최신 24시간 hosted window + 각 agent 최신 패배 1판 postmortem | Gemini 수집 / Claude 해석 / Codex 재현 | **제한 검토 종료 — 이 자료에서 실행 가능한 수정 가설 미확보.** PLACE MILK 실패·STRAWBERRY/WHEAT 방치·즉시 DROP 역전 주장은 반박. exact window/submission 연결 N/A와 raw replay 관측을 구분. [정정 보고서](reports/codex/20260918-P1C-BOUNDED-EVIDENCE.md) |
| **F0** | fast lane (09-19~29) — **09-19 전환: 상위 donor 고정 tape 0/52 → 09-16 이후 공개 notebook exact 재현** | Codex 재현·gate / Antigravity 원문·목록 확인 / Claude 후보 순서·Coordinator / 사람 제출 | [단계 B 결과·결정](proposals/claude/20260919-F0-STAGE-B-RESULT-DECISION.md), [Codex 지시서](proposals/claude/20260919-F0-PUBLIC-EXACT-WORK-ORDER-CODEX.md). 대상은 공개 제출 코드의 무수정 재현과 그 1-change 변형뿐. §3-2 gate. 단계 C(6/6) 종료 |
| **P2** | 새 전략 one-factor card | Claude | 실제 parent P1b PASS·관련 claim 인수·원인 근거·exact card가 선행. FAIL이면 새 전략 HOLD. C0/C1은 관측된 correctness failure만 다루며 P2나 release 승인 대체 불가. 재생 계열은 F0 로 이관, 비재생 전략만 이 HOLD 적용 |
| **P3** | 수락된 카드 구현·독립 검증 | Codex / 다른 검증자 | 카드 판정 + release gate를 별도 통과. local만으로 hosted 우위 선언 금지 |
| **P4** | final pair·제출 순서 결정 | Coordinator / 사람 | 독립 강도·패배 패턴·FIFO 이력 손실·승인 기록 |

### (과거·09-20판) Correctness 실행 경로 — 새 전략·제출과 구분

근거: 마스터 플랜 §5.2 FAIL/N/A 경로. 현재 parent FAIL은 유지하며 수정 artifact의 미래 PASS까지 불가능하다고 해석하지 않는다.

| 단계 | 담당 | 조건과 종료 |
|---|---|---|
| **C0 EXP-011** | Claude 카드 / Codex 계측 / 별도 독립 reviewer | **실행 완료:** 고정13경기/16 record exact baseline, D1~D4/R PASS, class 판정 REPAIR_AUTHORIZED. Antigravity 측정 검토 완료 및 Claude owner 인수. EXP-012의 기존 범위는 사전등록 불가; C1 실행 미승인 |
| **C1 EXP-013 준비** | Claude / Coordinator | 계약 검토6개 항목 수정, EXP-011 결과별 금지 범위 한정은 사용자 승인으로 해소. r3 카드 SHA·HYP 갱신 완료; 독립 설계·구현 검토와 EXP-013 실행 승인은 별도. 문서 작업은 C0와 함께 가능 |
| **C1 제한 실행** | Codex / 독립 reviewer / 사람 | 유효한 EXP-011 판정 + scope 충돌 해소 + exact-card 사람 승인 후 구현. candidate·runner freeze 및 독립 구현 검토 후 G0b parent→candidate 동일13경기. 결과는 diagnostic이며 제출 불가 |

EXP-011의 역사적 REPAIR_AUTHORIZED 라벨은 보존하지만 후속 검토에서 EXP-012의 허용 범위로 success 달성 불가를 확인해 사전등록 불가로 종결했다. EXP-013 자동 승인이 아니다. BLOCKED_AMBIGUOUS_ROOT_CAUSE/BLOCKED_STRATEGY_BOUNDARY이면 shed repair 금지를 유지한다. 독립 HIRE 근거의 EXP-013까지 금지하는지 Claude가 카드 범위를 명확히 하고 사람이 별도 bounded 실험 범위를 승인하기 전 대기한다. threshold나 표본을 바꿔 금지를 우회하지 않는다.

EXP-011 이후 EXP-013은 제한 실험 후보로 유지한다. 새로운 broad noop diagnostic보다 우선인지는 최신 failure 빈도와 구체성을 비교해야 한다. EXP-012는 기존 허용 범위로 사전등록하지 않는다. 같은 tools/instrument.py 변경은 순차 통합한다. parent가 바뀌면 카드·baseline 기준을 재동결한다. 새 runner로 parent baseline을 먼저 기록하며 P1b 원자료는 덮어쓰지 않는다.

상세 분기·승인 범위: [Coordinator 실행안](proposals/codex/20260917-correctness-path/DECISION.md). 문서 적용 승인은 실행 승인이 아니다. 새 전략 P2와 최종 release는 기존 전체 gate를 그대로 통과해야 한다. Coordinator/구현자는 자기 결과를 단독 승인하지 않는다.

P1b 근거: [실행 보고](../experiments/results/p1_release_preflight/report.md), [후속 독립검증](reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md). 최초 보고의 PENDING은 후속 검증으로 해소됐으나 LOCAL FAILURE 판정은 유지된다.

**이미 완료된 일:** EXP-008 계측·card 수락·고정 326셀 실행, gate split, release source 추적.
09-13 BOARD의 ‘EXP-008 card 수락 대기’, 과거 HANDOFF의 ‘v0 첫 제출’은 더 이상 지시가 아니다.
`TASKS.md`의 타 owner 과거 미실행 문구와 registry PENDING은 상태 갱신 대기이며 재실행 명령으로 쓰지 않는다.

### (과거·09-20판) 실험·가설의 현재 결론

- **F0 후보 정리 (2026-09-20):** 다른 계보 D1–D3, ladder 점수 공개 변형 V1(goodpjw2008)·V2(seyitkaangunes 기본 4-layer) 모두 로컬 진단에서 P2 상대 0/0/20(arena, 좌석 대칭이라 독립 seed 10). 두 번째 슬롯 후보에서 제외. 활성 {P2, alperen} 유지, 09-21 01:00 KST hosted 판독 후 결정. **진입점 사실**: 엔진은 파일의 마지막 callable 을 쓴다(FACTS 09-20) — `tools/instrument.py` 는 `agent` 이름을 써서 공개 변형에서 다른 함수를 시험할 수 있다.

- **P2 hosted 패배 분석 (2026-09-20, Claude):** 기준 시각까지 P2 112경기 **80승/25패/7무**. 패배·무 32 vs 대조 승리 32 비교에서 사전 고정 문턱(A≥20%, A−B≥20%p)을 넘는 원인 **없음** — 단일 반복 원인이 보이지 않는다. 같은 상대 매칭은 2쌍뿐이라 대조력이 약하다. [보고서](reports/claude/20260920-0114-P2-LOSS-ANALYSIS.md). P2 위 표적 수정보다 최신 공개 변형 비교가 다음 후보.

- **K3 범위 정정 (2026-09-18 승인, Codex 독립 검토 PASS, 09-19 적용):** K3는 market 주문 기록을 다른 작업 경로에 graft하는 것만 막는다. 원출처 [COMMUNITY] 정성, 구현·엔진·표본·기제 N/A, 재검토 조건 미정의(§9 예외 D-2 α). 같은 episode 전체 donor 재생은 K3 밖이지만 **허용이 아니다** — 비재생 새 전략은 P2 HOLD 적용, 재생 계열의 허용 근거는 F0 fast lane 승인뿐이다. EXP-007은 소급 판정 없는 일관성 사례.

- **HYP-0030 / TEST-0008: LOCAL_FAILED.** target cash·HIRE·tiles는 회복했지만 target 0/0/2, pool 새 패배 2셀. G1/G3/G4/G5 FAIL, G2 PASS. exact B schedule 폐기; 결과를 보고 seed 추가·factor 쪼개기 금지.
- **HYP-0006:** 현재 점수 우위와 clone-preempt 자체의 causal 효과는 별개다. parent 은퇴로 원래 hosted A/B는 N/A.
- **HYP-0007:** 두 슬롯 보완성 INCONCLUSIVE. 09-12 표본의 공통 상대 이름은 3명뿐이었다. 새로운 paired episode 판독은 아직 하지 않았다.
- **HYP-0031 / EXP-011:** LOCAL_SUPPORTED(attribution only).482 units 귀속, frozen card REPAIR_AUTHORIZED. 독립 검토 완료. EXP-012는 허용 범위로 success 달성 불가여서 사전등록 불가 종결. [결과](reports/codex/20260918-EXP011-RESULT.md).
- **HYP-0032 / EXP-013:** state-conditioned HIRE recovery, r3 dabe80a0…0cd9f / 실행 BLOCKED. P1c 제한 검토는 실행 가능한 수정 가설을 고르지 못했지만 HIRE·접전·donor 전략 전체를 기각하지 않는다. 6개 지적의 문서 수정 및 C1 scope 정리 반영; 구현 검증은 미실행.
- **09-14 community 제안:** 당시 HYP-0031..0033 표기는 역사적 예약 표기다. 현재 HYP-0031/0032는 위 두 카드의 공용 원장 ID다. EXP-009/010 제안과 혼동하지 않는다.
- **09-15 R10 정정:** 상대 MELON의 `yield_units` 합은 수확 readiness가 아니다. R10의 현재 재고 추가 SELL과 우리 maturity trigger·shift/repay 설계를 분리한다([원문 정정](proposals/codex/20260914-community-trends-plan-update.md)).
- **KILLS 유지:** pure PPO, 네 번째 땅, GOOSE 등은 항목별 재개 조건 확인 전 착수하지 않는다.

### (과거·09-20판) 제출 운영

최신 2개만 남고 새 제출은 먼저 올린 것을 은퇴시킨다. (09-20 당시 순서 `[EXP-007, yhay81-exact 56330776]` — **폐기된 과거 값. 현재 FIFO 는 위 '현재 상태' 표**.) 남길 bot 이 나중에 올린 쪽이 되도록 순서를 정한다. 최종 순위는 마감 후 약 2주 경기의 Bradley-Terry(evaluation.md) — 마감 전 점수 이력 손실의 비용은 작다. hosted A/B 는 두 bot 모두 24h 경과 후, 100점 이상 차이만 판단에 쓴다.
**약한 EXP-007만 교체할 수 있다고 가정하면 더 강한 EXP-006을 잃는다.**

- 최종 후보 pair가 통과하기 전 현재 두 제출 유지가 기본이다. C 하나만 올릴 때도 은퇴할 EXP-006 대비 근거를 검토한다.
- 제출마다 정확한 전후 ID와 이력 손실을 기록하고 사람 승인 후 실행한다. 이번 계획 승인은 제출 승인이 아니다.
- 동일 tar 재제출은 이전 ID·경기 이력을 복구하지 못한다. 점수 reroll용 duplicate 제출 금지.
- 09-27 00:00 KST 새 전략 중단 → 09-28 18:00 freeze → **09-29 18:00 최종 제출 완료 목표**.
- 충분한 후보가 없으면 현재 A/B를 유지한다. 날짜를 맞추려고 gate를 낮추지 않는다.

### (과거·09-20판) 다음 agent가 확인할 exact artifact

- parent: `coordination/proposals/claude/exp006/submission.tar.gz`, SHA `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721`.
- 다른 활성: `releases/public-thomas-replay-router-v2-exact/submission.tar.gz`, SHA `8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180`.
- EXP-008 판정: `evidence/raw/EXP-008/verdict.json`, SHA `9e8cabf4020607abf193ded71071807a8bc9165cba2a95c03180c8a291622d43`.
- 결과: [EXP008-RESULT](reports/codex/20260914-2025-EXP008-RESULT.md), [GATE-SPLIT](reports/codex/20260914-2043-GATE-SPLIT.md).

정정 이력 2026-09-15: 09-13판의 날짜·점수·EXP-008 대기 상태를 최신 근거로 교체했다. 과거 내용은 Git 이력에 남는다. `coordination/CURRENT.yaml`은 구현되지 않았으므로 현재 경로로 가정하지 않는다.

정정 2026-09-18: EXP-011 r2 SHA `8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e`의 §D-1 한정은 사용자 승인으로 발효했다. 위 C1 분기표의 범위 승인 전 대기 조건은 충족됐지만 C0 판정·독립 결과 검토·EXP-013 실행 승인 조건은 남는다. EXP-013 코드·counter는 이번 작업에서 추가하지 않는다.

EXP-011 결과 정정 2026-09-18: 1603 checks PASS, S1 64/64·S2 416/418·record별 단독최다16/16. 사후 엔진 검산464 events/44 loss events에서 모든 소멸이 carried−room과 일치. card의 REPAIR_AUTHORIZED는 설계 자격만 의미하며 실행·release 승인은 아니다. [Antigravity handoff](proposals/codex/20260918-EXP011-ANTIGRAVITY-HANDOFF.md), [owner 사실 정정안](proposals/codex/20260918-EXP011-OWNER-CORRECTIONS.md).

종결 갱신 2026-09-18: [Antigravity 검토](reports/antigravity/20260918-EXP011-REVIEW.md) 및 [Claude 인수](reports/claude/20260918-EXP011-REVIEW-ADJUDICATION.md) 확인. 이전 문단의 독립 검토 대기 상태는 해소됐다. [Coordinator 종결·우선순위 및 owner 정정안](proposals/codex/20260918-EXP011-CLOSURE-PRIORITY.md) 참조. 평균단가 환산을 coin 상한으로, noop횟수/items 비율을 가치비로 사용하지 않는다. P2 HOLD/release FAIL과 EXP-013 미승인은 유지한다.

P1c 정정 2026-09-18: HIRE pre/action/post 정렬을 재검산했다. 세 패배의 HIRE 실패는 상관이며 원인 확정이 아니다. EXP-011 verify-only는 read-only로 수정했고 live identity INVALID에도 원본 aggregate SHA는 보존된다. [owner 인계](proposals/codex/20260918-P1C-GEMINI-CORRECTIONS.md). 새 경기·EXP-013 구현·실행 없음.

P1c 제한 검토 종결 2026-09-18: commit `f64e37a`의 32/32 bounded assertions와 [정정 보고서](reports/codex/20260918-P1C-BOUNDED-EVIDENCE.md)를 Coordinator 상태에 반영했다. 110106409/109802471의 PLACE MILK는 실제 예치됐고, 109831239의 STRAWBERRY5/WHEAT3은 최종 전에 매도됐으며, 109856629의 action718 직전에는 관련 재고 운반자가 shed access 밖이어서 즉시 DROP 대안이 불가능했다. 이는 해당 세 설명의 반박일 뿐 HIRE·접전 개선·상위 donor 행동 활용 전체의 기각이 아니다. exact collection window/submission/artifact 연결은 N/A이고 raw replay의 action 전후 관측과 분리한다. 109831239 metadata 확보는 미래 판단에 유용할 수 있으나 자동 최우선 작업으로 등록하지 않는다. P2 HOLD, release gate FAIL, EXP-013 미승인을 유지한다. [Gemini owner exact 정정안](proposals/codex/20260918-P1C-BOUNDED-CLOSURE-GEMINI.md).
