-- ==========================================
-- PATIENT AUTHENTICATION MAPPING
-- ==========================================
-- Creates a secure mapping between Supabase Auth users and patient records

CREATE TABLE IF NOT EXISTS public.patient_auth (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    UNIQUE(auth_user_id),
    UNIQUE(patient_id)
);

ALTER TABLE public.patient_auth ENABLE ROW LEVEL SECURITY;

-- Users can only read their own mapping
CREATE POLICY "Users can view own mapping" 
ON public.patient_auth FOR SELECT 
USING (auth.uid() = auth_user_id);

-- Also add a policy to allow patients to see their data if they have a mapping
CREATE POLICY "Patients can view own profile via auth mapping" 
ON public.patients FOR SELECT 
USING (
    id IN (
        SELECT patient_id FROM public.patient_auth WHERE auth_user_id = auth.uid()
    )
);

CREATE POLICY "Patients can update own profile via auth mapping" 
ON public.patients FOR UPDATE 
USING (
    id IN (
        SELECT patient_id FROM public.patient_auth WHERE auth_user_id = auth.uid()
    )
);

-- Note: Other tables (assessments, doctor_visits, etc) in 001_rls_setup.sql 
-- rely on `patient_id IN (SELECT id FROM patients WHERE email = auth.jwt() ->> 'email')`.
-- Since the user now has access to their row in `patients`, those policies still work 
-- IF the email in auth.jwt() matches the email in patients table. 
-- However, to be robust, we could also add mapping policies to other tables, 
-- but ensuring the `email` column is set during mapping is simpler and safer.
