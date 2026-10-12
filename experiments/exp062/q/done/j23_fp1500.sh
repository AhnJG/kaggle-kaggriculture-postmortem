for i in $(seq 1 60); do [ -f experiments/exp062/q/done/j215_collect_1500.sh ] && break; sleep 20; done
$PY analysis/hosted_0930d/step4_5_fingerprint.py > analysis/hosted_0930d/snap_1500/step4_5.log 2>&1
cp analysis/hosted_0930d/opponents.csv analysis/hosted_0930d/summary.json analysis/hosted_0930d/snap_1500/
wc -l analysis/hosted_0930d/snap_1500/opponents.csv
