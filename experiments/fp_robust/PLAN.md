# FIRSTPRINCIPLES: approach screen and preregistration (2026-09-29)

The target is a single bot for the current 2200-2400 population. [LOCAL] is a
selection screen; hosted 2300+ remains unmeasured until a human submits.

## Six structurally different approaches, before candidate runs

| Approach | Expected gain | Failure risk | Estimated time | Decision and evidence |
|---|---|---|---|---|
| A. Robust market-order search: score our SELL/fixed-order permutations under several opponent order scenarios instead of treating the rival as our mirror | Avoid losses from diverse late departures from 55be | Rival orders are hidden; an ensemble can still be wrong and existing search is strong | 4-7 h | **Select.** Existing `_v44y_factor_margin` copies our orders into the rival schedule (`releases/exp035-d157/main.py:6089-6127`), while observed private variants have median 15 divergent steps, mostly late (`coordination/reports/claude/20260929-EXP050-051-LOSS-ANALYSIS.md:3-8`). |
| B. Observed-opponent regime classifier that switches between intact d157 and c26 policies for the rest of a game | Avoid using one policy across close-clone and other opponent regimes | Early public behavior may not predict late divergence; d157/c26 differ in only one constant | 3-5 h | **Select as independent mechanism.** Current-pop tape gives c26 +0.048 against 55be lineage but 2000-2200 −0.012 (`coordination/reports/claude/20260929-EXP050-051-LOSS-ANALYSIS.md:10-14`); candidate must select by in-game observations, never hidden labels. |
| C. Production route redesign (animal/crop mix) | Change inventory timing before the late sale race | Full horizon effects, action bottleneck and market feedback; prior low-value crop substitution failed | >15 h | Defer. `analysis/exp044_margin/FINDINGS.md:1-9`; `evidence/FACTS.md:228-232`. |
| D. Terminal physical inventory planner | Recover late cargo or improve final SELL inventory | Existing exact physical planner already entered EXP-039 but was not selected; repeated idea without new failure evidence | 6-10 h | Defer. `experiments/exp039_camargin/variants/c30.py:1022`; `experiments/exp039_camargin/judge39.py:1-15`. |
| E. Public 55be shadow next-action forecast | Preempt imminent WOOL/MILK/STRAWBERRY sales | Prediction precision 0.114; reacts to wrong events | 4-8 h | Reject for now. `coordination/reports/codex/20260928-2133-EXP047.md:4-8`. |
| F. Market-only replay graft from hosted opponents | Emulate successful market timing | K3 explicitly forbids this mechanism without an ENGINE/HOSTED reopening condition | 2-4 h | Reject. `evidence/KILLS.md:10`. |
| G. Time-dependent WHEAT/crop turnover schedule | Free action budget or supply | WHEAT cash is uncorrelated with margin in this panel, and prior WHEAT imitation failed | 8-12 h | Reject. `analysis/exp044_margin/FINDINGS.md:3-4`; FIRSTPRINCIPLES card failed-list. |
| H. Two-slot portfolio allocation | Reduce correlation of rating outcomes | This card requires one bot and forbids submission; does not raise one bot's strength | 1-2 h | Defer. `coordination/BOARD.md:8-18`, AGENTS.md §7.4. |

## Fixed evaluation, frozen before candidate results

- Sources: `experiments/exp051_curpop/meta.json`, `jobs.json`, `games.jsonl`.
  This is 269 hosted-opponent tapes; 187 d157-origin and 82 c26-origin.
- Time holdout: for **each originating submission separately**, sort by the
  original episode ID as timestamp proxy and reserve the latest `ceil(20%)`.
  The exact IDs and source SHA are in `freeze.json`. No candidate development
  uses these rows. Any new hosted replay with endTime after 2026-09-28T17:27:00Z
  and absent from EXP-051 is a forward holdout, with no post-result filtering.
- Development current-pop score = W + 0.5 D on the remaining episodes, using
  original seed and seat. The selected candidate must beat **both** c26 and
  d157 by >0.030 paired score, with 95% episode bootstrap lower bound >0 for
  both. Also require +0.050 point difference against each on the 2200-2400
  55be-labeled subset if that subset has >=20 episodes; otherwise report N/A.
- Holdout: score difference >=0 against both baselines, with no invalid game.
  The holdout does not select or tune a candidate.
- Auxiliary 2400+ tapes: point difference >=−0.010 against the stronger
  baseline on the fixed EXP-049 fresh panel (all available, excluding banned
  seeds). Closed-loop: paired scores >= stronger baseline −0.020 against
  public D, HL63, M2965, FJ1010 at seeds 6001..6008, both seats.
- Safety: all episodes DONE/DONE, 719 own calls, no agent exceptions. D3:
  15 fresh-process games, 1 worker, max per-step <0.8 s. A complete panel is
  needed for PASS; incomplete panels yield NOT_RUN/BLOCKED, not a partial PASS.
- Candidate selection: choose the passing candidate with larger development
  point gain vs max(c26,d157). If neither passes, release candidate=N/A.
- Paired bootstrap: 10,000 resamples of episode keys, Python Random(290929),
  2.5 percentile, difference against each baseline. No threshold or sample
  change after outcomes. Margin is diagnostic only.

## c26 tape/hosted gap hypothesis

The 269-tape +0.030 is a paired counterfactual on a fixed opponent action
sequence, whereas hosted c26's 82 initial games were mainly against weaker
opponents; the observed early rating therefore does not estimate the same
population. Hosted c26 score fell .93 -> .78 -> .72 as opponent median LB
rose 1496 -> 1788 -> 1901 (`coordination/reports/claude/20260929-EXP048B-C26HOSTED.md:12-17`).
Frozen tape also cannot react to a candidate's altered earlier orders. These
are hypotheses, not a proven causal explanation. The closed-loop panel tests
one part of that gap; hosted 2300+ requires later hosted observation.
