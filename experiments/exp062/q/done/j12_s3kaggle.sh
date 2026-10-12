# Claude-B: replace j09 (S1L2 now on Mac via j11). After S2A kaggle collected -> launch S3 (unseen opponents) on kaggle.
pkill -f "j09_s1l2_kaggle.sh"; sleep 1
for i in $(seq 1 240); do [ -f experiments/exp062/games-s1b-kaggle.jsonl ] && break; sleep 30; done
bash experiments/exp062/kaggle_launch.sh experiments/exp062/jobs-s3k.json exp062s3 && bash experiments/exp062/kaggle_collect.sh exp062s3 experiments/exp062/games-s3-kaggle.jsonl
