import os
import json
import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score

# Directory where metrics JSON files are stored
METRICS_DIR = "/opt/airflow/metrics"

# Path to the latest model predictions file (assumed parquet with y_true and y_pred columns)
PREDICTIONS_PATH = "/opt/airflow/predictions/latest_predictions.parquet"

def load_previous_metrics():
    """
    Load the most recent metrics JSON file from METRICS_DIR.
    Returns:
        dict or None: Parsed JSON metrics if available, else None.
    """
    if not os.path.exists(METRICS_DIR):
        return None
    files = [f for f in os.listdir(METRICS_DIR) if f.endswith(".json")]
    if not files:
        return None
    # Sort files to get the latest by filename (assumes timestamp in filename)
    latest_file = sorted(files)[-1]
    with open(os.path.join(METRICS_DIR, latest_file), "r") as f:
        return json.load(f)

def run():
    """
    Main function to calculate and save model performance metrics.
    Steps:
    1. Ensure metrics directory exists.
    2. Load predictions with true and predicted labels.
    3. Compute confusion matrix and accuracy.
    4. Load previous metrics and compare accuracy.
    5. Save current metrics as a timestamped JSON file.
    """
    print('Running get_metrics task...')
    # Create metrics directory if it doesn't exist
    os.makedirs(METRICS_DIR, exist_ok=True)

    # Check if predictions file exists
    if not os.path.exists(PREDICTIONS_PATH):
        print("No predictions found. Skipping metrics calculation.")
        return

    # Load predictions DataFrame
    df = pd.read_parquet(PREDICTIONS_PATH)

    # Verify required columns exist
    if 'y_true' not in df or 'y_pred' not in df:
        print("Predictions file must contain 'y_true' and 'y_pred' columns.")
        return

    y_true = df['y_true']
    y_pred = df['y_pred']

    # Compute confusion matrix and convert to list for JSON serialization
    cm = confusion_matrix(y_true, y_pred).tolist()

    # Compute accuracy score
    acc = accuracy_score(y_true, y_pred)

    # Load previous metrics to compare accuracy
    prev_metrics = load_previous_metrics()
    prev_acc = prev_metrics['accuracy'] if prev_metrics else None

    # Print current metrics and comparison
    print(f"Confusion Matrix:\n{cm}")
    print(f"Accuracy: {acc:.4f}")
    if prev_acc is not None:
        print(f"Previous Accuracy: {prev_acc:.4f}")
        print(f"Accuracy Change: {acc - prev_acc:+.4f}")

    # Prepare metrics dictionary for saving
    metrics = {
        "confusion_matrix": cm,
        "accuracy": acc,
        "previous_accuracy": prev_acc,
        "n_samples": len(y_true)
    }

    # Save current metrics with timestamped filename
    metrics_file = os.path.join(
        METRICS_DIR, 
        f"metrics_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved metrics to {metrics_file}")

if __name__ == "__main__":
    run()
