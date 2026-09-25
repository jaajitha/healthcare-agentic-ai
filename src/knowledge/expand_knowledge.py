import json
from pathlib import Path

file = Path("knowledge/medical_knowledge.json")

with file.open("r", encoding="utf-8") as f:
    data = json.load(f)

new_entries = [
    {
        "name": "Paralysis (brain hemorrhage)",
        "aliases": ["hemorrhagic stroke", "intracerebral hemorrhage", "hemorrhagic stroke"],
        "description": "A hemorrhagic stroke occurs when a blood vessel in the brain bursts and causes bleeding in or around the brain.",
        "common_symptoms": [
            "sudden severe headache",
            "weakness",
            "numbness",
            "confusion",
            "trouble speaking",
            "vision problems",
            "dizziness",
            "loss of balance"
        ],
        "diagnostic_context": [
            "physical examination",
            "medical history",
            "brain imaging to check for bleeding"
        ],
        "important_context": "Stroke symptoms often begin suddenly. Sudden weakness, speech difficulty, vision problems, severe headache, or loss of balance require urgent medical evaluation.",
        "source": {
            "organization": "MedlinePlus / NIH",
            "url": "https://medlineplus.gov/hemorrhagicstroke.html"
        }
    },
    {
        "name": "(vertigo) Paroymsal Positional Vertigo",
        "aliases": [
            "benign positional vertigo",
            "benign paroxysmal positional vertigo",
            "BPPV"
        ],
        "description": "Benign positional vertigo is a common type of vertigo caused by a problem in the inner ear.",
        "common_symptoms": [
            "vertigo",
            "dizziness",
            "loss of balance",
            "nausea",
            "vomiting",
            "vision problems"
        ],
        "diagnostic_context": [
            "physical examination",
            "medical history",
            "Dix-Hallpike maneuver may be used"
        ],
        "important_context": "Vertigo is typically a spinning sensation. New weakness, slurred speech, or vision problems alongside vertigo can indicate a more serious condition.",
        "source": {
            "organization": "MedlinePlus / NIH",
            "url": "https://medlineplus.gov/ency/article/001420.htm"
        }
    },
    {
        "name": "Heart attack",
        "aliases": ["myocardial infarction", "MI"],
        "description": "A heart attack occurs when blood flow to part of the heart becomes blocked and the heart muscle is deprived of oxygen.",
        "common_symptoms": [
            "chest pain",
            "chest discomfort",
            "shortness of breath",
            "nausea",
            "vomiting",
            "dizziness",
            "lightheadedness",
            "sweating",
            "upper body discomfort",
            "fatigue"
        ],
        "diagnostic_context": [
            "physical examination",
            "medical history",
            "electrocardiogram (ECG)",
            "blood tests"
        ],
        "important_context": "A suspected heart attack is a medical emergency and requires prompt medical evaluation.",
        "source": {
            "organization": "MedlinePlus / NIH",
            "url": "https://medlineplus.gov/heartattack.html"
        }
    }
]

existing = {
    entry["name"].strip().lower()
    for entry in data.get("diseases", [])
}

added = 0

for entry in new_entries:
    if entry["name"].strip().lower() not in existing:
        data["diseases"].append(entry)
        added += 1

with file.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Knowledge base updated successfully. Added: {added}")
print(f"Total disease entries: {len(data['diseases'])}")
