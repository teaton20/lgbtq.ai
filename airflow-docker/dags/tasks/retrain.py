import os
import json
import joblib
import torch
import gc
from datetime import datetime
from torch.utils.data import DataLoader
from model_code.model import TripletNet, TripletLoss, get_triplet_dataset
import psutil
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env and connect to MongoDB
load_dotenv(dotenv_path="/opt/airflow/.env")
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["lgbtq-ai_db"]
new_data = db["new_data"]
all_data = db["all_data"]
production_data = db["production_data"]

MODEL_DIR = "/opt/airflow/models"
REVIEW_THRESHOLD = 20

# --------------------------------------------------------

# Training hyperparameters - edit these to your liking!

BATCH_SIZE = 2
NUM_EPOCHS = 1
CHECKPOINT_EVERY = 1  # Save model every n epochs

# --------------------------------------------------------

# Ensure necessary directories exist
os.makedirs(MODEL_DIR, exist_ok=True)

def combine_data():
    """Move new_data articles into all_data if not already present (by uid)."""
    files_moved = 0
    cursor = new_data.find()

    for article in cursor:
        uid = article.get("uid")
        if not uid:
            continue
        if all_data.find_one({"uid": uid}):
            print(f"⚠️ Skipping duplicate article with uid {uid}")
            continue
        all_data.insert_one(article)
        new_data.delete_one({"_id": article["_id"]})
        files_moved += 1

    return files_moved

def load_data():
    """Load 'content' and 'true_label' fields from all_data for training."""
    texts, labels = [], []
    for doc in all_data.find({"content": {"$exists": True}, "true_label": {"$exists": True}}):
        texts.append(doc["content"])
        labels.append(doc["true_label"])
    return texts, labels

def cleanup_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    elif torch.backends.mps.is_available():
        pass

def train_triplet_model():
    print("📦 Combining data...")

    # Remove old retrained flag if exists
    flag_path = os.path.join(MODEL_DIR, "retrained_flag.txt")
    if os.path.exists(flag_path):
        os.remove(flag_path)

    count_before = new_data.count_documents({})
    print(f"🧮 new_data documents before move: {count_before}")

    files_moved = combine_data()

    if files_moved < REVIEW_THRESHOLD:
        print(f"⏹️ Not enough new data to retrain (moved {files_moved}/{REVIEW_THRESHOLD}).")
        return "not_enough_data"

    print("📚 Loading labeled data...")
    texts, labels = load_data()

    print(f"🧠 Initial memory usage: {psutil.virtual_memory().percent}%")
    print("🧠 Preparing triplet training data...")
    triplet_dataset = get_triplet_dataset(texts, labels)

    del texts, labels
    cleanup_memory()

    dataloader = DataLoader(
        triplet_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=True,
        pin_memory=False
    )

    print("🔍 Loading encoder from local cache...")
    model = TripletNet()

    if torch.cuda.is_available():
        device = torch.device('cuda')
        torch.backends.cudnn.benchmark = False
    elif torch.backends.mps.is_available():
        device = torch.device('mps')
    else:
        device = torch.device('cpu')

    print(f"🖥️ Using device: {device}")
    model.to(device)
    model.train()

    GRAD_ACCUMULATION_STEPS = 4
    effective_batch_size = BATCH_SIZE * GRAD_ACCUMULATION_STEPS
    print(f"📊 Using gradient accumulation: effective batch size = {effective_batch_size}")

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = TripletLoss()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    print("🚀 Training triplet model...")
    for epoch in range(NUM_EPOCHS):
        total_loss = 0
        batch_count = 0
        total_batches = len(dataloader)
        last_logged_percent = -1

        for i, batch in enumerate(dataloader):
            percent_done = int((i + 1) * 100 / total_batches)
            bucket = percent_done // 10

            if bucket > last_logged_percent and bucket < 10:
                print(f"📊 Epoch {epoch+1}/{NUM_EPOCHS} — {bucket * 10}% complete ({i+1}/{total_batches} batches)")
                last_logged_percent = bucket

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

            loss = loss_fn(anchor, positive, negative) / GRAD_ACCUMULATION_STEPS
            loss.backward()

            if (i + 1) % GRAD_ACCUMULATION_STEPS == 0 or (i + 1) == total_batches:
                optimizer.step()
                optimizer.zero_grad()
                if (i + 1) % 10 == 0:
                    print(f"🧠 Memory usage: {psutil.virtual_memory().percent}%")
                cleanup_memory()

            total_loss += loss.item() * GRAD_ACCUMULATION_STEPS
            batch_count += 1

            for key in batch:
                for subkey in batch[key]:
                    if device.type != 'cpu':
                        batch[key][subkey] = batch[key][subkey].cpu()

        avg_loss = total_loss / batch_count if batch_count > 0 else 0
        print(f"📈 Epoch {epoch + 1}/{NUM_EPOCHS}: Loss={avg_loss:.4f}")
        print(f"🧠 Memory usage: {psutil.virtual_memory().percent}%")

        if (epoch + 1) % CHECKPOINT_EVERY == 0:
            checkpoint_path = os.path.join(MODEL_DIR, f"checkpoint_model_{timestamp}_epoch{epoch+1}.joblib")
            model.cpu()
            joblib.dump(model.state_dict(), checkpoint_path)
            print(f"💾 Saved checkpoint to {checkpoint_path}")
            model.to(device)
            cleanup_memory()

    model.cpu()
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