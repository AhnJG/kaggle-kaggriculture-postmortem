# Kaggriculture — 9월 15일부터 대회 마감까지의 계획

작성: **2026-09-15 KST · Codex, 사람 위임 Coordinator**. 현재 계획의 단일 진입점은 [CURRENT.md](CURRENT.md).
이 문서는 작업 순서와 중단 기준을 정한다. **새 실험의 사전등록 카드나 Kaggle 제출 승인을 대신하지 않는다.**
갱신 2026-09-15: [독립 검토 F3/F5/F6](../coordination/reports/codex/20260915-independent-review.md)에 따라 R10 해석, 공개 source triage, release preflight와 슬롯 관측 조건을 구체화했다. 아래 P1 산출물은 아직 실행·완료되지 않았다.

## 1. 먼저 이해할 핵심

**지금 필요한 것은 강한 농장 계획을 유지하면서, 실제로 지는 상황을 하나씩 줄이는 일이다.**
처음부터 모든 것을 다시 만드는 방식으로 돌아가기에는 검증할 시간이 짧다. 그렇다고 기존 판매 순서를 무작정 바꾸면 돈·재고·고용이 연쇄적으로 어긋난다는 실패도 이미 확인했다. 이 방향은 현재 기록에서 도출한 `[INFERENCE]`이며 우승을 보장하는 전략은 아니다.

쉽게 말하면 기존 tape는 **하루 종일 돌아가는 식당의 작업표**다. 재료를 사는 시각, 요리하는 시각, 손님에게 내는 시각이 연결돼 있다. 초반 계산대에 돈을 더 남기는 데 성공해도 다음 재료 구매가 꼬이면 식당 전체 성적은 나빠진다. 따라서 ‘초반 문제가 사라졌는가’와 ‘끝까지 더 많이 이기는가’를 따로 검사한다.

이번 검토에서 확인한 결과는 다음과 같다.

| 항목 | 현재 판단 | 뜻 |
|---|---|---|
| `[HOSTED]` 활성 EXP-006 | **1862.6**, COMPLETE | 현재 둘 중 우선 보존할 기준 후보(incumbent) |
| `[HOSTED]` 활성 EXP-007 | **1635.9**, COMPLETE | 점수가 낮고 보완성은 아직 미확인 |
| `[HOSTED]` Sian | **1,724위**, 같은 세션 10위 **2974.2** | 상금권 도달 가능성을 숫자로 예측할 근거는 N/A |
| `[LOCAL]` EXP-008 | **FAILURE**, 고정 326셀 | 첫날 회복은 있었지만 목표 0승 0무 2패, pool 새 패배 2셀 |
| `[LOCAL]` 계측·release gate | schema 3 구현 완료 | ‘많이 팔라고 요청함’과 ‘실제로 못 팔아 남김’을 구분 |
| `[LOCAL]` 기록 관리 | BOARD·HANDOFF와 카드·registry가 뒤처짐 | 완료한 일을 다시 시작하지 않도록 현재 포인터를 정리 |

출처: [이번 직접 조회](../coordination/reports/codex/20260915-0115-KAGGLE-SNAPSHOT.md), [EXP-008 결과](../coordination/reports/codex/20260914-2025-EXP008-RESULT.md), [gate 변경](../coordination/reports/codex/20260914-2043-GATE-SPLIT.md).
점수는 09-15 KST 조회 snapshot이다. 새 같은-window W/D/L과 causal 비교는 **N/A**다. EXP-006의 clone-preempt 효과, EXP-007의 슬롯 보완성이 입증됐다는 뜻은 아니다.

## 2. 마감과 계획의 근거

| 구분 | 한국시간 KST | UTC | 성격 |
|---|---|---|---|
| 참가·팀 합치기 마감 | **09-24 08:59** | 09-23 23:59 | 공식 |
| 최종 제출 마감 | **10-01 08:59** | 09-30 23:59 | 공식 |
| 새 전략 개발 중단 | **09-27 00:00** | 09-26 15:00 | 이 계획의 내부 cutoff |
| 최종 pair 결정·코드 동결 | **09-28 18:00** | 09-28 09:00 | 내부 목표 |
| 최종 제출 완료 목표 | **09-29 18:00** | 09-29 09:00 | 내부 목표, 공식 마감보다 38시간 59분 빠름 |
| 마감 뒤 평가 | 10-01부터 약 10-15까지 | 공식 페이지 참조 | 제출 잠김, 수렴에 따라 종료 |

`[OFFICIAL]` 위 공식 일정·하루 5개·최신 2개 규칙은 [공식 Overview](https://www.kaggle.com/competitions/kaggriculture/overview)에서 **09-15 KST 직접 확인**했다. 내부 cutoff는 관측과 오류 대응 시간을 남기기 위한 운영 선택이며, 39시간이면 rating이 수렴한다는 주장이 아니다.

`[OFFICIAL]` [Kaggle Staff 답변](https://www.kaggle.com/competitions/kaggriculture/discussion/732931)은 전 기간 경기 중 **양쪽 agent가 최종에도 활성인 경기**를 final Bradley–Terry 계산에 포함한다고 명시한다. 오래 유지한 기간만큼 유효 경기가 반드시 쌓이는 것은 아니다. 상대가 은퇴해도 해당 경기는 빠진다.

검증 방식은 다음 원자료를 참고했다.

- [Glasserman & Yao, 1992, Common Random Numbers](https://pubsonline.informs.org/doi/10.1287/mnsc.38.6.884): 같은 난수 조건에서 시스템을 비교하는 방법과 성립 조건을 다룬다. **같은 날씨에서 두 농장 운영법을 시험한다**는 직관으로 same-seed 비교에 사용한다. 이 게임에서 분산 감소를 보장한다는 뜻은 아니다.
- [Bradley & Terry, 1952](https://academic.oup.com/biomet/article-abstract/39/3-4/324/326091): pairwise 비교 모델의 원전이다. 대회의 세부 구현은 논문에서 추정하지 않고 공식 평가 설명을 따른다.
- 게임 동작은 [ENGINE_LOCK](../environment/ENGINE_LOCK.md)의 **1.32.7**을 따른다. 이번 세션에 설치된 엔진 Python·JSON SHA가 lock과 일치함을 확인했다. 현재 hosted engine version을 새로 수집한 것은 아니므로 패치 여부는 다음 episode 수집 때 재확인한다.

## 3. 프로젝트에서 유지하고, 멈추고, 새로 확인할 것

| 대상 | 결정 | 이유·근거 |
|---|---|---|
| replay 기반 농장 backbone | 유지 | HYP-0008·0017. 우리 exact artifact에 대한 과거 hosted 근거가 있다. 모든 rule agent보다 좋다는 일반화는 금지 |
| EXP-006 clone-preempt | 다음 후보의 잠정 parent로 고정 | 현재 활성 두 점수에서 우위. parent 대비 causal 효과는 미결 |
| EXP-008 exact B opening schedule | 폐기, 재실행하지 않음 | HYP-0030·TEST-0008, G1/G3/G4/G5 FAIL. seed 추가나 이름만 바꾼 재시험 금지 |
| 광범위한 매도 재작성·작물 이름 치환 | 이번 기간 기본 경로에서 제외 | HYP-0027, FACTS F-T10/F-T11: 기존 작업표와 충돌한 local 실패 |
| 상대 standing MELON 신호에 반응하는 좁은 분기 | 조건부 조사 | R10은 상대 MELON의 `yield_units`를 합산해 현재 shed 재고를 추가 SELL한다. maturity trigger·shift/repay는 우리 별도 설계이며, 우리 parent의 해당 패배 증거가 먼저 필요 |
| 동물 먹이 실패 방지 | 원인 조사만 우선 | 같은 제안의 cow 사례는 타인 결과. 우리 agent의 같은 실패가 확인되기 전 구현하지 않음 |
| pure PPO·새 전면 planner·대규모 재구축 | 기본 일정에서 제외 | KILLS K6 재개 조건과 별도 검증 비용. 고정 incumbent·근거·자원 조건이 충족됐다는 확인 없음 |
| 네 번째 땅·GOOSE 등 KILL 항목 | 조건 성립 전 닫힘 | [KILLS](../evidence/KILLS.md)의 재검토 조건과 ENGINE/HOSTED 근거 필요 |

**제안 파일에 적힌 HYP-0031~0033, EXP-009/010은 아직 공용 원장·카드에 등록되지 않았다.** 현재 원장은 30개다. ‘이미 다음 실험으로 승인됨’으로 해석하지 않는다. 관련 source를 확인하고 updater가 발급한 ID로 기록한 뒤 Claude가 카드를 만든다.

**R10 해석 정정 — 2026-09-15:** `[COMMUNITY]` R10 cell 2:1135–1162는 MELON 나이를 검사하지 않는다. `[ENGINE]` 1.32.7은 심을 때부터 `yield_units=1`로 만들며 HARVEST에는 `first_yield_day=10` 조건이 있다(`kaggriculture.py:16,215–225,449–462`). 따라서 이전의 ‘상대 수확 시점’ 설명을 수확 가능성의 근거로 쓰지 않는다. source URL·수집일·SHA·cell과 engine 재현은 [독립 검토 F3·§3](../coordination/reports/codex/20260915-independent-review.md), 정정 대상 원문은 [09-14 제안](../coordination/proposals/codex/20260914-community-trends-plan-update.md)에 있다. 이 정정은 새 전략의 효과를 입증하지 않는다.

## 4. 날짜별 실행 계획

아래 날짜는 모두 KST다. 순서는 날짜보다 선행 조건이 우선한다. 통과하지 못한 작업을 일정 때문에 제출 단계로 밀어 넣지 않는다.

| 기간 | 무엇을 하는가·왜 하는가 | 담당 | 끝났다고 판단할 산출물 | 미달 시 다음 행동 |
|---|---|---|---|---|
| **09-15** | 현재 상태 정리, EXP-008 실패 종결, release gate 차이 명시 | Coordinator / Claude | BOARD·HANDOFF·CURRENT 연결, EXP-008 결과·registry 갱신 또는 명시적 pending, 최신 점수 출처 | 미갱신 문서는 작업 지시로 쓰지 않고 owner에게 결과 반영만 이관 |
| **09-15~16** | 공개 자료 판독·실제 parent tar release preflight·최신 hosted 패배 조사. 잘못된 힌트와 제출 불가능한 경로를 먼저 걸러냄 | Gemini 수집 / Claude 판독·manifest 확인 / Codex 실행 / 독립 검증자 | **09-16 18:00까지** §5의 source triage 표·preflight manifest/판정·hosted 보고서 | preflight FAIL/N/A면 새 전략 HOLD 및 correctness 경로 결정. source가 미확인이라면 해당 claim 보류, causal target이 없으면 상대 pool 보강 |
| **09-17~26 매일 18:00까지** | notebook/discussion 변경분과 기존 근거의 정정 댓글 확인 | Gemini → Claude → Codex | §5.1의 날짜별 triage 표. 변경 없음 또는 partial/failed도 기록 | 누락 자료를 채택 근거로 쓰지 않음. 기존 승인 카드 범위는 자동 변경하지 않음 |
| **09-17~19** | 첫 번째 좁은 변경을 한 카드로 구현·검사 | Claude 설계 → Codex 구현 → 독립 검증자 | 사전등록·candidate SHA·target/control/public/pool 결과·수치 verdict | FAILURE면 폐기, INCONCLUSIVE면 보류. 결과를 보고 같은 표본 확대 금지 |
| **09-20~23** | 통과 후보의 별도 확인 평가와 슬롯 교체 판단. 필요하면 다른 원인의 두 번째 카드 | 같은 역할 순서 / 사람 제출 승인 | 최신 pool holdout·release 5줄·FIFO 전후 표·§7의 제출 후 active pair 관측 계획·승인 또는 HOLD | local/release/FIFO 독립 검토가 미통과하거나 제출 후 관측 담당·경로가 없으면 교체 HOLD. 제출 전 C/A hosted causal 비교는 N/A |
| **09-23 18:00까지** | 팀 유지·합치기 결정 | 사람 | 솔로 유지 또는 병합 결정. 기본 계획은 현재 솔로 유지 | 연락·병합·코드 공유는 별도 사람 승인 전 실행하지 않음 |
| **09-24~26** | 최종 후보를 별도 평가. 후보별 강도와 둘이 함께 지는 상황 확인 | Claude 판정 / Codex 실행 / 독립 검증자 | 고정 final manifest, 동일 상대·seed·좌석 비교, 개별 및 pair 보고 | 통과 후보 없으면 현재 활성 두 제출 유지. 숫자가 낮다는 이유로 미검증 후보를 올리지 않음 |
| **09-27~28** | 새 전략 중단, 최종 두 후보 결정·freeze·clean-room 검사 | Codex / 검증자 / 사람 | 09-28 18:00까지 source·tar SHA, 재현 명령, runtime, license, 제출 순서 | code 변경이 생기면 영향받는 검증을 다시 통과해야 함 |
| **09-29 18:00까지** | 승인된 경우 최종 제출 완료, validation·ID 확인 | 사람 / Coordinator 기록 | 두 활성 ID·업로드 SHA·COMPLETE·episode 연결 | ERROR는 기존 freeze에서 최소 수정 후 재검증. 무계획 연속 제출 금지 |
| **09-30~10-01 08:59** | 새 아이디어 없이 최종 상태 점검 | Coordinator / 사람 | 09-30 18:00과 10-01 07:00 KST에 active pair·status 확인 기록 | 검증 시간 없는 변경은 보류. 공식 마감 직전 업로드를 기본값으로 삼지 않음 |
| **마감 뒤~최종 확정** | 코드 변경 없이 오류·episode 상태 판독, 재현·license 자료 정리 | Gemini / Claude / Codex | 최종 두 ID 중심 보고서, 소스·환경·출처 bundle | 수상 대응 요청 시 사람에게 전달. 자동 공개하지 않음 |

운영 예산 제안: **동시에 실행하는 전략 카드 1개, 09-26까지 새 전략 카드 최대 2개**. 실패 원인 분석·환경 canary는 전략 카드 수와 구분한다. 추가 compute 구매 없이 기존 Mac/가용 환경을 기본으로 한다. 카드마다 benchmark로 예상 wall time을 먼저 기록하고 **전체 실행 8시간을 넘을 예상이면 시작 전에 설계를 다시 검토**한다. 이것은 표본을 실행 도중 줄여도 된다는 뜻이 아니다. 자원 부족은 BLOCKED로 기록한다.

## 5. 다음 작업 P1 — 가장 먼저 무엇을 알아야 하는가

**목표:** ‘어디를 고칠까’를 직감으로 고르지 않고 최근 패배에서 고른다. 현 상태의 ranking을 재는 작업과 전략 원인을 시험하는 작업을 분리한다.

### 5.1 공개 자료를 다음 결정으로 연결한다

자료 수집은 **힌트가 적힌 쪽지를 가져오는 일**이고, triage는 그 힌트가 우리 문제에 맞는지 확인해 담당자에게 넘기는 일이다. 파일이 늘었다는 이유만으로 다음 실험이 정해지지는 않는다.

- **담당·시점:** Gemini가 09-16 18:00 KST까지 보유 notebook/discussion 전체 inventory와 변경분·근거로 인용한 source의 watchlist를 정리한다. 최초 목록은 [독립 검토의 48개/16개 inventory](../coordination/reports/codex/20260915-independent-review.md)와 대조하고 이후 증감을 기록한다. 09-17~26에는 매일 18:00까지 직전 수집 cutoff 이후 변경분·새 관련 자료·정정 댓글을 확인한다. listing 범위·page/reply completeness·실패를 남기며 `dateRun`을 전략 평가일로 대신 쓰지 않는다.
- **완료 파일:** Gemini는 `analysis/public_source_triage/YYYYMMDD.md`에 source ID/URL·작성/갱신시각·수집시각 UTC·source version·local path/SHA·engine·license·본문/댓글 completeness·fetch status를 기록하고, Claude의 판독 제안과 Codex의 원장 확인을 인수해 같은 표에 반영한다. 모르는 값은 **N/A**다. 실패한 조회를 ‘변경 없음’으로 기록하거나 이전 정상 원문을 덮지 않는다. source 변경으로 요약을 고쳤다면 이전 source SHA와 정정 이유를 연결한다.
- **claim별 결정:** source의 실제 code/댓글 위치, 기존 HYP-ID 또는 중복 없음, 우리 parent 패배와의 관련성, **채택/보류/기각** 및 이유, 다음 owner를 한 행으로 남긴다. ‘채택’은 카드 설계용 힌트 채택이며 성능 검증·실행 승인이 아니다. 원문/SHA가 없거나 핵심 조건이 미확인이면 보류하고, license N/A인 source의 코드·데이터는 사용하지 않는다. source date/engine이 N/A인 성능 주장은 현재 meta 근거로 인용하지 않는다.
- **인수 종료:** Claude가 채택한 claim만 postmortem·KILLS 재검토 조건과 함께 설계 대상으로 인수한다. Codex는 HYP 중복을 확인해 updater event를 남기고 strict validation을 통과시킨다. 새 HYP-ID는 updater로 등록하기 전 예약하지 않는다. 초기 및 날짜별 표에 owner의 인수 여부·미처리 이유가 있어야 triage 완료다. 부분 실패는 기록 완료일 뿐 해당 claim의 검증 완료가 아니다.
- **유입 cutoff:** 09-27 00:00 KST 이후 새 전략 아이디어는 보류 목록으로 보낸다. 공식 일정·engine patch·우리 artifact에 직접 해당하는 오류만 Coordinator가 별도 correctness 검토로 전달한다. 이 경로도 freeze 뒤 변경이면 영향받는 검증을 다시 통과해야 한다.

### 5.2 실제 parent tar의 release 가능성을 먼저 확인한다

새 조리법을 시험하기 전에 **지금 주방이 기본 점검을 통과할 수 있는지** 확인한다. 오래된 schema-2 counter는 점검 필요성의 근거이며 새 schema-3 결과를 대신하지 않는다([독립 검토 F6](../coordination/reports/codex/20260915-independent-review.md)).

1. **실행 전 고정:** Codex가 §10의 actual parent A tar를 대상으로 `experiments/results/p1_release_preflight/manifest.json` 초안을 만들고 Claude와 독립 검증자가 범위를 확인한다. tar·추출 source/dependency·engine·runner SHA, schema 3, 전체 opponent artifact·seed 목록·좌석·예상 판수, self-play 3판과 양 좌석 smoke/stress·기존 EXP-008 control 실패 재현 셀, 출력 경로·재현 명령·숫자 runtime 상한·측정 환경을 실행 전에 확정한다. manifest가 불완전하면 **BLOCKED**이며 임의의 소규모 실행을 preflight 완료로 대신하지 않는다.
2. **실행·산출물:** Codex가 빈 폴더에 tar를 풀어 §8의 제출 전 5줄과 schema-3 zero gate를 검사하고 `experiments/results/p1_release_preflight/report.md` 및 cell별 JSON·counter·지연 기록을 남긴다. test 상대의 counter와 우리 counter를 구분하며 parent self-play는 양쪽을 확인한다. `sell_unfilled`는 diagnostic, `shed_unsold` 등 §6의 실제 손실은 각각 별도 기록한다. 구현자와 다른 검증자가 manifest 대비 누락·SHA·판정을 확인한다.
3. **P1 종료 판정:** 고정된 모든 셀의 결과가 있고 제출 전 5줄·zero gate가 전부 PASS하며 독립 검증이 끝나야 **preflight PASS**다. 이는 그 manifest에서의 release 기본 조건 확인이며 새 후보의 성능 승격이나 최종 release를 대신하지 않는다. 미실행·누락·식별/계측 불가·license 미확인은 **N/A/BLOCKED**, 실제 gate 위반은 **FAIL**로 기록한다. Ledger는 신규 제출 전 N/A가 정상이며 이 사유만으로 preflight를 막지 않는다.
4. **FAIL/N/A 경로:** 새 전략 카드 착수를 **HOLD**하고 Coordinator/Claude가 09-16 P1 보고서에 기존 A/B 유지 또는 별도 사전등록한 correctness repair 후 새 parent freeze·동일 preflight 재검증 경로와 owner를 기록한다. 계약 해석이 필요하면 근거를 모아 사람에게 이관하며 결정 전 HOLD를 유지한다. 실패 뒤 zero gate를 낮추거나 불리한 셀을 빼지 않는다. correctness 완료 없이 날짜만으로 09-17 전략 단계에 넘어가지 않는다.

### 5.3 최신 hosted 패배와 상대를 조사한다

1. 수집 시작 전에 **직전 24시간의 UTC 시작·끝을 고정**하고, EXP-006/007 각각 최신 완료 **50판**을 수집한다. 50판 미만이면 관측된 수와 N/A를 보고하고 기간을 소급 확대하지 않는다. 이후 관측은 새 window로 구분한다. 먼저 판수를 정하고 결과를 읽는 운영 설계다.
2. episode ID·생성시각·우리/상대 submission ID·좌석·W/D/L·engine version을 묶는다. 상대 이름만으로 같은 code라고 간주하지 않는다. ID가 없으면 N/A. 양 제출이 같은 상대·같은 seed를 만난다는 보장은 없다.
3. 각 제출의 최신 패배 중 **가장 최근 완료된 1판**을 postmortem한다. 패배가 없다면 0판이라고 적는다. 첫 구조적 분기와 마지막 손실을 찾고, 우리 exact tar + frozen 상대 transcript를 양 좌석에서 재현한다. 상대 transcript 재생은 반응형 상대 전체를 재현한 증거가 아니다.
4. 공개 4봇·47 tape는 **고정 regression 세트**로 보존한다. 최신 opponent 세트는 별도 manifest로 추가한다. source/episode·수집일·license·engine·SHA를 기록하며, 같은 donor의 비슷한 tape 여러 개를 독립적인 상대 여러 종류처럼 세지 않는다.
5. 비교 보고에는 W/D/L·표본수·시간창·상대 분포를 함께 쓴다. **같은-window라도 상대가 다르면 point score 차이는 causal 효과가 아니다.** 새 실험의 target과 성공/실패 임계는 이 보고서를 읽은 뒤 후보 결과를 보기 전에 정한다.

가능한 다음 분기는 둘이다. **시장 경쟁이 실제 패배 원인이면** 관측 신호와 판매 개입을 분리한 bounded branch를 검토한다. standing MELON의 `yield_units`만으로 maturity를 판정하지 않으며 maturity trigger·shift/repay는 §3의 별도 우리 가설이다. **동물 급여 누락이 실제 원인이면** 그 상황만 처리하는 guard를 검토한다. 둘 다 없으면 해당 제안은 보류하고 관측된 다른 failure에 한정한다. 한 판에서 보이지 않았다는 이유로 해당 실패가 전체 경기에서 없다고 결론내리지 않는다. 기존 EXP-008 B를 둘 중 하나로 이름만 바꾸지 않는다.

## 6. 새 카드가 반드시 답해야 할 질문

쉬운 흐름은 **실전 패배 → 실패 원인 → 한 가지 수정 → 같은 조건 비교 → 새 상황 확인 → 제출 판단**이다.

| 단계 | 필요한 근거·기준 | 실패했을 때 |
|---|---|---|
| 사전등록 | 원장 HYP-ID·고유 TEST-ID, exact parent/opponent SHA, 한 변화 A→B, seed 전체 목록·both seats, postmortem, 숫자 success/failure/inconclusive | 하나라도 모호하면 BLOCKED, 구현 전에 Claude에 반환 |
| 기본 동작 | engine SHA 일치, 모든 경기 720 steps DONE/DONE, 예외·timeout 0, 새 guard 전용 counter | 결과를 성능 표에 섞지 않고 INVALID로 격리 |
| 원인 확인 | target 실패가 사전 임계만큼 줄고, control·상대별 손해가 카드의 non-inferiority 기준을 통과 | 원인 지표만 좋아졌으면 제출 금지 |
| 비교 평가 | 공개 4봇 **paired score의 95% CI 하한 > 0.5**라는 AGENTS §7.1 승격 기준 유지. parent 대비·최신 pool·상대별 non-inferiority도 별도 판정 | local 탐색 개선과 승격 실패를 함께 기록 |
| 최종 확인 | 개발에 쓰지 않은 고정 holdout에서 frozen artifact 재평가. 모든 seed·상대는 실행 전에 확정 | 결과를 본 뒤 표본 추가·후보 수정 금지 |
| release | 아래 6줄 중 제출 전 5줄 PASS, 실제 tar에 대해 검증 | card SUCCESS만으로 release PASS 선언 금지 |

**Gate를 혼동하지 않는다.** EXP-008의 상대적 counter 기준(candidate ≤ parent)은 그 카드의 원인 검증용이다. 현재 일반 release gate는 `noop_actions`, `shed_discarded`, `shed_unsold`, `orders_truncated`, `buy_failed`, `hire_failed`, `seed_blocked_plant`, `exceptions` **각각 0**을 요구한다. `sell_unfilled`는 diagnostic이다([schema 3 보고](../coordination/reports/codex/20260914-2043-GATE-SPLIT.md)). 이미 제출된 tar를 새 schema로 다시 검증해 PASS했다는 기록은 아직 N/A다.

따라서 **parent보다 덜 망가지는 후보라도 실제 손실이 남으면 release는 막힐 수 있다.** §5.2의 actual-tar preflight PASS와 §5.1의 triage 완료·§5.3의 원인 근거가 첫 새 전략 카드의 선행 조건이다. 공개 source를 사용하는 카드는 해당 claim의 인수도 필요하다. 통과할 수 없는 후보에 제출 일정을 예약하지 않는다. 실험 후 gate를 낮춰 통과시키지 않는다.

**한 변화와 action parity도 다르다.** 같은 입력에서 trigger 밖 행동이 parent와 같은지 검사할 수 있지만, 실제 경기에서 돈이 달라지면 이후 행동도 달라질 수 있다. 새 카드에서는 동일 observation 비교와 실제 trajectory의 허용된 변화 범위를 구현 전에 나눠 정의한다. EXP-008의 G5와 FAILURE를 소급 변경하지 않는다.

**표본 주의:** seed별 양 좌석을 묶어 CI를 계산한다. 같은 seed·복제 tape를 많이 돌렸다고 독립 정보가 그만큼 늘지 않는다. 전승으로 기존 t-interval이 폭 0을 반환해도 확실성 100%로 해석하지 않는다. 최종 카드에 경계값을 다루는 interval과 상대별 non-inferiority margin을 고정한다. 이 계획에서 아직 없는 효과 크기나 통계적 power를 만들어 내지는 않는다.

**두 슬롯 보완성:** 두 점수를 더해 평가하는 방식이 아니며 각 후보 자체의 강도가 먼저다. 동일 opponent artifact·seed·좌석에 대해 두 후보의 승패를 나란히 기록하고, 둘 다 패배·한쪽만 승리한 셀·패배 상관을 보고한다. 한쪽 결과가 전부 같으면 상관계수는 N/A다. 보완성 임계는 별도 final-pair 카드에서 사전등록한다. 09-12에 패배 상대 이름이 겹치지 않았다는 사실만으로 합격시키지 않는다.

## 7. 슬롯 교체 — 현재 가장 조심할 결정

`[OFFICIAL+INFERENCE]` 현재 오래된 순서는 **A=EXP-006 → B=EXP-007**이다. 최신 2개 규칙 때문에:

```text
현재                [A(1862.6), B(1635.9)]
새 후보 C 한 번 제출 [B, C]       → 먼저 사라지는 것은 더 강한 A
그 뒤 후보 D 제출   [C, D]       → B도 사라짐
```

**‘약한 EXP-007만 교체하고 기존 EXP-006 ID를 보존한다’는 단일 제출 계획은 실행할 수 없다.** 두 슬롯은 후보를 임의로 골라 고정하는 진열장이 아니라, 마지막 두 제출만 남는 줄이다.

- 기본값: **새 pair가 통과하기 전에는 현재 A/B 유지**. C 하나만 올릴 때도 비교 대상은 B가 아니라 먼저 은퇴할 A다.
- 새 후보 둘을 준비했다면 C·D **각각**의 강도와 release를 확인한 후 사람이 **제출 두 건 전체의 전후 상태와 이력 손실**을 승인한다. 첫 제출 성공을 확인한 뒤 둘째를 진행한다.
- 하나만 준비됐다면 `[B,C]`가 되는 결과를 명시하고 A를 잃을 만큼 근거가 있는지 독립 검토한다. 불명확하면 HOLD다.
- A를 같은 바이트로 다시 올려도 기존 ID·경기 이력은 복구되지 않는다. 단순 점수 reroll용 duplicate 제출은 KILLS에 따라 하지 않는다.
- **제출 전:** 기존 활성 A/B의 같은-window 자료는 현재 pair의 맥락이다. 새 C와 은퇴할 A의 동시 hosted causal 비교는 **N/A**이며, 두 날짜의 live 점수를 붙여 그 비교를 대신하지 않는다. C/A의 local·holdout·release와 FIFO 이력 손실을 독립 검토하고 사람이 제한을 포함해 승인해야 한다. C/A hosted N/A 자체를 local PASS나 교체 허가로 바꾸지 않는다.
- **제출 후:** C 한 건이면 **B/C**, C·D 두 건 완료 뒤에는 **C/D**를 같은-window에서 관측한다. 제출 전에 Gemini 수집·Claude 판독의 담당, 조회 경로, UTC window 시작·끝과 수집 예정 시점을 기록한다. 이 관측 계획이 없으면 교체 HOLD다. 두 제출 사이의 B/C 관측이 최종 C/D 관측을 대신하지 않는다.
- 각 제출 후 +24h, +72h 시점을 관측 목표로 하고 각 시점 직전 24시간을 **서로 다른 고정 window**로 둔다. 표본·ID·누락 처리는 §5.3을 따른다. 같은-window라도 상대 분포가 다르면 causal 효과는 N/A다. 이 시점은 convergence 보장이나 합격 임계가 아니다. 표본 부족이면 INCONCLUSIVE, 즉시 다시 제출하지 않는다. +72h가 마감 뒤라면 사후 판독용이며 이미 끝난 제출 결정의 근거로 소급하지 않는다.

동점 처리에서 ‘먼저 제출한 쪽’은 [Rules](https://www.kaggle.com/competitions/kaggriculture/rules)의 최종 동점 규정이다. **개별 게임의 무승부를 승리로 바꾸지 않는다.** 과거 계획의 두 표현이 섞인 문장은 사용하지 않는다.

## 8. 최종 제출 전 점검

각 후보의 release 보고서에 [AGENTS §7.5](../AGENTS.md) 양식을 복사한다.

```text
Identity:  제출 파일 SHA-256 = 성능을 측정한 파일 SHA-256 인가?      [ ]
Schema:    루트 main.py / agent(obs) / hands 길이 정렬 / 절대 raise 안 함  [ ]
Runtime:   에피소드 예산(§6)의 70~80% 이내인가? p99 턴 지연 기록      [ ]
Isolation: 빈 폴더 clean-room 에서 tar 풀고 import 성공했는가?        [ ]
License:   외부 코드·상대 봇·데이터의 라이선스가 Rules 를 만족하는가?   [ ]
Ledger:    submission ID ↔ artifact SHA ↔ 에피소드를 연결했는가?       [ ]
```

앞 5줄은 제출 전, Ledger는 제출 후 채운다. root `main.py`가 아니라 **실제 tar에서 꺼낸 source·dependency**를 시험한다. 첫 호출·p99·최대 지연·전체 episode 시간, self-play 3판, 양 좌석 stress를 기록한다. 한 턴 1초·overage 60초만 보지 말고 **양쪽 합산 local episode 1200초 예산**을 함께 본다. hosted scheduling은 N/A이며 local 시간으로 보증하지 않는다.

CPU thread 수를 1로 고정하고, 최신 release 카드에 숫자 runtime 상한·측정 환경을 명시한다. source·manifest·의존 자료 SHA·복원 명령을 Git에 보존한다. tar가 ignore돼 있어도 재구축 경로가 있어야 하며, 새 tar의 바이트 SHA가 다르면 새로운 artifact로 기록한다.

## 9. 역할과 이번 갱신의 범위

- **Coordinator(Codex, 이번 사람 위임):** BOARD·HANDOFF·현재 계획 포인터, 작업 순서와 제출 전후 슬롯표.
- **Claude:** 사전등록·결과 해석·evidence·registry의 현재 행. 이번에 남은 기록 반영은 [owner 이관안](../coordination/proposals/codex/20260915-owner-record-sync.md)을 따른다.
- **Codex integrator:** candidate·runner·검증·release. 같은 파일을 여러 agent가 동시에 바꾸지 않는다.
- **Gemini:** 최신 opponent·replay·공식 패치·license 및 notebook/discussion 변경분 수집, §5.1 triage 표의 단일 writer. Claude 판독·Codex 원장 확인을 인수해 공개 주장과 우리 측정 결과를 구분한다.
- **독립 검증자:** 구현자와 다른 검토자가 카드·identity·결과를 확인한다. 본 계획 작성 자체를 독립 검증 완료로 기록하지 않는다.
- **사람:** 외부 제출·팀 변경·코드 공개 승인, 최종 pair와 순서 결정. 계획 작성 승인은 제출 승인이 아니다.

이 작업은 계획·현재 상태 갱신이다. 새 strategy run·제출·팀 변경은 하지 않았다. 엔진 사실 확인 스크립트의 기본 simulation과 문서/해시 확인만 수행했다. 다른 agent의 dirty 파일과 EXP-008의 frozen 카드를 수정하지 않았다.

## 10. 재시작할 때 읽을 근거와 정확한 artifact

| 역할 | exact path | SHA-256 |
|---|---|---|
| 잠정 parent A | `coordination/proposals/claude/exp006/submission.tar.gz` | `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` |
| 현재 B | `releases/public-thomas-replay-router-v2-exact/submission.tar.gz` | `8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180` |
| 폐기한 EXP-008 main.py | `experiments/candidates/exp008_opening_liquidity/main.py` | `930ed160a1696ca9118b2f6704112a181e528bf2c7c9fafac5db76518f87f079` |
| EXP-008 판정 | `evidence/raw/EXP-008/verdict.json` | `9e8cabf4020607abf193ded71071807a8bc9165cba2a95c03180c8a291622d43` |
| frozen EXP-008 card | `experiments/cards/EXP-008-opening-liquidity.md` | `e0e93652991005514bb37f11cf9c69be6d07739594cfee4760ac8792ff30773a` |
| 현재 schema 3 계측 | `tools/instrument.py` | `83861d7abd4845e3c8349e98fc2a95ad6a46af49dc755294ddefbf78adeafd6b` |

`[LOCAL]` 위 SHA는 이번 세션에서 재계산했다. EXP-008은 당시 계측 SHA `6c0b36af…fedd`로 실행됐으므로 현재 schema 3으로 이미 재실행한 것처럼 서술하지 않는다.

재개 순서: `AGENTS.md → coordination/BOARD.md → plan/CURRENT.md → HYPOTHESES.md → evidence/FACTS.md·KILLS.md → 최신 report → 해당 card`.
과거 TASKS의 ‘다음 작업’·미실행 문구는 이 현재 계획보다 오래된 기록이며, owner 반영 전까지 [이관안](../coordination/proposals/codex/20260915-owner-record-sync.md)의 상태 차이를 함께 읽는다.

다음 행동 두 가지: **① P1 공개 source triage·최신 24시간 episode 조사와 EXP-008 결과 기록을 마무리한다. ② 고정 manifest로 actual parent tar preflight를 끝내고, PASS와 원인 근거가 함께 있을 때만 첫 새 전략 카드로 넘어간다.**
