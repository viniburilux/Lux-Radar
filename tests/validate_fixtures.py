from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
FIXTURES = ROOT / "fixtures"


def validate(payload: dict, schema_name: str, path: Path) -> None:
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path))
    if errors:
        details = "\n".join(f"{path}: {error.message} at {list(error.path)}" for error in errors)
        raise AssertionError(details)


def validate_product_views() -> None:
    data_dir = ROOT / "data"
    all_payload = json.loads((data_dir / "opportunities.json").read_text(encoding="utf-8"))
    current_payload = json.loads((data_dir / "current-opportunities.json").read_text(encoding="utf-8"))
    secondary_payload = json.loads((data_dir / "signals-history.json").read_text(encoding="utf-8"))
    all_records = all_payload.get("opportunities", [])
    current_records = current_payload.get("opportunities", [])
    secondary_records = secondary_payload.get("signals", [])
    all_ids = {record.get("opportunity_id") for record in all_records}
    current_ids = {record.get("opportunity_id") for record in current_records}
    secondary_ids = {record.get("opportunity_id") for record in secondary_records}
    if current_ids & secondary_ids or current_ids | secondary_ids != all_ids:
        raise AssertionError("product views do not partition the opportunity database")
    for record in current_records:
        if record.get("current_view") is not True or record.get("experience_type") != "OPPORTUNITY":
            raise AssertionError("current view contains a non-opportunity record")
        if record.get("status") in {"UNKNOWN", "CANDIDATE", "INSUFFICIENT_EVIDENCE"}:
            raise AssertionError("uncertain record surfaced in current view")


def main() -> int:
    for path in (FIXTURES / "observations").glob("*.json"):
        validate(json.loads(path.read_text()), "source-observation.schema.json", path)
    for path in (FIXTURES / "evidence").glob("*.json"):
        validate(json.loads(path.read_text()), "evidence.schema.json", path)
    for path in (FIXTURES / "normalized").glob("*.json"):
        validate(json.loads(path.read_text()), "normalized-record.schema.json", path)
    for path in (FIXTURES / "opportunities").glob("*.json"):
        validate(json.loads(path.read_text()), "opportunity.schema.json", path)
    for path in (FIXTURES / "releases").rglob("manifest.json"):
        validate(json.loads(path.read_text()), "release-manifest.schema.json", path)
    signals_path = ROOT / "data" / "signals.json"
    if signals_path.exists():
        signal_payload = json.loads(signals_path.read_text(encoding="utf-8"))
        for index, signal in enumerate(signal_payload.get("signals", [])):
            validate(signal, "derived-signal.schema.json", Path(f"{signals_path}#signals[{index}]"))
    validate_product_views()
    print("public fixture validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
