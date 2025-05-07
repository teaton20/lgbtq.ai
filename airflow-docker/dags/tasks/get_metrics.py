import os
import json
import torch
import joblib
import numpy as np
from datetime import datetime
from sklearn.metrics import accuracy_score
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer
from model_code.model import TripletNet, encode_texts

ALL_DATA_DIR = "/opt/airflow/all_data"
MODEL_DIR = "/opt/airflow/models"
METRICS_DIR = "/opt/airflow/metrics"
HF_MODEL_CACHE = "/opt/airflow/hf_model"
HF_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

os.makedirs(METRICS_DIR, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_articles():
    texts, labels = [], []
    for f in os.listdir(ALL_DATA_DIR):
        if f.endswith(".json"):
            with open(os.path.join(ALL_DATA_DIR, f)) as file:
                data = json.load(file)
                if "content" in data and "true_label" in data:
                    label_raw = data["true_label"]
                    # Normalize label to lowercase string
                    if isinstance(label_raw, int):
                        label = "pro" if label_raw == 1 else "anti" if label_raw == 0 else None
                    elif isinstance(label_raw, str):
                        label = label_raw.strip().lower()
                    else:
                        label = None
                    if label in ["pro", "anti"]:
                        texts.append(data["content"])
                        labels.append(label)
    return texts, labels

def classify_from_centroids(embeddings, labels, train_embeddings, train_labels):
    train_embeddings = np.array(train_embeddings)
    labels = np.array(labels)
    train_labels = np.array(train_labels)

    pro_mask = train_labels == "pro"
    anti_mask = train_labels == "anti"

    if not np.any(pro_mask) or not np.any(anti_mask):
        print("⚠️ Skipping evaluation — missing 'pro' or 'anti' samples.")
        return None  # signal to skip

    pro_centroid = train_embeddings[pro_mask].mean(axis=0)
    anti_centroid = train_embeddings[anti_mask].mean(axis=0)

    pro_sim = cosine_similarity(embeddings, [pro_centroid]).squeeze()
    anti_sim = cosine_similarity(embeddings, [anti_centroid]).squeeze()

    preds = ["pro" if p > a else "anti" for p, a in zip(pro_sim, anti_sim)]
    return preds

def evaluate_model(model_path):
    print(f"📥 Loading model from {model_path}")
    model = TripletNet().to(device)
    model.load_state_dict(joblib.load(model_path))
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    texts, labels = load_articles()
    embeddings = encode_texts(model, tokenizer, texts, batch_size=16, device=device)

    pred_labels = classify_from_centroids(embeddings, labels, embeddings, labels)
    if pred_labels is None:
        return None  # Not enough data for proper evaluation

    return accuracy_score(labels, pred_labels)

def get_comparison_models():
    """Returns (new_model, production_model)."""
    joblibs = sorted([f for f in os.listdir(MODEL_DIR) if f.endswith(".joblib")])
    if len(joblibs) == 0:
        raise ValueError("No model files found.")

    new_model = joblibs[-1]

    try:
        with open(os.path.join(MODEL_DIR, "latest_production_model.txt")) as f:
            prod_model = f.read().strip()
    except FileNotFoundError:
        prod_model = None

    return new_model, prod_model

def run():
    print("📏 Evaluating latest models...")

    flag_path = os.path.join(MODEL_DIR, "retrained_flag.txt")
    if not os.path.exists(flag_path):
        print("⏭️ No new model retrained. Skipping evaluation.")
        return "no_new_model"

    joblibs = sorted([f for f in os.listdir(MODEL_DIR) if f.endswith(".joblib")])
    if len(joblibs) < 2:
        print("⏭️ Not enough models to compare. Skipping evaluation.")
        return "not_enough_models"

    new_model = joblibs[-1]
    prev_model = joblibs[-2]

    if new_model == prev_model:
        print("⏭️ No new model to evaluate.")
        return "no_new_model"

    new_acc = evaluate_model(os.path.join(MODEL_DIR, new_model))
    if new_acc is None:
        print("⚠️ Skipping evaluation. Not enough diversity in labels.")
        return "not_enough_label_diversity"

    print(f"🔍 Accuracy of latest model ({new_model}): {new_acc:.3f}")

    prev_acc = evaluate_model(os.path.join(MODEL_DIR, prev_model))
    prev_acc = prev_acc if prev_acc is not None else 0
    print(f"📊 Accuracy of previous model ({prev_model}): {prev_acc:.3f}")

    best_model = new_model if new_acc >= prev_acc else prev_model
    with open(os.path.join(METRICS_DIR, "model_metrics.json"), "w") as f:
        json.dump({
            "best_model": best_model,
            "new_accuracy": new_acc,
            "prev_accuracy": prev_acc,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)

    print(f"✅ Selected model: {best_model}")
    return "metrics_recorded"