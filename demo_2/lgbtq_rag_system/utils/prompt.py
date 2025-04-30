# lgbtq_rag_system/utils/prompt.py
def compose_prompt(user_query, articles):
    prompt_lines = [
        "Incorporate the knowledge below for your response:\n"
    ]
    for i, article in enumerate(articles, start=1):
        # Include key fields and truncate content to avoid overly long prompts.
        article_str = (
            f"Date: {article.get('date', 'N/A')}\n"
            f"Tags: {', '.join(article.get('tags', []))}\n"
            f"Content: {article.get('summary', article.get('content', ''))[:500]}...\n"
        )
        prompt_lines.append(article_str)
    prompt_lines.append("\n Using ONLY the above, give a brief answer to the following and provide only the answer:\n")
    prompt_lines.append(f"\"{user_query}\"")
    return "\n".join(prompt_lines)