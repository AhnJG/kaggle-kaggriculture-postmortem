import os
import sys
import time
import json
import subprocess
from pathlib import Path

def main():
    top10_file = Path("private_artifacts/leaderboard/latest_top10.txt")
    if not top10_file.exists():
        print(f"{top10_file} not found.")
        sys.exit(1)
        
    with open(top10_file, "r") as f:
        teams = [line.strip() for line in f if line.strip()]
        
    kernel_dir = Path("/tmp/kaggriculture-episode-extractor")
    kernel_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate extract.py for the kernel
    extract_py = kernel_dir / "extract.py"
    with open(extract_py, "w") as f:
        f.write(f"""import os
import pandas as pd

# The dataset is mounted at /kaggle/input/kaggriculture-episodes-index
# Wait, actually, let's just search for CSVs or JSONs in /kaggle/input
teams = {teams}

def find_episodes():
    import glob
    all_files = glob.glob("/kaggle/input/kaggriculture-episodes-index/**/*.csv", recursive=True)
    
    # We don't know the exact format, so let's try to read them or just output whatever we find.
    # Usually, a dataset with episodes has a main csv, e.g. episodes.csv
    # Or maybe we can just query Meta Kaggle. But the prompt says use this dataset.
    print("Files found:", all_files)
    
    # Let's try to parse all csvs
    results = []
    
    for f in all_files:
        try:
            df = pd.read_csv(f)
            print(f"Read {{f}}, columns: {{df.columns}}")
            # We need to find TeamName, EpisodeId.
            # Typical Meta Kaggle columns: EpisodeId, TeamName, SubmissionId...
            
            # Let's just output head to debug if we are not sure
            if 'TeamName' in df.columns or 'TeamId' in df.columns or 'teamName' in df.columns:
                team_col = [c for c in df.columns if 'Team' in c or 'team' in c][0]
                ep_col = [c for c in df.columns if 'Ep' in c or 'ep' in c][0]
                for team in teams:
                    team_df = df[df[team_col] == team]
                    episodes = team_df[ep_col].unique()[:5]
                    for ep in episodes:
                        results.append({{"TeamName": team, "EpisodeId": ep}})
        except Exception as e:
            print(f"Error reading {{f}}: {{e}}")
            
    out_df = pd.DataFrame(results)
    out_df.to_csv("episodes.csv", index=False)
    print("Saved episodes.csv")

if __name__ == '__main__':
    find_episodes()
""")

    # Generate kernel-metadata.json
    metadata = {
      "id": "<kaggle_user>/kaggriculture-episode-extractor",
      "title": "Kaggriculture Episode Extractor",
      "code_file": "extract.py",
      "language": "python",
      "kernel_type": "script",
      "is_private": "true",
      "enable_gpu": "false",
      "enable_internet": "true",
      "dataset_sources": ["kaggle/kaggriculture-episodes-index"],
      "competition_sources": ["kaggriculture"],
      "kernel_sources": []
    }
    with open(kernel_dir / "kernel-metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    env = os.environ.copy()
    env["HOME"] = str(Path.cwd())
    env["KAGGLE_CONFIG_DIR"] = str(Path.cwd() / ".kaggle")
    
    print("Pushing kernel...")
    res = subprocess.run(["kaggle", "kernels", "push"], cwd=kernel_dir, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        print("Push failed:", res.stderr)
        sys.exit(1)
        
    print(res.stdout)
    
    print("Waiting for kernel to finish...")
    while True:
        time.sleep(10)
        res = subprocess.run(["kaggle", "kernels", "status", "<kaggle_user>/kaggriculture-episode-extractor"], cwd=kernel_dir, env=env, capture_output=True, text=True)
        status = res.stdout.strip()
        print(status)
        if "complete" in status.lower() or "error" in status.lower() or "cancel" in status.lower():
            break
            
    print("Fetching output...")
    subprocess.run(["kaggle", "kernels", "output", "<kaggle_user>/kaggriculture-episode-extractor"], cwd=kernel_dir, env=env)
    
if __name__ == '__main__':
    main()
