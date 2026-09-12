import pandas as pd
from pathlib import Path

# ==========================================
# AGENTIC AI HEALTHCARE
# DATA CLEANING & PREPROCESSING
# ==========================================

print("=" * 70)
print("DATA CLEANING & PREPROCESSING")
print("=" * 70)


# ==========================================
# 1. LOAD RAW DATA
# ==========================================

train_path = "data/Training.csv"
test_path = "data/Testing.csv"

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

print("\n1. RAW DATA")
print("-" * 50)

print("Training shape:", train_df.shape)
print("Testing shape :", test_df.shape)


# ==========================================
# 2. REMOVE UNNAMED COLUMN
# ==========================================

train_df = train_df.drop(
    columns=["Unnamed: 133"],
    errors="ignore"
)

test_df = test_df.drop(
    columns=["Unnamed: 133"],
    errors="ignore"
)

print("\n2. AFTER REMOVING UNNAMED COLUMN")
print("-" * 50)

print("Training shape:", train_df.shape)
print("Testing shape :", test_df.shape)


# ==========================================
# 3. SEPARATE FEATURES AND TARGET
# ==========================================

target_column = "prognosis"

feature_columns = [
    column for column in train_df.columns
    if column != target_column
]

X = train_df[feature_columns]
y = train_df[target_column]

print("\n3. FEATURES AND TARGET")
print("-" * 50)

print("Number of features:", len(feature_columns))
print("Target column:", target_column)


# ==========================================
# 4. CHECK MISSING VALUES
# ==========================================

print("\n4. MISSING VALUES")
print("-" * 50)

print("Missing values in X:", X.isnull().sum().sum())
print("Missing values in y:", y.isnull().sum())


# ==========================================
# 5. REMOVE DUPLICATE SYMPTOM PATTERNS
# ==========================================

print("\n5. DUPLICATE REMOVAL")
print("-" * 50)

before = len(train_df)

# Remove duplicate rows based ONLY on symptoms.
# This keeps one copy of each unique symptom pattern.

unique_df = train_df.drop_duplicates(
    subset=feature_columns,
    keep="first"
).copy()

after = len(unique_df)

print("Rows before removing duplicates:", before)
print("Rows after removing duplicates :", after)
print("Rows removed                   :", before - after)


# ==========================================
# 6. VERIFY LABEL CONSISTENCY
# ==========================================

print("\n6. LABEL CONSISTENCY CHECK")
print("-" * 50)

# Check whether identical symptom patterns
# have different disease labels.

label_counts = (
    train_df
    .groupby(feature_columns)["prognosis"]
    .nunique()
)

conflicting_patterns = label_counts[
    label_counts > 1
]

print(
    "Conflicting symptom patterns:",
    len(conflicting_patterns)
)

if len(conflicting_patterns) == 0:
    print("✓ Every symptom pattern has one disease label.")
else:
    print("⚠ Conflicting labels found.")


# ==========================================
# 7. CHECK FEATURE VALUES
# ==========================================

print("\n7. FEATURE VALUE CHECK")
print("-" * 50)

unique_feature_values = set()

for column in feature_columns:
    unique_feature_values.update(
        train_df[column].dropna().unique()
    )

print(
    "Unique values in symptom features:",
    sorted(unique_feature_values)
)


# ==========================================
# 8. CLASS DISTRIBUTION AFTER DEDUPLICATION
# ==========================================

print("\n8. CLASS DISTRIBUTION AFTER DEDUPLICATION")
print("-" * 50)


print(
    unique_df["prognosis"].value_counts().sort_index()
)


# ==========================================
# 9. SAVE PROCESSED DATASET
# ==========================================

output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "unique_training_data.csv"

unique_df.to_csv(
    output_path,
    index=False
)

print("\n9. SAVED DATASET")
print("-" * 50)

print("Saved to:", output_path)
print("Final shape:", unique_df.shape)


# ==========================================
# 10. SAVE FEATURE LIST
# ==========================================

feature_list_path = output_dir / "feature_columns.txt"

with open(feature_list_path, "w", encoding="utf-8") as file:
    for feature in feature_columns:
        file.write(feature + "\n")

print("Feature list saved to:", feature_list_path)


print("\n" + "=" * 70)
print("PREPROCESSING COMPLETED SUCCESSFULLY")
print("=" * 70)