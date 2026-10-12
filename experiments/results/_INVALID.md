# 무효 처리된 결과 (2026-09-07 05:55 UTC, Cowork)

아래 6건은 현재 `main.py`(sha `b0c32e1a…5ddf`, mtime 05:44:05)가 존재하기 **전**에
생성되었다. 파라미터 override 가 no-op 이던 시점의 산출물이므로 승격 판정에 쓸 수 없다.

- `v1_workers_9_vs_10.json`   (05:37)
- `v1_workers_9_vs_12.json`   (05:37)
- `v1_workers_10_vs_12.json`  (05:37)
- `v1_carrots_5_vs_8.json`    (05:40)
- `v1_carrots_5_vs_15.json`   (05:40)
- `v1_carrots_8_vs_15.json`   (05:40)

재현 실패 증거 및 재실행 절차: `coordination/reports/claude/20260907-0555-EXP001-stale-artifact.md`

유효한 결과: `v1_timing_*_rerun.json` (05:51, 초판과 수치 완전 일치 → 재현 확인).
