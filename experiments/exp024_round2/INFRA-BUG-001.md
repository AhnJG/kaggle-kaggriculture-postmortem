# INFRA-BUG-001 — nested `_SEARCH_ENTRY` self-reference

- 발견: initial Screen 3,720/3,720 완료 후 판정 시각.
- 증상: 186개 variant가 O1/O2 모두 score 0.0, candidate reward 3,000, action digest empty, measured action count 0에 해당했다. Engine status만 `DONE/DONE`이어서 최초 runner의 status-only invalid check가 놓쳤다.
- 원인: EXP-023 `gen.py` wrapper를 이미 같은 `_SEARCH_ENTRY` wrapper가 붙은 v171에 다시 적용하면서 이전 `search_entry`의 global `_SEARCH_ENTRY`가 자기 자신으로 바뀌었다.
- 보존: `invalid-self-recursive/`에 최초 generator, variants manifest, 186 variant bytes, jobs, raw 3,720 rows, summary를 이동했다. 삭제하지 않았다.
- 수리: EXP-024 전용 `_EXP024_ENTRY`와 `exp024_entry` 이름을 사용한다. mutation specs, one-change 값, seed, seats, opponents, workers, gate는 변경하지 않는다.
- 계측 수리: runner에 `action_count`와 `agent_errors`를 추가하고, 719 call이 아니면 invalid로 판정한다.
- 최초 invalid raw SHA-256: `74ea30ce10af4b3180b85d5736e2c7c40ff38080d21bd2382e3581397c165671`.
- 최초 invalid summary SHA-256: `19f77da6295d1a74b2d13219ae33aa401328c122865ccbbddf6bca02e10bde84`.
