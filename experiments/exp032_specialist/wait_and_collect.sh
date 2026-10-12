#!/bin/bash
USER=$(kaggle config view | awk '/username/{print $NF}')
MAX_CHECKS=12
for ((i=1; i<=MAX_CHECKS; i++)); do
  echo "--- Check $i / $MAX_CHECKS at $(date) ---"
  ALL_DONE=1
  for k in {0..4}; do
    STATUS=$(kaggle kernels status $USER/kaggriculture-exp032-k$k 2>&1)
    echo "k$k: $STATUS"
    if [[ "$STATUS" == *"RUNNING"* ]] || [[ "$STATUS" == *"QUEUED"* ]]; then
      ALL_DONE=0
    fi
  done
  
  if [ $ALL_DONE -eq 1 ]; then
    echo "All kernels completed or errored."
    break
  fi
  
  if [ $i -lt $MAX_CHECKS ]; then
    sleep 600
  fi
done

echo "Downloading outputs..."
for k in {0..4}; do
  mkdir -p experiments/kaggle_runs/exp032/out/k$k
  kaggle kernels output $USER/kaggriculture-exp032-k$k -p experiments/kaggle_runs/exp032/out/k$k
done

echo "Merging games.jsonl..."
cat experiments/kaggle_runs/exp032/out/k*/games-*.jsonl > experiments/exp032_specialist/games.jsonl 2>/dev/null
wc -l experiments/exp032_specialist/games.jsonl

echo "Running judge32.py..."
python3 experiments/exp032_specialist/judge32.py > experiments/exp032_specialist/judge.txt 2>&1
head -3 experiments/exp032_specialist/judge.txt
echo "DONE_ALL"
