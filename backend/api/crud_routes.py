from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.schemas import (
    PatientCreateRequest,
    PatientUpdateRequest,
    PatientResponse,
    DeleteResponse,
)
from dbapi.database import get_db
import logic.create_patient as create_patient_logic
import logic.get_patients as get_patients_logic
import logic.update_patient as update_patient_logic
import logic.delete_patient as delete_patient_logic

router = APIRouter(tags=["Patients"])


@router.post(
    "/patients",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new patient record",
)
def create_patient(
    payload: PatientCreateRequest,
    db: Session = Depends(get_db),
):
    patient = create_patient_logic.create_patient_record(db, payload)
    return patient


@router.get(
    "/patients",
    response_model=List[PatientResponse],
    summary="Retrieve all patient records",
)
def get_all_patients(
    db: Session = Depends(get_db),
):
    return get_patients_logic.get_all_patient_records(db)


@router.get(
    "/patients/{patient_id}",
    response_model=PatientResponse,
    summary="Retrieve a patient by ID",
)
def get_patient_by_id(
    patient_id: int,
    db: Session = Depends(get_db),
):
    return get_patients_logic.get_patient_by_id_record(db, patient_id)


@router.put(
    "/patients/{patient_id}",
    response_model=PatientResponse,
    summary="Update a patient record",
)
def update_patient(
    patient_id: int,
    payload: PatientUpdateRequest,
    db: Session = Depends(get_db),
):
    return update_patient_logic.update_patient_record(db, patient_id, payload)


@router.delete(
    "/patients/{patient_id}",
    response_model=DeleteResponse,
    summary="Delete a patient record",
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
):
    return delete_patient_logic.delete_patient_record(db, patient_id)
