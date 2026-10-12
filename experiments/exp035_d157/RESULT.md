# EXP-035 결과 — PASS (Claude, 2026-09-27 21:25 KST)
사전등록: experiments/exp035_d157/PREREG.md (sha b054c5bf…, 20:03 KST, EXP-033/034 결과 확인 전).
대상: d157 = releases/exp035-d157/main.py (sha 94a46c11…), submission.tar.gz sha 4281ea3c… (USTAR, member main.py 1개).

| 조건 | 기준 | 결과 | 판정 |
|---|---|---|---|
| 1 성능(EXP-032, 관측 후 인용) | transition lower95>0, legacy≥−0.10, hosted≥−0.10 | +0.141 / +0.026 / −0.075 | PASS |
| 2 runtime-A (EXP-034 Kaggle 순차 6경기) | DONE, overage 0, max<1.0, total<60 | max 0.247s, overage 0, total 4.31s | PASS |
| 3 runtime-B (D3 v2, 새 프로세스 15경기 1 worker) | max<0.8, total<30, error 0 | max 0.503s, step0 0.178s, total ≤3.30s | PASS |
| 4 tape (EXP-033 부분: P·d157 × hosted tape 350) | 127 변형 diff ≥ +0.10, 전체 diff ≥ 0 | +0.522 (lo95 +0.42) / +0.29 (lo95 +0.23) | PASS |

tape 세부(open-loop; v074 자기 경기 163/163 hosted 결과 exact 재현, invalid 0):
| 구간 | n | v074 | d157 | diff (lo95) |
|---|---:|---:|---:|---|
| 127 변형 | 112 | 0.228 | 0.750 | +0.52 (+0.42) |
| DP/55be 변형 | 62 | 0.516 | 0.839 | +0.32 (+0.18) |
| 기타 | 93 | 0.484 | 0.763 | +0.28 (+0.17) |
| 127 exact | 81 | 0.914 | 0.852 | −0.06 (−0.15) |
| 상대 LB <2200 | 139 | 0.770 | 0.878 | +0.11 |
| 상대 LB 2200–2400 | 161 | 0.357 | 0.764 | +0.41 (+0.32) |
| 상대 LB 2400+ | 50 | 0.240 | 0.660 | +0.42 (+0.26) |
한계: open-loop 는 상대 반응을 모델링하지 않아 선매형(55be 계열)에 낙관 편향 가능. closed-loop(EXP-032)에서 guard −0.14, hosted 재현 −0.075 의 약점은 남아 있다. rating 환산 불가.
결정: 사람 방침(09-27 20:07 "메달권 밖이면 위험 감수") 에 따라 제출 권고. 제출 시 FIFO 로 v171(56567563) 은퇴, v074(56577440) 유지.
