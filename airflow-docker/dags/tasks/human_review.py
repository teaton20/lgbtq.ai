import os
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

REVIEW_THRESHOLD = 5

# MongoDB connection setup
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["lgbtq-ai_db"]
review_queue = db["review_queue"]
new_data = db["new_data"]
all_data = db["all_data"]
production_data = db["production_data"]

def article_id_exists(article_id):
    """Check if article ID exists in any collection other than review_queue."""
    for collection in [new_data, all_data, production_data]:
        if collection.find_one({"_id": article_id}):
            return True
    return False

def run():
    print("👀 Checking for enough articles in review queue...")

    total_in_queue = review_queue.count_documents({})
    if total_in_queue >= REVIEW_THRESHOLD:
        print(f"✅ Found {total_in_queue} files — simulating human review...")

        print("💌 Sending email to team...")
        print("hiyyyy time 2 label these new entries babe okthxbye")  # this should be an actual email at some point

        reviewed = 0
        cursor = review_queue.find().limit(REVIEW_THRESHOLD)

        for article in cursor:
            article_id = article.get("_id")
            if not article_id:
                print("⚠️ Skipping malformed article (no _id)")
                continue

            if article_id_exists(article_id):
                print(f"⚠️ Skipping duplicate article {article_id} — already exists elsewhere.")
                continue

            article["true_label"] = article.get("predicted_label")
            new_data.insert_one(article)
            review_queue.delete_one({"_id": article_id})
            print(f"📤 Reviewed + moved article {article_id} → new_data/")
            reviewed += 1

        print("🧠 Human review simulated for this batch.")
    else:
        print(f"⏳ Not enough files ({total_in_queue}/{REVIEW_THRESHOLD}). Waiting.")