import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId

REVIEW_THRESHOLD = 100

# MongoDB connection setup
load_dotenv(dotenv_path="/opt/airflow/.env")
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["lgbtq-ai_db"]
review_queue = db["review_queue"]
new_data = db["new_data"]
all_data = db["all_data"]
production_data = db["production_data"]

def article_id_exists(article_id):
    """Check if article ID exists in other collections."""
    for collection in [new_data, all_data, production_data]:
        if collection.find_one({"_id": article_id}):
            return True
    return False

def run():
    print("👀 Checking review queue for labeled articles...")

    total_in_queue = review_queue.count_documents({})
    if total_in_queue < REVIEW_THRESHOLD:
        print(f"⏳ Not enough files in review queue ({total_in_queue}/{REVIEW_THRESHOLD}). Waiting for more.")
        return

    # Only proceed with articles that have been manually labeled (true_label exists)
    labeled_articles = review_queue.find({"true_label": {"$exists": True}})
    labeled_count = review_queue.count_documents({"true_label": {"$exists": True}})

    if labeled_count < REVIEW_THRESHOLD:
        print(f"✋ Waiting for manual labeling. Only {labeled_count}/{REVIEW_THRESHOLD} articles labeled.")
        return

    print(f"✅ Found {labeled_count} labeled articles. Moving to new_data...")

    for article in labeled_articles.limit(REVIEW_THRESHOLD):
        article_id = article.get("_id")

        if not article_id:
            print("⚠️ Skipping malformed article (no _id)")
            continue

        if article_id_exists(article_id):
            print(f"⚠️ Skipping duplicate article {article_id}")
            continue

        new_data.insert_one(article)
        review_queue.delete_one({"_id": article_id})
        print(f"📤 Moved labeled article {article_id} → new_data/")

    print("🎯 Finished human_review processing.")

if __name__ == "__main__":
    run()