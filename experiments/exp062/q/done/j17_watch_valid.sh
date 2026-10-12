# poll new submission status every 2 min until not PENDING/RUNNING (max 6h)
for i in $(seq 1 180); do
  s=$(kaggle competitions submissions kaggriculture 2>&1 | grep 56694892 | head -1)
  echo "$(date '+%H:%M') $s" | cut -c1-40,200-300 >> experiments/exp062/valid_watch.log
  echo "$s" | grep -qE "COMPLETE|ERROR|FAIL" && break
  sleep 120
done
tail -2 experiments/exp062/valid_watch.log
