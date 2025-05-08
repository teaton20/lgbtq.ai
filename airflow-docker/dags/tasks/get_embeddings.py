import os
import json
import torch
from transformers import AutoTokenizer, AutoModel
from datetime import datetime

# Constants
HF_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
HF_MODEL_CACHE = "/opt/airflow/hf_model"
NEW_DATA_DIR = "/opt/airflow/new_data"

def run():
    print("🧠 Starting embedding task on new_data articles...")

    if not any(f.endswith(".json") for f in os.listdir(NEW_DATA_DIR)):
        print("🕳️ No new articles found in new_data. Moving to next task.")
        return "no_new_articles"

    # Load HF model and tokenizer
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

    for filename in os.listdir(NEW_DATA_DIR):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(NEW_DATA_DIR, filename)

        with open(file_path, "r") as f:
            article = json.load(f)

        # try to embed based on title first, but if no title, try on full_text.
        text_input = article.get("title") or article.get("full_text")
        source = "title" if article.get("title") else "full_text"

        # skip this article if no title or full_text is found.
        if not text_input:
            print(f"⚠️ Skipping {filename} — no title or full_text found.")
            continue

        # Create embedding and update article
        embedding = embed_text(text_input)
        article["embedding"] = embedding

        with open(file_path, "w") as f:
            json.dump(article, f, indent=2)

        print(f"✅ Embedded {source} for {filename}")
        embedded_count += 1

    print(f"📦 Embedded {embedded_count} article(s) into their JSON files.")
    return "embeddings_stored"

if __name__ == "__main__":
    run()