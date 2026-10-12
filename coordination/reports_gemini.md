# coordination/reports/gemini — 10개 문서 묶음

원본 파일을 파일명(시간) 순으로 이어 붙였다. 각 절 제목이 원래 경로다.


---

## `reports/gemini/20260907-1440-KAGRI-006.md`

# KAGRI-006 완료 보고 — 공개 상위 봇 4개 확보 및 독립 검증

- 작성일시: 2026-09-07 14:40 (KST)
- 작성자: Gemini
- 관련 태스크: KAGRI-006 (`coordination/proposals/gemini/BRIEF_opponents.md`)

---

## 1. VERDICT
**SUCCESS** — `docs/code/`의 4개 공개 노트북에서 에이전트를 AST/안전 파싱 방식으로 추출하여 `opponents/public/`에 4개 독립 봇 확보 완료. `kaggle-environments==1.32.7` 엔진 샌드박스 내부에서 4개 봇 모두 720턴 완주 (`status=['DONE', 'DONE']`, `exc=0`, 리워드 105k~136k), `tools/arena.py` 페어드 대전 연동 정상 동작 확인.

## 2. 핵심 사실 2개
1. **[LOCAL] Kaggle CLI / 네트워크 불필요**: 타깃 4개 노트북은 이미 `docs/code/`에 온전히 로컬 보관되어 있었으며, 샌드박스 내 Python 3.13 환경에 `kaggle-environments==1.32.7`이 정상 설치되어 있어 외부 네트워크 호출 없이 100% 로컬 샌드박스(`BypassSandbox: false`) 안에서 추출 및 완주 검증이 완료된다.
2. **[OFFICIAL] 라이선스 및 안전성**: Kaggle 대회 공식 규정 §7.b에 의해 공개 노트북 공유 코드는 상업적 제한 없는 OSI-approved 오픈소스(Kaggle 기본 Apache-2.0) 라이선스를 적용받으므로 벤치마크 상대로 합법적 사용이 가능하며, 노트북 셀의 `WORK = Path.cwd()` 직접 실행 시 발생할 수 있는 `main.py` 덮어쓰기 위험을 회피하는 AST 기반 안전 추출 파이프라인을 구축했다.

## 3. path + SHA-256
| 파일 | 크기(bytes) | SHA-256 | 출처 노트북 및 원작자 |
|---|---|---|---|
| `opponents/public/boatlee.py` | 18,946 | `f029fa0cb66a9eb509afbe44e3f59b800332d0419db91607183410e4089c4d19` | boatlee (v16-rc5) |
| `opponents/public/kaitofukami.py` | 20,813 | `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8` | kaitofukami (v27 midgame reset) |
| `opponents/public/raykkretzschmar.py` | 75,098 | `489f5d197527f107027626cce79d850fd2ca90edd43d94384b849b6511e27bdb` | raykkretzschmar (최종 C95 artifact) |
| `opponents/public/lynnsakurai.py` | 46,342 | `1dc166ae2bf0c56a44fac4482f469b8812968c4cb32459cb9860f5077897a7d4` | lynnsakurai (Farming Score) |

## 4. 실행한 검증과 결과
1. **720턴 완주 검증 (`tools/instrument.py --a opponents/public/<bot>.py --b starter --seeds 7`)**:
   - `boatlee.py`: rewards=[125139, 3536], status=['DONE', 'DONE'], steps=720, wall=2.9s, exc=0
   - `kaitofukami.py`: rewards=[105679, 3560], status=['DONE', 'DONE'], steps=720, wall=4.0s, exc=0
   - `raykkretzschmar.py`: rewards=[136062, 3536], status=['DONE', 'DONE'], steps=720, wall=4.0s, exc=0
   - `lynnsakurai.py`: rewards=[118292, 3431], status=['DONE', 'DONE'], steps=720, wall=4.3s, exc=0
2. **페어드 아레나 연동 검증 (`tools/arena.py --a main.py --b opponents/public/boatlee.py --seeds 1`)**:
   - 2경기(양 좌석) 실행 완료, 9.0s 소요, status 전부 정상, 에러 0. (v0 대패 확인: 마진 -95,332)

## 5. 상위 봇 전략 실측 프로파일링 (v1/v2 설계 직접 기여)
재현: `seed=7`에서 4개 봇 vs starter 시뮬레이션 후 액션 트레이스 계측

| 분석 항목 | `boatlee` (v16-rc5) | `kaitofukami` (v27) | `raykkretzschmar` (C95) | `lynnsakurai` (Math) | v0와의 차이 및 시사점 |
|---|---|---|---|---|---|
| **최종 리워드 (코인)** | **125,139** | **105,679** | **136,062** | **118,292** | v0(~17,000) 대비 **6~8배** 압도적 격차 |
| **땅 매입 턴 (BUY_LAND)** | **step 161, 241** (Day 6, 10) | **step 161, 241** (Day 6, 10) | **step 161, 241** (Day 6, 10) | **step 151, 266** (Day 6, 11) | **전원 정확히 3구획까지만 확장**. 4번째 구획($4k)은 전원 미구매 (K1 영구 KILL 재확인) |
| **최대 일꾼 수 (hands)** | **14명** | **14명** | **14명** | **12명** | v0는 4명 고정(유휴 41%). 상위 봇은 경제 규모에 맞춰 **12~14명까지 동적 증원** |
| **동물 구성 (소/양/거위)** | **COW 8, SHEEP 4, GOOSE 0** | **COW 9, SHEEP 4, GOOSE 0** | **COW 10, SHEEP 4, GOOSE 0** | **COW 9, SHEEP 8, GOOSE 0** | **거위(GOOSE)는 전원 0마리 채택 안 함.** 전원 **소 8~10마리 + 양 4~8마리** 극대화 |
| **시장 매도 (SELL)** | 비료(5단위 주기적 매도), 우유, 양털 | 비료 5단위, 밀 17단위 등 | 비료 5단위, 밀 17단위 등 | 밀 다수 분할 매도 | 매일 비료 5단위를 $100 고정가에 선점 매도하여 일일 현금 흐름 창출 |

## 6. NEXT ACTION
- **Codex**: 확보된 `opponents/public/` 상위 봇들을 상대로 `tools/arena.py`를 실행하여 현재 진행 중인 v1(면적 확장) 에이전트의 페어드 벤치마크 평가 및 승격 판단 진행.
- **Cowork**: `environment/LICENSES.md`에 추출된 4개 공개 봇에 대한 Apache-2.0 라이선스 출처 행 반영 완료.

## 7. 리스크
- 공개 노트북의 에이전트 코드는 공개 시점의 최상위 전략이지만, 리플레이 헌팅 등에 의한 과적합(replay memoization) 요소가 포함되어 있을 수 있음.
- 따라서 상대 모델링 및 심층 메타 분석 시에는 공개 코드 단독이 아닌 hosted 리플레이 행동 테이프와의 교차 검증을 병행해야 함.



---

## `reports/gemini/20260907-1621-KAGRI-014-TaskA.md`

VERDICT | CLEAN (No Errors), but Critical Seat Bias & No-ops found

핵심 사실 2개:
1. `status` 에 ERROR나 TIMEOUT은 없으며, 모든 에피소드가 정상 종료(DONE)됨. (턴당 소요 시간도 1초를 넘지 않아 Overage time이 깎이지 않음).
2. **로컬과 달리 호스트 환경에서 no-op 비율이 21.6% (1558 / 7190)** 에 달함. 또한 좌석 편향이 심각함 (Player 0일 때 4승 0패, Player 1일 때 1승 5패).

exact path + SHA-256:
- `~/kaggle/Kaggriculture/private_artifacts/replays/own/*.json` (10개 에피소드)
- (다운로드한 파일들에 대해 일괄 검증 진행)

실행한 검증과 결과:
`kaggle competitions episodes 56068891` 를 통해 최근 10판을 다운로드하고 분석 스크립트를 돌려 다음 결과를 얻음.
- `status` 에 ERROR / TIMEOUT 이 있는가: 없음 (0건)
- 우리 최종 뱅크 분포: [15427.0, 16104.0, 16211.0, 16471.0, 16748.0, 17080.0, 18053.0, 18230.0, 18249.0, 25172.0] (대부분 1.5만~1.8만 사이로 로컬 1.7만 대와 유사하나, 일부 2.5만 등 튀는 값 있음)
- 상대 최종 뱅크: [5777.0, 5957.0, 6331.0, 9806.0, 13868.0, 17520.0, 20798.0, 29189.0, 29621.0, 42295.0]
- 우리 액션 중 no-op 비율: 21.6% (1558 / 7190 actions) -> 로컬 0과 다르게 호스트에서 심각한 차이 존재
- 좌석(player 0/1)별 승률 차: Player 0 (4승 0패), Player 1 (1승 5패) -> Player 1일 때 치명적인 버그가 있는 것으로 보임
- 턴당 소요 시간 최댓값: <= 1s (Overage time 감소 없음)

NEXT ACTION:
- Task B (상위 봇 에피소드 추출) 진행
- Player 1 좌석일 때의 버그 원인 파악 및 No-op(PASS만 있는 액션)이 발생하는 호스트 환경 차이 디버깅


---

## `reports/gemini/20260908-1636-KAGRI-015-TaskC.md`

# Task C: Top Teams Replay Analysis

Analyzed **47** team instances from 29 replays.

## 1. BUY_LAND First Turn Distribution
- No BUY_LAND actions found.

## 2. Max Workers
- Average Max Workers per Episode: 0.0
- Absolute Max Workers seen: 0

## 3. BUY_ANIMAL Distribution
- No animals bought.

## 4. BUILD_COOP vs BUILD_PASTURE
- Coops Built: 0
- Pastures Built: 0

## 5. SELL Quantities and Orders
- Average SELL Orders per episode: 0.0



---

## `reports/gemini/20260908-1643-KAGRI-015-TaskC.md`

# Task C: Top Teams Replay Analysis

Analyzed **47** team instances from 47 tapes.

## 1. BUY_LAND First Turn Distribution
- Average turn: 141.7
- Median turn: 151

## 2. Max Workers
- Average Max Workers per Episode: 12.1
- Absolute Max Workers seen: 14

## 3. BUY_ANIMAL Distribution
- COW: 388 (50.4%)
- SHEEP: 319 (41.4%)
- GOOSE: 63 (8.2%)

## 4. BUILD_COOP vs BUILD_PASTURE
- Coops Built: 111
- Pastures Built: 711
- Ratio (Coop/Pasture): 0.16

## 5. SELL Quantities and Orders
- Average SELL Quantity per order: 726.7
- Average SELL Orders per episode: 265.9



---

## `reports/gemini/20260908-1646-KAGRI-014.md`

# KAGRI-014 - 리플레이 수집 및 분석 완료 보고

VERDICT | SUCCESS |
|---|---|
| **핵심 사실 1** | 상위 10팀의 리플레이 47건을 분석한 결과, 평균 141.7 턴(중앙값 151)에 첫 땅(BUY_LAND)을 구매하며, 평균 최대 일꾼 수는 12.1명입니다. |
| **핵심 사실 2** | 상위 팀들은 비용이 0인 BUILD_PASTURE(목초지)를 적극적으로 건설(평균 15개/팀)하며, 가축 구매는 소(COW, 50.4%)와 양(SHEEP, 41.4%)에 집중하고 거위(GOOSE)는 거의 사지 않습니다. |
| **파일 경로** | `coordination/reports/gemini/20260908-1643-KAGRI-015-TaskC.md` (상세 지표) 및 `private_artifacts/tapes/*.json` |
| **SHA-256** | `shasum -a 256 coordination/reports/gemini/20260908-1643-KAGRI-015-TaskC.md` |

## 실행한 검증과 결과
- **Task A**: 우리 팀 리플레이 10판 분석 완료 (이전 세션 보고 완료: `20260907-1621-KAGRI-014-TaskA.md`).
- **Task B**: Kaggle Kernel (`arki13/kaggriculture-top-episodes-grep`) 을 실행하여 `kaggle-environments` 의 방대한 21GB 로그 중 상위 10팀의 최근 에피소드 ID 40개를 추출 후, `kaggle competitions replay` 로 안전하게 로컬 다운로드 완료 (API 제한 속도 2초 간격 준수).
- **Task C**: 다운로드된 40개 리플레이 중 유효한 29개 리플레이(47개의 팀 시점)를 분석하여 `private_artifacts/tapes/` 에 JSON 테이프로 추출하고 5가지 주요 지표(BUY_LAND 시점, 일꾼 수, 동물 선호도, 목초지/닭장 비율, 평균 SELL 수량)를 집계했습니다.
- **주요 발견**:
  - `BUY_LAND`는 보통 140~150턴 사이에 처음 일어납니다.
  - 상위 팀의 최대 일꾼 수(Max Workers)는 12~14명으로 매우 높습니다 (우리 팀은 no-op가 많았음).
  - 동물은 COW와 SHEEP만 압도적으로 구매하며, GOOSE의 비중은 매우 낮습니다(8.2%).
  - `BUILD_PASTURE`(목초지) 건설이 `BUILD_COOP`(닭장)보다 훨씬(약 6배 이상) 많습니다.

## NEXT ACTION
- (Claude) `coordination/reports/gemini/20260908-1643-KAGRI-015-TaskC.md`와 본 보고서를 참고하여 v2 에이전트의 구체적 전략(가축 선호도, 일꾼 수 확장 시기 등)을 계획할 것.
- (Codex) `action` JSON 형태가 `{ "farmer": [...], "hands": [...], "market": [...] }` 구조임이 확인되었으므로 `main.py` 리팩토링 시 이를 반영하여 합법적인 액션만을 반환하도록 보완할 것.
fe8d35337fedd5719e7baf748a3260114db5d0d5eb84452edf3b1b83ab22ffff  coordination/reports/gemini/20260908-1643-KAGRI-015-TaskC.md


---

## `reports/gemini/20260910-1750-KAGRI-014.md`

# VERDICT: [LOCAL] 리더보드 스냅샷 및 리플레이 수집 완료

- KAGRI-014 정찰 루틴 실행
- 리더보드 팀 수: 8481팀
- 경로: 
  - `private_artifacts/leaderboard/snapshots.csv`
  - `private_artifacts/leaderboard/latest_top10.txt`
  - `private_artifacts/leaderboard/episodes.csv`
  - `private_artifacts/replays/top/*.json`
  - `private_artifacts/tapes/*.json`
- 실행한 검증과 결과: `kaggle` CLI로 리더보드 스냅샷 및 상위 10팀의 최근 에피소드 다운로드, 파싱 완료
- NEXT ACTION: Cowork가 아래 데이터를 분석해 KILLS나 실험 카드를 업데이트할 것

## Task 1 — 리더보드 일일 스냅샷
우리 레이팅/순위 (Sian): 2026-09-10,7400,Sian,327.6

## Task 2 — 상위 봇 리플레이 분석

### 팀: Himanshu Kumar (8 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 90414 / 92001 |
| `BUY_LAND` 발행 step | 평균 2.0 구획 (평균 step: 208) |
| 최대 동시 일꾼 수 / 도달 step | 11.2 명 / 283 step |
| `BUY_ANIMAL` 내역 | COW: 5.6마리, SHEEP: 5.0마리, GOOSE: 1.5마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1107.4, HARVEST: 474.4, PLANT: 238.9, SELL: 411.4, CARE: 412.4, FEED: 319.4, COLLECT_FERTILIZER: 368.5, FERTILIZE: 72.5, PICKUP: 190.6, PLACE: 101.4, DIG: 35.1, 이동: 2857.5, PASS: 528.6 |
| 품목별 판매 총량 | WHEAT: 19209.2, FERTILIZER: 11351.2, WOOL: 7893.2, MILK: 8390.4, MELON: 6197.0, EGG: 8194.2, STRAWBERRY: 7153.1, CARROT: 18170.0, TOMATO: 6125.0 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 244.4 턴 / 225.3 개 |


### 팀: Otter Vibe (5 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 95995 / 91944 |
| `BUY_LAND` 발행 step | 평균 2.0 구획 (평균 step: 183) |
| 최대 동시 일꾼 수 / 도달 step | 14.2 명 / 457 step |
| `BUY_ANIMAL` 내역 | SHEEP: 3.6마리, GOOSE: 3.6마리, COW: 4.6마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1010.2, HARVEST: 537.8, PLANT: 212.0, SELL: 239.8, CARE: 377.6, FEED: 411.4, COLLECT_FERTILIZER: 371.8, FERTILIZE: 190.6, PICKUP: 327.0, PLACE: 20.8, DIG: 40.4, 이동: 2852.8, PASS: 604.6 |
| 품목별 판매 총량 | FERTILIZER: 238.4, EGG: 254.2, WHEAT: 368.8, WOOL: 135.4, CARROT: 184.8, MILK: 171.6, MELON: 100.8, STRAWBERRY: 187.8, TOMATO: 116.8 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 85.4 턴 / 7.3 개 |


### 팀: SpaTaro (5 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 96454 / 94606 |
| `BUY_LAND` 발행 step | 평균 3.6 구획 (평균 step: 149) |
| 최대 동시 일꾼 수 / 도달 step | 11.6 명 / 366 step |
| `BUY_ANIMAL` 내역 | COW: 7.6마리, SHEEP: 3.8마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1247.4, HARVEST: 452.0, PLANT: 273.2, SELL: 319.2, CARE: 270.0, FEED: 266.8, COLLECT_FERTILIZER: 320.0, FERTILIZE: 111.0, PICKUP: 128.8, PLACE: 19.0, DIG: 25.4, 이동: 2836.8, PASS: 1021.8 |
| 품목별 판매 총량 | WHEAT: 905.8, FERTILIZER: 223.0, CARROT: 180.0, WOOL: 142.8, MILK: 216.4, MELON: 85.4, STRAWBERRY: 262.6 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 250.2 턴 / 6.3 개 |


### 팀: Unknown Mother-Goose (7 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 96491 / 89780 |
| `BUY_LAND` 발행 step | 평균 2.0 구획 (평균 step: 142) |
| 최대 동시 일꾼 수 / 도달 step | 12.0 명 / 306 step |
| `BUY_ANIMAL` 내역 | COW: 1.3마리, SHEEP: 8.0마리, GOOSE: 3.1마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1040.6, HARVEST: 479.4, PLANT: 249.1, SELL: 268.9, CARE: 302.0, FEED: 322.7, COLLECT_FERTILIZER: 384.6, FERTILIZE: 169.4, PICKUP: 199.1, PLACE: 122.3, DIG: 39.7, 이동: 3135.4, PASS: 1023.3 |
| 품목별 판매 총량 | FERTILIZER: 406.1, WHEAT: 502.6, WOOL: 240.3, MILK: 178.0, MELON: 113.7, STRAWBERRY: 233.6, TOMATO: 82.0, CARROT: 228.0, EGG: 126.3 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 188.7 턴 / 7.9 개 |


### 팀: Yusuke Hayashi (5 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 108942 / 111073 |
| `BUY_LAND` 발행 step | 평균 2.0 구획 (평균 step: 208) |
| 최대 동시 일꾼 수 / 도달 step | 11.2 명 / 270 step |
| `BUY_ANIMAL` 내역 | COW: 5.6마리, SHEEP: 5.0마리, GOOSE: 1.6마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1108.6, HARVEST: 475.6, PLANT: 239.0, SELL: 410.2, CARE: 413.0, FEED: 367.0, COLLECT_FERTILIZER: 375.6, FERTILIZE: 65.2, PICKUP: 191.2, PLACE: 100.0, DIG: 35.0, 이동: 2861.0, PASS: 440.0 |
| 품목별 판매 총량 | WHEAT: 18794.0, FERTILIZER: 11951.6, WOOL: 7283.8, MILK: 8469.8, MELON: 6272.0, EGG: 8276.0, STRAWBERRY: 7662.8, CARROT: 17248.0, TOMATO: 6200.0 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 252.6 턴 / 224.7 개 |


### 팀: binghua (14 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 88524 / 90444 |
| `BUY_LAND` 발행 step | 평균 2.0 구획 (평균 step: 191) |
| 최대 동시 일꾼 수 / 도달 step | 12.0 명 / 337 step |
| `BUY_ANIMAL` 내역 | COW: 7.1마리, SHEEP: 5.1마리, GOOSE: 0.9마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1110.3, HARVEST: 469.9, PLANT: 239.9, SELL: 260.7, CARE: 348.1, FEED: 342.2, COLLECT_FERTILIZER: 361.6, FERTILIZE: 101.1, PICKUP: 170.8, PLACE: 118.1, DIG: 39.9, 이동: 3303.1, PASS: 710.7 |
| 품목별 판매 총량 | FERTILIZER: 339.8, WHEAT: 398.3, WOOL: 199.1, MILK: 276.4, MELON: 72.4, EGG: 38.4, STRAWBERRY: 331.6, CARROT: 115.1, TOMATO: 18.9 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 192.9 턴 / 6.9 개 |


### 팀: feel the agi (9 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 106938 / 100056 |
| `BUY_LAND` 발행 step | 평균 2.0 구획 (평균 step: 208) |
| 최대 동시 일꾼 수 / 도달 step | 12.3 명 / 354 step |
| `BUY_ANIMAL` 내역 | COW: 6.0마리, SHEEP: 4.2마리, GOOSE: 3.3마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1018.0, HARVEST: 518.6, PLANT: 238.1, SELL: 262.7, CARE: 385.8, FEED: 402.4, COLLECT_FERTILIZER: 368.2, FERTILIZE: 156.2, PICKUP: 248.8, PLACE: 68.1, DIG: 26.6, 이동: 3032.7, PASS: 626.0 |
| 품목별 판매 총량 | WHEAT: 533854.1, FERTILIZER: 89158.0, WOOL: 200178.3, MILK: 200218.3, MELON: 88960.9, EGG: 89064.3, STRAWBERRY: 89117.2, CARROT: 200136.3, TOMATO: 88897.9 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 158.3 턴 / 6013.7 개 |


### 팀: kanno (8 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 103668 / 106297 |
| `BUY_LAND` 발행 step | 평균 2.0 구획 (평균 step: 208) |
| 최대 동시 일꾼 수 / 도달 step | 11.6 명 / 343 step |
| `BUY_ANIMAL` 내역 | COW: 5.0마리, SHEEP: 6.2마리, GOOSE: 0.8마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1104.8, HARVEST: 473.0, PLANT: 238.8, SELL: 464.9, CARE: 405.1, FEED: 369.2, COLLECT_FERTILIZER: 370.5, FERTILIZE: 61.0, PICKUP: 169.0, PLACE: 105.1, DIG: 35.2, 이동: 2918.9, PASS: 576.1 |
| 품목별 판매 총량 | WHEAT: 19961.5, FERTILIZER: 13347.6, WOOL: 8248.8, MILK: 8646.2, MELON: 6447.0, EGG: 8434.6, STRAWBERRY: 8881.8, CARROT: 17423.0, TOMATO: 6375.0 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 258.6 턴 / 210.3 개 |


### 팀: mtmr_s1 (5 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 102358 / 101623 |
| `BUY_LAND` 발행 step | 평균 2.0 구획 (평균 step: 208) |
| 최대 동시 일꾼 수 / 도달 step | 11.2 명 / 279 step |
| `BUY_ANIMAL` 내역 | COW: 5.8마리, SHEEP: 4.6마리, GOOSE: 1.6마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1108.2, HARVEST: 473.6, PLANT: 238.8, SELL: 280.6, CARE: 413.2, FEED: 368.8, COLLECT_FERTILIZER: 367.4, FERTILIZE: 61.0, PICKUP: 191.0, PLACE: 100.2, DIG: 35.2, 이동: 2815.0, PASS: 516.0 |
| 품목별 판매 총량 | WHEAT: 294.0, FERTILIZER: 343.6, WOOL: 184.4, MILK: 234.2, MELON: 72.0, EGG: 62.4, STRAWBERRY: 247.8, CARROT: 82.2 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 193.8 턴 / 5.4 개 |


### 팀: デワンシュ (7 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 98971 / 99528 |
| `BUY_LAND` 발행 step | 평균 2.4 구획 (평균 step: 244) |
| 최대 동시 일꾼 수 / 도달 step | 11.9 명 / 316 step |
| `BUY_ANIMAL` 내역 | COW: 5.6마리, SHEEP: 5.0마리, GOOSE: 1.6마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1127.9, HARVEST: 485.3, PLANT: 241.9, SELL: 558.3, CARE: 395.9, FEED: 373.9, COLLECT_FERTILIZER: 373.6, FERTILIZE: 66.7, PICKUP: 205.3, PLACE: 100.7, DIG: 35.0, 이동: 2856.3, PASS: 421.6 |
| 품목별 판매 총량 | WHEAT: 16616.0, FERTILIZER: 8613.6, STRAWBERRY: 9585.9, WOOL: 13309.1, EGG: 9211.0, TOMATO: 10180.0, MILK: 13448.1, CARROT: 18280.0, MELON: 10222.0 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 334.6 턴 / 196.1 개 |



---

## `reports/gemini/20260916-1705-P1a-SOURCE-TRIAGE.md`

# P1a 완료 보고 — 공개 자료 판독 및 인벤토리 정밀 검토

**일시: 2026-09-16 17:05 KST · 작성자: Gemini (Antigravity)**  
**작업 ID: `P1a-SOURCE-TRIAGE`**  
**산출물: [`analysis/public_source_triage/20260916.md`](../../analysis/public_source_triage/20260916.md)**  

---

## 1. 사람에게 설명하는 핸드오프 요약

1. **무엇을 바꾸거나 시험하는가:**
   - 공개 Notebook(51개)과 Discussion(18개)의 전체 인벤토리를 확보하고, 09-16 신규 수집된 자료 및 감시 대상 14건에 대한 정밀 판독(Triage)을 완료했습니다.

2. **왜 하는가:**
   - 검증되지 않은 공개 소스의 과장 주장(예: 2200+ Elo 주장, Day 3 소 증원, R10 미숙 멜론 오판 매도 등)이 우리 전략 카드의 전제로 유입되어 연쇄 패배를 일으키는 것을 사전에 차단하기 위함입니다.

3. **무엇을 측정했고 결과가 어땠는가:**
   - `[LOCAL]` 수집 스크립트 실행(Run ID: `20260916T080012960132Z`, complete)을 통해 51개 Notebook(고유 50개)과 18개 Discussion(고유 18개)을 확보했습니다.
   - 핵심 14건 판정 결과: 채택 3건(V41 자원 도착 분리 확인 방법론, Kaito 중반 지속 진단 관점, Georgy 표본 분리 원칙), 보류 4건(R10 멜론 선점, Cow starve 가드, 741003 등), 기각 7건(Day 3 Cow challenger, 비료 버그, Specialist, 2200+ Elo baseline 등).
   - Notebook 코드는 일절 실행하지 않았으며, 새 strategy 실행 및 hosted 측정은 `N/A`입니다.

4. **무엇이 막혀 있고 다음 행동은 무엇인가:**
   - P1b (Actual parent A tar schema-3 release preflight) 및 P1c (최신 24시간 Hosted 패배 조사) 통과 전까지 신규 전략 카드 착수는 `HOLD`입니다.

```text
VERDICT | P1a 완료 · 공개 소스 51/18건 인벤토리 및 14건 판독 완료 · 결함 힌트 기각/보류 | analysis/public_source_triage/20260916.md | 수집(16건 complete) · 정적 파싱 PASS · 가설 원장 strict PASS | NEXT ACTION: P1c 패배 조사 및 P1b release preflight 확인
```

---

## 2. 세부 검증 사실 및 산출물

- **인벤토리**:
  - `docs/code/` 51개 `.ipynb` (신규 3건: `haideptry`, `kunaldesale2408`, `xuantianfengwu_day-3-cow`)
  - `docs/discussion/` 18개 `.md` (신규 2건: `736219`, `740022`)
- **결함 확인**:
  - R10 및 신규 `xuantianfengwu_day-3-cow`의 `_rival_ready_melons` 함수는 멜론 나이(`first_yield_day=10`)를 확인하지 않고 `yield_units`만 합산하여 미숙 멜론을 수확 대기물로 오판함 (`kaggriculture.py:16, 215-225, 449-462` 대조 완료).
  - `haideptry`의 2200+ Elo 주장은 초보적인 규칙형 코드에 불과함을 정적 파싱으로 확인하여 기각함.
- **가설 원장 검증**:
  - `python3 tools/validate_hypotheses.py --strict` 실행 결과: PASS (30 entries).

---

## 3. 다음 작업 (P1b, P1c)으로의 인계 사항

1. **Claude (P1c 패배 해석)**:
   - 패배 분석 체크리스트에 V41 인사이트(실제 자원 도착 여부 분리 진단: seed/food/pickup/spawn)를 반영할 것.
   - 오프닝 실패와 160턴 이후 중반 continuation 실패를 분리 진단할 것.
2. **Codex (P1b Preflight & 계측)**:
   - actual parent tar의 schema-3 release preflight manifest 고정 및 실행 대기.
   - P1b 통과 전까지 새 전략 카드 사전등록 착수 금지 (HOLD).


---

## `reports/gemini/20260916-2141-KAGRI-014.md`

# VERDICT: [LOCAL] 리더보드 스냅샷 및 리플레이 수집 완료

- KAGRI-014 정찰 루틴 실행
- 리더보드 팀 수: 9234팀
- 경로 및 SHA: N/A
- 실행한 검증과 결과: `kaggle` CLI로 리더보드 스냅샷 및 상위 10팀의 최근 에피소드 다운로드, 파싱 완료
- NEXT ACTION: Cowork가 아래 데이터를 분석해 KILLS나 실험 카드를 업데이트할 것

## Task 1 — 리더보드 일일 스냅샷
우리 레이팅/순위 (Sian): 2026-09-16,2007,Sian,1726.6

## Task 2 — 상위 봇 리플레이 분석

### 팀: DSM (7 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 126742 / 126677 |
| `BUY_LAND` 발행 step | 평균 2.7 구획 (평균 step: 194) |
| 최대 동시 일꾼 수 / 도달 step | 11.0 명 / 241 step |
| `BUY_ANIMAL` 내역 | COW: 9.0마리, SHEEP: 4.9마리, GOOSE: 1.4마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1342.0, HARVEST: 501.3, PLANT: 273.0, SELL: 3174.3, CARE: 362.3, FEED: 355.9, COLLECT_FERTILIZER: 388.3, FERTILIZE: 161.3, PICKUP: 214.0, PLACE: 124.9, DIG: 37.7, 이동: 3323.0, PASS: 57.9 |
| 품목별 판매 총량 | STRAWBERRY: 2145.7, MELON: 2244.1, MILK: 1957.6, WOOL: 1958.7, TOMATO: 2788.7, EGG: 2188.0, CARROT: 2217.0, WHEAT: 1483.6, FERTILIZER: 1218.1 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 719.0 턴 / 5.7 개 |


### 팀: Driz Lo (5 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 107940 / 100322 |
| `BUY_LAND` 발행 step | 평균 2.6 구획 (평균 step: 232) |
| 최대 동시 일꾼 수 / 도달 step | 13.0 명 / 404 step |
| `BUY_ANIMAL` 내역 | COW: 4.4마리, SHEEP: 7.4마리, GOOSE: 1.2마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1058.0, HARVEST: 484.0, PLANT: 241.0, SELL: 517.2, CARE: 399.0, FEED: 361.0, COLLECT_FERTILIZER: 409.0, FERTILIZE: 144.6, PICKUP: 201.4, PLACE: 115.4, DIG: 37.2, 이동: 3041.0, PASS: 633.4 |
| 품목별 판매 총량 | WHEAT: 6262.8, FERTILIZER: 6364.2, WOOL: 9549.8, MILK: 8912.8, MELON: 6672.0, EGG: 8689.6, STRAWBERRY: 10503.4, CARROT: 17679.0, TOMATO: 6616.0 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 293.6 턴 / 157.1 개 |


### 팀: Excluding (6 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 122050 / 120690 |
| `BUY_LAND` 발행 step | 평균 2.2 구획 (평균 step: 184) |
| 최대 동시 일꾼 수 / 도달 step | 12.7 명 / 250 step |
| `BUY_ANIMAL` 내역 | COW: 6.5마리, SHEEP: 4.2마리, GOOSE: 3.2마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1053.0, HARVEST: 499.8, PLANT: 214.3, SELL: 288.3, CARE: 316.8, FEED: 346.2, COLLECT_FERTILIZER: 397.7, FERTILIZE: 188.7, PICKUP: 296.2, PLACE: 123.7, DIG: 39.2, 이동: 3405.3, PASS: 358.8 |
| 품목별 판매 총량 | WHEAT: 369.8, FERTILIZER: 224.8, WOOL: 118.8, MILK: 214.5, MELON: 86.2, EGG: 158.7, STRAWBERRY: 262.5, TOMATO: 49.8, CARROT: 122.0 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 184.3 턴 / 5.6 개 |


### 팀: M & M & P & Q (9 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 131988 / 126118 |
| `BUY_LAND` 발행 step | 평균 2.6 구획 (평균 step: 212) |
| 최대 동시 일꾼 수 / 도달 step | 12.3 명 / 465 step |
| `BUY_ANIMAL` 내역 | COW: 4.6마리, SHEEP: 6.1마리, GOOSE: 4.1마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1251.2, HARVEST: 477.8, PLANT: 274.4, SELL: 209.0, CARE: 352.6, FEED: 391.1, COLLECT_FERTILIZER: 437.4, FERTILIZE: 221.0, PICKUP: 202.1, PLACE: 28.1, DIG: 32.3, 이동: 2583.3, PASS: 285.8 |
| 품목별 판매 총량 | FERTILIZER: 236.3, WHEAT: 359.8, CARROT: 193.6, WOOL: 188.0, EGG: 182.7, MILK: 164.3, MELON: 88.6, STRAWBERRY: 197.9, TOMATO: 70.9 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 90.1 턴 / 8.0 개 |


### 팀: Majkel1337 (6 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 132474 / 138170 |
| `BUY_LAND` 발행 step | 평균 4.3 구획 (평균 step: 169) |
| 최대 동시 일꾼 수 / 도달 step | 11.0 명 / 245 step |
| `BUY_ANIMAL` 내역 | COW: 12.0마리, SHEEP: 3.8마리, GOOSE: 1.2마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1343.7, HARVEST: 471.5, PLANT: 245.7, SELL: 378.2, CARE: 341.7, FEED: 331.5, COLLECT_FERTILIZER: 372.8, FERTILIZE: 165.7, PICKUP: 216.3, PLACE: 115.5, DIG: 36.7, 이동: 3416.3, PASS: 54.7 |
| 품목별 판매 총량 | WHEAT: 466.8, FERTILIZER: 197.2, WOOL: 142.3, MILK: 224.5, MELON: 70.8, EGG: 47.2, STRAWBERRY: 269.5, CARROT: 53.2, TOMATO: 27.0 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 279.3 턴 / 4.0 개 |


### 팀: Orbital Terraformer (9 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 101416 / 98055 |
| `BUY_LAND` 발행 step | 평균 3.8 구획 (평균 step: 201) |
| 최대 동시 일꾼 수 / 도달 step | 11.1 명 / 252 step |
| `BUY_ANIMAL` 내역 | COW: 8.7마리, SHEEP: 4.4마리, GOOSE: 1.7마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1390.9, HARVEST: 501.0, PLANT: 304.7, SELL: 548.3, CARE: 352.1, FEED: 343.6, COLLECT_FERTILIZER: 371.8, FERTILIZE: 156.9, PICKUP: 237.9, PLACE: 122.6, DIG: 33.4, 이동: 3261.0, PASS: 68.9 |
| 품목별 판매 총량 | WHEAT: 533.4, FERTILIZER: 209.9, WOOL: 158.2, MILK: 237.4, MELON: 93.4, TOMATO: 250.7, STRAWBERRY: 193.4, EGG: 126.4, CARROT: 112.6 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 333.3 턴 / 3.5 개 |


### 팀: Sida Zuo (7 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 100476 / 99844 |
| `BUY_LAND` 발행 step | 평균 2.0 구획 (평균 step: 173) |
| 최대 동시 일꾼 수 / 도달 step | 11.1 명 / 251 step |
| `BUY_ANIMAL` 내역 | COW: 5.3마리, SHEEP: 3.1마리, GOOSE: 3.9마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1084.0, HARVEST: 503.1, PLANT: 233.1, SELL: 291.7, CARE: 319.0, FEED: 321.0, COLLECT_FERTILIZER: 375.7, FERTILIZE: 151.9, PICKUP: 289.0, PLACE: 77.0, DIG: 39.0, 이동: 3089.9, PASS: 744.6 |
| 품목별 판매 총량 | FERTILIZER: 223.4, WOOL: 102.0, WHEAT: 409.0, MILK: 209.7, EGG: 164.6, MELON: 79.3, STRAWBERRY: 214.0, CARROT: 107.1, TOMATO: 52.9 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 192.4 턴 / 5.4 개 |


### 팀: SpaTaro (7 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 104345 / 98427 |
| `BUY_LAND` 발행 step | 평균 2.7 구획 (평균 step: 160) |
| 최대 동시 일꾼 수 / 도달 step | 11.4 명 / 296 step |
| `BUY_ANIMAL` 내역 | COW: 7.4마리, SHEEP: 4.6마리, GOOSE: 0.1마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1290.6, HARVEST: 444.7, PLANT: 269.6, SELL: 348.6, CARE: 273.9, FEED: 271.9, COLLECT_FERTILIZER: 303.9, FERTILIZE: 101.1, PICKUP: 139.4, PLACE: 26.3, DIG: 29.4, 이동: 2820.9, PASS: 896.6 |
| 품목별 판매 총량 | WHEAT: 895.0, FERTILIZER: 264.9, CARROT: 180.4, WOOL: 145.0, MILK: 199.3, MELON: 102.1, STRAWBERRY: 308.9 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 268.4 턴 / 6.0 개 |


### 팀: THIRD FARM CLUB (6 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 104867 / 101846 |
| `BUY_LAND` 발행 step | 평균 2.5 구획 (평균 step: 194) |
| 최대 동시 일꾼 수 / 도달 step | 13.8 명 / 338 step |
| `BUY_ANIMAL` 내역 | COW: 7.0마리, SHEEP: 4.3마리, GOOSE: 3.7마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 1091.7, HARVEST: 436.3, PLANT: 242.8, SELL: 230.0, CARE: 336.3, FEED: 370.0, COLLECT_FERTILIZER: 425.5, FERTILIZE: 170.2, PICKUP: 334.2, PLACE: 70.2, DIG: 48.0, 이동: 2884.2, PASS: 1049.3 |
| 품목별 판매 총량 | FERTILIZER: 272.0, WHEAT: 281.2, WOOL: 110.0, MILK: 218.2, MELON: 88.0, CARROT: 154.7, STRAWBERRY: 170.5, EGG: 173.7, TOMATO: 81.8 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 150.7 턴 / 6.7 개 |


### 팀: ymg_aq (6 episodes)
| 항목 | 결과 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 113107 / 113938 |
| `BUY_LAND` 발행 step | 평균 2.0 구획 (평균 step: 152) |
| 최대 동시 일꾼 수 / 도달 step | 12.0 명 / 357 step |
| `BUY_ANIMAL` 내역 | COW: 7.0마리, SHEEP: 2.7마리, GOOSE: 4.0마리 |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 0.0 / 0.0 |
| 액션 타입별 총 횟수 | WATER: 993.2, HARVEST: 460.5, PLANT: 230.5, SELL: 368.8, CARE: 338.0, FEED: 357.0, COLLECT_FERTILIZER: 403.8, FERTILIZE: 198.3, PICKUP: 289.7, PLACE: 111.0, DIG: 38.0, 이동: 3541.3, PASS: 238.8 |
| 품목별 판매 총량 | WHEAT: 1388.5, FERTILIZER: 280.8, WOOL: 95.5, MILK: 232.7, MELON: 85.0, STRAWBERRY: 224.3, EGG: 149.3, CARROT: 141.7, TOMATO: 55.2 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 266.8 턴 / 7.2 개 |



---

## `reports/gemini/20260918-2104-PUBLIC-SOURCE-FETCH-20260918.md`

# 2026-09-18 21:04 PUBLIC-SOURCE-FETCH-20260918

1. **무엇을 바꾸거나 시험하는가**: 사용자 요청에 따라 현재 시간 기준으로 Kaggle 대회(Kaggriculture)의 최신 공개 코드(Notebook) 및 토론(Discussion) 글을 수집했습니다.
2. **왜 하는가**: 최신 커뮤니티 동향과 아이디어를 파악하여 프로젝트 전략에 반영하거나 분석하기 위함입니다.
3. **무엇을 측정했고 결과가 어땠는가**: `fetch_kaggle_updates.py` 스크립트를 실행하여 총 16건(Discussion 6건, Code 10건)의 자료를 에러 없이 성공적으로 수집했습니다.
4. **무엇이 막혀 있고 다음 행동은 무엇인가**: 막힌 부분은 없습니다. 다음 행동은 수집된 자료 중 유의미한 전략이나 증거(evidence)가 있는지 판독하는 작업(triage)입니다.

---

DONE | 16 sources collected, 0 errors | `docs/collection_runs/20260918T120427544503Z.json` (SHA-256: e350b48463d2cbe973fd838ccf0a9b1e433dc57d678ebc1da48c50a26df540c8) | `python3 scripts/fetch_kaggle_updates.py` exit 0 | NEXT ACTION: 수집된 자료 판독(triage)

### 상세 실행 결과
- **명령어**: `python3 scripts/fetch_kaggle_updates.py`
- **실행 시간**: 2026-09-18T12:04:27Z (UTC)
- **결과 파일**: `docs/collection_runs/20260918T120427544503Z.json`
- **수집 내역**:
  - Discussions: 6건 (top_voted/recent)
  - Codes: 10건 (top_voted/recent)
- **상태**: 16건 모두 `docs/code/` 및 `docs/discussion/` 경로에 성공적으로 저장되었습니다.


---

## `reports/gemini/20260918-P1C-ANALYSIS.md`

# P1c 24-hour Window Analysis & Priority Proposal (정정 및 최종 검증)

1. **무엇을 바꾸거나 시험하는가**: 
최근 24시간 동안 완료된 77개의 게임(승·무·패)을 분석하여, HIRE 실패, NOOP(상태 변화 없는 행동), 그리고 근소한 차이로 승패가 갈린 접전 경기를 재조명했습니다.
2. **왜 하는가**:
새로운 전략을 제출하기 전 패배의 구체적 원인을 찾기 위함입니다. 이전 분석에서 제기된 "HIRE 실패 100%" 등의 주장이 오류로 밝혀져 이를 정정하고, 엄밀한 정의를 통과한 True NOOP의 실제 발생 빈도를 확인하며, 접전 경기에서 실제로 승패를 바꿀 수 있었던 좁은 틈(분기점)을 특정하기 위해서입니다.
3. **무엇을 측정했고 결과가 어땠는가**:
- HIRE 실패는 단 3건의 패배 경기에서만 발생(W0, D0, L3)하여 패배의 주원인이 아님이 밝혀졌습니다. 
- 반면, 엄밀한 조건(엔진 강제 치환 및 이동 불가 제외)을 통과한 True NOOP은 승리/패배 무관하게 **100% 모든 경기에서 발생**함이 증명되었습니다. 이는 만성적인 스크립트 노이즈로 확인되었습니다.
- 접전 4경기(109856629, 110106409, 109831239, 109802471) 리플레이 분석 결과, 종반 1~2턴(Step 717-718)에 **무효한 PLACE 액션 버그**와 **보관소 잔여 재고 방치**로 인해 심각한 매도 누수가 발생하고 있음이 확인되었습니다.
4. **무엇이 막혀 있고 다음 행동은 무엇인가**:
종반부 청산을 최적화하는 구체적인 실험 카드를 설계하는 것을 다음 작업으로 추천합니다.

---

VERDICT | P1c 수집 및 대조 분석 정정 완료 | analysis/20260918-P1C-COLLECTION-PLAN.md, analysis/20260918-P1C-INVENTORY.md | HIRE/NOOP 서브에이전트 감사 결과 반영 및 접전 심층 분석 완료 | NEXT ACTION (종반 청산 로직 수정)

---

## 1. 수집 계획 및 메타데이터 (정정)
- **조회 시작 시각 (T)**: `2026-09-17T16:46:04Z` (UTC)
- **수집 대상 Window**: T 기준 직전 24시간. 원본 API 응답 메타데이터 유실로 인해 77개 표본의 정확한 24시간 window 소속 여부 및 46/31건 구분은 **N/A** 처리합니다.
- **결과**: 총 77경기 확보 (24 승 / 1 무 / 52 패)

---

## 2. 세 경로 (A, B, C) 분석표 최종 결과

| 경로 | 관측 수/분모 | 최초 시점 및 상태 변화 예시 | 가능한 설명과 대안 설명 | 다음 검증 및 예상 작업 범위 |
|---|---|---|---|---|
| **A. HIRE 실패/hands 부족** | 3 / 77<br>*(패배 3건에 한정)* | Codex 재검산 결과 W: 0/24, D: 0/1, L: 3/52 (총 13건 주문 실패) | **설명**: HIRE 실패는 100% 발생하는 현상이 아니며 극히 드문 예외입니다. | HIRE 실패는 패배의 주요 인과 관계가 아닙니다. 추가 검증 대상에서 제외합니다. |
| **B. 상태 무변화 반복 (True NOOP)** | 77 / 77<br>*(승리 시 24/24)* | `audit_p1c_noops.py` 결과, WATER/CARE 등 효과 없는 유효 액션 호출이 100% 경기에서 발생 (총 2,670건). | **설명**: 현재 스크립트가 유발하는 만성적 노이즈이며, 패배 경기에서 더 잦게 나타나나 승리 시에도 항상 발생합니다. | 거대한 코드 개편을 요하므로 접전 승부를 뒤집을 단기 최적화(하향식) 대상으로는 우선순위가 낮습니다. |
| **C. 접전/무승부 구체적 분기** | 4 / 53 | - 109856629 (Margin 0)<br>- 110106409 (Margin -10)<br>- 109831239 (Margin -92)<br>- 109802471 (Margin -422) | **설명**: 종반(Step 717~719)에 Shed/Pasture에서 잘못된 `PLACE` 액션을 호출해 무음 실패(Silent No-op)가 발생하거나, Shed에 보관된 STRAWBERRY/WHEAT를 방치해 코인화를 놓친 현상이 확인되었습니다. | 아래 심층 분석표를 통해 증명된 **종반 청산 매도 누락** 현상을 해결하는 로직 패치를 설계해야 합니다. |

---

## 3. 접전 4경기 카운터팩추얼 분석 (Close Match Counterfactuals)

| Episode | Action Pre-state & Actual Action | Execution Result | Concrete Legal Alternative Action | Required Funds/Inventory/Time for Alternative | Potential Future Impact (on price, cash, routing) | Confirmed Fact / Unverified Hypothesis / Needs Test |
|---|---|---|---|---|---|---|
| **109856629**<br>(Draw, Margin 0) | **Pre-state (Step 718)**: 유닛들이 Shed 타일에 위치한 상태로 총 WOOL 13, MILK 9, EGG 7 보유.<br>**Actual Action (Step 718)**: Market SELL 미제출, 719에 동시 덤프 발생. | 719 동시 덤프로 가격 폭락 (WOOL 154→31). 최종 0점 차 무승부. | Step 718에 `["DROP"]` 실행 후 시장에 1턴 일찍 모두 매도 주문. | Funds: 0, Inventory: 기보유분, Time: 0 | 선행 매도를 통해 가격 폭락을 피하고 154 코인 원가에 체결 (+2,100 코인 이상 확보). | **Confirmed Fact**: Step 719의 동시 폭락 현상.<br>**Needs Test**: 선제 덤프로 인한 슬리피지. |
| **110106409**<br>(Loss, Margin -10) | **Pre-state (Step 717)**: 유닛들이 MILK 18 보유.<br>**Actual Action (Step 718)**: Farmer와 Hand가 `["PLACE", "MILK", 1000]` 제출. | 불법 PLACE 액션으로 턴 허비 및 매도 기회 상실. 단 10 코인 차 패배. | 무효 PLACE 대신 `["DROP"]` 제출 후 시장에 `["SELL", "MILK", 18]` 등 제출. | Funds: 0, Inventory: 기보유분, Time: 0 | MILK 1단가가 103이므로 단 1개만 체결되어도 패배 마진(10)을 뒤집음. | **Confirmed Fact**: PLACE 버그 발생 및 단가 103 코인 확인 (마진 10 코인 초과). |
| **109831239**<br>(Loss, Margin -92) | **Pre-state (Step 717)**: Shed에 STRAWBERRY 5, WHEAT 3 보유.<br>**Actual Action (Step 718)**: Market 액션에서 해당 작물 매도 누락. | 해당 작물이 게임 끝까지 방치되어 92 코인 차 패배. | Step 718 Market Action에 `["SELL", "STRAWBERRY", 5]` 및 WHEAT 추가. | Funds: 0, Inventory: Shed 내 기보유분, Time: 0 | 잔여 작물(단가 26, 27) 매도로 즉시 211 코인 확보 (+119 코인 우위로 역전). | **Confirmed Fact**: Shed 내 방치된 작물 및 패배 마진 수학적 상회 증명. |
| **109802471**<br>(Loss, Margin -422) | **Pre-state (Step 717)**: 점수 완전 동점 (118,101).<br>**Actual Action (Step 718)**: 상대는 DROP/매도 성공(+4,244), Sian은 무효 PLACE/PASS 발생(+3,822). | 해당 턴에서 정확히 422 코인 손실이 누적되어 패배. | Shed 타일 위 유닛들의 무효 PLACE를 `["DROP"]`으로 교체. | Funds: 0, Inventory: 기보유분, Time: 0 | 상대와 대등한 청산 볼륨 달성으로 422 코인 열세 상쇄. | **Confirmed Fact**: Step 718 단일 턴에서 발생한 정확한 차액 422 코인 확인. |

> **주의(Caution)**: 사후적으로 점수를 더하는 계산은 인과 관계를 증명하지 못하지만, 우리 봇이 제출한 불법/무음 실패 액션(`PLACE` 버그)과 명백한 매도 누락(STRAWBERRY/WHEAT 방치)은 수정해야 할 핵심 결함임이 확인되었습니다.

---

## 4. 최종 제안: 가설 수립 및 다음 실험

종반부(Step 717-719)에 발생하는 결함을 해결하기 위한 다음 1가지 가설을 우선순위로 제안합니다:

**[HYP-001] 종반 청산 로직(Endgame Liquidation Module) 강화**
종반부에 Shed/Pasture 타일에서 비어있지 않은 인벤토리를 들고 있을 때 `PLACE` 액션 생성을 차단하고 무조건 `DROP`을 강제하며, 보관소에 남은 1개 이상의 모든 아이템(STRAWBERRY, FERTILIZER 등)을 예외 없이 SELL 큐에 자동 등록하면, 무의미한 점수 손실을 막아 접전 승률을 유의미하게 올릴 수 있다.
