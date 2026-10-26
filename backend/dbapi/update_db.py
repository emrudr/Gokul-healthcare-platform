from typing import Optional
from sqlalchemy.orm import Session
from models.patient_model import Patient
from models.db_schemas import PatientDBUpdate


def update_patient(
    db: Session, patient_id: int, patient_data: PatientDBUpdate
) -> Optional[Patient]:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return None

    update_fields = patient_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        if value is not None:
            setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient


def update_patient_remarks(
    db: Session, patient_id: int, remarks: str
) -> Optional[Patient]:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return None

    patient.remarks = remarks
    db.commit()
    db.refresh(patient)
    return patient
