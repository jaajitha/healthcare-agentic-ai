import pandas as pd
import numpy as np

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


# ============================================================
# 5-FOLD STRATIFIED CROSS-VALIDATION
# ============================================================

print("=" * 70)
print("5-FOLD STRATIFIED CROSS-VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv(
    "data/processed/unique_training_data.csv"
)

X = df.drop(columns=["prognosis"])
y = df["prognosis"]


print("\n1. DATASET")
print("-" * 50)

print("Samples :", len(X))
print("Features:", X.shape[1])
print("Classes :", y.nunique())


# ------------------------------------------------------------
# 2. ENCODE TARGET
# ------------------------------------------------------------

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)


# ------------------------------------------------------------
# 3. CREATE 5 STRATIFIED FOLDS
# ------------------------------------------------------------

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


# ------------------------------------------------------------
# 4. RANDOM FOREST
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RANDOM FOREST - 5-FOLD CROSS-VALIDATION")
print("=" * 70)

rf_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

rf_scores = cross_val_score(
    rf_model,
    X,
    y_encoded,
    cv=cv,
    scoring="accuracy",
    n_jobs=-1
)

print("\nFold accuracies:")

for i, score in enumerate(rf_scores, start=1):
    print(f"Fold {i}: {score * 100:.2f}%")

rf_mean = rf_scores.mean()
rf_std = rf_scores.std()

print("\nRandom Forest Results")
print("-" * 50)

print(f"Mean Accuracy: {rf_mean * 100:.2f}%")
print(f"Std Deviation: ±{rf_std * 100:.2f}%")


# ------------------------------------------------------------
# 5. XGBOOST
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("XGBOOST - 5-FOLD CROSS-VALIDATION")
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

xgb_scores = cross_val_score(
    xgb_model,
    X,
    y_encoded,
    cv=cv,
    scoring="accuracy",
    n_jobs=-1
)

print("\nFold accuracies:")

for i, score in enumerate(xgb_scores, start=1):
    print(f"Fold {i}: {score * 100:.2f}%")

xgb_mean = xgb_scores.mean()
xgb_std = xgb_scores.std()

print("\nXGBoost Results")
print("-" * 50)

print(f"Mean Accuracy: {xgb_mean * 100:.2f}%")
print(f"Std Deviation: ±{xgb_std * 100:.2f}%")


# ------------------------------------------------------------
# 6. MODEL COMPARISON
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL MODEL COMPARISON")
print("=" * 70)

print(
    f"\nRandom Forest: {rf_mean * 100:.2f}% "
    f"± {rf_std * 100:.2f}%"
)

print(
    f"XGBoost      : {xgb_mean * 100:.2f}% "
    f"± {xgb_std * 100:.2f}%"
)


if rf_mean >= xgb_mean:

    print("\nRecommended ML Model: Random Forest")

else:

    print("\nRecommended ML Model: XGBoost")


print("\n" + "=" * 70)
print("CROSS-VALIDATION COMPLETED")
print("=" * 70)