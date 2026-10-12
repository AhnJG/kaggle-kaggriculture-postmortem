# usage: bash experiments/exp062/submit62.sh <variant>   (release -> D3 on Mac -> kaggle submit -> list)
set -eu
V=$1; R=releases/exp062-$V
$PY experiments/exp062/release62.py $V
S=$(shasum -a 256 $R/main.py | cut -d' ' -f1)
D3_CAND=$R/main.py D3_CAND_SHA=$S D3_RESULT=../../$R/gate-d3-result.json $PY experiments/d3_gate_v2/measure_gate_v2_claude.py > $R/gate-d3.log 2>&1 || true
V3=$($PY -c "import json;print(json.load(open('$R/gate-d3-result.json'))['gate']['verdict'])")
echo "D3 verdict $V3"; grep -E '"max_step_incl_step0"|"max_total_per_game"|"errors_or_invalid"' $R/gate-d3-result.json
[ "$V3" = "PASS" ] || { echo "D3 FAIL -> no submit"; exit 3; }
[ -f experiments/exp062/SUBMIT_OK_$V ] || { echo "no SUBMIT_OK_$V flag -> stop before submit"; exit 4; }
kaggle competitions submit kaggriculture -f $R/submission.tar.gz -m "EXP-062 $V: d157 + glut lead (sell tape-planned MILK/WOOL/STRAWBERRY lots early when price<=base); retires X 56675447"
sleep 20; kaggle competitions submissions kaggriculture 2>&1 | head -6
