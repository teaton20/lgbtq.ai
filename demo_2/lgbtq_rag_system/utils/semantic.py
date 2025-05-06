# utils/semantic.py

import faiss
import numpy as np
import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Adjust this to your actual location
FRONTEND_DIR = Path("../../../airflow-docker/frontend")
INDEX_PATH = FRONTEND_DIR / "semantic_index.pkl"
ARTICLES_PATH = FRONTEND_DIR / "semantic_articles.json"

# Load FAISS index
def load_faiss_index():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"FAISS index not found at {INDEX_PATH}")
    return faiss.read_index(str(INDEX_PATH))

# Load metadata (articles list)
def load_articles():
    with open(ARTICLES_PATH, "r") as f:
        return json.load(f)

# Load embedding model and data
model = SentenceTransformer("all-MiniLM-L6-v2")  # match training
faiss_index = load_faiss_index()
articles = load_articles()

def semantic_search(query, top_k=3):
    query_embedding = model.encode([query], normalize_embeddings=True)
    distances, indices = faiss_index.search(np.array(query_embedding).astype('float32'), top_k)
    results = [articles[i] for i in indices[0] if i < len(articles)]
    return results