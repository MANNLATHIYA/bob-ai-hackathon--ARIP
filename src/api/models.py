from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Severity(StrEnum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    ADMINISTRATIVE = "ADMINISTRATIVE"


class SiteORM(Base):
    __tablename__ = "sites"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    last_monitoring_date: Mapped[date] = mapped_column(Date)
    enrollment_target: Mapped[int] = mapped_column(Integer, default=30)


class PatientORM(Base):
    __tablename__ = "patients"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id"), index=True)
    enrolled_at: Mapped[date] = mapped_column(Date)
    age: Mapped[int] = mapped_column(Integer)
    sex: Mapped[str] = mapped_column(String)


class VisitORM(Base):
    __tablename__ = "visits"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id"), index=True)
    visit_type: Mapped[str] = mapped_column(String)
    scheduled_date: Mapped[date] = mapped_column(Date)
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    dose_mg: Mapped[float | None] = mapped_column(Float, nullable=True)
    route: Mapped[str | None] = mapped_column(String, nullable=True)
    medications: Mapped[list] = mapped_column(JSON, default=list)
    assessments: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")
    query_resolution_days: Mapped[int] = mapped_column(Integer, default=0)


class DeviationORM(Base):
    __tablename__ = "deviations"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    visit_id: Mapped[str] = mapped_column(ForeignKey("visits.id"), index=True)
    patient_id: Mapped[str] = mapped_column(String, index=True)
    site_id: Mapped[str] = mapped_column(String, index=True)
    kind: Mapped[str] = mapped_column(String, index=True)
    severity: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(Text)
    rationale: Mapped[str] = mapped_column(Text)
    protocol_clause: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source: Mapped[str] = mapped_column(String, default="RULE")


class CAPAReportORM(Base):
    __tablename__ = "capa_reports"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    deviation_id: Mapped[str | None] = mapped_column(String, nullable=True)
    site_id: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Patient(ORMModel):
    id: str
    site_id: str
    enrolled_at: date
    age: int
    sex: str


class Site(ORMModel):
    id: str
    name: str
    country: str
    last_monitoring_date: date
    enrollment_target: int


class Visit(ORMModel):
    id: str
    patient_id: str
    site_id: str
    visit_type: str
    scheduled_date: date
    actual_date: date | None
    dose_mg: float | None
    route: str | None
    medications: list[str] = Field(default_factory=list)
    assessments: list[str] = Field(default_factory=list)
    notes: str = ""
    query_resolution_days: int = 0


class ProtocolRule(BaseModel):
    visit_type: str
    target_day: int
    window_days: int
    dose_mg: float | None = None
    dose_tolerance_pct: float = 0.05
    route: str | None = None
    required_assessments: list[str] = Field(default_factory=list)
    clause: str


class ProtocolSpec(BaseModel):
    protocol_id: str
    title: str
    banned_medications: list[str]
    eligibility: dict[str, Any]
    visit_rules: list[ProtocolRule]


class Deviation(ORMModel):
    id: str
    visit_id: str
    patient_id: str
    site_id: str
    kind: str
    severity: Severity
    description: str
    rationale: str
    protocol_clause: str
    confidence: float
    detected_at: datetime
    source: str


class RiskBand(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SiteRisk(BaseModel):
    site_id: str
    site_name: str
    country: str
    score: float = Field(ge=0, le=100)
    band: RiskBand
    deviation_count: int
    major_count: int
    trend: float
    days_since_monitoring: int
    monthly_trend: list[dict[str, Any]]


class CAPARequest(BaseModel):
    deviation_id: str | None = None
    site_id: str | None = None
    format: str = "markdown"


class CAPAReport(ORMModel):
    id: str
    deviation_id: str | None
    site_id: str
    content: str
    created_at: datetime
