# Kaggriculture — 멀티에이전트로 치른 Kaggle 시뮬레이션 대회 기록

Kaggle [Kaggriculture](https://www.kaggle.com/competitions/kaggriculture) (2인 농장 경영 시뮬레이션, 최종 순위 = Bradley-Terry) 에
솔로 팀 **Sian** 으로 참가한 4주간의 코드, 실험 기록, 의사결정 로그다.
사람 1명과 AI 에이전트 여러 개(Claude, Codex, Gemini/Antigravity, GPT-5.6 Sol)가 한 작업 폴더를 나눠 쓰는 방식으로 운영했다.

---

## English summary

**What this is.** A post-mortem repository for a solo entry in Kaggle's *Kaggriculture* (a two-player, 720-turn farming
simulation; final ranking by Bradley-Terry over matches between active submissions). It contains our harness and analysis
tools, every bot we derived and submitted, pre-registered experiment cards, verdicts, and the coordination log of a
human + multi-agent team (Claude, Codex, Gemini/Antigravity, GPT-5.6 "Sol") working in one shared folder.

**Result.** 25 submissions. Best observed hosted rating **2425.7** (EXP-016, ~808th of ~9,900, inside the bronze zone at the
time). At the deadline both slots had been resubmitted and were re-converging from 600; last recorded **1622.2, 1,855th / 10,230**
(2026-10-01). Final Bradley-Terry results were still being computed when this repository was published.

**Trajectory.** Hand-written rule-based bot (≈340) → switch to replaying recorded action "tapes" from strong public bots
(≈2,190) → rotating exact copies of the strongest public lineage (≈2,420, bronze zone) → one-constant searches on top of the
best lineage (d157, ≈2,400) → last-days attempts to beat the opponents we were actually losing to.

**Main lessons.**
1. *Validate the evaluator before you optimise against it.* Local metrics ranked different public lineages correctly, but
   almost never ranked small variants within one lineage (EXP-017 beat EXP-016 78/0/2 locally, then scored 165.6 lower hosted).
2. *Lineage choice beat our own code.* The big jumps (340 → 2188 → 2420) came from picking which public bot family to run.
3. *Open-loop replay is an upper bound.* Replaying hosted opponents reproduced games exactly (163/163, 136/136), but non-reactive
   opponents made it ~0.17 optimistic on mirror boards.
4. *Late slot changes are expensive.* Only games between the two active submissions count, and resubmissions restart at 600.
5. *Separate "did the experiment pass?" from "what do we submit?"* At least six submissions overrode a pre-registered verdict;
   one of them produced the best score of the competition.

Start with [`experiments/EXPERIMENT_LOG.md`](experiments/EXPERIMENT_LOG.md) (what we tried) and
[`plan/kaggriculture_process_retrospective_claude-opus-5.5.md`](plan/kaggriculture_process_retrospective_claude-opus-5.5.md)
(how we worked). Most records are in Korean.

---

## 결과

| 항목 | 값 |
|---|---|
| 제출 | 25회 (하루 5회, 최신 2개만 활성·최종 평가) |
| 대회 중 최고 | **2425.7** — EXP-016 (09-23, 약 808위, 당시 동메달권) |
| 마감 직후 관측 | 1622.2, 1,855위 / 10,230팀 (10-01 05:47 KST, 재제출본이 600에서 재수렴 중). 같은 시점 동메달선 1852.0 |
| 최종 활성 슬롯 | `L4pc` 56709992 (d157 + glut lead K=4) · `d157c` 56709342 (d157) |
| 최종 BT 순위 | 공개 시점 기준 평가 진행 중 |

점수 궤적 (대표 관측값):

```
09-07  v0 규칙기반 봇                       314.8
09-10  공개 9위 tape router 무수정 복제      2188.4   ← 방식 전환 (RESET)
09-19  공개 lynnsakurai v2 복제              2421.6   ← 동메달권 진입
09-23  EXP-016 (C1 + 판매 레이어 이식)       2425.7   ← 대회 최고
09-28  d157 (공개 55be + 상수 1개)           2400.9
10-01  최종 두 슬롯 (재제출, 재수렴 중)       1622.2
```

제출 25건 전체 원장, 실험 60여 개의 한 줄 대장, 로컬 판정과 hosted 결과 대조표(CV↔LB)는
[`experiments/EXPERIMENT_LOG.md`](experiments/EXPERIMENT_LOG.md) 에 있다.

## 어떻게 접근했나

| 단계 | 기간 | 질문 → 결론 |
|---|---|---|
| 0 계획·측정 장비 | 09-02~06 | 에이전트 3개가 각자 쓴 계획서를 교차 검토해 정본화. 엔진 `kaggle-environments==1.32.7` 고정, paired arena·무음 실패 계측기 구축 |
| 1 규칙기반 봇 | 09-07~09 | 직접 짠 실행기로 공개 상위 봇을 이길 수 있나? → 공개 4봇 상대 **0/0/400** |
| 2 RESET → tape router | 09-10~15 | 상위권은 잘 된 경기의 행동 기록(tape)을 재생한다. 공개 9위 무수정 복제로 343.9 → 2188.4 |
| 3 정합성·귀인 | 09-16~18 | release gate·패배 원인 귀인. 측정 품질은 높았지만 제출 개선 없음 (1862 → 1638) |
| 4 F0 fast lane | 09-19~24 | 공개 최강 계보 exact 복제를 돌려가며 제출 → 동메달권. 판매 레이어 이식(EXP-016)으로 최고점 |
| 5 동결 지표 탐색 | 09-25~27 | 자동 탐색 루프용 지표 calibration → 변별력 ≈0으로 BLOCKED. 상수 ±1 screen으로 v171·v074·d157 |
| 6 d157 개선·슬롯 분산 | 09-28~29 | 판매 hook, 상대 모형, 생산 재설계, route 재배정 — 대부분 FAIL. mirror 판 route 전환 봇(X) holdout PASS |
| 7 마지막 날 | 09-30 | hosted 542판 진단(55be 변형 상대 패배 64%) → glut lead L4p. 최종 조합 {L4p 사본, d157 사본} |

### 핵심 교훈

1. **평가기를 먼저 검증한다.** 로컬 지표가 hosted 방향을 맞히는지 처음 잰 것이 4주차였고 결과는 BLOCKED였다.
   다른 계보끼리의 큰 차이는 로컬이 맞혔지만, 같은 계보 안의 미세 변경은 거의 맞히지 못했다.
2. **점수를 크게 올린 것은 우리 코드가 아니라 계보 선택이었다.** 우리 변경 중 확실한 이득은 d157(상수 1개)과 EXP-016(판매 레이어) 정도다.
3. **open-loop tape 점수는 상한으로 읽는다.** hosted 경기 재현은 정확했지만, 상대가 반응하지 않아 mirror 판에서 +0.17 낙관 편향이 있었다.
4. **슬롯 교체는 비용이다.** 최종 BT는 활성 제출 간 경기만 세고 재제출은 600에서 다시 시작한다. 마지막 이틀에 6번 교체했다.
5. **기록 규율은 실제 오류를 잡았다.** 사전등록·SHA 원장·독립 검토가 stale artifact, wrapper 자기참조, seat 오류, gate 정의 오류를 걸렀다.
   다만 판정(실험 통과 여부)과 제출 결정(포트폴리오)을 분리하지 않아 사람 override가 6번 이상 반복됐다.

자세한 근거와 다음 대회용 체크리스트는 실험 로그 §7–§9, 운영 방식 평가(AGENTS.md·폴더 구조·에이전트 운영)는
[`plan/kaggriculture_process_retrospective_claude-opus-5.5.md`](plan/kaggriculture_process_retrospective_claude-opus-5.5.md) 에 있다.

## 멀티에이전트 운영

- **계약 문서** [`AGENTS.md`](AGENTS.md): 모든 에이전트가 따르는 정본. 진실의 순위(규정 → 엔진 → hosted → 로컬 → 커뮤니티),
  증거 꼬리표(수치에는 재현 명령 또는 `file:line`), 한 파일 한 writer, "모호하면 BLOCKED로 반환", 실패 범위 분리와 KILL 재검토 조건.
  `CLAUDE.md`·`GEMINI.md` 는 이를 import 하고 에이전트별 역할만 덧붙인다.
- **역할**: Claude = 가설·사전등록·red-team·판정 / Codex = 런타임·하네스·release / Gemini→Antigravity = 수집·정형 실행 /
  Sol(GPT-5.6) = 외부 독립 검토 / 사람 = 방침과 제출 결정.
- **채널은 파일**: 에이전트별 소유 폴더와 `coordination/reports|proposals/<agent>/` 로만 소통했다. 메시지 버스는 설계했지만 쓰지 않았다
  ([`coordination/README.md`](coordination/README.md)).
- **사실·가설 원장**: [`evidence/FACTS.md`](evidence/FACTS.md) (재현 명령이 붙은 사실만), [`evidence/KILLS.md`](evidence/KILLS.md) (죽은 방향과 재검토 조건),
  [`HYPOTHESES.md`](HYPOTHESES.md) (공용 가설 원장).

## 저장소 구조

| 경로 | 내용 |
|---|---|
| `AGENTS.md` `CLAUDE.md` `GEMINI.md` | 에이전트 계약과 역할 |
| `HYPOTHESES.md` | 공용 가설·검증 원장 |
| `tools/` | arena, 계측기(`instrument.py`), 탐색 루프, gate 검증, 리플레이 재현·부검 스크립트 |
| `tests/` | 하네스·gate·원장 단위 테스트 |
| `scripts/` | 엔진 사실 재현(`verify_engine_facts.py`), 리플레이 통계, 공개 자료 수집 |
| `configs/` `environment/` | holdout 정책, 고정 seed, 엔진 고정(`ENGINE_LOCK.md`), 외부 코드 provenance(`LICENSES.md`) |
| `releases/<label>/` | 우리가 만들고 제출·검증한 봇 15종: `main.py`, `NOTICE.txt`, `SHA256SUMS`, runtime gate 결과 |
| `experiments/` | 사전등록 카드(`cards/`, `exp*/PREREG.md`), 실행·판정 스크립트, `EXPERIMENT_LOG.md`, `registry.csv` |
| `analysis/` | hosted 경기 지도, 패배 분석, 상대 식별, 커뮤니티 조사 메모와 스크립트 |
| `evidence/` | FACTS · KILLS · HOSTED_LEDGER(제출 원장) · 엔진 사실(흡수량, 동물, 액션 예산 등) · 부검 |
| `plan/` | 모델별 계획서, 마감 계획, 회고 |
| `coordination/` | BOARD · TASKS · HANDOFF · RESET 문서, 그리고 에이전트별 보고·제안 묶음 |

`coordination/reports_<agent>.md`, `coordination/proposals_<agent>.md` 는 원래 수백 개의 개별 파일(보고 217건, 제안·지시서 165건)이던 것을
에이전트별로 시간순으로 이어 붙인 묶음이다. 각 절 제목이 원래 경로이므로, 다른 문서가 `coordination/reports/claude/2026...md` 같은
경로를 인용하면 해당 묶음 파일에서 그 경로로 검색하면 된다. `coordination/hypotheses_events.json` 은 가설 원장 이벤트 96건의 묶음이다.

문서 안의 다른 경로는 원래 작업 폴더 기준이며, 아래 "포함하지 않은 것"에 해당하는 경로는 이 저장소에 없다.

### 주요 봇 (`releases/`)

| 라벨 | 내용 | hosted |
|---|---|---|
| `v0`, `v1-20260910` | 직접 짠 규칙기반 봇 | 314.8 / 343.9 |
| `f0-c1-adv-exp016` | 공개 pipe16 + V53 sale-advance 레이어 (EXP-016) | **2425.7** (최고) |
| `f0-omw-adv-exp017` | OneMoreWheat + sale-advance (EXP-017) | 2100.2 |
| `mirror-screen-v171`, `round2-v074` | 127ed3e6 계열 상수 ±1 screen 결과 | 2337.5 / 2215.9 |
| `exp035-d157` | 공개 55be5d5f + `_S1002_PASSES` 34→35 | 2400.9 |
| `exp039-c26` | d157 + `_CA_MARGIN` −15→−26 | 1939.7 |
| `slot2r-Rc26_107` | mirror 판이면 route 107, 아니면 c26 | 1658.1 |
| `exp062-L3p`…`L6p` | d157 + glut lead K=3…6 (L4p가 최종 슬롯) | L4p 1800.5 |

모든 파생 봇은 Apache-2.0 공개 노트북에서 출발했고, 원 저자 표기와 라이선스 전문을 각 `main.py` 안에 그대로 유지했다.
일부 봇에는 Kaggle에 공개된 경기 리플레이에서 추출한 행동 기록(tape)이 데이터로 들어 있다.

## 재현

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.lock pytest     # kaggle-environments==1.32.7, Python ≥ 3.11
python3 scripts/verify_engine_facts.py      # 엔진 사실 재현
python3 -m pytest -q tests                  # 하네스 단위 테스트
```

이 정리본에서 `verify_engine_facts.py` 는 끝까지 돌고, 단위 테스트는 101개 중 91개가 통과한다. 실패하는 10개는 이 저장소에서 뺀
입력(공개 노트북 추출본, 생성된 변형 봇, 원시 결과 JSON, 묶음으로 합친 개별 제안서 파일)을 직접 읽는 테스트다.
실험 스크립트 다수도 원시 리플레이·공개 노트북 수집본 같은 대용량 입력을 전제로 하므로, 이 저장소만으로는 그대로 돌지 않는다.
필요한 입력은 각 카드의 "검증" 절과 `scripts/fetch_kaggle_updates.py`, `tools/build_public_exact.py` 를 보면 다시 모을 수 있다.

## 포함하지 않은 것

| 제외 | 이유 |
|---|---|
| 원시 리플레이·경기 결과(`private_artifacts/`, `analysis/**/replays`, `evidence/raw`, `*.jsonl`, 결과 JSON) — 약 45GB | 용량. 재수집 가능 |
| 대량 생성된 후보 봇(상수 변형 수천 개)과 Kaggle kernel 출력 | 용량. 생성 스크립트는 포함 |
| 남이 쓴 공개 노트북 원본(`releases/public-*-exact`, `opponents/`, `docs/`, `**/extracted`) | 우리 저작물이 아님. 출처는 `environment/LICENSES.md` |
| 대회 데이터, 리더보드 CSV | 재배포하지 않음 |
| 자격증명(`kaggle.json`), 개인 경로·연락처 | 보안. 남아 있던 로컬 경로는 `~` 로 치환 |
| 일회성 루트 스크립트, `scratch/`, 가상환경 | 정리 |

git 이력은 원래 작업 폴더의 91개 커밋을 가져오지 않고 이 정리본에서 새로 시작했다(이전 이력에 대용량 리플레이가 섞여 있었다).

## 라이선스

[Apache License 2.0](LICENSE). `releases/` 의 봇은 Apache-2.0 공개 노트북의 파생물이며 원 저자 고지를 각 파일에 유지한다
(thomastschinkel, yhay81, destbreso, aurax7, tetsutani, prvsiyan, Dmitrii Gluzdov, Ahmed Berat Ozer, nathanjacob, lynnsakurai 외).
게임 엔진은 [kaggle-environments](https://github.com/Kaggle/kaggle-environments) (Apache-2.0).
