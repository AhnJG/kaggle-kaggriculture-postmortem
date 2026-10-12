# C2 version (Claude-B 18:58 KST). usage: bash experiments/exp062/submit62c.sh <variant>   (Claude-B 11:05 KST)
# checks: release sha == manifest, tar roundtrip, cloud D3 PASS for same sha, SUBMIT_OK flag, active subs unchanged -> submit -> list
set -eu
: "${PY:?PY must be set}"
V=$1; R=releases/exp062-$V
S=$(shasum -a 256 $R/main.py | cut -d' ' -f1)
M=$($PY -c "import json,glob;m={};[m.update(json.load(open(f))) for f in glob.glob('experiments/exp062/variants/manifest_*.json')];print(m['$V']['sha256'])")
[ "$S" = "$M" ] || { echo "sha mismatch $S vs $M"; exit 2; }
$PY - <<PYX
import tarfile
t=tarfile.open('$R/submission.tar.gz'); assert t.getnames()==['main.py']; assert t.extractfile('main.py').read()==open('$R/main.py','rb').read(); print('tar ok')
import json; d=json.load(open('$R/gate-d3-result-cloud.json')); assert d['cand_sha']=='$S' and d['gate']['verdict']=='PASS'; print('D3', d['gate']['verdict'], round(d['gate']['max_step_incl_step0'],3))
PYX
[ -f experiments/exp062/SUBMIT_OK_$V ] || { echo "no SUBMIT_OK_$V flag -> stop"; exit 4; }
kaggle competitions submissions kaggriculture 2>&1 | head -5 > experiments/exp062/subs_before_c.txt; cat experiments/exp062/subs_before_c.txt
R1=$(sed -n 3p experiments/exp062/subs_before_c.txt | awk '{print $1}'); R2=$(sed -n 4p experiments/exp062/subs_before_c.txt | awk '{print $1}')
[ "$R1" = "56694892" ] && [ "$R2" = "56675458" ] || { echo "unexpected submissions state ($R1,$R2) -> stop"; exit 5; }
kaggle competitions submit kaggriculture -f $R/submission.tar.gz -m "EXP-062 $V: d157 + glut lead K=5 (sell tape-planned MILK/WOOL/STRAWBERRY lots up to 5 steps early when price<=base, steps 192-695); retires d157r 56675458; active {L4p, $V}"
sleep 30; kaggle competitions submissions kaggriculture 2>&1 | head -6 | tee experiments/exp062/subs_after_c.txt
