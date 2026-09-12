import json
import os

data = {
    "metadata": {
        "name": "Agentic AI Healthcare Medical Knowledge Base",
        "version": "1.0",
        "purpose": "Starter retrieval knowledge base",
        "source": "MedlinePlus / U.S. National Library of Medicine"
    },

    "diseases": [

        {
            "name": "Hepatitis C",
            "aliases": ["HCV"],
            "description": "Hepatitis C is inflammation of the liver caused by the hepatitis C virus.",
            "common_symptoms": [
                "dark urine",
                "fatigue",
                "fever",
                "joint pain",
                "loss of appetite",
                "nausea",
                "vomiting",
                "abdominal pain",
                "jaundice",
                "yellowish eyes",
                "yellowish skin"
            ],
            "diagnostic_context": [
                "medical history",
                "physical examination",
                "blood tests"
            ],
            "important_context": "Many people with hepatitis C may have no symptoms.",
            "source": {
                "organization": "MedlinePlus / NIH",
                "url": "https://medlineplus.gov/hepatitisc.html"
            }
        },

        {
            "name": "Gastroenteritis",
            "aliases": ["stomach flu"],
            "description": "Gastroenteritis is inflammation of the lining of the stomach and intestines.",
            "common_symptoms": [
                "diarrhea",
                "abdominal pain",
                "abdominal cramping",
                "nausea",
                "vomiting",
                "fever"
            ],
            "diagnostic_context": [
                "symptom history",
                "physical examination",
                "stool tests"
            ],
            "important_context": "Gastroenteritis can sometimes cause dehydration.",
            "source": {
                "organization": "MedlinePlus / NIH",
                "url": "https://medlineplus.gov/gastroenteritis.html"
            }
        },

        {
            "name": "GERD",
            "aliases": [
                "gastroesophageal reflux disease",
                "acid reflux"
            ],
            "description": "GERD is a condition in which stomach contents can move back into the esophagus.",
            "common_symptoms": [
                "heartburn",
                "acid taste",
                "food regurgitation",
                "dry cough",
                "hoarse voice",
                "trouble swallowing",
                "nausea"
            ],
            "diagnostic_context": [
                "symptoms and medical history",
                "upper GI endoscopy",
                "esophageal pH testing"
            ],
            "important_context": "Chest pain with shortness of breath or pain in the jaw or arm requires medical evaluation.",
            "source": {
                "organization": "MedlinePlus / NIH",
                "url": "https://medlineplus.gov/gerd.html"
            }
        },

        {
            "name": "Peptic ulcer",
            "aliases": [
                "peptic ulcer disease",
                "gastric ulcer",
                "duodenal ulcer"
            ],
            "description": "A peptic ulcer is a sore in the lining of the stomach or duodenum.",
            "common_symptoms": [
                "burning stomach pain",
                "upper abdominal pain",
                "nausea",
                "vomiting",
                "dark stools",
                "bloody vomiting",
                "heartburn",
                "weight loss"
            ],
            "diagnostic_context": [
                "Helicobacter pylori testing",
                "endoscopy",
                "medical history"
            ],
            "important_context": "Gastrointestinal bleeding or a perforated ulcer can be serious.",
            "source": {
                "organization": "MedlinePlus / NIH",
                "url": "https://medlineplus.gov/pepticulcer.html"
            }
        },

        {
            "name": "Migraine",
            "aliases": ["migraine headache"],
            "description": "Migraine is a recurring type of headache that can cause moderate to severe throbbing or pulsing pain.",
            "common_symptoms": [
                "headache",
                "throbbing headache",
                "nausea",
                "vomiting",
                "sensitivity to light",
                "sensitivity to sound",
                "visual aura"
            ],
            "diagnostic_context": [
                "clinical history",
                "symptom pattern",
                "physical examination when appropriate"
            ],
            "important_context": "Migraine symptoms can occur in different phases and vary between people.",
            "source": {
                "organization": "MedlinePlus / NIH",
                "url": "https://medlineplus.gov/migraine.html"
            }
        },

        {
            "name": "Asthma",
            "aliases": ["bronchial asthma"],
            "description": "Asthma is a chronic lung disease in which the airways can become inflamed and narrowed.",
            "common_symptoms": [
                "wheezing",
                "cough",
                "chest tightness",
                "shortness of breath",
                "breathing difficulty"
            ],
            "diagnostic_context": [
                "physical examination",
                "medical history",
                "spirometry",
                "peak expiratory flow testing"
            ],
            "important_context": "Severe asthma attacks can be life-threatening.",
            "source": {
                "organization": "MedlinePlus / NIH",
                "url": "https://medlineplus.gov/asthma.html"
            }
        },

        {
            "name": "Hypertension",
            "aliases": [
                "high blood pressure",
                "HTN"
            ],
            "description": "Hypertension is the medical term for high blood pressure.",
            "common_symptoms": [
                "often no symptoms"
            ],
            "diagnostic_context": [
                "blood pressure measurements",
                "repeated blood pressure measurements"
            ],
            "important_context": "Untreated high blood pressure can increase the risk of serious health problems.",
            "source": {
                "organization": "MedlinePlus / NIH",
                "url": "https://medlineplus.gov/highbloodpressure.html"
            }
        }
    ]
}


folder = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(folder, "medical_knowledge.json")

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print("Medical knowledge base created successfully.")
print("File:", output_file)
print("Diseases:", len(data["diseases"]))