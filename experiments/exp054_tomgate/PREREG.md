# EXP-054 사전등록 (Claude 09-29, 결과 전)
가설: 공급 부족 품목 TOMATO 의 기존 투자 모듈(_CXTB, day 18 땅+토마토 10그루)을 더 자주 열면(기대 매출 기준 9000 → 7000/6000) 현재 상대 집단에서 c26 보다 낫다.
단일 요인: _CXTB_MIN_REVENUE. 부모 c26(ff230c83…). 변형 X7(7000), X6(6000).
Stage 1 (현재 상대 집단 tape 269, experiments/exp051_curpop, 기준선 = EXP-051 의 c26 행): 변형 − c26 paired 점추정 > 0 이고, 투자가 새로 열린 판(행동이 달라진 판)만 따로 본 Δ 도 > 0.
Stage 2 (Stage 1 통과 시): 주 holdout H 219(exp041 holdout 148 + exp049 H 71) 와 exp049 F 228 에서 c26 대비 Δ ≥ 0, family arena(exp039 jobs) c26 대비 ≥ −0.02, 새 HOSTEDPM 상대(시간 분리 holdout, EXP-051 에 없는 경기) 에서 c26 대비 Δ ≥ 0.
둘 다 통과하면 Stage 1 점추정이 큰 쪽. 결과를 본 뒤 기준값(7000/6000)을 바꾸지 않는다.
