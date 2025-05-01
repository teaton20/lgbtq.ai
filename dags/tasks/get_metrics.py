import os
import json
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

METRICS_DIR = "/opt/airflow/metrics"
PREDICTIONS_PATH = "/opt/airflow/predictions/latest_predictions.parquet"

def load_previous_metrics():
    """Load the most recent metrics JSON file from METRICS_DIR."""
    if not os.path.exists(METRICS_DIR):
        return None
    files = [f for f in os.listdir(METRICS_DIR) if f.endswith(".json")]
    if not files:
        return None
    latest_file = sorted(files)[-1]
    with open(os.path.join(METRICS_DIR, latest_file), "r") as f:
        return json.load(f)

def run():
    print("Running get_metrics task...")

    os.makedirs(METRICS_DIR, exist_ok=True)

    if not os.path.exists(PREDICTIONS_PATH):
        print("No predictions found. Skipping metrics calculation.")
        return

    df = pd.read_parquet(PREDICTIONS_PATH)

    if 'y_true' not in df or 'y_pred' not in df:
        print("Predictions file must contain 'y_true' and 'y_pred' columns.")
        return

    y_true = df['y_true']
    y_pred = df['y_pred']

    # Compute core metrics
    cm = confusion_matrix(y_true, y_pred).tolist()
    acc = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    # AUC (optional, only if probabilities are available)
    auc = None
    if 'y_prob' in df.columns:
        try:
            auc = roc_auc_score(y_true, df['y_prob'])
        except ValueError as e:
            print(f"AUC could not be computed: {e}")

    # Compare to previous metrics
    prev_metrics = load_previous_metrics()
    prev_acc = prev_metrics.get("accuracy") if prev_metrics else None

    # Display current metrics
    print(f"Confusion Matrix:\n{cm}")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    if auc is not None:
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
        "n_samples": len(y_true)
    }

    metrics_file = os.path.join(
        METRICS_DIR,
        f"metrics_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved metrics to {metrics_file}")

if __name__ == "__main__":
    run()