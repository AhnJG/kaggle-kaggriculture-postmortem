# EXP-014 — 정확한 복제 상대에게만 판매 앞당김 창을 3턴→4턴 (거울전 우위 1)

hypothesis_id: HYP-0033
test_id: TEST-F0-MIRROR-LEAD-20260920

사전등록 2026-09-20 (Claude, Coordinator 역할). **실행 전 문서.** 커밋 후 seed·좌석·상대·임계·감지 규칙 변경 금지. 결과를 본 뒤 임계를 고치지 않는다.
실행 범위: F0 fast lane "공개 exact artifact + 개선 1개 변형"(승인 2026-09-18·19). 제출은 사람이 건별로 결정.

## 근거 (§7.3 postmortem 인용)

- `[HOSTED]` P2(56347732) 112경기 중 무승부 7판. episode **110866715**(상대 Anaconda): 두 플레이어 행동 **719/719 동일**, 최종 100,774 대 100,774, turn 1–143 두 농장 공개 상태 매 턴 동일 — 상대가 P2 와 같은 코드. (`evidence/FACTS.md` 2026-09-20 절, `evidence/raw/p2_losses_20260920/features.csv`, 분석 보고 `coordination/reports/claude/20260920-0114-P2-LOSS-ANALYSIS.md`)
- `[ENGINE]` `kaggriculture.py:544-628` — 같은 slot 의 SELL 은 단위별 같은 가격(대칭). 같은 turn·같은 slot 에서 두 복제본은 영원히 대칭이다. 한쪽이 **먼저(더 이른 turn)** 팔면 그 쪽이 commit 전 높은 가격을 받는다.
- P2 는 이미 EXP293 판매 앞당김을 갖고 있다(`main.py:3316` `_ADV_LOOK=3` — 3턴 안에 팔 물건이 창고에 있으면 지금 판다). 복제본도 똑같이 3턴이라 대칭이다. **4턴으로 늘리면 복제본보다 한 턴 먼저 판다.**
- KILLS K2("2턴 앞 선행매도" C92 상대 2-2)는 일반 상대 기준이다. 이 카드는 **정확한 거울전에서만** 창을 늘리므로 K2 의 재검토 대상이 아니며 K2 를 인용해 부활시키지 않는다.

```yaml
# hypothesis_id·test_id: 파일 머리 참조
id:            EXP-014
parent:        releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz
               # sha256 1178ffa0614673a58fb1ee5b2a44003eecd5640634d6f3471e84ac92c1fbf388
               # main.py cddf51ea4e5bac24e5118b12b78f771a92055e17064e062b0267724822b8a94d (entry = 마지막 callable _e336_agent)
one_change:    거울 모드일 때 turn 144–717 에서 _ADV_LOOK 3 -> 4 (호출 동안만, 끝나면 3 으로 복원)
fixed:         [parent main.py 바이트 전부, 거울 모드 밖의 모든 행동, _ADV_* 의 다른 값, 오프닝, router]
opponents:     # 모두 파일 경로, arena 가 엔진 로더(마지막 callable)로 불러온다
  mirror:      releases/public-lynnsakurai-farming-score-v2-exact/main.py        # P2 정확 복제
  panel:       [releases/public-alperen-before-dawn-stock-cash-sales-exact/main.py,          # tar cce494e5…a9ec
                releases/public-goodpjw2008-kaggriculture-melon-threshold-squeeze-2749-exact/main.py,  # cfdd7f6c…7f63
                releases/public-seyitkaangunes-kaggriculture-2820-score-exact/main.py,        # f623578b…9114
                releases/public-tetsutani-market-smart-farming-exact/main.py,                  # f5e41bd0…916e
                releases/public-yhay81-shop-router-0909-exact/main.py]                        # 40d2bc39…7791
seeds:         mirror [3000..3014] (15개) / panel [3000..3009] (10개)
seats:         both
runner:        tools/arena.py --a <A> --b <B> --seeds N --seed-start 3000 --json <out>
metric:        승격 = M 점수(W=1,D=0.5,L=0) / 진단 = N 회귀 수, N 총점
success:       M 점수 >= 22.5/30  AND  N 회귀 <= 2/100  AND  N 변형 총점 >= N P2 총점 - 2.0
failure:       M 점수 <= 16.5/30  OR  N 회귀 >= 6/100
inconclusive:  그 밖
invalid:       기준선 P2 vs P2 (seed 3000..3014 양 좌석) 무승부 < 25/30  OR  예외/ERROR >= 1  OR  입력 SHA 불일치
next_if_success: 사람 결정 — P2 재제출 + 변형 제출로 hosted 동시 비교 (fast lane §4 단계 E)
next_if_failure: 창 변경 폐기. EXP-015 결과와 독립
artifact:      releases/f0-mirror-lead-exp014/submission.tar.gz (빌드 후 SHA 기록)
```

## 정의

- **M (거울 시험):** 변형 vs P2, seed 3000–3014 양 좌석 30경기. 먼저 **기준선** P2 vs P2 같은 seed 30경기를 기록한다(invalid 판정용).
- **N (비열등 패널):** 변형 vs 패널 5개, seed 3000–3009 양 좌석 = 100경기. 같은 조건의 P2 vs 패널 100경기를 기준으로.
  **회귀** = 같은 (상대, seed, 좌석)에서 P2 는 이기거나 비겼는데 변형은 진 경기.
- **거울 모드** (EXP-015 와 공통, 부록 A 코드 그대로): turn 1–143 의 매 호출에서 `observation['farms'][0] == observation['farms'][1]` 이 143번 모두 참이면, turn 144 에 켜고 그 경기 끝까지 유지. 한 번이라도 다르면 그 경기 내내 끔. step 0 에 초기화.
- **계측:** `_MIR_REPORT` 에 거울 모드 켜진 경기 수, 적용 turn 수, 오류 수. 패널 경기에서 거울 모드가 켜진 경기 수를 결과에 따로 적는다.

## 부록 A — parent `main.py` 끝에 **그대로 덧붙일** 코드 (다른 바이트 변경 금지)

```python
# ---- EXP-014 mirror sale lead (Sian, 2026-09-20). Appended; parent bytes above are unchanged. ----
_MIR_PARENT = _e336_agent
_MIR_STATE = {}
_MIR_REPORT = {'mirror_games': 0, 'mirror_turns': 0, 'errors': 0}
_MIR_FROM, _MIR_TO = 144, 718


def _mir_mode(obs):
    step = int(obs.get('step', 0) or 0)
    player = int(obs.get('player', 0) or 0)
    st = _MIR_STATE.get(player)
    if st is None or step == 0 or step < st['last']:
        st = _MIR_STATE[player] = {'ok': True, 'n': 0, 'last': -1, 'mode': False}
    if step != st['last']:
        st['last'] = step
        if 1 <= step <= 143:
            farms = obs.get('farms') or []
            if len(farms) == 2 and farms[0] == farms[1]:
                st['n'] += 1
            else:
                st['ok'] = False
        if step == _MIR_FROM:
            st['mode'] = st['ok'] and st['n'] == 143
            if st['mode']:
                _MIR_REPORT['mirror_games'] += 1
    return st['mode'] and _MIR_FROM <= step < _MIR_TO


def _mirror_lead_agent(observation, configuration=None):
    global _ADV_LOOK
    try:
        on = _mir_mode(observation)
    except Exception:
        _MIR_REPORT['errors'] += 1
        on = False
    if not on:
        return _MIR_PARENT(observation, configuration)
    _MIR_REPORT['mirror_turns'] += 1
    old = _ADV_LOOK
    _ADV_LOOK = 4
    try:
        return _MIR_PARENT(observation, configuration)
    finally:
        _ADV_LOOK = old


_mirror_lead_agent.telemetry = _MIR_REPORT
```

빌드 확인(구현자): exec 후 마지막 callable 이 `_mirror_lead_agent` 인지, 거울 모드가 꺼진 경기에서 parent 와 719턴 행동이 **완전히 같은지**(패널 1경기 이상), 예외 0.

---

## 결과 기록 (2026-09-20, Claude 판정 — 카드 본문은 위에서 한 글자도 바꾸지 않았다)

입력: Antigravity 실행 보고 `coordination/reports/antigravity/20260920-2130-EXP014-015-RUN.md` (SHA `4cb62f91e98e22a98160313ff7e40cd6be831b99e06998f13a0f40b6875d24ca`), 집계 `analysis/exp014_015/summary.json` (SHA `569a3d4da6de3c2c41699351a038a76e62290585dd6bb8ccdb5084669ea13351`), raw 18개. Claude 가 raw `games_detail` 에서 W/D/L·회귀를 다시 계산해 일치 확인. 예외·ERROR 0/390.

| 항목 | 값 |
|---|---|
| B0 P2 vs P2 (seed 3000–3014, 양 좌석) | 3/24/3 — **무승부 24/30** (비무승부 6경기 = seed 3002·3011·3012, 좌석이 바뀌면 부호만 반대: 좌석 비대칭) |
| M14 EXP-014 vs P2 | **25/0/5, 25.0/30** (승리 격차 중앙값 101 코인; 패배 seed 3003×2, 3006×2, 3012 좌석0) |
| M15 EXP-015 vs P2 | 1/0/29, 1.0/30 |
| N P2 vs 패널 | 100/0/0 |
| N14 | 100/0/0, 회귀 **0**. 거울 모드는 alperen 상대 20경기에서 켜진 것으로 보인다(격차 20/20 변화), 나머지 80경기는 P2 와 격차 완전 동일 |
| N15 | 86/0/14, 회귀 **14** (전부 alperen 상대) |

**판정:** 카드 invalid 조건 "기준선 P2 vs P2 무승부 < 25/30" 에 해당(24/30) → **EXP-014 · EXP-015 모두 INVALID**(성능 판정 N/A). 임계를 결과를 보고 고치지 않는다.
- EXP-014: invalid 가 아니었다면 success 조건(M ≥ 22.5, 회귀 ≤ 2, N 총점 ≥ P2−2)을 모두 만족하는 수치였다. → 새 seed 재현 카드 EXP-014R 로 넘긴다.
- EXP-015: 수치상 failure 조건 두 개(M ≤ 16.5, 회귀 ≥ 6)를 모두 크게 넘었다. 재현하지 않고 **폐기** 권고.
