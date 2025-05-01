import os
import json

METRICS_DIR = "/opt/airflow/metrics"

def load_latest_metrics(n=2):
    """Load the two most recent metrics files."""
    files = sorted([
        f for f in os.listdir(METRICS_DIR) if f.endswith(".json")
    ])[-n:]
    
    metrics = []
    for f in files:
        with open(os.path.join(METRICS_DIR, f), "r") as file:
            metrics.append(json.load(file))
    return metrics if len(metrics) == 2 else [None, None]

def decide_branch():
    print("🤖 Evaluating model performance...")
    prev, new = load_latest_metrics()

    if not prev or not new:
        print("⚠️ Not enough metrics to compare. Defaulting to keep_model.")
        return "keep_model"
    
    print(f"🔢 Previous Accuracy: {prev['accuracy']:.4f}")
    print(f"🔢 New Accuracy:      {new['accuracy']:.4f}")

    # force deploy_model to trigger to verify that it works!
    return "deploy_model"
    
    # You can swap this out for f1_score, auc, etc.
    # if new["accuracy"] > prev["accuracy"]:
    #     print("✅ Deploying new model")
    #     return "deploy_model"
    # else:
    #     print("🛑 Keeping current model")
    #     return "keep_model"