# usage: bash experiments/exp062/kaggle_collect.sh <tag> <out.jsonl>   (waits until all 5 kernels finish)
set -u
TAG=$1; OUT=$2; U=<kaggle_user>; R=experiments/kaggle_runs/$TAG
for i in $(seq 1 240); do
  done_n=0
  for k in 0 1 2 3 4; do s=$(kaggle kernels status $U/kaggriculture-$TAG-k$k 2>&1); echo "$(date '+%H:%M') k$k $s" >> $R/status.log
    echo "$s" | grep -qiE 'complete|error|cancel' && done_n=$((done_n+1)); done
  [ $done_n -eq 5 ] && break; sleep 60
done
: > $OUT.tmp
for k in 0 1 2 3 4; do mkdir -p $R/out/k$k; kaggle kernels output $U/kaggriculture-$TAG-k$k -p $R/out/k$k > /dev/null 2>&1 || { sleep 20; kaggle kernels output $U/kaggriculture-$TAG-k$k -p $R/out/k$k; }
  cat $R/out/k$k/games-$k.jsonl >> $OUT.tmp 2>/dev/null; done
mv $OUT.tmp $OUT; wc -l $OUT; tail -5 $R/status.log
