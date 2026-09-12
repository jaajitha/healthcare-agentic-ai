# ============================================================
# PATIENT INFORMATION + VITAL SIGNS ASSESSMENT
# ============================================================

print("=" * 70)
print("AGENTIC AI HEALTHCARE - PATIENT ASSESSMENT")
print("=" * 70)


# ------------------------------------------------------------
# 1. PATIENT INFORMATION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PATIENT INFORMATION")
print("=" * 70)

patient_id = input("\nPatient ID: ")
age = int(input("Age: "))

sex = input("Sex (Male/Female/Other): ")

print("\nEnter symptoms separated by commas.")
print("Example: fatigue, vomiting, headache")

symptoms = input("Symptoms: ")


# ------------------------------------------------------------
# 2. VITAL SIGNS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("VITAL SIGNS")
print("=" * 70)

temperature = float(
    input("\nTemperature (°C): ")
)

heart_rate = int(
    input("Heart rate (bpm): ")
)

systolic = int(
    input("Systolic blood pressure (mmHg): ")
)

diastolic = int(
    input("Diastolic blood pressure (mmHg): ")
)

spo2 = float(
    input("SpO2 (%): ")
)


# ------------------------------------------------------------
# 3. MEDICAL HISTORY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MEDICAL HISTORY")
print("=" * 70)

medical_history = input(
    "\nKnown medical conditions "
    "(enter 'None' if none): "
)


# ------------------------------------------------------------
# 4. CURRENT MEDICATIONS
# ------------------------------------------------------------

current_medications = input(
    "\nCurrent medications "
    "(enter 'None' if none): "
)


# ------------------------------------------------------------
# 5. BASIC RISK FLAGS
# ------------------------------------------------------------

risk_flags = []


# Temperature

if temperature >= 39.0:

    risk_flags.append(
        "High temperature detected"
    )

elif temperature < 35.0:

    risk_flags.append(
        "Low temperature detected"
    )


# Heart rate

if heart_rate > 100:

    risk_flags.append(
        "Elevated heart rate detected"
    )

elif heart_rate < 60:

    risk_flags.append(
        "Low heart rate detected"
    )


# Blood pressure

if systolic >= 140 or diastolic >= 90:

    risk_flags.append(
        "Elevated blood pressure detected"
    )

elif systolic < 90 or diastolic < 60:

    risk_flags.append(
        "Low blood pressure detected"
    )


# SpO2

if spo2 < 90:

    risk_flags.append(
        "Low oxygen saturation detected"
    )

elif spo2 < 94:

    risk_flags.append(
        "Reduced oxygen saturation detected"
    )


# ------------------------------------------------------------
# 6. DISPLAY PATIENT SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PATIENT ASSESSMENT SUMMARY")
print("=" * 70)

print("\nPatient ID:", patient_id)
print("Age:", age)
print("Sex:", sex)

print("\nSymptoms:")
print(symptoms)

print("\nVital Signs:")
print("Temperature:", temperature, "°C")
print("Heart Rate:", heart_rate, "bpm")
print(
    "Blood Pressure:",
    f"{systolic}/{diastolic}",
    "mmHg"
)
print("SpO2:", spo2, "%")

print("\nMedical History:")
print(medical_history)

print("\nCurrent Medications:")
print(current_medications)


# ------------------------------------------------------------
# 7. RISK ASSESSMENT RESULT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RISK ASSESSMENT")
print("=" * 70)

if len(risk_flags) == 0:

    print("\n✓ No basic vital-sign risk flags detected.")

else:

    print("\n⚠ Risk flags detected:")

    for flag in risk_flags:

        print("→", flag)


# ------------------------------------------------------------
# 8. SAFETY MESSAGE
# ------------------------------------------------------------

print("\n" + "=" * 70)

print(
    "IMPORTANT: These are basic prototype risk flags, "
    "not medical diagnoses or emergency triage."
)

print(
    "Clinical decisions must be made by a qualified "
    "healthcare professional."
)

print("=" * 70)