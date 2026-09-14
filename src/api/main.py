from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, time
from io import BytesIO
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.capa_generator.generator import CAPAGenerator, to_docx, to_pdf
from src.risk_scoring import score_sites

from .database import get_db, init_db
from .models import (CAPAReportORM, CAPARequest, Deviation, DeviationORM, Patient,
                     PatientORM, Site, SiteORM, Visit, VisitORM)
from .seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db(); await seed_database(); yield


app = FastAPI(title="Clinical Trial Risk Monitor API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health(): return {"status": "ok", "data": "synthetic-only"}


@app.get("/patients", response_model=list[Patient])
def patients(limit: int = Query(100, le=1000), offset: int = 0, site_id: str | None = None, db: Session = Depends(get_db)):
    query = select(PatientORM).offset(offset).limit(limit)
    if site_id: query = query.where(PatientORM.site_id == site_id)
    return db.scalars(query).all()


@app.get("/visits", response_model=list[Visit])
def visits(limit: int = Query(100, le=1000), offset: int = 0, site_id: str | None = None, db: Session = Depends(get_db)):
    query = select(VisitORM).offset(offset).limit(limit)
    if site_id: query = query.where(VisitORM.site_id == site_id)
    return db.scalars(query).all()


@app.get("/deviations", response_model=list[Deviation])
def deviations(limit: int = Query(200, le=1000), offset: int = 0, severity: str | None = None,
               site_id: str | None = None, date_from: str | None = None, date_to: str | None = None,
               db: Session = Depends(get_db)):
    query = select(DeviationORM).order_by(DeviationORM.detected_at.desc())
    if severity: query = query.where(DeviationORM.severity == severity.upper())
    if site_id: query = query.where(DeviationORM.site_id == site_id)
    if date_from:
        query = query.where(DeviationORM.detected_at >= datetime.combine(datetime.fromisoformat(date_from).date(), time.min))
    if date_to:
        query = query.where(DeviationORM.detected_at <= datetime.combine(datetime.fromisoformat(date_to).date(), time.max))
    return db.scalars(query.offset(offset).limit(limit)).all()


@app.get("/sites/risk")
def risks(db: Session = Depends(get_db)):
    sites = [Site.model_validate(x) for x in db.scalars(select(SiteORM)).all()]
    visits_ = [Visit.model_validate(x) for x in db.scalars(select(VisitORM)).all()]
    deviations_ = [Deviation.model_validate(x) for x in db.scalars(select(DeviationORM)).all()]
    return score_sites(sites, visits_, deviations_)


@app.get("/sites/{site_id}")
def site_detail(site_id: str, db: Session = Depends(get_db)):
    site = db.get(SiteORM, site_id)
    if not site: raise HTTPException(404, "Site not found")
    site_devs = [Deviation.model_validate(x) for x in db.scalars(select(DeviationORM).where(DeviationORM.site_id == site_id)).all()]
    site_visits = [Visit.model_validate(x) for x in db.scalars(select(VisitORM).where(VisitORM.site_id == site_id)).all()]
    return {"site": Site.model_validate(site), "risk": score_sites([Site.model_validate(site)], site_visits, site_devs)[0], "deviations": site_devs[:100]}


@app.post("/capa/generate")
async def generate_capa(request: CAPARequest, db: Session = Depends(get_db)):
    dev = db.get(DeviationORM, request.deviation_id) if request.deviation_id else db.scalar(select(DeviationORM).where(DeviationORM.site_id == request.site_id).order_by(DeviationORM.detected_at.desc()))
    if not dev: raise HTTPException(404, "No matching deviation found")
    content = await CAPAGenerator().generate(Deviation.model_validate(dev))
    report = CAPAReportORM(id=f"CAPA-{uuid4().hex[:12]}", deviation_id=dev.id, site_id=dev.site_id, content=content)
    db.add(report); db.commit()
    fmt = request.format.lower()
    if fmt == "pdf":
        return StreamingResponse(BytesIO(to_pdf(content)), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{report.id}.pdf"'})
    if fmt == "docx":
        return StreamingResponse(BytesIO(to_docx(content)), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": f'attachment; filename="{report.id}.docx"'})
    return {"id": report.id, "site_id": report.site_id, "deviation_id": report.deviation_id, "content": content}


@app.post("/admin/reseed", include_in_schema=False)
async def reseed(db: Session = Depends(get_db)):
    db.close(); await seed_database(force=True); return {"status": "reseeded"}
