from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.api.models import Deviation, ProtocolSpec, Visit

from .llm import LLMClient, get_llm
from .severity import classify


class DeviationEngine:
    def __init__(self, protocol: ProtocolSpec, llm: LLMClient | None = None):
        self.protocol = protocol
        self.llm = llm or get_llm()
        self.rules = {r.visit_type: r for r in protocol.visit_rules}

    def _deviation(self, visit: Visit, kind: str, description: str, clause: str, confidence: float = 1.0, source: str = "RULE") -> Deviation:
        severity, rationale = classify(kind, visit.notes)
        return Deviation(id=f"DEV-{uuid4().hex[:12]}", visit_id=visit.id, patient_id=visit.patient_id,
            site_id=visit.site_id, kind=kind, severity=severity, description=description,
            rationale=rationale, protocol_clause=clause, confidence=confidence,
            detected_at=datetime.now(timezone.utc).replace(tzinfo=None), source=source)

    def evaluate_rules(self, visit: Visit) -> list[Deviation]:
        rule = self.rules.get(visit.visit_type)
        if not rule:
            return [self._deviation(visit, "ADMIN_RECORD", f"Unknown visit type: {visit.visit_type}", "Protocol schedule")]
        out: list[Deviation] = []
        if visit.actual_date is None:
            out.append(self._deviation(visit, "MISSED_VISIT", "Required visit was not completed", rule.clause))
            return out
        day_delta = abs((visit.actual_date - visit.scheduled_date).days)
        if day_delta > rule.window_days:
            out.append(self._deviation(visit, "OUT_OF_WINDOW", f"Visit occurred {day_delta} days from scheduled date; allowed ±{rule.window_days}", rule.clause))
        if rule.dose_mg is not None:
            low, high = rule.dose_mg * (1 - rule.dose_tolerance_pct), rule.dose_mg * (1 + rule.dose_tolerance_pct)
            if visit.dose_mg is None or not low <= visit.dose_mg <= high:
                out.append(self._deviation(visit, "DOSE_ERROR", f"Dose {visit.dose_mg!r} mg is outside {low:.1f}–{high:.1f} mg", rule.clause))
        if rule.route and (visit.route or "").lower() != rule.route.lower():
            out.append(self._deviation(visit, "WRONG_ROUTE", f"Route {visit.route!r}; required {rule.route}", rule.clause))
        banned = {m.lower() for m in self.protocol.banned_medications}
        found = banned.intersection(m.lower() for m in visit.medications)
        if found:
            out.append(self._deviation(visit, "BANNED_MEDICATION", f"Banned concomitant medication: {', '.join(sorted(found))}", "Section 6.4 Prohibited therapy"))
        missing = set(rule.required_assessments) - set(visit.assessments)
        if missing:
            out.append(self._deviation(visit, "MISSING_ASSESSMENT", f"Missing required assessments: {', '.join(sorted(missing))}", rule.clause))
        return out

    async def evaluate(self, visit: Visit) -> list[Deviation]:
        out = self.evaluate_rules(visit)
        if visit.notes.strip():
            response = await self.llm.complete_json(
                "You review synthetic clinical notes. Do not infer facts. Return keys is_deviation, kind, severity, confidence, reason, clause.",
                f"Protocol: {self.protocol.model_dump_json()}\nVisit: {visit.model_dump_json()}"
            )
            if response.get("is_deviation") and float(response.get("confidence", 0)) >= .7:
                dev = self._deviation(visit, response.get("kind", "NOTE_REVIEW"), response.get("reason", "Narrative deviation"), response.get("clause", "Protocol narrative review"), float(response["confidence"]), "LLM")
                if response.get("severity") in {"MAJOR", "MINOR", "ADMINISTRATIVE"}:
                    dev.severity = response["severity"]
                    dev.rationale = response.get("reason", dev.rationale)
                out.append(dev)
        return out

