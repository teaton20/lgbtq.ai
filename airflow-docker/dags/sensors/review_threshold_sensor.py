from airflow.sensors.python import PythonSensor
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/opt/airflow/.env")
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["lgbtq-ai_db"]
review_queue = db["review_queue"]

def check_review_threshold():
    count = review_queue.count_documents({
        "stance": { "$nin": [None, ""] }
    })
    print(f"🔁 Sensor check: {count} labeled articles found.")
    return count >= 20