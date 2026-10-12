# PREREG 추가안 — 확정 (사람 승인 09-29, Stage A 결과 열람 전)
초안 sha 95712a455d6c3334(결과 전) → 아래 A3·A4 추가 후 확정. Stage A 결과는 이 파일 확정 전까지 열지 않았다.

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

## A3. holdout 정의 (FRESH2400 도착 시)
- 주 holdout H = 기존 holdout 5팀 148 tape + 같은 5팀의 새 경기(09-28 05:27 UTC 이후) tape.
- 보조 F = 선택에 쓴 19팀의 새 경기 tape. 경기는 새것이지만 상대 bot 은 선택에 쓴 것과 같을 수 있어 선택 편향이 일부 남는다. 그래서 F 만으로는 통과시키지 않는다.
- 엄격 기준 B4 와 완화 기준 R2-1 은 H 로 판정한다. 추가 조건: F 에서 d157 대비 paired Δ 점추정 ≥ 0.
- FRESH2400 이 Stage B 판정 전에 도착하지 않으면 H = 기존 148 tape 만, F 조건은 생략한다.

## A4. 두 번 제출 허용 (사람 09-29)
C26HOSTED 에서 c26 이 d157 보다 뚜렷이 나쁘면(R2-4 조건 위반), 통과 후보 X 를 제출해 d157 을 은퇴시킨 뒤 d157 동일 바이트(tar 4281ea3c…)를 다시 제출해 c26 을 은퇴시킨다 → 최종 활성 = X / d157(재제출). 두 제출 모두 사람이 한다. 마지막 제출 시한 09-30 21:00 KST 안에 두 번 모두 끝낸다.
