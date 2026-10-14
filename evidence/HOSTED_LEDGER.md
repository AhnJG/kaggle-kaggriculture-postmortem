# HOSTED LEDGER — Kaggle에서 돌아온 외부 결과

로컬 결과는 여기 들어올 수 없다. artifact SHA ↔ submission ID 매핑이 이 파일의 존재 이유다.

## 계정 상태

| 확인일 | 항목 | 값 | 확인 방법 |
|---|---|---|---|
| 2026-09-06 | 규칙 동의 | **완료** | 대회 페이지에 "Submit Agent" 노출, Team 탭 접근 가능 |
| 2026-09-06 | 팀 | **Sian (솔로, 1/5명)** | Team 탭. 받은 초대 없음 |
| 2026-09-06 | 제출 수 | 0회 | Submissions 탭 |
| **2026-09-07** | **제출 수** | **1회 (v0)** | Submissions 탭에 submission.tar.gz 확인 |
| 2026-09-07 | 활성 슬롯 | **1 / 2** | v0 접수 |
| 2026-09-06 | 마감까지 | 24일 | 대회 헤더 |

→ ~~슬롯 예산 5회 중 1회 사용~~ **정정 2026-09-10**: 제출은 **하루 5개**이고 최종 평가는 **마지막 2개**다
  (`docs/official/rules.md:38`, `docs/official/evaluation.md:1`, `coordination/RESET_2026-09-10.md` §1a).
  총량 예산이라는 전제가 틀렸다. 2026-09-10 잔여 4/5.

**2026-09-07 06:20 UTC 확인 완료**: validation **통과**. 제출 시각 2026-09-07 04:36 UTC.
**submission ID = 56068891**, status `SubmissionStatus.COMPLETE`.
Kaggle UI 는 ID 를 노출하지 않는다. 맥 로컬 CLI `kaggle competitions submissions -c kaggriculture` 로만 얻는다.
Cowork VM(device_bash)·클라우드 컨테이너 어디에도 Kaggle CLI 와 자격증명이 없다 —
**Kaggle API 호출은 전부 맥 로컬(Antigravity/Gemini 또는 사람) 담당이다.**

## 제출 원장

| # | 제출일 | 라벨 | artifact SHA-256 | submission ID | 엔진 | validation | 활성 | 은퇴시킨 것 |
|---|---|---|---|---|---|---|---|---|
| v0 | 2026-09-07 | v0 pipeline validation (commit 4ed2d29) | `aed79ff3…5844` | **56068891** | 1.32.7 | **✅ Success (check_circle)** | 1/2 | 없음 |
| v1-20260910 | 2026-09-10 | v1-20260910 measurement submission | `723f8fd8…eb4a` | **56145245** | 1.32.7 | ✅ COMPLETE · publicScore **343.9** (23:16 UTC 확인) | 활성 (2번째) | 없음 |
| yhay81-exact | 2026-09-10 | public-yhay81-shop-router-0909-exact (사람 제출, description 공란) | `40d2bc3986f4ed3e927c81842d399a58bf20b07b57858355da4b75c280fd7791` | **56147691** | 1.32.7 | ✅ COMPLETE · publicScore **2188.4** (23:16 UTC 확인) | 활성 (최신) | v0 `56068891` (FIFO 추정) |
| exp006-clone-preempt | 2026-09-11 | exp006 clone-preempt sha 1c478c24 (사람 제출) | `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721` | **56165718** | 1.32.7 | ✅ COMPLETE · publicScore **1915.6** (2026-09-12 사람 제공 snapshot) | 활성 | v1-20260910 `56145245` (FIFO 추정) |
| exp007-thomas-exact | 2026-09-12 | exp007 thomas router v2 exact sha 8031d51a (사람 제출) | `8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180` | **56175620** | 1.32.7 | ✅ COMPLETE · publicScore **1819.8** (2026-09-12 사람 제공 snapshot) | 활성 (최신) | yhay81 복사본 `56147691` (FIFO 추정) |

## 에피소드 관측

| 관측일 | submission ID | 에피소드 수 | 상대 | 좌석 | 결과 | 레이팅(시각) |
|---|---|---|---|---|---|---|
| 2026-09-07 06:20 UTC | 56068891 | (미확인) | — | — | — | 314.8 |
| 2026-09-07 07:10 UTC | 56068891 | (미확인) | — | — | — | **337.2** (+22.4) |

## ⚠️ 2026-09-07 06:20 UTC — 첫 hosted 신호

| 항목 | 값 |
|---|---|
| 우리 레이팅 | **314.8** |
| 우리 순위 | **6,989 / 7,963** (하위 12%) |
| 1위 | ymg_aq **2,850.6** |
| 10위 (상금 경계) | Crop Dusta **2,764.0** |
| 신규 제출 기본 레이팅 | 600 |

**해석 `[HOSTED]`**: 제출 2시간 만에 기본 600 에서 **314.8 까지 하락**했다.
에피소드가 정상적으로 돌고 있으며 **거의 전패**하고 있다는 뜻이다.
파이프라인은 검증되었고(S15~S16 목표 달성), 전략은 리그 최하위권이다.

**상금권까지 필요한 것**: 314.8 → 2,764.0. 로컬 자가대전 개선으로는 닿지 않는 거리다.
Gemini KAGRI-006 프로파일(상위 봇 105k~136k vs v0 17k)과 일치한다.

## 2026-09-09 07:30 UTC — 사다리 디플레이션 자체 확인 `[HOSTED]`

**우리는 아무것도 안 했는데 레이팅과 순위가 둘 다 내려갔다.**

| 시각 | 우리 레이팅 | 우리 순위 | 전체 팀 | 10위 경계 | 1위 |
|---|---|---|---|---|---|
| 09-07 07:00 | 337.2 | 6,989 / 7,963 | 7,963 | 2,764.0 | ymg_aq 2,850.6 |
| **09-09 07:30** | **330.6** | **7,253 / 8,341** | **8,341** | **2,867.5** | **SpaTaro 2,957.6** |
| 변화 (2일) | **−6.6** | **−264위** | +378팀 | **+103.5** | +107.0 |

- 제출물은 동일하다(submission 56068891, 09-07 04:36 이후 변경 없음).
- 커뮤니티 노트북 `dariushafshar_same-file-9-days-apart` 의 주장
  "필드가 강해지면서 고정 에이전트의 레이팅이 내려간다" 를 **우리 제출로 직접 확인했다.**
- **10위 경계가 하루 약 +50 씩 멀어진다.** 정지해 있으면 순위는 자동으로 내려간다.

### 상위 10위 물갈이 — 2일 만에 7/10 교체

| 09-07 top10 | 09-09 top10 |
|---|---|
| ymg_aq 2850.6 | SpaTaro 2957.6 |
| 3정훈 2844.2 | Otter Vibe 2944.3 |
| Mengfei Li 2832.5 | Mengfei Li 2935.3 |
| get some fries 2819.8 | Matthew Huang 2926.8 |
| SpaTaro 2805.6 | Fih 2890.8 |
| Suliman Tadros 2805.6 | keiz 2888.3 |
| Jiro2 2787.6 | binghua 2886.6 |
| binghua 2780.5 | redblackbst 2878.6 |
| Syed Asad Ali 2772.4 | Yusuke Hayashi 2868.6 |
| Crop Dusta 2764.0 | let cats farm 2867.5 |

생존 3팀(SpaTaro, Mengfei Li, binghua). **09-07 1위 ymg_aq 는 23위 밖으로 사라졌다.**

→ `[INFERENCE]` 오늘의 상위 봇에 과적합하면 그 자체가 썩는다.
   `AGENTS.md §7.1` 의 "4종 중 3종 이상" 요건이 이 관측으로 강화된다.

## 2026-09-10 13:36 UTC — v1-20260910 접수 `[HOSTED]`

| 항목 | 값 |
|---|---|
| submission ID | **56145245** |
| artifact SHA-256 | `723f8fd81f3dd010e90581da96adff9ccb25081833aa5cba054027a13d98eb4a` |
| tar 내 main.py SHA-256 | `d6cdb83ffdb27d2614330b20d438a6a20e82c7f4a72ead5ca8be897859de0b59` |
| source commit | 4709b1e |
| 엔진 | kaggle-environments==1.32.7 (`bc8a5487…653e`, ENGINE_LOCK 일치) |
| status | `SubmissionStatus.PENDING` (접수 시각 기준) |
| 활성 슬롯 | 1/2 → **2/2** |
| 오늘 잔여 제출 | **4 / 5** |
| v0 publicScore(대조) | 337.3 |

**목적**: 성능 가설 없음. 활성 슬롯 2/2 를 채우고 hosted 표본을 n=1 에서 n=2 로 올려
로컬 지표 ↔ hosted 레이팅 상관축(§7.1 삼중쌍)의 두 번째 점을 만든다.
v0 와 **같은 계열(규칙 기반 실행기)** 이므로 §7.4 의 "두 슬롯 = 서로 다른 두 전략" 요건은
**아직 충족하지 않는다.** 다음 제출에서 테이프 라우터 계열로 한 슬롯을 교체해야 한다.

**릴리스 체크리스트 §7.5** — Identity/Schema/Runtime/Isolation/License 5줄 제출 전 PASS,
Ledger 이 행으로 완결. 상세는 `releases/v1-20260910/manifest.json`.

## 2026-09-10 23:16 UTC — CLI 확인 (사람이 맥에서 실행해 붙여넣음) `[HOSTED]`

`kaggle competitions submissions kaggriculture`:

| ref | 제출 시각 (UTC) | description | status | publicScore |
|---|---|---|---|---:|
| **56147691** | 2026-09-10 15:57:05 | (공란) | COMPLETE | **2188.4** |
| 56145245 | 2026-09-10 13:36:45 | v1-20260910 measurement submission (sha 723f8fd8) | COMPLETE | 343.9 |
| 56068891 | 2026-09-07 04:36:28 | v0 pipeline validation (commit 4ed2d29) | COMPLETE | 347.2 |

리더보드 경계 (`--download` CSV, 같은 시점): 1위 SpaTaro **3,122.2** · 10위 **2,960.9** · 59위 2,834.0 ·
100위 2,782.7 · 300위 2,653.4 · **500위 2,537.4** · 1,000위 2,257.2. 전체 팀 수는 출력에 없음.
Yusuke Hayashi(yhay81 원저자) **16위 2,929.4** (`--show`).
09-10 08:34 CSV 대비 경계 변화: 500위 2,535.8 → 2,537.4 (+1.6), 10위 2,963.7 → 2,960.9 (−2.8) — 이 15시간 창에서는 "하루 +50~96" 이 관측되지 않았다.

**ID ↔ SHA 연결 근거와 한계**
- 56147691 ↔ `40d2bc39…d7791`: 사람 진술(yhay81-exact 를 직접 제출함) + 시간 근접(`releases/public-yhay81-shop-router-0909-exact/` 파일 mtime 15:50–15:53, 제출 15:57:05).
  CLI 는 업로드 파일 해시를 보여주지 않는다 → **업로드한 파일 경로는 사람 확인 필요.** 에피소드 연결 미완(`kaggle competitions episodes 56147691` 필요).
- 활성 슬롯: evaluation.md:1 "latest 2 tracked" 에 따라 {56147691, 56145245} 로 **추정**. v0 은퇴 여부는 v0 점수가 이후에도 움직이는지로 확인한다(337.3@13:36 → 347.2@23:16, 은퇴 시점 15:57 전후 어느 쪽 변화인지 미상).
- 56147691 은 접수 후 약 7.3 시간 시점 값이다. 수렴 전 값이므로 원저자 2,929.4 와 직접 비교하지 않는다(§3).

## 2026-09-11 12:58 UTC — exp006-clone-preempt 접수 `[HOSTED]`
- submission **56165718** ↔ `coordination/proposals/claude/exp006/submission.tar.gz` sha256 `1c478c24…9721` (description 에 sha 앞 8자리, 사람 붙여넣기 CLI 출력으로 확인). 카드 `experiments/cards/EXP-006-clone-preempt.md` SUCCESS.
- 활성 슬롯 추정: {56147691 yhay81 복사본, 56165718 exp006}. v1 56145245 은퇴.
- 판독 예정: 2026-09-12 12:58 UTC 이후 CLI 1회 — Δ = 56165718 − 56147691. 에피소드 연결(`kaggle competitions episodes 56165718`)은 미완.

## 2026-09-12 01:13 UTC — exp007-thomas-exact 접수 `[HOSTED]`
- submission **56175620** ↔ `releases/public-thomas-replay-router-v2-exact/submission.tar.gz` sha256 `8031d51a…0180` (member main.py `8241246…5a97`). 카드 `experiments/cards/EXP-007-thomas-router.md` 사전등록 SUCCESS(검증자 반대 의견 병기).
- 활성 슬롯 추정: {56165718 exp006, 56175620 thomas}. yhay81 복사본 56147691 은퇴 → exp006 vs 복사본 24h A/B 판독은 수행 불가.
- 다음 판독: 두 봇의 publicScore 와 `kaggle competitions episodes` 로 서로 다른 판에서 지는지(계보별 상대 분포) 확인.

## 2026-09-12 11:14 UTC — EXP-006/007 COMPLETE 및 공개 episode 비교 `[HOSTED]`

사람이 붙여넣은 같은 CLI 출력에서 EXP-006은 **1915.6**, EXP-007은 **1819.8**로 둘 다 COMPLETE였다.
snapshot의 정확한 조회 시각은 제공되지 않아 **2026-09-12 당일 snapshot**까지만 확정한다. 두 tar의 SHA-256은
각 카드에 고정된 exact artifact와 다시 일치했다.

두 제출이 모두 활성화된 2026-09-12 01:13:25 UTC 이후, 11:14:20 UTC까지 EXP-006의 최신 50판과
생성시각이 가장 가까운 EXP-007의 중복 없는 50판을 비교했다.

| submission | 표본 | 좌석 0/1 | W/D/L | point score | 패배 상대 수 |
|---|---:|---:|---:|---:|---:|
| EXP-006 `56165718` | 50 | 21/29 | **41/0/9** | **0.82** | 9 |
| EXP-007 `56175620` | 50 | 21/29 | **21/9/20** | **0.51** | 20 |

- `[HOSTED]` 이 snapshot과 표본에서는 EXP-006이 publicScore **+95.8**, episode point score **+0.31**로 더 강하다.
- 패배 상대 이름 교집합은 **0명**이지만, 전체 상대 이름 교집합도 3명뿐이다(EXP-006 49명, EXP-007 48명).
  따라서 이것은 두 슬롯의 보완 가능성을 암시할 뿐, 같은 상대에 대한 실패 상관이 낮다는 증명은 아니다.
- EXP-006의 parent `56147691`은 이미 은퇴했으므로 HYP-0006의 사전등록 같은-window Δ gate는 계산할 수 없다.
  과거 2188.4와 현재 1915.6을 바로 빼서 clone-preempt의 효과라고 해석하지 않는다.

재현 명령:

```bash
python3 tools/compare_hosted_episodes.py --submission-a 56165718 --submission-b 56175620 --team Sian --after 2026-09-12T01:13:25 --as-of 2026-09-12T11:14:20 --count 50 --output experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json
```

원자료 요약: `experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json`.
해석 보고: `coordination/reports/codex/20260912-1114-HOSTED-EPISODE-COMPARE.md`.

## 2026-09-14 10:47 UTC — 활성 2슬롯 snapshot `[HOSTED]`

사람이 `kaggle competitions submissions` 출력을 붙여넣었다. 조회 시각은 제공되지 않아
**2026-09-14 10:47 UTC 이전** 까지만 확정한다. 목록에는 활성 2건만 나왔다.

| submission | 파일 | 접수 (UTC) | description | status | publicScore |
|---|---|---|---|---|---:|
| **56165718** | submission.tar.gz | 2026-09-11 12:58:06.513 | exp006 clone-preempt sha 1c478c24 | COMPLETE | **1896.9** |
| **56175620** | submission.tar.gz | 2026-09-12 01:13:24.880 | exp007 thomas router v2 exact sha 8031d51a | COMPLETE | **1647.4** |

### 09-12 snapshot 대비 변화

| submission | 2026-09-12 | 2026-09-14 | Δ |
|---|---:|---:|---:|
| EXP-006 `56165718` | 1915.6 | **1896.9** | **−18.7** |
| EXP-007 `56175620` | 1819.8 | **1647.4** | **−172.4** |
| 두 슬롯 격차 | +95.8 | **+249.5** | +153.7 |

- `[HOSTED]` 두 slot 모두 점수가 내려갔고, **EXP-007 의 하락폭이 EXP-006 의 9.2배** 다.
  순서는 09-12 와 같다(EXP-006 > EXP-007).
- `[INFERENCE]` 이 Δ 는 **우리 코드 변화가 아니다.** 두 artifact 는 접수 이후 바이트가 고정돼 있다.
  leaderboard 상대 분포가 바뀌었거나 rating 이 계속 수렴 중이거나 둘 다다. 어느 쪽인지는 이 snapshot 만으로 구분 불가.
- `[N/A]` episode 단위 재비교(`tools/compare_hosted_episodes.py`)는 이번에 실행하지 않았다.
  Δ 의 원인을 상대 분포로 귀속하려면 09-12 와 같은 방식의 window 비교가 한 번 더 필요하다.
- 상금 경계(10위 2960.9 · 1위 3122.2)는 2026-09-10 23:16 UTC 값이며 **현재값이 아니다.**
  현재 순위·경계는 이번 출력에 포함되지 않아 N/A 다.

### 의미 (판단)

- EXP-007 은 09-11 스크리닝에서 "parent 가 지는 셀을 이긴다" 는 비상관 근거로 채택됐다.
  `[HOSTED]` 두 번의 snapshot 모두에서 EXP-007 이 EXP-006 보다 낮고 격차가 벌어지는 중이다.
  **두 슬롯 비상관 가설은 아직 반증되지 않았지만 지지되지도 않는다** — 09-12 비교에서 전체 상대 교집합이
  3명뿐이었으므로 "다른 상대를 만났다" 와 "서로를 보완한다" 를 여전히 구분하지 못한다.
- 다음 슬롯 교체는 FIFO 다. EXP-007 을 교체하면 이 계보의 판독이 끊긴다. 교체 전에 판독 계획을 고정할 것.

원자료: 사람이 붙여넣은 CLI 출력 (이 절에 전재).

## 2026-09-15 01:13 KST (완료 시각 상한 2026-09-14 16:13:12 UTC) — 직접 CLI+UI snapshot `[HOSTED]`

출처: [20260915-0115-KAGGLE-SNAPSHOT.md](../coordination/reports/codex/20260915-0115-KAGGLE-SNAPSHOT.md) (Codex, `kaggle competitions submissions kaggriculture -v` 직접 실행 + 공개 leaderboard UI 대조).
[owner 이관안](../coordination/proposals/codex/20260915-owner-record-sync.md) §4 반영. 새 episode 단위 W/D/L·실패 상관 재판독은 **N/A** — 이 절은 publicScore·활성 슬롯·순위 snapshot만 기록한다.

| submission | 접수 (UTC) | description | status | publicScore |
|---|---|---|---|---:|
| **56165718** | 2026-09-11 12:58:06.513 | exp006 clone-preempt sha 1c478c24 | COMPLETE | **1862.6** |
| **56175620** | 2026-09-12 01:13:24.880 | exp007 thomas router v2 exact sha 8031d51a | COMPLETE | **1635.9** |

### 09-14 10:47 UTC snapshot 대비 변화

| submission | 2026-09-14 | 2026-09-15 (본 snapshot) | Δ |
|---|---:|---:|---:|
| EXP-006 `56165718` | 1896.9 | **1862.6** | **−34.3** |
| EXP-007 `56175620` | 1647.4 | **1635.9** | **−11.5** |
| 두 슬롯 격차 | +249.5 | **+226.7** | −22.8 |

- `[HOSTED]` 순서는 09-12·09-14와 같다(EXP-006 > EXP-007). 이번 창에서는 EXP-006 하락폭이 EXP-007보다 크다 — 09-14 관측("EXP-007 하락폭이 9.2배")과 방향이 반대다. 두 창 모두 episode 단위 재판독이 없어 원인(상대 분포 변화 vs 레이팅 수렴)은 **N/A**.
- `[HOSTED]` 공개 leaderboard UI: Sian(`<kaggle_user>`) **1,724위**, 활성 제출 dialog 표시값 1635.9 / **1862.6**(leaderboard 표시). 1위 Majkel1337 3232.2, 10위 Thomas Tschinkel 2974.2 — 이 상금 경계는 **2026-09-15 KST 값**이며 09-10 23:16 UTC 값(10위 2960.9)과 날짜가 다르므로 직접 비교하지 않는다.
- 활성 2슬롯 = {56165718, 56175620} — CLI 최신 두 ID·공식 latest-2 규칙·공개 UI 대조로 확인. 로컬 tar SHA 재확인 결과 두 artifact 모두 기존 기록과 일치.
- `[N/A]` episode 단위 재비교(`tools/compare_hosted_episodes.py`)는 이번 snapshot에서 실행하지 않았다.

원자료·재현: 위 snapshot 보고서 §2(CLI 원출력)·§3(leaderboard UI)·§4(로컬 SHA 재확인).

## 2026-09-18 21:1x KST (2026-09-18 ≈12:10 UTC) — 브라우저 UI + 로그인 세션 leaderboard API snapshot `[HOSTED]`

출처: Claude가 사용자 요청으로 Claude 데스크톱 내장 브라우저(사용자 로그인 세션)에서 직접 조회. `kaggle` CLI는 이 환경(로컬 VM·cloud 모두)의 egress 에서 kaggle.com 이 403 으로 막혀 실행 불가 → **CLI 원출력 없음.**
조회 경로: `kaggle.com/competitions/kaggriculture/submissions`(UI 텍스트), `…/leaderboard`(UI) 및 같은 페이지가 쓰는 `POST /api/i/competitions.LeaderboardService/GetLeaderboard {competitionId:147734}`(read-only, 9,423행). 다운로드 없음.

| submission | description (UI) | 상태 (UI) | publicScore |
|---|---|---|---:|
| **56175620** | exp007 thomas router v2 exact sha 8031d51a | 활성 | **1487.4** |
| **56165718** | exp006 clone-preempt sha 1c478c24 | 활성 | **1638.5** |
| 56147691 | (공란) — yhay81-exact `40d2bc39…d7791` | "Disabled due to the competition's active submission limit" | 2081.8 (은퇴 후 표시값, 갱신 시점 N/A) |
| 56145245 | v1-20260910 measurement submission | Disabled | 316.4 |
| 56068891 | v0 pipeline validation | Disabled | 347.2 |

| 항목 | 값 |
|---|---|
| 팀 수 | **9,423** (GetCompetition.totalTeams, leaderboard 행수 일치) |
| Sian 순위 | **2,201위** (표시 점수 1638.5 = EXP-006; leaderboard 는 팀의 최고 bot 만 표시 — evaluation.md) |
| 메달 경계 (API `medal` 필드) | GOLD 28팀 · 28위 2924.8 / SILVER ~471위 **2648.1** / **BRONZE ~942위 2395.3** |
| 참고 분위 | 300위 2727.0 · 500위 2628.2 · 700위 2525.4 · 900위 2421.4 · 1000위 2359.2 · 1500위 2054.5 · 2000위 1745.7 |
| 상금권 | 1위 Majkel1337 3183.6 · 10위 Otter Vibe 3019.0 |
| 제출 한도 | 하루 5개, 활성 2개 (latest-2), 마감 2026-09-30T23:59Z |

### 09-15 snapshot 대비

| submission | 2026-09-15 | 2026-09-18 | Δ |
|---|---:|---:|---:|
| EXP-006 `56165718` | 1862.6 | **1638.5** | **−224.1** |
| EXP-007 `56175620` | 1635.9 | **1487.4** | **−148.5** |
| 순위 | 1,724위 | **2,201위** | −477 |

- `[HOSTED]` 두 활성 bot 모두 3일간 크게 하락했다. 원인(상대 분포 강화 vs 수렴)은 episode 판독 없이 N/A (HYP-0011 방향과는 일치).
- 56147691(yhay81-exact)의 2081.8은 은퇴 bot 의 표시값이다. 활성 bot 과 같은 window 값이 아니므로 직접 비교하지 않는다(§3). 다만 이 artifact 의 manifest 는 로컬 silent-failure gate **FAIL** 상태에서 사람 override 로 제출됐고 hosted 2188.4(09-10)를 기록했다 — P1b 의 zero-gate FAIL 이 hosted 강도를 예측한다는 근거는 현재 없다 `[INFERENCE]`.
- FIFO: 현재 활성 순서는 [56165718 (09-11), 56175620 (09-12)]. 새 제출 1건은 **56165718(EXP-006, 현 최고)** 을 은퇴시킨다.
- `[N/A]` episode 단위 W/D/L 재판독 없음.

## 2026-09-18 ≈13:00 UTC — yhay81-exact 재제출 `[HOSTED]`

- 사람이 직접 제출 (Mac 터미널 CLI). description `yhay81 exact resubmit sha 40d2bc39 2026-09-18`. artifact `releases/public-yhay81-shop-router-0909-exact/submission.tar.gz` SHA `40d2bc3986f4ed3e927c81842d399a58bf20b07b57858355da4b75c280fd7791` (제출 전 로컬 재확인 일치). 이전 제출 56147691과 같은 bytes, 새 submission.
- submission ID: **56330776** (사람 제공, 2026-09-18). 이전 56147691 과 같은 bytes.
- 접수 약 44분 뒤 UI: **1538.9**, COMPLETE. 수렴 전 값이다.
- FIFO 결과 (UI): 활성 = {yhay81 재제출, EXP-007 `56175620` 1489.0}. **EXP-006 `56165718` 은퇴** (표시 1638.3, "Disabled due to the competition's active submission limit").
- silent-failure gate: 이 artifact의 manifest 는 FAIL(no-op 44–136 등) 상태 그대로 사람 override 로 제출됐다. 새 판정 없음.

## 2026-09-19 ≈11:30 KST — 활성 2개 재조회 `[HOSTED]` (내장 브라우저 UI)

| submission | 경과 | publicScore |
|---|---|---:|
| yhay81-exact 재제출 **56330776** | 약 14시간 | **1515.3** |
| EXP-007 `56175620` | 7일 | **1475.1** |

- 같은 bytes(`40d2bc39…d7791`)의 56147691 은 09-10 2188.4 / 은퇴 시 2081.8 이었다. 9일 뒤 재제출본은 14시간 시점 1515.3. 수렴 전 값이지만, 같은 artifact 의 상대 강도가 그 사이 크게 떨어졌을 가능성이 높다(필드 강화, HYP-0011 방향) `[INFERENCE]`.
- 이 값은 09-18 "yhay81-exact 가 EXP-006 보다 강하다" 판단(09-12 무렵 비교)이 현재 필드에서는 성립하지 않을 수 있음을 뜻한다. 은퇴한 EXP-006 표시값 1638.3 은 은퇴 시점 값이라 직접 비교하지 않는다(§3).

## 2026-09-19 — F0 P2 lynnsakurai v2 exact 제출 `[HOSTED]`

- 사람 제출. submission ID **56347732**. artifact `releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz` SHA `1178ffa0614673a58fb1ee5b2a44003eecd5640634d6f3471e84ac92c1fbf388` (Codex 3회 빌드 동일, Claude 재확인 일치). 원문 `docs/code/lynnsakurai_farming-score-v2-a-better-approach.ipynb` SHA `f419b98e…ac12`.
- 주의: 이 빌드의 `main.py`(SHA `cddf51ea…a94d`)는 notebook 자체의 기대값 `d3bebf51…b1497` 과 다르다 — notebook 본문 그대로지만 작성자의 실제 제출 파일과 같다는 증명은 없다.
- FIFO 예상: EXP-007 `56175620` 은퇴 → 활성 {yhay81-exact 56330776, P2 56347732}. 점수는 24h 후 판독.

## 2026-09-20 00:1x KST (2026-09-19 ≈15:20 UTC) — P2 첫 판독 `[HOSTED]` (내장 브라우저 UI + leaderboard API)

| submission | 경과 (UI) | publicScore |
|---|---|---:|
| F0 P2 lynnsakurai v2 exact **56347732** | 11h | **2421.6** |
| yhay81-exact 재제출 56330776 | 1d | 1483.8 |
| (은퇴) EXP-007 56175620 | — | 1467.3 |

- Sian **949위 / 9,550팀, 표시 medal = BRONZE.** 동메달 경계 955위 **2418.9** — 여유 **+2.7점**. 은 477위 2652.6, 금 29위 2913.5.
- P2 는 제출 11시간째로 수렴 전이다. 라이브 변동 ±25–50(KILLS 방법론)보다 여유가 작아 **현재 동메달권은 확정이 아니다.** 최종 순위는 마감 후 약 2주 경기의 BT(evaluation.md).
- 활성 = {yhay81-exact 56330776 (09-18), P2 56347732 (09-19)}. 다음 제출은 yhay81 을 은퇴시킨다.

## 2026-09-20 — F0 P1 alperen before-dawn exact 제출 `[HOSTED]`

- 사람 제출. submission ID **56363545**. artifact `releases/public-alperen-before-dawn-stock-cash-sales-exact/submission.tar.gz` SHA `cce494e5419f06028fa3fd19ddf0f2400e661427132c895664469f4fe6c5a9ec` (notebook 자체 기대 main SHA `87142c0e…43b39` 일치, Codex 3회 빌드 동일). 원 notebook 은 09-19 조회 시 403(비공개/삭제 추정), 코드 안 Apache-2.0 고지 보존.
- 계보: P2 와 같은 가족(sim 0.900, tape 38/38 공유). 로컬 진단 P2 상대 2/0/18 `[LOCAL]`.
- FIFO: yhay81-exact 56330776 은퇴 → 활성 {P2 56347732, P1 56363545}. 점수는 24h 후 판독.

## 2026-09-20 (KST 오전) — 활성 2개 판독 `[HOSTED]` (내장 브라우저 UI + leaderboard API)

| submission | 경과 | publicScore |
|---|---|---:|
| F0 P2 lynnsakurai **56347732** | 1d | **2410.4** |
| F0 P1 alperen **56363545** | 10h | **1471.3** |

- Sian **1,017위 / 9,594팀 — 동메달권 밖.** 동메달 경계 959위 **2444.5**(09-19 15:20 UTC 2418.9 에서 약 하루 새 +25.6). 격차 **−34.1**.
- alperen 은 같은 계보인데 P2 보다 약 940점 낮다. 로컬 arena 진단(P2 상대 2/0/18)과 방향이 같다 — 로컬 arena 가 이 계보 안에서는 유용한 거르개라는 첫 hosted 대조점 `[INFERENCE]`, 표본 1쌍.

## 2026-09-20 14:50 UTC — EXP-014 + P2 대조 재제출 `[HOSTED]`

| submission | 접수 (UTC) | artifact | SHA-256 |
|---|---|---|---|
| **56398274** | 2026-09-20 14:50:13 | EXP-014 mirror sale lead (`releases/f0-mirror-lead-exp014/submission.tar.gz`, 진입점 `_mirror_lead_agent`) | `be529b5cce50c53e738b79094e41852d8195b4f03cb8a391fd1c9ddee1600d29` |
| **56398276** | 2026-09-20 14:50:17 | P2 대조 재제출 (56347732 와 같은 bytes) | `1178ffa0614673a58fb1ee5b2a44003eecd5640634d6f3471e84ac92c1fbf388` |

- 사람 제출, 접수 시 PENDING. FIFO: P2 56347732 · alperen 56363545 은퇴 → 활성 {56398274, 56398276}. 같은 기간 A/B.
- 근거: EXP-014R INCONCLUSIVE(22.0/30), fast lane 단계 F 조건(패널 회귀 0/200) 충족. 판독: 두 bot 모두 24h 이후, 100점 이상 차이만 판단(BOARD 제출 운영).

### 정정 2026-09-20 — 활성 ID (사람 제공)

- 실제 활성 = **EXP-014 56398297** (14:51:04 UTC) / **P2 대조 56398299** (14:51:08 UTC). artifact·SHA 는 위 표와 같다.
- 위 표의 56398274·56398276 이 실제로 접수된 제출이라면 같은 bytes 의 중복 제출이며, latest-2 규칙으로 즉시 비활성이다. 판독·비교에는 56398297·56398299 만 쓴다.

## 2026-09-21 12:40 KST 스냅샷 (사용자 보고)
- 중복 제출로 P2 사본 2개가 활성 → 사용자가 EXP-014 (be529b5c…0d29) 재제출 2026-09-21 03:35:41 UTC, ID 56415087, 600.0 (시작값).
- 활성 = EXP-014 재제출 / P2 대조 56398299 2161.9 (~13h, 아직 수렴 전). 이전 행의 56398297 은 비활성으로 간주.
- 2026-09-21 공개 LB 스냅샷 (GetLeaderboard, 9,699팀): 1위 3124.1 · 10위 2994.1 · 20위 2946.3 · 100위 2806.0 · 200위 2748.1 · ≥2700 315팀 · ≥2900 30팀 · 동메달 경계(969위) 2440.6.
- 2026-09-21 11:07:00 UTC 제출: **56426857** C1 pipe16 exact (main 827ddf29…8181, tar submission_clean.tar.gz 3f410af2…c240), PENDING. FIFO 로 P2 대조 56398299 은퇴 → 활성 = EXP-014 56415087 / C1 56426857. 다음 제출은 EXP-014 를 은퇴시킨다.
- 2026-09-21 (사용자 보고): C1 56426857 COMPLETE, hosted 경기 정상 진행(오류 없음).
- 로컬 사슬 (Stage 2b, 20경기씩): C1 > C2 (0/20, margin −50) > C3 (C2 20/0) ; C1 vs C4(V53) 12/8, C1 vs C5(V51) 16/4. C1 = 현재 로컬 최강. C1 main 827ddf29 은 tetsutani/demand-preserving-turn-sale-timing 출력·haideptry 2950 Peak Farm 과 동일 바이트 → hosted 에 복제본 다수 예상.
- 2026-09-22 C1 56426857 hosted 148경기 (as_of 수집): 91승 50패 7무. 상대 지문(20260922-1716-C1-HOSTED-MAP): C2|C3 38 (C1 35-3), 미확인 prefix 0 35 (28-7), **step 53 까지 C1 동일한 미확인 봇 34 (4-30, 서로 다른 34팀 이상)**, C1 거울 9 (0-2-7), P2 8 (8-0), C4|C5 6 (5-1). 53-봇은 step 54 에 hand 1 이 HARVEST 대신 PASS, step 55 BUILD_PASTURE 대신 PASS (C1 보다 밀을 한 번 더 키우는 오프닝으로 보임). margin 대부분 −27~−60.
- 2026-09-22 08:29:40 UTC 제출: **56458814** EXP-016 (C1 + V53 판매 앞당김, main 9d58536d…6013, tar 4071f6c5…ef76) — **hosted 실험** (로컬 사전 기준 INCONCLUSIVE, 사람 결정). FIFO 로 EXP-014 56415087 은퇴 → 활성 = C1 56426857 / EXP-016 56458814. **다음 제출은 C1 을 은퇴시킨다.**
- 2026-09-22 step 53 봇 식별: dmitriigluzdov "One More Wheat" 18/34, "More Wheat Smarter Sales"·"7 Turn Rescue" 16/34. OMW = C1 + 50줄 (임시 밀을 하루 더 키움). 로컬: OMW vs C1 40/0 (+28), OMW vs EXP-016 10/30.
- 2026-09-23 점수: **EXP-016 56458814 = 2425.7**, C1 56426857 = 2206.6 (차 +219.1, 노이즈 ~90 초과). 판매 앞당김 층이 hosted 에서도 이득.
- 2026-09-23 LB 스냅샷 (9,886팀): 1위 3192.6 · 5위 3032.9 · **동메달 경계(988위) 2346.1**. 2425.7 = 약 808위 → **현재 동메달 구간 안**. (참가팀 증가로 경계가 2444 → 2346 으로 내려감)
- 2026-09-23 EXP-017 (OMW + 판매 앞당김, main 56941da2…, tar 177eedc0…) 로컬 SUCCESS: OMW 상대 59/0/21 (순승 +38), EXP-016 상대 78/0/2 (+76), 패널 패배 147 vs EXP-016 155.
- 2026-09-23 09:59:56 UTC 제출: **56490029** EXP-017 (main 56941da2…, tar 177eedc0…), COMPLETE, 1985.2 (제출 직후 상승 중). FIFO 로 C1 56426857 은퇴 → 활성 = EXP-016 56458814 (2425.7) / EXP-017 56490029.
- 2026-09-23 상위권 관찰 (Antigravity, 팀당 40경기): DSM 3157.3 평균 최종 cash 112,432 · Majkel1337 3066.0 107,449 · M&M&P&Q 3065.3 99,039 vs EXP-017 로컬 92,717. 구간별 차이: d0-11 MELON 상위 52u@222 vs 우리 72u@181; d12-18 CARROT 상위 13~49u vs 우리 0u; d19-29 WHEAT 상위 302~383u vs 우리 266u. (상대 구성이 달라 cash 직접 비교는 참고값)
- 2026-09-24 점수 (사용자 보고): EXP-016 56458814 = **2265.8** (전일 2425.7, −160), EXP-017 56490029 = **2100.2** (제출 약 24h). EXP-017 이 EXP-016 보다 −165.6 → 정책 B-3 되돌림 조건 도달.
- 2026-09-24 LB 스냅샷 (9,942팀): 1위 3096.5 · 50위 2782.1 · 200위 2638.6 · 500위 2492.3 · **동메달 경계(994위) 2302.8**. EXP-016 ≈ 1084위(경계 −37), EXP-017 ≈ 1459위. 상위 분포 전체가 09-21 대비 약 100점 내려감(100위 2806→?, 200위 2748→2638).
- 관찰: 로컬 EXP-017 vs EXP-016 78/0/2 였으나 hosted 는 EXP-017 이 165 낮음 → **형제 변형 간 로컬 직접 대결은 hosted 순위를 예측하지 못했다.**
- 2026-09-24 hosted 지도 (Antigravity 20260924-1610): EXP-016 200경기 77-123 (12h 구간 승률 50→32→41→**19%**), EXP-017 145경기 77-68 (69→51→40%). 최대 상대군 = **step 91 까지 OMW 계열과 동일한 미확인 봇** 137경기 (EXP-016 41-59, EXP-017 10-27, 서로 다른 팀 다수 → 공개 notebook 복제).
- Claude 확인 (EXP-017 상대 4경기): step 90–142 의 유일한 차이는 step 92 에서 OMW 의 `SELL WHEAT 3` (임시 밀 즉시 판매) 을 **하지 않는 것**. step 144 이후 차이는 미확인.
- 09-22/09-24 스캔에 OMW 계열 공개 파일이 약 35종(고유 sha) 있음 → 어느 것인지 지문 필요.
- 2026-09-24 사람 결정: **B안** — step 91 봇 X 식별 후 X exact 만 제출 (FIFO 로 EXP-016 은퇴, 슬롯 = EXP-017 / X). 두 번째 실험은 이후 EXP-017 자리.
- 2026-09-24 Claude 판독 (analysis/step91_id per-episode FULL 일치 + LB teamId 대조, analysis/step91_id/full_match_teams_claude.json):
  | 공개 파일 (FULL 일치) | 우리 W-L | 그 팀들 LB 점수 중앙값 (최소~최대) |
  |---|---|---|
  | V56 (Antigravity 선정 X, 복제 최다) | **17-9 (우리가 이김)** | 2229 (2107~2630), n=23 |
  | V57 | 2-6 | 2205 (2040~2311) |
  | **tetsutani demand-preserving 09-24 (178ae0f7)** | **0-7** | **2457 (2263~2594)**, n=7 |
  | 2965 hybrid 93831c | 1-4 | 2337 |
  → "가장 많이 복제된 파일"(V56)은 우리를 이기지 못한다. 우리를 이기고 LB 도 높은 쪽은 **demand-preserving 09-24**. 이 파일에는 판매 앞당김 층(_ADV_LOOK)과 최종 판매 블록 재정렬이 이미 들어 있다. LB 점수는 팀의 최고 봇 기준이라 참고값. 동메달 경계 2289.7 (995위, 09-24 저녁).
- release: releases/public-tetsutani-demand-preserving-0924-exact (main 178ae0f7…d3a, tar 1f88c3e7…269 = main.py+NOTICE.txt, tar 안 main sha 일치). 마지막 callable `_final_sell_block_reorder_entrypoint`, replay 관측 재생 예외 0, 최대 0.037초. `V92_SELL_LIB` 환경변수 경로는 hosted 에서 미설정 → no-op.
- 2026-09-24 10:26:01 UTC 제출: **56518910** tetsutani demand-preserving 0924 exact (main 178ae0f7…d3a, tar 1f88c3e7…269). FIFO 로 EXP-016 56458814 은퇴 → 활성 = EXP-017 56490029 (09-23 09:59) / demand-preserving 56518910 (09-24 10:26). **다음 제출은 EXP-017 을 은퇴시킨다** (재제출 절차 불필요).
- 2026-09-24 DP 0924 계열 hosted 지도 (Antigravity 20260924-2155-DP-HOSTED-MAP, as_of 11:45 UTC, Claude 재확인): 같은 파일(178ae0f7) 8개 submission 884경기 666-199-19. 720 step 재현 23/24 (56502662 ep 112837776 step 300 `SELL MILK 6` 불일치, 원인 미확인). DP 승점률 by 상대 LB: <2200 0.92 · 2200–2400 0.73 · 2400–2600 0.56 · 2600–2800 0.22 · ≥2800 0 (09-24 ≥2600 상대 0-24) → 균형 약 2450~2550 추정. DP 팀 LB (11:43 UTC): haseryooooo 2603.4 · yaya__k 2512.2 · wennan cao 2508.7 · Taisei 2435.9 · 青葉 2370.8 · Pihulski 2287.5 · Muroya 2269.7 (팀 최고 봇 기준). herd-safe-v3 FULL 상대에게 DP 1-15 (사용 팀 LB 중앙값 ≈ 2340). closed-loop 패널 가능 59경기 (29L/30W). 우리 56518910 = 2069.1, 18경기 17-1 (수렴 중).
- 2026-09-25 13:52 KST 점수 (사용자 보고): **DP 0924 56518910 = 2191.6** (제출 약 27h), EXP-017 56490029 = 2010.8. 동메달 경계 2289.7(09-24 저녁) 대비 **−98 → 현재 동메달 밖**. 09-24 Claude 추정 "DP 균형 2450~2550" 은 **틀림** — 상대 강도로 팀 LB(팀 최고 봇 점수)를 썼기 때문에 상대를 과대평가했다(그 경기에서 만난 submission 의 실제 레이팅이 아님). 정정 필요 자료: 경기 목록 API 의 agent 별 score (Antigravity 09-25 지시).
- 2026-09-25 13:40 KST Codex EXP-018 (DP + `_V92_P_EVERY = 2`, 판매 예측 갱신 3→2턴, candidate main f3e727b1…): 유효 hosted 복제 패널 47경기 23-0-24 → 28-0-19 (Δ 0.106 > 2SE 0.091, 새 패배 0), DP 직접 80경기 22/34/24 = 0.4875 < 필수 하한 0.50 → **VERIFIED_NOT_ELIGIBLE_DP_FLOOR** (카드 f2eaac36…). 패널은 Q1/Q2 선택에 쓴 개발 자료(8경기 중 3 flip 포함)라 선택 편향 있음. herd-safe FULL 재가중 field 비중 약 2.6%.
- 2026-09-25 14:25 KST Antigravity DP-RATING-CHECK: 경기 목록 API 의 agents 항목에 submission 별 점수 필드(initialScore/updatedScore) **없음** → 상대 submission 의 실제 레이팅은 얻을 수 없음 (BLOCKED, 보고 20260925-1425-DP-RATING-CHECK.md). 127ed3e6 재지문: 09-24 수집 319경기 중 match_full 1 (ep 112849618, DP 패), match_143 2 (둘 다 DP 패) — 표본이 너무 작아 판단에 쓰지 않음.
- 2026-09-25 20:40 KST Claude — **D3 runtime gate 재정의 (사람 결정, 사후 변경임을 명시)**: 0.25초(Coordinator 임의 여유값) → 엔진 한도 기반 gate v2 (단일 worker 최대 step < 0.8초 · step 0 cold start < 0.8초 · 6-worker 부하 < 1.0초 · 경기당 누적 < 30초 · 예외/INVALID 0 · engine SHA 일치). NEWMETA-EXACT 의 기록상 판정 NOT_ELIGIBLE(0.25 기준)은 그대로 둔다. **새 gate 판정 (별도 줄): 127ed3e6 exact = PASS** — Mac(M3) Cowork Linux VM, 루프 6-worker 동시 실행 중(보수적), 15경기(D3 지정 seed + stage1 느린 상위) 최대 step 0.168초(step 0 포함), 누적 최대 1.55초, 예외 0, 6-worker stage1 0.7506초. 보조: 클라우드 Linux x86 단일 worker 0.313초 PASS. 기존 측정 도구(dp_counterfactual.run_game)는 소스 로딩을 타이머 밖에서 해서 step 0 을 잰 적 없음 → 새 스크립트 experiments/d3_gate_v2/measure_gate_v2.py 로 측정. 원자료 experiments/d3_gate_v2/result-mac-vm.json, result-cloud-linux-x86.json. 한계: 네이티브 macOS python 이 아니라 VM 측정. D4 에 따라 사람 제출 판단 대기 (FIFO: EXP-017 56490029 은퇴).
- 2026-09-25 11:48:30 UTC 제출 (사람): **56549720** 127ed3e6 exact (submission.tar.gz sha 63e1554c…, tar 안 main 127ed3e6…c652), COMPLETE, 초기 점수 2165.6 (제출 직후, 레이팅 미수렴). FIFO 로 **EXP-017 56490029 은퇴** → 활성 = DP 0924 56518910 (09-24 10:26) / 127ed3e6 56549720 (09-25 11:48). **다음 제출은 DP 0924 를 은퇴시킨다.** D4 감시: 제출 후 6시간(09-26 02:48 KST 까지) hosted ERROR/TIMEOUT 확인 필요.
- 2026-09-25 22:50 KST Claude D4 1차 감시 (ListEpisodes 메타데이터, 파일 다운로드 없음): 56549720 경기 28 (validation 1 + public 27) 전부 COMPLETED, 보상 결측 0 (ERROR/TIMEOUT 없음), public 22-0-5, validation self-play 134초 (DP 0924 332초). 레이팅 미수렴 — 24h 후 재판독.
- 2026-09-28 23:30 KST Claude (Coordinator) 원장 보충 — 09-25 이후 제출 4회를 HANDOFF-20260928 기준으로 적는다(시각·점수는 그 문서 값, 새 조회 아님): v171 56567563 → v074 56577440 → **d157 56607884** (FIFO 로 v171 은퇴; 09-28 18시 2345.7, 136경기 0.640) → **c26 56635330** (09-28 08:45 UTC, FIFO 로 v074 은퇴). 현재 활성 = d157 / c26, 다음 제출은 d157 을 은퇴시킨다.
