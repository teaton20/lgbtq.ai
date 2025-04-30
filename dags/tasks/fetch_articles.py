import pandas as pd
import os
from datetime import datetime

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/19gFONrR0d4Ed57gGWtUqVHjjvw85WgysCh9ukhiTmBM/export?format=csv"
REVIEW_QUEUE_DIR = "/opt/airflow/review_queue"
CHUNK_SIZE = 5

def run():
    print("Fetching CSV data from Google Sheets...")

    os.makedirs(REVIEW_QUEUE_DIR, exist_ok=True)

    df = pd.read_csv(SHEET_CSV_URL)

    sample = df.sample(n=CHUNK_SIZE, random_state=42)

    for i, row in sample.iterrows():
        file_path = os.path.join(REVIEW_QUEUE_DIR, f"article_{i}_{datetime.now().isoformat()}.json")
        row.to_json(file_path, indent=2)
        print(f"Wrote article to {file_path}")

    print(f"Added {CHUNK_SIZE} articles into the review queue.")