import os
import sys
import json
import time
import subprocess
from pathlib import Path
import csv

def run_cmd(cmd):
    env = os.environ.copy()
    env["HOME"] = str(Path.cwd())
    env["KAGGLE_CONFIG_DIR"] = str(Path.cwd() / ".kaggle")
    res = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
    return res

def main():
    top10_file = Path("private_artifacts/leaderboard/latest_top10.txt")
    if not top10_file.exists():
        print(f"{top10_file} not found.")
        sys.exit(1)
        
    with open(top10_file, "r") as f:
        teams = [line.strip() for line in f if line.strip()]
        
    # Find TeamIds from the latest leaderboard CSV
    lb_csvs = list(Path.cwd().glob("kaggriculture-publicleaderboard*.csv"))
    if not lb_csvs:
        print("No leaderboard CSV found.")
        sys.exit(1)
    lb_csv = max(lb_csvs, key=os.path.getctime)
    
    team_ids = {}
    with open(lb_csv, "r", encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['TeamName'] in teams:
                team_ids[row['TeamName']] = row['TeamId']
                
    episodes = []
    
    for team in teams:
        team_id = team_ids.get(team)
        if not team_id:
            print(f"Team {team} not found in leaderboard CSV.")
            continue
            
        print(f"Fetching submissions for {team} ({team_id})...")
        res = run_cmd(f"kaggle competitions team-submissions {team_id} --csv")
        if res.returncode != 0:
            continue
            
        lines = res.stdout.strip().split('\n')
        if len(lines) < 2:
            continue
            
        # Get the latest submission
        reader = csv.DictReader(lines)
        subs = list(reader)
        if not subs:
            continue
        latest_sub = subs[0]['id']
        
        print(f"Fetching episodes for submission {latest_sub}...")
        res = run_cmd(f"kaggle competitions episodes {latest_sub} --csv")
        if res.returncode != 0:
            continue
            
        lines = res.stdout.strip().split('\n')
        if len(lines) < 2:
            continue
            
        reader = csv.DictReader(lines)
        eps = list(reader)
        # Filter completed public episodes
        valid_eps = [e for e in eps if e.get('type') == 'EpisodeType.EPISODE_TYPE_PUBLIC' and e.get('state') == 'EpisodeState.COMPLETED']
        
        # Take up to 5
        for e in valid_eps[:5]:
            episodes.append({"TeamName": team, "EpisodeId": e['id']})
            
    # Save episodes.csv
    ep_df_path = Path("private_artifacts/leaderboard/episodes.csv")
    with open(ep_df_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["TeamName", "EpisodeId"])
        writer.writeheader()
        writer.writerows(episodes)
        
    print(f"Found {len(episodes)} episodes to download.")
    
    # Download replays
    replays_dir = Path("private_artifacts/replays/top")
    replays_dir.mkdir(parents=True, exist_ok=True)
    tapes_dir = Path("private_artifacts/tapes")
    tapes_dir.mkdir(parents=True, exist_ok=True)
    
    for ep in episodes:
        team = ep['TeamName']
        ep_id = ep['EpisodeId']
        out_path = replays_dir / f"{ep_id}.json"
        
        if not out_path.exists():
            print(f"Downloading {ep_id} for {team}...")
            run_cmd(f"kaggle competitions replay {ep_id} -p {replays_dir}")
            time.sleep(2)  # Respect rate limit
            
        # Rename or locate the downloaded file which might be {ep_id}.json or episode-{ep_id}-replay.json
        dl_path = replays_dir / f"{ep_id}.json"
        if not dl_path.exists():
            cand = replays_dir / f"episode-{ep_id}-replay.json"
            if cand.exists():
                dl_path = cand
        if dl_path.exists():
            # Process to tape
            tape_path = tapes_dir / f"{team}_{ep_id}.json"
            if not tape_path.exists():
                with open(dl_path, "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        continue
                
                # Extract actions
                # Assuming data structure matches kaggriculture replay
                steps = data.get('steps', [])
                if not steps:
                    continue
                    
                # Find agent index for this team? We don't have team names in replay directly easily.
                # Actually, the replay just has agent 0 and agent 1.
                # We can save both or try to figure out which one is the team.
                # Let's save the whole steps' actions.
                actions = []
                for step in steps:
                    step_actions = []
                    for p in step:
                        if 'action' in p:
                            step_actions.append(p['action'])
                    actions.append(step_actions)
                    
                with open(tape_path, "w") as f:
                    json.dump(actions, f)
                    
    print("Done downloading and processing tapes.")

if __name__ == '__main__':
    main()
