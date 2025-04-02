from flask import Flask, render_template, request, jsonify
import subprocess
import io, contextlib
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
from newspaper import Article  # For article extraction

app = Flask(__name__)

# --- LLM Query functions ---

def llama_query(prompt: str, max_tokens: int = 150, model_choice: str = "llama3.2") -> str:
    print(f"Calling model {model_choice} via Ollama CLI...")
    if model_choice.lower() == "llama3.2":
        model_command = "llama3.2:latest"
    elif model_choice.lower() == "mistral":
        model_command = "mistral:latest"
    else:
        model_command = f"{model_choice}:latest"
    print(f"Using model: {model_command}")
    try:
        result = subprocess.run(
            ["ollama", "run", model_command, prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error calling {model_command}: {e.stderr}")
        return ""

def get_tone_description(text: str, model_choice: str) -> str:
    print("Generating tone and style description...")
    prompt = (
        "Analyze the following text and describe its tone, style, intent, and intended audience in a few sentences:\n\n"
        f"{text}\n"
    )
    return llama_query(prompt, max_tokens=150, model_choice=model_choice)

def get_comparative_analysis(text1: str, text2: str, model_choice: str) -> str:
    print("Generating comparative analysis between the two texts...")
    prompt = (
        "Compare the following two texts in terms of tone, purpose, and topic. "
        "Rate their similarity on a scale from 0 (not similar) to 1 (very similar) and provide a brief justification.\n\n"
        f"Text 1:\n{text1}\n\nText 2:\n{text2}\n"
    )
    return llama_query(prompt, max_tokens=200, model_choice=model_choice)

def run_guardrails(text: str, guardrail_questions: list, model_choice: str) -> dict:
    responses = {}
    for question in guardrail_questions:
        app.logger.info(f"Running guardrail question: {question}")
        prompt = (
            "Evaluate the following text for potential issues.\n\n"
            f"Text:\n{text}\n\n"
            f"Question: {question}\n"
            "Answer concisely:"
        )
        response = llama_query(prompt, max_tokens=150, model_choice=model_choice)
        if not response:
            app.logger.warning(f"Guardrail question '{question}' returned an empty response.")
            response = "No response received."
        responses[question] = response
    return responses

# --- Emotion Classification with Pagination ---

def chunk_text(text: str, tokenizer, max_tokens: int = 512) -> list:
    """Splits the text into chunks based on the tokenizer's tokenization."""
    tokens = tokenizer.tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0
    for token in tokens:
        current_chunk.append(token)
        current_length += 1
        if current_length >= max_tokens:
            chunk_str = tokenizer.convert_tokens_to_string(current_chunk)
            chunks.append(chunk_str)
            current_chunk = []
            current_length = 0
    if current_chunk:
        chunk_str = tokenizer.convert_tokens_to_string(current_chunk)
        chunks.append(chunk_str)
    return chunks

def classify_emotions_paginated(text: str, emotion_classifier) -> list:
    """Splits the text into chunks, classifies each chunk, and aggregates the results."""
    tokenizer = emotion_classifier.tokenizer
    chunks = chunk_text(text, tokenizer, max_tokens=512)
    print(f"Text split into {len(chunks)} chunk(s) for emotion classification.")
    aggregated_scores = {}
    num_chunks = 0
    for chunk in chunks:
        results = emotion_classifier(chunk)
        # In case results are nested in a list
        if results and isinstance(results[0], list):
            results = results[0]
        for res in results:
            label = res["label"]
            score = res["score"]
            aggregated_scores[label] = aggregated_scores.get(label, 0) + score
        num_chunks += 1
    averaged_scores = [{"label": label, "score": score / num_chunks} for label, score in aggregated_scores.items()]
    return averaged_scores

# --- Other Analysis Functions ---

def compute_semantic_similarity(text1: str, text2: str, sbert_model) -> float:
    print("Encoding text 1 for semantic similarity...")
    embedding1 = sbert_model.encode(text1)
    print("Encoding text 2 for semantic similarity...")
    embedding2 = sbert_model.encode(text2)
    print("Computing cosine similarity between embeddings...")
    similarity = cosine_similarity([embedding1], [embedding2])[0][0]
    return similarity

# --- Main Analysis Routine ---

def run_analysis(text1: str, text2: str, model_choice: str, guardrail_questions: list) -> dict:
    results = {}
    print("Loading SBERT model for embeddings...")
    sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("\n--- Computing Semantic Similarity ---")
    results['semantic_similarity'] = compute_semantic_similarity(text1, text2, sbert_model)
    print(f"Semantic similarity computed: {results['semantic_similarity']:.4f}\n")
    
    print("\n--- Analyzing Tone and Style for Text 1 ---")
    results['tone_description1'] = get_tone_description(text1, model_choice)
    print("Tone and style for Text 1 obtained.\n")
    
    print("\n--- Analyzing Tone and Style for Text 2 ---")
    results['tone_description2'] = get_tone_description(text2, model_choice)
    print("Tone and style for Text 2 obtained.\n")
    
    print("\n--- Generating Comparative Analysis ---")
    results['comparative_analysis'] = get_comparative_analysis(text1, text2, model_choice)
    print("Comparative analysis obtained.\n")
    
    print("\nAttempting to load an alternative emotion classifier...")
    try:
        emotion_classifier = pipeline(
            "text-classification", 
            model="j-hartmann/emotion-english-distilroberta-base", 
            tokenizer="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True,
            truncation=True,
            max_length=512
        )
        print("Emotion classifier loaded successfully.\n")
    except Exception as e:
        print(f"Error loading emotion classifier: {e}")
        emotion_classifier = None
    
    print("\n--- Classifying Emotions for Text 1 (paginated) ---")
    if emotion_classifier:
        results['emotions_text1'] = classify_emotions_paginated(text1, emotion_classifier)
    else:
        results['emotions_text1'] = []
    print("Emotion classification for Text 1 complete.\n")
    
    print("\n--- Classifying Emotions for Text 2 (paginated) ---")
    if emotion_classifier:
        results['emotions_text2'] = classify_emotions_paginated(text2, emotion_classifier)
    else:
        results['emotions_text2'] = []
    print("Emotion classification for Text 2 complete.\n")
    
    print("\n--- Running Guardrail Analysis for Text 1 ---")
    results['guardrails_text1'] = run_guardrails(text1, guardrail_questions, model_choice)
    print("Guardrail analysis for Text 1 complete.\n")
    
    print("\n--- Running Guardrail Analysis for Text 2 ---")
    results['guardrails_text2'] = run_guardrails(text2, guardrail_questions, model_choice)
    print("Guardrail analysis for Text 2 complete.\n")
    
    return results

# --- Route for Article Extraction ---

@app.route("/get_articles", methods=["POST"])
def get_articles():
    url1 = request.form.get("url1", "").strip()
    url2 = request.form.get("url2", "").strip()
    articles = {"text1": "", "text2": ""}
    try:
        if url1:
            article1 = Article(url1)
            article1.download()
            article1.parse()
            articles["text1"] = article1.text
            print(f"Fetched article from {url1}")
    except Exception as e:
        articles["text1"] = f"Error fetching article: {e}"
        print(f"Error fetching article from {url1}: {e}")
    try:
        if url2:
            article2 = Article(url2)
            article2.download()
            article2.parse()
            articles["text2"] = article2.text
            print(f"Fetched article from {url2}")
    except Exception as e:
        articles["text2"] = f"Error fetching article: {e}"
        print(f"Error fetching article from {url2}: {e}")
    return jsonify(articles)

# --- Flask Routes for Index & Analysis ---

@app.route("/", methods=["GET"])
def index():
    default_guardrails = (
        "Does the text contain violent content? Please explain if any.\n"
        "Does the text contain racist content or language? Please explain if any.\n"
        "Does the text contain sexist content or language? Please explain if any.\n"
        "Does the text promote hate speech or discriminatory language? Please explain if any.\n"
        "Does the text include problematic stereotypes or prejudiced language? Please explain if any."
    )
    return render_template("index.html", default_guardrails=default_guardrails)

@app.route("/analyze", methods=["POST"])
def analyze():
    text1 = request.form.get("text1", "").strip()
    text2 = request.form.get("text2", "").strip()
    model_choice = request.form.get("model_choice", "llama3.2").strip()
    guardrail_text = request.form.get("guardrail_questions", "")
    guardrail_questions = [q.strip() for q in guardrail_text.splitlines() if q.strip()]

    app.logger.info(f"Guardrail raw text: {guardrail_text}")
    app.logger.info(f"Parsed guardrail questions: {guardrail_questions}")

    if not text1 or not text2:
        error_msg = (f"Both article texts are required for analysis. "
                     f"Received text1 length: {len(text1)}, text2 length: {len(text2)}.")
        app.logger.error(error_msg)
        return jsonify({"error": error_msg}), 400

    log_buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(log_buffer):
            results = run_analysis(text1, text2, model_choice, guardrail_questions)
    except Exception as e:
        error_msg = f"An error occurred during analysis: {str(e)}"
        app.logger.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 500

    logs = log_buffer.getvalue()
    rendered_results = render_template("results_partial.html", results=results, logs=logs, text1=text1, text2=text2)
    app.logger.info("Analysis completed successfully.")
    return rendered_results

if __name__ == "__main__":
    app.run(debug=True)