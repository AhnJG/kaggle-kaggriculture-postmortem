# usage: bash experiments/exp062/kaggle_launch.sh <jobs.json> <tag>
set -u
J=$1; TAG=$2; U=arki13
$PY experiments/kaggle_pilot/make_kaggle2.py $U $J $TAG 5 || exit 1
kaggle datasets create -p experiments/kaggle_runs/$TAG/dataset || { sleep 30; kaggle datasets create -p experiments/kaggle_runs/$TAG/dataset || exit 2; }
for i in $(seq 1 60); do s=$(kaggle datasets status $U/kaggriculture-$TAG 2>&1); echo "status: $s"; echo "$s" | grep -qi ready && break; sleep 10; done
for k in 0 1 2 3 4; do kaggle kernels push -p experiments/kaggle_runs/$TAG/kernel$k || { sleep 20; kaggle kernels push -p experiments/kaggle_runs/$TAG/kernel$k; }; done
echo launched $(date)
