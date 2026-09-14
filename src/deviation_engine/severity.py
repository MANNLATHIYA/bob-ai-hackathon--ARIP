from src.api.models import Severity


def classify(kind: str, context: str = "") -> tuple[Severity, str]:
    text = context.lower()
    if kind in {"BANNED_MEDICATION", "WRONG_ROUTE", "DOSE_ERROR", "MISSED_VISIT"}:
        return Severity.MAJOR, "Potential impact on participant safety, primary data integrity, or trial validity."
    if any(term in text for term in ("hospital", "serious", "overdose", "pregnan")):
        return Severity.MAJOR, "Clinical narrative indicates a potential participant-safety impact."
    if kind in {"OUT_OF_WINDOW", "MISSING_ASSESSMENT"}:
        return Severity.MINOR, "Protocol departure detected without direct evidence of immediate safety impact."
    return Severity.ADMINISTRATIVE, "Documentation or process departure with no identified safety or data impact."

