import datetime
import re
from typing import Any, Dict
from fastapi import HTTPException

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_full_name(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HTTPException(
            status_code=400,
            detail="Full name is required and cannot be empty.",
        )
    return value.strip()


def validate_email(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HTTPException(
            status_code=400,
            detail="Email is required and must be a valid email string.",
        )
    cleaned = value.strip()
    if not EMAIL_REGEX.match(cleaned):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format. Email must include '@' and a valid domain (e.g., patient@example.com).",
        )
    return cleaned


def validate_dob(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HTTPException(
            status_code=400,
            detail="Date of birth is required and must be in DD.MM.YYYY or DD/MM/YYYY format.",
        )

    cleaned = value.strip().replace("/", ".")
    parts = cleaned.split(".")

    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise HTTPException(
            status_code=400,
            detail="Date of birth must be formatted as DD.MM.YYYY or DD/MM/YYYY (e.g., 15.08.1990).",
        )

    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])

    try:
        parsed_date = datetime.date(year, month, day)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid calendar date '{value}'. Please verify the day, month, and year.",
        )

    if parsed_date > datetime.date.today():
        raise HTTPException(
            status_code=400,
            detail="Date of birth cannot be in the future.",
        )

    # Return normalized DD.MM.YYYY string
    return f"{day:02d}.{month:02d}.{year:04d}"


def validate_biomarker(value: Any, field_name: str) -> float:
    if value is None:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} is required.",
        )

    try:
        numeric_val = float(value)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be a valid numeric value.",
        )

    if numeric_val <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be a positive number greater than 0.",
        )

    return round(numeric_val, 2)


def validate_patient_create_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    full_name = validate_full_name(payload.get("full_name"))
    dob = validate_dob(payload.get("dob"))
    email = validate_email(payload.get("email"))
    glucose = validate_biomarker(payload.get("glucose"), "Glucose")
    haemoglobin = validate_biomarker(payload.get("haemoglobin"), "Haemoglobin")
    cholesterol = validate_biomarker(payload.get("cholesterol"), "Cholesterol")

    raw_remarks = payload.get("remarks")
    remarks = raw_remarks.strip() if isinstance(raw_remarks, str) else ""

    return {
        "full_name": full_name,
        "dob": dob,
        "email": email,
        "glucose": glucose,
        "haemoglobin": haemoglobin,
        "cholesterol": cholesterol,
        "remarks": remarks,
    }


def validate_patient_update_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    validated: Dict[str, Any] = {}

    if "full_name" in payload and payload["full_name"] is not None:
        validated["full_name"] = validate_full_name(payload["full_name"])

    if "dob" in payload and payload["dob"] is not None:
        validated["dob"] = validate_dob(payload["dob"])

    if "email" in payload and payload["email"] is not None:
        validated["email"] = validate_email(payload["email"])

    if "glucose" in payload and payload["glucose"] is not None:
        validated["glucose"] = validate_biomarker(payload["glucose"], "Glucose")

    if "haemoglobin" in payload and payload["haemoglobin"] is not None:
        validated["haemoglobin"] = validate_biomarker(payload["haemoglobin"], "Haemoglobin")

    if "cholesterol" in payload and payload["cholesterol"] is not None:
        validated["cholesterol"] = validate_biomarker(payload["cholesterol"], "Cholesterol")

    if "remarks" in payload and payload["remarks"] is not None:
        val = payload["remarks"]
        validated["remarks"] = val.strip() if isinstance(val, str) else ""

    return validated
