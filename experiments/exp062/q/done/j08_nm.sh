# wait for j05 (L screen + S1L2) to finish, then non-mirror open-loop panel
for i in $(seq 1 240); do [ -f experiments/exp062/q/done/j05_mac_L_first.sh ] && break; sleep 30; done
W=7 EXP024_OUT=experiments/exp062/games-nm.jsonl $PY experiments/exp062/run62.py experiments/exp062/jobs-nm.json
wc -l experiments/exp062/games-nm.jsonl
