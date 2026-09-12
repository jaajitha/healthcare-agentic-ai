import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from xgboost import XGBClassifier

import joblib


# ============================================================
# MACHINE LEARNING MODEL TRAINING
# ============================================================

print("=" * 70)
print("MACHINE LEARNING MODEL TRAINING")
print("=" * 70)


# ------------------------------------------------------------
# 1. LOAD PROCESSED DATA
# ------------------------------------------------------------

df = pd.read_csv(
    "data/processed/unique_training_data.csv"
)

print("\n1. DATASET")
print("-" * 50)

print("Dataset shape:", df.shape)


# ------------------------------------------------------------
# 2. SEPARATE FEATURES AND TARGET
# ------------------------------------------------------------

X = df.drop(columns=["prognosis"])

y = df["prognosis"]

print("\n2. FEATURES AND TARGET")
print("-" * 50)

print("Number of features:", X.shape[1])
print("Number of classes:", y.nunique())


# ------------------------------------------------------------
# 3. ENCODE DISEASE LABELS
# ------------------------------------------------------------

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

print("\n3. LABEL ENCODING")
print("-" * 50)

print("Classes:", len(label_encoder.classes_))

# Display mapping
for i, disease in enumerate(label_encoder.classes_):
    print(i, "->", disease)


# ------------------------------------------------------------
# 4. TRAIN / VALIDATION SPLIT
# ------------------------------------------------------------

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)

print("\n4. TRAIN / VALIDATION SPLIT")
print("-" * 50)

print("Training samples  :", X_train.shape[0])
print("Validation samples:", X_val.shape[0])


# ------------------------------------------------------------
# 5. RANDOM FOREST
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRAINING RANDOM FOREST")
print("=" * 70)

rf_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

rf_predictions = rf_model.predict(X_val)

rf_accuracy = accuracy_score(
    y_val,
    rf_predictions
)

print("\nRandom Forest Accuracy:",
      round(rf_accuracy * 100, 2), "%")


# ------------------------------------------------------------
# 6. XGBOOST
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRAINING XGBOOST")
print("=" * 70)

xgb_model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softprob",
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)

xgb_model.fit(
    X_train,
    y_train
)

xgb_predictions = xgb_model.predict(X_val)

xgb_accuracy = accuracy_score(
    y_val,
    xgb_predictions
)

print("\nXGBoost Accuracy:",
      round(xgb_accuracy * 100, 2), "%")


# ------------------------------------------------------------
# 7. MODEL COMPARISON
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print("\nRandom Forest :", round(rf_accuracy * 100, 2), "%")
print("XGBoost       :", round(xgb_accuracy * 100, 2), "%")


if xgb_accuracy >= rf_accuracy:
    best_model = xgb_model
    best_model_name = "XGBoost"
    best_predictions = xgb_predictions
else:
    best_model = rf_model
    best_model_name = "Random Forest"
    best_predictions = rf_predictions


print("\nBest model:", best_model_name)


# ------------------------------------------------------------
# 8. CLASSIFICATION REPORT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

print(
    classification_report(
        y_val,
        best_predictions,
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# ------------------------------------------------------------
# 9. CONFUSION MATRIX
# ------------------------------------------------------------

cm = confusion_matrix(
    y_val,
    best_predictions
)

plt.figure(figsize=(14, 12))

plt.imshow(cm)

plt.title(
    f"Confusion Matrix - {best_model_name}"
)

plt.xlabel("Predicted Disease")
plt.ylabel("Actual Disease")

plt.colorbar()

plt.tight_layout()

plt.savefig(
    "data/processed/confusion_matrix.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# 10. FEATURE IMPORTANCE
# ------------------------------------------------------------

if best_model_name == "Random Forest":

    importance = best_model.feature_importances_

else:

    importance = best_model.feature_importances_


feature_importance = pd.Series(
    importance,
    index=X.columns
).sort_values(
    ascending=False
)


print("\n" + "=" * 70)
print("TOP 20 IMPORTANT SYMPTOMS")
print("=" * 70)

print(
    feature_importance.head(20)
)


# Plot top 20 features

plt.figure(figsize=(12, 7))

feature_importance.head(20).sort_values().plot(
    kind="barh"
)

plt.title(
    f"Top 20 Important Symptoms - {best_model_name}"
)

plt.xlabel("Importance")
plt.ylabel("Symptom")

plt.tight_layout()

plt.savefig(
    "data/processed/feature_importance.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# 11. SAVE MODELS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SAVING MODELS")
print("=" * 70)

joblib.dump(
    rf_model,
    "data/processed/random_forest_model.pkl"
)

joblib.dump(
    xgb_model,
    "data/processed/xgboost_model.pkl"
)

joblib.dump(
    label_encoder,
    "data/processed/label_encoder.pkl"
)

joblib.dump(
    list(X.columns),
    "data/processed/feature_columns.pkl"
)


print("\nSaved:")
print("random_forest_model.pkl")
print("xgboost_model.pkl")
print("label_encoder.pkl")
print("feature_columns.pkl")


# ------------------------------------------------------------
# 12. FINAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MODEL TRAINING COMPLETED")
print("=" * 70)

print("\nRandom Forest Accuracy:",
      round(rf_accuracy * 100, 2), "%")

print("XGBoost Accuracy:",
      round(xgb_accuracy * 100, 2), "%")

print("Best Model:", best_model_name)

print("\nModels are ready for the prediction layer.")