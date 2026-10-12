# EXP-043b 사전등록 (Claude 09-28 19:35 KST, 43b 결과 보기 전)
문제: EXP-043 은 d157 패배 tape 130개만 실행 → "팀 합계 점수" 는 d157 승리 tape 를 bot 도 이긴다고 가정한 상한값.
기존 V074(127 계열) games42 참고: Shawn404 +6 flip / −5 lose, thisray +3/−3 → 상한 가정이 틀릴 수 있음.
추가 실행: 1차 판정 CLUE 16개 bot × 5팀의 d157 승리 tape 49개 = 784경기 (같은 run.py, 엔진 동일; VM parity 3/3 exact).
판정(원 규칙 그대로, 데이터만 완성): bot 이 d157 패배판 ≥10개 승리 AND 어떤 팀에서 (bot 팀 전체 점수 − d157 팀 전체 점수) ≥ +0.15 → CLUE.
없으면 NO CLUE → 새 탐색 중단, d157+c26 유지 권고.
