const state = {
  all: [],
  current: [],
  secondary: [],
  filteredCurrent: [],
  filteredSecondary: [],
  manifest: null,
  secondaryLimit: 12,
};

const $ = (id) => document.getElementById(id);
const CACHE_VERSION = "product-layer-20260826";

const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#039;", '"':"&quot;"}[char]));
const listValue = (value) => Array.isArray(value) ? value : (value ? [value] : []);
const statusLabel = (status) => ({
  VERIFIED: "Verificada", CANDIDATE: "Candidata", CLOSED: "Encerrada", UNKNOWN: "Não verificada",
  INSUFFICIENT_EVIDENCE: "Evidência insuficiente", OPEN: "Aberta", UPCOMING: "Próxima",
  EXTENDED: "Prorrogada", CANCELLED: "Cancelada", EXPIRED: "Encerrada",
}[status] || status || "Não observado");
const lifecycleLabel = (stateName) => ({
  ACTIVE: "Aberta", CLOSING_SOON: "Fechando em breve", UPCOMING: "Próxima",
  ONGOING: "Em andamento", SIGNAL: "Sinal", HISTORICAL: "Histórico",
}[stateName] || stateName || "Não observado");
const typeLabel = (type) => ({
  grant: "Grant", call: "Edital", public_call: "Chamada pública", research_call: "Pesquisa",
  funding: "Financiamento", sponsorship: "Patrocínio", scholarship: "Bolsa", procurement: "Procurement",
  partnership: "Parceria", innovation_program: "Programa de inovação", award: "Prêmio",
  event: "Evento", workshop: "Workshop", challenge: "Desafio", opportunity_candidate: "Oportunidade",
}[type] || String(type || "Oportunidade").replaceAll("_", " "));

function parseDate(value) {
  if (!value || typeof value !== "string") return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function dateLabel(value) {
  if (!value) return "Não observado";
  const parsed = parseDate(value);
  return parsed ? parsed.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" }) : escapeHtml(value);
}

function relativeDate(value) {
  const parsed = parseDate(value);
  if (!parsed) return "Atualização não observada";
  return `Atualizado em ${parsed.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" })}`;
}

function getDomains(item) { return listValue(item.domains || item.themes); }
function getTerritories(item) { return [...new Set(listValue(item.territories).concat(listValue(item.geography?.territories)).concat(item.geography?.state ? [item.geography.state] : []))]; }
function getType(item) { return item.type || item.opportunity_type || "opportunity_candidate"; }
function getStatus(item) { return item.status || "UNKNOWN"; }
function getLifecycle(item) { return item.lifecycle_state || (getStatus(item) === "VERIFIED" ? "ONGOING" : getStatus(item) === "CLOSED" ? "HISTORICAL" : "SIGNAL"); }
function getDeadline(item) { return item.deadline || item.deadlines?.submission || item.deadlines?.end || ""; }
function getOrganization(item) { return item.organization || item.issuer?.name || item.source_id || "Organização não observada"; }
function getFunding(item) {
  const funding = item.funding || {};
  if (funding.amount) return `${funding.currency || ""} ${Number(funding.amount).toLocaleString("pt-BR")}`.trim();
  if (funding.maximum) return `${funding.currency || ""} até ${Number(funding.maximum).toLocaleString("pt-BR")}`.trim();
  if (funding.minimum) return `${funding.currency || ""} a partir de ${Number(funding.minimum).toLocaleString("pt-BR")}`.trim();
  return "Valor não observado";
}
function getSources(item) { return [...new Set(listValue(item.sources).concat(item.source_id || []).filter(Boolean))]; }
function getId(item) { return item.opportunity_id || item.id || item.official_url; }
function searchable(item) {
  return [item.title, item.description, getOrganization(item), item.source_id, item.experience_type, item.lifecycle_state, ...getDomains(item), ...getTerritories(item), ...getSources(item)].join(" ").toLowerCase();
}
function statusClass(value) {
  if (["HISTORICAL", "CLOSED", "EXPIRED"].includes(value)) return "closed";
  if (["SIGNAL", "UNKNOWN", "INSUFFICIENT_EVIDENCE"].includes(value)) return "unknown";
  if (["ACTIVE", "ONGOING", "VERIFIED"].includes(value)) return "verified";
  if (["CLOSING_SOON", "UPCOMING", "CANDIDATE"].includes(value)) return "candidate";
  return "";
}

function setOptions(id, values, firstLabel = "Todos") {
  const select = $(id);
  const unique = [...new Set(values.filter(Boolean).map(String))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  select.innerHTML = `<option value="">${firstLabel}</option>` + unique.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
}

function populateFilters() {
  setOptions("type", state.all.flatMap((item) => [getType(item)]));
  setOptions("domain", state.all.flatMap(getDomains));
  setOptions("territory", state.all.flatMap(getTerritories));
  setOptions("organization", state.all.map(getOrganization), "Todas");
}

function filterRecords(records) {
  const query = $("search").value.trim().toLowerCase();
  const type = $("type").value;
  const domain = $("domain").value;
  const territory = $("territory").value;
  const organization = $("organization").value;
  const deadlineFilter = $("deadline").value;
  const filtered = records.filter((item) => {
    const deadline = Boolean(getDeadline(item));
    return (!query || searchable(item).includes(query))
      && (!type || getType(item) === type)
      && (!domain || getDomains(item).includes(domain))
      && (!territory || getTerritories(item).includes(territory))
      && (!organization || getOrganization(item) === organization)
      && (!deadlineFilter || (deadlineFilter === "with_deadline" ? deadline : !deadline));
  });
  const sort = $("sort").value;
  return filtered.sort((left, right) => {
    if (sort === "title_asc") return String(left.title || "").localeCompare(String(right.title || ""), "pt-BR");
    if (sort === "updated_desc") return String(right.updated_at || right.last_seen_at || "").localeCompare(String(left.updated_at || left.last_seen_at || ""));
    const leftDeadline = parseDate(getDeadline(left))?.getTime() || Number.MAX_SAFE_INTEGER;
    const rightDeadline = parseDate(getDeadline(right))?.getTime() || Number.MAX_SAFE_INTEGER;
    return leftDeadline - rightDeadline;
  });
}

function render() {
  state.filteredCurrent = filterRecords(state.current);
  state.filteredSecondary = filterRecords(state.secondary);
  const closing = state.filteredCurrent.filter((item) => getLifecycle(item) === "CLOSING_SOON");
  const newItems = state.filteredCurrent.filter((item) => item.change_type === "NEW");

  $("current-count").textContent = state.current.length;
  $("hero-current-count").textContent = state.current.length;
  $("closing-count").textContent = closing.length;
  $("new-count").textContent = state.current.filter((item) => item.change_type === "NEW").length;
  $("secondary-count").textContent = state.secondary.length;
  $("current-caption").textContent = `${state.filteredCurrent.length} exibidas`;
  $("closing-caption").textContent = `${closing.length} ${closing.length === 1 ? "oportunidade" : "oportunidades"}`;
  $("new-caption").textContent = `${newItems.length} ${newItems.length === 1 ? "oportunidade" : "oportunidades"}`;
  $("secondary-caption").textContent = `${state.secondary.length} registros`;

  $("current-empty").hidden = state.filteredCurrent.length > 0;
  $("closing-empty").hidden = closing.length > 0;
  $("new-empty").hidden = newItems.length > 0;
  $("current-cards").innerHTML = state.filteredCurrent.map((item) => cardHtml(item)).join("");
  $("closing-cards").innerHTML = closing.slice(0, 6).map((item) => cardHtml(item, true)).join("");
  $("new-cards").innerHTML = newItems.slice(0, 6).map((item) => cardHtml(item, true)).join("");
  renderSecondary();
}

function renderSecondary() {
  const visible = state.filteredSecondary.slice(0, state.secondaryLimit);
  $("secondary-cards").innerHTML = visible.map((item) => cardHtml(item, true)).join("");
  $("show-more-secondary").hidden = state.filteredSecondary.length <= state.secondaryLimit;
  $("show-more-secondary").textContent = `Mostrar mais (${state.filteredSecondary.length - state.secondaryLimit})`;
  bindDetailButtons();
}

function cardHtml(item, compact = false) {
  const lifecycle = getLifecycle(item);
  const status = getStatus(item);
  const domains = getDomains(item).slice(0, 2).map((value) => escapeHtml(value)).join(" · ") || "Tema não observado";
  const territories = getTerritories(item).slice(0, 2).map((value) => escapeHtml(value)).join(" · ") || "Território não observado";
  const deadline = getDeadline(item);
  const sources = getSources(item);
  const isCurrent = item.current_view === true || lifecycle === "ACTIVE" || lifecycle === "CLOSING_SOON" || lifecycle === "UPCOMING" || lifecycle === "ONGOING";
  const stateText = isCurrent ? lifecycleLabel(lifecycle) : lifecycleLabel(lifecycle);
  const qualityText = status === "VERIFIED" ? "Verificada" : status === "CANDIDATE" ? "Pendente" : statusLabel(status);
  return `<article class="card ${compact ? "card-compact" : ""} ${isCurrent ? "card-current" : "card-secondary"}">
    <div class="card-top"><span class="badge ${statusClass(lifecycle)}">${escapeHtml(stateText)}</span><span class="quality-pill ${statusClass(status)}">${escapeHtml(qualityText)}</span><span class="source-count">${sources.length} ${sources.length === 1 ? "fonte" : "fontes"}</span></div>
    <h3>${escapeHtml(item.title || "Registro sem título")}</h3>
    <p class="card-description">${escapeHtml(item.description || (isCurrent ? "Oportunidade com evidência oficial suficiente para consulta." : "Sinal observado em fonte pública; ainda não promovido a oportunidade atual."))}</p>
    <div class="card-facts">
      <div><span>Tipo</span><strong>${escapeHtml(typeLabel(getType(item)))}</strong></div>
      <div><span>Tema</span><strong>${domains}</strong></div>
      <div><span>Território</span><strong>${territories}</strong></div>
      <div><span>${isCurrent ? "Prazo" : "Observação"}</span><strong>${isCurrent ? escapeHtml(deadline ? dateLabel(deadline) : "Não observado") : escapeHtml(relativeDate(item.updated_at || item.last_seen_at))}</strong></div>
    </div>
    <div class="card-footer"><div class="source"><strong>${escapeHtml(getOrganization(item))}</strong><br>${escapeHtml(getFunding(item))}</div><button class="detail-button" data-id="${escapeHtml(getId(item))}">${isCurrent ? "Ver oportunidade" : "Ver registro"}</button></div>
  </article>`;
}

function formatList(value) {
  const values = listValue(value).filter(Boolean);
  return values.length ? values.map(escapeHtml).join("<br>") : "Não observado";
}

function openDetail(id) {
  const item = state.all.find((candidate) => getId(candidate) === id);
  if (!item) return;
  const status = getStatus(item);
  const lifecycle = getLifecycle(item);
  const sources = getSources(item);
  const evidence = listValue(item.evidence || item.evidence_ids);
  const limitations = listValue(item.provenance?.limitations);
  const officialUrl = item.official_url || "";
  const pdfUrl = item.official_pdf_url || "";
  const isCurrent = item.current_view === true;
  const action = isCurrent
    ? `Consulte a fonte oficial e verifique os requisitos antes de preparar uma submissão. ${item.next_action?.description || ""}`
    : "Acompanhe a fonte oficial: este registro permanece como sinal ou histórico porque ainda não há evidência suficiente de oportunidade atual.";
  $("detail-content").innerHTML = `<div class="detail-kicker"><span class="badge ${statusClass(lifecycle)}">${escapeHtml(lifecycleLabel(lifecycle))}</span><span class="quality-pill ${statusClass(status)}">${escapeHtml(statusLabel(status))}</span></div>
    <h2>${escapeHtml(item.title || "Registro sem título")}</h2>
    <p class="detail-lede">${escapeHtml(item.description || "Registro observado em fonte pública.")}</p>
    <div class="action-box"><span>O que fazer agora</span><strong>${escapeHtml(action)}</strong></div>
    <h3>Informações da oportunidade</h3><dl>
      <dt>Organização</dt><dd>${escapeHtml(getOrganization(item))}</dd>
      <dt>Tipo</dt><dd>${escapeHtml(typeLabel(getType(item)))}</dd>
      <dt>Tema</dt><dd>${escapeHtml(getDomains(item).join(", ") || "Não observado")}</dd>
      <dt>Território</dt><dd>${escapeHtml(getTerritories(item).join(", ") || "Não observado")}</dd>
      <dt>Prazo</dt><dd>${escapeHtml(dateLabel(getDeadline(item)))}</dd>
      <dt>Valor</dt><dd>${escapeHtml(getFunding(item))}</dd>
      <dt>Elegibilidade</dt><dd>${formatList(item.eligibility)}</dd>
      <dt>Última atualização</dt><dd>${escapeHtml(dateLabel(item.updated_at || item.last_seen_at))}</dd>
    </dl>
    <h3>Fonte e evidência</h3><dl>
      <dt>Fonte primária</dt><dd>${escapeHtml(sources[0] || item.source_id || "Não observado")}</dd>
      <dt>Encontrada também em</dt><dd>${sources.length > 1 ? escapeHtml(sources.slice(1).join(", ")) : "Não observado"}</dd>
      <dt>Estado de qualidade</dt><dd>${escapeHtml(item.verification?.reason || statusLabel(status))}</dd>
      <dt>Evidências</dt><dd>${evidence.length ? escapeHtml(evidence.join(", ")) : "Não observadas"}</dd>
      <dt>Limitações</dt><dd>${limitations.length ? escapeHtml(limitations.join(" ")) : "Nenhuma limitação adicional observada."}</dd>
    </dl>
    <div class="detail-links">${officialUrl ? `<a class="primary-link" href="${escapeHtml(officialUrl)}" target="_blank" rel="noopener">Abrir fonte oficial →</a>` : ""}${pdfUrl ? `<a href="${escapeHtml(pdfUrl)}" target="_blank" rel="noopener">Abrir documento PDF oficial</a>` : ""}</div>`;
  $("detail-dialog").showModal();
}

function bindDetailButtons() {
  document.querySelectorAll(".detail-button").forEach((button) => button.addEventListener("click", () => openDetail(button.dataset.id)));
}

function bindScrollButtons() {
  document.querySelectorAll("[data-scroll]").forEach((button) => button.addEventListener("click", () => $(button.dataset.scroll)?.scrollIntoView({ behavior: "smooth", block: "start" })));
}

async function load() {
  try {
    const suffix = `?v=${CACHE_VERSION}`;
    const responses = await Promise.all([
      fetch(`data/opportunities.json${suffix}`),
      fetch(`data/release-manifest.json${suffix}`),
      fetch(`data/current-opportunities.json${suffix}`),
      fetch(`data/signals-history.json${suffix}`),
    ]);
    if (responses.some((response) => !response.ok)) throw new Error("O release público ainda não foi gerado.");
    const [allPayload, manifest, currentPayload, secondaryPayload] = await Promise.all(responses.map((response) => response.json()));
    state.all = allPayload.opportunities || [];
    state.manifest = manifest;
    state.current = currentPayload.opportunities || state.all.filter((item) => item.current_view === true);
    state.secondary = secondaryPayload.signals || state.all.filter((item) => item.current_view !== true);
    populateFilters();
    $("hero-release").textContent = `Release ${manifest.release_id}`;
    $("source-label").textContent = `${manifest.source_ids?.length || 0} fontes observadas`;
    $("updated-label").textContent = `Atualizado em ${dateLabel(manifest.created_at)}`;
    render();
  } catch (error) {
    $("error").textContent = error.message;
    $("error").hidden = false;
  }
}

["search", "type", "domain", "territory", "organization", "deadline", "sort"].forEach((id) => $(id).addEventListener("input", render));
$("show-more-secondary").addEventListener("click", () => { state.secondaryLimit += 12; renderSecondary(); });
$("close-detail").addEventListener("click", () => $("detail-dialog").close());
$("detail-dialog").addEventListener("click", (event) => { if (event.target === $("detail-dialog")) $("detail-dialog").close(); });
bindScrollButtons();
load();
