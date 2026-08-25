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
    print("public fixture validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
