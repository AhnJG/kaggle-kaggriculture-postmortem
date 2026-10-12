# EXP-018 — DP 0924 single-factor loss-cause protocol

id: EXP-018
hypothesis_id: HYP-0016
test_id: TEST-DP-LOSS-CAUSE-20260925
status: PREREGISTERED — no counterfactual or panel result yet

## Authority and scope

User requested execution on 2026-09-25, after BOARD 00:40 and work-order resume 00:45. Work order `coordination/proposals/claude/20260924-DP-LOSS-CAUSE-CODEX.md`: resume, 09-25 addition, collection correction, analysis priority, Q5 correction override body. No submission/download. This card explicitly authorizes only the two ordered Q2 alternatives below and at most one Q4 candidate. They are never stacked. No parameter search or third alternative; no post-result threshold changes.

parent: releases/public-tetsutani-demand-preserving-0924-exact/main.py
parent_sha256: 178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a
engine: kaggle-environments 1.32.7
engine_sha256: bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e
entrypoint: _final_sell_block_reorder_entrypoint (last callable, not an earlier agent binding)
fixed: all parent bytes, routes, production logic except the selected scalar, _ADV_LOOK=4, final SELL-block reorder, all market quantities/order rules outside effects of selected scalar, engine, seeds, seats, opponents, sample sizes, thresholds

## Q1 evidence, not causal conclusions

`tools/dp_loss_cause.py describe` reconstructs actual unit actions and market commits from recorded pre-state and post-state using the locked engine; 319 replays, 288360 player-step cash assertions PASS. `q1_summary.json` freezes cohort membership. No new policy trial was used to choose thresholds or seeds.

Primary symptom: 8 eligible FULL-herd losses have lower DP STRAWBERRY average sale price during d19–29. Parent `main.py:3415` refreshes inherited opponent forecast every 3 turns; herd source `main.py:3411` uses 2. This difference is a hypothesis, not proved cause. Append only `_V92_P_EVERY = 2`; retain the inherited sale horizon. This is not adding another advance-sale layer, market-only tape graft, or reopening K2 two-turn leading.

Fallback symptom: 9 eligible FULL-herd losses have fewer actual total CARROT sales than their opponents. Parent `main.py:4479` has `_CA_MARGIN=-5.0`; herd `main.py:4475` has -15.0. Append only `_CA_MARGIN = -15.0` to a fresh parent, HYP-0037. Existing feed/seed checks remain. It does not introduce GOOSE, fourth land, MELON reallocation, or new routes.

Required postmortem: existing `tools/postmortem.py:build_report` applied to recorded episode 112606102 (DP seat0), output `experiments/results/dp_loss_cause_20260925/episodes/112606102.json`: divergence day9 gap -4, worst day26 gap change -389, final margin -499. Episode112786680 seat0: worst day28 -812, final -1897. These identify timing, not causal attribution. No seed inferred: original replay info.seed is checked against opponents.csv.

## Q2 — frozen screening, before Q4

A refresh (HYP-0016): 112606102, 112673766, 112739528, 112774818, 112786680, 112797220, 112819173, 112820851
candidate path: experiments/candidates/exp018_dp0924/refresh/main.py
candidate SHA-256: f3e727b175eac13b702c3de34191b2cff170e30220bcb108b1010fc782505052
one_change: _V92_P_EVERY 3 -> 2

Only if A flips fewer than 3 baseline losses into strict wins, run B carrot (HYP-0037): 112606102, 112673766, 112689600, 112711443, 112739129, 112739528, 112774818, 112797220, 112820851
candidate path: experiments/candidates/exp018_dp0924/carrot/main.py
candidate SHA-256: 10126ec79499929cff8427de467585f477d19e85e4e5c58cd25012f58a128c0c
one_change: _CA_MARGIN -5.0 -> -15.0

Use each listed hosted seed and original DP seat, exact FULL opponent file, standard 720-state game. Fresh module globals per file/seat/game. Run parent first and verify 1438 actions + 1440 projected states vs original replay, then candidate. Reproduction mismatch is BLOCKED, not a performance failure; no replacement or omitted game. If both yield <3 wins, report PATCH_NONE and skip Q3/Q4 per work order. Draw is not a flipped win. No tuning iterations beyond these initial two alternatives.

## Q4 — fixed hosted reproduction panel

Manifest has all 59 FULL rows (29L/30W). The explicit higher-priority exclusion removes submission56502662 from judgment: 12 rows (5L/7W), retained in inventory with eligible=false. Eligible judgment sample = 47 rows (24L/23W), all listed in frozen input_audit.json/full_panel. No invented replacement to restore59. Original seeds, original DP seats, exact opponent paths and raw SHA hashes are frozen in freeze.json before running. No additions/removals based on outcomes. Q2 episodes remain in Q4; therefore this is a development/reused panel, not independent holdout.

For the selected single candidate: parent then candidate on every eligible episode. Q2 results can be reused only with the identical frozen file/runner/config/seed/seat/opponent hashes and matching parent identity. Original hosted actions, not fingerprint labels alone, must match both parent and opponent. Engine or identity mismatch => BLOCKED; do not reinterpret as defeat.

Score per episode = 1/0.5/0 for win/draw/loss. Let d_i = candidate score - parent score. Primary panel delta = mean(d_i), paired SE = sample_stdev(d_i, ddof=1)/sqrt(47). No weights on this primary panel statistic. Report parent/candidate W/D/L, delta, SE, 2SE, flipped losses and new losses on hosted-win baseline. Unique seeds checked before execution; any duplicate/dependency requiring a different denominator => BLOCKED rather than changing SE after results.

### 사전 판정 — 지시서 그대로

- SUCCESS: 패널 점수율(후보 − 부모) > **2 × paired SE** 이고, 승리 기준선 경기에서 새로 지는 경기 ≤ 뒤집힌 패배 수의 1/3, 예외 0, 최대 step < 0.5초.
- INCONCLUSIVE: 차 > 0 이지만 2 × SE 이하.
- FAILURE: 차 ≤ 0, 또는 예외·시간 초과.

If the original cases do not define a unique verdict (e.g. delta>2SE but regression condition fails), return BLOCKED_VERDICT_GAP to Coordinator. Never invent a new failure threshold. Retain raw panel classification separately from eligibility.

### 09-25 필수 DP 하한

Candidate vs exact parent DP0924, seeds 2400–2439 inclusive, BOTH seats = 80 games. Score rate (W+0.5D)/80 **>=0.50**. Below 0.50 => SUCCESS and B-2 eligibility prohibited regardless of panel. Exactly0.50 passes the floor. This is a point-score floor, not a confidence-interval lower bound. Also report 40 seed-paired mean scores and SE. The body optional20-game comparison is superseded by this mandatory80-game defensive comparison; no extra seeds2300–2309 trial is required for this path.

Step max must be strictly <0.5 seconds including the first call. Record both players, judge selected candidate exceptions/status and inherited caught-error telemetry, max/p99 and episode total. Run serially, no competing benchmark. Runtime failure is not excused as noise or rerun into PASS.

INCONCLUSIVE is not automatic B-2 acceptance: every B-2/E-2 condition must be evidenced. Missing EXP-017 comparisons or weights/UNKNOWN coverage => B-2 N/A, no recommendation. No existing result is promoted to hosted strength.

## Reweighting and DP share scenarios (report only)

Each sampled victory weight = header submission wins / downloaded submission wins; loss weight=1. Use only eligible rows for closed-loop performance. The 19 header draws lack replays: do not silently call non-draw reweighting a full884-game estimate. Report non-draw conditional estimates and uncovered draw mass. Unidentified/unmeasured families have effect N/A; zero-effect contribution may be shown only as an explicitly assumed sensitivity calculation, with coverage. Weight source input_audit.json.

DP-prefix family = label contains DP-0924-exact and prefix_len>=143 (not UNKNOWN mentioning DP among many files). Report current reweighted non-draw DP share for the eligible collection as well as the eligible FULL panel. For current(panel estimate),20%,40% mixture, remove DP-family panel rows from non-DP weighted mean to avoid double counting. Parent mirror score baseline0.50 by symmetry; candidate DP score from fixed80 games. E_parent(p)=(1-p)*weighted_nonDP_parent+p*0.50; E_candidate(p)=(1-p)*weighted_nonDP_candidate+p*DP_score; delta=E_candidate-E_parent. These conditional scenarios do not predict full-field BT and never change verdict.

## Release and identity

Only a recommended candidate receives a release tar: one root main.py, exact same measured bytes, preserve parent prefix, tar member hash==extracted main.py hash, last callable, no external files/network/environment dependency, exceptions0,maxstep<0.5. Record fixed card SHA and runner SHA before any Q2/Q4 game in `experiments/results/dp_loss_cause_20260925/freeze.json`; record pre-run UTC time and complete list of source/raw/engine/opponent hashes. Never overwrite the card/freeze/results. Output report and hypothesis events, strict ledger validation. No submission; FIFO target is EXP-01756490029, DP56518910 retained.
