const state = { opportunities: [], manifest: null, filtered: [] };
const $ = (id) => document.getElementById(id);

const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#039;", '"':"&quot;"}[char]));
const listValue = (value) => Array.isArray(value) ? value : (value ? [value] : []);
const dateLabel = (value) => {
  if (!value) return "Não observado";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? escapeHtml(value) : parsed.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
};
const statusLabel = (status) => ({OPEN: "Aberta", UPCOMING: "Em breve", CLOSED: "Encerrada", EXPIRED: "Encerrada", EXTENDED: "Prorrogada", CANCELLED: "Cancelada", UNKNOWN: "Desconhecida", ready_for_action: "Em ação", unknown: "Desconhecida"}[status] || status || "Desconhecido");
const statusClass = (status) => ["CLOSED", "EXPIRED", "closed"].includes(status) ? "closed" : ["UNKNOWN", "unknown"].includes(status) ? "unknown" : "";

function setOptions(id, values) {
  const select = $(id);
  const unique = [...new Set(values.filter(Boolean).map(String))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  select.innerHTML = '<option value="">Todos</option>' + unique.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
}

function getDomains(item) { return listValue(item.domains); }
function getTerritories(item) { return listValue(item.territories).concat(listValue(item.geography?.territories)).concat(item.geography?.state ? [item.geography.state] : []); }
function getType(item) { return item.type || item.opportunity_type || "opportunity_candidate"; }
function getStatus(item) { return item.status || "UNKNOWN"; }
function getDeadline(item) { return item.deadline || item.deadlines?.submission || ""; }
function searchable(item) { return [item.title, item.description, item.organization, item.issuer?.name, item.source_id, ...getDomains(item), ...getTerritories(item)].join(" ").toLowerCase(); }

function populateFilters() {
  setOptions("domain", state.opportunities.flatMap(getDomains));
  setOptions("territory", state.opportunities.flatMap(getTerritories));
  setOptions("type", state.opportunities.map(getType));
  setOptions("status", state.opportunities.map(getStatus));
}

function render() {
  const query = $("search").value.trim().toLowerCase();
  const domain = $("domain").value;
  const territory = $("territory").value;
  const type = $("type").value;
  const status = $("status").value;
  const deadlineFilter = $("deadline").value;
  state.filtered = state.opportunities.filter((item) => {
    const hasDeadline = Boolean(getDeadline(item));
    return (!query || searchable(item).includes(query))
      && (!domain || getDomains(item).includes(domain))
      && (!territory || getTerritories(item).includes(territory))
      && (!type || getType(item) === type)
      && (!status || getStatus(item) === status)
      && (!deadlineFilter || (deadlineFilter === "with_deadline" ? hasDeadline : !hasDeadline));
  });
  $("visible-count").textContent = state.filtered.length;
  $("open-count").textContent = state.filtered.filter((item) => ["OPEN", "ready_for_action", "UPCOMING", "EXTENDED"].includes(getStatus(item))).length;
  $("updated-at").textContent = dateLabel(state.manifest?.created_at);
  $("empty").hidden = state.filtered.length > 0;
  $("cards").innerHTML = state.filtered.map(cardHtml).join("");
  document.querySelectorAll(".detail-button").forEach((button) => button.addEventListener("click", () => openDetail(button.dataset.id)));
}

function cardHtml(item) {
  const status = getStatus(item);
  const organization = item.organization || item.issuer?.name || item.source_id || "Fonte não informada";
  const deadline = getDeadline(item);
  const domains = getDomains(item).slice(0, 3).join(" · ");
  return `<article class="card">
    <div class="card-top"><span class="badge ${statusClass(status)}">${escapeHtml(statusLabel(status))}</span><span class="source">${escapeHtml(item.source_id || "Fonte")}</span></div>
    <h2>${escapeHtml(item.title || "Oportunidade sem título")}</h2>
    <p>${escapeHtml(item.description || domains || "Oportunidade observada em fonte pública; verifique os detalhes oficiais.")}</p>
    <div class="card-footer"><div class="source"><strong>${escapeHtml(organization)}</strong><br>${deadline ? `Prazo: ${dateLabel(deadline)}` : "Prazo não observado"}</div><button class="detail-button" data-id="${escapeHtml(item.opportunity_id || item.id || item.official_url)}">Ver detalhe</button></div>
  </article>`;
}

function openDetail(id) {
  const item = state.opportunities.find((candidate) => (candidate.opportunity_id || candidate.id || candidate.official_url) === id);
  if (!item) return;
  const organization = item.organization || item.issuer?.name || "Não observado";
  const domains = getDomains(item).join(", ") || "Não observado";
  const territories = getTerritories(item).join(", ") || "Não observado";
  const deadline = getDeadline(item);
  const funding = item.funding && Object.keys(item.funding).length ? JSON.stringify(item.funding) : "Não observado";
  const eligibility = item.eligibility && Object.keys(item.eligibility).length ? JSON.stringify(item.eligibility) : "Não observado";
  $("detail-content").innerHTML = `<span class="badge ${statusClass(getStatus(item))}">${escapeHtml(statusLabel(getStatus(item)))}</span>
    <h2>${escapeHtml(item.title || "Oportunidade sem título")}</h2>
    <p>${escapeHtml(item.description || "Registro candidato observado em fonte pública.")}</p>
    <h3>Registro</h3><dl>
      <dt>Organização</dt><dd>${escapeHtml(organization)}</dd>
      <dt>Tipo</dt><dd>${escapeHtml(getType(item))}</dd>
      <dt>Domínios</dt><dd>${escapeHtml(domains)}</dd>
      <dt>Território</dt><dd>${escapeHtml(territories)}</dd>
      <dt>Prazo</dt><dd>${escapeHtml(dateLabel(deadline))}</dd>
      <dt>Financiamento</dt><dd>${escapeHtml(funding)}</dd>
      <dt>Elegibilidade</dt><dd>${escapeHtml(eligibility)}</dd>
      <dt>Última atualização</dt><dd>${escapeHtml(dateLabel(item.updated_at || item.last_seen_at))}</dd>
    </dl>
    <h3>Proveniência</h3><dl>
      <dt>Fonte</dt><dd>${escapeHtml(item.source_id || "Não observado")}</dd>
      <dt>Confiança</dt><dd>${escapeHtml(item.confidence ?? item.context?.confidence ?? "Não informada")}</dd>
      <dt>Evidências</dt><dd>${escapeHtml((item.evidence || item.evidence_ids || []).join(", ") || "Não observadas")}</dd>
    </dl>
    <p><a href="${escapeHtml(item.official_url || "#")}" target="_blank" rel="noopener">Abrir fonte oficial</a></p>`;
  $("detail-dialog").showModal();
}

async function load() {
  try {
    const [opportunitiesResponse, manifestResponse] = await Promise.all([fetch("data/opportunities.json"), fetch("data/release-manifest.json")]);
    if (!opportunitiesResponse.ok || !manifestResponse.ok) throw new Error("O release público ainda não foi gerado.");
    const opportunitiesPayload = await opportunitiesResponse.json();
    state.opportunities = opportunitiesPayload.opportunities || [];
    state.manifest = await manifestResponse.json();
    $("release-label").textContent = `Release ${state.manifest.release_id}`;
    $("source-label").textContent = `${state.manifest.source_ids?.length || 0} fontes observadas`;
    populateFilters();
    render();
  } catch (error) {
    $("error").textContent = error.message;
    $("error").hidden = false;
  }
}

["search", "domain", "territory", "type", "status", "deadline"].forEach((id) => $(id).addEventListener("input", render));
$("close-detail").addEventListener("click", () => $("detail-dialog").close());
$("detail-dialog").addEventListener("click", (event) => { if (event.target === $("detail-dialog")) $("detail-dialog").close(); });
load();
