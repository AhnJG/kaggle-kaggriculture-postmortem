# EXP-001 — v1 land expansion

hypothesis_id: HYP-0001
test_id: TEST-0001

상태: **사전등록** (실행 전 작성, 2026-09-07)

## 공통

- parent: `releases/v0/main.py`
- engine: `kaggle-environments==1.32.7`, `kaggriculture.py` sha256
  `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- hypothesis `[HYPOTHESIS]`: NW 25칸의 idle action budget을 NE+SW에 쓰면 v0보다 W/D/L이 개선된다.
- forbidden: SE($4,000) 구매, sell timing 변경, 동물/비료/신규 작물 도입, 결과 확인 후 seed 추가
- opponent: 단계별 variant 또는 고정 v0. 각 비교는 같은 seed와 양 좌석을 사용한다.
- pilot seed/seat: `1000..1019`, 20 seeds × both seats = 40 games/comparison
- promotion seed/seat: `configs/paired_seeds.txt`, 200 seeds × both seats = 400 games
- primary metric: paired score와 seed-level 95% CI
- diagnostics: W/D/L, mean/median margin, >10k loss, error, silent-failure counters,
  per-item realized SELL price
- expected failure plane: land/crew cost가 추가 산출보다 큼; 먼 구획 travel로 action budget 소진;
  empty unlocked tile weeds; carrot glut; market 10-slot truncation; seed-budget rewrite; shed overflow

## 고정 pilot 순서

각 단계의 wrapper와 공통 `main.py` SHA는 실행 전에 아래 표에 기록한다.

1. **land timing only**, hands=4, carrots=15/75:
   - early: NE day4, SW day8
   - observed-prior: NE day6, SW day10
   - late: NE day8, SW day12
   - 세 후보 round-robin. paired score 합이 가장 큰 timing을 선택한다.
2. **worker count only**, 선택 timing, carrots=15/75:
   - hands=9 / 10 / 12
   - 세 후보 round-robin. paired score 합이 가장 큰 count를 선택한다.
3. **crop allocation only**, 선택 timing+hands:
   - carrots=5 / 8 / 15칸, 나머지는 WHEAT
   - 세 후보 round-robin. paired score 합이 가장 큰 allocation을 선택한다.

단계 내 paired score 합이 같으면 (1) head-to-head, (2) big-loss가 적은 쪽,
(3) mean margin, (4) 비용이 낮은 쪽(later land / fewer hands / fewer carrots) 순서로 결정한다.
pilot은 후보 선택용 재사용 holdout이며 hosted 또는 promotion evidence가 아니다.

## 변경 요인과 단계별 판정

- stage 1: v0 대비 `BUY_LAND` 2회와 75-tile routing만 변경.
- stage 2: stage 1 대비 worker target만 변경.
- stage 3: stage 2 대비 WHEAT/CARROT allocation만 변경.
- 각 단계: error 또는 silent failure가 하나라도 있으면 해당 후보 FAIL.
- 각 단계: round-robin 우열이 없으면 위의 사전등록 tie-break로 선택하며 결과는 `불확정`으로 기록.

## 최종 승격 판정

- SUCCESS: silent-failure gate와 self-play gate가 CLEAN이고, v1 vs v0의 95% CI 하한 > 0.5.
- FAILURE: gate error/silent failure 발생 또는 95% CI 상한 < 0.5.
- UNCERTAIN: clean이지만 95% CI가 0.5를 포함.
- SUCCESS next action: exact artifact SHA와 registry를 기록하고 독립 검증 요청. hosted 우위는 주장하지 않는다.
- FAILURE next action: v0 유지. 실패를 land timing / worker / crop implementation 범위로 한정해 보고한다.
- UNCERTAIN next action: v0 유지. 같은 200 seeds에 재튜닝하지 않고 새 hypothesis를 별도 카드로 제안한다.

## Frozen artifact ledger

wrapper는 local experiment 전용이며 아래 공통 `main.py` SHA와 쌍으로 식별한다.

- common `main.py`: `344093a8b1bffb5ce181591a1a1397ad31e66dd9329d097c51232f1656c76f02`
- `v1_timing_early.py`: `d6b8c281a391712b2f482e459b56d8cff15c9e3afc4e9923674819826614fd09`
- `v1_timing_prior.py`: `b0a7e9b843871c295236c653dd304ae4488c1d54e6db985562b90d067745ed88`
- `v1_timing_late.py`: `78c07e31c5eb9825d1bf792a1ea36d941934cb18cc1702a375d4154ce8871ae4`
- `v1_workers_9.py`: `403d2c79f839a7e4db45f88949612cee4a83e79e62b07e5e1ddcf38d5c61bf6b`
- `v1_workers_10.py`: `2360a12772284e0c8a1e21e3e98aa4acba0f6f2463402e8fc0131e1c15d3f966`
- `v1_workers_12.py`: `1199892b35ce067f7741305ddff75aaa2f7878f367916b5c85510c6dfd38d2c5`
- `v1_carrots_5.py`: `f2d264034e740a10f18a34803877744bac84e729e72bd0d5f5e18134547f9c79`
- `v1_carrots_8.py`: `83c710ccd1527d9b1b3739d759c5294b909d9b6b24612bc6cbbf260a0fd47de6`
- `v1_carrots_15.py`: `22cfd7ef3248836d394d1f1f0f6cb3d83aa1cb63821a841d3fe39ba14af5efc6`

## 2026-09-07 pre-rerun amendment — concurrent overwrite

첫 timing/worker/crop 실행 중 다른 작업이 `main.py`를 common SHA `344093a8…76f02`에서
v0 SHA `eb64b3c…2af85`로 덮어썼다. wrapper가 매 episode live `main.py`를 읽었으므로 첫 실행의
9개 result JSON은 모두 **INVALID**이며 어떤 선택에도 사용하지 않는다. 첫 crop 실행에는 별도로
5/8/15 설정을 모두 15 tiles로 만든 placement bug도 있었다.

재실행에서는 exact-count placement를 사용하며 각 wrapper가 episode 시작 시 common SHA를 assert한다.
아래 SHA를 실행 전에 동결했고 seed/표본/판정 규칙은 원래 사전등록에서 바꾸지 않았다.

- common `main.py`: `b0c32e1a181e9308c05046b10d618258397c4088e21025ba78346aaa9ac25ddf`
- `v1_timing_early.py`: `124622f57bd7768fc77509331959d775a037e3da12b997d3ba24cc40808aa844`
- `v1_timing_prior.py`: `e4cf817909b85eec69ff117020ec936eaa6dbe6f61950aae31517a2031c0a127`
- `v1_timing_late.py`: `02114130f28d2ecf1bd0fa4c87070a0e55d2af070bae29d6f12aa804552e8282`
- `v1_workers_9.py`: `6533e846408a20b835f8a7653549d088b2b8b8b63dd08b59330d735de90c7cf7`
- `v1_workers_10.py`: `c8dcf2e242686b0c1e8cb0ecc6687dec6bc7cc483fd8941c2e2d73849ce269ee`
- `v1_workers_12.py`: `1441146a713feafd3994400c5a3d51e900d632c70d9b74d7052001dd82f0e9a8`
- `v1_carrots_5.py`: `e960609e19e7b256304743573147c618a172688304a94b455da3218a2bcdf6ca`
- `v1_carrots_8.py`: `31d97a26f1030a1c1b990498f00c35f168c66f386b7676e7dff5cdb16a5e119d`
- `v1_carrots_15.py`: `2cafd337a1b45b7831b8a50a98215a21cec365886c3da146159cae48864da68d`
