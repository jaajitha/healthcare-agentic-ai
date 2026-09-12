import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# EXPLORATORY DATA ANALYSIS
# ============================================================

print("=" * 70)
print("EXPLORATORY DATA ANALYSIS")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD PROCESSED DATA
# ------------------------------------------------------------

df = pd.read_csv("data/processed/unique_training_data.csv")

print("\n1. DATASET INFORMATION")
print("-" * 50)

print("Dataset shape:", df.shape)

feature_columns = [col for col in df.columns if col != "prognosis"]

print("Number of symptoms/features:", len(feature_columns))
print("Number of diseases:", df["prognosis"].nunique())

# ------------------------------------------------------------
# 2. BASIC STATISTICS
# ------------------------------------------------------------

print("\n2. BASIC STATISTICS")
print("-" * 50)

print("Total unique symptom patterns:", len(df))
print("Total diseases:", df["prognosis"].nunique())

print("\nMissing values:")
print(df.isnull().sum().sum())

# ------------------------------------------------------------
# 3. DISEASE DISTRIBUTION
# ------------------------------------------------------------

print("\n3. DISEASE DISTRIBUTION")
print("-" * 50)

disease_counts = df["prognosis"].value_counts().sort_values(ascending=False)

print(disease_counts)

# ------------------------------------------------------------
# 4. MOST COMMON SYMPTOMS
# ------------------------------------------------------------

print("\n4. MOST COMMON SYMPTOMS")
print("-" * 50)

symptom_counts = df[feature_columns].sum().sort_values(ascending=False)

print("\nTop 20 symptoms:")
print(symptom_counts.head(20))

# ------------------------------------------------------------
# 5. NUMBER OF SYMPTOMS PER PATTERN
# ------------------------------------------------------------

df["number_of_symptoms"] = df[feature_columns].sum(axis=1)

print("\n5. SYMPTOM COUNT PER PATTERN")
print("-" * 50)

print("Minimum symptoms:", df["number_of_symptoms"].min())
print("Maximum symptoms:", df["number_of_symptoms"].max())
print("Average symptoms:", round(df["number_of_symptoms"].mean(), 2))

# ------------------------------------------------------------
# 6. SUMMARY
# ------------------------------------------------------------

print("\n6. SUMMARY")
print("-" * 50)

print("Unique symptom patterns :", len(df))
print("Symptoms/features       :", len(feature_columns))
print("Disease classes          :", df["prognosis"].nunique())
print("Average symptoms/pattern:", round(df["number_of_symptoms"].mean(), 2))

# ============================================================
# VISUALIZATIONS
# ============================================================

# ------------------------------------------------------------
# GRAPH 1 — Disease Distribution
# ------------------------------------------------------------

plt.figure(figsize=(14, 8))

disease_counts.plot(kind="bar")

plt.title("Distribution of Unique Symptom Patterns by Disease")
plt.xlabel("Disease")
plt.ylabel("Number of Unique Patterns")
plt.xticks(rotation=90)
plt.tight_layout()

plt.savefig("data/processed/disease_distribution.png", dpi=300)

plt.show()

# ------------------------------------------------------------
# GRAPH 2 — Top 20 Symptoms
# ------------------------------------------------------------

plt.figure(figsize=(12, 7))

symptom_counts.head(20).sort_values().plot(kind="barh")

plt.title("Top 20 Most Common Symptoms")
plt.xlabel("Number of Patterns")
plt.ylabel("Symptom")

plt.tight_layout()

plt.savefig("data/processed/top_20_symptoms.png", dpi=300)

plt.show()

# ------------------------------------------------------------
# GRAPH 3 — Number of Symptoms per Pattern
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

df["number_of_symptoms"].plot(kind="hist", bins=15)

plt.title("Distribution of Number of Symptoms per Pattern")
plt.xlabel("Number of Symptoms")
plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig("data/processed/symptom_count_distribution.png", dpi=300)

plt.show()

print("\n" + "=" * 70)
print("EDA COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nGraphs saved inside:")
print("data/processed/")