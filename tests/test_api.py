import os
from pathlib import Path

os.environ["DATABASE_URL"] = f"sqlite:///{Path('/tmp/clinical-risk-test.db')}"

from fastapi.testclient import TestClient
from src.api.main import app


def test_health_and_seeded_endpoints():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        risks = client.get("/sites/risk").json()
        assert len(risks) == 200
        assert risks == sorted(risks, key=lambda x: x["score"], reverse=True)
        assert client.get("/deviations").status_code == 200

