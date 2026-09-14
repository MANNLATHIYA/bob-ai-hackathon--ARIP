import csv
import json
from datetime import date, datetime, time
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.models import PatientORM, SiteORM, Visit, VisitORM
from src.deviation_engine import DeviationEngine
from src.ingestion import load_protocol

from .database import engine
from .models import DeviationORM

ROOT = Path(__file__).resolve().parents[2]


async def seed_database(force: bool = False):
    sample = ROOT / "data/sample"
    if not (sample / "visits.csv").exists():
        from data.generate_synthetic import generate
        generate()
    with Session(engine) as db:
        if not force and db.scalar(select(func.count()).select_from(SiteORM)):
            return
        if force:
            for model in (DeviationORM, VisitORM, PatientORM, SiteORM): db.query(model).delete()
        for row in csv.DictReader((sample / "sites.csv").open()):
            row["last_monitoring_date"] = date.fromisoformat(row["last_monitoring_date"])
            row["enrollment_target"] = int(row["enrollment_target"])
            db.add(SiteORM(**row))
        for row in csv.DictReader((sample / "patients.csv").open()):
            row["enrolled_at"] = date.fromisoformat(row["enrolled_at"])
            row["age"] = int(row["age"])
            db.add(PatientORM(**row))
        db.flush(); engine_ = DeviationEngine(load_protocol(sample / "protocol.json"))
        for row in csv.DictReader((sample / "visits.csv").open()):
            row["actual_date"] = date.fromisoformat(row["actual_date"]) if row["actual_date"] else None
            row["scheduled_date"] = date.fromisoformat(row["scheduled_date"]); row["dose_mg"] = float(row["dose_mg"]) if row["dose_mg"] else None
            row["medications"] = json.loads(row["medications"]); row["assessments"] = json.loads(row["assessments"]); row["query_resolution_days"] = int(row["query_resolution_days"])
            visit = Visit(**row); db.add(VisitORM(**visit.model_dump()))
            for dev in engine_.evaluate_rules(visit):
                dev.detected_at = datetime.combine(visit.actual_date or visit.scheduled_date, time(hour=12))
                db.add(DeviationORM(**dev.model_dump(mode="python")))
        db.commit()
