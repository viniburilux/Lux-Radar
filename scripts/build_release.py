from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
from difflib import SequenceMatcher
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

try:
    from quality_layer import extract_quality_records, norm_url
except ModuleNotFoundError:
    from scripts.quality_layer import extract_quality_records, norm_url


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DEFAULT = ROOT / "config" / "sources.json"
DATA_DIR = ROOT / "data"
SITE_DATA_DIR = ROOT / "site" / "data"
USER_AGENT = "Lux-Radar-Public-Collector/0.1 (+https://github.com/viniburilux/Lux-Radar)"
TERMS = [
    "edital", "chamada", "call", "grant", "funding", "seleção", "selection",
    "programa", "program", "oportunidade", "opportunity", "proposta", "proposal",
    "prêmio", "award", "projeto", "project", "life", "sustainability", "climate",
]


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


CURRENT_QUALITY_STATES = {"VERIFIED", "OPEN", "UPCOMING", "EXTENDED", "ready_for_action", "verified_primary"}
CLOSED_STATES = {"CLOSED", "CANCELLED", "EXPIRED", "HISTORICAL", "expired", "superseded"}


def hash_bytes(body: bytes) -> str:
    return f"sha256:{hashlib.sha256(body).hexdigest()}"


def norm_text(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def norm_url(value: str | None) -> str:
    if not value:
        return ""
    parts = urlsplit(value)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), parts.query, ""))


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    return hash_bytes(text.encode("utf-8"))


def fetch_source(source: dict[str, Any]) -> dict[str, Any]:
    observed_at = now()
    try:
        response = requests.get(
            source["url"],
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/json,application/pdf;q=0.8"},
            timeout=30,
            allow_redirects=True,
        )
        body = response.content[:4_000_000]
        status = "success" if response.ok else "failed"
        fetch = {
            "status": status,
            "method": "http_get",
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type", "").split(";", 1)[0],
        }
        claims: list[dict[str, Any]] = []
        limitations = list(source.get("limitations", []))
        if response.ok and "html" in fetch["content_type"].lower():
            soup = BeautifulSoup(body, "html.parser")
            title_node = soup.find("h1") or soup.find("title")
            title = title_node.get_text(" ", strip=True) if title_node else source["name"]
            candidates: list[dict[str, Any]] = []
            seen: set[str] = set()
            domains = [term.lower() for term in source.get("domain", [])]
            for anchor in soup.find_all("a", href=True):
                label = re.sub(r"\s+", " ", anchor.get_text(" ", strip=True))
                url = urljoin(response.url, anchor["href"].strip())
                if not label or len(label) < 8 or not url.startswith(("http://", "https://")):
                    continue
                if url in seen:
                    continue
                haystack = f"{label} {url}".lower()
                score = sum(term in haystack for term in TERMS + domains)
                if score == 0:
                    continue
                seen.add(url)
                candidates.append({"title": label[:240], "url": url, "term_hits": score})
            candidates.sort(key=lambda item: (-item["term_hits"], item["title"]))
            claims = [
                {"path": "source.name", "value": source["name"], "epistemic_status": "observed"},
                {"path": "source.organization", "value": source.get("organization", source["name"]), "epistemic_status": "observed"},
                {"path": "source.domain", "value": source.get("domain", []), "epistemic_status": "observed"},
                {"path": "page.title", "value": title[:500], "epistemic_status": "observed"},
                {"path": "page.candidate_links", "value": candidates[:50], "epistemic_status": "observed"},
                {"path": "page.candidate_count", "value": len(candidates), "epistemic_status": "observed"},
            ]
            limitations.append("Generic public collector observes candidate links; detail pages require a later source-specific pass.")
        elif response.ok:
            limitations.append("Response was not HTML; the public builder retained metadata without candidate parsing.")
        else:
            limitations.append("HTTP failure was preserved; no retry or access bypass was attempted.")
        observation_id = f"{source['id']}:{status}:{response.status_code}"
        return {
            "observation_id": observation_id,
            "source_id": source["id"],
            "source_url": source["url"],
            "observed_at": observed_at,
            "source_profile": source.get("source_type", "public"),
            "fetch": fetch,
            "content": {"media_type": fetch["content_type"] or "application/octet-stream", "content_hash": hash_bytes(body), "byte_size": len(body)},
            "claims": claims,
            "evidence_ids": [],
            "collector": {"name": "public-html-opportunity", "version": "0.1.0", "repository": "https://github.com/viniburilux/Lux-Radar"},
            "limitations": sorted(set(limitations)),
            "license_or_terms_note": "Reference URLs and metadata only; external content remains governed by source terms.",
        }
    except requests.RequestException as exc:
        return {
            "observation_id": f"{source['id']}:failed:network",
            "source_id": source["id"],
            "source_url": source["url"],
            "observed_at": observed_at,
            "source_profile": source.get("source_type", "public"),
            "fetch": {"status": "failed", "method": "http_get", "http_status": None, "content_type": None},
            "content": {"media_type": "application/octet-stream", "content_hash": None, "byte_size": 0},
            "claims": [],
            "evidence_ids": [],
            "collector": {"name": "public-html-opportunity", "version": "0.1.0", "repository": "https://github.com/viniburilux/Lux-Radar"},
            "limitations": [f"Network failure: {type(exc).__name__}.", "No retry or access bypass was attempted."],
            "license_or_terms_note": "Reference URLs and metadata only; external content remains governed by source terms.",
        }


def parse_iso_datetime(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def classify_experience(record: dict[str, Any], reference_time: datetime | None = None) -> tuple[str, str, bool]:
    """Return (lifecycle_state, experience_type, current_view) without promoting uncertainty."""
    reference_time = reference_time or datetime.now(timezone.utc)
    status = str(record.get("status") or "UNKNOWN")
    deadline = parse_iso_datetime(record.get("deadline"))
    if status in CLOSED_STATES:
        return "HISTORICAL", "HISTORICAL", False
    if status not in CURRENT_QUALITY_STATES:
        return "SIGNAL", "SIGNAL", False
    if deadline and deadline < reference_time:
        return "HISTORICAL", "HISTORICAL", False
    if deadline and deadline <= reference_time + timedelta(days=30):
        return "CLOSING_SOON", "OPPORTUNITY", True
    if deadline and deadline > reference_time + timedelta(days=30):
        return "UPCOMING", "OPPORTUNITY", True
    if status in {"OPEN", "ready_for_action"}:
        return "ACTIVE", "OPPORTUNITY", True
    return "ONGOING", "OPPORTUNITY", True


def decorate_experience(records: list[dict[str, Any]], observed_at: str) -> list[dict[str, Any]]:
    reference_time = parse_iso_datetime(observed_at) or datetime.now(timezone.utc)
    for record in records:
        lifecycle_state, experience_type, current_view = classify_experience(record, reference_time)
        record["lifecycle_state"] = lifecycle_state
        record["experience_type"] = experience_type
        record["current_view"] = current_view
        events = [event for event in record.get("history", []) if event.get("at") == observed_at]
        if any(event.get("event") == "first_seen" for event in events):
            record["change_type"] = "NEW"
        elif any(event.get("event") in {"updated", "not_seen_in_release"} for event in events):
            record["change_type"] = "UPDATED"
        else:
            record["change_type"] = "UNCHANGED"
    return records


def claim_map(observation: dict[str, Any]) -> dict[str, Any]:
    return {item["path"]: item.get("value") for item in observation.get("claims", [])}


def evidence_for(observation: dict[str, Any], claim_paths: list[str]) -> dict[str, Any]:
    return {
        "evidence_id": f"evidence:{observation['source_id']}:{observation['content'].get('content_hash', 'nohash')[-16:]}",
        "evidence_type": "official_page",
        "source_name": observation["source_id"],
        "source_url": observation["source_url"],
        "source_role": "primary",
        "observed_at": observation["observed_at"],
        "observation_ids": [observation["observation_id"]],
        "content_hash": observation["content"].get("content_hash"),
        "supports_claims": claim_paths,
        "reliability": "observed_candidate",
        "limitations": observation.get("limitations", []),
        "access_notes": f"Fetch status: {observation['fetch']['status']}; HTTP {observation['fetch'].get('http_status')}.",
        "license_notes": "Reference URL only; review source terms before redistributing content.",
    }


def candidate_records(observations: list[dict[str, Any]], registry: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    source_by_id = {source["id"]: source for source in registry}
    evidences: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    normalized: list[dict[str, Any]] = []
    for observation in observations:
        if observation["fetch"]["status"] != "success":
            continue
        source = source_by_id.get(observation["source_id"], {})
        claims = claim_map(observation)
        evidence = evidence_for(observation, ["page.candidate_links", "source.organization", "source.domain"])
        candidate_links = claims.get("page.candidate_links", [])
        if not candidate_links:
            candidate_links = [{"title": claims.get("page.title", source.get("name", observation["source_id"])), "url": observation["source_url"], "term_hits": 0}]
        evidences.append(evidence)
        observation["evidence_ids"] = [evidence["evidence_id"]]
        for candidate in candidate_links[:50]:
            title = candidate.get("title") or source.get("name", observation["source_id"])
            url = candidate.get("url") or observation["source_url"]
            digest = hashlib.sha1(f"{observation['source_id']}|{norm_url(url)}".encode("utf-8")).hexdigest()[:16]
            record = {
                "opportunity_id": f"candidate-{digest}",
                "canonical_key": f"url:{norm_url(url)}",
                "title": title,
                "description": "Candidate observed on an official source page; detail verification pending.",
                "organization": source.get("organization", source.get("name", observation["source_id"])),
                "type": "opportunity_candidate",
                "domains": source.get("domain", []),
                "territories": [],
                "eligibility": [],
                "funding": {},
                "deadline": "",
                "status": "CANDIDATE",
                "verification": {"state": "CANDIDATE", "reason": "Candidate link observed on an official source page; detail verification pending."},
                "official_url": url,
                "source_id": observation["source_id"],
                "published_at": None,
                "updated_at": observation["observed_at"],
                "first_seen_at": observation["observed_at"],
                "last_seen_at": observation["observed_at"],
                "evidence": [evidence["evidence_id"]],
                "provenance": {"observation_ids": [observation["observation_id"]], "method": "official page candidate link", "limitations": observation.get("limitations", [])},
                "confidence": 0.55,
            }
            records.append(record)
            normalized.append({
                "normalized_id": f"normalized:{record['opportunity_id']}",
                "record_type": "opportunity_candidate",
                "opportunity_id": record["opportunity_id"],
                "normalized_at": observation["observed_at"],
                "source_observation_ids": [observation["observation_id"]],
                "evidence_ids": [evidence["evidence_id"]],
                "fields": {"title": title, "official_url": url, "organization": record["organization"]},
                "provenance": {"method": "claim-preserving public page normalization", "limitations": record["provenance"]["limitations"]},
            })
    return records, evidences, normalized


def records_match(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_url = norm_url(left.get("official_url"))
    right_url = norm_url(right.get("official_url"))
    if left_url and left_url == right_url:
        return True
    left_pdf = norm_url(left.get("official_pdf_url"))
    right_pdf = norm_url(right.get("official_pdf_url"))
    if left_pdf and right_pdf and left_pdf == right_pdf:
        return True
    title_similarity = SequenceMatcher(None, norm_text(left.get("title")), norm_text(right.get("title"))).ratio()
    left_org = norm_text(left.get("organization"))
    right_org = norm_text(right.get("organization"))
    left_deadline = left.get("deadline") or ""
    right_deadline = right.get("deadline") or ""
    return title_similarity >= 0.93 and left_org and left_org == right_org and (not left_deadline or not right_deadline or left_deadline == right_deadline)


def merge_record_metadata(target: dict[str, Any], record: dict[str, Any]) -> None:
    target["evidence"] = sorted(set(target.get("evidence", [])) | set(record.get("evidence", [])))
    target["evidence_ids"] = sorted(set(target.get("evidence_ids", [])) | set(record.get("evidence_ids", [])))
    target.setdefault("provenance", {}).setdefault("observation_ids", [])
    target["provenance"]["observation_ids"] = sorted(set(target["provenance"].get("observation_ids", [])) | set(record.get("provenance", {}).get("observation_ids", [])))
    target["provenance"]["limitations"] = sorted(set(target["provenance"].get("limitations", [])) | set(record.get("provenance", {}).get("limitations", [])))
    target["sources"] = sorted({source for source in (set(target.get("sources", [])) | set(record.get("sources", [])) | {target.get("source_id", ""), record.get("source_id", "")}) if source})
    if record.get("status") in {"VERIFIED", "CLOSED", "INSUFFICIENT_EVIDENCE"} or target.get("status") in {"UNKNOWN", "CANDIDATE"}:
        for field in ["title", "description", "organization", "type", "domains", "territories", "eligibility", "funding", "deadline", "status", "verification", "official_url", "official_pdf_url", "updated_at", "last_seen_at", "confidence"]:
            if field in record and record[field] not in (None, "", [], {}):
                target[field] = record[field]


def dedupe(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    consolidated: list[dict[str, Any]] = []
    for record in records:
        match = next((existing for existing in consolidated if records_match(existing, record)), None)
        if match is None:
            item = dict(record)
            item["sources"] = sorted({source for source in item.get("sources", [item.get("source_id", "")]) if source})
            consolidated.append(item)
            continue
        merge_record_metadata(match, record)
    return consolidated


def merge_history(incoming: list[dict[str, Any]], previous: list[dict[str, Any]], observed_at: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    previous_by_key = {item.get("canonical_key"): item for item in previous}
    output: list[dict[str, Any]] = []
    stats = {"new": 0, "updated": 0, "closed": 0}
    seen: set[str] = set()
    for candidate in dedupe(incoming):
        key = candidate["canonical_key"]
        old = previous_by_key.get(key)
        if not old:
            old = next((item for item in previous if records_match(item, candidate)), None)
        if not old:
            candidate["first_seen_at"] = observed_at
            candidate["history"] = [{"at": observed_at, "event": "first_seen", "status": candidate["status"]}]
            candidate["sources"] = [candidate["source_id"]]
            stats["new"] += 1
        else:
            candidate["first_seen_at"] = old.get("first_seen_at", observed_at)
            candidate["history"] = old.get("history", [])
            candidate["sources"] = sorted(set(old.get("sources", [old.get("source_id", "")])) | set(candidate.get("sources", [candidate["source_id"]])))
            if old.get("status") != candidate.get("status") or old.get("title") != candidate.get("title"):
                candidate["history"].append({"at": observed_at, "event": "updated", "before": {"status": old.get("status")}, "after": {"status": candidate.get("status")}})
                stats["updated"] += 1
        candidate["last_seen_at"] = observed_at
        candidate["updated_at"] = observed_at
        seen.add(key)
        if old and old.get("canonical_key"):
            seen.add(old["canonical_key"])
        output.append(candidate)
    for old in previous:
        key = old.get("canonical_key")
        if key not in seen and old.get("status") not in {"CLOSED", "CANCELLED"}:
            item = dict(old)
            item["status"] = "UNKNOWN"
            item["updated_at"] = observed_at
            item.setdefault("history", []).append({"at": observed_at, "event": "not_seen_in_release", "status": "UNKNOWN"})
            output.append(item)
            stats["updated"] += 1
    return output, stats


def csv_value(value: Any) -> str:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return "" if value is None else str(value)


def write_csv(path: Path, records: list[dict[str, Any]]) -> str:
    columns = ["opportunity_id", "title", "description", "organization", "type", "domains", "territories", "eligibility", "funding", "deadline", "status", "lifecycle_state", "experience_type", "current_view", "change_type", "official_url", "official_pdf_url", "sources", "source_id", "published_at", "updated_at", "first_seen_at", "last_seen_at", "confidence"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow({column: csv_value(record.get(column, "")) for column in columns})
    return hash_bytes(path.read_bytes())


def run(args: argparse.Namespace) -> int:
    registry_payload = load_json(args.registry, {"sources": []})
    registry = [source for source in registry_payload.get("sources", []) if source.get("enabled", True)]
    if args.limit_sources:
        registry = registry[: args.limit_sources]
    observed_at = now()
    observations = [fetch_source(source) for source in registry]
    candidate_incoming, candidate_evidences, candidate_normalized = candidate_records(observations, registry)
    quality_observations, quality_evidences, quality_normalized, quality_records, _details = extract_quality_records(observations, registry)
    detail_urls = {norm_url(record.get("official_url", "")) for record in quality_records}
    incoming = [record for record in candidate_incoming if norm_url(record.get("official_url", "")) not in detail_urls]
    incoming.extend(quality_records)
    evidences = candidate_evidences + quality_evidences
    normalized = candidate_normalized + quality_normalized
    observations = quality_observations
    previous_payload = load_json(DATA_DIR / "opportunities.json", {"opportunities": []})
    previous = previous_payload.get("opportunities", []) if isinstance(previous_payload, dict) else previous_payload
    collected_count = len(incoming)
    deduped_incoming = dedupe(incoming)
    duplicate_consolidated = max(collected_count - len(deduped_incoming), 0)
    database, stats = merge_history(deduped_incoming, previous, observed_at)
    database = decorate_experience(database, observed_at)
    current_records = [item for item in database if item.get("current_view") is True]
    signals_history = [item for item in database if item.get("current_view") is not True]
    failed = [item for item in observations if item["fetch"]["status"] in {"failed", "blocked"}]
    release_id = args.release_id or f"weekly-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    artifact_specs = [
        ("observations", "observations", observations, "application/json"),
        ("evidence", "evidence", evidences, "application/json"),
        ("normalized", "normalized", normalized, "application/json"),
        ("opportunities", "opportunities", database, "application/json"),
        ("current-opportunities", "opportunities", current_records, "application/json"),
        ("signals-history", "signals", signals_history, "application/json"),
    ]
    artifacts: list[dict[str, Any]] = []
    for name, payload_key, payload, media_type in artifact_specs:
        ref = f"data/{name}.json"
        digest = save_json(DATA_DIR / f"{name}.json", {"release_id": release_id, payload_key: payload})
        artifacts.append({"kind": name, "ref": ref, "content_hash": digest, "media_type": media_type})
    csv_digest = write_csv(DATA_DIR / "opportunities.csv", database)
    artifacts.append({"kind": "opportunities_csv", "ref": "data/opportunities.csv", "content_hash": csv_digest, "media_type": "text/csv"})
    site_data = SITE_DATA_DIR
    site_data.mkdir(parents=True, exist_ok=True)
    for filename in ["observations.json", "evidence.json", "normalized.json", "opportunities.json", "current-opportunities.json", "signals-history.json"]:
        (site_data / filename).write_text((DATA_DIR / filename).read_text(encoding="utf-8"), encoding="utf-8")
    (site_data / "opportunities.csv").write_bytes((DATA_DIR / "opportunities.csv").read_bytes())
    manifest = {
        "release_id": release_id,
        "created_at": observed_at,
        "source_ids": [source["id"] for source in registry],
        "observation_window": {"started_at": min((item["observed_at"] for item in observations), default=observed_at), "ended_at": max((item["observed_at"] for item in observations), default=observed_at)},
        "record_counts": {"observations": len(observations), "evidence": len(evidences), "normalized": len(normalized), "opportunities": len(database), "current_opportunities": len(current_records), "signals_history": len(signals_history), "moved_to_history_or_signals": len(signals_history), "closing_soon": sum(item.get("lifecycle_state") == "CLOSING_SOON" for item in database), "new_current": sum(item.get("current_view") is True and item.get("change_type") == "NEW" for item in database), "deduplicated": duplicate_consolidated, "collected": collected_count, "new": stats["new"], "updated": stats["updated"], "closed": stats["closed"], "unchanged": max(len(database) - stats["new"] - stats["updated"], 0), "failed": len(failed), "total_candidates": sum(item.get("status") == "CANDIDATE" for item in database), "total_verified": sum(item.get("status") == "VERIFIED" for item in database), "total_closed": sum(item.get("status") == "CLOSED" for item in database), "total_unknown": sum(item.get("status") == "UNKNOWN" for item in database), "total_insufficient_evidence": sum(item.get("status") == "INSUFFICIENT_EVIDENCE" for item in database)},
        "artifacts": artifacts,
        "source_status": {item["source_id"]: item["fetch"]["status"] for item in observations},
        "errors": [{"source_id": item["source_id"], "status": item["fetch"]["status"], "http_status": item["fetch"].get("http_status"), "limitations": item.get("limitations", [])} for item in failed],
        "producer": {"name": "lux-radar-public-builder", "version": "0.1.0", "repository": "https://github.com/viniburilux/Lux-Radar"},
        "limitations": ["The current opportunity view requires a quality state and temporal evidence; UNKNOWN, CANDIDATE and INSUFFICIENT_EVIDENCE remain outside it.", "Generic HTML extraction is candidate-level; detail verification remains source-specific.", "External content is referenced, not redistributed by default.", "A source failure does not imply absence of opportunities."],
    }
    save_json(DATA_DIR / "release-manifest.json", manifest)
    (site_data / "release-manifest.json").write_text((DATA_DIR / "release-manifest.json").read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps({"release_id": release_id, "counts": manifest["record_counts"], "source_status": manifest["source_status"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY_DEFAULT)
    parser.add_argument("--release-id")
    parser.add_argument("--limit-sources", type=int)
    raise SystemExit(run(parser.parse_args()))
