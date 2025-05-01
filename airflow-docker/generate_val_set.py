# script to get a validation set from the data. just as a starting point.

import pandas as pd
import os
import json
from sentence_transformers import SentenceTransformer

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/19gFONrR0d4Ed57gGWtUqVHjjvw85WgysCh9ukhiTmBM/export?format=csv"
VAL_PATH = "validation/val_data.json"
VAL_SPLIT = 0.25  # 25% of total rows

def run():
    print("📥 Downloading full Google Sheet...")
    df = pd.read_csv(SHEET_CSV_URL)

    print("🧪 Generating validation split...")
    df["full_text"] = df["title"].fillna("") + " " + df["content"].fillna("")
    df["stance_encoded"] = df["stance"].str.lower().map({"pro": 1, "anti": 0})

    val_df = df.sample(frac=VAL_SPLIT, random_state=42)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(val_df["full_text"].tolist(), show_progress_bar=True)

    records = []
    
    for idx, (_, row) in enumerate(val_df.iterrows()):
        records.append({
            "full_text": row["full_text"],
            "true_label": int(row["stance_encoded"]),
            "embedding": embeddings[idx].tolist()
        })

    os.makedirs("validation", exist_ok=True)
    with open(VAL_PATH, "w") as f:
        json.dump(records, f, indent=2)

    print(f"✅ Saved {len(records)} validation records to {VAL_PATH}")

if __name__ == "__main__":
    run()