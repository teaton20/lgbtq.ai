import pandas as pd
import os
import json
from datetime import datetime
from sentence_transformers import SentenceTransformer

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/19gFONrR0d4Ed57gGWtUqVHjjvw85WgysCh9ukhiTmBM/export?format=csv"
REVIEW_QUEUE_DIR = "/opt/airflow/review_queue"
PRODUCTION_DATA_DIR = "/opt/airflow/production_data"
CHUNK_SIZE = 5

def article_already_exists(article_index):
    for filename in os.listdir(PRODUCTION_DATA_DIR):
        if filename.startswith(f"article_{article_index}"):
            return True
    return False

def run():
    print("📥 Fetching CSV data from Google Sheets...")

    os.makedirs(REVIEW_QUEUE_DIR, exist_ok=True)
    os.makedirs(PRODUCTION_DATA_DIR, exist_ok=True)

    df = pd.read_csv(SHEET_CSV_URL)

    # Fill full_text and encode stance
    df["full_text"] = df["title"].fillna("") + " " + df["content"].fillna("")
    df["stance_encoded"] = df["stance"].str.lower().map({"pro": 1, "anti": 0})

    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Split: CHUNK_SIZE for 'new', rest for 'production'
    sample = df.tail(CHUNK_SIZE)
    remaining = df.drop(sample.index)

    # Save production data (the full training base)
    for i, row in remaining.iterrows():
        file_path = os.path.join(PRODUCTION_DATA_DIR, f"article_{i}.json")
        row_data = row.to_dict()
        row_data["true_label"] = int(row_data["stance_encoded"])
        row_data["embedding"] = model.encode([row_data["full_text"]])[0].tolist()
        with open(file_path, "w") as f:
            json.dump(row_data, f, indent=2)
        print(f"🧱 Saved to production_data: {file_path}")

    # Save sample to review queue as "new data"
    for i, row in sample.iterrows():
        if article_already_exists(i):
            print(f"⚠️ Skipping article_{i} — already exists in production_data.")
            continue
        file_path = os.path.join(REVIEW_QUEUE_DIR, f"article_{i}_{datetime.now().isoformat()}.json")
        row_data = row.to_dict()
        row_data["embedding"] = model.encode([row_data["full_text"]])[0].tolist()
        row_data["predicted_label"] = int(row_data["stance_encoded"])  # simulated prediction
        with open(file_path, "w") as f:
            json.dump(row_data, f, indent=2)
        print(f"📝 Saved to review_queue: {file_path}")

    print(f"📦 Finished: {CHUNK_SIZE} new, {len(remaining)} production.")