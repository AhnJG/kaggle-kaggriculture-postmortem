# coordination/reports/cowork — 1개 문서 묶음

원본 파일을 파일명(시간) 순으로 이어 붙였다. 각 절 제목이 원래 경로다.


---

## `reports/cowork/20260909-1930-KAGRI-018.md`

# KAGRI-018 — 외부 플레이북 검토, ABSORPTION 정정, AGENTS.md 개정

담당: cowork(claude-opus-5) · 사람 승인: **받음** (2026-09-09)

## VERDICT

**DONE.** 외부 가이드 문서(`~/Documents/Codex/2026-09-08/kaggle/outputs/kaggle-top-player-playbook.html`)
검증 중 `evidence/ABSORPTION.md` 의 상점 해금 주기 오류를 발견해 엔진 소스로 판정·정정했고,
그 결과가 진행 중인 EXP-003 의 매도 상한 정의를 바꿨다. 함께 `AGENTS.md` 8개 조항을 추가하고
`coordination/BOARD.md` 를 v0 제출 이후 상태로 갱신했다. **전략 코드는 건드리지 않았다.**

## 핵심 사실 2개

1. `[ENGINE]` **상점 해금은 3일마다, 상한 8개다** — `kaggriculture.py:867`
   (`townShopUnlockInterval` default **3**), `:886` (`next_day % 3 == 0`), `:118`
   (`MAX_SHOP_INSTANCES = 8`). `ABSORPTION.md` 는 소비 주기 `townShopSellInterval`(**4턴**, `:733`)과
   혼동해 "4일마다 7개"로 계산했다. 실제 스케줄은 **day 3·6·9·12·15·18·21·24**.
   상점 인스턴스 소비 tick 합 588 → **792**. **시즌 흡수량 전체 +28.8%** (160,035 → **206,190**).
   교차검증: 정정값을 8개 상점 정상상태 일일 흡수율로 환산하면
   딸기 25·우유 19·당근 19·밀 31·양털 13·토마토 13·달걀 13·멜론 1·비료 0 으로
   **`FACTS.md` 의 `[ENGINE+계산]` 일일표와 정확히 일치**한다. 즉 틀린 문서는 ABSORPTION 하나였다.

2. `[ENGINE]` **일일 흡수량은 상수가 아니다.** 상점이 day 3 에 1개 → day 24 에 8개가 되므로
   같은 품목의 일일 흡수량이 후반에 **8배**가 된다. day 1~2 는 상점 0개라 전 품목 **1/일**(타운센터뿐).
   따라서 `시즌흡수량 / 30` 평탄 상한은 **초반 과다 매도·후반 과소 매도**를 동시에 만든다.
   미래 해금은 예측 불가하지만 **`obs["town"]["unlocked_shops"]` 는 관측 가능**하므로
   상한을 기댓값이 아닌 **실현값의 함수**로 정의할 수 있다.

## exact path + SHA-256

```
AGENTS.md                                              3da05020d1166a1102554d2a6874f0c84ef1483e426de134894d8283cfe757f2
evidence/ABSORPTION.md                                 aa3fc7f7a7106bd519c887c2567153b9aefa0232e14bbdc77eef5e8b7f28cd92
evidence/FACTS.md                                      ee3f08ea85e4485ee95049173f5f6ac6c6183018b53b64eebeb9d0c6a29aaa07
coordination/BOARD.md                                  fd5a2b1c62a199841eaf1a5a5b4672b36c8a908bd63a41d050313f7d4f2b459f
coordination/proposals/codex/BRIEF_exp003_absorption.md 0b5d2a6b1d859773bed4ffb6b1669f7361ed1f56278ceeef3b3bd1f605c27764
```

| 파일 | 조치 |
|---|---|
| `evidence/ABSORPTION.md` | §1·§2 정정, §5 동적 흡수량 함수 신설, §7 영향 범위 추가 |
| `evidence/FACTS.md` | 상점 해금 file:line 명시, 일일표에 시간가변 경고, 시즌가치 추가, 파이썬 3.13.14 정정 |
| `coordination/proposals/codex/BRIEF_exp003_absorption.md` | §1 표 교체, A-2 고정 cap **폐기**, **부록 B 동적 cap** 추가 |
| `coordination/BOARD.md` | 전면 갱신 (이전 판 `BOARD.md.20260906.bak`) |
| `AGENTS.md` | R1~R8 반영 (이전 판 `AGENTS.md.20260907.bak`) |
| `coordination/proposals/cowork/PROPOSAL_20260909_playbook_review.md` | 제안 원문 |

## 실행한 검증과 결과

```bash
# 1. 해금/소비 주기 상수 확인
grep -n "ShopUnlockInterval\|ShopSellInterval\|MAX_SHOP_INSTANCES =" \
  .venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py
python3 -c "import json;j=json.load(open('.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.json'))['configuration'];print({k:j[k]['default'] for k in ['townShopUnlockInterval','townShopSellInterval','townCenterSellInterval','turnsPerDay']})"
# -> {'townShopUnlockInterval': 3, 'townShopSellInterval': 4, 'townCenterSellInterval': 24, 'turnsPerDay': 24}

# 2. 시즌 흡수량 재계산 (스니펫 전문은 evidence/ABSORPTION.md §2)
# -> tick sum 792 / 합계 206,190 / MILK+WOOL 97,920 (47.5%)

# 3. 교차검증 — 정상상태 일일 흡수율이 FACTS 일일표와 일치
# -> {'WHEAT':31,'STRAWBERRY':25,'MILK':19,'CARROT':19,'TOMATO':13,'EGG':13,'WOOL':13,'MELON':1,'FERTILIZER':0}
```

- `[LOCAL]` 세 검증 모두 PASS. 에이전트 코드·후보·결과 JSON·릴리스·제출은 **만들지 않았다.**
- 플레이북 수치 12개 전수 대조: **불일치 0건** (tapes 47개, BUY_LAND 141.7/151, 일꾼 12.1/14,
  PASTURE 15.0 / COOP 2.3, COW+SHEEP 91.8%, v0 337.2, crop 후보 100/0/0 vs 0/0/400 등).

## AGENTS.md 개정 요약

| # | 위치 | 내용 |
|---|---|---|
| R1 | §2.1 | 우리 문서끼리 모순 시 **엔진으로 판정**, 판정 전 양쪽 인용 금지, 진 쪽에 정정 사유 기록 |
| R2 | §3 | **`[COMMUNITY]` 태그** 신설 — "1위 솔루션이 그랬다"는 승격 사유 아님 |
| R3 | §3 | 무음 실패 표로 정리 + **흡수량 초과 매도**·**씨앗 부족 PLANT**·**자체 클램프** 추가. "카운터 0 ≠ 손실 0" |
| R4 | §5 | 실험 카드 **YAML 스키마** 고정, 서술형 항목 있으면 구현자가 **BLOCKED 반환**(계약 준수) |
| R5 | §6 | **에피소드 1,200s 합산 예산** — 779s × 2 = 1,558s > 1,200s. 내부 deadline 은 예산÷719 |
| R6 | §7.4/7.5 | 2슬롯 "다름"을 **승패 패턴 상관**으로 정의, 동점=선제출 승 명시, **릴리스 전 6줄 체크리스트** |
| R7 | §9 | **KILL 부활 차단** — 재검토 조건 인용 필수, 근거는 `[ENGINE]`/`[HOSTED]`, `[LOCAL]` 단독 불가 |
| R8 | §11 | **BOARD 신선도 게이트** — 2일 이상 오래됐거나 LEDGER 와 어긋나면 작업 전 반환 |

## 사람 질문 2건에 대한 답

**Q1. cap 공식 변경이 one-factor 계약을 깨는가?**
아니다. §5 의 one-factor 는 **후보 간 비교축**에 대한 제약이다. 동적 cap 은 B1/B2/B3 **전부에
동일하게** 적용되는 공통 규칙이고, 세 후보를 가르는 축은 여전히 `issues_per_day` 하나다.
다만 **A-2 고정 cap 으로 측정한 결과가 있다면 부록 B 결과와 같은 표에 올리지 않는다** —
규칙이 다르면 다른 실험이다(§5 신설 조항). 선행 MELON 30→3 은 원래부터 실험이 아니라
correction 이고, cap 규칙 교체도 같은 성격이므로 **correction 단계에 함께 넣는다.**

**Q2. K1(4구획)은 시장이 29% 커진 지금도 유효한가?**
**유효하다. 재검토 조건이 성립하지 않았다.**
K1 의 재검토 조건은 "**액션 예산이 근본적으로 늘어난 경우**"다. 흡수량 정정은 시장 크기를 바꿨을 뿐
액션 예산을 1도 늘리지 않았다. 게다가 정정은 **네 번째 구획을 사야 할 이유를 오히려 줄인다** —
파이가 커진 곳이 MILK·WOOL·STRAWBERRY 이고 셋 다 **타일이 아니라 동물·배분 문제**다.
현재 우리는 STRAWBERRY 를 상한 426 중 102 만 팔고 MILK·WOOL 은 0 이다.
**이미 가진 3구획의 상한도 못 채우는 상태에서 $4,000 을 네 번째 땅에 쓰는 것은
`[LOCAL]` 450게임 10-0 패라는 기존 근거를 뒤집을 이유가 되지 못한다.**
KILLS.md 는 수정하지 않았다.

## NEXT ACTION

**Codex**: BOARD 우선순위 0 (계측 정비: `harvest_blocked_by_shed`, `shed_peak`, `main.py:410` 주석)
→ 우선순위 1 (MELON 30→3 correction + cap 규칙 교체, `1000..1049` × 양 좌석)
→ stage A. **부록 A-2 의 cap 표는 쓰지 마라. 부록 B 함수를 쓴다.**

**Claude**: KAGRI-013 동물 레이어 실험 카드를 §5 신설 스키마로 사전등록.
파이의 47.5%(MILK 52,320 + WOOL 45,600)가 여기 있다.

**사람**: 팀 구성 여부 09-23 23:59 UTC 전 확정.

## 남긴 미결 2건 (내가 임의로 고치지 않음)

1. **KAGRI-017(상점 조건부 분기)의 우선순위가 올라갔다.** 부록 B 의 동적 cap 이
   `town.unlocked_shops` 를 읽으므로, 그 카드가 요구하는 관측 배관이 **stage B 에서 이미 깔린다.**
   KAGRI-016 뒤로 미룰 게 아니라 **stage B 와 묶는 것**을 코디네이터가 판단하라.
2. **`K9` 참조가 끊겨 있다.** `TASKS.md` 와 `POSTMORTEM_4bots.md` 가 "GOOSE 제외(K9)"를
   인용하는데 `KILLS.md` 에는 K8 까지만 있다. 내가 지어내지 않았다.
   `evidence/` 소유자(Claude)가 K9 를 정식 등재하거나 참조를 지워야 한다.
   근거는 이미 충분하다 — EGG 시즌 가치 **11,400** vs MILK 52,320 / WOOL 45,600, 상위 4봇 전원 거위 0.
