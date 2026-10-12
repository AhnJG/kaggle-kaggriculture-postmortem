# coordination — 에이전트 간 조율

**파일이 곧 채널이다.** 별도의 메시지 버스를 쓰지 않는다.

## 왜 메시지 버스를 안 쓰는가
초기 설계는 `buzz.py` 라는 파일 기반 메시지 버스였고, 그 이름은
[block/buzz](https://github.com/block/buzz)(Nostr 기반 협업 플랫폼)에서 따왔다.
그런데 실제로 굴려보니 **한 건도 쓰지 않았다.** 세 에이전트가 같은 로컬 폴더를 공유하는 구조에서는
"에이전트별 소유 디렉터리 + 몇 개의 append-only 문서"만으로 충분했고,
버스가 해결하려던 동시 append 충돌은 **디렉터리를 에이전트별로 나눈 시점에 구조적으로 사라졌다.**

그래서 `coordination/buzz/` 를 폐지하고 실제로 쓰는 것만 남긴다.
(진짜 buzz 도입은 대회 종료 후 검토. 23일 안에 릴레이를 세우는 비용이 이득보다 크다.)

## 구조

| 경로 | 무엇 | writer |
|---|---|---|
| `BOARD.md` | **지금 무엇이 중요한가.** 매일 갱신 | 코디네이터만 |
| `TASKS.md` | 작업 원장 (append-only) | 전원 (자기 행만) |
| `HANDOFF_CURRENT.md` | 최신 인계 1건 | 직전 작업자 |
| `proposals/<agent>/` | **소유 경로 밖**을 바꾸자는 제안 | 해당 agent |
| `reports/<agent>/` | 완료 보고. 한 건 한 파일 | 해당 agent |
| `SUBMIT_*.md` | 제출 실행 절차 (사람 전용) | 코디네이터 |

## 규칙
- 공유 파일에 **동시 append 금지.** 보고는 `reports/<나>/` 에 새 파일로 만든다
- 파일명 `YYYYMMDD-HHMM-<task_id>.md` (예: `20260907-1400-KAGRI-006.md`)
- 보고 형식은 `AGENTS.md` §10 핸드오프:
  `VERDICT | 핵심 사실 2개 | exact path + SHA-256 | 실행한 검증과 결과 | NEXT ACTION`
- 소유 경로 밖을 바꾸고 싶으면 직접 고치지 말고 `proposals/<나>/` 에 제안을 낸다
