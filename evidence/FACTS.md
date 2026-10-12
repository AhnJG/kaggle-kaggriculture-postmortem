# FACTS — 재현 명령이 붙은 사실만

**재현 명령 또는 file:line이 없는 줄은 여기 들어올 수 없다.** 그런 건 `HYPOTHESES.md`로.
엔진 기준: `kaggle-environments==1.32.7` (`environment/ENGINE_LOCK.md`)
공통 재현: `python3 scripts/verify_engine_facts.py`

## [OFFICIAL] 대회 운영
- 720턴 = 30일 × 24턴, 시작 자금 3,000, 승리 = 종료 시 은행 현금 — `docs/official/how_to_play.md`
- 코인 격차는 레이팅에 반영되지 않는다 (승/무/패만) — `docs/official/evaluation.md`
- 하루 5회 제출, **최신 2개만 활성**이고 그 2개가 최종 평가 대상 — `docs/official/evaluation.md:1`
- 신규 제출 시 **self-play validation** 에피소드가 돈다 — `docs/official/evaluation.md:5`
- 참가/팀병합 마감 2026-09-23 23:59 UTC, 최종 제출 2026-09-30 23:59 UTC — 공식 Timeline
- 상금 1~10위 각 $5,000 · 팀 최대 5명 — `docs/official/rules.md`
- 무승부 시 **먼저 제출한 쪽이 승자** — `docs/official/rules.md`
  **[2026-09-16 구분 추가]** 이 규정은 **최종 순위 동점자(tie) 처리 규정**이다. 개별 에피소드의 게임 내 draw(D)는
  그대로 draw로 기록되며 이 규정으로 W로 전환되지 않는다. W/D/L 집계·`paired_score`·게이트 판정에서
  draw 셀을 승리로 재해석하지 않는다. 근거: `docs/official/rules.md`(순위 tiebreak 조항) vs 관측(§7.2·EXP 카드들의
  D 카운트, 예: EXP-008 verdict `evidence/raw/EXP-008/verdict.json` control_wdl/target_wdl의 D=0 값을 그대로 사용).
- **리플레이는 행동까지 공개된다** — `docs/official/rules.md` §2.11
- 평가 중 네트워크 ingress/egress 전면 금지 — `docs/official/rules.md` §2.12
- 자원: 제출 **100 MiB** / RAM **6.5 GiB** / **vCPU 1.6** / HDD 8 GiB, 파일은 `/kaggle_simulations/agent/`
  — 공식 FAQ 렌더값 (로컬 `docs/official/frequently_asked_questions.md`는 템플릿 미치환 상태)
- **★ 시간 예산은 "턴당 1초"가 전부가 아니다.** `kaggriculture.json` 에 `runTimeout` 정의가 없어
  framework default **1,200초**를 상속한다(`schemas.json` 확인). 그런데 `episodeSteps=720` 은
  초기 상태 뒤 **719회의 agent action call** 을 만들므로, 에이전트당 nominal 상한은
  `719 × 1s + 60s overage = 779초`, 두 에이전트 합 **1,558초 > 1,200초**다.
  로컬 `env.run()` 은 file/callable/builtin 에이전트를 **순차 호출**한다(UrlAgent 만 병렬).
  → **양쪽이 모두 느리면 턴 타임아웃이 아니라 에피소드 전체가 먼저 죽는다.**
  hosted 스케줄링 경로는 `[N/A]`. 재현: `docs/discussion/739874_*.md`, `evidence/` 검증 로그
- ⚠️ **최종 BT 범위 불일치**: 공식 Evaluation·Timeline·공지(731587)는 "마감 후 2주 에피소드"로 읽히고,
  스태프 답변(discussion/732931)은 "전 기간 × 양쪽 최종 활성 경기 전부"라고 한다. **양쪽에서 안전한 설계로 우회 중.**
  **[2026-09-16 연결]** 이 불일치는 아래 **F-T12**에서 스태프 원문 재확인으로 이미 해소됐다 —
  F-T12 결론(양쪽 에이전트가 끝까지 활성인 경기만 최종 BT에 포함)을 따른다. 이번에 새로 발견한 사실이 아니라
  기존 F-T12 판정을 이 서두 bullet과 명시적으로 연결한 것이다.

## [ENGINE] 게임 동작 — 1.32.7 소스 직접 확인
- **파머·일꾼 전원이 매일 아침 셰드로 리스폰** — `kaggriculture.py:879-881`
- **가격은 턴 내에서 즉시 갱신** — `:660`(유닛마다 재고 증가) `:628`(슬롯마다 refresh).
  공식 문서 how_to_play:250의 "previous turn 기준"은 **틀렸다**
- **주문 슬롯 인덱스가 체결 순서를 결정** — `_process_market` 슬롯 루프. 양 플레이어가 슬롯 i를 동시에,
  유닛 단위로, 같은 사전 재고 가격에 견적받는다 → **같은 턴 안의 "분할"은 무의미하고 순서만 유효**
- **`HIRE`·`BUY_LAND`도 시장 주문 10칸을 소비** — `:560` `queues.append(q[:max_orders])`
- **`PLANT` 씨앗 부족 시 그 턴의 모든 PLANT가 실패** — `docs/official/how_to_play.md:52-53`
- **불법 액션 = 무음 no-op / 셰드 초과 = 물건 소멸 / 11번째 주문 = 조용히 절삭** — 셋 다 예외 아님
- **$1에 판 물량은 시장 재고에 안 들어간다** — `_commit_unit` `if price > 1:`
- **`BUY_PRODUCT`는 밀·비료만**, 매수 견적이 매수 후 재고 기준이라 왕복 차익 0, **셰드 캡에도 막힘**
- 급수·급여는 **격일이면 생존**(`consecutive_unwatered >= 2`에서 사망). 단 **일회성 작물 수확량은 물 준 날 수에 비례**
- 일회성 작물 물주기 보너스 창 = `(max_yield_day+1)//2` ~ `max_yield_day`. 멜론은 **age 6~12** — `:440`
- 동물은 살아만 있으면 급여 무관 **매일 비료 1**. `CARE`는 급여+케어한 날 +1 적립 → 다음 생산일 지급
- 일꾼 고용비 = 그날 n번째에 `fib(n)`. 누적 4명 7 / 8명 54 / 10명 143 / 13명 609 / 15명 1,596
- 땅 $1,000 / $2,000 / $4,000 (NE→SW→SE), 셰드 100칸(씨앗 제외)
- 상대 타일·자금·유닛 위치·해금 구역·오늘 고용수는 관측 가능, **셰드·인벤토리는 불가**.
  `market.inventory`와 `town.unlocked_shops`는 **공유**
- 상점은 **3일마다 복원추출로 8개까지 해금** — `:867` `townShopUnlockInterval` default **3**,
  `:886` `next_day % 3 == 0`, `:118` `MAX_SHOP_INSTANCES = 8`.
  실제 스케줄 **day 3·6·9·12·15·18·21·24**. 시드는 관측에서 제거되어 **미래 해금 예측 불가**지만
  **현재 해금 목록 `town.unlocked_shops` 는 관측 가능**하다.
  ⚠️ 소비 주기(`townShopSellInterval` default **4턴**, `:733`)와 **다른 값이다.** 혼동 사고 1건 발생 —
  `evidence/ABSORPTION.md` §7

## [ENGINE+계산] 경제
재현: `python3 scripts/verify_engine_facts.py`
- **마을 흡수율/일**(상점 8개 **정상상태**): 딸기 25 · 우유 19 · 당근 19 · 밀 31 · 양털 13 · 토마토 13 · 달걀 13 · **멜론 1** · **비료 0**
  ⚠️ **이 값은 게임 후반값이다.** day 1~2 는 상점 0개라 전 품목 1/일이고, day 3 부터 3일마다 1개씩 늘어
  day 24 에 위 값이 된다. 매도 상한을 이 표에서 상수로 유도하지 마라 — `evidence/ABSORPTION.md` §5
- **시즌 흡수량 × base** (전체 파이 **206,190**): MILK 52,320 · STRAWBERRY 51,120 · WOOL 45,600 ·
  TOMATO 13,680 · WHEAT 13,125 · CARROT 11,445 · EGG 11,400 · **MELON 7,500** · **FERTILIZER 0**.
  재현: `evidence/ABSORPTION.md` §2 스니펫
- **타일 수익률**(coin/tile/day, base): 멜론 137.5 > 소 80 > 양 66.7 > 거위 50 > 딸기 28.8 > 당근 26.2 > 밀 20 > 토마토 19.8
- **1회 덤핑 천장**(I0→$1): 멜론 158 / 비료 493 / 당근 842 / 토마토 529 / 우유 76 / 양털 59 / 딸기 62. 밀·달걀은 바닥 없음
- 마감 캘린더: 딸기 파종 day13 / 소·양 배치 day17 / 멜론 day17(만수확) / 토마토 day18 / 거위 day20
- 비료를 밭에 쓸 때 이득: 멜론 **+0** / 당근 +1 / 밀 +2. 이득이 큰 곳은 토마토·딸기뿐

## [LOCAL] 실측
- `starter` vs `starter` = **3,507** (시작 3,000, 순익 507). seed=7, 720턴
- 아무도 안 팔면 가격이 오른다: 딸기 120→311 · 우유 160→377 · 토마토 60→77 · **비료 100→100(불변)**. seed=7
- **공개 상위 봇 4종 실측 (seed=7 vs starter, 720턴 완주)**:
  - `boatlee.py`: 125,139 코인 / 3구획(step 161, 241) / 최대 일꾼 14 / 소 8, 양 4, 거위 0 / 비료 5단위 주기적 매도
  - `kaitofukami.py`: 105,679 코인 / 3구획(step 161, 241) / 최대 일꾼 14 / 소 9, 양 4, 거위 0
  - `raykkretzschmar.py`: 136,062 코인 / 3구획(step 161, 241) / 최대 일꾼 14 / 소 10, 양 4, 거위 0
  - `lynnsakurai.py`: 118,292 코인 / 3구획(step 151, 266) / 최대 일꾼 12 / 소 9, 양 8, 거위 0
  - 재현: `python3 tools/instrument.py --a opponents/public/<bot>.py --b starter --seeds 7`
  - 핵심 공통점: **4번째 구획 전원 미구매(3구획 고정), 거위 0마리, 일꾼 12~14명 동적 증원, 비료 선점 매도**


## [HOSTED] 필드
- 2026-09-03 LB: 1위 2959.1 / 10위 2886.9 → **상금권 폭 72점**. 팀 7,834
- 상위권 터미널 캐시 **90~95k** (rayk 88 에피소드 평균 뱅크 93,615) / 순수 PPO 공개 최고 80k

## [LOCAL] S4~S7 실행 결과 (2026-09-06)
재현: `python3 tools/smoke.py` · `python3 tools/instrument.py` · `python3 tools/arena.py`
상세: `experiments/results/S4_S7_RESULTS.md`

- **엔진 해시 검증 통과** — 클라우드와 맥북 워크스페이스 양쪽에서
  `kaggriculture.py` sha256 = `bc8a5487…653e`, ENGINE_LOCK 과 일치
  ⚠️ **정정 2026-09-09**: 이 줄의 원문은 양쪽 파이썬을 `3.11.15` 로 적었다. 현재 맥북 워크스페이스
  `.venv` 는 **3.13.14** 다 (`.venv/pyvenv.cfg`, KAGRI-016 보고와 일치). 해시는 그대로 통과한다.
- **공식 3봇 전 조합(9개)이 양 좌석 720턴 완주, 예외 0**
- **`random`은 항상 0으로 끝난다** — 무작위 매수로 시작 자금 3,000을 전부 소진.
  `pass`는 3,000 그대로. → **아무것도 안 하는 게 무작위보다 낫다.** random 은 승격 판정 상대로 무의미
- `starter` 최종 뱅크 3,421~3,641 (30일 순익 400~640). 상위권 90~95k 대비 **약 1/150**
- ~~`starter`는 720턴 중 147~167턴이 무음 실패~~ **[2026-09-06 철회]**
- ~~상대가 공유 시장을 통해 우리 액션 예산을 갉아먹는다~~ **[2026-09-06 철회]**
  두 항목 모두 **계측기 귀속 버그의 산물**이었다. 상세는 아래 "계측기 귀속 버그" 참조.
  **정정된 사실**: `starter` 의 무음 실패는 상대와 무관하게 **0** 이다. 147~167 은 전부 `random` 의
  것이 P0 버킷으로 샌 것이다. `random` 의 실제 noop 은 약 300~333.
- 처리량: 720턴 1경기 ≈ **맥북 워크스페이스 0.65~0.8s** / 클라우드 1.7~1.9s.
  → 200시드 페어드(400판)가 맥북에서 **약 5분**, 승격 판정에 충분히 실용적
- **계측기 함정 1**: `K.interpreter` 재할당은 무효다(레지스트리가 로드 시점 객체를 잡고 있음).
  `_initialize` / `_end_of_day` / `_process_market` / `_apply_unit_action` /
  `_drop_inventories_to_shed` / `_commit_unit` 을 감싸야 한다
- **계측기 귀속 버그 (2026-09-06 발견·수정)**: `id(farm)` 으로 플레이어를 귀속하면 **틀린다.**
  ① kaggle-environments 는 매 스텝 관측 객체를 새로 만들고 **id 를 재활용**한다
  ② 인터프리터 호출 순서가 `_apply_unit_action`(×전 유닛) → `_process_market` → `_end_of_day` 라서,
     market 단계에서 등록한 id 는 **다음 스텝 유닛 단계에서 이미 낡았다**
  → 미스가 기본값 pid 0 으로 흘러 **상대의 무음 실패가 우리 버킷에 쌓인다.**
  **수정**: 호출 순서 기반 귀속 — `unit_index == 0` 이 올 때마다 플레이어 커서 +1,
  `_process_market` 에서 리셋. drop 은 `_end_of_day` 에서 리셋.
  **검증 방법(필수)**: 좌석을 교체해 두 번 돌리고 카운터가 좌석을 따라가는지 확인할 것

## [OFFICIAL] 환경 요구사항
- `kaggle-environments==1.32.7` 은 **requires_python >= 3.11**.
  맥북 Cowork 워크스페이스 기본 파이썬은 **3.10.12 라 설치가 거부된다.**
  `uv venv --python 3.11` 로 별도 인터프리터를 확보해야 한다 (확인 완료, 동작함)

## [HOSTED] 리더보드 상위 10팀 리플레이 분석 (2026-09-08)
재현: `grep -A 20 '"action": {' private_artifacts/tapes/*.json | head -n 30` (tapes 추출 스크립트: `scratch/analyze_top_replays.py`)
- **액션 구조**: 액션 JSON은 `{"farmer": [...], "hands": [[...]], "market": [[...]]}` 형태다.
  `"BUY_LAND"`는 `market` 배열의 원소, `"BUILD_PASTURE"`는 `hands` 또는 `farmer`의 원소로 전달된다.
- **BUY_LAND 시점**: 평균 141.7턴, 중앙값 151턴 (140~150 턴 사이에 최초 구매 발생).
- **일꾼 증원**: 평균 최대 12.1명, 절대 최대 14명까지 적극적으로 늘린다.
- **가축 편향**: 비용 0인 `BUILD_PASTURE`(평균 15개/팀) 건설이 `BUILD_COOP`(평균 2.3개/팀)보다 월등히 많다. 동물도 COW(50.4%)와 SHEEP(41.4%)에 치중하며 GOOSE(8.2%)는 거의 사지 않는다.

---

## 2026-09-10 테이프 재생 계측 `[LOCAL]` `[ENGINE]`

측정: 47 테이프 × {boatlee, starter} × seeds[7,1000,1001,1002,1003] × 양 좌석 = **940 에피소드**
+ main.py 동일 조건 baseline 20 에피소드. 결측 0, 에러 0, 전 에피소드 status DONE/DONE.
엔진 kaggle-environments==1.32.7 (`kaggriculture.py` sha256 `bc8a5487…653e`, ENGINE_LOCK 일치).
원자료 960줄 — 클라우드 컨테이너 `/home/claude/tapelab/results.jsonl` (세션 종료 시 소멸).
재현: `tar -xzf scratch/_bundle/tape_bundle.tar.gz && python3 run_experiment.py`

### F-T1 `[LOCAL]` 순수 테이프 재생이 main.py 를 페어드로 압도한다
전략 로직 0 인 `agent(obs) -> tape[obs["step"]+1]["action"]` 재생기 기준.

| 상대 | n | 평균 뱅크 차 (재생 − main.py) | 95% CI | 재생 승/패 |
|---|---:|---:|---|---|
| 전체 | 940 | **+79,744** | [77,597, 81,892] | 929 / 11 |
| boatlee (LB 59위) | 470 | +59,404 | [57,083, 61,725] | 460 / 10 |
| starter | 470 | +100,085 | [97,576, 102,594] | 469 / 1 |

W/D/L (§7.2 1차 지표):
- 재생 vs starter: **470-0-0**
- 재생 vs boatlee: **263-0-207 (56.0%)**, 평균차 −4,239 이지만 **중앙값 +2,947** (대형 패배가 평균을 끎)
- main.py vs boatlee: 23,258 vs 140,813 — 궤멸

### F-T2 `[LOCAL]` 테이프 품질은 소유자의 hosted 순위와 무관하다 (역상관 사례)
테이프별 평균 뱅크 상위: Syed_Asad_Ali_106273289 **123,358** / 3정훈_105976137 120,165 /
binghua_105943236 118,305 / Syed_Asad_Ali_106271578 117,011 / Suliman_Tadros_106271578 116,793.
Jiro2_106270500 은 20판 **20-0-0**.
최하위 2개는 **hosted 리더보드 1위 ymg_aq** 의 테이프다 (26,490 / 30,717).
중앙값 107,967, 최소 26,490, 최대 123,358.
→ `[INFERENCE]` ymg_aq 는 테이프가 아니라 반응형 에이전트일 가능성. 그 액션을 개루프로 재생하면 desync 한다.

### F-T3 `[ENGINE]` 엔진은 `hands` 길이 정렬을 요구하지 않는다
`kaggriculture.py:913-918` 은 `action.get("hands", [])` 를 길이 검증 없이 받고,
`:937-939` 가 리스트 길이만큼 순회한다. `_farmer_position(:278-282)` 는 범위 밖 인덱스에 `None` 을
돌려주고 `_apply_unit_action(:314,317-319)` 은 `pos is None` 이면 즉시 return —
**초과 hand 는 조용한 no-op, 부족 hand 는 암묵적 PASS.** 예외 0. §3 무음 실패 표에 해당한다.
실측: 940판 중 124판에서 hands 불일치 턴 발생(평균 3.76턴), 크래시 0.

### F-T4 `[ENGINE]` 로컬 `env.run()` 은 같은 시드에서 완전 결정론적이다 — `[COMMUNITY]` 주장 반박
zhincez 노트북 주장: *"엔진이 상점 재고를 잡초와 같은 난수 스트림에서 뽑아 같은 시드도 두 번 돌리면
다른 마을이 나오고 결과가 2만 코인 흔들린다"* → **반박.**
게임 상태에 영향을 주는 RNG 사용처는 3줄뿐: `:839` 잡초 스폰, `:871`
`rng = random.Random((seed * 1_000_003) ^ day)`, `:891` `rng.choice(sorted(SHOPS))`.
시딩이 `(seed, day)` 에만 의존하고 상대·시장가·좌석과 무관하다.
시장 재고는 `_commit_unit(:652-687)` 과 `_town_consume(:728-749)` 에서만 바뀌며 둘 다 RNG 미사용,
`market_price(:192-206)` 도 결정론적.
실측: seed 7, starter vs starter 2회 독립 실행 → 뱅크·상점 해금 순서·잡초 수 **완전 동일**.
**부분 인정**: 잡초와 "어떤 상점이 열릴지" 가 같은 rng 객체를 공유하는 것은 사실(:871→:891).
다만 그것은 "상점 재고"가 아니라 해금 종류다. **판정 범위는 로컬 `env.run()` 한정** — hosted 채점
인프라의 비결정성은 이 소스로 확인 불가 `[N/A]`.

### F-T5 `[ENGINE]` `core.py` 는 매 스텝 상태를 깊은 복제한다
`kaggle_environments/core.py` 의 `__loop_through_interpreter` 가 매 스텝 `structify(state)`
(`utils.py:117-122`) 를 호출해 farm dict 의 `id()` 가 매 턴 바뀐다.
→ 계측기를 만들 때 객체 id 를 한 번만 캡처하면 turn 0 이후 전부 매칭 실패한다. 매 진입마다 재계산할 것.

### F-T6 `[COMMUNITY]` 남의 테이프 재생은 소유자 점수의 약 88% 를 회수한다 — 미승격
출처: `docs/code/zhincez_replaying-someone-elses-tape-gets-you-88-percent.ipynb` (수집 2026-09-08 경).
자기보고 n=2 (tiki 92.0%, gogogo 84.8%, 평균 88.4%). 아티팩트·시드 수·엔진 버전 미기재 →
§3 에 따라 `[COMMUNITY]` 를 벗어나지 못한다. **인용은 가능하나 승격 근거 불가.**
같은 노트북의 다른 수치: Thomas Tschinkel 의 replay router 가 공개 LB **2,531.4**,
zhincez 본인 2,527.7(2026-09-08 기준 271위/8,151). 상대 26명 중 25명이 테이프라고 주장.
**우리 F-T2 는 이 88% 가설과 상충하지 않는다** — 소유자가 반응형이면 회수율이 크게 낮아진다.

### F-T7 `[ENGINE]` `[LOCAL]` yhay81 의 "unfilled sell 83,998..116,738" 은 sentinel 과다요청이다 — 실손 아님 (2026-09-10)
- `[ENGINE]` SELL 에 가격 조건이 없다. 체결 = min(n, 처리 시점 창고 재고) (`kaggriculture.py:596-628`, `:652-660`). 창고 재고를 남긴 채 SELL 이 끝나는 경로는 없다. 단 같은 턴 BUY_PRODUCT(WHEAT/FERTILIZER)는 창고를 먼저 채울 수 있다 (`:662-672`).
- `[LOCAL]` yhay81 13 테이프의 SELL 줄 중 **n=1000 이 1,245줄**, n=100 이 329줄. `tools/instrument.py:62` 의 `sell_unfilled = Σn − 체결` 이 이를 그대로 센다.
- 분해: artifact `40d2bc39…d7791`, 엔진 `bc8a5487…653e`, seeds 7/1000/1001 × 양좌석 × {starter, boatlee, lynn, rayk, kaito, self} = 42 player-run.
  unfilled 합 4,049,574 = **phantom(어디에도 재고 없음) 98.7%** + carried(일꾼 인벤토리, 이후 판매) 1.3% + **창고 미판매 0**.
  엔진 절삭 0 · 에이전트 자기 절삭 0 · 수동 DROP 소멸 0 · 종료 잔여 0 · 일말 셰드 소멸 1..7 units/run (≤120 코인).
- 독립 검토(서브에이전트, sellaudit 미사용 재구성)가 품목별 수치를 재현했고, 수동 DROP 사각지대를 지적 → 훅 추가 후 42 run 전부 0.
- → `releases/public-yhay81-shop-router-0909-exact/manifest.json` 의 `silent_failure_gate: FAIL` 은 **게이트 정의 오류**다 (thomas 릴리스의 "SELL 미체결 31–6,193" 도 같은 정의).
- 재현: `PYTHONPATH=<engine site> python3 coordination/proposals/claude/harness/sellaudit.py --a releases/public-yhay81-shop-router-0909-exact/main.py --b <opp> --seeds 7 1000 1001 --both-seats --out x.jsonl`

### F-T8 `[LOCAL]` 1코인 매도는 붕괴 "후" 처리다 — 원인은 얇은 시장(MILK T=122, STRAWBERRY T=100) 동시 생산
- yhay81 vs boatlee seed 7: yhay81 MILK 108 + STRAWBERRY 203 units, boatlee MILK 102 + STRAWBERRY 240 units 를 1코인에 매도. 42 run 범위 0..317 units/run.
- 전량이 가격 붕괴(MILK step 372, STRAWBERRY step 451) 이후 발생. 붕괴 후 최고가 MILK 24 / STRAWBERRY 5 → 보유했어도 회수 불가 (검토자 재구성).

### F-T9 `[LOCAL]` yhay81-exact vs 긁어온 top 테이프 47개 (상대로만 사용): 452-0-18
- 47 테이프 × seeds [7,1000,1001,1002,1003] × 양좌석 = 470판, 결측 0. 점수 0.9617, Wilson 95% 하한 0.9403. 좌석 교대 결과가 다른 셀 2/235.
- 패배 9 (테이프, 시드) 셀: 3정훈 4 · Crop_Dusta 3 · Suliman_Tadros 1 · binghua 1. 마진 −934 ~ −23,377.
- 공개 4봇(96-0-0)과 달리 **포화되지 않은 로컬 게이트**다.
- 재현: `python3 coordination/proposals/claude/harness/pool.py --cand releases/public-yhay81-shop-router-0909-exact/main.py --opps $(ls private_artifacts/tapes/*.json | sed 's/^/tape:/') --seeds 7 1000 1001 1002 1003 --out x.jsonl`

### F-T10 `[LOCAL]` 개루프 farm 테이프 위에서 매도 레이어만 바꿔도 farm 계획이 어긋난다 (EXP-005, 2026-09-11)
- 매도 시점 변경 3종 모두 테이프풀에서 크게 짐: 즉시 매도 X1 0.9617→0.7277 (탐색 235셀, b=3 c=58) · 경합품만 X2 0.7362 (b=3 c=56) · 기준가 이상만 X5 0.0449 (156셀, b=0 c=141).
- 확인 실행(seeds 5101–5103 양좌석 282셀): X1 0.7872 vs parent 0.9787, b=0 c=54. 셰드 소멸 X1 11,032 vs parent 1,980 units (344 run), X1 만 미배치 SHEEP 7마리 × 4 run.
- 기제: 매도가 셰드 점유·현금 시점을 바꿔 테이프의 DROP/PICKUP/PLACE·BUY_ANIMAL 턴과 어긋남 (독립 검토 재계측).
- 반대 방향 관측: 같은 X1 이 Crop_Dusta_106275940 테이프 상대 seed 1002 에서 상대 뱅크를 121,859 → 32,649 로 무너뜨림 (상대 매출 154,584 → 63,770). 개루프 테이프는 가격 충격에 취약하다 — 우리 테이프도 마찬가지.
- 재현: `evidence/raw/EXP-005/judge_exp005.py` (원자료 같은 폴더), 하니스 `coordination/proposals/claude/harness/`.

### F-T11 `[LOCAL]` "군중 회피형" 품목 치환은 yhay81 골격에서 크게 진다 (2026-09-11, EXP-007 탐색 단계)
- yhay81 노동·이동 골격을 그대로 두고 품목만 이름 치환한 5개 변형. starter 상대 seed 7 뱅크 (parent 136,286):
  M1 STRAWBERRY→TOMATO 136,876 · M4 STRAWBERRY→CARROT 132,037 · M2 COW·SHEEP→GOOSE 55,904 · M3 M1+M2 58,840 · M5 SHEEP→GOOSE 43,039.
- 경쟁 상대 스크리닝 (47 테이프 seed 1001 seat0 + parent 패배 9셀 + parent·exp006 h2h 12판):
  M1 풀 0.191 vs parent 0.936 (b=0 c=35), h2h 0-0-12, parent 패배 셀 1/9 승 · M4 0.149 (b=0 c=37), h2h 0-0-12, 0/9, 셰드 소멸 5,701 units/65 run.
- 기제 (Jiro2_106270500 seed 1001): M1 은 TOMATO 131 units(4일 수명, 수확 일정 불일치) vs parent STRAWBERRY 249 units, 단가도 절반(기준가 60 vs 120) → 우리 매출 119,512 → 73,320, 상대는 STRAWBERRY 독점으로 116,145 → 125,553.
- → 저가 품목(TOMATO 60·CARROT 35·EGG 50)으로의 회피는 고가 품목(STRAWBERRY 120·MILK 160·WOOL 200·MELON 250)을 나눠 파는 손실보다 크다. 이 골격 위 치환으로는 두 번째 슬롯 후보가 나오지 않는다.
- 재현: `coordination/proposals/claude/harness/` 의 sellaudit·pool + 치환 래퍼(클라우드 /home/claude/lab/cand/sub/, 미전달).

### F-T12 `[OFFICIAL]` 최종 BT 는 "양쪽 에이전트가 끝까지 활성"인 경기만 센다 — 원문 재확인 (2026-09-12)
출처: discussion 732931 (https://www.kaggle.com/competitions/kaggriculture/discussion/732931), 2026-09-12 브라우저로 원문 직접 확인.
- Addison Howard (Kaggle Staff): *"The Final B-T tournament will use all episodes between active agents across the whole competition. Any episodes your agent played against now deactivated agents will not count."*
- Bovard Doerschuk-Tiberi (Kaggle Staff): *"BOTH agents need to still be active for the episode to count."*
- 귀결 1: 우리가 새로 제출하면 FIFO 로 은퇴하는 봇의 **경기 이력 전부가 최종 계산에서 사라진다**. 지금까지 은퇴시킨 것: v0, v1, yhay81 복사본 56147691.
- 귀결 2: 상대가 재제출해도 그 경기는 사라진다. 필드 churn 이 크므로 마감 직전·마감 후(10/01~10/15, 제출 잠김) 경기가 가장 잘 살아남는다.
- 귀결 3: 슬롯 교체는 **늦게 할수록 비싸다**. 교체하려면 빨리 하고, 마감 직전에는 하지 않는다.
- `coordination/RESET_2026-09-10.md` §1a 의 "매일 제출해도 손해가 없다"는 이 답변과 배치된다 — RESET 은 evaluation.md 만 근거로 했다. 이 항목이 우선한다(§2 진실의 순위: 공식·스태프 답변 > 우리 문서).


### F-T13 `[HOSTED]` 2026-09-15 01:13 KST 직접 CLI+UI snapshot — 활성 2슬롯 publicScore·순위 재확인
출처: `coordination/reports/codex/20260915-0115-KAGGLE-SNAPSHOT.md` (Codex, `kaggle competitions submissions kaggriculture -v` 직접 실행 + 공개 leaderboard UI, 완료 시각 상한 2026-09-14 16:13:12 UTC). [owner 이관안](../coordination/proposals/codex/20260915-owner-record-sync.md) §4 반영.
- EXP-006 `56165718` publicScore **1862.6**, EXP-007 `56175620` **1635.9**, 둘 다 COMPLETE. 09-14 10:47 UTC snapshot(1896.9 / 1647.4) 대비 각각 −34.3 / −11.5.
- 공개 UI: Sian(`<kaggle_user>`) **1,724위**. 1위 Majkel1337 3232.2, 10위 Thomas Tschinkel 2974.2 — 이 상금 경계는 2026-09-15 KST 값이며 09-10 23:16 UTC 값(10위 2960.9)과 날짜가 달라 직접 비교하지 않는다.
- 로컬 tar SHA 재확인: `coordination/proposals/claude/exp006/submission.tar.gz` `1c478c24…9721`, `releases/public-thomas-replay-router-v2-exact/submission.tar.gz` `8031d51a…0180` — 둘 다 기존 기록과 일치.
- 전문 기록: `evidence/HOSTED_LEDGER.md` "2026-09-15 01:13 KST" 절. episode 단위 W/D/L 재판독은 이 snapshot에 없음(`[N/A]`).
- 재현: `kaggle competitions submissions kaggriculture -v`; 위 snapshot 보고서 §2~§4.

### F-T14 `[ENGINE]` `shed_discarded` 는 "하루 종료 이월 초과분 소멸"만 센다 — in-day 소멸은 미계측 (2026-09-16)
엔진 `kaggriculture.py` sha256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`.
- `:843-856 _drop_inventories_to_shed(private, capacity)` — 하루 끝에 모든 unit inventory 를 shed 로 이월한다. `current = sum(shed.values())` → `room = max(0, capacity - current)` → `take = min(n, room)` → **`del inv[item]`**. `take < n` 인 초과분은 예외 없이 소멸한다. `shedCapacity` 기본값 100 (`:553` `:866` `:908`).
- `:866-878 _end_of_day` 가 player 순서대로 위 함수를 1회씩 호출하고 **그 뒤에** `farm["farmer"]` 리셋·`farm["hands"] = []` 를 한다 → drop 시점에는 그날 마지막 위치와 hands 구성이 아직 살아 있다.
- `:940-947` 스텝 순서 `unit actions → _process_market → _town_consume → _decay_plants → _end_of_day` → 그날 마지막 턴의 시장 매도는 이월 **앞**에서 끝난다.
- ~~**동일한 소멸이 in-day 경로에도 있다**: `:344-355 DROP` 과 `:393-411 PLACE` 도 용량 초과분을 `del inv[item]` 으로 버린다.~~
  **[2026-09-18 정정 — PLACE 부분은 틀렸다]** in-day 소멸 경로는 `:344-355 DROP` **하나뿐**이다.
  `:393-411 PLACE` 는 `n = min(n, room)` 뒤 **`inv[item] -= n`** 만 하므로 **초과분이 unit inventory 에 보존**된다 — 소멸하지 않는다.
  근거: engine 소스 직접 확인 + fixture `tests/test_instrument_exp011.py::test_drop_discards_but_place_retains_overflow_and_animal_is_not_loss`
  (shed 98/100, inv 5 → DROP loss 3·left 0 / PLACE loss 0·left 3) + EXP-011 실측 `shed_discarded_inday_place` 26/26 record 에서 0.
  정정 경위: `coordination/reports/claude/20260918-EXP011-REVIEW-ADJUDICATION.md` A1.
  재현: `sed -n '344,355p;393,411p' .venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`
- 그런데 `tools/instrument.py` sha256 `284dee4cdacfc56aab2125f8a92b41df53e14744cca7a8cafa10b853fb6d0629` 의 drop hook(`:450-461`)은 `_drop_inventories_to_shed` **만** 감싼다(`lost = max(0, carried - moved)`).
  → **`shed_discarded` 값은 일일 종료 경로 손실만이며 총 자원 손실의 하한이다.** in-day DROP/PLACE 초과분은 어느 counter 에도 잡히지 않는다.
  **[2026-09-18 추가]** EXP-011 의 새 runner `tools/instrument.py` sha256 `ca64256f941f2098cafc531fc422363c5757995f721b449369ce72877a33fe28` 가
  관측 전용 counter `shed_discarded_inday_drop` / `shed_discarded_inday_place` 를 신설했다(zero gate 밖, release 판정 불변).
  실측은 gated 16 record 전부 0/0 이다(F-T20). `shed_discarded` 의 정의·값은 변경되지 않았다.
- 재현: `sed -n '843,880p;340,412p;900,950p' .venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py` · `sed -n '440,465p' tools/instrument.py`

### F-T15 `[LOCAL]` P1b parent A 의 `shed_discarded` 482 는 16/16 record 에서 shed 포화와 동반한다 (2026-09-16)
대상: actual parent A tar `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721`, manifest `46fd9e5eacb79200fd03ce2302649e05e0f75f2eb51f77d2f745b87fb6e4801c` 의 고정 13경기 / gated parent record 16개. 13/13 이 `steps=720` `statuses=["DONE","DONE"]`.
- group 별 합: self_play **40** (6 record) · builtin_smoke **10** (6) · hosted_loss_stress **418** (2) · exp008_control **14** (2) = **482**. 16/16 record 가 nonzero.
- record 별: target 1125321547 양 좌석 각 **209** (`noop_actions` 1,149, `hands_length_mismatch` 46) · control 1989066512 각 7 · self 7·1001 각 7 · self 1000 각 6 · starter 7 각 3 · starter 1000·1001 각 1.
- **16/16 record 가 `daily_max_shed` 에서 `shedCapacity` 100 에 최소 1일 도달**하고, 100 도달 일수가 클수록 `shed_discarded` 가 크다(target 6일/209, control·self 1~2일/6~7, starter 1일/1~3). 예외 record 없음.
- target 2 record 는 hosted episode 108076177 의 exact 재현이며 최종 reward `[58,246 / 167,541]` 이 hosted 결과 및 postmortem `coordination/reports/codex/20260913-0250-EXP006-HOSTED-POSTMORTEM.md` 와 일치한다.
- **원인은 귀속되지 않았다**: day 별 손실·drop 시점 shed 점유·소멸 item·보유 unit·그 unit 의 마지막 action·shed 인접 여부가 기존 JSON 에 **전부 없다**(`N/A`). `tools/postmortem.py` 는 shed 필드를 0건 추출하며 `make()`+`env.run()` 으로 새 경기를 만든다 → 이 목적에 사용 불가. 필요한 최소 계측은 `experiments/cards/EXP-011-shed-discard-attribution.md` §B.
- 재현: `python3 scratch/claude_shed_attribution_20260916.py` (read-only, 새 경기 생성 없음, exit 0 = `aggregate.json` 의 9개 counter 합·nonzero record 수와 완전 일치)

### F-T16 `[LOCAL]` zero-gate 실패는 우리 layer가 아니라 공개 parent에서 상속된 것이고, 두 활성 제출 모두 실패한다 (2026-09-16)
- **EXP-006 layer는 self-play counter를 0만큼 바꿨다.** `releases/public-yhay81-shop-router-0909-exact/preflight_selfplay.json`(무수정 yhay81 exact)과 P1b의 EXP-006 self-play가 세 seed 전부에서 `noop_actions`·`shed_discarded` 동일: seed 7 = 44/7, seed 1000 = 114/6, seed 1001 = 44/7. reward만 다르다(yhay81 108,809 vs EXP-006 108,091 @seed 7) — clone-preempt는 매도 시점을 바꾸지만 무음 실패 counter는 건드리지 않는다.
- **EXP-007(thomas router)도 zero gate를 실패한다.** `releases/public-thomas-replay-router-v2-exact/preflight-selfplay.json`: seed 7 `noop=62 shed_discarded=0 buy_failed=0`, seed 1000 `74/7/1`, seed 1001 `62/0/3`. (schema 2 기록이며 schema 3 재측정은 `N/A`.)
- → 현재 활성 2슬롯(56165718 = 1862.6, 56175620 = 1635.9) **둘 다** release zero gate를 통과하지 못한 상태로 hosted 에서 돌고 있다. zero gate 실패는 hosted 실행을 막지 않는다(엔진·Kaggle 규칙이 아니라 우리 자체 release 규율이다).
- ~~**손실 규모 상한**: … `shed_discarded` 209 units ≈ **최대 19,200 coin** … 전량 회수해도 큰 패배는 뒤집지 못한다.~~
  **[2026-09-18 정정 — '최대'는 근거 없는 표현이었다]** 두 가지 **추정** 방식이 있고 **어느 쪽도 상한이 아니다.**
  - **방식 A (원래 F-T16)**: 그 경기 **전체** 실현 매도 평균 단가를 소멸 개수에 곱한다. target 92.0 coin/unit(78,122 / 849) × 209 ≈ **19,231**, self seed 7 86.2 × 7 ≈ 603, gated 16 record 합 ≈ **43,977**.
  - **방식 B (item 별 실현 단가)**: 같은 경기의 `realized_sell[item].avg_price` 를 그 item 의 소멸 수량에 적용한다. target ≈ **13,938**, self seed 7 ≈ **294**, control ≈ **308**, gated 16 record 합 ≈ **30,886**.
  - **A 는 B 대비 29.8% 과대추정**이다. 소멸 item 구성이 싼 품목에 치우쳐 있기 때문이다 — gated 482 units 중 WHEAT(base 25) **61.4%**, target 418 units 중 WHEAT **70.8%**. base 가중 평균은 gated 61.8 / target 56.0 coin/unit 이며 전체 매도 평균 92.0 과 다르다. 미판매 item 은 0건이라 B 는 전 품목에서 계산됐다.
  - **B 도 상한이 아니다.** 엔진 `market_price(item, inventory)` 는 `inventory > I0` 구간에서 재고의 감소함수(`:192-206`)이고 `_commit_unit` SELL 은 체결마다 `market["inventory"][item] += 1` 한다 → 추가 매도는 단가를 낮춘다. 반대로 drop 시점 marginal price 가 그 경기 평균보다 높았을 수도 있다. **drop 시점의 market inventory·price 는 EXP-011 artifact 에 기록돼 있지 않다** → **엄밀한 상한 `N/A`**. 주장하려면 per-step market 상태를 기록하는 별도 계측이 필요하다.
  - 마진 대비: target 패배 마진 **109,295** (58,246 vs 167,541) 대비 A 17.6% / B 12.8%. baseline 은 뱅크 68k~136k 대비 1% 미만.
  - **이 환산은 정적 시나리오이지 causal effect 가 아니다.** "소멸분을 그 단가로 그대로 은행에 더한다"는 가정이며, 실제 회수는 매도 타이밍·가격·현금 연쇄·상대 궤적을 전부 바꾼다. **"전량 회수해도 큰 패배는 뒤집지 못한다"를 확정 결론으로 쓰지 않는다.** hosted 패배 마진 분포는 여전히 미측정(`N/A`, 계획 §5.3 P1c).
  - 근거: `coordination/reports/claude/20260918-EXP011-CLOSURE-PRIORITY-ADJUDICATION.md` 지적 1·2.
  - 재현: `python3 scratch/claude_exp011_owner_20260918/discard_value_estimates.py` · `python3 scratch/claude_exp011_owner_20260918/discard_item_mix.py`
- 재현: `python3 -c "import json;[print(p,[ (e['seed'],e['players'][0]['noop_actions'],e['players'][0]['shed_discarded'],e['players'][0]['buy_failed']) for e in json.load(open(p))]) for p in ['releases/public-thomas-replay-router-v2-exact/preflight-selfplay.json','releases/public-yhay81-shop-router-0909-exact/preflight_selfplay.json']]"` · P1b 대조는 `python3 scratch/claude_shed_attribution_20260916.py`

### F-T17 `[HOSTED]` 09-12 window 패배 마진 분포 — 접전은 흔하지만 `shed_discarded` 규모보다 한 자릿수 크다 (2026-09-16 재분석)
출처: 기존 `experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json` (window `2026-09-12T01:13:25` ~ `11:14:20`, submission 당 50판, time-matched·상대/시드 미매칭). **새 조회 없음 — 기존 파일 재분석이다.**

| | EXP-006 `56165718` | EXP-007 `56175620` |
|---|---|---|
| W/D/L (50판) | 41 / **0** / 9 | 21 / **9** / 20 |
| 패배 마진 median | **13,359** | **3,606** |
| 패배 마진 min | **252** | 602 |
| 패배 < 1,000 | 1 / 9 | **4 / 20** |
| 패배 < 5,000 | 2 / 9 | **13 / 20** |
| 승리 < 10,000 | 29 / 41 | 14 / 21 |

- **EXP-007 의 무승부 9판은 전부 마진 정확히 0** (예: ep 108029800 121,737 vs 121,737, ep 108125200 145,066 vs 145,066). 같은 공개 노트북(thomas replay router v2 exact) 복제본끼리 만나 **완전 대칭 경기**가 된 것이다. EXP-006 은 무승부 0판이다 — clone-preempt layer 가 대칭을 깬다. (상대 pool 이 다르므로 causal 주장은 아님. HYP-0006 은 계속 INCONCLUSIVE.)
- **함의 (가정 하 산술 시나리오 — causal effect 아님):** 접전은 흔하다. `shed_discarded` 회수 가치의 baseline 추정은 6~7 units ≈ **294~308 coin**(방식 B) 또는 **520~600 coin**(방식 A) 이고(F-T16 정정 참조), 패배 마진 median 은 3,606~13,359 다. **소멸분을 그 단가로 그대로 최종 은행에 더한다는 정적 가정**을 두면 50판 중 뒤집히는 것은 EXP-006 에서 **1판(마진 252 coin)** 수준이다 — point score 0.82 → 0.84.
  **[2026-09-18 한정]** 이것은 **확정 결론이 아니다.** 실제 회수는 그 경기의 매도 시점·가격·현금·이후 행동과 상대 궤적을 바꾸므로 경기별 회수 counterfactual 은 측정되지 않았다(`N/A`). 이 숫자를 작업 우선순위의 확정 근거로 쓰지 않는다. 근거: `coordination/reports/claude/20260918-EXP011-CLOSURE-PRIORITY-ADJUDICATION.md` 지적 2.
- **더 큰 신호는 무승부 9판이다.** 마진 0 을 깨는 개입은 `shed_discarded` 수리보다 W/D/L 기여가 크며, 그 기제는 이미 HYP-0006 에 등록돼 있다.
- 한계: 09-12 window 이며 09-15 기준 점수(1862.6 / 1635.9)와 다른 시점이다. 상대 pool 이 서로 달라 두 제출을 직접 비교하지 않는다. 현재 window 재수집은 `N/A` (계획 §5.3 P1c).
- 재현: `python3 -c "import json,statistics as st; d=json.load(open('experiments/results/hosted_episode_compare_56165718_56175620_20260912T111420Z.json')); [print(s, sorted(round(e['opponent_reward']-e['reward']) for e in b['episodes'] if e['result']=='L')) for s,b in d['submissions'].items()]"`

### F-T18 `[HOSTED]` 09-16 leaderboard — 동메달 경계 2,442.5, 우리 격차 716점. 공개 노트북은 저자의 실제 제출물이 아니다
출처: `kaggriculture-publicleaderboard-2026-09-16.csv` (사람이 09-16 12:37 KST 다운로드), **9,234팀** (09-10 8,481팀 대비 +753).
- 메달 경계: **금** rank 28 = 2,922.0 · **은** rank 461 = 2,679.7 · **동 rank 923 = 2,442.5**.
- **Sian rank 2,005, 1,726.6.** 동메달까지 **716점**. 09-10 snapshot 기준 추정치(440점)보다 악화됐다 — 점수는 내리고(1,862.6 → 1,726.6) 팀 수와 경계는 올랐다.
- **top 50 전원이 `SubmissionCount == 2`다.** 상위권은 슬롯 2개를 전부 쓴다.
- **공개 노트북 저자의 실제 제출 점수 vs 우리가 그 노트북을 복사해 받은 점수:**

| 저자 (공개 자료) | 저자 본인 순위/점수 | 그 공개물을 우리가 복사한 결과 |
|---|---|---|
| Thomas Tschinkel — "95.5% Win Rate via Replay Routing" | **rank 13 / 2,986.6** | EXP-007 `56175620` = **1,635.9** (byte-exact 복사) |
| yhay81 — "Shop Router 0909" | rank 937 / 2,436.2 | 복사본 `56147691` ≈ 2,188.4 (접수 7.3h, 수렴 전) |
| boatlee — "V14 Clone Preemption" (HYP-0006 착상원) | rank 1,526 / 2,050.8 | 아이디어만 채택 (EXP-006) |
| xuantianfengwu — "R10 Adaptive Allocator" (W01) | **rank 5,759 / 593.1** | 미채택 (triage 보류) |

  → **공개된 노트북은 저자의 실제 제출 에이전트가 아니다.** rank 13 저자의 공개물을 그대로 복사해도 1,636 이고 저자 본인과 **1,350점** 차이가 난다. 공개 노트북 복사의 상한은 낮다.
- 재현: `python3 -c "import csv;rows=list(csv.DictReader(open('kaggriculture-publicleaderboard-2026-09-16.csv')));sc=sorted([(float(r['Score']),r['TeamName']) for r in rows],key=lambda x:-x[0]);n=len(sc);print(n, sc[922], [x for x in enumerate(sc,1) if x[1][1]=='Sian'])"`

### F-T19 `[OFFICIAL]` 에피소드 리플레이는 공개 데이터이며 Kaggle 이 상위 에피소드 일일 데이터셋을 직접 배포한다
- `docs/official/rules.md:108` — *"A replay of each episode of the competition, which includes the actions taken by your Submission in the episode, may be publicly available and downloadable."*
- `docs/official/rules.md:68-70` §6a — 외부 데이터는 **모든 참가자에게 공개·동등 접근·무비용**이면 사용 가능.
- `docs/discussion/731215_Daily_Top_Episodes_Dataset.md` — Kaggle 공식 계정이 매일 평균 레이팅 상위 에피소드를 최대 20GB 씩 묶어 `https://www.kaggle.com/datasets/kaggle/kaggriculture-episodes-index` 로 배포하며, 본문이 **"helpful for everyone trying IL/BC, bootstrapping RL"** 라고 용도를 명시한다. 09-12 댓글 기준 일별 657~928 에피소드, 중앙 avg_score 2,735~3,080.
- → **상위 에이전트의 실제 행동 스트림 확보는 규정상 허용되고 수단도 공식적으로 제공된다.** 이는 §2.4d "private sharing" 금지와 무관하다(공개 데이터).
- 단, 수상 시 `rules.md` §2.8 winners obligation 으로 **제출물 생성에 쓴 소스 전부를 CC-BY 4.0 공개**해야 한다. 타인 리플레이 기반 artifact 의 공개 범위는 사람 확인 사항(`N/A`).
- 보유 현황: `private_artifacts/tapes/` 47 tape — **ymg_aq(현 rank 6, 3,022.8) 6판**, **Mengfei Li(rank 12, 2,987.1) 6판**, binghua(rank 86) 5판, Remielle(rank 260) 등.
- 재현: `sed -n '108p;68,70p' docs/official/rules.md` · `ls private_artifacts/tapes/`


### F-T20 `[ENGINE]` `[LOCAL]` EOD 소멸량은 `max(0, carried − room)` 과 항등이고 **이월 순서와 무관**하다 — EXP-011 확정 (2026-09-18)

대상: EXP-011 산출물 `experiments/results/p1_shed_attribution/` (`aggregate.json` sha256 `22ebb92731e8c65c1ffeda249b8fdcf197a967f203eafafd3150c59d766430ba`,
`allocation_audit.json` sha256 `66ed824393d41aaae507866f327f5f9ae8f8bfa7c46d7993b10e197e43011fa8`, freeze commit `0a4b10f`),
runner `tools/instrument.py` sha256 `ca64256f941f2098cafc531fc422363c5757995f721b449369ce72877a33fe28`,
card r2(측정 당시) sha256 `8736d403e3fdf870de74060d7d0a7c2660ff311a6aed24b2c8ff5cc503e5dd0e`.

- **계측은 경기를 바꾸지 않았다.** P1b 원본 cell 과 직접 대조해 **26 player-record 전부** `rewards`·`statuses`·`steps` 와
  9개 counter(`shed_discarded` `noop_actions` `buy_failed` `hire_failed` `seed_blocked_plant`
  `hands_length_mismatch_count` `shed_unsold` `orders_truncated` `exceptions`)가 **정확히 일치**한다 — mismatch **0**.
- **482 단위 전부 귀속.** gated 16 record 합 482, loss event **44**개. class 는
  `ROOM_PARTIAL|REMOTE|NO_DEPOSIT_ATTEMPT` **480** + `ROOM_PARTIAL|ADJACENT|NO_DEPOSIT_ATTEMPT` **2**.
  지배 class share: S1 64/64 = 1.0, S2 416/418 = 0.9952, record 별 단독 최다 16/16 → 카드 판정 `REPAIR_AUTHORIZED`.
- **`ROOM_PARTIAL` 은 "공간이 충분했다"가 아니다.** 44/44 loss event 에서 `carried_total > room`
  (`room = shedCapacity − shed_total_before`). `carried_total <= room` 인 loss event 는 **0건**.
  예: target seat0 day15 step383 — shed 55, room 45, carried 51, loss 6.
- **항등식**: 모든 event 에서 `discarded_total == max(0, carried_total − room)` 이 성립한다 — 위반 **0**.
  엔진의 greedy 배분은 `room` 소진까지 채우므로 **총 예치량 = `min(carried_total, room)`** 이다.
- **순서 불변성**: 각 loss event 에 대해 unit 순열 × item 순열을 무작위 200회 적용해 엔진과 동일한 배분을 재현했을 때
  **총 소멸량이 달라진 event 0건**. 순서는 *어느 물건이* 버려지는지만 바꾼다.
  → **최종 이월의 순서나 클램프만 바꿔서 총 소멸량을 줄이는 것은 불가능하다.** EXP-012 는 사전등록하지 않는다
  (`experiments/cards/EXP-011-shed-discard-attribution.md` §G C-3).
- `shed_discarded_inday_drop` / `shed_discarded_inday_place` 는 gated 16 record 전부 **0** (이 13경기·이 tape 한정 관측).
- 재현: `python3 scratch/claude_exp011_owner_20260918/verify_d1c_vs_p1b.py` (mismatch 0) ·
  `python3 scratch/claude_exp011_owner_20260918/verify_order_invariance.py` (위반 0 / 순열 0). 둘 다 새 경기 생성 없음, 파일 쓰기 없음.
- 🔁 **`run.py --verify-only` 경고 — 수정 전 위험과 수정 후 동작을 구분한다** `[2026-09-18 정정]`
  원문 경고는 삭제하지 않는다. 아래 (1) 은 커밋 `35e9f45` **이전** runner 에 대해 참이었고, (2)(3) 이 현재 동작이다.

  **(1) 수정 전 위험 — 원문 그대로 보존** (`[2026-09-18 추가]` 당시 runner
  `experiments/results/p1_shed_attribution/run.py` sha256 `20547a4ac8a47045b254bbe6534c2c543f052d2cf6c1f07ba1c21bf0066eefb8`,
  즉 `freeze.json['inputs']` 가 고정한 바로 그 값):
  > ⚠️ **`python3 experiments/results/p1_shed_attribution/run.py --verify-only` 를 live checkout 에서 실행하지 말 것**
  > `freeze.json['inputs']` 가 카드를 **측정 당시 r2 SHA** 로 고정하는데, 카드에 정정 이력(§G)이 붙어 SHA 가 바뀌었다.
  > `verify()` 는 `identity()` 를 D1-a gate 에 넣고 **마지막에 `aggregate.json` 을 덮어쓴다** → live 에서 돌리면
  > `card_verdict='INVALID'` 가 기록되어 측정 산출물이 파괴된다. freeze commit `0a4b10f` 의 r2 카드를 복원한
  > **별도 checkout 또는 결과 폴더 사본**에서만 실행한다. `freeze.json` 을 새 카드 SHA 로 덮어쓰지 않는다.
  > 개선 제안은 `coordination/proposals/claude/20260918-EXP011-verify-only-guard.md` (run.py 는 Codex 소유).

  **(2) 수정 후 동작 — 이 위험은 해소됐다** `[LOCAL]` (Codex, 커밋 `35e9f45`
  `coordination/reports/codex/20260918-P1C-AUDIT-VERIFY-GUARD.md`; 현재 runner sha256
  `883c4792d855dbed2fccfc0e16a83f608d820fc9a1d82c0489168d0df3d9de37`)
  - `verify()` 는 `verify(*, persist=False)` 가 됐고 `write(ROOT/'aggregate.json', result)` 는 `if persist:` 아래로 들어갔다.
  - `main()` 의 `--verify-only` 분기는 `verify()` 를 인자 없이 호출한다 → **쓰기 없음, 판정만 stdout**.
    쓰기는 13-cell batch 를 실제로 완료한 경로(`main()` 끝의 `verify(persist=True)`)에만 남는다.
  - regression test `tests/test_exp011_verify_readonly.py` 가 identity 성공/실패 **양쪽 모두**에서
    `write` 호출이 없고 보호 대상 4파일 SHA 가 불변임을 강제한다.
  - **owner 독립 재현 2026-09-18**: `python3 -m pytest tests/test_exp011_verify_readonly.py tests/test_audit_p1c_replays.py -q` → **3 passed**.
    live checkout 에서 `python3 experiments/results/p1_shed_attribution/run.py --verify-only` 를 직접 실행 →
    exit **1**, stdout `INVALID INVALID checks 1603 …`, 그리고 `aggregate.json` `freeze.json` `commands.json`
    `allocation_audit.json` **4개 SHA 전후 완전 동일**(`aggregate.json` = `22ebb927…` 유지).
  - → **live checkout 실행 금지 사유(원본 파괴)는 더 이상 유효하지 않다.**

  **(3) live 의 `INVALID` 는 provenance drift 이지 역사적 결과의 무효화가 아니다** `[LOCAL]`
  - freeze 의 30개 input 중 **불일치는 정확히 2개**뿐이다 (owner 재현):
    `experiments/cards/EXP-011-shed-discard-attribution.md` (측정 당시 r2 `8736d403…` → 정정 이력이 붙은 현재 카드)
    와 `experiments/results/p1_shed_attribution/run.py` (`20547a4a…` → guard 적용본 `883c4792…`).
  - **측정 입력은 전부 일치**한다 — 엔진 `kaggriculture.py`/`.json`, `tools/instrument.py`, tape 2종,
    P1b parent·cells 13개, `gate_contract.py`, 제출 tar. 즉 데이터는 흐르지 않았고 **문서·러너 SHA 만 흘렀다**.
  - 따라서 `card_verdict='INVALID'` 는 **D1-a identity gate 하나**가 깨진 결과이며(나머지 1602 check 는 통과),
    **보존된 역사적 EXP-011 결과(`aggregate.json` `22ebb927…`, 판정 `PASS` / `REPAIR_AUTHORIZED`)를 무효화하거나 덮어쓰지 않는다.**
  - **freeze 와 측정 당시 SHA, 기존 결과·임계·판정은 그대로 유지한다.** `freeze.json` 을 현재 카드/러너 SHA 로
    덮어쓰지 않으며, 원장·registry 가 인용하는 card SHA 는 r2 `8736d403…` 그대로다.
  - SHA 일치까지 포함한 완전 재현이 필요하면 freeze commit `0a4b10f` 를 복원한 별도 checkout/사본에서 실행한다.
    Codex 기록: `experiments/results/p1c_20260918_audit/verify_readonly_check.json`.

  **(4) 남은 쓰기 경로 — 아직 보호되지 않았다** `[LOCAL]` `[2026-09-18 owner 확인]`
  `experiments/results/p1_shed_attribution/check_allocation.py` 는 `--verify-only` 같은 분기 없이
  무조건 `allocation_audit.json` 을 다시 쓴다(:35). 이 파일은 `run.py` guard 의 적용 대상이 아니었다.
  live checkout 에서 이 스크립트를 실행하지 말 것. 개선은 Codex 소유 경로이므로 제안으로 낸다
  (`coordination/reports/claude/20260918-EXP011-VERIFY-GUARD-ACCEPTANCE.md` §잔여 갭).

### F-T21 `[ENGINE]` `[LOCAL]` 손실을 줄이는 유일한 agent 레버는 **총 보유량 감소**이며, 그 산술 상한은 482/482 다 (2026-09-18)

- 엔진 스텝 순서는 `:940-947` `unit actions → _process_market → _town_consume → _decay_plants → _end_of_day` 이고,
  `_commit_unit` 의 `SELL` 은 **shed 에서만** 차감한다(`private["shed"][item] -= 1`; shed 재고 0 이면 실패).
  unit inventory 는 직접 매도할 수 없다.
- 따라서 EOD 직전의 보존량 `T = shed 점유 + 전 unit carried` 에 대해 손실은 `max(0, T − shedCapacity)` 이고,
  **DROP·PLACE 로 미리 옮겨도 `T` 는 보존되므로 손실은 변하지 않는다.** `T` 를 줄이는 개입
  (마지막 턴 매도 증량, 생산·수확 조절)만이 손실을 줄인다.
- **매도 여력은 충분하다(산술 상한).** gated 44 loss event **전부**에서 EOD 직전 shed 재고가 100% 판매 가능
  `PRODUCTS` 였고(비판매 품목 0), 재고량 **9~82** 가 손실 **1~28** 을 매 event 에서 초과했다.
  매도 1 unit 당 손실 1 unit 감소이므로 상한은 **482/482 = 100%**.
- **이것은 상한일 뿐 효과 증거가 아니다.** `market_price` 는 시장 재고의 함수라 매도 증량은 단가를 눌러 이후 매도까지
  손해를 주고(§3 "흡수량 초과 매도"), 현금 변화가 BUY/HIRE/PLANT 연쇄와 action parity 를 바꾼다. 전부 **미측정(`N/A`)**.
- ~~**가치 상한은 이미 닫혀 있다** … → **shed 경로는 회수해도 순위 가치가 작다.**~~
  **[2026-09-18 정정 — 상한이 아니라 추정이었다]** F-T16 정정 참조: target 209 units 의 coin 환산은 방식 A ≈19,231 /
  방식 B ≈13,938 이고 **엄밀한 상한은 `N/A`** 다. 마진 109,295 대비 12.8~17.6% 라는 것도 **정적 환산 시나리오**이지
  causal effect 가 아니다. **"shed 경로는 가치가 작다"를 확정 결론으로 쓰지 않는다.** 확정된 것은 아래 순서 불변성 하나뿐이다.
- 참고(비교 근거 아님): gated 16 record 의 `noop_actions` 합 **3,488** 은 op 별로 이미 분해돼 있다 —
  `CARE` 846 / `COLLECT_FERTILIZER` 668 / `FEED` 578 / `WATER` 556 / `HARVEST` 550 / `FERTILIZE` 106 /
  `PLACE` 102 / `PICKUP` 36 / `DROP` 30 / `DIG` 16 (합 3,488, 누락 0). **coin 귀속은 `N/A`.**
  **[2026-09-18 주의]** `noop_actions` 3,488 은 **unit-turn 단위 action 횟수**이고 `shed_discarded` 482 는 **item 개수**다.
  **두 수의 비(7.2배)는 전략 가치·회수 가능 coin·기대 승률의 비교가 아니며 작업 우선순위의 근거로 쓰지 않는다.**
  `noop_actions` 의 정의와 혼입 문제는 F-T22 를 볼 것.
- 재현: `python3 scratch/claude_exp011_owner_20260918/sellable_headroom.py` ·
  `sed -n '940,947p;375,392p' .venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`


### F-T22 `[ENGINE]` `noop_actions` 는 "PASS 치환 횟수"가 아니다 — 세 종류가 섞여 있고 seed-blocked PLANT 는 빠진다 (2026-09-18)

계측기 `tools/instrument.py` sha256 `ca64256f941f2098cafc531fc422363c5757995f721b449369ce72877a33fe28` `:537-541`:

```python
elif op in _TILE_OPS:
    if (_tile_sig(farm, before_pos[0], before_pos[1]) == before_tile
            and _inv_total(private, unit_index) == before_inv):
        c.noop_actions += 1
        c.noop_by_op[op] = c.noop_by_op.get(op, 0) + 1
```

- **판정 기준은 "엔진 호출 뒤 tile JSON 서명과 그 unit 의 inventory 총량이 둘 다 불변"** 이다. PASS 치환 여부를 보지 않는다.
  `_TILE_OPS` (`:46-49`) = PLANT·WATER·HARVEST·FERTILIZE·DIG·BUILD_COOP·BUILD_PASTURE·FEED·COLLECT_FERTILIZER·CARE·PICKUP·PLACE·DROP 13개.
  `_tile_sig` 는 `json.dumps(tile, sort_keys=True)` (`:299-300`), `_inv_total` 은 **개수 합**만 본다 (`:303-307`).
- **최소 세 종류가 한 counter 에 혼입된다**:
  (a) 엔진이 전제조건 불충족으로 거부한 action, (b) 실행됐으나 대상이 이미 목표 상태여서 변화가 없는 **불필요한 중복 요청**,
  (c) 관측 축(tile 서명 + inventory 총량) **밖**에서만 변한 action.
  (b) 실례: 엔진 `:524-530` `CARE` 는 `tile["cared_today"]` 가 이미 `True` 면 그대로 return 한다 — **PASS 치환 없이** 무변화다.
- **역방향 누락**: 엔진 `:920-931` 의 atomic PLANT 검증은 씨앗 부족 작물의 PLANT 를 `_apply_unit_action` **호출 전에** `["PASS"]` 로
  치환한다. 그 결과 op 가 `"PASS"` 라 `_TILE_OPS` 에 들어오지 않아 **`noop_actions` 에 전혀 잡히지 않는다.**
  그것은 별도 counter `seed_blocked_plant` (gated 16 record 합 56) 가 센다. → **"PASS 치환 = `noop_actions`" 는 양방향으로 틀렸다.**
- **추가 한계**: `_inv_total` 은 총 개수만 보므로 1:1 품목 교환은 탐지되지 않는다. `money` 와 `private["seeds"]` 변화는 관측 축 밖이다.
  `_MOVES` (NORTH/SOUTH/EAST/WEST) 는 별도 `blocked_moves` 로 센다.
- **따라서 `noop_actions` 총계는 diagnostic 이며 "고칠 수 있는 낭비 action 수"가 아니다.** 이 counter 를 쓰는 후속 진단 카드의
  1차 산출물은 coin 환산이 아니라 **reason taxonomy**(엔진의 어떤 분기에서 무변화가 되었는가) 여야 한다.
- 재현: `sed -n '46,49p;299,307p;537,541p' tools/instrument.py` · `sed -n '524,530p;915,935p' .venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`

## 2026-09-20 파일 agent 의 진입점 = "마지막 callable" `[ENGINE]`

- `kaggle_environments/agent.py:64` `get_last_callable` 은 파일을 `exec` 한 뒤 **모듈 전역 dict 에서 callable 인 값 중 마지막 것**을 agent 로 쓴다. `:149` 파일 경로 agent 는 이 함수로 로드된다. 이름이 `agent` 인 함수를 찾는 것이 아니다.
  dict 는 **처음 대입된 순서**를 유지하므로, 앞에서 정의한 `agent` 를 나중에 다시 대입해도 위치는 앞에 남는다.
- 실례: F0 P2 제출본 `main.py`(SHA `cddf51ea…a94d`)를 exec 하면 마지막 callable 은 `_e336_agent`, 모듈 전역 `agent` 는 **다른 객체**다. hosted 는 `_e336_agent` 를 돌린다.
- 영향: `tools/instrument.py:617-624` `load_agent` 는 `getattr(mod, "agent")` 를 쓰므로 이런 파일에서 **hosted 와 다른 함수를 시험한다.** `tools/arena.py:58-59` 는 경로를 `env.run` 에 넘겨 엔진 로더를 쓰므로 hosted 와 같은 함수를 시험한다.
  → 09-19 F0 gate(instrument) 중 P2·D3 는 다른 함수로 측정됐을 수 있다(2026-09-20 Claude 실행 보고: V2 는 두 방식 결과가 seed 10/10 다름). arena 기반 진단 결과는 영향 없음.
- AGENTS §6 "진입점은 `main.py` 의 `agent(obs)`"는 우리 자체 파일에서는 참이지만(마지막 callable 이 `agent` 일 때) **일반 규칙으로는 부정확하다.** 판정 기준은 엔진 로더다(§2 진실의 순위).
- 재현: `sed -n '40,64p;140,152p' .venv/lib/python3.13/site-packages/kaggle_environments/agent.py` · `python3 -c "import tarfile;s=tarfile.open('releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz').extractfile('main.py').read().decode();e={};exec(compile(s,'main.py','exec'),e);l=[v for v in e.values() if callable(v)][-1];print(l.__name__, l is e['agent'])"`

## 2026-09-20 시장 주문 체결 순서와 거울전 무승부 `[ENGINE]` `[HOSTED]`

- `[ENGINE]` `kaggriculture.py:544-628` `_process_market`: 두 플레이어의 market 주문을 **slot 번호 순서대로** 처리한다(i = 0,1,2,…). 같은 slot 번호의 SELL/BUY 는 **1개 단위 lockstep** — 매 단위마다 두 플레이어가 **같은 commit 전 재고로 가격을 받고** 그 다음 둘 다 체결한다. HIRE·BUY_LAND 는 slot 마다 **player 0 먼저** 처리.
  → 같은 turn 에 같은 품목을 팔 때 **더 앞 slot 에 둔 쪽이 먼저 팔아** 높은 가격을 받는다. 같은 slot 이면 단위별로 같은 가격이다(대칭).
- `[HOSTED]` P2(56347732) 2026-09-20 수집 112경기 중 무승부 7판(`evidence/raw/p2_losses_20260920/features.csv`, margin 0). 확인한 1판(episode 110866715, 상대 Anaconda)은 **두 플레이어 행동이 719/719 턴 전부 동일**, 최종 100,774 대 100,774 — 상대가 P2 와 같은 코드다. 무승부 7판 에피소드: 110866715, 110852721, 110829615, 110771965, 110768678, 110736042, 110723852.
- `[HOSTED]` 같은 경기에서 P2 의 고가 SELL(MILK·WOOL·MELON·STRAWBERRY)이 있는 122턴 중 첫 고가 SELL 이 slot 0 이 아닌 턴이 **13턴**(slot 1: 12, slot 2: 1).
- `[HOSTED]` 패배·무 32판 중 30판, 대조 승리 32판 중 30판에서 상대가 초반 143턴 farmer+hands 90% 이상 일치(같은 가족). 패배 25판 중 18판은 3,000 코인 이내.
- 재현: `sed -n '544,628p' .venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py` · `python3 -c "import json;r=json.load(open('private_artifacts/p2_losses_20260920/raw/episode-110866715-replay.json'));s=r['steps'];print(sum(s[t][0]['action']==s[t][1]['action'] for t in range(1,720)), r['rewards'])"`
