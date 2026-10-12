> **SUPERSEDED — 2026-09-15:** 현재 일정·우선순위·제출 gate는 [CURRENT.md](CURRENT.md)에서 시작한다. 아래 본문은 과거 검토 기록이며 현재 실행 지시가 아니다. 첫 제출 지시, 제출 총량 5회 전제, parent 대결 중심 gate, SELL 미체결 절대 0 기준은 최신 계약·schema 3과 함께 사용하지 않는다.

# Kaggriculture 검증 보고서와 최종 실행 계획

검토 기준일: 2026-09-03 KST  
검토 방식: 원본 계획 3개를 공식 대회 문서, 현행 환경 소스, 배포 버전, 운영진 설명 및 관련 연구와 대조했다. 전략적 결론은 사실이 아니라 검증할 가설로 분리했다.

## 0. 한 문장 판정

세 계획 중 `kaggriculture_codex_plan.md`를 운영 골격으로 삼고 `kaggriculture_claude_plan.md`의 협업·증거관리 장점을 합치되, 두 문서의 잘못된 공식 사실과 검증되지 않은 전략 결론을 제거해야 한다. `kaggriculture_gemini_plan.md`는 단순화 원칙만 유지할 수 있으며, 존재하지 않는 물 구매 메커니즘 때문에 전략 근거로는 사용할 수 없다.

어떤 문서도 현재 상태로는 우승 계획으로 확정할 수 없다. 우승을 보장할 방법은 없으며, 아래 계획의 목적은 제한된 제출 기회를 재현 가능한 증거에 배분하여 우승 확률을 높이는 것이다.

## 1. 검토 대상의 정확한 식별

| 파일 | SHA-256 | 판정 |
|---|---|---|
| `kaggriculture_claude_plan.md` | `b3c388b80702160fd395733fa1363e4f499ae7ede95bab0cf6e8c905f0341fce` | 대폭 수정 필요. 협업 설계는 좋지만 평가 이력, 행동량, 시장 상한, 거위·비료 전략을 사실처럼 단정했다. |
| `kaggriculture_codex_plan.md` | `7f1bb96c0ae7a0a8db92e7eeebd66b7c1b2d4d4e13a3bbd195ad71b4e0a196d5` | 보완 후 기반으로 채택. 증거 설계는 가장 좋지만 자원 한도, 참고문헌, 버전·규정·게임별 전략이 불완전하다. |
| `kaggriculture_gemini_plan.md` | `38ce9879024d5cc41e42148be654a07732961538b8c637d4f0d060d7ad8a9c17` | 우승 계획으로 채택 불가. 물 구매라는 치명적 환각과 부분관측·평가 체계 누락이 있다. |

현재 폴더는 Git 저장소가 아니다. 따라서 세 계획에 등장하는 commit SHA, branch, base SHA 기반 협업은 저장소를 초기화하기 전에는 실행할 수 없다. Kaggle 계정의 규칙 동의 여부, 현재 제출 수, 현재 활성 agent ID와 점수는 이 로컬 파일만으로 확인할 수 없으므로 `N/A — Kaggle 계정에서 확인 필요`로 둔다.

## 2. 계획이 따라야 할 검증된 공식 사실

### 2.1 게임과 평가 목표

- 한 경기는 2인, 30일, 하루 24턴으로 총 720턴이다.
- 경기 승패는 종료 시점의 **은행 현금**으로 정한다. 현금 차이의 크기는 rating에 직접 반영되지 않으므로 평균 현금 극대화가 아니라 승/무/패 확률을 우선 최적화해야 한다.
- 하루 최대 5개 agent를 제출할 수 있고, 가장 최근 2개가 활성 상태 및 최종 평가 대상이 된다. 팀 leaderboard에는 둘 중 더 좋은 결과가 표시된다.
- 최종 Bradley–Terry 계산에는 단순히 마감 후 경기만 들어가는 것이 아니다. Kaggle 운영진 설명에 따르면 대회 전체 기간에 치른 경기 중 **경기 양쪽 agent가 최종적으로도 활성 상태인 경기**가 들어가고, 비활성화된 agent가 포함된 경기는 제외된다. 그러므로 검증된 incumbent를 무심코 밀어내면 그 agent의 유용한 경기 이력까지 최종 계산에서 빠질 수 있다.
- 상금은 1위부터 10위까지 각 미화 5,000달러, 총 50,000달러다.

근거: [공식 Overview/Evaluation](https://www.kaggle.com/competitions/kaggriculture/overview/evaluation), [최종 경기 포함 범위에 관한 Kaggle Staff 설명](https://www.kaggle.com/competitions/kaggriculture/discussion/732931)

### 2.2 일정

| 이벤트 | UTC | KST |
|---|---:|---:|
| Entry 및 Team Merger 마감 | 2026-09-23 23:59 | 2026-09-24 08:59 |
| Final Submission 마감 | 2026-09-30 23:59 | 2026-10-01 08:59 |
| 추가 경기 및 수렴 | 2026-10-01부터 약 2주 | 약 2026-10-15까지 |

근거: [공식 Timeline](https://www.kaggle.com/competitions/kaggriculture/overview/timeline)

### 2.3 현행 엔진과 실행 계약

- 2026-08-15 balance patch는 carrot, tomato, egg 가격 곡선을 변경했고 `kaggle-environments >= 1.32.7` 사용을 요청했다. 재현 실험에서는 범위를 열어 두지 말고 우선 `kaggle-environments==1.32.7`과 정확한 wheel/source SHA를 고정한다. 새 공식 패치가 나오면 별도 migration 실험으로 승격한다.
- 환경 설정의 `actTimeout`은 1초다. 안전 기준은 1초를 그대로 목표로 쓰는 것이 아니라 로컬과 Kaggle 조건에서 충분한 headroom을 둔 내부 deadline으로 정하고, 전체 720턴 stress test에서 timeout이 없어야 한다.
- `100 MiB`는 메모리 한도가 아니라 제출 패키지 크기 한도다. 원격 LLM은 평가 중 네트워크 ingress/egress 금지 때문에 사용할 수 없다. 번들 모델 자체가 문언상 절대 금지라는 근거는 없지만, 크기·CPU·시간·라이선스 gate를 모두 통과하지 못하면 실전 후보가 될 수 없다.
- 제출은 단일 `main.py`도 가능하고, 루트에 `main.py`가 들어 있는 다중 파일 `tar.gz`도 가능하다. 단일 파일 병합은 공식 의무가 아니라 선택 가능한 단순화다.

근거: [공식 balance 공지](https://www.kaggle.com/competitions/kaggriculture/discussion/735311), [PyPI 1.32.7](https://pypi.org/project/kaggle-environments/1.32.7/), [환경 JSON](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.json), [공식 제출 안내](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/AGENTS.md), [공식 Rules](https://www.kaggle.com/competitions/kaggriculture/rules)

### 2.4 정보와 시장의 경계

- 상대의 농장 상태, 돈, 위치는 공개되지만 상대의 shed, seed 및 unit inventory는 비공개다. 따라서 상대 재고를 “추적”한다고 쓰지 말고 공개 정보로부터 분포를 갱신하는 belief estimation이라고 써야 한다.
- 시장에서 다시 살 수 있는 상품은 `WHEAT`와 `FERTILIZER`뿐이다. 다른 상품에 일반적인 buy-low/sell-high arbitrage를 적용할 수 없다.
- 시장 재고는 날짜가 바뀌어도 유지되며, town과 상대 주문으로 줄 수 있다. 가격이 바닥 `$1`에 닿아도 판매자는 `$1`을 받고 그 단위가 시장 재고에 추가되지 않을 뿐이다. 따라서 초기 재고만으로 계산한 가격 바닥 도달량은 “시즌 매출 상한”이 아니다.
- farm hand의 고용비는 매일 Fibonacci 방식으로 늘고 고용된 손은 하루가 끝나면 사라진다. 고용 시점, 기본 farmer의 행동, 이동·수거·급수·먹이 행동을 함께 계산해야 한다.
- shed 용량 100, 턴당 시장 order 최대 10, 작물의 급수·수명·weed, 동물의 먹이·탈출·생산, town shop 일정과 처리 순서가 모두 정책과 테스트에 들어가야 한다.

근거: [공식 환경 README](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/README.md), [공식 interpreter 소스](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.py)

### 2.5 규정과 공개 의무

- Kaggle 팀은 최대 5명이다. 이는 Gemini/Claude/Codex 같은 도구 수와 별개의 제한이다.
- 팀 밖 비공개 코드 공유는 금지된다. 공개 competition code는 대회 참가자가 접근할 수 있는 Kaggle 경로에서 공개하고 상업 이용을 막지 않는 라이선스 조건을 따라야 한다.
- 외부 데이터·모델·도구는 합리적으로 접근 가능해야 하고 사용 및 출력 권리가 있어야 한다.
- 평가 중 네트워크 입출력은 금지된다. episode replay와 행동은 공개될 수 있으므로 비밀 전략을 전제로 설계하지 않는다.
- 이 simulation 대회에는 일반적인 private leaderboard가 없다. 공개 rating 변화와 최종 재계산을 같은 개념으로 취급하지 않는다.
- 수상 시 규칙이 요구하는 라이선스와 재현 가능한 상세 설명·저장소 제공에 대비해 출처, 라이선스, 환경, artifact를 처음부터 기록한다.

근거: [공식 Rules](https://www.kaggle.com/competitions/kaggriculture/rules)

## 3. 원본 계획별 오류와 유지할 부분

### 3.1 `kaggriculture_claude_plan.md`

#### 잘못되었거나 과장된 주장

1. **L11, L46, L230 — 최종 평가 이력:** “마감 후 경기만 사용되고 live 이력은 버려진다”는 주장은 틀렸다. 최종 활성 agent들 사이의 대회 전체 해당 경기가 최종 계산에 들어간다.
2. **L52–68 — 행동량과 병목:** 고용손 `N×24`만 세어 기본 farmer를 빠뜨렸고, turn 0에 고용해도 새 손이 첫 행동을 즉시 모두 수행하는 것은 아니다. 첫날 이상적 상한도 대략 `24 + 23N`이며 실제 값은 고용 턴과 이동 때문에 더 작다. 매일 반복되는 고용비도 계산해야 한다. 따라서 “행동은 거의 공짜이고 시장만 진짜 병목”이라는 결론도 입증되지 않았다.
3. **L72–103 — 시장 “시즌 매출 상한”:** `[LOCAL]` 초기 시장 재고 10,000, 다른 주문 없음, 한 단위씩 순서대로 판매한다는 조건으로 현행 정수 반올림 공식을 재현하면 첫 `$1` 호가는 대략 carrot 842, tomato 529, fertilizer 493 단위로 문서의 867, 537, 495와도 다르다. 이는 문서 수치의 sanity check일 뿐이다. 더 중요한 문제는 어느 값도 시즌 상한이 아니라는 점이다. town·상대 수요가 재고를 줄이고 `$1` 판매도 수입을 만든다.
4. **L99 — 거위·비료:** “비료 비용 0”, “가장 싼 거위가 항상 최적”은 성립하지 않는다. 구매, 배치, 먹이, 생존, 수거, 이동, coop와 행동 기회비용이 있다. 검증할 ROI 가설로 낮춰야 한다.
5. **L101–111 — 고정 전략 결론:** “멜론 158개 이후 완전히 무가치”, 특정 작물·동물은 함정, carrot shop이 항상 우세, 상대보다 하루 먼저 팔면 유리하다는 서술은 엔진 사실이 아니라 상대·shop·시장 상태에 의존하는 가설이다.
6. **L115 — 하루 행동 전부 캐시:** 1초 제약을 이유로 하루 24턴을 고정하면 시장, town, 상대 변화에 반응하지 못한다. 일일 기본 계획을 캐시하되 매 턴 invariant를 확인하고 사건 발생 시 bounded replan해야 한다. `p99 < 0.30초`는 공식값이 아니라 측정 후 정할 내부값이다.
7. **L44, L48, L136–140 — 표본과 gate:** 커뮤니티의 특정 시점 rating 변동, random bot 95%, 100 또는 200게임 같은 숫자는 보편적 승격 기준이 아니다. 상대별 결과, 고정된 seed 수, 좌석 교대, 신뢰구간과 최소 효과를 사전 선언해야 한다.
8. **L139 — 서로 다른 최종 두 전략:** 다양성 자체는 점수로 합쳐지지 않는다. 각 slot 후보가 독립적으로 강해야 하며, 유사한 두 최강 변형이 더 나을 수도 있다.
9. **L219 — 단일 파일:** 공식 요구가 아니다. 실제 업로드할 tarball을 검증하는 것이 핵심이다.
10. **L150–174 — agent 제품 동작:** Cowork와 각 CLI가 자동으로 완전히 같은 파일 상태를 본다는 설명, idle reclaim 수치, symlink 의존은 인용된 공식 근거가 없다. 실제 client·cwd·권한·instruction load를 확인하는 중립적인 절차로 바꿔야 한다.
11. **L238 — 실행 불가능한 다음 행동:** 현재 폴더에는 언급한 `setup_kaggriculture.py`가 없다.

#### 유지할 부분

- 엔진 소스 우선 검증, 공식 사실과 가설 분리, patch 감시
- 한 폴더와 경로별 단일 책임자
- BOARD/FACT/KILL/실험 로그의 파일 기반 상태
- 가설 사전등록, artifact registry, 사람의 최종 제출 승인
- 마감 전 동결과 안정성 gate

단, `KILL`은 영구 금지가 아니라 `엔진 버전 + 상대군 + 구현 + 실패면 + 재검토 조건`으로 범위를 제한한다.

### 3.2 `kaggriculture_codex_plan.md`

#### 잘못되었거나 부족한 주장

1. **L19 — 100 MiB memory:** 명백한 단위·항목 오류다. 제출 패키지 크기와 RAM을 혼동했다. “런타임 LLM 전부 금지”도 원격 호출 금지와 번들 모델의 현실적 부적합을 구분해야 한다.
2. **L38–43, L229 — 두 정책은 반드시 달라야 함:** 공식 요구도, 우승의 필요조건도 아니다. 각각의 독립 강도가 먼저다.
3. **L104–107, L284 — blind seeds:** 모든 agent가 읽는 같은 폴더의 seed는 blind가 아니라 재사용 holdout이다. 진짜 blind 평가는 코드 동결 뒤 사람이 seed를 생성하거나 evaluator가 seed를 숨기고 집계 결과만 공개해야 한다.
4. **L129–140 — 데이터 흐름:** runtime은 `main.py → src/*`, 로컬 평가는 `arena → main.py`다. 더 중요한 `package → clean extraction → Kaggle validation → submission ID → episodes/replays/logs → hosted ledger`가 빠졌다.
5. **L183–263 — 지침 wrapper:** `Follow AGENTS.md.` 한 줄은 실제 내용을 자동 import한다고 보장하지 않는다. Claude와 Gemini의 문서화된 import 문법을 사용해야 한다.
6. **L265–286 — 일정:** 실제 UTC/KST 날짜와 후보 동결·승격·중단 조건이 없다.
7. **L308 — 출처 설명:** discussion 735311은 active submission 설명이 아니라 balance patch 공지다.
8. **L310 — 논문 설명:** DOI `10.1287/opre.39.4.583`은 Bradley–Terry가 아니라 common random numbers와 control variates의 multiple-comparison 연구다. 같은 seed 비교 근거로 옮길 수 있다.
9. **L311 — 논문 설명:** arXiv `1711.00832`는 AlphaStar 논문이 아니라 PSRO를 제시한 다중 agent game-theoretic 연구다. opponent mixture 근거로는 적절하다.
10. **전체 — 핵심 누락:** 엔진 version/SHA, balance patch watch, 팀·라이선스·네트워크 규정, 실제 게임 메커니즘별 가설, 제출 artifact에서 hosted 결과까지의 추적성이 없다.

Bradley–Terry 원전은 [Bradley & Terry, 1952](https://academic.oup.com/biomet/article-abstract/39/3-4/324/326091)다. 같은 random seed로 변형 간 분산을 줄이는 설계는 [common random numbers 연구](https://pubsonline.informs.org/doi/10.1287/mnsc.38.6.884)가 뒷받침한다. 다양한 상대 정책을 섞어 과적합을 줄이자는 아이디어는 [PSRO 논문](https://arxiv.org/abs/1711.00832)에서 개념적 근거를 얻을 수 있지만, 이 게임에서의 우위는 직접 실험해야 한다.

#### 유지할 부분

- 평균 cash와 공식 W/D/L 목표 분리
- same-seed, 양 seat 교환, opponent zoo
- local과 hosted evidence 분리
- 얇은 `main.py`, 모듈화, 단일 integrator
- frozen release, SHA-256 registry, compile/import/latency/package gate
- 간결한 handoff와 종료 전 liquidation

### 3.3 `kaggriculture_gemini_plan.md`

#### 잘못되었거나 부족한 주장

1. **L3 — Profit 표현:** 한 경기의 정확한 기준은 종료 은행 현금이며 대회 평가는 W/D/L 기반이다.
2. **L26–28 — 모델별 과제:** Claude의 reward 설계, Codex의 MCTS, Gemini의 가격 주기 분석이 각각 우월하다는 근거가 없다. 공식 reward는 바꿀 수 없고, MCTS는 1초 안에서 성능을 입증해야 하며, 가격 함수는 이미 소스로 공개되어 있다.
3. **L34–35 — 물 구매:** 게임에는 물 재고나 물 구매가 없다. `WATER`는 타일에 수행하는 행동이다. 이 예시는 삭제하고 “급수 작업이 deadline 전에 배정되지 않음”으로 바꿔야 한다.
4. **L44 — 55% 승격:** 표본 수, 상대, seed, 좌석, 불확실성이 없는 임의 기준이다.
5. **L45–46 — 단일 파일과 1~5초:** tarball 다중 파일도 지원되며 현행 `actTimeout`은 1초다.
6. **L51 — 상대 inventory와 arbitrage:** 상대 inventory는 일부 비공개이고 WHEAT/FERTILIZER 외 상품을 시장에서 다시 살 수 없다.
7. **L52 — 로컬 대회가 곧 순위:** 로컬 결과는 proxy일 뿐이다. hosted episode와 rating만 외부 성능 증거다.
8. **L48–57 — 핵심 세 가지:** 실제로 네 가지를 열거해 원 프롬프트도 충족하지 못했다.
9. **전체 — 핵심 누락:** 평가 방식, 최신 두 slot, final history, 일정, 버전, 패키지 계약, 부분관측, 규정, artifact 추적, 출처가 없다.

#### 유지할 부분

- 단순하고 검증 가능한 baseline부터 시작
- 모듈화, 로컬 반복 평가, fallback
- 전략·구현·분석을 나누는 발상
- 초·중·후반과 liquidation을 구분하는 발상

## 4. 놓치고 있던 공통 항목

1. **공식 사실의 영역별 우선순위:** 규정·평가·일정은 Rules/Overview/Staff 공지, 게임 동작은 고정된 배포 엔진, 성능은 같은 창의 hosted episode, 그다음이 로컬 실험이다. 커뮤니티 글은 가설 생성 자료다.
2. **엔진 drift:** `master` 링크만 쓰지 말고 package version, source commit, file SHA, replay의 module version을 기록한다.
3. **정확한 artifact identity:** source commit이 아니라 실제 업로드한 `submission.tar.gz`의 full SHA-256, 파일 목록, dependency, build command, validation log, Kaggle submission ID를 묶는다.
4. **동시 작업 안전성:** 한 폴더에서 branch 전환, rebase, stash, Git index, `main.py`, release를 여러 agent가 동시에 만지면 안 된다.
5. **상대·데이터 출처:** 공개 opponent는 URL, 저자, 라이선스, 수집일, engine version을 기록한다. raw replay와 대회 데이터는 `.gitignore`된 private 영역에 둔다.
6. **부분관측:** 보이는 상대 농장과 보이지 않는 inventory를 명시적으로 분리하고 belief 오차를 stress test한다.
7. **통계 설계:** 효과가 좋을 때까지 seed를 계속 추가하지 않는다. pilot으로 분산을 추정한 뒤 최소 검출 효과, seed 수, opponent mix, 평가식을 고정한다.
8. **운영 상태:** 규칙 동의, 팀, 제출 수, 현재 active ID, episode 수, engine version과 latest patch를 매일 확인하는 checklist가 필요하다.
9. **실패의 범위:** 한 구현이 실패해도 전략 전체를 죽이지 않는다. `구체 구현 실패`, `운영 결정`, `넓은 가설 상태`를 분리한다.
10. **보안과 재현성:** 평가 중 네트워크 호출을 완전히 제거하고, 수상 시 재현·라이선스 제출을 즉시 만들 수 있게 dependency provenance를 보존한다.

## 5. 최종 우승 확률 극대화 계획

### 5.1 성공 정의와 증거 언어

1차 목표는 목표 상대 분포에서 `win=1, draw=0.5, loss=0`로 계산한 paired score와 추정 Bradley–Terry 강도를 높이는 것이다. 은행 현금 차이, 생산량, 평균 profit은 원인 분석용 2차 지표다.

모든 주장은 아래 꼬리표 중 하나를 붙인다.

- `[OFFICIAL]`: Rules, Overview, Kaggle Staff 공지
- `[ENGINE]`: 고정한 배포 버전의 source/config로 재현됨
- `[HOSTED]`: 정확한 submission ID와 episode로 관측됨
- `[LOCAL]`: 정확한 artifact, seed, 상대와 runner로 재현됨
- `[INFERENCE]`: 위 증거에서 도출한 해석
- `[HYPOTHESIS]`: 아직 승격 실험을 통과하지 않은 전략 아이디어

`[LOCAL]`은 `[HOSTED]`를 대체하지 않는다. 서로 다른 날짜와 episode 수의 live rating도 직접 비교하지 않고, 같은 창과 상대·게임 수를 기록한다.

### 5.2 하나의 작업 폴더 구조

```text
Kaggriculture/
├── AGENTS.md                         # 공통 프로젝트 계약
├── CLAUDE.md                         # @AGENTS.md
├── GEMINI.md                         # @./AGENTS.md
├── README.md
├── requirements.lock                 # kaggle-environments==1.32.7 등
├── environment/
│   ├── ENGINE_LOCK.md                # package/source/config SHA와 patch 날짜
│   └── LICENSES.md                   # 외부 코드·모델 provenance
├── main.py                           # Kaggle root entrypoint, 얇게 유지
├── src/kaggriculture_agent/
│   ├── state.py                      # 관측 파싱과 공개/비공개 경계
│   ├── planner.py                    # 일/phase 계획과 event replan
│   ├── allocator.py                  # unit별 routing·deadline·충돌 회피
│   ├── economy.py                    # ROI, 시장, shop, shed, liquidation
│   ├── opponent.py                   # 공개 정보 기반 belief
│   └── safety.py                     # 합법 action, deadline, fallback
├── tests/
│   ├── unit/
│   ├── properties/
│   ├── replay_regression/
│   └── latency/
├── tools/
│   ├── arena.py
│   ├── build_release.py
│   ├── analyze_replays.py
│   └── registry_check.py
├── configs/
│   ├── paired_seeds.yaml
│   ├── holdout_policy.md
│   └── opponents.yaml
├── opponents/
│   └── README.md                     # URL·license·version·수집일
├── experiments/
│   ├── registry.csv                  # append-only 실험 및 중복 방지
│   ├── cards/EXP-*.md
│   └── results/EXP-*/
├── evidence/
│   ├── OFFICIAL_SOURCES.md
│   ├── FACTS.md
│   ├── HYPOTHESES.md
│   ├── KILLS.md
│   └── HOSTED_LEDGER.md
├── coordination/
│   ├── BOARD.md                      # coordinator만 갱신
│   ├── HANDOFF_CURRENT.md
│   ├── proposals/{gemini,claude}/
│   └── buzz/                         # 한 메시지당 한 원자적 JSON 파일
├── releases/<candidate_id>/
│   ├── submission.tar.gz
│   ├── manifest.json
│   └── validation.log
└── private_artifacts/                # gitignored raw replay/data
```

`experiments`는 질문과 결과의 원장이고, `releases`는 실제 제출 가능한 고정 물건이며, `evidence/HOSTED_LEDGER.md`는 Kaggle에서 돌아온 외부 결과다. 세 영역을 섞지 않는다.

### 5.3 세 agent를 최대한 활용하는 역할과 검증 순환

`Gemini Pro`, `Claude Pro`, `Codex Plus`는 구독명이지 재현 가능한 모델 식별자가 아니다. 매 작업에 실제 client, model, reasoning 수준, 날짜, cwd, 권한을 기록한다. 상위 reasoning 모델은 규칙·엔진 충돌 판정, 새 정책 설계, 최종 승격 심사에 우선 배치하고, 반복 실행·로그 정리에는 빠른 모드를 써도 된다.

| Agent | 1차 책임 | 쓰기 허용 경로 | 독립 검증 책임 |
|---|---|---|---|
| Gemini | 공식 문서·엔진 patch 감시, replay/meta 데이터 분석, 반례 수집 | `environment/` 제안, `coordination/proposals/gemini/` | Claude의 전략 전제가 엔진과 일치하는지 검사 |
| Claude | 경제·게임 가설 제안, 실험 사전등록, red-team 및 실패면 설계 | `experiments/cards/`, `coordination/proposals/claude/` | Codex 결과가 가설을 실제로 검증했는지 검사 |
| Codex | 코드, 테스트, arena, build, exact artifact 통합 | `main.py`, `src/`, `tests/`, `tools/`, `releases/` | 제안의 구현 가능성·시간·패키지 계약 검사 |
| 사람 | 계정·팀·규정 확인, 외부 제출 승인, 최종 active slot 결정 | `coordination/BOARD.md`, hosted ledger 승인 | 자동화가 넘을 수 없는 외부 상태와 책임 확인 |

역할은 “이 모델이 항상 이 일을 더 잘한다”는 가정이 아니라 충돌 방지용 1차 소유권이다. 중요한 변경은 반드시 `제안자 → 구현자 → 독립 검증자 → 사람 승인` 순환을 거치며, 제안자가 자기 결과를 단독 승인할 수 없다.

### 5.4 Buzz와 handoff 프로토콜

공유 `buzz.md`를 여러 agent가 동시에 append하지 않는다. `coordination/buzz/YYYYMMDD-HHMMSS-<agent>-<task>.json`처럼 한 메시지당 한 파일을 원자적으로 생성한다.

필수 필드:

```text
task_id, created_at, agent_client, model, base_sha,
owner, status, owned_paths, claim_type,
claim, evidence, artifact_path, artifact_sha256,
verification, risk, next_action
```

상태는 `CLAIMED → IN_PROGRESS → REVIEW → DONE` 또는 `BLOCKED`만 쓴다. lease 만료시간을 두고, coordinator만 `BOARD.md`를 수정한다. runtime integrator인 Codex 외 agent는 `main.py`, Git index, release를 건드리지 않는다. 같은 폴더에서 branch checkout, rebase, stash를 병렬 실행하지 않는다.

handoff는 다음 한 줄 요약과 증거를 붙인다.

```text
VERDICT | 핵심 사실 2개 | exact path + SHA-256 | 실행한 검증과 결과 | NEXT ACTION
```

### 5.5 프로젝트 지침 작성안

루트 `AGENTS.md`는 장황한 전략 문서가 아니라 다음 계약만 담는다.

1. **Objective:** 평균 현금이 아니라 공식 W/D/L 및 최종 B–T 강도 최적화.
2. **Authority:** Rules/Overview/Staff → pinned engine/source → hosted same-window → local → community 순서. 영역이 다르면 해당 영역의 공식 출처를 우선.
3. **Evidence:** 모든 수치와 결론에 위 여섯 꼬리표, URL 또는 file:line, command, exit code, seed/config, raw result path와 SHA를 기록.
4. **Ownership:** 한 파일 한 writer, Codex만 runtime/release 통합, 겹치는 수정과 병렬 Git 상태 변경 금지.
5. **Experiment contract:** parent, 정확히 한 변경요인, 가설, 실패면, 금지 해석, opponent mix, seed·seat, 평가식, 표본 수와 성공/실패/다음 행동을 실행 전에 기록.
6. **Runtime contract:** 네트워크 없음, 합법 action, 내부 deadline과 결정론 fallback, 720턴 양 좌석, clean extract/import, package size와 dependency 검사.
7. **Promotion:** local 결과만으로 hosted 우위를 주장하지 않음. exact artifact와 registry check 없는 제출 금지.
8. **External action:** Kaggle 제출·팀 변경·코드 공개는 사람 승인 없이는 실행하지 않음.
9. **Failure scope:** 구현 실패, 운영 결정, 넓은 전략 가설의 상태를 분리. KILL에는 재검토 조건 포함.
10. **Handoff:** 위의 고정 형식 사용, 완료 조건과 실제 검증 명령을 명시.

Codex는 루트 `AGENTS.md`를 사용한다. Claude용 `CLAUDE.md`에는 `@AGENTS.md`, Gemini용 `GEMINI.md`에는 `@./AGENTS.md`를 두고 실제 로드된 내용을 각 client의 memory/context 명령으로 확인한다. 단순히 `Follow AGENTS.md.`라고 쓰거나 symlink 지원을 가정하지 않는다. 근거: [Codex AGENTS.md 안내](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Claude Code memory/import](https://code.claude.com/docs/en/memory), [Gemini CLI context/import](https://geminicli.com/docs/cli/gemini-md/)

### 5.6 정책 구조

런타임은 복잡한 end-to-end 학습기보다 검증 가능한 계층형 controller로 시작한다.

1. `state.py`: 관측 파싱, 규칙 invariant, 공개/비공개 정보 표시.
2. `planner.py`: 하루·phase의 기본 계획을 만들되 market, shop, opponent, deadline 변화 시 bounded replan.
3. `allocator.py`: farmer/hand별 위치, 소지품, 목적지, 작물·동물 deadline을 비용으로 삼아 충돌 없는 action 배정.
4. `economy.py`: 구매·토지·고용·작물·동물의 남은 기간 ROI, shed overflow, 시장 충격과 final liquidation 계산.
5. `opponent.py`: 공개 farm·money·position과 시장 변화로 상대의 가능한 inventory 및 다음 행동 분포를 추정.
6. `safety.py`: 불법·중복 action 제거, 내부 deadline 감시, 마지막으로 검증된 deterministic fallback 반환.

고정된 24턴 행동 전체를 캐시하지 않는다. 비싼 계산 결과와 경로 후보만 캐시하고, 매 호출에서 상태 fingerprint와 deadline을 확인한다.

### 5.7 실험 순서

#### Phase A — 환경과 baseline

1. `kaggle-environments==1.32.7`과 source/config hash를 고정한다.
2. 공식 `pass`, `random`, `starter`를 end-to-end 실행하고 720턴·양 좌석·replay 저장을 검증한다.
3. 규칙에 맞는 deterministic baseline을 만들고 invalid action, exception, timeout을 0으로 만든다.
4. actual tarball을 clean temp에 풀어 import/self-play하는 release test를 만든다.

#### Phase B — 한 번에 한 축만 바꾸는 게임 가설

다음은 사실이 아니라 우선순위가 높은 실험 lane이다.

1. `[HYPOTHESIS]` 고용손 수·고용 시점·토지 확장의 남은 기간 ROI와 routing 결합.
2. `[HYPOTHESIS]` 현재 town shop과 시장 재고에 적응하는 crop/animal mix가 고정 조합보다 강함.
3. `[HYPOTHESIS]` shed 100과 동시 주문을 반영한 hold/batch/sell 정책이 즉시 전량 판매보다 강함.
4. `[HYPOTHESIS]` 공개된 상대 생산·현금·위치 기반 belief와 counter-policy가 정적 정책보다 강함.
5. `[HYPOTHESIS]` final day만이 아니라 작물 수명·이동·시장 충격에서 역산한 liquidation scheduler가 고정 날짜 중단보다 강함.
6. `[HYPOTHESIS]` 거위/비료, carrot, melon 등 원본 계획의 구체 전략은 동일한 ROI·상대별 gate를 통과할 때만 채택.

#### Phase C — 상대 과적합 방지

opponent zoo는 최소한 `pass`, `random`, `starter`, 현재 local champion, 구조가 다른 공격적·보수적·시장조작·rush policy와 합법적으로 수집한 공개 강자를 포함한다. 공개 강자는 URL·license·engine version을 기록한다.

같은 seed에서 A/B를 모두 좌석 교대해 비교한다. 이는 common random numbers로 환경 변동을 줄이기 위한 것이다. 모든 agent가 볼 수 있는 seed는 `holdout`이라 부른다. 진짜 blind 평가는 코드와 config를 먼저 freeze한 뒤 사람이 새 seed를 생성하여 평가하고, 집계가 끝나면 그 seed set을 다시 쓰지 않는다.

#### Phase D — 사전등록된 승격 판정

각 candidate card에 다음을 실행 전에 적는다.

- candidate ID, parent ID, source commit, engine/runner version
- 정확히 한 변경 요인
- 가설과 구조적 이유
- 독립 근거와 예상 실패면
- opponent별 seed 수, 좌석 교대, primary score 정의
- 성공, 실패, inconclusive 기준과 금지 해석
- timeout/invalid/exception 및 latency headroom 기준
- 성공·실패 각각의 next action

primary score는 seed-pair 단위 `win=1, draw=0.5, loss=0` 차이이며 opponent별 W/D/L과 paired confidence interval을 같이 본다. pilot으로 분산과 최소 검출 효과를 정한 뒤 고정 표본으로 평가한다. 계속 들여다보다가 좋아 보일 때 멈추지 않는다. 평균·중앙 bank 차이, shed loss, 생산량, p50/p95/p99/max latency는 진단값이다.

승격 조건은 다음을 모두 만족해야 한다.

1. 사전 선언한 target opponent mix에서 parent 대비 실질 효과와 통계적 불확실성 기준 통과.
2. 핵심 상대별 predeclared non-inferiority 기준 통과.
3. 전체 720턴 양 좌석 stress에서 invalid, exception, timeout 0.
4. 실제 tarball의 clean extract/import/self-play와 package/dependency/license 검사 통과.
5. source, config, release, raw result SHA가 registry에 있고 exact duplicate가 아님.

#### Phase E — hosted evidence와 최종 두 slot

로컬 승격 후에도 사람이 exact artifact SHA를 확인하고 제출한다. ledger에는 submission ID, artifact SHA, 제출 시각, engine/module version, active 여부, validation 결과, episode ID·상대·좌석·결과·rating 시각을 기록한다.

- Slot A: 가장 강하고 안정적이며 충분한 hosted episode 근거가 있는 incumbent.
- Slot B: Slot A와 다르기 때문이 아니라, 독립적으로 강하다는 근거가 있는 challenger. 상성 보완은 추가 장점일 뿐 필수조건이 아니다.
- 새 제출이 incumbent를 active 두 자리 밖으로 밀어내기 전에 예상 이득, 잃는 경기 이력, 남은 수렴 시간을 함께 심사한다.
- 서로 다른 시간·게임 수의 live rating만 비교하지 않는다. 가능한 한 같은 창의 상대별 episode와 불확실성을 비교한다.
- 계정의 현재 제출이 0개라면 안정 baseline을 일찍 올려 validation과 hosted 데이터 경로를 먼저 검증한다. 현재 제출 수가 확인되지 않았으므로 이 조건은 아직 `N/A`다.

### 5.8 2026-09-03부터의 일정

| 기간 | 산출물과 종료 조건 |
|---|---|
| 09-03~09-04 | Rules/Overview/Staff/engine snapshot, `==1.32.7` lock, 저장소와 폴더 골격, 공식 starter end-to-end. |
| 09-05~09-08 | deterministic baseline, arena, 양 좌석 paired runner, replay parser, clean release test. 모든 720턴 stress가 timeout/invalid 없이 끝나야 함. |
| 09-09~09-16 | 고용·토지·routing, 생산 mix, market/shed, liquidation을 한 축씩 실험. 실패 lane은 범위를 적어 종료. |
| 09-17~09-22 | opponent belief, counter-policy, zoo·holdout 검증. 팀 구성과 merger 조건을 09-23 23:59 UTC 전에 확정. |
| 09-23~09-24 | entry/team gate 재확인. 최고 candidate의 hosted validation과 episode 상태 점검. 급한 구조 변경 중단. |
| 09-24~09-27 | 최종 후보 2개 독립 blind/holdout·stress·license·artifact audit. Slot A incumbent는 정당한 승격 증거 없이 교체하지 않음. |
| 09-28~09-29 | exact tarball freeze, SHA/manifest/registry 확인, 사람이 여유 있게 최종 제출. validation error 수정 외 신규 아이디어 금지. |
| 09-30 23:59 UTC 전 | active ID 두 개와 artifact 매핑을 마지막으로 확인. 마지막 순간 교체 금지. KST 마감은 10-01 08:59. |
| 10-01~약 10-15 | 제출 변경 없이 episode/error/active 상태 모니터링, 최종 재현 보고서와 source/license bundle 준비. |

## 6. 비전공자를 위한 전체 구조와 데이터 흐름

이 프로젝트는 “아이디어를 바로 Kaggle에 던지는 작업”이 아니라 작은 공장처럼 운영한다.

```text
공식 규칙·고정 엔진
        ↓
검증된 사실 / 아직 모르는 가설
        ↓
한 요소만 바꾼 코드
        ↓
같은 조건·양쪽 자리의 로컬 경기
        ↓
통과/실패/불확실 판정과 원시 증거
        ↓
SHA로 봉인한 실제 제출 tarball
        ↓
Kaggle validation·episode·rating
        ↓
두 active slot 유지 또는 교체 결정
```

Gemini는 원재료인 사실과 외부 변화를 확인하고, Claude는 어떤 실험이 질문에 답하는지 설계하고 반박하며, Codex는 기계를 실제로 만들고 검사한다. 사람은 공장 밖으로 나가는 제출을 승인한다. 파일 hash는 제품의 일련번호라서, 로컬에서 이긴 코드와 Kaggle에 올라간 코드가 같은 물건인지 증명한다.

## 7. 대회 기간 내내 명심할 핵심 세 가지

1. **현금 차이가 아니라 승패 확률을 최적화한다.** 평균 돈과 멋진 전략은 진단 자료일 뿐, 다양한 강한 상대에 대한 W/D/L이 먼저다.
2. **사실·가설·로컬·hosted 증거를 섞지 않는다.** 엔진 버전, seed, 좌석, 상대, 실제 artifact SHA가 없는 성능 주장은 채택하지 않는다.
3. **안정성과 active 이력을 전략의 일부로 본다.** timeout·invalid·미판매 재고를 0에 가깝게 만들고, 최종 B–T에 쓰일 incumbent의 경기 이력을 근거 없이 버리지 않는다.

## 8. 최종 결론

최선의 통합은 “Codex 계획의 증거·release 구조 + Claude 계획의 소스 검증·협업 규율 + Gemini 계획의 KISS”다. 반대로 “Claude의 고정 경제 정답”, “Codex의 반드시 다른 두 slot”, “Gemini의 물 구매·일반 arbitrage”는 폐기한다. 이후의 모든 전략은 공식 엔진에서 재현 가능한 단일요인 실험을 통과한 경우에만 사실에 가까운 운영 지식으로 승격한다.
