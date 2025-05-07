import os
import json

METRICS_DIR = "/opt/airflow/metrics"
MODEL_DIR = "/opt/airflow/models"

def load_latest_metrics():
    """Load the most recent model_metrics.json."""
    path = os.path.join(METRICS_DIR, "model_metrics.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as file:
        return json.load(file)

def decide_branch():
    print("👀 Evaluating model performance...")
    metrics = load_latest_metrics()

    if not metrics or "new_accuracy" not in metrics or "prev_accuracy" not in metrics:
        print("⚠️ Metrics missing or malformed. Defaulting to keep_model.")
        return "keep_model"
    
    print(f"🔢 Previous Accuracy: {metrics['prev_accuracy']:.4f}")
    print(f"🔢 New Accuracy:      {metrics['new_accuracy']:.4f}")

    best_model = metrics.get("best_model")
    try:
        with open(os.path.join(MODEL_DIR, "latest_production_model.txt")) as f:
            current_production_model = f.read().strip()
    except FileNotFoundError:
        current_production_model = None

    # Only deploy if new model is better AND not already deployed
    if (
        best_model and 
        best_model != current_production_model and 
        metrics["new_accuracy"] > metrics["prev_accuracy"]
    ):
        print("✅ Deploying new model")
        return "deploy_model"
    else:
        print("🛑 Keeping current model")
        return "keep_model"