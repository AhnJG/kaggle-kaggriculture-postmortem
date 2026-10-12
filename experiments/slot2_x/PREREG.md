# SLOT2-X 사전등록 (Claude 2026-09-29 18:15 KST, 후보 결과 전)
사람 승인(09-29): Fritz식 생산 재설계로 두 번째 슬롯용 봇 X 를 찾는 자율 루프. 중단 09-30 18:00 KST(09:00 UTC). holdout 최대 2회 개방. 제출은 사람.
목적: 평균 점수가 아니라 **보험**이다. d157 과 평균은 비슷하되 d157 이 지는 판에서 이기는 봇.

## 부모와 수정 범위
- 부모 d157 = releases/exp035-d157/main.py (sha 94a46c11…). 변형은 부모 바이트를 그대로 두고 파일 끝에 wrapper 를 붙인다(EXP-055 방식: `_IMPL.chassis.routes` tape 편집 또는 진입점 wrapper).
- 파일 위치: experiments/slot2_x/variants/. releases/·main.py·src/ 는 수정하지 않는다.
- 엔진·RNG 수정 금지. holdout seed 9000–9599 사용 금지.

## 선택 panel S (반복 사용 허용)
- S = experiments/exp051_curpop 269 tape (C26HOSTED, as_of 2026-09-28T17:27:08Z). d157 기준 0.606.
- L = S 중 d157 tape 점수 < 1 인 111판(패 101, 무 10).
- 스모크: S 앞 10판, 오류 0 이고 행동이 d157 과 달라야 다음 단계.
- 선별: S 중 고정된 80판(jobs 순서 앞 80) → S-a 추정이 −0.10 미만이면 버림.
- 적격 조건: S-a = mean_S(X) − mean_S(d157) ≥ −0.03, **그리고** S-b = mean_L(X) − mean_L(d157) ≥ +0.15.
- 적격 후보가 여럿이면 S-a 가 큰 것을 holdout 에 올린다(동률이면 S-b).

## holdout (개방 최대 2회, 1회에 후보 1개)
- HF(전방 현재 집단): d157·c26 hosted 경기 중 endTime > 2026-09-28T17:27:08Z 인 것.
  - 출처: analysis/hosted_20260929b(74판) + 루프 중 Antigravity 가 새로 수집하는 d157/c26 hosted 경기(HOSTED0930, 09-30 수집 시각까지). 중복 episode 는 1회만.
  - 중복 없는 상대 tape 로 만든 뒤 X·d157 을 같은 seed·좌석으로 실행한다.
- HT(상위 팀): exp058 Stage C 와 같은 H ∪ F 집합(exp041 holdout 5팀 + exp049 fresh), 단 **target 팀이 Fritz Cremer 인 tape 은 제외**(가설 생성에 Fritz 경기를 봤기 때문).
- 통과 조건(모두):
  - H-a: HF 에서 X − d157 ≥ −0.03
  - H-b: HF 중 d157 점수 < 1 인 판에서 X − d157 ≥ +0.10
  - H-c: HT 에서 X − d157 ≥ −0.05
  - D3 v2 (single/step0/total/error 4항목) PASS
  - closed-loop X vs d157 20판(seed 15000–15009 양 좌석) agent error 0 (점수는 기록만)
- 1회차 불통과면 2회차는 다른 후보로만. 2회 모두 불통과 → FAIL, d157 + c26 유지.

## 한계(미리 적어 둠)
- tape 은 open-loop 라 상대 반응을 재현하지 않는다.
- S 를 반복 사용하므로 S 추정은 위로 편향된다. 결정은 holdout 이 한다.
- HF 는 작다(수집 전 74판). H-b 부분집합은 더 작다.
- 결과를 본 뒤 기준·panel·중단 시각을 바꾸지 않는다(바꾸면 새 번호).
