# lgbtq_rag_system/scripts/validate_json.py
import json
import sys

def validate_article(article):
    required_fields = ['title', 'author', 'source', 'date', 'content', 'tags']
    for field in required_fields:
        if field not in article:
            return False, f"Missing required field: {field}"
    return True, "Valid article."

def validate_articles(filename='articles.json'):
    with open(filename, 'r') as f:
        articles = json.load(f)
    for idx, article in enumerate(articles, start=1):
        valid, message = validate_article(article)
        if not valid:
            print(f"Article {idx} validation failed: {message}")
            return False
    return True

if __name__ == '__main__':
    if validate_articles():
        print("All articles are valid.")
    else:
        sys.exit(1)