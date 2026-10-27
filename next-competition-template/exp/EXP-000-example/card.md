# EXP-NNN — <한 줄 제목>

실행 **전에** 모든 칸을 채운다. 숫자가 아닌 기준이 하나라도 있으면 실행자는 `BLOCKED`로 돌려보낸다(AGENTS §5).

```yaml
id:              EXP-NNN            # ledger/experiments.csv 에 먼저 행을 추가해 발급
designer:        <에이전트/사람>
created_utc:     YYYY-MM-DDTHH:MMZ
parent:          releases/<label>/main.py   # + SHA-256
parent_sha256:
one_change:      <무엇을> <전 값> -> <후 값>
fixed:           [ 이번에 건드리지 않는 것 ]
hypothesis:      <왜 나아질 거라 보는가. 근거 1건: 진 경기 분석, 엔진 사실, 이전 실험>
evidence_level:  ENGINE | HOSTED | LOCAL | COMMUNITY | INFERENCE
opponents:       [ <경로> + SHA-256, ... ]   # 실전 상위권과 같은 유형이 들어 있는가?
seeds:           [ ... ]                     # 리스트로 고정. 실행 후 추가 금지
seats:           both
n_games:
metric:          <승격 지표>                 # 평가기 검증 게이트(AGENTS §7)를 통과한 지표인가?
success:         <숫자 임계>
failure:         <숫자 임계>
inconclusive:    <숫자 임계>
holdout:         <확인용 집합. 탐색에 쓰지 않은 것>
validity_counters: [ action_count, agent_errors, seat_match ]
stop_condition:  <언제 멈추나>
next_if_success:
next_if_failure:
```

## 제출과의 관계

이 카드의 판정은 제출 결정이 아니다. 제출 여부는 `facts/SUBMISSION_POLICY.md`로 정한다(AGENTS §8).
