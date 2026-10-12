# Kaggriculture 실험 로그 (EXPERIMENT_LOG)

> 대회: Kaggle **Kaggriculture** (2인 농장 시뮬레이션, 최종 순위 = Bradley-Terry) · 팀 **Sian** (솔로)
> 기간: 2026-09-02 계획 시작 → 2026-09-30 23:59 UTC 최종 제출 마감 · 최종 BT 평가 기간 약 10-01~10-15
> 작성: 2026-10-01, Claude (claude-opus-5-5). 작업 폴더 `experiments/`·`evidence/`·`coordination/`·`analysis/`·`releases/`, 그리고 프로젝트 문서 `claude/00~60`을 원본으로 삼아 재구성했다.
> 이 파일은 **색인이자 이야기**다. 숫자는 원본 문서에서 그대로 옮겼다. 원본끼리 값이 다르면 §10에 둘 다 남겼다.

---

## 0. 읽는 법

| 알고 싶은 것 | 볼 곳 |
|---|---|
| 1분 요약 | §1 TL;DR |
| 점수가 어떻게 움직였나 | §2 점수 궤적 · §3 제출 원장 |
| 왜 그 방향으로 갔나 (흐름) | §4 단계별 흐름 (Phase 0~7) |
| 실험 하나를 찾고 싶다 | §5 실험 대장 (한 줄 표) → §6 실험 카드 |
| 로컬 검증이 hosted를 맞췄나 | §7 CV↔LB 대조 |
| 무엇이 효과 있었나/없었나 | §8 What worked / What didn't |
| 다음 대회에 가져갈 것 | §9 교훈과 체크리스트 |
| 모순·빠진 데이터 | §10 |
| 판정 규칙·KILL·용어·원본 파일 | §11 부록 |

**표기 규칙**
- 시각: 제출 시각은 **UTC**(Kaggle CLI 기준)로 쓰고, 필요한 곳에 KST(=UTC+9)를 괄호로 붙였다. 원본이 KST만 적은 경우는 KST로 표시했다.
- 점수: `hosted` = Kaggle 서버 레이팅(새 제출은 600에서 시작해 약 12시간에 걸쳐 수렴). `local` = 우리 기계에서 돌린 판정.
- 판정 단어는 원본 그대로 쓴다: `PASS / FAIL / SUCCESS / FAILURE / INCONCLUSIVE / INVALID / STOP / BLOCKED / NO CLUE`.
- `[사실]`은 원본에 적힌 것이다. `[해석]`은 이 로그를 쓰며 Claude가 붙인 판단이며, 사실과 섞지 않았다.
- ID: `EXP-NNN` = 사전등록 카드가 있는 실험. `ANL-*` = 분석·수집·조사(카드 없음). 제출물은 라벨(예: `d157`, `L4p`)로 부른다.

---

## 1. TL;DR

**최종 상태 [사실]**
- 최종 활성 두 슬롯: **L4pc `56709992`** (d157 + glut-lead K=4의 사본) + **d157c `56709342`** (d157 사본). 둘 다 COMPLETE, 실전 오류 0.
- 10-01 05:47 KST 표시 점수: L4pc 1587.0, d157c 1622.2 → 팀 **1622.2, 1,855위 / 10,230팀**. 같은 시점 동메달선(1,023위) **1852.0**, 은메달선 2079.2. (재제출본이라 600에서 다시 수렴하는 중이었다.)
- 대회 중 최고 관측: **EXP-016 2425.7** (09-23, 약 808위, 당시 동메달권 안), **P2 lynnsakurai exact 2421.6** (09-19, 949위, 동메달선 +2.7), **d157 2400.9** (09-28, 제출 21시간 뒤).
- 최종 BT 순위는 아직 기록되지 않았다 (평가가 10-15 무렵까지 계속된다).

**흐름 한 줄**: 규칙기반 봇(hosted ≈340) → 공개 상위 봇의 **tape 재생**으로 전환(≈2,190) → 공개 노트북 **exact 복제를 돌려가며 제출**해 잠깐 동메달권(≈2,420) → 공개 상위 계열(127ed3e6, 55be)에 **상수 1개 바꾸기** 탐색(d157 ≈2,400) → 마지막 사흘은 d157 개선과 슬롯 분산을 시도했지만 로컬 우위가 hosted에서 재현되지 않았고, 마감 직전 재제출로 슬롯 점수가 600에서 다시 시작했다.

**가장 중요한 교훈 다섯 [해석]**
1. **로컬 지표는 hosted 순위를 거의 예측하지 못했다.** EXP-017은 로컬에서 EXP-016을 78/0/2로 이겼지만 hosted에선 165.6점 낮았다. c26은 tape에서 d157보다 +0.033이었지만 hosted에선 더 낮게 표시됐다. L5p는 사전 조건 A8을 통과했지만 이어진 검증에서 L4p에 역전됐다. 반대로 INCONCLUSIVE였던 EXP-016이 대회 최고점을 냈다 (§7).
2. **이 대회에서 점수를 크게 올린 것은 우리 코드가 아니라 어떤 공개 봇 계보를 고르느냐였다.** 340 → 2,188 → 2,420은 모두 공개 코드 복제로 얻었다. 우리 변경 중 확실히 이득을 낸 것은 d157(상수 1개)과 EXP-016(판매 레이어 이식) 정도다.
3. **hosted 상대를 tape로 재생하면 실제 경기가 정확히 재현됐다.** v074 163/163, d157 136/136, v171 107/107이 일치했다. 다만 open-loop라 상대가 반응하지 않으므로 낙관 편향이 있었다(mirror에서 +0.17).
4. **슬롯 교체는 늦을수록 비쌌다.** 최종 BT는 두 제출이 모두 활성인 경기만 센다(F-T12). 그런데 마지막 이틀에 6번 제출했고, 같은 바이트의 d157이 09-28엔 2400.9였는데, 09-30에 다시 낸 사본(d157c)은 10-01 05:47 KST에 1622.2로 표시됐다(리그 전체 하락분도 섞여 있다).
5. **기록 규율은 오류를 여러 번 잡아냈다.** 사전등록, SHA 원장, 독립 검토가 stale artifact(EXP-001), wrapper 자기참조(INFRA-BUG-001), seat 오류(EXP-025b), gate 정의 오류(F-T7) 등을 걸렀다. 하지만 09-16~18 정합성 작업(P1b·EXP-011·EXP-013)에 사흘을 쓰는 동안 제출 개선은 없었고 점수는 1,915에서 1,638로 떨어졌다.

**비전공자용 세 줄**
- 처음엔 농사 규칙을 직접 짰지만 상위권 봇과 400판 중 한 판도 못 이겼다. 상위권은 "잘 된 경기 기록을 통째로 따라 하는 봇"을 쓰고 있었다.
- 그래서 공개된 강한 봇을 그대로 가져와 제출하고, 숫자 하나씩 바꿔 보며 더 나은 버전을 찾았다. 한때 동메달 선을 넘었다.
- 우리 컴퓨터에서 "더 낫다"고 나온 버전이 실제 리그에서는 자주 더 못했다. 마지막에 여러 번 갈아 끼우면서 점수가 처음부터 다시 쌓이는 상태로 마감했다.

---

## 2. 점수 궤적

### 2.1 팀 점수와 메달선 [사실]

| 관측 시각 | 팀 수 | Sian 점수 (순위) | 동메달선 | 은메달선 | 그때 활성 슬롯 |
|---|---|---|---|---|---|
| 09-07 06:20 UTC | 7,963 | 314.8 (6,989) | — | — | v0 |
| 09-09 07:30 UTC | 8,341 | 330.6 (7,253) | — | — | v0 |
| 09-10 23:16 UTC | (08:34 CSV 8,481) | **2188.4** | — | 500위 2,537.4 | v1, yhay81-exact |
| 09-15 | — | 1862.6 (1,724) | — | — | EXP-006, EXP-007 |
| 09-16 | 9,234 | 1726.6 (2,005; Gemini 기록 2,007) | 923위 2,442.5 | 461위 2,679.7 | EXP-006, EXP-007 |
| 09-18 | 9,423 | 1638.5 (2,201) | ~942위 2,395.3 | ~471위 2,648.1 | EXP-006, EXP-007 |
| 09-19 15:20 UTC | ~9,550 | **2421.6 (949, 동메달권)** | 955위 2,418.9 | 477위 2,652.6 | yhay81 재제출, P2 |
| 09-20 | ~9,594 | 2410.4 (1,017) | 959위 2,444.5 | — | P2, alperen |
| 09-23 | 9,886 | **2425.7 (≈808, EXP-016)** | 988위 2,346.1 | — | C1, EXP-016 |
| 09-24 | 9,942 | — | 994위 2,302.8 | — | EXP-017, DP |
| 09-28 05:27 UTC | 10,105 | 2381.4 (354) | ~1,010위 2,096.5 | 505위 2,308.7 | v074, d157 |
| 09-28 23:38 UTC | 10,139 | 2198.8 (612) | ~1,013위 2,042.8 | ~506위 2,252.7 | d157, c26 |
| 09-29 11:45 UTC | 10,157 | 2127.1 (671) | 1,015위 1,983.1 | 507위 2,206.9 | d157, c26 |
| 09-29 23:33 UTC | — | 1861.6 (1,178) | 1,916.2 | — | X, d157r |
| 10-01 05:47 KST | 10,230 | **1622.2 (1,855)** | 1,023위 1,852.0 | 2,079.2 | L4pc, d157c |

- 동메달선은 09-20의 2,444.5에서 마감 직전 1,852.0까지 내려갔다. 리더보드 전체가 하락한 것이다.
- 신규 제출은 600에서 시작해 약 12시간에 걸쳐 수렴한다 (`evidence/FACTS.md`).
- 공개 노트북에 적힌 점수는 저자의 실제 제출 점수가 아니다. Thomas는 실제 13위 2,986.6이었지만 우리가 낸 사본은 1,635.9였다 (F-T18).

### 2.2 제출물별 hosted 최고·최종 관측 [사실]

```
v0              ███ 314.8 → 347.2
v1              ███ 343.9
yhay81-exact    ██████████████████████ 2188.4 → 2081.8
EXP-006         ███████████████████ 1915.6 → 1638.3
EXP-007         ██████████████████ 1819.8 → 1467.3
yhay81 재제출   ███████████████ 1538.9 → 1483.8
P2 lynnsakurai  ████████████████████████ 2421.6 → 2410.4
P1 alperen      ███████████████ 1471.3
P2 control      ██████████████████████ 2161.9
C1 pipe16       ██████████████████████ 2206.6
EXP-016         ████████████████████████ 2425.7 → 2265.8   ← 대회 최고
EXP-017         █████████████████████ 2100.2 → 2010.8
DP 0924         ██████████████████████ 2191.6
127ed3e6        ███████████████████████ 2314.7 → 2251.0
v171            ███████████████████████ 2337.5 → 2211.7
v074            ██████████████████████ 2215.9 → 2068.4
d157            ████████████████████████ 2400.9 → 2127.1
c26             ███████████████████ 1939.7 → 1925.9
X Rc26_107      █████████████████ 1658.1
d157r           ███████████████████ 1888.4 → 1844.5
L4p             ██████████████████ 1800.5 → 1784.0
L5p             █████████████████ 1713.7 → 1712.9
d157c (최종)    ████████████████ 1622.2   (재수렴 중)
L4pc (최종)     ████████████████ 1593.4   (재수렴 중)
```
(막대 1칸 ≈ 100점, 첫 값 또는 최고 관측값 기준. 관측 시각이 제출마다 달라 같은 시점 비교가 아니다.)

---
## 3. 제출 원장 (모든 Kaggle 제출, 시간순) [사실]

규칙: 하루 5개까지 제출할 수 있고, 최신 2개만 활성이다(새 제출이 들어오면 가장 오래된 것이 은퇴, FIFO). 최종 평가도 최신 2개로 한다. 원본: `evidence/HOSTED_LEDGER.md`, `experiments/exp062/subs_*.txt`, `analysis/hosted_*/subs.txt`.

| # | 제출 (UTC) | 라벨 | submission ID | artifact SHA | 계보 / 바꾼 것 | 제출 근거 (로컬 판정) | hosted 관측 | 은퇴 |
|---|---|---|---|---|---|---|---|---|
| 1 | 09-07 04:36 | v0 | 56068891 | tar `aed79ff3…` | 규칙기반 최소 봇 | 파이프라인 검증 (vs starter 40/0/0) | 314.8 → 337.2 → 347.2 | yhay81-exact 제출 때 (FIFO 추정) |
| 2 | 09-10 13:36 | v1-20260910 | 56145245 | tar `723f8fd8…` | v0 + 땅·일꾼·작물 조정 (EXP-001) | 측정용 (성능 가설 없음) | 343.9 → 316.4 | EXP-006 |
| 3 | 09-10 15:57 | yhay81-exact | 56147691 | tar `40d2bc39…` | 공개 9위 yhay81 tape router 무수정 | 사람 결정 (preflight HOLD, gate 정의 오류) | **2188.4** → 2081.8 | EXP-007 |
| 4 | 09-11 12:58 | EXP-006 clone-preempt | 56165718 | tar `1c478c24…` | #3 + clone 상대 선행매도 | SUCCESS (h2h 20-0-0) | 1915.6 → 1862.6 → 1638.3 | yhay81 재제출 |
| 5 | 09-12 01:13 | EXP-007 thomas exact | 56175620 | tar `8031d51a…` | 공개 thomas router v2 무수정 | SUCCESS (검증자 "제출 불가" 의견 병기) | 1819.8 → 1647.4 → 1467.3 | P2 |
| 6 | 09-18 ~13:00 | yhay81 재제출 | 56330776 | `40d2bc39…` (#3과 같은 바이트) | #3 | 동메달 목표 전환 직후 | 1538.9 → 1483.8 | alperen |
| 7 | 09-19 | P2 lynnsakurai v2 exact | 56347732 | tar `1178ffa0…` | 공개 lynnsakurai v2 | F0 fast lane gate PASS, round-robin 0.9667 | **2421.6 (949위, 동메달권)** → 2410.4 | EXP-014 쌍 |
| 8 | 09-20 | P1 alperen exact | 56363545 | tar `cce494e5…` | 공개 alperen | F0 gate PASS | 1471.3 | EXP-014 쌍 |
| 9a | 09-20 14:51 | EXP-014 mirror sale lead | 56398297 ⚠️ | tar `be529b5c…` | P2 + `_ADV_LOOK` 3→4 | EXP-014R INCONCLUSIVE (22.0/30) | 미기록 | (중복 제출 혼선) |
| 9b | 09-20 14:51 | P2 control 사본 | 56398299 ⚠️ | `1178ffa0…` | #7 사본 | 대조군 | 2161.9 | C1 |
| 10 | 09-21 03:35 | EXP-014 재제출 | 56415087 | `be529b5c…` | #9a | 위와 같음 | 미기록 | EXP-016 |
| 11 | 09-21 11:07 | C1 nathanjacob pipe16 exact | 56426857 | main `827ddf29…` | 공개 pipe16 | vs P2 20/0/0 | 2206.6 | EXP-017 |
| 12 | 09-22 08:29 | EXP-016 C1 + sale advance | 56458814 | tar `4071f6c5…` | C1 + V53 sale-advance 레이어 | INCONCLUSIVE (P_c2 +6 > 2), 사람 결정 | **2425.7 (≈808위)** → 2265.8 | DP |
| 13 | 09-23 09:59 | EXP-017 OMW + sale advance | 56490029 | tar `177eedc0…` | OMW + sale-advance | SUCCESS (vs EXP-016 78/0/2) | 1985.2 → 2100.2 → 2010.8 | 127ed3e6 |
| 14 | 09-24 10:26 | DP 0924 exact | 56518910 | tar `1f88c3e7…` | 공개 tetsutani demand-preserving | 사람 "B안" (step-91 봇 식별 후 exact) | 2069.1 → 2191.6 (예상 2450~2550은 오류로 정정) | v171 |
| 15 | 09-25 11:48 | 127ed3e6 exact | 56549720 | tar `63e1554c…` | 공개 newmeta 127ed3e6 | DP80 0.825, D3 v2 PASS | 2165.6 → 2314.7 → 2251.0 | v074 |
| 16 | 09-26 (시각 미기록) | v171 | 56567563 | tar `998b46c5…` | 127ed3e6 계열 + `_DP_H` 8→9 | EXP-023 Stage 3 SUCCESS | 2337.5 → 2211.7 | d157 |
| 17 | 09-26 (시각 미기록) | v074 | 56577440 | tar `a8f43236…` | v171 + `V9_RACE_DEFAULT` 44→45 | EXP-024 Stage 3 SUCCESS | 2215.9 → 2068.4 | c26 |
| 18 | 09-27 12:00 | d157 | 56607884 | tar `4281ea3c…` | 공개 55be5d5f + `_S1002_PASSES` 34→35 | EXP-035 PASS (tape +0.29) + 사람 위험 감수 방침 | 2299.7(12h) / **2400.9(21h)** → 2127.1 | X |
| 19 | 09-28 08:45 | c26 | 56635330 | tar `8961e03e…` | d157 + `_CA_MARGIN` −15→−26 | EXP-039 FAIL(frozen). 사람 방침 "슬롯2 공격적 후보 허용" 아래 제출 | 717 → 1939.7 → 1925.9 | d157r |
| 20 | 09-29 12:35 | X = Rc26_107 | 56675447 | tar `03bde595…` | c26 + mirror 판에서 route 107 | slot2-R holdout PASS | 1016.9 → 1658.1 | L4p |
| 21 | 09-29 12:36 | d157r (재제출) | 56675458 | = #18 바이트 | #18 | X와 짝 맞추기 | 831.7 → 1888.4 → 1844.5 | L5p |
| 22 | 09-30 02:32 (11:32 KST) | L4p | 56694892 | tar `e458957d…` | d157 + glut lead K=4 | EXP-062 S2 하한 −0.002 (기준 "하한 > 0" 미달), 위험 감수 방침 | 600 → 1800.5 → 1784.0 | d157c |
| 23 | 09-30 11:17 (20:17 KST) | L5p | 56705818 | tar `748c722c…` | d157 + glut lead K=5 | EXP-062 A8 통과 (이후 A11에서 역전) | 1691.5 → 1713.7 → 1712.9 | L4pc |
| 24 | 09-30 13:56 (22:56 KST) | **d157c** (최종) | **56709342** | = #18 바이트 | d157 사본 | 최종 조합 A | 1121.0 → **1622.2** (10-01 05:47 KST) → 1618.8 (07:15 KST) | — |
| 25 | 09-30 14:24 (23:24 KST) | **L4pc** (최종) | **56709992** | = #22 바이트 | L4p 사본 | 최종 조합 A | → **1587.0** (10-01 05:47 KST) → 1593.4 (07:15 KST) | — |

⚠️ #9: `HOSTED_LEDGER.md`의 표는 56398274/56398276이라고 적고, 같은 파일의 정정 문단은 56398297/56398299라고 적는다(§10-1).
마감 시점 활성 슬롯은 **{L4pc 56709992, d157c 56709342}**다. 당일 남은 제출 1회는 복구용으로 봉인했다.

---

## 4. 단계별 흐름 (Phase 0 → 7)

각 단계를 *질문 → 한 일 → 알게 된 것 → 다음 단계로 넘어간 이유* 순서로 적었다.

### Phase 0 · 계획과 측정 장비 (09-02 ~ 09-06)
- **질문**: 엔진이 실제로 어떻게 돌아가고, 무엇을 측정해야 하나?
- **한 일**: Claude·Codex·Gemini가 각자 쓴 계획서를 서로 검토해 최종 계획 하나로 정리했다(`proj 00~04`). 엔진 `kaggle-environments==1.32.7`을 고정했다. S4~S8 하니스(공식 3봇 완주, 무음 실패 계측기, paired arena)를 만들었다.
- **알게 된 것 [사실]**: 세 계획서의 경제 모델이 틀렸다("딸기·우유·양털은 함정" 등). 시장은 두 플레이어가 함께 쓴다. docs 검토 결론은 "상위권은 룰베이스를 짜지 않는다. 720턴 tape를 추출해 재생한다"(8개 중 6개 노트북)였다. S6의 "starter 무음 실패 147"은 계측기 귀속 버그로 철회했다.
- **다음으로**: 첫 제출은 성능이 아니라 파이프라인 검증용 최소 봇으로 하기로 결정했다.

### Phase 1 · 규칙기반 봇 (09-07 ~ 09-09)
- **질문**: 직접 짠 실행기(executor)를 단계별로 키우면 공개 상위 봇을 이길 수 있나?
- **한 일**: v0 제출(hosted 314.8, 6,989위). EXP-001(땅·일꾼·작물 수)을 돌렸고, 중간에 stale artifact로 결과 6건이 무효가 되어 재실행했다. EXP-002(MELON/STRAWBERRY 전환), EXP-003(흡수량 맞춤)을 돌렸다. EXP-004(동물)는 사전등록만 했다. 부검으로 ACTION_BUDGET·PASS_DIAGNOSIS·ABSORPTION 엔진 사실을 정리했다.
- **알게 된 것 [사실]**: 공개 4봇 상대 **0/0/400**. EXP-002 후보도 0/0/400이었다(평균 마진 −105,573). v0와 상위 봇의 6~9배 격차는 작물 효율 차이가 아니라 동물·비료 레이어가 통째로 없어서 생긴 것이었다. 상점 해금은 3일마다 8개였고 시즌 흡수 총량 추정을 160,035에서 206,190으로 고쳤다. EXP-003의 −98.0은 측정 불가(MDE ±1,674)인데도 K10으로 KILL했다가 09-10에 철회했다.
- **다음으로 [사실]**: 09-10 RESET. 근거는 넷이다. 제출은 총량이 아니라 하루 5개다. 4봇 검증 풀의 천장은 59위다. 정지는 곧 후퇴다. 공개 9위 yhay81 tape router는 hosted 2,188이다.

### Phase 2 · RESET → tape router 계열 (09-10 ~ 09-15)
- **질문**: 남의 tape를 재생하는 봇이 우리 실행기보다 강한가? 강하다면 그 위에 무엇을 얹을까?
- **한 일**: 47개 tape × 940판 재생 계측(F-T1~F-T6), yhay81 exact 제출(2188.4). EXP-005(X1 매도 레이어 교체) FAILURE. EXP-006(clone 선행매도) SUCCESS → 제출. EXP-007(thomas router, 다른 계보) SUCCESS → 제출. EXP-006 hosted 패배를 부검한 뒤 EXP-008(첫 턴 시장 일정 A→B)을 돌렸고 FAILURE였다. 09-15 마감 계획을 세웠다(09-27 새 전략 중단, 09-29 제출 완료 목표).
- **알게 된 것 [사실]**: 순수 tape 재생이 main.py를 뱅크 +79,744, 929/11로 압도했다. 엔진은 로컬에서 결정론적이다(F-T4). open-loop farm tape 위에서 매도 레이어만 바꿔도 농장 계획이 어긋난다(F-T10). `sell_unfilled` gate는 n=1000 sentinel을 손실로 세는 정의 오류였다(F-T7). 최종 BT는 두 제출이 모두 활성인 경기만 센다(F-T12). 그래서 슬롯 교체는 늦을수록 비싸다.
- **다음으로**: 활성 두 슬롯(EXP-006, EXP-007)이 매일 하락했다(1915→1862, 1819→1636). 다음 후보를 내기 전에 release gate를 실제 tar로 검증하는 단계(P1)를 먼저 넣었다.

### Phase 3 · 정합성·귀인 작업 (09-16 ~ 09-18)
- **질문**: 현재 parent가 zero-gate를 통과하나? 실패하면 원인은 무엇인가?
- **한 일**: P1b actual-tar preflight 13판(LOCAL FAILURE, zero gate 16/16 FAIL). EXP-011 shed-discard 귀인(측정 PASS, 인과 해석은 독립 검토에서 FAIL, EXP-012 사전등록 불가로 종결). EXP-013 hire recovery는 사전등록 r1~r3까지 갔지만 미실행. P1c hosted 77판 감사(추천 가설 0). TOP10 donor 재현(7190/7190 exact).
- **결정 [사실]**: 09-16 사람이 목표를 "**점수를 지킬 필요 없어. 최소한 동메달을 확보하기 원해**"로 바꿨다. 09-18에는 K3 범위를 "market 기록만 떼어 붙이기 금지"로 좁히고 **F0 fast lane**(공개 노트북 exact 복제를 gate §3-2만으로 제출)을 승인했다.
- **결과 [사실]**: 이 기간에 우리 개선으로 나간 제출은 없다. 활성 슬롯 점수는 1862.6에서 1638.5(2,201위)로 떨어졌다.

### Phase 4 · F0 fast lane, 공개 exact를 돌려가며 제출 (09-19 ~ 09-24)
- **질문**: 지금 가장 강한 공개 계보는 무엇이고, 그 위에 얹을 1요인은 무엇인가?
- **한 일**: donor tape 재생은 full_match 0/52로 실패했다. 공개 노트북 exact 3개(P1 alperen, P2 lynnsakurai, P3 tetsutani)를 만들어 P2를 제출했고 **2421.6, 동메달권**에 들었다. lineage 분류, DIFFERENT 계보 3개는 부적격. EXP-014/015 mirror 조정(INVALID) → EXP-014R INCONCLUSIVE → 제출. 2945-line 탐색에서 C1 pipe16 제출. C1 패배 분석으로 V53 sale-advance가 빠진 것을 찾아 EXP-016을 만들었고 **2425.7로 대회 최고**를 냈다. step-53 봇 식별(OMW) → EXP-017 SUCCESS → 제출했지만 hosted에선 EXP-016보다 −165.6. step-91 봇 식별 → DP 0924 exact 제출(2191.6).
- **알게 된 것 [사실]**: 엔진 진입점은 *마지막 callable*이었다(instrument.py가 다른 함수를 테스트하던 결함을 수정). 공개 계보를 바꾸면 hosted가 수백 점 움직였다. "로컬 sibling 맞대결은 hosted 순위를 예측하지 못한다"는 ledger 메모가 남았다(EXP-016/017).
- **다음으로**: 09-23 CANDIDATE-POLICY(slot A/B, rollback 규칙). 09-25에는 하루 1실험 체제를 버리고 *동결 목표 지표 + 자율 탐색 + 사전 고정 holdout* 방식으로 가기로 했다.

### Phase 5 · 동결 지표 탐색 루프 시도 → 상수 knife-edge 탐색 (09-25 ~ 09-27)
- **질문**: 고정된 자동 평가 지표로 공개 최강 계열을 넘는 변형을 찾을 수 있나?
- **한 일**: EXP-018(DP 1요인, DP floor 미달 NOT_ELIGIBLE). 127ed3e6 exact 평가(DP80 0.825). runtime gate를 0.25s에서 엔진 한도 기반 **D3 v2**로 재정의(사후 변경으로 기록)하고 제출(2314.7). parent tournament. **metric calibration BLOCKED**(변별력 거의 0, 실행 이상 5) → 루프 정지. EXP-021/022 mirror-edge STOP/FAIL(행동이 parent와 같음). P4/P4b tape fidelity(ρ 0.90, SUCCESS). EXP-023 상수 ±1 screen에서 v171 선택 → 제출(2337.5). EXP-024 round2(INFRA-BUG-001 수정 후) v074 → 제출(2215.9). EXP-025 hosted 107판 검증, ±1 회복 가설 폐기. EXP-026/027 near-clone. 55be5d5f 발견 → EXP-028 HOLD. EXP-029 mirror screen에서 d157 후보. EXP-030/032 FAIL. EXP-033 Kaggle kernel로 tape 실행, hosted 경기 163/163·136/136 재현. **EXP-035 d157 PASS** → 제출(21시간 후 2400.9).
- **결정 [사실]**: 09-27 20:07 사람 방침 "**메달권 밖이면 위험 감수**"로 Codex의 NO_SUBMISSION 판단을 override했다. 21:36에는 "v171/v074 exact 재제출 금지, 둘째 슬롯은 d157 + 개선"이 나왔다.

### Phase 6 · d157 개선과 슬롯 분산 (09-28 ~ 09-29)
- **질문**: d157이 지는 상대를 이기는 변경이 있나? 두 슬롯이 같은 계열이라는 위험은 어떻게 줄이나?
- **한 일**: EXP-036 d157 ±1 158변형 FAIL(상수 ±1은 tape 상대에게 거의 무효과). EXP-038 55be family 중 d157이 최강. EXP-039 `_CA_MARGIN` grid FAIL(frozen) → 사람 방침 "슬롯2는 공격적 후보 허용"(14:05) 아래 c26 제출(제출 결정 자체의 기록은 원본에 없음). EXP-040~042 LB≥2400 tape 743개 수집·평가(c26−d157 +0.033). EXP-043 oracle NO CLUE. EXP-044~048 판매·상대모형 hook FAIL. EXP-053~055 tomato/Fritz 라인 FAIL. EXP-056 공개 family FAIL. EXP-057 geese FAIL. EXP-058S route 재배정 FAIL. slot2 다양화 검토 끝에 RL 제외, Fritz식 재설계 12변형 전부 FAIL. **slot2-R mirror gating Rc26_107 holdout PASS** → X·d157r 제출.
- **결정 [사실]**: 09-28 22:10 "**제출하지 않음은 없다. 계속 개선한다.**" 09-29 다른 팀의 전체 경기 기록(farmer+hands+market)을 route로 쓰는 것을 허용하고, 밤사이 무인 운영을 시작했다.
- **알게 된 것 [사실]**: c26은 tape에서 d157보다 +0.030~+0.033이었지만 hosted에선 1,887~1,940 대 d157 ~2,200으로 반대였다. 공통 상대는 331판 중 0개였다. "c26 ≥ d157" 판단은 team-best LB 편향 때문이었다며 doc 45에서 철회했다.

### Phase 7 · 마지막 날 (09-30 ~ 10-01)
- **질문**: 남은 하루에 현재 점수대에서 지는 상대를 이기는 개선을 넣을 수 있나?
- **한 일**: READOUT0930(X vs d157r, combined −0.028, cannot judge). EXP-060 MBR(mirror route 재배정, 최종 FAIL, 제출 없음). EXP-061 donor route 29개 중 27 fail(DN29만 채택). Codex 사용량이 소진되어 Claude가 실행을 넘겨받았다. **EXP-062 glut lead**: hosted 542판 분석 → private 55be 변형 상대 패배가 64%라는 진단 → L3p~L6p를 만들어 L4p 제출(S2 하한 −0.002로 "하한 > 0" 기준 미달이지만 위험 감수 방침), L5p 제출(A8 통과) → A11/S8에서 L5p가 L4p보다 −0.058로 역전 → 최종 조합 A = {L4p 사본, d157 사본}.
- **결정 [사실]**: 09-30 사람이 Claude의 직접 제출(Mac kaggle CLI)을 허용했다. 21:00 KST를 새 후보 시한으로 정했다. 22:50 조합 A를 결정했다. Sol 7차 검토는 L4p 사본 즉시 제출에 동의하고, X454 기준을 사후 완화하는 것에는 반대했다.
- **결과 [사실]**: 10-01 05:47 KST 1622.2, 1,855위(동메달선 1852.0). 09-30 22:42 수집에서 L4p·d157r은 1800–2000 상대 0.50/0.45, 2000–2200 상대 0.29/0.33이었다(doc 60: "1800 이상 상대에게 5할 미만 — 동메달까지 남은 과제").

---
## 5. 실험 대장 (한 줄 표)

열 설명: **변경** = parent 대비 바꾼 것(1요인이 원칙). **로컬 결과** = 사전등록 지표의 핵심 수치. **판정** = 원본 단어. **제출** = submission ID (없으면 —).
상세는 §6의 같은 ID 카드를 본다.

| ID | 날짜 | Ph | parent | 변경 | 로컬 결과 (핵심) | 판정 | 제출 → hosted |
|---|---|---|---|---|---|---|---|
| S4–S8 | 09-06 | 0 | — | 하니스·v0 gate | v0 vs starter 40/0/0, 마진 +15,280 | PASS | v0 56068891 → 314.8 |
| EXP-001 | 09-07→08 | 1 | v0 | 땅 시점 → 일꾼 수 → 당근 칸 (3단계 순차) | 일꾼 9 (40/0/0), 당근 15; 1차 실행 6건 stale로 INVALID | SUCCESS(태스크) / HYP LOCAL_SUPPORTED | v1 56145245 → 343.9 |
| EXP-002 | 09-08→09 | 1 | v1 | 작물 MELON 30 / STRAWBERRY 30 | vs 공개 4봇 **0/0/400**, 마진 −105,573 | FAILURE | — |
| EXP-003 | 09-09 | 1 | v2c_c3 | MELON 30→3 (흡수량 맞춤) | 평균 bank −98.0 (p≈0.87, MDE ±1,674) | FAILURE → K10 등재 → 09-10 RETRACTED | — |
| EXP-004 | 09-10 | 1 | v2c_c3 | 동물 레이어 (소·양) | 미실행 (RESET으로 중단) | PLANNED | — |
| ANL-TAPE | 09-10 | 2 | main.py | 순수 tape 재생 | 재생이 bank +79,744, 929/11 | 사실 F-T1~5 | — |
| yhay81-exact | 09-10 | 2 | — | 공개 9위 무수정 | vs 47 tape 452-0-18 (0.9617) | HOLD → 사람 제출 | 56147691 → **2188.4** |
| EXP-005 | 09-11 | 2 | yhay81 | 7개 산출물 SELL 레이어 교체 (X1) | Δpool −0.1915, 안전 gate 위반 (discard 81, end_units 28) | FAILURE | — |
| EXP-006 | 09-11 | 2 | yhay81 | clone 상대 선행매도 (preempt) | h2h **20-0-0**, pool b=0 c=0 | SUCCESS | 56165718 → 1915.6 |
| EXP-007 | 09-11 | 2 | (다른 계보) | thomas router v2 exact | pool 0.9433, A셀 4, public 40-0 | SUCCESS (검증자 반대) | 56175620 → 1819.8 |
| EXP-008 | 09-14 | 2 | EXP-006 | step 1 시장 일정 A→B | target 0/0/2, pool c=2, 회귀 72건, parity 38셀 위반 | FAILURE | — |
| EXP-009/010 | 09-14 | 2 | — | (market preempt / animal guard 초안) | 카드 없음, proposal BLOCKED | 결번 | — |
| ANL-P1b | 09-16 | 3 | EXP-006 tar | parent zero-gate preflight 13판 | zero gate FAIL 16/16 (noop 3,488, discard 482) | LOCAL FAILURE | — |
| EXP-011 | 09-16→18 | 3 | EXP-006 | 측정만 (shed-discard 귀인) | C* S1 64/64, S2 416/418, sole-top 16/16 | PASS / 인과 해석 기각(독립 검토) | — |
| EXP-012 | 09-18 | 3 | — | — | "사전등록 불가로 종결" | 결번 | — |
| EXP-013 | 09-17 | 3 | EXP-006 | 상태 조건부 HIRE 회복 레이어 | 미실행 (사람 불허) | PLANNED | — |
| ANL-P1c | 09-18 | 3 | — | hosted 77판 감사 | Gemini 주장 다수 반박, 추천 가설 0 | 근거 부족 | — |
| ANL-F0 donor | 09-18→19 | 4 | — | donor tape 재생 | full_match 0/52 | target 없음 | — |
| ANL-F0 exact | 09-19 | 4 | — | 공개 P1/P2/P3 exact | round-robin P2 0.9667 | gate PASS | P2 56347732 → **2421.6** / P1 56363545 → 1471.3 |
| ANL-F0 lineage | 09-19→20 | 4 | — | DIFFERENT 계보 3개 | 6쌍 중 5쌍 0/20 | 부적격 | — |
| ANL-P2-LOSS | 09-20 | 4 | P2 | hosted 112판 패배 원인 | 사전 임계 넘는 후보 없음 | 없음 | — |
| ANL-LIVECLAIM | 09-20 | 4 | P2 | 공개 "2749/2820" 변형 | vs P2 0/20; 진입점 결함 발견 | V1 vs V2 INCONCLUSIVE | — |
| EXP-014 | 09-20 | 4 | P2 | `_ADV_LOOK` 3→4 (mirror) | M14 25/0/5, B0 무승부 24/30 < 25 | INVALID | (아래 014R) |
| EXP-015 | 09-20 | 4 | P2 | SELL 묶음 가격 내림차순 | M15 1/0/29 | INVALID (폐기) | — |
| EXP-014R | 09-20 | 4 | P2 | EXP-014 재현 (새 seed) | M14R 22.0/30 (기준 22.5), 회귀 0 | INCONCLUSIVE | 56398297⚠️, 56415087 → 미기록 |
| ANL-2945 | 09-21 | 4 | P2 | 공개 2945-line C1~C5 | C1 vs P2 20/0/0 | — | C1 56426857 → 2206.6 |
| EXP-016 | 09-22 | 4 | C1 | V53 sale-advance 이식 | mirror net +23, panel 손실 55 vs 63, P_c2 +6 | INCONCLUSIVE | 56458814 → **2425.7 (최고)** |
| EXP-017 | 09-22→23 | 4 | OMW | sale-advance 레이어 | A 59/0/21, vs EXP-016 **78/0/2** | SUCCESS | 56490029 → 2100.2 (EXP-016 대비 −165.6) |
| ANL-STEP91 | 09-24 | 4 | — | prefix 91 상대 식별 | X = ahmedberatozer V56(Antigravity). LB 판독에선 V56에 17-9, DP 0924에 0-7 | — | DP 0924 56518910 → 2191.6 |
| EXP-018 | 09-24→25 | 5 | DP 0924 | `_V92_P_EVERY` 3→2 | panel Δ +0.106 > 2SE, DP80 0.4875 < 0.50 | NOT_ELIGIBLE_DP_FLOOR | — |
| EXP-019/020 | 09-25 | 5 | DP / 127ed3e6 | (제안) | 미실행, 탐색 루프로 흡수 | 대체됨 | — |
| ANL-NEWMETA | 09-25 | 5 | — | 127ed3e6 exact | DP80 0.825, E-5 0.80; 0.25s gate NOT_ELIGIBLE → D3 v2 PASS | NOT_ELIGIBLE → PASS | 56549720 → 2314.7 |
| ANL-CALIB | 09-25 | 5 | — | 동결 목표 지표 선택 | 변별력 ≈0, 실행 이상 5 | BLOCKED (루프 정지) | — |
| EXP-021 | 09-25→26 | 5 | e496a4fe | mirror-edge arm (horizon 등) | P/H1a/H1b/H3 모두 0.500, 행동 동일 | STOP → FAIL | — |
| EXP-022 | 09-26 | 5 | — | H2′ | harness KeyError → smoke 불일치 | STOP | — |
| ANL-P4/P4b | 09-26 | 5 | — | tape fidelity | P4 n=2 WEAK → P4b ρ 0.90, D 0.74 | WEAK → SUCCESS | — |
| EXP-023 | 09-26 | 5 | e496a4fe | 상수 ±1 screen (1,870 keys) | v171 vs 127 0.8075 (Wilson99 0.75), DP Δ +0.025 | SUCCESS (v171) | 56567563 → 2337.5 |
| EXP-024 | 09-26 | 5 | v171 | 상수 ±1 round 2 (186변형) | v074 A 0.725, A′ +0.138 | SUCCESS (v074) | 56577440 → 2215.9 |
| EXP-025/025b | 09-26→27 | 5 | v171 | hosted 107판 검증, ±1 회복 | 127 변형 상대 3/3/16; ±1 변형 0/171 | PASS / 회복 가설 폐기 | — |
| EXP-026 | 09-27 | 5 | v074 | near-clone ±1 142변형 (open-loop) | w067 +0.394 (= v111과 같은 변경) | PASS (낙관 편향 지적) | — |
| EXP-027 | 09-27 | 5 | v074 | closed-loop guard | 결과 없음 | 대체됨 | — |
| EXP-028 | 09-27 | 5 | v074 | 55be5d5f exact | pooled Δ −0.084 | HOLD | — |
| EXP-029 | 09-27 | 5 | 55be | mirror ±1 158변형 | d157 o1 0.8 o2 1.0 | screen 완료 | — |
| EXP-030 | 09-27 | 5 | 55be | bypass | b020 −0.083 | FAIL | — |
| EXP-031 | 09-27 | 5 | — | hosted census 350판 | v074 127변형 상대 8/1/43 | (관측) | — |
| EXP-032 | 09-27 | 5 | 55be | Kaggle kernel specialist | d157 transition [0.192,0.141], runtime만 FAIL | FAIL | — |
| EXP-033 | 09-27 | 5 | — | Kaggle kernel tape 실행 | hosted 재현 v074 163/163, d157 136/136 | COMPLETE | — |
| EXP-034 | 09-27 | 5 | — | runtime 측정 | d157 max 0.247s | COMPLETE | — |
| EXP-035 | 09-27 | 5 | v074 | d157 = 55be + `_S1002_PASSES` 34→35 | tape 127변형 +0.522, 전체 +0.29 | PASS | 56607884 → **2400.9** |
| EXP-036 | 09-27→28 | 6 | d157 | ±1 158변형 | best e076 +0.01 | FAIL | — |
| EXP-037 | 09-28 | 6 | — | d157·v074 hosted 수집 | 374판(d157 136), replay 불일치 0 | (관측) | — |
| EXP-038 | 09-28 | 6 | 55be family | family arena | d157 FS 0.7266 최강 | FAIL | — |
| EXP-039 | 09-28 | 6 | d157 | `_CA_MARGIN` −18/−22/−26/−30 | c26 tapeU −0.0037 | FAIL (frozen) | c26 56635330 → 1939.7 |
| EXP-040/041 | 09-28 | 6 | — | LB≥2400 tape 수집 | 743 tape, holdout 5팀 | (수집) | — |
| EXP-042 | 09-28 | 6 | d157 | c26 vs d157 on 2400+ tape | c26−d157 +0.033 (lo95 +0.017) | (지지) | — |
| EXP-043/043b | 09-28 | 6 | d157 | oracle 30봇 × loss tape | 043b 0 qualified | NO CLUE | — |
| EXP-044 | 09-28 | 6 | — | margin 분해 | WOOL r .48, MILK .49 | (분석) | — |
| EXP-045 v2 | 09-28 | 6 | d157 | 판매 변형 11개 | Stage A → 048A/B | → 048 | — |
| EXP-046 | 09-29 | 6 | — | 55be가 상위팀 판매 예측 | recall 0.90 | (분석) | — |
| EXP-047 | 09-29 | 6 | d157 | shadow-55be hook | precision 0.114 | → 048 | — |
| EXP-048A | 09-29 | 6 | d157 | 12변형 × 595 tape | hook +0.0109, K3 +0.0042 | Stage B로 | — |
| EXP-048B | 09-29 | 6 | d157 | hook/K3 확인 3,164판 | hook +.004, K3 −.192 | FAIL (045/047 종료) | — |
| EXP-049~051 | 09-29 | 6 | — | fresh 수집, loss 분석, curpop | private 55be 변형 상대 20-44 | (분석) | — |
| EXP-052 | — | — | — | — | 문서 없음 (`analysis/exp052_oracle` 폴더만) | 미확인 | — |
| EXP-053 | 09-29 | 6 | — | 상위팀 tomato 분석 | Fritz 등 4팀 | (분석) | — |
| EXP-054 | 09-29 | 6 | d157 | `_CXTB_MIN_REVENUE` 9000→7000/6000 | X7 −0.004, X6 −0.084 | FAIL | — |
| EXP-055 | 09-29 | 6 | d157 | Fritz-lite (day 11 딸기→토마토) | F11 −0.372 | FAIL (tomato 종료) | — |
| EXP-056 | 09-29 | 6 | — | 공개 Step1009 family 7봇 | 전부 음수 | FAIL | — |
| EXP-057 | 09-29 | 6 | d157 | geese | G1 −0.061 | FAIL | — |
| EXP-058S | 09-29 | 6 | d157 (비교 c26) | route group 재배정 | best S→107 +0.024, lo95 −0.0125 | FAIL | — |
| EXP-059 | 09-29 | 6 | — | (제안) | "해도 되지만 최선 아님" | 미실행 | — |
| ANL-SLOT2-X | 09-29 | 6 | — | Fritz식 wheat→tomato 12변형 | 전부 −0.15~−0.22 | FAIL | — |
| ANL-SLOT2-R | 09-29 | 6 | c26 | mirror면 route 107, 아니면 c26 | HF 0.571 vs d157 0.462; HT 0.477 vs 0.456 | holdout PASS | X 56675447 → 1658.1 |
| ANL-READOUT | 09-30 | 7 | X, d157r | hosted 비교 195판 | combined −0.028 (−0.074, +0.018) | cannot judge | — |
| EXP-060 | 09-29→30 | 7 | X | mirror route 그룹 배정 (MBR) | M2 채택 3그룹, closed-loop Cc vs 55be 0.550 < X 0.562 | FAIL | — |
| EXP-061 | 09-30 | 7 | — | donor route 29개 | 27 fail, DN29 0.725 | (DN29만 060에 채택) | — |
| EXP-062 | 09-30 | 7 | d157 | glut lead K=3/4/5/6 | L4p S1+S2 +0.079 [+0.030,+0.126]; S2 [−0.002,+0.112] | L4p 제출 (S2 "하한 > 0" 기준 미달) | L4p 56694892 → 1800.5, L5p 56705818 → 1713.7 |
| FINAL-A | 09-30 | 7 | — | {L4p 사본, d157 사본} | S8 L5p−L4p −0.058; S9 통과 후보 없음 | 사람 결정 | **L4pc 56709992, d157c 56709342** |

---
## 6. 실험 카드 (상세)

형식: **가설 / 변경 / 검증 설계 / 결과 / 판정 → 결정 / 제출·artifact / 교훈 / 근거**. 교훈은 원본에 적힌 것만 옮겼고, 원본에 없으면 생략했다. 경로는 작업 폴더 기준이며, `proj NN`은 프로젝트 문서 `claude/NN_*.md`를 뜻한다.

### Phase 0–1 · 규칙기반

#### v0 / S4–S8 — 파이프라인 검증용 최소 봇
- **가설**: 성능 가설 없음 (파이프라인 검증).
- **변경**: NW 25칸에서 밀·당근을 돌리는 규칙기반 봇. 일꾼 4명. 동물·비료·멜론은 의도적으로 쓰지 않음.
- **검증**: 무음 실패 계측(seed 7·11·13), self-play 3판, vs starter 20시드 양좌석 40판, latency.
- **결과**: 무음 실패 0, vs starter **40/0/0**, paired 1.000, 마진 +15,280, latency p99 0.17ms.
- **판정 → 결정**: PASS → 09-07 제출. hosted 314.8(6,989/7,963위) → 337.2. Gemini의 hosted 10판 분석은 no-op 21.6%, Player 1 좌석 1승 5패였다.
- **교훈**: 씨앗이 부족하면 엔진이 해당 PLANT를 전부 PASS로 바꾸는데, 계측기에 잡히지 않는다. starter를 이기는 것은 리그 순위와 무관했다(K5).
- **근거**: `experiments/results/S8_RESULTS.md`, `S4_S7_RESULTS.md`, `coordination/SUBMIT_v0.md`, `evidence/HOSTED_LEDGER.md`

#### EXP-001 — v1 땅 확장 (HYP-0001)
- **가설**: NW 25칸의 남는 액션을 NE·SW에 쓰면 v0보다 W/D/L이 좋아진다.
- **변경**: 3단계를 차례로 했고, 각 단계는 1요인이다. ① 땅 구매 시점 ② 일꾼 수 9/10/12 ③ 당근 칸 5/8/15.
- **검증**: 단계마다 3후보 round-robin, seed 1000–1019 양좌석 40판. 최종 승격은 200시드 400판(CI 하한 > 0.5)로 사전등록.
- **결과**: 땅 = (NE day 6, SW day 10), 일꾼 9(vs 10 40/0/0 +1,263), 당근 15(paired 1.45). correctness gate 13/13 카운터 0. 200시드 최종 승격 판정은 원본에서 찾지 못했다.
- **무효 이력**: 1차 실행 중 다른 작업이 `main.py`를 v0로 덮어써 결과 9건이 INVALID가 됐다. 05:55 UTC에는 결과 6건이 현재 코드보다 먼저 만들어진 stale artifact로 확인됐다(P0). 사전등록 tie-break대로였다면 당근 5가 뽑힐 뻔했다.
- **판정 → 결정**: KAGRI-012 SUCCESS(태스크 완료 의미) / HYP LOCAL_SUPPORTED → 09-10 측정용 v1 제출 343.9(v0와 사실상 같음).
- **교훈**: "wrapper의 assert만으로는 결과가 언제 만들어졌는지 막지 못한다." 이후 결과 JSON에 parent/agent/engine SHA를 기록하게 했다.
- **근거**: `experiments/cards/EXP-001-land.md`, `experiments/results/_INVALID.md`, `coordination/reports/claude/20260907-0555-EXP001-stale-artifact.md`

#### EXP-002 — MELON/STRAWBERRY 작물 전환 (HYP-0002)
- **가설**: WHEAT/CARROT을 MELON/STRAWBERRY 중심으로 바꾸면 공개 4봇 상대 paired score가 오른다.
- **변경**: 단계별 1요인(MELON 15/30/45 → 전환일 → 주문 시각 → STRAWBERRY 0/15/30).
- **검증**: pilot 40판 + stage D 공개 4봇 × 50시드 × 양좌석 = 400판. SUCCESS = 합산 CI 하한 > 0.5 그리고 4봇 중 3봇 개별 CI 하한 > 0.5.
- **결과**: 후보 vs 4봇 **0/0/400**, 마진 −105,573. parent v1도 0/0/400(−121,611). 후보 vs parent 100/0/0.
- **판정 → 결정**: FAILURE. 그래도 §7.1b 탐색층(4봇 평균 뱅크)에 따라 c3를 다음 parent로 삼았다. 이후 "MELON 흡수 30이므로 MELON 최적화는 오류"로 정정했다.
- **교훈**: 0/0/400이면 마진이 16,037 좋아져도 레이팅 개선으로 이어지지 않는다.
- **근거**: `experiments/cards/EXP-002-crops.md`, `coordination/reports/codex/20260909-0156-KAGRI-015.md`

#### EXP-003 — 흡수량 맞춤 작물·판매 (HYP-0003)
- **가설**: 흡수량을 넘긴 MELON 생산을 STRAWBERRY로 옮기면 4봇 상대 평균 bank가 오른다.
- **변경**: 선행 correction으로 MELON 30→3, 회수한 27칸은 STRAWBERRY(1요인).
- **검증**: 4봇 × 50시드 × 양좌석 400판, 평균 bank가 parent 이상이면 PASS.
- **결과**: 29,212.7 vs 29,310.7 = **−98.0**. 상대별 2승 2패, matched median +313. 4봇 W/D/L은 여전히 0/0/400.
- **판정 → 결정**: FAILURE → K10으로 KILL 등재 → **09-10 RETRACTED**(p≈0.87, CI [−1,269, +1,073], MDE ±1,674. 측정할 수 없는 크기였다. 원 보고서는 KILL하지 말라고 했다).
- **근거**: `experiments/cards/EXP-003-absorption.md`, `coordination/RESET_2026-09-10.md` §2, `evidence/KILLS.md`

#### EXP-004 — 동물 레이어 (미실행)
- 사전등록(09-10, H20: 소·양 도입 → pass_rate와 bank가 동시에 개선)했으나 같은 날 RESET으로 실행하지 않았다. HYP-0004 PLANNED. 카드에는 철회된 K10 금지가 남아 있다(§10).
- **근거**: `experiments/cards/EXP-004-animals.md`

#### ANL · 부검과 엔진 사실 (09-06 ~ 09-09)
- v0 vs 공개 4봇 8판 8패. 분기일은 day 5~8. 우리가 0회, 4봇은 전원 사용한 액션: CARE·FEED·COLLECT_FERTILIZER·FERTILIZE·PICKUP·PLACE·BUILD_PASTURE·BUY_ANIMAL·BUY_PRODUCT.
- PASS 42%의 원인은 "생육중이라 할 일 없음"이 83.5%였다. 라우팅 실패(H19-a)와 자본 제약(H19-b)은 둘 다 KILLED.
- 상점 해금은 3일마다 8개(`kaggriculture.py:867,886,118`). 시즌 흡수 총량 206,190, MILK+WOOL이 47.5%. 고정 매도 상한을 버리고 동적 `sell_cap`을 도입했다.
- 공개 상위 봇 4종: BUY_LAND 3구획, 4번째 구획은 전원 미구매(K1), GOOSE 0(K9).
- **근거**: `evidence/POSTMORTEM_4bots.md`, `ACTION_BUDGET.md`, `PASS_DIAGNOSIS.md`, `SLOT_CONTENTION.md`, `ABSORPTION.md`, `ENGINE_ANIMALS.md`, `coordination/reports/cowork/20260909-1930-KAGRI-018.md`

### Phase 2 · tape router

#### ANL-TAPE — tape 재생 계측 (F-T1~F-T6, 09-10)
- **설계**: 47 tape × {boatlee, starter} × 5시드 × 양좌석 = 940판.
- **결과**: 순수 재생이 main.py보다 bank **+79,744** (95% CI [77,597, 81,892]), 929/11. vs boatlee 263-0-207. tape 품질과 소유자 hosted 순위는 일치하지 않았다(F-T2). 로컬 `env.run()`은 같은 시드에서 결정론적이었다(F-T4).
- **결정**: RESET의 방향 전환(tape router) 근거가 됐다.
- **근거**: `evidence/FACTS.md` F-T1~F-T6

#### yhay81-exact — 공개 9위 무수정 복제 (09-10)
- **검증**: clean-room 추출, starter 양좌석 6/6 승. silent-failure gate는 FAIL(unfilled sell 83,998~116,738)이었지만, 이는 `n=1000` sentinel을 손실로 센 **gate 정의 오류**였다(F-T7). vs 47 tape 470판 **452-0-18**(0.9617, Wilson 하한 0.9403).
- **판정 → 결정**: Codex preflight HOLD → 사람이 예외로 제출 → **2188.4**(약 7.3시간 후). HYP-0008 HOSTED_SUPPORTED.
- **근거**: `coordination/reports/codex/20260911-0053-PUBLIC-REFERENCE-REPRO.md`, `evidence/FACTS.md` F-T7~F-T9

#### EXP-005 — X1 매도 레이어 교체 (HYP-0005)
- **가설**: 로컬 tape pool 점수 변화가 hosted 레이팅 변화를 예측하는지 보는 프로브. Δpool ≤ −0.10이면 hosted도 −300 이하일 것이다.
- **변경**: 7개 산출물의 SELL을 tape 줄 대신 매 턴 `projected_shed`로 교체(1요인).
- **검증**: 47 tape pool 282셀 + public 40 + h2h 20, 안전 gate 포함. 개정 2회 모두 결과를 보기 전에 했다.
- **결과**: Δpool −0.1915, c−b 54는 충족. **discard 최대 81/run, end_units 28 위반**.
- **판정 → 결정**: FAILURE → 제출하지 않음(따라서 hosted 예측은 검증하지 못함).
- **교훈 (F-T10)**: open-loop farm tape 위에서 매도 레이어만 바꿔도 셰드 점유와 현금 시점이 바뀌어 farm 계획이 어긋난다.
- **근거**: `experiments/cards/EXP-005-x1-probe.md`

#### EXP-006 — clone preemption (HYP-0006)
- **가설**: parent clone 상대 h2h 20판 W≥18, L=0이고, 비-clone 상대에서는 승패가 뒤집히지 않는다.
- **변경**: 상대 farm 서명 거리 ≤6 그리고 120≤step<680일 때 STRAWBERRY/MELON/MILK/WOOL을 최대 30개 먼저 판다(아이디어 출처는 boatlee "V14 Clone Preemption").
- **검증**: G1 h2h 20, G2 pool 282셀, G3 public 40, G4 안전, G5 runtime, G6 self.
- **결과**: G1 **20-0-0**(+660~+3,756), G2 b=0 c=0, G3 40-0-0, 승패 뒤집힘 0. 독립 검증에서 byte-identical 재현.
- **판정 → 결정**: SUCCESS → 제출 56165718 → 1915.6 → 매일 하락해 1638.3. hosted 50판 비교에서 EXP-006은 41/0/9, EXP-007은 21/9/20이었다. parent(yhay81 사본)가 은퇴하는 바람에 인과 효과는 판정 불가(HYP INCONCLUSIVE).
- **교훈**: 같은 시간대에 parent와 A/B를 하려면 후속 제출을 늦춰야 한다. EXP-007 제출로 A/B 판독이 사라졌다.
- **근거**: `experiments/cards/EXP-006-clone-preempt.md`, `coordination/reports/codex/20260912-1114-HOSTED-EPISODE-COMPARE.md`

#### EXP-007 — 두 번째 슬롯 thomas router v2 exact (HYP-0007)
- **가설**: 풀 점수 ≥0.80이고, EXP-006이 못 이긴 셀을 보완한다(비상관).
- **변경**: 두 번째 슬롯을 yhay81 사본에서 thomas router v2로 바꿈(코드 0줄 변경).
- **결과**: G1 0.9433, G2 4/6, G3 40-0. 독립 검증자 반대 의견 5건(실효 표본 3쌍, Jiro2 tape 집중, manifest HOLD 등).
- **판정 → 결정**: SUCCESS + 검증자 "제출 불가" 의견 → 사람이 제출 → 1819.8 → 1467.3. HYP INCONCLUSIVE(공통 상대 3명뿐).
- **근거**: `experiments/cards/EXP-007-thomas-router.md`

#### EXP-008 — opening liquidity (첫 턴 시장 일정 A→B, HYP-0030)
- **배경**: hosted 패배 108076177을 부검했다. step 1의 52코인 차이 → step 23 현금 0 → step 25 HIRE 3건 실패 → 회복 불가로 이어졌다(Codex 부검. 주원인 해석은 `[INFERENCE]`로 표시됨).
- **변경**: step 1 시장 일정 A=[BUY 13, SELL 13, BUY 13] → B=[BUY 13, BUY 30, SELL 30] (나눌 수 없는 1요인).
- **검증**: target 2 + control 2 + public 40 + pool 282 = 326셀. G1~G5. G4는 결과를 보기 전에 "절대 0"에서 "셀별 non-regression"으로 재정의했다.
- **결과**: G1 target 0/0/2(초기 지표는 회복). G2 PASS. G3 pool c=2 FAIL. G4 회귀 72건 FAIL. G5 parity 38셀 FAIL.
- **판정 → 결정**: **FAILURE** → exact B 폐기. seed 추가나 요인 쪼개기로 재해석하는 것을 금지했다.
- **근거**: `experiments/cards/EXP-008-opening-liquidity.md`, `coordination/reports/codex/20260914-2025-EXP008-RESULT.md`, proj 09·10

### Phase 3 · 정합성·귀인

#### ANL-P1b — 실제 tar release preflight (09-16)
- parent EXP-006 tar, 13판(self 3, starter 6, hosted 패배 재현 2, control 2).
- 결과: Identity·Runtime·Isolation·License PASS, Schema FAIL, **zero gate FAIL 16/16**(noop 3,488, shed_discarded 482, buy_failed 74, hire_failed 18).
- 판정: LOCAL FAILURE(Codex), VERIFIED_LOCAL_FAILURE(Antigravity). 이 결과가 EXP-011·013의 입력이 됐다.
- **근거**: `coordination/reports/codex/20260916-1919-P1B-ACTUAL-TAR-PREFLIGHT.md`

#### EXP-011 — shed-discard 귀인 (HYP-0031, 측정만)
- **결과**: 1,603 checks PASS. 482 units 중 C*(ROOM_PARTIAL|REMOTE|NO_DEPOSIT) 클래스가 S1 64/64, S2 416/418, sole-top 16/16.
- **판정**: 카드 PASS / REPAIR_AUTHORIZED. Claude 판정은 "측정 PASS 확정 / 카드 서술 정정 / EXP-012 사전등록 불가", Antigravity 독립 검토는 인과 해석을 기각했다. 코인 환산 상한은 ≈19,200(17.6%)에서 ≈13,938(12.8%)로 정정됐다. EXP-012는 사전등록 불가로 닫았다.
- **근거**: `experiments/cards/EXP-011-shed-discard-attribution.md`, `coordination/reports/claude/20260918-EXP011-*`

#### EXP-013 — 상태 조건부 HIRE 회복 (HYP-0032, 미실행)
- 사전등록을 r1~r3까지 했다(Codex contract review NEEDS_REVISION 6건 반영). 09-18 사람이 구현·실행을 불허했다. PLANNED.
- **근거**: `experiments/cards/EXP-013-state-conditioned-hire-recovery.md`

#### ANL-P1c — hosted 77판 패배 감사 (09-18)
- Gemini 주장(HIRE 실패 100%, NOOP 77/77 등)을 Codex가 감사했다. 실제 HIRE 실패는 패배 52판 중 3판이었고, 32/32 assertion으로 주장 다수를 반박했다. 추천 가설 0, "현재 근거 부족".
- **근거**: `coordination/reports/codex/20260918-P1C-BOUNDED-EVIDENCE.md`

### Phase 4 · F0 fast lane

#### ANL-F0 — donor tape → 공개 exact → lineage (09-18 ~ 09-20)
- donor tape 재생 full_match **0/52**(첫 분기 ≤32턴이 17팀). → 사람 "§3 A 채택"(공개 노트북 exact).
- 공개 exact 3개 gate PASS. round-robin lynnsakurai 0.9667 / alperen 0.70 / tetsutani 0.33 / yhay81 0.00. → **P2 제출 2421.6(동메달권)**, P1 alperen 1471.3.
- lineage: 추출 가능 37개 중 SAME_FAMILY 34, DIFFERENT 3. DIFFERENT 3개는 6쌍 중 5쌍 0/20으로 둘째 슬롯 후보 부적격.
- 공개 "2749/2820" 변형은 vs P2 0/20. 이 과정에서 **엔진 진입점 = 마지막 callable**인데 instrument.py가 다른 함수를 테스트하던 결함을 찾아 고쳤다.
- P2 hosted 112판 패배 분석: 사전 임계(A≥20%, A−B≥20pp)를 넘는 후보 없음.
- **근거**: `coordination/reports/antigravity/20260919-1128-F0-STAGE-BC.md`, `coordination/reports/codex/20260919-1221-F0-PUBLIC-EXACT.md`, `coordination/reports/claude/20260920-0011-F0-DIFFERENT-LINEAGE.md`, `20260920-0114-P2-LOSS-ANALYSIS.md`, `20260920-0950-F0-LIVE-CLAIM-VARIANTS.md`

#### EXP-014 / EXP-015 / EXP-014R — mirror 조정 (HYP-0033/0034)
- **가설**: exact clone 상대(1–143턴 농장 동일)에게 `_ADV_LOOK` 3→4(014) 또는 SELL 묶음 가격 내림차순(015)을 쓰면 mirror 승률이 오른다.
- **검증**: mirror seed 3000–3014, panel 5봇 3000–3009, 양좌석 390판. 유효성 조건: baseline B0 무승부 ≥25/30.
- **결과**: B0 무승부 24/30으로 **INVALID**(014는 M14 25/0/5라 수치로는 success 기준을 넘었을 것). 015는 M15 1/0/29로 폐기.
- **014R**(새 seed 4000–): M14R **22.0/30**(기준 22.5에 0.5 부족), M−B0 7.0, 회귀 0/100 → INCONCLUSIVE → 로컬 seed 추가는 금지하고 hosted 실험으로 제출. hosted 점수는 기록되지 않았다.
- **근거**: `experiments/cards/EXP-014*`, `EXP-015*`, `coordination/reports/antigravity/20260920-2130-EXP014-015-RUN.md`, `20260920-2215-EXP014R-RUN.md`

#### ANL-2945 / C1 — 2945-line 후보 (09-21)
- C1 nathanjacob pipe16과 C5 ozer v51 모두 vs P2 20/0/0. C1 vs C5 16/0/4. → C1 제출(2206.6).
- C1 hosted 148판 상대 지도: W91/L50/D7. "UNKNOWN(53 with C1)" 상대에게 4-30.
- **근거**: `coordination/reports/antigravity/20260921-1442-2945-LINE-*.md`, `20260922-1716-C1-HOSTED-MAP.md`

#### EXP-016 — C1 + V53 sale advance (HYP-0035)
- **배경**: C1과 V53은 물리 행동이 같고 판매 레이어만 다르다. C1에는 V53의 EXP293 sale-advance가 없다(C1-HB 분석).
- **변경**: V53 `main.py:3532-3629` `_adv_apply`+`_adv_frontload` 이식(LOOK 3, FROM 144, TO 718).
- **검증**: seed 2100–2139 양좌석. 블록 A_mirror, P_c4, P_c5, P_c2, P_p2. 유효성 parent vs parent ≥14/20 무승부.
- **결과**: 유효성 20/20. mirror 31/1/8(seed 기준, net +23). panel 손실 55 vs 63. 단 **P_c2 +6 > 2** 위반.
- **판정 → 결정**: INCONCLUSIVE → 사람 결정으로 hosted 실험 제출 → **2425.7(≈808위, 대회 최고)** → 2265.8. 200판 77-123.
- **근거**: `experiments/cards/EXP-016-c1-sale-advance.md`, `coordination/reports/antigravity/20260922-1701-EXP016-RUN.md`

#### EXP-017 — OMW + sale advance (HYP-0036)
- **배경**: step-53 cadence 상대 = OneMoreWheat(OMW). OMW는 vs C1 40/0/0, vs EXP-016 10/0/30.
- **변경**: OMW(main `10f58185…`, CRLF 원본)에 sale-advance 레이어(1요인).
- **결과**: A_parent 59/0/21(net +38), **vs EXP-016 78/0/2**, panel 손실 147 vs 155, 예외 0.
- **판정 → 결정**: SUCCESS → 제출 → 1985.2 → 2100.2 → 2010.8. **EXP-016보다 −165.6**. hosted 145판 77-68.
- **교훈 (ledger)**: 로컬 sibling 맞대결은 hosted 순위를 예측하지 못했다.
- **근거**: `experiments/cards/EXP-017-omw-sale-advance.md`, `exp017_results.txt`, `coordination/reports/antigravity/20260924-1610-EXP016-017-HOSTED-MAP.md`

#### ANL-STEP91 / DP 0924 (09-24)
- Antigravity는 prefix 91 상대를 ahmedberatozer V56으로 식별했다(상위 3개 파일이 FULL 26으로 동률). 이후 Claude의 LB teamId 판독에선 우리가 V56에 17-9로 이겼고, 우리를 이긴 쪽은 tetsutani DP 0924(0-7)였다. DP hosted 지도: 884판 666-199-19. 상대 LB가 오를수록 승률이 떨어졌다(<2200 .92 → ≥2800 0).
- 사람 "B안"으로 DP 0924 exact 제출 → 2191.6. Claude가 예상한 "균형 2450~2550"은 team LB를 상대 레이팅으로 잘못 쓴 오류였다.
- **근거**: `coordination/reports/antigravity/20260924-1845-STEP91-ID.md`, `20260924-2155-DP-HOSTED-MAP.md`

### Phase 5 · 동결 지표 루프 → 상수 탐색

#### EXP-018 — DP 0924 `_V92_P_EVERY` 3→2
- **검증**: Q2 패배 8건, Q4 panel 47, 필수 DP 80판(seed 2400–2439, 하한 0.50). 카드 freeze 09-24 15:59Z.
- **결과**: 패배 8건 중 3건 뒤집힘. panel 23/0/24 → 28/0/19(Δ 0.106 > 2SE 0.091). **DP80 0.4875 < 0.50**.
- **판정**: VERIFIED_NOT_ELIGIBLE_DP_FLOOR → 제출하지 않음. 후속 EXP-019/020은 탐색 루프에 흡수됐다.
- **근거**: `experiments/cards/EXP-018-dp0924-single-factor.md`, `coordination/reports/codex/20260925-1340-DP-LOSS-CAUSE.md`

#### ANL-NEWMETA + D3 gate v2 (09-25)
- 127ed3e6 exact: DP80 66/0/14(0.825), E-5 0.80, panel47 42/0/5. runtime max step 0.7506s로 기존 0.25s gate에서 **NOT_ELIGIBLE**.
- 사람이 19:48에 **D3 v2**를 승인했다(엔진 한도 기반: single <0.8s, step0 <0.8s, 6-worker <1.0s, 게임당 <30s, 오류 0). ledger는 이를 "post-hoc rule change"로 기록했고, 기존 NOT_ELIGIBLE 줄은 지우지 않고 PASS 줄을 추가했다.
- 제출 → 2165.6 → **2314.7** → 2251.0.
- **근거**: proj 13, `coordination/reports/codex/20260925-1846-NEWMETA-EXACT.md`

#### ANL-CALIB — 동결 목표 지표 calibration (09-25)
- **목적**: SEARCH-LOOP v2.3(동결 지표, successive halving 150→50→15→3, holdout CP1 9000–9199 / CP2 9200–9399)에 쓸 지표 고르기.
- **결과**: 후보 a/b/c/d 모두 판정 False, 실행 이상 5, tape 방향 일치 0.25(N=4). Claude 검토는 "조건부 타당"이었지만 변별력은 거의 0이었다(유효 쌍 1, 무작위 자의 통과율 .22 대 후보 .55).
- **판정 → 결정**: **BLOCKED** → 루프 정지(23:02) → 수작업 mirror screen(EXP-021/023)으로 전환.
- **근거**: `coordination/reports/codex/20260925-2302-METRIC-CALIBRATION.md`, proj 15

#### EXP-021 / EXP-022 — mirror edge
- 021: parent e496a4fe vs 127ed3e6, arm별 1요인(horizon 32/40, liquidation 등), seed 5000–5049 양좌석. 결과 P/H1a/H1b/H3 = 0.500으로 **행동이 parent와 같았다**. H4 0.33. → STOP → FAIL.
- 022: harness `KeyError('step')` → 수정 → smoke 현금 차이 −28(기대 −25±2). BUY_PRODUCT 가격이 단위마다 다시 매겨졌다 → STOP.
- **근거**: proj 17·18, `coordination/reports/codex/20260926-0108-EXP021-MIRROR-EDGE.md`, `20260926-0133-EXP022-H2P.md`

#### ANL-P4 / P4b — tape fidelity
- P4: 1,694판에서 정보가 있는 쌍 n=2 → WEAK. P4b: 121 에피소드 × 6 agent × 2 mode에서 정보 쌍 486, D 0.74, **ρ 0.90**(CI 0.30–1.00). closed-loop에서 v171 +0.008, v111 −0.100. → SUCCESS.
- **근거**: `coordination/reports/antigravity/20260926-1147-P4B.md`

#### EXP-023 — 상수 ±1 mirror screen → v171
- **설계**: 1,870 key(상수 하나 ±1). Stage 2는 후보당 60판 vs 127ed3e6. Stage 3은 4,000판(vs 127, vs DP, vs 공개 14). 기준 A~E 사전등록(sha `644e9ba5…`).
- **결과**: v171(`_DP_H` 8→9) A 0.8075(Wilson99 하한 0.7519), DP Δ +0.025, D +0.031, max 0.43s → **유일하게 전 기준 PASS**. v173·v074는 runtime(E)에서, v111은 C·D에서 FAIL.
- **판정 → 결정**: SUCCESS → 사람 "v171이 더 뛰어나다고 가정하고 진행" → 제출 → **2337.5** → 2211.7.
- **근거**: proj 19, `experiments/exp023_mirror_screen/`, `releases/mirror-screen-v171/`

#### EXP-024 — round 2 (v171 parent) → v074
- **인프라 사고**: INFRA-BUG-001. wrapper가 v171에 다시 적용되면서 자기참조가 생겨 186변형이 0 action으로 끝났는데, status만 검사해서 놓쳤다. → `action_count`·`agent_errors` 검사를 추가하고 재실행했다.
- **결과**: Stage 3 5,604판, v074(`V9_RACE_DEFAULT` 44→45) A 0.725, A′ +0.138, D +0.003. v111·v169는 FAIL.
- **판정 → 결정**: SUCCESS → 제출 → 2215.9(같은 시각 v171 2211.7) → 2068.4.
- **근거**: proj 20·21, `experiments/exp024_round2/INFRA-BUG-001.md`

#### EXP-025 / 025b — v171 hosted 검증
- hosted 107판 107/107 재현. v171은 127ed3e6 *변형*(private) 상대에서 3/3/16(0.20)이었다. ±1 변형 186개는 그 상대들에게 0/171 → **±1 회복 가설 폐기**.
- 025b: "verification failures 0" 보고에서 Claude가 **seat 오류**를 찾았다(1,397개 중 1,028 invalid). refilter 후 유효 214개.
- 이 카드부터 토큰 절약 운영 규칙을 적용했다(09-26).
- **근거**: proj 22·23, `coordination/reports/antigravity/20260926-2045-EXP025-V171-HOSTED.md`, `20260927-0100-EXP025B.md`

#### EXP-026 / EXP-027 — v074 near-clone
- 026: 142변형 × 40 tape(open-loop). w067 +0.394 등이 통과했지만 Codex REVIEW-0927이 **open-loop 낙관 편향**을 지적했다. w067은 v111과 같은 변경이었다.
- 027(closed-loop guard)은 실행하지 않고 대체했다.
- **근거**: proj 24, `coordination/reports/codex/20260927-1036-REVIEW-0927.md`

#### EXP-028 ~ EXP-032 — 55be5d5f 계열 탐색
- 028: 55be5d5f exact vs v074, pooled Δ −0.084 → HOLD.
- 029: 55be mirror ±1 158변형 screen → **d157**(`_S1002_PASSES` 34→35) 등 6개 진출.
- 030: bypass → FAIL. 031: hosted census 350판(v074는 127 변형 상대 8/1/43).
- 032: Kaggle kernel 5개에서 d157 transition [0.192, 0.141]. FAIL 사유는 4병렬 contention 때문인 runtime 하나뿐이었다.
- **근거**: `experiments/exp028_dpnew/`, `exp029_dpnew_mirror/`, `exp030_dpnew_bypass/`, `exp032_specialist/`, proj 28

#### EXP-033 / EXP-034 — Kaggle kernel tape·runtime
- 033: 1차 ERROR(dataset 생성 실패) → 재실행 2,100행. **hosted 경기를 tape로 정확히 재현**했다(v074 163/163, d157 136/136).
- 034: d157 순차 max 0.247s.
- **근거**: `experiments/exp033_tapes/`, `exp034_runtime/`

#### EXP-035 — d157 제출 판정
- **사전등록**(20:03, sha `b054c5bf…`): EXP-032 성능(transition 하한 > 0, legacy ≥ −0.10, hosted ≥ −0.10) + runtime A/B + tape.
- **결과**: tape 127 변형 +0.522(lo95 +0.42), 전체 +0.29. 127 변형 상대 0.228 → 0.750, 127 exact 상대 0.914 → 0.852.
- **판정 → 결정**: PASS. 그 전에 Codex REVIEW-0927C는 NO_SUBMISSION(d157 EXP-032 FAIL)이었으나, 20:07 사람 "메달권 밖이면 위험 감수"로 뒤집혔다. → 12:00:04Z 제출 → 2299.7(12h) / **2400.9(21h)**.
- **기록 순서 문제**: RESULT 문서(21:25 KST)가 제출(21:00:04 KST)보다 늦다. D3 json은 09-27에 FAIL(6-worker 칸 null)이었다가 09-30에 PASS로 재평가됐다(§10).
- **근거**: `experiments/exp035_d157/PREREG.md`, `RESULT.md`, `releases/exp035-d157/`

#### ANL · 09-27 기타
- TOP1 노트북은 제출된 그대로면 no-op이었다(마지막 callable이 패치 함수). 고쳐도 vs v074 0/20.
- HYPGEN/H1/INSIGHT-SWEEP/LATE/ALTMECH는 모두 FAIL 또는 NO_SUPPORTED_CANDIDATE였다.
- **근거**: proj 26, `coordination/reports/codex/20260927-*.md`

### Phase 6 · d157 개선과 슬롯 분산

#### EXP-036 / EXP-038 — d157 ±1, 55be family
- 036: 158변형, 총 16,380판. best e076 +0.01 → FAIL. "**55be 계열 상수 ±1은 tape 상대에게 거의 무효과**." 상수 미세조정 라인을 종료했다.
- 038: family arena 5,770행에서 d157(FS 0.7266)이 최강 → FAIL(대체 후보 없음).
- **근거**: `experiments/exp036_d157plus/`, `exp038_family/`, proj 29

#### EXP-039 → c26 — `_CA_MARGIN` grid
- 4,266행. c26(−26) tape +0.0237, tapeU −0.0037 → **frozen FAIL**.
- 사람 방침(09-28 14:05): "슬롯2는 공격적 후보 허용". 이 방침 아래 c26을 제출했다(08:45 UTC) → 717 → 1939.7. 제출 결정 자체의 기록은 원본에 없다.
- EXP-042(2400+ tape 742개): c26−d157 **+0.033**(lo95 +0.017). 그러나 hosted에선 c26 1,887~1,940, d157 ~2,200이었다. 공통 상대는 331판 중 0. doc 45는 "c26 ≥ d157" 판단을 team-best LB 편향으로 철회했다.
- **근거**: `experiments/exp039_camargin/`, `releases/exp039-c26/`, proj 37·43·45

#### EXP-043 / 043b — oracle
- 30봇 × d157 패배 tape 130 = 3,900행 → 16봇 자격 → 043b(16봇 × 승리 tape 49)에서 **0 qualified**.
- 판정 NO CLUE → 새 탐색 중단, d157+c26 유지.
- **근거**: proj 32, `analysis/exp043_oracle/`

#### EXP-044 ~ EXP-048 — 판매·상대모형 라인
- 044 margin 분해: net cash와 margin 상관은 WOOL .48, MILK .49, WHEAT .01. Claude는 "d157은 상대 관측이 없다"는 doc 33 서술을 스스로 정정했다(이미 `_OR2`·`_V9_RACE`로 관측함).
- 046: 55be가 상위팀 판매를 recall 0.90으로 예측. 047 shadow hook precision 0.114.
- 048A: 12변형 × 595 tape, hook +0.0109, K3 +0.0042. 048B: 3,164판 확인에서 hook +.004, K3 −.192 → **FAIL** → 045/047 라인 종료.
- **근거**: proj 33·34·36·37, `experiments/exp045_sale/`, `exp047_oppmodel/`, `exp048_stageA/`, `exp048_stageB/`

#### EXP-053 ~ EXP-057 — 생산 재설계 라인
- 053 상위팀 tomato 분석(Fritz·Hikaru·Shawn404·juliencst). 054 `_CXTB_MIN_REVENUE` 7000/6000: −0.004/−0.084 FAIL. 055 Fritz-lite: −0.372 FAIL → tomato 라인 종료.
- 056 공개 Step1009 family 7봇: 전부 음수 FAIL. 057 geese: −0.061 등 FAIL.
- **근거**: proj 40·41·44·46

#### EXP-058S / EXP-059 — route 재배정
- 058S: 1,345판, best S→107 +0.024, group lo95 −0.0125 → FAIL. 사후 관찰한 "non-yarn→107 +0.039"는 관찰로만 남겼다.
- 059: 이를 새 번호로 사전등록하자는 안이었지만 "해도 되지만 최선은 아니다"로 보류했다.
- **근거**: proj 49·50

#### ANL-SLOT2 — 슬롯 분산 (09-29)
- 배경: 두 활성 봇(d157·c26)이 같은 계열이라 약점이 잡히면 함께 내려간다는 판단(사람). RL은 제외했다(doc 52). Fritz식 재설계 12변형은 전부 −0.15~−0.22로 FAIL.
- **slot2-R**: step 144에 농장이 같으면 mirror 판으로 보고 route 107, 아니면 c26. rev1은 detection 82% 대 label 87/269 불일치로 무효, rev2·rev3에서 조건을 추가했다.
- holdout: HF 78판 X 0.571 / d157 0.462 / c26 0.545, HT 421판 0.477 / 0.456 / 0.493, D3 0.513s → **holdout PASS** → X(Rc26_107)와 d157r 제출.
- **근거**: proj 52·53·55, `experiments/slot2_x/`, `releases/slot2r-Rc26_107/`

### Phase 7 · 마지막 날

#### ANL-READOUT0930 — X vs d157r hosted
- 195판 자기재현 195/195. A(X 실제 − d157 가상) −0.079(n76), B +0.004(n119), combined **−0.028 (−0.074, +0.018)**, mirror B−A +0.333.
- 판정: cannot judge. 여기서 tape replay가 mirror 판에서 **+0.17 낙관적**이라는 근거가 나왔다.
- **근거**: proj 56, `analysis/readout0930/`

#### EXP-060 — MBR (mirror route 그룹 배정)
- 사전등록 + A1·A2 addendum. M0 mirror 504판(Y/D/S 그룹) → M1 5,040 → M2 1,791(채택 Y→DN29 +0.200, D→110 +0.179, S→110 +0.301) → M3-A 870.
- 결과: HF Cd/Cc 0.603 > X 0.571이었지만 closed-loop **Cc vs 55be 0.550 < X 0.562** → FAIL, 제출 없음.
- Sol 1·2차 검토: winner's curse, 포트폴리오 목적함수.
- **근거**: `experiments/exp060_mbr/`, `coordination/reports/claude/20260930-0815-EXP060-M3-READOUT-VERDICT.md`

#### EXP-061 — donor route
- rank 1–100 팀의 donor route 29개 중 27개 fail. DN29(Y 그룹) 0.725 vs d157 0.500. 061b(rank 101–300)는 58/85에서 사람이 중단(평균 −0.30).
- **근거**: `experiments/exp061_donor/`

#### EXP-062 — glut lead (최종 경로)
- **진단**: hosted 542판에서 LB 1750–2250 구간 293판 중 111패, 그중 71패(64%)가 private 55be 변형 상대였다(113판 0.358). public 55be 원본 상대는 0.776.
- **가설**: 과잉(glut) 구간에서 tape가 계획한 MILK/WOOL/STRAWBERRY 판매를 K step 앞당기면(steps 192–695, 가격 ≤ base) 55be 변형에게 덜 진다.
- **사전등록**: PREREG A1–A12(09-30 08:45). 9상대 pool × 20 seed × 2 seat.
- **결과**: S1 L3p +0.111, L4p +0.107. S2 L4p +0.060 [−0.002, +0.112] (strict 조건 하한 >0을 0.002 미달). S1+S2 L4p +0.079 [+0.030, +0.126]. S3(새 공개 10봇) L4p +0.002. A8 S5 L5p vs L4p +0.037 [+0.004, +0.068] → L5p 제출. 그런데 A11 S7d/S8(Kaggle 2,160판)에서 **L5p−L4p −0.058 [−0.104, −0.011]**, d157−L4p −0.064. S9(1,880판)에서는 A11 통과 후보가 없었다(X454 +0.025 < +0.03).
- **판정 → 결정**: L4p는 strict 미달이었지만 A6(09-27 사람 "위험 감수 > 사전 고정 FAIL 불변")으로 11:32 KST 제출. L5p는 20:17 KST 제출 후 역전됐다. 22:50 사람 조합 A = {강한 L, d157 사본} → d157c(22:56) + L4pc(23:24 KST). Sol 7차는 L4p 사본 즉시 제출에 동의하고 X454 사후 완화에 반대했다.
- **실전(09-30 22:42 수집)**: 1600–1800 구간 L4p 0.73 / d157r 0.70, 1800–2000 0.50 / 0.45, 2000–2200 0.29 / 0.33. "1800 이상 상대에게 5할 미만 — 동메달까지 남은 과제."
- **근거**: proj 59·60, `experiments/exp062/PREREG.md`, `COORD.md`, `releases/exp062-*/`

---
## 7. CV ↔ LB 대조: 로컬 판정이 hosted를 맞췄나

Kaggle 상위권 기록에서 가장 많이 보는 표다. 제출한 후보마다 로컬 근거와 hosted 결과를 나란히 놓았다. hosted 값은 관측 시각이 서로 다르고, 리그 전체가 하락하는 중이었다는 점을 감안해서 읽어야 한다. [사실]

| 제출 | 로컬 근거 (비교 대상) | 로컬 방향 | hosted 결과 (비교 대상) | 일치? |
|---|---|---|---|---|
| v0 | vs starter 40/0/0 | ↑↑ | 314.8 (리그 하위 12%) | ✗ (지표 자체가 무관, K5) |
| v1 | v0 대비 단계별 우위 | ↑ | 343.9 vs v0 337~347 | ✗ (차이 없음) |
| yhay81-exact | vs 47 tape 0.9617 | ↑↑ | 2188.4 (v1 343.9) | ✓ |
| EXP-006 | h2h vs parent 20-0-0 | ↑ | hosted 50판 41/0/9 vs EXP-007 21/9/20; parent 은퇴로 직접 비교 불가 | ? |
| EXP-007 | pool 0.9433 (EXP-006 0.9787보다 낮음) | ↓ | 1819.8 < EXP-006 1915.6 | ✓ (방향) |
| P2 | round-robin 0.9667 (1위) | ↑↑ | 2421.6 (당시 최고) | ✓ |
| P1 alperen | round-robin 0.70 (P2보다 낮음) | ↓ | 1471.3 | ✓ (방향) |
| C1 | vs P2 20/0/0 | ↑ | 2206.6 (P2 2410.4) | ✗ |
| EXP-016 | INCONCLUSIVE (C1 대비 mirror +23, P_c2 악화) | ? | **2425.7** (C1 2206.6) | ✓ (결과적으로) |
| EXP-017 | vs EXP-016 **78/0/2** | ↑↑ | **−165.6** vs EXP-016 | ✗ |
| DP 0924 | (exact, 로컬 근거 없음) / Claude 예상 2450~2550 | — | 2191.6 | ✗ (예상 오류) |
| 127ed3e6 | vs DP 820-2-178 (0.821) | ↑↑ | 2314.7 > DP 2191.6 | ✓ |
| v171 | vs 127 0.8075, DP Δ +0.025 | ↑ | 2337.5 (127 2314.7) → 2211.7 | △ (첫 관측만 ↑) |
| v074 | Stage 3 vs 127ed3e6 A 0.725, A′ +0.138; Stage 2 vs v171 0.700 | ↑ | 2215.9 vs v171 2211.7 (같은 시각) → 2068.4 | △ (차이 없음) |
| d157 | tape vs v074 +0.29 (lo95 +0.23) | ↑↑ | 2400.9 vs v074 2215.9 | ✓ |
| c26 | tape vs d157 +0.033 (lo95 +0.017), frozen gate FAIL | ↑ / ✗ | 1,887~1,940 vs d157 ~2,200 | ✗ |
| X Rc26_107 | holdout HF 0.571 vs d157 0.462 | ↑ | readout combined −0.028; 1658.1 vs d157r 1888.4 | ✗ |
| L4p | S1+S2 vs d157 +0.079 [+0.030, +0.126] | ↑ | 1800.5 vs d157r 1844.5 (같은 시각) | ✗ (재수렴 중이라 판단 유보) |
| L5p | vs L4p +0.037 → 이후 −0.058 | ↑ → ↓ | 1713.7 < L4p 1795.9 | ✓ (최종 판정과 일치) |

**관찰된 패턴 [해석]**
- **계보 사이 비교(다른 공개 봇끼리)는 대체로 맞았다**: yhay81, P2, 127ed3e6, d157. 큰 차이(round-robin 0.9 대 0.3, vs DP 0.82)는 hosted에서도 보였다.
- **같은 계보 안의 미세 변경(sibling)은 거의 맞지 않았다**: EXP-017, v074, c26, X, L4p. 로컬 우위는 대부분 +0.03~+0.14 수준이었는데, hosted에서는 반대이거나 구분되지 않았다.
- 원인으로 원본이 든 후보: ① open-loop tape는 상대가 반응하지 않는다(mirror에서 +0.17 낙관, EXP-026 낙관 편향 지적). ② 로컬 상대 풀이 hosted 상대 분포와 다르다(calibration "pool 비대표, mirror 비중 ≈52%"). ③ hosted 점수는 수렴 시간, 상대 분포 변화, 재제출 600 시작의 영향을 받는다. ④ 같은 상대를 만난 경기가 거의 없다(c26 vs d157 공통 상대 0/331).
- calibration(09-25)은 이 문제를 미리 측정했다. 변별력 ≈0, tape 방향 일치 0.25(N=4)라는 결과가 나왔고 그래서 루프를 정지했다. 이후 대체 지표(Wilson·tape·holdout)도 sibling 수준 차이를 hosted와 맞추지 못했다.

---

## 8. What worked / What didn't

### 효과가 있었던 것 [사실 + 근거]
| 무엇 | 근거 |
|---|---|
| 규칙기반 → **tape 재생 계열로 전환** | hosted 343.9 → 2188.4 (09-10) |
| **공개 exact를 돌려가며 제출**해 그 시점 최강 계보 따라가기 | P2 2421.6 (동메달권), 127ed3e6 2314.7 |
| 판매 레이어 이식 (V53 sale-advance → C1) | EXP-016 2425.7, 대회 최고 |
| 강한 계보 + 상수 1개 (d157 = 55be + `_S1002_PASSES` 35) | 2400.9 (21h) |
| hosted 경기 tape 재생으로 상대 재현 | 163/163, 136/136, 107/107, 195/195 exact |
| 엔진 소스로 직접 사실 확인 | 흡수량 3일/8개 정정, 진입점 = 마지막 callable, BUY_PRODUCT 가격이 단위마다 재평가 |
| 사전등록 + SHA 원장 + 독립 검토 | stale artifact(EXP-001), INFRA-BUG-001, seat 오류(025b), gate 정의 오류(F-T7), K10 오등재 철회 |
| 결과를 보기 전에 판정 규칙을 고정하고 사후 완화를 거부 | EXP-008 G4 재정의를 결과 전에 함, X454 사후 완화 거부 (Sol 7차) |

### 효과가 없었던 것 [사실 + 근거]
| 무엇 | 근거 |
|---|---|
| 직접 짠 executor와 작물·흡수량 조정 | 공개 4봇 0/0/400 (EXP-002·003) |
| open-loop tape 위에서 매도 레이어만 교체 | EXP-005 FAILURE, F-T10 |
| 첫 턴 시장 일정 같은 국소 수리 | EXP-008 FAILURE |
| 상수 ±1 대량 탐색 (2라운드 이후) | EXP-025 0/171, EXP-036 best +0.01 |
| 상대 예측·판매 hook | EXP-045/047/048 FAIL |
| 생산 재설계 (tomato·Fritz·geese) | EXP-054·055·057, slot2-X 전부 음수 |
| 공개 family 추가 탐색 | EXP-056 전부 음수, DIFFERENT lineage 0/20 |
| donor tape·route 일괄 이식 | F0 full_match 0/52, EXP-061 27/29 fail |
| 자동 탐색 루프용 동결 지표 | calibration BLOCKED (변별력 ≈0) |
| hosted 패배 원인 귀인 (P1c, P2 loss) | 추천 가설 0, 임계 넘는 후보 없음 |

### 비용이 컸던 것 [해석]
- **09-16~18 정합성 작업**(P1b preflight → EXP-011 귀인 → EXP-013 사전등록 3회): 측정 품질은 높았지만 제출로 이어지지 않았고, 그사이 활성 슬롯은 1862 → 1638로 떨어졌다. 09-18 fast lane 결정 이후 하루 만에 2421.6으로 회복했다.
- **마감 전 이틀간 슬롯 6회 교체**: 활성 슬롯이 매번 600에서 다시 시작했다. 같은 바이트의 d157이 09-28엔 2400.9였고, 09-30 재제출본(d157c)은 10-01 05:47 KST에 1622.2였다(리그 전체 하락도 함께 반영된 값이다).

---

## 9. 교훈과 다음 대회 체크리스트

### 9.1 이 대회에서 얻은 교훈
원본에 적힌 교훈은 출처를 달았고, 이 로그를 쓰며 덧붙인 것은 [해석]으로 표시했다.

1. **평가 지표를 먼저 검증한다.** 로컬 지표가 hosted 방향을 맞히는지, 이미 제출한 2~3개 쌍으로 먼저 확인하고 나서 탐색을 시작한다. (09-25 calibration이 이를 시도해 BLOCKED를 냈다. 문제는 그 시점이 대회 4주차였다는 것이다. [해석])
2. **같은 계보 안의 미세 변경은 로컬로 구분할 수 없다고 보고 시작한다.** 이번 대회에서 sibling 비교가 hosted와 맞은 사례는, 첫 관측만 맞은 v171(△)을 빼면 L5p 하나뿐이었다(§7). [해석]
3. **open-loop tape 점수는 상한으로 읽는다.** mirror 판에서 +0.17 낙관, EXP-026 낙관 편향 (READOUT0930, REVIEW-0927).
4. **슬롯 교체는 비용이다.** 최종 BT는 활성 제출 간 경기만 센다(F-T12). 재제출은 600에서 다시 시작한다. 마지막 48시간에는 바꿀 이유가 hosted 증거로 뒷받침될 때만 교체한다. [해석]
5. **같은 시간대 A/B를 보존한다.** parent를 은퇴시키는 순서로 제출하면 인과 판정을 할 수 없다 (EXP-006 교훈).
6. **"카운터 0 ≠ 손실 0".** 자체 클램프나 guard의 PASS 전환은 계측 밖에 있다 (AGENTS R3, SLOT_CONTENTION).
7. **gate의 정의부터 검증한다.** `sell_unfilled` sentinel(F-T7), status만 보는 검사(INFRA-BUG-001), seat 필터(025b), 진입점 함수(F0 live-claim)가 모두 "통과"를 거짓으로 만들었다.
8. **결과 파일에 코드 SHA를 박는다.** stale artifact 사건(EXP-001) 이후의 규칙.
9. **측정 불가는 KILL이 아니다.** K10 철회 (MDE ±1,674에서 −98).
10. **공개 노트북 점수는 저자의 실제 점수가 아니다** (F-T18). 공개 코드는 직접 재현해서 판단한다.

### 9.2 다음 Kaggle 대회 운영 체크리스트 [해석, 위 교훈에서 도출]
- [ ] Day 1~3: 엔진·규칙 사실 정리(FACTS), 제출 한도·슬롯·최종 평가 방식을 원문으로 확인(F-T12 같은 staff 답변 포함).
- [ ] Day 1~3: 공개 상위 노트북 exact 재현 → 즉시 1개 제출(기준선 확보). 이번 대회에서는 이 단계가 09-10(제출 시작 4일 차)에야 이뤄졌다.
- [ ] 첫 주 안: 이미 제출한 2개 이상의 쌍으로 **로컬 지표 ↔ hosted 방향 일치율**을 측정한다. 맞지 않으면 sibling 미세 탐색은 하지 않는다.
- [ ] 실험 카드 필수 칸: 가설 / 1요인 변경 / parent SHA / 상대 풀·seed·seat·n / 성공·실패·무효 기준(결과 전 고정) / holdout / 결과 / 판정 / 다음 행동 / 제출 ID.
- [ ] 모든 결과 JSON에 parent·agent·engine SHA와 `action_count`·`agent_errors`를 기록한다.
- [ ] 제출 원장 1개(제출 시각 UTC, ID, artifact SHA, 은퇴시킨 것, 관측 점수 + 시각). 정정은 표 안에서 한다.
- [ ] 마지막 72시간: 슬롯 교체 상한을 정한다(예: 슬롯당 1회). 교체 조건 = hosted 증거.
- [ ] 이 로그 형식(§1 TL;DR, §3 원장, §5 대장, §7 CV↔LB)을 대회 시작일에 만들어 두고 매 실험 후 한 줄씩 추가한다.

---

## 10. 모순·미확정 사항 (원본끼리 다르거나 비어 있는 것)

| # | 항목 | 내용 | 원본 |
|---|---|---|---|
| 1 | EXP-014 쌍 submission ID | 표는 56398274/56398276(14:50), 정정 문단은 56398297/56398299(14:51). 앞의 쌍도 실제로 접수됐다면 총 제출은 28건이다. | `evidence/HOSTED_LEDGER.md` |
| 2 | 시간순 점수 차이 | v0 327.6/330.6/337.2/337.3/347.2, EXP-006 1915.6/1896.9/1862.6, d157 2299.7/2400.9/2345.7/2393, L4p 1784.0/1792/1796.9, L5p 1695/1701.8/1713.7. 관측 시각이 달라서 생긴 차이다. | ledger, registry, proj 29·30·60 |
| 3 | 판정 → 제출 불일치 | EXP-039 frozen FAIL → c26 제출, L4p strict 미달 → 제출, d157은 Codex NO_SUBMISSION → 제출, EXP-007은 검증자 "제출 불가" → 제출. 모두 사람 결정이거나 사람 방침 아래 제출이었다(c26은 "슬롯2 공격적 후보 허용" 방침만 기록됨). | proj 28·30·59, EXP-007 카드 |
| 4 | 재제출 KILL vs 실제 재제출 | KILLS 방법론 "같은 봇 재제출로 리롤" 금지 ↔ d157r·d157c·L4pc·yhay81 재제출(포트폴리오·슬롯 순서 목적). | `evidence/KILLS.md` |
| 5 | 기록 순서 | EXP-035 RESULT(21:25 KST)가 제출(21:00:04 KST)보다 늦다. d157 D3 json은 FAIL(09-27) → PASS(09-30 재평가). | `experiments/exp035_d157/` |
| 6 | runtime gate 변천 | 0.25s(임의 margin) → 0.5s(tournament 보정) → D3 v2(0.8/1.0s). 127ed3e6은 NOT_ELIGIBLE → PASS(사후 재정의로 기록됨). | proj 13, ledger |
| 7 | 최종 BT 범위 문구 | "마감 후 약 2주" 해석 vs staff "활성 제출 간 모든 경기"(#742571). doc 50의 문구는 doc 51에서 정정. Rules "최대 2개 선택" vs Evaluation "최신 2개". | FACTS F-T12, proj 50·51·58 |
| 8 | 결번·미기록 | EXP-009/010(proposal BLOCKED), EXP-012(사전등록 불가), EXP-019/020(대체), EXP-027(대체, 결과 없음), EXP-052(문서 없음, `analysis/exp052_oracle` 폴더만), EXP-059(미실행). | — |
| 9 | ID 이중 사용 | EXP-019가 두 안(opus55 V219-2SHOP, DP second factor) 모두에 쓰였다. EXP-013이 예약한 "EXP-014"는 mirror sale lead에 쓰였다. | proj, proposals |
| 10 | 빠진 값 | v0 전체 SHA, v171·v074 제출 시각, EXP-014 hosted 점수, EXP-001 stage 1 후보별 점수, 200시드 최종 승격 판정, 최종 BT 순위(평가 진행 중). | — |
| 11 | tape 수 | 743(수집) vs 742(EXP-042·CALIB) vs 750(listed). EXP-048A select 594(doc 36) vs 595(doc 31·35). | `experiments/exp041_top2400/` 등 |
| 12 | 상태 문서 미갱신 | `coordination/BOARD.md`·`evidence/HOSTED_LEDGER.md`가 09-28 23:30 이후 갱신되지 않았다. 09-29~10-01 제출은 `experiments/exp062/subs_*.txt`, `analysis/hosted_0930*/`에만 있다. `experiments/registry.csv`는 v0·EXP-006·007·008·011 다섯 행뿐이다. | — |
| 13 | NOTICE 문구 | `releases/exp062-L*`, `slot2r-Rc26_107`의 NOTICE.txt가 d157 문구를 그대로 반복한다(실제 후보 설명이 아님). | `releases/*/NOTICE.txt` |
| 14 | 사람·AI 주장 정정 이력 | Claude: DP 2450~2550 예상 오류, doc 33 "상대 관측 없음" 오류, doc 43 c26 ≥ d157 철회. Gemini: P1c HIRE 100%·NOOP 77/77, 09-10 정찰 수치 모순(인용 금지). Antigravity: EXP-025b "verification failures 0"(seat 오류). | proj 33·45, B·C 절 |
| 15 | step-91 상대 식별 | Antigravity는 V56(동률 FULL 26), Claude LB 판독은 V56에 17-9 승·DP 0924에 0-7 패. | `coordination/reports/antigravity/20260924-1845-STEP91-ID.md`, ledger 09-24 |
| 16 | v1 main.py SHA | `50efced8…`(KAGRI-012) vs `d6cdb83f…`(EXP-002 parent, tar 안). 차이의 원인이 적혀 있지 않다. | `coordination/reports/codex/20260908-1656-KAGRI-012.md` |

---
## 11. 부록

### 11.1 검증 방법론의 변천 [사실]
| 날짜 | 바뀐 것 | 왜 (원본 문구 요지) | 근거 |
|---|---|---|---|
| 09-06 | S8 paired score (vs starter) | 파이프라인 검증 | `experiments/results/S8_RESULTS.md` |
| 09-07 | AGENTS §7.1 "ladder not self": 승격 1차 지표 = 공개 4봇 paired | starter 지표는 순위와 무관(K5) | `AGENTS.md` §7.1 |
| 09-09 | R1~R8: 엔진 판정 우선, `[COMMUNITY]` 태그, 무음 실패 확장, 카드 YAML 스키마, 1,200s 예산, 슬롯 상관, KILL 부활 차단, BOARD 신선도 | 흡수량 오류 등 | proj 05 |
| 09-10 | **RESET**: 4봇 풀·§7.1b 2층 지표·400판 승격 폐기, AGENTS 동결, tape router | 풀 천장 59위, 정지 = 후퇴 | `coordination/RESET_2026-09-10.md` |
| 09-11 | 사전등록 카드 G1~G6 (h2h / pool 47 / public / 안전 / runtime / self) | 숫자 임계 고정 | EXP-006·007 카드 |
| 09-12 | 공용 가설 원장 `HYPOTHESES.md` + "원장에 없는 ID면 실행 금지" | 에이전트 간 추적 | `AGENTS.md` §3.1 |
| 09-14 | gate 분리: 일반 release gate(절대 0) vs EXP별 gate, `sell_unfilled` 진단으로 강등, `shed_unsold` 신설 | F-T7 정의 오류 | `coordination/reports/codex/20260914-2043-GATE-SPLIT.md` |
| 09-16 | actual-tar preflight 선행 | 실제 제출 바이트로 검증 | P1b |
| 09-18 | **F0 fast lane**: 공개 exact는 gate §3-2(Identity/Schema/Runtime/Isolation/License/Ledger)만으로 제출 | 동메달 목표, 시간 | `coordination/proposals/claude/20260918-DONOR-TAPE-FASTLANE-PLAN.md` |
| 09-23 | CANDIDATE-POLICY: slot A/B, INCONCLUSIVE 제출 조건, 24h 후 −100이면 rollback, 비상 경로 ≥14/20 | 제출 결정 규칙화 | `coordination/proposals/claude/20260923-CANDIDATE-POLICY.md` |
| 09-25 | **D3 v2** runtime gate (엔진 한도 기반) | 0.25s는 임의 margin | proj 13 |
| 09-25 | SEARCH-LOOP v2.3: 동결 지표 + successive halving + 사전 고정 holdout → calibration BLOCKED로 정지 | 변별력 ≈0 | proj 15 |
| 09-26 | Wilson 하한·bootstrap 기반 다단계 screen (Stage 1→3) | 수작업 대체 | proj 19·21 |
| 09-27 | tape open-loop 평가(Kaggle kernel), hosted 재현 확인 | 163/163, 136/136 | EXP-033 |
| 09-28 | "d157′ ≥ d157 모든 panel", 팀 단위 holdout(5팀) | 선택 편향 차단 | proj 31·35 |
| 09-29 | freeze-before-result screen, evaluator calibration(c26 P +0.054 과대평가) | 로컬로는 d157 대체 판단 불가 | `coordination/reports/codex/20260929-1120-CALIB.md` |
| 09-30 | **closed-loop 사전등록 A1–A12** (hosted 확인·revert 규칙 포함), 외부 검토자(Sol) 7회 | tape 낙관 편향 +0.17 | `experiments/exp062/PREREG.md` |

### 11.2 결정 로그 (사람 결정 중심) [사실]
| 날짜 (시각) | 결정 | 근거 |
|---|---|---|
| 09-06 | 첫 제출은 파이프라인 검증용 최소 봇. 계획 문서는 단독으로 읽히는 정본. 24일 안에는 룰베이스 + 좁은 ML까지만 | proj 03 |
| 09-09 | ABSORPTION 정정, 동적 매도 상한, AGENTS R1~R8 | proj 05 |
| 09-10 | RESET: 목표 상위 500위(≈2,535), tape router, 매일 제출, AGENTS 동결. 라이벌 tape는 분석 입력으로만 | proj 07 |
| 09-10 | yhay81 exact 사람 제출 (gate HOLD 예외) | ledger |
| 09-11 | 공개 코드 파생물을 최종 슬롯에 써도 된다 | EXP-006 카드 |
| 09-15 | 마감 계획: 09-27 새 전략 중단, 09-28 freeze, 09-29 제출 완료 | `plan/kaggriculture_deadline_plan_20260915.md` |
| 09-16 | **목표 변경: "점수를 지킬 필요 없어. 최소한 동메달을 확보하기 원해."** | `coordination/proposals/claude/20260916-BRONZE-TARGET-PLAN.md` |
| 09-18 | EXP-011만 승인, EXP-013 불허. K3 범위 축소, F0 fast lane 승인. 팀 병합 안 함 | `coordination/reports/claude/20260918-FASTLANE-AUTHORIZATION.md` |
| 09-18~20 | 역할: 단순 수집은 Antigravity, 판단은 Codex. 판단 없는 작업은 모두 Antigravity | BOARD |
| 09-19 | "§3 A 채택" (공개 노트북 exact) | `coordination/proposals/claude/20260919-F0-STAGE-B-RESULT-DECISION.md` |
| 09-22 | EXP-016 INCONCLUSIVE인 채 hosted 실험 제출 | ledger |
| 09-24 | "B안": step-91 봇 식별 후 exact만 제출 → DP | `coordination/reports/antigravity/20260924-1845-STEP91-ID.md` |
| 09-25 14:33 | 하루 1실험 → 동결 지표 + 자율 탐색 + 사전 고정 holdout | `coordination/proposals/claude/20260925-SEARCH-LOOP-CODEX.md` |
| 09-25 19:48 | D3 v2 승인 | proj 13 |
| 09-26 | "v171이 더 뛰어나다고 가정하고 진행". 토큰 절약 지시 | proj 19·22 |
| 09-27 | Kaggle private dataset·notebook(5개) 사용 승인 | proj 31 |
| 09-27 20:07 | **"메달권 밖이면 위험 감수"** (사전 고정 FAIL 불변 원칙보다 우선) | proj 28 |
| 09-27 21:36 | v171/v074 exact 재제출 금지, 둘째 슬롯은 "d157 + 개선" | proj 28 |
| 09-28 14:05 | d157′는 모든 panel에서 d157 이상이어야 제출. 슬롯2는 공격적 후보 허용. 상위 bot 방식 흉내 승인. 팀 단위 holdout | proj 30·31 |
| 09-28 22:10 | **"제출하지 않음은 없다. 계속 개선한다."** 연구에 Sol(GPT-5.6) 병행 | proj 33·35 |
| 09-29 | 한 슬롯을 다른 방식으로 분산. 다른 팀 전체 기록 route 허용(market만 떼어 붙이기는 금지 유지). 밤사이 무인 운영 | proj 52·55 |
| 09-30 | 목표 "현재 점수대에서 지는 상대를 이기는 개선". Claude 직접 제출 허용. 시한 21:00 KST | proj 59 |
| 09-30 22:50 | 최종 조합 A = {강한 L, d157 사본} | proj 60 |

### 11.3 KILL 목록 (최종 상태) [사실]
| # | 죽은 방향 | 근거 | 재검토 조건 |
|---|---|---|---|
| K1 | 4번째 구획(SE $4,000) 매입 | rayk 450판 모두 10-0 패 | 액션 예산 근본 증가 |
| K2 | 2턴 앞 선행매도 | 1턴이 정답 (rayk) | 엔진 가격 갱신 변경 |
| K3 | 라이벌 market 기록만 다른 경로에 graft | 09-18 범위 축소. 같은 경기 전체 재생은 09-29 허용 | 미정의 |
| K4 | 광범위 잡초 청소 | 17-17-66, −35 코인 | — |
| K5 | starter 상대 평균 bank 최적화 | 방법론 오류 | 없음 |
| K6 | 순수 self-play PPO | 80k 벽 (discussion 738619) | 엔진 고정 + ≥10일 여유. doc 52는 이 근거가 낡았다고 서술했지만 마감 전 시간상 RL은 제외 |
| K7 | 여러 선생 BC | 스타일 붕괴 (다른 대회) | — |
| K8 | 멜론 가격 회복 대기 | 흡수 1/일 | — |
| K9 | GOOSE 도입 | EGG 가치 상한 5.5% | 액션 여유 + EGG 수요 |
| ~~K10~~ | ~~MELON 재배분~~ | **09-10 RETRACTED** (측정 불가) | — |
| 방법론 | n 없는 승률 임계 / 결과 보고 n 늘리기 / ±50 변동에 반응 / 같은 봇 재제출로 리롤 | — | — |
| 실험 라인 종료 | exact B schedule(008), 상수 ±1(036), layer bypass(030), H1·LATE·ALTMECH·HYPGEN2, 판매 hook(045/047/048), tomato·Fritz·geese(054/055/057), route 재배정(058) | proj 31·49·50 | — |

### 11.4 용어
| 용어 | 뜻 |
|---|---|
| tape | 한 경기에서 한 플레이어가 낸 719턴 행동 기록. 그대로 재생하면 봇이 된다 |
| route / donor | 재생할 tape(경로)와 그 출처 팀 |
| open-loop / closed-loop | 상대 행동을 기록대로 고정(상대가 반응하지 않음) / 실제 봇끼리 대국 |
| mirror (판) | step 144까지 두 농장이 같은 경기. 같은 공개 계보끼리 만나면 생긴다 |
| hosted | Kaggle 서버 레이팅·경기 |
| FIFO | 새 제출이 가장 오래된 활성 제출을 은퇴시키는 규칙 |
| BT | Bradley-Terry. 최종 순위 산정 방식. 활성 제출 간 경기만 센다(F-T12) |
| D3 gate | runtime gate. v2 = single <0.8s, step0 <0.8s, 6-worker <1.0s, 게임당 <30s |
| 55be / d157 / c26 | 공개 55be5d5f(tetsutani demand-preserving 계열) / 55be + `_S1002_PASSES` 35 / d157 + `_CA_MARGIN` −26 |
| 127ed3e6 / v171 / v074 | 공개 newmeta / 127 계열 + `_DP_H` 9 / v171 + `V9_RACE_DEFAULT` 45 |
| P2 / C1 / OMW / DP | lynnsakurai v2 / nathanjacob pipe16 / OneMoreWheat / tetsutani demand-preserving 0924 |
| glut lead (L4p 등) | 과잉 구간에서 tape가 계획한 판매를 K step 앞당김 (K=4 → L4p) |
| X / Rc26_107 | mirror 판이면 route 107, 아니면 c26 |
| W/D/L, seat | 승/무/패, 좌석(0/1). 같은 seed로 좌석을 바꿔 두 판 = paired |
| Wilson 하한, lo95 | 승률 신뢰구간 하한, 95% 하한 |

### 11.5 원본 파일 색인
| 종류 | 위치 |
|---|---|
| 사전등록 카드 | `experiments/cards/EXP-001 ~ EXP-018*.md`, `experiments/exp0NN_*/PREREG*.md` |
| 실험별 원자료·판정 스크립트 | `experiments/exp0NN_*/`, `experiments/registry.csv`(5행만) |
| 제출 원장 | `evidence/HOSTED_LEDGER.md`(09-28까지), `experiments/exp062/subs_*.txt`, `analysis/hosted_*/subs.txt` |
| 엔진·대회 사실 | `evidence/FACTS.md`, `OFFICIAL_SOURCES.md`, `ABSORPTION.md`, `ENGINE_ANIMALS.md` |
| KILL | `evidence/KILLS.md` |
| 가설 원장 | `HYPOTHESES.md` |
| 에이전트별 보고 | `coordination/reports/{claude,codex,antigravity,gemini,sol,cowork}/` |
| 제안·지시서 | `coordination/proposals/` |
| 상태·인수인계 | `coordination/BOARD.md`, `HANDOFF_*.md`, `RESET_2026-09-10.md`, `plan/CURRENT.md` |
| hosted 수집 | `analysis/*hosted*/`, `analysis/survey300_20260929/` 등 |
| 제출 바이트 | `releases/<label>/` (main.py, submission.tar.gz, SHA256SUMS, NOTICE.txt, gate-d3-*.json) |
| Claude 판정 문서 (프로젝트) | claude.ai 프로젝트 "Kaggriculture" `claude/00 ~ 60` |

---
*이 로그는 2026-10-01 기준 원본에서 재구성했다. 최종 BT 순위가 나오면 §1·§2.1·§3 마지막 줄에 추가한다.*
