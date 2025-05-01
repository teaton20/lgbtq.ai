import os
import shutil 

PRODUCTION_DATA_DIR = "/opt/airflow/production_data"
NEW_DATA_DIR = "/opt/airflow/new_data"
ALL_DATA_DIR = "/opt/airflow/all_data"
REVIEW_THRESHOLD = 5

def run():
    print("🔁 Starting retraining process...")
    
    os.makedirs(ALL_DATA_DIR, exist_ok=True)

    # Check if there are exactly 5 new articles in new_data
    new_files = [f for f in os.listdir(NEW_DATA_DIR) if f.endswith(".json")]
    if len(new_files) != REVIEW_THRESHOLD:
        print(f"Trigger not met: {len(new_files)}/{REVIEW_THRESHOLD} articles in new_data.")
        return

    # Move all production data files to all_data
    prod_files = [f for f in os.listdir(PRODUCTION_DATA_DIR) if f.endswith(".json")]
    for f in prod_files:
        src = os.path.join(PRODUCTION_DATA_DIR, f)
        dst = os.path.join(ALL_DATA_DIR, f)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            print(f"Copied {f} from production_data to all_data.")

    # Move all new data files to all_data
    for f in new_files:
        src = os.path.join(NEW_DATA_DIR, f)
        dst = os.path.join(ALL_DATA_DIR, f)
        if not os.path.exists(dst):
            shutil.move(src, dst)
            print(f"Moved {f} from new_data to all_data.")

    print("All production and new data files are now combined in all_data.")

if __name__ == "__main__":
    run()