from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from datetime import datetime, timezone
import hashlib
import re
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = "Lux-Radar-Quality-Layer/0.2 (+https://github.com/viniburilux/Lux-Radar)"
MAX_DETAILS_PER_SOURCE = 8
QUALITY_EXCLUDED_IDS = {"petrobras-socioambiental", "transferegov-parcerias"}
DATE_PATTERNS = [
    re.compile(r"(?P<day>\d{1,2})[/.](?P<month>\d{1,2})[/.](?P<year>20\d{2})"),
    re.compile(r"(?P<year>20\d{2})-(?P<month>\d{2})-(?P<day>\d{2})"),
]


def observed_at() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def content_hash(body: bytes) -> str:
    return f"sha256:{hashlib.sha256(body).hexdigest()}"


def norm_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed._replace(fragment="").geturl().rstrip("/")


def clean_text(value: str | None, limit: int = 1200) -> str:
    return re.sub(r"\s+", " ", value or "").strip()[:limit]


def parse_dates(text: str) -> list[str]:
    found: list[str] = []
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            try:
                day = int(match.group("day"))
                month = int(match.group("month"))
                year = int(match.group("year"))
                if 1 <= day <= 31 and 1 <= month <= 12:
                    found.append(f"{year:04d}-{month:02d}-{day:02d}T23:59:59Z")
            except ValueError:
                continue
    return list(dict.fromkeys(found))


def extract_deadline(text: str) -> str | None:
    date = r"((?:\d{1,2}[/.]\d{1,2}[/.]20\d{2})|(?:20\d{2}-\d{2}-\d{2}))"
    patterns = [
        rf"(?:até|until|by|no later than|deadline\s*[:\-]?|prazo(?: final| limite)?\s*[:\-]?)[^.!?]{{0,80}}?{date}",
        rf"(?:inscri(?:ção|ções)|submiss(?:ão|ões)|application(?:s)?)\s*(?:até|until|by)\s*{date}",
        rf"{date}[^.\n!?]{{0,50}}?(?:é o prazo|is the deadline|deadline|prazo final)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if not match:
            continue
        value = match.group(1)
        dates = parse_dates(value)
        if dates:
            return dates[0]
    return None


def extract_amount(text: str) -> dict[str, Any]:
    for pattern, currency in [(r"R\$\s*([\d.]+(?:,\d{1,2})?)", "BRL"), (r"€\s*([\d.,]+)", "EUR"), (r"\$\s*([\d.,]+)", "USD")]:
        match = re.search(pattern, text, flags=re.I)
        if match:
            raw = match.group(1).replace(".", "").replace(",", ".")
            try:
                return {"amount": float(raw), "currency": currency, "raw": match.group(0)}
            except ValueError:
                pass
    return {}


def extract_pdf_url(url: str, soup: BeautifulSoup) -> str | None:
    for anchor in soup.find_all("a", href=True):
        candidate = urljoin(url, anchor["href"].strip())
        label = (anchor.get_text(" ", strip=True) + " " + candidate).lower()
        if re.search(r"\.pdf(?:$|[?#])", candidate, flags=re.I):
            if candidate.startswith(("http://", "https://")):
                return candidate
    return None


def extract_pdf_text(pdf_url: str) -> tuple[str, str | None, str | None]:
    try:
        response = requests.get(pdf_url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"}, timeout=20, allow_redirects=True)
        body = response.content[:8_000_000]
        if not response.ok:
            return "", None, f"Official PDF fetch returned HTTP {response.status_code}."
        if not ("pdf" in response.headers.get("content-type", "").lower() or body.startswith(b"%PDF")):
            return "", None, "The selected document link did not return a PDF response."
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(body))
            text = "\\n".join(page.extract_text() or "" for page in reader.pages[:20])
            return clean_text(text, 24000), content_hash(body), None
        except Exception as exc:
            return "", content_hash(body), f"PDF was fetched but text extraction failed with {type(exc).__name__}."
    except requests.RequestException as exc:
        return "", None, f"Official PDF network failure: {type(exc).__name__}."


def infer_type(text: str, label: str) -> str:
    haystack = f"{label} {text}".lower()
    if "grant" in haystack or "financiamento" in haystack or "funding" in haystack:
        return "grant"
    if "pesquisa" in haystack or "research" in haystack:
        return "research_call"
    if "prêmio" in haystack or "award" in haystack:
        return "award"
    if "evento" in haystack or "event" in haystack:
        return "event"
    if "programa" in haystack or "program" in haystack:
        return "innovation_program"
    if "parceria" in haystack or "partnership" in haystack:
        return "partnership"
    if "desafio" in haystack or "challenge" in haystack:
        return "challenge"
    return "call"


def infer_domains(text: str, configured: list[str]) -> list[str]:
    haystack = text.lower()
    aliases = {
        "climate": ["climate", "clima", "carbono", "emission"],
        "biodiversity": ["biodiversidade", "biodiversity", "fauna", "flora"],
        "water": ["água", "water", "bacia", "hídrica"],
        "circular_economy": ["economia circular", "circular economy", "resíduos", "waste"],
        "energy": ["energia", "energy", "renewable", "renovável"],
        "sustainability": ["sustentabilidade", "sustainability", "sustainable"],
        "research": ["pesquisa", "research", "ciência", "science"],
        "innovation": ["inovação", "innovation", "tecnologia", "technology"],
        "territory": ["território", "territory", "comunidade", "community"],
    }
    result = set(configured)
    for domain, terms in aliases.items():
        if any(term in haystack for term in terms):
            result.add(domain)
    return sorted(result)


def infer_territories(text: str, country: str) -> list[str]:
    names = ["Bahia", "Brasil", "Amazônia", "Amazon", "Pantanal", "Parnaíba", "Xingu", "Europe", "Europa", "Brazil"]
    found = [name for name in names if name.lower() in text.lower()]
    return list(dict.fromkeys(found or ([country] if country else [])))


def quality_state(text: str, *, deadline: str | None, eligibility: list[str], organization: str, pdf_url: str | None) -> tuple[str, str]:
    haystack = text.lower()
    closed = any(term in haystack for term in ["encerrad", "closed", "deadline passed", "prazo encerrado", "concluded", "finalizado"])
    open_signal = any(term in haystack for term in ["inscrições abertas", "inscricao aberta", "open call", "open for", "submissions open", "chamada aberta"])
    critical_count = sum(bool(item) for item in [deadline, eligibility, organization])
    if closed and critical_count >= 2:
        return "CLOSED", "Detail page identifies the opportunity and indicates a closed or expired state."
    if critical_count == 3 and (open_signal or deadline):
        return "VERIFIED", "Official detail page is accessible and supplies title, organization, deadline and eligibility, with the official URL preserved."
    if critical_count >= 2:
        return "INSUFFICIENT_EVIDENCE", "Official detail page is accessible, but one or more critical fields remain unobserved."
    return "CANDIDATE", "The source page yielded a candidate, but the detail evidence is not sufficient for verification."


def _detail_request(candidate: dict[str, Any], source: dict[str, Any], root_observation: dict[str, Any]) -> dict[str, Any]:
    url = candidate.get("url", "")
    timestamp = observed_at()
    base = {
        "source_id": source["id"],
        "root_observation_id": root_observation["observation_id"],
        "candidate_url": url,
    }
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.7"}, timeout=20, allow_redirects=True)
        body = response.content[:4_000_000]
        if not response.ok:
            return {**base, "status": "failed", "http_status": response.status_code, "observed_at": timestamp, "url": response.url, "body": b"", "limitations": [f"Detail fetch returned HTTP {response.status_code}."]}
        content_type = response.headers.get("content-type", "")
        if "html" not in content_type.lower():
            return {**base, "status": "success", "http_status": response.status_code, "observed_at": timestamp, "url": response.url, "body": body, "content_type": content_type, "limitations": ["Detail response was not HTML; metadata was retained and no HTML field extraction was attempted."]}
        soup = BeautifulSoup(body, "html.parser")
        title_node = soup.find("h1") or soup.find("title")
        title = clean_text(title_node.get_text(" ", strip=True) if title_node else candidate.get("title"), 500)
        description_node = soup.find("meta", attrs={"name": re.compile("description", re.I)})
        description = clean_text(description_node.get("content") if description_node else "", 1600)
        if not description:
            paragraph = soup.find("p")
            description = clean_text(paragraph.get_text(" ", strip=True) if paragraph else "", 1600)
        text = clean_text(soup.get_text(" ", strip=True), 24000)
        limitations = ["Detail extraction is claim-preserving and does not publish the complete third-party document."]
        headings = [clean_text(node.get_text(" ", strip=True), 300) for node in soup.find_all(["h1", "h2", "h3"]) if node.get_text(" ", strip=True)]
        pdf_url = extract_pdf_url(response.url, soup)
        pdf_text, pdf_hash, pdf_error = extract_pdf_text(pdf_url) if pdf_url else ("", None, None)
        if pdf_error:
            limitations.append(pdf_error)
        combined_text = f"{text} {pdf_text}"
        amount = extract_amount(combined_text)
        deadline = extract_deadline(combined_text)
        eligibility = []
        for pattern in [r"(?:público[- ]alvo|elegibilidade|eligible|eligibility|quem pode participar)[^.!?]{0,300}", r"(?:podem participar|destinado a)[^.!?]{0,300}"]:
            match = re.search(pattern, combined_text, flags=re.I)
            if match:
                eligibility.append(clean_text(match.group(0), 500))
        eligibility = list(dict.fromkeys(eligibility))
        organization = source.get("organization", source.get("name", source["id"]))
        status, reason = quality_state(combined_text, deadline=deadline, eligibility=eligibility, organization=organization, pdf_url=pdf_url)
        return {**base, "status": "success", "http_status": response.status_code, "observed_at": timestamp, "url": response.url, "body": body, "content_type": content_type, "title": title, "description": description, "text": text, "pdf_text": pdf_text, "pdf_hash": pdf_hash, "headings": headings[:30], "pdf_url": pdf_url, "amount": amount, "deadline": deadline, "eligibility": eligibility, "organization": organization, "domains": infer_domains(combined_text, source.get("domain", [])), "territories": infer_territories(combined_text, source.get("country", "")), "quality_status": status, "quality_reason": reason, "limitations": limitations}
    except requests.RequestException as exc:
        return {**base, "status": "failed", "http_status": None, "observed_at": timestamp, "url": url, "body": b"", "limitations": [f"Detail network failure: {type(exc).__name__}."]}


def _make_evidence(detail: dict[str, Any], root: dict[str, Any]) -> dict[str, Any]:
    digest = content_hash(detail.get("body", b"")) if detail.get("body") else None
    return {
        "evidence_id": f"evidence:{detail['source_id']}:detail:{(digest or 'nohash')[-16:]}",
        "evidence_type": "official_detail_page",
        "source_name": detail["source_id"],
        "source_url": detail.get("url") or detail.get("candidate_url"),
        "source_role": "primary",
        "observed_at": detail["observed_at"],
        "observation_ids": [root["observation_id"], f"{detail['source_id']}:detail:{(digest or 'failed')[-16:]}"] ,
        "content_hash": digest,
        "supports_claims": ["title", "description", "organization", "deadline", "eligibility", "status", "official_pdf_url"],
        "reliability": "official_detail_observed" if detail["status"] == "success" else "detail_fetch_failed",
        "limitations": detail.get("limitations", []),
        "access_notes": f"Detail fetch status: {detail['status']}; HTTP {detail.get('http_status')}.",
        "license_notes": "Reference URL and selected claims only; complete third-party content is not redistributed.",
    }


def _make_record(detail: dict[str, Any], source: dict[str, Any], root: dict[str, Any], evidence: dict[str, Any], candidate: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    url = detail.get("url") or candidate.get("url") or root["source_url"]
    pdf_url = detail.get("pdf_url")
    digest = hashlib.sha1(f"{source['id']}|{norm_url(pdf_url or url)}".encode("utf-8")).hexdigest()[:16]
    title = detail.get("title") or candidate.get("title") or source.get("name", source["id"])
    status = detail.get("quality_status", "CANDIDATE") if detail.get("status") == "success" else "CANDIDATE"
    deadline = detail.get("deadline")
    record = {
        "opportunity_id": f"opportunity-{digest}",
        "canonical_key": f"pdf:{norm_url(pdf_url)}" if pdf_url else f"url:{norm_url(url)}",
        "title": title,
        "description": detail.get("description") or "Candidate observed on an official source page; detail verification pending.",
        "organization": detail.get("organization") or source.get("organization", source.get("name", source["id"])),
        "type": infer_type(f"{title} {detail.get('text', '')}", candidate.get("title", "")),
        "domains": detail.get("domains") or source.get("domain", []),
        "territories": detail.get("territories", []),
        "eligibility": detail.get("eligibility", []),
        "funding": detail.get("amount", {}),
        "deadline": deadline or "",
        "status": status,
        "verification": {"state": status, "reason": detail.get("quality_reason", "Detail verification pending."), "critical_fields": {"title": bool(title), "organization": bool(record_organization := (detail.get("organization") or source.get("organization"))), "deadline": bool(deadline), "eligibility": bool(detail.get("eligibility")), "official_url": bool(url)}},
        "official_url": url,
        "official_pdf_url": pdf_url,
        "source_id": source["id"],
        "published_at": None,
        "updated_at": detail["observed_at"],
        "first_seen_at": detail["observed_at"],
        "last_seen_at": detail["observed_at"],
        "evidence": [evidence["evidence_id"]],
        "evidence_ids": [evidence["evidence_id"]],
        "provenance": {"observation_ids": [root["observation_id"], evidence["observation_ids"][-1]], "method": "detail follow-up and claim-preserving extraction", "limitations": detail.get("limitations", [])},
        "confidence": 0.92 if status == "VERIFIED" else 0.72 if status == "INSUFFICIENT_EVIDENCE" else 0.55,
        "sources": [source["id"]],
        "history": [{"at": detail["observed_at"], "event": "first_seen", "status": status}],
    }
    normalized = {
        "normalized_id": f"normalized:{record['opportunity_id']}",
        "record_type": "opportunity",
        "opportunity_id": record["opportunity_id"],
        "normalized_at": detail["observed_at"],
        "source_observation_ids": record["provenance"]["observation_ids"],
        "evidence_ids": record["evidence_ids"],
        "fields": {"title": title, "description": record["description"], "organization": record["organization"], "deadline": deadline, "eligibility": record["eligibility"], "status": status, "official_url": url, "official_pdf_url": pdf_url},
        "provenance": {"method": "detail claim normalization", "limitations": detail.get("limitations", [])},
    }
    return record, normalized


def extract_quality_records(observations: list[dict[str, Any]], registry: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    source_by_id = {source["id"]: source for source in registry}
    root_by_id = {observation["source_id"]: observation for observation in observations}
    tasks: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for root in observations:
        source = source_by_id.get(root["source_id"], {})
        if (not source.get("detail_enabled", True) or root["source_id"] in QUALITY_EXCLUDED_IDS
                or root["fetch"]["status"] != "success"):
            continue
        candidates = next((claim["value"] for claim in root.get("claims", []) if claim["path"] == "page.candidate_links"), []) or []
        seed_urls = [url for url in source.get("detail_seeds", []) if isinstance(url, str) and url]
        seed_candidates = [{"title": source.get("name", source["id"]), "url": url, "term_hits": 100} for url in seed_urls]
        seen_urls = {norm_url(item.get("url", "")) for item in seed_candidates}
        ordered_candidates = seed_candidates + [item for item in candidates if norm_url(item.get("url", "")) not in seen_urls]
        for candidate in ordered_candidates[:MAX_DETAILS_PER_SOURCE]:
            tasks.append((candidate, source, root))
    details: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(_detail_request, candidate, source, root) for candidate, source, root in tasks]
        for future in as_completed(futures):
            details.append(future.result())
    out_observations = list(observations)
    evidences: list[dict[str, Any]] = []
    normalized: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for detail in details:
        root = root_by_id.get(detail["source_id"])
        source = source_by_id.get(detail["source_id"], {})
        if not root:
            continue
        detail_hash = content_hash(detail.get("body", b"")) if detail.get("body") else None
        detail_observation_id = f"{detail['source_id']}:detail:{(detail_hash or 'failed')[-16:]}"
        detail_observation = {
            "observation_id": detail_observation_id,
            "source_id": detail["source_id"],
            "source_url": detail.get("url") or detail.get("candidate_url"),
            "observed_at": detail["observed_at"],
            "source_profile": source.get("source_type", "public"),
            "fetch": {"status": detail["status"], "method": "http_get", "http_status": detail.get("http_status"), "content_type": detail.get("content_type")},
            "content": {"media_type": detail.get("content_type") or "application/octet-stream", "content_hash": detail_hash, "byte_size": len(detail.get("body", b""))},
            "claims": [{"path": path, "value": value, "epistemic_status": "observed"} for path, value in {"title": detail.get("title"), "description": detail.get("description"), "organization": detail.get("organization"), "deadline": detail.get("deadline"), "eligibility": detail.get("eligibility", []), "status": detail.get("quality_status", "CANDIDATE"), "official_pdf_url": detail.get("pdf_url")}.items() if value not in (None, "", [])],
            "evidence_ids": [],
            "collector": {"name": "detail-follow-up", "version": "0.2.0", "repository": "https://github.com/viniburilux/Lux-Radar"},
            "limitations": detail.get("limitations", []),
            "license_or_terms_note": "Selected claims only; complete third-party content is not redistributed.",
        }
        out_observations.append(detail_observation)
        evidence = _make_evidence(detail, root)
        evidence["observation_ids"] = [root["observation_id"], detail_observation_id]
        detail_observation["evidence_ids"] = [evidence["evidence_id"]]
        record, normalized_record = _make_record(detail, source, root, evidence, detail.get("candidate", {}))
        records.append(record)
        normalized.append(normalized_record)
        evidences.append(evidence)
    return out_observations, evidences, normalized, records, details
