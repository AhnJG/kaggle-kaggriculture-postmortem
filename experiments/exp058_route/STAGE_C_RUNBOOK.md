# EXP-058 Stage C 준비 (Claude 09-29, Stage S 결과 전에 작성)
Stage S 판정 → 통과 시 아래 순서. 불통과면 FAIL 기록 후 방침 A.
1. python3 experiments/exp058_route/judge58S.py            # verdictS.json, SELECTED G->R
2. python3 experiments/exp058_route/build_rg.py G R         # variants/RG_GR.py, manifest 갱신 (d157 sha 94a46c11 확인)
3. python3 experiments/exp058_route/prep58C.py G R          # jobsC-kaggle 419 / jobsC-mac 278 (X148 + fresh 299 + FAM 250)
4. CARD_C_TEMPLATE.md 의 {G}{R}{TS}{SHA_*} 채워 coordination/proposals/claude/<date>-EXP058C-ANTIGRAVITY.md 발행
5. (병행, VM) python3 experiments/exp058_route/release58.py RG_GR → D3: D3_CAND=releases/exp058-RG_GR/main.py D3_CAND_SHA=<sha> D3_RESULT=../../releases/exp058-RG_GR/gate-d3-result.json python3 experiments/d3_gate_v2/measure_gate_v2_claude.py
6. python3 experiments/exp058_route/judge58C.py RG_GR       # verdictC-RG_GR.json, local_pass
7. local_pass 이고 D3 PASS 면 사람에게 제출 판단 요청(제출은 사람만; 제출 시 d157 은퇴). 아니면 FAIL → 방침 A.
Dry run 09-29: build/prep 경로 확인(697 jobs), RG_S105 가 seed 20000–20003(어느 panel 에도 없음)에서 오류 0·동작 확인. 산출물은 _dryrun/ 로 옮김(판정 데이터 아님).
