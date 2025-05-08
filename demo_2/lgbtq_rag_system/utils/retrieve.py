# lgbtq_rag_system/utils/retrieve.py

import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

INDEX_PATH = "lgbtq_rag_system/embeddings/index.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

def retrieve_articles(query, top_n=5):
    print("🔎 Running semantic retrieval...")

    # Load index and metadata
    with open(INDEX_PATH, "rb") as f:
        data = pickle.load(f)
    index = data["index"]
    metadata = data["metadata"]

    # Load embedding model and encode query
    model = SentenceTransformer(MODEL_NAME)
    query_vec = model.encode([query])
    
    # Search index
    D, I = index.search(np.array(query_vec).astype("float32"), top_n)

    # Return top N articles with metadata
    results = []
    for idx in I[0]:
        if idx < len(metadata):
            results.append(metadata[idx])
    return results