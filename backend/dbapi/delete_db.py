from sqlalchemy.orm import Session
from models.patient_model import Patient


def delete_patient(db: Session, patient_id: int) -> bool:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return False

    db.delete(patient)
    db.commit()
    return True
