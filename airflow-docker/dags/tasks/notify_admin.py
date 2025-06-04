import os
import json

MODEL_DIR = "/opt/airflow/models"
METADATA_PATH = os.path.join(MODEL_DIR, "deployment_metadata.json")

def run():
    print("📣 Running notify_admin task...")

    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r") as f:
            metadata = json.load(f)
        print("💌 Sending email to team...")
        print(f"""
            📢 A new model was deployed!
            🆕 Path:     {metadata['deployed_model_path']}
            📂 Source:   {metadata['source_model_path']}
            🕒 Deployed: {metadata['deployed_at']}
            📝 Reason:   {metadata['deployment_reason']}
        """)
    else:
        print("🕳️ No new model was deployed in this run. Nothing to notify.")

if __name__ == "__main__":
    run()