import pandas as pd

# ==========================================
# LOAD DATA
# ==========================================

train_df = pd.read_csv("data/Training.csv")
test_df = pd.read_csv("data/Testing.csv")

print("=" * 70)
print("DUPLICATE & DATASET STRUCTURE INVESTIGATION")
print("=" * 70)


# ==========================================
# 1. REMOVE ONLY THE EMPTY COLUMN FOR ANALYSIS
# ==========================================

train_clean_view = train_df.drop(columns=["Unnamed: 133"])

print("\n1. DATASET AFTER REMOVING EMPTY COLUMN")
print("-" * 50)

print("Shape:", train_clean_view.shape)


# ==========================================
# 2. COMPLETE ROW DUPLICATES
# ==========================================

print("\n2. COMPLETE ROW DUPLICATES")
print("-" * 50)

print("Total rows:", len(train_clean_view))
print("Duplicate rows:", train_clean_view.duplicated().sum())
print("Unique complete rows:", train_clean_view.drop_duplicates().shape[0])


# ==========================================
# 3. UNIQUE SYMPTOM PATTERNS
# ==========================================

print("\n3. UNIQUE SYMPTOM PATTERNS")
print("-" * 50)

feature_columns = [
    col for col in train_clean_view.columns
    if col != "prognosis"
]

unique_symptom_patterns = train_clean_view[
    feature_columns
].drop_duplicates()

print("Total symptom patterns:",
      len(unique_symptom_patterns))


# ==========================================
# 4. DUPLICATES BASED ONLY ON SYMPTOMS
# ==========================================

print("\n4. SYMPTOM-ONLY DUPLICATES")
print("-" * 50)

symptom_duplicates = train_clean_view[
    feature_columns
].duplicated().sum()

print("Duplicate symptom patterns:",
      symptom_duplicates)

print("Unique symptom patterns:",
      len(train_clean_view) - symptom_duplicates)


# ==========================================
# 5. UNIQUE PATTERNS PER DISEASE
# ==========================================

print("\n5. UNIQUE SYMPTOM PATTERNS PER DISEASE")
print("-" * 50)

patterns_per_disease = (
    train_clean_view
    .groupby("prognosis")[feature_columns]
    .apply(lambda x: len(x.drop_duplicates()))
    .sort_values()
)

print(patterns_per_disease)


# ==========================================
# 6. MOST REPEATED SYMPTOM PATTERNS
# ==========================================

print("\n6. MOST REPEATED SYMPTOM PATTERNS")
print("-" * 50)

pattern_counts = (
    train_clean_view
    .groupby(feature_columns, dropna=False)
    .size()
    .sort_values(ascending=False)
)

print("Top 20 repeated patterns:")

print(pattern_counts.head(20))


# ==========================================
# 7. CHECK WHETHER SAME SYMPTOM PATTERN
#    HAS MULTIPLE DISEASE LABELS
# ==========================================

print("\n7. SAME SYMPTOMS WITH DIFFERENT DISEASES")
print("-" * 50)

pattern_disease_counts = (
    train_clean_view
    .groupby(feature_columns)["prognosis"]
    .nunique()
)

ambiguous_patterns = pattern_disease_counts[
    pattern_disease_counts > 1
]

print("Symptom patterns associated with multiple diseases:",
      len(ambiguous_patterns))


# ==========================================
# 8. TRAIN / TEST OVERLAP
# ==========================================

print("\n8. TRAIN / TEST OVERLAP")
print("-" * 50)

test_clean_view = test_df.copy()

test_features = [
    col for col in test_clean_view.columns
    if col != "prognosis"
]

train_patterns = set(
    train_clean_view[feature_columns]
    .apply(tuple, axis=1)
)

test_patterns = set(
    test_clean_view[test_features]
    .apply(tuple, axis=1)
)

overlap = train_patterns.intersection(test_patterns)

print("Unique training symptom patterns:",
      len(train_patterns))

print("Unique testing symptom patterns:",
      len(test_patterns))

print("Patterns appearing in BOTH:",
      len(overlap))


# ==========================================
# 9. TESTING DISEASE DISTRIBUTION
# ==========================================

print("\n9. TESTING DISEASE DISTRIBUTION")
print("-" * 50)

print(test_df["prognosis"].value_counts())


print("\n" + "=" * 70)
print("INVESTIGATION COMPLETED")
print("=" * 70)