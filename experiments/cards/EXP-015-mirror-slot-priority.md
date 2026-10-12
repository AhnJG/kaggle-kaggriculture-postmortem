# EXP-015 — 정확한 복제 상대에게만 앞쪽 SELL 묶음을 가격 높은 순으로 (거울전 우위 2)

hypothesis_id: HYP-0034
test_id: TEST-F0-MIRROR-SLOT-20260920

사전등록 2026-09-20 (Claude, Coordinator 역할). **실행 전 문서.** EXP-014 와 독립인 다른 한 요인이다(둘을 합친 변형은 이 카드가 아니다). 커밋 후 seed·좌석·상대·임계·감지 규칙 변경 금지.

## 근거 (§7.3 postmortem 인용)

- `[HOSTED]` 무승부 episode **110866715**(EXP-014 와 같은 근거). 그 경기에서 P2 의 고가 SELL(MILK·WOOL·MELON·STRAWBERRY)이 있는 122턴 중 **첫 고가 SELL 이 slot 0 이 아닌 턴 13턴**(slot 1: 12, slot 2: 1) — `evidence/FACTS.md` 2026-09-20 절.
- `[ENGINE]` `kaggriculture.py:544-628` — slot 번호 순서로 체결. 복제본이 같은 품목을 slot 1 에 두는 turn 에 우리가 slot 0 에 두면 우리가 먼저 판다.
- P2 는 이미 `_adv_frontload`(sale 을 앞으로, `main.py` EXP293 절)가 있으나 앞쪽 SELL 묶음 **안의 순서**는 원래 순서다. 이 카드는 그 묶음 안에서만 순서를 바꾼다.

```yaml
# hypothesis_id·test_id: 파일 머리 참조
id:            EXP-015
parent:        releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz
               # sha256 1178ffa0614673a58fb1ee5b2a44003eecd5640634d6f3471e84ac92c1fbf388 / main.py cddf51ea…a94d
one_change:    거울 모드일 때 turn 144–717 에서 market 목록 앞의 연속 SELL 묶음(길이 >= 2)을 원래 순서 -> 현재 시장 가격 내림차순(같으면 원래 순서)
fixed:         [parent main.py 바이트 전부, SELL 묶음 뒤의 주문 순서, 주문 수량, 거울 모드 밖의 모든 행동]
opponents:     EXP-014 와 동일 (mirror = P2, panel 5개, 경로·SHA 동일)
seeds:         mirror [3000..3014] / panel [3000..3009]
seats:         both
runner:        tools/arena.py (EXP-014 와 동일 형식)
metric:        EXP-014 와 동일
success:       M 점수 >= 22.5/30  AND  N 회귀 <= 2/100  AND  N 변형 총점 >= N P2 총점 - 2.0
failure:       M 점수 <= 16.5/30  OR  N 회귀 >= 6/100
inconclusive:  그 밖
invalid:       EXP-014 와 동일 (기준선 P2 vs P2 는 EXP-014 에서 기록한 것을 공유해도 된다 — 같은 runner·seed·SHA 일 때만)
next_if_success: 사람 결정 — hosted 동시 비교
next_if_failure: 순서 변경 폐기
artifact:      releases/f0-mirror-slot-exp015/submission.tar.gz
```

정의(M, N, 회귀, 거울 모드, 계측)는 EXP-014 §정의와 같다. 계측 추가: 순서를 실제로 바꾼 turn 수 `reorders`.

## 부록 A — parent `main.py` 끝에 **그대로 덧붙일** 코드

EXP-014 부록 A 의 `_MIR_PARENT` 부터 `_mir_mode` 함수 끝까지를 **같은 바이트로** 넣고(`_MIR_REPORT` 에 `'reorders': 0` 추가), 그 뒤에:

```python
def _mirror_slot_agent(observation, configuration=None):
    try:
        on = _mir_mode(observation)
    except Exception:
        _MIR_REPORT['errors'] += 1
        on = False
    action = _MIR_PARENT(observation, configuration)
    if not on or not isinstance(action, dict):
        return action
    try:
        _MIR_REPORT['mirror_turns'] += 1
        market = [list(o) for o in (action.get('market') or [])]
        k = 0
        while k < len(market) and len(market[k]) >= 3 and market[k][0] == 'SELL':
            k += 1
        if k < 2:
            return action
        prices = (observation.get('market') or {}).get('prices') or {}
        head = sorted(market[:k], key=lambda o: -float(prices.get(o[1], 0) or 0))
        if head == market[:k]:
            return action
        _MIR_REPORT['reorders'] += 1
        return dict(action, market=head + market[k:])
    except Exception:
        _MIR_REPORT['errors'] += 1
        return action


_mirror_slot_agent.telemetry = _MIR_REPORT
```

빌드 확인(구현자): 마지막 callable 이 `_mirror_slot_agent`, 거울 모드가 꺼진 경기에서 parent 와 719턴 행동 동일, 예외 0.

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
