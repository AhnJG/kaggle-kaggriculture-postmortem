"""공통 machine-enforced gate 계약."""

from __future__ import annotations

SCHEMA_VERSION = 1
ALLOWED_VERDICTS = {"PASS", "FAILURE", "INCONCLUSIVE", "INVALID",
                    "ENGINE_MISMATCH", "IDENTITY_MISMATCH"}
REQUIRED_FIELDS = {
    "schema_version",
    "verdict",
    "gate_passed",
    "reasons",
    "engine_sha256",
    "artifact_sha256",
}


def document(*, verdict: str, gate_passed: bool, reasons: list[str],
             engine_sha256: str | None, artifact_sha256, payload,
             extra: dict | None = None):
    result = {
        "schema_version": SCHEMA_VERSION,
        "verdict": verdict,
        "gate_passed": bool(gate_passed),
        "reasons": list(reasons),
        "engine_sha256": engine_sha256,
        "artifact_sha256": artifact_sha256,
        "payload": payload,
    }
    if extra:
        result.update(extra)
    return result


def validate(doc: dict) -> list[str]:
    """Return missing/invalid schema fields; do not raise on bad input."""
    if not isinstance(doc, dict):
        return ["document is not an object"]
    missing = sorted(REQUIRED_FIELDS - set(doc))
    reasons = [f"missing field: {name}" for name in missing]
    if doc.get("schema_version") != SCHEMA_VERSION:
        reasons.append(f"schema_version must be {SCHEMA_VERSION}")
    if doc.get("verdict") not in ALLOWED_VERDICTS:
        reasons.append("verdict is not an allowed value")
    if not isinstance(doc.get("gate_passed"), bool):
        reasons.append("gate_passed must be boolean")
    if isinstance(doc.get("verdict"), str):
        expected_pass = doc["verdict"] == "PASS"
        if doc.get("gate_passed") is not expected_pass:
            reasons.append("gate_passed is inconsistent with verdict")
    if not isinstance(doc.get("reasons"), list):
        reasons.append("reasons must be a list")
    elif any(not isinstance(item, str) for item in doc["reasons"]):
        reasons.append("reasons entries must be strings")
    for field in ("engine_sha256", "artifact_sha256"):
        value = doc.get(field)
        values = value.values() if isinstance(value, dict) else (value,)
        for sha in values:
            if sha is not None and (not isinstance(sha, str) or
                                    len(sha) != 64 or
                                    any(c not in "0123456789abcdef" for c in sha)):
                reasons.append(f"{field} contains an invalid SHA-256")
                break
    return reasons


def exit_code(verdict: str) -> int:
    """Map a gate verdict to the documented require-pass exit contract."""
    if verdict == "PASS":
        return 0
    if verdict in {"FAILURE", "INCONCLUSIVE"}:
        return 2
    if verdict == "INVALID":
        return 3
    if verdict in {"ENGINE_MISMATCH", "IDENTITY_MISMATCH"}:
        return 4
    return 3
