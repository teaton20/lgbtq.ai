# lgbtq_rag_system/utils/prompt.py

def compose_prompt(user_query, articles):
    prompt_lines = [
        "Refer to these current events as facts in your answer:\n"
    ]
    for i, article in enumerate(articles, start=1):
        # Extract and format key fields with the new structure
        article_str = (
            #f"Title: {article.get('title', 'N/A')}\n"
            f" {article.get('date', 'N/A')}\n"
            #f"Publication: {article.get('publication', 'N/A')}\n"
            f" {article.get('full_text', '')[:500]}...\n"
        )
        prompt_lines.append(article_str)

    prompt_lines.append("\nYou have been asked to reply to a question in an organized manner. You are a kind and caring person, with a lot of heart. Answer this question:\n")
    prompt_lines.append(f"\"{user_query}\"")
    return "\n".join(prompt_lines)

