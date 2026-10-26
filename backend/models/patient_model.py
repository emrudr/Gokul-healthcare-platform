from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from dbapi.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    full_name = Column(String(255), nullable=False)
    dob = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    glucose = Column(Float, nullable=False)
    haemoglobin = Column(Float, nullable=False)
    cholesterol = Column(Float, nullable=False)
    remarks = Column(Text, nullable=True, default="")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
