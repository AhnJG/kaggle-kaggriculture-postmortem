# EXP-058 사전등록 (Claude 09-29 15:00 KST, 결과 전) — route 선택 규칙의 그룹 단위 재배정

## 가설
d157 의 router(releases/exp035-d157/main.py:960, sha 94a46c11…)는 step 144 에 첫 두 상점의 **순서 있는 쌍**(64가지)으로 route 를 고르고 step 648 에 route 2 로 바꾼다.
이 표는 과거 상대 집단에 맞춰졌다. 현재 상대 집단에서는 **그룹 단위로** 다른 기존 route 가 더 강할 수 있다.
조합별 최적화는 하지 않는다(현재 상대 tape 에서 조합당 1–10판, 중앙값 4판 — Codex 검토 09-29).

## 그룹 (d157 자신의 실효 route 로 정의, experiments/exp058_route/effective_route_by_pair.json)
- Y: 실효 route 9 (YARN_STORE 포함 15쌍). 현재 상대 tape 69판.
- D: 실효 route 105 (기본값, 21쌍). 80판.
- S: 나머지 28쌍(쌍마다 전용 route). 120판.

## 진단 arm (Stage S 입력)
FR{R}: 모든 쌍을 route R 로 강제(_V92_TABLE 덮어쓰기, 부모 바이트 불변), R ∈ {105, 9, 107, 103, 0}.
현재 상대 tape 269(experiments/exp051_curpop) × 5 = 1,345경기. smoke 10판: 오류 0, 행동 변화 확인.

## 규칙 집합 (13개, 결과 전 고정)
(G, R): G ∈ {Y, D, S}, R ∈ {105, 9, 107, 103, 0}, R ≠ G 의 기본 route(Y=9, D=105).
경기 i 의 합성 Δ_i = FR_R(i) − d157(i) (i ∈ G), 아니면 0.

## Stage S (선택)
전체 Δ 가 가장 큰 규칙 1개를 고른다. 통과 조건:
- 전체 Δ ≥ +0.02
- 그룹 안 Δ 의 상대 단위 bootstrap 95% 하한 > 0
- c26 대비 합성 Δ ≥ 0 (그룹 안 FR_R − c26, 밖 d157 − c26)
13개 중에서 고르므로 Stage S 추정은 위로 편향된다. 결정은 Stage C 가 한다.

## Stage C (확인, 선택된 규칙을 실제 파일 RG 로 구현해 새로 실행)
- exp048 H219 ∪ exp049 F228 에서 d157 대비 Δ > 0, 그리고 두 panel 모두 Δ ≥ −0.02
- closed-loop d157 직접 50판(seed 15000–15024 양 좌석) ≥ 0.5
- family arena d157 대비 ≥ −0.02
- D3 gate
하나라도 불통과면 FAIL → 방침 A(d157 + c26 유지).

## 한계
tape 는 상대 반응을 재현하지 못한다. route 전환 후 농장 상태가 route 가 가정한 상태와 다를 수 있다(행동 변화는 smoke 로만 확인).
결과 후 기준·집합을 바꾸지 않는다(바꾸면 새 번호).

## 시간표
Stage S 09-29 밤 → Stage C 09-30 12:00 → 릴리스·D3 18:00 → 사람 제출 판단 21:00 KST.
