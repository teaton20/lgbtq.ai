import os
import shutil

REVIEW_QUEUE_DIR = "/opt/airflow/review_queue"
NEW_DATA_DIR = "/opt/airflow/new_data"
REVIEW_THRESHOLD = 5

def run():
    print("👀 Checking for enough articles in review queue...")

    os.makedirs(REVIEW_QUEUE_DIR, exist_ok=True)
    os.makedirs(NEW_DATA_DIR, exist_ok=True)

    files = [f for f in os.listdir(REVIEW_QUEUE_DIR) if f.endswith(".json")]

    if len(files) >= REVIEW_THRESHOLD:
        print(f"✅ Found {len(files)} files — simulating human review...")
        for f in files[:REVIEW_THRESHOLD]:
            src = os.path.join(REVIEW_QUEUE_DIR, f)
            dst = os.path.join(NEW_DATA_DIR, f)
            shutil.move(src, dst)
            print(f"Moved {f} to new_data/")
        print("Review complete.")
    else:
        print(f"Not enough files ({len(files)}/{REVIEW_THRESHOLD}). Review skipped.")