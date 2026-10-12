# EXP-005 — X1 프로브: 로컬 테이프풀 점수가 hosted 레이팅을 예측하는가

hypothesis_id: HYP-0005
test_id: TEST-0005

사전등록 2026-09-11 00:40 UTC (Claude). 확인 실행 전 작성. 이 파일 커밋 이후 seeds·임계 변경 금지.
설계 근거 수치는 `evidence/FACTS.md` F-T7~F-T9 와 본문 §A. 모든 수치 `[LOCAL]` 은 엔진 1.32.7 `bc8a5487…653e`.

```yaml
id:            EXP-005
parent:        releases/public-yhay81-shop-router-0909-exact/submission.tar.gz   # sha256 40d2bc3986f4ed3e927c81842d399a58bf20b07b57858355da4b75c280fd7791, hosted 56147691
               # members main.py d6d74997dc5b… / actions.json 17d503f2fd20… / LICENSE.txt cfc7749b96f6…
candidate:     tar{ main.py sha256 dd41b6df36e5d88f654e428e12929db2ba8dcc9eafaac36a648ca8715348698c (우리 파일),
                    yh_base.py = parent main.py (d6d74997…, 바이트 동일), actions.json (17d503f2…), LICENSE.txt (cfc7749b…) }
one_change:    비입력 산출물 7종 {MELON,WOOL,MILK,STRAWBERRY,TOMATO,EGG,CARROT} 의 SELL:
               A = parent 의 테이프 SELL 줄 + advance_sales
               -> B = 해당 줄 제거 후 매 턴 ["SELL", item, projected_shed(item)] (price>=2), price*qty 내림차순, 전체 market 줄 [:10]
               step 718 은 parent liquidate 그대로. 예외 시 parent 액션 반환(guard 카운터 2종).
fixed:         [actions.json 13테이프 바이트 동일, farmer/hands 액션 전부(repair_weeds), ROUTE_STEP=144·SHOP_PLANS, FINAL_PLAN_STEP=648,
                WHEAT·FERTILIZER SELL 줄, BUY_SEED·BUY_PRODUCT·BUY_ANIMAL·HIRE·BUY_LAND 줄, step 718 liquidate, 엔진 1.32.7]
hypothesis:    H_local: 확인 seeds 에서 Δpool = score(X1) − score(parent) ≤ −0.10  (탐색 seeds 7,1000..1003 seat0: −0.234, b=3 c=58, n=235)
               H_steep: hosted Δrating = publicScore(X1) − publicScore(parent) ≤ −300   (선형 모형 예측 −643)
               H_flat:  hosted Δrating ≥ −120                                          (공개봇 모형 예측 ≈ 0)
opponents:     tape pool = private_artifacts/tapes/*.json 47개 (분석 입력, 제출물 미포함)
                 풀 해시 = sha256(concat(sort(각 파일 sha256 hex))) = 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1
               public = opponents/public/boatlee.py f029fa0cb66a9eb509afbe44e3f59b800332d0419db91607183410e4089c4d19
                        lynnsakurai.py 1dc166ae2bf0c56a44fac4482f469b8812968c4cb32459cb9860f5077897a7d4
                        raykkretzschmar.py 489f5d197527f107027626cce79d850fd2ca90edd43d94384b849b6511e27bdb
                        kaitofukami.py f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8
               h2h = parent
seeds:         tape pool [5101, 5102, 5103] / public [5101, 5102, 5103, 5104, 5105] / h2h [5101..5110]
seats:         both
metric:        1차 Δpool (같은 tape·seed·seat 셀 282개 페어드, 셀 점수 W=1 D=0.5 L=0), b=X1만 나은 셀 수, c=parent만 나은 셀 수
               진단: 공개봇 W/D/L(40판), h2h 점수(20판), 품목별 1코인 매도 units, hands 불일치 턴
               안전: exceptions, guard_counts, shed_unsold_units, manual_drop_lost_units, end_units, discard_units, agent CPU s/episode, p99 턴 ms
               hosted: Δrating (같은 CLI 호출 한 번에서 두 publicScore)
success:       Δpool ≤ −0.10 AND c − b ≥ 20 AND exceptions = 0 AND guard 합 = 0 AND shed_unsold = 0 AND manual_drop_lost = 0
               AND end_units = 0 AND discard ≤ 10 units/player-run AND CPU ≤ 5.0 s/episode AND p99 ≤ 5.0 ms  -> 제출 후보(사람 승인)
failure:       Δpool > −0.05 OR exceptions ≥ 1 OR guard 합 ≥ 1 OR shed_unsold ≥ 1 OR manual_drop_lost ≥ 1 OR end_units ≥ 1
               OR discard > 10 OR CPU > 5.0 OR p99 > 5.0  -> 제출 안 함
inconclusive:  나머지 (−0.10 < Δpool ≤ −0.05, 또는 Δpool ≤ −0.10 이지만 c − b < 20) -> 제출 안 함, seeds 추가 금지
hosted_read:   T = X1 제출 시각. T+24h 이후 첫 CLI 출력 1회로 판정 (X1 경과 ≥ 24.0h, 두 publicScore 모두 존재)
               Δrating ≤ −300 -> STEEP · Δrating ≥ −120 -> FLAT · 그 사이 -> WEAK. 재판독 없음.
next_if_success: 제출 -> hosted_read -> STEEP: EXP-006 = 테이프풀을 1차 게이트로 채택, k = Δrating/Δpool 기록
                                       FLAT:  EXP-006 = 로컬 게이트 수리(09-11 이후 hosted top-50 리플레이로 풀 재구성), 전략 튜닝 중지
                                       WEAK:  EXP-006 = 게이트 수리, 풀 판정은 |Δpool| ≥ 0.30 인 경우만 사용
next_if_failure: 제출 없음. 활성 슬롯 유지(v1 56145245). EXP-006 = 게이트 수리
artifact:      프로토타입 /home/claude/lab/cand/x1/ (클라우드) -> releases/exp005-x1-probe/ (Codex 빌드)
               결과 experiments/results/EXP-005/{pool_parent,pool_x1,public,h2h}.jsonl
               하니스 coordination/proposals/claude/harness/ sellaudit.py a3143902… · pool.py 0c6777df… · paired.py 7b23c71b…
```

## A. 왜 이 제출인가 — 세 축과 베팅

| 축 | X1 | 판단 |
|---|---|---|
| 레이팅 기대값 | parent 대비 음(−) — 탐색 Δpool −0.234 | 이 슬롯은 최종 슬롯이 아니다(마감 시점 마지막 2개). 팀 최고점(parent)은 불변 |
| 정보 획득 | 같은 창·같은 가족·한 가지 변경. 두 예측이 −643 vs ≈0 으로 갈린다 | **여기에 건다** |
| §7.4 비상관 | 낮음 — 같은 farm 테이프, X1 패배 ⊇ parent 패배 대부분 | 임시로 포기. 최종 2슬롯 카드에서 복원 |

지금 로컬 증거끼리 충돌한다: exact 두 점(v1 0.021 → 343.9, parent 0.962 → 2,188.4@7h 수렴 중)은 가파른 기울기를,
공개봇 4점(아래)은 순서가 뒤섞인 평평한 관계를 말한다. 남은 19일의 모든 후보 판정이 이 풀에 달려 있으므로
**어느 쪽인지 hosted 로 한 번에 가르는 것**이 지금 슬롯의 최대 가치다. X1 은 이미 존재하고 탐색 수치가 있는 가장 큰 단일 변경 대조다.

| 봇 (seed 1001, seat0, 47셀) | 풀 점수 | 리더보드 (09-10 23:16) |
|---|---:|---:|
| kaitofukami | 0.404 | 1,897.8 |
| boatlee | 0.447 | 2,834.0 |
| raykkretzschmar | 0.511 | 2,123.0 |
| lynnsakurai | 0.872 | 2,681.3 |
공개 코드 = 저자 제출물이라는 연결은 미검증 `[COMMUNITY]`.

## B. 기각한 대안

| 대안 | 기각 수치 |
|---|---|
| 무음 실패 수리 (시장 레이어) | 회수 가능 ≤7 units/run(≤120코인), 창고 미판매 0 (F-T7) → W/L 변화 0, 사실상 리롤 |
| X2 경합품만 즉시 매도 | 탐색 0.9617 → 0.7362, b=3 c=56 — X1 과 같은 방향, 대조 크기 동일 |
| X5 기준가 이상에서만 매도 | 탐색 156셀 0.9487 → 0.0449, b=0 c=141 — v1 점(0.021)과 겹쳐 보정 정보 없음, 중단 |
| thomas replay router v2 exact | 5개 "donor schedules" 라우팅(main.py:630-647) = 남의 리플레이 탑재 → K3·Rules §3.14a. 공개 LB 2,531.4 < yhay81 저자 2,929.4. 우리 코드 0줄 |
| shop-pair 라우터 재적합 | LOO-CV −428 (오라클 +4,792 는 비일반화) |
| 최고 스크랩 테이프 순수 재생 | K3 · Rules. vs boatlee 263-0-207 (56%) < parent 96-0-0 |
| 규칙기반 main.py 개선 | hosted 343.9, 풀 0.021 |
| 오늘 제출 안 함 | 슬롯이 343.9 봇으로 남아 정보 0 |

## C. §7.5 체크리스트 채우는 법 (Ledger 제외 제출 전)

```
Identity:  tar SHA-256 = 확인 실행에 쓴 tar 풀린 폴더의 SHA 와 동일. 멤버 4개 SHA 가 위 candidate 와 일치.
           프로토타입 vs 릴리스 액션 해시 동일(h2h seeds 5101..5110 × 양좌석 20판).                              [ ]
Schema:    tar 루트 main.py; get_last_callable 규칙상 마지막 callable = agent; hands 불일치 턴 = parent 와 동일값;
           exceptions 0 · guard 합 0 (664판 전부).                                                              [ ]
Runtime:   X1 agent CPU ≤ 5.0 s/episode (예산 1,200s 의 0.42%), p99 ≤ 5.0 ms, 최대 턴 ms 기록.                   [ ]
Isolation: 빈 폴더에 tar 해제 → kaggle_environments.agent.get_last_callable(raw, path=main.py) 로 로드
           (__file__ 없음) → starter 상대 720 steps DONE 1판.                                                    [ ]
License:   LICENSE.txt(Apache-2.0) 동봉, 변경 고지는 우리 main.py docstring, parent 파일 무수정.
           Rules :149c(OSI 허용) 충족 / :185 §3.14a 보증은 사람 판단 항목. 라이벌 테이프 미탑재(actions.json SHA 불변). [ ]
Ledger:    (제출 후) submission ID ↔ tar SHA ↔ `kaggle competitions episodes <ID>` 목록.                          [ ]
```

## D. 은퇴 결정

X1 제출은 FIFO 로 **v1-20260910 (56145245, 343.9)** 을 은퇴시킨다. parent 56147691 은 유지된다.
- v1 이 잃는 것: 규칙기반 가족의 hosted 이력(풀 0.021, 레이팅 343.9). 이 가족의 패배 집합은 거의 전체 경기라 활성 슬롯 커버리지 기여 0.
- X1 을 두 번째 슬롯에 두는 동안 §7.4 는 의도적으로 미충족이다. 판독(T+24h) 전 추가 제출은 parent 를 은퇴시키므로 **판독 전 0건**.
- 판독 후 첫 제출이 parent 를, 두 번째 제출이 X1 을 은퇴시킨다 (하루 5개 한도 내).

## E. 이탈 조건

| 시점 | 숫자 | 행동 |
|---|---|---|
| 확인 실행 | failure / inconclusive 조건 | 제출 안 함, X1 폐기 |
| 제출 후 T+6h | X1 validation `Error` 또는 publicScore 없음 | 원인 로그 확인, 재제출 안 함 |
| T+24h 판독 | STEEP / FLAT / WEAK | 위 next_if_success 분기 |
| T+24h 판독 | parent publicScore < 2,537.4 (09-10 500위 경계) | "public copy 로 500위 확보" 가정 폐기 — 자체 테이프 경로 우선순위 1 |

## F. 개정 1 — 2026-09-11 00:50 UTC (맥 파일 기록 00:50:58), 확인 실행 결과 열람 전 (독립 검토 반영)

로컬 seeds·로컬 임계는 바꾸지 않는다. **hosted_read 규칙과 문서 근거만** 바꾼다. 위 원문은 보존한다.

| 검토 지적 | 판정 | 개정 |
|---|---|---|
| a. X1 이 parent 보다 ≥9h 어리다 → Δrating 에 수렴 단계 차가 섞인다 (parent 0→7.3h 동안 600→2,188.4, 약 +217/h) | 수용 | hosted_read 를 **이중 판독**으로 교체 (아래) |
| a. −643 은 "parent 수렴값 = 원저자 2,929.4" 가정 | 수용 | 현재값 앵커(2,188.4) 예측 **−459** 병기. 두 예측 모두 STEEP 임계(−300) 이하, 공개봇 모형(≈0)은 FLAT 임계(−120) 이상 |
| b. 은퇴 봇도 계속 플레이할 수 있다 (evaluation.md 두 문장 충돌) | 부분 수용 | A/B 는 두 봇 모두 latest-2 라 영향 없음. 다음 CLI 판독에서 v0(56068891)가 347.2 에서 움직였는지 기록 → 은퇴 봇 플레이 여부 사실화 |
| c. 공개봇 4종 추가 반입으로 무제출 보정 가능 | 기각 | 공개 코드 = LB 제출물 연결이 `[COMMUNITY]` 인 한 점을 늘려도 연결 문제는 남는다. 기존 4점이 이미 비단조. exact artifact 대조는 제출로만 얻는다 |
| c. 매일 제출 보류 비용 미정량 | 수용 | 보류 1일. RESET 의 −3.2/일은 무변경 구 봇 수치이고, 최종 평가는 마감 시점 마지막 2개라 최종 순위 비용 0 |
| d. X1 좌석 대칭 근거는 parent 데이터(비대칭 2/235)다 | 수용 | X1 양좌석은 확인 실행(282셀)에서 처음 측정. 임계는 셀 기준 그대로 |
| e. thomas "5개" 출처 | 정정 | `releases/public-thomas-replay-router-v2-exact/manifest.json` preflight `clean_room_import: "5 schedules x 719 steps"`, source.title "95.5% Win Rate via Replay Routing", main.py:630-647 "donor schedules" |
| g. Apache-2.0 §4(c)(d) 미기재 | 수용 | License 줄을 기계 체크로 분리 (아래) |
| f. 로더 | 유지 | 검토자가 get_last_callable 로 격리 폴더 로드 → vs starter seed 9001 720 steps DONE, 142,482 vs 3,651 |

### hosted_read (개정본 — 원문 대체)
- 사람이 `kaggle competitions submissions kaggriculture` 를 X1 제출 후 **+6h, +12h, +24h** 와 **parent 경과 24h 시점(2026-09-11 15:57 UTC ±1h)** 에 실행해 붙여넣는다.
- Δ_wall = X1(T+24h) − parent(T+24h), 같은 CLI 출력.
- Δ_age = X1(경과 24h) − parent(경과 24h), 두 출력 (parent 는 09-11 15:57±1h 값).
- **STEEP**: Δ_wall ≤ −300 AND Δ_age ≤ −300 · **FLAT**: Δ_wall ≥ −120 AND Δ_age ≥ −120 · 그 외 **WEAK**.
- parent 경과 24h 출력이 없으면(15:57±1h 창 놓침) Δ_age 는 결측 → 판정은 WEAK 로 고정.

### License (개정본 — 기계 체크)
```
L1 LICENSE.txt sha256 = cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 (Apache-2.0 전문)   [ ]
L2 yh_base.py sha256 = d6d74997…866b = parent main.py (저작권·출처 고지 무수정, §4(c))                     [ ]
L3 NOTICE 파일: parent tar 멤버 3개에 없음 → §4(d) 해당 없음 (tar -tzf 로 확인)                           [ ]
L4 변경 고지: 우리 main.py docstring 1~9행에 변경 내용·날짜 (§4(b))                                       [ ]
L5 라이벌 테이프 미탑재: actions.json sha256 = 17d503f2…95ef, private_artifacts/ 파일 0개                  [ ]
```
Rules :185 §3.14a 보증 해석은 체크리스트가 아니라 **사람 승인 항목**으로 분리한다.

## G. 개정 2 — 2026-09-11 00:53 UTC, 확인 실행 결과 열람 전

parent 경과 24h 는 09-11 15:57 UTC(00:57 KST)라 사람이 직접 읽기 어렵다. Δ_age 원천을 **맥 시간별 로그**로 허용한다.
- 로그: 맥 crontab `0 * * * * cd ~/kaggle/Kaggriculture && (date -u; kaggle competitions submissions kaggriculture) >> evidence/raw/cli_submissions.log 2>&1`
- 경과 24h 값 = 경과 24h 를 앞뒤로 감싸는 두 판독의 선형보간, 두 판독 간격 ≤ 2h. 감싸는 판독이 없으면 Δ_age 결측 → WEAK.
- 판정 임계(−300 / −120)와 이중 조건(Δ_wall AND Δ_age)은 개정 1 그대로.

## H. 결과 — 2026-09-11 01:21 UTC · 판정 **FAILURE** → 제출 안 함

원자료 `evidence/raw/EXP-005/` (카드 artifact 줄의 `experiments/results/` 는 Codex 경로라 Claude 소유 경로로 옮김, 내용 동일).
판정 스크립트 `evidence/raw/EXP-005/judge_exp005.py`. 664판, 결측 0, 전부 720 steps DONE.

| 항목 | 임계 | 값 | |
|---|---|---:|---|
| Δpool (282셀) | ≤ −0.10 | **−0.1915** (parent 0.9787 → X1 0.7872) | 충족 |
| c − b | ≥ 20 | **54** (b=0, c=54) | 충족 |
| exceptions / guard / shed_unsold / manual_drop_lost | 0 | 0 / 0 / 0 / 0 | 충족 |
| CPU max · p99 max | ≤ 5.0 s · ≤ 5.0 ms | 0.41 s · 4.10 ms | 충족 |
| **discard max / player-run** | ≤ 10 | **81** (X1 합 11,032 / 344 run, 위반 324 run) | **위반** |
| **end_units** | 0 | **28** (전부 SHEEP, 4 run × 7) | **위반** |

진단(판정 불변): h2h X1 0-0-20 · 공개봇 X1 34-0-6 vs parent 40-0-0 · X1 좌석 비대칭 셀 1/141.
독립 검토(서브에이전트, sellaudit 미사용 재계측): discard 81(X1)·36(parent, Crop_Dusta_106263397 seed 5102) 재현, 귀속 오류 없음 → **FAILURE 유지**.
- end_units 28 은 가격 없는 미배치 가축(SHEEP)이다. 하니스 정의 결함(PRODUCTS 외 포함)이지만 parent 는 같은 셀에서 0 → X1 고유. discard 하나로 이미 failure.
- 원인: X1 매도가 셰드 점유 시점과 현금 흐름을 바꿔 개루프 테이프의 DROP/PICKUP/PLACE 턴과 어긋난다 (BUY_PRODUCT WHEAT 체결 수는 173 = 173 동일).
- parent 도 discard > 10 인 run 이 2개(각 36). 임계 ≤10 은 탐색 최대치(7)에서 잡은 값이라 이 가족에 빡빡하다 — 다음 카드는 parent 대비 상대 임계로 쓴다.
- H_local(대조 존재)은 확인됐다. hosted 판독은 제출이 없으므로 수행하지 않는다.
