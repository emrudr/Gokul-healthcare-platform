from sqlalchemy.orm import Session
from api.schemas import PatientCreateRequest
from logic.validators import validate_patient_create_payload
from models.db_schemas import PatientDBCreate
from models.patient_model import Patient
import dbapi.create_db as create_db


def create_patient_record(db: Session, request: PatientCreateRequest) -> Patient:
    clean_data = validate_patient_create_payload(request.model_dump())
    db_dto = PatientDBCreate(**clean_data)
    patient = create_db.insert_patient(db, db_dto)
    return patient
