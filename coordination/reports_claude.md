# coordination/reports/claude — 39개 문서 묶음

원본 파일을 파일명(시간) 순으로 이어 붙였다. 각 절 제목이 원래 경로다.


---

## `reports/claude/20260907-0555-EXP001-stale-artifact.md`

# ⛔ EXP-001 stage 2·3 결과 무효 — stale artifact 오염

- 작성일시: 2026-09-07 05:55 UTC
- 작성자: Cowork (Claude)
- 심각도: **P0 — 잘못된 파라미터가 승격될 뻔했다**

## 1. 사실

`experiments/candidates/v1_*.py` 는 전부 `main.py` sha256
`b0c32e1a181e9308c05046b10d618258397c4088e21025ba78346aaa9ac25ddf` 를 assert 한다.
그런데 파일 mtime 은 다음과 같다.

| 대상 | mtime (UTC) |
|---|---|
| `results/v1_timing_*.json` (초판) | 05:34 |
| `results/v1_workers_*.json` | 05:37 |
| `results/v1_carrots_*.json` | 05:40 |
| **`main.py` (현재 sha)** | **05:44:05** |
| `candidates/v1_*.py` (현재 wrapper) | 05:44:42 |
| `results/v1_timing_*_rerun.json` | 05:51 |

→ **stage 1·2·3 의 초판 결과는 전부 현재 `main.py` 가 존재하기 전에 생성되었다.**
   timing 만 05:51 에 재실행되어 초판과 수치가 완전히 일치했다(재현 OK).
   **workers 와 carrots 는 재실행되지 않았다.**

## 2. 재현 — carrots 결과는 현재 코드에서 재현되지 않는다

저장된 `v1_carrots_5_vs_15.json`: `paired_score 0.5, W/D/L 0/40/0, mean_margin 0.0`
(= 두 후보가 완전히 동일하게 동작했다는 뜻)

현재 코드로 재실행(`tools/arena.py --seeds 2`):

```
페어드 점수 0.0000  W/D/L 0/0/4  마진 평균 -3,972  에러 0
판정: A(carrots=5) 열세
```

단일 게임 직접 확인(seed=1000, 파일 로드 방식):

```
v1_carrots_5.py vs v1_carrots_15.py -> [21312, 25377]     # 15가 +4,065
v1_carrots_5.py  vs random          -> 23319
v1_carrots_15.py vs random          -> 25985
```

파라미터가 실제로 먹는지도 직접 확인:

```
CARROT_TILES=5  -> carrot 5,  wheat 70
CARROT_TILES=8  -> carrot 8,  wheat 67
CARROT_TILES=15 -> carrot 15, wheat 60
```

**결론: 저장된 carrots 결과 3건은 파라미터가 no-op 이던 시점의 산출물이다.**

## 3. 왜 위험한가

EXP-001 사전등록 tie-break 는 전부 동점일 때 `(4) 비용이 낮은 쪽(fewer carrots)` 을 고르게 되어 있다.
저장된 결과를 그대로 채택하면 **carrots=5 가 선택**되는데,
실측은 **carrots=15 가 약 4,000 코인 우위**다. 사전등록 규칙이 정확히 반대 방향으로 작동한다.

## 4. 요구 조치 (Codex)

1. `results/v1_workers_*.json` 3건과 `results/v1_carrots_*.json` 3건을
   `results/_invalid/` 로 이동하거나 파일명에 `_STALE` 를 붙여 무효화한다.
2. 현재 `main.py` (sha `b0c32e…5ddf`) 로 **stage 2 (workers 9/10/12) 재실행**.
   stage 1 선택값(prior = NE day6, SW day10)은 재현되었으므로 그대로 사용한다.
3. stage 2 선택 후 **stage 3 (carrots 5/8/15) 재실행**.
4. 앞으로 모든 결과 JSON 에 `parent_sha256` 필드를 기록한다.
   wrapper 의 assert 만으로는 *결과가 언제 만들어졌는지* 를 막지 못한다.

## 5. 부수 관찰

- `main.py` 가 v1(토지 매입 포함)로 in-place 변경되었다. 제출된 v0 는
  `releases/v0/main.py` (sha `eb64b3c0…f85a`) 에 보존되어 있어 복구는 가능하지만,
  "`main.py` = 마지막 제출물" 불변식은 지금 깨져 있다. 승격 전까지는
  `main.py` 를 v1 작업본으로 본다는 사실을 `coordination/BOARD.md` 에 명시할 것.
- 저장소 인덱스에 `kaggle.json` 이 staged 되어 있었다. `git rm --cached` 로 제거했다.
  HEAD 에는 없다(과거 커밋 오염 없음). `.gitignore` 는 이미 3줄 모두 갖고 있다.


---

## `reports/claude/20260914-1521-EXP008-PREREGISTERED.md`

# EXP-008 사전등록 완료 — BLOCK 해제

> **정정 2026-09-14 06:35 UTC** — 아래 "G1 — 측정 시점" 절의 "같은 index 의 action 은 아직 반영 전" 및 "G1 과 G5 는 규약이 다르다" 는 **틀렸다.**
> `env.steps[i].observation` 은 같은 index 의 action 을 처리한 **뒤**의 상태이고, action label 과 observation index 는 같은 transition 이다.
> 정정본: `coordination/reports/claude/20260914-1536-EXP008-TIMING-CORRECTION.md`.

1. **무엇을 했는가:** EXP-008(첫날 시장 거래 순서 A→B) 실험을 정식 카드로 사전등록했다.
   막혀 있던 두 가지를 결과 보기 전에 확정했다 — (a) 안전 counter 다섯 개의 합격 기준,
   (b) "step 23/25/47" 이 정확히 어느 시점의 값인지.
2. **왜 했는가:** 원래 기준은 "실패 counter 가 0이어야 통과"였는데, **바꾸기 전 parent 가 이미
   실패 9·34·16건**이라 candidate 가 무엇을 하든 무조건 FAIL 이 나오는 구조였다. 그대로 두면
   가설이 측정도 되기 전에 죽는다. step 시점도 정의가 없어 같은 숫자를 두 가지로 읽을 수 있었다.
3. **측정과 결과:** pool 검증 `PASS, count=47`, exact SHA 일치.
   계측 함수 2개를 합성 입력으로 직접 호출해 engine 조건과 일치함을 확인했다.
   hypothesis ledger `PASS: 30 entries`. 카드 SHA-256
   `6a5adda98c1e6388d2729a24dba6ee97c2334bbf61296f8a80328cf2c640a4b1`.
4. **막힌 점과 다음 행동:** 막힌 점 없음. 다음은 Codex 가 candidate 를 구현하고 SHA 를 freeze 한 뒤,
   **parent 326셀 baseline 을 먼저 기록**하고 candidate 를 실행한다. 나는 구현·실행을 하지 않았다.

---

## 확정한 두 규칙

### G4 — 셀별 non-regression
다섯 counter `hire_failed`·`buy_failed`·`seed_blocked_plant`·`shed_discarded`·`orders_truncated` 는
각 `(opponent, seed, candidate seat)` 셀에서 **`candidate <= parent`**. `status != DONE = 0` 은 절대 기준 유지.
셀 총수 326 = target 2 + control 2 + public 40 + pool 282.

판정 순서 고정: parent 326셀 counter 를 `evidence/raw/EXP-008/parent_counters.jsonl` 에 먼저 기록 →
그 파일 SHA-256 freeze → candidate 실행 → 셀 키로 join 비교. parent 키 부재는 `0` 으로 읽는다.

`[LOCAL]` 근거: target 셀 parent 가 `hire_failed=9`, `buy_failed=34`, `seed_blocked_plant=16`,
`shed_discarded=209` (`coordination/reports/codex/20260914-1446-EXP008-INSTRUMENTATION.md`,
`experiments/results/hosted_postmortem_108076177_baseline_both_seats.jsonl` 의 `buy_failed=34`·`discard_units=209` 와 일치).
절대 0 은 구조적 도달 불가였다.

**정직한 기록:** 이 기준은 세 counter 에 대해 원문 절대 0 보다 **약하다.** 약하게 만든 근거는 위 측정값
하나뿐이고, candidate 구현 **전**에 고정했다. G4 통과는 "silent failure 가 없다"가 아니라
**"silent failure 가 늘지 않았다"** 로만 보고해야 한다. 가설의 핵심인 opening HIRE 회복은
G1 의 `step25 hands>=3` 이 직접 판정한다.

### G1 — 측정 시점
step 23/25/47 은 **`env.steps[index]` 에 저장된 observation** 기준. hosted `step_snapshot` 의
`replay["steps"][i]` 규약과 동일. index 는 0-based 이고, 같은 index 의 `action` 은 **아직 반영 전**이다.
추출기 `tools/instrument.py:local_step_snapshot`, 실행 `--focus-steps 23 25 47`,
판정 필드 `focus_steps[*].players[seat].{bank,hands,nonempty_tiles}`.

**혼동 금지:** G5 의 action stream 라벨은 `obs["step"] + 1` 이다(719개, 1..719).
`one_change` 의 opening market schedule 이 라벨 **1** 이므로 G5 허용 차이 집합 `{1}` 은 그대로 유효하다.
G1 의 observation index 와 G5 의 action 라벨을 섞어 읽지 말 것.

## 완화하지 않은 것

`one_change`, `fixed`, `seeds`, `seats`, G1 의 `bank>=4`·`hands>=3`·`nonempty_tiles>=25`,
G2 `L=0`, G3 `c=0`·`public L=0`, G5 `차이 step 집합={1}`·`farmer/hands 차이=0`,
`next_if_success`/`next_if_failure` — **한 자리도 바꾸지 않았다.**

## pool 고정 (B4)

`private_artifacts/tapes/*-replay.json` **47개**. `*.json` 은 49개이고 추가된 두 개가 본 실험의
target·control tape 라서 glob 을 쓰면 G1·G3 가 독립이 아니게 된다. 실행 전 필수 단계:

```bash
python3 tools/verify_pool.py --glob 'private_artifacts/tapes/*-replay.json' \
  --expected-count 47 \
  --expected-sha256 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1
# 2026-09-14 06:18 UTC 재실행: PASS, count=47, exact SHA matched
```

## 반송 1~7 처리 확인

| 항목 | 판정 | 근거 |
|---|---|---|
| 1 `hire_failed` | 해소 | `tools/instrument.py` `_do_hire` wrapper, 전후 `len(farm["hands"])` 비교 |
| 2 `seed_blocked_plant` | 해소 | `seed_blocked_plants()` 가 engine `kaggriculture.py:920-928` atomic 조건과 동일 — 합성 입력 직접 검증 |
| 3 로컬 step 추출기 | 해소 | `local_step_snapshot()` — 합성 입력 직접 검증 |
| 4 action stream diff | 도구 존재, **미시험** | self-compare smoke 만 통과. parent-vs-candidate parity 는 구현 후 최초 판정 |
| 5 G4 기준 | **본 카드에서 확정** | §A |
| 6 pool 고정 | 해소 | §B, verify_pool PASS |
| 7 step 시점 | **본 카드에서 확정** | §C |

## 파일과 SHA-256

- `experiments/cards/EXP-008-opening-liquidity.md` — `6a5adda98c1e6388d2729a24dba6ee97c2334bbf61296f8a80328cf2c640a4b1` (신규)
- `HYPOTHESES.md` HYP-0030 — `실험`·`다음 행동` 갱신, 상태는 `PLANNED` 유지
- event `coordination/hypotheses/claude/EVT-2026-09-14T062052.457676+0000-196712d7.json`

## 실행한 검증

```text
python3 tools/verify_pool.py --glob 'private_artifacts/tapes/*-replay.json' \
  --expected-count 47 --expected-sha256 201d9724…6e1
PASS, count=47, exact SHA matched

python3 -c "seed_blocked_plants / local_step_snapshot 합성 입력 호출"
seeds W1/C1 -> {'WHEAT': 2} · W2/C1 -> {} · W2/C0 -> {'CARROT': 1}   # engine atomic 조건과 일치
snapshot -> bank/hands/nonempty_tiles/action 이 env.steps[index] observation 에서 추출됨

python3 tools/validate_hypotheses.py
hypothesis ledger PASS: 30 entries
```

주의: 이 환경에서는 `.venv` 가 macOS 용이라 `pytest`·`kaggle_environments` 전체 테스트를 재실행하지 못했다.
`tests/test_instrument_exp008.py` 19 passed 는 Codex 보고의 인용이며 내가 재현한 값이 아니다.

VERDICT | EXP-008 사전등록 완료, BLOCK 해제 | `experiments/cards/EXP-008-opening-liquidity.md` sha256 `6a5adda98c1e6388d2729a24dba6ee97c2334bbf61296f8a80328cf2c640a4b1` | verify_pool PASS(47) · 계측 함수 2종 engine 조건 일치 · ledger PASS(30) | NEXT ACTION: Codex 가 candidate 구현 → SHA freeze → parent 326셀 baseline 기록 → candidate 실행


---

## `reports/claude/20260914-1536-EXP008-TIMING-CORRECTION.md`

# EXP-008 §C timing 정정 — Codex 지적 수용

1. **무엇을 바꿨는가:** 카드 §C 의 "같은 index 의 action 은 아직 반영 전" 이라는 설명이 **틀렸다.**
   `env.steps[i]` 는 transition 한 칸이고, 거기 저장된 observation 은 **그 action 을 처리한 뒤의 상태**다.
   G5 가 몇 개 셀에 적용되는지도 비어 있어서 **326셀 각각**으로 명시했다.
2. **왜 하는가:** G1 의 `step25 hands>=3` 은 index 25 의 `HIRE x3` 이 **실행된 뒤** 일꾼이 몇 명인지 보는 gate다.
   "반영 전"으로 읽으면 합격 숫자의 의미가 뒤집힌다. 결과를 보기 전에 고쳐야 사전등록이 유효하다.
3. **측정과 결과:** engine 1.32.7 에서 3-step 에피소드를 **직접 재현**했다 —
   `index 1` 에 `action=HIRE` 와 그 결과인 `money=2999`·`hands=1` 이 함께 저장된다.
   `verify_pool` `PASS, count=47`, ledger `PASS: 30 entries`.
   카드 SHA-256 `6a5adda9…a4b1` → **`fe27fc14bc7b56fcb8e87ce36cfcd7b0e4f301ef73a7fa13e11b05113c4abc2a`**.
4. **막힌 점과 다음 행동:** 막힌 점 없음. Codex 가 정정본을 재검토한 뒤 candidate 를 구현한다.
   나는 candidate 구현·실험 실행을 하지 않았다.

---

## 정정 내용

### P0 — transition 규약 (수용)

```text
env.steps[i].action       = observation step i-1 을 보고 agent 가 만든 action
env.steps[i].observation  = 그 action 을 interpreter 가 처리한 뒤의 상태
env.steps[i].observation.step == i      (kaggle_environments/core.py:626)
```

따라서 **action stream label `i` 와 observation index `i` 는 같은 transition** 을 가리킨다.
`tools/instrument.py` 의 라벨 `obs["step"] + 1` 은 agent 가 본 observation 이 index `i-1` 이므로 `i` 가 된다.

| gate | 읽는 대상 |
|---|---|
| G1 | transition `i` 의 **결과 상태** `env.steps[i].observation` |
| G5 | transition `i` 에 **적용된 action** `env.steps[i].action` |

정정 전 카드가 쓴 "G1 의 index 와 G5 의 라벨은 규약이 다르다" 도 **틀렸다.** 같은 index 다.

### P1 — G5 적용 범위 (수용)

G5 는 **326셀 각각** (target 2 + control 2 + public 40 + pool 282) 에서
`different_steps == [1]` 및 `farmer_or_hands_different_steps == []` 를 판정한다.
`fixed: step 2..718 전체 parent action` 을 실제로 검증하려면 표본 셀로는 부족하다.
yaml `metric`·`success` 의 G5 줄에 범위를 적었고, **허용 차이 집합 `{1}` 은 바꾸지 않았다.**

### Codex 의 질문 두 건 회신 (수용)

- `hire_failed<=7` 은 채택하지 않는다. 숫자 7 의 근거가 없고 핵심 세 HIRE 는 G1 이 직접 판정한다.
  G4 는 사전등록한 셀별 non-regression 역할을 유지한다.
- SUCCESS 여도 `[LOCAL]` mechanism support 일 뿐이며 hosted 우위 근거가 아니다.
  카드의 `next_if_success` 와 §근거와 한계가 이미 명시하므로 그대로 유지한다.

## 바꾸지 않은 것

`one_change`, `fixed`, `seeds`, `seats`, index `23/25/47`,
G1 `bank>=4`·`hands>=3`·`nonempty_tiles>=25`, G2 `L=0`, G3 `c=0`·`public L=0`,
G4 셀별 `candidate <= parent`·`status!=DONE=0`, G5 `{1}`·`farmer/hands 차이 0`,
`next_if_success`/`next_if_failure`, pool 47개·hash.

## 실행한 검증

```text
/usr/bin/python3 -c "kaggle_environments.make('kaggriculture', episodeSteps=3, seed=7).run([hire_once,'pass'])"
index 0 | obs.step 0 | action PASS | money 3000.0 | hands 0
index 1 | obs.step 1 | action HIRE | money 2999.0 | hands 1
index 2 | obs.step 2 | action PASS | money 2999.0 | hands 1

kaggle_environments/core.py:626
new_state[0].observation.step = 0 if self.done else len(self.steps)

python3 tools/verify_pool.py --glob 'private_artifacts/tapes/*-replay.json' \
  --expected-count 47 --expected-sha256 201d9724…6e1
PASS, count=47, exact SHA matched

python3 tools/validate_hypotheses.py
hypothesis ledger PASS: 30 entries
```

주의: 이 환경의 `.venv` 는 macOS 용이라 `pytest` 전체 스위트는 재실행하지 못했다.
위 engine 재현은 `/usr/bin/python3` 에 `.venv` site-packages 를 경로 추가해 실행한 것이며,
`kaggriculture` 환경 모듈은 lock 과 같은 파일을 썼다.

## 파일과 SHA-256

- `experiments/cards/EXP-008-opening-liquidity.md` — `fe27fc14bc7b56fcb8e87ce36cfcd7b0e4f301ef73a7fa13e11b05113c4abc2a`
- 선행 보고 `coordination/reports/claude/20260914-1521-EXP008-PREREGISTERED.md` — §C 관련 서술은 본 보고로 대체
- ledger event `coordination/hypotheses/claude/EVT-2026-09-14T063615.634873+0000-268c397d.json`

VERDICT | §C 정정 완료, 숫자 gate 불변 | card sha256 `fe27fc14bc7b56fcb8e87ce36cfcd7b0e4f301ef73a7fa13e11b05113c4abc2a` | engine 3-step transition 직접 재현 · verify_pool PASS(47) · ledger PASS(30) | NEXT ACTION: Codex 재검토 후 candidate 구현 → SHA freeze → parent 326셀 baseline 선기록 → 실행


---

## `reports/claude/20260914-1945-REVIEW-FEEDBACK-BATCH.md`

# 검토 피드백 5건 처리 — Claude 소유 경로 완료, 나머지는 work order 로 이관

1. **무엇을 했는가:** 외부 검토가 지적한 5건 중 Claude 가 직접 할 수 있는 것을 전부 처리했다 —
   EXP-008 카드의 중복 ID 제거(strict validator 복구), 실험 registry 채우기, 미추적 파일 추적.
   나머지 둘(gate 코드 수정, EXP-008 실행)은 Codex 소유 경로라 work order 로 넘겼고,
   BOARD·HANDOFF 는 코디네이터 소유라 붙여넣을 문구까지 만들어 proposal 로 냈다.
2. **왜 했는가:** validator 가 깨져 있으면 어떤 실험도 사전등록 무결성을 주장할 수 없고,
   문서마다 현재 상태가 달라 들어오는 agent 가 서로 다른 작업을 시작할 수 있었다.
3. **측정과 결과:** `validate_hypotheses.py --strict` **exit 3 → exit 0**.
   tar SHA 2건 기록과 일치 확인. pool `PASS, count=47`.
   commit `0291151`(카드 수정), `64af7d7`(추적·registry).
4. **막힌 점과 다음 행동:** Claude 쪽은 막힌 점 없음. Codex 착수 2건과 사람 확인 2건이 남았다(아래 §이관).

---

## 처리 1 — EXP-008 카드 중복 ID 제거 (내가 만든 결함)

`experiments/cards/EXP-008-opening-liquidity.md` 의 yaml 블록이 상단 header 와 같은
`hypothesis_id` / `test_id` 를 다시 선언하고 있었다. `tools/validate_hypotheses.py:15-16` 의 정규식은
파일 전체에서 필드를 세므로 `multiple ... fields` 와 **자기 자신과의** `duplicate TEST-0008` 가 났다.

```text
before: python3 tools/validate_hypotheses.py --strict  -> exit 3
after : python3 tools/validate_hypotheses.py --strict  -> exit 0 (ledger PASS: 30 entries)
```

yaml 에서 두 줄을 삭제했다. EXP-005~007 카드와 같은 형태가 됐다(yaml 에는 `id:` 만).
**숫자 gate·`one_change`·`fixed`·`seeds`·`seats`·측정 시점 정의는 변경 없음.**
카드 SHA-256 `fe27fc14…bc2a` → **`e0e93652991005514bb37f11cf9c69be6d07739594cfee4760ac8792ff30773a`**
(`HYPOTHESES.md` HYP-0030, `coordination/TASKS.md` 동시 갱신). commit `0291151`.

## 처리 2 — registry 완결과 미추적 파일 추적 (commit `64af7d7`)

`experiments/registry.csv` 에 v0 한 행만 있었다. 열 4개를 추가하고 현재 경로를 채웠다.

| exp_id | artifact sha256 | submission | hosted |
|---|---|---|---|
| EXP-006 | `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` | 56165718 | 1915.6 |
| EXP-007 | `8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180` | 56175620 | 1819.8 |
| EXP-008 | card `e0e93652…773a` | 미제출 | N/A (PENDING) |

두 tar SHA 를 직접 재계산해 기록과 **일치** 확인했다.
추적에 올린 것: `experiments/cards/EXP-005..007`,
`coordination/proposals/claude/{exp005,exp006,exp007,harness}` 의 소스와 manifest.
`submission.tar.gz` 는 `.gitignore:5,9` 대상이라 그대로 둔다 — **복원 경로는 source + manifest + SHA** 다.
`releases/` 는 Codex 소유라 손대지 않고 work order 로 넘겼다.

과거 전수 정리는 하지 않았다. 현재 사용하는 경로만 완결했다.

## 이관 — Codex 착수 2건

| 파일 | 내용 | 선행 |
|---|---|---|
| `coordination/proposals/claude/WORK_ORDER_EXP-008_execution.md` | candidate 구현 → SHA freeze → **parent 326셀 baseline 선기록** → 실행 → G1~G5 | 없음 |
| `coordination/proposals/claude/WORK_ORDER_gate_split_and_release_tracking.md` | 일반 release gate 에서 `sell_unfilled` 강등, `releases/` 추적 | 없음, 병행 가능 |

`sell_unfilled = Σ요청n − 체결` 은 `evidence/FACTS.md` F-T7 이 이미 **phantom 98.7% · 창고 미판매 0** 으로
판정했는데도 `tools/instrument.py` 의 `is_clean()` 합격 조건에 남아 있다.
**EXP-008 의 G4 는 이 변경과 무관하다** — 카드가 정한 셀별 기준을 그대로 쓴다.

## 이관 — 코디네이터·사람 확인

`coordination/proposals/claude/PROPOSAL_20260914_board_handoff_sync.md`
- BOARD 한 문장 요약 1줄 교체 (표의 나머지 값은 **맞다**)
- HANDOFF_CURRENT.md 전면 교체 (2026-09-07 자로 낡음)
- `plan/` 정본이 어느 파일인지 사람 확인 필요 — 정해지면 Claude 가 첫 제출 지시 절을 정리한다

## 하지 않은 것

- **최신 hosted snapshot 미확보.** 09-12 사람 제공 snapshot 이후 값은 N/A. Kaggle CLI 는 사람 실행이 필요하다.
- **두 슬롯 비상관 재판독 계획 미고정.** 별도 카드가 필요하며 EXP-008 표본과 섞지 않는다.
- **테스트 전체 스위트 미재현.** 이 세션의 device VM 은 Linux 인데 레포 `.venv` 는 macOS 용이다.

## 실행한 검증

```text
python3 tools/validate_hypotheses.py --strict            -> exit 0, ledger PASS: 30 entries
python3 tools/verify_pool.py --glob '...*-replay.json'   -> PASS, count=47, exact SHA matched
shasum -a 256 coordination/proposals/claude/exp006/submission.tar.gz
  1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721   (기록과 일치)
shasum -a 256 releases/public-thomas-replay-router-v2-exact/submission.tar.gz
  8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180   (기록과 일치)
```

VERDICT | 피드백 5건 중 Claude 몫 완료 | commit `0291151` `64af7d7` · card sha256 `e0e93652…773a` | strict validator exit 3 → 0 · tar SHA 2건 일치 · pool PASS(47) | NEXT ACTION: Codex 가 work order 2건 착수, 코디네이터가 BOARD·HANDOFF 적용, 사람이 hosted snapshot 확보


---

## `reports/claude/20260916-1710-P0-OWNER-RECORD-SYNC.md`

# P0 — EXP-008 결과·registry·hosted ledger 동기화

**2026-09-16 17:10 KST · claude (cowork) · 근거: `coordination/proposals/codex/20260915-owner-record-sync.md`**

1. 무엇을 바꾸거나 시험하는가: EXP-008 실행 결과(FAILURE)를 `experiments/registry.csv`에 반영하고,
   `evidence/HOSTED_LEDGER.md`에 09-15 01:13 KST 직접 snapshot을 추가하고,
   `evidence/FACTS.md`의 무승부 규정 문구와 "최종 BT 범위 불일치" 서술을 정정·연결했다.
2. 왜 하는가: BOARD P0가 이 동기화를 종료 조건으로 걸었고, EXP-008 결과·registry·ledger의 current 포인터가
   서로 어긋난 상태였다.
3. 무엇을 측정했고 결과가 어땠는가: 문서 정리 작업이라 실험 측정은 없다. 적용 후
   `python3 tools/validate_hypotheses.py --strict` → **PASS: 30 entries, exit 0**.
4. 무엇이 막혀 있고 다음 행동은 무엇인가: BLOCK 없음. 남은 것은 Gemini P1a(완료, `analysis/public_source_triage/20260916.md`),
   Codex P1b(release preflight, 아직 manifest 미작성), P1c(hosted 패배 조사)다. 본 세션은 P1b manifest를
   독립 검토만 했고 새 전략 카드나 추가 agent는 만들지 않았다.

VERDICT | **P0 적용 완료** | registry EXP-008 행 갱신, HOSTED_LEDGER 09-15 snapshot 추가, FACTS 정정 2건 | `--strict` exit 0 | NEXT ACTION: Codex가 P1b manifest 확정 시 본 세션의 [독립 검토](20260916-1720-P1B-PREFLIGHT-MANIFEST-REVIEW.md) 반영

## 적용한 항목 (proposal 1~6 대조)

1. **EXP-008 결과 반영** — 이미 `coordination/reports/codex/20260914-2025-EXP008-RESULT.md`와
   `evidence/raw/EXP-008/verdict.json`(sha256 `9e8cabf4…22d43`)에 기록돼 있음을 확인했다.
   candidate main.py sha256 `930ed160…f079`도 이 보고서와 일치.
2. **Frozen card 보존** — `experiments/cards/EXP-008-opening-liquidity.md`(사전등록 sha256 `e0e93652…773a`)는
   **미변경**이다. 본문 `## 결과` 절의 "미실행" 문구를 조용히 덮어쓰는 대신, proposal이 제시한 두 방법 중
   "별도 dated 결과 문서와 registry 포인터를 사용" 쪽을 택했다 — 카드를 고치면 이 SHA를 인용하는
   BOARD.md/HANDOFF_CURRENT.md/TASKS.md/verdict.json 여러 곳의 참조가 동시에 깨지기 때문이다.
   결과는 `experiments/registry.csv`의 `card_path`·`result_path` 두 열과 이 보고서로 연결했다.
3. **registry 현재 행** — `experiments/registry.csv` EXP-008 행의 `agent`·`code_sha`·`n`·`result`·`verdict`·
   `next_action`·`result_path`·`card_path`·`artifact_sha256`을 갱신했다. `artifact_sha256`은 지시대로
   card SHA를 쓰지 않고 `N/A (candidate tar 미생성, 미제출)`로 두었고, card SHA는 `card_path` 열에
   "frozen"으로 명시해 분리했다.
4. **HOSTED_LEDGER append** — `evidence/HOSTED_LEDGER.md`에 "2026-09-15 01:13 KST" 절을 추가했다.
   출처는 `coordination/reports/codex/20260915-0115-KAGGLE-SNAPSHOT.md`. EXP-006 1862.6(−34.3) ·
   EXP-007 1635.9(−11.5), Sian 1,724위. 과거 행은 그대로 두었다(append-only).
5. **FACTS 최소 정정** —
   - `docs/official/rules.md` 무승부 규정 줄에 "이 규정은 최종 순위 tiebreak이며 게임 내 draw를 W로
     바꾸지 않는다"는 `[2026-09-16 구분 추가]` 각주를 달았다.
   - "⚠️ 최종 BT 범위 불일치" bullet에 `[2026-09-16 연결]`로 F-T12를 명시적으로 연결했다
     (F-T12가 이미 스태프 원문으로 해소한 사실이며, 이번에 새로 발견한 것처럼 쓰지 않았다).
   - 새 snapshot 출처를 `F-T13 [HOSTED]`으로 추가했다(09-15 01:13 KST CLI+UI, `20260915-0115-KAGGLE-SNAPSHOT.md`).
   - `git diff` 확인 결과 F-T1~F-T12(테이프 재생 계측 섹션)는 이미 작업트리에 uncommitted 상태로
     존재했다 — 이번 세션이 새로 쓴 내용이 아니라 그 위에 이어서 썼다.
6. **자기 TASKS 문구** — `coordination/TASKS.md`의 `TEST-0008`·`REVIEW-2026-09-14` 두 섹션(모두 claude 소유
   행)에 2026-09-16 날짜의 연결 addendum을 추가해, candidate 미구현/실험 미실행 서술과 "Codex 착수 대기"
   이관 문구를 각각 실제 완료 행(TEST-0008-EXEC DONE·GATE-SPLIT-20260914 DONE)에 연결했다.
   다른 agent의 과거 행(예: KAGRI 시리즈, PUBLIC-PLAN-* 행)은 손대지 않았다. 이번 작업 자체의 행도
   테이블 끝에 `P0-OWNER-RECORD-SYNC-20260916`으로 추가했다.

가설 원장(`HYPOTHESES.md`, `coordination/hypotheses/`)은 지시대로 직접 편집하지 않았다 — Codex updater event 대상이다.
`coordination/BOARD.md`도 coordinator 전용이라 수정하지 않았다.

## 재현

```bash
python3 tools/validate_hypotheses.py --strict
git diff --stat -- experiments/registry.csv evidence/HOSTED_LEDGER.md evidence/FACTS.md coordination/TASKS.md
```


---

## `reports/claude/20260916-1720-P1B-PREFLIGHT-MANIFEST-REVIEW.md`

# P1b — Codex release preflight manifest 사양 독립 검토

**2026-09-16 17:20 KST · claude (cowork), 독립 검증자 역할 — 실행하지 않음, manifest·계획 문구만 검토**
대상: `plan/kaggriculture_deadline_plan_20260915.md` §5.2·§6·§8, BOARD P1b 행. `experiments/results/p1_release_preflight/manifest.json`은 이번 확인 시점(2026-09-16 17:xx KST) **아직 생성되지 않았다** — 초안 자체가 없으므로 실제 manifest 파일이 아니라 그 사양(§5.2)을 검토 대상으로 삼았다.

1. 무엇을 바꾸거나 시험하는가: P1b의 실행 전 사양(§5.2 1~4단계)이 AGENTS §5(실험 규약)·§7.5(6줄 체크리스트)·§6(런타임 계약) 기준으로 "실행 전 고정"에 필요한 숫자·범위를 실제로 다 갖췄는지 확인했다.
2. 왜 하는가: BOARD P1b 종료 조건이 "manifest 불완전이면 BLOCKED"이고, AGENTS §5는 서술형 항목이 하나라도 있으면 구현자가 BLOCKED로 반환하라고 못박는다. 사전등록 카드와 동일한 기준으로 봐야 한다.
3. 무엇을 측정했고 결과가 어땠는가: `[LOCAL]` §5.2 원문·§6·§8 대조, `experiments/results/` 디렉터리 확인(해당 폴더 없음), 기존 release manifest 2건(`releases/public-thomas-…`, `releases/public-yhay81-…`)과 GATE-SPLIT schema-3 정의 대조. 아래 §A에 5건의 미확정 항목을 정리했다.
4. 무엇이 막혀 있고 다음 행동은 무엇인가: manifest 초안이 아직 없어 PASS/FAIL 판정 자체가 **N/A**다. 아래 §A의 항목을 Codex가 manifest 작성 시 숫자로 채우고, Claude(범위 확인)·별도 독립 검증자가 그 수치를 승인한 뒤 실행해야 한다. §B에 오늘 18:00 KST 종료 조건 대비 시간 실행 가능성 평가를 적었다.

VERDICT | **manifest 사양 N/A — 미착수, §A 5건 미확정 항목 존재** | 근거는 plan §5.2/§6/§8 원문과 아래 인용 | 실행 없음(검토만) | NEXT ACTION: Codex가 §A 반영해 `manifest.json` 초안 작성 → Claude 범위 확인 → 별도 독립 검증자 지정 → 실행

## §A. §5.2 사양에서 빠졌거나 모순되는 조건

1. **"기존 EXP-008 control 실패 재현 셀"은 존재하지 않는다.** EXP-008 verdict(`evidence/raw/EXP-008/verdict.json`, 보고서 `20260914-2025-EXP008-RESULT.md`)는 **control W/D/L = 2/0/0 (G2 PASS)**, 실패한 쪽은 **target** Remielle_108076177 seed `1125321547` (target W/D/L 0/0/2, G1 FAIL)이다. §5.2 1단계 문구 그대로 읽으면 재현 대상이 없는 채로 manifest가 확정된다. `control` → `target`으로 정정하고 정확한 opponent artifact·seed를 명시해야 실행 가능하다.
2. **"에피소드 예산(§6)의 70~80%"의 §6이 어느 문서인지 모호하다.** 이 문구는 plan §8에 있는데, plan 자기 자신의 §6은 "새 카드가 반드시 답해야 할 질문"으로 런타임과 무관하다. 실제로 가리키는 것은 **AGENTS.md §6**(턴 1s·overage 60s·에피소드 1,200s, 에이전트당 nominal 상한 719×1s+60s=779s)로 보이지만, 그렇다 해도 "1,200s의 70~80%"(840~960s)인지 "779s의 70~80%"(545~623s)인지 원문이 숫자로 확정하지 않았다. AGENTS §5 "모든 임계는 숫자다" 기준으로 이 항목은 서술형이다 — manifest는 정확한 초 단위 상한 하나를 못박아야 한다.
3. **self-play 3판·smoke/stress의 seed가 없다.** §5.2 1단계는 "self-play 3판과 양 좌석 smoke/stress"라고만 쓰고 구체적 seed 목록을 주지 않는다. 기존 release manifest(`public-thomas-…/manifest.json`)는 self-play seeds `7,1000,1001`을 실제로 썼으므로 전례는 있지만, 이번 §5.2 원문 자체에는 seed가 박혀 있지 않아 "실행 전 고정" 기준을 충족하지 못한다.
4. **opponent 모집단이 EXP-008과 같은 326셀(47 tape + 4 public bot)인지 명시가 없다.** §5.2는 "전체 opponent artifact·seed 목록"이라고만 쓴다. plan §5.2 도입부가 "공개 4봇·47 tape는 고정 regression 세트로 보존한다"(§5.3-4)고 한 것과 같은 모집단을 재사용한다는 명시적 연결이 없으면, 다음 검토자가 임의로 부분집합을 고를 위험이 있다(AGENTS §5의 "seed는 리스트로 확정. 실행 후 추가 금지"와 같은 문제).
5. **"독립 검증자"가 누구인지 지정돼 있지 않다.** BOARD P1b 행은 "Codex / Claude manifest 확인 / 독립 검증자"로 3인 역할을 나눴고 AGENTS §4는 "제안자가 자기 결과를 단독 승인할 수 없다"고 못박는다. Codex가 manifest 작성자이자 실행자이므로, Codex와 다른 제3의 검증자가 필요하다 — 이번 P1 배치에는 Gemini(P1a 담당)·Claude(범위 확인) 둘뿐이고 이번 세션에서는 사람 지시로 추가 agent를 만들지 않으므로, 이 역할은 **사람이 직접 맡거나 Gemini가 P1a 완료 후 겸임**하는 방식으로 사람이 결정해야 한다. manifest에 이름이 없으면 Codex 단독 승인이 되어 §4를 위반한다.

## §B. 오늘 18:00 KST 종료 조건 대비 실행 가능성

- BOARD·HANDOFF는 P1 세 산출물(§5.1/§5.2/§5.3)의 **09-16 18:00 KST** 종료 조건을 걸었다. 이 검토 시점(17:20 KST) 기준 manifest 초안조차 없다.
- §5.2 스스로 "manifest 초안 → Claude·독립 검증자 확인 → 실행 → report.md/JSON 산출 → 구현자와 다른 검증자가 재확인"이라는 최소 5단계를 요구한다. §A의 5개 항목을 지금 확정해도, 326셀 규모(EXP-008과 동일 모집단이라면) 실행과 독립 재확인까지 남은 40분 안에 끝내는 것은 **현실적으로 불가능**하다.
- 좋은 소식: 실행에 필요한 도구(`tools/instrument.py` schema-3, `tools/verify_pool.py`, clean-room tar 추출 명령)는 EXP-008에서 이미 검증된 채로 존재한다 — 도구 부재가 병목은 아니다. 병목은 **사양 확정과 독립 검증자 배정**이다.
- 권고: 오늘 18:00 KST에는 §5.2를 "PASS"가 아니라 **BLOCKED**로 기록하고(§5.2 4단계가 이미 이 경로를 정의해 둠), §A 5건을 반영한 manifest 초안 작성과 독립 검증자 지정을 다음 세션의 최우선 항목으로 넘기는 것이 계약과 맞다. 시간에 맞추려고 축소 실행을 "preflight 완료"로 대신하는 것은 §5.2 1단계가 명시적으로 금지한다.

## 재현

```bash
ls experiments/results/p1_release_preflight/   # 없음 — manifest 미작성 확인
grep -n "control 실패\|에피소드 예산(§6)\|self-play 3판\|독립 검증자" plan/kaggriculture_deadline_plan_20260915.md
cat evidence/raw/EXP-008/verdict.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['target_wdl'], d['control_wdl'])"
```


---

## `reports/claude/20260916-1745-P1B-CURRENT-MANIFEST-REVIEW.md`

# P1b — 실제 manifest.json 현재본 검토 (current-manifest review)

**2026-09-16 17:45 KST · claude (cowork), `reviews.claude_manifest_review` 역할.**
검사 실행·새 전략 설계·추가 agent 생성 없음 — 파일 대조와 비파괴적 SHA-256 확인만 했다.

대상: `experiments/results/p1_release_preflight/manifest.json`
**manifest_draft sha256 `97ee065713465957e119c706b00f5b01c459d2c47dd0900a4bda9d3863af1019`**
(prepared_at_utc 2026-09-16T08:02:51Z, updated_at_utc 2026-09-16T08:26:10Z, status `BLOCKED`, `execution_authorized: false`).
함께 검토: `report.md` sha256 `f307438f4c971c1aa3cf37660cf337c7b1e8b26585191aa30d0dc9e9d3899dbf`,
`resume.json` sha256 `2ae25f2115e7da8f3457ea7f779edb47b9479190b5503b57f6dc140cc8bd51a8`,
`coordination/reports/codex/20260916-1726-P1B-RUNNER-UPDATE.md`.

**이전 검토와의 관계:** 이전 `20260916-1720-P1B-PREFLIGHT-MANIFEST-REVIEW.md`는 manifest 생성 **전** plan §5.2 사양 검토였다.
이번이 실제 manifest 파일에 대한 첫 current-manifest review다 — 이전 판단(특히 "manifest 미작성")을 그대로 재사용하지 않았다.

1. 무엇을 바꾸거나 시험하는가: 실제 manifest.json·report.md·resume.json을 재현 대상/opponent·seed·좌석·전체 판수/시간 분모와 정확한 초 단위 상한/parent-only 판정/제출 전 체크리스트 다섯 축으로 대조했다.
2. 왜 하는가: BOARD P1b 종료 조건이 "Claude manifest 확인"이고, manifest 자체가 `reviews.claude_manifest_review.required_checks`로 이 다섯 축을 명시했다.
3. 무엇을 측정했고 결과가 어땠는가: 아래 §A(항목별 PASS/BLOCKED), §B(교차 일관성 대조 결과 — 전부 일치), §C(비파괴적 SHA-256 재확인 — 11개 파일 전부 manifest 기재값과 일치) 참고. 실제 tar 실행·episode 측정은 **N/A**(금지됨).
4. 무엇이 막혀 있고 다음 행동은 무엇인가: 5개 계약 미확정 항목 중 3개는 [proposal](../../proposals/claude/20260916-p1b-manifest-contract-resolution.md)로 Codex에 정정을 제안했다. 나머지 2개(opponent population 크기, 독립 검증자 지정)는 사람 판단이 필요해 BLOCKED로 남긴다.

VERDICT | **CURRENT-MANIFEST REVIEW: 3/5 항목 제안으로 해소 가능, 2/5 BLOCKED(사람 결정 필요)** | manifest `97ee0657…f1019`, 11개 인용 SHA 전부 실물과 일치 | 교차 일관성 대조 5축 전부 통과 | NEXT ACTION: 사람이 §D 두 질문에 답하고 Codex가 proposal 3건 반영 → manifest 재freeze → 독립 검증자 승인 → 실행

## §A. 항목별 상태

| 항목 | 이전(2026-09-16 17:20) 상태 | 이번 상태 | 처리 |
|---|---|---|---|
| 재현 대상(target/control) | 계획 §5.2 문구 오류 지적만 | **PROPOSAL로 해소 제안** | target 2 + control 2 유지, control 그룹명·목적 문구 정정 제안(§1) — schema-3에서도 gating되는 `noop_actions=44`·`shed_discarded=7` 이력이 근거 |
| opponent 모집단 크기 | 미확인 | **BLOCKED — 사람 결정 필요** | 13-episode 초안 vs EXP-008식 326-cell vs 다른 고정 집합; manifest 자체가 "성능/hosted 우위 주장이 아니다"라고 명시해 326-cell 전량이 계약상 필수는 아니지만, 정확한 크기는 자원·시간 배분 문제라 계약만으로 못 정한다 |
| seeds | 미지정 지적 | **승인(APPROVED)** — proposal에 포함 | `7,1000,1001`은 결과를 보기 전 고정된 기존 release 전례, `1125321547`/`1989066512`는 EXP-008 카드 target/control seed와 정확히 일치. Claude reviewer 권한으로 승인 |
| runtime 분모·정확한 초 | §6 모호성만 지적 | **PROPOSAL로 해소 제안** | AGENTS §6의 "에이전트당 779s"가 단일 아티팩트 판정에 맞는 분모라고 결론, 80% = 623초를 PASS 상한으로 제안(§3). 나머지 세부 임계(first_call_ms 등)는 원문에 숫자가 없어 이번 제안에서 제외 |
| 독립 검증자 | 미지정 지적 | **BLOCKED — 사람 결정 필요** | manifest 자체가 "human assignment or an existing non-Codex reviewer designated by the human; no agent is created"로 못박음. 이번 세션 지시("추가 agent 생성 금지")와도 합치 |

## §B. 교차 일관성 대조 (사용자 요청 5축)

**모두 내부적으로 일치함을 확인했다 — 불일치 발견 없음.**

1. **재현 대상(target/control):** `opponents[2]` seed `1125321547` = EXP-008 카드 target seed, `opponents[3]` seed `1989066512` = EXP-008 카드 control seed. 둘 다 EXP-008 verdict.json의 `target_wdl=[0,0,2]`(FAIL) / `control_wdl=[2,0,0]`(PASS)와 정확히 대응 — manifest가 "control 실패"라고 잘못 부르지 않고 `DISPUTED_LABEL_AND_PURPOSE`로 스스로 격리해 둔 것도 확인했다.
2. **상대·seed·좌석·전체 판수:** `cells` 4개 그룹 합산 — self_play 3ep(양쪽 parent, 6 player-record) + builtin_smoke 6ep(3seed×2seat, parent 6·opponent 6) + hosted_loss_stress 2ep(1seed×2seat, parent 2·opponent 2) + exp008_control 2ep(1seed×2seat, parent 2·opponent 2) = **13 episodes, parent 16 player-record, opponent 10 player-record, self-play parent 6** — `expected_totals`의 `episodes=13`·`parent_player_records_gated=16`·`opponent_player_records_recorded_not_gated=10`·`self_play_parent_players_checked=6`과 **정확히 일치**(직접 재계산 확인).
3. **시간 기준 분모·상한:** manifest는 현재 `UNRESOLVED_NO_PASS_THRESHOLD`로 올바르게 미확정 상태를 유지하고 있다(assert 없이 측정만) — §5.2 원문의 모호한 "§6"을 그대로 gate로 쓰지 않은 것은 안전한 처리다. 정확한 숫자는 proposal §3에서 제안.
4. **우리 봇만의 합격 판정:** `runners.gate_scope`("non-self-play는 parent A seat만 top-level verdict, self-play는 both") + `acceptance.diagnostic_not_gating`에 "opponent counters outside self-play" 명시 + `reproduction.execution_note`("sell_unfilled을 gate failure로 해석 금지")가 서로 정합적이다. `--gate-agent` 인자가 `runner_template_argv`에도 반영돼 있어 사양-실행 스크립트 간 불일치도 없다.
5. **제출 전 체크리스트:** AGENTS §7.5 6줄(Identity/Schema/Runtime/Isolation/License/Ledger) 각각이 `acceptance`의 `identity`/`schema`/`runtime`/`isolation`/`license`/`ledger` 필드로 1:1 대응한다. `completion`(720 steps DONE/DONE 등)과 `parent_zero_gate_each_player_record`(8-counter 절대 0)는 AGENTS §7.5엔 없지만 plan §6·GATE-SPLIT 계약의 정당한 확장이라 모순이 아니다. `ledger.required_before_submission=false`도 AGENTS §7.5의 "Ledger는 제출 후에만 채운다"와 일치.

## §C. 비파괴적 SHA-256 재확인 (실행 없이 파일만 hash)

manifest가 인용한 11개 경로를 `shasum -a 256`로 직접 재확인했다 — **전부 일치**.

```
AGENTS.md                                                        c687a612…ec96d  ✓
plan/CURRENT.md                                                  af86e425…0ab3b  ✓
plan/kaggriculture_deadline_plan_20260915.md                     df62f4b6…4f238  ✓
coordination/BOARD.md                                            5d31e77d…9b9cd  ✓
experiments/cards/EXP-006-clone-preempt.md                       6be09531…2788  ✓
coordination/proposals/claude/exp006/submission.tar.gz(artifact) 1c478c24…9721  ✓
private_artifacts/tapes/Remielle_episode-108076177-actions.json  75ea188e…caa5c4 ✓
private_artifacts/tapes/today_episode-108079022-actions.json     b1bd786a…2faa637 ✓
tools/instrument.py (runner)                                     284dee4c…d0629  ✓
tools/gate_contract.py                                           3a3e423b…71353c ✓
tools/smoke.py                                                   4fa89573…21f38ac2262b ✓
```

tar 멤버 4개(`main.py`/`yh_base.py`/`actions.json`/`LICENSE.txt`)의 개별 SHA는 **추출 없이는 확인 불가**이고, 추출은
`reproduction.preconditions`가 리뷰 완료 전까지 금지한 행위라 이번엔 하지 않았다 — tar 전체 SHA만 재확인했다.

## §D. 사람 결정이 필요한 두 항목

1. **opponent population 크기.** 현재 초안(13 episodes: self-play 3 + builtin smoke 6 + target/control stress 4)로 진행할지,
   EXP-008 규모(326-cell, 47 tape+4 public bot)까지 넓힐지, 다른 고정 집합으로 할지. manifest 목적이 "release correctness, not
   performance/hosted-strength claim"이라 326-cell 전량이 계약상 필수는 아니라고 판단했지만, 최종 크기는 이 세션이 정할 수 없다.
2. **독립 검증자 이름.** Codex(작성자)와 달라야 한다(AGENTS §4). 사람이 직접 맡거나, P1a를 마친 Gemini가 겸임하거나,
   제3의 기존 검토자를 지정해야 한다. 이번 세션은 추가 agent를 만들지 않았다.

## 재현

```bash
cat experiments/results/p1_release_preflight/resume.json
python3 -c "
import json
d = json.load(open('experiments/results/p1_release_preflight/manifest.json'))
print(d['status'], d['execution_authorized'])
print(d['review_reconciliation']['reproduction_target']['status'])
print(d['review_reconciliation']['seeds']['status'])
print(d['review_reconciliation']['runtime_cutoff']['status'])
print(d['review_reconciliation']['opponent_population']['status'])
print(d['review_reconciliation']['independent_validator']['status'])
"
shasum -a 256 AGENTS.md plan/CURRENT.md plan/kaggriculture_deadline_plan_20260915.md coordination/BOARD.md \
  experiments/cards/EXP-006-clone-preempt.md coordination/proposals/claude/exp006/submission.tar.gz \
  private_artifacts/tapes/Remielle_episode-108076177-actions.json private_artifacts/tapes/today_episode-108079022-actions.json \
  tools/instrument.py tools/gate_contract.py tools/smoke.py
```


---

## `reports/claude/20260916-1814-P1B-REVISED-MANIFEST-APPROVAL.md`

# P1b — 개정 manifest(runtime 기준 포함) 최종 검토

**2026-09-16 18:14 KST · claude (cowork), `review_reconciliation.runtime_cutoff` 최종 승인자 역할.**
검사 실행·tar 추출·새 전략 설계·추가 agent 생성 없음 — 파일 대조·SHA-256 재확인·diff 재계산·과거 측정치 대조만 했다.

대상: `experiments/results/p1_release_preflight/manifest.json`
**reviewed_manifest_sha256 `46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c`**
(status `BLOCKED`, `execution_authorized: false` — 정상. 이 리뷰가 실행을 승인하는 것이 아니라 기준을 승인하는 것이다.)
근거 문서: `coordination/reports/codex/20260916-P1B-13EP-SCOPE-APPROVED.md`.

1. **무엇을 검토했는가:** 이전 draft(`97ee0657…f1019`, 내가 17:45에 검토)와 현재 manifest(`46fd9e5e…4801c`) 사이의 전체 필드 diff, 개정된 runtime 기준(parent별 623s / 공유 episode wall 960s / hard ceiling 1200s)의 산출식, `tools/instrument.py`의 실제 측정 구현, 과거 유사 실행(동일 720-step 구조)의 실측 wall/agent 시간.
2. **왜 하는가:** codex 보고서가 "최신 manifest SHA와 이 보고서를 읽고 623s/960s 제안을 검토해 승인 또는 구체적 수정 근거를 별도 보고서에 남기라"고 명시했고, `review_reconciliation.runtime_cutoff.status`가 `PROPOSED_PENDING_FINAL_REVIEWS`로 남아 있어 이 리뷰 없이는 13경기 실행이 계속 BLOCKED다.
3. **무엇을 측정했고 결과가 어땠는가:** 아래 §A(diff 범위 확인) · §B(산출식 재계산) · §C(코드 대조) · §D(과거 실측 대조) 참고. 전부 PASS.
4. **남은 일:** Antigravity가 같은 SHA(`46fd9e5e…4801c`)에 대해 별도 보고서로 승인하면, Codex가 artifact/runner/engine/opponent hash를 재확인한 뒤 13경기를 전부 실행할 수 있다.

VERDICT | **REVISED RUNTIME CRITERIA APPROVED (623s parent / 960s shared / 1200s hard ceiling) — 수정 없음** | manifest `46fd9e5e…4801c`, diff는 scope-approval + runtime 필드로 한정, 나머지(seeds/opponents/artifact/engine/runner SHA)는 전부 불변 | §A~§D 전부 PASS, 과거 실측 대비 여유 150~400배 확인 | NEXT ACTION: Antigravity의 동일 SHA 승인 대기 → Codex 실행

## §A. diff 범위 확인 (prior `97ee0657…f1019` → current `46fd9e5e…4801c`)

두 JSON을 전체 key 단위로 diff했다(78개 leaf 차이, 스크립트 재현 가능). 차이는 정확히 다음 범위로 한정된다:

- `cells[*].scope_status`: `PROPOSED_NOT_APPROVED` → `APPROVED_BY_USER_13_EPISODE_DRAFT` (4개 그룹 전부, episodes/seeds/opponent_id/parent_seats 값 자체는 불변)
- `cells[3].group`: `exp008_control_failure_reproduction` → `exp008_control_counter_violation_stress`, 라벨 텍스트를 "outcome-failure reproduction 아님"으로 재확인 (내 17:45 리뷰 §A 제안과 일치)
- `acceptance.runtime.*`: 이전 미확정 draft 값(`first_call_ms_lte 800` 등 6개, 근거 없이 gate가 될 뻔한 값)을 `prior_proposed_criteria`로 격하·보존하고, 새 `proposed_criteria`(총 3개: `total_s_by_parent_player_lte 623`, `wall_seconds_lte 960`, `wall_seconds_hard_ceiling_lt 1200`)로 교체
- `review_reconciliation.*` / `reviews.*`: 상태 전이(`UNRESOLVED`→`APPROVED_BY_USER` 등)와 이번 두 보고서(claude 17:45, antigravity 17:46) 경로·SHA 기록 추가
- `owner_decision`: 신규 블록, 사람 승인(초안의 13경기로 진행) 기록
- `status_reasons`, `next_action_after_review`, `updated_at_utc`: 위 변경을 반영한 서술 갱신

**변경되지 않음(직접 대조):** `artifact.*`(sha/bytes/멤버 4개), `engine.*`, `runners.primary/gate_contract.sha256`, `opponents[*].sha256`, `cells[*].seeds`, `cells[*].episodes`, `expected_totals.episodes/parent_player_records_gated/opponent_player_records_recorded_not_gated/self_play_parent_players_checked`(13/16/10/6, 직접 합산 재확인 — 3+6+2+2=13, 6+6+2+2=16, 6+2+2=10). Codex 보고서의 "원래 13경기와 seed·좌석·상대를 유지" 주장과 정확히 일치한다.

## §B. runtime 산출식 재계산

```
per_parent = floor(0.8 * (719 * 1 + 60)) = floor(0.8 * 779) = floor(623.2) = 623   ✓ manifest와 일치
shared     = 0.8 * 1200 = 960                                                        ✓ manifest와 일치
margin     = 1200 - 960 = 240s (엔진 오버헤드 여유)                                  ✓ 명시된 설명과 일치
623 * 2    = 1246 > 1200(hard ceiling)                                               ✓ "parent별 한도만으로는 공유 예산을 보장 못 한다"는 근거가 수치적으로 성립
```

`engine.agent_calls_per_player=719`, `act_timeout_seconds=1`, `overage_seconds=60`, `local_episode_timeout_seconds=1200`과 대조해 세 입력값 모두 manifest 자체 필드에서 가져온 것이며 임의 상수가 아님을 확인했다.

논리 구조도 타당하다: parent별 상한(623s)은 "한쪽이 비정상적으로 느리다"를 잡고, 공유 wall 상한(960s)은 "둘 다 개별 상한 안에 있어도 합이 hard ceiling을 넘는" 경우를 잡는다 — 두 기준이 서로 다른 실패 모드를 커버하므로 중복이 아니다. `acceptance.runtime.scope`가 "공유 timing 실패는 이 실행을 막지만 parent 귀책을 증명하지 않는다"고 명시한 것도 EXP-006 리뷰 피드백(디버그 F-T7, sell_unfilled 오판정 사례)과 같은 원칙 — 진단과 판정을 분리 — 이라 일관적이다.

## §C. 코드 대조

- `tools/instrument.py` (SHA `284dee4c…d0629`, manifest 기재값과 재계산 일치, §A에서 미변경 확인) — `time.perf_counter()`로 `agent_ms`와 `wall`을 측정해 JSON의 `total_s`/`wall_seconds` 필드로 출력한다(코드 522·591·616·618·636·656행). CPU time이 아니라 elapsed time이라는 manifest의 `timing_semantics` 서술과 일치.
- `tools/gate_contract.py` (SHA `3a3e423b…71353c`, 미변경) — 623/960/1200 수치나 runtime 관련 키가 코드에 전혀 없다. 즉 **runtime은 현재 `--require-pass`로 자동 게이트되지 않는다** — manifest가 `acceptance.runtime.status`를 `PROPOSED_PENDING_FINAL_REVIEWS`로 두고 gate가 아니라 "제안된 기준"으로 명시한 것과 정확히 일치하며, 코드와 문서 사이 괴리가 없다.
- **실행 시 주의(코드 결함 아님, 절차 노트):** runtime 기준이 승인되어도 `instrument.py`가 자동으로 623s/960s를 assert하지 않으므로, 13경기 실행 후 각 cell JSON의 `total_s`(parent별)와 `wall_seconds`를 이 승인된 숫자와 **수동으로 대조**해야 PASS/FAILURE 판정이 완결된다. Codex가 aggregate 단계에서 이 대조를 수행하는지 실행 전에 한 번 더 확인 권장.

## §D. 과거 실측 대비 여유 확인

같은 720-step 구조의 과거 실행에서 실제 관측된 시간(동일 저장소, 추출 없이 기존 tracked JSON만 열람):

| 파일 | wall_seconds | player total_s |
|---|---|---|
| `evidence/raw/EXP-008/candidate/control_today_108079022__seed-1989066512__seat-1.json` | 2.597 | — |
| `evidence/raw/EXP-008/candidate/pool_Mengfei_Li_episode-106276129-replay__seed-5101__seat-0.json` | 2.607 | — |
| `releases/public-yhay81-shop-router-0909-exact/preflight_selfplay.json` (3 episodes) | 3.266 / 3.454 / 2.784 | 0.042 / 0.218 / 0.035 |

실측 wall_seconds는 2.6~3.5초, player별 agent 시간은 0.03~0.22초 — 제안된 960s/623s 상한 대비 **약 150~400배 여유**가 있다. 즉 이번 parent A 아티팩트가 과거와 비슷한 속도라면 새 기준은 정상 실행을 오탐(false failure)시키지 않으면서, 엔진이 허용하는 최악의 경우(호출당 최대 1s + 719회 + 60s 초과분)까지 안전하게 커버한다. 기준이 지나치게 느슨해 사실상 무의미한 것도 아니다 — hard ceiling(1200s)의 80%로 설정돼 있어 실제 pathological stall(예: 무한루프 근접 또는 대량 timeout 누적)은 여전히 잡아낸다.

## 결론

세 가지 개정 사항(scope_status 승인, exp008_control 그룹 라벨 정정, runtime 기준 623s/960s/1200s) 모두 제안대로 승인한다. 수정 요청 없음. manifest 파일 자체는 이 리뷰에서 변경하지 않았다.

## 재현

```bash
shasum -a 256 experiments/results/p1_release_preflight/manifest.json
python3 -c "
import json
d = json.load(open('experiments/results/p1_release_preflight/manifest.json'))
c = d['cells']
print('episodes', sum(x['episodes'] for x in c))
print('parent_gated', sum(x['parent_player_records_gated'] for x in c))
print('opponent_recorded', sum(x.get('opponent_player_records_recorded_not_gated',0) for x in c))
print(d['acceptance']['runtime']['proposed_criteria'])
"
shasum -a 256 tools/instrument.py tools/gate_contract.py
grep -n "623\|960\|1200" tools/instrument.py tools/gate_contract.py
```


---

## `reports/claude/20260916-2035-P1B-CORRECTNESS-PREREG.md`

# P1b 상태 동기화 + 첫 correctness 경로 사전등록

task `P1B-CORRECTNESS-PREREG-20260916` · Claude(opus-5) · 2026-09-16 20:35 KST / 11:35 UTC

## 1. 무엇을 바꾸거나 시험하는가

두 가지다.

첫째, **끝난 검증을 문서에 반영했다.** P1b 결과의 독립 검증이 끝났는데 산출물 네 곳에
"독립 검증 PENDING" 이 남아 있었다. 이를 `VERIFIED_LOCAL_FAILURE` 로 맞추는 exact patch 를 정리했다.
내 소유 경로(`HYPOTHESES.md` via updater)는 직접 갱신했고, Codex·Coordinator 소유 경로는 제안으로 냈다.

둘째, **첫 correctness 작업을 사전등록했다.** 대상은 release zero gate 실패 중
실제로 물건이 사라지는 `shed_discarded` 다. 다만 **repair card 가 아니라 진단 card 를 등록했다.**
기존 증거만으로는 "어떤 행동이 그 손실을 만들었는지" 를 특정할 수 없기 때문이다.
원인을 모른 채 수정을 넣으면 손실을 숨기게 된다.

## 2. 왜 이 원인을 먼저 고치는가

zero gate 실패 counter 중 실제 자원 손실은 `shed_discarded` 하나다.

| counter | 합 | 성질 |
|---|---:|---|
| `shed_discarded` | **482** | **물건이 소멸** — 되돌릴 수 없는 실제 손실 |
| `noop_actions` | 3,488 | 액션 1개 낭비. 자원 소멸은 아님 |
| `seed_blocked_plant` | 56 | 그 턴 PLANT 가 PASS 로 치환. 씨앗은 남음 |
| `buy_failed` / `hire_failed` | 74 / 18 | 거래 미체결. 현금은 남음 |
| `hands_length_mismatch` | 92 | schema 문제. 별도 경로 |
| `shed_unsold` / `orders_truncated` / `exceptions` | 0 / 0 / 0 | 이미 깨끗함 |
| `sell_unfilled` | 1,541,806 | **diagnostic** — 요청 초과분이며 손실이 아님 |

`shed_discarded` 만이 "가진 것을 잃는" 항목이다. 그래서 첫 correctness 대상이다.
그리고 `one_change` 원칙에 따라 `noop_actions`·BUY/HIRE/PLANT 실패·hands mismatch 는
같은 카드에서 건드리지 않는다.

## 3. 기존 evidence 로 무엇을 측정했고 결과가 어땠는가

**새 경기를 한 판도 돌리지 않았다.** 기존 13개 cell JSON 과 엔진 소스만 읽었다.
재현: `python3 scratch/claude_shed_attribution_20260916.py` → exit 0.

### 3.1 독립 3차 재집계 — 전부 일치

16개 gated parent record 를 manifest 의 cell 정의로 귀속해 재계산했다.
`aggregate.json` 의 9개 counter 합과 nonzero record 수가 **한 건도 어긋나지 않았다.**
13/13 이 `steps=720`, `statuses=["DONE","DONE"]`.

### 3.2 group 별 `shed_discarded` 재집계 `[LOCAL]`

| group | record | `shed_discarded` | nonzero | 점유율 |
|---|---:|---:|---:|---:|
| self_play | 6 | **40** | 6/6 | 8.3% |
| builtin_smoke (starter) | 6 | **10** | 6/6 | 2.1% |
| hosted_loss_stress (target, Remielle 108076177) | 2 | **418** | 2/2 | **86.7%** |
| exp008_control_counter_violation_stress | 2 | **14** | 2/2 | 2.9% |
| **합계** | **16** | **482** | **16/16** | 100% |

record 별 (seed 별 좌석 2개는 값이 동일):

| record | `shed_discarded` | `noop_actions` | `daily_max_shed==100` 일수 | `>=90` 일수 |
|---|---:|---:|---:|---:|
| target 1125321547 (양 좌석) | **209** | 1,149 | **6** | 13 |
| control 1989066512 (양 좌석) | 7 | 44 | 2 | 5 |
| self 7 / self 1001 | 7 | 44 | 2 | 5 |
| self 1000 | 6 | 114 | 1 | 4 |
| starter 7 | 3 | 136 | 1 | 2 |
| starter 1000 / 1001 | 1 | 101 / 112 | 1 | 5 |

- **16/16 record 가 `shedCapacity` 100 에 최소 하루 도달**하고, 100 도달 일수가 많을수록
  `shed_discarded` 가 크다. 예외 record 없음.
- target stress 2 record 가 전체 손실의 86.7% 를 차지한다. 이 두 record 는
  hosted episode 108076177 의 exact 재현이며 최종 reward `[58,246 / 167,541]` 이
  hosted 결과와 일치한다(postmortem `20260913-0250` 와 동일).
  즉 **실제로 크게 진 경기에서 자원 손실이 집중된다.**

### 3.3 엔진 메커니즘 — 여기까지는 확정 `[ENGINE]`

`kaggriculture.py` sha256 `bc8a5487…653e`:

- `:843-856 _drop_inventories_to_shed` — 하루 종료 시 unit inventory 를 shed 로 이월.
  `room = max(0, capacity - current)`, `take = min(n, room)`, 그 뒤 **`del inv[item]`**.
  초과분은 예외 없이 소멸한다.
- `:866-878 _end_of_day` 가 player 마다 1회 호출하고, **그 뒤에** farmer/hands 를 리셋한다.
- `:940-947` 스텝 순서상 그날 마지막 턴의 시장 매도는 이 이월 **앞**에서 끝난다.
- `tools/instrument.py:450-461` 의 hook 이 `lost = carried - moved` 로 세는 값이 `shed_discarded` 다.

→ **482 는 전부 "하루 끝에 창고 여유가 모자라 unit 이 들고 있던 물건이 사라진 것"** 이다.
이 메커니즘은 확정이다.

### 3.4 그런데 원인은 특정되지 않았다 — `N/A / BLOCKED`

메커니즘이 확정이라고 원인이 확정된 것은 아니다. 기존 JSON 에 없는 값들:

| 필요한 값 | 기존 JSON | 비고 |
|---|---|---|
| day 별 `shed_discarded` | **N/A** | 총합만 누적 |
| drop 시점의 shed 점유량 | **N/A** | `daily_max_shed` 는 market hook 시점의 그날 최대치이지 drop 시점 값이 아니다 |
| 사라진 item 과 수량 | **N/A** | 기록 없음 |
| 어느 unit 이 들고 있었는가 | **N/A** | 기록 없음 |
| 그 unit 의 그날 마지막 action | **N/A** | 기록 없음 |
| 그 unit 이 창고에 인접했는가 | **N/A** | 기록 없음 |
| in-day `DROP`/`PLACE` 초과 소멸 | **미계측** | 현재 hook 은 end-of-day 경로만 감싼다 → 482 는 총 손실의 **하한**일 수 있다 |

`tools/postmortem.py` 도 이 목적에 **불충분**하다. 두 가지 이유다.
① shed 관련 필드를 하나도 추출하지 않는다(`grep -n "shed" tools/postmortem.py` → 0건).
② `make()` + `env.run()` 으로 **새 에피소드를 생성**한다. 이번 작업의 금지 사항이다.
그래서 실행하지 않았다.

따라서 지금 상태에서 후보 원인은 최소 셋이며, **기존 증거로는 구분할 수 없다.**

1. 하루 끝에 창고 여유가 있었는데도 이월이 실패 (순서/클램프 문제)
2. 창고가 꽉 찬 채로 하루가 끝났고 인접한 unit 이 예치를 시도하지 않음
3. 창고가 꽉 찼고 unit 이 창고에 닿지도 못함 (이 경우 수정하려면 tape·매도·생산 중 하나를
   건드려야 하는데 셋 다 fixed → correctness repair 가 아니라 전략 변경이다)

셋 중 하나를 지금 고르는 것은 추측이다. 그래서 **repair card 를 승인하지 않았다.**

## 4. 무엇이 BLOCKED 이고 Codex 의 다음 행동은 무엇인가

**BLOCKED: 원인 귀속에 필요한 계측이 없다.**

등록한 것은 진단 card `experiments/cards/EXP-011-shed-discard-attribution.md`
sha256 `daabcd0d1386b95559d3433bd410c8b06a09d37f6a1407a5427e2c8c2164ddf2`
(`HYP-0031` / `TEST-0011`, `EXP-009`·`EXP-010`·`TEST-0009`·`TEST-0010` 은 예약이므로 미사용).

필요한 최소 계측(카드 §B): `tools/instrument.py` **한 파일**에만
`_drop_inventories_to_shed` 호출 1건당 구조화 레코드 1건을 추가한다 —
`day`·`step`·`shed_total_before`·`carried_before`(unit×item)·`deposited`·`discarded`·
`unit_last_op`·`unit_shed_adjacent_at_drop`·`shed_full_turns_today`.
그리고 in-day `DROP`/`PLACE` 소멸을 관측 전용 counter 로 신설한다(gate 에는 넣지 않는다).
**제출 tar 는 1바이트도 바꾸지 않는다.** 바꾸면 identity 가 깨져 재현 자체가 무효다.

그 뒤 **같은 13경기**를 새 출력 경로로 다시 돌린다. 유효성 조건은 하나다 —
16 record 의 9개 counter 와 episode reward 가 frozen 값과 **정확히** 같아야 한다.
다르면 계측이 경기를 바꾼 것이므로 결과 전체를 INVALID 로 격리한다.

판정은 전부 숫자다. 482 단위를 (창고 여유 / 창고 인접 / 마지막 op) 세 축의 8개 class 로
배타 분류하고, 지배 class 가 **baseline 층 80% 이상 + target 층 80% 이상 + 16 record 중
14개 이상에서 단독 최다** 일 때에만 repair 를 승인한다. 미달이면 repair 금지다.
지배 class 가 "창고가 꽉 찼고 예치를 시도했다" 또는 "unit 이 창고에 닿지 못한다" 로 나오면
그건 tape·매도·생산을 건드려야 하는 전략 경계이므로 **repair card 를 만들지 않고 사람에게 이관**한다.

후속 repair card `EXP-012` 의 acceptance (success 9개 / failure 6개, guard 전용 counter 의무,
parity 검사)는 카드 §E 에 **지금 고정**했다. 결과를 본 뒤 임계를 바꿀 수 없다.

### Codex 의 다음 행동 2가지

1. `coordination/proposals/claude/20260916-EXP011-codex-implementation-handoff.md`
   sha256 `5535e737034be0bb41588744ce04477dc2f9dc72f220279331f9dbd8039e5d67` 의 §3 착수 전 SHA 표를
   대조하고, §4 계측을 구현한 뒤 §5 로 같은 13경기를 재실행한다. 모호한 항목이 있으면
   구현하지 말고 BLOCKED 로 반환한다(AGENTS §5).
2. `coordination/proposals/claude/20260916-p1b-status-sync-patches.md`
   sha256 `e7f1376ef1eaa98a6a9c094b6c079b00b27e2e509a0347e68e03a6af0baecda6` 의 §4.1~4.4 patch 를
   자기 소유 경로에 반영한다. §4.5 BOARD 는 Coordinator 전용이다.

---

VERDICT | **BLOCKED_NEEDS_INSTRUMENTATION** — `shed_discarded` 482 의 메커니즘은 `[ENGINE]` 확정이지만 원인 귀속에 필요한 per-drop-event 계측이 없다. repair card 를 승인하지 않고 진단 card 만 사전등록했다 | card `experiments/cards/EXP-011-shed-discard-attribution.md` sha256 `daabcd0d1386b95559d3433bd410c8b06a09d37f6a1407a5427e2c8c2164ddf2` · parent tar `coordination/proposals/claude/exp006/submission.tar.gz` sha256 `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` · manifest sha256 `46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c` | 13개 cell JSON 독립 재집계 9/9 counter 일치·exit 0, group 재집계 40/10/418/14 = 482, 16/16 record 가 shedCapacity 100 도달, `postmortem.py` 는 shed 필드 0건이며 새 경기 생성이 필요해 사용 불가, `validate_hypotheses.py --strict` exit 0 (31 entries) | NEXT ACTION: Codex 가 `tools/instrument.py` 에만 drop-event 귀속 계측을 추가해 동일 13경기 재실행 → §D 판정 후에만 EXP-012 사전등록

## 부록 — 판정 경계 (성공해도 참인 것)

- 이 진단이나 EXP-012 가 성공해도 **즉시 제출 가능하다는 뜻이 아니다.**
- `noop_actions` 3,488 등 다른 zero-gate failure 가 남으면 다음 correctness card 가 필요하다.
- local correctness 는 hosted superiority 를 증명하지 않는다. hosted 주장 `N/A`.
- 현재 active `EXP-006`(56165718) / `EXP-007`(56175620) 과 제출 tar 는 수정하지 않았다.
- zero gate 를 낮추거나 `shed_discarded` 를 diagnostic 으로 강등하지 않았다.
- 이번 작업에서 코드 구현·경기 실행·Kaggle 제출·threshold 완화를 하지 않았다.


---

## `reports/claude/20260918-EXP011-CLOSURE-PRIORITY-ADJUDICATION.md`

# EXP-011 종결·우선순위 Coordinator 검토서에 대한 owner 판정 (2차)

VERDICT | **지적 6건 전부 수용 / 반박 0 / 미확정 1건 신설** | 소멸 482 units 의 coin 환산은 방식에 따라 43,977 ↔ 30,886 으로 **29.8% 차이** — 어느 쪽도 상한이 아니다 | NEXT ACTION: 우선순위 근거를 P1c 로 이관, `noop` reason taxonomy 를 먼저 정의

대상 검토서: `coordination/proposals/codex/20260918-EXP011-CLOSURE-PRIORITY.md`
sha256 `b1ed06b777abc4841747a60b4328ad670638878f5bf87fc51e3f0649ca15d137`.

**측정 결과는 뒤집지 않았다.** D1~D4/R 판정, 1,603 checks PASS, 482 units, 지배 class
`ROOM_PARTIAL|REMOTE|NO_DEPOSIT_ATTEMPT` (S1 64/64, S2 416/418, 단독 최다 16/16), 카드 라벨
`REPAIR_AUTHORIZED`, 임계 0.80/0.80/14, class 정의 8개, 층 고정, 측정 당시 card r2 sha256
`8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e` — **전부 그대로다.**
이번 작업은 그 결과에서 **도출할 수 있는 결론의 범위**만 좁힌다.

## 쉬운 설명

지난번 보고에서 "사라진 물건 209개는 돈으로 최대 19,200 정도" 라고 적었다. 그 숫자는 그 경기에서 **판 물건
전체의 평균 단가**를 사라진 물건 개수에 곱한 것이다. 그런데 사라진 물건은 대부분 **제일 싼 밀**이었다.
같은 경기에서 **밀은 밀 값으로, 딸기는 딸기 값으로** 계산하면 13,938 이 나온다. 27% 차이다.
그리고 그 13,938 도 최대치가 아니다 — 물건을 더 팔면 값이 떨어지기 때문이다. 그래서 "최대"라는 말을 뺀다.

## 1. 지적별 판정

### 지적 1 — 19,200 은 검증된 상한이 아니다 → **수용**

`evidence/FACTS.md` F-T16 은 `209 units × 92.0 coin/unit ≈ 19,200` 을 "**최대** 19,200 coin" 으로 적었다.
92.0 은 그 경기 **전체 실현 매도**의 평균 단가(`78,122 / 849`)이며 소멸 item 구성과 무관하다.

**추가 근거 (이번에 계산).** 소멸 item 구성은 싼 품목에 크게 치우쳐 있다:

| | gated 16 record (482 units) | target 2 record (418 units) |
|---|---|---|
| WHEAT (base 25) | 296 (61.4%) | 296 (**70.8%**) |
| FERTILIZER (base 100) | 98 (20.3%) | 34 (8.1%) |
| STRAWBERRY (base 120) | 34 (7.1%) | 34 (8.1%) |
| WOOL (base 200) | 30 (6.2%) | 30 (7.2%) |
| MILK (base 160) / EGG (base 50) | 12 / 12 | 12 / 12 |
| base 가중 평균 | 61.8 coin/unit | **56.0 coin/unit** |

같은 경기의 **item 별 실현 단가**(`realized_sell[item].avg_price`)를 그 item 의 소멸 수량에 적용하면:

| record | units | A: `n × 전체평균` (F-T16 방식) | B: `Σ n_item × 그 item 실현단가` | 차이 |
|---|---:|---:|---:|---:|
| target seat-0 / seat-1 | 209 / 209 | 19,231 / 19,231 | **13,938 / 13,938** | −27.5% |
| self seed-7 p0 | 7 | 603 | **294** | −51.2% |
| control seed-1989066512 p0 | 7 | 639 | **308** | −51.8% |
| **gated 16 record 합** | **482** | **43,977** | **30,886** | **−29.8%** |

→ F-T16 의 A 방식은 **약 30% 과대추정**이다. 미판매 item 은 0건이므로 B 는 전 품목에서 계산됐다.

**B 도 상한이 아니다.** 엔진 `market_price(item, inventory)` 는 `inventory > I0` 구간에서 재고의
**감소함수**이고(`:192-206`), `_commit_unit` 의 SELL 은 체결마다 `market["inventory"][item] += 1` 한다(price>1 일 때).
즉 209 units 를 추가로 팔면 단가가 내려간다. 반대로 drop 시점의 marginal price 가 그 경기 평균보다
높았을 수도 있다. **drop 시점의 market inventory·price 는 EXP-011 artifact 에 기록돼 있지 않다.**
따라서 **엄밀한 상한은 `N/A`** 이며, 이를 주장하려면 per-step market 상태를 기록하는 별도 계측이 필요하다.

**조치:** F-T16 의 "최대 19,200 coin" → "A 방식 거친 환산 ≈19,200 / B 방식 ≈13,938 / 엄밀한 상한 `N/A`" 로 정정.
baseline 의 "6~7 units ≈ 520~600 coin" 도 B 방식 **≈294~308 coin** 을 병기.

### 지적 2 — 추정치로 "주원인 아님"·"50판 중 1판"을 확정하지 말 것 → **수용**

- "shed 가 target 패배의 주원인이 아니다" 는 **정적 환산 시나리오**다: 마진 109,295 대비 A 방식 17.6% /
  B 방식 12.8%. 이것은 "소멸분을 그 단가에 그대로 돈으로 바꿔 우리 은행에 더한다" 는 가정이며,
  실제 회수는 매도 타이밍·가격·현금 연쇄·상대 궤적을 전부 바꾸므로 **causal effect 가 아니다.**
  회수가 다른 경로로 더 큰(또는 더 작은) 차이를 만들 가능성은 배제되지 않았다.
- F-T17 의 "50판 중 1판만 뒤집힘" 도 마찬가지다. 최소 패배 마진 252 coin 에 baseline 회수 추정치를
  **정적으로** 더한 산술이며, 실제 경기별 회수 counterfactual 은 측정되지 않았다.
- **조치:** F-T16·F-T17·카드 §G C-4·HYP-0031/0032 에서 해당 문장을 "가정 하 산술 시나리오" 로 한정하고,
  HYP-0032 의 'shed 주원인 배제' 표현을 확정 근거에서 내린다.

### 지적 3 — 3,488 actions 와 482 items 는 다른 단위다 → **수용**

`noop_actions` 는 **unit-turn 단위의 action 횟수**이고 `shed_discarded` 는 **item 개수**다.
7.2배는 두 양의 비율일 뿐 전략 가치·회수 가능 coin·기대 승률의 비교가 아니다.
shed 는 소멸 단위가 곧 판매 가능 item 이라 (부정확하게나마) coin 환산 경로가 있지만,
noop 은 "성공했다면 얼마였는가" 라는 반사실 모델이 필요해 같은 축에 놓을 수 없다.
**조치:** 7.2배를 우선순위 근거에서 **완전히 제거**한다. `noop_by_op` 분해(합 3,488, 누락 0)는
기술적 사실로만 남긴다.

### 지적 4 — no-op 은 모두 PASS 치환이 아니다 → **수용**

`tools/instrument.py` sha256 `ca64256f941f2098cafc531fc422363c5757995f721b449369ce72877a33fe28` `:537-541` 확인:

```
elif op in _TILE_OPS:
    if (_tile_sig(farm, before_pos[0], before_pos[1]) == before_tile
            and _inv_total(private, unit_index) == before_inv):
        c.noop_actions += 1
```

- 판정 기준은 **"엔진 호출 후 tile JSON 서명과 그 unit 의 inventory 총량이 둘 다 불변"** 이다.
  PASS 치환 여부를 보지 않는다. `_TILE_OPS` 는 PLANT·WATER·HARVEST·FERTILIZE·DIG·BUILD_COOP·
  BUILD_PASTURE·FEED·COLLECT_FERTILIZER·CARE·PICKUP·PLACE·DROP 13개.
- 따라서 **최소 세 종류가 한 counter 에 섞여 있다**: (a) 엔진이 전제조건 불충족으로 거부한 action,
  (b) 실행됐으나 상태가 이미 목표 상태여서 변화가 없는 **불필요한 중복 요청**, (c) 관측 축(tile 서명 + inv 총량)
  **밖**에서만 변한 action.
  (b) 실례: 엔진 `:524-530` `CARE` 는 `tile["cared_today"]` 가 이미 `True` 면 그대로 return 한다 —
  PASS 치환 없이 무변화다. 코디네이터가 든 예가 정확하다.
- **역방향 누락도 있다.** 엔진 `:920-931` 의 atomic PLANT 검증은 씨앗 부족 작물의 PLANT 를 `_apply_unit_action`
  **호출 전에** `["PASS"]` 로 치환한다. 그러면 op 가 `"PASS"` 라 `_TILE_OPS` 에 들어오지 않아
  **`noop_actions` 에 전혀 잡히지 않는다.** 그것은 별도 counter `seed_blocked_plant` (gated 합 56) 가 센다.
  즉 **"PASS 치환 = noop_actions" 는 양방향으로 틀렸다.**
- 추가 한계: `_inv_total` 은 **총 개수**만 보므로 1:1 품목 교환은 탐지되지 않고, money·seeds 변화는 관측 축 밖이다.
- **조치:** `evidence/FACTS.md` 에 F-T22 신설(정의·혼입·누락·한계). 향후 diagnostic 카드의 1차 산출물은
  coin 이 아니라 **reason taxonomy** 여야 한다는 것을 명시.

### 지적 5 — 기존 재현이 다음 계측의 무개입을 보장하지 않는다 → **수용**

EXP-011 의 "16/16 record exact" 는 **그 hook, 그 runner SHA, 그 13경기**에 대한 사실이다.
새 reason hook 은 자기 freeze·자기 tests·parent exact 재현을 다시 통과해야 한다.
`제출 위험 0` 이라는 표현은 **"이 범위에서 artifact 를 제출하지 않는다"** 는 범위 설명일 뿐이며
**계측 안전성의 근거로 쓰지 않는다.** → 판정문 §5 에서 해당 근거 ①을 정정.

### 지적 6 — EXP-014 를 noop 으로 선점하지 않는다 → **수용**

`experiments/cards/EXP-013-state-conditioned-hire-recovery.md` 가 `:98` `:648` `:680` `:776` `:810` 에서
`EXP-014` 를 **pool/public 확장 카드**로 이미 예약하고 있다.
**확인: `EXP-014` 라는 문자열은 내 소유 문서(카드 §G, FACTS, registry, 판정문, HYPOTHESES) 어디에도 기록되지 않았다**
(`grep -rn "EXP-014" experiments/cards/EXP-011-*.md evidence/ experiments/registry.csv coordination/reports/claude/` → EXP-011 관련 0건).
ID 선점은 대화에서만 언급됐고 **철회**한다. 설계 필요가 확정되면 원장을 대조해 충돌 없는 ID 를 배정한다.

## 2. 이번에 새로 발견한 것 — `--verify-only` 재현 명령의 위험 (미확정 → 확정, 코디네이터 지적의 확장)

코디네이터는 "r3 이후 live checkout 에서 `run.py --verify-only` 를 돌리면 card identity mismatch 가 나는 것이 정상"
이라고 적었다. **그보다 심각하다.**

`experiments/results/p1_shed_attribution/run.py` 를 읽으면:

- `identity()` 는 `freeze.json['inputs']` 의 **모든 경로**를 frozen SHA 와 대조하고, 그 inputs 에
  `experiments/cards/EXP-011-shed-discard-attribution.md` 가 **r2 SHA 로 포함**돼 있다.
- `verify()` 는 `check('D1-a', ..., identity(), [])` 로 그 결과를 gate 에 넣은 뒤,
  **마지막에 `write(ROOT/'aggregate.json', result)` 로 결과 파일을 덮어쓴다** (`:105` 직전).
- 따라서 r3/r4 카드가 있는 live checkout 에서 `--verify-only` 를 실행하면 D1-a 가 깨져
  `card_verdict='INVALID'`, `root_cause_verdict='INVALID'` 가 되고 **그 INVALID 가 aggregate.json 에 기록되어
  측정 결과가 파괴된다.**

**이번 작업에서 그 명령을 실행하지 않았다.** `aggregate.json` 은 현재도 sha256
`22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba` / `PASS` / `REPAIR_AUTHORIZED` 로 온전하다.

**조치 (owner 문서):** F-T20 과 카드 §G 의 재현 명령 주석에 "**live checkout 에서 실행 금지**,
freeze commit `0a4b10f` 의 r2 카드를 복원한 별도 checkout/사본에서만 실행" 을 명기한다.
**조치 (타 writer):** `run.py` 는 Codex 소유이므로 직접 고치지 않고
`coordination/proposals/claude/20260918-EXP011-verify-only-guard.md` 로 제안만 남긴다.

## 3. 유지되는 확정 결론 — 범위를 넘기지 않는다 (요청 항목 5)

**확정된 것은 이 한 문장뿐이다:**

> EXP-011 카드 §D 가 `ROOM_PARTIAL` class 에 허용한 `one_change` — **고정된 최종 이월(EOD `_drop_inventories_to_shed`)의
> 순서/클램프 변경** — 만으로는 gated 16 record 전부 `shed_discarded == 0` (§E 성공조건 2)을 달성할 수 없다.

근거: 엔진의 총 예치량 = `min(carried_total, room)` 은 unit 순서·item 순서와 무관(소스) + 44 event × 200 순열
시뮬레이션에서 총 소멸량 변화 0건(데이터). 그러므로 **EXP-012 는 사전등록 불가**다.

**이것이 기각하지 않는 것 — 확대 해석 금지:**

- shed 관련 **다른 전략 전체**를 기각하지 않는다. 마지막 턴 매도 증량, 사전 예치·매도 스케줄 변경,
  생산·수확 조절, 품목 우선순위 변경은 **이 카드가 측정하지 않았고 판정 대상도 아니다.**
- `shed_discarded` 의 전략적 가치가 작다고 확정하지 않는다. 지적 1·2 대로 coin 환산은 추정이고 상한은 `N/A` 다.
- 회수가 순위에 미치는 영향을 확정하지 않는다. 최신 window 표본은 `N/A` 다.
- EXP-013 을 지지하지도 기각하지도 않는다.

## 4. 우선순위 — 이전 제안을 철회하고 코디네이터 제안을 수용

**철회.** 1차 판정문 §5 의 "`noop_actions` 3,488 의 coin 귀속을 다음 카드로" 제안은 근거 세 가지 중
둘이 무너졌다 — (가) 7.2배는 단위가 다른 비교였고(지적 3), (나) "shed 경로는 가치 상한이 닫혔다" 는
상한이 아니라 추정이었다(지적 1·2). 셋째 근거("도구가 이미 입증됐다")도 지적 5 로 한정된다.

**수용.** 다음 의사결정 자료는 **P1c — 같은 최신 window 안의 패배·무승부와 실제 failure 연결**이다.
같은 비교표로 HIRE failure / actionable no-op / 접전·무승부를 정리한다:
해당 경기 수·분모, 최초 관측 시점, 분기 이후 손실 경로, artifact·submission ID, 실패 예시, 변경 범위, 검증 비용,
그리고 **인과 미확정 표시**. broad noop count 만으로 순서를 정하지 않는다.
09-12 표본(F-T17)·716점 격차(F-T18)를 현재값처럼 쓰지 않는다 — 최신 조회는 이번에 실행하지 않았고 `N/A` 다.

P1c 없이 당장 하나를 고르라는 **별도 사람 지시**가 있을 때에 한해 EXP-013 을 **검토 우선 후보**로 둔다.
이유는 hosted failure 연결과 구체 카드가 이미 있다는 것이지 **효과가 입증됐기 때문이 아니다.**
현재 그 지시도 실행 승인도 없으므로 구현하지 않는다.

## 5. 이번에 갱신한 문서 (owner 소유만)

| 경로 | 변경 |
|---|---|
| `evidence/FACTS.md` | F-T16 coin 환산 정정(A/B 병기, 상한 `N/A`), F-T17 산술 시나리오 한정, F-T20 재현 명령 경고, F-T21 가치 표현 정정·단위 불일치 주석, **F-T22 신설**(`noop_actions` 정의·혼입·누락) |
| `experiments/cards/EXP-011-...md` | §G **C-4 정정**(coin 추정 A/B), **C-6 신설**(확정 결론의 범위와 확대 해석 금지), 재현 명령 경고 |
| `coordination/reports/claude/20260918-EXP011-REVIEW-ADJUDICATION.md` | 상단 **정정 고지** 추가 — §5 우선순위 제안 철회, U2 수치 정정. 본문 판정(수용 4/반박 3/미확정 3)과 V1~V6 재검산은 유효 |
| `experiments/registry.csv` | EXP-011 행 `next_action` 정정 |
| `HYPOTHESES.md` | `tools/update_hypotheses.py` 로 HYP-0031·HYP-0032 event 기록 |
| `coordination/proposals/claude/20260918-EXP011-verify-only-guard.md` | **신규 제안** — `run.py` 의 identity 실패 시 `aggregate.json` 덮어쓰기 금지 (Codex 소유 파일) |

**보존한 것:** 측정 당시 card r2 SHA, 임계 0.80/0.80/14, class 정의 8개, 축 정의, 층(S1 64 / S2 418),
seeds·좌석·상대, §E acceptance, `REPAIR_AUTHORIZED` 라벨, `aggregate.json`·`allocation_audit.json`·
`freeze.json`·`commands.json` 원본. **`coordination/BOARD.md` 와 타 writer 파일은 수정하지 않았다.**
새 카드 작성·candidate 구현·경기 실행·제출 없음.


---

## `reports/claude/20260918-EXP011-REVIEW-ADJUDICATION.md`

# EXP-011 독립 검토 판정 — owner(Claude) 인수

> ## ⚠️ 정정 고지 (2026-09-18, 2차)
>
> Coordinator 검토서 `coordination/proposals/codex/20260918-EXP011-CLOSURE-PRIORITY.md`
> sha256 `b1ed06b777abc4841747a60b4328ad670638878f5bf87fc51e3f0649ca15d137` 의 지적을 **전부 수용**했다.
> 2차 판정문: `coordination/reports/claude/20260918-EXP011-CLOSURE-PRIORITY-ADJUDICATION.md`
> sha256 `3909891dcc4412c63b8802c5c9017545d5d8a35e2b695f4a7b09194b193d251c`.
>
> **아래 본문에서 무효가 된 부분:**
>
> 1. **§2 미확정 U2 의 coin 수치.** "target 209 units ≈ 최대 19,200 coin(17.6%)", "baseline 6~7 units ≈ 520~600 coin",
>    "50판 중 1판" — 19,200 은 **상한이 아니라** 그 경기 전체 매도 평균 단가(92.0)를 곱한 거친 환산이다.
>    소멸 item 의 61.4%(target 70.8%)가 WHEAT(base 25) 이므로 item 별 실현 단가를 쓰면 target ≈ **13,938**
>    (gated 합 43,977 → **30,886**, A 가 29.8% 과대). **엄밀한 상한은 `N/A`** 다. "50판 중 1판" 도
>    정적 환산 가정 하의 **산술 시나리오**이며 causal effect 가 아니다.
> 2. **§4 의 "shed 가 target 패배의 주 원인이 아니라는 해석은 배제된다".** 위 1 에 따라 이 표현을 **확정 근거에서 내린다.**
> 3. **§5 다음 행동 제안 전체를 철회한다.** 근거였던 "`noop_actions` 가 7.2배 크다" 는 **단위가 다른 비교**
>    (3,488 = action 횟수 / 482 = item 개수)이고, "shed 경로는 가치 상한이 닫혔다" 는 상한이 아니라 추정이었다.
>    또한 `noop_actions` 는 **PASS 치환 횟수가 아니다**(`evidence/FACTS.md` F-T22). 대화에서 언급한
>    `EXP-014` ID 는 EXP-013 r3 가 pool/public 확장으로 예약한 번호이므로 **철회**한다(이 문서에는 기록되지 않았다).
>    다음 의사결정 자료는 **BOARD P1c** 다 — 2차 판정문 §4.
> 4. **§1 V 표의 `run.py --verify-only` 재현 명령.** 이 카드에 정정 이력이 붙어 SHA 가 바뀐 뒤로는
>    **live checkout 에서 실행하면 `aggregate.json` 이 `INVALID` 로 덮어써진다.** 2차 판정문 §2 와
>    `coordination/proposals/claude/20260918-EXP011-verify-only-guard.md` 참조.
>
> **아래 본문에서 유효한 부분:** 지적별 판정(수용 4 / 반박 3 / 미확정 3)의 판정 자체,
> V1~V6 독립 재검산 결과(D1-c mismatch 0, 항등식 위반 0, 순열 불변성 0, class 재집계 일치, 매도 여력),
> §3 `REPAIR_AUTHORIZED` 와 설계 가능성의 분리, §4 EXP-013 분리 원칙(수치 근거 제외).
> 측정 결과·임계·class 정의·층·측정 당시 SHA 는 이 정정으로 바뀌지 않는다.


VERDICT | **측정 PASS 확정 / 카드 §A·§D 서술 정정 / EXP-012 사전등록 불가** | 44/44 loss event 에서 `discarded_total == max(0, carried_total − room)` (위반 0), unit·item 순열 200회/event 에서 총 소멸량 변화 0 | NEXT ACTION: shed repair 경로 종결, 계측 예산을 `noop_actions` 3,488 의 coin 귀속으로 이동 제안

문서 SHA-256 (판정 시점):

| 문서 | sha256 |
|---|---|
| 독립 검토 `coordination/reports/antigravity/20260918-EXP011-REVIEW.md` | `cb4f4c9e4b1171a0424b678eaef4d72d0d0993853d43d192c7ce0655ed689e1d` |
| 실행 결과 `coordination/reports/codex/20260918-EXP011-RESULT.md` | `10f885923175559a535bc93f2300979e8d6188d32a85c45ba78c8d7d3d18f919` |
| 정정 제안 `coordination/proposals/codex/20260918-EXP011-OWNER-CORRECTIONS.md` | `bb86221cc7dfb5f5f251876a1f27cc1e6e8d9c11f1d68921c7f2a6612737148a` |
| 실행 승인 `coordination/reports/codex/20260918-EXP011-AUTHORIZATION.md` | `2c1820d204ffe94bc49e51aa9e77570ff14d7c93fed5f16784ba3c99b0ab5f18` |
| **측정 당시 card r2** (보존) | `8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e` |
| 결과 `experiments/results/p1_shed_attribution/aggregate.json` | `22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba` |
| 결과 `experiments/results/p1_shed_attribution/allocation_audit.json` | `66ed824393d41aaae507866f327f5f9ae8f8bfa7c46d7993b10e197e43011fa8` |
| runner `tools/instrument.py` | `ca64256f941f2098cafc531fc422363c5757995f721b449369ce72877a33fe28` |

engine `kaggle-environments==1.32.7` py `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`. freeze commit `0a4b10f`.

## 쉬운 설명

Antigravity 의 독립 검토는 "숫자는 맞는데 원인 해석이 틀렸다" 고 말한다. owner 로서 그 말을 그대로 받지 않고
엔진 소스와 결과 데이터로 직접 다시 계산했다. 결론은 **검토가 맞다**. 하루 끝에 사라진 482개는
전부 "들고 온 양이 남은 공간보다 많았기" 때문이고, 넣는 순서를 바꿔도 사라지는 총량은 1개도 줄지 않는다.
그래서 카드가 예약해 둔 후속 실험(EXP-012)은 지금 형태로는 만들 수 없다. 카드의 과거 판정과 숫자는
그대로 두고, 잘못된 **설명 문장**만 정정 이력으로 남긴다.

## 1. owner 가 직접 돌린 재검산 (검토서를 인용하지 않은 독립 경로)

재현 스크립트는 `scratch/claude_exp011_owner_20260918/` 에 있다. 새 경기를 만들지 않고 저장된 cell JSON 과
엔진 소스만 읽는다.

| # | 검증 | 명령 | 결과 |
|---|---|---|---|
| V1 | D1-c 를 P1b 원본과 직접 대조 (rewards·statuses·steps·9 counter) | `python3 scratch/claude_exp011_owner_20260918/verify_d1c_vs_p1b.py` | **26 player-record 비교, mismatch 0**. `shed_unsold` 는 26/26 record 에서 0 |
| V2 | 손실 항등식 `discarded_total == max(0, carried_total − room)` | `python3 scratch/claude_exp011_owner_20260918/verify_order_invariance.py` | 48 loss event(gated 44 + 비 gated 4) **전부 성립, 위반 0**. `carried_total <= room` 인 event **0건** |
| V3 | 엔진 배분 재현 (`_drop_inventories_to_shed` 동일 greedy) | 동 | deposited·discarded **불일치 0** |
| V4 | 순서 불변성 — unit 순열 × item 순열 무작위 200회/event | 동 | **총 소멸량이 바뀐 event 0건** |
| V5 | class 재집계 | 동 | gated 480 `ROOM_PARTIAL\|REMOTE\|NO_DEPOSIT_ATTEMPT` + 2 `ROOM_PARTIAL\|ADJACENT\|NO_DEPOSIT_ATTEMPT` = 482, `aggregate.json` strata 와 일치 |
| V6 | EOD 직전 shed 재고의 판매 가능 여부 | `python3 scratch/claude_exp011_owner_20260918/sellable_headroom.py` | gated 44 event **전부** shed 재고가 100% `PRODUCTS`(비판매 품목 0), 재고량 9~82 가 손실 1~28 을 **매 event 에서 초과** |

V4 는 검토서가 산술로 논증한 것을 기계적으로 확인한 것이다. 엔진의 배분은 `room` 이 소진될 때까지 탐욕적으로
채우므로 **총 예치량 = `min(carried_total, room)`** 이고, 이 값은 unit 순서·item 순서에 의존하지 않는다.

## 2. 지적별 판정

### 수용 (4건)

| ID | 지적 | 근거 | 조치 |
|---|---|---|---|
| **A1** | card §A 의 "PLACE 도 용량 초과분을 버린다" 는 서술이 틀렸다 | engine `:393-411` 은 `n = min(n, room)` 뒤 `inv[item] -= n` 만 한다 → 초과분은 inventory 에 **보존**. `:344-355 DROP` 만 `del inv[item]` 로 버린다. fixture `tests/test_instrument_exp011.py::test_drop_discards_but_place_retains_overflow_and_animal_is_not_loss` (DROP loss 3/left 0, PLACE loss 0/left 3). 실측 `shed_discarded_inday_place` 는 26/26 record 에서 0 | card §A 정정 이력 r3, `evidence/FACTS.md` F-T14 정정 주석 |
| **A2** | `ROOM_PARTIAL` 은 event **시작 시점의 전체 shed 점유**만 뜻하며 "들고 온 물건을 다 담을 공간이 있었다"를 뜻하지 않는다 | V2: 44/44 loss event 에서 `carried_total > room`. 예 target seat0 day15 step383 — shed 55, room 45, carried 51, loss 6 | card §D 판정표의 **설명문** 정정 이력 r3. class 정의·임계·판정 결과는 불변 |
| **A3** | 최종 이월의 순서/클램프만 바꿔서는 총 소멸량을 줄일 수 없다 | V4 순열 불변성 0 위반 + 총 예치량 = `min(carried_total, room)` | card §D 후속 경로에 "이 경로로는 §E 성공조건 2 달성 불가" 명시. **EXP-012 사전등록 불가** |
| **A4** | 계측 자체는 게임을 오염시키지 않았고 D1~D4/R 판정은 정확하다 | V1 mismatch 0, V3 불일치 0, V5 strata 일치 | 카드상 `REPAIR_AUTHORIZED` 와 측정 결과를 **그대로 보존**. 덮어쓰지 않는다 |

### 반박 (3건)

| ID | 지적 | 반박 근거 |
|---|---|---|
| **R1** | 검토서 VERDICT 줄이 `aggregate.json` 의 SHA-256 자리에 `277566 바이트 파일` (파일 크기)을 적었다 | 실제 sha256 은 `22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba`. **검토서 본문의 identity 기재 결함**이다. 검토의 결론(§3.1~§3.3)은 별도 근거로 성립하므로 유지하되, 이 줄은 identity 근거로 인용하지 않는다 |
| **R2** | "EXP-012 는 이월 순서 변경이 아닌 **다른 전략적 접근을 취하도록 계획을 수정**해야 한다" | **수용 불가.** §E acceptance 는 실행 전 고정이고 카드 서두가 "결과를 본 뒤 임계를 고치지 않는다"고 못박았다. 생산 조절·사전 매도는 §D `ROOM_PARTIAL` 분기가 허용한 one_change(`이월 순서/클램프 단일 지점`) **밖**이다. 따라서 올바른 처리는 EXP-012 의 내용을 바꾸는 것이 아니라 **EXP-012 를 사전등록 불가로 종결하고, 필요하면 자기 근거·자기 gate·사람 승인을 갖춘 새 ID 의 카드를 따로 세우는 것**이다 |
| **R3** | "causal 해석 FAIL" 을 카드 판정의 실패로 읽는 것 | 카드가 산출한 것은 class 점유율과 그에 따른 라벨뿐이고 그 계산은 정확하다(A4). FAIL 인 것은 §D 판정표에 붙어 있던 **자연어 설명문**("여유 용량이 있는데도 이월에 실패했다")이다. 판정 라벨·임계·표본·class 정의는 정정 대상이 아니며 과거 판정을 소급 변경하지 않는다 |

### 미확정 (3건)

| ID | 항목 | 지금 아는 것 | 아직 모르는 것 |
|---|---|---|---|
| **U1** | 482 의 회수 **가능성** | V6: gated 44 event 전부에서 EOD 직전 shed 재고가 100% 판매 가능 품목이고 그 양(9~82)이 손실(1~28)을 초과한다. 엔진 스텝 순서가 `unit actions → _process_market → ... → _end_of_day` 이고 `_commit_unit` 의 SELL 은 shed 에서만 차감하므로, **마지막 턴 매도 1 unit 당 손실 1 unit 감소**가 산술적으로 성립한다 → 상한 482/482 (100%) | 이것은 **상한일 뿐이다.** `market_price` 는 시장 재고의 함수라 매도 증량은 단가를 눌러 이후 매도까지 손해를 준다(F-T14 근방 주의사항·AGENTS §3). 현금 경로 변화 → BUY/HIRE/PLANT 연쇄, action parity, 상대 반응은 **전혀 측정되지 않았다**. 이 경로는 별도 카드·별도 gate 없이 주장할 수 없다 |
| **U2** | 회수의 **가치** | F-T16: target record 209 units ≈ 최대 19,200 coin 인데 그 경기의 패배 마진은 109,295 (최대 17.6%). baseline 6~7 units ≈ 520~600 coin. F-T17: 09-12 window 패배 마진 median 3,606~13,359, 전량 회수로 뒤집히는 경기는 EXP-006 기준 50판 중 1판 | 09-16 이후 window 의 마진 분포는 미측정(`N/A`, BOARD P1c). 따라서 "회수해도 순위가 오른다"는 **아직 근거 없음** |
| **U3** | in-day DROP 경로 | `shed_discarded_inday_drop` 은 gated 16 record 전부 0 | 이 13경기·이 tape 에 한정된 관측이다. 다른 tape·다른 전략에서 0 이라는 근거는 없다 |

## 3. `REPAIR_AUTHORIZED` 와 EXP-012 설계 가능성의 분리

- **카드상 판정:** `REPAIR_AUTHORIZED` 는 **성립한다.** 지배 class `ROOM_PARTIAL|REMOTE|NO_DEPOSIT_ATTEMPT` 가
  S1 64/64 = 1.0, S2 416/418 = 0.9952, record 별 단독 최다 16/16 으로 사전등록 임계(0.80 / 0.80 / 14)를 넘는다.
  이 값은 측정 당시 그대로 보존한다.
- **실제 설계 가능성:** **없다.** §D 가 이 class 에 허용한 one_change 는 `이월 순서/클램프 단일 지점` 인데,
  V4 가 그 경로의 총 손실 감소 효과가 **정확히 0** 임을 보였다. §E 최소 success 조건 2 는
  "gated 16 record 전부 `shed_discarded == 0`" 이므로, 허용된 변경 범위만으로는 **구조적으로 달성 불가능**하다.
- 따라서 카드의 라벨은 유지하되 **EXP-012 는 사전등록하지 않는다.** 억지 후보를 만들지 않는다.
- 이 repair 경로의 한계를 명시한다: `_drop_inventories_to_shed` 는 agent 가 호출하지도, 인자를 바꾸지도 못하는
  **엔진 내부 함수**다. 하루 마지막 턴에 agent 가 할 수 있는 것은 자기 unit action 과 market order 뿐이고,
  DROP·PLACE 로 미리 넣어도 `shed 점유 + carried` 총량은 보존되므로 EOD 손실
  `max(0, 총량 − shedCapacity)` 는 변하지 않는다. **총량을 줄이는 개입(매도·생산 조절)만이 손실을 줄인다**
  — 그것은 이 카드가 측정하지 않았고 §D 가 허용하지도 않은 다른 intervention 이다.

## 4. EXP-013 과의 분리 (요청 항목 5)

- EXP-011 의 모든 산출값(`share(C*, S1)`, `share(C*, S2)`, record 별 최다 class)은 **shed 소멸 단위의 속성에서만**
  계산된다(card §D-1 근거 2). 소멸 단위가 0 인 실패 양식에 대해 이 카드는 어떤 값도 내지 않는다.
- 따라서 **EXP-011 결과는 EXP-013(HYP-0032)의 효과 증거가 아니고 실행 승인도 아니다.**
  EXP-013 은 자기 근거(opening HIRE 부분 체결, target seat1 hands mismatch 46턴, 미충원 9명),
  자기 숫자 gate, 사람의 별도 승인을 갖춰야 한다(EXP-013 §G, BOARD C1).
- EXP-011 이 EXP-013 에 주는 사실은 **한 가지뿐이고 그것은 지지 증거가 아니다**:
  target 패배 마진 109,295 중 shed 손실의 coin 상한은 19,200(17.6%)이므로 **"shed 가 target 패배의 주 원인"
  이라는 해석은 배제된다.** 이는 shed 경로의 우선순위를 낮추는 근거이며, HIRE 경로가 옳다는 근거는 아니다.
  두 가설의 상대 가치는 아직 비교 측정되지 않았다.

## 5. 다음 행동 — 하나만

**제안: EXP-011 에서 검증된 무개입 계측 방법론을 `noop_actions` 3,488 의 coin 귀속에 재사용한다 (새 카드, 미승인).**

근거:

1. **도구가 이미 입증됐다.** EXP-011 은 계측 확장이 baseline 을 1비트도 바꾸지 않음을 16/16 record exact 로
   보였다(V1 mismatch 0). 같은 runner·같은 13경기·artifact 무변경이면 제출 위험 0 이다.
2. **shed 경로는 가치 상한이 닫혔다.** U2 로 회수 가치가 패배 마진 대비 한 자릿수 작다는 것이 확정됐고,
   A3 로 허용된 repair 범위의 효과가 0 이라는 것도 확정됐다.
3. **`noop_actions` 는 7.2배 크고 coin 귀속이 전무하다.** gated 16 record 합 3,488 이고
   op 분해는 이미 있다 — `CARE` 846 / `COLLECT_FERTILIZER` 668 / `FEED` 578 / `WATER` 556 / `HARVEST` 550 /
   `FERTILIZE` 106 / `PLACE` 102 / `PICKUP` 36 / `DROP` 30 / `DIG` 16 (합 3,488, 누락 0).
   **없는 것은 "왜 PASS 로 치환됐는가" 의 reason 과 그 coin 가치다.** shed 는 F-T16 에서 coin 상한이 나왔지만
   noop 는 `N/A` 다. 즉 다음 계측 1회가 메우는 정보량이 가장 크다.
4. 비용이 낮다: 카드 1장 + `tools/instrument.py` reason hook + 같은 13경기 재실행.

**이번에 하지 않은 것:** EXP-012·EXP-013 구현, 경기 실행, BOARD 변경, 제출. 전부 범위 밖이며 사람 승인이 선행한다.

**이 제안의 한계 (독립 검토자 지적 반영):**

- **coin 귀속 난이도가 shed 와 대칭이 아니다.** shed 는 소멸 단위가 곧 판매 가능 단위라 F-T16 처럼 실현 단가를 곱해
  상한이 바로 나온다. 반면 `CARE`·`FEED`·`WATER`·`HARVEST` 의 noop 은 "성공했다면 얼마였는가" 라는 **반사실 모델**이
  필요하다. 따라서 이 카드의 1차 산출물은 coin 이 아니라 **reason 귀속**(엔진이 어떤 조건에서 PASS 로 치환했는가)이어야
  하고, coin 은 reason 별로 상한이 계산 가능한 것에 한해 부차 산출물로 둔다. 카드 설계 시 이 순서를 명시한다.
- **대안과의 상대 가치는 비교되지 않았다.** F-T17 은 "더 큰 신호는 무승부 9판"(HYP-0006)이라고 적었고,
  HYP-0032(EXP-013 HIRE 경로)도 등록돼 있다. 이 제안은 **shed 경로 대비** 우위만 논증했을 뿐
  HYP-0006·HYP-0032 와의 우선순위 비교는 하지 않았다. 세 경로의 상대 가치 비교는 아직 `N/A` 이며,
  그 비교에 가장 직접적인 자료는 BOARD P1c(최신 hosted window 패배 마진 분포)다.

## 5.1 독립 검토 기록

이 판정문과 위 문서 변경 전체를 별도 세션의 독립 검토자가 재검증했다(2026-09-18, read-only).
V1~V6 을 인용하지 않고 원자료에서 직접 재계산한 결과:

- D1-c 26/26 player-record mismatch **0**, 13경기 전부 `steps=720` / `DONE,DONE`
- gated loss event **44**, 합 **482**, 항등식 실패 **0**, `carried<=room` 인 loss event **0**
- 순열 시뮬레이션 44 event × 200회 = **8,800 trial, 총 소멸량 불일치 0**
- DROP `del inv[item]` / PLACE `inv[item] -= n` 소스·fixture 확인
- 44/44 event 에서 shed 비 `PRODUCTS` 키(GOOSE/COW/SHEEP)가 전부 0, `sum(PRODUCTS) >= discarded_total`
- `git show HEAD:experiments/cards/EXP-011-...md` 의 sha256 = `8736d403…dd0e` (측정 당시 r2 보존 확인),
  현재 파일 = `f5783e40…4b13f` (r3), diff 는 **126 insertions / 1 deletion**(삭제된 1줄은 `미실행. N/A.` placeholder)
- `experiments/cards/EXP-013-state-conditioned-hire-recovery.md` sha256 = `dabe80a0…0cd9f` **불변**
- `coordination/BOARD.md` **변경 없음**
- `python3 tools/validate_hypotheses.py --strict` → `hypothesis ledger PASS: 32 entries`, exit 0
- `noop_by_op` 합 = 3,488 (= `noop_actions` 합)

**검토자 판정: 사실 오류 0건. 8개 주장 전부 참.** 지적 2건은 (1) BOARD 미반영 — 코디네이터 소유이므로 의도된 인계,
(2) 다음 행동 권고의 비교 범위가 좁고 noop coin 귀속 난이도가 shed 와 비대칭 — **위 "이 제안의 한계" 로 반영했다.**

## 6. 이번에 갱신한 owner 문서

| 경로 | 변경 |
|---|---|
| `experiments/cards/EXP-011-shed-discard-attribution.md` | **정정 이력 r3** 절 추가 + `## 결과` 절 기록. 측정 당시 card SHA `8736d403…dd0e`·임계·class 정의·층·seeds·좌석·상대·§E acceptance **전부 불변** |
| `evidence/FACTS.md` | F-T14 에 PLACE 정정 주석, **F-T20**(EXP-011 attribution 확정 + 순서 불변성), **F-T21**(매도 여력 상한) 신설 |
| `experiments/registry.csv` | EXP-011 행 추가 |
| `HYPOTHESES.md` | `tools/update_hypotheses.py` 로 HYP-0031·HYP-0032 event 기록 (직접 편집 없음) |
| `scratch/claude_exp011_owner_20260918/` | 재현 스크립트 3개 (read-only, 새 경기 생성 없음) |

`coordination/BOARD.md` 는 코디네이터 소유이므로 수정하지 않았다. BOARD 3·4행의 "독립 검토 대기" 는
이 문서로 해소되었으므로 코디네이터 반영을 요청한다.


---

## `reports/claude/20260918-EXP011-VERIFY-GUARD-ACCEPTANCE.md`

# Codex EXP-011 verify-only guard 인수 검토 (Claude, owner)

VERDICT: **ACCEPTED — guard 는 의도대로 동작한다.** 단 잔여 쓰기 경로 1개와 테스트 사각 1개가 남는다.
P1c 우선순위는 **확정하지 않는다.**

대상: 커밋 `35e9f45`, 보고 `coordination/reports/codex/20260918-P1C-AUDIT-VERIFY-GUARD.md`,
지시 `coordination/proposals/codex/20260918-P1C-GEMINI-CORRECTIONS.md`.
이번 작업에서 새 경기·candidate·카드 사전등록·EXP-013 구현/실행·제출은 **없다.**

## 1. 독립 재현 (owner, read-only)

| 항목 | 결과 |
|---|---|
| `pytest tests/test_exp011_verify_readonly.py tests/test_audit_p1c_replays.py -q` | **3 passed** |
| `python3 experiments/results/p1_shed_attribution/run.py --verify-only` | exit **1**, `INVALID INVALID checks 1603 class ROOM_PARTIAL\|REMOTE\|NO_DEPOSIT_ATTEMPT shares 1.0 0.9952153110047847 sole_top 16` |
| `aggregate.json` 전/후 | `22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba` / 동일 |
| `freeze.json` 전/후 | `654e0bbb28b4db2fcbf7e68de7a49c87004c7c62aba86be348ea84ffc3e68a84` / 동일 |
| `commands.json` 전/후 | `aa3a1db6508172713aa0a3e36e4d18997cbde8abb685ac78169f654566fc83b3` / 동일 |
| `allocation_audit.json` 전/후 | `66ed824393d41aaae507866f327f5f9ae8f8bfa7c46d7993b10e197e43011fa8` / 동일 |

코드 확인: `verify(*, persist=False)`, `write(ROOT/'aggregate.json', result)` 는 `if persist:` 아래,
`main()` 의 `--verify-only` 분기는 인자 없이 `verify()` 호출, batch 완료 경로만 `verify(persist=True)`.
→ **확인 1: verify-only 는 원본 `aggregate.json` 을 쓰지 않는다.**

## 2. live `INVALID` 의 정확한 원인 — provenance drift

`freeze.json['inputs']` 30개 중 **불일치 2개뿐**이다.

| input | expected (측정 당시) | actual (현재) |
|---|---|---|
| `experiments/cards/EXP-011-shed-discard-attribution.md` | `8736d403…` (r2) | 정정 이력(§G) 부착본 |
| `experiments/results/p1_shed_attribution/run.py` | `20547a4a…` | `883c4792…` (guard 적용) |

나머지 28개는 전부 일치한다 — 엔진 `kaggriculture.py`/`.json`, `tools/instrument.py`, tape 2종,
P1b parent 4파일·cells 13개, `manifest.json`, `commands.json`, `gate_contract.py`,
`tests/test_instrument_exp011.py`, 제출 tar, authorization 보고.
즉 **측정 데이터는 흐르지 않았고 문서·러너 SHA 만 흘렀다.** 깨진 gate 는 D1-a 하나이고 나머지 1602 check 는 통과한다.

→ **확인 2: 현재 card/runner 가 역사적 freeze 와 달라 live identity 검증은 INVALID 일 수 있다.**
→ **확인 3: 이는 보존된 역사적 EXP-011 결과의 무효화·덮어쓰기가 아니다.** `aggregate.json` 은 `22ebb927…` 그대로이고
판정 `PASS` / `REPAIR_AUTHORIZED`, 강도 S1 1.0 / S2 0.9952 / sole-top 16/16 도 그대로다.
→ **확인 4: freeze 와 측정 당시 SHA, 기존 결과·임계·판정을 유지한다.** `freeze.json` 을 현재 SHA 로 덮어쓰지 않는다.
원장·registry 인용 card SHA 는 r2 `8736d403…` 고정. r3/r4 정정 이력의 새 SHA 가 그것을 대체하지 않는다.

## 3. owner 문서 정정 (이번에 수행)

원 경고를 **삭제하지 않고** "수정 전 위험 / 수정 후 동작"으로 분리했다.

- `evidence/FACTS.md` F-T20 — (1) 수정 전 원문 인용 보존 (2) 수정 후 read-only 동작 + 재현 증거
  (3) live INVALID = provenance drift, 역사적 결과 불변 (4) 잔여 쓰기 경로.
- `experiments/cards/EXP-011-shed-discard-attribution.md` — §결과 재현 항목을 정정하고 §G 에 **C-7** 추가(r4).
  측정 판정·숫자·임계·class 정의는 불변.
- `HYPOTHESES.md` — HYP-0031 을 `tools/update_hypotheses.py` 로 갱신, `--strict` 통과.

## 4. 잔여 갭 (Codex 소유 경로 — 제안만)

1. **`experiments/results/p1_shed_attribution/check_allocation.py` 는 무보호다.** :35 에서 분기 없이
   `allocation_audit.json` 을 다시 쓴다. `run.py` guard 와 같은 read-only 기본값을 권한다.
2. **regression test 의 사각.** `tests/test_exp011_verify_readonly.py` 는 `verify()` 기본값만 본다.
   누군가 `main()` 의 `--verify-only` 분기를 `verify(persist=True)` 로 바꾸면 테스트는 통과한 채 회귀한다.
   `main()` 을 `--verify-only` 인자로 직접 호출하는 케이스를 추가할 것.
3. (참고) `coordination/proposals/codex/20260918-EXP011-ANTIGRAVITY-HANDOFF.md` 의
   "verify-only 는 aggregate 만 같은 값으로 다시 기록" 서술은 현재 동작과 다르다 — Codex 소유 문서라 수정하지 않았다.

## 5. P1c — 우선순위 미확정

Codex 재검산으로 Gemini 의 **HIRE 100% 실패 주장은 반박됐다** (W 0/24, D 0/1, L 3/52, 미체결 13건;
대표 사례 110024392 row2 는 hands 0→5 전부 성공). NOOP 100% 주장도 정의·정렬 재검증 전까지 보류다.
접전 4경기 마진은 0 / -10 / -92 / -422 이며 네 경기 모두 HIRE 미체결 0건 — 작은 마진은 개입 효과의 증거가 아니다.
표본 provenance 도 미확정이다 (`episodes_{ID}_filtered.json` 부재로 submission 별 46/31 과 24시간 window 재검증 불가).

→ **Gemini 정정 + 표본 provenance 확인 전까지 HIRE / noop / 접전 경로의 우선순위를 확정하지 않는다.**
EXP-013 미승인·미구현, EXP-014 예약, P2 / release zero gate FAIL 유지는 그대로다.


---

## `reports/claude/20260918-FASTLANE-AUTHORIZATION.md`

# 사용자 승인 기록 — K3 정정 + donor tape fast lane

기록: Claude (Coordinator 역할), 2026-09-18 ≈14:00 UTC. 사람이 아래 내용을 승인했다.

- (1) `20260918-K3-DONOR-FINAL-DECISION.md` §A-3 K3 정정(D-2 α) 승인.
- (2) `20260918-DONOR-TAPE-FASTLANE-PLAN.md` §3 fast lane을 §3-1 대상에 한해 2026-09-29까지 적용하고, §3-3 표의 AGENTS §7·§7.1·§7.4 및 BOARD P2 예외를 그 범위로 승인.
- (3) §4 단계 A–D 승인(상위 1–60위 replay 최대 180개 다운로드 포함).
- 각 hosted 제출은 사람이 직접 실행한다. §1-2 기준·§3-2 gate를 바꾸면 자동 진행하지 않고 사람에게 돌아온다.

승인 대상 문서 SHA-256:
- `coordination/proposals/claude/20260918-K3-DONOR-FINAL-DECISION.md` `466aca3f427fecb8424b6b31e4cb3d5c94d87cdd6e57d6341bf38bb1cec69598`
- `coordination/proposals/claude/20260918-DONOR-TAPE-FASTLANE-PLAN.md` `d7ca9eb44f24d1a26885eb0703caad911e572069ac611fce95050fff5557b24c`

## 이번에 적용한 것
- `coordination/BOARD.md`: 계획 §6 변경안 적용(머리 4줄, 현재 상태 4행, F0 행 추가, P2 행 범위 문구, 제출 운영 문단).
- `evidence/HOSTED_LEDGER.md`: yhay81-exact 재제출 submission ID **56330776** 기입(사람 제공).

## 적용하지 않은 것 (조건 대기)
- `evidence/KILLS.md` K3 행과 plan 두 줄: K3 결정안의 적용 조건(Antigravity §E 독립 검토 전 항목 PASS)이 남아 있다. 승인 문장 (1)은 문구를 승인했고, 그 문서가 정한 적용 순서는 유지한다. 그동안 fast lane 대상의 허용 근거는 이번 승인 (2)다.
- AGENTS.md 본문: 예외는 이 기록과 BOARD 로 범위를 명시했다. 본문 개정은 요청되지 않았다.
- 단계 A–D 실행: 아직 시작 전. Codex 작업 지시서가 다음이다. 단계 E 이후 제출은 사람이 건별로 실행한다.

## 후속 적용 2026-09-19
- 담당 재배정(사람 지시): 단순 자료 수집 = Antigravity, 판단·결정 = Codex. K3 독립 검토는 Codex 가 수행.
- Codex 독립 검토 `coordination/reports/codex/20260918-2348-K3-WORDING-REVIEW.md` (SHA `f888684288342e2ddf6096748b14da4d79f565e4e01b7c48306d21f534011f12`) — E1–E5 전 항목 PASS, SCOPE-FAIL 없음.
- 적용: `evidence/KILLS.md` K3 행을 결정안 §A-3 After 문구로 교체(날짜 칸 2026-09-18 기입 외 무변경, 적용 후 SHA `194afde839a2a9e27b69fa8a96c903d0169ac95b89391cff62ffb5683106ff04`). plan 두 파일 K3 행 마지막 칸에 정정 주석. BOARD 결론 절에 §B 문구.
- 방침 변경 기록: 2026-09-10 방침 "긁어온 라이벌 리플레이/테이프는 분석 입력으로만 쓰고 제출물에 넣지 않음"은 이번 fast lane 승인(2026-09-18)으로 §3-1 대상·09-29 까지 대체된다.
- F0 단계 A 완료(Antigravity 보고 `coordination/reports/antigravity/20260918-2354-F0-STAGE-A.md`). Claude 가 원자료에서 규칙을 독립 재계산: 상태 분포(eligible 81 / ambiguous 14 / ineligible 5)·1–60위 적격 52팀·선정 104 slot 의 episode ID 전부 일치, 불일치 0. 고유 episode 87개(두 donor 가 같은 경기에 나온 중복 17).

## 추가 사용자 승인 2026-09-19
> 승인: `20260919-F0-STAGE-B-RESULT-DECISION.md` §3 A를 채택한다. fast lane(§3-2 gate, 09-29까지)의 대상을 "09-16 이후 공개된 Kaggriculture notebook의 제출 코드를 수정 없이 재현한 artifact"로 넓힌다. 후보는 §3 A 표의 4개에서 시작하고, Codex가 재현·gate를 하며, 각 hosted 제출은 내가 직접 실행한다. 단계 C(6/6)는 대상 없음으로 종료한다.

대상 문서 SHA `34e642e5a2708d9ee68aa31130d3348b8308e859d96e9643cbc3f8c64e2a1c11`. 후속 지시서: `coordination/proposals/claude/20260919-F0-PUBLIC-EXACT-WORK-ORDER-CODEX.md`, `…-F0-PUBLIC-SOURCE-CHECK-ANTIGRAVITY.md`.


---

## `reports/claude/20260919-F0-LINEAGE-CHECK.md`

# F0 계보 분류 결과 확인 (Claude, Coordinator 역할)

1. **무엇:** Antigravity 계보 분류(`coordination/reports/antigravity/20260919-1438-F0-LINEAGE.md`, 결과 `analysis/lineage_20260919/`)의 통제 사례와 DIFFERENT 3개를 원자료로 재확인했다.
2. **왜:** 두 번째 슬롯을 P2 와 다른 가족에서 고르기 위해.
3. **결과:**
   - 통제 사례 7건 기대값 일치: P2 1.000/38/38, tetsutani 0.900/38/38, alperen 0.900/38/38, yhay81 0.005/13/13 → 모두 SAME_FAMILY. 공개 bot 3개 sim ≤ 0.011.
   - 추출 가능한 37개 중 **34개가 SAME_FAMILY**(P2 와 코드 또는 tape 공유). RELATED·AMBIGUOUS 0, UNKNOWN 4(외부 dataset 2, 추출 패턴 없음 2).
   - DIFFERENT 3개 원문 확인:
     - `hesoponyo/pure-rl-agent-bc-ppo-self-play` — BC+PPO 로 학습한 Transformer 정책, 가중치를 lzma+base85 로 내장, 순수 Python 추론(2,470줄). `kagg_native` import 는 try/except 선택 사항. 점수 주장 N/A.
     - `salemali7/kaggriculture-2900` — **단일 tape 720행** 재생 + 잡초 수리·선행 판매·hands 정렬(250줄). tape 가 719 가 아니라 720 이라 분류기의 tape 감지(719 고정)에서 빠졌다. Claude 가 직접 비교: P2 route 38개와 farmer+hands 일치 최대 0.4%, yhay81 13개와도 0.4% — **다른 tape 가 맞다.** 첫 턴 COW1·SHEEP4·MELON 씨앗 5 등. 수집본은 09-08 에도 있었다(오래된 tape 일 가능성).
     - `aasim2003/notebookb3a3ef21c3` — 처음부터 쓴 규칙 기반 agent(912줄, `math` 만 import). 시장 흡수 모델·일손 적극 고용 설계. 점수 주장 N/A.
   - 분류기 한계 1건: tape 길이를 719 로만 인식한다. 이번 분류 결과는 바뀌지 않았다(위 수동 비교).
4. **다음:** 세 후보 모두 hosted 강도 근거 없음. Codex 무수정 재현·gate 후 로컬 진단(P2 상대)으로 두 번째 슬롯 후보를 고를지 사람 결정.


---

## `reports/claude/20260920-0011-F0-DIFFERENT-LINEAGE.md`

# F0 다른 계보 공개 notebook 3개 exact gate·진단 결과 (Codex 중단 → Claude 이어서 실행)

**무엇을 바꾸거나 시험하는가:** P2(lynnsakurai) 가족과 코드·tape를 공유하지 않는 공개 notebook 3개(D1 hesoponyo BC+PPO 신경망, D2 salemali7 단일 tape 재생, D3 aasim2003 규칙 기반)를 exact 재현해 gate 22경기씩 돌리고, P2·yhay81-exact 상대로 로컬 진단했다.
**왜 하는가:** 공개 제출 코드 37개 중 34개가 P2 가족이라, 두 번째 활성 슬롯 후보를 찾으려면 다른 계보가 필요하다.
**무엇을 측정했고 결과가 어땠는가:** 세 후보 모두 gate PASS(22/22 완주, 예외 0, runtime 한도 내). 진단에서는 셋 다 P2·yhay81-exact 상대로 열세 — D1만 yhay81-exact 상대 2/20 승(CI 상한 0.326 < 0.5, 열세 판정), 나머지 5개 쌍은 전부 0/20.
**무엇이 막혀 있고 다음 행동은 무엇인가:** 제출은 금지 범위라 실행하지 않았다. 세 후보 모두 두 번째 슬롯 후보로 진단상 부적격(P2보다 전부 약함)이라, Claude는 이 세 후보를 F0 두 번째 슬롯 제안에서 제외할 것을 권한다. License 최종 판정과 `environment/LICENSES.md` 반영은 그 파일 소유자(Cowork)에게 넘긴다.

```
VERDICT: PASS_LOCAL_GATE, 두 번째 슬롯 후보로는 부적격(진단 열세) | D1/D2/D3 22/22 완주·예외 0; 진단 6쌍 중 5쌍 0/20, 1쌍 2/20 | 아래 tar SHA | engine 1.32.7 bc8a5487…653e | NEXT: 사람에게 "이 3개는 두 번째 슬롯 후보 아님" 보고, License 반영은 Cowork
```

## 0. 이어받기 사실

- 원 지시서: `coordination/proposals/claude/20260919-F0-DIFFERENT-LINEAGE-WORK-ORDER-CODEX.md` (수신 Codex)
- 이어받기 지시: `coordination/proposals/claude/20260919-F0-DIFFERENT-LINEAGE-RESUME-CLAUDE.md` (사람이 Codex 사용량 제한 중단을 확인하고 2026-09-19 Claude에게 지시)
- 소유권 예외: `tools/` `releases/` `experiments/results/`는 AGENTS §4상 Codex 소유이나, 이 작업 1건에 한해 사람이 Claude의 쓰기를 허용했다.
- Codex가 이어받기 시점까지 끝낸 것(디스크 확인, 다시 실행하지 않음):
  - `tools/build_public_exact.py`에 d1·d2·d3 빌더 추가 (미커밋, `git diff --stat` +151/−11)
  - D1/D2/D3 release 3개 + `manifest.json` (아래 SHA 표)
  - `experiments/results/f0_different_lineage_20260919/d1_vs_starter_seat0.json` (D1 vs starter seat0 10경기, macOS native)
- Claude가 이어서 실행한 것: 아래 §2 gate 잔여분(D1 seat1+self, D2 3종, D3 3종), 진단 6쌍, clean-room import 재확인, 요약 파일 2개, 이 보고서.

## 1. 실행 환경 확인 (§2-1)

- `uname -a`: Darwin arm64 (macOS native, Claude Code 셸 직접 실행) — Linux VM 경로 아님.
- 엔진: `kaggle-environments==1.32.7`. `kaggriculture.py` sha256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`, `kaggriculture.json` sha256 `a82c89c1a2315b93f39775d8e025471a01b738647c9772658368ee6b1b6f4867` — `environment/ENGINE_LOCK.md`와 **일치**. 멈추지 않고 진행.
- `.venv/bin/python` 사용, Python 3.13.14, CPU 8코어(`sysctl -n hw.ncpu`).
- D1 gate seat0(Codex 산출)과 Claude가 실행한 나머지는 같은 host family(macOS native)라 같은 표에 섞었다. Linux VM 실행분 없음.

## 2. 후보 · gate 결과

| # | notebook | tar 경로 | tar SHA-256 | 기대 SHA 일치 | gate | p99 ms (최대) | 후보 agent 누적 s (최대, player-episode) |
|---|---|---|---|---|---|---:|---:|
| D1 | hesoponyo `pure-rl-agent-bc-ppo-self-play` | `releases/public-hesoponyo-pure-rl-agent-bc-ppo-self-play-exact/submission.tar.gz` | `6fe16a8c1820ab69f5b4e8758982d6cb1c2ed0d74f4532d7bee386ffcd4e3f7c` | 기대값 없음(notebook에 미기재) — N/A | **PASS** | 285.95 | 166.70 |
| D2 | salemali7 `kaggriculture-2900` | `releases/public-salemali7-kaggriculture-2900-exact/submission.tar.gz` | `f1a8da39e253accff2915fae9f8d7d55d546071720803c0103e0865b0e78e262` | **불일치** — notebook 잔존 기대값 `f029…d19` vs 실제 원문 `main.py` `3b1c…8fe9`(`BLOCKED_SHA_MISMATCH` 기록, 원문 무수정 유지) | **PASS**(측정 계속, Codex 판단 유지) | 0.627 | 0.112 |
| D3 | aasim2003 `notebookb3a3ef21c3` | `releases/public-aasim2003-notebookb3a3ef21c3-exact/submission.tar.gz` | `e74d545c7725be665ca171ddc17d35facd73bd39f9af03dd37d2fc198cbfcf51` | 기대값 없음(notebook에 미기재) — N/A | **PASS** | 1.355 | 0.405 |

- **판정 기준(F0 계약)**: 22경기 모두 720 steps·DONE/DONE, 예외/ERROR 0, 에피소드 wall ≤ 960s, 후보 agent 누적 ≤ 623.2s/player-episode. 세 후보 모두 통과. 무음실패 counter는 §silent_failure_policy대로 기록만 하고 판정에서 제외.
- **D1 시간 위험 (기록만)**: Mac 턴 p99 최대 285.95ms(턴 한도 1000ms 대비 여유 약 3.5배). hosted vCPU 1.6은 Mac arm64보다 느릴 수 있다 — 새 기준을 만들지 않았고 사실만 기록한다.
- clean-room: 세 tar 모두 빈 폴더에서 `tar -xzf` → `import main` 성공, `callable(main.agent)` True. `tar -tzf`로 각 tar의 유일한 멤버가 `main.py`임을 확인.

### Silent-failure counter (기록 전용, 판정 제외)

| 후보 | noop | shed_discarded | shed_unsold | orders_truncated | sell_unfilled | buy_failed | hire_failed | seed_blocked | hands mismatch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 hesoponyo | 982 | 131 | 343 | 0 | 0 | 4 | 0 | 0 | 0 |
| D2 salemali7 | 17,761 | 0 | 0 | 0 | 7,219 | 152 | 4 | 72 | 0 |
| D3 aasim2003 | 3,265 | 2,800 | 22 | 0 | 537 | 0 | 0 | 0 | 0 |

## 3. 진단 결과 `[LOCAL]` (판정 아님, seed 2000–2009 좌석 교대, 쌍당 20경기, seed 추가 없음)

| A | B | A W/D/L | A score | A CI95 | mean margin |
|---|---|---:|---:|---|---:|
| D1 hesoponyo | P2 lynnsakurai | 0/0/20 | 0.0000 | [0.000, 0.000] | −45,163.3 |
| D1 hesoponyo | yhay81-exact | 2/0/18 | 0.1000 | [−0.126, 0.326] | −35,783.4 |
| D2 salemali7 | P2 lynnsakurai | 0/0/20 | 0.0000 | [0.000, 0.000] | −31,317.9 |
| D2 salemali7 | yhay81-exact | 0/0/20 | 0.0000 | [0.000, 0.000] | −23,840.7 |
| D3 aasim2003 | P2 lynnsakurai | 0/0/20 | 0.0000 | [0.000, 0.000] | −83,555.6 |
| D3 aasim2003 | yhay81-exact | 0/0/20 | 0.0000 | [0.000, 0.000] | −79,868.4 |

에러 6쌍 모두 0. **세 후보 모두 P2·yhay81-exact 양쪽에 열세다.** D1만 yhay81-exact 상대 2승을 냈지만 CI 상한(0.326)이 0.5 미만이라 여전히 열세 판정. `[LOCAL]` 결과일 뿐 hosted 강도나 제출 승인을 뜻하지 않는다.

## 4. Exact 재현·검증 자료

- 공통 builder: `tools/build_public_exact.py` (Codex가 이어받기 전 d1·d2·d3 추가, 미커밋)
- gate 정본: `experiments/results/f0_different_lineage_20260919/gate_summary.json`
- 진단 정본: `experiments/results/f0_different_lineage_20260919/diagnostic_summary.json`
- raw gate JSON 9개(D1 seat0은 Codex 산출, 나머지 8개는 Claude 산출) + raw 진단 JSON 6개: 같은 디렉터리
- manifest: 각 release 디렉터리의 `manifest.json`

실행한 핵심 명령(Claude 실행분):

```bash
# gate 잔여분 — 한 번에 하나씩 순차 실행
.venv/bin/python tools/instrument.py --a starter --b <D1> --seeds 1000..1009 --time-agent b --gate-agent b --json starter_vs_d1_seat1.json
.venv/bin/python tools/instrument.py --a <D1> --b <D1> --seeds 1000 1001 --time-agent both --gate-agent both --json d1_self.json
.venv/bin/python tools/instrument.py --a <D2> --b starter --seeds 1000..1009 --time-agent a --gate-agent a --json d2_vs_starter_seat0.json
.venv/bin/python tools/instrument.py --a starter --b <D2> --seeds 1000..1009 --time-agent b --gate-agent b --json starter_vs_d2_seat1.json
.venv/bin/python tools/instrument.py --a <D2> --b <D2> --seeds 1000 1001 --time-agent both --gate-agent both --json d2_self.json
.venv/bin/python tools/instrument.py --a <D3> --b starter --seeds 1000..1009 --time-agent a --gate-agent a --json d3_vs_starter_seat0.json
.venv/bin/python tools/instrument.py --a starter --b <D3> --seeds 1000..1009 --time-agent b --gate-agent b --json starter_vs_d3_seat1.json
.venv/bin/python tools/instrument.py --a <D3> --b <D3> --seeds 1000 1001 --time-agent both --gate-agent both --json d3_self.json

# 진단 — 병렬 실행
.venv/bin/python tools/arena.py --a <D> --b <상대> --seeds 10 --seed-start 2000 --json diag_<d>_vs_<상대>.json   # 6쌍

# clean-room
tar -tzf <tar>            # main.py만 있는지 확인
tar -xzf <tar> -C <tmp>
(cd <tmp> && python3 -c "import main; print(callable(main.agent), main.agent.__name__)")
```

## 5. 경계 (원 지시서 §3 + 이어받기 문서 §3 준수)

- Kaggle 제출: 실행하지 않음
- 원문·builder·release 파일 수정: 없음 (D2의 SHA 불일치도 원문 그대로 두고 측정만 함)
- 추가 다운로드: 없음
- `BOARD.md`, `KILLS.md`, 실험 card, `HYPOTHESES.md` 직접 편집: 없음
- seed·gate 기준 변경: 없음
- `experiments/results/f0_latest_rebuild_20260919/`(취소된 작업 잔여물): 건드리지 않음
- 커밋: **하지 않음.** Codex의 미커밋 builder 변경(`tools/build_public_exact.py`)과 Claude가 추가한 gate/진단 산출물이 현재 워킹트리에 섞여 있다 — 커밋 시점과 방식은 사람/Codex 판단으로 남긴다.

## 6. License (판정 참고용, `environment/LICENSES.md` 반영은 Cowork 소유)

세 tar 모두 archive 안에 별도 license 파일 없음(`manifest.json`의 `license.archive_license_file: false`). 본문에도 별도 라이선스 문구가 없어(`source_notice`: "No separate license notice was found") 기존 P3 tetsutani 처리(`environment/LICENSES.md:22`, Kaggle Rules §7.b OSI 라이선스 간주)와 같은 유형으로 판단한다. **이 판단은 참고용이며, `environment/LICENSES.md`는 Cowork 소유라 Claude가 직접 쓰지 않는다.**

## 7. 다음 행동 제안

1. D1/D2/D3 세 후보 모두 진단상 P2·yhay81-exact에 열세 — **두 번째 활성 슬롯 후보로 제안하지 않는다.**
2. Cowork에게 License 판정(§6) 반영 요청.
3. 다른 계보 탐색을 계속할지, 아니면 P2 가족 내에서 두 번째 슬롯을 찾을지는 사람 결정 필요(§7.4 "활성 슬롯 2개는 서로 다른 두 전략" 조항 참고).

## 가설 원장

```bash
python3 tools/update_hypotheses.py --agent claude --hypothesis-id HYP-0028 --test-id TEST-DONOR-ROUTES-20260917 --reason "F0 different-lineage gate/diag (resumed from Codex)" --set "다음 행동=외부 점수는 COMMUNITY로 두고 우리 submission ID로만 승격 + coordination/reports/claude/20260920-0011-F0-DIFFERENT-LINEAGE.md"
python3 tools/validate_hypotheses.py --strict
```

- event: `coordination/hypotheses/claude/EVT-2026-09-19T151422.483915+0000-f4d9078e.json`
- validation: `hypothesis ledger PASS: 32 entries` (exit 0)
- 상태·결과 칸: 변경하지 않음 (LOCAL_SUPPORTED 유지)


---

## `reports/claude/20260920-0114-P2-LOSS-ANALYSIS.md`

# 20260920-P2-LOSS-ANALYSIS (Claude)

1. **무엇을 바꾸거나 시험하는가**
   무엇도 바꾸지 않는다. P2(56347732) hosted 패배·무승부 32판(A)과 대조 승리 32판(B)의 replay 원자료를
   같은 코드로 요약해 "질 때만 자주 생기는 일"을 빈도로 세었다. 경기 재실행 없음, `tools/` 수정 없음.
2. **왜 하는가**
   동메달 여유가 09-19 기준 +2.7점뿐이라, P2 위에 얹을 개선 1–2개를 근거 있게 고르기 위해서다
   (`coordination/proposals/claude/20260920-P2-LOSS-ANALYSIS-CLAUDE.md`).
3. **무엇을 측정했고 결과가 어땠는가**
   `[HOSTED]` A 32판(L25·D7) vs B 32판(대조 승리) 65개 필드 비교. **문턱(A≥20%, A−B≥20%p)을 넘는
   후보 원인이 하나도 없었다 → 결론 "없음".** 근접 신호(15.6%p, 문턱 미달)와 반대 방향 신호(YARN_STORE)는
   §3에 기록. 상세는 아래.
4. **무엇이 막혀 있고 다음 행동은 무엇인가**
   막힌 것 없음(BLOCKED 아님). `failed_orders` 필드 1개만 정의상 계산 불가로 N/A 처리(§1.4, 사유 명시).
   다음 행동: 사람 결정 대기 — ①이 결과를 그대로 받아들이고 P2 개선 없이 다른 경로(F0 donor tape 등)에
   집중, 또는 ②표본을 넓히거나(A/B 각 32→더 많이) 다른 필드 정의를 사람이 추가 지시.

VERDICT | A(L+D)=32·B(W)=32, 문턱 통과 후보 0개 → "없음" | manifest.json SHA 09b5786f…dabee0 (antigravity 보고와 일치, 재계산 확인) | features.csv 64행 전수 계산 + postmortem_hosted.py 64회 실행(원문 그대로) + agg_features.py 로 A/B 대조 | NEXT ACTION: 사람이 "없음" 결론을 받아들일지, 표본 확대/필드 추가를 지시할지 결정

---

## 0. 시작 전 점검

- `[OFFICIAL]` `coordination/BOARD.md` 갱신 2026-09-18 23:00 KST, 확인 시각 2026-09-20 00:56 KST → 약 26시간, 2일 미만이라 그대로 진행. `HYPOTHESES.md`(HYP-0027·HYP-0028·HYP-0029), `evidence/FACTS.md`·`evidence/KILLS.md` 확인 — P2(56347732) 관련 기존 FACT/KILL 없음(신규 작업).
- **SHA 재계산**:
  - `analysis/p2_losses_20260920/manifest.json` → `09b5786fc95392d603d7fb20ba080c757da8116ed02af6f9803a9bbae7dabee0` — antigravity 보고(`coordination/reports/antigravity/20260920-0047-P2-LOSS-COLLECTION.md`)의 VERDICT 줄과 **정확히 일치**. 재현: `python3 -c "import hashlib;print(hashlib.sha256(open('analysis/p2_losses_20260920/manifest.json','rb').read()).hexdigest())"`
  - `analysis/p2_losses_20260920/selection.json` → `04eeadba617ff273369c145641c135964c394a596e878744308a95be7642bf63` — **antigravity 보고에는 selection.json 자체의 SHA가 별도로 적혀 있지 않다** (`file_hashes.json`도 raw replay 64개 해시만 담고 selection.json·manifest.json 자신은 포함하지 않음, git 이력도 `analysis/`가 untracked라 없음). 따라서 "불일치"가 아니라 "대조할 기준값이 없음"이며, 대조 가능한 유일한 값(manifest.json)이 일치하므로 **멈추지 않고 진행**. 이 판단 자체를 투명하게 남긴다.
- 실행 환경: `mcp__remote-devices__device_bash`는 사용자 Mac에 마운트된 리눅스 VM이라 `.venv/bin/python`이 깨진 심볼릭 링크(macOS Python.framework 경로)였다 → 제안서 지침대로 표준 `python3`(3.10.12) 사용.

## 1. 경기별 요약

- `tools/postmortem_hosted.py --replay <raw> --team Sian --output evidence/raw/p2_losses_20260920/postmortem/<episode>.json` 를 64개 replay 전부에 무수정 실행. 에러 0건(`evidence/raw/p2_losses_20260920/postmortem_run_errors.log` 비어있음).
- `evidence/raw/p2_losses_20260920/compute_features.py`(신규, `tools/` 밖) 로 features.csv 64행 계산. 재현: `cd` 리포 루트, `python3 evidence/raw/p2_losses_20260920/compute_features.py`.
- **오프셋 규약 검증**: replay의 `steps[i]['action']`은 `steps[i-1]['observation']`을 보고 결정되어 `steps[i]['observation']`을 만든다(양방향 아님). episode 110875333 steps 0-3 에서 WHEAT/hands/COW·SHEEP 증감이 이 규약 하에 요청량과 **정확히** 일치함을 직접 대조해 확인(`sed -n` 대신 위 파이썬 스니펫으로 재현, 리포 안 저장 스크립트 없음 — 필요시 요청).
- **필드별 계산 방법과 한계**:
  - `result`,`margin`: manifest `result` + `rewards[target]-rewards[opponent]`.
  - `div_day`: `tools/postmortem_hosted.py`의 `daily_curve`/`durable_loss_day`(`:30-56`)와 같은 공식(`bank()`)을 쓰되, **양방향**(P2가 유리하게 5,000+ 벌어져 유지되는 경우도 포함)으로 내가 별도로 계산(`tools/` 미수정, features.csv 산출용 로직만 별도 파일에 작성). 단방향(패배쪽)만 보는 `durable_loss_day`와 교차검증(episode 110872851: 둘 다 day=23) 일치.
  - `route_at_144`: `releases/public-lynnsakurai-farming-score-v2-exact/main.py:732-736`의 라우터 코드(`step>=144`일 때 `unlocked_shops[:2]`를 키로 라우트 결정)를 그대로 재현 — step index 144의 관측값.
  - `opp_is_clone`: turn 1–143(포함) 구간에서 `(farmer,hands)` 튜플 일치 비율 ≥0.9.
  - `hands_d2`,`hands_d6`: `tools/postmortem_hosted.py`의 day 인덱스 규약(day d → step (d+1)*24-1)을 그대로 따름 — "2일차"=day index1=step47, "6일차"=day index5=step143.
  - `min_cash_d1_7`: step 0–167(1–7일차) 구간 최저 money.
  - `sell_units_by_item`,`sell_revenue_by_item`: 매 턴 `market` 배열을 기록 순서대로 처리(BUY_PRODUCT/BUY_ANIMAL 증가 → SELL을 그 시점 shed 잔량에 clamp)하고, 같은 턴의 DROP(직전 관측된 actor inventory 전량)·PLACE(명시 수량)·PICKUP(shed→inventory, 기본 1개) 을 shed 증감에 반영. **한계**: 하루 경계(hour=0)에 원인 불명의 자동 생산/입고가 있어(동물·작물 산출로 추정, 엔진 소스 미확인) shed 델타의 평균 6.4%(중앙값 6.4%, 최대 8.3%, 표본 64경기) 턴이 위 모델과 재현되지 않는다(`compute_features.py`의 `notes` 컬럼에 경기별 `sell_reconciliation_mismatch_turns` 기록). 이 오차는 A·B 양쪽에 비슷한 비율로 나타나(계측만 했을 뿐 승패와 상관 짓지 않음) **상대 비교(§2)를 무효화할 정도는 아니라고 판단**하되, 절대값은 근사치로 취급한다.
  - `animals_final`: 최종 step에서 P2/상대 tile 중 `tile['animal']`이 COW/SHEEP/GOOSE인 개수.
  - `shed_full_days`: 하루 24턴 중 한 번이라도 P2 shed 총합(`sum(shed.values())`)이 100(cap) 이상인 날의 수.
  - `failed_orders`: **N/A** (전 경기 공통). 이유 — BUY_SEED/BUY_PRODUCT/BUY_ANIMAL 의 실제 체결 여부는 같은 턴의 PLANT(씨앗 소모)·SELL(같은 품목)·PLACE/DROP/PICKUP(shed 증감)·shed cap(100) 초과 소멸과 얽혀 있고, 이를 안전하게 분리하려면 엔진의 턴 내부 실행 순서를 재구현(=사실상 재실행)해야 한다. 이 작업은 "경기 재실행 없음" 제약과 상충하므로 정의를 바꾸지 않고 N/A로 둔다. (HIRE·BUY_LAND만은 다른 연산과 간섭이 없어 원칙적으로 분리 가능하지만, 지시된 필드 정의가 "BUY/HIRE 주문 수" 하나로 묶여 있어 일부만 계산해 정의를 바꾸지 않기로 했다.)
- 산출물: `evidence/raw/p2_losses_20260920/features.csv`(64행), `evidence/raw/p2_losses_20260920/postmortem/*.json`(64개), `evidence/raw/p2_losses_20260920/compute_features.py`, `evidence/raw/p2_losses_20260920/agg_features.py`(집계 스크립트, 재현용).

## 2. 집계 — 빈도와 대조 (A n=32, B n=32, Wilson 95% CI)

| 필드(이진화) | A 비율 | B 비율 | A−B | 문턱(≥20%p·A≥20%) 통과? |
|---|---|---|---|---|
| `opp_is_clone`(turn1-143 same-action≥0.9) | 30/32=93.8% [79.9,98.3] | 30/32=93.8% [79.9,98.3] | 0.0pp | 아니오 |
| durable divergence **against P2**(div_day 존재·margin<0) | 5/32=15.6% [6.9,31.8] | 0/32=0.0% [0.0,10.7] | **+15.6pp** | 아니오 (A<20%, 문턱 미달) |
| durable divergence **P2 유리**(div_day 존재·margin>0) | 0/32=0.0% | 3/32=9.4% [3.2,24.2] | −9.4pp | 아니오(방향 반대) |
| any durable divergence(방향 무관) | 5/32=15.6% | 3/32=9.4% | +6.3pp | 아니오 |
| `shed_full_days`≥1(창고 100 도달 최소 1일) | 31/32=96.9% [84.3,99.4] | 30/32=93.8% [79.9,98.3] | +3.1pp | 아니오(양쪽 다 거의 보편적) |
| `route_at_144`에 YARN_STORE 포함(참고용, §1 필드의 자연스러운 하위 지표) | 4/32=12.5% [5.0,28.1] | 11/32=34.4% [20.4,51.7] | **−21.9pp** | 아니오(방향이 반대 — A가 아니라 B에서 더 자주 나타남. "질 때만 자주"의 정의를 만족 못 함) |
| `min_cash_d1_7`≤0 | 0/32=0.0% | 0/32=0.0% | 0.0pp | 아니오(양쪽 다 0, 표본에 바닥난 경우 없음) |
| `hands_d2`≤2 / `hands_d6`≤3 | 0/32=0.0% (둘 다) | 0/32=0.0% (둘 다) | 0.0pp | 아니오(바닥 효과, 정보 없음) |

**연속형 분포(중앙값, A vs B)** — 참고용, 위 표의 이진 문턱 판정 대상 아님(비율 아님):
`margin`: A −1057.5 vs B +1289.5(정의상 당연/결과의 재서술). `hands_d2`: 3 vs 3. `hands_d6`: 4 vs 4. `min_cash_d1_7`: 7 vs 7. `shed_full_days` 중앙값: 5 vs 5. `animals_final`(P2) 중앙값 COW: A 8 vs B 6, SHEEP: 6 vs 6, GOOSE: 3 vs 3(COW만 근소한 차이, 이진 문턱 대상 아니고 승패 방향과 직관적으로 맞지 않아 추가 조사 없이 참고만 함).

**`route_at_144` 상세**: 64경기에서 서로 다른 상점 쌍 35종, 표본이 5경기 이상인 쌍이 **하나도 없음**(최다 4경기: `BRUNCH_SPOT|ICE_CREAM_SHOP` A1/B3, `BRUNCH_SPOT|BRUNCH_SPOT` A0/B4). 제안서 지침대로 5경기 미만은 전부 `OTHER(<5)`로 묶으면 A=B=32(전부)가 되어 원 필드로는 판정 불가 — YARN_STORE 유무만 별도로 봤다(위 표, 방향 반대로 문턱 미달).

**상대별 패배 수 상위 10팀**: 표본 64경기에서 **서로 다른 상대 31명**(A32판 중 31명, B32판 중 31명) — 한 상대에게 반복 패배하는 패턴 없음. 최다: `Sankalp Wanjari` 2패(표본 내 이 상대와 총 2경기, 즉 2전 2패), 나머지는 전부 1패씩(그 상대와 표본 내 1~2경기). 반복 패배 신호 없음.

**같은 상대 매칭 쌍 비교**(`same_opponent_match=True`, n=2, 별도 표):

| A(패배/무승부) | 상대 | A margin | B(대조 승리) | B margin |
|---|---|---|---|---|
| 110852721 | spbforce | 0.0(D) | 110784235 | +38.0 |
| 110747001 | BraydenPikachu | −706.0 | 110730549 | +1808.0 |

표본 2쌍뿐이라 패턴 판정 불가(참고용).

## 3. 결론

**후보 원인 최대 2개 중 문턱을 넘는 것: 0개 → "없음".**

- §2에서 시도한 8개 이진 지표(opp_is_clone, 방향별 durable divergence 3종, shed_full_days≥1, YARN_STORE 포함, min_cash≤0, hands 저치) 중 어느 것도 "A≥20% 이고 A−B≥20%p" 문턱을 넘지 못했다.
- 가장 근접했던 신호: **durable divergence against P2**(A 15.6% vs B 0%, +15.6pp) — 문턱(20%p)에 4.4pp 못 미치고 A 비율 자체도 20% 미만이라 기준 미달. 대표 경기 5개(episode/div_day/opp): 110872851(day23,PUN,margin−7669), 110859631(day24,nilochan,margin−8403), 110856483(day29,Aamod06,margin−5567), 110832351(day29,Ömer Faruk Yüce,margin−5455), 110754582(day19,Odyssey,margin−15218) — postmortem 인용: `evidence/raw/p2_losses_20260920/postmortem/110872851.json`의 `durable_loss_day={"threshold":5000,"day":23,"step":575,"gap":-5245.0}`.
- 방향이 반대로 나온 신호(참고, 원인 후보 아님): `route_at_144`에 YARN_STORE가 포함되면 오히려 **B(승리)에서 더 자주**(34.4% vs 15.6%) 나타났다 — "질 때만 자주"의 정의를 만족하지 않으므로 후보에서 제외.
- **문턱을 넘는 것이 없으므로 §3.2의 1-change 개선 초안은 작성하지 않는다.** 억지로 만들지 않는다(제안서 §3 지침).
- `opp_is_clone`(93.8% 대 93.8%)·`shed_full_days≥1`(96.9% 대 93.8%)처럼 A·B 양쪽에서 **거의 동일하게 보편적**인 현상은 P2의 구조적 특성(상대 대부분이 유사 tape를 쓰고, 창고가 자주 꽉 참)이지 승패를 가르는 요인이 아니라는 뜻으로 읽힌다 — 이 자체가 하나의 결론(개선 우선순위를 다른 곳에 둬야 함을 시사)이라 §4 원장에 남긴다.

## 4. 원장 갱신 및 검증

- 실행: `python3 tools/update_hypotheses.py --agent claude --hypothesis-id HYP-0028 --test-id TEST-DONOR-ROUTES-20260917 --reason "P2 hosted loss analysis" --set "다음 행동=외부 점수는 COMMUNITY로 두고 우리 submission ID로만 승격 + coordination/reports/codex/20260919-1221-F0-PUBLIC-EXACT.md + coordination/reports/codex/20260919-1332-F0-LATEST-REBUILD.md + coordination/reports/claude/20260920-0011-F0-DIFFERENT-LINEAGE.md + coordination/reports/claude/20260920-0114-P2-LOSS-ANALYSIS.md"`
  결과: `hypothesis update PASS: HYP-0028 -> coordination/hypotheses/claude/EVT-2026-09-19T161840.607645+0000-e45abf5b.json`
- 실행: `python3 tools/validate_hypotheses.py --strict` → 결과: `hypothesis ledger PASS: 32 entries` (exit 0).
- **환경 메모**: `coordination/hypotheses/.update.lock`이 이전 실행에서 남아 있었는데, 이 세션의 device-bridge 마운트가 처음엔 파일 삭제(unlink) 권한이 없어(`Operation not permitted`) 막혀 있었다. 사용자 승인으로 이 폴더의 삭제 권한을 받은 뒤 잠금 파일을 지우고 재실행해 통과시켰다. `tools/`는 수정하지 않았다(환경 권한 문제였을 뿐 코드 문제 아님).

## 5. 금지 사항 준수 확인

경기 실행 없음(replay JSON만 읽음) · `tools/` 코드 수정 없음(신규 스크립트는 `evidence/raw/` 아래) · 제출 없음 · 추가 다운로드 없음 · BOARD·KILLS 편집 없음 · §1/§2의 항목 정의·문턱을 결과 확인 후 바꾸지 않음(모두 사전에 고정된 정의로 계산 후 판정) · 새 가설 ID 배정 없음(사람 승인 전).


---

## `reports/claude/20260920-0950-F0-LIVE-CLAIM-VARIANTS.md`

# F0 live-claim 변형 2개(V1 melon squeeze, V2 2820-score) exact 재현·gate·진단 결과

**무엇을 바꾸거나 시험했는가:** 작성자가 실제 ladder 점수를 밝힌 P2 가족 최신 공개 notebook 2개(V1 goodpjw2008 "2749", V2 seyitkaangunes "2820")를 한 글자도 바꾸지 않고 deterministic tar 로 재현했다. 후보마다 고정 22경기 gate 를 돌리고, 고정 seed 2000–2009(좌석 교대, 쌍당 20경기)로 각 후보 vs P2, 각 후보 vs P1 alperen, V1 vs V2 를 진단했다.
**왜 하는가:** P2 는 2421.6(09-19)로 동메달 경계와 몇 점 차이라 더 강한 후보가 필요하다. 표적 수정보다 더 강해 보이는 최신 변형을 그대로 hosted 에 올려 비교하는 쪽이 먼저다(지시서 근거).
**무엇을 측정했고 결과가 어땠는가:** 두 후보 모두 gate 6줄 중 제출 전 5줄 PASS(22/22 완주·예외 0·runtime 한도의 0.5% 미만). 진단에서는 **V1·V2 둘 다 P2 를 한 판도 못 이겼다**(0/20, 0/20; 평균 마진 −2,353 / −1,487). P1 alperen 에도 V1 0/20, V2 2/18. V1 vs V2 는 14/0/6 (V1 우세, CI 하한 0.354 < 0.5 라 arena 판정은 INCONCLUSIVE). 모든 쌍에서 두 좌석 결과가 코인 단위로 동일해서 20경기 = 독립 10 seed 다.
**무엇이 막혀 있고 다음 행동은 무엇인가:** 제출·커밋·원문 수정은 하지 않았다. 아래 두 가지가 코디네이터 판단을 기다린다. (1) V2 notebook 기본값(`USE_CADENCE=True`, 4-layer)은 작성자가 "2801" 이라고 밝힌 build 가 **아니다**(2801 은 3-layer=`USE_CADENCE=False`, 4-layer 는 "4시간 후 2389, 아직 상승 중"). 지시대로 기본값을 유지했다. (2) `tools/instrument.py` 는 경로를 받으면 module `agent` 를 시험하는데 P2·V2 처럼 이것이 Kaggle 이 실제 부르는 entry point(last callable)와 **다른 객체**인 release 가 있다(§4). 그래서 이번 gate 는 last callable 로 돌렸다.

```
VERDICT: PASS_LOCAL_GATE (V1·V2 각 22/22, 제출 전 5줄 PASS·License 는 Claude 판정 대기) ; 진단은 P2 열세 | 핵심: ① V1/V2 vs P2 = 0/20·0/20 (마진 −2353/−1487, 은행 대비 2.5%/1.5%) ② V2 default 는 4-layer, 작성자의 2801 은 3-layer | 아래 tar SHA | engine 1.32.7 bc8a5487…653e | NEXT: Claude License 판정·제출 순서 제안, V2 3-layer(USE_CADENCE=False) exact 빌드 여부 결정
```

## 1. 결과 표 (지시서 §3 형식)

| 후보 | tar SHA-256 | 기대 SHA (main.py) | gate | p99 ms | vs P2 (W/D/L, 마진) | vs P1 alperen (W/D/L, 마진) | V1 vs V2 |
|---|---|---|---|---:|---|---|---|
| V1 goodpjw2008 melon-threshold-squeeze-2749 | `cfdd7f6c9513155b960776311c7a12bd73ff2146f8f56498646ccfbcb2e27f63` | `1f5c7a18035e522ee91f10674e0007ceaebe8e523f2fe9440324d27d6525fd49` — **일치** (build cell 이 print 하는 값; assert 아님) | PASS 22/22 | 3.633 | 0/0/20, −2,353 | 0/0/20, −2,523 | V1 14/0/6, +595 (점수 0.700, 95% CI 0.354–1.046, arena 판정 INCONCLUSIVE) |
| V2 seyitkaangunes kaggriculture-2820-score (기본값 `USE_CADENCE=True`) | `f623578bdd7e62558626d4fdcc332060f8db1d1b06ee4e1ce34ff72ca82a9114` | `fa9e47d81de5020847c1dbc7ca10d058b227be66deea7c019040fb12a1d99f19` — **일치** (cell-14 활성 assert, 통과) | PASS 22/22 | 4.680 | 0/0/20, −1,487 | 2/0/18, −738 (점수 0.100, CI −0.126–0.326) | V2 6/0/14, −595 |

- `STALE_EXPECTATION` 없음. 원문 notebook SHA 는 지시서 값과 일치했다(`ae34db0e…6eed`, `09d9833a…3be4`, 작업 전후 동일).
- P2 = `releases/public-lynnsakurai-farming-score-v2-exact/main.py`(지시서가 지정한 09-19 exact, 이 파일은 last callable `_e336_agent`), P1 = `releases/public-alperen-before-dawn-stock-cash-sales-exact/main.py`. 최신 P2(`…-v2-latest-exact`)는 지시서 범위 밖이라 쓰지 않았다.
- 진단은 arena 가 경로 문자열로 `env.run` 하므로 Kaggle 과 같은 last callable 로 실행된다.
- `p99 ms` = 후보 player 의 episode 별 p99 최댓값(22경기 중 최대).

## 2. 재현(Identity) — 무엇을 어떻게 만들었나

| | V1 | V2 |
|---|---|---|
| 원문 | `docs/collection_snapshots/kaggriculture-melon-threshold-squeeze-2749/…ipynb` | `docs/collection_snapshots/kaggriculture-2820-score/…ipynb` |
| main.py 생성 방식 | code cell `a1635dde-7dda-456e-a8ae-fa27b23b28bc` 의 `%%writefile main.py` 본문을 verbatim | notebook 자체 셀 `cell-04`(V44 base blob 복원+assert) 와 `cell-14`(build+assert)를 **무수정 exec**, layer 4개(`cell-06/08/10/12`)는 `%%writefile` 만 흉내 |
| 설정 분기 | 없음 | notebook 기본값 그대로: `USE_CADENCE=True`, `EXTRA_LAYERS=[]`, `VERIFY_LIVE_SHA=True` (manifest `build_details.v2_build.notebook_defaults` 에 기록) |
| main.py SHA / 크기 | `1f5c7a18…fd49` / 338,273 B | `fa9e47d8…9f19` / 352,588 B (V44 base `797d9bca…4e2f` 327,314 B + layer 1·2·3·4) |
| entry point (last callable) | `agent` | `_y_agent_shopherd` (module `agent` 는 별개 객체) |
| tar | 멤버 `main.py` 1개, PAX_FORMAT, `GzipFile(mtime=0)`, uid/gid 0, mode 0644 | 동일 |

- **tar SHA 는 우리 builder 정의**다. 두 notebook 이 만드는 `tarfile.open('submission.tar.gz','w:gz')` 는 파일시스템 mtime·uid 가 들어가 매번 다른 SHA 이므로 작성자가 올린 tar 와 바이트 비교는 불가능하고, main.py SHA 가 동일성의 기준이다.
- **결정론:** `tools/build_public_exact.py` 를 독립 출력 dir 두 곳(A/B)과 release dir 에 각각 빌드 → 세 tar SHA 동일, manifest 도 A==B(V2 는 임시 경로·notebook 자체 tar 크기를 stdout 에서 지워 manifest 가 결정론적). runner 의 `identity` 단계가 A/B 를 다시 빌드해 같은 SHA 임을 `identity_summary.json` 에 기록했다.
- **V2 주의:** notebook TL;DR 의 "2801 rating, rank ≈188 (09-16 스냅샷)" 은 **3-layer**(V44+layers 1,2,4, submission 56277542, main SHA `016b9a32…3fe7`) 이다. 기본값 4-layer(V44+1,2,3,4, submission 56280605)는 같은 notebook 이 "4시간 후 2389 에서 상승 중, 아직 수렴 전" 이라고 적었다. 3-layer 를 빌드하려면 `USE_CADENCE=False` 라는 1개 설정 변경이므로 지시서 범위 밖이라 만들지 않았다.
- **License:** 두 tar 모두 archive 안에 별도 license 파일 없음. `main.py` 안에 Apache-2.0 notice 와 upstream attribution 이 남아 있다(`grep -ci apache`: V1 27줄, V2 25줄). 판단은 Claude 에 넘긴다.

## 3. Gate 6줄 (release 마다 동일 기준, 상세는 release `manifest.json` 의 `preflight`)

```
Identity:  PASS — 독립 빌드 A/B 와 release 빌드의 tar SHA 동일; 기대 main.py SHA 일치(V1 printed literal, V2 active assert)
Schema:    PASS — root main.py; loader entry point 호출 가능; 22/22 경기 720 steps·DONE/DONE, 예외 0
Runtime:   PASS — V1 max wall 3.610s / agent 누적 0.393s ; V2 max wall 3.681s / agent 누적 0.458s (한도 80%: 960s / 623.2s)
Isolation: PASS — 빈 폴더에 tar 를 풀어 import main 성공; audit hook 으로 720-step 전 경기의 agent 호출 중 network·process 이벤트 0, 파일 open 0
License:   DEFERRED_TO_CLAUDE — tar 안 license 파일 없음; main.py 안 Apache-2.0 notice 유지
Ledger:    N/A — 제출하지 않음
```

- 22경기 = starter seed 1000–1009 × 좌석 0·1 (20경기, 후보 20/0/0 전승) + self-play seed 1000·1001. seed 를 늘리지 않았다.
- 엔진 `kaggle-environments==1.32.7`. `kaggriculture.py` `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`, `kaggriculture.json` `a82c89c1a2315b93f39775d8e025471a01b738647c9772658368ee6b1b6f4867` — `environment/ENGINE_LOCK.md` 와 일치.
- 실행 host: Linux VM(aarch64, 4 vCPU, RAM 3 GB), CPython 3.11.16(repo 밖 uv venv). 09-19 gate 는 macOS·Python 3.13·8코어였으므로 **절대 시간(ms/s)을 그 보고서와 직접 비교하지 않는다.** 한도 대비 여유는 세 자릿수 배수라 판정에는 영향이 없다.
- silent-failure counter(기록 전용, 판정 제외; 후보 player-run 24개 합): 

| 후보 | noop | shed_discarded | shed_unsold | orders_truncated | sell_unfilled | buy_failed | hire_failed | seed_blocked | hands mismatch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | 1,380 | 40 | 0 | 0 | 2,409,580 | 6 | 0 | 6 | 0 |
| V2 | 1,504 | 36 | 0 | 0 | 2,410,398 | 2 | 0 | 6 | 0 |

## 4. 발견: instrument.py 경로 실행은 P2 가족의 실제 entry point 를 시험하지 않는다 `[LOCAL]`

- `tools/instrument.py` 의 `load_agent` 는 module 속성 `agent` 를 돌려준다. Kaggle loader(`kaggle_environments.agent.get_last_callable`)는 파일을 exec 한 뒤 **마지막 callable** 을 쓴다. 재확인 명령: `python3 tools/f0_variants_gate.py` 의 `loader_entrypoint` / 이 보고서 §7 의 scan.
- 두 객체가 다른 release: `public-seyitkaangunes-…-2820-score-exact`(`_y_agent_shopherd`), `public-lynnsakurai-farming-score-v2-exact` 와 `…-v2-latest-exact`(`_e336_agent`), `public-aasim2003-notebookb3a3ef21c3-exact`(`_decide`). V1 과 나머지 release 는 두 객체가 같다.
- 행동이 실제로 다르다. V2 를 starter 상대 seed 1000–1009 seat0 에서 비교하면 module `agent` 와 last callable 의 후보 보상이 **10/10 seed 에서 다르다**(예: seed 1000 164,098 vs 164,139). tool-default(module `agent`) 결과는 `experiments/results/f0_live_claim_variants_20260920/tool_default_entry/` 에 비교용으로만 남겼다. V1 은 20+2 경기 보상이 전부 같다.
- 따라서 이번 gate·timing·counter 는 `tools/instrument.py` 의 `instrumented_run` 을 그대로 쓰되 agent 를 last callable 로 넘겼다(같은 counter·같은 timing 계측). **09-19 P2 gate 의 timing·counter 는 module `agent` 로 측정됐을 가능성이 높다**(재실행하지 않음, 판정 변경 없음). 수정 여부(instrument.py 의 `load_agent`)는 이 지시서 범위 밖이라 손대지 않았다.

## 5. 진단 `[LOCAL]` — seed 2000–2009, 좌석 교대, 쌍당 20경기 (seed 추가 없음)

| A | B | A W/D/L | A 점수 | 95% CI (seed 단위 n=10) | A 평균 마진 | arena 판정 |
|---|---|---:|---:|---|---:|---|
| V1 | P2 | 0/0/20 | 0.000 | 0.000–0.000 | −2,353 | FAILURE |
| V2 | P2 | 0/0/20 | 0.000 | 0.000–0.000 | −1,487 | FAILURE |
| V1 | P1 alperen | 0/0/20 | 0.000 | 0.000–0.000 | −2,523 | FAILURE |
| V2 | P1 alperen | 2/0/18 | 0.100 | −0.126–0.326 | −738 | FAILURE |
| V1 | V2 | 14/0/6 | 0.700 | 0.354–1.046 | +595 | INCONCLUSIVE |

- **두 좌석 결과가 모든 쌍·모든 seed(10/10)에서 코인 단위로 동일**하다(결정론적 agent + 대칭 엔진). 20경기는 독립 10 seed 로 읽어야 하고, CI 는 seed 단위(n=10)라 넓다.
- P2 와의 격차는 작다: 평균 마진이 P2 은행(약 93–97k)의 1.5–2.5%. 지는 방향은 일관됐다(20/20). 같은 계보(지시서: sim_p2 0.87/0.84)라 승패 패턴이 P2 와 겹칠 가능성이 크고, 두 번째 슬롯(AGENTS §7.4)용으로는 이 진단만으로 "다르다"를 보이지 못했다(승패 패턴 상관은 아직 측정하지 않음).
- V1 vs V2 는 결과가 뒤집힌다: V1 이 V2 를 14/6 으로 이기지만 P1 상대로는 V2(2/18)가 V1(0/20)보다 낫다. 비추이적이며 10 seed 라 순서를 확정할 수 없다.
- 09-19 보고의 진단 순서(참고): P2 가 P1 alperen 을 18/2 로 이겼다. 이번 결과와 합치면 로컬에서는 P2 ≥ P1 > V2 ≳ V1 이다. 이 순서는 `[LOCAL]` 이며 hosted 강도나 제출 허가를 뜻하지 않는다(AGENTS §7.1, 지시서 §3).
- 작성자 주장(2749 / 2801·2389)은 `[COMMUNITY]` 로 유지한다. 우리 exact 제출의 ladder 점수는 사람이 제출하기 전에는 N/A 다.

## 6. 지시서 대비 이탈·부수 조치

1. **builder 버그 수정(최소):** 작업 시작 시 워킹트리의 `tools/build_public_exact.py`(미커밋, D1–D3 작업 중 변경분)에서 `manifest["source"]["main_cell_id"]`/`archive_cell_id` 를 `info.get("cell_id", f"index:{info['cell_index']}")` 로 계산해 `cell_index` 없는 후보(lynnsakurai·tetsutani·p2-new·p3-new·d1·d3·v1·v2)가 `KeyError` 로 실패했다(f-string 이 eager 평가). 지연 평가로 고쳤고 기존 candidate 의 출력은 바뀌지 않는다: 기존 8개 후보를 다시 빌드해 lynnsakurai·p2-new·p3-new·tetsutani·d1·d2·d3 의 tar 가 기존 release 와 **바이트 동일**, d1·d2·d3 는 manifest 도 동일. alperen 은 tar 가 다르지만 원인이 gzip 헤더 OS 바이트뿐이다(`gzip.compress(mtime=0)` 경로: 이번 Python 3.11 은 `ff`, 09-19 macOS 3.13 은 `03`; 압축 전 tar 는 동일). 이번 후보는 `GzipFile` 경로라 영향이 없다. 나머지 manifest 차이는 gate 뒤 채워진 `preflight` 블록뿐이다.
2. **새 파일 `tools/f0_variants_gate.py`:** 위 §4 이유로 만든 runner(identity·isolation·gate·diag·tool-default·summarize 단계, seed 고정). 기존 `arena.py`/`instrument.py` 는 수정하지 않았다.
3. **tool-default 대조 실행 추가:** §4 근거로 CLI 기본 방식 결과를 `tool_default_entry/` 에 별도 보존했다. gate 판정에는 쓰지 않는다.
4. **release manifest 의 `preflight` 채움:** 09-19 release 와 같은 방식으로 gate 뒤 두 manifest 에 결과를 적었다(tar·main.py 는 그대로).
5. **updater lock:** `tools/update_hypotheses.py` 가 event 와 원장을 정상 갱신한 뒤 `coordination/hypotheses/.update.lock` 삭제만 sandbox 권한(`Operation not permitted`)에 막혀 exit 3 을 냈다. 원장 반영과 event 기록은 끝난 상태였고, 남은 stale lock 이 다음 updater 를 막으므로 사람 승인(삭제 권한 요청)을 받아 그 파일 1개만 지웠다. 이후 `validate_hypotheses.py --strict` 재실행 exit 0.
6. `coordination/TASKS.md` 에 행을 추가하지 않았다(지시서·허가 범위에 없음). 필요하면 코디네이터가 추가한다.
7. AGENTS §11-0: `coordination/BOARD.md` 갱신일이 2026-09-18 23시 KST 로 오늘(09-20)과 달력상 2일 차이다. 지시서가 09-20 에 코디네이터(Claude)에게서 발행됐고 이후 BOARD 를 바꾸는 작업이 아니어서 진행했다. 갱신 여부는 코디네이터가 본다.
8. 새 코드는 repo 밖 `$HOME/kenv`(uv venv, Python 3.11.16 + `kaggle-environments==1.32.7`)로 실행했다. repo 의 `.venv` 는 macOS 용이라 Linux VM 에서 쓸 수 없었다.

## 7. 재현 명령

```bash
# 재확인 (지시서)
shasum -a 256 docs/collection_snapshots/kaggriculture-melon-threshold-squeeze-2749/*.ipynb docs/collection_snapshots/kaggriculture-2820-score/*.ipynb
# 빌드 (결정론: 독립 dir 2회 + release)
python3 tools/build_public_exact.py v1 releases/public-goodpjw2008-kaggriculture-melon-threshold-squeeze-2749-exact
python3 tools/build_public_exact.py v2 releases/public-seyitkaangunes-kaggriculture-2820-score-exact
shasum -a 256 releases/public-goodpjw2008-*/submission.tar.gz releases/public-seyitkaangunes-*/submission.tar.gz
# gate·진단 (각 단계 <180s; 결과: experiments/results/f0_live_claim_variants_20260920/)
python3 tools/f0_variants_gate.py identity
python3 tools/f0_variants_gate.py isolation
python3 tools/f0_variants_gate.py gate
python3 tools/f0_variants_gate.py diag --only v1_vs_p2 v2_vs_p2 v1_vs_p1_alperen --workers 3
python3 tools/f0_variants_gate.py diag --only v2_vs_p1_alperen v1_vs_v2 --workers 2
python3 tools/f0_variants_gate.py tool-default
# entry point 불일치 scan
python3 - <<'PY'
import glob
from pathlib import Path
for mp in sorted(glob.glob("releases/public-*/main.py")):
    env = {}; exec(compile(Path(mp).read_text(encoding="utf-8"), mp, "exec"), env)
    last = [v for v in env.values() if callable(v)][-1]
    print(mp.split("/")[1], last.__name__, env["agent"] is last)
PY
```

정본 결과: `experiments/results/f0_live_claim_variants_20260920/` — `gate_summary.json`(+`gate_v1/v2_summary.json`), `diagnostic_summary.json`(+`diag_*.json` 5쌍 raw), `identity_summary.json`, `isolation_summary.json`, raw gate JSON 6개(`v?_vs_starter`, `starter_vs_v?`, `v?_self`), `tool_default_entry/`. 각 release 의 `manifest.json` 도 함께 본다.

## 8. 가설 원장

```bash
python3 tools/update_hypotheses.py --agent claude --hypothesis-id HYP-0028 --test-id TEST-DONOR-ROUTES-20260917 \
  --reason "F0 live-claim variants V1/V2 exact builds" \
  --set "다음 행동=<기존 값> + coordination/reports/claude/20260920-0950-F0-LIVE-CLAIM-VARIANTS.md"
python3 tools/validate_hypotheses.py --strict
```

- updater: HYP-0028 / TEST-DONOR-ROUTES-20260917 `다음 행동` 칸만 변경(기존 값 뒤에 이 보고서 경로 추가). **상태·결과 칸 불변**(`상태: LOCAL_SUPPORTED` 그대로). event `coordination/hypotheses/claude/EVT-2026-09-20T005051.185990+0000-572d2a8c.json`.
- updater 종료 코드: **3** — 원장·event 는 갱신됐고, `.update.lock` 삭제만 sandbox 권한에 막혀 실패(§6-5). lock 을 사람 승인으로 지운 뒤 상태를 다시 확인했다.
- `validate_hypotheses.py --strict`: `hypothesis ledger PASS: 32 entries`, **exit 0** (updater 직후·lock 제거 후 두 번 실행).
- `HYPOTHESES.md` 는 직접 편집하지 않았다. BOARD·KILLS·실험 card 도 수정하지 않았다(git status 에 보이는 기존 변경은 이 작업 이전부터 있었다).

## 9. 다음 행동

1. Claude(Coordinator): License 판정과 제출 순서 제안. 로컬은 P2 가 V1·V2 를 이기지만 격차가 작고 hosted 는 미측정이라, V1·V2 를 제출할지는 사람이 정한다.
2. Claude(Coordinator): V2 를 `USE_CADENCE=False`(3-layer, 작성자가 2801 이라고 밝힌 build)로 exact 빌드해 같은 gate·진단을 돌릴지 결정한다(1개 설정 변경, 별도 지시서 필요).
3. Codex/Claude: `tools/instrument.py` 가 last callable 을 시험하도록 고칠지 결정하고, 09-19 P2·D3 gate 를 last callable 로 다시 볼지 정한다(이 보고서는 수정하지 않았다).


---

## `reports/claude/20260920-2105-EXP014-015-BUILD.md`

# 보고 — EXP-014·015 변형 빌드 + instrument 진입점 수정

작성: Claude (Cowork, 새 채팅, Sonnet) · 2026-09-20 21:05 KST · 작업 지시서 `coordination/proposals/claude/20260920-EXP014-015-BUILD-CODEX.md` (r2)
**상태: DONE (빌드·확인 3항목·instrument 수정 완료) + 지시서 전제 1건 불성립 → §4 "주의 발견" 참조.** 제출·커밋·경기 matrix 없음.

## 1. host
- Cowork **Linux VM** (aarch64), 시스템 Python 3.10 (`kaggle-environments==1.32.7` 은 `>=3.11` 이라 `pip --user` 설치 불가). `.venv` 는 macOS 용 깨진 symlink 라 사용 불가.
- 대응: `uv` 로 CPython 3.12.14 venv 를 **프로젝트 밖**(`$HOME/venv312`)에 만들고 `kaggle-environments==1.32.7` 설치. (지시서의 `pip --user` 와 명령만 다르고 패키지·버전은 같다.)
- 엔진 SHA 대조: `kaggriculture.py` `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`, `kaggriculture.json` `a82c89c1a2315b93f39775d8e025471a01b738647c9772658368ee6b1b6f4867` — `ENGINE_LOCK.md` 와 **일치**. arena 가 계산한 `engine_sha256` 도 일치.

## 2. 산출물 (두 tar)

| 변형 | 카드 | main.py SHA-256 | **tar 경로** | **tar SHA-256** | tar bytes |
|---|---|---|---|---|---|
| EXP-014 | `experiments/cards/EXP-014-mirror-sale-lead.md` | `f2196b3958651bec800158f0c1bf7aa11a104c892075429fbf983afc38d19460` | `releases/f0-mirror-lead-exp014/submission.tar.gz` | `be529b5cce50c53e738b79094e41852d8195b4f03cb8a391fd1c9ddee1600d29` | 143,294 |
| EXP-015 | `experiments/cards/EXP-015-mirror-slot-priority.md` | `a9358dd80371b4256358156e7a99abd10c1ae5a85310326f04d54e03b785eff0` | `releases/f0-mirror-slot-exp015/submission.tar.gz` | `bfb3157a4a1ee6299b5d26d50e72f6fd91f96415aa97da27b400db32a75a76e0` | 143,335 |

각 폴더에 `main.py`, `submission.tar.gz`, `manifest.json`(checks 결과 포함) 3개. manifest 는 tar 밖이라 tar SHA 에 영향 없음.

입력 SHA (빌드 전·후 모두 확인, 불변): P2 `main.py` `cddf51ea…a94d`, P2 tar `1178ffa0…f388`, 카드 014 `419ed1d0…df1c`, 카드 015 `7afc314a…b446`.

**빌드 방법**
- `main.py = P2 main.py 바이트 + b"\n\n" + 카드 부록 코드`. 카드에서 ```python 블록을 프로그램으로 추출(수기 입력 없음). 별도로 카드 줄 번호 범위(014: 55–101행, 015 slot: 42–70행)를 잘라 `main.py` 끝과 `endswith` 로 비교 → 일치. P2 바이트 prefix 불변 확인.
- tar: `tools/build_public_exact.py` 의 `archive_main` 을 import (builder 파일 미수정). `gzip_file=True`, GNU_FORMAT, mtime 0, uid/gid 0, mode 0644, gzip header mtime 0, 멤버 `main.py` 하나. **먼저 P2 `main.py` 에 같은 함수를 적용해 P2 tar SHA `1178ffa0…` 가 재현되는 것을 확인**한 뒤 사용. 서로 다른 프로세스에서 2회 빌드해 같은 SHA, tar 를 풀어 `main.py` 바이트 일치.
- EXP-015 는 카드 지시대로 EXP-014 부록의 `_MIR_PARENT` 줄부터 `_mir_mode` 끝까지를 같은 바이트로 넣고, `_MIR_REPORT` 에 `'reorders': 0` 만 추가(dict 맨 끝), 빈 줄 2개 뒤에 카드 015 의 `_mirror_slot_agent` 블록. 해석한 부분(행동에는 영향 없음): (a) 카드가 "`_MIR_PARENT` 부터" 라고 하여 EXP-014 의 `# ---- EXP-014 …` 머리 주석은 **넣지 않았다**; (b) `_mir_mode` 와 `_mirror_slot_agent` 사이 간격은 EXP-014 의 함수 사이 간격과 같은 빈 줄 2개. 이 두 선택이 015 의 SHA 를 결정한다 — 다른 선택을 원하면 SHA 가 달라지므로 알려 달라.

## 3. 빌드 확인 3항목 (seed 3000, 양 좌석)

| # | 항목 | EXP-014 | EXP-015 |
|---|---|---|---|
| 1 | exec 후 마지막 callable (엔진 `get_last_callable`, `main.py` 와 tar 안 `main.py` 모두) | `_mirror_lead_agent` **PASS** | `_mirror_slot_agent` **PASS** |
| 2 | 거울 OFF 경기에서 P2 와 719턴 행동 동일 | **PASS** — 상대 goodpjw2008·seyitkaangunes·tetsutani·yhay81, 양 좌석 = 8경기, 719/719 동일, `mirror_games=0`, 예외 0 | **PASS** — 같은 8경기, 719/719 동일, `mirror_games=0`, `reorders=0`, 예외 0 |
| 3 | 상대 P2 에서 거울 ON, 예외 0 | **PASS** — `mirror_games=1`, `mirror_turns=574`(=turn 144–717), `errors=0`, 예외 0, 상태 DONE/DONE, 720 step | **PASS** — 같은 값 + `reorders`=28(양 좌석 경기 모두) |

- 항목 3: `arena.py --a <변형> --b <P2> --seeds 1 --seed-start 3000` 도 실행 — 에러 0, 양 좌석 완료. (arena 는 telemetry 를 보여주지 않으므로 `mirror_games` 는 위와 같은 harness 로 `fn.telemetry` 를 읽었다. harness 자체는 P2 vs Alperen 에서 엔진 path 실행과 행동 719/719 동일함을 확인.)
- 1 seed 결과(승패·점수)는 smoke 일 뿐 성능 증거가 아니다. 판정에 쓰지 말 것.

## 4. 주의 발견 — 지시서 항목 2 의 전제가 성립하지 않았다
지시서는 `--b …alperen-before-dawn… --seed-start 3000` 1경기로 "거울 모드 꺼짐" 을 확인하라고 했다. 실제로는 **Alperen 상대에서도 거울 모드가 켜진다** (seed 3000, 양 좌석 모두: 014 `mirror_games=1, mirror_turns=574`; 015 는 `reorders`=29). 그래서 그 경기는 OFF 동일성 검사가 될 수 없었고(행동이 P2 와 달라지는 것이 정상), 위 표의 OFF 검사는 **나머지 패널 4개**로 대체했다. 카드·지시서는 수정하지 않았다.

원인: P2 와 Alperen 은 로컬에서 **초반 행동이 같다.** P2 vs Alperen 경기에서 두 쪽 행동의 첫 차이 step = seed 3000 → 162, 3001 → 162, 3002 → 164 (차이 나는 step 수 116/133/123 of 719). 거울 감지 창은 turn 1–143 이므로 `farms[0]==farms[1]` 이 143번 모두 참이 된다.
영향(판단은 Claude/사람 몫): 카드의 N 패널(Alperen 포함)에서 Alperen 경기는 거의 전부 거울 ON 일 가능성이 높다 — seed 3000 만 변형으로 직접 확인했고 3001·3002 는 divergence step 이 143 보다 커서 같을 것이라는 추정일 뿐이다. 카드 §계측이 "패널 경기에서 거울 모드가 켜진 경기 수를 결과에 따로 적는다" 고 이미 요구하므로 Antigravity 결과에서 이 수를 반드시 분리 기록해야 한다.

## 5. `tools/instrument.py` `load_agent`
- `getattr(mod, "agent")` → 엔진과 같은 규칙: `kaggle_environments.agent.get_last_callable(read_file(path), path=str(path))` (빈 dict 전역 exec, 전역 값 중 마지막 callable). 이 함수 1개만 수정했다(diff 는 `load_agent` 본문 한 곳).
- 효과: P2 → `_e336_agent`(이전 `agent`), 014 → `_mirror_lead_agent`, 015 → `_mirror_slot_agent`.
- 회귀 확인: 자체 `main.py`(마지막 callable = `agent`, 바이트코드 동일) vs `starter`, seed 7, `capture_actions=True` — 수정 전/후 **reward `[23440, 3378]` 동일, counter·상태 동일, action stream 719개 동일, 양쪽 `is_clean()`**. (시간 필드 제외. `co_filename` 만 절대→상대 경로로 달라진다.)
- 09-19 gate 재실행 안 함. 참고: `tools/f0_variants_gate.py` docstring 은 옛 동작("`agent` 를 반환")을 설명하고 있어 이제 낡았다 — 다른 tools 파일이라 수정하지 않았다.
- 남긴 것: 더 이상 쓰지 않는 `import importlib.util` (최소 diff 유지).

## 6. 사고 기록 (해결됨)
작업 초기에 마운트 폴더에서 `git status` 를 실행했다가 `.git/index.lock`(0 byte)이 남았다(삭제 권한이 없어 지워지지 않음). 다른 git 작업을 막을 수 있어서 `.git/_trash/index.lock.claude-stale-20260920T1152` 로 **이동**해 lock 을 풀었다(기존 `_trash` 관행과 동일). 이후 git 은 `--no-optional-locks` 로만 읽었다. 삭제는 하지 않았다.

## 7. 수정·미수정 확인
- 새로 만든 것: `releases/f0-mirror-lead-exp014/`, `releases/f0-mirror-slot-exp015/` (각 3파일), 이 보고서. 수정: `tools/instrument.py`(`load_agent` 만).
- 미수정 확인(SHA/mtime): P2 release 폴더, 두 카드, `tools/build_public_exact.py` 및 다른 tools 파일, 기존 release 폴더. 지난 50분간 프로젝트 내 변경 파일은 위 목록뿐(`find -mmin`).
- 작업용 스크립트·로그·arena JSON 은 프로젝트 밖 VM scratch 에만 있다(세션 종료 시 사라짐). 재현은 §2 방법 기술로 가능.
- 커밋·제출·경기 matrix: 안 함.


---

## `reports/claude/20260921-C1-LOCAL-LOSS-FIRST-READ.md`

# 20260921 C1 로컬 패배·거울전 1차 판독 (Claude)
근거: analysis/c1_losses/20260921/games.csv (280경기), coordination/reports/antigravity/1790000790-C1-LOSS-MIRROR.md

1. **결과는 seed 로 정해지고 좌석과 무관.** 같은 seed 의 seat0/seat1 경기가 cash 까지 정확히 좌우 대칭. 유효 표본 = seed 40개 (경기 80 이 아님).
2. **거울전(C1 vs C1):** 40 seed 중 36 무승부. 비무승부 4 seed 에서 P1 3, P0 1 → **좌석 편향은 작다** (2011 −68, 2021 −1170, 2022 +968, 2036 −129).
3. **V53/V51 상대 패배는 같은 seed 에 몰림** (2013, 2014, 2021, 2022, 2029, 2031, 2043, 2046 + 2017/2018/2028).
4. **BRUNCH_SPOT 이 들어간 첫 두 shop 조합에서 패배 집중:** L1+L2+R1 비거울 200경기 중 BRUNCH 포함 74경기에서 30패 (41%), 나머지 126경기에서 7패 (6%). route 103 8/12, 101 7/16, 105 14/56.
5. 샘플 3개(2013, 2029, 2046): C1 은 day 12~14 까지 앞서다 day 14~18 에 역전됨. 상대(V53)는 EGG 판매가 있고(C1 0회) STRAWBERRY 판매가 약간 많음. 원인 확정 아님 — 다음 분석에서 day 12~18 구간 농장 구성·판매 가격 차이를 본다.

판단(가설 후보, 아직 카드 아님):
- H-A 거울전 무승부 깨기 (36/40 이 무승부 → 작은 이득이 0.5→1.0 로 바뀜). EXP-014 의 C1 판.
- H-B BRUNCH 조합 day 12~18 경제 보정 (V53 쪽 행동 차용).


---

## `reports/claude/20260922-C1-HB-ANALYSIS.md`

# 20260922 H-B 분석 — C1 이 V53/V51 에게 지는 이유 (Claude)

자료: analysis/c1_losses/20260921/replays/ 의 L1/L2 패배 seat0 replay 17개 (seat1 은 좌우 대칭 사본이라 제외). 엔진 kaggriculture.py 1.32.7.
주의: 패배 경기만 저장돼 있어 승리 대조군이 없다. 아래는 "패배 경기 안에서 C1 과 상대가 어떻게 달랐나" 이다.

## 1. 물리 행동은 완전히 같다 — 차이는 전부 시장(판매) 층
- day 8/12/15/18 농장 구성(소·양·거위·딸기 33·멜론 12 등)이 17경기 모두 두 농장 동일 (같은 route tape).
- HIRE 수, BUY_ANIMAL, BUY_LAND, FERTILIZE 횟수(d12-18, d19+)도 동일.
- 즉 C1 과 V53/V51 은 같은 tape 로 같은 물건을 만들고, **언제·얼마나 파느냐**만 다르다.

## 2. BRUNCH 와의 연결 (엔진)
- `SHOPS["BRUNCH_SPOT"] = [EGG, WHEAT, STRAWBERRY]`, 4 step 마다 시장 재고를 깎는다 (`_town_consume`, kaggriculture.py:728-748). BAKERY 도 EGG·WHEAT.
- 패배 17경기 중 15경기가 BRUNCH_SPOT 을 첫 두 shop 에 포함, 다수가 BRUNCH 2~3개 + BAKERY. → EGG·STRAWBERRY 가격이 높고 크게 흔들리는 판 = 누가 먼저 파느냐의 값이 커지는 판.

## 3. 판매 경주 (한쪽이 먼저 팔고 다른 쪽이 1~3 step 뒤 같은 물건을 판 사건)
| 품목 | 구간 | C1 선행 | 상대 선행 | 경주 구간 cash 차 변화 (C1 기준, 17경기 합) |
|---|---|---:|---:|---:|
| WOOL | d19+ | 53 | 67 | −33,975 |
| STRAWBERRY | d19+ | 35 | 36 | −20,712 |
| WHEAT | d12-18 | 108 | 10 | −12,727 |
| FERTILIZER | d19+ | 13 | 12 | −10,489 |
| EGG | d12-18 | 8 | 13 | −9,090 |
| MILK | d19+ | 65 | 45 | +6,222 |
| WHEAT | d19+ | 254 | 140 | +8,040 |
(창이 겹쳐 합계는 과대 — 방향만 본다.)
- 예: seed 2046 step 385, 상대가 WOOL 14 를 226 에 먼저 팔고 C1 은 한 step 뒤 220 에 판다. seed 2013 에서 WHEAT 은 C1 이 한 step 먼저 판다(비슷한 크기로 상쇄).
- 평균 판매가: STRAWBERRY d19+ C1 142.7 / 상대 148.1, WOOL d19+ 76.3 / 85.8, EGG 판매량 d12-18 415 / 469.

## 4. 코드 근거
- V53(`releases/public-ozer-v53-exact/main.py:3532-3629`)에는 **EXP293 판매 앞당김** 층이 있다: 3턴 안에 tape 가 팔 STRAWBERRY/WOOL/EGG/MILK/MELON/CARROT/TOMATO 가 창고에 이미 있으면 지금 판다 + SELL 을 market 목록 앞에 둔다(frontload). 공개 sdy623/jaxa623 기법, Apache-2.0.
- **C1 에는 이 층이 없다** (`_ADV_*` 없음). 의존 심볼(_IMPL.chassis, projected_shed, FarmView, _RACE_STATE, r36_debts)은 C1 에 모두 있다.
- 상대가 앞서는 품목(WOOL·STRAWBERRY·EGG)이 정확히 이 층의 대상 품목이다. C1 이 앞서는 WHEAT 은 대상 밖이다.

## 5. 결론 → EXP-016
- H-B 는 "BRUNCH 전용 보정"이 아니라 **판매 앞당김 층 누락**으로 보인다 [INFERENCE — 승리 대조군 없음]. BRUNCH 판은 그 차이가 커지는 판일 뿐.
- 같은 층은 C1 복제본 상대(거울전 90% 무승부)에서도 한 턴 먼저 팔게 하므로 **H-A 와 같은 변형**이다.
- 위험: KILLS K2(남의 실험, C92 에서 2턴 선행매도 2-2)와 EXP-015(P2 에서 SELL 재정렬이 자금 규칙과 충돌, 회귀 14) — 그래서 패널 회귀를 사전 고정 기준으로 본다.


---

## `reports/claude/20260923-NEW-GAIN-OPUS55.md`

# 20260923 NEW-GAIN — Claude Opus 5.5 (지시서 20260923-NEW-GAIN-SEARCH-OPUS55.md)

VERDICT | **엄밀한 의미로는 "찾지 못했다".** DSM 과의 격차는 1개 층(layer)이 아니라 농장 계획 전체(4번째 땅 d10–11 · 동물 22.7 vs 17.5 · shop 비례 GOOSE/TOMATO)에서 나온다. append-only 층으로 가져올 수 있는 가장 가까운 후보는 **V219-2SHOP**(기존 V219 tomato 투자 문턱 3→2 shop)인데, 기대 이득이 0 근처고 K1 재검토가 선행돼야 한다 | Q1 숫자 있음 (40/40 짝) | parent `56941da2…fc33` | NEXT: 사람 — K1/K9 재검토 여부 결정, E-2 가중치용 EXP-016/017 hosted episode 수집

작성 2026-09-23 KST (Claude Opus 5.5). 제출·Kaggle 다운로드·releases/ 편집·BOARD/KILLS/HYPOTHESES 수정 **없음**.
추정은 `[INFERENCE]`, 엔진 직접 확인은 `[ENGINE]`, 새 로컬 실행은 `[LOCAL]`, hosted replay 재현은 `[HOSTED]` 로 표시한다.

---

## 0. 읽은 순서와 실행량

§1 순서대로 읽음: `evidence/KILLS.md` → `evidence/FACTS.md` → `coordination/proposals/claude/20260923-CANDIDATE-POLICY.md` → `evidence/HOSTED_LEDGER.md`(09-21 이후) · `coordination/reports/claude/20260922-C1-HB-ANALYSIS.md` → `coordination/reports/antigravity/20260923-2000-TOP-AGENT-SNAPSHOT.md` · `analysis/top_agents_20260923/` → `releases/f0-omw-adv-exp017/main.py`(sha `56941da2…fc33` 일치) · engine `kaggriculture.py`(sha `bc8a5487…653e`, ENGINE_LOCK 일치).
겹침 회피: codex-astra 는 **판매량 vs 흡수량**(판매 층)을 맡았다. 이 보고는 **생산·토지 구성**만 다룬다.

| 실행 | 수 | 성격 |
|---|---:|---|
| 새 로컬 경기 (EXP-017 vs EXP-016) | **36** (≤ 40) | 진단: probe 1 + Q1 짝 31 + telemetry 2 + 빈 타일 계측 2 |
| hosted replay 재시뮬레이션 | 120 | 새 경기 아님 — 상위 3팀 120경기의 **기록된 양쪽 행동을 그대로** 엔진에 넣어 재현 (§6 F1) |

---

## 1. Q1 — DSM 과 EXP-017 이 처음 갈라지는 결정

### 1.1 짝짓기 방법
- DSM 40경기의 첫 두 shop 조합은 **31종**(가장 흔한 조합도 2경기).
- `[ENGINE]` shop 은 `rng=Random((seed*1_000_003)^day)` 에서 뽑히지만, **그 전에 양쪽 농장의 빈 타일(None) 수만큼 `rng.random()` 이 먼저 소비된다**(`_spawn_weeds` → `rng.choice`, `kaggriculture.py:836-839, 871-891`). EXP-017 vs EXP-016 은 d2·d5 끝에 빈 타일이 0 이라 첫 두 shop 이 seed 만으로 결정된다.
- 그래서 조합마다 첫 두 shop 이 DSM 경기와 같아지는 seed 를 골라(≥3,000,000, 가장 작은 값) EXP-017 을 **DSM 과 같은 좌석**에 두고 EXP-016 과 1경기씩 돌렸다. **예측 31/31 적중** (`plan17.json`, `exp17_local.jsonl`).
- ⚠️ 상대가 다르다(DSM ← 상위 팀들, EXP-017 ← 거의 거울인 EXP-016). **cash 는 참고값.** 3번째 shop 부터는 두 경기가 서로 다를 수 있다.

### 1.2 결과 — 처음 갈라지는 곳은 **day 0 opening**, 40/40 (shop 과 무관)
| | DSM (hosted 40) | EXP-017 (local 31 → 40 짝) |
|---|---|---|
| step 0 market | `BUY_ANIMAL COW 1`, `BUY_PRODUCT WHEAT 5` | `BUY_PRODUCT WHEAT 13`, `BUY_PRODUCT WHEAT 30`, `SELL WHEAT 30`, `BUY_SEED WHEAT 1` |
| step 1 market | `SELL WHEAT 1`, HIRE×4, `COW 1`, **`SHEEP 3`** | `SELL WHEAT 13`, `BUY WHEAT 5`, HIRE×5, `COW 2`, **`SHEEP 2`** |
| d0 끝 | MELON **6**, WHEAT 9, SHEEP **3**, hands 4 | MELON **12**, WHEAT 8, SHEEP **2**, hands 5 |
| STRAWBERRY 시작 | **d2 4칸 → d3 10칸** | d5 4칸 → d8 20칸 |
| 2·3·4번째 땅 | **d6 · d9 · d10(36/40)/d11(4/40)** | d6 · **d11** · 없음(26/31) |
| 첫 GOOSE | d6 (24/40) | 없음(15/31), d10(10/31) |

DSM 의 opening 은 40경기 모두 같은 바이트다(첫 3 step market 이 40/40 동일). 큰 차이 기준(작물 ±4칸, 동물 ±2, hands ±2)으로 **첫 차이 = day 0, 40/40, 내용 = MELON 6 vs 12.**

**첫 번째 shop 의존 차이**(day ≥ 6; TOMATO/CARROT ≥ +3칸, GOOSE ≥ +2, 땅 ≥ +1): **d6 GOOSE 20/40, d9 땅(3 vs 2) 20/40.** 경기별 표는 부록 A.

### 1.3 day 별 평균 구성 (DSM hosted 40 / EXP-017 짝 40)
| day | WHEAT | CARROT | STRAWB | TOMATO | MELON | COW | SHEEP | GOOSE | hands |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 9.0/8.0 | 0/0 | 0/0 | 0/0 | **6/12** | 2/2 | **3/2** | 0/0 | 4/5 |
| 3 | 0/7.0 | 0/0 | **10/0** | 0/0 | 10/12 | 2/4 | 3/2 | 0/0 | 6/5 |
| 6 | 6.2/5.0 | 0/0 | 15.5/12 | 0/0 | 10/12 | 6.3/5.0 | 4.6/2.7 | **1.4/0.3** | 8/7.3 |
| 10 | **29.5/12** | 1.5/0 | 20.7/20 | 2.3/0 | 4/0 | 8.9/7.2 | 6.5/7.7 | **5.0/1.1** | 11.7/11 |
| 12 | 29.6/23.9 | 2.5/0.1 | 27.9/33 | **5.6/0** | 0/0 | 9.2/7.2 | 7.2/8.7 | 6.0/1.6 | 11.3/9.2 |
| 16 | 22.8/24.8 | 3.0/0.2 | 32.1/33 | **11.4/0** | 0/0 | 9.2/7.2 | 7.5/8.7 | 6.0/1.6 | 12/11.1 |
| 20 | 26.4/24.8 | 6.8/0.2 | 21.9/33 | 14.2/0.8 | 0/0 | 8.8/7.2 | 7.7/8.7 | 5.9/1.6 | 11.7/11.6 |
| 26 | 29.2/15.7 | 21.2/29.1 | 11.8/13 | 5.5/0.8 | 0/0 | 6.8/7.2 | 6.1/8.7 | 5.6/1.6 | 11.3/11.5 |

occupied 타일(작물+동물) d16: **DSM 92.0** / Majkel 74.4 / MMPQ 74.6 / EXP-017 75.4. 최종 cash 참고값: DSM 112,432 / EXP-017 짝 103,657 (차 **+8,775 ± 6,720**, 95% CI).

---

## 2. Q2 — 생산 구성 차이가 설명하는 몫

### 2.1 정확한 수확·판매 (재시뮬레이션 계측, 추정 아님)
Antigravity 스냅샷은 판매를 행동+가격으로 근사했다. 여기서는 엔진 `_commit_unit`/`HARVEST` 를 직접 계측했다(`instr.py`). d12-29 요약:

| 품목 | DSM 수확/판매/수입 | Majkel | MMPQ | EXP-017 짝 |
|---|---|---|---|---|
| TOMATO | 112u / 111u / **7,304** | 72 / 72 / 6,202 | 0 / 0 / 0 | 6 / 6 / **1,024** |
| EGG | 173 / 176 / **8,244** | 154 / 155 / 7,105 | 0 / 0 / 0 | 49 / 49 / **2,570** |
| CARROT | 157 / 156 / 5,841 | 149 / 150 / 6,151 | 226 / 227 / 8,815 | 111 / 111 / 4,939 |
| STRAWBERRY | 235 / 233 / 34,348 | 202 / 201 / 29,893 | 224 / 226 / 29,810 | 248 / 246 / 32,340 |

(지시서의 "d19-29 TOMATO 우리 32u" 는 seed 2140-2149 vs OMW 값이다. 짝 40경기에서는 6u.)

### 2.2 "해금된 shop 이 사 주는 작물을 키웠는가" — 반응 기울기
각 경기의 실제 shop 목록으로 d12-29 shop 소비량(dem)을 계산하고 `수확량 = a + b·dem` 을 적합했다 (`q2d.py`):

| 품목 | DSM b | Majkel b | MMPQ b | **EXP-017 b** |
|---|---|---|---|---|
| STRAWBERRY | 0.49 | 0.41 | 0.55 | **0.00** (항상 248u) |
| TOMATO | 0.39 | 0.35 | 0 | **0.18** (V219 가 켜질 때만) |
| CARROT | 0.53 | 0.41 | 0.78 | **0.19** |
| EGG | 0.40 | 0.30 | 0 | **0.05** |
| MILK | 0.58 | 0.54 | 0.50 | **0.23** |
| WOOL | 0.57 | 0.50 | 0.59 | 0.45 |

GOOSE 수 (d9 까지 egg shop 수 0/1/2+): **DSM 3.7 / 7.1 / 9.2** · Majkel 2.4 / 4.6 / 7.0 · **EXP-017 1.3 / 1.5 / 3.4**.
→ 상위 팀은 **해금된 shop 에 맞춰 생산량을 바꾸고**, EXP-017 은 route tape 에 고정된 양을 만든다.

### 2.3 몫 추정 (seed 비용 차감 순수입, DSM 과 짝 EXP-017 비교)
| 품목 | 차이 합 | 그중 shop 이 설명하는 몫 `[INFERENCE]` | shop 과 무관한 기본 차이 |
|---|---:|---:|---:|
| TOMATO | +5,299 | **+2,005** | +3,294 (DSM 은 tomato shop 이 없어도 61u 를 키움) |
| EGG | +5,720 | **+3,121** | +2,600 (goose 값·사료 미차감) |
| CARROT | −35 | −69 | +34 |
| STRAWBERRY | −215 | −215 | 0 |

- shop 이 설명하는 몫 ≈ **+5.1k**, 최종 cash 차이 +8.8k(±6.7k) 대비. 이를 깎는 항목: WHEAT −5.0k(±10.0k), FERTILIZER −2.3k, MELON −1.0k (EXP-017 이 더 번다).
- 한계: ① 상대가 다르다(MILK d12-18 단가 151 vs 108 은 EXP-016 거울 효과일 가능성 큼) ② EGG 에서 goose 300×약 4.5마리와 사료 밀(1/일)을 빼지 않았다 ③ shop 목록은 각자 자기 경기 기준이다(3번째 shop 부터 다를 수 있음).

### 2.4 이 차이를 가능하게 하는 구조 `[HOSTED]`
- DSM 은 **4번째 땅(SE, $4,000)을 d10 36/40, d11 4/40 에 산다.** Majkel·MMPQ 는 0/80.
- DSM 의 SE 칸은 주로 WHEAT(8~11칸) + 빈칸 6~7 + STRAWBERRY 4. TOMATO·GOOSE 는 대부분 SE 밖에 있다 → 추가 땅은 더 큰 가축 떼(22.7 vs 17.5 마리, 사료 = 밀 1/일)를 먹이는 데 쓰인다 `[INFERENCE]`.
- EXP-017 은 d11 부터 빈 타일이 거의 없다(EOD 빈칸 0~1, 계측 2경기). **더 키우려면 땅이나 tape 계획이 바뀌어야 한다.**

---

## 3. Q3 — 부모 바이트를 건드리지 않는 층으로 가져올 수 있는가

현재 parent 에서 관련된 층: V9 HERD(d9 에 yarn 이 있고 egg shop ≤ 1 이면 tape 의 goose 를 sheep 으로 교체), HERD2/COWSWAP, CARROT/CARROT2(밀→당근), **V219**(d18 에 PIZZA/FM 인스턴스 ≥ 3 이면 SE 를 사서 tomato 10칸 + 전용 일꾼).
telemetry 2경기(BAKERY+SMOOTHIE, BRUNCH+PIZZA)에서 goose 를 없앤 것은 **V9 HERD** 였다(`herd_species=SHEEP`, rewrites 11). HERD2 는 동작하지 않았다.

| 방법 | 바꾸는 것 | 적용 빈도 | 기대 이득 `[INFERENCE]` | 구현 | 회귀 위험 | EXP-017 과 메커니즘 차이 | KILL |
|---|---|---|---|---|---|---|---|
| **(a) V9HERD-EGGKEEP** | `V9_HERD_MAX_EGG_SHOPS = 0` 한 줄 덧붙이기 (egg shop 이 있으면 goose 유지) | 약 **4%** (첫 두 shop 에 yarn 없음 × 3번째 = yarn × egg shop 정확히 1) | 적용 판당 부호 불명, 평균 **≈0** | 1줄 | 낮음 (tape 가 goose 를 pasture 동물처럼 다룸) | 동물 구성 (다름) | K9 인접 |
| **(b) V219-2SHOP** | `_v219_qualifies` 재정의, 문턱 `< 3` → `< 2` (나머지 동일) | d18 까지 6 shop 중 정확히 2: 이론 30%, 로컬 6/31. 단 tomato 가격 ≥ 70 조건 때문에 실제로는 **≈10~19%** | 적용 판당 −1k~+2k (SE 4,000 + 일꾼 고용 vs tomato 약 80u × 60~80), 평균 **0~+0.3k** | 약 25줄 | 중간 (SE 매입·현금). parent 는 이미 3-shop 판에서 같은 경로를 쓴다 | 생산·토지 (다름) | **K1** |
| **(c) SE-ANNEX (DSM 형)** | d10-11 SE 매입 + 전용 인력 + 늘린 가축 떼·사료 | 대부분 | 최대 +5~9k (DSM 격차) | route 재계획. append 는 가능해도 ≫ 200줄 | 높음 (F-T10: tape desync; d8-11 현금 부족) | 농장 계획 전체 | **K1, K9** |

제외한 것:
- tape 의 밀 칸을 tomato 로 바꾸기: tomato 는 8일 뒤 4번만 생산하고 수확 주기가 tape 와 맞지 않다(F-T11 의 품목 치환 손실).
- STRAWBERRY 줄이기: 수입은 이미 DSM 과 같다(−215).
- 3번째 땅을 d8 로 당기기: d8 현금이 평균 1,529 라 $2,000 부족.

**추천 1개: (b) V219-2SHOP.** 단, 조건부다.
- 이유: append 로 가장 작고, parent 에서 이미 검증된 코드를 문턱 하나만 바꿔 재사용한다. 판매 층을 공유하는 EXP-016/017 과 메커니즘이 다르다.
- 약점: 기대 평균 이득이 0 근처다 → **EXP-017 을 넘을 확률은 낮다고 본다.** E-3 기준으로 슬롯 B 1순위 자격이 약하다. arena 시간이 남을 때만, codex-astra 판매 후보 **다음** 순서로 돌릴 것을 권한다.
- **K1 재검토가 사람에게 승인되기 전에는 실행하지 않는다** (§6 F3).

---

## 4. Q4 — 제약 점검 (V219-2SHOP)
| 제약 | 판정 |
|---|---|
| 0.5초/step, 예외 0 | ✔ 예상. 재정의한 함수는 step 432 에서 한 번만 불린다(`main.py:1422`). V219 본체는 parent 에서 이미 매 step 돈다. **측정은 카드에서** |
| append-only | ✔ `_v219_qualifies` 는 global 이름으로 불리므로 뒤에 재정의하면 적용된다. 선례: V13V 가 `_v219_request` 를 같은 방식으로 재정의 |
| 외부 의존 없음 | ✔ 표준 라이브러리도 불필요 |
| arena 1회 ≤ 1,000경기 | ✔ 카드 640경기 ≈ 3.2시간 (18.2초/경기) |
| 설계 제약 초과 | 줄 수는 초과하지 않는다. 대신 **KILL K1 영역**(4번째 땅)이다 — 설계 제약이 아니라 KILL 이므로 사람 승인이 필요 |

---

## 5. 사전등록 카드 초안 (실행 금지 — K1 재검토 승인 후)
```yaml
id:          EXP-019 (가번호 — codex-astra 초안이 EXP-018)
hypothesis:  tomato 를 사는 shop 이 2개일 때도 V219 의 d18 SE tomato 투자는 순이득이다
parent:      releases/f0-omw-adv-exp017/main.py   # 56941da238ccdc8f5286bf7e3191b6208ee3451306e06b74bb2660134a69fc33
one_change:  parent 끝에 _v219_qualifies 재정의 1개 추가 — 본문은 parent :1265-1283 과 같고
             `sum(s in ('PIZZA_SHOP','FARMERS_MARKET') ...) < 3` 만 `< 2` 로 바꾼다. 다른 상수·함수는 그대로
seeds:       2220-2259, 양 좌석 (seed 당 2경기)
blocks:
  A_parent:  candidate vs EXP-017 (parent)                      80
  B_ours:    candidate vs releases/f0-c1-adv-exp016/main.py     80
  panel (candidate 와 대조 EXP-017 을 같은 seed·좌석으로):
    - OMW   releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py (10f58185…)
    - C2    releases/public-thomastschinkel-metav4-v13-exact/main.py
    - C4    releases/public-ozer-v53-exact/main.py              3 × 80 × 2 = 480
  합계 640경기
changed_set S: candidate 의 V219 commitments=1 이고 같은 seed·좌석·상대의 parent/대조가 0 인 cell
               (V219 telemetry 로 사전 정의. S 밖 cell 은 두 봇의 행동이 같아야 한다 → 다르면 INVALID)
success (모두):
  - S 위 paired cash 차 (candidate − 대조) 평균 > 0, 95% CI 하한 > 0
  - A_parent seed 순승 >= +2
  - panel 합산 candidate 패배 <= 대조 패배, 어느 상대도 +2 초과 증가 없음
  - 예외 0, 최대 step 시간 < 0.5s, S 밖 행동 불일치 0
failure: S 위 paired 차 평균의 95% CI 상한 < 0, 또는 A_parent 순승 <= -2, 또는 panel 패배 +4 이상
inconclusive: 그 밖. |S| < 20 이면 자동 INCONCLUSIVE (표본 부족)
제출 판단 (정책 B-2/E-2):
  hosted 가중치 출처 = EXP-016 56458814 · EXP-017 56490029 의 최신 hosted episode (각 ≥ 100경기),
  analysis/c1_hosted_20260921/fingerprint.py 방식으로 상대 계열 비율 share_f 계산.
  → 현재 저장소에 없음: **BLOCKED — 사람이 다운로드해야 함** (이 작업에서는 Kaggle 다운로드 금지).
  C1(~2200) 구간 가중치(analysis/c1_hosted_20260921/opponents.csv) 는 E-2 에 따라 사용 금지.
실행 Antigravity · 판정 Claude · 제출 사람
```

---

## 6. 부수 발견 (KILLS/FACTS 는 직접 고치지 않음 — evidence owner 에게 제안)
- **F1 `[ENGINE]` `[HOSTED]`** 상위 3팀 hosted 120경기 전부를 기록된 양쪽 행동 + `info.seed` 로 로컬 1.32.7 에서 돌리면 **보상 120/120, shop 순서 120/120 정확히 재현**된다. → hosted 경기를 상대 행동을 고정한 채 counterfactual 로 계측할 수 있다.
- **F2 `[ENGINE]`** FACTS F-T4 의 "shop 종류는 (seed, day) 로만 결정" 은 불완전하다. 양쪽 농장의 빈 타일 수가 rng 소비량을 바꾼다. hosted 상위 경기 120 중 seed-only 예측 적중은 **14** 뿐이고, EXP-017 vs EXP-016 로컬은 32/32 적중. 즉 **어느 한쪽 농장만 바뀌어도 이후 shop 이 달라진다.** 로컬 A/B 에서 shop 순서가 갈라질 수 있다는 뜻이다. (seed 가 숨겨져 있어 shop 을 조종하는 데 쓸 수는 없다 `[INFERENCE]`.)
- **F3 `[HOSTED]` K1 재검토 근거:** 1위 DSM 이 SE 를 d10-11 에 40/40 매입하고 이 40경기에서 36-4. K1 의 근거는 남의 실험(rayk)이고 재검토 조건은 "액션 예산이 근본적으로 늘어난 경우"다. 이 관측은 그 조건과 다른 축이지만 K1 의 전제("4구획은 모든 변형에서 진다")와 충돌한다. **사람 판단 필요.**
- **F4 `[HOSTED]` K9 전제 갱신 필요:** "공개 상위 봇 4종 중 3종이 0마리" 는 현 상위 3팀 중 2팀(DSM 평균 6, Majkel 4.3)과 맞지 않는다. goose 수는 egg shop 수에 비례한다(§2.2).

## 7. 재현
분석 폴더 `analysis/new_gain_opus55_20260923/` (스크립트 + `exp17_local.jsonl` sha `fb447e0e…c741`, `plan17.json` `f4b2ef83…c44c`), hosted 재현본 `private_artifacts/new_gain_opus55_20260923/resim_hosted.jsonl` (`073c1a99…aa4`), 계측기 `instr.py` (`859b6ba2…75b4`).
1. `python3 analysis/new_gain_opus55_20260923/extract_tapes.py` (원본 replay → tapes.jsonl, 읽기 전용)
2. `python3 resim.py tapes.jsonl resim_hosted.jsonl` → 120/120 일치 확인
3. `run17.py` (31경기) → `q1.py` · `q2.py` · `q2d.py` · `q2e.py`
4. `python3 analysis/new_gain_opus55_20260923/se_quadrant.py` (DSM SE 칸 구성)
engine `kaggle-environments==1.32.7`, `kaggriculture.py` sha `bc8a5487…653e`. EXP-016 main `9d58536d…6013`.

## 부록 A — Q1 경기별 짝 (DSM hosted ↔ EXP-017 local, 같은 첫 두 shop)
| DSM episode | 첫 두 shop | DSM 결과 | cash DSM / E17 (참고) | 첫 차이 (전부 d0) | 첫 shop 의존 차이 |
|---|---|---|---|---|---|
| 112404753 | FARME+SMOOT | W | 135,401 / 123,755 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112396243 | PET_C+YARN_ | L | 94,505 / 73,695 | d0: MELON 6v12, SHEEP 3v2 | d9: GOOSE 2v0, land 3v2 |
| 112386948 | BAKER+BRUNC | W | 107,052 / 79,209 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 4v2 |
| 112378715 | BRUNC+PIZZA | W | 84,946 / 101,219 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112370239 | BRUNC+SMOOT | W | 113,750 / 102,061 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112361804 | ICE_C+ICE_C | L | 131,997 / 117,700 | d0: MELON 6v12, SHEEP 3v2 | d9: land 3v2 |
| 112353528 | BRUNC+YARN_ | W | 120,248 / 100,374 | d0: MELON 6v12, SHEEP 3v2 | d9: land 3v2 |
| 112346082 | BRUNC+PIZZA | W | 104,168 / 101,219 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112342409 | YARN_+PIZZA | W | 121,055 / 107,177 | d0: MELON 6v12, SHEEP 3v2 | d9: TOMATO 4v0, land 3v2 |
| 112334226 | BRUNC+SMOOT | W | 93,665 / 102,061 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112326822 | PET_C+YARN_ | W | 104,581 / 73,695 | d0: MELON 6v12, SHEEP 3v2 | d9: TOMATO 4v0, GOOSE 4v0, land 3v2 |
| 112319629 | YARN_+YARN_ | L | 84,472 / 117,043 | d0: MELON 6v12, SHEEP 3v2 | d9: TOMATO 4v0, land 3v2 |
| 112312667 | SMOOT+YARN_ | W | 142,410 / 87,291 | d0: MELON 6v12, SHEEP 3v2 | d9: land 3v2 |
| 112312507 | BAKER+PET_C | W | 110,094 / 70,457 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 4v2 |
| 112305594 | PIZZA+PET_C | W | 76,391 / 65,780 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112298198 | YARN_+BRUNC | W | 120,632 / 87,675 | d0: MELON 6v12, SHEEP 3v2 | d9: GOOSE 3v0, land 3v2 |
| 112298128 | ICE_C+BRUNC | L | 120,732 / 94,009 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112290478 | PET_C+PET_C | W | 87,937 / 70,472 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 4v2 |
| 112282976 | BRUNC+YARN_ | W | 119,423 / 100,374 | d0: MELON 6v12, SHEEP 3v2 | d9: GOOSE 2v0, land 3v2 |
| 112275602 | SMOOT+BAKER | W | 96,420 / 98,498 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112268530 | SMOOT+BRUNC | W | 104,227 / 124,261 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112262072 | FARME+PIZZA | W | 102,547 / 109,065 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112255699 | ICE_C+YARN_ | W | 136,390 / 109,336 | d0: MELON 6v12, SHEEP 3v2 | d9: TOMATO 4v0, land 3v2 |
| 112252285 | BRUNC+BRUNC | W | 88,526 / 105,200 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 4v2 |
| 112245955 | ICE_C+ICE_C | W | 92,067 / 117,700 | d0: MELON 6v12, SHEEP 3v2 | d9: GOOSE 3v0, land 3v2 |
| 112239177 | YARN_+YARN_ | W | 120,736 / 117,043 | d0: MELON 6v12, SHEEP 3v2 | d9: land 3v2 |
| 112232283 | SMOOT+ICE_C | W | 116,051 / 130,693 | d0: MELON 6v12, SHEEP 3v2 | d9: land 3v2 |
| 112225424 | YARN_+PET_C | W | 103,380 / 87,589 | d0: MELON 6v12, SHEEP 3v2 | d9: land 3v2 |
| 112218497 | YARN_+FARME | W | 131,019 / 118,604 | d0: MELON 6v12, SHEEP 3v2 | d9: GOOSE 3v0, land 3v2 |
| 112212743 | YARN_+ICE_C | W | 136,142 / 100,843 | d0: MELON 6v12, SHEEP 3v2 | d9: TOMATO 3v0, land 3v2 |
| 112212742 | PIZZA+SMOOT | W | 116,695 / 92,111 | d0: MELON 6v12, SHEEP 3v2 | d9: GOOSE 3v0, land 3v2 |
| 112207248 | SMOOT+BRUNC | W | 114,871 / 124,261 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112200692 | ICE_C+BAKER | W | 121,979 / 131,845 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112194373 | FARME+FARME | W | 152,104 / 118,999 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 4v2 |
| 112187659 | BAKER+SMOOT | W | 101,100 / 68,203 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112181172 | BRUNC+BAKER | W | 121,611 / 99,695 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 4v2 |
| 112180931 | ICE_C+BAKER | W | 96,625 / 131,845 | d0: MELON 6v12, SHEEP 3v2 | d6: GOOSE 2v0 |
| 112176039 | PIZZA+YARN_ | W | 98,694 / 118,953 | d0: MELON 6v12, SHEEP 3v2 | d9: TOMATO 6v0, land 3v2 |
| 112175311 | ICE_C+PIZZA | W | 154,297 / 135,586 | d0: MELON 6v12, SHEEP 3v2 | d9: GOOSE 3v0, land 3v2 |
| 112170306 | SMOOT+ICE_C | W | 118,331 / 130,693 | d0: MELON 6v12, SHEEP 3v2 | d9: land 3v2 |


---

## `reports/claude/20260925-2005-PARENT-TOURNAMENT.md`

# PARENT-TOURNAMENT (Claude 요약·검토) — 2026-09-25 20:05 KST

원 보고: `coordination/reports/codex/20260925-1955-PARENT-TOURNAMENT.md` (workflow 자동 작성). 이 문서는 그 표를 요약하고 교차검증한 결과다. [LOCAL] 전부 Mac 로컬, engine 1.32.7. hosted 우위 아님.

## 결과
고유 파일 32개 중 gate 통과 28개 (탈락 4개 = `V92_SELL_LIB` 환경변수·`open(path)` 외부 의존: DP 178ae0f7, 9f5e8924, 12ad317e, 3ec06d07 — DP 는 상대 기준점으로만 사용).

| 순위 | SHA | 계열 (scan 이름) | screen DP40 / NEW40 | confirm DP80 / NEW80 | 이력 최대 step |
|---|---|---|---|---|---|
| 1 | e496a4fe | **127ed3e6 과 동일 행동** (`kaggriculture`) | 0.80 / 0.50 | 0.875 / 0.50 | 0.192s (242경기) |
| 2 | 127ed3e6 | NEWMETA cha22 (주류 4개) | 0.80 / 0.50 | 0.875 / 0.50 | 0.751s (1,392경기, stage1 6-worker) |
| 3 | cda529cb | 2965 master hybrid | 0.625 / 0.30 | 0.75 / 0.2125 | 0.183s |
| 4 | 8378f73c | shepherds-ledger herd-safe (09-25) | 0.525 / 0.25 | 0.525 / 0.20 | 0.347s |
| 5 | 37d284d4 | harvest-ledger (09-24) | 0.50 / 0.20 | 0.50 / 0.125 | 0.192s |
| (보충) | ae44d83b | shepherds-ledger herd-safe (09-24) | 0.475 / 0.20 | 실행 중 (correction) | 0.293s |

## 교차검증에서 새로 확인한 것
1. **e496a4fe ≡ 127ed3e6 (행동 동일)**: 두 파일이 같은 (상대, seed, 좌석)에서 둔 경기 242/242 전부 action SHA 가 같다. 줄 수도 7,482 로 같다. → D5 의 "127ed3e6 과 다른 계열" 후보가 **아니다**. 두 번째 슬롯 다양화 후보로 쓰면 안 된다.
2. **workflow 의 gate 정정(reconcile)이 옛 기준 0.5초를 쓴다**: `tools/search_calibration.py` `reconcile_tournament()` 는 이력 최대 step ≥ 0.5초인 SHA 를 부모 후보에서 뺀다 → 127ed3e6 제외, ae44d83b 가 보충 confirmation 중. 이는 D3 (0.8/1.0초, 사람 결정)와 불일치한다. 다만 잠정 부모가 e496a4fe(행동 동일)라서 **탐색 부모의 행동은 사실상 127ed3e6 과 같다** → 지금 루프를 멈출 이유는 아니다. e496a4fe 가 0.5초를 통과한 것은 1,000경기 부하 측정을 안 받았기 때문이지 더 빨라서가 아니다 (같은 연산).
3. 계열이 다른 파일 중 DP 상대 최고는 cda529cb (0.75) 이지만 NEWMETA 상대 0.21 로 크게 진다.

## 슬롯 B·두 번째 슬롯에 주는 의미 (D4·D5)
- D4 는 127ed3e6 exact 그대로. e496a4fe 로 바꿀 근거 없음 (행동 동일, 공개 추천 4개가 127ed3e6).
- D5 "다른 계열 & metric 0.05 이내" 후보는 현재 로컬 직접 대결 기준으로는 **없음** (차이가 가장 작은 cda529cb 도 합계 0.46 vs 0.65). metric 동결 후 다시 판정.

## 재현
`python3 - <<...` 없이 확인하려면: `experiments/search_20260925/games.jsonl` 에서 `result.sha256` 이 e496a4fe…/127ed3e6… 인 행을 (opponent_sha256, seed, seat) 로 맞춰 `result.action_sha256[seat]` 비교. 이력 최대 step 은 같은 파일의 `result.timing[0].max_seconds` 최대값.


---

## `reports/claude/20260926-2000-EXP024-STAGE3.md`

# EXP-024 Stage 3 — SUCCESS, 선택 v074 (Claude, 2026-09-26 20:00 KST)

Codex 가 사용 한도에 걸린 동안 실행된 5,604/5,604 경기를 Codex 의 `judge_stage3.py`(카드 기준 그대로)로 판정했다. 결과: `experiments/exp024_round2/stage3-summary.json`.

| 후보 | A vs v171 (Wilson99 하한) | A′ vs 127ed3e6 Δ (하한) | B DP Δ (하한) | C 나쁜 파일 | D 통합 Δ (하한) | H hosted Δ (하한) | E | 판정 |
|---|---|---|---|---|---|---|---|---|
| v111 | 0.850 (0.798) | +0.065 (+0.013) | −0.025 (−0.105) | 10개 | −0.129 (−0.181) | −0.107 (−0.182) | 0 invalid | FAIL |
| v169 | 0.598 (0.533) | +0.010 (−0.010) | 0 | 0 | 0 | 0 | 0 invalid | FAIL (A) |
| **v074** | **0.725 (0.664)**, 207/166/27 | **+0.138 (+0.105)** | 0.000 (−0.030) | 0 | +0.003 (−0.010) | 0.000 (0.000) | 0 invalid, 최대 0.327s | **PASS** |

- v111 은 복제본 상대로는 가장 강하지만 공개 파일 10개와 hosted 상대에서 크게 무너진다. guard 가 제 역할을 했다.
- release `releases/round2-v074/`: main.py sha 860a502c… (= variants/v074.py, v171 + `V9_RACE_DEFAULT` 44→45). submission.tar.gz sha a8f43236…, USTAR 형식, xattr 없음, main.py 한 파일.
- D3 gate v2 (cloud Linux x86, 새 프로세스, 15경기): 최대 step 0.178s, step 0 최대 0.156s, 경기당 누적 최대 1.41s, 예외 0 → PASS. `gate-d3-cloud.log`. (스크립트 끝의 stage1-summary 참조 단계는 클라우드 사본에 파일이 없어 실행되지 않았다. 측정값에는 영향이 없다.)
- E-5: tar 단일 파일·sha 일치, 마지막 callable `exp024_entry`, 외부 의존 없음(부모와 같음), Stage 3 1,501경기 invalid 0, 최대 step 0.327s.
- 제출하면 FIFO 에 따라 127ed3e6 exact(56549720)가 은퇴한다. 슬롯은 {v171, v074} 가 된다.


---

## `reports/claude/20260926-2140-EXP025-ANALYSIS.md`

# EXP-025 분석 — v171 은 누구에게 지는가 (Claude, 2026-09-26 21:40 KST)

## 독립 검증 (antigravity 수집분)
- 107/107 경기: 목록, replay, seed, 승패, margin 이 모두 일치한다(Claude 가 raw replay 에서 직접 계산).
- FULL 라벨 검증: v171 vs 127ed3e6 FULL 3판(113676012, 113615445, 113608331)을 로컬에서 같은 seed·좌석으로 돌리면 **hosted 보상이 정확히 재현**된다 → 엔진·라벨·v171 바이트 모두 정확하다.
- 누락: 카드 1단계의 127ed3e6 exact(56549720) 경기와 5단계(복제본 경기)는 수행되지 않았다.

## v171 hosted 101판 (53승 13무 35패)
| 상대 유형 | n | 승/무/패 | 점수율 | 평균 margin |
|---|---|---|---|---|
| 127ed3e6 FULL 복제본 | 26 | 16/10/0 | 0.81 | +48 |
| **127ed3e6 변형(중간에 갈라짐)** | **22** | **3/3/16** | **0.20** | **−358** |
| 공개 파일과 무관(prefix 0) | 23 | 14/0/9 | 0.61 | +14,874 |
| 다른 공개 계열 변형 | 24 | 14/0/10 | 0.58 | +4,382 |
| 다른 공개 FULL | 6 | 6/0/0 | 1.00 | +1,680 |
- 2400+ 상대: 127ed3e6 변형 0/6, 무관 봇 3/8, 다른 계열 변형 2/5.
- **가장 큰 구멍은 127ed3e6 을 몰래 고친 다른 팀들**이다(전체 경기의 22%, 점수율 0.20).
  - 이들은 49–632 step 동안 127ed3e6 과 똑같이 움직이다가 **판매 시점·수량을 아주 조금 바꾼다**. 예: 한 턴 먼저 MILK 3 판매, MILK 6 대 우리 5, WHEAT 판매 한 턴 보류.
  - 차이는 몇백 코인이다. 우리가 v171 로 한 것과 **같은 칼날 게임을 우리보다 잘하고 있다.**
- 이 팀들의 코드를 복원할 수 있는지 시험했다: 127ed3e6 의 단일 ±1 변형 186개 중 어떤 것도 갈라지는 지점을 넘어서 일치하지 않았다(2 episode, 0/171, 0/135). → ±1 조정이 아니다. 복원 가설은 폐기한다.

## 결론과 R3 방향
- R3 목표 = **127ed3e6 변형 팀들의 tape 상대 margin 을 올리는 v074 의 ±1 변형**. 조건은 127ed3e6 FULL·v171·v074 상대 비열등, 그리고 일반 guard(DP, 공개 19개, hosted 121판)다.
- tape 표본이 22판이면 과적합 위험이 크다. 그래서 **변형 팀들이 127ed3e6 FULL 복제본과 둔 경기**를 추가로 모은다. 상대가 우리와 같은 행동을 하므로, 그 경기의 변형 팀 행동은 우리 상대로도 유효한 tape 다. → EXP-025b (antigravity).
- 기대 이득(근사): 변형 팀 상대 0.20 을 0.50 으로 올리면 전체 점수율 +0.066, rating 으로 약 +40.


---

## `reports/claude/20260927-1225-TOP1-NOTEBOOK-CHECK.md`

판정: CLOSE — vote 1위 notebook(kaggricult-man) 제출물은 loader 상 no-op(매 턴 PASS), loader 수정본도 v074 에 0/20(평균 margin −2,090). 상세: Project doc claude/26_TOP1_NOTEBOOK_CHECK_2026-09-27.md
- packaging: 12ad317e(= a-song-of-ice-and-fire main.py) 바이트 그대로 단일 member tar. 우리 dataset 사본 853472b4 는 다른 버전.
- License/Rules: Apache-2.0 header, Rules 3.6.b/2.6.a 상 평가·참고 OK. 성능상 사용 이유 없음.


---

## `reports/claude/20260928-2010-EXP043-VERDICT.md`

# EXP-043 판정 — NO CLUE (Claude 09-28 20:10 KST)
검증: games43 3,900행, 중복 0. Mac VM 에서 3경기 재실행(O127·PUB08·d157) → rewards·act_sha 3/3 일치. G2600·G2602 는 entrypoint TypeError 로 260행 무효(각 130), 판정에서 제외.
1차(judge43.py): 규칙 "패배판 ≥10 승 AND 팀 Δ≥+0.15" 에 16개 bot 해당. 단 bot 은 d157 패배판만 실행돼 팀 Δ 가 상한값(d157 승리판 유지 가정).
보완 EXP-043b(PREREG_43b.md sha 8a28bf0f…, 결과 전 기록): CLUE 16 bot × d157 승리 tape 49 = 784경기 → 팀 전체 점수로 같은 규칙 재적용.
결과(verdict43b.txt): 해당 0. 최대 팀 Δ = PUB08/PUB10 thisray +0.138, DP0924/PUB03 Shawn404 +0.100. 5팀 합계 Δ 는 +0.011~+0.028 (c26 +0.034 가 더 높음).
해석: 127 계열·공개 bot 은 d157 이 근소하게 진 판(대부분 margin −1~−1,100)을 11–13개 뒤집지만 d157 이 이긴 판을 6–9개 잃는다 → 체계적 우위가 아니라 근소한 판의 교환.
결정(사전 규칙): 새 탐색 중단, d157 + c26 유지 권고. 추가 제출 없음.
파일: analysis/exp043_oracle/{judge43.py, result43.json, PREREG_43b.md, jobs43b.json, games43b.jsonl, judge43b.py, verdict43b.txt}
다음: 09-29 09:00 KST C26HOSTED 카드(coordination/proposals/claude/20260929-C26HOSTED-ANTIGRAVITY.md) → 분석 계획 analysis/c26_hosted_20260929/PLAN.md


---

## `reports/claude/20260929-1330-EXP056-057-VERDICT.md`

# EXP-056 · EXP-057 판정 (Claude 09-29 13:30 KST)

VERDICT | 둘 다 FAIL. 통과 후보 없음 → 현 방침(A: 제출 없이 d157 + c26 유지) 그대로.

## EXP-056 공개 Step1009 계열 7개 (PREREG experiments/exp056_pubscreen/PREREG.md)
tape 269(exp051_curpop), bot − d157, 상대 단위 bootstrap. 판정 스크립트 judge56.py, 결과 verdict56.json.
| bot | Δ vs d157 | 95% 하한 |
|---|---|---|
| D(55be exact), FJ1010, HL63, HL8c | −0.061 | −0.09 |
| M2965 | −0.024 | −0.065 |
| SHEP | −0.416 | −0.48 |
| V53 | −0.476 | −0.54 |
주의: 사전등록은 "팀 무관 bootstrap"이었으나 meta 에 상대 팀 이름이 없어 상대 submission(=tape) 단위로 했다. 결론에 영향 없음(모두 점추정 음수).

## EXP-057 거위 확대 (PREREG experiments/exp057_geese/PREREG.md sha b99f38d8…)
근거: SURVEY300 top100 거위 4.5–5.9 vs 우리 1.5–2.4, EGG 가격 곡선(log) 둔감.
| 변형 | Δ vs d157 | 95% 하한 | Δ vs c26 | 바뀐 판 | 바뀐 판 Δ |
|---|---|---|---|---|---|
| G1 거위→타 가축 전환 3층 끔 | −0.061 | −0.091 | −0.091 | 45 | −0.367 |
| G2 소→거위 전환 문턱 완화 | −0.047 | −0.089 | −0.076 | 96 | −0.130 |
| G3 G1+G2 | −0.110 | −0.158 | −0.139 | 127 | −0.232 |
해석: d157 의 shop 조건부 가축 선택(HERD/HERD2/v44y/COWSWAP)은 제 역할을 한다. 상위 팀의 거위 수는 다른 계열 봇의 통합 계획의 일부이지, d157 에 옮겨 붙일 단일 요인이 아니다(토마토 EXP-054/055 와 같은 결론).

## SURVEY300 교훈
상위권 행동 차이(딸기↓, 거위·토마토·밀↑, 둘째 땅 조기)는 계열 차이가 섞인 상관이다. d157 단일 knob 로 옮긴 두 시도(토마토, 거위)가 모두 크게 졌다.
부가 사실: 밀 대량 매매(top 1,300 매수/1,500 매도)는 사고파는 단가가 같아(≈39–40) 순이익 차이가 작다(top100 10.5k vs 우리 8.6k).


---

## `reports/claude/20260929-1650-EXP058S-VERDICT.md`

# EXP-058 Stage S 판정 (Claude 09-29 16:50 KST)
VERDICT | **FAIL** (사전등록 PREREG sha 75a8125e…, 판정 judge58S.py sha f2579d0d…, 결과 verdictS.json). 1,345행, 무효 0.
선택 규칙 S->107: 전체 Δ +0.0242(≥0.02 충족) · 그룹 안 Δ +0.054, 95% 하한 −0.0125(>0 불충족) · c26 대비 −0.0056(≥0 불충족). 바뀐 판 23/120.
차순위 D->107: Δ +0.0149(불충족), 하한 +0.0125, c26 대비 −0.0149, 바뀐 판 6/80. 나머지 11개 규칙은 모두 Δ ≤ +0.0074, Y 그룹 변경·route 9·0 은 크게 음수(−0.04 ~ −0.18).
해석: d157 의 yarn 쌍 route 9 는 강하게 맞다. 비-yarn 쪽에서 route 107 이 약간 나을 수 있다는 신호가 있으나 사전 기준에 못 미친다. PREREG 에 따라 Stage C 는 하지 않는다.
사후 관찰(판정 아님): S->107 과 D->107 을 합친 "비-yarn 쌍 → 107" 은 현재 tape 에서 약 +0.039. 이는 Stage S 자료에서 나온 사후 가설이므로 쓰려면 새 번호로 사전등록하고, 선택에 쓰지 않은 panel(H219 · F228 · FAM250)에서만 판정해야 한다.


---

## `reports/claude/20260929-CLAUDE-INDEPENDENT-ASSESSMENT.md`

# Claude 독립 검토 — 2300+ 로 가는 길 (Codex FIRSTPRINCIPLES 중간 보고를 보기 전에 작성·봉인)
작성: 2026-09-29, Claude. 이 파일의 sha 를 Codex 중간 보고 열람 전에 기록한다.

## 1. 현재 수준 (C26HOSTED 269경기, 상대 LB 점수로 Elo-400 성능 레이팅 추정)
- d157: 전체 2207, 최근 절반 2097, 최근 1/3 2062 → 표시 2216 은 아직 내려갈 여지가 있다.
- c26: 전체 2096, 최근 절반 2081, 최근 1/3 2120. 표시 1887 은 717 출발 후 수렴 지연으로 보인다.
- 결론: 둘 다 실제 약 2100. 2300 은 +200, 같은 수준 상대에게 기대 점수 약 0.76 이 필요하다. 작은 조정(+0.01–0.05)으로는 닿지 않는다.

## 2. 판이 갈리는 곳
- 같은 계열 상대 91경기: 공개 55be 와 같은 상대에게 18승 0패 7무, 비공개 변형에게 20승 44패. 격차는 수십–수백 코인.
- 부호가 마지막으로 바뀌는 step 중앙값: 승 565, 패 575. 막판 결정이 아니라 Q2–Q3 에 조금씩 벌어진다(패배판 money 차 −23@576 → −224 최종).
- 정확 재생 품목별(83경기, parity 83/83): 판매 수량은 같고, 패배판에서 WOOL −230, STRAWBERRY −161, CARROT −109, MILK −79, FERTILIZER −47 의 가격·시점 차이. 전부 수백 코인 규모.
- 최종 money 수준은 상위 팀과 우리 모두 93k–104k 로 같다 → 생산 총량 격차가 아니다.

## 3. 오늘 닫은 가설
- 상대 판매를 완벽히 아는 front-run(oracle, 기존 _front_run hook 에 실제 미래 tape 주입, 91경기): 0.462 → 0.434. 선매도 방식은 완벽한 정보로도 이득이 없다.
- 같은 step 같은 품목 슬롯 선후: 승·패 모두 2%/2% 대칭.
- 승자 변형의 이탈은 경기당 약 15 step 이고 종류가 제각각 → 단일 규칙으로 흉내 불가.

## 4. 구조적 지렛대 후보 (근거 순)
L1 **공급 부족 품목(TOMATO) 활용** — 가장 유력.
  - 90경기 시장 가격: 후반 STRAWBERRY 36–44(기준 120), MILK 39–49(160), WOOL 24–55(200) 로 모두가 과잉 공급. TOMATO 만 기준가(60) 이상, 중앙값 78–84, 최대 528.
  - day 18 까지 TOMATO 소비 shop(PIZZA, FARMERS_MARKET)이 2개 이상인 판 44%: TOMATO 가격 93@600, 130@700, 부족분 286. 50개를 더 팔면 매출 중앙값 약 3.8k(엔진 가격식).
  - 상위 팀도 step 576 에 토마토 밭 2–3칸 뿐 → 누구도 이 수요를 가져가지 않는다.
  - d157 에는 이미 조건부 토마토 투자 모듈 _V219(main.py:1265–1335, day 18 에 4번째 땅 + 토마토 10개)가 있지만 발동 조건이 좁다: shop ≥3(90경기 중 16), 가격 ≥70, money ≥12000, 땅 상태 등. tape 6판 REPORT 에서도 발동 0.
  - 주의(공유 시장 산수): 이미 과잉인 품목(STRAWBERRY 등)을 줄여 토마토로 바꾸면 그 품목 가격이 오르며 상대도 같이 이득을 본다. 이득은 새 땅·빈 칸·저가치 칸에서 토마토를 더 만드는 경우에 순수하다(V219 설계가 바로 그 형태).
  - 시험안: V219 발동 조건 완화(shop ≥2, 가격 기준 유지 또는 완화, day 15–18). 현재 상대 집단 tape(EXP-051 + HOSTEDPM) 로 판정.
L2 수요 regime 에 따른 후반 품목 배분 전반(shop 구성으로 품목별 후반 가격을 예측해 파종·가축 투자 조정). L1 의 일반화. 시간상 L1 먼저.
L3 두 슬롯 운용: c26 과 다른 방향의 후보를 넣어 최댓값 기대를 올린다. L1 후보가 그 역할도 한다.
기각·후순위: front-run 류(오늘 oracle 로 기각), 슬롯 순서, 막판 청산(남는 재고 0), 생산 총량.

## 5. Codex 결과와 비교할 기준
- Codex 가 L1(또는 수요 기반 품목 배분)을 찾았는지, 다른 구조적 지렛대를 근거와 함께 냈는지.
- c26 tape/hosted 모순 설명이 1번의 성능 레이팅 추정과 맞는지.
- 평가 panel 이 현재 상대 집단 tape 를 주로 쓰는지, 시간 분리 holdout 이 있는지.


---

## `reports/claude/20260929-EXP045-047-VERIFY.md`

# EXP-045 v2 / EXP-047 산출물 독립 검증 (Claude)
- EXP-045: parent sha 일치. 11 변형 sha 가 manifest 와 일치. K1–K8 은 d157 대비 정확히 1줄(모듈 apply 의 조기 return 또는 parent 직접 반환)이고, 위치가 카드의 모듈과 맞는다. G_A 115줄·G_B 116줄·B6 132줄은 파일 끝에 추가되며, G_A 상수(4/1.15, 5/1.08)를 확인했다.
- EXP-047: hook.py 는 d157 전체 바이트 + 110줄 추가. shadow 55be 를 base85 로 내장해 외부 파일 의존이 없다(Kaggle 번들 안전). shadow sha 는 manifest 와 일치.
- jobs: 4개 파일 모두 holdout 팀 0, seed 9000–9599 0, seed·our_seat 이 meta 와 일치, 중복 key 0. EXP-045 6,545 = 11×595, EXP-047 595.
- 재실행: K4·hook 각 1판을 Mac VM 에서 직접 돌림 → DONE/DONE, 719 actions, 오류 0, max step 0.072s / 0.170s.
- 주의: EXP-047 추정 상태 예측 precision 0.114(상한 0.553). 오탐이 많아 front-run 이 과하게 발동할 위험이 있다. 사전 규칙대로 Stage A 에서 판정한다.
- 실행: 두 jobs 를 합쳐 experiments/exp048_stageA/ (7,140) → 카드 20260929-EXP048A-ANTIGRAVITY.md.


---

## `reports/claude/20260929-EXP048A-VERDICT.md`

# EXP-048 Stage A 판정 (Claude 09-29) — Stage B 진출: hook, K3
판정 스크립트 analysis/exp045/judge48A.py (sha ded9d29b…, 결과 전 작성). select 594 tape, d157 0.400, c26 0.439.
| 변형 | Δ vs d157 | flips | team-boot lo95(참고) |
|---|---|---|---|
| hook(EXP-047) | +0.0109 | 13 | −0.003 |
| K3(_S758 끄기) | +0.0042 | 37 | −0.013 |
| K7 −0.005, K6 −0.006, K5 −0.018, K4 −0.021, K2 −0.024, K8 −0.033, B6 −0.080, K1 −0.086 | | | |
| G_A, G_B | −0.390 | 232 | 판매 보류 규칙이 판매를 거의 막음(구현 또는 규칙 결함) |
- invalid: 모든 변형이 같은 1개 tape(X114488298)에서 실패. tape 의 JSON null 결함으로 d157·c26 기준선(games42)도 같은 tape 에서 실패해 기준선 594 에서 이미 빠져 있다. 변형 문제가 아니므로 모든 변형에서 제외했다(스크립트의 invalid 0 조건은 이 tape 를 뺀 뒤 적용한 것과 같다). 이 해석은 결과를 본 뒤 밝히는 것이므로 기록한다.
- 해석: 두 진출 후보 모두 효과가 작다(±SE 약 0.01 수준). c26 이 select 에서 +0.039 로 더 크다. 모듈 끄기는 대부분 손해 → 판매 모듈들은 상위 팀 상대로도 대체로 도움이 된다. K1(_OR2)·B6 가 가장 크게 손해.
- 다음: EXP048B(hook, K3 × exp039 panel + old holdout 148 + fresh tape; fresh 에는 d157·c26 기준선 포함). 판정 experiments/exp048_stageB/judge48B.py (sha 7bde61ea…, 결과 전 작성).
- 기타: 공개 다른 계열 multi-route c94(scan DIFFERENT) vs d157 closed-loop 20판 0승(margin −18k~−52k) → 위협 아님.
- fresh tape(exp049): 305 새 경기, parity 300/303(3개 제외), H 74 / F 231. prep49·parity49.


---

## `reports/claude/20260929-EXP048B-C26HOSTED.md`

# EXP-048 Stage B 판정 = FAIL(엄격·R2 모두) + C26HOSTED 분석 (Claude 09-29)
## Stage B (judge48B.py; 첫 실행 KeyError → 'F'+episode 키가 family 상대 'FJ1010' 과 충돌하던 버그만 수정, 기준 불변, v1 보존)
| panel | hook | K3 | d157 | c26 |
|---|---|---|---|---|
| U 136 | .640 | .529 | .640 | .636 |
| T 350 | .789 | .771 | .794 | .829 |
| family Δ vs d157 | +.004 | −.192 | 0 | (+.104, EXP-039) |
| vs D Δ | −.04 | −.24 | 0 | |
| O127 / V074 | .88/.88 | .84/.84 | .88/.88 | |
| 주 holdout H 219 (148+71) | .448 | .420 | .457 | .470 |
| 보조 F 228 Δ | +.009 | −.004 | | |
→ hook, K3 모두 엄격·R2 로컬 조건 불통과. EXP-045/047 계열 종료. (A2: hook 은 Stage A 를 통과했으므로 A2 진단 대상 아님)
## C26HOSTED (as_of 09-28 17:27 UTC; c26 82경기, d157 187경기)
- c26 0.799: <2000 67경기 .85, 2000–2200 8 .69, 2200–2400 5 .60, 2400–2600 2 0. 시간 순 3분할 .93→.78→.72 (상대 LB 중앙값 1496→1788→1901). → 레이팅이 아직 오르는 중. 같은 구간에서 d157 보다 나쁘다는 증거 없음(표본 작음). R2-4/A4 발동 안 함.
- d157 0.524: 2000–2200 .67, 2200–2400 .46(09-27 .695), 2400–2600 .12. 시간 순 .81→.51→.26 (상대 1–2위 중앙값 2035→2251→2296). 55be5d5f 계열 상대 38W 45L 8D.
  → d157 하락은 2200–2400 구간에 55be/Step1009 계열 상대가 늘고 그들에게 절반 이하로 지기 때문으로 보인다(관찰, 인과 미확인).
- 로컬 근거도 c26 우위: 2400+ 742 tape .449 vs .416, family arena +.104, 주 holdout .470 vs .457, T .829 vs .794.
## 권고
활성 d157 + c26 유지. 다음 제출은 d157 을 은퇴시키므로, c26 보다 나은 근거가 있는 후보만 제출한다(현재 없음).


---

## `reports/claude/20260929-EXP050-051-LOSS-ANALYSIS.md`

# 패배 기록 분석 EXP-050/051 (Claude 09-29)
## EXP-050 d157 이 실전에서 만난 55be 계열 상대 91경기 (C26HOSTED raw)
- 상대의 기록된 관측을 55be exact 에 넣어 행동 차이를 셌다(div50·fp50·events50).
- 공개 55be 와 완전히 같은 상대: 18승 0패 7무. d157 은 공개 55be 를 이긴다.
- 우리를 이긴 45경기 상대는 공개 파일(D, M2965, HL63, 새 harvest-ledger 8cffc452, FJ1010) 어느 것과도 일치하지 않는다 = 비공개 변형. 55be 와 다른 step 은 중앙값 15개이고 대부분 후반부(Q2·Q3)다.
- 이런 비공개 변형 상대 전적: 20승 44패(약 0.31). 격차는 −1, −8, −32 처럼 아주 작다.
- 차이의 종류는 다양하다(주문 변경 25/경기, 순서 교환 4, 농부 행동 7). 같은 step 같은 품목의 슬롯 선후는 승·패 모두 2%/2% 로 대칭 → 한 가지 반복 규칙으로 흉내 낼 패턴은 찾지 못했다.
## EXP-051 현재 상대 집단 tape (d157·c26 실전 상대 269경기)
- 재현: d157 자기 경기 187/187, c26 자기 경기 82/82 결과 일치.
- c26 − d157 (같은 269 tape): 전체 +0.030 (SE .019), 55be 계열 +0.048, 2200–2400 구간 +0.056 (SE .038), 2400+ +0.053, 2000–2200 −0.012.
- 결론: 현재 레이팅 구간 상대 집단에서도 c26 이 d157 보다 낫다는 쪽이다. c26 실전 점수(1887)는 717 에서 출발해 아직 수렴 중이다.
## 권고
- 평가 panel 은 과거 상위 24팀보다 "현재 상대 집단 tape"(EXP-051, 매일 갱신 가능)가 레이팅에 직접적이다.
- 활성 d157 + c26 유지. 새 제출은 c26 과의 최댓값을 올리지 못하면 의미가 없다.


---

## `reports/claude/20260929-EXP054-TOMGATE.md`

# EXP-054 토마토 투자 조건 완화 — Stage 1 FAIL (Claude 09-29)
사전등록 experiments/exp054_tomgate/PREREG.md (sha 8021d5be…, 결과 전). 부모 c26. 단일 요인 _CXTB_MIN_REVENUE 9000 → X7 7000 / X6 6000.
현재 상대 집단 tape 269 (invalid 0):
| 변형 | Δ vs c26 | 투자가 새로 열린 판 | 그 판들의 Δ | margin Δ 중앙값 | W→L / L→W |
|---|---|---|---|---|---|
| X7 | −0.004 (SE .006) | 15 | −0.067 | +156 | 2/1 |
| X6 | −0.084 (SE .018) | 73 | −0.308 | −864 | 25/2 |
→ 둘 다 FAIL. 기존 기준 9000 은 근거가 있었다: day 18 에 땅 4000 + 씨앗 500 + 고용을 들여 day 26–29 나흘만 수확하는 구조는 기대 매출이 낮은 판에서 손해다.
해석: "후반 한 번에 땅을 사서 토마토를 심는 55be 방식"을 더 자주 여는 것은 답이 아니다. 상위 팀 중 이득을 보는 Fritz 는 구조가 다르다(day 6·8 땅, day 9 부터 연속 파종, 후반 딸기 → 토마토·당근). 그 구조를 옮기는 것은 route(작업 일정) 재설계라 큰 작업이다.


---

## `reports/claude/20260929-EXP055-FRITZ11.md`

# EXP-055 Fritz-lite (day 11 딸기 13그루 → 토마토) — Stage 1 FAIL (Claude 09-29)
사전등록 experiments/exp055_fritz11/PREREG.md (sha 4d4abc56…, 결과 전). rev1 진입점 버그(부모 callable 오지정, smoke reward 3000)는 결과 전에 수정(rev2, manifest 기록).
현재 상대 집단 269(invalid 0): F11 Δ −0.372 (margin 중앙값 −8,400, 승→패 115), F11c Δ −0.234 (바뀐 164판 −0.384).
원인(8판 품목 분해, c26 대비): 딸기 매출 −7.4k(247 → 136개), 토마토 매출 +1.2k(10 → 51개). day 11 딸기 배치는 비료로 그루당 약 8개를 내고 평균 약 66 에 팔린다(시장 종가 36–44 가 아니라 실제 체결가). 토마토는 4회 수확 후 소멸해 그루당 약 3개.
결론: 딸기를 토마토로 단순 치환하는 것은 크게 손해다. 토마토가 이득이려면 Fritz 처럼 12일마다 다시 심는 연속 파종·비료·인력 설계가 필요하다(대규모 재설계, 근거 약함). 토마토 계열 실험은 여기서 종료한다.
교훈: 시장 가격(종가)으로 품목 가치를 추정하면 틀린다. 실제 체결가와 그루당 수확량(비료 포함)으로 계산해야 한다.


---

## `reports/claude/20260930-0200-EXP060M2-VERDICT.md`

# EXP-060 M2 판정 (Claude, 2026-09-30 02:00 KST) — 사전등록 137f92985e2f 규칙 그대로
확인 집합(M1 에 쓰지 않은 거울판) 384판, 1,791경기, 오류 0. judge_m2.py (c087d49b118e) → m2_verdict.json (411e62b14b1e).
| 그룹 | n | 최고 | 평균 | d157 | 차이 | bootstrap 90% 하한 | 107(X 방식) | 채택 |
|---|---|---|---|---|---|---|---|---|
| Y | 85 | DN29 (R95 donor) | 0.694 | 0.494 | +0.200 | +0.082 | 0.212 | DN29 |
| D | 126 | FM110 | 0.675 | 0.496 | +0.179 | +0.087 | 0.548 | FM110 |
| S | 173 | FM110 | 0.699 | 0.399 | +0.301 | +0.223 | 0.500 | FM110 |
- 표: 거울판 Y→donor route 929(DN29), D→110, S→110. 후보 cand/Cd_final.py (d157 기반), cand/Cc_final.py (c26 기반), manifest-final.json 3b6e1b552c17.
- 검증: Cd_final 이 세 그룹 확인 tape 에서 해당 arm 과 행동 완전 일치. VM D3: Cd max 0.246s, Cc max 0.236s, 오류 0, PASS.
- 참고(판정 아님): 확인 집합에서 d157 기반 107 규칙 대비 거울판 평균 약 +0.24. 전체 경기로 환산하면 거울판 비율(37–58%)만큼 줄어든다.
- 한계: 모두 open-loop tape. 거울판은 상대 반응 편향이 가장 클 수 있는 곳(Sol 지적) → M3 closed-loop 와 07:30 판독 A/B 로 확인.
- 다음: M3-A(HF 78 + closed-loop 480, 카드 20260930-EXP060M3A-ANTIGRAVITY.md) → 07:30 수집 → M3-N(NEW) → judge_m3.py final,finalN → 제출 조건 판정.

## 추가 점검 (03:20 KST, 판정 변경 없음 — 확인 집합 안에서 세분)
- 상점 쌍별: DN29 는 Y 15쌍 중 10쌍 +, 2쌍 −(YARN+YARN −0.25 n8, YARN+PET_CAFE −0.14 n7). FM110 은 D 21쌍 중 12 +/1 −, S 28쌍 중 23 +/1 −. 한 쌍에 몰린 이득이 아니다.
- tape 출처별: Y·S 는 모든 출처에서 +. D 는 09-26 전후 옛 panel(exp033 n8 −0.25, exp039 n11 −0.27)에서 −, 최근 panel(exp041 +0.18 n71, exp049 +0.41 n33, exp051 +0.50 n3)에서 +. 현재 상대 집단 쪽이 유리하다.
- Sol 2차 검토 요청문: coordination/reports/sol/20260930-0310-SOL-REQUEST2.md (ChatGPT 창이 전체 화면 Space 밖이라 전송 대기).


---

## `reports/claude/20260930-0815-EXP060-M3-READOUT-VERDICT.md`

# EXP-060 M3 + READOUT0930 판정 (Claude, 2026-09-30 08:15 KST)
규칙: PREREG 137f92985e2f + 보충 A1 80b37c145ac7 / A2 5af074028ded, 판독 계획 a762337d68aa. 자료: NEW 195판(X 76, d157r 119; as_of 07:30), HF 78판, closed-loop 480+160, 총 2,278경기, 오류 0. judge_m3.py 335d5b192bcb → m3_verdict-final+finalN.json.

## 0. 유효성: 자기 재현 195/195 일치, 우리 좌석 오류·시간 초과 0 → R1 해당 없음.

## 판독 (X 실전 대 d157)
| 구간 | A = X실전 − d157가상 | B = X가상 − d157실전 | B − A |
|---|---|---|---|
| 전체 | −0.079 (−0.145, −0.026), n76 | +0.004 (−0.059, +0.067), n119 | +0.083 |
| 거울판 | −0.312 (−0.562, −0.062), n16 | +0.020 (−0.081, +0.122), n74 | **+0.333** |
| 비거울 | −0.017, n60 | −0.022, n45 | −0.006 |
- 합친 추정 −0.028 (−0.074, +0.018) → 판정 불가(구간이 0 포함). 거울판 비율: X 경기 21%, d157 경기 62%.
- X 의 실전 거울판 16판 점수 0.25. 같은 판을 기록 재생하면 d157 0.562, c26 0.562, Cc 0.625 — 기록과 다르게 움직이는 봇이면 모두 +0.3 이상 좋아 보인다. 거울판에서 기록 재생 평가는 "기록과 다르게 움직인 쪽"을 크게 유리하게 본다(편향 추정 약 +0.17).

## M3 (기록 재생, HF + NEW 273판)
- Cc 0.659, Cd 0.667, X 0.615, d157 0.604, Cn 0.619. Cc − X +0.044 (−0.004, +0.095). portfolio Cc +0.059 (+0.027, +0.092).
- 거울판 그룹별 Cc − X: Y +0.467 (n30), D −0.068 (n44), S +0.015 (n65).
- 편향 없는 비교(둘 다 기록과 다르게 움직이는 d157 경기 거울판 74판): Cc − X +0.047 (−0.088, +0.176). NEW 에서 Cc 우위의 대부분은 X 경기 거울판 16판(+0.375)에서 나오는데, 그곳은 X 만 기록을 그대로 재생하는 편향된 비교다.
- closed-loop: Cc 0.550/0.550 대 X 0.525/0.562 (d157/55be exact 상대).

## 판정: FAIL (제출하지 않음)
- ① 전체 C−X ≥ 0 통과, ② 거울판 C−X > 0 통과(모두 기록 재생).
- ③ 판독에서 A ≤ 0 이고 거울판 B − A = +0.333 > +0.10 → closed-loop 기준이 C ≥ X 로 강화. Cc 대 55be exact 0.550 < X 0.562 → **불통과**. Cd 도 같음.
- 보충 A1 ⑥ 도 같은 이유로 불통과. Sol 1·2차 검토의 중단 조건과도 일치.
- 결정: {X, D'} 유지. 판독 계획 규칙("점수만으로 제출 변경 안 함")에 따라 X 도 그대로.

## 뜻
- EXP-058/059/060 과 SLOT2-R 의 거울판 route 이득은 대부분 기록 재생 편향일 가능성이 크다. 거울판에서 route 를 바꾸는 변경은 closed-loop 로만 판단해야 한다.
- X(거울판 107)의 실전 거울판 성적은 16판뿐이지만 나쁘다(0.25).


---

## `reports/claude/20260930-1145-EXP062-L4P-SUBMIT.md`

# EXP-062 — 실전 패배 분석 → 과잉 구간 선매 L4p 제출 (Claude, 2026-09-30 11:45 KST)
사전등록 experiments/exp062/PREREG.md (본문 + A1–A7). 사람 결정 09-30 08:20: 로컬 검증 + 실전 확인, Claude 직접 제출, 시한 21:00, 목표 "현재 점수대에서 지는 상대를 이기기".

## 1. 패배 분석 (실전 hosted 542판, 상대 LB 1750–2250 구간 293판)
- 패배 111 중 71(64%) = 비공개 55be 변형(113판 0.358). 공개 55be 원본 상대는 0.776, 다른 계열(prefix 0) 0.558.
- 55be 변형 패배의 현금 격차는 품목에 흩어져 있다(최악 품목 WOOL 16, CARROT 13, STRAWBERRY 13, WHEAT 12, MILK 7). 프리미엄 판매 대부분은 같은 step 에 동시 판매이고, 승패는 한쪽만 먼저 파는 판매에서 갈린다.
- 상대는 과잉 구간(가격 ≤ 기준가)에서 tape 계획 판매를 1 step 먼저(주로 hour 0) 판다. lag=1 사건 가치: 패배 5,498 코인(71판), 승리 454(39판). d157 은 과잉 구간에서 선매를 전혀 안 한다(RACEGATE 가 예약 선매를 막음).
- 첫 이탈 행동(firstdiv62, 118판): 패배에서 프리미엄 판매 변경 27%(MILK 8, WOOL 7, STRAWBERRY 5), 승리 9%. 첫 이탈 +SELL 은 패배에서 hour 0 이 가장 많다(10/37).
- 자료: experiments/exp062/loss/{sales62,cash62,firstdiv62}.jsonl

## 2. 후보와 평가 (모두 closed-loop, 상대 반응)
- L 계열 = d157 바이트 그대로 + tail: MILK·WOOL·STRAWBERRY 가 과잉일 때 tape 의 다음 K step 계획 판매를 지금 판다(step 192–695, 같은 debt 장부, 예외는 삼킴).
- S1(선택, 20 seed × 2 좌석, 55be 계열 7 상대, d157 대비 P): L3p +0.111, L4p +0.107, L3pE +0.111, L3a +0.118, L2p +0.075, L6p +0.039. 판매 모듈 끄기·파라미터 격자 16개는 모두 음수.
- S2(확인, 새 30 seed, pool + VP): L4p +0.060 [−0.002, +0.112], L6p +0.040, L3p +0.026, L2p +0.005. 엄격 조건 통과 없음.
- VP(1-step 선매 변형 = 실전 패배 기제의 대리) 상대: d157 0.45, L3p 0.65, L4p 0.733, L6p 0.75.
- S1+S2 합친 P: L4p +0.079 [+0.030, +0.126] > L3p +0.060 > L6p +0.040 → L4p.
- 손해 점검: 비거울 tape 220 Δ 0.000 / 처음 보는 공개 봇 10개 30 seed +0.002 [−0.022, +0.024] (HL63x 거울 상대만 −0.10, 판마다 ±50 코인의 동전 던지기) / D3 PASS(cloud x86 max 0.513s, 오류 0) / Sonnet 독립 검토 PASS.
- 평가 도구 점검(S1-cal): c26 P +0.054(구간 0 포함), X +0.004 (X 는 D55·HL63·FJ1010 상대 −0.2). 실전과 같은 방향(X ≤ d157). c26 은 약간 과대평가.

## 3. 결정
- 엄격 조건(S2 하한 > 0)은 0.002 차이로 미달. 사람 방침(메달권 밖이면 위험 감수 우선) + 교체 대상이 d157 이하 증거뿐인 X 슬롯 → 제출.
- 제출 56694892 (11:32 KST, 11:35 COMPLETE 600). 활성 {d157r 56675458, L4p 56694892}. X 은퇴. 오늘 남은 제출 4.
- 순위표 09-29 23:33 UTC: 동메달 경계 1916.2, Sian 1861.6 (1178위).

## 4. 실전 확인 (A5)
- 15:00 / 17:30 / 20:00 수집(analysis/hosted_0930d, subs.json). 20:30 판정: 오류·시간 초과 → 즉시 되돌림. 같은 상대 LB 구간 n ≥ 30 에서 L4p − d157r ≤ −0.15 → 되돌림.
- 되돌림 순서: d157 재제출(d157r 은퇴) → 다음 제출로 L4p 은퇴.

## 5. 운영 메모
- Mac 작업 대기열 experiments/exp062/q (runner.sh, 사람이 08:33 시작). 09:20–09:50 사이 Claude 세션 기억이 끊겨 파일(PREREG A1–A4, 설계, 판정 스크립트)로 이어받았다(COORD.md).


---

## `reports/claude/20260930-2335-EXP062-FINAL-A.md`

# EXP-062 최종 제출 (조합 A) — 2026-09-30 23:35 KST, Claude-B

## 결과
- 최종 활성 제출 = **L4pc 56709992** (L4p 사본, sha 3265b749…) + **d157c 56709342** (d157 사본, sha 94a46c11…). 둘 다 검증 COMPLETE.
- 은퇴: L4p 원본 56694892 (표시 1792), L5p 56705818 (표시 1695). 남은 제출 1회는 복구용으로 봉인.

## 왜 이 조합인가
- 실전 패배 원인: 55be 계열 변형이 과잉 구간에서 우리보다 먼저 팜 → L 계열(과잉이면 다음 K step 계획 판매를 당겨 팜)로 대응.
- S7d(100 seed): 원본(D55) 상대 약점은 L5p(K5)만의 문제. L4p ≈ d157 (D55), VP(선매 변형) 상대 +0.23.
- S8(Kaggle 2,160판, 오류 0): L5p−L4p −0.058 [−0.104, −0.011], d157−L4p −0.064 [−0.120, −0.004]. L4p 맞대결 d157 0.650, L5p 0.483.
- S9(Mac 1,880판, 오류 0, 사람 제안: 원본·d157·L5p 모두 이기기): A11 합격 후보 없음. 최선 X454(양털4·딸기5·우유4) 주 지표 +0.025 < 문턱 +0.03 → L = L4p.
- 포트폴리오: D55·M2965 에서는 d157, VP·L3 계열에서는 L4p 가 강함 → "둘 중 최대"로 서로 보완(Sol 동의).

## 실전 참고(22:42 수집)
- 상대 1600–1800: L5p 0.80(15) / L4p 0.73(46) / d157r 0.70(69); 1800–2000: 0.40(5) / 0.50(28) / 0.45(82); 2000–2200: – / 0.29(7) / 0.33(27).
- 1800 이상 상대에게 5할 미만 — 동메달(≈1916)까지의 남은 과제.

## 검증
- 두 제출 모두 release sha = 검증된 바이트, tar 왕복, D3 PASS(d157 은 6-worker 칸 누락 표기 오류 재평가, gate-d3-result-final.json), 실전 오류 0(d157r 213판, L4p 110판).
- 판정 규칙은 모두 결과 전 사전 등록(PREREG A11, A12), Sol(GPT-5.6) 7차 검토 동의.

## 남은 일정
- 05:45 자동 점검: 제출 상태·실전 오류·점수 요약. 07:15 안전 확인: 이상 시에만 복구 제출. 마감 08:59.

## 아침 상태 (10-01 05:47 KST 자동 점검)
- 제출 목록 맨 위 두 줄 = L4pc 56709992, d157c 56709342, 둘 다 COMPLETE. 실전 오류 0 (L4pc 68판, d157c 75판 + 각 검증 1판).
- 표시 점수(600에서 재수렴 중): L4pc 1587.0, d157c 1622.2 → 팀 1622.2, 순위 1855 / 10,230.
- 공개 LB 스냅샷(20:46Z): 동메달선(상위 10%, 1023위) 1852.0 (전날 1916에서 하락), 은메달선(상위 5%) 2079.2.
- 새 제출 실전(상대 LB 구간별 점수): L4pc <1600 0.96(47), 1600–1800 0.67(12), 1800–2000 0.60(5), 2000+ 0.00(4); d157c <1600 0.90(34), 1600–1800 0.50(29), 1800–2000 0.10(10), 2000+ 0.00(2).
- 복구 제출 불필요(오류 없음). 남은 1회 봉인 유지. 07:15 안전 확인 예정.

## 07:16 KST 안전 확인 — 정상
- 맨 위 두 줄 = L4pc 56709992 (COMPLETE, 1593.4), d157c 56709342 (COMPLETE, 1618.8). 실전 오류 0 (L4pc 71판, d157c 81판). 추가 제출 없음, 복구용 1회 미사용.
