import os
import json

METRICS_DIR = "/opt/airflow/metrics"
MODEL_DIR = "/opt/airflow/models"
RETRAIN_FLAG = os.path.join(MODEL_DIR, "retrained_flag.txt")

def load_latest_metrics():
    path = os.path.join(METRICS_DIR, "model_metrics.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as file:
        return json.load(file)

def decide_branch():
    print("👀 Evaluating model performance...")

    # ✅ Skip decision if no retrain occurred
    if not os.path.exists(RETRAIN_FLAG):
        print("🕳️ No retrain detected this run. Skipping deployment decision.")
        return "keep_model"

    metrics = load_latest_metrics()
    if not metrics:
        print("⚠️ No metrics found. Keeping current model.")
        return "keep_model"

    best_model = metrics.get("best_model")
    new_acc = metrics.get("new_accuracy")
    prev_acc = metrics.get("prev_accuracy")

    if not best_model or new_acc is None or prev_acc is None:
        print("⚠️ Incomplete metrics file. Keeping current model.")
        return "keep_model"

    print(f"🔢 Previous Accuracy: {prev_acc:.4f}")
    print(f"🔢 New Accuracy:      {new_acc:.4f}")

    try:
        with open(os.path.join(MODEL_DIR, "latest_production_model.txt")) as f:
            current_production_model = f.read().strip()
    except FileNotFoundError:
        current_production_model = None

    if best_model != current_production_model and new_acc > prev_acc:
        print("✅ Deploying new model")
        return "deploy_model"
    else:
        print("🛑 Keeping current model")
        return "keep_model"