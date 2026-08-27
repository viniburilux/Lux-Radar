const state = {
  all: [],
  signals: [],
  current: [],
  secondary: [],
  filteredCurrent: [],
  filteredSecondary: [],
  manifest: null,
  secondaryLimit: 12,
};

const $ = (id) => document.getElementById(id);
const CACHE_VERSION = "signal-engine-20260827";

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
const reasonLabel = (reason) => ({
  current_opportunity: "Oportunidade atual", deadline_expired: "Prazo vencido",
  status_explicitly_closed: "Fechamento explícito", missing_deadline: "Prazo ausente",
  missing_status: "Status ausente", insufficient_evidence: "Evidência insuficiente",
  primary_source_not_verified: "Fonte primária não verificada", aggregator_only: "Somente agregador",
  parser_failure: "Falha de coleta/parsing", historical_content: "Conteúdo histórico",
  ongoing_program: "Programa em andamento", signal_only: "Somente sinal",
  not_opportunity: "Não é oportunidade", not_seen_in_release: "Não observado no release",
  duplicate: "Duplicata consolidada", unknown: "Motivo desconhecido",
}[reason] || reason || "Não observado");
const typeLabel = (type) => ({
  grant: "Grant", call: "Edital", public_call: "Chamada pública", research_call: "Pesquisa",
  funding: "Financiamento", sponsorship: "Patrocínio", scholarship: "Bolsa", procurement: "Procurement",
  partnership: "Parceria", innovation_program: "Programa de inovação", award: "Prêmio",
  event: "Evento", workshop: "Workshop", challenge: "Desafio", opportunity_candidate: "Oportunidade",
}[type] || String(type || "Oportunidade").replaceAll("_", " "));

const signalTypeLabel = (type) => ({
  opportunity: "Oportunidade", historical_content: "Conteúdo histórico", record_signal: "Sinal de registro",
  source_observation: "Observação de fonte", source_snapshot: "Snapshot de fonte", territorial_data: "Dado territorial",
  environmental_data: "Dado ambiental", funding_opportunity: "Financiamento / oportunidade", news_signal: "Sinal de notícia",
  discovery_signal: "Sinal de descoberta", research_funding: "Pesquisa / financiamento", procurement: "Procurement",
}[type] || String(type || "Sinal").replaceAll("_", " "));
const signalChangeLabel = (change) => ({
  NEW: "Novo", UPDATED: "Atualizado", UNCHANGED: "Sem mudança", SOURCE_UNAVAILABLE: "Fonte indisponível",
}[change] || change || "Não observado");

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
function getLensMatches(item) { return listValue(item.lens_matches || getDomains(item)); }
function getTerritories(item) { return [...new Set(listValue(item.territories).concat(listValue(item.geography?.territories)).concat(item.geography?.state ? [item.geography.state] : []))]; }
function getType(item) { return item.type || item.opportunity_type || "opportunity_candidate"; }
function getStatus(item) { return item.status || "UNKNOWN"; }
function getDeadline(item) { return item.deadline || item.deadlines?.submission || item.deadlines?.end || ""; }

const CLOSED_STATUSES = new Set(["CLOSED", "CANCELLED", "EXPIRED", "HISTORICAL", "SUPERSEDED"]);
const CURRENT_STATUSES = new Set(["VERIFIED", "OPEN", "UPCOMING", "EXTENDED", "READY_FOR_ACTION", "VERIFIED_PRIMARY", "ONGOING"]);
const NON_CURRENT_STATUSES = new Set(["UNKNOWN", "CANDIDATE", "INSUFFICIENT_EVIDENCE", "VERIFICATION_PENDING", "REJECTED"]);

function temporalState(item, now = new Date()) {
  const status = String(getStatus(item) || "UNKNOWN").toUpperCase();
  if (CLOSED_STATUSES.has(status)) return "HISTORICAL";
  const deadline = parseDate(getDeadline(item));
  if (deadline && deadline.getTime() < now.getTime()) return "HISTORICAL";
  if (NON_CURRENT_STATUSES.has(status)) return "SIGNAL";
  if (deadline && deadline.getTime() <= now.getTime() + 30 * 24 * 60 * 60 * 1000) return "CLOSING_SOON";
  if (deadline && deadline.getTime() > now.getTime() + 30 * 24 * 60 * 60 * 1000) return "UPCOMING";
  if (CURRENT_STATUSES.has(status)) return "ACTIVE";
  return "SIGNAL";
}

function getLifecycle(item) { return temporalState(item); }
function isCurrentAtNow(item) { return ["ACTIVE", "CLOSING_SOON", "UPCOMING", "ONGOING"].includes(temporalState(item)); }
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
  return [item.title, item.description, getOrganization(item), item.source_id, item.experience_type, item.lifecycle_state, ...getDomains(item), ...getLensMatches(item), ...getTerritories(item), ...getSources(item)].join(" ").toLowerCase();
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
  const lens = $("lens").value;
  const filtered = records.filter((item) => {
    const deadline = Boolean(getDeadline(item));
    return (!query || searchable(item).includes(query))
      && (!type || getType(item) === type)
      && (!domain || getDomains(item).includes(domain))
      && (!territory || getTerritories(item).includes(territory))
      && (!organization || getOrganization(item) === organization)
      && (!lens || getLensMatches(item).includes(lens))
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
  // Recalculate temporal validity from stored fields at view time, not from the last collection snapshot.
  state.current = state.all.filter((item) => isCurrentAtNow(item));
  state.secondary = state.all.filter((item) => !isCurrentAtNow(item));
  state.filteredCurrent = filterRecords(state.current);
  state.filteredSecondary = filterRecords(state.secondary);
  const closing = state.filteredCurrent.filter((item) => getLifecycle(item) === "CLOSING_SOON");
  const newItems = state.filteredCurrent.filter((item) => item.change_type === "NEW");

  $("current-count").textContent = state.filteredCurrent.length;
  $("hero-current-count").textContent = state.filteredCurrent.length;
  $("closing-count").textContent = closing.length;
  $("new-count").textContent = newItems.length;
  $("secondary-count").textContent = state.filteredSecondary.length;
  $("current-caption").textContent = `${state.filteredCurrent.length} exibidas`;
  $("closing-caption").textContent = `${closing.length} ${closing.length === 1 ? "oportunidade" : "oportunidades"}`;
  $("new-caption").textContent = `${newItems.length} ${newItems.length === 1 ? "oportunidade" : "oportunidades"}`;
  $("secondary-caption").textContent = `${state.filteredSecondary.length} registros na lente atual`;

  $("current-empty").hidden = state.filteredCurrent.length > 0;
  $("closing-empty").hidden = closing.length > 0;
  $("new-empty").hidden = newItems.length > 0;
  $("current-cards").innerHTML = state.filteredCurrent.map((item) => cardHtml(item)).join("");
  $("closing-cards").innerHTML = closing.slice(0, 6).map((item) => cardHtml(item, true)).join("");
  $("new-cards").innerHTML = newItems.slice(0, 6).map((item) => cardHtml(item, true)).join("");
  renderSecondary();
  renderSignals();
}

function renderSignals() {
  const lens = $("lens").value;
  const query = $("search").value.trim().toLowerCase();
  const visible = state.signals.filter((signal) => {
    const lensMatches = getLensMatches(signal);
    const text = [signal.title, signal.summary, signal.source_id, signal.signal_type, ...getDomains(signal), ...lensMatches].join(" ").toLowerCase();
    return (!lens || lensMatches.includes(lens)) && (!query || text.includes(query));
  }).sort((left, right) => {
    const rank = {NEW: 0, UPDATED: 1, SOURCE_UNAVAILABLE: 2, UNCHANGED: 3};
    return (rank[left.change_type] ?? 9) - (rank[right.change_type] ?? 9) || String(right.observed_at || "").localeCompare(String(left.observed_at || ""));
  });
  const sourceSignals = state.signals.filter((signal) => String(signal.canonical_key || "").startsWith("source:"));
  const failures = sourceSignals.filter((signal) => signal.change_type === "SOURCE_UNAVAILABLE");
  $("signal-new-count").textContent = state.signals.filter((signal) => signal.change_type === "NEW").length;
  $("signal-change-count").textContent = state.signals.filter((signal) => ["UPDATED", "SOURCE_UNAVAILABLE"].includes(signal.change_type)).length;
  $("signal-source-count").textContent = sourceSignals.length;
  $("signal-failure-count").textContent = failures.length;
  $("signals-caption").textContent = `${visible.length} ${visible.length === 1 ? "sinal" : "sinais"} na lente atual`;
  $("signals-empty").hidden = visible.length > 0;
  $("signal-cards").innerHTML = visible.slice(0, 12).map(signalCardHtml).join("");
  bindSignalButtons();
}

function signalCardHtml(signal) {
  const changeClass = signal.change_type === "SOURCE_UNAVAILABLE" ? "signal-failure" : signal.change_type === "UNCHANGED" ? "signal-unchanged" : "signal-active";
  const sourceLabel = signal.source_id || "Fonte não observada";
  const domains = getDomains(signal).slice(0, 3).map((value) => escapeHtml(value)).join(" · ") || "Domínio não observado";
  const count = Number.isFinite(signal.observed_item_count) ? `${signal.observed_item_count} itens observados` : signal.opportunity_id ? "Registro normalizado" : "Snapshot de fonte";
  return `<article class="signal-card ${changeClass}">
    <div class="signal-card-top"><span class="signal-change">${escapeHtml(signalChangeLabel(signal.change_type))}</span><span class="signal-type">${escapeHtml(signalTypeLabel(signal.signal_type))}</span></div>
    <h3>${escapeHtml(signal.title || "Sinal sem título")}</h3>
    <p>${escapeHtml(signal.summary || "Observação preservada com proveniência.")}</p>
    <div class="signal-facts"><span>${escapeHtml(sourceLabel)}</span><span>${escapeHtml(count)}</span><span>${escapeHtml(domains)}</span></div>
    <div class="signal-footer"><small>${escapeHtml(relativeDate(signal.observed_at))}</small><button class="signal-detail-button" data-signal-id="${escapeHtml(signal.signal_id)}">Ver observação</button></div>
  </article>`;
}

function openSignalDetail(id) {
  const signal = state.signals.find((candidate) => candidate.signal_id === id);
  if (!signal) return;
  const changes = listValue(signal.changes).filter(Boolean).slice(-8).map((change) => typeof change === "string" ? change : JSON.stringify(change)).join("\n");
  const limitations = listValue(signal.limitations);
  const fields = signal.observed_fields && Object.keys(signal.observed_fields).length ? JSON.stringify(signal.observed_fields, null, 2) : "Não há campos normalizados neste sinal.";
  const source = signal.source_url ? `<a class="primary-link" href="${escapeHtml(signal.source_url)}" target="_blank" rel="noopener">Abrir fonte observada →</a>` : "";
  $("detail-content").innerHTML = `<div class="detail-kicker"><span class="badge ${signal.change_type === "SOURCE_UNAVAILABLE" ? "unknown" : "verified"}">${escapeHtml(signalChangeLabel(signal.change_type))}</span><span class="quality-pill">${escapeHtml(signalTypeLabel(signal.signal_type))}</span></div>
    <h2>${escapeHtml(signal.title || "Sinal sem título")}</h2>
    <p class="detail-lede">${escapeHtml(signal.summary || "Observação estruturada de fonte pública.")}</p>
    <div class="action-box"><span>O que este sinal significa</span><strong>${signal.change_type === "SOURCE_UNAVAILABLE" ? "A fonte não respondeu neste release; isso não prova ausência de informação." : "O sistema observou este item e preservou sua evidência para interpretação posterior."}</strong></div>
    <h3>Observação</h3><dl><dt>Tipo</dt><dd>${escapeHtml(signalTypeLabel(signal.signal_type))}</dd><dt>Fonte</dt><dd>${escapeHtml(signal.source_id || "Não observada")}</dd><dt>Observado em</dt><dd>${escapeHtml(dateLabel(signal.observed_at))}</dd><dt>Status</dt><dd>${escapeHtml(signal.status || "Não observado")}</dd><dt>Itens</dt><dd>${escapeHtml(String(signal.observed_item_count ?? "Não observado"))}</dd><dt>Domínios</dt><dd>${escapeHtml(getDomains(signal).join(", ") || "Não observado")}</dd></dl>
    <h3>Campos observados</h3><pre class="signal-pre">${escapeHtml(fields)}</pre>
    <h3>Mudanças preservadas</h3><pre class="signal-pre">${escapeHtml(changes || "Nenhuma mudança detalhada neste snapshot.")}</pre>
    <h3>Limitações</h3><p>${escapeHtml(limitations.join(" ") || "Nenhuma limitação adicional observada.")}</p>
    <div class="detail-links">${source}</div>`;
  $("detail-dialog").showModal();
}

function bindSignalButtons() {
  document.querySelectorAll(".signal-detail-button").forEach((button) => button.addEventListener("click", () => openSignalDetail(button.dataset.signalId)));
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
  const isCurrent = isCurrentAtNow(item);
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
  const isCurrent = isCurrentAtNow(item);
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
      <dt>Motivo do estado</dt><dd>${escapeHtml(reasonLabel(item.reason_code))}</dd>
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
      fetch(`data/signals.json${suffix}`),
    ]);
    if (responses.some((response) => !response.ok)) throw new Error("O release público ainda não foi gerado.");
    const [allPayload, manifest, signalsPayload] = await Promise.all(responses.map((response) => response.json()));
    state.all = allPayload.opportunities || [];
    state.signals = signalsPayload.signals || [];
    state.manifest = manifest;
    state.current = state.all.filter((item) => isCurrentAtNow(item));
    state.secondary = state.all.filter((item) => !isCurrentAtNow(item));
    populateFilters();
    $("hero-release").textContent = `Release ${manifest.release_id}`;
    $("source-label").textContent = `${manifest.source_ids?.length || 0} fontes observadas`;
    $("updated-label").textContent = `Atualizado em ${dateLabel(manifest.created_at)}`;
    $("lens").value = manifest.default_lens || "sustainability";
    render();
  } catch (error) {
    $("error").textContent = error.message;
    $("error").hidden = false;
  }
}

["search", "lens", "type", "domain", "territory", "organization", "deadline", "sort"].forEach((id) => $(id).addEventListener("input", render));
$("show-more-secondary").addEventListener("click", () => { state.secondaryLimit += 12; renderSecondary(); });
$("close-detail").addEventListener("click", () => $("detail-dialog").close());
$("detail-dialog").addEventListener("click", (event) => { if (event.target === $("detail-dialog")) $("detail-dialog").close(); });
bindScrollButtons();
load();
