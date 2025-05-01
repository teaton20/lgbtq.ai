import os
import shutil
import json

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

        # Here's where we'd actually set up the email command
        print("💌 Sending email to team...")
        print("hiyyyy time 2 label these new entries babe okthxbye")

        for f in files[:REVIEW_THRESHOLD]:
            src_path = os.path.join(REVIEW_QUEUE_DIR, f)
            dst_path = os.path.join(NEW_DATA_DIR, f)

            with open(src_path, "r") as infile:
                article = json.load(infile)

            # Simulate human review for now by copying predicted_label to true_label
            article["true_label"] = article.get("predicted_label")

            with open(dst_path, "w") as outfile:
                json.dump(article, outfile, indent=2)

            os.remove(src_path)
            print(f"📤 Reviewed + moved {f} → new_data/")

        print("🧠 Human review simulated for this batch.")
    else:
        print(f"⏳ Not enough files ({len(files)}/{REVIEW_THRESHOLD}). Waiting.")