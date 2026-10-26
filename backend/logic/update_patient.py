from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.schemas import PatientUpdateRequest
from logic.validators import validate_patient_update_payload
from models.db_schemas import PatientDBUpdate
from models.patient_model import Patient
import dbapi.update_db as update_db
import dbapi.read_db as read_db


def update_patient_record(
    db: Session, patient_id: int, request: PatientUpdateRequest
) -> Patient:
    existing_patient = read_db.get_patient_by_id(db, patient_id)
    if not existing_patient:
        raise HTTPException(
            status_code=404,
            detail=f"Patient with ID {patient_id} not found.",
        )

    raw_payload = request.model_dump(exclude_unset=True)
    if not raw_payload:
        return existing_patient

    clean_data = validate_patient_update_payload(raw_payload)
    db_dto = PatientDBUpdate(**clean_data)
    updated = update_db.update_patient(db, patient_id, db_dto)
    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Patient with ID {patient_id} not found.",
        )
    return updated
