from fastapi import HTTPException
from sqlalchemy.orm import Session
import dbapi.delete_db as delete_db
import dbapi.read_db as read_db


def delete_patient_record(db: Session, patient_id: int) -> dict:
    patient = read_db.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"Patient with ID {patient_id} not found.",
        )

    success = delete_db.delete_patient(db, patient_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete patient with ID {patient_id}.",
        )

    return {
        "success": True,
        "message": f"Patient with ID {patient_id} deleted successfully.",
    }
