for v in L3p L4p L6p; do echo "== $v"; $PY experiments/exp062/release62.py $v; done
ls -la releases/exp062-*/
