import json
import os


# Find the medical knowledge file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "medical_knowledge.json")


def load_knowledge():
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize(text):
    return text.lower().strip().replace("_", " ").replace("-", " ")


def find_disease(knowledge, disease_name):

    target = normalize(disease_name)

    for disease in knowledge["diseases"]:

        names = [disease["name"]] + disease.get("aliases", [])

        for name in names:

            if normalize(name) == target:
                return disease

    return None


def show_information(disease):

    print("\n" + "=" * 60)
    print("RETRIEVED MEDICAL INFORMATION")
    print("=" * 60)

    print("\nDisease:")
    print(disease["name"])

    print("\nDescription:")
    print(disease["description"])

    print("\nCommon Symptoms:")

    for symptom in disease.get("common_symptoms", []):
        print(" -", symptom)

    print("\nDiagnostic Context:")

    for item in disease.get("diagnostic_context", []):
        print(" -", item)

    print("\nImportant Context:")
    print(disease.get("important_context", "Not available."))

    print("\nSource:")
    print(disease["source"]["organization"])
    print(disease["source"]["url"])

    print("\n" + "=" * 60)


def main():

    print("=" * 60)
    print("AGENTIC AI HEALTHCARE")
    print("KNOWLEDGE RETRIEVAL TEST")
    print("=" * 60)

    knowledge = load_knowledge()

    print("\nAvailable diseases:")

    for disease in knowledge["diseases"]:
        print(" -", disease["name"])

    disease_name = input(
        "\nEnter a disease name: "
    )

    disease = find_disease(
        knowledge,
        disease_name
    )

    if disease:

        show_information(disease)

    else:

        print("\nDisease not found in knowledge base.")


if __name__ == "__main__":
    main()