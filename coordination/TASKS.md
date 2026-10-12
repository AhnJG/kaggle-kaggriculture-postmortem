# TASKS — 작업 원장 (append-only)

편집 전에 `task id · 소유 경로 · 예상 산출`을 여기 적는다.

| task id | 날짜 | agent | 소유 경로 | 무엇 | 상태 |
|---|---|---|---|---|---|
| CALIB-20260929 | 2026-09-29 | Codex | `experiments/calib/` `coordination/reports/codex/` `coordination/hypotheses/codex/` | c26·d157 로컬/hosted 평가 보정 및 d157 대체 최소 기준 제안; 새 경기·제출 없음 | DONE — 20260929-1120-CALIB.md |
| KAGRI-001 | 2026-09-06 | cowork(claude-opus-5) | `environment/` `evidence/` `coordination/` `AGENTS.md` | S1~S3: 계정 확인 · 엔진 고정 · 폴더 골격과 지침 | DONE |
| KAGRI-002 | 2026-09-06 | cowork | `tools/smoke.py` | S4 공식 3봇 720턴 양 좌석 완주 | **DONE** |
| KAGRI-003 | 2026-09-06 | cowork | `tools/instrument.py` | S6 무음 실패 4개 카운터 | **DONE** |
| KAGRI-004 | 2026-09-06 | cowork | `tools/arena.py` `configs/paired_seeds.txt` | S7 페어드 아레나 (시드 단위 CI) | **DONE** |
| KAGRI-005 | 2026-09-06 | 서브에이전트(Opus)+cowork 검증 | `main.py` | S8 v0 — 게이트 3종 PASS, starter 40/0/0 | **DONE** |
| KAGRI-006 | 2026-09-07 | **Gemini** | `opponents/public/` `environment/LICENSES.md` | 공개 상위 봇 4개 확보 및 검증 — 지시서 `coordination/proposals/gemini/BRIEF_opponents.md` | **DONE** |
| KAGRI-007 | 2026-09-06 | cowork | `tools/instrument.py` | 계측기 귀속 버그 수정(호출 순서 기반) | **DONE** |
| KAGRI-008 | | Codex | `main.py` | S9~S11 확대 스트레스 + S12~S14 패키징 | 미착수 |
| KAGRI-009 | | **Codex** | `main.py` `src/` `experiments/` | v1 면적 확장 — 지시서 `coordination/proposals/codex/BRIEF_v1_land.md` | **다음 작업** |
| KAGRI-010 | | Codex | `tools/extract_tape.py` | 테이프 추출 + bank-reproduction gate (선택) | 미착수 |
| KAGRI-011 | 2026-09-07 | cowork | `coordination/` `AGENTS.md` | buzz 폐지 -> reports/proposals 구조로 정리 | **DONE** |
| KAGRI-009 | 2026-09-07 | Codex | `main.py` `src/` `experiments/` | v1 면적 확장 구현·고정 표본 평가 | **진행중** |
| KAGRI-012 | 2026-09-08 | Codex | `tools/arena.py` `experiments/results/` `coordination/reports/codex/` | EXP-001 stage 2·3 재실행 및 provenance 강화 | **DONE** |
| KAGRI-015 | 2026-09-08 | Codex | `main.py` `tools/` `experiments/` `evidence/HYPOTHESES.md` `coordination/reports/codex/` | EXP-002 crop transition 사전등록·평가 | **DONE — FAILURE** |
| KAGRI-014 | 2026-09-08 | Gemini | `private_artifacts/replays/top/` `private_artifacts/tapes/` | 리플레이 수집 및 지표 추출 (Task A, B, C) | **DONE** |
| KAGRI-016 | 2026-09-09 | Codex | `main.py` `tools/` `experiments/` `coordination/reports/codex/` | EXP-003 흡수량 정합 사전등록·평가 | **DONE — correction gate FAILURE** |
| TEST-0008-EXEC | 2026-09-14 | Codex | `experiments/candidates/exp008_opening_liquidity/` `experiments/results/` `evidence/raw/EXP-008/` `coordination/reports/codex/` | EXP-008 고정 326셀 parent 선기록·candidate 판정 | **DONE — FAILURE** |
| GATE-SPLIT-20260914 | 2026-09-14 | Codex | `tools/instrument.py` `tests/` `releases/` `coordination/reports/codex/` | release gate 분리와 release source 추적 | **DONE** |
| DEADLINE-PLAN-20260915 | 2026-09-15 | Codex (사람 위임 Coordinator) | `coordination/BOARD.md` `coordination/HANDOFF_CURRENT.md` `plan/` 현재 계획·포인터·과거 계획 표지, `coordination/proposals/codex/` `coordination/reports/codex/` `coordination/hypotheses/codex/` (원장은 updater만) | 최신 기록·공식 일정 대조, BOARD 갱신, 마감까지 실행 계획 작성; 실험·제출 없음 | DONE |
| PUBLIC-PLAN-REVIEW-20260915 | 2026-09-15 | Codex + 독립 검토 3개 | `coordination/reports/codex/20260915-independent-*` `coordination/hypotheses/codex/` (원장은 updater만) | 계획 누락·공개 corpus·수집 방식 독립 검토와 근거 재확인; 개선 제안 보고 | DONE — 개선 미적용, 보고 `20260915-independent-review.md` |
| PUBLIC-PLAN-APPLY-20260915 | 2026-09-15 | Codex integrator + collector/plan 독립 agent (사람 위임) | `scripts/fetch_kaggle_updates.py` 관련 `tests/`, `plan/` 현재 계획, `coordination/BOARD.md` `coordination/HANDOFF_CURRENT.md`, R10 제안·docs 정정, `coordination/reports/codex/` `coordination/hypotheses/codex/` | 수집 실패 보존·SDK·R10 정정, P1 source triage/release preflight 반영 및 독립 검증 | DONE 09-16 — 13 tests·독립 검증 PASS, 실제 P1 실행 대기; `20260916-VET-APPLY.md` |
| P0-OWNER-RECORD-SYNC-20260916 | 2026-09-16 | claude(cowork) | `experiments/registry.csv` `evidence/HOSTED_LEDGER.md` `evidence/FACTS.md` `coordination/TASKS.md`(자기 행) | EXP-008 결과·registry·hosted ledger 동기화 — `coordination/proposals/codex/20260915-owner-record-sync.md` 1~6 적용 | DONE — 보고 `coordination/reports/claude/20260916-1710-P0-OWNER-RECORD-SYNC.md` |
| P1B-CURRENT-MANIFEST-REVIEW-20260916 | 2026-09-16 | claude(cowork) | `coordination/reports/claude/`(자기 보고서) `coordination/proposals/claude/`(자기 제안) | 실제 `experiments/results/p1_release_preflight/manifest.json`(Codex 소유) 검토 — 재현 대상·seed·시간분모·parent-only 판정·제출전 체크리스트 대조, 3건 proposal 제안, 2건 사람 결정 대기 BLOCKED | DONE(검토) — 실행 없음. 보고 `coordination/reports/claude/20260916-1745-P1B-CURRENT-MANIFEST-REVIEW.md`, 제안 `coordination/proposals/claude/20260916-p1b-manifest-contract-resolution.md` |
| P1a-SOURCE-TRIAGE | 2026-09-16 | Gemini | `analysis/public_source_triage/` `docs/` `coordination/reports/gemini/` | P1a: 공개 자료 인벤토리(51/18건) 정밀 판독 및 R10/Day3-Cow triage | **DONE** |
| KAGRI-014-20260916 | 2026-09-16 | Gemini | `private_artifacts/` `scripts/` `coordination/reports/gemini/` `coordination/proposals/gemini/` | Task 1 리더보드 스냅샷(9,234팀, Sian 1726.6 / 2007위) 및 Task 2 상위 10팀 50판 리플레이 수집/통계 파싱 완료, BOARD/LEDGER 동기화 제안 | **DONE** |
| EXP-025-V171-HOSTED | 2026-09-26 | Antigravity | `analysis/v171_hosted_20260926/` `private_artifacts/v171_hosted_20260926/` `coordination/reports/antigravity/` | v171 hosted 경기 107판 수집 및 상대 지문 분석 | **DONE** |



## KAGRI-012 — EXP-001 stage 2·3 재실행 `[완료 2026-09-08]`
담당 Codex · 브리프 `coordination/proposals/codex/BRIEF_exp001_rerun.md`
저장된 결과 6건이 현재 `main.py` 이전 산출물이라 재현 실패. stage 1(timing prior)만 유효.
arena.py 에 `parent_sha256`/`agent_*_sha256`/`engine_sha256` 기록 추가 포함.

## KAGRI-013 — EXP-004 동물 레이어 `[P0 · 다음]`
담당 Codex · `coordination/proposals/codex/BRIEF_exp004_animals.md` (2026-09-10 전면 재작성)
근거 `evidence/PASS_DIAGNOSIS.md`. 동물 = 남는 액션(42%) 흡수 장치. parent 는 v2c_c3_strawberry30.
담당 Codex · 브리프 `coordination/proposals/codex/BRIEF_exp002_animals.md`
근거 `evidence/ENGINE_ANIMALS.md`. stage A(동물구성) → B(일꾼) → C(비료용도) → D(200시드 대조).
GOOSE 제외(K9), SE 구획 제외(K1). **v1 은 제출하지 않는다** — v0 레이팅 314.8 / 상금 경계 2764.0.

## KAGRI-014 — 정찰 루틴 (리더보드 일일 + 리플레이 주2회) `[반복]`
담당 Gemini(Antigravity, 맥 로컬) · `coordination/proposals/gemini/BRIEF_recon.md` (2026-09-10 재작성)
Kaggle CLI 와 자격증명이 맥에만 있어 위임 불가. 아직 보고 없음.

## KAGRI-015 — EXP-002 작물 전환 `[완료 2026-09-09 · promotion FAILURE]`
승격 실패(4봇 0/0/400)이나 탐색 지표 전진(v1 18,600 → c3 42,050).
`AGENTS.md §7.1b` 에 따라 c3 를 다음 parent 로 채택.
⚠️ 이 카드는 MELON 을 최적화했는데, MELON 시즌 흡수량은 30개다 → KAGRI-016 에서 정정.

## KAGRI-016 — EXP-003 흡수량 정합 `[보류 — KAGRI-013 뒤]`
담당 Codex · `coordination/proposals/codex/BRIEF_exp003_absorption.md`
근거 `evidence/ABSORPTION.md`. 선행 버그픽스(MELON 30칸→3칸) + stage A~D.
⛔ `BRIEF_exp003_execution.md` 는 폐기.

## KAGRI-017 — 상점 조건부 분기 `[보류 · 순서 미정]`
상위 봇 2종이 초기 해금 상점으로 720턴 플랜을 분기한다. 우리는 `unlocked_shops` 를 0회 읽는다.
KAGRI-016·013 뒤로 둘지 앞당길지 사람이 결정한다.

## KAGRI-018 — 플레이북 검토 · ABSORPTION 정정 · AGENTS.md 개정 `[완료 2026-09-09]`
담당 cowork · 보고 `coordination/reports/cowork/20260909-1930-KAGRI-018.md`
상점 해금 주기 오류(4일/7개 → **3일/8개**) 엔진 판정. 시즌 파이 160,035 → **206,190**.
`BRIEF_exp003_absorption.md` **부록 A-2 고정 cap 폐기 → 부록 B 동적 cap**.
`AGENTS.md` R1~R8 추가, `BOARD.md` v0 제출 이후 상태로 갱신.
⚠️ KAGRI-017 우선순위 재검토 필요 — 동적 cap 이 `unlocked_shops` 배관을 stage B 에서 이미 깐다.

## TEST-0008 — EXP-008 사전등록 (opening liquidity) `[DONE 2026-09-14]`
담당 claude · 보고 `coordination/reports/claude/20260914-1521-EXP008-PREREGISTERED.md`
`coordination/proposals/codex/EXP-008-opening-liquidity.md` BLOCK 해제.
카드 `experiments/cards/EXP-008-opening-liquidity.md` sha256 `e0e93652991005514bb37f11cf9c69be6d07739594cfee4760ac8792ff30773a` (중복 ID 제거 후).
G4 = 셀별 `candidate <= parent` (326셀) · G5 = 326셀 각각 · pool = `*-replay.json` 47개.
G1 = `env.steps[index]` observation = 해당 action 처리 **후** 상태 (2026-09-14 06:35 UTC 정정,
보고 `coordination/reports/claude/20260914-1536-EXP008-TIMING-CORRECTION.md`).
G1/G2/G3/G5 임계와 `one_change`·`seeds`·`seats` 는 변경 없음.
⚠️ candidate 미구현 · 실험 미실행. 다음은 Codex 재검토 → 구현 → SHA freeze → parent 326셀 baseline 선기록 → 실행.
2026-09-16 추가 (claude, P0 owner-record-sync): candidate 구현·SHA freeze·326셀 실행 **완료** (2026-09-14) —
**FAILURE**, exact B schedule 폐기. 결과 `coordination/reports/codex/20260914-2025-EXP008-RESULT.md`,
verdict `evidence/raw/EXP-008/verdict.json` sha256 `9e8cabf4…22d43`, registry `experiments/registry.csv` EXP-008 행 갱신.
카드 본문(사전등록 yaml·§A~§C·`## 결과` 자리)은 frozen sha256 `e0e93652…773a`를 보존하기 위해 미변경.

## REVIEW-2026-09-14 — 검토 피드백 5건 처리 `[진행중]`
담당 claude · 보고 `coordination/reports/claude/20260914-1945-REVIEW-FEEDBACK-BATCH.md`
완료: EXP-008 카드 중복 ID 제거(`--strict` exit 3→0, card sha256 `e0e93652…773a`, commit `0291151`) ·
registry 4열 추가와 EXP-006/007/008 행 · 미추적 카드·소스 추적 (commit `64af7d7`).
이관: `WORK_ORDER_EXP-008_execution.md`, `WORK_ORDER_gate_split_and_release_tracking.md` → **Codex 착수 대기**.
2026-09-16 추가 (claude, P0 owner-record-sync): 위 이관 두 건 모두 **완료로 연결** —
`WORK_ORDER_EXP-008_execution.md` → `TEST-0008-EXEC` 행(DONE — FAILURE, 2026-09-14),
`WORK_ORDER_gate_split_and_release_tracking.md` → `GATE-SPLIT-20260914` 행(DONE, 2026-09-14).
이 줄은 두 work order가 그 시점 이후 실제로 착수·완료됐다는 연결 기록이며 과거 상태 서술 자체는 고치지 않는다.
`PROPOSAL_20260914_board_handoff_sync.md` → **코디네이터 적용 대기**.
⚠️ 최신 hosted snapshot N/A · 두 슬롯 비상관 재판독 계획 미고정(별도 카드).
2026-09-14 10:47 UTC 추가: 사람 제공 hosted snapshot 기록 — EXP-006 **1896.9**(−18.7) · EXP-007 **1647.4**(−172.4).
`evidence/HOSTED_LEDGER.md` 갱신, `experiments/registry.csv` hosted_score 갱신,
BOARD 표 교체 문구는 proposal `P0` 에 추가. ⚠️ EXP-007 하락폭이 EXP-006 의 9.2배 — 슬롯 교체 전 판독 계획 고정 필요.
| P1B-INDEPENDENT-VERIFICATION-20260916 | 2026-09-16 | antigravity (독립 검증자) | tools/instrument.py, experiments/results/p1_release_preflight/manifest.json | P1b 릴리스용 manifest와 검사 도구가 독립적으로 무결성(SHA), 측정값 포함 여부, 판정 분리, 그리고 고정 기준 적용을 준수하는지 런타임 수정 없이 검증 | DONE — 도구/Manifest는 PASS, 단 오너 5개 미확정 항목으로 인해 실제 Preflight는 BLOCKED 판정, 보고 20260916-1746-P1B-INDEPENDENT-VERIFICATION.md |

## P1B-13EP-SCOPE-APPROVED-20260916 — Codex

- 소유: experiments/results/p1_release_preflight/ 및 coordination/reports/codex/20260916-P1B-13EP-SCOPE-APPROVED.md
- 상태: DONE — Claude·Antigravity 동일 manifest/time 기준 승인 뒤 13/13경기 실행 완료. LOCAL FAILURE, 독립 결과 검증 PENDING.
- 검증: 13/13 `DONE/DONE`, gated parent 16/16 zero gate FAIL, Identity/Runtime/Isolation/License PASS, Schema FAIL, strict 30 entries PASS.
| P1B-RESULT-INDEPENDENT-VERIFICATION-20260916 | 2026-09-16 | antigravity | `experiments/results/p1_release_preflight/` | P1b actual parent A preflight 결과(13 cell JSON) 독립 재계산 및 무결성 검증 | DONE(검증) — 독립 검증 완료된 LOCAL FAILURE, 보고 `coordination/reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md` |
| P1B-CORRECTNESS-PREREG-20260916 | 2026-09-16 | claude(cowork) | `experiments/cards/`(EXP-011 신규) `evidence/FACTS.md` `coordination/proposals/claude/` `coordination/reports/claude/` `coordination/TASKS.md`(자기 행) `HYPOTHESES.md`(updater 경유) | P1b 독립 결과 검증 상태 동기화 + `shed_discarded` 원인 귀속 진단 카드 사전등록 (코드 구현·경기 실행 없음) | DONE(사전등록) — **BLOCKED_NEEDS_INSTRUMENTATION**. 카드 `EXP-011-shed-discard-attribution.md` sha256 `daabcd0d1386b95559d3433bd410c8b06a09d37f6a1407a5427e2c8c2164ddf2` (HYP-0031/TEST-0011). repair card 미승인 — 원인 미특정. 제안 `20260916-p1b-status-sync-patches.md` `20260916-EXP011-codex-implementation-handoff.md`, 보고 `coordination/reports/claude/20260916-2035-P1B-CORRECTNESS-PREREG.md` |
| P1C-MARGIN-AND-GATE-SCOPE-20260916 | 2026-09-16 | claude(cowork) | `evidence/FACTS.md` `coordination/proposals/claude/` `coordination/TASKS.md`(자기 행) | correctness 경로의 비용/편익 근거 확보 — 기존 hosted 표본 재분석(F-T17)과 공개 parent 상속 증거(F-T16), P1c 축소 work order 및 gate 범위 결정 제안 발행 | DONE(제안) — 실행·제출 없음. `WORK_ORDER_20260916_P1C_MARGIN_DISTRIBUTION.md` sha256 `b6e07ab97aef4fe6bbbd488edcdb4c2ed3c5d1bc159419da0dc18e01fc5a27d2`, `WORK_ORDER_20260916_GATE_SCOPE_DECISION.md` sha256 `9a408c065d40a083582e4c2c82d8aa57a1cc554f6fb6fe9e9de4c39266b2d0ab`. 결정 기한 09-27 00:00 KST, 사람 승인 대상 |
| BRONZE-TARGET-REPLAN-20260916 | 2026-09-16 | claude(cowork) | `coordination/proposals/claude/` `coordination/TASKS.md`(자기 행) | 사람 목표 변경(최소 동메달) 반영 — 메달 경계 수치화, 슬롯 운용 재설계, 우선순위 재배치, EXP-007 무승부 card 보류 판단 | DONE(제안) — `20260916-BRONZE-TARGET-PLAN.md` sha256 `1ac31cf31d5d15bce6e9272c134bd32d7bbba6af11c9a0986bc12ab423c5b79a`. gate 범위 독립 검토자 Codex 지정 반영. 사람 승인 대상: yhay81-exact 재제출 |

| TOP10-IMITATION-REVIEW-20260916 | 2026-09-16 | codex | `coordination/proposals/codex/20260916-TOP10-IMITATION-PLAN.*`, `coordination/reports/codex/20260916-2210-TOP10-IMITATION-REVIEW.md`, updater event | Claude 답변 검토·조건부 실행계획, 코드·대전·제출 없음 | DONE(검토·계획) — 새 실험은 S0 전 BLOCKED |

| TOP10-DONOR-REPRO-20260916 | 2026-09-16 | codex | tools/top10_donor_inventory.py, tools/reproduce_replay.py, tests/test_reproduce_replay.py, experiments/results/top10_donor_20260916/, private_artifacts/top10_donor_20260916/ | 사용자 직접 요청: 최신 donor inventory 및 원래 양측 경기 재현; 전략 실험 아님 | DONE — top10/20 submissions, 5 original games exact PASS; 새 정책 성능 N/A |

| DONOR-ROUTE-ANALYSIS-20260916 | 2026-09-16 | codex | tools/analyze_donor_routes.py, tests/test_analyze_donor_routes.py, experiments/results/top10_donor_routes_20260916/, coordination/reports/codex/20260917-1640-DONOR-ROUTES.md | 기존 고정 5경기 행동·직전 상태 비교, 새 arena/후보 없음 | DONE — 반복 opening 및 pre-action state 비교; causal/새 상대 성능 N/A |

| DONOR-VALIDATOR-20260917 | Codex | DONE | 재현 validator23 checks 및 negative control PASS; HYP-0032 owner용 BLOCKED_DRAFT 작성 | coordination/reports/codex/20260917-1710-DONOR-VALIDATOR.md |

| COORDINATOR-CORRECTNESS-PATH-20260917 | Codex Coordinator | DONE | 실행 경로·BOARD 변경안 작성, 미적용·미실행 | coordination/reports/codex/20260917-COORDINATOR-CORRECTNESS-PATH.md |

| EXP011-ATTRIBUTION-20260918 | Codex | 검토중 | 승인된 구현·30 focused/68 full tests·13경기 실행 완료, attribution PASS, Antigravity 독립 검토 대기 | coordination/reports/codex/20260918-EXP011-RESULT.md |

| P1C-AUDIT-VERIFY-GUARD-20260918 | Codex | DONE | 77 replay HIRE 재검산·read-only verifier 수정·3 tests PASS; owner 정정 대기 | coordination/reports/codex/20260918-P1C-AUDIT-VERIFY-GUARD.md |

| P1C-BOUNDED-EVIDENCE-20260918 | Codex | DONE | 제한 검토 현재 근거 부족; 32 assertions PASS·strict32 PASS; proposal/새 경기/구현 없음 | coordination/reports/codex/20260918-P1C-BOUNDED-EVIDENCE.md |
| PUBLIC-SOURCE-FETCH-20260918 | 2026-09-18 | Gemini | docs/code/ docs/discussion/ | 사용자 요청: 현재 시간 기준 최신 공개 코드 및 discussion 수집 완료 (16건) | DONE |
| F0-STAGE-BC-20260919 | antigravity | DONE | 단계 B 87개 다운로드 및 추출/검증 완료, full_match 0건 확인, 단계 C 생략 | coordination/reports/antigravity/20260919-1128-F0-STAGE-BC.md |
| F0-PUBLIC-EXACT-20260919 | 2026-09-19 | Codex | `tools/build_public_exact.py` `releases/public-{alperen,lynnsakurai,tetsutani}-*-exact/` `experiments/results/f0_public_exact_20260919/` `coordination/reports/codex/` `coordination/hypotheses/codex/` (원장은 updater만) | 공개 notebook P1-P3 exact 재현, 후보별 22경기 gate, PASS 후보 round-robin; 제출 없음 | DONE — 3/3 local gate PASS, 보고 `20260919-1221-F0-PUBLIC-EXACT.md` |
| F0-LATEST-REBUILD-20260919 | 2026-09-19 | Codex | `tools/build_public_exact.py` `releases/public-{lynnsakurai-farming-score-v2,tetsutani-market-smart-farming}-latest-exact/` `experiments/results/f0_latest_rebuild_20260919/` `coordination/reports/codex/` `coordination/hypotheses/codex/` (원장은 updater만) | 최신 snapshot P2/P3 exact 재빌드, 후보별 22경기 gate, 지정 3쌍 진단; 제출 없음 | DONE — 2/2 기대 SHA 일치·local gate PASS, 보고 `20260919-1332-F0-LATEST-REBUILD.md` |
| F0-DIFFERENT-LINEAGE-20260919 | 2026-09-19 | Codex | `tools/build_public_exact.py` `releases/public-{hesoponyo,salemali7,aasim2003}-*-exact/` `experiments/results/f0_different_lineage_20260919/` `coordination/reports/codex/` `coordination/hypotheses/codex/` (원장은 updater만) | D1-D3 원문 exact 재현, 후보별 22경기 gate, P2/yhay81 고정 진단; 제출 없음 | 진행중 |
| P2-LOSS-ANALYSIS-20260920 | 2026-09-20 | Claude | `evidence/raw/p2_losses_20260920/` `coordination/reports/claude/` (원장은 updater만) | P2(56347732) hosted L/D 32 vs 대조 W 32 빈도 분석 — 문턱(A≥20%·A-B≥20%p) 통과 후보 0개 → "없음"; 개선 구현·제출 없음 | DONE — 보고 `20260920-0114-P2-LOSS-ANALYSIS.md` |
| EXP014-015-RUN-20260920 | 2026-09-20 | Antigravity | `analysis/exp014_015/` `coordination/reports/antigravity/` | EXP-014·015 사전등록 390경기 실행 및 집계 (B0 30, M14 30, M15 30, NP2 100, N14 100, N15 100); 판정·해석 없음 | DONE — 에러 0, 보고 `coordination/reports/antigravity/20260920-2130-EXP014-015-RUN.md` |
| EXP014R-RUN-20260920 | 2026-09-20 | Antigravity | `analysis/exp014r/` `coordination/reports/antigravity/` | EXP-014R 사전등록 260경기 실행 및 집계 (B0R 30, M14R 30, NP2R 100, N14R 100); 판정·해석 없음 | DONE — 에러 0, 보고 `coordination/reports/antigravity/20260920-2215-EXP014R-RUN.md` |

| C1-HOSTED-OPPONENT-MAP-20260921 | 2026-09-22 | Antigravity | analysis/c1_hosted_20260921/ coordination/reports/antigravity/ | C1 hosted 경기 수집 및 상대 지문 (prefix step 1~143) 추출 | DONE — 대조 통과, 148경기 중 거울전 6건, 보고 20260922-1716-C1-HOSTED-MAP.md |
| DAILY-PUBLIC-SCAN-20260922 | 2026-09-22 | Antigravity | analysis/daily_scan/20260922/ coordination/reports/antigravity/ | 09-22 공개 notebook 38개 스캔 및 09-21 EXTRACTION_FAILED 후보 17건 재검토(13건 SAME_FAMILY 승격 완료), 코드 확인 규칙 적용 | DONE — 보고 20260922-1855-DAILY-SCAN.md |

| FUNDAMENTAL-GAIN-20260923 | 2026-09-23 | Codex | `analysis/fundamental_gain_20260923/` (지시서 예외 허용), `coordination/reports/codex/20260923-FUNDAMENTAL-GAIN.md`, `coordination/hypotheses/codex/` | Q1 숫자 상한 먼저, Q2/Q3 연구 및 카드 초안; 제출/다운로드/releases 편집 없음 | DONE — 조건부 상한·2271 checks PASS·카드 초안, 보고 `20260923-FUNDAMENTAL-GAIN.md` |
| TOP-AGENT-REPLAY-COLLECTION-20260923 | 2026-09-23 | Antigravity | `private_artifacts/top_agents_20260923/raw/` `analysis/top_agents_20260923/` `coordination/reports/antigravity/` | 상위 3팀(DSM, Majkel1337, M & M & P & Q) 공개 리플레이 120개 수집 및 EXP-017 로컬 20경기 대조 지표 전수 집계 | DONE — 에러 0, 보고 `coordination/reports/antigravity/20260923-2000-TOP-AGENT-SNAPSHOT.md` |

| ABSORPTION-20260923 | 2026-09-23 | Codex | `analysis/absorption_20260923/`, `coordination/reports/codex/20260923-ABSORPTION.md`, updater HYP-0003/0016 | 기존 분석 resume: Q1~Q4 및 EXP018 초안, 소비 cap 비추천; releases/제출/다운로드 없음 | DONE — 6501 checks·hypothesis strict PASS; EXP018은 E2 자료·runtime freeze 미충족으로 DRAFT_BLOCKED_PREFLIGHT |
| DAILY-PUBLIC-SCAN-20260924 | 2026-09-24 | Antigravity | `analysis/daily_scan/20260924/` `coordination/reports/antigravity/` | 09-24 공개 notebook/script 47개 스캔, 코드 확인 4대 규칙 및 multi-file 보충 규칙 적용, 계보 분류 완료 (제출·경기 실행 없음) | DONE — 보고 `coordination/reports/antigravity/20260924-1510-DAILY-SCAN.md` |
| EXP016-017-HOSTED-MAP-20260924 | 2026-09-24 | Antigravity | `analysis/exp016_017_hosted_20260924/` `coordination/reports/antigravity/` | EXP-016 및 EXP-017 hosted 경기 345건 수집, 10경기 재현성 대조(10/10 PASS), 17개 참조 봇 기준 상대 지문 추출 완료 (제출·해석 없음) | DONE — 345경기 지문 완료, 대조 10/10 PASS, MIRROR_EXACT 0건, 보고 20260924-1610-EXP016-017-HOSTED-MAP.md |
| STEP91-BOT-ID-20260924 | 2026-09-24 | Antigravity | `analysis/step91_id/` `releases/public-ahmedberatozer-kaggriculture-v56-smarter-seeds-and-fertilizer-exact/` `coordination/reports/antigravity/` | hosted prefix_len=91 경기 137건 대상 34종 candidate 전수 측정, 최다 일치 봇 X(V56, e410_agent) 확정, exact release 빌드, E-5 gate 및 arena(vs EXP-016 12/0/8, vs EXP-017 10/0/10) 완료 (다운로드·제출·해석 없음) | DONE — 보고 20260924-1845-STEP91-ID.md |
| DP-HOSTED-MAP-20260924 | 2026-09-24 | Antigravity | `analysis/dp_hosted_20260924/` `private_artifacts/dp_hosted_20260924/` `coordination/reports/antigravity/` | demand-preserving 0924 계열 8개 submission hosted 경기 884건 수집, 거울전 분리, 4단계 720 step 대조(7/8 PASS), 44종 상대 지문 및 LB 점수 매핑 완료 (제출·해석 없음) | DONE — 보고 20260924-2155-DP-HOSTED-MAP.md |

| DP-LOSS-CAUSE-20260925 | 2026-09-25 | Codex | `coordination/reports/codex/20260925-0017-DP-LOSS-CAUSE.md`, TASKS 자기 행 | DP 지시서 시작 조건 확인; BOARD 갱신일/FIFO 충돌로 Coordinator 반환. Q1–Q5·카드·패널·제출 미실행 | BLOCKED — AGENTS §11; strict ledger PASS 36 |
| DP-LOSS-CAUSE-RESUME-20260925 | 2026-09-25 | Codex | `tools/dp_loss_cause.py`, `experiments/results/dp_loss_cause_20260925/`, EXP-018 카드, `analysis/exp018_panel/`, Codex 보고/event | 00:45 재개 지시; Q1→Q5 및 DP 80경기 하한 사전등록·검증, 제출 없음 | DONE — VERIFIED_NOT_ELIGIBLE_DP_FLOOR; 패널 23→28승, DP80 22/34/24=0.4875<0.50; 보고 20260925-1340-DP-LOSS-CAUSE.md; release·제출 없음 |
| DAILY-PUBLIC-SCAN-20260925 | 2026-09-25 | Antigravity | `analysis/daily_scan/20260925/` `coordination/reports/antigravity/` | 09-25 공개 notebook/script 17개 스캔, 코드 확인 4대 규칙 및 multi-file 보충 규칙 적용, 계보 분류 완료 (제출·경기 실행 없음) | DONE — 보고 `coordination/reports/antigravity/20260925-1415-DAILY-SCAN.md` |

| SEARCH-LOOP-20260925 | 2026-09-25 | Codex | tools/search_loop.py, tools/dp_counterfactual.py, tests/test_search_loop.py, experiments/search_20260925/, releases/public-newmeta-127ed3e6-exact/, Codex reports/events | User-approved v2.3; exact then tournament then calibration; worker6 sustained load; no submission | 진행중 |
| EXP021-MIRROR-EDGE-20260926 | 2026-09-26 | Codex | `tools/mirror_edge_exp021*.py`, `tests/test_mirror_edge_exp021*.py`, `experiments/mirror_edge_20260926/`, Codex reports | Coordinator-approved v2 four-arm continuation plus separate H2-prime gate; 5 workers; no submission/download/search-loop write | DONE — FAIL: baseline 0.50; H1a/H1b/H3 0.50, H4 0.33, no Stage-1 pass; H2-prime telemetry STOP 8/8 invalid |
| EXP022-H2P-RETEST-20260926 | 2026-09-26 | Codex | `tools/mirror_edge_exp022.py`, `tests/test_mirror_edge_exp022.py`, `experiments/mirror_edge2_20260926/`, Codex report | Human-approved 01:20 KST H2-prime import-only retest; 01:30 clarification permits harness-only repair; 5 workers; preserve EXP-021; no submission/download/search-loop write | DONE — STOP at smoke: unit 3/3 PASS; 8/8 valid/error0, O expected cash −25 vs actual −28 so our_mirror 0/2; screen 0 games |
| EXP023-STAGE3-20260926 | 2026-09-26 | Codex | `experiments/exp023_mirror_screen/`, `releases/mirror-screen-v171/`, `experiments/d3_gate_v2/result-exp023-v171.json`, Codex report | Human-approved 09:55 KST Stage 3; 5 workers; 4,000-game A–E confirmation, exact release, E-5, D3 gate v2; no submission/download | DONE — SUCCESS v171; A–E PASS, E-5 0.75 PASS, D3 PASS; report `20260926-1151-EXP023-STAGE3.md` |
| EXP024-ROUND2-20260926 | 2026-09-26 | Codex | `experiments/exp024_round2/`, `coordination/reports/codex/` | Human-approved 09-26; v171 parent round-2 mirror screen, exactly 5 workers; no submission/download/holdout | 진행중 — Step 0 input/environment/baseline validation |
| DAILY-PUBLIC-SCAN-20260926 | 2026-09-26 | Antigravity | `analysis/daily_scan/20260926/` `coordination/reports/antigravity/` | 09-26 공개 notebook 12개 스캔, 코드 확인 4대 규칙 및 multi-file 보충 규칙 적용, 계보 분류 완료 (제출·경기 실행 없음) | DONE — 보고 `coordination/reports/antigravity/20260926-1215-DAILY-SCAN.md` |
| EXP025B-NEARCLONE-20260926 | 2026-09-26 | Antigravity | `analysis/exp025b_nearclone/` `coordination/reports/antigravity/` | 127ed3e6 exact와 일치하는 상대를 만난 변형 팀의 에피소드 수집 및 승패 기록 | DONE — 검증 0 실패, 1397건 확보, 보고 `coordination/reports/antigravity/20260927-0100-EXP025B.md` |
| DAILY-PUBLIC-SCAN-20260927 | 2026-09-27 | Antigravity | `analysis/daily_scan/20260927/` `coordination/reports/antigravity/` | 09-27 공개 notebook 17개 스캔, 코드 확인 4대 규칙 및 multi-file/ARCHIVE_B85/SOURCE_PARTS 보충 규칙 적용, 계보 분류 완료 (제출·경기 실행 없음) | DONE — 보고 `coordination/reports/antigravity/20260927-1015-DAILY-SCAN.md` |
| DAILY-PUBLIC-SCAN-20260928 | 2026-09-28 | Antigravity | `analysis/daily_scan/20260928/` `coordination/reports/antigravity/` | 09-28 공개 notebook 14개 스캔, 코드 확인 4대 규칙 및 multi-cell ARCHIVE_PARTS 보충 규칙 적용, 계보 분류 완료 (제출·경기 실행 없음) | DONE — 보고 `coordination/reports/antigravity/20260928-0925-DAILY-SCAN.md` |
| EXP-040-TOP2400-COLLECT | 2026-09-28 | Antigravity | `analysis/top2400_20260928/` `coordination/reports/antigravity/` | LB>=2400 상대 25개 submission 의 hosted 경기 및 replay 수집 | DONE — episodes 750건, replay 743건, 보고 `coordination/reports/antigravity/20260928-1448-EXP040.md` |
| DAILY-PUBLIC-SCAN-20260928-EVENING | 2026-09-28 | Antigravity | `analysis/daily_scan/20260928/` `coordination/reports/antigravity/` | 09-28 오후 갱신분 포함 16개 스캔, DIFFERENT 계보(multi-route c94) 재출현 및 V53 신규 확인 (제출·경기 실행 없음) | DONE — 보고 `coordination/reports/antigravity/20260928-2255-DAILY-SCAN.md` |
| HOSTEDPM-20260929 | 2026-09-29 | Antigravity | `analysis/hosted_20260929pm/` `coordination/reports/antigravity/` | d157·c26 최신 실전 전적 수집(331건) 및 lb_scores.txt 기록, 무판단 보고 | DONE — 331건 전수 검증 PASS, missing 0, 보고 `coordination/reports/antigravity/20260929-0910-HOSTEDPM.md` |
| SURVEY300-20260929 | 2026-09-29 | Antigravity | `analysis/survey300_20260929/` `coordination/reports/antigravity/` | 상위 300위+비교군 355팀 경기 수집 카드 수행, 2,840경기 수집 및 2,572건 리플레이 확보, reward 불일치 0건 완료 | DONE — 보고 `20260929-1357-SURVEY300.md` |
| FP-PUBLIC-SIGNAL-20260929 | 2026-09-29 | Codex | `experiments/fp_signal/`, `coordination/reports/codex/20260929-1408-FP-PUBLIC-SIGNAL.md`, `coordination/hypotheses/codex/` | 비공개 55be 변형 패배의 공개 관측 신호 진단; 새 후보·경기 실행·제출 없음 | DONE — 43경기 30고정검사 통과0, HYP-0039 INCONCLUSIVE, strict39 PASS; 보고 `20260929-1408-FP-PUBLIC-SIGNAL.md` |
| DAILY-PUBLIC-SCAN-20260929 | 2026-09-29 | Antigravity | `analysis/daily_scan/20260929/` `coordination/reports/antigravity/` | 09-29 공개 notebook/script 10개 스캔, 코드 확인 4대 규칙 및 multi-file/ARCHIVE_PARTS/PAYLOAD_B85 보충 규칙 적용, 계보 분류 완료 (제출·경기 실행 없음) | DONE — 보고 `coordination/reports/antigravity/20260929-1615-DAILY-SCAN.md` |
| FP-CLOSE-LOSS-20260929 | 2026-09-29 | Codex | `coordination/reports/codex/20260929-1923-FP-CLOSE-LOSS.md` | d157 근소 패배에서 c26 행동 차이와 승패 반전을 기존 개발 표본으로 진단; 새 후보·제출 없음 | DONE — 43경기 재집계, 8경기 행동 점검, 반복 공개 신호 N/A; strict39 PASS |
