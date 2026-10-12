#!/bin/bash
# EXP-060 M3-N + READOUT0930 morning pipeline (Claude 2026-09-30 03:00 KST).
# Mac terminal, once:  cd ~/kaggle/Kaggriculture && caffeinate -dimsu bash experiments/exp060_mbr/morning.sh
# Waits until 07:30 local (KST), then: HOSTEDX0930 collect (card 20260930-HOSTEDX0930 steps 1-3) -> NEW panel -> M3-N games on this Mac -> judge.
# No submission, no script edits. Log: experiments/exp060_mbr/morning.log
set -u
cd ~/kaggle/Kaggriculture || exit 1
LOG=experiments/exp060_mbr/morning.log
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
log(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
target=$(date -j -f "%Y-%m-%d %H:%M:%S" "2026-09-30 07:30:00" +%s 2>/dev/null || echo 0)
now=$(date +%s); if [ "$target" -gt "$now" ]; then log "waiting $(( (target-now)/60 )) min until 07:30"; sleep $((target-now)); fi
log "start; python=$PY"
shasum -a 256 analysis/hosted_x0930/*.py >> "$LOG"
for s in step1_2_collect step3_download_replays step4_5_fingerprint; do
  log "run $s"
  $PY analysis/hosted_x0930/$s.py > analysis/hosted_x0930/${s%%_[a-z]*}.log 2>&1 || { log "$s failed once, retry in 120s"; sleep 120; $PY analysis/hosted_x0930/$s.py > analysis/hosted_x0930/${s%%_[a-z]*}.retry.log 2>&1 || { log "$s FAILED twice -> STOP"; exit 2; }; }
done
wc -l analysis/hosted_x0930/opponents.csv | tee -a "$LOG"
log "prep NEW panel"
M3_NOHF=1 M3_NOCLOSED=1 $PY experiments/exp060_mbr/prep_m3.py finalN >> "$LOG" 2>&1 || { log "prep FAILED -> STOP"; exit 3; }
$PY -c "import json;J=json.load(open('experiments/exp060_mbr/jobs-m3-finalN-kaggle.json'))+json.load(open('experiments/exp060_mbr/jobs-m3-finalN-mac.json'));json.dump(J,open('experiments/exp060_mbr/jobs-m3-finalN-all.json','w'));print('jobs',len(J))" | tee -a "$LOG"
log "run M3-N games on Mac"
EXP024_OUT=experiments/exp060_mbr/games-m3-finalN-mac.jsonl $PY experiments/exp024_round2/run.py experiments/exp060_mbr/jobs-m3-finalN-all.json > experiments/exp060_mbr/run-m3-finalN.log 2>&1
wc -l experiments/exp060_mbr/games-m3-finalN-mac.jsonl | tee -a "$LOG"
log "judge"
$PY experiments/exp060_mbr/judge_m3.py final,finalN > experiments/exp060_mbr/judge_m3-final.log 2>&1
log "DONE -> experiments/exp060_mbr/m3_verdict-final+finalN.json (Claude 판정 대기)"
