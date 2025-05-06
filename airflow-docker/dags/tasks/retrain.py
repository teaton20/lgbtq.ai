import os
import shutil
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from datetime import datetime

# directories
PRODUCTION_DATA_DIR = "/opt/airflow/production_data"
NEW_DATA_DIR = "/opt/airflow/new_data"
ALL_DATA_DIR = "/opt/airflow/all_data"
MODEL_DIR = "/opt/airflow/models"
FRONTEND_DIR = "/opt/airflow/frontend"
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "classifier.joblib")

REVIEW_THRESHOLD = 5

def combine_data():
    os.makedirs(ALL_DATA_DIR, exist_ok=True)

    for f in os.listdir(PRODUCTION_DATA_DIR):
        if f.endswith(".json"):
            src = os.path.join(PRODUCTION_DATA_DIR, f)
            dst = os.path.join(ALL_DATA_DIR, f)
            if not os.path.exists(dst):
                shutil.copy(src, dst)

    for f in os.listdir(NEW_DATA_DIR):
        if f.endswith(".json"):
            try:
                article_id = f.split("_")[1]
            except IndexError:
                print(f"⚠️ Skipping malformed filename: {f}")
                continue
            if any(existing.startswith(f"article_{article_id}_") for existing in os.listdir(ALL_DATA_DIR)):
                print(f"⚠️ Skipping duplicate article_{article_id}")
                continue
            shutil.move(os.path.join(NEW_DATA_DIR, f), os.path.join(ALL_DATA_DIR, f))

def load_training_data():
    X, y = [], []
    for f in os.listdir(ALL_DATA_DIR):
        if f.endswith(".json"):
            with open(os.path.join(ALL_DATA_DIR, f), "r") as file:
                data = json.load(file)
            if "embedding" in data and "true_label" in data:
                X.append(data["embedding"])
                y.append(data["true_label"])
    return np.array(X), np.array(y)

def run():
    print("🔁 Starting retraining process...")

    new_files = [f for f in os.listdir(NEW_DATA_DIR) if f.endswith(".json")]
    if len(new_files) < REVIEW_THRESHOLD:
        print(f"Trigger not met: only {len(new_files)} articles in new_data.")
        return

    print("📦 Combining production and new data into all_data...")
    combine_data()

    print("📊 Loading training data...")
    X, y = load_training_data()
    if len(X) == 0:
        print("❌ No data found for retraining.")
        return

    print(f"🧠 Retraining classifier on {len(X)} samples...")
    if os.path.exists(CLASSIFIER_PATH):
        classifier = joblib.load(CLASSIFIER_PATH)
        backup_path = os.path.join(MODEL_DIR, f"classifier_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.joblib")
        shutil.copy(CLASSIFIER_PATH, backup_path)
        print(f"🛡️ Backed up model to {backup_path}")
    else:
        classifier = LogisticRegression()

    classifier.fit(X, y)
    joblib.dump(classifier, CLASSIFIER_PATH)
    print(f"✅ Saved classifier to {CLASSIFIER_PATH}")

    print("📈 Saving predictions...")
    y_prob = classifier.predict_proba(X)[:, 1]
    y_pred = classifier.predict(X)
    predictions_df = pd.DataFrame({"y_true": y, "y_pred": y_pred, "y_prob": y_prob})
    predictions_dir = "/opt/airflow/predictions"
    os.makedirs(predictions_dir, exist_ok=True)
    predictions_df.to_parquet(os.path.join(predictions_dir, "latest_predictions.parquet"), index=False)

    # 🔍 Build Semantic Index for RAG
    try:
        from sentence_transformers import SentenceTransformer
        import faiss

        print("📚 Building semantic index for frontend...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        texts, metadata = [], []

        for f in os.listdir(ALL_DATA_DIR):
            if f.endswith(".json"):
                with open(os.path.join(ALL_DATA_DIR, f), "r") as file:
                    article = json.load(file)
                if "content" in article:
                    texts.append(article["content"])
                    metadata.append({
                        "title": article.get("title", ""),
                        "summary": article.get("summary", ""),
                        "content": article.get("content", ""),
                        "tags": article.get("tags", []),
                        "date": article.get("date", ""),
                        "url": article.get("url", "")
                    })

        if not texts:
            print("⚠️ No valid content found for embeddings.")
            return

        vectors = model.encode(texts)
        index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(vectors)

        # Save paths for frontend compatibility
        os.makedirs(FRONTEND_DIR, exist_ok=True)
        with open(os.path.join(FRONTEND_DIR, "semantic_articles.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        faiss.write_index(index, os.path.join(FRONTEND_DIR, "semantic_index.faiss"))

        print("✅ Semantic index and metadata saved for frontend.")

    except Exception as e:
        print(f"❌ Semantic index creation failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting retrain.run() from __main__")
    run()