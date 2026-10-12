import json,sys,os
sys.path.insert(0,'experiments/exp026_nearclone')
from common26 import run
if __name__=='__main__':
    run([tuple(j) for j in json.load(open('experiments/exp027_stage3/jobs-n.json'))],'experiments/exp027_stage3/games-n.jsonl',int(os.environ.get('W','5')))
