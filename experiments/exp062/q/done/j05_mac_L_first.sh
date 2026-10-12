# reprioritize Mac: stop S1 mac run, run L-family screen first (W=7), then resume S1 mac (run62 skips done keys)
pkill -f "run62.py experiments/exp062/jobs-s1-mac.json"; sleep 3
W=7 EXP024_OUT=experiments/exp062/games-s1L-mac.jsonl $PY experiments/exp062/run62.py experiments/exp062/jobs-s1L-mac.json
wc -l experiments/exp062/games-s1L-mac.jsonl
W=7 EXP024_OUT=experiments/exp062/games-s1-mac.jsonl $PY experiments/exp062/run62.py experiments/exp062/jobs-s1-mac.json
wc -l experiments/exp062/games-s1-mac.jsonl
