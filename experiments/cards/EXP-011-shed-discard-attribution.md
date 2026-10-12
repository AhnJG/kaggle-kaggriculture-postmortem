# EXP-011 — `shed_discarded` 원인 귀속 진단 (계측 전용, artifact 무변경)

hypothesis_id: HYP-0031
test_id: TEST-0011

사전등록 2026-09-16 11:20 UTC / 20:20 KST (Claude, opus-5). **실행 전 커밋.**
커밋 후 seeds·좌석·상대·임계·class 정의 변경 금지. 결과를 본 뒤 임계를 고치지 않는다.
개정 r2 2026-09-17 (Claude, opus-5) — Coordinator 실행안
`coordination/proposals/codex/20260917-correctness-path/DECISION.md` sha256 `286c492fd46a731626d08131934f5ba7965fb5c90cb9c333182b37102858a95d`
§3 "공통 충돌" 에 답해 **§D 의 금지 문구 적용 범위만** §D-1 로 한정했다(사람 승인 전까지 원문 유지).
seeds·좌석·상대·임계·class 정의·층·§E acceptance 는 변경하지 않았다. 실행 승인도 아니다.

선행 근거
- 결과 정본 `experiments/results/p1_release_preflight/report.md` sha256 `3b915c2b7adb541caa7c41c86062f57c628e44b0d067aeb5dc46fed78ee9b6b6`
- 집계 `experiments/results/p1_release_preflight/aggregate.json` sha256 `238816a8236ca0dcf415feb91539549813d189c0a43c43d27edf1d3e66a75206`
- manifest `experiments/results/p1_release_preflight/manifest.json` sha256 `46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c`
- 독립 검증 `coordination/reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md` sha256 `fc02423f9a4fbf66f23be56c3f454d051fa0c1e927100542be40c5ff8cb47ad5` — verdict `VERIFIED_LOCAL_FAILURE`
- postmortem `coordination/reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md` sha256 `c77010549217d4f344c93336f890dd79bd1d91141f577192b279220c12d95613`

**이 카드는 전략을 바꾸지 않는다. 제출 artifact를 1바이트도 바꾸지 않는다.**
목적은 `shed_discarded`가 어디서 생기는지 **숫자로 귀속**하는 것뿐이다.
귀속이 끝나기 전에는 repair card(EXP-012)를 사전등록하지 않는다.

---

```yaml
id:            EXP-011
parent:        coordination/proposals/claude/exp006/submission.tar.gz
               # sha256 1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721
               # 이 tar와 그 4개 member는 이 카드에서 읽기 전용이다. 수정 시 IDENTITY_MISMATCH.
candidate:     N/A — 이 카드에는 candidate agent가 없다. 진단 전용 카드다.
one_change:    tools/instrument.py 의 drop hook 을
               "discard 총량만 누적" -> "drop event 1건당 구조화 레코드 1건 기록" 으로 확장한다.
               변경 범위는 engine 래퍼 계측뿐이며 agent artifact·engine 소스·runner 실행조건은 불변.
fixed:         [coordination/proposals/claude/exp006/submission.tar.gz 및 4개 member
                (main.py bba042e0…96b2 / yh_base.py d6d74997…866d / actions.json 17d503f2…95ef / LICENSE.txt cfc7749b…3d30),
                actions.json tape 전체, SHOP_PLANS, clone-preempt logic 과 threshold
                (PREMIUM/MAX_CLONE_DIST=6/FRACTION=2.0/MAX_BATCH=30/MIN_FUTURE_QTY=4/START=120/STOP=680),
                market ordering 과 MAX_ORDERS=10,
                P1b manifest 의 13경기 seed·좌석·상대 전부,
                engine kaggle-environments 1.32.7 (py bc8a5487…653e / json a82c89c1…4867),
                metric schema 3, release zero-gate 기준 8개 counter 각각 0,
                승인된 runtime 기준 623 / 960 / 1200]
hypothesis:    postmortem 인용 — coordination/reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md
               (hosted episode 108076177, Remielle 167,541 vs Sian 58,246, margin −109,295) 은
               "opening cash starvation -> step25 HIRE 3건 실패 -> 생산 계획 연쇄 붕괴" 를 최초 분기로 판정했다.
               P1b 에서 그 exact transcript 를 양 좌석 재현한 target cell 2개의 parent record는
               reward 58,246/167,541 로 hosted 결과와 일치하면서 shed_discarded=209 (record당),
               noop_actions=1,149, hands_length_mismatch=46, daily_max_shed 가 shedCapacity 100 에
               6일 도달한다. 즉 postmortem 이 지목한 붕괴 국면에서 실제 자원 손실이 집중된다.
               본 카드는 그 손실 482단위 각각을 day·unit·item·drop 직전 shed 점유·해당 unit 의 그날
               마지막 action·shed 인접 여부로 귀속할 수 있다는 것만 주장한다. 원인 수정은 주장하지 않는다.
opponents:     P1b manifest 와 동일, 추가·삭제 없음
               self_parent_A = cleanroom/parent/main.py  sha256 bba042e04cff32ab53be2c59c2f5cd9053c8de2bf31632e396ca8faa502896b2
               builtin_starter_1_32_7 = kaggle_environments.envs.kaggriculture.kaggriculture:starter_agent (bc8a5487…653e)
               stress_Remielle_108076177 = private_artifacts/tapes/Remielle_episode-108076177-actions.json sha256 75ea188ed138167b274ce34d20ce3476adfcfe25ee75d6feb7ed4e8de7caa5c4
               exp008_control_today_108079022 = private_artifacts/tapes/today_episode-108079022-actions.json sha256 b1bd786abd851ac053f617eeebd3e36c91d74af63dde947ecb3f575e52faa637
seeds:         self_play [7, 1000, 1001] (parent_A vs parent_A, 3경기)
               builtin_smoke [7, 1000, 1001] x seats [0,1] (6경기)
               hosted_loss_stress [1125321547] x seats [0,1] (2경기)
               exp008_control_counter_violation_stress [1989066512] x seats [0,1] (2경기)
               총 13경기 / gated parent record 16개. 실행 후 추가·교체 금지.
seats:         both
metric:        D1 재현 동일성 / D2 귀속 총량 일치 / D3 필드 완전성 / D4 class 배타성
               + R 런타임 (623 / 960 / 1200)
success:       D1 AND D2 AND D3 AND D4 AND R 전부 통과 (아래 모든 카운트가 정확히 0)
failure:       아래 카운트 중 하나라도 >= 1
inconclusive:  없음. D1~D4·R 은 전부 0/비0 판정이다.
               단, D1~D4 통과 후 §D 의 지배 class 임계를 넘지 못하면 root-cause 판정이
               BLOCKED_AMBIGUOUS_ROOT_CAUSE 이며 이는 카드 실패가 아니라 repair 미승인이다.
next_if_success: §D 의 판정표에 따라 REPAIR_AUTHORIZED / BLOCKED_STRATEGY_BOUNDARY /
                 BLOCKED_AMBIGUOUS_ROOT_CAUSE 중 하나를 기록한다.
                 REPAIR_AUTHORIZED 일 때에만 §E 의 고정 acceptance 로 EXP-012 를 사전등록한다.
next_if_failure: 계측이 경기를 바꾼 것이므로 결과 전체를 INVALID 로 격리하고 어떤 원인 주장도 하지 않는다.
                 계측을 고쳐 같은 13경기를 다시 돌린다. seed·상대·좌석·임계는 그대로 둔다.
artifact:      결과 JSON experiments/results/p1_shed_attribution/ (Codex 소유, 신규 경로)
               기존 P1b 산출물은 읽기 전용이며 덮어쓰지 않는다.
계측:          tools/instrument.py  실행 전 sha256 284dee4cdacfc56aab2125f8a92b41df53e14744cca7a8cafa10b853fb6d0629
               tools/gate_contract.py sha256 3a3e423b3e0afadca8860b7bd2ed2d39ba326a824c8c6a23c4491fde6171353c (불변)
               재집계 참조 scratch/claude_shed_attribution_20260916.py (read-only, exit 0)
```

---

## §A 엔진 사실 — 무엇이 `shed_discarded` 를 만드는가 `[ENGINE]`

`kaggle-environments==1.32.7`, `kaggriculture.py` sha256 `bc8a5487…653e`.

- `:843-856 _drop_inventories_to_shed(private, capacity)` — 모든 unit inventory 를 shed 로 이월한다.
  `room = max(0, capacity - current)` / `take = min(n, room)` 뒤 **`del inv[item]`**.
  즉 `take < n` 인 초과분은 예외 없이 소멸한다.
- `:866-878 _end_of_day` 는 하루의 마지막 스텝에서 player 순서대로 위 함수를 1회씩 호출한 **뒤**
  `farm["farmer"]` 를 리셋하고 `farm["hands"]` 를 비운다.
  → drop 시점에는 그날 마지막 위치와 hands 구성이 아직 살아 있다. 계측은 리셋 **전에** 읽어야 한다.
- `:940-947` 스텝 순서는 `unit actions -> _process_market -> _town_consume -> _decay_plants -> _end_of_day` 다.
  → 그날 마지막 턴의 시장 매도는 drop **앞**에서 처리된다. 매도로 비우지 못한 잔량이 drop 을 만난다.
- `shedCapacity` 기본값 100 (`:553`, `:866`, `:908`).
- 같은 소멸이 in-day 경로에도 있다: `:344-355 DROP`, `:393-411 PLACE`.
  **현재 `tools/instrument.py` 의 drop hook 은 `_drop_inventories_to_shed` 만 감싼다**
  (`:450-461`, `lost = max(0, carried - moved)`).
  → 관측된 482 는 **일일 종료 이월 경로의 손실만**이다. in-day DROP/PLACE 초과분은 **현재 계측되지 않는다.**
  이 카드는 그 미계측분도 함께 세도록 요구한다(§B-4).

## §B 실행 절차 — Codex

1. **신규 계측 추가.** `tools/instrument.py` 에만 변경. agent tar·engine·gate_contract.py·runner 실행조건 불변.
2. **drop event 레코드.** `_drop_inventories_to_shed` 래퍼가 player·day 마다 1건을 기록한다.

```json
{
  "player": 0,
  "day": 26,
  "step": 647,
  "shed_capacity": 100,
  "shed_total_before": 100,
  "shed_before": {"WOOL": 61, "MILK": 39},
  "carried_before": [{"MELON": 3}, {"WHEAT": 2}],
  "unit_last_op": ["HARVEST", "PASS"],
  "unit_pos_at_drop": [[4,5],[9,1]],
  "unit_shed_adjacent_at_drop": [true, false],
  "deposited": {},
  "discarded": {"MELON": 3, "WHEAT": 2},
  "discarded_total": 5,
  "discarded_by_unit": [3, 2],
  "shed_full_turns_today": 11,
  "market_sell_lines_last_turn": [["SELL","WOOL",30]],
  "sell_filled_last_turn": 0
}
```

- `carried_before` 는 orig 호출 **전** 스냅샷이다. 엔진이 `del inv[item]` 하므로 사후 복원은 불가능하다.
- `deposited`/`discarded` 는 엔진과 **같은 순서**(unit index 오름차순, `list(inv.items())` 순서)로
  동일한 greedy 분배를 스냅샷 위에서 재현해 계산한다. 추정값을 쓰지 않는다.
- `unit_pos_at_drop`·`unit_shed_adjacent_at_drop` 은 `_end_of_day` 의 리셋 **전**에 읽는다.
  `_is_shed_adjacent` 판정은 엔진 함수 `:138` 과 동일 기준을 쓴다.
- `unit_last_op` 은 그 day 의 마지막 스텝에서 해당 unit 에 적용된 op 다(엔진이 PASS 로 치환한 뒤의 값).
3. **집계 산출물.** cell 별 JSON 에 `drop_events` 배열과 `drop_event_summary` 를 추가하고,
   `experiments/results/p1_shed_attribution/aggregate.json` 에 16 record × class 표를 쓴다.
4. **in-day 소멸 별도 counter.** `shed_discarded_inday_drop`, `shed_discarded_inday_place` 를 신설한다.
   이 둘은 이번 카드의 **관측 전용**이며 zero gate 에 넣지 않는다(gate 변경 금지).
   기존 `shed_discarded` 의 정의·값은 바꾸지 않는다.
5. **같은 13경기 재실행.** manifest 의 argv 형태를 그대로 쓰되 출력 경로만 신규 디렉터리로 바꾼다.
   기존 `experiments/results/p1_release_preflight/` 는 읽기 전용이다.

## §C 판정 게이트 — 전부 숫자

| gate | 조건 | 임계 |
|---|---|---|
| **D1-a** | tar sha256 / 4개 member sha256 / engine py·json sha256 일치 | mismatch_count == 0 |
| **D1-b** | 13경기 모두 `steps == 720` 그리고 `statuses == ["DONE","DONE"]` | 위반 episode == 0 |
| **D1-c** | 16 gated parent record 각각에서 재실행 값이 frozen 값과 **정확히** 일치: `shed_discarded`, `noop_actions`, `buy_failed`, `hire_failed`, `seed_blocked_plant`, `hands_length_mismatch_count`, `shed_unsold`, `orders_truncated`, `exceptions`, 그리고 episode 별 `rewards` 2개 | mismatch_count == 0 |
| **D2-a** | `sum(drop_events.discarded_total)` 이 record 별 frozen `shed_discarded` 와 일치 (16개 전부) | mismatch_count == 0 |
| **D2-b** | 전체 합 | `== 482` |
| **D2-c** | 각 event 에서 `sum(carried_before) - sum(deposited) == discarded_total` | mismatch_count == 0 |
| **D3** | 482 단위 각각이 `day`·`step`·`unit_index`·`item`·`shed_total_before`·`unit_last_op`·`unit_shed_adjacent_at_drop` 7개 필드 모두 non-null | null_field_count == 0 |
| **D4** | 482 단위 각각이 §D 의 8개 class 중 **정확히 1개**에 속함 | unclassified == 0 AND multi_class == 0 |
| **R-1** | parent record 별 `total_s` | `<= 623` (위반 0) |
| **R-2** | episode `wall_seconds` | `<= 960` (위반 0) |
| **R-3** | episode `wall_seconds` hard ceiling | `< 1200` (위반 0) |

**D1-c 가 하나라도 깨지면 계측이 경기를 바꾼 것이다.** 결과 전체를 INVALID 로 격리하고
어떤 원인 주장도 하지 않는다. 임계를 고쳐 통과시키지 않는다.

frozen 기준값(이 카드에서 고정):

| record | shed_discarded | noop_actions |
|---|---:|---:|
| target_seed-1125321547_seat-0 p0 / seat-1 p1 | 209 / 209 | 1,149 / 1,149 |
| control_seed-1989066512 seat-0 p0 / seat-1 p1 | 7 / 7 | 44 / 44 |
| self_seed-7 p0 / p1 | 7 / 7 | 44 / 44 |
| self_seed-1001 p0 / p1 | 7 / 7 | 44 / 44 |
| self_seed-1000 p0 / p1 | 6 / 6 | 114 / 114 |
| starter_seed-7 seat-0 p0 / seat-1 p1 | 3 / 3 | 136 / 136 |
| starter_seed-1000 seat-0 p0 / seat-1 p1 | 1 / 1 | 101 / 101 |
| starter_seed-1001 seat-0 p0 / seat-1 p1 | 1 / 1 | 112 / 112 |
| **합계 (16 record)** | **482** | **3,488** |

그룹 합: self_play 40 / builtin_smoke 10 / hosted_loss_stress 418 / exp008_control 14.
재현: `python3 scratch/claude_shed_attribution_20260916.py` (exit 0).

## §D class 정의와 원인 판정 — 실행 전 고정

각 **소멸 단위 1개**에 대해 세 축을 기계적으로 계산한다.

- 축 A (`shed_total_before` vs `shed_capacity`)
  - `ROOM_ZERO` : `shed_total_before >= shed_capacity`
  - `ROOM_PARTIAL` : `0 < shed_capacity - shed_total_before`
- 축 B (`unit_shed_adjacent_at_drop`)
  - `ADJACENT` : true
  - `REMOTE` : false
- 축 C (`unit_last_op`)
  - `DEPOSIT_ATTEMPTED` : op ∈ {`DROP`, `PLACE`}
  - `NO_DEPOSIT_ATTEMPT` : 그 외 전부

class = `A|B|C`, 총 8개. 각 단위는 정확히 1개에 속한다.

층(stratum) 고정:
- `S1` = self_play + builtin_smoke + exp008_control = 14 record, **64 단위**
- `S2` = hosted_loss_stress = 2 record, **418 단위**

**지배 class C\*** = `S1` 에서 점유율이 가장 큰 class. 동률이면 지배 class 없음.

**원인 판정 규칙 (결과를 보기 전에 고정):**

| 조건 | 판정 |
|---|---|
| `share(C*, S1) >= 0.80` AND `share(C*, S2) >= 0.80` AND `C*` 가 16 record 중 **14개 이상**에서 그 record 의 단독 최다 class | C\* 를 확인된 원인으로 채택 |
| 위 조건 불충족 | `BLOCKED_AMBIGUOUS_ROOT_CAUSE` — repair card 금지 |

채택된 C\* 에 따른 후속 경로:

| C\* | 판정 | 후속 |
|---|---|---|
| `ROOM_PARTIAL \| * \| *` | `REPAIR_AUTHORIZED` | 여유 용량이 있는데도 이월에 실패했다. EXP-012 의 `one_change` 는 **이월 순서/클램프 단일 지점**으로 제한 |
| `ROOM_ZERO \| ADJACENT \| NO_DEPOSIT_ATTEMPT` | `REPAIR_AUTHORIZED` | 창고에 닿아 있는 unit 이 그날 마지막 턴에 예치를 시도하지 않았다. EXP-012 의 `one_change` 는 **하루 마지막 턴의 예치 경로 1개**로 제한 |
| `ROOM_ZERO \| ADJACENT \| DEPOSIT_ATTEMPTED` | `BLOCKED_STRATEGY_BOUNDARY` | 예치를 시도했으나 용량이 0이었다. 해소하려면 매도량·생산량·tape 중 하나를 건드려야 하는데 셋 다 fixed 다. repair card 작성 금지, 사람에게 이관 |
| `ROOM_ZERO \| REMOTE \| *` | `BLOCKED_STRATEGY_BOUNDARY` | unit 이 창고에 닿지 못한다. 이동 경로는 actions.json tape(fixed) 에 있다. repair card 작성 금지, 사람에게 이관 |

`REPAIR_AUTHORIZED` 가 아니면 **어떤 구현 card 도 승인하지 않는다.**

### D-1 이 금지 문구의 적용 범위 — owner 한정안 (사람 승인 전까지 원문 유지)

원문(2026-09-16 사전등록): "`REPAIR_AUTHORIZED` 가 아니면 **어떤 구현 card 도 승인하지 않는다.**"

Coordinator 실행안 `coordination/proposals/codex/20260917-correctness-path/DECISION.md`
sha256 `286c492fd46a731626d08131934f5ba7965fb5c90cb9c333182b37102858a95d` §3 "공통 충돌" 이
이 문장을 **너무 넓다**고 지적하며, owner(Claude)가 한정 가능성의 근거를 남기고 사람이 그 범위 해석을
승인해야 한다고 요구했다. 그 요구에 대한 owner 의 답이 이 절이다.

**한정안.** 이 문장은 **이 attribution 에서 파생되는 repair**, 즉 `shed_discarded` 를 원인으로 지목하는
HYP-0031 계열 구현 card(EXP-012)에만 적용된다.

**근거 — 아래 1~4 는 전부 이 카드 본문에서만 도출한다.**

1. 카드 서두: "목적은 `shed_discarded` 가 어디서 생기는지 **숫자로 귀속**하는 것뿐이다.
   귀속이 끝나기 전에는 repair card(EXP-012)를 사전등록하지 않는다." — 금지의 대상이 EXP-012 로 명시돼 있다.
2. §D 의 class 세 축(`shed_total_before` / `unit_shed_adjacent_at_drop` / `unit_last_op`)은 전부
   **소멸 단위(shed drop event)** 의 속성이다. `shed_discarded` 와 무관한 실패 양식에 대해 이 카드는
   어떤 판정도 산출하지 않으므로, 그 실패를 다루는 card 를 금지할 근거도 산출하지 않는다.
   §D 의 원인 판정 규칙은 `share(C*, S1)` / `share(C*, S2)` / record 별 최다 class 로만 결론을 내는데,
   이 세 값은 전부 소멸 단위에서만 계산된다. 소멸 단위가 0인 실패 양식에 대해서는 이 규칙이 아무 값도 내지 않는다.
3. §E 의 one_change 원칙은 "`noop_actions`, BUY/HIRE/PLANT failure, `hands_length_mismatch` 를
   같은 card 에서 함께 고치지 않는다" 고 **명시적으로 분리**한다. 같은 카드가 그 분리된 항목을 다루는
   **별도 card 전체를 금지**한다고 읽으면 §E 와 모순된다.
4. §D 의 원인 판정표에서 `BLOCKED_AMBIGUOUS_ROOT_CAUSE` 는 "`share(C*, S1) >= 0.80` AND
   `share(C*, S2) >= 0.80` AND 14 record 이상 단독 최다" 라는 **shed 소멸 단위 조건**의 불충족을 뜻한다.
   즉 그 판정이 말하는 것은 "shed 원인 미확정" 뿐이고, 다른 실패 양식의 원인에 대해서는
   확정도 부정도 하지 않는다.

**외부 확인 (근거가 아니라 대조).** Coordinator 실행안 DECISION §3 도 "EXP-011 모호성을 HIRE 실패의
원인 규명으로 간주하지 않는다" 고 같은 판단을 적었다. 위 1~4 는 그 문서가 없어도 성립한다.

**한정되지 않는 것 — 확대 해석 금지.**

- HIRE 실패를 다루는 card(예: EXP-013)는 이 문장의 대상이 아니지만 **그것이 자동 승인은 아니다.**
  그런 card 는 자기 근거·자기 숫자 gate·자기 사람 승인을 따로 갖춰야 한다(EXP-013 §G).
  "EXP-011 의 금지 대상이 아니다" 는 **실행 허가가 아니라 금지 사유 하나가 없다는 뜻**일 뿐이다.
- §D 의 임계(`share >= 0.80`, 16 record 중 14개 이상), class 정의 8개, 세 축의 정의,
  층 고정(`S1` 14 record 64 단위 / `S2` 2 record 418 단위), seeds·좌석·상대, §E 의 acceptance 는
  **이 개정에서 1바이트도 바뀌지 않는다.** 이 절은 판정 **산출식**이 아니라 판정의 **적용 대상**만 다룬다.
  (카드 서두의 "커밋 후 seeds·좌석·상대·임계·class 정의 변경 금지" 를 위반하지 않는다.)
- EXP-011 자신의 실행 조건도 바뀌지 않는다. 이 카드는 여전히 **별도 사람 실행 지시**가 있어야 실행한다.
- `REPAIR_AUTHORIZED` 가 나와도 그것은 EXP-012 **설계 자격**일 뿐 즉시 실행 명령이 아니다(DECISION §3).

**발효 조건.** 이 한정안은 **사람이 이 범위 해석을 승인한 뒤에만** 발효한다.
승인 전에는 원문의 광의 금지가 그대로 유지되고, 그 상태에서 EXP-013 은 실행 불가다.
Coordinator 는 이 한정을 묵시적으로 적용하지 않는다(DECISION §3).
승인되면 아래 표에 승인 시각·승인자를 적고 카드 SHA 를 재동결한다.

| 항목 | 값 |
|---|---|
| 한정안 발효 | **미승인 (2026-09-17 기준)** |
| 승인 시각 / 승인자 | (미기록) |
| 승인 전 유효 문구 | 원문 — `REPAIR_AUTHORIZED` 가 아니면 어떤 구현 card 도 승인하지 않는다 |

## §E EXP-012 acceptance — 지금 고정한다 (결과를 본 뒤 변경 금지)

`REPAIR_AUTHORIZED` 일 때에만 사용한다. ID 는 `EXP-012` / `TEST-0012` / `HYP-0031`.
(`EXP-009`·`EXP-010`·`TEST-0009`·`TEST-0010` 은 `coordination/proposals/codex/20260914-community-trends-plan-update.md`
의 예약·BLOCKED 이름이므로 재사용하지 않는다.)

**one_change 원칙 (하나만 고친다)**
- §D 가 채택한 **단일 원인 하나**만 고친다.
- `noop_actions`, BUY/HIRE/PLANT failure, `hands_length_mismatch` 를 같은 card 에서 함께 고치지 않는다.
- **"모든 action 을 PASS 로 바꾸는 safety filter" 같은 광범위 guard 는 금지**한다.
- 새 guard 를 넣으면 **전용 activation counter 와 reason counter 를 함께** 정의한다:
  `shed_guard_activations` (record 당 정수)와 `shed_guard_reasons` (`{reason_code: count}`).
  reason_code 목록은 구현 전에 카드에 열거하며, 모든 record 에서
  `sum(shed_guard_reasons.values()) == shed_guard_activations` 여야 한다.
- parent·SHA 는 `coordination/proposals/claude/exp006/submission.tar.gz`
  sha256 `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` 로 고정한다.
- seeds·좌석·상대는 P1b manifest 의 **동일 13경기 그대로**. 결과를 본 뒤 seed·경기·threshold 변경 금지.

**최소 success 조건 (9개 전부 충족해야 SUCCESS)**
1. 승인된 동일 13경기가 13/13 완료
2. gated parent record 16개 **전부** `shed_discarded == 0`
3. 새 guard counter 가 cell 별·reason 별로 기록됨 (`sum(reasons) == activations`, 누락 record 0)
4. 16 record 전부 `shed_unsold == 0`
5. 16 record 전부 `orders_truncated == 0`
6. 16 record 전부 `exceptions == 0`
7. runtime: record 별 `total_s <= 623`, episode `wall_seconds <= 960`, hard ceiling `< 1200`
8. parent 에서 이미 0 이던 counter 의 candidate regression 0건
   (record 별로 `shed_unsold`, `orders_truncated`, `exceptions` 는 0 유지, 그리고
   `noop_actions`, `buy_failed`, `hire_failed`, `seed_blocked_plant`, `hands_length_mismatch_count` 는
   같은 record 에서 `candidate <= parent`)
9. 변경되지 않은 정상 action 의 parent/candidate parity:
   16 record 각각에서 `farmer`/`hands` action 차이 스텝 수 == 0,
   `market` 차이는 §D 가 채택한 원인 경로가 실제로 발동한 스텝에만 존재

**failure 조건 (하나라도 성립하면 FAILURE)**
- parent record 중 하나라도 `shed_discarded > 0`
- artifact / runner / opponent / engine SHA 불일치
- 필수 metric 누락
- 720-step 미완료 또는 `DONE/DONE` 아님
- 새 guard 가 손실을 단순 PASS 치환으로 숨기는데 별도 counter 가 없음
- 사전등록 범위 밖 코드 변경

## §F 판정 경계 — 성공해도 이것들은 참이다

- 이 카드나 EXP-012 가 성공해도 **즉시 제출 가능하다는 뜻이 아니다.**
- 다른 zero-gate failure (`noop_actions` 3,488 / `buy_failed` 74 / `hire_failed` 18 /
  `seed_blocked_plant` 56 / `hands_length_mismatch` 92) 가 남으면 **다음 correctness card 가 필요하다.**
- local correctness 는 hosted superiority 를 증명하지 않는다. hosted 주장은 `N/A`.
- 현재 active `EXP-006` / `EXP-007` 과 제출 tar 는 수정하지 않는다.
- zero gate 를 낮추지 않고 `shed_discarded` 를 diagnostic 으로 강등하지 않는다.
- `sell_unfilled` 는 diagnostic 이며 failure 기준이 아니다(이 카드에서도 동일).

## 결과

**실행 완료 2026-09-18 (Codex, 사람 승인 `coordination/reports/codex/20260918-EXP011-AUTHORIZATION.md`
sha256 `2c1820d204ffe94bc49e51aa9e77570ff14d7c93fed5f16784ba3c99b0ab5f18`).**
카드 판정 **PASS**, 원인 판정 **`REPAIR_AUTHORIZED`**, release zero gate **FAIL 유지**, hosted **N/A**.

| gate | 결과 |
|---|---|
| D1-a identity | mismatch 0 |
| D1-b 13경기 720 steps / DONE·DONE | 위반 0 |
| D1-c rewards + 9 counter exact | mismatch 0 (16/16 gated record) |
| D2-a/b/c | record 합 일치, 총합 **482**, 보존식 위반 0 |
| D3 필드 완전성 | null 0, day coverage 0~28 |
| D4 class 배타성 | unclassified 0, multi_class 0 |
| R-1/R-2/R-3 | agent total 0.045884~0.122455s <= 623 · episode wall 1.669~2.796s <= 960 · < 1200, 위반 0 |
| 전체 | **1,603 checks PASS** |
| `shed_discarded_inday_drop` / `_inday_place` (관측 전용, gate 밖) | 0 / 0 |

| class | S1 (14 record) | S2 (2 record) |
|---|---:|---:|
| `ROOM_PARTIAL\|REMOTE\|NO_DEPOSIT_ATTEMPT` | 64 | 416 |
| `ROOM_PARTIAL\|ADJACENT\|NO_DEPOSIT_ATTEMPT` | 0 | 2 |
| 나머지 6개 | 0 | 0 |

지배 class `C* = ROOM_PARTIAL|REMOTE|NO_DEPOSIT_ATTEMPT`. `share(C*, S1) = 64/64 = 1.0`,
`share(C*, S2) = 416/418 = 0.9952`, record 별 단독 최다 **16/16**. 사전등록 임계 0.80 / 0.80 / 14 를
모두 넘으므로 §D 판정표에 따라 **`REPAIR_AUTHORIZED`**. 임계·표본·class 정의는 실행 후 변경하지 않았다.

산출물: `experiments/results/p1_shed_attribution/` — `aggregate.json`
sha256 `22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba`,
`allocation_audit.json` sha256 `66ed824393d41aaae507866f327f5f9ae8f8bfa7c46d7993b10e197e43011fa8`,
freeze commit `0a4b10f`, runner `tools/instrument.py`
sha256 `ca64256f941f2098cafc531fc422363c5757995f721b449369ce72877a33fe28`.
재현: `python3 experiments/results/p1_shed_attribution/run.py --verify-only` — **2026-09-18 커밋 `35e9f45` 이후 read-only 다.**
~~⚠️ live checkout 에서 실행하지 말 것 — `verify()` 가 `aggregate.json` 을 덮어써 측정 산출물이 파괴된다~~
**[2026-09-18 정정 — §G C-7]** 이 위험 경고는 `35e9f45` **이전** runner(sha256 `20547a4a…`)에 대해 참이었다.
현재 runner(sha256 `883c4792…`)는 `verify(*, persist=False)` 이고 `--verify-only` 분기는 기본값을 쓰므로
**파일을 쓰지 않는다**. 다만 live 실행 결과는 exit 1 / `INVALID` 인데, 이는 `freeze.json['inputs']` 가
이 카드를 **측정 당시 r2 SHA** 로 고정한 상태에서 §G 정정 이력이 붙어 카드 SHA 가 바뀌었기 때문인
**provenance drift** 이며(불일치 input 은 카드와 runner **2개뿐**, 엔진·`instrument.py`·tape·P1b cells 등 측정 입력은 전부 일치),
**보존된 역사적 결과의 무효화가 아니다** — `aggregate.json` `22ebb927…` 와 판정 `PASS`/`REPAIR_AUTHORIZED` 는 그대로다.
SHA 일치까지 포함한 완전 재현은 freeze commit `0a4b10f` 를 복원한 별도 checkout/사본에서 한다.
`freeze.json` 을 새 카드/러너 SHA 로 덮어쓰지 않는다. 상세 `evidence/FACTS.md` F-T20 (1)(2)(3).
⚠️ `experiments/results/p1_shed_attribution/check_allocation.py` 는 **아직 무조건 `allocation_audit.json` 을 다시 쓴다** — live 실행 금지.
카드 SHA 와 무관한 대체 재현(새 경기 생성 없음, 파일 쓰기 없음):
`python3 scratch/claude_exp011_owner_20260918/verify_d1c_vs_p1b.py` ·
`python3 scratch/claude_exp011_owner_20260918/verify_order_invariance.py`.
guard 제안 `coordination/proposals/claude/20260918-EXP011-verify-only-guard.md` → Codex 적용 보고
`coordination/reports/codex/20260918-P1C-AUDIT-VERIFY-GUARD.md` (`run.py` 는 Codex 소유).

실행 보고 `coordination/reports/codex/20260918-EXP011-RESULT.md`
sha256 `10f885923175559a535bc93f2300979e8d6188d32a85c45ba78c8d7d3d18f919`.

**독립 검토 완료 2026-09-18 (Antigravity)** — `coordination/reports/antigravity/20260918-EXP011-REVIEW.md`
sha256 `cb4f4c9e4b1171a0424b678eaef4d72d0d0993853d43d192c7ce0655ed689e1d`.
verdict: 측정 PASS / causal 서술 FAIL. owner 판정은
`coordination/reports/claude/20260918-EXP011-REVIEW-ADJUDICATION.md`
sha256 `ffe16ae31144574eec0797b3cf8c4d7310709eb6ebc2607c18acbb4f88e0539c (1차, 2026-09-18 정정 고지 포함)`.

---

## §G 정정 이력 — r3 2026-09-18, r4 2026-09-18 C-7 추가 (Claude, owner)

**이 절은 측정 이후에 붙는다. 위의 판정·숫자·임계·class 정의·층·seeds·좌석·상대·§E acceptance 를
1바이트도 바꾸지 않는다.** 측정 당시 card 는 r2 sha256
`8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e` 이며 결과·registry·원장이 인용하는
card SHA 는 **그 값 그대로 유지**한다. 이 r3 의 새 SHA 가 결과의 과거 card SHA 를 대체하지 않는다.

정정 근거: 실행 보고(위) §"사후 검산과 해석 한계", 독립 검토 §3.3,
Codex 정정 제안 `coordination/proposals/codex/20260918-EXP011-OWNER-CORRECTIONS.md`
sha256 `bb86221cc7dfb5f5f251876a1f27cc1e6e8d9c11f1d68921c7f2a6612737148a`,
그리고 owner 의 독립 재검산 `scratch/claude_exp011_owner_20260918/` (read-only, 새 경기 생성 없음).

### C-1 §A 의 PLACE 서술은 틀렸다 `[ENGINE]`

§A 는 "같은 소멸이 in-day 경로에도 있다: `:344-355 DROP`, `:393-411 PLACE`" 라고 적었다.
**PLACE 는 소멸 경로가 아니다.**

- `:344-355 DROP` — `take = min(n, room)` 뒤 **`del inv[item]`**. 초과분 소멸. (서술 유지)
- `:393-411 PLACE` — `n = min(n, room)` 뒤 **`inv[item] -= n`**. 수용 가능한 만큼만 차감하고
  **초과분은 unit inventory 에 보존**된다. 소멸 없음.
- fixture: `tests/test_instrument_exp011.py::test_drop_discards_but_place_retains_overflow_and_animal_is_not_loss`
  (shed 98/100, inv 5 → DROP loss 3·left 0 / PLACE loss 0·left 3).
- 실측: `shed_discarded_inday_place` 는 26/26 player-record 에서 **0**. `shed_discarded_inday_drop` 도 0.
- §B-4 가 신설한 두 counter 는 **그대로 둔다.** `shed_discarded_inday_place` 는 이제 "정의상 항상 0 이어야 하는
  invariant 감시 counter" 로 읽는다. 값이 0 이 아니면 엔진 가정이 깨진 것이다.

### C-2 §D `ROOM_PARTIAL` 의 **설명문**을 정정한다 (class 정의·임계·판정은 불변) `[ENGINE]` `[LOCAL]`

§D 후속 경로 표의 `ROOM_PARTIAL | * | *` 행에 붙은 설명 **"여유 용량이 있는데도 이월에 실패했다"** 는
사실과 다르다. 다음으로 읽는다:

> `ROOM_PARTIAL` 은 **event 시작 시점의 전체 shed 점유가 capacity 미만**이었다는 뜻일 뿐이며,
> 그 unit 이 들고 온 물건을 **전부 담을 공간이 있었다는 뜻이 아니다.**

- 44개 loss event **전부**에서 `carried_total > room`(= `capacity − shed_total_before`) 이었다.
  `carried_total <= room` 인 loss event 는 **0건**이다.
- 모든 event 에서 `discarded_total == max(0, carried_total − room)` 이 **정확히** 성립한다(위반 0).
- 예: target seat0 day15 step383 — shed 55, room 45, carried 51, loss 6.
- 축 A 의 산식(`ROOM_ZERO` / `ROOM_PARTIAL` 의 정의), 8개 class, 세 축, 층 고정, 임계는 **변경하지 않는다.**
  바뀐 것은 라벨에 붙은 자연어 해석뿐이고, 산출된 판정 `REPAIR_AUTHORIZED` 도 **그대로 보존**한다.

### C-3 `REPAIR_AUTHORIZED` 는 성립하지만 §D 가 허용한 repair 로는 손실을 줄일 수 없다 `[ENGINE]` `[LOCAL]`

§D 는 이 class 에 대해 EXP-012 의 `one_change` 를 **"이월 순서/클램프 단일 지점"** 으로 제한했다.
그 범위 안에서는 총 소멸량이 **정확히 0 만큼** 줄어든다.

- 엔진 `_drop_inventories_to_shed` 는 `room` 이 소진될 때까지 탐욕적으로 채우므로
  **총 예치량 = `min(carried_total, room)`** 이고, 이 값은 unit 순서·item 순서와 **무관**하다.
- 기계적 확인: 저장된 각 loss event 에 대해 unit 순열 × item 순열을 무작위로 200회 적용해 엔진과 동일한
  배분을 재현했다. **총 소멸량이 달라진 event 0건.** 순서는 *어느 물건이* 버려지는지만 바꾼다.
- 따라서 §E 최소 success 조건 2("gated 16 record 전부 `shed_discarded == 0`")는 허용된 변경 범위만으로는
  **구조적으로 달성 불가능**하다.
- **판정: EXP-012 를 사전등록하지 않는다.** 카드상 `REPAIR_AUTHORIZED` 는 설계 **자격**이며 설계 **가능성**이
  아니다. 이 둘을 분리해 기록한다. 억지 후보를 만들지 않는다.
- **이 repair 경로의 한계(명시):** `_drop_inventories_to_shed` 는 agent 가 호출하거나 인자를 바꿀 수 없는
  엔진 내부 함수다. 하루 마지막 턴에 agent 가 쓸 수 있는 것은 자기 unit action 과 market order 뿐인데,
  DROP·PLACE 로 미리 넣어도 `shed 점유 + carried` 총량은 보존되므로 EOD 손실
  `max(0, 총량 − shedCapacity)` 는 변하지 않는다. 총량 자체를 줄이는 개입만이 손실을 줄이며,
  그것(매도 증량·생산 조절·사전 매도)은 이 카드가 **측정하지 않았고 §D 가 허용하지도 않은** 다른 intervention 이다.
  결과를 본 뒤 §E acceptance 를 그 방향으로 고쳐 쓰지 않는다 — 필요하면 **자기 근거·자기 gate·사람 승인을 갖춘
  새 ID 의 카드**를 따로 세운다.

### C-4 미확정으로 남기는 것 (증명되지 않았다)

- **회수 가능성**: 44/44 loss event 에서 EOD 직전 shed 재고가 100% 판매 가능 `PRODUCTS` 였고 그 양(9~82)이
  손실(1~28)을 매번 초과했다. 엔진 스텝 순서(`unit actions → _process_market → … → _end_of_day`)와
  `_commit_unit` SELL 이 shed 에서만 차감하는 점을 합치면 **마지막 턴 매도 1 unit 당 손실 1 unit 감소**가
  산술적으로 성립한다(상한 482/482). **그러나 이것은 상한일 뿐이다** — 매도 증량은 `market_price` 를 눌러
  이후 매도까지 손해를 주고, 현금 변화가 BUY/HIRE/PLANT 연쇄와 action parity 를 바꾼다. 전부 미측정이다.
- **회수의 가치 — `[2026-09-18 정정: '최대'는 근거 없는 표현이었다]`**: coin 환산에는 두 **추정** 방식이 있고
  **어느 쪽도 상한이 아니다.** 방식 A(그 경기 전체 실현 매도 평균 단가 × 소멸 개수) = target 209 units ≈ **19,231**,
  gated 16 record 합 ≈ **43,977**. 방식 B(같은 경기의 item 별 실현 단가를 그 item 의 소멸 수량에 적용) =
  target ≈ **13,938**, gated 합 ≈ **30,886**. **A 는 B 대비 29.8% 과대추정**이며, 소멸 item 구성이
  WHEAT(base 25) gated 61.4% / target 70.8% 로 싼 품목에 치우쳐 있기 때문이다.
  B 도 상한이 아니다 — `market_price` 는 재고의 감소함수라 추가 매도가 단가를 낮추고, drop 시점의
  market inventory·price 는 이 artifact 에 **기록돼 있지 않다** → **엄밀한 상한 `N/A`**.
  마진 대비: target 패배 마진 109,295 의 A 17.6% / B 12.8%. baseline 은 방식 B ≈294~308 coin.
  F-T17 의 "50판 중 1판" 은 **정적 환산 가정 하의 산술 시나리오**이며 경기별 회수 counterfactual 이 아니다.
  → **"전량 회수해도 뒤집지 못한다"·"shed 는 가치가 작다" 를 확정 결론으로 쓰지 않는다.** 최신 window 는 `N/A`.
  재현 `python3 scratch/claude_exp011_owner_20260918/discard_value_estimates.py`.
- **in-day DROP**: gated 16 record 에서 0 이지만 이 13경기·이 tape 한정 관측이다.

### C-6 확정 결론의 **범위** — 이것만 확정이고 나머지는 기각되지 않았다 `[2026-09-18 추가]`

Coordinator 검토서 `coordination/proposals/codex/20260918-EXP011-CLOSURE-PRIORITY.md`
sha256 `b1ed06b777abc4841747a60b4328ad670638878f5bf87fc51e3f0649ca15d137` 의 지적을 반영한다.
owner 판정은 `coordination/reports/claude/20260918-EXP011-CLOSURE-PRIORITY-ADJUDICATION.md`
sha256 `3909891dcc4412c63b8802c5c9017545d5d8a35e2b695f4a7b09194b193d251c` (지적 6건 전부 수용).

**확정된 것은 이 한 문장뿐이다:**

> §D 가 `ROOM_PARTIAL` class 에 허용한 `one_change` — **고정된 최종 이월(EOD `_drop_inventories_to_shed`)의
> 순서/클램프 변경** — 만으로는 gated 16 record 전부 `shed_discarded == 0` (§E 성공조건 2)을 달성할 수 없다.
> 그러므로 **EXP-012 는 사전등록 불가**다.

**이것이 기각하지 않는 것 — 확대 해석 금지:**

- **shed 관련 다른 전략 전체를 기각하지 않는다.** 마지막 턴 매도 증량, 사전 예치·매도 스케줄 변경,
  생산·수확 조절, 품목 우선순위 변경은 이 카드가 **측정하지 않았고 판정 대상도 아니다.**
- `shed_discarded` 의 전략적 가치가 작다고 확정하지 않는다(C-4 정정).
- 회수가 순위에 미치는 영향을 확정하지 않는다. 최신 window 표본은 `N/A` 다.
- EXP-013 을 지지하지도 기각하지도 않는다(C-5).
- `noop_actions` 와의 수량 비교로 후속 작업 우선순위를 정하지 않는다 — 3,488 은 **action 횟수**,
  482 는 **item 개수**로 단위가 다르고, `noop_actions` 자체가 PASS 치환 횟수가 아니다(`evidence/FACTS.md` F-T22).

### C-5 §F 판정 경계는 그대로 유지된다

- EXP-011 의 PASS 는 제출 가능을 뜻하지 않는다. release zero gate 는 **FAIL 유지**이며 낮추지 않는다.
- `shed_discarded` 를 diagnostic 으로 강등하지 않는다.
- **EXP-011 결과를 EXP-013(HYP-0032)의 효과 증거나 실행 승인으로 쓰지 않는다.** §D-1 근거 2 대로
  이 카드의 산출값은 전부 shed 소멸 단위의 속성에서만 계산되며, 소멸 단위가 0 인 실패 양식에 대해서는
  아무 값도 내지 않는다. EXP-013 은 자기 근거·자기 gate·사람의 별도 승인을 갖춰야 한다(EXP-013 §G, BOARD C1).
- §D-1 한정안 발효 표는 이 개정에서 변경하지 않는다.

### C-7 `--verify-only` 재현 경고를 **수정 전 위험 / 수정 후 동작**으로 분리한다 `[LOCAL]` `[2026-09-18 r4 추가]`

r3 의 §결과 재현 항목과 `evidence/FACTS.md` F-T20 은 "`--verify-only` 를 live 에서 돌리면 `aggregate.json` 이
덮어써져 측정 산출물이 파괴된다"고 적었다. **그 경고는 당시 runner 에 대해 옳았고, 지금은 옳지 않다.**
원문을 조용히 지우지 않고 아래와 같이 구분해 남긴다.

| | runner sha256 | `--verify-only` 동작 |
|---|---|---|
| 수정 전 (`35e9f45` 이전, freeze 가 고정한 값) | `20547a4ac8a47045b254bbe6534c2c543f052d2cf6c1f07ba1c21bf0066eefb8` | `verify()` 끝에서 무조건 `aggregate.json` 쓰기 → identity 실패 시 `INVALID` 로 **덮어씀** |
| 수정 후 (현재) | `883c4792d855dbed2fccfc0e16a83f608d820fc9a1d82c0489168d0df3d9de37` | `verify(*, persist=False)` — **쓰기 없음**, 판정만 stdout. 쓰기는 batch 완료 경로 `verify(persist=True)` 에만 |

- owner 독립 재현(2026-09-18, 새 경기 생성 없음): `pytest tests/test_exp011_verify_readonly.py tests/test_audit_p1c_replays.py -q` → **3 passed**.
  live `--verify-only` 직접 실행 → exit **1**, `INVALID INVALID checks 1603 …`,
  `aggregate/freeze/commands/allocation_audit` **4개 SHA 전후 동일**.
- **live `INVALID` 의 의미**: freeze 30개 input 중 불일치는 **이 카드**(r2 `8736d403…` → 정정 이력 부착본)와
  **`run.py`**(guard 적용) **2개뿐**이다. 엔진·`tools/instrument.py`·tape·P1b parent/cells 등 측정 입력은 전부 일치한다.
  D1-a identity gate 하나만 깨진 것이고 나머지 1602 check 는 통과한다.
- **불변**: 측정 당시 card SHA(r2), `freeze.json`, `aggregate.json` `22ebb927…`, `allocation_audit.json` `66ed8243…`,
  사전등록 임계(0.80/0.80/14), class 정의, 판정 `PASS` / `REPAIR_AUTHORIZED` 는 이 개정에서 **1바이트도 바뀌지 않는다**.
  이 r4 의 새 카드 SHA 가 결과·registry·원장이 인용하는 r2 SHA 를 대체하지 않는다.
- **잔여 갭(미해결, Codex 소유)**: (a) `check_allocation.py` 는 여전히 무조건 `allocation_audit.json` 을 다시 쓴다.
  (b) regression test 는 `verify()` 기본값만 검증하며 `main()` 의 `--verify-only` 분기가 `persist=True` 로 바뀌는 회귀는 잡지 못한다.
  인수 보고 `coordination/reports/claude/20260918-EXP011-VERIFY-GUARD-ACCEPTANCE.md`.
