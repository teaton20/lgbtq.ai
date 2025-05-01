import pandas as pd
import os
import json
from datetime import datetime
from sentence_transformers import SentenceTransformer
import joblib
import numpy as np

# Configs
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/19gFONrR0d4Ed57gGWtUqVHjjvw85WgysCh9ukhiTmBM/export?format=csv"
REVIEW_QUEUE_DIR = "/opt/airflow/review_queue"
CLASSIFIER_PATH = "/opt/airflow/models/classifier.joblib"
CHUNK_SIZE = 5

def run():
    print("Fetching CSV data from Google Sheets...")
    os.makedirs(REVIEW_QUEUE_DIR, exist_ok=True)

    df = pd.read_csv(SHEET_CSV_URL)

    # Basic filtering and combining
    sample = df.sample(n=CHUNK_SIZE, random_state=42)
    sample["full_text"] = sample["title"].fillna("") + " " + sample["content"].fillna("")

    # Tokenize and embed using SentenceTransformer
    print("Generating embeddings...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(sample["full_text"].tolist(), show_progress_bar=False)

    # Load trained classifier
    print("Loading classifier...")
    classifier = joblib.load(CLASSIFIER_PATH)

    # Get predictions
    print("Predicting stances...")
    predictions = classifier.predict(embeddings)

    # Store into review queue
    for i, (idx, row) in enumerate(sample.iterrows()):
        output = {
            "id": str(idx),
            "title": row.get("title", ""),
            "url": row.get("url", ""),
            "date": row.get("date", ""),
            "text": row.get("text", ""),
            "source": row.get("source", ""),
            "author": row.get("author", ""),
            "embedding": embeddings[i].tolist(),
            "predicted_label": int(predictions[i]),
        }
        out_path = os.path.join(REVIEW_QUEUE_DIR, f"article_{idx}_{datetime.now().isoformat()}.json")
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Saved article to {out_path}")

    print(f"Finished processing {CHUNK_SIZE} articles.")
