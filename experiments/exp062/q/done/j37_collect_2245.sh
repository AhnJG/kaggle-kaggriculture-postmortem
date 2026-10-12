mkdir -p analysis/hosted_0930d/snap_2245
$PY analysis/hosted_0930d/step1_2_collect.py > analysis/hosted_0930d/snap_2245/step1_2.log 2>&1
cp analysis/hosted_0930d/episodes_all.json analysis/hosted_0930d/as_of.txt analysis/hosted_0930d/snap_2245/
$PY analysis/hosted_0930d/errcheck.py 56705818 > analysis/hosted_0930d/snap_2245/errcheck_L5p.log 2>&1
kaggle competitions submissions kaggriculture 2>&1 | head -6 > analysis/hosted_0930d/snap_2245/subs.txt
echo done
