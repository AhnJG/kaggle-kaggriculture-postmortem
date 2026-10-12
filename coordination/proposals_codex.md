# coordination/proposals/codex — 31개 문서 묶음

원본 파일을 파일명(시간) 순으로 이어 붙였다. 각 절 제목이 원래 경로다.


---

## `proposals/codex/20260911-CURRENT_RECONCILIATION_AND_AUTORECORD.md`

# 2026-09-11 current-state 통합 제안

상태: **PROPOSAL — Coordinator/Cowork 승인 필요**

첨부 작업지시서의 Commit A를 실제 정본 파일에 적용하기 전, 현재 문서들의 날짜·소유권·증거 경계를 정리한 제안이다. `BOARD.md`와 `HANDOFF_CURRENT.md`는 각각 coordinator/Cowork 소유 또는 직전 작업자 소유이므로 이 파일에서 직접 수정하지 않는다.

## 1. 현재 상태의 우선순위

`BOARD.md`(2026-09-09)보다 최신인 `RESET_2026-09-10.md`와 `evidence/HOSTED_LEDGER.md`(2026-09-10 23:16 UTC)를 현재 판단의 우선 근거로 둔다.

```yaml
as_of: 2026-09-11
status: CONTROL_PLANE_RECONCILIATION_REQUIRED
workspace_gate:
  wp3: DONE
  commit: dbd1673
  commit_a: PENDING_COORDINATOR_APPROVAL
strategy_direction: TAPE_ROUTER_FIRST_RECOMMENDED
active_submissions:
  - id: 56147691
    label: yhay81-exact
    public_score: 2188.4
    status: COMPLETE
    active_slot: INFERRED
  - id: 56145245
    label: v1-20260910
    public_score: 343.9
    status: COMPLETE
    active_slot: INFERRED
next_owner: Coordinator
next_decision: choose_tape_router_before_absorption_experiment
```

`active_slot: INFERRED`는 ledger가 업로드 파일 해시와 활성 슬롯을 완전히 직접 증명하지 않는다고 명시하기 때문이다. 이를 `CONFIRMED`로 바꾸지 않는다.

## 2. 문서별 처리

| 문서 | 제안 처리 |
|---|---|
| `coordination/CURRENT.yaml` | 새로 만들고 위 상태의 단일 기계 판독 source로 사용 |
| `coordination/BOARD.md` | CURRENT의 사람이 읽는 요약으로 갱신. 9/9 이후 제출·WP3·테이프 방향 반영 |
| `coordination/HANDOFF_CURRENT.md` | 9/7 v0 handoff를 archive하고 현재 상태를 가리키도록 교체 |
| `coordination/TASKS.md` | 중복 KAGRI-009는 history로 남기고, workspace repair와 strategy 선택을 새 task로 명시 |
| `AGENTS.md` | live 숫자·점수는 넣지 않음. 자동 기록 규칙만 최소 추가 |
| `RESET_2026-09-10.md` | history로 보존. CURRENT에서 참조 |
| `evidence/HOSTED_LEDGER.md` | 현재 문서의 최신 hosted 수치 source로 유지 |

## 3. 앞으로 자동 기록하는 방법

공용 규칙 파일(`AGENTS.md`)만 수정하는 것으로는 부족하다. `AGENTS.md`는 “누가 언제 어떤 문서를 갱신할지”라는 안정적인 규칙만 담고, 실제 상태는 별도 파일에 기록해야 한다.

권장 구조:

1. `coordination/CURRENT.yaml`: 현재 task, owner, parent, blocker, active submission의 단일 상태
2. `coordination/events/YYYYMMDD.jsonl`: 제출·검증·실패·승인 같은 변경을 append-only로 기록
3. `coordination/reports/<agent>/`: 사람이 읽는 상세 보고
4. `tools/update_current.py`: event를 추가하고 CURRENT의 필수 필드·날짜·owner를 검사
5. CI 또는 작업 종료 checklist: `CURRENT.yaml`과 최신 report가 없으면 실패

즉, **규칙은 AGENTS.md, 현재값은 CURRENT.yaml, 변경 이력은 events/**로 분리한다. 자동화는 “모든 변경을 몰래 기록”하는 방식보다, 각 agent가 작업 종료 시 표준 event를 남기고 validator가 누락을 막는 방식이 안전하다.

## 4. 전략 우선순위 제안

**테이프 라우터를 먼저 추천한다.** 단, 첫 단계는 큰 실험이 아니라 작은 재현 검증이다.

이유:

- hosted 결과에서 우리 규칙형 v1은 **343.9점**, 공개 yhay81 계통은 **2188.4점**이었다. 현재 가장 큰 격차는 흡수량 숫자 하나보다 전체 행동 순서·시장 실행 방식에 있다.
- RESET과 master plan은 상위권이 720턴 행동 테이프와 얇은 안전 가드를 쓴다는 방향으로 이미 전환했다.
- 흡수량 실험은 현재 전략의 일부만 고치는 작업이다. 전략 뼈대가 계속 바뀌면 실험 결과를 버릴 가능성이 높다.
- 테이프 라우터를 먼저 만들면 이후 흡수량 수정은 시장 가드의 한 요소로 재사용할 수 있다.

권장 순서:

1. 공개 리플레이 1개에서 720턴 action을 추출한다.
2. 기록된 최종 bank와 재생 결과가 같은지 확인한다.
3. 재현이 통과한 테이프에만 흡수량·셰드 가드를 하나씩 붙인다.
4. 각 단계에서 `smoke`, `instrument`, paired arena를 통과시킨다.

흡수량 실험을 완전히 버리자는 뜻은 아니다. `harvest_blocked_by_shed`와 `shed_peak` 계측 보강은 테이프 라우터와 독립적이므로 먼저 해도 되지만, EXP-003의 큰 전략 실험은 테이프 재현 기준이 생긴 뒤로 미루는 편이 안전하다.

## 5. Coordinator 승인 시 다음 상태

- `CURRENT.yaml` 생성
- BOARD/HANDOFF/TASKS의 과거 기록은 삭제하지 않고 `SUPERSEDED` 또는 archive 표시
- `strategy_direction`을 `TAPE_ROUTER_FIRST`로 하나만 선택
- EXP-003은 `DEFERRED_UNTIL_TAPE_BASELINE`으로 표시
- 새 hosted 제출·expensive arena는 위 상태 정합화 후 사람 승인 아래 실행


---

## `proposals/codex/20260914-community-trends-plan-update.md`

# 2026-09-14 커뮤니티 동향 4건 반영 제안

상태: **PROPOSAL ONLY** — `plan/`·`experiments/cards/`는 Claude 소유다. `HYPOTHESES.md`는
`tools/update_hypotheses.py`로만 갱신한다. 이 문서는 owner가 그대로 적용·반송할 수 있는 work order다.

## 2026-09-15 정정 — R10 신호와 source/우리 설계의 경계

이전의 **‘수확 가능한 MELON signal’ 설명은 폐기**한다. `[ENGINE]` 1.32.7에서 MELON은
심을 때 `yield_units=1`이며 HARVEST는 crop age가 `first_yield_day=10`보다 작으면 실행하지 않는다.
`[COMMUNITY source]` R10 cell 2:1135–1144는 age를 검사하지 않고 상대 MELON의 `yield_units`만 합산한다.
같은 cell :1152–1162는 현재 shed의 MELON을 추가 SELL한다. **next-turn shift/repay는 우리 별도
`[HYPOTHESIS]`이며 R10의 동작이나 검증 결과가 아니다.** maturity를 조건으로 쓰려면 별도 정의·검증이 필요하다.

정정 근거: `environment/ENGINE_LOCK.md`; 고정 `kaggriculture.py:16,215–225,449–462`, SHA
`bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`; R10 source SHA
`808210418de2cc24d1df643855c8055eeaceb1b0e442dc978e8007b195ddb9e7` (URL·수집일은 §1.2).
재현: 아래 SHA가 ENGINE_LOCK의 값과 같은지 확인하고 source 조건을 읽는다(게임 실행 없음).

```bash
shasum -a 256 .venv/lib/python*/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py
rg -n '"MELON"|yield_units|first_yield_day|planted_day' .venv/lib/python*/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py
```

[독립 판정](../../reports/codex/20260915-independent-review.md) F3 참고. HYP-0031~0033·EXP-009/010은
**등록·승인되지 않은 초안 이름**이다. 아래 09-14 validator BLOCKED와 master plan 수정 순서는 당시 기록이다.
09-15에는 strict validator가 PASS이고 EXP-008은 FAILURE로 종결됐다. 현재 작업 순서는
[plan/CURRENT.md](../../../plan/CURRENT.md)를 따른다. 이 정정은 전략 구현·제출 승인이 아니다.

## 비전공자용 요약

1. **무엇을 바꾸거나 시험하는가:** 이미 구현된 clone preemption은 유지하고, 상대 밭 MELON의 **공개 yield_units**를
   보고 우리 MELON 판매를 앞당기는 별도 실험을 제안한다. 가축 아사 방지는 우리 artifact에서도 같은 실패가
   있는지 먼저 찾는다. FERTILIZER 판매를 막는 guard는 추가하지 않는다.
2. **왜 하는가:** 네 주장 중 둘은 새 가설 후보지만, clone preemption은 이미 `EXP-006`에 있고
   FERTILIZER 무음 실패는 현재 엔진이 아니라 구버전 `1.29.3` 현상이다. 서로 다른 문제를 한 카드에 섞으면
   원인을 판정할 수 없다.
3. **측정과 결과:** `[ENGINE+LOCAL]` `1.32.7`에서 FERTILIZER 1개를 100에 사서 다음 step에 100에 팔면
   bank `3000→2900→3000`, shed `0→1→0`, market inventory `10000→9999→10000`으로 정상 동작했다.
   `[LOCAL]` 새 strategy candidate는 아직 만들거나 실행하지 않았다(`N/A`).
4. **막힌 점과 다음 행동:** `EXP-008` card가 같은 `hypothesis_id`와 `test_id`를 두 번 적어 strict validator가
   실패한다. 또 새 Market Preemption은 현재 parent의 관련 패배 postmortem과 exact R10 opponent가 없고,
   animal guard는 우리 parent에서 실제 아사가 확인되지 않았다. owner가 이 세 gate를 해소하기 전에는 card를
   canonical로 만들거나 candidate를 실행하지 않는다.

VERDICT | **제안만 작성** — standing-MELON 반응과 animal survival의 source claim 등록 제안, clone은 기존 실험 유지, FERTILIZER 차단 guard는 기각 | exact source SHA와 parent SHA 아래 기록 | engine canary PASS, strategy run N/A | NEXT ACTION: validator 복구 → owner가 HYP/card 제안 수락 또는 BLOCKED 반환

---

## 1. 증거 대조 결과

| 입력 주장 | 판정 | 현재 반영 | 필요한 변경 |
|---|---|---|---|
| 상대 standing-MELON 관측 기반 Market Preemption | **부분 지지 `[COMMUNITY]`** | `HYP-0016`은 일반 1-step sale timing, `HYP-0006`은 near-clone next-turn sale을 다룬다. 상대 standing-MELON signal 자체는 미등록 | `HYP-0031` source claim 추가. `EXP-009`는 별도 one-factor card로만 제안 |
| public clone counter | **이미 반영** | `HYP-0006` / `EXP-006`, local SUCCESS, hosted causal effect `INCONCLUSIVE` | 새 HYP-ID를 만들지 않는다. `EXP-009`에서 EXP-006 clone layer는 fixed로 둔다 |
| day-1 cow starvation | **새 source claim `[COMMUNITY]`** | `HYP-0030` / `EXP-008`은 cash starvation→HIRE failure이며 animal starvation과 다른 failure plane | `HYP-0032` 추가. 우리 parent에서 `animal_starved>=1`인 loss를 찾기 전 `EXP-010` BLOCKED |
| FERTILIZER resale silent failure | **현재 엔진에는 부적용** | `1.32.7` engine과 기존 local runs는 FERTILIZER SELL을 처리 | `HYP-0033`에 version boundary 기록. 차단 guard 대신 engine canary + `fertilizer_sell_failed` counter만 추가 |

### 1.1 Source fact와 과장 방지

- `[COMMUNITY]` Adaptive Land Allocator R10 최종 code는 상대 farm의 MELON tile 중
  `yield_units` 합이 0보다 크고, 현재 MELON SELL이 없고, day < 29일 때 own shed MELON을 최대 10개 판다.
  이것은 **상대 standing-MELON의 yield_units signal**이다. 수확 readiness나 다음-turn SELL을 검사하지 않는다.
  R10은 현재 shed에서 추가 SELL하며, 아래 next-turn shift/repay는 우리 별도 설계 가설이다.
  notebook의 실행 확인은 `pass` 상대 seeds `1,2,3` × both seats뿐이다. 경쟁 승률·hosted artifact는 `N/A`.
- `[COMMUNITY]` boatlee V14는 clone distance `<=6`, step `120..679`, premium four products,
  next-turn quantity `>=4`, shift cap `30`으로 shift/repay를 수행한다. source artifact는 engine `1.32.6`이다.
  우리 `EXP-006`은 이 아이디어를 engine `1.32.7`에서 exact parent와 다시 검증했으나 parent가 hosted에서
  은퇴해 causal hosted effect는 여전히 `INCONCLUSIVE`다.
- `[COMMUNITY]` cow report는 v40의 local loss 4개 중 3개에서 day-1 cow 2마리 소실,
  patched v40 vs v41 `23-7`, 11 public agents `156-62-2`를 자기보고한다. 우리 artifact 결과가 아니다.
- `[ENGINE]` animal은 `consecutive_unfed >= 2`이면 structure만 남고 사라진다
  (`kaggriculture.py:_daily_refresh_animals`, current source lines 805-833).
- `[COMMUNITY]` FERTILIZER 글은 실패가 notebook engine `1.29.3`, 정상 동작이 local `1.32.7`이라고
  후속 댓글에서 직접 구분한다. `[ENGINE]` current `1.32.7`의 `_process_market`은 SELL item을 모든
  `PRODUCTS`에 허용하고 `_commit_unit`이 shed에서 차감하고 bank를 늘린다(lines 596-660).

### 1.2 출처와 수집 경계

| 자료 | URL | 수집일 | engine | local SHA-256 |
|---|---|---|---|---|
| Adaptive Land Allocator R10 | https://www.kaggle.com/code/xuantianfengwu/kaggriculture-adaptive-land-allocator-r10 | 2026-09-14 | source pins 1.32.7 | `808210418de2cc24d1df643855c8055eeaceb1b0e442dc978e8007b195ddb9e7` |
| V14 Clone Preemption | https://www.kaggle.com/code/boatlee/84-84-base-public-holdout-v14-clone-preemption | 2026-09-14 | 1.32.6 | `9ab82fd86a9f3be300ec4ee2ae2a6a9bdabc5a1232926ed57a5e3b645dda11e0` |
| Replay Forensics cow bug | https://www.kaggle.com/competitions/kaggriculture/discussion/741235 | 2026-09-14 | N/A | `5c3fc283577fe31a629366bb3d44c069b13014a2da83759e432240576b6ec513` |
| Selling fertilizer | https://www.kaggle.com/competitions/kaggriculture/discussion/740650 | 2026-09-14 | failure 1.29.3 / success 1.32.7 | `5f9ee30c3f95db44407d6c461e9d5b28fe442db0fc7bf86458c4ca9e794848ca` |

---

## 2. `HYPOTHESES.md` 변경안

### 2.1 먼저 고칠 validator blocker

`experiments/cards/EXP-008-opening-liquidity.md`는 lines 3-4와 fenced YAML lines 19-20에 같은
`hypothesis_id` / `test_id`가 중복된다. Claude owner가 **상단 lines 3-4를 유지하고 YAML 내부 두 줄만 제거**한다.

수정 후:

```bash
python3 tools/validate_hypotheses.py --strict
# expected: exit 0
```

현재 실제 결과는 exit `3`이며 다음 세 오류다.

```text
EXP-008-opening-liquidity.md: multiple hypothesis_id fields
EXP-008-opening-liquidity.md: multiple test_id fields
EXP-008-opening-liquidity.md: duplicate TEST-0008; already used by the same card
```

### 2.2 신규 entry 3건

아래 entry는 직접 붙여넣지 말고 updater로 만든다. 현재 next IDs를 `HYP-0031..0033`으로 예약했지만,
적용 시 이미 사용 중이면 updater가 다음 free ID를 할당하고 card pointer도 함께 바꾼다.

#### HYP-0031 — standing-MELON 반응 초안 (미등록)

```text
쉬운 설명=상대 밭의 MELON 수량 신호에 반응해 판매를 바꾸는 아이디어다. 아직 익었는지 또는 다음에 팔지는 이 신호만으로 알 수 없다.
주장=R10 source는 상대 MELON tile의 yield_units 합이 1 이상일 때 조건에 따라 현재 shed의 MELON을 최대 10개 추가 SELL한다. next-turn 예정 SELL을 shift/repay하여 우리 W/D/L을 높이는 것은 별도 미검증 설계 가설이다.
출처 수준=COMMUNITY,HYPOTHESIS
출처=docs/code/xuantianfengwu_kaggriculture-adaptive-land-allocator-r10.ipynb sha256 80821041…ddb9e7; https://www.kaggle.com/code/xuantianfengwu/kaggriculture-adaptive-land-allocator-r10; 수집 2026-09-14
엔진=source pins 1.32.7; 우리 검증 engine 1.32.7
실험=coordination/proposals/codex/20260914-community-trends-plan-update.md EXP-009 draft; canonical card N/A — BLOCKED
로컬 결과=N/A — source notebook은 pass 상대 seeds 1,2,3 both seats DONE만 확인하며 경쟁 비교가 아님
Hosted 결과=N/A
상태=SOURCE_CLAIM
유효 범위=R10 standing-MELON signal 기반 추가 SELL의 source 판독; 수확 readiness·next-turn 예측·shift/repay 효과·MILK 일반화는 증명되지 않음
다음 행동=R10 exact artifact와 license를 freeze하고, current parent의 관련 loss postmortem을 확보한 뒤 EXP-009를 owner가 수락
```

#### HYP-0032 — opening animal survival guard

```text
쉬운 설명=첫 이틀에 굶을 위험이 있는 가축에게 먹이를 우선하면 농장 전체가 무너지는 큰 패배를 막을 수 있는지 확인한다.
주장=day 1에 consecutive_unfed=1인 animal을 우선 FEED하는 bounded guard는 해당 animal 소실과 그 뒤의 큰 패배를 줄인다.
출처 수준=COMMUNITY,ENGINE,HYPOTHESIS
출처=docs/discussion/741235_Replay_Forensics_The_64K_Bug_in_v40__Patched_Agent.md sha256 5c3fc283…6ec513; https://www.kaggle.com/competitions/kaggriculture/discussion/741235; 수집 2026-09-14; engine condition kaggriculture.py:805-833
엔진=community artifact N/A; current condition checked on 1.32.7
실험=coordination/proposals/codex/20260914-community-trends-plan-update.md EXP-010 draft; canonical card N/A — BLOCKED
로컬 결과=N/A — report의 23-7와 156-62-2는 저자 자기보고이며 우리 artifact 재현이 아님
Hosted 결과=N/A
상태=SOURCE_CLAIM
유효 범위=source v40 patch claim과 current engine starvation condition; EXP-006/007에 동일 failure가 있다는 뜻이 아님
다음 행동=recent hosted와 fixed 47-tape pool에서 parent loss 중 animal_starved>=1인 exact cell을 먼저 찾고 postmortem
```

#### HYP-0033 — FERTILIZER resale version boundary

```text
쉬운 설명=비료 판매 실패는 현재 게임 전체의 규칙이 아니라 구버전에서만 보고된 차이인지 확인한다.
주장=고정 engine 1.32.7에서는 shed의 FERTILIZER를 SELL하면 수량이 줄고 bank가 증가하므로 FERTILIZER SELL 차단 guard를 두지 않는다.
출처 수준=COMMUNITY,ENGINE,LOCAL
출처=docs/discussion/740650_Selling_fertilizer.md sha256 5f9ee30c…848ca; https://www.kaggle.com/competitions/kaggriculture/discussion/740650; 수집 2026-09-14; kaggriculture.py:596-660
엔진=1.32.7; discussion failure 1.29.3
실험=engine canary BUY_PRODUCT FERTILIZER 1 at step 0 -> SELL FERTILIZER 1 at step 1, seed 7, episodeSteps 4
로컬 결과=bank 3000→2900→3000, shed 0→1→0, market inventory 10000→9999→10000, price 100; PASS
Hosted 결과=N/A
상태=ENGINE_CONFIRMED
유효 범위=local shipped engine 1.32.7; hosted module_version이 다르면 N/A로 되돌리고 canary 재실행
다음 행동=tests에 engine canary를 고정하고 instrument에 fertilizer_sell_failed counter를 추가하되 runtime SELL 차단은 하지 않음
```

### 2.3 기존 entry 처리

- `HYP-0006`: 변경 없음. source를 추가하려면 V14 notebook URL·수집일·engine `1.32.6`을 덧붙이되
  상태 `INCONCLUSIVE`와 exact hosted 한계를 유지한다.
- `HYP-0016`: `HYP-0031`과 합치지 않는다. `HYP-0016`은 sale timing 전체, `HYP-0031`은
  standing-MELON signal 기반 source claim과 별도 shift/repay 가설을 구분하는 초안이다.
- `HYP-0030`: animal starvation 문구를 넣지 않는다. 이것은 opening cash/HIRE failure 전용이다.

---

## 3. Master plan 수정안

대상 정본: `plan/kaggriculture_master_plan_claude-opus-5.md`.

1. 제목을 `마스터 플랜 v3 (2026-09-14 current-state reconciliation)`로 갱신한다.
2. §0/§1의 과거 “첫 제출 v0를 지금 한다”와 09-06 기준 snapshot을 제거하고 다음 current state로 교체한다.
   - active: EXP-006 `56165718` score snapshot `1915.6`, EXP-007 `56175620` `1819.8` (`[HOSTED]`, 2026-09-12 사람 제공)
   - provisional incumbent: EXP-006; clone-preempt causal effect `INCONCLUSIVE`
   - current priority: EXP-008 opening liquidity candidate 구현·freeze·326-cell test
3. §2.5의 “rank 3–20 99~100% 동일”, “핵심 meta 확인” 같은 외부 수치는 artifact/URL/date/engine이
   없으면 `[COMMUNITY]`로 내린다. `[HOSTED]` label은 우리 submission/episode와 연결된 값만 유지한다.
4. §3.2/§3.4의 broad market-layer rollout을 다음 순서로 바꾼다.
   - replay-derived backbone 유지
   - one factor bounded branch
   - normal-state parent parity
   - target/control/public/pool both-seat test
   - local success는 hosted promotion이 아님
5. §3.4에 두 preemption을 분리한다.
   - **near-clone next-turn shift**: implemented/tested in EXP-006; fixed baseline, not a new claim
   - **standing-MELON 추가 SELL**: R10 source claim. HYP-0031/EXP-009의 shift/repay는 별도 미검증 설계이며 readiness를 보장하지 않음
6. §3.5 FERTILIZER 문단에 “SELL silent failure는 1.29.3 report이며 1.32.7에서 정상”을 추가한다.
   기존 판매 경제 가설과 engine action legality를 분리한다.
7. §6의 달력형 계획을 다음 dependency order로 교체한다.
   - P0 EXP-008 validator fix → candidate test
   - P1 latest public-opponent refresh + relevant loss postmortem
   - P2 EXP-009 standing-MELON 반응 가설, source/우리 설계를 분리하고 gates 충족 시에만
   - P3 animal-starvation census; parent failure가 확인될 때만 EXP-010
   - P4 engine FERTILIZER canary는 regression test로 유지, strategy slot을 소비하지 않음
8. `plan/kaggriculture_docs_insights_claude-opus-5.md`에는 2026-09-14 appendix를 추가해 source 네 건의
   URL/date/engine/SHA와 위 evidence boundary를 남긴다. 과거 본문을 조용히 덮어쓰지 않는다.

---

## 4. 신규 card draft

### 4.1 `EXP-009-visible-ready-melon-preempt.md` — 역사적 초안 이름; readiness 의미는 폐기

상태: **BLOCKED** — (B1) current parent의 relevant public-opponent loss postmortem 없음,
(B2) R10 exact opponent artifact·license·SHA 없음. 둘 중 하나라도 미해결이면 owner는 canonical card를 만들지 않는다.

```yaml
id:            EXP-009
hypothesis_id: HYP-0031
test_id:       TEST-0009
parent:        coordination/proposals/claude/exp006/submission.tar.gz  # sha256 1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721
candidate:     experiments/candidates/exp009_visible_ready_melon/submission.tar.gz  # 구현 전 SHA N/A; 실행 전 freeze
one_change:    EXP-006의 preempt trigger A -> B;
               A = clone_distance<=6에서만 next-turn premium SELL shift;
               B = A에 다음 조건을 OR로 추가: 120<=step<680, rival MELON tile yield_units 합>=1,
               current action에 MELON SELL 없음, next-turn baseline MELON SELL>=4일 때
               MELON만 min(projected_shed, next-turn planned MELON-due, 10) shift하고 step+1에서 같은 수량 repay
fixed:         [EXP-006 actions.json·yh_base.py·clone_distance<=6 branch, farmer/hands, route, BUY/HIRE/BUY_LAND,
                non-MELON market orders, terminal liquidation, maxMarketOrdersPerTurn=10, engine 1.32.7]
hypothesis:    community R10은 rival MELON yield_units 합만 보아 own shed MELON 최대 10개를 추가 SELL한다.
               수확 readiness 검사가 없으며 B의 next-turn shift/repay는 우리 미검증 설계다.
               AGENTS.md §7.3용 current-parent public loss postmortem은 N/A이므로 B1 해소 전 실행 BLOCKED.
opponents:     target = opponents/public/xuantianfengwu_r10.py  # exact extraction·license·SHA N/A -> B2
               clone = releases/public-yhay81-shop-router-0909-exact/main.py  # sha256 40d2bc3986f4ed3e927c81842d399a58bf20b07b57858355da4b75c280fd7791
               public = boatlee f029fa0c…d19 · kaitofukami f48c2116…c7b8 · lynnsakurai 1dc166ae…a7d4 · raykkretzschmar 489f5d19…bdb
               pool = private_artifacts/tapes/*-replay.json 47개, pool hash 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1
seeds:         target [6101..6110] / clone [5201..5210] / public [5101..5105] / pool [5101,5102,5103]
seats:         both
metric:        G0 four engine fixtures trigger·repay·quantity conservation·control parity;
               G1 target 20셀 McNemar b(candidate only win)·c(parent only win)와 trigger cell 수;
               G2 clone h2h 20셀 W/D/L; G3 public 40셀 L과 pool 282셀 b·c;
               G4 cell별 hire_failed·buy_failed·seed_blocked_plant·shed_discarded·orders_truncated·status;
               G5 farmer/hands byte parity와 허용 market diff/repay ledger
success:       G0 4/4 PASS AND G1 b>=1 AND c=0 AND trigger_cells>=1
               AND G2 W>=18 AND L=0 AND G3 public_L=0 AND pool_c=0
               AND G4 모든 셀에서 candidate counter<=parent counter AND status_not_DONE=0
               AND G5 farmer_hands_diff_steps=0 AND quantity_conservation_error_units=0 AND unpaid_due_units=0
failure:       G0_pass<=3 OR G1 c>=1 OR G2 L>=1 OR G3 public_L>=1 OR pool_c>=1
               OR G4 위반 셀>=1 OR status_not_DONE>=1 OR G5 위반>=1
inconclusive:  G0·G2·G3·G4·G5 통과 AND G1 b=0 AND c=0; seeds 추가 금지
next_if_success: HYP-0031을 LOCAL_SUPPORTED로만 갱신; 사람 승인 없는 submit 금지; hosted test는 새 card
next_if_failure: 해당 standing-MELON shift 가설의 구체 branch 폐기; clone branch EXP-006 유지; source claim 일반화 금지
artifact:      card·candidate·target opponent·harness SHA와 raw JSONL을 evidence/raw/EXP-009/manifest.json에 freeze
```

### 4.2 `EXP-010-opening-animal-survival.md`

상태: **BLOCKED** — 우리 parent의 loss에서 `animal_starved>=1`인 exact target cell이 아직 없다.
아래 preflight가 0이면 card를 만들지 않고 HYP-0032를 `SOURCE_CLAIM`으로 유지한다.

Preflight 숫자 gate:

```text
scope = EXP-006 recent hosted loss replays + fixed 47-tape pool loss cells
required_target_count >= 1
required fields = opponent artifact/tape SHA, seed, seat, first starvation step, animal type, parent final W/D/L
if target_count = 0 -> BLOCKED, no candidate
```

target가 생긴 경우에만 다음 card를 수락한다.

```yaml
id:            EXP-010
hypothesis_id: HYP-0032
test_id:       TEST-0010
parent:        coordination/proposals/claude/exp006/submission.tar.gz  # sha256 1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721
candidate:     experiments/candidates/exp010_opening_animal_survival/submission.tar.gz  # 구현 전 SHA N/A; 실행 전 freeze
one_change:    steps 24..46에서 consecutive_unfed=1 AND fed_today=false인 animal이 있으면,
               own WHEAT>=1을 든 unit 중 Manhattan distance 최소(unit index tie-break)를 1개 골라
               x축 우선으로 해당 tile까지 이동시키고 도착 시 FEED로 base farmer/hands action을 override;
               at-risk animal은 (y,x) 순서로 1개만 처리, 조건 불충족이면 parent action 그대로
fixed:         [EXP-006 market 전체·clone preemption·route tape, steps 0..23와 47..718 전체 action,
                animal 구매·배치, HIRE/BUY/BUY_LAND, order cap, engine 1.32.7]
hypothesis:    community v40 postmortem은 day-1 FEED 누락으로 cow 2마리가 사라진 반복 loss를 보고했다.
               우리 parent target postmortem path·SHA·seed·seat는 preflight 전 N/A이므로 실행 BLOCKED.
opponents:     target = preflight에서 freeze한 parent-loss opponent 1개 이상;
               public = EXP-006 public 4봇 exact SHA;
               pool = private_artifacts/tapes/*-replay.json 47개, pool hash 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1
seeds:         target = preflight exact seeds; public [5101..5105] / pool [5101,5102,5103]
seats:         both
metric:        G1 target별 animal_starved·W/D/L·first divergence step;
               G2 public 40셀 L과 pool 282셀 McNemar b·c;
               G3 action parity: market byte-identical, guard 밖 farmer/hands byte-identical, changed_units_per_step;
               G4 hire_failed·buy_failed·seed_blocked_plant·shed_discarded·orders_truncated·status
success:       target_count>=1 AND 모든 target에서 parent_animal_starved>=1 AND candidate_animal_starved=0
               AND target_candidate_L=0 AND public_L=0 AND pool_c=0
               AND market_diff_steps=0 AND guard_outside_diff_steps=0 AND max_changed_units_per_step<=1
               AND 모든 G4 counter가 셀별 candidate<=parent AND status_not_DONE=0
failure:       target_count=0 OR candidate_animal_starved>=1 OR target_candidate_L>=1 OR public_L>=1 OR pool_c>=1
               OR market_diff_steps>=1 OR guard_outside_diff_steps>=1 OR max_changed_units_per_step>=2
               OR G4 위반 셀>=1 OR status_not_DONE>=1
inconclusive:  target_count>=1 AND candidate_animal_starved=0 AND target_candidate_L=0이나 G2~G4 중 success도 failure도 아닌 경우; seeds 추가 금지
next_if_success: HYP-0032를 LOCAL_SUPPORTED로만 갱신; EXP-008 cash/HIRE 결과와 합치지 않고 별도 hosted card 검토
next_if_failure: exact rescue controller 폐기; broad animal-survival 가설은 SOURCE_CLAIM 유지
artifact:      preflight target manifest + card·candidate·harness SHA + evidence/raw/EXP-010/*.jsonl
```

### 4.3 FERTILIZER는 EXP card가 아니라 engine contract test

Codex 소유 `tests/`와 `tools/` 변경은 별도 implementation task로 한다.

- `tests/test_engine_fertilizer_sell.py`: seed 7, `episodeSteps=4`, step0 BUY 1, step1 SELL 1,
  expected bank/shed/inventory tuple을 exact assert.
- `tools/instrument.py`: `fertilizer_sell_attempted`, `fertilizer_sell_committed`,
  `fertilizer_sell_failed`를 engine hook에서 집계한다.
- acceptance: `attempted=1`, `committed=1`, `failed=0`; engine lock mismatch면 test exit non-zero.
- runtime agent에서 FERTILIZER SELL을 제거하거나 PASS로 바꾸는 guard는 **금지**한다.

---

## 5. 적용 순서와 owner

1. **Claude** — `EXP-008` duplicate ID 두 줄 삭제, strict validator exit 0.
2. **Codex updater** — HYP-0031..0033 event 기록. 새 IDs가 선점됐으면 자동 배정 후 이 문서/card pointer 교정.
3. **Claude** — canonical master plan v3 update; EXP-009/010은 BLOCK 조건을 그대로 적고 미해소 시 실행 금지.
4. **Gemini** — R10 exact opponent extraction, URL/author/license/collection date/engine 기록. `opponents/` writer 계약 준수.
5. **Codex** — FERTILIZER engine test/counter 구현. EXP-009/010은 canonical card와 target freeze 뒤에만 구현.

Commit order:

1. `fix(exp008-card): remove duplicate ledger identifiers`
2. `docs(hypotheses): register community preemption survival and fertilizer engine boundary`
3. `docs(plan): reconcile v3 priorities and evidence boundaries`
4. `test(engine): lock fertilizer resale behavior`
5. `experiment(exp009|exp010): preregister only after blocked gates clear`

## 6. Acceptance criteria

- `python3 tools/validate_hypotheses.py --strict` exit `0`.
- 각 `[COMMUNITY]` entry에 URL·수집일·engine 또는 `N/A`가 있다.
- EXP-009는 clone logic과 standing-MELON 반응을 같은 새 factor로 주장하지 않는다. clone은 fixed다.
- EXP-010은 `animal_starved>=1`인 우리 parent loss postmortem 없이는 canonical/실행되지 않는다.
- FERTILIZER action은 `1.32.7`에서 차단하지 않는다.
- 모든 card는 exact parent SHA, fixed seeds, both seats, numeric success/failure/inconclusive, next action을 가진다.
- local 결과를 hosted 우위로 쓰지 않는다.

## 7. Owner에게 전달할 copyable prompt

```text
coordination/proposals/codex/20260914-community-trends-plan-update.md를 검토해 주세요.
먼저 EXP-008 card의 duplicate hypothesis_id/test_id를 제거해 strict validator를 복구하세요.
그 뒤 HYP-0031..0033과 master plan v3 수정안을 evidence boundary 그대로 반영하세요.
EXP-009는 relevant parent-loss postmortem과 exact R10 opponent SHA/license가 없으면 BLOCKED,
EXP-010은 우리 parent의 animal_starved>=1 target이 없으면 BLOCKED로 반환하세요.
FERTILIZER는 engine 1.32.7에서 정상 SELL되므로 runtime 차단 guard를 만들지 마세요.
수락·반송 결과에 exact path, SHA-256, 실행한 validator command와 exit code를 남겨 주세요.
```


---

## `proposals/codex/20260915-owner-record-sync.md`

# Claude owner에게 — 완료 결과와 현재 원장 동기화

2026-09-15 KST · Codex. **문서 반영 작업만 요청한다. EXP-008 재실행 금지.**
사람이 Codex에 BOARD·마감 계획 갱신을 맡겼다. `plan/CURRENT.md`가 새 계획을 가리키며 BOARD·HANDOFF는 갱신했다.
아래는 Claude 소유 evidence·registry에 필요한 최소 반영이다. 이번 세션은 해당 파일을 직접 수정하지 않았다.

1. **EXP-008 결과 반영:** `coordination/reports/codex/20260914-2025-EXP008-RESULT.md`와 `evidence/raw/EXP-008/verdict.json`을 읽는다. verdict SHA `9e8cabf4020607abf193ded71071807a8bc9165cba2a95c03180c8a291622d43`; candidate main SHA `930ed160a1696ca9118b2f6704112a181e528bf2c7c9fafac5db76518f87f079`. 326셀 완료, target `0/0/2`, control `2/0/0`, public `40/0/0`, pool 새 패배 2셀, G1/G3/G4/G5 FAIL, G2 PASS. **FAILURE, exact B 폐기**.
2. **Frozen card 보존:** 실행 당시 `EXP-008-opening-liquidity.md` SHA `e0e93652991005514bb37f11cf9c69be6d07739594cfee4760ac8792ff30773a`는 verdict에 고정돼 있다. 본문 ‘미실행’을 조용히 덮어쓰지 않는다. 별도 dated 결과 문서와 registry 포인터를 사용하거나, 카드 snapshot을 먼저 보존하고 결과 후 append임을 분명히 구분한다. 사전등록 수치·조건을 변경하지 않는다.
3. **registry 현재 행:** EXP-008의 `code_sha`, `n`, `result`, `verdict`, `next_action`, `result_path`를 위 결과로 갱신. `artifact_sha256`에 card SHA를 제출 tar SHA처럼 쓰지 않는다. candidate tar는 미생성이므로 N/A, source는 `code_sha`로 구분한다. EXP-006/007 hosted_score는 아래 직접 snapshot을 날짜와 함께 갱신한다.
4. **HOSTED_LEDGER append:** [직접 수집 snapshot](../../reports/codex/20260915-0115-KAGGLE-SNAPSHOT.md)을 출처로 `56165718 COMPLETE 1862.6`, `56175620 COMPLETE 1635.9`, Sian 1,724위, 활성 UI 2개 확인을 추가한다. CLI 시각은 09-15 01:13:12 KST 이전 본 세션 조회로만 확정. 새 episode W/D/L은 N/A. 과거 점수 행을 지우지 않는다.
5. **FACTS 최소 정정:** 새 snapshot 출처를 추가하고, 서두의 ‘무승부 시 먼저 제출한 쪽 승자’를 **최종 동점 규정**으로 구분한다. 게임 draw는 draw다. 서두 ‘final BT 범위 불일치’는 이미 F-T12가 재확인한 Staff 답변과 이번 직접 원문 확인으로 연결한다. 새 engine fact를 이번에 발견한 것처럼 기록하지 않는다.
6. **자기 TASKS 문구:** TEST-0008의 candidate 미구현·미실행과 REVIEW 작업의 Codex 착수 대기를 완료 보고로 연결한다. 타인의 옛 행을 일괄 수정하지 않는다.

수락 조건: result·registry·ledger의 current 포인터가 위와 일치하고, 과거 측정 source SHA를 보존하며, `python3 tools/validate_hypotheses.py --strict` exit 0. 가설 원장의 HYP-0006/0007/0030은 이번 Codex updater event에서 최신 snapshot·다음 행동을 갱신하므로 직접 편집하지 않는다.

권장 순서: 결과 문서·registry → hosted/FACTS append 및 정정 → 자기 TASKS → strict 검증 → 자기 report·commit. 기존 dirty `evidence/FACTS.md`는 owner 자신의 변경을 확인하며 반영한다.

복사용 지시:

> 이 proposal의 1~6만 적용하세요. BOARD와 plan/CURRENT.md는 이미 갱신됐습니다. EXP-008 사전등록 gate를 바꾸거나 전략 실험을 다시 돌리지 말고, frozen card SHA와 현재 실행 결과의 경계를 보존해 결과·원장만 연결하세요. 완료 후 strict validator와 변경 파일을 보고하세요.


---

## `proposals/codex/20260916-TOP10-IMITATION-PLAN.md`

# 상위권 replay 활용 — 답변 검토와 실행계획 제안

작성: Codex, 2026-09-16 22:10 KST. 범위: 검토·계획. 후보 구현·대전·다운로드·제출은 실행하지 않았다.

**판정: 추진 가치가 있는 가설이다. 다만 ‘top 10의 tape를 복사하면 비슷한 점수가 나온다’는 근거는 없다. 최신 donor의 일관된 행동 묶음을 확보하고, 원래 경기 재현과 새 상황 성능을 따로 검증하는 경로를 권한다.**

1. 무엇: 강한 공개 replay에서 반복되는 build order와 상태별 결정을 가져오는 후보를 설계한다.
2. 이유: 공개 notebook 저자의 이름이나 현재 순위보다, 실제 episode의 행동·당시 submission·관측 상태가 더 직접적인 자료다.
3. 이번 측정: 기존 pool 47개와 SHA 일치, ymg_aq 6개·Mengfei Li 6개 존재, CSV 9,234팀·Sian 2,005위/1726.6·923위 2442.5 확인. 새 후보 성능·rating 예상은 N/A.
4. blocker: BOARD에 오늘 P1b FAIL과 새 hosted snapshot 반영 필요. 현재 계획 §5.2는 새 전략 착수를 HOLD한다. K3의 재검토 조건도 비어 있다. 아래는 owner가 채택할 조건부 실행안이며 승인된 실험 카드가 아니다.

## 1. Claude 답변에서 유지할 것과 고칠 것

| 주장 | 검토 결과 | 계획에 미치는 영향 |
|---|---|---|
| 공개 replay를 학습 자료로 활용 가능 | 저장된 공식 rules §2.6/§2.11과 Daily Top Episodes 본문은 사용 가능성을 뒷받침한다. 공개 여부·license·winner obligation은 각각 확인한다. 실시간 웹 본문은 이번 fetch에서 비어 최신 문구/공식 작성자 확인은 N/A | 수집·출처 확인부터 시작 가능. 평가 중 네트워크는 금지 |
| 저자 점수와 복사본 점수 차이가 공개 버전을 일부러 약하게 만든 증거 | **성립하지 않는다.** 팀 순위는 특정 notebook artifact의 강도가 아니며, 제출 age·상대군·두 활성 슬롯·버전이 다르다. F-T18은 09-16 저자 점수와 09-15 EXP-007 점수까지 섞었다 | F-T18의 ‘실제 제출물이 아니다/복사 상한이 낮다’를 [INFERENCE]로 정정 제안. 의도는 N/A |
| 70% 행동 재현이면 약 2100 rating | **근거 없음.** 일치율·bank·W/D/L·Bradley–Terry rating은 서로 다른 양이다. 한 번의 중요한 HIRE 실패가 수백 턴을 망칠 수 있다 | rating 선형 환산 금지. 100% 과거 action 일치도 새 상대의 W/D/L 보장 아님 |
| 초기 농장이 seed와 무관 | [ENGINE] 동일 configuration의 `_new_farm`은 deterministic. 함수에 seed 인자가 없다는 것만이 아니라 실제 본문에 RNG 호출이 없음을 확인 | boardSize·startingMoney 등 configuration까지 manifest에 고정 |
| seed 변화는 상점·잡초, 나머지는 시장 압력뿐 | 설명이 불충분하다. 일꾼 수·자금·seed·재고·tile 상태가 누적되고 좌석별 처리와 상대 행동도 영향을 준다 | 관측 상태와 ‘첫 divergence’를 기록해야 함 |
| 첫 두 상점이 같으면 route 대응 가능 | [ENGINE] 잡초와 상점이 같은 일별 RNG를 공유한다. 빈 tile 수에 따라 RNG 소비가 달라진다. 같은 seed라도 정책/상대/좌석이 다르면 상점 경로가 달라질 수 있다 | 미래 상점/최종 reward로 route 선택 금지. 실행 시점까지 열린 상점과 현재 상태만 사용 |
| 보유 6판은 현재 top 6 agent의 행동 | 파일 존재는 확인. 당시 submission ID·날짜·당시 rating과 현재 artifact 동일성은 N/A | 팀 이름만으로 ‘현재 top 10’ label을 붙이지 않음. 과거 자료는 파이프라인 검증용 |
| K3는 우리 실험이 아니므로 풀어도 됨 / §9가 사람 승인만 요구 | 둘 다 부정확. §9는 재검토 조건의 명시적 인용과 [ENGINE]/[HOSTED] 근거를 요구한다. K3 조건은 ‘—’다 | 먼저 Claude가 K3 scope/재검토 조건 정정안을 쓰고 독립 검토·Coordinator 반영. 사람 승인만으로 근거를 대체하지 않음 |
| 6개 tape × 4봇·47 pool은 몇 분 | 후보만 6×(4+47)×2=612경기/seed. 가정상 4초면 2448초=40.8분이며 parent·I/O·계측은 별도 | 실제 runner benchmark로 예산 산정. pool 전체 전수검색보다 후보 수를 사전에 줄임 |
| top 50 SubmissionCount=2는 복제 방어의 증거 | CSV 필드값은 확인. 전략 다양성이나 복제 방어 의도는 알 수 없음 | 두 슬롯의 효과는 같은 셀의 패배 패턴으로 측정 |

동메달 rank 923/2442.5는 **제공된 CSV에서 해당 행을 확인한 값**이다. 메달 정책의 최신 적용 여부는 별도 공식 확인 전 확정하지 않는다. CSV의 수집시각은 F-T18에 12:37 KST로 쓰였으나 이번에 독립 검증하지 않았다. Gemini의 21:35 보고는 Sian 2,007위·EXP-007 1541.3으로 더 최신이므로 서로 다른 snapshot을 합치지 않는다. 2442.5−1726.6=715.9는 해당 CSV의 거리일 뿐 예측치가 아니다.

## 2. 기술적 선택

**추천: donor 한 계보의 일관된 route를 단위로 가져오고, 관측 상태가 맞는지 확인하는 작은 executor를 단계적으로 검증한다.**

- tape replay: 시각 t→기록 action. 가장 싸지만 원래 경로를 벗어나면 대응 정보가 없다.
- behavior cloning(BC): 현재 observation→action 학습. unseen state와 조합된 action의 합법성·데이터량 문제가 추가된다.
- 이번 후보: 먼저 donor route 자체의 이전 가능성을 확인하고, 실패 원인이 특정되면 한 가지 상태 대응을 별도 카드로 검증한다. 여러 donor의 개별 action을 다수결로 섞거나 새 RL 학습까지 동시에 시작하지 않는다.

단순히 기존 parent의 farm plan에 donor market만 붙이지 않는다. 구매·고용·이동·생산·판매가 서로 전제이므로 한 묶음으로 비교한다. 반대로 검증되지 않은 큰 시장 controller를 한 번에 추가하지 않는다. route 교체와 guard 추가는 서로 다른 factor다. route 교체를 one_change로 쓸 때는 ‘모든 전략이 동일’이라고 쓰지 않고 `route bundle SHA A → SHA B, executor 고정`으로 정확히 정의한다.

Ross, Gordon, Bagnell(2011)은 행동이 다음 관측 분포를 바꾸는 imitation learning의 문제를 설명한다. 이 연구는 **모방 경로에서 벗어난 상태의 검증이 필요하다는 근거**이며, Kaggriculture의 성공률을 예측하지 않는다. DAgger는 방문 상태에서 expert label을 받을 수 있어야 하는데, 여기에는 donor 실행 코드/oracle이 없으므로 replay만으로 그대로 적용할 수 없다.
출처: https://proceedings.mlr.press/v15/ross11a.html

## 3. 실행 순서와 담당

날짜는 09-16 기준 제안이다. 선행 조건 미충족 시 뒤 단계로 넘어가지 않는다. 새 전략은 기존 내부 cutoff인 09-27 00:00 KST 전에 끝낸다.

### S0 — 09-17, 계약·최신 상태 정리 (Coordinator + Claude, Codex 검토)

- BOARD에 P1b 독립 검증 LOCAL FAILURE, EXP-011 사전등록/계측 대기, 최신 snapshot 출처를 반영한다. 현재 HOLD를 숨기지 않는다.
- K3 원문은 rayk notebook markdown cell 48의 전체 market-tape graft 실패다. 이는 모든 replay 활용·BC·일관된 full-route 교체 실패의 증거가 아니다. 그렇다고 이름만 바꿔 K3를 우회하지도 않는다. Claude가 구현 범위·engine·상대·재검토 조건·새 [ENGINE]/[HOSTED] 근거를 명시하고 독립 검토자가 적용 범위를 판정한다.
- 근거 후보: engine의 자금/일꾼 상태 의존성과 episode 108076177의 cash→HIRE 실패. 이것은 대응 계측의 필요성이지 새 guard가 해결됐다는 증거가 아니다. EXP-008 실패도 함께 인용한다.
- P1b correctness 경로 또는 명시적인 전향적 계약 변경 중 하나를 owner가 확정한다. ‘상속 counter만 빼면 기준은 동일’은 사실상 허용 집합을 바꾸는 변경이다. candidate≤parent aggregate만으로 새 손실 원인 0을 입증할 수 없고, 기존 16 record를 다른 seed의 허용량으로 전용할 수도 없다. 이 계획은 해당 변경을 채택하지 않는다.
- **종료:** Coordinator의 실행 가능 범위·gate 버전·K3 판단이 파일에 남음. 미충족이면 후보 실행 BLOCKED, 자료 조사와 재현 도구 설계만 진행.

### S1 — 09-17, 최신 donor inventory (Gemini 수집, Claude 출처 확인)

- 먼저 공식 index의 metadata·파일 목록·일별 URL·license를 읽는다. index 다운로드와 20GB replay archive 다운로드를 구분한다. 전체 archive를 선제 수집하지 않는다.
- 고정된 leaderboard snapshot의 top 10 팀에서 최근 72시간 episode를 목록화한다. 팀 ID와 episode의 submission ID를 연결하고, 좌석·상대·당시 rating·날짜·engine/configuration·raw SHA·수집 URL을 기록한다. 접근 불가/ID 부재는 N/A로 남긴다.
- 제안 수집 상한: 전략 계보가 겹치지 않는 최대 2 donor, donor당 최대 12 episode. label 없는 과거 tape로 부족분을 ‘현재 top 10’처럼 채우지 않는다. 승리뿐 아니라 패배도 보존한다. 실제 데이터가 적으면 실행 카드 전에 재설계한다.
- 시간·상점 경로·상대·action hash 중복을 조사한다. donor 내부 route를 보존하고 복제본을 독립 donor로 세지 않는다. 결과를 본 뒤 가장 bank가 큰 episode를 고르지 않는다.
- 기존 ymg_aq 6판은 extractor 검증용으로 활용 가능. snapshot 시점 Mengfei Li는 rank 12이므로 ‘top 10 자료’와 구분한다.
- **종료:** raw→episode→seat→donor submission→tape 연결표, license 기록, donor 선택 규칙, 개발/평가 분리 manifest. 라이선스 불명 자료는 후보 삽입 전 BLOCKED.

### S2 — 09-18, 원래 경기 재현 (Codex 구현, 독립 검증자 확인)

- raw replay의 `steps[i]`는 action 실행 후 상태다. 학습/판정용 입력은 행동 직전 observation이며, 초기화 row와 719번 agent call을 구분한다. 자체 생성 replay round-trip으로 action off-by-one 오류를 먼저 배제한다.
- **원래 seed·configuration·양측 기록 action·원래 seat를 모두 고정한 재현**에서 action 및 비교 대상 state projection 일치율 100%, 양측 최종 reward exact match를 요구한다. wall time·로그 등 비게임 필드는 제외하고 projection을 사전 명시한다. 한쪽 donor만 다른 상대와 재생하는 것은 이 검증이 아니다.
- seed는 `configuration.seed`가 null일 수 있어 `info.seed`를 확인한다. sample 106263397에서 실제로 이 구조를 확인했다.
- 원래 상태를 맞춘 다음 좌석 교대·새 seed·새 상대에서 첫 divergence를 기록한다. exact reproduction은 추출기 검증이고 일반화 성능이 아니다.
- **종료:** 추출 fixture PASS, donor별 원래 경기 재현 PASS. 1개라도 미일치면 원인을 해결하기 전 성능 arena 금지. donor private state가 누락되면 reconstruction 검증 또는 BLOCKED로 남김.

### S3 — 09-19~20, 후보 1개 선택용 screening (Claude 카드, Codex 실행)

- S0 완료 후 HYP-0010 아래 새로운 고유 TEST-ID를 updater로 발급하고 정식 card를 만든다. 이 문서의 검토 TEST-ID를 대전에 재사용하지 않는다. HYP-0019의 rating 회수율 주장은 별도이고 검증된 것으로 바꾸지 않는다.
- A는 실제 parent tar를 그대로 clean-room에 푼 것. B는 동일 executor에서 사전 선택한 donor route bundle 하나만 교체한다. 호환 불가능하면 별도 executor 기반 재설계로 돌리고 parent 대비 one-factor인 척하지 않는다.
- 제안 예산: 최대 2개 donor candidate, 공개 4봇, 고정 seed 5개, 양 좌석. A를 한 번씩 공통 측정하면 최대 `(1+2)×4×5×2=120경기`. 실제 seed 목록·상대 SHA·후보 SHA·runner SHA를 결과 보기 전에 card에 고정한다. 여기서는 seed를 임의 배정하지 않았다.
- 기존 47 pool은 이미 여러 번 쓴 diagnostic set이다. donor와 같은 episode의 양측, 같은 submission, exact/near-duplicate action 계보는 독립 평가에서 제외한다. 제외 뒤 새 목록과 SHA를 만들며 47개라고 부르지 않는다.
- 측정: W/D/L, paired score, parent 대비 paired delta, 상대별 결과, 큰 패배 빈도와 패배 margin 분산. bank는 보조. `noop`, `shed_discarded`, `shed_unsold`, `orders_truncated`, `buy_failed`, `hire_failed`, `seed_blocked_plant`, hands mismatch, exception과 guard activation을 기록. `sell_unfilled`는 diagnostic.
- 추가 diagnostic: 첫 divergence turn·전제 불충족 사유, 실제 체결량, cash·hands·seeds·tile·동물 feed 상태, shop route coverage. 단순 action 일치율로 후보를 선택하지 않는다.
- **종료:** 사전 정의된 선택 규칙으로 최대 1개 후보 또는 NONE. 숫자 success/failure/inconclusive·상대별 non-inferiority margin·동률 처리 규칙은 Claude 카드에서 고정한다. 지금 효과 크기/power 근거가 없어 이 문서가 임의를 확정하지 않는다. 빈 항목이 있으면 BLOCKED. 작은 screen 통과는 제출 근거가 아니다.

### S4 — 09-21~23, 새 상황 확인·최대 한 가지 보정 (Claude 설계, Codex 실행)

- screen 결과를 보기 전에 보류했던 날짜·donor submission·상대 계보의 평가자료와 별도 seed 집합을 사용한다. 같은 episode의 다른 seat를 holdout으로 나누지 않는다. 공개 tape 상대는 고정 기록일 뿐 원래 reactive agent가 아니므로 ‘top 10 agent를 이겼다’고 쓰지 않는다.
- 최종 confirmation 제안: A/B×공개 4봇×50 fixed seeds×양 좌석=800경기. 최신 donor-disjoint replay stress set은 별도 manifest와 예산으로 사전 고정한다. seed를 모든 agent가 볼 수 있으므로 reused holdout이며 blind라고 부르지 않는다.
- seed의 양 좌석과 같은 계보를 고려한 CI를 사전 고정한다. 기존 arena의 t-interval은 전승에서 폭 0이 될 수 있으므로 그대로 승격 판정에 사용하지 않는다. 경계값에서도 유효한 CI 구현 검증이 선행 조건이다.
- 승격은 기존 공개 4봇 paired score의 95% CI 하한 >0.5, 사전 숫자 non-inferiority 및 release gate 모두 충족해야 한다. 해당 표본의 power가 부족하면 INCONCLUSIVE이지 seed 추가 근거가 아니다.
- 실패 원인이 하나로 좁혀질 때만 다음 카드에서 guard 한 가지를 시험한다. 예: HIRE 실패를 검출하고 의존 action 재계획. **HIRE를 PASS로 바꾸는 것만으로 복구라고 하지 않는다.** 어느 상태로 돌아올지·guard 비용·fallback 동작을 명시한다. 새 guard activation=0만을 성공으로 삼지 않는다.
- 원래 postmortem 108076177 및 정상 control을 포함하되 이미 개발에 사용한 사례임을 표시한다. 다른 opponent/seed의 confirmation이 필요하다. EXP-008 exact B schedule을 재활용하지 않는다.
- **종료:** PASS/FAIL/INCONCLUSIVE, 성능 gate와 release gate 별도 판정. 후보를 고른 데이터로 최종 성능을 선언하지 않음.

### S5 — 09-24~26, release·hosted 판단 (독립 검증자 + 사람)

- Identity / Schema / Runtime / Isolation / License를 exact tar 기준으로 통과시킨다. 제출 후 Ledger 연결. 관련 계약은 AGENTS §7.5.
- 동일 상대·seed·좌석의 패배 overlap과 각 후보의 독립 강도로 final pair를 고른다. 상관이 계산 불가하면 N/A. 전략 이름이 다른 것만으로 다양성을 인정하지 않는다.
- 활성 `[EXP-006, EXP-007]`에 C를 올리면 `[EXP-007,C]`가 된다. EXP-006이 먼저 은퇴한다. 교체할 ID·잃는 경기 이력·새 관측 계획을 표에 쓰고 사람에게 구체적인 tar를 제시한다. 이번 요청은 제출 승인이 아니다.
- 제출 시각+24h/+72h에 각각 직전 24h episode window를 고정해 W/D/L·opponent/seat·sample 수·무음 실패를 보고한다. 이는 수렴 보장이 아니다. A가 은퇴한 뒤 과거 A와 현재 C rating 차이를 causal improvement라고 쓰지 않는다.
- 09-27 00:00 새 전략 중단, 09-28 18:00 freeze, 09-29 18:00 제출 완료 목표. 최종 공식 deadline은 기존 확인 기록상 10-01 08:59 KST이며 실행 직전 official timeline을 재확인한다. 실패 시 목표를 몰래 낮추거나 gate를 완화하지 않고 ‘목표 미달 위험/제출 후보 없음’으로 보고한다.

## 4. 기존 도구와 새로 필요한 최소 구현

- 재사용: `tools/verify_pool.py`, `tools/postmortem.py`, `tools/postmortem_hosted.py`, `tools/instrument.py`, `tools/compare_action_streams.py`, `tools/arena.py`, `tools/compare_hosted_episodes.py`.
- 부족분: donor provenance/split manifest, raw-action round-trip verifier, route compatibility/첫 divergence 기록, 경계값에서 유효한 CI. 기존 도구가 이 요건을 충족한다고 가정하지 말고 acceptance test부터 정한다.
- 후보/결과는 Codex 소유 경로, card·KILLS·FACTS 정정은 Claude, raw 수집·분석은 Gemini. runtime 네트워크 사용 없음. top 10 source code 복원·새 RL pipeline은 이 계획 범위 밖이다.
- 상위 모델이 유용한 부분: K3/gate 계약 해석과 독립 설계 검토. 파일 추출·SHA·inventory는 경량 모델로 충분하다. 이번 검토는 sub-agent를 실행하지 않았다.

## 5. 근거와 재현

- `evidence/FACTS.md:297` F-T18 및 `:314` F-T19 — 검토 대상 주장, 원문 수정은 Claude에게 제안.
- `docs/official/rules.md:30` data license, `:56` winner license, `:62` incompatible input data/model 예외, `:68` external data, `:108` replay, `:111` no ingress/egress. ‘타인의 모든 원자료도 CC-BY로 재공개’로 일반화 금지.
- 공식 URL: https://www.kaggle.com/competitions/kaggriculture/rules 및 https://www.kaggle.com/datasets/kaggle/kaggriculture-episodes-index — 이번 web fetch 본문 N/A. 저장된 `docs/discussion/731215_Daily_Top_Episodes_Dataset.md:7`의 배포 목적은 확인, Author가 N/A라 공식 작성자 attribution은 재확인 필요. 댓글 수치는 [COMMUNITY]이지 [OFFICIAL] 아님.
- engine 1.32.7 `kaggriculture.py:142-170`, `:836-840`, `:870-891`; SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` 직접 일치 확인.
- `docs/code/raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb` markdown cell 48 (0-based), C94 subsection: K3 원출처. [COMMUNITY], 수집일/원 notebook engine/version은 이 문서에서 N/A, 로컬 일반화 결과로 승격하지 않음.
- `coordination/reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md` — 108076177 cash→HIRE 실패 관측; 최종 패배의 causal 설명은 [INFERENCE].
- `coordination/reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md` — 13경기/16 parent record LOCAL FAILURE 독립 확인. 이번에 대전을 재실행하지 않음.
- parent tar `coordination/proposals/claude/exp006/submission.tar.gz`, SHA `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721`.
- pool 검증: `python3 tools/verify_pool.py --glob 'private_artifacts/tapes/*-replay.json' --expected-count 47 --expected-sha256 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1` → PASS. `*.json`은 49개로 target/control 2개까지 포함한다.
- 상세 inventory와 해시는 같은 이름의 `.audit.json`에 보존한다. 가설 상태는 새 대전 없이 SOURCE_CLAIM 유지; 검토 event만 추가한다.

다음 행동 두 가지:

1. Coordinator/Claude가 최신 상태와 K3 적용 범위·P1b HOLD 처리방안을 먼저 확정한다.
2. Gemini가 최신 top 10 donor의 episode/submission/날짜 inventory를 만들고, Codex가 원래 경기 재현 fixture부터 준비한다.


---

## `proposals/codex/20260917-DONOR-ROUTES-INDEPENDENT-REVIEW.md`

# 새 채팅용 독립 검토 지시

권장: GPT-5.6 Sol / high. 분석 재실행을 위한 필수 전환이 아니라, 해석을 새 시각에서 검증하기 위한 선택이다.

다음 내용을 새 채팅에 붙여 넣는다.

> ~/kaggle/Kaggriculture에서 두 donor 행동 분석을 독립 검토해 줘. 먼저 AGENTS.md와 coordination/BOARD.md를 읽고, coordination/reports/codex/20260917-1640-DONOR-ROUTES.md를 검토해. 근거는 experiments/results/top10_donor_routes_20260916/analysis.json 및 validation.json, donor identity는 experiments/results/top10_donor_20260916/donor_manifest.json에 있다. tools/analyze_donor_routes.py와 tests/test_analyze_donor_routes.py도 확인해.
>
> 확인할 핵심은 ① action 직전 observation을 사용했는가 ② Majkel의 6/7코인 고용 차이 및 index27 복구가 실제 상태로 입증되는가 ③ 실패한 STRAWBERRY seed 요청을 실행된 구매와 분리했는가 ④ M의 최초 action 차이를 shop/상대 반응이라고 과장하지 않았는가 ⑤ market 빈 배열 일치와 실제 주문 일치를 구분했는가 ⑥ GOOSE·4번째 토지의 동시 관측을 독립적인 효과로 승격하지 않았는가다.
>
> 원자료는 private_artifacts/top10_donor_20260916/의 고정 5경기이며 두 donor가 만난 한 경기를 중복 표본으로 세지 마. 동일 submission의 3경기만으로 donor 소스 코드나 hidden policy를 복원했다고 주장하지 마. 검토는 read-only로 하고 후보 구현·새 대전·다운로드·제출·gate/KILL 수정은 하지 마. 자동 skill 호출 없이 직접 검토해. 오류와 근거 file/JSON path를 우선 보고하고, ‘관측으로 확정/설명 가능하지만 미확정/근거 없음’을 나눠 마지막에 실험으로 옮길 가치가 있는 한 가지 가설만 추천해.


---

## `proposals/codex/20260917-EXP013-CONTRACT-REVIEW.md`

# EXP-013 구현 전 계약 검토 및 Coordinator 제안

VERDICT: NEEDS_REVISION. candidate/계측 구현 및 baseline 실행 없음.
검토 카드 SHA-256: 96f0278293d56fe50e639f273abe6eaf5f5987c334d9d037cde63c3874354fd6.

[ENGINE/CODE] 고정 엔진과 parent tar를 직접 읽었다. parent main member SHA bba042e04cff32ab53be2c59c2f5cd9053c8de2bf31632e396ca8faa502896b2 확인. 카드에 적힌 모든 replay 수치는 이번에 독립 재계산한 것이 아니다.

## 구현 전에 Claude가 고칠 항목

1. **parent action 정의 오류 (카드158).** `yh.agent()`는 parent의 최종 action이 아니다. tar main.py agent는 그 결과에 `_layer(yh, observation, deepcopy(base_action))`를 적용한다. recovery는 기존 layer와 fallback을 포함한 parent 최종 action 뒤에 붙여야 한다. yh.agent를 두 번 호출하지 않는다. 그렇지 않으면 clone-preempt 보존과 무트리거 parity가 깨질 수 있다.
2. **daily reset과 recovery_days 정의 충돌 (카드165/189/192/333).** T(s)=0이어도 T_first(day)>0이면 hour0의 A=0에서 shortfall은 양수다. '정의상0'은 틀리며 hour window로 배제되는 것이다. recovery_days와 A_ontime 기록도 first HIRE 실행 후 observation에서만 평가하도록 동일 조건을 명시해야 한다. day0은 first HIRE가 step1이므로 일반적인 hour>=1 검사만으로 충분하지 않다.
3. **4턴 제한이 실행식에 없음 (카드199/204).** eligible 조건에 `hire_turns_today < MAX_RECOVERY_HIRE_TURNS`를 넣고 성공/실패와 별개로 추가 HIRE를 emit한 턴마다 정확히1 증가, day reset 시0으로 정한다. 문장 상한과 4개 조건 중 무엇이 우선인지 구현자가 추측하게 하지 않는다.
4. **trace와 parity hash 경계 (카드D-1/G2).** tools/instrument.py:530의 _audited는 추가 키까지 action_stream에 저장한다. 무트리거에서도 `__exp013_*:0`을 붙이면 동작은 같아도 hash는 다르다. 무트리거에서는 trace 키를 전혀 붙이지 않는 방식 등 하나를 정한다. 기존 hash를 조용히 변경하지 않는다. metadata 자체를 recovery_trigger_turns로 세지도 않는다.
5. **route desync라고 부르는 측정값은 실제 위치/소지품 정합성을 검증하지 않음 (D-3).** instrument.py:435-448은 tile 변화와 inventory 총량의 불변 여부로 tile-op no-op을 센다. 기대 위치/기대 item별 inventory와 비교하지 않고 이동 실패는 blocked_moves로 별도 집계한다. `hand_tile_noop_actions` 같은 정확한 이름으로 기록하거나 별도 기대상태 비교를 정의한다. diagnostic으로 남기는 결정은 유지 가능하다.
6. **catch-up의 expect 갱신을 분리 (C-4).** expect를 spawn_slot로 초기화한 뒤 'emit한 이동마다 갱신'한다고 쓰면 catch-up 이동을 다시 더할 수 있다. walk 중 expect는 목적지 spawn_slot로 유지하고, 도착 후 queue 이동에만 갱신하는 등 상태 전이를 명확히 고정한다. 또한 queue pop 시점·seed guard로 PASS된 PLANT의 소모/재시도 여부를 명시한다.

[INFERENCE] 빈 inventory는 full route 지연 재생의 출발 조건일 뿐 성공 보장이 아니다. 늦은 PICKUP 시점에 shed 물건이 없을 수 있다. '유일하게 정합적' 대신 '이번 카드에서 택한 방식'으로 한정한다. reserve를 사전 고정하는 것이 원천적으로 one-factor 규약 위반인 것도 아니다. reserve0은 정당한 설계 선택이지만 유일한 허용안은 아니다.

## Coordinator 제안 — 기준 완화와 진단 허용을 구분

현재 fixed parent의 P1b는 FAIL이다. 그 사실은 바뀌지 않는다. 하지만 수정 artifact의 미래 PASS까지 불가능한 것은 아니다. BOARD P2 전체를 'EXP-011 판정+사람 승인'으로 대체하면 새 전략에도 release 실패를 우회하는 길이 생긴다.

제안 문구: '새 전략 P2는 기존 P1b PASS 조건 유지. 이미 관측된 correctness failure를 고치는 bounded diagnostic/repair는 EXP-011 판정, exact parent, 카드별 scope·gate, 독립 검토, 사람 승인을 갖추면 별도 경로로 실행 가능. 그 결과는 release PASS를 대신하지 않으며 수정 candidate의 release preflight를 다시 통과해야 한다.'

현재 카드 §G는 EXP-011 우선 및 사람 승인을 요구한다. 본 제안은 그 조건을 해제하지 않는다. EXP-011과 EXP-013은 같은 tools/instrument.py를 변경하므로 구현은 순차 통합하고 각 runner SHA를 동결한다. EXP-013 문서 수정은 EXP-011과 독립적으로 진행 가능하다. G0b는 카드 자체가 §G 충족 전 parent 실행을 금지하므로 지금 실행 가능한 선행 작업으로 부르지 않는다.

## 다음 실행 순서

1. Claude가 위 계약 결함을 수정하고 카드/원장 SHA를 갱신한다. Codex는 EXP-011 기존 계약을 우선하며 EXP-013 counter 구현을 동시에 섞지 않는다.
2. Coordinator가 bounded correctness 경로를 명시한 뒤 사용자 승인을 받는다. EXP-013 G0b parent baseline 재기록 후 candidate 비교. EXP-014는 상대/seed/gate를 미리 정할 수 있으나 candidate와 parent SHA는 실제 확보 후 동결하며 성급히 카드 번호를 선점하지 않는다.

검증: `python3 tools/validate_hypotheses.py --strict` exit0,32 entries. 이것은 원장 형식 검증이며 EXP-013 설계의 correctness 검증은 아니다.


---

## `proposals/codex/20260917-STATE-CONDITIONED-RECOVERY.md`

# State-conditioned opening recovery — owner용 사전등록 제안

VERDICT: BLOCKED_DRAFT (실행 카드 아님). HYP-0032 / TEST-STATE-CONDITIONED-RECOVERY-PREREG.

고용이 덜 됐을 때 실제 hands를 보고 부족분을 채우는 변경 하나를 검토한다. 효과는 N/A다. late hire의 시작 위치·소지품과 missed action 처리까지 정의해야 실행할 수 있다.

## 근거와 범위

[LOCAL descriptive] donor Majkel의 index25 cash 7/7/6, post hands 4/4/3, index27 3→4를 관측했다. donor 내부 decision rule과 효과는 미확정이다. 입력: experiments/results/top10_donor_routes_20260916/analysis.json; 재현: `python3 tools/validate_donor_routes.py`.

[HOSTED] 우리 episode108076177에서 cash0, HIRE3 실패, 이후 존재하지 않는 hands에 의존하는 tape가 관측됐다. 근거: coordination/reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md. 이 연결은 recovery 실험의 동기이며 효과 증거는 아니다.

Parent 후보는 EXP-006 tar `coordination/proposals/claude/exp006/submission.tar.gz`, SHA-256 `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721`. P1b correctness 이후 parent가 바뀌면 새 SHA로 카드와 baseline을 다시 동결한다. 실패한 EXP-008 opening schedule은 사용하지 않는다.

## 한 가지 변경의 제안

A: frozen parent의 기존 fixed schedule.
B: opening HIRE 결과가 부족한 경우에만 실제 `len(hands)`를 기준으로 recovery mode를 켠다. planned target보다 부족한 인원만 요청하고, 현 observation에 존재하는 hands에만 작업을 배정한다. 성공한 opening에서는 A와 action stream이 같아야 한다.

고정: opening 자금 배분, 작물·동물 선택, shop routing, 판매 전략, 다른 날의 고용 정책, 엔진1.32.7. GOOSE·4번째 토지·donor 전체 tape 복사는 추가하지 않는다.

**구현 전 owner가 확정할 세 항목:**
1. opening 범위·목표 인원 source·재시도 종료 index를 숫자로 지정한다. 다음 날 hands reset과 부분 체결을 구분한다.
2. HIRE를 기존 주문 사이 어디에 넣고 자금·10주문 한도를 어떻게 배분할지 정한다. 기존 BUY를 밀어내면 별도 효과가 된다.
3. late hand가 놓친 이동/작업을 replay할지, 현재 상태에서 route를 다시 만들지 결정하고 exact rule을 쓴다. 단순 hand 배열 자르기는 복구가 아니다.

이 세 항목을 임의로 채우면 서로 다른 candidate가 되므로 현재 구현/arena는 실행하지 않는다.

## 고정 diagnostic 표본과 숫자 gate 제안

owner 인수 후 결과를 보기 전에 동결한다. target seed1125321547 × both seats, Remielle episode108076177 tape; control seed1989066512 × both seats, today episode108079022 tape. 총4 cells, parent 먼저 실행한 뒤 candidate 동일 cells. 추가 seed로 결과를 보완하지 않는다.

- correctness: exception/illegal action/order truncation/seed-blocked PLANT 증가 0; recovery 전용 dropped/deferred action 카운터 필수.
- unaffected control: recovery trigger0인 각 cell의 parent/candidate action mismatch0.
- mechanism: target의 missing-hand-dependent action 수가 parent보다 감소하고 최종 누락 인원0. route desynchronization은 actor position·inventory·pending work를 포함한 계측 정의를 먼저 동결한다. 정의 N/A면 이 gate도 미실행이다.
- outcome: target paired score 증가 >0, control candidate-only loss0이면 다음 큰 bank 카드 후보. 동일이면 INCONCLUSIVE, target 점수 감소 또는 control 새 패배 >=1이면 FAILURE. mechanism 통과만으로 효과를 선언하지 않는다.
- 네 cells는 failure 재현용이며 승격용 아님. public4/pool 평가의 exact 상대 SHA·seed·숫자 gate는 별도 카드에서 동결한다. hosted 효과 N/A.

## 실행 조건 및 owner 이관

P1b FAIL/HOLD를 그대로 유지한다. 먼저 EXP-011 correctness 경로를 따른다. K3는 donor 전체 market tape 복사에 대한 항목이며 이 제안은 우리 parent의 좁은 recovery다. 범위를 donor tape 복사로 넓히려면 K3 재검토 조건 및 ENGINE/HOSTED 근거를 별도 제시한다. K1/K9 수정 없음.

Claude는 미확정 세 항목과 계측 정의를 확정한 뒤 소유 경로 experiments/cards/에 새 카드 번호를 부여한다. EXP-012는 EXP-011 후속으로 예약돼 있으므로 여기서 사용하지 않는다. canonical card·candidate SHA·opponent SHA·실행 TEST-ID와 독립 검토가 준비되기 전까지 이 문서는 제안이다.


---

## `proposals/codex/20260917-correctness-path/BOARD.proposed.md`

# BOARD — 지금 무엇이 중요한가

**갱신 2026-09-17 KST · Codex, 사람 요청으로 Coordinator 역할 수행.**

<!-- 검토용 제안본: 사람의 문서 적용 승인 전 정본 아님. 실험 실행 승인 아님. -->
코디네이터만 수정한다. 2일 이상 갱신되지 않았으면 AGENTS §11에 따라 먼저 현재 상태를 재확인한다.

**현재 계획: [plan/CURRENT.md](../plan/CURRENT.md) → [마감까지의 계획](../plan/kaggriculture_deadline_plan_20260915.md).**

1. 무엇을 하는가: P1b에서 확인한 failure의 correctness 경로를 준비한다.
2. 왜 하는가: 새 전략을 추가하기 전에 기존 손실을 진단하고 범위가 정해진 repair를 검증해야 한다.
3. 측정 결과: `[LOCAL]` P1b 13/13경기 완료, gated parent 16/16 zero gate FAIL, hands mismatch92. 후속 독립 검증은 VERIFIED_LOCAL_FAILURE. EXP-011은 PLANNED, EXP-013은 NEEDS_REVISION/실행 BLOCKED.
4. 다음: EXP-011 진단을 우선 준비하고 EXP-013 계약 수정은 함께 진행한다. 별도 실행 지시 전에는 baseline/candidate 경기를 시작하지 않는다.

## 현재 상태

| 항목 | 값 | 근거 |
|---|---|---|
| 공식 최종 제출 | **09-30 23:59 UTC = 10-01 08:59 KST** | 09-15 직접 읽은 공식 Timeline, 아래 snapshot |
| 공식 참가·팀병합 | **09-23 23:59 UTC = 09-24 08:59 KST** | 동 |
| 제출 기록 | **5건**, 모두 COMPLETE 표시 | 이번 CLI 조회 |
| 활성 슬롯 | **EXP-006 56165718 / EXP-007 56175620**, 2개 | CLI 최신 두 ID·공식 latest-2·공개 active UI 대조 |
| 최신 hosted 점수 | EXP-006 **1862.6**, EXP-007 **1635.9** | **09-15 KST 조회**, CLI 완료 시각 상한 01:13:12 KST |
| Sian 순위 / 상금 경계 | **1,724위 / 10위 2974.2** | 09-15 KST 공개 UI; 현재값은 계속 변함 |
| 팀 | 공개 UI Sian, member `<kaggle_user>` 1명 확인 | 비공개 초대·합병 상태 N/A, 기본 계획은 솔로 유지 |
| 잠정 incumbent | **EXP-006** | 현재 두 활성 점수에서 우위; parent 대비 causal 효과는 미결 |
| 최신 완료 실험 | **EXP-008 FAILURE** | 결과 report·verdict SHA 아래 |
| 엔진 | **kaggle-environments 1.32.7**, 설치 Python/JSON SHA lock 일치 | 이번 read-only 해시 확인; hosted 최신 module_version N/A |
| 현재 Python | **3.13.14** | `python3 --version` |
| release 계측 | **schema 3 · P1b FAIL** | 실제 parent tar 고정13경기, 독립검증 VERIFIED_LOCAL_FAILURE. 새 candidate preflight는 N/A |

최신 직접 조회 정본: [20260915-0115-KAGGLE-SNAPSHOT.md](reports/codex/20260915-0115-KAGGLE-SNAPSHOT.md).
09-17 갱신은 P1b 후속 판정과 correctness 실행 경로만 반영한다. 위 hosted 수치는 과거 snapshot이며 새 조회가 아니다.
[evidence/HOSTED_LEDGER.md](../evidence/HOSTED_LEDGER.md)는 09-14 이전 snapshot까지이며 Claude owner의 새 행 반영을 기다린다. 날짜가 다른 두 값을 같은 시점 값처럼 비교하지 않는다. 이 BOARD는 더 최신인 위 직접 조회를 명시적으로 인용한다.

## 다음 작업 — 우선순위와 종료 조건

| 순위 | 작업 | 담당 | 종료 조건 |
|---|---|---|---|
| **P0** | EXP-008 결과·registry·hosted 원장 동기화 | Claude | [owner 이관안](proposals/codex/20260915-owner-record-sync.md) 반영. EXP-008 frozen card는 보존하고 결과 보고서로 연결 |
| **P1a** | 공개 notebook/discussion inventory·변경분·정정 댓글 판독 | Gemini 단일 writer / Claude 판독 / Codex 원장 | 09-16 18:00 KST까지 계획 §5.1의 source SHA·채택/보류/기각·owner 인수 표. 이후 09-26까지 매일 변경분; 미확인 claim은 보류 |
| **P1b** | actual parent A release preflight | Codex / 독립 검증자 | **VERIFIED_LOCAL_FAILURE**: 13/13 완료, parent16/16 zero gate FAIL. 정본 report와 후속 독립검증 참조. 새 전략 HOLD 유지; 아래 C0/C1 경로 준비 |
| **P1c** | 최신 24시간 hosted window + 각 agent 최신 패배 1판 postmortem | Gemini 수집 / Claude 해석 / Codex 재현 | 09-16 P1 보고서에 계획 §5.3의 표본·ID·SHA·W/D/L·실패 원인 보고; 부족하면 N/A |
| **P2** | 새 전략 one-factor card | Claude | 실제 parent P1b PASS·관련 claim 인수·원인 근거·exact card가 선행. FAIL이면 새 전략 HOLD. C0/C1은 관측된 correctness failure만 다루며 P2나 release 승인 대체 불가 |
| **P3** | 수락된 카드 구현·독립 검증 | Codex / 다른 검증자 | 카드 판정 + release gate를 별도 통과. local만으로 hosted 우위 선언 금지 |
| **P4** | final pair·제출 순서 결정 | Coordinator / 사람 | 독립 강도·패배 패턴·FIFO 이력 손실·승인 기록 |

## Correctness 실행 경로 — 새 전략·제출과 구분

근거: 마스터 플랜 §5.2 FAIL/N/A 경로. 현재 parent FAIL은 유지하며 수정 artifact의 미래 PASS까지 불가능하다고 해석하지 않는다.

| 단계 | 담당 | 조건과 종료 |
|---|---|---|
| **C0 EXP-011** | Claude 카드 / Codex 계측 / 별도 독립 reviewer | 별도 실행 지시 후 artifact 불변 attribution 진단. 고정13경기 D1~D4/R·class 판정을 원장에 기록하고 독립 검증. INVALID 또는 gate 실패면 C1 대기 |
| **C1 EXP-013 준비** | Claude / Coordinator | 계약 검토6개 항목 수정, EXP-011 결과별 금지 범위 해소, 카드 SHA·HYP 갱신·독립 설계 검토. 문서 작업은 C0와 함께 가능 |
| **C1 제한 실행** | Codex / 독립 reviewer / 사람 | 유효한 EXP-011 판정 + scope 충돌 해소 + exact-card 사람 승인 후 구현. candidate·runner freeze 및 독립 구현 검토 후 G0b parent→candidate 동일13경기. 결과는 diagnostic이며 제출 불가 |

EXP-011의 REPAIR_AUTHORIZED는 EXP-012 shed repair 설계 자격이며 EXP-013 자동 승인이 아니다. BLOCKED_AMBIGUOUS_ROOT_CAUSE/BLOCKED_STRATEGY_BOUNDARY이면 shed repair 금지를 유지한다. 독립 HIRE 근거의 EXP-013까지 금지하는지 Claude가 카드 범위를 명확히 하고 사람이 별도 bounded 실험 범위를 승인하기 전 대기한다. threshold나 표본을 바꿔 금지를 우회하지 않는다.

EXP-011 이후 계약이 정리된 EXP-013을 다음 제한 실험으로 제안한다. EXP-012는 별도 카드·승인 없이 실행하지 않는다. 같은 tools/instrument.py 변경은 순차 통합한다. parent가 바뀌면 카드·baseline 기준을 재동결한다. 새 runner로 parent baseline을 먼저 기록하며 P1b 원자료는 덮어쓰지 않는다.

상세 분기·승인 범위: [Coordinator 실행안](proposals/codex/20260917-correctness-path/DECISION.md). 문서 적용 승인은 실행 승인이 아니다. 새 전략 P2와 최종 release는 기존 전체 gate를 그대로 통과해야 한다. Coordinator/구현자는 자기 결과를 단독 승인하지 않는다.

P1b 근거: [실행 보고](../experiments/results/p1_release_preflight/report.md), [후속 독립검증](reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md). 최초 보고의 PENDING은 후속 검증으로 해소됐으나 LOCAL FAILURE 판정은 유지된다.

**이미 완료된 일:** EXP-008 계측·card 수락·고정 326셀 실행, gate split, release source 추적.
09-13 BOARD의 ‘EXP-008 card 수락 대기’, 과거 HANDOFF의 ‘v0 첫 제출’은 더 이상 지시가 아니다.
`TASKS.md`의 타 owner 과거 미실행 문구와 registry PENDING은 상태 갱신 대기이며 재실행 명령으로 쓰지 않는다.

## 실험·가설의 현재 결론

- **HYP-0030 / TEST-0008: LOCAL_FAILED.** target cash·HIRE·tiles는 회복했지만 target 0/0/2, pool 새 패배 2셀. G1/G3/G4/G5 FAIL, G2 PASS. exact B schedule 폐기; 결과를 보고 seed 추가·factor 쪼개기 금지.
- **HYP-0006:** 현재 점수 우위와 clone-preempt 자체의 causal 효과는 별개다. parent 은퇴로 원래 hosted A/B는 N/A.
- **HYP-0007:** 두 슬롯 보완성 INCONCLUSIVE. 09-12 표본의 공통 상대 이름은 3명뿐이었다. 새로운 paired episode 판독은 아직 하지 않았다.
- **HYP-0031 / EXP-011:** shed discard attribution, PLANNED.
- **HYP-0032 / EXP-013:** state-conditioned HIRE recovery, NEEDS_REVISION/실행 BLOCKED.
- **09-14 community 제안:** 당시 HYP-0031..0033 표기는 역사적 예약 표기다. 현재 HYP-0031/0032는 위 두 카드의 공용 원장 ID다. EXP-009/010 제안과 혼동하지 않는다.
- **09-15 R10 정정:** 상대 MELON의 `yield_units` 합은 수확 readiness가 아니다. R10의 현재 재고 추가 SELL과 우리 maturity trigger·shift/repay 설계를 분리한다([원문 정정](proposals/codex/20260914-community-trends-plan-update.md)).
- **KILLS 유지:** pure PPO, 네 번째 땅, GOOSE 등은 항목별 재개 조건 확인 전 착수하지 않는다.

## 제출 운영

최신 2개만 남는다. 현재 순서 `[EXP-006, EXP-007]`에서 새 C를 올리면 `[EXP-007, C]`가 된다.
**약한 EXP-007만 교체할 수 있다고 가정하면 더 강한 EXP-006을 잃는다.**

- 최종 후보 pair가 통과하기 전 현재 두 제출 유지가 기본이다. C 하나만 올릴 때도 은퇴할 EXP-006 대비 근거를 검토한다.
- 제출마다 정확한 전후 ID와 이력 손실을 기록하고 사람 승인 후 실행한다. 이번 계획 승인은 제출 승인이 아니다.
- 동일 tar 재제출은 이전 ID·경기 이력을 복구하지 못한다. 점수 reroll용 duplicate 제출 금지.
- 09-27 00:00 KST 새 전략 중단 → 09-28 18:00 freeze → **09-29 18:00 최종 제출 완료 목표**.
- 충분한 후보가 없으면 현재 A/B를 유지한다. 날짜를 맞추려고 gate를 낮추지 않는다.

## 다음 agent가 확인할 exact artifact

- parent: `coordination/proposals/claude/exp006/submission.tar.gz`, SHA `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721`.
- 다른 활성: `releases/public-thomas-replay-router-v2-exact/submission.tar.gz`, SHA `8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180`.
- EXP-008 판정: `evidence/raw/EXP-008/verdict.json`, SHA `9e8cabf4020607abf193ded71071807a8bc9165cba2a95c03180c8a291622d43`.
- 결과: [EXP008-RESULT](reports/codex/20260914-2025-EXP008-RESULT.md), [GATE-SPLIT](reports/codex/20260914-2043-GATE-SPLIT.md).

정정 이력 2026-09-15: 09-13판의 날짜·점수·EXP-008 대기 상태를 최신 근거로 교체했다. 과거 내용은 Git 이력에 남는다. `coordination/CURRENT.yaml`은 구현되지 않았으므로 현재 경로로 가정하지 않는다.


---

## `proposals/codex/20260917-correctness-path/DECISION.md`

# Coordinator 실행 경로·BOARD 변경안

상태: PROPOSED / NOT AUTHORIZED. 사용자 요청은 계획 작성만이며 이번 문서는 실행 승인이 아니다.
2026-09-17. Coordinator: Codex. BOARD 정본·카드·agent·runner는 수정하지 않는다.

기본 결정 제안: **EXP-011로 기존 손실을 먼저 확인하고, EXP-013의 계약 수정은 그동안 진행한다. agent를 바꾸는 실험과 제출 검사는 별도로 판정한다.** 코드 변경은 같은 integrator가 순차 통합한다.

## 1. 확인한 근거

- [LOCAL] P1b: 13/13경기 완료, gated parent16/16 zero gate FAIL, hands mismatch92. `experiments/results/p1_release_preflight/report.md`와 `coordination/reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md`의 VERIFIED_LOCAL_FAILURE를 함께 읽는다. 최초 보고의 독립검증 PENDING은 후속 보고로 해소됐지만 FAIL은 유지된다.
- [CONTRACT] `plan/kaggriculture_deadline_plan_20260915.md:107`은 이미 FAIL 뒤 별도 correctness repair, 새 parent freeze, 동일 preflight 재검증을 허용하는 경로를 요구한다. 따라서 BOARD P2의 새 전략 PASS 조건을 삭제할 필요가 없다.
- [CONTRACT] EXP-011은 artifact를 바꾸지 않는 attribution diagnostic이다. EXP-013은 행동을 바꾸며 효과가 N/A인 recovery 가설이다. correctness라는 이름만으로 EXP-013을 자동 승인하지 않는다.
- [REVIEW] EXP-013은 `20260917-EXP013-CONTRACT-REVIEW.md`의6개 항목 수정 전 NEEDS_REVISION이다. 카드 SHA는96f0278293d56fe50e639f273abe6eaf5f5987c334d9d037cde63c3874354fd6.
- hosted live 수치는 이번에 갱신하지 않았다. BOARD 기존 수치는 과거 snapshot으로 유지한다. 이 계획은 live 순위나 시간 추정으로 gate를 바꾸지 않는다.

## 2. 담당·산출물·실행 순서

| 단계 | 담당 | 산출물/종료 조건 | 다음 단계 허용 범위 |
|---|---|---|---|
| A. 문서 준비 | Claude 카드 / Codex Coordinator | EXP-013 6개 지적 반영·반박 근거, 카드 SHA/HYP 갱신. EXP-011 금지 문구 범위와 EXP-013 §G를 아래 경로와 일치시키는 owner 수정안 | 문서 검토만. 지금은 이 단계의 변경안 작성까지 |
| B. EXP-011 준비·진단 | Codex 구현 / 별도 reviewer 검증 | 별도 실행 지시 후 계측만 수정, fixtures, card·runner·manifest SHA freeze, 기존13경기 재실행, D1~D4/R 및 class 판정, 독립 결과 검토 | 승인받은 diagnostic만. agent tar 불변 |
| C. 결과 분기 | Claude 판정 기록 / Coordinator 범위 확인 | 아래 판정표대로 후속 카드의 허용 범위·blocker 기록 | EXP-013 자동 실행 없음 |
| D. EXP-013 제한 실험 | Claude 정본 / Codex 구현 / 별도 reviewer / 사람 승인 | 카드 계약 수정 완료, 범위 충돌 해소, 사람의 exact-card 실행 승인. candidate 구현·unit 검증 후 candidate/runner/상대 SHA freeze 및 독립 구현 검토. G0b parent 재기록→candidate 동일13경기. 16 record씩 | diagnostic 결과만. 새 전략·release 허가 아님 |
| E. 후속 판단 | Coordinator / Claude / reviewer | G4 improvement의 n=1 한계 유지. 후속 평가 또는 다른 repair의 별도 카드·승인. 새 전략은 actual parent preflight PASS 후 | 날짜나 bank 개선만으로 승격 금지 |
| F. release | Codex / 독립 reviewer / 사람 | 최종 exact artifact의 전체 release gate, 성능 gate, FIFO 영향 확인·제출 승인 | 여기서만 제출 가능 |

A의 EXP-013 문서 수정은 B와 독립적으로 진행할 수 있다. B와 D의 tools/instrument.py 변경·실행을 병렬로 진행하지 않는다. EXP-011용 runner를 commit/hash로 고정하고, EXP-013 확장은 별도 commit 및 baseline을 쓴다. 먼저 기록한 결과를 새 runner 결과라고 재사용하지 않는다.

## 3. EXP-011 판정별 EXP-013 경로

| EXP-011 판정 | EXP-012 | EXP-013 |
|---|---|---|
| 미실행 / INVALID / D1~D4 또는 R 실패 | 실행 금지 | 대기. 계측/identity 문제를 먼저 해결. 실패한 자료로 scope 결정 금지 |
| 유효 + REPAIR_AUTHORIZED | 카드가 허용한 shed repair 하나의 설계 자격만 획득 | 자동 승인 아님. HIRE failure가 별도 근거를 가진다는 scope 검토 후 사람 승인으로 제한 실험 가능하도록 제안 |
| 유효 + BLOCKED_AMBIGUOUS_ROOT_CAUSE | shed 원인 미확정이므로 금지 | 독립적인 HIRE 근거에 한한 실험 허용 여부를 별도 결정. EXP-011 모호성을 HIRE 실패의 원인 규명으로 간주하지 않는다. owner가 금지 문구를 shed 경로로 한정하고 사람이 scope를 승인하기 전 대기 |
| 유효 + BLOCKED_STRATEGY_BOUNDARY | fixed를 넘는 shed repair 금지, 사람 이관 | 자동 우회 금지. EXP-013도 지연 route로 행동을 바꾸므로 별도 bounded 행동 실험임을 공개해 검토. 금지 범위 owner 정정과 명시적 scope 승인 전 대기 |

**공통 충돌:** EXP-011 §D의 'REPAIR_AUTHORIZED가 아니면 어떤 구현 card도 승인하지 않는다'는 문구는 넓다. Coordinator가 이를 묵시적으로 무시하지 않는다. Claude가 '이 attribution에서 파생되는 HYP-0031/EXP-012 shed repair'로 한정 가능한지 근거를 남기고, 사람이 해당 범위 해석을 승인해야 위 분기가 적용된다. 수정 전 기존 금지 유지. EXP-011 threshold/class/표본은 변경하지 않는다.

**EXP-012와 EXP-013 순서 제안:** EXP-011 결과 기록 후 계약이 정리된 EXP-013을 다음 제한 실험으로 하고, EXP-012는 별도 설계·승인 전 미실행으로 둔다. REPAIR_AUTHORIZED를 EXP-012 즉시 실행 명령으로 읽지 않는다. 다른 순서를 선택하려면 이유·parent SHA를 실행 전에 명시한다. 두 변경을 합쳐 효과를 측정하지 않는다. parent를 바꾸면 EXP-013 카드를 재동결하고 G0b 기준의 유효성까지 재검토해야 한다.

## 4. BOARD에 반영할 내용

동봉 `BOARD.proposed.md`는 BOARD 위치에 들어갈 전체 문안이며 링크는 그 위치 기준이다. `BOARD.patch`는 현재 정본 SHA를 기준으로 생성한 검토용 diff다. 적용 명령은 실행하지 않았다.

- P1b의 미실행 표기를 VERIFIED_LOCAL_FAILURE로 정정.
- P2의 새 전략 PASS 선행조건은 유지.
- 별도 C0/C1 correctness 단계와 위 분기 원칙 추가.
- HYP-0031/0032를 과거 예약 ID로만 적은 문장을 현재 원장과 맞춤.
- 기존 hosted 수치·일정·release zero gate는 그대로 보존.

BOARD만 고쳐도 EXP-013 §G와 EXP-011 금지 문구가 자동 수정되는 것은 아니다. 카드 owner 정정·검토·사람 승인이 맞춰질 때까지 실행 BLOCKED다.

## 5. 사람이 추후 승인할 정확한 범위 (지금은 미승인)

1. **운영 문서 승인:** 검토한 BOARD 변경안 적용과 bounded correctness 경로 채택. 이것만으로 실험 실행은 허가되지 않는다.
2. **EXP-011 실행 지시:** 검토된 exact card에 따라 계측 구현·검증 및 고정13경기 attribution까지. agent 변경·EXP-012/013·제출 제외.
3. **EXP-013 실행 승인:** 유효한 EXP-011 판정과 scope 해결, 수정 카드의 SHA·독립 설계 검토를 첨부한다. 승인 범위는 candidate 구현/검증 및 artifact·runner freeze·독립 구현 검토를 통과한 뒤 G0b와 고정13경기 비교까지. 조건 미충족이면 중단한다. 후속 pool/public·release·제출은 별도다.

현재 독립 reviewer 담당자는 N/A다. Codex는 Coordinator·integrator를 맡지만 자기 구현 결과의 독립 승인자가 될 수 없다. Claude가 설계한 카드를 Claude 단독으로 최종 승인하지도 않는다. 요청받지 않은 다른 task나 agent는 만들지 않는다.

핵심: '고쳐 볼 허가'와 '제출해도 된다는 판정'을 구분한다. 기존 FAIL을 지우는 것이 아니라 실패를 해결할 제한된 경로를 명확히 한다.


---

## `proposals/codex/20260918-DONOR-MINIMUM-TRANSFER-CHECK.md`

# Donor 경로의 최소 다음 검증 — 설계 BLOCKED

**바꿀 결정:** 아래 고정 stress 두 좌석에서 donor 복사본이 모두 이기면 이 exact donor 경로의 독립 평가 설계를 계속하고, 모두 지면 이 전체 복사 구현만 중단한다. 섞인 결과는 보류한다.

작성: Codex, 2026-09-18. 제안은 한 가지다: **Majkel1337의 단일 frozen 행동 기록을, 원래 상대가 아닌 Remielle stress tape에 대입해 현재 parent와 비교한다.**

**현재 판정: 설계 BLOCKED — K3의 명시적 재검토 조건과 그 조건을 충족하는 ENGINE/HOSTED 근거가 없다. 실행용 donor artifact도 N/A다.** 아래는 결정을 검토하기 위한 수치 초안이지 실행 지시·사전등록·K3 예외가 아니다. 재개 근거가 없으면 이 안은 실행하지 않는다.

- 무엇/왜: 원본 경기 재현 다음에 필요한 것은 다른 시장 경로에서의 결과다. 이미 알려진 parent 패배 한 조건을 사용해 최소 비용으로 전체 복사 경로의 첫 탈락 여부를 결정한다.
- 측정: 이번에는 파일·SHA·기존 결과만 확인했다. 새 경기·candidate 성능은 N/A.
- 막힌 것/다음: K3와 P2 HOLD를 유지한다. 재개 근거가 없는 것을 opening 검사나 HIRE recovery로 이름만 바꾸어 우회하지 않는다.
- 소유 범위: 이 proposal 한 개와 허용된 hypothesis updater 기록만 작성한다. 별도 report/TASKS 행·card·candidate·BOARD·KILLS 변경 없음. EXP/TEST ID를 새로 선점하지 않는다.

## 1. 먼저 확인한 정본과 기존 증거

AGENTS.md, plan/CURRENT.md, coordination/BOARD.md, HYPOTHESES.md, evidence/FACTS.md, evidence/KILLS.md를 읽었다. BOARD는 2026-09-18 갱신이며 HOSTED_LEDGER의 최신 행과 활성 submission 56165718/56175620·09-15 snapshot이 일치한다. BOARD의 원장 갱신 대기 문구 일부는 과거 상태지만 새 제출 충돌은 확인되지 않았다. 이 작업은 사용자가 허용한 proposal 작성이며 P2 실행 승인이 아니다.

요청한 manifest/reproduction/routes/분석기/재현기/P1c 보고서는 모두 실제 경로에서 확인했다. 최신 관련 보완은 `coordination/reports/codex/20260917-1710-DONOR-VALIDATOR.md`; 최초 route 보고서의 assertion 증거 부족은 이 보완과 현재 validation.json으로 연결된다. 이전 memory의 미보완 상태를 현재 사실로 쓰지 않았다.

| 구분 | 이미 확인한 것 | 아직 모르는 것 |
|---|---|---|
| [LOCAL] 원래 경기 재현 | 2026-09-16 22:26 KST snapshot의 donor 2명, 6 views = **5 unique episodes**. episode 109675071은 두 donor가 함께 나온 한 경기다. 각 경기 action 1,438/1,438, state projection 1,440/1,440 및 final rewards 일치; 합계 7,190/7,190·7,200/7,200·5/5 | 양측의 원래 행동·원래 seed/config를 고정한 재현이다. donor의 source policy나 다른 상대 성능을 복원한 것이 아니다. projection은 runtime/overage/info를 제외한다 |
| [HOSTED] Majkel 반복 구간 | 전체 action 공통 prefix 19개, farmer+hands 공통 prefix 25개. index23의 COW2/SHEEP3/MELON6/WHEAT10 배치 반복 | prefix 이후 어떤 상태에서 어떤 행동을 고르는지, 전체 tape가 새 환경에서도 유효한지 |
| [HOSTED] 상태별 차이 | Majkel index25 HIRE8 요청 → 실제 hands4/4/3, index27 세 번째 경기만 추가 HIRE로 3→4. index20의 추가 STRAWBERRY seed 요청은 실제 재고0→0 | 관측된 recovery가 donor 내부 if 규칙이거나 승리 원인이라는 주장. 실패한 요청을 삭제하면 더 강하다는 주장 |
| [HOSTED] M의 분기 | 같은 seat0 두 경기 전체 action prefix25, 첫 차이26은 상점 해금 전. market 544/719 일치는 전부 빈 배열; nonempty 175개 index의 세 경기 일치는0 | 첫 분기가 shop/상대 반응 때문이라는 설명. GOOSE/네 번째 땅과 승리의 동시 관측을 각각의 causal effect로 해석하는 것 |
| [LOCAL]/[N/A] 이전 분석 경계 | P1c bounded 검토가 특정 PLACE/잔여 작물/즉시 DROP 설명을 반박했다 | donor 활용 전체를 반박한 것은 아니다. P1c의 metadata 누락을 이번 donor 경로의 자동 선행 작업으로 삼지 않는다 |

출처: `experiments/results/top10_donor_20260916/donor_manifest.json`의 각 row 및 `reproduction/<episode>.json`; `tools/reproduce_replay.py:14-23,46-91`; `tools/analyze_donor_routes.py:24-39`; `coordination/reports/codex/20260917-1640-DONOR-ROUTES.md` §§2–5; `coordination/reports/codex/20260918-P1C-BOUNDED-EVIDENCE.md` §§한 장 증거표·Artifact 연결.

이번 읽기에서 raw 5개의 실제 SHA와 manifest가 **5/5 일치**했다. reproduction 결과 파일은 재실행하지 않고 읽었다. **과거 snapshot의 rank1/2**이지 현재 top10이라는 주장은 하지 않는다. 다른 seed·shop·시장 압력·상대에서의 donor 복사본 성능은 모두 N/A다.

## 2. K3 판정 — 재개 근거 없음

`evidence/KILLS.md:10`의 현재 원문 전체:

> | K3 | 라이벌의 전체 마켓 테이프 복사 | 큰 일반화 실패 | rayk (남의 실험) | — |

- 기록된 구현 범위는 **라이벌의 전체 마켓 테이프 복사**, 실패 범위는 **큰 일반화 실패**, 출처는 **rayk (남의 실험)**, 재검토 조건은 문자 그대로 **`—`**다.
- K3 행에는 exact source/candidate SHA, seed, 상대, seat, engine version, 실패 수치가 없다. 확인한 관련 계획서(`plan/kaggriculture_docs_insights_claude-opus-5.md:202`, `plan/kaggriculture_master_plan_claude-opus-5.md:205`)도 이 요약을 반복할 뿐이다. **그 상세는 N/A**이며 "market만 바꾼 실험이었다" 같은 좁은 해석을 만들지 않는다.
- 제안한 단일 donor의 farmer+hands+market 전체 재생은 **전체 market 복사를 포함하므로 K3 적용 대상**으로 처리한다. farm도 함께 복사한다는 이유, donor가 달라졌다는 이유, 원래 경기 재현 PASS라는 이유로 예외를 선언할 수 없다. 남의 실패라는 표시는 증거의 출처이지 계약 무효화 사유가 아니다.
- `AGENTS.md` §9는 재검토 조건의 명시적 인용과 그 성립에 대한 **ENGINE 또는 HOSTED** 근거를 요구한다. `—`를 "조건 없음, 자유롭게 재개"로 읽지 않는다. **현재 충족된 재개 조건: 없음.** 원본 양측 재현은 LOCAL이고 donor 원본의 승리는 복사본의 새 상대 성능이 아니므로 둘 다 해제 증거가 아니다.

**필요한 최소 증거 하나:** 기존에 존재하는 자료 중, **전체 market을 복사한 exact artifact와 연결된, 원본 경기가 아닌 다른 상대에서의 HOSTED 성공 사례 1건**. artifact bytes/SHA → submission → episode → 상대 submission/seed/seat/engine이 연결되어야 한다. donor 원본의 승리, 저자 rating, action이 비슷한 replay는 대체할 수 없다. 현재 읽은 inventory·reproduction·route 자료에서 이 증거는 **N/A**다. 이는 owner가 좁은 재검토 조건을 논의할 최소 반례이지 일반화 증명이나 자동 K3 해제가 아니다.

현재 K3에 판정식 자체가 없으므로, 이 증거가 있더라도 owner의 명시적 조건 정의와 사람의 범위 승인 없이는 실행할 수 없다. **그 증거를 만들겠다고 먼저 local 경기나 새 hosted 제출을 실행하는 순환 논리는 금지한다.** 기존 증거를 확보할 수 없으면 이번 전체 복사 안은 BLOCKED로 종료한다. K3 원실험의 상세 실패 artifact가 확인되면 scope를 더 정확히 논의할 수 있지만, 현재 없는 것을 있다고 전제하지 않는다.

## 3. 허용 조건이 먼저 해결될 경우 검토할 단 하나의 stress 비교

### 가설과 선택

[HYPOTHESIS] **Majkel의 하나의 frozen 전체 행동 기록이 donor 개발 표본과 다른 Remielle 시장 경로에서도 현재 parent의 두 패배를 모두 승리로 바꿀 수 있다.** HYP-0010의 donor 활용 가능성에 대한 제한된 탐색 질문이다. top10% 도달/88% rating 회수 가설을 증명하는 시험은 아니다. 별도 HYP가 필요한지는 사전등록 owner가 판단하며 지금은 새 HYP/EXP/TEST를 만들지 않는다. HYP-0013의 원본 재현 PASS와 HYP-0032의 HIRE recovery 결과로 대체하지 않는다.

- donor: **Majkel1337 / submission56156662 / episode109675071 / source seat0**. 개발 manifest의 Majkel 최신 completed public episode를 사용한다. 원본은 패배지만 결과를 보고 승리 tape로 갈아타지 않는다.
- 선택 이유: Majkel의 반복 opening은 양 좌석에서 관측됐다. M의 전체 route에는 K1/K9의 추가 쟁점까지 있으므로 이번 한 비교에 넣지 않는다. 이것이 Majkel 복사본이 더 강하다는 판단은 아니다.
- source raw: `private_artifacts/top10_donor_20260916/episode-109675071-replay.json`, SHA `11758bf6601ff6c14da94f6e62fac4f8f7ba7988f5b79e7c5af8ccdfa9fc4eaa`.
- source donor action stream: manifest `action_sha256=0ec1d7167be1c517ea1f4419b4f2ca698142b106fef1263d8189963f34b76baa`. 719 actions는 `steps[1..719][0].action`을 뜻한다. 이번 읽기에서도 `json.dumps(actions, sort_keys=True, separators=(',', ':')).encode()`의 SHA를 다시 계산해 일치했다. action0을 포함한720개 배열의 hash와 구별한다(`tools/top10_donor_inventory.py:82-88`).
- **실행용 donor artifact/path/SHA: N/A**. raw replay와 action hash는 source identity이며 agent 구현의 SHA가 아니다. 구현·추출물을 이번에 만들지 않는다.

### 바꾸는 요소 하나와 고정 조건

**one_change(나누지 않는 strategy 선택):** 시험할 agent를 parent A의 exact policy에서 위 단일 donor action stream을 고정 재생하는 D로 교체한다. strategy package 비교이며 작물·market·opening 중 무엇이 효과를 냈는지는 식별하지 않는다.

D는 `obs.step=t`에 source `steps[t+1][0].action`을 반환한다. 평가 seat1에서도 source seat0의 같은 action을 쓰며 다른 donor tape로 routing하지 않는다. index20의 실패한 주문·hands 과부족·market 수량을 임의로 고치지 않는다. HIRE recovery·shop router·매도 변경·다른 donor 혼합을 추가하지 않는다. 별도 guard나 fallback을 넣으면 다른 정의가 되므로 이 안을 그대로 실행하지 않는다.

고정할 것은 engine1.32.7의 Python/JSON SHA, 720 rows/719 agent calls, 상대의 exact transcript, seed, 양 seat, initial config, 계측 정의다. configuration은 P1b target의 저장 command/config에서 동결하고 source donor의 seed2116997393으로 되돌리지 않는다.

| 조건 | exact 입력·선정 이유 |
|---|---|
| parent A | `coordination/proposals/claude/exp006/submission.tar.gz` / `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` |
| 유일한 상대 | `private_artifacts/tapes/Remielle_episode-108076177-actions.json` / `75ea188ed138167b274ce34d20ce3476adfcfe25ee75d6feb7ed4e8de7caa5c4`. 반응하는 Remielle 본인이 아니라 고정 transcript |
| seed | **[1125321547]만**. parent의 알려진 패배 조건이며 donor 개발 5경기의 seed에는 없다. donor 결과를 보기 전의 stress 선택이지만 random sample은 아니다 |
| seats | **[0,1]**. 한 좌석의 성공으로 seat 편향을 숨기지 않는다. 같은 seed의 두 seat를 독립된 두 seed로 세지 않는다 |
| cells / 순서 | A vs 상대 seat0, A vs 상대 seat1을 먼저 확인하고 이후 D의 seat0, seat1. **총4경기**. 과거 A 결과만 새 runner의 D와 비교하지 않는다 |
| 기존 baseline | P1b target에서 A=58,246, 상대=167,541, A의 W/D/L=0/0/2. `experiments/results/p1_release_preflight/cells/target_seed-1125321547_seat-{0,1}.json`의 `payload[0]`. 이번에 새로 측정한 값이 아니다 |

이 상대를 고른 이유는 parent가 지는 조건에 직접 답하기 위해서다. starter나 이미 이기는 공개 bot에 대한 평균 bank 증가를 성공으로 삼지 않는다. source donor의 원래 상대·원래 seed를 양측 재생하는 reproduction 반복도 아니다.

### 지표·수치 제안과 종료

먼저 validity를 확인한다: input SHA mismatch0, 4/4셀 존재, 각720 rows, DONE/DONE, uncaught exceptions0. A의 양 seat reward와 기존 counter가 과거 baseline과 다르면 runner/config 차이를 해결할 때까지 **INVALID**다. 이를 D의 패배로 세지 않는다.

primary는 D의 W/D/L, seat별 point score(W=1,D=0.5,L=0), 같은 조건의 A와의 차이다. 수치는 전체 모집단의 승률 임계가 아니라 **알려진 두 seat의 패배를 모두 바꾸었는가**라는 한정된 질문에서 정했다.

| 탐색 판정 제안 | 수치 조건 | 다음 결정 |
|---|---|---|
| success | valid, D=**2/0/0**, 양 seat score 차이 **+1** | 이 exact donor 경로의 독립 평가를 설계할 가치가 있다. 새 실행·release 승인은 아니다 |
| failure | valid, D=**0/0/2**, 양 seat score 차이 **0** | 이 단일 tape 전체 복사를 종료한다. bank 증가만으로 success로 올리지 않는다. donor 활용 전체를 KILL하지 않는다 |
| inconclusive | valid이고 위 둘 외의 결과(좌석별 승패 혼재, draw 포함) | 이번 최소 비교로 전진을 결정하지 않는다. 같은 test에 seed/tape를 추가하지 않는다 |
| INVALID | 누락1 이상, input mismatch1 이상, status/예외/재baseline 불일치 | 성능 판정N/A. 기록하고 멈추며 자동 repair하지 않는다 |

secondary로 seat별 final bank·margin, 두 seat의 패배 횟수·margin 범위, p99 시간, 기존 전체 zero-gate counter와 hands mismatch를 함께 기록한다. `sell_unfilled`는 diagnostic이다. counter0을 회수 가능한 손실0으로 읽지 않으며 새로운 광범위 NOOP 분류 작업으로 확장하지 않는다.

**탐색 판정과 release 판정은 별도로 낸다.** success라도 nonzero counter를 허용한 release PASS로 바꾸지 않는다. release gate의 전부0 조건·현재 parent FAIL·P2 HOLD를 유지한다. correctness 위반이 있는 artifact의 구현 계속이나 제출을 승인하지 않는다. success는 증거를 보존하고 독립 평가의 설계 가능성을 검토한다는 뜻이다.

95% CI로 모집단 우위를 판단하는 것은 **N/A**다. 선택한 한 stress seed/두 seat를 독립 random sample로 취급해 좁은 CI를 만들지 않는다. 기존 승격 CI 조건을 이 작은 표본으로 대신하지 않는다. score 차이0과 넓은 donor 가설의 기각을 구분한다.

전체4셀은 결과에 따라 늘리거나 줄이지 않는다. 유효한 중간 패배로 끊지 않고 고정 셀을 끝낸 뒤 판정한다. failure 후 tape 교체, 표본 추가, market guard/HIRE recovery 추가를 같은 시험에서 하지 않는다. identity 손상이나 실행 불가는 performance failure와 분리해 중단한다.

### 표본과 비용

- 가설 생성: unique episodes **109675071,109668602,109662252,109669865,109668692** 다섯 개 전부. 이미 본 다섯 경기를 holdout으로 바꾸어 부르지 않는다.
- 제안한 stress 평가: **새로운 donor×Remielle×1125321547×seat** 조합이지만 Remielle/seed는 parent와 EXP-008에서 이미 쓴 **재사용 진단 표본**이다. independent holdout이 아니다.
- **독립 평가 표본: 미선정, N/A.** 이번 비교에 섞지 않는다. success 이후 별도로 freeze해야 일반화 평가 설계로 진행할 수 있다.
- 계산량 제안: **4경기×719 calls×2 players=5,752 calls**. 기존 donor reproduction의 wall은 2.92–3.25초/경기, P1b target은 4.058/4.146초/경기다. 기존 가벼운 tape와 비슷하다는 가정 아래 engine 부분 약 **12–20초**, 시작·계측을 포함한 작업용 예상은 **1–5분**이다. 새 adapter 실측은 N/A이며 속도 보장이 아니다. 구현·독립 검증에 드는 사람 시간은 미정이다.
- engine의 episode 상한1,200초를 유지한다. 비용을 줄이려고 승인이나 artifact 동결을 생략하지 않는다. 현재 새 경기0, download0이다.

## 4. 좋은 결과여도 주장할 수 없는 것과 남은 실행 조건

성공해도 현재 top10 상대의 강도, donor 본인과 같은 policy, rating 회수율, 다른 shop/seed/반응형 상대 전체에 대한 우위, 특정 build order 요소의 causal effect, 두 submission의 보완성, 제출 가능성을 주장할 수 없다. 고정 상대는 시장 변화에 맞춰 원래 policy를 바꾸지 않는다. seed가 바뀌면 shop·잡초 조건도 바뀌므로 source의 적응 행동이 부적절해질 수 있다.

실행 전에 필요한 것:

1. **K3:** §2의 ENGINE/HOSTED 근거에 따른 owner 판단과 명시적 재검토 조건. 현재 `—`이므로 미충족이다. 위1건은 검토의 시작점일 뿐이다.
2. **운영 범위:** BOARD의 P2 HOLD가 적용된다. parent preflight PASS 등 기존 조건을 충족하거나 사람이 범위를 명시한 별도 진단을 승인해야 한다. 이 proposal은 어느 쪽도 대신하지 않는다.
3. **실행 identity:** donor 추출물/adapter의 exact path+SHA, index alignment·양 seat·hands 처리의 독립 확인, 공통 runner+config freeze. 기존 `tools/reproduce_replay.py`는 원본 양측 재현기이며 이 A/D 비교를 그대로 실행하는 명령이 아니다. raw hash로 실행 artifact의 부족을 감추지 않는다.
4. **계약:** owner의 정규 card·ID 배정과 독립 review, exact 범위의 사람 실행 승인. 이번에는 card를 쓰지 않는다. 새 ENGINE/HOSTED 자료 수집·download, candidate 구현, 경기, KILL/BOARD 수정, 제출은 현재 승인 밖이다.

그러므로 지금 실행할 CLI를 기재하지 않는다. 수치안이 있어도 **재개 조건과 실행 artifact가 부족한 설계**다. 원본 reproduction을 다시 실행해 부족한 근거를 채웠다고 하지 않는다.

## 5. 이번 검증과 원장 기록

확인한 input SHA:

| artifact | SHA-256 |
|---|---|
| `experiments/results/top10_donor_20260916/donor_manifest.json` | `ae55ea152f56268610e160f9a3f315289ca040456d2bff18bdbee2f883aebcd6` |
| `experiments/results/top10_donor_routes_20260916/analysis.json` | `dc2dce03f20b46e011757cce65366ca987f2a68a79a5b4b6bfcfdc1dabd7b4ac` |
| `experiments/results/top10_donor_routes_20260916/validation.json` | `45edf15dc3d7a719cd713321ba8eff2cdb141c9ebf14cf515931cb0eb5e3a2c8` |
| `tools/reproduce_replay.py` | `9b1e879fda0a3b5a125510e674711af46cced469f9ae601d714247d39580fa29` |
| `tools/analyze_donor_routes.py` | `fc41cb86c3a956fb9726d1ca24542de614cdf6c02644cc0f2729a8f465f1def2` |
| 현재 `tools/instrument.py`(이 비교용으로 미승인된 runner 후보) | `ca64256f941f2098cafc531fc422363c5757995f721b449369ce72877a33fe28` |
| engine `kaggriculture.py` | `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` |
| engine `kaggriculture.json` | `a82c89c1a2315b93f39775d8e025471a01b738647c9772658368ee6b1b6f4867` |

P1b의 과거 계측 runner SHA는 `284dee4c…0629`로 현재와 다르다. 기존 raw counter는 참고 증거로만 재사용하고, 향후 D와 비교할 때는 같은 runner로 A부터 다시 baseline을 기록한다.

기존 HYP-0010의 `다음 행동`에 이 proposal과 BLOCKED 이유를 updater로 기록한다. 기존 `TEST-DONOR-ROUTES-20260917`은 **과거 descriptive 분석의 후속 검토 context**로만 쓰며 새 실험을 그 ID로 등록하지 않는다. HYP status는 SOURCE_CLAIM, local/hosted 결과는 N/A를 유지한다. 새 TEST/EXP/HYP는 배정하지 않는다.

실제로 실행한 검증:

- `python3 tools/validate_hypotheses.py --strict` → **exit0, hypothesis ledger PASS: 32 entries**.
- `python3`의 inline JSON/SHA 읽기 → unique raw **5/5 SHA 일치**, saved reproduction **5/5 PASS** 확인, 선택한 donor의 719-action SHA 일치. engine Python/JSON, parent tar, 상대 tape의 실제 SHA도 위 기록과 일치했다. **reproduction 재실행은 아니다.**
- updater event의 before/after 비교 → 바뀐 필드는 `다음 행동` 하나, SOURCE_CLAIM·local N/A·Hosted N/A 유지. event: `coordination/hypotheses/codex/EVT-2026-09-18T095722.185555+0000-d759426f.json`, SHA `5fd6a432187f4f7ee4bcf6b654d01b68c8e9c5c53eac4ac10fb426454422f5cb`.
- proposal 문장·공백·선택 raw/상대/양 seat 결과 경로 확인 → PASS. 전체 workspace의 `git diff --check`는 기존 타 owner의 discussion/registry trailing whitespace로 exit2였다. 그 파일은 고치지 않았으며 본인 산출물만 별도로 검사한다.
- 코드 변경·경기 실행이 없으므로 engine/game test는 실행하지 않았다. 별도 report는 만들지 않았다. 시작 전부터 변경 중인 HYPOTHESES.md와 타 agent 파일은 선택 commit에 섞지 않는다. 이 proposal과 자신의 immutable event만 commit 대상으로 삼는다.

raw identity 확인을 다시 할 때의 read-only 명령(새 경기·download 없음):

```bash
python3 - <<'PY'
import hashlib, json
from pathlib import Path
rows = json.loads(Path('experiments/results/top10_donor_20260916/donor_manifest.json').read_text())
unique = {r['episode']['id']: r for r in rows}
assert len(rows) == 6 and len(unique) == 5
for r in unique.values():
    assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest() == r['sha256']
print('raw identity PASS: 5 unique episodes')
PY
```

다음 행동 두 가지:
1. K3 owner에게 기존 자료에 §2의 exact HOSTED 반례가 있는지와 `—`로 남은 재검토 조건의 판단을 요청한다. 새 실험부터 실행해 예외를 만들지 않는다.
2. 그 block과 P2 조건이 해소된 경우에만 이 4셀안의 artifact 동결·정규 card·독립 review·별도 실행 승인으로 진행한다. 해소되지 않으면 전체 복사 안을 보류하고 종료한다.


---

## `proposals/codex/20260918-EXP011-ANTIGRAVITY-HANDOFF.md`

# Antigravity 독립 결과 검토 요청용 handoff

사용자가 Antigravity 검토용 자료 준비를 요청했다. 이 파일은 준비된 handoff이며 검토를 실제 전송/완료했다고 주장하지 않는다.

검토 대상: `coordination/reports/codex/20260918-EXP011-RESULT.md`, `experiments/results/p1_shed_attribution/`.
freeze/구현 commit `0a4b10f`, EXP-011 r2 SHA `8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e`.

보고된 결과는 LOCAL ATTRIBUTION PASS, 카드상 REPAIR_AUTHORIZED, release FAIL 유지다. 독립 검토는 아직 PENDING이다. 보고의 PASS를 그대로 받아들이지 말고 raw에서 검산해 달라.

1. freeze.json의 tar·네 member·engine·tape·기존 baseline·runner SHA와13개 argv 확인. P1b와의 차이가 output path 및 계측뿐인지 검토.
2. tools/instrument.py diff를 읽고 unit argument mapping, day/step 정렬, player cursor, EOD reset 전 snapshot, inventory/item iteration 순서, atomic PLANT 이후 last op 수집을 검토.
3. engine `_drop_inventories_to_shed`와 event allocation을 독립 대조. event.day0~28, 총464 events는719 agent calls에 맞는지 확인.
4. raw cells에서16 gated records/13 episodes 및 기존 rewards·9개 counter 동일성 확인. 기존 runner exit2와 EXP-011 verifier exit0을 혼동하지 말 것.
5. D1~D4/R 재계산: 482 units, S1=64/S2=418, 지배class64/416, sole-top16/16, gate 임계 그대로인지 확인.
6. 사후 arithmetic audit는 gate 추가가 아니다. ROOM_PARTIAL은 event 시작의 빈 공간만 뜻한다. 44개 loss event 모두 carried>room이며, 끝의 이월 순서만 바꾸는 방식이 card의 shed_discarded0 목표를 달성할 수 있는지 별도 판단. REMOTE라는 class 자체가 causal effect를 입증하는지 비판적으로 검토.
7. PLACE 보존/DROP 소멸 fixture와 gate에 영향 없는 신규 diagnostic counters 검토. EXP-013 code/counter가 섞이지 않았는지 확인.
8. 판정을 분리: 계측 정확성 / 재현 / 카드 gate / class의 causal 해석 / repair 가능성 / release·hosted 경계. 수정이 필요하면 exact file/line과 재현 방법을 제시.

read-only 재검증: `python3 experiments/results/p1_shed_attribution/run.py --verify-only` (aggregate만 같은 값으로 다시 기록), `python3 experiments/results/p1_shed_attribution/check_allocation.py` (audit JSON 재기록), 또는 raw 직접 독립 스크립트. 원 산출물 변경을 피하려면 복사본에서 실행. 전체13경기 재실행은 원 결과를 덮어쓰지 않는다.

최종 보고는 Antigravity 소유 `coordination/reports/antigravity/`에 별도 파일로 작성하고 확인한 artifact SHA를 적어 달라. EXP-012/013 구현·실행·submission은 이 검토 요청 범위 밖이다.


---

## `proposals/codex/20260918-EXP011-CLOSURE-PRIORITY.md`

# EXP-011 종결 및 다음 우선순위 — Coordinator 판정

## 수용

Antigravity cb4f4c9e4b1171a0424b678eaef4d72d0d0993853d43d192c7ce0655ed689e1d 보고와 Claude owner adjudication을 확인했다. 이번에도 raw13 files/26 player records의 rewards/statuses/steps 및9 counters를 assert로 대조해 mismatch0을 확인했다. aggregate SHA22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba, current card r3 SHAe47bb87b5aa2813f99105ac0e9d357c956c528ac823ae39010f02381d88fbe32.

측정 PASS/독립 검토 완료. 측정 당시 카드 라벨 REPAIR_AUTHORIZED는 역사적 결과로 보존한다. 허용된 최종 이월 순서/클램프 변경으로 총 소멸을0으로 만드는 EXP-012는 사전등록 불가로 종결한다. 이는 shed 관련 모든 전략을 기각하는 것이 아니다. EXP-013은 여전히 별도 근거·검토·승인이 필요하다.

## owner 정정 제안 — 다음 우선순위의 근거로 쓰지 말 것

1. **19,200은 검증된 상한이 아니다.** FACTS F-T16은 209 units × 전체 실현 매도 평균단가92.0을 사용한다. 소멸 item 구성·판매 가능 시점·당시 marginal price가 같다는 근거 없이 평균을 최대 단가로 사용할 수 없다. 추가 매도가 이후 가격/현금/생산을 바꿀 수 있으므로 직접 환산치도 전체 causal loss의 상한이 아니다. '최대19,200'→'기존 평균단가를 사용한 거친 환산 약19,200; 엄밀한 상한 N/A' 정정 제안. F-T17의 '50판 중1판만 뒤집힘'도 실제 경기별 회수 counterfactual이 아니라 이 가정의 산술 시나리오로 한정해야 한다. HYP-0032의 'shed 주원인 배제' 표현은 확정 근거로 유지하지 않는다.
2. **3,488 actions와482 items는 다른 단위다.** 7.2배는 전략 가치·회수 가능 coin·기대 승률의 비교가 아니다. no-op reason은 useful diagnostic이 될 수 있지만 그 수치로 최우선이라고 결론낼 수 없다.
3. **no-op은 모두 PASS 치환이 아니다.** instrument의 tile/inventory 변화 없음 판정은 실행 무효/불필요한 요청을 함께 포함한다. 예 이미 충분히 돌본 동물의 CARE는 PASS 치환 없이 상태변화가 없을 수 있다. atomic seed-blocked PLANT와 reason taxonomy를 분리해야 한다.
4. **기존 계측 재현은 다음 계측의 무개입을 보장하지 않는다.** 새 reason hook도 tests·runner SHA freeze·parent exact 재현이 필요하다. '제출 위험0'은 artifact를 제출하지 않는 현재 범위의 설명으로만 사용한다.
5. **EXP-014 번호를 noop으로 선점하지 않는다.** EXP-013 r3가 이미 후속 pool/public 카드로 언급한다. 설계 필요가 확정되면 원장을 대조해 충돌 없는 ID를 배정한다.

## 우선순위 제안 (미실행)

새 noop 카드부터 만드는 것은 보류한다. 다음 의사결정 자료는 P1c의 같은 최신 window 내 패배/무승부와 실제 failure 연결이다. 점수 격차716이나09-12표본, 타 artifact의2169점을 현재값처럼 비교하지 않는다. 최신 조회는 이번에 실행하지 않았으며 N/A다.

동일한 비교표로 HIRE failure, actionable no-op, 접전·무승부를 정리한다: 해당 경기 수/분모, 최초 관측 시점, 분기 이후 손실 경로, 정확한 artifact/submission, 실패 예시, 변경 범위, 검증 비용. 인과 미확정은 표시한다. HIRE 문제가 반복되면 EXP-013의 제한 실험을 우선 검토하고, 특정 no-op이 실패와 연결되면 그 reason만 다루는 diagnostic을 사전등록한다. broad noop count만으로 순서를 정하지 않는다.

P1c 수집 없이 당장 카드 하나를 고르라는 별도 지시가 있다면 EXP-013을 검토 우선 후보로 둔다. 이유는 이미 hosted failure 연결과 구체 카드가 있기 때문이지 효과가 입증됐기 때문은 아니다. 현재는 그 지시도 실행 승인도 없으므로 구현하지 않는다.

## provenance 주의

freeze.json은 측정 당시 r2 card SHA를 고정한다. owner가 r3 정정 이력을 추가한 뒤 원래 run.py --verify-only를 live checkout에서 실행하면 card identity mismatch가 나는 것이 정상이다. freeze를 r3 SHA로 덮어쓰지 않는다. 재현 검토는 freeze commit0a4b10f의 r2 파일을 별도 checkout/복사본에 복원해 실행하거나 측정 당시 SHA와 현재 정정 문서를 분리해 확인한다. 이 문서 작업은 원 aggregate와 runner를 재실행/변경하지 않았다.


---

## `proposals/codex/20260918-EXP011-OWNER-CORRECTIONS.md`

# Claude owner에게 — EXP-011 사실 정정 및 결과 인수 제안

원 카드 r2와 thresholds는 측정 당시 그대로 보존한다. 새 결과는 `coordination/reports/codex/20260918-EXP011-RESULT.md`와 결과 폴더에 있다. FACTS/cards는 Codex가 직접 수정하지 않았다.

1. card §A PLACE 서술: engine1.32.7 `kaggriculture.py:393-411`은 room만큼 n을 낮춘 뒤 그 양만 inventory에서 차감한다. DROP(:344-355)와 달리 초과분은 버리지 않는다. fixture `tests/test_instrument_exp011.py::test_drop_discards_but_place_retains_overflow_and_animal_is_not_loss`로 확인. 정정일·근거를 붙여 owner 문서에 정정 이력 추가 제안.
2. card §D ROOM_PARTIAL 해석: frozen 분류는 event 시작의 room>0을 뜻한다. carried<=room을 뜻하지 않는다. 예 target day15: room45,carried51,loss6. 카드상 REPAIR_AUTHORIZED를 그대로 기록하되 '여유가 있는데도 이월 실패'를 capacity가 충분한 상태에서의 구현 오류로 해석하지 말 것. 이월순서만 변경해 총 loss0이 가능하다는 증거 없음. EXP-012 구현은 승인되지 않았다.
3. §D-1 사용자 범위 승인 표는 `coordination/reports/codex/20260918-EXP011-AUTHORIZATION.md`를 근거로 owner가 반영 가능. 기존 측정 card SHA는 보존. 신규 revision SHA가 결과의 과거 card SHA를 대체하지 않게 명시.
4. FACTS 추가 제안 [LOCAL]: fixed13 episodes/16 parent records baseline reward·counter exact, attribution482, C*=ROOM_PARTIAL|REMOTE|NO_DEPOSIT_ATTEMPT S1=64/64,S2=416/418,sole-top16/16. 실험 효과/hosted 강도 증거 아님. 재현: `python3 experiments/results/p1_shed_attribution/run.py --verify-only`.
5. 결과 registry 반영은 owner가 수행. HYP-0031은 Codex updater event로 LOCAL_SUPPORTED(attribution only), 독립 Antigravity 검토 대기. EXP-013은 미구현·미실행.


---

## `proposals/codex/20260918-P1C-BOUNDED-CLOSURE-GEMINI.md`

# P1c 제한 검토 종결 — Gemini owner exact 정정안

대상: `coordination/reports/gemini/20260918-P1C-ANALYSIS.md`

직접 수정하지 않는다. Gemini owner는 아래 문구로 기존 요약·경로표·접전표·최종 제안의 상충 부분을 교체한다.

## 교체 문구

```text
VERDICT | P1c 제한 검토 종료 — 이 자료에서 실행 가능한 수정 가설 미확보 | coordination/reports/codex/20260918-P1C-BOUNDED-EVIDENCE.md; experiments/results/p1c_20260918_audit/bounded_evidence_assertions.json | 32/32 assertions PASS | NEXT ACTION: 새 수정 카드 자동 생성 없음

[HOSTED raw 관측] 저장된 77개 replay는 W24/D1/L52이며, HIRE 미체결은 패배 3경기의 13주문에서 관측됐다. 이 빈도는 HIRE가 패배의 주원인이 아니라는 causal 결론도, state-conditioned HIRE recovery 전체의 기각도 증명하지 않는다.

[MEASUREMENT LIMIT] 기존 True NOOP 집계는 whole-turn projection을 사용해 다른 unit의 shared-state 변화가 있으면 실제 무효 action을 누락하고, blocked move를 포함하며, farmer를 검사하지 않는다. 따라서 77/77 및 2,670건을 엄밀한 개별 실패 빈도로 사용하지 않는다. 전체 실제 빈도는 N/A이며 이번 제한 검토에서 재계측하지 않았다.

[REFUTED] 110106409 action718과 109802471 action718의 PLACE MILK는 실패하지 않았다. 고정 엔진의 unit-stage 검산에서 각각 MILK 3과 15가 shed에 예치됐고 raw post-state와 일치했다. PLACE→DROP을 이 두 경기의 실패 수리로 제안하지 않는다.

[REFUTED] 109831239의 STRAWBERRY 5와 WHEAT 3은 방치되지 않았다. action718의 실제 10칸 market order 안에 SELL STRAWBERRY999와 SELL WHEAT9가 있었고 raw post-state에서 0/0이다. 211coin을 최종 bank에 더하는 역전 계산은 이미 판매된 재고의 이중 계산이다.

[REFUTED / EFFECT N/A] 109856629 action718 직전 WOOL/MILK/EGG 운반자 위치 [3,5], [5,3], [6,4]는 모두 shed access 밖이므로 같은 action에 즉시 DROP 후 판매할 수 없다. 719의 WOOL price 154→31은 관측이지만, 154 고정 체결이나 +2,100coin 역전 효과는 N/A다. 더 이른 경로 변경은 이번 검토 범위 밖이다.

[REFUTED / EFFECT N/A] 109802471은 action718 직전 이미 bank 117682 대 118101로 419coin 뒤져 있었다. 직후 수입은 4241 대 4244로 margin 변화는 -3이다. 단일 PLACE 실패가 422coin 패배를 만들었다는 설명은 반박됐다.

[OBSERVED, NOT ACTIONABLE] 109831239 최종 WOOL 2개 잔여는 raw replay에서 확인됐다. 그러나 episode seat1을 exact submission ID와 source artifact에 연결할 metadata가 없어 수정할 코드와 효과는 N/A다. 종료 price 1에서의 단순 2coin도 -92 역전 근거가 아니다.

[PROVENANCE] exact collection window, episode→submission ID, upload artifact SHA 연결은 N/A다. 이 identity 한계는 각 raw SHA에 고정된 action 전 observation→issued action→action 후 observation 자체를 무효화하지 않는다. raw 관측과 source identity를 별도 열로 유지한다.

[SCOPE] 위 판정은 PLACE MILK 실패, STRAWBERRY/WHEAT 방치, 즉시 DROP 역전이라는 특정 설명만 반박한다. HIRE recovery, 접전 개선, donor 전략 전체를 기각하지 않는다. 109831239 metadata 확보는 유용한 미래 입력일 수 있지만 자동 최우선 작업으로 등록하지 않는다. P2/release gate와 EXP-013 미승인 상태는 그대로다.
```

## 삭제하거나 철회할 문구

- `HIRE 실패는 패배의 주요 인과 관계가 아니다. 추가 검증 대상에서 제외한다.`
- `True NOOP 77/77`과 `2,670건`을 엄밀한 실패 빈도로 단정하는 모든 문구
- `무효한 PLACE 액션 버그`, `STRAWBERRY/WHEAT 방치`, `즉시 DROP`, `+2,100`, `211coin 확보`, `정확히 422coin 손실`을 confirmed fact 또는 실행 가능한 수정 가설로 쓰는 모든 문구
- `[HYP-001] 종반 청산 로직 강화`와 그 자동 우선순위·실험 카드 추천
- 109831239 metadata 수집을 자동 NEXT ACTION 또는 최우선 작업으로 등록하는 문구

## 근거

- `coordination/reports/codex/20260918-P1C-BOUNDED-EVIDENCE.md`
- `experiments/results/p1c_20260918_audit/bounded_evidence_assertions.json`
- `tools/verify_p1c_bounded_evidence.py`
- commit `f64e37a24eeb052a9e5fa71cc2c9875d43e8f0b2`

새 분석·경기·candidate·metadata 수집 없이 문서 정정만 수행한다.


---

## `proposals/codex/20260918-P1C-GEMINI-CORRECTIONS.md`

# Gemini / Claude owner corrections

근거: coordination/reports/codex/20260918-P1C-AUDIT-VERIFY-GUARD.md 및 experiments/results/p1c_20260918_audit/replay_audit.json.

Gemini에게 전달할 작업 지시:

P1c 원자료와 Codex audit을 읽고 기존 보고서를 정정하라. 새 실험·전략 구현·제출은 하지 않는다.
1. 77개 episode 각각의 submission ID, 완료 UTC, 수집 endpoint/명령, source response 경로와 SHA를 연결하라. 저장된 metadata가 없으면 수집 당시 정확한 window 검증은 N/A로 남기고 재조회 결과를 과거 snapshot처럼 쓰지 마라.
2. steps[i-1].observation → steps[i].action → steps[i].observation 정렬로 다시 계산하라. HIRE 실패는 W0/24, D0/1, L3/52 및 총13건이라는 audit 결과와 원자료를 대조하라. 110024392 row2 성공과 다른 턴의 실제 실패를 구분하라.
3. NOOP은 PASS 치환과 구분하고 측정 가능한 정의를 먼저 명시하라. tile 서명/재고 총량 proxy, 이동 실패, seed-blocked PLANT를 섞지 마라. 사용한 parser와 실행 명령을 보존하라. 기존 100% 결론은 재검증 전 보류한다.
4. 접전 마진0/-10/-92/-422를 정정하고 작은 마진은 개입 효과의 증거가 아니라고 명시하라. 자료 정정 후 네 경기의 분기 시점과 합법적인 대안 action을 관측/가설로 나눠 표로 정리하라. counterfactual 경기 실행은 하지 않는다.
5. analysis/와 본인 보고서에 정정 이력을 남기고 다른 owner 파일은 proposal로 넘겨라.

Claude에게 전달할 작업 지시:
Codex guard 보고서를 인수하고 FACTS의 verify-only 경고에 수정 이후의 read-only 동작을 구분해 기록하라. 역사적 runner/freeze SHA와 측정 결과는 보존한다. 현재 live verifier의 INVALID는 provenance drift이며 역사적 aggregate 변경이 아님을 명시하라. P1c 우선순위는 정정된 자료 검토 전 확정하지 않는다. EXP-013 구현·실행과 새 카드 사전등록은 이번 지시에 포함하지 않는다.


---

## `proposals/codex/20260925-DP-LOSS-RESULT-INTEGRATION.md`

# Coordinator / evidence owner 인계 — EXP-018

요청: BOARD와 FACTS의 해당 owner가 아래 완료 결과를 반영한다. Codex는 소유 문서를 직접 고치지 않았다. 제출 지시가 아니다.

- `[LOCAL]` DP 0924 기존 `_V92_P_EVERY` 3→2 후보의 유효 hosted 복제 패널47개: 부모23승/0무/24패 → 후보28승/0무/19패. Δ0.1063829787 > 2SE0.0909207206, 기존 승리의 새 패배0.
- `[LOCAL]` 필수 DP 직접80경기(seed2400–2439 양좌석):22승/34무/24패,39/80=0.4875<0.50. **최종 SUCCESS 및 B-2 불가. 추천 없음.** 패널 단독 SUCCESS를 최종 SUCCESS로 기록하면 안 된다.
- 판정: **VERIFIED_NOT_ELIGIBLE_DP_FLOOR**. 오류에 의한 BLOCKED가 아니라 유효한 필수 gate 실패다. 하한·seed·표본 수 변경 없음.
- Q2 first candidate가3flip 조건을 충족했으므로 사전등록 carrot fallback은 미실행. 이후 DP 하한 실패를 이유로 뒤늦게 실행하지 않는다.
- Q5 공개 exact 추천 없음. herd-safe는 지시대로 상성 상대만. pipe18은 유효 FULL DP2승2패, 팀LB 중앙값2305.0으로 외부 DP7팀 중앙값2435.9보다 낮다. 단일 높은 팀2466.5만으로 추천하지 않는다.
- 입력 정정: FULL59는 제외 submission56502662의12경기(5L/7W)를 포함했다. 상단 제외 지시 적용 후 유효47(24L/23W). 전체59목록과 제외12를 freeze에 보존했다.
- Runtime max0.127131917s, exceptions0. 부모47의1438 actions/1440 states씩 원본과 일치. 별도 재계산2039 checks PASS.
- release/tar/E-5 isolation은 N/A: 후보 미채택으로 release 미생성. Kaggle 다운로드·제출 없음.

보고: `coordination/reports/codex/20260925-1340-DP-LOSS-CAUSE.md`.
원자료: `analysis/exp018_panel/summary.json`, `experiments/results/dp_loss_cause_20260925/verification.json`.
재현 검산: `python3 tools/verify_dp_loss_results.py`.

- 카드 `experiments/cards/EXP-018-dp0924-single-factor.md` SHA `f2eaac36d5f002316692e2265b95d4b79bc54755563587be426a2a6a32c58686`.
- 후보 `experiments/candidates/exp018_dp0924/refresh/main.py` SHA `f3e727b175eac13b702c3de34191b2cff170e30220bcb108b1010fc782505052`.
- freeze SHA `12704c262374b21c52507a7cb5aa08d18a89b6ba27f089b2c0e712ead214bcd2`, 2026-09-24T15:59:43.720643+00:00, 실행 전 기록.

다음 두 행동: ① BOARD에 gate 실패/후보 미채택 및 Q5 없음 반영. ② 현재 DP의 새 hosted snapshot과 새 공개 계열을 다음 판단 근거로 삼되, 이 카드의 사후 기준 변경·seed 추가·fallback 실행으로 우회하지 않기.


---

## `proposals/codex/20260925-NEWMETA-EXACT-OWNER-SYNC.md`

# NEWMETA-EXACT owner 기록 제안

[LOCAL] 1단계 결과 NOT_ELIGIBLE. Exact main SHA127ed3e6…c652와 CRLF7482개, tar의 main.py 단독 바이트 일치. DP80=66/0/14, panel47=42/0/5, worker6 고정1000경기 예외/비정상0. 연속2094.187초, 초기1584→마지막1776games/h, worker5 비교 조건 불발. 최대step0.750587초가필수0.25초미만을 넘었다. p99는 game별p99의 최댓값0.044139초. Threshold 완화/재실행 없음.

정본 보고: coordination/reports/codex/20260925-1846-NEWMETA-EXACT.md.
원자료와 재현: experiments/search_20260925/stage1-games.jsonl; python3 tools/verify_search_stage1.py (8074checksPASS).

Claude owner가 필요시 FACTS/BOARD에 위 제한된 결과와1b진행 상태를 반영한다. 코드가 빠른 일반적인 경기들의 성과만으로 worst-step gate 실패를 지우지 않는다. 제출하지 않았다.


---

## `proposals/codex/20260928-TOP2400-EXECUTION-HANDOFF.md`

# TOP2400 external execution handoff — 2026-09-28 16:56 KST

1. **시험:** d157이 이미 내보내는 인접한 WHEAT 매수·매도 주문의 순서만 바꾸는 한 요인 후보를 고정했다.
2. **이유:** 선택 팀 상대 d157 20패의 원본 replay를 같은 엔진으로 재생해 20/20 상태 일치를 확인했다. 상위 상대의 실제 WHEAT 매수/매도는 30,891/35,298개, d157은 6,687/10,920개였다. 요청량과 체결량을 구분했다.
3. **측정:** 단일 worker smoke 40/40 DONE, 719 action, 오류 0; 두 arm의 action SHA가 달라진 episode 8/20, 승패 flip 0/20; candidate 최대 턴 0.495165초. 이는 선택 팀 전체 승격 결과가 아니다.
4. **다음:** Claude/Antigravity는 아래 고정 jobs를 실행하고 결과 파일을 지정 경로에 둔다. holdout은 select 판정 통과 뒤에만 실행·판독한다. Codex가 09-29 06:00/15:00 KST에 보고한다. 제출·다운로드·후보 재튜닝은 금지다.

`PENDING_EXTERNAL_EXECUTION` | parent `releases/exp035-d157/main.py` SHA-256 `94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e` | candidate `experiments/top2400_codex/d157_order_swap.py` SHA-256 `320f8bc92726d163e1d6569d8c664c66a5df270e6081236cc6fb5fc6bbd451cf` | prereg SHA-256 `578f171b6b14b22050f73c275666d901ac0bee97117f9f8aad33d052c008be8d` | NEXT: external select + panel jobs.

## 고정 입력과 순서

| panel | jobs | SHA-256 | games | expected result |
|---|---|---|---:|---|
| select | `experiments/top2400_codex/jobs-select.json` | `00bb6f5b2f549afd0d37b3046b55c8fac663dc2d088db5de0902a8755e7c44d3` | 1190 | `games-select.jsonl` |
| U | `experiments/top2400_codex/jobs-u.json` | `eaf4b96215c3a1cbc889ad7b2f6ff3a1f7d917bdeb18d865af2a3f248f7c7fc8` | 272 | `games-u.jsonl` |
| T | `experiments/top2400_codex/jobs-t.json` | `73b9ee1264b68e37c704a072616ac3122ce446495f553470624babfbd8378195` | 700 | `games-t.jsonl` |
| family | `experiments/top2400_codex/jobs-family.json` | `eaab5fdedef561e4ef3de26456d509b599beba14cb5fdcb3fc066efe8b9773e4` | 500 | `games-family.jsonl` |
| O127/V074 | `experiments/top2400_codex/jobs-guard.json` | `1e366a95b577d59392f7968e815bcbe5bce8c348b2b75b86758d38838db38e5f` | 200 | `games-guard.jsonl` |
| holdout, last | `experiments/top2400_codex/jobs-holdout.json` | `06d68c188af9cea97d670fb428da50e3a0de816a3f61d94a2d28b60408a0f2d8` | 296 | `games-holdout.jsonl` |

All output files live in `experiments/top2400_codex/`. They use the same JSONL schema as `experiments/exp024_round2/run.py`. Validate input paths and SHA from `experiments/top2400_codex/input-manifest.json`. Every result key must be unique and each arm must have the same episode/seed/seat. Do not substitute a previous EXP-039/042 baseline row; rerun d157 paired to the candidate as listed. The judge checks exact prereg/candidate/job SHA, completeness, DONE/DONE, 719 actions and agent errors.

After `games-select.jsonl` is complete, use `python3 experiments/top2400_codex/judge.py` to apply the frozen 10,000-resample lower95 > 0 gate. If it fails, do not execute or open the 5-team holdout results. If it passes, execute `jobs-holdout.json`, then run the same judge on all complete panels. The panel gates and no-submit boundary are in `experiments/top2400_codex/prereg.json`; do not edit them.

`[LOCAL]` Exact 20-loss analysis: `experiments/top2400_codex/select_loss_fills.jsonl` and `select_loss_summary.json`, generated by `python3 experiments/top2400_codex/replay_fills.py` and `python3 experiments/top2400_codex/summarize_fills.py`. One loss postmortem is `experiments/top2400_codex/postmortem-114420421.json` (step 359/day 14 gap change −6113; final margin −13829). These 20 losses exclude all five holdout teams.


---

## `proposals/codex/BRIEF_exp001_rerun.md`

# KAGRI-012 — EXP-001 stage 2·3 재실행 (선행 작업, 먼저 이것부터)

담당: Codex · 우선순위: **P0** · 예상: 30~40분

## 왜 다시 하나

`experiments/results/` 의 6건이 현재 `main.py` 가 존재하기 **전**에 생성되었다.
재현을 시도했더니 실패했다:

```
저장값 v1_carrots_5_vs_15.json : paired 0.5, W/D/L 0/40/0, mean_margin 0.0
현재 코드 재실행 (arena, 2시드) : paired 0.0, W/D/L 0/0/4, mean_margin -3,972
seed=1000 단일 게임            : carrots_5 21,312  vs  carrots_15 25,377
```

사전등록 tie-break 는 전부 동점일 때 `(4) 비용이 낮은 쪽` 을 고른다.
저장값을 그대로 채택하면 **carrots=5 가 승격되는데 실측은 carrots=15 가 약 4,000 우위**다.
정확히 반대로 작동한다. 상세: `coordination/reports/claude/20260907-0555-EXP001-stale-artifact.md`

## 할 일

1. `experiments/results/` 의 아래 6건을 `experiments/results/_invalid/` 로 이동한다.
   삭제하지 말고 이동만 한다. `_INVALID.md` 는 그대로 둔다.
   - `v1_workers_9_vs_10.json`, `v1_workers_9_vs_12.json`, `v1_workers_10_vs_12.json`
   - `v1_carrots_5_vs_8.json`, `v1_carrots_5_vs_15.json`, `v1_carrots_8_vs_15.json`

2. **stage 1 은 재실행하지 않는다.** `v1_timing_*_rerun.json` 이 초판과 수치가 완전히 일치해
   재현이 확인되었다. 선택값 확정: **prior = NE day 6, SW day 10**.
   이 값은 Gemini KAGRI-006 프로파일에서 상위 봇 4개가 전원 step 161 / 241 에 매입한 것과 일치한다.

3. 현재 `main.py` (sha `b0c32e1a181e9308c05046b10d618258397c4088e21025ba78346aaa9ac25ddf`) 로
   **stage 2 (workers 9 / 10 / 12) round-robin 재실행**. 시드·좌석은 EXP-001 카드 그대로
   (`1000..1019`, 양 좌석, 40경기/비교).

4. stage 2 선택 뒤 **stage 3 (carrots 5 / 8 / 15) 재실행**. 같은 조건.

5. `tools/arena.py` 를 고쳐서 결과 JSON 에 다음 3개 필드를 반드시 기록하게 한다:
   - `parent_sha256` — 실행 시점 `main.py` 의 sha256
   - `agent_a_sha256`, `agent_b_sha256` — wrapper 파일의 sha256
   - `engine_sha256` — `kaggriculture.py` 의 sha256
   wrapper 안의 `assert` 만으로는 *결과가 언제 만들어졌는지* 를 막지 못한다.
   이번 사고의 직접 원인이다.

## 보고

`coordination/reports/codex/YYYYMMDD-HHMM-KAGRI-012.md` 에
VERDICT / 각 stage 선택값 / 재실행한 결과 파일 경로 / arena.py 변경 diff 요약.

**stage 3 까지 끝나면 v1 은 로컬 gate 통과만 확인하고 멈춘다. 제출하지 않는다.**
이유는 `BRIEF_exp002_animals.md` §0 에 있다.


---

## `proposals/codex/BRIEF_exp002_animals.md`

# ⛔ 폐기 — `BRIEF_exp004_animals.md` 로 전면 재작성됨 (2026-09-10)

> `evidence/PASS_DIAGNOSIS.md` 로 동물의 역할이 재정의되었다(수익원 → 액션 흡수 장치).
> parent 도 바뀌었다. **이 파일을 따르지 마라.**

---

# KAGRI-013 — EXP-003 사전등록: 동물 · 비료 레이어 (v3)

> **[2026-09-07 순서 변경]** 이 카드는 이제 **KAGRI-015(작물 교체) 다음**이다.
> 부검 결과 STRAWBERRY·MELON 은 새 액션 타입 없이 타일당 4~5배가 나올 수 있고,
> MELON 단가(248.8)는 동물 산물(WOOL 192.8, MILK 140.1)보다도 높다.
> 싸고 위험 낮은 축을 먼저 측정해야 동물의 순효과를 분리할 수 있다.
> 근거: `evidence/POSTMORTEM_4bots.md` §3, 브리프 `BRIEF_exp002_crops.md`
> parent 는 v1 이 아니라 **KAGRI-016 의 승자**다.
>
> **[2026-09-09 재조정]** 순서가 한 번 더 밀렸다: KAGRI-016(시장 실행)이 앞선다.
> 측정된 실행 손실 상한이 MELON 단일 품목만으로 38,164 이고 새 액션 타입이 0개다.
> 근거: `evidence/MARKET_EXECUTION.md`
> 본문의 "실패 시 v1 유지" 조항은 *더 나빠졌을 때*를 뜻한다.
> 승격 실패라도 탐색 지표가 전진했으면 그 승자를 parent 로 채택한다.

담당: Codex · 우선순위: **P0 (KAGRI-012 직후)** · 선행: KAGRI-012 완료

---

## 0. 왜 v1 을 제출하지 않고 v2 로 가나 `[HOSTED]`

2026-09-07 06:20 UTC 관측:

| 항목 | 값 |
|---|---|
| v0 validation | ✅ Success |
| v0 레이팅 | **314.8** (신규 제출 기본값 600에서 2시간 만에 하락) |
| v0 순위 | **6,989 / 7,963** |
| 10위 상금 경계 | **2,764.0** |
| 1위 | 2,850.6 |

에러가 아니라 **정상 플레이하며 거의 전패**했다는 뜻이다.
Gemini KAGRI-006 프로파일과 일치한다 — 같은 상대(starter) 기준 상위 봇 105k~136k, v0 17k.
v1(토지 3구획 + 일꾼 9명)로 314.8 → 2,764.0 을 메울 수 없다.
**제출 슬롯은 5회 중 1회 사용, 남은 4회는 동물 레이어가 들어간 v2 이후에만 쓴다.**

---

## 1. 근거가 되는 엔진 사실

전부 `evidence/ENGINE_ANIMALS.md` 에 줄번호와 함께 있다. **읽고 시작할 것.**
설계에 직접 영향을 주는 5가지만 여기 옮긴다.

1. **`BUILD_COOP` / `BUILD_PASTURE` 는 비용 0** (kaggriculture.py:493-503).
   구조물은 공짜다. 드는 것은 빈 타일 1칸과 유닛 액션 1회뿐이다.
2. **유닛은 턴당 액션 1개** (935-939). 동물 1마리 유지에 FEED + CARE + HARVEST +
   COLLECT_FERTILIZER = 최대 4 유닛-액션/일. **이것이 일꾼 12~14명이 필요한 이유다.**
   KAGRI-012 의 stage 2 에서 hands=9 가 12를 이긴 것은 *할 일이 없어서*이지
   일꾼이 비싸서가 아니다. 동물이 들어오면 최적 일꾼 수는 반드시 올라간다.
3. **2일 연속 미급여 → 동물 영구 소실, 예외 없음** (817-820).
   FEED 는 그 유닛 인벤토리의 밀 1을 쓴다. 밀이 없으면 무음 no-op 이다 (510-513).
4. **비료는 마을 수요에서 제외** (103-114). 시장 재고가 town consumption 으로 줄지 않는다.
   판 만큼 가격이 영구히 눌린다. 상위 봇의 "매일 5단위 매도"는 이 제약 아래의 선택이다.
5. **`BUY_ANIMAL` 은 시장 10슬롯을 쓴다** (604-605). FEED/CARE/HARVEST/COLLECT 는 쓰지 않는다.

실측 흡수량 (엔진 `market_price` 직접 호출, 시작 재고 10000, 단독 매도):

| 품목 | N=5 | N=10 | N=20 | N=50 | N=20 단가 |
|---|---|---|---|---|---|
| WOOL | 998 | 1,983 | **3,856** | 7,655 | **192.8** |
| MILK | 780 | 1,506 | 2,802 | 5,430 | 140.1 |
| FERTILIZER | 498 | 991 | 1,962 | 4,755 | 98.1 |
| EGG | 242 | 474 | 927 | 2,244 | 46.4 |

**GOOSE 는 후보에서 제외한다.** 매일 급여 액션 1개를 쓰고 개당 46을 받는다.
상위 봇 4개 전원이 거위 0마리인 것이 이 숫자로 설명된다. `evidence/KILLS.md` 에 K9 로 등재할 것.

---

## 2. 가설

`[HYPOTHESIS]` H15: v1(3구획 + 밀/당근)에 **PASTURE 기반 소·양 + 비료 순환**을 얹으면
v1 대비 paired score 95% CI 하한 > 0.5 를 얻는다.

메커니즘: 구조물이 공짜이므로 초기 자본은 전부 동물 구매(소 400 / 양 500)와 일꾼 임금에 간다.
동물은 (a) 산물 매출, (b) 매일 비료 1개를 낳고, 비료는 (c) 시장 매도 현금흐름과
(d) 작물 수확량 1→2 배증에 동시에 쓰인다. 즉 동물은 작물 라인의 **승수**이지 별도 라인이 아니다.

---

## 3. 하드 제약 (위반 시 후보 즉시 FAIL)

1. **SE 구획($4,000)은 절대 사지 않는다.** K1 영구 KILL. 상위 봇 4개 전원 미구매로 재확인됨.
2. **GOOSE 를 사지 않는다.** §1 참조.
3. **급여 실패 0.** 매 턴 각 동물의 `fed_today` 와 `consecutive_unfed` 를 확인하고,
   담당 유닛이 밀을 실제로 들고 있는지 **PLANT/HARVEST 예산과 별개로** 검증한다.
   계측기 카운터에 `unfed_animal_days` 와 `animals_lost` 를 추가하고, **둘 다 0이 아니면 FAIL.**
4. **⚠️ 셰드 여유는 1칸뿐이다 (2026-09-09 실측).**
   동물 없는 현재도 하루 끝 피크가 **99/100** 이다(`evidence/SLOT_CONTENTION.md`).
   MILK·WOOL·미배치 동물이 **같은 100칸 풀**을 쓰므로(`kaggriculture.py:171`) 확정적으로 넘친다.
   넘칠 때 `guard_shed_capacity` 가 HARVEST 를 PASS 로 바꾸므로
   **`shed_discarded` 도 `noop_actions` 도 0 인 채로 손실이 발생한다.**
   KAGRI-016 에서 추가되는 `harvest_blocked_by_shed` 카운터를 gate 에 넣어라. 0 이 아니면 FAIL.
   동물 구매 전에 셰드 여유를 확보하는 로직(선매도 또는 즉시 PICKUP→PLACE)이 없으면 이 카드는 실패한다.

4b. **셰드 100은 작물·산물·비료·미배치 동물이 공유한다.** 동물 구매 직후 PICKUP→PLACE 까지
   몇 턴이 걸리는지 계산하고, 그 사이 셰드 여유가 있는지 확인한다. `shed_discarded` 0 유지.
5. **마지막 턴(step 718)에는 SELL 외 주문을 발행하지 않는다.**
   판매 품목이 WHEAT/CARROT/MILK/WOOL/FERTILIZER 로 늘어나므로 10슬롯이 실제로 빡빡해진다.
   `orders_truncated` 0 유지.
6. **시장 가격을 하드코딩하지 않는다.** 항상 `obs["market"]["prices"]` 를 읽는다.
   호스트가 `marketParams` 를 덮어쓸 수 있다.
7. **절대 raise 하지 않는다.** 폴백은 일꾼 수만큼 `["PASS"]`.
8. 에피소드 전체 `runTimeout = 1200s` 이다 (`evidence/FACTS.md`). 턴당 예산을 늘리지 않는다.

---

## 4. 고정 pilot 순서 — 한 번에 한 축만 바꾼다

parent = KAGRI-012 에서 확정된 v1 (timing prior, 선택된 hands, 선택된 carrots).
각 단계 20 시드(`1000..1019`) × 양 좌석 = 40경기. 상대는 **같은 단계의 다른 variant**.

**stage A — 동물 구성.** 일꾼은 이 단계에서만 14로 고정(액션 병목을 먼저 제거해야
동물 구성의 효과가 보인다). 비료는 전량 매도, FERTILIZE 미사용.
- `A1` COW 8 / SHEEP 4
- `A2` COW 10 / SHEEP 4
- `A3` COW 9 / SHEEP 8
(세 조합은 Gemini 프로파일의 실측 상위 봇 구성이다. 임의 탐색이 아니다.)

**stage B — 일꾼 수.** stage A 선택 구성 고정.
- `B1` hands 12  ·  `B2` hands 14  ·  `B3` hands 16

**stage C — 비료 용도 분배.** stage A+B 고정.
- `C1` 전량 매도
- `C2` 전량 FERTILIZE (작물 수확량 배증)
- `C3` 하루 5개까지 매도, 나머지 FERTILIZE

**stage D — 최종 대조. `[2026-09-07 개정 — AGENTS.md §7.1]`**
1차 지표는 **`opponents/public/` 4개 봇 상대** 페어드 점수다. 각 봇 50 시드 × 양 좌석 = 400경기.
v1 대비 비교는 같은 시드로 함께 돌리되 **진단으로만** 기록한다.
v1 을 이겼다는 사실은 승격 근거가 아니다 — 사다리를 근사하는 것이 목표다.

tie-break 는 EXP-001 카드와 동일: (1) head-to-head (2) big-loss 적은 쪽
(3) mean margin (4) 비용 낮은 쪽. 동점이면 결과를 `불확정` 으로 기록한다.

**pilot 은 후보 선택용 재사용 holdout 이다. hosted 우위 근거가 아니다.**

---

## 5. 승격 판정

- **SUCCESS**: silent-failure gate(§3 의 카운터 전부 0)와 self-play gate 가 CLEAN 이고,
  stage D 의 **공개봇 4종 합산** 95% CI 하한 > 0.5.
  4종 중 3종 이상에서 개별 CI 하한 > 0.5 여야 한다 (한 봇에만 강한 것은 과적합이다).
- **FAILURE**: gate 위반이 하나라도 있거나 CI 상한 < 0.5. → v1 유지, 실패를
  동물/비료 구현 범위로 한정해 보고.
- **UNCERTAIN**: CLEAN 이지만 CI 가 0.5 를 포함. → 같은 200 시드에 재튜닝 금지.
  새 가설을 별도 카드로 제안.

SUCCESS 시 추가 관문 하나: **`opponents/public/` 4개 봇 상대로 각 20시드 양 좌석**을 돌린다.
여기서 전패하면 SUCCESS 라도 제출하지 않는다. 로컬 v1 대비 개선이
리그 방향을 가리키는지 확인하는 유일한 수단이다 (K5: rayk 는 83-5, 마진 +14,196 인데 레이팅 3000 미만이었다).

---

## 6. 산출물

- `experiments/cards/EXP-002-animals.md` — **실행 전에** 이 브리프를 카드 형식으로 옮겨 사전등록
- `experiments/candidates/v2_*.py` — wrapper. parent sha 를 assert
- `experiments/results/v2_*.json` — KAGRI-012 에서 추가한 4개 sha 필드 포함
- `tools/instrument.py` — `unfed_animal_days`, `animals_lost` 카운터 추가
- `evidence/KILLS.md` — K9: GOOSE (근거는 §1 표)
- `coordination/reports/codex/YYYYMMDD-HHMM-KAGRI-013.md`

## 7. 하지 않을 것

- 720턴 하드코딩 테이프
- 상대 행동에 반응하는 적응 로직
- 시장 조작·선점 전략
- SE 구획, 거위, 딸기 등 신규 작물
이번 카드는 **동물 + 비료 한 축**이다. 다른 것이 섞이면 무엇이 효과였는지 알 수 없다.


---

## `proposals/codex/BRIEF_exp002_crops.md`

# KAGRI-015 — EXP-002 사전등록: 작물 교체 (v2) `[순서 변경: 동물보다 먼저]`

담당: Codex · 우선순위: **P0 (KAGRI-012 직후)** · 선행: KAGRI-012 완료
근거: `evidence/POSTMORTEM_4bots.md` §3

## 0. 왜 동물(KAGRI-013)보다 이걸 먼저 하나

부검 8판에서 4개 봇 전원이 파는데 우리는 0인 품목이 5개였다.
그중 MILK·WOOL·FERTILIZER 는 동물 레이어가 필요하지만,
**STRAWBERRY 와 MELON 은 새 액션 타입이 하나도 필요 없다. `PLANT` 의 인자만 바뀐다.**

| | 새 액션 타입 | 새 상태 관리 | 조용한 실패 위험 |
|---|---|---|---|
| **작물 교체 (이 카드)** | **0개** | 없음 | 낮음 (씨앗 예산만) |
| 동물 (KAGRI-013) | 9개 | 급여·소실·구조물·배치 | 높음 (2일 미급여 = 영구 소실) |

엔진 실측 단가 (한 턴 20개 투매):

| 작물 | 씨앗값 | first_yield_day | max_yield | ongoing | N=20 단가 |
|---|---|---|---|---|---|
| WHEAT (현재) | 10 | 2 | 6 | X | **23.4** |
| CARROT (현재) | 20 | 2 | 4 | X | **31.7** |
| TOMATO | 50 | 8 | 4 | O(interval 1) | 52.7 |
| STRAWBERRY | 100 | 10 | 4 | O(interval 2) | 101.7 |
| MELON | 80 | 10 | 6 | X | **248.8** |

MELON 단가 248.8 은 동물 산물(WOOL 192.8, MILK 140.1)보다도 높다.
`above_func = sq`, `T = 300` 이라 20개를 한 턴에 던져도 가격이 0.4% 밖에 안 빠진다.

**즉 가장 싼 변경이 가장 큰 효과일 가능성이 높다. 이것부터 측정한다.**

## 1. 가설

`[HYPOTHESIS]` H17: v1 의 75칸 작물 구성을 WHEAT/CARROT 에서
MELON·STRAWBERRY 중심으로 바꾸면, **새 액션 타입 없이** 공개 상위 봇 4종 상대
페어드 점수가 개선된다.

## 2. 핵심 제약 — 자본 램프

씨앗값이 WHEAT 10 → MELON 80 / STRAWBERRY 100 이다.
75칸을 한 번에 멜론으로 채우면 6,000 인데 **시작 자본은 3,000**이다.
상위 봇이 시즌 내내 밀을 계속 파는 이유가 이것으로 보인다(boatlee WHEAT 479개 매도).

따라서 이 카드는 "전부 멜론"이 아니라 **전환 스케줄**을 탐색한다.

## 3. 고정 pilot 순서 — 한 번에 한 축

parent = KAGRI-012 에서 확정된 v1. 20 시드(`1000..1019`) × 양 좌석 = 40경기/비교.

**stage A — 고수익 작물 비중.** 전환일은 day 4 고정, 나머지는 WHEAT.
- `A1` MELON 15칸  ·  `A2` MELON 30칸  ·  `A3` MELON 45칸

**stage B — 전환 시점.** stage A 선택 비중 고정.
- `B1` day 2  ·  `B2` day 4  ·  `B3` day 8
  (MELON first_yield_day 가 10 이다. day 8 전환이면 첫 수확이 day 18 이라
   30일 안에 1주기밖에 못 돈다. 이 축은 실제로 민감할 것이다.)

**stage C — STRAWBERRY 혼합.** stage A+B 고정. STRAWBERRY 는 `ongoing` 이라
한 번 심으면 계속 나오지만 day 10 성숙까지 물을 계속 줘야 한다.
- `C1` STRAWBERRY 0칸 (멜론만)
- `C2` STRAWBERRY 15칸
- `C3` STRAWBERRY 30칸

**stage D — 승격 판정.** `AGENTS.md §7.1` 에 따라
**1차 지표는 `opponents/public/` 4개 봇 상대** 페어드 점수. 각 봇 50시드 × 양 좌석.
v1 대비 비교는 같은 시드로 함께 돌리되 **진단으로만** 기록한다.

tie-break 는 EXP-001 카드와 동일.

## 4. 하드 제약 (위반 시 후보 즉시 FAIL)

1. **씨앗 부족 시 PLANT 미발행.** 같은 턴 같은 작물 PLANT 유닛 수 ≤ 보유 씨앗.
   MELON 80 / STRAWBERRY 100 이라 이 제약이 WHEAT 때보다 훨씬 자주 걸린다.
   계측기 `buy_failed` 와 `noop_actions` 를 반드시 0 으로 유지하라.
2. **현금이 음수가 되는 순간이 없어야 한다.** 자본 램프가 이 카드의 핵심 실패면이다.
   일별 최저 현금을 진단으로 기록하라.
3. **SE 구획($4,000) 금지** (K1). **동물 금지** — 이 카드는 작물 한 축이다.
4. 마지막 턴(step 718)에는 SELL 외 주문을 발행하지 마라. 판매 품목이 늘어난다.
5. 시장 가격을 하드코딩하지 마라. `obs["market"]["prices"]` 를 읽어라.
6. 절대 raise 하지 마라. 폴백은 일꾼 수만큼 `["PASS"]`.

## 5. 부수 확인 (같이 측정, 별도 카드 아님)

부검에서 **우리만 토지를 16스텝 일찍 산다**는 것이 나왔다.

| | NE | SW |
|---|---|---|
| 우리 | step **145** (day6 h1) | step 241 |
| boatlee / rayk / kaito | step **161** (day6 h17) | step 241 |

EXP-001 stage 1 은 **일 단위만** 비교했다. 시각까지는 안 봤다.
씨앗값이 8~10배로 오르는 이 카드에서는 현금을 16스텝 일찍 빼는 것이 실제로 아플 수 있다.
stage B 안에서 `NE 매입 시각 h1 vs h17` 을 하나의 variant 로 추가해 함께 본다.

## 6. 산출물

- `experiments/cards/EXP-002-crops.md` — 실행 전 사전등록
- `experiments/candidates/v2c_*.py` — parent sha assert
- `experiments/results/v2c_*.json` — KAGRI-012 에서 추가한 4개 sha 필드 포함
- `evidence/HYPOTHESES.md` — H17 등재
- `coordination/reports/codex/YYYYMMDD-HHMM-KAGRI-015.md`

## 7. 다음

이 카드가 끝나면 **KAGRI-013(동물·비료)** 으로 간다.
동물은 이 카드의 승자 위에 얹는다. 순서를 바꾸지 마라 —
싸고 위험 낮은 축을 먼저 측정해야 동물의 순효과를 분리할 수 있다.


---

## `proposals/codex/BRIEF_exp003_absorption.md`

# KAGRI-016(개정) — EXP-003: 흡수량 정합 `[이전 execution 카드를 대체한다]`

담당: Codex · 우선순위: **P0** · parent: KAGRI-015 의 `v2c_c3_strawberry30`
근거: **`evidence/ABSORPTION.md`** (이 문서를 먼저 읽어라)

> ⚠️ **2026-09-09 2차 개정 (cowork, 사람 승인).** `evidence/ABSORPTION.md` §1 의
> 상점 해금 주기가 틀려 있었다(4일/7개 → **실제 3일/8개**). 시즌 흡수량이 **+28.8%** 상향됐다.
> §1 표를 교체했고 **부록 A-2 의 고정 cap 표는 폐기**한다 — 부록 B 의 동적 cap 을 쓴다.
> 품목 순위와 stage 구성은 그대로다.

## 0. ⚠️ 이전 브리프는 폐기한다

`BRIEF_exp003_execution.md` 의 §1 "MELON 실행 개선 상한 38,164" 는 **틀렸다.**
MELON 은 어느 상점 목록에도 없어 시즌 흡수량이 **30개**뿐이다(타운센터 24턴×1).
분산 매도로도 30개까지만 base 250 을 받는다. 그 브리프는 읽지 마라.
분산 매도 아이디어 자체는 이 카드의 stage B 로 살아 있다.

## 1. 이 게임의 실제 경제 지도

| 품목 | 시즌 흡수량 | base | **시즌 가치 상한** | 우리 현재(seed1000) |
|---|---|---|---|---|
| **MILK** | 327 | 160 | **52,320** | **0** |
| **STRAWBERRY** | 426 | 120 | **51,120** | 102 |
| **WOOL** | 228 | 200 | **45,600** | **0** |
| TOMATO | 228 | 60 | 13,680 | 0 |
| WHEAT | 525 | 25 | 13,125 | 314 |
| CARROT | 327 | 35 | 11,445 | 6 |
| EGG | 228 | 50 | 11,400 | 0 |
| **MELON** | **30** | 250 | **7,500** | **259 (8.6배 초과)** |
| FERTILIZER | 0 | 100 | 0 | 0 |
| 합계 | | | **206,190** | 우리 42,050 (20%) |

**MILK + WOOL = 97,920 = 전체 파이의 47.5%.** 둘 다 동물에서만 나온다.

boatlee 는 121,116 = 파이의 **58.7%** 를 가져간다.

## 2. 선행 수정 (실험 아님, 버그 픽스)

parent 에 아래를 적용하고 gate 만 확인한다. 사전등록 실험이 아니다 —
**시즌 수요 30개인 작물에 30칸을 준 것은 탐색이 아니라 오류다.**

- MELON 타일을 **30칸 → 3칸 이하**로 줄인다 (시즌 30개 흡수, 양 플레이어 공유이므로 실효 ~15개).
- 회수한 칸은 **STRAWBERRY** 로 돌린다 (상한 324개 중 우리는 102개만 팔고 있다).
- 적용 후 `tools/instrument.py` gate 가 CLEAN 이고 4봇 평균 뱅크가 parent 이상인지만 확인한다.
  뱅크가 내려가면 되돌리고 보고하라 — 그 경우 내 흡수량 모델이 틀린 것이다.

이 수정본을 `v2a_parent.py` 로 동결하고 아래 stage 의 parent 로 쓴다.

## 3. 고정 pilot 순서

20 시드(`1000..1019`) × 양 좌석 = 40경기/비교. **생산 로직은 stage A 에서만 바꾼다.**

**stage A — 작물 배분을 흡수량에 맞춘다.** 75칸을 어떻게 나누는가.
- `A1` STRAWBERRY 45 / WHEAT 27 / MELON 3
- `A2` STRAWBERRY 30 / WHEAT 30 / TOMATO 12 / MELON 3
- `A3` STRAWBERRY 45 / WHEAT 15 / CARROT 12 / MELON 3
  (TOMATO 는 `ongoing`, 상한 10,620. CARROT 은 PET_CAFE 가 ×2 로 먹는다.)

**stage B — 매도 스케줄.** stage A 선택 고정. 생산은 건드리지 않는다.
현재 우리는 **720턴 중 62턴에만 주문을 내고 1회 평균 12.2개**를 던진다.
boatlee 는 286턴, 8.6개다.
- `B1` 하루 1턴 (현재)  ·  `B2` 하루 4턴 (h1/h7/h13/h19)  ·  `B3` 매 2턴마다
- 1회 매도 수량 상한은 각 후보에서 `흡수량/일` 근처로 잡는다(예: STRAWBERRY 하루 ~11개).

**stage C — 10슬롯 우선순위.** 우리는 24턴에서 슬롯이 꽉 찼고 HIRE 가 267줄을 먹었다.
- `C1` 현재  ·  `C2` SELL 우선, HIRE 는 남는 슬롯  ·  `C3` SELL 우선 + 시즌가치 높은 품목 먼저

**stage D — 승격 판정.** `AGENTS.md §7.1`. 4봇 각 50시드 × 양 좌석.
`§7.1b` 에 따라 페어드 점수가 여전히 0/0/400 이면 **탐색 지표(4봇 상대 평균 뱅크)** 로
후보를 고르고, 승격은 하지 않는다.

## 4. 하드 제약

1. **셰드 100 초과 금지.** 매도를 늦추면 재고가 쌓인다. `shed_discarded` 가 1순위 실패면이다.
   일별 최대 셰드 점유율을 진단으로 기록하라.
2. step 718 전량 청산 유지. 마지막 턴에는 SELL 외 주문 금지.
3. `orders_truncated` 0. `noop_actions` 0. `buy_failed` 0.
4. 시장 가격 하드코딩 금지 — `obs["market"]["prices"]`.
5. 동물 금지 (KAGRI-013 소관). SE 구획 금지 (K1).
6. 절대 raise 하지 마라.

## 5. 진단으로 반드시 기록

- **품목별 실현 총액과 실현 단가** (수량이 아니라 받은 돈)
- 품목별 판매량 ÷ `evidence/ABSORPTION.md` 의 시즌 흡수량 = **초과 배수**
- 주문 발행 턴 수, 10슬롯 포화 턴 수, 1회 평균 매도 수량
- 일별 최대 셰드 점유율

## 6. 다음 — 그리고 이게 진짜 큰 건이다

**MILK + WOOL = 97,920 = 전체 파이의 47.5% 이고, 우리는 0 이다. 둘 다 동물에서만 나온다.**
이 카드가 끝나면 **KAGRI-013(동물·비료)** 이 남은 최대 레버다.
parent 는 이 카드의 승자.

---

# 부록 A — 모호 항목 확정 (2026-09-09, KAGRI-016 BLOCKED 보고에 대한 답)

Codex 가 지적한 세 가지를 exact 값으로 고정한다. **이 부록이 본문 §3 stage B·C 를 대체한다.**
먼저 `evidence/SLOT_CONTENTION.md` 를 읽어라 — 그 측정이 아래 정의의 근거다.

## A-1. 선행 correction gate 의 시드 범위 — 확정

**`1000..1049` (50 시드) × 양 좌석.** 기존 `v2c_parent_vs_*.json` 이 같은 범위로 돌았으므로
matched-seed 비교가 된다. pilot 의 `1000..1019` 를 쓰지 마라 — 비교 대상이 없다.

판정: MELON 30칸→3칸 수정본의 **4봇 상대 우리 평균 뱅크**가 parent 이상이면 통과.
`tools/instrument.py` 카운터 전부 0 도 함께 요구한다.
뱅크가 내려가면 되돌리고 보고하라 — 그 경우 `evidence/ABSORPTION.md` 의 흡수량 모델이 틀린 것이다.
통과하면 `experiments/candidates/v2a_parent.py` 로 동결한다.

## A-2. stage B — 매도 스케줄과 exact cap

> ⛔ **이 절의 cap 규칙과 표는 2026-09-09 폐기됐다. 부록 B 를 대신 쓴다.**
> 발행 스케줄(B1/B2/B3)과 셰드 안전밸브는 그대로 유효하다.

cap 규칙: `cap(item) = max(1, ceil(시즌흡수량 / 30 / 발행횟수))`. 반올림은 **ceil** 로 고정.

| 품목 | 시즌흡수량 | **B2** (하루 4턴: h1/h7/h13/h19) | **B3** (짝수 hour, 하루 12턴) |
|---|---|---|---|
| WHEAT | 398 | 4 | 2 |
| STRAWBERRY | 324 | 3 | 1 |
| CARROT | 250 | 3 | 1 |
| MILK | 250 | 3 | 1 |
| TOMATO | 177 | 2 | 1 |
| EGG | 177 | 2 | 1 |
| WOOL | 177 | 2 | 1 |
| MELON | 30 | 1 | 1 |
| FERTILIZER | 0 | 1 | 1 |

- `B1` = 현재(하루 1턴 h1, cap 없음). baseline.
- `B2` = 위 표 4턴 열.
- `B3` = 위 표 12턴 열.

**셰드 안전밸브 (B2·B3 공통, 필수):**
`sum(shed.values()) >= 60` 이면 **그 턴은 cap 을 무시하고 전량 매도한다.**
근거: cap 없는 현재도 최대 점유가 **91** 이다(`evidence/SLOT_CONTENTION.md` §2).
step 718 전량 청산은 cap 과 무관하게 유지한다.

진단으로 **일별 최대 셰드 점유율**과 **안전밸브 발동 횟수**를 반드시 기록하라.
`shed_discarded` 가 1이라도 나오면 그 후보는 FAIL 이다.

## A-3. stage C — 재정의 (SELL 우선순위 축은 폐기)

측정 결과 SELL 은 한 번도 잘리지 않았다. 잘린 것은 **BUY_SEED 32줄, HIRE 26줄** 이다.
따라서 축을 **BUY_SEED vs HIRE 슬롯 배분**으로 바꾼다.
**stage C 는 stage B 승자 위에서 돌린다** (B 가 h1 슬롯을 이미 일부 비워주므로 독립이 아니다).

- `C1` 현재 순서: `SELL 전량 → BUY_LAND → HIRE → BUY_SEED`, 꼬리부터 클램프.
- `C2` 씨앗 우선: `SELL 전량 → BUY_LAND → BUY_SEED → HIRE`.
  (파종 결손은 며칠 뒤 수확 결손으로 복리된다는 가설)
- `C3` 슬롯 예약제: `SELL 최대 4줄(가격 내림차순) → BUY_LAND 1줄 → BUY_SEED 최대 3줄 → HIRE 나머지`.
  SELL 초과분은 다음 매도 턴으로 이월한다. 단 A-2 안전밸브가 걸리면 SELL 4줄 제한도 해제한다.

## A-4. 진단 추가 항목

기존 항목에 더해 **클램프 전후 주문 줄 수와 잘려나간 주문 종류별 개수**를 기록하라.
`orders_truncated` 는 에이전트가 스스로 자른 것을 잡지 못한다 — 이번 사고의 원인이다.

## A-5. 셰드 계측 구멍 — 이 카드에서 반드시 막을 것

**현재 셰드 100 제한의 비용은 0 이다** (반사실 실험: cap 400 으로 올려도 뱅크 변화 없음).
그러나 실측 피크가 **99/100** 이고, `guard_shed_capacity` (`main.py:600-621`) 가
넘칠 상황에서 **HARVEST 를 PASS 로 바꾼다.** 이때:

- `shed_discarded` = 0 (버리지 않고 안 거두므로)
- `noop_actions` = 0 (PASS 는 합법 액션이므로)
- 실제 손실은 밭에 남은 작물의 decay 로 나타난다

**어느 카운터에도 안 잡힌다.** stage B 는 이 여유 1칸을 의도적으로 잡아먹는다.
따라서 다음 두 가지를 이 카드에서 함께 한다.

1. **`tools/instrument.py` 에 카운터 2개 추가:**
   - `harvest_blocked_by_shed` — `guard_shed_capacity` 가 HARVEST 를 PASS 로 바꾼 횟수
   - `shed_peak` — 에피소드 중 `sum(shed.values())` 의 최댓값
   **두 값을 gate 에 넣는다: `harvest_blocked_by_shed > 0` 이면 그 후보는 FAIL.**
   `shed_peak` 은 진단으로 기록한다(FAIL 조건 아님).

2. **`main.py:410` 의 거짓 주석을 고친다.**
   현재: "매 턴 비우므로 셰드가 100칸에 닿는 일도 없다"
   실측: 6판 중 4판이 99/100. 아래로 교체하라.
   ```
   # 하루 1턴 전량 매도라 다음 날 아침 비워지지만, 하루 끝 피크는 실측 99/100 이다.
   # 여유는 1칸뿐이다. 매도를 늦추거나(cap) 동물 산물이 들어오면 즉시 넘친다.
   # 넘칠 때 guard_shed_capacity 가 HARVEST 를 PASS 로 바꾸므로
   # shed_discarded 도 noop_actions 도 0 인 채로 손실이 발생한다.
   # -> harvest_blocked_by_shed 카운터로만 보인다. (evidence/SLOT_CONTENTION.md)
   ```

이 두 가지는 실험이 아니라 계측 정비다. stage A 시작 **전에** 끝내라.


---

# 부록 B — 동적 매도 cap (2026-09-09, A-2 를 대체한다)

## B-0. 왜 고정 cap 이 틀렸나

A-2 는 `시즌흡수량 / 30 / 발행횟수` 로 cap 을 잡았다. 이는 **일일 흡수량이 상수라고 가정**한다.
엔진은 그렇지 않다. 상점은 **day 3 에 1개로 시작해 day 24 에 8개**가 된다
(`kaggriculture.py:867,886,118`). 같은 품목의 일일 흡수량이 게임 후반에 **8배**가 된다.

- day 1~2: 상점 0개. 모든 품목 일일 흡수량 = **1** (타운센터뿐).
- day 24 이후: 8개 정상상태. 밀 31 · 딸기 25 · 우유 19 · 당근 19 · 토마토 13 · 달걀 13 · 양털 13 · 멜론 1 · 비료 0.

평탄 cap 은 **초반에 과다 매도하고 후반에 과소 매도**한다. 두 방향 모두 손해다.

## B-1. exact 규칙

**미래 해금은 예측 불가지만 현재 해금은 관측 가능하다** — `obs["town"]["unlocked_shops"]`.
기댓값이 아니라 실현값을 쓴다.

```python
# turnsPerDay 24 / townShopSellInterval 4 -> 하루 6 tick
SHOP_PRODUCTS = {   # kaggriculture.py:103-112, 정적 상수. 하드코딩 허용.
  "BAKERY":["EGG","WHEAT"], "PIZZA_SHOP":["MILK","TOMATO","WHEAT"],
  "BRUNCH_SPOT":["EGG","WHEAT","STRAWBERRY"], "YARN_STORE":["WOOL"],
  "ICE_CREAM_SHOP":["STRAWBERRY","MILK","WHEAT"], "PET_CAFE":["CARROT"],
  "SMOOTHIE_SHOP":["STRAWBERRY","MILK"],
  "FARMERS_MARKET":["WHEAT","CARROT","TOMATO","STRAWBERRY"],
}
SHARE = 0.5          # 흡수량은 양 플레이어 공유 파이다
import math

def daily_absorption(item, unlocked_shops):
    per_tick = 0
    for name in unlocked_shops:                  # 중복 등장 가능 — 그대로 센다
        prods = SHOP_PRODUCTS.get(name, ())
        if item in prods:
            per_tick += 2 if len(prods) == 1 else 1
    return 6 * per_tick + (0 if item == "FERTILIZER" else 1)

def sell_cap(item, unlocked_shops, issues_per_day):
    a = daily_absorption(item, unlocked_shops) * SHARE
    return max(1, math.ceil(a / issues_per_day))
```

- `issues_per_day` = 그 후보의 매도 발행 횟수. `B1`=1 · `B2`=4 · `B3`=12.
- `SHARE = 0.5` 를 **stage B 전체에서 고정**한다. share 값 자체는 이 카드의 실험 축이 아니다.
- `max(1, ...)` 때문에 상점 0개 구간에서도 품목당 1개는 나간다. 의도된 하한이다.
- **`SHOP_PRODUCTS` 외에 시장 가격·흡수량을 하드코딩하지 마라.** 가격은 `obs["market"]["prices"]`.

## B-2. 참고값 — 정상상태(상점 8개) cap

디버깅용 눈금이다. **코드에 이 표를 박지 마라.** B-1 함수로 계산하라.

| 품목 | 일일 흡수 | share 0.5 | **B2 cap** | **B3 cap** |
|---|---:|---:|---:|---:|
| WHEAT | 31 | 15.5 | 4 | 2 |
| STRAWBERRY | 25 | 12.5 | 4 | 2 |
| MILK | 19 | 9.5 | 3 | 1 |
| CARROT | 19 | 9.5 | 3 | 1 |
| TOMATO | 13 | 6.5 | 2 | 1 |
| EGG | 13 | 6.5 | 2 | 1 |
| WOOL | 13 | 6.5 | 2 | 1 |
| MELON | 1 | 0.5 | 1 | 1 |
| FERTILIZER | 0 | 0 | 1 | 1 |

초반값 대비: day 3~5 구간은 상점 1개이므로 대부분 품목의 cap 이 **1**로 떨어진다.

## B-3. 이 변경이 "한 요인" 계약을 깨지 않는 이유

`AGENTS.md §5` 는 **후보 간 비교에서** 한 요인만 다를 것을 요구한다.
B-1 은 B1/B2/B3 **전부에 동일하게 적용되는 공통 규칙**이고, 세 후보를 가르는 축은
여전히 `issues_per_day` 하나다. 따라서 one-factor 는 유지된다.

단, **A-2 의 고정 cap 으로 이미 측정한 결과가 있다면 B-1 결과와 같은 표에 올리지 마라.**
cap 규칙이 다르면 다른 실험이다.

## B-4. 진단 추가

기존 항목에 더해 기록하라.

- 품목별 **일일 실제 매도량 / `daily_absorption`** 비율의 시계열 (일 단위)
- `unlocked_shops` 의 day 별 스냅샷 — 시드마다 상점 구성이 달라 cap 궤적이 달라진다
- cap 에 걸려 이월된 물량과, 셰드 안전밸브가 그것을 되돌린 횟수


---

## `proposals/codex/BRIEF_exp003_execution.md`

# ⛔ 폐기 — `BRIEF_exp003_absorption.md` 로 대체됨 (2026-09-09)

> 이 브리프의 핵심 수치 "MELON 실행 개선 상한 38,164" 는 **틀렸다.**
> MELON 은 어느 상점 목록에도 없어 시즌 흡수량이 30개뿐이다.
> 근거: `evidence/ABSORPTION.md` §3. **이 파일을 따르지 마라.**

---

# KAGRI-016 — EXP-003 사전등록: 시장 실행(execution) `[동물보다 먼저]`

담당: Codex · 우선순위: **P0** · parent: **KAGRI-015 의 `v2c_c3_strawberry30`**
근거: `evidence/MARKET_EXECUTION.md`

## 0. coordinator 결정 (KAGRI-015 보고의 질문에 대한 답)

**KAGRI-013(동물)의 parent 는 v1 이 아니라 KAGRI-015 의 `v2c_c3_strawberry30` 이다.**

브리프의 "실패 시 v1 유지" 조항은 *더 나빠졌을 때*를 전제로 쓴 것이다.
KAGRI-015 는 promotion gate 를 실패했지만 탐색 지표에서는 크게 전진했다
(v1 대비 100/0/0, +29,681; 4봇 평균 마진 −121,611 → −105,573).
**후퇴가 아니라 아직 못 이긴 것**이므로 parent 로 채택한다.
KAGRI-015 의 FAILURE 판정 자체는 유지한다 — 제출하지 않는다.

## 1. 왜 이 카드가 동물보다 먼저인가

| | 새 액션 타입 | 조용한 실패 위험 | 측정된 상한 |
|---|---|---|---|
| **시장 실행 (이 카드)** | **0개** | 낮음 (10슬롯만) | **MELON 단일 품목 +38,164** |
| 동물 (KAGRI-013) | 9개 | 높음 (2일 미급여 = 영구 소실) | 미측정 |

측정된 사실 (`evidence/MARKET_EXECUTION.md`):

| | 우리 | boatlee |
|---|---|---|
| 주문 발행 턴 수 | **62 / 720** | 286 / 720 |
| 10슬롯 꽉 찬 턴 | **24** | 5 |
| 1회 평균 매도 수량 | **12.2** | 8.6 |
| MELON 판매량 | **259** | 126 |
| 최종 뱅크 | 42,050 | 121,116 |

**멜론을 2배 더 팔고 뱅크는 1/3 이다.** 생산이 아니라 판매에서 잃는다.
MELON 259개: 연속 투매 26,586 vs 완전 분산 64,750 → **상한 38,164**.

## 2. 가설

`[HYPOTHESIS]` H18: 동일한 생산량을 유지한 채 SELL 주문을 하루 안에서 분산하고
1회 수량을 줄이면, 새 액션 타입 없이 4봇 상대 평균 마진이 개선된다.

## 3. 고정 pilot 순서 — 한 번에 한 축

parent = `v2c_c3_strawberry30`. 20 시드(`1000..1019`) × 양 좌석 = 40경기/비교.
**생산 로직(작물 구성·전환일·토지·일꾼)은 이 카드에서 절대 바꾸지 마라.**
바뀌는 것은 "언제 몇 개를 파는가" 뿐이다.

**stage A — 1회 매도 상한.** 한 SELL 줄의 최대 수량을 캡한다. 초과분은 다음 기회로 이월.
- `A1` cap 4  ·  `A2` cap 8  ·  `A3` cap 16 (현재는 사실상 무제한, 평균 12.2)

**stage B — 매도 발행 빈도.** stage A 선택 고정.
- `B1` 하루 1턴 (현재)  ·  `B2` 하루 4턴 (h1/h7/h13/h19)  ·  `B3` 매 2턴마다

**stage C — 슬롯 우선순위.** stage A+B 고정. 10슬롯이 꽉 찰 때 무엇을 버리는가.
- `C1` HIRE 우선 (현재)  ·  `C2` SELL 우선, HIRE 는 남는 슬롯에
- `C3` SELL 우선 + 단가 높은 품목(MELON > WOOL > MILK > STRAWBERRY > FERTILIZER > CARROT > WHEAT) 먼저

**stage D — 승격 판정.** `AGENTS.md §7.1`. 4봇 각 50시드 × 양 좌석.

## 4. 하드 제약

1. **생산 로직 불변.** PLANT/WATER/HARVEST/BUY_LAND/HIRE 의 타이밍과 대상을 바꾸지 마라.
   변경은 `market` 주문 리스트를 만드는 지점 한 곳에 국한한다.
2. **셰드 100 초과 금지.** 매도를 늦추면 재고가 쌓인다. `shed_discarded` 가 이 카드의
   1순위 실패면이다. 반드시 0을 유지하고, 일별 최대 셰드 점유율을 진단으로 기록하라.
3. **step 718 청산 유지.** 마지막 턴에 남은 재고를 전부 턴다. cap 이 이걸 막으면 안 된다.
   마지막 턴에는 SELL 외 주문을 발행하지 마라.
4. `orders_truncated` 0 유지. 10슬롯을 넘기지 마라.
5. 시장 가격 하드코딩 금지. `obs["market"]["prices"]` 를 읽어라.
6. 절대 raise 하지 마라.

## 5. 진단으로 반드시 기록할 것

- 품목별 **실현 총액과 실현 단가** (수량이 아니라 받은 돈)
- 주문 발행 턴 수, 10슬롯 꽉 찬 턴 수, 1회 평균 매도 수량
- 일별 최대 셰드 점유율
이 세 줄이 없으면 무엇이 효과였는지 알 수 없다.

## 6. 산출물

`experiments/cards/EXP-003-execution.md` (실행 전 사전등록),
`experiments/candidates/v2e_*.py`, `experiments/results/v2e_*.json`,
`evidence/HYPOTHESES.md` H18 등재,
`coordination/reports/codex/YYYYMMDD-HHMM-KAGRI-016.md`

## 7. 다음

이 카드 뒤에 **KAGRI-013(동물·비료)**. parent 는 KAGRI-016 의 승자
(승격 실패라도 탐색 지표가 전진했으면 채택 — §0 과 같은 규칙).


---

## `proposals/codex/BRIEF_exp004_animals.md`

# KAGRI-013 — EXP-004 동물 레이어 (v2) `[2026-09-10 재작성 — Codex 지적 6건 반영]`

담당: Codex · parent: `experiments/candidates/v2c_c3_strawberry30.py` (sha `adf8e798…855`)
**사전등록 카드: `experiments/cards/EXP-004-animals.md` — 그 카드가 정본이다.**
이 브리프는 카드에 없는 실행 지침만 담는다. 충돌하면 카드가 이긴다.

## 0. Codex 지적 6건에 대한 답 (전부 수용)

| # | 지적 | 조치 |
|---|---|---|
| 1 | §1 은 이미 같은 조건으로 실행·실패(−98.005) | **§1 삭제.** `evidence/KILLS.md` **K10** 으로 등재. 이 카드에서 재시도 금지 |
| 2 | 브리프가 정정 전 경제 수치 사용 | 아래 §1 표를 정정본(`ABSORPTION.md` 206,190 기준)으로 교체 |
| 3 | K9 가 존재하지 않음 / K1 은 영구 KILL 아님 | **K9 를 실제로 등재했다.** K1 표현을 "재검토 조건 있는 KILL" 로 정정 |
| 4 | stage A 가 동물과 hands 를 동시에 변경 | **stage A 는 hands=9 고정, 동물만.** hands 는 stage B 로 분리. A0(동물 없음) 대조군 추가 |
| 5 | 비교 상대·threshold·`불확정` 기준·FERTILIZE 대상 미정의 | 카드에 전부 명시(round-robin, 0.20 threshold, 4단 tie-break, D2 대상 타일 규칙) |
| 6 | `experiments/` `evidence/` writer 는 Claude | **`AGENTS.md` 소유권을 실제 운영에 맞게 정정.** `experiments/cards/`·`evidence/` = Claude, `experiments/candidates/`·`experiments/results/` = Codex |

## 1. 왜 이 카드인가 — 정정된 수치

**측정 1** (`PASS_DIAGNOSIS.md`): 우리 액션의 **42%가 PASS**. 원인 진단 완료 —
자본 제약(1.3%)도 라우팅 실패도 아니고, **83.5% 가 "생육중이라 할 일 없음"** 이다.
작물 75칸이 요구하는 액션은 하루 약 67개, 예산은 하루 240개. **수요가 공급의 28%.**

**측정 2** (`ABSORPTION.md`, 2026-09-09 정정본):

| 품목 | 시즌 흡수량 | base | 시즌 가치 상한 | 우리 |
|---|---:|---:|---:|---:|
| MILK | 327 | 160 | **52,320** | **0** |
| STRAWBERRY | 426 | 120 | 51,120 | 102 |
| WOOL | 228 | 200 | **45,600** | **0** |
| MELON | 30 | 250 | 7,500 | 259 |
| 전체 파이 | | | **206,190** | 우리 약 42,050 |

**MILK + WOOL = 97,920 = 전체의 47.5%. 우리는 0 이다.** 둘 다 동물에서만 나온다.

**두 측정은 같은 사실이다.** 동물 1마리가 하루 `FEED + CARE + COLLECT_FERTILIZER +
HARVEST(2~3일마다)` ≈ 3.5 액션을 소비하고 그 산출이 위 두 블록이다.
boatlee 의 생산 액션 3,173 중 **1,773 이 동물 관련**이고 작물 관련은 1,400 으로
우리(1,592)보다 **오히려 적다**.

→ **동물은 추가 수익원이 아니라 남는 액션을 흡수하는 장치다.**

## 2. 엔진 사실 (`evidence/ENGINE_ANIMALS.md`, 줄번호 포함)

```
ANIMALS = {GOOSE: (300, COOP,    first_yield 4, interval 1, max_held 4, EGG),
           COW:   (400, PASTURE, first_yield 8, interval 2, max_held 6, MILK),
           SHEEP: (500, PASTURE, first_yield 6, interval 3, max_held 6, WOOL)}
```
- `BUILD_PASTURE` / `BUILD_COOP` 는 **비용 0** (:493-503). 빈 소유 타일 + 액션 1회.
- 유닛은 **턴당 액션 1개** (:935-939).
- **2일 연속 미급여 → 동물 영구 소실** (:817-820). FEED 는 그 유닛 인벤토리의 밀 1을 쓰고,
  밀이 없으면 **무음 no-op** (:510-513).
- 구매한 동물은 밭이 아니라 **셰드**로 들어간다 (:685). 셰드 100칸은 작물·산물·
  미배치 동물이 **공유**한다 (:171). **동물 없는 현재도 피크 99/100 이다.**
- `BUY_ANIMAL` 은 **시장 주문**이라 10슬롯을 먹는다 (:604-605).
  FEED/CARE/HARVEST/COLLECT_FERTILIZER/PLACE 는 유닛 액션이라 안 먹는다.

## 3. 하드 제약

1. **SE 구획($4,000) 금지** — K1 (재검토 조건: 액션 예산이 근본적으로 늘어난 경우).
2. **GOOSE·`BUILD_COOP` 금지** — K9.
3. **MELON 타일 재배분 금지** — K10. 이미 실패했다.
4. **급여 실패 0.** `fed_today`/`consecutive_unfed` 확인 + 담당 유닛이 밀을 실제 보유하는지
   PLANT 예산과 **별개로** 검증.
5. **셰드.** `harvest_blocked_by_shed` 0 유지. 동물 구매 후 PICKUP→PLACE 까지의 셰드 점유를
   계산하고, 구매 전 여유 확보 로직이 없으면 이 카드는 실패한다.
6. **마지막 턴(step 718)에는 SELL 외 주문 금지.**
7. 시장 가격 하드코딩 금지 — `obs["market"]["prices"]`.
8. **절대 raise 하지 마라.** 폴백은 일꾼 수만큼 `["PASS"]`.
9. 작물 구성·전환일·토지 타이밍 불변. **이 카드는 동물 한 축이다.**

## 4. 실행 순서

1. **선행 계측** — `tools/instrument.py` 에 카드의 카운터 5종 추가.
   완료 후 parent 기준선 1회 측정 → `experiments/results/v2n_baseline.json`.
   **이 기준선의 `pass_rate` 가 모든 stage 의 비교 대상이다. 이것 없이 stage A 를 시작하지 마라.**
2. stage A → B → C → D → E. 카드의 threshold·tie-break·`불확정` 기준을 그대로 따른다.
3. **stage A 에서 A0(동물 없음)이 이기면 거기서 종료**하고 FAILURE 로 보고하라.

## 5. 산출물과 소유권

| 경로 | writer |
|---|---|
| `main.py`, `tools/instrument.py` | Codex |
| `experiments/candidates/v2n_*.py`, `experiments/results/v2n_*.json` | Codex |
| `experiments/cards/EXP-004-animals.md`, `evidence/*` | **Claude — 건드리지 마라** |
| `coordination/reports/codex/YYYYMMDD-HHMM-KAGRI-013.md` | Codex |

결과 JSON 에는 `parent_sha256`·`agent_a_sha256`·`agent_b_sha256`·`engine_sha256` 을 포함한다.
모든 로컬 수치에 `[LOCAL]`. **로컬 결과로 hosted 우위를 주장하지 마라.**
막히면 추측하지 말고 무엇이 모호한지 적고 멈춰라 — 지난 두 번 다 옳은 판단이었다.


---

## `proposals/codex/BRIEF_v1_land.md`

# Codex 작업 지시서 — v1: 면적 확장 (KAGRI-009)

이 파일을 그대로 Codex 세션에 붙여넣으면 된다. 작업 폴더 `~/kaggle/Kaggriculture`.

---

## 시작 전 확인 3가지

1. `AGENTS.md` 를 읽었는지 확인하라. 이게 프로젝트 계약이다.
2. `python3 --version` **3.11 이상**이어야 한다. 미만이면 `kaggle-environments==1.32.7` 설치가 거부된다.
   우회: `uv venv --python 3.11 ~/.venv311 && ~/.venv311/bin/python -m pip install -r requirements.lock`
3. 엔진 해시 검증: `python3 tools/smoke.py` 첫 줄이 ENGINE_LOCK 과 일치해야 한다.

## 배경 — 왜 이게 v1의 전부인가

v0(`main.py`)는 이미 제출됐고 게이트를 전부 통과했다.
그런데 계측에서 **유닛 액션의 41%가 PASS** 로 나왔다.

| | |
|---|---|
| NW 25칸이 요구하는 일 | 하루 **68 액션** |
| 일꾼 4명 + 농부가 내는 액션 | 하루 **120 액션** |
| v0 최종 뱅크 | 17,294~20,193 (13시드) |
| 상위권 터미널 캐시 | **90,000~95,000** |

**노동력은 남는데 밭이 없다.** 그리고 자금은 이미 충분하다 — v0 자금 곡선이
d8에 4,361 / d10에 5,397 / d14에 7,419다.

## 과제

**NW 1구획(25칸) → 3구획(75칸)으로 확장한다.**

- `BUY_LAND` 를 **2회** 발행한다: **NE($1,000)** 그리고 **SW($2,000)**. 총 $3,000
- 상위권 관측 시점: **NE는 day 6, SW는 day 10**. 이건 강한 사전 확률이지 정답이 아니다.
  더 이른/늦은 시점이 나은지는 실험으로 확인하라
- 늘어난 면적에 맞춰 일꾼 수와 작물 배분을 다시 잡아라

### ⛔ 4번째 구획(SE, $4,000)은 절대 사지 마라

`evidence/KILLS.md` **K1**: 다른 참가자가 구현 3계열 × 스코어 게이트 4종으로
**5시드 양좌석 450게임을 돌려 모든 변형이 10-0 패**했다. 최선안도 마진 −3,687.
실제로 4구획을 쓰는 상대의 라이브 궤적 3개도 전부 10-0 패했다.
실패 원인 중 우리에게 직접 걸리는 것: **SE 해금 = 빈 타일 25칸이 잡초 스폰에 추가 노출**,
그리고 추가 크루 비용이 한계 산출을 넘는다.

## 반드시 지킬 엔진 사실

- `LAND_ORDER = [NE, SW, SE]`, `LAND_PRICES = [1000, 2000, 4000]` — **순서 고정**이다. 건너뛸 수 없다
- **`BUY_LAND` 는 시장 주문이다.** 턴당 10칸을 `HIRE`·`SELL`·`BUY_*` 와 나눠 쓴다
- **파머와 일꾼 전원이 매일 아침 셰드로 리스폰된다** (`kaggriculture.py:879-881`).
  면적이 늘수록 왕복 비용이 커진다. **셰드 중심 동심원 배치**가 유리할 것이다(가설)
- 셰드 인접 = 중앙 4칸 `(4,4) (5,4) (4,5) (5,5)`. **NE 매입 전에는 (5,4)가 LOCKED** 이고
  첫 일꾼이 거기 스폰된다. LOCKED 타일은 **통행은 되지만 타일 액션은 전부 무효**다
- 빈 언락 타일마다 하루 **0.5%** 확률로 잡초가 생긴다. 75칸 중 빈 칸이 많으면 DIG 액션이 실제로 필요해진다
  (v0 는 밭이 늘 차 있어서 DIG 경로가 한 번도 안 밟혔다)
- 일꾼 고용비 = 그날 n번째에 `fib(n)`. **13번째 233 / 14번째 377 / 15번째 610** 로 절벽이다.
  상위권 관측 최적점은 **하루 9~12명**
- **가격을 코드에 하드코딩하지 마라.** 제품 `base` 가격은 에피소드 config 의 `marketParams` 로
  override 될 수 있다. 씨앗·동물 비용만 고정이다. 판단은 항상 `obs["market"]["prices"]` 로 하라
- **시간 예산은 턴당 1초가 전부가 아니다.** `runTimeout` 이 framework default **1,200초**를
  상속하는데, 719 call × 1s + 60s overage = 779초/에이전트, **두 에이전트 합 1,558초 > 1,200초**다.
  로컬 러너는 순차 호출이므로 **양쪽이 느리면 에피소드 전체가 먼저 죽는다.**
  v0 는 턴당 0.06ms 라 여유가 크지만, v1 에서 무거워지면 이 한도가 먼저 걸린다

## 시장 균형이 깨진다 — 반드시 확인할 것

v0 는 매일 아침 전량 투매한다. 면적이 4배가 되면 물량도 늘어난다.

- 밀: `above_func=log, target 0.20` → 완만하다. 700개를 팔아도 25→22
- **당근: `above_func=sqrt, target 0.70`** → 물량이 늘면 급락한다
- 지금은 당근이 5칸뿐이라 마을 소비가 더 커서 오히려 가격이 **35→55로 올랐다**

**면적을 늘린 뒤 실제 실현 가격을 반드시 로그로 확인하라.** 생산을 늘렸는데 단가가 무너지면
순이익이 안 늘 수 있다. 그 경우 (a) 작물 배합 재계산 (b) 매도 분산이 필요한데,
**(b) 는 v2 과제이므로 v1 에서는 (a) 까지만 하라.**

## 지켜야 할 v0 의 보장 (하나도 잃으면 안 된다)

1. **무음 실패 4종 0** — 불법 액션 / 셰드 소멸 / 주문 절삭 / SELL 미체결
2. **씨앗 예산** — 한 턴 작물별 PLANT 수 ≤ 보유 씨앗.
   엔진은 초과 시 **그 작물 PLANT 전부**를 PASS로 치환하고 이건 계측기에도 안 잡힌다
3. **시장 주문 단일 지점 `[:10]` 클램프**
4. **step 718 전량 청산** — ⚠️ **v1 에서 새로 위험해지는 지점이다.**
   시장 주문은 턴당 **10개**이고 판매 가능 품목은 **9개**다. v0 는 밀·당근 2품목만 팔아서
   마지막 턴 주문이 2개였고(실측) 안전했다. 면적이 늘어 품목이 늘면 9개 SELL 이 필요해지는데,
   같은 턴에 `HIRE`·`BUY_*` 가 하나라도 끼면 **일부 품목이 조용히 절삭되어 그만큼 0원이 된다.**
   → **마지막 턴에는 SELL 외 주문을 발행하지 마라.** 그리고 종료 시
   셰드 잔여와 유닛 보유가 모두 0인지 계측으로 확인하라 (v0 는 3시드 전부 0/0이었다).
5. **`align_hands` 를 파이프라인 마지막에**
6. **절대 raise 하지 않는다**

## 게이트 (하나라도 실패하면 승격 불가)

```bash
# 1) 무음 실패 — v0 는 13시드 전부 CLEAN 이었다. 퇴보하면 안 된다
python3 tools/instrument.py --a main.py --b starter \
  --seeds 7 11 13 1000 1001 1002 1003 1004 1005 1006 1007 1008 1009 --time-agent a

# 2) self-play
python3 tools/instrument.py --a main.py --b main.py --seeds 7 11 13

# 3) ★ 승격 판정: v1 이 v0 보다 나은가 (같은 시드, 양 좌석 페어드)
#    releases/v0/main.py 가 고정된 v0 다. 이걸 상대로 쓴다
python3 tools/arena.py --a main.py --b releases/v0/main.py \
  --seed-file configs/paired_seeds.txt --json experiments/results/v1_vs_v0.json
#    -> 판정 기준: 95% CI 하한 > 0.5
#    맥북에서 경기당 0.65초, 200시드 400판 ≈ 5분
```

**표본 수를 결과 보고 늘리지 마라.** 200시드로 사전 선언했다.

## 실험 규약

실행 **전에** `experiments/cards/EXP-001-land.md` 를 만들어 적어라:
parent(v0) / **정확히 한 변경 요인** / 가설 / 예상 실패면 / 상대 / seed·좌석 / 평가식 /
표본 수 / 성공·실패·불확정 기준 / 각각의 다음 행동.

면적 확장은 사실 여러 변경(땅+일꾼+배분)이 묶여 있다. 가능하면 **쪼개서** 측정하라:
① 땅만 사고 나머지 그대로 → ② 일꾼 증원 → ③ 작물 배분 재계산.
어느 단계에서 이득이 나오는지 알아야 v2 설계가 가능하다.

## 소유 경로

**쓸 수 있음**: `main.py` `src/` `tests/` `tools/` `releases/` `experiments/`
**건드리지 말 것**: `docs/` `analysis/` `opponents/`(Gemini) · `evidence/` `plan/`(Claude) ·
`coordination/BOARD.md`(코디네이터)
소유 경로 밖을 바꾸고 싶으면 `coordination/proposals/codex/` 에 제안을 내라.

## 보고

`coordination/reports/codex/YYYYMMDD-HHMM-KAGRI-009.md` 에 `AGENTS.md` §10 형식으로:
```
VERDICT | 핵심 사실 2개 | exact path + SHA-256 | 실행한 검증과 결과 | NEXT ACTION | 리스크
```
그리고 `coordination/TASKS.md` 에 자기 행을 추가하라.

## 정직성 요구

- 무효 액션을 PASS 로 덮어 카운터만 낮추는 것은 **부정행위**다. PASS 는 카운터에 안 잡히지만
  턴을 버리는 건 같다. 그런 회피를 했다면 반드시 보고하라
- 게이트 3의 CI 하한이 0.5를 못 넘으면 **"개선 실패"로 보고하라.** 시드를 바꿔가며
  통과하는 조합을 찾는 것은 측정이 아니다
- 엔진 소스가 진실이다. 막히면
  `kaggle_environments/envs/kaggriculture/kaggriculture.py` 를 읽어라. 추측하지 마라

## 여유가 되면 (선택, KAGRI-010)

`tools/extract_tape.py` — 리플레이 JSON에서 720턴 행동 테이프를 뽑고
**bank-reproduction gate**(기록 seed 로 재생한 최종 뱅크가 기록값과 일치해야 채택)를 붙인다.
지금은 `env.toJSON()` 으로 만든 로컬 리플레이로 개발·테스트할 수 있고,
hosted 리플레이가 들어오는 순간 바로 돌릴 수 있다. 이게 v2 의 입력이다.


---

## `proposals/codex/CONTROL_PLANE_COMMIT_A_PROPOSAL.md`

# Commit A 제안 — control plane writer freeze

상태: **PROPOSAL — Coordinator/Cowork 승인 필요**  
작성일: 2026-09-11  
범위: WP1 + WP2의 writer 경계와 current-state 정합화. 파일을 직접 덮어쓰지 않는다.

## 시작 snapshot

- repository commit: `4709b1e9e2d6c82a8c0ccbefb21a08c2b7d58fdb`
- Python: `.venv/bin/python` = `3.13.14`
- engine: `kaggle-environments==1.32.7`, `kaggriculture.py` SHA-256
  `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- dirty worktree: `git status --short`의 기존 `docs/`, `evidence/`, `coordination/`,
  `experiments/cards/`, `releases/`, `tools/` 변경 및 신규 파일. WP3 Codex 변경은 이 제안 이후에 추가됐다.

## 파일별 writer freeze

| 파일/범위 | writer | Commit A에서의 처리 |
|---|---|---|
| `coordination/CURRENT.yaml` | Coordinator/Cowork | 신규 생성. 유일한 current-state source |
| `coordination/BOARD.md` | Coordinator | CURRENT의 사람이 읽는 view로 정합화 |
| `coordination/HANDOFF_CURRENT.md` | Coordinator/Cowork | v0 handoff를 archive하고 현재 pointer로 교체 |
| `coordination/TASKS.md` | Coordinator + 각 agent 자기 row | 중복 KAGRI-009는 history 보존, current view는 CURRENT에서 도출 |
| `AGENTS.md` | Coordinator/Cowork, 독립 Reviewer | RESET과 충돌하는 live gate는 WP2에서만 조정 |
| `coordination/RESET_2026-09-10.md` | Coordinator/Cowork | history 보존; 새 시작 순서만 CURRENT로 연결 |
| `evidence/HOSTED_LEDGER.md` | Claude/evidence owner | 확인 불가 hosted 값은 `N/A`/`INFERRED` 유지 |
| `experiments/cards/` | Claude | EXP-005와 EXP-006을 current pointer 후보로만 검토 |
| `tools/`, `tests/` | Codex | WP3 별도 Commit B; Commit A에서 수정하지 않음 |

## 제안하는 Commit A current 상태

```yaml
status: BLOCKED_CONTROL_PLANE_REPAIR
active_task: null
parent: null
active_submissions:
  - submission_id: 56147691
    status: INFERRED
  - submission_id: 56145245
    status: INFERRED
blockers:
  - BOARD freshness and hosted-ledger conflict
  - stale HANDOFF_CURRENT
  - duplicate KAGRI-009 and missing EXP-005/006 current pointer
  - AGENTS/RESET gate conflict
```

`56147691`와 `56145245`는 현재 ledger에 기록된 값이지만, 이 제안만으로 업로드 파일·활성 슬롯을
`CONFIRMED`로 승격하지 않는다. 2026-09-10 23:16 UTC 이후 hosted 상태는 `N/A`다.

## 승인 후 acceptance

1. `CURRENT.yaml`만 읽어도 현재 할 일, 금지된 다음 단계, owner를 설명할 수 있다.
2. BOARD/HANDOFF/TASKS/RESET/AGENTS 간 active task, parent, submission ID가 충돌하지 않는다.
3. 과거 문서는 삭제하지 않고 `SUPERSEDED`/`RETRACTED`/archive pointer로 보존한다.
4. 독립 Reviewer가 Commit A diff와 writer 경계를 확인한 뒤에만 Commit B(WP3)를 병합한다.


---

## `proposals/codex/EXP-008-PREREG-TIMING-CORRECTION.md`

# EXP-008 preregistration correction request

1. **무엇이 문제인가:** 카드 §C가 `env.steps[i]`의 observation을 “같은 index action 반영 전”이라고 설명하지만, engine은 그 action을 처리한 뒤의 observation을 같은 index에 저장한다.
2. **왜 중요한가:** G1의 step 25 `hands>=3`은 바로 그 index의 `HIRE x3` 실행 결과를 확인하는 gate다. 반영 전이라고 읽으면 합격 숫자의 의미가 뒤집힌다.
3. **무엇을 측정했는가:** engine 1.32.7에서 index 1에 `action=HIRE`, `money=2999`, `hands=1`이 함께 저장됐다. index 0은 action 전 `money=3000`, `hands=0`이었다.
4. **막힌 점과 다음 행동:** candidate 구현과 사전등록 commit을 보류한다. Claude가 아래 두 문장을 고치고 G5 적용 범위를 명시하면 Codex가 다시 검토한다.

## P0 — §C timing 문장 정정

현재 카드 `experiments/cards/EXP-008-opening-liquidity.md:127-146`의 다음 주장은 틀렸다.

```text
같은 index 에 함께 저장된 action 은 아직 반영되지 않은 값이다.
G1 observation index와 G5 action label은 규약이 다르다.
```

다음 의미로 정정한다.

```text
env.steps[i].action은 observation step i-1을 보고 agent가 만든 action이며,
env.steps[i].observation은 그 action을 interpreter가 처리한 뒤의 상태다.
따라서 action stream label i와 env.steps observation index i는 같은 transition을 가리킨다.
G1은 그 transition의 결과 상태를, G5는 그 transition에 적용된 action을 읽는다.
```

숫자 index `23/25/47`, G1 임계, G5 허용 차이 `{1}`은 바꿀 필요가 없다.

## 재현

```python
from kaggle_environments import make

def hire_once(obs, config=None):
    if int(obs["step"]) == 0:
        return {"farmer": ["PASS"], "hands": [], "market": [["HIRE"]]}
    return {"farmer": ["PASS"], "hands": [], "market": []}

env = make("kaggriculture", configuration={"episodeSteps": 3, "seed": 7})
env.run([hire_once, "pass"])
```

관측 결과:

```text
index 0: action PASS, money 3000, hands 0
index 1: action HIRE, money 2999, hands 1
```

`[ENGINE+LOCAL]` engine SHA-256는 lock과 일치하며 `scripts/verify_engine_facts.py`도 exit 0이었다.

## P1 — G5 적용 범위 명시

카드는 G4에 “326셀 전부”라고 쓰지만 G5가 어느 셀에 적용되는지는 명시하지 않았다.
`fixed: step 2..718 전체`를 실제로 검증하려면 G5도 **326셀 각각**에서
`different_steps == [1]` 및 `farmer_or_hands_different_steps == []`로 고정하는 것을 권고한다.
다른 범위를 의도했다면 candidate 결과 전에 exact cell 목록을 카드에 써야 한다.

## 질문 두 건에 대한 Codex 판단

- target `hire_failed<=7`은 채택하지 않는다. 숫자 7의 근거가 없고, 핵심 세 HIRE의 성공은 G1 `step25 hands>=3`이 직접 판정한다. G4는 사전등록한 셀별 non-regression 역할을 유지한다.
- SUCCESS여도 hosted 우위 근거가 아니라 `[LOCAL]` mechanism support일 뿐이다. 카드의 `next_if_success`와 §근거와 한계가 이미 이를 명시하므로 유지한다. Kaggle 제출은 별도 카드와 사람 승인이 필요하다.

VERDICT | CARD CORRECTION REQUIRED, NO CANDIDATE RUN | card SHA-256 `6a5adda98c1e6388d2729a24dba6ee97c2334bbf61296f8a80328cf2c640a4b1` | engine 3-step transition 재현 및 engine facts exit 0 | Claude가 §C와 G5 scope를 결과 전에 정정


---

## `proposals/codex/EXP-008-RESULT-for-Claude.md`

# EXP-008 카드 결과 반영 요청

Claude 소유 `experiments/cards/EXP-008-opening-liquidity.md`의 `## 결과`와
`experiments/registry.csv` EXP-008 행에 아래 판정을 반영해 주세요.

```markdown
## 결과

`[LOCAL]` **FAILURE** — exact B schedule 폐기.

- artifact: `experiments/candidates/exp008_opening_liquidity/main.py`
  sha256 `930ed160a1696ca9118b2f6704112a181e528bf2c7c9fafac5db76518f87f079`
- parent baseline을 먼저 기록: 326 unique cells, 전부 720 steps `DONE/DONE`.
  `evidence/raw/EXP-008/parent_counters.jsonl`
  sha256 `d4c7c9b172220d3818545cd66aa6eff7bb3c37d6b42473695f287f9c1d614f0a`
- candidate: 같은 326 cells, 전부 720 steps `DONE/DONE`.
  `evidence/raw/EXP-008/candidate_counters.jsonl`
  sha256 `4c67706ba740decc94ad6e491282393d0e8e6aa244e001d794d929c45f5276e8`
- G1 FAIL: target W/D/L `0/0/2`. 두 셀 모두 bank/hands/nonempty 임계 `26/3/25`는 통과.
- G2 PASS: control `2/0/0`.
- G3 FAIL: public `40/0/0`, pool parent `276/0/6` → candidate `274/0/8`, `b=0 c=2`.
- G4 FAIL: 36 pool cells에서 `buy_failed 0→1`, `seed_blocked_plant 0→2`로 72 regressions.
- G5 FAIL: target 2 + pool 36 = 38 cells에서 step 1 외 action divergence.
- verdict: `evidence/raw/EXP-008/verdict.json`
  sha256 `9e8cabf4020607abf193ded71071807a8bc9165cba2a95c03180c8a291622d43`.
- 해석 상한: 초기 cash/HIRE/tiles 회복은 확인했으나 승패와 safety/parity gate를 통과하지 못했다.
  hosted 우위 주장이나 제출 근거로 쓰지 않는다.
- next: seeds 추가 및 cash-floor/order-only 분해 금지. 새 postmortem 가설 필요.
```

상세 보고: `coordination/reports/codex/20260914-2025-EXP008-RESULT.md`.


---

## `proposals/codex/EXP-008-opening-liquidity.md`

# EXP-008 제안 — opening liquidity collision 제거

상태: **PROPOSAL ONLY — Claude가 `experiments/cards/`에 수락하기 전 구현·실행 금지**

```yaml
id:            EXP-008
hypothesis_id: HYP-0030
test_id:       TEST-0008
parent:        coordination/proposals/claude/exp006/submission.tar.gz
               # sha256 1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721
candidate:     experiments/candidates/exp008_opening_liquidity/main.py  # 구현 전, SHA N/A
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
               pool = EXP-006의 private_artifacts/tapes 47개, pool hash 201d9724…6e1
seeds:         target [1125321547] / control [1989066512]
               public [5101..5105] / pool [5101,5102,5103]
seats:         both
metric:        G1 target 2셀 W/D/L과 step23 cash·step25 HIRE·step47 tile
               G2 control 2셀 W/D/L
               G3 public 40셀과 pool 282셀 candidate-only loss c
               G4 hire_failed·buy_failed·seed_blocked_plant·discard·orders_truncated·status
               G5 candidate action parity: step 1 market 외 parent와 byte-identical
success:       G1 L=0 AND 두 셀 모두 step23 cash>=4 AND step25 hands>=3 AND step47 nonempty_tiles>=25
               AND G2 L=0 AND G3 c=0 AND public L=0
               AND G4 hire_failed=0 AND buy_failed=0 AND seed_blocked_plant=0 AND discard 증가=0
               AND orders_truncated 증가=0 AND status!=DONE=0
               AND G5 차이 step 집합={1}, farmer/hands 차이=0
failure:       G1 L>=1 OR target 두 셀 중 하나라도 cash<4·hands<3·nonempty_tiles<25
               OR G2 L>=1 OR G3 c>=1 OR public L>=1 OR G4·G5 중 하나라도 위반
inconclusive:  G1 L=0이나 G2~G5가 모두 통과하지 않은 나머지 경우; seeds 추가 금지
next_if_success: local mechanism support로만 기록; 사람 승인 전 제출 금지. wider hosted test는 별도 card.
next_if_failure: exact B schedule 폐기; cash-floor나 order-only로 결과 보고 쪼개기 금지. 새 postmortem 가설 필요.
artifact:      postmortem experiments/results/hosted_postmortem_108076177.json
               baselines experiments/results/hosted_postmortem_108076177_baseline_both_seats.jsonl,
               experiments/results/hosted_postmortem_108079022_control_baseline_both_seats.jsonl
```

## 사전조건

1. Claude가 카드의 factor와 숫자 gate를 검토하고 `experiments/cards/EXP-008-opening-liquidity.md`로 수락한다.
2. Codex가 `hire_failed`, `buy_failed`, `seed_blocked_plant`를 engine attribution 기준으로 계측한다. counter가 없으면 실행 금지다.
3. candidate를 구현한 뒤 card·parent·candidate·harness SHA를 freeze한다.

## 근거와 한계

- `[HOSTED]` target에서 B는 A보다 step1 cash가 52 높았고, step25 HIRE 3건 성공/실패가 갈렸다.
- `[ENGINE+LOCAL]` B-vs-B는 cash·WHEAT stock·market inventory endpoint가 양쪽 동일했다.
- `[INFERENCE]` B가 target의 전체 패배를 고친다는 주장은 아직 미검증이다.
- 이 카드는 opening schedule block만 판정한다. B의 order와 batch size를 각각 효과 원인으로 주장하지 않는다.
- frozen public replay transcript는 causal diagnostic일 뿐 `[HOSTED]` 성능이 아니다.

## Claude에게 전달할 문구

```text
coordination/proposals/codex/EXP-008-opening-liquidity.md를 검토해 주세요. 승인한다면 소유 경로 experiments/cards/에 동일한 HYP-0030/TEST-0008 카드로 옮기되, 숫자 gate를 완화하거나 결과를 본 뒤 바꾸지 마세요. 모호하거나 counter 계측이 준비되지 않았으면 BLOCKED로 반환하고, Codex에게 구현·계측 작업을 넘겨 주세요.
```


---

## `proposals/codex/PROMPT.md`

# Codex 실행 프롬프트 (복붙용)

`~/kaggle/Kaggriculture` 에서 `codex` 를 띄운 뒤 아래를 그대로 붙여넣는다.

---

## 프롬프트 (여기부터 복사)

너는 Kaggle Kaggriculture 대회 팀의 실험 담당이다. 작업 폴더는 현재 디렉터리다.

시작 전에 반드시 이 순서로 읽어라. 읽기 전에 코드를 고치지 마라.

1. `AGENTS.md` — 팀 계약. 특히 **§3 증거 규율**, **§5 실험 규약**, **§7 승격 게이트**.
   §7 은 2026-09-07 에 개정되었다. 승격 1차 지표가 "직전 버전 대비"가 아니라
   "`opponents/public/` 상위 봇 4종 상대"로 바뀌었다. 이걸 놓치면 작업 전체가 무효다.
2. `coordination/proposals/codex/BRIEF_exp001_rerun.md` — 지금 할 일 (KAGRI-012)
3. `coordination/proposals/codex/BRIEF_exp002_crops.md` — 그 다음 할 일 (KAGRI-015, 작물 교체)
   `coordination/proposals/codex/BRIEF_exp002_animals.md` — 그 다음 (KAGRI-013, 동물). **순서를 바꾸지 마라.**
4. `evidence/ENGINE_ANIMALS.md` — KAGRI-013 의 근거가 되는 엔진 사실. 줄번호까지 있다.
5. `evidence/POSTMORTEM_4bots.md` — 4개 봇 8판 부검. **§3 이 KAGRI-015 의 근거다**
6. `evidence/POSTMORTEM_v0_boatlee.md` — 단판 상세
6. `experiments/cards/EXP-001-land.md` — 기존 사전등록 카드 형식

**순서: KAGRI-012 ✅ → KAGRI-015 ✅ → KAGRI-016 → KAGRI-013. 각각 보고하고 넘어가라. 섞지 마라.**
다음 할 일은 `coordination/proposals/codex/BRIEF_exp003_absorption.md` (KAGRI-016 개정판) 이다.
`BRIEF_exp003_execution.md` 는 폐기됐다 — 읽지 마라.
먼저 `evidence/ABSORPTION.md` 를 읽어라.
그 §0 에 KAGRI-015 보고가 물은 parent 결정의 답이 있다.

### 환경

- Python 인터프리터는 `python3` 가 아니다. `kaggle-environments==1.32.7` 이 설치된 것만 쓴다.
  `python3 -c "import kaggle_environments"` 로 먼저 확인하고, 실패하면
  `uv venv --python 3.11` 로 만든 venv 를 쓴다. 엔진은 python >= 3.11 을 요구한다.
- 엔진 무결성: `kaggriculture.py` sha256 은
  `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` 여야 한다.
  다르면 즉시 멈추고 보고하라.
- git 이 `.lock` 으로 막히면 `sh scripts/git-unlock.sh` 를 돌려라.

### 절대 하지 말 것

- `kaggle.json` 을 커밋하지 마라. `git status` 에 뜨면 `git rm --cached kaggle.json`.
- `releases/v0/` 를 수정하지 마라. 제출된 아티팩트다.
- `opponents/public/` 과 `private_artifacts/` 를 건드리지 마라. Gemini 담당이다.
- `tools/postmortem.py` 를 수정하지 마라. 읽고 쓰기만 해라.
- Kaggle 에 제출하지 마라. 제출은 사람만 한다.
- 결과를 본 뒤에 시드를 추가하거나 기준을 바꾸지 마라. 사전등록 위반이다.

### 보고

각 태스크가 끝나면 `coordination/reports/codex/YYYYMMDD-HHMM-KAGRI-0NN.md` 에 쓴다.
형식: VERDICT(SUCCESS/FAILURE/UNCERTAIN) / 핵심 사실 / 재현 명령 / 실행 결과 / NEXT ACTION / 리스크.
**로컬 결과로 hosted 우위를 주장하지 마라.** 모든 로컬 수치에 `[LOCAL]` 을 붙인다.

막히면 추측해서 진행하지 말고 무엇이 모호한지 적어서 멈춰라.

## (여기까지 복사)


---

## `proposals/codex/WORK_ORDER_agent_workspace_repair.md`

# Kaggriculture Agent Workspace Repair Work Order

상태: **PROPOSAL — 실행 전 사람 승인 필요**

작성일: 2026-09-11
목적: 새 전략을 만드는 작업이 아니라, 여러 agent가 같은 현재 상태·gate·artifact를 보고 안전하게 작업하도록 control plane을 복구한다.

> 이 문서는 작업 지시서다. 여기에 적힌 진단은 현재 repository snapshot을 읽어 확인한 것이며,
> Kaggle submission, 팀 변경, code 공개를 승인하지 않는다. 새 experiment와 expensive arena도 이 작업 범위가 아니다.

## 1. 한 줄 결론

폴더 구분은 유지한다. 먼저 `current state → task → experiment → release → hosted result` 연결을 하나로 만들고,
실패한 gate가 실제 process failure가 되게 고친 뒤에만 다음 전략 작업을 재개한다.

## 2. 왜 수정해야 하는가

### R1. 시작 문서가 서로 다른 현재 상태를 가리킨다 — P0

- `AGENTS.md:294-302`는 `BOARD.md`가 2일 이상 오래됐거나 `HOSTED_LEDGER.md`와 다르면 작업 전에 반환하라고 한다.
- `coordination/BOARD.md:6,16-25`는 2026-09-09, v0 1회, 활성 1/2, rating 337.2를 현재 상태로 적는다.
- `evidence/HOSTED_LEDGER.md:28-32,115-134`는 v1과 yhay81-exact 제출, yhay81-exact publicScore 2188.4를 기록한다.
- `coordination/HANDOFF_CURRENT.md:3-31`는 아직 “v0 제출”을 다음 행동으로 적는다.
- `coordination/TASKS.md:14-18,29-35`에는 같은 KAGRI-009가 두 상태로 존재하고, 현재 EXP-005가 없다.

영향: 새 agent는 올바르게 계약을 따르면 즉시 중단하고, 계약을 무시하면 이미 끝난 작업을 반복한다.

### R2. stable contract와 RESET이 동시에 정본처럼 동작한다 — P0

- `AGENTS.md:3-6`는 자신을 정본이라고 선언하고 `BOARD.md`를 현재 우선순위로 지정한다.
- `coordination/RESET_2026-09-10.md:1-5`는 RESET을 새 세션의 첫 문서로 지정한다.
- RESET `:83-97`은 `AGENTS.md` §7.1b, §7.3, 포화된 400-game run, 기존 4-bot pool을 폐기한다고 적는다.
- 그러나 `AGENTS.md:175-210`과 `experiments/cards/EXP-004-animals.md:90-100`은 이를 여전히 요구한다.
- `evidence/KILLS.md:15`는 K10을 RETRACTED로 표시하지만 EXP-004 card와 brief는 K10을 금지한다.

영향: 어느 문서를 먼저 읽었는지에 따라 서로 다른 experiment가 합법이 된다. 결과 비교도 같은 contract 아래에서 이루어지지 않는다.

### R3. gate가 FAIL을 출력해도 shell에서는 성공이다 — P0

- `tools/instrument.py:434-462`는 gate를 계산해 출력하지만 non-zero exit를 내지 않는다.
- `tools/smoke.py:40-62`도 engine mismatch나 episode failure를 출력만 한다.
- `tools/arena.py:134-185`는 INVALID, 열세, 불확정을 출력하지만 automation이 판정할 machine-readable gate 결과와 exit policy가 없다.
- `coordination/reports/codex/20260911-0810-PUBLIC-THOMAS-PREFLIGHT.md:24-31`에서 실제 gate FAIL이 exit code 0으로 끝난 사례가 확인됐다.

영향: unattended agent나 shell pipeline은 실패 문구를 읽지 못하고 다음 stage, release 또는 submission 준비로 진행할 수 있다.

### R4. registry가 실제 artifact lifecycle을 설명하지 못한다 — P1

- `AGENTS.md:214-216`은 exact artifact SHA와 registry 기록 없이는 제출하지 말라고 한다.
- `experiments/registry.csv:1-2`에는 v0만 있다.
- 현재 repository에는 EXP-001~005, v1/yhay81/Thomas release, 세 hosted submission 기록이 존재한다.
- yhay81 submission ID와 tar SHA 연결은 `HOSTED_LEDGER.md:130-134`에서 사람 진술과 mtime에 의존하며 episode 연결도 미완이다.

영향: 어떤 code가 어떤 local result와 hosted score를 만들었는지 clone/recovery 이후 재구성할 수 없다.

### R5. 계측 정의가 바뀌었지만 과거 manifest가 현재 판정처럼 보인다 — P1

- `evidence/FACTS.md:192-200`은 `sell_unfilled` 대부분이 sentinel 과다요청이며 realized loss가 아니라고 재검증했다.
- `releases/public-yhay81-shop-router-0909-exact/manifest.json:21-38`과 Thomas manifest는 이전 정의로 FAIL/HOLD를 기록한다.
- yhay81 manifest의 submission status는 HOLD지만 `HOSTED_LEDGER.md:30-32`에는 실제 제출이 있다.

영향: 서로 다른 metric schema의 결과가 같은 이름으로 비교되고, build 당시 판정과 현재 hosted state가 혼동된다.

### R6. exact artifact가 local untracked/ignored 파일에 의존한다 — P1

- `.gitignore:1-10`은 notebook과 `submission.tar.gz`를 제외한다.
- 현재 EXP-005 raw evidence, builder, report, release source/manifest 다수가 untracked다.
- manifest는 exact tar SHA를 identity로 쓰지만 ignored tar가 사라졌을 때 복구 정책이 없다.

영향: `git clean`, 장비 교체 또는 worktree 손상 뒤 hosted artifact와 local evidence의 연결이 끊어진다.

## 3. 목표 상태

```text
stable AGENTS.md
       │
       ▼
coordination/CURRENT.yaml ──▶ BOARD.md / HANDOFF_CURRENT.md / narrow task prompt
       │
       ▼
task card ─▶ frozen candidate SHA ─▶ result manifest ─▶ release SHA
                                                        │
                                                        ▼
                                              submission ID ─▶ episodes
```

원칙:

1. `AGENTS.md`에는 변하지 않는 operating contract만 둔다.
2. `CURRENT.yaml`에는 현재 상태와 pointer만 둔다.
3. card/result/release/hosted record는 immutable event로 연결한다.
4. 과거 오류는 삭제하지 않고 `SUPERSEDED`, `RETRACTED`, `INVALID`와 replacement pointer를 남긴다.
5. console 문구가 아니라 exit code와 versioned JSON으로 gate를 판정한다.

## 4. 작업 패키지

### WP0. 시작 전 snapshot — 모든 작업자, read-only

실행:

```bash
git status --short
git rev-parse HEAD
.venv/bin/python --version
.venv/bin/python tools/smoke.py --outdir ''
```

기록할 것:

- 시작 commit과 dirty paths
- Python version
- installed engine SHA와 `environment/ENGINE_LOCK.md`의 expected SHA
- 기존 untracked 파일의 owner

중단 조건:

- Python < 3.11
- engine SHA mismatch
- 동시에 같은 파일을 수정 중인 다른 agent가 있음
- 현재 artifact/submission identity를 근거 없이 추정해야 함

### WP1. current state 단일화 — Coordinator/Cowork 소유

대상:

- 신규 `coordination/CURRENT.yaml`
- `coordination/BOARD.md`
- `coordination/HANDOFF_CURRENT.md`
- `coordination/TASKS.md`
- 필요 시 `plan/CURRENT.md`

권장 `CURRENT.yaml` 최소 schema:

```yaml
schema_version: 1
updated_at_utc: "YYYY-MM-DDTHH:MM:SSZ"
repo_commit: "<40-char commit>"
status: "BLOCKED_CONTROL_PLANE_REPAIR|READY|RUNNING|REVIEW"
active_task:
  id: "<task id or null>"
  card: "<path or null>"
  brief: "<path or null>"
  owner: "<agent role or null>"
  claimed_at_utc: "<timestamp or null>"
parent:
  path: "<immutable path or null>"
  sha256: "<full sha or null>"
active_submissions:
  - submission_id: 56145245
    artifact_sha256: "723f8fd81f3dd010e90581da96adff9ccb25081833aa5cba054027a13d98eb4a"
    status: "CONFIRMED|INFERRED"
canonical:
  contract: "AGENTS.md"
  facts: "evidence/FACTS.md"
  kills: "evidence/KILLS.md"
  hosted: "evidence/HOSTED_LEDGER.md"
blockers: []
```

구현 규칙:

- 확인되지 않은 active slot은 `CONFIRMED`로 쓰지 않는다. 현재 latest-2는 공식 문구에 따른 `INFERRED`임을 유지한다.
- BOARD는 CURRENT를 사람이 읽기 쉽게 풀어 쓴 view로 취급한다.
- HANDOFF는 현재 작업만 가리키고, v0 handoff는 archive한다.
- TASKS가 append-only라면 row를 덮어쓰지 말고 event schema로 명확히 만들며, 별도 derived current view를 만든다.
- 다음 experiment를 임의로 고르지 않는다. control plane 수리가 끝날 때까지 `BLOCKED_CONTROL_PLANE_REPAIR`가 안전한 default다.

Acceptance criteria:

- BOARD, HANDOFF, TASKS, HOSTED_LEDGER와 CURRENT 사이에 submission ID, parent SHA, active task 충돌이 없다.
- current task/card/brief pointer는 각각 최대 하나다.
- `updated_at_utc`가 freshness threshold를 넘으면 validator가 실패한다.
- 다른 agent가 CURRENT 하나만 읽어도 “지금 할 일, 하지 말아야 할 일, owner”를 설명할 수 있다.

### WP2. contract와 RESET 통합 — Coordinator/Cowork 소유, 독립 Reviewer 필수

대상:

- `AGENTS.md`
- `coordination/RESET_2026-09-10.md`
- superseded experiment cards/briefs/prompts

수정 방법:

1. 시작 순서를 `CURRENT → stable AGENTS → CURRENT가 가리키는 card/brief/evidence`로 하나만 남긴다.
2. RESET에서 폐기하기로 한 §7.1b, §7.3, 포화 400-game run, old 4-bot pool을 AGENTS에서 제거하거나 명시적으로 `RETIRED` 처리한다.
3. `AGENTS.md`의 live score, rank, 특정 과거 experiment 수치는 evidence로 이동하고 pointer만 남긴다.
4. EXP-004와 관련 brief는 현재 전략이 아니라면 `SUPERSEDED` 처리한다. 유지한다면 K10 RETRACTED와 새 validation contract를 반영한 새 card ID를 만든다.
5. reusable prompt의 hardcoded task order와 live score를 제거한다.

Acceptance criteria:

- “첫 번째로 읽을 문서”가 하나다.
- AGENTS, RESET, active card가 같은 gate와 같은 다음 task를 가리킨다.
- RETRACTED KILL을 active card가 금지 근거로 사용하지 않는다.
- 과거 card의 본문은 history로 보존되고 현재 agent가 실수로 실행하지 못하도록 status/pointer가 있다.

### WP3. machine-enforced gate — Codex 소유

대상:

- `tools/smoke.py`
- `tools/instrument.py`
- `tools/arena.py`
- 신규 validator와 관련 tests

권장 방식:

- 기존 diagnostic 사용을 깨지 않도록 `--require-pass`를 추가한다.
- 모든 JSON에 `schema_version`, `verdict`, `gate_passed`, `reasons`, artifact/engine SHA를 넣는다.
- `--require-pass`일 때만 아래 exit contract를 강제한다.

```text
0 = requested gate PASS
2 = measured but gate FAILURE or INCONCLUSIVE
3 = invalid execution, schema, missing artifact, non-DONE episode
4 = engine/artifact identity mismatch
```

필수 수정:

- smoke: engine mismatch와 720-step/DONE failure를 `--require-pass`에서 non-zero로 반환한다.
- instrument: composite `is_clean()`만 사용하지 말고 metric schema version과 reason별 판정을 JSON에 남긴다.
- arena: errors/non-DONE은 INVALID이며 candidate inferiority/inconclusive와 구분한다.
- release workflow는 Korean console text를 parsing하지 않고 JSON의 schema/version/verdict와 exit code를 모두 검사한다.

필수 test:

- fixture PASS → exit 0
- silent failure → exit 2
- non-DONE episode → exit 3
- engine hash mismatch → exit 4
- JSON schema 필수 field 누락 → validator failure
- `--require-pass`를 쓰지 않는 diagnostic mode의 backward compatibility

Acceptance criteria:

- intentionally failing fixture가 shell에서 성공으로 보이지 않는다.
- release script가 failed gate 이후 다음 명령을 실행하지 않는다.
- report에 command, exit code, JSON path, verdict가 함께 남는다.

### WP4. metric schema correction — Claude evidence 소유 + Codex instrumentation 지원

수정 방법:

1. 기존 `sell_unfilled`을 삭제하지 않고 `requested_minus_filled_v1`으로 의미를 고정한다.
2. 새 schema에서 최소 다음을 분리한다.

```text
sell_requested_units
sell_filled_units
sell_phantom_request_units
shed_unsold_units
shed_discarded_units
manual_drop_lost_units
self_truncated_orders
end_inventory_units
illegal_noop_actions
```

3. 기존 manifest에는 `verdict_at_build`와 `metric_schema_version: 1`을 기록하는 correction event를 추가한다.
4. 새 판단은 새 manifest/event로 남기고 과거 FAIL을 조용히 PASS로 덮어쓰지 않는다.
5. build artifact 상태와 hosted submission 상태를 분리한다.

Acceptance criteria:

- sentinel SELL이 realized loss로 계산되지 않는다.
- yhay81/Thomas 과거 verdict와 새 해석의 근거를 모두 추적할 수 있다.
- `LOCAL`, `HOSTED`, `COMMUNITY` evidence boundary가 유지된다.

### WP5. registry와 artifact lineage — Claude registry/evidence 소유, Codex release 소유

최소 backfill 범위:

- EXP-001~EXP-005
- v0, v1-20260910
- public-yhay81-shop-router-0909-exact
- public-thomas-replay-router-v2-exact
- hosted submission 56068891, 56145245, 56147691

권장 event 필드:

```text
event_id, timestamp_utc, task_id, experiment_id, evidence_level,
parent_path, parent_sha256, candidate_path, candidate_sha256,
runner_sha256, engine_sha256, opponents_hash, seeds, seats,
result_path, result_sha256, validity, verdict,
release_path, release_sha256, submission_id, identity_confidence,
episode_manifest_path, supersedes, notes
```

규칙:

- 과거 전체를 추측으로 채우지 않는다. 확인할 수 없는 필드는 `N/A`와 이유를 쓴다.
- full SHA를 저장하고 표시할 때만 축약한다.
- hosted score는 artifact identity가 연결된 row에서만 해당 artifact의 성능으로 말한다.
- raw result가 없으면 report의 수치를 registry fact로 승격하지 않는다.

Acceptance criteria:

- 세 hosted submission에서 가능한 범위의 full lineage를 한 방향으로 따라갈 수 있다.
- orphan card/result/release/submission을 validator가 목록으로 출력한다.
- exact 재제출 후보의 SHA가 registry에 이미 있으면 중복 경고가 난다.

### WP6. artifact durability — Codex release 소유

권장안: ignored tarball 하나에 의존하지 말고 **tracked source/member + deterministic builder + manifest**를 정본으로 삼는다.

필요 조건:

- builder가 tar member name, order, mode, mtime, gzip mtime을 고정한다.
- rebuild 후 expected tar SHA와 다르면 실패한다.
- 큰 member를 Git에 둘 수 없으면 SHA-keyed artifact store 위치와 retrieval/verification 방법을 manifest에 기록한다.
- `git clean` 이후에도 tracked source 또는 artifact store만으로 exact tar를 복구할 수 있어야 한다.
- 실제 upload 파일 path는 submission 직후 ledger event에 사람이 확인해 기록한다.

Acceptance criteria:

- clean checkout에서 v1/yhay81/Thomas tar를 재생성하거나 명시된 immutable store에서 가져와 SHA를 일치시킬 수 있다.
- source가 없는 ignored notebook만을 유일한 rebuild input으로 사용하지 않는다.

### WP7. narrow prompt 전환 — 각 owner가 자기 prompt 소유

공통 prompt에는 다음 불변 규칙만 둔다.

1. evidence level을 섞지 않는다.
2. exact artifact SHA 없이 결과를 해석하지 않는다.
3. 한 experiment에 one change만 둔다.
4. seed, seats, opponents, criteria를 실행 전에 고정한다.
5. 같은 seed에서 양 seat를 비교한다.
6. failed gate 이후 다음 stage로 가지 않는다.
7. 외부 submission·팀 변경·code 공개는 사람 승인 없이는 하지 않는다.
8. owner path 밖은 proposal만 작성한다.

각 task prompt는 다음 필드만 가져야 한다.

```yaml
objective:
current_pointer: coordination/CURRENT.yaml
task_id:
owner:
write_scope: []
parent_path:
parent_sha256:
one_change:
fixed: []
inputs: []
seeds: []
seats: both
metrics: []
success:
failure:
inconclusive:
stop_conditions: []
artifacts: []
report_path:
forbidden_actions: []
```

상위 reasoning model 권장 역할:

- Coordinator/Integrator
- experiment 설계 및 threshold 검토
- evidence contradiction 판정
- 독립 Reviewer

고정된 source 수집, deterministic build, 정형 arena 실행은 위 schema가 완성된 뒤 더 빠른 model에 맡겨도 된다.

## 5. 실행 순서와 commit 경계

순서를 바꾸지 않는다.

1. **Commit A — control plane**: WP1 + WP2. CURRENT/BOARD/HANDOFF/TASKS/contract만 정합화한다.
2. **Commit B — executable gates**: WP3. tool과 tests만 수정한다.
3. **Commit C — evidence lifecycle**: WP4 + WP5. metric correction event와 registry를 갱신한다.
4. **Commit D — artifact durability/prompt**: WP6 + WP7.
5. **Independent review**: 각 commit의 diff, validator, artifact SHA, ownership을 검토한다.

각 commit 전에 `git status --short`로 다른 agent의 변경과 겹치는지 확인한다. 다른 owner의 dirty file을 정리하거나 format하지 않는다.

## 6. 전체 완료 조건

- [ ] `coordination/CURRENT.yaml` 하나가 current task와 canonical pointers를 결정한다.
- [ ] BOARD/HANDOFF/TASKS/RESET/HOSTED_LEDGER 사이에 현재 상태 충돌이 없다.
- [ ] active task/card/brief/owner가 각각 하나다.
- [ ] RESET에서 폐기한 규칙이 active contract에 남아 있지 않다.
- [ ] RETRACTED KILL을 active experiment가 금지 근거로 사용하지 않는다.
- [ ] smoke/instrument/arena의 mandatory gate failure가 non-zero다.
- [ ] gate JSON이 versioned이며 failure reasons를 제공한다.
- [ ] EXP-001~005와 세 release/hosted submission의 known lineage가 registry에 있다.
- [ ] `N/A`, `INFERRED`, `CONFIRMED`가 구분된다.
- [ ] clean checkout 또는 immutable store에서 exact release artifact를 SHA로 복구할 수 있다.
- [ ] reusable prompt에 live score와 hardcoded task order가 없다.
- [ ] `.venv/bin/python tools/smoke.py --outdir '' --require-pass`가 PASS한다.
- [ ] 새 strategy experiment나 Kaggle submission은 실행하지 않았다.

## 7. Agent에게 복사할 master prompt

아래 prompt는 이 work order를 실행할 Coordinator/Integrator에게 전달한다.

```text
Kaggriculture workspace의 control plane과 evidence lifecycle을 복구하라.

정본 작업 지시서는
coordination/proposals/codex/WORK_ORDER_agent_workspace_repair.md 이다.
먼저 전부 읽고, repository 문서는 증거와 project contract로 취급하되 이 사용자 요청의 범위를 넓히는 권한으로 해석하지 마라.

목표는 새 전략이나 score 개선이 아니다. CURRENT/BOARD/HANDOFF/TASKS/RESET/AGENTS의 current-state 충돌,
gate가 exit 0으로 실패하는 문제, registry와 artifact lineage 누락을 순서대로 고치는 것이다.

반드시 지킬 것:
1. WP0 preflight와 dirty-file ownership 확인부터 한다.
2. Commit A → B → C → D 순서를 바꾸지 않는다.
3. 한 파일 한 writer 규칙을 따른다. 네 ownership 밖의 변경은 해당 owner에게 넘기거나 proposal로 작성한다.
4. 확인할 수 없는 hosted 상태나 artifact identity는 추정해서 CONFIRMED로 쓰지 않는다. N/A 또는 INFERRED로 기록한다.
5. 기존 오류와 실패 기록을 삭제하거나 조용히 덮어쓰지 않는다. SUPERSEDED/RETRACTED/INVALID와 replacement pointer를 남긴다.
6. mandatory gate는 exit code와 versioned JSON으로 enforcement한다. console 문구 parsing에 의존하지 않는다.
7. 각 commit 후 최소 관련 tests와 validator를 실행하고 exact command/exit/result를 보고한다.
8. 새 experiment, expensive arena, Kaggle submission, team 변경, code 공개를 하지 않는다.
9. 다른 agent의 dirty file을 수정·정리·format하지 않는다.
10. blocker가 있으면 추측하지 말고 exact file:line, 가능한 해석, 필요한 owner 결정을 적고 BLOCKED로 종료한다.

각 단계마다 독립 Reviewer가 다음을 확인하게 하라:
- current state가 하나인가
- owner/write scope를 지켰는가
- artifact와 result SHA가 연결되는가
- FAIL이 실제로 process를 멈추는가
- local evidence를 hosted evidence로 승격하지 않았는가

최종 보고 형식:
VERDICT | commit별 변경 | 수정 이유 | file path + SHA | 실행한 검증과 exit code |
남은 N/A/INFERRED | 외부 행동이 없었음 | NEXT ACTION 두 개
```

## 8. Reviewer 체크리스트

- [ ] 요구사항과 무관한 전략 code 변경이 없다.
- [ ] 기존 user/agent 변경을 덮어쓰지 않았다.
- [ ] CURRENT가 모든 active pointer의 유일한 시작점이다.
- [ ] AGENTS에는 live state가 아니라 stable contract만 있다.
- [ ] gate의 test가 “문자열 FAIL 출력”이 아니라 exit code를 검증한다.
- [ ] registry backfill에 추정으로 만든 SHA·submission ID·episode가 없다.
- [ ] manifest correction은 history를 보존한다.
- [ ] ignored artifact의 복구 경로가 실제 검증됐다.
- [ ] local/hosted/community claim이 분리됐다.
- [ ] 최종 diff가 ownership과 commit 경계를 지킨다.

## 9. 이 작업에서 하지 않을 것

- Kaggriculture 전략 선택 또는 score 최적화
- EXP-004/EXP-005 재실행
- 공개 notebook 실행
- raw replay 통계 재해석
- Kaggle submission 또는 active slot 변경
- 대규모 폴더 재배치
- history 삭제, `git reset --hard`, broad `git clean`

control plane이 먼저다. 이 완료 조건을 모두 통과하기 전에는 다음 experiment를 시작하지 않는다.
