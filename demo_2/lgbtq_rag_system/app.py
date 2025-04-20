# lgbtq_rag_system/app.py
from flask import Flask, render_template, request
import json
import logging
import os

from utils import query as query_util
from utils import retrieve as retrieve_util
from utils import prompt as prompt_util
from model import llama_runner

app = Flask(__name__)

# Configure logging: log user queries, retrieval details, and LLM responses
logging.basicConfig(filename='logs/queries.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Function to load the articles from the JSON store
def load_articles():
    with open('articles.json', 'r') as f:
        return json.load(f)

articles = load_articles()

# Optional: Maintain a conversation context (memory) across queries
conversation_context = []

@app.route('/', methods=['GET', 'POST'])
def index():
    response_text = ""
    user_query = ""
    if request.method == 'POST':
        user_query = request.form.get('query', '')
        logging.info("User query: " + user_query)

        # Preprocess: tokenization, lowercasing, stopword removal, and synonym expansion
        processed_tokens = query_util.preprocess_query(user_query)
        logging.info("Processed tokens: " + ", ".join(processed_tokens))

        # Retrieve articles using keyword and weighted field matching
        matched_articles = retrieve_util.retrieve_articles(processed_tokens, articles, top_n=3)
        logging.info(f"Found {len(matched_articles)} matching articles.")

        # If no matching articles are found, use a fallback response.
        if not matched_articles:
            with open('fallback/canned_response.txt', 'r') as f:
                response_text = f.read()
        else:
            # Compose the prompt: details of matched articles + user query
            prompt_str = prompt_util.compose_prompt(user_query, matched_articles)
            # Save the query & prompt in the conversation context (for optional follow-ups)
            conversation_context.append({'query': user_query, 'prompt': prompt_str})
            # Call the local LLM (e.g., LLaMA3 via Ollama) via the subprocess wrapper
            response_text = llama_runner.run_llm(prompt_str)
        
        logging.info("LLM Response: " + response_text)
        return render_template('index.html', query=user_query, response=response_text)
    
    return render_template('index.html', query=user_query, response=response_text)

if __name__ == '__main__':
    # Use port 5000 by default, or adjust if already in use.
    app.run(debug=True, port=5001)