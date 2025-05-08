import os
import torch
import json
from transformers import AutoTokenizer, AutoModel
from dotenv import load_dotenv
from pymongo import MongoClient

# Constants
HF_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
HF_MODEL_CACHE = "/opt/airflow/hf_model"

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["lgbtq-ai_db"]
new_data = db["new_data"]

def run():
    print("🧠 Starting embedding task on new_data articles...")

    articles = list(new_data.find({"embedding": {"$exists": False}}))

    if not articles:
        print("🕳️ No unembedded articles found in new_data. Moving to next task.")
        return "no_new_articles"

    # Load model + tokenizer
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID, cache_dir=HF_MODEL_CACHE)
    model = AutoModel.from_pretrained(HF_MODEL_ID, cache_dir=HF_MODEL_CACHE)
    model.eval()

    def embed_text(text):
        with torch.no_grad():
            encoded = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
            output = model(**encoded)
            embeddings = output.last_hidden_state.mean(dim=1)
            return embeddings.squeeze(0).tolist()

    embedded_count = 0

    for article in articles:
        article_id = article["_id"]
        title = article.get("title") or ""
        full_text = article.get("full_text") or ""

        if not (title or full_text):
            print(f"⚠️ Skipping article {article_id} — no title or full_text found.")
            continue

        combined_input = f"{title}\n\n{full_text}".strip()
        embedding = embed_text(combined_input)

        new_data.update_one(
            {"_id": article_id},
            {"$set": {"embedding": embedding}}
        )

        print(f"✅ Embedded title + full_text for article {article_id}")
        embedded_count += 1

    print(f"📦 Embedded {embedded_count} article(s) into MongoDB.")
    return "embeddings_stored"

if __name__ == "__main__":
    run()