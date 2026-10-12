# coordination/proposals/cowork — 1개 문서 묶음

원본 파일을 파일명(시간) 순으로 이어 붙였다. 각 절 제목이 원래 경로다.


---

## `proposals/cowork/PROPOSAL_20260909_playbook_review.md`

# PROPOSAL — 플레이북 검토 결과와 AGENTS.md 개정안

작성 2026-09-09 · 작성자 cowork(claude-opus-5) · 상태 **✅ 승인·반영 완료 (2026-09-09)** — 결과 보고 `coordination/reports/cowork/20260909-1930-KAGRI-017.md`
대상 문서 `~/Documents/Codex/2026-09-08/kaggle/outputs/kaggle-top-player-playbook.html`

---

## 0. VERDICT

플레이북의 **Kaggriculture 수치는 전부 워크스페이스와 일치**한다(§1 검증표).
문제는 틀린 값이 아니라 **빠진 값**이다 — 이 프로젝트가 가진 가장 인과적인 두 사실
(시즌 흡수량, 에피소드 단위 1,200초 예산)이 문서에 없고,
이미 죽은 가설(K1 4구획)이 "실험해볼 것"으로 되살아나 있다.

검토 도중 **`evidence/ABSORPTION.md`의 시즌 흡수량 표가 약 29% 과소집계**임을
엔진 소스로 확인했다(§2). 이건 플레이북의 오류가 아니라 우리 문서의 오류이고,
**진행 중인 KAGRI-016(흡수량 정렬 매도 상한)의 입력값을 직접 바꾼다.**

---

## 1. 플레이북 사실 검증 `[LOCAL] 2026-09-09`

| 플레이북 주장 | 대조 | 판정 |
|---|---|---|
| 47 team-view / 유효 replay 29 | `private_artifacts/tapes` 파일 47개 | ✅ |
| 첫 BUY_LAND 평균 141.7턴 / 중앙값 151 | FACTS `[HOSTED] 2026-09-08` | ✅ |
| 평균 최대 일꾼 12.1 / 절대 최대 14 | 동일 | ✅ |
| BUILD_PASTURE 15.0 vs COOP 2.3 | 동일 | ✅ |
| COW+SHEEP 91.8% / GOOSE 8.2% | 동일 (50.4+41.4) | ✅ |
| Python 3.13.14 + `kaggle-environments==1.32.7` + `kaggriculture.py` = `bc8a5487…653e` | `.venv/pyvenv.cfg`, `environment/ENGINE_LOCK.md`, KAGRI-016 | ✅ |
| 720턴 / 시작 3,000 / 땅 1,000·2,000·4,000 / 셰드 100 / 시장 10칸 / HIRE·BUY_LAND도 10칸 소비 | FACTS `[OFFICIAL]` `[ENGINE]` | ✅ |
| 09-23 팀병합 · 09-30 최종제출 · 하루 5회 · 최신 2개 활성 | FACTS `[OFFICIAL]` | ✅ |
| v0 hosted 레이팅 337.2 | `evidence/HOSTED_LEDGER.md` | ✅ |
| crop 후보 v1 대비 100/0/0, 4봇 상대 0/0/400 (parent도 동일) | HYPOTHESES H17, AGENTS §7.1b | ✅ |
| builtin 3종 9조합 720턴 완주 | FACTS `[LOCAL] S4~S7` | ✅ |

> 부수 확인: **`evidence/FACTS.md`의 "클라우드·맥북 양쪽 3.11.15" 기재가 낡았다.**
> 현재 워크스페이스 인터프리터는 3.13.14다. 플레이북 쪽이 맞다. FACTS 정정 필요.

---

## 2. ⚠️ ABSORPTION.md 정정 — 시즌 흡수량 +28.8% `[ENGINE]`

`evidence/ABSORPTION.md` §1은 "상점은 **4일마다** 1개씩 해금 → day 4·8·…·28 → **7개**"라고 쓴다.
**엔진은 그렇지 않다.** `townShopSellInterval`(소비 4턴)과 `townShopUnlockInterval`(해금 3일)을
같은 값으로 혼동한 것이다.

```
kaggriculture.py:867   shop_interval = max(1, int(get(cfg, "townShopUnlockInterval", 3)))
kaggriculture.py:886   if next_day > 0 and next_day % shop_interval == 0:
kaggriculture.py:118   MAX_SHOP_INSTANCES = 8
kaggriculture.json     townShopUnlockInterval.default = 3   (townShopSellInterval.default = 4)
```

→ 실제 해금은 **day 3·6·9·12·15·18·21·24 = 8개**(상한 도달), ABSORPTION 가정보다
상점이 하나 더 많고 매번 더 일찍 열린다. 상점 인스턴스 소비 tick 합은 588 → **792**.

`evidence/FACTS.md`의 "**상점은 3일마다 8개까지 해금**"과 일일 흡수율표(딸기 25·밀 31·우유 19…)는
**엔진과 정확히 일치한다.** 즉 두 문서 중 틀린 쪽은 ABSORPTION.md 하나다.

### 정정된 시즌 흡수량 (상점 균등추출 기댓값, 30일)

| 품목 | 흡수량(정정) | 흡수량(기존) | base | **시즌 가치(정정)** | 기존 |
|---|---:|---:|---:|---:|---:|
| MILK | 327 | 250.5 | 160 | **52,320** | 40,080 |
| STRAWBERRY | 426 | 324 | 120 | **51,120** | 38,880 |
| WOOL | 228 | 177 | 200 | **45,600** | 35,400 |
| TOMATO | 228 | 177 | 60 | 13,680 | 10,620 |
| WHEAT | 525 | 397.5 | 25 | 13,125 | 9,938 |
| CARROT | 327 | 250.5 | 35 | 11,445 | 8,768 |
| EGG | 228 | 177 | 50 | 11,400 | 8,850 |
| **MELON** | **30** | 30 | 250 | **7,500** | 7,500 |
| FERTILIZER | 0 | 0 | 100 | 0 | 0 |
| **합계** | | | | **206,190** | 160,035 |

**결론은 안 뒤집힌다** — MILK+WOOL+STRAWBERRY 상위 3블록이 여전히 파이의 72%이고,
MELON 30 상한과 FERTILIZER 0도 그대로다. **바뀌는 건 상한의 절대값이다.**

**KAGRI-016 직접 영향**: BRIEF의 Stage B "1회 매도 상한 ≈ 흡수량/일"을
STRAWBERRY 324/30로 잡으면 안 된다. 일일 흡수율은 **상점 수에 따라 시간에 따라 커진다**
(day 3에 1개 → day 24에 8개). 시즌 총량/30 이라는 평탄화 자체가 모델 오류다.
전반 저활성·후반 고활성 구조이므로 **캡은 상수가 아니라 `f(현재 unlocked_shops)`여야 한다.**
`market.inventory`와 `town.unlocked_shops`는 둘 다 관측 가능하다(FACTS `[ENGINE]`).

재현:
```bash
python3 - <<'PY'
import re
src = open(".venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py").read()
print([l for l in src.splitlines() if "ShopUnlockInterval" in l or "MAX_SHOP_INSTANCES =" in l])
PY
```

---

## 3. 플레이북에서 **가져올 것** (현재 대회 적용)

| # | 가져올 것 | 왜 지금 필요한가 |
|---|---|---|
| P1 | **실험 카드 스키마**(`one_change` / `fixed` / `budget` / `success` / `failure` / `next_if_*` / `artifact`) | KAGRI-016이 BLOCKED된 이유가 정확히 이것 — 사전등록이 exact 값을 안 담았다 |
| P2 | **제출 전 10분 체크리스트**(Identity·Schema·Leakage·Runtime·License·Ledger) | 지금 §6·§7·§8에 흩어져 있어 릴리스 때 한 번에 못 본다 |
| P3 | **`[COMMUNITY]` 등급** | §2 진실의 순위에 5순위로 있는데 §3에 태그가 없다. 커뮤니티 주장이 무태그나 `[INFERENCE]`로 샌다 |
| P4 | **2슬롯 = error가 다른 두 전략**(안정 incumbent + 반응형 challenger) | §7.4가 "서로 다른 두 전략"이라 쓰지만 *무엇이 다름인지* 정의가 없다 |
| P5 | 무음 실패 계측 항목 확장 | 플레이북 목록에 없는 항목을 우리가 추가해야 한다 — §4 참조 |

## 3b. 플레이북에서 **가져오지 말 것**

| # | 항목 | 이유 |
|---|---|---|
| N1 | "4번째 구획은 별도 실험이 이길 때만 연다" | **K1은 이미 KILL이다.** 450게임 10-0 패, 재검토 조건은 "액션 예산이 근본적으로 늘어난 경우". 죽은 가설이 이름 바꿔 부활하는 전형적 경로 |
| N2 | "GOOSE는 항상 나쁘다 — 아직 결론 내리지 말 것" | 결론 낼 근거가 이미 있다. EGG 시즌 가치 11,400은 MILK 52,320·WOOL 45,600 대비 1/4이고, 상위 4봇 전원 거위 0이다. `[HOSTED]` 상관이 아니라 `[ENGINE]` 용량 문제 |
| N3 | "COW+SHEEP 91.8%는 상관 pattern일 뿐" | 인과가 이미 있다 — MILK+WOOL이 파이의 47%. 플레이북이 자기 `[ENGINE]` 등급을 안 쓴 부분 |
| N4 | 1위 solution 인용을 사실처럼 사용 | 플레이북 자신의 기준으로는 `[COMMUNITY]`인데(저자 자기보고), 본문에서 "1위니까"로 승격했다 |

---

## 4. AGENTS.md 개정안 (8건, 전부 계약 층위 — 수치는 안 박는다)

### R1 · §2 진실의 순위 — 내부 모순 판정 규칙 추가
> **우리 문서끼리 모순되면 엔진 소스로 판정한다. 판정 전까지 두 값 모두 인용 금지.**
> 판정 결과는 진 쪽 문서에 정정 사유와 재현 명령을 남긴다.

*근거*: 상점 해금 주기 3일/4일 모순이 오늘까지 살아 있었고, 진행 중인 실험의 입력값을 오염시켰다.

### R2 · §3 증거 규율 — `[COMMUNITY]` 태그 추가
태그 목록을 `[OFFICIAL] [ENGINE] [HOSTED] [LOCAL] [COMMUNITY] [INFERENCE] [HYPOTHESIS]`로.
> `[COMMUNITY]`는 **출처 URL·수집일·엔진 버전 없이 인용 금지**. 자기보고 성능 수치는
> 상대·시드·좌석·아티팩트가 없으면 `[COMMUNITY]`를 벗어나지 못한다.

### R3 · §3 무음 실패 목록 — 두 항목 추가
현재 목록(불법 액션·셰드 소멸·주문 절삭·SELL 미체결)에 추가:
> - **흡수량 초과 매도** — 시즌 수요를 넘긴 물량은 시장을 영구히 눌러 이후 매도까지 손해다.
> - **씨앗 부족 PLANT 치환** — 엔진이 조용히 PASS로 바꾸며 계측기에도 안 잡힌다 (`:920-928`).

*근거*: 전자는 seed 1000에서 MELON을 상한의 8.6배 팔았던 실제 손실이고,
후자는 H13에서 `[ENGINE]` 확정인데 §3 목록에는 없다.

### R4 · §5 실험 규약 — 카드 스키마를 계약으로 고정
> 카드는 다음을 **exact 값**으로 담는다. 하나라도 서술형이면 구현자는 실행하지 않고 BLOCKED로 반환한다.
> `parent SHA-256` / `one_change`(변경 전·후 값) / `fixed`(고정 목록) /
> `seeds`(리스트, 실행 전 확정) / `seats`(양 좌석) / `opponents`(파일 경로 + SHA) /
> `success` `failure` `inconclusive`(각각 숫자 임계) / `next_if_success` `next_if_failure`.
>
> **구현자는 모호한 정의를 임의 해석하지 않는다. 반환은 실패가 아니라 계약 준수다.**

*근거*: KAGRI-016이 정확히 이 행동을 했다. 계약에 없어서 "BLOCKED"로 보였을 뿐, 옳은 행동이었다.

### R5 · §6 런타임 계약 — 에피소드 합산 예산 명시
현재는 "턴 1s + overage 60s + 에피소드 1200s"를 나열만 한다. 함의를 박는다.
> **세 예산은 독립이 아니다.** 719회 호출 × 1s + overage 60s = 에이전트당 779s이고,
> 두 에이전트 합 1,558s > 에피소드 1,200s다. 로컬 `env.run()`은 순차 호출한다.
> → **양쪽이 모두 느리면 턴 타임아웃이 아니라 에피소드가 먼저 죽는다.**
> 내부 deadline은 턴 1s가 아니라 **에피소드 예산 / 719** 기준으로 잡는다. hosted 스케줄링은 `[N/A]`.

*근거*: FACTS의 ★ 항목이 계약에 반영돼 있지 않다. 이 대회에서 가장 늦게 발견되는 실패 유형이다.

### R6 · §7 승격 게이트 — 릴리스 전 체크리스트 6항목
> `Identity`(제출 파일 SHA = 측정 파일 SHA) / `Schema`(루트 main.py, hands 정렬) /
> `Runtime`(에피소드 예산의 70~80% 이내) / `Isolation`(빈 폴더 clean-room import) /
> `License`(외부 코드·상대 봇 라이선스) / `Ledger`(submission ID ↔ artifact SHA).
> **여섯 줄을 릴리스 보고서에 그대로 복사해 채운다.**

### R7 · §9 실패의 범위 — KILL 부활 차단
> **KILL 항목은 해당 항목의 재검토 조건을 인용하지 않고는 실험 카드의 `hypothesis`가 될 수 없다.**
> 재검토 조건이 성립했다는 근거는 `[ENGINE]` 또는 `[HOSTED]`여야 한다. `[LOCAL]` 단독 불가.

*근거*: 플레이북이 K1(4구획)을 "실험이 이기면 연다"로 되살렸다. 계약이 막아야 한다.

### R8 · §11 세션 시작 — BOARD 신선도 게이트
> 1번 단계에서 `coordination/BOARD.md`의 **갱신일을 먼저 본다.**
> 오늘과 2일 이상 벌어졌거나 `HOSTED_LEDGER.md`의 최신 제출과 상태가 어긋나면,
> **작업을 시작하기 전에 코디네이터에게 반환한다.**

*근거*: BOARD는 2026-09-06에 멈춰 "제출 0회, 슬롯 5회 전부 보유"라고 쓰여 있는데
`HOSTED_LEDGER.md`는 v0 제출 완료(56068891, 레이팅 337.2)를 기록한다.
**세션 시작 1번 문서가 틀린 상태로 사흘 갔다.**

---

## 5. 사람 승인이 필요한 것 — **전건 승인, 반영 완료**

> 1·2·3·4 반영 완료. 5는 부록 B(동적 cap)로 확정.
> KILLS.md K1 은 **수정하지 않았다** — 재검토 조건 미성립(보고서 Q2).


1. R1~R8을 `AGENTS.md`에 반영할지 (반영 주체·시점)
2. `evidence/ABSORPTION.md` §1·§2 정정 — 소유자는 Claude
3. `evidence/FACTS.md` 파이썬 버전 3.11.15 → 3.13.14 정정
4. `coordination/BOARD.md` 갱신 — 코디네이터만 가능
5. KAGRI-016 BRIEF의 Stage B 캡 정의를 `f(unlocked_shops)`로 바꿀지 (상수 캡은 모델 오류)

## 6. NEXT ACTION

코디네이터가 §5의 5건을 판정한다. §2 정정은 진행 중 실험의 입력값이므로 **가장 먼저**.
