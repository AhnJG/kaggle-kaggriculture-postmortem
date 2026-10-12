# EXP-017 — "One More Wheat"(step 53 봇)에 EXP-016 과 같은 판매 앞당김 층 이식

hypothesis_id: HYP-0036
test_id: TEST-OMW-ADV-20260922

사전등록 2026-09-22 (Claude). **실행 전 문서.** seed·상대·임계 변경 금지.
근거: C1 hosted 50패 중 30패가 step 53 봇(20260922-1716-C1-HOSTED-MAP). 식별 = dmitriigluzdov "One More Wheat" 18/34, "More Wheat Smarter Sales"·"7 Turn Rescue" 16/34 (20260922-1737-STEP53-ID). 로컬: OMW vs C1 40/0 (평균 margin +28), OMW vs EXP-016 10/30.
OMW = C1 + 50줄(밀 임시 작물을 하루 더 키움, `_CL_*` 래퍼). 판매 앞당김 층 없음 (`_ADV_LOOK` 0회).

```yaml
id:          EXP-017
parent:      releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py  # 10f58185b916392ca39697c83f67f455df81a74dfb6eb1aacd60fd81d50c9970 (CRLF 원본)
             # 주의: 같은 폴더 submission.tar.gz 의 main.py 는 본문이 두 번 들어간 불량(13276줄, b497a0ec…) — 사용 금지
candidate:   releases/f0-omw-adv-exp017/main.py   # 56941da238ccdc8f5286bf7e3191b6208ee3451306e06b74bb2660134a69fc33
             # tar 177eedc05b428b4131c14ec214fbdd050e7bf160711ba3f0a9300598ea08d385 (main.py 한 줄)
one_change:  parent 바이트 끝에 releases/public-ozer-v53-exact/main.py:3532-3629 그대로 (EXP-016 과 같은 블록)
seeds:       2140-2179 (새 seed), 양 좌석 = 80경기씩
blocks:
  A_parent:  candidate vs parent (OMW)
  B_ours:    candidate vs releases/f0-c1-adv-exp016/main.py (hosted 56458814)
  panel (각각 candidate 와 대조 EXP-016 을 같은 seed 로):
    - releases/public-nathanjacob-pipe16-exact/main.py (C1)
    - releases/public-thomastschinkel-metav4-v13-exact/main.py (C2)
    - releases/public-ozer-v53-exact/main.py (C4)
    - releases/public-dmitriigluzdov-kaggriculture-more-wheat-smarter-sales-exact/main.py
    - releases/public-dmitriigluzdov-kaggriculture-7-turn-rescue-historical-lb-2800-exact/main.py
    - parent (OMW) — EXP-016 대조만 추가 (candidate 쪽은 A_parent)
success (모두):
  - A_parent seed 순승 >= +10
  - B_ours seed 순승 >= 0
  - panel 합산 candidate 패배 <= EXP-016 패배, 어느 상대도 +2 초과 증가 없음
  - 예외 0, 최대 step 시간 < 0.5s
failure: A_parent 순승 <= 0 이거나 B_ours 순승 <= -6
inconclusive: 그 밖
```
실행 Antigravity, 판단 Claude, 제출 사람. 통과 시 제출하면 FIFO 로 C1 이 빠진다 → EXP-016 hosted 24h 판독 후에 제출.

## 결과 (2026-09-23, Antigravity 실행 · Claude 판정) — **SUCCESS**
보고: coordination/reports/antigravity/20260923-1725-EXP017-RUN.md
- A_parent (vs OMW): 59/0/21, seed 순승 +38 (기준 +10) ✔
- B_ours (vs EXP-016): 78/0/2, 순승 +76 (기준 0) ✔
- 패널 합산 패배 147 (EXP-016 155), 어느 상대도 +2 초과 증가 없음 ✔ / 예외 0 ✔
- 부모 tar 불량은 재생성해 tar 안 main.py sha = 10f58185… 확인.
판정: 제출 후보. hosted 2425.7(EXP-016) > 2206.6(C1) 이므로 C1 은퇴 제출로 진행 권고.
