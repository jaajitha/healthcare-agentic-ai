import os
from fpdf import FPDF
from datetime import datetime

class HospitalReportPDF(FPDF):
    def __init__(self, patient_profile):
        super().__init__()
        self.patient_profile = patient_profile

    def header(self):
        # Hospital Logo (Optional, we'll just use text for now)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(2, 132, 199) # Streamlit blue
        self.cell(0, 10, 'Apollo Healthcare', border=False, align='C', new_x="LMARGIN", new_y="NEXT")
        
        self.set_font('Helvetica', '', 12)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, 'Confidential Clinical Discharge Summary', border=False, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', align='C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(15, 23, 42)
        self.set_fill_color(241, 245, 249)
        self.cell(0, 10, f'  {title}', border=False, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def chapter_body(self, text, indent=0):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(51, 65, 85)
        if indent:
            self.set_x(self.get_x() + indent)
        self.multi_cell(0, 6, text)
        self.ln(2)

def generate_patient_pdf(patient_profile, visits, medications, filepath):
    pdf = HospitalReportPDF(patient_profile)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # 1. Personal Information
    pdf.chapter_title('Patient Demographics')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(50, 8, 'Full Name:', border=0)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, str(patient_profile.get('patient_name', 'N/A')), border=0, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(50, 8, 'Patient ID:', border=0)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, str(patient_profile.get('patient_id', 'N/A')), border=0, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(50, 8, 'Age / Gender:', border=0)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f"{patient_profile.get('age', 'N/A')} Years / {patient_profile.get('gender', 'N/A')}", border=0, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Pre-existing Conditions
    pdf.chapter_title('Medical History')
    conditions = patient_profile.get('medical_history', [])
    if conditions:
        for condition in conditions:
            pdf.chapter_body(f"- {condition}", indent=5)
    else:
        pdf.chapter_body("No pre-existing conditions reported.")
    pdf.ln(5)
    
    # 2. Past Visits
    pdf.chapter_title('Clinical Encounters')
    if visits:
        for v in visits:
            dr_name = v.get('doctors', {}).get('name', 'Unknown')
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 8, f"Visit on {v.get('visit_date')} - Dr. {dr_name}", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font('Helvetica', 'B', 11)
            pdf.write(6, "Diagnosis: ")
            pdf.set_font('Helvetica', '', 11)
            diag_text = str(v.get('diagnosis', 'None'))
            pdf.multi_cell(0, 6, diag_text if diag_text else "None", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font('Helvetica', 'B', 11)
            pdf.write(6, "Care Plan: ")
            pdf.set_font('Helvetica', '', 11)
            plan_text = str(v.get('future_plan', 'None'))
            pdf.multi_cell(0, 6, plan_text if plan_text else "None", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)
    else:
        pdf.chapter_body("No previous visits found.")
    pdf.ln(5)
    
    # 3. Medications
    pdf.chapter_title('Active Prescriptions')
    if medications:
        for m in medications:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 7, f"- {str(m.get('medication_name')).title()}", new_x="LMARGIN", new_y="NEXT")
            
            # Use left margin for indentation
            orig_lmargin = pdf.l_margin
            pdf.set_left_margin(orig_lmargin + 5)
            
            pdf.set_font('Helvetica', '', 11)
            pdf.multi_cell(0, 6, f"Dosage: {m.get('dosage')} ({m.get('frequency')}) for {m.get('duration')}", new_x="LMARGIN", new_y="NEXT")
            
            instr = m.get('instructions')
            if instr:
                pdf.multi_cell(0, 6, f"Notes: {instr}", new_x="LMARGIN", new_y="NEXT")
                
            pdf.set_left_margin(orig_lmargin)
            pdf.ln(2)
    else:
        pdf.chapter_body("No active prescriptions.")
        
    pdf.output(filepath)
    return filepath
