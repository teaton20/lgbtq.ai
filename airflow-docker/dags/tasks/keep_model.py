import os

MODEL_DIR = "/opt/airflow/models"
METADATA_PATH = os.path.join(MODEL_DIR, "deployment_metadata.json")

def run():
    print("🛑 No model deployed. Cleaning up metadata if it exists.")
    if os.path.exists(METADATA_PATH):
        os.remove(METADATA_PATH)
        print("🧹 Removed stale deployment metadata.")
    else:
        print("🕳️ No deployment metadata to clean up.")