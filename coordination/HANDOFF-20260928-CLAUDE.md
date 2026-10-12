# Kaggriculture 인계 — 2026-09-28 18:20 KST (Claude → 새 채팅)
저장소: Mac `~/kaggle/Kaggriculture` (클라우드에서는 device bridge `$HOME/mnt/Kaggriculture`). 사람이 제출, antigravity=고정 명령 실행, Codex=판단·연구, Claude=설계·독립 검증.

## 1. 활성 슬롯 (FIFO: 새 제출은 가장 오래된 활성 은퇴)
| 순서 | ID | bot | 점수(09-28 18시) | 파일 |
|---|---|---|---|---|
| 1(오래됨) | 56607884 | **d157** = 55be5d5f + `_S1002_PASSES` 35 | 2345.7 (136경기 0.640) | releases/exp035-d157 (main 94a46c11…, tar 4281ea3c…) |
| 2 | 56635330 | **c26** = d157 + `_CA_MARGIN` −26 | 717 (제출 08:45 UTC) | releases/exp039-c26 (main ff230c83…, tar 8961e03e…) |
- **다음 제출은 d157 을 은퇴시킨다.** d157′ 는 d157·c26 중 나은 쪽을 넘어야 의미.
- 마감: 제출 10-01 08:59 KST(09-30 23:59 UTC). 최종 = 마감 후 ~2주 경기 포함, 활성 bot 끼리 BT 재적합. bronze 경계 약 2290(재확인 필요).

## 2. 사람 결정·규칙
- 메달권 밖이면 위험 감수. d157′ 는 **모든 panel 에서 d157 이상**이어야 제출(사람 09-28 14:05). 공격적 슬롯 허용. 상위 bot 방식 흉내 시도 승인. 팀 단위 holdout 사용.
- v171/v074 재제출 안 함. Kaggle 다운로드는 카드 범위로 승인(상위 팀 경기 포함). Kaggle private notebook 5개 사용 승인.
- 금지: 엔진/RNG 수정, holdout seed 9000–9599, 결과 본 뒤 기준 변경. Mac 은 `caffeinate -dimsu`.

## 3. 핵심 사실
- tape(open-loop, hosted 상대 행동 재생) 평가가 실전과 일치: v074 163/163, d157 136/136 hosted 결과 재현; d157 127 변형 tape 0.75 → 실전 0.857.
- 55be 계열 variant(D·d157·d053·b020)는 tape 에서 결과 100% 동일 — 상수 ±1 은 대칭(mirror) 경기에서만 차이. ±1 탐색(EXP-036) 무효.
- d157 실전: LB<2200 0.85, 2200–2400 0.695, **2400–2600 0.306**(벽). 2400+ 상위 24팀 tape 742: d157 0.416, c26 0.449, v074 0.318. 약한 팀: juliencst 0.20, thisray 0.24, Hikaru 0.27, Shawn404 0.27, Fritz Cremer 0.33.
- 상위 팀 행동: 생산 구성·최종 money 는 d157 과 거의 동일(딸기~32, 밀20, 양~8, 소~7, ~98–100k). 차이는 주문: WHEAT BUY_PRODUCT/SELL 요청 수천(Fritz ~2.8k/3.0k, ctree 6.7k/8.3k) vs d157 330/572, 4분기 SELL 요청 3–6배. **요청 수량 기준, 체결 미분석**(replay private 에 shed 있음 → 복원 가능).
- field: 공개 상위가 55be Step1009 계열로 수렴(55be5d5f, 63dde9e4=HL63, 836cbfb6=M2965, 03165654=FJ1010 도 Step1009 위). d157 이 그중 family arena 최강(FS 0.727).
- 55be 계열 runtime: 순차 0.25s, D3 1-worker max ~0.5s; Kaggle 4병렬 1.6s 는 contention.

## 4. 진행 중
- **Codex TOP2400** (`coordination/proposals/claude/20260928-TOP2400-CODEX.md`): 체결 복원 → 메커니즘 → 가설 ≤5(흉내 포함) → d157′ 구현·사전등록·Kaggle jobs. 1차 09-29 06:00, 최종 15:00. 결과 오면 Claude 가 독립 검증 + Kaggle 실행(make_kaggle2).
- **EXP-043** (antigravity, `20260928-EXP043-ANTIGRAVITY.md`): 약한 5팀 d157 패배 tape 130 × 기존 bot 30(guard 23 + D, HL63, M2965, FJ1010, O127, DP0924, V171) oracle. 결과: `experiments/exp041_top2400/games43-*.jsonl` → 어느 bot 이 이 팀들을 이기는지 표를 만들어 Codex 에 전달.
- c26 hosted 관찰: 09-29 오전 EXP-037 파이프라인 복사로 수집(analysis/d157_hosted_20260928 스크립트, 대상 ID 만 교체).

## 5. 도구·데이터 위치
- 경기 실행: `experiments/exp024_round2/run.py`(job=[vid,path,opp_id,opp_path,seed,seat], EXP024_OUT, WORKERS=5). Kaggle 분산: `experiments/kaggle_pilot/make_kaggle2.py <user> <jobs> <tag> 5`(bundle.tgz, private). D3: 클라우드 `/home/claude/d3root/experiments/d3_gate_v2/measure_gate_v2.py`(D3_CAND/D3_CAND_SHA/D3_RESULT), 릴리스 = USTAR tar(main.py 1개, mtime 0) + NOTICE + SHA256SUMS.
- tape: `experiments/exp033_tapes/`(350, v074/v171 시기), `experiments/exp039_camargin/tapes/U*`(d157 실전 136), `experiments/exp041_top2400/tapes/X*`(상위 팀 743; meta.json our_seat; team-split.json holdout 5팀: dodoshark, weense, Phi, Claudex - An, Bohann Wang).
- hosted 수집: `analysis/{v074_hosted_20260927,d157_hosted_20260928,top2400_20260928}/`(step1_2_collect/step3_download/step4_5_fingerprint, opponents.csv).
- 판정 스크립트 예: judge38(family arena), judge39(d157′ 전 panel), prep42(2400+ panel).
## 6. 닫힌 경로
±1 knife-edge(EXP-023/024/026/029/036), layer bypass(030), H1, v074 late closure(LATE), 관측 front-run(ALTMECH, `_r37_quote_priority` 로 이미 구현), marketshock/12ad317e(no-op), HYPGEN2(양털 순서 후보 gate 실패), family arena 선택(038: d157 최강).
## 7. 운영 규칙
antigravity 카드는 sha·STOP·단일 대기·짧은 보고. Codex 는 판단 작업만, 근거(파일:줄) 요구, 결과 전 기준 고정. antigravity 산출물은 Claude 가 표본 독립 검증.
