# lgbtq_rag_system/utils/retrieve.py
def score_article(article, tokens):
    score = 0
    # Retrieve and lowercase article fields.
    title = article.get('title', '').lower()
    summary = article.get('summary', '').lower()
    content = article.get('content', '').lower()
    tags = [tag.lower() for tag in article.get('tags', [])]
    
    for token in tokens:
        if token in title:
            score += 3   # Title weight
        if token in summary:
            score += 2   # Summary weight
        if token in content:
            score += 2   # Content weight
        if token in tags:
            score += 3
        # Tags: each exact match weights 2 points.
        score += 2 * sum(1 for tag in tags if token == tag)
    return score

def retrieve_articles(tokens, articles, top_n=5):
    scored_articles = []
    for article in articles:
        score = score_article(article, tokens)
        if score > 0:
            scored_articles.append((score, article))
    # Rank the results by score (highest first)
    scored_articles.sort(key=lambda x: x[0], reverse=True)
    return [article for score, article in scored_articles][:top_n]