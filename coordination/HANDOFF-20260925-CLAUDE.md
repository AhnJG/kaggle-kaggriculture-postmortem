# 인계 — 2026-09-25 19:40 KST (새 Claude 채팅: Coordinator + 실행자)

이전 Coordinator 채팅에서 작성. Codex 는 사용량 한도로 **09-25 23:38 KST 까지 중단**. 이 채팅이 탐색 루프의 **실행자 역할까지** 맡는다 (소유권 예외: 20260919 §0 과 같은 조건 — 사람 지시). Codex 가 돌아와도 이 채팅이 넘겨주기 전에는 같은 파일을 만지지 않게 사람이 조정한다.

## 0. 먼저 할 것
1. 이 문서 → `coordination/BOARD.md` 현재 절 → `coordination/proposals/claude/20260925-SEARCH-LOOP-CODEX.md` (v2.3) → `coordination/reports/codex/20260925-1846-NEWMETA-EXACT.md` → `experiments/search_20260925/instructions.md`, `calibration-policy.json`.
2. 루프 상태 확인: `experiments/search_20260925/state.json`, `workflow.log` 끝, `workflow-state.json`/terminal 파일 유무. (19:28 KST 기준 1b tournament screening 1780/2240, RUNNING)
3. 에이전트는 제출하지 않는다.
4. 도구: 사람 Mac 은 remote-devices 로 접근 (`$HOME/mnt/Kaggriculture`). **그 VM 셸에는 kaggle_environments 가 없다** — 경기 실행은 Mac 의 루프(`tools/search_loop.py`)나 사람이 터미널에서 돌리는 명령으로만. Claude 는 Kaggle 에 닿지 못함.

## 1. 현재 상태 (검증된 것)
- 활성 슬롯 FIFO: ① EXP-017 56490029 (09-23, 2010.8) → ② DP 0924 exact 56518910 (09-24, 2191.6 @09-25 13:52). **다음 제출은 EXP-017 을 은퇴시킨다.** 동메달 경계 약 2290 (09-24 저녁) → 현재 동메달 밖. 목표 = 동메달 복귀 우선.
- 새 주류 공개 파일 **127ed3e6** (추천 상위 notebook 4개 동일 바이트, 진입점 `ig_agent` 확인). release `releases/public-newmeta-127ed3e6-exact/` (tar sha 63e1554c…).
  - 로컬: vs DP 1000경기 **820-2-178 (0.821)**, DP80 66-14, E-5 20경기 16-4, panel47 42-5 (개발 자료), 예외 0, 재현 결정적.
  - runtime: 6-worker 부하에서 최대 step **0.7506초** (0.25초 초과 42경기, 0.5초 초과 6경기), game p99 최대 0.044초 → 우리 gate(0.25초) 미달로 NOT_ELIGIBLE 판정.
- 루프: `tools/search_loop.py` + `tools/search_stages.py` workflow 가 1b → (calibration-ready 있으면) calibration → search 로 자동 진행. 24 tests PASS. `calibration-policy.json` = Codex 가 제안한 기본값(아래 D1 로 승인).
- 알려진 차단: metric (d) tape 패널의 seed 정의 충돌 → search-ready.json 이 "d blocks pending Coordinator definition" (아래 D2 로 해소).

## 2. 이번 인계에서 확정된 결정 (사람 승인 = 이 문서로 새 채팅을 시작한 것)
- **D1 Codex 수치 기본값 승인**: calibration seed 2600–2619 × 양 좌석, 상대 풀 95% 이상 패배 필터(잠정 부모 = tournament confirmation 1위), 상수 변형 정수 ±1 · 실수 ±10% · 0 은 ±0.1, KILL 범위 제외. `calibration-policy.json` 그대로.
- **D2 tape 패널 holdout 정의**: tape 경기는 **원래 replay 의 seed·좌석을 그대로** 쓴다 (다른 seed 로 돌리면 tape 가 무의미). holdout 은 seed 가 아니라 **episode 로 나눈다**: 각 점수 구간에서 episode id 오름차순으로 1–20번째 = calibration/search (현재 선택과 동일), 21–40번째 = CP1 holdout, 41–60번째 = CP2 holdout. 부족한 구간은 개수를 보고하고 그 구간은 해당 checkpoint 에서 공개 풀만 사용. `calibration-policy.json` 에 `tape_holdout` 항목으로 추가하고 sha 갱신, 테스트 추가.
- **D3 runtime gate 재정의 (사람 결정, 사후 변경임을 명시)**: 0.25초는 Coordinator 가 임의로 둔 여유값이었고 엔진 한도가 아니다. 엔진: step 당 `actTimeout=1`초 + 에이전트당 `remainingOverageTime=60`초 누적 여유, 에피소드 1,200초 (FACTS 23행, docs/review_insights.md 40–41행). 새 gate (모든 후보 공통):
  - **단일 worker** 로 느렸던 seed 재측정(상위 10개: 10198 양 좌석, 10062/1, 10119/0, 10118/0, 10117 양 좌석, 10200/0 …) 최대 step **< 0.8초**
  - 6-worker 부하 최대 step **< 1.0초**, 에이전트 누적 시간/경기 **< 30초**, 예외 0
  - NEWMETA 판정은 기록상 NOT_ELIGIBLE(0.25 기준) 로 남기고, 새 gate 판정을 **별도 줄**로 추가한다. HOSTED_LEDGER 에 "사람 결정으로 gate 재정의" 명시.
- **D4 127ed3e6 exact 슬롯 B 제출**: D3 새 gate 통과 즉시 사람에게 알림 → 사람이 제출 (EXP-017 은퇴). 제출 후 6시간 안에 hosted 경기 상태(ERROR/TIMEOUT) 이상이 보이면 즉시 보고(사람이 DP·EXP-017 등으로 되돌림 판단).
- **D5 두 번째 슬롯 원칙**: 127ed3e6 이 hosted 에서 DP 보다 확실히 높으면(24h, 100점 이상 또는 두 번 연속 우위) anchor = 127ed3e6, DP 은퇴. 두 번째 슬롯 = "A 를 넘을 확률 × 폭"(정책 E-3) 기준으로 — 탐색 후보(holdout SUCCESS)가 있으면 우선, 없으면 1b tournament 에서 **127ed3e6 과 다른 계열이면서 metric 이 127ed3e6 과 0.05 이내**인 파일, 둘 다 없으면 DP 유지.

## 3. 이 채팅의 할 일 (순서)
1. 루프 상태 확인 → 1b 보고 `coordination/reports/claude/<ts>-PARENT-TOURNAMENT.md` (workflow 가 쓰지 않으면 `tournament-screen.json`·games.jsonl 로 작성). 상위 5개, 계열, 두 상대 점수율.
2. D3 재측정: 사람에게 Mac 터미널에서 돌릴 **단일 worker 명령**을 만들어 준다(`tools/search_loop.py --manifest <새 manifest>` with workers 1, 위 seed 목록, 상대 DP). 결과로 새 gate 판정 → D4.
3. D2 반영 (policy + 테스트) → workflow 가 calibration 을 진행하게 둔다. calibration 결과(BLOCKED_CALIBRATION 이면 멈춤) 보고.
4. 탐색 진행 감시, 6시간마다 `coordination/reports/claude/<ts>-SEARCH-STATUS.md`. CP1 = **09-26 21:00 KST** (사람 참석 가능): holdout 1회 → SUCCESS 면 release + gate → 사람 제출 판단.
5. launchd: 사람이 아직 설치하지 않았으면 NEWMETA 보고의 설치 명령을 안내 (controller.lock 이 중복 실행을 막음). 덮개 닫힘 = 일시정지, 열면 재개.
6. 09-26 오후 사람에게 두 봇 hosted 점수 요청 → HOSTED_LEDGER·BOARD 갱신.

## 4. 금지
제출, Kaggle 다운로드, holdout(seed 9000–9599 및 D2 의 holdout episode)을 checkpoint 밖에서 사용, 판정 기준 사후 변경(D3 은 사람 결정으로 명시된 예외 하나뿐), BOARD 외 타 소유 파일의 무단 수정.
