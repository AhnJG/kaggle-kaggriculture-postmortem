for i in $(seq 1 90); do
  s=$(kaggle competitions submissions kaggriculture 2>&1 | grep 56709342 | head -1)
  echo "$(date '+%H:%M') $(echo "$s" | grep -oE 'SubmissionStatus\.[A-Z]+ *[0-9.]*')" >> experiments/exp062/valid_watch_d157c.log
  echo "$s" | grep -qE "COMPLETE|ERROR|FAIL" && break
  sleep 120
done
tail -1 experiments/exp062/valid_watch_d157c.log
