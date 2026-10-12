#!/bin/bash
# EXP-062 queue runner (Claude 2026-09-30). Mac Terminal, once:
#   cd ~/kaggle/Kaggriculture && caffeinate -dimsu bash experiments/exp062/q/runner.sh
# Runs each *.sh that Claude drops into experiments/exp062/q/inbox (in background, own log in q/logs).
# Scope: only this folder's queue. Stop: touch experiments/exp062/q/STOP  (or Ctrl-C)
cd ~/kaggle/Kaggriculture || exit 1
Q=experiments/exp062/q
mkdir -p $Q/inbox $Q/running $Q/done $Q/logs
export PY=python3; [ -x .venv/bin/python ] && export PY=$PWD/.venv/bin/python
export PATH="$PWD/.venv/bin:$PATH"
echo "$(date '+%m-%d %H:%M:%S') runner start pid=$$ py=$PY kaggle=$(command -v kaggle)" | tee -a $Q/runner.log
while [ ! -f $Q/STOP ]; do
  for f in $Q/inbox/*.sh; do
    [ -e "$f" ] || continue
    b=$(basename "$f" .sh)
    mv "$f" "$Q/running/$b.sh" || continue
    echo "$(date '+%m-%d %H:%M:%S') start $b" | tee -a $Q/runner.log
    ( bash "$Q/running/$b.sh" > "$Q/logs/$b.log" 2>&1; rc=$?; echo "exit=$rc" >> "$Q/logs/$b.log"; mv "$Q/running/$b.sh" "$Q/done/$b.sh"; echo "$(date '+%m-%d %H:%M:%S') end $b rc=$rc" | tee -a $Q/runner.log ) &
  done
  date '+%s' > $Q/heartbeat
  sleep 5
done
echo "$(date '+%m-%d %H:%M:%S') runner stop" | tee -a $Q/runner.log
