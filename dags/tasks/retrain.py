import os
import shutil 
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression

PRODUCTION_DATA_DIR = "/opt/airflow/production_data"
NEW_DATA_DIR = "/opt/airflow/new_data"
ALL_DATA_DIR = "/opt/airflow/all_data"
MODEL_DIR = "/opt/airflow/models"
CLASSIFIER_PATH = "/opt/airflow/models/classifier.joblib"

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
            # Only use entries with both embedding and stance_encoded
            if "embedding" in data and "predicted_label" in data:
                X.append(data["embedding"])
                y.append(data["stance_encoded"])
    return np.array(X), np.array(y)
            
def run():
    print("🔁 Starting retraining process...")
   
    # Check if there are exactly 5 new articles in new_data
    new_files = [f for f in os.listdir(NEW_DATA_DIR) if f.endswith(".json")]
    if len(new_files) != REVIEW_THRESHOLD:
        print(f"Trigger not met: {len(new_files)}/{REVIEW_THRESHOLD} articles in new_data.")
        return
    
    print("Combining production and new data into all_data...")
    combine_data()

    print("Loading all training data...")
    X, y = load_training_data()
    if len(X) == 0:
        print("No data found for retraining.")
        return

    print(f"Retraining classifier on {len(X)} samples...")
    # Load previous model if it exists, otherwise create a new one
    if os.path.exists(CLASSIFIER_PATH):
        print(f"Loading previous model from {CLASSIFIER_PATH}")
        classifier = joblib.load(CLASSIFIER_PATH)        
    classifier.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(classifier, CLASSIFIER_PATH)
    print(f"Saved retrained classifier to {CLASSIFIER_PATH}")

if __name__ == "__main__":
    run()