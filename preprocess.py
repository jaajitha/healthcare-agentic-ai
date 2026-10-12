import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# ==========================================
# LOAD DATA
# ==========================================

FILE = "data/raw/agentic_ai_patient_context_15000.csv.xlsx"

df = pd.read_excel(FILE)

print("Original shape:", df.shape)

# ==========================================
# CLEAN COLUMN NAMES
# ==========================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)

# ==========================================
# HANDLE MISSING VALUES
# ==========================================

text_columns = [
    "medical_history",
    "current_medications",
    "risk_flags",
    "symptoms_text"
]

for col in text_columns:
    df[col] = df[col].fillna("None")

# ==========================================
# GET ALL SYMPTOMS
# ==========================================

all_symptoms = set()

for symptoms in df["symptoms_text"]:

    for symptom in str(symptoms).split(","):

        symptom = symptom.strip()

        if symptom:
            all_symptoms.add(symptom)

all_symptoms = sorted(all_symptoms)

print("Number of symptom features:", len(all_symptoms))

# ==========================================
# CREATE BINARY SYMPTOM FEATURES
# ==========================================

for symptom in all_symptoms:

    df[symptom] = df["symptoms_text"].apply(
        lambda x:
        1 if symptom in [
            s.strip()
            for s in str(x).split(",")
        ]
        else 0
    )

# ==========================================
# ENCODE SEX
# ==========================================

df["sex"] = df["sex"].fillna("Unknown")

sex_mapping = {
    "Male": 0,
    "Female": 1,
    "Other": 2,
    "Unknown": 3
}

df["sex_encoded"] = df["sex"].map(sex_mapping).fillna(3)

# ==========================================
# SELECT FEATURES
# ==========================================

vital_features = [
    "age",
    "sex_encoded",
    "temperature_c",
    "heart_rate_bpm",
    "systolic_bp_mmhg",
    "diastolic_bp_mmhg",
    "spo2_percent"
]

feature_columns = vital_features + all_symptoms

X = df[feature_columns]

y = df["prognosis"]

# ==========================================
# LABEL ENCODE TARGET
# ==========================================

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

# ==========================================
# SAVE
# ==========================================

os.makedirs("data/processed", exist_ok=True)

X.to_csv(
    "data/processed/X_processed.csv",
    index=False
)

pd.DataFrame({
    "prognosis": y,
    "encoded": y_encoded
}).to_csv(
    "data/processed/y_processed.csv",
    index=False
)

joblib.dump(
    label_encoder,
    "data/processed/label_encoder.pkl"
)

joblib.dump(
    feature_columns,
    "data/processed/feature_columns.pkl"
)

print("\nPreprocessing completed.")

print("X shape:", X.shape)
print("Number of classes:", len(label_encoder.classes_))

print("\nClasses:")
for i, disease in enumerate(label_encoder.classes_):
    print(i, disease)