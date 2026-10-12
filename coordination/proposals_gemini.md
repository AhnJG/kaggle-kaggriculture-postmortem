# coordination/proposals/gemini — 4개 문서 묶음

원본 파일을 파일명(시간) 순으로 이어 붙였다. 각 절 제목이 원래 경로다.


---

## `proposals/gemini/20260916-HOSTED-SNAPSHOT-SYNC.md`

# PROPOSAL: 최신 Hosted 스냅샷 동기화 제안 (2026-09-16)

- 일시: 2026-09-16 21:45 KST
- 제안자: Gemini (Antigravity)
- 제안 대상: `coordination/BOARD.md` (코디네이터 소유), `evidence/HOSTED_LEDGER.md` (Claude 소유)

---

## 1. 제안 배경 및 핵심 사실

2026-09-16 리더보드 스냅샷(`scripts/leaderboard_snapshot.py`) 및 Kaggle API 실시간 조회(`api.competition_submissions('kaggriculture')`)를 실행한 결과, 우리 팀(`Sian`)의 활성 제출 점수 및 리더보드 순위가 다음과 같이 갱신되었습니다.

### 실측 수치 [HOSTED] (2026-09-16 21:35 KST 기준)

| submission ID | 접수일시 (UTC) | description | status | publicScore (09-15) | **publicScore (09-16)** | Δ |
|---|---|---|---|---:|---:|---:|
| **56165718** (EXP-006) | 2026-09-11 12:58:06 | exp006 clone-preempt sha 1c478c24 | COMPLETE | 1862.6 | **1726.6** | **−136.0** |
| **56175620** (EXP-007) | 2026-09-12 01:13:24 | exp007 thomas router v2 exact sha 8031d51a | COMPLETE | 1635.9 | **1541.3** | **−94.6** |
| **두 슬롯 격차** | | | | +226.7 | **+185.3** | −41.4 |

- **리더보드 팀 순위**: **2,007위** (이전 09-15: 1,724위에서 283위 하락)
- **리더보드 표시 점수**: **1,726.6** (EXP-006 점수 반영)
- **전체 참가 팀 수**: **9,234팀** (이전 09-10: 8,481팀 대비 +753팀 증가)
- **상금권 경계 (Top 10)**:
  - 1위: `Majkel1337` (3,208.0)
  - 10위: `Excluding` (3,005.8) — 3,000점 돌파 확인

---

## 2. 각 소유 파일별 구체적 반영 제안

### A. `coordination/BOARD.md` (코디네이터 적용 대상)

`## 현재 상태` 표의 해당 행 업데이트 제안:

```markdown
| 항목 | 값 | 근거 |
|---|---|---|
| 최신 hosted 점수 | EXP-006 **1726.6**, EXP-007 **1541.3** | **09-16 KST 조회**, Kaggle API competition_submissions |
| Sian 순위 / 상금 경계 | **2,007위 / 10위 3005.8** | 09-16 KST 리더보드 스냅샷 (1위 Majkel1337 3208.0) |
```

### B. `evidence/HOSTED_LEDGER.md` (Claude 적용 대상)

`## 제출 원장` 및 하단에 "2026-09-16 21:35 KST — 직접 API+UI snapshot [HOSTED]" 절 신설 제안:

```markdown
## 2026-09-16 21:35 KST — 직접 API+UI snapshot [HOSTED]

출처: `coordination/reports/gemini/20260916-2141-KAGRI-014.md` (Gemini, `scripts/leaderboard_snapshot.py` 및 Kaggle API 조회).

| submission | 접수 (UTC) | description | status | publicScore |
|---|---|---|---|---:|
| **56165718** | 2026-09-11 12:58:06.513 | exp006 clone-preempt sha 1c478c24 | COMPLETE | **1726.6** |
| **56175620** | 2026-09-12 01:13:24.880 | exp007 thomas router v2 exact sha 8031d51a | COMPLETE | **1541.3** |

### 09-15 KST snapshot 대비 변화

| submission | 2026-09-15 | 2026-09-16 (본 snapshot) | Δ |
|---|---:|---:|---:|
| EXP-006 `56165718` | 1862.6 | **1726.6** | **−136.0** |
| EXP-007 `56175620` | 1635.9 | **1541.3** | **−94.6** |
| 두 슬롯 격차 | +226.7 | **+185.3** | −41.4 |

- `[HOSTED]` 두 슬롯 모두 큰 폭으로 점수가 하락함 (EXP-006 -136.0, EXP-007 -94.6). 순서는 EXP-006 > EXP-007 유지.
- `[HOSTED]` 공개 리더보드: Sian 2,007위, 표시값 1726.6, 1위 Majkel1337 3208.0, 10위 Excluding 3005.8, 전체 9,234팀.
- 상금권 경계(10위)가 3,000점을 돌파하여 필드 인플레이션 및 우리 에이전트의 상대적 감점이 가속되고 있음.
```


---

## `proposals/gemini/BRIEF_opponents.md`

# Gemini 작업 지시서 — 공개 상위 봇 확보 (KAGRI-006)

이 파일을 그대로 Gemini CLI 세션에 붙여넣으면 된다.
작업 폴더 `~/kaggle/Kaggriculture` 에서 실행할 것.

---

## 배경 (왜 이 일이 급한가)

우리 v0(`main.py`)가 완성됐고 공식 `starter` 를 **40전 40승, 마진 +15,280** 으로 이겼다.
그런데 이제 **더 이상 측정할 수가 없다.**

- `starter` 최종 뱅크 3,400 / 우리 v0 17,000 / **상위권 90,000~95,000**
- `random` 은 **항상 0으로 끝난다** (무작위 매수로 시작 자금 3,000을 전부 소진). 상대로서 무의미
- `pass` 는 3,000 그대로

즉 **우리는 지금 바닥 상대만 갖고 있어서 v1 개선이 진짜인지 판정할 수 없다.**
`starter` 를 이겨도 정보가 없다. 실제 상위권 봇이 있어야 승격 판정이 성립한다.

## 목표

`opponents/public/` 에 **엔진 1.32.7에서 720턴을 완주하는 상위권 봇 3개**를 확보하고,
`opponents/README.md` 와 `environment/LICENSES.md` 의 출처 표를 채운다.

## 대상 (우선순위 순)

`docs/code/` 에 이미 `.ipynb` 원본이 있다. 여기서 실행 가능한 `agent(obs)` 를 추출한다.

1. `boatlee_v16-rc5-high-score-8c-4s-premium-market-lead.ipynb` — public 2913.3 (LB 6위권)
2. `kaitofukami_25-27-strict-future-v27-midgame-meta-reset.ipynb`
3. `raykkretzschmar_kaggriculture-findings-from-zero-to-top-meta.ipynb`
4. (여유 있으면) `lynnsakurai_farming-score-a-mathematical-approach.ipynb`

주의: 이 노트북들은 **에이전트 코드를 base85+zlib 압축 페이로드로 임베드**해 두었다.

## ⛔ 노트북 셀을 그대로 실행하지 마라 (2026-09-07 추가)

독립 검토에서 `docs/code/` 노트북들의 실행 위험이 확인됐다:

| 노트북 | 무엇이 들어 있나 |
|---|---|
| `reyhanksatria_adaptive-route-agent-v1` | **1,129,128 바이트 opaque ELF64 x86-64 `agent.so`** 를 `ctypes.CDLL` 로 실행 |
| `tetsutani_adaptive-farming-strategy` | **고정 디렉터리 `rmtree`** + archive overwrite |
| `anasriaz_kaggriculture` | **native C++ 컴파일** + `ctypes` bridge |
| 다수 | `pip install`, network request, 임의 file write |

SHA 일치는 **출처·라이선스·안전성을 보장하지 않는다.**

**따라서 추출은 이 순서로 한다.**
1. **정적 추출 우선** — `json` 으로 `.ipynb` 를 열어 셀 소스만 읽는다. 실행하지 않는다.
2. 압축 페이로드는 **직접 디코드**한다. 셀을 실행하지 말고 페이로드 문자열만 꺼내
   `zlib.decompress(base64.b85decode(payload))` 를 별도 스크립트로 돌린다.
3. 디코드 결과가 **사람이 읽을 수 있는 파이썬 소스**인지 확인한다.
   바이너리·컴파일 산출물·난독화 페이로드면 **채택하지 않고 그 사실을 보고**한다.
4. `rmtree` / `pip install` / network / `ctypes` / `subprocess` 를 포함한 셀은 **실행 금지**.
5. 위 표의 3개 노트북(`reyhanksatria` `tetsutani` `anasriaz`)은 **이번 작업 대상이 아니다.**

## 반드시 지킬 것

### 1. 라이선스 확인이 **먼저**다
`.ipynb` 추출본에는 메타데이터가 없어 라이선스를 알 수 없다.
**원본 Kaggle 노트북 페이지를 열어 라이선스를 직접 확인**하고 기록하라.
- 확인 전에는 `opponents/public/` 에 두지 마라
- 상업적 이용을 제한하는 라이선스면 **쓰지 마라** (대회 규정 §A.2 위반)
- 수상 시 우리 제출물과 그 생성에 쓴 소스 전부를 CC-BY 4.0으로 공개해야 한다.
  출처를 지금 남기지 않으면 나중에 복원할 수 없다

### 2. 우리 저장소에 남길 것은 **상대로 쓸 실행 파일과 출처 기록**뿐이다
- 이 코드를 우리 `main.py` 에 **복사하지 마라.** 상대로만 쓴다
- 우리 코드를 팀 밖에 공유하는 것은 **실격 사유**다

### 3. 검증 없이 등록하지 마라
각 봇이 실제로 도는지 확인한 것만 등록한다.

## 절차

```bash
cd ~/kaggle/Kaggriculture

# 0) 파이썬 3.11+ 확인 (엔진이 3.11 미만을 거부한다)
python3 --version
# 3.11 미만이면:  uv venv --python 3.11 ~/.venv311 && ~/.venv311/bin/python -m pip install -r requirements.lock

# 1) 노트북에서 에이전트 정적 추출 -> opponents/public/<author>.py
#    셀 실행 금지. json 으로 소스만 읽고, 페이로드는 별도 스크립트로 디코드한다.
#    디코드 결과가 읽을 수 있는 파이썬 소스가 아니면 채택하지 않는다.

# 2) 720턴 완주 검증
python3 tools/instrument.py --a opponents/public/<author>.py --b starter --seeds 7 11 13
#    -> status DONE, exc=0 이어야 등록 자격이 있다 (noop 은 상대 것이므로 신경 쓰지 마라)

# 3) 우리 v0 대비 실제 강도 측정
python3 tools/arena.py --a main.py --b opponents/public/<author>.py \
        --seeds 30 --seed-start 2000 --json experiments/results/vs_<author>.json
```

## 산출물 (완료 조건)

1. `opponents/public/*.py` — **720턴 완주가 확인된** 봇 3개 이상
2. `opponents/README.md` 표 — 파일 · URL · 저자 · **라이선스** · 수집일 · 엔진 버전 · 출처 유형
3. `environment/LICENSES.md` 갱신
4. `experiments/results/vs_<author>.json` — 각 봇 대비 우리 v0 의 페어드 점수와 95% CI
5. `coordination/reports/gemini/YYYYMMDD-HHMM-KAGRI-006.md` 완료 보고 (형식은 `AGENTS.md` §10)

## 보고 형식 (`AGENTS.md` 핸드오프 규약)

```
VERDICT | 핵심 사실 2개 | exact path + SHA-256 | 실행한 검증과 결과 | NEXT ACTION
```

## 하지 말 것

- 라이선스 미확인 상태로 등록
- 완주 검증 없이 등록
- 노트북의 **서술을 믿는 것** — 서술과 실제 코드가 다른 사례가 여러 건 확인됐다. 한 참가자의
  공개 코드와 실제 필드 에이전트는 719턴 중 **697턴이 달랐다.** 코드를 신뢰하라
- `random` 을 상대 풀에 넣는 것 — 항상 0으로 끝나므로 판정에 무의미하다
- `main.py` `src/` `tools/` `releases/` 수정 — 이 경로는 Codex 단독 소유다

## 우리가 알고 싶은 것 (부가 가치)

봇을 확보하면서 아래를 관찰하면 v1 설계에 직접 쓰인다. 확인한 것만, 근거와 함께 적어라.
- 각 봇의 **땅 매입 시점**과 최종 구획 수
- **일꾼 수의 일별 프로파일** (우리 v0 는 4명 고정이고 액션의 41%가 놀고 있다)
- 매도 로트 크기와 **어느 슬롯에 넣는지**
- 동물 구성 (소/양/거위 마리 수)


---

## `proposals/gemini/BRIEF_recon.md`

# KAGRI-014 — 정찰 루틴 (Antigravity / 맥 로컬 전용)

담당: **Gemini (Antigravity, 맥 로컬 셸)** · 성격: **반복 루틴** (일회성 작업 아님)
**⛔ 이전 판 `BRIEF_replays.md` 는 폐기한다.** 상위 10팀 이름이 09-07 기준으로
하드코딩되어 있는데, 2일 만에 7명이 갈렸다. 당시 1위 `ymg_aq` 는 23위 밖으로 사라졌다.

왜 여기냐: Kaggle CLI 와 `kaggle.json` 이 **맥에만** 있다.
Cowork VM 과 클라우드 컨테이너에는 CLI 도 pip 도 없다. 이 작업은 위임 불가다.

작업 폴더: `~/kaggle/Kaggriculture`

---

## ⛔ 먼저 지킬 것

1. **`kaggle.json` 을 절대 커밋하지 마라.** `.gitignore` 3줄로 막혀 있지만
   과거에 한 번 인덱스에 올라간 적이 있다. `git status` 에 뜨면 즉시 `git rm --cached kaggle.json`.
2. **노트북 셀을 실행하지 마라.** 저장소의 노트북 중에는 1.1MB 불투명 ELF64 `agent.so` 를
   `ctypes.CDLL` 로 실행하는 것과, 고정 경로에 `rmtree` 를 거는 것이 있다. 정적 파싱만 하라.
3. 쓰기 허용 경로는 **`scripts/`, `private_artifacts/`, `coordination/reports/gemini/`** 뿐이다.
   `main.py`, `tools/`, `experiments/`, `evidence/`, `AGENTS.md` 를 건드리지 마라 — Codex 와 Cowork 소유다.
4. git 이 잠기면 `sh scripts/git-unlock.sh`.
5. **해석하지 말고 숫자를 내라.** 이 브리프의 산출물은 요약이 아니라 원시 수치와 파일 경로다.
   판단은 Cowork 가 한다. (지난 수집에서 요약이 원문과 크게 달랐던 전례가 있다.)

---

## Task 1 — 리더보드 일일 스냅샷 `[매일]`

**일회성 조회가 아니라 스크립트를 만들어라.** 사람이 매일 붙어 있지 않아도 되게 한다.

만들 것: `scripts/leaderboard_snapshot.py`

- Kaggle CLI 또는 API 로 `kaggriculture` 리더보드를 가져온다.
  (`kaggle competitions leaderboard -c kaggriculture --show` 계열을 먼저 시도하고,
   시뮬레이션 대회에서 동작하지 않으면 API 엔드포인트로 우회하라. **웹 스크래핑은 최후수단.**)
- **append-only** 로 `private_artifacts/leaderboard/snapshots.csv` 에 한 줄씩 쌓는다.
  컬럼: `utc_ts, rank, team, score` — 상위 30팀 + 우리 팀(`Sian`) 행.
  기존 행을 절대 덮어쓰지 마라. 시계열이 이 파일의 존재 이유다.
- 같은 실행에서 `private_artifacts/leaderboard/latest_top10.txt` 를 덮어쓴다
  (팀명 한 줄씩 10개). Task 2 가 이 파일을 읽는다.
- 재실행 안전: 같은 날 두 번 돌려도 중복 행이 쌓이지 않게 `utc_ts` 로 판단하라.

매일 실행 후, **직전 스냅샷 대비 아래가 바뀐 경우에만** 보고하라(변화 없으면 보고 생략):

| 항목 | 보고 조건 |
|---|---|
| 우리 레이팅 | 항상 (숫자만) |
| 우리 순위 | 항상 (숫자만) |
| 10위 경계 점수 | 항상 (숫자만) |
| 상위 10팀 구성 | 1팀이라도 바뀌면 진입/이탈 팀명 |
| 전체 팀 수 | 항상 |

참고 기준선 (`evidence/HOSTED_LEDGER.md`):
09-07 07:00 → 우리 337.2 / 6,989위 / 10위 경계 2,764.0 / 7,963팀
09-09 07:30 → 우리 330.6 / 7,253위 / 10위 경계 2,867.5 / 8,341팀
**우리는 제출을 안 바꿨는데 레이팅이 내려간다.** 이 추세가 계속되는지가 관측 목적이다.

## Task 2 — 상위 봇 리플레이 `[주 2회]`

**대상 팀을 하드코딩하지 마라.** `private_artifacts/leaderboard/latest_top10.txt` 를 읽어라.

1. `kaggle/kaggriculture-episodes-index` 를 **Kaggle 노트북 안에서** 연다.
   **로컬로 내려받지 마라 — 하루 21GB 다.**
2. 노트북에서 위 10팀의 최근 에피소드 ID 를 팀당 5개, 총 50개 추출해 CSV 로 출력한다.
3. 그 50개만 맥으로 가져와 `kaggle competitions replay` 로 받는다
   → `private_artifacts/replays/top/`. **요청 사이 최소 2초 간격.**
4. 각 리플레이에서 step 별 액션만 뽑아 팀별 JSON 으로 정규화
   → `private_artifacts/tapes/<team>_<episode_id>.json`

**팀별로 아래 표를 채워 보고하라. 해석은 붙이지 마라 — 숫자만.**

| 항목 | 형식 |
|---|---|
| 최종 뱅크 / 상대 뱅크 | 정수 |
| `BUY_LAND` 발행 step | 리스트 (몇 구획, 언제) |
| 최대 동시 일꾼 수 / 도달 step | 정수, step |
| `BUY_ANIMAL` 내역 | 종류별 마리 수와 구매 step |
| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | 정수 (**비용 0 이다 — 몇 개 짓는지가 핵심**) |
| 액션 타입별 총 횟수 | WATER/HARVEST/PLANT/SELL/CARE/FEED/COLLECT_FERTILIZER/FERTILIZE/PICKUP/PLACE/DIG/이동/**PASS** |
| 품목별 판매 총량 | 딕셔너리 |
| SELL 주문 발행 턴 수 / 1회 평균 수량 | 정수, 소수1자리 |

**`PASS` 횟수를 반드시 포함하라.** 우리 현재 42% 이고 이것이 최대 병목이다
(`evidence/PASS_DIAGNOSIS.md`). 상위 봇의 실측 PASS 비율이 이 카드의 1순위 관심사다.

## 보고

`coordination/reports/gemini/YYYYMMDD-HHMM-KAGRI-014.md`
형식은 `20260907-1440-KAGRI-006.md` 와 동일:
VERDICT / 핵심 사실 / path + SHA-256 / 실행한 검증과 결과 / NEXT ACTION / 리스크.

- **모든 로컬 수치에 `[LOCAL]`, Kaggle 에서 가져온 값에 `[HOSTED]` 를 붙여라.**
- 추정·해석에는 `[INFERENCE]` 를 붙이고, 사실과 **분리된 절**에 써라.
- Task 1 만 돌린 날은 표 한 개짜리 짧은 보고로 충분하다.

## Cowork(Claude) 가 할 일

- 보고서의 수치를 원본 파일과 대조 검증
- 상위 봇 행동 변화가 실험 카드에 미치는 영향 판단 및 브리프 개정
- `evidence/HOSTED_LEDGER.md` 갱신


---

## `proposals/gemini/BRIEF_replays.md`

# ⛔ 폐기 — `BRIEF_recon.md` 로 대체됨 (2026-09-10)

> 상위 10팀 이름이 09-07 기준으로 하드코딩되어 있는데 2일 만에 7명이 갈렸다.
> 당시 1위 `ymg_aq` 는 23위 밖으로 사라졌다. **이 파일을 따르지 마라.**

---

# KAGRI-014 — 리플레이 수집 (Antigravity / 맥 로컬 전용)

담당: **Gemini (Antigravity, 맥 로컬 셸)** · 우선순위: P1
왜 여기냐: Kaggle CLI 와 `kaggle.json` 자격증명이 **맥에만** 있다.
Cowork VM 과 클라우드 컨테이너에는 CLI 도 pip 도 없다. 이 작업은 위임 불가다.

작업 폴더: `~/kaggle/Kaggriculture`

---

## ⛔ 먼저 지킬 것

1. **`kaggle.json` 을 절대 커밋하지 마라.** 저장소 루트에 있고 `.gitignore` 3줄로 막혀 있다.
   오늘 한 번 인덱스에 staged 된 적이 있다. `git status` 에 뜨면 즉시 `git rm --cached kaggle.json`.
2. **`main.py` 를 건드리지 마라.** 지금 Codex 가 v1 작업본으로 쓰고 있다.
3. 산출물은 `private_artifacts/` (이미 gitignore) 와 `coordination/reports/gemini/` 에만 쓴다.
4. git 이 잠기면 `sh scripts/git-unlock.sh` 를 먼저 돌려라. 맥에서는 그냥 `rm` 도 된다.
5. **노트북 셀을 그대로 실행하지 마라.** `BRIEF_opponents.md` 의 정적 추출 원칙이 여기도 적용된다.

---

## Task A — 우리 에피소드 (싸다, 먼저)

```
kaggle competitions episodes 56068891
kaggle competitions replay <EPISODE_ID> -p private_artifacts/replays/own
```

**목적은 상대 학습이 아니다.** 현재 레이팅 337.2 라 우리가 만나는 상대도 최하위권이라
전략적으로 배울 게 없다. 확인할 것은 **우리 에이전트가 호스트에서 실제로 무슨 짓을 하는지**다.

에피소드 10판 정도만 받아서 다음을 표로 보고하라.

| 확인 항목 | 왜 |
|---|---|
| `status` 에 ERROR / TIMEOUT 이 있는가 | 로컬 gate 는 CLEAN 이었다. 호스트에서 다르면 그게 최우선 버그다 |
| 우리 최종 뱅크 분포 | 로컬 17,000 대와 일치하는가. 크게 낮으면 호스트 환경 차이가 있다 |
| 상대 최종 뱅크 | 우리가 몇 점짜리 상대에게 지는지 |
| 우리 액션 중 no-op 비율 | 로컬 계측은 0 이었다. 호스트에서도 0인가 |
| 좌석(player 0/1)별 승률 차 | 좌석 편향이 있으면 설계 버그다 |
| 턴당 소요 시간 최댓값 | `runTimeout = 1200s` / 에이전트당 예산. 여유가 얼마나 있나 |

## Task B — 상위 봇 에피소드 (진짜 목표)

이쪽이 v2 설계의 실제 입력이다. **로컬로 내려받지 마라 — 인덱스가 하루 21GB다.**

`kaggle/kaggriculture-episodes-index` 데이터셋을 **Kaggle 노트북 안에서** 붙여 처리한다.

1. 노트북에서 인덱스를 열어 **리더보드 상위 10팀**(`ymg_aq`, `3정훈`, `Mengfei Li`,
   `get some fries`, `SpaTaro`, `Suliman Tadros`, `Jiro2`, `binghua`, `Syed Asad Ali`,
   `Crop Dusta` — 2026-09-07 07:00 UTC 기준)의 에피소드 ID 를 뽑는다.
2. 팀당 최근 에피소드 **5판씩**, 총 50판의 `EpisodeId` 만 CSV 로 추출해 노트북 출력으로 저장한다.
3. 그 50개만 맥으로 가져와 `kaggle competitions replay` 로 받는다 →
   `private_artifacts/replays/top/`.
4. API 를 연속 호출하지 마라. 요청 사이 최소 2초 간격.

## Task C — 추출 (Task B 완료 후)

각 리플레이에서 **step 별 액션 배열만** 뽑아 팀별 1개 JSON 으로 정규화한다.

```
private_artifacts/tapes/<team>_<episode_id>.json
{"team":..., "episode_id":..., "final_bank":..., "opponent_bank":...,
 "steps":[{"step":0,"actions":[...]}, ...]}
```

그리고 팀별로 다음 5개 숫자를 뽑아 표로 보고하라 — `evidence/ENGINE_ANIMALS.md` 의
파라미터와 대조할 것이다.

1. `BUY_LAND` 를 낸 step (몇 구획, 언제)
2. 최대 동시 일꾼 수와 도달 step
3. `BUY_ANIMAL` 내역 — 종류별 마리 수와 구매 step
4. `BUILD_COOP` / `BUILD_PASTURE` 횟수 (**비용 0 이다** — 몇 개나 짓는지가 핵심)
5. 하루 평균 `SELL` 주문 줄 수와 품목 구성, 특히 FERTILIZER 매도량

---

## 보고

`coordination/reports/gemini/YYYYMMDD-HHMM-KAGRI-014.md`
형식은 `20260907-1440-KAGRI-006.md` 와 동일: VERDICT / 핵심 사실 / path+SHA-256 /
실행한 검증과 결과 / NEXT ACTION / 리스크.

**Task A 만 끝나도 즉시 보고하라.** ERROR 나 TIMEOUT 이 하나라도 나오면
Task B 를 중단하고 그것부터 알린다 — v2 설계보다 급하다.
