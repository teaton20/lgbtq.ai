import os
import shutil
import json
from datetime import datetime

MODEL_DIR = "/opt/airflow/models"
METRICS_PATH = "/opt/airflow/metrics/model_metrics.json"

def run():
    print("🚀 Deploying new model...")

    # Load path to best model from metrics
    if not os.path.exists(METRICS_PATH):
        raise FileNotFoundError(f"No metrics file found at {METRICS_PATH}")

    with open(METRICS_PATH) as f:
        metrics = json.load(f)
    
    best_model_name = metrics.get("best_model")
    if not best_model_name:
        raise ValueError("❌ No 'best_model' key found in metrics file.")

    best_model_path = os.path.join(MODEL_DIR, best_model_name)
    if not os.path.exists(best_model_path):
        raise FileNotFoundError(f"❌ Best model file not found at {best_model_path}")

    # Generate deployment path with new timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    deployed_model_path = os.path.join(MODEL_DIR, f"production_model_{timestamp}.joblib")

    # Backup old production model
    old_model_path = os.path.join(MODEL_DIR, "production_model.joblib")
    if os.path.exists(old_model_path):
        backup_path = os.path.join(MODEL_DIR, f"production_model_backup_{timestamp}.joblib")
        shutil.copy(old_model_path, backup_path)
        print(f"🛡️ Backed up previous production model to {backup_path}")

    # Copy best model to new production location
    shutil.copy(best_model_path, deployed_model_path)
    print(f"✅ New model deployed to {deployed_model_path}")

    # Save deployment metadata
    metadata = {
        "deployed_model_path": deployed_model_path,
        "deployed_at": datetime.now().isoformat(),
        "source_model_path": best_model_path,
        "deployment_reason": "automated pipeline decision"
    }
    with open(os.path.join(MODEL_DIR, "deployment_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print("📝 Saved deployment metadata")

    # Sync new training files from all_data to production_data (append-only)
    ALL_DATA_DIR = "/opt/airflow/all_data"
    PRODUCTION_DATA_DIR = "/opt/airflow/production_data"
    os.makedirs(PRODUCTION_DATA_DIR, exist_ok=True)

    added = 0
    for f in os.listdir(ALL_DATA_DIR):
        if f.endswith(".json") and not os.path.exists(os.path.join(PRODUCTION_DATA_DIR, f)):
            shutil.copy(os.path.join(ALL_DATA_DIR, f), os.path.join(PRODUCTION_DATA_DIR, f))
            added += 1

    print(f"📁 Appended {added} new file(s) to production_data/")

    with open(os.path.join(MODEL_DIR, "latest_production_model.txt"), "w") as f:
        f.write(os.path.basename(deployed_model_path))

    # Update symlink to always point to the newest deployed model
    symlink_path = os.path.join(MODEL_DIR, "production_model.joblib")
    if os.path.islink(symlink_path) or os.path.exists(symlink_path):
        os.remove(symlink_path)
    os.symlink(deployed_model_path, symlink_path)
    print(f"🔗 Updated symlink: production_model.joblib → {deployed_model_path}")