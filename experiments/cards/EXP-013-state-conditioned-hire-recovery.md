# EXP-013 — opening HIRE 부분 체결의 state-conditioned recovery (한 요인, 실행 BLOCKED)

hypothesis_id: HYP-0032
test_id: TEST-0013

사전등록 2026-09-17 08:35 UTC / 17:35 KST (Claude, opus-5). **실행 전 커밋.**
개정 r2 2026-09-17 (Claude, opus-5) — codex 계약 검토
`coordination/proposals/codex/20260917-EXP013-CONTRACT-REVIEW.md` sha256 `54dcaf42541a3afbbb573e2c69dc3cb3d5c0ff7c0b47e77a0cedce742f63a2ef`
(검토 대상이던 r1 카드 sha256 `96f0278293d56fe50e639f273abe6eaf5f5987c334d9d037cde63c3874354fd6`)
의 6개 항목을 parent 코드·엔진으로 확인해 §C-A/§C-0~§C-5, §D-1~§D-3, §E G1~G3 을 고쳤다. 대응 내역은 §J.
**실행 전 문서 개정이며 실행 결과는 아직 없다.** window·target source·자금 규칙·slot 규칙·seed·좌석·상대·임계는 바뀌지 않았다.
개정 r3 2026-09-17 (Claude, opus-5) — Coordinator 실행안
`coordination/proposals/codex/20260917-correctness-path/DECISION.md` sha256 `286c492fd46a731626d08131934f5ba7965fb5c90cb9c333182b37102858a95d`
에 맞춰 **§G 의 적용 범위만** 고쳤다: 이 카드는 P2 가 아니라 C1 경로이고, **BOARD P2 의 "실제 parent P1b PASS"
선행 조건은 유지**되며 이 카드는 그 조건의 대체를 요구하지 않는다(r2 §G-2 의 요구 철회).
§C·§D·§E 의 계약과 숫자 gate 는 1바이트도 바뀌지 않았다. 실행 승인도 아니다.
커밋 후 window·target source·자금 규칙·slot 규칙·seed·좌석·상대·임계 변경 금지. 결과를 본 뒤 임계를 고치지 않는다.
**이 카드는 지금 실행 승인이 아니다.** §G-1 의 네 선행 조건이 모두 기록되기 전에는 parent baseline 기록도 시작하지 않는다.

출처 제안: `coordination/proposals/codex/20260917-STATE-CONDITIONED-RECOVERY.md` (VERDICT: BLOCKED_DRAFT).
이 카드는 그 제안의 미확정 3항목과 계측 정의를 확정한 소유 경로 정본이다.

선행 근거
- postmortem `coordination/reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md` sha256 `c77010549217d4f344c93336f890dd79bd1d91141f577192b279220c12d95613`
- P1b 결과 정본 `experiments/results/p1_release_preflight/report.md` sha256 `3b915c2b7adb541caa7c41c86062f57c628e44b0d067aeb5dc46fed78ee9b6b6`
- P1b manifest `experiments/results/p1_release_preflight/manifest.json` sha256 `46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c`
- 독립 검증 `coordination/reports/antigravity/20260916-1933-P1B-RESULT-INDEPENDENT-VERIFICATION.md` sha256 `fc02423f9a4fbf66f23be56c3f454d051fa0c1e927100542be40c5ff8cb47ad5` — verdict `VERIFIED_LOCAL_FAILURE`
- 엔진 `.venv/.../kaggriculture/kaggriculture.py` sha256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

**증거 경계 선언.** donor(Majkel 등) 관측은 이 카드의 근거가 아니다.
`coordination/reports/codex/20260917-1640-DONOR-ROUTES.md`의 index25 cash 7/7/6, post hands 4/4/3, index27 3→4는
동일 submission 3경기의 **descriptive** 관측이며 treatment effect가 아니다.
이 카드의 §A~§C 어디에서도 donor 수치를 인용하지 않는다. 동기는 우리 episode 108076177의 `[HOSTED]` 실패와 `[ENGINE]` 규칙뿐이다.

**EXP-008 금지 재확인.** step 1 opening market schedule(A→B)은 `LOCAL_FAILED`로 폐기됐다.
이 카드는 opening market schedule의 순서·수량을 **1바이트도 바꾸지 않는다**. tape의 기존 주문은 추가·삭제·재배치되지 않는다(§C-3).

---

```yaml
id:            EXP-013
parent:        coordination/proposals/claude/exp006/submission.tar.gz
               # sha256 1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721
               # member: main.py bba042e04cff32ab53be2c59c2f5cd9053c8de2bf31632e396ca8faa502896b2
               #         yh_base.py d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b
               #         actions.json 17d503f2fd20d59f9c0f14024d1e74a8add8bb9b5561d4d908b45deecb5495ef
               #         LICENSE.txt cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30
               # 실행 시점에 이 SHA가 아니면 IDENTITY_MISMATCH. P1b correctness 경로가 tar를 바꾸면
               # 이 카드는 새 SHA로 재동결하고 parent baseline을 처음부터 다시 기록한다.
candidate:     experiments/candidates/exp013_hire_recovery/main.py  (Codex 구현, 실행 전 SHA freeze)
               main.py 외 member는 parent tar에서 byte-identical 복사한다.
one_change:    main.py 의 parent 최종 action 뒤에 "state-conditioned hire recovery mode" 한 겹을 덧붙인다.
               parent 의 base agent 호출·_layer·두 fallback 은 1바이트도 바꾸지 않고, 그 결과(PA) 를 입력으로 받는다(§C-A).
               A = frozen parent: tape 의 hands 배열과 market 주문을 그대로 낸다.
               B = §C 의 recovery mode. day 의 first-wave 목표 인원 대비 실제 len(hands) 가
                   부족한 날에만 켜지고, 부족한 인원만 요청하며, 존재하는 hand 에만 작업을 배정한다.
               이 mode 는 6개 하위 규칙(C-A 적용 지점 / C-0 목표 인원 source·판정 시점 / C-1 trim /
               C-2 trigger / C-3 HIRE 배치·자금 / C-4 late-hand route)이 서로를 전제하는
               **indivisible factor** 다. 하위 규칙을 따로 켜면 다른 candidate 다(§F-2, §F-6b).
fixed:         [parent tar 4 member 와 actions.json tape 전체, SHOP_PLANS,
                clone-preempt logic 과 threshold (PREMIUM / MAX_CLONE_DIST=6 / FRACTION=2.0 /
                MAX_BATCH=30 / MIN_FUTURE_QTY=4 / START=120 / STOP=680),
                yh_base 의 repair_weeds / subtract_advanced_sales / advance_sales / liquidate,
                opening market schedule (EXP-008 B 부활 금지), 작물·동물 선택, shop routing, 판매 전략,
                tape 가 이미 낸 market 주문의 내용·수량·순서, MAX_ORDERS=10,
                second-wave(hour 2/4/5) 고용의 목표 인원 — 추가 HIRE 트리거 대상 아님(§C-0),
                GOOSE · 4번째 토지 · donor tape 복사 — 추가하지 않음(K3 재검토 아님),
                engine kaggle-environments 1.32.7 (py bc8a5487…653e / json a82c89c1…4867),
                configuration 기본값 boardSize=10 / turnsPerDay=24 / shedCapacity=100 /
                maxMarketOrdersPerTurn=10 / episodeSteps=720,
                P1b manifest 의 13경기 seed·좌석·상대 전부, metric schema 3,
                승인된 runtime 기준 623 / 960 / 1200]
hypothesis:    postmortem 인용 — coordination/reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md:
               hosted episode 108076177 (Remielle 167,541 vs Sian 58,246, margin −109,295) 에서
               "day0 종료 cash 0 → day1 HIRE 3건(비용 4) 조용한 실패 → 존재하지 않는 hands 에 의존하는
               tape 가 계속 나옴" 이 최초 구조적 분기였다.
               본 카드는 그 분기가 **부분 체결 시점에 실제 len(hands) 를 읽어 부족분만 고용하고
               존재하는 hand 에만 작업을 배정하면** target cell 에서 (i) 미충원 인원이 0 이 되고
               (ii) 존재하지 않는 hand 에 배정된 action 이 0 이 되며 (iii) 그 결과 final bank 가
               parent 보다 크다는 것만 주장한다. hosted 우위·pool 우위는 주장하지 않는다.
opponents:     P1b manifest 와 동일, 추가·삭제 없음 (sha256 46fd9e5e…801c)
               self_parent_A                   = cleanroom/parent/main.py sha256 bba042e04cff32ab53be2c59c2f5cd9053c8de2bf31632e396ca8faa502896b2
               builtin_starter_1_32_7          = kaggle_environments.envs.kaggriculture.kaggriculture:starter_agent (bc8a5487…653e)
               stress_Remielle_108076177       = private_artifacts/tapes/Remielle_episode-108076177-actions.json sha256 75ea188ed138167b274ce34d20ce3476adfcfe25ee75d6feb7ed4e8de7caa5c4
               exp008_control_today_108079022  = private_artifacts/tapes/today_episode-108079022-actions.json  sha256 b1bd786abd851ac053f617eeebd3e36c91d74af63dde947ecb3f575e52faa637
seeds:         self_play            [7, 1000, 1001]                    (3경기. parent_A vs candidate 대결이 아니라 parent run 과 candidate run 이 각각 self_parent_A 를 상대한다 — §E G2 의 parity cell)
               builtin_smoke        [7, 1000, 1001] x seats [0,1]      (6경기)
               hosted_loss_stress   [1125321547]    x seats [0,1]      (2경기)  ← target
               exp008_control       [1989066512]    x seats [0,1]      (2경기)  ← control
               총 13경기 / gated record 16개. parent 16 + candidate 16 = 32 record. 실행 후 추가·교체 금지.
seats:         both
metric:        G0 identity·재현 / G1 safety / G2 parity(무트리거 14 record) /
               G3 mechanism(target 2 record) / G4 outcome(target, n=1 seed) /
               G5 control outcome / G6 runtime
success:       G0·G1·G2·G3·G5·G6 전부 PASS AND G4 = TARGET_IMPROVED
failure:       G0·G1·G2·G3·G5·G6 중 하나라도 FAIL, 또는 G4 = FAILURE
inconclusive:  hard gate 전부 PASS 이고 G4 = INCONCLUSIVE (target 양 좌석 bank 가 parent 와 동일)
next_if_success: 승격 아님. pool/public 확장 카드(EXP-014)를 **별도로** 사전등록한다.
                 그 카드에서 상대 SHA·seed·좌석·숫자 gate 를 새로 동결한다. 제출 근거로 쓰지 않는다.
next_if_failure: recovery mode 폐기. window·자금 규칙·slot 규칙을 결과를 보고 재조정하지 않는다.
                 seed 추가·factor 쪼개기·hour 경계 재탐색 금지. 새 postmortem 근거가 있어야 새 HYP-ID 로 재시작.
artifact:      결과 JSON experiments/results/exp013_hire_recovery/ (Codex 소유, 신규 경로)
               P1b 산출물은 읽기 전용이며 덮어쓰지 않는다.
계측:          tools/instrument.py — §D 의 확장 필요. 확장 후 새 sha256 을 실행 전에 동결한다.
               확장 전 sha256 284dee4cdacfc56aab2125f8a92b41df53e14744cca7a8cafa10b853fb6d0629
               tools/gate_contract.py sha256 3a3e423b3e0afadca8860b7bd2ed2d39ba326a824c8c6a23c4491fde6171353c (불변)
```

---

## §A 엔진 사실 — 무엇이 실제로 일어나는가 `[ENGINE]`

`kaggle-environments==1.32.7`, `kaggriculture.py` sha256 `bc8a5487…653e`. 아래는 전부 소스에서 직접 확인했다.

- `:698-711 _hire_cost / _do_hire` — n번째 고용 비용은 `farmHandCostMult * fib(farm["hires_today"])`,
  `fib(0)=1, fib(1)=1, fib(2)=2, fib(3)=3, fib(4)=5, …`. 기본 mult 는 `:101 FARM_HAND_COST_MULT = 1`.
  **`farm["money"] < cost` 면 예외 없이 return** 한다. 실패해도 `hires_today` 는 증가하지 않는다.
- `:145-153 _new_farm` — `hires_today` 는 **public farm observation 필드**다. replay 확인:
  `steps[25].observation.farms[1] = {'farmer': [4,4], 'hands': [], 'hires_today': 0, 'money': 0.0, …}`.
  → 다음 고용 비용을 관측만으로 정확히 계산할 수 있다.
- `:533-541 _spawn_hand` — 새 hand 는 shed 인접 4칸 `[(4,4),(5,4),(4,5),(5,5)]`(boardSize 10, NWSE 순서) 중
  **점유 수가 가장 적은 칸**, 동점이면 그 리스트 순서. 점유는 `[farmer] + hands` 로 센다.
  한 턴에 여러 명을 고용하면 append 순서대로 순차 계산된다.
- `:702-711` — `_do_hire` 는 `farm["hands"].append(...)` 와 `private["inventories"].append({})` 를 함께 한다.
  → **늦게 고용된 hand 의 소지품은 항상 빈 dict 다.** parent 의 같은 slot hand 가 spawn 시점에 갖는 것과 동일하다.
- `:571-580 _process_market` — market 주문은 index 순서로 처리되고, 같은 index 에서 HIRE/BUY_LAND 가 먼저,
  그다음 SELL/BUY 의 per-unit lockstep 이 돈다. 따라서 **앞 index 의 SELL 수익은 뒤 index 의 HIRE 자금이 된다.**
- `:311-317 _apply_unit_action` — `idx-1 >= len(farm["hands"])` 이면 `pos is None` 이라 **즉시 return**.
  존재하지 않는 hand 의 action 은 예외도, 로그도, 카운터도 남기지 않는다.
- `:916-934 interpreter` — PLANT 의 atomic 검증은 `[farmer, *hands_actions]` **전체**로 수요를 센다.
  존재하지 않는 hand 의 PLANT 요청도 수요에 포함되어, 씨앗이 모자라면 **그 작물의 PLANT 전부**가 PASS 된다.
- `:866-884 _end_of_day` — 매일 종료 시 `hands = []`, `hires_today = 0`, `inventories = [{}]`,
  `farmer = _default_spawn = (4,4)`. **hand 는 하루를 넘기지 않는다.** 늦은 고용의 가치는 당일 안에만 있다.

## §B 관측 사실 — target episode 108076177 의 실패 구조 `[HOSTED]` `[LOCAL]`

replay `private_artifacts/replays/episode-108076177-replay.json`, seat 1 (Sian).
`steps[i][seat].action` 은 `steps[i-1]` 관측에서 낸 action 이다(action stream step = obs.step + 1, `tools/instrument.py:546`).
이 정렬로 세면 hands 불일치 턴은 **정확히 46턴**이고, P1b 의 `hands_length_mismatch_count = 46`(record 당)과 일치한다.

불일치는 두 날에만 있다.

| day | tape 가 낸 것 | 그때 money / hires_today | 실제 hands | 결과 |
|---|---|---|---|---|
| 1 (step 24, h0) | `HIRE ×3` (비용 1+1+2=4) | 0 / 0 | 0 | 3건 전부 조용히 실패. h1~h23 23턴 동안 phantom hand 3명 |
| 8 (step 192, h0) | `HIRE ×8` + `SELL FERTILIZER 1` | 3 / 0 | 2 | 앞 2건만 체결(1+1), 나머지 6건 실패. SELL 은 HIRE **뒤**라 87코인은 늦게 들어옴. h1~h23 23턴 동안 phantom hand 6명 |

- 존재하지 않는 hand 에 배정된 unit action = `3×23 + 6×23 = 207`건. 전부 조용한 no-op.
- hour 12 시점 미충원 인원 = day1 3명 + day8 6명 = **9**.
- day 8 은 **같은 턴에 HIRE 를 SELL 뒤로 옮기기만 해도** 전부 체결됐다(90 ≥ 1+1+2+3+5+8+13+21=54).
  day 1 은 그 턴에 팔 것이 없었고 money 가 0 에서 벗어나는 최초 시각은 **h9(100)** 이다.
  → **주문 재배치만으로는 day1 을 고칠 수 없고, 같은 날 안의 재시도만이 두 날을 모두 덮는다.**
- parent 의 손해는 그 두 날에 갇히지 않는다. replay 에서 tile-op 무변화 비율은 day2 11/45 에서 day15 78/144 로 계속 커진다.
  즉 이 실패는 **누적 cascade** 이고, 따라서 판정은 §E 의 outcome 으로만 한다. 특정 날의 no-op 감소를 효과로 쓰지 않는다.

P1b gated parent record (target, 각 좌석 동일):
`reward 58,246` · `noop_actions 1,149` · `shed_discarded 209` · `buy_failed 34` · `hire_failed 9` ·
`seed_blocked_plant 16` (STRAWBERRY 12 / WHEAT 4) · `hands_length_mismatch_count 46` · `exceptions 0` · `orders_truncated 0`.
control record (각 좌석 동일): `reward 115,745` · `noop_actions 44` · `shed_discarded 7` ·
`buy_failed 0` · `hire_failed 0` · `seed_blocked_plant 0` · `hands_length_mismatch_count 0`.
**16 record 중 hire_failed 가 0 이 아닌 것은 target 2개뿐이고, hands_length_mismatch 가 0 이 아닌 것도 그 2개뿐이다.**
나머지 14 record 는 그대로 무트리거 parity cell 이 된다(§E G2).

## §C 변경 B — recovery mode 의 exact 규칙

용어. `P = observation["player"]`, `F = observation["farms"][P]`, `s = observation["step"]`,
`day = s // 24`, `hour = s % 24`, `A = len(F["hands"])`.
`plan` = base agent 실행 **후** `yh._POLICY.players[P].plan` (EXP-006 layer 가 이미 쓰는 접근 경로).
`tape = yh._POLICY.tapes[plan]`, `T(s) = len(tape[s].get("hands") or [])`.
`mult = int(configuration.get("farmHandCostMult", 1))` — configuration 이 없으면 1.

`PA` (**parent action**) = parent tar `main.py` 의 `agent()` 가 그 턴에 **실제로 반환하는 action**.
`PA` 는 `yh.agent(...)` 의 결과가 **아니다**(§C-A). 이 카드에서 "parent 가 낼 action" 은 언제나 `PA` 를 가리킨다.

### C-A 적용 지점 — recovery 는 parent 최종 action 뒤에 붙는다 `[CODE]`

parent `main.py:126-137` 의 구조(직접 확인, member sha256 `bba042e0…96b2`):

```
def agent(observation, configuration=None):
    try:
        yh = _yh(); base_action = yh.agent(observation, configuration)
    except Exception:
        GUARD_COUNTS["base_raise"] += 1
        return {"farmer": ["PASS"], "hands": [], "market": []}      # (i) base fallback
    try:
        return _layer(yh, observation, copy.deepcopy(base_action))  # (ii) 정상 경로
    except Exception:
        GUARD_COUNTS["layer_raise"] += 1
        return base_action                                          # (iii) layer fallback
```

`PA` 는 (i)/(ii)/(iii) 중 그 턴에 실제로 반환된 값이다. 정상 턴에서 `PA` 는
`_layer` 의 clone-preempt(선행 매도 SELL 추가), due 정산, `market[:MAX_ORDERS]` 절단이
**이미 적용된** action 이다. candidate 는 이 세 갈래를 **그대로 두고** 뒤에 한 겹만 더 얹는다.

```
def agent(observation, configuration=None):
    try:
        yh = _yh(); base_action = yh.agent(observation, configuration)   # 호출은 이 한 번뿐
    except Exception:
        GUARD_COUNTS["base_raise"] += 1
        return {"farmer": ["PASS"], "hands": [], "market": []}
    try:
        PA = _layer(yh, observation, copy.deepcopy(base_action))
    except Exception:
        GUARD_COUNTS["layer_raise"] += 1
        PA = base_action
    try:
        return _recovery(yh, observation, configuration, PA)   # 새 dict 반환, PA 를 in-place 변형하지 않는다
    except Exception:
        RECOVERY_COUNTS["recovery_raise"] += 1
        return PA
```

(i) base fallback 경로에서도 `_recovery` 는 호출된다. 그 경로의 `PA["hands"]` 는 `[]` 이므로
§C-1 은 `A` 개의 `["PASS"]` 를 채우고, `PA["market"] == []` 이므로 §C-3 조건 3 은 만족된다.
`layer_raise` 와 `recovery_raise` 는 **서로 다른 counter** 다(이전 판은 둘을 `layer_raise` 하나로 묶어 두었다).

**금지 — `yh.agent(...)` 와 `_layer(...)` 를 한 턴에 두 번 호출하지 않는다.**
취향이 아니라 상태 파괴다(직접 확인):
- `yh_base.py:201-206` — `Policy.act` 는 `if state is None or step <= state.last_step:` 에서
  **DayState 를 새로 만든다.** 같은 step 으로 두 번째 호출하면 `state.plan` 이 0 으로 되돌아가고
  `queues / advanced_sales / sale_due_step` 가 전부 초기화된다. step 144(ROUTE_STEP) 이후에는
  **다른 tape 를 쓰게 되므로** 경기가 통째로 달라진다.
- `yh_base.py:84-100` — `repair_weeds` 는 `state.queues` 에서 popleft 한다. 두 번째 호출은 큐를 한 칸 더 소비한다.
- `main.py:76-89` — `_layer` 의 due 정산은 `st["due_step"] == step` 인 턴에 한 번만 유효하고 실행 후
  `st["due"]` 를 비운다. 두 번째 호출은 clone-preempt 의 되돌림을 잃는다.

**이 순서가 안전한 이유 (확인).** recovery 는 `PA["hands"]` 를 잘라내지만(§C-1),
`_layer` 와 `advance_sales` 가 쓰는 `yh_base.projected_shed(action, view)` 는
`for worker in range(min(len(workers), len(view.positions)))` 로만 순회한다(`yh_base.py:112-113`).
`view.positions` 는 **관측된** `[farmer, *hands]` 라 길이가 `A+1` 이고, trim 후 `workers` 길이도 `A+1`,
index `0..A` 의 원소는 trim 전과 동일하다. 따라서 **trim 은 parent 의 매도 판단에 영향을 줄 수 없다.**
순서를 뒤집어 먼저 trim 하고 `yh.agent` 를 부르면 recovery 통제 hand 의 치환된 행동이
`projected_shed` 에 들어가 clone-preempt 와 `advance_sales` 가 달라지고 무트리거 parity(§C-5)가 깨진다.

**되먹임 없음.** recovery 가 바꾼 hand action 은 `yh` 와 `_layer` 의 내부 상태에 반영되지 않는다.
parent 의 `state.queues` 는 계속 base action 기준으로 진행한다.
이것을 동기화하려 하지 않는다 — 동기화는 parent 코드를 바꾸는 것이고 한 요인이 아니다.

**마지막 턴 예외.** `s == yh.LAST_STEP == 718` 에서 `Policy.act` 는 `liquidate(view)` 를 돌려주며
그 action 의 `hands` 길이는 정의상 `len(view.positions) - 1 == A` 다(`yh_base.py:183-191`).
이 턴에는 recovery 를 **전혀 적용하지 않고** `PA` 를 그대로 반환한다(§C-1 trim 도 하지 않는다).
`s == 718` 은 hour 22 라 §C-2 window 밖이므로 §C-3 은 원래 발화하지 않지만,
§C-4 의 route 치환이 liquidate 의 DROP 을 덮는 것은 이 예외가 막는다.

### C-0 목표 인원 source 와 판정 시점 — first wave 하나만 쓴다

```
first_hire_step(day) = 1 if day == 0 else day*24
T_first(day)         = T(first_hire_step(day) + 1)
```

**이것이 유일한 목표 인원 source 다.** 별도 표를 두지 않는다.

`actions.json`(member sha256 `17d503f2…95ef`, 13 tape × 719 turn) 전수 확인 — 390개 (tape, day) 전부:
- `day == 0` 의 첫 HIRE 주문은 step 1, `day >= 1` 의 첫 HIRE 주문은 hour 0 이다. HIRE 가 없는 날은 없다.
- `T(first_hire_step(day)+1)` 은 그 턴의 HIRE 주문 개수와 정확히 같다.
- `T_first(day)` 의 분포는 3~10 이고 **0 인 날은 없다**.
- 하루 안에서 `T(s)` 는 단조 비감소이며, `s > first_hire_step(day)` 에서 `T(s) >= T_first(day)` 다.
- hands 길이가 증가하는 hour 는 13 tape 전체에서 {1, 2, 4, 5} 뿐이다.
- 모든 hour 0 step 에서 `T(s) = 0` 이다.

**판정 시점 — `s >= first_hire_step(day) + 1` 인 턴에서만 shortfall 을 읽는다.**

이전 판의 "hour 0 에는 shortfall 이 정의상 0" 은 **틀렸다.** 근거로 든 "모든 hour 0 에서 `T(s) = 0`" 은
사실이지만, `shortfall` 은 `T(s)` 가 아니라 `T_first(day)` 로 정의된다. `T_first(day) >= 3` 이고
hour 0 의 `A` 는 `_end_of_day` 직후라 0 이므로 **hour 0 의 shortfall 은 항상 3 이상**이다.
실측(target replay, seat 1): day 8 hour 0 = step 192 에서 `A = 0`, `T_first(8) = 8` → shortfall 8.
hour 0 을 배제하는 것은 정의가 아니라 **window** 다(§C-2).

`day == 0` 은 hour 창만으로 부족하다. 첫 HIRE 가 step 1(hour 1)이므로 step 1 관측 시점에는
`A = 0`, `T_first(0) >= 3` 이라 **아직 시도조차 하지 않은 고용을 부족으로 오판**한다.
`s >= first_hire_step(day) + 1` 하나가 day 0 의 step 1 과 day >= 1 의 hour 0 을 **같은 규칙으로** 배제한다.

**하루에 한 번만 재는 값.**
```
A_ontime(day)         = A  at  s = first_hire_step(day) + 1
shortfall_ontime(day) = max(0, T_first(day) - A_ontime(day))
```
`day` 가 **recovery day** 인 것은 `shortfall_ontime(day) >= 1` 과 동치다. 다른 시점에서 다시 판정하지 않는다.
하루 안에서 `A` 는 비감소이므로(`_do_hire` 는 append 만 하고 `hands` 는 `_end_of_day` 에서만 비워진다)
`shortfall_ontime(day)` 가 그날 shortfall 의 최댓값이다.
`recovery_days`(§D-2)와 §C-4 의 통제 대상 판정은 **모두 이 한 값**으로 한다.

**second wave(hour 2/4/5 증가분)는 §C-3 의 추가 HIRE 트리거 대상이 아니다.**
이유는 §C-4 의 spawn 계산이 "hour 0 시점 `hands == []`, `farmer == (4,4)`" 라는 엔진 보장 위에서만
정확하기 때문이다. second wave 고용이 실패해도 그 부족분은 `shortfall` 에 들어가지 않고
(`T_first` 는 first wave 만 센다) 추가 HIRE 를 요청하지 않는다. 그 slot 의 tape action 은 §C-1 에서 잘려 나간다.

**다만 "트리거 대상 아님" 은 "손대지 않음" 이 아니다.** recovery day 에 second wave 로 실제 생긴 hand 는
index 가 `>= A_ontime(day)` 이므로 §C-4 의 통제 대상이 된다. 이유는 그 hand 가
tape slot `j` 가 전제하는 시각·칸에서 생기지 않았기 때문이다 — recovery day 에는 `A_ontime < T_first` 라
그 hand 의 spawn 칸 점유 상태가 tape 가 가정한 것과 다르고, base action 을 그대로 주면 위치가 어긋난다.
recovery day 가 아닌 날(`shortfall_ontime(day) == 0`)에는 second-wave hand 를 포함해 통제 대상이 하나도 없다.

### C-1 존재하는 hand 에만 작업 배정 (trim)

`s < 718` 인 모든 턴에서, emit 하는 `action["hands"]` 의 길이는 **항상 정확히 `A`** 다. 기준은 `PA["hands"]` 다.
- `len(PA["hands"]) > A` → 뒤에서 잘라낸다. 잘린 action 은 엔진에서도 no-op 였으므로 게임 상태는 바뀌지 않지만,
  `:916-934` 의 PLANT 수요 집계에서 빠지므로 **seed-blocked PLANT 는 달라질 수 있다**(측정 대상, §E G3).
- `len(PA["hands"]) < A` → `["PASS"]` 로 채운다(§C-4 가 채우지 못한 index 만 해당).
- `len(PA["hands"]) == A` → **원소 그대로**. 이때 이 규칙은 no-op 다.
- `s == 718` 은 §C-A 의 마지막 턴 예외로 이 규칙에서 제외된다(liquidate 가 이미 길이 `A` 를 보장한다).

이 규칙은 `shortfall_ontime` 을 보지 않고 **길이만** 본다. `len(PA["hands"]) > A` 는
(a) first-wave 부분 체결(= recovery day) 뿐 아니라 (b) second-wave 고용 실패로도 생길 수 있고,
(b) 는 recovery day 가 아니므로 추가 HIRE 없이 trim 만 일어난다. 두 경우를 구분하지 않는다.

P1b 16 record 중 14개에서 `hands_length_mismatch_count = 0` 이므로, 그 14개에서 (a)·(b) 둘 다 없었고
C-1 은 증명된 no-op 다.

### C-2 트리거 — 언제 부족을 확인하고 언제 재시도를 끝내는가

`shortfall(s) = max(0, T_first(day) - A)` — **`s >= first_hire_step(day) + 1` 인 턴에서만 정의**한다(§C-0).
그 밖의 턴에서 recovery 는 shortfall 을 읽지 않는다.

`RECOVERY_FIRST_HOUR = 1`, `RECOVERY_LAST_HOUR = 11`.
- hour 0 은 **window 로** 배제한다(정의상 0 이어서가 아니다 — §C-0).
- 어떤 tape 에서도 계획된 인원 증가는 hour 5 이후에 없다. hour 11 은 그 뒤 6시간의 재시도 여유이며,
  target episode 에서 day1 의 money 가 0 을 벗어나는 최초 시각 h9 를 포함하도록 고른 **고정 상수**다.
  실행 후 이 값을 조정하지 않는다.
- `hour > RECOVERY_LAST_HOUR` 에서는 **추가 HIRE 를 emit 하지 않는다**(§C-3 조건 1). 그뿐이다.
  window 는 §C-3 에만 걸리고 §C-4 에는 걸리지 않는다: 이미 통제 대상이 된 hand 의 emit 규칙은
  hour 와 무관하게 그날 끝까지 계속 돌고, **hour 11 에 고용된 hand 가 hour 12 에 처음 관측되면
  그 턴에 queue/walk 를 만든다.** (이전 판의 "새 route 를 시작하지 않는다" 는 이 경계를 금지하는 것으로도
  읽혔다. 금지하지 않는다 — 금지하면 window 마지막 턴의 고용이 일은 못 하고 코인만 쓰는 고용이 된다.)

**하루 상한 2개. 둘 다 §C-3 실행식의 조건이다 — 문장 상한이 아니다.**

| 상수 | 값 | counter | 증가 규칙 |
|---|---|---|---|
| `MAX_RECOVERY_HIRE_TURNS` | 4 | `hire_turns_today` | 추가 HIRE 를 **emit 한 턴마다 정확히 1**. 엔진에서의 성공·실패, 요청 건수와 무관 |
| `MAX_RECOVERY_HIRES_PER_DAY` | 8 | `hires_added_today` | 그 턴에 emit 한 `n_afford` 만큼 |

두 counter 는 day 가 바뀌는 첫 턴에 0 으로 초기화한다(모든 per-day 상태와 함께, §C-4 말미).
`hire_turns_today` 는 §C-3 조건 4, `hires_added_today` 는 §C-3 조건 5 의 `cap` 에 들어간다.
**어느 쪽이 먼저 걸리든 그날의 추가 HIRE 는 거기서 끝난다.** 둘 사이에 우선순위는 없다.
target episode 에서 필요한 값은 day1 1턴/3건, day8 1턴/6건 이므로 두 상한 모두 binding 되지 않는다.

### C-3 HIRE 주문 위치와 자금 배분

턴 `s` 가 **hire-eligible** 인 조건은 아래 **다섯 가지를 모두** 만족하는 것이다.

1. `s >= first_hire_step(day) + 1` **그리고** `RECOVERY_FIRST_HOUR <= hour <= RECOVERY_LAST_HOUR`
2. `shortfall(s) >= 1`
3. `PA["market"] == []` — **parent 의 최종 action 에 그 턴 주문이 하나도 없다.**
   `yh` 의 tape·`subtract_advanced_sales`·`advance_sales` 와 `_layer` 의 due 정산·clone-preempt·
   `[:MAX_ORDERS]` 절단을 **모두 거친 뒤**의 값이다(§C-A). `base_action["market"]` 이 아니다.
4. `hire_turns_today < MAX_RECOVERY_HIRE_TURNS`
5. `n_afford >= 1`, 여기서
   ```
   money = float(F["money"]); h0 = int(F["hires_today"]); n = 0
   cap = min(shortfall(s), MAX_RECOVERY_HIRES_PER_DAY - hires_added_today)
   while n < cap:
       cost = mult * fib(h0 + n)          # fib(0)=1, fib(1)=1, fib(2)=2, fib(3)=3, fib(4)=5, ...
       if cost > money: break
       money -= cost; n += 1
   n_afford = n
   ```
   `cap <= 0` 이면 `n_afford = 0` 이므로 조건 5 는 불충족이다.

eligible 이면 `action["market"] = [["HIRE"]] * n_afford` 로 **치환**하고
`hire_turns_today += 1`, `hires_added_today += n_afford`,
record counter `recovery_hire_turns += 1`, `recovery_hire_requested += n_afford`.
eligible 이 아니면 `action["market"] = PA["market"]` 그대로이고 네 counter 는 건드리지 않는다.
`hire_turns_today` / `hires_added_today` 는 **하루마다 0 으로 초기화**되는 per-day 상태이고,
`recovery_hire_turns` / `recovery_hire_requested` 는 **record 전체 누적**이다(§D-2).

**조건 3 이 자금 배분 규칙 전부다.** `PA` 의 기존 주문은 밀려나지도, 잘리지도, 재배치되지도 않는다
(§`fixed` 의 opening schedule 불변, EXP-008 부활 아님). clone-preempt 가 그 턴에 SELL 을 붙였다면
`PA["market"] != []` 이므로 recovery 는 그 턴을 건너뛴다 — **clone-preempt 주문은 구조적으로 보존된다.**
이것이 §C-A 의 순서를 강제하는 두 번째 이유다.

그 턴에 우리 주문이 HIRE 뿐이므로 HIRE 실행 시점의 money 는 관측된 money 와 **정확히 같다**:
`:935-940` 에서 모든 unit action 이 `_process_market` **앞**에 적용되고,
`farm["money"]` 를 바꾸는 곳은 market commit(`:657-684`) 뿐이며, 상대 주문은 우리 money 에 영향이 없다.
또 `_hire_cost` 는 `farm["hires_today"]` 를 쓰고 `hires_today` 는 **성공 시에만** 증가하므로(`:702-708`)
위 `while` 의 `fib(h0 + n)` 은 n번째 추가 HIRE 의 실제 비용과 일치한다.
따라서 `n_afford` 건은 전부 체결되고 **recovery 가 추가한 HIRE 의 실패는 구조적으로 0** 이다
(§E G1 의 `recovery_hire_failed = 0`). `n_afford <= 8 <= MAX_ORDERS` 이므로 order truncation 도 없다.

**발화 턴 (target episode, `PA` 기준 사전 확인).**
출처는 tape 가 아니라 `private_artifacts/replays/episode-108076177-replay.json` 의
seat 1 action stream 이다. 이 replay 의 action 은 EXP-006 parent 가 실제로 반환한 값이므로 곧 `PA` 다.

| day | 발화 턴 | 그때 money / hires_today / A | shortfall | 요청 | 비용 | 그 앞 턴들이 탈락한 이유 |
|---|---|---|---|---|---|---|
| 1 | step 34 (h10) | 71 / 0 / 0 | 3 | 3 | 1+1+2 = 4 | h1~h5 는 `PA["market"] == []` 이지만 money 0 → 조건 5 불충족. h6~h9 는 `PA["market"] != []` → 조건 3 불충족(h9 는 money 100) |
| 8 | step 193 (h1) | 90 / 2 / 2 | 6 | 6 | 2+3+5+8+13+21 = 52 | h0 은 조건 1(window)·3 둘 다 불충족 |

두 날 모두 발화 직후 `A == T_first(day)` 가 되어 그날 `shortfall(s) = 0` 이므로 추가 발화가 없다.
발화 이후의 money 궤적은 parent 와 달라지므로 위 표는 **첫 발화 턴까지만** 사전 확정된 사실이다.

**사전 식별된 부작용(가리지 않는다).** day8 에서 52코인을 고용에 쓰면 tape 가 h4(step 196)에 계획한
`BUY_PRODUCT WHEAT 6 / BUY_ANIMAL SHEEP 2 / BUY_PRODUCT FERTILIZER 1`(관측상 약 64코인) 중 일부가
자금 부족으로 실패할 수 있다. 이는 recovery 의 실제 비용이며 `buy_failed` 로 관측된다.
**예비금(reserve)을 두지 않는다.** reserve 를 두려면 그 값을 결과를 보기 전에 골라야 하는데
엔진에서 유도되는 값이 없어 자유 파라미터가 되고, 한 요인 실험의 factor 정의가 흐려진다.
reserve 0 은 **이 카드에서 택한 설계 선택**이며, 다른 reserve 규칙이 원리적으로 금지된다는 주장은 하지 않는다(§J-7).
`buy_failed` 는 target record 에서 **diagnostic** 이고(§E diagnostic 목록), parity record 에서는 gate 다(§E G2).

### C-4 늦게 고용한 hand — 위치·소지품·놓친 작업

**소지품.** `_do_hire` 가 `inventories.append({})` 하므로 늦은 hand 의 소지품은 언제나 빈 dict 다.
parent 의 같은 slot hand 도 spawn 시점에 빈 dict 였다.
따라서 **그 slot 의 하루 route 를 처음부터 재생하는 방식만이 출발 조건(빈 소지품)과 일치**한다.
route 중간부터 붙이는 skip-forward 는 갖고 있지 않은 물건을 전제하므로 채택하지 않는다.
다만 전체 재생이 성공을 보장하지는 않는다 — 늦은 PICKUP 시점에 shed 에 그 물건이 없을 수 있다.
이는 이 카드가 택한 방식의 잔여 위험이며, 그때의 PICKUP 은 no-op 으로 `route_desync` 계열
diagnostic(§D-3)에 잡힌다. "유일하게 정합적" 이라고 주장하지 않는다(§J-6).

**통제 대상(slot).** `F["hands"]` 는 append 만 하므로 하루 동안 index 가 고정된다.
`shortfall_ontime(day) >= 1` 인 날(§C-0)에 한해, **index `j >= A_ontime(day)` 인 hand 를 전부
recovery 통제 대상**으로 둔다(우리가 고용했든 tape 의 second wave 가 고용했든 동일 취급).
index `j` 가 통제 대상으로 **처음 판정되는 턴에 `recovery_hands_created += 1`** 한다
(hand 당 1회. 아래 idle hand 도 포함한다. 하루 경계에서 통제 상태를 폐기하므로 다음 날 같은 index 가
다시 통제 대상이 되면 다시 1 증가한다).
recovery 통제 hand `j` 는 **tape slot `j`** 를 맡는다. `j >= T_first(day)` 이면 그날 내내 `["PASS"]` 이고
`recovery_idle_hands` 를 증가시킨다(hand 당 1회. 이 경우 `spawn_slot[j]` 는 계산하지도, 필요하지도 않다).
index `j < A_ontime(day)` 인 hand 는 `PA["hands"][j]` 그대로다.
`shortfall_ontime(day) == 0` 인 날에는 통제 대상이 하나도 없다.

**위치.** slot `j` 의 그날 spawn 칸 `spawn_slot[j]` 를 `first_hire_step(day)` 턴에 한 번 계산한다.
그 턴의 상태는 엔진이 보장한다: `F["hands"] == []`(전수 확인: 모든 hour 0 에서 `T(s)=0`, day0 은 step 1 이 첫 HIRE),
`day >= 1` 이면 `F["farmer"] == (4,4) = _default_spawn(10)`.
```
fpos = apply_move(F["farmer"], emitted_farmer_op)     # 우리가 그 턴에 낼 farmer action 기준
sim  = []
for k in range(T_first(day)):
    sim.append(spawn_hand(fpos, sim))                 # §A 의 _spawn_hand 를 그대로 복제
spawn_slot = sim
```
`spawn_hand(fpos, sim)`:
```
SHED = [(4,4),(5,4),(4,5),(5,5)]                      # _shed_access_tiles(10), NWSE 순서
occ  = {t: 0 for t in SHED}
for p in [tuple(fpos)] + [tuple(x) for x in sim]:
    if p in occ: occ[p] += 1
return min(SHED, key=lambda t: (occ[t], SHED.index(t)))
```
`apply_move(p, op)`: `op` 가 `FARMER_MOVES = {"NORTH":(0,-1), "SOUTH":(0,1), "EAST":(1,0), "WEST":(-1,0)}`
에 있으면 `(x+dx, y+dy)` 로 옮기되 `0 <= nx < 10 and 0 <= ny < 10` 이 아니면 **이동하지 않는다.**
`kaggriculture.py:323-331` 은 clamp 가 아니라 **거부**다(경계 밖이면 `return`, 위치 불변).
LOCKED tile 은 이동을 막지 않는다(같은 주석). `op` 가 이동이 아니면 위치는 그대로다.
이 계산은 우리가 **실제로 낼 farmer action** 을 쓰므로 repair_weeds 의 DIG 치환까지 반영된다.

**놓친 작업 — catch-up walk 후 지연 재생, 해질녘 절단.**
recovery 통제 hand `j` 가 관측에 처음 나타난 턴에 **한 번만** 아래를 만든다(이후 재계산하지 않는다).
- `queue_j = deque(tape[t]["hands"][j] for t in day_steps(day) if j < T(t))`
  — slot `j` 의 그날 route **전체**, tape 순서. `day_steps(day) = [day*24 .. min(day*24+23, 718)]`.
  관측 시점 이전의 원소도 버리지 않는다(지연 재생).
- `walk_j = deque(...)` = 관측 위치에서 `spawn_slot[j]` 까지의 결정적 이동열:
  `x < tx → "EAST"`, `x > tx → "WEST"` 를 먼저 다 낸 뒤 `y < ty → "SOUTH"`, `y > ty → "NORTH"`.
  shed 인접 4칸 사이의 L1 거리는 최대 2 이므로 `len(walk_j) <= 2`.
- `arrived_j = (len(walk_j) == 0)`, `expect_j = spawn_slot[j]`, `abandoned_j = False`.

매 턴 emit 규칙 — **위에서부터 처음 맞는 하나만** 실행한다.

1. `abandoned_j` 면 → `["PASS"]`. (아무 counter 도 증가시키지 않는다.)
2. `walk_j` 가 비어 있지 않으면 → `walk_j.popleft()` 를 emit, `recovery_walk_actions += 1`.
   **이 턴에는 `queue_j` 를 소비하지 않고 위치 검사도 하지 않는다.**
   `expect_j` 는 `spawn_slot[j]` 로 **고정 유지**한다(갱신하지 않는다).
   이 pop 으로 `walk_j` 가 비면 `arrived_j = True` 로 둔다 — 검사는 **다음 턴부터**다.
3. `arrived_j` 이고 관측된 hand `j` 의 위치 `!= expect_j` 이면 → `["PASS"]` 를 emit,
   `recovery_route_abandoned += 1`, `abandoned_j = True`,
   남은 `len(queue_j)` 를 `recovery_dropped_queue_actions` 에 더하고 `queue_j` 를 비운다.
   정상 구현에서는 발생하지 않는다 — **G1 gate**.
4. `queue_j` 가 비어 있지 않으면 → `a = queue_j.popleft()` 를 emit, `recovery_route_actions += 1`.
   **pop 은 emit 하는 턴에 정확히 1회**다. `a` 가 이동이면 `expect_j = apply_move(expect_j, a)`,
   이동이 아니면 `expect_j` 는 그대로다.
5. 그 밖에는 `["PASS"]`.

`expect_j` 를 갱신하는 곳은 **규칙 4 하나뿐**이다. 규칙 1·2·3·5 는 갱신하지 않는다.
(이전 판의 "emit 한 이동마다 갱신한다" 는 walk 이동까지 포함해 읽혀, 목적지에서 다시 걸어나가는 해석을 허용했다.)
window(§C-2) 는 §C-3 의 추가 HIRE 에만 걸린다. 이미 통제 중인 hand 의 위 규칙은 `hour > 11` 에도 계속 돈다.

**PLANT 씨앗 guard (recovery 전용).** action 을 다 조립한 뒤, 엔진 `:917-928` 과 동일한 방식으로
`[farmer, *hands]` 의 crop 별 PLANT 수요를 센다.
```
for c in demand:
    while demand[c] > int(private["seeds"].get(c, 0) or 0):
        j = (현재 emit 이 ["PLANT", c] 인 recovery 통제 hand 중 가장 큰 index)
        if j is None: break
        emit[j] = ["PASS"]; demand[c] -= 1; recovery_plant_yielded += 1
```
- `break` 로 빠져나온 경우(= farmer 와 base hand 의 요청만으로 이미 씨앗을 넘긴 경우) 그 crop 은
  어차피 엔진에서 전부 PASS 된다. 이때 **이미 PASS 로 바꾼 recovery PLANT 를 되돌리지 않는다.**
- guard 로 PASS 된 원소는 `queue_j` 로 **되돌리지 않고 재시도하지 않는다**(규칙 4 에서 이미 pop 되었다).
  근거: 되돌리면 slot `j` 의 그날 route 가 tape 순서와 어긋나고, 씨앗이 계속 모자라면 종료하지 않는다.
  대가는 그 tile 에 작물이 심기지 않아 같은 slot 의 이후 WATER/HARVEST 가 no-op 이 되는 것이며,
  `hand_tile_noop_actions`(diagnostic, §D-3)에 잡힌다. 가리지 않는다.
- farmer 와 base hand(`j < A_ontime(day)`)의 PLANT 는 절대 건드리지 않는다.
- 이 guard 가 없으면 늦은 hand 의 PLANT 요청이 `:916-934` 의 atomic 차단을 새로 유발할 수 있다.

**해질녘.** 그날 layer 가 마지막으로 실행되는 턴 — `hour == 23`, 단 day 29 는 `s == 718` —
의 emit 이 끝난 뒤 남은 `len(queue_j)` 를 `recovery_dropped_queue_actions` 에 더하고 전부 버린다.
`walk_j` 에 남은 원소는 세지 않는다(작업이 아니다).
이어서 `T_first`, `A_ontime`, `spawn_slot`, `hire_turns_today`, `hires_added_today`,
그리고 hand 별 `queue_j / walk_j / expect_j / arrived_j / abandoned_j` 를 전부 폐기한다.
다음 날은 엔진이 `hands` 를 비우므로(`:866-884`) 어떤 상태도 이월하지 않는다.

**예외 처리.** recovery 전체를 try/except 로 감싸고(§C-A), 예외 시 `PA` 를 그대로 돌려주며
`recovery_raise += 1`. 어떤 상태에서도 raise 하지 않는다(AGENTS §6).
parent 자신의 `base_raise` / `layer_raise` 는 parent 코드 그대로 유지하고 값을 바꾸지 않는다.

### C-5 무변화 동치 (parity property)

어떤 record 에서 **모든 날에** `len(PA["hands"]) == A` 이고 hire-eligible 턴이 한 번도 없었다면,
C-1 은 no-op, C-2/C-3 은 아무것도 추가하지 않고, C-4 는 통제 hand 가 없으므로 아무것도 하지 않는다.
이때 emit 되는 dict 의 `farmer` / `hands` / `market` 은 `PA` 와 동일하고,
§D-1 의 metadata 규칙에 따라 추가 키도 붙지 않으므로 **`PA` 와 byte-identical** 이다.
이것이 G2 가 검사하는 성질이다.

### C-6 채택하지 않은 더 작은 대안과 그 이유 (기록)

| 대안 | 왜 아닌가 |
|---|---|
| hands 배열만 자르기 | 제안서가 "복구가 아니다" 라고 명시. 인원이 회복되지 않는다. |
| 늦은 hand 를 그날 내내 PASS | `_end_of_day` 가 hands 를 비우므로 늦은 고용의 가치는 당일뿐이다. 이익이 구조적으로 0 이고 코인만 쓴다. |
| index 순 queue shift (spawn 보정 없음) | day1 재현: parent slot 0/1/2 의 spawn 은 `(5,4)/(4,5)/(5,5)`, 늦은 고용의 spawn 은 farmer 가 shed 칸을 떠난 뒤라 `(4,4)/(5,4)/(4,5)`. route 전체가 한 칸씩 어긋난다. |
| skip-forward (현재 step 의 tape action 부터) | 소지품이 빈 상태인데 route 중간은 PICKUP 이후를 전제한다. 위치도 어긋난다. |
| HIRE 를 SELL 뒤로 재배치 | day8 은 고치지만 day1 은 팔 것이 없어 못 고친다. 그리고 무조건 재배치는 무변화 동치(§C-5)를 깬다. |
| 현재 상태에서 route 재생성 | 한 요인이 아니다. tape 계열 전체를 바꾸는 별도 전략이다. |

## §D 계측 정의 — 실행 전에 동결

### D-1 `tools/instrument.py` 확장과 metadata 경계 (Codex 소유, 실행 전 SHA freeze)

1. `noop_actions` 를 unit index 별로 분리해 `noop_by_unit_index: dict[int,int]` 를 추가한다.
   기존 `noop_actions` 총합의 정의와 값은 바꾸지 않는다.
2. **metadata 키는 "emit 이 `PA` 와 다른 턴" 에만 붙인다.** `__exp013` 키 하나에 dict 로 담는다.
   candidate 는 emit 을 확정한 뒤 `emit["farmer"] / emit["hands"] / emit["market"]` 세 필드를
   `PA` 의 같은 세 필드와 비교하고, **셋 다 같으면 `__exp013` 을 붙이지 않는다.**
   다르면 그 턴의 recovery counter 증분을 담아 붙이고 `recovery_trigger_turns += 1`.
   이 규칙은 선택지가 아니라 **동결된 계약**이다. 이유:
   `tools/instrument.py:546` 의 `_audited` 는 `action_stream.append({"step": ..., "action": copy.deepcopy(action)})`
   로 **action dict 전체**를 저장하고, `action_stream_sha256`(`:287-289`)은
   `json.dumps(..., sort_keys=True)` 를 해싱한다. 따라서 값이 `0` 이어도 키가 붙으면 hash 가 달라진다.
   무트리거 14 record 에서 `__exp013` 을 붙이면 **동작이 같아도 G2 의 hash 비교가 FAIL** 한다.
   기존 parent hash 는 손대지 않는다(P1b 산출물은 읽기 전용).
3. `recovery_trigger_turns` 는 위 **세 필드의 차이**로 정의한다. **metadata 키의 유무로 세지 않는다.**
   metadata 가 붙는 턴 집합과 세 필드가 다른 턴 집합이 일치하는 것은 candidate 구현이 지켜야 할
   불변식이며, G2(hash 동일 ∧ `recovery_trigger_turns = 0`)로 외부에서 확인된다.
4. `missing_hand_dependent_actions` 와 `residual_headcount_deficit` 은 runner 에서 관측·emit 으로 계산한다
   (metadata 를 쓰지 않는다).
5. 엔진이 `farmer`/`hands`/`market` 외의 키를 무시하는 것은 확인했다(`kaggriculture.py:912-934` 는
   `action.get("farmer")`, `action.get("hands")` 만 읽고, `_process_market` 은 `market` 만 읽는다).
   action schema(`kaggriculture.json` 의 `action`)는 `{"type": "object"}` 이고
   `additionalProperties` 제약이 없어 `jsonschema.validate`(`utils.py:187-195`)를 통과한다.

### D-2 counter 정의 (전부 player record 단위)

| 이름 | 정의 |
|---|---|
| `recovery_days` | `shortfall_ontime(day) >= 1` 인 날의 수. 하루에 한 번, `s = first_hire_step(day)+1` 에서만 판정한다(§C-0) |
| `recovery_trigger_turns` | emit 의 `farmer`/`hands`/`market` 이 `PA` 의 같은 세 필드와 다른 턴 수(§D-1) |
| `recovery_hire_turns` | 추가 HIRE 를 emit 한 턴 수. 하루 상한 `MAX_RECOVERY_HIRE_TURNS = 4`(§C-2) |
| `recovery_hire_requested` | layer 가 추가한 `["HIRE"]` 주문 총 건수. 하루 상한 `MAX_RECOVERY_HIRES_PER_DAY = 8` |
| `recovery_hire_failed` | 추가 HIRE 중 다음 관측에서 `len(hands)` 증가로 이어지지 않은 건수 |
| `recovery_hands_created` | recovery 통제 대상이 된 hand 수 |
| `recovery_walk_actions` | §C-4 규칙 2 의 catch-up 이동 emit 수 |
| `recovery_route_actions` | §C-4 규칙 4 의 queue action emit 수 |
| `recovery_route_abandoned` | 기대 위치 불일치로 포기한 hand 수(§C-4 규칙 3) |
| `recovery_idle_hands` | `j >= T_first(day)` 라 그날 내내 PASS 한 hand 수 |
| `recovery_plant_yielded` | 씨앗 guard 로 PASS 된 recovery PLANT 수 |
| `recovery_dropped_queue_actions` | 해질녘 절단 + 규칙 3 포기로 버려진 queue action 수 |
| `recovery_raise` | recovery 블록 예외 포착 수 (candidate 전용) |
| `layer_raise` | parent `_layer` 예외 포착 수 (parent·candidate 공통, parent 코드 그대로) |
| `base_raise` | parent base agent 예외 포착 수 (parent·candidate 공통) |

### D-3 route desynchronization 정의 (제안서가 요구한 동결 대상)

네 성분으로 나눈다. 각각 독립으로 기록한다.

- **누락 인원** `residual_headcount_deficit = Σ_day max(0, T_first(day) - A(day*24 + 12))`.
  hour 12 는 recovery window(hour <= 11) 종료 직후의 고정 관측 시각이다.
  target parent 값 = **9** (day1 3 + day8 6).
- **존재하지 않는 hand 에 배정된 작업** `missing_hand_dependent_actions = Σ_turn max(0, len(emit["hands"]) - A)`.
  target parent 값 = **207** (46턴). candidate 는 C-1 때문에 **구조적으로 0** 이다 →
  이것은 **구현 준수 확인이지 효과 증거가 아니다**. §E G3 에서 그렇게 표기한다.
- **hand 의 tile-op 무변화** `hand_tile_noop_actions = Σ noop_by_unit_index[i] for i >= 1`.
  **이전 판의 이름 `route_desync_units` 를 폐기한다.** 이 값은 기대 위치·기대 소지품과의 비교가 아니다.
  `tools/instrument.py:423-450` 의 실제 판정은 다음과 같다:
  `op` 가 `_TILE_OPS`(PLANT/WATER/HARVEST/FERTILIZE/DIG/BUILD_*/FEED/COLLECT_FERTILIZER/CARE/PICKUP/PLACE/DROP)
  일 때, **행동 직전 그 unit 이 서 있던 tile 의 signature** 와 `_inv_total`(그 unit 인벤토리 **총량**)이
  둘 다 불변이면 `noop_actions += 1`. 이동(`_MOVES`)은 여기서 제외되고 실패 시 `blocked_moves` 로 따로 센다.
  즉 (a) 기대 위치와 비교하지 않고, (b) item 별 inventory 가 아니라 총량만 보며, (c) 이동 실패는 포함하지 않는다.
  route 가 어긋나면 이 값이 커지는 경향은 있으나 **route 정합성 검사가 아니다.**
  **이 값은 diagnostic 이다.** parent 의 phantom action 은 `pos is None` 으로 즉시 return 되어(`:311-317`)
  어느 counter 에도 잡히지 않으므로 parent ↔ candidate 의 부등식이 well-posed 하지 않다. gate 로 쓰지 않는다.
  기대 위치·기대 item 별 소지품과 비교하는 별도 검사는 이 카드에서 정의하지 않는다(필요하면 새 카드).
- **남은 작업** `pending_work = recovery_dropped_queue_actions + recovery_idle_hands`. diagnostic.

## §E 숫자 gate — 실행 전에 동결

parent 16 record 를 **먼저** 기록하고, 그 다음 candidate 16 record 를 같은 13경기로 기록한다.

### G0 identity·재현 (hard)
- tar/member SHA, engine py/json SHA, `metric_schema_version == 3`, 13/13 episode, 720 step, `DONE/DONE`: 불일치 0.
- **G0b** — 확장된 runner 로 다시 기록한 parent 16 record 의
  `noop_actions / shed_discarded / buy_failed / hire_failed / seed_blocked_plant /
  hands_length_mismatch_count / orders_truncated / exceptions / rewards` 가
  P1b(`46fd9e5e…801c`) 값과 **전부 일치**해야 한다(target 1,149 / 209 / 34 / 9 / 16 / 46 / 0 / 0 / 58,246 등).
  하나라도 다르면 계측이 경기를 바꾼 것이므로 **결과 전체 INVALID**, 원인 주장 금지, 계측을 고쳐 다시 돌린다.

### G1 safety — candidate 16 record 전부 (hard)
`exceptions = 0` · `base_raise = 0` · `layer_raise = 0` · `recovery_raise = 0` ·
`orders_truncated = 0` · `recovery_hire_failed = 0` ·
`recovery_route_abandoned = 0` · `hands_length_mismatch_count = 0`.
하나라도 0 이 아니면 **FAILURE**.
`layer_raise`(parent `_layer`)와 `recovery_raise`(새 블록)는 별개 counter 다(§C-A, §D-2).

### G2 parity — 무트리거 14 record (hard)
대상: P1b 에서 `hire_failed = 0` 인 gated record 14개 (self_play 6, builtin_smoke 6, control 2).
- `recovery_trigger_turns = 0`
- `action_stream_sha256(candidate) == action_stream_sha256(parent)`
- **`__exp013` 키가 붙은 턴 0** — §D-1 의 metadata 규칙이 지켜졌는지 확인한다.
  이 record 들에서 키가 하나라도 붙으면 동작이 같아도 위 hash 가 달라지므로 FAIL 로 나타난다.
  계측이 추가 키 때문에 parity 를 깨뜨린 것인지, 실제 동작이 달라진 것인지는
  `recovery_trigger_turns` 와 키 유무로 구분해 보고한다.
- reward 동일, `noop_actions / shed_discarded / buy_failed / seed_blocked_plant` 동일
차이가 하나라도 있으면 **FAILURE**. (EXP-008 은 G5 parity 를 38셀에서 실패했다. 같은 함정을 4셀로는 못 잡는다.)

### G3 mechanism — target 2 record (hard)
- `residual_headcount_deficit`: parent 9 → candidate **= 0**
- `missing_hand_dependent_actions`: parent 207 → candidate **= 0** (구현 준수 확인, 효과 증거 아님)
- `recovery_days = 2` (day1·day8. §C-0 의 `shortfall_ontime` 기준 — 하루 한 번 판정이므로
  daily reset 이 값을 부풀리지 않는다. hour 0 에서 재면 30 이 나온다)
- `recovery_hire_turns = 2` 이고 `recovery_hire_requested = 9` (day1 1턴/3건 + day8 1턴/6건)
- `recovery_route_actions >= 1` (실제로 작업을 했는가)
- `seed_blocked_plant`: candidate **<= 16**
- 양 좌석 대칭: 두 record 의 위 여섯 항목(`residual_headcount_deficit`, `missing_hand_dependent_actions`,
  `recovery_days`, `recovery_hire_turns`, `recovery_hire_requested`, `seed_blocked_plant`)이
  서로 같아야 한다(결정성 확인)
위반 시 **FAILURE**.

### G4 outcome — target 2 record (n = 1 seed)
- 양 좌석 모두 candidate final bank > parent final bank(58,246) → `TARGET_IMPROVED`
- 양 좌석 모두 동일 → `INCONCLUSIVE`
- 한 좌석이라도 낮으면 → `FAILURE`

**표본 경고(사전등록).** target 두 좌석은 같은 seed·같은 frozen transcript 의 거울상이며
parent 에서 정확히 `58,246 / 167,541` 로 대칭이었다. 따라서 **이것은 n = 2 가 아니라 n = 1 이고,
좌석 쌍은 결정성·대칭성 확인일 뿐 반복 표본이 아니다.**
게다가 이 episode 는 가설을 만든 바로 그 경기다. `TARGET_IMPROVED` 는
승격도, 제출 근거도, hosted 주장도 아니며 EXP-014(pool/public) 사전등록 자격만 준다.

### G5 control outcome — control 2 record (hard)
reward 가 parent 와 **정확히 동일**(115,745 / 99,654). G2 의 따름정리지만 따로 판정한다.

### G6 runtime (hard)
record 당 `total_s <= 623`, episode `wall_seconds <= 960`, hard ceiling `< 1200`. P1b 와 동일.

### diagnostic — gate 아님
`hand_tile_noop_actions`, `noop_actions`, `shed_discarded`, `hire_failed`, `buy_failed`(target record 한정),
`sell_unfilled`, `blocked_moves`, `recovery_*` 의 나머지, `pending_work`.
**diagnostic 의 개선을 효과로 선언하지 않는다.**

## §F 제안서 원안에 대한 타당성 검토

1. **4 cells 는 부족하다.** target 2 + control 2 로는 parity 를 확인할 수 없다.
   EXP-008 의 G5 parity 실패는 38셀에서 나왔고 그중 36셀은 pool 이었다.
   **새 상대·새 seed 를 추가하지 않고** 이미 동결된 P1b 13경기/16 record 로 확장한다.
   그중 14 record 가 `hire_failed = 0` 이므로 비용 0 의 parity cell 이 된다. target/control 2쌍은 그 안에 포함된다.
2. **"가장 작은 변경"의 경계.** C-1~C-4 는 분리 불가다. trim 없이 고용만 하면 phantom action 이 남고,
   고용 없이 trim 만 하면 복구가 아니며, route 규칙 없이 고용하면 늦은 hand 가 엉뚱한 칸에서 움직인다.
   따라서 이 카드는 **하나의 indivisible recovery mode** 를 잰다. 하위 규칙별 기여도는 주장하지 않는다.
3. **"correctness: hire_failed 증가 0" 은 그대로 쓸 수 없다.** candidate 는 HIRE 를 추가하므로
   `hire_failed` 가 늘 수 있다. C-3 조건 3 덕분에 **추가분의 실패는 0 임이 증명**되므로
   gate 를 `recovery_hire_failed = 0` 으로 바꾸고 `hire_failed` 는 target 에서 diagnostic 으로 둔다.
4. **"mechanism: route desynchronization" gate 는 정의 후에도 gate 로 승격하지 않는다.**
   §D-3 에서 정의는 동결했지만, parent 의 phantom action 이 어느 counter 에도 잡히지 않아
   parent ↔ candidate 부등식이 성립하지 않는다. 대신 `residual_headcount_deficit` 과
   `missing_hand_dependent_actions` 를 hard gate 로 쓴다.
   덧붙여 r2 에서 이름을 `route_desync_units` → `hand_tile_noop_actions` 로 바꿨다.
   기존 계측은 tile signature 와 인벤토리 **총량**의 불변 여부만 보므로 "route 정합성" 을 재지 않는다(§D-3).
5. **"target paired score 증가 > 0" 는 n=1 로 다시 쓴다**(§E G4). 원안의 "다음 큰 bank 카드 후보" 표현은
   승격 뉘앙스를 주므로 `EXP-014 사전등록 자격` 으로 한정한다.
6. **donor 관측은 근거에서 제외한다**(카드 서두 증거 경계). K3 재검토 아님, K1/K9 수정 없음.
6b. **적용 지점이 계약의 일부다.** recovery 를 `yh.agent()` 결과 위에 얹으면 clone-preempt 가
   재계산되거나 소실되고(§C-A), `yh.agent` 를 두 번 부르면 `DayState` 가 초기화되어 tape 자체가 달라진다.
   따라서 "parent 최종 action(PA) 뒤" 는 구현 편의가 아니라 **한 요인 실험의 성립 조건**이다.
6c. **하루 상한은 실행식의 조건이다.** `MAX_RECOVERY_HIRE_TURNS` 를 문장으로만 두면
   구현자가 조건 순서를 고르게 된다. r2 에서 §C-3 의 5번째 조건과 `cap` 에 각각 넣고
   counter 증가 시점(성공·실패 무관, emit 한 턴마다 1)을 고정했다.
7. **release zero gate 와의 관계.** parent 는 target record 에서 이미 zero gate 를 FAIL 한다.
   이 카드의 판정은 카드 gate 로만 하며(`tools/instrument.py` docstring 의 EXP별 gate 원칙),
   zero gate 를 낮추지도, 이 카드의 결과로 release 승인을 대신하지도 않는다.

## §G 실행 조건 — C1 경로, 지금은 BLOCKED

**P1b 현재 상태.** `P1-RELEASE-PREFLIGHT-EXP006-A-20260916` 은 승인된 13/13 episode 를
720-step DONE/DONE 으로 완료했으나 **gated parent 16/16 zero gate FAIL** 이다
(Identity/Runtime/Isolation/License PASS, Schema FAIL — `hands_length_mismatch_count` 92 ≠ 0).
Antigravity 독립 검증 `VERIFIED_LOCAL_FAILURE` (2026-09-16). **preflight PASS 가 아니다.**
BOARD P1b 의 종료 조건에 따라 **"새 전략 HOLD" 가 발효 중**이다.

### G-0 이 카드의 위치 — P2 가 아니라 C1

Coordinator 실행안
`coordination/proposals/codex/20260917-correctness-path/DECISION.md`
sha256 `286c492fd46a731626d08131934f5ba7965fb5c90cb9c333182b37102858a95d`,
보고 `coordination/reports/codex/20260917-COORDINATOR-CORRECTNESS-PATH.md`
sha256 `096a68ec665d19abbe4edb41cd8ae26e5b59dc20c1d7f769d607483865552274`
(VERDICT: PROPOSAL COMPLETE / EXECUTION NOT AUTHORIZED).

그 실행안은 BOARD 에 **P2 와 별개인 C0/C1 bounded correctness 단계**를 둔다.
이 카드는 그 중 **C1** 이다. C0 는 EXP-011 이다.

**BOARD P2 의 선행 조건("실제 parent P1b PASS")은 그대로 유지된다.**
이 카드는 그 조건을 삭제·완화·대체하지 않으며, 그렇게 해달라고 요구하지도 않는다.
(r2 까지의 §G 는 선행 조건을 번호 목록 1·2·3 으로 적었고, 그중 **2번**이
"BOARD P2 의 선행 조건 'P1b PASS' 가 'EXP-011 판정 기록 + 사람 승인' 으로 **대체되어야**
이 카드가 실행 가능하다" 였다. 그 요구를 **철회한다.** r3 의 `§G-2` 라벨은 그 철회된 항목과 무관하며
"승인받았을 때 실행 가능한 범위" 를 가리킨다. 실행안 §1 이 확인했듯
`plan/kaggriculture_deadline_plan_20260915.md:107` 은 이미 FAIL 뒤의 별도 correctness repair 경로를
허용하고 있으므로, P2 조건을 건드릴 필요가 애초에 없다.)

그 대신 이 카드에 걸리는 경계는 다음 세 가지다.

1. **C1 은 P2 를 열지 않는다.** 이 카드가 전부 PASS 해도 새 전략 HOLD 는 해제되지 않고,
   P2 의 "실제 parent P1b PASS" 조건은 그대로 남는다.
2. **C1 은 release PASS 를 대신하지 않는다.** 이 카드의 결과는 diagnostic 이며 제출 근거가 아니다.
   recovery 를 넣은 candidate 를 언젠가 내보내려면 그 **수정 artifact 가 별도로 전체 release preflight
   (zero gate 포함)를 처음부터 다시 통과**해야 한다. 이 카드는 그 preflight 의 일부가 아니다.
3. **"correctness" 라는 이름이 자동 승인이 아니다.** EXP-011 은 artifact 를 바꾸지 않는 attribution
   diagnostic 이지만, EXP-013 은 **행동을 바꾸는** bounded 실험이다(지연 route 재생 + 추가 HIRE).
   실행안 §1 의 이 구분을 이 카드가 흐리지 않는다. §D-3·§E 의 diagnostic/gate 분리가 그 장치다.

BOARD 정본은 이 개정에서 **변경하지 않았다.** BOARD 문안 적용 여부는 Coordinator/사람의 결정이며,
BOARD 를 고쳐도 이 §G 와 EXP-011 §D 가 자동으로 바뀌지 않는다(실행안 §4 말미).

### G-1 실행 전에 전부 기록되어야 하는 네 가지

아래 네 가지가 **전부 기록된 뒤에만** parent baseline(G0b) 기록을 시작한다.
하나라도 비면 문서 작업만 계속하고 경기는 돌리지 않는다.

1. **C0 판정 기록.** EXP-011(HYP-0031)이 사람의 별도 실행 지시를 받아 실행되고,
   D1~D4·R 판정과 §D 의 class 판정(`REPAIR_AUTHORIZED` / `BLOCKED_STRATEGY_BOUNDARY` /
   `BLOCKED_AMBIGUOUS_ROOT_CAUSE` 중 하나)이 `tools/update_hypotheses.py` 로 원장에 기록되고
   **독립 reviewer 의 결과 검토**를 받는다. C0 가 미실행·INVALID 이거나 D1~D4/R 중 하나라도 실패하면
   이 카드는 **대기**한다 — 실패한 자료로 scope 를 정하지 않는다(실행안 §3).
2. **판정별 분기 확인.** 실행안 §3 의 표를 이 카드에 그대로 적용한다.

   | EXP-011 판정 | EXP-013 의 상태 |
   |---|---|
   | 미실행 / INVALID / D1~D4·R 실패 | **대기.** 계측·identity 문제를 먼저 해결한다 |
   | 유효 + `REPAIR_AUTHORIZED` | **자동 승인 아님.** HIRE failure 가 shed 와 **별도 근거**를 갖는다는 scope 검토를 거쳐 사람 승인으로만 제한 실험 가능 |
   | 유효 + `BLOCKED_AMBIGUOUS_ROOT_CAUSE` | **대기.** shed 원인 미확정을 HIRE 실패의 원인 규명으로 간주하지 않는다. §G-1-3 의 범위 정정과 사람 승인 전에는 실행하지 않는다 |
   | 유효 + `BLOCKED_STRATEGY_BOUNDARY` | **자동 우회 금지.** EXP-013 도 지연 route 로 행동을 바꾸는 별도 bounded 행동 실험임을 공개해 검토받고, 범위 정정과 명시적 scope 승인 전에는 대기 |

   어느 칸에도 "EXP-011 이 이러이러하면 EXP-013 이 자동으로 실행된다" 는 없다.
3. **EXP-011 §D 금지 범위 해소.** EXP-011 §D 의 "`REPAIR_AUTHORIZED` 가 아니면 어떤 구현 card 도
   승인하지 않는다" 는 문구는 문자 그대로면 이 카드도 덮는다. owner(Claude)가
   `experiments/cards/EXP-011-shed-discard-attribution.md` §D-1(r2, sha256
   `8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e`)에 한정 근거를 적었고,
   **사람이 그 범위 해석을 승인**해야 발효한다.
   승인 전에는 원문의 광의 금지가 유지되므로 **이 카드는 실행 불가**다.
   Coordinator 도 이 한정을 묵시적으로 적용하지 않는다(실행안 §3 "공통 충돌").
   그리고 그 한정이 발효해도 그것은 **금지 사유 하나가 사라진 것**일 뿐 실행 승인이 아니다.
4. **사람의 exact-card 실행 승인.** 제안자(Claude)가 자기 설계를 단독 승인하지 않는다(AGENTS §4).
   승인 요청에는 수정 카드 SHA·독립 설계 검토·유효한 EXP-011 판정을 첨부한다(실행안 §5-3).

### G-2 승인받았을 때 실행 가능한 범위 (그 바깥은 별도 승인)

실행안 §2 의 D 단계와 §5-3 을 이 카드의 언어로 고정한다. 승인 범위는 **여기까지**다.

- candidate 구현(Codex) 과 unit 검증 → candidate `main.py` / 확장된 `tools/instrument.py` /
  상대 artifact SHA **freeze** → **독립 구현 검토**(설계자와 구현자가 아닌 제3자).
- G0b parent 16 record 재기록 → candidate 16 record, **동일 13경기**(§`seeds`).
- §E 의 gate 판정과 `experiments/results/exp013_hire_recovery/` 산출.

범위 **밖** (각각 별도 카드·별도 승인):
pool/public 확장(EXP-014), release preflight, Kaggle 제출, parent tar 변경, BOARD 변경,
seed·좌석·상대 추가, factor 분해, hour 경계 재탐색.

### G-3 shared runner 순차 통합 — 병렬 금지

EXP-011(C0)과 EXP-013(C1)은 **같은 `tools/instrument.py`** 를 바꾼다. 실행안 §2 의 제약을 그대로 받는다.

- 두 카드의 `tools/instrument.py` 변경과 실행을 **병렬로 진행하지 않는다.**
- EXP-011 용 runner 를 **commit / hash 로 고정**한다. EXP-013 의 §D-1 확장은
  **별도 commit 과 별도 baseline** 을 쓴다.
- 먼저 기록한 결과를 새 runner 의 결과로 **재사용하지 않는다.**
  §E G0b 가 이것을 강제한다 — 확장된 runner 로 다시 기록한 parent 16 record 가 P1b 값과
  전부 일치해야 하며, 하나라도 다르면 결과 전체 INVALID 다.
- 문서 작업(이 카드의 계약 수정·SHA 재동결)은 C0 와 **독립적으로** 진행할 수 있다(실행안 §2 A 단계).
  이 개정(r3)이 그 A 단계의 산출물이며, **실행 승인이 아니다.**

### G-4 독립성

실행안 §5 말미: 현재 독립 reviewer 담당자는 **N/A** 다.
Codex 는 Coordinator·integrator 를 맡지만 **자기 구현 결과의 독립 승인자가 될 수 없고**,
Claude 가 설계한 이 카드를 **Claude 단독으로 최종 승인하지도 않는다.**
독립 reviewer 가 지정되기 전에는 §G-1-1 의 "독립 결과 검토" 와 §G-2 의 "독립 구현 검토" 를 충족할 수 없다.

실행 시점에 parent tar SHA 가 `1c478c24…9721` 이 아니면 카드를 새 SHA 로 재동결하고 baseline 을 다시
기록한다. parent 가 바뀌면 §E G0b 기준의 유효성 자체를 다시 검토한다(실행안 §3 말미).

## §H Blocker — 설계로 해결되지 않는 항목

| ID | 내용 | 누가 푸는가 | 이 카드가 할 수 있는 것 |
|---|---|---|---|
| **BLK-1** | P1b 는 PASS 할 수 없고 새 전략 HOLD 가 유효하다. 이 카드는 그 HOLD 를 풀지 않는다. | Coordinator + 사람 | r3 에서 해소 경로 확정 — 이 카드는 P2 가 아니라 C1 이고 P2 조건은 유지된다(§G-0). 자체 승인 불가 |
| **BLK-1b** | EXP-011 §D 의 광의 금지 문구가 문자 그대로면 이 카드도 덮는다. | 사람(범위 해석 승인) | owner 한정 근거를 EXP-011 §D-1 에 기록. 승인 전 실행 불가를 §G-1-3 에 고정 |
| **BLK-2** | correctness 경로의 EXP-011(C0)이 아직 `PLANNED` 다. 우선순위상 먼저이고, 같은 `tools/instrument.py` 를 공유해 병렬 실행이 금지된다. | Codex 실행 / Claude 판정 / 사람 실행 지시 | 실행 순서를 §G-1 에, 순차 통합·runner 고정을 §G-3 에 고정 |
| **BLK-10** | 독립 reviewer 담당자가 N/A 다. Codex 는 자기 구현의 독립 승인자가 될 수 없고 Claude 는 자기 카드를 단독 승인하지 않는다. | 사람(담당자 지정) | §G-4 에 명시. 지정 전에는 §G-1-1·§G-2 의 독립 검토 조건을 충족할 수 없다 |
| **BLK-3** | target 은 **n = 1 seed** 이고, 가설을 만든 바로 그 경기다. 어떤 설계로도 비순환이 되지 않는다. | 별도 EXP-014 (pool/public, 새 상대 SHA·seed·gate) | G4 의 해석 상한을 §E 에 못박음 |
| **BLK-4** | hosted 효과 N/A. 제출은 FIFO 로 EXP-006 을 먼저 은퇴시킨다. | 사람 승인 | 제출 근거로 쓰지 않는다고 명시 |
| **BLK-5** | `tools/instrument.py` 에 `noop_by_unit_index` 와 `recovery_*` 가 없다. `tools/` 는 Codex 소유이며, 확장하면 runner SHA 가 바뀌어 P1b manifest 의 pin 과 달라진다. → **P1b 수치를 그대로 재사용할 수 없고 parent baseline 을 재기록해야 한다.** | Codex | §D-1 에 확장 범위, §E G0b 에 재현 검증 gate |
| **BLK-6** | `farmHandCostMult` 등 hosted configuration 은 사전 관측 불가다. 로컬은 기본값 1 이다. 값이 1 보다 크면 C-3 의 "추가 HIRE 실패 0" 증명이 "과소 요청" 으로만 약해진다. | 해결 불가 (hosted) | `configuration` 에서 읽도록 규정, 잔여 위험으로 기록 |
| **BLK-7** | HYP-0032 의 `실험` 필드가 `TEST-STATE-CONDITIONED-RECOVERY-PREREG` 다. `EXP-013 / TEST-0013` 확정은 원장 event 가 필요하다. | `tools/update_hypotheses.py` (Claude event) | 이 카드 커밋과 같은 턴에 event 기록 |
| **BLK-8** | day8 에서 고용에 쓴 52코인이 tape 의 h4 구매(약 64코인)를 실패시킬 수 있다. reserve 를 두면 튜닝 파라미터가 된다. | 해결하지 않음 (설계 선택) | reserve 없음을 §C-3 에 고정, `buy_failed` 를 diagnostic 으로 관측 |
| **BLK-9** | 늦은 hand 의 route 를 처음부터 재생해도 PICKUP 시점에 shed 에 그 물건이 없을 수 있다. 빈 inventory 는 출발 조건일 뿐 성공 보장이 아니다. | 해결하지 않음 (설계 선택) | §C-4 에 한정 문구, 실패 시 `hand_tile_noop_actions` diagnostic 으로 관측 |

## §I 재현

```bash
# 엔진·artifact 확인 (read-only)
shasum -a 256 coordination/proposals/claude/exp006/submission.tar.gz
python3 - <<'PY'
import hashlib, os, kaggle_environments as k
d = os.path.join(os.path.dirname(k.__file__), "envs", "kaggriculture")
for f in ("kaggriculture.py", "kaggriculture.json"):
    print(f, hashlib.sha256(open(os.path.join(d, f), 'rb').read()).hexdigest())
PY

# §B 의 46턴·207건·9명 재현 (read-only, 경기 실행 없음)
python3 tools/postmortem_hosted.py \
  --replay private_artifacts/replays/episode-108076177-replay.json \
  --control-replay private_artifacts/replays/episode-108079022-replay.json \
  --team Sian --focus-steps 24 25 34 192 193 204
```

실행 승인 후에는 P1b 와 동일한 13경기 runner 로 parent → candidate 순서로 기록하고
`experiments/results/exp013_hire_recovery/` 에 cell JSON·aggregate·verdict 를 남긴다.

## §J r2 개정 — codex 계약 검토 대응

검토서 `coordination/proposals/codex/20260917-EXP013-CONTRACT-REVIEW.md`
sha256 `54dcaf42541a3afbbb573e2c69dc3cb3d5c0ff7c0b47e77a0cedce742f63a2ef`.
이 카드의 r1(검토 대상) sha256 은 `96f0278293d56fe50e639f273abe6eaf5f5987c334d9d037cde63c3874354fd6` 다.
아래 확인은 전부 **이번에 직접 읽은 코드**다. parent tar 를 풀어 `main.py`(sha256 `bba042e0…96b2`)·
`yh_base.py`(`d6d74997…866b`)·`actions.json`(`17d503f2…95ef`) 을 읽고,
엔진 `.venv/.../kaggriculture/kaggriculture.py`(`bc8a5487…653e`) 와
`tools/instrument.py`(`284dee4c…0629`) 를 읽었으며, 경기는 실행하지 않았다.
tape·replay 통계는 read-only 로 재계산했다.

| # | 검토 지적 | 판정 | 확인한 근거 | 카드 반영 |
|---|---|---|---|---|
| 1 | `yh.agent()` 는 parent 최종 action 이 아니다. recovery 는 `_layer` 와 fallback 을 포함한 최종 action 뒤에 붙어야 한다 | **타당** | `main.py:126-137` — 반환값은 `_layer(yh, obs, deepcopy(base_action))` 또는 두 fallback | §C-A 신설. `PA` 정의, candidate 구조 코드로 고정, 마지막 턴(718, liquidate) 예외 추가 |
| 2 | daily reset 과 `recovery_days` 판정 시점이 충돌한다. hour 0 의 shortfall 은 0 이 아니다. day0 은 hour>=1 검사로 부족하다 | **타당** | tape 390 (tape,day) 전수: `T_first >= 3`, 0 인 날 없음 → hour 0 shortfall >= 3. target replay day8 h0 에서 `A=0, T_first=8` → 8. day0 첫 HIRE 는 step 1 | §C-0 재작성. `s >= first_hire_step(day)+1` 단일 조건, `A_ontime` / `shortfall_ontime` 도입, `recovery_days` 를 하루 1회 판정으로 정의 |
| 3 | 4턴 제한이 실행식에 없다 | **타당** | 이전 판 §C-3 의 네 조건에 `hire_turns_today` 가 없었고 `cap` 에도 없었다 | §C-3 조건 4 로 승격, §C-2 에 두 counter 의 증가·초기화 규칙 표로 고정, G3 에 `recovery_hire_turns = 2` 추가 |
| 4 | 계측용 metadata 때문에 무트리거 parity hash 가 깨진다. `recovery_trigger_turns` 를 metadata 로 세지 마라 | **타당** | `instrument.py:546` 은 action dict 전체를 deepcopy 해 stream 에 넣고, `:287-289` 는 `json.dumps(sort_keys=True)` 를 해싱한다 → 값이 0 이어도 키가 있으면 hash 가 달라진다 | §D-1 에 "emit 이 `PA` 와 다른 턴에만 `__exp013` 을 붙인다" 를 동결 계약으로 명시. `recovery_trigger_turns` 는 세 필드 차이로 정의. G2 에 키 0 확인 추가 |
| 5 | `route_desync_units` 는 실제 위치/소지품 정합성을 재지 않는다 | **타당** | `instrument.py:423-450` — `_TILE_OPS` 에 한해 tile signature 와 `_inv_total`(총량) 불변만 본다. 이동 실패는 `blocked_moves` 로 별도 | §D-3 에서 `hand_tile_noop_actions` 로 개명하고 측정 내용을 그대로 기술. diagnostic 유지, 기대상태 비교는 이 카드에서 정의하지 않음 |
| 6 | catch-up 중 expect 갱신, queue pop 시점, seed guard 로 취소된 작업의 처리가 미정이다 | **타당** | 이전 판은 "emit 한 이동마다 갱신" 이라 walk 이동까지 포함해 읽혔다 | §C-4 를 5단계 우선순위 규칙으로 재작성. `expect_j` 는 규칙 4 에서만 갱신, walk 중에는 `spawn_slot[j]` 고정. pop 은 emit 턴에 1회. guard 로 PASS 된 원소는 큐로 되돌리지 않음(근거 명시). 포기·해질녘 절단·상태 폐기 목록 고정 |

**검토가 짚지 않았으나 같은 종류의 미정의라 r2 에서 함께 닫은 것.**

- `s == 718` 에서 parent 는 `liquidate(view)` 를 반환하고 그 `hands` 길이는 이미 `A` 다.
  §C-4 의 route 치환이 liquidate 의 DROP 을 덮을 수 있었다 → 마지막 턴 전면 pass-through 로 고정(§C-A).
- `apply_move` 를 "경계 clamp" 라고 썼으나 엔진(`:323-331`)은 **거부**다(위치 불변). LOCKED tile 은 이동을 막지 않는다 → §C-4 에 정정.
- parent 의 base fallback 경로에서도 recovery 가 도는지 미정이었다 → 돈다(§C-A). `layer_raise` 와 `recovery_raise` 를 분리(이전 판은 한 counter 로 묶여 G1 이 두 사건을 구분하지 못했다).
- C-1 이 `shortfall` 과 묶여 있었으나, second-wave 고용 실패만으로도 길이 불일치가 생긴다 → C-1 은 **길이만** 보도록 분리.
- 씨앗이 farmer·base hand 요청만으로 이미 모자란 경우 guard 가 종료하지 못할 수 있었다 → `break` 규칙과 되돌리지 않음을 명시.

**독립 검토(서브에이전트, 문서 전용)에서 추가로 닫은 것.**

1. §C-0 의 "second wave 는 recovery 대상이 아니다" 가 §C-4 의 "index `j >= A_ontime` 인 hand 를 전부 통제" 와
   충돌해 보였다 → "**추가 HIRE 트리거 대상이 아님**" 으로 범위를 좁히고, recovery day 의 second-wave hand 가
   통제 대상이 되는 이유(spawn 시각·칸이 tape 전제와 다름)를 §C-0 에 명시했다.
2. §C-2 의 "window 밖에서는 새 route 를 시작하지 않는다" 가 hour 11 고용 → hour 12 첫 관측 경계에서
   §C-4 와 반대 지시를 줬다 → window 는 §C-3 에만 걸린다고 고치고, 그 경계에서 route 를 만든다고 명시했다.
3. yaml `one_change` 의 "4개 하위 규칙" → C-A·C-0 을 포함한 6개로 갱신(둘 다 깨지면 parity·판정이 무너진다).
4. yaml `fixed` 의 second-wave 절 참조 `§C-2` → `§C-0` 으로 정정.
5. `recovery_hands_created` 의 증가 시점이 어디에도 없었다 → §C-4 에 "통제 대상으로 처음 판정되는 턴에 1" 로 고정.
6. `§E-1 / §E-2 / §E-3` 참조가 §E 의 실제 소제목(G0~G6)과 대응하지 않았다 → 전부 `§E G<N>` 로 정규화.

**반박·한정 (검토서 [INFERENCE] 항목).**

- **J-6. "유일하게 정합적" 은 과한 표현이라는 지적 — 수용한다.** 빈 inventory 는 full route 지연 재생의
  출발 조건이 맞을 뿐 성공 보장이 아니다. 늦은 PICKUP 시점에 shed 가 비어 있을 수 있다.
  §C-4 를 "출발 조건과 일치하는 방식" 으로 고치고 잔여 위험을 §H BLK-9 에 적었다.
  다만 skip-forward 를 배제하는 근거는 그대로다 — 그쪽은 출발 조건 자체가 어긋난다.
- **J-7. reserve 0 이 유일한 허용안은 아니라는 지적 — 수용한다.** §C-3 의 문장을
  "원천적 규약 위반" 이 아니라 "이 카드에서 택한 설계 선택" 으로 한정했다.
  다만 reserve 를 두려면 결과를 보기 전에 값을 골라야 하고 엔진에서 유도되는 값이 없으므로
  자유 파라미터가 된다는 점은 유지한다. 대안 reserve 규칙은 새 HYP-ID 로만 시험한다.
- **J-8. 발화 턴 표의 근거를 tape 에서 `PA` 로 올렸다.** 지적 1 을 반영하면 조건 3 이
  clone-preempt 이후의 market 을 보게 되므로, 이전 판의 표(tape 기준)가 그대로 성립하는지 다시 확인했다.
  `private_artifacts/replays/episode-108076177-replay.json` seat 1 의 실제 action 은
  step 34 와 step 193 에서 `market == []` 이었고 두 발화 턴·요청 수·비용이 모두 그대로였다.
  step 34 는 `START = 120` 미만이라 clone-preempt 가 아예 비활성이고, step 193 에서는 활성 구간이지만
  그 턴에 주문을 붙이지 않았다. 표의 "그 앞 턴들이 탈락한 이유" 는 실측에 맞게 정정했다.
- **J-9. Coordinator 실행안은 r3 에서 반영했다.** r2 시점에는 제안 단계라 카드가 처리하지 않았다.
  r3 에서 §G 를 C0/C1 경로에 맞춰 다시 썼다. 핵심은 **P2 의 "실제 parent P1b PASS" 조건을 유지**하고
  이 카드를 그 바깥의 C1 로 두는 것이다 — r2 §G 선행 조건 **2번**이 요구했던 "P2 조건을
  EXP-011 판정 + 사람 승인으로 대체" 는 **철회**했다(r3 의 §G-2 라벨은 다른 내용이다). 실행안 §1 이 `plan/kaggriculture_deadline_plan_20260915.md:107` 에
  이미 별도 correctness repair 경로가 있음을 확인했으므로 P2 조건을 건드릴 이유가 없다.
  BOARD 정본은 r3 에서도 **변경하지 않았다.**
- **J-10. EXP-011 과의 통합 순서 지적에 동의한다.** 두 카드 모두 `tools/instrument.py` 를 바꾸므로
  구현은 순차 통합하고 각 runner SHA 를 실행 전에 동결한다. 이 문서 개정은 EXP-011 과 독립적으로 진행했고,
  §G-3 이 그 순차 통합·runner 고정·병렬 금지를 카드 조항으로 확정했다(r3).
  선행 조건은 r3 에서 네 가지로 다시 정리됐다(§G-1) — **r2 도 r3 도 실행 승인이 아니다.**
