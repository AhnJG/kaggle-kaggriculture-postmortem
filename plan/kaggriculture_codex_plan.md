# Kaggriculture Codex Plan

작성일: 2026-09-03

대상 대회: [Kaggriculture](https://www.kaggle.com/competitions/kaggriculture)

## 1. 대회 목표 분석

Kaggriculture는 2인 대전형 Kaggle Game AI 대회다. 에이전트는 30일 동안 매일 24턴, 총 720턴을 진행하며 농산물 생산, 이동, 판매, 보관, 현금화를 결정한다. 최종 평가는 마지막 은행 잔고를 기준으로 승패가 정해지고, 리더보드는 단순 평균 점수가 아니라 승/패/무 결과를 Bradley-Terry 계열 방식으로 반영한다.

따라서 최적화 목표는 `평균 코인 최대화`가 아니라 `상대 분포를 상대로 이길 확률 최대화`다. 큰 점수 차로 이기는 전략보다, 다양한 상대에게 안정적으로 승을 쌓고 치명적인 패배를 줄이는 전략이 더 중요하다.

핵심 제약:

- 게임 길이: 30일 x 24턴 = 720턴
- 평가 기준: 최종 은행 잔고 기반 승/패/무
- 제출 제한: 하루 최대 5회
- 활성 슬롯: 최신 제출 2개가 평가 대상
- 런타임 제약: 액션당 1초, 메모리 100MiB, 네트워크 및 런타임 LLM 사용 불가
- 마감: 2026-09-23, 최종 마감 2026-09-30 23:59 UTC

실전 결론은 명확하다. 런타임에서 거대한 탐색이나 LLM 추론을 돌리는 전략보다, 사전에 충분히 실험한 결정론적 정책과 가벼운 상태 추적, 상대 대응 규칙, 종료 시점 현금화 로직이 더 현실적이다.

## 2. 우승을 위한 기본 전략

초기에는 RL보다 계층형 결정론 정책을 먼저 만든다. 이유는 대회 시간이 짧고, 평가가 상대 기반이며, 제출 슬롯이 제한되어 있기 때문이다. 먼저 강한 규칙 기반 에이전트를 만들고, 이후 필요한 부분만 통계적 튜닝이나 간단한 탐색으로 보강한다.

권장 정책 구조:

- 상태 추적: 재고, 현금, 날짜, 남은 턴, 시장 가격, 상대 행동 패턴을 매턴 업데이트한다.
- 생산 계획: 남은 기간과 가격 흐름을 고려해 어떤 작물을 생산할지 결정한다.
- 이동/라우팅: 생산지, 창고, 시장 사이의 이동 비용과 시간을 최소화한다.
- 시장 타이밍: 즉시 판매, 보관, 지연 판매의 기대값을 비교한다.
- 상대 모델링: 상대가 특정 자원을 과점하거나 가격을 흔드는지 탐지한다.
- 안전장치: 시간 초과, 잘못된 액션, 재고 음수, 막판 미판매 재고를 방지한다.
- 종료 현금화: 마지막 구간에서는 미래 기대값보다 확정 은행 잔고를 우선한다.

최종 제출은 서로 다른 성격의 2개 정책으로 구성한다.

- 1번 슬롯: 대부분의 상대에게 안정적으로 강한 범용 정책
- 2번 슬롯: 특정 메타나 취약한 상대군을 노리는 독립 정책

두 정책이 거의 같은 로직이면 슬롯을 낭비한다. 반드시 서로 다른 실패면과 승리 조건을 가져야 한다.

## 3. 실험 설계

대회용 실험은 로컬 점수, 내부 아레나 점수, Kaggle hosted score를 분리해서 기록해야 한다. 로컬에서 좋아 보이는 전략이 hosted leaderboard에서 반드시 강하다는 보장은 없다.

필수 실험 원칙:

- 같은 seed, 양쪽 seat를 모두 바꾸는 paired match를 사용한다.
- 단일 상대가 아니라 opponent zoo를 만든다.
- 평균 최종 잔고뿐 아니라 승률, 무승부율, 큰 패배 빈도, 시간 초과율을 함께 본다.
- 실험마다 코드 SHA, 설정 파일, 상대 목록, seed 목록, 결과 CSV를 남긴다.
- 최종 후보는 별도 blind seed set에서 재검증한다.
- 제출 전에는 `py_compile`, import smoke test, 제한 시간 테스트, 패키징 해시를 확인한다.

추천 opponent zoo:

- baseline random
- 단순 greedy 판매형
- 생산 극대화형
- 보관 후 판매형
- 빠른 현금화형
- 시장 특정 자원 집중형
- 이전 제출물 스냅샷
- 외부 공개 notebook 또는 discussion 기반 재현 상대

## 4. 하나의 작업 폴더 운영

모든 agent는 하나의 작업 폴더만 사용한다.

작업 폴더:

```text
~/kaggle/Kaggriculture
```

권장 폴더 구조:

```text
Kaggriculture/
  AGENTS.md
  CLAUDE.md
  GEMINI.md
  README.md
  main.py
  bot/
    policy.py
    state.py
    actions.py
    opponent_model.py
    terminal.py
  tests/
    test_rules.py
    test_policy_smoke.py
    test_terminal_liquidation.py
  tools/
    run_match.py
    run_arena.py
    summarize_results.py
    package_submission.py
    registry_check.py
  configs/
    arena.yaml
    candidate_default.yaml
    blind_seeds.yaml
  opponents/
    random_bot.py
    greedy_bot.py
    cashout_bot.py
    archive/
  experiments/
    README.md
    runs/
  releases/
    README.md
  artifacts/
    local/
    kaggle/
  coordination/
    TASKS.md
    DECISIONS.md
    EXPERIMENT_LEDGER.md
    SUBMISSION_REGISTRY.md
    HANDOFF_CURRENT.md
```

데이터 흐름:

```text
main.py
  -> bot/state.py에서 게임 상태 해석
  -> bot/policy.py에서 의사결정
  -> bot/actions.py에서 유효 액션 생성
  -> tools/run_arena.py에서 대량 평가
  -> experiments/runs/에 결과 저장
  -> coordination/EXPERIMENT_LEDGER.md에 요약
  -> releases/에 제출 후보 고정
```

`main.py`는 Kaggle 제출 진입점이므로 가능한 얇게 유지한다. 실제 로직은 `bot/` 아래에 두고, 실험과 제출 패키징은 `tools/`가 담당한다.

## 5. Agent 역할 분담

사용 가능 agent:

- Gemini Pro
- Codex Plus
- Claude Pro

역할은 겹치지 않게 나누고, 최종 런타임 코드는 Codex Plus가 단일 통합 권한을 갖는 편이 좋다. 여러 agent가 동시에 같은 파일을 수정하면 추적이 어려워지고 회귀가 늘어난다.

권장 역할:

- Gemini Pro: 대회 규칙, 공개 discussion, notebook, game mechanics, 수학적 전략, opponent 아이디어 조사
- Codex Plus: 저장소 구조, 런타임 코드, 테스트, 아레나, 패키징, 제출 후보 고정
- Claude Pro: 독립 리뷰, 전략 허점 검토, 실험 설계 검증, 문서 품질 검토

작업 소통 규칙:

- Git이나 파일이 source of truth다.
- Buzz는 알림 버스 또는 handoff 알림으로만 사용한다.
- 중요한 상태는 반드시 `coordination/` 아래 파일에 남긴다.
- agent 간 메시지는 짧고 검증 가능한 형식으로 보낸다.

Buzz 또는 메시지 예시:

```text
[KAGRI-014] policy terminal cashout review requested
BASE_SHA: abc1234
OWNED_PATHS: bot/terminal.py, tests/test_terminal_liquidation.py
EVIDENCE: pytest tests/test_terminal_liquidation.py passed
RISK: may over-liquidate on day 29 if market spread is high
REQUEST: Claude Pro review only, no edits
NEXT: Codex integrates if accepted
```

핵심은 "누가 무엇을 바꿨는지"보다 "어떤 증거로 다음 결정을 내릴 수 있는지"다.

## 6. 프로젝트 지침 작성안

루트 `AGENTS.md`에는 모든 agent가 따라야 할 공통 원칙을 둔다. `CLAUDE.md`, `GEMINI.md`는 같은 지침을 참조하되 각자 역할만 덧붙이는 얇은 wrapper로 둔다.

권장 `AGENTS.md` 초안:

```markdown
# Kaggriculture Agent Instructions

## Objective

Optimize win probability on Kaggle Kaggriculture, not average final cash alone.

## Source Of Truth

- Use this repository as the only working folder.
- Record durable state in `coordination/`.
- Do not treat local arena results as Kaggle leaderboard proof.
- Separate local, hosted, and manual-review evidence.

## Runtime Constraints

- Submission entrypoint is `main.py`.
- No network calls at runtime.
- No runtime LLM calls.
- Keep per-action latency below the official limit with margin.
- Keep memory usage within the official limit.

## Editing Rules

- Codex Plus owns runtime implementation and packaging.
- Gemini Pro owns research notes unless explicitly assigned otherwise.
- Claude Pro owns review notes unless explicitly assigned otherwise.
- Do not edit files outside your assigned paths.
- Before editing, write task id, owned paths, and expected output in `coordination/TASKS.md`.

## Experiment Rules

- Every experiment must record config, code SHA, opponent set, seed set, metric, result path, and interpretation.
- Use paired same-seed, both-seat matches when comparing candidates.
- Report win rate, draw rate, average final bank, large-loss rate, invalid-action rate, timeout rate.
- No candidate can be promoted from one favorable seed or one favorable opponent.

## Submission Rules

- Run compile, smoke, arena, and packaging checks before release.
- Store frozen candidates in `releases/`.
- Record SHA-256 and purpose in `coordination/SUBMISSION_REGISTRY.md`.
- Final two active submissions must be strategically distinct.

## Handoff Format

Use:

- Task id
- Base SHA
- Owned paths
- What changed
- Exact commands run
- Result
- Risk
- Next action
```

권장 `CLAUDE.md`:

```markdown
# Claude Pro Instructions

Follow `AGENTS.md`.

Primary role: independent review. Prefer findings with file paths, exact failure mode, and suggested verification. Do not modify runtime files unless explicitly assigned.
```

권장 `GEMINI.md`:

```markdown
# Gemini Pro Instructions

Follow `AGENTS.md`.

Primary role: research and strategy. Cite official rules, public discussions, notebooks, and reproducible observations. Do not present unverified claims as hosted-score evidence.
```

## 7. 대회 기간 운영 일정

초기 구간:

- 공식 환경을 로컬에서 재현한다.
- baseline bot과 opponent zoo를 만든다.
- deterministic policy v1을 빠르게 완성한다.
- invalid action과 timeout을 0에 가깝게 만든다.

중간 구간:

- 생산, 판매, 보관, 라우팅 정책을 독립적으로 실험한다.
- 각 개선은 단일 changed factor로 비교한다.
- 약한 상대에게만 이기는 전략과 강한 상대에게도 버티는 전략을 구분한다.
- hosted score가 있는 후보와 로컬 후보를 별도 관리한다.

마감 전 구간:

- 최종 후보 3~5개를 freezing한다.
- blind seed set으로 재검증한다.
- 최종 2개 active submission을 일찍 고정한다.
- 마감 직전에는 큰 로직 변경을 금지한다.

## 8. 대회 기간 동안 명심할 핵심 세 가지

1. 평균 점수가 아니라 승률을 최적화한다.

   리더보드는 상대전 승패 기반이다. 더 많은 코인을 버는 전략보다 더 자주 이기는 전략이 우선이다.

2. 단일 seed, 단일 상대, 단일 leaderboard 변화는 증거가 아니다.

   Kaggle game competition은 노이즈와 상대 분포 영향이 크다. 같은 seed 양쪽 seat, 여러 상대, blind set, hosted score를 분리해서 봐야 한다.

3. 새 아이디어보다 재현성, 안정성, 활성 슬롯 관리가 중요하다.

   마지막에 invalid action, timeout, 잘못된 패키징, 거의 중복된 두 제출로 무너지는 경우가 많다. 우승권에서는 작은 안정성 차이가 전략 아이디어보다 더 크게 작용한다.

## 9. 참고 자료

- Kaggle competition overview: <https://www.kaggle.com/competitions/kaggriculture/overview>
- Kaggle competition rules: <https://www.kaggle.com/competitions/kaggriculture/rules>
- Kaggle Environments Kaggriculture README: <https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/README.md>
- Kaggle Environments Kaggriculture source: <https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.py>
- Kaggle discussion on active submissions: <https://www.kaggle.com/competitions/kaggriculture/discussion/735311>
- Kaggle Environments package: <https://pypi.org/project/kaggle-environments/>
- Bradley-Terry-style ranking background: <https://pubsonline.informs.org/doi/10.1287/opre.39.4.583>
- AlphaStar / league-style agent training background: <https://arxiv.org/abs/1711.00832>

## 10. 바로 다음 행동

1. 위 폴더 구조를 만든 뒤 `AGENTS.md`, `coordination/TASKS.md`, `coordination/EXPERIMENT_LEDGER.md`, `coordination/SUBMISSION_REGISTRY.md`를 먼저 채운다.
2. Kaggle 환경을 로컬에서 실행해 baseline random, greedy, cashout 상대를 만들고 첫 paired arena를 돌린다.
