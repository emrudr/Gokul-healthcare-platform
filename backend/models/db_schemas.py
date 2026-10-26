from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PatientDBCreate(BaseModel):
    full_name: str
    dob: str
    email: str
    glucose: float
    haemoglobin: float
    cholesterol: float
    remarks: str = ""


class PatientDBUpdate(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[str] = None
    email: Optional[str] = None
    glucose: Optional[float] = None
    haemoglobin: Optional[float] = None
    cholesterol: Optional[float] = None
    remarks: Optional[str] = None


class PatientDBRead(BaseModel):
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
