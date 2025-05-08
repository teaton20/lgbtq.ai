# lgbtq_rag_system/app.py

from flask import Flask, render_template, request
import json
import logging
import os
import traceback

from utils import prompt as prompt_util
from model import llama_runner
from utils import semantic as semantic_util

app = Flask(__name__)

# Configure logging: log user queries, retrieval details, and LLM responses
logging.basicConfig(filename='logs/queries.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Optional: Maintain a conversation context (memory) across queries
conversation_context = []

@app.route('/', methods=['GET', 'POST'])
def index():
    response_text = ""
    user_query = ""

    if request.method == 'POST':
        user_query = request.form.get('query', '')
        logging.info("User query: " + user_query)

        # 🔍 Use semantic retrieval to get top 3 relevant articles
        matched_articles = semantic_util.semantic_search(user_query, top_k=3)
        logging.info(f"Found {len(matched_articles)} matching articles via semantic search.")

        # If no matching articles are found, use a fallback response.
        if not matched_articles:
            with open('fallback/canned_response.txt', 'r') as f:
                response_text = f.read()
        else:
            # Compose the prompt: details of matched articles + user query
            prompt_str = prompt_util.compose_prompt(user_query, matched_articles)
            conversation_context.append({'query': user_query, 'prompt': prompt_str})
            response_text = llama_runner.run_llm(prompt_str)
        
        logging.info("LLM Response: " + response_text)
    
    # Always pass the query back to the template, even if empty
    return render_template('index.html', query=user_query, response=response_text)


@app.errorhandler(Exception)
def handle_exception(e):
    # Log full traceback to Cloud Run logs
    logging.error("Exception occurred", exc_info=True)
    return "An error occurred: {}".format(str(e)), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)