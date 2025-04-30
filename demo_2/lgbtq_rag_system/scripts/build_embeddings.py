# lgbtq_rag_system/scripts/build_embeddings.py
import json
import random

def build_embeddings(articles, dim=3):
    # Generate a dummy embedding vector for each article that lacks one.
    for article in articles:
        if 'embedding' not in article or not article['embedding']:
            article['embedding'] = [round(random.uniform(0, 1), 3) for _ in range(dim)]
    return articles

if __name__ == '__main__':
    with open('articles.json', 'r') as f:
        articles = json.load(f)
    articles = build_embeddings(articles)
    with open('articles.json', 'w') as f:
        json.dump(articles, f, indent=4)
    print("Embeddings built and updated.")