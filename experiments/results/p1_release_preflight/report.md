# P1b actual parent A release preflight — 13경기 실행 결과

1. **무엇을 시험했는가:** 실제 active parent A 제출 tar를 새 clean-room에 풀고, 승인된 self-play 3판·starter 6판·target/control stress 4판을 고정 seed·좌석·상대로 실행했다.
2. **왜 하는가:** 새 전략 전에 현재 제출 artifact가 schema-3 release 기준을 만족하는지 확인하기 위해서다.
3. **무엇을 측정했고 결과가 어땠는가:** `[LOCAL]` 13/13경기는 모두 720-step `DONE/DONE`이었고 runtime은 PASS였다. 그러나 parent record 16/16에서 zero gate가 FAIL했다.
4. **막힌 점과 다음 행동:** 독립 결과 검증이 남아 있고 zero gate가 실패했으므로 전체 preflight는 PASS가 아니다. 기준을 낮추지 말고 correctness 경로를 결정해야 한다.

VERDICT | **LOCAL FAILURE — 13/13 VALIDLY COMPLETED, INDEPENDENT RESULT VERIFICATION PENDING** | artifact `1c478c24…9721`, manifest `46fd9e5e…4801c` | Identity PASS · Schema FAIL · Runtime PASS · Isolation PASS · License PASS · zero gate FAIL | NEXT ACTION: independent result verification → correctness path decision

## 실행 승인 대조

- Claude 최종 검토: `coordination/reports/claude/20260916-1814-P1B-REVISED-MANIFEST-APPROVAL.md`, reviewed manifest `46fd9e5e…4801c`, parent 623s / episode wall 960s / hard ceiling 1200s 승인.
- Antigravity 최종 검토: `coordination/reports/antigravity/20260916-1812-P1B-RUNTIME-REVIEW.md`, 동일 manifest와 동일 시간 기준 승인.
- 실행 중 manifest bytes는 변경하지 않았다. manifest 내부의 이전 `BLOCKED` 값은 외부 승인 전 freeze 상태이며, 위 두 외부 보고서가 실행 조건 충족 근거다.

## Identity와 clean-room

- tar SHA-256: `1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721`, 실행 전·후 일치.
- engine: `kaggle-environments==1.32.7`; Python source `bc8a5487…653e`, JSON config `a82c89c1…4867`, manifest와 일치.
- runner: `tools/instrument.py` `284dee4c…d0629`; gate contract `3a3e423b…71353c`, 일치.
- 상대: starter engine source와 두 tape SHA 모두 일치.
- clean-room은 실행 전에 존재하지 않았다. 추출 직후 root member는 `LICENSE.txt`, `actions.json`, `main.py`, `yh_base.py` 네 개뿐이고 각 member SHA가 일치했다. import 뒤 생성된 `__pycache__`는 tar member가 아니다.
- clean-room import에서 `main.agent` callable 확인, `__file__` runtime 의존 0건.

자세한 값: `identity.json`.

## 13경기 완료와 exit code

| 그룹 | 예정 | 완료 | 결과 |
|---|---:|---:|---|
| self-play | 3 | 3 | 3개 모두 `DONE/DONE`, exit 2 zero-gate FAIL |
| starter | 6 | 6 | 6개 모두 `DONE/DONE`, exit 2 zero-gate FAIL |
| target stress | 2 | 2 | 2개 모두 `DONE/DONE`, exit 2 zero-gate FAIL |
| control counter stress | 2 | 2 | 2개 모두 `DONE/DONE`, exit 2 zero-gate FAIL |
| 합계 | **13** | **13** | JSON 13개, runner/parse/metric 누락 0 |

각 argv·시작/종료 시각·stdout/stderr·exit code는 `commands.json`, 원자료는 `cells/*.json`에 보존했다. 정상 완료된 FAIL 뒤에도 다음 경기를 계속 실행했다.

## Zero gate

gated parent record는 self-play 양쪽 6개 + 나머지 parent seat 10개 = 16개다. **PASS 0 / FAIL 16**이다.

| counter | 합계 | nonzero record |
|---|---:|---:|
| `noop_actions` | 3,488 | 16/16 |
| `shed_discarded` | 482 | 16/16 |
| `shed_unsold` | 0 | 0/16 |
| `orders_truncated` | 0 | 0/16 |
| `buy_failed` | 74 | 6/16 |
| `hire_failed` | 18 | 2/16 |
| `seed_blocked_plant` | 56 | 6/16 |
| `hands_length_mismatch_count` | 92 | 2/16 |
| `exceptions` | 0 | 0/16 |

`sell_unfilled` 합 1,541,806은 diagnostic이며 gate failure에 넣지 않았다. 모든 record가 `noop_actions`와 `shed_discarded`만으로도 frozen zero gate를 실패하므로 이 diagnostic을 빼도 판정은 바뀌지 않는다.

## Runtime

- parent record `total_s`: 0.078023–0.197821s, 승인 한도 623s 이하 — PASS.
- episode wall: 2.841–4.652s, 승인 한도 960s 이하·hard ceiling 1200s 미만 — PASS.
- first call 최대 33.214ms, p99 최대 0.881ms, 개별 call 최대 91.611ms. 이 세 값은 measure-only이며 별도 gate로 만들지 않았다.
- timing은 `time.perf_counter` elapsed duration이다. process CPU time으로 해석하지 않는다.

자세한 값: `latency.json`과 각 cell JSON.

## 제출 전 체크리스트

```text
Identity:  제출 파일 SHA-256 = 성능을 측정한 파일 SHA-256 인가?      [PASS]
Schema:    루트 main.py / agent(obs) / hands 길이 정렬 / 절대 raise 안 함  [FAIL]
Runtime:   에피소드 예산(§6)의 70~80% 이내인가? p99 턴 지연 기록      [PASS]
Isolation: 빈 폴더 clean-room 에서 tar 풀고 import 성공했는가?        [PASS]
License:   외부 코드·상대 봇·데이터의 라이선스가 Rules 를 만족하는가?   [PASS]
Ledger:    submission ID ↔ artifact SHA ↔ 에피소드를 연결했는가?       [N/A — 제출 전]
```

Schema는 root/import/exception 측면은 통과했지만 target stress의 두 parent record에서 `hands_length_mismatch_count=46`씩 발생했고, release zero gate도 별도로 실패했다.

## 판정 경계

- **파일 불일치:** 0건. Identity PASS.
- **계측 오류:** 0건. 13 JSON 모두 schema 3이며 필수 metric이 있다.
- **성능/correctness 실패:** 13개 cell과 16개 parent record의 frozen zero gate FAIL.
- **Runtime:** PASS.
- **Hosted 우위:** N/A. 이 실행은 `[LOCAL]` release correctness만 측정한다.
- **독립 결과 검증:** PENDING. Antigravity의 기존 보고서는 manifest/runner 사전 검토이며 이번 새 JSON 결과 검증은 아니다. 따라서 전체 preflight PASS를 선언하지 않는다.

## 재현

실행 명령은 `commands.json`에 argv 배열로 저장했다. 공통 형태는 다음과 같다.

```text
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
python3 tools/instrument.py --a <seat-0> --b <seat-1> --seeds <frozen-seed> --steps 720 \
  --time-agent both --gate-agent <a|b|both> --json <cell.json> --require-pass
```

Orchestrator: `python3 experiments/results/p1_release_preflight/run_approved_13.py` — exit 0은 13개 command를 끝까지 dispatch하고 기록했다는 뜻이며, 개별 13개 exit code는 모두 2다.
