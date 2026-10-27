# 지시서 — <task_id>

칸만 채운다. 서술형 기준이 있으면 받는 쪽은 BLOCKED 로 돌려보낸다.

| 칸 | 내용 |
|---|---|
| 목표 (한 문장) | |
| 받는 에이전트 · 모델 · effort | |
| 입력 경로 (+ SHA) | |
| 산출 경로 | |
| 판정 기준 (숫자) | |
| 유효성 카운터 | action_count, agent_errors, seat_match |
| 중지 조건 | 시간 상한, 사용량 상한, 오류 발생 시 |
| 하지 말 것 | 소유 밖 파일 수정, 외부 행동, 기준 변경 |
| 보고 위치 | coordination/reports/<agent>/YYYYMMDD-HHMM-<task_id>.md |
