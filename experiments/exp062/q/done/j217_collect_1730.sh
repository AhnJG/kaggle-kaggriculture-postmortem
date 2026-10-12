# real confirmation collection at 1730 KST (L4p 56694892 + d157r 56675458)
target=$(date -j -f "%Y-%m-%d %H%M" "2026-09-30 1730" +%s); now=$(date +%s); [ $target -gt $now ] && sleep $((target-now))
mkdir -p analysis/hosted_0930d/snap_1730
$PY analysis/hosted_0930d/step1_2_collect.py > analysis/hosted_0930d/snap_1730/step1_2.log 2>&1 || { sleep 120; $PY analysis/hosted_0930d/step1_2_collect.py > analysis/hosted_0930d/snap_1730/step1_2.retry.log 2>&1; }
cp analysis/hosted_0930d/episodes_all.json analysis/hosted_0930d/as_of.txt analysis/hosted_0930d/snap_1730/ 2>/dev/null
$PY analysis/hosted_0930d/errcheck.py 56694892 > analysis/hosted_0930d/snap_1730/errcheck.log 2>&1
$PY analysis/hosted_0930d/step3_download_replays.py > analysis/hosted_0930d/snap_1730/step3.log 2>&1
kaggle competitions submissions kaggriculture 2>&1 | head -5 > analysis/hosted_0930d/snap_1730/subs.txt
echo done $(date)
