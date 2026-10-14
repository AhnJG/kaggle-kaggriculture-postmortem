# coordination/proposals/claude — 113개 문서 묶음

원본 파일을 파일명(시간) 순으로 이어 붙였다. 각 절 제목이 원래 경로다.


---

## `proposals/claude/20260916-BRONZE-TARGET-PLAN.md`

# 제안 — 목표 변경: 최소 동메달. 그에 따른 슬롯 운용 재설계

발행 2026-09-16 21:45 KST · Claude(opus-5) · 수신 Coordinator(Codex) → 사람
**사람 결정 2026-09-16: 점수 유지 대신 최소 동메달 확보를 목표로 한다.**

## 1. 목표를 숫자로

Kaggle 메달 기준(팀 수 1,000 초과): 동 상위 10% · 은 상위 5% · 금 상위 10팀 + 0.2%.
09-10 공개 leaderboard snapshot `kaggriculture-publicleaderboard-2026-09-10T08:34:17.csv`, **8,481팀**:

| 목표 | rank | 필요 점수(09-10 기준) |
|---|---:|---:|
| **동메달 (top 10%)** | 848 | **≈ 2,303** |
| 은메달 (top 5%) | 424 | ≈ 2,566 |
| 금메달 | ~26 | ≈ 2,883 |
| (참고) 과거 목표 top 500 | 500 | 2,535.8 |

현재 활성 최고: **EXP-006 `56165718` = 1,862.6** (09-15 CLI).
**동메달까지 약 440점.** 경계값은 계속 움직이므로 최신 leaderboard 재수집이 필요하다(`N/A`).

## 2. 목표 변경이 무효로 만드는 기존 전제 3개

1. **"현재 A/B 유지가 기본값"** → 무효. 1,862.6 유지는 동메달 실패 확정이다.
   F-T12(제출 시 은퇴 봇의 경기 이력 소멸)는 여전히 참이지만,
   **메달권이 아닌 artifact 의 이력을 지키는 것은 가치가 0이다.**
2. **"release PASS 없이 제출 금지"** → 동메달 경로를 봉쇄한다.
   현재 활성 2개 모두 zero gate 를 실패하고 있으므로(F-T16) 이 규칙은 신규 제출을 전부 막는다.
   `WORK_ORDER_20260916_GATE_SCOPE_DECISION.md` 결정이 **선행 조건**이 됐다. 독립 검토자: **Codex**(사람 지정).
3. **`shed_discarded` correctness 우선** → 무효.
   회수 가치는 baseline 520~600 coin/경기(F-T16)이고 요구 격차는 440 rating point 다.
   `EXP-011` 진단 card 는 폐기하지 않되 **우선순위를 3순위로 내린다.**

## 3. 지금 남은 유일한 큰 미지수

| artifact | hosted | 관측 시점 | 상태 |
|---|---:|---|---|
| yhay81-exact 복제본 `56147691` | **2,188.4** | 접수 후 **7.3시간** — 수렴 전 | **은퇴** |
| EXP-006 = yhay81 + clone-preempt `56165718` | 1,915.6 → 1,896.9 → **1,862.6** | 09-12 → 09-14 → 09-15, 수렴 진행 | 활성 |
| EXP-007 = thomas-exact 복제본 `56175620` | 1,819.8 → 1,647.4 → **1,635.9** | 동 | 활성 |
| (참고) yhay81 원저자 본인 | 2,929.4 | 09-10 | 타인 |

**우리 layer 가 도움인지 손해인지 아직 모른다.**
`evidence/HOSTED_LEDGER.md:136,165,166` 이 이미 경고한 그대로다 —
2,188.4는 7.3시간 값이고 parent 는 은퇴해서 같은-window A/B 가 **불가능**하다.
로컬은 답을 주지 못한다: EXP-006 은 parent 를 **h2h 20-0-0** 으로 이겼는데(registry EXP-006 행)
hosted 는 더 낮다. AGENTS §7.1 의 K5 사례가 그대로 재현된 형태다.

한편 **layer 가 작동한다는 방증**도 있다(F-T17):
EXP-007(복제본, layer 없음)은 50판 중 **무승부 9판이 전부 마진 정확히 0** — 같은 공개 노트북
복제본끼리의 완전 대칭 경기다. EXP-006(layer 있음)은 무승부 **0판**이다.
즉 **필드에 공개 노트북 복제본이 다수 존재하며, 복제본을 그대로 올리면 자기 클론에게 0.5점만 얻는다.**

→ 이 불확실성을 남겨둔 채로는 동메달 경로를 고를 수 없다. **슬롯을 써서 답을 사야 한다.**

## 4. 제안하는 슬롯 운용 — 사람 승인 대상

원칙: **메달권이 아닌 artifact 는 지키지 않는다. 슬롯은 정보를 사는 데 쓴다.**

**제출 1 (즉시 결정 대상): `yhay81-exact` 재제출**
- artifact `releases/public-yhay81-shop-router-0909-exact/`, tar SHA 는 재빌드 후 확정 필요
  (기존 제출 파일 SHA `40d2bc39…d7791` 은 사람 확인 미완 — ledger:133~134)
- 결과 슬롯: `[EXP-007 1,636 → yhay81-exact]`. **EXP-006(1,862) 이 은퇴한다.**
- 얻는 것: yhay81-exact 의 **수렴 점수**. 이것이 2,100 이상이면 layer 는 손해였고
  동메달 경로는 "yhay81 계열 + 소폭 개선" 이다. 1,900 이하면 layer 는 무해했고
  2,188 은 수렴 전 착시였다는 뜻이며, **공개 복제본만으로는 동메달이 불가능**하다는 결론이 선다.
- 잃는 것: EXP-006 의 경기 이력. 1,862 는 메달권이 아니므로 목표상 손실 가치 0.
- **판독 시점 고정:** 제출 +24h / +72h, 각 직전 24시간을 별도 window 로(계획 §7).

**제출 2 (제출 1 결과 이후):** 위 분기에 따라 결정. 지금 정하지 않는다.

**하지 않는 것**
- 같은 tar 재제출로 점수 reroll (KILLS)
- 제출 1 결과를 보기 전에 제출 2 실행
- 동메달 경계값을 09-10 snapshot 으로 고정 — 제출 전 최신 leaderboard 재수집

## 5. 우선순위 재배치

| 순위 | 작업 | 근거 |
|---|---|---|
| **1** | gate 범위 결정 (Codex 독립 검토 → 사람) | 결정 전까지 모든 신규 제출이 봉쇄된다 |
| **2** | `yhay81-exact` 재제출 + 최신 leaderboard·동메달 경계 재수집 | 유일한 큰 미지수를 산다 |
| **3** | P1c 축소판 (마진 분포 현재 window) | 제출 1 판독의 기준선 |
| **4** | `EXP-011` `shed_discarded` 진단 | 폐기 아님. 440점 격차에 대해 600 coin/경기는 3순위 |
| **보류** | EXP-007 무승부 9판 전용 card | §6 |

## 6. EXP-007 무승부 9판을 별도 card 로 만들지 않는 이유

- 무승부는 BT 에서 0.5다. 9판을 전부 승리로 바꾸면 50판 point score 는 0.51 → 0.60.
  의미는 있지만 **EXP-007 은 1,636 으로 동메달에서 가장 먼 슬롯**이다. 가장 약한 슬롯을 고쳐도 2,303 에 닿지 않는다.
- 고치는 기제는 clone-preempt = `HYP-0006` 이고, 그 hosted causal 효과가 바로 §3 의 미지수다.
  **효과를 모르는 처치를 가장 약한 슬롯에 적용하려고 슬롯 하나를 쓰는 것**이 된다.
- 대신 이 관측은 **증거로 보존**한다(F-T17). 실제 쓰임은 두 가지다:
  ① 공개 복제본을 그대로 올리면 자기 클론에게 0.5 로 상한이 걸린다 → §4 제출 1 판독 시 **무승부 비율을 함께 본다.**
  ② yhay81-exact 재제출 결과에 무승부가 많으면, 그때 clone 대칭 파괴는 **가설이 아니라 측정된 필요**가 된다.
- 즉 **지금 card 로 만들지 않고, 제출 1 의 판독 항목으로 넣는다.** 결과가 요구하면 그때 card 를 만든다.

## 7. 솔직한 전망

12일에 440점은 쉽지 않다. 우리가 가진 어떤 artifact 도 2,303 을 관측한 적이 없고,
공개 자료 triage 51/18건에서도 성능 artifact 는 0건이었다.
**동메달은 목표로 삼을 수 있지만 보장할 수 없다.**
그래도 이 계획이 최선인 이유는, 남은 시간을 *확실히 실패하는 경로*(현상 유지)에 쓰지 않고
**하나 남은 큰 미지수를 먼저 사기 때문**이다. 그 답이 나와야 남은 9~10일을 어디에 쓸지 정해진다.


---

## `proposals/claude/20260916-CODEX-REVIEW-BRIEF-gate-scope.md`

# Codex 독립 검토 브리프 — gate 범위 제안

발행 2026-09-16 22:00 KST · Claude(opus-5) · 사람이 Codex를 독립 검토자로 지정(2026-09-16)

아래 블록을 그대로 Codex에 붙여넣으면 된다.

```text
당신은 이 제안의 독립 검토자다. 제안자는 Claude이며, AGENTS.md §4에 따라
제안자는 자기 제안을 단독 승인할 수 없다. 당신의 역할은 승인이 아니라 검토 의견 작성이다.
최종 채택/기각은 사람이 한다.

읽을 파일 (순서대로):
1. AGENTS.md  — 특히 §7.1, §7.1b, §7.4, §8, §9
2. coordination/proposals/claude/WORK_ORDER_20260916_GATE_SCOPE_DECISION.md
   sha256 ee97a53a63640c87bfa55d627b9fbdb184acdac5a8bab9d3e8e3fd02860ff40a
3. coordination/proposals/claude/20260916-BRONZE-TARGET-PLAN.md
   sha256 1ac31cf31d5d15bce6e9272c134bd32d7bbba6af11c9a0986bc12ab423c5b79a
4. evidence/FACTS.md  — F-T12, F-T16, F-T17
5. experiments/results/p1_release_preflight/aggregate.json
6. releases/public-thomas-replay-router-v2-exact/preflight-selfplay.json
7. releases/public-yhay81-shop-router-0909-exact/preflight_selfplay.json
8. coordination/reports/codex/20260914-2043-GATE-SPLIT.md

검토할 질문은 정확히 5개다. 각각에 대해 PASS / FAIL / N/A 와 근거(file:line 또는 수치)를 달라.

Q1. 사실 검증. 제안 §2의 사실 3개가 실제 파일과 일치하는가?
    ① 현재 활성 2슬롯(EXP-006 56165718, EXP-007 56175620)이 모두 release zero gate를 실패하는가
    ② 무수정 yhay81 exact와 EXP-006의 self-play counter가 seed 7/1000/1001에서 동일한가
       (즉 zero-gate 실패가 우리 layer가 아니라 공개 parent에서 상속된 것인가)
    ③ P1b에서 gated parent record 16/16이 실패해 게이트가 후보를 구분하지 못하는가
    틀린 수치가 하나라도 있으면 그것을 먼저 적어라.

Q2. 제안 §3의 2층 구조가 AGENTS.md §7.4와 계획 §6의 "gate를 낮추지 않는다"를 위반하는가?
    핵심 구분: 임계(0)는 그대로 두고 적용 대상만 [상속 baseline]과 [신규 도입]으로 나눈다.
    [상속 baseline]은 candidate <= parent (같은 cell·seed·좌석)로 판정한다.
    이 구분이 정당한 범위 조정인가, 아니면 실질적인 게이트 완화인가?
    EXP-008 G4가 이미 같은 기준(candidate <= parent, 326셀)을 썼다는 점을 함께 판단하라.

Q3. 안전장치 2개가 충분한가?
    ① baseline freeze: 기준값을 parent artifact SHA와 함께 실행 전에
       experiments/baselines/<artifact-sha>.json 에 커밋, 사후 조정 불가
    ② 사람 승인 (AGENTS §8)
    부족하다면 무엇을 추가해야 하는지 구체적으로 적어라.
    특히 "결과를 본 뒤 baseline을 바꾸는" 우회 경로가 남아 있는지 확인하라.

Q4. 제안 §5의 주장이 성립하는가?
    "사람이 목표를 최소 동메달로 확정했으므로, 이 제안을 기각하면
     release zero gate가 동메달 경로 자체를 봉쇄한다."
    동메달 경계 ≈ 2,303점 (8,481팀, top 10% = rank 848,
    kaggriculture-publicleaderboard-2026-09-10T08:34:17.csv)과
    현재 최고 1,862.6의 계산이 맞는지 확인하라.
    기각이 정당하려면 "zero gate를 통과하면서 2,303에 도달하는 artifact를 12일 안에 만드는 경로"가
    있어야 한다. 그런 경로가 있는지, 있다면 무엇인지 적어라. 없으면 없다고 적어라.

Q5. 이 제안이 채택될 경우 EXP-008의 FAILURE 판정, sell_unfilled의 diagnostic 지위,
    shed_discarded의 gate 지위 중 하나라도 소급 변경되는가?
    변경된다면 어디인지 지적하라. 제안은 셋 다 변경하지 않는다고 주장한다.

출력 형식:
  coordination/reports/codex/YYYYMMDD-HHMM-GATE-SCOPE-REVIEW.md 한 파일.
  맨 위에 AGENTS §10.1의 4줄 요약(무엇을/왜/측정 결과/막힌 점)을 쓰고,
  그 아래 Q1~Q5 각각의 판정과 근거, 마지막에 VERDICT 한 줄:
    ENDORSE          (사람에게 채택 권고)
    ENDORSE_WITH_CONDITIONS  (조건을 명시)
    REJECT           (기각 권고, 대안 경로를 함께 제시)
  그리고 coordination/TASKS.md 에 자기 행을 추가하라.

금지:
- 제안 문서를 수정하지 마라. 그것은 Claude 소유 경로다.
- AGENTS.md, HYPOTHESES.md, BOARD.md 를 수정하지 마라.
- 새 실험을 실행하거나 Kaggle 에 제출하지 마라.
- 채택을 스스로 확정하지 마라. 당신은 검토자이고 결정권자는 사람이다.
- 동의해 주려고 애쓰지 마라. 이 제안은 "게이트를 무르는 것"으로 오용될 수 있는 형태다.
  그 위험이 실재한다고 판단되면 REJECT 를 권고하는 것이 당신의 일이다.
```


---

## `proposals/claude/20260916-EXP011-codex-implementation-handoff.md`

# Codex 구현 handoff — EXP-011 `shed_discarded` 원인 귀속 진단

작성 2026-09-16 11:30 UTC / 20:30 KST · Claude(opus-5)
카드 `experiments/cards/EXP-011-shed-discard-attribution.md` sha256 `daabcd0d1386b95559d3433bd410c8b06a09d37f6a1407a5427e2c8c2164ddf2`
ledger `HYP-0031` / `TEST-0011` — `python3 tools/validate_hypotheses.py --strict` exit 0 (31 entries)

## 1. 무엇을 만드는가

`tools/instrument.py` **한 파일**에 drop-event 귀속 계측을 추가하고,
P1b 의 **같은 13경기**를 새 출력 경로로 다시 돌린다.
**제출 tar 도, agent 코드도, engine 도, gate 기준도 바꾸지 않는다.**

## 2. 왜 하는가

P1b 에서 gated parent 16/16 이 zero gate 를 실패했다. 그 중
`shed_discarded` 482 는 **물건이 실제로 사라진 것**이고 (`sell_unfilled` 같은 요청 초과분이 아니다),
`orders_truncated`·`shed_unsold`·`exceptions` 는 이미 0 이다.
따라서 correctness 수리는 여기서 시작한다.

그런데 **어떤 행동이 그 손실을 만들었는지는 기존 JSON 으로 알 수 없다.**
현재 계측은 하루치 손실 총량만 누적한다(`lost = carried - moved`).
day·unit·item·drop 직전 shed 점유·마지막 action·shed 인접 여부가 없다.
원인을 모른 채 guard 를 넣으면 손실을 숨기게 된다. 그래서 진단이 먼저다.

## 3. 착수 전 확인 (BLOCKED 반환 기준)

아래 중 하나라도 어긋나면 **실행하지 말고 BLOCKED 로 반환**한다(AGENTS §5).

| 항목 | 기대값 |
|---|---|
| parent tar | `coordination/proposals/claude/exp006/submission.tar.gz` sha256 `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` |
| tar member | `main.py` `bba042e0…96b2` · `yh_base.py` `d6d74997…866d` · `actions.json` `17d503f2…95ef` · `LICENSE.txt` `cfc7749b…3d30` |
| engine | `kaggle-environments==1.32.7`, py `bc8a5487…653e`, json `a82c89c1…4867` |
| instrument 시작본 | `tools/instrument.py` sha256 `284dee4cdacfc56aab2125f8a92b41df53e14744cca7a8cafa10b853fb6d0629` |
| gate contract | `tools/gate_contract.py` sha256 `3a3e423b…71353c` — **불변** |
| 상대 tape | Remielle `75ea188e…a5c4` · today `b1bd786a…a637` |
| 13경기 | seed·좌석·상대 전부 P1b manifest `46fd9e5e…4801c` 그대로 |

## 4. 구현 (`tools/instrument.py` 만)

현재 hook (`:450-461`):

```python
def drop(private, capacity):
    cursor["drop"] += 1
    pid = min(max(0, cursor["drop"]), len(counters) - 1)
    carried = sum(sum(int(v or 0) for v in inv.values())
                  for inv in (private.get("inventories") or []))
    shed_before = sum(int(v or 0) for v in private["shed"].values())
    r = orig["drop"](private, capacity)
    moved = sum(int(v or 0) for v in private["shed"].values()) - shed_before
    lost = max(0, carried - moved)
    if lost:
        counters[pid].shed_discarded += lost
    return r
```

요구 사항 6가지.

1. **`carried_before` 를 unit 별·item 별로 스냅샷**한다. 엔진이 `del inv[item]` 하므로
   `orig["drop"]` 호출 후에는 복원할 수 없다.
2. **deposit/discard 를 엔진과 같은 순서로 재현**해서 unit·item 단위로 나눈다.
   엔진 순서는 `for inv in private["inventories"]` (unit index 오름차순) 안에서
   `for item, n in list(inv.items())`, `room = max(0, capacity - current)`, `take = min(n, room)` 이다
   (`kaggriculture.py:843-856`). **추정·비례배분 금지.**
3. **위치와 마지막 op 를 리셋 전에 읽는다.** `_end_of_day` 는 drop **뒤에**
   `farm["farmer"]` 를 리셋하고 `farm["hands"]` 를 비운다(`:872-881`).
   `unit_shed_adjacent_at_drop` 은 엔진 `_is_shed_adjacent`(`:138`) 와 같은 기준을 쓴다.
   `unit_last_op` 은 그 day 마지막 스텝에 **실제로 적용된** op 다(엔진 PASS 치환 이후 값).
   기존 `unit` hook 이 이미 op 를 보므로 거기서 `(pid, step, unit_index) -> op` 를 저장하면 된다.
4. **event 스키마**는 카드 §B-2 의 JSON 그대로. 필드 이름을 바꾸지 않는다.
5. **in-day 소멸 별도 counter 신설** — `shed_discarded_inday_drop`(`:344-355` DROP 경로),
   `shed_discarded_inday_place`(`:393-411` PLACE 경로).
   **관측 전용이며 zero gate 에 넣지 않는다.** `shed_discarded` 의 정의와 값은 바꾸지 않는다.
6. **기존 counter 의 값·이름·gate 판정 로직을 바꾸지 않는다.** 추가만 한다.

출력: `experiments/results/p1_shed_attribution/` (신규).
`experiments/results/p1_release_preflight/` 는 **읽기 전용**이다.

## 5. 실행

manifest 의 argv 형태 그대로, 출력 경로만 신규:

```text
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
python3 tools/instrument.py --a <seat-0> --b <seat-1> --seeds <frozen-seed> --steps 720 \
  --time-agent both --gate-agent <a|b|both> --json experiments/results/p1_shed_attribution/cells/<cell>.json --require-pass
```

- 13개 cell 각각 별도 JSON. FAIL 이 뒤 cell 을 막지 않게 한다(exit code 는 전부 기록).
- exit code 2 는 정상이다 — parent 는 여전히 zero gate 를 실패한다.
- **새 경기·새 seed·새 상대 생성 금지.** 같은 13경기만 다시 돌린다.

## 6. 판정 (카드 §C 와 동일, 전부 숫자)

| gate | 임계 |
|---|---|
| D1-a SHA 일치 | mismatch_count == 0 |
| D1-b 720-step `DONE/DONE` | 위반 episode == 0 |
| D1-c 16 record 의 9개 counter + episode rewards 가 frozen 값과 **정확히** 일치 | mismatch_count == 0 |
| D2-a record 별 `sum(drop_events.discarded_total)` == frozen `shed_discarded` | mismatch_count == 0 |
| D2-b 전체 합 | `== 482` |
| D2-c event 별 `sum(carried_before) - sum(deposited) == discarded_total` | mismatch_count == 0 |
| D3 482 단위의 7개 필드 non-null | null_field_count == 0 |
| D4 8개 class 배타 분류 | unclassified == 0, multi_class == 0 |
| R-1/2/3 runtime | `total_s <= 623`, `wall_seconds <= 960`, `< 1200` — 위반 0 |

**D1-c 가 깨지면 계측이 경기를 바꾼 것이다.** 결과 전체를 INVALID 로 격리하고
원인 주장을 하지 않는다. 임계를 고쳐 통과시키지 않는다.

frozen 기준값은 카드 §C 의 표를 쓴다. 재확인 명령:
`python3 scratch/claude_shed_attribution_20260916.py` (read-only, exit 0)

## 7. 결과 보고에 반드시 포함할 것

1. 16 record × 8 class 표 (단위 수)
2. 층별 점유율 — `S1`(64단위) / `S2`(418단위)
3. 지배 class `C*` 와 그것이 단독 최다인 record 수 (16 중 몇 개)
4. 카드 §D 판정표에 따른 결론 한 줄:
   `REPAIR_AUTHORIZED` / `BLOCKED_STRATEGY_BOUNDARY` / `BLOCKED_AMBIGUOUS_ROOT_CAUSE`
5. `shed_discarded_inday_drop` / `shed_discarded_inday_place` 관측값
   (gate 아님. 0 이 아니면 현재 482 가 **총 손실의 하한**이라는 뜻이므로 명시)
6. 보고 경로 `coordination/reports/codex/YYYYMMDD-HHMM-EXP011-RESULT.md`
7. `tools/update_hypotheses.py` 로 HYP-0031 event 기록 후 `validate_hypotheses.py --strict` exit 0

**`REPAIR_AUTHORIZED` 가 아니면 구현 card 를 만들지 않는다.** 사람에게 이관한다.

## 8. 금지

- 제출 tar / `main.py` / `yh_base.py` / `actions.json` / `SHOP_PLANS` / clone-preempt threshold 수정
- market ordering, `MAX_ORDERS=10`, seed·좌석·상대, engine, metric schema 3, zero gate 기준 변경
- 결과를 본 뒤 seed 추가·threshold 조정·불리한 cell 제외
- 손실을 PASS 로 치환하는 guard 를 이 카드에서 넣는 것 (이 카드에는 candidate 자체가 없다)
- Kaggle 제출, 현재 활성 `EXP-006`/`EXP-007` 변경

## 9. ID 충돌 주의 (Coordinator 확인 요청)

`tools/update_hypotheses.py` 는 새 가설에 `max+1` 을 배정한다. 이번에 실제 배정된 값은 **`HYP-0031`** 이다.
`coordination/proposals/codex/20260914-community-trends-plan-update.md` 는 `HYP-0031..0033` 을
초안 예약명으로 쓰고 있지만, 같은 문서 §2.2 가 **"적용 시 이미 사용 중이면 updater 가 다음 free ID 를
할당하고 card pointer 도 함께 바꾼다"** 고 규정한다.
→ 그 문서의 `HYP-0031`(standing-MELON) / `HYP-0032`(opening animal) / `HYP-0033`(FERTILIZER) 은
**등록 시점에 `HYP-0032` / `HYP-0033` / `HYP-0034` 로 이동**한다. `EXP-009`/`EXP-010`/`TEST-0009`/`TEST-0010`
이름은 그대로 예약 상태로 두었고, 이번 카드는 `EXP-011` / `TEST-0011` 을 썼다.


---

## `proposals/claude/20260916-p1b-manifest-contract-resolution.md`

# Codex에게 — P1b manifest draft의 계약으로 확정 가능한 3개 항목

**2026-09-16 · claude (cowork), manifest 검토 역할.** 대상: `experiments/results/p1_release_preflight/manifest.json` draft sha256 `97ee065713465957e119c706b00f5b01c459d2c47dd0900a4bda9d3863af1019` (`report.md` sha256 `f307438f4c971c1aa3cf37660cf337c7b1e8b26585191aa30d0dc9e9d3899dbf`, `resume.json` sha256 `2ae25f2115e7da8f3457ea7f779edb47b9479190b5503b57f6dc140cc8bd51a8`). 이 파일들은 Codex 소유라 직접 고치지 않고 제안만 한다. **manifest·plan 실행은 요청하지 않는다 — 문구·숫자 정정 제안뿐이다.**

## 1. `review_reconciliation.reproduction_target` — 기존 증거로 확정 가능

- `exp008_control_failure_reproduction` 그룹의 `scope_status: DISPUTED_LABEL_AND_PURPOSE`는 draft 자체가 이미 옳게 지적했다: EXP-008 control은 **outcome G2 PASS**(2/0/0)였으므로 "실패 재현"이 아니다.
- 그런데 같은 cell의 `historical_schema_2_release_counter_context_not_acceptance`에 적힌 `noop_actions=44`, `shed_discarded=7`은 **schema-3에서도 그대로 gating되는 counter**다(schema 2→3 변경은 `sell_unfilled` diagnostic 강등과 `shed_unsold` 추가뿐, `noop_actions`·`shed_discarded`는 변경 없음 — `coordination/reports/codex/20260914-2043-GATE-SPLIT.md` "Gate contract"). 즉 이 cell은 **outcome은 이겼지만 release absolute-zero gate(`plan §6`, AGENTS §7.5 Schema 항목)는 이미 위반한 이력이 있는 opponent다.**
- 결론: target(Remielle, 실제 outcome-loss stress)과 control(today, 이미 확인된 counter-violation stress)은 **다른 것을 검증하므로 둘 다 유지하는 것이 계약과 맞다.** draft의 `current_draft: "retain both but label them separately"`를 그대로 채택하되, group 이름을 실제 목적에 맞게 바꾸는 것을 제안한다:
  - `hosted_loss_stress` (Remielle) → 이름 유지, 목적 = "outcome-loss stress, EXP-008 target"
  - `exp008_control_failure_reproduction` → **`exp008_control_counter_violation_stress`로 개명** 제안, purpose 문구를 "control passed outcome G2 but its schema-2 measurement already showed non-zero noop_actions/shed_discarded; this cell re-measures those two counters under schema-3 on the actual parent A artifact"로 교체
- `status`를 `UNRESOLVED` → **`RESOLVED_BY_CONTRACT`**로, `scope_status`를 `DISPUTED_LABEL_AND_PURPOSE` → **`RESOLVED_RETAIN_BOTH_DISTINCT_PURPOSE`**로 바꾸는 것을 제안한다. episode 수(4 = target 2 + control 2)는 변경 없음.

## 2. `review_reconciliation.seeds` — 승인

- `7, 1000, 1001` self-play/smoke seed는 기존 release manifest 2건(`releases/public-thomas-…`, `releases/public-yhay81-…`)의 전례이고, 결과를 보기 전에 이미 draft에 고정돼 있다(AGENTS §5 사전등록 요건 충족). `hosted_loss_stress`/`exp008_control_…` seed는 각각 EXP-008 카드의 target/control seed(`1125321547`/`1989066512`)와 정확히 일치한다.
- **Claude manifest reviewer로서 이 seed 목록을 승인한다.** `review_reconciliation.seeds.status`를 `PROPOSED_NOT_APPROVED` → **`APPROVED_BY_CLAUDE_REVIEW`**로 바꾸는 것을 제안한다. (별도로, `독립 검증자`의 승인은 여전히 필요 — 이건 §3 항목이 아니라 §5 항목이다.)

## 3. `review_reconciliation.runtime_cutoff` — 계약으로 분모 확정 가능

- AGENTS §6 은 두 숫자를 명시적으로 정의한다: 공유 에피소드 예산 **1,200초**(양 에이전트 합), 그리고 AGENTS §6이 스스로 유도한 **"에이전트당 nominal 상한" 719×1s+60s = 779초**. plan §8의 "에피소드 예산(§6)의 70~80%"에서 **"에이전트당" 문맥(우리 parent A 하나의 clean/dirty 판정)에는 779초가 맞는 분모다** — 1,200초는 두 에이전트 합산 공유 예산이라 단일 아티팩트의 release 판정 기준으로 쓸 수 없다.
- 계산: 779 × 0.70 = 545.3초, 779 × 0.80 = 623.2초. **PASS 임계로 상한 하나만 필요하므로 623초(80%)를 권장**하고, 545~623초 구간은 "여유 있음"으로만 참고한다.
- 제안 문구: `acceptance.runtime.status`를 `UNRESOLVED_NO_PASS_THRESHOLD` → **`RESOLVED`**로, 아래 필드 추가 제안:
  ```json
  "denominator": "per-agent nominal cap (AGENTS §6: 719*1+60=779s), not the 1200s shared episode budget",
  "total_s_by_parent_player_lte": 623,
  "wall_seconds_hard_ceiling_lt": 1200
  ```
- `previous_draft_values_retracted_from_acceptance`의 나머지 값(`first_call_ms_lte`, `p99_ms_lte`, `max_call_ms_lt`, `combined_parent_agent_cpu_seconds_lte`)은 AGENTS/plan 어디에도 원래 숫자가 없어 **계약으로 확정 불가 — 이번 제안에 포함하지 않는다.** 이 항목들은 계속 measure-only로 남기고, 필요하면 owner가 별도로 숫자를 정해야 한다.

## 이번 제안이 다루지 않는 것 (owner 결정 필요, Claude review에서 BLOCKED로 별도 기록)

- opponent population 크기(13 episodes vs EXP-008식 326-cell vs 다른 고정 집합) — 시간·자원 배분 문제라 계약만으로 못 정한다.
- 독립 검증자 지정 — 사람이 정할 이름의 문제다.
- 위 두 항목과 나머지 세부는 `coordination/reports/claude/20260916-1745-P1B-CURRENT-MANIFEST-REVIEW.md`에 있다.

## plan 문서 자체의 wording 제안 (plan은 이번 라운드 Codex 위임이라 직접 고치지 않음)

`plan/kaggriculture_deadline_plan_20260915.md` §5.2 1단계의 "기존 EXP-008 control 실패 재현 셀"을 "기존 EXP-008 target 실패(outcome) 재현 셀과 control counter-violation 재현 셀"로 정정할 것을 제안한다. 같은 문서 §8의 "에피소드 예산(§6)의 70~80%"는 자기 문서의 §6(다른 주제)과 혼동되므로 "AGENTS.md §6"으로 명시할 것을 제안한다.


---

## `proposals/claude/20260916-p1b-status-sync-patches.md`

# 제안 — P1b 독립 결과 검증 상태 동기화 (exact patch)

작성 2026-09-16 11:25 UTC / 20:25 KST · Claude(opus-5) · task `P1B-CORRECTNESS-PREREG-20260916`

## 1. 무엇을 바꾸자는 것인가

P1b actual parent A preflight 결과의 독립 검증이 끝났다. 그런데 산출물 4곳에
`independent result verification PENDING` 계열 문구가 아직 남아 있다.
그 문구들을 **독립 검증 보고서와 일치하도록** `VERIFIED_LOCAL_FAILURE` 로 바꿔야 한다.

## 2. 왜 하는가

BOARD 가 이틀 멈춘 채 "제출 0회" 라고 적혀 있던 사고(AGENTS §11)의 재발을 막기 위해서다.
**판정은 바뀌지 않는다.** PENDING → VERIFIED 는 "검증이 끝났다" 는 뜻이고, FAILURE 는 그대로다.
zero gate 를 낮추거나 `shed_discarded` 를 diagnostic 으로 강등하는 변경은 이 제안에 없다.

## 3. 근거 (검증 정본)

| 항목 | 값 |
|---|---|
| 독립 검증 보고 | `coordination/reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md` |
| 보고 sha256 | `fc02423f9a4fbf66f23be56c3f454d051fa0c1e927100542be40c5ff8cb47ad5` |
| verdict | `VERIFIED_LOCAL_FAILURE` |
| 검증 대상 manifest sha256 | `46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c` |
| 검증자 | Antigravity (manifest 작성자 Codex 및 실행 integrator 와 다름 — AGENTS §4 충족) |
| 재확인 | 13/13 720-step `DONE/DONE`, gated parent 16, zero gate PASS 0 / FAIL 16, 파일 불일치 0, 계측 오류 0 |

Claude 측 3차 재집계도 동일값을 재현했다 — `python3 scratch/claude_shed_attribution_20260916.py` exit 0
(16 record, `shed_discarded` 482, `noop_actions` 3,488, 9개 counter 합·nonzero record 수 전부 일치).

---

## 4. 소유 경로별 patch

### 4.1 `experiments/results/p1_release_preflight/aggregate.json` — **owner Codex**

`result_verification` 블록 전체를 아래로 교체:

```json
  "result_verification": {
    "integrator_cross_check": "PASS",
    "independent_result_verification": "VERIFIED_LOCAL_FAILURE",
    "independent_verifier": "Antigravity",
    "independent_verification_report": "coordination/reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md",
    "independent_verification_report_sha256": "fc02423f9a4fbf66f23be56c3f454d051fa0c1e927100542be40c5ff8cb47ad5",
    "independent_verification_at_utc": "2026-09-16T10:33:00Z",
    "note": "The pre-run Antigravity review approved the manifest and runner. This separate post-run review independently recomputed the 13 newly generated cell JSON files and reproduced every counter sum and nonzero-record count with zero deviation."
  },
```

`overall_verdict` 1줄 교체:

```diff
-  "overall_verdict": "LOCAL_FAILURE_INDEPENDENT_RESULT_VERIFICATION_PENDING",
+  "overall_verdict": "VERIFIED_LOCAL_FAILURE",
```

**변경하지 않는 것:** `parent_records.verdict` = `FAILURE`, `pre_submission_checklist` 6줄,
`hosted_strength_claim` = `N/A`, `submission_authorized` = `false`, 모든 counter 값.

### 4.2 `experiments/results/p1_release_preflight/resume.json` — **owner Codex**

```diff
-  "status": "LOCAL_FAILURE_INDEPENDENT_RESULT_VERIFICATION_PENDING",
+  "status": "VERIFIED_LOCAL_FAILURE",
```

`blockers` 배열 교체:

```json
  "blockers": [
    "Frozen zero gate failed in every gated parent record",
    "The root cause of shed_discarded is not attributed yet; EXP-011 diagnostic must complete before any repair card"
  ],
```

`resume_only_when` 배열 교체:

```json
  "resume_only_when": [
    "SATISFIED 2026-09-16: an independent validator checked commands.json, all 13 cell JSON files, aggregate.json, and report.md without changing the frozen criteria",
    "Run experiments/cards/EXP-011-shed-discard-attribution.md on the same frozen 13 episodes; do not lower gates or alter the completed sample"
  ],
```

**변경하지 않는 것:** `do_not` 5줄 전부, `checklist`, `execution` 수치, `manifest_sha256`.

### 4.3 `experiments/results/p1_release_preflight/report.md` — **owner Codex**

3곳.

```diff
-4. **막힌 점과 다음 행동:** 독립 결과 검증이 남아 있고 zero gate가 실패했으므로 전체 preflight는 PASS가 아니다. 기준을 낮추지 말고 correctness 경로를 결정해야 한다.
+4. **막힌 점과 다음 행동:** 독립 결과 검증은 2026-09-16 완료됐고(VERIFIED_LOCAL_FAILURE), zero gate가 실패했으므로 전체 preflight는 PASS가 아니다. 기준을 낮추지 말고 correctness 경로로 간다 — 첫 단계는 EXP-011 `shed_discarded` 원인 귀속 진단이다.
```

```diff
-VERDICT | **LOCAL FAILURE — 13/13 VALIDLY COMPLETED, INDEPENDENT RESULT VERIFICATION PENDING** | artifact `1c478c24…9721`, manifest `46fd9e5e…4801c` | Identity PASS · Schema FAIL · Runtime PASS · Isolation PASS · License PASS · zero gate FAIL | NEXT ACTION: independent result verification → correctness path decision
+VERDICT | **VERIFIED_LOCAL_FAILURE — 13/13 VALIDLY COMPLETED, INDEPENDENT RESULT VERIFICATION DONE** | artifact `1c478c24…9721`, manifest `46fd9e5e…4801c` | Identity PASS · Schema FAIL · Runtime PASS · Isolation PASS · License PASS · zero gate FAIL | NEXT ACTION: EXP-011 shed_discarded 원인 귀속 진단 (계측 전용, artifact 무변경)
```

`## 판정 경계` 마지막 줄:

```diff
-- **독립 결과 검증:** PENDING. Antigravity의 기존 보고서는 manifest/runner 사전 검토이며 이번 새 JSON 결과 검증은 아니다. 따라서 전체 preflight PASS를 선언하지 않는다.
+- **독립 결과 검증:** **DONE — VERIFIED_LOCAL_FAILURE** (Antigravity, 2026-09-16, 보고 `coordination/reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md` sha256 `fc02423f…7ad5`). 사전 manifest/runner 검토와 별개로 새 13개 cell JSON을 독립 재집계했고 counter 합·nonzero record 수가 전부 일치했다. 검증이 끝났다는 뜻이며 **전체 preflight PASS 가 아니다** — zero gate 는 여전히 16/16 FAIL 이다.
```

### 4.4 `coordination/TASKS.md` — **해당 행 owner Codex**

`P1-RELEASE-PREFLIGHT-MANIFEST-20260916` 행 상태 칸:

```diff
-| ... | DONE — LOCAL FAILURE; 13/13 valid completion, zero gate 0/16 PASS, runtime PASS, 독립 결과 검증 PENDING |
+| ... | DONE — VERIFIED_LOCAL_FAILURE; 13/13 valid completion, zero gate 0/16 PASS, runtime PASS, 독립 결과 검증 DONE (antigravity 20260916-1933) |
```

`## P1B-13EP-SCOPE-APPROVED-20260916 — Codex` 의 상태 줄:

```diff
-- 상태: DONE — Claude·Antigravity 동일 manifest/time 기준 승인 뒤 13/13경기 실행 완료. LOCAL FAILURE, 독립 결과 검증 PENDING.
+- 상태: DONE — Claude·Antigravity 동일 manifest/time 기준 승인 뒤 13/13경기 실행 완료. VERIFIED_LOCAL_FAILURE, 독립 결과 검증 DONE (antigravity 20260916-1933).
```

### 4.5 `coordination/BOARD.md` — **owner Coordinator 전용**

머리말 4번:

```diff
-4. 다음: 공개 source triage·actual parent tar release preflight·최신 episode/postmortem을 P1에서 먼저 끝낸다. **승인된 다음 실험 카드는 아직 없다.**
+4. 다음: P1b는 VERIFIED_LOCAL_FAILURE로 종결됐다. 새 전략 카드는 계속 HOLD이며, 승인된 다음 카드는 correctness 진단 **EXP-011**(계측 전용, artifact 무변경) 하나뿐이다. P1a triage·P1c postmortem은 병행한다.
```

상태 표에 한 행 추가(또는 `최신 완료 실험` 행 아래):

```markdown
| P1b release preflight | **VERIFIED_LOCAL_FAILURE** — 13/13 valid, gated parent 16/16 zero gate FAIL | report.md · aggregate.json · antigravity 20260916-1933 |
```

P1b 행 종료 조건:

```diff
-| **P1b** | actual parent A tar의 schema-3 release preflight | Codex / Claude manifest 확인 / 독립 검증자 | 계획 §5.2의 실행 전 고정 manifest와 제출 전 5줄·zero gate 판정. **미실행 N/A**, FAIL/N/A면 새 전략 HOLD 후 correctness 경로 결정 |
+| **P1b** | actual parent A tar의 schema-3 release preflight | Codex / Claude manifest 확인 / Antigravity 독립 검증 | **종료 2026-09-16 — VERIFIED_LOCAL_FAILURE.** 13/13 valid, Identity/Runtime/Isolation/License PASS, Schema FAIL, zero gate 0/16 PASS. 계획 §5.2-4에 따라 새 전략 카드 HOLD, correctness 경로 진입 |
```

P2 행:

```diff
-| **P2** | 관측된 failure에 대한 새 one-factor card | Claude | P1b PASS·관련 claim 인수·원인 근거가 선행. HYP/TEST-ID, exact parent, target/control, seed·숫자 gate 확정. 없으면 BLOCKED |
+| **P2** | correctness 경로 — `shed_discarded` 원인 귀속 진단 | Claude 설계 / Codex 실행 / 제3 검증자 | 사전등록 완료: `experiments/cards/EXP-011-shed-discard-attribution.md` (HYP-0031 / TEST-0011). D1~D4·R 전부 0 판정이고 §D 지배 class 임계를 넘어야 repair card EXP-012 승인. 임계 미달이면 repair 금지 |
+| **P2b** | 새 전략 one-factor card | Claude | **HOLD** — P1b FAIL이므로 correctness 완료 전 착수하지 않는다. 날짜만으로 전략 단계로 넘어가지 않는다(계획 §5.2-4) |
```

`## 실험·가설의 현재 결론` 에 항목 추가:

```markdown
- **HYP-0031 / TEST-0011: PLANNED.** P1b의 `shed_discarded` 482는 engine `_drop_inventories_to_shed` 경로의 실제 자원 손실이다. group별 self_play 40 / starter 10 / target stress 418 / control 14, 16/16 record nonzero. **원인은 아직 귀속되지 않았다** — EXP-011 진단 전에는 repair card를 승인하지 않는다.
- **HYP-0006 갱신:** P1b 독립 결과 검증 완료(VERIFIED_LOCAL_FAILURE). preflight PASS 아님. 현재 EXP-006/EXP-007 제출 tar는 수정하지 않는다.
```

---

## 5. 하지 말아야 할 것 (제안에 포함되지 않음)

- `parent_records.verdict`·checklist·counter 값 변경 금지
- zero gate 8개 counter 기준 완화 금지
- `shed_discarded` 를 diagnostic 으로 재분류 금지
- `sell_unfilled` 를 gate 로 승격 금지
- 13경기 seed·좌석·상대 변경 금지
- 현재 활성 제출 `EXP-006` / `EXP-007` tar 변경 또는 재제출 금지

## 6. 이미 적용된 것 (Claude 소유 경로 — 제안 아님)

- `HYPOTHESES.md` HYP-0006 — `tools/update_hypotheses.py` 로 갱신 완료.
  event `coordination/hypotheses/claude/EVT-2026-09-16T111036.743309+0000-942aa378.json`
- `HYPOTHESES.md` HYP-0031 신규 등록 — event `EVT-2026-09-16T111126.701382+0000-099e427d.json`
- `experiments/cards/EXP-011-shed-discard-attribution.md` 신규 사전등록
- `coordination/TASKS.md` 의 **Claude 자기 행**만 추가


---

## `proposals/claude/20260918-DONOR-TAPE-FASTLANE-PLAN.md`

# 상위 donor tape exact 재생 계획 + fast lane BOARD 변경안

작성: Claude (사람 요청으로 Coordinator 역할), 2026-09-18 ≈13:10 UTC. **상태: PROPOSAL — 적용하지 않음.**
BOARD·AGENTS·KILLS 무변경. 다운로드·candidate 구현·경기·제출 없음. 이 문서는 Coordinator 작성본이며 **독립 검토 아님**.
선행 문서: [K3 최종 결정안](20260918-K3-DONOR-FINAL-DECISION.md) — 이 계획은 그 K3 정정이 승인돼야 성립한다(§3).

---

## 한 화면 요약

1. **무엇을 하는가:** 현재 상위권 팀 중 **여러 경기에서 행동이 완전히 같은 팀(= 고정 tape 로 추정)** 을 골라, 그 기록을 그대로 재생하는 bot 을 만들어 hosted 로 시험한다. 그 위에 개선을 **한 번에 하나씩** 얹는다 — ① 마지막 턴 정리 → ② 1턴 선행 판매.
2. **왜 하는가:** 목표가 순위 상승(동메달 942위 · 2395.3)으로 바뀌었다. 자체 계열은 1487–1638로 757점 부족하고 12일 안에 메울 근거가 없다. 상위 tape 재생은 상위권이 실제로 쓴 경로다(rayk c14 `[COMMUNITY]`, HYP-0019 88% 회수 주장 `[COMMUNITY]`, HYP-0029 field 다수가 tape `[COMMUNITY]`).
3. **측정 결과:** N/A — 아직 donor 수집·구현·경기 없음. 기준선: yhay81-exact 재제출 44분 뒤 1538.9 (수렴 전).
4. **막힌 것 / 다음:** 사람 승인 1건(§5 문장)이 필요하다 — K3 정정 + fast lane + 다운로드 허용 범위. 승인 후 Codex 가 사람 Mac 에서 metadata 수집부터 시작한다(이 VM·cloud 는 kaggle.com 403).

```
VERDICT  PROPOSE: donor-tape fast lane (exact 재생 → 순차 개선), P2 HOLD 는 비재생 전략에 유지
사실1    동메달 경계 942위 2395.3 / Sian 2,201위 (09-18 12:10 UTC, HOSTED_LEDGER)
사실2    yhay81-exact 는 로컬 silent-failure gate FAIL 상태로 hosted 2188.4 — 현재 gate 는 hosted 강도의 검증된 예측자가 아니다 [INFERENCE]
path     coordination/proposals/claude/20260918-DONOR-TAPE-FASTLANE-PLAN.md
NEXT     사람: §5 승인 문장 → Codex: 단계 A(metadata) → Claude: donor 선정 카드
```

---

## 1. 질문에 대한 답

### 1-1. 개선 둘을 차례로 하면 되는가 — 예. 순서는 ① 마지막 턴 정리 → ② 1턴 선행 판매

- **한 번에 하나.** 둘을 같이 넣으면 어느 쪽이 효과를 냈는지(또는 깎았는지) 모른다. EXP-006(yhay81 + clone-preempt)이 exact 보다 약 170점 낮았는데(09-12 무렵, 같은 window 아님) 원인을 아직 판정 못 한 것이 그 예다.
- **정리가 먼저인 이유:** 마지막 몇 턴만 바꾸므로 tape 의 midgame 시장·현금 흐름을 건드리지 않는다(HYP-0027 붕괴 기제를 피함). rayk c14 이 exact tape + 마지막 8턴 정리로 이전 버전 상대 27-3 `[COMMUNITY]`.
- **선행 판매가 두 번째인 이유:** 기대 이득은 더 크지만(상위권 오프닝이 같아 mirror 경기가 많고, 1턴 선행이 정답이라는 K2), 판매 시점을 옮기면 현금이 바뀌어 이후 tape 가 어긋날 수 있다. EXP-006 이 비슷한 종류였다. 우리가 인기 tape 를 복사할수록 mirror 경기가 늘어 이 개선의 가치가 커진다 `[INFERENCE]`.
- 각 개선은 **로컬 선별 → hosted 확인** 순서다(§4 단계 F).

### 1-2. "몇 경기 일치"를 기준으로 할까 — **같은 submission 의 최신 6경기 중 6경기 완전 일치**

| 조건 | 값 | 이유 |
|---|---|---|
| 일치 범위 | farmer + hands + market 전체, 719 행동 전부 | 일부만 같으면 나머지가 상태에 반응하는 것이다 |
| 경기 수 | **6/6** | rayk·VN-Orion 사례가 5경기. 하나 더 두어 우연 일치를 줄인다. 10 이상은 상위 팀이 submission 을 자주 바꿔 경기 수가 모자랄 수 있다 |
| 다양성 | 그 6경기에 **서로 다른 상대 ≥4명, 좌석 0·1 모두 포함** | 같은 상대·같은 좌석만 보면 반응할 일이 없었을 뿐일 수 있다 |
| 같은 agent | 6경기가 **같은 submission ID** | 팀이 여러 bot 을 돌리면 섞인다 |
| 2순위 (1순위 donor 가 없을 때만) | farmer+hands 6/6 일치, market 은 주문 있는 index 의 **≥90%** 일치 | 부분 반응형. 재생 시 어긋날 위험을 manifest 에 표시 |

**한계:** 6경기 일치는 "그 6경기에서 반응할 일이 없었다"까지만 증명한다. 상태에 반응하지 않는 policy 라는 증명은 아니다. 그래서 이 기준은 **후보 선정용**이고, 강도 판정은 hosted 가 한다.

## 2. 현재 사실 (전부 이번 세션 확인)

| 항목 | 값 | 근거 |
|---|---|---|
| 팀 수 / 메달 경계 | 9,423 / GOLD 28위 2924.8 · SILVER 471위 2648.1 · **BRONZE 942위 2395.3** | HOSTED_LEDGER 09-18 절 (leaderboard API `medal` 필드) |
| 활성 슬롯 | yhay81-exact 재제출(ID N/A, 1538.9 @44분) · EXP-007 `56175620` 1489.0 | HOSTED_LEDGER 09-18 13:00 절 |
| 최종 평가 | 마감 후 약 2주 경기로 Bradley-Terry. 최신 2개 사용, 팀 표시는 최고 bot | `docs/official/evaluation.md:15-16`, `:3` |
| 제출 한도 | 하루 5, 활성 2 (FIFO: 새 제출이 **먼저 올린 것**을 은퇴) | 같은 파일 `:1`, 09-18 관측 |
| donor 공식 공급원 | Kaggle 공식 계정이 매일 평균 레이팅 상위 에피소드를 dataset 으로 배포, "helpful for … IL/BC" | `docs/discussion/731215_Daily_Top_Episodes_Dataset.md` (`https://www.kaggle.com/datasets/kaggle/kaggriculture-episodes-index`). 하루 657–928 경기, replay 1개 평균 약 31 MiB(09-11 댓글) |
| 기존 도구 | `tools/top10_donor_inventory.py`(상위팀 submission·episode metadata), `tools/reproduce_replay.py`(원경기 exact 재현), `tools/analyze_donor_routes.py`, `tools/build_thomas_reference.py`(결정론적 빌드) | 로컬 파일 |
| 네트워크 | 이 Cowork VM·cloud 에서 kaggle.com 403. 사람 Mac 터미널은 제출 성공 | 이번 세션 |

## 3. Fast lane — 무엇을 바꾸는가

### 3-1. 대상 (이 밖은 기존 규칙 그대로)

**exact 재생 artifact**: donor 1명의 1개 submission 이 6/6 일치로 보인 행동 기록을 turn 순서대로 반환하는 bot. 허용하는 코드는 **합법성 adapter** 뿐이다 — hands 길이를 현재 일손 수에 맞춤(초과분 자르기·부족분 PASS), market 10개 초과 자르기, 예외 시 PASS 반환. adapter 가 개입할 때마다 **전용 counter**를 올린다(§3 무음 실패 규율).
**개선 변형**: 위 artifact + §1-1 개선 1개. 한 번에 1개만.

### 3-2. 게이트 — 기존 §7(4봇 페어드 CI) 대신

| 줄 | 판정 | 방법 |
|---|---|---|
| Identity | tar SHA · source replay SHA · action SHA · manifest 기록 | 결정론적 빌드 2회 같은 SHA |
| Schema | root `main.py`, `agent(obs)`, hands 정렬, 절대 raise 안 함 | 로컬 **20경기**(starter 10 seed × 2좌석) + self-play 2경기: 예외 0, ERROR 0, 720 steps |
| Runtime | 에피소드 예산 70–80% 이내, p99 턴 지연 기록 | 같은 20경기 |
| Isolation | 빈 폴더에서 tar 풀고 import | 기존 clean-room 명령 |
| License | donor 출처 = Kaggle 공식 dataset / 공개 replay (Rules §11). `environment/LICENSES.md` 기록(Cowork owner) | 제출 전 |
| Ledger | submission ID ↔ SHA ↔ 에피소드 | 제출 후 |

- **silent-failure counter 는 기록하되 gate 로 쓰지 않는다.** 근거: 이 counter 전부 0 조건이 hosted 강도를 예측한다는 검증이 없고, yhay81-exact 는 FAIL 상태로 2188.4 였다 `[INFERENCE]`. counter 값은 개선 후보를 고르는 진단으로 쓴다.
- **로컬 성능 수치로 제출을 막거나 허락하지 않는다.** 강도는 hosted 가 판정한다. 단 개선 변형은 §4 단계 F 의 로컬 선별을 먼저 통과해야 한다.

### 3-3. AGENTS 와 충돌하는 조항 — 사람이 결정할 범위

| 조항 | 충돌 | 제안 |
|---|---|---|
| §7 "하나라도 실패하면 제출 금지" / §7.1 4봇 페어드 점수 | fast lane 은 4봇 gate 를 쓰지 않는다 | **§3-1 대상에 한해, 2026-09-29 까지** 예외. 비재생 전략은 기존 gate |
| BOARD P2 "parent P1b PASS 선행" | 재생 artifact 는 새 parent 라 P1b FAIL 과 무관하게 진행 | 같은 범위 예외. P2 HOLD 는 비재생 전략에 유지 |
| KILLS K3 (현행 넓은 문구) | 같은 경기 전체 재생이 K3 에 걸린다 | **K3 최종 결정안 §A-3 정정 승인이 선행조건.** 그 문서도 "범위 밖 ≠ 허용"이라 했으므로, 허용 근거는 K3 가 아니라 이번 fast lane 승인이다 |
| §7.4 "활성 슬롯 2개는 서로 다른 두 전략" | 단계 E–G 동안 두 슬롯을 같은 계열 A/B 에 쓴다 | 09-26 까지 측정 기간 예외. 09-27 이후 최종 조합에는 §7.4 적용 |
| §8 제출은 사람 승인 | 변경 없음 | 사람이 Mac 에서 제출 명령을 실행하는 것이 승인 시점이다(에이전트 환경은 어차피 kaggle.com 불가) |

**Rules 위험 (알고 고른다):** Rules 3.14 는 "Submission is your own original work"를 보증하게 한다. 남의 행동 기록을 그대로 재생하는 것은 공개 notebook(thomas router 등)과 공식 dataset 안내문("IL/BC")에서 흔히 쓰이지만, 상금권 심사에서는 회색지대다. 메달만 목표라면 위험은 낮다고 보지만 **판정 권한은 Kaggle 에 있다** `[INFERENCE]`.

## 4. 실행 계획

| 단계 | 담당 | 할 일 | 종료 조건 | 날짜 (KST) |
|---|---|---|---|---|
| **A. metadata** | Codex (사람 Mac) | leaderboard 1–100위의 현재 최고 submission 과 최신 완료 경기 목록(ID·상대·좌석·날짜)만 수집. replay 다운로드 없음. `top10_donor_inventory.py` 를 범위만 넓혀 새 출력 폴더에 동결 | 목록 JSON + SHA. **결과를 보고 선정 규칙을 바꾸지 않는다** | 09-19 |
| **B. 1차 선별** | Codex | 1–60위 팀마다 같은 submission 최신 **2경기** replay 다운로드(≤120개, 약 3.7 GB) → action 배열·SHA 추출 → 2경기 완전 일치 팀만 남김 | 추출 JSON. 원본 replay 는 추출 후 삭제 가능(사람 승인) | 09-19~20 |
| **C. 확정** | Codex / Claude | 남은 팀(최대 15) 4경기 추가(≤60개) → **§1-2 기준 6/6** 판정. Claude 가 donor 카드에 순위(LB 점수 순)와 탈락 사유 기록 | 1순위 donor 1–3명 | 09-20 |
| **D. 빌드·gate** | Codex / Antigravity | exact 재생 artifact 빌드, §3-2 gate. Antigravity 가 index 정렬(obs.step=t → steps[t+1])·좌석·adapter counter 독립 확인 | gate 6줄 중 제출 전 5줄 PASS | 09-20~21 |
| **E. hosted 1차** | 사람 제출 | 1순위 donor exact 제출 → yhay81-exact 재제출이 은퇴하지 않도록 **EXP-007 이 먼저 은퇴하는지 확인**(FIFO: 현재 가장 오래된 활성 = EXP-007) | 24시간 뒤 표시 점수와 경기 수 기록 | 09-21 |
| **F. 개선 ①** | Claude 카드 / Codex | 마지막 턴 정리 변형. **로컬 선별**: 상대 = 단계 C 에서 모은 **다른 상위 donor tape 들**(고정 기록), 고정 seed 20개 × 양 좌석, exact 대비 W/D/L. 패배 증가 0 이면 hosted 로 | 로컬 결과 + hosted A/B | 09-22~23 |
| **G. 개선 ②** | 같음 | 1턴 선행 판매 변형. F 에서 채택된 쪽 위에 | 같음 | 09-23~25 |
| **H. tape 갱신** | Codex / Claude | 09-25 기준 상위 tape 로 A–C 를 한 번 더(오래된 tape 는 빨리 약해진다 — EXP-007 1487) | 새 1순위 donor | 09-25~26 |
| **I. 최종 조합** | Coordinator / 사람 | 09-27 00:00 새 전략 중단. 최강 1개 + **다른 계열 1개**(다른 donor 또는 공개 반응형 router) | 09-29 18:00 제출 완료 | 09-27~29 |

**hosted A/B 해석 규칙**
- 표시 점수는 bot 나이에 따라 수렴 상태가 다르다. **두 bot 모두 24시간 이상 지난 뒤** 비교한다.
- 라이브 점수 변동 ±25–50 은 잡음이다(KILLS 방법론). **100점 이상 차이만 판단에 쓴다.** 작은 개선(마지막 턴 정리 등)은 hosted 로 감지되지 않을 수 있으므로 단계 F 의 로컬 선별이 1차 신호다.
- FIFO 때문에 "남기고 싶은 bot 이 더 나중에 올린 쪽"이 되도록 제출 순서를 정한다. 먼저 올린 쪽이 이겼다면 같은 tar 를 다시 올린다(점수 재시작; 최종 평가는 마감 후 경기라 비용이 작다 — 단, 같은 bot 재제출 **리롤** 금지 규칙과 구분해 사유를 ledger 에 적는다).
- 각 제출은 `(로컬 선별 점수, hosted 24h 점수)` 쌍으로 기록한다(§7.1 삼중쌍의 축소판). 상관이 깨지면 로컬 선별 방식을 고친다.

**다운로드 비용:** 최대 약 180 replay ≈ 5.6 GB(1개 31 MiB 기준, 사람 Mac 디스크). 단계 H 에서 한 번 더. 공식 dataset 전체(하루 20 GB)는 받지 않는다. index CSV 가 submission ID 를 담고 있으면 단계 A 를 index 로 대체할 수 있다 — 확인 전 N/A.

## 5. 사람이 선택할 승인 문장

> 승인: (1) `20260918-K3-DONOR-FINAL-DECISION.md` §A-3 K3 정정(D-2 α)을 승인한다. (2) `20260918-DONOR-TAPE-FASTLANE-PLAN.md` §3 fast lane 을 §3-1 대상에 한해 2026-09-29 까지 적용하고, §3-3 표의 AGENTS §7·§7.1·§7.4 및 BOARD P2 예외를 그 범위로 승인한다. (3) §4 단계 A–D 를 승인한다(상위 1–60위 replay 최대 180개 다운로드 포함). 각 hosted 제출은 내가 직접 실행하며, §1-2 기준·§3-2 gate 를 바꾸면 자동 진행하지 않고 나에게 돌아온다.

**포함하지 않는 것:** 단계 E 이후 각 제출(사람이 명령 실행 시 개별 결정), 비재생 전략, 4번째 땅·GOOSE 등 KILL 항목, K3 의 market-only graft.

## 6. BOARD 변경안 (Coordinator, 승인 후에만 적용)

**머리 4줄 교체:**

```
1. 무엇을 하는가: 목표를 순위 상승(동메달 942위·2395.3)으로 전환. 상위 donor tape exact 재생 → 개선 1개씩 hosted 시험(fast lane).
2. 왜 하는가: 자체 계열 1487–1638로 757점 부족. P1b gate FAIL 은 hosted 강도의 검증된 예측자가 아니다(yhay81-exact FAIL·2188.4).
3. 측정 결과: [HOSTED] 09-18 Sian 2,201위/9,423. yhay81-exact 재제출 1538.9(44분, 수렴 전). donor 재생 결과 N/A.
4. 다음: 단계 A metadata(Codex, 사람 Mac) → C donor 확정 → D gate → E 제출. 비재생 새 전략은 P2 HOLD 유지.
```

**현재 상태 표 교체 행:**

```
| 활성 슬롯 | yhay81-exact 재제출(ID 기입 대기) / EXP-007 56175620 | 09-18 UI |
| 최신 hosted 점수 | yhay81-exact 1538.9(44분) · EXP-007 1489.0 · 은퇴 EXP-006 1638.3 | 09-18 KST UI |
| Sian 순위 / 메달 경계 | 2,201위 / 동 942위 2395.3 · 은 471위 2648.1 · 금 28위 2924.8 | 09-18 leaderboard API |
| 잠정 incumbent | yhay81-exact (09-12 무렵 EXP-006 대비 +166, 같은 window 아님) | HOSTED_LEDGER |
```

**우선순위 표에 추가 (P2 위):**

```
| **F0** | donor tape fast lane (09-19~29) | Codex 수집·빌드 / Claude 선정·카드 / Antigravity 독립 확인 / 사람 제출 | 단계 A–I (proposals/claude/20260918-DONOR-TAPE-FASTLANE-PLAN.md §4). 대상은 exact 재생과 그 1-change 변형뿐. §7 4봇 gate 대신 §3-2 gate |
```

**P2 행 종료 조건 끝에 추가:** `재생 계열은 F0 로 이관. 비재생 전략만 이 행의 HOLD 적용.`

**제출 운영 절 교체 문단:**

```
최신 2개만 남고 새 제출은 먼저 올린 것을 은퇴시킨다. 남길 bot 이 나중에 올린 쪽이 되도록 순서를 정한다.
최종 순위는 마감 후 약 2주 경기의 Bradley-Terry(evaluation.md) — 마감 전 점수 이력 손실의 비용은 작다.
hosted A/B 는 두 bot 모두 24h 경과 후, 100점 이상 차이만 판단에 쓴다.
```

## 7. 남은 독립 검토

| 대상 | 상태 | 담당 |
|---|---|---|
| 이 계획 전체 | Coordinator 작성, **독립 검토 대기** | 사람 판단 (시간 제약상 별도 검토 없이 승인할지 사람 결정) |
| 단계 D artifact | 미착수 | Antigravity |
| K3 정정 문구 | 독립 검토 대기 | Antigravity (K3 결정안 §E) |


---

## `proposals/claude/20260918-EXP011-verify-only-guard.md`

# Codex 에게 — `run.py --verify-only` 가 identity 실패 시 측정 결과를 덮어쓴다 (제안, 미실행)

소유자: `experiments/results/` 와 `tools/` 는 Codex 단독 writer 이므로 **직접 수정하지 않았다.** 제안만 남긴다.
이번 작업에서 해당 명령을 **실행하지 않았고**, `aggregate.json` 은 sha256
`22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba` / `card_verdict=PASS` /
`root_cause_verdict=REPAIR_AUTHORIZED` 로 온전하다.

## 무엇이 문제인가

`experiments/results/p1_shed_attribution/run.py`:

1. `identity()` 는 `freeze.json['inputs']` 의 모든 경로를 frozen SHA 와 대조한다. 그 inputs 에
   `experiments/cards/EXP-011-shed-discard-attribution.md` 가 **측정 당시 r2 SHA
   `8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e`** 로 들어 있다.
2. `verify()` 는 `check('D1-a', 'freeze.json identities including tar/member/engine', identity(), [])` 로
   그 결과를 gate 에 넣는다.
3. `verify()` 의 마지막이 **`write(ROOT/'aggregate.json', result)`** 다. `--verify-only` 경로도 이 `verify()` 를 그대로 탄다
   (`main()` 의 `if args.verify_only: return verify()`).

owner 가 카드에 정정 이력(§G, r3 이후)을 추가하면 카드 SHA 가 바뀐다. 이는 **정상이고 의도된 것**이다
(측정 당시 r2 는 freeze 와 registry·원장에 보존되고, r3 는 그것을 대체하지 않는다).
그러나 그 상태의 live checkout 에서 `python3 experiments/results/p1_shed_attribution/run.py --verify-only` 를
실행하면 D1-a 가 깨지고 `card_verdict='INVALID'` / `root_cause_verdict='INVALID'` 가 되어
**그 INVALID 가 `aggregate.json` 에 기록된다.** 즉 재현 검증 명령 한 번이 측정 산출물을 파괴한다.

Coordinator 검토서(`coordination/proposals/codex/20260918-EXP011-CLOSURE-PRIORITY.md`
sha256 `b1ed06b777abc4841747a60b4328ad670638878f5bf87fc51e3f0649ca15d137`)의 "provenance 주의" 절은
identity mismatch 가 정상이라는 점까지는 적었지만, **덮어쓰기 부작용**은 다루지 않았다.

## 제안 (셋 중 하나, Codex 판단)

1. **읽기 전용 verify.** `--verify-only` 일 때 `write(ROOT/'aggregate.json', ...)` 를 생략하고 stdout 판정만 낸다.
   비교가 필요하면 `--emit <path>` 로 명시할 때만 쓴다. (가장 작은 변경, 권장)
2. **identity 실패 시 쓰기 중단.** `identity()` 가 비어 있지 않으면 `write` 전에 `SystemExit` 로 종료한다.
   `commands.json` 존재 시 재실행을 거부하는 기존 가드와 같은 성격이다.
3. **freeze inputs 의 card 항목 분리.** 카드를 `inputs` 가 아니라 `provenance` 같은 별도 키로 옮겨
   기록은 남기되 D1-a gate 에서 제외한다. 단 이 방식은 **freeze.json 을 바꾸는 것**이라 측정 당시 고정과
   충돌하므로, 한다면 새 실험부터 적용하고 EXP-011 의 freeze 는 건드리지 않는 편이 안전하다.

어느 쪽이든 **`freeze.json` 을 r3 이후 카드 SHA 로 덮어쓰지 않는다** — 코디네이터 지적대로 그것은 provenance 파괴다.

## 그때까지의 운용 (owner 문서에 반영함)

재현 검증은 freeze commit `0a4b10f` 의 r2 카드를 복원한 **별도 checkout 또는 결과 폴더 사본**에서만 실행한다.
`evidence/FACTS.md` F-T20 과 `experiments/cards/EXP-011-shed-discard-attribution.md` §G 의 재현 명령 주석에
"live checkout 에서 실행 금지" 를 명기했다.

대안 재현(카드 SHA 와 무관, 새 경기 생성 없음, 파일 쓰기 없음):

- `python3 scratch/claude_exp011_owner_20260918/verify_d1c_vs_p1b.py` — P1b 원본과 26/26 record 대조
- `python3 scratch/claude_exp011_owner_20260918/verify_order_invariance.py` — 항등식·순열 불변성
- `python3 scratch/claude_exp011_owner_20260918/sellable_headroom.py` — 매도 여력
- `python3 scratch/claude_exp011_owner_20260918/discard_value_estimates.py` — coin 환산 A/B 비교


---

## `proposals/claude/20260918-F0-STAGE-A-WORK-ORDER-CODEX.md`

# 작업 지시서 — F0 단계 A: 상위 팀 metadata 수집 (Antigravity)

**개정 r2 2026-09-18:** 사람 지시로 수신자를 Codex → **Antigravity**(단순 자료 수집 담당)로 바꿨다. AGENTS §4 소유권에 맞춰 스크립트·출력 경로를 `analysis/` 로 옮겼다. §2-6 에 사람이 승인한 61–100위 자동 보충 규칙을 추가했다. 파일명은 이력 보존을 위해 그대로 둔다.

발행: Claude (Coordinator 역할), 2026-09-18. 수신: **Antigravity**. 실행 위치: **사람 Mac 터미널** (Cowork VM·cloud 는 kaggle.com 403).
근거: [사용자 승인 기록](../../reports/claude/20260918-FASTLANE-AUTHORIZATION.md) (2) fast lane · (3) 단계 A–D, [계획](20260918-DONOR-TAPE-FASTLANE-PLAN.md) §1-2 · §4 단계 A.

## 한 화면 요약

1. **무엇을 하는가:** leaderboard 상위 100팀의 "지금 점수를 만든 submission"과 그 submission 의 최신 경기 목록(상대·좌석·시각)을 모은다. **replay 는 한 개도 받지 않는다.**
2. **왜 하는가:** 단계 B 에서 어떤 팀의 어떤 경기 replay 를 받을지, **결과를 보기 전에** 규칙대로 동결하기 위해서다. 받을 replay 수(≤120)를 metadata 로 미리 줄인다.
3. **측정:** N/A — 수집만 한다. 성능 판정 없음.
4. **막힌 것 / 다음:** 없음. 완료 보고 → Claude 가 단계 B 선정 목록을 확인 → 단계 B(다운로드·추출, Antigravity) → 단계 C 판정(Codex).

## 1. 허용 범위

| 허용 | 금지 |
|---|---|
| Kaggle API 읽기: leaderboard, team submissions, submission episode 목록 | replay 다운로드 (`competition_episode_replay`) — 단계 B 에서 |
| leaderboard 는 `competition_leaderboard_view` 사용. 100팀이 안 나오면 `competition_leaderboard_download`(CSV, metadata) 허용 — SHA 기록 | 제출·팀 변경·코드 공개 |
| 새 스크립트 `analysis/donor_tape/collect_stage_a.py` 작성 (`tools/` 는 Codex 소유라 쓰지 않는다. 기존 `tools/top10_donor_inventory.py` 는 읽기·참고만) | §2 선정 규칙 변경. 모호하면 BLOCKED 반환 |
| 출력: `analysis/donor_tape_20260919/` (새 폴더, 이미 있으면 중단) | BOARD·KILLS·카드·HYPOTHESES 직접 편집 |

## 2. 수집·동결 규칙 (그대로 구현)

**as_of** = 스크립트 시작 시각(UTC). 모든 파일에 기록.

1. **팀:** leaderboard 1–100위. 우리 팀(Sian, teamId 16668610)은 제외하고 그 사실을 기록한다. 100위 점수를 기록한다(09-18 12:10 UTC 참고값 2831.9).
2. **대상 submission:** 팀의 submission 중 `publicScore` 가 leaderboard 점수와 **소수 첫째 자리까지 같은** 것. 없거나 2개 이상이면 그 팀은 `ambiguous_submission` 으로 표시하고 **제외**한다(추측으로 고르지 않는다).
3. **경기 목록:** 대상 submission 의 episode 목록에서 `state` COMPLETED 이고 `type` 이 `EPISODE_TYPE_PUBLIC` 인 것만. `createTime` 내림차순, 같으면 `id` 내림차순. **최신 12개**까지 metadata 저장(id, createTime, endTime, 양 agent 의 submissionId·teamId·teamName·index·reward).
   - donor 좌석 = donor agent 의 `index` (없으면 0 — 09-16 자료에서 확인된 스키마). 상대 = 다른 agent.
4. **6경기 창:** 위 순서의 **최신 6개**. 6개 미만이면 `insufficient_episodes`.
5. **사전 적격 (replay 없이 판정 가능한 조건만):** 6경기 창에서 서로 다른 상대 teamId **≥4**, donor 좌석 0 과 1 이 **모두** 존재. 미달이면 `ineligible_diversity` 와 실제 값.
   - 6/6 행동 일치는 여기서 판정하지 **않는다**(replay 필요 — 단계 B·C).
6. **단계 B 선정 동결 (`selection_stageB.json`):** 사전 적격 팀 중 **leaderboard 1–60위**만. 각 팀 6경기 창의 **가장 최신 2경기**. 팀 수 × 2 ≤ 120 이어야 한다(초과는 불가능하지만 assert). 61–100위 적격 팀은 `reserve_61_100` 으로 기록한다. **1–60위 적격 팀이 5팀 미만이면**(사람 승인 2026-09-18) `reserve_61_100` 을 순위 순으로 선정 목록에 추가한다 — 1–60위 팀과 합쳐 **5팀이 될 때까지**, 단 단계 B replay 합계 ≤120. 추가 여부와 추가된 팀을 `selection_stageB.json` 에 명시한다.
7. 보상(reward)·승패로 팀이나 경기를 고르거나 빼지 않는다. 저장만 한다.

## 3. 산출물

| 파일 | 내용 |
|---|---|
| `leaderboard.json` | as_of, 100행 원자료 (+ CSV 를 썼다면 그 경로·SHA) |
| `team-<teamId>.json` | 팀 submission 목록 원자료 |
| `submission-<id>.json` | 대상 submission episode 목록 원자료 |
| `inventory.json` | 팀별: rank, score, 대상 submission, 상태(`eligible` / `ambiguous_submission` / `insufficient_episodes` / `ineligible_diversity` / `error`), 6경기 창 id·상대·좌석 |
| `selection_stageB.json` | §2-6 동결 목록 + 규칙 문장 + as_of |
| `summary.json` | 상태별 팀 수, 1–60위 적격 수, 단계 B 예상 replay 수, 에러 목록 |
| `file_hashes.json` | 위 파일 전부 SHA-256 |

## 4. 검증 (완료 조건)

- `summary.json` 의 상태별 합 = 수집 팀 수. 1–60위 중 `error` 0 (있으면 재시도 1회 후 그대로 기록하고 BLOCKED 아님 — 보고서에 명시).
- `selection_stageB.json` 의 모든 경기가 `inventory.json` 의 해당 팀 6경기 창 최신 2개와 일치하는지 assert.
- 재현 명령과 실행 시간 기록. 새 도구 단위 테스트 1개 이상(가짜 episode 목록으로 §2-2~6 규칙 확인).
- 가설 원장: `tools/update_hypotheses.py --agent antigravity --hypothesis-id HYP-0019 --test-id TEST-DONOR-ROUTES-20260917` 로 `다음 행동` 에 산출 경로만 추가(상태·결과 칸 불변, 새 TEST 미배정). `python3 tools/validate_hypotheses.py --strict` exit 0.

## 5. BLOCKED 로 반환할 때

- 인증·네트워크 실패, leaderboard 100행 확보 불가, episode 스키마에 좌석(`index`) 판별 정보가 없음, 대상 submission 규칙(§2-2)으로 1–60위 중 절반 이상이 `ambiguous_submission`.
- 반환 보고에는 막힌 항목과 **가능한 해석 후보**를 적는다. 규칙을 임의로 바꿔 진행하지 않는다.

## 6. 보고

`coordination/reports/antigravity/YYYYMMDD-HHMM-F0-STAGE-A.md` 한 파일. AGENTS §10.1 형식(무엇·왜·측정·다음) + `VERDICT | 핵심 사실 2개 | exact path + SHA | 검증 | NEXT`.
핵심 사실에는 "1–60위 사전 적격 팀 수"와 "단계 B replay 예상 수"를 넣는다.

## 7. 이후 (참고, 이번 지시 아님)

단계 B: `selection_stageB.json` 그대로 replay 다운로드 → donor 좌석 action 배열(steps[1..719][seat].action)·SHA 추출 → 2경기 완전 일치 팀만 남김. 원본 replay 삭제는 사람 승인 후. 단계 C 에서 남은 팀(≤15) 6경기 창의 나머지 4경기를 받아 6/6 판정.


---

## `proposals/claude/20260918-K3-DONOR-FINAL-DECISION.md`

# 최종 결정안 — K3 범위 정정 승인 / donor 제한 진단 보류

작성: Claude (사람 요청으로 Coordinator 역할), 2026-09-18 12:0x UTC. **상태: PROPOSAL — 적용하지 않음.**
`evidence/KILLS.md`·`AGENTS.md`·`coordination/BOARD.md`·`plan/` 무변경. 카드·candidate·adapter·경기·다운로드·제출 없음.
이 문서는 **Coordinator 검토**다. 독립 검토가 아니다. 독립 검토가 끝나지 않은 항목은 모두 "독립 검토 대기"로 표시했다.
이전 Claude 제안(`20260918-K3-SCOPE-REVIEW.md`, SHA `7263c050…4d61`)은 이 문서로 대체한다. 무엇을 고쳤는지는 §F에 있다.

---

## 한 화면 요약

**1. 무엇을 승인 요청하는가**
- **요청하는 것 (1건):** K3 한 줄의 *사실 정정*과 *적용 범위 해석*(§A-3 After 행). 그리고 AGENTS §9와 충돌하는 부분에 대한 사람 결정 D-2(추천 α).
- **요청하지 않는 것:** Majkel donor 4경기 진단. **추천은 보류다.** 이유는 아래 4번과 §C-2에 있다. 6단계 중 **어느 단계도** 이번 승인에 넣지 않는다.

**2. 왜 지금 필요한가**
- K3 재검토 조건이 `—`다. AGENTS §9 "조건 없는 영구 금지는 없다"를 어긴다.
- 같은 문구가 넓게 읽히기도 하고 좁게 읽히기도 해서 적용이 갈렸다. Codex 09-18 donor 제안은 K3를 적용했고, EXP-007 카드는 K3를 인용하지 않았다.
- 새 전략 중단(09-27 00:00 KST)까지 약 8일 남았다. 이후 donor나 tape 관련 판단은 모두 정확한 K3 범위를 기준으로 해야 한다.

**3. 허용 범위와 실행 전 조건 (승인 시)**
- 허용: Antigravity가 §E 체크리스트로 K3 After 문구를 독립 검토한다 → **전 항목 PASS**면 Claude(evidence/plan owner)가 `KILLS.md` K3 행과 plan 두 줄에 주석을 적용한다 → Coordinator가 §B BOARD 문구를 적용한다.
- 실행 전 조건: 검토자가 After 문구를 **한 글자라도 바꾸라고 요구하면 자동 적용을 멈추고** 사람에게 돌아온다. 정의가 달라진 문구는 이번 승인 대상이 아니다.

**4. 허용하지 않는 작업**
- market-only graft를 카드의 `hypothesis`/`one_change`로 쓰는 것 (K3 유지).
- donor 진단 관련 6단계 전부: 정규 카드, adapter 구현, artifact 동결, 구현 검토, 4경기, 결과 보고.
- "K3 범위 밖"이라는 판단을 근거로 전체 donor 재생을 승인하거나 착수하는 것.
- K3 재검토 조건을 새로 만들어 넣는 것 (현재 근거 있는 조건을 정의할 수 없다, §A-4).
- EXP-007에 대한 소급 위반 판정. 반대로 EXP-007을 근거로 새 실험을 허용하는 것.
- BOARD P2 HOLD·release FAIL·EXP-013 미승인 상태의 변경.

**5. 결과별 다음 결정**

| 결과 | 다음 |
|---|---|
| 승인 + 독립 검토 PASS | Claude가 KILLS/plan 적용, Coordinator가 BOARD 적용. donor 진단은 보류 상태로 기록한다. 자동 후속 작업 없음 |
| 승인 + 검토가 수정 요구 | 적용 중지. Claude가 수정본을 만들어 사람에게 다시 제출한다 (문구 정의가 바뀌었기 때문) |
| 거절 | 현행 K3 문구를 유지한다. Codex §2의 K3 적용과 donor BLOCKED를 유지한다. §9 위반(`—`)은 해소되지 않은 채로 남는다는 사실을 BOARD에 기록한다 |
| 사람이 진단도 원함 | §C-3 대안 문장을 사용한다 (비추천) |

**6. 남은 독립 검토와 담당**

| 대상 | 상태 | 담당 |
|---|---|---|
| K3 After 문구 ↔ notebook 원문 대조 (§E) | **독립 검토 대기** | Antigravity (이해관계 없음. Claude는 제안자, Codex는 넓은 읽기를 적용한 당사자) |
| EXP-007 router 코드 서술(§A-5) | **독립 검토 대기** | Antigravity, 같은 검토에서 |
| 이 Coordinator 결정안 전체 | Coordinator 검토만 완료. **독립 검토 아님** | 사람 판단 |
| donor 4경기안 | 보류이므로 검토하지 않음 | — |

```
VERDICT  APPROVE-K3-CORRECTION-ONLY / DONOR-DIAGNOSTIC-HOLD
사실1    K3 원출처로 추정되는 rayk §16(cell 48)은 정성 한 줄이다. 구현·엔진·상대·표본·실패 수치·실패 기제 모두 N/A다
사실2    P1b에서 parent는 Remielle tape·seed 1125321547의 두 좌석 모두 58,246 대 167,541이었다. hosted 108076177과 같은 값이다. 좌석 교대가 새 정보를 주지 않았다
path     coordination/proposals/claude/20260918-K3-DONOR-FINAL-DECISION.md
검증     read-only SHA 대조 12건 일치, python3 tools/validate_hypotheses.py --strict (§G)
NEXT     사람: 승인 문장 선택 → Antigravity §E 검토 → Claude/Coordinator 적용
```

---

## A. K3 정정안

### A-1. 원출처 — 사실만

| 항목 | 값 | 근거 |
|---|---|---|
| K3 현재 행 | `\| K3 \| 라이벌의 전체 마켓 테이프 복사 \| 큰 일반화 실패 \| rayk (남의 실험) \| — \|` | `evidence/KILLS.md:10`, SHA `34f18435…60bf` |
| 최초 기록 | commit `4ed2d29`(2026-09-07). 이후 문구 불변 | `git log -L10,10:evidence/KILLS.md` |
| 수집본 | `docs/code/raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb` SHA `a7447511510ed22b73f2315246b6bf4de66f219ffe3ba692a377f3fb47931331`, fetched 2026-09-16T08:00:12Z, `last_run_time` 2026-08-11 | `docs/collection_inventory.json:281-300`. inventory 자체가 "listed version is not a verified version of unpinned pulled bytes"라고 적었다 |
| **09-07 당시 bytes와 동일한가** | **N/A (미확정).** `docs/code/`는 git 미추적이고, K3 행에는 SHA가 없다 | — |
| cell 48 대응 | K3 행은 "rayk"만 적었다. cell 48 표의 "Copy a full rival market tape \| Large generalization failure"는 K3 문구의 거의 직역이다. 그래서 대응 관계는 **`[INFERENCE]`(강한 문구 일치)**이지 확인된 인용이 아니다 | notebook 전체 grep. "generali[sz]" 일치는 cell 48 한 곳뿐 |

원문 (`[COMMUNITY]`, 인용):

- cell 48: "I screened complete market-tape grafts, …" / "The experiments used both seats and new seeds throughout." / 표 행 "Copy a full rival market tape | Large generalization failure".
- cell 53 (저자의 재서술): "…copying a field layer or an isolated rival market tape is not coherent."

**입증 수준: `[COMMUNITY]` 정성 보고.** 다음은 모두 **N/A**다: 구현(graft를 어느 route에 붙였는지, farmer/hands를 어떻게 다뤘는지, 상태 반응이 있었는지), 실행 엔진(notebook은 `kaggle-environments>=1.32.4`만 요구), 라이벌 신원, 평가 상대, seed 값과 수, 표본 수, 실패 수치(W/L·margin). **실패 기제도 미확정이다.** cell 53의 "not coherent" 설명은 저자의 해석이지 측정이 아니다.

### A-2. 세 종류의 변경을 분리

| 종류 | 내용 | 근거 수준 |
|---|---|---|
| **사실 정정** | 출처를 "rayk"에서 notebook §16 cell 48(추정 대응)·수집 SHA·N/A 목록으로 구체화한다. "큰 일반화 실패"가 정성 문구라는 점과 bytes 동일성 N/A를 명시한다 | 원문 대조 |
| **적용 범위 해석** | K3가 막는 것을 "라이벌의 market 주문 기록을 **그 기록이 나온 경기와 다른 작업 경로**(farmer/hands 기록)에 붙이는 것"으로 정한다. 근거는 원문 단어 "graft", "isolated rival market tape"다. 같은 source episode의 farmer+hands+market 전체 재생은 **이 행의 금지 범위에 넣지 않는다.** 원문이 그런 재생을 다뤘는지는 N/A다 | 원문 단어 기반의 **해석**. 원실험이 farmer/hands를 복사하지 않았다는 사실 확인이 아니다 |
| **새 운영 규칙** | ① K3 재검토 조건 칸: "근거 있는 조건 미정의"와 정의 절차(§A-4). ② 범위 밖 판단은 허용이 아니라는 명시 | 사람 결정 D-2 |

**한계 — 해석이 기제를 가르지 못한다.** 전체 donor 재생도 새 seed·새 상대에서는 경기 상태가 source와 어긋난다. 그러면 market 기록이 원래 짝이었던 재고·현금과 떨어진다. cell 53이 "not coherent"의 이유로 든 것(private inventory)이 전체 재생에도 적용되는지는 **알 수 없다.** 따라서 "범위 밖"은 **정의상의 구분**이다. 전체 재생이 그 실패를 피한다는 주장이 아니다.

### A-3. Before / After

**Before** (`evidence/KILLS.md:10`):

```
| K3 | 라이벌의 전체 마켓 테이프 복사 | 큰 일반화 실패 | rayk (남의 실험) | — |
```

**After** (5열 형식 유지):

```
| K3 | **라이벌의 market 주문 기록을, 그 기록이 나온 경기와 다른 작업 경로(farmer/hands 기록)에 붙이기(graft)** — 원문 "complete market-tape grafts" · 저자 재서술 "isolated rival market tape". 같은 source episode 의 farmer+hands+market 전체 재생은 이 행의 금지 범위가 아니다. **범위 밖이라는 것은 허용이 아니다** — 그 경로는 HYP-0010 · HYP-0019 와 BOARD 게이트를 따른다. *범위 정정 YYYY-MM-DD: 원 문구 "라이벌의 전체 마켓 테이프 복사"는 원출처보다 넓게 읽혔다 — `coordination/proposals/claude/20260918-K3-DONOR-FINAL-DECISION.md`* | `[COMMUNITY]` 정성 보고 "Large generalization failure", 양 좌석 · new seeds. graft 대상 route · farmer/hands 처리 · 상태 반응 여부 · 구현 · 실행 엔진(notebook 요구 ≥1.32.4) · 상대 · seed 수 · 표본 수 · 실패 수치 **N/A**. 실패 기제 **미확정** | rayk notebook §16 cell 48 (문구 일치에 따른 `[INFERENCE]` 대응), 수집본 SHA `a7447511…1331`, fetched 2026-09-16. 2026-09-07 최초 기록 당시 bytes 와의 동일성 **N/A** (남의 실험) | **근거 있는 재검토 조건 미정의 — 원 실패 기제 N/A.** 기제를 식별하는 `[ENGINE]` 또는 `[HOSTED]` 근거가 생기면 evidence owner 가 조건을 정의하고 사람이 승인한다. 그 전까지 market-only graft 는 카드의 `hypothesis`/`one_change` 가 될 수 없다 (§9 부활 차단). §9 와의 관계는 사람 결정 D-2 (YYYY-MM-DD) |
```

같은 적용 커밋에서 할 일 (Claude, plan owner): `plan/kaggriculture_docs_insights_claude-opus-5.md:202`와 `plan/kaggriculture_master_plan_claude-opus-5.md:205`의 K3 줄 끝에 `(범위 정정 YYYY-MM-DD — evidence/KILLS.md K3 참조)`를 붙인다. 본문은 역사 기록이므로 다시 쓰지 않는다.

### A-4. 재검토 조건 — 정의할 수 없는 이유와 AGENTS §9 충돌

이전 제안의 조건 둘을 모두 뺐다.

- **(b) "서로 다른 상대·seed 3경기 이상에서 market 주문열 100% 일치" — 삭제.** 표본에서 행동이 같다는 것은 그 표본의 상태에서 반응할 일이 없었다는 뜻일 수 있다. 상태에 반응하지 않는 policy라는 증거가 아니다. donor 주문과 graft 대상의 생산·현금·재고가 호환된다는 증거는 더더욱 아니다. seat 수나 다른 숫자로 대체하지 않는다.
- **(a) "시장 주문 처리 코드가 달라지면" — 삭제.** 실패 기제가 N/A이므로 어떤 엔진 변경이 그 실패와 관련되는지 설명할 수 없다. 예를 들어 "자기 재고·현금 부족 시 SELL/BUY 부분 체결 규칙 변경"을 적으면 그럴듯해 보인다. 하지만 그것은 cell 53의 해석을 기제로 격상시킨 것이다. 그렇게 쓰면 조건이 해결책처럼 읽힌다.

**결론: 현재 근거 있는 재검토 조건을 정의할 수 없다.** 문서 형식을 채우려고 조건을 만들지 않는다.

**AGENTS §9와 충돌하는 조항과 사람이 결정할 범위 (D-2):**

| §9 조항 | 정정 후 K3 | 충돌 |
|---|---|---|
| "항목에는 엔진 버전 · 상대군 · 구현 · 실패면 · 재검토 조건을 함께 적는다" | 엔진·상대군·구현 N/A, 실패면 정성, 조건 미정의 | 칸은 채웠지만 내용이 N/A다 |
| "조건 없는 영구 금지는 없다" | 조건 미정의 + 정의 절차 | **실질 충돌.** 절차는 있어도 조건 자체는 없다 |
| 부활 차단 (조건을 인용해야 카드 가능, 근거는 ENGINE/HOSTED) | 조건이 없으므로 market-only graft 카드 불가 | 충돌 없음 (일관됨) |

사람이 고를 범위는 **K3 한 행**뿐이다. §9 본문 개정은 요청하지 않는다.

- **α (추천):** 위 After대로 KILL을 유지하고, "조건 미정의 + 정의 절차"를 §9 예외로 **이 행에 한해** 명시 기록한다. 이유: 원출처는 저자의 명시적 부정 결과다. 우리 쪽 관측도 방향이 같다 — HYP-0027 `[LOCAL]` (open-loop farm tape 위 market 광범위 rewrite → pool 0.9787→0.7872), donor M nonempty market index 3경기 일치 0/175 `[HOSTED]` 기술통계. 다만 둘 다 K3 원실험 재현도, 기제 입증도 아니다.
- **β:** K3를 KILLS에서 내려 보류(HELD)로 표시한다(K10 RETRACTED 형식). §9 충돌은 사라지지만 market-only graft 금지도 사라진다.
- 대회는 09-30에 끝난다. 두 선택 모두 그 전에 조건이 정의될 가능성은 낮다. 그래서 α는 사실상 대회 끝까지 금지로 작동한다. 이 점을 알고 고른다.

### A-5. 관련 사례

**EXP-007 (규칙 적용 일관성 사례)**
- 사실: `releases/public-thomas-replay-router-v2-exact/main.py`(SHA `82412467…5a97`)의 `agent()`는 72턴 block마다 `route_for()`로 공개 관측 기반 tree를 평가하고, 선택한 schedule의 farmer/hands/market을 그대로 낸다(market은 파싱 불가 slot만 `['SELL','WHEAT',0]`로 바꿈, `:614-666`). 이전 제안의 "turn 144에 전환"은 이번 읽기로 **확인하지 못했다**. 실제 전환 시점은 tree 내용에 달려 있다 — **독립 검토 대기**.
- 해석: block 경계에서 schedule이 바뀌면, 앞 schedule이 만든 농장 상태 위에 다른 schedule의 market이 붙는다. 이것이 정정 K3의 "graft"에 해당하는지는 **회색 지대**다.
- 처리: 제출(09-12) 당시 K3 적용 범위가 불명확했다. 그래서 **소급 위반을 판정하지 않는다.** 반대로 EXP-007이 제출됐다는 사실은 **새 router/replay 실험의 허용 근거가 아니다.** 사례로만 기록한다. 활성 제출은 건드리지 않는다.

**rayk cell 28 — 전체 route 복사 미전이**
- 원문: "Copying the whole irregular route did not transfer" (수치 N/A). HYP-0010 주의사항으로 둔다. 이미 09-18 Claude event로 기록돼 있다. **새 KILL을 만들지 않는다.**
- 같은 notebook의 관련 주의 (`[COMMUNITY]`): cell 53 "copying a field layer … is not coherent", cell 49 "live rivals are exact public action reconstructions and may not expose every branch of their original policies". 반대 방향 보고도 있다: cell 8 c14 exact field+market schedule 채택 성공, cell 13 c16. HYP-0010 주의사항에 함께 둔다.

**"다른 상대에서 성공한 exact 복사본 HOSTED 사례 1건"**
- 기존 계약이 아니다. Codex `20260918-DONOR-MINIMUM-TRANSFER-CHECK.md` §2가 새로 제안한 조건이다. AGENTS §9·KILLS 머리말 어디에도 없다. 필수조건으로 유지하지 않는다. 정정 K3에서는 전체 donor 재생이 범위 밖이므로 이 조건이 걸릴 대상도 없다.

---

## B. BOARD 변경안 (Coordinator, 승인·검토 PASS 후에만)

"실험·가설의 현재 결론"에 한 줄 추가:

```
- **K3 범위 정정 (YYYY-MM-DD 승인, Antigravity 검토 PASS):** K3는 market 주문 기록을 다른 작업 경로에 graft하는 것만 막는다. 원출처 [COMMUNITY] 정성, 구현·엔진·표본·기제 N/A, 재검토 조건 미정의(§9 예외 D-2 α). 같은 episode 전체 donor 재생은 K3 밖이지만 **허용이 아니다** — P2 HOLD 적용. Majkel donor 4경기 진단은 보류([결정안](proposals/claude/20260918-K3-DONOR-FINAL-DECISION.md) §C-2). EXP-007은 소급 판정 없는 일관성 사례.
```

P2 행과 C0/C1 경로는 바꾸지 않는다. 거절 시에는 "K3 재검토 조건 `—`, §9 미해소, 현행 문구 적용"을 같은 위치에 한 줄로 적는다.

---

## C. Donor 4경기안 검토

기준: Codex `20260918-DONOR-MINIMUM-TRANSFER-CHECK.md` §3 (SHA `e12431e6…8306`). donor·상대·seed·표본 수는 바꾸거나 늘리지 않았다.

### C-1. 확인한 것

| 항목 | 결과 |
|---|---|
| donor source | `private_artifacts/top10_donor_20260916/episode-109675071-replay.json` SHA `11758bf6…4eaa` 일치. TeamNames `['Majkel1337','M & M & P & Q']`, source seat0, 원래 seed 2116997393, 결과 **Majkel 패** (100,050 대 107,191). 719-action SHA `0ec1d716…6baa` 재계산 일치 |
| 실행용 donor artifact | **N/A.** raw replay와 action hash는 source identity일 뿐, agent 구현이 아니다 |
| parent identity | tar `1c478c24…9721` 일치. clean-room `main.py` `bba042e0…96b2`(P1b identity.json). tar 구성은 `main.py`·`yh_base.py`·`actions.json`·`LICENSE.txt` |
| runner | P1b 당시 `tools/instrument.py` `284dee4c…0629`, 현재 `ca64256f…fe28`. **다르다.** 따라서 A baseline을 새로 기록해야 한다(Codex 안에 포함) |
| 상대 | `Remielle_episode-108076177-actions.json` `75ea188e…a5c4`. 720행 고정 transcript |

**원래 경기 재현과 다른 조건의 차이.** hosted 108076177은 Remielle(seat0) 167,541 대 우리 EXP-006(seat1) 58,246이었다. P1b에서 parent A는 같은 seed·같은 tape로 **두 좌석 모두 정확히 58,246 대 167,541**이었다. 그래서 A 두 셀은 사실상 **원 hosted 경기의 재현**이다. D 두 셀은 다르다. Remielle tape는 EXP-006의 플레이에 반응해 기록된 행동인데, D를 상대로는 반응하지 않는다. D 셀이 재는 것은 "Majkel 기록 vs Remielle 선수"가 아니라 **"Majkel 기록 vs EXP-006을 상대로 녹화된 Remielle 기록"**이다.

**고정 tape의 한계.** 두 에이전트 모두 상대에게 반응하지 않는 기록이다. 이 조합은 결정론적인 한 궤적만 만든다. Remielle tape의 주문도 D와의 시장 상호작용 때문에 원래와 다르게 체결될 수 있다. 그래서 상대 역시 "Remielle의 route"를 그대로 재현한다고 볼 수 없다.

**좌석 대칭.** 위 P1b 수치가 보여 주듯 이 조건에서 좌석 교대는 같은 결과를 거울처럼 되풀이했다. D에서도 그렇다면 4셀은 **A 관측 1개 + D 관측 1개**다. 두 좌석을 독립 표본 2개로 세지 않는다. Codex 안도 이 점을 적었다.

**성공해도 주장할 수 없는 것.** 일반화, hosted 강도, top10 상대 강도, donor 본인 policy와의 동일성, 제출 가능성. Codex 안 §4와 같다.

### C-2. 보류 사유 (구체)

1. **결과가 지금의 어떤 결정도 바꾸지 않는다.**
   - success면 "독립 평가를 설계할 가치"가 생긴다. 하지만 독립 평가 표본은 **N/A**다(Codex 안 스스로 미선정).
   - source 경기 안에서도 이미 실패하거나 부분 체결된 주문이 있다: index20 STRAWBERRY seed 재고 0→0, index25 HIRE8 요청 → hands 4/4/3. 새 seed·상대에서는 hands 길이 정렬(§7.5 Schema)과 zero-gate counter가 어떻게 나올지 **N/A**다. 통과하지 못하면 guard를 붙인 D는 **다른 정의**이고, 새 카드가 필요하다.
   - 09-27 00:00 KST 새 전략 중단 전에 success → 독립 평가 카드 → 수정 D 카드 → release gate를 거칠 여지가 거의 없다.
   - failure면 이 단일 tape가 종료된다. 이 tape는 지금 어느 경로에도 올라 있지 않다.
2. **정보량이 1비트 수준이다.** 고정 tape 한 개, seed 한 개, 거울 대칭 좌석. §C-1 참조.
3. **P2 HOLD의 첫 예외가 된다.** P2 HOLD는 P1b parent FAIL에서 나왔다. 이 진단은 correctness 경로(C0/C1)가 아니라 HYP-0010 전략 탐색이다. 1·2를 감안하면 HOLD를 깰 만한 근거가 부족하다.
4. **사전 기대가 낮다.** rayk cell 28/49/53의 `[COMMUNITY]` 부정·주의 보고가 있다. KILL 근거는 아니다.

**보류를 다시 결정 대상으로 올리는 조건 (자동 대기열 아님).** 사람이 요청한 경우에만 Claude가 다음 두 가지를 문서로 준비한다. ① success 분기가 도달할 다음 카드: 사전 동결된 독립 평가 seed·상대·seat 목록, D의 hands 정렬·zero-gate 처리 정의. ② 그 카드가 09-27 00:00 KST 전에 끝나는 일정. 둘이 없으면 다시 올리지 않는다.

### C-3. 대안 (비추천) — 진단까지 승인할 경우의 단계 경계

사람이 진단을 원하면 **한 번의 승인으로** 아래 1–6을 묶는다. 정의는 Codex 안 §3 그대로 고정한다: donor 109675071 seat0 / parent tar `1c478c24…` / Remielle tape `75ea188e…` / seed [1125321547] / seats [0,1] / 4셀 / 판정표. 미정 구현에 대한 포괄 승인이 되지 않게, **정의가 바뀌면 그 단계에서 멈춘다.**

| 단계 | 담당 | 진행 조건 | 멈춤 (자동 진행 안 함) |
|---|---|---|---|
| 1 정규 카드 | Claude | AGENTS §5 스키마 전 항목 숫자·exact. HYP-0010 인용, 새 TEST ID, postmortem 108076177 인용(§7.3), K3 "범위 밖·허용 아님" 명시 | 서술형·모호 항목이 1개라도 있음, 또는 정의가 Codex 안과 다름 → 사람에게 반환 |
| 2 adapter | Codex | `obs.step=t` → source `steps[t+1][0].action`. guard·fallback·수정 없음. 두 seat 모두 source seat0 | 엔진 오류를 피하려고 guard가 필요 → 다른 정의 → 반환 |
| 3 동결 | Codex | adapter·runner·config·A baseline command의 path+SHA를 카드에 기록 | SHA 변동 |
| 4 독립 구현 검토 | Antigravity | index 정렬·seat 처리·identity PASS | FAIL → 반환 |
| 5 4경기 | Codex | 1–4 전부 PASS 후. A 두 셀 먼저 → A가 58,246/167,541과 다르면 **INVALID로 정지** | 표본 추가·교체 금지 |
| 6 보고·종료 | Codex 보고 / Claude 판정 기록 | 아래 표 | 후속 실행 없음 |

| 판정 (Codex 안 §3 수치 그대로) | 종료 |
|---|---|
| success: valid, D 2/0/0, 양 seat score +1 | 이 exact tape의 독립 평가 **설계 검토**만. 실행·release 승인 아님 |
| failure: valid, D 0/0/2 | 이 단일 tape 전체 재생 종료. donor 활용 전체 KILL 아님 |
| 혼재: 그 밖의 valid 결과 | 결정 없음. seed/tape 추가 금지 |
| INVALID: 누락·SHA 불일치·예외·A 재baseline 불일치 | 성능 판정 N/A. 자동 repair 금지 |

대안 승인 문장 (비추천):
> 승인: 결정안 §A-3 K3 정정(D-2 α)과 §C-3 표의 단계 1–6을 Codex 안 §3의 고정 정의로 한 번에 승인한다. 각 단계의 멈춤 조건에 걸리면 자동 진행하지 않고 나에게 돌아온다. 결과와 무관하게 제출·release·추가 경기는 승인하지 않는다.

---

## D. 추천

**K3 범위 정정만 승인 요청한다. donor 제한 진단은 §C-2 사유로 보류한다.**

## E. 독립 검토 체크리스트 (Antigravity, 독립 검토 대기)

1. After 1열 범위가 cell 48·53의 단어("graft", "isolated rival market tape")를 넘지 않는가. farmer/hands를 복사하지 않았다고 **단정하지 않는가**.
2. 2·3열의 N/A 목록이 원문과 맞는가. 수치를 새로 만들지 않았는가. bytes 동일성 N/A와 cell 48 대응 `[INFERENCE]`가 유지되는가.
3. 5열이 조건을 만들어 넣지 않았는가. §9 충돌 서술(§A-4)이 정확한가.
4. "범위 밖 ≠ 허용"이 1열과 BOARD 문구에 모두 있는가.
5. §A-5 EXP-007 코드 서술(`main.py:614-666`, block별 tree)이 코드와 맞는가.
6. 보고: `coordination/reports/antigravity/`에 PASS/FAIL 항목별로 1파일. 수정 요구가 있으면 적용하지 않는다.

## F. 이전 Claude 제안에서 고친 것

| 이전 | 이번 |
|---|---|
| "exact 인용 위치 cell 48" | 대응은 `[INFERENCE]`. 09-07 bytes 동일성 N/A |
| 원문 확인표 "시장 주문 layer. 확인" | 원문 **단어**가 market tape를 가리킬 뿐이다. 구현 범위는 N/A |
| 재검토 조건 (a) ENGINE 시장 코드 변경 | 삭제. 기제 N/A → 관련성 설명 불가 |
| 재검토 조건 (b) 3경기 100% 일치 | 삭제. 비반응성·호환성 증거가 아님 |
| 선택지 A/B/C | 하나로 정리. §9 충돌은 D-2 α/β로 분리 |
| EXP-007 "turn 144 전환" | 코드상 block별 tree. 전환 시점 미확인, 독립 검토 대기 |
| B안 "K3 비적용이면 설계 가능" 뉘앙스 | 범위 밖 ≠ 허용. 진단은 별도 사유로 보류 |

## G. 검증과 원장 기록

입력 SHA-256 (이번 read-only 확인):

| 파일 | SHA-256 |
|---|---|
| `AGENTS.md` (작업 트리) | `f53bdcd455707f6aef33123f2c86c24e9e022befc1aed973d04fd51a955cae20` |
| `coordination/BOARD.md` | `0df85ca3a0177f26525820dd5c19f900f8dc86f4de9ef7a4cff927adc9f15eba` |
| `HYPOTHESES.md` (updater 실행 전) | `ada90589d25ec8c5fcb22f730b15a7e3a165a8820c92f040eaec4ecda6783088` |
| `evidence/KILLS.md` | `34f18435d713b4df0b6449c993b3cd4bd7b17e7135dfdd9a65628760d89660bf` |
| `coordination/proposals/claude/20260918-K3-SCOPE-REVIEW.md` | `7263c050dc1191846337174f79db489155083fa8a15cb217ff7056d259c54d61` |
| `coordination/proposals/codex/20260918-DONOR-MINIMUM-TRANSFER-CHECK.md` | `e12431e644e57a249ae2bf20d9d1dec53fb4094caea008cb53f2f5cccaea8306` |
| rayk notebook | `a7447511510ed22b73f2315246b6bf4de66f219ffe3ba692a377f3fb47931331` |
| donor raw 109675071 | `11758bf6601ff6c14da94f6e62fac4f8f7ba7988f5b79e7c5af8ccdfa9fc4eaa` |
| parent tar | `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` |
| Remielle tape | `75ea188ed138167b274ce34d20ce3476adfcfe25ee75d6feb7ed4e8de7caa5c4` |
| P1b target seat0 / seat1 | `9513e586…81b0` / `b5f2e6e2…18e4` |
| thomas router `main.py` | `8241246765098c50223d897739cb32076b71a303284d2e5e1c5f0fb495bb5a97` |
| `tools/instrument.py` (현재) | `ca64256f941f2098cafc531fc422363c5757995f721b449369ce72877a33fe28` |

재현 (read-only):

```bash
python3 -c "import json;nb=json.load(open('docs/code/raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb'));[print(i,''.join(nb['cells'][i]['source'])) for i in (8,13,28,40,48,49,53)]"
python3 -c "import json;[print(s,json.load(open(f'experiments/results/p1_release_preflight/cells/target_seed-1125321547_seat-{s}.json'))['payload'][0]['rewards']) for s in (0,1)]"
python3 -c "import json;print(json.load(open('experiments/results/hosted_postmortem_108076177.json'))['rewards'])"
```

원장 기록과 strict validation 결과는 아래 "실행 기록"에 적는다.

## 실행 기록

- updater: `python3 tools/update_hypotheses.py --agent claude --hypothesis-id HYP-0010 --test-id TEST-DONOR-ROUTES-20260917 --set '다음 행동=<기존 값 + 이 결정안 요약>'` → exit 0. event `coordination/hypotheses/claude/EVT-2026-09-18T120623.398186+0000-8e1769da.json`, SHA `f86ef9975e84bf5ee3e2ce41e332589077b159c933c363699b18538872a69c32`. 바뀐 칸은 `다음 행동` 하나다. 상태 SOURCE_CLAIM, 로컬/Hosted N/A는 유지했다. 새 HYP/TEST/EXP ID는 배정하지 않았다.
- `python3 tools/validate_hypotheses.py --strict` → **exit 0, "hypothesis ledger PASS: 32 entries"**.
- 부수 사건 1건: 이번 세션 초기에 read-only `git status`가 `.git/index.lock`(0 byte)을 만들었는데, 삭제 권한이 없어 남아 있었다. 사람의 삭제 권한 승인 후 이 파일 하나만 지웠다. updater lock은 정상 해제됐다.
- 커밋하지 않았다. 대상은 이 파일과 위 event 1개다.


---

## `proposals/claude/20260918-K3-REVIEW-REQUEST-ANTIGRAVITY.md`

# 독립 검토 요청 — K3 정정 문구 (Codex)

**개정 r2 2026-09-18:** 사람 지시(판단·결정 문제는 Codex)로 수신자를 Antigravity → **Codex** 로 바꿨다. 파일명은 이력 보존을 위해 그대로 둔다.
**이해관계 고지:** Codex 는 09-18 donor proposal §2 에서 K3 를 넓게 적용한 당사자다. 그 proposal 의 판단을 지키거나 뒤집는 것이 목적이 아니다. **원문과 문구의 일치만** 판정한다.

발행: Claude (제안자 겸 Coordinator 역할), 2026-09-18. 수신: **Codex**. 사람이 K3 정정 문구를 승인했으며, 적용 조건은 이 검토의 **전 항목 PASS** 다.
Claude 는 제안자이므로 이 검토의 결론을 대신 내릴 수 없다(AGENTS §4).

## 읽을 것 (이 순서)

1. `AGENTS.md` §3, §4, §9
2. `evidence/KILLS.md` — K3 현재 행 (SHA `34f18435…60bf`)
3. **원문**: `docs/code/raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb` (SHA `a7447511510ed22b73f2315246b6bf4de66f219ffe3ba692a377f3fb47931331`) — markdown cell 8, 13, 28, 40, 48, 49, 53
   ```bash
   python3 -c "import json;nb=json.load(open('docs/code/raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb'));[print(i,''.join(nb['cells'][i]['source'])) for i in (8,13,28,40,48,49,53)]"
   ```
4. 검토 대상: `coordination/proposals/claude/20260918-K3-DONOR-FINAL-DECISION.md` (SHA `466aca3f427fecb8424b6b31e4cb3d5c94d87cdd6e57d6341bf38bb1cec69598`) — §A-1~A-5, §B, §E
5. EXP-007 코드: `releases/public-thomas-replay-router-v2-exact/main.py` (SHA `8241246765098c50223d897739cb32076b71a303284d2e5e1c5f0fb495bb5a97`) `:614-666`

**원문을 먼저 읽고 결정안을 나중에 읽는다.** 결정안의 해석을 전제로 원문을 읽지 않는다.

## 판정할 항목 (§E 그대로)

| # | 질문 | PASS 조건 |
|---|---|---|
| E1 | After 1열 범위가 cell 48·53 의 단어("complete market-tape grafts", "isolated rival market tape")를 넘지 않는가. farmer/hands 를 복사하지 않았다고 **단정하지 않는가** | 두 조건 모두 참 |
| E2 | 2·3열의 N/A 목록이 원문과 맞는가. 수치를 새로 만들지 않았는가. 09-07 bytes 동일성 N/A 와 cell 48 대응 `[INFERENCE]` 가 유지되는가 | 원문에 없는 수치·사실 0건 |
| E3 | 5열(재검토 조건)이 근거 없는 조건을 만들어 넣지 않았는가. §9 충돌 서술(§A-4 표)이 조항과 정확히 대응하는가 | 둘 다 참 |
| E4 | "범위 밖 ≠ 허용"이 After 1열과 §B BOARD 문구에 모두 있는가 | 둘 다 있음 |
| E5 | §A-5 EXP-007 서술 — 72턴 block 마다 tree 로 schedule 선택, market 은 파싱 불가 slot 만 치환 — 이 코드와 맞는가. "turn 144 전환"을 확인된 사실로 쓰지 않았는가 | 둘 다 참 |

## 규칙

- **아무 파일도 고치지 않는다.** KILLS·결정안·BOARD 모두. 수정이 필요하면 FAIL 과 함께 **정확한 대체 문구**를 제안한다.
- 판정은 PASS / FAIL 두 가지다. 애매하면 FAIL 로 두고 이유를 적는다.
- 원문 인용은 항목당 한 줄 이내.

## 보고

`coordination/reports/codex/YYYYMMDD-HHMM-K3-WORDING-REVIEW.md` 한 파일. 가설 원장 기록은 하지 않는다(판정 결과만).

```
VERDICT  PASS | FAIL (E# 목록)
E1 … E5  각 PASS/FAIL + 근거 cell 번호 또는 file:line
FAIL 항목의 대체 문구 (있을 때만)
읽은 파일 SHA-256 (위 5개와 일치 여부)
```

**E1 또는 E4 가 FAIL 이면** 보고서 첫 줄에 `SCOPE-FAIL` 을 적는다(donor 제출 단계 E 를 멈추는 신호). 전 항목 PASS 면 Claude 가 `evidence/KILLS.md` K3 행과 plan 두 줄에 적용한다. FAIL 이 하나라도 있으면 적용하지 않고 사람에게 돌아간다(문구가 바뀌면 승인 대상이 달라지기 때문).


---

## `proposals/claude/20260918-K3-SCOPE-REVIEW.md`

# K3 실패 범위와 재검토 조건 — 정정 제안 1건

작성: Claude, 2026-09-18 (UTC 11:1x). **상태: PROPOSAL.** `evidence/KILLS.md`·`AGENTS.md`·`BOARD.md`는 바꾸지 않았다.
K3를 해제하지 않았고, 경기·candidate·제출·다운로드·새 HYP/EXP/TEST ID 선점도 하지 않았다.

1. **무엇을 바꾸거나 시험하는가:** K3 한 줄의 적용 범위와 재검토 조건 문구. 시험은 하지 않는다.
2. **왜 하는가:** K3의 재검토 조건이 `—`여서 AGENTS §9("조건 없는 영구 금지는 없다")를 어긴다. 문구도 원출처보다 넓게 읽혀 에이전트마다 다르게 적용되고 있다(§3).
3. **무엇을 측정했고 결과가 어땠는가:** 새 측정 N/A. 로컬 원자료를 읽기만 했다. 원출처는 정성 한 줄("Large generalization failure")이며 판수·상대·seed·수치는 전부 N/A다.
4. **무엇이 막혀 있고 다음 행동은 무엇인가:** 사람이 범위 선택지(§4)를 고르고 독립 검토자를 지정해야 한다. 그 전까지 현행 K3 문구를 그대로 적용한다.

```
VERDICT  PROPOSE-NARROW (추천: 입증된 실패 범위로 한정 + ENGINE/HOSTED 재검토 조건 명시)
사실1    원출처는 rayk §16의 "complete market-tape grafts" → 표 한 줄 "Copy a full rival market tape | Large generalization failure". 시장 layer만 다룬다. 수치 N/A
사실2    "HOSTED 성공 사례 1건"은 AGENTS §9에 없는 조건이다. Codex 09-18 proposal이 새로 제안했다
path     coordination/proposals/claude/20260918-K3-SCOPE-REVIEW.md (이 파일)
검증     python3 tools/validate_hypotheses.py --strict (§7)
NEXT     사람: A/B/C 중 선택 + (b) 수치 승인 → 독립 검토 → Claude(evidence owner)가 KILLS.md 적용
```

---

## 1. 원출처 추적

로컬 자료만으로 원문을 확인했다. 공개 Kaggle 페이지는 조회하지 않았다. 지금 조회하면 **현재** 버전만 보인다. 그 버전으로는 K3가 쓰인 09-07 당시 버전을 확인할 수 없어서 N/A가 줄지 않는다.

| 항목 | 값 | 근거 |
|---|---|---|
| K3 현재 원문 | `\| K3 \| 라이벌의 전체 마켓 테이프 복사 \| 큰 일반화 실패 \| rayk (남의 실험) \| — \|` | `evidence/KILLS.md:10` (파일 SHA `34f18435…60bf`) |
| K3 최초 기록 | commit `4ed2d29` (2026-09-07, 프로젝트 초기화) 이후 문구 불변 | `git log -S'K3' -- evidence/KILLS.md` |
| 계획서 반복 | `plan/kaggriculture_docs_insights_claude-opus-5.md:202`, `plan/kaggriculture_master_plan_claude-opus-5.md:205` — 같은 요약. 상세 없음 | 파일 직접 확인 |
| 원출처 notebook | Ray Kretzschmar, "Kaggriculture: Findings from Zero to Top Meta" | `docs/collection_inventory.json` |
| URL | https://www.kaggle.com/code/raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta | 같은 inventory |
| 로컬 경로·SHA | `docs/code/raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb`, SHA-256 `a7447511510ed22b73f2315246b6bf4de66f219ffe3ba692a377f3fb47931331` (240,118 B) | `sha256sum`; inventory `sha256`과 일치 |
| 수집일·버전 | fetched 2026-09-16T08:00:12Z, Kaggle `last_run_time` 2026-08-11T14:13:28. `docs/code/`는 git 미추적이다. **K3를 쓴 09-07 당시에 읽은 bytes가 이 SHA와 같은지는 N/A** | inventory; `git ls-files docs/code` 결과 없음 |
| exact 인용 위치 | markdown cell 48 (0-based), "## 16. C94: protect feed first, advance only fertilizer" | 아래 인용 |

**exact 인용 (cell 48):**

> I screened complete market-tape grafts, five/ six/ 14/ 19-unit wheat openings, premium-product splits, wheat and fertilizer splits, late-only timing, two-turn anticipation and gates based on whether the opponent resembled our route. The experiments used both seats and new seeds throughout.
>
> | Copy a full rival market tape | Large generalization failure |

**항목별 확인 결과 `[COMMUNITY]`:**

| 항목 | 원문에서 확인한 것 | 상태 |
|---|---|---|
| 구현 | "complete market-tape **grafts**" / "Copy a full rival **market** tape" | 시장 주문 layer. 확인 |
| graft의 host route | 명시 없음. §16이 C92 수정 탐색이라 C92 route일 가능성이 있음 `[INFERENCE]` | **N/A** |
| farmer/hands 복사 여부 | 원문 없음. "market tape"만 언급 | **N/A** — 복사했다고도, 안 했다고도 적지 않는다 |
| 고정 schedule vs 상태 대응 | "tape"는 notebook §4.1에서 고정 schedule을 뜻한다("Is the market schedule also stable, or is it reacting to the match?"). graft 구현에 sanitize나 조건 로직이 있었는지는 없음 | **N/A** |
| 라이벌 신원 | 없음 | N/A |
| 엔진 | notebook setup이 `kaggle-environments>=1.32.4`를 요구 (cell 2). 실행 버전은 N/A. 우리 lock은 1.32.7 | N/A |
| 평가 상대 | 없음. 같은 §16의 다른 행은 "several established agents", "Kaito's route", C92를 언급한다 | N/A |
| seed | "new seeds throughout" — 값·개수 없음 | N/A |
| seat | "both seats" | 확인 |
| 표본 수 | 없음. 같은 절의 "900 games over six new seeds"는 finalist 5종의 held-out이고 graft는 그 표에 없다 | **N/A** |
| 실패 지표 | 정성 문구 "Large generalization failure". W/L·margin·BT 없음 | N/A |

**같은 notebook 안의 관련 서술 (모두 `[COMMUNITY]` 자기보고, K3의 인용 대상은 아님):**

| cell | 내용 | K3와의 관계 |
|---|---|---|
| 8 (§4.1) | senkin13의 "exact 720-turn field and market schedule"을 채택하고 cleanup을 더해 c14를 만듦 → c11–13에 27-3, ladder 2182.2 | 저자 본인이 **field+market 전체 tape 채택을 성공 사례로 보고** |
| 13 (§4.3) | VN-Orion의 "exact full tape"를 c16의 base schedule로 교체 | 같은 방향 |
| 28 (§4.9) | Aleks: "Copying the whole irregular route did not transfer" (수치 없음) | **전체 route 복사의 별도 부정 사례.** K3의 인용 대상은 아니다 |
| 40 (§9) | "a small market-timing change can transfer better than another full clone", "broad route swaps regressed" | 전체 clone이 **상대적으로** 열세라는 요약 |
| 53 (§19) | "copying a field layer or an isolated rival market tape is not coherent" | 저자가 문제를 **"isolated" market tape**로 한정해 다시 서술 |

## 2. 원래 실험이 실패로 보인 것

- **입증 수준:** `[COMMUNITY]` 저자의 로컬 스크리닝에 대한 정성 보고. 우리가 재현하지 않았다.
- **대상:** 라이벌의 complete market tape를 **graft한 것**. graft는 다른 무언가 위에 붙인다는 뜻이다. 원문 표현이 가리키는 범위는 "시장 주문 layer를 통째로 라이벌 것으로 바꾸기"까지다.
- **원문에 없는 것:** farmer/hands까지 같은 source에서 복사했는지, host route가 무엇인지, 상태 대응이 있었는지, 몇 판이었는지. 이 빈칸을 좁게도 넓게도 채우지 않는다.
- **관련 기제의 우리 근거:** HYP-0027 `[LOCAL]` (EXP-005 X1, 1.32.7). open-loop farm tape는 그대로 두고 market schedule만 넓게 바꿨더니 pool 0.9787 → 0.7872로 떨어졌다. market layer와 farm/cash/shed timing이 결합돼 있다는 뜻이다. 이는 K3의 **좁은 범위**와 같은 방향의 증거다. 다만 K3 원실험을 재현한 것은 아니다.
- **관련 `[HOSTED]` 기술 통계:** Codex donor route 분석에서 donor M의 세 경기 중, 한 경기에서라도 market 주문이 있는 index 175곳의 일치는 **0/175**였다 (`coordination/reports/codex/20260917-1640-DONOR-ROUTES.md` §4, SHA `75a216f3…b24b`). 상위 donor의 market은 경기마다 다르다는 뜻이다. 따로 떼어 낸 market tape가 다른 경기에 맞지 않을 수 있다는 설명과 맞는다 `[INFERENCE]`.

## 3. 현재 문구가 원자료보다 넓은가 — 넓다

현재 "라이벌의 전체 마켓 테이프 복사"는 두 가지로 읽힌다.

| 읽기 | 포함 범위 | 원출처와의 관계 |
|---|---|---|
| (i) 좁은 읽기 | 시장 주문 layer 전체를 라이벌 것으로 교체 (graft) | 원문과 일치 |
| (ii) 넓은 읽기 | 전체 market을 **포함하는** 모든 복사: 같은 episode의 farmer+hands+market 전체 재생, 공개 replay router 등 | 원문에 없음. 저자 본인의 c14/c16 성공 보고(cell 8, 13)와 충돌 |

실제로 두 읽기가 모두 쓰였다:

- **(ii)로 적용된 경우:** Codex 09-18 donor proposal §2는 "farmer+hands+market 전체 재생은 전체 market 복사를 포함하므로 K3 적용 대상"이라고 판정했다.
- **K3를 인용하지 않은 경우:** EXP-007(Claude 사전등록 09-11)은 thomas replay router v2 exact를 제출했다(`56175620`, tar `8031d51a…0180`). 이 artifact는 공개 replay의 전체 schedule을 재생하고, market 주문은 파싱 불가 slot만 무해화해 그대로 낸다(`releases/public-thomas-replay-router-v2-exact/main.py:630-666`, SHA `82412467…5a97`). turn 144에 5개 schedule 중 하나로 전환한다. 카드와 원장 어디에도 K3 인용이 없다(`grep -n K3 experiments/cards/EXP-007*` 결과 없음).
- 즉 (ii)로 읽으면 **현재 hosted 활성 슬롯 하나가 K3 범위 안**에 있다. (i)로 읽으면 두 경우 모두 K3 밖이다. 문구가 이 차이를 정하지 않기 때문에 적용이 갈렸다.

현재 문구가 원출처보다 **더 금지한 것**: 같은 source episode의 farmer+hands+market 전체 재생, 여러 공개 schedule 사이의 router, c14식 exact full-tape 채택. 게다가 재검토 조건이 `—`여서 이 금지는 영구적이다.

§9 형식 기준으로 봐도 K3에는 필수 칸인 엔진 버전·상대군·구현·실패면·재검토 조건이 모두 비어 있다.

다음 두 극단은 모두 피한다.
- "남의 실험이므로 무효" — 틀리다. `[COMMUNITY]`도 저자의 명시적 부정 결과이고, 좁은 범위에서는 HYP-0027·HOSTED 기술 통계와도 방향이 같다.
- "상세가 없으므로 모든 복사를 영구 금지" — 틀리다. 원문에 없는 범위를 금지하는 것이고 §9에도 어긋난다.

## 4. 처리 선택지와 실험 허용에 미치는 영향

| 선택 | K3가 막는 것 | Codex donor 4셀안 | EXP-007 같은 router | market-only graft |
|---|---|---|---|---|
| **A.** 현재 범위 유지 + 조건 명시 | (ii) 전체 | K3 적용. 아래 (a)/(b) 조건이 성립해야 카드 가능 | 소급해서 K3 범위. 이미 제출된 것의 처리를 사람이 정해야 함 | 금지 |
| **B. 입증된 범위로 한정 (추천)** | (i) market-only graft | **K3 비적용.** 그래도 P2 HOLD·실행 artifact 없음·카드/독립검토/사람승인 필요로 **여전히 실행 불가** | K3 비적용 | 조건 성립 전까지 금지 |
| **C.** 증거 부족 보류로 정정 | 없음 (KILLS에서 HYP로 이동) | K3 비적용, 다른 블록은 동일 | 비적용 | **금지 해제.** 저자의 명시적 부정 결과와 HYP-0027을 잃는다 |

**B를 추천하는 이유**
1. 원문 단어("market tape", "graft", 저자의 재서술 "isolated rival market tape")가 가리키는 범위가 정확히 (i)이다.
2. 좁은 범위에서는 우리 `[LOCAL]` HYP-0027과 `[HOSTED]` 기술 통계(0/175)가 같은 방향이다. 그래서 C처럼 금지를 풀 이유는 없다.
3. (ii)는 원출처에 근거가 없다. 저자 본인의 c14/c16 성공 보고와도 충돌한다. 넓은 금지는 KILL이 아니라 가설로 다룬다(HYP-0010·HYP-0019). 전체 route 복사에 대한 저자의 별도 부정 보고(cell 28)는 HYP-0010의 주의사항으로 남긴다(§7).
4. B는 K3를 **해제하지 않는다.** market-only graft 금지는 그대로다. donor 전체 재생도 다른 블록 때문에 계속 막혀 있다. 바뀌는 것은 "K3 때문에 설계조차 못 한다"는 판정 하나다.

### 4.1 정확한 변경 문구 (B)

**Before** (`evidence/KILLS.md:10`):

```
| K3 | 라이벌의 전체 마켓 테이프 복사 | 큰 일반화 실패 | rayk (남의 실험) | — |
```

**After**:

```
| K3 | **라이벌의 complete market tape 를 다른 route 에 graft** — 시장 주문 layer 만 라이벌 것으로 통째 교체. 같은 source episode 의 farmer+hands+market 전체 재생과 공개 replay router 는 이 항목이 아니다 (→ HYP-0010 · HYP-0019). *정정 YYYY-MM-DD: 원 문구 "라이벌의 전체 마켓 테이프 복사"는 전체 agent 복사까지 읽혀 원출처보다 넓었다 — `coordination/proposals/claude/20260918-K3-SCOPE-REVIEW.md`* | C94 탐색의 "complete market-tape grafts" → "Large generalization failure" (정성). 양 좌석·새 seed. **host route·라이벌 신원·상대군·seed 수·판수·W/L 수치·실행 엔진 버전 N/A** (notebook 은 kaggle-environments ≥1.32.4 요구). 같은 계열 기제의 우리 근거: HYP-0027 `[LOCAL]` (EXP-005 X1, 1.32.7) | rayk notebook §16, `docs/code/raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb` markdown cell 48, SHA `a7447511…1331`, 수집 2026-09-16 (남의 실험, `[COMMUNITY]`) | 다음 중 하나가 성립하면 재검토: **(a)** `[ENGINE]` 고정 엔진이 1.32.7 에서 바뀌어 시장 주문 처리(slot 순서 경쟁 · 가격 갱신 · 흡수량 · shed/현금 제약에 따른 부분 체결) 코드가 달라짐. **(b)** `[HOSTED]` 이미 존재하는 replay 에서 graft 할 donor 의 exact market 주문열이 서로 다른 상대 · 다른 seed 의 **≥3 경기**에서, 주문이 있는 index 기준 **100% 일치** — 즉 그 market tape 가 경기에 반응하지 않음. 이 근거를 얻으려고 새 경기 · 제출을 하지 않는다 |
```

적용할 때 같은 커밋에서 할 일(§2.1 관행): 위 두 plan 파일의 K3 줄에 "범위 정정 — KILLS.md K3 참조" 한 줄을 단다. 계획서 본문은 역사 기록이므로 다시 쓰지 않는다.

**(b)가 무엇을 해결하고 무엇을 해결하지 않는가:** (b)는 "donor market이 경기마다 반응한다"는 실패 설명 하나를 배제할 뿐이다. host farm과 cash·shed의 결합(HYP-0027 기제)은 배제하지 못한다. 따라서 (b)가 성립해도 할 수 있는 것은 "K3 조건을 인용한 카드를 설계할 수 있음"까지다. 그 카드는 결합 위험을 자기 failure 조건에 넣어야 한다. 이것은 §9의 "실험해서 이기면 열자"와 다르다. 열리는 근거가 경기 결과가 아니라 기존 HOSTED 관측이기 때문이다.

### 4.2 참고: A와 C를 택할 경우의 After

- **A:** 1열 문구는 유지하고, 2열에 N/A 목록을, 5열에 위 (a)/(b)를 적는다. (b)의 "graft할 donor"는 "복사할 donor"로 바꾼다. EXP-007에 대해서는 "K3 범위이나 조건 인용 없이 제출됨(2026-09-12)"을 병기해야 한다.
- **C:** K3 행에 `~~K3~~ **HELD 날짜**`를 표시하고(K10 RETRACTED 형식), 5열에 "원출처 수치·범위 N/A — HYP로 이관"을 적는다. 이관할 HYP ID는 owner가 새로 배정해야 한다. 이번 작업에서는 배정하지 않는다.

## 5. "다른 상대에서 성공한 exact 복사본의 HOSTED 사례 1건" 조건 평가

**이것은 기존 계약이 아니다. 이번 제안자(Codex, `20260918-DONOR-MINIMUM-TRANSFER-CHECK.md` §2 "필요한 최소 증거 하나")가 새로 제안한 것이다.**

- AGENTS §9가 요구하는 것은 세 가지다. ① KILL 항목의 재검토 조건을 명시적으로 인용할 것. ② 그 조건이 성립했다는 근거가 `[ENGINE]` 또는 `[HOSTED]`일 것(`[LOCAL]` 단독 불가). ③ "이기면 열자"는 조건이 아니다. 어떤 **종류**의 HOSTED 사례여야 하는지는 정하지 않는다. `KILLS.md` 머리말도 "조건이 성립하면 다시 열 수 있다"뿐이다.
- 그 제안 자체가 이를 "owner가 좁은 재검토 조건을 논의할 최소 반례이지 자동 해제가 아니다"라고 적었다. 또 새 경기로 만드는 것을 금지했다. 그러니 순환은 아니다. 다만 현행 K3에는 조건이 `—`여서 그 사례가 있어도 인용할 조건이 없다. 이 점도 그 제안이 인정했다.

**문제점**
1. "성공"의 판정식이 없다(W/D/L 기준, 표본 수, 비교 대상 모두 N/A).
2. 선택 A에서 이 조건을 채울 수 있는 것은 우리 제출이나 공개 제출뿐이다. 우리 제출은 K3 때문에 만들 수 없다. 사실상 영구 금지로 되돌아가며, 이는 §9와 충돌한다.
3. 선택 B에서는 donor 전체 재생이 K3 밖이므로 이 조건이 필요 없다. market-only graft의 재검토는 §4.1 (a)/(b)로 대체된다. (b)는 새 실행 없이 기존 replay에서 관측할 수 있다.

**기존 자료 중 가장 가까운 HOSTED 사례 — 조건 충족 아님, 판정 N/A**
- EXP-007 `56175620`. exact tar `8031d51a…0180` → submission 연결은 ledger에 있다. 2026-09-12 01:13–11:14 UTC의 hosted 50판(좌석 21/29, 상대 48명): **21/9/20, point score 0.51**. publicScore 1819.8 → 1647.4 → 1635.9 (`evidence/HOSTED_LEDGER.md:160,192,229`; `experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json`, SHA `d27ebf70…e19c`).
- 이 사례는 다른 선수들의 전체 schedule을 exact 재생한 artifact가 hosted에서 새 상대들과 경기한 기록이다. 하지만 ① market-only graft가 아니다. ② 단일 고정 tape가 아니라 turn 144에 전환하는 router다. ③ 결과 json에 episode별 seed·engine 필드가 없다(N/A). ④ "성공"의 판정식이 없어 성공인지 실패인지 정할 수 없다. 따라서 **K3 해제 근거도, K3 좁은 범위의 반박도 아니다.** 다만 넓은 읽기 (ii)가 "큰 일반화 실패"를 예측한다면, 적어도 붕괴 수준의 hosted 결과는 아니었다는 참고 자료로만 남긴다 `[HOSTED]`, 해석은 `[INFERENCE]`.

**ENGINE 근거로 가능한 재검토 경로:** 있다. §4.1 (a)다. 엔진은 성능의 성공을 증명할 수 없지만, 실패 기제의 전제(시장 체결 규칙)가 바뀌었다는 것은 증명할 수 있다. `ENGINE_LOCK.md` 변경은 사람 결정 사항이므로 이 경로가 우회로가 되지 않는다.

## 6. 사람의 결정이 필요한 부분

1. **A / B / C 선택.** 추천은 B다. B를 택해도 donor 4셀안은 P2 HOLD·실행 artifact 없음·카드 없음 때문에 계속 실행 불가다.
2. **(b)의 수치 승인:** "≥3 경기, 서로 다른 상대·seed, 주문 있는 index 100% 일치". 이 값은 제안자의 초안이다.
3. **독립 검토자 지정.** AGENTS §4에 따라 제안자는 단독 승인할 수 없다. KILLS.md의 writer는 Claude이므로 적용은 검토와 승인 뒤 Claude가 한다.
4. **A를 택할 경우 EXP-007 소급 처리.** 활성 제출은 건드리지 않고 "조건 인용 없이 K3 범위 artifact 제출" 사실만 기록할지 결정한다.
5. **cell 28(전체 route 복사 미전이) 처리.** HYP-0010 주의사항으로 두면 충분한지, 아니면 별도 KILL로 만들지. 별도 KILL이라면 그 항목에도 엔진·상대·조건 칸이 필요하고, 원문 수치는 N/A다.

## 7. 원장 기록과 검증

- HYP-0010의 `다음 행동`에 이 proposal 경로와 "K3 범위 검토 중, 해제 아님"을 덧붙인다. rayk cell 28의 주의사항도 함께 적는다. 기존 `TEST-DONOR-ROUTES-20260917`은 context로만 재사용한다(Codex 09-18과 같은 방식). 새 HYP/TEST/EXP ID는 배정하지 않는다. 상태·결과 칸은 그대로 둔다.
- event 경로와 strict validation 결과는 이 파일 끝의 "실행 기록"에 적는다.

### 확인한 입력 SHA-256

| 파일 | SHA-256 |
|---|---|
| `evidence/KILLS.md` | `34f18435d713b4df0b6449c993b3cd4bd7b17e7135dfdd9a65628760d89660bf` |
| `AGENTS.md` (작업 트리, 미커밋 §0 변경 포함) | `f53bdcd455707f6aef33123f2c86c24e9e022befc1aed973d04fd51a955cae20` |
| `coordination/proposals/codex/20260918-DONOR-MINIMUM-TRANSFER-CHECK.md` | `e12431e644e57a249ae2bf20d9d1dec53fb4094caea008cb53f2f5cccaea8306` |
| `docs/code/raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb` | `a7447511510ed22b73f2315246b6bf4de66f219ffe3ba692a377f3fb47931331` |
| `releases/public-thomas-replay-router-v2-exact/main.py` | `8241246765098c50223d897739cb32076b71a303284d2e5e1c5f0fb495bb5a97` |
| `coordination/reports/codex/20260917-1640-DONOR-ROUTES.md` | `75a216f391f74dba93fd55fc1c6a583b365f6439a194eb6a438b1b53b209b24b` |
| `experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json` | `d27ebf70c758cae7f6cd106f97dfc4620d5fdd054e4fa261ac9f5826dd17e19c` |

원문 재현 (read-only):

```bash
python3 -c "import json;nb=json.load(open('docs/code/raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb'));[print(i,''.join(nb['cells'][i]['source'])) for i in (8,13,28,40,48,53)]"
```

## 실행 기록

- updater: `python3 tools/update_hypotheses.py --agent claude --hypothesis-id HYP-0010 --test-id TEST-DONOR-ROUTES-20260917 --set '다음 행동=…'` → event `coordination/hypotheses/claude/EVT-2026-09-18T111434.183583+0000-cc40f81f.json`, SHA `7e24e2da9be348a52d661d684c01a69ec684c8887d2ba150d45daba39a2faeef`. before/after 차이는 `다음 행동` 한 칸뿐이다. 상태 SOURCE_CLAIM과 Local/Hosted N/A는 그대로다.
- 이상 1건: 이 환경은 처음에 삭제 권한이 없었다. 그래서 updater가 event와 원장을 쓴 뒤 lock 해제(`unlink`) 단계에서 exit 3으로 끝났다. `HYPOTHESES.md`에 반영된 것은 확인했다. 남은 `coordination/hypotheses/.update.lock`(내용 `pid=7`)은 사람의 삭제 승인을 받아 이 파일 하나만 지웠다.
- `python3 tools/validate_hypotheses.py --strict` → **exit 0, "hypothesis ledger PASS: 32 entries"** (lock 제거 후 재실행).
- 커밋은 하지 않았다. 대상은 이 proposal과 위 event 1개다. `HYPOTHESES.md`에는 이번 세션 전부터 다른 사람의 미커밋 변경이 있다.


---

## `proposals/claude/20260919-F0-DIFFERENT-LINEAGE-RESUME-CLAUDE.md`

# 이어서 하기 — 다른 계보 3개 gate·진단 (Claude 새 세션용)

발행: Claude (Coordinator 역할), 2026-09-19. 수신: **Claude (같은 프로젝트 새 채팅)**.
원 지시서: `coordination/proposals/claude/20260919-F0-DIFFERENT-LINEAGE-WORK-ORDER-CODEX.md` (SHA `45977213…2bc`) — **이 문서는 그 지시서의 남은 부분만 다룬다. 원 지시서를 먼저 읽는다.**

## 0. 소유권 예외 (사람 지시)

`tools/`·`releases/`·`experiments/results/` 는 AGENTS §4 상 Codex 소유다. Codex 가 사용량 제한으로 중단돼 **사람이 Claude 에게 이어서 실행하도록 지시했다(2026-09-19).** 이 작업에 한해 Claude 가 아래 경로에 쓴다. 이미 있는 Codex 산출물(builder, 3개 release, `d1_vs_starter_seat0.json`)은 **수정하지 않는다.**

## 1. Codex 가 끝낸 것 (디스크에서 확인됨, 다시 하지 않는다)

| 항목 | 상태 | 근거 |
|---|---|---|
| builder `tools/build_public_exact.py` 에 d1·d2·d3 추가 | 완료 (미커밋) | `git diff --stat` +151/−11 |
| D1 release | 완료 | `releases/public-hesoponyo-pure-rl-agent-bc-ppo-self-play-exact/submission.tar.gz` SHA `6fe16a8c1820ab69f5b4e8758982d6cb1c2ed0d74f4532d7bee386ffcd4e3f7c`, `main.py` `f6e92e27…0b17` |
| D2 release | 완료, **`BLOCKED_SHA_MISMATCH` 로 기록 예정** — notebook 에 "더 이상 필요 없다"는 주석과 함께 남은 과거 기대값 `f029…d19` 와 원문 `main.py` `3b1c…8fe9` 불일치. 코드는 고치지 않고 측정은 계속한다(Codex 판단 유지) | `releases/public-salemali7-kaggriculture-2900-exact/submission.tar.gz` SHA `f1a8da39e253accff2915fae9f8d7d55d546071720803c0103e0865b0e78e262` |
| D3 release | 완료 | `releases/public-aasim2003-notebookb3a3ef21c3-exact/submission.tar.gz` SHA `e74d545c7725be665ca171ddc17d35facd73bd39f9af03dd37d2fc198cbfcf51` |
| 두 번 빌드 같은 SHA | Codex 보고상 3/3 | Codex 세션 출력 |
| D1 gate: D1 vs starter, seed 1000–1009, D1 좌석 0 | **완료 10/10**, 전부 720 steps DONE/DONE. **1경기 wall 약 155–158초**, D1 턴 p50 221ms · p99 232ms, 에피소드 누적 약 156초 | `experiments/results/f0_different_lineage_20260919/d1_vs_starter_seat0.json` |

`releases/public-hesoponyo-…/` 안의 `__pycache__/` 는 tar 멤버가 아니다(`tar -tzf` = `main.py` 하나). 지우지 않는다.

## 2. 남은 일

### 2-1. 실행 환경 먼저 (다르면 멈춤)

- **Mac 에서 직접 도는 셸**(Claude Code 등)이면 `.venv/bin/python` 을 쓴다.
- **Cowork 리눅스 VM** 이면 `.venv` 가 macOS 용이라 안 된다. `python3 -m pip install --user kaggle-environments==1.32.7` 후, `environment/ENGINE_LOCK.md` 의 `kaggriculture.py` SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` 와 `kaggriculture.json` SHA 가 **일치하는지 확인**. 불일치·설치 실패면 BLOCKED.
- 어느 쪽이든 결과 JSON 과 보고서에 `host`(macOS native / Linux VM, CPU 수)를 적는다. **VM 에서 잰 시간은 D1 좌석 0 의 Mac 수치와 같은 표에 섞지 않는다** — 따로 적는다.
- 셸 한 번의 시간 제한이 짧으면 `nohup … &` 로 돌리고 로그를 주기적으로 확인한다. **gate(시간 측정) 경기는 한 번에 하나씩** 돌린다(병렬이면 시간이 왜곡된다). 진단(승패만)은 병렬 가능.

### 2-2. gate — 남은 경기 (명령 형식은 `coordination/reports/codex/20260919-1221-F0-PUBLIC-EXACT.md` 와 동일)

`<D>` = 각 release 폴더의 `main.py`. 출력은 모두 `experiments/results/f0_different_lineage_20260919/`.

| 후보 | 남은 것 | 출력 파일 |
|---|---|---|
| D1 | `tools/instrument.py --a starter --b <D1> --seeds 1000 … 1009 --time-agent b --gate-agent b` | `starter_vs_d1_seat1.json` |
| D1 | `--a <D1> --b <D1> --seeds 1000 1001 --time-agent both --gate-agent both` | `d1_self.json` |
| D2·D3 | 위 세 가지 전부 (좌석 0 10경기, 좌석 1 10경기, self 2경기) | `d2_vs_starter_seat0.json` 등 같은 규칙 |

- 판정: 22경기 모두 720 steps · DONE/DONE · 예외 0 · ERROR 0, 에피소드 wall ≤ 960초, 후보 agent 누적 ≤ 623.2초/경기(기존 gate_summary 의 `runtime_limits` 그대로). silent-failure counter 는 기록만.
- **D1 시간 위험은 기록만 한다.** hosted 는 vCPU 1.6 이라 더 느릴 수 있다. 새 기준을 만들지 말고, 보고서에 "Mac p99 232ms, hosted 에서 N배 느리면 턴 1초 근접"처럼 사실만 적는다.
- clean-room: 각 tar 를 빈 폴더에 풀고 `import main` 성공, `callable(main.agent)`.

### 2-3. 진단 (판정 아님)

`tools/arena.py --a <D> --b <상대> --seeds 10 --seed-start 2000 --json <out>` — 쌍당 20경기(좌석 교대). 상대 2개:
- P2 제출본 `releases/public-lynnsakurai-farming-score-v2-exact/main.py`
- yhay81-exact `releases/public-yhay81-shop-router-0909-exact/main.py`
출력 `diag_<d>_vs_p2.json`, `diag_<d>_vs_yhay81.json`. **seed 추가 금지.** D1 은 경기당 약 2.6분이라 D1 진단 40경기 ≈ 1시간 45분 — 병렬 가능.

### 2-4. 정리·보고

- `gate_summary.json`, `diagnostic_summary.json` 를 기존 `f0_public_exact_20260919/` 형식에 맞춰 작성 (D1 좌석 0 기존 결과 포함, host 구분).
- 보고서 `coordination/reports/claude/YYYYMMDD-HHMM-F0-DIFFERENT-LINEAGE.md` 한 파일 — 원 지시서 §4 표 형식 + "Codex 중단 → Claude 이어서 실행" 사실과 이어받은 시점·파일 목록.
- 원장: `python3 tools/update_hypotheses.py --agent claude --hypothesis-id HYP-0028 --test-id TEST-DONOR-ROUTES-20260917 --reason "F0 different-lineage gate/diag (resumed from Codex)" --set "다음 행동=<기존 값> + 보고서 경로"` → `python3 tools/validate_hypotheses.py --strict` exit 0. (VM 이면 lock 해제에 삭제 권한이 필요할 수 있다.)
- **커밋하지 않는다.** Codex 의 미커밋 builder 변경과 섞이지 않게, 산출물 목록만 보고서에 적는다.

## 3. 금지

제출, 원문·builder·release 수정, 추가 다운로드, BOARD·KILLS·카드·`HYPOTHESES.md` 직접 편집, seed·기준 변경, `experiments/results/f0_latest_rebuild_20260919/`(취소된 작업의 잔여물) 수정. 모호하면 멈추고 BLOCKED + 해석 후보.


---

## `proposals/claude/20260919-F0-DIFFERENT-LINEAGE-WORK-ORDER-CODEX.md`

# 작업 지시서 — 다른 계보 공개 notebook 3개 exact 재현·gate (Codex)

발행: Claude (Coordinator 역할), 2026-09-19. 수신: **Codex**. 실행 위치: 사람 Mac.
근거: fast lane 대상 확대 승인(2026-09-19, "09-16 이후 공개 notebook 제출 코드의 무수정 재현"), 계보 분류 확인 `coordination/reports/claude/20260919-F0-LINEAGE-CHECK.md`.

## 한 화면 요약

1. **무엇:** P2 와 코드·tape 를 공유하지 않는 공개 notebook 3개를 무수정 재현하고 gate 를 돌린 뒤, P2 상대로 로컬 진단한다.
2. **왜:** 두 번째 슬롯 후보. 공개 제출 코드 37개 중 34개가 P2 가족이라, 다른 가족은 이 3개뿐이다.
3. **측정:** gate 22경기 + 진단. hosted 는 사람 제출 후.
4. **다음:** 보고 → Claude 가 두 번째 슬롯 제안 → 사람 결정.

## 1. 후보 (Antigravity 가 받아 둔 원문, 추가 다운로드 없음)

| # | notebook | 원문 SHA-256 | 형태 (Claude 원문 확인) |
|---|---|---|---|
| D1 | `docs/collection_snapshots/pure-rl-agent-bc-ppo-self-play/pure-rl-agent-bc-ppo-self-play.ipynb` (hesoponyo) | `d6afc8cd3ee39164432bc3e1dc198e25a4553099fc03c544b58dee3bfe33fea5` | BC+PPO Transformer, 가중치 내장, 순수 Python 추론. `kagg_native` 는 try/except 선택 import |
| D2 | `docs/collection_snapshots/kaggriculture-2900/kaggriculture-2900.ipynb` (salemali7) | `2acebbad45c10703e1587f6e57a964f571e2a9c2891d2ffdeea19ab03846b6cc` | 단일 tape(720행) 재생 + 잡초 수리·선행 판매·hands 정렬 |
| D3 | `docs/collection_snapshots/notebookb3a3ef21c3/notebookb3a3ef21c3.ipynb` (aasim2003) | `99e9c4f9bdc846d6a41fa6b4eb646878f1ff94184ee95a3c4f6f005efa665952` | 처음부터 쓴 규칙 기반(912줄) |

Antigravity 의 정적 추출물(`analysis/lineage_20260919/extracted/`)은 **참고용**이다. 빌드는 원문에서 Codex 가 직접 한다.

## 2. 할 일

1. `tools/build_public_exact.py` 에 `d1`·`d2`·`d3` 를 추가해 원문 그대로 재현. 결정론적 tar, 두 번 빌드 같은 SHA. notebook 에 기대 SHA 가 있으면 **일치해야 PASS**, 불일치면 `BLOCKED_SHA_MISMATCH`. 수정이 필요해 보이면 `BLOCKED_NEEDS_CHANGE`(고치지 않음).
2. 출력 `releases/public-<author>-<slug>-exact/` + `manifest.json`(라이선스 표기 포함).
3. gate: 지난 지시서(`20260919-F0-PUBLIC-EXACT-WORK-ORDER-CODEX.md`) §3 그대로 — 22경기, 예외·ERROR 0, 720 steps, runtime(에피소드 예산 70–80% 이내 — **D1 은 신경망 추론이라 턴 시간 p99·에피소드 누적을 반드시 기록**), clean-room import(외부 파일·네트워크 없음).
4. 진단(판정 아님, seed 2000–2009 좌석 교대, 쌍당 20경기): 각 후보 vs **P2 제출본**(`releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz`), 각 후보 vs **yhay81-exact**. seed 추가 금지.

## 3. 금지

제출, 원문 수정, 추가 다운로드, BOARD·KILLS·카드·`HYPOTHESES.md` 직접 편집, 결과를 보고 기준 변경. 모호하면 BLOCKED + 해석 후보.

## 4. 보고

`coordination/reports/codex/YYYYMMDD-HHMM-F0-DIFFERENT-LINEAGE.md` 한 파일. AGENTS §10.1 + 표:
`후보 | tar 경로 | tar SHA | 기대 SHA 일치 | gate | p99 ms / 에피소드 누적 s | vs P2 W/D/L | vs yhay81 W/D/L`
원장: `tools/update_hypotheses.py --agent codex --hypothesis-id HYP-0028 --test-id TEST-DONOR-ROUTES-20260917 --reason "F0 different-lineage exact builds" --set "다음 행동=<기존 값> + 보고서 경로"`, `validate_hypotheses.py --strict` exit 0.


---

## `proposals/claude/20260919-F0-LATEST-REBUILD-WORK-ORDER-CODEX.md`

# 작업 지시서 — P2·P3 최신판 exact 재빌드 (Codex)

> **보류 2026-09-19 (Claude, 발행 직후 원문 대조):** 이 지시서는 실행하지 않는다.
> - P2 최신판에서 복원한 `main.py`(SHA `99604be9…8364`, notebook 기대값 일치)는 제출한 P2 옛판(`cddf51ea…a94d`)과 **AST 가 완전히 같다.** 차이는 라이선스·출처 주석 222줄과 빈 줄 2개뿐이다. 다시 올리면 같은 bot 재제출(KILLS 방법론 "리롤")이다.
> - P3 최신판(`f6a756cf…62d2`, variant `mirror_aware_opening_pressure`)은 P3 옛판에 EXP284(0턴 밀 왕복 오프닝)·EXP293(판매 앞당기기) 두 층을 더한 것이다. 두 층 모두 P2 에 이미 있다. 코드 줄 유사도 P3옛~P3새 0.974, P2~P3새 0.924.
> - P1 alperen 포함 네 후보가 모두 같은 계보(Ahmed Berat Ozer EXP 체인, yhay81 shop-router 0908/0909 + thomas router 기반)다.

발행: Claude (Coordinator 역할), 2026-09-19. 수신: **Codex**. 실행 위치: 사람 Mac.
근거: [승인 기록](../../reports/claude/20260918-FASTLANE-AUTHORIZATION.md) 추가 승인 2026-09-19 — fast lane 대상 "09-16 이후 공개 notebook 제출 코드의 무수정 재현". 이전 결과: `coordination/reports/codex/20260919-1221-F0-PUBLIC-EXACT.md`.

## 한 화면 요약

1. **무엇:** 작성자가 09-18 이후 고친 P2(lynnsakurai)·P3(tetsutani) 최신 notebook 으로 제출 파일을 무수정 재빌드하고, 지난번과 같은 gate 를 돌린다.
2. **왜:** 제출한 P2(56347732)는 옛 수집본으로 만들었고 notebook 자체 기대 SHA 와 맞지 않았다. 최신판은 자체 SHA 검사가 들어 있다. 더 강하면 다음 제출이 되어 yhay81(1515)을 은퇴시킨다.
3. **측정:** 로컬 gate + 옛판 대비 진단 비교. hosted 는 사람 제출 후.
4. **다음:** 보고 → Claude 가 다음 제출 1개 제안 → 사람 제출.

## 1. 입력 (Antigravity 가 09-19 03:06 UTC 에 받아 둔 최신판 — 추가 다운로드 없음)

| # | notebook | SHA-256 | notebook 안의 기대 SHA |
|---|---|---|---|
| P2-new | `docs/collection_snapshots/farming-score-v2-a-better-approach/farming-score-v2-a-better-approach.ipynb` | `2fbebaf26ff26d47b606d7d80bf205331fd9374ac1ec549a8837fb32dba60d9e` | `EXPECTED_MAIN_SHA256 = 99604be9332db3e6cc2167e7425587c2a77a69825ca5ca116de9a48f37f08364` (code cell 5, 내장 `SOURCE_BYTES`) |
| P3-new | `docs/collection_snapshots/market-smart-farming-kaggriculture/market-smart-farming-kaggriculture.ipynb` | `17d587525c226205467ac00a9b61eb7631fa1a4c73d6ef44a2f76b9e3e879201` | `3f252be7…81ef`, `f6a756cf…62d2` (tar/main 중 무엇인지 Codex 가 원문으로 확인) |

같은 폴더의 `kernel-metadata.json` 도 manifest 에 기록한다.

## 2. 할 일

1. `tools/build_public_exact.py` 에 후보 `p2-new`, `p3-new` 를 추가한다. P2-new 는 `%%writefile` 이 아니라 내장 `SOURCE_BYTES` 방식이므로 **notebook 이 스스로 하는 방식 그대로** 복원한다. 기존 후보(P1–P3) 동작은 바꾸지 않는다.
2. **자체 검사 대조:** 복원한 `main.py`(또는 tar)의 SHA 가 notebook 기대값과 **일치해야 PASS.** 불일치면 그 후보는 `BLOCKED_SHA_MISMATCH` — 지난번처럼 "기록 후 진행"하지 않는다(이번 재빌드의 목적이 바로 이 일치다).
3. 결정론적 tar, 두 번 빌드 같은 SHA. 출력 `releases/public-lynnsakurai-farming-score-v2-latest-exact/`, `releases/public-tetsutani-market-smart-farming-latest-exact/` (+ `manifest.json`).
4. gate: 지난 지시서 §3 그대로 — starter seed 1000–1009 × 좌석 0·1 + self-play seed 1000·1001 = 22경기, 예외·ERROR 0, 720 steps, runtime, clean-room import. silent-failure counter 는 기록만.
5. 진단 비교(판정 아님, seed 2000–2009 좌석 교대, 쌍당 20경기): **P2-new vs P2-old(제출본 `1178ffa0…f388`)**, **P3-new vs P3-old**, **P2-new vs P3-new**. seed 추가 금지.

## 3. 금지

제출, 코드 수정(원문 무변경 원칙), 추가 다운로드, BOARD·KILLS·카드·`HYPOTHESES.md` 직접 편집, 결과를 보고 기준 변경. 모호하면 BLOCKED + 해석 후보.

## 4. 보고

`coordination/reports/codex/YYYYMMDD-HHMM-F0-LATEST-REBUILD.md` 한 파일. AGENTS §10.1 + 표:
`후보 | tar 경로 | tar SHA | main SHA | notebook 기대값 일치 | gate 결과 | 진단 비교 W/D/L`
원장: `tools/update_hypotheses.py --agent codex --hypothesis-id HYP-0028 --test-id TEST-DONOR-ROUTES-20260917 --reason "F0 latest rebuild" --set "다음 행동=<기존 값> + 보고서 경로"`, `validate_hypotheses.py --strict` exit 0. 커밋은 산출물만.


---

## `proposals/claude/20260919-F0-LINEAGE-SORT-ANTIGRAVITY.md`

# 작업 지시서 — 공개 notebook 계보 분류 (Antigravity) — r2

**r2 2026-09-19 (Claude 검토, 기존 제출 artifact 로 규칙을 시험한 뒤 수정):**
1. r1 은 줄바꿈을 정규화하지 않았다. tetsutani·alperen 의 `main.py` 는 CRLF 라서 그대로 비교하면 P2 와의 유사도가 0.009/0.044 로 나와 `OTHER` 로 잘못 분류된다(정규화하면 둘 다 0.900).
2. r1 은 "같은 tape 를 쓰는가"를 보지 않았다. yhay81-exact 의 tape 13개가 **전부** P2 의 route 안에 같은 행동으로 들어 있다(turn 1–718 일치 13/13). 코드가 달라도 같은 tape 를 재생하면 경기에서 같은 행동을 하므로, 슬롯 다양성 목적으로는 같은 가족이다. r1 은 이런 notebook 을 `YHAY81_OTHER` 로 non-Ozer 목록에 넣었다.
3. r1 은 tar 안 `main.py` 만 꺼냈다. tape 가 `actions.json` 같은 다른 멤버에 있으면(yhay81 형식) 놓친다.

발행: Claude (Coordinator 역할), 2026-09-19. 수신: **Antigravity** (단순 자료 수집·정리). 실행 위치: 사람 Mac.

## 한 화면 요약

1. **무엇:** 09-16 이후 공개 notebook 48개(제출 코드 있음 41개)의 제출 파일을 **실행하지 않고** 꺼내, 우리가 제출한 P2 와 코드 또는 tape 를 공유하는지 기계적으로 분류한다.
2. **왜:** P2·P3·alperen 이 모두 한 계보(Ahmed Berat Ozer EXP 체인, yhay81 shop-router 0908/0909 + thomas router 기반)였다. 최종 두 슬롯이 같은 가족이면 같은 상대에게 같이 진다(AGENTS §7.4). 다른 계보 후보를 찾는다.
3. **측정:** 문자열·유사도 계산만. 경기·빌드 없음.
4. **다음:** 보고 → Claude 가 후보 선별 → Codex 재현·gate.

## 입력

- 목록: `analysis/public_exact_20260919/new_notebooks.json` (SHA `970c3438a1f324bc25074c449599005bb0a72eb770d8f3852274b5387a4df954`), 필드 `submission_code_generated == true` 인 41개. 나머지 7개는 `no_submission_code` 로만 기록.
- 원문: `docs/collection_snapshots/<slug>/<slug>.ipynb` (이미 받아 둠). **추가 다운로드 없음.**
- 기준 파일(P2 제출본): `releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz` 안의 `main.py` (SHA `cddf51ea…a94d`).

## 1. 파일 꺼내기 — 정적 추출만

- **notebook 코드를 실행하지 않는다**(외부 코드 실행 위험). 코드 셀의 **문자열·bytes 리터럴만** 읽는다.
- 인정하는 패턴 (이 밖은 `extraction_unsupported` + 패턴 한 줄 설명):
  1. `%%writefile <파일>` 셀 → 첫 줄 뒤 본문 그대로 (파일 이름별로 모두)
  2. `SOURCE_BYTES = b''.join((...))` 같은 bytes 리터럴 연결
  3. base64 / base85 문자열 → (zlib·gzip 해제) → tar 이면 **모든 멤버**
  4. 외부 `/kaggle/input` 에서 복사 → `external_dataset` 로 기록하고 추출하지 않음
- notebook 에 기대 SHA 가 적혀 있으면 추출물과 대조해 `expected_sha_match: true/false/none` 기록.
- 추출물은 `extracted/<slug>/<원래 파일 이름>` 으로 저장한다.

## 2. 계보 신호 — 숫자만 기록

**정규화 (모든 비교에 공통):** bytes 를 UTF-8 로 읽고 `\r\n`·`\r` 을 `\n` 으로 바꾼 뒤, 각 줄 끝 공백을 지운다. 코드 줄 = 빈 줄과 `#` 로 시작하는 줄을 뺀 나머지.

후보마다:
- `hdr_ozer`: `main.py` 앞 80줄에 `Ahmed Berat Ozer` 또는 `EXP260 combined` 존재 (true/false)
- `mentions`: 모든 .py 에서 `yhay81`, `thomastschinkel`, `aurax7`, `tetsutani`, `Ozer` 각각 등장 횟수
- `sim_p2`: 모든 .py 를 이름순으로 이어 붙인 코드 줄 목록 vs 기준 P2 `main.py` 코드 줄 목록, `difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()`. 한쪽이 6,000줄을 넘으면 `quick_ratio()` 로 대신하고 `sim_method` 에 표시
- `tapes_found`: 추출물 안에서 찾은 tape 수. **tape** = 길이 719 인 리스트이고 모든 원소가 `farmer`·`hands`·`market` 키를 가진 dict. 찾는 곳: .json 멤버, .py 안의 JSON/리스트 리터럴, base64·base85(+zlib/gzip) 로 풀리는 문자열. `{"actions":[...], "routes":{id:[index...]}}` 처럼 **index 로 조립하는 형식**도 조립해서 센다.
- `tapes_shared_with_p2`: 찾은 tape 중 기준 tape 집합과 같은 것의 수. 비교 키 = `sha256(json.dumps(tape[1:], sort_keys=True))` (0턴은 오프닝 덮어쓰기가 있어 뺀다)
- `imports_nonstd`, `main_sha256`, `main_lines`, `members`

**기준 tape 집합 만들기:** P2 제출본 `main.py` 의 `_R108_DATA=json.loads(zlib.decompress(base64.b85decode('...')))` 리터럴(파일 안에 여러 번 나오면 전부)을 풀어 `routes` 의 각 index 목록을 `actions` 로 조립 → 위 키로 해시 → 중복 제거. **38개**, 정렬한 해시를 줄바꿈으로 이은 문자열의 SHA-256 = `20f4edeedefab30f30935e96c234d140d9b6ae82339021c635f7fc3fd7466da5`. 다르면 BLOCKED.

## 3. 분류 규칙 (고정 — 결과를 보고 바꾸지 않는다)

위에서부터 처음 맞는 것:

| 분류 | 조건 | 뜻 |
|---|---|---|
| `UNKNOWN` | 추출 실패 / external_dataset | 판단 불가 |
| `SAME_FAMILY` | `hdr_ozer` 또는 `sim_p2 ≥ 0.70` 또는 `tapes_shared_with_p2 ≥ 1` | 같은 가족 (코드 또는 행동) |
| `AMBIGUOUS` | `0.30 ≤ sim_p2 < 0.70` | 코드 일부 공유 가능 — 사람이 볼 대상 |
| `RELATED` | `mentions` 중 `yhay81`·`thomastschinkel`·`aurax7` 합 ≥ 1 | 조상을 공유할 수 있음, tape 는 다름 |
| `DIFFERENT` | 나머지 | 다른 계보 후보 |

## 3-1. 통제 사례 (규칙 구현 확인용 — 이 결과가 안 나오면 BLOCKED)

48개 분류 전에 우리 artifact 로 먼저 돌린다.

| 입력 | 기대 |
|---|---|
| `releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz` | SAME_FAMILY, sim_p2 = 1.000 |
| `releases/public-tetsutani-market-smart-farming-exact/submission.tar.gz` (CRLF) | SAME_FAMILY, sim_p2 ≈ 0.900, tapes_shared 38 |
| `releases/public-alperen-before-dawn-stock-cash-sales-exact/submission.tar.gz` | SAME_FAMILY, sim_p2 ≈ 0.900, tapes_shared 38 |
| `releases/public-yhay81-shop-router-0909-exact/submission.tar.gz` | SAME_FAMILY, sim_p2 < 0.01, **tapes_found 13, tapes_shared 13** |
| `opponents/public/boatlee.py`, `kaitofukami.py`, `raykkretzschmar.py` | sim_p2 < 0.05 (분류 기대값 없음, 기록만) |

## 4. 부수 수정

`new_notebooks.json` 의 `score_claim` 필드가 notebook JSON 원문 앞부분으로 잘못 채워져 있다. 이번 출력에서는 **markdown 셀**에서 `\b[1-3]\d{3}(\.\d)?\b` 를 포함한 첫 문장을 그대로 한 줄 넣는다(없으면 N/A). 기존 파일은 덮어쓰지 않는다.

## 출력

- 스크립트 `analysis/lineage/classify_lineage.py`, 결과 `analysis/lineage_20260919/`
  - `lineage.json` — 48개 전부, 위 필드 + ref·title·votes·last_run·score_claim·분류
  - `controls.json` — §3-1 결과
  - `different.json` — `DIFFERENT` 만, `sim_p2` 오름차순 / `related_ambiguous.json` — `RELATED`·`AMBIGUOUS`
  - `extracted/<slug>/...` — 추출물 (실행 금지)
  - `file_hashes.json`
- 금지: notebook·추출 코드 실행, 추가 다운로드, `docs/code/`·`docs/collection_snapshots/` 수정, `tools/`·`releases/`·BOARD·KILLS·`HYPOTHESES.md` 편집, 순위 매기기·추천. 애매하면 BLOCKED + 해석 후보.

## 보고

`coordination/reports/antigravity/YYYYMMDD-HHMM-F0-LINEAGE.md` 한 파일. AGENTS §10.1 + `VERDICT | 핵심 사실 2개 | 결과 파일 SHA | 검증 | NEXT`.
핵심 사실: §3-1 통제 사례 통과 여부, 분류별 개수(UNKNOWN / SAME_FAMILY / AMBIGUOUS / RELATED / DIFFERENT), `different.json` 전부의 ref·sim_p2·tapes_found·score_claim.
검증: 무작위 3개를 두 번째 방법(예: 셀을 다시 읽는 별도 함수)으로 재추출해 `main_sha256` 일치 확인. 가설 원장은 기록하지 않는다.


---

## `proposals/claude/20260919-F0-PUBLIC-EXACT-WORK-ORDER-CODEX.md`

# 작업 지시서 — 공개 notebook exact 재현·gate (Codex)

발행: Claude (Coordinator 역할), 2026-09-19. 수신: **Codex** (판단·구현). 실행 위치: 사람 Mac.
근거: [승인 기록](../../reports/claude/20260918-FASTLANE-AUTHORIZATION.md) "추가 사용자 승인 2026-09-19", [결정안](20260919-F0-STAGE-B-RESULT-DECISION.md) §3 A, [fast lane 계획](20260918-DONOR-TAPE-FASTLANE-PLAN.md) §3-2 gate.

## 한 화면 요약

1. **무엇을 하는가:** 09-16 이후 공개된 notebook 3개의 제출 코드를 **한 글자도 바꾸지 않고** tar 로 재현하고, fast lane gate(§3-2)를 통과시킨다.
2. **왜:** 상위 donor 는 고정 tape 가 아니어서(0/52) 재생 경로가 막혔다. 최신 공개 bot 을 그대로 올려 hosted 로 강도를 잰다. 우리 활성 두 개는 1515.3 / 1475.1 이다.
3. **측정:** 로컬 gate 와 진단 round-robin 뿐. hosted 판정은 사람 제출 후.
4. **다음:** 보고 → Claude 가 제출 순서 제안 → 사람 제출.

## 1. 후보 (수집본은 `docs/code/`, 추가 다운로드 없음)

| # | notebook | 수집본 SHA-256 | 코드 위치 (Claude 사전 확인) |
|---|---|---|---|
| P1 | `alperen5252525_kaggriculture-before-dawn-stock-cash-sales.ipynb` (last_run 09-18) | `d49b0540fe7ff082c4f5947563b0e433c62161cdf284638c08db103372f657de` | code cell 1: 내장 payload(약 184 KB) → tar 생성 |
| P2 | `lynnsakurai_farming-score-v2-a-better-approach.ipynb` (09-18) | `f419b98e395cf1ab970bc8355257ac2c98a27f982739647886c881d69942ac12` | code cell 5 `%%writefile main.py`(약 349 KB), cell 9 tar |
| P3 | `tetsutani_market-smart-farming-kaggriculture.ipynb` (09-16) | `ac5bfab445488fe88589a06460a7509a7fb5aff1273c8b679bbcd04b5d6fd0d3` | code cell 9: base64 payload → tar, cell 25 tar 확인 |
| (P4) | `mzcao7_kaggriculture-2476-8-peak-lightgbm-xgboost.ipynb` | `74bd0e7d328dc96635427b58a8828beb05a639f158a77a24009047f8f69f033b` | cell 1 이 `/kaggle/input` 의 외부 dataset 파일 8개를 복사 → **수집본만으로 재현 불가. 이번 대상 아님.** Antigravity 가 dataset 출처를 확인한 뒤 별도 결정 |

위 "코드 위치"는 Claude 의 읽기 확인일 뿐이다. 실제 추출은 Codex 가 notebook 원문에서 직접 한다.

## 2. 재현 규칙

- **exact:** notebook 이 만드는 파일들을 notebook 원문 그대로 추출한다. 들여쓰기·주석·상수 포함 무변경. notebook 이 tar 를 만드는 방식(멤버·경로)을 따른다. 결정론적 tar(mtime/uid/gid/순서 고정)로 **두 번 빌드해 같은 SHA**.
- notebook 이 기대 SHA 를 적어 두었으면 그 값과 대조하고, 다르면 기록한다(제외하지 않음 — 원문 표기 오류일 수 있다).
- 출력: `releases/public-<author>-<slug>-exact/` 에 `submission.tar.gz`, `manifest.json`(원문 경로·SHA·cell id·추출 방법·멤버 SHA·라이선스 파일 유무), 재현 스크립트 `tools/build_public_exact.py`(후보 3개 공통, 기존 `tools/build_public_reference.py`·`build_thomas_reference.py` 패턴 재사용 가능).
- **수정이 필요해 보이면**(import 실패, `__file__` 의존, 네트워크 호출 등) 고치지 말고 그 후보를 `BLOCKED_NEEDS_CHANGE` 로 기록한다. 수정본은 fast lane 의 1-change 변형이므로 exact hosted 결과 뒤 별도 결정이다.

## 3. gate (§3-2, 후보마다)

| 줄 | 기준 |
|---|---|
| Identity | 두 번 빌드 같은 SHA, manifest 완비 |
| Schema | root `main.py`, `agent(obs)` 호출 가능. 로컬 **20경기**(starter, seed 1000–1009 × 좌석 0·1) + self-play 2경기(seed 1000, 1001): 예외 0, 상태 ERROR/INVALID 0, 720 steps |
| Runtime | 같은 22경기에서 에피소드 wall 과 agent 누적 시간이 예산(AGENTS §6) 70–80% 이내, p99 턴 지연 기록 |
| Isolation | 빈 폴더에서 tar 풀고 `import main` 성공, 외부 파일·네트워크 접근 0 |
| License | 원문·tar 안의 라이선스 표기 기록. 없으면 "Kaggle 공개 notebook 기본" 이라고만 적고 판단은 Claude 에 넘긴다 |
| Ledger | 제출 후(사람) |

- 엔진: `kaggle-environments==1.32.7`, SHA 는 `environment/ENGINE_LOCK.md` 와 대조.
- silent-failure counter(`tools/instrument.py`)는 **기록만** 한다. gate 판정에 쓰지 않는다.

## 4. 진단 round-robin (판정 아님 — 제출 순서 참고용)

- 참가: gate PASS 후보 전부 + `releases/public-yhay81-shop-router-0909-exact/submission.tar.gz`(현재 활성 기준선).
- 모든 쌍, seed **2000–2009**, 좌석 교대(쌍당 20경기). W/D/L 과 쌍별 점수만 기록.
- 이 수치로 제출을 막거나 허락하지 않는다(§7.1 — 로컬·hosted 상관 미확인). 결과를 보고 seed 를 늘리지 않는다.

## 5. 금지

제출, 공개 코드 수정, 외부 dataset·replay 다운로드, BOARD·KILLS·카드·`HYPOTHESES.md` 직접 편집, 결과를 보고 gate 기준 변경.

## 6. 보고

`coordination/reports/codex/YYYYMMDD-HHMM-F0-PUBLIC-EXACT.md` 한 파일. AGENTS §10.1 + 후보별 표:
`후보 | tar 경로 | tar SHA | gate 6줄 결과 | 22경기 예외/ERROR | p99 ms | 진단 round-robin 점수 | 비고`
가설 원장: `tools/update_hypotheses.py --agent codex --hypothesis-id HYP-0028 --test-id TEST-DONOR-ROUTES-20260917 --reason "F0 public exact builds" --set "다음 행동=<기존 값> + 보고서 경로"` (HYP-0028 = 공개 notebook 과 실제 artifact 구분 가설. 상태·결과 칸 불변). `python3 tools/validate_hypotheses.py --strict` exit 0.


---

## `proposals/claude/20260919-F0-PUBLIC-SOURCE-CHECK-ANTIGRAVITY.md`

# 작업 지시서 — 공개 notebook 원문 재확인·목록 (Antigravity)

발행: Claude (Coordinator 역할), 2026-09-19. 수신: **Antigravity** (단순 자료 수집). 실행 위치: 사람 Mac.
근거: [승인 기록](../../reports/claude/20260918-FASTLANE-AUTHORIZATION.md) 추가 승인 2026-09-19. 코드 수정·빌드·제출은 Codex·사람 몫이다.

## 할 일

**1. 후보 4개 원문이 바뀌었는지 확인**
- 대상: `alperen5252525/kaggriculture-before-dawn-stock-cash-sales`, `lynnsakurai/farming-score-v2-a-better-approach`, `tetsutani/market-smart-farming-kaggriculture`, `mzcao7/kaggriculture-2476-8-peak-lightgbm-xgboost`.
- `kaggle kernels pull <ref>` 로 현재 버전을 **`docs/collection_snapshots/` 아래 새 폴더**에 받는다(`docs/code/` 의 기존 수집본은 덮어쓰지 않는다).
- 새 SHA-256 과 `docs/code/` 수집본 SHA 비교: alperen `d49b0540…57de`, lynnsakurai `f419b98e…ac12`, tetsutani `ac5bfab4…d0d3`, mzcao7 `74bd0e7d…033b`. 다르면 `CHANGED` 로 표시만 한다(어느 쪽을 쓸지는 Claude·사람 결정).
- `kaggle kernels metadata` 로 버전 번호, 마지막 실행 시각, `dataset_sources`, 라이선스 표기를 기록한다.

**2. mzcao7 외부 dataset 출처만 확인 (다운로드 금지)**
- notebook metadata 의 `dataset_sources` 에서 dataset ref, 소유자, 크기, 라이선스, 마지막 갱신 시각. `kaggle datasets files <ref>` 로 파일 목록만. 받지 않는다.

**3. 09-16 이후 공개 notebook 목록**
- 대회 `kaggriculture` 의 공개 notebook 중 `last_run_time` ≥ 2026-09-16T00:00Z. 항목: ref, 제목, 투표 수, last_run, 제출 코드 생성 여부(`%%writefile main.py` 또는 tar 생성 cell 유무), 외부 dataset 의존 여부, 본문에 적힌 점수 주장(문장 그대로 한 줄, 없으면 N/A).
- 목록에 넣기만 한다. 순위 매기기·추천은 하지 않는다.

## 출력·금지

- 스크립트 `analysis/public_exact/check_sources.py`, 결과 `analysis/public_exact_20260919/`(`candidates.json`, `mzcao7_dataset.json`, `new_notebooks.json`, `file_hashes.json`).
- 금지: dataset·replay 다운로드, `docs/code/` 덮어쓰기, `tools/`·`releases/`·BOARD·KILLS·`HYPOTHESES.md` 편집, 코드 빌드·경기 실행, 목록 해석.
- 애매하면 멈추고 BLOCKED 로 보고(막힌 항목 + 가능한 해석 후보).

## 보고

`coordination/reports/antigravity/YYYYMMDD-HHMM-F0-PUBLIC-SOURCE-CHECK.md` 한 파일. AGENTS §10.1 + `VERDICT | 핵심 사실 2개 | 결과 파일 SHA | 검증 | NEXT`. 핵심 사실: "후보 4개 중 CHANGED 수", "09-16 이후 제출 코드가 있는 notebook 수". 가설 원장은 이번에 기록하지 않는다.


---

## `proposals/claude/20260919-F0-STAGE-B-RESULT-DECISION.md`

# F0 단계 B 결과와 다음 결정 — 고정 tape donor 없음

작성: Claude (Coordinator 역할), 2026-09-19. **상태: PROPOSAL.** 계획 §1-2 기준을 바꾸는 선택이므로 승인 문장(§4)에 따라 사람에게 돌아온다. Coordinator 작성본이며 독립 검토 아님.

1. **무엇을 시험했는가:** 상위 1–60위 적격 52팀의 최신 2경기 행동이 똑같은지(고정 tape 인지).
2. **왜:** 똑같은 팀이어야 기록 재생 bot 이 그 팀과 같은 행동을 한다.
3. **결과:** `[HOSTED]` replay 원자료 기준 **52팀 전부 불일치 (full_match 0, field_match 0)**. Claude 가 raw 87개에서 독립 재계산해 Antigravity 결과와 일치 확인.
4. **다음:** 계획 그대로의 단계 C(6/6 확인)는 대상이 없어 종료. 새 경로를 사람이 고른다(§3).

## 1. 수치 (raw 에서 재계산)

| 항목 | 값 |
|---|---|
| 2경기 완전 일치 | **0 / 52** |
| 같은 turn 행동 비율 | 중앙값 **28.5%**, 최대 577/719 (80%) |
| 처음 달라지는 turn | ≤32: **17팀** · 72–104: 8팀 · **144–218: 26팀** · >218: 1팀 |
| 상위 10팀 처음 불일치 | 3위 25 · 4위 72 · 5위 76 · 6위 25 · 7위 9 · 8위 150 · 9위 25 · 10위 144 · 11위 149 · 12위 1 |
| 90% 차선 기준(field 일치 + market ≥90%) | **충족 0팀** — field_match 가 0 이므로 성립 불가 |

재현: `analysis/donor_tape_20260919/stage_bc/stage_b_pairs.json` (Antigravity), 원자료 `private_artifacts/donor_tape_20260919/raw/` 87개. Antigravity 보고 `coordination/reports/antigravity/20260919-1128-F0-STAGE-BC.md`, 산출 해시 파일 SHA `5740ac3f…6e42`.

## 2. 해석

- **현재 상위권은 고정 tape 가 아니다.** 절반은 day 6 전후(turn 144–150)에서 갈라진다 — 공통 오프닝 뒤 상태를 보고 경로를 고르는 router 구조와 맞는다(thomas router 는 72턴 block 마다 tree 로 schedule 을 고른다, 144 = 두 번째 block 경계). 나머지 1/3 은 처음 32턴 안에 갈라진다 — 처음부터 상태에 반응한다 `[INFERENCE]`.
- 그래서 **계획 §3-1 의 "단일 tape exact 재생"은 상위 60위에서 donor 를 만들 수 없다.** 60위 밖으로 넓혀도 고정 tape 팀은 대개 공개 tape 를 그대로 쓰는 팀일 가능성이 높고, 그러면 우위가 없다 `[INFERENCE]`.
- 함께 본 hosted: yhay81-exact 재제출이 14시간 뒤 **1515.3** (같은 bytes 가 09-10 에 2188.4). 오래된 공개 tape 는 현재 필드에서 크게 약해졌다 `[INFERENCE]`.

## 3. 선택지

| | 내용 | 비용 | 성공 시 | 위험 |
|---|---|---|---|---|
| **A. 공개 최신 artifact exact (추천)** | 09-16 이후 공개 notebook 중 제출용 코드가 있는 것을 exact 재현 → §3-2 gate → hosted. 1차 후보: `alperen5252525/…before-dawn-stock-cash-sales`(09-18), `lynnsakurai/farming-score-v2`(09-18, writefile 있음), `tetsutani/market-smart-farming`(09-16, route library), `mzcao7/…2476-8-peak`(09-18) | 빌드·gate 후보당 반나절. 다운로드 없음(`docs/code/` 수집본 사용) | 하루 안에 hosted 점수 확인. 최신 반응형이라 필드 변화에 덜 약함 | 성능 주장은 전부 `[COMMUNITY]`. 공개본이라 같은 bot 끼리 붙는 경기가 많다 |
| B. router 복원 탐사 | 처음 불일치가 ≥144 인 상위 팀 최대 15팀의 나머지 4경기 수집(≤60, 승인 한도 180 안) → turn 144 이후 구간이 소수의 반복 tape 로 나뉘는지 확인 | 수집 반나절 + Codex 판정. 그 뒤 routing 규칙 추정·구현은 별도 | 상위권 route library 확보 | routing 규칙을 모르면 bot 이 안 된다. 09-27 까지 완성 가능성 낮음 |
| C. F0 종료 | 현재 두 슬롯 유지 | 0 | — | 동메달 경로 없음 |

**추천: A 를 주 경로로.** B 는 A 의 첫 hosted 결과가 2200 에 못 미칠 때만 다시 올린다.

A 는 계획 §3-1 대상(donor tape 재생)이 아니므로 fast lane 범위를 넓히는 승인이 필요하다. 역할: 재현 빌드·gate = Codex(`tools/`·`releases/` 소유), 공개 notebook 목록·원문 SHA 확인 = Antigravity, 후보 순서 = Claude.

## 4. 승인 문장 (사람이 고른다)

> 승인: `20260919-F0-STAGE-B-RESULT-DECISION.md` §3 A 를 채택한다. fast lane(§3-2 gate, 09-29 까지)의 대상을 "09-16 이후 공개된 Kaggriculture notebook 의 제출 코드를 수정 없이 재현한 artifact"로 넓힌다. 후보는 §3 A 표의 4개에서 시작하고, Codex 가 재현·gate 를 하며, 각 hosted 제출은 내가 직접 실행한다. 단계 C(6/6)는 대상 없음으로 종료한다.

포함하지 않는 것: B(추가 replay 수집), 공개 notebook 의 수정본(개선은 exact hosted 확인 뒤 별도 1-change), 09-16 이전 공개본.


---

## `proposals/claude/20260919-F0-STAGE-BC-WORK-ORDER-ANTIGRAVITY.md`

# 작업 지시서 — F0 단계 B + 단계 C 다운로드: replay 수집·행동 추출 (Antigravity)

발행: Claude (Coordinator 역할), 2026-09-19. 수신: **Antigravity** (단순 자료 수집). 실행 위치: **사람 Mac 터미널**.
근거: [승인 기록](../../reports/claude/20260918-FASTLANE-AUTHORIZATION.md) (3) 단계 A–D, replay 최대 180개. [계획](20260918-DONOR-TAPE-FASTLANE-PLAN.md) §1-2 · §4.
입력(동결): `analysis/donor_tape_20260919/selection_stageB.json` SHA `9195f9d3cb21c81d3650fc44978f0f6aa4cd72a0e89a1ba57a62122b401f8d4b`, `inventory.json` SHA `d405cc1026c114b231506a03e09a823ff872686308282699723485077b415781`.

## 한 화면 요약

1. **무엇을 하는가:** 단계 A가 고른 52팀의 최신 2경기 replay(고유 **87개**)를 받아, 각 팀 donor 좌석의 719개 행동을 뽑고 두 경기가 똑같은지 본다. 두 경기가 똑같은 팀만, 6경기 창의 나머지 4경기도 받아 행동을 뽑는다.
2. **왜 하는가:** "여러 경기에서 행동이 완전히 같은 팀" = 재생이 통할 후보를 찾기 위해서다. 최종 6/6 판정과 donor 선정은 이 자료로 **Codex**가 한다.
3. **측정:** N/A — 수집·추출·일치 여부 계산만 한다. 성능 판정·경기 실행 없음.
4. **다음:** 완료 보고 → Codex 단계 C 판정.

## 1. 허용 / 금지

| 허용 | 금지 |
|---|---|
| `competition_episode_replay` 로 §2·§3 목록의 replay 만 다운로드. 합계 **≤147개** (B 87 + C ≤60) | 목록 밖 replay, 61위 이하 reserve 추가(1–60위 적격이 52팀이라 보충 조건 미성립) |
| raw 저장: `private_artifacts/donor_tape_20260919/raw/episode-<id>-replay.json` (gitignore 경로) | raw 삭제(사람 승인 필요), 경기 실행·엔진 재현, candidate·제출 |
| 코드 `analysis/donor_tape/extract_stage_bc.py`, 결과 `analysis/donor_tape_20260919/stage_bc/` | `tools/`·`experiments/`·BOARD·KILLS·카드·`HYPOTHESES.md` 직접 편집 |
| 429 에는 대기 후 재시도(기존 단계 A 방식) | 결과를 보고 규칙·목록 변경. 애매하면 BLOCKED |

## 2. 단계 B — 87개

1. `selection_stageB.json` 의 모든 (team, episode) 쌍을 펼치고 episode ID 로 중복 제거 → 다운로드 목록. 고유 수가 87 이 아니면 BLOCKED.
2. 각 replay 검증: `info.EpisodeId` = 요청 ID. 파일 SHA-256, bytes, `module_version`, `configuration`, `rewards` 기록. `module_version` 이 `1.32.7` 이 아니면 표시만 한다(제외하지 않음).
3. **donor 좌석** = selection 의 그 episode `agents` 에서 `submissionId == target_submission` 인 agent 의 `index` (없으면 0). 추가 확인: `info.TeamNames[seat]` == 그 agent 의 `teamName`, replay `rewards[seat]` == metadata `reward`. 하나라도 다르면 그 쌍은 `identity_mismatch` 로 기록하고 일치 판정에서 뺀다.
4. **행동 추출:** `actions = [replay['steps'][t][seat]['action'] for t in range(1, 720)]` — 719개. 길이가 719 가 아니면 `length_mismatch`.
5. 해시 3종 (모두 `json.dumps(x, sort_keys=True, separators=(',',':')).encode()` 의 SHA-256):
   - `full_sha` = actions 전체
   - `field_sha` = 각 행동의 `{farmer, hands}` 만
   - `market_sha` = 각 행동의 `market` 만
6. 팀별 2경기 비교 (`stage_b_pairs.json`):
   - `full_match` (full_sha 같음), `field_match`
   - `market_nonempty_agree` = 두 경기 중 하나라도 market 이 비어 있지 않은 index 에서 market 이 같은 비율 (분모 0 이면 N/A)
   - `first_diff_index` (full 기준 처음 다른 turn, 같으면 null)

## 3. 단계 C 다운로드 — ≤60개

1. **대상 팀:** `full_match == true` 이고 identity·length 문제 없는 팀을 **leaderboard 순위 순**으로 최대 **15팀**. 16팀 이상이면 상위 15팀만, 나머지는 `overflow` 로 기록.
2. full_match 팀이 **0팀**이면 단계 C 다운로드를 하지 않고 보고한다(90% 차선 기준 적용 여부는 Codex·사람 판단).
3. 각 대상 팀의 6경기 창(`inventory.json`)에서 단계 B 에 쓰지 않은 **나머지 4경기**를 받는다(이미 받은 episode 는 재사용). §2-2~5 와 같은 검증·추출.
4. `stage_c_windows.json`: 팀별 6경기의 full/field/market SHA, 6경기 중 full_sha 가 최빈값과 같은 수(`k_of_6`), 상대 teamId 목록, donor 좌석 목록.
   - **6/6 판정은 하지 않는다.** 숫자만 기록한다.

## 4. 산출물

| 파일 | 내용 |
|---|---|
| `download_log.json` | episode 별 요청 시각·결과·재시도 횟수·SHA·bytes |
| `actions/<teamId>-<episodeId>.json` | 추출한 719 행동 + seat + 3종 SHA |
| `stage_b_pairs.json` | §2-6 |
| `stage_c_selection.json` | §3-1 대상 팀·overflow, 받을 episode 목록 (**다운로드 전에 저장**) |
| `stage_c_windows.json` | §3-4 |
| `summary.json` | 다운로드 수(B/C), full_match 팀 수, field_match 팀 수, identity/length 문제 수, 비-1.32.7 수 |
| `file_hashes.json` | 위 전부 SHA-256 |

## 5. 검증 (완료 조건)

- 다운로드 합계 ≤147, 요청 목록 = 실제 받은 목록.
- 무작위 3개 쌍에 대해 추출을 두 번째 코드 경로(예: 전체 steps 를 다시 읽는 별도 함수)로 재계산해 full_sha 일치.
- 단위 테스트 1개 이상: 가짜 replay 2개로 좌석 판별·해시·`market_nonempty_agree` 확인.
- 가설 원장: `python3 tools/update_hypotheses.py --agent antigravity --hypothesis-id HYP-0019 --test-id TEST-DONOR-ROUTES-20260917 --reason "F0 stage B/C collection" --set "다음 행동=<기존 값> + 산출 경로"` (상태·결과 칸 불변). `python3 tools/validate_hypotheses.py --strict` exit 0.

## 6. BLOCKED 조건

인증·네트워크 실패가 30분 이상 지속, 고유 episode 수 ≠ 87, replay 스키마에 `steps[t][seat].action` 이 없음, identity_mismatch 가 10쌍 이상. 반환 보고에 막힌 항목과 가능한 해석 후보를 적는다.

## 7. 보고

`coordination/reports/antigravity/YYYYMMDD-HHMM-F0-STAGE-BC.md` 한 파일. AGENTS §10.1 형식 + `VERDICT | 핵심 사실 2개 | exact path + SHA | 검증 | NEXT`.
핵심 사실: "단계 B full_match 팀 수"와 "단계 C 에서 k_of_6 = 6 인 팀 수".


---

## `proposals/claude/20260920-DAILY-PUBLIC-SCAN-ANTIGRAVITY.md`

# 작업 지시서 — 매일 새 공개 변형 확인 루프 (Antigravity, 09-20 ~ 09-26 매일 1회)

발행: Claude, 2026-09-20. 수신: **Antigravity** (Gemini 3.5 Flash · Low). 실행 위치: 사람 Mac.
근거: 사람 승인(2026-09-20) — 매일 새 공개 변형을 확인해 P2 와 로컬 비교, 기준을 넘는 것만 제출 후보로 올린다.

## 매일 할 일

1. **목록:** 대회 공개 notebook 중 **직전 실행 이후** `last_run_time` 이 새로 바뀐 것(첫 실행은 2026-09-19T00:00Z 이후). ref·제목·투표·last_run·점수 주장 한 줄(markdown 셀에서 `\b[1-3]\d{3}(\.\d)?\b` 포함 첫 문장).
2. **받기:** 그 notebook 들만 `docs/collection_snapshots/<slug>/` 에 새 폴더로(기존 폴더가 있으면 `<slug>__YYYYMMDD/`). `docs/code/` 덮어쓰기 금지.
3. **계보:** `analysis/lineage/classify_lineage.py`(r2 규칙 그대로)로 분류.
4. **재현 가능 여부만 기록:** 제출 코드 생성 셀 유무, 외부 dataset 의존 여부, notebook 기대 SHA 유무. **빌드·경기는 하지 않는다**(빌드는 Codex, 비교 경기는 별도 지시).
5. **출력:** `analysis/daily_scan/YYYYMMDD/{new.json,lineage.json,file_hashes.json}`, 보고 `coordination/reports/antigravity/YYYYMMDD-HHMM-DAILY-SCAN.md` — 새 notebook 수, 분류별 수, 점수 주장이 있는 것 목록.

금지: 순위·추천, 코드 실행, 추가 다운로드(replay·dataset), BOARD·KILLS·`HYPOTHESES.md` 편집. 새 것이 0개면 "0개"로 보고하고 끝낸다.

## 이후 (Claude 몫, 참고)

Claude 가 목록에서 후보를 고르면 → Codex 무수정 재현 → Antigravity 가 arena 로 후보 vs P2 (seed 2000–2009 양 좌석 20경기) → **P2 상대 8승 이상**이면 제출 후보.

## 추가 규칙 (2026-09-22, 사람 승인) — 추출물이 실제 agent 코드인지 확인
09-21 스캔에서 dmitriigluzdov notebook 3개가 main.py 대신 LICENSE 본문을 추출했고, 그 중 하나로 보이는 봇이 C1 hosted 패배 30/50 의 원인이었다.
각 추출 main.py 에 대해 아래를 **모두** 확인하고 결과를 lineage.json 의 `code_check` 필드에 기록:
1. `ast.parse` 성공 (실행하지 않음).
2. 최상위에 callable 정의(def/class/lambda 대입)가 1개 이상, 그리고 마지막 callable 이름 기록.
3. 첫 30줄이 라이선스 본문만("Apache License", "TERMS AND CONDITIONS")이고 def 가 없으면 실패.
4. 50줄 미만이거나, notebook 안에 base64/zlib payload·`%%writefile`·`write_bytes` 가 있는데 추출 파일에 그 내용이 없으면 실패.
- 실패 시 classification = `EXTRACTION_FAILED` (UNKNOWN·DIFFERENT 로 두지 않음), 보고서 맨 위 "재추출 필요" 목록에 올리고, payload 디코드(C2 방식)나 셀 본문 재추출을 한 번 시도.
- 투표 수 상위 10 notebook 이 EXTRACTION_FAILED 이면 VERDICT 에 명시.
- 보충 (09-22): multi-file 패키지(main.py 가 같은 폴더의 .py 를 import)는 main.py 단독이 아니라 **import 되는 로컬 모듈까지 합쳐** 규칙 1~4 를 적용한다 (줄 수 합산, 각 파일 ast.parse). 합쳐서 통과하면 EXTRACTION_FAILED 아님.
- 보충 (09-22): release 를 만들 때 tar 안 main.py 의 sha 가 release 폴더 main.py 와 같은지 반드시 확인 (one-more-wheat tar 에서 본문이 두 번 들어간 불량 발견).


---

## `proposals/claude/20260920-EXP014-015-BUILD-CODEX.md`

# 작업 지시서 — EXP-014·015 변형 빌드 + instrument 진입점 수정 (짧은 작업)

발행: Claude, 2026-09-20. **r2: 수신자 Codex → Claude (같은 프로젝트 새 채팅, Sonnet)** — 사람 지시. 파일명은 이력 보존을 위해 그대로 둔다.
**소유권 예외(사람 지시 2026-09-20):** 이 작업에 한해 Claude 가 `releases/`·`tools/instrument.py` 에 쓴다. 다른 `tools/` 파일, 기존 release 폴더, 카드는 수정하지 않는다. 커밋하지 않는다.

**실행 환경:** Mac 에서 도는 셸이면 `.venv/bin/python` 을 쓴다. Cowork 리눅스 VM 이면 `.venv` 가 macOS 용이라 쓸 수 없으니 `python3 -m pip install --user kaggle-environments==1.32.7` 후 `kaggriculture.py` SHA 가 `environment/ENGINE_LOCK.md` 값(`bc8a5487…653e`)과 같은지 확인, 다르면 멈춘다. 보고에 host 를 적는다.

1. **빌드 2개** — 카드 부록 A 코드를 **바이트 그대로** parent `releases/public-lynnsakurai-farming-score-v2-exact/main.py`(SHA `cddf51ea…a94d`) 끝에 `\n\n` 뒤로 덧붙인다. parent 바이트 변경 금지.
   - `experiments/cards/EXP-014-mirror-sale-lead.md` (SHA `419ed1d0…df1c`) → `releases/f0-mirror-lead-exp014/{main.py,submission.tar.gz,manifest.json}`
   - `experiments/cards/EXP-015-mirror-slot-priority.md` (SHA `7afc314a…b446`) → `releases/f0-mirror-slot-exp015/…` (EXP-015 는 EXP-014 공통 부분 + `'reorders': 0` + 자기 함수)
   - 결정론적 tar — `tools/build_public_exact.py` 의 tar 생성 함수(`archive_main`)를 import 해서 쓰거나 같은 규칙(mtime·uid·gid·mode 고정, 멤버 `main.py` 하나)으로 만든다. builder 파일 자체는 수정하지 않는다, 두 번 같은 SHA.
2. **빌드 확인** (각 변형): exec 후 마지막 callable 이 카드에 적힌 함수인지 / `tools/arena.py --a <변형> --b releases/public-alperen-before-dawn-stock-cash-sales-exact/main.py --seeds 1 --seed-start 3000` 1경기에서 변형과 parent 의 719턴 행동이 완전히 같은지(거울 모드 꺼짐 확인) / `--b` 를 P2 로 1경기 돌려 `mirror_games`≥1 이고 예외 0.
3. **`tools/instrument.py` `load_agent` 수정** — `getattr(mod, "agent")` 대신 엔진과 같은 규칙(모듈 전역에서 **마지막 callable**; `kaggle_environments/agent.py:64` 참조)으로 불러오게 한다. 기존 자체 파일(마지막 callable 이 `agent`)에서 결과가 바뀌지 않는지 `main.py` vs starter 1경기로 확인. 09-19 gate 재실행은 하지 않는다.
4. 금지: 카드 수정, 경기 matrix 실행(Antigravity 가 한다), 제출. 보고 `coordination/reports/claude/YYYYMMDD-HHMM-EXP014-015-BUILD.md` — 두 tar 경로·SHA, 확인 3항목 결과.


---

## `proposals/claude/20260920-EXP014-015-RUN-ANTIGRAVITY.md`

# 작업 지시서 — EXP-014·015 사전등록 경기 실행 (Antigravity)

발행: Claude, 2026-09-20. 수신: **Antigravity** (Gemini 3.5 Flash · Low). 선행: 빌드 보고(`coordination/reports/claude/*-EXP014-015-BUILD.md`).
판단 없이 카드에 적힌 경기만 돌리고 숫자만 집계한다. 판정은 Claude 가 한다.

## 실행 (모두 `tools/arena.py`, 결과는 `analysis/exp014_015/raw/`)

| # | --a | --b | --seeds / --seed-start | 경기 |
|---|---|---|---|---:|
| B0 | P2 | P2 | 15 / 3000 | 30 |
| M14 | EXP-014 변형 | P2 | 15 / 3000 | 30 |
| M15 | EXP-015 변형 | P2 | 15 / 3000 | 30 |
| NP2-* | P2 | 패널 5개 각각 | 10 / 3000 | 100 |
| N14-* | EXP-014 변형 | 패널 5개 각각 | 10 / 3000 | 100 |
| N15-* | EXP-015 변형 | 패널 5개 각각 | 10 / 3000 | 100 |

- P2 = `releases/public-lynnsakurai-farming-score-v2-exact/main.py`, 변형 = 빌드 보고의 `releases/f0-mirror-*/main.py`, 패널 5개 경로 = 카드 EXP-014 `opponents.panel` 그대로.
- 시작 전 입력 SHA(P2 tar `1178ffa0…f388`, 패널 tar 5개, 변형 tar 2개, 카드 2개)를 계산해 기록. 다르면 멈춤.
- **seed·경기 수를 늘리거나 줄이지 않는다.** 중간에 멈추지 않는다.

## 집계 (`analysis/exp014_015/summary.json`) — 카드 정의 그대로

- B0: 무승부 수 / 30.
- M14·M15: 변형의 W/D/L 과 점수(W=1, D=0.5).
- N: 변형·P2 각각 패널 총점. **회귀 수** = 같은 (상대, seed, 좌석)에서 P2 는 W 또는 D 인데 변형은 L 인 경기 수.
- 패널 경기 중 변형의 거울 모드가 켜진 경기 수(변형 telemetry 가 없으면 N/A 로 적음).
- 예외·ERROR 수.
- **판정(success/failure 등)은 적지 않는다.**

## 보고

`coordination/reports/antigravity/YYYYMMDD-HHMM-EXP014-015-RUN.md` 한 파일 — 위 숫자 표, 입력 SHA, 결과 파일 SHA. 금지: 코드·카드 수정, 제출, 해석.


---

## `proposals/claude/20260920-EXP014R-RUN-ANTIGRAVITY.md`

# 작업 지시서 — EXP-014R 재현 경기 실행 (Antigravity)

발행: Claude, 2026-09-20. 수신: **Antigravity** (Gemini 3.5 Flash · Low). 카드: `experiments/cards/EXP-014R-mirror-sale-lead-replication.md` (SHA `73019a7a3abb78c7147eab54501dfc86c65c59b690f46a8a054a3f94b5c6309c`).
판단 없이 표의 경기만 돌리고 숫자만 집계한다. 판정은 Claude.

| # | --a | --b | --seeds / --seed-start | 경기 |
|---|---|---|---|---:|
| B0R | P2 | P2 | 15 / 4000 | 30 |
| M14R | EXP-014 변형 | P2 | 15 / 4000 | 30 |
| NP2R-* | P2 | 패널 5개 각각 | 10 / 4000 | 100 |
| N14R-* | EXP-014 변형 | 패널 5개 각각 | 10 / 4000 | 100 |

- 경로: P2 `releases/public-lynnsakurai-farming-score-v2-exact/main.py`, 변형 `releases/f0-mirror-lead-exp014/main.py`(tar `be529b5c…0d29`), 패널 5개는 지난 실행과 같은 경로.
- 시작 전 입력 SHA(카드, P2 tar, 변형 tar, 패널 tar 5개) 기록. 다르면 멈춤. seed·경기 수 변경 금지, 중간 중단 금지.
- 결과 `analysis/exp014r/raw/`, 집계 `analysis/exp014r/summary.json`: B0R W/D/L·점수·무승부 수, M14R W/D/L·점수, NP2R·N14R 총점, 회귀 수(같은 상대·seed·좌석에서 P2 는 W/D 인데 변형은 L), 예외·ERROR 수, 경기별 margin. **판정 문구는 쓰지 않는다.**
- 보고 `coordination/reports/antigravity/YYYYMMDD-HHMM-EXP014R-RUN.md` — 숫자 표, 입력·결과 SHA.


---

## `proposals/claude/20260920-F0-LIVE-CLAIM-VARIANTS-WORK-ORDER.md`

# 작업 지시서 — 실제 ladder 점수를 밝힌 최신 공개 변형 2개 exact 재현·gate

발행: Claude (Coordinator 역할), 2026-09-20 KST. 수신: **Codex** (사용량이 없으면 Claude 새 채팅 — 사람 지시로 소유권 예외, `20260919-F0-DIFFERENT-LINEAGE-RESUME-CLAUDE.md` §0 와 같은 조건).
근거: fast lane 승인(09-19, "09-16 이후 공개 notebook 무수정 재현"). P2 패배 분석 결과 단일 원인 없음 → 표적 수정보다 더 강한 최신 변형 비교가 우선.

## 한 화면 요약

1. **무엇:** 작성자가 **실제 ladder 점수**를 밝힌 P2 가족 최신 변형 2개를 무수정 재현하고 gate·로컬 진단을 한다.
2. **왜:** P2 는 2421.6(09-19)로 동메달 경계와 몇 점 차이다. 같은 bytes 도 ladder 에서 약 90점까지 벌어진다는 공개 측정(`jaxa623/2802-two-identical-agents-90-points-apart`, `[COMMUNITY]`)이 있어, 여유가 더 필요하다.
3. **측정:** gate 22경기 + 진단. hosted 는 사람 제출 후.
4. **다음:** 보고 → Claude 제출 순서 제안 → 사람 제출.

## 1. 후보 (Antigravity 수집본, 추가 다운로드 없음)

| # | notebook | 원문 SHA-256 | 작성자 주장 `[COMMUNITY]` |
|---|---|---|---|
| V1 | `docs/collection_snapshots/kaggriculture-melon-threshold-squeeze-2749/…ipynb` (goodpjw2008, last_run 09-19) | `ae34db0ef30bb7f858532ded3bbed229678c2db804f117d8fe5cdbad1e5d6eed` | "2749 on the live ladder", Özer V4x 계열 파생 + day-0 멜론 squeeze |
| V2 | `docs/collection_snapshots/kaggriculture-2820-score/…ipynb` (seyitkaangunes, 09-16) | `09d9833a860b521db3083abd24a9abcd9a74404be81adf2b0ae096a01b6a3be4` | "V44 + layers 1,2,4 (submission 56277542): 2801 rating, rank ~188" (09-16 스냅샷). notebook 에 `USE_CADENCE` 등 **설정 분기가 있다** — **notebook 기본값 그대로** 빌드하고 기본값을 manifest 에 기록 |

두 notebook 모두 계보 분류상 P2 와 같은 가족(sim_p2 0.87 / 0.84, tape 38/38 공유). 점수 주장은 날짜·필드가 다르며 우리 exact 제출은 작성자 주장보다 낮게 나온 전례가 있다(HYP-0028: yhay81 작성자 2929 vs 우리 2188).

## 2. 할 일

`20260919-F0-PUBLIC-EXACT-WORK-ORDER-CODEX.md` §2–§4 와 **같은 규칙**:
1. `tools/build_public_exact.py` 에 `v1`·`v2` 추가, 원문 무수정, 결정론적 tar 두 번 같은 SHA, notebook 기대 SHA 가 **활성 assert** 로 있으면 일치해야 PASS(주석으로만 남은 과거 값은 `STALE_EXPECTATION` 으로 기록하고 진행). 출력 `releases/public-<author>-<slug>-exact/`.
2. gate 22경기(starter seed 1000–1009 × 좌석 0·1 + self seed 1000·1001), runtime, clean-room.
3. 진단(seed 2000–2009 좌석 교대, 쌍당 20경기): 각 후보 vs **P2** `releases/public-lynnsakurai-farming-score-v2-exact/main.py`, 각 후보 vs **P1 alperen** `releases/public-alperen-before-dawn-stock-cash-sales-exact/main.py`, **V1 vs V2**. seed 추가 금지.

## 3. 금지·보고

제출, 원문 수정, 추가 다운로드, BOARD·KILLS·카드·`HYPOTHESES.md` 직접 편집, 결과를 보고 기준 변경.
보고서 `coordination/reports/<실행자>/YYYYMMDD-HHMM-F0-LIVE-CLAIM-VARIANTS.md` — 표 `후보 | tar SHA | 기대 SHA | gate | p99 ms | vs P2 | vs P1 | V1 vs V2`. 원장 updater(HYP-0028, TEST-DONOR-ROUTES-20260917, 상태·결과 불변) + `validate --strict` exit 0.

재확인 명령: `shasum -a 256 docs/collection_snapshots/kaggriculture-melon-threshold-squeeze-2749/*.ipynb docs/collection_snapshots/kaggriculture-2820-score/*.ipynb`


---

## `proposals/claude/20260920-P2-LOSS-ANALYSIS-CLAUDE.md`

# 작업 지시서 — P2 hosted 패배 원인 빈도 분석 (Claude)

발행: Claude (Coordinator 역할), 2026-09-20 KST. 수신: **Claude (같은 프로젝트 새 채팅)** — 사람 지시로 Codex 대신 Claude 가 분석한다.
선행: Antigravity 수집 완료 보고(`coordination/reports/antigravity/*-P2-LOSS-COLLECTION.md`)와 `analysis/p2_losses_20260920/`.

## 한 화면 요약

1. **무엇:** P2(56347732)의 hosted 패배·무승부 전부와 대조 승리를 **같은 기준으로** 요약해, "질 때만 자주 생기는 일"을 빈도로 센다.
2. **왜:** 동메달 여유가 몇 점뿐이다(09-19 기준 +2.7). P2 위에 얹을 개선 1–2개를 근거 있게 고르기 위해서다.
3. **측정:** replay 원자료 요약만. 경기 재실행 없음.
4. **다음:** 개선 후보 카드 초안(사람 승인 전 구현·실행 없음).

## 0. 시작 전

- AGENTS §11 시작 절차(BOARD·HYPOTHESES·FACTS·KILLS 읽기). §3 꼬리표 규율을 지킨다 — 이 분석은 `[HOSTED]` 원자료 기술 통계, 원인 주장은 `[INFERENCE]`.
- 수집 보고의 `selection.json`·`manifest.json` SHA 를 재계산해 보고와 일치하는지 확인. 불일치면 멈춤.
- 실행 환경: Mac native 셸이면 `.venv/bin/python`, 리눅스 VM 이면 표준 `python3` (엔진 불필요 — replay JSON 만 읽는다).

## 1. 경기별 요약 (A·B 모두 같은 코드로)

기존 `tools/postmortem_hosted.py --replay <raw> --team Sian --output evidence/raw/p2_losses_20260920/postmortem/<episode>.json` 을 각 replay 에 돌린다. `tools/` 는 수정하지 않는다. `analysis/` 는 Gemini 경로라 Claude 출력은 모두 `evidence/raw/p2_losses_20260920/` 아래에 둔다.

추가로 경기마다 아래를 replay 에서 직접 계산해 `evidence/raw/p2_losses_20260920/features.csv` 로 저장 (필드 이름 그대로):

| 필드 | 정의 |
|---|---|
| `result`, `margin` | W/L/D, P2 − 상대 최종 뱅크 |
| `div_day` | 두 플레이어 뱅크 차가 처음 5,000 이상 벌어져 끝까지 유지된 날 (없으면 null) |
| `route_at_144` | P2 의 turn 144 시점 해금 상점 앞 2개 (P2 router 입력) |
| `opp_is_clone` | turn 1–143 동안 상대 farmer+hands 행동이 P2 와 같은 turn 비율 ≥ 0.9 |
| `hands_d2`, `hands_d6` | P2 의 2일차·6일차 끝 일손 수 |
| `min_cash_d1_7` | 1–7일 P2 최저 현금 |
| `sell_units_by_item`, `sell_revenue_by_item` | 품목별 실제 판매량·매출 (P2, 상대 각각) |
| `animals_final` | 최종 COW·SHEEP·GOOSE 수 (P2, 상대) |
| `shed_full_days` | P2 창고 100 도달 일수 |
| `failed_orders` | P2 의 체결 안 된 BUY/HIRE 주문 수 (요청 대비 실제 변화로 판정) |
| `opp_team` | 상대 팀 이름 |

정의가 replay 스키마로 계산 불가능하면 그 필드는 `N/A` 로 두고 이유를 적는다. **정의를 바꾸지 않는다.**

## 2. 집계 — 빈도와 대조

- A(패배·무승부)와 B(대조 승리)에서 각 필드의 분포를 나란히 적는다(비율·중앙값). 같은 상대 매칭 쌍만의 비교를 별도 표로.
- **"질 때만 자주" 기준:** A 에서의 비율 − B 에서의 비율 ≥ 20%p 이고, A 에서 20% 이상인 특징만 후보 원인으로 올린다. 이 문턱은 지금 고정한다.
- 상대별 패배 수 상위 10팀, `opp_is_clone` 여부별 패배율, `route_at_144` 별 패배율(경기 5개 미만 경로는 묶음).
- 표본: A·B 각각 경기 수를 표마다 적는다. 신뢰구간이 필요한 비율은 Wilson 95%.

## 3. 결론 형식

- 후보 원인 **최대 2개**. 각각: 정의, A/B 비율, 해당 패배 수, 대표 패배 1경기(episode ID, `div_day`)의 postmortem 인용.
- 각 원인마다 P2 위에 얹을 **1-change 개선 초안 1개**: 무엇을 A→B 로 바꾸는지, 어느 turn 범위에서만 작동하는지, 원래 tape 작업을 덮어쓰지 않는지(HYP-0027 주의), 로컬 선별 방법(fast lane 계획 §4 단계 F — 다른 상위 tape 상대 고정 seed). **구현·경기 실행은 하지 않는다.**
- 후보 원인이 하나도 문턱을 넘지 않으면 그대로 "없음"으로 보고한다. 억지로 만들지 않는다.

## 4. 산출·금지

- 보고서 `coordination/reports/claude/YYYYMMDD-HHMM-P2-LOSS-ANALYSIS.md` 한 파일 (AGENTS §10.1 + VERDICT 줄). 원자료 `evidence/raw/p2_losses_20260920/`.
- 원장: `python3 tools/update_hypotheses.py --agent claude --hypothesis-id HYP-0028 --test-id TEST-DONOR-ROUTES-20260917 --reason "P2 hosted loss analysis" --set "다음 행동=<기존 값> + 보고서 경로"` → `validate_hypotheses.py --strict` exit 0. (새 가설 ID 배정은 개선 카드 단계에서 사람 승인 후.)
- 금지: 경기 실행, 코드·release 수정, 제출, 추가 다운로드, BOARD·KILLS 편집, 결과를 보고 문턱·정의 변경. 애매하면 멈추고 BLOCKED + 해석 후보.


---

## `proposals/claude/20260920-P2-LOSS-COLLECTION-ANTIGRAVITY.md`

# 작업 지시서 — P2 hosted 패배 전부 + 대조 승리 수집 (Antigravity)

발행: Claude (Coordinator 역할), 2026-09-20 KST. 수신: **Antigravity** (단순 자료 수집). 실행 위치: 사람 Mac (kaggle CLI/API).
사람 승인 2026-09-20: 패배 전부 수집, **상한 200**, 대조 승리 동수, replay 다운로드 허용.

## 한 화면 요약

1. **무엇:** P2(submission **56347732**)의 hosted 경기 목록을 받아, 기준 시각 이전에 끝난 **패배·무승부 전부**(최신순 최대 200)와 **같은 수의 대조 승리** replay 를 받는다.
2. **왜:** P2 가 실제로 어디서 지는지 원인 빈도를 세서 개선 후보를 고르기 위해서다. 분석은 Claude 가 별도로 한다.
3. **측정:** 없음 — 목록·다운로드·기초 메타데이터만.
4. **다음:** 보고 → Claude 분석(`20260920-P2-LOSS-ANALYSIS-CLAUDE.md`).

## 1. 범위 고정 (다운로드 전에 파일로 저장)

1. **기준 시각** `as_of` = 스크립트 시작 시각(UTC). 이후 끝난 경기는 넣지 않는다.
2. `competition_list_episodes(56347732)` 전부 → `state` COMPLETED, `type` `EPISODE_TYPE_PUBLIC`, `endTime ≤ as_of` 만. validation(자기 자신 대전)은 제외.
3. 결과 분류(P2 좌석 = `agents` 중 `submissionId == 56347732` 의 `index`, 없으면 0):
   - `W` P2 reward > 상대 reward / `L` 작음 / `D` 같음.
4. **대상 A (패배·무승부):** `L` 과 `D` 전부. 합이 200 을 넘으면 `endTime` 최신순 200개. 잘린 수를 기록.
5. **대상 B (대조 승리):** 대상 A 의 각 경기에 대해, 최신 A 부터 순서대로
   - 같은 상대 `teamId` 에게 이긴 경기 중 아직 안 고른 것 가운데 `endTime` 이 그 A 경기에 가장 가까운 것
   - 없으면 상대 무관, 아직 안 고른 승리 중 `endTime` 이 가장 가까운 것
   - 승리가 바닥나면 그 이상 짝짓지 않는다(부족 수 기록).
6. `selection.json` 에 as_of, 규칙 문장, 전체 경기 수, W/L/D 수, A 목록, B 목록(각 B 가 어느 A 의 짝인지, 같은 상대 매칭인지)을 **다운로드 전에** 저장한다. **결과를 보고 규칙·목록을 바꾸지 않는다.**

## 2. 다운로드·검증

- `competition_episode_replay(<id>)` → `private_artifacts/p2_losses_20260920/raw/episode-<id>-replay.json` (gitignore 경로). 429 는 대기 후 재시도.
- 각 replay: `info.EpisodeId` 일치, `info.TeamNames[seat] == "Sian"`, replay `rewards` 가 목록 metadata 와 일치, `module_version`·`configuration.seed` 기록. 불일치는 `identity_mismatch` 로 기록하고 분석 목록에서 뺀다.
- 파일 SHA-256·bytes 기록. **raw 는 지우지 않는다.**

## 3. 출력

- 스크립트 `analysis/p2_losses/collect.py`, 결과 `analysis/p2_losses_20260920/`
  - `episodes_all.json` — 기준 시각까지 전체 경기 metadata (W/L/D, 상대 teamId·teamName·submissionId, 좌석, 양쪽 reward, 시각)
  - `selection.json` — §1-6
  - `manifest.json` — 받은 replay 별 경로·SHA·bytes·seat·seed·engine·결과·짝 정보
  - `summary.json` — 전체/W/L/D 수, A 수(잘림 포함), B 수(같은 상대 매칭 수), identity_mismatch 수, 총 용량
  - `file_hashes.json`
- 금지: 분석·해석·원인 추정, 경기 실행, P2 이외 submission 수집, `tools/`·`releases/`·BOARD·KILLS·`HYPOTHESES.md` 편집. 애매하면 BLOCKED + 해석 후보.

## 4. 보고

`coordination/reports/antigravity/YYYYMMDD-HHMM-P2-LOSS-COLLECTION.md` 한 파일. AGENTS §10.1 + `VERDICT | 핵심 사실 2개 | 결과 파일 SHA | 검증 | NEXT`. 핵심 사실: 기준 시각까지 P2 전체 W/L/D, 받은 A·B 수.
검증: 무작위 3개 replay 로 좌석·reward 를 별도 코드 경로로 재확인. 가설 원장 기록은 하지 않는다.


---

## `proposals/claude/20260921-C1-HOSTED-OPPONENT-MAP-ANTIGRAVITY.md`

# 20260921 C1 hosted 경기 수집 + 상대 계열 지문 (Antigravity 수집 / Claude 분석)

실행 위치: 사람 Mac (kaggle CLI/API, 20260920-P2-LOSS-COLLECTION 과 같은 방법). 사람 승인 = 이 prompt 전송 (replay 다운로드 허용, 상한 300).

## 왜
hosted 에서 C1(56426857)이 실제로 누구와 붙고 누구에게 지는지 — C1 복제본(거울전)인지, Ozer V5x 계열인지 — 를 세기 위함.

## 1. 수집 (P2 수집 지시서 §1~§2 규칙 그대로, submission 만 56426857)
- `as_of` 고정 → PUBLIC·COMPLETED·endTime ≤ as_of 경기 **전부** 목록 (validation 제외).
- replay 는 **전부** 받음 (최신순 300 상한, 잘린 수 기록). 결과 W/L/D, 상대 teamName·submissionId, 좌석, seed, 양쪽 reward.
- 출력: `analysis/c1_hosted_20260921/` (episodes_all.json, manifest.json, summary.json, file_hashes.json). raw 는 `private_artifacts/c1_hosted_20260921/raw/`.

## 2. 상대 지문 (결정적 비교, 해석 금지)
- 참조 파일: C1, C2, C3, C4(V53), C5(V51), P2, releases/public-yhay81-shop-router-0909-exact.
- **먼저 대조 검사:** hosted 경기 5개를 골라 같은 seed·같은 좌석으로 C1 vs C1 을 로컬 실행 → hosted 의 **우리 쪽** 행동과 step 1~143 이 완전히 같은지. 5개 중 하나라도 다르면 지문 단계는 `BLOCKED: replay not reproducible` 로 멈추고 수집 결과만 보고.
- 대조 통과 시, 각 hosted 경기마다: 같은 seed·좌석에서 상대 자리에 참조 파일 R 을 넣고 우리 자리엔 C1 을 넣어 로컬 실행 → 상대의 step 1~143 행동이 R 과 완전히 같은 가장 긴 prefix 길이 기록.
  - 143 전체 일치하는 R 이 있으면 label = R, 여러 개면 모두 기록, 없으면 `UNKNOWN` (최장 prefix 와 그 R 기록).
  - 거울전 판정: 상대 행동이 경기 **전체 720 step** 에서 C1 과 같으면 `MIRROR_EXACT`.
- 출력: `analysis/c1_hosted_20260921/opponents.csv` (episode, seed, seat, 결과, margin, 상대 team, label, prefix 길이, MIRROR_EXACT 여부).

## 3. 보고
`coordination/reports/antigravity/<ts>-C1-HOSTED-MAP.md`: 전체 W/L/D, label 별 경기 수와 C1 W/L/D, MIRROR_EXACT 수, 대조 검사 결과, VERDICT 한 줄. 제출·원인 추정·경기 해석 금지.


---

## `proposals/claude/20260921-C1-LOSS-MIRROR-COLLECTION-ANTIGRAVITY.md`

# 20260921 C1 패배·거울전 수집 (Antigravity 수집 / Claude 분석)

## 왜
- C1 (releases/public-nathanjacob-pipe16-exact, 827ddf29) 이 slot A. slot B 는 C2 대신 **C1-variant** 로 쓴다.
- C1 의 로컬 패배는 C4(V53) 8/20, C5(V51) 4/20 에서만 나옴. 또 C1 은 공개 복제본이 여럿이라 hosted 에서 **C1 vs C1 거울전**이 잦을 것.
- 개선 방향을 정하기 전에 이 두 종류 경기를 충분히 모은다. 판단·변형 설계는 하지 말 것.

## 경기 (tools/arena.py, 엔진 로더, 양 좌석)
| 블록 | 대전 | seed | 경기 수 |
|---|---|---|---|
| L1 | C1 vs C4 (releases/public-ozer-v53-exact) | 2010–2049 | 80 |
| L2 | C1 vs C5 (releases/public-ozer-v51-exact) | 2010–2049 | 80 |
| M1 | C1 vs C1 | 2010–2049 | 80 (좌석 교대 = 같은 파일 두 번) |
| R1 | C1 vs C2 (releases/public-thomastschinkel-metav4-v13-exact) | 2010–2029 | 40 |

## 기록 (경기마다 1행, `analysis/c1_losses/20260921/games.csv`)
seed, seat, opponent, 결과(W/D/L), 최종 cash 양쪽, margin, 무승부 여부, C1 이 받은 route id(step 144 이후 첫 route), 양쪽 첫 두 shop, 예외 수, 최대 step 시간.
- C1 이 진 경기와 무승부 경기는 **전부** replay JSON 저장 (`analysis/c1_losses/20260921/replays/`). 상한 200.
- M1 은 좌석별 승률(P0 vs P1)과 무승부 비율을 따로 집계.
- 저장된 패배 replay 마다 `tools/postmortem.py` 가 되면 돌려 첫 분기 step 과 요약만 첨부 (해석 금지).

## 보고
`coordination/reports/antigravity/<ts>-C1-LOSS-MIRROR.md`: 블록별 W/D/L, 평균·최악 margin, 좌석별 승률, 패배 수, 예외 수, 저장 파일 목록 + sha, VERDICT 한 줄. 제출·다운로드 금지.


---

## `proposals/claude/20260921-F0-2945-LINE-CANDIDATES-ANTIGRAVITY.md`

# 20260921 F0 — 2945 Farm 계열 후보 exact 재구성 + P2 대비 arena (Antigravity)

작성: Claude (Coordinator) · 근거: coordination/reports/antigravity/20260921-1231-DAILY-SCAN.md, analysis/daily_scan/20260921/lineage.json (35238cd1…7021)
범위: fast lane (09-18 승인). 제출·팀 변경·코드 공개 금지. 외부 dataset 다운로드는 **사람 승인 후** Stage 2 에서만.

## 왜
- P2 대조본 56398299 = 2161.9 (~13h). 동메달 cutoff 2444.5 (09-20). P2 계열로는 격차가 줄지 않음.
- 스캔에서 새 상위 계열 발견: Thomas Tschinkel "The 2945 Farm" (주장: 정확히 이 파일이 ladder 2944.7, submission 56269928) → "Metav4 Farm v13" (주장: 2945 대비 40–0) → nathanjacob Pipe16 (v13 + HybridOpening).
- 주장은 저자 자기 보고. 로컬 arena 로 P2 대비 실제 우위를 먼저 확인.

## 후보
| ID | 출처 | 상태 | main sha256 |
|---|---|---|---|
| C1 | nathanjacob/kaggriculture-pipe16-idle-workers (= haideptry/the-2950-peak-farm, CR/EOF 차이만) | 추출 완료 | 827ddf29…8181 (haideptry 613245d9…a7) |
| C5 | ahmedberatozer/kaggriculture-v51-lean-flock | 추출 완료 | c1e3590d…9891 |
| C2 | thomastschinkel/the-metav4-farm-submission-v13 | external_dataset — Stage 2 | — |
| C3 | thomastschinkel/the-2945-farm-96-vs-the-top-10-public-bots | external_dataset — Stage 2 | — |
| C4 | ahmedberatozer V52 / V53 | 추출 실패(패턴 없음) — Stage 2 | — |

## Stage 1 (지금, 다운로드 없음): C1, C5
1. `tr -d '\r'` 정규화 후 sha 기록. 원본 바이트는 그대로 release 에 사용.
2. release: `releases/public-nathanjacob-pipe16-exact/`, `releases/public-ozer-v51-exact/` (main.py, SHA256SUMS, LICENSE 문구 보존, tar).
3. 진입점: 엔진 규칙 = **마지막 callable** (FACTS 2026-09-20). C1 은 `agent=globals().pop('agent')` 로 끝남 → 마지막 callable 이름을 기록.
4. §3-2 6줄 gate (identity/schema/runtime/isolation/license/ledger). LICENSES.md 에 행 추가(Apache-2.0).
5. arena (tools/arena.py, 엔진 로더 사용):
   - 각 후보 vs P2 (releases/public-lynnsakurai-farming-score-v2-exact), seed 2000–2009 × 양쪽 좌석 = 20경기.
   - C1 vs C5 동일 20경기.
   - 기록: W/L/D, 평균 cash margin, 최악 margin, step 시간 최대값, 예외 수.
6. 기준 (사전 고정, 결과 후 변경 금지): P2 대비 **≥14/20 승** 이고 예외 0 이면 "제출 후보". 8–13 은 "보류". <8 은 폐기.

## Stage 2 (사람이 다운로드 승인한 뒤): C2, C3, C4
- notebook + 연결 dataset 파일 스냅샷 → main.py 추출(코드 실행 금지, 정적 추출) → Stage 1 과 같은 절차.
- 추가 arena: C2 vs C1, C3 vs C1 (같은 20 seed).

## 보고
`coordination/reports/antigravity/<ts>-2945-LINE-ARENA.md` — 표 + VERDICT 한 줄. 판단(어느 것을 올릴지)은 Claude.


---

## `proposals/claude/20260921-F0-2945-LINE-STAGE2-ANTIGRAVITY.md`

# 20260921 F0 — 2945 계열 Stage 2 (외부 dataset 스냅샷) (Antigravity)

전제: 사람이 이 프롬프트를 보냄 = 아래 3개 notebook 과 연결 dataset 의 다운로드 승인.
선행: 20260921-F0-2945-LINE-CANDIDATES-ANTIGRAVITY.md Stage 1.

## 대상
- C2 thomastschinkel/the-metav4-farm-submission-v13
- C3 thomastschinkel/the-2945-farm-96-vs-the-top-10-public-bots
- C4 ahmedberatozer/kaggriculture-v53-opening-signature (없으면 v52-lean-flock-yarn-route)

## 절차
1. notebook 버전 + 연결 dataset 의 현재 버전을 `analysis/daily_scan/20260921/stage2/<slug>/` 에 스냅샷. 버전 번호·파일 sha256 기록.
2. 정적 추출만 (notebook/dataset 코드 실행 금지). submission 이 tar 이면 구성 파일 전부, main.py 단일이면 그 파일.
3. 마지막 callable 이름 기록. 외부 파일 읽기(open/os.path)·네트워크 import 가 있으면 행 표시 → 그 후보는 보류.
4. exact release + §3-2 6줄 gate + LICENSES.md 행.
5. arena (seed 2000–2009 × 양 좌석 = 20경기씩):
   - C2, C3, C4 각각 vs P2
   - C2 vs C1, C3 vs C1, C4 vs C1
6. 보고: `coordination/reports/antigravity/<ts>-2945-LINE-STAGE2.md` — W/L/D, 평균·최악 margin, 최대 step 시간, 예외 수, VERDICT 한 줄.
판단 기준은 Stage 1 과 동일 (P2 대비 ≥14/20 & 예외 0 = 제출 후보). 후보 간 순위는 Claude 가 정함.


---

## `proposals/claude/20260921-F0-2945-LINE-STAGE2B-ANTIGRAVITY.md`

# 20260921 F0 — Stage 2b: C2/C3 보류 해제 + C3 재추출 + C1 대비 arena (Antigravity)

## Claude 판정 (Stage 2 보고 검토)
- C2/C3 의 `open()` (main.py:3590) 은 `os.environ.get("V92_SELL_LIB")` 가 있을 때만 실행되는 **개발용 경로**. Kaggle hosted 에는 이 env 가 없으므로 파일을 읽지 않음 → 보류 사유 아님. **보류 해제.**
- "외부 dataset" 은 제출물 의존성이 아니라 notebook 의 **비교용 상대 봇** (kernel_sources: tetsutani/demand-preserving-turn-sale-timing). 그 main.py sha = 827ddf29… = C1 과 동일.
- C2 main.py sha 9d634946… = notebook 의 EXPECTED_SHA256 과 일치 → exact OK.
- C3 main.py sha 4f3ca95d… ≠ notebook 의 EXPECTED_SHA256 bfee70e9… → **추출이 exact 가 아님**. notebook 은 `%%writefile` 뒤에 CRLF→LF 치환을 하므로, 셀 본문을 그대로 쓰고 끝 개행 처리까지 맞춰 bfee70e9 가 나올 때까지 재추출. 안 맞으면 C3 는 보류 유지.
- C1 release tar 에 macOS `._main.py` 가 섞여 있었음 → Claude 가 `releases/public-nathanjacob-pipe16-exact/submission_clean.tar.gz` (3f410af2…, main.py 만, sha 827ddf29) 생성. 앞으로 모든 tar 는 `COPYFILE_DISABLE=1 tar --no-xattrs -czf submission.tar.gz main.py` 로 만들고 `tar tzf` 로 main.py 한 줄만 나오는지 확인.

## 할 일
1. C3 재추출 (위 기준). release: `releases/public-thomastschinkel-2945-farm-exact/`, C2: `releases/public-thomastschinkel-metav4-v13-exact/`. 6줄 gate, 마지막 callable 기록, LICENSES 행.
2. arena, seed 2000–2009 × 양 좌석 = 20경기씩:
   - C2 vs C1, C3 vs C1 (C3 은 exact 확인된 경우만), C2 vs C3
   - C2 vs P2 (기준 확인용)
3. 보고: `coordination/reports/antigravity/<ts>-2945-LINE-STAGE2B.md` — W/L/D, 평균·최악 margin, 최대 step 시간, 예외 수, VERDICT 한 줄. 다운로드·제출 금지 (이미 받은 파일만 사용).

## Slot A 교체 규칙 (09-21 Claude 제안, 09-27 00:00 KST 까지)
1. 새 후보는 현재 최고 활성 bot 상대 로컬 **≥14/20 승 & 예외 0** 일 때만 제출 후보. (P2 상대는 확인용, ≥18/20)
2. 제출은 **하루 1회까지**. 직전 제출이 hosted 24h 를 채우지 않았으면 다음 제출 보류 (runtime 오류 확인 목적).
3. hosted 에서 새 bot 이 48h 후 기존 최고보다 100점 이상 낮으면 되돌림 (기존 파일 재제출).
4. 09-27 00:00 KST 이후에는 새 계열·새 variant 금지, 이미 hosted 검증된 파일끼리만. 09-29 에 최종 2슬롯 고정.


---

## `proposals/claude/20260922-STEP53-BOT-ID-ANTIGRAVITY.md`

# 20260922 hosted 최대 패배원 "step 53 봇" 식별 + 대전 (Antigravity 수집·실행 / Claude 판단)

사람 승인 = 이 prompt 전송 (아래 공개 notebook 스냅샷 다운로드 허용). 제출 금지.

## 왜
C1 hosted 148경기 중 50패의 30패가 한 부류: step 1–53 은 C1 과 같고 step 54 에 hand 1 이 HARVEST 대신 PASS, step 55 에 BUILD_PASTURE 대신 PASS (34경기, 서로 다른 팀 30+ → 공개 notebook 복제본). margin 대부분 −27~−60.
설명이 맞는 후보: dmitriigluzdov 의 "One More Wheat", "A Smaller Market Shock", "More Wheat, Smarter Sales" ("idle opening worker 로 pasture 가 되기 전 밀을 한 번 더 키움"). 09-21 스캔에서는 main.py 대신 LICENSE 가 추출돼 코드가 없다.

## 할 일
1. 세 notebook (+ 09-22 기준 dmitriigluzdov 의 다른 Kaggriculture 공개 notebook 이 있으면 포함) 현재 버전 스냅샷 → `analysis/step53/<slug>/`. 코드 실행 없이 정적 추출 (base64/zlib payload 면 C2 때 방식). notebook 안에 EXPECTED_SHA256 류 값이 있으면 일치 확인.
2. release: `releases/public-dmitriigluzdov-<slug>-exact/` (tar 는 `COPYFILE_DISABLE=1 tar --no-xattrs`, main.py 외 NOTICE 등 notebook 이 tar 에 넣는 파일 그대로). 마지막 callable 기록. LICENSES 행.
3. 지문: `analysis/c1_hosted_20260921/opponents.csv` 에서 prefix_len=53 & label 에 C1 인 34경기 각각을, 지난번과 같은 방법(같은 seed·좌석, 우리 자리 C1)으로 각 후보를 상대 자리에 넣어 step 1–143 완전 일치 여부. 34경기 중 몇 경기가 어느 후보와 143 전체 일치하는지 표.
4. arena (seed 2100–2119 × 양 좌석 = 40경기씩), 143 일치가 가장 많은 후보 X 에 대해:
   - X vs C1 (releases/public-nathanjacob-pipe16-exact)
   - X vs EXP-016 (releases/f0-c1-adv-exp016)
5. 보고 `coordination/reports/antigravity/<ts>-STEP53-ID.md`: 추출 sha, 지문 표, arena W/D/L(경기·seed)·평균/최악 margin·예외·최대 step 시간, VERDICT 한 줄. 해석 금지.


---

## `proposals/claude/20260923-ABSORPTION-RESEARCH-CODEX-ASTRA.md`

# 20260923 후속 연구 — 품목별 시장 흡수량 대비 우리 판매량 (codex-astra)

기한: **2026-09-25 12:00 KST**. 금지: 제출, Kaggle 다운로드, releases/ 편집. 허용: 저장소·엔진 읽기, analysis/ 아래 분석 스크립트, 이미 받은 replay.

## 왜 (1차 보고 뒤 바뀐 초점)
1차 보고의 조건부 상한(실제 대비 2~5배)은 느슨해서 행동을 정하지 못한다. 대신 **엔진의 비대칭 하나**를 정량화하자.
- `SHOPS` (kaggriculture.py:103-112): BAKERY EGG·WHEAT / PIZZA MILK·TOMATO·WHEAT / BRUNCH EGG·WHEAT·STRAWBERRY / YARN WOOL / ICE_CREAM STRAWBERRY·MILK·WHEAT / PET_CAFE CARROT / SMOOTHIE STRAWBERRY·MILK / FARMERS_MARKET WHEAT·CARROT·TOMATO·STRAWBERRY.
- `_town_consume` (728-748): 해금된 shop 인스턴스마다 4 step 에 품목당 1개(단일품목 shop 은 2개), town center 는 24 step 에 전 품목 1개.
- **MELON 은 어느 shop 에도 없다** → 24 step 에 1개만 흡수된다. FERTILIZER 도 shop 목록에 없다.
- 가격은 재고의 비증가 함수이므로, 흡수량보다 많이 팔면 그 품목 가격은 사실상 회복되지 않는다.
- 관찰(20260923-2000-TOP-AGENT-SNAPSHOT): d0-11 MELON 상위 3팀 52u @222 vs 우리 72u @181. d12-18 CARROT 상위 13~49u vs 우리 0u.

## 질문
Q1. 한 경기(예: seed 2142, EXP-017 vs OMW)에서 품목별 **시즌 누적 흡수량**(해금 일정 반영)과 **우리 누적 판매량**을 표로 내라. 어느 품목에서 얼마나 초과 판매하는가.
Q2. 초과 판매가 가격에 준 손실을 계산하라: 같은 수량을 (a) 실제 시점, (b) 흡수량에 맞춰 분산한 시점에 팔았을 때의 수입 차이. 상대 행동은 실제 replay 그대로 고정.
Q3. 손실이 큰 품목 상위 2개에 대해, **부모 바이트를 건드리지 않고 덧붙이는 층**으로 고칠 수 있는 규칙을 제시하라 (예: 품목별 1턴 최대 판매 단위 상한, 남은 수량은 다음 턴으로). 규칙은 상수 몇 개로 표현되어야 한다.
Q4. 생산을 바꿔야만 얻는 이득(예: MELON 대신 CARROT)과, 판매만 바꿔서 얻는 이득을 나눠서 추정하라. 09-27 마감을 고려해 판매 쪽만 권고해도 된다.

## 제약 (2026-09-23 재검토본 — 근거와 함께)
권고안은 아래를 만족해야 한다. 못 맞추면 "왜 넘는지 + 넘을 때의 기대 이득"을 적어라. 상한은 금지선이 아니라 **기본값**이다.

| 제약 | 근거 | 성격 |
|---|---|---|
| 한 step 0.5초 이내, 예외 0 | 엔진 `actTimeout = 1`초 (kaggriculture.json). 2배 여유 | **하드** — 넘으면 hosted 에서 실격 위험 |
| parent `releases/f0-omw-adv-exp017/main.py` (56941da2…) **바이트 수정 없이 뒤에 덧붙이기** | 실패 시 부모를 그대로 재제출해 되돌릴 수 있다. 지금까지 성공한 변경(EXP-016/017 의 98줄 층, OMW 의 49줄)은 전부 append 형태였고, OMW 는 append 로 tape 자체도 고쳤다 → 표현력 제한이 거의 없다 | **하드** |
| 외부 파일 읽기·네트워크·환경변수 의존 없음 (표준 라이브러리 import 는 허용) | fast lane §3-2 isolation gate. C2/C3 의 `V92_SELL_LIB` 처럼 환경 의존 코드는 hosted 에서 조용히 꺼진다 | **하드** |
| 검증이 **arena 1회(≤ 약 1,000경기)** 안에 끝날 것 | 측정된 처리량 18.2초/경기 (EXP-016 A_mirror 80경기 1457.1초) → 1,000경기 ≈ 5시간. 09-24~09-26 에 후보 2~3개가 한계 | **하드** (09-27 00:00 KST 신규 전략 마감) |
| 상수 몇 개 + wrapper 함수로 표현되어 각 상수를 따로 껐다 켤 수 있을 것 | 실패 시 원인 분리가 가능해야 한다. EXP-016 은 두 기능(앞당김·frontload)이 묶여 있어 v13 상대 회귀의 원인을 못 갈랐다 | **강한 권고** |
| 추가 줄 수 약 200줄 | 성공 사례 최대치(98줄)의 2배. **줄 수 자체가 위험을 예측한다는 근거는 없다** — 검토·분리 가능성의 대용치일 뿐 | **soft default** — 기대 이득이 크면 초과 제안 가능, 대신 위 "상수 분리"와 arena 1회 조건은 지킬 것 |

## 산출물
`coordination/reports/codex/<날짜>-ABSORPTION.md`: Q1~Q4 답(숫자 우선, 추정은 [INFERENCE]) + 사전등록 카드 초안(EXP-018, parent sha, one_change, seed 2180-2219, 상대 OMW·EXP-016·V53·v13, success/failure 기준). 실행 Antigravity, 판정 Claude, 제출 사람.


---

## `proposals/claude/20260923-CANDIDATE-POLICY.md`

# 20260923 후보 운영 규칙 (제약을 언제 박고, 아슬아슬한 후보를 어떻게 다룰지)

작성 Claude. 사람 승인 전 초안. 적용 범위: 09-29 최종 2슬롯 고정까지.

## A. 제약은 두 종류로 나눈다
**A-1 환경 제약 = 지시서에 미리 박는다** (아이디어의 좋고 나쁨과 무관한 사실)
- 한 step 0.5초 이내(엔진 actTimeout 1초), 예외 0
- 부모 바이트 수정 없이 덧붙이기 (되돌림 가능성)
- 외부 파일·네트워크·환경변수 의존 없음 (isolation gate)
- 검증이 arena 1회 ≤ 약 1,000경기 (측정 18.2초/경기 → 약 5시간; 09-27 00:00 KST 마감)

**A-2 설계 제약 = 미리 박지 않는다** (줄 수, 어느 층을 건드릴지, 어떤 기법인지)
- 기본값으로만 적고, **초과하는 아이디어는 버리지 말고 "초과 사유 + 기대 이득"과 함께 보고**하게 한다.
- 이유: 지금까지 이득이 큰 발견(판매 앞당김 층, step 53 봇)은 모두 우리가 미리 정한 범위 밖에서 나왔다.

## B. 후보 판정과 제출은 분리한다
카드의 판정(SUCCESS / INCONCLUSIVE / FAILURE)은 **사전 기준 그대로** 두고 절대 사후 변경하지 않는다.
제출 여부는 아래 **슬롯 정책**이 따로 정한다. 즉 "기준을 고치는" 일은 없고, "슬롯을 어떻게 쓰는가"만 정한다.

### B-1 슬롯 역할
- **슬롯 A(현재 hosted 최고 점수 파일)**: SUCCESS 판정 후보만 올린다.
- **슬롯 B**: hosted 실험용. 아래 조건을 모두 만족하는 INCONCLUSIVE 후보를 올릴 수 있다.

### B-2 INCONCLUSIVE 후보를 슬롯 B 에 올릴 조건 (모두 만족)
1. 현재 최고 파일과의 직접 대결에서 seed 기준 순승 ≥ 0
2. 패널 **합산** 패배가 늘지 않음
3. **hosted 가중 기대 변화 > 0**: Σ_f share_f × (후보 점수율_f − 부모 점수율_f). share_f 는 최신 hosted 상대 지문(analysis/c1_hosted_*/opponents.csv)의 계열 비율, 점수율은 로컬 (승 + 0.5×무)/경기. 지문에 없는 계열(UNKNOWN)은 0 으로 두고 그 비율을 함께 보고.
   그리고 hosted 비율 20% 이상인 계열 중 점수율이 10%p 넘게 떨어지는 계열이 없을 것 (큰 상대 하나에서 무너지는 것 방지)
4. 예외 0, 런타임 조건 충족
5. 현재 슬롯 B 가 비어 있거나, 그 자리의 파일보다 위 1~2 에서 낫다
- FAILURE 판정(사전 failure 조건 발동)은 어떤 경우에도 제출하지 않는다.
- 실험은 **한 번에 하나**. 두 슬롯을 동시에 실험에 쓰지 않는다.

### B-3 되돌림
hosted 24시간 이상 지난 시점에 실험 파일이 다른 슬롯보다 **100점 이상 낮으면** 직전 파일이나 검증된 exact 를 재제출한다.

### B-4 날짜 (09-23 개정)
- 09-27 00:00 KST 이후에도 **슬롯 B 실험은 허용**. 슬롯 A 는 hosted 24h 이상 검증된 최고 점수 파일로 고정하고 건드리지 않는다.
- 실험 후보도 로컬 gate(SUCCESS 또는 B-2 충족)는 그대로 통과해야 한다.
- 마지막 실험 제출: **09-30 12:00 UTC** (최종 마감 23:59 UTC 전 12시간 — runtime 오류가 보이면 되돌릴 시간).
- 근거: 최종 순위는 팀의 가장 좋은 봇 하나로 정해진다(지금까지의 전제). 슬롯 B 는 보험이 아니라 두 번째 기회라서, 슬롯 A 가 지켜지는 한 실험의 하방은 작다.

### B-5 FIFO 주의 (슬롯 A 보호 절차)
새 제출은 항상 **두 활성 제출 중 오래된 것**을 은퇴시킨다. 슬롯 A 파일이 더 오래됐으면 다음 실험 제출이 슬롯 A 를 날린다.
- 슬롯 A 가 더 오래됐을 때 실험을 교체하려면: ① 슬롯 A 파일을 **같은 바이트로 재제출**(오래된 A 가 은퇴, 새 A' 가 최신) → ② 실험 제출(이전 실험이 은퇴). 교체 1회에 제출 2회.
- 재제출한 A' 는 점수가 600 에서 다시 시작하지만 바이트가 같으므로 마감 후 2주 경기에서 같은 수준으로 수렴한다. 매 제출 전 BOARD 활성 슬롯 줄에서 "다음 제출이 무엇을 은퇴시키는가"를 확인한다.

## C. 근거 (이 규칙이 나온 사례)
- EXP-016: 사전 기준 INCONCLUSIVE(v13 상대 패배 +6). B-2 를 적용하면 제출 가능했고, 실제 hosted 2425.7 로 C1(2206.6)보다 +219 였다. 기준을 고치지 않고도 옳은 결정을 내릴 수 있었다.
- EXP-015: 사전 failure 조건 발동(회귀 14). B-2 의 2번에서 걸러진다.
- 제약을 미리 좁게 박았다면 EXP-016 의 판매 앞당김 층(98줄, 남의 파일에서 통째 이식)은 후보에 오르지 못했을 수 있다.

## D. B-2 3번 식의 예시 (EXP-016, 사후 계산)
hosted 비율(C1 148경기): v13|2945 25.7% · step53 봇 23.0% · C1 거울 6.1% · P2 5.4% · V53|V51 4.1% · UNKNOWN ≈ 35.8%.
로컬 점수율 변화(후보−부모): v13 −7.5%p · step53 봇 +75%p · 거울 +29%p · P2 +2.5%p · V53|V51 약 +7.5%p.
- 당시 알던 패널만 쓰면: 0.257×(−7.5) + 0.061×29 + 0.054×2.5 + 0.041×7.5 ≈ **+0.3%p** (작지만 양수 → 제출 가능)
- step53 봇까지 넣으면: 위 + 0.230×75 ≈ **+17.5%p** (실제 hosted +219점과 방향 일치)
- v13 계열 비율 25.7% 이상 · 하락 7.5%p < 10%p → 두 번째 조건도 통과.

## E. 개정 (09-23 저녁, 사람 제공 사실 반영)
### E-1 최종 순위 규칙 (사람 확인)
- 두 활성 봇이 **각자** 최종 Bradley-Terry 레이팅을 받고, 더 높은 쪽 등수가 팀 순위.
- 최종 BT fitting 은 "양쪽 모두 활성인 경기"만 쓴다 → **마감 후 2주 경기가 핵심 표본**. 레이팅은 600 으로 초기화되지 않는다.
- 늦은 제출의 비용: ① 600 에서 상위 매칭 풀까지 약 60경기(5~6시간) 수렴 ② 마감 직전 오류(Validation Error·시간 초과)에 대응할 시간 없음. 하루 제출 한도 5회.

### E-2 B-2 3번 식 보정 (방향 판단용 1차 필터로만 사용)
- 가중치 share_f 는 **평가 대상과 같은 레이팅 구간의 최신 hosted 경기**(지금은 EXP-016/017)에서 잰다. C1(~2200) 구간 값 사용 금지.
- 통과 조건: 합 > **2 × 표준오차** (계열별 로컬 paired 점수율 차의 SE 로 계산). 합이 오차 안이면 "판단 불가".
- UNKNOWN 비율이 30% 를 넘으면 결론 옆에 반드시 병기하고, 40% 를 넘으면 이 식으로 제출 판단하지 않는다.

### E-3 슬롯 B 의 목표 재정의
최종 순위 = max(A, B). 슬롯 B 의 가치는 "B 가 A 를 넘을 확률 × 넘는 폭".
- 1순위: A 를 넘을 가능성이 있고(E-2 통과 또는 A 상대 직접 대결 순승 ≥ 0) **A 와 메커니즘이 다른** 후보 — 마감 직전 field 변화(새 공개 notebook 확산)에 A 와 다르게 반응하므로 둘이 같이 무너질 위험이 줄어든다.
- 평균이 A 보다 크게 낮은 "보완형"은 A 를 넘을 확률이 거의 없어 가치가 없다. 한 계열만 잡는 "저격형"도 전체 레이팅이 낮으면 기여하지 못한다.
- 지금 EXP-016/017 은 같은 판매 층을 공유하는 형제 → 판매 방식이 다른 후보가 나오면 슬롯 B 1순위.

### E-4 마지막 일정
- 09-30 오전(KST) Antigravity 최종 공개 notebook scan (지시서 20260923-FINAL-SCAN-ANTIGRAVITY.md).
- **마지막 제출 09-30 12:00 UTC** (= 21:00 KST). 이후 오류 확인·되돌림 시간 12시간.
- 마감 직전 제출은 수렴 시간(5~6시간) 때문에 마감 전 hosted 확인이 거의 불가능 → 09-30 에 올리는 파일은 로컬 gate 를 이미 통과한 것만.

### E-5 09-30 긴급 경로 (최종 scan 에서 슬롯 A 를 이기는 새 파일 X)
패널 회귀 검증을 12:00 UTC 전에 끝낼 수 없으면, **슬롯 B 에 한해** 아래 최소 gate 만으로 제출 가능.
- 필수(생략 불가, 수 분): tar 안에 main.py 한 파일 · tar 안 sha = 추출 sha · 마지막 callable 기록 · 외부 파일/네트워크/환경변수 의존 없음 · 예외 0 · 최대 step < 0.5초
- 성능: X vs 슬롯 A **≥14/20** (20경기, seed 2300-2309 양 좌석). 13 이하면 올리지 않는다.
- FIFO 확인: 이 제출이 은퇴시키는 쪽이 **슬롯 B** 인지 BOARD 에서 확인. 슬롯 A 가 더 오래됐으면 A 재제출 → X 제출 순서(2회). 하루 한도 5회.
- 근거: 최종 순위 = max(A, B). 슬롯 A 가 남아 있는 한 X 가 틀려도 손해는 "슬롯 B 의 기회 하나". 반대로 20경기 우위는 우연일 확률이 약 6% 이고, 직접 대결 우위가 field 전체 우위로 이어지지 않은 전례(OMW: C1 40-0, 그러나 EXP-016 에 10-30)가 있다 → 슬롯 A 교체에는 쓰지 않는다.

### E-6 마감 후 (10-01 ~ 약 10-14)
제출 변경 불가 → 의사결정 없음. 할 일은 기록뿐: 마감 직후 1회, 1주 후 1회, 최종 발표 후 1회 LB·두 봇 점수 스냅샷을 HOSTED_LEDGER 에 남긴다 (사후 회고용).

## F. 개정 (09-25, 사람 지시 반영)
### F-1 E-5 긴급 경로 보강 — "상성 상대에게 강하면서 기존 상대도 계속 이기는가"
09-30 에 상성 파일(예: herd-safe-v3) 확산이 보여 그에 강한 파일 X 를 슬롯 B 에 올리려면, E-5 필수 gate 에 더해 **둘 다** 만족:
1. **기존 상대 유지**: DP hosted 복제 패널(유효 47경기, `analysis/exp018_panel/` 목록, 같은 seed·좌석)에서 X 점수율 ≥ 슬롯 A 점수율 − 2 × paired SE. (18초/경기 기준 약 15분)
2. **상성 상대 개선**: 확산된 상성 파일 상대 closed-loop 경기(패널 안 해당 계열 + 없으면 seed 2300–2319 × 양 좌석 40경기)에서 X 가 슬롯 A 보다 점수율이 높을 것.
- 참고: 09-24 수집 기준 herd-safe FULL 의 재가중 field 비중은 약 2.6% 로 작다. 확산 규모(최종 scan 4번 표)가 이 값보다 크게 늘었을 때만 이 경로를 검토한다.
### F-2 목표 재설정
09-25 DP 2191.6 (동메달 경계 2289.7 아래). 목표를 "은 구간 도전" → **"동메달 복귀 우선"** 으로 되돌린다. 09-24 균형 추정(2450~2550)은 상대 강도를 팀 LB 로 잰 오류로 폐기.


---

## `proposals/claude/20260923-FINAL-SCAN-ANTIGRAVITY.md`

# 20260923 최종 공개 notebook scan (Antigravity) — 실행일 2026-09-30 오전 KST

사람 승인 = 이 지시서 (실행 당일 사람이 prompt 전송). 제출 금지.

## 언제
- **2026-09-30 오전 (KST 09:00~11:00 사이 시작)**. 결과 보고 기한 **KST 15:00 (= 06:00 UTC)**.
- 이유: 마지막 제출 시한 09-30 12:00 UTC(21:00 KST) 전에 후보 판단(Claude)·로컬 gate(Antigravity)·제출(사람)을 끝내야 한다.

## 할 일
1. 20260920-DAILY-PUBLIC-SCAN-ANTIGRAVITY.md 의 매일 절차 + 추출물 코드 확인 규칙 그대로 적용. 기준 시각 = 직전 scan 이후.
2. SAME_FAMILY / 새 계열 모두, 추천 수 상위 15개는 반드시 코드 확인(EXTRACTION_FAILED 이면 한 번 재추출).
3. **빠른 대전 (새 파일만, 1개당 20경기)**: 새 공개 파일 X 각각에 대해 X vs 우리 슬롯 A 파일, seed 2300–2309 × 양 좌석. 새 파일이 많으면 추천 수 상위 5개까지.
4. **상성 파일 확산 확인 (09-25 사람 지시 추가)** — 슬롯 A 계열(DP 0924)에 강한 파일이 퍼졌는지:
   - 대상: `herd-safe-v3-experimental-risk-aware-feed` 계열, DP 를 step 143 까지 따라가다 갈라지는 변형(label `DP-0924-exact|harvest-ledger`), 그리고 `analysis/dp_hosted_20260924/summary.json` 의 `top_15_opponents_defeating_dp` 가 가리키는 공개 파일.
   - 각각: 공개 notebook 수·최신 버전 시각·추천 수 (09-24 대비 증감), 새 fork/변형 여부.
   - DP 자신: 같은 sha(178ae0f7) 또는 DP 파생 notebook 수 (09-24 대비).
   - 가능하면 DP 를 쓰는 submission 3개(56518910 포함)의 **최근 24h hosted 경기 헤더만** 받아 상대 계열 비율과 DP 승점률 (다운로드는 헤더만, 전체 replay 금지). 09-24 수치(`evidence/HOSTED_LEDGER.md` DP 지도)와 나란히.
5. 보고 `coordination/reports/antigravity/20260930-FINAL-SCAN.md`: 새 notebook 목록, 분류, 코드 확인 결과, 빠른 대전 W/D/L·평균 margin·예외, **4번 확산 표**, VERDICT 한 줄. 해석·제출 금지.

## 이후 (Claude, 참고)
X 가 슬롯 A 를 20경기 중 14승 이상 이기면: 당일 조합(X + 우리 판매 층) 또는 X exact 를 후보 정책 E-3/E-4 에 따라 판단. 로컬 gate 는 축소판(부모·슬롯 A·상위 2계열, 각 40경기)으로 12:00 UTC 전에 끝내야 한다.


---

## `proposals/claude/20260923-FUNDAMENTAL-GAIN-RESEARCH-CODEX-ASTRA.md`

# 20260923 근본적 점수 상승 탐색 (codex-astra) — 연구 지시서

발행: Claude (Coordinator). 수신: codex-astra (판단·설계 담당). 기한: **2026-09-25 24:00 KST 까지 1차 답**, 09-26 까지 카드 1장.
금지: 제출, Kaggle 다운로드(필요하면 BLOCKED 로 적고 사람에게 요청), releases/ 편집, BOARD·KILLS·HYPOTHESES.md 직접 수정, 결과 보고 전 코드 대량 작성.
허용: 저장소 읽기, 엔진 소스 읽기, 이미 받아둔 replay·로그 분석, 작은 분석 스크립트(analysis/ 아래), 사고 실험, 계산.

## 1. 지금 상태 (사실만)
- 활성 2슬롯: C1 pipe16 exact 2206.6 / EXP-016 (C1+판매 앞당김) **2425.7**. LB 9,886팀, 1위 3192.6, 동메달 경계 2346.1.
- 우리 계열은 전부 **공개 tape 재생 + 반응 층 적층**이다. 로컬 사슬: EXP-017 > EXP-016 > OMW > C1 > v13(C2) > 2945Farm(C3) > V51/V53 > P2.
- 같은 tape 를 쓰는 상대끼리는 **시장 판매 타이밍**이 승패를 가른다 (coordination/reports/claude/20260922-C1-HB-ANALYSIS.md: 농장 물리 행동 100% 동일, 차이는 판매).
- 상위권과 우리 차 ≈ 700점. 층을 하나 더 얹는 방식으로는 27~200점 단위 개선만 나왔다.
- 이미 죽은 길: evidence/KILLS.md 전부 읽을 것. 특히 K3(외부 replay 에서 tape 복제 — 0/52 실패), K2(2턴 선행매도).

## 2. 질문 (이 순서로 답할 것)
Q1. **상한이 어디인가.** 결정적 엔진(kaggle_environments 1.32.7, kaggriculture.py)에서 한 seed 의 우리 최종 cash 와, 같은 seed 에서 이론상 도달 가능한 cash 의 차이는 얼마인가? 최소한 느슨한 상한(예: 생산량 고정 + 판매를 사후 최적 가격에 배치)이라도 계산해 숫자로 제시.
Q2. **그 차이가 어디에 있는가.** 생산 계획(무엇을 언제 심고 짓고 고용) / 판매 스케줄 / 상대 반응 중 어디가 큰가. 한 구간이라도 수치로 나눠라.
Q3. **가장 큰 구간을 09-27 전에 건드릴 수 있는가.** 가능하면 방법 3개를 기대 점수 · 구현 난이도 · 회귀 위험으로 표로 비교하고 1개를 추천.

## 3. 반드시 볼 것
- 엔진: `.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py` — `_process_market`(544-628), `_refresh_prices`, `_town_consume`(728-748), 작물/동물 표, 고용 비용(Fibonacci), `shedCapacity` 100, `maxMarketOrdersPerTurn` 10.
- 우리 파일: `releases/f0-omw-adv-exp017/main.py` (현재 최고), `releases/public-ozer-v53-exact/main.py:3532-3629` (판매 앞당김 층).
- 자료: `analysis/c1_losses/20260921/` (로컬 패배·거울전 replay), `analysis/c1_hosted_20260921/` (hosted 148경기 + 상대 지문), `evidence/FACTS.md`, `evidence/KILLS.md`.

## 4. 참고 가설 (검증 대상이지 결론 아님)
- H1 판매 스케줄 최적화: 시장 가격이 재고에 따라 움직이고 town 이 4 step 마다 재고를 깎는다. 생산량을 고정한 채 "언제 몇 개를 파는가"만 전 구간 최적화하면 얼마가 남는가.
- H2 생산 계획 자체가 최적이 아님: 공개 tape 38개는 09-08 경 만들어진 것이다. 결정적 엔진에서 탐색(beam/DP)으로 더 나은 계획이 나오는가.
- H3 상대 반응: 주문은 slot 순서로 체결된다. 같은 tape 상대의 다음 수를 알 수 있으면 최적 대응이 존재한다(v44y 가 일부 구현). 남은 이득이 있는가.
- H4 노동 경제: 고용 비용이 Fibonacci 로 오른다. 고용 수·시점이 최적인가.

## 5. 산출물
`coordination/reports/codex/<날짜>-FUNDAMENTAL-GAIN.md`
1) Q1~Q3 답 (숫자 우선, 추정은 [INFERENCE] 표시)
2) 방법 3개 비교표 + 추천 1개
3) 추천안의 사전등록 카드 초안 (parent sha, one_change, seed, 상대, success/failure 기준). 실행은 Antigravity, 판정은 Claude.
4) 포기 권고도 정당한 결론이다 — 상한이 작으면 "층 적층 유지"라고 써라.


---

## `proposals/claude/20260923-NEW-GAIN-SEARCH-OPUS55.md`

# 20260923 새 점수 향상 방법 탐색 (Opus 5.5) — 연구 지시서

수신: Claude Opus 5.5 (새 대화). 기한: **2026-09-25 18:00 KST 1차 답**, 09-26 12:00 KST 까지 카드 초안.
codex-astra 가 "판매량이 시장 흡수량을 넘는가"(20260923-ABSORPTION-RESEARCH-CODEX-ASTRA.md)를 맡고 있다. **이 지시서는 그와 겹치지 않는 방향**을 맡는다.
금지: 제출, Kaggle 다운로드(필요하면 BLOCKED 로 적고 사람에게 요청), releases/ 편집, BOARD·KILLS·HYPOTHESES.md 직접 수정.
허용: 저장소·엔진 읽기, analysis/ 아래 분석 스크립트, 이미 받은 replay 분석, 로컬 경기 소량(진단용 ≤ 40경기).

## 1. 먼저 읽을 것 (순서대로)
1. `evidence/KILLS.md`, `evidence/FACTS.md` — 이미 죽은 길을 반복하지 말 것 (특히 K2, K3)
2. `coordination/proposals/claude/20260923-CANDIDATE-POLICY.md` — 제약·슬롯 정책. **환경 제약(A-1)은 하드, 설계 제약은 soft**
3. `evidence/HOSTED_LEDGER.md` 09-21 이후, `coordination/reports/claude/20260922-C1-HB-ANALYSIS.md`
4. `coordination/reports/antigravity/20260923-2000-TOP-AGENT-SNAPSHOT.md` 와 `analysis/top_agents_20260923/` (상위 3팀 120경기 + EXP-017 20경기 집계), raw 는 `private_artifacts/top_agents_20260923/raw/`
5. 현재 최고 파일 `releases/f0-omw-adv-exp017/main.py` (56941da2…), 엔진 `.venv/.../kaggriculture.py`

## 2. 목표
최종 순위 = 두 봇 중 **높은 쪽**의 Bradley-Terry 레이팅. 지금 두 봇(EXP-016/017)은 같은 판매 층을 공유하는 형제다.
→ **슬롯 B 용으로, 지금 봇과 메커니즘이 다르면서 지금 봇을 넘을 가능성이 있는 변경**을 찾는 것이 목표다.

## 3. 질문 (이 순서로, 숫자 우선)
Q1. **DSM(1위, 40경기 36승) 과 EXP-017 이 처음 갈라지는 결정은 무엇인가.** 같은 첫 두 shop 인 경기끼리 짝지어, day 별 농장 구성(작물 종류별 타일·동물·hand 수)과 첫 번째 큰 차이의 day·내용을 표로. 상대가 달라 cash 는 참고값임을 명시.
Q2. **생산 구성 차이가 설명하는 몫.** 관찰: d12-18 CARROT 상위 13~49u vs 우리 0u, d19-29 TOMATO 상위 71~109u vs 우리 32u, MELON 우리가 더 많이 더 싸게 판다. shop 해금 목록(SHOPS)과 연결해, "그 판에 해금된 shop 이 사 주는 작물을 키웠는가"로 설명되는 차이를 추정.
Q3. **부모 바이트를 건드리지 않고 덧붙이는 층으로 그 차이의 일부를 가져올 수 있는가.** (예: OMW 처럼 `_alt_install` 류 hook 으로 route tape 의 특정 구간 작물을 shop 해금에 따라 바꾸기.) 가능한 방법 2~3개를 기대 이득·구현 규모·회귀 위험·**EXP-017 과의 메커니즘 차이** 로 비교하고 1개 추천.
Q4. 추천안이 환경 제약(0.5초/step, append-only, 외부 의존 없음, arena 1회 ≤ 1,000경기)을 지키는지. 설계 제약을 넘으면 사유와 기대 이득.

## 4. 산출물
`coordination/reports/claude/<날짜>-NEW-GAIN-OPUS55.md`
1) Q1~Q4 답 (추정은 [INFERENCE]) 2) 비교표 + 추천 1개
3) 사전등록 카드 초안: parent sha, one_change, seed 2220-2259, 상대(EXP-017·EXP-016·OMW·C2(v13)·C4(V53)), success/failure 기준, 그리고 **정책 E-2 식을 쓸 hosted 가중치 출처**
4) "찾지 못했다"도 정당한 결론이다 — 그 경우 가장 가까웠던 후보와 막힌 이유를 적어라.


---

## `proposals/claude/20260923-TOP-AGENT-REPLAY-COLLECTION-ANTIGRAVITY.md`

# 20260923 상위권 에이전트 경기 수집 (Antigravity 수집 전용)

사람 승인 = 이 prompt 전송 (공개 episode replay 다운로드 허용, 상한 200). 제출·해석 금지.

## 왜
LB 1위 3192.6, 우리 최고 2425.7. 상위 봇이 우리와 **어떤 결정에서 갈라지는지** 보려면 그들의 경기 기록이 필요하다.
주의: 남의 replay 에서 행동을 그대로 복제하는 길은 이미 실패로 기록돼 있다 (evidence/KILLS.md K3). 이 작업은 **관찰용 자료 수집**이며 tape 복제가 목적이 아니다.

## 할 일
1. LB 상위 3팀의 team id 와 현재 점수를 기록 (competition leaderboard). 각 팀의 공개 episode 목록을 받을 수 있는지 확인.
   - 받을 수 없으면 그 사실을 적고 **BLOCKED** 로 멈춘다. 우회 시도 금지.
2. 받을 수 있으면 팀당 최신 COMPLETED PUBLIC 경기 최대 40개의 replay 를 `private_artifacts/top_agents_20260923/raw/` 에 저장. 목록·결과·상대·seed·좌석을 `analysis/top_agents_20260923/episodes.json` 에 기록.
3. 각 경기에서 **상위 봇 쪽 좌석**에 대해 아래만 표로 집계 (해석 금지):
   - day 별 cash, day 별 보유 동물 수(GOOSE/COW/SHEEP)·작물 종류별 타일 수·hand 수
   - 품목별 판매 단위 수와 그 시점 가격 (d0-11 / d12-18 / d19-29)
   - 첫 두 shop, 첫 HIRE step, 첫 BUILD_PASTURE step, 마지막 날 cash
4. 같은 표를 우리 EXP-017 로컬 경기(seed 2140-2149, 양 좌석)에 대해서도 만들어 나란히 둔다.
5. 보고 `coordination/reports/antigravity/<ts>-TOP-AGENT-SNAPSHOT.md` — 표 + VERDICT 한 줄. 원인 추정·전략 제안 금지 (Claude/codex-astra 몫).


---

## `proposals/claude/20260924-DP-LOSS-CAUSE-CODEX.md`

# 20260924 demand-preserving 0924 의 hosted 패배 원인 → 덧붙이는 패치 1개 (Codex) — 판단 작업

발행: Claude (Coordinator), 2026-09-24 20:45 KST. 수신: **Codex** (최상위 모델 · reasoning high). Codex 사용량이 막히면 Claude 새 채팅(Opus 5.5)에서 같은 지시로 실행 — 소유권 예외는 20260919 §0 과 같은 조건.
**발행 조건: Antigravity `*-DP-HOSTED-MAP.md` 의 VERDICT 가 PASS 이고 Coordinator 가 이 문서 상단에 "발행" 줄을 추가했을 때.** (수집 결과를 보고 Coordinator 가 숫자·범위를 고칠 수 있다.)
기한: **2026-09-25 21:00 KST** (분석·카드), **2026-09-26 20:00 KST** (release + gate). 신규 전략 마감 09-27 00:00 KST.
금지: 제출, Kaggle 다운로드(필요하면 BLOCKED + 목록), BOARD·KILLS·HYPOTHESES 직접 수정, 카드 판정 기준의 사후 변경.
대체: `20260924-LOSS-DIVERGENCE-ASTRA.md` 는 이 지시서로 **대체**(자료 출처를 우리 경기 → DP 를 쓰는 8개 submission 경기로 바꿈). `20260924-PREFIX0-FAMILY-OPUS55.md` 는 발행하지 않고 그 Q4 를 아래 Q5 로 흡수.

**발행 2026-09-24 22:50 KST (Coordinator).** 수집 보고 `coordination/reports/antigravity/20260924-2155-DP-HOSTED-MAP.md` VERDICT PASS, Coordinator 가 원본 산출물로 재확인함. 아래 "수집 결과 반영" 이 본문보다 우선한다.

**재개 2026-09-25 00:45 KST (Coordinator).** 09-25 00:17 §11 반환 사유(BOARD 갱신일·FIFO 충돌)는 BOARD 09-25 00:40 갱신으로 해소. 같은 지시서로 재개한다.

## 09-25 추가 (사람 목표: 은 구간 도전 · DP 복제 확산 대비) — 카드 작성 전에 반영
- DP 는 공개 코드라 마감까지 복제가 늘어난다 → **DP 자신이 가장 큰 상대 계열이 될 수 있다.** 그래서 DP 상대 직접 대결을 이번에는 **필수 하한**으로 둔다 (예측치가 아니라 방어선):
  - 후보 vs DP 0924, seed 2400–2439 × 양 좌석 = 80경기, 점수율 **≥ 0.50** (미달이면 SUCCESS·B-2 모두 불가).
- 패널 결과와 함께 **DP 비중 시나리오** 표: field 에서 DP 계열 비중 = 현재(패널 추정) / 20% / 40% 일 때 기대 점수율 변화 (패널 재가중 + DP 직접 대결 점수율 혼합). 판정에는 쓰지 않고 보고만.

## 수집 결과 반영 (Coordinator 확인치 — 본문보다 우선)
- 헤더 884경기 (666-199-19), 다운로드 319경기 = 패배 199 전부 + 승리 **무작위 15/submission (120)**. → 승·패 비율이 field 와 다르다. field 수준 추정치는 submission 별로 승리 가중치 = (헤더 승 수 / 다운로드 승 수), 패배 가중치 = 1 로 **재가중**해서 낸다.
- **56502662 (Yusaku Muroya) 는 closed-loop 판정에서 제외**: 720 step 재현 2/3 (ep 112837776 step 300, hosted 는 `SELL MILK 6` 을 냈고 로컬은 안 냄). 같은 submission 이면 바이트가 같으므로 원인은 실행 환경 쪽(예: 모듈 전역 `_*_STATE` 가 경기 간 유지되는 경우) 가능성 — 확인되지 않음. Q1 에 쓰되 표시만.
- DP 승점률 (헤더 884경기, 상대 LB 점수 구간): <2200 0.92 · 2200–2400 0.73 · **2400–2600 0.56** · 2600–2800 0.22 · ≥2800 0.00. 09-24 만: ≥2600 상대 0-24. → DP 의 균형 레이팅은 약 2450~2550. **순위를 올리는 곳은 2400–2600 상대와 2200–2400 상대에게 진 경기**이고, 2600+ 사설 봇 패배(prefix 0, DSM·Majkel1337 등)는 우선순위 최하.
- closed-loop 가능한 경기(상대가 공개 파일과 720 전부 일치) = **59경기 (29패 30승)**. 이것이 Q4 패널 전부다. 작다 → 판정 SE 를 반드시 표에 쓴다.

## 분석 우선순위 (Q1 을 이 순서로)
1. **herd-safe-v3-experimental-risk-aware-feed FULL 일치 상대: DP 1승 15패.** 전부 closed-loop 재현 가능. 가장 먼저 본다. (사용 팀 LB 2240~2515, 중앙값 약 2340 — DP 팀들보다 낮다 = 상성 문제일 수 있음. field 비중과 함께 보고.)
2. **DP 와 step 143 까지 같은 상대 (label `DP-0924-exact|harvest-ledger`, MATCH_400 포함 약 17패)**: 누군가 DP 를 고친 변형일 가능성. 그 상대가 DP 와 처음 갈라지는 step·행동을 표로 — **그 차이 자체가 패치 후보**다 (open-loop, 상대 파일 미공개).
3. 상대 LB < 2400 에게 진 경기 (upset) 의 공통 패턴.
4. 나머지. 2600+ 사설 봇 패배는 표에 개수만.

## Q5 보정
herd-safe-v3 는 DP 를 15-1 로 이기지만 사용 팀 LB 가 DP 팀들보다 낮아 본문 Q5 조건(LB ≥ DP 팀들)을 못 넘는다. 추천하지 말고 "상성 상대"로 기록만. 다른 Y 후보 조건은 본문 그대로.

## 배경 (검증된 사실만)
- hosted 경기는 seed + 양쪽 행동으로 로컬에서 정확히 재현된다 (Opus 120/120, Antigravity 10/10).
- 로컬 직접 대결은 hosted 순위를 예측하지 못했다 (EXP-017 vs EXP-016 로컬 78-2 → hosted −165). → **검증은 hosted 복제 패널로 한다** (아래 Q4).
- DP 0924 에는 판매 앞당김 층(`_ADV_LOOK`)과 최종 판매 블록 재정렬이 이미 있다 → **같은 층을 다시 붙이지 않는다.**
- 대상 파일: `releases/public-tetsutani-demand-preserving-0924-exact/main.py` (178ae0f7…, 7,333줄, 마지막 callable `_final_sell_block_reorder_entrypoint`).

## 재료
`analysis/dp_hosted_20260924/` (episodes_all.json, opponents.csv, submission_verify.json, summary.json, file_hashes.json), raw `private_artifacts/dp_hosted_20260924/raw/*.json.gz`, 참조 파일 추출물 `analysis/daily_scan/2026092{2,4}/extracted/`, `tools/arena.py`, `tools/instrument.py`, `analysis/exp016_017_hosted_20260924/reproducibility.py`.

## 질문
**Q1. 패배 분류.** DP 패배 경기(거울·불일치 submission 제외)마다: 날짜 구간별(d0-11 / d12-18 / d19-29) 품목별 판매 수량·평균가, 땅·동물·고용 구매 시점, 구간 끝 cash 차. 이 차이가 **처음 벌어지는 구간과 그 결정**으로 패배를 묶어 표로 (묶음별 경기 수, margin 합, 상대 LB 점수 중앙값). 5경기 이상 반복되는 묶음만 후보.

**Q2. 반사실.** 상위 1~2 묶음에서 DP 의 그 결정 하나만 바꿔 끝까지 재생:
- 상대가 공개 파일과 720 step 전부 일치한 경기 → **closed-loop** (상대 = 그 파일, 같은 seed·좌석)
- 아니면 → **open-loop** (상대 행동 replay 고정). 근사임을 표에 따로 표시.
경기별 margin 변화, 뒤집힌 경기 수.

**Q3. 패치.** 효과가 가장 크고 반복되는 1개를 DP 0924 위의 **덧붙이는 변경**으로 (부모 바이트 수정 없음). 환경 제약 A-1: step ≤ 0.5초, 예외 0, 외부 파일·네트워크·환경변수 의존 없음. 설계 제약(줄 수·층)은 기본값만 — 넘으면 "초과 사유 + 기대 이득" 과 함께 보고.

**Q4. 검증 = hosted 복제 패널 (카드에 먼저 적고 실행).**
- 패널 = `opponents.csv` 중 상대가 공개 파일과 720 전부 일치한 경기 **전부**(패배 + 승리 기준선), 같은 seed·같은 좌석, 우리 자리에 부모 / 후보, 상대 자리에 그 파일.
- 보조 = open-loop 경기 (따로 보고, 판정에는 쓰지 않음).
- **사전 판정 (카드에 그대로):**
  - SUCCESS: 패널 점수율(후보 − 부모) > **2 × paired SE** 이고, 승리 기준선 경기에서 새로 지는 경기 ≤ 뒤집힌 패배 수의 1/3, 예외 0, 최대 step < 0.5초.
  - INCONCLUSIVE: 차 > 0 이지만 2 × SE 이하.
  - FAILURE: 차 ≤ 0, 또는 예외·시간 초과.
  - 참고치(판정에 안 씀): DP 상대 직접 대결 20경기 (seed 2300-2309 양 좌석).
- 슬롯 정책: SUCCESS 또는 CANDIDATE-POLICY B-2 충족 INCONCLUSIVE → 슬롯 B(현 EXP-017 자리) 후보. FAILURE 는 어떤 경우에도 제출 안 함.

**Q5. 다른 계열 (PREFIX0 흡수).** DP 에게 가장 많이 이긴 상대 계열 중 공개 exact 파일 Y 가 있고, DP 상대 closed-loop 성적이 좋고 그 팀들 LB 점수가 DP 팀들 이상이면 "슬롯 B exact 후보 Y" 로 추천 (경로·sha·마지막 callable). 없으면 "없음".

## 포기·수정 조건 (미리 정함)
- Q1 에서 5경기 이상 반복 묶음이 없으면 → Q2~Q4 생략, "패치 없음" 보고 후 Q5 만.
- Q2 에서 closed-loop 로 뒤집힌 경기가 3 미만이면 → 그 묶음 버리고 2순위 1회만 시도. 2순위도 같으면 "패치 없음".
- 같은 방향의 패치를 3번 넘게 조정하지 않는다.

## 산출물
- `coordination/reports/codex/<날짜>-DP-LOSS-CAUSE.md` — Q1 표, Q2 표, 추천 1개(또는 "없음"), Q5 결과, 끝줄 VERDICT.
- 카드 `experiments/cards/EXP-018-dp0924-<짧은이름>.md` (parent = DP 0924 178ae0f7, 위 사전 판정 그대로) — **패널 실행 전에** sha 기록.
- 추천이 있으면 release `releases/dp0924-<짧은이름>-exp018/` (main.py 한 파일, tar 안 sha = 추출 sha, 마지막 callable 기록, E-5 필수 gate 결과) + 패널 결과 `analysis/exp018_panel/`.
- 제출은 사람이 한다. FIFO: 다음 제출은 EXP-017 56490029 를 은퇴시킨다 (BOARD 에서 재확인).


---

## `proposals/claude/20260924-DP-LOSS-COLLECT-ANTIGRAVITY.md`

# 20260924 demand-preserving 0924 hosted 경기 수집 + 상대 지문 (Antigravity) — 최우선

발행: Claude (Coordinator), 2026-09-24 20:40 KST. 수신: **Antigravity** (Gemini 3.5 Flash · Medium). 실행 위치: 사람 Mac.
사람 승인 = 이 prompt 전송 (아래 8개 submission 의 hosted replay 다운로드, 상한 명시). **제출·원인 해석·코드 수정 금지.**
기한: **2026-09-25 09:00 KST**. 뒤이어 Codex 원인 분석(20260924-DP-LOSS-CAUSE-CODEX.md)이 이 산출물을 쓴다.

## 왜
우리 슬롯 56518910 = tetsutani demand-preserving 0924 exact (main 178ae0f7…). 같은 파일을 쓰는 다른 팀 submission 7개가 09-23~24 부터 hosted 경기를 치르고 있다(그 팀들 LB 중앙값 ≈ 2457 = 우리 목표 구간). 우리 봇의 24h 를 기다리지 않고, **이 파일이 목표 구간에서 누구에게 어떻게 지는지**를 지금 모은다.

## 대상 submission (같은 바이트로 추정 — 1단계에서 확인)
| 팀 | submission ID |
|---|---|
| Taisei_Tsuneki | 56486914 |
| wennan cao | 56488661 |
| yaya__k | 56481644 |
| Yusaku Muroya | 56502662 |
| Dzmitry Pihulski | 56506164 |
| 青葉 涼風 | 56506193 |
| haseryooooo | 56507682 |
| **우리 (Sian)** | **56518910** |
출처: `analysis/step91_id/result_chunk_*.json` 의 178ae0f7 match_full 경기 → `episodes_all.json` op_submissionId.

## 할 일
0. `as_of` = 작업 시작 시각(UTC) 을 고정해 기록. 이후 끝난 경기는 넣지 않는다.
1. **목록 + 결과 헤더**: 각 submission 에 `api.competition_list_episodes(sub_id)` → COMPLETED·endTime ≤ as_of 전부. 각 경기의 결과는 replay **헤더만** 읽어 얻는다 (`tools/compare_hosted_episodes.py` 의 `fetch_replay_header` 방식 — `"steps":` 전까지만 읽음). 기록: episode id, create/end time, 대상 submission, 좌석, 양쪽 reward, margin, W/L/D, 상대 teamId·teamName·submissionId.
2. **거울 제외**: 상대 submissionId 가 위 8개 중 하나면 `MIRROR_KNOWN` 표시하고 다운로드 대상에서 뺀다 (집계에는 따로 표시).
3. **다운로드 (전체 replay)**:
   - 패배: submission 별 **최신순 상한 60**
   - 승리: submission 별 **무작위 15** (random seed 20260924, 회귀 확인용 기준선)
   - 총 상한 600경기. 받은 즉시 gzip 저장 → `private_artifacts/dp_hosted_20260924/raw/<episode>.json.gz`. 디스크 여유 20GB 아래로 떨어지면 멈추고 BLOCKED.
4. **같은 파일인지 확인**: submission 별 3경기, DP 쪽 행동을 `releases/public-tetsutani-demand-preserving-0924-exact/main.py` 로 상대 행동 주입 재현(ReplayOpponent, `analysis/exp016_017_hosted_20260924/reproducibility.py` 방식) 했을 때 **720 step 전부 일치**하는지. 불일치 submission 은 표시하고 이후 집계에서 분리 (지우지 말 것).
5. **상대 지문** (step91_id 와 같은 방법: 경기별 match_143 / match_400 / match_full, 최장 prefix, 가장 가까운 파일):
   참조 = 20260924-1610 보고의 17종 + step91_id 후보 34종 (`analysis/daily_scan/2026092{2,4}/extracted/`) + DP 0924 자신 + 09-24 이후 스캔 추출물이 있으면 포함. 파일 목록과 sha 를 `file_hashes.json` 에.
6. **상대 LB 점수**: `kaggle competitions leaderboard kaggriculture --download` (또는 사람이 준 LB 스냅샷) 에서 teamId → 점수·순위. 스냅샷 시각 기록.
7. 출력 `analysis/dp_hosted_20260924/`:
   `episodes_all.json` (1단계 전체) · `opponents.csv` (다운로드한 경기: submission, episode, seed, dp_seat, result, margin, op_team, op_teamId, op_lb_score, label, prefix_len, match_143/400/full, closest_file) · `submission_verify.json` (4단계) · `summary.json` · `file_hashes.json`.

## 보고 `coordination/reports/antigravity/<ts>-DP-HOSTED-MAP.md`
- submission 별 전체 W/L/D (헤더 기준, 거울 분리) 와 **12시간 단위 승률**
- 4단계 결과 (submission 별 3/3 일치 여부)
- label 별 경기 수·W/L (다운로드분, 8개 합산 + submission 별)
- **DP 에게 이긴 상대 상위 15** (팀명, teamId, LB 점수, DP 상대 W-L, label, 최장 prefix·가장 가까운 파일)
- 패배 margin 분포 (사분위, −1000 미만 건수)
- 끝줄 `VERDICT | … | 산출 파일 sha256 | 방법 한 줄 | NEXT ACTION`. **원인 추정 금지.**

## 멈춤 조건 (추측하지 말고 BLOCKED 로 보고)
- API 인증·권한 오류, 헤더 파싱 실패 10% 초과, 4단계에서 8개 중 3개 이상 불일치, 디스크 부족.


---

## `proposals/claude/20260924-EXP016-017-HOSTED-MAP-ANTIGRAVITY.md`

# 20260924 EXP-016 / EXP-017 hosted 경기 수집 + 상대 지문 (Antigravity) — 최우선

사람 승인 = 이 prompt 전송 (두 submission 의 hosted replay 다운로드, 각 상한 200). 제출·해석 금지.

## 왜
EXP-016 2425.7 → 2265.8 (하루 −160), EXP-017 2100.2. 로컬에서는 EXP-017 이 EXP-016 을 78/2 로 이겼는데 hosted 는 반대다. 누구에게 지는지 모르면 다음 결정을 할 수 없다. 두 연구(codex-astra, Opus 5.5)도 이 자료(E-2 가중치)가 없어 BLOCKED 이다.

## 할 일 (20260921-C1-HOSTED-OPPONENT-MAP-ANTIGRAVITY.md 와 같은 방법)
1. 56458814, 56490029 각각: PUBLIC·COMPLETED·endTime ≤ as_of 전부 목록 → replay 최신순 상한 200. 결과·상대 팀·seed·좌석·양쪽 reward·**경기 시각** 기록.
2. 재현성 대조 5경기 (우리 쪽 step 1–143 일치) — 실패하면 지문 단계 BLOCKED.
3. 지문 참조 파일 (step 1–143 완전 일치, 720 전체 일치는 MIRROR_EXACT):
   C1 pipe16, C2 v13, C3 2945 Farm, C4 V53, C5 V51, P2, OMW, dmitriigluzdov more-wheat-smarter-sales, 7-turn-rescue, a-smaller-market-shock, EXP-016, EXP-017, 그리고 09-22·09-23 스캔에서 SAME_FAMILY 로 새로 들어온 파일 중 추천 수 상위 5개.
4. 출력: `analysis/exp016_017_hosted_20260924/` (episodes_all.json, opponents.csv, summary.json, file_hashes.json), raw 는 `private_artifacts/exp016_017_hosted_20260924/raw/`.
5. 보고 `coordination/reports/antigravity/<ts>-EXP016-017-HOSTED-MAP.md`:
   - submission 별 W/L/D, **시간대별(12시간 단위) 승률** — 하락이 언제 시작됐는지
   - label 별 경기 수와 W/L/D (두 submission 따로), UNKNOWN 은 prefix 길이·가장 가까운 파일별로
   - UNKNOWN 중 **우리에게 이긴 상대 팀 상위 10** (팀명, 경기 수, 그 상대의 최장 일치 파일·prefix)
   - VERDICT 한 줄. 원인 추정 금지.


---

## `proposals/claude/20260924-LOSS-DIVERGENCE-ASTRA.md`

# 20260924 hosted 패배의 첫 결정 차이 (codex-astra) — 패배에서 출발하는 좁은 질문

기한: **2026-09-25 18:00 KST**. 금지: 제출, Kaggle 다운로드, releases/ 편집. 허용: 이미 받은 hosted replay·로컬 재현·analysis/ 스크립트.
배경: hosted 경기는 기록된 양쪽 행동 + seed 로 로컬에서 정확히 재현된다 (Opus 120/120, Antigravity 10/10).

## 재료
- `analysis/exp016_017_hosted_20260924/opponents.csv`, `episodes_all.json`, raw `private_artifacts/exp016_017_hosted_20260924/raw/`
- 경기별 상대 파일 판정: `analysis/step91_id/result_chunk_*.json` (per_episode match_full), 요약 `analysis/step91_id/full_match_teams_claude.json`
- 상대 파일: `releases/public-tetsutani-demand-preserving-0924-exact/main.py` (178ae0f7, 우리 0-7), V57 `analysis/daily_scan/20260924/extracted/kaggriculture-v57-funding-order-invariant/main.py` (우리 2-6), V56 release (우리 17-9)

## 질문
Q1. 우리가 **진** 경기 중 상대가 한 공개 파일과 720 step 전부 일치한 경기(demand-preserving 7, V57 6 등)에서, 우리와 상대의 **판매 행동이 처음 달라지는 step** 과 그 내용(품목·수량·주문 순서), 그 시점부터 끝까지의 cash 차 변화를 표로.
Q2. 그 차이를 반사실로 잰다: 상대 행동은 replay 그대로 고정하고, **우리 쪽 그 한 결정만** 상대가 한 방식으로 바꿔 끝까지 재생했을 때 최종 cash 차. (우리 정책이 이후 반응하는 경우와 행동을 그대로 두는 경우 둘 다 가능하면)
Q3. Q2 에서 효과가 가장 크고 여러 경기에 반복되는 차이 1~2개를, 대상 파일 = **demand-preserving 0924(178ae0f7)** 위의 덧붙이는 변경으로 표현할 수 있는지. 환경 제약(A-1) 준수 여부.
Q4. 반대 방향: 우리가 **이긴** V56 경기에서 V56 이 무엇을 놓쳤는지 1~2줄 (demand-preserving 도 같은 약점이 있는지 코드로 확인).

## 산출물
`coordination/reports/codex/<날짜>-LOSS-DIVERGENCE.md` — 표 + 추천 1개(없으면 "없음") + 카드 초안(parent = demand-preserving 0924, seed 2400-2439, 상대 = demand-preserving·V57·V56·EXP-017, success 는 CANDIDATE-POLICY E-2/E-3 기준).


---

## `proposals/claude/20260924-PREFIX0-FAMILY-OPUS55.md`

# 20260924 "step 1 부터 다른 계열" 식별과 슬롯 B 판단 (Opus 5.5)

기한: **2026-09-25 18:00 KST**. 금지: 제출, Kaggle 다운로드(필요하면 BLOCKED + 목록), releases/ 편집, BOARD·KILLS·HYPOTHESES 직접 수정.

## 왜
최종 순위 = 두 봇 중 높은 쪽. 슬롯 A 후보는 OMW 계열(demand-preserving 0924)이다. 슬롯 B 에는 **메커니즘이 다른** 후보가 필요하다.
hosted 지도에서 EXP-016 은 참조 17종 어느 것과도 step 1 부터 다른 상대(prefix 0)에게 36경기 10승 26패, EXP-017 은 30경기 22승 8패였다. 이 안에 강한 다른 계열이 섞여 있을 수 있다.

## 재료
- `analysis/exp016_017_hosted_20260924/opponents.csv` (prefix_len=0 경기), raw replay, `episodes_all.json` (op_teamId)
- 09-22·09-24 스캔 추출물 전부 (`analysis/daily_scan/2026092{2,4}/extracted/`), DIFFERENT 목록 `analysis/daily_scan/20260924/different.json`
- 너의 09-23 보고 `coordination/reports/claude/20260923-NEW-GAIN-OPUS55.md` (DSM 분석, K1/K9 충돌)

## 질문
Q1. prefix 0 경기의 상대를 **행동으로 묶어라** (step 1 행동, 첫 BUY_LAND 시점, 동물 구성, opening 작물). 묶음별 경기 수·우리 W/L·상대 팀 LB 점수(teamId 로; 브라우저 LB API 는 사람에게 요청해도 됨).
Q2. 가장 강한 묶음이 공개 파일(스캔 추출물) 중 무엇과 일치하는가 (step 1–143 완전 일치). 없으면 가장 가까운 파일과 차이.
Q3. 그 묶음이 **4번째 땅 구매**(K1)나 shop 에 맞춘 생산을 하는가 — DSM 과 같은 부류인지.
Q4. 슬롯 B 판단: 식별된 파일 Y 가 (a) 공개 exact 로 존재하고 (b) 환경 제약 A-1 을 지키고 (c) 우리 상대 hosted 성적이 좋으면 "슬롯 B exact 후보"로 추천. 아니면 "없음"과 이유.

## 산출물
`coordination/reports/claude/<날짜>-PREFIX0-FAMILY-OPUS55.md` — 묶음 표 + 추천(Y 경로·sha·마지막 callable) 또는 "없음".


---

## `proposals/claude/20260924-STEP91-BOT-ID-ANTIGRAVITY.md`

# 20260924 hosted 최대 상대군 "step 91 봇" 식별 (Antigravity) — 최우선

제출 금지. 다운로드 없음 (이미 받은 replay·스캔 추출물만 사용).

## 왜
EXP-016/017 hosted 345경기 중 137경기가 step 1–91 은 OMW 계열과 같고 step 92 에서 갈라지는 봇이다 (EXP-017 상대 10승 27패).
Claude 확인: step 92 에서 OMW 의 `["SELL","WHEAT",3]` 을 하지 않는다. 그 뒤 차이는 모른다.

## 할 일
1. 참조 파일 = `analysis/daily_scan/20260922/extracted/*/main.py` 와 `analysis/daily_scan/20260924/extracted/*/main.py` 중 `_CL_INSTALL` 이 들어 있는 파일 전부 (CRLF 제거 후 sha 로 중복 제거, 약 35종) + multi-file 패키지는 패키지 통째.
2. `analysis/exp016_017_hosted_20260924/opponents.csv` 의 prefix_len=91 경기 **전부**에 대해, 지난번과 같은 방법(같은 seed·좌석, 우리 자리엔 실제 우리 파일, 상대 자리에 참조 파일)으로 상대의 **step 1–400** 행동 일치 길이 측정. 720 전체 일치면 FULL.
3. 표: 참조 파일별 (143 일치 경기 수, 400 일치 경기 수, FULL 경기 수). 가장 많이 FULL/400 일치한 파일 = X.
4. X 가 정해지면:
   - release `releases/public-<owner>-<slug>-exact/` (main.py 원본 바이트, `COPYFILE_DISABLE=1 tar --no-xattrs`, tar 안 main.py sha 대조), 마지막 callable, LICENSES 행.
   - E-5 최소 gate: 외부 파일/네트워크/환경변수 의존 여부, 예외, 최대 step 시간.
   - 빠른 대전: X vs EXP-016(`releases/f0-c1-adv-exp016`), X vs EXP-017(`releases/f0-omw-adv-exp017`), 각 seed 2300–2309 × 양 좌석 = 20경기.
5. 보고 `coordination/reports/antigravity/<ts>-STEP91-ID.md`: 참조 표, X 의 notebook·버전·sha·마지막 callable, gate 결과, 대전 W/D/L·평균 margin·예외·최대 step 시간, VERDICT 한 줄. 해석·제출 금지.

## 추가 (09-24 19:00 KST) — 두 번째 상대군 "prefix 0 봇"
EXP-016 은 참조 17종 어느 것과도 step 1 부터 다른 상대(prefix 0)에게 36경기 10승 26패였다. 계열이 완전히 다른 봇일 수 있다 (슬롯 B 후보).
6. prefix_len=0 경기 전부(두 submission)에 대해, 참조 파일을 **09-24 스캔의 DIFFERENT 4종**(visualized-what-every-crop-pays, getting-started, multi-route-farming-agent, graph-reinforcement-learning) + 09-22 DIFFERENT 전부 + 09-24 SAME_FAMILY 중 `_CL_INSTALL` 이 **없는** 파일로 넓혀 같은 방식(step 1–143)으로 지문.
7. 보고서에 표 하나 추가: prefix 0 경기의 참조 파일별 143 일치 수, 일치 파일이 없으면 상대 팀 상위 10과 그 상대의 step 1 행동 요약(farmer·hands·market 그대로).
8. prefix 0 에서 파일 Y 가 식별되면 X 와 같은 절차(release, gate, 빠른 대전: Y vs X, Y vs EXP-016, 20경기씩).


---

## `proposals/claude/20260925-CALIBRATION-REVIEW-PROMPT.md`

# 독립 검토 요청 — Kaggriculture 자동 탐색의 "채점 기준(metric) calibration" 이 목표에 최선이고 타당한가

당신은 이 작업에 참여하지 않은 **독립 검토자**다. 아래 설명과 이전 결론을 믿지 말고, 원자료와 코드로 직접 확인하라. 찬성 논거를 모으기보다 **이 방법이 틀리게 되는 경로**를 먼저 찾아라. 파일은 사람 Mac 의 `~/kaggle/Kaggriculture` (연결되면 `$HOME/mnt/Kaggriculture`). **파일을 수정하지 말고, 제출·Kaggle 다운로드·holdout(seed 9000–9599, `experiments/search_20260925/tape-holdout-policy.json` 의 CP1/CP2 episode) 사용을 하지 마라.** 전문용어는 영어 그대로 써라.

## 1. 목표와 상황
- Kaggle 시뮬레이션 대회 Kaggriculture (2인 농장 경제 게임, 720 step). 최종 순위 = 활성 봇 2개 중 높은 쪽의 hosted Bradley-Terry rating. 제출 마감 09-30 23:59 UTC, 신규 전략 마감 09-27 00:00 KST.
- 목표: **동메달 복귀 (경계 약 2290)**. 현재 활성: DP 0924 공개 파일 56518910 (2191.6), 127ed3e6 공개 파일 56549720 (09-25 제출, 초기 2165.6). 사람 방침: 두 슬롯 모두 공개 최고 봇을 넘는 개선 모델로 교체한다.
- 방식: Mac(M3, 6 worker) 무인 루프가 부모(127ed3e6 과 행동이 같은 e496a4fe)의 상수 ±1단계·덧붙은 층 끄기 변형 약 150개를 successive halving(40→120→400→1,000 경기)으로 걸러, checkpoint(CP1 09-26 21:00 KST, CP2 09-28 21:00 KST)마다 1개를 disjoint holdout 으로 확인한다. **변형의 순위를 매기는 자(metric)** 를 calibration 으로 먼저 고르고 동결한다.

## 2. 검토 대상 (calibration 설계)
정본: `coordination/proposals/claude/20260925-SEARCH-LOOP-CODEX.md` §2단계, 코드 `tools/search_calibration.py` (`_calibrate`, `public_pool`, `weights`, `tape_metric`), 정책 `experiments/search_20260925/calibration-policy.json`, 결과가 나오면 `calibration-summary.json` · `coordination/reports/codex/*METRIC-CALIBRATION*.md`.
- metric = 상대 풀에 대한 가중 점수율 (승 1, 무 0.5), paired seed 2600–2619 × 양 좌석.
- 상대 풀 = 09-22~25 공개 scan 고유 파일 + DP + 127ed3e6, 잠정 부모에게 95% 이상 지는 상대 제외.
- 후보 자 4개: (a) 127ed3e6 30%·DP 15%·나머지 55% (b) 50/15/35 (c) 균등 (d) 0.6×(a) + hosted replay tape 패널(상대 팀 LB 2200–2400 15%, 2400–2600 15%, 2600+ 10%; open-loop 편향 방향 일치율 ≥ 0.70 일 때만).
- **판정**: 우리 과거 submission 중 같은 시기에 동시에 활성이던 5쌍의 hosted 순서를 맞히는지 — C1(2206.6) < EXP-016(2425.7) · EXP-017(2100.2) < EXP-016(2265.8) [필수, 로컬 78-2 로 뒤집혔던 쌍] · EXP-017(2010.8) < DP(2191.6) · yhay81-exact(1483.8) < P2(2421.6) · EXP-007 < EXP-006. 5쌍 중 4쌍 이상 + 필수 쌍 → 통과. 통과한 것 중 **127ed3e6 비중이 큰 쪽** 채택. 모두 실패하면 BLOCKED.
- 알려진 사정: 탐색 코드는 (d) 가 뽑히면 아직 채점을 지원하지 않아 멈춘다. 공개 파일 복사본이 hosted 에서 흔들린 전례(같은 바이트 yhay81 이 2188 → 1515).

## 3. 답해야 할 질문 (각각 결론 + 근거 파일·줄 또는 계산)
1. **판별력**: 5쌍·4/5 기준이 좋은 자와 나쁜 자를 가려내는가? 무작위 자가 통과할 확률, 쌍 사이 점수 차 크기, 쌍들이 서로 독립인지(같은 봇이 여러 쌍에 등장) 계산하라.
2. **해상도 불일치**: calibration 쌍들은 수백 점 차이 나는 서로 다른 봇들이다. 탐색이 가려야 하는 것은 127ed3e6 의 미세 변형 간 몇십 점 차이다. 큰 차이를 맞히는 자가 작은 차이도 올바르게 정렬한다는 근거가 있는가? 없다면 무엇으로 보완해야 하는가?
3. **대표성**: 상대 풀(공개 파일)과 hosted 실제 상대 분포(사설 상위 봇 포함, 우리 목표 구간 2200–2600)가 얼마나 다른가? 95% 필터가 목표 구간의 상대를 빼 버리지는 않는가?
4. **선택 규칙**: 통과한 자들 중 "127ed3e6 비중이 큰 쪽"을 고르는 규칙이 타당한가, 더 나은 규칙(예: 쌍 margin 적합도, rank correlation)이 있는가?
5. **과적합·누설**: 필수 쌍, 가중치 후보, 통과 기준이 결과를 본 뒤 정해진 흔적이 있는가? holdout 과 탐색 seed 가 섞일 경로가 있는가?
6. **대안**: 남은 시간(약 3일, Mac 1대 ≈ 1,700 경기/시간) 안에서 동메달 확률을 더 올릴 calibration/채점 방식이 있다면 구체적으로 (비용·기대효과·위험) 제시하라. "현 방식 유지"도 정당한 결론이다.
7. **폐기 조건**: 어떤 관측이 나오면 이 metric 을 버려야 하는지 사전에 정의하라 (예: CP1 후보가 holdout 은 통과했는데 hosted 에서 부모보다 낮음).

## 4. 출력 형식
- 첫 줄: 판정 한 줄 (타당 / 조건부 타당 / 부적절) + 이유 한 문장.
- 질문 1–7 각각: 결론, 근거(파일:줄·명령·계산), 확신도(높음/중간/낮음).
- 권고 변경 목록: 우선순위, 구체적 수정 내용, 루프를 멈추지 않고 적용 가능한지.
- 마지막: 다음 행동 2개, 사람이 가져야 할 질문 2개.


---

## `proposals/claude/20260925-DP-RATING-CHECK-ANTIGRAVITY.md`

# 20260925 DP 계열 실제 레이팅 확인 (Antigravity) — 최우선, 짧은 작업

발행: Claude (Coordinator), 2026-09-25 14:10 KST. 수신: **Antigravity** (Gemini 3.5 Flash · Low). 실행 위치: 사람 Mac.
사람 승인 = 이 prompt 전송. **replay 다운로드 금지 (경기 목록 API 만)**. 제출·해석 금지. 기한: **2026-09-25 17:00 KST**.

## 왜
우리 DP 56518910 은 2191.6 인데, 09-24 추정(2450~2550)은 상대 강도를 "팀 LB 점수"(팀 최고 봇)로 쟀다. 실제로 그 경기에서 만난 submission 의 레이팅이 필요하다. 경기 목록 API 의 agent 항목에는 submission 별 점수(initialScore/updatedScore 등)가 들어 있다.

## 할 일
1. `as_of` = 시작 시각(UTC) 기록.
2. 아래 8개 DP submission 각각 `api.competition_list_episodes(sub_id)` → COMPLETED·PUBLIC 전부. **각 episode 의 `to_dict()` 원문을 그대로 저장** (agents 배열 전체 — submissionId, reward, index, initialScore, updatedScore 등 API 가 주는 모든 필드).
   56486914, 56488661, 56481644, 56502662, 56506164, 56506193, 56507682, **56518910 (우리)**
3. 우리 두 활성 submission 도 같은 방법: **56518910, 56490029**.
4. `kaggle competitions leaderboard kaggriculture --download` 로 현재 LB (스냅샷 시각 기록).
5. 출력 `analysis/dp_rating_20260925/`: `episodes_raw.json` (2~3단계 원문), `leaderboard_<ts>.csv`, `summary.json`.
6. 보고 `coordination/reports/antigravity/<ts>-DP-RATING-CHECK.md`:
   - agent 필드 이름 목록 (API 가 실제로 준 키 그대로)
   - submission 별: 경기 수, **가장 최근 경기의 해당 submission 점수**, 시간순 점수 추이(6시간 간격 표)
   - 경기별 **상대 submission 의 그 경기 당시 점수**가 있으면: DP 승점률을 상대 점수 구간(<2000, 2000–2200, 2200–2400, 2400–2600, ≥2600)별로 (8개 합산, 우리 따로)
   - 현재 LB: 1위, 100위, 200위, 500위, 동메달 경계(총 팀 수 × 10% 순위) 점수, 우리 순위
   - VERDICT 한 줄. 원인 추정 금지.

## 멈춤 조건
agent 항목에 점수 필드가 아예 없으면 → 필드 목록만 보고하고 BLOCKED (다른 방법을 추측하지 말 것).

## 추가 (09-25 14:45 KST) — 이미 시작했으면 끝난 뒤 이어서
7. `analysis/dp_hosted_20260924/fingerprint.py` 방법 그대로, 참조에 `analysis/daily_scan/20260925/extracted/demand-preserving-turn-sale-timing/main.py` (sha 127ed3e6…) 와 `.../kaggriculture/main.py` (e496a4fe…) 를 **추가**해 319경기 상대 지문을 다시 계산. 진입점은 파일 끝 `kaggle_agent = cha20_entry_agent` 기준(마지막 callable 규칙)으로, 잘 모르겠으면 `ig_agent` 와 둘 다 시도해 일치 수를 각각 보고.
   - 보고: 127ed3e6 과 match_full / match_143 인 경기 수, 그 경기들의 DP W/L, 상대 팀.
   - 출력 `analysis/dp_rating_20260925/refingerprint_127ed3e6.json`.


---

## `proposals/claude/20260925-EXP019-DP-SECOND-FACTOR-CODEX.md`

# 20260925 EXP-019 — DP 위 두 번째 단일 변경 (Codex) — 판단 작업

발행: Claude (Coordinator), 2026-09-25 14:15 KST. 수신: **Codex** (최상위 모델 · reasoning high). 사용량이 막히면 Claude 새 채팅(Opus 5.5)에서 같은 지시로.
기한: **2026-09-26 21:00 KST** (결과·release). 금지: 제출, Kaggle 다운로드, BOARD·KILLS·HYPOTHESES 직접 수정, 카드 기준 사후 변경, 결과를 보고 seed 추가.
선행 자료: `coordination/reports/codex/20260925-1340-DP-LOSS-CAUSE.md` (EXP-018), `experiments/results/dp_loss_cause_20260925/`, `analysis/exp018_panel/`, freeze `experiments/results/dp_loss_cause_20260925/freeze.json`.

## 왜
DP 56518910 hosted 2191.6 (동메달 경계 2289.7 아래). EXP-018(refresh 3→2)은 패널 +5승·새 패배 0 이었지만 DP 하한 0.4875 로 미채택. 슬롯 B 는 EXP-017(2010.8)이 차지하고 있어 사실상 비어 있다. 09-27 00:00 KST 신규 전략 마감 전에 **다른 방향 하나**를 더 시험한다.

## 후보 (각각 DP 0924 부모 위 단일 변경, 이 순서로)
- **F1 이른 WOOL 판매**: EXP-018 Q1 의 DP-prefix 첫 분기 16건 중 5건(112493607, 112694693, 112717208, 112795924, 112830224)에서 DP 변형 상대가 step 150–160 무렵 DP 가 팔지 않는 `SELL WOOL 2` 를 냈다. DP 의 WOOL 판매 조건 중 어느 값이 이 차이를 만드는지 코드로 찾아, 그 값 하나만 바꾼다.
- **F2 carrot 전환 margin −5 → −15**: EXP-018 에서 사전 고정된 2순위(미실행).
F1 이 Q2 기준을 못 넘으면 F2. 둘 다 못 넘으면 "없음".

## 절차 (EXP-018 과 같은 도구·같은 패널)
1. **Q2 (선택용)**: 후보 변경이 영향을 주는 closed-loop 패배를 사전 고정 목록으로 정하고 실행. strict 패→승 ≥ 3 이면 통과.
2. **카드** `experiments/cards/EXP-019-dp0924-<짧은이름>.md` — 아래 판정을 그대로 적고 **패널 실행 전 SHA 기록**.
3. **Q4 판정** (유효 패널 47경기 = EXP-018 과 같은 목록, 56502662 제외 유지):
   - SUCCESS: 패널 점수율 Δ > 2 × paired SE, 기존 승리 새 패배 ≤ 뒤집힌 패배의 1/3, 예외 0, 최대 step < 0.5초, **DP 직접 80경기(seed 2400–2439 × 양 좌석) 점수율 ≥ 0.45**.
   - INCONCLUSIVE: Δ > 0 이고 나머지 조건 충족, 2SE 이하.
   - FAILURE: 그 외.
   - DP 하한을 0.50 → 0.45 로 둔 이유(이 카드에 적을 것): DP-vs-DP 는 무승부가 많은 거울 대결이고(EXP-018 80경기 중 34무), 재가중 field 의 DP 비중은 1.7~3.8% 다. 하한의 목적은 "DP 복제에게 확실히 지지 않는 것"이며 0.45 는 EXP-018 의 paired SE(0.058) 약 1배 아래다.
4. **조합 (SUCCESS 또는 INCONCLUSIVE 일 때만)**: EXP-018 의 `_V92_P_EVERY = 2` 와 이번 변경을 함께 덧붙인 조합 C 를 만들어 **같은 패널 47 + DP 80** 을 돌려 보고 (조합의 판정 기준은 3번과 동일, 카드에 미리 적음).
5. release: SUCCESS/INCONCLUSIVE 인 것 중 조합 C 우선, 없으면 단일 후보. `releases/dp0924-<이름>-exp019/` (main.py 한 파일, tar 안 sha = 추출 sha, 마지막 callable 기록, E-5 필수 gate).

## 한계 (보고서에 명시)
패널은 EXP-018 선택에도 쓴 개발 자료다. 새 holdout 이 없으므로 hosted 우위 증명이 아니다.

## 산출물
`coordination/reports/codex/<날짜>-EXP019.md` — Q2 표, 패널·DP 표, 조합 결과, 추천 1개 또는 "없음", VERDICT. 제출은 사람이 한다 (FIFO: 다음 제출은 EXP-017 을 은퇴시킨다).


---

## `proposals/claude/20260925-EXP020-NEWMETA-127ED3E6-CODEX.md`

# 20260925 EXP-020 — 새 공개 주류 파일 127ed3e6 평가 (Codex) — **EXP-019 보다 우선**

발행: Claude (Coordinator), 2026-09-25 14:45 KST. 수신: **Codex** (최상위 모델 · reasoning high). 막히면 Claude 새 채팅(Opus 5.5).
기한: **2026-09-26 12:00 KST**. 금지: 제출, Kaggle 다운로드, BOARD·KILLS·HYPOTHESES 직접 수정, 사후 기준 변경.
EXP-019 (`20260925-EXP019-DP-SECOND-FACTOR-CODEX.md`) 는 이 작업이 끝날 때까지 **보류** (이미 시작했으면 현 단계에서 멈추고 기록).

## 왜
- 09-25 일일 scan: 추천 수 상위 notebook 4개 — `guruprasaathas111/kaggriculture-master-engine-v3` (115), `flexonafft/kaggriculture-multi-route-farming-agent` (110), `tetsutani/demand-preserving-turn-sale-timing` **새 버전** (88, 09-24 16:06 UTC), `abhinav0370/cha22-agent` (77) — 가 **같은 바이트** `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652` (7,482줄, CRLF). `kaggriculture` (59) 는 끝 개행만 다른 `e496a4fe…`.
- 우리 DP 0924 (178ae0f7, 2191.6) 와 약 850줄이 다르다. 이 파일은 마감까지 가장 많이 복제될 가능성이 크다 → (a) 슬롯 후보이고 (b) DP 의 가장 큰 상대가 된다.
- 지금까지 +100 이상 이득은 모두 "더 강한 공개 파일로 교체"에서 나왔다 (C1→EXP-016 +219). 단일 줄 패치(EXP-018)의 기대는 +20 안팎이다.

## 재료
`analysis/daily_scan/20260925/extracted/{demand-preserving-turn-sale-timing,kaggriculture-master-engine-v3,cha22-agent,kaggriculture-multi-route-farming-agent,kaggriculture}/main.py`, EXP-018 도구·freeze·패널 (`tools/dp_counterfactual.py`, `experiments/results/dp_loss_cause_20260925/freeze.json`, `analysis/exp018_panel/`).

## 할 일
0. **진입점 확인**: 파일 끝이 `kaggle_agent = cha20_entry_agent` 다. scan 은 마지막 def 를 `ig_agent` 로 적었다. 엔진이 실제로 호출하는 callable(FACTS 09-20 "마지막 callable" 규칙)이 무엇인지 확인하고, 그 callable 로 실행한다. CRLF 는 그대로(바이트 exact).
1. **release** `releases/public-newmeta-127ed3e6-exact/` — main.py 한 파일 exact, tar 안 sha = 127ed3e6, E-5 필수 gate (외부 파일·네트워크·환경변수 의존, 예외 0, 최대 step < 0.5초). `environment/LICENSES.md` 행.
2. `tools/dp_counterfactual.py` 에 **임의 candidate 경로**를 받는 옵션을 추가 (기존 refresh/carrot 결과 재현이 바뀌지 않음을 테스트로 확인).
3. **카드** `experiments/cards/EXP-020-newmeta-127ed3e6.md` (parent = DP 0924 178ae0f7) — 아래 판정, 실행 전 SHA 기록.
4. 실행:
   - 유효 hosted 복제 패널 47경기 (EXP-018 과 같은 목록, 우리 자리 = 127ed3e6, 상대 = 그 경기 공개 파일)
   - **127ed3e6 vs DP 0924 직접 80경기** (seed 2400–2439 × 양 좌석)
   - **127ed3e6 vs EXP-018 refresh 80경기** (같은 seed) — 참고
5. **사전 판정**
   - SUCCESS (슬롯 후보): 패널 점수율 − DP 패널 점수율 > 2 × paired SE **그리고** DP 직접 ≥ 0.55, 예외 0, 런타임 충족.
   - INCONCLUSIVE: 패널 Δ > 0 이고 DP 직접 ≥ 0.50.
   - FAILURE: 그 외.
   - DP 직접 비중을 높게 두는 이유(카드에 기록): 이 파일이 field 에 퍼지면 "DP 대 127ed3e6" 이 곧 field 대결이 된다.
6. 보고 `coordination/reports/codex/<날짜>-EXP020.md` — 진입점, gate, 패널 표(47, 승리 재가중 포함), 직접 대결 2종, 판정, VERDICT. 제출은 사람.


---

## `proposals/claude/20260925-EXP021-MIRROR-EDGE-CODEX.md`

# EXP-021 MIRROR-EDGE — 127ed3e6 복제본을 이기는 가설 변형 사전등록 카드 (Codex)

발행: Claude, 2026-09-25 23:55 KST. **사람 지시(09-25 23:31)**: 127ed3e6 을 이기는 가설 변형 3–5개의 사전등록 카드를 작성해 Codex 에 넘긴다. 사람 결정(같은 시각): **이 카드의 결과를 제출하면 DP 0924(56518910)를 비운다.** 현재 FIFO 는 ① DP → ② 127ed3e6 이므로 다음 제출이 DP 를 자동으로 은퇴시킨다(BOARD 로 재확인).
수신: **Codex**. 실행: 사람 Mac.
금지: 제출, Kaggle 다운로드, holdout(seed 9000–9599, CP1/CP2 tape episode), BOARD·KILLS·HYPOTHESES 직접 수정, 탐색 루프 파일(`experiments/search_20260925/*`) 쓰기, 결과를 본 뒤 기준 변경.

## 왜
- 127ed3e6 은 09-25 기준 공개 주류(4개 파일)다. hosted 복제본은 늘어날 것이다(사람 판단, 전제로 받아들임).
- **복제본은 로컬 평가가 hosted 를 정확히 대표하는 유일한 상대**다. 같은 코드이므로 closed-loop 결과가 hosted 결과와 같고, seed 분포만 다르다.
- 로컬 부모(e496a4fe) vs 127ed3e6 은 40경기 중 38무다(`calibration-pool.json`). 엔진은 per-unit lockstep 으로 두 플레이어에게 같은 가격을 매긴다(`kaggriculture.py:_process_market` 544–628). 그래서 복제본끼리는 대칭이고, **대칭을 먼저 깨는 쪽이 이긴다.**
- 127ed3e6 은 이미 복제본 감지 로직을 갖고 있다(`main.py` 5431–5530).
  - 첫 턴 뒤 현금이 같으면 mirror 로 보고 sale reservation horizon 을 24 로 올린다(`_RACE_HORIZON_MIRROR=24`).
  - clone 으로 판단하면 8, 경주에서 지면 24(`_RACE_HORIZON_ESCALATED`)를 쓴다.
  - 최종 턴(step ≥ 718)에는 shed 전량을 판다(`LAST_ACT_STEP=718`, `_terminal_liquidation`).
  - 즉 **양쪽이 똑같은 선매 규칙**을 쓴다. 아래 가설은 모두 이 대칭을 우리 쪽으로 기울이는 것이다.

## 부모와 대상
- 부모 P: `analysis/daily_scan/20260925/extracted/kaggriculture/main.py` (e496a4fe). 127ed3e6 exact 와 **마지막 줄바꿈만 다르다**(`diff` 확인). 부모 바이트는 수정하지 않고 끝에 wrapper 를 덧붙인다(`build_variant` 방식).
- 주 상대 O: `releases/public-newmeta-127ed3e6-exact/main.py` (hosted 56549720 과 같은 파일).
- 참고: 127ed3e6 이 runtime 으로 부모 후보에서 빠진 것(최대 step 0.75초)은 **같은 코드인 e496a4fe 에도 해당하는 위험**이다. 이 카드의 runtime gate 는 모든 경기에서 잰다.

## 가설 (5 arm, 각각 독립 변형)
| id | 가설 | 구현 (wrapper) | 발동 조건 |
|---|---|---|---|
| **H1a** | mirror 상대보다 더 일찍 선매하면 선매 경주에서 이긴다 | `_RACE_HORIZON_MIRROR = 32` | step 1 현금 동일(mirror 감지)일 때만 |
| **H1b** | 같은 가설, 더 큰 폭 | `_RACE_HORIZON_MIRROR = 40` | 같음 |
| **H2** | 상대의 mirror 감지를 피하고 우리만 mirror 모드에 들어가면, 상대는 horizon 8, 우리는 24 로 비대칭이 된다 | step 0 action 에서 첫 SELL 한 주문의 수량을 1 줄여 첫 턴 현금을 1단위 가격만큼 다르게 만든다. 우리 쪽 mirror 감지는 "상대 현금 = 우리 현금 + 포기한 단위의 step 0 quote 가격(±0.5)"으로 바꾸고, 참이면 부모의 step 1 처리 직후 `_RACE_STATE[player]['level']=24` 로 설정한다 | step 0 은 모든 상대에게 적용된다(비용 발생). mirror 모드는 감지 시에만 |
| **H3** | 상대가 경주에서 진 뒤 올리는 horizon(24)보다 우리 escalated horizon 이 길면 escalated 경주에서도 이긴다. 같은 route tape 계열(hosted 상위권)에도 효과가 있을 수 있다 | `_RACE_HORIZON_ESCALATED = 32` | clone 감지 후 race-lost 가 일어났을 때. 복제본이 아닌 같은 계열 상대에도 발동한다 |
| **H4** | 최종 턴의 동시 전량 판매에서 한 턴 먼저 팔면 가격이 내려가기 전에 판다 | mirror 감지 시 step 717 에 `_terminal_liquidation` 과 같은 규칙으로 shed 전량을 SELL 한다(step 718 은 부모 동작 유지) | mirror 감지 시에만 |

- 조합 arm 은 없다. 단독 통과 arm 이 2개 이상이면 §4 에서 **새 변형**으로 따로 검증한다.
- 구현 전 확인 사항(Codex): 각 wrapper 가 의도한 변수에 실제로 적용되는지 발동 telemetry 로 확인한다. 예: `_RACE_REPORT['race_mirror']`, horizon 사용 턴 수, H4 의 717 SELL 단위 수. H2 는 첫 턴 현금 차이가 실제로 ≥ 1 인지 확인한다.

## 시험 설계 (seed 는 기존 사용 범위 2400–2619, 3000–4999, 9000–9599 와 겹치지 않음)
### 1단계 screen (arm 당 100경기)
- 각 arm vs O: seed 5000–5049 × 양 좌석 = 100경기. 부모 vs O 도 같은 seed 로 돌려 기준선을 확인한다(거의 전부 무승부 예상).
- **기준선 검사**: 부모 vs O 의 score rate 가 0.45–0.55 밖이면 **STOP**(대칭 가정 붕괴).
- 통과 조건: score rate ≥ 0.60. 통과한 arm 만 2단계로 간다.

### 2단계 확인 (통과 arm 마다)
| 항목 | 경기 | 기준 (모두 충족) |
|---|---|---|
| **주 지표**: vs O | seed 5050–5249 × 양 좌석 = 400 | score rate 의 Wilson 95% 하한 > **0.55** (5-arm 다중비교 보정: 하한은 99% 기준, z=2.576) |
| 비열등: vs DP 0924 exact | seed 5250–5349 × 양 좌석 = 200, 부모와 paired | Δ score rate(arm − P) 의 95% 하한 > **−0.05** |
| 대참패 guard: 공개 추천 상위 15 파일 | 파일당 seed 5350–5359 × 양 좌석 = 20, paired | 부모 대비 **0.10 넘게 떨어지는 파일 0개**. 기존 SEARCH-LOOP §4 guard 와 같은 정의 |
| hosted 일치 패널(보조) | P4 의 원천 A episode, closed-loop, hosted seed·좌석 | 평균 Δ_margin 의 95% 하한 > −(부모 평균 \|margin\| × 0.05). P4 가 끝나지 않았으면 N/A 로 기록하고 판정에서 제외 |
| runtime | 이 카드의 모든 경기 | 예외 0, 최대 step < 0.5초, p99 < 0.10초 |
| 발동률 | vs 비복제 상대 | H1a·H1b·H2·H4 는 mirror 발동률 ≤ 2%. 넘으면 오발동 → FAIL |

### 3단계 조합과 최종 선택
- 2단계 통과 arm 이 2개 이상이면, 서로 간섭 가능성이 낮은 조합 1개(예: H2+H1a, H1+H4)를 **새 변형**으로 만들어 seed 5400–5599 에서 2단계 기준 전체로 다시 검증한다.
- 최종 후보 = 2단계(또는 3단계)를 통과한 것 중 **주 지표 하한이 가장 높은 1개**. 동률이면 DP 비열등 Δ 가 큰 쪽이다.
- **최종 확인**: 후보만 seed 5600–5799 × 양 좌석 vs O(400경기)로 다시 돌린다. 점추정이 2단계 값에서 0.05 넘게 떨어지면 winner's curse 로 보고 보고서에 병기한다(판정은 유지하되 사람에게 경고).
- SUCCESS → `releases/mirror-edge-<id>/` + E-5 gate(`tools/gate_contract.py`, `tools/validate_gate.py`) → 사람이 제출을 판단한다(DP 슬롯 은퇴).
- 전부 FAIL → 제출 없음. 그 사실과 arm 별 수치를 보고한다.

## 연산 예산과 순서
- 1단계: 6 × 100 = 600경기. 2단계: arm 당 400+200+300 = 900경기(+보조 패널). 3단계와 최종 확인: 약 1,300경기. 최대 약 6,000경기.
- **CPU 충돌**: 탐색 루프가 6 worker 를 쓰고 있고(`search_loop.verify_manifest` 가 5/6 만 허용), P4(antigravity)가 2개를 쓴다. 이 카드는 **사람 결정이 필요**하다. 둘 중 하나를 고른다.
  - (a) 루프를 일시정지(`launchctl unload`)하고 이 카드를 6 worker 로 실행.
  - (b) 루프를 유지하고 P4 종료 후 2 worker 로 실행(약 2–3배 느림).
  - Claude 권고: **(a)**. ±1 탐색의 기대 이득보다 이 카드의 기대 이득이 크고, 새 전략 마감(09-27 00:00 KST)이 가깝다.
- 목표 시각: 1단계 보고 09-26 06:00 KST, 2단계 보고 09-26 15:00 KST, 최종 09-26 21:00 KST(CP1 과 같은 시각).

## 사전 폐기 조건 (이 카드 자체)
- 부모 vs O 기준선이 대칭이 아니면(§1단계) STOP.
- 모든 arm 이 1단계에서 < 0.55 이면 "선매 경주 비대칭으로는 복제본을 못 이긴다"로 기록하고 종료한다.
- 제출 후 hosted 24h 에서 후보가 127ed3e6 exact(56549720)보다 40 이상 낮으면, 이 가설 계열의 추가 제출을 중단한다.

## 보고
`coordination/reports/codex/<ts>-EXP021-MIRROR-EDGE.md`: 첫 줄 판정, arm 별 표(1단계, 2단계 각 항목, 발동률, runtime), 최종 후보 sha, 다음 행동 2개. 모든 경기는 이 카드 전용 `experiments/mirror_edge_20260926/games.jsonl` 에 쓴다.


---

## `proposals/claude/20260925-P4-TAPE-FIDELITY-ANTIGRAVITY.md`

# P4 — Tape fidelity 시험 실행 사양 (antigravity 용)

발행: Claude, 2026-09-25 23:50 KST. 사람 지시(09-25 23:31)로 작성. 실행: **antigravity**. 설계·판정 해석: Claude/Codex.
근거: `claude/15_CALIBRATION_REVIEW_2026-09-25.md` (권고 P4), 사람 제안(127ed3e6 복제본 hosted 패배 수집 → 로컬 재현 기준).

## 0. 이 시험이 답하는 질문 (한 줄)
부모(e496a4fe)의 **미세 변형**을 hosted 경기의 상대 행동 tape(open-loop)에 붙였을 때 나오는 효과가, 같은 상대를 실제 코드로 붙인 closed-loop 효과와 **방향·순위가 일치하는가**.
- 일치하면: 127ed3e6 복제본 hosted 경기(비공개 상대 포함)를 다운로드해 tape 로 metric 을 만들 수 있다.
- 불일치하면: tape 를 버리고, 공개 파일과 720 step 일치하는 상대만 쓴다. 이 경우 복제본 경기 다운로드는 가치가 낮다.

## 1. 절대 금지 (위반 시 즉시 중단·보고)
1. `experiments/search_20260925/` 안의 **어떤 파일도 쓰거나 지우지 않는다**. 대상: `games.jsonl`, `state.json`, `controller.lock`, `metric*.json`, `variants/`, `tapes/`. 읽기만 허용한다.
2. `tools/search_optimize.build_variant` 와 `tools/search_loop.run` 을 **호출하지 않는다**. 둘 다 탐색 루프 폴더에 쓴다. 로직만 복제해서 자기 폴더에 쓴다.
3. launchd·`com.sian.searchloop` 을 건드리지 않는다. 루프를 멈추지 않는다.
4. holdout 사용 금지: seed 9000–9599, `tape-holdout-policy.json` 의 CP1/CP2 episode. 이 파일은 **CP1/CP2 ID 를 제외하는 용도로만** 읽고, 그 목록을 출력·기록하지 않는다(제외한 개수만 기록).
5. 제출 금지. Kaggle 다운로드 금지(다운로드는 §7 판정 후 사람이 결정한다). 기존 파일 수정 금지.
6. **동시 실행 게임 프로세스는 최대 2개**다. 탐색 루프가 이미 6 worker 를 쓰고 있다(M3 Air 8코어, 팬 없음).

## 2. 출력 폴더
`experiments/p4_20260926/` (새로 만든다). 모든 산출물은 여기만 쓴다.
```
experiments/p4_20260926/
  preregistration.json      # §5 판정 기준 + 입력 sha, 실행 전 동결 (먼저 작성, 이후 변경 금지)
  episodes.json             # §3 episode 목록 (id, seed, seat, raw path+sha, opponent file+sha, 출처)
  variants/<vid>/main.py    # §4 변형 (부모 바이트 + wrapper)
  tapes/<raw_sha20>-<seat>.py
  games.jsonl               # 한 경기 한 줄, append-only, 재시작 시 기존 key skip
  summary.json              # §6 계산 결과
  REPORT.md                 # §8 형식
```

## 3. 입력 episode (hosted, 상대 720 step FULL 일치)
- 원천 A (주력): `analysis/step91_id/summary.json` 에서 `match_full=True` 인 episode. 메타데이터는 `analysis/exp016_017_hosted_20260924/manifest.json` 의 `id, seat, seed, path, sha256` 을 쓴다. 상대 파일은 summary 의 `path` 이고, `sha` 로 검증한다. 현재 73개(panel47 제외 후)다.
- 원천 B (보조): `analysis/dp_hosted_20260924/opponents.csv` 에서 `match_full=True` 인 episode. 상대 파일은 `analysis/dp_hosted_20260924/file_hashes.json` 의 name→path 로 찾는다. raw 는 `private_artifacts/dp_hosted_20260924/raw/<episode>.json.gz` 다. submission `56502662` 는 제외한다. **panel47 은 포함을 허용한다.** 이 시험은 변형을 고르는 게 아니라 시뮬레이터 충실도를 재는 것이라, 개발 오염이 결과를 편향시키지 않는다. 대신 `source=B_panel47` 로 표시하고 A 단독 결과도 따로 보고한다.
- 공통 제외: CP1/CP2 ID, seed 9000–9599, raw 가 720 step 이 아니거나 configuration 이 기본값과 다른 경기. 검증 로직은 `tools/search_calibration.py:tape_file` 과 같다.
- 예상 규모: A 73 + B 약 47 = 약 120 episode.

## 4. 변형 (6개 + 부모)
- 부모 P = `analysis/daily_scan/20260925/extracted/kaggriculture/main.py` (sha `e496a4fe…`). 127ed3e6 과 마지막 줄바꿈만 다르다.
- 변형 생성: `tools/search_optimize.mutation_specs(부모 바이트)` 로 목록을 만들고, `variants()` 와 같은 round-robin 순서(constant, layer 교대)로 정렬한 뒤 **앞에서 6개**(v000–v005)를 쓴다. 이미 결과를 본 변형을 고르는 일을 막기 위해 이렇게 기계적으로 고른다.
- 파일 생성: `build_variant` 와 **같은 바이트 규칙**(부모 바이트 + `# Frozen search wrapper…` 블록)으로 `experiments/p4_20260926/variants/v00k/main.py` 에 쓴다. 탐색 루프가 나중에 같은 id 를 만들면 sha 가 같아야 한다. sha 를 기록한다.

## 5. 실행 설계 (preregistration.json 에 그대로 동결)
각 episode e, 우리 좌석 s = manifest 의 seat, hosted seed 에 대해:
- **closed**: 우리 = X ∈ {P, v000..v005}, 상대 = 일치하는 공개 파일, 같은 seed·좌석.
- **open**: 우리 = X, 상대 = tape(좌석 1−s 의 녹화 action). tape 는 `tape_file` 과 같은 형식의 `.py` 다.
- 실행기: `python tools/dp_counterfactual.py --phase game --candidate <X> --opponent <op> --seed <seed> --seat <s> --output <tmp.json>`. 결과에서 rewards, margin(우리−상대), score, timing, exceptions 를 `games.jsonl` 에 append 한다.
- 경기 수: 7 agent × 약 120 episode × 2 mode = **약 1,680경기**. 동시 2개면 약 3–4시간이 걸린다(경기당 약 8–13초).
- **Gate 0 (배관 검증, 먼저 실행)**: 원천 A 에서 10 episode 를 고른다. 원래 우리 코드(`experiments/search_20260925/historical/EXP016|EXP017/main.py`, 읽기 전용)를 closed 와 open 모두로 돌려서, 두 mode 모두 **hosted reward 를 정확히 재현**해야 한다. 하나라도 불일치하면 **STOP**(배관 오류)하고 보고한다.

## 6. 계산 (summary.json)
- 변형 v, episode e, mode m 에 대해 Δ_margin(v,e,m) = margin(v) − margin(P) 이고, Δ_score 도 같은 방식으로 계산한다.
- **informative**: |Δ_margin| 이 closed 나 open 중 하나에서라도 ≥ 1 인 쌍.
- 지표:
  1. **D (방향 일치율)** = informative 쌍 중 sign(Δ_margin,open) = sign(Δ_margin,closed) 인 비율. 전체 D, 변형별 D, 원천 A 단독 D 를 모두 낸다.
  2. **R (순위 상관)** = 변형 6개의 episode 평균 Δ_margin(open) 과 평균 Δ_margin(closed) 사이의 Spearman ρ.
  3. **M (크기 비)** = median |Δ_open| / median |Δ_closed|.
  4. Δ_score 기준의 D 도 참고로 보고한다(승패는 대부분 Δ=0 이라 정보가 적다).
  5. 불확실성: episode 단위 bootstrap 2,000회로 D 와 ρ 의 95% CI 를 낸다.

## 7. 판정 (사전 동결)
| 판정 | 조건 | 다음 행동 |
|---|---|---|
| **PASS** | informative 쌍 ≥ 60 이고 D 95% CI 하한 ≥ 0.65 이고 점추정 D ≥ 0.70 이고 ρ ≥ 0.6 | 사람에게 127ed3e6 복제본 hosted 경기 다운로드를 권고. tape 패널을 metric 성분으로 쓰는 안을 Codex 에 전달 |
| **WEAK** | D ≥ 0.60 이지만 PASS 조건 미달 | tape 는 회귀 gate(새 대패 감시)로만 쓰고 metric 에는 넣지 않음 |
| **FAIL** | D < 0.60 이거나 ρ < 0.3 | tape 폐기. 공개 파일과 FULL 일치하는 상대만 사용. 복제본 경기 다운로드는 closed-loop 가능한 상대 확인용으로만 |
| **STOP** | Gate 0 실패, 예외·invalid 발생 경기 > 1%, 금지 조항 위반 | 즉시 중단·보고 |

- 원천 A 단독과 A+B 의 판정이 다르면 **A 단독을 정본**으로 한다.
- 판정 후 기준을 바꾸거나 표본을 추가하지 않는다(적응적 재표집 금지).

## 8. 보고 (REPORT.md 와 `coordination/reports/antigravity/<ts>-P4-TAPE-FIDELITY.md`)
1. 첫 줄: PASS / WEAK / FAIL / STOP 과 한 문장 이유.
2. 표: 변형별 informative n, D, 평균 Δ_open, 평균 Δ_closed.
3. 전체 D·ρ·M 과 95% CI, 원천 A 단독 결과.
4. 실행 사실: 경기 수, 실패 수, 소요 시간, 최대 동시 프로세스 수, 입력 sha, 제외 개수(panel47 사용 수, CP 제외 수).
5. 다음 행동 2개.

## 9. 시간
- 시작: 가능한 즉시. 목표 보고: **09-26 06:00 KST**.
- 09-26 12:00 KST 까지 끝나지 않으면 그 시점의 부분 결과로 보고하고, 판정은 "미완(INCOMPLETE)"으로 한다.


---

## `proposals/claude/20260925-SEARCH-LOOP-CODEX.md`

# 20260925 자율 탐색 루프 v2.3 (Codex) — EXP-020 을 포함·대체

발행: Claude (Coordinator), 2026-09-25 15:40 KST. **사람 승인 완료 (09-25 14:33)**: Mac 무인 연산 09-26~28, 탐색 단계 변형별 카드 생략, 가중치(아래 calibration 으로 확정).
v1 → v2: 독립 검토(서브에이전트, 판정 "조건부 타당") 반영 — metric 사전 검증, successive halving, checkpoint 별 disjoint holdout, 비열등 하한, panel 을 metric 에서 빼고 회귀 gate 로, 무인 구간은 상수·층 끄기만, runtime 여유 강화, 127ed3e6 exact 조기 제출. v1 사본 `20260925-SEARCH-LOOP-CODEX.v1.bak`.
v2 → v2.1 (09-25 15:30, 사람 제안): **점수대별 hosted tape 패널**을 metric 후보에 추가(open-loop 편향은 closed-loop 로 측정), **공개 상위 파일 대참패 방지 guard**, 루프를 **독립 스크립트**로 실행(Codex 사용량·세션과 무관하게 계속), Mac 절전 방지.
v2.1 → v2.2 (09-25 15:20, 사람 답변): 하드웨어 = **MacBook Air M3 (8코어 4P+4E, 팬 없음), 24GB**, 전원 상시 연결, 덮개가 닫힐 수 있음 → 재개 설계 강화(games.jsonl append·원자적 state·launchd). tape 편향이 크면 대체 방법(가장 가까운 공개 파일 대리) 추가.
v2.2 → v2.3 (09-25 15:30, 사람 지적): 부모 후보를 127ed3e6·DP 둘로 한정했던 것을 **09-24·09-25 scan 의 고유 공개 파일 전부**로 넓힘 (1b단계 부모 토너먼트).
수신: **Codex** (최상위 모델 · reasoning high). 실행: 사람 Mac, 무인.
대체: `20260925-EXP020-NEWMETA-127ED3E6-CODEX.md`, `20260925-EXP019-DP-SECOND-FACTOR-CODEX.md`.
금지: 제출, Kaggle 다운로드, BOARD·KILLS·HYPOTHESES 직접 수정, holdout seed 를 탐색·조합 판단에 사용.

## 왜
공개 주류 파일(127ed3e6) 머리말의 V233·EXP-173·E182 가 보여주듯 공개 작성자들은 수백 번 반복했다. 우리는 23일간 카드 약 18개. 병목은 모델이 아니라 반복 횟수다. Codex 가 **사전 검증된 고정 지표**를 스스로 올리는 루프를 돌리고, 엄밀성은 마지막 holdout 확인에 둔다.

## 1단계 — 127ed3e6 exact 준비 (≤ 3시간, 끝나면 즉시 보고 → 사람이 슬롯 B 제출 판단)
- 진입점 확인: 파일 끝 `kaggle_agent = cha20_entry_agent` vs 마지막 def `ig_agent` — 엔진의 마지막 callable 규칙으로 실제 호출 함수를 확정 (FACTS 09-20).
- `releases/public-newmeta-127ed3e6-exact/` exact (CRLF 그대로, tar 안 sha = 127ed3e6…c652). E-5 필수 gate + **runtime: Mac 최대 step < 0.25초, p99 < 0.10초, 1,000경기 이상에서 예외 0**.
- 경기당 실측 시간(127ed3e6 은 7,482줄 — 3초 가정 확인), 병렬 worker 수 확정 → 3단계 예산 재계산.
- `tools/dp_counterfactual.py` 임의 candidate 경로 지원 (기존 결과 재현 테스트).
- 127ed3e6 vs DP 0924 80경기 (seed 2400–2439 × 양 좌석), panel 47 (참고).
- **보고 `coordination/reports/codex/<ts>-NEWMETA-EXACT.md` 를 쓰면 1단계 완료. 이 시점에 사람이 127ed3e6 exact 를 슬롯 B 에 제출할 수 있다** (FIFO: 다음 제출은 EXP-017 56490029 은퇴 — BOARD 재확인).

## 1b단계 — 부모 토너먼트 (1단계 직후, ≈ 1시간)
DP 를 이길 가능성이 있는 공개 파일을 **전부** 부모 후보로 본다.
- 대상: `analysis/daily_scan/2026092{4,5}/extracted/*/main.py` 중 고유 sha, 1,000줄 이상, 진입점(마지막 callable 규칙) 확인된 것. 09-25 기준 예: 127ed3e6 (주류 4개), e496a4fe, 1dfd4630 harvest-ledger (`_dsm_crop_prices`, 새 버전), 939c4457 tetsutani-demand-preserving (8,407줄), cda529cb 2965 hybrid, 8378f73c shepherds-ledger (herd-safe 계열 — herd-safe-v3 는 DP 에 15-1), 4f8637a3 herd-safe-v3, 12ad317e, 3ec06d07, 919fc1d6 utils-v1, 2993cf92, 그리고 09-24 의 나머지 고유 sha. 50줄 미만·분석용 파일 제외.
- 각 파일에 E-5 필수 gate(예외 0, 최대 step, 외부 의존) 먼저 → 실패하면 제외하고 사유 기록.
- screening: 각 파일 vs DP 0924 40경기 + vs 127ed3e6 40경기 (seed 2500–2519 × 양 좌석, 1b 전용). 합산 점수율 상위 5개 → 각 80+80경기 (seed 2520–2559).
- 상위 5개는 **2단계 동결 후 metric 으로도 채점**해 부모를 고른다 (부모 = metric 최고, 동률이면 DP 직접 대결이 높은 쪽). 두 번째로 좋은 **다른 계열** 파일은 슬롯 B exact 후보로 보고 (최종 순위 = max(A,B), 메커니즘이 다를수록 가치).
- 보고 `coordination/reports/codex/<ts>-PARENT-TOURNAMENT.md`: 파일별 gate, 두 상대 점수율, 순위.

## 2단계 — metric 사전 검증 후 동결 (≈ 1–2시간, 탐색 전)
후보 metric = 상대 풀 가중 점수율 (승 1, 무 0.5), paired (부모와 같은 seed·좌석).
- **상대 풀**: 09-22~25 scan 고유 sha 파일(진입점 확인된 것) + DP 0924 + 127ed3e6. 부모에게 95% 이상 지는 상대는 제외.
- **calibration**: 같은 시기에 동시에 활성이던 우리 submission 쌍의 hosted 순서를 metric 이 맞히는지 (release 가 있는 것):
  C1(2206.6) < EXP-016(2425.7) [09-23] · EXP-017(2100.2) < EXP-016(2265.8) [09-24, 로컬 78-2 로 뒤집혔던 쌍] · EXP-017(2010.8) < DP 0924(2191.6) [09-25] · yhay81-exact(1483.8) < P2(2421.6) [09-19] · (가능하면) EXP-007 < EXP-006 [09-18].
  - 통과: **EXP-016 > EXP-017 쌍 포함, 5쌍 중 4쌍 이상 맞힘**. 시기가 다른 점수끼리 비교 금지 (같은 바이트 yhay81 이 09-10 2188 → 09-18 1515 로 흔들린 전례).
  - 가중치 후보 4개만 비교 (위 (d) 포함): (a) 127ed3e6 30% · DP 15% · 나머지 균등 55% (b) 127ed3e6 50% · DP 15% · 나머지 35% (c) 균등. 통과한 것 중 127ed3e6 비중이 큰 쪽 채택. 모두 실패하면 **BLOCKED 로 보고하고 멈춤** (검증 안 된 지표로 탐색하지 않는다).
- **점수대별 hosted tape 패널 (사람 제안)**: 이미 받은 hosted replay (`private_artifacts/{dp_hosted_20260924,exp016_017_hosted_20260924,top_agents_20260923,c1_hosted_20260921}/raw/`, 약 900경기) 에서 상대 행동을 tape 로 고정(`ReplayOpponent`, `analysis/exp016_017_hosted_20260924/reproducibility.py`)하고 같은 seed·좌석으로 후보를 붙인다. 상대 팀 LB 점수로 구간을 나눈다: <2200 / 2200–2400 / 2400–2600 / ≥2600 (DSM·Majkel1337 등 사설 상위 봇 포함). 공개 풀에 없는 **사설 강자**를 대표하는 유일한 자료다.
  - **open-loop 편향 측정 (필수)**: 상대가 공개 파일과 720 step 일치하는 경기는 closed-loop(상대 = 그 파일)과 open-loop(상대 = tape) 둘 다 돌려, 부모→후보 Δ 의 방향 일치율과 크기 차이를 보고한다. 방향 일치율 < 70% 이면 tape 패널을 metric 에서 빼고 **대체: 가장 가까운 공개 파일 대리** — 사설 상대마다 step 143 이상 일치하는 공개 파일 중 가장 긴 일치 파일을 그 상대의 대리로 closed-loop 실행(같은 seed·좌석). 143 미만 상대는 제외하고 제외 비율을 보고. 이 대리 패널도 calibration 을 통과해야 쓴다.
  - 구간 가중치: 우리 목표 구간(2200–2600) 중심. calibration 후보에 (d) "공개 풀 60% + tape 패널 40% (2200–2400 과 2400–2600 에 각 15%, ≥2600 10%)" 를 추가.
- hosted 복제 panel 47 은 metric 에서 **제외** (개발에 쓰여 오염). 대신 회귀 gate: 최종 후보가 panel 에서 부모 대비 새 패배 0.
- `experiments/search_20260925/metric.json` 동결 + sha 기록. 이후 변경 금지.

## 실행 방식 (필수)
- 탐색 루프는 **Codex 대화가 아니라 독립 Python 스크립트**(`tools/search_loop.py`)로 돌린다. Codex 는 스크립트를 만들고 6시간마다 상태를 읽어 보고만 한다 → Codex 사용량이 막혀도 루프는 계속된다.
- **재개 설계 (덮개 닫힘·재부팅·충돌 대비)**:
  - 경기 결과는 끝날 때마다 `experiments/search_20260925/games.jsonl` 에 한 줄씩 append (키 = 변형 id + seed + 좌석 + 상대). 재시작 시 이미 있는 키는 건너뛴다 → 어느 순간 끊겨도 잃는 것은 진행 중이던 경기뿐.
  - 단계 전환·halving 결정은 `state.json` 에 **원자적 쓰기**(임시 파일 → rename). 결정은 games.jsonl 로부터 항상 다시 계산 가능해야 한다.
  - **launchd LaunchAgent** (`~/Library/LaunchAgents/com.sian.searchloop.plist`, `KeepAlive=true`, `RunAtLoad=true`) 로 실행 → 터미널을 닫아도, 충돌·재부팅 후에도 자동 재시작. 설치·제거 명령을 보고서에 적는다 (사람이 실행).
  - 덮개를 닫으면 macOS 는 잠자기에 들어가 프로세스가 **멈췄다가 열면 이어서 돈다** (종료되지 않음). `caffeinate -dimsu` 는 덮개가 열린 동안의 잠자기만 막는다. 덮개를 닫은 채 돌리려면 `sudo pmset -a disablesleep 1` 이 필요하나 팬 없는 Air 의 발열 때문에 **권장하지 않음** (사람 선택).
  - 재시작 직후 로그 1줄: 재개 시각, 건너뛴 경기 수, 남은 경기 수.
- **worker 수 = 6** (M3 8코어 − 2). 팬이 없어 장시간 부하에서 성능이 떨어진다 → 1단계에서 30분 연속 부하 실측(경기/시간)으로 예산을 다시 잡고, 초기값의 60% 이하로 떨어지면 worker 를 5 로 줄여 비교. 메모리: worker 당 사용량을 재고 24GB 의 70% 를 넘지 않게.

## 3단계 — 무인 탐색 (1차 checkpoint 09-26 21:00 KST, 종료 09-28 21:00 KST)
- 부모 P = 1b단계 부모 토너먼트 결과.
- **무인 구간의 탐색 공간 = 두 가지만**: (1) 모듈 상수 (`^_?[A-Z][A-Z0-9_]{2,} = 숫자`, 127ed3e6 기준 77개) 하나씩 ±단계, (2) 덧붙은 층 하나씩 끄기(wrapper, 부모 바이트 무수정). 새 로직 작성(층 이식·패배 기반 변경)은 CP1 이후 사람이 본 뒤 별도 1–2개.
- **successive halving (paired, 공통 seed, 탐색 seed 3000–3999)**: 150 변형 × 40경기 → 상위 50 × 120 → 상위 15 × 400 → 상위 3 × 1,000. 1,000 단계만 score rate 로 판정, 앞 단계는 정규화 최종 자산 차 proxy 허용. 해당 변경이 한 번도 발동하지 않은 경기(결과 동일)는 분산 계산에서 제외하고 발동률 기록.
- **조합**: 1,000 단계 통과 변형끼리의 조합은 **새 변형**으로 취급해 새 seed(4000–4999)에서 다시 halving.
- 같은 상수·층 미세조정 3단계 제한. 모든 변형은 `experiments/search_20260925/leaderboard.csv` (id, diff, stage, seed set, git sha, 경기 수, Δ, SE, 발동률, 예외, 최대 step). 변형별 카드 없음.
- 6시간마다 `coordination/reports/codex/<ts>-SEARCH-STATUS.md`.

## 4단계 — 최종 확인 (이 문서가 사전 등록 카드)
checkpoint 마다 최상위 1개만, **checkpoint 별 disjoint holdout**: CP1 = seed 9000–9199, CP2 = 9200–9399, 예비 = 9400–9599. 한 번 쓴 holdout 은 재사용 금지.
- **SUCCESS**: metric Δ(후보 − 부모) > 2 × paired SE **그리고** 127ed3e6 상대 점수율 95% CI 하한 > 0.50 (부모가 127ed3e6 이면 > 0.50 을 "부모 대비 우위"로 읽음) **그리고** DP 0924 상대 95% CI 하한 > 0.45, panel 47 새 패배 0, runtime(1단계 기준) 충족,
  **그리고 대참패 방지 guard**: 공개 풀 중 추천 수 상위 15개 파일 각각에 대해 후보 점수율이 부모보다 **0.10 넘게 떨어지는 파일이 없을 것** (전부 이기는 것을 요구하지 않는다 — 상성 때문에 불가능할 수 있다. 예: herd-safe 가 DP 에 15-1). tape 패널을 쓰면 각 점수 구간에서도 같은 조건.
- SUCCESS → `releases/search-<id>/` + E-5 gate → 사람 제출 판단.

## 제출 운용 (Coordinator 규칙, 참고)
- anchor 1개(DP 또는 127ed3e6 중 hosted 에서 높은 쪽) 유지, 실험은 나머지 1슬롯.
- 최종 제출 목표 **09-29 12:00 UTC** (hosted 24h 이상 관측). 09-30 12:00 UTC 는 비상용.
- 127ed3e6 을 슬롯 B 에 올리면 FIFO 는 DP → 127ed3e6 순 → 그 다음 제출은 DP 를 은퇴시킨다. 탐색 후보 제출 전에 anchor 를 정하고 필요하면 재제출 절차(정책 B-5).


---

## `proposals/claude/20260926-EXP023-STAGE3-CODEX.md`

# EXP-023 Stage 3 — Codex 실행 카드 (Claude 발행, 2026-09-26 07:10 KST)

사전등록: `experiments/exp023_mirror_screen/preregistration.json` (sha 644e9ba5…) 의 stage3 문구를 구체화한 것이다. 기준은 그대로다.
근거: `stage1-summary.json` (1,870경기, 클라우드와 Mac 합산, 충돌 0, 기준선 0.500), `stage2-summary.json` (540경기).

## 대상 (Stage 2 통과 4개 + 부모)
| id | 변경 | Stage 2 vs 127ed3e6 (60경기) |
|---|---|---|
| v171 | `_DP_H` 8→9 | 0.800 (37W 22D 1L), Wilson95 하한 0.682 |
| v173 | `_MP_H` 8→9 | 0.800 (41W 14D 5L), 0.682 |
| v111 | `_OR2_SN_K` 0→1 | 0.783 (47W 0D 13L), 0.664 — 무승부 0: 행동이 크게 바뀜, 일반 성능 위험 큼 |
| v074 | `V9_RACE_DEFAULT` 44→45 | 0.650 (21W 36D 3L), 0.524 — 경계선 |
| P | 부모 e496a4fe | 0.500 (1W 58D 1L) |
파일: `experiments/exp023_mirror_screen/variants/<id>.py` (sha 는 variants.json 과 대조).

## 실행 (Mac, 5 worker, 같은 run.py; 출력 `games-stage3.jsonl`)
환경 확인은 앞 지시와 같다: .venv, 엔진 sha bc8a5487…
1. **vs 127ed3e6 exact**: 4개 후보 × seed 7200–7399 × 양 좌석 = 1,600경기
2. **vs DP 0924 exact** (paired): 4개 후보 + P × seed 7400–7499 × 양 좌석 = 1,000경기
3. **공개 guard**: `stage3-opponents.json` 의 public_top15 (127ed3e6 은 1번과 중복이므로 제외 → 14개) × (4개 후보 + P) × seed 7500–7509 × 양 좌석 = 1,400경기
합계 약 4,000경기. 작업 목록은 직접 만들되 위 정의 그대로 쓰고, jobs-stage3.json 으로 저장한 뒤 sha 를 기록한다.

## 판정 (모두 충족해야 SUCCESS, 결과를 보기 전에 고정)
- A. vs 127ed3e6: score rate 의 **Wilson 99% 하한 > 0.55** (400경기)
- B. vs DP: 같은 seed·좌석으로 짝지은 Δ(후보 − P) 의 **95% 하한 > −0.05** (seed 단위 bootstrap 2,000회)
- C. 공개 guard: 파일별 Δ(후보 − P) 점수율이 **−0.10 보다 나쁜 파일 0개** (파일당 20경기)
- D. 통합 guard: DP + 14개 파일 전체(480경기) paired Δ 의 **95% 하한 > −0.03**
- E. runtime: 우리 쪽 invalid 0, 최대 step < 0.5초
- 선택: 통과한 것 중 **A 의 하한이 가장 높은 1개**. 동률이면 D 의 점추정이 큰 쪽.
- 통과 0개 → FAIL. 기준을 완화하지 않는다.

## SUCCESS 이후 (Codex)
- `releases/mirror-screen-<id>/`: main.py(= variants/<id>.py 바이트 그대로), submission.tar.gz(main.py 한 파일), SHA256SUMS, NOTICE.txt(원본 attribution)
- E-5 필수 gate + D3 gate v2 (`experiments/d3_gate_v2/measure_gate_v2.py`, 15경기)
- 제출은 사람이 한다. 다음 제출은 FIFO 에 따라 **DP(56518910)를 은퇴**시킨다.

## 금지
제출, Kaggle 다운로드, holdout seed 9000–9599, 엔진·RNG 수정, 다른 experiments 폴더 쓰기, 결과를 본 뒤 기준·seed 변경.

## 보고
`coordination/reports/codex/<ts>-EXP023-STAGE3.md`: 첫 줄 판정, 후보별 A–E 표, 선택 id·sha, release·gate 결과, 다음 행동 2개.


---

## `proposals/claude/20260926-EXP024-ROUND2-CODEX.md`

# EXP-024 — 2라운드 거울 screen (부모 = v171) · Codex 실행 카드

발행: Claude, 2026-09-26 12:10 KST. 사람 방침(09-26 09:53): 우리 봇 개선을 계속한다. **제출된 v171 이 hosted 에서 관측되는 동안 병렬로 실행한다.** 제출은 사람이 한다.

## 부모와 상대
- 부모 P1 = `releases/mirror-screen-v171/main.py` (sha 496460f8…, e496a4fe + `_DP_H = 9`).
- 주 상대: **O1 = 127ed3e6 exact**, **O2 = v171 자신(P1)**. 거울 칼날 구조(EXP-023)는 두 상대 모두에서 성립한다. 두 상대를 모두 이기는 변형은 공개 복제본과 우리 직전 버전을 함께 넘는다.

## 변형
- EXP-023 의 `gen.py` 규칙(mutation_specs 전체, 단일 변경)을 **P1 바이트에 적용**한다. wrapper 는 P1 끝에 덧붙이는데, P1 의 기존 `_DP_H = 9` 줄 뒤에 온다.
- `_DP_H` 는 9→8(되돌림)·9→10 두 개만 생성한다.
- 산출물: `experiments/exp024_round2/variants.json` + sha. 생성 후 수정 금지.

## 단계 (seed 는 기존 사용 범위와 겹치지 않음: 8000–8999)
1. **Screen**: 각 변형 vs O1 과 vs O2, seed 8000–8004 × 양 좌석 = 변형당 20경기. 부모 기준선 vs O1 은 약 0.8 로 예상되고, vs O2 는 0.5 여야 한다(아니면 STOP).
   - 진출: **vs O2 ≥ 0.70 이면서 vs O1 ≥ 부모의 vs O1 점수**. 무효 0. 최대 8개. 순위는 vs O2 점수 → vs O1 점수 → 두 상대 margin 합 순.
   - 행동이 부모와 같은 변형(action digest 동일)은 NO_EFFECT 로 표시한다.
2. **Stage 2**: seed 8100–8129 × 양 좌석 × {O1, O2} = 변형당 120경기. 통과: 각 상대에서 Wilson95 하한 > 0.50 이고, vs O2 점추정 ≥ 0.65, vs O1 점추정 ≥ 부모 − 0.02.
3. **Stage 3**: EXP-023 Stage 3 카드와 같은 A–E 기준을 적용하되, A 는 **O2 상대**(seed 8200–8399, Wilson99 하한 > 0.55)로 하고 **A′ vs O1 400경기에서 부모 대비 비열등**(paired Δ 하한 > −0.03)을 추가한다. B·C·D 의 기준선은 P1 이다. seed 8400–8599.
   - **추가 guard (P4b PASS 로 가능해짐)**: `experiments/p4b_20260926/` 의 121 hosted episode 를 closed-loop 로 돌려 P1 대비 Δ score 95% 하한 > −0.03 이어야 한다.
4. SUCCESS → `releases/round2-<id>/` (tar 는 macOS xattr 없이: `COPYFILE_DISABLE=1 tar --no-xattrs` 또는 python tarfile USTAR) + E-5 + D3 gate.

## 운영
- 5 worker. 규모: 변형 약 186개 × 20 = 약 3,700경기(약 70분) + Stage 2 약 1,000 + Stage 3 약 3,500.
- 인프라 버그는 수정 후 진행해도 된다(기록 필수). 가설·기준·seed·candidate 바이트는 변경 금지.
- 금지: 제출, 다운로드, holdout 9000–9599, 엔진·RNG 수정, 다른 experiments 폴더 쓰기.
- 보고: 각 단계마다 `coordination/reports/codex/<ts>-EXP024-*.md`.


---

## `proposals/claude/20260926-EXP024-STAGE3-CODEX.md`

# EXP-024 Stage 3 — Codex 실행 카드 (Claude 발행, 2026-09-26 16:15 KST)

**사람 승인(09-26): 이 카드가 Stage 3 실행 승인이다.** 정본 EXP-024 카드(`20260926-EXP024-ROUND2-CODEX.md`, Project `20_EXP024_ROUND2_CARD`)의 Stage 3 를 구체화한 것이다. 기준은 바꾸지 않았다.

## 지금까지 (Codex 사용 한도 중 Claude 가 이어서 수행)
- Screen 3,720/3,720(수리 후 재실행)을 Codex 의 `judge_screen.py` 로 판정했다. 결과는 PASS 이고 진출은 v111·v169·v104·v121·v074 다.
  - 인프라 수정 1건: `row.get("agent_errors")`(list) 합산 TypeError → `bool(...)` 로 감쌌다. 판정 로직은 같다.
  - 결과 파일: `screen-summary.claude-fixedjudge.json`. invalid 300 은 층 끄기 변형 15개(v049–v079 홀수)의 agent error 이며 전부 진출에서 제외됐다.
- Stage 2 720/720(클라우드, 같은 `run.py`, worker 2개)을 Codex 의 `judge_stage2.py` 로 판정했다. 결과는 PASS 이고 **v111, v169, v074** 가 통과했다. 부모 P1(v171)은 vs O1 0.750, vs O2 0.500 이다. 결과 파일: `stage2-summary.claude.json`, `games-stage2.claude.jsonl`.

| id | 변경 (v171 기준) | vs O1 127ed3e6 | vs O2 v171 |
|---|---|---|---|
| v111 | `_OR2_SN_K` 0→1 | 0.850 (51/0/9) | 0.850 (51/0/9) |
| v169 | `_EV_H` 8→9 | 0.800 (42/12/6) | 0.650 (22/34/4) |
| v074 | `V9_RACE_DEFAULT` 44→45 | 0.867 (48/8/4) | 0.700 (28/28/4) |

- 주의: v111 은 무승부 0 으로 행동이 크게 바뀐다. 1라운드 P4b 의 hosted 상대 guard 에서 −0.10 이었다. 아래 H guard 가 판정한다.
- Step 0 (부록): v171 과 부모 vs 09-26 새 인기 파일 5개(G26) 각 20판이 모두 valid 였다. v171 은 0.8–1.0 으로 부모와 완전히 같다(Δ 0). 결과 파일: `games-step0g.claude.jsonl`.

## Stage 3 실행 (Mac, 5 worker, 같은 run.py, 출력 `games-stage3.jsonl`)
후보 C ∈ {v111, v169, v074}, 기준선 P1 = `releases/mirror-screen-v171/main.py`.
1. **A** vs O2(v171): C × seed 8200–8399 × 양 좌석 = 후보당 400판
2. **A′** vs O1(127ed3e6): C 와 P1 × seed 8200–8399 × 양 좌석 (paired)
3. **B** vs DP 0924 exact: C 와 P1 × seed 8400–8499 × 양 좌석 (paired)
4. **C/D guard**: `experiments/exp023_mirror_screen/stage3-opponents.json` 의 public_top15 중 127ed3e6 을 뺀 14개 + G26 5개 = 19개 파일 × (C 와 P1) × seed 8500–8509 × 양 좌석
   - G26 경로: `analysis/daily_scan/20260926/extracted/{a-song-of-ice-and-fire-fixed-flexible, kaggriculture-harvest-ledger, kaggriculture-multi-route-farming-agent, kaggriculture-top-2-master-engine-v4, kaggriculture-hack}/main.py`
5. **H hosted guard**: `experiments/p4b_20260926/` 의 121 episode closed-loop(일치 공개 파일 상대, hosted seed·좌석) × (C 와 P1)
합계 약 5,600판.

## 판정 (결과를 보기 전에 고정)
- A: Wilson 99% 하한 > 0.55
- A′: paired Δ(C − P1) seed bootstrap 95% 하한 > −0.03
- B: paired Δ 95% 하한 > −0.05
- C: 파일별 Δ 점수율이 −0.10 보다 나쁜 파일 0개
- D: DP + 19개 파일 합산 paired Δ 95% 하한 > −0.03
- H: 121 episode paired Δ score 95% 하한 > −0.03
- E: 우리 쪽 invalid 0(action_count 719, agent_errors 없음), 최대 step < 0.5초
- 선택: 통과한 것 중 A 하한이 가장 높은 1개. 동률이면 D 점추정이 큰 쪽.
- 통과 0개 → FAIL(v171 유지).
- SUCCESS → `releases/round2-<id>/`: main.py 바이트 그대로, submission.tar.gz 는 **xattr 없이** (python tarfile USTAR, 또는 `COPYFILE_DISABLE=1 tar --no-xattrs`). E-5 + D3 gate v2. 제출은 사람이 한다.

금지: 제출, 다운로드, holdout 9000–9599, 엔진·RNG 수정, 기준·seed 변경.
보고: `coordination/reports/codex/<ts>-EXP024-STAGE3.md` (첫 줄 판정, 후보별 A–H 표, 선택 id·sha, 다음 행동 2개).


---

## `proposals/claude/20260926-EXP025-V171-HOSTED-ANTIGRAVITY.md`

# EXP-025 Phase 1 — v171 hosted 경기 수집·상대 식별 (antigravity 실행 카드)

발행: Claude, 2026-09-26 20:20 KST. **사람 승인(09-26 20:10): Kaggle episode·replay·leaderboard 다운로드 허용(이 카드 범위만).** 제출은 금지.
목적: v171 (56567563, hosted 약 2323)이 **누구에게 지는지** 알아낸다. 분석과 R3 설계는 Claude 가 한다. 이 카드는 데이터 수집과 라벨링만 한다.

## 토큰 절약 운영 규칙 (필수)
- 이 카드를 **한 번** 읽고 곧바로 실행한다. 저장소 탐색은 아래 명시 파일만 한다.
- 동시 게임·다운로드 프로세스는 5개 이하. 오래 걸리는 단계는 `nohup … > log 2>&1 &` 로 띄운 뒤, 끝날 때까지 **명령 한 번으로 대기**한다: `while kill -0 PID 2>/dev/null; do sleep 60; done`. 진행 상황 폴링이나 중간 상태 메시지를 내지 않는다.
- 보고는 단계 완료, STOP, 오류 때만 한다. 최종 보고는 한 번, 20줄 이내로 한다.
- 기존 스크립트를 복사해 경로·ID 만 바꿔 쓴다. 새로 설계하지 않는다.

## 출력 위치
- 메타데이터: `analysis/v171_hosted_20260926/`
- replay: `private_artifacts/v171_hosted_20260926/raw/<episode>.json.gz`
- 다른 폴더는 쓰지 않는다.

## 단계
1. **episode 목록** — `analysis/exp016_017_hosted_20260924/collect.py` 의 필터(COMPLETED, PUBLIC, 두 팀 다름, 우리 submission 1개)를 그대로 쓴다.
   - 대상 submission: **56567563 (v171)**, cap 400. 추가로 **56577440 (v074)** 는 있는 만큼, cap 200.
   - 저장: `episodes_all.json` (id, seed, our_seat, result, margin, op_teamName, op_teamId, op_submissionId, endTime).
2. **leaderboard 스냅샷** — `kaggle competitions leaderboard -c kaggriculture --download` 를 이 폴더에 받는다. 각 episode 에 `op_lb_score`(팀 최고 점수; 제출물 rating 이 아님을 명시)를 붙인다.
3. **replay 다운로드** — `analysis/dp_hosted_20260924/download_replays.py` 방식(gzip 저장, 429 대응, 이미 있으면 건너뜀). 병렬은 4개 이하로 한다. 각 replay 의 seed·좌석·보상이 1단계 메타데이터와 같은지 확인하고, 다르면 해당 행에 표시한다.
4. **상대 식별 (fingerprint)** — `analysis/exp016_017_hosted_20260924/fingerprint.py` 를 복사해 refs 를 아래로 바꾼다. 출력은 `prefix_len`(상대 행동이 공개 파일과 일치한 step 수)과 `label`(가장 긴 일치 파일, 720 이면 FULL)이다. worker 는 5개다.
   - refs = 기존 17개 + `127ed3e6`(releases/public-newmeta-127ed3e6-exact/main.py) + DP 0924 exact + `experiments/exp023_mirror_screen/stage3-opponents.json` 의 public_top15 + 09-26 새 파일 5개(`analysis/daily_scan/20260926/extracted/{a-song-of-ice-and-fire-fixed-flexible,kaggriculture-harvest-ledger,kaggriculture-multi-route-farming-agent,kaggriculture-top-2-master-engine-v4,kaggriculture-hack}/main.py`) + herd-safe-v3(4f8637a3). 중복 sha 는 하나로 합친다.
   - 우리 봇(v171·v074)이 상대인 경기(같은 팀)는 1단계에서 이미 제외된다.
5. **요약** `summary.json` + `opponents.csv` (episode 당 한 줄):
   - 전체 W/D/L, 상대 LB 구간(<2200 / 2200–2400 / 2400–2600 / 2600+)별 W/D/L
   - 상대 label 별 W/D/L. FULL 일치 여부와 127ed3e6 계열 여부를 따로 집계한다.
   - **패배 목록**: episode, 상대 팀, op_lb_score, label, prefix_len, margin, seed, seat

## 금지
제출, holdout seed 9000–9599 사용, 엔진·RNG 수정, 기존 파일 수정, 경기 실행(fingerprint 재현 외).

## 보고
`coordination/reports/antigravity/<ts>-EXP025-V171-HOSTED.md`: 첫 줄 PASS/STOP, 수집 수(목록·replay·검증 실패), 위 요약표, 가장 많이 진 상대 5개, 다음 행동 2개.


---

## `proposals/claude/20260926-EXP025-V171-HOSTED-CODEX.md`

# EXP-025 Phase 1 — v171 hosted 경기 수집·상대 식별 (Codex 실행 카드)

발행: Claude, 2026-09-26 20:20 KST. **사람 승인(09-26 20:10): Kaggle episode·replay·leaderboard 다운로드 허용(이 카드 범위만).** 제출은 금지.
목적: v171 (56567563, hosted 약 2323)이 **누구에게 지는지** 알아낸다. 분석과 R3 설계는 Claude 가 한다. 이 카드는 데이터 수집과 라벨링만 한다.

## 토큰 절약 운영 규칙 (필수)
- 이 카드를 **한 번** 읽고 곧바로 실행한다. 저장소 탐색은 아래 명시 파일만 한다.
- 오래 걸리는 단계는 `nohup … > log 2>&1 &` 로 띄운 뒤, 끝날 때까지 **명령 한 번으로 대기**한다: `while kill -0 PID 2>/dev/null; do sleep 60; done`. 진행 상황 폴링이나 중간 상태 메시지를 내지 않는다.
- 보고는 단계 완료, STOP, 오류 때만 한다. 최종 보고는 한 번, 20줄 이내로 한다.
- 기존 스크립트를 복사해 경로·ID 만 바꿔 쓴다. 새로 설계하지 않는다.

## 출력 위치
- 메타데이터: `analysis/v171_hosted_20260926/`
- replay: `private_artifacts/v171_hosted_20260926/raw/<episode>.json.gz`
- 다른 폴더는 쓰지 않는다.

## 단계
1. **episode 목록** — `analysis/exp016_017_hosted_20260924/collect.py` 의 필터(COMPLETED, PUBLIC, 두 팀 다름, 우리 submission 1개)를 그대로 쓴다.
   - 대상 submission: **56567563 (v171)**, cap 400. 추가로 **56577440 (v074)** 는 있는 만큼, cap 200.
   - 저장: `episodes_all.json` (id, seed, our_seat, result, margin, op_teamName, op_teamId, op_submissionId, endTime).
2. **leaderboard 스냅샷** — `kaggle competitions leaderboard -c kaggriculture --download` 를 이 폴더에 받는다. 각 episode 에 `op_lb_score`(팀 최고 점수; 제출물 rating 이 아님을 명시)를 붙인다.
3. **replay 다운로드** — `analysis/dp_hosted_20260924/download_replays.py` 방식(gzip 저장, 429 대응, 이미 있으면 건너뜀). 병렬은 4개 이하로 한다. 각 replay 의 seed·좌석·보상이 1단계 메타데이터와 같은지 확인하고, 다르면 해당 행에 표시한다.
4. **상대 식별 (fingerprint)** — `analysis/exp016_017_hosted_20260924/fingerprint.py` 를 복사해 refs 를 아래로 바꾼다. 출력은 `prefix_len`(상대 행동이 공개 파일과 일치한 step 수)과 `label`(가장 긴 일치 파일, 720 이면 FULL)이다. worker 는 5개다.
   - refs = 기존 17개 + `127ed3e6`(releases/public-newmeta-127ed3e6-exact/main.py) + DP 0924 exact + `experiments/exp023_mirror_screen/stage3-opponents.json` 의 public_top15 + 09-26 새 파일 5개(`analysis/daily_scan/20260926/extracted/{a-song-of-ice-and-fire-fixed-flexible,kaggriculture-harvest-ledger,kaggriculture-multi-route-farming-agent,kaggriculture-top-2-master-engine-v4,kaggriculture-hack}/main.py`) + herd-safe-v3(4f8637a3). 중복 sha 는 하나로 합친다.
   - 우리 봇(v171·v074)이 상대인 경기(같은 팀)는 1단계에서 이미 제외된다.
5. **요약** `summary.json` + `opponents.csv` (episode 당 한 줄):
   - 전체 W/D/L, 상대 LB 구간(<2200 / 2200–2400 / 2400–2600 / 2600+)별 W/D/L
   - 상대 label 별 W/D/L. FULL 일치 여부와 127ed3e6 계열 여부를 따로 집계한다.
   - **패배 목록**: episode, 상대 팀, op_lb_score, label, prefix_len, margin, seed, seat

## 금지
제출, holdout seed 9000–9599 사용, 엔진·RNG 수정, 기존 파일 수정, 경기 실행(fingerprint 재현 외).

## 보고
`coordination/reports/codex/<ts>-EXP025-V171-HOSTED.md`: 첫 줄 PASS/STOP, 수집 수(목록·replay·검증 실패), 위 요약표, 가장 많이 진 상대 5개, 다음 행동 2개.


---

## `proposals/claude/20260926-EXP025B-NEARCLONE-ANTIGRAVITY.md`

# EXP-025b — 127ed3e6 변형 팀 tape 수집 (antigravity 실행 카드)

발행: Claude, 2026-09-26 21:45 KST. **사람 승인(09-26 20:10) 범위: Kaggle episode·replay 다운로드 허용, 제출 금지.**
배경: `coordination/reports/claude/20260926-2140-EXP025-ANALYSIS.md`. v171 은 127ed3e6 을 몰래 고친 팀들에게 3승 3무 16패를 했다.

## 토큰 절약 규칙 (필수)
- 이 카드만 한 번 읽고 실행한다. 긴 단계는 nohup 으로 띄우고 `while kill -0 PID; do sleep 60; done` 한 번으로 기다린다.
- 폴링이나 중간 보고를 하지 않는다. 최종 보고 한 번, 15줄 이내.
- 판단이 필요하면(검증 불일치 10% 이상, 스크립트가 예상과 다르게 동작) 멈추고 보고한다. 임의로 고치지 않는다.

## 입력
`analysis/v171_hosted_20260926/opponents.csv` 에서 `submission_label=v171`, `is_full=False`, label 에 `127ed3e6` 포함, `prefix_len>0` 인 행의 `op_submissionId`(19개 고유).

## 단계
1. 각 op_submissionId 의 공개 COMPLETED episode 목록을 받는다(submission 당 cap 200, 기존 collect.py 필터).
2. 그 중 **상대(=변형 팀의 상대)가 127ed3e6 exact 와 FULL(720) 일치**하는 경기만 고른다.
   - 방법: replay 를 받아 `experiments/exp025_recon/recon.py` 의 `prefix()` 를 쓴다. 인자는 our_seat = **상대 좌석**, our_file = `releases/public-newmeta-127ed3e6-exact/main.py`, cand_file = 같은 파일이다.
   - 반환값 `our_first_mismatch` 가 None(= 720 step 전부 일치)이면 선택한다. 변형 팀 쪽 `opp_prefix` 도 기록한다.
   - v171·v074(우리)와 둔 경기는 제외한다(이미 있음).
3. 선택된 경기의 replay 는 `private_artifacts/exp025b_nearclone/raw/<episode>.json.gz` 에 저장한다. 목록 `analysis/exp025b_nearclone/tapes.json` 의 필드: episode, seed, nearclone_seat, nearclone_submission, nearclone_team, result(변형 팀 기준), margin, divergence_step(opp_prefix), raw sha256.
4. 병렬 5개 이하. 2단계 검사는 경기당 수 초면 된다(갈라지면 멈춤).

## 보고
`coordination/reports/antigravity/<ts>-EXP025B.md`: 목록 수, 선택 수(submission 별), 변형 팀 승/무/패, 검증 실패 수, 다음 행동 2개.
금지: 제출, holdout 9000–9599, 엔진 수정, 기존 파일 수정.


---

## `proposals/claude/20260927-ALTMECH-CODEX.md`

# ALTMECH-0928 카드 (Codex) — d157 과 다른 메커니즘의 2번째 슬롯 후보 설계 (보험)
발행: Claude 2026-09-27 21:55 KST. 보고 목표 **09-28 08:00 KST**. 판단 작업(상위 모델·high 이상).
배경: 활성 = v074(56577440) + d157(56607884). 두 번째 슬롯(v074 교체)은 EXP-036(d157 ±1, 밤새 Kaggle+Mac)이 1순위. 이 카드는 EXP-036 이 FAIL 하거나 d157 과 상관이 너무 높을 때의 **독립 대안**이다(d157/d053 결과 90.8% 일치 → 같은 계열 두 슬롯은 max 이득이 작다).
사실: LATE 보고(`coordination/reports/codex/20260927-2126-LATE.md`) — d157 이득은 자기 cash 가 아니라 late SELL 순서로 상대 판매가를 낮추는 market suppression. EXP-031/033: 127 변형이 hosted 상대의 32%, LB 2200–2400 중심, v074 0.163. tape 는 `experiments/exp033_tapes/`(meta.json, games-cloud.jsonl: P·d157 × 350).
금지: 제출, 다운로드, holdout 9000–9599, 기존 파일 수정, 결과 본 뒤 기준 변경. **CPU: Mac·Kaggle 는 EXP-036 사용 중 → 새 게임은 1 worker, 최대 24경기.** 쓰기: `experiments/altmech_0928/`, 보고서 1개.

## Claude 사전 확인 (21:58, 중복 방지)
- engine: 상대 `farms[1-player]` 의 money·tiles(작물/동물·yield_units 등)·farmer·hands·unlocked_quadrants·hires_today 는 공개, **shed·inventories 는 private**(`kaggriculture.py:142-154, 169, 269`).
- 이미 쓰는 공개 코드: 127 계열(v074·127ed3e6·55be5d5f 공통) `_r37_quote_priority`(`releases/round2-v074/main.py:1796-1818`)가 상대의 **보이는 익은 yield**로 "rival batch"(8–24개)를 가정해 SELL 순서를 정한다. `_r37_similarity`(1779-1793)는 상대 타일 배치로 mirror 판단. 55be 의 Step793 reorder 도 이 위에 있다.
- 따라서 "상대 재고 기반 front-run" 은 **순서 정렬 수준으로는 이미 공통**이다. 새 후보는 이것과 다른 축이어야 한다: 예) 상대 작물·동물의 **익을 시점 예측**으로 며칠 앞서 판매 일정을 당기기, 상대 money 변화로 상대 판매량·shed 추정, 또는 전혀 다른 축(생산 배분 등). 같은 축이면 "기존 대비 무엇이 새로운지" 를 코드 근거로 증명하라.
## 과제
1. **관측 가능성 확인(코드·engine 근거)**: observation 에서 상대 farm 상태(현금, shed 재고, 작물·동물, 그날 주문)가 무엇까지 보이는가? (`kaggriculture.py` observation 구성부 줄번호)
2. **메커니즘 후보 ≤ 3개**, d157 과 다른 축에서. 예시(참고만, 근거가 없으면 버려라):
   - (a) 상대 재고 인식 front-run: 상대 shed 에 쌓인 품목을 상대보다 먼저 팔아 그 품목 가격을 선점·억제(보이는 경우에만).
   - (b) suppression 방어: 127 변형이 우리 판매가를 누를 때 판매를 분산·지연해 손실을 줄이는 반응.
   - (c) 상대 계열 조기 식별(관측 후 신호) → v074 정책 유지 vs 선매 강화 분기.
   각 후보: 근거(파일:줄, tape 재집계), 부모(v074 또는 d157), wrapper 구현 지점, 예상 효과(127 변형·127 exact·55be·기타), 반증 기준, d157 과의 예상 결과 상관.
3. **1순위 후보 1–2개 구현 + 24경기 이내 smoke test**(tape 상에서 발동 확인, action 이 부모와 달라지는 step, 예외 0).
4. **사전등록 문서** `experiments/altmech_0928/prereg.json`: Claude 가 09-28 오전 Kaggle 로 돌릴 jobs 파일(EXP-036 stage2 와 같은 panel: held-out tape 300 + V074/O127/D/guard23, 파일은 `experiments/exp036_d157plus/tape-split.json` 참조)과 frozen 판정 규칙(d157 대비 tape lower95>0, closed-loop 각 ≥ −0.03, guard ≥ −0.02, 1-worker max<0.8).
## 보고 (`coordination/reports/codex/<ts>-ALTMECH.md`, 120줄): 첫 줄 1순위 후보와 확신도, 관측 가능성 표, 후보 표, smoke 결과, jobs 경로·sha, 다음 행동 2개. 근거 없는 후보는 "없음" 이 정답이다.


---

## `proposals/claude/20260927-EXP026-NEARCLONE-ANTIGRAVITY.md`

# EXP-026 — 127ed3e6 변형 팀 tape 상대 R3 탐색 (antigravity 실행 카드, 스크립트 실행만)

발행: Claude, 2026-09-27 01:50 KST. 사람 방침 (가) (09-26 20:10). **판단은 스크립트와 Claude 가 한다. 실행자는 명령만 순서대로 실행한다.**

## 먼저 알아둘 것: EXP-025b 결과 오류
Claude 가 무작위 8판을 직접 검증했다. `nearclone_seat=1` 인 6판은 모두 상대가 127ed3e6 과 FULL 일치하지 **않았다**(0–167 step 에서 갈라짐). 좌석 처리 오류로 보인다. 1,028/1,397 행이 의심스럽다. **`tapes.json` 은 쓰지 않는다.** 아래 1단계에서 Claude 의 스크립트로 다시 거른다.

## 토큰 절약 규칙
- 이 카드만 읽는다. 각 명령을 `nohup … > log 2>&1 &` 로 띄우고 `while kill -0 $!; do sleep 60; done` 한 번으로 기다린다. 폴링이나 중간 보고는 하지 않는다.
- 스크립트를 고치지 않는다. 오류가 나면 로그 마지막 30줄을 붙여 STOP 보고한다.
- 최종 보고는 한 번, 15줄 이내.

## 실행 (저장소 루트에서, .venv 파이썬, 엔진 sha bc8a5487… 확인)
스크립트 위치: `experiments/exp026_nearclone/` (common26.py, screen26.py, judge26.py, stage2_26.py), `experiments/exp025_recon/refilter.py`.
```
cp experiments/exp026_nearclone/*.py .            # 루트에서 import 되도록 (끝나면 루트 사본만 지운다)
python experiments/exp025_recon/refilter.py        # 약 30분 → analysis/exp025b_nearclone/tapes_verified.json
```
- **STOP 조건**: 출력 `valid` 가 200 미만이면 멈추고 보고한다.
```
W=5 python screen26.py                              # 142 변형 × 40 tape + 기준 = 5,720판, 약 2시간
python judge26.py screen                            # → experiments/exp026_nearclone/screen-summary.json
```
- **STOP 조건**: `selected` 가 비어 있으면 멈추고 보고한다(FAIL, 정상 결과다).
```
W=5 python stage2_26.py                             # 최대 8 변형 × 160 tape + 기준
python judge26.py stage2                            # → stage2-summary.json
```

## 보고
`coordination/reports/antigravity/<ts>-EXP026.md`: 첫 줄 PASS/FAIL/STOP. 이어서 refilter 출력 JSON 한 줄, screen·stage2 의 `selected` 와 baseline 한 줄씩, 경기 수·invalid 수·소요 시간을 적는다. 해석은 쓰지 않는다(Claude 가 한다).
금지: 제출, 다운로드, holdout 9000–9599, 엔진·스크립트 수정, 다른 experiments 폴더 쓰기.


---

## `proposals/claude/20260927-EXP027-STAGE3-ANTIGRAVITY.md`

# EXP-027 — EXP-026 3단계 closed-loop guard (antigravity 실행 카드, 스크립트 실행만)

발행: Claude, 2026-09-27 11:00 KST. 준비(`prepare27.py`)는 Claude 가 Mac 에서 이미 실행했다: `experiments/exp027_stage3/` 에 jobs-closed.json(7,206판, sha ad6c283e…), jobs-n.json(160판), manifest.json, c3.py 가 있다.
판정 규칙은 `judge27.py` 머리말에 결과를 보기 전에 고정했다. 해석은 Claude 가 한다.

## 토큰 절약 규칙
- 이 카드만 읽는다. 명령마다 `nohup … > log 2>&1 &` 로 띄우고 `while kill -0 $!; do sleep 60; done` 한 번으로 기다린다. 폴링이나 중간 보고는 하지 않는다.
- 스크립트를 고치지 않는다. 오류가 나면 로그 마지막 30줄과 함께 STOP 보고한다. 최종 보고는 한 번, 10줄 이내.

## 실행 (저장소 루트, .venv 파이썬)
```
EXP024_OUT=experiments/exp027_stage3/games-closed.jsonl python experiments/exp024_round2/run.py experiments/exp027_stage3/jobs-closed.json   # 약 2.5시간, 5 worker
W=5 python experiments/exp027_stage3/run_n27.py        # 160판, 약 5분
python experiments/exp027_stage3/judge27.py             # → stage3-summary.json
```
(`run.py` 는 EXP-024 에서 쓴 것 그대로다. 재실행하면 끝난 key 는 건너뛴다.)

## 보고
`coordination/reports/antigravity/<ts>-EXP027.md`: 첫 줄 SUCCESS/FAIL/STOP, judge27 의 출력 전체(verdict 줄 + 후보별 줄), 경기 수, 소요 시간.
금지: 제출, 다운로드, holdout 9000–9599, 엔진·스크립트 수정.


---

## `proposals/claude/20260927-EXP028-029-ANTIGRAVITY.md`

# EXP-028/029 — 55be5d5f 확인 비교 + 거울 칼날 탐색 (antigravity 실행 카드, 명령 실행만)

발행: Claude, 2026-09-27 11:40 KST. **사람 승인(09-27 10:40): marketshock dataset 다운로드 허용, 55be5d5f 제출 방침.** 제출은 사람이 한다.
**EXP-027 은 실행하지 않는다**(대체됨).
준비물(Claude 가 Mac 에서 생성·확인 완료):
- release `releases/public-dpnew-55be5d5f-exact/` (tar sha 938be4c0…, D3 gate PASS)
- `experiments/exp028_dpnew/jobs.json` (1,962판)
- `experiments/exp029_dpnew_mirror/` (variants 158개, jobs-screen.json 3,180판)

## 토큰 절약 규칙
- 이 카드만 읽는다. 명령마다 `nohup … > log 2>&1 &` 로 띄우고 `while kill -0 $!; do sleep 60; done` 한 번으로 기다린다. 폴링이나 중간 보고는 하지 않는다.
- 스크립트를 고치지 않는다. 오류가 나거나 판정 스크립트가 STOP·NO_ADVANCE 를 출력하면 그 출력과 함께 멈추고 보고한다.

## 명령 (저장소 루트, .venv 파이썬, 5 worker)
A. dataset (몇 분)
```
kaggle datasets download -d <owner>/marketshock-m1-wr1-agent -p private_artifacts/marketshock_20260927 --unzip
```
- owner 는 `kagricult-man-reverse-engineering` 노트북 메타데이터(dataset_sources)에서 확인한다.
- 받은 파일 목록과 각 main.py 의 sha256 을 `analysis/marketshock_20260927/files.json` 에 적는다. 경기는 돌리지 않는다.

B. EXP-028 (약 40분)
```
EXP024_OUT=experiments/exp028_dpnew/games.jsonl python experiments/exp024_round2/run.py experiments/exp028_dpnew/jobs.json
python experiments/exp028_dpnew/judge28.py
```

C. EXP-029 (screen 약 65분 + stage2 약 25분)
```
EXP024_OUT=experiments/exp029_dpnew_mirror/games-screen.jsonl python experiments/exp024_round2/run.py experiments/exp029_dpnew_mirror/jobs-screen.json
python experiments/exp029_dpnew_mirror/judge29.py screen
python experiments/exp029_dpnew_mirror/prep29.py stage2
EXP024_OUT=experiments/exp029_dpnew_mirror/games-stage2.jsonl python experiments/exp024_round2/run.py experiments/exp029_dpnew_mirror/jobs-stage2.json
python experiments/exp029_dpnew_mirror/judge29.py stage2
```

## 보고
- **B 가 끝나면 곧바로 1차 보고**: `coordination/reports/antigravity/<ts>-EXP028.md` 에 judge28 출력 전체를 붙인다(사람이 이 결과로 제출 여부를 정한다).
- 전체가 끝나면 `<ts>-EXP029.md` 에 A 파일 목록, judge29 screen·stage2 출력 전체, 경기 수·소요 시간을 적는다. 해석은 쓰지 않는다.
금지: 제출, holdout 9000–9599, 엔진·스크립트 수정, 다른 experiments 폴더 쓰기.


---

## `proposals/claude/20260927-EXP030-BYPASS-ANTIGRAVITY.md`

# EXP-030 실행 카드 (antigravity) — 판단 없음, 고정 명령만 실행
발행: Claude 2026-09-27 12:10 KST. 근거: Codex REVIEW-0927B. 이 카드는 20260927-EXP028-029 카드의 C 단계(stage2)를 **대체**한다.
금지: 제출, Kaggle 다운로드, 스크립트/기준 수정, holdout(seed 9000–9599), 탐색 루프 폴더 쓰기, 결과를 보고 재실행·재표집.
토큰 규칙: 진행상황 polling 금지. 각 단계는 명령 1회 실행 후 종료까지 대기. 보고는 각 judge 의 stdout 첫 줄 + 상위 10줄만.

입력 sha(시작 전 확인, 다르면 STOP): prep30.py b381d2527c0d…, judge30.py ffe5f0e0780e… (`shasum -a 256`).

## 1. EXP-029 마무리 (진행 중인 screen 은 끝까지 둔다)
0. (새 채팅에서 시작한 경우) 먼저 `pgrep -fl "exp029_dpnew_mirror/jobs-screen"` 로 이전 run.py 가 살아 있는지 본다.
   - 살아 있으면: 새로 실행하지 말고 그 프로세스가 끝날 때까지 기다린다(중복 실행 금지).
   - 없고 `games-screen.jsonl` 이 3,180행 미만이면: `EXP024_OUT=experiments/exp029_dpnew_mirror/games-screen.jsonl python experiments/exp024_round2/run.py experiments/exp029_dpnew_mirror/jobs-screen.json` 1회(기존 key skip 으로 이어서 실행).
1. screen 실행이 끝나면: `python experiments/exp029_dpnew_mirror/judge29.py screen` 1회. stdout 저장: `experiments/exp029_dpnew_mirror/judge-screen.txt`
2. **`prep29.py stage2` 와 stage2 경기는 실행하지 않는다.** (EXP-029 는 여기서 종료)

## 2. EXP-030 screen (4,980경기)
`EXP024_OUT=experiments/exp030_dpnew_bypass/games-screen.jsonl python experiments/exp024_round2/run.py experiments/exp030_dpnew_bypass/jobs-screen.json`
→ `python experiments/exp030_dpnew_bypass/judge30.py screen` (stdout → `experiments/exp030_dpnew_bypass/judge-screen.txt`)
- `INCOMPLETE` assert 면 run.py 를 같은 명령으로 1회 재실행(기존 key skip) 후 judge 재시도. 두 번째도 실패면 STOP·보고.

## 3. EXP-030 final
`python experiments/exp030_dpnew_bypass/prep30.py final`
- `NO_ADVANCE` 면 여기서 종료하고 "EXP-030 NO_ADVANCE" 보고.
`EXP024_OUT=experiments/exp030_dpnew_bypass/games-final.jsonl python experiments/exp024_round2/run.py experiments/exp030_dpnew_bypass/jobs-final.json`
→ `python experiments/exp030_dpnew_bypass/judge30.py final` (stdout → `experiments/exp030_dpnew_bypass/judge-final.txt`)

## STOP 조건
sha 불일치 / run.py 예외로 중단 / 디스크 부족 / 이 카드에 없는 명령이 필요해짐 → 즉시 멈추고 한 줄 보고.

## 보고 (`coordination/reports/antigravity/<ts>-EXP030.md`, 10줄 이내)
각 단계 완료 시각, 경기 수, judge stdout 첫 줄. 판정 해석·릴리스 제작은 하지 않는다(Claude 가 독립 검증).


---

## `proposals/claude/20260927-EXP031-FAMILY-CENSUS-ANTIGRAVITY.md`

# EXP-031 실행 카드 (antigravity) — v074·v171 hosted 상대 계열 집계 (판단 없음)
발행: Claude 2026-09-27 16:20 KST. **사람 승인(16:00): 이 카드 범위의 Kaggle episode·replay·leaderboard 다운로드.** 제출 금지.
목적: 09-26 이후 hosted 상대 중 **55be5d5f 계열 / 127ed3e6 계열 / 기타** 비중과 v074·v171 의 W/D/L. 해석은 Claude 가 한다.
금지: 제출, 스크립트 수정, 다른 폴더 쓰기, holdout seed 9000–9599, EXP-030 방해(fingerprint 는 2 worker 고정).
토큰 규칙: `run_all.sh` 를 nohup 으로 띄우고 `while kill -0 PID 2>/dev/null; do sleep 120; done` 한 번으로 대기. 중간 보고 없음.

입력 sha(`shasum -a 256`, 다르면 STOP): step1_2_collect.py 426c00f3e132…, step3_download_replays.py 1508d82adeb8…, step4_5_fingerprint.py 50d115931004…, run_all.sh 162a4dbc579b…
(모두 `analysis/v074_hosted_20260927/`. 기존 v171 파이프라인 복사본이며 대상 submission·ref 목록·worker 수만 바뀌었다.)

1. `nohup bash analysis/v074_hosted_20260927/run_all.sh > analysis/v074_hosted_20260927/run_all.log 2>&1 &` → 대기.
2. 끝나면 `tail -5 analysis/v074_hosted_20260927/run_all.log` 와 `summary.json` 존재 확인.

STOP: sha 불일치, 인증 오류, 429 가 반복되어 step3 가 30분 넘게 진행 없음, 스크립트 예외.
보고(`coordination/reports/antigravity/<ts>-EXP031.md`, 10줄): 수집 episode 수(v074/v171), replay 누락 수, run_all.log 마지막 줄, 소요 시간. 해석하지 않는다.


---

## `proposals/claude/20260927-EXP032-KAGGLE-ANTIGRAVITY.md`

# EXP-032 실행 카드 (antigravity) — Kaggle notebook 5개로 specialist gate 실행 (판단 없음)
발행: Claude 2026-09-27 16:50 KST. 사람 승인(15:43): pilot PASS 시 Kaggle notebook 5개 동시 사용, private 한정.
금지: `--public`, 대회 제출, 스크립트 수정, Mac 에서 게임 실행, 다른 dataset/kernel 수정·삭제.
토큰 규칙: 상태 확인은 10분 간격 최대 12회. 보고 10줄.
입력 sha(`shasum -a 256`, 다르면 STOP): experiments/kaggle_pilot/make_kaggle.py 3b24f25d1a93…, experiments/exp032_specialist/jobs.json 34e32358536d…, judge32.py 26fabb76880c…

1. `USER=$(kaggle config view | awk '/username/{print $NF}')`
2. `python experiments/kaggle_pilot/make_kaggle.py $USER experiments/exp032_specialist/jobs.json exp032 5` → `jobs 2540 … per_shard [508×5]` 확인.
3. `kaggle datasets create -p experiments/kaggle_runs/exp032/dataset` (private 기본값). ready 될 때까지 대기(`kaggle datasets status $USER/kaggriculture-exp032`).
4. k=0..4: `kaggle kernels push -p experiments/kaggle_runs/exp032/kernel$k`
5. 5개 모두 complete 까지 대기(예상 60–70분, 최대 150분). error 인 kernel 은 output 만 받고 보고에 기록(재실행하지 않는다).
6. k=0..4: `kaggle kernels output $USER/kaggriculture-exp032-k$k -p experiments/kaggle_runs/exp032/out/k$k`
7. `cat experiments/kaggle_runs/exp032/out/k*/games-*.jsonl > experiments/exp032_specialist/games.jsonl && wc -l experiments/exp032_specialist/games.jsonl`
8. `python experiments/exp032_specialist/judge32.py > experiments/exp032_specialist/judge.txt 2>&1; head -3 experiments/exp032_specialist/judge.txt`

STOP: sha 불일치, ENGINE_MISMATCH, 동시 세션 한도 오류(한도 메시지 원문을 보고), 카드에 없는 명령 필요.
보고(`coordination/reports/antigravity/<ts>-EXP032.md`): kernel 별 상태·소요, games.jsonl 행 수, judge.txt 첫 줄. 해석하지 않는다.


---

## `proposals/claude/20260927-EXP033-KAGGLE-ANTIGRAVITY.md`

# EXP-033 실행 카드 (antigravity) — hosted 상대 tape panel 을 Kaggle 5개로 (판단 없음)
발행: Claude 2026-09-27 19:45 KST. 사람 승인(15:43): Kaggle notebook 5개, private 한정. EXP-032 카드와 같은 절차.
금지: `--public`, 제출, 스크립트 수정, Mac 에서 게임 실행. 토큰 규칙: 상태 확인 10분 간격 최대 10회, 보고 10줄.
입력 sha: experiments/exp033_tapes/jobs-kaggle.json dd5fcad97f72…, make_kaggle.py 3b24f25d1a93…
1. `USER=$(kaggle config view | awk '/username/{print $NF}')`
2. `python experiments/kaggle_pilot/make_kaggle.py $USER experiments/exp033_tapes/jobs-kaggle.json exp033 5` → `jobs 2100 … per_shard [420×5]`
3. `kaggle datasets create -p experiments/kaggle_runs/exp033/dataset` → ready 대기
4. k=0..4 `kaggle kernels push -p experiments/kaggle_runs/exp033/kernel$k`
5. 모두 complete 대기(예상 50–60분, 최대 120분). error 는 output 만 받고 기록.
6. k=0..4 `kaggle kernels output $USER/kaggriculture-exp033-k$k -p experiments/kaggle_runs/exp033/out/k$k`
7. `cat experiments/kaggle_runs/exp033/out/k*/games-*.jsonl > experiments/exp033_tapes/games-kaggle.jsonl && wc -l experiments/exp033_tapes/games-kaggle.jsonl`
STOP: sha 불일치, ENGINE_MISMATCH, 세션 한도 오류. 보고(`coordination/reports/antigravity/<ts>-EXP033.md`): kernel 상태·소요, 행 수. 해석 금지.


---

## `proposals/claude/20260927-EXP034-RUNTIME-ANTIGRAVITY.md`

# EXP-034 실행 카드 (antigravity) — Kaggle 1개 kernel 로 순차 runtime 측정 (판단 없음)
발행: Claude 2026-09-27 19:55 KST. 사람 승인 범위(Kaggle private notebook) 안. EXP-033 과 동시 실행 가능하면 함께 띄운다(세션 한도 오류면 EXP-033 끝난 뒤).
금지: `--public`, 제출, 스크립트 수정. 보고 8줄.
입력 sha: experiments/exp034_runtime/jobs.json, rt_kernel.py (아래 출력값을 보고에 적는다)
1. `USER=$(kaggle config view | awk '/username/{print $NF}')`
2. `python experiments/kaggle_pilot/make_kaggle.py $USER experiments/exp034_runtime/jobs.json exp034rt 1`
3. `cp experiments/exp034_runtime/rt_kernel.py experiments/kaggle_runs/exp034rt/kernel0/run_kernel.py`
4. `kaggle datasets create -p experiments/kaggle_runs/exp034rt/dataset` → ready 대기 → `kaggle kernels push -p experiments/kaggle_runs/exp034rt/kernel0`
5. complete 대기(예상 15–25분) → `kaggle kernels output $USER/kaggriculture-exp034rt-k0 -p experiments/kaggle_runs/exp034rt/out`
6. `cp experiments/kaggle_runs/exp034rt/out/rt.jsonl experiments/exp034_runtime/rt.jsonl && wc -l experiments/exp034_runtime/rt.jsonl`
보고(`coordination/reports/antigravity/<ts>-EXP034.md`): 상태, 행 수(24 기대), sha. 해석 금지.


---

## `proposals/claude/20260927-EXP036-ANTIGRAVITY.md`

# EXP-036 실행 카드 (antigravity) — d157 ±1 screen → stage2 (Kaggle 5개 + Mac 병렬, 판단 없음)
발행: Claude 2026-09-27 22:15 KST. 사람 승인 범위(Kaggle private notebook 5개, Mac 실행). 밤새 무인 실행 전제.
금지: `--public`, 제출, 스크립트·기준 수정, holdout 9000–9599. Mac 은 `caffeinate -dimsu` 가 켜져 있어야 한다(없으면 먼저 실행).
토큰 규칙: 긴 단계는 nohup + 단일 대기 명령. Kaggle 상태 확인은 10분 간격. 중간 보고 없음, 최종 보고 12줄.
입력 sha(다르면 STOP): make_kaggle2.py 1cff6a2d9dfe…, prep36.py 636a67926f4f…, judge36.py 29026970f221…, jobs-screen-kaggle.json 276e8ce2a389…, jobs-screen-mac.json 5f14f2d30459…
(모두 experiments/exp036_d157plus/ 또는 experiments/kaggle_pilot/)

## A. screen (7,900경기)
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp036_d157plus/jobs-screen-kaggle.json exp036s 5
3. kaggle datasets create -p experiments/kaggle_runs/exp036s/dataset → ready 대기 → k=0..4: kaggle kernels push -p experiments/kaggle_runs/exp036s/kernel$k
   (datasets create 가 실패하면 1회만 재시도, 또 실패하면 Kaggle 몫도 Mac 에서 돌린다: 아래 4번 명령을 jobs-screen-kaggle.json / games-screen-kaggle.jsonl 로 한 번 더, Mac 몫이 끝난 뒤)
4. Mac 동시 실행: EXP024_OUT=experiments/exp036_d157plus/games-screen-mac.jsonl nohup python experiments/exp024_round2/run.py experiments/exp036_d157plus/jobs-screen-mac.json > experiments/exp036_d157plus/run-screen-mac.log 2>&1 &
5. 둘 다 끝나면: k=0..4 kaggle kernels output $USER/kaggriculture-exp036s-k$k -p experiments/kaggle_runs/exp036s/out/k$k ; cat experiments/kaggle_runs/exp036s/out/k*/games-*.jsonl > experiments/exp036_d157plus/games-screen-kaggle.jsonl
6. python experiments/exp036_d157plus/judge36.py screen > experiments/exp036_d157plus/judge-screen.txt 2>&1 ; head -1 그 파일
   - INCOMPLETE 면 누락 job 이 속한 쪽(Mac: 4번 명령 재실행, 기존 key skip / Kaggle: 해당 kernel 만 push 재시도 1회) 후 재판정. 두 번째도 실패면 STOP.
   - advance 가 빈 목록이면 여기서 종료, 보고.
## B. stage2 (advance 8개 기준 약 8,500경기)
7. python experiments/exp036_d157plus/prep36.py stage2
8. A 의 2–5 를 tag exp036t, jobs-stage2-kaggle.json / jobs-stage2-mac.json, games-stage2-*.jsonl 로 반복.
9. python experiments/exp036_d157plus/judge36.py stage2 > experiments/exp036_d157plus/judge-stage2.txt 2>&1 ; head -1
STOP: sha 불일치, ENGINE_MISMATCH, 세션 한도, 카드에 없는 명령 필요.
보고(coordination/reports/antigravity/<ts>-EXP036.md): 단계별 완료 시각·행 수, judge-screen / judge-stage2 첫 줄. 해석 금지.


---

## `proposals/claude/20260927-H1-CODEX.md`

# H1 카드 (Codex) — v074 + post-92 gated sale lead (HYPGEN H1) 구현·1차 검증
발행: Claude 2026-09-27 16:50 KST. 근거: `coordination/reports/codex/20260927-1615-HYPGEN.md` §B H1. 보고 목표 **20:00 KST**.
금지: 제출, 다운로드, holdout 9000–9599, 기존 파일 수정, 결과 본 뒤 detector/기준 변경. 게임은 **1 worker**(EXP-030 이 Mac 사용 중).
쓰기: `experiments/h1_0927/`, 보고서 1개.

## 고정 사양 (실행 전 `experiments/h1_0927/prereg.json` 에 sha 와 함께 기록)
- 부모 P = `releases/round2-v074/main.py`(860a502c). 부모 바이트 뒤 wrapper 만 추가, 새 마지막 top-level callable 로 진입.
- detector: HYPGEN 보고서 그대로(step 92, own−rival money ∈ {87,90}, 직전 own action 에 WHEAT 3 SELL). flag 는 한 번 켜지면 유지. **flag=false 면 부모 action 을 그대로 반환**(객체 동일).
- lead: step 144–717, 부모가 다음 1–4 step 에 낼 SELL 중 MILK/STRAWBERRY/WOOL 을 현재 shed 재고·10-order cap·price≥2 한도에서 앞당기고 같은 수량을 원래 step 에서 차감(unit credit). 구현 방식은 Codex 판단이나 “미래 SELL” 은 부모를 부작용 없이 미리 호출할 수 없다면 55be5d5f Step738(`main.py:7500-7559`) 방식처럼 native tape 조회로 한다. 불가능하면 STOP·보고.
## 1차 검증 (36경기, seed 14400–14405 × 양 좌석)
- FP gate: vs 127ed3e6 12경기 + vs PUB01·PUB12(`experiments/exp027_stage3/manifest.json` guard) 각 6경기 = 24경기: activation 0 이고 act_sha 가 부모 P 와 **전부 동일**해야 한다(부모 P 도 같은 seed 로 실행).
- 효과: vs D(55be5d5f) 12경기: activation 12/12, 그리고 (H1 − P) paired score 점추정 > 0.
- 하나라도 실패 → FAIL(기준 변경 금지). 통과 → PASS 와 함께 variant 경로·sha 보고(대규모 검증은 Claude 가 Kaggle 로 진행).
## 보고 (`coordination/reports/codex/<ts>-H1.md`, 60줄 이내): 첫 줄 PASS/FAIL, 표(패널·경기·activation·act_sha 동일 수·score H1/P), variant sha, runtime max step, 다음 행동 2개.


---

## `proposals/claude/20260927-HYPGEN-CODEX.md`

# HYPGEN-0927 카드 (Codex) — 55be5d5f 가 v074 를 이기는 메커니즘 → 반격 가설 생성
발행: Claude 2026-09-27 16:00 KST. 보고 목표 **19:30 KST**. 판단 작업(가설 생성·설계). 
금지: 제출, Kaggle 다운로드, holdout seed 9000–9599, 기존 파일 수정, EXP-030 실행 방해(게임은 **1 worker, 최대 12경기**).
쓰기 허용: `experiments/hypgen_0927/`, 보고서 1개. 토큰 규칙: grep/head 로 필요한 부분만, 중간 보고 없음.

## 배경 (사실)
- 최종 순위 = 마감 후 ~2주 경기까지 포함, **활성 bot 끼리의 전체 경기로 BT 재적합**. hosted field 는 공개 tape/bot 복제가 대다수(discussion 740437: 상대 25/26 이 공개 tape 와 >60% 일치).
- 55be5d5f(09-27 공개, `releases/public-dpnew-55be5d5f-exact/main.py`) = 127ed3e6 + `_V93_ROUTE_BY_RIVAL` + Step7xx–1009 sale-timing layer.
- EXP-028(`experiments/exp028_dpnew/games.jsonl`): **D(55be5d5f) vs v074 직접 대결 0.88**(opponent `X-D-vs-P`, seed 12300–12349 양 좌석), vs 127ed3e6 D 0.885 / v074 0.870, 공개 guard 23 파일에서는 D 0.82 < v074 0.97, hosted-replay 121: D 0.851 < v074 0.926.
- 즉 55be5d5f 는 "127 계열 전문 킬러, 일반 수입은 약함". 55be 복제가 field 에 늘면 v074(현재 활성, 약 2216)가 떨어진다.
- EXP-029 screen(`experiments/exp029_dpnew_mirror/judge-screen.txt`): 55be5d5f ±1 변형 d157 등이 55be5d5f 자기 복제에 0.8(기준 0.5).
- EXP-030(진행 중): 55be5d5f layer 1개씩 bypass → 일반 수입 회복 후보 탐색.

## 과제
### A. 메커니즘 (근거 필수)
1. 직접 대결 50 seed×2 좌석 중 **최대 12경기**를 골라(큰 margin D 승 6, 근소 D 승 3, D 패/무 3) 양쪽 per-step action 을 기록하며 재실행한다(`experiments/exp024_round2/run.py` 의 play 를 복사해 trace 추가; 결과 rewards 가 games.jsonl 과 같아야 함 — 다르면 STOP).
2. 첫 행동 분기 step, 분기 후 **어느 품목의 매도 시점/수량**이 shared demand 를 선점하는지, 그 차이를 만든 55be5d5f 의 코드 위치(layer 이름·줄번호)를 특정한다. rival 감지(`_V93_ROUTE_BY_RIVAL`)가 v074 를 어떻게 식별하는지(어느 step, 어떤 관측) 확인한다.
### B. 반격 가설 (최대 5개, 우선순위순)
각 가설: 메커니즘 1줄 | 발동 조건(55be 계열 감지 신호·step) | 구현(부모 바이트 뒤 wrapper, 어느 action 필드) | 부모 후보(v074 / EXP-030 후보 / 둘 다) | 예측(vs D, vs 127ed3e6, vs 기타 각각 방향) | 반증 기준 | 시험 비용(경기 수).
- 우선: 55be 계열에서만 발동해 다른 상대 성적을 건드리지 않는 것, 그리고 55be 의 rival 감지를 무력화/역이용하는 것.
- 가설이 "구현 불가/효과 없음"으로 결론 나도 그 근거를 쓴다(억지 가설 금지).
### C. 두 슬롯 포트폴리오
field 시나리오(127 계열 %, 55be 계열 %, 기타 %) 3–4개에서, 기존 로컬 행렬(EXP-028, EXP-029 screen, 가능하면 EXP-030 screen)로 후보 쌍 {v074, EXP-030 최상위, 55be5d5f exact, d157, v074 exact 재제출}의 **E[max]** 대리지표를 비교하고, 시나리오에 강건한 쌍과 제출 순서를 권고한다. 가정·한계 명시.

## 보고 (`coordination/reports/codex/<ts>-HYPGEN.md`, 150줄 이내)
첫 줄: 가장 유망한 가설 1개 + 확신도. A 결과(표), B 가설 표, C 권고, 다음 행동 2개, 사람이 결정할 질문 2개.


---

## `proposals/claude/20260927-INSIGHT-SWEEP-CODEX.md`

# INSIGHT-SWEEP 카드 (Codex) — 점수 외 공개 인사이트 재수집
발행: Claude 2026-09-27 15:45 KST. 사람 지시: 점수가 높지 않은 공개 자료에서도 놓친 인사이트가 있는지 확인한다.
목표 시각: **17:30 KST** 보고. 읽기 전용.
금지: 경기 실행(Mac CPU는 EXP-030 사용 중), Kaggle 다운로드·제출, 보고서 외 파일 쓰기, 이미지 해석 시도.
토큰 규칙: 파일은 필요한 부분만 grep/head 로 읽는다. 전문 인용 금지(한 줄 요약+위치). 중간 보고 없음.

## 입력
1. discussion: `docs/discussion/*.md` 19개. `docs/review_insights.md` §8 이 이미 다룬 7개는 건너뛴다(09-07 이후 글만).
2. notebook 설명부: `docs/collection_snapshots/<slug>__<최신날짜>/*.ipynb` 의 markdown cell 과 저장된 output 텍스트.
   대상 = `analysis/daily_scan/20260927/new.json`·`lineage.json` 의 votes 상위 30개 중 `review_insights.md` §7 미검토분.
   **점수·코드 계보와 무관하게** 메커니즘 주장(엔진 규칙, 시장/가격, 판매 타이밍, 이동/물류, shop world, mirror/race, 버그)을 찾는다.
3. 이미 확인된 것(재보고 불필요): vote 1위 kaggricult-man 의 제출물은 no-op(Project doc 26). 단 그 notebook 의 **주장**(day-6 shop pair→route 표, 목록 밖 pair→plan 0 fallback, T4 adaptive sale lead-1/lead-2 + unit credit, 64 shop world coverage)은 평가 대상에 포함.

## 우리 bot 에 이미 있는지 확인할 기준 파일
- v074: `releases/round2-v074/main.py` (127ed3e6 계열 + ±1 knife-edge 변형; race horizon mirror 24/escalated 24, `_terminal_liquidation`, route tape)
- 55be5d5f: `releases/public-dpnew-55be5d5f-exact/main.py` (위 + `_V93_ROUTE_BY_RIVAL` + Step7xx–1009 sale-timing layer)
- 판정은 grep 근거(변수/함수명 + 줄번호)로. 근거를 못 찾으면 `UNSURE` 로 쓰고 추정하지 않는다.

## 보고 (`coordination/reports/codex/<ts>-INSIGHT-SWEEP.md`, 120줄 이내)
첫 줄: 실행 가능 가설 수와 최우선 1개.
표(최대 10행, 우선순위순): id | 주장 1줄 | 출처(파일·cell/줄) | 근거 유형(측정/주장/일화) | v074 에 있음? | 55be5d5f 에 있음? | wrapper 로 구현 가능?(hook: 어느 step·어느 action 필드) | 127 계열 상대 W/D/L 에 영향 주는 경로 | 시험 비용(경기 수 추정)
우선순위 기준: (1) 우리 bot 에 없음 (2) 부모 바이트 뒤 wrapper 로 구현 가능 (3) 근거가 측정값 (4) mirror/near-clone 경기의 승부에 닿음.
별도 목록(최대 5개): 실행 불가하지만 알아야 할 사실(엔진 규칙·버그·평가 방식).
마지막: 다음 행동 2개.


---

## `proposals/claude/20260927-KAGGLE-PILOT-ANTIGRAVITY.md`

# KAGGLE-PILOT 카드 (antigravity) — 판단 없음, 고정 명령만
발행: Claude 2026-09-27 15:45 KST. 사람 승인(15:30): 우리 코드를 **private** Kaggle dataset 으로 올려 notebook pilot 1개 실행.
목적: Kaggle CPU notebook 이 Mac 과 **같은 결과**를 내는지, 처리량이 얼마인지 확인.
금지: `--public` 옵션, 대회 제출, 다른 dataset/notebook 수정·삭제, 스크립트 수정, EXP-030 실행 방해(Mac 에서 게임 실행 금지 — 이 카드는 Kaggle 서버에서만 게임을 돌린다).
토큰 규칙: 상태 확인은 5분 간격 최대 8회. 보고 10줄 이내.

입력 sha(`shasum -a 256`, 다르면 STOP): make_pilot.py fc10829d302f…, compare_pilot.py e872e058ad7c…, kernel/pilot_kernel.py 92d7edae532b…

1. `USER=$(kaggle config view | awk '/username/{print $NF}')` 로 사용자명 확인.
2. `python experiments/kaggle_pilot/make_pilot.py $USER` → 출력 `jobs 60 files 63 …` 확인.
3. `kaggle datasets create -p experiments/kaggle_pilot/dataset` (**private 기본값, --public 금지**). 이미 있으면 `kaggle datasets version -p experiments/kaggle_pilot/dataset -m pilot`.
4. dataset 처리 완료 후(`kaggle datasets status $USER/kaggriculture-pilot-0927` 가 ready) `kaggle kernels push -p experiments/kaggle_pilot/kernel`.
5. `kaggle kernels status $USER/kaggriculture-pilot-0927-run` 가 complete 가 될 때까지 대기(최대 40분). error 면 `kaggle kernels output … -p experiments/kaggle_pilot/out` 로 로그만 받고 STOP·보고.
6. `kaggle kernels output $USER/kaggriculture-pilot-0927-run -p experiments/kaggle_pilot/out`
7. `python experiments/kaggle_pilot/compare_pilot.py` → stdout 을 `experiments/kaggle_pilot/compare.txt` 에 저장.

STOP: sha 불일치, internet 설정 불가 오류, ENGINE_MISMATCH, 카드에 없는 명령이 필요할 때.
보고: `coordination/reports/antigravity/<ts>-KAGGLE-PILOT.md` — compare.txt 첫 줄, dataset/kernel URL, 소요 시간. 해석하지 않는다.


---

## `proposals/claude/20260927-LATE-CODEX.md`

# LATE-0928 카드 (Codex) — v074 막판(step ≥ 576) 판매·청산 단일 변경 설계·screen
발행: Claude 2026-09-27 20:40 KST. 목표: 1차 보고 **09-28 09:00 KST**(설계+screen), 최종 판정 09-28 18:00. 판단 작업(상위 모델 권장).
근거: REVIEW-0927C Q4 경로 2 — v074 가 127 변형에 진 43경기의 현금 격차가 step576 −34 → step648 −177 → step719 −226 로 벌어짐(`experiments/review_0927c/analysis.json:55-105`). d157 의 유일한 차이도 막판 fixed-sell closure pass(`_S1002_PASSES` 34→35, `releases/exp035-d157/main.py:9949-9975`).
금지: 제출, Kaggle 다운로드, holdout 9000–9599, 기존 파일 수정, 결과 본 뒤 기준 변경. 쓰기: `experiments/late_0928/`, 보고서.
CPU: Mac 은 이제 비어 있음(5 worker 허용). 대규모는 Kaggle(`experiments/kaggle_pilot/make_kaggle.py`, antigravity 실행) 로 넘길 jobs 파일만 만든다.

## 과제
1. **원인 특정 (게임 추가 ≤ 30, 1 worker)**: `experiments/exp033_tapes/tapes/`(hosted 상대 tape) 중 127 변형 패배 경기에서 v074 와 d157 을 같은 tape 로 돌려(`experiments/exp024_round2/run.py` 의 play 형식; tape 파일은 agent 로 바로 로드됨) step 576 이후 **품목별 매도 수량·체결가·shed 잔량**을 비교. 어느 품목·시점에서 v074 가 현금을 잃는지 표로.
2. **단일 변경 후보 ≤ 3개 설계**: v074 부모 바이트 뒤 wrapper, **step < 576 에서는 action 이 부모와 byte 동일**(act 비교로 확인). 예: (a) d157 계열 fixed-sell closure 를 v074 막판에만 이식, (b) 청산 시작 step/분할 조정, (c) 1번에서 드러난 특정 품목 선매. 각 후보에 메커니즘 근거와 반증 기준.
3. **사전등록 후 screen**: `experiments/late_0928/prereg.json` 에 기준 고정 후
   - open-loop: 127 변형 tape 112개 + 기타 tape 93개, (cand − v074) paired.
   - closed-loop: vs 127ed3e6 exact 50 seed×2, guard 23×5 seed×2, vs 55be5d5f 25×2 (Kaggle jobs 파일로 준비).
   - 통과: 127 변형 tape (cand−v074) lower95 > 0, 기타 tape point ≥ −0.02, closed-loop 127/guard 각 point ≥ −0.03, runtime(1 worker) max < 0.8.
4. 통과 후보가 있으면 release 준비 없이 sha 와 판정만 보고(Claude 가 D3·release).
## 보고 (`coordination/reports/codex/<ts>-LATE.md`, 100줄): 첫 줄 판정, 원인 표, 후보 표, screen 결과(진행 중이면 jobs 경로), 다음 행동 2개.


---

## `proposals/claude/20260927-REVIEW-0927C-CODEX.md`

# REVIEW-0927C (Codex) — 오늘 밤 A 슬롯 계획 검토 + 127 변형 격파·2400+ 경로
발행: Claude 2026-09-27 19:50 KST. 보고 목표 **21:15 KST**. 판단 작업(상위 모델·높은 reasoning 권장).
금지: 제출, Kaggle 다운로드, holdout seed 9000–9599, 기존 파일 수정, EXP-030 final(Mac 5 worker) 방해 — 새 게임은 **1 worker, 최대 16경기**, 쓰기는 `experiments/review_0927c/` 와 보고서 1개.
토큰 규칙: 필요한 부분만 grep/head, 중간 보고 없음. 모든 주장에 근거(파일:줄, 재집계 명령, 계산식). 근거 없으면 `UNSURE`.

## 1. 현재 사실 (재검증 대상)
- 활성: v171(56567563) / v074(56577440), rating 약 2212/2216, bronze 경계 약 2290. FIFO: 다음 제출은 v171 은퇴.
- 최종 순위 = 마감(09-30 23:59 UTC) 후 약 2주 경기까지 포함, 활성 bot 끼리의 전체 경기로 BT 재적합(`docs/official/evaluation.md`, Project doc 03 §2.1 인용). 은퇴 bot 의 경기는 제외.
- EXP-031 hosted census(`analysis/v074_hosted_20260927/opponents.csv`, 350경기): v074 vs **127 변형(prefix<720) 52경기 0.163**, 127 exact 0.887, 기타 0.50, DP/55be 변형 0.50, 55be exact 1경기(패). 127 변형 상대 LB 중앙값 2272, 112명 중 73명이 2200–2400.
- EXP-032(`experiments/exp032_specialist/judge.txt`, Kaggle 2,540경기, 판정규칙 `judge32.py` docstring): d157 vs D 0.85(P 0.04), vs O127 0.86(P 0.88), guard23 0.846(P 0.989), hosted-replay −0.075; 시나리오 transition +0.19(lower +0.14). **FAIL 사유는 runtime 하나**: Kaggle 4병렬에서 max_step d157 1.63s(>0.8 279/880경기), P 0.29s. Mac 에서는 d157 0.43s.
- EXP-033(진행 중, 부분): hosted 상대 tape(open-loop) 127 변형 17–18 ep: D 0.667, d157 0.706, d053 0.706, P 0.333, V171 0.265. 자기 bot 재현 17/17 exact. 전체는 Kaggle 로 재실행 중(`experiments/exp033_tapes/`).
- EXP-030(`experiments/exp030_dpnew_bypass/`): screen 통과 b020 1개, final 진행 중(`judge30.py` frozen).
- EXP-034(대기): Kaggle 1 kernel 순차 runtime 측정(d157, D, P, b020; `experiments/exp034_runtime/rt_kernel.py`).
- 폐기: H1(`coordination/reports/codex/20260927-1639-H1.md`), marketshock/12ad317e(no-op).

## 2. 검토 질문
Q1. **계획 타당성**: "EXP-034 runtime 안전 → d157 을 A(=v171 교체) 1순위, 위험 → b020(EXP-030 final 통과 시) 또는 55be 속도 개선" 이 맞는가? 판정 순서·기준·빠진 위험(예: open-loop 낙관 편향, Kaggle max_step 의 대표성, d157 의 winner's curse, 55be exact 공개 확산)을 짚고 보완하라.
Q2. **runtime 경계선**: 1초 초과 턴이 게임당 수십 번·초과 합계 10–30초면 제출을 감수해야 하는가? hosted 제약(vCPU 1.6·actTimeout 1s·remainingOverageTime 60s — `docs/official/frequently_asked_questions.md` 는 값이 템플릿 placeholder 이므로 engine `kaggriculture.json` 설정과 Project doc 03 §2.2 기록값을 쓰고 출처를 명시)을 근거로 **정량 기준**을 제시하라. 가능하면 55be5d5f 에서 가장 느린 layer 를 코드/프로파일로 특정하고(1 worker, ≤4경기 cProfile 허용), 결과를 바꾸지 않는 속도 개선(캐싱 등) 가능성과 검증 방법을 제시하라.
Q3. **v074 유지 가치**: 127 변형·기타 2200–2400 에서 v074 가 0.185/0.30 인 상황에서, 09-28 에 두 번째 슬롯도 55be 계열(다른 후보)로 바꾸는 게 E[max final BT] 를 높이는가? 두 슬롯이 같은 계열일 때의 상관 위험 포함. **E[max] 는 bot 별 전체 field 가중 점수의 max** 로 계산하라(상대 계열별 max 합산 금지).
Q4. **127 변형을 이기고 2400+ 로 가는 방법**: 남은 시간(제출 마감 10-01 08:59 KST, Mac 1대 ≈ 1,500경기/h + Kaggle 5 kernel ≈ 2,400경기/h)에서 현실적인 경로를 우선순위로 최대 4개. 각 경로: 메커니즘 근거(EXP-031 패배 경기 replay 분석 가능: `private_artifacts/v074_hosted_20260927/raw/`, tape 는 `experiments/exp033_tapes/tapes/`), 구현 방식(부모·wrapper), 검증 설계(open-loop tape + closed-loop 둘 다), 소요 시간, 성공 시 기대 rating 변화의 근거 있는 범위, 실패 조건. 2400+ 가 근거상 비현실적이면 그렇게 결론 내라.
  - 참고 관점: 127 변형 상대들은 어디서(prefix step 분포) 무엇을 바꿨나? 우리 패배는 어느 품목·시점에서 갈리나? 55be 계열이 이기는 이유가 같은 메커니즘인가?
Q5. Claude 가 놓친 것 1–3개.

## 3. 출력 (`coordination/reports/codex/<ts>-REVIEW-0927C.md`, 150줄 이내)
첫 줄: Q1 판정(타당/조건부/부적절) + 오늘 밤 A 슬롯 권고 한 문장.
Q1–Q5 각각: 결론, 근거, 확신도(0–1). Q4 는 표.
마지막: 오늘 밤 실행할 행동 2개(명령 수준), 사람이 결정할 질문 2개.


---

## `proposals/claude/20260928-EXP037-D157-HOSTED-ANTIGRAVITY.md`

# EXP-037 실행 카드 (antigravity) — d157 hosted 초기 경기 수집·계열 집계 (판단 없음)
발행: Claude 2026-09-27 23:35 KST. **실행 시각: 즉시**(09-27 23:40 사람 지시). 09-28 08:00 이후 같은 명령으로 한 번 더 실행해 경기를 보충한다(이미 받은 replay 는 건너뜀). 사람 승인(09-27 16:00 범위와 동일): 이 카드 범위의 Kaggle episode·replay·leaderboard 다운로드. 제출 금지.
EXP-031 과 같은 파이프라인 복사본(대상만 d157 56607884 + v074 56577440, fingerprint 에서 우리 bot 경로만 d157 로 변경).
입력 sha: step1_2_collect.py b67c38ff664f…, step3_download_replays.py 17af25c70e56…, step4_5_fingerprint.py bc89ecc5686f…, run_all.sh c6794ba6f430… (모두 analysis/d157_hosted_20260928/)
1. EXP-036 과 동시에 실행해도 된다(fingerprint 는 2 worker 고정, EXP-036 은 조금 느려질 수 있음).
2. `nohup bash analysis/d157_hosted_20260928/run_all.sh > analysis/d157_hosted_20260928/run_all.log 2>&1 &` → 단일 대기.
3. `tail -3 analysis/d157_hosted_20260928/run_all.log`
STOP: sha 불일치, 인증 오류, 30분 넘게 429 반복, 예외. 보고(`coordination/reports/antigravity/<ts>-EXP037.md`, 8줄): 수집 수(d157/v074), 누락, 로그 마지막 줄. 해석 금지.


---

## `proposals/claude/20260928-EXP038-ANTIGRAVITY.md`

# EXP-038 실행 카드 (antigravity) — family arena (Kaggle 5 + Mac 병렬, 판단 없음)
발행: Claude 2026-09-28 12:40 KST. 사람 승인 범위(Kaggle private notebook 5개, Mac). EXP-036 과 같은 절차.
금지: `--public`, 제출, 스크립트·기준 수정, holdout 9000–9599. 토큰 규칙: nohup + 단일 대기, Kaggle 상태 10분 간격, 최종 보고 10줄.
입력 sha(다르면 STOP): make_kaggle2.py 1cff6a2d9dfe…, prep38.py a943ad93150b…, judge38.py 89d2dcb3e5da…, jobs-kaggle.json 2dd8d7b14c67…, jobs-mac.json f6a8eee0498c… (experiments/exp038_family/, experiments/kaggle_pilot/)
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp038_family/jobs-kaggle.json exp038 5
3. kaggle datasets create -p experiments/kaggle_runs/exp038/dataset → ready 대기 → k=0..4: kaggle kernels push -p experiments/kaggle_runs/exp038/kernel$k (실패 시 1회 재시도, 또 실패면 Kaggle 몫을 Mac 에서 Mac 몫 뒤에 실행)
4. 동시에 Mac: EXP024_OUT=experiments/exp038_family/games-mac.jsonl nohup python experiments/exp024_round2/run.py experiments/exp038_family/jobs-mac.json > experiments/exp038_family/run-mac.log 2>&1 &
5. 둘 다 끝나면 k=0..4 output 을 experiments/kaggle_runs/exp038/out/k$k 로 받고 cat .../games-*.jsonl > experiments/exp038_family/games-kaggle.jsonl
6. python experiments/exp038_family/judge38.py > experiments/exp038_family/judge.txt 2>&1 ; head -1 (INCOMPLETE 면 누락 쪽만 1회 재실행 후 재판정)
보고(coordination/reports/antigravity/<ts>-EXP038.md): 완료 시각·행 수, judge.txt 첫 줄. 해석 금지.


---

## `proposals/claude/20260928-EXP039-ANTIGRAVITY.md`

# EXP-039 실행 카드 (antigravity) — d157 + _CA_MARGIN grid (Kaggle 5 + Mac, 판단 없음)
발행: Claude 2026-09-28 14:40 KST. EXP-038 과 같은 절차·금지·토큰 규칙. 최종 보고 10줄.
입력 sha(다르면 STOP): prep39.py 88107a2b1ef6…, judge39.py 7f91aecc56aa…, jobs-kaggle.json cac13d76011e…, jobs-mac.json e92fd971d64c…, make_kaggle2.py 1cff6a2d9dfe… (experiments/exp039_camargin/)
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp039_camargin/jobs-kaggle.json exp039 5
3. kaggle datasets create -p experiments/kaggle_runs/exp039/dataset → ready → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp039/kernel$k (실패 시 1회 재시도, 또 실패면 Kaggle 몫을 Mac 에서)
4. 동시에 Mac: EXP024_OUT=experiments/exp039_camargin/games-mac.jsonl nohup python experiments/exp024_round2/run.py experiments/exp039_camargin/jobs-mac.json > experiments/exp039_camargin/run-mac.log 2>&1 &
5. 끝나면 k=0..4 output → experiments/kaggle_runs/exp039/out/k$k, cat .../games-*.jsonl > experiments/exp039_camargin/games-kaggle.jsonl
6. python experiments/exp039_camargin/judge39.py > experiments/exp039_camargin/judge.txt 2>&1 ; head -1 (INCOMPLETE 면 누락 쪽 1회 재실행)
보고: coordination/reports/antigravity/<ts>-EXP039.md — 완료 시각·행 수·judge 첫 줄.


---

## `proposals/claude/20260928-EXP040-TOP2400-ANTIGRAVITY.md`

# EXP-040 실행 카드 (antigravity) — 2400+ 상위 상대 25개 submission 의 hosted 경기 수집 (판단 없음)
발행: Claude 2026-09-28 14:50 KST. **사람 승인(14:20): 상위 팀 공개 경기 추가 다운로드.** 제출 금지.
대상: d157 을 이긴 LB≥2400 상대 submission 25개(`analysis/top2400_20260928/targets.json`), 각 최대 30경기(COMPLETED·PUBLIC·서로 다른 팀). our_seat = 대상 bot 의 좌석.
입력 sha: analysis/top2400_20260928/step1_2_collect.py e7f4c1e037f7…, step3_download_replays.py 7024cde88ba9… (EXP-037 스크립트 복사본, 대상 목록·폴더만 변경)
EXP-039 와 동시 실행 가능(네트워크 작업, 게임 실행 없음).
1. cd 저장소 루트; nohup sh -c 'python3 analysis/top2400_20260928/step1_2_collect.py > analysis/top2400_20260928/step1_2.log 2>&1 && python3 analysis/top2400_20260928/step3_download_replays.py > analysis/top2400_20260928/step3.log 2>&1 && echo DONE >> analysis/top2400_20260928/step3.log' > /dev/null 2>&1 &
2. 단일 대기 후 `tail -3 analysis/top2400_20260928/step1_2.log analysis/top2400_20260928/step3.log`
STOP: 인증 오류, 30분 넘게 429 반복, 예외. 보고(`coordination/reports/antigravity/<ts>-EXP040.md`, 6줄): 목록 수, replay 수·누락, 소요 시간. 해석 금지.


---

## `proposals/claude/20260928-EXP042-ANTIGRAVITY.md`

# EXP-042 실행 카드 (antigravity) — 2400+ tape panel (Kaggle 5 + Mac, 판단 없음)
발행: Claude 2026-09-28 17:05 KST. EXP-039 와 같은 절차·금지·토큰 규칙. 보고 8줄.
입력 sha: jobs42-kaggle.json c69b174cdc80…, jobs42-mac.json 378f58ba9249…, prep42.py f449997d7826…, make_kaggle2.py 1cff6a2d9dfe… (experiments/exp041_top2400/)
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp041_top2400/jobs42-kaggle.json exp042 5
3. kaggle datasets create -p experiments/kaggle_runs/exp042/dataset → ready → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp042/kernel$k (실패 시 1회 재시도, 또 실패면 Kaggle 몫을 Mac 에서)
4. 동시에 Mac: EXP024_OUT=experiments/exp041_top2400/games42-mac.jsonl nohup python experiments/exp024_round2/run.py experiments/exp041_top2400/jobs42-mac.json > experiments/exp041_top2400/run42-mac.log 2>&1 &
5. 끝나면 k=0..4 output → experiments/kaggle_runs/exp042/out/k$k, cat .../games-*.jsonl > experiments/exp041_top2400/games42-kaggle.jsonl ; wc -l experiments/exp041_top2400/games42-*.jsonl
보고: coordination/reports/antigravity/<ts>-EXP042.md — 완료 시각·행 수(2229 기대). 판정은 Claude.


---

## `proposals/claude/20260928-EXP043-ANTIGRAVITY.md`

# EXP-043 실행 카드 (antigravity) — 약한 5팀 상대 oracle (Kaggle 5 + Mac, 판단 없음)
발행: Claude 2026-09-28 18:15 KST. EXP-042 와 같은 절차·금지·토큰 규칙. 보고 8줄.
입력 sha: prep43.py 94c85a67faeb…, jobs43-kaggle.json 2d897e42991f…, jobs43-mac.json 71f804044904…, make_kaggle2.py 1cff6a2d9dfe… (experiments/exp041_top2400/)
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp041_top2400/jobs43-kaggle.json exp043 5
3. kaggle datasets create -p experiments/kaggle_runs/exp043/dataset → ready → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp043/kernel$k (실패 시 1회 재시도, 또 실패면 Kaggle 몫을 Mac 에서)
4. 동시에 Mac: EXP024_OUT=experiments/exp041_top2400/games43-mac.jsonl nohup python experiments/exp024_round2/run.py experiments/exp041_top2400/jobs43-mac.json > experiments/exp041_top2400/run43-mac.log 2>&1 &
5. 끝나면 k=0..4 output → experiments/kaggle_runs/exp043/out/k$k, cat .../games-*.jsonl > experiments/exp041_top2400/games43-kaggle.jsonl ; wc -l experiments/exp041_top2400/games43-*.jsonl (합계 3900 기대)
보고: coordination/reports/antigravity/<ts>-EXP043.md — 완료 시각·행 수. 판정은 Claude.


---

## `proposals/claude/20260928-EXP045-CODEX.SUPERSEDED.md`

# EXP-045 카드 (Codex, **상위 모델 권장**) — 상대 재고 기반 WOOL/MILK 판매 시점 d157′
발행: Claude 2026-09-28 22:30 KST. 사람 방침(09-28 22:10): 제출하지 않는 선택지는 두지 않고 개선을 계속한다.
마감: 1차 보고 09-29 12:00 KST, 최종(release + D3 포함) 09-29 20:00 KST. 마지막 제출 시한 09-30 21:00 KST.

## 근거 (먼저 읽기, 요약만)
- analysis/exp044_margin/FINDINGS.md (sha 086eaa13…): WHEAT 는 margin 과 무관(r=.01). 분산은 WOOL/MILK 단가에 있다. 같은 step 판매 단가는 동일하고, 차이는 한쪽만 파는 step 에서 난다(패배판 isolated WOOL 42 대 승리판 154).
  결과로 나눈 분해이므로 인과가 아니다. 이 실험이 개입 검증이다.
- analysis/exp044_margin/gpt_answer1-2.md (sha 060d4efe…): GPT-5.6 Sol 의 규칙 후보 A·B. stress tape 는 엔진 상태 수정이라 채택하지 않는다.
- d157 기존 기능과 겹칠 수 있다: _S758 rival-flow lead seller(releases/exp035-d157/main.py:7750–), _front_run(:655–), V9_RACE, _V92_Q. **새 규칙을 넣기 전에 이 셋이 실제로 어떤 조건에서 발동하는지 파일:줄로 보고한다.**

## 작업
1. 코드 조사(≤30분): 위 기능들이 WOOL/MILK 판매량과 시점을 어떻게 결정하는지 파일:줄로 정리한다. 마지막 wrapper(최종 agent) 뒤에 규칙을 붙일 위치를 정한다.
2. 후보는 **최대 2개**(A, B)로 한다. 각각 d157 에 단일 요인 한 개만 더한다: 상대 재고 추정 R_opp(수거 − 역산 판매)를 쓰는 WOOL/MILK SELL veto/hold 규칙.
   상수는 GPT 원안 그대로 쓴다(A: 4/1.15, 5/1.08, P_future 8 step; B: 4, +15%/+8%, 24-step median). 종료 처리(684/696/710)와 shed 임계(85/92/97)도 원안 그대로. 튜닝 금지.
   R_opp 추정이 맞는지 먼저 확인한다: select tape 20판에서 추정 R_opp 와 실제 상대 shed(엔진 로그)의 MAE 를 보고한다. 이 확인은 판정 기준이 아니라 구현 점검이다.
3. prereg.json 을 결과 전에 sha 로 고정한 뒤 실행한다(Kaggle 5 + Mac, make_kaggle2.py). 1-worker smoke 20경기 max step < 0.5s.

## 판정 (결과 전 고정, judge39 형식 재사용: experiments/exp039_camargin/judge39.py sha 7f91aecc…)
기준선은 d157·c26 의 기존 행(games42, exp039)을 쓰고, 기준선을 다시 돌리지 않는다. invalid 0.
- G1 2400+ select 595 tape: 후보−d157 paired 점수 차 점추정 > 0, **팀 cluster bootstrap lower95 > 0**, 그리고 점추정 ≥ c26.
- G2 U 136 + T 350 tape: 각각 점추정 ≥ max(d157, c26).
- G3 family arena(D, HL63, M2965, FJ1010, d157 × seed 15000–15024 × 양 좌석, closed-loop): paired 차 점추정 ≥ 0.
- G4 vs O127, vs V074 각각 ≥ d157 − 0.02.
- 통과 후보 2개면 G1 점추정이 큰 쪽을 고른다. 동률이면 G3.
- 선택된 1개만 holdout 5팀 148 tape 를 **1회** 연다: 점추정 ≥ max(d157, c26) 이면 PASS, 아니면 FAIL.
- 폐기: G1 실패 → LOCAL_FAILED. 기준을 완화하지 않는다.
PASS 이후: releases/exp045-<id>/ (USTAR tar main.py 1개, mtime 0, NOTICE, SHA256SUMS) + D3 gate(experiments/d3_gate_v2/measure_gate_v2_claude.py, 1 worker, 새 프로세스 15경기, max < 0.8s). 제출은 사람이 한다(다음 제출은 FIFO 로 d157 은퇴).

## 금지
제출, 엔진·RNG 수정, 시장 상태 주입(stress tape 포함), holdout seed 9000–9599, 결과 본 뒤 기준·상수 변경, 기존 공용 파일 수정(새 폴더 experiments/exp045_oppstock/ 만).

## 보고 (토큰 절약)
coordination/reports/codex/<ts>-EXP045.md: 첫 줄 판정. 다음으로 G1–G4·holdout 표, 후보 sha, R_opp MAE, 코드 조사 파일:줄 5줄 이내, 다음 행동 2개.


---

## `proposals/claude/20260928-EXP045v2-CODEX.md`

# EXP-045 v2 카드 (Codex, 상위 모델) — 판매 모듈 ablation·변형 11개 구현만 (실행은 antigravity)
**기준 상태:** 활성 d157 56607884 / c26 56635330 (BOARD 09-28 23:30 KST). 카드가 BOARD 보다 최신이면 카드를 따르고, 어긋남은 보고 첫 줄에 적은 뒤 계속한다.
발행: Claude 2026-09-28 23:00 KST. v1(…SUPERSEDED.md)은 d157 에 상대 관측이 없다는 틀린 전제였다.
근거: analysis/exp044_margin/FINDINGS.md(6번 정정 포함), reports45.py 출력(d157 판매 모듈 발동 횟수).
시한: 09-29 07:00 KST(구현 + manifest + jobs). 이후 antigravity 가 실행하고 Claude 가 판정한다.

## 할 일
1. d157(releases/exp035-d157/main.py sha 94a46c11…)의 아래 모듈 각각에 대해 "끄는" 최소 변경을 만든다. 모듈의 apply 가 action 을 그대로 돌려주게 하는 1곳 수정이다. 파일:줄을 적는다.
   K1 _OR2(slot 재배열·rival 추적, :4730–)  K2 _V9_RACE(:3786–)  K3 _S758(:7750–)  K4 _S793(sell mover, :7891–)
   K5 _V92_P(:3406–)  K6 _S738(:7504–)  K7 _V44Y reorder  K8 _S928(:8718–)
2. 새 규칙 3개(가장 바깥 wrapper 뒤에 붙인다):
   G_A GPT 후보 A(WOOL R_opp≥4 AND 가격<1.15×P_future → SELL 보류; MILK 5/1.08; P_future = 8 step 결정적 소비만). R_opp 는 _OR2 의 rival 추적값을 재사용하고, 없으면 수거 − 역산 판매로 계산.
   G_B GPT 후보 B(R_opp≥4 이면 24-step median 대비 WOOL +15%, MILK +8% 이상일 때만 SELL).
   B6 WOOL·MILK 한 턴 판매량 상한 6개(초과분은 다음 턴으로).
   세 규칙 모두 종료 처리(WOOL 684+, MILK 696+ 원래 d157 로 복귀)와 shed 사용량 ≥92 이면 해제. 상수는 이것으로 고정하고 튜닝하지 않는다.
3. experiments/exp045_sale/variants/{K1..K8,G_A,G_B,B6}.py + manifest.json(sha, 변경 줄 수, 파일:줄).
4. smoke: 각 변형 × tape 4판(1 worker). DONE/DONE, max step < 0.5s. 그리고 d157 대비 act_sha 가 달라진 판 수를 보고한다. 4판 모두 같으면 "무발동"으로 표시한다(제외하지 않음).
5. jobs: experiments/exp045_sale/jobs-A-{kaggle,mac}.json = 11 변형 × 2400+ select 595 tape(holdout 제외, prep42 형식, 3:2 분할).
   stage B jobs 는 만들지 않는다(선택 후 Claude 가 만든다).
금지: 실행(smoke 제외), 제출, 엔진·RNG 수정, holdout 팀·seed 9000–9599, 새 폴더 밖 쓰기.
보고: coordination/reports/codex/<ts>-EXP045v2.md — 변형별 sha·파일:줄·smoke 결과(10줄 이내 표).

## 판정 (Claude 사전 고정 — analysis/exp045/PREREG.md)


---

## `proposals/claude/20260928-HYPGEN2-CODEX.md`

# HYPGEN2 카드 (Codex) — 가설 생성부터: d157 을 넘거나 d157 과 다른 계열로 2300+ 를 노릴 후보
발행: Claude 2026-09-27 23:45 KST. 보고 목표 **09-28 09:00 KST**. 판단·연구 작업(상위 모델, high 이상).
## 현재 (사실)
- 활성: **d157 56607884 = 2299.7**(제출 12h), v074 56577440 = 2160.8. bronze 경계 약 2290. 제출 마감 10-01 08:59 KST, 최종 = 마감 후 ~2주 경기 포함 BT 재적합(활성 bot 끼리).
- 두 번째 슬롯(v074 자리)을 쓸 후보가 필요하다. 사람 판단: v074 는 의미 없음, **d157 과 다른 계열 탐색**을 원함(같은 계열은 결과 상관이 높아 max 이득이 작음: 55be5d5f·d157·d053·b020 은 hosted tape 350 에서 결과 100% 동일).
- 지금까지 닫힌 경로(재제안 금지, 근거 파일 참고): ±1 knife-edge(EXP-023/024/026/029/036), layer bypass(EXP-030), H1 gated lead(`reports/codex/20260927-1639-H1.md`), v074 late closure(`…2126-LATE.md`), 관측 기반 front-run(`…2311-ALTMECH.md`: 이미 `_r37_quote_priority` 로 구현), marketshock/12ad317e(no-op).
## 데이터 (읽기 전용)
- hosted replay: `private_artifacts/v074_hosted_20260927/raw/`(350, 계열 라벨 `analysis/v074_hosted_20260927/opponents.csv`), d157 hosted 는 EXP-037 이 `analysis/d157_hosted_20260928/` 에 수집 중(완료되면 사용).
- tape 평가: `experiments/exp033_tapes/`(tapes/, meta.json, games-cloud.jsonl·games-kaggle.jsonl: P,V171,D,d157,d053,b020 × 350).
- 로컬 행렬: EXP-028/032(`experiments/exp028_dpnew`, `exp032_specialist`), daily scan 공개 파일 `analysis/daily_scan/2026092*/extracted/*/main.py`, discussion `docs/discussion/`.
- engine: kaggle-environments 1.32.7 `kaggriculture.py`.
## 과제
1. **가설 생성**: 위 데이터에서 "field 의 어느 상대에게, 왜 지는가 / 누가 이기는가" 를 스스로 분석해 가설을 최대 8개 생성. 최소 2개는 **d157(55be 계열)과 다른 계열**(다른 공개 bot 계열, 다른 생산·판매 구조, 새 조합 등). 예: hosted 에서 d157·v074 를 모두 이기는 상대의 행동 특징(판매 품목 구성·시점·생산 배분)을 replay 로 역추적 → 어떤 공개 파일이 가장 가까운지, 우리가 그 방식을 만들 수 있는지.
2. **증거로 순위화**: 각 가설 — 근거(파일:줄·재집계·trace), 부모/구현 방식, 예상 효과(127 변형·127 exact·55be·기타·LB 2200–2400), d157 과의 예상 결과 상관, 구현·검증 시간, 반증 기준.
3. **상위 1–2개 사전등록 카드 + jobs 파일**: Claude 가 09-28 오전 Kaggle 5 kernel(약 2,400경기/h)로 돌릴 수 있게. panel = hosted tape 350(open-loop) + closed-loop(V074/O127/D/d157 각 50 seed×2, guard 23×5×2) + D3 runtime. 판정 규칙은 결과 전에 고정.
금지: 제출, Kaggle 다운로드, holdout 9000–9599, 기존 파일 수정, 결과 본 뒤 기준 변경. **CPU: Mac 은 EXP-036(5 worker)·EXP-037(2 worker) 사용 중 → 새 게임 1 worker, 최대 40경기.** 쓰기: `experiments/hypgen2_0928/`, 보고서 1개.
## 보고 (`coordination/reports/codex/<ts>-HYPGEN2.md`, 150줄): 첫 줄 최우선 가설+확신도, 가설 표(순위), 상위 카드 경로·jobs sha, 다른 계열 후보가 없으면 그 근거, 다음 행동 2개. 근거 없는 가설은 버린다.


---

## `proposals/claude/20260928-TOP2400-CODEX.md`

# TOP2400 카드 (Codex) — 2400+ 상위 팀이 d157 을 이기는 메커니즘 → d157′ 구현·검증 (가설 생성부터)
발행: Claude 2026-09-28 17:10 KST. 1차 보고 **09-29 06:00 KST**, 최종 **09-29 15:00 KST**. 판단·연구·구현(상위 모델, high 이상). 사람 지시: 필요하면 상위 bot 의 방식을 d157 위에 흉내 내는 것까지 시도.
## 사실
- 활성: d157 56607884 ≈2393 (136경기: LB 2400–2600 상대 11승 25패), v074 ≈2061. 제출 마감 10-01 08:59 KST. FIFO: 다음 제출은 v074 은퇴, 그다음은 d157 은퇴 → d157′ 는 d157 을 모든 panel 에서 넘어야 한다(사람 규칙).
- 데이터: `analysis/top2400_20260928/`(25 submission, 24팀, 750 episode, replay `private_artifacts/top2400_20260928/raw/` — **replay 의 각 좌석 observation 에 private(shed·inventories) 포함** → 실제 체결량 계산 가능), 특징 `experiments/exp041_top2400/feat/*.jsonl`(목표·상대 양쪽: money@144..719, animals/crops@288/576, 요청 SELL/BUY 수량·분기), d157 136경기 특징 `d157feat.jsonl`, tape `experiments/exp041_top2400/tapes/X*.py`(상위 팀 행동; 우리 bot 은 `meta.json` our_seat 로 투입), 팀 분할 `team-split.json`(holdout 5팀 — **선택·튜닝에 쓰지 말 것**).
- Claude 1차 관찰(요청 수량 기준, 체결 아님): 생산 구성·최종 money 는 d157 과 거의 같다(딸기 ~32, 밀 20, 양 ~8, 소 ~7, money719 ~98–100k). 차이는 **판매·구매 주문 방식**: 상위 다수가 WHEAT BUY_PRODUCT/SELL 을 수천 단위 요청(Fritz Cremer 2561 매 게임 ~2.8k/3.0k, ctree 6.7k/8.3k, Hikaru 4.7k/5.0k; d157 330/572), 4분기에 CARROT/FERTILIZER/MILK/WOOL SELL 요청이 d157 의 3–6배. 승률 상위 Shawn404 0.70, Fritz 0.65, Hikaru 0.63, juliencst 0.63.
- EXP-042(진행 중): d157·c26·V074 × 2400+ tape 750 → 기준선.
- 닫힌 경로(재제안 금지): ±1 knife-edge, layer bypass, H1, v074 late closure, ALTMECH front-run, _CA_MARGIN(EXP-039: c26 tape +0.024, U −0.004, fam +0.10 — 슬롯2 후보로 따로 판단 중).
## 과제
1. **체결 기준 행동 분석**: private shed/money 변화로 실제 체결(품목·수량·단가·step)을 복원. 상위 팀 vs d157(같은 경기 25패 우선, 이후 전체)에서 어떤 거래가 수입·상대 억제를 만드는지. WHEAT 대량 BUY/SELL 의 실제 체결·목적(가격 조작? 사료? 순환 차익? 주문 스팸?) 을 엔진 코드(`_process_market`) 근거로 판정.
2. **가설 ≤ 5개**(근거·예상 효과·반증), 최소 1개는 "상위 팀 방식 흉내"(예: 주문 방식·청산 방식 이식).
3. **d157′ 구현**(d157 바이트 뒤 wrapper 우선; 불가하면 명시) → **사전등록**(`experiments/top2400_codex/prereg.json`, 결과 전 고정) → Kaggle jobs 파일(select 팀 tape + holdout 팀 tape + EXP-039 panel: U 136·T 350·family arena·O127·V074) 작성. 실행은 Claude/antigravity 가 Kaggle 로 한다(요청 시 1시간 내 결과 반환). 로컬 smoke 는 1 worker ≤ 60경기.
4. 판정 규칙(고정): select 팀 tape 에서 d157 대비 lower95>0, **holdout 5팀 tape 에서 point>0**, EXP-039 panel 모든 항목 d157 이상(U tape ≥0, T tape ≥0, family ≥0, O127/V074 ≥ −0.02), D3 1-worker max<0.8.
금지: 제출, 다운로드(이미 받은 것만), holdout seed 9000–9599, holdout 팀으로 튜닝, 기존 파일 수정, 결과 본 뒤 기준 변경.
## 보고 (`coordination/reports/codex/<ts>-TOP2400.md`): 1차(06:00) = 분석 표 + 가설 + jobs 경로·sha. 최종(15:00) = 판정. 근거 없는 가설은 버린다.


---

## `proposals/claude/20260929-C26HOSTED-ANTIGRAVITY.md`

# C26HOSTED 실행 카드 (antigravity) — c26·d157 hosted 성적 수집 (판단 없음)
발행: Claude 2026-09-28 20:10 KST. 실행 시각: **09-29 09:00 KST 이후 1회**. 보고 8줄. EXP-037(d157_hosted_20260928) 과 같은 절차.
대상: c26 = 56635330 (releases/exp039-c26/main.py ff230c83…), d157 = 56607884 (releases/exp035-d157/main.py 94a46c11…).
입력 sha(앞 12자, analysis/c26_hosted_20260929/): run_all.sh 2a3a9de59913, step1_2_collect.py d3e8ec9d6ed7, step3_download_replays.py 5e04d7b493a0, step4_5_fingerprint.py 58dd81ec0515
0. cd ~/kaggle/Kaggriculture ; shasum -a 256 analysis/c26_hosted_20260929/*.{py,sh} releases/exp039-c26/main.py releases/exp035-d157/main.py → 위 값과 다르면 STOP(보고만).
1. caffeinate -dimsu nohup bash analysis/c26_hosted_20260929/run_all.sh > analysis/c26_hosted_20260929/run_all.log 2>&1 &
2. 단일 대기: 끝날 때까지 기다린 뒤 tail -3 run_all.log 1회 확인. 폴링 반복 금지.
STOP: 어느 step 이 실패하면 1회 재실행, 또 실패하면 그 step 의 log 마지막 20줄만 보고. 스크립트·대상 ID 수정 금지. 제출 금지.
산출: analysis/c26_hosted_20260929/{episodes_all.json, opponents.csv, summary.json, as_of.txt}
보고: coordination/reports/antigravity/<ts>-C26HOSTED.md — 완료 시각, as_of, sub 별 경기 수, replay missing/corrupt 수. 판정·해석은 Claude.


---

## `proposals/claude/20260929-CALIB-CODEX.md`

# CALIB 카드 (Codex, 상위 모델) — 어떤 로컬 평가가 hosted 순서를 맞히는가
**기준 상태:** 활성 d157 56607884(약 2200, 주력) / c26 56635330(약 1930). 다음 제출은 d157 을 은퇴시킨다. 카드가 BOARD 보다 최신이면 카드를 따른다.
발행: Claude 2026-09-29. 시한 09-30 02:00 KST (중간 보고 09-29 22:00).
## 왜
로컬 도구 세 가지가 모두 c26 > d157 이라고 했다: 현재 상대 집단 tape +0.030(SE .019), 2400+ tape +0.033, family arena closed-loop +0.104. 그런데 hosted 표시 점수는 c26 이 17시간째 1930 부근에서 정체다(d157 은 136경기 만에 2345 도달).
원인이 ① 로컬 평가의 오류인지 ② hosted 레이팅의 수렴 지연·표시 방식인지 모른다. 이걸 모르면 어떤 새 후보도 d157(주력)을 은퇴시킬 근거가 없다.
## 할 일
1. hosted 레이팅 방식 확인: Kaggle 공식 문서(대회 overview/evaluation)에서 표시 점수가 μ 인지 μ−kσ 인지, 새 submission 초기값과 갱신 규칙. 근거 URL.
2. 버전별 대조표: v074, v171, 127ed3e6 exact, DP0924, d157, c26 의 hosted 기록(analysis/*_hosted_*, evidence/HOSTED_LEDGER.md)과 각 로컬 평가(exp033/exp039/exp041/exp051 tape, family arena)의 순위를 나란히 놓고, 어떤 로컬 지표가 hosted 순서를 맞혔는지.
3. c26 판정: analysis/hosted_20260929b/(antigravity 가 곧 수집, 최신 17시간 포함)에서 c26 의 최근 승률과 상대 강도로 "아직 오르는 중"인지 "약 1930 에서 균형"인지 판단. 상대 강도는 팀 LB 가 아니라 가능하면 상대 submission 단위로 추정하고, 불가능하면 그 한계를 적어.
4. 결론: 앞으로 후보가 d157 을 대체해도 된다고 볼 **최소 통과 기준**(어떤 panel 에서 얼마 이상)을 제안. 근거 없으면 "로컬 평가로는 d157 대체 판단 불가"라고 써도 된다.
금지: 제출, 엔진·RNG 수정, seed 9000–9599, 결과 본 뒤 기준 변경. 새 폴더 experiments/calib/ 에만 쓴다.
보고: coordination/reports/codex/<ts>-CALIB.md — 첫 줄 결론, 대조표 1개, 최소 통과 기준 제안, 근거(파일:줄·URL).


---

## `proposals/claude/20260929-COMMUNITY-ANTIGRAVITY.md`

# COMMUNITY0929 수집 카드 (antigravity) — discussion 공백 메우기 + 커뮤니티 노트북 실행 결과 (판단 없음)
발행: Claude 2026-09-29. **사람 승인(09-29): 이 카드 범위의 Kaggle discussion 조회와 kernel source·output 다운로드만 허용.** 제출·dataset 다운로드는 금지.
목적:
- A: discussion 수집이 09-18에서 멈춰 있다. 그 뒤로 올라온 운영진 공지와 평가·규정 변경을 놓치지 않기 위해 수집한다.
- B: 커뮤니티 분석 노트북 3개는 우리 저장본에 소스만 있고 실행 결과가 0줄이다. 실행 결과를 받는다.
- 해석과 판정은 Claude가 한다. 이 카드는 수집만 한다.

## 운영 규칙 (필수)
- 이 카드를 한 번 읽고 바로 실행한다. 아래에 적힌 파일 외에는 저장소를 탐색하지 않는다.
- 단계마다 명령 하나로 실행하고 끝날 때까지 기다린다. 진행 상황을 폴링하거나 중간 메시지를 보내지 않는다.
- 쓰기 허용 위치는 `analysis/community_20260929/`와 보고서 파일 1개뿐이다. `docs/`, `scripts/`, 기존 파일은 수정하지 않는다.
- 스크립트를 고치지 않는다. 오류가 나면 1회만 재실행하고, 또 실패하면 STOP한다.

## 입력 sha256 (앞 12자)
- `analysis/community_20260929/fetch_community.py` = `114a1902f43e`
- `scripts/fetch_kaggle_updates.py` = `2729ae529114` (helper import만 한다)

## 단계
0. `cd ~/kaggle/Kaggriculture; shasum -a 256 analysis/community_20260929/fetch_community.py scripts/fetch_kaggle_updates.py`로 위 값과 대조한다. 다르면 STOP.
1. **A. discussion 수집**
   - 실행: `caffeinate -dimsu python3 analysis/community_20260929/fetch_community.py discussions > analysis/community_20260929/discussions.log 2>&1`
   - 수집 범위: 2026-09-18T00:00Z 이후 활동이 있는 topic. recent 정렬 최대 15쪽에 top 1쪽을 더한다.
   - 출력: `discussion/index.csv`, `discussion/<id>.md`(새 메시지에 [NEW] 표시), `discussion/raw/<id>.json`, `discussion/summary.json`
2. **B. 노트북 source와 실행 결과 다운로드**
   - 실행: `caffeinate -dimsu python3 analysis/community_20260929/fetch_community.py kernels > analysis/community_20260929/kernels.log 2>&1`
   - 대상 3개:
     - `georgymamarin/kaggriculture-what-2600-farms-do-differently`
     - `destbreso/kaggriculture-know-your-noise`
     - `destbreso/everyone-is-playing-the-same-opening`
   - 크기 3GB 초과나 30분 초과 시 스크립트가 스스로 중단하고 STOP을 기록한다.
   - 출력: `kernels/<slug>/{source,output}/`, `kernels/<slug>/outputs_text.txt`, `kernels/manifest.json`(파일별 sha256)
3. **B 대체 수단 (조건부)**
   - 조건: manifest에서 어떤 kernel의 `out_lines`가 0이고 status가 ok일 때만 실행한다. 원인은 output API가 실행된 셀 출력을 주지 않는 경우다.
   - 방법: 브라우저로 해당 kernel 페이지(`https://www.kaggle.com/code/<ref>`)를 연다. 로그인은 필요 없다. 아래 섹션만 전체 화면 스크린샷 png로 저장한다.
     - 2600-farms: 섹션 1, 4, 5, 7, 8, 9, 10, Takeaways
     - know-your-noise: 결론과 효과 크기(유효 표본, 분산 팽창 등)가 나오는 표·차트
     - same-opening: turn 48 관련 표·차트
   - 저장 위치: `kernels/<slug>/screens/NN_<섹션>.png`
   - fork, 실행(Run/Copy & Edit), 댓글, 투표는 하지 않는다.

## 금지
- 제출
- dataset 다운로드: georgymamarin episodes, destbreso benchmark 45k 모두 해당
- kernel push·fork·실행
- 경기 실행, holdout 사용
- 기존 파일 수정
- 수집 내용의 요약·해석 (flag는 스크립트가 붙인 키워드만 옮긴다)

## STOP
- sha 불일치
- 인증 실패
- 같은 단계 2회 실패
- size cap 또는 timeout
- A에서 `summary.json`의 errors가 3개 초과

## 보고
`coordination/reports/antigravity/<ts>-COMMUNITY0929.md`, 15줄 이내로 쓴다.
- 첫 줄: PASS 또는 STOP과 한 문장 이유
- A: candidates, saved, flagged 수, errors 수. flags가 비어 있지 않은 topic을 전부 한 줄씩 적는다(topic_id, first_new, author, title, flags). 10개가 넘으면 first_new 최신순 10개만 적고 나머지는 개수만 적는다.
- B: kernel별 status, 파일 수, 총 bytes, out_lines, images, 스크린샷 수
- 소요 시간, 다음 행동: "Claude 판독 대기"


---

## `proposals/claude/20260929-EXP045A-ANTIGRAVITY.SUPERSEDED.md`

# EXP-045 Stage A 실행 카드 (antigravity) — 판단 없음
발행: Claude 2026-09-28 23:00 KST. **시작 조건: Codex 보고 coordination/reports/codex/*-EXP045v2.md 가 존재할 때.** 보고 8줄. EXP-043 과 같은 절차.
0. cd ~/kaggle/Kaggriculture; experiments/exp045_sale/manifest.json 의 sha 와 variants/*.py 를 shasum -a 256 으로 대조. 하나라도 다르면 STOP(보고만).
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp045_sale/jobs-A-kaggle.json exp045a 5
3. kaggle datasets create -p experiments/kaggle_runs/exp045a/dataset → ready → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp045a/kernel$k (실패 시 1회 재시도, 또 실패면 그 몫을 Mac 에서)
4. 동시에 Mac: caffeinate -dimsu nohup env EXP024_OUT=experiments/exp045_sale/games-A-mac.jsonl python experiments/exp024_round2/run.py experiments/exp045_sale/jobs-A-mac.json > experiments/exp045_sale/runA-mac.log 2>&1 &
5. 단일 대기. 끝나면 k=0..4 output → experiments/kaggle_runs/exp045a/out/k$k, cat .../games-*.jsonl > experiments/exp045_sale/games-A-kaggle.jsonl; wc -l experiments/exp045_sale/games-A-*.jsonl (합계 = jobs 수 기대, 11×595=6545)
금지: 스크립트·jobs 수정, 제출, 판정. 보고: coordination/reports/antigravity/<ts>-EXP045A.md — 완료 시각·행 수·실패 커널.


---

## `proposals/claude/20260929-EXP047-CODEX.md`

# EXP-047 카드 (Codex, 상위 모델) — known-opponent 판매 예측 → d157 front-run hook 연결
**기준 상태:** 활성 d157 56607884 / c26 56635330 (BOARD 09-28 23:30 KST). 카드가 BOARD 보다 최신이면 카드를 따르고, 어긋남은 보고 첫 줄에 적은 뒤 계속한다.
발행: Claude 2026-09-29 00:20 KST (사람 승인). 시한: 구현·smoke·jobs-A 09-29 12:00 KST. 근거: analysis/exp046_predict/FINDINGS.md.
핵심: 상위 팀 다수의 WOOL/MILK/STRAWBERRY 판매는 공개 55be 로 예측된다(상한 step recall .90, 7팀 ≥.95). d157 에는 이미 opponent_plan 을 받아 "상대가 다음 step 에 팔 품목을 지금 먼저 판다"는 _front_run hook(main.py:655–, 487)이 있지만 hosted 에서는 plan 이 없어 꺼져 있다.
## 단계
0. 조사(≤1h): _front_run 입력 형식과 발동 조건, _OR2 의 상대 shed 추정값 위치를 파일:줄로 적는다.
1. 예측기: d157 안에 공개 55be 를 상대 좌석의 shadow agent 로 한 번 더 인스턴스화한다. 상대 관점 관측(player 교체, 공개 farms/market/town, private.shed = _OR2 추정, seeds·inventories 는 빈 값)을 넣어 이번 step 상대 SELL 을 얻는다. 다음 step 예측이 필요하면 가장 단순한 근사를 쓰고 그 근사를 명시한다.
   측정: select 20판에서 추정 상태 예측 정확도(step 사건 recall·precision) 대 FINDINGS 상한. 1 worker max step < 0.8s(D3 기준). 넘으면 shadow 를 SELL 경로만 남기도록 줄인다.
2. 후보 1개: 예측을 opponent_plan 으로 _front_run 에 연결(상수는 hook 기본값, 튜닝 금지). 필요하면 대안 1개(같은 step 동시 판매 억제)만 추가해 최대 2개.
3. experiments/exp047_oppmodel/: variants, manifest(sha·파일:줄), smoke 4판, jobs-A(select 595, prep42 형식). 실행은 antigravity.
## 판정 (Claude 사전등록 analysis/exp045/PREREG.md 와 같은 규칙 적용, 추가 1개)
- 추가 B5: closed-loop family arena 중 **vs D(55be exact)** paired 차 ≥ 0. open-loop tape 는 상대 반응이 없어 front-run 을 과대평가할 수 있기 때문이다.
금지: 제출, 엔진·RNG 수정, holdout 팀·seed 9000–9599, 결과 본 뒤 상수 변경.
보고: coordination/reports/codex/<ts>-EXP047.md — 첫 줄 판정, 예측 정확도(추정 대 상한), runtime, 변형 sha·파일:줄.


---

## `proposals/claude/20260929-EXP048A-ANTIGRAVITY.md`

# EXP-048 Stage A 실행 카드 (antigravity) — EXP-045 11 변형 + EXP-047 hook, 판단 없음
**기준 상태:** 활성 d157 56607884 / c26 56635330 (BOARD 09-28 23:30 KST). 카드가 BOARD 보다 최신이면 카드를 따르고, 어긋남은 보고 첫 줄에 적은 뒤 계속한다.
발행: Claude 2026-09-29 00:50 KST. EXP-043 과 같은 절차. 보고 8줄. (EXP045A 카드는 SUPERSEDED)
입력 sha(앞 12자): experiments/exp048_stageA/jobs-kaggle.json f92c7d285656 (4,284 jobs), jobs-mac.json 5c3c858d581b (2,856 jobs), make_kaggle2.py 1cff6a2d9dfe. 변형 sha 는 experiments/exp045_sale/manifest.json(a2f0c47d…), experiments/exp047_oppmodel/manifest.json 과 대조.
0. cd ~/kaggle/Kaggriculture; 위 sha 와 두 manifest 의 변형 sha 를 shasum -a 256 으로 대조. 하나라도 다르면 STOP(보고만).
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp048_stageA/jobs-kaggle.json exp048a 5
3. kaggle datasets create -p experiments/kaggle_runs/exp048a/dataset → ready → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp048a/kernel$k (실패 시 1회 재시도, 또 실패면 그 몫을 Mac 에서)
4. 동시에 Mac: caffeinate -dimsu nohup env EXP024_OUT=experiments/exp048_stageA/games-mac.jsonl python experiments/exp024_round2/run.py experiments/exp048_stageA/jobs-mac.json > experiments/exp048_stageA/run-mac.log 2>&1 &
5. 단일 대기. 끝나면 k=0..4 output → experiments/kaggle_runs/exp048a/out/k$k, cat .../games-*.jsonl > experiments/exp048_stageA/games-kaggle.jsonl; wc -l experiments/exp048_stageA/games-*.jsonl (합계 7,140 기대)
금지: 스크립트·jobs 수정, 제출, 판정. 보고: coordination/reports/antigravity/<ts>-EXP048A.md — 완료 시각, 행 수, 실패 커널.


---

## `proposals/claude/20260929-EXP048B-ANTIGRAVITY.md`

# EXP-048 Stage B 실행 카드 (antigravity) — hook·K3 확인 + fresh tape 기준선 (판단 없음)
**기준 상태:** 활성 d157 56607884 / c26 56635330. 카드가 BOARD 보다 최신이면 카드를 따르고, 어긋남은 보고 첫 줄에 적은 뒤 계속한다.
발행: Claude 2026-09-29. EXP048A 와 같은 절차. 보고 8줄. 3,164경기 예상.
입력 sha(앞 12자): experiments/exp048_stageB/jobs-kaggle.json 4e5bfa66afc5 (1,899), jobs-mac.json ff91227a00c0 (1,265), make_kaggle2.py 1cff6a2d9dfe, judge48B.py 7bde61ea58b0(실행하지 말 것, 대조만).
0. cd ~/kaggle/Kaggriculture; 위 sha 대조. 다르면 STOP.
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp048_stageB/jobs-kaggle.json exp048b 5
3. kaggle datasets create -p experiments/kaggle_runs/exp048b/dataset → ready → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp048b/kernel$k (실패 시 1회 재시도, 또 실패면 그 몫을 Mac 에서)
4. 동시에 Mac: caffeinate -dimsu nohup env EXP024_OUT=experiments/exp048_stageB/games-mac.jsonl python experiments/exp024_round2/run.py experiments/exp048_stageB/jobs-mac.json > experiments/exp048_stageB/run-mac.log 2>&1 &
5. 단일 대기. 끝나면 k=0..4 output → experiments/kaggle_runs/exp048b/out/k$k, cat .../games-*.jsonl > experiments/exp048_stageB/games-kaggle.jsonl; wc -l experiments/exp048_stageB/games-*.jsonl (합계 3,164 기대)
금지: 스크립트·jobs 수정, 제출, 판정. 보고: coordination/reports/antigravity/<ts>-EXP048B.md — 완료 시각, 행 수, 실패 커널.


---

## `proposals/claude/20260929-EXP056-ANTIGRAVITY.md`

# EXP-056 실행 카드 (antigravity) — 공개 bot 7개 × 현재 상대 집단 269 tape (판단 없음)
**기준 상태:** 활성 d157 56607884 / c26 56635330. 카드가 BOARD 보다 최신이면 카드를 따른다.
발행: Claude 2026-09-29. EXP-048A 와 같은 절차. 1,883경기. 보고 8줄.
입력 sha(앞 12자): experiments/exp056_pubscreen/jobs-kaggle.json cd4c338bc51e (1,131), jobs-mac.json 719d46b221e5 (752), make_kaggle2.py 1cff6a2d9dfe.
0. cd ~/kaggle/Kaggriculture; sha 대조. 다르면 STOP.
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp056_pubscreen/jobs-kaggle.json exp056 5
3. kaggle datasets create -p experiments/kaggle_runs/exp056/dataset → ready → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp056/kernel$k (실패 시 1회 재시도, 또 실패면 그 몫을 Mac 에서)
4. 동시에 Mac: caffeinate -dimsu nohup env EXP024_OUT=experiments/exp056_pubscreen/games-mac.jsonl python experiments/exp024_round2/run.py experiments/exp056_pubscreen/jobs-mac.json > experiments/exp056_pubscreen/run-mac.log 2>&1 &
5. 단일 대기 → k=0..4 output 합쳐 experiments/exp056_pubscreen/games-kaggle.jsonl; wc -l experiments/exp056_pubscreen/games-*.jsonl (합계 1,883)
금지: 스크립트·jobs 수정, 제출, 판정. SURVEY300 다운로드가 진행 중이면 그대로 두고 병행한다(Kaggle API 429 가 나면 datasets/kernels 명령만 5분 간격 3회까지 재시도).
보고: coordination/reports/antigravity/<ts>-EXP056.md — 완료 시각, 행 수, 실패 커널.


---

## `proposals/claude/20260929-EXP058S-ANTIGRAVITY.md`

# EXP-058 Stage S 실행 카드 (antigravity) — route 강제 5 arm × 현재 상대 집단 269 tape (판단 없음)
**기준 상태:** 활성 d157 56607884 / c26 56635330. 카드가 BOARD 보다 최신이면 카드를 따른다.
발행: Claude 2026-09-29 15:00 KST. EXP-056 과 같은 절차. 1,345경기. 보고 8줄. **사람 승인 09-29 — 즉시 시작.**
입력 sha(앞 12자): experiments/exp058_route/PREREG.md 75a8125e5366, jobs-kaggle.json d3c885eb36d4 (807), jobs-mac.json 13bd775c1ead (538), make_kaggle2.py 1cff6a2d9dfe.
0. cd ~/kaggle/Kaggriculture; sha 대조. 다르면 STOP.
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp058_route/jobs-kaggle.json exp058 5
3. kaggle datasets create -p experiments/kaggle_runs/exp058/dataset → ready → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp058/kernel$k (실패 시 1회 재시도, 또 실패면 그 몫을 Mac 에서)
4. 동시에 Mac: caffeinate -dimsu nohup env EXP024_OUT=experiments/exp058_route/games-mac.jsonl python experiments/exp024_round2/run.py experiments/exp058_route/jobs-mac.json > experiments/exp058_route/run-mac.log 2>&1 &
5. 단일 대기 → k=0..4 output 합쳐 experiments/exp058_route/games-kaggle.jsonl; wc -l experiments/exp058_route/games-*.jsonl (합계 1,345)
금지: 스크립트·jobs·variants 수정, 제출, 판정.
보고: coordination/reports/antigravity/<ts>-EXP058S.md — 완료 시각, 행 수, 실패 커널.


---

## `proposals/claude/20260929-FIRSTPRINCIPLES-CODEX.md`

# FIRSTPRINCIPLES 카드 (Codex, 상위 모델) — 비공개 55be 변형 집단을 이기고 hosted 2300+ 로 가는 방법을 처음부터 찾는다
**기준 상태:** 활성 d157 56607884 (~2216, 하락 중) / c26 56635330 (~1890, 정체). 다음 제출은 FIFO 로 d157 을 은퇴시킨다. 카드가 BOARD 보다 최신이면 카드를 따른다.
발행: Claude 2026-09-29. 마감: 후보 release 09-30 15:00 KST, 사람 제출 시한 09-30 21:00 KST. 중간 보고 09-29 22:00 KST.

## 목표
2200–2400 구간을 채운 **비공개 55be/Step1009 변형 집단**을 이겨 hosted 2300 이상에 도달할 bot 1개. "지금 bot 그대로 제출"은 답이 아니다.

## 알려진 사실 (출발점일 뿐, 틀렸다고 판단되면 근거와 함께 뒤집어도 된다)
- 엔진: .venv/.../kaggle_environments/envs/kaggriculture/kaggriculture.py (sha bc8a5487…). 공유 시장, 슬롯 단위 lockstep 체결, 보상 = 최종 money. seed 는 agent 에게 숨겨진다.
- d157 = 공개 55be5d5f(Step1009, 약 10k 줄, 판매 모듈 수십 층) + 상수 1개. 엔진 unit 규칙을 내장하고 있다(main.py:1020 부근 _UNIT_NS).
- 누구에게 지는가(analysis/exp050_divergence/, coordination/reports/claude/20260929-EXP050-051-LOSS-ANALYSIS.md): 공개 55be 와 같은 상대에게 18승 0패 7무. 비공개 변형에게 20승 44패, 격차는 수십 코인. 변형은 55be 와 경기당 약 15 step 만 다르고 후반부에 몰려 있으며 종류가 제각각이다.
- 승패 분산은 WHEAT 가 아니라 WOOL/MILK/STRAWBERRY 판매 단가에서 나온다(analysis/exp044_margin/FINDINGS.md).
- 현재 상대 집단 tape: experiments/exp051_curpop/ (d157·c26 실전 상대 269경기, 자기 경기 재현 187/187, 82/82). 곧 analysis/hosted_20260929pm/ 으로 갱신된다(antigravity).
- 풀리지 않은 모순: c26 은 현재 상대 집단 tape 에서 d157 보다 +0.03(2200–2400 +0.056)인데 hosted 는 1900 아래에서 정체라고 사람이 판단했다. 이 차이의 원인(레이팅 수렴, 매칭, tape 가 못 보는 반응, 기타)을 설명하는 것도 과제의 일부다.
- 이미 실패한 방향(새 근거 없이 반복 금지, 근거가 있으면 재개 가능): 상수 ±1 탐색, 공개 bot 교체, WHEAT 순환 흉내, WHEAT 순서 교환, 판매 모듈 끄기 8종, 판매 보류 규칙, 턴당 판매 상한, shadow 55be 선매도 hook(EXP-045/047/048).

## 자유도
- d157 을 조금 고치는 것에서 시작하지 않아도 된다. 새 구조, 탐색·시뮬레이션 기반 계획(내장 엔진 규칙으로 몇 step 앞을 굴리기), 상대 모델, 상대 식별 후 정책 전환, 생산 계획 재설계, 시장 선점·방해, 두 슬롯 운용 전략 등 무엇이든 된다. 여기 적힌 예시에 묶이지 마라.
- 먼저 서로 **구조적으로 다른 접근 6개 이상**을 적고, 각각 기대 이득·실패 위험·소요 시간을 근거(파일:줄 또는 데이터)와 함께 1–2줄로 평가한다. 그다음 최대 2개를 골라 만든다. 고른 이유와 버린 이유를 남긴다.
- 막히면 가정을 의심하고 다른 접근으로 바꾼다. 같은 실패를 파라미터만 바꿔 반복하지 않는다.
- 필요하면 hosted 원본(private_artifacts/*/raw), 공개 notebook 스캔(analysis/daily_scan/), 과거 보고서(coordination/reports/)를 자유롭게 읽는다.

## 평가 (결과 보기 전에 스스로 고정하고 sha 로 남긴다)
- 주 panel: 현재 상대 집단 tape(exp051 + hosted_20260929pm 갱신분). 개발에 쓰지 않을 **시간 분리 holdout**(가장 최근 경기 일부)을 먼저 떼어 둔다.
- 보조: 2400+ tape(experiments/exp041_top2400, exp049_fresh), closed-loop 55be 계열 대결. open-loop tape 가 상대 반응을 못 보는 한계를 어떻게 보완할지 스스로 정한다.
- 통과 기준은 네가 정하되, "c26 과 d157 중 나은 쪽보다 현재 상대 집단에서 확실히 높다"를 포함한다.
- 실행은 Mac 에서 직접 해도 되고(nohup, 5 worker), 큰 실행은 Kaggle private notebook 5개(experiments/kaggle_pilot/make_kaggle2.py)를 써도 된다.

## 제약
제출 금지(사람만). 엔진·RNG 수정 금지. seed 9000–9599 금지. 결과를 본 뒤 기준 변경 금지(바꾸면 새 실험으로 기록). 릴리스 = USTAR tar(main.py 1개, mtime 0) + NOTICE + SHA256SUMS, D3 gate(experiments/d3_gate_v2/measure_gate_v2_claude.py, 1 worker, 새 프로세스 15경기, max step < 0.8s). 새 폴더 experiments/fp_<이름>/ 에만 쓴다.

## 보고 (토큰 절약)
coordination/reports/codex/<ts>-FIRSTPRINCIPLES.md
- 중간(09-29 22:00): 접근 6개 이상 평가표, 선택 2개와 이유, 고정한 평가 기준 sha, 초기 결과.
- 최종(09-30 15:00): 첫 줄 판정, 후보 sha·release 경로, panel 별 결과(d157·c26 대비), holdout, D3, 남은 위험 2개.


---

## `proposals/claude/20260929-FRESH2400-ANTIGRAVITY.md`

# FRESH2400 수집 카드 (antigravity) — 2400+ 25개 submission 의 09-28 05:27 UTC 이후 새 경기 (판단 없음)
**기준 상태:** 활성 d157 56607884 / c26 56635330 (BOARD 09-28 23:30 KST). 카드가 BOARD 보다 최신이면 카드를 따르고, 어긋남은 보고 첫 줄에 적은 뒤 계속한다.
발행: Claude 2026-09-29. 목적: Stage B 판정용 새 holdout(선택에 쓰지 않은 새 경기). 다운로드 범위는 이 카드로 승인된 것만(사람 승인 09-28: 상위 팀 경기 다운로드).
입력: analysis/top2400_fresh_20260929/step1_2_collect.py, step3_download_replays.py (기존 top2400_20260928 복사본. 바뀐 것은 경로와 "endTime > 2026-09-28T05:27:08Z" 조건 1개).
0. cd ~/kaggle/Kaggriculture; diff analysis/top2400_20260928/step1_2_collect.py analysis/top2400_fresh_20260929/step1_2_collect.py 가 경로 1줄 + 조건 2줄만 다른지 확인. 다르면 STOP.
1. caffeinate -dimsu python3 analysis/top2400_fresh_20260929/step1_2_collect.py > analysis/top2400_fresh_20260929/step1_2.log 2>&1
2. caffeinate -dimsu python3 analysis/top2400_fresh_20260929/step3_download_replays.py > analysis/top2400_fresh_20260929/step3.log 2>&1
STOP: 실패 시 1회 재실행, 또 실패하면 log 마지막 20줄만 보고. 스크립트 수정 금지. EXP048A 실행과 동시에 해도 된다(Kaggle API 다운로드만 사용, 커널 안 씀).
보고: coordination/reports/antigravity/<ts>-FRESH2400.md — as_of, submission 별 경기 수, 다운로드 성공·실패 수. tape 변환·판정은 Claude.


---

## `proposals/claude/20260929-FRITZALL-ANTIGRAVITY.md`

# FRITZALL 수집 카드 (antigravity) — Fritz Cremer 전 경기 목록 + replay (판단 없음)
발행: Claude 2026-09-29. 사람 요청: Fritz 의 모든 경기 기록을 받은 뒤 분석 시작. 조회와 replay 다운로드만 허용.
대상 제출(teamId 16925604): 56613024(09-27), 56619080(09-28), 56647721(09-29 신규).

## 운영 규칙
- 이 카드를 한 번 읽고 바로 실행한다. 아래 파일 외에는 저장소를 탐색하지 않는다.
- 단계마다 명령 하나로 실행하고 끝날 때까지 기다린다. 폴링·중간 메시지 없음.
- 쓰기 허용: `analysis/fritz_all_20260929/`, `private_artifacts/fritz_all_20260929/raw/`, 보고서 1개.
- 스크립트를 고치지 않는다. 오류로 멈추면 같은 명령을 1회만 재실행(받은 replay 는 건너뜀). 또 실패하면 STOP.

## 입력 sha256
- `analysis/fritz_all_20260929/collect_fritz.py` = `a50e82ed888f`

## 단계
0. `cd ~/kaggle/Kaggriculture; shasum -a 256 analysis/fritz_all_20260929/collect_fritz.py` → 앞 12자 대조. 다르면 STOP. 이전 수집 카드와 같은 venv 사용.
1. `caffeinate -dimsu python3 analysis/fritz_all_20260929/collect_fritz.py list > analysis/fritz_all_20260929/list.log 2>&1`
2. `caffeinate -dimsu python3 analysis/fritz_all_20260929/collect_fritz.py download > analysis/fritz_all_20260929/download.log 2>&1`

## 금지
제출, kernel 실행, 경기 실행, holdout 사용, 기존 파일·스크립트 수정, 결과 해석.

## STOP
sha 불일치 / 인증 실패 / 같은 단계 2회 실패 / download fail 이 전체의 5% 초과.

## 보고
`coordination/reports/antigravity/<ts>-FRITZALL.md`, 10줄 이내.
- 첫 줄: PASS 또는 STOP + 한 문장 이유
- `summary.json` 의 제출별 listed/kept, total, fritz_lb, other_fritz_subs_seen
- download ok/fail, verify missing/mismatch, 소요 시간
- 다음 행동: "Claude 판독 대기"


---

## `proposals/claude/20260929-FRITZALL2-ANTIGRAVITY.md`

# FRITZALL2 (antigravity) — 429 이후 느린 재다운로드 (판단 없음)
발행: Claude 2026-09-29 19:00 KST. FRITZALL STOP(429) 후속. 이미 받은 목록(episodes_all.json)을 그대로 쓴다.
## 입력 sha256
- `analysis/fritz_all_20260929/collect_fritz.py` = `e183d7817152`
## 단계
0. `cd ~/kaggle/Kaggriculture; shasum -a 256 analysis/fritz_all_20260929/collect_fritz.py` → 앞 12자 대조. 다르면 STOP.
1. `caffeinate -dimsu python3 analysis/fritz_all_20260929/collect_fritz.py download2 > analysis/fritz_all_20260929/download2.log 2>&1`
   - 다른 폴더에 이미 있는 replay 는 복사하고, 나머지는 1개씩 쉬면서 받는다(약 1–1.5시간 예상). 끝날 때까지 기다린다.
## 규칙
- 폴링·중간 보고 없음. 스크립트 수정 금지. 실패해도 재실행하지 않는다(스크립트가 이미 재시도한다).
- 쓰기 허용: `analysis/fritz_all_20260929/`, `private_artifacts/fritz_all_20260929/raw/`, 보고서 1개.
## 보고
`coordination/reports/antigravity/<ts>-FRITZALL2.md`, 6줄 이내: PASS/STOP, copied from cache, ok/fail, verify missing/mismatch, 소요 시간, "Claude 판독 대기".


---

## `proposals/claude/20260929-HOSTED0930-ANTIGRAVITY.md`

# HOSTED0930 수집 카드 (antigravity) — d157·c26 hosted 경기 최신분 (판단 없음)
발행: Claude 2026-09-29 21:00 KST. 목적: SLOT2 holdout(HF) 확대. hosted_20260929b 파이프라인을 폴더명만 바꿔 복사했다.
대상: d157 56607884, c26 56635330 (각 cap 400, as_of = 실행 시각).

## 입력 sha256 (앞 12자)
- `analysis/hosted_20260930/step0_copy_cached.py` = `a98658efa2c1`
- `analysis/hosted_20260930/step1_2_collect.py` = `ce51cd461673`
- `analysis/hosted_20260930/step3_download_replays.py` = `5a79e0d2eb10` (1 worker, 요청 사이 2–3초: 429 대응)
- `analysis/hosted_20260930/step4_5_fingerprint.py` = `3e5552cfe6eb`

## 단계 (각각 한 명령, 끝날 때까지 대기)
0. `cd ~/kaggle/Kaggriculture; shasum -a 256 analysis/hosted_20260930/*.py` → 대조. 다르면 STOP.
1. `caffeinate -dimsu python3 analysis/hosted_20260930/step1_2_collect.py > analysis/hosted_20260930/step1_2.log 2>&1`
2. `python3 analysis/hosted_20260930/step0_copy_cached.py > analysis/hosted_20260930/step0.log 2>&1`
3. `caffeinate -dimsu python3 analysis/hosted_20260930/step3_download_replays.py > analysis/hosted_20260930/step3.log 2>&1`
4. `python3 analysis/hosted_20260930/step4_5_fingerprint.py > analysis/hosted_20260930/step4_5.log 2>&1`

## 규칙
- 폴링·중간 보고 없음. 스크립트 수정 금지. 단계가 오류로 끝나면 같은 명령 1회만 재실행, 또 실패하면 STOP.
- 쓰기 허용: `analysis/hosted_20260930/`, `private_artifacts/hosted_20260930/raw/`, 보고서 1개.
- 금지: 제출, kernel 실행, 경기 실행, 기존 파일 수정, 결과 해석.

## 보고
`coordination/reports/antigravity/<ts>-HOSTED0930.md`, 8줄 이내: PASS/STOP+이유, as_of, 제출별 episode 수, step0 copied/to fetch, 다운로드 실패 수, opponents.csv 행 수, 소요 시간, "Claude 판독 대기".


---

## `proposals/claude/20260929-HOSTED2-ANTIGRAVITY.md`

# HOSTED2 수집 카드 (antigravity) — d157·c26 최신 실전 전적 (판단 없음)
**기준 상태:** 활성 d157 56607884 / c26 56635330. 카드가 BOARD 보다 최신이면 카드를 따르고, 어긋남은 보고 첫 줄에 적은 뒤 계속한다.
발행: Claude 2026-09-29. C26HOSTED 와 같은 파이프라인을 새 폴더 analysis/hosted_20260929b/ 에서 실행한다(이전 결과를 덮어쓰지 않기 위해 경로만 바꾼 복사본).
입력 sha(앞 12자, step1_2 / step3 / step4_5 / run_all 순): dd5784d82daa e7b017538f50 e62e30b5d397 2030865aec63 
0. cd ~/kaggle/Kaggriculture; shasum -a 256 analysis/hosted_20260929b/*.{py,sh} 로 위 값 대조. 다르면 STOP.
1. caffeinate -dimsu nohup bash analysis/hosted_20260929b/run_all.sh > analysis/hosted_20260929b/run_all.log 2>&1 &
2. 단일 대기 후 tail -3 run_all.log 1회 확인.
3. 사람에게 받은 현재 점수를 그대로 기록: echo "<시각> d157=<점수> c26=<점수>" >> analysis/hosted_20260929b/lb_scores.txt (모르면 N/A)
STOP: step 실패 시 1회 재실행, 또 실패하면 log 마지막 20줄만 보고. 스크립트·대상 ID 수정 금지. 제출 금지.
보고: coordination/reports/antigravity/<ts>-HOSTED2.md — 8줄: 완료 시각, as_of, sub 별 경기 수·W/D/L, missing/corrupt 수. 판정·해석은 Claude/Codex.


---

## `proposals/claude/20260929-HOSTEDPM-ANTIGRAVITY.md`

# HOSTEDPM 수집 카드 (antigravity) — d157·c26 최신 실전 전적 (판단 없음)
**기준 상태:** 활성 d157 56607884 / c26 56635330. 카드가 BOARD 보다 최신이면 카드를 따르고, 어긋남은 보고 첫 줄에 적은 뒤 계속한다.
발행: Claude 2026-09-29. C26HOSTED 와 같은 파이프라인을 새 폴더 analysis/hosted_20260929pm/ 에서 실행한다(이전 결과를 덮어쓰지 않기 위해 경로만 바꾼 복사본).
입력 sha(앞 12자, step1_2 / step3 / step4_5 / run_all 순): 8bf8f952413d 4b762a5d47a1 423c5793d77d 09db289b877b 
0. cd ~/kaggle/Kaggriculture; shasum -a 256 analysis/hosted_20260929pm/*.{py,sh} 로 위 값 대조. 다르면 STOP.
1. caffeinate -dimsu nohup bash analysis/hosted_20260929pm/run_all.sh > analysis/hosted_20260929pm/run_all.log 2>&1 &
2. 단일 대기 후 tail -3 run_all.log 1회 확인.
3. 사람에게 받은 현재 점수를 그대로 기록: echo "<시각> d157=<점수> c26=<점수>" >> analysis/hosted_20260929pm/lb_scores.txt (모르면 N/A)
STOP: step 실패 시 1회 재실행, 또 실패하면 log 마지막 20줄만 보고. 스크립트·대상 ID 수정 금지. 제출 금지.
보고: coordination/reports/antigravity/<ts>-HOSTEDPM.md — 8줄: 완료 시각, as_of, sub 별 경기 수·W/D/L, missing/corrupt 수. 판정·해석은 Claude/Codex.


---

## `proposals/claude/20260929-RL-COMMUNITY-ANTIGRAVITY.md`

# RL0929 수집 카드 (antigravity) — discussion·code의 강화학습 관련 글 전수 + 댓글 (판단 없음)
발행: Claude 2026-09-29. **사람 요청(09-29): 대회 discussion과 code에서 RL 관련 글을 댓글까지 모두 수집.** 조회와 kernel source 다운로드만 허용.
목적: RL(PPO·DQN·self-play·AlphaZero·BC 등)을 시도한 참가자들의 글·노트북·댓글을 한 곳에 모은다. 해석은 Claude가 한다.

## 운영 규칙 (필수)
- 이 카드를 한 번 읽고 바로 실행한다. 아래 파일 외에는 저장소를 탐색하지 않는다.
- 단계마다 명령 하나로 실행하고 끝날 때까지 기다린다. 폴링하거나 중간 메시지를 보내지 않는다.
- 쓰기 허용 위치: `analysis/rl_community_20260929/`와 보고서 파일 1개. `docs/`, `scripts/`, 기존 파일은 수정하지 않는다.
- 스크립트를 고치지 않는다. 오류로 멈추면 **같은 명령을 1회만 재실행**한다(캐시가 있어 받은 것은 다시 받지 않는다). 또 실패하면 STOP.

## 입력 sha256 (앞 12자)
- `analysis/rl_community_20260929/fetch_rl_community.py` = `e4c191b9ecf5`

## 단계
0. `cd ~/kaggle/Kaggriculture; shasum -a 256 analysis/rl_community_20260929/fetch_rl_community.py` → 위 값과 대조. 다르면 STOP.
   - 이전 카드(COMMUNITY0929)와 같은 venv를 쓴다. 다른 venv면 `export KAGGLE_VENV=<site-packages 경로>`를 앞에 붙인다.
1. **discussion 전수 → RL 필터**
   - `caffeinate -dimsu python3 analysis/rl_community_20260929/fetch_rl_community.py discussions > analysis/rl_community_20260929/discussions.log 2>&1`
   - 범위: 대회 전 topic(new 정렬 전 페이지 + top/hot/active 5쪽 보강), topic마다 메시지·답글 전부.
   - 출력: `discussion/index.csv`, `discussion/<id>.md`(답글 들여쓰기), `discussion/cache/<id>.json`(전 topic 원본), `discussion/summary.json`
2. **code 전수 → RL 필터 + 노트북 댓글**
   - `caffeinate -dimsu python3 analysis/rl_community_20260929/fetch_rl_community.py code > analysis/rl_community_20260929/code.log 2>&1`
   - 범위: 대회 노트북 전부(dateCreated·voteCount 정렬 전 페이지 + RL 검색어 11개 보강). 노트북마다 source pull, 댓글 스레드 전부.
   - 출력: `code/index.csv`, `code/<owner>__<slug>.md`(markdown 셀 + 댓글), `code/cache/<owner>__<slug>/`(source, comments.json), `code/summary.json`
   - 노트북 실행 결과(output)는 받지 않는다.
3. **합본**
   - `python3 analysis/rl_community_20260929/fetch_rl_community.py digest`
   - 출력: `ALL_RL.md` (tier A/B 본문 전체, tier C는 목록만)

## tier 의미 (스크립트가 자동으로 붙임)
- discussion: `A_core_in_post`(제목·본문에 RL 키워드) / `B_core_in_comments`(댓글에만) / `C_adjacent_only`(BC·MCTS·진화 등 인접 기법만)
- code: `A_core_in_title_or_markdown` / `B_core_in_code`(코드에 RL 키워드 2종 이상 또는 3회 이상) / `B_core_in_comments` / `C_adjacent_or_weak`

## 금지
- 제출, kernel push·fork·실행, 투표·댓글 작성
- dataset 다운로드, kernel output 다운로드
- 경기 실행, holdout 사용
- 기존 파일 수정, 스크립트 수정
- 수집 내용의 요약·해석

## STOP
- sha 불일치 / 인증 실패 / 같은 단계 2회 실패
- `summary.json`의 errors가 단계별 10개 초과

## 보고
`coordination/reports/antigravity/<ts>-RL0929.md`, 15줄 이내.
- 첫 줄: PASS 또는 STOP과 한 문장 이유
- discussion: topics_listed, rl_saved, by_tier, errors 수
- code: kernels_listed, rl_saved, by_tier, comments_total, errors 수
- tier A 항목을 votes 순으로 최대 10개(한 줄씩: kind, id, votes, title)
- `ALL_RL.md` 크기(bytes), 소요 시간, 다음 행동: "Claude 판독 대기"


---

## `proposals/claude/20260929-SURVEY300-ANTIGRAVITY.md`

# SURVEY300 수집 카드 (antigravity) — 상위 300위 + 비교군 경기 전수 수집 (판단 없음)
**기준 상태:** 활성 d157 56607884 / c26 56635330. 카드가 BOARD 보다 최신이면 카드를 따르고, 어긋남은 보고 첫 줄에 적은 뒤 계속한다.
발행: Claude 2026-09-29. 대상: 09-28 순위표 상위 300위 중 submission id 를 아는 235팀 + 600–1300위 비교군 120팀, 팀당 최근 8경기(최대 2,840경기). 다운로드는 이 카드 범위로 승인(사람 09-29).
입력 sha(앞 12자, step1_2 / step3 / targets 순): 3c27acefbb17 b6bfaf446c17 da2568a54aae 
0. cd ~/kaggle/Kaggriculture; 위 sha 대조. 다르면 STOP.
1. caffeinate -dimsu python3 analysis/survey300_20260929/step1_2_collect.py > analysis/survey300_20260929/step1_2.log 2>&1
2. caffeinate -dimsu python3 analysis/survey300_20260929/step3_download_replays.py > analysis/survey300_20260929/step3.log 2>&1
- step3 의 "seat_team_mismatch ... expected Sian" 경고는 재사용 스크립트의 알려진 결함이라 무시한다(reward 불일치만 문제).
- 은퇴한 submission 이라 경기가 0개인 팀이 있어도 정상이다. 그대로 진행한다.
STOP: step 실패 시 1회 재실행, 또 실패하면 log 마지막 20줄만 보고. 스크립트 수정 금지. EXP·HOSTEDPM 과 동시에 해도 된다(API 다운로드만).
보고: coordination/reports/antigravity/<ts>-SURVEY300.md — 8줄: 완료 시각, 수집 경기 수(top300/비교군), 다운로드 성공·실패, reward 불일치 수. 분석은 Claude.


---

## `proposals/claude/20260930-EXP060M1-ANTIGRAVITY.md`

# EXP-060 M1 실행 카드 (antigravity) — 거울판 route screen 5,040경기 (판단 없음)
발행: Claude 2026-09-30 00:00 KST. 사람 방침(09-29 23:00): 밤사이 무인, Claude 가 에이전트 운영. **즉시 시작.**
EXP-058S 와 같은 절차. 사전등록 experiments/exp060_mbr/PREREG.md.

입력 sha(앞 12자): PREREG.md 137f92985e2f, jobs-m1-kaggle.json 36bdf0c14559 (3,024), jobs-m1-mac.json 5f979d6715e8 (2,016), manifest.json 1af1bd08584e, make_kaggle2.py 1cff6a2d9dfe, experiments/exp024_round2/run.py d6e5b4790a57.

0. cd ~/kaggle/Kaggriculture; shasum -a 256 로 위 파일 대조. 다르면 STOP.
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp060_mbr/jobs-m1-kaggle.json exp060m1 5
3. kaggle datasets create -p experiments/kaggle_runs/exp060m1/dataset → ready 확인 → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp060m1/kernel$k (실패 시 1회 재시도, 또 실패면 그 몫을 Mac 에서)
4. 동시에 Mac: caffeinate -dimsu nohup env EXP024_OUT=experiments/exp060_mbr/games-m1-mac.jsonl python experiments/exp024_round2/run.py experiments/exp060_mbr/jobs-m1-mac.json > experiments/exp060_mbr/run-m1-mac.log 2>&1 &
5. 단일 대기(폴링·중간 보고 없음) → k=0..4 output 을 합쳐 experiments/exp060_mbr/games-m1-kaggle.jsonl; wc -l experiments/exp060_mbr/games-m1-*.jsonl (합계 5,040)

금지: 스크립트·jobs·variants 수정, 제출, 판정, Kaggle API 로 경기 기록 다운로드(07:30 수집의 429 방지).
보고: coordination/reports/antigravity/<ts>-EXP060M1.md, 8줄 이내 — 완료 시각, 행 수(kaggle/mac), 실패 커널, 오류 행 수, "Claude 판정 대기".


---

## `proposals/claude/20260930-EXP060M2-ANTIGRAVITY.md`

# EXP-060 M2 실행 카드 (antigravity) — 거울판 route 확인 1,791경기 (판단 없음)
발행: Claude 2026-09-30 01:00 KST. M1 카드와 같은 절차, 파일 이름만 m2. 사전등록 experiments/exp060_mbr/PREREG.md (137f92985e2f). **즉시 시작.**

입력 sha(앞 12자): jobs-m2-kaggle.json 38d45c91caca (1,075), jobs-m2-mac.json 4deab0e39395 (716), make_kaggle2.py 1cff6a2d9dfe, experiments/exp024_round2/run.py d6e5b4790a57.

0. cd ~/kaggle/Kaggriculture; shasum -a 256 로 위 파일 대조. 다르면 STOP.
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp060_mbr/jobs-m2-kaggle.json exp060m2 5
3. kaggle datasets create -p experiments/kaggle_runs/exp060m2/dataset → ready 확인 → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp060m2/kernel$k (실패 시 1회 재시도, 또 실패면 그 몫을 Mac 에서)
4. 동시에 Mac: caffeinate -dimsu nohup env EXP024_OUT=experiments/exp060_mbr/games-m2-mac.jsonl python experiments/exp024_round2/run.py experiments/exp060_mbr/jobs-m2-mac.json > experiments/exp060_mbr/run-m2-mac.log 2>&1 &
5. 단일 대기(폴링·중간 보고 없음) → k=0..4 output 을 합쳐 experiments/exp060_mbr/games-m2-kaggle.jsonl; wc -l experiments/exp060_mbr/games-m2-*.jsonl (합계 1,791)

금지: 스크립트·jobs·variants 수정, 제출, 판정, Kaggle API 로 경기 기록 다운로드.
보고: coordination/reports/antigravity/<ts>-EXP060M2.md, 8줄 이내 — 완료 시각, 행 수(kaggle/mac), 실패 커널, 오류 행 수, "Claude 판정 대기".


---

## `proposals/claude/20260930-EXP060M3A-ANTIGRAVITY.md`

# EXP-060 M3-A 실행 카드 (antigravity) — 최종 후보 holdout HF + closed-loop 870경기 (판단 없음)
발행: Claude 2026-09-30 02:00 KST. M1·M2 카드와 같은 절차, 파일 이름만 m3-final. 사전등록 experiments/exp060_mbr/PREREG.md (137f92985e2f). **즉시 시작.**
(07:30 수집분 NEW panel 은 수집 뒤 별도 카드 M3-N 으로 돌린다.)

입력 sha(앞 12자): jobs-m3-final-kaggle.json 75f1c3665022 (522), jobs-m3-final-mac.json 2b4037cdae22 (348), cand/manifest-final.json 3b6e1b552c17, make_kaggle2.py 1cff6a2d9dfe, experiments/exp024_round2/run.py d6e5b4790a57.

0. cd ~/kaggle/Kaggriculture; shasum -a 256 로 위 파일 대조. 다르면 STOP.
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp060_mbr/jobs-m3-final-kaggle.json exp060m3a 5
3. kaggle datasets create -p experiments/kaggle_runs/exp060m3a/dataset → ready 확인 → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp060m3a/kernel$k (실패 시 1회 재시도, 또 실패면 그 몫을 Mac 에서)
4. 동시에 Mac: caffeinate -dimsu nohup env EXP024_OUT=experiments/exp060_mbr/games-m3-final-mac.jsonl python experiments/exp024_round2/run.py experiments/exp060_mbr/jobs-m3-final-mac.json > experiments/exp060_mbr/run-m3-final-mac.log 2>&1 &
5. 단일 대기(폴링·중간 보고 없음) → k=0..4 output 을 합쳐 experiments/exp060_mbr/games-m3-final-kaggle.jsonl; wc -l experiments/exp060_mbr/games-m3-final-*.jsonl (합계 870)

금지: 스크립트·jobs·후보 파일 수정, 제출, 판정, Kaggle API 로 경기 기록 다운로드(07:30 수집의 429 방지).
보고: coordination/reports/antigravity/<ts>-EXP060M3A.md, 8줄 이내 — 완료 시각, 행 수(kaggle/mac), 실패 커널, 오류 행 수, "Claude 판정 대기".


---

## `proposals/claude/20260930-HOSTEDX0930-ANTIGRAVITY.md`

# HOSTEDX0930 수집 카드 (antigravity) — X·새 d157 hosted 경기 (판단 없음)
발행: Claude 2026-09-29 22:10 KST. 실행 시각: 09-30 07:30 KST 이후(사람이 지시할 때). 판독 계획: experiments/slot2_x/readout0930/PLAN.md.
대상: X 56675447, d157r 56675458 (각 cap 400). hosted_20260929b 파이프라인을 폴더·ID·라벨만 바꿔 복사했다.

## 입력 sha256 (앞 12자)
- analysis/hosted_x0930/step1_2_collect.py = 718cc74d19b1
- analysis/hosted_x0930/step3_download_replays.py = 2fe223cd228e (2 worker, 요청 사이 1–2초: 429 대응)
- analysis/hosted_x0930/step4_5_fingerprint.py = c49d01a99727

## 단계 (각각 한 명령, 끝날 때까지 대기)
0. cd ~/kaggle/Kaggriculture; shasum -a 256 analysis/hosted_x0930/*.py → 대조. 다르면 STOP.
1. caffeinate -dimsu python3 analysis/hosted_x0930/step1_2_collect.py > analysis/hosted_x0930/step1_2.log 2>&1
2. caffeinate -dimsu python3 analysis/hosted_x0930/step3_download_replays.py > analysis/hosted_x0930/step3.log 2>&1
3. python3 analysis/hosted_x0930/step4_5_fingerprint.py > analysis/hosted_x0930/step4_5.log 2>&1

## 규칙
- 폴링·중간 보고 없음. 스크립트 수정 금지. 단계가 오류로 끝나면 같은 명령 1회만 재실행, 또 실패하면 STOP.
- 쓰기 허용: analysis/hosted_x0930/, private_artifacts/hosted_x0930/raw/, 보고서 1개.
- 금지: 제출, kernel 실행, 경기 실행, 기존 파일 수정, 결과 해석.

## 보고
coordination/reports/antigravity/<ts>-HOSTEDX0930.md, 8줄 이내: PASS/STOP+이유, as_of, 제출별 episode 수·W/D/L, 다운로드 실패 수, mismatch 수, opponents.csv 행 수, 소요 시간, "Claude 판독 대기".


---

## `proposals/claude/EXP-008-REVIEW-BLOCKED.md`

# EXP-008 검토 결과 — **BLOCKED** (사전등록 거부, Codex 반송)

검토자: Claude (opus-5) · 2026-09-14 · 대상 `coordination/proposals/codex/EXP-008-opening-liquidity.md` (2026-09-12 17:53)
판정: **BLOCKED**. `experiments/cards/EXP-008-opening-liquidity.md` 는 **생성하지 않았다.**
숫자 gate 는 하나도 완화하지 않았다. 아래 B1~B4 가 해소되고 재제출되면 원문 gate 그대로 수락한다.

가설 자체(HYP-0030, step1 opening schedule A→B)는 기각하지 않는다. one-factor 설계·target/control 분리·`next_if_failure` 의 쪼개기 금지 조항은 그대로 타당하다.
막는 것은 **계측 부재**와 **판정 불가능한 gate 한 건**이다.

---

## B1. 세 counter 중 두 개가 존재하지 않는다 — 제안서 자신의 사전조건 2 위반

제안서 사전조건 2: "`hire_failed`, `buy_failed`, `seed_blocked_plant` 를 engine attribution 기준으로 계측한다. counter 가 없으면 실행 금지다."

| counter | 현재 상태 | 근거 |
|---|---|---|
| `hire_failed` | **없음** | 레포 전체에서 이 문자열은 EXP-008 제안서 본문(29·33·49행)에만 나온다 |
| `seed_blocked_plant` | **없음** | 동일 — 제안서 본문에만 존재 |
| `buy_failed` | 있음 | `tools/instrument.py:359`, `coordination/proposals/claude/harness/sellaudit.py:149` |

### B1-a. `hire_failed` 는 기존 hook 으로 만들 수 없다
- `kaggriculture.py:702-705` `_do_hire` 는 `if farm["money"] < cost: return` — 예외도 플래그도 없는 **무음 실패**.
- HIRE 는 `_process_market` 의 "Atomic orders" 블록(`kaggriculture.py:571-578`)에서 `_do_hire` 로 직접 처리된다. **`_commit_unit` 을 거치지 않는다** (`_commit_unit` 은 `:618` 의 BUY_*/SELL 경로 전용).
- 따라서 `buy_failed` 는 HIRE 실패를 **구조적으로 관측할 수 없다**. EXP-006 hosted postmortem 의 "step25 HIRE 3건 무음 실패"가 바로 이 경로다.
- 필요한 작업: `_do_hire` 자체 hook, 또는 "Atomic orders" 구간에서 `farm["money"]` 와 `_hire_cost(farm["hires_today"])` 를 비교하는 pre/post hook.

### B1-b. `seed_blocked_plant` 는 hook 지점 자체가 없다
- `kaggriculture.py:915-932`: 한 턴의 crop 별 PLANT 요청 수가 보유 seed 를 넘으면 해당 crop 의 **모든** PLANT 를 `["PASS"]` 로 치환한 뒤 `_apply_unit_action` 을 호출한다.
- 이 블록은 `interpreter(state, env)` (`:894`) 안에 있다. `tools/instrument.py` 가 거는 hook 은 `_initialize` · `_end_of_day` · `_process_market` · `_apply_unit_action` · `_drop_inventories_to_shed` · `_commit_unit` **여섯 개뿐**이고 (`tools/instrument.py:210-215`, `:366-371`) `interpreter` 는 포함되지 않는다.
- `_apply_unit_action` hook 은 이미 `PASS` 로 바뀐 값만 본다 → 차단된 PLANT 와 진짜 PASS 를 구분할 수 없다.
- 필요한 작업: `interpreter` hook 신설, 또는 blocked-set 계산을 이미 hook 된 함수로 분리.

## B2. G1 의 step 단위 지표를 로컬에서 뽑을 수단이 없다

G1 은 `step23 cash` · `step25 hands` · `step47 nonempty_tiles` 를 요구한다.
- 이 세 값을 만드는 함수는 `tools/postmortem_hosted.py:146-165` `step_snapshot()` 뿐인데, `replay["info"]["TeamNames"]` 와 `replay["steps"]` 를 요구하는 **hosted replay JSON 전용**이다.
- EXP-008 은 tape 상대 + seed 로 돌리는 **로컬** 테스트다. 로컬 하니스 `sellaudit.run()` 의 반환 키는 `seed, agents, rewards, status, wall, engine_steps, players, per_item, floor_item` — **per-step snapshot 이 없다**.
- `env.steps` 는 `sellaudit.run` 안에 살아 있으므로 추출기 추가는 가능하다. 다만 지금은 없다. 없는 계측으로 gate 를 판정할 수는 없다.

## B3. G4 `buy_failed=0` 은 one_change 와 무관하게 결정적으로 실패한다 — gate 재정의 필요

측정값 (`experiments/results/hosted_postmortem_108076177_baseline_both_seats.jsonl`, parent 두 좌석 모두):

```
buy_failed = 34 · discard_units = 209
```

control (`..._108079022_control_baseline_both_seats.jsonl`) 의 parent: `buy_failed` 키 자체가 없음(=0) · `discard_units = 7`.

- G4 는 `discard` 와 `orders_truncated` 는 **"증가=0"(델타)** 으로, `hire_failed`·`buy_failed`·`seed_blocked_plant` 는 **절대 0** 으로 쓰여 있다.
- parent 가 target 셀에서 이미 `buy_failed=34` 이므로, opening schedule 한 블록을 바꾼다고 720 step 전체의 BUY 실패 34건이 0 이 될 이유가 없다. 즉 **G1~G3 결과와 무관하게 G4 에서 FAILURE 가 확정**되고, `failure` 조항이 "exact B schedule 폐기"를 명령하므로 가설이 측정되지 않은 채 죽는다.
- 나는 이 임계를 **바꾸지 않았다**. 델타로 읽는 것이 의도였는지, parent 의 34건이 opening schedule 에서 유래한다는 별도 근거가 있는지는 **Codex 가 카드에 명시**해야 할 사항이다. 결과를 본 뒤 바꾸는 것은 금지되므로 지금 확정해야 한다.

## B4. pool 지정이 stale glob 이다 — 오염 위험

- 카드의 pool 은 "`private_artifacts/tapes` 47개, pool hash `201d9724…6e1`".
- 현재 `private_artifacts/tapes/*.json` 은 **49개**다. 2026-09-12 에 `Remielle_episode-108076177-actions.json` 과 `today_episode-108079022-actions.json` 이 추가됐다 — **이 둘이 바로 EXP-008 의 target 과 control 테이프다.**
- glob 으로 pool 을 만들면 target/control 이 pool 에 섞여 G1·G3 가 독립이 아니게 된다.
- pool hash 는 재계산으로 확정했다: 카드 정의 `sha256(concat(sort(각 파일 sha256 hex)))` 를 **`*-replay.json` 47개**에 적용하면 정확히 `201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1` 이 나온다. (49개 전체 / 파일명 정렬 변형은 모두 불일치.)
- 요구: 카드에 `private_artifacts/tapes/*-replay.json` (47개) 을 명시하고, 실행 전 pool hash 검증을 필수 단계로 넣을 것. 이는 gate 완화가 아니라 모집단 고정이다.

---

## 확인했고 문제 없는 항목

- HYP-0030 이 `HYPOTHESES.md:396-407` 에 PLANNED 로 존재. `다음 행동` 이 본 검토와 일치.
- artifact 3종 존재: `experiments/results/hosted_postmortem_108076177.json`, `..._baseline_both_seats.jsonl`, `..._108079022_control_baseline_both_seats.jsonl`.
- target/control tape 파일 존재. 셀 수 정합: target 1시드×2좌석=2 · control 2 · public 4봇×5시드×2=40 · pool 47×3×2=282.
- parent tar sha256 `1c478c24…9721` 은 EXP-006/EXP-007 카드와 동일 값.
- `one_change` 가 step1 market 한 블록으로 분리되어 있고, A/B 가 WHEAT stock 13 을 보존한다는 점이 postmortem `focus_steps[step=1]` 과 일치 (target bank 2604 / opponent 2656, 차 52).
- `next_if_failure` 의 "cash-floor·order-only 로 쪼개기 금지" 조항은 사후 재해석 차단으로 타당. 유지할 것.

## 기록해 두는 한계 (BLOCK 사유 아님)

- G1 은 단일 시드 2셀이고 tape 는 결정론적이므로 좌석 교대가 독립 정보를 거의 주지 않는다. 실효 표본은 사실상 1. 카드가 `next_if_success` 를 "local mechanism support 로만 기록, 사람 승인 전 제출 금지" 로 못박은 것은 이 한계와 정합하며 적절하다. 성능 주장으로 승격하지 말 것.
- G5 action parity(step1 외 parent 와 byte-identical) 를 로컬에서 검증할 도구도 현재 없다. `tools/postmortem_hosted.py:own_action_difference` 는 hosted replay 두 개를 비교하는 함수다. candidate action 스트림 덤프 + 비교기가 필요하다. B2 와 같은 작업 묶음.
- candidate 미구현(SHA N/A)은 **BLOCK 사유가 아니다** — 사전등록은 구현 전에 하는 것이 맞다. 다만 사전조건 3 의 freeze 는 구현 후에만 가능하다.

---

## Codex 에게 반송하는 작업 목록

1. `_do_hire` (또는 `_process_market` atomic orders 구간) hook 으로 `hire_failed` 구현. engine attribution 기준.
2. `interpreter` hook 으로 `seed_blocked_plant` 구현. blocked crop 별 드롭된 PLANT 요청 수.
3. 로컬 에피소드에서 임의 step 의 `bank` / `hands` / `nonempty_tiles` 를 뽑는 추출기 추가 (`sellaudit.run` 의 `env.steps` 재사용). G1 판정에 필요.
4. candidate action 스트림 덤프 + parent 대비 step 집합 diff (G5 판정에 필요).
5. G4 의 `buy_failed` 를 절대 0 으로 둘지 "증가=0" 으로 둘지 확정하고 **근거와 함께** 카드에 고정. `hire_failed`·`seed_blocked_plant` 도 동일하게 명시.
6. pool 을 `*-replay.json` 47개로 명시하고 실행 전 pool hash `201d9724…6e1` 검증 단계 추가.
7. G1 의 step23/25/47 측정 시점 정의를 명시 (해당 index 의 observation 기준인지, 그 step 의 action 반영 후인지). `step_snapshot` 의 규약을 그대로 쓰면 `replay["steps"][i]` 의 observation 기준이다.

1~7 이 끝나고 counter 가 실제로 값을 내는 것이 확인되면, 원문 gate 를 **한 자리도 바꾸지 않고** `experiments/cards/EXP-008-opening-liquidity.md` 로 수락한다.


---

## `proposals/claude/NEXT_SESSION_PROMPT_2026-09-10.md`

# 새 채팅에 붙여넣을 프롬프트

---

Kaggle **Kaggriculture** 대회를 이어서 진행한다. 작업 폴더는 `~/kaggle/Kaggriculture` 이고 맥에 연결돼 있다.

## 0. 첫 번째로 할 일 — 점수 확인

**너는 Kaggle 에 도달할 수 없다.** 클라우드 컨테이너와 맥의 Cowork Linux VM 둘 다 `www.kaggle.com` 이 프록시 403 으로 막혀 있고 양쪽 다 `kaggle` CLI 가 없다. 맥의 `.venv` 는 macOS 3.13 프레임워크 파이썬이라 Linux VM 에서 실행 불가이고 그 venv 에 `kaggle` 패키지도 없다. **프록시를 끄거나 TLS 검증을 비활성화하는 우회를 시도하지 마라.**

그러니 나에게 아래를 맥 터미널에서 돌려서 붙여넣어 달라고 **먼저 요청하고 기다려라**:

```bash
cd ~/kaggle/Kaggriculture && kaggle competitions submissions kaggriculture
kaggle competitions leaderboard kaggriculture --show | head -20
```

점수를 받기 전에는 계획을 확정하지 마라. 받는 동안 아래 §4 의 읽기·계측 작업을 진행해도 된다.

## 1. 읽는 순서 — 이전 세션의 결론을 신뢰하지 마라

문서가 명시적으로 "검증됨"이라 표시한 것만 사실로 받아들여라.

1. `coordination/RESET_2026-09-10.md` ← 전부
2. `AGENTS.md` — **동결이다. 조항을 늘리지 마라.** §7.1b/§7.3 등 일부는 RESET §4 로 폐기됨
3. `evidence/FACTS.md` 의 `## 2026-09-10 테이프 재생 계측` 절 (F-T1~F-T6) — 아래 §3 에 요약돼 있다
4. `evidence/HOSTED_LEDGER.md` — **원장이 최신이 아니다.** 아래 §2 참조
5. `releases/public-yhay81-shop-router-0909-exact/manifest.json` — **여기 FAIL 이 하나 적혀 있다. 놓치지 마라**
6. `docs/code/yhay81_shop-router-0909.ipynb` — **셀 실행 금지.** `json.load` + `ast` 로 상수만 꺼내라 (저장소의 일부 노트북에 악성 페이로드 가능성). `exec`/`eval`/`nbconvert`/`pickle` 금지

## 2. 제출 현황 (2026-09-10 기준, 원장 미갱신 상태)

| # | 라벨 | artifact SHA-256 | submission ID | 상태 |
|---|---|---|---|---|
| v0 | 규칙기반 실행기 (09-07) | `aed79ff3…5844` | **56068891** | publicScore **337.3**, 6,989/7,963위 |
| v1-20260910 | 규칙기반 실행기 현행 main.py | `723f8fd8…eb4a` | **56145245** | 13:36:45 UTC 접수, PENDING |
| yhay81-exact | 공개 9위 노트북 **무수정** 재현 | `40d2bc3986f4ed3e927c81842d399a58bf20b07b57858355da4b75c280fd7791` (167,858 B) | **미기록** | 사람이 직접 제출함 |

- `evaluation.md:1` — 하루 5개 제출, **최신 2개만 추적되고 최종 평가도 최신 2개**. FIFO 이므로 현재 활성 슬롯은 `{v1-20260910, yhay81-exact}` 이고 v0 는 은퇴했을 것이다. **이걸 §0 의 CLI 출력으로 확인하라.**
- **`HOSTED_LEDGER.md` 에 yhay81-exact 행이 없다.** submission ID 를 받으면 §7.5 Ledger 규약대로 네가 채워라. (`evidence/` 는 Claude 소유 경로다)
- yhay81-exact 의 3개 멤버 해시는 저자가 노트북 셀[5] `expected_hashes` 에 박아둔 값과 **전부 일치**한다 — 진본 확인됨.

## 3. 2026-09-10 에 검증된 것

### 계측 (940 에피소드, `[LOCAL]`, 엔진 1.32.7 `bc8a5487…653e`)
47개 스크랩 테이프 × {boatlee, starter} × seeds[7,1000,1001,1002,1003] × 양좌석. 결측 0, 에러 0.

- **순수 테이프 재생(전략 로직 0)이 현행 `main.py` 를 페어드로 압도**: 평균 **+79,744** [77,597, 81,892], **929승 11패**
- 순수 재생 vs boatlee(LB 59위): **263-0-207 (56.0%)**, 평균차 −4,239, 중앙값 +2,947
- `main.py` vs boatlee: **23,258 vs 140,813** (궤멸)
- 테이프별 최고 Syed_Asad_Ali_106273289 **123,358**, 최저는 **hosted 1위 ymg_aq** 테이프 **26,490** — ymg_aq 는 hands 불일치 최다(평균 34.5턴)·주문 체결률 최저(74%). `[INFERENCE]` ymg_aq 는 테이프가 아니라 반응형이다. **"1위 것을 베껴라"는 틀린 휴리스틱.**

### yhay81 에이전트 계측 (`[LOCAL]`, 계획 서브에이전트 산출 — 나는 4판만 독립 재현했다)
- 홀드아웃 seeds 3000–3011 × 공개봇 4종 × 양좌석 96판 → **96-0-0**, 페어드 1.0000, Wilson 95% 하한 0.9615
- 상대별 최소 마진 전부 양수: boatlee +11,325 / lynn +2,295 / rayk +17,045 / kaito +23,631
- 런타임: 에이전트 CPU **0.084 s/에피소드** (예산 1,200s 의 0.007%), p99 턴 0.13 ms
- **수리 규칙 3종 기여도 합계 +13** (잡초 DIG +130 이 1판에서만 발화, 매도 1턴 당김 **정확히 0**, step718 청산 **정확히 0**)
- **라우팅 이득 실측 +1,671**, 오라클(시드별 최적 plan) 상한 +4,792, 그러나 **shop-pair 재적합은 LOO-CV −428** (같은 shop pair 가 시드마다 다른 최적 plan 을 가짐 → shop pair 에 일반화 신호 없음)
- 자기대전은 **정확한 동점** (99,743/99,743 등). 09-09 공개 노트북이라 동일 포크가 늘면 무승부가 쌓여 BT 레이팅이 서로를 끌어당긴다 — **이 계열의 가장 실질적인 구조적 위험**
- 상대만 바꾸면 우리 액션 해시가 달라진다 → 완전 개루프는 아니고 시장가를 통해 반응한다

### ★ 가장 큰 미개척 지점 — yhay81 도 무음 실패가 크다
`releases/public-yhay81-shop-router-0909-exact/manifest.json` 의 `preflight.silent_failure_gate` 가 **FAIL** 이다:

```
candidate no-op 44..136 / shed discard 1..7 /
unfilled sell 83,998..116,738 units / buy failure 0..2  (player-run 당)
```

**미체결 매도가 8만~11만 유닛이다.** 9위 에이전트가 팔려고 낸 주문의 상당량이 체결되지 않는다. 이게 사실이라면 **테이프를 바꾸지 않고 시장 레이어만 고쳐도 큰 폭의 개선 여지가 있다** — 그리고 그것은 우리 자체 코드가 된다(아래 §5 규정 문제를 우회한다). **이 숫자를 먼저 재확인하고, 원인을 분해하라** (흡수량 초과인가, 재고 부족인가, 주문 10개 절삭인가, 가격 조건인가).

### 엔진 사실 `[ENGINE]`
- **F-T3**: 엔진은 `hands` 길이 정렬을 요구하지 않는다. `kaggriculture.py:913-918` 이 길이 검증 없이 받고 `:937-939` 가 리스트 길이만큼 순회, `_farmer_position(:278-282)` 이 범위 밖에 `None`, `_apply_unit_action(:314,317-319)` 이 즉시 return → **초과 hand 는 조용한 no-op, 부족 hand 는 암묵 PASS.** 예외 0.
- **F-T4**: 로컬 `env.run()` 은 **완전 결정론**이다. 게임 상태에 영향 주는 RNG 는 3줄뿐(`:839` 잡초, `:871` `rng = random.Random((seed*1_000_003) ^ day)`, `:891` `rng.choice(sorted(SHOPS))`)이고 시딩이 `(seed, day)` 에만 의존한다. 상대·시장가·좌석 무관. **같은 시드 2회 실행 → 뱅크·상점 해금 순서·잡초 수 완전 동일.** zhincez 의 "같은 시드도 흔들린다" 주장은 **반박됨**(로컬 한정; hosted 인프라는 `[N/A]`).
  → **이것이 자체 테이프 생성(오프라인 액션 시퀀스 탐색)을 가능하게 하는 근거다.**
- **F-T5**: `kaggle_environments/core.py` 의 `__loop_through_interpreter` 가 매 스텝 `structify(state)` 로 상태를 깊은 복제한다. 계측기에서 객체 `id()` 를 한 번만 캡처하면 turn 0 이후 전부 매칭 실패한다.

### `[COMMUNITY]` 미승격
`docs/code/zhincez_replaying-someone-elses-tape-gets-you-88-percent.ipynb` — 남의 테이프 재생은 소유자 점수의 **약 88%** 만 회수(자기보고 n=2), 복사 계열 전체가 골드 아래 상한이라 주장. Thomas Tschinkel 의 replay router 공개 LB **2,531.4**, zhincez 본인 2,527.7. **§3 증거 규율상 승격 근거로 쓸 수 없다.** 다만 우리 47테이프 데이터가 이 방향을 지지한다.

## 4. 목표와 제약

- **목표: 최소 상위 500위 ≈ 2,535.8점** (2026-09-10 08:34 CSV, 8,481팀 기준). 상한은 열어둔다. 10위(상금 경계) 2,963.7. **경계가 하루 +50~96 오른다** — 이 값들을 §0 의 최신 리더보드로 갱신하라.
- 마감 2026-09-30, 최종 평가 10/1~10/15 Bradley-Terry.
- 제출 하루 5개, 최종 평가는 마지막 2개. **매일 제출한다** (정지 = 후퇴: 상위 10팀 마지막 제출 경과일 중앙값 0.47일, 2,000위+ 는 18.64일).
- `AGENTS.md §7.4`: **활성 슬롯 2개는 지는 경기가 겹치지 않는 서로 다른 두 전략**이어야 한다.
- 엔진 `kaggle-environments==1.32.7` 고정. 클라우드 컨테이너에 `pip3 install --break-system-packages kaggle-environments==1.32.7` 로 설치 가능하고, 설치본 `kaggriculture.py` sha256 이 `bc8a5487…653e` = ENGINE_LOCK 값과 일치한다.

## 5. 규정 — 여기가 진짜 갈림길이다

`docs/official/rules.md` 를 **직접 읽고** 판단하라. 내가 확인한 지점:

- `:108` 리플레이는 호스트가 공개·다운로드 가능하게 함. `:70` §2.6a 외부 데이터는 공개·전원 동등접근·무비용이면 허용.
- `:148b` Kaggle 에 공개 공유된 Competition Code 는 상업이용 제한 없는 **OSI 승인 라이선스로 간주**. `:149c` 도 OSI 오픈소스 사용을 허용. → **yhay81 테이프·코드는 출처가 깨끗하다** (저자가 Apache-2.0 `LICENSE.txt` 동봉).
- **`:185` §3.14a** — 제출물이 *"your own original work"* 이고 *"sole and exclusive owner and rights holder"* 임을 **보증**하라. `:59` §2.5a.1 수상 시 제출물+소스 전부 CC-BY 4.0, `:96` "무제한 라이선스 부여 권리 표명". **제출물의 본체 전부가 남의 저작물인 경우 이 보증이 성립하는지는 미해결이다.**
- `private_artifacts/tapes/` 의 **긁어온 라이벌 리플레이 47개는 분석 입력으로만 써라. 제출물에 박지 마라** — §3.14a·§2.5 와 충돌하고, `evidence/KILLS.md:10` **K3(라이벌 테이프 복사)가 아직 KILL 등재 상태**다. `AGENTS.md §9` 는 재검토 근거로 `[ENGINE]`/`[HOSTED]` 를 요구한다(`[LOCAL]` 단독 불가). **K3 해제는 사람 승인 사항.**

**따라서 규정 위험이 0 인 경로를 우선하라**: 우리가 직접 만든 코드, 우리가 생성한 테이프. F-T4(결정론)가 자체 테이프 생성을 가능하게 한다.

## 6. 디스크에 있는 자산

- `private_artifacts/tapes/` — 47개, 각 720 원소 `{"turn": i, "action": {"farmer":[...], "hands":[[...]], "market":[[...]]}}`. **`turn 0` 은 프레임워크 placeholder이므로 `obs["step"]==s` 일 때 낼 액션은 `tape[s+1]["action"]`.** distinct 에피소드는 29개(18개가 양쪽 플레이어로 이중 계상). 출처 8팀: ymg_aq, Crop_Dusta, 3정훈, Jiro2, Mengfei_Li, Suliman_Tadros, Syed_Asad_Ali, binghua
- `private_artifacts/replays/top/` — 75개 × 약 32MB 원본 hosted 리플레이 (2.3GB). **통째로 `json.load` 하지 마라**
- `private_artifacts/replays/own/` — 우리 hosted 에피소드 10개
- `opponents/public/` — boatlee(59위) / lynnsakurai(235위) / raykkretzschmar(1,132위) / kaitofukami(1,427위)
- `docs/code/` — 공개 노트북 30개
- `scratch/_bundle/tape_bundle.tar.gz` — 위 테이프 47개 + 상대봇 4개 + main.py 를 묶어둔 것. 클라우드 컨테이너로 스테이징해서 바로 풀면 된다
- **주의**: 이전 세션이 클라우드 컨테이너 `/home/claude/tapelab/` 에 만든 하네스(`tapelib.py`, `run_experiment.py`, `results.jsonl` 960줄)는 **그 세션과 함께 사라졌다.** 필요하면 재구축하라

## 7. 이번 세션에 할 일

**점수를 받은 뒤, "지금 올릴 단 하나의 제출"을 설계하라.** 여러 안을 나열하고 끝내지 마라 — 하나로 수렴하라.

산출물:

1. **선택안과 이유** — 무엇을 만드는가(아키텍처 1문단), 왜 지금 그것인가. "의미 있음"을 네가 정의하라: 레이팅 기대값 / 정보 획득량(로컬↔hosted 상관축) / §7.4 슬롯 비상관화. 셋의 트레이드오프를 명시하고 어디에 걸었는지 밝혀라.
2. **기각한 대안 최소 3개**와 기각 사유 — **숫자로**.
3. **사전등록 실험 카드** — `AGENTS.md §5` 스키마 전 항목을 **숫자 임계**로. 서술형 항목이 하나라도 있으면 실패다. (§7.3 postmortem 인용 강제는 RESET §4 로 폐기)
4. **§7.5 릴리스 체크리스트 6줄**을 어떻게 채울지 — Identity/Schema/Runtime/Isolation/License 는 제출 전, Ledger 는 제출 후
5. **은퇴 결정** — 어느 활성 슬롯을 교체하는가. §7.4 "지는 경기가 겹치지 않는 두 슬롯" 기준으로 논증
6. **이탈 조건** — 어떤 숫자가 나오면 이 방향을 접는가
7. **사람 승인이 필요한 항목** 목록

## 8. 작업 방식

- **매 실행마다 서브에이전트로 독립 검토를 붙여라.** 이전 세션이 자기 결론을 검증하지 않아 KILL 하나(K10)를 잘못 등재했다. 검토자에게는 "승인이 아니라 깨뜨리는 것이 일"이라고 지시하라.
- 소스 읽기·정형 추출·계측처럼 **Sonnet 으로 되는 작업은 서브에이전트에 맡겨라** (토큰 절약).
- **문서를 늘리지 마라.** `AGENTS.md` 동결. 산출물은 제출된 에이전트지 문서가 아니다. 새 사실은 `evidence/FACTS.md` 에 **재현 명령과 함께** 짧게.
- **막히면 추측하지 말고 무엇이 모호한지 적고 멈춰라.**
- 소유 경로: `experiments/cards/`·`evidence/`·`plan/` 은 Claude, `main.py`·`src/`·`tools/`·`releases/` 는 Codex, `docs/`·`analysis/`·`opponents/` 는 Gemini. 소유 경로 밖은 `coordination/proposals/claude/` 로 제안만.
- **Kaggle 제출·팀 변경·코드 공개는 사람 승인 없이 실행하지 않는다** (`AGENTS.md §8`). 어차피 네트워크가 없어 네가 실행할 수도 없다.

답변은 **한 줄 직관 요약**으로 시작하고, 마지막에 **다음 행동 2개**를 추천해라.


---

## `proposals/claude/PROPOSAL_20260914_board_handoff_sync.md`

# PROPOSAL (Claude → 코디네이터) — BOARD·HANDOFF 현재 상태 정정

발신 Claude · 2026-09-14 10:45 UTC
대상 `coordination/BOARD.md` (코디네이터 전용), `coordination/HANDOFF_CURRENT.md`
**Claude 는 이 두 파일을 쓰지 않는다** (`AGENTS.md` §4 소유권). 아래 문구를 그대로 붙여 넣으면 된다.

1. **무엇이 문제인가:** 들어오는 agent 가 문서마다 다른 작업을 시작할 수 있다.
   BOARD 는 EXP-008 을 "Claude card 수락 대기" 로, HANDOFF 는 "첫 제출 전" 으로,
   정본 master plan 은 "첫 제출 지시" 로 남아 있다. 실제로는 제출 5건, 활성 2슬롯, EXP-008 사전등록 완료다.
2. **왜 중요한가:** 세션 시작 1번 문서가 틀리면 그날 작업이 통째로 어긋난다.
   BOARD 자신이 2026-09-13 갱신 때 같은 이유로 신선도 게이트를 추가했다.
3. **무엇을 확인했는가:** BOARD 의 표(제출 5건·활성 슬롯·레이팅)는 **맞다.** 틀린 것은 **한 문장 요약 한 줄**뿐이다.
   HANDOFF 는 2026-09-07 자로 통째로 낡았다.
4. **막힌 점과 다음 행동:** 소유권 때문에 Claude 가 고칠 수 없다. 코디네이터(또는 사람 요청을 받은 Codex)가 적용한다.

---

## P0 — `coordination/BOARD.md` hosted 레이팅 갱신 `[2026-09-14 10:47 UTC 추가]`

새 snapshot 이 들어왔다 (`evidence/HOSTED_LEDGER.md` 2026-09-14 10:47 UTC 절). BOARD 표 두 줄이 낡았다.

현재:

```text
| 활성 hosted 레이팅 | EXP-006 **1915.6** · EXP-007 **1819.8** (2026-09-12 사람 제공 snapshot) | 동 |
| 최신 완료 snapshot | EXP-006 **1915.6** · EXP-007 **1819.8**, 둘 다 COMPLETE | 동 |
```

교체:

```text
| 활성 hosted 레이팅 | EXP-006 **1896.9** · EXP-007 **1647.4** (2026-09-14 사람 제공 snapshot) | 동 |
| 최신 완료 snapshot | EXP-006 **1896.9** · EXP-007 **1647.4**, 둘 다 COMPLETE · 09-12 대비 −18.7 / −172.4 | 동 |
```

`[INFERENCE]` 두 artifact 는 접수 후 바이트가 고정이므로 이 하락은 **우리 코드 변화가 아니다.**
상대 분포 변화이거나 rating 수렴 중이며, 이 snapshot 만으로는 구분할 수 없다.

---

## P1 — `coordination/BOARD.md` 한 문장 요약 교체 (1줄)

현재:

```text
**한 문장 요약: EXP-006의 큰 패배는 첫날 cash 0 → 다음 날 HIRE 3건 실패의 연쇄였고, 이를 겨냥한 EXP-008 opening schedule A/B가 Claude card 수락 대기다.**
```

교체:

```text
**한 문장 요약: EXP-006의 큰 패배는 첫날 cash 0 → 다음 날 HIRE 3건 실패의 연쇄였고, 이를 겨냥한 EXP-008 카드는 사전등록이 끝났다(commit 0291151, card sha256 e0e93652…773a). 다음 작업은 Codex의 candidate 구현과 326셀 비교이며, 그 전에 parent baseline을 먼저 기록해야 한다.**
```

갱신일 줄도 `갱신 **2026-09-14**` 로 바꾼다.

## P2 — `coordination/HANDOFF_CURRENT.md` 전면 교체

현재 내용은 2026-09-07 v0 제출 직전 상태다. 아래로 교체한다.

```text
# HANDOFF — 최신 인계

**2026-09-14 · Claude(opus-5) → Codex / 사람**

**VERDICT**: EXP-008 사전등록이 끝났고 strict validator 도 통과한다. 다음은 Codex 의 candidate 구현이다.

**현재 parent**: EXP-006 tar sha256 1c478c24…9721 (hosted 56165718)
**활성 슬롯**: EXP-006 56165718 (1915.6) · EXP-007 56175620 (1819.8) — 2026-09-12 사람 제공 snapshot
**최종 제출 마감**: 2026-09-30 23:59 UTC

**다음 작업 (우선순위 순)**
1. Codex — `coordination/proposals/claude/WORK_ORDER_EXP-008_execution.md`
   candidate 구현 → SHA freeze → parent 326셀 baseline 선기록 → candidate 실행 → G1~G5 판정
2. Codex — `coordination/proposals/claude/WORK_ORDER_gate_split_and_release_tracking.md`
   일반 release gate 에서 sell_unfilled 강등, releases/ 추적 (1번과 병행 가능)
3. 사람 — 최신 hosted snapshot 확보 (Kaggle CLI). 현재 hosted 상태는 09-12 이후 N/A
4. 사람/Claude — 두 슬롯 비상관 재판독 계획을 제출 전에 고정 (별도 카드)

**실제 blocker**: 없음. EXP-008 은 Codex 착수 대기다.

**하지 말 것**
- EXP-008 결과를 hosted 우위 근거로 승격하지 말 것. `[LOCAL]` mechanism support 까지다.
- 최신 상대 검증을 EXP-008 표본에 섞지 말 것. 별도 실험으로 분리한다.
```

## P3 — 정본 master plan 의 첫 제출 지시 (사람 확인 필요)

`plan/` 의 master plan 에 "첫 제출" 지시가 남아 있다. 이미 5건 제출했으므로
해당 절을 "완료 2026-09-07 (v0 56068891)" 로 표시하거나 §진행 상황으로 옮겨야 한다.
`plan/` 은 Claude 소유이므로, 사람이 어느 문서를 정본으로 볼지 정해 주면 Claude 가 적용한다.
**질문: 정본은 `plan/kaggriculture_master_plan_claude-opus-5.md` 인가, `plan/kaggriculture_final_plan.md` 인가?**

VERDICT | 제안 | BOARD 1줄 · HANDOFF 전면 · master plan 1절 | Claude 미적용(소유권) | NEXT ACTION: 코디네이터 적용


---

## `proposals/claude/WORK_ORDER_20260916_GATE_SCOPE_DECISION.md`

# 제안 — release zero gate 의 **적용 범위** 결정 (사람 승인 필요)

발행 2026-09-16 21:10 KST · Claude(opus-5) · 수신 Coordinator(Codex) → 사람
근거 `evidence/FACTS.md` F-T16 / F-T17 · `experiments/results/p1_release_preflight/aggregate.json`

## 0. 무엇을 결정해 달라는 것인가

> **release zero gate 를 "우리가 도입한 손실"에만 적용할 것인가, 아니면 지금처럼 artifact 전체에 적용할 것인가.**

임계를 낮추자는 제안이 **아니다.** 새로 도입한 손실에는 절대 0 을 그대로 유지한다.
바꾸자는 것은 **어디에 적용하는가**다.

## 1. 왜 지금 결정해야 하는가

계획 §5.2-4 는 "P1b FAIL 이면 새 전략 카드 HOLD" 로 적혀 있다. P1b 는 FAIL 이다.
그 문장을 그대로 두면 **09-30 까지 신규 제출 0건**이 확정된다.
전략 중단선 **09-27 00:00 KST 까지 10일 3시간** 남았다.
결정을 미루면 "결정하지 않음"이 곧 "제출 0건"으로 자동 확정된다.

## 2. 결정에 필요한 사실 3개 (전부 측정됨)

**① 현재 활성 2슬롯 모두 zero gate 를 통과하지 못한다** `[LOCAL]`

| 제출 | hosted score | self-play zero gate |
|---|---:|---|
| EXP-006 `56165718` | 1862.6 | **FAIL** — `noop` 44/114/44, `shed_discarded` 7/6/7 |
| EXP-007 `56175620` | 1635.9 | **FAIL** — `noop` 62/74/62, `shed_discarded` 0/7/0, `buy_failed` 0/1/3 |

출처 `releases/public-thomas-replay-router-v2-exact/preflight-selfplay.json`,
`releases/public-yhay81-shop-router-0909-exact/preflight_selfplay.json`.
zero gate 는 Kaggle 규칙이 아니라 **우리 자체 규율**이며 hosted 실행을 막지 않는다.

**② 실패는 우리 layer 가 아니라 공개 parent 에서 상속됐다** `[LOCAL]`

무수정 yhay81 exact 와 EXP-006 의 self-play counter 가 세 seed 전부 **동일**하다
(44/7, 114/6, 44/7). clone-preempt layer 가 바꾼 것은 reward 뿐이고 무음 실패 counter 는 0 만큼 바꿨다.
→ 이 counter 들을 0 으로 만드는 일은 버그 수정이 아니라 **남의 open-loop tape 재작성**이다.
그런데 `actions.json` tape · `SHOP_PLANS` · market ordering 은 전부 `fixed` 다.
**correctness repair 로 접근 가능한 표면이 사실상 없다.**

**③ 게이트가 포화해 정보를 주지 않는다** `[LOCAL]`

P1b 결과는 gated parent record **16/16 FAIL** 이다. 후보를 구분하는 정보량이 0 이다.
이것은 AGENTS §7.1b 가 이미 인정한 상황과 같은 구조다 — KAGRI-015 에서 후보와 parent 가
둘 다 4봇 상대 0/0/400 이라 페어드 점수가 정보를 주지 못했던 때와 동일하다.

## 3. 제안 내용

```text
release zero gate 를 두 층으로 나눈다.

[층 1 — 상속 baseline]  parent artifact 가 이미 가지고 있던 counter 값
   판정: candidate <= parent, 같은 cell·같은 seed·같은 좌석
   근거: EXP-008 G4 가 이미 쓰던 기준. 새 기준이 아니다.

[층 2 — 신규 도입]  우리 변경이 만든 손실 (새 guard 포함)
   판정: 절대 0. 변경 없음.
   새 guard 는 전용 activation counter + reason counter 를 함께 낸다. 변경 없음.
```

**반드시 함께 가는 안전장치 2개 (없으면 이 제안은 기각돼야 한다):**

1. **baseline freeze.** 층 1 의 기준값은 실행 **전에** parent artifact SHA 와 함께 고정하고
   `experiments/baselines/<artifact-sha>.json` 에 커밋한다. 사후 조정 불가.
   기준값은 P1b 의 16 record 값을 그대로 쓴다(`shed_discarded` 482, `noop_actions` 3,488 등).
2. **사람 승인.** AGENTS §8 대상이다. Claude·Codex 단독으로 채택하지 않는다.

## 4. 이 제안의 위험 — 솔직하게

**겉모습이 "날짜에 맞춰 게이트를 무르는 것"과 같다.** AGENTS §7.4 와 계획 §6 이 금지하는 행동이다.
차이는 하나뿐이다 — 임계를 건드리지 않고 **적용 대상만** 나눈다는 것.
그러나 이 구분은 남용하기 쉽다. 그래서:

- 이 제안이 채택되더라도 **`shed_discarded` 를 diagnostic 으로 강등하지 않는다.** 여전히 gate 다.
- `sell_unfilled` 를 gate 로 승격하지 않는다. 변경 없음.
- EXP-008 의 FAILURE 판정을 소급 변경하지 않는다.
- 이 제안은 **제출 승인이 아니다.** 후보의 강도 판정(AGENTS §7.1 페어드 CI 하한 > 0.5)은 그대로다.
- 채택 시 그 사유·날짜·근거를 BOARD 와 이 파일에 남긴다. 조용히 바꾸지 않는다.

## 5. 기각할 경우 — 목표 변경으로 선택지가 사라졌다 `[2026-09-16 21:40 갱신]`

**사람이 목표를 확정했다: 점수 유지가 아니라 최소 동메달 확보.**
동메달 = 상위 10% = 09-10 snapshot 기준 **rank 848 / 약 2,303점**
(8,481팀, `kaggriculture-publicleaderboard-2026-09-10T08:34:17.csv`).
현재 최고 활성 점수는 `EXP-006` **1,862.6** 이고 **격차 약 440점**이다.

→ 이 목표에서는 **현재 A/B 유지가 곧 목표 실패 확정**이다. 신규 제출은 선택이 아니라 필수다.
따라서 이 제안을 기각하면 **release zero gate 가 동메달 경로 자체를 봉쇄**한다.
기각하려면 "zero gate 를 통과하면서 2,303점에 도달하는 artifact 를 12일 안에 만든다" 는
경로를 함께 제시해야 한다. 현재 그런 후보는 없다 —
공개 자료 triage 51/18건에서 채택 3건은 전부 *힌트* 수준이고 성능 artifact 는 0건이다
(`analysis/public_source_triage/20260916.md`).

이전 판(09-16 21:10)의 "제출 0건이 정상적인 최적해일 수 있다" 는 문장은
**점수 유지가 목표일 때의 논리였고, 목표 변경으로 무효다.**

## 6. 담당과 모델

| 단계 | 담당 | 모델 |
|---|---|---|
| 제안 작성 | Claude (완료 — 이 문서) | `claude-opus-5` — 계약 해석이라 상위 모델 |
| 독립 검토 | **Codex** (사람 지정 2026-09-16) | `claude-opus-5` 급 권장 — §4 위험 판단이 핵심 |
| baseline freeze 구현 | Codex | `claude-sonnet-5` 충분 — JSON 고정과 SHA 기록뿐 |
| 채택/기각 결정 | **사람** | — |

## 7. 결정 기한

**09-27 00:00 KST (전략 중단선) 이전.** 그 이후의 채택은 freeze·재검증 시간이 없어 무의미하다.
§WORK_ORDER_20260916_P1C_MARGIN_DISTRIBUTION 의 결과가 나오면 그 판정표와 함께 올린다.


---

## `proposals/claude/WORK_ORDER_20260916_P1C_MARGIN_DISTRIBUTION.md`

# WORK ORDER — P1c 축소판: 현재 window 패배 마진 분포

발행 2026-09-16 21:05 KST · Claude(opus-5) · 선행 근거 `evidence/FACTS.md` F-T16 / F-T17

## 0. 이 작업이 결정하는 것

**"09-30까지 correctness 경로에 며칠을 쓸 것인가"** 한 가지다.
`shed_discarded` 회수 가치는 baseline **520~600 coin/경기**다(F-T16).
그 값이 실제 패배 마진 분포의 어디에 있는지가 나오면 EXP-011 착수 여부가 자동으로 정해진다.

**이미 나온 부분(F-T17, 09-12 window, 재조회 없음):**

| | EXP-006 | EXP-007 |
|---|---|---|
| W/D/L | 41/0/9 | 21/**9**/20 |
| 패배 마진 median | 13,359 | 3,606 |
| 패배 < 1,000 | 1/9 | 4/20 |
| 무승부 마진 | — | **전부 정확히 0** |

→ 남은 것은 **현재 window 로 이 표를 갱신**하는 것뿐이다. 새 설계는 없다.

## 1. 담당과 모델

| 단계 | 담당 | 모델 | 이유 |
|---|---|---|---|
| 1-A 데이터 수집 | **사람(맥 터미널)** | — | Kaggle 자격증명이 맥에만 있다. Claude 클라우드 세션은 Kaggle 에 닿지 못한다. 프록시·우회 시도 금지 |
| 1-B 집계·표 작성 | **Sonnet 서브에이전트** | `claude-sonnet-5` | JSON 파싱·정형 집계·표 출력. 판단이 없다. **Opus 불필요** |
| 1-C 판독·결정 연결 | Claude 본세션 | `claude-opus-5` | gate 범위·카드 착수 판단과 연결되므로 상위 모델 |

Gemini 는 이번 건에서 호출하지 않는다 — §5.1 source triage 와 별개 작업이고, 입력이 CLI 출력 2개뿐이다.

## 2. 1-A 사람이 실행할 명령 (맥 터미널, 작업 폴더 루트)

```bash
cd ~/kaggle/Kaggriculture
date -u +"UTC now = %Y-%m-%dT%H:%M:%SZ"          # window 끝을 먼저 고정해서 붙여넣을 것

mkdir -p private_artifacts/episodes/20260916
kaggle competitions episodes 56165718 > private_artifacts/episodes/20260916/exp006_56165718.json
kaggle competitions episodes 56175620 > private_artifacts/episodes/20260916/exp007_56175620.json

wc -c private_artifacts/episodes/20260916/*.json
shasum -a 256 private_artifacts/episodes/20260916/*.json
```

**붙여넣어 줄 것:** 위 `date -u` 출력 1줄 + `wc -c` + `shasum` 결과.
명령이 실패하면 **실패한 그대로** 알려줄 것. "변경 없음"으로 기록하지 않는다.

## 3. 1-B Sonnet 서브에이전트 지시문 (그대로 사용)

```text
역할: 읽기 전용 집계자. 새 경기 실행·파일 수정·Kaggle 접근을 하지 않는다.

입력 파일 2개:
  private_artifacts/episodes/20260916/exp006_56165718.json
  private_artifacts/episodes/20260916/exp007_56175620.json
참조 구현: tools/compare_hosted_episodes.py (시간 매칭 방식)
참조 스키마: experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json

window 는 실행 전에 고정한다. as_of = 사람이 준 UTC 시각, after = as_of - 24h.
그 안에서 state=="COMPLETED" 인 최신 50판을 submission 별로 고른다.
50판 미만이면 관측된 판수와 N/A 를 그대로 보고한다. 기간을 소급 확대하지 않는다.

submission 별로 다음을 산출한다.
1. n, W/D/L, point_score, seat 분포
2. 패배 마진(상대 reward - 우리 reward) 전체 목록을 오름차순으로, episode_id/seat/상대명 포함
3. 패배 마진의 min / median / max
4. 패배 마진 < 600, < 1000, < 5000, < 10000 각각의 건수와 비율
5. 승리 마진의 min / median / max 와 < 1000, < 5000 건수
6. 무승부 건수와, 각 무승부의 (우리 reward, 상대 reward, 차이). 차이가 정확히 0 인 건수를 따로 센다
7. 상대 이름 목록 (두 submission 의 교집합도 함께)

출력:
  experiments/results/hosted_margin_20260916/summary.json  (위 1~7 을 구조화)
  experiments/results/hosted_margin_20260916/report.md     (표 형식)
두 파일에 입력 JSON 2개의 sha256 과 고정한 window 시각을 반드시 적는다.

금지: 임계값을 새로 만들지 말 것. 위 6개 임계(600/1000/5000/10000)만 쓴다.
     두 submission 의 point score 를 직접 비교해 우열을 주장하지 말 것 — 상대 pool 이 다르다.
     결과를 본 뒤 window 나 표본 수를 바꾸지 말 것.
숫자만 보고하고 해석은 하지 않는다.
```

## 4. 판정 규칙 — 실행 전 고정

`P` = EXP-006 의 **패배 마진 < 1,000 비율**, `Q` = EXP-007 의 동일 비율.

| 조건 | 결론 | 다음 |
|---|---|---|
| `max(P, Q) >= 0.25` | 접전이 지배적 | EXP-011 착수. `shed_discarded` 600 coin 회수가 W/D/L 에 실제로 기여 |
| `0.10 <= max(P, Q) < 0.25` | 경계 | EXP-011 착수하되 **동시에** gate 범위 제안(§WORK_ORDER_GATE_SCOPE)을 사람 결정에 올린다 |
| `max(P, Q) < 0.10` | 접전이 드물다 | EXP-011 을 **09-27 이후 보류 목록**으로 보내고 남은 일수를 다른 곳에 쓴다 |
| 무승부 중 마진 정확히 0 이 **3건 이상** | 위 결과와 **무관하게** 별도 보고 | clone 대칭 파괴가 `shed_discarded` 보다 W/D/L 기여가 크다는 신호. HYP-0006 판독에 연결하고 새 카드로 분리 |

09-12 값으로는 `P = 1/9 = 0.111`, `Q = 4/20 = 0.200` → 둘 다 "경계" 구간이었다.

## 5. 금지

- Kaggle 제출·팀 변경·코드 공개 금지
- 새 경기 생성 금지 (이 작업은 hosted 조회 + 집계뿐)
- 결과를 본 뒤 window·표본 수·임계 변경 금지
- 두 제출의 point score 를 같은 표에 놓고 우열 주장 금지 (상대 pool 미매칭)
- 09-12 window 와 09-16 window 를 같은 시점 값처럼 비교 금지


---

## `proposals/claude/WORK_ORDER_EXP-008_execution.md`

# WORK ORDER (Claude → Codex) — EXP-008 candidate 구현과 사전등록 비교

수신 Codex · 발신 Claude · 2026-09-14 10:45 UTC
카드 `experiments/cards/EXP-008-opening-liquidity.md` sha256 `e0e93652991005514bb37f11cf9c69be6d07739594cfee4760ac8792ff30773a`
상태 **카드 사전등록 완료, BLOCK 없음** · commit `1ff22f8`(사전등록) `0291151`(중복 ID 수정)

1. **무엇을 하는가:** EXP-008 candidate 를 구현하고, 카드가 정한 326셀에서 parent 와 비교한다.
2. **왜 하는가:** "첫날 cash 0 → 다음 날 HIRE 3건 실패" 는 지금 우리가 가진 가장 구체적인 패배 원인인데,
   이를 겨냥한 candidate 가 아직 없다. 카드·계측·pool 은 모두 준비됐다.
3. **무엇을 측정하는가:** 카드의 G1~G5.
4. **막힌 점과 다음 행동:** 막힌 점 없음. 아래 순서대로 실행한다.

---

## 선행 확인 (실행 전 3줄)

```bash
python3 tools/validate_hypotheses.py --strict          # exit 0 이어야 한다
shasum -a 256 experiments/cards/EXP-008-opening-liquidity.md
# e0e93652991005514bb37f11cf9c69be6d07739594cfee4760ac8792ff30773a
python3 tools/verify_pool.py --glob 'private_artifacts/tapes/*-replay.json' \
  --expected-count 47 --expected-sha256 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1
```

세 줄 중 하나라도 어긋나면 실행하지 말고 반송한다.

## 순서 (바꾸지 말 것)

### 1. candidate 구현

`experiments/candidates/exp008_opening_liquidity/main.py`.
`one_change` 는 step 1 opening market schedule **한 블록 전체**를 A → B 로 교체하는 것뿐이다.

```
A = [[BUY_PRODUCT,WHEAT,13],[SELL,WHEAT,13],[BUY_PRODUCT,WHEAT,13]]
B = [[BUY_PRODUCT,WHEAT,13],[BUY_PRODUCT,WHEAT,30],[SELL,WHEAT,30]]
```

`fixed` 는 step 1 farmer/hands, step 2..718 전체 parent action·router·clone-preempt,
`actions.json`·`yh_base.py`, engine 1.32.7, MAX_ORDERS=10. **order 와 batch size 를 따로 쪼개지 말 것.**

### 2. SHA freeze

card · parent tar `1c478c24…9721` · candidate `main.py` · harness 의 SHA-256 을 보고서에 적는다.
이 시점 이후 카드를 수정하면 사전등록이 무효다.

### 3. parent baseline 을 **먼저** 기록

```bash
python3 tools/instrument.py --a tape:<opponent> --b <parent main.py> --seeds <seed> \
  --focus-steps 23 25 47 --include-actions --json evidence/raw/EXP-008/parent/<cell>.json
```

326셀 = target 2 + control 2 + public 40 + pool 282.
셀 키는 `(opponent, seed, candidate seat)`.
전부 모아 `evidence/raw/EXP-008/parent_counters.jsonl` 로 만들고 그 파일의 SHA-256 을 보고서에 적는다.

> **이 단계를 건너뛰거나 candidate 결과를 먼저 열람하면 카드가 무효다.** (카드 §A 판정 절차 1~4)

### 4. candidate 실행

같은 326셀, 같은 명령, `--b <candidate main.py>`.

### 5. 판정

| gate | 판정 |
|---|---|
| G1 | target 2셀 L=0 AND 두 셀 모두 `step23 bank>=4` `step25 hands>=3` `step47 nonempty_tiles>=25` |
| G2 | control 2셀 L=0 |
| G3 | public 40셀 L=0 AND pool 282셀 candidate-only loss c=0 |
| G4 | 326셀 각각 `hire_failed` `buy_failed` `seed_blocked_plant` `shed_discarded` `orders_truncated` 모두 `candidate <= parent` AND `status!=DONE=0` |
| G5 | 326셀 각각 `different_steps == [1]` AND `farmer_or_hands_different_steps == []` |

측정 시점 규약 (카드 §C):
`env.steps[i].action` 은 observation step `i-1` 을 보고 만든 action, `env.steps[i].observation` 은
그 action 을 처리한 **뒤**의 상태. 둘은 같은 transition 이다. **G1 은 결과 상태를, G5 는 그 상태를 만든 action 을 읽는다.**
parent 에 counter 키가 없으면 그 값은 `0` 으로 읽는다.

### 6. 보고

`coordination/reports/codex/YYYYMMDD-HHMM-EXP008-RESULT.md` 한 파일 + 카드 `## 결과` 절 채우기(카드는 Claude 소유이므로
결과 본문은 proposal 로 넘기거나 Claude 에게 요청).
`tools/update_hypotheses.py` 로 HYP-0030 의 `로컬 결과`·`상태` 를 갱신한다.
`experiments/registry.csv` EXP-008 행의 `result` `verdict` `result_path` 갱신은 Claude 가 한다.

## 결과 해석의 상한 — 반드시 지킬 것

- SUCCESS 여도 결론은 **"이 패배 원인을 고쳤다"** 까지다. `[LOCAL]` mechanism support 로만 기록한다.
- **hosted 우위 주장 금지.** 제출은 별도 카드 + 사람 승인이 필요하다.
- G1 은 단일 시드 2셀이고 tape 는 결정론적이라 좌석 교대가 독립 정보를 거의 주지 않는다. **실효 표본 1.**
- G4 통과는 "silent failure 가 없다" 가 아니라 **"늘지 않았다"** 로만 보고한다.
- FAILURE 면 `next_if_failure` 대로 exact B schedule 을 폐기한다. cash-floor 나 order-only 로 쪼개서
  다시 보고하지 않는다. seeds 추가 금지.

VERDICT | 제안 | card `e0e93652…773a` · 326셀 · parent baseline 선기록 필수 | 미실행 | NEXT ACTION: Codex 착수


---

## `proposals/claude/WORK_ORDER_gate_split_and_release_tracking.md`

# WORK ORDER (Claude → Codex) — release gate 분리 · releases/ 추적

수신 Codex (소유 경로 `tools/` `tests/` `releases/`) · 발신 Claude · 2026-09-14 10:45 UTC
상태 **제안, 미착수** · 선행 조건 없음 · EXP-008 실행과 **병행 가능**

1. **무엇을 바꾸는가:** 일반 release gate 가 "요청한 SELL 수량 − 실제 판매량" 을 실패로 세는 것을 멈춘다.
2. **왜 하는가:** 재고 10개에 `SELL n=1000` 을 쓰고 10개를 다 팔아도 990이 실패로 잡힌다.
   이미 `evidence/FACTS.md` F-T7 이 이 값의 98.7% 가 phantom 이고 **창고 미판매는 0** 이라고 판정했는데,
   합격 기준 코드에는 그대로 남아 있다. 이대로면 정상 후보를 떨어뜨리거나 매번 예외 설명으로 통과시킨다.
3. **무엇을 측정하는가:** 아래 §3 의 회귀 테스트.
4. **막힌 점과 다음 행동:** 막힌 점 없음. Codex 가 §1~§4 를 처리하고 보고한다.

---

## §1. `sell_unfilled` 를 합격 조건에서 진단 지표로 강등

대상 `tools/instrument.py` — `Counters.is_clean()` 과 `Counters.gate_reasons()`.

현재 두 함수 모두 `sell_unfilled` 를 합격 조건에 포함한다.

```python
# 현재 (tools/instrument.py)
def is_clean(self) -> bool:
    return (self.noop_actions == 0 and self.shed_discarded == 0
            and self.orders_truncated == 0 and self.sell_unfilled == 0
            and self.buy_failed == 0 and self.hire_failed == 0
            and self.seed_blocked_plant == 0 and self.exceptions == 0)
```

요청: **합격 조건에서 `sell_unfilled` 를 제거**하고, 실손 지표만 남긴다.

| 남길 것 (합격 조건) | 근거 |
|---|---|
| `shed_discarded` | 셰드 100칸 초과로 물건이 실제 소멸 |
| `orders_truncated` | 11번째 주문부터 실제 절삭 |
| `buy_failed` | `_commit_unit` 실패 |
| `hire_failed` | 자금 부족으로 HIRE 무음 실패 |
| `seed_blocked_plant` | 씨앗 부족으로 PLANT 전량 PASS 치환 |
| `exceptions` | 그대로 |
| `noop_actions` | 그대로 (판정 유지 여부는 Codex 판단, 근거를 보고에 적을 것) |

| 강등할 것 (진단 전용) | 근거 |
|---|---|
| `sell_unfilled` | `Σ요청n − 체결`. `evidence/FACTS.md` F-T7 — phantom 98.7%, carried 1.3%, **창고 미판매 0** |

`sell_unfilled` 는 JSON 출력과 `gate_reasons()` 의 **진단 섹션**에는 그대로 남긴다. 값을 지우지 말 것.
실손에 해당하는 `shed_unsold`(에피소드 종료 시 창고에 남은 판매 가능 재고)가 별도 counter 로 없다면
같은 작업에서 추가한다 — 이것이 `sell_unfilled` 가 재려던 실제 손실이다.

## §2. 일반 gate 와 EXP별 gate 의 역할 분리 명시

`tools/instrument.py` 모듈 docstring 또는 `tools/gate_contract.py` 에 아래를 적는다.

- **일반 release gate** — 제출 후보가 실손을 내지 않는지 본다. 절대 0 기준. §1 의 "남길 것".
- **EXP별 gate** — 해당 카드가 정한 기준으로만 판정한다. 절대 0 일 수도, 셀별 non-regression 일 수도 있다.
  일반 gate 가 EXP별 gate 를 덮어쓰지 않는다.

근거: EXP-008 카드 §A 는 다섯 counter 를 `(opponent, seed, candidate seat)` 셀별 `candidate <= parent`
로 확정했다. parent 가 target 셀에서 이미 `hire_failed=9 buy_failed=34 seed_blocked_plant=16` 이라
절대 0 은 구조적으로 도달 불가였기 때문이다. **EXP-008 의 G4 는 이 work order 로 바뀌지 않는다.**

## §3. 회귀 테스트

`tests/` 에 최소 두 건을 추가한다.

1. **sentinel 과다요청이 gate 를 떨어뜨리지 않는다** — 재고 n개에 `SELL n*100` 을 요청해 n개가 모두 체결된
   run 에서 `is_clean()` 이 True. (`sell_unfilled > 0` 이어도 통과)
2. **실손은 여전히 떨어뜨린다** — `shed_discarded > 0` 또는 `hire_failed > 0` 인 run 에서 `is_clean()` 이 False.

기존 `tests/test_gate_contract.py` 의 기대값이 §1 로 바뀌면 그 변경도 같은 커밋에 넣고 보고에 적는다.

## §4. `releases/` 추적 (별건, 작음)

새 checkout 에서 현재 제출물을 복원할 수 있어야 한다. `releases/` 는 Codex 소유라 넘긴다.

```bash
git add releases/public-thomas-replay-router-v2-exact/{main.py,manifest.json,source-metadata.json,source.ipynb,preflight-selfplay.json}
git add releases/public-yhay81-shop-router-0909-exact  # tar.gz 제외
git add releases/v0 releases/v1-20260910               # tar.gz 제외
```

`submission.tar.gz` 는 `.gitignore` 대상 그대로 둔다 (`.gitignore:5,9`). 복원은 **source + manifest + SHA** 로 한다.
`releases/.DS_Store` 는 추적하지 말 것.

Claude 쪽은 이미 처리했다 (commit `64af7d7`): `experiments/cards/EXP-005..008`,
`coordination/proposals/claude/{exp005,exp006,exp007,harness}`, `experiments/registry.csv`
(열 추가 `card_path` `artifact_sha256` `submission_id` `hosted_score`, EXP-006/007/008 행 기록).

## 보고

`coordination/reports/codex/YYYYMMDD-HHMM-GATE-SPLIT.md` 한 파일.
`AGENTS.md` §10.1 형식 — 무엇 / 왜 / 측정과 결과 / 막힌 점과 다음 행동 + VERDICT 줄.
`python3 -m pytest -q tests/` 전체 결과와 변경 파일 SHA-256 을 포함할 것.

VERDICT | 제안 | `tools/instrument.py` `is_clean`/`gate_reasons` · `releases/` 추적 | 미실행 | NEXT ACTION: Codex 착수


---

## `proposals/claude/exp005/BUILD_AND_GATE_PROPOSAL.md`

# 제안 (Claude → Codex) — EXP-005 릴리스 빌드 + 무음 실패 게이트 재정의

카드: `experiments/cards/EXP-005-x1-probe.md`. 이 제안은 소유 경로(`releases/` `tools/`) 밖이므로 Codex 가 구현한다.

## 1. 릴리스 `releases/exp005-x1-probe/` — **보류: EXP-005 판정 FAILURE (2026-09-11). 빌드하지 않는다.**
tar 루트 멤버 4개, 전부 바이트 복사(수정 금지):

| 멤버 | 원천 | sha256 |
|---|---|---|
| main.py | `coordination/proposals/claude/exp005/main.py` | dd41b6df36e5d88f654e428e12929db2ba8dcc9eafaac36a648ca8715348698c |
| yh_base.py | `releases/public-yhay81-shop-router-0909-exact/main.py` 이름만 변경 | d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b |
| actions.json | 같은 폴더 | 17d503f2fd20d59f9c0f14024d1e74a8add8bb9b5561d4d908b45deecb5495ef |
| LICENSE.txt | 같은 폴더 | cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 |

- Identity: 빈 폴더에 tar 해제 → 위 4개 SHA 대조 → 해제 폴더의 main.py 로 h2h seeds 5101..5110 × 양좌석 20판을 다시 돌려 양쪽 최종 뱅크 40개가 `experiments/results/EXP-005/h2h.jsonl` 과 전부 일치 (엔진 결정론 F-T4).
- Isolation: `kaggle_environments.agent.get_last_callable(open(p).read(), path=p)` 로 로드(`__file__` 없음) → vs starter 720 steps DONE.
- Runtime: `harness/sellaudit.py` 출력 `agent_cpu_s ≤ 5.0`, `turn_p99_ms ≤ 5.0`.

## 2. 무음 실패 게이트 재정의 (`tools/instrument.py` `is_clean`)
근거 `evidence/FACTS.md` F-T7: `sell_unfilled = Σn − 체결` 은 n=1000 sentinel 을 손실로 센다 (yhay81 unfilled 의 98.7% 가 어디에도 재고 없는 요청, 창고 미판매 0).

| 현재 | 제안 |
|---|---|
| `sell_unfilled == 0` | `shed_unsold_units == 0` (시장 단계 직전 창고 재고 중 미체결) |
| `shed_discarded == 0` (일말 자동 드롭만) | `discard_units ≤ 10/run` AND `manual_drop_lost_units == 0` (수동 DROP 초과 소멸 — 현재 계측 안 됨) |
| — | `end_units == 0` (종료 시 셰드+인벤토리의 **PRODUCTS** 잔여) + `end_animals` 별도 기록 (미배치 가축 = farm 계획 어긋남 신호) |
| `noop_actions == 0` | 유지하되 no-op 은 진단 (parent 44..136, 이 카드의 one_change 와 무관) |

참조 구현: `coordination/proposals/claude/harness/sellaudit.py` (현재 sha256 8a5f558ccfc9048bd6bbde2c04d2eccc2a775a243c667bce58287b4ad2248fef — end_units 를 PRODUCTS 로 한정한 패치. EXP-005 실행본은 a3143902…).
