# EXP-060 MBR — 거울판 그룹별 route 표 (사전등록, Claude Opus 5.5, 2026-09-29 23:50 KST)
작성 시점: M0(거울판 표시)만 끝났고, 이 실험의 어떤 경기 결과도 보기 전이다. 계획: plan/kaggriculture_explore0930_plan_claude-opus-5.5.md.

## 가설 (바꾸는 요인 1개)
step 144 에 두 농장이 완전히 같은 판(거울판, slot2_x/rg_layer.py 와 같은 판정)에서만, 상점 그룹 g∈{Y,D,S}(experiments/exp058_route/effective_route_by_pair.json 의 d157 실효 route 9→Y, 105→D, 그 밖→S)마다 정한 route 를 쓰면 X(모든 거울판 107)보다 점수가 높다. 비거울판은 기반 봇 그대로.

## 자료
- 선택 pool: experiments/exp060_mbr/m0_final.json 의 mirror=true 504판(Y 125, D 166, S 213). HF 78판 제외.
- M1 screen 집합: 그룹마다 40판. pool 을 (panel, tape 경로) 순으로 정렬한 뒤 panel 을 돌아가며 뽑는다(결정적, make_m1.py). 나머지(약 384판) = M2 확인 집합.
- holdout: HF 78판 + 09-30 07:30 수집하는 X·D' hosted 경기로 만든 새 panel(NEW). 선택에 쓰지 않는다.

## 단계와 판정
- M1: FM{r}(d157 + 거울판에서 route r) × 41 route + d157 × screen 120판.
- M2: 그룹마다 M1 평균 상위 3 route + 기존(d157) + 107 을 그 그룹의 M2 확인 집합 전체에서 실행. (EXP-061 donor route 는 09-30 06:00 까지 준비되면 그룹별 최대 5개를 같은 방식으로 추가.)
- 그룹 g 의 route: M2 평균 점수 최고 route r*. r* ≠ 기존이고, M2 에서 (r* − 기존) ≥ +0.05, 경기(tape) 단위 bootstrap 2,000회 90% 하한 > 0 일 때만 채택. 아니면 기존 route. 동점은 기존 → 107 → 번호 작은 순.
- 후보: C_d = d157 + 표, C_c = c26(experiments/exp039_camargin/variants/c26.py) + 표. 표가 세 그룹 모두 107 이면 C_c = X 이므로 C_d 만 본다.
- M3 holdout (HF + NEW): C_d, C_c, X(releases/slot2r-Rc26_107/main.py), d157, c26. 전체와 거울판 부분을 따로 보고, bootstrap 구간을 붙인다.
- 기반 선택: 판독 B 에서 비거울판 (X 실전 − D' 실전) 90% 구간 상한 < 0 이면 C_d. 아니면 holdout 전체 평균이 높은 쪽(동점 C_d).
- 제출 조건(모두): ① holdout 전체 C − X ≥ 0 ② holdout 거울판 C − X > 0 ③ closed-loop (C 대 d157, C 대 55be exact; 각 seed 60000–60039 × 2좌석) 점수가 같은 jobs 의 X 점수 − 0.03 이상. 판독에서 거울판 (Δ2 − Δ1) > +0.10 이면 X 이상 ④ D3 v2 PASS(max < 0.8s, total < 30s, error 0), holdout·closed-loop 에서 agent 오류 0.
- 불통과면 제출하지 않는다({X, D'} 유지).

## 고정
엔진 1.32.7, 위 tape·seed·좌석. 결과를 본 뒤 규칙·집합·기준을 바꾸면 새 번호로 기록한다. 판단 보조로 Sol 검토를 받아도 이 규칙은 바꾸지 않는다.
