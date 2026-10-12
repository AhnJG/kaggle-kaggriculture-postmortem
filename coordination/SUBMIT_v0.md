# v0 제출 실행 절차 (사람 전용)

`AGENTS.md` §8: **제출은 사람 승인 없이 실행하지 않는다.** 자격증명도 맥에만 있다.
맥 터미널에서 아래를 순서대로 실행한다.

## 0. (선택) git 잠금 정리
```bash
rm -f ~/kaggle/Kaggriculture/.git/*.lock ~/kaggle/Kaggriculture/.git/objects/*/tmp_obj_*
cd ~/kaggle/Kaggriculture && git add -A && git commit -m "S12~S14: v0 릴리스 빌드 + clean-room 검증"
```

## 1. 제출 (S15)
```bash
cd ~/kaggle/Kaggriculture
shasum -a 256 releases/v0/submission.tar.gz
#   -> aed79ff3cf0c38f94ae4c958f4798fc2aef5ea568ce285f40fb6c4e752985844 인지 확인

kaggle competitions submit kaggriculture \
  -f releases/v0/submission.tar.gz \
  -m "v0 pipeline validation (commit 4ed2d29)"
```

**왜 단일 `main.py` 가 아니라 tar.gz 인가**: 내용물은 `main.py` 하나로 동일하다.
v1 이후에는 다중 파일 tar.gz 가 필요하므로, **버려도 되는 v0 슬롯에서 그 경로를 먼저 검증**한다.
tar.gz 가 `Error` 로 뜨면 즉시 단일 파일로 재제출:
```bash
kaggle competitions submit kaggriculture -f main.py -m "v0 single-file fallback"
```

## 2. validation 확인 (S16)
```bash
kaggle competitions submissions kaggriculture
```
- 상태가 `Error` 가 아니어야 한다 (검증 에피소드는 **자기 자신과의 대전**이다)
- `Error` 면: `kaggle competitions logs <EPISODE_ID> 0`
- **submission ID 를 기록**할 것

## 3. 리플레이 경로 개통 (S17) — 이게 v0 의 진짜 목적이다
제출 후 1~2시간 뒤(에피소드가 몇 판 돌고 나서):
```bash
kaggle competitions episodes <SUBMISSION_ID>
kaggle competitions replay <EPISODE_ID> -p private_artifacts/replays
kaggle competitions logs <EPISODE_ID> 0 -p private_artifacts/logs
```
리플레이가 로컬에 떨어지면 **테이프 파이프라인의 입력이 확보된다.**

## 4. 원장 기록
`evidence/HOSTED_LEDGER.md` 제출 원장 표에 한 줄 추가:

| # | 제출일 | 라벨 | artifact SHA-256 | submission ID | 엔진 | validation | 활성 | 은퇴시킨 것 |
|---|---|---|---|---|---|---|---|---|
| v0 | 2026-09-__ | v0 pipeline validation | aed79ff3…5844 | (기입) | 1.32.7 | (기입) | 1/2 | 없음 |

## 슬롯 회계
현재 활성 0/2 → 제출 후 1/2. 은퇴시키는 에이전트 없음.
**대회 전체 제출 예산 5회 중 1회 사용.**
