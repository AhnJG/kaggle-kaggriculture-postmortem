# PREREG 추가안 (Claude 초안, Stage A 결과 보기 전 작성 — 사람 승인 시 발효)
작성 시각: EXP-048A 결과 도착 전. 이 파일 sha 를 결과 전에 기록한다.

## A1. 완화 기준 R2 (Stage B 에서 PASS 가 0개일 때만 적용, d157 을 은퇴시키는 제출용)
전제: 다음 제출은 FIFO 로 d157 을 은퇴시키고, c26 이 남는 안정 슬롯이 된다.
- R2-1 holdout 2400+ (기존 148 tape + 새 holdout 이 있으면 합산) paired Δ vs d157 점추정 ≥ +0.02
- R2-2 Stage A select Δ vs d157 > 0 (이미 선택 조건)
- R2-3 U 136, T 350, family arena, vs O127, vs V074 각각 ≥ d157 − 0.02
- R2-4 C26HOSTED 결과에서 c26 이 d157 보다 2200+ 구간 score rate 가 0.05 이상 낮지 않을 것(낮으면 제출 보류, 사람 판단)
- 통과 후보가 여럿이면 R2-1 점추정이 큰 1개.

## A2. EXP-047 hook 진단 규칙 (Stage A 에서 hook 이 떨어졌을 때만)
팀 구분(EXP-046 상한 step recall 기준, 결과 전 고정): 예측 가능 7팀 = saberzky, Joseph Ayanda, JM, thisray, 인공저능연구소( Artificial Idiocy Lab ), base_camp_2002, MISIS loss volos. 나머지 12팀 = 예측 불가군.
- 예측 가능 7팀에서 hook Δ vs d157 > 0 이고 예측 불가군에서 < 0 → 후속 1회 허용: "온라인 일치 gate"(상대의 지난 판매가 shadow 예측과 맞은 비율이 일정 이상일 때만 hook 발동) 1개 변형, 상수는 사전 고정 후 Stage A 부터 다시.
- 예측 가능 7팀에서도 Δ ≤ 0 → 기제 실패. EXP-047 계열 종료.
