import os
import shutil
import json
from datetime import datetime

MODEL_DIR = "/opt/airflow/models"
NEW_MODEL_PATH = os.path.join(MODEL_DIR, "classifier.joblib")
TIMESTAMP = datetime.now().strftime('%Y%m%d%H%M%S')
DEPLOYED_MODEL_PATH = os.path.join(MODEL_DIR, f"production_model_{TIMESTAMP}.joblib")

def run():
    print("🚀 Deploying new model...")

    # Backup old production model if it exists
    old_model_path = os.path.join(MODEL_DIR, "production_model.joblib")
    if os.path.exists(old_model_path):
        backup_path = os.path.join(
            MODEL_DIR, f"production_model_backup_{TIMESTAMP}.joblib"
        )
        shutil.copy(old_model_path, backup_path)
        print(f"🛡️ Backed up previous production model to {backup_path}")

    # Copy new model into timestamped production path
    shutil.copy(NEW_MODEL_PATH, DEPLOYED_MODEL_PATH)
    print(f"✅ New model deployed to {DEPLOYED_MODEL_PATH}")

    # Save deployment metadata
    metadata = {
        "deployed_model_path": DEPLOYED_MODEL_PATH,
        "deployed_at": datetime.now().isoformat(),
        "source_model_path": NEW_MODEL_PATH,
        "deployment_reason": "automated pipeline decision"
    }

    metadata_path = os.path.join(MODEL_DIR, "deployment_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"📝 Saved deployment metadata to {metadata_path}")