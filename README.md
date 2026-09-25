# Agentic AI in Healthcare – Intelligent Autonomous Diagnostic Assistant

This repository contains the source code for a B.Tech CSE Final-Year Project: **Agentic AI in Healthcare**. It is an AI-powered clinical decision-support prototype that leverages Machine Learning, FHIR (Fast Healthcare Interoperability Resources) data integration, and Agentic Reasoning to assist medical professionals.

> **Disclaimer:** This project is a strict **academic prototype**. It does not perform autonomous diagnosis, nor has it been clinically validated. All outputs are for demonstration purposes and are intended to demonstrate AI-assisted clinical decision support. The doctor remains the final decision-maker.

---

## 🌟 Key Features

1. **FHIR / EHR Integration**
   - Ingests mock Electronic Health Records (EHR) in the standard FHIR format (JSON).
   - Automatically parses patient demographics, medical history, vitals, and current medications.
   - Clean UI state-management to separate loaded EHR data from active manual clinical assessment.

2. **Machine Learning Diagnostic Engine**
   - Utilizes a Random Forest classifier trained on a deduplicated public symptom-disease dataset containing 132 symptom features.
   - Outputs top-5 disease candidates with probability and confidence levels (High/Moderate/Low).
   - Features 5-fold cross-validation demonstrating robust dataset-level performance.

3. **Vital-Risk Rules Engine**
   - Evaluates patient vitals (Temperature, Heart Rate, Blood Pressure, SpO₂) against critical thresholds.
   - Flags abnormal readings (e.g., Hypoxia, Hypertension, Fever) for priority review.

4. **Medication Interaction Checker**
   - Cross-references current patient medications (from FHIR or manual entry) against a localized knowledge base.
   - Flags drug-to-drug interactions categorized by severity (e.g., Aspirin + Warfarin = HIGH severity bleeding risk).

5. **Agentic Reasoning & Orchestration**
   - Synthesizes the ML predictions, vital risks, medication alerts, and retrieved medical knowledge.
   - Utilizes a priority-based logic tree to guide clinical next steps (e.g., Red flags trigger "URGENT CLINICAL REVIEW RECOMMENDED").
   - Generates a comprehensive **Doctor Briefing** summarizing all contexts into one unified actionable report.

6. **Interactive Streamlit UI**
   - Clean, modern, and responsive user interface.
   - Designed to mimic a real-world clinical workspace where a clinician can import EHR data, review it, and append manual symptom observations.

---

## 📂 Project Structure

```text
healthcare-agentic-ai/
├── main.py                     # Main application entry point (Routing)
├── .env                        # Environment variables
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
│
├── src/                        # Main source code directory
│   ├── pages/                  # Streamlit pages (loaded by main.py)
│   │   ├── login.py
│   │   ├── patient_dashboard.py
│   │   ├── doctor_dashboard.py
│   │   └── admin_dashboard.py
│   │
│   ├── services/               # External API and database clients
│   │   ├── supabase_client.py
│   │   └── hospital_client.py
│   │
│   ├── agents/                 # Agentic logic and routing
│   │   ├── hospital_routing_agent.py
│   │   └── patient_assessment.py
│   │
│   ├── ml/                     # Machine Learning pipeline and inference
│   │   ├── train_model.py
│   │   ├── predict.py
│   │   ├── cross_validation.py
│   │   ├── preprocess_data.py
│   │   └── eda.py
│   │
│   ├── fhir/                   # FHIR parsing logic
│   │   └── parser.py           
│   │
│   └── knowledge/              # Knowledge base scripts and logic
│       ├── medication_checker.py
│       └── expand_knowledge.py
│
├── data/                       # Datasets & ML models
│   ├── processed/              # Trained models & graphs
│   ├── Testing.csv
│   └── Training.csv
│
├── fhir/                       # FHIR payload mocks
│   └── patient.json
│
└── knowledge/                  # Medical & medication JSON rules
    ├── medical_knowledge.json
    └── medication_knowledge.json
```

---

## 🚀 Getting Started

### Prerequisites & Installation

Ensure you have Python 3.9+ installed. Because modern Linux distributions enforce externally managed Python environments (PEP 668), it is highly recommended to use a virtual environment to install dependencies.

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **Install the required libraries:**
   Install the dependencies directly using `pip` inside the activated virtual environment:
   ```bash
   pip install streamlit pandas scikit-learn xgboost matplotlib seaborn python-dotenv supabase
   ```

### Running the Application

Once the virtual environment is activated and dependencies are installed, launch the full Agentic AI Healthcare Assistant UI from the project root:

```bash
python -m streamlit run main.py
```

*(Note: Ensure your virtual environment is activated every time you want to run the application).*

The application will be accessible in your web browser at `http://localhost:8501`.

---

## 🧪 Testing the Pipeline

You can simulate a complete end-to-end clinical workflow using the provided mock data:

1. **Load FHIR Patient:** Click the `Load FHIR Patient` button in the sidebar/UI. This will read `fhir/patient.json` (Patient: Rahul Sharma) without overwriting manual form inputs.
2. **Import Data:** Click `Use FHIR Data for Assessment` to import the EHR vitals, demographics, and medications into the active clinical assessment form.
3. **Add Symptoms:** In the manual symptoms input box, type `vomiting, abdominal_pain`.
4. **Assess:** Click the `🔍 ASSESS PATIENT` button.
5. **Review Output:** Watch the Agentic Orchestrator run the ML model, Vital Risk engine, Medication checker, and output the final **Doctor Briefing**.

You can also test specific safety edges, such as manually adding `warfarin` to a patient already taking `aspirin`, or lowering the SpO₂ to `89` to see the vital-risk engine intercept the ML outputs with safety warnings.

---

## 🏗️ Architecture Overview

The system follows a modular architecture orchestrated by `main.py`:

```mermaid
graph TD
    A[Patient Data] --> B{Streamlit UI}
    B --> |Load Button| C[Local FHIR Mock JSON]
    C --> |Parser| B
    B --> |Demographics, Vitals, History, Meds, Symptoms| D[Agentic AI Orchestrator]
    
    D --> E[Random Forest ML Model]
    E --> |Predicts Disease Candidates| D
    
    D --> F[Risk Rule Engine]
    F --> |Evaluates Vitals & Red Flags| D
    
    D --> G[Medication Checker]
    G --> |Checks Drug Interactions| D
    
    D --> H[Knowledge Retrieval]
    H --> |Fetches Medical Context| D
    
    D --> I[Agentic Decision Logic]
    I --> |Prioritizes Findings & Generates Recommendation| J[Doctor Briefing]
    
    J --> K[Final Output Display in UI]
```

---

## 🔒 Safety & Limitations

- **Model Constraints:** The Random Forest model is strict and accepts only 132 predefined binary symptom features. Demographics, vitals, and medications are routed exclusively through the logic/rules engines, bypassing the ML model to maintain feature integrity.
- **Mock FHIR Data:** The FHIR JSON bundle is synthetically generated and does not correspond to any real patient data.
- **Clinical Validation:** The system is an academic proof-of-concept for Agentic coordination in healthcare IT. It is not FDA-approved, nor does it have real-world clinical validation.
