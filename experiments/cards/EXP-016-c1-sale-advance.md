# EXP-016 — C1 에 V53 판매 앞당김 층을 그대로 이식

hypothesis_id: HYP-0035
test_id: TEST-C1-ADV-20260922

사전등록 2026-09-22 (Claude). **실행 전 문서.** seed·상대·임계 변경 금지. 결과를 본 뒤 기준을 고치지 않는다.
근거: coordination/reports/claude/20260922-C1-HB-ANALYSIS.md. 범위: fast lane "공개 exact + 개선 1개".

```yaml
id:          EXP-016
parent:      releases/public-nathanjacob-pipe16-exact/main.py   # 827ddf2997fa442e80baadebc4cc91ffaeedec1ff333c1fa7d872b0f1d448181 (hosted 56426857)
candidate:   releases/f0-c1-adv-exp016/main.py                  # 9d58536d37d02d2587072cd7465fb0244eb3e558cc72521d5c5ad07a94876013
             # tar submission.tar.gz 4071f6c5b39c05be300dfb5ecdd101b30afd8cb0fe6c2b7b449093e2f00def76 (main.py 한 줄)
one_change:  parent 바이트 끝에 releases/public-ozer-v53-exact/main.py:3532-3629 (EXP293 _adv_apply + _adv_frontload + wrapper) 를 그대로 붙임. 마지막 callable = 새 agent
fixed:       [parent 바이트 전부, _ADV_* 값은 V53 원본 그대로 (LOOK 3, FROM 144, TO 718, FRONT True)]
seeds:       2100-2139 (새 seed, 분석에 쓰지 않은 것), 양 좌석 = 80경기씩
blocks:
  A_mirror:  candidate vs parent
  P_c4:      candidate vs releases/public-ozer-v53-exact ; 대조 parent vs 같은 상대
  P_c5:      candidate vs releases/public-ozer-v51-exact ; 대조 parent vs 같은 상대
  P_c2:      candidate vs releases/public-thomastschinkel-metav4-v13-exact ; 대조 parent vs 같은 상대
  P_p2:      candidate vs releases/public-lynnsakurai-farming-score-v2-exact ; 대조 parent vs 같은 상대
success (모두 만족):
  - A_mirror: seed 단위 순승 (W-L, 40 seed 기준) >= +10
  - 패널 4개 합산: candidate 패배 수 <= parent 패배 수 (패배 증가 0)
  - 패널 어느 한 상대도 candidate 패배가 parent 보다 +2 경기 이상 많지 않음
  - 예외 0, 최대 step 시간 < 0.5s
failure: A_mirror 순승 <= 0 이거나 패널 합산 패배 증가
inconclusive: 그 밖
validity: parent vs parent (A_mirror 대조로 20경기, seed 2100-2109) 무승부 >= 14/20 이어야 거울전 기준선 유효
```
실행: Antigravity. 판단: Claude. 제출은 사람.

## 결과 (2026-09-22, Antigravity 실행 · Claude 판정) — **INCONCLUSIVE**
보고: coordination/reports/antigravity/20260922-1701-EXP016-RUN.md. sha 확인 일치, 예외 0, validity 20/20 무승부 (유효).
| 블록 | candidate W/D/L | parent W/D/L | 패배 차 |
|---|---|---|---:|
| A_mirror (seed) | 31/1/8, 순승 +23 (기준 ≥ +10 충족) | — | — |
| P_c4 | 51/0/29 | 43/0/37 | −8 |
| P_c5 | 64/0/16 | 60/0/20 | −4 |
| P_c2 | 70/0/10 | 76/0/4 | **+6 (기준 +2 초과)** |
| P_p2 | 80/0/0 | 78/0/2 | −2 |
| 합산 | 55 패 | 63 패 | −8 (충족) |
- success 셋째 조건(한 상대 +2 이상 금지) 위반 → 사전 규칙대로 success 아님. failure 조건(거울 순승 ≤ 0 또는 합산 증가)도 아님 → INCONCLUSIVE.
- 사람 결정 시 참고: hosted 상대 분포(20260922-1716-C1-HOSTED-MAP)에서 C2|C3 판정 상대 38/148. 가장 큰 패배원은 "step 53 까지 C1 과 같은 미확인 봇" 34경기(C1 4승 30패) — 이 상대에 대한 EXP-016 효과는 미측정.
