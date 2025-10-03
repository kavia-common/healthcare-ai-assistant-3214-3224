"""
Patient CRUD APIs and history retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .db import get_db_session
from . import models
from .schemas import PatientCreate, PatientOut, ChatThreadOut

router = APIRouter(prefix="/patients", tags=["Patients"])


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[PatientOut],
    summary="List patients",
    description="Get all patients.",
)
def list_patients(db: Session = Depends(get_db_session)):
    """List all patients."""
    return db.query(models.Patient).order_by(models.Patient.created_at.desc()).all()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=PatientOut,
    summary="Create or update patient",
    description="Create or update a patient record by optional ID.",
)
def upsert_patient(
    payload: PatientCreate, db: Session = Depends(get_db_session)
):
    """Create a new patient or update an existing one if id is provided."""
    if payload.id:
        patient = db.query(models.Patient).filter(models.Patient.id == payload.id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        patient.name = payload.name
        patient.age = payload.age
        patient.notes = payload.notes
        db.add(patient)
        db.flush()
        db.refresh(patient)
        return patient

    patient = models.Patient(name=payload.name, age=payload.age, notes=payload.notes)
    db.add(patient)
    db.flush()
    db.refresh(patient)
    return patient


# PUBLIC_INTERFACE
@router.get(
    "/{patient_id}/history",
    response_model=List[ChatThreadOut],
    summary="Get patient chat history",
    description="Get all chat threads with messages for a patient.",
)
def get_history(patient_id: int, db: Session = Depends(get_db_session)):
    """Retrieve all chat threads and messages for a given patient."""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    threads = (
        db.query(models.ChatThread)
        .filter(models.ChatThread.patient_id == patient_id)
        .order_by(models.ChatThread.updated_at.desc())
        .all()
    )

    # Eagerly load messages per thread
    for t in threads:
        _ = [m for m in t.messages]  # Access relationship to ensure it's populated

    return threads
