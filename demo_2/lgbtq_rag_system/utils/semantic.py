# lgbtq_rag_system/utils/semantic.py

import os
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Adjust this to your actual location
CURRENT_DIR = Path(__file__).resolve()
FRONTEND_DIR = CURRENT_DIR.parents[3] / "airflow-docker" / "frontend"
ARTICLES_PATH = FRONTEND_DIR / "semantic_articles.json"
EMBEDDINGS_PATH = FRONTEND_DIR / "embeddings" / "article_embeddings.npy"

# Load SentenceTransformer model (must match model used during training)
model = SentenceTransformer("all-MiniLM-L6-v2")  # Replace with actual model !!!!

# Load articles and embeddings
def load_articles_with_embeddings():
    with open(ARTICLES_PATH, "r") as f:
        articles = json.load(f)

    # Filter only those that include an embedding
    return [a for a in articles if "embedding" in a]

# Main semantic search
def semantic_search(query, top_k=3):
    articles = load_articles_with_embeddings()
    if not articles:
        print("⚠️ No articles with embeddings found.")
        return []

    query_emb = model.encode([query])[0]  # shape: (dim,)
    article_embs = np.array([a["embedding"] for a in articles])

    similarities = cosine_similarity([query_emb], article_embs)[0]
    top_indices = np.argsort(similarities)[::-1][:top_k]

    return [articles[i] for i in top_indices]