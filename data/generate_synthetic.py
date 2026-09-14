#!/usr/bin/env python3
"""Generate deterministic, entirely fictional demo data (200 sites, 5,000 visits)."""
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "sample"
SEED = 20260915


def write_csv(name, rows):
    with (ROOT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)


def generate(site_count=200, visit_count=5000):
    random.seed(SEED); ROOT.mkdir(parents=True, exist_ok=True)
    today = date(2026, 9, 15); countries = ["US", "CA", "GB", "DE", "IN", "AU", "BR", "JP"]
    sites = [{"id": f"SITE-{i:03d}", "name": f"Synthetic Research Center {i:03d}", "country": countries[i % len(countries)],
              "last_monitoring_date": (today - timedelta(days=random.randint(5, 150))).isoformat(), "enrollment_target": 30} for i in range(1, site_count + 1)]
    patients = [{"id": f"SUBJ-{i:05d}", "site_id": sites[(i - 1) % site_count]["id"],
                 "enrolled_at": (today - timedelta(days=random.randint(60, 420))).isoformat(), "age": random.randint(18, 79),
                 "sex": random.choice(["F", "M", "X"])} for i in range(1, 1001)]
    visit_types = ["SCREENING", "BASELINE", "WEEK_4", "WEEK_8", "WEEK_12"]
    offsets = {"SCREENING": 0, "BASELINE": 7, "WEEK_4": 35, "WEEK_8": 63, "WEEK_12": 91}
    visits = []
    for i in range(visit_count):
        p = patients[i // 5]; kind = visit_types[i % 5]; scheduled = date.fromisoformat(p["enrolled_at"]) + timedelta(days=offsets[kind])
        actual = None if random.random() < .025 else scheduled + timedelta(days=random.choices(range(-10, 11), weights=[1,1,2,2,4,6,9,12,16,22,32,22,16,12,9,6,4,2,2,1,1])[0])
        dosed = kind != "SCREENING" and actual is not None
        dose = random.choice([80, 100, 100, 100, 120]) if dosed else None
        meds = ["acetaminophen"] + (["warfarin"] if random.random() < .012 else [])
        req = ["vitals", "adverse_events"] + (["cbc"] if kind in {"SCREENING", "WEEK_8"} else [])
        if random.random() < .04: req = req[:-1]
        visits.append({"id": f"VIS-{i+1:05d}", "patient_id": p["id"], "site_id": p["site_id"], "visit_type": kind,
            "scheduled_date": scheduled.isoformat(), "actual_date": actual.isoformat() if actual else "", "dose_mg": dose if dose is not None else "",
            "route": random.choice(["oral"] * 49 + ["intravenous"]) if dosed else "", "medications": json.dumps(meds),
            "assessments": json.dumps(req), "notes": "Participant reported no new concerns." if random.random() < .2 else "",
            "query_resolution_days": random.randint(0, 45)})
    write_csv("sites.csv", sites); write_csv("patients.csv", patients); write_csv("visits.csv", visits)
    protocol = {"protocol_id": "SYN-CTRM-001", "title": "Synthetic Phase III Demo Protocol", "banned_medications": ["warfarin", "rifampin"],
        "eligibility": {"min_age": 18, "max_age": 80}, "visit_rules": []}
    for name in visit_types:
        protocol["visit_rules"].append({"visit_type": name, "target_day": offsets[name], "window_days": 3 if name != "SCREENING" else 7,
            "dose_mg": None if name == "SCREENING" else 100, "dose_tolerance_pct": .05, "route": None if name == "SCREENING" else "oral",
            "required_assessments": ["vitals", "adverse_events"] + (["cbc"] if name in {"SCREENING", "WEEK_8"} else []), "clause": f"Section 5.{visit_types.index(name)+1} {name.title()} visit"})
    (ROOT / "protocol.json").write_text(json.dumps(protocol, indent=2))
    (ROOT / "README.md").write_text("# Synthetic demo data\n\nAll identities and records are deterministically generated and fictional. No PHI is present.\n")
    print(f"Generated {len(sites)} sites, {len(patients)} patients, and {len(visits)} visits")


if __name__ == "__main__": generate()

