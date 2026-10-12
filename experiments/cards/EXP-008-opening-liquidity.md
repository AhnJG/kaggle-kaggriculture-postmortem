# EXP-008 — opening liquidity collision 제거 (step 1 schedule A -> B)

hypothesis_id: HYP-0030
test_id: TEST-0008

사전등록 2026-09-14 06:18 UTC (Claude, opus-5). **확인 실행 전 커밋.** 커밋 후 seeds·임계·factor 변경 금지.
출처 제안: `coordination/proposals/codex/EXP-008-opening-liquidity.md` (2026-09-12 17:53)
선행 BLOCK: `coordination/proposals/claude/EXP-008-REVIEW-BLOCKED.md` (B1~B4)
해소 근거: `coordination/reports/codex/20260914-1446-EXP008-INSTRUMENTATION.md`

정정 2026-09-14 06:35 UTC (Claude) — §C timing 서술 오류를 바로잡고 G5 적용 범위를 명시했다.
근거 `coordination/proposals/codex/EXP-008-PREREG-TIMING-CORRECTION.md`.
**숫자 gate·`one_change`·`seeds`·`seats` 는 정정에서도 바뀌지 않았다.**

BLOCK 해제 상태 — B1 계측 구현 완료 · B2 step 추출기 구현 완료 · B3 본 카드 §A 에서 확정 · B4 본 카드 §B 에서 확정.

```yaml
id:            EXP-008   # hypothesis_id / test_id 는 상단 header 에만 둔다 (validator 중복 방지)
parent:        coordination/proposals/claude/exp006/submission.tar.gz
               # sha256 1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721
candidate:     experiments/candidates/exp008_opening_liquidity/main.py  # 구현 전, SHA N/A (사전조건 3에서 freeze)
one_change:    step 1 opening market schedule 전체를 indivisible factor A -> B로 교체
               A = [[BUY_PRODUCT,WHEAT,13],[SELL,WHEAT,13],[BUY_PRODUCT,WHEAT,13]]
               B = [[BUY_PRODUCT,WHEAT,13],[BUY_PRODUCT,WHEAT,30],[SELL,WHEAT,30]]
fixed:         [step 1 farmer/hands, step 2..718 전체 parent action·router·clone-preempt,
                actions.json·yh_base.py, engine 1.32.7, MAX_ORDERS=10]
hypothesis:    episode 108076177 postmortem에서 A가 B와 충돌해 day0 cash 0 -> step25 HIRE 3건 실패를 만들었다.
               B는 opening WHEAT stock 13을 보존하면서 collision을 없애 target transcript의 초기 생산력 붕괴를 막는다.
opponents:     target = private_artifacts/tapes/Remielle_episode-108076177-actions.json
               control = private_artifacts/tapes/today_episode-108079022-actions.json
               public = EXP-006의 public 4봇 exact SHA 4개
               pool = private_artifacts/tapes/*-replay.json 47개 (glob 고정, §B)
                      pool hash 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1
seeds:         target [1125321547] / control [1989066512]
               public [5101..5105] / pool [5101,5102,5103]
seats:         both
metric:        G1 target 2셀 W/D/L과 step23 bank·step25 hands·step47 nonempty_tiles (§C 측정 시점 정의)
               G2 control 2셀 W/D/L
               G3 public 40셀과 pool 282셀 candidate-only loss c
               G4 hire_failed·buy_failed·seed_blocked_plant·shed_discarded·orders_truncated 의
                  셀별 non-regression (§A) 과 status
               G5 candidate action parity: 326셀 각각에서 step 1 market 외 parent와 byte-identical
success:       G1 L=0 AND 두 셀 모두 step23 bank>=4 AND step25 hands>=3 AND step47 nonempty_tiles>=25
               AND G2 L=0 AND G3 c=0 AND public L=0
               AND G4 모든 326셀에서 다섯 counter 각각 candidate <= parent(같은 셀) AND status!=DONE=0
               AND G5 모든 326셀에서 차이 step 집합={1}, farmer/hands 차이=0
failure:       G1 L>=1 OR target 두 셀 중 하나라도 bank<4·hands<3·nonempty_tiles<25
               OR G2 L>=1 OR G3 c>=1 OR public L>=1 OR G4·G5 중 하나라도 위반
inconclusive:  G1 L=0이나 G2~G5가 모두 통과하지 않은 나머지 경우; seeds 추가 금지
next_if_success: local mechanism support로만 기록; 사람 승인 전 제출 금지. wider hosted test는 별도 card.
next_if_failure: exact B schedule 폐기; cash-floor나 order-only로 결과 보고 쪼개기 금지. 새 postmortem 가설 필요.
artifact:      postmortem experiments/results/hosted_postmortem_108076177.json
               baselines experiments/results/hosted_postmortem_108076177_baseline_both_seats.jsonl,
               experiments/results/hosted_postmortem_108079022_control_baseline_both_seats.jsonl
               결과 원자료 evidence/raw/EXP-008/
계측:          tools/instrument.py    6c0b36af31692ef6676728a916ba9b1100db3b02fee0e43a7ab09f73dc12fedd
               tools/verify_pool.py   a7e22af1a68051119d50f3c71da5217fc390ed7830abdabbb5f489c28297764d
               tools/compare_action_streams.py e505f1a2dc6af1449e5f4618642dc2a7d602255ff1faebd473b2d7e6c01593df
               tests/test_instrument_exp008.py cccb99ed863bbc4faf00e832d0ff3cf1b9b530ee8fb18ccce01fe19553c73e0e
```

---

## §A. G4 확정 — 셀별 non-regression (`candidate <= parent`)

**규칙.** 다섯 silent-failure counter `hire_failed`, `buy_failed`, `seed_blocked_plant`,
`shed_discarded`, `orders_truncated` 는 **각 `(opponent, seed, candidate seat)` 셀에서
`candidate <= parent`** 를 만족해야 한다. 절대 0 요구가 아니고, 전체 합산 비교도 아니다.
`status != DONE = 0` 은 절대 기준 그대로 유지한다. 셀 총수 326 = target 2 + control 2 + public 40 + pool 282.

**판정 절차 (순서 고정).**
1. parent 를 326셀 전부 `tools/instrument.py` 로 돌려 셀별 counter 를 `evidence/raw/EXP-008/parent_counters.jsonl` 에 기록한다.
2. 이 parent baseline 파일의 SHA-256 을 보고서에 적어 **freeze** 한다.
3. 그 뒤에 candidate 를 같은 326셀로 돌린다.
4. 셀 키 `(opponent, seed, candidate seat)` 로 join 해 counter 다섯 개를 각각 비교한다.
   parent 에 키가 없으면 그 counter 의 parent 값은 `0` 으로 읽는다.
   parent baseline 측정 전에 candidate 결과를 열람하면 이 카드는 무효다.

**왜 절대 0 이 아닌가 (결과 보기 전 확정, 완화 아님).**
- 제안서 원문은 `hire_failed`·`buy_failed`·`seed_blocked_plant` 를 **절대 0** 으로,
  `discard`·`orders_truncated` 를 **증가 0** 으로 썼다. 두 기준이 섞여 있었다.
- `[LOCAL]` 측정: target 셀의 **parent** 가 이미
  `hire_failed=9`, `buy_failed=34`, `seed_blocked_plant=16`, `shed_discarded=209` 다.
  (`coordination/reports/codex/20260914-1446-EXP008-INSTRUMENTATION.md`;
  `..._108076177_baseline_both_seats.jsonl` 의 `buy_failed=34`·`discard_units=209` 와 일치)
- 따라서 절대 0 은 candidate 성능과 무관하게 **구조적으로 도달 불가**였다. 그 기준을 두면
  G1~G3 결과와 상관없이 G4 가 FAILURE 를 확정하고, `next_if_failure` 가 "exact B schedule 폐기"를
  명령하므로 **가설이 측정되지 않은 채 죽는다.** 이는 가설 검정이 아니라 설계 결함이다.
- 가설의 핵심 주장인 opening HIRE 회복은 **G1 의 `step25 hands>=3` 이 직접 판정**한다.
  G4 는 "candidate 가 다른 시점의 기존 실패를 악화시키지 않는다"는 **safety gate** 역할만 맡는다.
- 이 재정의는 G4 한 항목에만 적용한다. **G1·G2·G3·G5 의 숫자는 한 자리도 바꾸지 않았다.**

**정직한 기록.** `candidate <= parent` 는 세 counter 에 대해 원문 절대 0 보다 **약한** 기준이다.
약하게 만든 이유는 위의 `[LOCAL]` 측정값 하나뿐이며, candidate 결과를 본 뒤가 아니라 **구현 전**에 고정했다.
G4 통과는 "silent failure 가 없다"가 아니라 "silent failure 가 늘지 않았다"로만 보고해야 한다.

**참고 baseline (판정용 아님 — 판정은 위 절차 1~4 의 재측정값으로 한다).**

| 셀 | hire_failed | buy_failed | seed_blocked_plant | shed_discarded |
|---|---|---|---|---|
| target Remielle_108076177 · seed 1125321547 · parent | 9 | 34 | 16 | 209 |
| control today_108079022 · seed 1989066512 · parent | 미측정 | 0 (`buy_failed` 키 부재) | 미측정 | 7 |

control 행의 `sellaudit` 수치는 counter 정의가 다른 하니스에서 나온 값이므로 **참고만** 한다.
판정은 반드시 `tools/instrument.py` 재측정값으로 한다.

## §B. pool 고정 (B4 해소)

- pool 은 `private_artifacts/tapes/*-replay.json` **47개**로 고정한다.
  `private_artifacts/tapes/*.json` 은 현재 **49개**이고, 추가된 두 개가 바로 본 실험의
  target `Remielle_episode-108076177-actions.json` 과 control `today_episode-108079022-actions.json` 이다.
  `*.json` glob 을 쓰면 target/control 이 pool 에 섞여 G1·G3 가 독립이 아니게 된다.
- **실행 전 필수 단계** (실패하면 실행 금지):

```bash
python3 tools/verify_pool.py --glob 'private_artifacts/tapes/*-replay.json' \
  --expected-count 47 \
  --expected-sha256 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1
```

- pool hash 정의: `sha256(concat(sort(각 파일 sha256 hex)))`.
  2026-09-14 06:18 UTC 재검증 결과 `PASS, count=47` — exact SHA 일치.

## §C. G1·G5 측정 시점 확정 (B2·반송 7 해소 / 2026-09-14 06:35 UTC 정정)

**엔진의 transition 규약.** `env.steps[i]` 한 칸은 **transition i** 하나를 담는다.

- `env.steps[i].action` 은 **observation step `i-1`** 을 보고 agent 가 만든 action 이다.
- `env.steps[i].observation` 은 **그 action 을 interpreter 가 처리한 뒤의 상태**다.
- `env.steps[i].observation.step == i` 다 (`kaggle_environments/core.py:626`
  `new_state[0].observation.step = len(self.steps)`).

따라서 **action stream label `i` 와 `env.steps` observation index `i` 는 같은 transition 을 가리킨다.**
`tools/instrument.py` 의 action stream 라벨은 `obs["step"] + 1` 인데, agent 가 본 observation 이 index `i-1`
(`obs["step"] == i-1`) 이므로 라벨이 `i` 가 되어 `env.steps[i].action` 과 정확히 일치한다.
720 step 에서 agent action 은 719개, 라벨 범위는 1..719 다.

**G1 과 G5 가 읽는 것.**

| gate | 읽는 대상 | 필드 |
|---|---|---|
| G1 | transition `i` 의 **결과 상태** | `env.steps[i].observation` |
| G5 | transition `i` 에 **적용된 action** | `env.steps[i].action` |

즉 G1 의 `step25 hands>=3` 은 **index 25 의 `HIRE x3` 이 실행된 뒤의 hands 수**를 확인하는 gate다.
"action 반영 전"으로 읽으면 합격 숫자의 의미가 뒤집힌다.

**G1 정의.** step 23 / 25 / 47 은 `env.steps[index]` 에 저장된 observation 기준이다.
hosted `tools/postmortem_hosted.py:step_snapshot` 의 `replay["steps"][i]` 규약과 같다.

- `index` 는 **0-based transition index** 다. `--focus-steps` 로 지정한 값을 그대로 쓴다. 재해석 금지.
- 읽는 필드: `players[candidate seat]` 의 `bank`(= `farm["money"]`), `hands`(= `len(farm["hands"])`),
  `nonempty_tiles`(= `tiles` 중 `dict` 인 칸 수). 추출기는 `tools/instrument.py:local_step_snapshot`.
- 실행:

```bash
python3 tools/instrument.py --a tape:<opponent> --b <agent> --seeds <seed> \
  --focus-steps 23 25 47 --include-actions --json evidence/raw/EXP-008/<cell>.json
```

- 판정 필드: `focus_steps[*].players[seat].{bank,hands,nonempty_tiles}`.

**G5 정의와 적용 범위.** G5 는 **326셀 각각**에서 판정한다 (G4 와 같은 셀 집합:
target 2 + control 2 + public 40 + pool 282). `fixed: step 2..718 전체 parent action` 을 실제로 검증하려면
일부 셀 표본으로는 부족하다. 다른 범위를 쓰려면 candidate 결과를 보기 전에 exact cell 목록을 카드에 써야 한다.

```bash
python3 tools/compare_action_streams.py --left <parent.json> --right <candidate.json> \
  --left-player <seat> --right-player <seat>
# 판정(셀마다): different_steps == [1] AND farmer_or_hands_different_steps == []
```

`one_change` 의 opening market schedule 은 observation step 0 에서 계산되어 `env.steps[1]` 에 적용되므로
라벨 **1** 이다. G5 허용 차이 집합 `{1}` 은 그대로 유효하다.

**`[ENGINE+LOCAL]` 재현 (2026-09-14 06:35 UTC, engine 1.32.7, Claude 독립 실행).**

```text
episodeSteps=3, seed=7, agent0 = step0 에서만 market [["HIRE"]]
index 0 | obs.step 0 | action PASS      | money 3000.0 | hands 0
index 1 | obs.step 1 | action HIRE      | money 2999.0 | hands 1
index 2 | obs.step 2 | action PASS      | money 2999.0 | hands 1
```

index 1 에 `action=HIRE` 와 그 결과인 `money=2999`·`hands=1` 이 **함께** 저장된다.

정정 근거: `coordination/proposals/codex/EXP-008-PREREG-TIMING-CORRECTION.md`.
정정 전 §C 는 "같은 index 의 action 은 아직 반영되지 않은 값" 이라고 썼고 이는 **틀렸다.**
숫자 index `23/25/47`, G1 임계, G5 허용 차이 `{1}` 은 바뀌지 않았다.

## 사전조건

1. **완료** — Claude 가 factor 와 숫자 gate 를 검토하고 본 카드로 수락했다. G4 는 §A, 측정 시점은 §C 로 확정.
2. **완료** — `hire_failed`, `buy_failed`, `seed_blocked_plant` 가 engine attribution 기준으로 계측된다.
   - `hire_failed`: `kaggriculture.py:_do_hire` wrapper, 호출 전후 `len(farm["hands"])` 비교
     (`tools/instrument.py:459`). 자금 부족으로 인한 무음 실패만 센다.
     MAX_ORDERS 절삭으로 `_do_hire` 에 도달하지 못한 HIRE 는 `orders_truncated` 가 잡는다.
   - `seed_blocked_plant`: agent action 반환 직후 engine `interpreter`(`kaggriculture.py:920-928`)와
     **동일한 crop 별 atomic 조건**을 재현 (`tools/instrument.py:200-215`).
     crop 별 내역은 `seed_blocked_by_crop`.
   - `buy_failed`: `_commit_unit` 반환 False (`tools/instrument.py` 의 `commit` wrapper, BUY_*/SELL 경로 전용).
   - 2026-09-14 06:18 UTC 독립 확인: `seed_blocked_plants` / `local_step_snapshot` 를 합성 입력으로 직접 호출해
     engine 조건과 일치함을 확인했다.
3. **미완** — candidate 를 구현한 뒤 card·parent·candidate·harness SHA 를 freeze 한다.
   본 카드의 SHA-256 은 커밋 직후 `coordination/reports/claude/` 보고서에 기록한다.

## 근거와 한계

- `[HOSTED]` target 에서 B 는 A 보다 step1 cash 가 52 높았고, step25 HIRE 3건 성공/실패가 갈렸다.
- `[ENGINE+LOCAL]` B-vs-B 는 cash·WHEAT stock·market inventory endpoint 가 양쪽 동일했다.
- `[INFERENCE]` B 가 target 의 전체 패배를 고친다는 주장은 아직 미검증이다.
- 이 카드는 opening schedule block 만 판정한다. B 의 order 와 batch size 를 각각 효과 원인으로 주장하지 않는다.
- frozen public replay transcript 는 causal diagnostic 일 뿐 `[HOSTED]` 성능이 아니다.
- **실효 표본 한계**: G1 은 단일 시드 2셀이고 tape 는 결정론적이므로 좌석 교대가 독립 정보를 거의 주지 않는다.
  실효 표본은 사실상 1. `next_if_success` 를 "local mechanism support 로만 기록, 사람 승인 전 제출 금지" 로
  못박은 것은 이 한계와 정합한다. **성능 주장으로 승격 금지.**
- **G5 미시험**: `tools/compare_action_streams.py` 는 self-compare smoke test 만 거쳤다.
  parent-vs-candidate parity 는 candidate 구현 후 최초 판정이다.

## 변경 이력 (제안서 대비)

| 항목 | 제안서 | 본 카드 | 성격 |
|---|---|---|---|
| G4 counter 기준 | 3개 절대 0 + 2개 증가 0 | 5개 모두 셀별 `candidate <= parent` | **재정의** (§A, 결과 전 확정) |
| G1 측정 시점 | 미정의 | `env.steps[index]` observation = 해당 action 처리 **후** 상태 | 명시화 (§C) |
| G5 적용 범위 | 미정의 | 326셀 각각 | 명시화 (§C) |
| pool glob | `private_artifacts/tapes` 47개 | `*-replay.json` 47개 + 실행 전 hash 검증 | 모집단 고정 (§B) |
| G1/G2/G3/G5 임계 | — | **변경 없음** | — |
| one_change / fixed / seeds / seats | — | **변경 없음** | — |

## 결과

미실행. candidate 미구현. 결과 기록 전까지 이 절을 채우지 않는다.
