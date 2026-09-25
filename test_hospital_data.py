from hospital_client import (
    get_hospital,
    get_departments,
    get_doctors,
    get_services,
    get_doctors_by_speciality,
    get_hospital_profile
)


print("\n" + "=" * 60)
print("APOLLO ARAGONDA HOSPITAL DATA TEST")
print("=" * 60)


# ------------------------------------------------------------
# HOSPITAL
# ------------------------------------------------------------

hospital = get_hospital()

print("\n🏥 HOSPITAL")
print("-" * 60)

if hospital:
    print("Name:", hospital["name"])
    print("Type:", hospital["hospital_type"])
    print("Beds:", hospital["beds"])
    print("Address:", hospital["address"])
    print("Phone:", hospital["phone"])
    print("Emergency:", hospital["emergency_available"])
    print("Telemedicine:", hospital["telemedicine_available"])
else:
    print("Hospital not found.")


# ------------------------------------------------------------
# DEPARTMENTS
# ------------------------------------------------------------

departments = get_departments()

print("\n🩺 DEPARTMENTS / SPECIALITIES")
print("-" * 60)

for department in departments:
    print("•", department["department_name"])


# ------------------------------------------------------------
# DOCTORS
# ------------------------------------------------------------

doctors = get_doctors()

print("\n👨‍⚕️ DOCTORS")
print("-" * 60)

for doctor in doctors:
    print("\nName:", doctor["name"])
    print("Speciality:", doctor["speciality"])
    print("Experience:", doctor["experience_years"], "years")
    print("Qualifications:", doctor["qualifications"])
    print("Languages:", doctor["languages"])
    print("Hours:", doctor["consultation_hours"])


# ------------------------------------------------------------
# DOCTORS BY SPECIALITY
# ------------------------------------------------------------

orthopedic_doctors = get_doctors_by_speciality("Orthopedics")

print("\n🦴 ORTHOPEDICS DOCTORS")
print("-" * 60)

for doctor in orthopedic_doctors:
    print("•", doctor["name"])


# ------------------------------------------------------------
# SERVICES
# ------------------------------------------------------------

services = get_services()

print("\n🏥 HOSPITAL SERVICES")
print("-" * 60)

for service in services:
    status = "24×7" if service["available_24x7"] else "Available"

    print(
        f"• {service['service_name']} ({status})"
    )


# ------------------------------------------------------------
# COMPLETE PROFILE
# ------------------------------------------------------------

profile = get_hospital_profile()

print("\n" + "=" * 60)
print("PROFILE SUMMARY")
print("=" * 60)

if profile:
    print(
        "Hospital:",
        profile["hospital"]["name"]
    )

    print(
        "Departments:",
        len(profile["departments"])
    )

    print(
        "Doctors:",
        len(profile["doctors"])
    )

    print(
        "Services:",
        len(profile["services"])
    )

print("\n✅ Hospital data test completed.")