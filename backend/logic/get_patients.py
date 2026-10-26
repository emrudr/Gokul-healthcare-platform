from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.patient_model import Patient
import dbapi.read_db as read_db


def get_all_patient_records(db: Session) -> List[Patient]:
    return read_db.get_all_patients(db)


def get_patient_by_id_record(db: Session, patient_id: int) -> Patient:
    patient = read_db.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"Patient with ID {patient_id} not found.",
        )
    return patient
