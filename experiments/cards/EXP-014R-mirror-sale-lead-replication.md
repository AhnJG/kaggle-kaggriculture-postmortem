# EXP-014R — EXP-014 새 seed 재현 (같은 artifact, 유효성 조건만 사전 재정의)

hypothesis_id: HYP-0033
test_id: TEST-F0-MIRROR-LEAD-R2-20260920

사전등록 2026-09-20 (Claude). **새 seed 결과를 보기 전에 커밋.** EXP-014 는 INVALID 로 남는다 — 이 카드는 EXP-014 를 고치는 것이 아니라 별도 시험이다.

## 왜 유효성 조건을 바꾸는가 (결과가 아니라 이미 확인된 사실 때문에)

EXP-014 의 invalid 조건 "P2 vs P2 무승부 ≥ 25/30" 은 복제전이 거의 항상 비긴다는 가정이었다. B0 에서 비무승부 6경기는 **모두 같은 seed 의 두 좌석이 부호만 반대**(3002 ±131, 3011 ±209, 3012 ±884)였다. 엔진은 HIRE·BUY_LAND 를 player 0 먼저 처리한다(`kaggriculture.py:571-582`). 즉 비무승부는 좌석 비대칭에서 나오고, 두 좌석을 합치면 대칭이다. 그래서 유효성은 "무승부 비율"이 아니라 **"기준선이 좌석 합으로 대칭인가"**로 본다. 성공·실패 임계는 EXP-014 와 **같다.**

```yaml
id:            EXP-014R
artifact:      releases/f0-mirror-lead-exp014/submission.tar.gz   # sha256 be529b5cce50c53e738b79094e41852d8195b4f03cb8a391fd1c9ddee1600d29 (EXP-014 과 같은 bytes)
parent:        releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz   # 1178ffa0…f388
one_change:    EXP-014 와 동일 (거울 모드일 때 _ADV_LOOK 3 -> 4)
opponents:     EXP-014 와 동일 (mirror = P2, panel 5개, 같은 경로·SHA)
seeds:         mirror [4000..4014] / panel [4000..4009]   # EXP-014 에서 쓰지 않은 seed
seats:         both
runner:        tools/arena.py --seed-start 4000
success:       M 점수 >= 22.5/30  AND  M 점수 - B0 점수 >= 6.0  AND  N 회귀 <= 2/100  AND  N 변형 총점 >= N P2 총점 - 2.0
failure:       M 점수 <= 16.5/30  OR  N 회귀 >= 6/100
inconclusive:  그 밖
invalid:       B0(P2 vs P2, seed 4000–4014 양 좌석) 점수가 15.0 ± 2.0 밖  OR  무승부 < 20/30  OR  예외/ERROR >= 1  OR  입력 SHA 불일치
next_if_success: 사람 결정 — EXP-014 artifact hosted 제출 + P2 재제출로 동시 비교
next_if_failure: 거울 창 변경 폐기
```

정의(M, N, 회귀, 거울 모드)는 EXP-014 §정의와 같다. 실행은 Antigravity, 판정은 Claude.

---

## 결과 기록 (2026-09-20, Claude 판정 — 카드 본문 무변경)

입력: `coordination/reports/antigravity/20260920-2215-EXP014R-RUN.md`, `analysis/exp014r/summary.json` (SHA `8273195f45353466a50fb24263192630a0516a9ae1cfbab3e648344e7bc09b82`). Claude 가 raw 12개에서 재계산해 일치 확인. 예외·ERROR 0/260.

| 조건 | 값 | 기준 | 충족 |
|---|---|---|---|
| invalid: B0R 점수 15.0±2.0 | 15.0 (1/28/1) | 안 | 유효 |
| invalid: B0R 무승부 ≥ 20 | 28 | ≥ 20 | 유효 |
| success: M ≥ 22.5 | **22.0** (22/0/8) | ≥ 22.5 | **아니오 (0.5 부족)** |
| success: M − B0 ≥ 6.0 | 7.0 | ≥ 6.0 | 예 |
| success: N 회귀 ≤ 2 | 0 | ≤ 2 | 예 |
| success: N 총점 ≥ P2 − 2 | 92 vs 92 | ≥ 90 | 예 |
| failure: M ≤ 16.5 또는 회귀 ≥ 6 | 22.0 / 0 | — | 아니오 |

**판정: INCONCLUSIVE.** 결과를 보고 seed 를 늘리거나 두 실행을 합쳐 다시 판정하지 않는다(방법론 KILL).
참고 기록(판정 근거 아님): EXP-014 무효 실행 25/0/5 와 이번 22/0/8. 패널 200경기 회귀 합계 0.
fast lane 계획 §4 단계 F 의 hosted 진입 조건("로컬 선별에서 패배 증가 0")은 충족한다 — hosted 제출 여부는 사람 결정.
