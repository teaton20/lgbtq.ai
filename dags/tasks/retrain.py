import os
import shutil
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from datetime import datetime

PRODUCTION_DATA_DIR = "/opt/airflow/production_data"
NEW_DATA_DIR = "/opt/airflow/new_data"
ALL_DATA_DIR = "/opt/airflow/all_data"
MODEL_DIR = "/opt/airflow/models"
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "classifier.joblib")

REVIEW_THRESHOLD = 5

def combine_data():
    """Combine all JSON files from production and new data into ALL_DATA_DIR."""
    os.makedirs(ALL_DATA_DIR, exist_ok=True)

    # Copy production data
    for f in os.listdir(PRODUCTION_DATA_DIR):
        if f.endswith(".json"):
            src = os.path.join(PRODUCTION_DATA_DIR, f)
            dst = os.path.join(ALL_DATA_DIR, f)
            if not os.path.exists(dst):
                shutil.copy(src, dst)

    # Move new data
    for f in os.listdir(NEW_DATA_DIR):
        if f.endswith(".json"):
            src = os.path.join(NEW_DATA_DIR, f)
            dst = os.path.join(ALL_DATA_DIR, f)
            if not os.path.exists(dst):
                shutil.move(src, dst)

def load_training_data():
    """Load embeddings and labels from ALL_DATA_DIR."""
    X = []
    y = []
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

    print("📊 Loading all training data...")
    X, y = load_training_data()
    if len(X) == 0:
        print("❌ No data found for retraining.")
        return

    print(f"🧠 Retraining classifier on {len(X)} samples...")
    if os.path.exists(CLASSIFIER_PATH):
        print(f"📂 Loading previous model from {CLASSIFIER_PATH}")
        classifier = joblib.load(CLASSIFIER_PATH)

        # Backup previous model
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = os.path.join(MODEL_DIR, f"classifier_backup_{timestamp}.joblib")
        shutil.copy(CLASSIFIER_PATH, backup_path)
        print(f"🛡️ Backed up previous model to {backup_path}")
    else:
        print("🚀 No existing model found. Creating new one.")
        classifier = LogisticRegression()

    classifier.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(classifier, CLASSIFIER_PATH)
    print(f"✅ Saved retrained classifier to {CLASSIFIER_PATH}")

    # Save predictions for evaluation
    print("📦 Generating predictions for metric evaluation...")

    # Predict probabilities and labels
    y_prob = classifier.predict_proba(X)[:, 1]  # Probability for class 1
    y_pred = classifier.predict(X)

    # Build DataFrame
    predictions_df = pd.DataFrame({
        "y_true": y,
        "y_pred": y_pred,
        "y_prob": y_prob
    })

    # Create predictions directory if it doesn't exist
    PREDICTIONS_DIR = "/opt/airflow/predictions"
    os.makedirs(PREDICTIONS_DIR, exist_ok=True)

    # Debugging
    print(predictions_df.head())
    print(f"Saving to: {predictions_path}")

    # Save to Parquet
    predictions_path = os.path.join(PREDICTIONS_DIR, "latest_predictions.parquet")
    predictions_df.to_parquet(predictions_path, index=False)
    print(f"✅ Saved predictions to {predictions_path}")

print("📛 Retrain.py loaded")

if __name__ == "__main__":
    print("🚀 Starting retrain.run() from __main__")
    run()