W=7 EXP024_OUT=experiments/exp062/games-nm5.jsonl $PY experiments/exp062/run62.py experiments/exp062/jobs-nm5.json
W=7 EXP024_OUT=experiments/exp062/games-s5b-mac.jsonl $PY experiments/exp062/run62.py experiments/exp062/jobs-s5b-mac.json
wc -l experiments/exp062/games-nm5.jsonl experiments/exp062/games-s5b-mac.jsonl
