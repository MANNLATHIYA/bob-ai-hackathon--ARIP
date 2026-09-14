from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date

from src.api.models import Deviation, RiskBand, Site, SiteRisk, Visit


def _band(score: float) -> RiskBand:
    return RiskBand.CRITICAL if score >= 75 else RiskBand.HIGH if score >= 55 else RiskBand.MEDIUM if score >= 30 else RiskBand.LOW


def score_sites(sites: list[Site], visits: list[Visit], deviations: list[Deviation], today: date | None = None) -> list[SiteRisk]:
    today = today or date.today()
    v_by = defaultdict(list); d_by = defaultdict(list)
    for v in visits: v_by[v.site_id].append(v)
    for d in deviations: d_by[d.site_id].append(d)
    result = []
    for site in sites:
        sv, sd = v_by[site.id], d_by[site.id]
        major = sum(d.severity == "MAJOR" for d in sd)
        rate = len(sd) / max(len(sv), 1)
        weighted = sum({"MAJOR": 3, "MINOR": 1.5, "ADMINISTRATIVE": .5}.get(str(d.severity), 1) for d in sd) / max(len(sv), 1)
        days = max(0, (today - site.last_monitoring_date).days)
        slow_queries = sum(v.query_resolution_days for v in sv) / max(len(sv), 1)
        repeats = max(Counter(d.kind for d in sd).values(), default=0) / max(len(sd), 1)
        monthly = Counter(d.detected_at.strftime("%Y-%m") for d in sd)
        timeline = [{"month": m, "count": monthly[m]} for m in sorted(monthly)]
        counts = [x["count"] for x in timeline]
        trend = (counts[-1] - counts[-2]) / max(counts[-2], 1) if len(counts) > 1 else 0
        enrollment_velocity = len({v.patient_id for v in sv}) / max(site.enrollment_target, 1)
        score = 100 * (.25 * min(rate / .5, 1) + .25 * min(weighted / 1.2, 1) +
            .15 * min(max(trend, 0), 1) + .12 * min(days / 120, 1) +
            .10 * min(enrollment_velocity * rate / .35, 1) + .08 * repeats + .05 * min(slow_queries / 30, 1))
        result.append(SiteRisk(site_id=site.id, site_name=site.name, country=site.country,
            score=round(score, 1), band=_band(score), deviation_count=len(sd), major_count=major,
            trend=round(trend, 2), days_since_monitoring=days, monthly_trend=timeline))
    return sorted(result, key=lambda x: x.score, reverse=True)

