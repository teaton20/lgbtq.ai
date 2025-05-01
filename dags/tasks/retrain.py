from metaflow import FlowSpec, step
import os
import json
import shutil
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression

PRODUCTION_DATA_DIR = "/opt/airflow/production_data"
NEW_DATA_DIR = "/opt/airflow/new_data"
ALL_DATA_DIR = "/opt/airflow/all_data"
MODEL_DIR = "/opt/airflow/models"
MODEL_PATH = os.path.join(MODEL_DIR, "classifier.joblib")
TRIGGER_THRESHOLD = 5

class RetrainFlow(FlowSpec):

    @step
    def start(self):
        # Check trigger condition
        self.new_files = [f for f in os.listdir(NEW_DATA_DIR) if f.endswith(".json")]
        if len(self.new_files) != TRIGGER_THRESHOLD:
            print(f"Trigger not met: {len(self.new_files)}/{TRIGGER_THRESHOLD} in new_data.")
            self.do_retrain = False
        else:
            self.do_retrain = True
        self.next(self.combine_data)

    @step
    def combine_data(self):
        if not self.do_retrain:
            print("Skipping combine step.")
            self.next(self.end)
            return

        os.makedirs(ALL_DATA_DIR, exist_ok=True)

        # Copy production data
        for f in os.listdir(PRODUCTION_DATA_DIR):
            if f.endswith(".json"):
                src = os.path.join(PRODUCTION_DATA_DIR, f)
                dst = os.path.join(ALL_DATA_DIR, f)
                if not os.path.exists(dst):
                    shutil.copy(src, dst)

        # Move new data
        for f in os.listdir(NEW_DATA_DIR):
            if f.endswith(".json"):
                src = os.path.join(NEW_DATA_DIR, f)
                dst = os.path.join(ALL_DATA_DIR, f)
                if not os.path.exists(dst):
                    shutil.move(src, dst)

        print("Combined production and new data into all_data.")
        self.next(self.load_data)

    @step
    def load_data(self):
        if not self.do_retrain:
            print("Skipping load_data step.")
            self.next(self.end)
            return

        X = []
        y = []
        for f in os.listdir(ALL_DATA_DIR):
            if f.endswith(".json"):
                with open(os.path.join(ALL_DATA_DIR, f), "r") as file:
                    data = json.load(file)
                if "embedding" in data and "stance_encoded" in data:
                    X.append(data["embedding"])
                    y.append(data["stance_encoded"])
        self.X = np.array(X)
        self.y = np.array(y)
        if len(self.X) == 0:
            print("No data found for retraining.")
            self.do_retrain = False
        self.next(self.retrain_model)

    @step
    def retrain_model(self):
        if not self.do_retrain:
            print("Skipping retrain_model step.")
            self.next(self.end)
            return

        print(f"Retraining classifier on {len(self.X)} samples...")
        os.makedirs(MODEL_DIR, exist_ok=True)
        # Load previous model if exists, else create new
        if os.path.exists(MODEL_PATH):
            print(f"Loading previous model from {MODEL_PATH}")
            classifier = joblib.load(MODEL_PATH)
        else:
            print("No previous model found, creating a new one.")
            classifier = LogisticRegression(max_iter=1000)
        classifier.fit(self.X, self.y)
        joblib.dump(classifier, MODEL_PATH)
        print(f"Saved retrained classifier to {MODEL_PATH}")
        self.next(self.end)

    @step
    def end(self):
        print("Retrain flow complete.")

if __name__ == "__main__":
    RetrainFlow()
