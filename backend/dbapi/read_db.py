from typing import List, Optional
from sqlalchemy.orm import Session
from models.patient_model import Patient


def get_all_patients(db: Session) -> List[Patient]:
    return db.query(Patient).order_by(Patient.id.asc()).all()


def get_patient_by_id(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.id == patient_id).first()
