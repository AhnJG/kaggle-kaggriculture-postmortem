# c26 hosted 분석 계획 (Claude 09-28 20:10 KST, 데이터 수집 전 고정)
목적: 관찰만 한다. 새 제출 후보가 없으므로 이 결과로 제출 결정을 하지 않는다(d157+c26 유지는 EXP-043b NO CLUE 로 이미 결정).
표: sub(c26, d157) × {전체, LB <2200/2200–2400/2400–2600/2600+, family label(127ed3e6·55be5d5f·DP-0924·UNKNOWN)} W/D/L, score rate(무=0.5), Wilson95.
보조: 같은 op_submissionId 를 둘 다 만난 경우의 paired 차이(c26−d157). c26 표본이 30경기 미만인 칸은 "표본 부족" 으로만 쓴다.
검증: replay 재현 — 표본 10경기(c26 5, d157 5)에서 우리 쪽 action 이 releases main.py 로 exact 재현되는지 Claude 가 확인.
