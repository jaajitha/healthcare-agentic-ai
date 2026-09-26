
import streamlit as st
import functools

import os
from dotenv import load_dotenv
from supabase import create_client
from src.services.supabase_client import get_supabase_client

# ============================================================
# SUPABASE CONNECTION
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing from .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================
# HOSPITAL
# ============================================================

@st.cache_data(ttl="1h")
def get_hospital(hospital_code="AH-ARAGONDA"):
    """
    Get hospital information using the hospital code.
    """

    response = (
        get_supabase_client()
        .table("hospitals")
        .select("*")
        .eq("hospital_code", hospital_code)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


# ============================================================
# DEPARTMENTS / SPECIALITIES
# ============================================================

@st.cache_data(ttl="1h")
def get_departments(hospital_code="AH-ARAGONDA"):
    """
    Get all departments/specialities of the hospital.
    """

    hospital = get_hospital(hospital_code)

    if not hospital:
        return []

    response = (
        get_supabase_client()
        .table("departments")
        .select("*")
        .eq("hospital_id", hospital["id"])
        .order("department_name")
        .execute()
    )

    return response.data or []


# ============================================================
# DOCTORS
# ============================================================

@st.cache_data(ttl="1h")
def get_doctors(hospital_code="AH-ARAGONDA"):
    """
    Get all doctors belonging to the hospital.
    """

    hospital = get_hospital(hospital_code)

    if not hospital:
        return []

    response = (
        get_supabase_client()
        .table("doctors")
        .select("*")
        .eq("hospital_id", hospital["id"])
        .order("name")
        .execute()
    )

    return response.data or []


# ============================================================
# DOCTORS BY SPECIALITY
# ============================================================

@st.cache_data(ttl="1h")
def get_doctors_by_speciality(
    speciality,
    hospital_code="AH-ARAGONDA"
):
    """
    Get doctors belonging to a particular speciality.
    """

    hospital = get_hospital(hospital_code)

    if not hospital:
        return []

    response = (
        get_supabase_client()
        .table("doctors")
        .select("*")
        .eq("hospital_id", hospital["id"])
        .ilike("speciality", speciality)
        .order("name")
        .execute()
    )

    return response.data or []


# ============================================================
# HOSPITAL SERVICES
# ============================================================

@st.cache_data(ttl="1h")
def get_services(hospital_code="AH-ARAGONDA"):
    """
    Get hospital services and facilities.
    """

    hospital = get_hospital(hospital_code)

    if not hospital:
        return []

    response = (
        get_supabase_client()
        .table("hospital_services")
        .select("*")
        .eq("hospital_id", hospital["id"])
        .order("service_name")
        .execute()
    )

    return response.data or []


# ============================================================
# COMPLETE HOSPITAL PROFILE
# ============================================================

@st.cache_data(ttl="1h")
def get_hospital_profile(hospital_code="AH-ARAGONDA"):
    """
    Return hospital + departments + doctors + services
    as one structured object.
    """

    hospital = get_hospital(hospital_code)

    if not hospital:
        return None

    departments = get_departments(hospital_code)
    doctors = get_doctors(hospital_code)
    services = get_services(hospital_code)

    return {
        "hospital": hospital,
        "departments": departments,
        "doctors": doctors,
        "services": services
    }