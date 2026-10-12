import pickle
import pandas as pd

MODEL = "models/random_forest_model.pkl"
ENCODER = "data/processed/label_encoder.pkl"
FEATURES = "data/processed/feature_columns.pkl"

# Load model
with open(MODEL, "rb") as f:
    model = pickle.load(f)

with open(ENCODER, "rb") as f:
    encoder = pickle.load(f)

with open(FEATURES, "rb") as f:
    feature_columns = pickle.load(f)

# Load processed data
X = pd.read_csv("data/processed/X_processed.csv")

# Take one patient from the dataset
patient = X.iloc[[0]][feature_columns]

# Predict
prediction = model.predict(patient)[0]
probabilities = model.predict_proba(patient)[0]

disease = encoder.inverse_transform([prediction])[0]
confidence = probabilities.max() * 100

print("\n==============================")
print("AGENTIC AI PATIENT PREDICTION")
print("==============================")
print("Predicted disease:", disease)
print(f"Confidence: {confidence:.2f}%")