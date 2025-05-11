import os
import json
import shutil
import joblib
import numpy as np
from datetime import datetime

# This script is solely for making sure that retrain and get_metrics are 
# correctly working together and that transfer logic is sound.

# Test-friendly local paths
BASE_DIR = os.path.abspath("test_outputs")  # Use a folder inside your project
MODEL_DIR = os.path.join(BASE_DIR, "models")
METRICS_DIR = os.path.join(BASE_DIR, "metrics")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(METRICS_DIR, exist_ok=True)

def fake_model(loss_val):
    # Create a fake model state dict with some numpy weight arrays
    return {"fc.weight": np.random.rand(768, 768) * loss_val}

def simulate_retrain():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Simulate 3 epochs with decreasing loss
    losses = [0.7, 0.5, 0.6]
    best_idx = int(np.argmin(losses)) + 1
    best_loss = min(losses)

    for i, loss in enumerate(losses):
        model_state = fake_model(loss)
        fname = f"checkpoint_model_{timestamp}_epoch{i+1}.joblib"
        path = os.path.join(MODEL_DIR, fname)
        joblib.dump(model_state, path)
        print(f"💾 Wrote fake checkpoint: {fname} (loss={loss})")

    best_model_fname = f"production_model_{timestamp}_epoch{best_idx}_best.joblib"
    best_model_path = os.path.join(MODEL_DIR, best_model_fname)
    joblib.dump(fake_model(best_loss), best_model_path)
    print(f"🏆 Wrote best model: {best_model_fname} (loss={best_loss})")

    # Simulate writing retrained flag and model pointer
    with open(os.path.join(MODEL_DIR, "retrained_flag.txt"), "w") as f:
        f.write(best_model_path)
    with open(os.path.join(MODEL_DIR, "best_candidate_model.txt"), "w") as f:
        f.write(best_model_fname)

    return best_model_fname

def simulate_previous_backup():
    fname = "production_model_backup_prev.joblib"
    fpath = os.path.join(MODEL_DIR, fname)
    joblib.dump(fake_model(0.65), fpath)
    print(f"🧾 Wrote fake previous model backup: {fname}")
    return fname

def simulate_get_metrics(new_model_name, prev_model_name):
    print("🔍 Simulating get_metrics...")

    # Simulate evaluation logic by encoding accuracy as inverse of "loss"
    def mock_accuracy_from_filename(name):
        loss = float(name.split("_")[-2].replace("epoch", "")) * 0.1
        return 1.0 - loss

    new_acc = mock_accuracy_from_filename(new_model_name)
    prev_acc = 0.35  # Simulated score

    best_model = new_model_name if new_acc >= prev_acc else prev_model_name

    with open(os.path.join(METRICS_DIR, "model_metrics.json"), "w") as f:
        json.dump({
            "best_model": best_model,
            "new_model": new_model_name,
            "prev_model": prev_model_name,
            "new_accuracy": new_acc,
            "prev_accuracy": prev_acc,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)

    print(f"✅ Best model selected: {best_model}")
    return best_model

def run_test():
    print("\n=== SIMULATED DAG PIPELINE TEST ===\n")

    prev_model = simulate_previous_backup()
    best_candidate = simulate_retrain()
    selected_model = simulate_get_metrics(best_candidate, prev_model)

    print("\n🎉 DAG logic test complete!\n")
    print("👉 Files to verify:")
    print(f"• {os.path.join(MODEL_DIR, 'best_candidate_model.txt')}")
    print(f"• {os.path.join(METRICS_DIR, 'model_metrics.json')}")

if __name__ == "__main__":
    run_test()