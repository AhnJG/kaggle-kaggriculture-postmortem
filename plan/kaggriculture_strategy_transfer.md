# 부록 A — 기존 전략 흡수 전략 (알파고 SL 노선 검토)

작성 2026-09-03 · 본문: `kaggriculture_final_plan.md`
질문: "비슷한 종류의 게임 공략에 있는 전략을 쓸 수 없나? 초기 알파고처럼 기존 전략을 흡수할 수 있을 것 같다."

## 0. 결론

**된다. 그리고 이 대회는 특히 잘 맞는다.** 다만 알파고 비유의 절반만 옮겨온다.

| 알파고 구성요소 | 이 대회 | 판정 |
|---|---|---|
| SL 정책망 (인간 기보 흡수) | 리플레이에 **양 seat의 action + 각자의 private 관측**이 전부 들어있다 (로컬 확인) | **옮겨온다** |
| MCTS (온라인 탐색) | 턴당 1초, 720턴, 동시수·확률적, 거대 분기 | **불가** |
| 알파제로의 실제 레버 = "비싼 오프라인 → 싼 온라인" | 1초 제한은 **런타임에만** 걸린다. 학습·계획 시간은 무제한 | **이게 진짜 기회** |

운영진이 데이터셋 설명에 직접 *"IL/BC, bootstrapping RL, or just gathering statistics"* 라고 적어놨다. 흡수 노선은 주최측이 열어둔 길이다.

## 1. 이 게임을 흡수에 유리하게 만드는 구조 (엔진 확인)

**상대가 나에게 영향을 주는 경로는 `market["inventory"]` 하나뿐이다.**
엔진의 모든 플레이어별 함수(`_do_hire`, `_do_buy_land`, `_apply_unit_action`, `_commit_unit`)는 `farms[player_id]`만 건드린다. 공유 가변 객체는 `market` 뿐이고 `town`은 외생이다. 공격·방해 액션은 존재하지 않는다.

→ 게임이 이렇게 분해된다:
```
[내 농장 단일 에이전트 스케줄링]  ──9차원 벡터(market inventory)──  [상대 농장 단일 에이전트 스케줄링]
```
**농장 쪽은 상대 없이 오프라인 최적화가 가능하고, 상대 대응은 매도 스케줄에만 넣으면 된다.**
알파고처럼 게임 트리 전체를 다룰 필요가 없다. 이게 아래 L3를 성립시키는 근거다.

## 2. 흡수 사다리 (ROI 순)

### L0. 공개 상위 코드를 읽는다 — 오늘, 무료, 위험 0
`boatlee/V16-RC5 8C/4S Premium Market Lead`, public **2913.3**, **Apache-2.0**. LB 6위(2912.0) 수준.
이건 기보가 아니라 **선생의 뇌 자체다. 알파고는 이걸 못 봤다.**
- 실행 → 매 턴 의사결정 로그 → 규칙 역추출(동물 수·땅 매입 시점·일꾼 수·매도 임계값)
- opponent zoo의 **챔피언으로 고정** → 모든 개선을 이것 대비 페어드 승률로 판정
- ⚠️ 그대로 제출하면 다른 수천 팀 클론과 **같은 봇**이 된다. 베이스라인·상대·해부 대상으로만 쓴다.

### L1. 리플레이에서 파라미터만 뽑는다 — BC보다 먼저
BC가 정책을 통째로 복제하는 것이라면, 이건 **결정 임계값만 추출**하는 것이다. 27일 안에 확실히 끝난다.
- 승자들의 day별 동물 수 / 땅 매입 시점 / 일꾼 수 / 품목 믹스 분포
- **승패가 갈린 판에서 무엇이 달랐나 (paired)** — 이게 진짜 공략
- 매도 타이밍 vs 시장 재고 산점도 → 상위권의 실제 매도 룰
- 상점 추첨 벡터별 승자 품목 믹스 → §M5의 조건부 배분표를 **데이터로** 채운다
출력이 숫자 20~30개짜리 config면 우리 룰베이스에 그대로 꽂힌다. **gemini 1주차 최우선.**

### L2. 행동 복제 (BC) — 알파고 SL 그대로
**가능하다.** 근거와 주의점:

*데이터*
- `kaggle/kaggriculture-episodes-index`: 하루 660~930판 × 35일 ≈ **24,000판**
- **하루치가 21.5GB** → 맥북에어 다운로드 금지. **Kaggle 노트북에서 데이터셋을 마운트해 파싱하고 (state, action) 텐서만 파생 데이터셋으로 내보내는 것이 유일하게 성립하는 파이프라인.**
- 리플레이 구조 확인 완료: `steps[t][seat]`에 `action` + `observation`(자기 `private` 포함) + `info.seed` + `module_version`

*Orbit Wars(같은 런타임, ~5,000팀) BC 리포트의 실측 교훈 — 그대로 적용*
- **승자 쪽 상태만 학습한다**
- **한 명만 복제한다** — 여러 명을 섞으면 스타일 일관성이 깨져 더 나빠진다
- **상태 수가 전부다** — 승률이 winner-state 2배마다 약 +9pt
- 복제 난이도는 상대의 **행동 예측가능성**을 따르지 레이팅을 따르지 않는다
- 정규화 버그가 "복제 불가능"처럼 보이게 만든다 (가장 흔한 함정)
- 조건부 BC `π(a|s, z, r)` (선생 one-hot + recency)가 개별 클론보다 낫고 데이터도 1/4만 쓴다
- **2.3M 파라미터 어텐션 넷이 1초/턴 안에 돈다** → NN 배포 자체는 확실히 가능
- 공식 제출은 `tar.gz`에 `model_weights.pkl` 동봉 가능 (공식 AGENTS.md 명시)

*이 게임 고유의 난점*
행동이 `farmer 1개 + hands N개 + market ≤10개`의 **가변길이 구조 행동**이다. Orbit Wars보다 지저분하다.
→ 헤드를 쪼갠다: 유닛별 op 헤드(타일 상태 조건부) + 시장 주문 헤드(품목별 수량). 유닛 순서는 permutation-invariant하게.

*정직한 기대치*
Orbit Wars에서 BC는 5,000팀 중 **49위(솔로 실버)**, 우승은 전부 대규모 self-play RL이었다.
**BC = 확실한 상위권, 그 자체로 우승은 아님.**

### L3. 오프라인 탐색 → 런타임 테이블 — 알파제로의 진짜 레버
§1의 분해 덕분에 성립한다.
- 농장 쪽 = **타일 × 날 자원배분 스케줄링** → MILP / DP로 오프라인 최적해를 구할 수 있다
- `(day, 해금 구역, 현금, 상점 벡터)` 격자에 대해 미리 풀어 **빌드오더 테이블**로 컴파일
- 런타임은 O(1) 조회 + 시장 대응만 → actTimeout 문제가 사라진다
- RTS 빌드오더 / 알파스타의 최대 레버가 이것이었다
- **BC와 배타적이지 않다**: BC를 policy prior, 테이블을 백본으로 섞을 수 있다

### L4. self-play RL — **KILL**
근거 셋:
1. 이 대회 디스커션의 RL 시도 보고 (`734952 Is Pure Self-Play PPO viable?`, `736567 End-to-End RL Is Harder Than It Looks`)
2. Orbit Wars 49위 리포트: warm-start self-play를 단일 GPU로 돌려 **클론을 넘지 못했다.** 로컬 eval에서 이긴 체크포인트가 사다리에서는 더 나빴다(훈련 풀 과적합)
3. 우리 컴퓨트(맥북에어 + Colab)는 그 대회 우승 솔루션의 1/1000 이하 규모
→ `coordination/KILL.md`에 등재. 재제안 금지.

## 3. 장르에서 직접 옮겨오는 전략 (검증된 매핑)

| 이 게임의 문제 | 기성 이론 | 즉시 나오는 정책 |
|---|---|---|
| 가격충격 곡선에 대량 매도 | **최적 실행 (Almgren–Chriss)** | 한 번에 던지지 말고 **회복률에 맞춰 쪼갠다**. 여기서 회복률 = 마을 흡수율(§1.2c) |
| 딸기·우유·양털 (재생 수요) | **재생자원 수확 / 최대지속수확량(MSY)** | **재생률 이하로만 판다.** 넘기면 자기 가격을 죽인다 |
| 멜론·비료 (재생 0, 상대와 공유) | **고갈자원 복점 (Hotelling)** | 경쟁은 채굴을 앞당긴다 → **독점자보다 먼저, 빨리** 판다 |
| 매 판 다른 상점 추첨 | **랜덤 수요에 대한 배분 게임 (Blotto류)** | day 3/6/9…마다 재배분. 고정 품목은 그 판 추첨에 지고 시작 |
| 타일 100칸 + 30일 시계 | **타이쿤 장르: 타일·일당 가치 + 회수기간** | 계산 완료 — 멜론 137.5 > 소 80 > 양 66.7 > 거위 50 > 딸기 28.8 … + 마감 캘린더(§1.2k) |
| 되돌릴 수 없는 초기 투자 | **RTS 빌드오더** | 오프닝을 오프라인에서 최적화해 테이블로 굽는다 (L3) |

## 4. 27일 배치안

| 시점 | 노선 | 담당 |
|---|---|---|
| 즉시 | **L0** 공개 2913 봇 확보 → 챔피언 상대로 고정, 의사결정 로그 해부 | codex + cowork |
| 1주차 | **L1** 리플레이 파라미터 추출 (Kaggle 노트북에서, 다운로드 금지) | gemini |
| 2주차 | **L3** 오프라인 스케줄링 → 빌드오더 테이블 = **1번 슬롯 백본** | codex |
| 2~3주차 | **L2** BC 클론 = **2번 슬롯 헤지** | gemini + codex |
| — | **L4** RL = KILL | — |

**두 슬롯을 이렇게 나누는 이유**: 서로 다른 실패면을 가져야 한다.
- 오프라인 최적화 룰베이스는 **메타 드리프트에 약하고** 이상 시드에 강하다
- 상위권 BC 클론은 **이상 시드에 약하고** 메타 드리프트에 강하다 (메타를 학습했으니까)
최종 2주간 메타가 어느 쪽으로 움직여도 한쪽은 버틴다.

## 5. 이 부록의 FACT (재현 명령)

- 리플레이 구조: `env.toJSON()['steps'][t][seat]` → `action` / `observation`(자기 `private` 포함). `verify_engine_facts.py` 뒤에 붙일 것
- 플레이어 간 결합이 market 하나뿐: `grep -n "farms\[" kaggriculture.py` → 전부 `farms[player_id]` 단일 인덱스
- 데이터 규모: `kaggle/kaggriculture-episodes-index` manifest.csv → 하루 660~930 에피소드, 13.6~21.5 GB
- 런타임: `configuration.runTimeout = 1200`(에피소드 전체), `actTimeout = 1`(턴), `observation.remainingOverageTime = 60`

## 출처

- [Kaggriculture Episodes Index](https://www.kaggle.com/datasets/kaggle/kaggriculture-episodes-index) (운영진, 매일 갱신)
- [Kaggriculture Episodes](https://www.kaggle.com/datasets/georgymamarin/kaggriculture-episodes) (커뮤니티, 37,000+ 리플레이)
- [V16-RC5 | High-Score 8C/4S Premium Market Lead](https://www.kaggle.com/code/boatlee/v16-rc5-high-score-8c-4s-premium-market-lead) (public 2913.3, Apache-2.0)
- [Top 50 Imitation Learning Solution — Orbit Wars](https://www.kaggle.com/competitions/orbit-wars/writeups/top-50-imitation-learning-solution) (같은 런타임, BC로 49/5000)
- [Is Pure Self-Play PPO viable?](https://www.kaggle.com/competitions/kaggriculture/discussion/734952) · [End-to-End RL Is Harder Than It Looks](https://www.kaggle.com/competitions/kaggriculture/discussion/736567)
