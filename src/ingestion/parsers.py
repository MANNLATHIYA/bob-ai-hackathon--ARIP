import csv
import json
from pathlib import Path
from typing import Any

from src.api.models import ProtocolSpec


def read_json_or_csv(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else data.get("records", [])
    if path.suffix.lower() == ".csv":
        with path.open(newline="") as handle:
            return list(csv.DictReader(handle))
    raise ValueError("Only CSV and JSON visit files are supported")


def parse_hl7_like(text: str) -> list[dict[str, str]]:
    """Parse the demo's pipe-delimited VIS segments; no claim of full HL7 conformance."""
    records = []
    for line in text.splitlines():
        fields = line.strip().split("|")
        if fields and fields[0] == "VIS" and len(fields) >= 9:
            records.append(dict(zip(
                ["segment", "id", "patient_id", "site_id", "visit_type", "scheduled_date", "actual_date", "dose_mg", "route"],
                fields,
            )))
    return records


def load_protocol(path: str | Path) -> ProtocolSpec:
    return ProtocolSpec.model_validate_json(Path(path).read_text())
