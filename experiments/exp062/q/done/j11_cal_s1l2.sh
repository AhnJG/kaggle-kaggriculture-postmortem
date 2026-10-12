# Claude-B: after j08 (nm) -> evaluator calibration (c26, X vs S1 pool) -> S1L2 on Mac
for i in $(seq 1 240); do [ -f experiments/exp062/q/done/j08_nm.sh ] && break; sleep 30; done
W=7 EXP024_OUT=experiments/exp062/games-s1cal-mac.jsonl $PY experiments/exp062/run62.py experiments/exp062/jobs-s1cal.json
wc -l experiments/exp062/games-s1cal-mac.jsonl
W=7 EXP024_OUT=experiments/exp062/games-s1L2-mac.jsonl $PY experiments/exp062/run62.py experiments/exp062/jobs-s1L2.json
wc -l experiments/exp062/games-s1L2-mac.jsonl
