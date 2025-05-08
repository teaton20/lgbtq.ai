import os
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient



# MongoDB Atlas Connection URI (Replace with your actual URI)
MONGODB_URI = "mongodb+srv://teaton20:ni0nQTGVyKmeHqjn@lgbtq-ai.j5sdxbs.mongodb.net/?retryWrites=true&w=majority&appName=lgbtq-ai"  # e.g., "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "lgbtq-ai_db"
COLLECTION_NAME = "production_data"

# Load SentenceTransformer model (must match model used during training)
model = SentenceTransformer("all-MiniLM-L6-v2")  # Replace with actual model !!!

# MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Load articles and embeddings from MongoDB
def load_articles_with_embeddings():
    articles = list(collection.find({
        "embedding": {"$exists": True}, 
        "stance": "Pro"
    }))
    
    print(f"✅ Loaded {len(articles)} 'Pro' stance articles with embeddings from MongoDB.")
    
    if articles:
        print(f"✅ Example embedding shape: {np.array(articles[0]['embedding']).shape}")
    
    if not articles:
        print("⚠️ No articles with embeddings found with 'Pro' stance in MongoDB.")
    
    return articles

# Main semantic search
def semantic_search(query, top_k=5):
    articles = load_articles_with_embeddings()
    if not articles:
        print("⚠️ No 'Pro' articles with embeddings found.")
        return []

    query_emb = model.encode([query])[0]  # shape: (dim,)
    article_embs = np.array([a["embedding"] for a in articles])

    similarities = cosine_similarity([query_emb], article_embs)[0]
    print(f"✅ Similarity Scores: {similarities}")

    top_indices = np.argsort(similarities)[::-1][:top_k]
    print(f"✅ Top {top_k} Indices: {top_indices}")

    return [articles[i] for i in top_indices]