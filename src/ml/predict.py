import pandas as pd
import joblib


# ============================================================
# DISEASE PREDICTION + CONFIDENCE CHECK
# ============================================================

print("=" * 70)
print("AGENTIC AI HEALTHCARE - DISEASE PREDICTION")
print("=" * 70)


# ------------------------------------------------------------
# 1. LOAD MODEL
# ------------------------------------------------------------

model = joblib.load(
    "data/processed/random_forest_model.pkl"
)

label_encoder = joblib.load(
    "data/processed/label_encoder.pkl"
)

feature_columns = joblib.load(
    "data/processed/feature_columns.pkl"
)

print("\nModel loaded successfully.")


# ------------------------------------------------------------
# 2. GET SYMPTOMS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("ENTER PATIENT SYMPTOMS")
print("=" * 70)

print("\nEnter symptoms separated by commas.")
print("Example:")
print("fatigue, vomiting, nausea, abdominal_pain")

user_input = input("\nSymptoms: ")


# ------------------------------------------------------------
# 3. CLEAN INPUT
# ------------------------------------------------------------

entered_symptoms = [
    symptom.strip().lower().replace(" ", "_")
    for symptom in user_input.split(",")
    if symptom.strip()
]


# ------------------------------------------------------------
# 4. VALIDATE SYMPTOMS
# ------------------------------------------------------------

valid_symptoms = []
invalid_symptoms = []

for symptom in entered_symptoms:

    if symptom in feature_columns:
        valid_symptoms.append(symptom)
    else:
        invalid_symptoms.append(symptom)


if invalid_symptoms:

    print("\n⚠ Symptoms not recognized:")

    for symptom in invalid_symptoms:
        print("-", symptom)


if not valid_symptoms:

    print("\nNo valid symptoms entered.")
    print("Please run the program again.")

    exit()


# ------------------------------------------------------------
# 5. CREATE INPUT VECTOR
# ------------------------------------------------------------

input_data = pd.DataFrame(
    0,
    index=[0],
    columns=feature_columns
)

for symptom in valid_symptoms:
    input_data.loc[0, symptom] = 1


# ------------------------------------------------------------
# 6. PREDICTION
# ------------------------------------------------------------

prediction = model.predict(input_data)[0]

predicted_disease = label_encoder.inverse_transform(
    [prediction]
)[0]


# ------------------------------------------------------------
# 7. PROBABILITIES
# ------------------------------------------------------------

probabilities = model.predict_proba(input_data)[0]

top_indices = probabilities.argsort()[-5:][::-1]

top_probability = probabilities[top_indices[0]]


# ------------------------------------------------------------
# 8. CONFIDENCE LEVEL
# ------------------------------------------------------------

if top_probability >= 0.70:

    confidence_level = "HIGH"

elif top_probability >= 0.40:

    confidence_level = "MODERATE"

else:

    confidence_level = "LOW"


# ------------------------------------------------------------
# 9. DISPLAY RESULT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PREDICTION RESULT")
print("=" * 70)

print("\nEntered symptoms:")

for symptom in valid_symptoms:
    print("✓", symptom)


print("\nPredicted Disease:")
print(">>>", predicted_disease)


print(
    f"\nPrediction Probability: "
    f"{top_probability * 100:.2f}%"
)

print(
    f"Confidence Level: {confidence_level}"
)


# ------------------------------------------------------------
# 10. TOP 5 PREDICTIONS
# ------------------------------------------------------------

print("\nTop 5 Predictions:")
print("-" * 55)

for rank, index in enumerate(top_indices, start=1):

    disease = label_encoder.inverse_transform(
        [index]
    )[0]

    probability = probabilities[index] * 100

    print(
        f"{rank}. {disease:<40} "
        f"{probability:.2f}%"
    )


# ------------------------------------------------------------
# 11. UNCERTAINTY HANDLING
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CLINICAL INFORMATION CHECK")
print("=" * 70)

if confidence_level == "LOW":

    print("\n⚠ LOW CONFIDENCE")

    print(
        "The available symptom information is insufficient "
        "for a confident prediction."
    )

    print("\nRecommended next step:")

    print("→ Collect additional symptoms")
    print("→ Check patient vital signs")
    print("→ Review medical history")
    print("→ Review current medications")
    print("→ Perform appropriate clinical evaluation")


elif confidence_level == "MODERATE":

    print("\n⚠ MODERATE CONFIDENCE")

    print(
        "Additional patient information should be "
        "considered before clinical interpretation."
    )

    print("\nRecommended next step:")

    print("→ Collect vital signs")
    print("→ Review medical history")
    print("→ Review current medications")


else:

    print("\n✓ HIGH MODEL CONFIDENCE")

    print(
        "The model has a high prediction probability "
        "for the selected disease."
    )

    print(
        "Further clinical evaluation is still required."
    )


# ------------------------------------------------------------
# 12. SAFETY MESSAGE
# ------------------------------------------------------------

print("\n" + "=" * 70)

print(
    "IMPORTANT: This system is a decision-support prototype "
    "and does not replace evaluation or diagnosis by a "
    "qualified healthcare professional."
)

print("=" * 70)