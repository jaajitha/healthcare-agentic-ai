from hospital_routing_agent import (
    route_patient_to_hospital,
    format_routing_result
)


print("\n" + "=" * 60)
print("APOLLO ARAGONDA HOSPITAL ROUTING AGENT TEST")
print("=" * 60)


# ============================================================
# TEST 1 — ORTHOPAEDICS
# ============================================================

print("\n\nTEST 1: ORTHOPAEDICS")
print("-" * 60)

symptoms = [
    "joint_pain",
    "back_pain",
    "difficulty_walking"
]

result = route_patient_to_hospital(
    symptoms=symptoms
)

print(format_routing_result(result))


# ============================================================
# TEST 2 — INTERNAL MEDICINE
# ============================================================

print("\n\nTEST 2: INTERNAL MEDICINE")
print("-" * 60)

symptoms = [
    "fever",
    "vomiting",
    "fatigue"
]

result = route_patient_to_hospital(
    symptoms=symptoms
)

print(format_routing_result(result))


# ============================================================
# TEST 3 — NO MATCHING SPECIALITY
# ============================================================

print("\n\nTEST 3: NO SPECIFIC SPECIALITY")
print("-" * 60)

symptoms = [
    "itching",
    "skin_rash"
]

result = route_patient_to_hospital(
    symptoms=symptoms
)

print(format_routing_result(result))


# ============================================================
# TEST 4 — HOSPITAL INFORMATION
# ============================================================

print("\n\nTEST 4: HOSPITAL INFORMATION")
print("-" * 60)

result = route_patient_to_hospital(
    symptoms=["joint_pain"]
)

if result.get("hospital"):

    hospital = result["hospital"]

    print("Hospital:", hospital["name"])
    print("Type:", hospital["hospital_type"])
    print("Beds:", hospital["beds"])
    print("Emergency:", hospital["emergency_available"])
    print("Telemedicine:", hospital["telemedicine_available"])


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 60)
print("✅ HOSPITAL ROUTING AGENT TEST COMPLETED")
print("=" * 60)