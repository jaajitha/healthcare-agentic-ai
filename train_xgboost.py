import os
import pickle
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier


# ==============================
# PATHS
# ==============================

X_FILE = "data/processed/X_processed.csv"
Y_FILE = "data/processed/y_processed.csv"

MODEL_DIR = "models"
MODEL_FILE = os.path.join(MODEL_DIR, "xgboost_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)


# ==============================
# LOAD DATA
# ==============================

print("Loading processed data...")

X = pd.read_csv(X_FILE)
y = pd.read_csv(Y_FILE).iloc[:, 0]

# Convert disease names to integer labels for XGBoost
from sklearn.preprocessing import LabelEncoder

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

print(f"Number of disease classes: {len(label_encoder.classes_)}")

print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")


# ==============================
# TRAIN / TEST SPLIT
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")


# ==============================
# XGBOOST
# ==============================

print("\nTraining XGBoost...")

model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softprob",
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


# ==============================
# EVALUATION
# ==============================

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\n==============================")
print("XGBOOST RESULTS")
print("==============================")

print(f"Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# ==============================
# SAVE MODEL
# ==============================

with open(MODEL_FILE, "wb") as f:
    pickle.dump(model, f)

print("\nModel saved to:")
print(MODEL_FILE)