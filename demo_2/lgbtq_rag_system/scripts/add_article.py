# lgbtq_rag_system/scripts/add_article.py
import json
import argparse

def add_article(article, filename='articles.json'):
    with open(filename, 'r') as f:
        articles = json.load(f)
    articles.append(article)
    with open(filename, 'w') as f:
        json.dump(articles, f, indent=4)
    print("Article added.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a new article to the JSON store')
    parser.add_argument('--file', type=str, help='Path to JSON file with article data', required=True)
    args = parser.parse_args()
    
    with open(args.file, 'r') as f:
        article = json.load(f)
    add_article(article)