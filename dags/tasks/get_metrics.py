import os
import json
import numpy as np
import joblib
import mlflow
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

ALL_DATA_DIR = "/opt/airflow/all_data"
MODEL_DIR = "/opt/airflow/models"
METRICS_DIR = "/opt/airflow/metrics"
MODEL_PATH = os.path.join(MODEL_DIR, "classifier.joblib")

def run():
    # Set up MLflow tracking
    mlflow.set_tracking_uri("file:///opt/airflow/mlflow")
    mlflow.set_experiment("stance_classifier")
    
    if not os.path.exists(MODEL_PATH):
        print(f"No model found at {MODEL_PATH}. Cannot compute metrics.")
        return
    
    # Load model
    print(f"Loading model from {MODEL_PATH}")
    classifier = joblib.load(MODEL_PATH)
    
    # Load data for evaluation
    X = []
    y_true = []
    for f in os.listdir(ALL_DATA_DIR):
        if f.endswith(".json"):
            with open(os.path.join(ALL_DATA_DIR, f), "r") as file:
                data = json.load(file)
            if "embedding" in data and "stance_encoded" in data:
                X.append(data["embedding"])
                y_true.append(data["stance_encoded"])
    
    if len(X) == 0:
        print("No data found in all_data directory to evaluate.")
        return
    
    X = np.array(X)
    y_true = np.array(y_true)
    print(f"Evaluating model on {len(X)} samples...")
    
    # Generate predictions
    y_pred = classifier.predict(X)
    
    # Calculate metrics
    cm = confusion_matrix(y_true, y_pred).tolist()
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted')
    recall = recall_score(y_true, y_pred, average='weighted')
    f1 = f1_score(y_true, y_pred, average='weighted')
    
    # Print metrics
    print(f"Confusion Matrix:\n{cm}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    # Save metrics to JSON
    os.makedirs(METRICS_DIR, exist_ok=True)
    timestamp = np.datetime64('now').astype(str).replace(':', '-')
    metrics_file = os.path.join(METRICS_DIR, f"metrics_{timestamp}.json")
    
    metrics_data = {
        "timestamp": timestamp,
        "confusion_matrix": cm,
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "n_samples": int(len(y_true))
    }
    
    with open(metrics_file, "w") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Saved metrics to {metrics_file}")
    
    # Log metrics with MLflow
    with mlflow.start_run():
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1", f1)
        mlflow.log_metric("n_samples", len(y_true))
        
        # Log confusion matrix as a JSON artifact
        cm_path = os.path.join(METRICS_DIR, f"confusion_matrix_{timestamp}.json")
        with open(cm_path, "w") as f:
            json.dump({"confusion_matrix": cm}, f)
        mlflow.log_artifact(cm_path)
        
        # Log model
        mlflow.sklearn.log_model(classifier, "stance_classifier")
        
        print("Logged metrics and model to MLflow")

if __name__ == "__main__":
    run()
