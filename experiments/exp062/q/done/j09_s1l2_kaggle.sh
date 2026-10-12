# after S2A kaggle output collected, run S1L2 (L4p,L6p,L3pE,L1pE,L2pE,L3a) on kaggle
for i in $(seq 1 240); do [ -f experiments/exp062/games-s1b-kaggle.jsonl ] && break; sleep 30; done
bash experiments/exp062/kaggle_launch.sh experiments/exp062/jobs-s1L2.json exp062s1l2 && bash experiments/exp062/kaggle_collect.sh exp062s1l2 experiments/exp062/games-s1L2-kaggle.jsonl
