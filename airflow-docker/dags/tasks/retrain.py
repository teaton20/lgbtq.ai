# Import the optimized retrain.py content here
import os
import shutil
import json
import joblib
import torch
import numpy as np
import gc
from datetime import datetime
from torch.utils.data import DataLoader
from model_code.model import TripletNet, TripletLoss, get_triplet_dataset
import psutil  # for memory diagnostics
from tqdm.auto import tqdm as notebook_tqdm
from airflow.exceptions import AirflowSkipException

# Directory paths
PRODUCTION_DATA_DIR = "/opt/airflow/production_data"
NEW_DATA_DIR = "/opt/airflow/new_data"
ALL_DATA_DIR = "/opt/airflow/all_data"
MODEL_DIR = "/opt/airflow/models"
REVIEW_THRESHOLD = 5

# Training hyperparameters
BATCH_SIZE = 2
NUM_EPOCHS = 1
CHECKPOINT_EVERY = 1  # Save model every N epochs

# Ensure necessary directories exist
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(ALL_DATA_DIR, exist_ok=True)

def combine_data():
    """Merge production and new data into ALL_DATA_DIR, deduplicating on article_id."""
    files_moved = 0

    for f in os.listdir(PRODUCTION_DATA_DIR):
        if f.endswith(".json"):
            shutil.copy(os.path.join(PRODUCTION_DATA_DIR, f), os.path.join(ALL_DATA_DIR, f))

    for f in os.listdir(NEW_DATA_DIR):
        if f.endswith(".json"):
            article_id = f.split("_")[1]
            if any(existing.startswith(f"article_{article_id}_") for existing in os.listdir(ALL_DATA_DIR)):
                print(f"⚠️ Skipping duplicate article_{article_id}")
                continue
            shutil.move(os.path.join(NEW_DATA_DIR, f), os.path.join(ALL_DATA_DIR, f))
            files_moved += 1

    return files_moved

def load_data():
    """Load content and true_label fields from articles."""
    texts, labels = [], []
    for f in os.listdir(ALL_DATA_DIR):
        if f.endswith(".json"):
            with open(os.path.join(ALL_DATA_DIR, f)) as file:
                data = json.load(file)
                if "content" in data and "true_label" in data:
                    texts.append(data["content"])
                    labels.append(data["true_label"])
    return texts, labels

def cleanup_memory():
    """Force garbage collection and clear CUDA cache if available"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    elif torch.backends.mps.is_available():
        # No explicit cleaning for MPS, but gc should help
        pass

def train_triplet_model():
    print("📦 Combining data...")

    # Remove old retrained flag at the start
    flag_path = os.path.join(MODEL_DIR, "retrained_flag.txt")
    if os.path.exists(flag_path):
        os.remove(flag_path)

    files_moved = combine_data()

    if files_moved == 0:
        print("⏭️ No new labeled data to retrain on.")
        return "no_new_data"

    print("📚 Loading labeled data...")
    texts, labels = load_data()
    if len(texts) < REVIEW_THRESHOLD:
        print(f"⏹️ Not enough total data to retrain (found {len(texts)} items).")
        return "not_enough_data"

    # Print memory usage
    print(f"🧠 Initial memory usage: {psutil.virtual_memory().percent}%")
    
    print("🧠 Preparing triplet training data...")
    triplet_dataset = get_triplet_dataset(texts, labels)
    
    # Important: Clear references to large data when no longer needed
    del texts
    del labels
    cleanup_memory()
    
    # Use a smaller batch size and more workers for better memory management
    dataloader = DataLoader(
        triplet_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=True,
        pin_memory=False  # Set to True only if using CUDA and have enough memory
    )

    print("🔍 Loading encoder from local cache...")
    model = TripletNet()
    
    # Determine device and optimize memory usage
    if torch.cuda.is_available():
        device = torch.device('cuda')
        # Set to use less memory at the expense of some speed
        torch.backends.cudnn.benchmark = False
    elif torch.backends.mps.is_available():
        device = torch.device('mps')
    else:
        device = torch.device('cpu')
    
    print(f"🖥️ Using device: {device}")
    model.to(device)
    model.train()
    
    # Use gradient accumulation to simulate larger batches without memory impact
    GRAD_ACCUMULATION_STEPS = 4
    effective_batch_size = BATCH_SIZE * GRAD_ACCUMULATION_STEPS
    print(f"📊 Using gradient accumulation: effective batch size = {effective_batch_size}")
    
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = TripletLoss()

    # Create timestamp for model naming
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    print("🚀 Training triplet model...")
    for epoch in range(NUM_EPOCHS):
        total_loss = 0
        batch_count = 0
        total_batches = len(dataloader)
        progress_intervals = 10  # Logs progress 10 times per epoch (10%, 20%, ..., 100%)

        for i, batch in enumerate(dataloader):
            percent_done = int((i + 1) * 100 / total_batches)
            
            # Log only on each X% step
            if percent_done % (100 // progress_intervals) == 0 and (i + 1) != total_batches:
                print(f"📊 Epoch {epoch+1}/{NUM_EPOCHS} — {percent_done}% complete ({i+1}/{total_batches} batches)")

            # Forward pass
            anchor = model(
                batch["anchor"]["input_ids"].squeeze(1),
                batch["anchor"]["attention_mask"].squeeze(1)
            )
            positive = model(
                batch["positive"]["input_ids"].squeeze(1),
                batch["positive"]["attention_mask"].squeeze(1)
            )
            negative = model(
                batch["negative"]["input_ids"].squeeze(1),
                batch["negative"]["attention_mask"].squeeze(1)
            )

            # Loss + optimizer step
            loss = loss_fn(anchor, positive, negative) / GRAD_ACCUMULATION_STEPS
            loss.backward()

            if (i + 1) % GRAD_ACCUMULATION_STEPS == 0 or (i + 1) == len(dataloader):
                optimizer.step()
                optimizer.zero_grad()
                if (i + 1) % 10 == 0:
                    print(f"🧠 Memory usage: {psutil.virtual_memory().percent}%")
                cleanup_memory()

            total_loss += loss.item() * GRAD_ACCUMULATION_STEPS
            batch_count += 1

            # Free memory
            for key in batch:
                for subkey in batch[key]:
                    if device.type != 'cpu':
                        batch[key][subkey] = batch[key][subkey].cpu()
    
        avg_loss = total_loss / batch_count if batch_count > 0 else 0
        print(f"📈 Epoch {epoch + 1}/{NUM_EPOCHS}: Loss={avg_loss:.4f}")
        print(f"🧠 Memory usage: {psutil.virtual_memory().percent}%")
        
        # Save checkpoint if needed
        if (epoch + 1) % CHECKPOINT_EVERY == 0:
            checkpoint_path = os.path.join(MODEL_DIR, f"checkpoint_model_{timestamp}_epoch{epoch+1}.joblib")
            # Move model to CPU for saving to avoid OOM
            model.cpu()
            joblib.dump(model.state_dict(), checkpoint_path)
            print(f"💾 Saved checkpoint to {checkpoint_path}")
            # Move model back to device
            model.to(device)
            # Clear memory after saving
            cleanup_memory()

    # Save final model
    model.cpu()  # Move to CPU before saving
    model_path = os.path.join(MODEL_DIR, f"production_model_{timestamp}.joblib")
    joblib.dump(model.state_dict(), model_path)
    print(f"✅ Saved final model to {model_path}")

    with open(os.path.join(MODEL_DIR, "retrained_flag.txt"), "w") as f:
        f.write(model_path)

def run(**kwargs):
    try:
        result = train_triplet_model()
        return result if result else "trained"
    except Exception as e:
        print(f"❌ Training failed with error: {str(e)}")
        cleanup_memory()
        return "error"

if __name__ == "__main__":
    run()