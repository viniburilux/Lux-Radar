from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import re
import unicodedata
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = "Lux-Radar-Environmental-Signal-Engine/1.0 (+https://github.com/viniburilux/Lux-Radar)"
MAX_PUBLISHED_ENTITY_SIGNALS = 600

ENVIRONMENTAL_SOURCE_IDS = {
    "inpe-queimadas",
    "gbif-occurrences",
    "nasa-eonet",
    "ibge-localidades-api",
    "open-meteo",
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def content_hash(body: bytes) -> str:
    return f"sha256:{hashlib.sha256(body).hexdigest()}"


def json_hash(payload: Any) -> str:
    return content_hash(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def clean(value: Any, limit: int = 500) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def norm_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def as_float(value: Any) -> float | None:
    if value in (None, "", "null"):
        return None
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None


def iso_value(value: Any) -> str | None:
    if isinstance(value, bool):
        return None
    text = clean(value, 80)
    if not text:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", text):
        return text.replace(" ", "T") + "Z"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", text):
        return text.replace(" ", "T") + ":00Z"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text + "T00:00:00Z"
    if text.endswith("Z") or "+" in text[10:]:
        return text
    return text


def claim(path: str, value: Any, *, confidence: float = 1.0, epistemic_status: str = "observed") -> dict[str, Any]:
    return {"path": path, "value": value, "confidence": confidence, "epistemic_status": epistemic_status}


def claim_map(observation: dict[str, Any]) -> dict[str, Any]:
    return {item.get("path"): item.get("value") for item in observation.get("claims", []) if item.get("path")}


def _base_observation(source: dict[str, Any], observed_at: str, source_profile: str, method: str, response: requests.Response | None, body: bytes, claims: list[dict[str, Any]], limitations: list[str], request_parameters: dict[str, Any] | None = None, pagination: dict[str, Any] | None = None, observation_suffix: str = "") -> dict[str, Any]:
    status = "success" if response is not None and response.ok else "failed"
    http_status = response.status_code if response is not None else None
    content_type = response.headers.get("content-type", "").split(";", 1)[0] if response is not None else None
    suffix = observation_suffix or (str(http_status) if http_status is not None else "network")
    fetch: dict[str, Any] = {"status": status, "method": method, "http_status": http_status, "content_type": content_type}
    if request_parameters:
        fetch["request_parameters"] = request_parameters
    if pagination:
        fetch["pagination"] = pagination
    return {
        "observation_id": f"{source['id']}:success:{suffix}" if status == "success" else f"{source['id']}:failed:{suffix}",
        "source_id": source["id"],
        "source_url": source["url"],
        "observed_at": observed_at,
        "source_profile": source_profile,
        "fetch": fetch,
        "content": {"media_type": content_type or "application/octet-stream", "content_hash": content_hash(body) if body else None, "byte_size": len(body)},
        "claims": claims,
        "evidence_ids": [],
        "collector": {"name": source.get("collector", source["id"]), "version": "1.0.0", "repository": "https://github.com/viniburilux/Lux-Radar"},
        "limitations": sorted(set(limitations)),
        "license_or_terms_note": source.get("license_or_terms_note", "Reference URLs and selected structured claims only; source terms remain applicable."),
    }


def _failed(source: dict[str, Any], observed_at: str, method: str, exc: Exception | None = None, response: requests.Response | None = None) -> dict[str, Any]:
    reason = f"Network failure: {type(exc).__name__}." if exc else f"HTTP failure: {response.status_code}." if response is not None else "Source parsing failure."
    return _base_observation(
        source,
        observed_at,
        "api" if source["id"] != "inpe-queimadas" else "csv",
        method,
        response,
        b"",
        [],
        [reason, "No retry, access bypass, or content redistribution was attempted."],
    )


def _request(url: str, *, params: dict[str, Any] | None = None, timeout: int = 60) -> requests.Response:
    return requests.get(url, params=params, headers={"User-Agent": USER_AGENT, "Accept": "application/json,text/csv,text/html;q=0.8"}, timeout=timeout, allow_redirects=True)


def parse_inpe(source: dict[str, Any], observed_at: str) -> dict[str, Any]:
    try:
        directory = _request(source["url"], timeout=45)
        if not directory.ok:
            return _failed(source, observed_at, "http_get", response=directory)
        soup = BeautifulSoup(directory.text, "html.parser")
        links = sorted({anchor.get("href", "") for anchor in soup.find_all("a", href=True) if anchor.get("href", "").lower().endswith(".csv")})
        if not links:
            return _base_observation(source, observed_at, "csv", "http_get", directory, directory.content, [], ["Directory responded but no daily CSV file was exposed."])
        latest_name = links[-1]
        latest_url = latest_name if latest_name.startswith("http") else source["url"].rstrip("/") + "/" + latest_name.lstrip("/")
        response = _request(latest_url, timeout=90)
        if not response.ok:
            return _failed(source, observed_at, "http_get", response=response)
        text = response.content.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text), delimiter=",")
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in reader:
            item_id = clean(raw.get("id"), 120)
            if not item_id or item_id in seen:
                continue
            seen.add(item_id)
            latitude = as_float(raw.get("lat"))
            longitude = as_float(raw.get("lon"))
            item = {
                "key": item_id,
                "entity_type": "fire_hotspot",
                "occurred_at": iso_value(raw.get("data_hora_gmt")),
                "location": {"latitude": latitude, "longitude": longitude} if latitude is not None and longitude is not None else None,
                "municipality_id": clean(raw.get("municipio_id"), 40) or None,
                "municipality": clean(raw.get("municipio"), 160) or None,
                "state": clean(raw.get("estado"), 80) or None,
                "country": clean(raw.get("pais"), 80) or None,
                "biome": clean(raw.get("bioma"), 120) or None,
                "satellite": clean(raw.get("satelite"), 80) or None,
                "dry_days": as_float(raw.get("numero_dias_sem_chuva")),
                "precipitation_mm": as_float(raw.get("precipitacao")),
                "fire_risk": as_float(raw.get("risco_fogo")),
                "frp": as_float(raw.get("frp")),
            }
            rows.append(item)
        grouped: dict[str, dict[str, Any]] = {}
        for item in rows:
            group_key = item.get("municipality_id") or f"{norm_text(item.get('municipality'))}|{norm_text(item.get('state'))}"
            group = grouped.setdefault(group_key, {"key": group_key, "municipality_id": item.get("municipality_id"), "municipality": item.get("municipality"), "state": item.get("state"), "biome": item.get("biome"), "count": 0, "total_frp": 0.0, "max_frp": None, "latest_occurred_at": None})
            group["count"] += 1
            if item.get("frp") is not None:
                group["total_frp"] += item["frp"]
                group["max_frp"] = max(group["max_frp"] or item["frp"], item["frp"])
            if item.get("occurred_at") and (not group["latest_occurred_at"] or item["occurred_at"] > group["latest_occurred_at"]):
                group["latest_occurred_at"] = item["occurred_at"]
        frps = [item["frp"] for item in rows if item.get("frp") is not None]
        metrics = {
            "file": latest_name,
            "file_count": len(links),
            "entity_count": len(rows),
            "municipality_count": len({item.get("municipality_id") or f"{norm_text(item.get('municipality'))}|{norm_text(item.get('state'))}" for item in rows}),
            "biome_count": len({item.get("biome") for item in rows if item.get("biome")}),
            "frp_total": round(sum(frps), 3),
            "frp_mean": round(sum(frps) / len(frps), 3) if frps else None,
            "frp_max": max(frps) if frps else None,
            "top_territories": sorted(grouped.values(), key=lambda group: (-group["count"], -group["total_frp"], group["key"]))[:20],
        }
        body = response.content
        claims = [
            claim("environmental.signal_type", "FIRE_ACTIVITY"),
            claim("environmental.entity_key", "id"),
            claim("environmental.entity_items", rows),
            claim("environmental.metrics", metrics),
            claim("environmental.file_url", response.url),
            claim("source.name", source["name"]),
        ]
        return _base_observation(source, observed_at, "csv", "http_get", response, body, claims, ["CSV diário oficial parseado com delimitador vírgula; os focos são detecções, não necessariamente incêndios distintos.", "Histórico completo não é baixado; somente o arquivo diário mais recente é observado nesta versão.", "FRP e risco são preservados como medidas observadas, sem inferir anomalia ou causalidade."], {"directory_url": source["url"], "selected_file": latest_name}, {"page": 1, "page_size": len(rows), "has_more": False}, latest_name)
    except requests.RequestException as exc:
        return _failed(source, observed_at, "http_get", exc=exc)
    except (csv.Error, UnicodeError) as exc:
        return _base_observation(source, observed_at, "csv", "http_get", None, b"", [], [f"CSV parsing failure: {type(exc).__name__}.", "No record was promoted from this observation."])


def parse_gbif(source: dict[str, Any], observed_at: str) -> dict[str, Any]:
    try:
        response = _request(source["url"], timeout=90)
        if not response.ok:
            return _failed(source, observed_at, "rest_api", response=response)
        payload = response.json()
        results = payload.get("results", []) if isinstance(payload, dict) else []
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in results:
            key = clean(raw.get("key") or raw.get("gbifID"), 120)
            if not key or key in seen:
                continue
            seen.add(key)
            lat = as_float(raw.get("decimalLatitude"))
            lon = as_float(raw.get("decimalLongitude"))
            item = {
                "key": key,
                "entity_type": "biodiversity_occurrence",
                "occurred_at": iso_value(raw.get("eventDate") or raw.get("year")),
                "location": {"latitude": lat, "longitude": lon} if lat is not None and lon is not None else None,
                "municipality": clean(raw.get("municipality"), 160) or None,
                "state": clean(raw.get("stateProvince"), 120) or None,
                "country": clean(raw.get("country"), 80) or None,
                "taxon_key": raw.get("taxonKey"),
                "scientific_name": clean(raw.get("scientificName") or raw.get("species") or raw.get("genus"), 240) or None,
                "taxon_rank": clean(raw.get("rank"), 80) or None,
                "occurrence_status": clean(raw.get("occurrenceStatus"), 80) or None,
                "license": clean(raw.get("license"), 240) or None,
                "dataset_name": clean(raw.get("datasetName"), 240) or None,
                "publishing_org_key": clean(raw.get("publishingOrgKey"), 120) or None,
                "modified": iso_value(raw.get("modified")),
                "last_crawled": iso_value(raw.get("lastCrawled")),
                "last_interpreted": iso_value(raw.get("lastInterpreted")),
                "references": clean(raw.get("references"), 500) or None,
            }
            items.append(item)
        metrics = {
            "page_count": len(items),
            "reported_count": payload.get("count") if isinstance(payload, dict) else None,
            "offset": payload.get("offset") if isinstance(payload, dict) else None,
            "limit": payload.get("limit") if isinstance(payload, dict) else None,
            "end_of_records": payload.get("endOfRecords") if isinstance(payload, dict) else None,
            "taxon_count": len({item.get("taxon_key") or item.get("scientific_name") for item in items if item.get("taxon_key") or item.get("scientific_name")}),
            "municipality_count": len({f"{norm_text(item.get('municipality'))}|{norm_text(item.get('state'))}" for item in items if item.get("municipality") or item.get("state")}),
            "licenses": dict(Counter(item.get("license") or "UNKNOWN" for item in items)),
        }
        claims = [claim("environmental.signal_type", "BIODIVERSITY_OCCURRENCE"), claim("environmental.entity_key", "key"), claim("environmental.entity_items", items), claim("environmental.metrics", metrics), claim("api.reported_count", payload.get("count")), claim("source.name", source["name"])]
        return _base_observation(source, observed_at, "api", "rest_api", response, response.content, claims, ["Somente uma página limitada é coletada; `reported_count` não é baixado integralmente.", "Licença e proveniência são preservadas por ocorrência quando fornecidas.", "Ocorrência de biodiversidade não é convertida em risco, ameaça ou oportunidade."], {"country": "BR", "limit": payload.get("limit", len(items)), "offset": payload.get("offset", 0)}, {"page": 1, "page_size": len(items), "has_more": not bool(payload.get("endOfRecords", True))}, str(response.status_code))
    except (requests.RequestException, ValueError) as exc:
        return _failed(source, observed_at, "rest_api", exc=exc if isinstance(exc, requests.RequestException) else None)


def _find_coordinate(value: Any) -> tuple[float, float] | None:
    if isinstance(value, list) and len(value) >= 2 and all(isinstance(part, (int, float)) for part in value[:2]):
        return float(value[1]), float(value[0])
    if isinstance(value, list):
        for child in value:
            found = _find_coordinate(child)
            if found:
                return found
    return None


def parse_eonet(source: dict[str, Any], observed_at: str) -> dict[str, Any]:
    try:
        response = _request(source["url"], timeout=60)
        if not response.ok:
            return _failed(source, observed_at, "rest_api", response=response)
        payload = response.json()
        raw_events = payload.get("events", []) if isinstance(payload, dict) else []
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in raw_events:
            event_id = clean(raw.get("id"), 120)
            if not event_id or event_id in seen:
                continue
            seen.add(event_id)
            geometries = raw.get("geometry") if isinstance(raw.get("geometry"), list) else []
            latest_geometry = geometries[-1] if geometries else {}
            lat_lon = _find_coordinate(latest_geometry.get("coordinates")) if isinstance(latest_geometry, dict) else None
            categories = [{"id": clean(category.get("id"), 80), "title": clean(category.get("title"), 160)} for category in raw.get("categories", []) if isinstance(category, dict)]
            sources = [{"id": clean(item.get("id"), 120), "url": clean(item.get("url"), 500)} for item in raw.get("sources", []) if isinstance(item, dict)]
            item = {
                "key": event_id,
                "entity_type": "natural_event",
                "title": clean(raw.get("title"), 300),
                "description": clean(raw.get("description"), 1000) or None,
                "status": "CLOSED" if raw.get("closed") else "OPEN",
                "occurred_at": iso_value(latest_geometry.get("date") if isinstance(latest_geometry, dict) else None) or iso_value(raw.get("closed")) or iso_value(raw.get("date")),
                "closed_at": iso_value(raw.get("closed")),
                "location": {"latitude": lat_lon[0], "longitude": lat_lon[1]} if lat_lon else None,
                "categories": categories,
                "sources": sources,
                "geometry_type": latest_geometry.get("type") if isinstance(latest_geometry, dict) else None,
                "geometry_date": iso_value(latest_geometry.get("date")) if isinstance(latest_geometry, dict) else None,
                "link": clean(raw.get("link"), 500) or None,
            }
            items.append(item)
        metrics = {"entity_count": len(items), "open_count": sum(item.get("status") == "OPEN" for item in items), "closed_count": sum(item.get("status") == "CLOSED" for item in items), "categories": dict(Counter(category.get("title") for item in items for category in item.get("categories", []) if category.get("title")))}
        claims = [claim("environmental.signal_type", "NATURAL_EVENT"), claim("environmental.entity_key", "id"), claim("environmental.entity_items", items), claim("environmental.metrics", metrics), claim("source.name", source["name"])]
        return _base_observation(source, observed_at, "api", "rest_api", response, response.content, claims, ["Eventos e geometrias são observados conforme o snapshot EONET; ausência no snapshot não prova que o fenômeno deixou de existir.", "Status aberto/encerrado é preservado, mas não transforma evento natural em oportunidade."], {"status": "open", "limit": len(items)}, {"page": 1, "page_size": len(items), "has_more": False}, str(response.status_code))
    except (requests.RequestException, ValueError) as exc:
        return _failed(source, observed_at, "rest_api", exc=exc if isinstance(exc, requests.RequestException) else None)


def parse_ibge(source: dict[str, Any], observed_at: str) -> dict[str, Any]:
    try:
        response = _request(source["url"], timeout=90)
        if not response.ok:
            return _failed(source, observed_at, "rest_api", response=response)
        payload = response.json()
        rows = payload if isinstance(payload, list) else []
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in rows:
            municipality_id = clean(raw.get("municipio-id"), 40)
            if not municipality_id or municipality_id in seen:
                continue
            seen.add(municipality_id)
            items.append({
                "key": municipality_id,
                "entity_type": "municipality",
                "municipality_id": municipality_id,
                "municipality": clean(raw.get("municipio-nome"), 160),
                "state_id": clean(raw.get("UF-id"), 40) or None,
                "state": clean(raw.get("UF-sigla"), 8) or None,
                "state_name": clean(raw.get("UF-nome"), 120) or None,
                "region_id": clean(raw.get("regiao-id"), 40) or None,
                "region": clean(raw.get("regiao-sigla"), 12) or None,
                "region_name": clean(raw.get("regiao-nome"), 120) or None,
                "immediate_region_id": clean(raw.get("regiao-imediata-id"), 40) or None,
                "immediate_region": clean(raw.get("regiao-imediata-nome"), 160) or None,
                "intermediate_region_id": clean(raw.get("regiao-intermediaria-id"), 40) or None,
                "intermediate_region": clean(raw.get("regiao-intermediaria-nome"), 160) or None,
            })
        metrics = {"entity_count": len(items), "state_count": len({item.get("state") for item in items if item.get("state")}), "region_count": len({item.get("region") for item in items if item.get("region")})}
        claims = [claim("environmental.signal_type", "TERRITORIAL_CONTEXT"), claim("environmental.entity_key", "municipio-id"), claim("environmental.entity_items", items), claim("environmental.metrics", metrics), claim("source.name", source["name"])]
        return _base_observation(source, observed_at, "api", "rest_api", response, response.content, claims, ["O índice territorial contém nomes e hierarquias, mas não coordenadas municipais; lat/lon sem município seguro permanece NOT_PROVEN.", "O índice é usado como contexto, não como evidência de ocorrência ambiental."], {"orderBy": "nome", "view": "nivelado"}, {"page": 1, "page_size": len(items), "has_more": False}, str(response.status_code))
    except (requests.RequestException, ValueError) as exc:
        return _failed(source, observed_at, "rest_api", exc=exc if isinstance(exc, requests.RequestException) else None)


def _candidate_coordinates(observations: list[dict[str, Any]], source: dict[str, Any]) -> list[dict[str, float]]:
    configured = source.get("collector_config", {}).get("default_coordinates", {"latitude": -15.78, "longitude": -47.93})
    output: list[dict[str, float]] = [{"latitude": float(configured["latitude"]), "longitude": float(configured["longitude"])}]
    for preferred_source in ["inpe-queimadas", "nasa-eonet", "gbif-occurrences"]:
        observation = next((item for item in observations if item.get("source_id") == preferred_source and item.get("fetch", {}).get("status") == "success"), None)
        if not observation:
            continue
        items = claim_map(observation).get("environmental.entity_items", [])
        for item in items:
            location = item.get("location") if isinstance(item, dict) else None
            if not isinstance(location, dict) or location.get("latitude") is None or location.get("longitude") is None:
                continue
            coord = {"latitude": round(float(location["latitude"]), 2), "longitude": round(float(location["longitude"]), 2)}
            if all(abs(coord["latitude"] - old["latitude"]) > 0.25 or abs(coord["longitude"] - old["longitude"]) > 0.25 for old in output):
                output.append(coord)
            if len(output) >= int(source.get("collector_config", {}).get("max_locations", 4)):
                return output
    return output


def parse_open_meteo(source: dict[str, Any], observed_at: str, observations: list[dict[str, Any]]) -> dict[str, Any]:
    locations = _candidate_coordinates(observations, source)
    payloads: list[dict[str, Any]] = []
    raw_bodies: list[bytes] = []
    last_response: requests.Response | None = None
    failures: list[str] = []
    for location in locations:
        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "hourly": "temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m",
            "forecast_days": 2,
            "timezone": "UTC",
        }
        try:
            response = _request("https://api.open-meteo.com/v1/forecast", params=params, timeout=60)
            if not response.ok:
                failures.append(f"HTTP {response.status_code} at {location['latitude']},{location['longitude']}")
                continue
            last_response = response
            payload = response.json()
            payloads.append({"requested": location, "response": payload})
            raw_bodies.append(response.content)
        except (requests.RequestException, ValueError) as exc:
            failures.append(f"{type(exc).__name__} at {location['latitude']},{location['longitude']}")
    if not payloads:
        return _base_observation(source, observed_at, "api", "rest_api", None, b"", [], ["No climate location responded.", *failures])
    items: list[dict[str, Any]] = []
    for location_payload in payloads:
        requested = location_payload["requested"]
        payload = location_payload["response"]
        hourly = payload.get("hourly", {}) if isinstance(payload, dict) else {}
        times = hourly.get("time", []) if isinstance(hourly, dict) else []
        variables = ["temperature_2m", "precipitation", "relative_humidity_2m", "wind_speed_10m"]
        for index, time_value in enumerate(times):
            values = {variable: hourly.get(variable, [None] * len(times))[index] if index < len(hourly.get(variable, [])) else None for variable in variables}
            key = f"{round(float(payload.get('latitude', requested['latitude'])), 2)}|{round(float(payload.get('longitude', requested['longitude'])), 2)}|{time_value}"
            items.append({"key": key, "entity_type": "climate_point", "occurred_at": iso_value(time_value), "location": {"latitude": payload.get("latitude", requested["latitude"]), "longitude": payload.get("longitude", requested["longitude"])}, "values": values, "units": payload.get("hourly_units", {}), "forecast": True})
    metrics = {"location_count": len(payloads), "entity_count": len(items), "hours_per_location": len(items) // len(payloads) if payloads else 0, "locations": [{"latitude": payload.get("latitude", item["requested"]["latitude"]), "longitude": payload.get("longitude", item["requested"]["longitude"]), "timezone": payload.get("timezone")} for item in payloads for payload in [item["response"]]]}
    body = b"\n".join(raw_bodies)
    claims = [claim("environmental.signal_type", "CLIMATE_CONDITION"), claim("environmental.entity_key", "location|time"), claim("environmental.entity_items", items), claim("environmental.metrics", metrics), claim("environmental.locations", payloads), claim("source.name", source["name"])]
    limitations = ["Forecast values are contextual enrichment, not causal evidence or opportunity records.", "Only a bounded two-day hourly window and up to four locations are collected per release.", "Commercial use and redistribution terms must be reviewed before production adoption."]
    limitations.extend(failures)
    return _base_observation(source, observed_at, "api", "rest_api", last_response, body, claims, limitations, {"locations": locations, "forecast_days": 2, "timezone": "UTC"}, {"page": 1, "page_size": len(items), "has_more": False}, f"{len(payloads)}locations")


def fetch_environmental_source(source: dict[str, Any], observations: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    observed_at = now()
    observations = observations or []
    source_id = source.get("id")
    if source_id == "inpe-queimadas":
        return parse_inpe(source, observed_at)
    if source_id == "gbif-occurrences":
        return parse_gbif(source, observed_at)
    if source_id == "nasa-eonet":
        return parse_eonet(source, observed_at)
    if source_id == "ibge-localidades-api":
        return parse_ibge(source, observed_at)
    if source_id == "open-meteo":
        return parse_open_meteo(source, observed_at, observations)
    raise ValueError(f"unknown environmental source: {source_id}")


def environmental_evidence(observation: dict[str, Any]) -> dict[str, Any]:
    digest = observation.get("content", {}).get("content_hash")
    return {
        "evidence_id": f"evidence:{observation['source_id']}:environment:{(digest or 'nohash')[-16:]}",
        "evidence_type": "official_structured_observation",
        "source_name": observation["source_id"],
        "source_url": observation["source_url"],
        "source_role": "primary",
        "observed_at": observation["observed_at"],
        "observation_ids": [observation["observation_id"]],
        "content_hash": digest,
        "supports_claims": sorted({item.get("path") for item in observation.get("claims", []) if item.get("path")}),
        "reliability": "official_structured_source" if observation.get("fetch", {}).get("status") == "success" else "source_unavailable",
        "limitations": observation.get("limitations", []),
        "access_notes": f"Fetch status: {observation.get('fetch', {}).get('status')}; HTTP {observation.get('fetch', {}).get('http_status')}.",
        "license_notes": observation.get("license_or_terms_note", "Review source terms before redistribution."),
    }


def _source_type(source: dict[str, Any], observation: dict[str, Any]) -> str:
    return str(source.get("environmental_signal_type") or claim_map(observation).get("environmental.signal_type") or "environmental_observation")


def _entity_label(item: dict[str, Any]) -> str:
    return clean(item.get("title") or item.get("scientific_name") or item.get("municipality") or item.get("key") or "Entidade observada", 240)


def _entity_compare(item: dict[str, Any]) -> str:
    return json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def entity_diff(previous_items: list[dict[str, Any]], current_items: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    previous_by_key = {str(item.get("key")): item for item in previous_items if isinstance(item, dict) and item.get("key")}
    current_by_key = {str(item.get("key")): item for item in current_items if isinstance(item, dict) and item.get("key")}
    buckets: dict[str, list[dict[str, Any]]] = {"ADDED": [], "REMOVED": [], "CHANGED": [], "UNCHANGED": []}
    for key in sorted(set(current_by_key) | set(previous_by_key)):
        before = previous_by_key.get(key)
        after = current_by_key.get(key)
        if before is None:
            buckets["ADDED"].append({"key": key, "after": after})
        elif after is None:
            buckets["REMOVED"].append({"key": key, "before": before})
        elif _entity_compare(before) != _entity_compare(after):
            buckets["CHANGED"].append({"key": key, "before": before, "after": after})
        else:
            buckets["UNCHANGED"].append({"key": key, "after": after})
    return current_by_key, buckets


def _latest_previous_observation(source_id: str, previous_observations: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [item for item in previous_observations if item.get("source_id") == source_id and item.get("fetch", {}).get("status") == "success" and any(claim_item.get("path") == "environmental.entity_items" for claim_item in item.get("claims", []))]
    return max(candidates, key=lambda item: item.get("observed_at", ""), default=None)


def _observed_items(items: list[dict[str, Any]], limit: int = 200) -> list[dict[str, str]]:
    return [{"key": str(item.get("key")), "label": _entity_label(item)} for item in items[:limit] if item.get("key")]


STATE_ALIASES = {
    "acre": "AC", "alagoas": "AL", "amapa": "AP", "amazonas": "AM", "bahia": "BA",
    "ceara": "CE", "distrito federal": "DF", "espirito santo": "ES", "goias": "GO",
    "maranhao": "MA", "mato grosso": "MT", "mato grosso do sul": "MS", "minas gerais": "MG",
    "para": "PA", "paraiba": "PB", "parana": "PR", "pernambuco": "PE", "piaui": "PI",
    "rio de janeiro": "RJ", "rio grande do norte": "RN", "rio grande do sul": "RS", "rondonia": "RO",
    "roraima": "RR", "santa catarina": "SC", "sao paulo": "SP", "sergipe": "SE", "tocantins": "TO",
}


def _norm_state(value: Any) -> str:
    text = norm_text(value)
    return STATE_ALIASES.get(text, text.upper() if len(text) <= 3 else text)


def territory_index(observation: dict[str, Any] | None) -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    by_id: dict[str, dict[str, Any]] = {}
    by_name: dict[tuple[str, str], dict[str, Any]] = {}
    if not observation:
        return by_id, by_name
    for item in claim_map(observation).get("environmental.entity_items", []):
        if not isinstance(item, dict):
            continue
        municipality_id = str(item.get("municipality_id") or item.get("key") or "")
        if municipality_id:
            by_id[municipality_id] = item
        name = norm_text(item.get("municipality"))
        state = _norm_state(item.get("state"))
        if name and state:
            by_name[(name, state)] = item
    return by_id, by_name


def attach_territory(item: dict[str, Any], by_id: dict[str, dict[str, Any]], by_name: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    enriched = dict(item)
    municipality_id = str(item.get("municipality_id") or "")
    matched = by_id.get(municipality_id) if municipality_id else None
    if not matched:
        matched = by_name.get((norm_text(item.get("municipality")), _norm_state(item.get("state"))))
    if matched:
        enriched["territory"] = {
            "municipality_id": matched.get("municipality_id") or matched.get("key"),
            "municipality": matched.get("municipality"),
            "state": matched.get("state"),
            "state_name": matched.get("state_name"),
            "region": matched.get("region"),
            "region_name": matched.get("region_name"),
            "match_method": "municipality_id" if municipality_id and matched.get("municipality_id") == municipality_id else "municipality_name_state",
        }
        enriched["territory_status"] = "MATCHED"
    else:
        enriched["territory_status"] = "NOT_PROVEN"
        enriched["territory_limitation"] = "IBGE index has no coordinates and no safe municipality match was available."
    return enriched


def _distance_km(left: dict[str, Any], right: dict[str, Any]) -> float | None:
    try:
        lat1, lon1 = float(left["latitude"]), float(left["longitude"])
        lat2, lon2 = float(right["latitude"]), float(right["longitude"])
    except (KeyError, TypeError, ValueError):
        return None
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    hav = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return round(2 * radius * math.asin(math.sqrt(hav)), 2)


def _time_distance_minutes(left: Any, right: Any) -> float:
    try:
        left_dt = datetime.fromisoformat(str(left).replace("Z", "+00:00"))
        right_dt = datetime.fromisoformat(str(right).replace("Z", "+00:00"))
        return abs((left_dt - right_dt).total_seconds()) / 60
    except (TypeError, ValueError):
        return float("inf")


def nearest_climate(item: dict[str, Any], climate_items: list[dict[str, Any]], max_km: float = 160.0) -> dict[str, Any] | None:
    location = item.get("location") if isinstance(item, dict) else None
    if not isinstance(location, dict) or location.get("latitude") is None or location.get("longitude") is None:
        return None
    candidates: list[tuple[float, float, dict[str, Any]]] = []
    target_time = item.get("occurred_at") or ""
    for climate in climate_items:
        distance = _distance_km(location, climate.get("location") or {})
        if distance is not None and distance <= max_km:
            candidates.append((distance, _time_distance_minutes(target_time, climate.get("occurred_at")), climate))
    if not candidates:
        return None
    candidates.sort(key=lambda pair: (pair[1], pair[0]))
    distance, _, selected = candidates[0]
    return {"distance_km": distance, "observed_at": selected.get("occurred_at"), "location": selected.get("location"), "values": selected.get("values"), "units": selected.get("units"), "forecast": selected.get("forecast", True)}


def _entity_signal(source: dict[str, Any], observation: dict[str, Any], item: dict[str, Any], change_type: str, evidence_ids: list[str], observed_at: str, source_type: str) -> dict[str, Any]:
    source_id = source["id"]
    key = str(item.get("key"))
    status = item.get("status") or ("REMOVED" if change_type == "REMOVED" else "OBSERVED")
    observed_fields = {key: value for key, value in item.items() if key not in {"key", "entity_type"} and value not in (None, "", [], {})}
    title = _entity_label(item)
    return {
        "signal_id": f"signal:environment:{source_id}:{hashlib.sha1(key.encode('utf-8')).hexdigest()[:16]}",
        "canonical_key": f"environment:{source_id}:{key}",
        "signal_type": source_type,
        "title": title,
        "summary": f"{source_type}: {title} ({change_type}).",
        "source_id": source_id,
        "source_url": source.get("url", observation.get("source_url", "")),
        "observed_at": observed_at,
        "occurred_at": item.get("occurred_at"),
        "status": status,
        "change_type": change_type,
        "domains": source.get("domain", ["sustainability"]),
        "lens_matches": ["sustainability"],
        "current_view": False,
        "content_hash": observation.get("content", {}).get("content_hash"),
        "content_type": observation.get("content", {}).get("media_type"),
        "observed_item_count": 1,
        "observed_items": [{"key": key, "label": title}],
        "claim_paths": ["environmental.entity_items"],
        "observed_fields": observed_fields,
        "location": item.get("location"),
        "territory": item.get("territory"),
        "subject": {"entity_type": item.get("entity_type"), "key": key},
        "evidence_ids": evidence_ids,
        "observation_ids": [observation.get("observation_id")],
        "limitations": observation.get("limitations", []),
        "provenance": {"method": "entity-level environmental diff", "entity_key": key, "source_role": "primary"},
    }


def _source_signal(source: dict[str, Any], observation: dict[str, Any], previous: dict[str, Any] | None, current_items: list[dict[str, Any]], buckets: dict[str, list[dict[str, Any]]], evidence_ids: list[str], observed_at: str, source_type: str) -> dict[str, Any]:
    current_hash = observation.get("content", {}).get("content_hash")
    previous_hash = previous.get("content", {}).get("content_hash") if previous else None
    first_success = previous is None
    any_diff = any(buckets[key] for key in ["ADDED", "REMOVED", "CHANGED"])
    change_type = "NEW" if first_success else "UPDATED" if any_diff or current_hash != previous_hash else "UNCHANGED"
    metrics = claim_map(observation).get("environmental.metrics", {})
    diff_counts = {key.lower(): len(value) for key, value in buckets.items()}
    diff_sample = [{"change_type": kind, "key": item.get("key"), "before": item.get("before"), "after": item.get("after")} for kind in ["ADDED", "REMOVED", "CHANGED"] for item in buckets[kind][:40]]
    return {
        "signal_id": f"signal:source:{source['id']}",
        "canonical_key": f"source:{source['id']}",
        "signal_type": source_type,
        "title": source.get("name", source["id"]),
        "summary": f"Snapshot ambiental de {source.get('name', source['id'])}: {len(current_items)} entidades observadas; diff por entidade quando identificador estável existe.",
        "source_id": source["id"],
        "source_url": observation.get("source_url", source.get("url", "")),
        "observed_at": observed_at,
        "status": observation.get("fetch", {}).get("status", "failed"),
        "change_type": change_type,
        "domains": source.get("domain", ["sustainability"]),
        "lens_matches": ["sustainability"],
        "current_view": False,
        "content_hash": current_hash,
        "content_type": observation.get("content", {}).get("media_type"),
        "observed_item_count": len(current_items),
        "observed_items": _observed_items(current_items),
        "claim_paths": sorted(item.get("path") for item in observation.get("claims", []) if item.get("path")),
        "observed_fields": {"metrics": metrics, "entity_diff": diff_counts, "entity_key": claim_map(observation).get("environmental.entity_key")},
        "entity_diff": {"mode": "ENTITY_DIFF", "counts": diff_counts, "sample": diff_sample},
        "evidence_ids": evidence_ids,
        "observation_ids": [observation.get("observation_id")],
        "changes": diff_sample or ([{"kind": "content_changed", "status": change_type}] if current_hash != previous_hash and previous else []),
        "limitations": observation.get("limitations", []),
        "provenance": {"method": "source snapshot with entity-level diff", "entity_key": claim_map(observation).get("environmental.entity_key"), "source_role": "primary"},
    }


def _group_by_territory(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        territory = item.get("territory") if isinstance(item.get("territory"), dict) else None
        key = str(territory.get("municipality_id")) if territory and territory.get("municipality_id") else ""
        if key:
            groups[key].append(item)
    return groups


def _demo_signal(demo_id: str, title: str, summary: str, source_ids: list[str], related_signal_ids: list[str], observed_at: str, observed_fields: dict[str, Any], evidence_ids: list[str], observation_ids: list[str], territory: dict[str, Any] | None = None, location: dict[str, Any] | None = None, occurred_at: str | None = None) -> dict[str, Any]:
    return {
        "signal_id": f"signal:composite:{demo_id}",
        "canonical_key": f"composite:{demo_id}",
        "signal_type": "COMPOSITE_ENVIRONMENTAL",
        "title": title,
        "summary": summary,
        "source_id": "+".join(source_ids),
        "source_url": "https://github.com/viniburilux/Lux-Radar",
        "observed_at": observed_at,
        "occurred_at": occurred_at,
        "status": "OBSERVED",
        "change_type": "UNCHANGED",
        "domains": ["sustainability"],
        "lens_matches": ["sustainability"],
        "current_view": False,
        "observed_item_count": 1,
        "observed_items": [{"key": demo_id, "label": title}],
        "observed_fields": observed_fields,
        "location": location,
        "territory": territory,
        "subject": {"entity_type": "composite_environmental_signal", "key": demo_id},
        "related_signals": related_signal_ids,
        "evidence_ids": evidence_ids,
        "observation_ids": observation_ids,
        "limitations": ["Composição descritiva; não implica causalidade, risco, anomalia ou oportunidade."],
        "provenance": {"method": "deterministic cross-source composition", "source_role": "derived"},
    }


def build_demonstrations(observations: list[dict[str, Any]], signals: list[dict[str, Any]], registry: list[dict[str, Any]], observed_at: str) -> tuple[list[dict[str, Any]], list[str]]:
    by_id = {item.get("source_id"): item for item in observations}
    source_by_id = {source["id"]: source for source in registry}
    ibge = by_id.get("ibge-localidades-api")
    by_territory_id, by_territory_name = territory_index(ibge)
    current_entities: dict[str, list[dict[str, Any]]] = {}
    evidence_by_source: dict[str, list[str]] = {}
    observations_by_source: dict[str, str] = {}
    for source_id, observation in by_id.items():
        current_entities[source_id] = [attach_territory(item, by_territory_id, by_territory_name) for item in claim_map(observation).get("environmental.entity_items", []) if isinstance(item, dict)]
        evidence_by_source[source_id] = list(observation.get("evidence_ids", []))
        observations_by_source[source_id] = observation.get("observation_id", "")
    climate_items = current_entities.get("open-meteo", [])
    fires = current_entities.get("inpe-queimadas", [])
    biodiversity = current_entities.get("gbif-occurrences", [])
    eonet = current_entities.get("nasa-eonet", [])
    signal_by_key = {signal.get("canonical_key"): signal for signal in signals}
    demos: list[dict[str, Any]] = []
    limitations: list[str] = []
    fire_groups = _group_by_territory(fires)
    biodiversity_groups = _group_by_territory(biodiversity)
    if fire_groups:
        territory_id, fire_group = sorted(fire_groups.items(), key=lambda pair: (-len(pair[1]), pair[0]))[0]
        representative = fire_group[0]
        climate = nearest_climate(representative, climate_items)
        related = [signal_by_key.get(f"environment:inpe-queimadas:{item.get('key')}", {}).get("signal_id") for item in fire_group[:5]]
        related = [value for value in related if value]
        fields = {"fire_count": len(fire_group), "biome": Counter(item.get("biome") for item in fire_group).most_common(1)[0][0] if fire_group else None, "territory_id": territory_id}
        if climate:
            fields["climate_context"] = climate
            title = "Atividade de fogo recente + território + clima"
            summary = f"Foram observados {len(fire_group)} focos no município {representative.get('territory', {}).get('municipality')} ({representative.get('territory', {}).get('state')}); o sistema associou contexto meteorológico por proximidade de {climate['distance_km']} km, sem afirmar causalidade."
            demos.append(_demo_signal("fire-territory-climate", title, summary, ["inpe-queimadas", "ibge-localidades-api", "open-meteo"], related, observed_at, fields, evidence_by_source.get("inpe-queimadas", []) + evidence_by_source.get("ibge-localidades-api", []) + evidence_by_source.get("open-meteo", []), [observations_by_source.get(key, "") for key in ["inpe-queimadas", "ibge-localidades-api", "open-meteo"] if observations_by_source.get(key)], representative.get("territory"), representative.get("location"), representative.get("occurred_at")))
        else:
            limitations.append("INPE + IBGE foi observado, mas nenhum ponto Open-Meteo ficou dentro do limite de proximidade para uma composição climática segura.")
        concentration = {
            "fire_count": len(fire_group),
            "territory_id": territory_id,
            "biome": Counter(item.get("biome") for item in fire_group).most_common(1)[0][0] if fire_group else None,
            "frp_total": round(sum(item.get("frp") or 0 for item in fire_group), 3),
            "latest_occurred_at": max((item.get("occurred_at") or "" for item in fire_group), default=None),
        }
        demos.append(_demo_signal("fire-concentration-territory", "Concentração de fogo por território", f"O agrupamento do arquivo diário encontrou {len(fire_group)} focos no município {representative.get('territory', {}).get('municipality')} ({representative.get('territory', {}).get('state')}), preservando bioma e intensidade FRP observados. O sistema chama isso de CONCENTRATION, não de anomalia.", ["inpe-queimadas", "ibge-localidades-api"], related, observed_at, concentration, evidence_by_source.get("inpe-queimadas", []) + evidence_by_source.get("ibge-localidades-api", []), [observations_by_source.get(key, "") for key in ["inpe-queimadas", "ibge-localidades-api"] if observations_by_source.get(key)], representative.get("territory"), representative.get("location"), representative.get("occurred_at")))
    else:
        limitations.append("Não houve grupo de focos INPE com município associado nesta coleta.")
    if biodiversity_groups:
        territory_id, group = sorted(biodiversity_groups.items(), key=lambda pair: (-len(pair[1]), pair[0]))[0]
        representative = group[0]
        related = [signal_by_key.get(f"environment:gbif-occurrences:{item.get('key')}", {}).get("signal_id") for item in group[:5]]
        related = [value for value in related if value]
        territory = representative.get("territory")
        demos.append(_demo_signal("biodiversity-territory", "Ocorrências de biodiversidade + território", f"O snapshot GBIF contém {len(group)} ocorrência(s) associada(s) ao município {territory.get('municipality') if territory else 'não identificado'}; taxonomia, data, licença e proveniência permanecem nos sinais individuais.", ["gbif-occurrences", "ibge-localidades-api"], related, observed_at, {"occurrence_count": len(group), "territory_id": territory_id, "taxa": sorted({item.get("scientific_name") for item in group if item.get("scientific_name")})[:10]}, evidence_by_source.get("gbif-occurrences", []) + evidence_by_source.get("ibge-localidades-api", []), [observations_by_source.get(key, "") for key in ["gbif-occurrences", "ibge-localidades-api"] if observations_by_source.get(key)], territory, representative.get("location"), representative.get("occurred_at")))
    else:
        limitations.append("Nenhuma ocorrência GBIF da página limitada encontrou correspondência segura com município/UF do IBGE.")
    common_territories = sorted(set(fire_groups) & set(biodiversity_groups))
    if common_territories:
        territory_id = common_territories[0]
        fire_group = fire_groups[territory_id]
        biodiversity_group = biodiversity_groups[territory_id]
        territory = fire_group[0].get("territory") or biodiversity_group[0].get("territory")
        related = [signal_by_key.get(f"environment:inpe-queimadas:{item.get('key')}", {}).get("signal_id") for item in fire_group[:3]] + [signal_by_key.get(f"environment:gbif-occurrences:{item.get('key')}", {}).get("signal_id") for item in biodiversity_group[:3]]
        related = [value for value in related if value]
        demos.append(_demo_signal("cross-source-territory", "Fogo e biodiversidade observados no mesmo território", f"No snapshot, o município {territory.get('municipality') if territory else territory_id} aparece tanto no conjunto de focos INPE ({len(fire_group)}) quanto no conjunto amostrado de ocorrências GBIF ({len(biodiversity_group)}). Isso descreve co-presença observacional; não afirma relação causal ou ameaça.", ["inpe-queimadas", "gbif-occurrences", "ibge-localidades-api"], related, observed_at, {"fire_count": len(fire_group), "biodiversity_count": len(biodiversity_group), "territory_id": territory_id}, evidence_by_source.get("inpe-queimadas", []) + evidence_by_source.get("gbif-occurrences", []) + evidence_by_source.get("ibge-localidades-api", []), [observations_by_source.get(key, "") for key in ["inpe-queimadas", "gbif-occurrences", "ibge-localidades-api"] if observations_by_source.get(key)], territory, fire_group[0].get("location"), fire_group[0].get("occurred_at")))
    else:
        limitations.append("Não houve interseção segura entre territórios observados por INPE e GBIF nesta amostra.")
    if len(demos) < 3:
        for event in eonet:
            climate = nearest_climate(event, climate_items)
            if not climate:
                continue
            related_id = signal_by_key.get(f"environment:nasa-eonet:{event.get('key')}", {}).get("signal_id")
            demos.append(_demo_signal("eonet-climate-" + str(event.get("key")), "Evento natural + contexto climático", f"O evento natural {event.get('title') or event.get('key')} foi associado a um ponto climático próximo ({climate['distance_km']} km) apenas como contexto temporal/espacial.", ["nasa-eonet", "open-meteo"], [related_id] if related_id else [], observed_at, {"event_id": event.get("key"), "climate_context": climate}, evidence_by_source.get("nasa-eonet", []) + evidence_by_source.get("open-meteo", []), [observations_by_source.get(key, "") for key in ["nasa-eonet", "open-meteo"] if observations_by_source.get(key)], event.get("territory"), event.get("location"), event.get("occurred_at")))
            if len(demos) >= 3:
                break
    if len(demos) < 3:
        limitations.append(f"Somente {len(demos)} composição(ões) determinística(s) foram provadas; o restante permanece NOT_PROVEN.")
    return demos[:3], limitations


def build_environmental_signal_views(observations: list[dict[str, Any]], previous_observations: list[dict[str, Any]], registry: list[dict[str, Any]], evidence_by_source: dict[str, list[str]], observed_at: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    source_by_id = {source["id"]: source for source in registry}
    ibge = next((item for item in observations if item.get("source_id") == "ibge-localidades-api" and item.get("fetch", {}).get("status") == "success"), None)
    by_territory_id, by_territory_name = territory_index(ibge)
    signals: list[dict[str, Any]] = []
    temporal_changes: list[dict[str, Any]] = []
    diff_totals = Counter()
    for observation in observations:
        source_id = observation.get("source_id")
        if source_id not in ENVIRONMENTAL_SOURCE_IDS:
            continue
        source = source_by_id.get(source_id, {"id": source_id, "name": source_id, "url": observation.get("source_url", ""), "domain": ["sustainability"]})
        source_type = _source_type(source, observation)
        evidence_ids = evidence_by_source.get(source_id, [])
        if observation.get("fetch", {}).get("status") != "success":
            signal = _source_signal(source, observation, _latest_previous_observation(source_id, previous_observations), [], {"ADDED": [], "REMOVED": [], "CHANGED": [], "UNCHANGED": []}, evidence_ids, observed_at, source_type)
            signal["change_type"] = "SOURCE_UNAVAILABLE"
            signal["entity_diff"] = {"mode": "SOURCE_LEVEL_CHANGE_ONLY", "counts": {"added": 0, "removed": 0, "changed": 0, "unchanged": 0}, "sample": []}
            signal["limitations"] = sorted(set(signal.get("limitations", []) + ["SOURCE_UNAVAILABLE: entity-level removal is not inferred from a failed collection."]))
            signals.append(signal)
            diff_totals["source_level_change_only"] += 1
            continue
        raw_items = [item for item in claim_map(observation).get("environmental.entity_items", []) if isinstance(item, dict)]
        current_items = [attach_territory(item, by_territory_id, by_territory_name) for item in raw_items]
        previous_observation = _latest_previous_observation(source_id, previous_observations)
        previous_items = [item for item in claim_map(previous_observation).get("environmental.entity_items", []) if isinstance(item, dict)] if previous_observation else []
        previous_items = [attach_territory(item, by_territory_id, by_territory_name) for item in previous_items]
        current_by_key, buckets = entity_diff(previous_items, current_items)
        source_signal = _source_signal(source, observation, previous_observation, list(current_by_key.values()), buckets, evidence_ids, observed_at, source_type)
        signals.append(source_signal)
        for kind, changes in buckets.items():
            diff_totals[kind.lower()] += len(changes)
        for kind in ["ADDED", "REMOVED", "CHANGED"]:
            for change in buckets[kind][:MAX_PUBLISHED_ENTITY_SIGNALS]:
                item = change.get("after") or change.get("before") or {}
                signals.append(_entity_signal(source, observation, item, kind, evidence_ids, observed_at, source_type))
        temporal_changes.append({"source_id": source_id, "field": "entity_diff", "status": source_signal.get("change_type"), "before": {"entity_count": len(previous_items)}, "after": {"entity_count": len(current_items)}, "observation_ids": [observation.get("observation_id")], "evidence_ids": evidence_ids, "entity_changes": {"added": len(buckets["ADDED"]), "removed": len(buckets["REMOVED"]), "changed": len(buckets["CHANGED"]), "unchanged": len(buckets["UNCHANGED"]), "sample": source_signal.get("entity_diff", {}).get("sample", [])}})
    demos, limitations = build_demonstrations(observations, signals, registry, observed_at)
    signals.extend(demos)
    total_entity_changes = diff_totals.get("added", 0) + diff_totals.get("removed", 0) + diff_totals.get("changed", 0)
    published_entity_signals = sum(1 for signal in signals if signal.get("change_type") in {"ADDED", "REMOVED", "CHANGED"})
    stats = {"entity_added": diff_totals.get("added", 0), "entity_removed": diff_totals.get("removed", 0), "entity_changed": diff_totals.get("changed", 0), "entity_unchanged": diff_totals.get("unchanged", 0), "source_level_change_only": diff_totals.get("source_level_change_only", 0), "published_entity_signals": published_entity_signals, "truncated_entity_signals": max(total_entity_changes - published_entity_signals, 0), "demonstrations": len(demos), "composition_status": "PROVEN" if len(demos) >= 3 else "NOT_PROVEN", "limitations": limitations, "by_type": dict(Counter(signal.get("signal_type", "unknown") for signal in signals))}
    return signals, temporal_changes, demos, stats
