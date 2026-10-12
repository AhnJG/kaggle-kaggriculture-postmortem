# Kaggriculture — 솔로 참가 회고: 최고 약 150위(은메달권), 메달 미획득

Kaggle [Kaggriculture](https://www.kaggle.com/competitions/kaggriculture)(2026년 9월, 2인 농장 경영 시뮬레이션, 최종 순위 = Bradley-Terry)에
솔로 팀 **Sian** 으로 참가한 기록이다. 한때 약 150위(당시 은메달권)까지 올랐지만 마감 직전 슬롯 교체로 점수가 다시 쌓이는 상태에서 끝났다.
사람 1명과 LLM 에이전트 여러 개(Claude, Codex, Gemini/Antigravity, GPT-5.6 Sol)가 한 작업 폴더를 나눠 쓰며 운영했다.

**바로 가기** · [실험 로그](experiments/EXPERIMENT_LOG.md) · [운영 회고](plan/kaggriculture_process_retrospective_claude-opus-5.5.md) ·
[멀티에이전트 운영 방식](writeup/multi-agent-workflow.md) · [상위권과 비교](writeup/top-solutions-comparison.md) · [제출한 봇](releases/) · [English summary](#english-summary)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/score_trajectory_dark.png">
  <img alt="팀 점수 추이: 9월 7일 315점에서 9월 10일 tape 재생 봇으로 2188점, 9월 19~23일 동메달선 근처 2420점대, 마감 직전 재제출로 1622점, 10월 12일 최종 평가 중 1686점" src="media/score_trajectory_light.png">
</picture>

| | |
|---|---|
| 제출 | 25회 (하루 5회, 최신 2개만 활성·최종 평가) |
| 최고 순위 | **약 150위** — d157 첫 제출 후 (09-28 무렵, 당시 은메달선 약 505위·2308.7). 본인 관측이며 저장된 스냅샷은 없음 |
| 최고 점수 | **2425.7** — EXP-016, 09-23, 약 808위 / 9,886팀 (당시 동메달선 2346.1) |
| 마감 직후 | 1622.2, 1,855위 / 10,230팀 (10-01 05:47 KST, 재제출본이 600점부터 재수렴 중). 동메달선 1852.0 |
| 최종 평가 중 | **1686점, 1,558위** (10-12 확인. 최종 BT 평가는 10/15 무렵까지 진행) |

## 한 줄 요약

직접 짠 규칙기반 봇(≈340)은 상위 봇에게 400판 중 한 판도 못 이겼다. 상위권처럼 **잘 된 경기의 행동 기록(tape)을 재생하는 봇**으로 바꾸자 2,188점이 됐고,
그 시점 가장 강한 공개 계보를 골라 판매 레이어를 얹어 2,425.7까지 올랐다. 이후의 미세 개선은 **로컬에서 이긴다고 나와도 실전에서는 재현되지 않았고**,
마지막 이틀의 잦은 슬롯 교체가 점수를 처음부터 다시 쌓게 만들었다.

## 내 역할

1인 팀이다. 코드와 문서 대부분은 AI 에이전트가 썼고, 나는 **연구 운영자**로서 문제를 정의하고, 에이전트들이 일하는 규칙을 설계하고,
방향 전환과 제출을 결정했다. 이 저장소가 보여 주려는 것은 봇의 성능보다 이 과정이다.

**설계한 것**
- **운영 체계**: 에이전트 셋에게 각자 계획서를 쓰게 한 뒤 서로 검토시켜 정본 하나로 합치는 방식에서 출발했다. 한 작업 폴더를 에이전트별 소유 경로로 나누고,
  [`AGENTS.md`](AGENTS.md) 계약을 모든 에이전트가 따르게 했다.
- **증거 규칙**: 측정 없는 주장 금지, 수치에는 재현 명령 필수([FACTS](evidence/FACTS.md)), 이미 죽은 가설은 재검토 조건 없이 다시 꺼내지 않기([KILLS](evidence/KILLS.md)),
  이전 세션의 결론은 "검증됨" 표시가 있을 때만 사실로 받기, 모호하면 추측하지 말고 멈추기(BLOCKED), 실행마다 독립 검토 붙이기.
- **역할과 비용 배분**: 판단이 필요 없는 수집·실행은 Antigravity, 판단은 Codex·Claude, 마지막 결정 검토는 외부 모델(GPT-5.6 Sol)에 맡겼다.
  사용량이 바닥나는 문제가 생기자 지시서를 한 번에 대기·보고하는 형식으로 바꾸게 했다.

**주요 결정과 결과**

| 날짜 | 결정 | 결과 | 기록 |
|---|---|---|---|
| 09-02~06 | 계획서 3개를 교차 검토해 정본 1개로 합침. 첫 제출은 성능이 아니라 파이프라인 검증용 | 세 계획서 모두에서 경제 모델 오류를 찾아냄. v0 제출 314.8 | [`plan/kaggriculture_final_plan.md`](plan/kaggriculture_final_plan.md) |
| 09-10 | **RESET**: 직접 짠 실행기를 버리고 tape router 로 전환. 검증 gate 가 HOLD 를 냈지만 공개 9위 무수정본 제출 | 343.9 → **2188.4**. HOLD 는 gate 정의 오류(F-T7)였음 | [`RESET_2026-09-10.md`](coordination/RESET_2026-09-10.md) |
| 09-16 | 목표를 "점수 유지"에서 **"최소 동메달"**로 바꾸고, 09-18 공개 최강 계보를 바로 내는 fast lane 승인 | 다음 날 **2421.6, 동메달권** | `coordination/proposals_claude.md` 의 `20260916-BRONZE-TARGET-PLAN` |
| 09-22 | 사전등록 판정이 INCONCLUSIVE 인 EXP-016 을 실전 실험으로 제출 | **2425.7, 대회 최고** | [EXP-016](experiments/cards/EXP-016-c1-sale-advance.md) |
| 09-25 | 하루 1실험 대신 "동결한 목표 지표 + 에이전트 자율 탐색 + 사전 고정 holdout" 방식으로 전환 | 지표 calibration 에서 변별력 ≈0 → 루프 중단. 로컬 평가기를 먼저 검증해야 한다는 음성 결과 | `coordination/proposals_claude.md` 의 `20260925-SEARCH-LOOP-CODEX` |
| 09-27 | "메달권 밖이면 위험 감수"를 "사전 고정 FAIL 은 뒤집지 않는다"보다 우선 | d157 제출 → **2400.9, 최고 약 150위**. 같은 방침의 c26·L4p 는 실전에서 재현 안 됨 | [`experiments/exp035_d157/`](experiments/exp035_d157/) |
| 09-28~29 | 외부 독립 검토자(Sol) 도입. 두 슬롯이 같은 계열이라 함께 무너질 위험이 있다고 보고 한 슬롯을 다른 방식으로 분산 | Sol 7회 검토, 사후 문턱 완화 반대 의견을 채택. 분산 봇 X 는 1658.1 | `coordination/reports_sol.md` |
| 09-30 | 제출 실행을 Claude 에 위임하고 21:00 KST 를 새 후보 시한으로 고정. 최종 조합 {L4p, d157} 결정 | 마감 시점 활성 두 슬롯 | `coordination/reports_claude.md` 의 `20260930-2335-EXP062-FINAL-A` |

**돌아보면**
- 가장 큰 점수 상승 두 번은 공개 최강 봇을 그대로 낸 날이었다. 처음부터 "AlphaGo 처럼 기존 상위권 전략을 흡수하자"는 방향을 제안했고, 이는 상위권이 실제로 쓴 방법(리플레이 행동 복제)과 같은 방향이었다. 그러나 에이전트가 쓴 계획의 "그대로 제출하면 클론이 된다"는 권고와 내가 정한 "규칙기반 + 좁은 ML까지만"(09-06) 범위를 함께 승인했다. 그래서 공개 봇 제출은 8일째에야 나왔고, 행동 복제는 끝내 시도하지 않았다.
- 사전등록으로 실험 판정은 엄격하게 했지만, 판정을 넘어 제출할 조건은 미리 정하지 않았다. 그 결과 6건 이상을 그때그때 판단했다(최고점도, 실패도 거기서 나왔다).
- 대회가 끝난 뒤 에이전트에게 [실험 로그](experiments/EXPERIMENT_LOG.md)와 [운영 회고](plan/kaggriculture_process_retrospective_claude-opus-5.5.md)를 별도로 쓰게 해서
  내 결정을 포함한 전 과정을 다시 평가했다. 다음 대회용 계약 개정안(AGENTS.md v2)도 거기서 나왔다.

## 접근 방식

### 봇 구조

제출 봇은 모두 공개 Apache-2.0 계보 파일을 바이트 그대로 두고, 끝에 우리 wrapper 를 덧붙이는 형태다(엔진 진입점 = 파일의 마지막 callable).

```mermaid
flowchart LR
    O["관측 obs"] --> W["우리 wrapper<br/>예: exp062_entry"]
    W --> P["공개 계보 봇 (바이트 그대로)<br/>예: tetsutani 55be5d5f"]
    P --> R["router<br/>상황에 맞는 route 선택"]
    R --> T["route = 기록된 719턴 행동 tape 재생"]
    P --> Y["판매·보관·구조 레이어<br/>(공개 계보가 쌓아 온 것)"]
    W -.->|"상수 1개 변경 (d157)<br/>판매 앞당김 (L4p)"| Y
    T & Y --> A["행동 action"]
```

### 실험 루프

```mermaid
flowchart LR
    H["가설<br/>HYPOTHESES.md"] --> C["사전등록 카드<br/>1요인 변경 · 상대 · seed · 숫자 임계"]
    C --> L["로컬 판정<br/>paired arena · hosted 경기 tape 재생<br/>(Kaggle kernel 병렬)"]
    L --> V{"PASS / FAIL /<br/>INCONCLUSIVE"}
    V --> S["제출 결정<br/>(사람)"]
    S --> K["hosted 관측<br/>HOSTED_LEDGER"]
    K -.->|"패배 경기 부검"| H
```

### 단계별 흐름

| 단계 | 기간 | 질문 → 결론 | 점수 |
|---|---|---|---|
| 0 계획·측정 장비 | 09-02~06 | 에이전트 셋의 계획서를 교차 검토해 정본화, 엔진 고정, paired arena·무음 실패 계측기 | — |
| 1 규칙기반 봇 | 09-07~09 | 직접 짠 실행기로 상위 봇을 이길 수 있나? → 공개 4봇 상대 **0/0/400** | 315 → 344 |
| 2 RESET → tape router | 09-10~15 | 공개 9위 tape router 무수정 복제 → 우리 실행기를 929/11로 압도 | **2188** → 1863 |
| 3 정합성·귀인 | 09-16~18 | release gate·패배 원인 귀인. 측정은 정밀했지만 제출 개선 없음 | 1863 → 1638 |
| 4 공개 계보 갈아타기 | 09-19~24 | 공개 최강 계보 exact 복제를 돌려가며 제출, 판매 레이어 이식(EXP-016) | **2422 → 2426** |
| 5 동결 지표 탐색 | 09-25~27 | 자동 탐색용 지표 calibration → 변별력 ≈0으로 중단. 상수 ±1 screen으로 d157 | 2190 → 2401 |
| 6 d157 개선·분산 | 09-28~29 | 판매 hook·상대 모형·생산 재설계·route 재배정 → 대부분 FAIL | 2381 → 1862 |
| 7 마지막 날 | 09-30 | hosted 542판 진단 → glut lead(L4p). 최종 {L4p 사본, d157 사본} | 1622 (재수렴 중) |

## 무엇이 통했고 무엇이 안 통했나

| 통한 것 | 근거 |
|---|---|
| 규칙기반 → tape 재생 계열 전환 | hosted 343.9 → 2188.4 ([RESET](coordination/RESET_2026-09-10.md)) |
| 그 시점 최강 공개 계보를 exact 로 따라가기 | lynnsakurai v2 2421.6, 127ed3e6 2314.7 |
| 판매 레이어 이식 (V53 sale-advance → C1) | 2425.7, 대회 최고 ([EXP-016](experiments/cards/EXP-016-c1-sale-advance.md)) |
| 강한 계보 + 상수 1개 | d157 2400.9, 최고 약 150위 ([EXP-035](experiments/exp035_d157/PREREG.md)) |
| hosted 경기를 tape 로 재생해 상대 재현 | 163/163, 136/136, 107/107 경기 일치 |
| 엔진 소스로 직접 확인 | 상점 해금 3일/8개, 진입점 = 마지막 callable ([FACTS](evidence/FACTS.md)) |

| 안 통한 것 | 근거 |
|---|---|
| 직접 짠 실행기와 작물·흡수량 조정 | 공개 4봇 0/0/400 ([EXP-002](experiments/cards/EXP-002-crops.md), [EXP-003](experiments/cards/EXP-003-absorption.md)) |
| tape 위에서 매도 레이어만 교체 | 농장 계획이 어긋남 ([EXP-005](experiments/cards/EXP-005-x1-probe.md)) |
| 첫 턴 시장 일정 같은 국소 수리 | 회귀 72건 ([EXP-008](experiments/cards/EXP-008-opening-liquidity.md)) |
| 상수 ±1 대량 탐색 (2라운드 이후) | 지던 상대에게 ±1 변형 0/171, d157 ±1 158개 변형 최고 +0.01 (EXP-025, EXP-036) |
| 상대 예측·판매 hook, 생산 재설계(토마토·거위) | EXP-045~057의 개선 후보 전부 FAIL ([실험 로그 §5](experiments/EXPERIMENT_LOG.md)) |
| 자동 탐색 루프용 동결 지표 | calibration BLOCKED, 변별력 ≈0 |

### 로컬 판정과 실전 결과 대조 (CV ↔ LB)

같은 계보 안의 미세 변경은 로컬 우위가 실전에서 거의 재현되지 않았다. 다른 계보끼리의 큰 차이는 맞았다.

| 제출 | 로컬 근거 | 실전(hosted) | 일치 |
|---|---|---|---|
| lynnsakurai v2 exact | round-robin 0.9667 (1위) | 2421.6, 당시 최고 | ✓ |
| 127ed3e6 exact | vs DP 0.821 | 2314.7 > DP 2191.6 | ✓ |
| d157 | tape vs v074 +0.29 | 2400.9 vs v074 2215.9 | ✓ |
| EXP-017 | vs EXP-016 **78/0/2** | EXP-016보다 **−165.6** | ✗ |
| c26 | tape vs d157 +0.033 | 1,887~1,940 vs d157 ~2,200 | ✗ |
| X (Rc26_107) | holdout 0.571 vs d157 0.462 | 1658.1 vs d157r 1888.4 | ✗ |

전체 19건 대조와 원인 분석은 [실험 로그 §7](experiments/EXPERIMENT_LOG.md).

## 왜 메달을 못 땄나

1. **로컬과 실전이 어긋나는 것을 계속 확인했으면서도, 그 어긋남을 해결하기 전에 로컬 지표로 후보를 골랐다.** 어긋남은 처음부터 여러 번 관측했다.
   - 09-07: v0 이 로컬에서 starter 를 크게 이겼지만 실전 337점이었고, 그래서 판정 기준을 공개 상위 봇 상대로 바꿨다([`AGENTS.md`](AGENTS.md) §7.1).
   - 09-10: tape 품질과 그 소유자의 실전 순위가 무관했다([FACTS](evidence/FACTS.md) F-T2).
   - 09-11: 로컬 점수가 실전을 예측하는지 보려고 [EXP-005](experiments/cards/EXP-005-x1-probe.md)를 설계했지만, 안전 기준에 걸려 제출하지 못했다.
   - 09-23: 같은 계열 형제끼리의 로컬 대결이 실전 순위를 못 맞혔다는 기록을 남겼다([HOSTED_LEDGER](evidence/HOSTED_LEDGER.md)).

   그러나 계약이 요구한 "로컬 · 공개 봇 · 실전" 삼중쌍 표는 끝내 만들지 않았다. 지표 하나를 고정해 체계적으로 검증(calibration)한 것은 09-25가 처음이었고, 결과는 변별력 ≈0(BLOCKED)이었다.
   그 뒤에도 같은 계열 미세 변경을 로컬 지표로 골라 제출했다.
2. **가장 큰 상승 두 번은 모두 "공개 최강 봇을 그대로 낸 날"이었고, 그 결정이 늦었다.** 대회 시작 후 8일, 17일째였다.
   첫 번째가 늦은 이유는 초기 계획이 공개 봇을 기준선·상대·분석 대상으로만 쓰고 그대로 제출하지 말라고 권했기 때문이다.
   그 근거는 "수천 팀의 클론과 같은 봇이 된다", "공개 포크는 금방 죽은 계통이 된다"였다(Claude 작성, [09-03](plan/kaggriculture_strategy_transfer.md) · [09-06](plan/kaggriculture_master_plan_claude-opus-5.md)).
   공개 코드 파생물을 허용한 것은 09-11이다. 두 번째는 그 뒤에도 공개 계보 위에 우리 변경을 얹는 실험과 정합성 작업을 먼저 하느라 늦어졌다.
3. **판정과 제출 결정을 분리하지 않았다.** 사전등록 FAIL·INCONCLUSIVE 를 사람 결정으로 넘어선 제출이 6건 이상이었다(그중 EXP-016이 최고점).
   제출 규칙 자체는 미리 정해 두지 않았다.
4. **마지막 이틀 동안 슬롯을 6번 교체했다.** 최종 BT 는 활성 제출끼리의 경기만 세고, 재제출은 600점에서 다시 시작한다.
   같은 바이트의 d157 이 09-28엔 2400.9였지만 09-30 재제출본은 다음 날 아침 1622.2였다(리그 전체 하락분도 섞여 있다).
5. **조율 비용이 컸다.** 실험 62개에 조율 문서 약 440개가 쌓였다. 09-16~18 사흘은 정합성 작업에 쓰는 동안 제출 개선이 없었다.

### 상위권 write-up 과 비교하면

대회 후 공개된 상위권 글 8개(10-12 기준 1·4·5·11·26위 등)를 읽고 비교했다. 위 다섯 가지는 과정의 문제이고, 더 근본적인 차이는 **방식**이었다.

| | 상위권 (1·4·5·11·26위) | 우리 |
|---|---|---|
| 정책 | 상위권 리플레이로 학습한 신경망(행동 복제, BC)이 매 턴 상태를 보고 행동 생성. 1·11위는 그 위에 self-play PPO | 공개 계보의 기록된 행동 tape 재생 + 규칙 레이어 |
| 상대 반응 | 있음 (상태 입력) | tape 는 없음, 덧붙인 레이어만 |
| 경제 | 첫 턴부터 동물 중심 경제 | 계보가 정한 생산 계획 유지, 생산 변경 실험은 모두 FAIL |
| 컴퓨트 | 1위는 GPU 수십 장. 4·5·11위는 GPU 1~2장, 5위는 사전학습 약 50분 | 맥북에어 + Kaggle/Colab |

- **천장은 방식에서 정해졌다.** 같은 tape 계열로 438위를 한 팀은 tape 끼리는 5할 승부이고, 2100점 위 상대는 동물을 키우는 경제형 봇이라고 보고했다.
  우리 최종 봇도 1800–2000점 상대에게 0.45~0.50, 2000–2200점 상대에게 0.29~0.33이었다. 마지막 사흘의 진단과 개선은 tape 계열 안의 싸움이었다.
- **맞는 방향을 처음에 적어 두고 버렸다.** 09-03 [흡수 전략 문서](plan/kaggriculture_strategy_transfer.md)는 리플레이 행동 복제를 "확실한 상위권"으로 평가하고 2~3주차 후보로 잡았지만,
  09-06 범위 결정과 09-10 tape 전환 뒤 다시 다루지 않았다. 5위는 마지막 9일, 26위는 마지막 5일에 BC 로 그 자리에 올랐다.
- **RL 을 막은 KILL(K6)은 반만 맞았다.** 근거는 처음부터 self-play 만 하는 경우였다. 상위권에서 통한 것은 BC 로 출발한 뒤의 PPO 였고, 4·5위는 BC 만으로 충분했다.
- **같은 엔진 지식을 다르게 썼다.** 주문 절삭 같은 무음 처리를 우리는 검증 gate 에만 썼고, 4위는 실제 체결된 행동만 학습 라벨로 써서 큰 이득을 봤다.

출처와 팀별 요약, 다음 대회에 가져갈 것은 [writeup/top-solutions-comparison.md](writeup/top-solutions-comparison.md).

다음 대회용 체크리스트는 [실험 로그 §9](experiments/EXPERIMENT_LOG.md), 운영 방식 개선안은 [회고 §4](plan/kaggriculture_process_retrospective_claude-opus-5.5.md).

## 빠르게 실행해 보기

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.lock pytest            # kaggle-environments==1.32.7, Python ≥ 3.11

# 최종 슬롯 봇(L4p) vs 기본 starter 한 판
python3 - <<'EOF'
from kaggle_environments import make
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 7})
env.run(["releases/exp062-L4p/main.py", "starter"])
print([round(s.reward) for s in env.steps[-1]])     # 최종 은행 잔고 [L4p, starter]
EOF

python3 scripts/verify_engine_facts.py             # 엔진 사실 재현
python3 -m pytest -q tests                         # 하네스 단위 테스트
```

이 저장소에서 확인한 결과(2026-10-12): 위 대전은 seed 7·11 모두 L4p 가 starter 를 이겼다(168,074 대 3,421 / 195,049 대 3,421).
L4p 와 d157 은 같은 두 seed 에서 1승 1패였다. `verify_engine_facts.py` 는 끝까지 돈다.
단위 테스트는 101개 중 91개가 통과하고, 나머지 10개는 이 저장소에서 뺀 입력(공개 노트북 추출본, 생성된 변형 봇, 원시 결과 JSON,
묶음으로 합친 개별 제안서 파일)을 직접 읽는 테스트다. 실험 스크립트 다수도 대용량 원시 입력을 전제로 하므로 그대로는 돌지 않는다.

## 저장소 구조

| 경로 | 내용 |
|---|---|
| [`releases/`](releases/) | 우리가 만들고 검증·제출한 봇 15종. 최종 두 슬롯 = `exp062-L4p`, `exp035-d157` |
| [`experiments/`](experiments/) | 사전등록 카드(`cards/`, `exp*/PREREG.md`), 판정 스크립트, [`EXPERIMENT_LOG.md`](experiments/EXPERIMENT_LOG.md) |
| [`evidence/`](evidence/) | [FACTS](evidence/FACTS.md)(재현 명령이 붙은 사실) · [KILLS](evidence/KILLS.md)(죽은 방향) · [HOSTED_LEDGER](evidence/HOSTED_LEDGER.md)(제출 원장) · 엔진 사실 · 부검 |
| [`analysis/`](analysis/) | hosted 경기 지도, 패배 분석, 상대 식별, 커뮤니티 조사 메모 |
| [`tools/`](tools/) [`tests/`](tests/) [`scripts/`](scripts/) | arena, 계측기, 탐색 루프, gate 검증, 리플레이 재현·부검 / 단위 테스트 / 엔진 사실 재현·수집 |
| [`plan/`](plan/) | 모델별 계획서, 마감 계획, 회고 |
| [`coordination/`](coordination/) | BOARD · TASKS · HANDOFF · RESET, 에이전트별 보고·제안 묶음 |
| [`writeup/`](writeup/) | 이 저장소용으로 새로 쓴 정리 문서 |
| [`AGENTS.md`](AGENTS.md) [`CLAUDE.md`](CLAUDE.md) [`GEMINI.md`](GEMINI.md) [`HYPOTHESES.md`](HYPOTHESES.md) | 에이전트 계약·역할, 공용 가설 원장 |
| [`media/`](media/) | README 그림과 생성 스크립트 |

**읽는 순서** — 무엇을 했나: [실험 로그](experiments/EXPERIMENT_LOG.md) §1 → §3 제출 원장 → §5 실험 대장 → §7 CV↔LB.
어떻게 일했나: [멀티에이전트 운영](writeup/multi-agent-workflow.md) → [운영 회고](plan/kaggriculture_process_retrospective_claude-opus-5.5.md).
실험 하나를 자세히: [`experiments/cards/`](experiments/cards/) 의 카드나 [`experiments/exp062/PREREG.md`](experiments/exp062/PREREG.md).

`coordination/reports_<agent>.md`, `proposals_<agent>.md` 는 원래 개별 파일(보고 222건, 제안·지시서 150건)을 에이전트별로 시간순으로 이어 붙인 묶음이다.
각 절 제목이 원래 경로이므로, 다른 문서가 `coordination/reports/claude/2026...md` 를 인용하면 해당 묶음에서 그 경로로 검색하면 된다.
문서 안의 다른 경로는 원래 작업 폴더 기준이며, 아래 "포함하지 않은 것"에 해당하는 경로는 이 저장소에 없다.

## 멀티에이전트 운영

에이전트마다 쓰기 소유 폴더를 나누고, `AGENTS.md` 계약(진실의 순위, 증거 꼬리표, 한 파일 한 writer, "모호하면 BLOCKED", 사전등록)과
파일만으로 소통했다. 엔진 확인 습관과 독립 검토는 실제 오류를 여러 번 걸렀지만, 판단 왕복마다 문서가 쌓여 조율 비용이 실험 비용보다 컸다.
역할, 채널, 통한 것과 비쌌던 것, 다음에 바꿀 것은 [writeup/multi-agent-workflow.md](writeup/multi-agent-workflow.md) 에 정리했다.

## 포함하지 않은 것

| 제외 | 이유 |
|---|---|
| 원시 리플레이·경기 결과(`private_artifacts/`, `analysis/**/replays`, `evidence/raw`, `*.jsonl`, 판정·요약 외 결과 JSON), 약 45GB | 용량. 재수집 가능 |
| 대량 생성된 후보 봇(상수 변형 수천 개)과 Kaggle kernel 출력 | 용량. 생성 스크립트는 포함 |
| 남이 쓴 공개 노트북 원본(`releases/public-*-exact`, `opponents/`, 원 작업 폴더의 `docs/`, `**/extracted`, 다운로드한 상대 봇) | 우리 저작물이 아님. 출처는 [`environment/LICENSES.md`](environment/LICENSES.md) |
| 대회 데이터, 리더보드 CSV | 재배포하지 않음 |
| 자격증명(`kaggle.json`), 개인 경로·연락처·Kaggle 계정명 | 보안. 로컬 경로는 `~`, 계정명은 `<kaggle_user>` 로 치환 |
| 일회성 루트 스크립트, `scratch/`, 가상환경 | 정리 |

git 이력은 원래 작업 폴더의 91개 커밋을 가져오지 않고 이 정리본에서 새로 시작했다(이전 이력에 대용량 리플레이가 섞여 있었다).

## English summary

**What this is.** A post-mortem of a solo entry (team *Sian*) in Kaggle's *Kaggriculture* (Sep 2026; two-player, 720-turn farming
simulation; final ranking by Bradley-Terry over matches between each team's two active submissions). It contains the harness and
analysis tools, every bot we derived and submitted, pre-registered experiment cards and verdicts, and the coordination log of a
human working with several LLM agents (Claude, Codex, Gemini/Antigravity, GPT-5.6 "Sol") in one shared folder.

**Result.** 25 submissions. Peak rank **~150th** after the first d157 submission (around 2026-09-28, inside the silver zone at the time; self-observed, no saved snapshot). Best observed rating **2425.7** (EXP-016, ~808th of 9,886, above that day's bronze line of 2346.1).
Both slots were resubmitted at the deadline and were re-converging from 600; last observed **1622.2, 1,855th of 10,230**
(2026-10-01); **1686, 1,558th** on 2026-10-12 while final Bradley-Terry evaluation was still running. No medal.

**My role.** Solo team. AI agents wrote most of the code and documents; I acted as the research lead. I set up the
operating system: plans cross-reviewed by three agents, one shared folder with per-agent ownership, and the agent contract
([`AGENTS.md`](AGENTS.md)). I also set the evidence rules: no claim without a measurement, a reproduction command for every
number, no reopening a killed hypothesis without its stated re-test condition, and BLOCKED instead of guessing. The strategic
calls were mine: abandoning our own executor for tape replay (343.9 → 2188.4), switching the goal to "secure bronze" (2421.6
the next day), submitting an INCONCLUSIVE experiment (EXP-016, the competition best), adding an external reviewer model, and
choosing the final pair. In hindsight, I adopted public lineages too late and never pre-registered a submission policy
separate from experiment verdicts.

**Trajectory.** Hand-written rule-based bot (≈340, 0/0/400 against top public bots) → replaying recorded action tapes like the top
teams (≈2,190) → rotating exact copies of the strongest public lineage plus a ported sale layer (≈2,420) → one-constant searches
(d157, ≈2,400) → late attempts to beat the opponents we were actually losing to.

**Why no medal.**
1. We saw local-vs-ladder mismatches from the first week (v0, tape-quality vs owner rank, the EXP-005 probe design, EXP-016/017),
   but never built the local/public/hosted comparison table our own contract required, and ran the first systematic calibration only on
   day 24 (no discriminative power). Meanwhile we kept selecting within-lineage variants with local metrics, which almost never
   transferred (EXP-017 beat EXP-016 78/0/2 locally, then scored 165.6 lower).
2. Both big jumps came from submitting the strongest public bot as-is, which we only did on days 8 and 17. The early plan
   (agent-written, human-approved) advised using public bots only as baselines to avoid becoming "one of thousands of clones".
3. Pre-registered verdicts and submission decisions were not separated; at least six submissions overrode a verdict.
4. Six slot changes in the last two days restarted ratings from 600.
5. Coordination overhead (≈440 documents for 62 experiments) outweighed experiment cost.

**Compared with top write-ups.** Every top write-up we read (ranks 1, 4, 5, 11 and 26 as of 2026-10-12) used behaviour
cloning of top replays: a network that reacts to the state, sometimes followed by self-play PPO. We replayed fixed public tapes.
A tape-family team at ~438th reported that tapes split games 50/50 and that opponents above ~2100 are animal-economy bots, which
matches our own 0.29–0.50 win rates against 1800–2200 opponents. Our own 09-03 plan had rated replay behaviour cloning as a
reliable top-tier route, but we dropped it. Details: [`writeup/top-solutions-comparison.md`](writeup/top-solutions-comparison.md).

**Worth reusing.** The agent contract ([`AGENTS.md`](AGENTS.md)), the experiment log format with a CV↔LB table
([`experiments/EXPERIMENT_LOG.md`](experiments/EXPERIMENT_LOG.md)), and the multi-agent write-up
([`writeup/multi-agent-workflow.md`](writeup/multi-agent-workflow.md)). Most records are in Korean.

## 라이선스와 출처

[Apache License 2.0](LICENSE). [`releases/`](releases/) 의 봇은 Apache-2.0 공개 Kaggle 노트북의 파생물이며, 원 저자 표기를 각 `main.py` 안에 그대로 유지했다.
라이선스 전문은 `main.py` 안에 있거나, 제출 바이트를 바꾸지 않기 위해 같은 폴더의 `LICENSE.txt` 로 함께 두었다.
upstream 저자: thomastschinkel, yhay81, destbreso, aurax7, tetsutani, prvsiyan, Dmitrii Gluzdov, Ahmed Berat Ozer, nathanjacob, lynnsakurai 외
(전체 목록과 URL 은 [`environment/LICENSES.md`](environment/LICENSES.md)).
게임 엔진은 [kaggle-environments](https://github.com/Kaggle/kaggle-environments) (Apache-2.0).
