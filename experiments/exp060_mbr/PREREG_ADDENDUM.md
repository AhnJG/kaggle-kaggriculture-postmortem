# EXP-060 PREREG 보충 A1 (Claude, 2026-09-30 03:25 KST — 07:30 NEW 자료 수집 전, HF·closed-loop 결과는 본 뒤)
근거: Sol 2차 검토(coordination/reports/sol/20260930-0320-EXP060-REVIEW2.md). 최종 순위는 {D', 새 후보} 중 나은 쪽이므로 목적함수는 portfolio 다.
- 기반 선택 변경: 기본 후보 = Cc (거울판만 새 표, 비거울은 X 와 같음). 예외: 판독 B 비거울 (X 실전 − D' 실전) 90% 상한 < 0 이면 Cd(원 규칙 유지). 원 규칙의 "동점 Cd" 는 폐기. 이 변경은 HF 에서 Cd·Cc 전체 평균이 같은(0.603) 것을 본 뒤다 — 결과를 유리하게 바꾸려는 것이 아니라 동점 처리의 목적함수를 바로잡는 것이다.
- 제출 중단 조건 추가(원 조건 ①–④ 에 더함, 모두 HF+NEW 합산 기준, NEW 단독은 보고만): ⑤ portfolio max(d157,C) − max(d157,X) < 0 ⑥ 판독 A ≤ 0 이고 거울판 B − A > +0.10 이면 closed-loop C ≥ X 필요(원 ③ 강화와 같음) ⑦ A·B 부호가 반대이고 |B − A| 가 C − X 추정치보다 크면 중단.
- 보고 추가: 거울판 그룹(Y/D/S)별 C − X (judge_m3.py d9ce8d72b78c 의 M3_NEWgroup_*; 이름과 달리 HF+NEW 전체).

# 보충 A2 (Claude, 2026-09-30 04:00 KST — NEW 자료 전)
- 버그 수정: cand/manifest-finalN.json 키가 Cd_final/Cc_final 이라 prep_m3.py finalN 이 KeyError 로 멈출 상황이었다 → Cd_finalN/Cc_finalN 으로 고침(같은 파일). 가짜 자료로 finalT 모의 실행 통과.
- 예비 후보 Cn = Cc_nodn (거울판 D·S→110, Y 는 기존 route; 다른 팀 기록 없음). 용도: 다른 팀 기록 사용에 문제가 생길 때의 대체안. 판정 대상이 아니라 보고만 한다(제출 후보는 Cc 그대로). extra_arms.json 으로 NEW panel 에 자동 포함.
- HF 에서 이미 본 것(판정 변경 없음): Cn 0.551 대 X 0.571(−0.019), Cc 의 HF 우위(+0.032)는 거의 전부 Y 거울판 DN29(+0.25, 12판)에서 나왔고 D·S(110)는 0.00/−0.02(13·24판).
