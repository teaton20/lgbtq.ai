import joblib
import numpy as np

# Load the classifier
clf = joblib.load("classifier.joblib")

# Fake embedding (replace with real one later)
example_embedding = np.random.rand(128).reshape(1, -1)  # 384 is typical for MiniLM

# Make a prediction
prediction = clf.predict(example_embedding)

print("✅ Classifier loaded and predicted:")
print("Predicted label:", prediction[0])
