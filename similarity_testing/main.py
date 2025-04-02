import subprocess
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

def compute_semantic_similarity(text1: str, text2: str, sbert_model) -> float:
    print("Encoding text 1 for semantic similarity...")
    embedding1 = sbert_model.encode(text1)
    print("Encoding text 2 for semantic similarity...")
    embedding2 = sbert_model.encode(text2)
    print("Computing cosine similarity between embeddings...")
    similarity = cosine_similarity([embedding1], [embedding2])[0][0]
    return similarity

def llama_query(prompt: str, max_tokens: int = 150) -> str:
    print("Calling Llama3.2 via Ollama CLI...")
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2:latest", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error calling Llama3.2: {e.stderr}")
        return ""

def get_tone_description(text: str) -> str:
    print("Generating tone and style description...")
    prompt = (
        "Analyze the following text and describe its tone, style, intent, and intended audience in a few sentences:\n\n"
        f"{text}\n"
    )
    return llama_query(prompt, max_tokens=150)

def get_comparative_analysis(text1: str, text2: str) -> str:
    print("Generating comparative analysis between the two texts...")
    prompt = (
        "Compare the following two texts in terms of tone, purpose, and topic. "
        "Rate their similarity on a scale from 0 (not similar) to 1 (very similar) and provide a brief justification.\n\n"
        f"Text 1:\n{text1}\n\nText 2:\n{text2}\n"
    )
    return llama_query(prompt, max_tokens=200)

def classify_emotions(text: str, emotion_classifier) -> list:
    if emotion_classifier is None:
        print("Emotion classifier not available, skipping emotion classification.")
        return []
    print("Classifying emotions for a text using the emotion classifier...")
    return emotion_classifier(text)

def flatten_emotions(emotions):
    """
    Flatten the emotions output if it's nested. 
    For example, if emotions is a list containing another list, return that inner list.
    """
    if emotions and isinstance(emotions[0], list):
        return emotions[0]
    return emotions

def main():
    # Example input texts (replace these with your actual paragraphs)
    text1 = (
        "In today's rapidly evolving technological landscape, innovation is not just a buzzword "
        "but a driving force behind global progress. This article explores the emerging trends in AI "
        "and how they reshape our understanding of work and creativity."
    )
    text2 = (
        "The modern world is experiencing a surge in technological breakthroughs that are transforming industries. "
        "This piece delves into the impact of artificial intelligence on traditional work environments and creative sectors."
    )
    
    print("Loading SBERT model for embeddings...")
    sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("\n--- Computing Semantic Similarity ---")
    semantic_similarity = compute_semantic_similarity(text1, text2, sbert_model)
    print(f"Semantic similarity computed: {semantic_similarity:.4f}\n")
    
    print("\n--- Analyzing Tone and Style for Text 1 ---")
    tone_description1 = get_tone_description(text1)
    print("Tone and style for Text 1 obtained.\n")
    
    print("\n--- Analyzing Tone and Style for Text 2 ---")
    tone_description2 = get_tone_description(text2)
    print("Tone and style for Text 2 obtained.\n")
    
    print("\n--- Generating Comparative Analysis ---")
    comparative_analysis = get_comparative_analysis(text1, text2)
    print("Comparative analysis obtained.\n")
    
    print("\nAttempting to load an alternative emotion classifier...")
    try:
        emotion_classifier = pipeline(
            "text-classification", 
            model="j-hartmann/emotion-english-distilroberta-base", 
            return_all_scores=True
        )
        print("Emotion classifier loaded successfully.\n")
    except Exception as e:
        print(f"Error loading emotion classifier: {e}")
        emotion_classifier = None
    
    print("\n--- Classifying Emotions for Text 1 ---")
    emotions_text1 = classify_emotions(text1, emotion_classifier)
    emotions_text1 = flatten_emotions(emotions_text1)
    print("Emotion classification for Text 1 complete.\n")
    
    print("\n--- Classifying Emotions for Text 2 ---")
    emotions_text2 = classify_emotions(text2, emotion_classifier)
    emotions_text2 = flatten_emotions(emotions_text2)
    print("Emotion classification for Text 2 complete.\n")
    
    # Print out results
    print("\n=== Results ===")
    print("=== Semantic Similarity (Cosine Similarity) ===")
    print(f"Similarity Score: {semantic_similarity:.4f}\n")
    
    print("=== Tone and Style Analysis ===")
    print("Text 1 Analysis:")
    print(tone_description1 + "\n")
    print("Text 2 Analysis:")
    print(tone_description2 + "\n")
    
    print("=== Comparative Analysis ===")
    print(comparative_analysis + "\n")
    
    if emotions_text1 and emotions_text2:
        print("=== Emotion Classification ===")
        print("Text 1 Emotions:")
        for emotion in emotions_text1:
            try:
                print(f"{emotion['label']}: {emotion['score']:.4f}")
            except Exception as e:
                print(f"Error processing emotion: {e}")
        print("\nText 2 Emotions:")
        for emotion in emotions_text2:
            try:
                print(f"{emotion['label']}: {emotion['score']:.4f}")
            except Exception as e:
                print(f"Error processing emotion: {e}")
    else:
        print("Emotion classification was skipped or not available.")

if __name__ == "__main__":
    main()