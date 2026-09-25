import json
import os


# --------------------------------------------------
# Load Medication Knowledge Base
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KNOWLEDGE_FILE = os.path.join(
    BASE_DIR,
    "knowledge",
    "medication_knowledge.json"
)


with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
    MEDICATION_KNOWLEDGE = json.load(file)


# --------------------------------------------------
# Normalize Medication Name
# --------------------------------------------------

def normalize_medication(name):
    """
    Converts medication names into a standard format.
    """

    name = name.strip().lower()

    # Direct medication name
    if name in MEDICATION_KNOWLEDGE:
        return name

    # Check aliases
    for medication, data in MEDICATION_KNOWLEDGE.items():

        aliases = data.get("aliases", [])

        if name in [alias.lower() for alias in aliases]:
            return medication

    return name


# --------------------------------------------------
# Check Medication Interactions
# --------------------------------------------------

def check_medication_interactions(medications):

    normalized_medications = []

    for medication in medications:

        medication = normalize_medication(medication)

        if medication:
            normalized_medications.append(medication)

    # Remove duplicates
    normalized_medications = list(dict.fromkeys(normalized_medications))

    alerts = []

    # Check every medication against every other medication
    for i in range(len(normalized_medications)):

        med1 = normalized_medications[i]

        if med1 not in MEDICATION_KNOWLEDGE:
            continue

        interactions = MEDICATION_KNOWLEDGE[
            med1
        ].get("important_interactions", [])

        for interaction in interactions:

            med2 = normalize_medication(
                interaction["medication"]
            )

            if med2 in normalized_medications:

                alert = {
                    "medication_1": med1,
                    "medication_2": med2,
                    "severity": interaction["severity"],
                    "message": interaction["message"],
                    "action": interaction["action"]
                }

                # Avoid duplicate interaction alerts
                pair = {
                    med1,
                    med2
                }

                already_exists = False

                for existing in alerts:

                    existing_pair = {
                        existing["medication_1"],
                        existing["medication_2"]
                    }

                    if pair == existing_pair:
                        already_exists = True
                        break

                if not already_exists:
                    alerts.append(alert)

    return normalized_medications, alerts


# --------------------------------------------------
# Display Results
# --------------------------------------------------

def display_results(medications, alerts):

    print("\n" + "=" * 60)
    print("MEDICATION INTERACTION SCREENING")
    print("=" * 60)

    print("\nMedications entered:")

    for medication in medications:
        print(f"  - {medication}")

    if not alerts:

        print("\n✓ No interactions found in the current")
        print("  medication knowledge base.")

    else:

        print("\n⚠ POTENTIAL INTERACTIONS FOUND\n")

        for index, alert in enumerate(alerts, start=1):

            print(f"Interaction {index}")
            print("-" * 40)

            print(
                f"Medications: "
                f"{alert['medication_1'].title()} + "
                f"{alert['medication_2'].title()}"
            )

            print(f"Severity: {alert['severity']}")

            print(f"Concern: {alert['message']}")

            print(f"Action: {alert['action']}")

            print()

    print("-" * 60)
    print(
        "Safety note: This module is a medication screening "
        "prototype and does not replace professional clinical review."
    )
    print("=" * 60)


# --------------------------------------------------
# Main Program
# --------------------------------------------------

if __name__ == "__main__":

    print("\nMedication Interaction Checker")

    user_input = input(
        "\nEnter medications separated by commas: "
    )

    medications = user_input.split(",")

    medications, alerts = check_medication_interactions(
        medications
    )

    display_results(medications, alerts)