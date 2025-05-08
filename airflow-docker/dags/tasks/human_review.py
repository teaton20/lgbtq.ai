import os
import json

REVIEW_QUEUE_DIR = "/opt/airflow/review_queue"
NEW_DATA_DIR = "/opt/airflow/new_data"
REVIEW_THRESHOLD = 5

def article_id_exists(article_id):
    search_dirs = [NEW_DATA_DIR, "/opt/airflow/all_data", "/opt/airflow/production_data"]
    for dir_path in search_dirs:
        if not os.path.exists(dir_path):
            continue
        for f in os.listdir(dir_path):
            if f.startswith(f"article_{article_id}_"):
                return True
    return False

# for now this is simulating that we went in and labeled these new data that 
# were placed in the review_queue, so this is simulating that we're doing that
# so that the next task can trigger.

def run():
    print("👀 Checking for enough articles in review queue...")

    os.makedirs(REVIEW_QUEUE_DIR, exist_ok=True)
    os.makedirs(NEW_DATA_DIR, exist_ok=True)

    files = [f for f in os.listdir(REVIEW_QUEUE_DIR) if f.endswith(".json")]

    if len(files) >= REVIEW_THRESHOLD:
        print(f"✅ Found {len(files)} files — simulating human review...")

        print("💌 Sending email to team...")
        print("hiyyyy time 2 label these new entries babe okthxbye") # this should be an actual email at some point

        reviewed = 0
        for f in files:
            if reviewed >= REVIEW_THRESHOLD:
                break

            try:
                article_id = f.split("_")[1]  # assumes format article_{id}_{timestamp}.json
            except IndexError:
                print(f"⚠️ Skipping malformed filename: {f}")
                continue

            if article_id_exists(article_id):
                print(f"⚠️ Skipping duplicate article_{article_id} — already exists in new_data.")
                continue

            src_path = os.path.join(REVIEW_QUEUE_DIR, f)
            dst_path = os.path.join(NEW_DATA_DIR, f)

            with open(src_path, "r") as infile:
                article = json.load(infile)

            article["true_label"] = article.get("predicted_label")

            with open(dst_path, "w") as outfile:
                json.dump(article, outfile, indent=2)

            os.remove(src_path)
            print(f"📤 Reviewed + moved {f} → new_data/")
            reviewed += 1

        print("🧠 Human review simulated for this batch.")
    else:
        print(f"⏳ Not enough files ({len(files)}/{REVIEW_THRESHOLD}). Waiting.")