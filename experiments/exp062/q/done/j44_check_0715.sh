D=analysis/hosted_0930d/snap_0715; mkdir -p $D
kaggle competitions submissions kaggriculture 2>&1 | head -6 > $D/subs.txt
$PY analysis/hosted_0930d/errcheck.py 56709992 > $D/errcheck_L4pc.log 2>&1
$PY analysis/hosted_0930d/errcheck.py 56709342 > $D/errcheck_d157c.log 2>&1
echo done
