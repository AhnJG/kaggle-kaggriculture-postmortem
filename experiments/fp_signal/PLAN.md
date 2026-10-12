# Public-state signal audit, frozen before feature extraction (2026-09-29 14:05 KST)

Question: In d157 hosted games against privately modified 55be bots, is there a repeated loss-linked condition visible in the agent's observation early enough to act?

## Cohort and boundaries

- Source: `analysis/c26_hosted_20260929/opponents.csv`, exact d157 submission 56607884 and `is_55be=True`, `is_full=False`, W/L only. The opponent's action is used only to verify that it differs from public 55be; it is never a runtime feature.
- Remove all episode IDs in `experiments/fp_robust/freeze.json:holdout_episodes`. Do not read their replays. Do not use `analysis/hosted_20260929pm` episodes that were absent from EXP-051. This preserves both existing holdouts.
- Freeze the cohort by episode ID and input SHA in `cohort.json` before extraction. No extension after outcome inspection.
- `private_artifacts/c26_hosted_20260929/raw/<episode>.json.gz` is the source for observations. Read only `steps[t][seat].observation` public keys: `farms`, `market`, `town`, `step`. Never read `private` or opponent action when constructing a signal.
- Existing `analysis/exp050_divergence/fp50.jsonl` may establish offline private-variant identity; it cannot supply a runtime feature.

## Fixed feature checks

At each of steps 240, 384, 480, 576, and 624, evaluate these binary features:

1. opponent public money > our public money;
2. opponent count of COW + SHEEP > our count;
3. opponent count of STRAWBERRY + TOMATO planted tiles > our count;
4. shared WOOL inventory > 10000;
5. shared MILK inventory > 10000;
6. shared STRAWBERRY inventory > 10000.

These values are available in `observation` and use fixed thresholds. Money lead is a state warning, not a causal mechanism. Market inventory is shared, so an association alone cannot attribute it to the opponent.

## Evidence threshold

- Split episodes by original `endTime`, first half vs second half, before computing features. This is a reproducibility check, not an untouched holdout.
- For a feature to be a **repeated observable signal**, both halves must have >=3 W and >=3 L in each feature state, the loss-rate difference must have the same sign and >=0.20 in each half, and pooled Fisher two-sided p < 0.01 (30 checks; exploratory familywise screen). Otherwise `NO_REPEATED_SIGNAL`.
- If a feature passes, inspect the earliest public-state divergence on each loss and compare wins; report `ASSOCIATION` until one action-level mechanism and a closed-loop intervention verify causality. If none passes, do not propose a candidate from this audit.
- Report cohort W/L, group count by opponent submission, missing/invalid raw rows, feature 2x2 tables, half-level differences, and exact file SHA. Never infer hosted 2300+ strength from this audit.
