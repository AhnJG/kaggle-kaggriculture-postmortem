# wait for S1 kaggle collection, then launch S1b on kaggle
for i in $(seq 1 180); do [ -f experiments/exp062/games-s1-kaggle.jsonl ] && break; sleep 30; done
bash experiments/exp062/kaggle_launch.sh experiments/exp062/jobs-s1b-kaggle.json exp062s1b && bash experiments/exp062/kaggle_collect.sh exp062s1b experiments/exp062/games-s1b-kaggle.jsonl
