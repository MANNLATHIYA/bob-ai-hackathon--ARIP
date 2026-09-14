from datetime import date, datetime

from src.api.models import Deviation, Severity, Site, Visit
from src.risk_scoring.scorer import score_sites


def test_high_severity_site_ranks_first():
    sites = [Site(id=x, name=x, country="US", last_monitoring_date=date(2025, 1, 1), enrollment_target=10) for x in ["A", "B"]]
    visits = [Visit(id=f"V{x}", patient_id="P", site_id=x, visit_type="X", scheduled_date=date.today(), actual_date=date.today(), dose_mg=None, route=None) for x in ["A", "B"]]
    dev = Deviation(id="D", visit_id="VA", patient_id="P", site_id="A", kind="DOSE_ERROR", severity=Severity.MAJOR,
        description="x", rationale="x", protocol_clause="5", confidence=1, detected_at=datetime.now(), source="RULE")
    scored = score_sites(sites, visits, [dev], today=date(2026, 1, 1))
    assert scored[0].site_id == "A"
    assert 0 <= scored[0].score <= 100
