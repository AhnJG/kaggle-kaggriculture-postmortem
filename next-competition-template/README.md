# 다음 대회용 템플릿 — 사람 1명 + LLM 에이전트

> **English.** A starter folder for running a Kaggle competition with one human and a small team of LLM agents.
> It turns the lessons of this post-mortem into files:  a short agent contract,
> one "current state" file, CSV ledgers, and a check that blocks using a local metric until it predicts the leaderboard order of bots you have already submitted.

이 회고의 개선안([운영 회고 §4](../plan/kaggriculture_process_retrospective_claude-opus-5.5.md), [내 자원으로 어떻게 했어야 했나](../writeup/what-i-should-have-done.md))을 다음 대회에 바로 쓸 수 있게 만든 빈 양식이다. 다음 대회를 시작할 때 이 폴더를 새 저장소로 복사해서 쓴다.
그 대회에서는 실험 판정을 엄격하게 했지만, 로컬 평가가 실전 순위를 맞히는지 먼저 검증하지 않았고, 제출 규칙을 미리 정하지 않았고, "현재 상태" 문서 셋이 모두 낡았다.
이 템플릿은 그 세 가지를 첫날부터 막도록 짜여 있다.

## 들어 있는 것

| 파일 | 역할 | 회고의 근거 |
|---|---|---|
| [`AGENTS.md`](AGENTS.md) | 에이전트 공통 계약 (113줄) | 이전 계약은 폐기 조항이 남은 채 커졌다 |
| [`STATE.md`](STATE.md) | 유일한 "현재" 문서: 활성 슬롯, 평가기 검증 상태, 다음 행동, 에이전트 예산 | BOARD·HANDOFF·CURRENT 셋이 모두 마감 전에 멈췄다 |
| [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md) | 실험마다 한 줄 + 로컬↔실전 대조표 + 판정을 넘어선 제출 기록 | 실험 정보가 5~6곳에 흩어졌다 |
| [`ledger/experiments.csv`](ledger/experiments.csv) | 실험 ID 발급처 | ID 중복·결번이 생겼다 |
| [`ledger/submissions.csv`](ledger/submissions.csv) | 제출 원장 (UTC, ID, SHA, 은퇴시킨 것, 관측 점수) | 제출 기록이 여러 문서에 갈라졌다 |
| [`ledger/calibration.csv`](ledger/calibration.csv) | 같은 쌍의 로컬 지표와 실전 점수 | 계약에 있던 "삼중쌍 표"가 끝내 만들어지지 않았다 |
| [`exp/EXP-000-example/`](exp/EXP-000-example/) | 사전등록 카드와 결과 양식. 실험 하나 = 폴더 하나 | |
| [`templates/submission_policy.md`](templates/submission_policy.md) | 판정과 분리한 제출 정책 | 판정을 넘어선 제출 6건 이상이 그때그때 결정됐다 |
| [`templates/brief.md`](templates/brief.md) | 지시서 한 장 | 조율 문서가 실험 수의 7배였다 |
| [`facts/`](facts/) | 확인한 사실, 접은 방향(재검토 조건·만료일 포함), 공식 규정 요약 | |
| [`tools/check.py`](tools/check.py) | 원장 검사, 평가기 검증 게이트 | |

## 시작하기

```bash
# 1. 이 폴더를 새 저장소로 복사한 뒤, 그 저장소 루트에서
python3 -m unittest discover -s tests      # 도구 테스트
python3 tools/check.py ledger              # 원장 형식·ID 검사

# 2. 대회 첫 이틀
#    - facts/OFFICIAL.md 를 원문으로 채운다 (최종 평가 방식, 슬롯, 재제출 규칙)
#    - templates/submission_policy.md 를 채워 facts/SUBMISSION_POLICY.md 로 고정한다
#    - 공개 최강 노트북을 그대로 첫 제출로 낸다 (기준선)
#    - STATE.md 의 슬롯·예산·인수자를 채운다

# 3. 로컬 지표로 후보를 고르기 전에
#    ledger/calibration.csv 에 실전 결과를 아는 쌍을 3개 이상 넣고
python3 tools/check.py calibration --threshold 0.7
#    "탐색 금지"가 나오면 그 지표로 미세 탐색을 하지 않는다
```

`ledger/experiments.csv` 의 `EXP-000` 행과 `exp/EXP-000-example/` 은 양식 예시다. 첫 실험을 만들 때 복사해 쓰고, 예시 행은 지운다.

## 평가기 검증 게이트가 하는 일

`calibration.csv` 의 각 행은 두 봇 A·B 에 대해 "로컬 지표의 A−B 차이"와 "실전 점수"를 적는다.
`check.py calibration` 은 두 차이의 부호가 같은 쌍의 비율과 Wilson 95% 하한을 지표별로 출력한다.
Kaggriculture 에서는 같은 계보 안의 미세 변경이 로컬에서 80판 중 78승을 해도 실전에서 165.6점 낮았다. 이 검사는 그런 지표를 탐색에 쓰기 전에 걸러 내기 위한 것이다.

## 라이선스

Apache License 2.0 (저장소 루트의 [`LICENSE`](../LICENSE)).
