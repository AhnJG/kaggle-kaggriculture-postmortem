# EXP-006 — yhay81 복사본 + clone preemption (제출 후보)

hypothesis_id: HYP-0006
test_id: TEST-0006

사전등록 2026-09-11 12:17 UTC (Claude). 확인 실행 전 커밋. 커밋 후 seeds·임계 변경 금지.
사람 결정(2026-09-11): 공개 코드 파생물을 최종 슬롯에 써도 된다. 엔진 1.32.7 `bc8a5487…653e`.

```yaml
id:            EXP-006
parent:        releases/public-yhay81-shop-router-0909-exact/submission.tar.gz  # 40d2bc3986f4ed3e927c81842d399a58bf20b07b57858355da4b75c280fd7791, hosted 56147691
candidate:     coordination/proposals/claude/exp006/submission.tar.gz
               # sha256 1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721 (169,317 B, 결정론 재빌드 동일)
               # members main.py bba042e04cff32ab53be2c59c2f5cd9053c8de2bf31632e396ca8faa502896b2 (우리 파일)
               #         yh_base.py d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b (= parent main.py)
               #         actions.json 17d503f2fd20d59f9c0f14024d1e74a8add8bb9b5561d4d908b45deecb5495ef
               #         LICENSE.txt cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30
one_change:    parent 액션 A -> B = A + [상대 farm 공개 서명 거리 ≤ 6 AND 120 ≤ step < 680 일 때,
               STRAWBERRY/MELON/MILK/WOOL 중 이번 턴 SELL 이 없는 품목에 대해
               SELL min(projected_shed, 다음턴 계획량 − parent 가 이미 당긴 양, 30) 을 추가 (다음턴 계획량 − 당긴 양 ≥ 4 일 때만),
               다음 턴 tape SELL 에서 같은 양 차감]
               아이디어 출처 boatlee "V14 Clone Preemption"(공개 노트북), 구현은 독립 검토자 프로토타입(review4/candidate.py)과
               행동 동일 확인(8판 뱅크 완전 일치).
fixed:         [actions.json·yh_base.py 바이트 동일, farmer/hands 액션 전부, 라우팅, advance_sales, step 718 liquidate,
                WHEAT·FERTILIZER·CARROT·TOMATO·EGG 주문, 모든 BUY/HIRE/BUY_LAND 주문, 엔진 1.32.7]
hypothesis:    H1: 정확한 parent clone 상대 h2h 20판에서 W ≥ 18, L = 0 (파일럿 seeds 6001–6010: 20-0-0, 마진 +879~+3,254)
               H2: 비-clone 상대에서 승패 뒤집힘 없음 (파일럿 47테이프 seat0 94셀: 뒤집힘 0, 뱅크 변화 17셀)
opponents:     h2h = parent / tape pool = private_artifacts/tapes/*.json 47개, 풀 해시 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1
               public = boatlee f029fa0cb66a9eb509afbe44e3f59b800332d0419db91607183410e4089c4d19 · lynnsakurai 1dc166ae2bf0c56a44fac4482f469b8812968c4cb32459cb9860f5077897a7d4
                        raykkretzschmar 489f5d197527f107027626cce79d850fd2ca90edd43d94384b849b6511e27bdb · kaitofukami f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8
               self = candidate (validation episode 모사, path 로더)
seeds:         h2h [5201..5210] / pool [5101, 5102, 5103] / public [5101..5105] / self [5301, 5302]
               # pool·public 의 parent 결과는 EXP-005 원자료 재사용 (엔진 결정론 F-T4):
               # evidence/raw/EXP-005/pool_parent.jsonl 557f9360… · public_parent.jsonl d041bcd7…
seats:         both
metric:        G1 h2h W/D/L (20) · G2 풀 페어드 b(후보만 나은 셀)·c(parent만 나은 셀) (282) · G3 공개봇 후보 L (40)
               G4 안전 (풀+공개 322 페어드 셀): Σdiscard 차, 셀당 discard 증가 최대, Σend_units(PRODUCTS), Σend_animals, shed_unsold, manual_drop_lost
               G5 런타임: status≠DONE 수, guard 합, 후보 CPU s/episode 최대, p99 턴 ms 최대 · G6 self 2판 DONE
               진단: preempt 발동 턴·units (상대 유형별)
success:       G1 W ≥ 18 AND L = 0 · G2 c ≤ 1 AND c ≤ b · G3 L = 0 · G4 Σdiscard(후보) − Σdiscard(parent) ≤ 50 AND 셀당 증가 ≤ 10
               AND Σend_units(후보) ≤ Σend_units(parent) AND Σend_animals(후보) ≤ Σend_animals(parent) AND shed_unsold = 0 AND manual_drop_lost = 0
               · G5 status≠DONE = 0 AND guard 합 = 0 AND CPU ≤ 5.0 AND p99 ≤ 5.0 · G6 2/2 DONE      -> 제출 가능(사람 실행)
failure:       G1 L ≥ 1 OR G2~G6 중 하나라도 위반                                                    -> 제출 안 함
inconclusive:  G2~G6 통과 AND G1 L = 0 AND W < 18                                                     -> 제출 안 함, seeds 추가 금지
next_if_success: 사람 제출 -> hosted 판독(아래) -> EXP-007
next_if_failure: 제출 안 함. 원인 기록 후 EXP-007 = 자체 tape 생성기 v0
artifact:      빌드/판정 스크립트·원자료 evidence/raw/EXP-006/ · 하니스 sellaudit.py a4dc3443… (end_units PRODUCTS 한정, end_animals·preempt_counts 추가) · pool.py 0c6777df… · paired.py 7b23c71b…
```

## §7.5 체크리스트 (Ledger 제외 제출 전)
```
Identity:  tar sha256 1c478c24…9721 = 확인 실행에 쓴 clean-room 해제본의 멤버 4개 sha 와 일치 / 결정론 재빌드 동일        [PASS]
Schema:    루트 main.py · get_last_callable 마지막 callable = agent · __file__ 불사용 · guard 2종(예외 시 parent 액션)          [PASS]
Runtime:   CPU ≤ 5.0 s/episode (예산 1,200 s 의 0.4%) · p99 ≤ 5.0 ms                                                            [PASS: max 0.874 s · p99 0.86 ms · 첫 호출 516 ms(무경합)~713 ms(경합), actTimeout 1 s·overage 60 s]
Isolation: 빈 폴더 해제 → get_last_callable(raw, path) 로드 → starter 상대 720 steps DONE · path 로더 self 720 steps DONE     [PASS]
License:   L1 LICENSE.txt cfc7749b… · L2 yh_base.py = parent main.py · L3 NOTICE 없음 · L4 main.py docstring 에 변경·출처 고지 · L5 라이벌 테이프 미탑재 [PASS]
Ledger:    (제출 후) submission ID ↔ tar sha ↔ episodes                                                                            [ ]
```

## 은퇴 · 판독 · 이탈
- 은퇴: 제출 시 FIFO 로 v1-20260910 (56145245, 343.9) 은퇴. 복사본 56147691 은 유지 → 같은 창 A/B.
- §7.4: 복사본과 같은 계열이라 이 쌍은 최종 2슬롯 조건을 만족하지 않는다. 최종 쌍은 별도 카드에서 정한다.
- 판독 1 (제출 +24h, 한 CLI 출력): Δ = 후보 − 복사본. Δ ≥ +50 유지 / Δ ≤ −100 후보 폐기(복사본 유지 위해 다음 제출은 복사본 재제출 또는 두 개 연속 제출) / 그 사이 보류.
- 판독 2 (episodes·replay, 봇별 최근 20경기): 무승부 수, |뱅크 차| ≤ 5,000 박빙 수, TeamNames 가 ['Sian','Sian'] 인 판 수(분석에서 제외).
- 이탈: hosted 후보가 +24h 에 validation Error 또는 publicScore 없음 → 재제출 없이 로그 확인.

## 결과 — 2026-09-11 12:50 UTC · 판정 **SUCCESS** → 제출 가능 (사람 실행)

원자료 `evidence/raw/EXP-006/` · 판정 스크립트 `evidence/raw/EXP-006/judge_exp006.py` · 344판, 결측 0, 전부 720 steps DONE.

| 게이트 | 임계 | 값 |
|---|---|---|
| G1 h2h vs parent (20) | W ≥ 18, L = 0 | **20-0-0**, 마진 +660 ~ +3,756 |
| G2 풀 282셀 | c ≤ 1, c ≤ b | b = 0, c = 0 (뱅크 변화 44셀, 점수 0.9787 = 0.9787) |
| G3 공개봇 40 | L = 0 | 40-0-0 |
| G4 안전 322셀 | Σdiscard 차 ≤ 50, 셀당 ≤ 10, 잔여 ≤ parent | discard 1,864 = 1,864, 셀당 증가 0, 종료 PRODUCTS·가축 0, shed_unsold 0, 수동 DROP 0 |
| G5 런타임 | DONE, guard 0, CPU ≤ 5 s, p99 ≤ 5 ms | 전부 DONE, guard 0, 0.874 s, 0.86 ms |
| G6 self 2 | 2/2 DONE | 2/2 (106,511 = 106,511 · 85,295 = 85,295) |

preempt 발동: parent 상대 20/20판(434턴, 4,288 units) · 공개봇 10/40판 · 테이프 46/282판 — 발동해도 승패 뒤집힘 0.

독립 검증(서브에이전트): tar 재해제 SHA 일치, 6판 뱅크 정수 단위 재현, direct-path 실행 DONE, 판정 스크립트 재계산 byte-identical → **제출 가능**.
- 각주(절차): G4 는 parent 원자료가 구정의(end_units 에 가축 포함)라 스크립트가 `end_units + end_animals ≤ parent end_units` 로 비교했다. 세 값이 모두 0 이라 카드의 두 부등식과 결과 동일.
- RISK(낮음): `_layer` 되갚기 루프 중 `int(order[2])` 예외 시 due 가 한 턴 남을 수 있음(344판 guard 0회). hosted vCPU·프로세스 구조는 로컬 실측 불가.
