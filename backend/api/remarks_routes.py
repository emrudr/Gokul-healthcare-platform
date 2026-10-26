from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas import (
    PatientResponse,
    RemarkPreviewRequest,
    RemarkPreviewResponse,
)
from dbapi.database import get_db
import dbapi.update_db as update_db
import logic.get_patients as get_patients_logic
import logic.generate_remarks as remarks_logic
from logic.validators import validate_biomarker

router = APIRouter(tags=["Remarks"])


@router.post(
    "/patients/{patient_id}/check-remarks",
    response_model=PatientResponse,
    summary="Generate AI clinical remarks for an existing patient and save to database",
)
def check_patient_remarks(
    patient_id: int,
    db: Session = Depends(get_db),
):
    patient = get_patients_logic.get_patient_by_id_record(db, patient_id)

    generated_remarks = remarks_logic.generate_biomarker_remarks(
        glucose=patient.glucose,
        haemoglobin=patient.haemoglobin,
        cholesterol=patient.cholesterol,
    )

    updated_patient = update_db.update_patient_remarks(
        db, patient_id=patient_id, remarks=generated_remarks
    )
    return updated_patient


@router.post(
    "/remarks/preview",
    response_model=RemarkPreviewResponse,
    summary="Preview clinical remarks for arbitrary biomarker values before saving",
)
def preview_remarks(payload: RemarkPreviewRequest):
    glucose = validate_biomarker(payload.glucose, "Glucose")
    haemoglobin = validate_biomarker(payload.haemoglobin, "Haemoglobin")
    cholesterol = validate_biomarker(payload.cholesterol, "Cholesterol")

    remarks = remarks_logic.generate_biomarker_remarks(
        glucose=glucose,
        haemoglobin=haemoglobin,
        cholesterol=cholesterol,
    )
    return {"remarks": remarks}
