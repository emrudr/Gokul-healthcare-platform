from sqlalchemy.orm import Session
from models.patient_model import Patient
from models.db_schemas import PatientDBCreate


def insert_patient(db: Session, patient_data: PatientDBCreate) -> Patient:
    patient = Patient(
        full_name=patient_data.full_name,
        dob=patient_data.dob,
        email=patient_data.email,
        glucose=patient_data.glucose,
        haemoglobin=patient_data.haemoglobin,
        cholesterol=patient_data.cholesterol,
        remarks=patient_data.remarks or "",
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient
