# Claude-B 23:00 KST — final combo A submitter (generic). usage:
#   bash experiments/exp062/submit62d.sh <release_dir> <expected_sha> <gate_json> <expect_R1|NEW:tag> <expect_R2> "<message>"
# checks: main.py sha == expected, tar roundtrip, D3 gate PASS for same sha, current top-2 submissions match expectation
#   (NEW:tag = top row must contain tag and be COMPLETE) -> submit -> list
set -eu
: "${PY:?PY must be set}"
RD=$1; ES=$2; GJ=$3; E1=$4; E2=$5; MSG=$6
S=$(shasum -a 256 $RD/main.py | cut -d' ' -f1)
[ "$S" = "$ES" ] || { echo "sha mismatch $S vs $ES"; exit 2; }
$PY - <<PYX
import tarfile,json
t=tarfile.open('$RD/submission.tar.gz'); assert t.getnames()==['main.py']; assert t.extractfile('main.py').read()==open('$RD/main.py','rb').read(); print('tar ok')
d=json.load(open('$GJ')); assert d['cand_sha']=='$S' and d['gate']['verdict']=='PASS'; print('D3', d['gate']['verdict'], round(d['gate']['max_step_incl_step0'],3))
PYX
kaggle competitions submissions kaggriculture 2>&1 | head -5 > experiments/exp062/subs_before_d.txt; cat experiments/exp062/subs_before_d.txt
L3=$(sed -n 3p experiments/exp062/subs_before_d.txt); R1=$(echo "$L3" | awk '{print $1}'); R2=$(sed -n 4p experiments/exp062/subs_before_d.txt | awk '{print $1}')
case "$E1" in
  NEW:*) T=${E1#NEW:}; echo "$L3" | grep -q "$T" && echo "$L3" | grep -q "COMPLETE" || { echo "top row not COMPLETE '$T' -> stop"; exit 5; } ;;
  *) [ "$R1" = "$E1" ] || { echo "unexpected R1 $R1 (want $E1) -> stop"; exit 5; } ;;
esac
[ "$R2" = "$E2" ] || { echo "unexpected R2 $R2 (want $E2) -> stop"; exit 5; }
kaggle competitions submit kaggriculture -f $RD/submission.tar.gz -m "$MSG"
sleep 30; kaggle competitions submissions kaggriculture 2>&1 | head -6 | tee experiments/exp062/subs_after_d.txt
