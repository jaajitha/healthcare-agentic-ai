import joblib
import pandas as pd

# ==========================================
# FILE PATHS
# ==========================================

MODEL = "models/random_forest_model.pkl"
ENCODER = "data/processed/label_encoder.pkl"
FEATURES = "data/processed/feature_columns.pkl"
DATA = "data/processed/X_processed.csv"

# ==========================================
# LOAD MODEL
# ==========================================

print("Loading Random Forest model...")

model = joblib.load(MODEL)
label_encoder = joblib.load(ENCODER)

with open(FEATURES, "rb") as f:
    import pickle
    feature_columns = pickle.load(f)

# ==========================================
# LOAD DATA
# ==========================================

X = pd.read_csv(DATA)

print("Dataset loaded:", X.shape)

# ==========================================
# SELECT ONE PATIENT
# ==========================================

patient = X.iloc[[0]][feature_columns]

# ==========================================
# PREDICTION
# ==========================================

prediction = model.predict(patient)[0]

probabilities = model.predict_proba(patient)[0]

disease = label_encoder.inverse_transform([prediction])[0]

confidence = probabilities.max() * 100

# ==========================================
# RESULTS
# ==========================================

print("\n================================")
print("AGENTIC AI PATIENT PREDICTION")
print("================================")

print("Predicted disease:", disease)
print(f"Confidence: {confidence:.2f}%")

# ==========================================
# TOP 3 PREDICTIONS
# ==========================================

top3 = probabilities.argsort()[-3:][::-1]

print("\nTop 3 predictions:")

for index in top3:
    disease_name = label_encoder.inverse_transform([index])[0]
    probability = probabilities[index] * 100

    print(
        f"{disease_name}: {probability:.2f}%"
    )