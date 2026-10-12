# EXP-035 사전등록 — d157 exact, 교정된 runtime 측정으로 재판정 (Claude, 2026-09-27 20:03 KST (11:03 UTC))
작성 시점: EXP-034(rt.jsonl)·EXP-033 완결 결과 **미확인** 상태(이 파일 sha 를 보고서에 기록). 사람 승인 전에는 실행·제출하지 않는다.
## 왜 새 card 인가 (EXP-032 FAIL 을 뒤집는 것이 아님)
- EXP-032 FAIL 사유는 runtime 하나(Kaggle 4 병렬 max 1.63s). 같은 hardware 에서 v074 0.29s. Codex REVIEW-0927C 의 Mac 1-worker profile 은 d157 max 0.233s·total 3.48s·overage 0. 즉 4 병렬 contention 측정이 hosted(1 agent, vCPU 1.6)를 대표하는지가 불확실하다 → **측정 설계 교정**. EXP-032 의 성능 항목 결과는 이미 관측했으므로 여기서는 기준을 바꾸지 않고 그대로 인용한다(관측 후 인용임을 명시).
## 대상
d157 = `experiments/exp029_dpnew_mirror/variants/d157.py` sha 94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e (55be5d5f + `_S1002_PASSES` 34→35). bytes 변경 없음.
## 판정 (모두 충족 시 PASS)
1. 성능(EXP-032, 관측 완료·기준 불변): invalid 0; transition lower95 > 0 (관측 +0.141); legacy point ≥ −0.10 (+0.026); hosted_vs_P ≥ −0.10 (−0.075).
2. runtime-A (EXP-034, Kaggle 1 kernel 순차, d157 6경기): 전 경기 DONE/DONE, overage == 0, max < 1.0s, agent total < 60s.
3. runtime-B (release D3 gate v2, Mac 1 worker 15경기, 다른 작업 없음): max < 0.8s, 게임당 total < 30s, 예외 0.
4. tape(EXP-033 완결, open-loop): 127 변형 tape 에서 (d157 − P) point ≥ +0.10, 전체 350 tape 에서 (d157 − P) point ≥ 0. (open-loop 낙관 편향 때문에 보조 조건으로만 사용)
하나라도 실패 → FAIL, 기준 변경 없음. runtime-A 실패 시 Codex 경로 1(결과 보존 cache)을 별도 card 로.
## PASS 시 행동 (사람 승인 필요)
d157 release(clean USTAR, NOTICE, SHA256SUMS) 제출 → FIFO 상 v171(56567563) 은퇴, v074(56577440) 유지. 09-27 이후 “A 고정” 운영 정책의 예외이므로 사람이 명시 승인해야 한다.
