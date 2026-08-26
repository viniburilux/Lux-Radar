from __future__ import annotations

import hashlib
import re
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = "Lux-Radar-Wave2-Collector/0.1 (+https://github.com/viniburilux/Lux-Radar)"
WAVE2_COLLECTOR_IDS = {
    "funbio-chamadas",
    "fundo-casa-editais",
    "fundacao-boticario-editais",
    "bnb-fundeci",
    "sudene-editais",
    "embratur-editais",
    "prosas-editais",
    "capta-editais",
    "capitaai-meio-ambiente",
}


def now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def content_hash(body: bytes) -> str:
    return f"sha256:{hashlib.sha256(body).hexdigest()}"


def clean(value: str | None, limit: int = 500) -> str:
    return re.sub(r"\s+", " ", value or "").strip()[:limit]


def is_http(url: str) -> bool:
    return url.startswith(("http://", "https://"))


def same_host(url: str, host: str) -> bool:
    return urlparse(url).netloc.lower().endswith(host.lower())


def candidate(title: str, url: str, *, term_hits: int = 1) -> dict[str, Any] | None:
    title = clean(title, 300)
    if not title or len(title) < 8 or not is_http(url):
        return None
    return {"title": title, "url": url, "term_hits": term_hits}


def unique_candidates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        url = item.get("url", "")
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(item)
    return out


def claims_for(source: dict[str, Any], response: requests.Response, candidates: list[dict[str, Any]], page_title: str | None = None) -> list[dict[str, Any]]:
    return [
        {"path": "source.name", "value": source["name"], "epistemic_status": "observed"},
        {"path": "source.organization", "value": source.get("organization", source["name"]), "epistemic_status": "observed"},
        {"path": "source.domain", "value": source.get("domain", []), "epistemic_status": "observed"},
        {"path": "page.title", "value": clean(page_title or source["name"], 500), "epistemic_status": "observed"},
        {"path": "page.candidate_links", "value": candidates[:80], "epistemic_status": "observed"},
        {"path": "page.candidate_count", "value": len(candidates), "epistemic_status": "observed"},
    ]


def parse_funbio(source: dict[str, Any], response: requests.Response) -> tuple[list[dict[str, Any]], str]:
    soup = BeautifulSoup(response.content.decode("utf-8", errors="replace"), "html.parser")
    items: list[dict[str, Any]] = []
    skip = {"saiba mais", "submeter proposta", "inscreva-se", "home", "lista de seleções", "receba informações", "quem somos", "notícias", "login"}
    for anchor in soup.find_all("a", href=True):
        label = clean(anchor.get_text(" ", strip=True), 320)
        href = urljoin(response.url, anchor["href"].strip())
        if not is_http(href) or not same_host(href, "chamadas.funbio.org.br") or label.lower() in skip:
            continue
        if len(label) < 22 or any(term in label.lower() for term in ["política de privacidade", "voltar ao topo"]):
            continue
        item = candidate(label, href, term_hits=10)
        if item:
            items.append(item)
    return unique_candidates(items), "FUNBIO — Portal de Chamadas"


def parse_fundo_casa(source: dict[str, Any], response: requests.Response) -> tuple[list[dict[str, Any]], str]:
    soup = BeautifulSoup(response.content.decode("utf-8", errors="replace"), "html.parser")
    items: list[dict[str, Any]] = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(response.url, anchor["href"].strip())
        label = clean(anchor.get("title") or anchor.get_text(" ", strip=True), 320)
        if not same_host(href, "casa.org.br") or "/category/" in href or "/page/" in href:
            continue
        if len(label) < 28 or label.lower() in {"leia mais", "fundo casa", "home", "contato"}:
            continue
        if not any(term in f"{label} {href}".lower() for term in ["chamada", "edital", "programa", "prêmio", "premio", "apoio"]):
            continue
        item = candidate(label, href, term_hits=9)
        if item:
            items.append(item)
    return unique_candidates(items), "Fundo Casa — Editais"


def parse_boticario(source: dict[str, Any], response: requests.Response) -> tuple[list[dict[str, Any]], str]:
    soup = BeautifulSoup(response.content.decode("utf-8", errors="replace"), "html.parser")
    items: list[dict[str, Any]] = []
    terms = ["edital", "chamada", "inscri", "apoio a projetos", "selecionad", "teia"]
    for anchor in soup.find_all("a", href=True):
        href = urljoin(response.url, anchor["href"].strip())
        label = clean(anchor.get_text(" ", strip=True), 320)
        if not same_host(href, "fundacaogrupoboticario.org.br") or len(label) < 28:
            continue
        if not any(term in f"{label} {href}".lower() for term in terms):
            continue
        item = candidate(label, href, term_hits=8)
        if item:
            items.append(item)
    return unique_candidates(items), "Fundação Grupo Boticário — Notícias e chamadas"


def parse_bnb(source: dict[str, Any], response: requests.Response) -> tuple[list[dict[str, Any]], str]:
    soup = BeautifulSoup(response.content.decode("utf-8", errors="replace"), "html.parser")
    items: list[dict[str, Any]] = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(response.url, anchor["href"].strip())
        label = clean(anchor.get_text(" ", strip=True), 360)
        if not same_host(href, "bnb.gov.br") or len(label) < 20:
            continue
        if "edital" not in f"{label} {anchor.get('title', '')}".lower():
            continue
        item = candidate(label, href, term_hits=10)
        if item:
            items.append(item)
    return unique_candidates(items), "Banco do Nordeste — Editais do Fundeci"


def parse_sudene(source: dict[str, Any], response: requests.Response) -> tuple[list[dict[str, Any]], str]:
    if "pdf" in response.headers.get("content-type", "").lower() or response.content.startswith(b"%PDF"):
        item = candidate(source["name"], response.url, term_hits=10)
        return ([item] if item else []), source["name"]
    soup = BeautifulSoup(response.content.decode("utf-8", errors="replace"), "html.parser")
    items: list[dict[str, Any]] = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(response.url, anchor["href"].strip())
        label = clean(anchor.get_text(" ", strip=True), 320)
        if len(label) >= 18 and any(term in f"{label} {href}".lower() for term in ["edital", "chamamento", "projeto"]):
            item = candidate(label, href, term_hits=8)
            if item:
                items.append(item)
    return unique_candidates(items), "SUDENE — Editais e chamamentos"


def parse_embratur(source: dict[str, Any], response: requests.Response) -> tuple[list[dict[str, Any]], str]:
    soup = BeautifulSoup(response.content.decode("utf-8", errors="replace"), "html.parser")
    items: list[dict[str, Any]] = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(response.url, anchor["href"].strip())
        label = clean(anchor.get_text(" ", strip=True) or anchor.get("title"), 320)
        if not href.lower().split("?", 1)[0].endswith(".pdf") or len(label) < 12:
            continue
        item = candidate(label, href, term_hits=10)
        if item:
            items.append(item)
    return unique_candidates(items), "Embratur — Editais"


def parse_prosas(source: dict[str, Any], response: requests.Response) -> tuple[list[dict[str, Any]], str]:
    soup = BeautifulSoup(response.content.decode("utf-8", errors="replace"), "html.parser")
    items: list[dict[str, Any]] = []
    blocked_hosts = {"wa.me", "www.wa.me", "blog.prosas.com.br"}
    blocked_terms = {"fale com a nossa equipe", "cadastre-se", "acessar perfil", "ajuda", "suporte"}
    for anchor in soup.find_all("a", href=True):
        href = urljoin(response.url, anchor["href"].strip())
        label = clean(anchor.get_text(" ", strip=True), 320)
        host = urlparse(href).netloc.lower()
        haystack = f"{label} {href}".lower()
        if host in blocked_hosts or label.lower() in blocked_terms:
            continue
        if len(label) < 12 or not any(term in haystack for term in ["edital", "prêmio", "premio", "chamada", "concurso"]):
            continue
        if "prosas.com.br/editais/" not in href and not ("edital" in label.lower() or "chamada" in label.lower()):
            continue
        item = candidate(label, href, term_hits=7)
        if item:
            items.append(item)
    return unique_candidates(items), "Prosas — Central de Editais"


def parse_capta(source: dict[str, Any], response: requests.Response) -> tuple[list[dict[str, Any]], str]:
    soup = BeautifulSoup(response.content.decode("utf-8", errors="replace"), "html.parser")
    items: list[dict[str, Any]] = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(response.url, anchor["href"].strip())
        label = clean(anchor.get_text(" ", strip=True), 320)
        parent_p = anchor.find_parent("p")
        parent_text = clean(parent_p.get_text(" ", strip=True) if parent_p else "", 500)
        if parent_p and re.search(r"\bEdital\s*:", parent_text, flags=re.I):
            heading = parent_p.find_previous(["h2", "h3", "h4"])
            title = clean(heading.get_text(" ", strip=True) if heading else label, 320)
            item = candidate(title, href, term_hits=10)
            if item:
                items.append(item)
                continue
        if label.lower() not in {"edital", "edital completo", "acesse o edital", "confira o edital"}:
            continue
        parent = anchor.find_parent(["article", "li", "div"])
        title_node = parent.find(["h2", "h3", "h4"]) if parent else None
        title = clean(title_node.get_text(" ", strip=True) if title_node else (parent.get_text(" ", strip=True) if parent else ""), 320)
        item = candidate(title, href, term_hits=8)
        if item:
            items.append(item)
    if not items:
        for anchor in soup.find_all("a", href=True):
            href = urljoin(response.url, anchor["href"].strip())
            label = clean(anchor.get_text(" ", strip=True), 320)
            if "/oportunidades/" in href and href.rstrip("/") != response.url.rstrip("/") and len(label) >= 25:
                item = candidate(label, href, term_hits=6)
                if item:
                    items.append(item)
    return unique_candidates(items), "Capta — Oportunidades e editais abertos"


def parse_capitaai(source: dict[str, Any], response: requests.Response) -> tuple[list[dict[str, Any]], str]:
    soup = BeautifulSoup(response.content.decode("utf-8", errors="replace"), "html.parser")
    items: list[dict[str, Any]] = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(response.url, anchor["href"].strip())
        label = clean(anchor.get_text(" ", strip=True), 320)
        if len(label) < 20 or not any(term in f"{label} {href}".lower() for term in ["edital", "chamada", "prêmio", "premio"]):
            continue
        if "pay." in urlparse(href).netloc.lower() or "garantir" in label.lower():
            continue
        item = candidate(label, href, term_hits=5)
        if item:
            items.append(item)
    return unique_candidates(items), "Capitaai — Editais de meio ambiente"


PARSERS = {
    "funbio-chamadas": parse_funbio,
    "fundo-casa-editais": parse_fundo_casa,
    "fundacao-boticario-editais": parse_boticario,
    "bnb-fundeci": parse_bnb,
    "sudene-editais": parse_sudene,
    "embratur-editais": parse_embratur,
    "prosas-editais": parse_prosas,
    "capta-editais": parse_capta,
    "capitaai-meio-ambiente": parse_capitaai,
}


def _failed(source: dict[str, Any], observed: str, status: str, http_status: int | None, limitations: list[str]) -> dict[str, Any]:
    return {
        "observation_id": f"{source['id']}:{status}:{http_status or 'network'}",
        "source_id": source["id"],
        "source_url": source["url"],
        "observed_at": observed,
        "source_profile": source.get("source_type", "public"),
        "fetch": {"status": status, "method": "http_get", "http_status": http_status, "content_type": None},
        "content": {"media_type": "application/octet-stream", "content_hash": None, "byte_size": 0},
        "claims": [],
        "evidence_ids": [],
        "collector": {"name": source.get("collector", "wave2"), "version": "0.1.0", "repository": "https://github.com/viniburilux/Lux-Radar"},
        "limitations": limitations,
        "license_or_terms_note": "Reference URLs and metadata only; external content remains governed by source terms.",
    }


def fetch_wave2_source(source: dict[str, Any]) -> dict[str, Any]:
    observed = now()
    try:
        response = requests.get(source["url"], headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.8"}, timeout=30, allow_redirects=True)
    except requests.RequestException as exc:
        return _failed(source, observed, "failed", None, [f"Network failure: {type(exc).__name__}.", "No retry or access bypass was attempted."])
    body = response.content[:8_000_000]
    if not response.ok:
        return _failed(source, observed, "failed", response.status_code, [f"HTTP failure: {response.status_code}.", "No access bypass was attempted."])
    parser = PARSERS[source["id"]]
    candidates, page_title = parser(source, response)
    content_type = response.headers.get("content-type", "").split(";", 1)[0]
    return {
        "observation_id": f"{source['id']}:success:{response.status_code}",
        "source_id": source["id"],
        "source_url": source["url"],
        "observed_at": observed,
        "source_profile": source.get("source_type", "public"),
        "fetch": {"status": "success", "method": "http_get", "http_status": response.status_code, "content_type": content_type},
        "content": {"media_type": content_type or "application/octet-stream", "content_hash": content_hash(body), "byte_size": len(body)},
        "claims": claims_for(source, response, candidates, page_title),
        "evidence_ids": [],
        "collector": {"name": source.get("collector", "wave2"), "version": "0.1.0", "repository": "https://github.com/viniburilux/Lux-Radar"},
        "limitations": ["Source-specific Wave 2 adapter emits candidate links; detail verification and temporal validation remain downstream.", "Reference URLs and selected claims only; external content is not redistributed."],
        "license_or_terms_note": "Reference URLs and metadata only; external content remains governed by source terms.",
    }
