"""Copy already-downloaded replays into this collection's raw dir so step3 only fetches new episodes."""
import os,glob,shutil,json
RAW="private_artifacts/hosted_20260930/raw";os.makedirs(RAW,exist_ok=True)
E=json.load(open("analysis/hosted_20260930/episodes_all.json"));have={}
for d in glob.glob("private_artifacts/*/raw"):
    if d==RAW:continue
    for f in os.listdir(d):have.setdefault(f,d)
n=0
for e in E:
    fn=f"{e['id']}.json.gz"
    if fn in have and not os.path.exists(os.path.join(RAW,fn)):shutil.copy(os.path.join(have[fn],fn),os.path.join(RAW,fn));n+=1
print("episodes",len(E),"copied",n,"to fetch",sum(1 for e in E if not os.path.exists(os.path.join(RAW,f"{e['id']}.json.gz"))))
