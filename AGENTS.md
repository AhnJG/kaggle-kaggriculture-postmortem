# AGENTS.md — Kaggriculture 프로젝트 계약

**이 파일이 정본이다.** `CLAUDE.md`, `GEMINI.md`는 이 파일을 가리킨다.
여기에는 **계약만** 있다. 전략은 `plan/`, 사실과 수치는 `evidence/FACTS.md`,
지금의 우선순위는 `coordination/BOARD.md`에 있다.
지침에 수치를 박으면 틀린 채로 헌법이 된다. 실제로 지난 계획서들의 오류가 그렇게 생겼다.

## 0. Codex Skill 호출

- `kaggle-experiment-review` skill은 **자동호출하지 않는다.** 사용자가 명시적으로
  `kaggle-experiment-review`를 지정하거나 "그 skill을 써서 검토"하라고 요청할 때만 사용한다.

---

## 1. 목표

평균 코인이 아니라 **승/무/패 확률**과 최종 Bradley-Terry 강도를 올린다.
코인 격차는 레이팅에 반영되지 않는다. 현금 차이·생산량·평균 profit은 원인 분석용 2차 지표다.

**이미 이기는 상대에게 마진을 늘려도 레이팅은 오르지 않는다. 지는 소수 경기만이 중요하다.**

---

## 2. 진실의 순위

1. **공식 Rules / Overview / Kaggle Staff 답변** — 규정·평가·일정
2. **고정된 엔진 소스** `kaggle-environments==1.32.7` (`environment/ENGINE_LOCK.md`) — 게임 동작
3. **같은 창(window)의 hosted 에피소드** — 성능
4. **로컬 실험** — 가설 검증
5. **커뮤니티 글·공개 노트북** — 가설 생성 자료일 뿐

**공식 문서는 엔진 아래다.** 같은 공식 페이지 안에서 급수 주기가 서로 모순되고,
공식 Quick Start 예제에는 버그가 있으며, 공개 노트북의 서술과 실제 코드가 다른 사례가 여러 건 확인됐다.
영역이 다르면 그 영역의 1순위를 따른다 — 규정은 Rules, 게임 동작은 엔진.

### 2.1 우리 문서끼리 모순될 때 `[2026-09-09 추가]`

**엔진 소스로 판정한다. 판정 전까지 두 값 모두 인용 금지.**
판정 결과는 **진 쪽 문서에 정정 사유·정정일·재현 명령을 남긴다.** 조용히 덮어쓰지 않는다.
정정이 다른 문서의 유도값을 바꾸면 그 문서들을 같은 커밋에서 함께 고친다.

증거: `FACTS.md` 는 상점 해금을 "3일마다 8개", `ABSORPTION.md` 는 "4일마다 7개"로 적었고
**사흘간 둘 다 살아 있었다.** 엔진은 3일/8개다(`:867` `:886` `:118`).
그 사이 진행 중이던 EXP-003 의 매도 상한이 29% 낮은 값에서 유도되고 있었다.

---

## 3. 증거 규율

모든 주장에 꼬리표를 붙인다.

`[OFFICIAL]` `[ENGINE]` `[HOSTED]` `[LOCAL]` `[COMMUNITY]` `[INFERENCE]` `[HYPOTHESIS]`

- **`[COMMUNITY]`** = 공개 노트북·디스커션·수상 후기. **출처 URL · 수집일 · 엔진 버전 없이 인용 금지.**
  자기보고 성능 수치는 **아티팩트 · 상대 · 시드 수 · 좌석 · 엔진**이 전부 있기 전까지
  `[COMMUNITY]` 를 벗어나지 못한다. "1위 솔루션이 그랬다"는 승격 사유가 아니다.
- **`[LOCAL]`은 `[HOSTED]`를 대체하지 않는다.**
- 수치에는 **재현 명령 또는 file:line**을 반드시 붙인다. 없으면 FACT가 아니라 가설이다.
- 로컬 결과에는 artifact SHA · seed · 좌석 · 상대 · 러너 버전을 함께 적는다.
- 서로 다른 날짜·게임 수의 라이브 레이팅을 직접 비교하지 않는다.
- **무음 실패를 계측한다.** 아래는 전부 **예외를 내지 않는다.**
  "예외 0"만 확인하고 넘어가면 손실이 안 보인다.

  | 무음 실패 | 어떻게 보이나 |
  |---|---|
  | 불법 액션 | no-op |
  | 셰드 초과 | 물건 소멸 |
  | 11번째 이후 주문 | 조용히 절삭 |
  | SELL 미체결 / BUY 자금부족 | 부분 체결 |
  | **씨앗 부족 PLANT** | 엔진이 그 턴 해당 작물 PLANT **전부**를 PASS 로 치환. **계측기에도 안 잡힌다** (`:920-928`) |
  | **흡수량 초과 매도** | 카운터 0, 예외 0. 초과분이 시장을 **영구히 눌러** 이후 매도까지 손해 |
  | **에이전트가 스스로 자른 주문** | `orders_truncated` 는 엔진이 자른 것만 잡는다. 우리 클램프는 안 잡힌다 |

  **카운터가 0인 것은 손실이 0이라는 뜻이 아니다.** 가드가 액션을 합법 액션(PASS)으로
  바꿔치기하면 어느 카운터에도 안 잡힌다. 가드를 새로 넣을 때는 **그 가드 전용 카운터를 함께** 넣는다.

### 3.1 공용 가설 원장 `[2026-09-12 추가]`

루트 `HYPOTHESES.md`는 우리 실험과 공개 notebook/discussion 주장을 함께 찾는 정본이다.

- 공개 자료 검토, 새 전략 가설, 실험 카드·candidate, arena·결과 판독, release·submission·hosted 판독 **전에** 원장을 읽는다.
- 같은 주장은 같은 `HYP-####`를 쓴다. agent나 구현이 달라도 독립 검증은 별도 `TEST-...`만 배정한다.
- 실험 카드에는 실행 전 `hypothesis_id`와 고유 `test_id`를 넣는다. 원장에 없는 ID면 실행 금지다.
- 위 작업 뒤에는 성공·실패·불확정·N/A를 숨기지 말고 `tools/update_hypotheses.py`로 기록한다. 이 command가 agent별 immutable event와 원장을 함께 갱신한다.
- agent는 `HYPOTHESES.md`를 직접 편집하지 않는다. event는 `coordination/hypotheses/<agent>/`에만 쓴다.
- 공개 주장이 반복돼도 자동으로 `[LOCAL]`·`[HOSTED]`로 승격하지 않는다. 별도 검증 결과와 artifact/submission ID가 있어야 한다.
- 작업 종료 전에 `python3 tools/validate_hypotheses.py --strict`가 exit 0이어야 한다. 실패하면 기록 작업은 미완료다.

---

## 4. 소유권

| 경로 | writer |
|---|---|
| `main.py` `src/` `tests/` `tools/` `releases/` | **Codex — 단독 integrator** |
| `docs/` `analysis/` `opponents/` | Gemini |
| `experiments/cards/` `evidence/` `plan/` | **Claude** — 설계·사전등록·증거 |
| `experiments/candidates/` `experiments/results/` | **Codex** — 실행 산출물 |
| `environment/` | Cowork |
| `coordination/BOARD.md` | 코디네이터만 |
| `coordination/proposals/<agent>/` | 해당 agent |
| `HYPOTHESES.md` | **`tools/update_hypotheses.py`만** — 공용 tool-managed view |
| `coordination/hypotheses/<agent>/` | 해당 agent — updater가 쓰는 immutable event |

- **한 파일 한 writer.** 소유 경로 밖은 제안(proposal)으로만 낸다.
- 같은 폴더에서 branch checkout / rebase / stash를 **병렬 실행 금지**.
- 중요한 변경은 `제안자 → 구현자 → 독립 검증자 → 사람 승인`을 거친다.
  **제안자가 자기 결과를 단독 승인할 수 없다.**

---

## 5. 실험 규약

실행 **전에** `experiments/cards/EXP-*.md`에 적는다. **아래는 스키마다 — 항목이 아니라 형식이다.**

```yaml
id:            EXP-003
hypothesis_id: HYP-####
test_id:       TEST-####
parent:        experiments/candidates/<file>.py   # + SHA-256
one_change:    <무엇을> <A> -> <B>                 # 변경 전·후 exact 값
fixed:         [ ... ]                            # 이번에 건드리지 않는 것 명시
hypothesis:    <postmortem 인용 1건 필수 — §7.3>
opponents:     [ opponents/public/<bot>.py + SHA, ... ]
seeds:         [1000..1049]                        # 리스트로 확정. 실행 후 추가 금지
seats:         both
metric:        <승격 지표> / <탐색 지표>            # §7.1b
success:       <숫자 임계>
failure:       <숫자 임계>
inconclusive:  <숫자 임계>
next_if_success: <다음 카드>
next_if_failure: <다음 카드>
artifact:      <commit / config hash / 결과 JSON 경로>
```

- **모든 임계는 숫자다.** "개선되면"·"근처로"·"현재"는 임계가 아니다.
- **구현자는 모호한 정의를 임의 해석하지 않는다.** 서술형 항목이 하나라도 있으면
  실행하지 말고 **BLOCKED 로 반환한다. 이것은 실패가 아니라 계약 준수다.**
  반환 보고에는 모호한 항목과 **가능한 해석 후보들**을 적는다.
  근거: KAGRI-016 이 정확히 이 행동을 했고, 그 판단이 옳았다.
- 카드가 정의를 바꾸면(예: cap 규칙 변경) **이전 규칙으로 측정한 결과와 같은 표에 올리지 않는다.**
  규칙이 다르면 다른 실험이다.

- 같은 seed, **양 좌석 교대** 페어드 비교.
- **표본 수를 결과 보고 늘리지 않는다.** 좋아 보일 때 멈추지 않는다.
- 승률만 보지 않는다. 승/무/패 + 신뢰구간 + 큰 패배 빈도 + 무음 실패 카운터를 함께 본다.
- **상대별 non-inferiority**를 본다. 평균이 올라도 특정 강자에게 지기 시작하면 손해다.
- 모든 에이전트가 읽을 수 있는 seed는 blind가 아니라 **재사용 holdout**이다.
  진짜 blind는 코드 동결 후 사람이 새로 생성하고, 집계 후 재사용하지 않는다.

---

## 6. 런타임 계약

- 진입점은 `main.py`의 `agent(obs)`. 다중 파일은 **루트에 `main.py`가 있는 tar.gz**.
- 런타임 파일 위치는 `/kaggle_simulations/agent/`이고
  **Kaggle 로더는 `__file__`을 정의하지 않는다.** CWD 상대경로에 의존하지 않는다.
- 평가 중 **네트워크 금지**. 런타임 원격 LLM 금지.
- **어떤 상태에서도 합법 액션을 반환한다. 절대 raise하지 않는다.**
- 제약은 **단일 지점에서만** 강제한다 (시장 주문 개수 등을 여러 곳에 흩지 않는다).
- 자원: 제출 100 MiB · RAM 6.5 GiB · **vCPU 1.6**.
  vCPU가 1.6이므로 numpy 스레드를 1로 고정하고 턴당 할당을 최소화한다.
- **★ 시간 예산 세 개는 독립이 아니다.**
  턴 1s · overage 60s · **에피소드 1,200s**(`kaggriculture.json` 에 `runTimeout` 정의가 없어
  framework default 상속). `episodeSteps=720` 은 **719회의 agent call** 을 만드므로
  에이전트당 nominal 상한은 `719 × 1s + 60s = 779s`, **두 에이전트 합 1,558s > 1,200s** 다.
  로컬 `env.run()` 은 순차 호출한다(UrlAgent 만 병렬).
  → **양쪽이 모두 느리면 턴 타임아웃이 아니라 에피소드가 먼저 죽는다.**
  내부 deadline 은 턴 1s 가 아니라 **에피소드 예산 ÷ 719** 기준으로 잡는다.
  hosted 스케줄링 경로는 `[N/A]` — 로컬로 증명되지 않는다.

---

## 7. 승격 게이트

`plan/`의 최신 마스터 플랜 승격 게이트를 따른다. **하나라도 실패하면 제출 금지.**

### 7.1 검증 상대 — 자기 자신이 아니라 사다리다 `[2026-09-07 개정]`

**직전 버전 대비 우위는 승격 근거가 아니다.** v1 vs v0 를 이기는 것은
자기 학습 데이터로 검증하는 것과 같다. 우리가 근사해야 하는 것은 리더보드이지
어제의 우리가 아니다.

승격 판정의 1차 지표는 **`opponents/public/` 상위 봇 4개 상대 페어드 점수**다.
직전 버전 대비 비교는 *진단*으로만 쓴다.

증거: rayk 사례(K5) — 자가대전 83승 5패, 평균 마진 +14,196 인데 hosted 레이팅 3000 미만.
우리 v0 도 로컬에서 starter 를 5배 차로 이겼지만 hosted 레이팅 337.2, 6,989위였다.
**로컬 우위와 사다리 우위는 상관관계가 확인되기 전까지 별개의 양이다.**

새 버전을 만들 때마다 다음을 기록한다:
`(로컬 v_n vs v_{n-1} 점수, 공개봇 4종 상대 점수, hosted 레이팅)` 삼중쌍.
세 번째 열이 채워지는 대로 앞 두 열과의 상관을 확인한다.
**상관이 깨지면 로컬 지표를 고치는 것이 다음 실험이다. 전략 튜닝이 아니라.**

### 7.1b 지표 포화 — 게이트가 0을 돌려줄 때 `[2026-09-09 추가]`

후보와 parent 가 **둘 다** 4봇 상대 0/0/N 이면 페어드 점수는 정보가 없다.
KAGRI-015 에서 실제로 이 일이 일어났다(둘 다 0/0/400).
격차가 큰 동안에는 승격 게이트가 **탐색 신호로 쓸 수 없다.**

그래서 지표를 두 층으로 나눈다.

| 층 | 용도 | 지표 |
|---|---|---|
| 탐색 | 후보 선택 | **4봇 상대 우리 평균 최종 뱅크** (과 그 마진) |
| 승격 | 제출 여부 | 4봇 상대 페어드 점수 95% CI 하한 > 0.5 (불변) |

- 탐색 층에서 전진했으면 **승격 실패라도 다음 카드의 parent 로 채택한다.**
  "실패"는 *더 나빠졌을 때*를 뜻하지 *아직 못 이긴 것*을 뜻하지 않는다.
- 탐색 층 수치를 근거로 **제출하지 않는다.** 승격 층은 그대로다.
- 페어드 점수가 0/1 에서 벗어나기 시작하면 탐색 층을 폐기하고 승격 층 하나만 본다.

### 7.2 지표는 마진이 아니라 W/D/L 이다

레이팅은 승·무·패만 본다. 코인 마진은 레이팅에 기여하지 않는다.
따라서 **분산 축소가 기댓값 극대화보다 우선한다.**
1코인 차로 60% 이기는 전략이 5만 코인 차로 55% 이기는 전략보다 낫다.

- 승격 1차 지표: 페어드 점수와 그 95% CI 하한
- `mean_margin` 은 **진단 전용**이다. 승격 근거로 인용하지 않는다
- `big_losses_gt_10k` 대신 **패배 횟수 자체**와 패배의 분산을 본다

### 7.3 집계로 승격하고, 개별 패배로 설계한다

집계 승률은 *졌다는 사실*만 알려준다. **왜 졌는지는 `tools/postmortem.py` 로 본다.**

새 후보를 만들기 전에 **직전 버전이 공개 상위 봇에게 진 게임 최소 1판**을
`tools/postmortem.py` 로 열어 분기일과 최악의 날을 확인한다.
그 결과를 실험 카드의 `hypothesis` 근거로 인용한다.
**postmortem 인용 없는 실험 카드는 사전등록으로 인정하지 않는다.**

### 7.4 기존 조항

- 로컬 결과만으로 hosted 우위를 주장하지 않는다.
- **exact artifact SHA-256과 registry 기록 없이 제출하지 않는다.**
- 제출이 은퇴시키는 에이전트가 잃는 경기 이력을 명시하고, 그래도 이득인지 기록한다.
- **활성 슬롯 2개는 같은 전략의 두 버전이 아니라 서로 다른 두 전략이어야 한다.**
  최종 평가가 두 슬롯을 모두 쓰므로, 상관된 두 제출은 슬롯 하나를 버리는 것이다.
  **"다르다"의 정의 `[2026-09-09]`**: 같은 시드·좌석·상대에서 두 후보의 **승패 패턴 상관**을 잰다.
  같이 이기고 같이 지면 슬롯 하나다. 지는 경기가 겹치지 않아야 두 슬롯이다.
  기본 조합은 **안정형 incumbent + 시장/상대 반응형 challenger**.
- 동점 시 **먼저 제출한 쪽이 승자**다(`docs/official/rules.md`). 강도가 비슷한 두 후보라면
  **제출 순서 자체가 tiebreak** 이므로, 어느 쪽을 먼저 올릴지 근거를 남긴다.

### 7.5 릴리스 전 체크리스트 — 6줄 `[2026-09-09 추가]`

**릴리스 보고서에 아래 여섯 줄을 그대로 복사해 채운다. 빈 줄이 있으면 제출 금지.**

```
Identity:  제출 파일 SHA-256 = 성능을 측정한 파일 SHA-256 인가?      [ ]
Schema:    루트 main.py / agent(obs) / hands 길이 정렬 / 절대 raise 안 함  [ ]
Runtime:   에피소드 예산(§6)의 70~80% 이내인가? p99 턴 지연 기록      [ ]
Isolation: 빈 폴더 clean-room 에서 tar 풀고 import 성공했는가?        [ ]
License:   외부 코드·상대 봇·데이터의 라이선스가 Rules 를 만족하는가?   [ ]
Ledger:    submission ID ↔ artifact SHA ↔ 에피소드를 연결했는가?       [ ]
```

`Ledger` 는 제출 **후**에만 채울 수 있다. 나머지 다섯은 **제출 전**에 채운다.

---

## 8. 외부 행동

**Kaggle 제출 · 팀 변경 · 코드 공개는 사람 승인 없이 실행하지 않는다.**

- 외부 코드·데이터를 쓰면 `environment/LICENSES.md` 또는 `opponents/README.md`에
  URL · 저자 · 라이선스 · 수집일 · 엔진 버전을 기록한다.
- 수상 시 제출물과 **그 생성에 쓴 소스 전부**를 CC-BY 4.0으로 공개해야 한다.
- 팀 밖으로 우리 코드를 사적으로 공유하면 **실격**이다.
- **우리 리플레이는 공개된다.** 비밀 전략을 전제로 설계하지 않는다.

---

## 9. 실패의 범위

`구체 구현 실패` / `운영 결정` / `넓은 전략 가설`을 분리한다.
한 구현이 실패해도 전략 전체를 죽이지 않는다.

`evidence/KILLS.md`의 항목에는 **엔진 버전 · 상대군 · 구현 · 실패면 · 재검토 조건**을 함께 적는다.
조건 없는 영구 금지는 없다.

**KILL 부활 차단 `[2026-09-09 추가]`**

- KILL 항목은 **그 항목의 재검토 조건을 명시적으로 인용하지 않고는** 실험 카드의
  `hypothesis` 나 `one_change` 가 될 수 없다.
- 재검토 조건이 성립했다는 근거는 **`[ENGINE]` 또는 `[HOSTED]`** 여야 한다. `[LOCAL]` 단독 불가.
- "실험해서 이기면 열자"는 재검토 조건이 아니다. 그건 KILL 을 없던 일로 만드는 문장이다.
- 외부 문서·가이드가 KILL 된 항목을 권해도 그 자체로는 재검토 사유가 아니다.
  그 문서는 우리 실험 기록을 안 본 것이다.

---

## 10. 핸드오프

### 10.1 사람에게 설명하는 형식 `[2026-09-14 추가]`

모든 agent는 중간 갱신·완료 보고의 첫 부분을 비전공자도 이해할 수 있게 아래 순서로 쓴다.

1. **무엇을 바꾸거나 시험하는가**
2. **왜 하는가**
3. **무엇을 측정했고 결과가 어땠는가** — 아직 측정하지 않았으면 `N/A`
4. **무엇이 막혀 있고 다음 행동은 무엇인가**

짧고 구체적인 문장을 쓰되, 전문용어는 억지로 번역하지 않는다. 이 요약 아래에는 기존의
증거 꼬리표·수치·exact path·SHA-256·재현 명령을 생략하지 않고 이어서 기록한다.

```
VERDICT | 핵심 사실 2개 | exact path + SHA-256 | 실행한 검증과 결과 | NEXT ACTION
```

**파일이 곧 채널이다. 별도 메시지 버스는 쓰지 않는다.**

- 완료 보고: `coordination/reports/<나>/YYYYMMDD-HHMM-<task_id>.md` — **한 건 한 파일**
- 소유 경로 밖 변경 제안: `coordination/proposals/<나>/`
- 작업 원장: `coordination/TASKS.md` 에 자기 행만 추가
- 공유 파일에 **동시 append 금지**
- 가설·공개 주장·실험 결과 변경: `tools/update_hypotheses.py`로 자기 event를 쓰고 공용 원장을 갱신

상태는 `TASKS.md` 의 상태 칸으로 표현한다: `미착수 → 진행중 → 검토중 → DONE` 또는 `BLOCKED`.
상세는 `coordination/README.md`.

---

## 11. 세션 시작·종료 절차

**시작**
0. **`coordination/BOARD.md` 의 갱신일을 먼저 본다.** 오늘과 **2일 이상** 벌어졌거나,
   `evidence/HOSTED_LEDGER.md` 의 최신 제출 상태와 어긋나면
   **작업을 시작하기 전에 코디네이터에게 반환한다.**
   근거: BOARD 가 2026-09-06 에 멈춰 "제출 0회"라고 적힌 채 사흘이 갔다. 그 사이 v0 를 제출했고
   레이팅 337.2 를 받았다. 모두가 첫 번째로 읽는 문서가 틀린 상태였다.
1. `coordination/BOARD.md` 읽기 — 지금 무엇이 중요한가
2. `HYPOTHESES.md` 읽기 — 이미 제기·검증한 주장과 중복 여부
3. `evidence/FACTS.md` + `evidence/KILLS.md` 읽기 — 이미 아는 것, 이미 죽은 것
4. `coordination/reports/` 의 최근 보고 확인
5. 내 소유 경로를 CLAIM

**종료**
1. 바뀐 것을 소유 경로에 커밋
2. `coordination/reports/<나>/` 에 보고 한 파일
3. 새로 확인한 사실은 **재현 명령과 함께** `evidence/FACTS.md`에
4. 가설 관련 작업이면 event 기록 후 `python3 tools/validate_hypotheses.py --strict`

---

## 12. 자주 쓰는 명령

```bash
# 엔진 검증
python3 scripts/verify_engine_facts.py

# 로컬 대전
python3 -c "
from kaggle_environments import make
e = make('kaggriculture', configuration={'episodeSteps':720,'seed':7}); e.run(['main.py','starter'])
print([round(s.reward) for s in e.steps[-1]], [s.status for s in e.steps[-1]])"

# 페어드 아레나 (양 좌석 교대)
python3 tools/arena.py --a main.py --b opponents/public/<bot>.py --seeds 200 --both-seats

# 릴리스 빌드와 clean-room 검증
tar -czf releases/<id>/submission.tar.gz main.py src/
shasum -a 256 releases/<id>/submission.tar.gz
mkdir -p /tmp/cr && tar -xzf releases/<id>/submission.tar.gz -C /tmp/cr && (cd /tmp/cr && python3 -c "import main; print(main.agent)")

# 제출 (사람만)
kaggle competitions submit kaggriculture -f releases/<id>/submission.tar.gz -m "<msg>"
kaggle competitions submissions kaggriculture
kaggle competitions episodes <SUBMISSION_ID>
kaggle competitions replay <EPISODE_ID> -p private_artifacts/replays
kaggle competitions logs <EPISODE_ID> 0 -p private_artifacts/logs
```
