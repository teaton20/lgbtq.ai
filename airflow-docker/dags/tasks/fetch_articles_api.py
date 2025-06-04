import pandas as pd
import os
import json
from datetime import datetime
import requests
import joblib
import numpy as np
import re
import hashlib

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(dotenv_path="/opt/airflow/.env")
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["lgbtq-ai_db"]
review_queue = db["review_queue"]
all_data = db["all_data"]
new_data = db["new_data"]
production_data = db["production_data"]

SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
GNEWS_ENDPOINT = os.getenv("GNEWS_ENDPOINT")
CHUNK_SIZE = 5

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text

def fetch_articles_from_gnews():
    query = 'transgender OR "trans" OR "non-binary"'
    params = {
        "q": query,
        "lang": "en",
        "max": 1,
        "token": GNEWS_API_KEY
    }
    try:
        print("Trying to fetch trans-related articles from GNews...")
        r = requests.get(GNEWS_ENDPOINT, params=params)
        if r.status_code == 200:
            all_curr_articles = r.json().get("articles", [])
            unique_articles = []
            seen_titles = set()
            for curr_article in all_curr_articles:
                original_title = curr_article.get("title", "")
                cleaned_title = clean_text(original_title)
                if cleaned_title and cleaned_title not in seen_titles:
                    unique_articles.append(curr_article)
                    seen_titles.add(cleaned_title)
            return unique_articles
        else:
            print(f"Error: status code {r.status_code}, response: {r.text}")
    except Exception as e:
        print(f"Error fetching articles: {e}")
    return []

def make_article_json(row):
    url = row.get("url", "")
    uid = hashlib.sha256(url.encode()).hexdigest()
    date = row.get("date", "") or row.get("publishedAt", "")
    date = date[:10] if date else ""
    title = row.get("title", "")
    publication = row.get("source", "")
    full_text = f"{title} {row.get('content', '')}".strip()

    return {
        "uid": uid,
        "date": date,
        "title": title,
        "url": url,
        "publication": publication,
        "author": None,
        "stance": row.get("stance", ""),
        "full_text": full_text,
        "stance_encoded": None
    }

def actual_run():
    print("📥 Fetching CSV data from Google Sheets...")
    df = pd.read_csv(SHEET_CSV_URL)

    new_articles = []
    articles = fetch_articles_from_gnews()
    for art in articles:
        url = art.get("url", "")
        uid = hashlib.sha256(url.encode()).hexdigest()

        # Skip if already exists in any MongoDB collection
        if any(coll.find_one({"uid": uid}) for coll in [review_queue, all_data, new_data, production_data]):
            continue

        if url not in df["url"].values:
            source_name = art.get("source", {})
            if isinstance(source_name, dict):
                source_name = source_name.get("name", "")
            new_articles.append({
                "title": art.get("title", ""),
                "content": art.get("content", ""),
                "url": url,
                "publishedAt": art.get("publishedAt", ""),
                "source": source_name,
                "date": art.get("publishedAt", "")[:10],
                "stance": ""
            })

    if new_articles:
        print(f"📰 Found {len(new_articles)} new articles. Adding to MongoDB review_queue.")
        for row in new_articles[-CHUNK_SIZE:]:
            article_json = make_article_json(row)
            review_queue.insert_one(article_json)
            print(f"✅ Inserted article to review_queue: {article_json['title']}")

    print("📦 Finished GNews fetch.")

def run():
    print("🫡 skipping this one mawmawww 🗣️")
    # actual_run()

if __name__ == "__main__":
    run()