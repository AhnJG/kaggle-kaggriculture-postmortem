D=analysis/hosted_0930d/snap_0545; mkdir -p $D
kaggle competitions submissions kaggriculture 2>&1 | head -6 > $D/subs.txt
$PY analysis/hosted_0930d/errcheck.py 56709992 > $D/errcheck_L4pc.log 2>&1
$PY analysis/hosted_0930d/errcheck.py 56709342 > $D/errcheck_d157c.log 2>&1
$PY analysis/hosted_0930d/step1_2_collect.py > $D/step1_2.log 2>&1
cp analysis/hosted_0930d/episodes_all.json analysis/hosted_0930d/as_of.txt $D/
echo done
