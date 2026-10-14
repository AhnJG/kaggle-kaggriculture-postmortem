# coordination/reports/codex — 80개 문서 묶음

원본 파일을 파일명(시간) 순으로 이어 붙였다. 각 절 제목이 원래 경로다.


---

## `reports/codex/20260908-1656-KAGRI-012.md`

# KAGRI-012 — EXP-001 stage 2·3 재실행

## VERDICT

**SUCCESS** — stale 결과 6건을 보존 이동했고, 고정된 20 seeds(`1000..1019`) × 양 좌석으로 stage 2·3을 재실행했다. 동결된 v1은 correctness gate를 통과했다. 이 판정은 태스크 완료 및 `[LOCAL]` 동작 검증이며 promotion 또는 `[HOSTED]` 우위 판정이 아니다.

## 핵심 사실

1. `[LOCAL]` stage 2 round-robin paired score 합은 hands 9 = **2.00**, hands 10 = **1.00**, hands 12 = **0.00**이다. 세 비교 모두 40/0/0, errors=0으로 **hands=9**를 선택했다.
2. `[LOCAL]` stage 3 round-robin paired score 합은 carrots 5 = **0.20**, carrots 8 = **1.35**, carrots 15 = **1.45**이다. **carrots=15**를 선택했다. 최종 v1 설정은 land `(day 6, day 10)`, hands `9`, carrots `15`다.

## exact path + SHA-256

- `main.py`: `50efced8f7cee746957c648c097c0c4f6454649facd03f71e7e57c3afa7aef5e`
- `tools/arena.py`: `a226e633d438c6684a36f9ea29e2013775041c151cea02d49e3a1bc37bed1201`
- `experiments/results/v1_workers_9_vs_10.json`: `2c58d3c4c6622ac22f32cecdb5cf9c39970178971025486079e5213477614157`
- `experiments/results/v1_workers_9_vs_12.json`: `653336774cb666c2e22e5c6d079d5be9a4a5951f4a6b5cbd7ab807ca7cc66470`
- `experiments/results/v1_workers_10_vs_12.json`: `a55638601c6771d0786e53ba9c480af2b2be7b1ed108bd632c0f94f09a2f8081`
- `experiments/results/v1_carrots_5_vs_8.json`: `be6e3767f9d75e1d9529758abf71bbcc569b5d41b422f2c66d69d141ae288651`
- `experiments/results/v1_carrots_5_vs_15.json`: `f9e9d1794bb7dac06c22d777fb5cad3336a6f751cb3da1d0f1f6f4f17de62a61`
- `experiments/results/v1_carrots_8_vs_15.json`: `d1a2806cbcdf6108d967a2fccba480e442aab3890eed5f15f72f8d58ebaac567`
- `experiments/results/v1_gate_instrument.json`: `df93a94393f5efdea71e742b8ff275b23ca26e1c9830226f3c2e56b92759dd13`
- `experiments/results/v1_gate_selfplay.json`: `4527d992b833939acd3b3bcd87430316b807ea1045244faa8e3d2c4db0f45e21`

stale 6건은 삭제하지 않고 `experiments/results/_invalid/` 아래 같은 basename으로 이동했다. `_INVALID.md`는 수정하지 않았다.

## 재현 명령과 실행 결과

환경 gate:

```bash
python3 -c "import kaggle_environments; print(kaggle_environments.__version__)"
shasum -a 256 /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py
```

- `[LOCAL]` version `1.32.7`
- `[ENGINE]` SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` 일치

stage 2·3의 각 비교는 다음 형식으로 정확히 20 seeds, 40 games를 실행했다.

```bash
python3 tools/arena.py --a <wrapper-A> --b <wrapper-B> --seeds 20 --seed-start 1000 --json <result>
```

- `[LOCAL]` workers 9 vs 10: paired 1.000, W/D/L 40/0/0, mean margin +1,263, errors 0
- `[LOCAL]` workers 9 vs 12: paired 1.000, W/D/L 40/0/0, mean margin +6,879, errors 0
- `[LOCAL]` workers 10 vs 12: paired 1.000, W/D/L 40/0/0, mean margin +5,644, errors 0
- `[LOCAL]` carrots 5 vs 8: paired 0.000, W/D/L 0/0/40, mean margin -570, errors 0
- `[LOCAL]` carrots 5 vs 15: paired 0.200, W/D/L 8/0/32, mean margin -1,257, errors 0
- `[LOCAL]` carrots 8 vs 15: paired 0.350, W/D/L 14/0/26, mean margin -715, errors 0

correctness gate:

```bash
python3 tools/instrument.py --a main.py --b starter --seeds 7 11 13 1000 1001 1002 1003 1004 1005 1006 1007 1008 1009 --time-agent a --json experiments/results/v1_gate_instrument.json
python3 tools/instrument.py --a main.py --b main.py --seeds 7 11 13 --json experiments/results/v1_gate_selfplay.json
python3 -m py_compile main.py tools/arena.py
```

- `[LOCAL]` 13/13 runs에서 P0 `noop_actions`, `blocked_moves`, `shed_discarded`, `orders_truncated`, `sell_unfilled`, `buy_failed`, `exceptions` 모두 0. p99는 seed별 최대 0.38ms.
- `[LOCAL]` self-play 3/3 runs에서 양쪽 CLEAN, 동일 reward. compile PASS.

## arena.py 변경 diff 요약

- JSON에 `parent_sha256`, `agent_a_sha256`, `agent_b_sha256`, `engine_sha256`을 추가했다.
- 실행 전후 네 SHA를 비교해 하나라도 바뀌면 결과를 저장하지 않고 종료한다.
- builtin agent처럼 file path가 없는 경우 agent SHA는 `null`이며, 이번 6개 wrapper 비교에는 모두 exact SHA가 기록됐다.

## NEXT ACTION

KAGRI-015를 사전등록한 뒤, 이 v1을 parent로 작물 전환 schedule을 한 축씩 평가한다. KAGRI-012 결과만으로 v1을 제출하지 않는다.

## 리스크

- `[LOCAL]` v1 correctness gate는 promotion gate가 아니다. `AGENTS.md §7.1`의 4-bot 결과와 `[HOSTED]` 증거는 아직 없다.
- carrots 8 vs 15의 개별 CI는 0.5를 포함하지만, 사전등록된 선택 규칙은 세 후보 round-robin paired score 합이며 15가 1.45로 최댓값이다.


---

## `reports/codex/20260909-0156-KAGRI-015.md`

# KAGRI-015 — EXP-002 crop transition

## VERDICT

**FAILURE** — 모든 candidate가 correctness gate는 통과했지만, selected crop schedule은 `[LOCAL]` 공개 상위 봇 4종 상대 0/0/400, aggregate paired score 0.000, 95% CI `[0.000, 0.000]`으로 promotion gate를 실패했다. v1을 유지하며 제출하지 않는다.

## 핵심 사실

1. `[LOCAL]` fixed pilot은 MELON 30칸 → switch day 2 → NE unlock h1 → STRAWBERRY 30칸을 차례로 선택했다. selected 구성은 MELON 30 / STRAWBERRY 30 / WHEAT 15이며 모든 pilot wrapper의 양 좌석 silent-failure counters는 0, daily min cash는 0 이상이었다.
2. `[LOCAL]` selected candidate는 v1 direct diagnostic에서 100/0/0, paired score 1.000이었지만 공개 4봇에는 각각 0/0/100, 합계 0/0/400이었다. v1 parent도 4봇에 0/0/400이었다. direct win과 평균 패배 margin 축소는 promotion 또는 `[HOSTED]` 우위 근거가 아니다.

## exact path + SHA-256

- `experiments/cards/EXP-002-crops.md`: `86f915a71a94c6e8b3b8936ea2da3d99018f97d4e2e0da1f6647e706b5f2c649`
- `main.py` (v1 default + disabled crop pilot hooks): `d6cdb83ffdb27d2614330b20d438a6a20e82c7f4a72ead5ca8be897859de0b59`
- `tools/arena.py`: `b3138a7279edde375c0bd66eb17d780d2b9c25eab20d894a41223d36b138f7d1`
- `tools/instrument.py`: `67c7014d620c9a99145348432553e77ddc5757b616ba1ade4f90ea9e218f53f8`
- `experiments/candidates/v2c_c3_strawberry30.py`: `adf8e798a11ec461f2d9c95aa0ed34927ebf0c122684ec94852b30f8ded37855`
- `experiments/results/v2c_summary.json`: `3490bd3d02553c56f21f6cde11ba3372ef0c52bff6ddf779d6833facdd008bae`
- `experiments/results/v2c_parent_postchange_gate.json`: `3e2f6036c7e2cb31041b61c9a4019005eb71a4dbb8f0536fe89063aa7fb3eab8`

stage D raw results:

- candidate vs boatlee: `experiments/results/v2c_c3_vs_boatlee.json`, `2ad9b2c6521ad2a0b9673d038a7fdc0967283b3b6e5251577ea1e8ceadca606a`
- candidate vs kaitofukami: `experiments/results/v2c_c3_vs_kaitofukami.json`, `71dc411bd696ce1e54bc35ad1df99fe3edbaa2368abbb8d01eaa1516581b8975`
- candidate vs raykkretzschmar: `experiments/results/v2c_c3_vs_raykkretzschmar.json`, `93b38862c935ffa105b55c323dbccf6efad097cb05f98638d8babb3ad5beb82e`
- candidate vs lynnsakurai: `experiments/results/v2c_c3_vs_lynnsakurai.json`, `8c42960d8e3cacf31a639c43514e42eb9537e90337d828c347619da642ba9501`
- parent vs boatlee: `experiments/results/v2c_parent_vs_boatlee.json`, `28ea351e4223eb4c840a89f8d068787b511612336ea3b89be71c8cdad21b0643`
- parent vs kaitofukami: `experiments/results/v2c_parent_vs_kaitofukami.json`, `ae29a2b9de6f9c9984629611ca3be017d33b3719cf3e5f11aeb24d50727ebc40`
- parent vs raykkretzschmar: `experiments/results/v2c_parent_vs_raykkretzschmar.json`, `0935848f6484f359dba7b74bfc124cdb20a2894d1b84091d9ad524d09b1eab7f`
- parent vs lynnsakurai: `experiments/results/v2c_parent_vs_lynnsakurai.json`, `e7c76b9cac4cf88ad3b4d2844c084f27de7b278199ebb71f40eb6e037556284f`
- candidate vs parent diagnostic: `experiments/results/v2c_c3_vs_parent_diagnostic.json`, `f05238b72c20f08985770a1cb59a93bbc01fee023240cd83008323f884a37c5f`

## 재현 명령과 실행 결과

사전등록 근거:

- `[LOCAL]` `evidence/POSTMORTEM_4bots.md:46-62`: 4개 봇 전원이 STRAWBERRY/MELON을 팔고 v1은 0.
- `[ENGINE]` `evidence/POSTMORTEM_4bots.md:68-77`: crop/market parameter와 N=20 실현 단가.
- `[INFERENCE]` `evidence/POSTMORTEM_4bots.md:79-89`: 수익 잠재력과 자본 ramp 가설.
- `[LOCAL]` `evidence/POSTMORTEM_4bots.md:91-100`: NE h1 vs h17 차이.

각 variant hard gate:

```bash
python3 tools/instrument.py --a <variant.py> --b <variant.py> \
  --seeds 1000 1001 ... 1019 --json experiments/results/<variant>_gate.json
```

- `[LOCAL]` 11개 variant 전부 20 seeds, 양 player CLEAN.
- `noop_actions`, `blocked_moves`, `shed_discarded`, `orders_truncated`, `sell_unfilled`, `buy_failed`, `exceptions` 전부 0.
- 전체 daily min cash 최저 0.0; 음수 없음.

pilot comparison:

```bash
python3 tools/arena.py --a <A.py> --b <B.py> --seeds 20 --seed-start 1000 --json <result.json>
```

- `[LOCAL]` stage A score 합: melon15 1.00 / melon30 2.00 / melon45 0.00 → melon30.
- `[LOCAL]` stage B-day score 합: day2 2.00 / day4 1.00 / day8 0.00 → day2.
- `[LOCAL]` stage B-hour: h1 vs h17 = 40/0/0, paired 1.000 → h1.
- `[LOCAL]` seed 1000 BUY_LAND trace: h1 variant steps `[145,266]`, h17 variant `[161,290]`. NE delay가 cash path를 바꿔 SW도 24 steps 늦어졌다.
- `[LOCAL]` stage C score 합: strawberry0 0.35 / strawberry15 0.70 / strawberry30 1.95 → strawberry30.

stage D:

```bash
python3 tools/arena.py --a <candidate-or-parent.py> --b opponents/public/<bot>.py \
  --seeds 50 --seed-start 1000 --json <result.json>
python3 tools/arena.py --a experiments/candidates/v2c_c3_strawberry30.py \
  --b experiments/candidates/v2c_parent.py --seeds 50 --seed-start 1000 \
  --json experiments/results/v2c_c3_vs_parent_diagnostic.json
```

- `[LOCAL]` candidate vs 4 bots: 0/0/400, paired 0.000, CI `[0,0]`, mean margin -105,573, errors 0.
- `[LOCAL]` parent vs 4 bots: 0/0/400, paired 0.000, CI `[0,0]`, mean margin -121,611, errors 0.
- `[LOCAL]` candidate vs parent: 100/0/0, paired 1.000, CI `[1,1]`, mean margin +29,681, errors 0. 진단 전용.

final code checks:

```bash
python3 -m py_compile main.py tools/arena.py tools/instrument.py experiments/candidates/v2c_*.py
python3 tools/instrument.py --a main.py --b main.py --seeds 7 11 13 --json experiments/results/v2c_parent_postchange_gate.json
git diff --check -- coordination/TASKS.md evidence/HYPOTHESES.md main.py tools/arena.py tools/instrument.py experiments
```

- compile PASS; owned-path diff check PASS.
- `[LOCAL]` v1 default self-play는 3/3 CLEAN이고 rewards `[18872,18320,18601]`로 KAGRI-012 동결값과 일치한다.
- 전체 worktree `git diff --check`는 Gemini 소유 `docs/discussion/737885_*.md`의 기존 trailing whitespace 때문에 실패했으며 이 태스크에서는 수정하지 않았다.

## NEXT ACTION

**KAGRI-013 시작 전 coordinator 결정이 필요하다.** `BRIEF_exp002_animals.md:8`은 parent를 KAGRI-015 winner로 지정하지만, `:66`, `:96`, `:131-132`, `:151-155`는 v1 parent/실패 시 v1 유지/신규 crop 금지를 요구한다. KAGRI-015가 promotion FAILURE이므로 crop pilot winner를 parent로 쓰는 것과 v1을 parent로 쓰는 것은 서로 다른 실험이다.

## 리스크

- 이번 failure는 `MELON30/STRAWBERRY30/day2/h1` 구현의 failure plane이다. premium crop 전략 전체를 영구 KILL로 해석하지 않는다.
- candidate와 parent 모두 4-bot W/D/L이 0이어서 margin 개선 16,037은 rating 개선으로 번역되지 않았다.
- KAGRI-013 parent를 추측해 고르면 single-factor attribution이 깨지고 사전등록 전체가 무효가 될 수 있어 여기서 멈춘다.


---

## `reports/codex/20260909-1718-KAGRI-016.md`

# KAGRI-016 — EXP-003 absorption alignment preflight

## VERDICT

**BLOCKED** — 전략 코드는 수정하지 않았고 실험도 시작하지 않았다. 사전등록 전에 Stage B의 exact per-sale cap이 정의되지 않았고, Stage C의 `C1 현재`와 `C2 SELL 우선, HIRE는 남는 슬롯`이 현재 parent 구현에서 동일하다는 모순을 확인했다. 추측으로 후보를 만들면 `AGENTS.md` §5의 one-factor 및 실행 전 기준 고정 계약을 위반한다.

## 핵심 사실

1. `[LOCAL]` interpreter는 Python 3.13.14, `kaggle-environments==1.32.7`이며 설치된 `kaggriculture.py` SHA-256은 요구값 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`와 일치했다.
2. `[LOCAL]` parent seed 1000 단일 좌석 trace에서 SELL 발행은 24턴이었고 hour 분포는 h1 23턴, h22 1턴이었다. 그러나 `main.py`는 이미 SELL을 먼저 만들고 그 뒤 BUY_LAND와 HIRE를 추가한 다음 10-slot clamp를 적용한다(`main.py:408-447`, `main.py:665-672`). 실제 10-slot action에서도 SELL이 HIRE보다 앞섰다. 따라서 brief의 Stage C C1과 C2는 현재 정의대로는 구분되지 않는다.

## exact path + SHA-256

- parent `experiments/candidates/v2c_c3_strawberry30.py`: `adf8e798a11ec461f2d9c95aa0ed34927ebf0c122684ec94852b30f8ded37855`
- parent가 고정하는 `main.py`: `d6cdb83ffdb27d2614330b20d438a6a20e82c7f4a72ead5ca8be897859de0b59`
- runner `tools/arena.py`: `b3138a7279edde375c0bd66eb17d780d2b9c25eab20d894a41223d36b138f7d1`
- instrument `tools/instrument.py`: `67c7014d620c9a99145348432553e77ddc5757b616ba1ade4f90ea9e218f53f8`

## 실행한 검증과 결과

```bash
python3 -c "import sys, kaggle_environments; print(sys.executable); print(sys.version); print(kaggle_environments.__version__)"
python3 -c "import hashlib, os; from kaggle_environments.envs.kaggriculture import kaggriculture as K; p=os.path.join(os.path.dirname(K.__file__),'kaggriculture.py'); print(hashlib.sha256(open(p,'rb').read()).hexdigest())"
git status --short --branch
shasum -a 256 experiments/candidates/v2c_c3_strawberry30.py main.py tools/arena.py tools/instrument.py
```

- `[LOCAL]` environment gate PASS; worktree는 시작 시 clean이었다.

```bash
python3 - <<'PY'
from collections import Counter
from kaggle_environments import make
e = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': 1000})
e.run(['experiments/candidates/v2c_c3_strawberry30.py', 'starter'])
# player 0 action에서 SELL 발행 step/hour와 market len>=10을 집계
PY
```

- `[LOCAL]` SELL 발행 24턴; hour 분포 `{1: 23, 22: 1}`; 10-slot 포화 21턴.
- `[LOCAL]` 첫 SELL+10-slot action은 `[['SELL', 'CARROT', 3], ['HIRE'], ...]`로 SELL이 HIRE 앞이었다.
- 전략 후보, result JSON, release, Kaggle submission은 만들지 않았다.

## 모호한 결정

1. Stage B의 “1회 매도 수량 상한은 흡수량/일 근처”를 exact item별 정수와 반올림 규칙으로 고정해야 한다. 예를 들어 STRAWBERRY 324/30은 10.8이지만 10/11/ceil 중 어느 기준인지 명시되지 않았다.
2. Stage C는 서로 다른 정책 세 개로 다시 정의해야 한다. 현재 구현은 이미 SELL-first이므로 C1과 C2가 동일하다. 예를 들어 C1을 HIRE-first baseline으로 바꾸는 것은 “현재”가 아니며 Codex가 임의로 해석할 수 없다.
3. 선행 correction gate의 4-bot 평균 bank를 몇 seed로 판단할지 명시되지 않았다. 기존 parent 결과와 같은 `1000..1049`를 재사용할지, pilot `1000..1019`를 사용할지 사전 고정이 필요하다.

## NEXT ACTION

코디네이터가 위 세 정의를 brief에 exact 값으로 고정한 뒤 같은 parent SHA에서 재개한다. 재개 순서는 선행 MELON 30→3 correction → CLEAN 및 matched-seed 4-bot mean-bank gate → immutable `v2a_parent.py` freeze → Stage A–D이며, 결과 확인 후 seed·기준은 바꾸지 않는다.


---

## `reports/codex/20260909-1951-KAGRI-016.md`

# KAGRI-016 — EXP-003 absorption correction gate

## VERDICT

**FAILURE** — `[LOCAL]` MELON 30→3 correction은 correctness counters를 통과했지만, 공개 4봇 matched window에서 우리 평균 final bank가 source parent보다 98.005 낮아 선행 gate를 실패했다. `v2a_parent.py`는 다음-stage parent로 동결하지 않으며 Stage A–D는 실행하지 않았다. Kaggle submission도 하지 않았다.

## 핵심 사실

1. `[LOCAL]` `1000..1049` × both seats × 4봇에서 correction과 source parent 모두 W/D/L 0/0/400이었다. correction 평균 bank 29,212.665, source parent 29,310.670, delta −98.005였다. 재현은 아래 arena 8개 명령과 `experiments/results/v2a_correction_summary.json`이다.
2. `[LOCAL]` correction self-play 50 seeds, 100 player-runs에서 기존 7개 correctness counter 합은 전부 0, daily min cash 최저 0.0, shed peak 65였다. 실행 중 새 정본에 추가된 `harvest_blocked_by_shed`는 이 gate 당시 계측되지 않아 `N/A`다. 그러나 bank gate가 독립적으로 실패했으므로 correction FAILURE와 Stage A 중단 판정은 바뀌지 않는다.

상대별 `[LOCAL]` correction / parent / delta:

| 상대 | correction | parent | delta |
|---|---:|---:|---:|
| boatlee | 28,941.84 | 30,738.43 | −1,796.59 |
| kaitofukami | 28,589.28 | 31,821.95 | −3,232.67 |
| raykkretzschmar | 28,142.13 | 26,020.68 | +2,121.45 |
| lynnsakurai | 31,177.41 | 28,661.62 | +2,515.79 |

## exact path + SHA-256

- source parent `experiments/candidates/v2c_c3_strawberry30.py`: `adf8e798a11ec461f2d9c95aa0ed34927ebf0c122684ec94852b30f8ded37855`
- failed correction `experiments/candidates/v2a_parent.py`: `753ef229d3a7b65c6068da6b132b4189bc37b3a0e543617aa66b3e0cb3120e02`
- immutable helper `experiments/candidates/exp003_policy.py`: `ea02c5ecfe66def23dc0f40303286e2e70bfd594e7047d9bfedb81e9e76c8665`
- experiment card `experiments/cards/EXP-003-absorption.md`: 결과 반영 전 SHA `1d9607bf8237251cfb6d9bdfb3404a4eb511adec3fd968efad5dbd42c12b2153`; FAILURE 상태 반영 후 SHA `cec506fb9974cbe6e40a50fad470d930bd0276bab99ef979b5f24811f2273944`
- runner `tools/arena.py`: `e6da4580d72169f656329c62f1827fbf3796678b08beab60c4c9befa3422f936`
- instrument `tools/instrument.py`: `e7d93c77d386889215deee3c5287e43efbf26634e43d90985ce7c87a9e732a6f`
- instrument result `experiments/results/v2a_parent_gate.json`: `c6de1deefb4da6e824c0477b7aad4d543c17d84faa476e27b6b77f442c4306c1`
- aggregate summary `experiments/results/v2a_correction_summary.json`: `4c37bdcaab157583db836b941bdc9441d9e09938a0d9b56f147ac21bb579bf3c`

raw arena SHA는 다음과 같다.

| policy | boatlee | kaitofukami | raykkretzschmar | lynnsakurai |
|---|---|---|---|---|
| correction | `1eba550043fa62fcc704f90f2e7c9d754b0013695b0e5203f26f89b5fcdeb51b` | `ff7e85518052ce6c62a02c7c8056ff49e5c553ed163850fb4ea52e625d7de59f` | `7a401db7fb4cee6fbecaa31ca93dd07db27cfefdc3b9d1156f2f7b2610c5a12f` | `b86d02f9969c9fe94744066ddc6fdef2cf2924ae4f011ad86922f4877df0bfac` |
| source parent | `a1e9e742912f4f4eeec7e523468064cc21e5799b3a08d9bd86528cfe3d66ddb8` | `61e59117b4aa1e39a0c8b3a6412f0c9dce496e17a8b7ce357afdaa8170d75fba` | `3495362e6d3a93a19a6543f5f527560bc89b928b76c33f5eb814ab546a0759b6` | `ad117c67d092022473d4dda145a9e517ca414517dc0fd0f58162b084aeaf684e` |

## 실행한 검증과 결과

```bash
python3 -m py_compile tools/arena.py tools/instrument.py \
  experiments/candidates/exp003_policy.py experiments/candidates/v2a_*.py
python3 tools/postmortem.py \
  --a experiments/candidates/v2c_c3_strawberry30.py \
  --b opponents/public/boatlee.py --seed 1000
python3 tools/instrument.py \
  --a experiments/candidates/v2a_parent.py \
  --b experiments/candidates/v2a_parent.py \
  --seeds 1000 ... 1049 --json experiments/results/v2a_parent_gate.json
python3 tools/arena.py --a <correction-or-parent> \
  --b opponents/public/<bot>.py --seeds 50 --seed-start 1000 --json <result.json>
```

- compile PASS.
- `[LOCAL]` postmortem: source parent 42,050 대 boatlee 121,116; 분기일 day 1, 최악의 gap 악화 day 20의 −10,085.
- `[LOCAL]` correction tile-count check: MELON 3 / STRAWBERRY 57 / WHEAT 15, 총 75. A wrappers도 명시 배분 75칸을 정확히 생성했지만 gate 실패로 실행하지 않았다.
- `[LOCAL]` 첫 instrument smoke는 wrapper의 root-package import 의존으로 2 steps ERROR가 나 INVALID 처리했다. path-based import로 고친 뒤 같은 seed가 720 steps CLEAN으로 완주했고, 그 뒤 predeclared 50-seed gate를 처음부터 전부 실행했다.
- `[LOCAL]` arena JSON 8개 모두 seeds `1000..1049`, games 100, errors 0, both seats, engine SHA 일치를 확인했다.
- 실행 중 다른 작업의 commit `6295665`가 in-progress 파일을 함께 commit했다. runner의 start/end candidate·parent·opponent·engine SHA 비교는 모두 통과했고 file contents는 바뀌지 않았으므로 arena 결과는 유효하다. 다만 ownership 위반은 운영 리스크다.

## 실패 범위

이번 FAILURE는 MELON 30→3, STRAWBERRY 30→57 exact correction과 `1000..1049` 공개 4봇 window에 한정한다. `[LOCAL]` matched-game median delta는 +313이고 상대별 부호도 2승 2패여서 broader absorption hypothesis를 KILL하지 않는다. `[LOCAL]` 결과는 `[HOSTED]` 우위를 증명하지 않는다.

## NEXT ACTION

source parent `v2c_c3_strawberry30.py`를 유지한다. 새 card를 만들기 전에 correction이 boatlee/kaitofukami에서는 손해이고 rayk/lynn에서는 이득인 원인을 postmortem으로 분리하며, Stage B/C 또는 동물 레이어로 건너뛰려면 coordinator가 새 parent와 one-change 범위를 다시 사전등록해야 한다.


---

## `reports/codex/20260911-0053-PUBLIC-REFERENCE-REPRO.md`

# PUBLIC-REFERENCE-REPRO — Yusuke Shop Router 0909 exact baseline

## VERDICT

**HOLD — 사람의 gate 예외 승인 필요. Kaggle submission은 아직 실행하지 않았다.**

## 핵심 사실

1. `[PUBLIC CODE]` notebook embedded `main.py`, `actions.json`, `LICENSE.txt`를 전략 수정 없이 복원했다. 독립 재빌드도 동일한 tar SHA-256을 만들었다.
2. `[LOCAL]` 9개 계측 episode는 모두 720 steps `DONE`이고 starter 상대 양 좌석 6/6 승리했지만, mandatory silent-failure gate가 no-op 44..136, shed discard 1..7, unfilled sell 83,998..116,738 units, buy failure 0..2로 실패했다.

## exact path + SHA-256

- submission: `releases/public-yhay81-shop-router-0909-exact/submission.tar.gz`
- submission SHA-256: `40d2bc3986f4ed3e927c81842d399a58bf20b07b57858355da4b75c280fd7791`
- source notebook SHA-256: `a36029e34448e823b6b11990ad06a86e255da6b629cbfb30035b542422592dd4`
- embedded `main.py`: `d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b`
- embedded `actions.json`: `17d503f2fd20d59f9c0f14024d1e74a8add8bb9b5561d4d908b45deecb5495ef`
- embedded `LICENSE.txt`: `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`

## 실행한 검증과 결과

- `python3 -m py_compile tools/build_public_reference.py`: PASS.
- `python3 tools/smoke.py --outdir ''`: engine SHA 일치, builtin 9/9 조합 720 steps `DONE`.
- independent rebuild: tar SHA exact match.
- clean-room extraction/import: PASS; 13 tapes, 각 719 actions.
- `tools/instrument.py`, seeds 7/1000/1001, self-play 및 starter 양 좌석: runtime PASS, silent-failure gate FAIL.
- latency: p99 <= 0.15 ms, max 172.39 ms.

## NEXT ACTION

Exact reproduction을 유지하려면 전략을 고칠 수 없다. 사람에게 learning-only submission으로 mandatory silent-failure gate 예외 승인을 받은 경우에만 위 exact tar를 한 번 제출한다.


---

## `reports/codex/20260911-0810-PUBLIC-THOMAS-PREFLIGHT.md`

# PUBLIC-THOMAS-PREFLIGHT

## VERDICT

`HOLD` — exact public-source release는 생성·고정했지만 mandatory silent-failure gate가 실패하여 Kaggle 제출은 실행하지 않았다.

## 핵심 사실 2개

1. `[LOCAL]` Thomas Tschinkel의 공개 notebook version 2를 2026-09-11에 다시 내려받았고 notebook SHA-256은 사전 확인값과 일치했다. notebook의 `%%writefile main.py` cell을 수정 없이 추출했으며 deterministic rebuild에서도 같은 submission SHA-256이 나왔다.
2. `[LOCAL]` self-play seeds `7, 1000, 1001`의 양 player가 모두 720 steps / `DONE`, exceptions 0, measured p99 0.01–0.04 ms였지만, player별 no-op 62–74, SELL 미체결 31–6,193, BUY 자금부족 0–3, shed discard 0–7이 발생했다. 사전 규칙대로 이후 arena와 submit을 중단했다.

## exact path + SHA-256

- Source notebook: `releases/public-thomas-replay-router-v2-exact/source.ipynb`
  - SHA-256 `7e3c99179e84dcbb79aed3d5e80b142b9c370ddbd9200c9400123c1f5368823c`
- Extracted source: `releases/public-thomas-replay-router-v2-exact/main.py`
  - SHA-256 `8241246765098c50223d897739cb32076b71a303284d2e5e1c5f0fb495bb5a97`
- Submission artifact: `releases/public-thomas-replay-router-v2-exact/submission.tar.gz`
  - SHA-256 `8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180`
- Instrumentation: `releases/public-thomas-replay-router-v2-exact/preflight-selfplay.json`

## 실행한 검증과 결과

- `python3 -m py_compile tools/build_thomas_reference.py` — PASS.
- `python3 tools/build_thomas_reference.py <notebook> <metadata> <release>` — PASS.
- 같은 source에서 `/private/tmp`로 재빌드 — PASS, tar SHA-256 exact match.
- `tar -tzvf releases/public-thomas-replay-router-v2-exact/submission.tar.gz` — PASS, root `main.py` one member.
- 빈 폴더 extract/import — PASS, `agent`, 5 schedules × 719 steps, policy length 10.
- `python3 tools/smoke.py --outdir ''` — PASS, engine SHA exact match, 9/9 builtin pairings 720 steps / `DONE`.
- `python3 tools/instrument.py --a <Thomas> --b <Thomas> --seeds 7 1000 1001 --time-agent a --json <result>` — **FAIL**, silent-failure counters non-zero. 주의: tool process exit code는 0이므로 textual gate verdict를 확인했다.
- Kaggle submit command — **NOT RUN**.

## 증거 범위

- 이 release는 공개 notebook source cell의 exact reproduction이다. 저자가 실제 제출한 tar와 동일하다는 증거는 없다.
- notebook의 95.5% claim은 `[COMMUNITY]`, 저자의 live rating은 별도 `[HOSTED]` context다. 둘 다 이 tar의 hosted 성능 증거가 아니다.
- `coordination/BOARD.md`와 `evidence/HOSTED_LEDGER.md`는 2026-09-11 현재 stale하지만 Codex write ownership 밖이다. 직접 사용자 지시는 build와 gate 통과 시 submit을 승인했으며, 새 gate failure를 override한 것으로 해석하지 않았다.

## NEXT ACTION

사람이 이 exact artifact의 알려진 silent failures를 감수하고 1회 hosted probe를 명시적으로 승인하거나, 공개 source를 수정하지 않는 원칙을 유지한 채 다른 exact public candidate로 전환한다.


---

## `reports/codex/20260911-2155-WORKSPACE-REPAIR-WP3.md`

# Workspace repair WP3 report

VERDICT | WP3 PASS; Commit A BLOCKED_OWNER_APPROVAL

## 핵심 사실 2개

1. Commit B `dbd1673` (`chore: enforce optional gate contract`)가 `tools/`와 관련 `tests/`에만 적용되었다. `--require-pass`의 종료 계약은 PASS=0, FAILURE/INCONCLUSIVE=2, INVALID=3, ENGINE/IDENTITY mismatch=4이며, JSON에는 `schema_version`, `verdict`, `gate_passed`, `reasons`, artifact/engine SHA가 들어간다.
2. 독립 Reviewer가 P0 없음/조건부 PASS를 확인했고, 실행 예외와 artifact 변경이 동시에 발생하는 `arena` 경로의 identity 재검사 누락도 보완 후 재검증했다.

## exact path + SHA-256

- Commit: `dbd1673`
- `tools/gate_contract.py` — `3a3e423b3e0afadca8860b7bd2ed2d39ba326a824c8c6a23c4491fde6171353c`
- `tools/smoke.py` — `4fa89573a8f662d412067982a3d648b78614ce2944d6778d1c3e21f38ac2262b`
- `tools/instrument.py` — `8d29ef89992a68fef958fc218f862fc1b96bdd11032812818de57f893c362cc6`
- `tools/arena.py` — `ff22be90bbae960185f63ecabcdff1c0e6f05b00bec9e40e88c579b3ff49b683`
- `tools/validate_gate.py` — `9a9e9d860cc0778938b6ddca69a8eb2f5eae8007d7d3d17b29965d1ba12d5c2b`
- `tests/test_gate_contract.py` — `59d9d685327b84226878bdae755b2e3f44a0cbde4d5e1426f88e4cedb73c0faa`
- `tests/fixtures/silent_failure_agent.py` — `f67fb1dc88d29deb814b3750580c3b013bb2940de611ee3d0486b71f10fc1a45`

## 실행한 검증과 결과

- `python3 -m unittest discover -s tests -p 'test_*.py'` → 13 tests PASS
- `python3 -m py_compile tools/gate_contract.py tools/smoke.py tools/instrument.py tools/arena.py tools/validate_gate.py tests/test_gate_contract.py tests/fixtures/*.py` → PASS
- `.venv/bin/python tools/smoke.py --outdir '' --require-pass --json /tmp/wp3-smoke-pass.json` → exit 0, verdict `PASS`
- `.venv/bin/python tools/validate_gate.py /tmp/wp3-smoke-pass.json` → exit 0, `schema PASS`
- `.venv/bin/python tools/instrument.py --a tests/fixtures/silent_failure_agent.py --b tests/fixtures/silent_failure_agent.py --seeds 7 --require-pass --json /tmp/wp3-instrument-failure.json` → exit 2, verdict `FAILURE`; truncation/sell-unfilled reason recorded
- `.venv/bin/python tools/arena.py --a pass --b starter --seeds 1 --steps 1 --require-pass --json /tmp/wp3-arena-invalid.json` → exit 3, verdict `INVALID`
- diagnostic arena with the same wrong-step input and without `--require-pass` → exit 0 (backward compatibility)
- `git diff --cached --check` and `git diff --check -- tools tests` → PASS; unrelated dirty files remain untouched

## 남은 N/A / INFERRED

- Commit A의 coordinator/Cowork 소유 파일(`coordination/CURRENT.yaml`, `BOARD.md`, `HANDOFF_CURRENT.md`, `TASKS.md`, `AGENTS.md`/`RESET`)은 수정하지 않았다. 소유권 확인과 acceptance criteria는 [`coordination/proposals/codex/CONTROL_PLANE_COMMIT_A_PROPOSAL.md`](../../proposals/codex/CONTROL_PLANE_COMMIT_A_PROPOSAL.md)에 기록되어 있다.
- Hosted 최신 상태·새 registry lineage·artifact 복구는 이 WP3 범위에서 확정하지 않았다. 새 strategy/arena/submission도 실행하지 않았다.

## NEXT ACTION

1. Coordinator/Cowork가 Commit A proposal을 검토하고 current-state 정합화 후 Commit A를 별도로 확정한다.
2. Commit A가 반영된 clean checkout에서 WP3 validator와 release workflow의 JSON/exit-code 연계를 독립 검증한다.


---

## `reports/codex/20260912-1020-HYPOTHESIS-LEDGER.md`

# Hypothesis ledger proposal and validator

VERDICT | **IMPLEMENTED_IN_CODEX_SCOPE · CANONICAL_ADOPTION_PENDING_EVIDENCE_OWNER**

## 핵심 사실 2개

1. 기존 H1~H20, EXP-001~007, 주요 공개 notebook/discussion 주장을 전역 `HYP-####` 29개로 backfill한 적용 제안본을 만들었고, 모든 항목에 비전공자용 `쉬운 설명` 한 줄을 넣었다.
2. schema·상태·증거 수준·local/hosted 결과·experiment card ID·submission ID 연결을 검사하는 validator와 tests를 구현했다. 기존 card 7개에는 아직 `hypothesis_id`가 없어 strict 실행은 의도대로 exit 3이다.

## exact path + SHA-256

- Commit `281be75`
- `coordination/proposals/codex/HYPOTHESIS_LEDGER_PROPOSED.md` — `d0dec044b3688b956f70f9e77884190ea0b7388e657819010b26e1039c33d491`
- `tools/validate_hypotheses.py` — `550cf6314500368fddcc50949b1c9ece9a56e8ac3d1b516ed221d87d973af93a`
- `tests/test_hypothesis_ledger.py` — `d78f50a83ed7f6cf5f10b040a27a2fb7df332adf084c30ba9dc5fdbd8063ed89`

## 실행한 검증과 결과

- `python3 tools/validate_hypotheses.py coordination/proposals/codex/HYPOTHESIS_LEDGER_PROPOSED.md --hosted-ledger evidence/HOSTED_LEDGER.md` → exit 0, 29 entries PASS
- `python3 -m unittest discover -s tests -p 'test_*.py'` → 20 tests PASS
- `python3 -m py_compile tools/validate_hypotheses.py tests/test_hypothesis_ledger.py` → PASS
- `python3 tools/validate_hypotheses.py coordination/proposals/codex/HYPOTHESIS_LEDGER_PROPOSED.md --cards-dir experiments/cards` → exit 3, 기존 EXP-001~007의 `hypothesis_id` 누락 7건 탐지
- `git diff --check -- <세 변경 파일>` → PASS

## NEXT ACTION

1. Claude/evidence owner가 제안본을 `evidence/HYPOTHESES.md`에 적용하고 EXP-001~007에 제안된 `hypothesis_id`를 추가한다.
2. 적용 후 ledger+cards+HOSTED_LEDGER strict validator를 작업 종료 및 release gate에 연결한다.


---

## `reports/codex/20260912-1114-HOSTED-EPISODE-COMPARE.md`

# EXP-006/007 hosted episode 비교

VERDICT | **EXP-006을 provisional incumbent로 선택; HYP-0006/0007의 causal·보완성 판정은 INCONCLUSIVE** | exact tar SHA `1c478c24…9721`, `8031d51a…0180` | COMPLETE score와 고정된 같은 시간대 50판씩 확인 | NEXT ACTION: EXP-006 패배 postmortem

## 사람이 쉽게 이해하는 결론

현재 두 선수 중에는 EXP-006이 더 강하다. 그러나 두 선수가 만난 상대가 거의 달라서 “서로 다른 상대에게 강하니 두 자리를 함께 쓰면 좋다”까지는 아직 증명되지 않았다.

## Batch card

| 항목 | EXP-006 clone-preempt | EXP-007 thomas router |
|---|---|---|
| submission / artifact | `56165718` / `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` | `56175620` / `8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180` |
| hypothesis | clone 상대 판매 선점이 clone 승리를 만들고 non-clone 결과를 보존 | 다른 replay 계열이 EXP-006의 패배를 일부 보완 |
| local gate | SUCCESS: 20-0-0 h2h, 공개봇 40-0-0, pool 악화 0 | SUCCESS: pool 0.9433, EXP-006 비승리 6셀 중 4셀 승; Reviewer 반대 병기 |
| hosted snapshot | COMPLETE, **1915.6** | COMPLETE, **1819.8** |
| 고정 표본 | 50판 **41/0/9**, point score 0.82 | 50판 **21/9/20**, point score 0.51 |
| 사전 판정 경계 | parent 같은-window Δ ≥ +50 유지, ≤ −100 폐기 | hosted 숫자 경계 없음; 슬롯 보완성 판독 예정 |
| 실제 판정 | parent 은퇴로 사전 Δ 계산 불가 → INCONCLUSIVE | 패배 상대 교집합 0이나 공통 상대도 3명뿐 → INCONCLUSIVE |

publicScore는 사용자가 제공한 2026-09-12 동일 CLI 출력이다. 정확한 조회 시각이 없으므로 submission 나이 보정이나 과거 yhay81 2188.4와의 직접 차분에는 쓰지 않는다.

## Episode 비교 방법과 결과

- 공통 관측 시작: EXP-007 활성 직후인 `2026-09-12T01:13:25Z`.
- 고정 종료: `2026-09-12T11:14:20Z`.
- EXP-006의 최신 50판을 고르고, 각 생성시각에 가장 가까운 EXP-007 episode를 중복 없이 하나씩 골랐다.
- 좌석 수는 양쪽 모두 seat0 21판, seat1 29판이었다.
- EXP-006의 패배 상대 9명과 EXP-007의 패배 상대 19명(20패, Bibek 2패)은 겹치지 않았다.
- 그러나 전체 상대 이름도 EXP-006 49명, EXP-007 48명 중 **3명만 공통**이었다. 상대가 다르면 패배 목록이 다른 것은 자연스러우므로 낮은 실패 상관의 증거로 승격하지 않는다.

결과 JSON에는 선택된 episode ID, 생성시각, 좌석, 상대, 양쪽 reward와 W/D/L을 보존했다.

```bash
python3 tools/compare_hosted_episodes.py --submission-a 56165718 --submission-b 56175620 --team Sian --after 2026-09-12T01:13:25 --as-of 2026-09-12T11:14:20 --count 50 --output experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json
```

원자료: `experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json`.

## Evidence boundary

- `[HOSTED]`: COMPLETE status, publicScore snapshot, 공개 episode의 TeamNames·rewards·생성시각.
- `[INFERENCE]`: 이 관측 표본에서는 EXP-006이 현재 더 강해 provisional incumbent로 적합하다.
- 판정 불가: clone-preempt의 parent 대비 causal effect, 두 제출의 동일 상대 failure correlation, 최종 leaderboard 수렴값.

다음 실험 카드를 쓰기 전에 EXP-006의 최근 패배 최소 1판을 `tools/postmortem.py`로 분석해야 한다. 새 변경은 그 패배 원인 하나만 겨냥해야 한다.


---

## `reports/codex/20260912-1945-HYPOTHESIS-SHARED-LEDGER.md`

# Shared hypothesis ledger implementation

VERDICT: **PASS** — 공용 원장, agent별 event channel, updater, strict validator, 기존 EXP-001~007의 HYP-ID/TEST-ID 연결을 구현했다. 전략 실험이나 Kaggle 제출은 실행하지 않았다.

## 핵심 사실

1. 루트 `HYPOTHESES.md`에 29개 가설·공개 주장·검증 결과를 통합했고 각 항목에 `쉬운 설명`을 유지했다. EXP-007 hosted 접수 `56175620`은 `PENDING_HOSTED`로 반영했다.
2. Claude와 Codex는 원장을 직접 편집하지 않는다. `tools/update_hypotheses.py`가 file lock 아래 agent별 immutable JSON event를 먼저 기록하고 원장을 atomic replace한다. 같은 가설은 같은 HYP-ID, 독립 검증은 별도 TEST-ID를 쓴다.
3. `AGENTS.md`는 관련 작업 전 원장 조회, 작업 후 event 기록, 종료 전 strict gate를 요구한다. 기존 카드 EXP-001~007에는 `HYP-0001..0007`과 `TEST-0001..0007`을 연결했다.

EXP-005~007은 작업 시작 전부터 Claude 소유의 untracked 파일이었다. 두 ID 줄은 현재 working tree에 반영했지만 기존 본문 전체를 Codex commit에 섞지 않기 위해 staging하지 않았다. Claude가 해당 카드를 commit할 때 이 줄을 함께 포함해야 한다.

## 주요 artifact SHA-256

- `HYPOTHESES.md`: `6f87fb736fa6bb20d406f9a04717a4cf8dd7922ef8ded4c52f1d0f2fb478a769`
- `AGENTS.md`: `3a6e6ca9de542ab431389b82990316c1105145b45fdd9c7b8ee9320b52755c70`
- `tools/update_hypotheses.py`: `5d04b76c1d8160f6f96a1b5bf51e5d63d51f87f22dd49c627275c891b13ec5aa`
- `tools/validate_hypotheses.py`: `d087f4cca121421edc398227d27ec78e1381af0de910fa2ea44d73edfda67b63`
- initial Codex event: `8f8d0e2718baaeeae70406500850d76d840416451d1f4a9d29e0f18ac45702b4`

## 검증

- `python3 -m unittest discover -s tests -p 'test_*.py'` → **23 tests PASS**
- `python3 tools/validate_hypotheses.py --strict` → **29 entries PASS**
- `python3 -m py_compile tools/update_hypotheses.py tools/validate_hypotheses.py tests/test_hypothesis_ledger.py` → **PASS**
- `python3 tools/update_hypotheses.py --help` → **PASS**
- `git diff --check -- AGENTS.md README.md HYPOTHESES.md evidence/HYPOTHESES.md tools/update_hypotheses.py tools/validate_hypotheses.py tests/test_hypothesis_ledger.py experiments/cards coordination/hypotheses` → **PASS**

`coordination/BOARD.md`는 2026-09-09로 stale하며 최신 hosted ledger와 충돌한다. 이번 작업은 그 불일치를 늘리지 않는 control-plane 구현으로 한정했고 BOARD 값은 수정하지 않았다.

## NEXT ACTION

1. Coordinator가 `BOARD.md`를 2026-09-12 hosted 상태로 갱신하고 현재 실험 pointer를 하나로 고정한다.
2. Claude와 Codex의 다음 가설 관련 작업에서 각각 updater event를 1건씩 실제 사용해 cross-agent 운용을 확인한다.


---

## `reports/codex/20260912-1953-BOARD-CROSS-AGENT-EVENT.md`

# BOARD reconciliation and cross-agent event check

VERDICT: **ACTION 1 PASS · ACTION 2 PARTIAL/BLOCKED_EXTERNAL_APPROVAL**

## 결과

1. `coordination/BOARD.md`를 2026-09-12 `evidence/HOSTED_LEDGER.md`에 맞췄다. 누적 제출 5건, 최신 active slots EXP-006/EXP-007 추정, 두 active score는 PENDING이라 `N/A`, yhay81 2188.4와 leaderboard 경계는 2026-09-10 snapshot으로 명시했다. 다음 우선순위는 hosted 판독 → 원장 재정합 → 한 요인 tape/route card다.
2. Codex는 updater로 HYP-0006 / TEST-0006 event를 실제 기록했다. EXP-007이 parent slot을 은퇴시켜 사전등록된 parent same-window A/B가 불가능하다는 점을 다음 행동에 반영했다.
3. 실제 Claude Code 2.1.220은 로컬에 설치되어 있었으나, 호출하면 내부 전략·hosted 기록이 Anthropic 서비스로 전송되고 broad Bash access가 열리므로 security approval에서 거부됐다. Claude를 사칭한 event는 만들지 않았다. Claude event는 사용자에게 payload/destination을 설명한 뒤 명시 승인을 받아야 한다.

## SHA-256

- `coordination/BOARD.md`: `709077bdcc0bbe1dd594725cd860f4d2013115d6f17b44757ee04c82127abf61`
- `HYPOTHESES.md`: `94bd7136cad63c925d0754c6db808ef670fe5d01522edec0c102a3d17881858b`
- Codex event: `7319f5ed26daf72abdf20e4e2f9ed786255ca27d438caf02abfa47fd9ed4b369`

## 검증

- `python3 tools/validate_hypotheses.py --strict` → **29 entries PASS**
- `python3 -m unittest discover -s tests -p 'test_*.py'` → **23 tests PASS**
- `git diff --check -- coordination/BOARD.md HYPOTHESES.md coordination/hypotheses` → **PASS**

## NEXT ACTION

1. 사용자가 내부 네 파일의 Anthropic 전송과 제한된 Claude tool 실행을 명시 승인하면 Claude event 1건과 strict validation을 완료한다.
2. 2026-09-12 12:58 UTC 이후 EXP-006, EXP-007의 status·score·episodes를 수집해 HOSTED_LEDGER, HYP-0006/0007, BOARD를 같은 pass에서 갱신한다.


---

## `reports/codex/20260912-1958-CROSS-AGENT-LEDGER-PASS.md`

# Cross-agent hypothesis ledger verification

VERDICT: **PASS — 실제 Codex/Claude event 생성 및 cross-agent gate 통과**

## 결과

1. 사용자의 명시 승인 아래 실제 Claude Code 2.1.220이 네 상태 문서를 읽고 `--agent claude`로 HYP-0007 / TEST-0007 event를 생성했다. 원장의 `다음 행동`은 submission 56175620과 56165718의 같은-window 강도·패배 상대 중복 판독으로 갱신됐다.
2. Claude의 첫 strict 실행은 exit 3이었다. 데이터 손실이 아니라 validator/recovery가 event 시간 대신 `claude/`, `codex/` 경로순으로 최신 event를 골라, 더 오래된 Codex event를 최신으로 오판한 버그였다.
3. updater recovery와 validator 모두 `(created_at, event_id)` 순서를 사용하도록 수정했고, agent directory 정렬과 event 시간 정렬이 반대인 회귀 test를 추가했다.

## SHA-256

- `HYPOTHESES.md`: `aadb07e5d4cf62cc3c919f056cf7b840d0460911bffab3cdb1b42caadbc43a60`
- Claude event: `9292be7bd932c1deb46fff9a74404d8689cfa9b8424e5866186fca033ecaad18`
- `tools/update_hypotheses.py`: `fa6e6126e91fdc50983457bd4016f5fe777d4fa2e557caba1ff33f411638f597`
- `tools/validate_hypotheses.py`: `27917b4c2625db3dac6ace22c78ac6a15f09779ebadf5090917eb51bbf3804fb`
- `tests/test_hypothesis_ledger.py`: `8f338b50d72e4115437d9e030903cc7fbd0a71696e7f89337288b58933f0c552`

## 검증

- 실제 Claude updater → **PASS**, Claude event 생성
- Claude 첫 `python3 tools/validate_hypotheses.py --strict` → **exit 3**, cross-agent ordering bug 탐지
- 수정 후 `python3 -m unittest tests.test_hypothesis_ledger -v` → **11 tests PASS**
- 수정 후 `python3 tools/validate_hypotheses.py --strict` → **29 entries PASS**
- 수정 후 `python3 -m unittest discover -s tests -p 'test_*.py'` → **24 tests PASS**
- `python3 -m py_compile tools/update_hypotheses.py tools/validate_hypotheses.py tests/test_hypothesis_ledger.py` → **PASS**
- 추가 Claude 재검증은 `--max-budget-usd 0.25` 제한 초과로 command 실행 전 종료했다. local strict 결과에는 영향이 없다.

## NEXT ACTION

1. EXP-006/007의 hosted status·score·episodes가 들어오면 Codex와 Claude가 각 자기 event로 HYP-0006/0007을 갱신한다.
2. 다음 agent 작업 시작 시 `python3 tools/validate_hypotheses.py --strict`를 먼저 실행해 event/view 정합성을 확인한다.


---

## `reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md`

# EXP-006 hosted loss postmortem — episode 108076177

VERDICT | **초기 cash starvation이 첫 구조적 failure; absorption은 1차 원인이 아님** | EXP-006 tar `1c478c24…9721`, replay `108076177` | hosted replay와 engine 1.32.7 exact reproduction 확인 | NEXT ACTION: EXP-008 opening schedule A/B를 Claude card로 사전등록

## 쉬운 설명

EXP-006은 첫날을 마칠 때 돈을 정확히 0까지 써 버렸다. 다음 날 계획에는 일꾼 3명을 고용하는 주문이 있었지만 4코인이 없어 세 주문이 모두 조용히 실패했다. 그 뒤 tape는 일꾼 3명이 있다고 가정한 행동을 계속 냈고, 실행할 사람이 없어서 생산 계획이 연쇄적으로 무너졌다.

## Artifact와 경기

| 항목 | 값 |
|---|---|
| candidate | `coordination/proposals/claude/exp006/submission.tar.gz` |
| SHA-256 | `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` |
| submission | `56165718` |
| hosted target | episode `108076177`, Remielle seat0 vs Sian seat1, seed `1125321547` |
| 최종 reward | Remielle **167,541** vs Sian **58,246**, Sian margin **−109,295** |
| control | episode `108079022`, today seat0 vs Sian seat1, seed `1989066512` |
| control reward | today 99,654 vs Sian **115,745**, Sian margin **+16,091** |

## 가장 이른 failure chain

1. `[HOSTED]` step 1에서 양쪽 opening market schedule이 달랐다.
   - Remielle B: `BUY_PRODUCT WHEAT 13 → BUY_PRODUCT WHEAT 30 → SELL WHEAT 30`, cash **2,656**.
   - Sian A: `BUY_PRODUCT WHEAT 13 → SELL WHEAT 13 → BUY_PRODUCT WHEAT 13`, cash **2,604**.
   - 둘 다 step 종료 WHEAT stock은 13이다. 차이는 stock이 아니라 같은 시장에서 생긴 **52코인**이다.
2. `[HOSTED]` day0 종료 step 23에서 Remielle cash **52**, Sian cash **0**이었다.
3. `[ENGINE+HOSTED]` step 25에서 양쪽 모두 `HIRE` 3건을 요청했다. 비용은 `1+1+2=4`다.
   - Remielle: cash 52→48, hand **3명**.
   - Sian: cash 0, hand **0명**. 예외 없이 세 주문이 모두 실패했다.
4. `[HOSTED]` day1 종료 step 47에서 비어 있지 않은 tile은 Remielle 25, Sian 23이었다. control에서는 Sian이 day0 cash 24를 남겨 HIRE 3건에 성공하고 tile 25를 유지했다.
5. `[HOSTED]` Sian의 −5,000 이하 격차가 다시 회복되지 않은 첫날은 day 10(step 263, −5,988)이고, 최종 −109,295까지 커졌다.

두 agent의 farmer action은 전부 같았고 hands action 차이는 10 step뿐이었다. 반면 유효한 market order는 143 step에서 달랐다. 로컬 exact reproduction에서 현재 EXP-006의 `PREEMPT_COUNTS`는 **0회**였다. 따라서 후반 판매량 격차는 초기 일꾼 failure로 생산 상태가 달라진 결과로 보는 것이 가장 작은 현재 가설이다. 이는 아직 counterfactual A/B 전이므로 `[INFERENCE]`다.

## 폐기한 수정

“day0에 cash 4를 남기도록 `BUY_SEED`를 줄인다”는 제안은 폐기한다. target에서 step 21의 `BUY_SEED WHEAT 2`를 1로 줄이면 바로 다음 step 22의 `PLANT WHEAT` 2건보다 seed가 부족해진다. 엔진 1.32.7은 이 경우 한 건만 심는 것이 아니라 해당 작물의 **두 PLANT 모두 PASS**로 바꾼다(`kaggriculture.py:920-932`). cash reserve와 작물 손실이 함께 바뀌므로 한 요인 실험이 아니다.

## 제안한 한 요인

opening market schedule 전체를 하나의 indivisible factor로 보고 A→B만 바꾼다.

```text
A = [BUY WHEAT 13, SELL WHEAT 13, BUY WHEAT 13]
B = [BUY WHEAT 13, BUY WHEAT 30, SELL WHEAT 30]
```

`[ENGINE+LOCAL]` B vs B를 2-step lockstep으로 재생하면 양쪽 cash 2,630, WHEAT stock 13, shared inventory 9,973으로 같다. 즉 B는 seed나 최종 opening stock을 줄이지 않고 target의 opening collision만 중화할 수 있다. 다만 B의 **순서와 수량 중 어느 부분**이 효과인지 이 실험만으로 분리할 수 없고, 제3의 opening을 만날 때 손해일 수 있으므로 넓은 pool non-inferiority가 필수다.

상세 사전등록 제안: `coordination/proposals/codex/EXP-008-opening-liquidity.md`.

## 재현

```bash
kaggle competitions replay 108076177 -p private_artifacts/replays
kaggle competitions replay 108079022 -p private_artifacts/replays
python3 tools/postmortem_hosted.py --replay private_artifacts/replays/episode-108076177-replay.json --control-replay private_artifacts/replays/episode-108079022-replay.json --team Sian --durable-loss-threshold 5000 --top 5 --focus-steps 1 23 25 47 263 719 --output experiments/results/hosted_postmortem_108076177.json
```

Replay에서 Remielle/today의 action을 `private_artifacts/tapes/`로 추출한 뒤 engine 1.32.7에서 EXP-006과 재생한 결과:

- target 양 좌석: `[167541, 58246]`, `[58246, 167541]` — hosted target과 exact.
- control 양 좌석: `[99654, 115745]`, `[115745, 99654]` — hosted control과 exact.

결과 파일:

- `experiments/results/hosted_postmortem_108076177.json`
- `experiments/results/hosted_postmortem_108076177_baseline_both_seats.jsonl`
- `experiments/results/hosted_postmortem_108079022_control_baseline_both_seats.jsonl`

## Evidence boundary

- `[HOSTED]`: 공개 replay의 action, bank, hands, tiles, rewards.
- `[ENGINE]`: HIRE 비용과 seed 부족 PLANT의 atomic failure.
- `[LOCAL]`: frozen opponent transcript를 사용한 exact reward reproduction과 B-vs-B 2-step 계산.
- `[INFERENCE]`: step 25 HIRE failure가 최종 패배의 주원인이라는 해석. EXP-008 counterfactual이 이를 반증하거나 지지해야 한다.


---

## `reports/codex/20260914-1446-EXP008-INSTRUMENTATION.md`

# EXP-008 instrumentation handoff

VERDICT: **IMPLEMENTED, EXP-008 remains BLOCKED pending card-owner gate clarification**

## 핵심 사실

1. `[ENGINE+LOCAL]` target tape 양상 재현에서 EXP-006 parent는
   `hire_failed=9`, `buy_failed=34`, `seed_blocked_plant=16`, `shed_discarded=209`였다.
   따라서 G4의 세 counter 절대 0은 candidate 결과와 무관하게 parent baseline과 양립하지 않는다.
2. `[LOCAL]` 같은 실행에서 rewards `[167541, 58246]`, step 23 parent bank `0`,
   step 25 parent hands `0`, step 47 parent nonempty tiles `23`으로 기존 target baseline을 재현했다.

## 반송 작업 1~7 처리

1. **DONE** — engine `_do_hire` 결과 전후 hands 수로 `hire_failed`를 player별 기록한다.
2. **DONE** — agent action 반환 직후 engine `interpreter`와 동일한 crop별 atomic seed 조건으로
   `seed_blocked_plant`와 `seed_blocked_by_crop`을 기록한다. `K.interpreter` 직접 교체는 registry가
   원래 함수 객체를 보유하므로 효과가 없어 사용하지 않았다.
3. **DONE** — `--focus-steps 23 25 47`이 정확히 `env.steps[index]`에 저장된 observation에서
   `bank`, `hands`, `nonempty_tiles`, `action`을 뽑는다.
4. **TOOLING DONE; G5 NOT YET TESTED** — `--include-actions`로 719개 action을 덤프하며,
   `tools/compare_action_streams.py`가 전체/market/farmer-or-hands 차이 step과 canonical SHA-256을 낸다.
   아래 self-compare는 비교기 smoke test일 뿐, 미구현 candidate와 parent의 parity 증거가 아니다.
5. **RECOMMENDATION, CARD OWNER ACTION REQUIRED** — 다섯 silent-failure counter 모두 같은 셀에서
   각 `(opponent, seed, candidate seat)` 셀에서 `candidate <= parent`로 고정한다.
   핵심 opening HIRE 회복은 G1의 step 25 hands gate가 직접 판정하므로,
   G4는 다른 시점의 기존 실패를 candidate가 악화시키지 않는 safety gate 역할만 맡는다.
6. **DONE** — `tools/verify_pool.py`로 `private_artifacts/tapes/*-replay.json`, 47개,
   content-set SHA-256 `201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1`
   검증이 PASS했다.
7. **RECOMMENDATION, CARD OWNER ACTION REQUIRED** — G1 step 23/25/47은 hosted 도구와 동일하게
   `env.steps[index]`에 저장된 observation 기준으로 명시한다. 즉 index에 함께 저장된 action을
   실행하기 전 상태가 아니라, 직전 interpreter가 만든 해당 index의 관측값이다.

## 파일과 SHA-256

- `tools/instrument.py` — `6c0b36af31692ef6676728a916ba9b1100db3b02fee0e43a7ab09f73dc12fedd`
- `tools/verify_pool.py` — `a7e22af1a68051119d50f3c71da5217fc390ed7830abdabbb5f489c28297764d`
- `tools/compare_action_streams.py` — `e505f1a2dc6af1449e5f4618642dc2a7d602255ff1faebd473b2d7e6c01593df`
- `tests/test_instrument_exp008.py` — `cccb99ed863bbc4faf00e832d0ff3cf1b9b530ee8fb18ccce01fe19553c73e0e`

## 실행한 검증

```text
python3 -m pytest -q tests/test_instrument_exp008.py tests/test_gate_contract.py
19 passed in 17.11s

python3 scripts/verify_engine_facts.py
exit 0

python3 tools/verify_pool.py --glob 'private_artifacts/tapes/*-replay.json' \
  --expected-count 47 \
  --expected-sha256 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1
PASS, count=47, exact SHA matched

python3 tools/instrument.py \
  --a tape:private_artifacts/tapes/Remielle_episode-108076177-actions.json \
  --b <clean-room EXP-006 main.py> --seeds 1125321547 \
  --focus-steps 23 25 47 --include-actions --json /tmp/exp008-instrument-smoke.json
DONE/DONE, 720 steps, rewards=[167541,58246], parent counters hire=9 buy=34 seed=16 discard=209

python3 tools/compare_action_streams.py --left <smoke.json> --right <smoke.json> \
  --left-player 1 --right-player 1
719/719 actions, different_steps=[], equal SHA-256
```

NEXT ACTION: Claude가 항목 5와 7을 카드에 결과 전 규칙으로 고정해 BLOCK을 해제한 뒤에만,
Codex가 candidate를 구현한다. hosted submission은 이 작업 범위가 아니며 실행하지 않는다.


---

## `reports/codex/20260914-1511-INTUITIVE-REPORTING-RULE.md`

# 직관적 진행 설명 공용 규칙 추가

1. **무엇을 바꿨는가:** 모든 agent가 진행·완료 보고를 `무엇/이유/측정 결과/막힌 점과 다음 행동` 순서로 설명하도록 `AGENTS.md`에 공용 규칙을 추가했다.
2. **왜 하는가:** 비전공자도 현재 작업과 판단 이유를 바로 이해하면서, Claude와 Codex의 설명 형식을 일치시키기 위해서다.
3. **측정과 결과:** `git diff --check -- AGENTS.md`가 PASS했고, 변경 후 SHA-256은 `c687a612a363e04fd41096fa968d63d9f14d30ed449f2852bebcd322a12ec96d`다.
4. **막힌 점과 다음 행동:** 막힌 점은 없다. 다음 agent 작업부터 이 형식을 적용하되, 요약 아래의 증거 꼬리표·수치·path·SHA·재현 명령은 계속 보존한다.

VERDICT | 규칙 추가 완료 | `AGENTS.md` SHA-256 `c687a612a363e04fd41096fa968d63d9f14d30ed449f2852bebcd322a12ec96d` | Markdown diff check PASS | 다음 보고부터 즉시 적용


---

## `reports/codex/20260914-1531-EXP008-PREREG-REVIEW.md`

# EXP-008 preregistration review

1. **무엇을 했는가:** Claude의 EXP-008 사전등록 카드를 candidate 구현 전에 검토했다.
2. **왜 했는가:** 측정 시점을 반대로 설명한 문장이 있으면 같은 숫자로도 상반된 결론을 낼 수 있기 때문이다.
3. **측정과 결과:** engine 1.32.7의 3-step 재현에서 `env.steps[1]`은 `HIRE` action과 그 결과 `hands=1`, `money=2999`를 함께 저장했다. engine facts 검증도 exit 0이었다.
4. **막힌 점과 다음 행동:** 카드 §C의 “같은 index action 미반영” 문장을 정정하고 G5 적용 범위를 확정할 때까지 candidate 구현·baseline 실행·카드 commit을 보류한다.

상세 정정안: `coordination/proposals/codex/EXP-008-PREREG-TIMING-CORRECTION.md`

VERDICT | BLOCKED BY CARD SEMANTICS | card `experiments/cards/EXP-008-opening-liquidity.md` SHA-256 `6a5adda98c1e6388d2729a24dba6ee97c2334bbf61296f8a80328cf2c640a4b1` | engine transition 재현 PASS · engine facts exit 0 | Claude가 결과 전 정정 후 Codex 재검토


---

## `reports/codex/20260914-1534-COMMUNITY-TRENDS-PLAN.md`

# 커뮤니티 동향 4건 반영 검토 — proposal 완료

1. **무엇을 했는가:** Market Preemption, clone counter, opening animal starvation, FERTILIZER resale 네 주장을
   현재 ledger·master plan·EXP-006/008·engine 1.32.7과 대조하고 owner용 work order를 작성했다.
2. **왜 했는가:** 네 주장을 그대로 합치면 이미 검증한 clone logic을 중복 등록하고, 구버전 FERTILIZER
   문제를 현재 engine guard로 오인하며, 서로 다른 opening failure(cash/HIRE와 animal starvation)를 섞게 된다.
3. **측정과 결과:** FERTILIZER engine canary PASS — bank `3000→2900→3000`, shed `0→1→0`,
   market inventory `10000→9999→10000`. Strategy experiment는 미실행(`N/A`).
   `python3 tools/validate_hypotheses.py --strict`는 EXP-008 duplicate IDs 3건으로 exit 3.
4. **막힌 점과 다음 행동:** Claude 소유 EXP-008 card의 duplicate ID를 먼저 고쳐야 한다. Market EXP-009는
   relevant parent-loss postmortem과 exact R10 opponent가 없고, animal EXP-010은 우리 parent starvation
   target이 없어 둘 다 proposal 단계에서 BLOCKED다.

## 산출물

- `coordination/proposals/codex/20260914-community-trends-plan-update.md`
  - SHA-256 `04bff7f98a008e03c125104beedb7fc275be9c3ae73c8b64b937d2a442c7988f`
  - HYP-0031..0033 entry 초안
  - master plan v3 exact change list
  - EXP-009/010 numeric YAML draft와 BLOCK 조건
  - FERTILIZER engine contract test 설계

## 검증

```text
.venv/bin/python --version
Python 3.13.14

engine source: kaggle-environments==1.32.7
FERTILIZER canary: PASS
step 0: bank 3000, shed 0, inventory 10000
step 1: bank 2900, shed 1, inventory 9999
step 2: bank 3000, shed 0, inventory 10000

python3 tools/validate_hypotheses.py --strict
FAIL exit 3: EXP-008 multiple hypothesis_id, multiple test_id, duplicate TEST-0008
```

## Evidence boundary

- Adaptive R10 competitive performance: `[COMMUNITY]`, 우리 재현 `N/A`.
- V14 source engine: `1.32.6`; 우리 EXP-006 test engine: `1.32.7`.
- cow patch 성능: `[COMMUNITY]` 자기보고, 우리 artifact 결과 `N/A`.
- FERTILIZER resale: `[ENGINE+LOCAL]` 1.32.7 정상; hosted behavior `N/A`.

VERDICT | **부분 채택 proposal 완료, canonical owner 변경은 대기** | proposal exact path 위 기록 | engine canary PASS · strict validator FAIL(exit 3) | NEXT ACTION: EXP-008 validator 복구 → updater와 owner card review


---

## `reports/codex/20260914-2025-EXP008-RESULT.md`

# EXP-008 opening liquidity 실행 결과

1. **무엇을 바꾸거나 시험했는가:** EXP-006 parent의 transition 1 market schedule 전체를
   `[[BUY_PRODUCT,WHEAT,13],[SELL,WHEAT,13],[BUY_PRODUCT,WHEAT,13]]`에서
   `[[BUY_PRODUCT,WHEAT,13],[BUY_PRODUCT,WHEAT,30],[SELL,WHEAT,30]]`으로 한 번만 바꿨다.
2. **왜 했는가:** hosted loss 108076177에서 day 0 cash 0 뒤 HIRE 3건이 실패한 연쇄를 끊는지 확인했다.
3. **무엇을 측정했고 결과가 어땠는가:** `[LOCAL]` 고정 326셀에서 parent를 먼저 기록한 뒤 candidate를 측정했다.
   초기 생산력은 회복됐지만 target 두 셀을 모두 졌고 pool에서 candidate-only loss 2셀이 생겨 **FAILURE**다.
4. **무엇이 막혀 있고 다음 행동은 무엇인가:** 실행상 BLOCK은 없다. 카드의 `next_if_failure`에 따라 exact B schedule을
   폐기한다. seed를 늘리거나 cash-floor/order-only로 factor를 쪼개 재해석하지 않는다.

VERDICT | **FAILURE — exact B schedule 폐기** | card `e0e93652…773a`, parent baseline `d4c7c9b1…14f0a`, candidate `930ed160…f079` | 326셀 전부 720 steps `DONE/DONE`, G1/G3/G4/G5 FAIL · G2 PASS | NEXT ACTION: Claude가 카드 `## 결과`와 registry를 이 보고서대로 갱신

## 순서와 provenance

- 선행 확인: `python3 tools/validate_hypotheses.py --strict` exit 0; card SHA exact match;
  `verify_pool.py` PASS, count 47, pool hash `201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1`.
- 1단계 candidate 구현: `experiments/candidates/exp008_opening_liquidity/main.py`.
  `yh_base.py`와 `actions.json`은 parent tar 멤버와 SHA가 각각 동일하다.
- 2단계 SHA freeze:
  - card: `e0e93652991005514bb37f11cf9c69be6d07739594cfee4760ac8792ff30773a`
  - parent tar: `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721`
  - candidate `main.py`: `930ed160a1696ca9118b2f6704112a181e528bf2c7c9fafac5db76518f87f079`
  - candidate `yh_base.py`: `d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b`
  - candidate `actions.json`: `17d503f2fd20d59f9c0f14024d1e74a8add8bb9b5561d4d908b45deecb5495ef`
  - `tools/instrument.py`: `6c0b36af31692ef6676728a916ba9b1100db3b02fee0e43a7ab09f73dc12fedd`
  - `tools/verify_pool.py`: `a7e22af1a68051119d50f3c71da5217fc390ed7830abdabbb5f489c28297764d`
  - `tools/compare_action_streams.py`: `e505f1a2dc6af1449e5f4618642dc2a7d602255ff1faebd473b2d7e6c01593df`
- 3단계 parent baseline을 candidate보다 먼저 326셀 전부 기록했다.
  `evidence/raw/EXP-008/parent_counters.jsonl` SHA
  `d4c7c9b172220d3818545cd66aa6eff7bb3c37d6b42473695f287f9c1d614f0a`.
- 최초 public 40셀 호출에서 public path에 잘못 붙인 `file:` prefix 때문에 INVALID payload가 생겼다.
  candidate 실행 전에 이를 `evidence/raw/EXP-008/_invalid_parent_public_file_prefix/`로 격리하고 plain path로 40셀을
  재측정했다. 최종 parent aggregate는 326 unique cells, target/control/public/pool `2/2/40/282`, 전부 720 steps
  `DONE/DONE`임을 확인한 뒤 SHA를 freeze했다.
- 4단계 candidate도 동일한 326셀을 기록했다.
  `evidence/raw/EXP-008/candidate_counters.jsonl` SHA
  `4c67706ba740decc94ad6e491282393d0e8e6aa244e001d794d929c45f5276e8`.
- 판정기 `evidence/raw/EXP-008/judge_exp008.py` SHA
  `71ca3a8a66bfa9d16c5a3e89c8d376eba8ba458168346ccd478bee3b22ebf6b3`;
  판정 `evidence/raw/EXP-008/verdict.json` SHA
  `9e8cabf4020607abf193ded71071807a8bc9165cba2a95c03180c8a291622d43`.

## `[LOCAL]` G1–G5

| gate | 결과 | 근거 |
|---|---|---|
| G1 | **FAIL** | target W/D/L `0/0/2`. 두 셀 모두 step23 bank `26`, step25 hands `3`, step47 nonempty tiles `25`로 구조 임계는 통과했으나 승패 임계를 실패했다. |
| G2 | **PASS** | control W/D/L `2/0/0`. parent와 candidate reward가 양 좌석에서 동일했다. |
| G3 | **FAIL** | public W/D/L `40/0/0`이나 pool은 parent `276/0/6` → candidate `274/0/8`; `b=0`, candidate-only loss `c=2`. 두 셀 모두 `ymg_aq_episode-106279478-replay`, seed 5103 양 좌석이다. |
| G4 | **FAIL** | 전부 `DONE/DONE`이나 36 pool cells에서 72 counter regressions: `buy_failed` 36건 `0→1`, `seed_blocked_plant` 36건 `0→2`. |
| G5 | **FAIL** | 38 cells에서 허용 집합 `[1]` 밖 action divergence: target 2, pool 36. 이 중 일부는 farmer/hands도 달랐다. |

Target reward는 parent가 양 좌석에서 candidate 관점 `58,246 vs 167,541`이었다. B는 이를 각각
`81,960 vs 86,970`, `81,960 vs 86,970`의 작은 패배로 줄였지만 승패를 뒤집지 못했다.
따라서 결론 상한은 `[LOCAL]` **초기 cash/HIRE/tiles 회복은 확인했으나 exact B schedule은 전체 gate FAILURE**다.
hosted 우위나 제출 근거로 사용하지 않는다.

## 재현

```bash
PYTHONPATH=. python3 evidence/raw/EXP-008/judge_exp008.py aggregate \
  evidence/raw/EXP-008/parent evidence/raw/EXP-008/parent_counters.jsonl
PYTHONPATH=. python3 evidence/raw/EXP-008/judge_exp008.py aggregate \
  evidence/raw/EXP-008/candidate evidence/raw/EXP-008/candidate_counters.jsonl
PYTHONPATH=. python3 evidence/raw/EXP-008/judge_exp008.py judge \
  evidence/raw/EXP-008/parent_counters.jsonl \
  evidence/raw/EXP-008/candidate_counters.jsonl \
  evidence/raw/EXP-008/verdict.json
```


---

## `reports/codex/20260914-2043-GATE-SPLIT.md`

# Release gate 분리와 releases 추적

1. **무엇을 바꿨는가:** 일반 release gate에서 `sell_unfilled`를 diagnostic으로 강등하고,
   종료 시 판매 가능한 shed 재고를 `shed_unsold`로 새로 측정했다. 제출 source/manifest 14개를 Git index에 staging했다.
2. **왜 했는가:** `SELL n=1000` sentinel은 가진 물건을 전부 팔아도 요청량 차이 990을 실패로 만들기 때문에
   실제 손실과 phantom request를 구분하지 못했다.
3. **무엇을 측정했고 결과가 어땠는가:** sentinel integration regression과 실제 손실 unit regression을 포함해
   `python3 -m pytest -q tests/` **39 passed**. tar.gz와 `.DS_Store`는 계속 ignore된다.
4. **무엇이 막혀 있고 다음 행동은 무엇인가:** BLOCK 없음. 다음 release preflight부터 metric schema 3과
   `gate_diagnostics`를 사용한다. EXP별 gate는 각 card 기준을 별도로 적용한다.

VERDICT | **PASS — release gate와 EXP별 gate 역할 분리, release source 추적 완료** | `tools/instrument.py` `83861d7a…fd6b` · tests 39 passed · release 14 files staged | sentinel over-request PASS, 실제 HIRE failure run FAIL, tar/.DS_Store ignored | NEXT ACTION: 다음 release preflight에서 schema 3 JSON을 새로 생성

## Gate contract

- 일반 release gate 절대 0: `noop_actions`, `shed_discarded`, `shed_unsold`, `orders_truncated`,
  `buy_failed`, `hire_failed`, `seed_blocked_plant`, `exceptions`.
- `noop_actions`는 유지했다. engine이 합법 효과 없이 action budget을 소비한 실제 turn 손실이기 때문이다.
- `sell_unfilled = sell_requested - sell_filled`는 JSON의 원래 숫자를 유지하되 `is_clean()`과 failure reasons에서 제외했다.
  기존 `gate_reasons()` list API는 failure-only로 유지하고, diagnostic은 `gate_diagnostics` 및
  top-level `player_gate_diagnostics`로 분리했다.
- `shed_unsold`는 episode 종료 시 private shed에 남은 `PRODUCTS` 수량 합이다. 판매 가능한 재고가 reward로
  실현되지 않은 실제 손실이므로 release gate에 포함했다.
- metric schema는 gate 의미와 출력 field 변경을 드러내기 위해 `2 → 3`으로 올렸다.
- `tools/instrument.py` module docstring에 일반 release gate와 EXP별 card gate의 역할을 명시했다.
  EXP-008 G4의 cell별 `candidate <= parent` 기준은 이 변경으로 바뀌지 않는다.

## Regression tests

```text
python3 -m py_compile tools/instrument.py tests/fixtures/sentinel_sell_agent.py tests/test_gate_contract.py
PASS

python3 -m pytest -q tests/test_gate_contract.py
16 passed in 11.14s

python3 -m pytest -q tests/
39 passed in 11.26s

python3 tools/validate_hypotheses.py --strict
hypothesis ledger PASS: 30 entries
```

- sentinel integration: WHEAT 10개를 산 뒤 `SELL WHEAT 1000`; 양 player 모두 `sell_unfilled > 0`,
  `shed_unsold == 0`, `gate_passed == true`, process exit 0.
- actual loss unit regression: `shed_discarded=1`, `hire_failed=1`, `shed_unsold=1` 각각 `is_clean() == false`.
- actual run regression: 두 turn에 HIRE 10건씩 요청해 두 player 모두 실제 `hire_failed > 0`,
  `gate_passed == false`, process exit 2임을 확인했다.
- 전체 `git diff --check`는 작업 전부터 dirty였던
  `docs/discussion/731215_Daily_Top_Episodes_Dataset.md:18` trailing whitespace와
  `evidence/FACTS.md:236` EOF blank line 때문에 exit 2였다. 본 작업 경로만 지정한 `git diff --check -- ...`는 exit 0.

## 변경 파일 SHA-256

| 파일 | SHA-256 |
|---|---|
| `tools/instrument.py` | `83861d7abd4845e3c8349e98fc2a95ad6a46af49dc755294ddefbf78adeafd6b` |
| `tests/test_gate_contract.py` | `9d05b722c6060a4918b5af0417265661bae17a9a42747f2aa2c4e0cbdc368cd3` |
| `tests/fixtures/sentinel_sell_agent.py` | `f3083921217c2164e605a62df094c509fcf6c1810b1c8f0589e94c8d09301c6a` |
| `tests/fixtures/hire_failure_agent.py` | `b1d460e904e81112a36b6641b99a6c9325fc7b6e7862f9484ae29efdbecefb5f` |
| `releases/public-thomas-replay-router-v2-exact/main.py` | `8241246765098c50223d897739cb32076b71a303284d2e5e1c5f0fb495bb5a97` |
| `releases/public-thomas-replay-router-v2-exact/manifest.json` | `4454e2cacfbb73f9d2a95d9e63e45cc5c59bcacbbd5979ff8f72e28981e73a26` |
| `releases/public-thomas-replay-router-v2-exact/preflight-selfplay.json` | `6f9acab298fd15c715ac18d22ad1e4dd0a1c36a83c6fb3d53c9b6f878fc6cf05` |
| `releases/public-thomas-replay-router-v2-exact/source-metadata.json` | `f8e0e1a1adfb4837e9f1215157aa5141fa4f1004a0a0bdcf9fd8b3995aa2fe58` |
| `releases/public-thomas-replay-router-v2-exact/source.ipynb` | `7e3c99179e84dcbb79aed3d5e80b142b9c370ddbd9200c9400123c1f5368823c` |
| `releases/public-yhay81-shop-router-0909-exact/LICENSE.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| `releases/public-yhay81-shop-router-0909-exact/actions.json` | `17d503f2fd20d59f9c0f14024d1e74a8add8bb9b5561d4d908b45deecb5495ef` |
| `releases/public-yhay81-shop-router-0909-exact/main.py` | `d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b` |
| `releases/public-yhay81-shop-router-0909-exact/manifest.json` | `a47f217db2d876e68ee101e3cc4c42b3f9c077958a6baf2ce5485902c19f6ad8` |
| `releases/public-yhay81-shop-router-0909-exact/preflight_selfplay.json` | `9579377681dc3afd4fd08d8683bc354a09e33fc8852ff2191fbbfe9d6c781f68` |
| `releases/public-yhay81-shop-router-0909-exact/preflight_vs_starter_seat0.json` | `3bd0208d5c8f57a33f2eba54a306b18e105084b930120a9f2a0a6fbf8050148c` |
| `releases/public-yhay81-shop-router-0909-exact/preflight_vs_starter_seat1.json` | `c84f9624b88e66a4f899c8e3152d62a7234def09b1de7d4d0f2f8831e0851d94` |
| `releases/v1-20260910/main.py` | `d6cdb83ffdb27d2614330b20d438a6a20e82c7f4a72ead5ca8be897859de0b59` |
| `releases/v1-20260910/manifest.json` | `e563fe0d6689c6964a4d9bd287f1915fd1a6e82e9f36f853ff709a5ae3244f1c` |

`releases/v0/main.py`와 `manifest.json`은 이미 추적 중이라 새 staged change가 없다.
`submission.tar.gz` 4개는 `.gitignore:9`, `releases/.DS_Store`는 `.gitignore:20`에 의해 제외됨을 확인했다.


---

## `reports/codex/20260915-0115-DEADLINE-PLAN.md`

# 마감 계획·현재 상태 갱신 완료 보고

1. **무엇을 바꿨는가:** 사람 위임 Coordinator로 BOARD·HANDOFF를 갱신하고, `plan/CURRENT.md`가 새 마감 계획을 가리키게 했다. 과거 대표 계획 2개에는 SUPERSEDED 표지를 붙였다.
2. **왜 했는가:** BOARD는 09-13의 EXP-008 대기, HANDOFF는 09-07 v0 첫 제출을 가리켰다. 실제로 EXP-008은 끝났고 실패했다. 신규 제출 한 건이 더 강한 EXP-006을 먼저 은퇴시킨다는 점도 현재 계획에 필요했다.
3. **측정과 결과:** `[HOSTED]` 직접 조회 EXP-006 **1862.6**, EXP-007 **1635.9**, Sian **1,724위**. `[LOCAL]` EXP-008 result·card·parent·candidate와 원자료 SHA를 확인했다. 가설 원장 strict 검증은 **30 entries PASS**다.
4. **막힌 점·다음:** 계획 작성 blocker 없음. 새 전략의 causal 근거·사전등록·독립 검토는 다음 작업이며 N/A. Claude 소유 카드·registry·evidence는 직접 수정하지 않고 exact 반영안을 남겼다. 이것은 재실행 지시가 아니다.

VERDICT | **계획·현재 포인터 갱신 완료** | EXP-008 FAILURE · 현재 A/B 및 FIFO 확인 | 아래 plan SHA·입력 manifest | strict·identity·링크 검증 | NEXT ACTION: owner 기록 반영과 P1 최신 hosted 패배 조사

## 산출물

- [마감 계획](../../../plan/kaggriculture_deadline_plan_20260915.md)
- [현재 계획 포인터](../../../plan/CURRENT.md)
- [BOARD](../../BOARD.md), [HANDOFF](../../HANDOFF_CURRENT.md)
- [직접 조회 근거](20260915-0115-KAGGLE-SNAPSHOT.md)
- [Claude owner 반영안](../../proposals/codex/20260915-owner-record-sync.md)
- [검증 manifest](20260915-0115-DEADLINE-PLAN.validation.json)

Plan SHA-256: `2d3700ef6f0b51f47c5c653e1f0112cd759f312f3c64fa3e0b2978b10197917a`.
본 보고서·manifest는 자기 자신을 hash하지 않는다. 입력/문서별 hash는 manifest를 따른다.

## 계획의 결정과 근거

- 09-15~16 최신 패배와 상대 조사 → 09-17~26 한 요인 카드 최대 2개 → 09-27 새 전략 중단 → 09-28 freeze → **09-29 18:00 KST 제출 완료 목표**.
- 공식 마감 **10-01 08:59 KST**, 내부 여유 **38시간 59분**. 조기 제출은 관측·오류 대응 여유이며 rating 수렴 보장이 아니다.
- EXP-008 B는 회복 지표와 최종 승패가 달랐으므로 폐기 유지. local G4와 일반 release gate의 기준을 혼합하지 않는다.
- 새 제출 C는 현재 `[EXP-006, EXP-007]`을 `[EXP-007, C]`로 바꾼다. EXP-007만 교체하는 것으로 쓰지 않는다.
- HYP-0006/0007은 최신 hosted snapshot을 기록해도 INCONCLUSIVE 유지, HYP-0030은 LOCAL_FAILED 유지. 새 HYP·candidate를 생성하지 않았다.
- 과거 `coordination/CURRENT.yaml` 제안은 구현되지 않았다. 새 상태 관리 도구 없이 BOARD와 현재 계획 포인터만 정리했다.

## 검증과 재현

```bash
python3 tools/validate_hypotheses.py --strict
# exit 0, hypothesis ledger PASS: 30 entries

python3 scripts/verify_engine_facts.py
# exit 0, 엔진 계산과 기본 simulation 출력 확인. assertion 기반 전략 gate가 아님.

shasum -a 256 coordination/proposals/claude/exp006/submission.tar.gz \
  releases/public-thomas-replay-router-v2-exact/submission.tar.gz \
  experiments/candidates/exp008_opening_liquidity/main.py \
  experiments/cards/EXP-008-opening-liquidity.md evidence/raw/EXP-008/verdict.json \
  evidence/raw/EXP-008/parent_counters.jsonl evidence/raw/EXP-008/candidate_counters.jsonl
# 7개 모두 기존 실행 기록과 일치. 두 aggregate는 각각 326행.
```

설치 package `1.32.7`, Python `3.13.14`. 엔진 소스 SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`, JSON SHA `a82c89c1a2315b93f39775d8e025471a01b738647c9772658368ee6b1b6f4867`, `environment/ENGINE_LOCK.md`와 일치.

문서·입력 identity와 로컬 링크 재검증:

```bash
python3 - <<'PY'
import hashlib, json, re
from pathlib import Path
manifest = json.loads(Path('coordination/reports/codex/20260915-0115-DEADLINE-PLAN.validation.json').read_text())
for name, expected in manifest['sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
for name in manifest['markdown_documents']:
    p = Path(name)
    for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
        if '://' in target or target.startswith('#'):
            continue
        assert (p.parent / target.split('#')[0]).exists(), (name, target)
for label in ('parent', 'candidate'):
    assert len(Path(f'evidence/raw/EXP-008/{label}_counters.jsonl').read_text().splitlines()) == 326
print('documentation/identity PASS')
PY
```

검증 범위는 이번 문서·포인터·원장 event와 인용 입력이다. runtime code를 수정하지 않아 pytest 전체는 재실행하지 않았다. 직전 39 passed는 09-14 GATE-SPLIT 보고의 과거 결과이며 이번 결과가 아니다. EXP-008 경기 재실행이나 새 hosted W/D/L 분석도 하지 않았다.

`docs/`·`evidence/FACTS.md` 등 작업 전 dirty 파일은 보존했다. 전체 저장소 clean 여부와 이번 변경 검증은 별개다. 이번 경로만 `git diff --check`로 검사하고 명시적 경로만 commit한다.

## 가설 event

- HYP-0006: 최신 직접 점수 + EXP-008 종료 이후 다음 행동.
- HYP-0007: 최신 직접 점수 + 보완성 미결·FIFO 경계.
- HYP-0030: 기존 FAILURE source 링크와 owner 기록 이관.

`python3 tools/update_hypotheses.py --agent codex --test-id TEST-DEADLINE-PLAN-20260915 ...`를 각 ID에 실행했다. event 3개는 `coordination/hypotheses/codex/EVT-2026-09-14T162222.*.json`. 변경 전후 값과 이유를 event에 보존했다.

다음 행동 두 가지: **① Claude는 owner 반영안으로 결과·원장만 동기화한다. ② Gemini/Codex는 계획 §5의 window를 먼저 고정한 뒤 최신 hosted 패배를 조사한다.**


---

## `reports/codex/20260915-0115-KAGGLE-SNAPSHOT.md`

# Kaggle 일정·제출·leaderboard 재확인

수집: **2026-09-15 KST**, Codex. 시각 상한은 아래처럼 구분한다. 서버가 한 시점에 원자적으로 제공한 snapshot은 아니다.

1. 무엇을 확인했는가: 공식 일정, 최종 평가에 들어갈 경기 조건, 우리 제출 목록과 활성 슬롯.
2. 왜 확인했는가: 09-13 BOARD와 09-14 ledger를 현재 계획의 근거로 갱신하기 위해서다.
3. 결과: `[HOSTED]` EXP-006 1862.6, EXP-007 1635.9, 둘 다 COMPLETE. 공개 UI에서 활성 두 점수와 Sian 1,724위를 확인했다.
4. 다음: 같은-window episode 재판독은 별도 작업이다. 이 snapshot에는 새 W/D/L·실패 상관·점수 변화 원인 분석이 없다.

## 1. 직접 읽은 공식 문서

- [Overview / Timeline / Evaluation / FAQ](https://www.kaggle.com/competitions/kaggriculture/overview): 2026-09-15 KST 브라우저 본문 확인. 웹 검색 도구는 본문을 반환하지 않아 렌더된 페이지로 확인했다.
- [Kaggle Staff 답변](https://www.kaggle.com/competitions/kaggriculture/discussion/732931): Addison Howard와 Bovard Doerschuk-Tiberi의 답변을 같은 세션에서 확인했다.
- `[OFFICIAL]` Entry / Team Merger: **09-23 23:59 UTC = 09-24 08:59 KST**.
- `[OFFICIAL]` Final Submission: **09-30 23:59 UTC = 10-01 08:59 KST**. 이후 약 10-15까지, 또는 수렴할 때까지 추가 경기.
- `[OFFICIAL]` 하루 최대 5개 제출, 최신 2개가 활성·최종 평가 대상. 팀 leaderboard에는 더 높은 agent 점수가 표시된다.
- `[OFFICIAL]` 게임은 W/D/L로 평가하며 coin margin은 rating 변화에 직접 반영하지 않는다.
- `[OFFICIAL]` Staff는 전 기간 경기 중 **양쪽 agent가 최종적으로도 활성인 경기**만 final BT에 포함한다고 설명했다. 짧은 원문: “BOTH agents need to still be active for the episode to count.”
- `[OFFICIAL]` FAQ: 제출 100 MiB, RAM 6.5 GiB, vCPU 1.6. 이 값은 로컬 FAQ의 미치환 template 대신 렌더 본문에서 확인했다.

## 2. CLI 원출력

명령: `kaggle competitions submissions kaggriculture -v` — **exit 0**.
본 세션 직접 조회, 완료 시각의 상한 **2026-09-14 16:13:12 UTC = 09-15 01:13:12 KST**.
첫 sandbox 호출은 DNS 오류로 exit 1, 네트워크 접근 승인 후 같은 read-only 명령이 성공했다. 자격증명 내용은 출력·저장하지 않았다.

```csv
ref,fileName,date,description,status,publicScore,privateScore
56175620,submission.tar.gz,2026-09-12 01:13:24.880000,exp007 thomas router v2 exact sha 8031d51a,SubmissionStatus.COMPLETE,1635.9,
56165718,submission.tar.gz,2026-09-11 12:58:06.513000,exp006 clone-preempt sha 1c478c24,SubmissionStatus.COMPLETE,1862.6,
56147691,submission.tar.gz,2026-09-10 15:57:05.573000,,SubmissionStatus.COMPLETE,2081.8,
56145245,submission.tar.gz,2026-09-10 13:36:45.783000,v1-20260910 measurement submission (sha 723f8fd8),SubmissionStatus.COMPLETE,316.4,
56068891,submission.tar.gz,2026-09-07 04:36:28.727000,v0 pipeline validation (commit 4ed2d29),SubmissionStatus.COMPLETE,347.2,
```

`COMPLETE`는 활성 표시가 아니다. 최신 두 ID와 아래 활성 UI를 함께 대조했다. 은퇴 제출의 2081.8을 현재 활성 성능으로 사용하지 않는다.

## 3. 공개 leaderboard UI

[Leaderboard](https://www.kaggle.com/competitions/kaggriculture/leaderboard), 2026-09-15 KST 본 세션 확인.
1위·10위·Sian 행은 **01:15:05 KST 이전** 확인. 활성 제출 dialog는 그 직후 확인했다.

| 항목 | 표시값 |
|---|---:|
| 1위 Majkel1337 | 3232.2 |
| 10위 Thomas Tschinkel | 2974.2 |
| Sian (`<kaggle_user>`) | **1,724위 / 1862.6** |
| Sian 활성 제출 dialog | **1635.9 / 1862.6** (후자에 leaderboard 표시) |

UI는 이 dialog에 submission ID를 노출하지 않는다. CLI의 최신 두 submission·동일 점수·공식 latest-2 규칙과 결합해 EXP-006/007로 연결했다. 총 팀 수는 페이지 간 갱신 시차가 있어 이 보고서의 판단에 쓰지 않는다.

## 4. 로컬 파일 identity 재확인

```text
shasum -a 256 coordination/proposals/claude/exp006/submission.tar.gz
1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721
shasum -a 256 releases/public-thomas-replay-router-v2-exact/submission.tar.gz
8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180
```

두 파일 모두 기존 기록과 일치한다. 업로드 바이트의 서버측 SHA는 CLI에 없으므로 기존 제출 description·사람 확인에 의한 ID 연결을 유지한다.

VERDICT | 현재 snapshot 확인 | 활성 2개 COMPLETE · EXP-006 점수 우위 | 위 exact tar 경로·SHA | CLI exit 0, 공개 UI 대조, 로컬 SHA 일치 | NEXT ACTION: Claude ledger/registry에 이 출처를 합치고 새 episode window를 별도 판독


---

## `reports/codex/20260915-collector-apply.md`

# 공개 자료 수집기 수정

1. 무엇을 바꿨는가: 조회 실패 시 마지막으로 받은 원문과 목록을 보존하고, 인기·최신 자료 선정과 댓글 저장을 고쳤다.
2. 왜 했는가: 일시적인 API 장애나 놓친 정정 댓글이 잘못된 전략 근거로 이어지는 일을 줄이기 위해서다.
3. 결과: `[LOCAL]` network-free regression test 13개와 실제 SDK response 직렬화 probe가 통과했다. 실제 Kaggle 수집, notebook 실행, hosted 측정은 N/A다.
4. 다음: 독립 검증자의 확인 뒤 root가 통합한다. 이후 실제 수집에서는 run report의 complete/partial/failed와 source SHA를 먼저 확인한다.

**VERDICT: IMPLEMENTED, INDEPENDENT REVIEW PENDING | 실패 항목은 last-good pointer 유지; 재수집 전후 bytes는 SHA snapshot으로 보존 | scripts/fetch_kaggle_updates.py SHA-256 `2729ae529114e84b413c47a9a87db867f3c579ae51dad4fb60921e1fe1fe09bb` | 아래 검증 exit 0 | NEXT ACTION: root integrator의 독립 검증·문서/원장 동기화**

## Applied

- `[LOCAL]` `scripts/fetch_kaggle_updates.py:30` temp file → flush/fsync → atomic replace. 실패한 Message fetch에서 원문을 열지 않으며, listing 실패 시 해당 이전 selection을 유지한다. 모든 listing 실패 때 `latest_metadata.json` bytes를 바꾸지 않는다. `:211` 실행 결과는 complete/partial/failed이며 partial과 failed는 exit 1이다. manifest 쓰기 실패도 run report에 남긴다. 디스크 자체가 모든 쓰기를 거부하면 report 저장도 불가능하고 exception으로 nonzero 종료한다.
- `[LOCAL]` `:87` Discussion은 server `top`/`recent` 각각 page 1에서 최대 5개를 선택한다. Message API는 `sort_by='old', page_size=-1`이며 모든 반환 reply를 재귀 방문한다. id/API parent/date/author/deletion status를 보존한다. SDK의 빈 `raw_markdown` default는 `content` fallback으로 처리한다. server flattening 뒤 원래 부모를 복원했다고 주장하지 않는다.
- `[LOCAL]` `:104`, `:135` installed SDK의 `votes`, `author_name`, `last_comment_post_date`, `total_votes`, `current_version_number`, `last_run_time`을 사용한다. 제공받지 못한 optional 정보는 null/N/A, 실제 0은 0이다. SDK 자체가 wire-level 누락을 0 default로 바꾼 경우는 이 adapter에서 구분할 수 없다.
- `[LOCAL]` `:114` `kernels_pull(metadata=True)`의 `code_file`을 읽어 지원 source를 선택한다. directory 첫 파일을 고르는 동작을 제거했다. source/metadata의 SHA snapshot을 남기며 `listed_version`은 unpinned source와 검증되지 않은 값임을 명시한다. 다운로드 bytes의 정본 identity는 SHA다.
- `[LOCAL]` `:175` 같은 topic/ref는 run당 한 번만 fetch한다. 이전 원문 bytes도 덮기 전에 SHA snapshot으로 남긴다. API를 테스트용 fixture로 주입할 수 있으며 module import 때 authenticate하지 않는다.

## 출력 계약

| 파일 | 내용·한계 |
|---|---|
| `docs/latest_metadata.json` | 기존 `discussions/codes → top_voted/recent` 배열 유지. 새 `collection`에 run_id/started_at/scope/status/coverage. 실패 항목은 이전 entry를 유지하므로 fetched_at이 이번 실행보다 오래될 수 있다. |
| `docs/collection_snapshots/<SHA>/source.<ext>` | 원문 `.md/.py/.ipynb`, Message raw SDK response `.json`, kernel metadata `.json`. 같은 SHA의 bytes는 바꾸지 않는다. |
| `docs/collection_inventory.json` | source별로 이번 수정 이후 성공한 관측의 provenance history. 전체 과거 corpus의 완전한 catalog가 아니다. |
| `docs/collection_runs/<UTC>.json` | selection 규칙, 수집한 source SHA, 단계별 오류·기존 entry 보존 여부, complete/partial/failed. |

source entry는 URL, SHA/snapshot_path, fetched_at, SDK version, source_only scope, fetch_status, engine_version/license의 값 또는 null을 담는다. Code는 listed_version과 source_version(null)을 구별하고, source metadata에 dependency inventory를 보존한다. Source output·dependency bytes는 다운로드하지 않는다. Discussion은 returned_messages만 계산하고 expected_messages는 N/A다. **complete는 요청한 selection의 fetch 완료이며 전체 Kaggle corpus·모든 server 댓글의 완전 수집 증명이 아니다.**

파일 단위 atomic replace이며 모든 파일을 한 번에 commit하는 transaction은 아니다. manifest 저장에 실패하면 이번 run에서 바꾼 alias와 inventory를 이전 bytes로 복구하며, 새로 만든 alias/inventory는 제거한다. 복구 자체가 실패하면 run report에 `rollback` 오류와 path를 남기고 exit 1이다. 강제 프로세스 종료까지 복구하는 crash journal은 아니므로 검토 근거는 `snapshot_path`와 SHA에 연결해야 한다.

## 검증

```bash
python3 -m unittest discover -s tests -p test_fetch_kaggle_updates.py -v
python3 -m py_compile scripts/fetch_kaggle_updates.py tests/test_fetch_kaggle_updates.py
git diff --check -- scripts/fetch_kaggle_updates.py tests/test_fetch_kaggle_updates.py
```

모두 exit 0. Regression test 13개는 SDK field/server sort/reply tree/ref dedup, 부분 fetch 실패, 전체 listing 실패, kernel 실패, 이전 snapshot/history 보존, 0/missing 구분, atomic replace 실패, 빈 raw_markdown fallback, manifest 쓰기 실패, 이전 JSON 파손, legacy metadata 상태의 alias/inventory 복구, 새 alias 제거, 복구 실패 보고를 검사한다. 일부 test가 여러 failure mode를 함께 검사한다.

`tests/test_fetch_kaggle_updates.py` SHA-256: `27d40f442c77ef5531db0ca5858c7cf6eadd460891fc824e3bcf71072f2c391c`.

추가 local probe는 installed `kagglesdk.competitions.types.competition_api_service.ApiTopicMessage`와 `ApiListTopicMessagesResponse`만 import하여 `raw_markdown == ''` default 및 `json_bytes(response)`의 content 보존을 확인했다. API 호출·authentication은 없었다. 재현 핵심:

```python
from kagglesdk.competitions.types.competition_api_service import ApiTopicMessage, ApiListTopicMessagesResponse
from scripts.fetch_kaggle_updates import json_bytes
import json
msg = ApiTopicMessage()
msg.id = 1
msg.content = 'CONTENT'
response = ApiListTopicMessagesResponse()
response.messages = [msg]
assert msg.raw_markdown == ''
assert json.loads(json_bytes(response))['messages'][0]['content'] == 'CONTENT'
```

Primary source는 기존 script가 사용하던 scratch environment의 kaggle 2.2.4 / kagglesdk 0.1.37다. 공통 prefix: `~/.gemini/antigravity/brain/a8068519-c818-408b-8856-6802e8639fe9/scratch/venv/lib/python3.13/site-packages`.

- `kaggle/api/kaggle_api_extended.py:1013` server sort 값, `:3677` topics signature, `:3768` Message -1/all top-level semantics, `:6605` kernel metadata serialization.
- `kagglesdk/competitions/types/competition_api_service.py:4933` Message fields·flattening; `:5339` Topic fields.
- `kagglesdk/kernels/types/kernels_api_service.py:960` Kernel fields.

## Skipped / 경계

- 기존 전체 corpus의 provenance backfill, watchlist/전체 pagination, 자동 요약·index 생성은 이번 수정에 포함하지 않는다. 선정된 source 수집의 정확성과 실패 보존을 우선했고 README 실제 범위 정정은 root 담당이다.
- SDK 설치·환경 이동·인증 경로 변경은 하지 않았다. import는 main 안으로 옮겨 fixture가 외부 연결 없이 실행되게 했다.
- source_version 검증을 위한 추가 API나 notebook 실행은 넣지 않았다. source SHA가 바뀌면 새로운 근거로 검토한다.
- 실제 Kaggle 수집은 실행하지 않았다. root가 TASKS·HYPOTHESES strict 검사·commit을 맡는다.

## 2026-09-16 독립 검증 반영

`[LOCAL]` root와 독립 검증자가 legacy metadata에는 snapshot pointer가 없으므로 manifest 저장 실패 때 alias도 복구해야 한다고 지적했다. `update_alias`가 이전 bytes/부재를 기억하고 `restore_files`가 publish 실패 때 alias와 inventory를 복구하도록 수정했다. 성공 entry는 alias를 쓰기 전에 구성하므로 optional metadata 판독 오류가 alias 변경 뒤에 발생하지 않도록 순서를 조정했다. 세 regression test를 더해 전체 13개 PASS, py_compile와 diff --check도 exit 0을 확인했다. 전체 파일 동시 transaction이나 notebook 실행을 추가하지 않았다.


---

## `reports/codex/20260915-independent-collection-review.md`

# Notebook / Discussion 수집 pipeline 독립 검토

1. 무엇을 검토했는가: 수집 script와 저장된 목록·본문을 대조했다. 공유 docs는 수정하지 않았다.
2. 왜 했는가: 잘못 뽑힌 목록이나 사라진 댓글을 전략 근거로 읽는 일을 막기 위해서다.
3. 결과: `[LOCAL]` 다섯 mocked probe가 기존 본문 손실, 잘못된 field 해석, nested reply 누락, 중복 overwrite, 파일 선택 손실을 확인했다. 실제 Kaggle API 호출·공개 Notebook 실행·hosted 성능 측정은 N/A.
4. 다음: 먼저 실패 시 기존 자료를 보존하고 SDK field를 고친다. 그 뒤 수집 범위·version manifest와 index 동기화를 검증한다.

**VERDICT: CHANGES RECOMMENDED | SDK field mismatch가 현재 산출물에 남음; 일시 API 실패가 last-good snapshot을 삭제함 | 검토 대상 `scripts/fetch_kaggle_updates.py`, SHA-256 `01e9df0bb993f4371f393adc1c47de1fef10db7711d4c30199f13df6a6bae15f` | `python3 /tmp/kaggriculture_collection_probe.py` exit 0, 아래 5개 결함 관측 assertion 통과 | NEXT ACTION: owner에게 P1 수정안 전달**

## 범위와 증거 경계

- 2026-09-15 checkout의 `AGENTS.md`, `coordination/BOARD.md`, `HYPOTHESES.md`, FACTS/KILLS 머리말, `docs/README.md`, `docs/review_insights.md`, 수집 script, metadata/index, Discussion 표본, 실제 파일 inventory를 읽었다.
- BOARD는 09-15 갱신이며 HOSTED_LEDGER의 이전 snapshot 차이를 명시적으로 설명한다. 이번 검토는 전략 실험이 아니며 TASKS와 hypothesis event 기록은 root integrator 소유다.
- installed primary source: script가 line 6으로 우선 선택하는 scratch site-packages의 **kaggle 2.2.4 / kagglesdk 0.1.37**. SDK는 import/authenticate하지 않고 파일을 읽었다.
- 아래 SDK 경로의 공통 prefix `SDK`는 `~/.gemini/antigravity/brain/a8068519-c818-408b-8856-6802e8639fe9/scratch/venv/lib/python3.13/site-packages`다.
- `docs/`에는 검토 시작 전부터 dirty 파일이 있다. 수치와 SHA는 이 working tree snapshot에만 해당한다. 09-06 검토 문서는 검색 힌트로 사용했고 핵심 결함은 현재 코드와 SDK, mocked probe로 다시 확인했다.

## Findings

### F1 — P1: SDK field mismatch가 top/recent 선택과 출처 정보를 망가뜨린다

**위치:** `scripts/fetch_kaggle_updates.py:27`, `:29`, `:47`, `:51`, `:55`, `:111`.

`[LOCAL]` script는 `score`, `last_reply_time`, `author`, `post_time`, `totalVotes`를 읽지만 현재 SDK field는 Topic의 `votes`, `last_comment_post_date`, `author_name`; Message의 `author_name`, `post_date`; Kernel의 `total_votes`다. 존재하지 않는 field에 default를 넣어 오류 없이 모든 topic을 동점·빈 시각으로 만들고 원래 첫 page 순서를 그대로 양쪽 top 5로 낸다. 실제 `docs/latest_metadata.json:3-65`의 Discussion 두 배열이 같고, Notebook/Discussion score가 모두 0이다. 본문 `docs/discussion/731215_Daily_Top_Episodes_Dataset.md:2-5`도 `Unknown`과 빈 시각이다.

**SDK 근거:** `SDK/kagglesdk/competitions/types/competition_api_service.py:1070`, `:5339-5343`, `:4933-4946`; `SDK/kagglesdk/kernels/types/kernels_api_service.py:968-981`.

**최소 재현:** Appendix probe의 실제 SDK field명 fixture에 votes 1..6, 서로 다른 최신 시각을 주어도 선택은 IDs 1..5, 모든 score 0이다. Kernel `total_votes=23`도 0이다.

**영향:** 인기/최신이라는 selection 의미가 사라지고 Staff/사용자 및 시점 구분도 불가능해진다. author_name 자체가 비어 있는 실제 응답은 별도로 N/A로 보존해야 한다.

**최소 수정:** 현재 SDK field를 명시적 adapter로 읽고 missing과 실제 0을 구분한다. SDK version을 고정하고 해당 field fixture 검증을 추가한다. 값이 필수이면 빈 default로 조용히 통과시키지 않는다.

### F2 — P1: 일시 API 실패가 이전 본문·metadata를 덮고 성공으로 끝난다

**위치:** `scripts/fetch_kaggle_updates.py:38-45`, `:19-21`, `:73-82`, `:102`, `:105-109`, `:133-135`.

`[LOCAL]` Message fetch가 예외를 내면 `messages=[]`로 바뀐 뒤 기존 파일을 `w`로 연다. Topic/Kernel listing이 모두 실패해도 main은 빈 배열로 `latest_metadata.json`을 덮고 정상적으로 성공 메시지를 출력한다. 원본·metadata를 final path에 직접 쓰기 때문에 중단/부분 copy/JSON dump 실패에 대한 atomicity도 없다.

**최소 재현:** 정상 ROOT 본문 저장 후 같은 Topic Message API만 예외 발생 → ROOT 삭제. 기존 `{"last_good":true}` metadata에서 세 listing API 전부 예외 → 네 개 빈 배열로 교체되고 `Updates fetched` 출력. Appendix에서 각각 assertion 통과.

**영향:** 일시 장애가 근거 자료의 영구 손실이나 성공으로 오인되는 빈 수집으로 바뀐다. 같은 Topic이 양쪽 목록에 있으면 첫 fetch 성공 뒤 두 번째 실패만으로도 바로 지울 수 있다.

**최소 수정:** 모든 fetch/parse/validate가 성공한 파일만 temp+atomic replace한다. 실패 항목은 기존 pointer를 유지하고 `fetch_status`, `last_attempt_at`, error를 별도 run 기록에 쓴다. 실행 전체는 complete/partial/failed를 구분하고 필수 listing 실패 시 non-zero로 끝낸다. snapshot manifest는 완성된 파일들을 가리키는 마지막 단계에서 교체한다.

### F3 — P1: version 없는 overwrite와 ignored Notebook 때문에 예전 근거 파일을 재구성할 수 없다

**위치:** `scripts/fetch_kaggle_updates.py:85-102`, `:111`, `:128-134`; `.gitignore:4`.

`[LOCAL]` ref만으로 latest source를 pull하고 author_slug 경로에 덮는다. `current_version_number`, source URL, fetched_at, SHA, engine compatibility, license, fetch status를 기록하지 않는다. **실제 Notebook 48개가 `docs/code/*.ipynb` ignore 대상이며 `git ls-files docs/code`는 0개다.** 따라서 Git이 Notebook의 이전 bytes를 보존해 준다는 전제도 성립하지 않는다. 별도 snapshot/manifest는 수집 코드에 없다. 전체 로컬 inventory 48 notebooks/16 discussions 중 latest manifest에는 10/5개만 있고 나머지 38/11개의 수집 시점·이전 version 여부는 해당 manifest로 판단할 수 없다.

**최소 재현:** 같은 ref를 두 selection에 넣은 Changing fixture는 pull을 2회 수행하고 첫 selection의 path가 이미 두 번째 bytes를 가리킨다. `git ls-files docs/code` 및 `.gitignore:4`로 Git 추적 경계 확인.

**영향:** 이전 notebook claim·review가 어느 bytes를 읽었는지 재현할 수 없다. content SHA만 새로 계산해도 이미 잃어버린 이전 source를 복구하지는 못한다. license absence는 불법이라는 판정이 아니라 사용 전 검증할 source 정보가 N/A라는 뜻이다.

**최소 수정:** `(source_id, version)` 또는 content SHA별 immutable snapshot과 full inventory manifest를 만들고 selection은 pointer로 둔다. 최소 source URL/ref, source version, fetched_at UTC, SHA, SDK version, fetch status, license와 engine 정보의 확인/N/A를 기록한다. 같은 ref는 run당 한 번만 fetch한다. 기존 38/11개는 삭제 대신 provenance 미확인 historical entry로 등록한다.

### F4 — P2: 첫 Topic page를 locally sort해서 전역 top/recent라고 부른다

**위치:** `scripts/fetch_kaggle_updates.py:17`, `:27-29`, `:72`, `:79`.

`[LOCAL]` Topic listing은 sort/page 인자 없이 한 번만 호출하고 `total_count`를 확인하지 않는다. F1 field만 고쳐도 첫 page 밖의 고득표·최신 댓글 topic은 계속 제외된다. SDK의 `competition_list_topics`는 sort_by와 1-based page를 지원하며 response는 topics와 total_count다 (`SDK/kaggle/api/kaggle_api_extended.py:3677-3696`).

**최소 재현:** 첫 page에 6개, total_count=7인 fixture에서 함수는 7번째 항목을 조회하지 않는다. 상위 점수를 가진 항목을 다음 page에 두어도 코드의 단일 list call로는 선택할 수 없다.

**영향/범위:** 인기 목록 편향과 신규·기존 watch 대상의 update 누락. **Notebook은 이미 server-side voteCount/dateRun sort를 사용하므로 '첫 page라 top5가 무조건 틀림'은 주장하지 않는다.** 다만 top/recent 밖 watch 대상 version 갱신이나 전체 corpus 수집은 현재 설계에 없다.

**최소 수정:** top/recent 목적이면 각각 명시한 server sort와 limit을 사용하고 실제 sort 의미를 기록한다. 완전 수집 목적이면 total_count와 page exhaustion을 검증한다. 이전 연구에서 사용한 ref/topic의 watchlist 갱신은 별도 범위로 명시한다. dateRun은 마지막 run 기준이며 게시·수정일과 같은 의미라고 쓰지 않는다.

### F5 — P2: nested reply·원래 chronology를 버리면서 모든 댓글 저장을 약속한다

**위치:** `scripts/fetch_kaggle_updates.py:39-40`, `:50-53`; `docs/README.md:116`.

`[LOCAL]` SDK response는 `messages` tree인데 script는 top-level만 reverse하고 replies를 방문하지 않는다. Message의 id/parent/date도 저장하지 않는다. SDK는 `page_size=-1`을 'all top-level'로 명시하지만 script는 이를 지정하지 않는다 (`SDK/kaggle/api/kaggle_api_extended.py:3768-3795`). 실제 server tree는 depth cap 뒤 deeper reply를 ancestor에 flatten할 수 있어(`competition_api_service.py:4944-4946`) 복원된 부모 관계의 한계도 표시해야 한다.

**최소 재현:** ROOT 안에 NESTED reply를 둔 fixture는 ROOT만 저장한다. 실제 `731215` 파일은 질문이 line 6, 원 게시글이 line 23에 있어 '본문부터 timeline' 구조도 아니다.

**영향:** 원 주장에 대한 정정·Staff 답변·추가 조건을 놓친 채 해석할 수 있다. network 검증 없이 현재 특정 thread의 실제 누락 개수는 N/A다.

**최소 수정:** raw response를 보존하고 reply tree를 recursive하게 순회한다. message id와 API가 제공하는 parent 관계, post_date UTC, author, deletion 상태를 남긴다. 정렬 기준을 명시하고 모든 댓글이라고 쓰기 전 returned/expected completeness를 검증한다.

### F6 — P2: source-only 수집을 full runnable artifact로 오인할 수 있다

**위치:** `scripts/fetch_kaggle_updates.py:91-109`; `docs/README.md:64`.

`[LOCAL]` 현재 `kernels_pull` 호출은 metadata=False이고 source 하나만 쓰는 installed SDK 구현이다 (`SDK/kaggle/api/kaggle_api_extended.py:6600-6632`). script도 임시 폴더에서 첫 `.ipynb`/`.py`만 고르고 다른 파일을 삭제한다. saved output files, attached dataset/kernel sources 및 generated multi-file artifact를 수집하거나 manifest에 결손으로 적지 않는다. **실제 SDK가 지금 multi-file source를 반환한다는 뜻은 아니다.** Many fixture는 향후 추가 파일이 있어도 wrapper가 버리는 구조만 입증한다.

**최소 재현:** pull fixture가 notebook/helper.py/data.json을 쓰면 그중 첫 지원 파일 하나만 final output에 남는다. main_file 선택은 directory listing order에 의존한다.

**영향:** downloaded notebook source와 reproducible code/output bundle을 구분할 정보가 없다. Python 이외의 kernel이 recent selection에 잡히면 지원 확장자가 없어 path=None가 된다.

**최소 수정:** 기본 수집 범위를 `source_only`로 명시하고 metadata 및 dependency/output inventory를 저장한다. 실제 재현에 필요한 output만 별도 크기 상한·version·SHA와 함께 가져오는 선택 경로를 둔다. Notebook 실행으로 자동 복원하지 않는다. 지원하지 않는 language는 excluded 이유를 기록한다.

### F7 — P2: index 자동 갱신 계약이 구현되지 않아 최신 manifest와 요약이 어긋난다

**위치:** `scripts/fetch_kaggle_updates.py:120-135`; `docs/README.md:133`; `docs/discussion.md:27`; `docs/latest_metadata.json:29`.

`[LOCAL]` README는 매일 raw→code.md/discussion.md 갱신을 설명하지만 script는 이 두 index를 전혀 쓰지 않는다. 현 metadata top5 마지막 topic은 741235인데 discussion.md top5 마지막 항목은 741003이다. index 안의 `](docs/code/...)`, `](docs/discussion/...)`는 index의 위치에서 docs/docs/...로 해석되어 두 파일 각각 10/10개 상대 링크가 깨진다.

**최소 재현:** script AST에는 index 생성 함수가 없다. manifest id와 index section 비교, `Path(index).parent / target` existence 검사로 각 10개 broken link 확인.

**영향:** 읽는 entrypoint에 따라 선택된 source가 달라지고 원문을 바로 따라갈 수 없다. README의 09:00 실제 scheduler 설정은 이번 scope에서 확인하지 않았으므로 N/A이며 '스케줄 자체가 없다'고 판정하지 않는다.

**최소 수정:** metadata에서 deterministic index skeleton을 생성하고 summary는 source SHA에 묶는다. raw/index snapshot id를 함께 표시하고 상대 링크를 code/... 및 discussion/...로 고친다. 자동 생성 여부와 manual summary owner를 README에 실제대로 쓴다.

## 추가 확인 사항

- `scripts/fetch_kaggle_updates.py:6`은 개인 scratch site-packages에 의존한다. 현재 경로는 존재하므로 당장 import failure라고 판정하지 않았다. 관리되는 environment와 dependency lock으로 이관하는 P2 유지보수 항목이다.
- 경쟁별 filter는 `competition='kaggriculture'`로 들어간다. Notebook selection의 relevance/quality 검증은 없지만 임의의 키워드 filter를 지금 추가하면 원자료 누락을 늘릴 수 있으므로 필수 fix로 제시하지 않았다.
- 기존 notebook을 실행하지 않았고 standalone generated output을 검증하지 않았다. hosted 성능·license 허용 여부·최신 online corpus coverage는 N/A.

## Replay 수집에 적용할 manifest 경계 — 추가 정적 확인

Root 요청으로 `scripts/task2_replays.py:47-84`, `:101-116`만 추가로 읽었다. 전체 replay pipeline 감사나 실행은 하지 않았다. `subs[0]`와 `valid_eps[:5]`로 고른 뒤 `TeamName/EpisodeId`만 CSV에 남기고 replay download returncode는 사용하지 않는다. 따라서 공용 manifest를 replay까지 확장할 때에는 source window/selection rule, team_id, submission_id, episode_id, episode date, 양쪽 seat→submission/team 매핑, W/D/L/status, engine/module version, raw replay SHA, derived tape SHA와 extractor SHA, download status를 함께 보존해야 한다. Unknown 매핑은 N/A로 남긴다. TeamName이나 opening/action 유사도만으로 exact agent lineage를 확정하지 않는다.

## Artifact fingerprint

| 파일 | SHA-256 |
|---|---|
| scripts/fetch_kaggle_updates.py | 01e9df0bb993f4371f393adc1c47de1fef10db7711d4c30199f13df6a6bae15f |
| docs/latest_metadata.json | 1d2e484fd9fbea528508107d5cfeacc2f209a04362134a65e7e22eb41865c218 |
| docs/README.md | dcd4db2886ca3e46a941c3fd415e7eb5729cecbf5fc964ad3909da07d791d669 |
| docs/review_insights.md | c09e4d0d2ed211862db8c2bc8f90684ccaa38abdb2ccbaab6a8b89a207840655 |

## 검증 기록

`python3 /tmp/kaggriculture_collection_probe.py` → exit 0. 다섯 줄 PASS는 수집기가 정상이라는 뜻이 아니라 **보고한 결함을 그대로 관측했다**는 assertion 통과다. AST에서 function 정의만 로드해 third-party import/authentication/network를 배제하고, 모든 쓰기는 TemporaryDirectory에서 수행했다. 실제 공유 docs와 collector는 변경하지 않았다.

```text
PASS observed_wrong_fields_sort_and_nested_reply_loss
PASS observed_transient_message_failure_deletes_last_good_body
PASS observed_total_api_outage_replaces_manifest_and_reports_success
PASS observed_duplicate_pull_same_ref_overwrites_snapshot
PASS observed_single_file_filter_discards_extra_pull_files
```

Appendix 코드를 `/tmp/kaggriculture_collection_probe.py`로 저장해 같은 command로 재현할 수 있다. repo tests나 live ingestion은 실행하지 않았다.

## Appendix — 네트워크 없는 최소 재현 코드

```python
import ast, os, json, shutil, tempfile
from pathlib import Path
from types import SimpleNamespace as N
from contextlib import redirect_stdout
import io
root=Path('~/kaggle/Kaggriculture')
tree=ast.parse((root/'scripts/fetch_kaggle_updates.py').read_text())
ns=dict(os=os,json=json,shutil=shutil,tempfile=tempfile)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'collector_functions','exec'),ns)
class API:
 def competition_list_topics(self,*a,**kw):
  return N(topics=[N(id=i,title=f'T{i}',votes=i,last_comment_post_date=i,author_name='Writer') for i in range(1,7)],total_count=7)
 def competition_list_topic_messages(self,*a,**kw):
  return N(messages=[N(id=1,content='ROOT',author_name='Staff',post_date='2026-09-15',replies=[N(id=2,content='NESTED')])])
 def kernels_list(self,**kw):return [N(ref='a/k',title='K',total_votes=23,current_version_number=2)]
 def kernels_pull(self,ref,path):Path(path,'k.ipynb').write_text('{"cells": []}')
with tempfile.TemporaryDirectory() as td:
 os.chdir(td)
 with redirect_stdout(io.StringIO()):m=ns['fetch_discussions'](API(),'x'); c=ns['fetch_codes'](API(),'x')
 assert [x['id'] for x in m['top_voted']]==[1,2,3,4,5]
 assert m['top_voted']==m['recent'] and all(x['score']==0 for x in m['top_voted'])
 assert c['top_voted'][0]['score']==0
 body=Path(m['top_voted'][0]['path']).read_text()
 assert 'NESTED' not in body and 'Staff' not in body and '2026-09-15' not in body
 print('PASS observed_wrong_fields_sort_and_nested_reply_loss')
 class Broken(API):
  def competition_list_topic_messages(self,*a,**kw):raise RuntimeError('temporary outage')
 with redirect_stdout(io.StringIO()):ns['fetch_discussions'](Broken(),'x')
 assert 'ROOT' not in Path(m['top_voted'][0]['path']).read_text()
 print('PASS observed_transient_message_failure_deletes_last_good_body')
 class Outage:
  def authenticate(self):pass
  def competition_list_topics(self,*a,**kw):raise RuntimeError('outage')
  def kernels_list(self,*a,**kw):raise RuntimeError('outage')
 Path('docs/latest_metadata.json').write_text('{"last_good": true}')
 ns['KaggleApi']=Outage
 output=io.StringIO()
 with redirect_stdout(output):ns['main']()
 assert json.loads(Path('docs/latest_metadata.json').read_text())=={'discussions':{'top_voted':[],'recent':[]},'codes':{'top_voted':[],'recent':[]}}
 assert 'Updates fetched' in output.getvalue()
 print('PASS observed_total_api_outage_replaces_manifest_and_reports_success')
 class Changing(API):
  n=0
  def kernels_pull(self,ref,path):
   self.n+=1;Path(path,'k.ipynb').write_text(str(self.n))
 a=Changing()
 with redirect_stdout(io.StringIO()):c=ns['fetch_codes'](a,'x')
 assert a.n==2 and Path(c['top_voted'][0]['path']).read_text()=='2'
 print('PASS observed_duplicate_pull_same_ref_overwrites_snapshot')
 class Many(API):
  def kernels_pull(self,ref,path):
   Path(path,'k.ipynb').write_text('{}');Path(path,'helper.py').write_text('helper');Path(path,'data.json').write_text('{}')
 with redirect_stdout(io.StringIO()):c=ns['fetch_codes'](Many(),'x')
 assert len(list(Path('docs/code').iterdir()))<=2
 assert not Path('docs/code/data.json').exists() and not Path('docs/code/helper.py').exists()
 print('PASS observed_single_file_filter_discards_extra_pull_files')
```

## 다음 행동 두 가지

1. Gemini 수집 owner와 Codex integrator가 F1/F2/F3를 작은 수정 단위로 나누고 실패 보존·SDK schema·immutable snapshot 검증을 먼저 통과시킨다.
2. F4/F5/F7의 selection/completeness/index 계약을 확정한 뒤 한 번의 검토 가능한 수집 run으로 source manifest와 요약의 일치를 확인한다.


---

## `reports/codex/20260915-independent-plan-review.md`

# 마감 계획 독립 검토 — 실행·판정·공개 자료 연결

VERDICT | **보완 후 실행 권고** | 공개 자료 학습 루프와 release feasibility 선행 작업이 종료 조건까지 닫히지 않음 | 검토 plan SHA `2d3700ef6f0b51f47c5c653e1f0112cd759f312f3c64fa3e0b2978b10197917a` | 문서 대조·기존 JSON 재집계, 새 strategy run N/A | NEXT ACTION: 아래 F1/F2를 다음 카드 착수 조건으로 구체화

1. **무엇을 검토했는가:** 09-15 마감 계획의 실행 순서, 제출 판단, 공개 notebook/discussion 활용 절차를 독립 검토했다. 목적은 score improvement를 위한 의사결정 경로 평가다.
2. **왜 했는가:** 기록을 읽는 다음 agent가 조사·구현·검증 중 무엇을 언제 끝내야 하는지 같은 판단을 내릴 수 있어야 한다.
3. **무엇을 측정했고 결과가 어땠는가:** `[LOCAL]` 기존 EXP-008 parent 326셀의 counter를 재집계했다. `noop_actions`와 `shed_discarded`가 각각 326셀 모두 양수였다. `[INFERENCE]` 좁은 전략 변경이 성공하더라도 일반 release 조건을 충족할 경로는 아직 확정되지 않았다. 새 hosted 수집·실험 성능 측정은 N/A다.
4. **무엇이 막혀 있고 다음 행동은 무엇인가:** 다음 카드 자체가 아직 없으므로 새 통계 임계를 만들지 않는다. 공개 자료 조사 종료 조건과 actual-tar release baseline의 담당·manifest·판정 경로를 먼저 정해야 한다.

## 검토 범위와 후보 식별

읽은 정본: `AGENTS.md`, `plan/CURRENT.md`, `plan/kaggriculture_deadline_plan_20260915.md`, `coordination/BOARD.md`, `HYPOTHESES.md`, `evidence/FACTS.md`, `evidence/KILLS.md`. 보조 근거는 EXP-008 결과·gate split·EXP-006 postmortem·09-14 community 제안과 그 문서에 연결된 기존 JSON이다. 외부 주장 진위의 신규 수집은 다른 독립 검토의 범위다. 이 보고서는 계획, candidate, gate, TASKS, 원장을 수정하지 않는다.

| 대상 | exact file / 이번 SHA-256 | 가설·성공/실패·다음 행동·비교 |
|---|---|---|
| A / EXP-006 | `coordination/proposals/claude/exp006/submission.tar.gz` / `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` | HYP-0006; local card 결과와 hosted causal effect는 별개. 현재 원장은 INCONCLUSIVE. 잠정 parent 보존, 최신 패배 조사. 원래 hosted parent는 은퇴하여 causal A/B N/A (`HYPOTHESES.md:84-95`). |
| B / EXP-007 | `releases/public-thomas-replay-router-v2-exact/submission.tar.gz` / `8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180` | HYP-0007; 현재 보완성 미확인. final pair card에서 개별 강도·같은 셀의 승패를 확인. 현재 snapshot은 causal comparison이 아님 (`plan/kaggriculture_deadline_plan_20260915.md:17-25,115`). |
| EXP-008 | `experiments/candidates/exp008_opening_liquidity/main.py` / `930ed160a1696ca9118b2f6704112a181e528bf2c7c9fafac5db76518f87f079` | HYP-0030/TEST-0008; frozen G1–G5 중 G2만 PASS, FAILURE. exact B 폐기, 표본 추가·factor 사후 분해 금지. 같은 326셀 parent/candidate 비교 (`coordination/reports/codex/20260914-2025-EXP008-RESULT.md:44-57`). |
| 다음 candidate | N/A | 미등록. 새 target·success/failure/inconclusive·holdout은 결과를 보기 전에 card owner가 확정해야 한다. 이 계획을 실행 카드로 오인해서는 안 된다 (`plan/kaggriculture_deadline_plan_20260915.md:4,61,100`). |

## F1 — P1: 공개 notebook/discussion 수집을 실행 가능한 학습 루프로 닫지 않았다

- **위치:** `plan/kaggriculture_deadline_plan_20260915.md:56-61,69-74,86-92,160`; `coordination/BOARD.md:37-40`.
- **증거:** 계획은 09-14 source 두 갈래를 조건부 후보로 보존하고 새 source를 확인하라고 한다. 그러나 날짜별 산출물과 P1의 다섯 항목은 hosted episode/postmortem 및 opponent manifest 중심이다. 신규 notebook/discussion의 검색 범위·변경분 수집 시점·수집 담당의 완료 파일·각 claim의 채택/보류/기각 결과·card owner 인수 조건이 없다. `HYPOTHESES.md:7-16`은 공개 자료도 원장에 연결하도록 정하지만, 일정상 누가 해당 closure를 끝내는지는 명시하지 않는다. 09-14 제안도 새 claim 세 건을 제안한 상태에서 멈춰 있다 (`coordination/proposals/codex/20260914-community-trends-plan-update.md:86-136`).
- **실제 영향:** `[INFERENCE]` 담당자는 hosted replay와 opponent만 수집해 P1 완료를 선언할 수 있다. 이후 공개 자료는 오래된 두 아이디어를 재독하거나 파일만 쌓이고, 현재 실패와 연결되는 새 code/engine warning이 다음 카드 선택에 반영되지 않을 수 있다. 수집량 자체가 아니라 결정으로 연결되지 않는 것이 문제다.
- **최소 변경안:** P1에 한 개의 source triage 산출물을 추가한다. Gemini가 명시한 cutoff까지 notebook/discussion 변경분을 수집하고 URL·작성/갱신일·수집일·version·engine·license·local SHA·claim을 기록한다. Claude가 기존 HYP와 중복을 연결하고 `채택/보류/기각/N/A`, current-parent failure 관련성, 다음 owner를 한 줄씩 확정한다. Codex는 원장 event와 strict validation을 확인한다. 재수집 시점과 마지막 전략 유입 cutoff는 일정 owner가 정하고, 새 자료가 없거나 접근 실패한 경우도 기록으로 종료한다. 다수 자료를 읽었다는 이유만으로 새 strategy card를 자동 생성하지 않는다.
- **반대근거와 범위:** 계획은 이미 source 수준, license, exact artifact, HYP 중복·미승인 경계를 잘 지킨다. `:160`의 Gemini 수집 책임과 `:61`의 updater 경로도 있다. 따라서 “공개 자료를 무시했다”는 결론은 틀리다. 누락은 이 책임을 수집→판독→결정→인수의 확인 가능한 산출물로 묶는 부분이다.

## F2 — P1: release zero gate와 좁은 변경 경로의 충돌을 선언했지만 선행 확인 작업을 배정하지 않았다

- **위치:** `plan/kaggriculture_deadline_plan_20260915.md:70-72,86-90,107-111`; `coordination/BOARD.md:38-40`.
- **증거:** 계획 `:109`는 P1에서 release gate 차이를 먼저 드러내라고 한다. 하지만 P1 다섯 항목에는 actual parent tar의 schema-3 baseline, 대상 manifest, 검증 담당, 통과 불가 시 판정이 없다. `[LOCAL]` 기존 schema-2 parent 결과 `evidence/raw/EXP-008/parent_counters.jsonl:1-326` 재집계에서 `noop_actions` 양수 326/326셀(합 21,146), `shed_discarded` 양수 326/326셀(합 2,296)이다. control 한 셀만 보아도 `evidence/raw/EXP-008/parent/control_today_108079022__seed-1989066512__seat-0.json:99-102`에 schema 2, noop 44, discard 7이 있다. 두 counter의 zero 요구는 schema-3 gate에서도 유지된다 (`coordination/reports/codex/20260914-2043-GATE-SPLIT.md:15-20`).
- **실제 영향:** `[INFERENCE]` 시장 trigger나 animal guard 한 가지를 고쳐 카드가 성공해도 control의 기존 손실을 그대로 보존하면 release가 막힐 수 있다. 그 사실을 09-20 이후 확인하면 제한된 전략 카드·검증 시간을 제출 불가능한 경로에 쓸 수 있다. 현재 데이터는 schema-3 PASS/FAIL의 대체 측정이 아니므로 “parent schema 3 FAIL을 재확인했다”는 주장은 하지 않는다.
- **최소 변경안:** 첫 strategy card 전에 Codex 소유의 actual-tar schema-3 preflight를 P1 종료 조건에 넣는다. 먼저 고정 smoke/stress manifest와 gate 적용 범위를 정하고, 기존 실패 counter와 신규 `shed_unsold`를 분리해 기록한다. 위반이 유지되면 Coordinator/Claude가 `기존 A/B 유지`, `별도 preregistered correctness repair 후 새 parent freeze`, 또는 `계약 검토` 중 경로를 candidate 결과 전에 결정한다. 단순히 zero 기준을 낮추거나 실패를 PASS로 바꾸는 안은 아니다.
- **반대근거와 범위:** `:107-109`가 이미 위험과 미검증 N/A를 명확히 쓰므로 개념적 누락은 아니다. plan은 HOLD도 허용한다. 문제는 그 경고가 실제 다음 작업의 담당·산출물·차단 조건에 반영되지 않아, 뒤늦은 release failure로만 발견될 수 있다는 점이다.

## F3 — P2: same-window 미확보 시 제출 판단 규칙이 두 곳에서 다르게 읽힌다

- **위치:** `plan/kaggriculture_deadline_plan_20260915.md:72,129-134`.
- **증거:** 일정표 `:72`는 “같은-window hosted 관측을 확보할 경로가 없으면 … 교체 보류”라고 한다. 반면 `:133`은 교체 전 같은-window 대조가 불가능하면 N/A를 쓰고 local·전후 관측의 제한된 판단으로 기록하라고 한다. `:131`도 하나의 새 C에 대해 A를 잃을 근거가 충분한지 독립 검토하는 경로를 둔다. 어떤 baseline의 같은 window가 필수인지 구체화되지 않았다.
- **실제 영향:** `[INFERENCE]` FIFO상 C가 올라가면 A가 은퇴하므로 C/A의 동시 hosted 근거를 요구하면 교체 경로가 닫힌다. 반면 B/C 동시 관측은 C가 먼저 제출된 뒤 가능하다. 다음 담당자가 이를 제출 전 필수 gate로 해석하는지, 사후 관측 요건으로 해석하는지에 따라 HOLD/승인 판단이 달라질 수 있다.
- **최소 변경안:** 일정표의 같은-window 문구에 비교 pair와 제출 전/후를 지정한다. C/A causal hosted 비교는 N/A라는 제한을 유지하면서, 제출 전 필요한 local 및 FIFO 독립 검토와 제출 후 B/C window 관측을 구분한다. 혹은 Coordinator가 same-window 없이는 무조건 HOLD를 의도했다면 `:131-133`의 제한 판단 경로도 그에 맞춘다. 둘 중 선택을 report 작성자가 대신하지 않는다.
- **반대근거와 범위:** `:133`은 “제출 허용”이라고 직접 쓰지 않는다. 기존 A/B의 사전 window와 B/C의 사후 window를 뜻했다면 실제 모순은 없다. 따라서 P1 blocker가 아니라 실행자 간 해석 차이를 줄이는 P2 명료화다.

## 기존 계획에서 유지할 부분과 과잉 지적하지 않은 점

- `[LOCAL]` EXP-008 public 40/0/0이 pool regression을 가리지 못하도록 한 결정은 맞다. 과거 결과의 seed 확대·실패 gate 사후 수정은 하지 않는다.
- 공개 4봇을 regression으로 유지하고 최신 opponent manifest를 따로 만드는 방향, donor 중복 경고, seed별 both-seat CI, 경계값 interval을 card에 사전등록하는 방향은 이미 들어 있다. 새로운 CI 방식·margin·power 수치를 이번 review에서 발명하지 않았다.
- 각 agent 최신 패배 한 판은 최소 진단으로 적절하나 failure prevalence를 측정하는 census는 아니다. 이를 전체 패배 원인 비율로 확대 해석하지 않는 한 그 자체를 오류로 보지 않는다. source triage에서 다른 failure를 조사할 때도 한 판에서 미관측이라는 이유만으로 없다고 결론내리지 않아야 한다.
- 09-29 18:00 제출의 +72h는 10-02 18:00 KST로 공식 제출 잠금 뒤다. 계획은 이미 post-deadline 관측과 non-convergence boundary를 허용하므로 일정 오류로 판정하지 않았다. +72h는 해당 제출의 사전 교체 판단 자료가 될 수 없다는 용도만 유지하면 된다.
- FIFO, exact tar 식별, 새 public score를 causal effect로 승격하지 않는 규율, independent reviewer 및 사람 승인 경계는 적절하다.

## 재현·검증

새 code·strategy run·외부 수집·제출은 하지 않았다. 아래는 기존 자료를 읽기만 하는 재집계다.

```bash
python3 - <<'PY'
import json
from pathlib import Path
rows = [json.loads(s) for s in Path('evidence/raw/EXP-008/parent_counters.jsonl').read_text().splitlines() if s.strip()]
print('cells', len(rows))
for key in ['noop_actions', 'shed_discarded', 'hire_failed', 'buy_failed', 'seed_blocked_plant']:
    values = [row['candidate_counters'].get(key, 0) for row in rows]
    print(key, 'positive_cells', sum(v > 0 for v in values), 'total', sum(values), 'max', max(values))
PY
```

결과: exit 0; cells 326; noop `326 / 21146 / 1149`; discard `326 / 2296 / 209`; hire_failed `2 / 18 / 9`; buy_failed `4 / 76 / 34`; seed_blocked_plant `4 / 52 / 16` (positive cells / total / max). 입력 SHA-256은 `d4c7c9b172220d3818545cd66aa6eff7bb3c37d6b42473695f287f9c1d614f0a`다. 이는 schema-2 역사 자료이고 새 schema-3 검증이 아니다.

중요한 차이는 “좋은 규칙이 문장에 있다”와 “다음 담당자가 그 규칙을 통과한 파일을 남겨야 한다” 사이에 있다. 공개 자료와 release 검사 모두 이 연결을 채우면 다음 strategy card의 성공이 실제 제출 판단으로 이어질 수 있는지 훨씬 일찍 알 수 있다.

다음 행동 두 가지: **① source triage 산출물·담당·cutoff·HYP 인수 조건을 확정한다. ② 첫 새 strategy card 전에 실제 parent tar의 schema-3 release feasibility를 고정 manifest로 확인하고 경로를 결정한다.**


---

## `reports/codex/20260915-independent-public-corpus-review.md`

# 공개 corpus 독립 정적 검토 — 2026-09-15

1. **무엇을 검토했는가:** 로컬에 보유한 공개 notebook/discussion과 09-15 마감 계획을 대조했다. 대회 전체 공개 자료를 전수 수집하거나 남의 agent를 실행한 검토는 아니다.
2. **왜 했는가:** 이미 읽은 아이디어를 새 실험처럼 반복하거나, 요약의 과장을 다음 카드의 전제로 옮기는 일을 막기 위해서다.
3. **측정·결과:** `[LOCAL]` notebook 48개(서로 다른 SHA 47개), discussion 16개 중 1개는 본문 없음. 핵심 8건을 선별했다. 가장 중요한 발견은 R10 코드가 실제로 crop age를 확인하지 않는데 제안에서는 ‘수확 가능한 MELON’ 신호로 설명한다는 점이다. 새로운 성능 측정은 N/A.
4. **막힌 점·다음 행동:** source 수집시각이 없는 파일은 N/A이며 현재 hosted engine/성능도 이번 검토 범위 밖이다. 다음 카드 전에 R10 signal 의미를 바로잡고, P1 패배 조사에 자원 도착 확인·중반 continuation 분류를 더하는 정도가 적절하다.

VERDICT | **방향은 대체로 이미 반영, source 의미·원장 연결·표본 구성 보완 필요** | 현재 계획 SHA `2d3700ef6f0b51f47c5c653e1f0112cd759f312f3c64fa3e0b2978b10197917a` | JSON 정적 파싱·출처 대조 완료, gameplay 실행 N/A | NEXT ACTION: source claim 정정 → 기존 P1에 최소 항목 추가

## 1. 범위와 실제 보유량

- 진입점: `plan/CURRENT.md` → `plan/kaggriculture_deadline_plan_20260915.md`. `BOARD.md`는 09-15 갱신으로 시작 freshness 조건을 만족한다. 최신 HOSTED_LEDGER보다 새 snapshot을 명시적으로 연결한다.
- `docs/code/*.ipynb` **48개**를 JSON으로 열어 cell 수·saved output·본문의 version 문자열·SHA를 조사했다. `adilshamim8_kaggriculture-101.ipynb`와 `...grandmaster-starter.ipynb`는 byte-identical이므로 unique 47개다.
- **46개 notebook은 saved output이 0개**다. `anasriaz_kaggriculture.ipynb`는 output 있는 cell 8개, `ashok205_top10-replay-dataset-archive.ipynb`는 7개다. 출력 존재 자체도 competitive 재현 증거가 아니다.
- `docs/discussion/*.md` **16개** 중 **15개에 본문 HTML이 있고**, `741003_Has_anyone_had_success_with_optimization-based_planning.md:1-4`는 제목·Unknown·Score만 있다.
- `docs/latest_metadata.json`은 code **10개**(top 5/recent 5), discussion **unique 5개**(두 목록이 동일)만 가리킨다. 보유 corpus 전체의 색인이 아니다. score는 전부 0이므로 실제 투표수나 순위를 이번 파일에서 회복할 수 없다. 수집시각 field도 없다.
- `docs/code.md`·`docs/discussion.md`는 사람이 작성한 2차 요약이며 metadata와도 일치하지 않는다. 예: discussion 요약은 741003을 포함하지만 latest_metadata에는 없다. 파일 수정시각을 수집일로 바꿔 쓰지 않았다.
- 상세 판독은 아래 6개 notebook과 discussion 2개, 그리고 V16·X-ray·R10 관련 code cell 및 optimization/RL discussion으로 좁혔다. 모든 notebook의 모든 함수가 타당하다고 검증한 것은 아니다. 압축 payload 복원·compile·import·agent 실행·새 수집은 하지 않았다.
- `HYPOTHESES.md`의 30개 entry, 09-14 community proposal, FACTS/KILLS와 대조했다. root가 TASKS·hypothesis event를 담당하므로 이 보고서는 원장을 수정하지 않는다.

## 2. 선별한 8건

### C1. R10 ‘ready MELON’은 수확 시점 검출로 인정하면 안 된다 — 우선 정정

- `[COMMUNITY source-code fact]` `docs/code/xuantianfengwu_kaggriculture-adaptive-land-allocator-r10.ipynb`, **cell 2 source lines 1135–1144**의 `_rival_ready_melons`는 상대 PLANT/MELON의 `yield_units`를 합한다. `planted_day`, crop age, harvest 조건 검사가 없다. **같은 cell lines 90–93**은 one-time crop이 익기 전부터 `yield_units=1`로 시작한다고 설명하고 own HARVEST에는 age 조건을 둔다. 이 보고서가 엔진 동작을 독립 재현한 것은 아니지만, source 내부에서도 함수명과 조건의 의미가 다르다.
- **cell 2 lines 1152–1162**는 day<29, 현재 MELON SELL 없음, queue 여유, 상대 signal>0이면 own shed에서 최대 10개를 추가 SELL한다. 다음 턴 예정 물량을 옮기거나 `repay`하는 코드는 아니다. proposal의 shift/repay는 **우리 신규 설계 `[HYPOTHESIS]`**이고 R10에서 검증된 동작이라고 쓰면 안 된다.
- 반영 상태: 최신 계획 `:56,:92`는 수확 시점 분기를 조건부로 두고 있어 실행 gate는 적절하다. 그러나 09-14 proposal `§1.1, §2.2 HYP-0031`의 **‘수확 가능한 MELON signal’** 표현은 source보다 강하다. 새 카드의 trigger를 이 문구로 확정하지 말 것.
- 원장: HYP-0016은 일반 sale timing, HYP-0006은 clone timing이다. 정확한 R10 source claim은 아직 미등록. 예약 HYP-0031은 canonical ID가 아니다.
- 최소 제안: source claim은 ‘상대 standing MELON yield_units signal 기반 추가 SELL’로 기록하고, **maturity를 별도로 검증한 trigger**와 **shift/repay**는 구분해 설계한다. current parent의 관련 패배가 없으면 계속 보류한다.
- URL: https://www.kaggle.com/code/xuantianfengwu/kaggriculture-adaptive-land-allocator-r10
- 수집일: **2026-09-14**(09-14 proposal §1.2의 기록과 SHA 일치). engine: **source pins 1.32.7**(cell 1); own execution N/A. source test cell 3은 `pass` 상대 seeds 1,2,3 × both seats이며 competitive/hosted 우위 근거가 아니다.

### C2. V41의 ‘요청→실제 도착’ 확인은 P1 진단에 참고할 가치가 있다 — 부분 누락

- `[COMMUNITY]` `docs/code/ahmedberatozer_kaggriculture-v41-review-candidate.ipynb` **cell 0**: 다음 날 worker budget 보호, owned seed 내 PLANT, FEED 전에 food pickup, 다음 observation에서 실제 도착 확인, current field action 뒤 shed에 있는 제품만 funding에 사용한다. 예상 수확을 현재 cash로 세지 않는다.
- **cell 11**은 public-policy 비교가 개선돼도 current-elite point CI가 0을 포함하여 gate FAILED라고 보존한다. source는 352개 elite records에서 +20 wins, 95% interval 약 [-1.14,+12.22]pp를 보고하지만 **모두 COMMUNITY**다. 우리 candidate의 효과로 이전하지 않는다.
- 반영 상태: 계획 `:107–111`의 counter/trajectory 구분, `:113`의 cluster·boundary CI, backbone의 자원 연쇄 설명과 잘 맞는다. 새 architecture를 가져올 이유는 없다. 다만 P1 `:88,:92`에서 진단을 cash/HIRE·starvation만으로 조급하게 줄이지 않고 **seed 부족, pickup 실패, FEED 전 inventory, worker spawn 불일치, night-boundary 실패**를 구분하면 원인 선택에 유용하다.
- 원장: HYP-0015·0027·0030 및 animal proposal에 인접하지만 **actual-resource confirmation**이라는 source claim 직접 연결은 없다. 운영 checklist 보완이면 새 strategy HYP를 남발할 필요가 없다. 특정 guard 효과를 주장하는 경우 updater에서 별도 범위를 등록해야 한다.
- URL: https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v41-review-candidate
- 수집일: **N/A**(이번 검토일 09-15; filesystem mtime만으로 확정하지 않음). engine: **source requires 1.32.7**, cell 10. 저자의 09-14 audit 시각은 notebook 저자의 audit일이며 우리 수집일이 아니다.

### C3. Kaito v27은 opening 교체보다 continuation 진단을 보여 준다 — 방법은 참고, 최신 meta 수치로는 사용 금지

- `[COMMUNITY]` `docs/code/kaitofukami_25-27-strict-future-v27-midgame-meta-reset.ipynb` **cells 3,5,6**: 공통 opening이 넓게 퍼져도 continuation이 다르며, inner에서 좋아 보이는 seat-router가 실제 loss 해결에는 뒤져 coherent single route를 선택했다고 보고한다. 첫 market 차이는 step 161, farmer/hands 차이는 170이라고 적는다.
- **cell 8**의 strict-future는 **2026-08-10** snapshot A·freeze·snapshot B다. **cell 0**의 25/27은 recorded opponent가 반응하지 못하는 local counterfactual이며 Public-LB score가 아니라고 명시한다. ‘최근 5개’나 최신 filename은 최신 전략 관측일을 뜻하지 않는다.
- 반영 상태: 계획 `:88,:104`의 postmortem과 별도 holdout은 이미 반영한다. 최소 추가 가치는 P1에서 **opening failure와 mid/late continuation failure를 분리**하고, development 중 architecture 선택에 쓴 sample을 final holdout으로 다시 부르지 않는 것이다. 새 전면 planner·중간 route splice·전략 전환을 권하지 않는다.
- 원장: HYP-0012·0017·0028과 연결 가능하나 이 source의 chronological protocol 직접 연결은 없다. 성능 수치는 SOURCE_CLAIM에 머문다.
- URL: https://www.kaggle.com/code/kaitofukami/25-27-strict-future-v27-midgame-meta-reset
- 수집일: **N/A**. source evaluation window: **2026-08-10**. engine: **source 1.32.6**(code cell 4). 계획의 1.32.7 성능에 직접 합산 금지.

### C4. 최신 opponent census에도 selection bias와 self-play 제외가 필요하다 — P1 최소 보완

- `[COMMUNITY]` `docs/code/georgymamarin_kaggriculture-what-2600-farms-do-differently.ipynb` **cell 34**: crawl은 census가 아니며, best-game fingerprint는 평균 정책이 아니고, 연속 matchup은 독립이 아닐 수 있으며, validation self-play를 strength 비교에서 제외한다. **cell 32**는 opening hash coverage가 낮으면 population 비율을 발표하지 않는다고 설명한다.
- 반영 상태: 계획 `:87,:89,:90,:113`이 exact 상대 ID·donor 중복·window·CI 문제를 이미 다룬다. 다만 **validation/self-play의 명시적 제외**, 원자료 eligible 수와 선택 수, **engine version별 분리**는 P1 산출물에 적어 두는 것이 안전하다. 새 거대 dataset 다운로드는 필요 없다.
- 구현 차용 주의: 같은 notebook **cell 1**은 numeric version sorting을 쓰지만 **cell 24 source line 19**에는 `engine_version.astype(str) >= "1.32.7"` 문자열 비교가 남아 있다. 이 코드를 그대로 복사하면 1.32.10 같은 버전 분류를 틀릴 수 있다. notebook의 방법 설명을 실행 검증된 utility로 간주하면 안 된다.
- 원장: HYP-0011·0012·0029와 관련 있으나 source 파일 직접 연결 없음. population percentage나 rating 영향 숫자는 이번 실행 N/A.
- URL: https://www.kaggle.com/code/georgymamarin/kaggriculture-what-2600-farms-do-differently
- 수집일: **N/A**. engine: 여러 engine cohort를 읽는 분석이므로 **단일 evaluation version N/A**; source에는 1.32.7 boundary 및 1.32.9/1.32.10 sorting 사례가 있다.

### C5. V14 clone preemption은 이미 반영됐다 — 새 실험으로 중복 등록하지 않기

- `[COMMUNITY]` `docs/code/boatlee_84-84-base-public-holdout-v14-clone-preemption.ipynb`의 clone shift/repay 방법은 09-14 proposal §1.1과 HYP-0006/EXP-006에 이미 연결된다. 최신 계획 `:53`도 고정 parent로 둔다.
- version boundary: **cell 1**의 expected engine과 **cell 7**은 **1.32.6**이다. 제목 84/84는 source 저자의 결과이며 1.32.7 현 field의 우위가 아니다.
- 최소 제안: 기존 HYP-0006 source에 notebook URL·수집일·1.32.6을 보완할 수 있지만 HYP를 새로 만들지 않는다. 우리 exact artifact의 LOCAL 결과와 parent 은퇴로 판정 불가한 hosted causal 효과는 현재 원장대로 분리한다.
- URL: https://www.kaggle.com/code/boatlee/84-84-base-public-holdout-v14-clone-preemption
- 수집일: **2026-09-14**(09-14 proposal §1.2, SHA 일치). engine: **1.32.6**. 새 성능 재현 N/A.

### C6. Cow autopsy는 유효한 진단 가설이고 구현 처방은 아직 미검증 — 이미 조건부 반영

- `[COMMUNITY]` `docs/discussion/741235_Replay_Forensics_The_64K_Bug_in_v40__Patched_Agent.md:10–16`은 특정 route에서 day-1 cows가 사라졌다고 보고하며 survival guard와 **labor spawn reassignment**를 각각 언급한다. 두 원인을 하나의 ‘먹이 우선’ 패치로 뭉치지 말 것.
- `:28–37`의 2W-1L-27T, 23W-7L, 156W-62L-2T는 자기보고다. article 제목의 $64K도 우리 손실 예측치가 아니다.
- 반영 상태: 계획 `:57,:92`는 우리 parent의 같은 failure를 먼저 찾도록 하므로 적절하다. proposal의 guard draft를 승인된 다음 카드로 쓰지 않는 것도 적절하다. 최소 추가는 C2처럼 **FEED가 없었는지 / actor 위치가 틀렸는지 / 사료가 없었는지**를 나누는 것이다.
- 원장: 예약 HYP-0032 미등록. HYP-0030 cash/HIRE 실패와 섞지 않는다.
- URL: https://www.kaggle.com/competitions/kaggriculture/discussion/741235
- 수집일: **2026-09-14**(proposal SHA 일치). source engine: **N/A**. 우리 engine condition은 다른 ENGINE 검토가 담당하며 이 보고서는 재현하지 않았다.

### C7. FERTILIZER SELL 실패는 구버전 경계로 닫아야 한다 — 계획 연결은 있으나 색인은 오해 유발

- `[COMMUNITY]` `docs/discussion/740650_Selling_fertilizer.md:26–35`은 실패가 notebook **1.29.3**, 정상 동작이 local **1.32.7**이라고 후속 정정한다. `docs/discussion.md:54–57`은 후속 정정을 생략하고 resale 차단 가능성을 남긴다.
- 반영 상태: 09-14 proposal §1.1/§1.2에는 version 차이와 1.32.7 canary 결과가 이미 있다. 최신 계획 `:61`은 신규 ledger 3건 미등록을 명시하나 FERTILIZER의 결론을 본문에서 반복하지 않는다. 연결된 proposal을 읽으면 되므로 계획 대수술은 불필요하다.
- 원장: 예약 HYP-0033 미등록. root가 updater로 version boundary를 기록하면 된다. engine canary를 이 세션에 다시 실행했다고 쓰지 말 것.
- 최소 제안: 차단 guard는 기각 상태 유지, source summary에 후속 댓글을 연결. 새 strategy slot을 쓰지 않는다.
- URL: https://www.kaggle.com/competitions/kaggriculture/discussion/740650
- 수집일: **2026-09-14**(proposal SHA 일치). engine: **failure 1.29.3 / reported success 1.32.7**.

### C8. Specialist 실패는 ‘전역 자원 제약 누락’의 사례이지 모든 optimizer 폐기 근거가 아니다 — 요약의 일반화 버리기

- `[COMMUNITY]` `docs/code/mansiaggarwal88_kaggriculture-can-specialists-beat-one-agent.ipynb` **cells 3,11,14,15**의 요지는 cash·payroll·seed·actor capacity를 합쳐 검사하지 않으면 개별 최적화가 충돌한다는 것이다. cell 14는 algorithm 자체가 아니라 구현 실패라고 명시한다.
- **cell 10**의 isolated 수치는 **1 episode, 360 steps, PASS opponent, seed 42**이며 LB와 비교 금지라고 원문이 명시한다. cell 11은 일부 예시를 toy라고 밝히고, cell 18은 재현에 필요한 internal scripts를 요구한다. 현재 corpus만으로 이 실험을 재현할 수 없다. 전문적인 optimizer 이름·selfreported LB 수치가 인과 증거를 보강해 주지는 않는다.
- `docs/code.md:50–53`의 ‘단일 rule agent가 훨씬 강하다’는 결론은 넓다. 더욱이 `docs/discussion.md:27–30,:39–42`는 optimization discussion의 한계와 결론을 서술하지만 **원문 `docs/discussion/741003_...md:1–4`에는 본문이 없다**. 이 discussion에서 얻었다는 결론은 폐기/N/A 처리해야 한다.
- 반영 상태: 계획의 대규모 재구축 제외는 현재 시간·KILLS 조건에 근거하므로 유지할 수 있다. 근거를 ‘community가 모든 optimizer 실패를 증명했다’로 바꾸면 안 된다. HYP-0027의 exact implementation 실패 범위를 넓히지 않는다.
- 원장: global feasibility의 일반 source claim은 직접 미등록. 기존 HYP-0027·0030과 독립 주장인지 root가 범위를 판정한다. 본문 없는 741003은 SOURCE_CLAIM으로 내용을 발명해 등록하지 않는다.
- URL: https://www.kaggle.com/code/mansiaggarwal88/kaggriculture-can-specialists-beat-one-agent ; https://www.kaggle.com/competitions/kaggriculture/discussion/741003
- 수집일: **둘 다 N/A**. engine: **둘 다 N/A**. specialist source는 engine pin 없이 `pip install kaggle-environments`라고만 적는다.

## 3. 우선순위와 최소 수정안

1. **P0 — source 의미 정정:** R10의 `yield_units`가 수확 readiness를 뜻하는지 ENGINE 검토로 확정하고, 09-14 proposal/source-claim의 표현을 고친다. R10 추가 SELL과 우리 shift/repay 설계를 별도 문장으로 유지한다. 본문 없는 optimization discussion과 Kaito의 ‘LB 승률’ 과장 요약은 근거에서 제외한다.
2. **P1 — 기존 패배 조사만 구체화:** 이미 예정된 24h window에 validation/self-play 제외·eligible/selected counts·engine 분리를 적고, 원인 분류에 actual seed/food/pickup/spawn 확인 및 opening/midgame/terminal 구분을 넣는다. 새 후보, 표본 확대, archive 대량 다운로드를 이 검토만으로 시작하지 않는다.
3. **P1 — ledger 연결:** 기존 claim은 HYP-0006/0012/0015/0016/0017/0027/0028/0029와 연결하고, 09-14 미등록 3건은 root가 정정 후 updater로 SOURCE_CLAIM 또는 보유 ENGINE 증거에 맞게 기록한다. 예약 번호 그대로 쓰는 것을 요구하지 않는다.
4. **이번에 더하지 않을 것:** pure PPO·새 전면 planner·새 4-land/GOOSE·새 market rewrite. corpus에는 흥미로운 아이디어가 더 있지만 현재 parent의 패배와 연결되지 않았고 KILL 재개 조건을 충족한 새 ENGINE/HOSTED 근거도 확인하지 않았다.

## 4. Source identity

| 파일 | SHA-256 |
|---|---|
| R10 notebook | `808210418de2cc24d1df643855c8055eeaceb1b0e442dc978e8007b195ddb9e7` |
| V41 notebook | `a0f632f95e1817dd56af0897b22971d79fce6fe91160cfa42fc5927f5ee6eb26` |
| Kaito v27 notebook | `cc61bb10378c555e2cb3090bde2dd8ee442c34d9a8ee98b7ab918dd3acb3db8d` |
| Georgy farms notebook | `7f15418eeac390417219f9e061b1ad28acb5c54c53eecbfe551624724782991d` |
| V14 notebook | `9ab82fd86a9f3be300ec4ee2ae2a6a9bdabc5a1232926ed57a5e3b645dda11e0` |
| Specialist notebook | `f0d29143644dc2e0b7750a6bdafeab980e693be427be211cc54bdfdcd0029153` |
| Cow discussion | `5c3fc283577fe31a629366bb3d44c069b13014a2da83759e432240576b6ec513` |
| FERTILIZER discussion | `5f9ee30c3f95db44407d6c461e9d5b28fe442db0fc7bf86458c4ca9e794848ca` |
| latest_metadata.json | `1d2e484fd9fbea528508107d5cfeacc2f209a04362134a65e7e22eb41865c218` |

Notebook cell index는 **0-based**, cell source line은 **1-based**다. source 파일 SHA와 notebook 내부에 쓰인 candidate SHA는 서로 다른 객체다.

## 5. 실행한 확인과 종료 범위

- `python3` 표준 라이브러리 `json`, `pathlib`, `hashlib`로 notebook JSON parse·inventory·output cell·SHA 확인: **PASS**. notebook code는 문자열로만 읽음.
- `nl -ba` 및 `rg`로 plan/proposal/ledger/source pointer 대조: **PASS**. 수집일·engine이 없는 곳은 N/A로 유지.
- strategy simulation / artifact import / 외부 수집 / 제출: **not run — 독립 정적 검토 범위 밖**.
- 원장 event와 `python3 tools/validate_hypotheses.py --strict`: root가 별도로 수행. 이 subtask는 보고서 한 파일만 작성한다.

가장 중요한 구분은 **변수 이름이 약속하는 의미와 코드가 실제 검사하는 조건**이다. `ready_melons`라는 이름만 믿으면 익지 않은 밭까지 수확 신호로 취급할 수 있으므로, 계획에 옮기기 전에 조건과 engine을 함께 읽어야 한다.

다음 행동 두 가지: **① R10 source-claim의 readiness/추가 SELL/shift-repay 경계를 정정한다. ② 기존 P1에 자원 도착·continuation·표본 제외 기준만 보완하고 실제 패배가 확인된 한 원인에서 다음 카드를 고른다.**


---

## `reports/codex/20260915-independent-review.md`

# 마감 계획·공개 자료·수집 방식 독립 검토

검토일: 2026-09-15 KST. 상태: **CHANGES RECOMMENDED — 검토 완료, 아래 개선은 아직 미적용**.

1. **무엇을 검토했는가:** 마감 계획, 보유 notebook/discussion, 수집 코드를 세 갈래로 독립 검토한 뒤 Codex integrator가 핵심 지적을 재확인했다.
2. **왜 했는가:** 원문을 잘못 읽거나 불완전하게 모으면 그 뒤의 실험 설계가 정교해도 엉뚱한 문제를 풀게 된다.
3. **결과:** `[LOCAL]` notebook 48개·discussion 16개를 inventory로 확인했다. 수집기 결함 5개를 네트워크 없는 fixture로 재현했고, R10의 MELON 해석 오류를 고정 엔진과 대조했다. 새 strategy 성능·hosted 성능 측정은 N/A다.
4. **막힌 점·다음:** 검토 자체의 blocker는 없다. 실제 collector 수정과 plan 반영은 다음 작업이며, 새 카드 전에 source 의미와 release preflight를 정리해야 한다.

VERDICT | **자료 언급은 있지만 학습 절차가 일정에 닫히지 않음; 원문 보존과 source 해석에 실제 결함 있음** | 검토 plan SHA `2d3700ef6f0b51f47c5c653e1f0112cd759f312f3c64fa3e0b2978b10197917a`, collector SHA `01e9df0bb993f4371f393adc1c47de1fef10db7711d4c30199f13df6a6bae15f` | fixture 재실행·SDK 원본 대조·engine source 확인·기존 counter 재집계 PASS | NEXT ACTION: P1 수집 안정성/해석 정정 → 계획의 종료 조건 반영

## 1. 놓친 부분 — 중요한 순서

### F1 · P1 — 실패한 수집이 기존 근거를 지울 수 있다

`scripts/fetch_kaggle_updates.py:38–45`는 댓글 조회 실패를 빈 목록으로 바꾸고 기존 파일을 덮는다. 전체 listing 장애도 `:133–135`에서 빈 metadata와 성공 메시지로 끝난다. `[LOCAL]` 정상 본문을 저장한 뒤 조회 오류를 주자 본문이 사라졌고, 전체 API 오류에서는 기존 metadata가 빈 배열로 교체됐다. 이는 실제 장애가 과거 특정 파일을 지운 원인이라고 단정하는 결과가 아니라, **현재 코드로 그 손실이 가능함을 재현한 결과**다.

가장 먼저 성공적으로 읽고 검증한 자료만 교체하도록 해야 한다. 실패하면 마지막 정상 원문을 보존하고 complete/partial/failed, 실패 이유와 마지막 시도를 별도 기록한다. 쉽게 말하면 **신문을 못 받아 온 날 어제 신문까지 버리는 동작**을 먼저 없애야 한다.

### F2 · P1 — ‘인기·최신’ 선정이 SDK와 맞지 않는다

`scripts/fetch_kaggle_updates.py:27–29,47–55,111`의 `score/last_reply_time/author/post_time/totalVotes`는 설치된 SDK의 `votes/last_comment_post_date/author_name/post_date/total_votes`와 다르다. `[LOCAL]` 서로 다른 점수·시각을 넣어도 모든 점수가 0이 되고 Discussion 두 목록이 같은 순서가 되는 현상을 재현했다. 현재 metadata에서도 두 목록은 동일하다.

field만 고쳐도 끝나지 않는다. Discussion은 첫 page를 한 번 읽어 내부에서 정렬하고, nested reply를 방문하지 않는다. 인기 목록, 최근 변경분, 이미 근거로 쓴 자료의 watchlist를 구분하고 pagination/reply completeness를 기록해야 한다. Notebook의 `dateRun`을 전략 평가일로 해석해서도 안 된다. 상세 SDK line과 반대근거는 [수집 검토 F1/F4/F5](20260915-independent-collection-review.md)에 있다.

### F3 · P1 — 제가 이전 제안에 쓴 R10 ‘수확 가능한 MELON’ 설명은 부정확하다

`[COMMUNITY source]` R10 notebook cell 2:1135–1144는 상대 MELON의 `yield_units`만 합산하며 나이를 검사하지 않는다. `[ENGINE]` 고정 1.32.7은 MELON을 심을 때부터 `yield_units=1`로 만들고, HARVEST는 나이가 `first_yield_day=10`보다 작으면 실행하지 않는다. 양수라는 이유만으로 수확 가능하다고 볼 수 없다.

정정 대상은 `coordination/proposals/codex/20260914-community-trends-plan-update.md` §1.1·미등록 HYP-0031 초안과 이를 참조하는 plan `:56,:92`다. **정정일 2026-09-15, 판정 근거는 engine `kaggriculture.py:16,215–225,449–462`**다. 또한 R10 cell 2:1152–1162는 현재 shed의 MELON을 추가 SELL하며, 다음 턴 물량을 옮겨 되갚는 `shift/repay`는 우리 새 설계다. 두 동작을 source에서 검증된 하나의 방법처럼 묶으면 안 된다.

이 finding은 해당 전략 전체가 실패했다는 뜻이 아니다. source claim은 ‘상대 standing MELON의 yield_units에 반응하는 추가 SELL’로 낮추고, maturity를 검사하는 trigger·shift/repay·효과는 별도로 정의해야 한다. 신규 HYP/실험은 미승인 상태를 유지한다. 원문 URL·수집일 09-14·SHA·cell 위치는 [공개 corpus 검토 C1](20260915-independent-public-corpus-review.md)에 있다.

### F4 · P1 — 파일이 늘어나도 ‘어느 버전을 읽었는가’가 남지 않는다

`[LOCAL]` 보유 notebook은 48개(47 unique SHA), discussion은 16개지만 latest metadata는 각각 10개/5개만 가리킨다. 이는 **38개/11개가 수집되지 않았다는 뜻이 아니라 전체 inventory가 없다는 뜻**이다. source version·수집시각·SHA별 snapshot을 남기지 않고 같은 경로에 덮으며 notebook은 Git ignore 대상이다. 현재 bytes의 SHA로 이미 덮인 이전 source를 복구할 수는 없다.

최소 개선은 immutable 원문 snapshot과 전체 inventory, 최신 선택 pointer를 나누는 것이다. `source ID/URL, source version, 작성·갱신시각, fetched_at UTC, SHA, engine, license, completeness, fetch status`를 기록하고 모르는 값은 N/A로 둔다. Notebook source만 저장했는지 dependency/output도 확보했는지 구분한다. 요약은 source SHA에 연결하고 정정 댓글을 추적해야 한다.

`docs/README.md:133`은 raw 수집 뒤 요약 갱신을 설명하지만 collector에는 `code.md/discussion.md` 생성이 없다. 실제 별도 scheduler의 존재는 이번 검토에서 N/A이며 ‘자동 작업 자체가 없다’고 주장하지 않는다. [수집 검토 F3/F6/F7](20260915-independent-collection-review.md).

### F5 · P1 — 공개 자료를 다음 결정에 연결하는 일이 일정에서 빠져 있다

계획 `:56–61`은 notebook/discussion에서 온 시장·동물 아이디어를 분명 언급한다. 그런데 날짜별 P1 산출물 `:70,86–92`는 hosted 패배와 opponent 조사 중심이고, **변경 자료 수집 → 기존 HYP 중복 확인 → 채택/보류/기각 → 카드 담당 인수**의 완료 파일·주기·cutoff가 없다. 따라서 ‘공개 자료 언급이 전혀 없다’는 지적은 기각하지만, 자료를 의사결정까지 연결하는 절차의 누락은 인정한다.

계획에는 source triage 한 줄을 추가하는 정도가 적절하다. 아래 제안표의 날짜·주기는 아직 적용되지 않은 운영 제안이며 새로운 성능 임계가 아니다.

| 시점 제안 | 담당 제안 | 완료 산출물 |
|---|---|---|
| 09-15~16 P1 | Gemini 수집 → Claude 판독 → Codex 원장 확인 | 기존 48/16 inventory, 수집 실패·미확인 출처 포함; claim별 기존 HYP·우리 패배 관련성·채택/보류/기각·다음 owner |
| 09-26까지 매일 | 같은 역할 | 기존 source/watchlist 변경분과 새 관련 자료; 없으면 ‘변경 없음’, 실패면 partial/failed 기록 |
| 09-27 이후 | Coordinator triage | 새 전략 유입 중단은 유지. 공식 일정·engine patch·우리 artifact에 직접 해당하는 오류는 별도 검토 경로로 전달 |

### F6 · P1/P2 — release 불가능성을 먼저 확인하는 작업과 same-window 조건이 더 구체적이어야 한다

`[LOCAL]` EXP-008의 **기존 schema-2 parent 326셀 모두** `noop_actions`와 `shed_discarded`가 양수였다(합 21,146/2,296). 계획의 현재 일반 release 조건은 각각 0이다. 이것을 새 schema-3 FAIL 판정으로 대신할 수는 없지만, 한 가지 전략 개선 뒤에도 제출이 막힐 위험은 구체적이다. actual parent tar의 schema-3 검사를 새 전략보다 먼저 배정하고, 통과 불가 시 기존 pair 유지/별도 correctness repair/계약 검토의 담당 결정이 필요하다. gate를 결과에 맞춰 낮추자는 제안은 아니다.

또 plan `:72`의 same-window 미확보 시 HOLD와 `:131–133`의 제한된 local 판단 경로는 비교 pair 및 제출 전후를 명시해야 한다(P2). 새 C 제출 시 A가 은퇴하므로 C/A의 동시 hosted 근거와 제출 후 B/C 관측은 다른 문제다. [계획 검토 F2/F3](20260915-independent-plan-review.md)에 재현 명령·범위·반대근거가 있다.

## 2. 공개 자료에서 실제로 참고할 것

공개 source는 가설과 방법의 참고 자료다. 아래는 새 runtime 변경 승인이 아니며, 수집일이나 engine이 N/A인 source의 성능 수치는 이번 계획의 근거로 승격하지 않는다. 각 source의 정확한 cell·SHA·수집 경계는 [corpus C1–C8](20260915-independent-public-corpus-review.md)에 보존했다.

| 자료 | 참고할 부분 | 적용 또는 보류 판단 |
|---|---|---|
| V41 review candidate | 구매·pickup·FEED를 요청한 것과 다음 observation에 자원이 실제 도착한 것을 구분 | P1 패배 분석에 seed/food/worker 도착 확인 추가. 저자 승률은 우리 성능 N/A |
| Kaito v27 strict-future | opening 이후 continuation 실패를 분리하고 개발에 쓴 상대와 나중 관측 상대를 구분 | 평가 방법만 참고. 실제 source 평가일 08-10·engine 1.32.6이므로 최신 meta 근거로 사용 금지 |
| Georgy 2600 farms 분석 | self-play 제외, 표본 선택 편향·복제 계열·engine cohort 구분 | eligible/selected 수와 제외 이유를 manifest에 기록. source의 문자열 version 비교 코드는 그대로 복사하지 않음 |
| V14 clone preemption | clone의 판매 timing에 한정한 개입 | 이미 HYP-0006/EXP-006에 반영. 신규 전략처럼 중복 등록하지 않음 |
| Cow replay forensics | FEED 누락·food 미도착·worker 위치/배정 문제를 나눠 진단 | 우리 parent에서 같은 패배가 확인되기 전 guard 구현 보류 |
| Selling fertilizer | 후속 댓글이 실패 1.29.3 / 정상 1.32.7로 조건을 바로잡음 | `docs/discussion.md:54–57`의 막연한 resale 차단 가능성 요약 정정 권고. 새 SELL 차단 guard 근거가 아님 |
| Specialist notebook | 각 부분이 좋아도 cash/payroll/seed/actor를 합쳐 검사하지 않으면 전체가 실패 | 전역 자원 제약 점검에 참고. 모든 optimizer가 실패했다는 일반화는 기각 |

### 추가 확인: 공식 replay archive를 더 잘 쓰는 방법

`[OFFICIAL]` 09-15 KST 브라우저에서 [Daily Top Episodes Dataset](https://www.kaggle.com/competitions/kaggriculture/discussion/731215)의 **Bovard Doerschuk-Tiberi / Kaggle Staff** 표시와 원문을 확인했다. 매일 경기 당시 양 agent의 평균 rating을 기준으로 정렬하고, 최대 20 GB를 내려받아 일별 자료를 만든다고 설명한다. 단일 engine version은 N/A다. 원문은 [episode index](https://www.kaggle.com/datasets/kaggle/kaggriculture-episodes-index)를 연결한다.

`[INFERENCE]` 따라서 이 archive는 강한 상대 탐색에는 유용하지만 현재 전체 field의 무작위 표본이 아니다. index에서 최근 날짜·engine·submission/계열·우리에게 중요한 상대를 먼저 고르고 필요한 replay만 받는 방식을 권한다. 같은 계열 중복을 분리하고 양 좌석·승패·선택/제외 사유를 남긴다. archive 경기 수를 field prevalence의 분모로 사용하지 않는다. 날짜별 byte 제한에 따른 표본 차이는 댓글의 COMMUNITY 주장으로만 남기며 이번에 수치를 재현하지 않았다.

`scripts/task2_replays.py:61,78,83–87,103–107,124–137`도 보조 검토했다. 첫 submission·앞쪽 episode를 쓰며 `episodes.csv`는 TeamName/EpisodeId만 저장하고, tape에는 양쪽 actions를 묶되 target seat를 지정하지 않는다. 이 legacy script 출력만으로 plan의 exact submission/seat/engine manifest를 충족했다고 볼 수 없다. 실제 CLI 응답 순서·현재 호출 성공 여부는 N/A다. 새 P1 collector가 이 경로를 쓰는지 확인하고 부족한 식별자를 먼저 연결해야 한다.

### 추가 확인: 빈 원문을 채운 뒤에도 요약을 다시 검증해야 한다

`[LOCAL]` `docs/discussion/741003_Has_anyone_had_success_with_optimization-based_planning.md`는 header뿐이다. `[COMMUNITY]` 09-15 KST [실제 Discussion](https://www.kaggle.com/competitions/kaggriculture/discussion/741003)을 브라우저에서 읽어 본문과 댓글을 확인했다(engine N/A). 저자는 여러 의사결정의 결합 때문에 개선이 어렵다고 보고하고, 댓글에는 짧은 planning horizon과 계층 분리 제안·다른 참가자의 어려움이 있다. 비교 artifact가 없는 경험·제안이므로 ‘heuristic이 optimizer보다 우월하다는 다수의 검증’으로 요약할 수 없다.

`docs/discussion.md:27–30,39–42`의 넓은 결론과 `docs/code.md:50–53`의 Specialist 일반화는 근거를 좁혀야 한다. **원문 수집의 성공과 원문 해석의 정확성은 별도 검사**다. 이전 빈 파일이 지금도 온라인 원문이 없다는 뜻은 아니며, 본문의 부재 원인이 F1이었다고 단정하지 않는다.

## 3. 검증·인수 기록

- 독립 보고: [계획](20260915-independent-plan-review.md), [공개 corpus](20260915-independent-public-corpus-review.md), [수집 코드](20260915-independent-collection-review.md). 수집·corpus agent는 파일을 저장한 뒤 usage limit으로 종료됐다. root가 저장된 보고서·코드·원문을 읽고 핵심 결론을 다시 검증했다.
- 재현 명령: `python3 coordination/reports/codex/20260915-independent-collection-probe.py` — 5개 결함 관측 assertion PASS. 실제 collector/authentication/network는 실행하지 않았고 쓰기는 TemporaryDirectory에만 했다. PASS는 수집기가 정상이라는 뜻이 아니다.
- engine 검증: `.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py` SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`가 lock과 일치. AST에서 `CROPS`와 `_new_plant`만 추출해 `_new_plant('MELON',0,24)`의 yield_units=1, first_yield_day=10을 확인했고 HARVEST source를 대조했다. public notebook code는 실행하지 않았다.
- 기존 parent 재집계: [계획 검토의 재현 명령](20260915-independent-plan-review.md)을 root도 실행해 326셀과 두 counter의 합을 확인했다. 새 schema-3 episode run은 N/A다.
- 원장: 기존 HYP-0012/0014/0016에 이번 검토의 범위와 다음 행동을 updater event로 연결한다. 새 전략 HYP-ID를 예약·승인하지 않으며 기존 성능 결과·상태는 유지한다.
- 최종 check 결과와 파일 SHA는 `20260915-independent-review.validation.json`에 기록한다. runtime·collector·plan 본문은 이 검토에서 수정하지 않았다. owner가 사실 정정을 반영할 때 정정일·engine 근거를 원래 틀린 문서에 함께 남겨야 한다.

자료를 더 모으는 것보다 **정확한 원문을 보존하고, 무엇을 채택하지 않았는지까지 남기는 것**이 먼저다. 전략이 좋아 보인다는 주장과 우리 agent의 패배를 줄였다는 증거 사이에는 별도 검증이 필요하다.

다음 행동 두 가지: **① `/vet-apply`로 F1~F4의 수집 안정성·source 의미 정정부터 적용한다. ② P1에 source triage와 actual-tar release preflight를 넣어 새 전략 전에 끝낸다.**


---

## `reports/codex/20260915-plan-apply.md`

# 독립 검토 적용 — 마감 계획의 P1 종료 조건

작성: 2026-09-15 KST · Codex plan_apply. 사용자 요청에 따라 plan 경로의 문서 수정만 담당했다. BOARD·HANDOFF·TASKS·원장·원래 R10 제안 정정과 최종 commit은 root integrator가 처리한다.

1. **무엇을 바꿨는가:** 공개 자료를 다음 카드로 넘기는 표와 actual parent tar의 release 사전 점검을 P1 일정에 넣었다. R10 해석과 제출 전후 관측 대상도 구분했다.
2. **왜 했는가:** 잘못 읽은 힌트로 실험하거나, 성능 개선 뒤에야 제출 불가능함을 발견하는 일을 줄이기 위해서다.
3. **무엇을 확인했는가:** `[LOCAL]` 문서의 local link 15개, artifact SHA 6개, KST 마감·cutoff 순서, 기존 gate·FIFO·사람 승인 조건 보존을 확인했다. 새 preflight·source triage 실행과 성능 측정은 **N/A**다.
4. **막힌 점과 다음 행동:** 문서 적용의 blocker는 없다. 실제 P1은 manifest 확정·담당자 인수 뒤 실행해야 하며, preflight FAIL/N/A면 새 전략 착수는 HOLD다.

VERDICT | **APPLIED — F5/F6 계획 보완 및 F3 해석 정정** | source triage 담당·기한·인수 조건과 parent preflight FAIL/N/A 경로 명시 | `plan/kaggriculture_deadline_plan_20260915.md` SHA-256 `df62f4b6405da86408f14bef4582812d0daad6f378ed7e3fe8b448bcc0f4f238` | 문서·SHA·일정 검사 PASS; preflight 실행 N/A | NEXT ACTION: root 독립 검토·포인터 동기화 후 P1 실행 담당 인수

## 적용 항목과 범위

근거는 [통합 독립 검토 F3/F5/F6](20260915-independent-review.md), [계획 독립 검토 F1/F2/F3](20260915-independent-plan-review.md), [schema 3 gate 계약](20260914-2043-GATE-SPLIT.md)이다. 적용 전 현재 plan을 다시 읽어 같은 누락이 남아 있는지 확인했다. `arcanum:vet-apply`의 조사 후 적용 절차를 따랐다.

| 항목 | 반영 위치 | 완료 내용 |
|---|---|---|
| F5 공개 source triage | plan §4·§5.1·§9 | 최초 09-16 18:00 KST, 09-17~26 매일 18:00 변경분, 09-27 00:00 전략 유입 cutoff. Gemini가 날짜별 표의 단일 writer이며 Claude 판독 제안·Codex 원장 확인을 인수 |
| source evidence와 결정 | plan §5.1 | ID/URL·source/fetch 날짜·version·SHA·engine·license·completeness·fetch status·claim 위치·HYP 중복·우리 패배 관련성·채택/보류/기각·다음 owner. 미확인은 N/A, 실패는 변경 없음과 구분 |
| F6 actual-tar preflight | plan §4·§5.2·§6 | actual parent A tar, schema 3, 실행 전 manifest 전체 목록·SHA·숫자 runtime 상한 확정, cell별 결과·5줄·zero gate·독립 검증. Ledger의 제출 전 N/A는 정상 |
| preflight 실패 경로 | plan §5.2·§6 | FAIL/N/A면 새 전략 HOLD. 기존 A/B 유지 또는 별도 사전등록 correctness repair→새 parent freeze→동일 preflight. gate를 낮추거나 불리한 셀을 뺄 수 없음 |
| same-window 명료화 | plan §4·§7 | 제출 전 A/B 맥락, C/A hosted causal N/A, 제출 후 B/C 또는 C/D 관측으로 구분. 관측 담당·경로 부재면 HOLD. +72h가 마감 뒤면 사후 판독용 |
| F3 R10 의미 | plan §3·§5.3 | standing MELON `yield_units` 합산·추가 SELL이라는 source 동작과 우리 maturity trigger·shift/repay 설계 구분. 정정일과 engine/cell 근거 링크 보존 |

적용하지 않은 범위: `plan/CURRENT.md`는 동일 계획을 가리켜 변경하지 않았다. 새 card·HYP-ID·strategy 구현·수집 실행·preflight 실행·제출·automation 생성은 하지 않았다. 이 보고서는 원래 독립 검토를 대체하거나 그 당시의 ‘미적용’ 상태를 덮어쓰지 않는다.

## 검증

실행한 `git diff --check -- plan/kaggriculture_deadline_plan_20260915.md`는 exit 0이다. Python read-only 검사에서 다음 항목을 확인했다.

- plan의 Markdown local link 15개가 존재한다.
- §10에 적힌 artifact 파일 6개의 SHA-256이 현재 파일과 일치한다.
- 09-30 23:59 UTC = 10-01 08:59 KST이고 09-29 18:00 KST 목표부터 38시간 59분 남는다.
- 09-16 P1 종료 → 09-17 전략 단계 → 09-26 마지막 정기 triage → 09-27 cutoff → 09-28 freeze → 09-29 제출 목표 순서다. 선행 조건 미달이면 날짜만으로 넘어가지 않는 문구를 유지했다.
- 95% CI 하한 > 0.5, zero gate, FIFO, 제출 사람 승인, 새 ID 미등록, preflight FAIL/N/A HOLD와 Ledger 예외를 보존했다.
- `git show HEAD:plan/CURRENT.md`와 현재 파일의 bytes가 같다.

링크·SHA 재현 명령:

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib, re
p = Path('plan/kaggriculture_deadline_plan_20260915.md')
s = p.read_text()
links = [x for x in re.findall(r'\]\(([^)]+)\)', s) if '://' not in x and not x.startswith('#')]
assert all((p.parent / x.split('#')[0]).exists() for x in links)
artifacts = re.findall(r'\|[^\n]*\| `([^`]+)` \| `([a-f0-9]{64})` \|', s)
assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest() == h for f, h in artifacts)
print('PASS', len(links), 'local links;', len(artifacts), 'artifact SHAs')
PY
```

계획의 문장에 점검을 권하는 것과 담당자가 결과 파일을 남겨야 다음 단계가 열리는 것은 다르다. 이번에는 그 경계를 명확히 했으며, 자료를 채택했다는 판단도 우리 agent의 성능이 좋아졌다는 판단과 분리했다.

다음 행동 두 가지: **① source triage 표와 hosted 패배 근거를 담당자에게 인수한다. ② actual parent tar의 manifest를 먼저 확정하고 preflight 판정에 따라 전략 또는 correctness 경로를 선택한다.**


---

## `reports/codex/20260916-1726-P1B-RUNNER-UPDATE.md`

# P1b runner 보완과 manifest reconciliation

1. **무엇을 바꿨는가:** `tools/instrument.py`에 player별 Schema·Runtime 측정과 제출 player 선택 gate를 추가하고 P1b manifest 초안을 갱신했다.
2. **왜 하는가:** opponent의 진단값을 잃지 않으면서 actual parent A만 release verdict에 넣고, 누락된 first call·hands alignment·양 player CPU를 측정하기 위해서다.
3. **무엇을 측정했고 결과가 어땠는가:** fixture tests 56개가 모두 통과했다. actual parent tar와 P1b cell 결과는 **N/A**다.
4. **무엇이 막혀 있고 다음 행동은 무엇인가:** Claude의 review는 manifest 생성 전 사양 검토였고, 재현 대상·범위·seed·runtime cutoff·독립 검증자 5건은 여전히 미확정이다. 최신 manifest를 두 역할이 승인하기 전 실제 preflight는 BLOCKED다.

VERDICT | **TOOLING PASS / ACTUAL PREFLIGHT BLOCKED** | 양 player 측정 보존 + parent-only verdict, 56 tests PASS | runner `284dee4c…d0629` · manifest draft `97ee0657…f1019` | actual tar execution N/A | NEXT ACTION: 5개 contract 결정 → current-manifest reviews → manifest SHA freeze

상세 구현·검증·쟁점 표·재개 순서는 `experiments/results/p1_release_preflight/report.md`와 `resume.json`에 있다. 이번 작업은 tar extraction, clean-room import, episode 실행, submission을 하지 않았다.

다음 행동 두 가지: **① owner가 다섯 contract 항목을 확정한다. ② Claude와 지정된 independent validator가 최신 manifest를 승인한 뒤 별도 turn에서 preflight를 실행한다.**


---

## `reports/codex/20260916-1919-P1B-ACTUAL-TAR-PREFLIGHT.md`

# P1b actual parent A 제출 tar preflight 완료 보고

1. **무엇을 시험했는가:** 실제 제출 tar를 새 clean-room에 풀어 승인된 13경기(self-play 3, starter 6, target/control stress 4)를 고정 조건 그대로 실행했다.
2. **왜 하는가:** 새 전략을 만들기 전에 현재 artifact가 release correctness 기준을 만족하는지 확인하기 위해서다.
3. **측정 결과:** `[LOCAL]` 13/13경기는 모두 720-step `DONE/DONE`, runtime PASS였다. 그러나 gated parent 16/16이 zero gate를 실패했다.
4. **막힌 점과 다음 행동:** 독립 결과 검증이 남았고 correctness FAIL이므로 전체 preflight PASS가 아니다. 기준을 낮추거나 seed를 바꾸지 않고 별도 correctness 경로를 결정해야 한다.

VERDICT | **LOCAL FAILURE / INDEPENDENT RESULT VERIFICATION PENDING** | tar `1c478c24…9721`, manifest `46fd9e5e…4801c` | 13/13 valid completion; Identity PASS, Schema FAIL, Runtime PASS, Isolation PASS, License PASS, zero gate FAIL | NEXT ACTION: independent result verification → Coordinator/Claude correctness decision

정본 결과는 `experiments/results/p1_release_preflight/report.md`, 구조화 집계는 `aggregate.json`, argv·exit code는 `commands.json`, 원자료는 `cells/*.json`이다. Kaggle 제출과 전략 수정은 실행하지 않았다.

다음 행동 두 가지:

1. 기존 Antigravity 검증자가 새 `commands.json`·13개 cell JSON·`aggregate.json`·`report.md`를 독립 재집계해 결과 hash와 판정을 확인한다.
2. 검증 뒤 Coordinator/Claude가 frozen gate를 유지한 별도 correctness repair 또는 현재 A/B 유지 중 하나를 결정한다.


---

## `reports/codex/20260916-2210-TOP10-IMITATION-REVIEW.md`

# Top 10 imitation 검토·실행계획 보고

1. 무엇: Claude 답변의 근거를 재검토하고 donor provenance → exact reproduction → 독립 confirmation → release 계획을 작성했다.
2. 이유: 행동 기록은 특정 경기의 결과이고, 새 상황의 판단 능력이나 donor rating을 그대로 보장하지 않는다.
3. 결과: pool count/SHA PASS, ymg_aq 6·Mengfei Li 6 원자료 engine 1.32.7 확인, CSV 수치 확인. 새 후보 성능 N/A.
4. 다음: 계획 S0의 BOARD 최신 상태 반영·K3 scope·P1b HOLD 처리를 owner에게 이관. 새 대전·제출 없음.

VERDICT | REVIEW COMPLETE / EXPERIMENT BLOCKED UNTIL S0 | rating 선형 환산 근거 없음, donor/evaluation 오염 방지 필수 | 아래 plan+SHA | pool/ledger/data assertions PASS | NEXT ACTION: owner contract resolution → donor inventory/reproduction

- 계획: `coordination/proposals/codex/20260916-TOP10-IMITATION-PLAN.md`, SHA-256 `edd13cb75d6b529f04a09301aa158fb37c5747f642824f18dc3fdca5430e88f3`
- audit: `coordination/proposals/codex/20260916-TOP10-IMITATION-PLAN.audit.json`, SHA-256 `47ac2159250800942d5eda5559d0549f4745cf4746459409e8502d02f77bbc99`
- parent tar: `coordination/proposals/claude/exp006/submission.tar.gz`, SHA-256 `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721`
- source 파일·plan 정본·BOARD·KILLS·FACTS는 변경하지 않았다. 계획은 Codex proposal이며 owner 채택 전 실행 지시가 아니다.
- HYP-0010은 기존 SOURCE_CLAIM을 유지하고 updater로 다음 행동만 갱신했다. TEST-REVIEW-TOP10-20260916은 검토 ID이고 arena ID가 아니다.

## 실제 실행한 확인

- `python3 tools/verify_pool.py --glob 'private_artifacts/tapes/*-replay.json' --expected-count 47 --expected-sha256 201d9724032420969077a803e768f720d3741b6ece57142e8e4b8bfda3fe76e1` → exit 0, PASS.
- `python3 tools/validate_hypotheses.py --strict` → exit 0, PASS, 31 entries.
- Python read-only CSV/tape/raw replay/engine SHA audit 및 산출물 assertion → PASS. 구조화 출력은 audit JSON.
- 공식 Kaggle rules/index URL web open → 본문 0 lines. 최신 법적 문구·dataset license/작성자 직접 확인 N/A; 저장된 rules와 discussion 본문에 근거를 한정했다.
- PMLR Ross et al. (2011) 원문 초록 확인: https://proceedings.mlr.press/v15/ross11a.html . imitation learning의 상태 분포 변화 설명만 사용, 이 게임의 성능 예측에 쓰지 않음.
- candidate 코드 변경/새 simulation/hosted 조회/다운로드/제출: 미실행(검토·계획 범위).

기존 작업의 HYPOTHESES.md·TASKS.md 수정이 이미 존재했다. 다른 owner의 미커밋 변경은 포함하지 않고 이번에 만든 proposal/audit/report/event만 커밋한다. 공용 view와 자기 TASK 행은 작업 폴더에 남겨 owner의 기존 변경을 보존한다.

다음 행동 두 가지:
1. Coordinator/Claude가 S0 계약/상태 정리를 반영한다.
2. Gemini inventory 뒤 Codex가 exact reproduction fixture를 준비한다.


---

## `reports/codex/20260916-2232-TOP10-DONOR-REPRO.md`

# 최신 top 10 donor inventory와 원래 경기 재현

작성: Codex · snapshot 2026-09-16 22:26:06 KST (13:26:06 UTC).

**PASS — top 10의 활성 submission 20개를 수집했고, 상위 두 donor의 최근 기록 6개(고유 5경기)를 원래 조건으로 정확히 재현했다.**

1. 무엇: 최신 donor의 team → submission → episode → seat → raw SHA 연결과 양측 transcript 재현.
2. 이유: 현재 강자의 실제 제출 기록인지 확인하고, 잘못된 action 추출을 전략 성능과 혼동하지 않기 위해서다.
3. 결과: metadata 3,023 submission/episode 행, 고유 2,722경기. 5경기 action 7,190/7,190·state projection 7,200/7,200·최종 reward 5/5 exact match.
4. 다음: donor route/state dependency 분석. 새로운 상대에서의 강도, K3 범위 결정, P1b HOLD 해소, license 검토는 이번에 해결한 것이 아니다.

## 고정 snapshot inventory

| 순위 | 팀 | 팀 점수 | 공개 활성 submission (점수; 72h episode 수) |
|---:|---|---:|---|
| 1 | Majkel1337 | 3204.0 | 56216119 (3189.9; 275) / 56156662 (3204.0; 218) |
| 2 | M & M & P & Q | 3103.2 | 56254996 (3103.2; 180) / 56254995 (3068.5; 158) |
| 3 | DSM | 3083.4 | 56267093 (3083.4; 105) / 56257064 (3065.0; 166) |
| 4 | SpaTaro | 3060.4 | 56263693 (2987.8; 127) / 56233892 (3060.4; 269) |
| 5 | Sida Zuo | 3054.0 | 56263637 (3035.1; 122) / 56257389 (3054.0; 161) |
| 6 | ymg_aq | 3026.9 | 56265958 (3026.9; 108) / 56265944 (3006.9; 108) |
| 7 | THIRD FARM CLUB | 3021.7 | 56279316 (676.7; 1) / 56255642 (3025.1; 161) |
| 8 | Orbital Terraformer | 3016.9 | 56263779 (3016.9; 120) / 56212726 (2999.1; 361) |
| 9 | Excluding | 3010.7 | 56267341 (3010.7; 100) / 56258178 (3009.5; 156) |
| 10 | Driz Lo | 3008.2 | 56277070 (2808.8; 35) / 56270137 (3008.2; 92) |

팀 점수와 개별 submission 점수는 순차 조회다. 현재 시각의 동시점 값이나 현재 이후 순위로 해석하지 않는다. API가 반환한 활성 submission 목록만 대상으로 하며, 모든 은퇴 submission 이력 확보를 주장하지 않는다.

## 원래 경기 재현

선택 규칙을 다운로드 전에 `selection.json`에 고정했다: snapshot rank 1/2, 각 팀의 반환된 submission 중 최고 점수, 최근 완료된 공개 경기 3개씩. 승패나 reward로 골라내지 않았다. 두 donor가 전략적으로 다른지는 미확인이다.

| episode | donor / submission / seat | 원본 최종 reward [seat0,seat1] | 결과 |
|---|---|---|---|
| 109675071 | Majkel1337 / 56156662 / 0 | [100050.0, 107191.0] | exact PASS / donor L |
| 109668602 | Majkel1337 / 56156662 / 1 | [137409.0, 138000.0] | exact PASS / donor W |
| 109662252 | Majkel1337 / 56156662 / 0 | [92403.0, 88762.0] | exact PASS / donor W |
| 109675071 | M & M & P & Q / 56254996 / 1 | [100050.0, 107191.0] | exact PASS / donor W |
| 109669865 | M & M & P & Q / 56254996 / 0 | [124471.0, 123135.0] | exact PASS / donor W |
| 109668692 | M & M & P & Q / 56254996 / 0 | [111477.0, 109683.0] | exact PASS / donor W |

109675071은 두 donor가 맞붙은 동일 경기다. 6개 donor view를 6개 독립 경기로 세지 않았다. Majkel1337은 이 표본에서 2승 1패, M & M & P & Q는 3승이며 이는 선택된 원래 경기의 결과다. 각 donor의 3개 전체 action hash가 모두 달라 하나의 고정 tape라고 단정할 수 없다. 이 차이가 state 대응·shop·잡초·별도 route 중 무엇인지는 아직 분석하지 않았다.

재현은 양쪽의 기록 action을 step+1로 실행했다. 720 step 전체에서 양측 day/hour/farms/market/player/private/town/reward/status를 exact 비교했다. 실행시간·remainingOverageTime·framework step bookkeeping은 비교에서 제외했다. 양쪽 최종 reward와 status도 일치한다. Runtime timeout 재현이나 원래 policy 복원 검증은 아니다.

## 경계와 보존

- 원본 파일은 private_artifacts/top10_donor_20260916/에 5개, 총 171,579,277 bytes. source code는 내려받거나 실행하지 않았다.
- API `competition_list_episodes`의 agents.submissionId/teamId/index로 donor와 좌석을 검증했다. opponent submission도 donor_manifest에 연결했다. episode 당시 rating은 N/A다.
- collection window 시작 뒤 완료된 metadata 1행(109681578)을 summary에서 제외했다. 원래 API 응답과 inventory는 보존했고 selected 5경기는 영향 없었다. collector는 후속 수집부터 endTime 조건도 적용하도록 수정했다.
- 공식 episodes-index archive 대신 Kaggle 공개 competition API에서 필요한 replay만 직접 받았다. 20GB 일괄 다운로드는 하지 않았다. replay 이용 근거는 저장된 공식 rules의 공개 replay/external data 조항이며 재배포 license 범위는 미확인이다. candidate에 넣기 전 확인하고 원자료는 공개 커밋하지 않는다.
- 이번 5경기는 development/reproduction 전용이다. 같은 episode 양측, 동일 donor submission 및 유사 행동 계보는 후속 독립 평가에서 제외해야 한다. 별도 평가 manifest는 아직 없음.
- 새 정책 구현·새 상대 arena·제출·다른 owner 파일 변경 없음. 독립 검증자의 별도 검토는 N/A.

## 실행한 검증과 재현 명령

```bash
python3 -m unittest tests.test_reproduce_replay
python3 -m py_compile tools/top10_donor_inventory.py tools/reproduce_replay.py tools/summarize_donor_inventory.py
python3 tools/reproduce_replay.py --replay private_artifacts/top10_donor_20260916/episode-109675071-replay.json --output /tmp/top10-reproduce-109675071.json
python3 tools/summarize_donor_inventory.py --directory experiments/results/top10_donor_20260916
python3 tools/validate_hypotheses.py --strict
```

- unittest: 5 tests PASS. generated 720-step round-trip, action step alignment/deep-copy, 손상 상태 검출, seed 누락 차단, projection의 private state 보존을 확인했다.
- compile PASS; summary provenance assertions PASS; strict ledger PASS (31 entries).
- 위 replay 명령을 선택된 고유 5개 ID 각각에 실행해 exit 0을 확인했다. 기존 106263397 fixture도 별도로 PASS.
- initial network 조회는 sandbox DNS 오류로 실패하여 승인된 network 실행으로 수집했다. Kaggle 제출·업로드 요청 없음.

## Artifact identity

- `experiments/results/top10_donor_20260916/summary.json` SHA-256 `58b0f40b76263fb7c93d7e3e745aa4565c5155388a89cfb196231bf66114b291`
- `experiments/results/top10_donor_20260916/donor_manifest.json` SHA-256 `ae55ea152f56268610e160f9a3f315289ca040456d2bff18bdbee2f883aebcd6`
- `experiments/results/top10_donor_20260916/selection.json` SHA-256 `1cd1e3d3c5da41d8b02f1cc351434d2f8f85227b3da69f25919f0b0c462d45d1`
- `tools/reproduce_replay.py` SHA-256 `9b1e879fda0a3b5a125510e674711af46cced469f9ae601d714247d39580fa29`

전체 metadata·재현 JSON SHA는 `file_hashes.json`, 원본 replay SHA는 `donor_manifest.json`에 있다. HYP-0013에 LOCAL 재현 사실을 기록했고 HYP-0010의 SOURCE_CLAIM 상태는 유지했다.

VERDICT | INVENTORY + ORIGINAL REPRODUCTION PASS | top10/20 submissions, 5/5 exact games | summary/manifest SHA 위 참조 | 5 unit tests + provenance assertions + strict ledger PASS | NEXT ACTION: route/state 분석 → 별도 독립 평가 카드

다음 행동 두 가지:
1. 두 donor에서 반복되는 build order와 달라지는 action의 조건을 분석한다.
2. K3/P1b 실행 조건을 확정한 뒤 donor와 겹치지 않는 평가자료로 후보 비교 카드를 만든다.


---

## `reports/codex/20260916-P1B-13EP-SCOPE-APPROVED.md`

# P1b — 사용자 승인 13경기 반영

1. 무엇: 원래 13경기와 seed·좌석·상대를 유지하고 사용자 승인을 manifest에 기록했다.
2. 왜: 수집/도구 검증 완료와 실제 preflight 실행 승인을 구분하고, 이미 결정한 범위와 검증자를 다시 묻지 않기 위해서다.
3. 측정: 경기 측정 N/A. 파일 검토와 JSON/identity 검증만 수행하며 기존 56 tests 결과는 재실행한 결과가 아니다.
4. 남은 일: 시간 기준 변경의 두 reviewer 최종 확인. actual tar 실행/추출/제출 없음.

VERDICT | SCOPE APPROVED / EXECUTION BLOCKED | 13경기 유지, Antigravity 지정 해소 | manifest `46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c` | JSON/identity 및 strict 검증은 아래 실행 기록 참조 | NEXT ACTION: 최종 runtime review 후 13경기 실행

## 정확한 경로와 변경 범위

- manifest: `experiments/results/p1_release_preflight/manifest.json`
- runner: `tools/instrument.py`, SHA `284dee4cdacfc56aab2125f8a92b41df53e14744cca7a8cafa10b853fb6d0629` (변경 없음)
- prior manifest: `experiments/results/p1_release_preflight/reviews/manifest-before-scope-approval-97ee06571346.json`, SHA `97ee065713465957e119c706b00f5b01c459d2c47dd0900a4bda9d3863af1019`
- Claude: `coordination/reports/claude/20260916-1745-P1B-CURRENT-MANIFEST-REVIEW.md`
- independent: `coordination/reports/antigravity/20260916-1746-P1B-INDEPENDENT-VERIFICATION.md`
- 사람 승인: 초안의 13경기로 진행

## Runtime 검토 제안

Claude의 parent별 623초를 유지하되 공유 episode wall-time <=960초(1200초의 80%)를 함께 제안한다. 623*2=1246초이므로 parent별 제한만으로 공유 예산을 보장하지 못한다. 실제 runner timing은 perf_counter elapsed time이며 CPU time 주장은 하지 않는다. shared 실패는 해당 실행 실패로 기록하며 parent 귀책이라고 단정하지 않는다. first call/p99/max는 측정만 한다. 아직 승인된 gate가 아니므로 실제 경기는 시작하지 않는다.

## 최종 검토 지시

Claude와 기존 Antigravity 채팅에 같은 지시 전달: 최신 manifest SHA `46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c`와 이 보고서를 읽고 parent별 623초 + 공유 episode wall 960초 이하 제안을 검토해. 13경기와 seed, Antigravity 지정은 이미 확정됐다. 승인 또는 구체적인 수정 근거를 별도 보고서에 기록하고 manifest 자체는 바꾸지 마. 실제 검사나 제출은 실행하지 마.

두 보고서가 같은 최종 SHA를 승인하면 Codex가 artifact/runner/engine/opponent hash를 재확인한 뒤 13경기를 전부 실행한다. 승인 레코드는 manifest 바깥에 저장해 hash 자기참조를 피한다.

## 이번 검증 결과

- JSON/manifest 대조 PASS: 기존 13경기·16 parent records·seed·좌석 보존, pinned 파일 11개 SHA 일치, resume SHA 일치, 실제 경기 출력 없음.
- `python3 tools/validate_hypotheses.py --strict`: PASS, 30 entries. 가설 내용 변경 없음.
- 전체 `git diff --check`는 타 작업의 docs/discussion 및 registry 기존 변경 공백에서 실패했다. 해당 파일은 수정하지 않았다. 이번 변경 경로로 제한한 검사를 별도로 실행한다.


---

## `reports/codex/20260916-VET-APPLY.md`

# 공개 자료 수집·마감 계획 독립 적용

작성 2026-09-16 KST. 사용자 요청의 두 작업을 collector agent와 plan agent가 나눠 구현하고, 별도 validator와 root integrator가 확인했다. 계획에 실행 항목을 추가한 것과 그 항목을 실제 수행한 결과를 구분한다.

1. **무엇을 바꿨는가:** 수집 실패 시 원문 보존·SDK field·reply 처리·SHA snapshot을 고쳤다. R10의 수확 신호 해석을 정정하고 P1에 source triage와 실제 parent tar release preflight를 넣었다.
2. **왜 바꿨는가:** 원문을 못 가져온 날 기존 자료까지 잃거나, 잘못 읽은 힌트로 새 전략을 만드는 일을 막기 위해서다. 제출할 수 없는 상태도 새 전략 개발 전에 발견해야 한다.
3. **측정 결과:** `[LOCAL]` collector regression test 13개 PASS, 가설 원장 strict PASS(30개). 새 hosted·전략 성능, 실제 API 수집·preflight 실행은 **N/A**다. 최종 독립 검증 및 파일 SHA는 아래 validation 기록을 따른다.
4. **다음:** 현재 계획 §5에 따라 source triage·hosted 패배 조사와 preflight manifest 확정을 진행한다. preflight FAIL/N/A이면 새 전략은 HOLD다.

VERDICT | APPLIED — 두 요청의 구현·계획 반영 | collector는 실패를 성공으로 보고하지 않음; P1 완료 파일·담당·중단 기준을 명시 | exact path/SHA는 `20260916-VET-APPLY.validation.json` | 아래 실행 검증 | NEXT ACTION: P1 수집·판독과 실제 preflight 준비

## 적용한 변경

| 요청 | 적용 파일 | 바뀐 동작 |
|---|---|---|
| 실패 시 원문 보존 | `scripts/fetch_kaggle_updates.py` | 조회·parse 실패 source는 last-good 유지, atomic file replace, manifest 저장 실패 시 기존 alias·inventory 복원 및 새 alias 제거. 복원 실패도 보고하고 exit 1 |
| 정확한 SDK 사용 | 같은 파일 | server top/recent 선정, votes/date/author field 수정, 반환된 nested reply 저장, 빈 raw_markdown이면 content 보존, 동일 topic/ref run당 1회 fetch |
| source 식별 | 같은 파일 | content SHA snapshot·source별 관측 history·raw response/kernel metadata 저장; source_only, unpinned source version·engine·license 미확인 구분 |
| 실패 회귀 검증 | `tests/test_fetch_kaggle_updates.py` | 일시 API 장애, 전체 listing 장애, reply, source 갱신, atomic replace·manifest 실패 등 regression test |
| R10 의미 정정 | `coordination/proposals/codex/20260914-community-trends-plan-update.md`, `docs/code.md`, 현재 plan | standing-MELON yield_units 합과 수확 readiness 구분. R10의 현재 재고 추가 SELL과 우리 shift/repay 가설 분리. 원래 제안에 정정일·근거·재현 명령 남김 |
| 문서와 collector 일치 | `docs/README.md` | 자동 요약·scheduler를 확인한 기능처럼 쓰던 설명 정정. 신규 archive/history의 범위와 댓글 completeness 미검증 명시 |
| 공개 자료 판독 계획 | `plan/kaggriculture_deadline_plan_20260915.md` §5.1 | 최초 09-16 18:00 KST, 이후 09-26까지 일별 변경분·watchlist·채택/보류/기각·HYP·owner 인수 파일, 09-27 전략 유입 cutoff |
| release 선행 검사 계획 | 같은 plan §5.2 | actual parent A tar의 schema 3 고정 manifest·제출 전 5줄·zero gate·독립 확인, FAIL/N/A면 새 전략 HOLD·correctness 경로 |
| 포인터·원장 | BOARD·HANDOFF·TASKS, updater event | 현재 작업을 P1a/b/c로 정렬. 기존 점수는 09-15 snapshot으로 유지. HYP-0012/0014/0016에 적용 기록을 연결하며 성능 상태 유지 |

§7은 제출 전 기존 A/B 관측과 C/A hosted causal N/A, 제출 후 B/C 또는 C/D window를 분리한다. FIFO·기존 승격 gate·사람의 제출 승인은 유지했다.

## 근거와 독립 검증

- [이전 통합 검토](20260915-independent-review.md)의 F1~F6 중 이번 두 요청과 직접 연결되는 항목만 반영했다.
- [collector 구현 보고](20260915-collector-apply.md): SDK 원본 위치, 출력 계약·한계와 fixture 명령.
- [plan 적용 보고](20260915-plan-apply.md): local link·artifact SHA·일정·기존 gate 보존 확인.
- 별도 독립 validator의 최종 보고는 [독립 검증](20260916-apply-independent-validation.md)이다. 실제 SDK object를 확인했고, legacy metadata 저장 실패 때 alias가 바뀌는 문제를 추가 발견해 구현자에게 반환했다. rollback과 관련 regression 3개를 보완한 뒤 최종 재검증했다.
- `[ENGINE]` R10 정정은 고정 `kaggriculture.py` SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`, lines 16·215–225·449–462와 notebook SHA `808210418de2cc24d1df643855c8055eeaceb1b0e442dc978e8007b195ddb9e7`, cell 2:1135–1162에 근거한다. 값이 양수인 것과 HARVEST가 가능한 것은 다르다.

## 실제로 실행한 검사

```bash
python3 -m unittest discover -s tests -p 'test_fetch_kaggle_updates.py' -v
python3 tools/validate_hypotheses.py --strict
git diff --cached --check
```

최종 출력·exit code·파일 SHA·문서 링크 확인은 `20260916-VET-APPLY.validation.json`에 보존한다. root도 collector test를 독립 재실행했다. SDK import/fixture는 API authenticate나 네트워크 수집을 하지 않는다.

## 적용 범위의 한계

- 실제 Kaggle 수집, archive 전체 backfill, source triage 표 작성, parent preflight 실행은 이번 변경의 수행 결과가 아니다. 이 중 P1 작업들은 **계획에 추가됐으며 실행 대기**다. 전체 과거 corpus provenance를 새 inventory가 복구했다고 주장하지 않는다.
- Notebook을 실행하지 않고 outputs/dependency도 수집하지 않는다. server가 반환하지 않은 댓글의 완전성은 N/A다. 원문 SHA가 바뀌면 요약·실험 근거를 별도 재검토한다.
- 파일별 atomic replace와 감지된 manifest 저장 실패의 rollback을 제공한다. 프로세스 강제 종료·정전에 대한 전체 파일 transaction이나 디스크가 복원 쓰기까지 거부하는 상황에서의 복구를 보장하지 않는다. rollback 실패는 run report로 남긴다.
- 자동 요약·watchlist 자동화·예약 실행은 만들지 않았다. 일별 계획과 scheduler 설치는 다른 작업이다.
- `docs/code.md`의 기존 미커밋 요약 변경은 보존했다. 이번에는 파일 맨 앞에 우선 적용되는 R10 정정문만 추가했다. 다른 원문의 전체 요약 재작성은 별도 triage로 남긴다.
- 기존 `docs/discussion.md`, `docs/latest_metadata.json`, `evidence/FACTS.md` 등 다른 작업의 변경은 이번 commit에 포함하지 않는다. 기존 Codex proposal은 정정 근거를 남긴 상태로 추적한다.

제대로 수집됐다는 표시와 전략에 쓸 만하다는 판단은 다르다. `complete`여도 license·engine·원문 내용과 우리 패배의 관련성을 확인해야 다음 카드로 넘어갈 수 있다.

다음 행동 두 가지: **① P1 source triage와 최신 hosted 패배 조사를 실행해 claim별 담당자 인수를 마친다. ② actual parent tar preflight manifest를 먼저 확정하고 실제 검사 결과에 따라 전략 또는 correctness 경로를 고른다.**


---

## `reports/codex/20260916-apply-independent-validation.md`

# 수집기·마감 계획 적용의 독립 검증

검증일: 2026-09-16 KST. 검증자: Codex `apply_validator` — 구현 코드를 직접 수정하지 않았다.

1. **무엇을 확인했는가:** 수집 실패 때 이전 원문을 지키는지, 실제 SDK 응답을 읽는지, R10 정정과 P1 선행 조건이 서로 맞는지 확인했다.
2. **왜 하는가:** 테스트용 가짜 응답에서만 작동하거나, 목록 저장 실패 뒤 목록과 원문이 서로 다른 버전을 가리키면 잘못된 자료가 다시 실험에 들어갈 수 있다.
3. **결과:** `[LOCAL]` 최종 13개 regression test, 실제 SDK object 기반 수집 fixture, 독립적인 legacy alias 재검증이 통과했다. 추가로 찾은 본문 fallback과 legacy pointer 보존 문제는 구현자가 수정했고 검증자가 확인했다. 전략 성능·실제 Kaggle 수집·actual-tar preflight는 N/A다.
4. **다음:** 통합을 막는 미해결 결함은 없다. root가 원장·최종 보고를 마무리한다. P1 실행 자체의 완료를 이 보고서로 대신하지 않는다.

VERDICT | **PASS — 적용 범위 독립 검증 완료** | 실제 SDK 직렬화 PASS · legacy alias 복원 PASS | collector SHA `2729ae529114e84b413c47a9a87db867f3c579ae51dad4fb60921e1fe1fe09bb` | 13 regression tests·독립 fixture·변경 대상 diff check PASS | NEXT ACTION: root 통합 및 P1 실행 인수

## 검증 범위와 판단

### V1 — SDK optional raw Markdown 처리: 수정 확인

`[LOCAL]` 설치된 `ApiTopicMessage.raw_markdown`은 미제공 값도 `''`로 반환한다. 따라서 `is not None` 검사로 content fallback을 선택하면 본문을 빼먹는다. root와 독립 검증자가 같은 문제를 확인했고, 구현자는 `raw_markdown or content or ''`와 regression test를 추가했다.

최종 source의 `fetch_discussion`에서 fallback을 읽고, **실제 SDK class**에 `content`만 넣은 응답으로 수집했다. 생성 Markdown과 raw JSON snapshot 모두 sentinel 본문을 보존했다. nested reply, API parent, timezone-aware datetime의 JSON 저장도 확인했다.

SDK primary source prefix: `~/.gemini/antigravity/brain/a8068519-c818-408b-8856-6802e8639fe9/scratch/venv/lib/python3.13/site-packages`.

- `kagglesdk/competitions/types/competition_api_service.py:5001` — raw_markdown default.
- `kaggle/api/kaggle_api_extended.py:3677` — topic server sort/page.
- 같은 파일 `:3768` — `page_size=-1`은 모든 top-level message 요청. 반환 완전성 보증은 아님.
- 같은 파일 `:6501` — kernel pull과 `code_file` metadata 생성. `os.listdir` 첫 파일을 고르지 않는 구현이 맞다.
- `kagglesdk/kernels/types/kernels_api_service.py:960` — 실제 kernel metadata fields.

### V2 — manifest 저장 실패 때 legacy pointer가 다른 bytes를 가리킴: 수정 확인

`[LOCAL]` 초기 수정본은 source alias를 먼저 교체하고 manifest를 나중에 저장했다. `latest_metadata.json` 저장 실패를 주면 exit 1과 오류 기록은 맞지만, 이전 metadata의 `path`는 새 source bytes를 가리켰다. 이전 entry에 `snapshot_path`가 없는 기존 corpus에서는 옛 bytes의 SHA snapshot만 남고 그 metadata와의 연결이 없어졌다.

재현은 정상 수집 후 code entry를 기존 `{ref,title,path,score}` 형태로 바꾸고, source를 변경한 뒤 metadata 저장에만 OSError를 주었다. 결과는 `exit=1`, `metadata_unchanged=True`, **`legacy_alias_unchanged=False`**였다. 이는 실제 Kaggle 장애가 과거 자료를 바꿨다는 주장이 아니라 파일 쓰기 장애 fixture의 결과다.

최소 보완으로 변경할 alias의 원래 bytes를 보관하고 manifest publish 실패 시 복원하며, 복원 자체가 실패하면 별도 오류로 남기는 방법을 전달했다. 파일 전체의 crash-atomic transaction이나 정전 복구 보장을 요구한 것은 아니다.

**수정 후 재검증:** 최종 구현의 `update_alias`가 original bytes/부재를 기록하고 `restore_files`가 manifest publish 실패 시 alias와 inventory를 복원한다. 신규 alias는 제거하며 rollback 실패는 오류로 남긴다. 추가된 세 regression test를 포함한 전체 13 tests가 통과했고, 위 독립 legacy fixture를 그대로 재실행한 결과 **`exit=1`, `metadata_unchanged=True`, `legacy_alias_unchanged=True`**였다. 이전 bytes의 snapshot도 유지한다. report를 쓸 수 없을 정도의 storage 장애나 프로세스 강제 종료까지 복구된다는 보장은 하지 않는다.

### V3 — 계획·R10·운영 문서: 적용 범위 PASS

- `[ENGINE]` R10 notebook cell 2:1135–1162와 engine `kaggriculture.py:16,215–225,449–462`를 직접 대조했다. MELON 초기 `yield_units=1`, HARVEST age 조건, R10의 age 미검사와 현재 shed 추가 SELL은 정정과 일치한다. maturity trigger·shift/repay를 별도 우리 가설로 분리했고 새로운 실험을 승인하지 않았다.
- `[LOCAL]` plan §5.1은 source triage의 담당, 시간, 출력 경로, 채택/보류/기각, HYP 확인, owner 인수와 cutoff를 정한다. 원문 수집을 검증 완료로 바꾸지 않는다.
- `[LOCAL]` plan §5.2는 actual parent tar·schema 3·실행 전 manifest·제출 전 5줄·zero gate·독립 검증을 요구한다. 미실행은 N/A이며 FAIL/N/A에서 전략 HOLD와 correctness 경로를 분명히 했다.
- `[LOCAL]` plan §6의 기존 paired score gate와 release zero gate를 낮추지 않았다. EXP-008 FAILURE와 재시험 금지도 유지했다.
- `[LOCAL]` plan §7은 A가 먼저 은퇴하는 FIFO를 유지하고, 제출 전 C/A hosted N/A와 제출 후 B/C 또는 C/D 관측을 구분한다. 사람의 제출 승인을 대신하지 않는다.
- `[LOCAL]` BOARD·HANDOFF_CURRENT는 같은 P1 선행 조건을 안내한다. README는 선택된 source 수집, 전체 corpus/watchlist, scheduler, 수동 요약의 경계를 구분한다.

R10 source SHA: `808210418de2cc24d1df643855c8055eeaceb1b0e442dc978e8007b195ddb9e7`.
고정 engine SHA: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`.
두 SHA를 이번 검증에서 재계산했다. source URL·수집일·정정 재현 명령은 `coordination/proposals/codex/20260914-community-trends-plan-update.md` 정정 절과 §1.2에 있다.

## 실행한 검증

```bash
python3 -m unittest discover -s tests -p test_fetch_kaggle_updates.py -v
python3 -m py_compile scripts/fetch_kaggle_updates.py tests/test_fetch_kaggle_updates.py
git diff --check -- scripts/fetch_kaggle_updates.py tests/test_fetch_kaggle_updates.py plan/kaggriculture_deadline_plan_20260915.md docs/code.md coordination/BOARD.md coordination/HANDOFF_CURRENT.md coordination/proposals/codex/20260914-community-trends-plan-update.md
```

최종 13 tests PASS, py_compile PASS, 변경 대상 diff check PASS. plan·BOARD·HANDOFF_CURRENT의 상대 링크도 모두 존재했다. 전체 working tree의 diff check는 기존 타 작업 파일 `docs/discussion/731215_Daily_Top_Episodes_Dataset.md` trailing whitespace와 `evidence/FACTS.md` EOF blank line 때문에 실패했으며, 해당 파일은 수정하지 않았다.

실제 SDK 추가 fixture는 API 호출 없이 위 SDK의 `ApiCompetitionTopic`, `ApiTopicMessage`, `ApiListTopicMessagesResponse`, `ApiListCompetitionTopicsResponse`, `ApiKernelMetadata`를 생성하고 test의 `FakeApi`에 응답으로 주입했다. 핵심 assertion:

```python
# root는 TemporaryDirectory, api는 실제 SDK object를 반환하는 FakeApi다.
assert collector.collect(api, root) == 0
entry = metadata['discussions']['top_voted'][0]
assert all(s in (root / entry['path']).read_text()
           for s in ('CONTENT_ONLY', 'NESTED_CORRECTION', 'API parent: 1'))
assert raw['messages'][0]['replies'][0]['rawMarkdown'] == 'NESTED_CORRECTION'
assert metadata['codes']['top_voted'][0]['listed_version'] == 7
assert metadata['codes']['top_voted'][0]['source_version'] is None
```

이 fixture는 PASS다. public notebook을 import/실행하지 않았고, source code는 temp folder의 문자열 fixture였다.

## 남는 경계

이번 검증은 선정된 source 수집기의 정확성과 계획 반영을 다룬다. 실제 API 연결 성공, server의 모든 댓글 반환, 과거 전체 corpus의 provenance 복원, scheduler 설치, 공개 source triage 산출물 작성, 실제 parent release preflight, 전략 성능 측정은 **N/A**다. `complete`를 전체 대회 자료 수집 완료로 확대 해석하지 않는다.

## 검증한 최종 artifact SHA-256

| path | SHA-256 |
|---|---|
| `scripts/fetch_kaggle_updates.py` | `2729ae529114e84b413c47a9a87db867f3c579ae51dad4fb60921e1fe1fe09bb` |
| `tests/test_fetch_kaggle_updates.py` | `27d40f442c77ef5531db0ca5858c7cf6eadd460891fc824e3bcf71072f2c391c` |
| `plan/kaggriculture_deadline_plan_20260915.md` | `df62f4b6405da86408f14bef4582812d0daad6f378ed7e3fe8b448bcc0f4f238` |
| `coordination/proposals/codex/20260914-community-trends-plan-update.md` | `4c655d6fa6f1c8c21849c8717151c42f7ea61a2e460d81e221756d0be2c9b082` |
| `docs/code.md` | `baa1b5576e181f79626abe98b9e9bb2bb8d19694ccfd7a3092145bfcf87f3fe0` |
| `docs/README.md` | `b734e331a7474155f747ff65e74a97fea9388533a0b22e520716681459848bb7` |
| `coordination/BOARD.md` | `5d31e77d27d8da7d4b2354f9f3002b7caaa942eef0a41ff62745565494b3b9cd` |
| `coordination/HANDOFF_CURRENT.md` | `e1b986674ee94a6d2c833e978775af8c4f74d95bb3023a99f88cd4c1212c9bf4` |

재현: 각 경로에 `shasum -a 256 <path>`. source/table 내용이 바뀌면 이 검증의 bytes 범위를 벗어난다.

다음 행동 두 가지: **① root가 이 검증과 원장 검사 결과를 함께 통합한다. ② 계획 §5의 실제 source triage와 사전등록된 parent preflight를 별도 작업으로 실행한다.**


---

## `reports/codex/20260917-1640-DONOR-ROUTES.md`

# 두 donor의 반복 순서와 행동 분기 분석

작성 Codex · 2026-09-17. **09-16 22:26 KST에 고정한 자료**의 분석이며 최신 순위 재조회가 아니다.

1. 무엇: Majkel1337 56156662와 M & M & P & Q 56254996의 각 3개 기록(고유 5경기)에서 기본 순서와 action 직전 상태를 비교했다.
2. 이유: 따라 할 수 있는 반복 구간과 상황에 맞춰 다시 판단해야 하는 구간을 구분한다.
3. 결과: Majkel의 농장 작업은 처음 25턴까지 3/3 일치. M은 같은 좌석 두 경기의 전체 action이 처음 25턴까지 일치하나 다른 좌석의 시작 구성은 다르다. Majkel의 자금 부족 후 추가 고용을 직접 관측했다.
4. 다음: 이 분석의 인과 해석을 독립 검토한 뒤 기존 계약에 맞는 좁은 실험을 설계한다. 새 전략 구현·대전·제출 없음.

**판정: 반복 opening은 있다. 그러나 전체 719회 행동을 고정 복사할 근거는 없다. 먼저 복제할 가치가 있는 대상은 opening과 ‘실제로 확보한 일꾼에 맞춰 행동을 바꾸는 구조’다. 후자는 donor의 내부 규칙을 복원했다는 뜻이 아니다.**

## 1. 자료와 측정 방법

- raw SHA·seed·좌석·상대 submission: `experiments/results/top10_donor_20260916/donor_manifest.json`.
- 해당 5경기는 직전 작업에서 원래 seed/configuration/양측 action 재현에 모두 PASS했다. 여기서는 다시 대전하지 않고 원본을 읽었다.
- 결과: `experiments/results/top10_donor_routes_20260916/analysis.json`. 아래 JSON 경로의 root는 이 파일이다.
- index `i`의 action은 `steps[i-1]`의 observation과 비교한다. `steps[i]`의 observation은 **결과**이므로 의사결정 입력으로 쓰지 않는다.
- 전체 719턴을 같은 index로 정렬해 farmer/hands/market/전체 action을 exact 비교했다. 이동 좌표의 회전/일꾼 순서 정규화나 동적 sequence alignment는 하지 않았다. 일치율이 낮다고 공통의 상위 전략까지 없다고 해석하지 않는다.
- 상세 context는 고정 focus index 1,20,25,26,27,73,145,150,169,217,220 및 pre-action day별 최초 divergence에 보존했다. 전체 불일치 index 목록도 있다.
- `opponent_previous_action_forensics_only`는 사후 replay 판독용이다. 상대 action이 agent observation에 직접 제공된다고 가정하지 않는다. 같은 턴의 상대 행동을 donor가 미리 알았다고 해석하지 않는다.
- 본문 [HOSTED]는 공개 hosted replay의 관측, [LOCAL]은 로컬 파서/재현 검증, [ENGINE]은 고정 1.32.7 소스, [INFERENCE]는 해석이다.

## 2. 반복되는 기본 순서

### Majkel1337 — 가축 5마리와 MELON/WHEAT opening이 고정

[HOSTED] 세 경기 109675071(seat0), 109668602(seat1), 109662252(seat0)의 공통 순서:

| replay index | 실제 요청/상태에서 확인한 공통 작업 |
|---|---|
| 1 | COW 1·WHEAT 5 구매 요청 |
| 2 | COW 운반, HIRE 4회, COW 1·SHEEP 3 추가 구매 요청 |
| 3~8 | 같은 좌표에 PASTURE 5개가 실제 생성됨; 가축 배치·먹이·CARE를 병행 |
| 11~23 | MELON/WHEAT 파종·급수 진행 |
| 23 종료 상태 | 세 경기 모두 COW 2·SHEEP 3·MELON 6칸·WHEAT 10칸 |
| 25 | HIRE 8회를 요청하되 실제 고용 수는 자금에 따라 다름 |
| 27 | FERTILIZER 판매 → 필요하면 추가 HIRE → WHEAT 구매 |

전체 action의 공통 prefix는 19턴, **farmer+hands 공통 prefix는 25턴**이다. 이후 같은 형태의 농장을 유지하더라도 일꾼·매매·확장 시점이 갈라진다. 세 경기의 첫 추가 토지 확보는 index 220/150/150, 다음 토지는 299/221/222다. 마지막에는 모두 3구획이다.

근거: `donors.Majkel1337.metrics`, `.profiles[].opening_actions`, `.actual_structure_creation`, `.milestones`, `.land_expansion`.

### M & M & P & Q — 좌석별 opening 후보와 이후 생산 구성 변경

[HOSTED] 같은 seat0 두 경기 109669865·109668692는 **첫 25턴 전체 action이 일치**한다.

- index 1: WHEAT 상품 1, WHEAT seed 11·CARROT seed 4·MELON seed 5, COW 3·SHEEP 2, HIRE 4회를 요청한다.
- index 3~20: 같은 좌표·순서로 PASTURE 5개를 만들고 작물을 배치한다.
- index 23 상태: 두 경기 모두 COW 3·SHEEP 2·WHEAT 11칸·CARROT 4칸·MELON 5칸.
- index 25: WHEAT 5 구매와 HIRE 2회를 요청한다. 이후 급여 담당 배분부터 다르다.

seat1 경기 109675071은 처음부터 COW 4·SHEEP 1·GOOSE 1, HIRE 3회와 WHEAT 13·CARROT 4·MELON 2 seed를 요청하고, index 23에 그 구성이 실제로 배치됐다.

**좌석과 opening의 연관은 관측됐으나 좌석별 규칙으로 확정할 수는 없다.** seat1 표본은 1개이고 내부 randomization·hidden state·config 사용을 구분할 수 없다. 초기 observation은 player/step/remainingOverageTime을 제외하면 세 경기 모두 같았다. 초기 자금 3000·상점 없음·시장 초기 가격도 같고 이전 상대 action도 PASS이므로 이 첫 차이를 ‘관측된 가격 충격에 대응’이라고 설명할 수 없다.

세 경기 모두 NW→NE→SW→SE로 확장했다. 두 번째 구획은 index 145/145/169, 세 번째는 217/217/217, 네 번째는 385/409/433이다. ‘가축+작물 배치 → 이후 수익으로 고용/생산 구성 변경 → 토지 확장’이라는 단계는 반복되지만, 세부 action과 시점은 고정이 아니다.

근거: `donors.M & M & P & Q.pairs`, `.profiles`, `.divergence_contexts.1`.

## 3. 행동이 달라진 순간과 자금·상점·상대

### A. 가장 강한 사례: 고용 부족 뒤 한 명 보충

[HOSTED+ENGINE] Majkel의 index 25 전후:

| episode / 상대 submission | 직전 cash | HIRE 요청 | 실제 hands 0→ | index 27 행동 |
|---|---:|---:|---:|---|
| 109675071 / M 56254996 | 7 | 8 | 4 | FERTILIZER 1 SELL → WHEAT 2 BUY |
| 109668602 / M 56254995 | 7 | 8 | 4 | 동일 |
| 109662252 / DSM 56257064 | 6 | 8 | 3 | FERTILIZER 1 SELL → **HIRE** → WHEAT 2 BUY |

상점은 모두 아직 열리지 않았다. 고용 가격은 1,1,2,3…이므로 4명에 7코인이 필요하다. index 26의 hands action도 실제 일꾼 수 4/4/3에 맞는다. DSM 상대 경기에서는 index 27에 hands가 3→4가 됐다.

[INFERENCE] 가장 가까운 설명은 ‘실제 인원 부족에 맞춘 계획 수정’이다. 다만 자금·인원을 조작한 counterfactual이 없어 donor의 if 조건을 식별한 것은 아니다. DSM이 정확히 어떤 거래 하나로 현금 1코인 차이를 만들었는지의 인과 귀속도 이번에는 하지 않았다. 이미 index 1 종료 cash부터 2466/2467/2464로 달랐으며 여러 거래의 누적 결과다.

근거: `.Majkel1337.divergence_contexts.25/.26/.27`; engine `kaggriculture.py:690-707`의 `_fib/_hire_cost/_do_hire`.

### B. 행동이 달라도 효과가 없는 사례: 실행되지 않은 추가 구매

[HOSTED+ENGINE] Majkel index 20에서 109675071만 WHEAT seed 1 뒤에 STRAWBERRY seed 1을 더 요청했다. 직전 cash 37에서 WHEAT seed 비용 10을 내면 27이다. STRAWBERRY seed 가격은 100이므로 살 수 없고, 실제 seed 재고도 0→0이다.

다른 경기들은 추가 요청 없이 cash 37→27, 36→26이다. 이 차이는 ‘딸기 전략을 더 빨리 시작했다’는 증거가 아니다. 같은 cash 37·같은 가격·상점 없음에서도 요청이 달랐으므로 단순 cash 조건만으로 설명할 수도 없다.

근거: `.Majkel1337.divergence_contexts.20`; engine `kaggriculture.py:15`, `:673-678`. **요청 횟수와 실제 구매량을 섞지 않는다.**

### C. 첫 상점 이후 서로 다른 생산 구성 — 연관은 있으나 원인은 미확정

[HOSTED] 같은 seat0 M의 index 73 직전과 요청:

| episode / 상대 | 열린 상점 | cash | 기존 농장 | 새 구매 요청 |
|---|---|---:|---|---|
| 109669865 / ymg_aq 56265958 | PIZZA_SHOP | 755 | COW3·SHEEP2·GOOSE1·MELON5·WHEAT10·CARROT4 | WHEAT seed4·CARROT seed3·COW1·HIRE4 |
| 109668692 / Driz Lo 56270137 | BRUNCH_SPOT | 732 | 위와 같은 개수 | WHEAT seed5·CARROT seed1·STRAWBERRY seed1·GOOSE1·HIRE5 |

이후 index 145 직전 첫 경기는 COW8·GOOSE1·STRAWBERRY3, 두 번째는 COW4·GOOSE3·STRAWBERRY9로 갈라졌다. PIZZA/BRUNCH에 따라 생산 구성을 바꾸는 가설과 일관되지만, cash·시장·상대·과거 작업·두 번째 상점도 다르므로 shop 하나의 causal effect는 N/A다.

더구나 같은 seat0 두 경기는 **상점이 생기기 전 index 26부터** 달랐다. WHEAT 5를 보유한 상태에서 farmer/hands 급여용 배분이 2/2/1 대 3/1/1이고, cash는 39 대 35다. 이 최초 분기를 상점 때문이라고 설명하면 미래 정보를 끌어다 쓰는 오류다.

근거: `.M & M & P & Q.divergence_contexts.26/.73/.145`. engine SHOPS product list는 `kaggriculture.py:103-113`.

### D. 확장도 cash만으로 설명되지 않음

[HOSTED] Majkel index 150에서 109675071은 cash 584·hands9·첫 상점 BAKERY이며 WOOL을 판다. 다른 두 경기는 cash 1973/2109·hands8이고 BUY_LAND를 한다. 하지만 첫 경기는 이후 cash가 충분한 순간에도 바로 같은 schedule로 들어가지 않고 index 220에서야 토지를 산다. ‘cash가 임계 이상이면 무조건 확장’이라는 단순 규칙까지 식별된 것은 아니다.

근거: `.Majkel1337.divergence_contexts.150/.169/.217/.220`과 `.profiles[].land_expansion`.

## 4. 일치율을 잘못 읽지 않기

| 비교: 세 경기 같은 index | Majkel | M |
|---|---:|---:|
| farmer+hands 모두 일치 | 46/719 | 11/719 |
| market 배열 일치 | 228/719 | 544/719 |
| 최소 한 경기에 market 주문이 있는 index 중 세 경기 market 일치 | 63/554 | **0/175** |

M의 market 544회 일치는 전부 세 경기 모두 주문이 빈 턴이다. 이를 ‘매매 전략 76% 동일’이라고 부르면 오해다. 이동·수량·작업자 배치가 다른 전략에서 raw action 일치율은 상위 build order 일치율을 대신하지 못한다.

## 5. 기존 KILL과 연결할 때

[HOSTED] M은 세 경기 모두 GOOSE를 실제 배치하고 네 번째 구획까지 확장했다. 이 표본의 세 경기는 승리했다. 이는 K9/K1을 모든 상위 정책에 일반화하기 어렵다는 **scope 재검토 자료**다. 그러나 거위·네 번째 땅을 뺀 같은 policy를 측정하지 않았으므로 각각의 승리 기여를 증명하지 않는다. `evidence/KILLS.md`는 이번에 수정하거나 해제하지 않았다. Claude owner가 현 조건·액션 예산 등과 대조해야 한다.

## 6. 다음 설계에 가져갈 것

- [INFERENCE] 가장 작고 설명 가능한 후속 후보는 Majkel의 opening 전체 이식보다 **고용 결과를 확인해 부족 인원과 그 인원에 의존하는 작업을 함께 복구하는 가설**이다. 기존 EXP-008의 fixed opening 변경 실패와 별개이며 효과는 새 카드로 검증해야 한다.
- [INFERENCE] M의 생산 배분을 따라 하려면 먼저 같은 좌석·같은 초기 route에서 추가 사례를 읽어야 한다. 3개 replay로 arbitrary state→action policy를 학습했다고 주장할 수 없다.
- 학습용 raw action을 그대로 타깃으로 삼으면 실패한 주문까지 복제한다. issued action·실행 결과·상태 복구를 구분해야 한다.
- 이번 표본을 개발 분석에 사용했으므로 최종 확인 평가 자료로 재사용하지 않는다. 추가 표본 수집은 별도 분석/사전등록으로 고정하고 ‘이전 검증 표본 늘리기’로 처리하지 않는다.

## 7. 검증·artifact

실행:

```bash
python3 tools/analyze_donor_routes.py --manifest experiments/results/top10_donor_20260916/donor_manifest.json --output experiments/results/top10_donor_routes_20260916/analysis.json
python3 -m unittest tests.test_analyze_donor_routes
python3 -m py_compile tools/analyze_donor_routes.py
python3 tools/validate_hypotheses.py --strict
```

분석 exit0, unittest 2 tests PASS(실제 tile 집계·pre/post 및 상대 과거/동시 action 구분), compile PASS. 고정 표본 assertion은 `validation.json`에 PASS 기록. 전체 manifest와 raw SHA도 파서에서 확인한다. 독립 reviewer 검증은 아직 N/A.

분석 JSON의 `analyzer_sha256`, `manifest_sha256`, `.profiles[].sha256` 및 `validation.json.analysis_sha256`로 계보를 잇는다. 가설 관련 기록은 updater만 사용하며 성능 우위 상태로 승격하지 않는다. 다른 writer의 `analysis/`, `FACTS`, `KILLS`, BOARD는 변경하지 않았다.

## 8. 다른 모델/새 채팅

현재 분석을 다시 수행하기 위한 모델 전환은 필요 없다. **구현 전 인과 해석의 독립 검토**는 새 채팅에서 하는 편을 권한다. 대안 모델은 GPT-5.6 Sol, reasoning high를 제안한다. 이는 작업 범위에 대한 판단이며 이번 작업에서 모델 간 성능을 비교한 결과는 아니다. 공식 문서는 Sol을 복잡한 전문 작업용으로 안내한다: https://developers.openai.com/api/docs/models .

복사해 쓸 지시는 `coordination/proposals/codex/20260917-DONOR-ROUTES-INDEPENDENT-REVIEW.md`에 있다. 새 채팅을 자동 생성하거나 sub-agent를 실행하지 않았다.

VERDICT | DESCRIPTIVE ANALYSIS COMPLETE | Majkel 고용 부족/복구 관측, M 초기 차이를 shop 반응으로 해석 불가 | analysis/validation SHA 연결 | 2 tests 및 fixture assertions PASS | NEXT: 독립 해석 검토 → 좁은 가설 카드

다음 행동 두 가지:
1. 새 채팅에서 이 보고서의 관측/인과 구분을 독립 검토한다.
2. 통과한 관측 중 실제 인원에 맞춘 복구를 우선 가설로 정리하고, 실행 조건 확인 후 별도 카드로 검증한다.

## 2026-09-17 검증 증거 정정

위의 “고정 표본 assertion PASS” 및 “fixture assertions PASS”는 당시 실행 가능한 검증 파일이 없었으므로 재현 증거로는 불충분했다. 당시 synthetic unittest는 2개뿐이다. 사용자 제공 독립 검토는 DESCRIPTIVE PASS이며 causal effect/hidden policy는 미확정이다. 이번 보완은 `python3 tools/validate_donor_routes.py`로 raw 기반 검사와 재생성을 실행하고 expected/actual/입력 경로/명령을 validation.json에 기록한다. 상세 결과는 `coordination/reports/codex/20260917-1710-DONOR-VALIDATOR.md` 참조.


---

## `reports/codex/20260917-1710-DONOR-VALIDATOR.md`

# Donor validator 보완

VERDICT | DESCRIPTIVE PASS | raw 기반 검증 23 checks PASS, cash 변조 negative control exit1 | HYP-0032는 PLANNED, 카드 제안은 BLOCKED_DRAFT | NEXT: owner가 recovery semantics 확정

무엇을 바꿨나: validation.json을 실행 가능한 validator의 산출물로 교체했다. 각 check에 input/expected/actual/result와 실행 명령·validator SHA를 남긴다. 최초 보고의 불충분한 fixture 표현은 정정 이력을 추가했다.

[LOCAL] `python3 tools/validate_donor_routes.py`: exit0, 23 checks, DESCRIPTIVE PASS. raw identity, 표본6 views/5 unique games, pre/action/post alignment, issued market, cash/HIRE recovery, STRAWBERRY seed 무증가, 초기 observation 및 same-seat first difference, GOOSE/4구획/승리 동시 관측, analysis byte 재생성 확인. analysis SHA `dc2dce03f20b46e011757cce65366ca987f2a68a79a5b4b6bfcfdc1dabd7b4ac` 유지.

[LOCAL] `python3 -m unittest tests.test_analyze_donor_routes tests.test_validate_donor_routes`: 3 tests PASS. 새 integration test는 저장 analysis cash를999로 변조하여 raw alignment FAIL 및 exit1을 확인한다. 기존 synthetic tests는2개다. 재현에는 manifest가 가리키는 private raw replay5개가 필요하다. 이 validator는 독립 reviewer의 미제공11개 검증군을 재사용했다고 주장하지 않는다.

`python3 tools/validate_hypotheses.py --strict`: exit0,32 entries PASS.

[HYPOTHESIS] HYP-0032 / TEST-STATE-CONDITIONED-RECOVERY-PREREG 등록. proposal `coordination/proposals/codex/20260917-STATE-CONDITIONED-RECOVERY.md`에 parent, 근거 postmortem,4-cell diagnostic과 숫자 gate 제안, 미확정 recovery 정의를 기록했다. Claude 정본 카드 작성 전이며 candidate 구현·arena·submission 없음. P1b HOLD·K3·K1·K9는 변경하지 않았다.

관측된 복구와 복구의 승리 효과는 별개다. 늦게 고용한 hand의 위치·소지품·놓친 작업까지 맞춰야 route 복구를 시험할 수 있다.


---

## `reports/codex/20260917-1805-EXP013-CONTRACT-REVIEW.md`

# EXP-013 계약 검토

VERDICT: NEEDS_REVISION. parent 최종 action 정의와 daily-reset trigger를 포함한6개 계약 보완점을 확인했다. 실행/효과 N/A.

상세: coordination/proposals/codex/20260917-EXP013-CONTRACT-REVIEW.md.
검토 대상 카드 SHA 96f0278293d56fe50e639f273abe6eaf5f5987c334d9d037cde63c3874354fd6.
고정 parent tar main member SHA bba042e04cff32ab53be2c59c2f5cd9053c8de2bf31632e396ca8faa502896b2 직접 확인.
`python3 tools/validate_hypotheses.py --strict`: exit0,32 entries. static source inspection이며 replay46턴 등 전수 재계산은 하지 않았다.

카드·BOARD·instrument.py 변경 없음. HYP-0032는 updater로 검토 event와 다음 행동만 갱신. EXP-011 우선, EXP-013 §G BLOCKED 유지. 다음: Claude 계약 수정 → Coordinator bounded correctness 경로 명시 및 사람 승인.


---

## `reports/codex/20260917-COORDINATOR-CORRECTNESS-PATH.md`

# Coordinator correctness 실행 경로 제안

VERDICT: PROPOSAL COMPLETE / EXECUTION NOT AUTHORIZED.

사용자 요청: Coordinator로 실행 경로와 BOARD 변경안 작성, 아직 실행하지 않음.
산출물: coordination/proposals/codex/20260917-correctness-path/DECISION.md, BOARD.proposed.md, BOARD.patch, sources.json.

근거: 현재 마스터 플랜 §5.2에 이미 별도 correctness repair 경로가 존재한다. 따라서 새 전략 P2의 P1b PASS 조건을 없애지 않고 C0/C1을 구체화한다. EXP-011 결과별 EXP-013 조건, shared runner 순차 통합, 카드 owner 수정과 사람 승인 범위를 제안했다. EXP-011의 넓은 repair 금지와 EXP-013 §G 충돌은 owner 정정 전 유지한다.

검증: `git apply --check coordination/proposals/codex/20260917-correctness-path/BOARD.patch` exit0 (검사만, 미적용). `python3 tools/validate_hypotheses.py --strict` exit0,32 entries. BOARD SHA는 5d31e77d27d8da7d4b2354f9f3002b7caaa942eef0a41ff62745565494b3b9cd로 변경 전후 동일. source SHA는 sources.json에 기록.

실험 수0, baseline 재실행0, candidate/runner/카드/BOARD 정본 수정0. 새 hosted 조회 없음. 가설 상태 변경 없음. 계획은 효과 증거가 아니다.

다음: Claude가 카드6개 계약 결함 및 scope 문구 수정 → 사용자 운영 문서 검토·적용 결정. 실제 실행은 별도 지시를 받은 범위만 수행한다.


---

## `reports/codex/20260918-1842-P1C-BOUNDED-CLOSURE-SYNC.md`

# P1c 제한 검토 종결 — Coordinator 문서 동기화

1. **무엇을 바꿨는가:** `coordination/BOARD.md`의 P1c를 **“제한 검토 종료 — 이 자료에서 실행 가능한 수정 가설 미확보”**로 갱신하고, Gemini owner 문서용 exact 정정안을 proposal로 전달했다.
2. **왜 하는가:** commit `f64e37a`의 bounded review 결론과 Coordinator 정본의 기존 “재검증 대기” 상태가 충돌했기 때문이다.
3. **무엇을 측정했고 결과가 어땠는가:** 새 분석·경기·candidate·metadata 수집은 N/A. 기존 32/32 PASS 결과를 문서에 연결했고 `python3 tools/validate_hypotheses.py --strict`는 **exit 0, 32 entries PASS**였다.
4. **막힘과 다음 행동:** exact collection window/submission/artifact 연결은 계속 N/A다. raw replay 관측과 identity를 구분하며, 109831239 metadata 확보를 자동 최우선 작업으로 등록하지 않는다. P2 HOLD, release gate FAIL, EXP-013 미승인을 유지한다.

`VERDICT | P1c 제한 검토 종결 반영 | BOARD 0df85ca3…f15eba; Gemini proposal 3cdc6f33…f833681 | strict validation PASS | NEXT ACTION: 새 승인 또는 새 evidence가 있기 전 수정 가설·candidate 자동 생성 없음`

## 반영 내용

- `[ENGINE + HOSTED raw 관측]` 110106409/109802471 PLACE MILK 실패 주장을 반박 보고서에 연결했다.
- `[HOSTED raw 관측]` 109831239 STRAWBERRY5/WHEAT3 방치 주장을 반박 보고서에 연결했다.
- `[ENGINE + HOSTED raw 관측]` 109856629 action718 즉시 DROP 역전 대안이 당시 위치 제약상 불가능했음을 연결했다.
- 이 특정 설명의 반박을 HIRE recovery·접전 개선·donor 전략 전체의 기각으로 확대하지 않았다.
- exact window/submission 연결 N/A와 raw SHA에 고정된 pre/action/post 관측을 분리했다.
- Gemini 소유 `coordination/reports/gemini/20260918-P1C-ANALYSIS.md`는 직접 수정하지 않고 `coordination/proposals/codex/20260918-P1C-BOUNDED-CLOSURE-GEMINI.md`에 exact replacement와 철회 문구를 기록했다.

## 원장

기존 updater event `coordination/hypotheses/codex/EVT-2026-09-18T000144.056243+0000-9b1e9ec1.json`이 이미 HYP-0032 / TEST-0013에 동일한 bounded verdict, 세 반박, identity N/A, 전체 전략 비기각, EXP-013 미실행을 기록한다. Coordinator 상태 동기화를 위해 동일 내용을 중복하는 새 event는 만들지 않았다. `HYPOTHESES.md`의 기존 타 agent 미커밋 변경도 건드리거나 commit하지 않았다.

## 검증

- `python3 tools/validate_hypotheses.py --strict` → **exit 0, hypothesis ledger PASS: 32 entries**
- `git diff --check -- coordination/BOARD.md coordination/proposals/codex/20260918-P1C-BOUNDED-CLOSURE-GEMINI.md` → **exit 0**
- source evidence: `coordination/reports/codex/20260918-P1C-BOUNDED-EVIDENCE.md`, SHA-256 `85b77661a9760cbade2e24499f6547d83f87f2ed3a9b0e6a318be0c70faeea67`
- assertion JSON: `experiments/results/p1c_20260918_audit/bounded_evidence_assertions.json`, SHA-256 `688e4e50cc7f435eb4e013c72403373935d1c8f2b6404111f3e04faa0b01e80e`
- verifier: `tools/verify_p1c_bounded_evidence.py`, SHA-256 `63739b331af2c640c88dd942de8c8ede08486e75bba99782451e77305c71c0ab`
- reviewed source commit: `f64e37a24eeb052a9e5fa71cc2c9875d43e8f0b2`


---

## `reports/codex/20260918-2348-K3-WORDING-REVIEW.md`

# K3 wording 독립 검토

VERDICT  PASS (E1–E5 전 항목 PASS)

1. **무엇을 검토했는가:** rayk notebook 원문을 먼저 읽고, 이후 K3 결정안의 After 문구를 E1–E5별로 대조했다.
2. **왜 하는가:** K3를 넓게 적용했던 과거 판단과 분리해, 제안 문구가 원문과 `AGENTS.md` §9의 경계를 정확히 보존하는지만 판정했다.
3. **무엇을 측정했고 결과가 어땠는가:** 원문 cell 8·13·28·40·48·49·53, 결정안 §A-1~A-5·§B·§E, EXP-007 `main.py:614-666`, 실제 schedule의 market slot을 확인했다. E1–E5 모두 PASS다.
4. **무엇이 막혀 있고 다음 행동은 무엇인가:** 이 검토에서 막힌 항목은 없다. 적용 여부와 후속 변경은 승인된 owner가 수행하며, 이 보고서는 어떤 대상 파일도 변경하지 않는다.

## 항목별 판정

### E1 — PASS

- 원문 cell 48(`id=c94-strategy-search`)은 `complete market-tape grafts`와 `Copy a full rival market tape | Large generalization failure`만 말하고, cell 53(`id=c95-top20-counter`)은 `isolated rival market tape`가 coherent하지 않다고 재서술한다.
- After 1열은 금지 범위를 **market 주문 기록을 그 기록이 나온 경기와 다른 작업 경로에 붙이는 graft**로 한정한다. 같은 source episode의 farmer+hands+market 전체 재생은 K3 범위 밖이라고만 하고, 곧바로 `범위 밖이라는 것은 허용이 아니다`라고 제한한다.
- 원실험이 farmer/hands를 복사하지 않았다고 단정하지 않는다. After 2열에서 `graft 대상 route · farmer/hands 처리`를 N/A로 두고, 결정안 §A-2도 이 범위가 원실험 구현 사실이 아니라 원문 단어에 근거한 **해석**임을 명시한다.

원문 한 줄: `I screened complete market-tape grafts` / `copying ... an isolated rival market tape is not coherent.`

### E2 — PASS

- cell 48에서 K3 후보에 직접 귀속 가능한 사실은 `[COMMUNITY]` 정성 결과, 양 좌석, new seeds뿐이다. 같은 cell의 `900 games over six new seeds`는 뒤의 held-out finalists 표에 붙은 수치이며, full-market-tape graft의 표본·W/L·margin으로 귀속할 수 없다. After는 이를 새 수치로 만들지 않고 N/A로 유지한다.
- 원문에는 K3 구현, graft 대상 route, farmer/hands 처리, 상태 반응, 라이벌 신원, 평가 상대, seed 값·수, K3 표본 수, K3 실패 수치, 실패 기제가 없다. notebook setup은 `kaggle-environments>=1.32.4`만 요구하고 실행 output이 없어 exact 실행 엔진도 N/A가 맞다(cell 2, `id=code-02`).
- 2026-09-07 당시 notebook bytes 동일성은 N/A로 유지되고, K3와 cell 48의 대응도 문구 일치에 따른 `[INFERENCE]`로 유지된다(결정안 §A-1·After 3열).

원문 한 줄: `The experiments used both seats and new seeds throughout.`

### E3 — PASS

- After 5열은 재검토 조건을 만들어 넣지 않고 `근거 있는 재검토 조건 미정의`라고 적는다. `[ENGINE]` 또는 `[HOSTED]` 근거로 실패 기제를 식별한 뒤 owner가 조건을 정의하고 사람이 승인한다는 문장은 현재 KILL을 여는 조건이 아니라, 미래 조건을 정하는 절차다.
- 결정안 §A-4의 §9 대조는 정확하다: 엔진·상대군·구현·구체 재검토 조건이 N/A/미정의라 첫째 요구를 실질적으로 충족하지 못하고, `조건 없는 영구 금지는 없다`와는 **실질 충돌**한다. 반면 조건이 없어서 market-only graft를 카드에 쓸 수 없다는 처리는 §9 부활 차단과 일관된다.
- 따라서 D-2 α는 §9를 충족했다고 가장하지 않고, K3 한 행에 대한 명시적 예외 선택으로 기술되어 있다.

근거: `AGENTS.md` §9; 결정안 §A-3 5열·§A-4.

### E4 — PASS

- After 1열에 `범위 밖이라는 것은 허용이 아니다`가 명시되어 있다.
- §B BOARD 제안에도 `같은 episode 전체 donor 재생은 K3 밖이지만 **허용이 아니다** — P2 HOLD 적용`이 명시되어 있다.

근거: 결정안 §A-3 After 1열, §B.

### E5 — PASS

- `route_for()`는 block별 `POLICY` tree를 순회하며 public observation vector와 이전 route로 schedule을 선택한다(`releases/public-thomas-replay-router-v2-exact/main.py:614-627`). `agent()`는 `turn//72`로 block을 정하고 block이 바뀔 때만 `route_for()`를 호출한 뒤, 선택 route의 같은 turn farmer/hands/market을 낸다(`:649-666`).
- `market_order()`는 엔진 parser가 받지 못하는 slot을 `['SELL','WHEAT',0]`로 바꾼다(`:630-646`). 실제 5개 schedule을 전수 확인한 결과 market 길이 최댓값은 10으로 `[:10]`에 의한 실제 절삭은 0건이었다. 치환 대상은 `PASS` 25개와 수량 0인 `BUY_ANIMAL` 3개였고, 모두 engine `_parse_order()` 기준 파싱 불가였다.
- 결정안은 `turn 144 전환`을 확인된 사실로 쓰지 않고, 실제 전환 시점은 tree 내용에 달렸다고 명시한다(§A-5).

근거: `releases/public-thomas-replay-router-v2-exact/main.py:614-666`; installed engine 1.32.7 `kaggriculture.py:631-649` parser 대조.

## FAIL 대체 문구

N/A — FAIL 항목이 없다.

## 읽은 파일 SHA-256

| 파일 | 확인 SHA-256 | 요청/결정안 기록과 일치 |
|---|---|---|
| `AGENTS.md` | `f53bdcd455707f6aef33123f2c86c24e9e022befc1aed973d04fd51a955cae20` | 일치 |
| `evidence/KILLS.md` | `34f18435d713b4df0b6449c993b3cd4bd7b17e7135dfdd9a65628760d89660bf` | 일치 |
| `docs/code/raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb` | `a7447511510ed22b73f2315246b6bf4de66f219ffe3ba692a377f3fb47931331` | 일치 |
| `coordination/proposals/claude/20260918-K3-DONOR-FINAL-DECISION.md` | `466aca3f427fecb8424b6b31e4cb3d5c94d87cdd6e57d6341bf38bb1cec69598` | 일치 |
| `releases/public-thomas-replay-router-v2-exact/main.py` | `8241246765098c50223d897739cb32076b71a303284d2e5e1c5f0fb495bb5a97` | 일치 |

## 검증

- 원문 선독: notebook cell 8·13·28·40·48·49·53 출력 후 결정안 열람.
- SHA 확인: `shasum -a 256`로 위 5개 파일 재계산.
- EXP-007 schedule 점검: 5 routes 전체 719-turn action의 market 길이·치환 대상을 읽기 전용으로 집계.
- 변경 범위: 이 보고서 1파일만 생성. KILLS·결정안·BOARD·가설 원장은 변경하지 않음.

NEXT ACTION 1: Claude/evidence owner는 승인 조건대로 K3 After 문구를 그대로 적용하되, 문구 변경이 필요해지면 자동 적용을 중지하고 사람에게 반환한다.

NEXT ACTION 2: Coordinator는 같은 적용 시점에 §B BOARD 문구의 `범위 밖이지만 허용이 아니다`와 P2 HOLD를 함께 보존한다.


---

## `reports/codex/20260918-EXP011-AUTHORIZATION.md`

# EXP-011 사용자 승인 기록

사람 지시: BOARD 변경안 적용과 EXP-011 §D-1의 범위 한정 승인. BOARD에 최신 카드 수정 상태 반영. EXP-011만 구현·검증·실행하고 결과 보고. EXP-013 구현과 실행은 하지 않음. 독립 결과 검토는 Antigravity에 맡길 수 있도록 보고서 준비.

승인자: 사용자. 기록일: 2026-09-18 KST (원 메시지의 정확한 wall-clock 시각 N/A; 날짜 전환 뒤 작업 재개). Coordinator: Codex.
EXP-011 card SHA 8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e. EXP-013 r3 SHA dabe80a04f89a9f3bde9b8faff198a55108c1f4b1c4f1f809c3db2265ac0cd9f.

§D-1 범위 한정은 위 exact card에 대한 명시적 승인으로 발효한다. 카드 소유권을 보존해 Claude 카드의 승인 표를 직접 편집하지 않고 이 외부 승인 기록으로 연결한다. Claude는 이후 승인 표 반영 시 새 SHA를 기록하되 측정 당시 card SHA는 보존한다.

허용: BOARD 적용, EXP-011 계측·검증·동일13경기 attribution, 결과 보고 및 Antigravity용 handoff.
불허: EXP-013 구현/계측/실행, EXP-012 실행, 제출·공개·팀 변경. Antigravity의 검토 완료를 가정하지 않는다.


---

## `reports/codex/20260918-EXP011-COORDINATOR-CLOSURE.md`

# EXP-011 Coordinator 종결

VERDICT: MEASUREMENT REVIEW COMPLETE / EXP-012 CURRENT SCOPE CLOSED / NO NEW EXECUTION.

Antigravity 결과와 Claude owner adjudication을 확인하고 BOARD의 C0·HYP-0031·상단 요약을 갱신했다. raw13 cell/26 player-record의 rewards/statuses/steps/9 counters를 assert로 재검산해 mismatch0 확인. 역사적 REPAIR_AUTHORIZED는 보존하고 EXP-012의 final-transfer 순서/클램프 경로만 사전등록 불가로 종결했다.

추가 owner 정정 제안: 209×평균단가92.0=약19200은 검증된 coin 상한이 아니며 이 숫자로 causal 주원인을 배제할 수 없다. noop3488 actions/482 items의 비율은 가치비가 아니다. 상세는 coordination/proposals/codex/20260918-EXP011-CLOSURE-PRIORITY.md.

원본 aggregate SHA22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba, 검토 SHA cb4f4c9e4b1171a0424b678eaef4d72d0d0993853d43d192c7ce0655ed689e1d, card r3 SHA e47bb87b5aa2813f99105ac0e9d357c956c528ac823ae39010f02381d88fbe32 확인. card r2→r3 정정에 따른 freeze identity 차이는 정상적인 문서 revision이며 원 freeze를 변경하지 않는다.

`python3 tools/validate_hypotheses.py --strict`: PASS32 entries,exit0. `git diff --check -- coordination/BOARD.md`: exit0. 원 결과 JSON·runner·카드 변경 없음. 새 경기·새 hosted 조회·EXP-013 구현 없음.

다음은 최신 P1c에 기반한 HIRE/actionable-noop/접전 비교를 제안한다. 아직 미실행·미승인. 계측의 정확성과 다음 intervention의 가치를 구분한다.


---

## `reports/codex/20260918-EXP011-RESULT.md`

# EXP-011 — shed discard attribution 결과

VERDICT | **LOCAL ATTRIBUTION PASS / 카드 판정 REPAIR_AUTHORIZED / 독립 검토 대기** | 기존13경기·16 record의 reward와 핵심 counter 정확히 재현,482개 소멸 전부 귀속 | freeze commit `0a4b10f` | NEXT: Antigravity 검증 및 repair 해석 확인. EXP-013 미구현·미실행.

## 쉬운 설명

agent를 바꾸지 않고 물건이 사라지는 순간을 자세히 기록했다. 원래 경기와 결과가 같아 계측 때문에 성능이 바뀐 흔적은 없었다. 482개 모두 하루 끝 창고로 옮기는 과정에서 사라졌고, 그중480개는 창고에서 떨어진 일꾼이 마지막 턴에 DROP/PLACE를 하지 않은 경우였다.

**그러나 위치나 마지막 행동이 소멸의 원인이라고 입증한 것은 아니다.** 모든 소멸 event에서 남은 공간보다 들고 온 물건이 많았다. 엔진은 일꾼 위치와 무관하게 하루 끝 inventory를 창고로 옮기므로, 이월 순서만 바꾸면 어느 물건이 버려지는지는 바뀌어도 총 소멸량은 그대로다. 카드의 REPAIR_AUTHORIZED는 지정된 후속 수정안을 설계할 자격이며 실제 수정 가능성·효과 증거가 아니다.

## 승인·identity

- 사용자 승인: `coordination/reports/codex/20260918-EXP011-AUTHORIZATION.md`. BOARD 및 §D-1 scope 한정, EXP-011 구현·검증·실행만 허용.
- card r2: `experiments/cards/EXP-011-shed-discard-attribution.md`, SHA `8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e`.
- parent tar: `coordination/proposals/claude/exp006/submission.tar.gz`, SHA `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721`. 네 member SHA를 P1b manifest와 확인. agent 수정 없음.
- engine1.32.7 py SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`, config SHA `a82c89c1a2315b93f39775d8e025471a01b738647c9772658368ee6b1b6f4867`.
- P1b manifest SHA `46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c`.
- 새 runner `tools/instrument.py` SHA `ca64256f941f2098cafc531fc422363c5757995f721b449369ce72877a33fe28`, gate_contract 불변.
- 실행 전 freeze: `experiments/results/p1_shed_attribution/freeze.json`, 모든 입력30개 SHA·argv13개·환경 변수 포함. commit `0a4b10f` 후 실행. 종전 cleanroom을 같은 경로로 읽되 bytecode 쓰기를 꺼 기존 파일을 보존했다.
- EXP-013 r3 SHA `dabe80a04f89a9f3bde9b8faff198a55108c1f4b1c4f1f809c3db2265ac0cd9f` 불변. recovery counter 추가 없음.

## 구현한 계측

`tools/instrument.py`만 engine wrapper 동작을 확장했다. daily drop 전 inventory/shed/위치/실제 마지막 unit op를 저장하고, engine의 unit/item 순서대로 공간 배분을 별도 snapshot 위에서 계산했다. player별 drop_events·summary와 in-day DROP/PLACE 소멸 counter를 추가했다. 기존 counter와 release 판정은 그대로다.

- event.step은 action 실행 전 엔진 step `(day+1)*24-1`이다. raw replay row(action+post state) index와 혼동하지 않는다.
- 720 states는719 actions이며 마지막 호출은 step718. 일반 EOD는 day0~28까지29회/player다. gated16 records 합464 events.
- `unit_last_op`는 atomic PLANT 치환 후 engine에 전달된 op다. 마지막 턴 market에서 새로 고용돼 unit action 호출이 없으면 `NOT_CALLED`로 표기한다(정의는 freeze에 고정).
- `shed_full_turns_today`는 각 턴 market 처리 직후 한 번 sample. `sell_filled_last_turn`은 해당 market 처리의 실제 체결 증가량.
- class ROOM_ZERO/PARTIAL은 **event 시작의 전체 shed 점유**다. 각 unit 차례의 잔여 공간이 아니다. 이 차이가 repair 해석에 중요하다.
- 기존 unit wrapper의 인자 이름 순서를 engine signature에 맞췄다. 전달되는 positional 값 순서는 기존과 동일하며, 새 계측에서 board_size/day를 올바르게 읽기 위한 변경이다.

## 실행 결과 [LOCAL]

| 지표 | 결과 |
|---|---|
| 경기 |13/13,720 steps,DONE/DONE |
| 비교 대상 |self3경기 양쪽6 record + starter6 + target2 + control2 =16 |
| D1-a identity |mismatch0 |
| D1-b 완료 |누락/상태 위반0 |
| D1-c reward·9개 기존 counter |모든 cell/record 정확히 동일 |
| D2 소멸량 |event→record→총합482 일치, 보존식 위반0 |
| D3 필드 |null0, day coverage0~28 |
| D4 class |누락/중복/불일치0 |
| R runtime |agent total0.045884~0.122455초 <=623; episode wall1.669~2.796초 <=960,<1200 |
| 전체 검증 |1603 checks PASS |
| in-day DROP / PLACE loss |gated16 records에서0 /0 |
| 기존 release gate |16/16 FAIL 유지. 각 runner exit2는 예상된 기존 zero-gate FAIL |

| class | S1 (14 record) | S2 target (2 record) |
|---|---:|---:|
| ROOM_PARTIAL / REMOTE / NO_DEPOSIT_ATTEMPT |64 |416 |
| ROOM_PARTIAL / ADJACENT / NO_DEPOSIT_ATTEMPT |0 |2 |
| 나머지6개 |0 |0 |

지배 class의 S1 share=64/64=100%, S2 share=416/418=99.5215%, record별 단독 최다16/16. 카드 임계0.80/0.80/14를 통과하므로 **기계적 판정은 REPAIR_AUTHORIZED**다. 원 카드 임계·표본·class 정의 변경 없음. 단 독립 검토 전 자체 결과이며 EXP-012 구현 승인 아님.

## 사후 검산과 해석 한계 (preregistered gate에 추가하지 않음)

`check_allocation.py`는 저장된464개 event snapshot을 고정 엔진 `_drop_inventories_to_shed`에 넣어 deposited를 직접 대조했다. 전부 일치했다. 소멸이 있는44개 event에서 합482개는 모두 `max(0, carried_total - available_room)`와 정확히 같다.

예: target seat0 day15/step383: shed55, 빈 공간45, carried51, loss6. 시작에는 공간이 있었어도51개 전부를 넣을 공간은 없었다. 그래서 ROOM_PARTIAL을 "공간이 충분한데 engine 이월에 실패"로 읽으면 안 된다. 총 inventory·capacity가 고정된 최종 이월의 순서/클램프만 바꿔 총 소멸을0으로 만드는 것은 이 산술로 뒷받침되지 않는다. 다른 시점의 예치·판매/생산 변경은 별도 intervention이며 이번 카드가 측정하지 않았다.

또한 engine의 PLACE는 cap까지만 옮기고 초과분은 inventory에 보존한다. 카드 §A의 DROP/PLACE 둘 다 in-day 소멸이라는 서술 중 PLACE 부분은 정정 제안이 필요하다. 실제 fixture는 DROP overflow3, PLACE overflow손실0을 확인했다. 원 카드·gate는 변경하지 않았다.

## 실행한 검증 / 재현 명령

- `python3 -m pytest tests/test_instrument_exp011.py tests/test_instrument_exp008.py tests/test_gate_contract.py -q` →30 passed.
- `python3 -m pytest -q` →68 passed.
- `python3 experiments/results/p1_shed_attribution/run.py` →exit0,13경기 실행 및 카드 검증. 기존 run이 있으면 덮어쓰기 거부.
- `python3 experiments/results/p1_shed_attribution/run.py --verify-only` →exit0,PASS/REPAIR_AUTHORIZED, 경기 재실행 없음.
- `python3 experiments/results/p1_shed_attribution/check_allocation.py` →exit0,464 events/44 loss events/482 units 대조 PASS. 독립 reviewer 검증을 대신하지 않는다.
- `python3 tools/validate_hypotheses.py --strict` →exit0,32 entries.

raw cell, command stdout/stderr/exit, aggregate checks, freeze SHA는 `experiments/results/p1_shed_attribution/`에 있다. 정확한 산출물 SHA는 `file_hashes.json`에 기록.

## 다음

Antigravity가 identity/계측/D1~D4/R와 class→repair 해석을 독립 검토한다. Claude는 owner 문서 정정 제안을 확인한다. BOARD와 HYP-0031은 측정 PASS/독립 검토 대기로 기록하고 EXP-013은 실행 미승인을 유지한다. release zero gate와 hosted 효과는 각각 FAIL/N/A다.


---

## `reports/codex/20260918-P1C-AUDIT-VERIFY-GUARD.md`

# P1c replay audit and EXP-011 read-only verification

VERDICT: PARTIAL VERIFIED / P1c causal interpretation not accepted.

77개 저장 replay의 HIRE 체결을 다시 계산하고 EXP-011 verifier의 원본 덮어쓰기를 막았다. Gemini의 HIRE 100% 실패 주장은 잘못됐다. 접전 4경기의 점수는 맞지만 승패를 바꿀 개입의 효과는 미측정이다. 새 경기·candidate·제출은 실행하지 않았다.

## Replay audit

[HOSTED replay observation] `steps[i-1].observation → steps[i].action → steps[i].observation`으로 정렬했다. 처음 10개 market 주문의 HIRE 요청 수와 같은 action 전후 `hires_today` 증가를 비교하고 hands 길이 증가로 교차 확인했다. 일일 reset 턴은 unknown 처리하며 이번 표본에 unknown HIRE 턴은 0개다. 이는 HIRE 요청의 체결만 측정하며 요청하지 않은 계획 고용이나 누락 action은 측정하지 않는다.

| 결과 | 경기 | HIRE 실패 경기 | 미체결 HIRE 주문 |
|---|---:|---:|---:|
| W | 24 | 0 | 0 |
| D | 1 | 0 | 0 |
| L | 52 | 3 | 13 |

실패 경기: 109899313(8건), 110024392(2건), 110041385(3건). 패배에서만 관측됐다는 상관은 recovery의 효과를 입증하지 않는다.

Gemini 대표 사례 110024392 seat1의 row2 HIRE×5는 hands 0→5로 전부 성공했다. row3 hand index1 WEST도 [5,4]→[4,4]로 이동했다. 이 경기에는 다른 시점에 실제 HIRE 실패 2건이 있으므로 예시가 틀렸다는 사실을 경기 전체 성공으로 확대하지 않는다. NOOP 전체 100% 주장도 현 보고서의 정렬과 사례로는 수용할 수 없으며 전체 재계측은 이번 작업 범위 밖이다.

| 접전 후보 | seat | 우리 마진 |
|---|---:|---:|
| 109856629 | 0 | 0 |
| 110106409 | 0 | -10 |
| 109831239 | 1 | -92 |
| 109802471 | 0 | -422 |

네 경기 모두 HIRE 미체결 0건. -500≤margin≤0은 사후 목록 확인용 범위이지 사전등록 gate가 아니다. 10~100코인 네 경기라는 표현은 틀렸다. draw는 raw reward 동점이며 hosted tiebreak 승패와 구분한다.

77개 고유 replay와 W24/D1/L52는 확인했다. 하지만 수집 보고서가 가리키는 `episodes_{ID}_filtered.json`을 checkout에서 찾지 못했다. raw replay만으로는 submission별 46/31과 완료 시각에 따른 정확한 24시간 window를 재검증할 수 없다. 따라서 최신 window 전체를 대표한다는 주장은 보류한다. 입력 replay별 SHA/seed/seat/opponent/engine과 전 HIRE 사건은 아래 JSON에 기록했다.

재현: `python3 tools/audit_p1c_replays.py`
산출물: `experiments/results/p1c_20260918_audit/replay_audit.json` (script SHA 포함).

## EXP-011 guard

Claude proposal의 read-only 기본값 안을 적용했다. `verify(persist=False)`는 판정만 출력하고 파일을 쓰지 않는다. 실제 batch 완료 경로만 `persist=True`다. freeze와 역사적 file_hashes는 수정하지 않았다.

검증: `python3 -m pytest tests/test_exp011_verify_readonly.py tests/test_audit_p1c_replays.py -q` → 3 passed. identity 성공/실패 모두 write가 호출되지 않는 regression test와 HIRE 정렬/reset fixture다.

실제 `python3 experiments/results/p1_shed_attribution/run.py --verify-only` → exit 1, INVALID. 현재 card/runner가 측정 당시 freeze와 달라 예상되는 identity 실패다. 역사적 실험 결과의 무효화가 아니다. aggregate/freeze/commands/allocation_audit 4개 SHA 전후 동일. 상세: `experiments/results/p1c_20260918_audit/verify_readonly_check.json`.
원본 aggregate SHA: `22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba` (PASS / REPAIR_AUTHORIZED 보존).

## Handoff

1. Gemini: 수집 source metadata와 submission/episode/time 연결을 보존하고 올바른 pre/action/post 정렬로 HIRE/noop 판정을 정정한다. 구현 없는 비교 분석까지만 한다.
2. 정정 후 접전 4경기의 구체적 분기·실행 가능 action을 분석한다. 작은 마진 자체를 causal evidence로 쓰지 않는다. EXP-013 미승인, EXP-014 예약, P2/release gate는 그대로다.

## Artifact hashes and ledger

- `tools/audit_p1c_replays.py` SHA256 `e855226a15423e147cb36c4ef3611acb43328af84a50ea1526f26b88974dfa91`
- `experiments/results/p1c_20260918_audit/replay_audit.json` SHA256 `fa2efeb7b2704c1e6946443b863a1ccc3f34d10860a164b900222b94310c39bb`
- `experiments/results/p1c_20260918_audit/verify_readonly_check.json` SHA256 `a07dcc4ad48063db5d07eec41ef3b51d8895ee3206dea0ca0113fc3d653110f3`
- `experiments/results/p1_shed_attribution/run.py` SHA256 `883c4792d855dbed2fccfc0e16a83f608d820fc9a1d82c0489168d0df3d9de37`

`python3 tools/validate_hypotheses.py --strict` → PASS, 32 entries. HYP-0032의 다음 행동만 updater로 갱신했다. 공용 HYPOTHESES.md와 TASKS.md에는 이전 타 agent 미커밋 변경이 있어 이번 선택 커밋에서 제외하며 working tree에 보존한다. 전체 diff-check는 기존 타 owner docs/registry trailing whitespace 때문에 실패했으나 이번 선택 파일은 별도 확인한다.


---

## `reports/codex/20260918-P1C-BOUNDED-EVIDENCE.md`

# P1c 제한 증거 검토 — 2026-09-18

**VERDICT: 현재 근거 부족 — 이 자료에서는 실행 가능한 수정 가설을 확보하지 못함.**

종반 손실로 지목된 네 경기와 NOOP 측정 정의를 확인했다. 다음 실험을 잘못된 실패 사례에서 시작하지 않기 위해서다. `[HOSTED 관측 + ENGINE]` PLACE MILK 실패와 STRAWBERRY/WHEAT 방치 주장은 반박됐고, 다른 두 접전도 제안된 즉시 수정의 근거가 되지 못했다. 실제 잔여 WOOL 2개와 효과 없는 WATER는 확인했지만, 해당 경기를 만든 exact artifact 연결과 개선 효과는 N/A다. 새 경기·counterfactual 경기·candidate·EXP-013·네트워크 수집은 실행하지 않았다.

## 한 장 증거표

아래의 확정은 저장된 raw의 관측 또는 고정 엔진 동작에 한정한다. 별도 평가 결과가 아니다. 직접 근거의 `C`는 아래 재현 JSON의 `cases["episode:action index"]`다.

| 주장 | 확정·반박·미확정 | 직접 근거 | artifact 연결 상태 | 다음 결정에 주는 의미 |
|---|---|---|---|---|
| 110106409 seat0, action718 PLACE MILK가 실패했다 | **반박** | C110106409:718. farmer/hand4의 MILK 3/15가 각각 shed로 이동. 같은 턴 SELL MILK1000, 종료 MILK0. 현금 +1326은 MILK만의 매출로 분해하지 않음 | episode·seat·raw SHA 확인; submission부터 N/A | PLACE→DROP을 실패 수리라고 제안할 수 없음 |
| 109831239 seat1, STRAWBERRY5/WHEAT3이 끝까지 방치됐다 | **반박** | C109831239:718. SELL STRAWBERRY999/WHEAT9가 실제 주문 10칸 안에 존재, 각각 5→0/3→0. 719에도 0 | 동일 | 211coin을 최종 bank에 더하는 계산은 이미 판 재고를 이중 계산 |
| 109856629 seat0, action718에 DROP·선행 판매 가능, +2100 이상 | **부분 확정 / 대안 반박 / 효과 미확정** | C109856629:718/719. WOOL154→31은 관측. 하지만 718 직전 관련 재고 보유자는 [3,5]/[5,3]/[6,4]로 모두 shed 밖. 718은 이동, 719에 DROP·판매 | 동일 | 작은 마진0과 가격 하락은 수리 가능한 실패를 뜻하지 않음. 더 이른 경로 변경은 이번 검토 밖 |
| 109802471 seat0, action718 PLACE 실패가 422coin 손실을 만들었다 | **반박** | C109802471:718. 직전 bank117682/118101, 이미 -419. 직후121923/122345, -422. 당해 수입4241/4244, 차이는 -3. PLACE는 실제 예치 | 동일 | 종반 한 턴의 실패로 전체 열세를 설명할 수 없음 |
| True NOOP2670건·77/77이 엄밀한 개별 실패 측정이다 | **정의 불일치 확정; 전체 실제 빈도 미확정** | C109831239:167 hand1 WATER는 빈 타일에서 무효지만 다른 hand의 shed WHEAT21→22 때문에 미계수. blocked move 포함·farmer 제외 fixture도 PASS | 계측 코드 SHA 확인; 경기별 policy 연결 N/A | 이 숫자를 고칠 수 있는 손실·가치·필요 개발 규모로 바꾸지 않음. 전체 재계측 없음 |
| 기존 Codex: HIRE 실패는 3경기/13주문, 110024392 row2·3 반박 | **확정** | 기존 코드 호출 없이 77 raw의 HIRE만 재계산: W0/24,D0/1,L3/52, 13주문. C110024392:2 hands0→5, :3 hand1 WEST [5,4]→[4,4] | 각 raw hash 대조; window/submission N/A | HIRE가 흔하지 않다는 관측과 recovery의 causal effect는 별개. HIRE 전체 경로를 기각하지 않음 |
| 109831239 seat1 최종 WOOL2 잔여 | **확정; 수정 가설 선정 불가** | C109831239:719. shed10, SELL8, shed2. 다른 unit의 WOOL 증감 없음 | **episode→submission 연결 부재** | 구체적인 미판매 사례지만 수정할 코드가 미확정. -92를 뒤집는다는 증거도 없음 |

**범위 구분:** 무효 action의 존재 ≠ 실행 가능한 대안의 존재 ≠ 최종 손실 회수. 모든 경기에서 검출됐다는 통계 ≠ 패배 원인. 작은 최종 마진 ≠ 뒤집을 수 있는 경기. 이 네 접전은 결과를 보고 선택한 **가설 생성 표본**이며, 별도 평가 표본·수치 gate는 정하지 않았다. 반박은 표의 특정 구현 설명에 한정한다. HIRE·접전 개선·상위 donor 행동 활용 전체의 실패를 선언하지 않는다.

**종료와 다음 판단:** 추천 가설 0개, proposal 0개. 상위 donor 행동 활용을 다시 판단할 때 먼저 필요한 최소 자료는 **109831239의 seat1(Sian)을 정확한 submission ID에 연결하는 원본 episode-agent metadata 한 건**이다. 이를 기존 submission→보관 tar 원장과 연결해야 관측한 WOOL 잔여를 어느 구현의 수정 근거로 삼을 수 있는지 판단할 수 있다. 이 metadata 확보나 후속 artifact 검토는 실행하지 않았다.

---

## 재현 범위와 방법

- 검증 코드: `tools/verify_p1c_bounded_evidence.py`.
- assertion 결과: `experiments/results/p1c_20260918_audit/bounded_evidence_assertions.json`.
- `cases`에 각 episode·seat·raw SHA·action index·직전/직후 **전체 observation**·issued action·상대 issued action을 저장했다. `assertions`에는 expected/actual/PASS·FAIL, `recorded_unit_checks`에는 관심 unit의 실제 action 바로 전/후 상태가 있다. 큰 동일 값은 equality SHA로 압축했으며 원 상태는 cases/unit_checks에 남는다.
- 정렬은 오직 `steps[i-1].observation → steps[i].action → steps[i].observation`. 보고서의 모호한 Step717/718 표기를 action index로 통일했다. hand index는 0부터이며 unit index0은 farmer, unit index5는 hand4다.
- 이 raw들의 seat1에는 `step`이 없고 seat0에만 있다. shared `step`은 같은 row의 seat0에서 복원했다. 읽은 사례의 farms/market은 양 seat에 있다. 복원 함수는 shared 필드만 복사하고 **private/player는 반드시 해당 seat 것을 유지**한다. seat0 private를 seat1로 복사하지 않는 assertion을 포함한다.
- 전체 77개 pass는 **raw SHA·W/D/L·HIRE만** 검사한다. NOOP 정의는 실제 한 transition과 명시된 synthetic fixture로 확인했다. 77경기 NOOP 재계측 도구를 만들거나 실행하지 않았다.
- 엔진 `_apply_unit_action`을 복사한 직전 상태에 **원래 issued unit actions 그대로**, 엔진의 farmer→hands 순서로 적용한 지점은 다섯 곳뿐이다: 110106409:718, 109802471:718, 109831239:167/718/719. atomic PLANT 차단도 같은 seed snapshot 기준이다. 이것은 실제 action의 국소 검산이다. **interpreter·market·env.run·candidate·대안 action은 실행하지 않았다.**
- unit-stage inventory/tiles가 raw post와 일치하는지 확인하고, 각 PLACE 직후 shed 증분을 따로 기록했다. 턴 전체 bank 증가만으로 개별 unit의 성공이나 품목별 매출을 판정하지 않았다.

재현 명령(기존 결과 보존을 위해 stdout만 출력하거나 `/tmp`의 새 파일 사용):

```bash
.venv/bin/python tools/verify_p1c_bounded_evidence.py > /tmp/p1c-bounded-review-recheck.json
python3 tools/validate_hypotheses.py --strict
```

첫 명령 **exit0, 32/32 assertions PASS**. 모든 checked raw와 기존 audit 결과·계측 코드·engine SHA 전후 동일. 이 PASS는 아래 반박·관측 assertion의 성공이며 candidate 성공이 아니다. 엔진은 `kaggle-environments==1.32.7`, raw `module_version`도 다섯 사례 모두 1.32.7이다.

## Raw identity

파일은 모두 `evidence/raw/p1c_replays/episode-<ID>-replay.json`. 77개 전체 SHA는 결과 JSON의 `input_sha256`, HIRE 사건은 `hire_events`에 있다.

| episode | Sian seat / 상대 / seed | raw SHA-256 |
|---|---|---|
| 110106409 | 0 / wadia / 239360516 | `11906bf350aaa1926fbee9277879efa292f113b5f65eac4bcb33b1abe756f2b1` |
| 109831239 | 1 / T Hansda / 1076952679 | `707330a154ba707e869ca17fab08749f8caabfeaee084632908ed3d0eb5b3de8` |
| 109856629 | 0 / xiang156 xu / 115022097 | `a1f96287d59e2cd4b876b9f0ecacdb65bbeaaf65cdd22e818e5e5bf956d08c09` |
| 109802471 | 0 / Lazyman / 1389265183 | `c8a13021af817810876bb1faa7df5a8ceac79847c1589fdc32b45cc9efb67ed9` |
| 110024392 | 1 / IAMNAMNAM / 1387853967 | `028a559768e1c62ba5e4e8dadc11e603dab7732de2a095f6eab803ce70d46f47` |

각 raw의 `info`는 EpisodeId·TeamNames·Agents(Name/ThumbnailUrl)·seed를 제공한다. **submission ID·업로드 SHA·완료 UTC는 제공하지 않는다.** `configuration.seed`는 null이고 재현 seed는 `info.seed`다.

## 주장별 expected / actual / assertion

모든 행의 실행 명령은 위 첫 명령이다. observation 전문은 C키로 찾는다. 아래 expected는 보고서 주장이 참일 때 필요한 상태이며, assertion은 실제 결과를 반박 가능하게 고정했다.

| C키 | 직전 → issued → 직후 | 원 주장 expected / 확인 actual | assertion 결과 |
|---|---|---|---|
| 110106409:718 | row717(day29/hour21), farmer[5,4] MILK3·hand4[5,4] MILK15/WOOL4, shed0 → 양쪽 PLACE MILK1000; SELL MILK1000이 slot0 → row718(hour22) MILK0, hand4 WOOL4 유지 | 실패라면 두 PLACE의 즉시 예치량0 / **3와15**. unit stage shed18, post shed0. PRICE103→34. bank102546→103872는 전체 시장 합 | 두 개별 예치·raw post inventory·tile 일치 PASS |
| 109831239:718 | row717 shed STRAWBERRY5/WHEAT3 → slot1 SELL STRAWBERRY999, slot6 SELL WHEAT9 → row718 각각0, row719도0 | 끝까지 미매도라면 최종5/3 및 해당 SELL 부재 / **0/0·SELL 존재**. 총 market10칸으로 절삭되지 않음 | 5/3→0/0 PASS |
| 109856629:718 | row717 farmer[3,5] WOOL3/MILK3/EGG1, hand0[5,3] EGG2, hand1[6,4] WOOL10/MILK6/EGG4 → EAST/SOUTH/WEST → row718 [4,5]/[5,4]/[5,4]로 도착, 재고 유지 | 즉시 DROP 대안이면 action 직전 세 위치가 shed access / **셋 다 아님**. 기존 주문도 빈 market이 아니라 SELL CARROT1000000 | 위치 및 DROP 불가 PASS |
| 109856629:719 | 도착 후 DROP, SELL CARROT/MILK/WOOL/EGG → 모두 재고0, WOOL price154→31, bank61734→64656(양쪽 동일) | 가격 하락154→31은 참 / +2100 이상 선행 효과와 고정154 체결은 N/A | 가격·최종 마진0 PASS |
| 109802471:718 | row717 bank117682/118101 → PLACE MILK1000×2 및 WHEAT1000, SELL9종 → row718 bank121923/122345 | 직전 동점118101/118101, Sian 수입3822라는 주장 / **직전 -419, 수입4241/4244**, margin 변화 -3. MILK 각3/15 예치 | 기존 열세·수입·개별 PLACE 성공 PASS |
| 109831239:167 | row166 hand1[9,4] tile=None, inventory{} → WATER → row167 같은 위치·빈 tile·inventory{}; 다른 hand0 DROP으로 shed WHEAT21→22 | 엄밀한 개별 NOOP면 WATER를 포함 / 기존 audit WATER0. 원래 WATER만의 engine 호출은 상태 전체 동일 | 계측 누락 반례 PASS |
| 110024392:2/3 | row1 hands0 → HIRE5 → row2 hands5; row2 hand1[5,4] → WEST → row3[4,4] | 기존 오류 보고는 고용·이동 실패 / 실제 모두 성공 | 기존 Codex 반박 PASS. 이 경기의 다른 시점 HIRE2 실패는 유지 |
| 109831239:719 | row718 shed WOOL10 → SELL WOOL8(slot0), 다른 unit WOOL 변화0 → row719 shed WOOL2, price1, 최종 margin-92 | 최종 모든 제품 판매 가정이면0 / **2** | 실제 잔여 재고 PASS |

## 엔진으로 확인한 조건과 대안의 한계

기준 파일: `.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`, SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`.

- `:132-139` board10의 shed access는 **(4,4),(5,4),(4,5),(5,5)**. `:344-355` DROP은 그 위치에서만 가능하고 초과분은 버린다. `:393-411` PLACE는 shed access에서 지정 품목을 예치하며 초과분은 들고 남는다. “MILK이므로 PLACE 불법”은 틀렸다. 무조건 DROP으로 바꾸면 다른 품목과 용량 처리도 바뀌므로 같은 수정이 아니다.
- `:431-445` WATER는 PLANT tile이어야 한다. 109831239:167 hand1은 tile=None이므로 효과 없음이 확정된다. 대체할 작업의 경로·가치는 확인하지 않았으므로 개선 가능한 손실로 승격하지 않는다.
- `:545-628,652-660,940-947` unit action 다음 market, 주문 최대10칸, SELL은 shed에서 unit 단위로 체결·가격 갱신. 정적인 pre-price×수량은 실현 매출이 아니다.
- 109856629:718 대안은 자금0·품목 보유·주문 여유는 있어도 **위치와 unit당 한 action 제약을 충족하지 못한다**. 이동과 DROP을 같은 action에 넣을 수 없다. 가격 하락 관측은 원래 일정의 성능을 바꿀 수 있다는 증거가 아니다.
- 109831239:719에는 WOOL10이 이미 shed에 있고 현금77041, 주문1/10칸, market SELL에 unit 위치·비용 제약이 없다. 따라서 **현재 SELL8의 수량을 늘릴 수 있다는 국소 실행 가능성**은 엔진으로 확인된다. 그러나 source identity가 없어서 수정 위치는 N/A. 종료 price1에서 남은2개는 단순 산술2coin이지 -92 역전 근거가 아니다. market 영향·다른 상태에서의 판매 및 cash/routing 변화·W/D/L 회귀는 측정하지 않았다. 이 단서를 승인된 one_change나 효과로 표현하지 않는다.

## NOOP 코드가 실제로 세는 것

`tools/audit_p1c_noops.py` SHA `06002ba643e0fd79ff5cc05a8084d7e9a9d18b15e53fe848da00ce7c4f0669ee`를 그대로 읽고 함수만 호출했다. 수정하지 않았다.

1. **hands만** 순회한다. PASS, pre/post에 존재하지 않는 hand, seed-blocked PLANT를 제외한다. farmer는 plant 수요 계산에만 사용하고 NOOP으로 세지 않는다.
2. hand 위치, 해당 hand inventory dict, **그 hand의 직전 위치에 있는 tile**, farm 전체 shed와 seeds가 **턴 전체 전후** 모두 같으면 1을 더한다. 개별 unit 호출 직전/직후 비교가 아니다.
3. `_TILE_OPS`, `_MOVE_OPS`는 선언만 있고 판정 분기에 사용하지 않는다. 따라서 “단순 이동 불가 완벽 제외”는 코드와 다르다. synthetic 경계 WEST 한 건을 실제 감사 함수에 넣으면 `{'WEST':1}`이다.
4. 다른 unit·market·일일 처리의 shared 변화를 자신의 효과로 오인해 누락할 수 있다. 실제 C109831239:167의 확정 무효 WATER가 그 반례다. 따라서 `true_noop` 이름만으로 합법 여부·개별 기여·회수 가능 비용을 알 수 없다.

저장 `noop_audit.json`의 578+9+2083=2670 및 24+1+52=77은 **기존 산출물에 적힌 값**이다. 이번에는 77경기 전체 NOOP 빈도를 재검증하지 않았다. 코드 정의 불일치가 전체 경기에서 무효 action이 존재한다는 명제의 반증도 아니다. 올바른 표시: **정의 불일치 확정 / 실제 전체 빈도 미확정 / causal effect N/A**.

## Artifact 연결의 확인 범위

`analysis/20260918-P1C-COLLECTION-PLAN.md`는 원본 API 응답 삭제를 명시한다(SHA `9bdceba72162491f6b4527639b4a47e6f28704d0cc450086e761d7b927977c32`). 해당 경로들과 `private_artifacts/`, `evidence/raw/`, `experiments/results/`에서 `episodes_56165718.json`, `episodes_56175620.json`, filtered metadata를 찾지 못했다. **24시간 소속·submission별46/31은 N/A**. 파일 mtime이나 행동 유사성으로 대체하지 않았다.

보관 tar 두 개는 실제 bytes와 내부 member SHA를 읽었다. 다음 연결은 **기존 제출 기록과 로컬 archive 사이**까지이며 표의 다섯 episode에 연결한 것이 아니다.

| 기록상 submission | 보관 artifact / 실제 SHA | 내부 코드와 가능한 action 경로 | 이번 episode 연결 |
|---|---|---|---|
| 56165718 | `coordination/proposals/claude/exp006/submission.tar.gz` / `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` | main.py SHA `bba042e04cff32ab53be2c59c2f5cd9053c8de2bf31632e396ca8faa502896b2`, :126-137 base→layer. yh_base.py SHA `d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b`, :201-221 tape·guard·최종 liquidate(:183-191). actions.json SHA `17d503f2fd20d59f9c0f14024d1e74a8add8bb9b5561d4d908b45deecb5495ef` | N/A |
| 56175620 | `releases/public-thomas-replay-router-v2-exact/submission.tar.gz` / `8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180` | main.py SHA `8241246765098c50223d897739cb32076b71a303284d2e5e1c5f0fb495bb5a97`, :649-666 route→SCHEDULES→market_order | N/A |

업로드 연결은 `evidence/HOSTED_LEDGER.md`의 사람이 제공한 submission description/CLI 기록까지다. 이번에는 API를 다시 조회하지 않았다.

위 코드 경로는 bytes를 읽은 사실이며, 해당 episode의 action을 생성한 코드로 확정한 것이 아니다. 현재 루트 `main.py`를 대상으로 가정하지 않았고, policy 재실행이나 fingerprint 추정으로 빠진 identity를 채우지 않았다. raw 관측의 확정은 identity 불명이어도 유지한다.

## 원장과 종료

결과 포인터와 범위 제한은 updater로 기존 HYP-0032의 다음 행동에 추가했다. 기존 TEST-0013의 관련 증거 검토로 기록했으며 새 실험 ID를 배정하지 않았다. HYP status PLANNED·EXP-013 미실행을 유지한다. BOARD·FACTS·Gemini/Claude 문서·기존 freeze/결과는 변경하지 않았다.

검증과 선택 커밋의 결과는 아래에 기록한다. 시작 전부터 다른 agent의 미커밋 변경이 있던 HYPOTHESES.md/TASKS.md는 commit에 섞지 않는다.

최종 검증: `.venv/bin/python tools/verify_p1c_bounded_evidence.py` → **exit0, 32/32 PASS**; `python3 tools/validate_hypotheses.py --strict` → **exit0, 32 entries PASS**. 기존 HYP-0032/TEST-0013에 review context만 추가했고 status·card·gate는 그대로다.

- `tools/verify_p1c_bounded_evidence.py` SHA-256 `63739b331af2c640c88dd942de8c8ede08486e75bba99782451e77305c71c0ab`
- `experiments/results/p1c_20260918_audit/bounded_evidence_assertions.json` SHA-256 `688e4e50cc7f435eb4e013c72403373935d1c8f2b6404111f3e04faa0b01e80e`
- `coordination/hypotheses/codex/EVT-2026-09-18T000144.056243+0000-9b1e9ec1.json` SHA-256 `05331d49e721aa6e27c3f4aab39633966a0f723614734da0e5bfbe7ba3c95e37`

선택 커밋 대상은 위 신규 3파일과 이 보고서뿐이다. 기존 HYPOTHESES.md/TASKS.md의 타 agent 변경은 commit하지 않는다. owner 문서 정정은 이 보고서의 증거표로 전달하며 이번 작업에서 직접 적용하지 않는다.


---

## `reports/codex/20260919-1221-F0-PUBLIC-EXACT.md`

# F0 공개 notebook exact 재현·gate 결과

**무엇을 바꾸거나 시험했는가:** P1 alperen, P2 lynnsakurai, P3 tetsutani 공개 notebook의 제출물을 원문 그대로 deterministic tar로 재현하고, 후보마다 고정 22경기 gate와 고정 seed 2000–2009 round-robin을 실행했다. P4 mzcao7은 실행하지 않았다.

**왜 하는가:** 고정 donor tape 경로가 0/52로 막힌 뒤, 최신 공개 bot의 exact artifact를 hosted에서 측정하기 전 local identity/schema/runtime/isolation을 확인하기 위해서다.

**무엇을 측정했고 결과가 어땠는가:** 세 후보 모두 double-build identity, 22/22 720-step `DONE/DONE`, 예외 0, runtime, clean-room import를 통과했다. silent-failure counter는 기록만 하고 판정에서 제외했다. 진단 round-robin 종합 점수는 lynnsakurai 0.9667, alperen 0.7000, tetsutani 0.3333, yhay81-exact 0.0000이었다.

**무엇이 막혀 있고 다음 행동은 무엇인가:** 제출은 금지 범위라 실행하지 않았다. 세 tar 모두 archive 안에 별도 license 파일이 없어 License 판단은 Claude에게 넘긴다. P2 notebook의 기대 `main.py` SHA와 실제 unmodified `%%writefile` body SHA가 다르지만, work order §2에 따라 원문 표기 불일치로 기록하고 제외하지 않았다. 다음은 Claude가 License와 진단 순서를 검토한 뒤 사람에게 제출 순서를 제안하는 것이다.

`PASS_LOCAL_GATE | 3/3 exact 후보 22/22 완주·예외 0; round-robin은 진단 전용 | 아래 tar SHA | engine 1.32.7 bc8a5487…653e | NEXT: Claude License/순서 판정 → 사람 제출 여부 결정`

## 후보별 결과

| 후보 | tar 경로 | tar SHA-256 | gate 6줄 결과 | 22경기 예외/ERROR | p99 ms | 진단 round-robin 점수 | 비고 |
|---|---|---|---|---:|---:|---|---|
| P1 alperen | `releases/public-alperen-before-dawn-stock-cash-sales-exact/submission.tar.gz` | `cce494e5419f06028fa3fd19ddf0f2400e661427132c895664469f4fe6c5a9ec` | Identity PASS; Schema PASS; Runtime PASS; Isolation PASS; License DEFERRED_TO_CLAUDE; Ledger N/A | 0/0 | 5.189 | 종합 42/0/18, 0.7000 | source `main.py` SHA `87142c0e…43b39`; notebook 기대값 일치 |
| P2 lynnsakurai | `releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz` | `1178ffa0614673a58fb1ee5b2a44003eecd5640634d6f3471e84ac92c1fbf388` | Identity PASS; Schema PASS; Runtime PASS; Isolation PASS; License DEFERRED_TO_CLAUDE; Ledger N/A | 0/0 | 3.700 | 종합 58/0/2, 0.9667 | actual `main.py` SHA `cddf51ea…a94d`; notebook cell 7 기대 `d3bebf51…b1497` 불일치 기록, 원문 무변경 |
| P3 tetsutani | `releases/public-tetsutani-market-smart-farming-exact/submission.tar.gz` | `f5e41bd0ddad50a109f12381cc532cdc10b9e9d93dd6c6ab37cff47dfbc4916e` | Identity PASS; Schema PASS; Runtime PASS; Isolation PASS; License DEFERRED_TO_CLAUDE; Ledger N/A | 0/0 | 3.389 | 종합 20/0/40, 0.3333 | source `main.py` SHA `797d9bca…64e2f`; notebook 기대 tar/main SHA 모두 일치 |

`p99 ms`는 22경기 중 후보 player의 episode별 p99 최댓값이다. self-play 2경기에서는 두 seat를 각각 측정했다.

## Gate 6줄

세 후보에 공통으로 다음을 적용했다.

```text
Identity:  PASS — 독립 build A/B와 최종 release build의 tar SHA가 후보별로 동일
Schema:    PASS — root main.py, callable agent, 22/22 경기 720 steps·DONE/DONE, 예외/ERROR 0
Runtime:   PASS — max wall 3.317s, max agent 누적 0.524s; 80% 기준 960s/623.2s 이하
Isolation: PASS — 빈 폴더에 tar를 풀고 import main 성공; 외부 파일·network import 없음
License:   DEFERRED_TO_CLAUDE — tar 내 license 파일 없음; source attribution/license notice는 원문 그대로 보존
Ledger:    N/A — 제출하지 않음
```

엔진은 `kaggle-environments==1.32.7`, `kaggriculture.py` SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`로 `environment/ENGINE_LOCK.md`와 일치했다.

후보별 최대 runtime:

| 후보 | 최대 episode wall s | 최대 후보 agent 누적 s/player-episode | 최대 episode p99 ms |
|---|---:|---:|---:|
| alperen | 3.317 | 0.5240 | 5.189 |
| lynnsakurai | 3.168 | 0.4234 | 3.700 |
| tetsutani | 3.156 | 0.4188 | 3.389 |

## Silent-failure counter — 기록 전용

후보 22경기, candidate player-run 24개(self-play 양쪽 포함)의 합이다. 이 값들은 work order §3에 따라 gate 판정에 쓰지 않았다. `tools/instrument.py` raw JSON의 generic release verdict는 이 counter를 gate하므로 `FAILURE`로 표시되지만, 이번 F0 판정 정본은 `gate_summary.json`이다.

| 후보 | noop | shed_discarded | shed_unsold | orders_truncated | sell_unfilled | buy_failed | hire_failed | seed_blocked | hands mismatch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| alperen | 1,380 | 40 | 0 | 0 | 2,413,282 | 2 | 0 | 6 | 0 |
| lynnsakurai | 1,380 | 34 | 0 | 0 | 2,410,058 | 2 | 0 | 6 | 0 |
| tetsutani | 1,506 | 38 | 0 | 0 | 2,410,270 | 2 | 0 | 6 | 0 |

## 진단 round-robin `[LOCAL]`

고정 seed 2000–2009, 좌석 교대, 쌍당 20경기만 실행했다. 결과를 본 뒤 seed를 늘리지 않았다. 제출 허가/차단 근거가 아니다.

| A | B | A W/D/L | A score |
|---|---|---:|---:|
| alperen | lynnsakurai | 2/0/18 | 0.1000 |
| alperen | tetsutani | 20/0/0 | 1.0000 |
| alperen | yhay81-exact | 20/0/0 | 1.0000 |
| lynnsakurai | tetsutani | 20/0/0 | 1.0000 |
| lynnsakurai | yhay81-exact | 20/0/0 | 1.0000 |
| tetsutani | yhay81-exact | 20/0/0 | 1.0000 |

진단 순서는 `lynnsakurai > alperen > tetsutani > yhay81-exact`다. `[LOCAL]` 순서일 뿐 hosted 강도나 제출 승인을 뜻하지 않는다.

## Exact 재현·검증 자료

- 공통 builder: `tools/build_public_exact.py`
- gate 정본: `experiments/results/f0_public_exact_20260919/gate_summary.json`
- round-robin 정본: `experiments/results/f0_public_exact_20260919/round_robin_summary.json`
- raw gate JSON 9개와 raw round-robin JSON 6개: `experiments/results/f0_public_exact_20260919/`
- manifest: 각 release 디렉터리의 `manifest.json`

실행한 핵심 검증:

```bash
python3 -m py_compile tools/build_public_exact.py
python3 tools/build_public_exact.py <candidate> <independent-output-dir>  # 후보별 A/B + final, 총 3회
shasum -a 256 <A>/submission.tar.gz <B>/submission.tar.gz releases/<candidate>/submission.tar.gz
tar -xzf releases/<candidate>/submission.tar.gz -C <empty-dir>
(cd <empty-dir> && python3 -c "import main; print(callable(main.agent), main.agent.__name__)")
python3 tools/instrument.py --a <candidate-main> --b starter --seeds 1000 1001 1002 1003 1004 1005 1006 1007 1008 1009 --time-agent a --gate-agent a --json <raw>
python3 tools/instrument.py --a starter --b <candidate-main> --seeds 1000 1001 1002 1003 1004 1005 1006 1007 1008 1009 --time-agent b --gate-agent b --json <raw>
python3 tools/instrument.py --a <candidate-main> --b <candidate-main> --seeds 1000 1001 --time-agent both --gate-agent both --json <raw>
python3 tools/arena.py --a <A> --b <B> --seeds 10 --seed-start 2000 --json <raw>
```

## 경계

- Kaggle 제출: 실행하지 않음.
- 외부 dataset/replay 다운로드: 실행하지 않음.
- `BOARD.md`, `KILLS.md`, 실험 card: 수정하지 않음.
- `HYPOTHESES.md`: 아래 updater command만 사용하며 직접 편집하지 않음.
- P4 mzcao7: 실행하지 않음.

## 가설 원장

`HYPOTHESES.md`는 직접 편집하지 않고 지시된 updater만 실행했다.

```bash
python3 tools/update_hypotheses.py --agent codex --hypothesis-id HYP-0028 --test-id TEST-DONOR-ROUTES-20260917 --reason "F0 public exact builds" --set "다음 행동=외부 점수는 COMMUNITY로 두고 우리 submission ID로만 승격 + coordination/reports/codex/20260919-1221-F0-PUBLIC-EXACT.md"
python3 tools/validate_hypotheses.py --strict
```

- event: `coordination/hypotheses/codex/EVT-2026-09-19T032300.936149+0000-ff3b0582.json`
- validation: `hypothesis ledger PASS: 32 entries` (exit 0)
- 상태·결과 칸: 변경하지 않음

## 다음 행동

1. Claude가 세 후보의 License 표기와 P2 기대 SHA 불일치 기록을 검토하고, 진단 전용 순서를 바탕으로 사람에게 제출 순서를 제안한다.
2. 사람이 승인할 때만 선택한 exact tar를 제출하고 submission ID ↔ tar SHA ↔ episode를 Ledger에 연결한다.


---

## `reports/codex/20260919-1332-F0-LATEST-REBUILD.md`

# F0 P2·P3 최신 notebook exact 재빌드 결과

**무엇을 바꾸거나 시험했는가:** `docs/collection_snapshots/`의 지정된 최신 P2·P3 notebook에서 제출물을 원문 그대로 복원해 deterministic tar를 만들고, 후보별 고정 22경기 gate와 지정된 세 진단 비교를 실행했다.

**왜 하는가:** 기존 P2 제출본은 이전 수집본에서 만들어졌고 notebook 자체 기대 SHA와 달랐다. 최신 notebook의 self-check와 exact artifact identity를 먼저 맞춘 뒤, 기존판 및 최신 후보끼리의 제한된 local 차이를 확인하기 위해서다.

**무엇을 측정했고 결과가 어땠는가:** 두 후보 모두 notebook 기대 SHA와 일치했고, 독립 두 번 빌드와 release build가 같은 tar SHA를 냈다. 두 후보 모두 22/22경기 720 steps·`DONE/DONE`, 예외 0, runtime·clean-room import PASS다. 고정 진단은 P2-new vs P2-old `0/20/0`, P3-new vs P3-old `20/0/0`, P2-new vs P3-new `20/0/0`이었다 `[LOCAL]`.

**무엇이 막혀 있고 다음 행동은 무엇인가:** 제출은 금지 범위라 실행하지 않았다. tar 안에 별도 license 파일이 없어 License 최종 판단과 제출 후보 선택은 Claude 및 사람이 해야 한다. local 진단만으로 hosted 우위는 주장할 수 없다.

`PASS_LOCAL_GATE | 최신 notebook 기대 SHA 2/2 일치; 후보별 22/22 완주·예외 0 | P2 tar bf516d2f…b65d, P3 tar 3f252be7…81ef | exact build·runtime·clean-room·고정 60경기 진단 완료 | NEXT: Claude License/후보 판정 → 사람 제출 여부 결정`

## 후보별 결과

| 후보 | tar 경로 | tar SHA | main SHA | notebook 기대값 일치 | gate 결과 | 진단 비교 W/D/L |
|---|---|---|---|---|---|---|
| P2-new | `releases/public-lynnsakurai-farming-score-v2-latest-exact/submission.tar.gz` | `bf516d2f575a7de9ac9112a836a8791fa1a344408830a36a24182b7953f0b65d` | `99604be9332db3e6cc2167e7425587c2a77a69825ca5ca116de9a48f37f08364` | PASS — `main.py` 일치 | PASS — 22/22, 예외·ERROR 0, p99 max 3.834 ms | vs P2-old `0/20/0`; vs P3-new `20/0/0` |
| P3-new | `releases/public-tetsutani-market-smart-farming-latest-exact/submission.tar.gz` | `3f252be79997944c3b724e6577f1a68886a4a81377b4fbdeb0fdfa3db83081ef` | `f6a756cfb900b9d5f499905d596b63f1fde2445342ac4b1ae04e353739bd62d2` | PASS — tar·`main.py` 모두 일치 | PASS — 22/22, 예외·ERROR 0, p99 max 3.314 ms | vs P3-old `20/0/0`; vs P2-new `0/0/20` |

P2-old는 제출본 tar SHA `1178ffa0614673a58fb1ee5b2a44003eecd5640634d6f3471e84ac92c1fbf388`, P3-old tar SHA는 `f5e41bd0ddad50a109f12381cc532cdc10b9e9d93dd6c6ab37cff47dfbc4916e`다. 진단은 seed 2000–2009, 양 좌석, 쌍당 20경기만 실행했으며 seed를 늘리지 않았다. P2-new와 P2-old는 코드 SHA가 다르지만 이 고정 matchup에서는 모든 최종 bank가 같았다. 이는 정책 전체의 동등성 증거가 아니다.

## Gate 6줄

```text
Identity:  PASS — notebook SHA 고정, 기대 artifact SHA 전부 일치, 후보별 독립 build A/B와 release build의 tar SHA 동일
Schema:    PASS — root main.py, production loader callable, 후보별 22/22 경기 720 steps·DONE/DONE, 예외/ERROR 0
Runtime:   PASS — max wall P2 3.168s/P3 3.126s, max agent 누적 P2 0.422s/P3 0.398s, 80% 기준 960s/623.2s 이하
Isolation: PASS — 빈 폴더에 tar를 풀고 production loader로 callable entrypoint 확인; 외부 파일·network 불필요
License:   DEFERRED_TO_CLAUDE — tar 내 별도 license 파일 없음; 원문 source notice 보존
Ledger:    N/A — 제출하지 않음
```

엔진은 `kaggle-environments==1.32.7`, `kaggriculture.py` SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`로 lock과 일치했다.

## Silent-failure counter — 기록 전용

후보별 22경기, candidate player-run 24개(self-play 양쪽 포함)의 합이다. 지시서에 따라 gate 판정에서 제외했다. raw 계측기의 generic verdict는 이 counter를 hard gate하므로 `FAIL`로 보이지만, 이번 F0 판정 정본은 `gate_summary.json`이다.

| 후보 | noop | shed_discarded | shed_unsold | orders_truncated | sell_unfilled | buy_failed | hire_failed | seed_blocked | hands mismatch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P2-new | 1,380 | 34 | 0 | 0 | 2,410,058 | 2 | 0 | 6 | 0 |
| P3-new | 1,500 | 32 | 0 | 0 | 2,410,108 | 2 | 0 | 6 | 0 |

## 진단 비교 `[LOCAL]`

| A vs B | seeds / seats | A W/D/L | paired score | 평균 bank A / B | 평균 margin | errors |
|---|---|---:|---:|---:|---:|---:|
| P2-new vs P2-old | 2000–2009 / both | 0/20/0 | 0.5000 | 96,900.6 / 96,900.6 | 0.0 | 0 |
| P3-new vs P3-old | 2000–2009 / both | 20/0/0 | 1.0000 | 97,885.2 / 97,469.6 | +415.6 | 0 |
| P2-new vs P3-new | 2000–2009 / both | 20/0/0 | 1.0000 | 98,241.7 / 95,576.5 | +2,665.2 | 0 |

이 표는 제출 순서 참고용 진단이며 release 또는 hosted strength 판정이 아니다.

## 증거와 재현

- 입력 notebook:
  - P2-new `docs/collection_snapshots/farming-score-v2-a-better-approach/farming-score-v2-a-better-approach.ipynb`, SHA `2fbebaf26ff26d47b606d7d80bf205331fd9374ac1ec549a8837fb32dba60d9e`
  - P3-new `docs/collection_snapshots/market-smart-farming-kaggriculture/market-smart-farming-kaggriculture.ipynb`, SHA `17d587525c226205467ac00a9b61eb7631fa1a4c73d6ef44a2f76b9e3e879201`
- kernel metadata SHA:
  - P2-new `3676346e38990d32915bc3930372ab413c9028abc2c7103b9026b8e83085a98f`
  - P3-new `e02c5dccc0ce8561157d76c4985c999e7905e40a78b5667929d41a3a14d51bd0`
- gate 정본: `experiments/results/f0_latest_rebuild_20260919/gate_summary.json`
- 진단 정본: `experiments/results/f0_latest_rebuild_20260919/diagnostic_summary.json`
- raw gate JSON 6개와 raw 진단 JSON 3개: `experiments/results/f0_latest_rebuild_20260919/`
- builder syntax: `python3 -m py_compile tools/build_public_exact.py` — PASS
- build: `python3 tools/build_public_exact.py p2-new <output>` 및 `p3-new <output>` — 각 3회 동일 tar SHA, 기대 SHA PASS
- gate: `python3 tools/instrument.py ... --seeds 1000 ... 1009 --steps 720` 양 좌석 + self seed 1000·1001 — 후보별 22경기 완료
- 진단: `python3 tools/arena.py ... --seeds 10 --seed-start 2000 --steps 720` — 지정 3쌍 각 20경기 완료
- 제출: 실행하지 않음


---

## `reports/codex/20260923-ABSORPTION.md`

# ABSORPTION — 품목별 흡수량과 판매 timing

VERDICT | Q1 NUMERIC VERIFIED / 소비량에 맞춘 이월은 비추천 / EXP-018 DRAFT, 실행 전 조건 미충족 | MELON 72−30=42개 초과; 같은 수량 분산은 9품목 모두 상대 대비 순수입 악화 | parent `56941da238ccdc8f5286bf7e3191b6208ee3451306e06b74bb2660134a69fc33` | 저장 원자료 재검산 6,501 checks PASS | NEXT: Claude가 판매 순서 초안 검토, Antigravity가 E-2 자료·실행 조건 확정

이미 진행 중인 `analysis/absorption_20260923/`의 결과를 이어서 검토했다. 품목별 초과 판매를 먼저 확인하고, 같은 양을 나눠 팔 때 실제로 수입이 늘어나는지 살폈다. Q1 숫자는 검산됐지만 분산 판매는 상대에게 먼저 팔 기회를 주었고, 실제 창고·자금을 적용하면 생산까지 흔들렸다. 판매 순서만 바꾸는 WOOL 후보는 작은 진단 신호만 있으므로 채택·실행 승인이 아닌 카드 초안으로 남긴다.

## Q1. 시즌 흡수량과 우리 판매량 — 먼저 숫자

`[LOCAL]` seed **2142**, 우리 **seat 0 EXP-017**, 상대 **seat 1 OMW**, engine **1.32.7**, **719 actions / 720 states**. 최종 cash **104,150 / 104,360**, 우리 패배 **−210**. 주문 요청량이 아니라 성공한 `_commit_unit` SELL 수다. 재현 명령은 §검증, SHA는 §identity 및 `manifest.json`.

| 품목 | 실제 town 누적 흡수 A | 우리 판매 S | S−A | 양측 판매 | 양측 판매−A | 양측 BUY_PRODUCT | 양측 1 coin 판매 | 시장 재고 순증감 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| WHEAT | 606 | 410 | −196 | 820 | +214 | 274 | 0 | −60 |
| CARROT | 372 | 114 | −258 | 228 | −144 | 0 | 0 | −144 |
| TOMATO | 426 | 80 | −346 | 160 | −266 | 0 | 0 | −266 |
| STRAWBERRY | 534 | 247 | −287 | 494 | −40 | 0 | 0 | −40 |
| **MELON** | **30** | **72** | **+42** | 144 | +114 | 0 | 0 | +114 |
| EGG | 210 | 89 | −121 | 178 | −32 | 0 | 0 | −32 |
| MILK | 282 | 204 | −78 | 408 | +126 | 0 | 49 | +77 |
| WOOL | 174 | 137 | −37 | 274 | +100 | 0 | 44 | +56 |
| **FERTILIZER** | **0** | **332** | **+332** | 664 | +664 | 214 | 0 | +450 |

출처: `analysis/absorption_20260923/q1.json`, `baseline_fills.json`, `demand.json`. 원자료는 아래 identity 표와 manifest에 기록했다.

`[ENGINE]` 흡수량은 양 플레이어가 공유한다. 우리 혼자 A 이하를 팔아도 상대 공급과 합치면 초과할 수 있다. WHEAT는 양측 gross 판매가 A보다 214개 많지만 BUY_PRODUCT 274개 때문에 시즌 재고는 오히려 60개 줄었다. FERTILIZER는 town 소비가 없지만 플레이어 구매가 있으므로 흡수 0을 수요 0으로 읽으면 안 된다. 1 coin SELL은 시장 재고를 늘리지 않으므로 마지막 열은 `양측 SELL − 1 coin SELL − 양측 BUY_PRODUCT − A`다.

### seed2142의 실제 해금 일정

| 처음 관측된 step | shop | 누적 인스턴스 |
|---:|---|---:|
| 72 | PIZZA_SHOP | 1 |
| 144 | BRUNCH_SPOT | 2 |
| 216 | FARMERS_MARKET | 3 |
| 288 | FARMERS_MARKET | 4 |
| 360 | SMOOTHIE_SHOP | 5 |
| 432 | YARN_STORE | 6 |
| 504 | PET_CAFE | 7 |
| 576 | BRUNCH_SPOT | 8 |

출처 `verification.json:unlocks`. 같은 이름의 shop도 각각 센다. shop은 step%4=0, town center는 step%24=0에 소비하며 **step0도 포함**, 마지막 action은 step718이다. 예: WOOL은 step432..716의 72회×2 + center30 = **174**. MELON은 center30, FERTILIZER는 0. 특정 shop 한 개씩인 가상 시즌 표를 이 seed에 대입하지 않았다.

엔진 근거: 고정 `kaggriculture.py:103-118` shop·center 구성, `:728-748` 소비, `:860-891` 해금, `:941-946` market→consume→day-end 순서. engine 경로는 §identity. **Q1을 먼저 검산한 뒤 아래 Q2 결과를 사용했다.**

## Q2. 같은 수량을 실제 시점 / 소비 뒤 분산 시점에 판매

### 계산의 정의

`[LOCAL]` 각 품목을 **하나씩** 변경했다. (a)는 원래 양측 실제 체결 step·order slot·수량·engine 가격의 재생이다. (b)는 우리 그 품목의 원래 SELL 성공 수량을 원래 판매 step부터 대기열에 넣고, 직전 step에서 town이 소비한 수량까지만 다음 step에 판다. 사용하지 못한 소비량을 미래로 적립하지 않는다. 첫 원래 SELL slot에 넣고 해당 주문이 없으면 slot0에 넣으며, 10개 주문이 찼으면 기다린다. **step718에서 잔량을 전량 판다.** 상대 및 다른 품목의 원래 체결 시점·수량은 고정한다.

흡수량보다 많은 같은 수량을 시즌 안에 모두 팔면서 모든 턴의 흡수 cap을 지키는 것은 불가능하다. 따라서 마지막 flush는 cap의 명시적 예외이며, 이것을 숨겨서 '완전히 흡수량에 맞춘 판매'라고 부르지 않는다. MELON은 원래 판매까지 쌓인 72개 중 마지막에 53개, FERTILIZER는 332개 전부를 마지막에 판다.

이 비교는 **자금·shed를 완화한 가격 계산**이다. 상대가 새 가격에도 원래 수량을 사고팔 수 있다고 가정하며, 상대의 agent 재호출·반응을 모델링하지 않는다. 가격은 고정하지 않고 새 재고에서 재계산한다. 실제 순수입 증감은 BUY_PRODUCT 비용까지 포함한다. 품목별 변경을 동시에 적용한 결과가 아니므로 행들을 합산해 candidate 이득으로 쓰지 않는다.

| 품목 | 고정 우리 판매량 | (a) 실제 SELL 수입 | (b) 분산 SELL 수입 | b−a SELL 수입 | 우리 순수입 변화 | 우리−상대 순수입 차의 변화 |
|---|---:|---:|---:|---:|---:|---:|
| WHEAT | 410 | 15,988 | 16,031 | +43 | +28 | −243 |
| CARROT | 114 | 6,148 | 5,961 | −187 | −187 | −437 |
| TOMATO | 80 | 13,359 | 13,179 | −180 | −180 | −1,054 |
| STRAWBERRY | 247 | 42,381 | 43,519 | +1,138 | +1,138 | −359 |
| MELON | 72 | 14,267 | 13,183 | −1,084 | −1,084 | −4,257 |
| EGG | 89 | 4,657 | 4,661 | +4 | +4 | −5 |
| MILK | 204 | 13,445 | 12,745 | −700 | −700 | −3,352 |
| WOOL | 137 | 12,322 | 4,464 | −7,858 | −7,858 | −6,105 |
| FERTILIZER | 332 | 15,847 | 14,375 | −1,472 | −6,229 | −12,395 |

출처 `q2_fixed_fills.json`, `analyze.py::isolated`. 모든 실제 시점 가격은 원래 unit 체결과 일치하고, 두 조건의 판매 수량은 모든 품목에서 같다. **이 분산 규칙으로 회수한 초과 판매 손실은 확인되지 않았다.** 가격 하락 자체의 인과 손실을 고유한 숫자로 분해한 것은 아니며, 특정 timing 개입의 효과를 계산했다. 더 좋은 모든 timing 정책이 불가능하다는 결론도 아니다.

STRAWBERRY는 우리 수입 +1,138이어도 상대 수입이 +1,497여서 margin은 −359 악화된다. FERTILIZER는 SELL 수입 −1,472에 BUY_PRODUCT 비용 **+4,757**이 더해져 순수입 −6,229다. '가격 회복'만 보고 상대 수입과 조달비를 빼먹으면 방향을 잘못 판단한다.

### 창고·자금을 적용하면 같은 수량 가정도 무너진다

기존 `full_engine.json`을 보존했다. 원래 양측 farmer/hands/market **요청**을 재생하고 우리 target SELL만 위 규칙으로 바꾼 엔진 진단이다. baseline은 market 직전 state **719/719 일치**, 최종 cash와 체결 event 전체 일치로 기록돼 있다. 이 turn에는 새로 경기 실행을 하지 않았다.

| target | 우리 final cash 변화 | 상대 final cash 변화 | 실제 target 판매 | 미판매 대기 수량 |
|---|---:|---:|---:|---:|
| WHEAT | −51,144 | −36,141 | 394 | 16 |
| CARROT | −277 | +335 | 114 | 0 |
| TOMATO | −1,912 | +1,334 | 76 | 4 |
| STRAWBERRY | +495 | +1,661 | 245 | 2 |
| MELON | −19,803 | +13,060 | 54 | 18 |
| EGG | −374 | +244 | 89 | 0 |
| MILK | −1,927 | +9,930 | 204 | 0 |
| WOOL | −53,800 | +28,321 | 58 | 79 |
| FERTILIZER | −102,001 | +65,429 | 36 | 296 |

요청을 고정해도 cash·storage 변화 때문에 실제 체결·수확은 달라진다. 따라서 이 표는 **동일 수량 Q2의 대체물이 아니라 feasibility 경고를 주는 별도 진단**이다. 미판매 대기 수량은 원래 팔았을 수량과 새 실제 판매량의 차이며 전부 shed에 남아 있다는 뜻이 아니다. CARROT처럼 체결 수량이 보존된 경우도 slot 이동으로 다른 품목 가격이 달라져 품목만 계산한 −187과 전체 cash −277이 다르다.

`q2_fixed_fills.json:spread.virtual_shed_peak`는 가상으로 대기분을 더한 proxy로, WHEAT122/MELON159/WOOL117/FERTILIZER416 등이다. 실제 최대 shed 관측값이나 소멸량으로 인용하지 않는다. 가격 계산을 그대로 실행 가능한 wrapper라고 주장할 수 없는 이유다.

## Q3. 큰 손실 두 품목: 이월 대신 같은 턴 판매 순서

Q2에서는 **회수 가능한 양의 손실 상위 2개가 나오지 않았다.** 아래 두 품목은 분산 규칙이 만든 **우리 순수입 감소 상위 2개**, WOOL −7,858 / FERTILIZER −6,229다. 기존 보고의 '상대 공급 제거 상한 gap'(MILK42,678 등)과 이 순위를 섞지 않는다.

`[HYPOTHESIS]` append wrapper에서 다음의 작은 규칙은 표현 가능하다. parent 바이트, 생산 action, SELL 수량·step은 고정하고 **market의 처음부터 연속된 SELL 주문들 안에서만** target을 앞에 옮긴다. 첫 non-SELL 뒤는 건드리지 않는다. 같은 턴 BUY_PRODUCT가 있는 target은 제외한다. target 외 순서는 보존한다. 상수는 `WOOL_FIRST=1`, `FERTILIZER_FIRST=0`, master `ENABLE=1`뿐이다. 0이면 각각 비활성이다. cash를 쓰는 주문 위치와 주문 수를 바꾸지 않으며, 보유하지 않은 물량을 새로 요청하지 않는다.

| 따로 켠 규칙 | 바뀐 턴 | 우리 순수입 변화 | margin 변화 | 판단 |
|---|---:|---:|---:|---|
| WOOL_FIRST만 1 | 6 | +83 | +83 | 작은 가격 진단 신호; 카드 초안만 |
| FERTILIZER_FIRST만 1 | 16 | −382 | −702 | 비추천, 기본 0 |
| 둘 다 1 | 18 | −289 | −594 | 비추천, 묶지 않음 |

출처 `verification.json:priority_diagnostics`, `verify.py::fixed_market`. **고정 체결량·가격 계산**이고 full engine/candidate 성능이 아니다. WOOL 자체 수입 +101에서 다른 품목 −18을 빼면 +83이다. 조건부 margin −210→−127로 **여전히 패배**한다. 기대 BT 이득·새 seed W/D/L은 **N/A**다. 이 신호만으로 arena 실행을 추천하거나 SUCCESS라 하지 않는다.

parent는 이미 SELL을 앞에 보내지만 SELL 사이의 품목 우선순위는 보존한다(`main.py::_adv_frontload`). 따라서 WOOL 순서는 기존 기능의 단순 중복은 아니다. 구현할 경우 wrapper가 반환하는 최종 action을 parent의 `_RACE_STATE.prev_action`에도 맞춰야 한다. 그 기록이 내부 반응에 영향을 줄 수 있으므로 `farmer/hands`가 baseline과 계속 같은지는 실제 arena에서 별도로 검증해야 한다. 줄 수 예상 **30~60줄 [INFERENCE]**, 외부 의존 0, 현재 soft default를 넘길 이유 없음.

기존 HYP-0034 / EXP-015에는 SELL 순서 변경 뒤 패널 회귀 14/100이 기록돼 있다(`HYPOTHESES.md:448-459`). parent·trigger가 다른 구현이라 이번 WOOL 규칙의 결과를 대신하지는 않지만, 판매 순서가 후속 자금 규칙을 건드릴 수 있다는 경고다. 아래 guard 없이 '순서만 바꿔 안전하다'고 주장하지 않는다.

K8 MELON 회복 대기는 재권고하지 않는다. 이번 수치는 지정된 연구 질문의 사후 진단이며 K8 재개 조건 충족을 주장하지 않는다. K2 추가 선행·K3 rival market graft도 제안하지 않는다.

## Q4. 생산 변경 몫 / 판매 변경 몫 — 추정만

| 추정 조건 | 우리 순수입 변화 | margin 변화 | 해석 |
|---|---:|---:|---|
| 같은 생산·같은 판매량, WOOL SELL 순서만 변경 | +83 | +83 | 위 가격 진단. 실제 정책의 달성 가능 이득은 N/A |
| 같은 생산·같은 판매량, STRAWBERRY를 소비 tick 뒤로 이월 | +1,138 | −359 | cash가 늘어도 패배 차이는 악화 |
| 마지막 42 MELON 판매 unit을 같은 step/slot의 42 CARROT unit으로 가상 교체 | −5,805 | −6,993 | 생산구성의 효과가 아닌, 수량 1:1 가정의 가격 부분만 계산 |

마지막 행은 `[INFERENCE]`, `verification.json:production_price_only`. MELON 수입 14,267→7,412(−6,855), CARROT 6,148→7,198(+1,050). 상대 수입 변화도 반영했다. 이것은 한 주문 안의 일부 unit 품목까지 바꾸는 **가상 공급열**이며 legal market action 또는 가능한 작부계획이 아니다. 토지·수확일·yield·seed 비용·노동·fertilizer 비용을 다시 계획하지 않았으므로 실제 생산 변경의 이득은 **N/A**다. '42개 초과 → CARROT 42개로 교체하면 개선'이라는 산술은 이 제한된 계산에서도 성립하지 않는다.

생산 변경과 판매 변경은 상호작용하므로 두 행을 더해서 총 개선이라고 하지 않는다. **생산 구성 권고는 하지 않는다.** 다른 담당이 사용할 추정과 한계만 남긴다.

## 제약 점검

| 조건 | 이번 연구 / 초안의 상태 |
|---|---|
| step ≤0.5초, 예외0 (hard) | runtime candidate 미생성·미실행이므로 **N/A, 통과 주장 없음**. 초안은 측정 max≤0.5s 및 exception/fallback counter0을 요구. 초과 시 중단 |
| parent byte append only (hard) | parent 원본 SHA 재확인, 변경0. 후보를 만들면 `candidate[:len(parent)] == parent`와 SHA를 검증해야 함 |
| 외부 파일·network·환경변수 의존0 (hard) | runtime wrapper 설계 의존0; 후보 source/import clean-room 검증은 미실행. 분석 스크립트의 파일 읽기는 허용된 연구 범위 |
| arena 1회 ≤약1,000경기 (hard) | 아래 **720경기** 한 번만. 실패 뒤 상수 변경·재실행을 같은 카드에 넣지 않음 |
| 상수 분리 | master·WOOL·FERTILIZER 분리, 정식 후보에서는 WOOL만 켬. ablation 추가 경기 없음 |
| 약200줄 (soft) | 예상30~60줄, 초과 제안 없음. 실제 줄 수 N/A |

## EXP-018 사전등록 카드 초안 — 실행하지 않음

**DRAFT / BLOCKED_PREFLIGHT**. CANDIDATE-POLICY **E 전체를 읽고 E-2로 작성**했다. 이 문서는 설계 제안이며 `experiments/cards/`는 Claude 소유라 직접 쓰지 않았다. candidate/runner hash와 아래 hosted manifest가 아직 없으므로 frozen card가 아니며 실행 금지다.

### E-2에 맞춘 hosted 가중치

- 필요한 출처: 평가 대상과 **같은 rating 구간의 최신 EXP-016/017 hosted 경기**, episode/submission ID·수집 window·rating·분류 근거·manifest SHA가 있는 자료. arena 결과를 보기 전에 단일 window와 family mapping을 freeze한다.
- 현재 저장소에서 확인한 `analysis/c1_hosted_20260921/opponents.csv`는 **C1 구간이라 사용 금지**. `analysis/top_agents_20260923/`의 상위 3팀 자료 및 EXP-017 **로컬** 대조군도 대체 가중치가 아니다. 적합한 EXP-016/017 상대 지문 자료는 **N/A**. 이번 작업에서 다운로드하지 않았다.
- `share_f = 해당 family 경기 수 / window의 중복 제거 전체 경기 수`. episode 한 개를 한 family에만 배정한다. 복수 match 또는 식별 불가, 그리고 아래 패널로 효과를 측정할 수 없는 family는 보수적으로 UNKNOWN에 합쳐 기여0으로 둔다. 알려진 family만으로 다시 정규화하지 않는다.
- 각 seed s, family f에서 `d_sf = 두 좌석 평균(candidate 점수 − parent 점수)`; 점수는 W=1,D=0.5,L=0. `Δ_f = mean_s(d_sf)`. **40개 seed가 paired 표본 단위**, 80좌석을 독립 표본으로 부풀리지 않는다.
- `G = Σ share_f × Δ_f`. `z_s = Σ share_f × d_sf`, `SE(G) = stdev(z_s, ddof=1)/sqrt(40)`. 즉 family별 paired 차의 covariance까지 보존한다. family별 `SE_f=stdev(d_sf)/sqrt(40)`도 보고한다. 이 SE는 주어진 hosted 가중치에 조건부이며 hosted share 자체의 표본오차까지 포괄하지 않는다.
- E-2 통과는 **G > 2×SE(G)**. G가 양수여도 문턱 이하이면 판단 불가. UNKNOWN **>30%**면 결론 옆에 병기; **>40%**이면 이 식으로 제출 판단하지 않는다. 이 카드의 weighted SUCCESS도 판정 불가로 둔다. 같은 rating/window 자료 부재도 판단 불가이며 과거 C1로 대체하지 않는다.

```yaml
id: EXP-018
hypothesis_id: HYP-0016
test_id: TEST-ABSORPTION-WOOL-ORDER-20260923
status: DRAFT_BLOCKED_PREFLIGHT
design_and_verdict: Claude
execution: Antigravity
submission: human_only_separate_authorization
parent: releases/f0-omw-adv-exp017/main.py
parent_sha256: 56941da238ccdc8f5286bf7e3191b6208ee3451306e06b74bb2660134a69fc33
engine_version: 1.32.7
engine_sha256: bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e
candidate: N/A_until_Claude_accepts_and_source_is_frozen
candidate_sha256: N/A
runner_sha256: N/A
hosted_weights_manifest_sha256: N/A_required_before_execution
one_change: WOOL_FIRST 0 -> 1; append SELL-prefix stable priority wrapper
constants: {ENABLE: 1, WOOL_FIRST: 1, FERTILIZER_FIRST: 0}
fixed:
  - exact parent bytes including _ADV_LOOK=3 and all existing layers
  - SELL quantities and steps; order count and all non-SELL slot positions
  - no added SELL; no cross-turn backlog; no crop/animal/land/HIRE/feed changes
  - stable relative order of non-target SELL orders
  - same-turn BUY_PRODUCT target excluded
  - final action propagated to existing race bookkeeping
hypothesis: >-
  seed2142 parent loss -210; postmortem day26 step647 daily margin change -589.
  This was mainly STRAWBERRY timing, not proof that WOOL caused the loss.
  Absorption pacing worsened WOOL net -7858; same-turn WOOL priority instead
  gave price-only +83 across 6 changed turns, still a loss (-127).
  Test whether the small signal generalizes without production/funding regressions.
postmortem: analysis/fundamental_gain_20260923/exp017_2142_omw.postmortem.json
seeds: [2180, 2181, 2182, 2183, 2184, 2185, 2186, 2187, 2188, 2189,
        2190, 2191, 2192, 2193, 2194, 2195, 2196, 2197, 2198, 2199,
        2200, 2201, 2202, 2203, 2204, 2205, 2206, 2207, 2208, 2209,
        2210, 2211, 2212, 2213, 2214, 2215, 2216, 2217, 2218, 2219]
seats: [0, 1]
opponents:
  - path: releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py
    sha256: 10f58185b916392ca39697c83f67f455df81a74dfb6eb1aacd60fd81d50c9970
  - path: releases/f0-c1-adv-exp016/main.py
    sha256: 9d58536d37d02d2587072cd7465fb0244eb3e558cc72521d5c5ad07a94876013
  - path: releases/public-ozer-v53-exact/main.py
    sha256: 20fe549dd4573b9fd1dfb32a1782c205fa74f0edfdfd6cbe935079533e0a9d0e
  - path: releases/public-thomastschinkel-metav4-v13-exact/main.py
    sha256: 9d63494603f88219857a3101d7dc19cc750ded04e5886732ee428580326967d9
arena_budget:
  parent_panel: 320  # 4 opponents x 40 seeds x 2 seats
  candidate_panel: 320
  candidate_vs_parent: 80
  total: 720
  runs: 1
metric: W/D/L and E2 paired weighted score; cash/margin diagnostic_only
```

위 카드의 판정은 다음 숫자 기준으로 고정한다.

**direct seed 순승 정의:** 후보 vs parent 두 좌석 점수 합을 2로 나눈 값 q_s에 대해 `count(q_s>0.5) − count(q_s<0.5)`; 범위 −40..40. 기존 EXP-017 보고의 'seed 순승 +76'은 이 정의와 다르므로 가져오지 않는다.

판정 순서와 숫자 기준:

1. **INVALID / hard gate stop:** source identity mismatch >0, 정상 완료 누락 >0, exception(잡힌 fallback 포함)>0, max step>0.5s, candidate prefix mismatch>0, 금지 외부 의존>0. 단일 arena 중 첫 위반이면 중단하고 재튜닝하지 않는다. runtime은 계측 overhead를 구분하되 통과 주장은 전체 agent call max로 확인한다.
2. **FAILURE:** direct seed 순승 <0, 또는 패널 총 패배 `L_candidate−L_parent>0`, 또는 유효 hosted share≥0.20인 family의 `Δ_f<−0.10` 중 하나. 자료 부재를 family 통과로 처리하지 않는다.
3. **SUCCESS (모두):** hard gate PASS; direct seed 순승≥0; 패널 총 패배 증가≤0; 위 주요 family 회귀≤10%p; 적합한 frozen E-2 자료 존재; UNKNOWN≤0.40; **G>2×SE(G)**; 그리고 아래 fixed-production guard PASS.
4. **INCONCLUSIVE:** 유효하게 완료했고 FAILURE가 아니지만 SUCCESS를 충족하지 못함. 가중치 부재/UNKNOWN>40%/G≤2SE는 weighted 판단 불가로 병기. freeze 전 가중치 부재는 현재처럼 BLOCKED_PREFLIGHT이며 arena를 시작하지 않는다.

**fixed-production guard:** parent/candidate의 같은 seed·seat·상대에서 farmer/hands 및 non-SELL 요청 차이0, 실제 BUY_SEED/BUY_ANIMAL/HIRE/BUY_LAND/BUY_PRODUCT 체결 수량 차이0, PLANT/HARVEST/FEED/COLLECT 수량 차이0, 품목별 누적 SELL 수량 차이0, 추가 shed 소멸0, 추가 no-op0. 이 guard의 차이>0이면 판매 순서만의 해석은 **INCONCLUSIVE_SCOPE_DRIFT**로 두며 SUCCESS 불가. 상수 하나 바뀌어도 반응형 parent에서 downstream 생산이 바뀔 수 있기 때문이다. 이런 경우 생산 튜닝을 덧붙이지 않고 Claude에게 반환한다.

성공하면 Claude 독립 판정과 별도 release/runtime/isolation 검토로 넘긴다. 실패하면 exact 순서 규칙을 폐기하며 흡수량 가설 전체를 KILL하지 않는다. 불확정이면 표본 추가·threshold 완화·동일 카드 상수 변경 없이 종료한다. 비교 opponent의 runtime도 max를 보고하되 candidate 안전 gate와 분리한다. 처리량 18.2초/경기 가정 시 720경기 약 **3.64시간 [INFERENCE]**; 새 candidate의 실측 wall time은 N/A다. 별도 탐색 arena·ablation은 예산에 넣지 않았다.

## Identity, 검증, owner 인계

| 파일 | SHA-256 |
|---|---|
| `releases/f0-omw-adv-exp017/main.py` | `56941da238ccdc8f5286bf7e3191b6208ee3451306e06b74bb2660134a69fc33` |
| `releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py` | `10f58185b916392ca39697c83f67f455df81a74dfb6eb1aacd60fd81d50c9970` |
| `.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py` | `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` |

나머지 source/runner/result hash·크기는 `analysis/absorption_20260923/manifest.json`에 고정한다. Q1~Q4는 위 seed/seat/상대에 한정된 `[LOCAL]` 또는 명시한 `[INFERENCE]`다. hosted 결과·BT 개선은 N/A. 원본 markets snapshot은 **unit actions 이후 market 직전**이므로 action 직전 observation으로 바꿔 쓰지 않았다.

이번에 실행한 검증:

```bash
.venv/bin/python analysis/absorption_20260923/verify.py
python3 tools/validate_hypotheses.py --strict
```

- 첫 명령: **exit0, 6,501 checks PASS**. 원래 체결 records 일치, 718×9 시장 재고 전이 검산, 해금별 demand, Q1 재계산, Q2 저장값 재계산, 별도 전체 품목 가격 replay의 unit 가격 일치 포함. priority/production 가상 계산을 `verification.json`에 기록했다.
- 기존 `analyze.py`, `q1.json`, `q2_fixed_fills.json`, `full_engine.json`, `baseline_fills.json`, `demand.json`, `run.log`는 덮어쓰지 않았다. 기존 실제 엔진 진단을 재실행하지 않았다. 재현 원명령은 `.venv/bin/python analysis/absorption_20260923/analyze.py`이나 이 명령은 기존 산출물을 다시 쓰므로 이번 resume에서는 사용하지 않았다.
- `python3 tools/validate_hypotheses.py --strict`: **exit0, 36 entries PASS**. 연구 TEST-ABSORPTION-20260923은 HYP-0003, 판매 slot 초안 TEST-ABSORPTION-WOOL-ORDER-20260923은 기존 판매 timing 주장 HYP-0016에 연결했다. 두 넓은 가설 상태는 INCONCLUSIVE 유지. immutable events: `coordination/hypotheses/codex/EVT-2026-09-23T143426.703673+0000-9a4a580e.json`, `EVT-2026-09-23T143426.793985+0000-eb6aef3a.json`.

BOARD 표제는 09-20이고 현재 날짜와 2일 이상 차이나며 본문 상태도 섞여 있다. **Coordinator에게 상태 동기화를 반환한다.** 이번에는 사용자가 직접 지정한 09-23 연구 지시의 제한 범위만 이어 수행했으며 stale BOARD를 새 실행·제출 근거로 쓰지 않았다. FACTS owner에게는 Q1의 seed별 해금·flow와 'gross 판매−town 소비만으로 가격 손실을 판단할 수 없다'는 계산을 인계한다. BOARD/FACTS/KILLS는 수정하지 않았다.

제출·Kaggle 다운로드·releases 편집은 0. runtime candidate·2180..2219 arena도 미실행이다. 완료 범위는 숫자 연구와 카드 초안이며 candidate hard gate 통과와 구별한다.

다음 행동 두 가지:

1. Claude가 **소비 cap은 비추천, WOOL 순서 초안은 신호가 약함**이라는 결론과 E-2 기준을 검토하고 BOARD를 동기화한다.
2. Antigravity는 승인된 경로로 준비되는 **같은 rating 구간의 EXP-016/017 hosted 지문**과 candidate/runner freeze를 먼저 확인한다. 그 조건과 Claude 판정이 갖춰져야 판매 한 요인의 720경기 arena를 한 번 실행한다.


---

## `reports/codex/20260923-FUNDAMENTAL-GAIN.md`

# 20260923 FUNDAMENTAL-GAIN — Codex Astra

VERDICT | Q1 NUMERIC BOUND / Q2 LOCAL ACCOUNTING PASS / Q3 DIAGNOSTIC RECOMMENDED | EXP-017 seed2142: cash 104,150, 조건부 상한 244,257; OMW 상대 −210 중 STRAWBERRY −674 | parent SHA `56941da238ccdc8f5286bf7e3191b6208ee3451306e06b74bb2660134a69fc33` | 회계·수량·좌석 검산 2,271 checks PASS, hypothesis strict PASS | NEXT: 아래 진단 카드 Claude 검토 → Antigravity 실행

생산량을 더 늘려야 하는지, 같은 물건을 더 잘 팔 여지가 있는지 계산했다. Q1의 숫자를 먼저 확보한 뒤 Q2·Q3로 진행했다. 현재 parent의 알려진 패배에서는 양측 판매량이 같았고 STRAWBERRY 판매 수입 차이가 가장 큰 손실이었다. 큰 조건부 상한은 나왔지만, 달성 가능한 이득이나 BT 상승폭은 아직 N/A다.

제출·다운로드·`releases/` 편집은 하지 않았다. 새로운 runtime candidate는 만들지 않았다. 이번 실행은 원본 replay 재현과 기존 parent의 회계 진단이다. 아래 실험은 **초안이며 미실행**이다.

## 0. 읽은 근거와 범위

- `evidence/KILLS.md` → `evidence/FACTS.md`를 먼저 읽었다. 엔진의 가격·unit lockstep·town·고용·작물/동물 표·shed/order 제한을 직접 확인했다. 외부 자료를 새로 다운로드하지 않았다.
- `plan/CURRENT.md`, `coordination/BOARD.md`, `HYPOTHESES.md`, 최신 Claude/Antigravity 보고, 지시서의 두 release 파일과 두 분석 폴더를 확인했다.
- BOARD의 표제 날짜는 09-20이고 여러 역사적 상태가 섞여 있다. 09-23 지시서를 사용자가 직접 지정한 **이 연구 범위의 최신 지시**로 적용했다. BOARD 동기화는 Coordinator에게 반환할 사항이며 이 보고는 새 제출·전략 실행 허가가 아니다.
- 지시서의 “K3 = 외부 tape 복제 0/52”는 정본과 다르다. 현재 K3는 **다른 farm route에 rival market 기록만 graft**하는 경로다. 0/52 donor 고정성 실패와 별개다. K2의 2턴 추가 선행, K1의 네 번째 땅, K9의 GOOSE, K6의 pure PPO를 새로 제안하지 않는다. 기존 parent가 이미 네 번째 땅/GOOSE를 쓰는 경우는 frozen baseline으로만 유지한다.
- F-T16의 과거 오류를 반복하지 않도록 `소멸량 × 평균가`를 상한으로 쓰지 않았다. **고정 engine price curve와 실제 수량**을 쓴다. F-T10/EXP-005 때문에 cash·shed·BUY·HIRE 연쇄를 보존하는지 별도 확인해야 한다.
- `analysis/c1_hosted_20260921/summary.json`은 기존 148경기 91W/7D/50L 요약이다. 새 hosted 조회나 148개 raw replay 전체 재검증은 하지 않았다. 이 빈도로 이번 단일 seed 결과를 전체 field에 외삽하지 않는다.
- `coordination/reports/claude/20260922-C1-HB-ANALYSIS.md`의 겹치는 race-window 합은 원인별 가산 분해로 쓰지 않았다.

## 1. Q1 — 숫자 상한

### 1.1 같은 seed에서 측정한 cash

| 기존 agent / 상대 | seed / 우리 seat | 우리 cash | 상대 cash | margin | 출처 |
|---|---|---:|---:|---:|---|
| C1 / V53, 저장 replay 재현 | 2014 / 0 | 64,947 | 66,956 | −2,009 | `analysis/fundamental_gain_20260923/c1_2014.json` |
| EXP-017 / V53, 원본 파일 실행 | 2014 / 0 | 66,185 | 65,595 | +590 | `exp017_2014_s0.json` |
| EXP-017 / V53, 원본 파일 실행 | 2014 / 1 | 66,185 | 65,595 | +590 | `exp017_2014_s1.json` |
| EXP-017 / OMW, 알려진 패배 재현 | 2142 / 0 | 104,150 | 104,360 | −210 | `exp017_2142_omw.json` |

모두 `[LOCAL]`, engine 1.32.7, 720 states / 719 actions, DONE/DONE. 위 상대 경로·SHA는 §4. 파일명이 생략된 출처의 공통 prefix는 `analysis/fundamental_gain_20260923/`다.

2014는 지시서가 지정한 기존 C1 패배 자료에서 고른 development seed다. 2142는 `exp017_results.txt` A_parent의 세 번째 seed에서 발생한 기존 패배를 고른 것이다. 새 seed를 탐색하다 유리한 결과에서 멈춘 것이 아니다. **성능 표본은 독립 2 seeds에 불과하며**, 2014의 좌석 대칭을 독립 증거 2개로 세지 않는다.

### 1.2 상한의 정의와 계산

전체 게임의 자유로운 생산계획까지 포함한 전역 최적 cash는 **N/A**다. 대신 사람이 허용한 범위인 생산량 고정의 느슨한 상한을 다음과 같이 계산했다. 이름은 **고정 수확량·소비량·구매량·town demand 조건부 상한**이다.

`[ENGINE+계산]` 품목 j에 대해:

```
N_j = 실제 SELL 체결 수 + DROP/EOD 소멸 수 + 종료 보유량
L_j = 초기 market inventory − 시즌 town 소비량 − 양측 BUY_PRODUCT 체결 수
U_j = L_j에서 우리 N_j개를 순차 SELL할 때의 수입
      (engine market_price 사용; price=1이면 inventory를 늘리지 않음)
C_upper = 3,000 + Σ U_j
          − 실제 BUY_SEED/BUY_ANIMAL/HIRE/BUY_LAND 비용
          − 우리 BUY_PRODUCT 체결 수 × 1
```

기준 경기의 수확·자체 소비·구매량을 고정하고 소멸분도 판매할 수 있게 했다. town/양측 구매로 생긴 모든 재고 감소를 첫 판매 전에 준다. 상대 SELL 압력, 생산 시점, cash 선결제, shed 100, 10개 order 제한은 제거한다. BUY_PRODUCT는 실제 체결 가격을 고정하지 않고 floor인 1까지 낮춘다. 이 모든 완화가 실제보다 유리한 방향이다. 본래 경기에 없던 상품 매매 횟수·추가 생산·새 town 경로는 이 클래스 밖이다.

가격은 각 품목에서 inventory의 비증가 함수다. inventory 감소를 앞당기고 상대의 inventory 증가를 제거하면 우리 판매의 누적 수입은 낮아지지 않는다. price=1에서 inventory가 늘지 않는 분기도 계산에 그대로 넣었다. `verify.py`의 2,187개 작은 거래열 완전열거는 이 floor 분기 구현을 검산한다. 이는 수학적 설명을 보조하며 전체 전략 최적화 증명은 아니다.

| EXP-017 기준 경기 | 실제 cash | 위의 조건부 상한 | 차이 | WHEAT/FERTILIZER 거래 순수입을 고정한 추가 조건부 상한 | 그 차이 |
|---|---:|---:|---:|---:|---:|
| seed2014 / V53 | 66,185 | **532,564** | **466,379** | **161,266** | **95,081** |
| seed2142 / OMW | 104,150 | **244,257** | **140,107** | **210,680** | **106,530** |

첫 상한은 WHEAT 재매매까지 크게 완화한다. seed2014의 실제 WHEAT 판매는 3,688개이고 양측 WHEAT 구매는 6,777개다. 구매를 시즌 시작에 모두 준 뒤 싼 비용으로 매매하게 한 숫자를 실전 기대이득으로 읽으면 안 된다. 마지막 두 열은 **WHEAT/FERTILIZER의 실제 순수입과 모든 비용을 유지하고**, CARROT/TOMATO/STRAWBERRY/MELON/EGG/MILK/WOOL 판매만 완화한 더 좁은 비교다.

**결론:** Q1 숫자는 있다. 하지만 상한이 크다는 사실만으로 “+10만 cash가 가능하다”거나 “700 BT를 만회한다”고 결론내릴 수 없다. 상한은 달성 가능한 정책의 수입이 아니다. 상대 공급을 지운 효과와 판매 timing을 개선한 효과가 아직 섞여 있다.

## 2. Q2 — 어디에 차이가 있는가

### 2.1 좁은 상한을 품목별로 나눈 결과

`[ENGINE+계산]` seed2142 EXP-017의 고정 WHEAT/FERTILIZER 조건. 수량은 주문 요청이 아닌 **체결 수량**이다.

| 품목 | 판매 수량 | 실제 판매 수입 | 상대 SELL 제거·town 선지급 상한 수입 | 차이 |
|---|---:|---:|---:|---:|
| CARROT | 114 | 6,148 | 6,788 | 640 |
| TOMATO | 80 | 13,359 | 22,069 | 8,710 |
| STRAWBERRY | 247 | 42,381 | 71,543 | 29,162 |
| MELON | 72 | 14,267 | 18,447 | 4,180 |
| EGG | 89 | 4,657 | 5,340 | 683 |
| MILK | 204 | 13,445 | 56,123 | 42,678 |
| WOOL | 137 | 12,322 | 32,799 | 20,477 |
| 합 | — | 106,579 | 213,109 | **106,530** |

MILK가 이 **완화 계산**에서 가장 크다. 이를 “MILK 생산을 늘릴 가치” 또는 “MILK timing으로 회수할 금액”이라고 해석할 수 없다. 상대 공급을 없앤 항이 크기 때문이다. 생산계획 개선 몫 / timing 몫 / 상대 반응 몫을 서로 독립인 세 숫자로 나누는 인과 추정은 **N/A**다.

### 2.2 실제 패배 −210의 정확한 회계 분해

`[LOCAL]` seed2142에서 양측 **farmer+hands 요청은 719/719 동일**했다. 이는 요청 동일성이다. 실행된 모든 farm state의 동일성을 뜻하지 않는다. 모든 품목의 SELL 체결 수량은 두 플레이어가 같고, 구매·고용·땅의 비용을 포함한 최종 cash 차이는 다음처럼 정확히 합쳐진다.

| 품목 | 우리 순수입 − 상대 순수입 |
|---|---:|
| WHEAT | −12 |
| CARROT | +20 |
| TOMATO | 0 |
| STRAWBERRY | **−674** |
| MELON | 0 |
| EGG | −8 |
| MILK | +383 |
| WOOL | +118 |
| FERTILIZER | −37 |
| HIRE/BUY_LAND 차이 | 0 |
| 합 | **−210** |

품목 순수입에는 그 품목의 씨앗·제품 구매도 차감했다. 이 경기의 STRAWBERRY 씨앗 구매량/비용은 같아서 −674는 그대로 판매 수입 차이다. 상대가 먼저 팔아 우리 가격을 낮추고 우리 행동도 다시 상대에 영향을 줄 수 있으므로 “우리 +211이면 승리”라는 정적 산술을 실제 개입 효과로 쓰지 않는다.

`tools/postmortem.py::build_report`를 실제 parent 실행 states에 적용했다. 도구의 `divergence_day=5, gap=0`은 “이후 일말 gap이 0으로 복귀하지 않았다”는 알고리즘 정의이며 인과 분기일이 아니다. 최악의 날은 **0-based day26, 일말 step647**, 하루 margin 변화 **−589**였다 (`exp017_2142_omw.postmortem.json`).

그날 STRAWBERRY 판매 수입은 우리 2,179 / 상대 2,792, 차이 **−613**이었다. 실제 체결의 큰 부분:

- engine market step626: 상대가 STRAWBERRY **19개, 2,485 cash** 판매. 우리는 STRAWBERRY SELL을 요청하지 않았다.
- step629: 우리가 같은 수량 **19개, 1,878 cash** 판매. 두 batch의 차이는 **−607**이다.
- 여기의 step t는 action 직전 observation의 step과 대응하고, replay action은 `steps[t+1].action`이다. `*.markets.json`은 **unit actions 이후·market 처리 직전** snapshot이므로 이를 action 직전 전체 observation으로 재사용하면 안 된다.

시즌 판매 unit를 순번으로만 맞추면 늦게 판 43개의 가격 차이 합 −593, 일찍 판 16개 −46, 같은 step 188개 −35다. 합 −674. **순번 매칭은 설명용 회계이며 같은 물건의 추적이나 causal effect가 아니다.** 따라서 “판매 앞당김 층인데 왜 일부 STRAWBERRY는 오히려 늦어졌는가”가 다음 검증 질문이다. `_ADV_PROTECT`, `_RACE_STATE.prev_action` 상호작용은 코드에서 가능한 후보이나 원인 판정은 N/A다.

### 2.3 생산·노동 가설의 현재 한계

- seed2014 C1→EXP-017은 cash +1,238, 상대 cash −1,361, margin +2,599로 변했다. OMW와 sale layer가 함께 다른 비교이므로 이를 한 factor 효과로 주장하지 않는다. 이미 이기는 2014 판을 더 키우는 것보다 실제 패배2142의 분기를 보는 편이 적절하다.
- 실제 HIRE 비용은 seed2014 **4,397**, seed2142 **7,557**이다. 노동을 전부 무료로 만들어도, 생산과 다른 cash 흐름을 고정한 비용 절감 상한은 이 금액이다. 사람을 없애도 같은 생산이 된다는 뜻은 아니다.
- seed2142에서 소멸은 FERTILIZER **1개**, 종료 제품 보유 0. 이 경기의 큰 가격 차이를 일반적인 shed-loss 수리로 설명할 수 없다. 넓은 생산계획의 전역 상한은 여전히 N/A다.
- seed2142 parent의 BUY_LAND 비용 7,000은 이미 네 번째 땅을 사는 기존 동작이다. 이것을 K1 재개 조건의 충족이나 새 네 번째 땅 제안으로 쓰지 않는다.

## 3. Q3 — 09-27 전 가능한 방법 3개

아래 시간·난이도는 `[INFERENCE]` 작업 추정이다. 실행 wall time 실측은 아니다. **BT 기대 상승은 세 방법 모두 N/A**이며 cash→BT 변환식을 만들 근거가 없다.

| 방법 | 기대 점수 / 확인할 수치 | 구현 난이도·기한 | 회귀 위험 |
|---|---|---|---|
| A. 생산·수량 고정, STRAWBERRY SELL 1건을 ±1턴 옮기는 사후 진단 | BT N/A. 알려진 −674 판매 수입 차이 중 실제 legal 개입으로 회수되는 cash·W/D/L을 측정. 8개 baseline cell 평균 +200 이상을 진행 기준으로 제안 | 낮음~중간, 0.5~1.5일. 09-25~26 진단 가능 | 진단 자체는 release 영향 0. online 전환 시 자금·shed·반응 층 회귀 위험 중간 |
| B. 여러 품목의 하루 판매 계획을 함께 beam/DP로 탐색 | BT N/A. 좁은 상한 gap 95,081/106,530은 목표 이득이 아닌 완화의 크기. feasible 하한 미측정 | 높음, 2~4일. stock·market·slot·부채 상태가 결합되므로 09-27 전 검증 완료 불확실 | 높음. EXP-005의 cash·창고 연쇄 실패를 다시 만들 수 있음. K2 추가 다중턴 선행은 범위 밖 |
| C. 생산·고용 route를 함께 재설계 | BT N/A. HIRE 무료화 cap 4,397/7,557; 생산 추가분의 cash/WDL 효과 N/A | 매우 높음, 4일 이상. 09-27 전 완결 비추천 | 매우 높음. 긴 horizon·이동·feed·수확이 결합. K1/K6/K9 재개 조건 없는 변경 제외 |

상한이 작다는 결론은 아니다. **상한이 너무 느슨해 큰 구현을 정당화하지 못한다**는 결론이다. 현 시점에서 근본적 생산 재설계가 판매 진단보다 낫다는 증거는 없다.

## 4. Artifact·검증·Coordinator 인수 사항

기준 경로는 `~/kaggle/Kaggriculture`.

| 파일 | SHA-256 |
|---|---|
| `releases/f0-omw-adv-exp017/main.py` | `56941da238ccdc8f5286bf7e3191b6208ee3451306e06b74bb2660134a69fc33` |
| `releases/public-ozer-v53-exact/main.py` | `20fe549dd4573b9fd1dfb32a1782c205fa74f0edfdfd6cbe935079533e0a9d0e` |
| `releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py` | `10f58185b916392ca39697c83f67f455df81a74dfb6eb1aacd60fd81d50c9970` |
| engine `kaggriculture.py` | `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` |
| `analysis/fundamental_gain_20260923/bound.py` | `e98877284db1e88dca7a4a88e7f4ce7b642e19b63ff3cc168421b01367208e59` |
| `analysis/fundamental_gain_20260923/verified_summary.json` | `2c798f697cc0168ffed44e495e119ca06bc269908e22b0eba01cf8b6bfe03295` |

전체 파일 SHA·크기는 `analysis/fundamental_gain_20260923/manifest.json`에 있다. `*.events.json`은 실제 unit 체결 기록, `*.markets.json`은 market 직전 state, `*.postmortem.json`은 기존 도구 출력이다. 아래 명령으로 재계산한다:

```bash
.venv/bin/python analysis/fundamental_gain_20260923/bound.py --replay analysis/c1_losses/20260921/replays/L1_2014_seat0.json --out analysis/fundamental_gain_20260923/c1_2014.json
.venv/bin/python analysis/fundamental_gain_20260923/bound.py --out analysis/fundamental_gain_20260923/exp017_2014_s0.json
.venv/bin/python analysis/fundamental_gain_20260923/bound.py --seat 1 --out analysis/fundamental_gain_20260923/exp017_2014_s1.json
.venv/bin/python analysis/fundamental_gain_20260923/bound.py --seed 2142 --rival releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py --out analysis/fundamental_gain_20260923/exp017_2142_omw.json
.venv/bin/python analysis/fundamental_gain_20260923/verify.py
python3 tools/validate_hypotheses.py --strict
```

실행 결과: 네 진단 모두 exit0; 기존 C1 replay 양측 state projection **1,440/1,440 일치**; 새 baseline DONE/DONE. 실제 체결 기반 cash 보존, 수확·구매·소비·매도·소멸·종료 수량 보존, 상한 재계산, 좌석 대칭, floor 거래열 검산 합 **2,271 PASS**. `validate_hypotheses.py --strict`: **36 entries PASS**. 정식 release/runtime gate 또는 독립 reviewer 검증은 아니다. 계측 hook은 process 안에서만 설치하고 복원했다.

자료 선택과 진단 진행은 HYP-0016 / TEST-FUNDAMENTAL-BOUND-20260923의 Codex immutable event로 기록했다. 원장 상태는 INCONCLUSIVE 유지한다. 새 사실의 FACTS owner 인수와 BOARD/K3 문구 정정 요청은 이 보고로 Claude에게 넘긴다. FACTS/KILLS/BOARD는 직접 수정하지 않았다.

## 5. 추천 1개

**A: 생산을 고정한 STRAWBERRY 1-turn timing 진단을 먼저 한다.** 현재 parent가 실제로 진 판에서 판매량은 같고, 가장 큰 손실이 STRAWBERRY 가격·시점 차이에 있다. 더 큰 생산 optimizer를 만들기 전에, 물리 계획·구매·고용을 유지하는 작은 합법 변경으로 이 손실을 회수할 수 있는지 확인한다. 이것은 runtime 정책 채택 추천이 아니라 다음 검증 한 건의 추천이다.

## 6. 사전등록 카드 초안 — 아직 실행하지 않음

```yaml
id: DRAFT-FUNDAMENTAL-STRAWBERRY-1TURN-20260923
hypothesis_id: HYP-0016
test_id: TEST-FUNDAMENTAL-STRAWBERRY-1TURN-20260923
status: DRAFT_NOT_EXECUTED
owner_design_and_verdict: Claude
owner_execution: Antigravity
parent: releases/f0-omw-adv-exp017/main.py
parent_sha256: 56941da238ccdc8f5286bf7e3191b6208ee3451306e06b74bb2660134a69fc33
engine_sha256: bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e
one_change: baseline STRAWBERRY SELL 주문 한 건만 t에서 t-1 또는 t+1로 이동
fixed:
  - 양측 같은 baseline episode의 모든 farmer/hands action
  - 양측 다른 모든 market 주문의 상대 순서와 원래 step
  - crop/animal/land/HIRE/seed/feed/fertilizer 계획과 실행 수량
  - parent의 _ADV_LOOK=3 및 다른 기존 layer 상수
hypothesis: >-
  seed2142 EXP017 대 OMW postmortem에서 같은 SELL 수량의 STRAWBERRY 수입 차이 -674,
  day26 차이 -613. 주문 하나의 1turn 변경으로 물리 계획과 조달을 보존하며 개선할 수 있는가.
  evidence=analysis/fundamental_gain_20260923/exp017_2142_omw.postmortem.json
seeds: [2014, 2142]
seats: [0, 1]
opponents:
  - path: releases/public-ozer-v53-exact/main.py
    sha256: 20fe549dd4573b9fd1dfb32a1782c205fa74f0edfdfd6cbe935079533e0a9d0e
  - path: releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py
    sha256: 10f58185b916392ca39697c83f67f455df81a74dfb6eb1aacd60fd81d50c9970
baseline_cells: 8
candidate_class:
  source_steps: 144..717 inclusive
  shifts: [-1, 1]
  source_order: baseline의 각 SELL STRAWBERRY order index를 독립적으로 열거
  target_step: 144..717 안에서만 이동하며 source와 target은 같은 day
  exclude: source 또는 target의 step modulo24=23
  quantity: 원래 order의 요청 수량을 유지
  insertion: target의 min(원래 order index,target order 수)에 삽입하고 source에서 한 건 삭제
  capacity: target order 수가 이미 10이면 구조적으로 제외
  duplicate: target에 STRAWBERRY SELL이 이미 있으면 구조적으로 제외
  composition: 여러 변경을 결합하지 않으며 개선된 trace에 다시 적용하지 않음
  include_baseline: true
  tie_break: baseline 우선, 그다음 source step 오름차순, order index 오름차순, shift -1 우선
mode: offline same-episode full-trace counterfactual; 배포 불가
metric: cell별 유효 후보의 최대 final_cash와 그 후보의 margin 및 W/D/L 차이
validity:
  - baseline 전8cell SHA/version 일치, 720states, DONE/DONE
  - baseline 녹화 양측 state projection 재현율=1.0
  - 양측 farmer/hands 발행 action 일치율=1.0
  - 양측 farms에서 money만 뺀 전체 physical state 일치율=1.0
  - 양측 BUY/HIRE/LAND의 step/op/item별 성공 수량 차이=0
  - 양측 작물 수확/동물 제품/자체 소비의 품목별 수량 차이=0
  - 양측 모든 품목 SELL 성공 수량 차이=0
  - 양측 DROP/EOD 소멸 및 종료 재고의 품목별 수량 증가=0
  - exceptions=0, engine truncation 증가=0
success_all:
  - 전8cell 최대 cash 개선의 평균>=200
  - cash 개선>=100인 cell 수>=4
  - baseline L 또는 D에서 W로 바뀌는 cell 수>=1
failure: 전8cell 최대 cash 개선의 평균<=50
inconclusive: validity PASS이며 success도 failure도 아닌 경우
invalid: baseline 재현 실패 또는 미완료 cell 수>=1
next_if_success: Claude가 미래 정보를 쓰지 않는 단일 online 규칙을 별도 카드로 고정하고 다른 seed로 검증
next_if_failure: 이 1turn 근방 탐색 종료, EXP017 유지, 같은 seed에 factor 추가 금지
next_if_inconclusive: 불확정으로 종료, seed 추가 및 임계 변경 금지
artifact: analysis/fundamental_strawberry_1turn_20260924/manifest.json + results.jsonl
candidate_runner_sha: N/A — 구현 후 실행 전에 독립 확인과 freeze 필수
```

**이 초안은 실행 허가가 아니다.** Claude가 `experiments/cards/`에 정식 ID·확정 runner SHA·event를 기록하고 baseline 목록과 모든 변형 목록을 실행 전에 freeze해야 한다.

후보의 validity 실패는 지우지 말고 해당 변형 `INFEASIBLE`로 전부 보존한다. 원 baseline을 선택지에 포함하므로 각 cell의 유효 최고 개선은 최소 0이다. 허용되는 **모든** 후보를 돌리고 좋은 결과에서 중단하지 않는다. 판정은 8 cells 기준의 development 진단으로만 한다. 미래 전체 trace를 알고 고른 최선은 이 유한 1-change 클래스의 oracle이며, 전체 게임 상한이나 실행 가능한 online 정책이 아니다. 상대는 같은 episode의 **전체 action stream**으로 고정하므로 반응형 상대의 counter-response 효과는 별도 검증 대상이다. rival market 기록을 우리 다른 farm 경로에 이식하지 않는다.

다음 행동 두 가지: **(1)** Claude가 이 진단 카드와 조건부 상한 정의를 검토해 정식 사전등록한다. **(2)** Antigravity가 등록된 전 cell을 실행하고 raw 결과를 Claude에게 넘긴다. 이번 설계 판단에는 현재 Astra로 충분하며 더 높은 모델이나 새 채팅은 필요하지 않다.


---

## `reports/codex/20260925-0017-DP-LOSS-CAUSE.md`

# DP-LOSS-CAUSE — BLOCKED at session-start gate

1. 무엇을 하려는가: DP 0924 hosted 패배 원인을 분석하고, 반복되는 결정 하나를 바꿔 hosted 복제 패널로 검증한다. 사용자 지시대로 제안서 상단의 수집 결과 반영·분석 우선순위·Q5 보정을 본문보다 우선한다.
2. 왜 멈추는가: AGENTS.md §11의 시작 조건에 걸렸다. BOARD 갱신 표시는 2026-09-20이며 확인일 2026-09-25와 5일 차이다. 활성 슬롯 표는 최신 원장과 같지만, 하단의 현재 FIFO 설명은 다르다.
3. 무엇을 확인했는가: 제안서 발행 줄과 수집 보고 PASS 표기는 존재한다. parent SHA는 지시서의 178ae0f7 prefix와 일치한다. 패배 원인·패치 효과·패널 성적은 모두 N/A(미실행). 원장 형식 검증은 PASS(36 entries).
4. 다음 행동: Coordinator가 BOARD의 갱신일·현재 FIFO·최신 지시서 포인터를 정리한 뒤 재개한다. 또는 사람이 이번 작업에 한해 §11 시작 조건 예외를 명시한다. Codex가 BOARD를 직접 고치거나 최신 발행 줄을 예외 승인으로 추정하지 않았다.

## 차단 근거 [LOCAL]

- `AGENTS.md:328-330`: BOARD가 2일 이상 오래됐거나 최신 제출 상태와 어긋나면 **작업을 시작하기 전에 코디네이터에게 반환한다**.
- `coordination/BOARD.md:3`: 갱신 2026-09-20 KST. 파일의 실제 수정 시각을 이 문서상 갱신일 대신 쓰지 않았다.
- `coordination/BOARD.md:23`: 활성 EXP-017 56490029 / DP 56518910, 다음 은퇴 EXP-017. `evidence/HOSTED_LEDGER.md:372`와 일치한다.
- `coordination/BOARD.md:91`: 현재 순서 EXP-007 / yhay81-exact 56330776, 다음 은퇴 EXP-007이라고 적혀 있어 위 두 위치와 충돌한다.
- `coordination/BOARD.md:35`: HOSTED_LEDGER가 09-14 이전까지라고 적혀 있지만 실제 원장에는 09-24 기록이 있다(`evidence/HOSTED_LEDGER.md:372-373`).
- `coordination/proposals/claude/20260924-DP-LOSS-CAUSE-CODEX.md:9`: 09-24 22:50 발행 줄은 확인했다. 발행 조건 미충족을 차단 사유로 삼지 않는다. 이 줄에는 §11 시작 조건 예외가 없다.

이 판정은 실행 전 운영상 BLOCKED다. 전략 FAILURE, 패치 없음, Q5 후보 없음이라는 결론이 아니다. 이번 반환은 이 파일과 TASKS의 자기 행으로 전달하며 외부 메시지는 보내지 않는다.

## 재개 시 보존할 지시

- Q1 우선순위: herd-safe-v3 FULL → DP와 step 143까지 같은 상대의 첫 분기 → LB <2400 upset → 나머지. 2600+ 사설 봇 패배는 개수만.
- 56502662는 Q1에서 표시하고 closed-loop 판정에서는 제외한다. field 추정치는 submission별 승리 재가중을 적용한다.
- Q4 패널은 지시서가 지정한 전부를 사용하고 SE를 보고한다. 원자료로 패널 구성·제외 조건을 확인하기 전 수치를 확정하지 않는다.
- Q5의 herd-safe-v3는 상성 상대로만 기록한다.
- 카드 판정은 지시서 그대로 사전 고정한다. 완성된 카드 SHA를 **패널 실행 전에** 별도 기록하고 사후에 판정 기준을 바꾸지 않는다.
- Q1~Q5 분석·Q2 replay·Q4 패널·참고 직접 대결은 모두 미실행. EXP-018 카드/카드 SHA, candidate, release는 N/A. 미작성 카드를 동결했다고 기록하지 않는다.
- 제출·Kaggle 다운로드·BOARD/KILLS/HYPOTHESES 직접 수정 없음. 가설 검증을 수행하지 않아 hypothesis event를 만들지 않았다.

## 읽은 파일의 SHA-256 [LOCAL]

| 경로 | SHA-256 |
|---|---|
| `AGENTS.md` | `f53bdcd455707f6aef33123f2c86c24e9e022befc1aed973d04fd51a955cae20` |
| `coordination/BOARD.md` | `ba855711ca9a5f8415c143acd0a7a8eb132697ea099003e79763926996e70a80` |
| `evidence/HOSTED_LEDGER.md` | `6a05e05cc7968567ba575cac185fbee13df77c6c5590776f2c17e81c48b3ced1` |
| `coordination/proposals/claude/20260924-DP-LOSS-CAUSE-CODEX.md` | `ec6cdced91aacd15fab76e547295870c0222c8e0c53b581f1a2e7d74f7581329` |
| `coordination/reports/antigravity/20260924-2155-DP-HOSTED-MAP.md` | `aef13327883c04c8cbe69daf15d4dfd688fead36e2afab6fe55d259b68b6bf07` |
| `releases/public-tetsutani-demand-preserving-0924-exact/main.py` | `178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a` |

## 실행한 확인

- `python3 tools/validate_hypotheses.py --strict` → exit 0, `hypothesis ledger PASS: 36 entries`.
- Python `hashlib.sha256(Path(path).read_bytes())`로 위 6파일 SHA 계산. 날짜 차는 `date(2026,9,25) - date(2026,9,20)` = 5일.
- `git diff --cached --name-only` → 시작 시 staged 파일 없음. 다른 작업자의 기존 변경은 보존한다.
- 게임 코드·분석 코드 변경 없음. 경기 실행 및 runtime 검증 N/A.
- 전체 `git diff --check`는 이번 작업 밖 기존 변경의 trailing whitespace를 보고했다. 해당 파일들은 수정하지 않고 이번 두 문서만 별도로 확인한다.

VERDICT | BLOCKED: AGENTS §11 시작 조건, BOARD 갱신일/FIFO 충돌 | parent SHA 178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a | strict ledger PASS 36; Q1–Q5 N/A | NEXT ACTION: Coordinator 상태 정리 후 같은 지시서로 재개


---

## `reports/codex/20260925-1340-DP-LOSS-CAUSE.md`

# DP-LOSS-CAUSE — 필수 DP 하한 미달, 후보 채택 불가

1. 무엇을 시험했는가: DP 0924의 기존 판매 예측 갱신 주기 하나를 3턴에서 2턴으로 바꿨다. 부모 바이트 전체 뒤에 `_V92_P_EVERY = 2`만 덧붙였다.
2. 왜 했는가: herd-safe 상대의 반복 패배에서 후반 STRAWBERRY 판매 단가가 낮았고, 두 코드의 기존 예측 갱신 주기가 달랐다. 원인 후보였으며, 같은 판매 층을 새로 붙이지 않았다.
3. 결과: [LOCAL] 유효 hosted 복제 패널은 부모 23승/0무/24패 → 후보 28승/0무/19패. 그러나 DP 직접 대결은 22승/34무/24패, 39/80 = **0.4875 < 0.50**이다. 따라서 최종 SUCCESS 및 B-2 모두 불가다.
4. 다음: 추천 패치·Q5 exact 후보 모두 없음. release와 제출을 하지 않았다. 기준·seed·카드 SHA를 바꾸거나 근소한 미달을 재시험하지 않는다. 결과를 Coordinator에 인계한다.

## 판정의 의미

**VERIFIED_NOT_ELIGIBLE_DP_FLOOR**: 실행/identity 오류로 막힌 BLOCKED가 아니라, 유효하게 측정한 필수 하한 미달이다. 원자료의 `panel_verdict=SUCCESS`는 본문 패널 조건만 통과했다는 뜻이며 `eligible_success=false`와 함께 읽는다. 09-25 상단 조건을 적용한 최종 SUCCESS가 아니다. 분모·SE·임계값을 사후 변경하지 않았다.

원래 00:17 BOARD 차단 보고는 역사로 보존한다. 00:45 재개 지시로 해소한 뒤 이 작업을 수행했다. 중단 후에는 기존 프로세스의 완료 결과를 회수했으며, 완료한 경기를 다시 실행하지 않았다.

## Q1 — 실제 체결, 구매 시점, 패배 묶음

[LOCAL replay audit] 319개 저장 replay의 시장 주문을 고정 엔진 1.32.7로 재계산했다. pre-state → unit actions(atomic PLANT 포함) → market 순서이며, SELL 요청량이 아니라 `_commit_unit` 성공 수량과 가격이다. 288,360회 player-step 현금 검산이 저장 post-state와 일치했다. 재현: `python3 tools/dp_loss_cause.py describe`.

- 전체 패배 199, 제외 submission56502662의 패배 28은 표시만, 유효 패배 171. LB<2400 패배는 전체95/유효76이다.
- 모든 경기의 d0–11/d12–18/d19–29 품목별 판매 수량·평균가·구간 끝 cash: `experiments/results/dp_loss_cause_20260925/q1_period_sales.csv`.
- 실제 HIRE/BUY_LAND/BUY_ANIMAL 시점: 같은 폴더 `q1_purchases.csv`. 구매 요청과 실제 증가를 구분했다.
- 경기별 원래 metadata, raw SHA, trade ledger, postmortem: 같은 폴더 `episodes/<episode>.json`.
- `postmortem`의 bank_a/b는 원래 seat0/1이다. DP seat1이면 gap 부호를 반대로 읽어야 한다. 아래 근거112606102와112786680은 DP seat0다.

### 최우선 herd-safe FULL — 두 반복 증상

| 묶음 | 유효 패배 수 | 최종 margin 합 | 상대 LB 중앙값 | 관측된 결정/시험 |
|---|---:|---:|---:|---|
| refresh | 8 | -9152 | 2321.05 | d19–29 STRAWBERRY 평균 판매가 열세; 기존 예측 refresh 3→2 |
| carrot | 9 | -5924 | 2321.70 | 전체 CARROT 판매 수량 부족; 기존 전환 margin -5→-15 (미실행) |

두 묶음은 겹치므로 합산하지 않는다. 원본 herd FULL은 DP1승15패이나, 제외 submission의3패를 빼면1승12패다. 112606102의 첫 지속 분기는 day9 gap−4, 최악 day26의 gap 변화−389, 최종−499; 112786680의 최악 day28 변화−812, 최종−1897 (`tools/postmortem.py:build_report` 적용 결과). 후반 단가 차이가 모든 초기 분기와 모든 패배의 원인이라는 주장은 하지 않는다.

[INFERENCE, sampling correction] 승리 재가중 후 herd FULL 비중은 전체 non-draw 기준 2.590%, 제외 submission을 뺀 non-draw 기준 2.611%다. 다운로드 표본의 15패를 field의 큰 비중이라고 읽지 않는다.

### DP-prefix 상대 — 첫 행동 분기

상단 우선순위의 17패 전부를 확인했다. 상대의 실제 pre-observation에 fresh DP를 순서대로 호출한 비교다. 상대의 비공개 코드나 원인 효과를 재구성했다는 뜻은 아니다. action_row는 replay의 행 번호, decision step은 그보다1 작다. 결과 원문: `q1_dp_prefix_divergences.json`.

| Episode | submission 제외 표시 | decision step / action_row | 최초 다른 내용 (DP 예상 → 실제 상대) |
|---|---|---|---|
| 112433891 | 유효 | 479 / 480 | `market: [['SELL', 'STRAWBERRY', 1]] → [['SELL', 'STRAWBERRY', 6]]` |
| 112493607 | 유효 | 159 / 160 | `market: [['BUY_SEED', 'STRAWBERRY', 1], ['BUY_SEED', 'WHEAT', 2]] → [['SELL', 'WOOL', 2], ['BUY_SEED', 'STRAWBERRY', 1], ['BUY_SEED', 'WHEAT', 2]]` |
| 112534200 | 유효 | 505 / 506 | `market: [['SELL', 'FERTILIZER', 17], ['SELL', 'MILK', 9], ['HIRE'], ['HIRE'], ['HIRE']] → [['SELL', 'MILK', 9], ['SELL', 'FERTILIZER', 17], ['HIRE'], ['HIRE'], ['HIRE']]` |
| 112550063 | 유효 | 576 / 577 | `market: [['SELL', 'WOOL', 1], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE']] → [['SELL', 'WOOL', 8], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE']]` |
| 112581922 | 유효 | 180 / 181 | `market: [['BUY_SEED', 'STRAWBERRY', 1], ['BUY_SEED', 'WHEAT', 1]] → [['BUY_SEED', 'STRAWBERRY', 1], ['BUY_SEED', 'WHEAT', 1], ['BUY_PRODUCT', 'WHEAT', 7]]` |
| 112649927 | 유효 | 465 / 466 | `market: [['SELL', 'MILK', 1], ['SELL', 'WOOL', 1]] → [['SELL', 'WOOL', 2], ['SELL', 'MILK', 1]]` |
| 112666107 | 유효 | 291 / 292 | `market: [['SELL', 'MILK', 3]] → [['SELL', 'MILK', 3], ['SELL', 'WOOL', 1]]` |
| 112694693 | 유효 | 160 / 161 | `market: [] → [['SELL', 'WOOL', 2]]` |
| 112717208 | 56502662 제외 | 157 / 158 | `market: [] → [['SELL', 'WOOL', 2]]` |
| 112730129 | 유효 | 313 / 314 | `market: [['HIRE'], ['HIRE']] → [['SELL', 'MILK', 3], ['HIRE'], ['HIRE']]` |
| 112734737 | 유효 | 385 / 386 | `market: [['SELL', 'STRAWBERRY', 8], ['SELL', 'FERTILIZER', 12], ['SELL', 'WHEAT', 7], ['SELL', 'WOOL', 4], ['HIRE'], ['HIRE']] → [['SELL', 'FERTILIZER', 12], ['SELL', 'WHEAT', 7], ['SELL', 'WOOL', 4], ['SELL', 'STRAWBERRY', 8], ['HIRE'], ['HIRE']]` |
| 112745317 | 유효 | 150 / 151 | `market: [['SELL', 'WOOL', 4], ['BUY_PRODUCT', 'WHEAT', 2], ['BUY_PRODUCT', 'FERTILIZER', 1], ['BUY_LAND'], ['BUY_ANIMAL', 'GOOSE', 2]] → [['SELL', 'WOOL', 4], ['BUY_PRODUCT', 'WHEAT', 2], ['BUY_PRODUCT', 'FERTILIZER', 1], ['BUY_LAND'], ['BUY_ANIMAL', 'GOOSE', 2], ['BUY_SEED', 'CARROT', 8]]` |
| 112755668 | 유효 | N/A | `719개 행동 전부 일치; 수집기의 prefix label만으로 변형이라고 단정할 수 없음` |
| 112761382 | 유효 | 254 / 255 | `hands: [['WEST'], ['BUILD_PASTURE'], ['WEST'], ['PASS'], ['WEST'], ['PICKUP', 'WHEAT'], ['NORTH'], ['SOUTH'], ['COLLECT_FERTILIZER'], ['PLACE', 'MELON', 6], ['CARE']] → [['WEST'], ['BUILD_PASTURE'], ['WEST'], ['HARVEST'], ['WEST'], ['PICKUP', 'WHEAT'], ['NORTH'], ['SOUTH'], ['COLLECT_FERTILIZER'], ['PLACE', 'MELON', 6], ['CARE']]` |
| 112795924 | 유효 | 153 / 154 | `market: [['SELL', 'FERTILIZER', 3]] → [['SELL', 'WOOL', 2], ['SELL', 'FERTILIZER', 3]]` |
| 112830224 | 유효 | 160 / 161 | `market: [] → [['SELL', 'WOOL', 2]]` |
| 112837776 | 56502662 제외 | 150 / 151 | `market: [['SELL', 'WOOL', 4], ['BUY_PRODUCT', 'WHEAT', 2], ['BUY_PRODUCT', 'FERTILIZER', 1], ['BUY_LAND'], ['BUY_ANIMAL', 'GOOSE', 2]] → [['SELL', 'WOOL', 6], ['BUY_PRODUCT', 'WHEAT', 2], ['BUY_PRODUCT', 'FERTILIZER', 1], ['BUY_LAND'], ['BUY_ANIMAL', 'GOOSE', 2]]` |

추가 WOOL 판매, 판매 수량·순서, 씨앗/사료 구매 등의 차이가 관측됐다. 이들은 후속 가설 자료이며 Q2 최우선 후보가 선택 조건을 통과했으므로 별도 패치로 실행하지 않았다.

### 나머지 반복 패배 묶음

최초로 구간 끝 cash가 뒤진 구간과 그 구간에서 가장 큰 판매수입 부족 품목으로 묶은 **증상 분류**다. 구매비·판매시점 차이도 cash에 영향을 주므로 표를 확정 원인으로 읽지 않는다. 아래는 유효 표본에서5경기 이상인 묶음만 표시한다. 개별 기록은 q1_summary와 CSV에 보존했다.

| 우선순위 | 첫 cash 열세 구간 | 최대 판매수입 부족 | 경기 수 | margin 합 | 상대 LB 중앙값 |
|---|---|---|---:|---:|---:|
| 3-upset-lt2400 | d0–11 | MILK | 7 | -84177 | 1846.8 |
| 3-upset-lt2400 | d0–11 | WHEAT | 6 | -6689 | 2327.8 |
| 3-upset-lt2400 | d0–11 | purchase-or-other | 6 | -2448 | 2207.3 |
| 3-upset-lt2400 | d12–18 | WOOL | 6 | -6282 | 2307.1 |
| 3-upset-lt2400 | d19–29 | CARROT | 8 | -2597 | 2263.2 |
| 3-upset-lt2400 | d19–29 | MILK | 5 | -570 | 2304.7 |
| 3-upset-lt2400 | d19–29 | STRAWBERRY | 6 | -1542 | 2205.2 |
| 3-upset-lt2400 | d19–29 | WOOL | 6 | -5499 | 2343.8 |
| 4-other | d0–11 | MILK | 8 | -114609 | 2553.2 |
| 4-other | d0–11 | WHEAT | 10 | -36751 | 2460.7 |
| 4-other | d0–11 | purchase-or-other | 5 | -3294 | 2501.0 |
| 4-other | d19–29 | STRAWBERRY | 7 | -11846 | 2525.7 |

LB≥2600이고 FULL 공개 파일이 확인되지 않은 상대 패배: **전체37 / 유효33 / 제외4**. 사설 코드 여부 자체는 N/A이며 더 상세한 전략 분석이나 패치 우선순위를 부여하지 않았다.

## Q2 — 사전 고정 8경기 closed-loop

| Episode | 부모 margin | 후보 margin | 변화 | 패→승 |
|---|---:|---:|---:|---|
| 112606102 | -499 | -499 | +0 | N |
| 112673766 | -495 | -495 | +0 | N |
| 112739528 | -1445 | -1445 | +0 | N |
| 112774818 | -1349 | 635 | +1984 | Y |
| 112786680 | -1897 | 836 | +2733 | Y |
| 112797220 | -707 | -707 | +0 | N |
| 112819173 | -2130 | -2404 | -274 | N |
| 112820851 | -630 | 341 | +971 | Y |

3/8이 strict win으로 전환되어 Q2 기준(≥3)을 통과했다. draw는 전환으로 세지 않았다. 사전 순서에 따라 carrot fallback은 **미실행**이다. 같은 방향 재조정0회. open-loop 반사실 게임은 실행하지 않았고 Q1의 관측 비교를 반사실 성과로 세지 않는다.

## Q3 / Q4 — 변경과 최종 판정

변경: 부모7333줄을 한 바이트도 바꾸지 않고 끝에 `_V92_P_EVERY = 2`를 추가했다. `_ADV_LOOK=4`, 최종 SELL 재정렬, 기존 예측 horizon은 보존했다. 마지막 callable은 `_final_sell_block_reorder_entrypoint`다. 부가 wrapper·네트워크·파일 로딩은 추가하지 않았다. release는 추천 조건 미달로 생성하지 않았으며 E-5 clean-room/tar gate는 N/A다.

패널 inventory59(29L/30W) 전체를 freeze에 보존했다. 상단의 submission56502662 제외를 적용해12(5L/7W)를 판정에서 제외했다. 유효47(24L/23W) 전부를 실행했다. 부모47경기는 양쪽67,586개 행동·67,680개 projected state가 원본과 정확히 일치했다. 고유seed47개, 원래 DP좌석 그대로다.

| 항목 | 부모 | 후보/결과 | 판정 |
|---|---:|---:|---|
| 유효 패널 W/D/L | 23/0/24 | 28/0/19 | 5패→승 |
| 패널 점수율 | 0.48936170 | 0.59574468 | Δ=0.10638298 |
| paired SE / 2SE | — | 0.04546036 / 0.09092072 | Δ>2SE PASS |
| 기존 승리의 새 패배 | — | 0 ≤ 5/3 | PASS |
| DP 직접 80경기 W/D/L | — | 22/34/24 | 39점/80 |
| 필수 DP 하한 | ≥0.50 | **0.4875** | **FAIL; SUCCESS/B-2 불가** |
| DP 40seed paired SE | — | 0.05797739 | 참고값, 하한은 point score |
| 후보 최대 step | <0.5s | 0.127131917s | PASS |
| 예외 / caught-error telemetry / 비정상 종료 | 0 | 0 | PASS |

직접80경기는 seed2400–2439×양좌석을 모두 완료했다. 0.50에 필요한40점보다1점 부족하며, 반올림해서 통과시키지 않는다. body의 선택20경기를 필수80경기로 대체한 것은 실행 전 카드에 명시했다. Q2의16실행을 재사용해 전체 actual game 실행은174회(Q2 16 + 추가 패널78 + DP80 80)다.

패널은 Q1/Q2에도 사용한 development 자료다. 이 결과의 SE는 고정 sample의 기술 통계이며 독립 holdout의 선택 편향 보정값이나 hosted BT 우위 증명이 아니다. Runtime은 serial local 측정이며 hosted runtime은 N/A다.

### DP 비중 시나리오 — 보고용, 판정에 사용하지 않음

| DP 비중 | 부모 기대 점수율 | 후보 기대 점수율 | 변화 |
|---|---:|---:|---:|
| 1.6839% (current_panel) | 0.836140 | 0.868313 | +3.2173%p |
| 20.0000% (20%) | 0.773518 | 0.797368 | +2.3850%p |
| 40.0000% (40%) | 0.705138 | 0.719901 | +1.4763%p |

승리 weight=각submission의 전체승리/샘플승리, 패배weight=1. FULL 유효 패널의 가중치 합은154.4이며 유효 non-draw field743의 **20.78%**를 대표한다. 나머지 상대 효과를0으로 채워 full-field 예측으로 제시하지 않았다. 전체884헤더 중 draw19의 replay가 없으므로 non-draw 조건부 추정이다.

현재1.6839%는 **유효 FULL 패널의 exact-DP 비중**이다. 넓은 DP-prefix를 포함한 유효 수집 표본의 재가중 비중은3.7506%(전체submission은3.4528%)로 별개다. 비공개 DP 변형을 exact-DP로 간주하지 않았다. 혼합식은 카드대로 non-DP weighted mean×(1−p)+DP직접점수×p, 부모mirror는 양좌석 평균0.50이다. 조건부 시나리오가 양수여도 필수하한을 면제하지 않는다.

## Q5 — 다른 계열 exact 후보

| 공개 FULL 계열 | DP W/L (다운로드 표본) | 사용 팀 LB 중앙값 | 범위 | 추천 |
|---|---:|---:|---|---|
| herd-safe-v3-experimental-risk-aware-feed | 1/15 | 2321.70 | 2239.7–2515.0 | 없음: 상단 Q5 보정으로 상성 상대만 |
| v56-smarter | 0/4 | 2167.55 | 1879.0–2365.0 | 없음: 팀 집단 LB 근거 부족 |
| kaggriculture-pipe18-six-layers | 2/3 | 2305.00 | 2244.1–2466.5 | 없음: 팀 집단 LB 근거 부족 |
| kaggriculture-v57-funding-order-invariant | 2/1 | 2146.60 | 2145.0–2148.2 | 없음: 팀 집단 LB 근거 부족 |
| kaggriculture-herd-safe-sale-window-race-ca20 | 0/1 | 1846.80 | 1846.8–1846.8 | 없음: 팀 집단 LB 근거 부족 |
| order-book | 1/1 | 2103.50 | 2081.8–2125.2 | 없음: 팀 집단 LB 근거 부족 |
| C2 | 2/1 | 2028.90 | 1956.2–2297.1 | 없음: 팀 집단 LB 근거 부족 |
| kaggriculture-7-turn-rescue-historical-lb-2800 | 2/1 | 2193.50 | 2179.2–2194.8 | 없음: 팀 집단 LB 근거 부족 |
| more-wheat-smarter-sales | 0/1 | 2263.40 | 2263.4–2263.4 | 없음: 팀 집단 LB 근거 부족 |
| kaggriculture-more-wheat-smarter-sales | 0/1 | 2263.00 | 2263.0–2263.0 | 없음: 팀 집단 LB 근거 부족 |

DP 외부7팀 LB 중앙값2435.9 (Sian 수렴 중2069.1은 외부그룹에서 제외), 조회snapshot09-24 11:43:08 UTC. herd는지시대로 제외한다. pipe18은 높은 팀2466.5도 있으나 집단 중앙값2305.0이고, 유효 FULL에서는 DP2승2패다. 단일 고점 팀과 다운로드의 과대표집된 패배만으로 Y를 추천하지 않는다. 다른 패배유발 공개계열의 팀LB도 이 기준집단에 못 미친다. 새Y closed-loop 우위 시험은 N/A; **추천할 Y 없음**이다. 경로·raw SHA는 `q5.json`에 보존했다. 팀 최고LB를 해당submission의 점수로 간주하지 않는다.

## Artifact identity와 검증

| 파일 | SHA-256 |
|---|---|
| `experiments/cards/EXP-018-dp0924-single-factor.md` | `f2eaac36d5f002316692e2265b95d4b79bc54755563587be426a2a6a32c58686` |
| `experiments/results/dp_loss_cause_20260925/freeze.json` | `12704c262374b21c52507a7cb5aa08d18a89b6ba27f089b2c0e712ead214bcd2` |
| `releases/public-tetsutani-demand-preserving-0924-exact/main.py` | `178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a` |
| `experiments/candidates/exp018_dp0924/refresh/main.py` | `f3e727b175eac13b702c3de34191b2cff170e30220bcb108b1010fc782505052` |
| `tools/dp_counterfactual.py` | `cb8c83ff7c8db3f9526dc3651aa35b3b6e8ba1ec2b264731eee491803c5cb23f` |
| `analysis/exp018_panel/summary.json` | `2318cbdc2e714ed454a68f1e3572c6c59d633947ce45435e581d0327b03abd4c` |
| `experiments/results/dp_loss_cause_20260925/verification.json` | `6bc1c6873162e7d7dfaa917cd90e44a572be3552dee7c21675bf4fff62ab409f` |

카드/입력 freeze 시각은 **2026-09-24T15:59:43.720643+00:00** (09-25 00:59:43 KST), Q2 및 Q4 실행 전이다. source/opponent/raw319개 등을 포함한351개 입력 SHA가 종료 검산에서도 동일했다. 기록의 Q4 `started_at`은 runner가 결과 저장 직전에 쓴 시각이므로 정밀한 game 시작시각으로 인용하지 않는다; 사전 freeze는 별도 freeze.json과 Q2 실행 전 기록으로 확인한다.

실행한 검증:

- `python3 tools/dp_loss_cause.py audit` — 엔진 lock, 원자료 및 패널 제외 대조 PASS.
- `python3 tools/dp_loss_cause.py describe` — 319개 replay, 288360 cash checks PASS.
- `python3 tools/dp_loss_cause.py summarize` 및 `divergences` — Q1 집계·17패 최초 분기 기록.
- `python3 -m unittest tests.test_reproduce_replay -q` — 5 tests PASS (2.821s).
- `python3 tools/dp_counterfactual.py --freeze experiments/results/dp_loss_cause_20260925/freeze.json --candidate refresh` — 고정Q2 8개 모두 완료, 3flip.
- 같은 command에 `--phase q4` — 패널47개 양artifact 및 DP80 완료, exit0은 실행완료이며 후보승인이 아님.
- `python3 tools/verify_dp_loss_results.py` — 2039 checks PASS, 별도 계산으로 `VERIFIED_NOT_ELIGIBLE_DP_FLOOR`.
- `python3 tools/validate_hypotheses.py --strict` — exit0, hypothesis ledger PASS:37 entries. HYP-0016 결과와 HYP-0037 fallback 미실행을 updater event로 기록했다.

Q2/Q4 runner와 카드·freeze·측정결과는 검산 중 수정하지 않았다. BOARD/KILLS/다른 owner 문서는 직접 고치지 않았다. HYPOTHESES는 updater만 사용한다. 공유 원장에는 다른 agent의 기존 미커밋 변경도 있으므로 해당 전체 diff를 이번 commit에 섞지 않는다; 이번 immutable events가 변경 근거다.

다음 행동 두 가지: ① Coordinator가 이 gate 실패와 후보 미채택을 BOARD에 반영한다. ② 현재 DP의 다음 hosted snapshot과 새 공개 계열을 확인하되, 이 카드의 seed 추가·threshold 완화·fallback 뒤늦은 실행으로 미달을 우회하지 않는다.

VERDICT | VERIFIED_NOT_ELIGIBLE_DP_FLOOR — 패널 조건 PASS, 필수 DP80 하한 FAIL | 후보 f3e727b175eac13b702c3de34191b2cff170e30220bcb108b1010fc782505052 | independent arithmetic/identity audit 2039 checks PASS | NEXT ACTION: 후보 채택 없이 Coordinator 인계; release·제출 없음


---

## `reports/codex/20260925-1846-NEWMETA-EXACT.md`

# NEWMETA-EXACT — NOT_ELIGIBLE

127ed3e6 원본을 CRLF 그대로 포장하고, Mac worker6에서 1,000경기를 실행했다. 무인 탐색의 실행 속도와 runtime gate를 확인하기 위한 작업이다.
[LOCAL] Runtime 1000경기: invalid 0, maximum step 0.750587250s, 최대 game-p99 0.044139417s. p99는 game별 p99의 최댓값으로 보수적으로 판정했다.
최종 verdict **NOT_ELIGIBLE**. runtime 통과=False, 연속30분=True, memory 통과=True. 제출하지 않았다. 다음은 1b 부모 tournament이며 최종 부모는 calibration 이후 고른다.

- 진입점: `{'entry': 'ig_agent', 'has_file': False}`. tar member=['main.py']; 원본 SHA=127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652; tar SHA=63e1554c9330557787462eb875960c8c9c9d52c4830251e657a512881625d86b.
- DP80 W/D/L=66/0/14, score=0.825; seed2400–2439 양 좌석.
- E-5 20경기 W/D/L=16/0/4, score=0.8; seed2300–2309 양 좌석, 필수 ≥0.70.
- Panel47 W/D/L=42/0/5; 개발 자료이므로 metric/holdout에서 제외.
- 기존 DP 경기 112786680 actions/rewards/720-step 재현=True. 동일 seed/좌석 3회 deterministic 검증=True.
- Runtime seed10000–10499 양 좌석, 상대 DP178ae0f7, engine1.32.7. runner/상대/원자료 SHA는 `stage1-runtime.json`, `stage1-extra.json`, 각 games.jsonl행에 기록.
- 연속부하 2094.2s; 초기5분 1584games/h → 마지막5분 1776games/h; ratio=1.121212121212121. 전체 1719.04games/h. worker당 peak RSS 391.5MiB. 5-worker 비교 필요=False.
- 단일 standalone controller가 완료 즉시 games.jsonl append+fsync, state.json 임시파일+rename+fsync. 재시작은 완료 key를 건너뛴다. 진행 중 경기는 다시 실행할 수 있다. state는 성능 증거가 아니다.
- launchd 설치는 지시서대로 사람이 실행한다. 아래 파일은 template이며 이 보고서가 설치 완료를 의미하지 않는다. Mac 덮개 닫힘/잠자기 중 계산은 진행하지 않는다.

```sh
mkdir -p ~/Library/LaunchAgents
cp ~/kaggle/Kaggriculture/experiments/search_20260925/com.sian.searchloop.plist ~/Library/LaunchAgents/com.sian.searchloop.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.sian.searchloop.plist
launchctl kickstart gui/$(id -u)/com.sian.searchloop
# 덮개가 열린 동안 절전 방지 (별도 터미널)
caffeinate -dimsu
# 제거
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.sian.searchloop.plist
rm ~/Library/LaunchAgents/com.sian.searchloop.plist
```

검증: `python3 -m unittest tests.test_search_loop tests.test_reproduce_replay -q` 14 tests PASS; `python3 tools/search_loop.py --manifest experiments/search_20260925/stage1-runtime.json`; 추가 측정은 `stage1-extra.json`. 원자료: `experiments/search_20260925/games.jsonl`, summary: `experiments/search_20260925/stage1-summary.json`.

Identity: True
Schema: clean-room loader True, entry ig_agent; full action legality separately N/A
Runtime: False — Mac local only; hosted N/A
Isolation: True
License: source Apache-2.0 notices retained; provenance in source-audit.json
Ledger: N/A — no submission

다음 행동 두 가지: ① gate가 모두 통과했는지 사람이 보고 exact 제출 여부 판단(FIFO는 제출 직전 재확인). ② 1b screening→상위5개 confirmation을 완료하고 calibration 전 순위를 보고한다.

추가 검산: `python3 tools/verify_search_stage1.py` — 실행 controller와 별도 계산으로 8,074 checks PASS. 1,151경기 고정 snapshot `experiments/search_20260925/stage1-games.jsonl`, SHA256 `229e7552db1b1ee19105005cb7cea92a63433552022eaff49641a1996c493866`. Runtime NOT_ELIGIBLE 판정은 그대로다.


---

## `reports/codex/20260925-1955-PARENT-TOURNAMENT.md`

# PARENT-TOURNAMENT — LOCAL_RANKING_ONLY

09-24/25 공개 파일의 고유 SHA 전부를 대상으로 gate와 DP·NEWMETA 직접 대결을 실행했다. 부모 후보를 두 파일에 한정하지 않기 위한 비교다.
[LOCAL] 고유 파일 32개, gate 통과 28개. Screening seed2500–2519×양좌석×2상대, 상위5개 confirmation seed2520–2559×양좌석×2상대.
최종 부모와 다른 계열 슬롯 B 추천은 2단계 metric calibration 이후 확정한다. 이 표는 hosted 우위나 제출 승인이 아니다.

| SHA | gate | 사유/maximum step |
|---|---|---|
| a16e0e9b40c489972630a0b9d04f30e9c1cab03159fa78676db74277d84d82ab | True | external=[]; cleanroom=True; max=0.130057s |
| 178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a | False | external=[{'line': 3593, 'call': "_v92_os.environ.get('V92_SELL_LIB')"}, {'line': 3596, 'call': 'open(path)'}]; cleanroom=True; max=0.000000s |
| 4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01 | True | external=[]; cleanroom=True; max=0.128246s |
| 4889137f1adf1f9266b2ad5a6ac6700c40e9be6dfe3654e39db375fb55b71341 | True | external=[]; cleanroom=True; max=0.121996s |
| 2993cf9241b467bbfa317cf8ba13216f4f2b49070c5632984eb2704eb88a2435 | True | external=[]; cleanroom=True; max=0.119486s |
| dc5433c7996f3f18bc766083a3b6b0ef22ba290cf917fd680ee41c62b8de734d | True | external=[]; cleanroom=True; max=0.105728s |
| 37d284d4d4d9aff50ee2dce8a6cc2353ce3dddd6534bc7635d6e471310ca6689 | True | external=[]; cleanroom=True; max=0.095879s |
| 29454a13477f827c34615300f90a7bdb074ea3c9bcb948f3372bf95fa1fb207d | True | external=[]; cleanroom=True; max=0.105769s |
| c4b72e64acede4053c4b41d797afb562ce2aeadf5d9d0cf58e18aed9baa33c9e | True | external=[]; cleanroom=True; max=0.114511s |
| f6175fd1bc3850f74185e7a813bb5a87d54e7e15212c874133dafc6e1ce91d34 | True | external=[]; cleanroom=True; max=0.139085s |
| 45628c719dc967f81655c19f70e579c55a5758b9fe75a5fcdad9193eebf6a017 | True | external=[]; cleanroom=True; max=0.087705s |
| 0957bac0892defe4416cd8fcd774174e7177eef75b9ad4fff6ce184051bcdd75 | True | external=[]; cleanroom=True; max=0.104339s |
| 9f5e8924c61e9f70dc7f665bd95c0519163ce3d262010feb9659ebf8b558216c | False | external=[{'line': 3112, 'call': "_v92_os.environ.get('V92_SELL_LIB')"}, {'line': 3115, 'call': 'open(path)'}]; cleanroom=True; max=0.000000s |
| 7ac1a2545ea285fa75b6a51b7ea0bbdb5f334f405f20e72b72f8188a1d898a35 | True | external=[]; cleanroom=True; max=0.120847s |
| 5b6297c51c96f2bd92fe5b8558335f585363f9d96aecb9cb9d4e759d170f13f3 | True | external=[]; cleanroom=True; max=0.112751s |
| 939c445771d83901f27478561d0cc3137133e2233b3ef266f26277aa0b2c7714 | True | external=[]; cleanroom=True; max=0.178732s |
| d6565929be5283a5decf00c986359542ee1c106d7819815f8c69ccab35e363dd | True | external=[]; cleanroom=True; max=0.085628s |
| d5a192fac67f00da31fe2bc7b747b8c33766bf1024780c53e49f2292a97db2de | True | external=[]; cleanroom=True; max=0.117359s |
| 2ee689fdc58f38b7bf6b80b8d3f48129d19b47201dbee51fdcbd977498a5106f | True | external=[]; cleanroom=True; max=0.137838s |
| 8045c8872406044cb0b6bf9f80e440f07c250e325618894f4a91141af6d3b6ad | True | external=[]; cleanroom=True; max=0.124935s |
| 1d8c562280d9bbd12f34e58dcd0d85a074b27622a3ee4a50ff8904b7b8130c27 | True | external=[]; cleanroom=True; max=0.095721s |
| 2d7227833871cf92e574115dfa2e8a39d0c1304dc63b019789b352c4fea36fce | True | external=[]; cleanroom=True; max=0.107177s |
| bc8f84641d8e5ae8e083089c79572ed873b0f32dd071572f5efdcf342ec1143f | True | external=[]; cleanroom=True; max=0.119448s |
| ae44d83baf39ae2cf203d3617d0e9d7846d4a8b379b00c3ebd3734f1cfb5fbf3 | True | external=[]; cleanroom=True; max=0.100080s |
| 12ad317ecac6c07fb2c2e10bf4820ecd1fd4551a5a36aa0e34ab93b2c33c2693 | False | external=[{'line': 3587, 'call': "_v92_os.environ.get('V92_SELL_LIB')"}, {'line': 3590, 'call': 'open(path)'}]; cleanroom=True; max=0.000000s |
| 127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652 | True | external=[]; cleanroom=True; max=0.132485s |
| e496a4fe550d26533caa0c284c2915c680e8d339624a1b811165cc74f4c5235b | True | external=[]; cleanroom=True; max=0.145156s |
| 1dfd463070024f85879d642fc294e1848ccfab00aad3f3980a04b0a8eca37fdd | True | external=[]; cleanroom=True; max=0.085728s |
| 3ec06d07c1076dd8fdfe444cb5e19f1789f1e4f8d66597db3b3f70a5e80895fc | False | external=[{'line': 3367, 'call': "_v92_os.environ.get('V92_SELL_LIB')"}, {'line': 3370, 'call': 'open(path)'}]; cleanroom=True; max=0.000000s |
| 919fc1d61050cd96f799979e49177ae3ac7bce98ec9835724238bea73f4a08ed | True | external=[]; cleanroom=True; max=0.088008s |
| cda529cb6b359fc4a9ab124d4d7950d5912bd5de846dcec4be70ca83b7150b2d | True | external=[]; cleanroom=True; max=0.143719s |
| 8378f73c82db7624ce5d0369cf896aa0761a662af147b119f67254f1f8634c56 | True | external=[]; cleanroom=True; max=0.077379s |

| 순위 | SHA | DP40 | NEWMETA40 | 합계 | confirmation DP80 / NEWMETA80 |
|---|---|---|---|---|---|
| 1 | e496a4fe550d26533caa0c284c2915c680e8d339624a1b811165cc74f4c5235b | 0.8 | 0.5 | 0.65 | 0.875 / 0.5 |
| 2 | 127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652 | 0.8 | 0.5 | 0.65 | 0.875 / 0.5 |
| 3 | cda529cb6b359fc4a9ab124d4d7950d5912bd5de846dcec4be70ca83b7150b2d | 0.625 | 0.3 | 0.4625 | 0.75 / 0.2125 |
| 4 | 8378f73c82db7624ce5d0369cf896aa0761a662af147b119f67254f1f8634c56 | 0.525 | 0.25 | 0.3875 | 0.525 / 0.2 |
| 5 | 37d284d4d4d9aff50ee2dce8a6cc2353ce3dddd6534bc7635d6e471310ca6689 | 0.5 | 0.2 | 0.35 | 0.5 / 0.125 |
| 6 | ae44d83baf39ae2cf203d3617d0e9d7846d4a8b379b00c3ebd3734f1cfb5fbf3 | 0.475 | 0.2 | 0.3375 | N/A |
| 7 | 4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01 | 0.475 | 0.2 | 0.3375 | N/A |
| 8 | 1dfd463070024f85879d642fc294e1848ccfab00aad3f3980a04b0a8eca37fdd | 0.4 | 0.2 | 0.3 | N/A |
| 9 | 939c445771d83901f27478561d0cc3137133e2233b3ef266f26277aa0b2c7714 | 0.25 | 0.1 | 0.175 | N/A |
| 10 | c4b72e64acede4053c4b41d797afb562ce2aeadf5d9d0cf58e18aed9baa33c9e | 0.175 | 0.15 | 0.1625 | N/A |
| 11 | bc8f84641d8e5ae8e083089c79572ed873b0f32dd071572f5efdcf342ec1143f | 0.175 | 0.15 | 0.1625 | N/A |
| 12 | 5b6297c51c96f2bd92fe5b8558335f585363f9d96aecb9cb9d4e759d170f13f3 | 0.175 | 0.15 | 0.1625 | N/A |
| 13 | 4889137f1adf1f9266b2ad5a6ac6700c40e9be6dfe3654e39db375fb55b71341 | 0.175 | 0.15 | 0.1625 | N/A |
| 14 | 29454a13477f827c34615300f90a7bdb074ea3c9bcb948f3372bf95fa1fb207d | 0.175 | 0.15 | 0.1625 | N/A |
| 15 | 2d7227833871cf92e574115dfa2e8a39d0c1304dc63b019789b352c4fea36fce | 0.1 | 0.2 | 0.15 | N/A |
| 16 | 1d8c562280d9bbd12f34e58dcd0d85a074b27622a3ee4a50ff8904b7b8130c27 | 0.1 | 0.2 | 0.15 | N/A |
| 17 | d5a192fac67f00da31fe2bc7b747b8c33766bf1024780c53e49f2292a97db2de | 0.05 | 0.2 | 0.125 | N/A |
| 18 | 7ac1a2545ea285fa75b6a51b7ea0bbdb5f334f405f20e72b72f8188a1d898a35 | 0.05 | 0.2 | 0.125 | N/A |
| 19 | f6175fd1bc3850f74185e7a813bb5a87d54e7e15212c874133dafc6e1ce91d34 | 0.075 | 0.1 | 0.0875 | N/A |
| 20 | 8045c8872406044cb0b6bf9f80e440f07c250e325618894f4a91141af6d3b6ad | 0.075 | 0.05 | 0.0625 | N/A |
| 21 | d6565929be5283a5decf00c986359542ee1c106d7819815f8c69ccab35e363dd | 0.025 | 0.1 | 0.0625 | N/A |
| 22 | 0957bac0892defe4416cd8fcd774174e7177eef75b9ad4fff6ce184051bcdd75 | 0.025 | 0.1 | 0.0625 | N/A |
| 23 | dc5433c7996f3f18bc766083a3b6b0ef22ba290cf917fd680ee41c62b8de734d | 0.05 | 0.05 | 0.05 | N/A |
| 24 | 919fc1d61050cd96f799979e49177ae3ac7bce98ec9835724238bea73f4a08ed | 0.05 | 0.05 | 0.05 | N/A |
| 25 | 45628c719dc967f81655c19f70e579c55a5758b9fe75a5fcdad9193eebf6a017 | 0.05 | 0.05 | 0.05 | N/A |
| 26 | a16e0e9b40c489972630a0b9d04f30e9c1cab03159fa78676db74277d84d82ab | 0.025 | 0.05 | 0.0375 | N/A |
| 27 | 2ee689fdc58f38b7bf6b80b8d3f48129d19b47201dbee51fdcbd977498a5106f | 0.025 | 0.05 | 0.0375 | N/A |
| 28 | 2993cf9241b467bbfa317cf8ba13216f4f2b49070c5632984eb2704eb88a2435 | 0.025 | 0.05 | 0.0375 | N/A |

입력·결과: `experiments/search_20260925/tournament-*.json`, `games.jsonl`. 각 행에 artifact/runner/manifest SHA, seed, seat, 상대 기록. Engine1.32.7. 재현: `python3 tools/search_loop.py --queue` (완료 key skip).

다음 행동 두 가지: ① 고정 상대 풀로 calibration 4개 후보를 평가한다. ② EXP-016>EXP-017 필수 쌍을 포함해 4/5 기준을 통과한 metric만 freeze하고, 실패하면 BLOCKED로 종료한다.


---

## `reports/codex/20260925-1958-PARENT-TOURNAMENT-GATE-CORRECTION.md`

# PARENT-TOURNAMENT gate correction

짧은 새 gate가 과거 runtime 실패를 지우지 않도록 전체 기존 측정을 대조했다. NEWMETA의 stage1 최대0.750587초를 포함해 E5 최대0.5초 이상인 SHA는 부모 후보에서 제외한다. 기존 경기와 최초 보고는 보존했다. 다음 screening 순위에서 runtime gate를 만족하는 파일로 상위5개를 채웠으며, 추가 confirmation도 원래 seed2520–2559×양좌석×두 상대를 그대로 쓴다. 성능 미달을 이유로 표본을 늘리지 않았다.

정본 후속 후보 목록: `experiments/search_20260925/tournament-reconciled.json`.

다음 행동 두 가지: ① Coordinator는 첫 보고와 이 gate 정정을 함께 읽는다. ② calibration을 통과하기 전까지 부모 확정·탐색·holdout을 보류한다.


---

## `reports/codex/20260925-2302-METRIC-CALIBRATION.md`

# METRIC-CALIBRATION — BLOCKED

고정 공개 상대 풀 및 tape/proxy 후보로 과거 같은 시점의 hosted 쌍 순서를 재현했다. 잘못된 지표를 무인 최적화하지 않기 위한 사전 확인이다.
[LOCAL] 선택=None; mandatory EXP016>EXP017 포함4/5 통과 조건. 실행 이상=5. 실패면 탐색·holdout을 실행하지 않는다.

| 후보 | 맞힌 쌍 | mandatory pair | 판정 |
|---|---|---|---|
| a | 4 | True | False  |
| b | 4 | True | False  |
| c | 3 | False | False  |
| d | 4 | True | False  |

Tape 방향 일치율=0.25, informative N=4, 사용 mode=public-proxy; 양쪽 Δ=0은 방향 일치 증거에서 제외. 제외율=0.5166666666666667. 팀 LB는 실제 상대 submission rating과 다르다.

세부 scores·정확한 artifact/pool/seed/seat/SHA는 `experiments/search_20260925/calibration-summary.json`, 각 calibration manifest와 games.jsonl에 보존. seed2600–2619×양좌석, 후보 가중치4개만 비교. Panel47 및 holdout9000–9599는 제외.

다음 행동 두 가지: ① 실패했다면 Coordinator가 metric 가설을 다시 설계한다. ② 통과했다면 metric bytes를 동결하고 상위5개 부모를 그 metric으로 비교한 뒤에만 탐색한다.


---

## `reports/codex/20260926-0013-EXP021-STAGE1.md`

STOP

[LOCAL] EXP-021은 Stage 1 본 실행 전에 telemetry smoke에서 중단했다.

- 무엇을 시험했는가: 부모와 H1a/H1b/H2/H3/H4를 seed 5000, 양 좌석으로 O(127ed3e6 exact)와 각 2경기 실행했다. 이 12경기는 사전등록상 Stage 1에 포함될 예정이었으나 이후 588경기는 실행하지 않았다.
- 왜 멈췄는가: H2가 양 경기 모두 step-0 SELL 1단위 감소를 발동하지 못해 첫 턴 현금 차가 0이었다. 사전등록은 H2의 각 smoke 경기에서 현금 차 >= 1을 요구한다.
- 측정 결과: 12/12 valid, candidate exception/caught error/timeout 0. H1a/H1b/H3/H4 telemetry는 양 좌석에서 발동했다.
- 막힌 점: 카드의 H2는 step 0의 첫 SELL 주문을 1 줄이라고 지정하지만, 실제 부모 action에서는 줄일 qualifying SELL이 없었다. 다른 턴이나 다른 주문을 선택하는 것은 카드에 없는 판단이다.

| arm | smoke | 핵심 telemetry seat0 / seat1 | max step (s) | p99 (s) |
|---|---|---|---:|---:|
| P | PASS | race_mirror=1 / 1 | 0.057582 | 0.004488 |
| H1a | PASS | horizon32=476 / 476 | 0.057674 | 0.004235 |
| H1b | PASS | horizon40=476 / 476 | 0.055116 | 0.005166 |
| H2 | FAIL | removed=0/0; cash_diff=0.0/0.0 | 0.043899 | 0.005259 |
| H3 | PASS | escalated32=1 / 1 | 0.046326 | 0.005209 |
| H4 | PASS | step717_units=12 / 12 | 0.037536 | 0.003854 |

Preregistration SHA-256: `bc72d03d5f88b22cab72e7c26105a31e88ff9d8fc9fce474406bd8968d42f487`.
Raw append-only journal: `experiments/mirror_edge_20260926/games.jsonl` (12 rows).
Stage 1 score rate: N/A (600경기 screen 미실행). Stage 2/3/final/release: N/A.
P4 panel: N/A; STOP 이전이므로 판정에 사용하지 않았다.
Submission/Kaggle download/search-loop write/launchd change: none.

다음 행동 2개:
1. Coordinator가 H2의 정확한 대체 조작(턴·주문·현금 차 계산)을 새 카드로 발행할지 결정한다.
2. H2를 제외하고 H1a/H1b/H3/H4만 진행하려면 표본을 보기 전 새 사전등록으로 별도 승인한다.


---

## `reports/codex/20260926-0104-EXP021-STAGE1-V2.md`

FAIL

[LOCAL] EXP-021 v2 Stage 1(4 arm)과 H2′ telemetry gate 결과.

| arm | Stage 1 score rate | W/D/L | pass | activation | max step | p99 |
|---|---:|---:|---:|---:|---:|---:|
| P | 0.5000 | 3/94/3 | True | N/A | 0.127123 | 0.004407 |
| H1a | 0.5000 | 3/94/3 | False | 100.0% | 0.124588 | 0.004612 |
| H1b | 0.5000 | 3/94/3 | False | 100.0% | 0.150300 | 0.005085 |
| H3 | 0.5000 | 3/94/3 | False | 100.0% | 0.143631 | 0.005142 |
| H4 | 0.3300 | 2/62/36 | False | 100.0% | 0.127908 | 0.004996 |
| H2′ | N/A | N/A | False | telemetry gate STOP (8/8 invalid) | 0.050431 | 0.003892 |

H2′ parent step-0 actual action, both seats: `BUY_PRODUCT WHEAT 5`, `BUY_SEED WHEAT 1`; see `experiments/mirror_edge_20260926/h2prime-parent-step0-actions.json`.
SELL이 없었던 이유: `_PIPE_MODE='EarlyCycle'`의 `_pipe_install`이 wrapper 호출 전에 tape step 0 market을 위 두 주문으로 덮어쓴다 (`main.py:6344,6358-6360,6410-6418`).
H2′ STOP 이유: frozen wrapper가 action 기록 중 존재하지 않는 `_json` global을 참조해 8/8 `wrapper_errors=1`, `mutation_count=0`; 규칙에 따라 수정·재실행하지 않았다.
v2 prereg SHA-256: `6d52219747ac476a45d2242d3e7d2621b50b6edc46720cc11250ebe33493d442`; H2′ prereg SHA-256: `bbb20f02d815f4bf693507db5b161338f25d9f1860d79ceddb4eaa79991d63c0`.
기존 v1 smoke 12행은 보존했고, P/H1a/H1b/H3/H4의 10행은 Stage 1에 포함했다. H2 두 행은 v2 판정에서 제외했다.
Submission/Kaggle download/search-loop write/launchd change: none.

다음 행동 2개:
1. 통과 arm이 없으므로 Stage 2·3·release를 실행하지 않고 현재 슬롯을 유지한다.
2. H2′는 새 승인과 새 preregistration 없이는 수정하거나 재실행하지 않는다.


---

## `reports/codex/20260926-0108-EXP021-MIRROR-EDGE.md`

FAIL

1. 무엇을 시험했는가: 127ed3e6 exact 복제본을 상대로 H1a·H1b·H3·H4를 seed 5000–5049 양 좌석에서 screen하고, 별도 seed의 H2′ telemetry gate를 실행했다.
2. 왜 하는가: hosted 127ed3e6 exact 복제본 증가 시 mirror 평균으로 수렴할 위험을 헤지할 비대칭 후보를 찾기 위해서다.
3. 측정 결과: 부모 기준선은 0.5000으로 대칭 gate를 통과했으나 H1a/H1b/H3는 모두 0.5000, H4는 0.3300이었다. Stage 1 통과 arm은 0개다. H2′는 frozen wrapper 구현 오류로 telemetry gate 8/8 invalid STOP이다.
4. 막힌 점과 다음 행동: 통과 arm이 없어 Stage 2·3·release는 실행하지 않는다. 새 승인과 새 preregistration 없이는 H2′를 수정·재실행하지 않는다.

| arm | Stage 1 score rate | W/D/L | Stage 2 primary | DP non-inferiority | guard | activation | runtime max / p99 | 판정 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| P | 0.5000 | 3/94/3 | N/A | N/A | N/A | N/A | 0.127123 / 0.004407s | baseline PASS |
| H1a | 0.5000 | 3/94/3 | N/A | N/A | N/A | 100.0% | 0.124588 / 0.004612s | FAIL |
| H1b | 0.5000 | 3/94/3 | N/A | N/A | N/A | 100.0% | 0.150300 / 0.005085s | FAIL |
| H3 | 0.5000 | 3/94/3 | N/A | N/A | N/A | 100.0% | 0.143631 / 0.005142s | FAIL |
| H4 | 0.3300 | 2/62/36 | N/A | N/A | N/A | 100.0% | 0.127908 / 0.004996s | FAIL |
| H2′ | N/A | N/A | N/A | N/A | N/A | mutation 0/8 | 0.050431 / 0.003892s | STOP |

- `[LOCAL]` 모든 4-arm Stage 1 경기 500/500 valid; candidate exception/caught error/timeout 0.
- `[LOCAL]` H1a/H1b/H3는 부모와 W/D/L이 동일해 복제본 대칭을 깨지 못했다. H4는 부모 대비 score rate −0.17로 악화됐다.
- `[LOCAL]` H2′ gate 8경기는 모두 `_ME_REPORT.wrapper_errors=1`, `mutation_count=0`. frozen wrapper가 parent step-0 action 기록에 존재하지 않는 `_json` global을 사용한 구현 오류다. 기준에 따라 수정·재실행하지 않았다.
- `[LOCAL]` 부모 실제 step 0 action은 양 좌석 모두 `BUY_PRODUCT WHEAT 5`, `BUY_SEED WHEAT 1`이다. SELL이 없는 이유는 `_PIPE_MODE='EarlyCycle'`의 `_pipe_install`이 원 route tape를 wrapper 호출 전에 덮어쓰기 때문이다 (`analysis/daily_scan/20260925/extracted/kaggriculture/main.py:6344`, `:6358-6360`, `:6410-6418`).
- P4 hosted 일치 패널: N/A. Stage 1 통과 arm이 없어 판정에 필요하지 않았다.
- Stage 2·3·final confirmation·E-5 release: N/A. 제출 없음. 슬롯 변경 없음.

Identity:
- v1 prereg SHA-256 `bc72d03d5f88b22cab72e7c26105a31e88ff9d8fc9fce474406bd8968d42f487`
- v2 prereg SHA-256 `6d52219747ac476a45d2242d3e7d2621b50b6edc46720cc11250ebe33493d442`
- H2′ prereg SHA-256 `bbb20f02d815f4bf693507db5b161338f25d9f1860d79ceddb4eaa79991d63c0`
- append-only journal: `experiments/mirror_edge_20260926/games.jsonl`, 510 rows, SHA-256 `ad5be3d9e314318769d192842ffd51efca05ed2591329e052350bd355f13020e`
- summary: `experiments/mirror_edge_20260926/stage1-v2-summary.json`, SHA-256 `653c3ffbbda2d408ab57f41df7870d7b322892e0d6661a4509ccad12239d74b4`

금지 조항 확인: Kaggle 다운로드·제출·holdout·엔진/RNG 수정·search-loop 파일 쓰기·launchd 조작·BOARD/KILLS/HYPOTHESES 직접 수정 없음.

다음 행동 2개:
1. EXP-021의 Stage 2·3·release를 실행하지 않고 현재 DP → 127ed3e6 슬롯을 유지한다.
2. H2′ 구현 오류를 다시 시험하려면 이번 실패를 보존한 새 카드·새 preregistration·별도 seed를 먼저 승인한다.


---

## `reports/codex/20260926-0122-EXP022-H2P.md`

STOP

1. 무엇을 시험했는가: EXP-021의 H2′ wrapper에 누락된 `import json as _json` 한 줄만 추가하고, 본 실행 전 unit gate부터 확인했다.
2. 왜 하는가: EXP-021은 `_json` 미import로 8/8 caught error였으므로, 127ed3e6 exact 상대의 mirror 비대칭 가설 자체가 시험되지 않았기 때문이다.
3. 측정 결과: candidate diff는 정확히 import 한 줄뿐이지만, unit harness가 seat 1의 초기 observation에 없는 `step`을 parent에 넘겨 `KeyError('step')`가 발생했다. pytest는 2 PASS, 1 FAIL이다. candidate 경기·smoke·screen은 0경기다.
4. 막힌 점과 다음 행동: 사전 gate 하나라도 실패하면 재수정하지 말라는 지시에 따라 harness를 고치지 않고 STOP했다. 제출·Kaggle 다운로드·release·D3 gate는 실행하지 않았다.

| gate | 결과 | 수치·근거 |
|---|---|---|
| preregistration freeze | PASS | `experiments/mirror_edge2_20260926/preregistration.json`; SHA-256 `9ca2dca761f49be64fe002e80c6bf46e50defc89244a017eb72ad616c68d4ec5` |
| import-only candidate | PASS | EXP-021 H2′ 대비 추가 1줄 `import json as _json`; candidate SHA-256 `cfa854d5758f9e342197437d47c1e3b5f5efad4b50ba4c2492c7e8178c254912` |
| unit: step-0 exact 1-unit diff | **STOP** | `KeyError('step')` at parent `main.py:6409`; 2 tests PASS, 1 FAIL; action 결과 파일 생성 전 중단 |
| smoke seed 6190 × 양 좌석 | N/A | 0경기 |
| screen candidate/parent seed 6200–6249 | N/A | 0경기 |
| confirmation / final | N/A | 0경기 |
| runtime | N/A | agent call 0회 |

- `[LOCAL]` 실패는 H2′ 전략 결과가 아니라 새 unit harness의 입력 구성 오류다. 따라서 가설 판정은 N/A이며 EXP-021의 FAIL·H2′ STOP 기록도 그대로 유지한다.
- `[LOCAL]` 기존 EXP-021 journal SHA-256 `ad5be3d9e314318769d192842ffd51efca05ed2591329e052350bd355f13020e`, STOP gate SHA-256 `7b2bef3e69c85b7d113c7bbbf1837e8661d8dd83558a81438e938f4bb2a9cd91`, 최종 보고 SHA-256 `5f0c7c1f0009ce122233417e5592fe3649ff1f2cd2fff756f96518c2dde2e7fc`는 재확인했고 수정하지 않았다.
- 새 폴더에는 preregistration, import-only variant/manifest, unit STOP 증거와 result만 있다. `games.jsonl`은 생성되지 않았다.
- 실행한 검증: `python3 -m py_compile tools/mirror_edge_exp022.py` PASS; `python3 -m json.tool experiments/mirror_edge2_20260926/preregistration.json` PASS; `python3 -m pytest -q tests/test_mirror_edge_exp022.py` → 2 PASS, 1 FAIL.
- 금지 확인: 제출, Kaggle 다운로드, holdout seed 9000–9599, `experiments/search_20260925/` write, engine/RNG 수정, 결과 후 seed·기준 변경 없음.

다음 행동 2개:
1. EXP-022를 이 STOP 상태로 보존하고 현재 DP → 127ed3e6 활성 슬롯을 유지한다.
2. H2′를 다시 시험하려면 unit harness의 seat 1 observation 구성 수정 범위를 명시한 새 승인·새 experiment ID·새 preregistration을 먼저 발행한다.


---

## `reports/codex/20260926-0133-EXP022-H2P.md`

STOP

1. 무엇을 시험했는가: EXP-021에서 wrapper import 오류로 시험되지 않은 H2′를 import 한 줄만 고쳐 새 seed로 재시험했다.
2. 왜 하는가: 127ed3e6 exact 복제 상대의 native mirror 판정을 피하면서 우리만 horizon 24를 쓰는 비대칭이 승률을 높이는지 확인하기 위해서다.
3. 측정 결과: unit gate는 PASS했다. seed 6190 smoke 8경기는 전부 valid이고 wrapper error 0이었지만, 127ed3e6 양 좌석에서 expected cash difference −25와 actual −28의 차이가 3으로 frozen tolerance 2를 넘었다. 따라서 `our_mirror=0`이어서 smoke gate FAIL이다.
4. 막힌 점과 다음 행동: candidate의 mirror 판정 규칙이 실제 첫 턴 현금 차를 받아들이지 못했다. candidate 로직·tolerance를 바꾸지 않고 STOP했으며 screen 이후 단계, 제출, Kaggle 다운로드는 실행하지 않았다.

| gate | result | metric |
|---|---|---|
| unit step-0 one-unit diff | PASS | rows=2 |
| seed 6190 smoke | **STOP** | O 양 좌석 expected=−25, actual=−28, `wrapper_errors=0`, `our_mirror=0`, opponent `race_mirror=0`; nonmirror 6/6 `our_mirror=0` |
| screen H2′ | N/A | N/A |
| screen parent | N/A | N/A |
| confirm vs O | N/A | N/A |
| DP paired | N/A | N/A |
| public-15 guard | N/A | N/A |
| nonclone false mirror | N/A | N/A |
| final vs O | N/A | N/A |
| runtime all executed games | PASS | invalid=0; exceptions=0; caught=0; max=0.114003s; p99=0.003535s |

- Preregistration SHA-256: `9ca2dca761f49be64fe002e80c6bf46e50defc89244a017eb72ad616c68d4ec5`.
- Candidate SHA-256: `cfa854d5758f9e342197437d47c1e3b5f5efad4b50ba4c2492c7e8178c254912`; source H2′ SHA-256: `b75819d19e780805131314b57a5c6ae0d3c6c006edb28da1847e7a0920f08ff8`.
- Journal: `experiments/mirror_edge2_20260926/games.jsonl`, rows=8, SHA-256 `5804303a4cc3d85de7bec088ae0ec78e7350c6a2556a1ca2670cb7bf9851153e`.
- 기존 EXP-021 결과·STOP 파일은 읽기만 했고 수정하지 않았다.
- 금지 확인: 제출·Kaggle 다운로드·holdout 9000–9599·search-loop write·engine/RNG 수정 없음.

Harness 수정 내역(사람 승인 09-26 01:30 KST):

| 파일·줄 | 수정 | 이유 |
|---|---|---|
| `tools/mirror_edge_exp022.py:55` | runner self-SHA를 protected input 검사에서 제외 | 명확화된 protected 범위는 candidate bytes, 가설·기준, seed·경기 수이며 harness 수정은 허용됨. parent·상대·engine·candidate SHA 검사는 유지 |
| `tools/mirror_edge_exp022.py:154-155` | 초기 observation을 복사하고 누락 시에만 `step=0` 보완 | `env.reset(2)`의 seat 1 direct-call observation에 `step`이 없어 이전 unit harness가 candidate 평가 전에 `KeyError`를 냄 |

- 수정 기록: `experiments/mirror_edge2_20260926/harness-fix-0130.json`.
- 이전 STOP 보존: `coordination/reports/codex/20260926-0122-EXP022-H2P.md`, `experiments/mirror_edge2_20260926/unit-gate-error.json`, `result-stop-0122.json`.
- protected artifact 불변: preregistration SHA-256 `9ca2dca761f49be64fe002e80c6bf46e50defc89244a017eb72ad616c68d4ec5`; candidate SHA-256 `cfa854d5758f9e342197437d47c1e3b5f5efad4b50ba4c2492c7e8178c254912`.
- `[ENGINE]` 원인 진단: market은 주문을 unit별 lockstep으로 처리하고(`kaggriculture.py:583-628`), `BUY_PRODUCT` 가격은 매 unit마다 바뀐 inventory에서 다시 quote한다(`:598-601`). 양쪽 첫 4단위가 체결된 뒤 상대만 사는 5번째 WHEAT의 실제 marginal quote는 28이므로, 초기 표시 quote 25를 expected difference로 쓴 frozen rule과 3 차이가 났다. `smoke-cash-difference-diagnostic.json`에 재현값을 보존했다. 이 진단 뒤 candidate는 수정·재실행하지 않았다.
- HYP-0006 event: `coordination/hypotheses/codex/EVT-2026-09-25T163448.402688+0000-158ce6af.json`; `python3 tools/validate_hypotheses.py --strict` → 37 entries PASS. 이 event는 H2′ 효과를 N/A로 기록하고 frozen implementation smoke failure와 구분한다.

다음 행동 2개:
1. EXP-022를 이 STOP 상태로 보존하고 screen·confirmation·release·E-5·D3 gate v2를 실행하지 않는다.
2. H2′를 다시 시험하려면 cash difference의 3-unit discrepancy를 설명하고 candidate mirror 규칙 변경을 새 experiment ID·새 preregistration·사람 승인으로 분리한다.


---

## `reports/codex/20260926-0212-EXP023-MAC-SHARD.md`

# EXP-023 Mac shard 실행 보고

**VERDICT: COMPLETE — cross-check 6/6 일치, 본 실행 930/930 완료, ERROR 0. 결과의 순위·성능 판정은 하지 않았다.**

1. **무엇을 바꾸거나 시험했는가:** EXP-023 screen 후반부 `jobs-screen-mac.json` 930경기를 Mac에서 5 worker로 실행했다. 허용된 인프라 변경은 `run.py`의 `Pool(2)` → `Pool(5)` 한 줄뿐이다.
2. **왜 하는가:** Claude cloud shard와 합치기 전에 같은 engine·source에서 rewards가 정확히 재현되는지 확인하고, 승인된 Mac shard 원자료를 생산하기 위해서다.
3. **무엇을 측정했고 결과가 어땠는가:** cross-check rewards 6/6 exact match. 본 실행은 930/930, unique key 930, missing 0, extra 0, runner ERROR 0, `DONE/DONE` 아닌 행 0, `None` reward 행 0이었다. wall time은 1,231.52초(20분 31.52초)였다.
4. **무엇이 막혀 있고 다음 행동은 무엇인가:** 실행 blocker는 없다. 결과 순위·해석·판정은 사전등록대로 Claude가 수행해야 한다. 제출은 하지 않았다.

## 환경과 identity

- `[LOCAL]` Python: `~/kaggle/Kaggriculture/.venv/bin/python`, Python 3.13.14
- `[LOCAL]` `kaggle-environments==1.32.7`
- `[LOCAL]` engine: `.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`
  - SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` — 요청값 일치
- `[LOCAL]` parent: `experiments/exp023_mirror_screen/parent.py`
  - SHA-256 `e496a4fe550d26533caa0c284c2915c680e8d339624a1b811165cc74f4c5235b`
- `[LOCAL]` opponent: `experiments/exp023_mirror_screen/opp127.py`
  - SHA-256 `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- `[LOCAL]` `variants.json`와 `variants.claude.json`
  - 양쪽 SHA-256 `63c1196886b06f007c0efd986dddda06bef32ca3cf7218499df226c0de6113d9` — 일치

## 교차 기계 재현 검사

원자료: `experiments/exp023_mirror_screen/cross-check.jsonl`

| key | Mac rewards | cloud-reference rewards | 결과 |
|---|---:|---:|---|
| `P|7000|0` | `[122618.0, 122618.0]` | `[122618.0, 122618.0]` | PASS |
| `P|7000|1` | `[122618.0, 122618.0]` | `[122618.0, 122618.0]` | PASS |
| `P|7001|0` | `[68950.0, 68950.0]` | `[68950.0, 68950.0]` | PASS |
| `v000|7000|0` | `[122618.0, 122618.0]` | `[122618.0, 122618.0]` | PASS |
| `v000|7000|1` | `[122618.0, 122618.0]` | `[122618.0, 122618.0]` | PASS |
| `v001|7000|0` | `[3000.0, 201841.0]` | `[3000.0, 201841.0]` | PASS |

- cross-check: **6/6 PASS**
- `cross-check.jsonl` SHA-256: `7bd7c7551b443a1adf54f2c9150327766067ebb9094173117292cf3050c3df32`

## 본 실행

- 재현 명령: `cd experiments/exp023_mirror_screen && ../../.venv/bin/python run.py jobs-screen-mac.json`
- 입력: 930 jobs, seed 7000–7004, holdout seed 9000–9599 사용 0
- 완료: **930/930**
- unique key: **930**
- missing / extra: **0 / 0**
- runner `err != null`: **0**
- statuses가 `DONE/DONE`이 아닌 행: **0**
- `None` reward 행: **0**
- wall time: **1,231.52초 (20분 31.52초)**
- 원자료: `experiments/exp023_mirror_screen/games.jsonl`
- 원자료 SHA-256: `c1e45e5bdd425d2ed94ef24d22e0f62e76f8e25441dc00ec59e154e3b335098e`

## Stage 3 병행 준비

- 파일: `experiments/exp023_mirror_screen/stage3-opponents.json`
- 구성: DP 0924 exact 1개 + public 추천 상위 15개
- 선택 규칙: `tools/search_optimize.py` checkpoint guard와 동일하게 20260922–25 `lineage.json`의 SHA별 최대 `votes`, 이어서 SHA를 내림차순 정렬. DP는 별도 1개로 두고 public top-15에서 중복 제외.
- 16개 경로의 현재 SHA-256: **전부 일치**
- manifest SHA-256: `e5ae6ca2957dde5dc3b4f5310ac03530b7bfd6b1aa674e7c2bd20564f46a9ec8`

## 범위 준수

- Kaggle 제출: 하지 않음
- 다운로드: 하지 않음
- holdout seed 9000–9599: 사용하지 않음
- engine/RNG 수정: 하지 않음
- 다른 experiments 폴더 쓰기: 하지 않음
- 결과 순위·해석: 하지 않음

`COMPLETE | cross-check 6/6, 본 실행 930/930·ERROR 0 | games.jsonl c1e45e5b…5098e | 20분 31.52초, key 완전성 PASS | NEXT: Claude 판정 및 cloud shard 병합 검증`

다음 행동 두 가지:

1. Claude가 frozen preregistration에 따라 cloud shard와 Mac shard를 합쳐 판정한다.
2. 합친 뒤에도 source/variant SHA와 key 중복·누락을 다시 확인하고, 별도 승인 전에는 stage 3 경기나 제출을 실행하지 않는다.


---

## `reports/codex/20260926-1151-EXP023-STAGE3.md`

SUCCESS | v171만 A–E 전부 통과, release·E-5·D3 gate v2 PASS | main.py 496460f8…0bd5 / tar 998b46c5…fa1a | Stage 3 4,000/4,000 DONE·invalid 0 | NEXT: 사람 제출 판단, Coordinator ledger 연결 보완

# EXP-023 Stage 3 실행 보고

1. **무엇을 바꾸거나 시험했는가:** Stage 2 통과 후보 v171·v173·v111·v074를 127ed3e6 exact, DP 0924 exact, frozen public 14개에 대해 카드 그대로 비교했다. 5 worker로 4,000경기를 실행했다.
2. **왜 하는가:** 거울 대결에서 좋아진 후보가 DP 및 공개 상대에 회귀하지 않는지 A–E gate로 확인하고, 통과 시 exact release를 만들기 위해서다.
3. **무엇을 측정했고 결과가 어땠는가:** v171만 A–E 전부 통과해 SUCCESS로 선택됐다. release 필수 gate, E-5, D3 gate v2도 PASS했다.
4. **무엇이 막혀 있고 다음 행동은 무엇인가:** 제출은 사람만 할 수 있으므로 실행하지 않았다. EXP-023 preregistration에 `hypothesis_id`/`test_id`가 없어 공용 원장 event는 사후에 임의 생성하지 않았다. Coordinator가 원장 연결을 보완한 뒤 사람이 FIFO상 DP 56518910 은퇴를 포함해 제출 여부를 판단해야 한다.

## 고정 입력과 완전성

- 사람 승인: 2026-09-26 09:55 KST, Stage 3 별도 승인.
- 실행 카드: `coordination/proposals/claude/20260926-EXP023-STAGE3-CODEX.md`, SHA-256 `9040349f64486109322f71dcecb83b041b7d05bb02f3dfe876349ec5c907af29`.
- preregistration: `experiments/exp023_mirror_screen/preregistration.json`, SHA-256 `644e9ba5eaf48770edce4a8cf3e8d2780e088fef4e8e245c43dd6fbc0944d127`.
- engine: kaggle-environments 1.32.7, `kaggriculture.py` SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`.
- jobs: 4,000개, `jobs-stage3.json` SHA-256 `b0e58b9a5c68c65109f09cb584a64ec4b104c8741730581f553e63644ead41e3`.
- raw: 4,000행 / unique key 4,000 / missing 0 / extra 0 / duplicate 0 / err 0 / non-DONE 0 / score None 0.
- `games-stage3.jsonl` SHA-256 `8a8bbe0f8c4865d80851107ec88bbdd97e18341417ac0847020ca89fc7297a49`.
- `stage3-summary.json` SHA-256 `57d98487cf15ea4b9423af1231fe3ba368f6f6d3bc310274bba0ac1963eb9cc9`.
- B와 D는 2,000회 bootstrap, 고정 RNG seed 23023. 단위는 opponent×seed에서 양 좌석 평균이다.

## 후보별 A–E

| 후보 | A: vs 127 score / Wilson99 하한 | B: vs DP Δ / boot95 하한 | C: Δ<−0.10 파일 | D: pooled Δ / boot95 하한 | E: invalid / max step | 최종 |
|---|---:|---:|---:|---:|---:|---|
| v171 | 0.8075 / 0.7519 | +0.0250 / −0.0050 | 0 | +0.0313 / +0.0104 | 0 / 0.4275s | **PASS** |
| v173 | 0.6700 / 0.6071 | 0.0000 / −0.0300 | 0 | +0.0125 / −0.0042 | 0 / 0.5012s | FAIL(E) |
| v111 | 0.8350 / 0.7818 | +0.0200 / −0.0450 | 10 | −0.1000 / −0.1563 | 0 / 0.3814s | FAIL(C,D) |
| v074 | 0.6950 / 0.6329 | 0.0000 / −0.0300 | 0 | +0.0104 / −0.0063 | 0 / 0.5499s | FAIL(E) |

선택 규칙에 따라 전 gate 통과 후보 중 v171을 선택했다. v111은 A가 더 높지만 public guard와 pooled guard를 실패했으므로 선택 대상이 아니다.

## Release와 후속 gate

- 선택 후보: `v171`, one change `_DP_H` 8→9.
- variant/release `main.py` SHA-256: `496460f81869ebbd1bf80f3dd3c9440ef72c41819a831ee39a16f180d7c0bd5d` — byte-identical.
- release: `releases/mirror-screen-v171/`.
- `submission.tar.gz` SHA-256: `998b46c5e677a5f69500a0955fce781c07b2e8078e855fa1084fd55efe40fa1a`.
- tar members: `main.py` 한 개. 최초 macOS tar에 생긴 `._main.py`는 gate에서 발견해 결과 실행 전에 tar만 다시 만들었고, 최종 tar에는 없다.
- clean-room last callable: `search_entry`; `__file__` 의존 없음. reachable 외부 파일/network/env 호출 0, non-stdlib import 0.
- E-5 vs 127ed3e6 exact, seed 2300–2309 양 좌석: **11W/8D/1L, score 0.75 ≥ 0.70**, invalid 0, max step 0.2497s. raw SHA-256 `14db07d337ddd01b712df6a8cd319d940b763033a7ac1326a1329be6c3f693f4`.
- action schema 양 좌석 1,438 calls: schema error 0, `hands` 길이 불일치 0, 2/2경기 `DONE/DONE`. 결과 SHA-256 `f634de8912495832edc76ac1806a80a6a1fa4f55c1eab12976952e572bc22766`.
- D3 gate v2 15경기: **PASS**, invalid 0, max step incl. cold load 0.10677s, max p99 0.00798s, max total/game 0.92689s, engine SHA PASS. 결과 SHA-256 `4259352dc1e50f02951bb8009f14c25ad305e1526b954a7dc5f9fe571cbab215`.

Identity:  제출 파일 SHA-256 = 성능을 측정한 파일 SHA-256 인가?      [x]
Schema:    루트 main.py / agent(obs) / hands 길이 정렬 / 절대 raise 안 함  [x]
Runtime:   에피소드 예산(§6)의 70~80% 이내인가? p99 턴 지연 기록      [x]
Isolation: 빈 폴더 clean-room 에서 tar 풀고 import 성공했는가?        [x]
License:   외부 코드·상대 봇·데이터의 라이선스가 Rules 를 만족하는가?   [x]
Ledger:    submission ID ↔ artifact SHA ↔ 에피소드를 연결했는가?       [ ] N/A — 제출하지 않음

## 범위 준수

- Kaggle 제출: 하지 않음.
- Kaggle 다운로드: 하지 않음.
- holdout seed 9000–9599: 사용하지 않음.
- engine/RNG: 수정하지 않음.
- 다른 experiments 폴더: D3 gate v2의 승인된 결과 파일 외에는 쓰지 않음.
- `run.py`는 기존 5 worker를 유지하고 출력 파일 환경변수 1줄만 추가했다. public 14개에서 기존 resume key 충돌을 피하려고 job `vid`에 panel/opponent label을 포함했다.

다음 행동 두 가지:

1. 사람이 `releases/mirror-screen-v171/submission.tar.gz`의 SHA-256 `998b46c5…fa1a`를 확인하고, 제출 시 DP 56518910이 은퇴한다는 FIFO 비용을 검토해 제출 여부를 결정한다.
2. Coordinator가 EXP-023의 누락된 `hypothesis_id`/`test_id`를 정본에 연결하고, 제출 시 submission ID ↔ artifact SHA ↔ episode를 HOSTED_LEDGER에 기록한다.


---

## `reports/codex/20260927-1036-REVIEW-0927.md`

# REVIEW-0927 — EXP-026/027 및 남은 제출 2회 독립 검토

VERDICT | EXP-026의 open-loop 효과는 구조적으로 낙관 편향될 수 있고, 0.22N+0.78D는 hosted 기대값 추정식으로 정당화되지 않는다. 55be5d5f는 원인 후보이나 인과 증거가 없고 즉시 exact 제출은 고위험이다. | 지정 10개 파일만 읽음 | 경기·제출·다운로드 없음 | NEXT: 1회차 조건부 55be5d5f, 2회차 보류

## 범위
- Claude 결론을 전제로 채택하지 않았다. 질문에 주어진 rating·대전 점수·runtime은 별도 파일 증거가 아니라 `질문 전제`로 취급한다.
- 현재 허용 자료에는 EXP-027 결과, 실제 hosted 상대 lineage, 55be5d5f의 release/License 검증이 없다.

## 1. EXP-026 open-loop 편향과 w067
- 결론: **편향 경로가 명확히 존재한다.** 후보가 선매도로 시장·재고 상태를 바꿔도 상대는 현재 observation을 보지 않고 원 replay의 step별 action을 반환한다(`common26.py:46-58`). 그 action이 새 상태에서 비최적·부분체결·no-op이어도 상대는 다음 행동을 재계획하지 않는다.
- 더구나 `invalid`는 episode status, 우리 agent error/action count만 검사하며 상대 action의 합법성·체결량·반응 부재를 계측하지 않는다(`common26.py:62-64`). 판매 타이밍 경쟁 후보에 특히 유리한 counterfactual이다.
- tape 자체의 lineage 검증은 타당하다. 반대 seat가 127ed3e6 FULL이고 near-clone seat가 중간에 갈라지는지 검사한다(`refilter.py:9-15`); 다만 이것은 tape의 **출처**만 검증하며 closed-loop 타당성을 검증하지 않는다.
- w067은 stage2에서 v074 대비 dScore `+0.39375`, lower95 `+0.315625`, dMargin `+431.7375`였다(`stage2-summary.json:15-25`). 그러나 동일 change가 EXP-024 v111이며 public/hosted guard 실패로 EXP-027 combo에서 명시적으로 제외됐다(`prepare27.py:10-16`).
- 판정: w067 +0.39가 open-loop 편향의 산물일 가능성은 **상당함**. 전부가 artifact라고 수치화할 증거는 없지만, closed-loop 일반화 증거로 사용하면 안 된다.
- 확신도: 편향 경로 **높음(0.95)**; w067 효과의 상당 부분이 편향이라는 판단 **중상(0.75)**.

## 2. judge27 판정·선택 규칙
- 결론: hard gate들은 보수적 guard로 해석 가능하지만, `0.22*N + 0.78*D`를 expected hosted gain으로 부르는 것은 **결함**이다(`judge27.py:39-45`).
- 22/101은 v171 과거 표본의 관측 비율일 뿐 v074·새 후보의 미래 matchmaking 확률이 아니다. 원 보고도 127ed3e6 변형을 22/101로 분류했을 뿐이다(`20260926-2140-EXP025-ANALYSIS.md:8-17`). 단순 binomial 불확실성도 대략 14%~30%라 22% 고정은 과도하게 정밀하다.
- N과 D는 모집단의 상보 분할이 아니다. N은 선발에 이미 쓴 160개 open-loop tape이고(`judge27.py:24-26,36-38`), D는 DP 100 seed와 24 guard×10 seed를 한 pool로 합친 임의 mixture다(`prepare27.py:37-39`; `manifest.json:132-149`).
- 따라서 winner's curse와 mixture mismatch가 함께 있다. 반면 실제 hosted 121 rows의 H는 non-inferiority gate일 뿐 selection score에는 0% 가중된다(`judge27.py:33-45`; `manifest.json:133-135`).
- 판정: 22%는 **가설용 sensitivity weight**로는 쓸 수 있으나 단일 선택식의 정당한 근거는 아니다. 선택은 H/closed-loop 결과를 우선하고 N은 보조 진단으로 낮춰야 한다.
- 확신도: 규칙 결함 **높음(0.90)**; 적정 대체 weight는 자료 부족 **낮음(0.30)**.

## 3. 55be5d5f 원인 가능성과 exact 제출 위험
- 결론: 동시 rating 하락의 **가능한 원인 후보**이나, 현재 파일로는 인과 귀속 불가다. manifest는 해당 파일 SHA와 09-27 guard 편입만 증명한다(`manifest.json:107-110`); 실제 v171/v074가 hosted에서 이 파일을 만났다는 episode lineage는 없다.
- 질문 전제의 v074 상대 0.75, 127ed3e6 상대 0.875는 위협 신호다. 그러나 prepare27의 G27 panel은 각 파일당 고정 10 seed·양 seat뿐이다(`prepare27.py:24-25,39`). 직접대결 표본과 전체 rating 환경은 다르다.
- exact 제출 위험은 **높음**: 질문 전제 max step 0.56s는 EXP-027 frozen E `<0.5s`를 위반한다(`judge27.py:7,39-43`). 또한 allowed evidence에는 License, clean-room import, 제출 artifact identity, episode-budget tail, hosted 다양성 증거가 없다.
- 판정: 원인 가능성 **중간(0.50)**, 인과 결론 **낮음(0.20)**; 즉시 exact 제출의 risk **높음(0.85)**.

## 4. 남은 제출 2회 최선 배분
- **1회차(다음, v171 은퇴): 55be5d5f에 조건부 배정.** 이유는 두 incumbent 상대 신호가 가장 강하고 v171의 알려진 near-clone 약점(22판 3/3/16)과 방향이 맞기 때문이다(`20260926-2140-EXP025-ANALYSIS.md:11-19`). 단, License·identity·schema·clean-room·runtime/episode budget을 통과하지 못하면 제출하지 않는다.
- **2회차(v074 은퇴): 지금 배정하지 않는다.** 1회차 hosted evidence와, open-loop N을 selection score에서 분리한 EXP-027 closed-loop/H 판독 뒤에만 사용한다. 검증된 distinct 후보가 없으면 제출권을 소진하지 않고 v074를 유지한다.
- FIFO상 두 번을 연속 실행하면 검증된 두 incumbent를 모두 잃는다. 따라서 “2회 남음”은 quota가 아니라 최대치로 취급한다.
- 확신도: 1회차 우선순위 **중간(0.65, preflight 조건부)**; 2회차 보류 **높음(0.90)**.

## 다음 행동
1. 55be5d5f의 License·exact artifact·clean-room·runtime tail을 독립 preflight하고, 하나라도 실패하면 1회차를 중단한다.
2. EXP-027은 H와 closed-loop guard로 재순위화하고 open-loop N은 sensitivity 분석으로만 제시한 뒤, 1회차 hosted 결과 전에는 2회차를 쓰지 않는다.


---

## `reports/codex/20260927-1156-REVIEW-0927B.md`

판정: A 조건부 타당 / B 조건부 타당 / C 조건부(즉시 중단은 부적절) / D 조건부 타당.

# REVIEW-0927B — 55be5d5f·EXP-028/029·marketshock 독립 재검토

범위: 지정 파일만 읽고 기존 JSON/JSONL을 재집계했다. 새 경기·제출·다운로드·코드 변경 없음. 현재 rating, deadline, FIFO는 지정 파일로 확인할 수 없어 `질문 전제`다.

## 1. 판단 A — EXP-028가 hosted 열세를 뒷받침하는가
- 결론: **HOLD는 타당, “hosted에서 불리함이 확정”은 과함**. 확신도 0.85/0.70.
- 설계는 D/P를 같은 opponent·seed·seat에 놓고, O1 100 seed, DP 50, guard 23개×10을 양 seat로 실행한다(`prepare28.py:11-20`). 판정식도 결과 전 고정됐다(`judge28.py:1-2,14-25`).
- raw 1,962행 재집계: direct D-v074 0.880; O1 D/P 0.885/0.870; DP 0.860/0.860; guard D/P 0.8217/0.9674, 파일별 D 열세/동률/우세=19/3/1. summary와 일치(`summary.json:3-18,676-754`).
- hosted-replay 121행은 D/P 0.85124/0.92562, Δ=-0.07438; discordant 6승/15패(100동률), sign-test two-sided p=0.0784. row bootstrap 95%=[-0.14876,0.0]라 음의 신호는 강하지만 5% 유의 우월성 검정은 아니다.
- 121행 중 episode 112681752가 중복되어 unique=120, 재집계 Δ=-0.075. opponent path는 27개뿐이므로 121 iid row bootstrap은 유효 표본수를 과장한다. path-cluster bootstrap도 95%=[-0.14286,0.0].
- pooled Δ=-0.08421은 O1 100, DP 50, guard 230 seed를 seed 동일가중한 임의 mixture다(`judge28.py:19-22`); 미래 matchmaking 비율이 아니다.
- 반대 해석 경로: D는 v074를 직접 0.88로 이기고 O1에도 +0.015라 near-clone-heavy 환경에서는 유리하다. H는 과거 상대·seed·seat 재실행이지 실제 미래 hosted 표본이 아니며 중복·cluster·mixture shift가 있다.

## 2. 판단 B — 17% 손익분기
- 결론: **계산은 맞고 예측값으로는 조건부**. 확신도 계산 0.99, 미래 적용 0.35.
- games.jsonl 재계산: non-clone 점수 D=103/121=.85124, P=112/121=.92562; D-v074=.88이므로 v074-D=.12로 둔다.
- clone 비중 x에서 `D=.5x+.85124(1-x)`, `P=.12x+.92562(1-x)`; 동률 해 `x=.07438/(.38+.07438)=.16370`, 즉 **16.37%**.
- 일반식은 `x=(b-a)/[(c-p)+(b-a)]`: a/b=non-clone D/P, c/p=clone 상대 D/P. clone advantage `(c-p)`가 .20/.30/.38/.50/.60/.80이면 break-even은 27.11/19.87/16.37/12.95/11.03/8.51%. non-clone 효과도 균일하지 않으면 단일 x 자체가 무효다.
- v171 CSV 107행 재집계: 127ed3e6 FULL 26, variant 22, 기타 FULL 6, 기타 53; 127 lineage 48/107=44.9%(`opponents.csv:2-108`). Claude의 101 분모에서는 48/101=47.5%(`EXP025-ANALYSIS.md:8-17`).
- 이 표본은 09-26이고 55be5d5f는 09-27 공개라 confirmed 55be family는 0이다. 미래의 증거 기반 범위는 **0~44.9%(101 분모면 47.5%)**라는 느슨한 ceiling뿐이며, 17%가 현실적이라는 좁은 추정은 N/A.

## 3. 판단 C — EXP-029 중단/EXP-030 전환
- 결론: **EXP-030 우선 방향은 타당하나 현재 screen 즉시 중단은 부적절**. 확신도 0.80.
- 확인 시점 games-screen은 398행/398 unique, 40 vid, invalid 0. prep 기준 vid당 2 opponents×5 seeds×2 seats=20이므로 예상 800의 약 50%다(`prep29.py:24-38`). 남은 screen은 끝내되, public/H guard 없는 EXP-029 stage2는 자동 진입하지 않는다.
- EXP-029는 parent self-play와 127만 보며 screen 10게임/opponent, stage2 60게임/opponent다(`prep29.py:37-42`); 판정도 일반 guard 없이 O1/O2 absolute score다(`judge29.py:1-3,13-27`). 제출 근거로 부족하다.
- EXP-030 기술 가능: tail은 `_S1003_PARENT=step1002...`에서 `_S1009_PARENT=step1008...`까지 선형 alias chain이다(`main.py:9983-10000,10006-10023,10120-10137`). 단 Step1002 compaction과 공유 state/telemetry 때문에 “40층 독립 on/off”는 자동 보장되지 않는다.
- 제안 screen: 각 variant는 정확히 한 wrapper bypass, fresh seeds 14000..14009, 양 seat, v074+127(variant당 40게임); invalid=0, max_step<0.8, action_sha가 parent와 다름, 각 상대 score ≥ parent-0.05인 후보만 진출, 최대 6개.
- 제안 final: fresh seeds 14100..14149, 양 seat, v074+127(각 100게임), EXP-028 guard 23개×10 seeds×양 seat(460), hosted-replay unique 120행. invalid/agent_error=0, action_count=719, max_step<0.8을 hard guard로 둔다.
- 통과: v074·127 각각 candidate-parent paired Δ lower95>-0.03; guard는 candidate-parent Δ point>0 및 lower95≥0; hosted-replay candidate-v074 Δ point≥0 및 lower95>-0.03. no-effect·한 opponent라도 -0.10 초과 열화·동일 episode 중복은 탈락. 기준/seed는 실행 전 freeze한다.

## 4. 판단 D — marketshock loader·강도·License
- 결론: **last-callable loader 전제에서는 맞지만 실제 강도와 제출 권리는 미확정**. 확신도 loader 0.95, 무행동 0.75, License 0.70.
- SHA는 853472b44579…로 일치. 최후 top-level function은 `install_water_repair_local_patch`이고 마지막 줄은 기존 `agent` 이름에 closure를 재할당한다(`marketshock...main.py:5986-5994`). 기존-name 재할당은 dict insertion order를 옮기지 않으므로 “globals의 마지막 callable” loader는 installer를 고른다.
- installer는 observation을 parent 인자로 받아 action dict가 아닌 function을 반환한다. loader가 이를 PASS/no-op으로 정규화하는지는 허용 파일에 loader source가 없어 조건부다.
- 실제 1위 강도에는 notebook의 packaging/export cell, 실제 submission artifact bytes+SHA, 선택 entrypoint, submission ID와 hosted episodes가 필요하다. **패키징 코드는 확인해야 한다**; 이번에는 다운로드 금지라 실행하지 않았다.
- metadata License는 `other`(`dataset-metadata.json:2-7`)지만 파일은 Apache-2.0 header/license를 포함한다(`marketshock...main.py:1-20`). metadata-source 충돌과 추가 layer 권리·Rules는 현재 자료로 해소되지 않으므로 파생 제출은 HOLD; opponent-only 평가도 별도 Rules 확인 후다.

## 5. 남은 제출 1–2회 배분
- 55be5d5f exact와 현재 marketshock은 0회 배정. 다음 제출은 **EXP-030 통과 후보 1개에만 조건부**로 써서 질문 전제상 v171을 교체하고 v074를 보존한다.
- 두 번째는 첫 후보의 hosted evidence와 distinctness를 보기 전 보류한다. EXP-030이 위 gate를 못 넘거나 첫 후보가 v074보다 낫다는 증거가 없으면 제출하지 않고 v074 유지. 확신도 0.85.

## 6. Claude의 행동·질문에 대한 직접 답
- 행동 (a): EXP-029 screen만 완주, stage2 보류, 즉시 EXP-030을 우선 설계/실행. (b): 1위 notebook 패키징 코드는 확인하되 다운로드·사용은 별도 승인과 License/Rules 확인 뒤.
- 질문 (a): v074 hosted episodes를 재수집해 opponent submission ID로 cluster하고, replay의 719-step action signature를 같은 seed/seat의 55be5d5f exact와 비교한다. 이는 행동 동일성만 증명하며 artifact 동일성은 못 증명한다. N≈100이면 약 71,900 turn 비교; local 계산은 작고 API/replay 수집이 주비용(수 시간+rate limit)이다.
- 질문 (b): 09-28 12:00 KST까지 local gate를 freeze/완료해 1차 여부를 정하고, 09-29 12:00 KST 또는 첫 후보 valid hosted ≥50 중 늦은 시점에 2차를 결정한다. v074가 경계 30점 이내면 유지; 30점 밖이고 새 후보가 위 gate와 runtime/License/identity를 모두 통과할 때만 risk를 쓴다. 이 30점은 효용 기반 운영선이지 실험 추정치가 아니다.

## 7. 놓친 위험·대안
- exact release runtime log는 15개 측정 뒤 gate script가 TypeError로 종료한다(`gate-d3-cloud.log:16-23`); NOTICE의 runtime 요약(`NOTICE.txt:7-8`)만으로 gate 완료를 주장하면 안 된다.
- EXP-028 H 중복·27-path clustering, EXP-029의 unpaired Wilson/guard 부재, EXP-030 wrapper 간 shared state와 no-effect가 주요 누락 위험이다. 더 나은 대안은 “층 40개 전수”보다 tail 1003~1009부터 역순 single bypass하고 telemetry changed가 큰 층만 확장하는 것이다.
- 현재 최선 결론은 **55be5d5f exact HOLD 유지, EXP-029 screen 회수, EXP-030만 조건부 추진**이다.

## 사람이 결정할 항목 2개
1. EXP-029 screen 완주 후 stage2를 건너뛰고 EXP-030 frozen card로 전환할지 승인.
2. 별도 승인으로 notebook packaging/License/Rules를 확인할지, 그리고 09-28/29 decision cutoff를 채택할지 결정.


---

## `reports/codex/20260927-1615-HYPGEN.md`

가장 유망한 가설: **step 92에서만 확인되는 55be 계열 신호로 gate한 뒤 v074의 예정 SELL을 1–4 step 앞당겨 같은 shared demand를 동시에 선점한다** — 확신도 **0.72** `[LOCAL][ENGINE][HYPOTHESIS]`.

# HYPGEN-0927 카드 결과

## 사람 요약

1. **무엇을 시험했는가:** EXP-028 직접대결에서 큰 D 승 6, 근소 D 승 3, D 패 3의 12경기를 1 worker로 다시 돌려 두 bot의 719개 action을 전부 기록했다.
2. **왜 하는가:** 55be5d5f(D)가 v074(P)를 0.88로 이기는 원인이 rival route인지, sale timing인지 분리해 반격 조건을 만들기 위해서다.
3. **측정 결과:** 12/12 reward·status가 원본과 exact 일치했고 agent error 0, 양쪽 action call 719/719였다. D는 v074를 `_V93_ROUTE_BY_RIVAL`로 식별하지 않았다. 반복 관측된 우위 경로는 MILK·STRAWBERRY·WOOL 등을 P보다 1–4 step 먼저 파는 sale-advance였다.
4. **막힘/다음:** sale-advance의 단독 인과효과는 EXP-030 ablation 전에는 확정할 수 없다. d157은 작은 screen만 통과했고 일반 guard가 없어 제출 근거가 아니다. 새 H1 card와 d157/EXP-030 full guard가 다음이다.

VERDICT | **LOCAL_SUPPORTED_MECHANISM / COUNTER_HYPOTHESIS_READY / NO_SUBMISSION** | trace SHA·검증 아래 | 12경기 exact replay PASS | NEXT: H1 preregistration

## A. 메커니즘

### A1. 선택·재현

| 구간 | seed/seat | EXP-028와 재실행 D margin | 결과 |
|---|---|---:|---|
| 큰 D 승 6 | 12311/0,1; 12328/1,0; 12310/0,1 | +1,535; +1,556; +4,353 (각 양 seat 동일) | 6/6 exact |
| 근소 D 승 3 | 12341/0,1; 12345/0 | +127; +127; +168 | 3/3 exact |
| D 패 3 | 12331/0,1; 12326/0 | −4,297; −4,297; −5 | 3/3 exact |

- `[LOCAL]` 12행의 reward/status/call/error: `experiments/hypgen_0927/replay-verification.json:1-205`. 이 파일 SHA-256은 최종 검증 절에 기록한다.
- `[LOCAL]` 실행기는 `experiments/hypgen_0927/trace_selected.py`; `multiprocessing` 없이 순차 실행하므로 worker=1이다. 새 게임은 정확히 12개이고 holdout 9000–9599를 쓰지 않았다.

### A2. 첫 분기와 rival 감지

| 관측 | 근거 | 판정 |
|---|---|---|
| 첫 action 분기 = **step 0**, 12/12 | D=`BUY_PRODUCT WHEAT 8 → SELL 3 → BUY_SEED 1`, P=`BUY_PRODUCT WHEAT 5 → BUY_SEED 1`: `trace-12328-seat0.jsonl:1`; D의 opening 값은 `releases/public-dpnew-55be5d5f-exact/main.py:7028-7042` | opening 주문은 다르다 `[LOCAL]` |
| step 2 공개 상태와 key | 양쪽 money=1042, WHEAT inventory=9989, D `rkey=[1042,9989]`: `trace-12328-seat0.jsonl:3` | step 0 차이는 step 2 public state를 가르지 않는다 `[LOCAL]` |
| `_V93_ROUTE_BY_RIVAL` | 유일 key `(229.0,9989)→128`; step 2에 rival money/WHEAT를 저장하고 YARN_STORE world에서 step 144 route를 바꿈: `main.py:960-975` | v074 key `(1042,9989)`는 map miss. **D는 v074를 식별하지 않는다** `[LOCAL][CODE]` |
| 실제 step 144 route | 예: ICE_CREAM×2에서 route 105, key는 계속 `[1042,9989]`: `trace-12328-seat0.jsonl:145` | direct 0.88의 원인을 V93 route 128로 돌릴 수 없음 `[LOCAL]` |
| 최초 공개 식별 가능 시점 | step 91까지 money 동률; P만 WHEAT3 SELL(`:92`), step 92 money가 D/P=237/327 또는 YARN world 236/323(`:93`, 12경기 모두) | D-family gate는 **step 92 이후**에만 가능. step 91 이전 exclusive counter는 구현 불가 `[LOCAL][INFERENCE]` |

### A3. shared demand 선점 trace

`[ENGINE]` market은 같은 order slot의 양쪽 unit을 같은 pre-commit inventory로 quote한 뒤 commit하고, 다음 unit/step에는 늘어난 inventory가 반영된다(`/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py:544-628`). 따라서 먼저 단독 SELL한 쪽이 뒤 판매자의 quote를 낮출 수 있다.

| seed | D 선행 SELL | 이후 P SELL | 공개 pre-step price 변화 | trace |
|---|---|---|---:|---|
| 12328, D +1,556 | step465 MILK3 | step466 MILK3 | 158 → 152 | `trace-12328-seat0.jsonl:466-467` |
| 12326, D −5 | step392 MILK6 | step394 MILK6 | 154 → 145 | `trace-12326-seat0.jsonl:393-395` |
| 12310, D +4,353 | step497 STRAWBERRY8(P는 4) | step498 P의 나머지 4 | 145 → 114 | `trace-12310-seat0.jsonl:498-499` |
| 12311, D +1,535 | step553 STRAWBERRY10(+WOOL16) | step557 P STRAWBERRY13 | 62 → 51 | `trace-12311-seat0.jsonl:554-558` |

- `[CODE]` **Step738 sale-advance**는 step 144–717에서 native tape의 다음 1–4 step SELL을 찾고(`main.py:7500-7529`), 현재 projected stock·price≥2·10-order cap으로 수량을 제한한 뒤 extra SELL을 앞에 붙인다(`:7531-7559`). 위 MILK/STRAWBERRY/WOOL 패턴과 정확히 같은 방향이다.
- `[INFERENCE]` 이것이 관측된 shared-demand 선점의 가장 직접적인 layer다. 그러나 D에는 Step739–1009도 이어지고(`main.py:7576-10137`), 이번 12경기는 ablation이 아니므로 **Step738 단독 인과**와 각 품목의 margin 기여량은 N/A다.
- `[LOCAL]` D가 진 12326에서도 같은 MILK 선점이 있었다. 따라서 “선행 SELL이 있으면 반드시 승리”는 반증됐다; 생산량·다른 sale/order 차이가 최종 승패를 함께 결정한다.

## B. 반격 가설 — 우선순위순

| 순위 | 메커니즘 / 발동 조건 | wrapper 구현·부모 | 예측 (D / 127 / 기타) | 반증 기준 | 비용 |
|---|---|---|---|---|---:|
| H1 | **post-92 gated own-sale lead**. step92에 `own_money-rival_money∈{87,90}`이고 직전 own action이 WHEAT3 SELL이면 55be-family flag; step144부터 own parent tape의 다음 1–4 step 고가 SELL을 현재 stock 한도로 앞당김 | parent 뒤 stateful wrapper, `action.market`만 변경; v074와 EXP-030 통과 후보 모두 | ↑ / = / = (gate false면 byte-for-byte action 동일) | D 12경기 activation<12/12, 127+guard 24경기 중 false activation>0, 또는 D 상대 paired score가 parent 이하 | 36 |
| H2 | **post-92 exact-D schedule match**. 같은 flag 후 shop pair로 공개 D route를 정하고, trace에서 D가 먼저 파는 MILK/STRAWBERRY/WOOL lot과 같은 step·slot에 보유분만 SELL | parent 뒤 `market` prepend/merge; 둘 다. H1보다 exact-D에는 강하지만 clone 변형에 취약 | ↑ / = / = | exact D 상대 changed action=0, gate false action SHA 불일치, 또는 D 변형 2종에서 parent보다 패배 증가 | 36 |
| H3 | **V93 detector spoof**. step0 opening을 127 signature 후보로 바꿔 D가 step2 `(229,9989)`를 읽게 하고, YARN_STORE world의 step144 route128을 역이용 | step0 `action.market` override; v074만 | ? / ↓ 가능 / ↓ 가능 | YARN D 경기에서 route128 activation<100% 또는 score≤v074; non-YARN/guard 열화 1건이면 폐기 | 24 |
| 기각 | step91 WHEAT3 SELL을 **D 상대에서만** 억제 | 불가: step91 observation까지 양쪽 public state가 동률이고 D action 결과는 step92에야 보임(`trace-12328-seat0.jsonl:92-93`) | N/A | 정보가 action 시점 전에 없음 | 0 |

H1의 `{87,90}`은 이번 7 unique seed/12게임에서만 확인된 값이다. 새 card에서는 detector를 먼저 별도 false-positive gate로 고정해야 하며, 결과를 보고 범위를 넓히면 안 된다.

## C. 두 슬롯 E[max] 대리지표

정의: scenario `f`별 두 후보 중 큰 로컬 score를 택해 `Σ weight_f × max(score_A,f, score_B,f)`로 계산했다. 입력은 EXP-028의 v074/D `{127:.870/.885, 55be:.120/.500, 기타:.970/.820}`(`summary.json:3-18,676-754`)와 EXP-029 screen d157 `{127:1.0, 55be:0.8, 기타:N/A}`(`screen-summary.json:13-22`). d157은 각 상대 **5 seed×2 seat=10게임**뿐이다(`prep29.py:24-38`). d157의 기타 값은 빼고 이미 측정된 partner 값을 썼으므로 d157 pair 수치는 **lower bound**다. 이 값은 BT, 미래 mixture, 두 slot 간 correlation을 모델링하지 않는 선택용 surrogate다.

| scenario (127/55be/기타) | v074+D | v074+d157 | D+d157 | v074+동일 bytes 재제출 |
|---|---:|---:|---:|---:|
| legacy 60/10/30 | .872 | **≥.971** | ≥.926 | .825 |
| transition 40/30/30 | .795 | **≥.931** | ≥.886 | .675 |
| clone-heavy 20/60/20 | .671 | **≥.874** | ≥.844 | .440 |
| diverse 25/25/50 | .831 | **≥.935** | ≥.860 | .733 |

- `[INFERENCE]` surrogate 4/4에서 **v074+d157**이 1위다. v074가 기타(.97)를, d157 screen이 127(1.0)·55be(.8)를 맡는 구조다.
- `[LIMIT]` d157의 일반 guard는 N/A이고 screen은 selection-biased 10게임이다. 따라서 이것은 **full guard 우선순위**이지 제출 승인 아니다. EXP-030 screen/final 결과는 보고 시점 N/A이므로 EXP-030 pair의 E[max]도 N/A다.
- **권고:** 현재는 v074를 보존한다. d157이 EXP-028 guard+hosted-replay 재현 gate를 통과하면 두 번째 slot 후보 1순위; 아니면 frozen gate를 통과한 EXP-030 후보만 대체안이다. 둘 다 없으면 현 slots 유지.
- **제출 순서(조건부):** generalist v074를 먼저/기존 상태로 두고 specialist를 나중에 둔다. 다만 `BOARD.md`의 활성 ID는 09-25 상태인데 최근 보고는 v171 `56567563`/v074 `56577440`을 기록한다(`coordination/reports/antigravity/20260926-2045-EXP025-V171-HOSTED.md:5-6,53-54`). FIFO/재제출 필요 여부는 HOSTED_LEDGER 동기화 전 `BLOCKED`; 실제 제출은 사람 승인 사항이다.

## 검증·provenance

- 실행: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 experiments/hypgen_0927/trace_selected.py` — 12/12 exact, status DONE/DONE, error 0.
- source SHA-256: D `55be5d5f124c8daaaa63c1a29ba4aab096004909666f04748007603c67b7d2a8`; P `860a502c36f9a9f700c93125e6828f41378f50d74fa130f62a09f911316ea19c`; EXP-028 raw `b44231c495959b8a449451360a102de7d6c0ce19ac350dd6a5da90e477483856`.
- trace runner SHA `deb528ad5ec89d12421494a6683b8e912a20cafb2973403250210c1ee76f3de7`; replay verification SHA `7af2225d2b69cb4ae8c6cdef7b4e8424a38957a9c56b7b2962ec0358218bde39`.
- 가설 원장 update는 카드의 “기존 파일 수정 금지/보고서 1개” 범위 때문에 하지 않았다. H1–H3는 아직 HYP-####/TEST-####가 아닌 설계 후보이며 실행 승인도 아니다.

## 다음 행동 2개

1. H1 detector false-positive와 action-identity gate를 먼저 고정한 36게임 one-factor card를 Claude가 작성하고, 새 non-holdout seed로 실행한다.
2. d157 또는 EXP-030 최종 후보에 EXP-028 일반 guard·hosted-replay·runtime/identity gate를 적용한 뒤에만 slot 후보로 판정한다.

## 사람이 결정할 질문 2개

1. H1의 36게임 preregistration을 새 실험으로 승인할 것인가?
2. 최신 활성 submission/FIFO를 HOSTED_LEDGER에 먼저 동기화한 뒤, full guard를 통과한 specialist 한 개에만 다음 제출 기회를 배정할 것인가?


---

## `reports/codex/20260927-1639-H1.md`

FAIL

# H1-0927 1차 검증

1. **무엇을 시험했는가:** v074 exact bytes 뒤에 step-92 detector와 MILK/STRAWBERRY/WOOL 1–4 step sale lead wrapper를 붙였다.
2. **왜 하는가:** D(55be5d5f)의 shared-demand 선점을 되받되, 다른 opponent에서는 parent action을 그대로 보존할 수 있는지 확인했다.
3. **측정 결과:** 36 candidate 게임과 같은 seed/seat의 parent 36게임은 모두 DONE/DONE, action call 719, agent error 0이었다. 그러나 FP panel에서 12회 activation했고 D 상대 paired score delta는 0이었다.
4. **막힘/다음:** 고정 FP gate와 effect gate가 모두 실패했다. detector·기준은 바꾸지 않았고 이 H1은 여기서 STOP한다.

VERDICT | **LOCAL_FAILED / NO_SUBMISSION** | FP activation 12/24, identity 12/24; D activation 12/12, paired score delta 0.0000 | NEXT: H1 STOP

| panel | 게임/arm | activation H1 | act_sha 동일 | score H1 | score P |
|---|---:|---:|---:|---:|---:|
| O127 | 12 | 0 | 12 | 0.7500 | 0.7500 |
| PUB01 | 6 | 6 | 0 | 1.0000 | 1.0000 |
| PUB12 | 6 | 6 | 0 | 1.0000 | 0.6667 |
| FP 합계 | 24 | **12** | **12** | — | — |
| D | 12 | **12** | 0 | **0.1667** | **0.1667** |

- Frozen gates: FP `activation=0 && act_sha 동일=24/24`; effect `activation=12/12 && mean paired score delta>0`. 결과는 각각 FAIL, FAIL이다.
- Runtime: H1 max step **0.314409s**; parent max step **0.323324s**. 72/72 valid, 72 unique keys, worker=1.
- 구현 진단: FP는 PUB01/PUB12에서 각 6/6 발동했다. H1은 D에서 501 units를 앞당겼지만 original-step credit는 132 units, shortfall 369 units였다. native tape가 예고한 sale과 실제 parent action이 달라 unit-credit 계약도 완결되지 않았다.
- Variant: `experiments/h1_0927/h1.py` SHA-256 `cbd64bb48a1dc1da7a3c9559c82478bbfe6c37fd9812984d1fb5a6249b759936`.
- Parent: `releases/round2-v074/main.py` SHA-256 `860a502c36f9a9f700c93125e6828f41378f50d74fa130f62a09f911316ea19c`; variant 앞 494,522 bytes exact 일치.
- Frozen prereg: `experiments/h1_0927/prereg.json` SHA-256 `a8f025865e1db0cf0110ac5026952ea750e0fea0b0adb34b0609d3c0ecbd9774`.
- Raw: `experiments/h1_0927/games.jsonl` SHA-256 `fd07cce442afc85a16b65948055c9fc1f4ac5ef16ef33f18c8b853cbcb41c907`.
- Summary: `experiments/h1_0927/summary.json` SHA-256 `632d6edb4431b9dcac2ca4247ecd83e597d60392670ee6137e2e2b8301f50499`.
- 금지사항 준수: seed 14400–14405만 사용; holdout 9000–9599·다운로드·제출 없음; 기존 파일 수정 없음; detector/기준 변경 없음.

검증:
```bash
python3 -m py_compile experiments/h1_0927/{h1,prep,run,judge}.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 experiments/h1_0927/run.py
python3 experiments/h1_0927/judge.py
python3 tools/validate_hypotheses.py --strict
```
결과: compile PASS; 72/72 valid; frozen judge FAIL; hypothesis ledger 37 entries PASS.

## 다음 행동 2개

1. 이 H1 variant를 대규모 검증이나 release로 넘기지 않는다.
2. 후속을 원하면 PUB01/PUB12와 D를 구분하는 새 detector 및 실제 parent sale만 advance하는 방식을 **새 ID·새 preregistration**으로 먼저 동결한다.


---

## `reports/codex/20260927-1730-INSIGHT-SWEEP.md`

# INSIGHT-SWEEP 카드 (Codex) — 2026-09-27 17:30 KST

실행 가능 가설 0개; 최우선은 `N/A` (새 wrapper factor로 분리 가능한 측정 근거를 찾지 못함).

| id | 주장 1줄 | 출처(파일·cell/줄) | 근거 유형 | v074 에 있음? | 55be5d5f 에 있음? | wrapper 로 구현 가능?(hook) | 127 계열 W/D/L 영향 경로 | 시험 비용 |
|---|---|---|---|---|---|---|---|---|
| IS-01 | day-6 shop pair별 route 표와 목록 밖 pair→plan 0 fallback 주장 | `coordination/proposals/claude/20260927-INSIGHT-SWEEP-CODEX.md:12`; 원문 `docs/collection_snapshots/kaggricult-man-reverse-engineering__20260927/kaggricult-man-reverse-engineering.ipynb` cell 위치는 one-line JSON이라 `UNSURE` | 주장 | 있음: `_R108_SHOP_ROUTES` 947, `.get(shops,100)` 969, `_V92_TABLE` 956/970 | 있음: `_V93_ROUTE_BY_RIVAL` 960, route 선택 974–975 | 기존 route selector와 중복; 새 hook 없음 | shop pair가 다른 route를 고르면 opening·생산·매도 tape 전체가 바뀜 | 0 (중복)
| IS-02 | T4 adaptive sale lead-1/lead-2와 unit credit 주장 | `coordination/proposals/claude/20260927-INSIGHT-SWEEP-CODEX.md:12`; kaggricult-man notebook cell `UNSURE` | 주장 | 있음: `_sell_lead` 629, `_front_run` 660, lead 교체 1653–1670 | 있음: `_sell_lead` 631, `_front_run` 662, `_v9_race_update` 3815, `_v9_racepx_lead` 3918–3952 | 중복; `market` SELL quantity/order만 건드리는 기존 layer가 이미 담당 | rival보다 먼저 같은 lot을 팔아 shared demand/price를 바꾸는 mirror race | 0 (중복)
| IS-03 | 64 shop world coverage 주장 | `coordination/proposals/claude/20260927-INSIGHT-SWEEP-CODEX.md:12`; kaggricult-man notebook cell `UNSURE` | 주장 | `UNSURE`: map cardinality를 grep 근거로 확정하지 못함 | `UNSURE`: same | 가능한 selector data 확장은 parent bytes 뒤 wrapper 범위를 넘고, 측정 근거도 없음 | route mismatch가 초반 행동 tape를 갈라 mirror/near-clone 승부에 닿을 수 있음 | N/A (새 card 전 source/coverage 검증 필요)
| IS-04 | 매일 farmer가 shed로 돌아가고 hands/HIRE cost가 reset된다는 주장 | `docs/discussion/741907_The_farmer_gets_teleported_back_to_the_shed_every_day__and_it_explains_most_results.md:8-12` | 일화+문서 인용 주장 | `UNSURE`: route tape가 이 규칙을 전제할 수 있으나 explicit grep 근거 없음 | `UNSURE`: 동일 | 가능: day boundary에서 `farmer`/`hands`를 수정하는 guard. 단 engine 검증 전 구현 금지 | 이동·재고 회수·다음날 HIRE 시점이 달라져 생산량과 sale timing에 간접 영향 | N/A (먼저 ENGINE fact 검증)
| IS-05 | 마지막 7 step의 physical delivery/terminal sale은 baseline 우세일 때만 바꾼다는 closure 방식 | v074 source 1017 (E182 planner); 55 source 1017 및 terminal entry 10122–10136 | 구현 근거 | 있음: `_terminal_liquidation` 898–908 및 planner 1017 | 있음: `_terminal_liquidation` 900 및 Step1009 10122–10136 | 이미 구현됨: step 712–718 `farmer`/`hands`/`market` | terminal cargo를 shed에 넣고 SELL 하되 baseline delivery를 보존 | 0 (중복)

## 실행 불가하지만 알아야 할 사실

1. `kaggricult-man`의 vote/점수는 채택 근거가 아니다. 이 카드가 명시한 제출물은 no-op이며, 남은 것은 위의 mechanism claim뿐이다 (`coordination/proposals/claude/20260927-INSIGHT-SWEEP-CODEX.md:12`).
2. daily reset은 discussion 작성자의 one-variable 실험 서술과 README 인용이다. 이 sweep에서는 engine source로 재검증하지 않았으므로 `[COMMUNITY]`/`UNSURE`를 넘지 않는다 (`docs/discussion/741907_The_farmer_gets_teleported_back_to_the_shed_every_day__and_it_explains_most_results.md:8-12`).
3. v074에는 shop-pair selector, fallback, lead-sale/front-run, terminal layer가 이미 있고, 55be5d5f는 rival-key route와 Step1009 sale-timing까지 추가한다. 따라서 공개 claim을 같은 형태로 다시 넣으면 one-factor experiment가 아니다.
4. shop world coverage를 넓히는 것은 route data/selector 정책을 바꾸는 일이다. 현재 card의 wrapper-only 판단 기준과 맞지 않으며, coverage 수 자체도 원문 cell을 독립 계수하지 못해 `UNSURE`다.

재현한 read-only 확인: `grep -n -E '_R108_SHOP_ROUTES|_V92_TABLE|_sell_lead|_front_run|_terminal_liquidation' releases/round2-v074/main.py`; `grep -n -E '_V93_ROUTE_BY_RIVAL|step1009|_v9_racepx_lead|_v9_race_update' releases/public-dpnew-55be5d5f-exact/main.py`; `grep -n -E 'daily reset|teleports|re-hired|HIRE cost|one variable' docs/discussion/741907_The_farmer_gets_teleported_back_to_the_shed_every_day__and_it_explains_most_results.md`.

다음 행동 1: 새 실험 카드를 만들기 전에 daily-reset 주장을 pinned engine source로 확인하고, 사실이면 HYPOTHESES 원장과 postmortem에 독립적으로 연결한다.

다음 행동 2: `kaggricult-man`의 64-world 수와 T4 claim은 raw markdown cell을 분리해 source span·측정 artifact가 있는 경우에만 새 wrapper factor 후보로 재등록한다.


---

## `reports/codex/20260927-1956-REVIEW-0927C.md`

부적절 — 오늘 밤 A 슬롯은 교체하지 말고 유지한다; d157은 frozen EXP-032 FAILURE, b020은 방금 완결된 frozen final 재집계 FAILURE라 제출 후보가 아니다.

# REVIEW-0927C 판단 카드 — 2026-09-27 19:56 KST

1. **무엇을 검토했는가:** d157/b020/55be 계열의 A 슬롯 교체안, runtime 허용선, v074 유지 가치, 127 변형 대응 경로.
2. **왜 하는가:** 마감 직전 한 슬롯을 selection bias·runtime·동계열 상관 때문에 잃는 결정을 막기 위해서다.
3. **측정 결과:** 새 게임 2경기(1 worker, seed 14100, holdout 아님)로 d157 profile만 했고, 나머지는 기존 350 hosted replay·EXP-030/032 원자료를 재집계했다. b020 final은 1,680/1,680행 완결됐지만 FAIL이다.
4. **막힘/다음:** EXP-034 결과와 EXP-033 완결 산출물이 아직 없다. 2400+ rating 변화량은 submission별 상대 rating이 없어 `UNSURE`; 오늘 밤은 제출이 아니라 증거 완결과 새 card 여부 판단만 가능하다.

`VERDICT | NO_SUBMISSION / A 유지 | d157 EXP-032 FAIL, b020 final FAIL | experiments/review_0927c/analysis.json + profile_d157.json | 재집계·2-game profile PASS | NEXT: EXP-034/033 판독 후 새 card 여부만 결정`

## Q1. 계획 타당성 — 부적절 (확신도 0.97)

**결론.** “EXP-034 안전이면 d157을 A로 제출, 아니면 b020/55be 최적화” 순서는 쓰면 안 된다. 순서는 `EXP-034/033 증거 수집 → 기존 frozen verdict 유지 → 필요하면 새 artifact·새 card 사전등록 → B 슬롯만 검토`다. 오늘 밤 A는 유지한다.

**근거.**

- d157은 frozen gate가 `max_step<0.8`을 요구하고(`experiments/exp032_specialist/judge32.py:1-8,41-47`), 실제 verdict는 FAIL/selected null이며 max 1.6258초다(`experiments/exp032_specialist/judge.txt:1-3`). 원자료 재집계는 d157 880경기 중 max>0.8이 279, max>1.0이 198이다. 명령: `python3 -c "import json; r=[json.loads(x) for x in open('experiments/exp032_specialist/games.jsonl') if json.loads(x)['vid']=='d157']; print(len(r),sum(x['max_step']>.8 for x in r),sum(x['max_step']>1 for x in r),max(x['max_step'] for x in r))"`.
- EXP-034 단일-kernel 결과가 좋아도 EXP-032의 사전 verdict를 소급 변경하지 못한다. 정책은 FAILURE 제출 금지(`coordination/proposals/claude/20260923-CANDIDATE-POLICY.md:16-18,24-32`)이고, 09-27 00:00 KST 이후 A를 건드리지 않고 B만 실험하도록 한다(`...CANDIDATE-POLICY.md:37-40`). 사람의 명시적 정책 override 없이는 A 교체 자체가 범위 밖이다.
- d157은 158개 one-factor screen 중 최고값으로 골랐고, 최초 비교는 상대당 10게임뿐이다(`experiments/exp029_dpnew_mirror/judge29.py:1-3,20-27`; `screen-summary.json:1-22`). d157의 factor는 `_S1002_PASSES 34→35` 하나다(`experiments/exp029_dpnew_mirror/variants.json:1573-1580`). EXP-032가 fresh broad panel을 보강했지만 runtime failure와 selection history는 사라지지 않는다.
- EXP-033의 “17–18 episode open-loop” 수치는 요청서에만 있고 완결 summary/games artifact가 없다(`coordination/proposals/claude/20260927-REVIEW-0927C-CODEX.md:10-13`). 따라서 127 변형 일반화는 현재 `UNSURE`; open-loop는 상대 tape를 고정해 candidate가 유발할 반응을 제거하므로 closed-loop 대체도 아니다.
- b020은 final 1,680행 완결 재집계에서 invalid 0이지만 max 41.761초, hosted-v074 Δ=-0.0833/lower=-0.1583, frozen pass=false다(`experiments/review_0927c/analysis.json:245-269`). frozen 기준은 max<0.8, hosted point≥0/lower>-0.03이다(`experiments/exp030_dpnew_bypass/judge30.py:1-6,33-45`). b020 fallback도 종료다.
- 55be exact는 EXP-028에서 hosted-replay P 대비 -0.0744, 추천 HOLD였다(`experiments/exp028_dpnew/summary.json:3-18`). “속도만 개선하면 fallback”이 아니라 성능까지 다시 통과해야 하는 새 실험이다.

## Q2. runtime 경계선 — 감수하지 않는다 (확신도 0.94)

**결론.** 게임당 1초 초과가 수십 번이고 초과 합계가 10–30초이면 engine상 즉시 TIMEOUT은 아니지만, 현재 승인 gate를 명백히 실패하므로 제출하지 않는다. 새 card에서 사람 승인으로 기준을 바꾸지 않는 한 예외가 없다.

**정량식과 기준.**

- agent TIMEOUT 조건은 `Σ max(0,t_i−1s)>60s`; framework는 매 step 초과분을 차감한다(`.venv/.../agent.py:207-223`, `.venv/.../core.py:628-637`, `kaggriculture.json:8-9,128`). episode hard stop은 두 agent·engine 합 wall time `>1200s`다(`schemas.json:71-75`, `core.py:324-332`). 719 call이므로 engine-only nominal 상한은 agent당 779초, 두 agent 1,558초다(`evidence/FACTS.md:23-29`). hosted scheduling은 N/A다.
- 운영 gate는 더 강하다: single worker max<0.8, 6-worker max<1.0, agent total<30초, exception 0(`coordination/HANDOFF-20260925-CLAUDE.md:22-25`). 따라서 “수십 번 >1초”는 합계가 10초여도 max<1.0을 이미 실패한다.
- 이번 1-worker cProfile 2게임 중 보존된 두 번째 결과는 719 call, max 0.233초, agent total 3.479초, overage 0, DONE/DONE이다(`experiments/review_0927c/profile_d157.json:1-19`). 명령: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 experiments/review_0927c/profile_d157.py`. 단일 seed·Mac 부하 변동이므로 EXP-034를 대체하지 않는다.
- 가장 큰 self-time은 `_v44y_factor_margin.margin` 199,730회/0.623초이고 `_s793_reorder`는 7,335회/0.215초였다(`profile_d157.json:20`; 구현 `d157.py:6089-6119,7895-7937`). 반복 fixed-sell closure가 같은 combinatorial scorer를 여러 번 부르는 구조다(`d157.py:9941-9972`).
- 결과 보존형 최적화 후보는 **한 step 안에서** `(market inventory, projected stock, params, opponent orders, candidate schedule)`별 margin을 closure pass 사이 공유하는 cache다. 새 candidate에서 기존 EXP-032 2,540행과 EXP-030/hosted tape 전부 action SHA·W/D/L exact equality, telemetry equality, single-worker worst seeds max<0.8/total<30을 모두 확인해야 한다. 하나라도 다르면 “속도 개선”이 아니라 정책 변경으로 판정한다.

## Q3. v074 유지 가치 — 유지 (확신도 0.91)

**결론.** 09-28에 두 번째 슬롯까지 55be 계열로 바꾸는 판단 근거는 없다. 현재는 v074를 남기고, 서로 다른 계열의 한 candidate가 전체-field bot score로 v074를 넘을 때만 B 교체를 검토한다.

**근거와 계산.**

- v074 163경기 재집계: 127 variant 8/1/43, score `(8+0.5)/52=0.1635`; 127 exact 34/3/3, `35.5/40=0.8875`; 55be 9/0/8=`0.5294`; UNKNOWN 20/0/20=`0.50`(`analysis.json:277-312`). 2200–2400만 고정하면 127 variant는 3/0/24=`0.1111`, UNKNOWN은 5/0/12=`0.2941`(`analysis.json:201-242`). 요청서의 “0.185/0.30” 중 후자는 반올림 일치하지만 전자는 이 분류로 재현되지 않아 `UNSURE`다.
- E[max]는 category별 max의 합이 아니라 먼저 bot 전체를 합산한다. EXP-032 panel의 `(127,55,other)` 점수를 P=`(.88,.04,.98913)`, d157=`(.86,.85,.84565)`로 두면 `S_b=Σw_f s_bf`, `E[max]=max(S_P,S_d157)` surrogate는 legacy .8547, transition .8527, clone .8511, diverse .8503이다(`analysis.json:314-334`). 이는 d157 한 bot이 네 scenario에서 선택된 결과이지, category별 cherry-pick이 아니다.
- 그러나 위 panel의 127은 exact O127이지 hosted 127 variants가 아니고, d157은 frozen FAIL이다. 실제 field 전체 score·BT 분포·joint uncertainty가 없어 “두 55be로 바꾸면 E[max] 상승”은 `UNSURE`다.
- 같은 계열 d157/d053은 같은 880경기에서 outcome 799/880=90.80% 동일, score Pearson r=0.8443이다(`analysis.json:271-275`; 재집계 `python3 experiments/review_0927c/analyze.py`). 두 55be 슬롯은 failure correlation이 높아 `max(A,B)`의 diversification 가치가 작다. v074의 127 exact 0.8875는 남겨둘 실증적 보완축이다.

## Q4. 127 변형 및 2400+ 경로 (확신도 0.82; rating 범위는 모두 UNSURE)

127 variant는 prefix 구간 어디서나 약하다: `<100 .231`, `100–199 0`, `200–399 .20`, `400–719 .136`(`analysis.json:171-199`). 패배 43경기의 median cash gap은 step576 -34에서 step648 -177, step712/719 -226으로 벌어진다(`analysis.json:55-105`). 이는 late-game 집중을 지지하지만 품목별 causal attribution은 없다. 요청 SELL 합은 미체결/부분체결을 포함하므로 메커니즘 근거로 쓰지 않는다.

| 우선 | 경로 | 부모·wrapper / mechanism | 검증(open-loop + closed-loop) | 시간 | 성공/실패·rating |
|---:|---|---|---|---:|---|
| 1 | d157 semantics-preserving runtime compaction | d157 exact SHA `94a46c…`; 위 per-step scorer cache만 추가. 강점은 EXP-032 55=.85, O127=.86이나 variant 일반화는 UNSURE | EXP-033 전체 tape에서 action/WDL 비교 + closed-loop O127/23 guard/hosted panel; action identity가 바뀌면 별도 정책 card | 2–4h | 새 runtime gate와 기존 성능 gate 모두 통과해야 성공. rating 변화 **UNSURE** |
| 2 | late-game fixed-sell closure one-factor | v074 parent + step648 이후에만 one extra convergence pass; 패배 cash gap이 day27부터 벌어지고 d157 factor가 34→35 pass라는 관측 | 52 hosted 127-variant tapes 전수 open-loop + prefix 4 strata 대표 closed-loop 양 seat; exact/UNKNOWN non-inferiority 필수 | 3–6h | variant paired lower>0, exact/UNKNOWN 하락≤0.03, runtime PASS; 아니면 폐기. rating **UNSURE** |
| 3 | prefix-stratified reactive router | v074 parent; 0–99/100–199/200–399/400+의 **관측 후** signature만 사용해 late route 선택. action 전에 알 수 없는 분기는 사용 금지 | 각 stratum tape calibration/holdout 분리 + representative closed-loop; false-positive action identity gate | 6–10h | 모든 stratum pooled lower>0 및 other non-inferiority. 남은 시간상 오늘 밤 제출 경로 아님; rating **UNSURE** |

**2400+ 판정.** 현재 제시 rating 약 2212/2216과 2400의 차이는 약 +184~188이지만, 상대 submission rating을 얻을 수 없어 local score→BT 변환이 없다(`evidence/HOSTED_LEDGER.md:374-376`). 위 경로 어느 것도 +184 이상을 뒷받침하지 못하므로 2400+는 **근거상 비현실적/UNSURE**이며 목표로 약속하면 안 된다. 우선 목표는 검증된 A 보존과 단일 B upside다.

## Q5. 놓친 것 (확신도 0.96)

1. **governance hard stop:** d157/b020은 둘 다 frozen FAILURE다. EXP-034가 좋다는 이유로 과거 verdict를 SUCCESS로 바꾸거나 제출할 수 없다(`CANDIDATE-POLICY.md:16-18,31`).
2. **정본 불일치:** BOARD/HOSTED_LEDGER는 09-25 상태인데 요청서는 v171/v074 활성·약 2212/2216을 말한다. ID는 최근 보고로 확인되지만 rating/FIFO는 요청서 외 독립 원장이 없어 `UNSURE`; 제출 전 동기화가 선행돼야 한다(`BOARD.md:1-18`; `HOSTED_LEDGER.md:378-379`; `20260927-REVIEW-0927C-CODEX.md:7`).
3. **metric-to-rating gap:** team LB를 상대 submission rating으로 썼다가 이미 추정이 폐기된 전례가 있다(`HOSTED_LEDGER.md:374-376`). 지금도 expected rating “범위”를 숫자로 만드는 것은 같은 오류를 반복한다.

## 오늘 밤 실행할 행동 2개

1. `python3 experiments/review_0927c/analyze.py` — EXP-030 final 1,680행, EXP-032 correlation, EXP-031 census를 다시 읽어 이 review 전용 `analysis.json`만 갱신한다.
2. `test -f experiments/exp034_runtime/rt.jsonl && python3 -c "import json; r=[json.loads(x) for x in open('experiments/exp034_runtime/rt.jsonl')]; print([(v,max(x['max'] for x in r if x['vid']==v),max(x['overage'] for x in r if x['vid']==v),max(x['total'] for x in r if x['vid']==v)) for v in sorted({x['vid'] for x in r})])"` — EXP-034 owner가 결과를 저장한 뒤 추가 게임·다운로드 없이 max/overage/total을 판독한다.

## 사람이 결정할 질문 2개

1. frozen FAILURE인 d157/b020은 제출 후보에서 닫고, d157 cache를 **새 artifact·새 card**로 검증할 기회만 줄 것인가?
2. 09-27 이후 A 고정 정책을 유지하고, 동기화된 활성/FIFO 확인 뒤 새 SUCCESS candidate가 생길 때만 B 슬롯 한 번을 사용할 것인가?


---

## `reports/codex/20260927-2126-LATE.md`

FAIL | 원인은 자기 cash 부족이 아니라 late SELL 순서가 만드는 상대 market suppression | 3후보 모두 frozen open-loop gate FAIL | closed-loop 미실행·jobs만 고정 | NEXT: 이 경로 종료, 다른 원인으로 이동

# LATE-0928 1차 보고 — 2026-09-27 21:26 KST

1. **무엇을 시험했는가:** v074의 step 576 이후 판매·청산만 바꾸는 후보 3개를 원인 표 뒤에 사전등록하고 screen했다.
2. **왜 하는가:** 127 변형 상대 패배 43경기에서 step 576 이후 벌어진 cash gap의 원인을 좁히고, 결과를 보기 전에 정한 gate로만 판정하기 위해서다.
3. **측정 결과:** 원인 14 pair(28게임) + schema preflight 1 + corrected trace 1 = 추가 30게임. screen 615게임, 1-worker runtime 15게임. 전부 DONE/DONE·719 actions·error 0. 후보 3개 모두 FAIL.
4. **막힘/다음:** 통과 후보가 없으므로 closed-loop 1,520게임은 실행하지 않는다. Kaggle jobs 파일만 고정했다. release·submission·download·holdout 접근은 없다.

`VERDICT | LOCAL_FAILED / selected=null | prereg a85bbd90…9a68 | games-open 456b0013…065 / runtime a099aab0…909 | VERIFY PASS | NEXT: late-wrapper 경로 종료`

## 원인 표 `[LOCAL][ENGINE]`

고정 표본: v074가 127_near에 진 43 tape를 endTime 순으로 놓고 균등 간격 14개 선택. manifest `experiments/late_0928/cause_manifest.json` sha256 `cc9b780c…61224`.

| 측정 | v074 | d157 | d157−v074 |
|---|---:|---:|---:|
| score / 14 | 0.0000 | 0.7857 | +0.7857 (11 loss flips) |
| 자기 final cash 평균 | — | — | **−46.9** |
| 상대 final cash 평균 | — | — | **−1,041.6** |
| margin 평균 | — | — | **+994.8** |
| 자기 cash delta step576 / 648 / 696 / 719 | — | — | −28.6 / −80.1 / −9.0 / −46.9 |

판정: “v074가 자기 물건을 덜 팔아 cash를 잃는다”는 해석은 반박됐다. d157의 35번째 fixed-sell closure는 자기 cash를 늘리지 않으면서 late SELL 순서·시점을 바꾸고, 공유 market에서 tape 상대 cash를 더 크게 낮췄다. 확신도 0.88.

exact fill 예시 T114044162(step 576–718): v074/d157 SELL은 644/646 units, revenue 36,774/36,676, 자기 final cash delta −143, 상대 delta −598, margin delta +455. WOOL은 양쪽 96 units로 같지만 step 673(+5), 690(+7) 등 판매 시점이 이동했다. 품목별 표와 검증은 `experiments/late_0928/cause_table.json` sha256 `e51afef8…6246`; v074 replay는 모든 step의 post-market money exact 일치.

한계: item-level actual commit 비교는 위 1 pair이고, 14 pair 전체는 final cash/margin 및 checkpoint shed 비교다. tape는 상대 action을 고정하므로 closed-loop causal proof가 아니다.

## 후보 사전등록 `[HYPOTHESIS]`

parent `releases/round2-v074/main.py` sha256 `860a502c…19c`. 세 파일 모두 parent bytes 뒤 wrapper이며 saved replay의 step 0–575 action byte mismatch 0/576(`preflight_identity.json` sha256 `6a55ad01…fff4`).

| 후보 | SHA-256 | 단일 변경 | 반증 기준 |
|---|---|---|---|
| l576_closure1 | `bf67f5d9…7424` | step≥576 extra `_s793_reorder` 1회 | frozen gate 하나라도 FAIL |
| l648_closure1 | `3376ef5b…4621` | step≥648 extra `_s793_reorder` 1회 | 동 |
| l576_wool_first | `25c4e374…6b86` | step≥576 기존 WOOL SELL을 다른 SELL보다 앞에 배치; 수량·non-SELL slot 불변 | 동 |

사전등록 `experiments/late_0928/prereg.json` sha256 `a85bbd90…9a68`, HYP-0038 / TEST-LATE-0928-SCREEN. 결과 뒤 candidate·seed·threshold 수정 없음.

고정 gate: 127_near paired lower95>0; other point≥−0.02; closed-loop 127/guard 각각 point≥−0.03; 1-worker max<0.8s; invalid=0; action effect>0. bootstrap 10,000회 seed 928001.

## Screen 결과 `[LOCAL]`

| 후보 | effect games /205 | 127 point | 127 lower95 | other point | 1-worker max | 판정 |
|---|---:|---:|---:|---:|---:|---|
| l576_closure1 | 1 | 0.0000 | 0.0000 | 0.0000 | 0.0592s | **FAIL** (`>0` 불충족) |
| l648_closure1 | 2 | 0.0000 | 0.0000 | 0.0000 | 0.0580s | **FAIL** (`>0` 불충족) |
| l576_wool_first | 180 | −0.09375 | −0.15179 | −0.06452 | 0.0604s | **FAIL** (127·other) |

원자료: `games-open.jsonl` 615 unique, sha256 `456b0013…065`; `games-runtime.jsonl` 15 unique, sha256 `a099aab0…909`; invalid 0. 판정 `screen_summary.json` sha256 `12476ae3…38a1`.

closed-loop은 open gate 전부 FAIL이므로 실행하지 않았다. 준비된 jobs: `experiments/late_0928/jobs-closed-kaggle.json`, 1,520게임, sha256 `86d10578…47fa`; O127 50 seed×2, guard 23×5×2, 55be 25×2, parent+3 candidates. holdout 9000–9599 seed 0개.

## 다음 행동 2개

1. **이 late-wrapper 가설을 LOCAL_FAILED로 닫는다.** lower95가 0인 closure 후보에 pass 수·seed를 더하거나 threshold를 완화하지 않는다.
2. **남은 시간은 다른 원인으로 이동한다.** closed-loop jobs는 실행하지 말고, 기존 frozen SUCCESS 후보와 서로 다른 계열의 증거를 우선한다. 제출 판단은 Coordinator/사람에게 남긴다.


---

## `reports/codex/20260927-2311-ALTMECH.md`

1순위 후보: 없음 | 확신도: 기존 기능 중복 판정 높음, 가능한 모든 새 전략의 부재는 판단하지 않음 | DONE_DESIGN_NO_CANDIDATE

# ALTMECH-0928 — 2026-09-27 KST

1. 무엇을 검토했는가: d157과 다른 두 번째 슬롯 후보를 위해 관측 범위, 부모의 기존 기능, EXP-036 screen50의 저장 결과를 확인했다.
2. 왜 하는가: 이미 있는 front-run·분기·생산 예측을 다시 구현해 EXP-036 자원을 소비하지 않기 위해서다.
3. 결과: 채택 후보 0. 기존 50 pair/100행을 재집계했고 새 게임 0, policy 호출 0. 중복을 피하면서 개선 근거까지 갖춘 변경은 확보하지 못했다.
4. 다음: ALTMECH jobs는 실행하지 않는다. EXP-036을 우선하고, 새 후보에는 기존 기능과 다른 action 및 회복 가능한 손실의 근거가 먼저 필요하다.

`VERDICT | NO_SUPPORTED_CANDIDATE | 기존 기능은 R37보다 넓음 / 새 성능 측정 없음 | audit.json 53795ed6…916e | audit·ledger validation PASS | NEXT: 아래 두 행동`

## 관측 가능성 `[ENGINE]`

이하 E=`.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`, J=동일 경로 `kaggriculture.json`.

| 대상 | runtime observation에서 보이는가 | 코드 근거·주의 |
|---|---|---|
| 상대 money, farmer/hands 위치, unlocked_quadrants, hires_today | 예 | E:142–154, 261–273; J:92–102 |
| 상대 작물·동물·planted_day/placed_day·yield_units·급수/급여 상태 | 예, public tiles의 dict | E:214–240, 261–273, 769–832 |
| 상대 shed·seeds·운반 inventory | 아니오 | E:169–175, 255, 267–269; J:98–102의 shared=false |
| 상대의 이번 턴 주문 또는 당일 주문 이력 | 아니오 | J:86–129 observation에 action 없음; E:555–560은 interpreter의 state.action을 읽음 |
| market inventory·price, unlocked shops | 예, 공유 값 | E:261–273, 951–956; J:104–114 |
| 미래 생산일 | 조건부 예측 가능 | E:789–800, 821–830. 향후 급수/급여·care·harvest 행동과 운반·매도 시점은 확정 불가 |

`yield_units>0`을 곧바로 익은 작물로 읽으면 안 된다. E:223에서 일회성 작물은 1로 시작하지만 E:453–463은 first_yield_day 전 harvest를 거부한다.
상대 money 변화는 매도 수입과 구매·고용 지출이 섞인 순변화다. 그것만으로 품목별 shed를 정확히 복구할 수 없다(E:572–624, 652–696).
market delta도 직접 주문 관측이 아니다. $1 SELL은 inventory를 늘리지 않고 BUY_PRODUCT는 줄이며 town도 소비한다(E:652–672, 728–749).
저장 replay/tape의 상대 action을 runtime에서 볼 수 있는 신호로 취급하지 않았다.

## Claude 사전 확인을 넘어서 확인한 기존 구현 `[LOCAL: source]`

V=`releases/round2-v074/main.py`, D=`releases/exp035-d157/main.py`.

| 이미 존재하는 기능 | exact 코드 근거 | 새로움 판정 |
|---|---|---|
| 보이는 yield로 SELL exposure 계산·순서 변경 | V:1796–1843 | 사전 확인과 일치. 재구현 제외 |
| 상대 harvest 추적→추정 stock 누적→market flow 차감→순서·slot 판단 | D:4791–4957, V:4456 이후 | 단순 standing yield보다 이미 발전한 OR2가 있음. 추정 stock은 진짜 private shed가 아님 |
| clone 판별·선매 패배 감지·reservation horizon 변경 | D:5790–5838, 5849–5879; V:5455–5534 | 타일 유사도뿐 아니라 위치 이력·step1 money도 이미 사용 |
| 상대 동물 placed_day 기반 생산 일정·양측 공급·가격 효과로 생산 선택 | D:5282–5397; V:4947–5062 | 상대 생산량을 보고 COW/SHEEP를 고르는 일반 제안도 중복 |
| 상대 TOMATO planted_day 기반 미래 공급 예측 | D:6722–6761 | maturity forecasting 자체는 이미 있음. 이 경로를 새로 활성화/확장하자는 제안은 아님 |
| 상대 판매 이력과 forecast match, 선매 | D:3459–3536, 7098–7156 | 관측 뒤 상대 유형을 좁혀 판매를 앞당기는 일반 제안도 중복 |
| 최근 market flow 기반 추가 선매 | V:6996–7060; D:7762–7798 | flow를 붙인다는 설명만으로는 새 메커니즘이 아님 |

AST 비교에서 `_or2_tiles`, `_or2_exposure`, `_race_clone`, `_race_lost`, `_hd2_ev`, `_hd2_schedule`은 V/D 간 동일하다.
최종 callable은 V=`exp024_entry`, D=`exp029_entry`. 저장된 parent 함수 객체와 global reference 경로도 확인했다(`audit.json:source_inventory`).
이는 단순히 주석이나 죽은 함수 이름만 찾은 결과가 아니다. 다만 reference 연결은 해당 분기가 실제 발동했다는 증거가 아니며 발동 횟수는 N/A다.
특히 D:4731의 `_OR2_SN_K=0`은 해당 선매 분기를 끈다. 이를 켜는 것은 기존 기능 활성화이며 새 기능이라고 부르지 않는다.

## 검토한 후보 방향 3개 — 모두 미채택 `[INFERENCE]`

| 방향 | 부모·가능한 변경 지점 | 미채택 이유·재검토에 필요한 반증 가능 근거 |
|---|---|---|
| 상대 재고 추정 + 조기 식별 front-run | d157; OR2/RACE 이후 최종 wrapper | 실제 shed는 비공개이고 추정·분기는 이미 구현됨. 새 관측 신호가 기존 OR2/RACE와 다른 action을 만들며 실제 손실을 줄인다는 사례가 필요 |
| suppression에 반응하는 판매 분산·지연 | d157; 최종 market 반환 직전 | 순서 정렬과는 다를 수 있으나, 기다린 뒤 실제 체결가 회복·수량 보존·상대 이득까지 확인한 근거 없음. 단순히 가격이 낮다는 이유로 지연하지 않음 |
| 상대 maturity 예측 기반 판매 일정·생산 배분 변경 | v074 또는 d157; `_hd2_ev`/forecast 소비 지점 | 생산 예측·배분은 이미 있음. 예측을 다른 판매 시점에 쓰는 구체 변경은 새로울 수 있지만 운반·현금·shed 제약 안에서 회복 가능한 손실 사례를 확보하지 못함 |

미채택 방향의 127 변형 / 127 exact / 55be / 기타 효과는 모두 N/A이고, d157과의 예상 W/D/L 상관도 N/A다. 같은 코드라는 이유만으로 상관 수치를 만들지 않았다.
판매 지연 전체를 KILL로 일반화하지 않는다. 다만 MELON 회복 대기(K8), 2턴 선행(K2), 네 번째 땅(K1)은 `evidence/KILLS.md:9–23`의 재검토 조건 없이 재도입하지 않는다.
HYP-0003의 과거 pacing 결과는 다른 부모·상대의 제한된 결과다. 이번 d157 후보의 성능 증거나 전략 전체의 실패로 전용하지 않았다.

## 기존 tape 재집계 `[LOCAL: open-loop]`

대상은 EXP-036 `tape-split.json`의 screen50만이다. 원자료 `experiments/exp033_tapes/games-cloud.jsonl`에서 P/d157 각 50행, episode·seed·seat 일치 및 중복 없음 확인.
모든 사용 행은 DONE/DONE, action_count=719, err=null, agent_errors=[]이다. 개별 원자료 line은 `audit.json:pairs`에 보존했다.

| 계열(meta의 기존 분류) | n | v074 W/D/L | d157 W/D/L | d157 개선 / 악화 pair |
|---|---:|---|---|---|
| 127_full | 6 | 4/2/0 | 4/0/2 | 0 / 2 |
| 127_near | 17 | 1/0/16 | 3/0/14 | 3 / 1 |
| dp_near | 9 | 4/0/5 | 1/0/8 | 1 / 4 |
| other | 18 | 4/0/14 | 7/0/11 | 6 / 3 |
| 전체 | 50 | 13/2/35 | 15/0/35 | 10 / 10 |

이 표는 이미 d157 결과를 보고 고른 screen이다(`experiments/exp036_d157plus/prep36.py:21–24`). 전체 field 승률·독립 검증·hosted 강도로 해석하지 않는다.
점수 일치 30/50, Pearson 0.079765는 이 선택된 v074/d157 표본의 기술통계일 뿐이다. 카드의 d157/d053 90.8%와 비교하거나 상관 감소를 주장할 수 없다.
127_near의 평균 own cash delta −524.29, opponent delta −232.29로, LATE의 선택된 14패배 표본 결론을 전체에 그대로 확대할 수도 없다.
300 held-out tape의 성능 재집계·실행은 하지 않았다. split ID와 공유 원자료 파일은 읽었으나 holdout 행은 계산에서 제외했다.

## 산출물·smoke·검증

- `experiments/altmech_0928/prereg.json`: selected=null, execution_enabled=false. 성능 실험 preregistration 완료를 뜻하지 않는 NO_SUPPORTED_CANDIDATE 종결 기록이다.
- `experiments/altmech_0928/jobs-kaggle.json`: **빈 배열, 0 jobs, 실행 금지**. SHA-256 `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`.
- 원 지시의 future gate(tape lower95>0, closed 각 ≥−0.03, guard pooled ≥−0.02, 1-worker max<0.8)와 EXP-036 panel 참조는 prereg에 보존했다. 후보가 없으므로 통과 판정은 없다.
- smoke: **미실행, 0/24경기**. action 변경 step·예외 수·runtime=N/A. 예외 0 또는 무발동 PASS로 기록하지 않는다.
- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python experiments/altmech_0928/audit.py` → PASS: engine/schema SHA lock 일치, 기존 100행 정합, 50/300 disjoint, 사용 seed 9000–9599 없음, 입력 SHA 유지.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/validate_hypotheses.py --strict` → PASS, 38 entries. 새 HYP-ID·실험 결과·event는 등록하지 않았다.
- 기존 파일 수정 금지에 따라 TASKS/BOARD/FACTS/HYPOTHESES를 수정하거나 updater로 canonical 원장을 갱신하지 않았다. 이는 원장 기록 완료를 뜻하지 않는다.
- source initialization과 reference 분석만 실행했다. 새 게임·다운로드·제출·EXP-036 변경·기존 파일 커밋은 없다. 산출물은 지정 폴더와 이 보고서 1개다.
- BOARD/LEDGER는 09-25 snapshot이며 카드의 새 활성 ID를 아직 담지 않는다. 이번 판단은 사용자가 지정한 09-27 카드 범위이고 live 활성 슬롯을 검증한 보고가 아니다.

## Identity

- V SHA-256 `860a502c36f9a9f700c93125e6828f41378f50d74fa130f62a09f911316ea19c`; D SHA-256 `94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e`.
- `audit.json` SHA-256 `53795ed6b53b6bdce36666664fbc197dc2b2ccdd7494a20f8ab39fe15b0d916e`; `prereg.json` SHA-256 `2eb0137d51f5ccc38d78273baf8995869f5005aadb3c4c4a3a2d87b0aabf0875`.
- engine SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`; split SHA-256 `ca76c617c2c0964ca5b8012b96948af9c3d865dc30723704182dbb8f2a432f48`.

## 다음 행동 2개

1. Claude는 ALTMECH 빈 jobs를 실행하지 말고 EXP-036의 frozen 판정을 우선한다. 이 보고의 중복 목록과 미채택 결론을 owner 원장에 반영하고 BOARD/LEDGER의 최신 상태도 함께 정리한다.
2. EXP-036이 FAIL하면 같은 wrapper를 다시 만들지 않는다. 실제 패배의 pre/action/post에서 기존 OR2/RACE/forecast가 놓친 회복 가능한 손실 1건과 다른 action을 먼저 제시한 뒤, 새 frozen card로만 후보를 재검토한다.


---

## `reports/codex/20260928-1156-HYPGEN2.md`

최우선 가설: 세 마리 SHEEP crew의 WOOL delivery를 먼저 끝내면 일부 동형 상대의 선판매를 뒤집을 수 있다 — 기제 [ENGINE/LOCAL] 중간, 일반 승률 [UNSURE], 이번 구현 **FAIL/STOP**.

작성: 2026-09-28 11:56 KST. 요청한 09:00 KST 보고 시각을 넘겼다. 이 문서가 이번 작업의 유일한 보고서다.

## 비전공자 요약
1. 무엇을 시험했나: d157의 작업 순서에서 비료 수집보다 필수 동물 돌봄·양털 배송을 앞세운 한 요인 후보를 만들었다.
2. 왜 했나: 실제 저장된 hosted 패배에서 양털 판매량은 같았지만, 우리 배송이 3 turn 늦고 WOOL 매출이 3,664 낮았다.
3. 측정 결과: 해당 opponent action을 고정한 replay 한 쌍에서는 패배가 승리로 바뀌었지만, FERTILIZER 판매가 11 줄고 사전 고정한 zero-error gate도 실패했다. Full panel·D3는 실행하지 않았다.
4. 막힌 것: 후보는 승격 또는 두 번째 슬롯 근거가 아니다. 구조가 다른 별도 계열은 패배 trace에서 탐색 신호만 있고 runnable one-change 후보는 없다.

VERDICT | `LOCAL_FAILED` / full STOP | hosted 5패·old 구조패 6판 재추적, 새 게임 37/40·1 worker | parent SHA `94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e`, candidate SHA `34bff195b9a73766814603e9757e769e51c5f71096e101e646a46e712be4761b` | NEXT: 실패를 그대로 기록하고 다른 계열의 exact source부터 확보.

## 근거와 가설 순위
- [LOCAL] 입력 raw 두 window 350+226 중 overlap 163, 고유 episode 413. d157 신규 hosted 40판의 저장된 결과 34/1/5(W/D/L), 5패 모두 day-12 생산 구성 동일: `experiments/hypgen2_0928/field-totals.json:2-13,62`, 케이스 `field-reaggregation.json:416` 이하. 이는 다섯 패배의 분류일 뿐 hosted 미래 strength가 아니다.
- [LOCAL] EXP-033의 frozen open-loop 350 tape 재집계: P 173/7/170(score .5043), d157 278/0/72(.7943); 팀 LB 2200–2400 표시 161 tape에서 P 56/3/102(.3571), d157 123/0/38(.7640): `field-totals.json:14-53`. D·d053·b020의 승패 score는 d157과 각 350/350 동일(`:56-60`); 이를 두 번째 슬롯의 다양성으로 간주할 수 없다. `matrices.json:8057-8111`의 중복 입력 6 key는 action SHA 또는 reward/margin이 충돌한다. W/D/L에는 영향이 없었으나 causal 세부에는 불확실성이 남는다.
- [LOCAL/ENGINE] 저장된 11 hosted action을 engine에 다시 넣어 모든 720-step 상태가 일치했고(`trace_summary.jsonl:1-11`), d157 5패는 원본 action SHA·최종 reward까지 일치했다(`baseline-parity.json:1-26`). 실제 114208752에서는 우리·상대 WOOL 326 unit씩 팔아 각 51,363·55,027을 받았다(`loss-attribution.json:285-296`, `trace_summary.jsonl:7`). step 440 우리 worker 12/13이 `COLLECT_FERTILIZER`를 하는 동안 상대는 이동; step 450 상대는 WOOL 18을 놓아 팔고 우리는 step 453에 놓았다(`rival-delivery-trace.jsonl:2,6-7`). 부모 route `releases/exp035-d157/main.py:2019-2050`, engine 동물 처리 `.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py:490-510,805-835` 및 시장 `:544-628`와 맞는다. 매출 차이만으로 인과를 단정하지 않아 replay로 행동 변경을 확인했다.

| 순위 | 가설·계열 | 부모·근거 | 예상 효과 / d157 승패 상관 | 반증·상태 |
|---|---|---|---|---|
| 1 | 필수 SHEEP tour→WOOL delivery→비료 tour; d157 계열 | frozen d157, 위 114208752 trace | 127 변형·127 exact·55be·기타·LB 모두 N/A(기제 해당 경기 한 쌍만 관측); 같은 부모라 다양성 근거 없음, 상관 미측정 | prereg smoke의 양털·비료 unit 보존 및 error=0 실패. 이 구현 STOP. |
| 2 | 다른 생산 portfolio·route로 구조가 다른 opponent의 품목 조합 대응; **다른 계열** | old hosted 6패 중 5판 상대 TOMATO 28–164 판매, 우리 0; `loss-attribution.json:2-296`, `trace_summary.jsonl:1-6` | 전 panel 효과 N/A; d157 상관 N/A. 구현·검증 시간 N/A, runnable one-change가 아직 없음 | 단순 STRAWBERRY→TOMATO는 과거 M1 score .191 vs parent .936로 이미 실패(`evidence/FACTS.md:226-232`); 정확한 대체 route와 독립 승패 패턴 없으면 후보화 금지. |
| 3 | 공개 10C4S/8C6S macro route; **다른 계열** | 공개 source `analysis/daily_scan/20260926/extracted/kaggriculture-multi-route-farming-agent/main.py:127-145`; SHA `8ac34abce129cf5c9456776c90edf7d2233b3a280bbdcf7622628825ef3669a0` | 전 panel 효과 N/A, 상관 N/A | 기존 EXP-032 G2602 closed-loop에서 P·d157 모두 해당 봇 상대 20/20승: `experiments/exp032_specialist/jobs.json:1`, `matrices.json:1658-1667,6483-6492`; 이 exact 구현은 버림. |

[COMMUNITY] 다른 후보 점검: 2887 fieldcraft source는 독립 SE tomato garden(`analysis/daily_scan/20260922/extracted/kaggriculture-2887-score-fieldcraft-agent/main.py:422-447`)이지만 `mirror_plan` 누락으로 exact package가 없고, title의 점수는 증거가 아니다(`public-candidates.json:2-10`). 반응형 crop source는 `hands=[]`이고 HIRE/BUY_ANIMAL 생성 경로가 없어 strength 근거가 없다(`public-candidates.json:20-27`). 수집일·URL·SHA는 `public-candidates.json:2-36`; engine version 표기는 N/A. 그래서 다른 계열의 second prereg/jobs를 만들지 않았다. 해당 가설들의 반증 panel은 exact runnable source, 고정 parent·50 seed 양좌석, 상대별 score 및 d157과 패배 겹침이 확보될 때만 설계 가능하다.

닫힌 경로 제외: ±1 knife-edge EXP-023/024/026/029/036, EXP-030 bypass, H1 gated lead(`coordination/reports/codex/20260927-1639-H1.md`), late closure(`.../20260927-2126-LATE.md`), 이미 `_r37_quote_priority`로 구현된 front-run(`.../20260927-2311-ALTMECH.md`), marketshock/no-op. KILL은 ENGINE/HOSTED 재검토 조건이 확인되지 않아 재제안하지 않았다. 이 목록은 선택지가 아니라 제외 사유다.

## 사전등록 카드·jobs와 STOP 판정
- 카드 `experiments/hypgen2_0928/prereg.json:1-71`: `HYP-0020`(원장 `HYPOTHESES.md:266-277`), `TEST-HYPGEN2-0928-SHEEP-DELIVERY`, parent/candidate SHA와 한 요인, smoke·full·D3 gate를 실행 전 고정. Card SHA `d384cb94c69918383e30450472fba72c9c9389107aa5fde67f8bbbdccb75452d`. Seed·좌석·상대·runner는 `jobs-smoke.json`, `jobs-full.json`, `jobs-d3.json` 및 `run.py`; source SHA들은 `input_sha256.json`/card에 있다.
- 준비된 jobs SHA: smoke `b24ee402a08de90b870a8e9c36dbbf556ce4f4888bdafed43367072afa74c80d`(26), full `e06a61f5ea59e10903d39dbf6b8fc5467e7b729dd03ecfd0e8edfdaa3dce46fe`(1,960), D3 `069d334deac4eb8990ab6b67b688ec55378049b918a3fbb3aebb8d3715aac688`(30). Full은 arm당 hosted tape350(open-loop)+closed V074/O127/D/d157 각50seed×양좌석=400+guard 23×5×2=230. 5 kernel shard 파일도 준비됐지만 **실행 금지/NOT_RUN**. 9000–9599 holdout 접근 없음.
- [LOCAL] 새 Mac 경기는 exact hosted action 재생 11+smoke 26=37, 1 worker(`trace_summary.jsonl:1-11`, `games-smoke.jsonl:1-26`). 모든 smoke는 DONE/DONE·719 calls·boundary exception 0. Frozen 114208752 한 쌍은 parent margin −3,066→candidate +2,627(차 +5,693), action 44개 변화, WOOL 326 보존(`smoke-summary.json:16-27, primary`); 하지만 FERTILIZER 397→386, 11 unit 손실. 나머지 4패 replay와 4상대×양좌석 closed seed15080에서는 행동·score 동일(`smoke-summary.json:29-186`). 이는 opponent가 재계획하지 않는 replay의 한 쌍 개선이며 full/hosted 성능 증거가 아니다.
- [LOCAL] 사전 gate `prereg.json:24-32` 중 `primary_fertilizer_units_preserved=false`, `all_26_internal_errors_zero=false`(`smoke-summary.json:6-14`). `_S839_REPORT.errors`는 부모에서 물려받아 양 arm 24/26에서 동일하게 발생한 내부 계측 값이며 boundary exception과 구별한다(`smoke-summary.json:191-383`); 비료 손실만으로도 독립적으로 FAIL. Gate 변경·추가 seed 없이 `launch_full.py`는 STOP, full·D3 0경기. Smoke result SHA `8a24b366d7e3f66b17d385450f533eff17399db374ed827c59c6b44962ddb759`; raw jobs result SHA `60e8078be0ccbd83ec47fe0591b1b3ff15b4475acfe9cc83bad1d3cb873fa170`.

검증: `python3 tools/validate_hypotheses.py --strict` → `PASS: 38 entries`; 새 8 Python 파일 `compile(..., "exec")` → syntax PASS. 재집계·trace·게임 판정 명령은 각각 `python3 experiments/hypgen2_0928/research.py`, `trace_saved.py`, `synthesize.py`, `run.py`, `judge.py`(이미 생성된 artifacts를 기준으로 읽기/계산; `run.py` 재실행은 game cap 때문에 금지). 기존 파일·공용 원장 수정, Kaggle 제출·다운로드 없음. 실험 종료 event는 기존 파일 수정 금지와 공용 updater 계약이 충돌하므로 미기록; owner에게 STOP outcome의 tool-managed 등록 필요. `coordination/BOARD.md:3-4`는 09-25 갱신으로 stale; 이 보고서에서 슬롯/제출 결정을 내리지 않는다.

다음 행동 1. Claude/코디네이터가 이 smoke FAIL을 그대로 독립 검증하고 `HYP-0020`의 TEST event를 소유 절차로 기록한다; full/D3 1,990 jobs는 돌리지 않는다.
다음 행동 2. 다른 계열은 2887 garden의 누락 의존성을 포함한 exact runnable source와 패배 패턴을 먼저 확보한 뒤, M1과 구별되는 route one-change 여부를 새 카드에서 판정한다.


---

## `reports/codex/20260928-1802-TOP2400.md`

# TOP2400 d157′ 최종 보고 — 2026-09-28 18:02 KST

1. **시험:** d157이 이미 내보내는 인접한 WHEAT `BUY_PRODUCT`→`SELL`의 순서만 조건부로 뒤집은 d157′를 만들고, 결과 전에 고정한 선택 패널로 평가했다.
2. **이유:** 선택 팀 상대 d157 패배 20판에서 상위 팀의 실제 WHEAT 매수·매도가 d157보다 훨씬 많았다. 순서가 상대의 거래 가격을 바꿔 승패를 뒤집는지 확인했다.
3. **측정·결과:** 1,190/1,190 로컬 선택 경기가 유효했다. 595개 페어의 승·무·패 차이는 전부 0이고, 평균 점수 차이와 bootstrap 95% 하한 모두 0.0이다. 사전등록의 하한 `>0`에 실패했다. 선택 팀 595개 원본 리플레이도 595/595 엔진 상태가 일치했다.
4. **막힘·다음 행동:** 이 정확한 한 요인 후보는 `LOCAL_FAILED`다. U·T·family·O127/V074 및 holdout 5팀은 실행·판독하지 않았다. 제출하지 않는다. 다음 전략은 새 원인 증거와 별도 사전등록이 필요하며, 이번 실패를 피하려고 이 후보의 기준을 바꾸지 않는다.

`LOCAL_FAILED` | select 595페어 중 점수 flip 0, 행동 변화 134 | parent SHA `94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e`; candidate SHA `320f8bc92726d163e1d6569d8c664c66a5df270e6081236cc6fb5fc6bbd451cf` | `python3 experiments/top2400_codex/judge.py` → `select_point=0.0`, `select_lower95=0.0`, `holdout=UNOPENED` | NEXT: 후보 폐기, 독립 검증 후 새 카드 판단.

## 사전등록과 실행 경계

- `[LOCAL]` 사전등록은 결과 전 `experiments/top2400_codex/prereg.json` SHA-256 `578f171b6b14b22050f73c275666d901ac0bee97117f9f8aad33d052c008be8d`로 고정했다. 변경 조건은 같은 파일의 `one_change`와 `decision`에 있다. 구현은 `experiments/top2400_codex/d157_order_swap.py:10145-10192`; 부모의 앞부분은 동일 바이트다. 가설 다섯 개 이하와 채택·보류 사유는 `experiments/top2400_codex/hypotheses.md:5-13`이다.
- `[LOCAL]` 1-worker smoke 40/40 DONE/DONE, 후보 행동 719회/경기, 오류 0, 행동 SHA 변화 8/20페어, 후보 최대 턴 0.495164초. `games-smoke.jsonl` SHA `57f9da2fea6ebe077a4b8024aa199071ea246408898b0d995f46a5c6bacb4551`.
- `[LOCAL]` 최초 실행기의 tape `null` 파싱 결함으로 발생한 57개 진단 행은 판정에 쓰지 않았다. 실패 행은 `games-select-loader-failure.jsonl` SHA `8e63012fa35a37d8b9eb2a19d975ee6e29510b4656d0f4aa8cfafbe4a578bfe9`로 보존했다. JSON tape만 그대로 읽도록 수리한 `run_frozen.py` SHA `12f7c843a57726c3b134951eaa7a8643bb536d0a52370e5d290172857308cdb1`; 수리 기록은 `harness-repair.json` SHA `d24976b103512b0906229761b3cee9ebb2ee3e61f930a0886322763123ec87b7`, 판정 전 동결 기록은 `execution-freeze.json` SHA `16a76d7ff0e260ab9d67a4d559bbfb4dafa3e10b0ee61db8bf48836be28a7b91`이다. 후보·jobs·threshold는 바뀌지 않았다.
- `[LOCAL]` 선택 결과 `experiments/top2400_codex/games-select.jsonl` SHA `e1cd056263b581faf81b2390780aa4465acf2a0db7292b7d76aee11f6a8cc9c4`: 1,190개 고유·유효 job, d157/후보 595페어. d157과 후보가 각각 238승·1무·356패; 페어 점수 차이 595개 모두 0. 행동 SHA는 134페어에서 달랐고, 최종 코인 차이는 74페어에서 달랐다. 코인 격차의 후보−d157 평균 −1.0303, 최소 −30, 최대 +6이며 승격 지표가 아니다. 후보 최대 턴 0.510358초. 독립 집계 `select_result_summary.json` SHA `4f3534a40a43c2840349e3102a7cc996a4eebac3a98b21f6cafe9772ac435c47`; 재현: `python3 experiments/top2400_codex/summarize_select_result.py`와 `python3 experiments/top2400_codex/judge.py`.
- `[INFERENCE]` 이 결과는 같은 엔진의 **고정 상대 행동 tape에 대한 로컬 결과**다. 실시간으로 반응하는 상대, hosted 레이팅, Kaggle 제출 성능을 증명하지 않는다. `holdout` 결과는 없다.

## 체결 기준 분석

`[HOSTED→LOCAL REPLAY]` 선택 팀을 상대한 d157의 실제 패배 20판을 원본 양 좌석 행동으로 재생했다. 원본 상태·보상 20/20 일치. 원시 단계별 체결은 `experiments/top2400_codex/select_loss_fills.jsonl` SHA `b07e2a8071d84bfbd3ed4d38d8c3de7b7a0c9208c0b3cd1bc4f0bf53d921f956`; 집계는 `select_loss_summary.json` SHA `8d8f2d851a49d527eadbce10fa31d900d3a8f432a4996df81925f472c3c2667d`. 재현: `python3 experiments/top2400_codex/replay_fills.py && python3 experiments/top2400_codex/summarize_fills.py`. 재생은 경기 결과를 새로 관측한 것이 아니라 이미 받은 hosted 원본의 동작을 복원한 것이다.

| 20패, 품목·동작 | d157 요청→체결 | 상위 팀 요청→체결 | 상위 팀 체결 현금 |
|---|---:|---:|---:|
| WHEAT 매수 | 6,754→6,687 | 30,961→30,891 | 지출 1,266,747 |
| WHEAT 매도 | 11,284→10,920 | 54,765→35,298 | 수입 1,445,883 |
| CARROT 매도 | 2,472→2,362 | 20,398→2,813 | 수입 126,957 |
| FERTILIZER 매도 | 7,107→6,723 | 21,145→6,811 | 수입 307,577 |
| MILK 매도 | 4,779→3,911 | 12,586→3,804 | 수입 358,736 |
| WOOL 매도 | 4,648→3,875 | 10,456→3,876 | 수입 507,216 |

`[LOCAL]` WHEAT 순매도 체결은 상위 팀 4,407, d157 4,233개로 20판 합계 차이가 174개다. 상위 팀의 WHEAT 매도 현금−매수 현금은 179,136, d157은 170,997으로 차이 8,139(판당 406.95)이지만 생산·사료·상대 가격·재고 효과가 섞여 있어 **순이익이나 승리 원인으로 식별되지 않는다**. 큰 주문 수량은 다른 품목에서도 체결량으로 이어지지 않았다.

`[HOSTED→LOCAL REPLAY]` 그 뒤 holdout 5팀을 제외한 선택 팀 전체 원본 595판을 독립적으로 재생했고, 상태 일치 595/595였다. `select_all_fills.jsonl` SHA `04adf6ee4dafd3377dbda5b0dcb6037e8956d16715f5585d5f26e76d5020f4ba`, `select_all_summary.json` SHA `5fbc9181d9fc60807ee382176bd1d09f1d98511915b6b5f320b9ad75d874016e`. 재현: `python3 experiments/top2400_codex/replay_select_all.py && python3 experiments/top2400_codex/summarize_select_all.py`.

| 선택 팀 595판 | 요청 | 실제 체결 | 체결 현금 |
|---|---:|---:|---:|
| WHEAT 매수 | 878,817 | 870,053 | 지출 35,100,550 |
| WHEAT 매도 | 1,584,069 | 1,000,996 | 수입 40,390,736 |
| CARROT 매도 | 608,950 | 84,367 | 수입 4,149,669 |
| FERTILIZER 매도 | 602,963 | 199,722 | 수입 9,254,336 |
| MILK 매도 | 379,338 | 117,048 | 수입 12,366,907 |
| WOOL 매도 | 289,481 | 93,062 | 수입 11,261,656 |

`[ENGINE]` `_process_market`는 주문 슬롯을 순서대로 처리하고 두 좌석의 단위 가격을 같은 체결 전 시장 재고로 산정한다(`kaggriculture.py:544-628`). WHEAT 매수는 매수 후 재고 가격으로 견적돼 시장 변화가 없으면 자기 매수→매도 왕복은 0이다(`:597-602`). 매도는 shed가 비면 중단되고, 매수는 현금 또는 shed 용량이 부족하면 중단된다(`:652-674`). 따라서 WHEAT의 큰 **요청**은 주문 스팸 여부나 이익을 증명하지 않는다. 20패의 실제 순매도량이 비슷하고 595판의 WHEAT 매도 요청 체결률은 63.2%다. 상위 팀의 주관적 목적(가격 조작·사료 확보 등)은 관측 자료만으로 `UNSURE`다.

## 무결성과 소유권

- `[LOCAL]` `python3 tools/validate_hypotheses.py --strict` → `hypothesis ledger PASS: 38 entries`. 공용 기존 파일은 수정하지 말라는 카드의 금지 때문에 `HYPOTHESES.md` 갱신기는 실행하지 않았다. 이 테스트 ID와 결과는 위 신규 보고서에 기록했다.
- `[LOCAL]` holdout 5팀을 선택·튜닝·체결 분석에 사용하지 않았고, 금지된 9000–9599 seed도 실행하지 않았다. 제출·다운로드·외부 코드 공유는 없었다.
- `[INFERENCE]` 독립 검증자가 이 exact 후보의 실패 판정을 확인하면 종료할 수 있다. 다른 가설을 다시 구현하려면 별도 소유 실험 카드·사전등록과 새 결과가 필요하다.


---

## `reports/codex/20260928-2132-EXP045v2.md`

VERDICT: IMPLEMENTED_SMOKE_PASS — BOARD 기준 d157 56607884 / c26 56635330 일치; Stage A 본 실행 N/A.

1. 무엇을 바꾸는가: d157 exact(94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e)에 기존 판매층 우회 8개와 외부 판매 규칙 3개를 각각 한 위치에서 적용했다. PREREG 및 고정 상수는 변경하지 않았다.
2. 왜 하는가: EXP-044 FINDINGS 6번의 상대 관측 정정을 반영하고, 기존 판매층 및 WOOL/MILK 매도 결정을 Stage A에서 분리해 시험하기 위해서다. 이 보고는 smoke 결과이며 우위 판정이 아니다.
3. 측정: select 19팀 595 tape에 대해 jobs-A 6,545건(kaggle 3,927 / mac 2,618, prep42 형식)을 생성했다. holdout 팀 0건, 금지 seed 9000–9599 0건. smoke 11×4=44판 모두 DONE/DONE, 719 calls, errors 0, max step <0.5s. 모든 변형 Δact 4/4이며 무발동 0개. 첫 smoke의 신규 규칙 진입점 오류 10행은 `experiments/exp045_sale/smoke-initial-errors.jsonl`에 보존했고 수정 후 해당 12판을 재검증했다.
4. 다음: Antigravity가 Stage A jobs만 실행한다. Stage B jobs·제출·엔진/RNG 수정은 하지 않았다.

| 변형 1 | 변형 2 |
|---|---|
| **K1** `8b9dc5b19e718decfe1961731f7f988c04277f8a4280211ed72d8c9732919780` [K1.py:4793](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/K1.py:4793) · 1줄 · DONE 4/4 · Δact 4/4 · max 0.126s | **K2** `3186dc30062795e5d5f2cbbc58fb45575c56c178d7086fefdf83929c5c0b1f3a` [K2.py:3852](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/K2.py:3852) · 1줄 · DONE 4/4 · Δact 4/4 · max 0.175s |
| **K3** `b4599627317e7e55ccfad5f128959af00cd981387bc18f86e9085381b0543b6f` [K3.py:7763](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/K3.py:7763) · 1줄 · DONE 4/4 · Δact 4/4 · max 0.106s | **K4** `7a486c5e21666e50df1812117451d2bb5e4340ebe6b81c80d8869488f9a11c0e` [K4.py:7896](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/K4.py:7896) · 1줄 · DONE 4/4 · Δact 4/4 · max 0.066s |
| **K5** `a8d0d29a765f6560d32e3f7b7ee418667c8e26003464a0d9f53f4938f843003f` [K5.py:7113](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/K5.py:7113) · 1줄 · DONE 4/4 · Δact 4/4 · max 0.181s | **K6** `d4d217ea2d718a5c8687b6a1ffb91cc05a5d969ea5a03f794320ca9cd156f4ff` [K6.py:7514](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/K6.py:7514) · 1줄 · DONE 4/4 · Δact 4/4 · max 0.106s |
| **K7** `493e99f7c52074bf7aef104a5338ce4ec179e1a50689f41af6d6beb9b18b0956` [K7.py:6122](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/K7.py:6122) · 1줄 · DONE 4/4 · Δact 4/4 · max 0.107s | **K8** `49d022dcb9b8cb460bff441f408dc8f83a2a897b954edf3561d826264cf454ea` [K8.py:8736](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/K8.py:8736) · 1줄 · DONE 4/4 · Δact 4/4 · max 0.116s |
| **G_A** `119f06557e4953572094396c10762771625f4547b0904567fe54589787b466a4` [G_A.py:10145](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/G_A.py:10145) · 115줄 · DONE 4/4 · Δact 4/4 · max 0.062s | **G_B** `1136bd87e4dd36af81438699b0075829aebbf92602410ac6d2ba6bb7a2b9b6b5` [G_B.py:10145](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/G_B.py:10145) · 116줄 · DONE 4/4 · Δact 4/4 · max 0.079s |
| **B6** `6cb821d13029101b67b7f09cdfb96505fc7a778e40c00992ec22f00c627080c1` [B6.py:10145](~/kaggle/Kaggriculture/experiments/exp045_sale/variants/B6.py:10145) · 132줄 · DONE 4/4 · Δact 4/4 · max 0.109s | — |

파일: `experiments/exp045_sale/manifest.json` SHA-256 a2f0c47d08a3da258f029d2b36cd94db363e4fdb40f8e3395e6947b893a75cfe; `jobs-A-kaggle.json` f6eefc0f414b533bdc6c8623269626c8582387ea1c18c6e00ca08560540af785; `jobs-A-mac.json` 1815ef54fa0376416a2979ec3c3fdc5ead7081cd52458805ddf2a11f047c8836; `smoke.jsonl` 62705799c9f1bb1b58be518248bb0e52435087d53dd20f57299444b160ec3809.
재현: `python3 experiments/exp045_sale/build.py`; smoke panel과 runner는 `experiments/exp045_sale/smoke.py` 및 `smoke-panel.json`. PREREG SHA-256 8909d320e62a19c7a2cbdb87d3d350c741039eaa46769efc75fcb02acb161c45.


---

## `reports/codex/20260928-2133-EXP047.md`

VERDICT: PREPARED_DIAGNOSTIC_WEAK — BOARD와 카드 기준 상태(d157 56607884/c26 56635330) 일치; 본 실행·최종 판정 N/A.
[LOCAL] 목적: d157의 기존 `_front_run`에 공개 55be shadow의 상대 SELL 예측을 연결했다. 이유: 상위 팀의 55be 판매 유사성(`analysis/exp046_predict/FINDINGS.md:1-10`).
[ENGINE/LOCAL] hook 입력은 `opponent_plan[step+1]`의 action dict `market` SELL 목록; `front_run` 활성·plan 존재·own next SELL·shed·가격·주문 슬롯이 발동 조건(`releases/exp035-d157/main.py:487-488,662-690`).
[LOCAL] 상대 shed 추정은 `_OR2_STATE[seat]['stock']`(`releases/exp035-d157/main.py:4794-4832`); 현재 관측 delta를 같은 OR2 식으로 선반영(`experiments/exp047_oppmodel/variants/hook.py:10168-10203`).
[LOCAL] 다음 step 근사: 현재 공개 farms/market/town과 추정 shed를 유지하고 step/day/hour만 +1; seeds·inventories는 빈 값(`variants/hook.py:10205-10221`). shadow 원문 SHA 55be5d5f124c8daa…, 후보 SHA d9dd9cbe813e27554d6a39fadb70749b0e2066dcdf24807dd5164cd3ea38ef20(`variants/hook.py:10145-10166,10223-10253`).
[LOCAL] select 20판 WOOL/MILK/STRAWBERRY step 사건 추정 recall/precision 0.83884/0.11429 (TP 2030, FP 15732, FN 390); 같은 20판 비공개 상태 상한 0.87834/0.55333 (TP 2101, FP 1696, FN 291). 상한은 full step, 추정은 next-step 1..718이므로 경계 1 step 차이(`experiments/exp047_oppmodel/diagnostic-20.json`; 재현 `python3 experiments/exp047_oppmodel/diagnose47.py 20`).
[LOCAL] 1 worker 최대 호출: tape 진단 0.41272s, 4판 엔진 smoke 0.26093s (<0.8s); smoke 전부 DONE/DONE·719 calls·agent errors 0(`experiments/exp047_oppmodel/games-smoke.jsonl`).
[LOCAL] 후보 1개만 준비, 기본 hook 상수 유지; jobs-A select 595 = Kaggle 357 + Mac 238, smoke 4(`experiments/exp047_oppmodel/manifest.json`, `jobs-A-kaggle.json`, `jobs-A-mac.json`). `python3 tools/validate_hypotheses.py --strict` PASS.
NEXT: Antigravity가 본 실행, Claude가 `analysis/exp045/PREREG.md`+vs D paired 차 ≥0 판정. 낮은 예측 precision은 실패 위험; hosted 우위·제출 근거 N/A. 사용자 지정 쓰기 범위에 따라 가설 원장 event·commit은 수행하지 않았다.


---

## `reports/codex/20260929-0920-FIRSTPRINCIPLES.md`

VERDICT: [LOCAL] 두 초기 접근 모두 고정 개발 기준 FAIL; 현재 새 bot/release 없음. 제출 없음.

1. 무엇을 시험했나: 공개 원본을 복제한 판매 순서 가정 대신 여러 상대 주문 시나리오에 견디는 주문 탐색(A), 공개 농장 모습으로 c26/d157 정책을 고르는 게임별 전환(B)을 시험했다.
2. 왜: 비공개 55be 변형은 공개 원본과 경기당 중앙값 15 step 정도 다르고 후반에 차이가 몰린다. 같은 tape의 c26 우위와 낮은 초기 hosted 점수 사이의 원인도 분리해야 한다 (`coordination/reports/claude/20260929-EXP050-051-LOSS-ANALYSIS.md:3-14`).
3. 결과: 고정 개발 214 tape에서 A는 c26 대비 +0.0047(95% bootstrap 하한 −0.0187), B는 +0.0000(하한 0). 고정 기준 +0.030 초과·하한 >0을 둘 다 충족하지 못했다. A의 target 41 tape는 오히려 −0.0244. A D3 단일 worker 15경기 max 0.3935s, 오류 0, PASS지만 성능 FAIL을 덮지 않는다.
4. 막힘/다음: holdout 55경기와 09-29 새 hosted 전방 holdout을 열지 않았다. 두 접근 상한을 유지하면 NO_CANDIDATE로 종료한다. 추가 구조적 접근은 사용자 범위 결정 뒤 새 실험으로만 한다.

## 접근 평가 (후보 결과 전에 작성)

| 접근 | 예상 이득 | 위험 | 시간 | 선택 |
|---|---|---|---|---|
| 불확실한 상대 주문을 둔 시장 주문 탐색 | 후반 판매 경쟁의 작은 패배 뒤집기 | 주문 예측 오류·지연 | 4–7h | A |
| 공개 농장 형태에 따른 정책 전환 | 55be 근접 상대와 나머지 구분 | 초기 형태 중복·작은 정책 차이 | 3–5h | B |
| 생산 경로 재설계 | 판매 시점 자체 변경 | 전 기간 행동 예산·시장 피드백 | >15h | 보류 |
| terminal 물리 inventory planner | 마지막 cargo 회수 | 기존 EXP-039 유사 실험 재탕 | 6–10h | 보류 |
| 55be shadow 다음 SELL 예측 | 선매도 | 기존 precision 0.114 | 4–8h | 제외 |
| market-only replay graft | 상대 판매 재현 | K3 재검토 조건 없음 | 2–4h | 금지 |
| WHEAT 작물 순환 | 생산 여력 재배치 | WOOL/MILK 단가가 실제 변동축 | 8–12h | 제외 |
| 두 슬롯 포트폴리오 | 상성 분산 | 이 카드의 1 bot 목표·제출 금지 밖 | 1–2h | 보류 |

근거와 선택·기각 사유: `experiments/fp_robust/PLAN.md:5-18`, SHA-256 `8f24c83b04603640630dc386f1301efffa0276ee23d821f181373bb936ffd147`.

## 고정 기준과 실행 증거

- 기준/시간 분리: `experiments/fp_robust/freeze.json` SHA-256 `f86818c897f38befcb632500a9ef2a6ef0676db5e55365f13ea5d2906db9d44f`, EXP-051 269경기 중 제출별 최신 ceil(20%) 55경기를 holdout, 개발 214. 추가 09-28 17:27 UTC 이후 경기는 전방 holdout. 기준은 `PLAN.md:20-48`; 개발 결과 뒤 변경 없음.
- 엔진 [ENGINE]: `.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py` SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`.
- 후보 A/B [LOCAL]: `experiments/fp_robust/variant_a_v2.py` SHA-256 `68ac4ea24747dfd3dea6b38f7e7c78acf34295cfff8de3e0ef8c38b2b0cfaaa0`; `variant_b_v2.py` SHA-256 `cab425ac3c05ef7ba69205e3c61a193a922b29b97528d3a8f9f109cfaf778b94`. 첫 smoke의 get_last_callable 진입점 오류는 v1 바이트와 실패 row를 보존하고 v2에서 수정했다(`games_smoke.jsonl`, `games_smoke_v2.jsonl`). v2 smoke 4/4 DONE/DONE, 719 calls, 오류 0.
- 개발 [LOCAL]: `experiments/fp_robust/games_dev_v2.jsonl` 428/428, 각 후보 214/214 DONE/DONE·719 calls·agent errors 0. `dev_verdict.json` SHA-256 `3213e7b4d1d320150b6edd2510f39b0dc344d8762de2d5d0e4840d41428f2474`; 재현 `python3 experiments/fp_robust/judge_dev.py`.
- A: c26 대비 +0.00467, d157 대비 +0.02570; 두 95% 하한 −0.01869. 2200–2400 55be 표본 41개에서 c26 대비 −0.02439, d157 대비 0. A 행동 SHA는 c26과 166/214경기 다름. B: c26 대비 0, d157 대비 +0.02103; 변경 22/214. A의 점수 변화 8경기 대부분 공개 55be FULL, 비공개 prefix는 1경기 이득(`flip_timing.json`, `dev_verdict.json`).
- D3 [LOCAL]: `experiments/fp_robust/d3_a_v2.json` SHA-256 `40542ddf82083e9a988a27d083506d0461296ab37988350ad32b2a4fbab25548`, 1 worker fresh-process 15경기 max step 0.3935s, max total 3.347s, 예외/invalid 0; 실행 `D3_CAND=experiments/fp_robust/variant_a_v2.py D3_CAND_SHA=68ac4ea24747dfd3dea6b38f7e7c78acf34295cfff8de3e0ef8c38b2b0cfaaa0 D3_RESULT=../fp_robust/d3_a_v2.json python3 experiments/d3_gate_v2/measure_gate_v2_claude.py`. B D3 N/A(개발 gate FAIL).

## c26 tape와 hosted의 차이

[LOCAL] 같은 269 tape의 c26−d157 +0.030은 고정된 상대 행동을 재생한 paired 결과이고, tape agent는 관측과 무관하게 step별 기록 행동을 반환한다(`experiments/exp051_curpop/prep51.py:5-15`). [ENGINE] 실제 상대는 매 턴 변한 공유 시장과 농장을 본다(`kaggriculture.py:247-274,544-611,952-956`). 따라서 정책 반응은 tape에서 측정되지 않는다. [HOSTED] c26 초기 82경기의 승점은 0.799였지만 상대 LB 중앙값이 시간 순 1496→1788→1901로 상승했다(`coordination/reports/claude/20260929-EXP048B-C26HOSTED.md:12-17`); 09-29 09:10 KST snapshot의 c26 LB는 1920.6(`analysis/hosted_20260929pm/lb_scores.txt`). [INFERENCE] 초기 1900 미만은 수렴·매칭 차이와 양립하며, tape 정책 반응 누락도 가능한 설명이다. 각각의 인과 비중은 UNSURE.

## 남은 위험

1. [LOCAL→HOSTED] tape gain은 실제 상대 반응과 레이팅을 보장하지 않는다; 비공개 변형의 정책 코드는 없다.
2. [LOCAL] 초기 공개 농장 모습은 두 계열이 겹쳐 B가 c26의 214개 중 22개 행동 궤적만 바꿨고 승패는 하나도 바꾸지 못했다. d157/c26 oracle 선택 상한은 c26 대비 +0.0374/214여서 고정 +0.030 gate를 안정적으로 넘기 어렵다(`python3 -c` 계산은 `dev_verdict.json`과 EXP-051 원본에서 재계산 가능).

NEXT ACTION: 후보 release 없음, holdout 봉인 유지, 제출 없음. `experiments/fp_robust/` 외 쓰기는 사용자 지정 이 보고서 한 파일뿐이다. 사용자 범위 결정 전 추가 접근 실행 없음.
`python3 tools/validate_hypotheses.py --strict`는 38 entries, exit 0. 사용자 지정 쓰기 제한 때문에 새 hypothesis event는 기록하지 않았다.

## 09-29 13:55 KST 재개 검산 및 최종 판정

VERDICT | [LOCAL] NO_CANDIDATE. A/B의 고정 개발 gate FAIL을 독립 재집계로 확인했으며 새 release·제출은 N/A. 시간 분리 holdout 55경기와 전방 holdout은 봉인 유지.

- `experiments/exp051_curpop/games.jsonl`과 `experiments/fp_robust/games_dev_v2.jsonl`에서 214개 episode key를 직접 join했다. A−c26 승점 합계 `+1.0/214`(변화 8경기: +1 세 건, −1 세 건, +0.5 두 건), A−d157 `+5.5/214`. 2200–2400 `55be*` 41개에서는 A−c26 `−1/41`, A−d157 `0/41`. B−c26은 `0/214`(전 경기 동일 승점), B−d157 `+4.5/214`. 고정 요구 `>+0.030` 및 95% 하한 `>0`은 A/B 모두 FAIL(`PLAN.md:28-43`, `dev_verdict.json:2-38`).
- d157/c26 중 결과가 좋은 쪽을 사후에 고르는 비실행 가능 oracle조차 c26 대비 승점 합계 `+8/214=+0.0374`다. 실제 관측 기반 B는 +0이므로 같은 두 정책의 선택기만 다시 조정하는 방향은 우선순위가 낮다. 이것은 새 정책의 상한이 아니다.
- 09-29 추가 hosted snapshot은 `analysis/hosted_20260929pm/summary.json` SHA-256 `3506facff44787fe105ba8545eeb93b74af53cd36f54f94b8a8a173a96018eab`, 기준 시각 `as_of.txt:1`(09-29 08:38 KST)이다. d157 219경기 103W/10D/106L, c26 112경기 85W/2D/25L이지만 상대 배정이 다르다. 2200–2400 **상대 팀 LB band**는 d157 95경기 30W/1D/64L, c26 겨우 6경기 4W/0D/2L이다. 이 표본으로 c26의 해당 상대군 우위나 2300+ 도달을 확정하지 않는다. 09-29 09:10 KST LB snapshot은 d157 2215.9/c26 1920.6(`lb_scores.txt:1`); 두 제출의 나이·매칭이 달라 직접 성능 차이로 해석하지 않는다.
- 종료 검증: 위 두 JSONL의 key join으로 원래 `dev_verdict.json`의 승점과 target 수를 재현, 다섯 artifact SHA-256이 기존 보고와 일치, `python3 tools/validate_hypotheses.py --strict` 38 entries PASS. 새 전략 후보·성능 주장은 만들지 않는다.

NEXT ACTION | 이 카드의 최대 2개 구조 접근을 모두 사용했으므로 여기서 닫는다(`coordination/proposals/claude/20260929-FIRSTPRINCIPLES-CODEX.md:17-20`). 후속 실험은 결과를 본 A/B 재튜닝이 아니라 **새 카드/새 동결 기준**으로 시작한다. 우선 공개 state에서 반복 관측 가능한 패배 기제가 있는지 패배 trace에서 찾아야 한다. 없다면 `NO_CANDIDATE`로 보고하고 활성 d157+c26을 유지한다. hosted 2300+는 현재 N/A.


---

## `reports/codex/20260929-1005-KNOBS.md`

# d157 생산 구성 손잡이 지도 — 2026-09-29 10:05 KST

**판정: 조사 완료 / bot 변경 N/A.** A·B는 기존 기준대로 종료했고 시간 분리 holdout은 봉인 상태다. 이 문서는 상위 300 전수조사 결과가 들어왔을 때 생산 구성을 바꿀 정확한 지점을 찾기 위한 정적 코드 지도다. 대전·후보 생성·제출은 하지 않았다.

**왜 보는가:** `[LOCAL]` EXP-053은 Fritz의 조기 땅·연속 토마토와 juliencst의 거위·밀 구성이 d157과 다르다고 관측했다(`analysis/exp053_tomato/FINDINGS.md:7-11`). 이는 인과 증거가 아니다. `[LOCAL]` EXP-054에서는 후반 단발 토마토의 매출 문턱만 9000→7000/6000으로 낮춘 두 변형이 모두 실패했다(`coordination/reports/claude/20260929-EXP054-TOMGATE.md:1-9`). 따라서 survey 결과가 어느 생산 축을 가리키는지 확인한 뒤 해당 축의 일정·종자·노동·시장 주문을 함께 다뤄야 한다.

**기준 파일:** `releases/exp035-d157/main.py` SHA-256 `94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e`. 아래의 시간은 `[INFERENCE]` 단일 변경을 구현하고 호출·액션 정합성을 짧게 확인하는 작업 시간이다. panel 평가 시간은 포함하지 않는다. “폭”은 관찰된 경기 결과가 아니라 해당 코드가 건드릴 수 있는 행동 범위다. route의 파종·매입 건수는 압축 `_R108_DATA`를 읽기만 하여 집계한 **계획 테이프**이며 실제 체결·수확 건수가 아니다.

| 생산 축 / 손잡이 | 코드 근거 (파일:줄) · 현재 동작 | 변경 방법 · 1회 예상 시간 | 행동 변경 폭과 주의점 |
|---|---|---|---|
| 작물: **멜론·딸기** 기본량 | `releases/exp035-d157/main.py:947-949,982-986`의 압축 route 41종은 모두 `PLANT MELON` 12회(day 0), `STRAWBERRY` 33회(day 5–8, 11). | **route 편집**, 종자 구매·파종·물·수확·운반·판매까지 재배치. 6–12시간/작물 일정. | **매우 넓음**: 하루의 여러 일꾼과 후속 시장 주문. route 선택표만 바꿔서는 두 작물량이 그대로다. 멜론 재배분 K10은 철회된 항목이지 확정 금지가 아니다(`evidence/KILLS.md:15`). |
| 작물: **밀·당근** 기본 비율 | `main.py:947-949,961-980`: route별 파종 계획 WHEAT 156–165회, CARROT 28–38회. `main.py:6980-7015`는 후반 밀·당근 씨앗 구매 상한을 별도로 자른다. | 기존 route 선택 **표 편집** 1–2시간; 새 총량·날짜라면 **route 편집** 4–8시간. | 표 교체는 선택된 route의 밀↔당근·동물·고용까지 함께 바꾸지만, 새 작물 일정은 만들지 않는다. 새 route는 후반 씨앗 가드와 동기화해야 한다. |
| 작물: **밀→당근** 초기 반응 전환 | `main.py:3047-3052,3075-3113`: V9가 day 10–23에 가격 비·보유 밀 기준을 만족하면 예정된 밀 파종/씨앗을 당근으로 바꾸고 부족 사료를 구매한다. | `V9_CARROT_RATIO`, 날짜·feed reserve **상수** 또는 `_v9_carrot` **모듈**. 상수 0.5–1시간, 조건 재설계 2–4시간. | **중간**: 조건 성립 판의 해당 밀 파종과 씨앗·수확·판매. 뒤의 CA 층과 중첩되므로 단독 변경 효과를 action diff로 확인해야 한다. |
| 작물: **밀→당근** 후속 수익·수확 전환 | `main.py:4473-4482,4647-4709`: CA가 day 6–28, 수익·사료·남은 방문·씨앗 조건으로 밀 파종을 당근으로 바꾸며 씨앗 버퍼·조기 수확·판매를 관리한다. | `_CA_MARGIN`, `_CA_FROM/TO`, `_CA_BUFFER`, `_CA_FEED_DAYS` **상수** 0.5–1시간; 방문 예측/수확 **모듈** 3–5시간. | **넓음**: 여러 날의 밀·당근·사료·매도. c26은 바로 이 margin 변경 계열(`coordination/BOARD.md:9`); 단순 재튜닝은 새 구조가 아니다. |
| 작물: **토마토** 기존 후반 단발 투자 | `main.py:1265-1286,1296-1353,1380-1409,1412-1425,6711-6715,6764-6806`: day 18에 매출 9000 이상이면 SE 땅·씨앗 10개·전용 고용, day 26–29 수확. 최종 `_v219_qualifies`는 CXTB 매출 예측으로 연결된다. | `_CXTB_MIN_REVENUE` **상수** 0.5시간; day 18·10그루·노동/구획을 바꾸려면 **모듈** 4–8시간. | 상수는 **좁음**: 기존 10그루 투자를 여는 판만 변경. EXP-054의 7000/6000 완화 FAIL; Fritz식 day 9–19 연속 파종은 이 상수로 구현되지 않는다. |
| 작물: **토마토** 조기 소 대체 opening | `main.py:6473-6517,6528-6545,6601-6614`: 기본 `_ALT_MODE='HybridOpening'`; 기존 `TomatoInsteadOfCow` 분기는 첫 소 1마리를 토마토 1그루로 바꾸며 step 0–95 route 0과 opening 시장표 `CT_TABLE`도 수정한다. | `_ALT_MODE` **상수** 0.5–1시간; 확장 파종은 opening **route/모듈 편집** 4–8시간. | **중간**: 첫 96 step의 소·토마토·밀 거래가 함께 바뀐다. 확대하려면 이후 물·수확·구매까지 이어야 하므로 Fritz 구조의 대체재는 아니다. |
| 가축: **소·양·거위 기본 수** | `main.py:947-949,961-980`: 41 route의 계획 총량 범위 COW 4–9, SHEEP 4–14, GOOSE 0–5. route 0은 8/6/3, route 9는 6/11/0. | 기존 route 선택 **표 편집** 1–2시간; 목표 수량이 route에 없으면 구매·축사/목장·배치·사료·수확을 **route 편집** 6–12시간. | **넓음**: 해당 route의 생산·일꾼·시장 주문 전체. 계획 구매량은 실제 사육 수가 아니다. 거위 증가는 K9 재검토 조건(여유 액션과 EGG 수요)이 성립하는 근거를 따로 확인해야 한다(`evidence/KILLS.md:14`). |
| 가축: **초기 소→거위** | `main.py:5529-5535,5559-5623,5660-5710`: CS가 step 144–191 첫 소 구매를 보며 shop·예상가치 조건 통과 시 소 주문과 목장 작업을 거위/축사 작업으로 바꾼다. 기본 후보는 GOOSE 한 종. | `_CS_RATIO`, `_CS_MIN_GAIN`, `_CS_SHOP_RULE` **상수** 0.5–1시간; 물리 작업 계획은 `_cs_plan` **모듈** 3–5시간. | **중간**: 첫 소 묶음의 종·건물·운반·판매. 수량 확대 손잡이는 아니며 계획이 성립해야만 전환한다. |
| 가축: **거위→양·소** V9 | `main.py:3161-3165,3169-3224`: 첫 거위 구매(step≥216)의 shop/가격을 보고 기존 거위 주문·축사·운반을 양 또는 소로 치환한다. | `V9_HERD_*` **상수** 0.5–1시간; 예외·후속 판매까지 바꾸면 **모듈** 2–4시간. | **중간**: 기존 거위 묶음의 종과 생산품. 거위를 더 키우는 손잡이가 아니라 거위를 줄이는 경로이고, 뒤의 HD2가 남은 거위 주문을 다시 평가한다. |
| 가축: **거위→양·소** HD2 | `main.py:5243-5260,5367-5435,5487-5520`: 남은 거위 구매에서 현금·예상가치·비율을 비교해 COW/SHEEP으로 바꾸고 건물·운반·판매도 맞춘다. | `_HD2_RATIO`, `_HD2_MIN_GAIN`, `_HD2_OPTIONS` **상수** 0.5–1시간; 가치모델·action rewrite **모듈** 3–5시간. | **중간**: 거위 구매가 있는 판만. 소·양 증가와 EGG 감소가 같이 일어난다; V9보다 뒤에서 작동한다. |
| 가축: **추가 양 6마리** | `main.py:1954-2019,4329-4373,4393-4413`: V233/VE가 YARN_STORE·가격·현금·구획 조건을 만족하면 day 11 또는 12 SE 땅, SHEEP 6, WHEAT 사료 6, 매일 일꾼 2를 추가한다. 마지막 day 29는 0 또는 1명으로 줄인다. | 가격·일자·수량·예산 조건 **모듈** 2–4시간; 6마리/일꾼 수를 재설계하면 작업 경로까지 **모듈** 5–8시간. | **매우 넓음**: 구획·가축·사료·매일 고용·양모 판매. “6”만 고치면 일꾼 대상 타일·용량·예산이 어긋난다. |
| 땅: **기본 매입 시점** | `main.py:947-949`: 모든 41 route에 `BUY_LAND` step 150(day 6 hour 6), 265(day 11 hour 1). `main.py:961-980`의 route 전환은 day 6과 day 27에 발생한다. | 기존 buy 한 줄 이동은 **route 편집** 2–4시간; Fritz식 day 6·8과 재배 면적 활용은 route·일꾼 일정 **재설계** 8–16시간. | **매우 넓음**: 토지 가용성, 파종·동물 배치, 자금 순서에 영향. route 번호 교체만으로 시점은 바뀌지 않는다. V219 day 18·V233 day 11의 조건부 SE 매입은 위 행의 별도 경로다. |
| 고용: **기본 route 일손** | `main.py:406-910,947-949`: route별 `HIRE` 계획 260–282회/에피소드(동일 날짜 내 반복 포함), chassis가 tape와 현재 손 수를 맞춘다. | route의 HIRE 및 hand index **편집** 4–8시간/하루 일정; 전체 인력 곡선은 8–16시간. | **매우 넓음**: 손 번호가 바뀌면 뒤의 PLANT/CARE/HARVEST/운반 모두 영향. 단일 HIRE 삽입은 안전한 독립 상수가 아니다. |
| 고용: **반응형 전용 일손** | `main.py:1317-1353` 토마토 1–3명, `main.py:1994-2019` 양 2명, `main.py:2152-2153,2240-2284` 밀·당근 비료 최대 2명, `main.py:2372-2400` 토마토 노동 배정. | 해당 **모듈**의 고용 조건/작업 경로 편집. 단순 상한 0.5–1시간, 작업량·동선 3–6시간. | **중간~넓음**: 해당 투자 활성 판의 추가 시장 주문과 이후 hand index. 여러 모듈이 같은 날 고용을 조율하므로 통합 확인 필요. |
| route **선택 방식** | `main.py:949,956-980`: 첫 두 shop으로 EXP240 또는 V39 선택, YARN 포함 조합은 V92가 route 9로 덮고 특정 공개 rival key는 route 128, day 27부터 route 2 강제. `_IMPL=make_agent(...)`는 `main.py:986`. | `_R108_SHOP_ROUTES`/`_R110_OLD_SHOPS`/`_V92_TABLE`/`_V93_ROUTE_BY_RIVAL` **선택표·router 편집** 1–2시간; 새 관측 특징/정책 전환은 3–6시간. | **넓음**: day 6 이후 선택 route의 동물·밀/당근·고용·시장 일정. 그러나 41 route가 같은 멜론·딸기·기본 땅 일정이고 day 27부터 route 2라 그 축은 이 손잡이로 바뀌지 않는다. |

**가장 빨리 바꿀 수 있는 세 손잡이** (코드 변경+짧은 정합성 확인 기준, 효능 순위 아님):

1. `_ALT_MODE` (`main.py:6473,6503-6517`) — **0.5–1시간**, 첫 소 1마리↔토마토 1그루와 opening 밀 거래 변경. 조기 opening 변화를 검증할 때.
2. `_CA_MARGIN`/날짜·feed reserve (`main.py:4473-4480,4647-4676`) — **0.5–1시간**, 조건부 밀↔당근 전환. c26 계열의 단순 margin 재튜닝은 이미 탐색된 방향이므로 survey가 작물 부족과 시점을 구체적으로 지목할 때만 새 가설로 쓸 것.
3. 기존 route의 shop 매핑 (`main.py:949,956-980`) — **1–2시간**, 이미 준비된 밀·당근·동물·고용 구성 사이 전환. 딸기·멜론·땅 시점은 못 바꾸므로 조사 결과가 그 축이면 tape 재설계로 직행.

**검증:** 읽기 전용으로 `ast`에서 `_R108_DATA`의 base85/zlib를 풀어 41개 route의 `PLANT`·`BUY_ANIMAL`·`BUY_LAND`·`HIRE` 계획을 집계하고, 위 코드와 두 참고 보고서를 대조했다. 실제 `agent(obs)` 행동 diff, 경기, hosted 성능은 **N/A**. 상위 300 결과(`analysis/survey300_20260929/`)가 완성되면 품목·시점·노동 병목을 먼저 분리한 뒤 이 표의 해당 행에서 구현 범위를 정할 것. holdout은 그때까지 계속 봉인한다.


---

## `reports/codex/20260929-1120-CALIB.md`

VERDICT | **로컬 평가로는 d157 대체 판단 불가.** c26의 표시 점수 1930 부근이 실제 균형이라는 증거도 없고, 로컬 우위가 hosted 우위로 보정됐다는 증거도 없다. 17시간 hosted 원자료는 c26이 최근에도 이겼음을 보이지만 두 제출은 서로 다른 상대를 만났다. | `experiments/calib/calibration.json` | `python3 experiments/calib/analyze.py` | NEXT: 현재 d157+c26 유지, 후보의 fresh panel은 탐색·위험 축소에만 사용.

1. **무엇을 시험했나:** [LOCAL+HOSTED] c26·d157 및 이전 제출 4개의 로컬 점수와 공개 hosted 기록을 대조했다. 게임을 새로 실행하지 않았다.
2. **왜:** 다음 제출이 d157을 은퇴시킨다(`coordination/BOARD.md:5-17`). c26의 작은 로컬 우위가 실제 승률 우위인지 먼저 판단해야 한다.
3. **측정 결과:** [HOSTED] 09-29 02:13 UTC까지 c26 119경기 90/3/26, d157 228경기 105/10/113. [LOCAL] 현재 상대 tape의 c26−d157은 +0.02974, 단순 페어 SE 0.01909, 정규근사 95% 구간 [−0.00767,+0.06715]. 수치 재현은 아래 명령과 입력 SHA에 있다.
4. **막힘·다음 행동:** [INFERENCE] 상대 submission별 당시 rating·σ와 이 대회의 정확한 표시식·갱신식이 공개 자료에 없다. 같은 상대 submission을 만난 경우도 0개다. 따라서 균형 rating과 로컬→hosted 보정식을 추정하지 않는다.

## 버전별 대조표

`W/D/L`은 해당 제출 자신의 공개 hosted 경기이며, 행 사이에서 상대·시각이 달라 직접 순위가 아니다. 로컬 수치는 같은 행에 적은 특정 panel에만 유효하다. `N/A`는 비교 가능한 자료가 없다는 뜻이다.

| 제출 (ID) | 같은 로컬 panel에서의 위치 `[LOCAL]` | hosted 기록·표시 점수 snapshot `[HOSTED]` | 판독 |
|---|---|---|---|
| DP0924 (56518910) | 네 panel 공통 비교 N/A | 18경기 17/0/1 뒤 27h 점수 2191.6 (`evidence/HOSTED_LEDGER.md:372-374`) | 초기 고승률은 수렴 증거가 아님 |
| 127ed3e6 exact (56549720) | EXP-039에서 d157·c26이 이 파일 상대 각 0.88; 필드 상대 비교 N/A (`experiments/exp039_camargin/summary.json`, 아래 재현 명령) | 27경기 22/0/5; 제출 직후 점수 2165.6 (`evidence/HOSTED_LEDGER.md:378-379`) | 초기 snapshot만 존재 |
| v171 (56567563) | EXP-033 tape 0.4614 < v074 0.5043 < d157 0.7943 (`experiments/calib/calibration.json`, EXP-033 항목) | 101경기 53/13/35, 약 2323 (`coordination/reports/antigravity/20260926-2045-EXP025-V171-HOSTED.md:6-10`); 이후 187경기 80/17/90 (`coordination/reports/antigravity/20260927-1650-EXP031.md:3-8`) | d157보다 낮은 로컬 위치가 hosted에서 확증되지 않음 |
| v074 (56577440) | EXP-033 0.5043; EXP-041 top2400 0.3181 (`experiments/calib/calibration.json`, EXP-033; `experiments/exp041_top2400/games42-*.jsonl`) | 238경기 101/4/133 (`coordination/reports/antigravity/20260928-1247-EXP037.md:3-7`); 09-28 점수 2160.8 (`coordination/proposals/claude/20260928-HYPGEN2-CODEX.md:4`) | EXP-033의 v074>v171 순서와 점수 snapshot은 반대이나 같은 시각·상대가 아님 |
| d157 (56607884) | EXP-033 0.7943; EXP-041 0.4158; EXP-051 0.6059; EXP-039 family 기준 0 (`experiments/calib/calibration.json`) | 136경기 때 2345.7 (`evidence/HOSTED_LEDGER.md:380`) → 219경기 때 2215.9 (`analysis/hosted_20260929pm/lb_scores.txt`); 17h 집계 228경기 105/10/113 | 같은 바이트의 표시 점수가 이후 하락 |
| c26 (56635330) | EXP-041 0.4488; EXP-051 0.6357; EXP-039 family d157 대비 +0.104이나 U tape는 −0.0037로 **동결 판정 FAIL** (`experiments/exp039_camargin/summary.json`) | 82경기 시점 1887 (`coordination/reports/claude/20260929-EXP050-051-LOSS-ANALYSIS.md:8-11`) → 112경기 시점 1920.6 (`analysis/hosted_20260929pm/lb_scores.txt`); 17h 집계 119경기 90/3/26 | 한때 상승은 확인; 1930 균형·d157 추월은 미확인 |

## 공식 rating 방식과 c26 판정

- [OFFICIAL] 이 대회 [Evaluation](https://www.kaggle.com/competitions/kaggriculture/overview/evaluation)은 새 유효 제출을 **default rating**으로 시작하고, 비슷한 rating의 봇끼리 대전하며, 승패·무승부와 상대 rating 차이로 skill rating을 갱신한다고 설명한다. 코인 격차는 갱신에 쓰지 않으며, 새 제출이 더 자주 경기하고 최종은 별도 Bradley-Terry 평가다(`docs/official/evaluation.md:1-16`). [N/A] 이 대회 문서에는 default의 **숫자**, 표시 점수가 `μ`인지 `μ−kσ`인지, 초기 `σ`, 정확한 update 식이 없다. [Kaggle 일반 대회 안내](https://www.kaggle.com/docs/competitions)는 Gaussian `μ,σ`를 설명하지만 이 대회의 표시식을 확정하지 않는다. 다른 대회의 `μ₀=600`을 이 대회 상수로 전용하지 않는다.
- [HOSTED] 17시간 자료의 c26 **최근 30경기 21/2/7, 승점률 0.7333**, 처음 39경기 36/0/3, 마지막 40경기 27/2/11. 같은 시기 d157 최근 30경기는 6/2/22, 승점률 0.2333이다. PM snapshot 이후 새 경기는 c26 5/1/1, d157 2/0/7. 이는 원자료 `analysis/hosted_20260929b/episodes_all.json`에서 시간순으로 재집계했다(`experiments/calib/analyze.py:42-128`, `calibration.json`의 `hosted`·`new_since_pm`).
- [HOSTED] c26과 d157이 만난 상대 submission ID의 교집합은 **0**이다. 최근 30경기의 **상대 팀** LB 점수 중앙값은 각각 1942.7, 2259.0이다. 팀 LB는 그 팀의 **최고 제출** 점수이고 해당 경기 상대 submission 점수가 아니다(`analysis/hosted_20260929b/step1_2_collect.py:119-151`). DP0924 때 팀 LB proxy로 2450~2550을 예측했다가 실제 2191.6이어서 오류가 확인됐다(`evidence/HOSTED_LEDGER.md:373-376`). 이번 원자료에는 `op_submissionId`는 있지만 그 submission의 당시 rating/σ는 없다. 상대 강도를 제출 단위 숫자로 보정할 수 없다.
- [INFERENCE] c26의 82→112경기 표시 점수는 1887→1920.6으로 +33.6이었다. 마지막 7경기도 5/1/1이다. **수렴 지연과 대진 차이는 현재의 낮은 표시 점수를 설명할 수 있다.** 그러나 112경기 이후 표시 점수 snapshot은 이 자료에 없고, 최근 높은 승점률은 실제 약한 상대를 계속 만났어도 가능하다. 따라서 “아직 오르는 중”은 112경기까지 관측, 119경기 이후는 `UNSURE`; “1930 균형”도 `UNSURE`다.

## 로컬 평가의 예측력과 대체 기준

- [LOCAL] EXP-033 같은 350 tape에서 d157−v074 +0.290, d157−v171 +0.333이다. 이 큰 방향은 d157의 초기 hosted 강세와 양립한다. 하지만 v074−v171 로컬 순서와 두 제출의 서로 다른 시점 표시 점수는 반대다. 동시기에 동일 상대를 대상으로 한 hosted paired 실험이 없어 어느 쪽이 참 순서인지 확정할 수 없다.
- [LOCAL] c26−d157은 EXP-041 상위 2400+ tape 742페어에서 +0.03302(단순 페어 SE 0.00847), EXP-051 현 상대 269 tape에서 +0.02974(SE 0.01909)다. 각각 701/742, 238/269페어는 결과가 동일했다. EXP-039 family closed-loop는 +0.104였지만 기존 U tape는 −0.0037이라 당시 고정 `judge39.py`의 `tapeU>=0` 게이트에 실패했다(`experiments/exp039_camargin/judge39.py:1-5,44-64`). 양의 tape 수치와 현재 표시 점수 차이를 “평가기 오류” 또는 “rating 지연” 한 쪽으로 귀속할 수 없다. EXP-041은 같은 상위 팀의 tape를 반복 사용한 open-loop라 단순 페어 SE는 팀 간 독립성을 보장하지 않는다.
- **현재 유일하게 근거 있는 결론:** [INFERENCE] 로컬 평가로는 d157 대체 판단 불가. 여섯 버전의 서로 다른 시점 hosted snapshot은 로컬 지표의 순위 적중률을 추정할 비교쌍을 제공하지 않는다. `+0.03`, `+0.104` 또는 임의 rating 점수를 제출 허가 임계로 쓰지 않는다.
- **최소 필요 조건 제안(통과해도 제출 충분조건 아님):** [HYPOTHESIS] 후보 SHA·panel·상대 submission/팀·판정식을 **결과 전에 동결**한다. 현 상대의 시간 분리 fresh tape에서 후보−d157, 후보−c26을 **각각** 페어 집계하고, 각 차이의 **상대 submission 또는 팀 단위 bootstrap 95% 하한 > 0**; 별개 fresh 2400+ tape와 양 좌석 family closed-loop 각각에서 두 기준선 대비 점 추정 **≥0**; invalid/error 0, 실제 행동 변화 확인, 런타임·릴리스 게이트 PASS. 한 panel이라도 미측정/실패면 `BLOCKED/NO_SUBMIT`이다. 이 0 경계는 우위·비열등의 정의이지 hosted 예측력으로 검증된 효과 크기가 아니다. 현 BOARD의 “모든 panel에서 max(d157,c26) 이상” 결정(`coordination/BOARD.md:12-17`)과 결합한 **보수적 screen**이다. d157 은퇴의 충분한 실증 근거가 필요하면 현재 두 슬롯 구조에서는 새 후보의 hosted 성능을 사전 관측할 수 없어 사람의 별도 위험 결정이 필요하다.

## 재현·경계

`python3 experiments/calib/analyze.py` → 위 5개 로컬 페어·hosted 시간 절단·상대 submission 교집합. 스크립트 SHA-256 `6152a50fdad88c5cc3c701f81c91bc6d5bb1b9e3f0eb766fb5dc3856b2bc6297`, 출력 `experiments/calib/calibration.json` SHA-256 `5d9b24770286a42bbd0a29df9835a7af2a1ff7b104c65bb0aec57b85bddf725a`. 입력 SHA-256은 같은 JSON의 `input_sha256`에 **전체** 저장. 주요 입력: hosted-b `ce4b9203deed23cb0a9dc3add50dbd06a8536aeeb2ec9118b49589e9600a8efc`; PM `b0d18a7c2b4cd1f054a033df3c35265ed9e1f101f1b98b0d751aeccde1edf983`; EXP-051 `c4ae8c771039d92eb1c421d54e0ed8bdd96555c49032bd9e105033778f8e3813`; EXP-039 summary `a0c83b7abab5e0bfefc93c241bed42d39a380dbf801a32f735f685efec271255`. 로컬 엔진 잠금은 `environment/ENGINE_LOCK.md`, 행별 seed·좌석·상대는 각 `games*.jsonl`/`meta.json`에 보존했다. `analysis/hosted_20260929b/step3.log`의 검증은 347/347 replay, missing 0, mismatch 0이었다. 이 작업은 별도 게임·seed 9000–9599·제출·엔진/RNG 변경 없이 기존 raw 행만 읽었다.

가설 원장: `python3 tools/update_hypotheses.py --agent codex --hypothesis-id HYP-0012 --test-id TEST-CALIB-20260929 ...` → immutable event `coordination/hypotheses/codex/EVT-2026-09-29T022103.706986+0000-316bca54.json`; `python3 tools/validate_hypotheses.py --strict` → `PASS: 38 entries`. `python3 -m py_compile experiments/calib/analyze.py` → exit 0.

`CALIB-20260929` | 결정적 제한: 상대 submission rating·표시식 N/A, hosted 동일 상대 ID 0/두 제출 | 재현: `python3 experiments/calib/analyze.py` | NEXT ACTION: d157+c26 유지; 향후 후보는 위 사전등록 screen을 통과해도 human release decision 이전에 hosted 우위라고 부르지 않는다.


---

## `reports/codex/20260929-1408-FP-PUBLIC-SIGNAL.md`

VERDICT | [LOCAL] 비공개 55be 변형 패배를 설명할 **반복 가능한 조기 공개 신호/원인을 확인하지 못함**. 후반 자금 열세는 강한 경고지만 원인 또는 실행 가능한 개입은 아니다. 후보·release·제출 N/A.

1. 무엇을 시험했나: d157 실전에서 공개 55be와 행동이 달랐던 상대 43경기만 골라, 고정 step 240/384/480/576/624의 공개 관측 6항목이 패배를 반복적으로 구분하는지 확인했다.
2. 왜: 비공개 변형의 코드는 볼 수 없지만 상대 자금·농장·공유 시장은 매 턴 볼 수 있다. 패배 전에 보이는 신호가 있어야 반응형 전략을 만들 수 있다.
3. 측정 결과: 25패/18승, 상대 submission 42개. 사전 고정 30검사 중 통과 0개(각 시기·양쪽 상태 표본 조건을 충족한 검사 1개). step 576 상대 자금 우위는 21패/1승, 비우위는 4패/17승이나 이미 576/719 호출 시점이고 손실의 원인을 말하지 않는다. 현금흐름에서 상대가 가장 크게 앞선 품목은 딸기 6/25, 비료 5, 우유 4, 밀 4, 당근 3, 양털 3으로 분산됐다.
4. 막힘/다음: step 480 공유 STRAWBERRY 재고 >10000은 11패/2승 대 14패/16승(두 시간 절반의 위험차 +0.3625/+0.375)이나 pooled Fisher p=0.041 > 사전 기준 0.01, 각 절반 feature=true 승리 1건이라 근거 부족. 독립 자료에서 이 조건을 확인하고 실제 가격/판매 행동의 인과를 검증하기 전에는 후보를 만들지 않는다.

## 범위와 재현

- 사전 분석안 [PLAN.md](~/kaggle/Kaggriculture/experiments/fp_signal/PLAN.md) SHA-256 `ea3a457031ac0374489054376cb168f8157084027d4cc92f19e275e37be0659e`; feature를 읽기 전에 `freeze.py`로 동결한 [cohort.json](~/kaggle/Kaggriculture/experiments/fp_signal/cohort.json) SHA-256 `f6af6ad57b4858173531b7de9878a1664760eafe9f1b633b09f67fd2512dd999`. FP 기존 holdout 55 episode ID, EXP-051 이후 새 hosted episode를 cohort에서 제외. 43 raw SHA 목록 `experiments/fp_signal/raw_sha256.json` SHA-256 `e08bf1e365de2e4e6d4d237f57225e74ae9d113d3d1fe523ef76135139b7e6d9`.
- [audit.py](~/kaggle/Kaggriculture/experiments/fp_signal/audit.py)는 각 replay의 `observation`에서 `farms`, `market`, `town`, `step`만 읽는다. seat1 기록에서 빠진 공개 `step`은 seat0 공용 관측으로 보완했다. `private`나 상대 action을 feature에 쓰지 않았다. 재현 `python3 experiments/fp_signal/audit.py`; 결과 [verdict.json](~/kaggle/Kaggriculture/experiments/fp_signal/verdict.json) SHA-256 `ffacd2c8d9152abe740451f02a64e027d84ee50512aced134b1f93e44f4b1882`.
- 후행 진단 `python3 experiments/fp_signal/posthoc_cashflow.py`: 기존 engine replay 현금흐름 43/43 최종 reward parity. [posthoc_cashflow.json](~/kaggle/Kaggriculture/experiments/fp_signal/posthoc_cashflow.json) SHA-256 `2d7cdd4795fb1fa0f29d726bb197ad6d040e1796a7cc8635c51d130ff7b0686c`. 첫 실질 행동 차이 중앙 step은 패배 266, 승리 350(승리 18건 중 1건은 fingerprint 차이만 있고 material action 차이 없음). 첫 차이 유형은 패배 market 변경 14, 순서 변경 9, unit만 2. 품목별 현금 차이는 outcome으로 조건화했으므로 인과 귀속이 아니다.
- late warning의 정확한 표: step 576 상대 자금 우위 `L21/W1`, 그렇지 않음 `L4/W17`, Fisher p=`2.30645e-7`. 사전 gate는 각 시간 절반과 각 feature 상태에 승/패 최소 3건을 요구해 이 항목도 FAIL(`verdict.json`). 자금은 시장 매도와 구매의 결과값이어서 전략 원인으로 쓰지 않는다.

## 보존/제약

- **holdout 노출 사고:** 진단 중 `analysis/exp050_divergence/cash50.jsonl` 첫 3행을 화면에 출력했고, 이 3건(`114800913`, `114774446`, `114734127`)이 FP 기존 holdout임을 나중에 확인했다. `events50b/events50`에서는 그중 `114774446`·`114734127`의 일부 이벤트도 보였다. 원본 raw replay를 이 셋에 대해 열지는 않았고 이 감사의 43건 feature/cashflow 집계에도 넣지 않았지만, FP holdout을 향후 완전 미열람으로 주장할 수 없다. `posthoc_cashflow.py`는 선택된 43 ID만 JSON 파싱하도록 수정했다. 향후 후보에는 새로 동결한 별도 holdout이 필요하다.
- 공개 상태 경고와 비공개 변형의 **인과적 패배 원인**은 구분한다. 현재 자료로 확인된 조기 인과 원인은 `N/A`; `NO_REPEATED_SIGNAL`은 정해 둔 6특징×5시점 검사의 판정일 뿐 모든 가능한 신호의 부재 증명이 아니다.

NEXT ACTION | 이 분석으로는 후보 구현을 시작하지 않는다. 코디네이터가 새 카드에서 독립 자료와 하나의 기제를 먼저 고정해야 한다. 그 전에는 d157+c26 유지, 기존 seed 9000–9599와 holdout 5팀 미사용.

가설 원장: `HYP-0039 / TEST-FP-PUBLIC-SIGNAL-20260929`, 상태 `INCONCLUSIVE` (tool-managed event로 기록). 종료 검증: `python3 tools/validate_hypotheses.py --strict`.


---

## `reports/codex/20260929-1520-SURVEY300.md`

# SURVEY300 독립 전수조사 — 2026-09-29 15:20 KST

**VERDICT | 조사 완료, 생산 구성만으로 바로 옮길 단일 손잡이는 없음.** `[LOCAL]` 재생 파일이 있는 고유 2,572경기의 작물·가축·땅·고용을 읽었다. 상위권은 토마토·당근이 많고 딸기·후반 밀이 적지만, **수집 대상 상위권과 비교군이 실제로 직접 맞붙은 경기는 7판뿐**이며 상위권 3승이다. 거위의 팀 간 차이는 넓힌 경기 내 비교에서 사라지고, 밀 매출 차이는 매입비를 빼면 역전된다. A·B 판정과 holdout 봉인은 유지한다. bot 변경·새 경기·제출은 **N/A**.

## 무엇을 왜 측정했는가

- `[LOCAL]` 데이터 도착 전 계획 `analysis/survey300_20260929/PLAN.md:1-16`에 따라 step 288·576의 작물 5종과 가축 3종, 땅 세 번의 매입 day, 관측된 누적 고용을 경기·좌석별로 만들었다. 16개 시점별 수량 + 땅 3개 + 고용 1개로 실제 검사 열은 **20개**다. 계획의 “18개” 표기는 산술상 맞지 않는다. 판매·구매 체결은 기존 parity 검증된 부분 추출본으로 별도 계산했다.
- `[INFERENCE]` 목적은 상위 팀의 구성을 d157에 복사하는 것이 아니라, 같은 경기의 승자·패자와 투자 비용을 함께 보아 사전등록할 구조 실험의 근거를 고르는 것이다. 상관은 개입 효과가 아니다.

## 표본·검증·계열

| 항목 | 결과 |
|---|---:|
| 수집 메타 행 / 고유 경기 / 원본 재생 가능 | 2,840 / 2,771 / **2,572** |
| 재생 불가 | 199, 모두 비교군 대상 경기 |
| 승자−패자 경기 | 2,539 (나머지 33 무승부) |
| 순위표 기준 상위300−비교군이 같은 경기에 나온 경우 | 158, 상위300 105승; 대상 외 상대도 포함 |
| **사전 수집 대상** 상위300−비교군끼리 직접 만난 경우 | **7, 상위300 3승** |
| 실제 원본이 있는 수집 대상 팀 | 상위 235팀 / 비교군 98팀 |
| 체결 원장 `feat300.jsonl` | 1,865경기, 직접 순위 대조 147경기; 경기 ID 순서로 앞부분이어서 오래된 경기 편향 |

`[LOCAL]` `python3 experiments/fp_survey300/validate.py`는 메타 reward 불일치 0, 체결 원장과 우리 관측의 reward 불일치 0, step 288·576 작물·가축 snapshot 불일치 0을 확인했다. 기존 체결 원장 1,865건은 모두 replay parity가 참이다(`analysis/survey300_20260929/feat300.py:25-41`). 결측 199건은 비교군에만 몰려 있어 무작위 결측으로 취급하지 않았다. 대상 submission과 현재 순위표를 만든 submission이 다를 수도 있다(`analysis/survey300_20260929/PLAN.md:10-12`).

`[LOCAL]` 땅을 끝까지 사지 않은 경우 매입 day를 30으로 기록했다(`experiments/fp_survey300/analyze.py:29-35`). 첫 매입 누락은 0/5,144좌석, 둘째 매입 누락은 2/5,144좌석이지만 셋째는 4,050/5,144좌석이다. 따라서 셋째 땅 day의 평균 차이는 사실상 “샀는가”가 섞인 값이며 시점 효과로 해석하지 않는다.

`[LOCAL]` 공개 55be exact와 **팀당 원본 1경기**의 행동을 비교했다. 대상 333팀 중 이름 변경으로 확인이 어긋난 1팀을 제외한 332팀에서 재실행 예외는 0이다. 상위 234팀 전원이 계획의 “첫 이탈 <600”이고, 그중 186팀은 step 0부터 다르다. 비교군 98팀은 이른 이탈 91, 늦은 이탈(≥600) 1, 전 구간 동일 6이다. **상위권에 같은 계열(≥600) 표본이 0**이므로 계획의 “같은 계열 내 차이” 열은 `N/A`; 임계 600을 결과를 보고 낮추지 않았다. 이 판별은 계열의 정확한 유전 관계가 아니라 관측 행동 fingerprint다.

## 생산 구성 차이

`[LOCAL]` 아래 Δ는 **좌측−우측**이다. 승패 열은 2,539경기 승자−패자, 순위 직접 열은 158경기 상위300−600~1300위(수집 대상 외 상대 포함), 대상 직접 열은 7경기 사전 수집 대상끼리 상위−비교군, 팀 평균 열은 수집 대상 235팀−98팀의 팀 평균이다. 마지막 열은 팀 단위 bootstrap 분산의 정규 근사 p값에 BH-FDR 0.1을 적용한 탐색 표식이며 인과 판정이 아니다. 전체 95% 구간은 `summary.json`에 있다.

| 특징 | 승자−패자 | 순위 직접 | 대상 직접 | 대상 팀 평균 | BH 0.1 |
|---|---:|---:|---:|---:|:---:|
| TOMATO @288 | +0.39 | +0.77 | 0.00 | +0.96 | Y |
| STRAWBERRY @288 | −1.13 | −1.19 | +0.14 | −4.00 | Y |
| CARROT @288 | +0.15 | +0.33 | 0.00 | +0.60 | Y |
| WHEAT @288 | +1.04 | +0.24 | 0.00 | +2.60 | Y |
| MELON @288 | +0.35 | +0.83 | 0.00 | +1.38 | Y |
| COW @288 | +0.08 | +0.41 | −0.14 | +0.20 | Y |
| SHEEP @288 | −0.11 | −0.14 | +0.14 | −0.73 | Y |
| GOOSE @288 | +0.43 | −0.03 | 0.00 | +1.10 | Y |
| TOMATO @576 | +0.85 | +2.41 | 0.00 | +2.33 | Y |
| STRAWBERRY @576 | −1.36 | −1.42 | +0.14 | −3.87 | Y |
| CARROT @576 | +0.62 | +1.34 | −2.29 | +2.25 | Y |
| WHEAT @576 | −0.38 | −2.39 | +2.29 | −2.37 | Y |
| MELON @576 | +0.11 | +0.21 | 0.00 | +0.42 | Y |
| COW @576 | +0.06 | +0.38 | −0.14 | +0.04 | N |
| SHEEP @576 | −0.10 | −0.08 | +0.14 | −0.68 | Y |
| GOOSE @576 | +0.43 | −0.10 | 0.00 | +1.15 | Y |
| 첫 땅 매입 day | +0.01 | −0.03 | 0.00 | +0.01 | N |
| 둘째 땅 매입 day | −0.36 | −0.35 | 0.00 | −0.92 | Y |
| 셋째 땅 매입 day | −0.47 | −0.66 | 0.00 | +0.37 | N |
| 누적 고용 수(관측) | +1.94 | +1.48 | +1.57 | +2.97 | Y |

`[LOCAL]` 주요 팀 평균 Δ와 95% 구간: TOMATO@576 **+2.33 [1.80, 2.90]**, STRAWBERRY@576 **−3.87 [−4.52, −3.28]**, CARROT@576 **+2.25 [1.42, 3.10]**, WHEAT@576 **−2.37 [−3.26, −1.48]**, GOOSE@576 **+1.15 [0.87, 1.43]**, 둘째 땅 매입 day **−0.92 [−1.07, −0.78]**. 반면 순위 직접 158경기의 GOOSE@576은 **−0.10 [−0.43, +0.23]**이고, 대상 직접 7경기의 TOMATO·GOOSE·땅 시점 Δ는 모두 0이었다. 순위 직접 구간은 경기 단위 bootstrap으로 반복 팀의 상관을 완전히 제거하지 못한다.

`[INFERENCE]` 구성 snapshot이 step 288·576 모두 같은 순위 직접 경기 28판에서도 상위 팀이 18판 이겼다. 작은 조건부 표본이며, 생산 수량만으로 모든 승패를 설명할 수 없다는 진단이다. 체결·현금 흐름·작업 순서 등은 따로 본다.

## 실제 체결과 노동비: 같은 경기 147판, 부분 추출본

`[LOCAL]` 기존 exact replay 계측 `analysis/survey300_20260929/feat300.jsonl`의 parity 참 1,865판 중 순위 직접 147판만 썼다. 단위는 **상위−비교군의 경기당 평균 코인**이다. 비용을 품목에 완전히 배분한 순이익이 아니라 기록된 체결 현금흐름이다.

| 항목 | 판매 체결액 Δ | 매입액 Δ | 종자액 Δ | 판매−매입−종자 Δ |
|---|---:|---:|---:|---:|
| TOMATO | +1,895 | 0 | +181 | +1,714 |
| STRAWBERRY | +390 | 0 | −67 | +457 |
| WHEAT | +16,414 | +16,864 | −35 | **−414** |
| EGG | +72 | 0 | 0 | +72 (거위 구매·사료 제외) |
| 전체 HIRE 비용 | — | **+234** | — | 품목 배분 불가 |

`[INFERENCE]` 큰 밀 매출은 거의 같은 규모의 밀 매입을 동반했다. 토마토의 +1,714는 추가 일꾼·땅·딸기 기회비용·가격 영향 전의 수치이고, 중앙값은 0이다. 딸기 칸 수가 적어도 딸기 판매액은 +390이므로 “딸기를 토마토로 바꾸면 딸기 손실이 작다”는 결론은 성립하지 않는다. 이는 딸기 실매출을 놓쳐 실패한 EXP-055와 맞는다(`coordination/reports/claude/20260929-EXP055-FRITZ11.md:1-5`; `experiments/fp_survey300/flows.json`). 거위 확대 EXP-057의 세 변형은 모두 d157보다 낮았으므로 관측된 거위 수 차이를 재시험 근거로 단독 사용하지 않는다(`coordination/reports/claude/20260929-1330-EXP056-057-VERDICT.md:14-23`).

## 다음 설계 입력 — 후보 bot은 아직 없음

1. **작물 일정 전체**: TOMATO@576 +2.33, CARROT +2.25, WHEAT −2.37과 STRAWBERRY −3.87을 한 투자 일정의 징후로 본다. d157의 `_CXTB_MIN_REVENUE` 문턱만 낮춘 EXP-054와 day11 딸기→토마토 EXP-055가 실패했으므로 단일 상수·단일 파종 치환은 다시 하지 않는다. 검토하려면 route의 씨앗·파종·수확·판매·딸기 체결 수익·일손을 함께 계산한다. 구현 지점 `coordination/reports/codex/20260929-1005-KNOBS.md:11-19`.
2. **둘째 땅 매입과 사용 일정**: 상위 팀은 대상 평균 0.92일, 넓힌 같은 경기 평균 0.35일 빠르다. 그러나 대상 직접 7판은 차이 0이며, d157 기본 route는 day11 매입(`coordination/reports/codex/20260929-1005-KNOBS.md:22`). 매입 시점만 앞당겨 빈 땅을 만드는 실험은 근거가 약하다. 추가 면적의 작물 수익−매입·일손·포기한 작업을 같은 경기에서 계산한 뒤 route 단위 개입을 사전등록한다.
3. **생산량보다 거래·작업 효율**: 밀 판매액 +16,414와 매입액 +16,864가 상쇄되고, 같은 생산 snapshot으로도 승패가 갈린다. d157의 밀→당근 전환은 V9/CA에 이미 있으므로 margin 상수 재튜닝보다 주문·노동 일정이 바뀌는지 먼저 계측한다(`coordination/reports/codex/20260929-1005-KNOBS.md:13-15`). 이는 구조 가설이며 이 조사로 효과를 증명하지 않았다.

**남은 위험 2개:** (1) 비교군 원본 199경기가 비무작위로 빠졌고 체결 원장은 앞부분 1,865경기만 있어, 후기 경기의 비용 차이는 `N/A`; (2) 상위권 동일 55be 계열 0팀·대상 직접 7판으로 계열 내 효과와 목표 2200–2400 변형 상대의 인과 이득은 `N/A`. 다음 후보는 별도 카드·고정 평가 기준·새 bot 승인 범위에서만 만들 수 있다.

## 재현·식별

- 선행 계획 SHA-256: `dea1b533c6fdad1b62fe807864787a90808f1d2e1f0cea4816d040541695c8c3`; 입력 `episodes_all.json` `e2572db216505754788cce70231c282e3586161009ccc5d4831b8305b6c0c4d3`, `targets.json` `da2568a54aaeb1e448a498bd22666abe7b25befe0fb43fe1927b79781e0b7e49`.
- `experiments/fp_survey300/snapshots.jsonl` SHA `fe270d1cc13805337dd3109266ab2a01d2c9694332768ca4e42763f67f831fa6`; `summary.json` SHA `69fab7ea6ea34a34208ab8dcd092d24917cca6b944ca7fb443af59d420636fd8`; `flows.json` SHA `902e0282c87b5b4839f37efa88574f405bdabe72420482173411b6e9da1139b6`; `lineage.jsonl` SHA `7a90a8304a5f308756e3d903417c98401abe12bbdd97fdcb5e50dede0e18468f`.
- 코드 SHA: `scan_replays.py` `d81f7f78f72182f3339322579416b01907d24df4bd6b562f415b9a3d213a19b1`; `analyze.py` `32e03aed128a22d526ba9deca3d77fe2604cb2e324e675ede1a6ef42fd17473c`; `flow_check.py` `2a49a056695f8166ee4b7c49c497f996a8e629a72ce03a665ad72d235a2ac61c`; `lineage_probe.py` `e4ed061ac38a1b1ca4fbfd16f13c9e6ca6a425c0a3d9a4a7171f296e720e8806`; `validate.py` `136698e4ce86bffb6f63aa09e3dada1aeee848e7c2f3d552f0780a07a4210d4c`.
- 체결 입력 `analysis/survey300_20260929/feat300.jsonl` SHA `707b17d131048069e8a7d8b92011c984bcf978dc985bea8b972388fd2d44bc38`; 55be 원본 `releases/public-dpnew-55be5d5f-exact/main.py` SHA `55be5d5f124c8daaaa63c1a29ba4aab096004909666f04748007603c67b7d2a8`.
- 재현: `python3 experiments/fp_survey300/validate.py`; `python3 experiments/fp_survey300/analyze.py`; `python3 experiments/fp_survey300/flow_check.py`. 원본 재생 판독 스크립트는 같은 폴더의 `scan_replays.py`, 공개 봇 fingerprint는 `lineage_probe.py`; 두 원본 처리 명령은 산출 JSONL이 이미 있어 재실행 시 완료 행을 건너뛴다. 기존 `feat300.py`의 엔진 hook 추출은 이번 작업에서 실행하지 않았다. 엔진·RNG 파일 수정, seed 9000–9599 실행, holdout 열람, bot 생성, 제출은 없었다.


---

## `reports/codex/20260929-1923-FP-CLOSE-LOSS.md`

# d157 근소 패배의 c26 행동 차이 점검 — 2026-09-29 19:23 KST

VERDICT | `[LOCAL]` 반복되는 실행 가능 신호는 아직 없음. c26이 d157의 근소 패배를 일부 뒤집지만 같은 당근 전환이 기존 승리도 잃게 한다. 후보·새 대전·제출 N/A. | 입력 SHA 아래 | 기존 EXP-051 결과 재집계 및 8경기 행동 재생 | NEXT: 독립 자료에서 결정 전 공개 신호와 구체 행동의 인과를 함께 고정하기 전에는 규칙을 만들지 않는다.

1. 무엇을 확인했나: 이미 동결된 `experiments/fp_signal/cohort.json`의 43경기만 읽었다. 이 집합은 기존 FP holdout과 이후 hosted 경기를 제외한다. d157 패배 중 최종 현금 차이 절댓값 300 이하를 근소 패배로 정의해 기존 `experiments/exp051_curpop/games.jsonl`의 d157·c26 재생 점수를 대조했다. 임계 300은 이번 **사후 진단용**이며 후보 선택 기준이 아니다.
2. 왜: 판매·작물 행동 하나를 켜서 근소 패배를 뒤집을 수 있는지, 동시에 이기던 경기를 잃는지 확인했다.
3. 결과: 43경기에서 d157 승점 18, c26 승점 21. d157의 근소 패배 18경기 중 c26은 6경기를 승리로 바꿨다. 전체 43경기에서는 d157의 패배 7경기를 승리로, 승리 4경기를 패배로 바꿨다. 이는 **고정 상대 행동의 open-loop 재생**이며 hosted 개선 증거가 아니다.
4. 행동 점검: 뒤집힌 4경기와 새로 진 4경기를 동일 seed·좌석의 tape 상대에 재생해 첫 다른 행동을 기록했다. 뒤집힌 `114358294`와 새로 진 `114418822`는 모두 step 150에서 c26만 `BUY_SEED CARROT 8`을 추가했다. 각 경기에서 이후 행동 차이는 각각 66, 88 step으로 퍼졌다. 다른 첫 차이도 당근 씨앗·밀→당근 파종 계열이었다. 같은 개입이 상반된 결과를 내므로 step 또는 당근 전환 자체는 승패를 가를 공개 신호가 아니다.

기존 `HYP-0039 / TEST-FP-PUBLIC-SIGNAL-20260929`는 공개 정보 6특징×5시점의 사전 고정 검사 30개 중 통과 0개였다(`coordination/reports/codex/20260929-1408-FP-PUBLIC-SIGNAL.md`). 따라서 이 자료에서 사후 조건을 만들지 않는다. 결정 전 신호 → 행동 한 개 → 새 표본의 c26·d157 비교라는 순서를 유지하되, 첫 관문인 신호·기제 연결은 `N/A`다. 새 후보나 holdout 개봉은 하지 않았다.

## 재현과 식별

- d157: `releases/exp035-d157/main.py` SHA-256 `94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e`.
- c26: `releases/exp039-c26/main.py` SHA-256 `ff230c8368ff35106e664be87b05faa67532e8857bcdeaaa33ada24a20c7edb6`.
- cohort: `experiments/fp_signal/cohort.json` SHA-256 `f6af6ad57b4858173531b7de9878a1664760eafe9f1b633b09f67fd2512dd999`.
- outcome rows: `experiments/exp051_curpop/games.jsonl` SHA-256 `c4ae8c771039d92eb1c421d54e0ed8bdd96555c49032bd9e105033778f8e3813`; `meta.json` SHA-256 `4745474b4590d95889fbc59823c858d772a6f6abac9ca81f3a114144cb1d9077`.
- hosted-source margin table: `analysis/c26_hosted_20260929/opponents.csv` SHA-256 `eb55dd417e8ac196b5ff182db2f9399f57be2334483132fe3d30541b98963dd4`.
- 재집계: cohort의 episode 집합 `E`; `games.jsonl`에서 `(vid, opponent='C'+episode)`로 대조. 근소 패배 집합 `L={e∈E: opponents.csv.result='L' and abs(margin)<=300}`. `|E|=43`, `|L|=18`, `sum(score[d157,E])=18`, `sum(score[c26,E])=21`, `sum(score[c26,L])=6`.
- 행동 재생: `kaggle_environments.make('kaggriculture', configuration={'episodeSteps':720,'seed':int(meta[e]['seed'])})`, `get_last_callable`로 d157/c26과 `experiments/exp051_curpop/tapes/C<episode>.py`를 각각 로드하고 원래 seat에 배치. 비교한 8 ID: 뒤집힌 `114492095,114512363,114358294,114245731`; 새로 진 `114229262,114439927,114326263,114418822`. 행동 리스트의 최초 불일치 step은 순서대로 `590,160,150,399` 및 `532,652,582,150`.

`[INFERENCE]` 이번 결과는 c26의 당근 전환이 패배와 승리 양쪽에 영향을 준다는 진단이다. 상대별 정책 전환의 예측력·closed-loop 성능·hosted rating 영향은 `N/A`다.
