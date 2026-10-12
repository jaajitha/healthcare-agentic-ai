import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# ==========================================
# LOAD PROCESSED DATA
# ==========================================

X = pd.read_csv(
    "data/processed/X_processed.csv"
)

y_df = pd.read_csv(
    "data/processed/y_processed.csv"
)

y = y_df["encoded"]

label_encoder = joblib.load(
    "data/processed/label_encoder.pkl"
)

# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# ==========================================
# RANDOM FOREST
# ==========================================

rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

print("\nTraining Random Forest...")

rf_model.fit(
    X_train,
    y_train
)

# ==========================================
# PREDICTION
# ==========================================

y_pred = rf_model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n================================")
print("RANDOM FOREST RESULTS")
print("================================")

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_
    )
)

# ==========================================
# SAVE MODEL
# ==========================================

os.makedirs("models", exist_ok=True)

joblib.dump(
    rf_model,
    "models/random_forest_model.pkl"
)

print("\nModel saved:")
print("models/random_forest_model.pkl")