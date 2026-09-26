-- ==========================================
-- SUPABASE ROW LEVEL SECURITY (RLS) SETUP
-- ==========================================
-- This script secures your database so that even if an attacker 
-- bypasses the frontend, they cannot read or write data that 
-- does not belong to them.

-- 1. Enable RLS on all sensitive tables
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctor_visits ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctor_medications ENABLE ROW LEVEL SECURITY;
ALTER TABLE conditions ENABLE ROW LEVEL SECURITY;
ALTER TABLE medications ENABLE ROW LEVEL SECURITY;
ALTER TABLE symptoms ENABLE ROW LEVEL SECURITY;
ALTER TABLE observations ENABLE ROW LEVEL SECURITY;

-- 2. Create Policies for the 'patients' table
-- Patients can only select their own profile based on their authenticated email
CREATE POLICY "Patients can view own profile" 
ON patients FOR SELECT 
USING (auth.jwt() ->> 'email' = email);

-- Patients can update their own profile
CREATE POLICY "Patients can update own profile" 
ON patients FOR UPDATE 
USING (auth.jwt() ->> 'email' = email);

-- 3. Create Policies for 'assessments'
-- Assuming 'patient_id' in assessments maps to 'id' in patients table
CREATE POLICY "Patients can view own assessments" 
ON assessments FOR SELECT 
USING (
    patient_id IN (
        SELECT id FROM patients WHERE email = auth.jwt() ->> 'email'
    )
);

CREATE POLICY "Patients can insert own assessments" 
ON assessments FOR INSERT 
WITH CHECK (
    patient_id IN (
        SELECT id FROM patients WHERE email = auth.jwt() ->> 'email'
    )
);

-- 4. Create Policies for 'doctor_visits'
CREATE POLICY "Patients can view own visits" 
ON doctor_visits FOR SELECT 
USING (
    patient_id IN (
        SELECT id FROM patients WHERE email = auth.jwt() ->> 'email'
    )
);

-- 5. Create Policies for 'doctor_medications'
CREATE POLICY "Patients can view own medications" 
ON doctor_medications FOR SELECT 
USING (
    patient_id IN (
        SELECT id FROM patients WHERE email = auth.jwt() ->> 'email'
    )
);

-- 6. Role-Based Access Control (RBAC) for Doctors & Admins
-- Let's assume you create a custom JWT claim or a 'user_roles' table.
-- For simplicity, if we identify doctors/admins by email domains:
CREATE POLICY "Doctors can view all patients" 
ON patients FOR SELECT 
USING (auth.jwt() ->> 'email' LIKE '%@apollohospitals.com');

CREATE POLICY "Doctors can view all assessments" 
ON assessments FOR SELECT 
USING (auth.jwt() ->> 'email' LIKE '%@apollohospitals.com');

-- (You would duplicate the doctor policies for other tables like doctor_visits)

-- ==========================================
-- INSTRUCTIONS TO RUN:
-- 1. Open your Supabase Dashboard
-- 2. Go to the SQL Editor
-- 3. Paste this entire script and click "Run"
-- ==========================================
