# fresh hosted collection (X, d157r) + leaderboard -> analysis/hosted_0930c
set -e
for s in step1_2_collect step3_download_replays step4_5_fingerprint; do
  echo "== $s $(date)"; $PY analysis/hosted_0930c/$s.py > analysis/hosted_0930c/$s.log 2>&1 || { echo "$s failed, retry 120s"; sleep 120; $PY analysis/hosted_0930c/$s.py > analysis/hosted_0930c/$s.retry.log 2>&1; }
done
wc -l analysis/hosted_0930c/opponents.csv
