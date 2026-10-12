# EXP-045 사전등록 (Claude 2026-09-28 23:00 KST, 어떤 변형 결과도 보기 전)
기준선: d157·c26 의 games42 행(select 595)과 exp039 행(U 136, T 350, family, O127, V074). 기준선을 다시 돌리지 않는다. invalid 0.
Stage A (screen, 11 변형 × select 595): 변형−d157 paired 점수 차 점추정 > 0 인 것 중 상위 3개(동률은 act 변화 판 수가 적은 쪽)를 Stage B 로 보낸다. 0개면 LOCAL_FAILED.
  ※ select 는 선택에 썼으므로 이후 select 의 lower95 는 판정에 쓰지 않는다(선택 편향).
Stage B (확인, 상위 ≤3개): judge39 panel + holdout.
  B1 U 136, T 350: 각각 점추정 ≥ max(d157, c26)
  B2 family arena(D, HL63, M2965, FJ1010, d157 × 15000–15024 × 양 좌석): paired 차 ≥ 0
  B3 vs O127, vs V074: 각각 ≥ d157 − 0.02
  B4 holdout 5팀 148 tape: 점추정 ≥ max(d157, c26), 그리고 d157 대비 paired 차 > 0
  모두 통과한 것 중 B4 점추정이 큰 1개를 PASS 로 한다. 없으면 FAIL. 기준을 완화하지 않는다.
PASS → release(USTAR tar main.py 1개 mtime 0 + NOTICE + SHA256SUMS) + D3 gate → 사람 제출(FIFO 로 d157 은퇴).
