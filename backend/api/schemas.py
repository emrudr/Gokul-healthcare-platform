from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class PatientCreateRequest(BaseModel):
    full_name: Any
    dob: Any
    email: Any
    glucose: Any
    haemoglobin: Any
    cholesterol: Any
    remarks: Optional[str] = ""


class PatientUpdateRequest(BaseModel):
    full_name: Optional[Any] = None
    dob: Optional[Any] = None
    email: Optional[Any] = None
    glucose: Optional[Any] = None
    haemoglobin: Optional[Any] = None
    cholesterol: Optional[Any] = None
    remarks: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    full_name: str
    dob: str
    email: str
    glucose: float
    haemoglobin: float
    cholesterol: float
    remarks: Optional[str] = ""
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RemarkPreviewRequest(BaseModel):
    glucose: Any
    haemoglobin: Any
    cholesterol: Any


class RemarkPreviewResponse(BaseModel):
    remarks: str


class DeleteResponse(BaseModel):
    success: bool
    message: str
