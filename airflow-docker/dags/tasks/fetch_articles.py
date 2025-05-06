import pandas as pd
import os
import json
from datetime import datetime
from sentence_transformers import SentenceTransformer
import requests
from time import sleep
import joblib
import numpy as np


SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/19gFONrR0d4Ed57gGWtUqVHjjvw85WgysCh9ukhiTmBM/export?format=csv"
REVIEW_QUEUE_DIR = "/opt/airflow/review_queue"
PRODUCTION_DATA_DIR = "/opt/airflow/production_data"
MODEL_PATH = "/opt/airflow/models/classifier.joblib"
#MODEL_PATH = "~/Downloads/classifier.joblib"
CHUNK_SIZE = 5
GNEWS_API_KEY = "5656c1aafe7e3642d853a5bfb1570caa"  
GNEWS_ENDPOINT = "https://gnews.io/api/v4/search"

def fetch_one_article(publication):
    """
    Fetch one trans-related article from the given publication using GNews API.
    """
    query = f'site:{publication} transgender OR "trans community" OR "trans rights"'
    params = {
        "q": query,
        "lang": "en",
        "max": 1,
        "token": GNEWS_API_KEY
    }
    try:
        r = requests.get(GNEWS_ENDPOINT, params=params)
        if r.status_code == 200:
            articles = r.json().get("articles", [])
            if articles:
                art = articles[0]
                return {
                    "title": art.get("title", ""),
                    "content": art.get("content", ""),
                    "url": art.get("url", ""),
                    "publishedAt": art.get("publishedAt", ""),
                    "source": publication,
                    "summary": art.get("description", ""),
                    "date": art.get("publishedAt", "")[:10],
                    "stance": "",  # To be labeled later
                }
    except Exception as e:
        print(f"Error fetching for {publication}: {e}")
    return None

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

    # Get a list of unique publication names from the 'source' column, excluding any missing values
    publications = df['source'].dropna().unique().tolist()

    # Prepare an empty list to store any new articles found
    new_articles = []

    # Loop through each publication in the list
    for pub in publications:
        print(f"🔎 Searching for new article from {pub}...")
        # Try to fetch one trans-related article from this publication using your API function
        article = fetch_one_article(pub)
        # If an article was found AND its URL is not already in the existing DataFrame
        if article and article['url'] not in df['url'].values:
            # Add the new article to the list
            new_articles.append(article)
        # Wait 10 seconds between API requests to avoid hitting rate limits
        sleep(10)

    # If any new articles were found in this round
    if new_articles:
        print(f"📰 Found {len(new_articles)} new articles. Adding to dataframe.")
        # Convert the list of new articles (dicts) into a DataFrame
        new_df = pd.DataFrame(new_articles)
        # Concatenate the new articles onto the existing DataFrame
        df = pd.concat([df, new_df], ignore_index=True)
        # Remove duplicate articles based on the 'url' column
        df = df.drop_duplicates(subset=["url"])

        # Save the updated DataFrame to a CSV file
        df.to_csv("updated_articles.csv", index=False)
        print("✅ Updated CSV with new articles.")

    # Fill full_text and encode stance
    df["full_text"] = df["title"].fillna("") + " " + df["content"].fillna("")
    df["stance_encoded"] = df["stance"].str.lower().map({"pro": 1, "anti": 0})

    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Load the latest classifier model for prediction
    if os.path.exists(MODEL_PATH):
        classifier = joblib.load(MODEL_PATH)
        print("✅ Loaded classifier model for predictions.")
    else:
        classifier = None
        print("⚠️ No classifier model found. Predictions will be skipped.")

    # Split: CHUNK_SIZE for 'new', rest for 'production'
    sample = df.tail(CHUNK_SIZE)
    remaining = df.drop(sample.index)

    # Save production data (the full training base)
    for i, row in remaining.iterrows():
        file_path = os.path.join(PRODUCTION_DATA_DIR, f"article_{i}.json")
        row_data = row.to_dict()
        row_data["true_label"] = int(row_data["stance_encoded"]) if pd.notnull(row_data["stance_encoded"]) else None
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
        #row_data["predicted_label"] = int(row_data["stance_encoded"])  # simulated prediction
        if classifier is not None:
            X_pred = np.array(row_data["embedding"]).reshape(1, -1)
            row_data["predicted_label"] = int(classifier.predict(X_pred)[0])
        else:
            row_data["predicted_label"] = None
        with open(file_path, "w") as f:
            json.dump(row_data, f, indent=2)
        print(f"📝 Saved to review_queue: {file_path}")

    print(f"📦 Finished: {CHUNK_SIZE} new, {len(remaining)} production.")