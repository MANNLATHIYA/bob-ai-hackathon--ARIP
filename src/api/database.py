import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .models import Base

ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'clinical_trial.db'}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session

