# EXP-058 Stage C 실행 카드 (antigravity) — RG_{G}{R} × 확인 panel 697경기 (판단 없음)
**기준 상태:** 활성 d157 56607884 / c26 56635330. 카드가 BOARD 보다 최신이면 카드를 따른다.
발행: Claude {TS}. Stage S 선택 규칙 {G}->{R} (verdictS.json). EXP-058S 와 같은 절차. 697경기(Kaggle 419 + Mac 278). 보고 8줄.
입력 sha(앞 12자): experiments/exp058_route/PREREG.md 75a8125e5366, variants/RG_{G}{R}.py {SHA_V}, jobsC-kaggle.json {SHA_K} (419), jobsC-mac.json {SHA_M} (278), make_kaggle2.py 1cff6a2d9dfe.
0. cd ~/kaggle/Kaggriculture; sha 대조. 다르면 STOP.
1. USER=$(kaggle config view | awk '/username/{print $NF}')
2. python experiments/kaggle_pilot/make_kaggle2.py $USER experiments/exp058_route/jobsC-kaggle.json exp058c 5
3. kaggle datasets create -p experiments/kaggle_runs/exp058c/dataset → ready → k=0..4 kaggle kernels push -p experiments/kaggle_runs/exp058c/kernel$k (실패 시 1회 재시도, 또 실패면 그 몫을 Mac 에서; 429 는 5분 간격 3회)
4. 동시에 Mac: caffeinate -dimsu nohup env EXP024_OUT=experiments/exp058_route/gamesC-mac.jsonl python experiments/exp024_round2/run.py experiments/exp058_route/jobsC-mac.json > experiments/exp058_route/runC-mac.log 2>&1 &
5. 단일 대기 → k=0..4 output 합쳐 experiments/exp058_route/gamesC-kaggle.jsonl; wc -l experiments/exp058_route/gamesC-*.jsonl (합계 697)
금지: 스크립트·jobs·variants 수정, 제출, 판정.
보고: coordination/reports/antigravity/<ts>-EXP058C.md — 완료 시각, 행 수, 실패 커널.
