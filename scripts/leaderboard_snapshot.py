import os
import sys
import zipfile
import csv
import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

# Must be set before importing kaggle
kaggle_dir = Path.cwd() / '.kaggle'
if not kaggle_dir.exists():
    kaggle_dir.mkdir(parents=True, exist_ok=True)
    kaggle_json = Path.cwd() / 'kaggle.json'
    if kaggle_json.exists():
        import shutil
        shutil.copy(kaggle_json, kaggle_dir / 'kaggle.json')
        (kaggle_dir / 'kaggle.json').chmod(0o600)

os.environ['KAGGLE_CONFIG_DIR'] = str(kaggle_dir)
os.environ['HOME'] = str(Path.cwd())

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
except ImportError:
    print("Kaggle package not found. Please install it.")
    sys.exit(1)

def main():
    api = KaggleApi()
    api.authenticate()
    
    with TemporaryDirectory() as tmpdir:
        api.competition_leaderboard_download('kaggriculture', tmpdir)
        zip_path = next(Path(tmpdir).glob('*.zip'))
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            csv_name = next(n for n in zip_ref.namelist() if n.endswith('.csv'))
            with zip_ref.open(csv_name) as f:
                import io
                text_f = io.TextIOWrapper(f, encoding='utf-8-sig')
                reader = csv.DictReader(text_f)
                rows = list(reader)
                
    utc_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    
    snapshots_path = Path('private_artifacts/leaderboard/snapshots.csv')
    
    # Check if we already have entries for today
    already_run_today = False
    if snapshots_path.exists():
        with open(snapshots_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(utc_ts):
                    already_run_today = True
                    break
    
    if already_run_today:
        print(f"Already ran today ({utc_ts}). Exiting.")
        sys.exit(0)
        
    top_30 = []
    sian_row = None
    
    for row in rows:
        try:
            rank = int(row['Rank'])
        except ValueError:
            continue
            
        team_name = row['TeamName']
        score = row['Score']
        
        if rank <= 30:
            top_30.append((rank, team_name, score))
            
        if team_name == 'Sian':
            sian_row = (rank, team_name, score)
            
    # Write to snapshots.csv
    file_exists = snapshots_path.exists()
    with open(snapshots_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['utc_ts', 'rank', 'team', 'score'])
            
        for rank, team_name, score in top_30:
            writer.writerow([utc_ts, rank, team_name, score])
            
        if sian_row:
            # check if Sian is already in top 30 to avoid duplicate
            if sian_row[0] > 30:
                writer.writerow([utc_ts, sian_row[0], sian_row[1], sian_row[2]])
                
    # Write to latest_top10.txt
    top10_path = Path('private_artifacts/leaderboard/latest_top10.txt')
    with open(top10_path, 'w', encoding='utf-8') as f:
        for rank, team_name, score in top_30[:10]:
            f.write(f"{team_name}\n")
            
    print(f"Successfully saved snapshot for {utc_ts}.")
    if sian_row:
        print(f"Sian: Rank {sian_row[0]}, Score {sian_row[2]}")
    else:
        print("Team 'Sian' not found in leaderboard.")
        
if __name__ == '__main__':
    main()
