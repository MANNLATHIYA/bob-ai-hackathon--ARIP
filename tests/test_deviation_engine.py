from datetime import date

from src.api.models import ProtocolSpec, Visit
from src.deviation_engine.engine import DeviationEngine


def protocol():
    return ProtocolSpec(protocol_id="P", title="Synthetic", banned_medications=["warfarin"], eligibility={}, visit_rules=[
        {"visit_type": "WEEK_4", "target_day": 28, "window_days": 3, "dose_mg": 100,
         "route": "oral", "required_assessments": ["vitals"], "clause": "5.3"}
    ])


def visit(**overrides):
    base = dict(id="V1", patient_id="P1", site_id="S1", visit_type="WEEK_4",
        scheduled_date=date(2026, 1, 1), actual_date=date(2026, 1, 1), dose_mg=100,
        route="oral", medications=[], assessments=["vitals"], notes="", query_resolution_days=0)
    base.update(overrides); return Visit(**base)


def test_compliant_visit_has_no_deviation():
    assert DeviationEngine(protocol()).evaluate_rules(visit()) == []


def test_detects_multiple_deviations_and_severity():
    found = DeviationEngine(protocol()).evaluate_rules(visit(actual_date=date(2026, 1, 8), dose_mg=80,
        route="iv", medications=["warfarin"], assessments=[]))
    assert {d.kind for d in found} == {"OUT_OF_WINDOW", "DOSE_ERROR", "WRONG_ROUTE", "BANNED_MEDICATION", "MISSING_ASSESSMENT"}
    assert all(d.protocol_clause for d in found)
    assert next(d for d in found if d.kind == "BANNED_MEDICATION").severity == "MAJOR"


def test_missed_visit_stops_non_applicable_checks():
    found = DeviationEngine(protocol()).evaluate_rules(visit(actual_date=None))
    assert [d.kind for d in found] == ["MISSED_VISIT"]

