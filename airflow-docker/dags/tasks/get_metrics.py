import os
import json
import pandas as pd
import joblib
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from datetime import datetime

MODEL_PATH = "/opt/airflow/models/classifier.joblib"
VAL_DATA_PATH = "/opt/airflow/validation/val_data.json"
METRICS_DIR = "/opt/airflow/metrics"
LATEST_METRICS_POINTER = os.path.join(METRICS_DIR, "latest_metrics.json")

def load_previous_metrics():
    if not os.path.exists(LATEST_METRICS_POINTER):
        return None
    with open(LATEST_METRICS_POINTER, "r") as f:
        return json.load(f)

def run():
    print("📊 Running get_metrics task...")

    os.makedirs(METRICS_DIR, exist_ok=True)

    # Load classifier
    if not os.path.exists(MODEL_PATH):
        print("❌ No model found. Skipping.")
        return
    classifier = joblib.load(MODEL_PATH)

    # Load validation data
    if not os.path.exists(VAL_DATA_PATH):
        print("❌ No validation data found.")
        return
    with open(VAL_DATA_PATH, "r") as f:
        val_data = json.load(f)

    X = [item["embedding"] for item in val_data]
    y_true = [item["true_label"] for item in val_data]

    y_pred = classifier.predict(X)
    y_prob = classifier.predict_proba(X)[:, 1]

    # Compute metrics
    cm = confusion_matrix(y_true, y_pred).tolist()
    acc = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_prob)

    prev_metrics = load_previous_metrics()
    prev_acc = prev_metrics.get("accuracy") if prev_metrics else None

    print(f"📈 Confusion Matrix:\n{cm}")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"AUC: {auc:.4f}")
    if prev_acc is not None:
        print(f"Previous Accuracy: {prev_acc:.4f}")
        print(f"Accuracy Change: {acc - prev_acc:+.4f}")

    # Save metrics
    metrics = {
        "confusion_matrix": cm,
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "auc": auc,
        "previous_accuracy": prev_acc,
        "n_samples": len(y_true),
        "evaluated_at": datetime.now().isoformat()
    }

    timestamped_path = os.path.join(
        METRICS_DIR, f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(timestamped_path, "w") as f:
        json.dump(metrics, f, indent=2)

    with open(LATEST_METRICS_POINTER, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Saved metrics to {timestamped_path}")
    print(f"🔗 Updated latest_metrics.json for deployment reference.")

if __name__ == "__main__":
    run()