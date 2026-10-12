# 같은 상점 쌍 경기끼리 farmer+hands 행동 일치율 (Claude 2026-09-29 17:20 KST)
재현: `python3 experiments/slot2_lineage/consistency.py fritz` / `... d157` (step 150 의 unlocked_shops 앞 2개로 쌍 정의, step 1–718)

| 봇 | 경기 | 같은 쌍 비교 수 | step <144 | 144–431 | 432+ |
|---|---|---|---|---|---|
| Fritz Cremer (top2400 + fresh raw) | 86 | 43 | 0.72 | 0.06 | 0.01 |
| d157 (hosted_20260929b raw, 앞 90판) | 90 | 63 | 0.99 | 0.86 | 0.55 |

해석: d157 은 상점 쌍별 고정 일정(tape)이다. Fritz 는 step 144 이후 상태에 반응하는 정책이다 → Fritz 경기를 route 로 재생해도 Fritz 를 복제하지 못한다.
