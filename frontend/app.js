// app.js — PromptForge frontend

const API = "http://localhost:8000";

// ── Estado global ─────────────────────────────────────────────────────────────
const state = {
  prompts: [],
  categories: [],
  tags: [],
  activeTab: "prompts",
  search: "",
  filterCategory: null,
  filterTag: null,
  filterFavorite: false,
  editingPrompt: null,  // null = criar, objeto = editar
  selectedTagIds: [],
};

// ── Helpers HTTP ──────────────────────────────────────────────────────────────
async function api(path, options = {}) {
  try {
    const res = await fetch(`${API}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (res.status === 204) return null;
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Erro na API");
    return data;
  } catch (e) {
    toast(e.message, "error");
    throw e;
  }
}

const get    = (path) => api(path);
const post   = (path, body) => api(path, { method: "POST", body: JSON.stringify(body) });
const patch  = (path, body) => api(path, { method: "PATCH", body: JSON.stringify(body) });
const del    = (path) => api(path, { method: "DELETE" });

// ── Toast ─────────────────────────────────────────────────────────────────────
function toast(msg, type = "success") {
  const container = document.getElementById("toastContainer");
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

// ── Render principal ──────────────────────────────────────────────────────────
async function loadAll() {
  const [prompts, categories, tags] = await Promise.all([
    buildPromptsQuery(),
    get("/categories/"),
    get("/tags/"),
  ]);
  state.prompts    = prompts    || [];
  state.categories = categories || [];
  state.tags       = tags       || [];
  renderAll();
}

function buildPromptsQuery() {
  const params = new URLSearchParams();
  if (state.search)         params.set("search", state.search);
  if (state.filterCategory) params.set("category_id", state.filterCategory);
  if (state.filterTag)      params.set("tag_id", state.filterTag);
  if (state.filterFavorite) params.set("favorite", "true");
  return get(`/prompts/?${params}`);
}

function renderAll() {
  renderStats();
  renderSidebar();
  renderPrompts();
}

// ── Stats ──────────────────────────────────────────────────────────────────────
function renderStats() {
  const total   = state.prompts.length;
  const favs    = state.prompts.filter(p => p.is_favorite).length;
  const uses    = state.prompts.reduce((a, p) => a + p.use_count, 0);
  document.getElementById("statTotal").textContent   = total;
  document.getElementById("statFavs").textContent    = favs;
  document.getElementById("statUses").textContent    = uses;
  document.getElementById("statCats").textContent    = state.categories.length;
}

// ── Sidebar ────────────────────────────────────────────────────────────────────
function renderSidebar() {
  // Categorias
  const catList = document.getElementById("categoryList");
  catList.innerHTML = `
    <div class="sidebar-item ${!state.filterCategory ? 'active' : ''}" onclick="filterByCategory(null)">
      <span>📋</span> Todas
    </div>
    ${state.categories.map(c => `
      <div class="sidebar-item ${state.filterCategory === c.id ? 'active' : ''}" onclick="filterByCategory(${c.id})">
        <span>📁</span> ${esc(c.name)}
      </div>
    `).join("")}
  `;

  // Tags
  const tagList = document.getElementById("tagList");
  tagList.innerHTML = state.tags.map(t => `
    <span class="tag" style="cursor:pointer; ${state.filterTag === t.id ? 'border-color:var(--accent);color:var(--accent)' : ''}"
      onclick="filterByTag(${t.id})">${esc(t.name)}</span>
  `).join("") || '<span style="color:var(--muted);font-size:12px;padding:0 8px">Nenhuma tag</span>';
}

// ── Prompts grid ───────────────────────────────────────────────────────────────
function renderPrompts() {
  const grid = document.getElementById("promptsGrid");
  if (!state.prompts.length) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
      <div style="font-size:40px">🔨</div>
      <p>Nenhum prompt encontrado.<br>Crie o primeiro clicando em <strong>+ Novo Prompt</strong>.</p>
    </div>`;
    return;
  }

  grid.innerHTML = state.prompts.map(p => `
    <div class="prompt-card" onclick="openDetail(${p.id})">
      <div class="prompt-card-header">
        <div class="prompt-card-title">${esc(p.title)}</div>
        <div class="prompt-card-actions" onclick="event.stopPropagation()">
          <button class="btn-icon fav-star" title="Favoritar" onclick="toggleFav(${p.id})">
            ${p.is_favorite ? "⭐" : "☆"}
          </button>
          <button class="btn btn-sm btn-secondary" onclick="openEdit(${p.id})">✏️</button>
          <button class="btn btn-sm btn-danger" onclick="confirmDelete(${p.id}, '${esc(p.title)}')">🗑️</button>
        </div>
      </div>
      <div class="prompt-card-content">${esc(p.content)}</div>
      <div class="prompt-card-footer">
        <div class="tags">
          ${p.category ? `<span class="category-badge">${esc(p.category.name)}</span>` : ""}
          ${p.tags.map(t => `<span class="tag">${esc(t.name)}</span>`).join("")}
        </div>
        <span class="use-count" title="Vezes usado">▶ ${p.use_count}x</span>
      </div>
    </div>
  `).join("");
}

// ── Filtros ────────────────────────────────────────────────────────────────────
function filterByCategory(id) {
  state.filterCategory = id;
  applyFilters();
}
function filterByTag(id) {
  state.filterTag = (state.filterTag === id) ? null : id;
  applyFilters();
}
async function applyFilters() {
  state.prompts = await buildPromptsQuery() || [];
  renderAll();
}

document.getElementById("searchInput").addEventListener("input", debounce(async (e) => {
  state.search = e.target.value.trim();
  state.prompts = await buildPromptsQuery() || [];
  renderAll();
}, 350));

document.getElementById("favFilter").addEventListener("change", async (e) => {
  state.filterFavorite = e.target.checked;
  state.prompts = await buildPromptsQuery() || [];
  renderAll();
});

// ── Modal Novo/Editar ──────────────────────────────────────────────────────────
function openCreate() {
  state.editingPrompt = null;
  state.selectedTagIds = [];
  document.getElementById("modalTitle").textContent = "Novo Prompt";
  document.getElementById("promptTitle").value  = "";
  document.getElementById("promptContent").value = "";
  document.getElementById("promptDesc").value   = "";
  document.getElementById("promptCategory").value = "";
  renderTagsPicker();
  showModal("promptModal");
}

async function openEdit(id) {
  const prompt = await get(`/prompts/${id}`);
  if (!prompt) return;
  state.editingPrompt  = prompt;
  state.selectedTagIds = prompt.tags.map(t => t.id);
  document.getElementById("modalTitle").textContent  = "Editar Prompt";
  document.getElementById("promptTitle").value       = prompt.title;
  document.getElementById("promptContent").value     = prompt.content;
  document.getElementById("promptDesc").value        = prompt.description || "";
  document.getElementById("promptCategory").value    = prompt.category_id || "";
  populateCategorySelect();
  renderTagsPicker();
  showModal("promptModal");
}

async function openDetail(id) {
  const prompt = await get(`/prompts/${id}`);
  if (!prompt) return;

  // Registra uso
  await post(`/prompts/${id}/use`);
  prompt.use_count++;

  document.getElementById("detailTitle").textContent   = prompt.title;
  document.getElementById("detailContent").value       = prompt.content;
  document.getElementById("detailDescription").textContent = prompt.description || "—";
  document.getElementById("detailCategory").textContent = prompt.category?.name || "—";
  document.getElementById("detailTags").innerHTML      = prompt.tags.map(t => `<span class="tag">${esc(t.name)}</span>`).join("") || "—";
  document.getElementById("detailUseCount").textContent = prompt.use_count;
  document.getElementById("detailFav").textContent     = prompt.is_favorite ? "⭐ Favorito" : "☆ Favoritar";
  document.getElementById("detailFav").onclick         = () => toggleFavDetail(id);
  document.getElementById("detailEdit").onclick        = () => { closeModal("detailModal"); openEdit(id); };

  // Versões
  const versions = await get(`/prompts/${id}/versions`);
  const vList = document.getElementById("versionList");
  vList.innerHTML = (versions || []).reverse().map(v => `
    <div style="background:var(--surface2);border:1px solid var(--border);border-radius:7px;padding:10px 14px;margin-bottom:8px">
      <div style="font-size:11px;color:var(--muted);margin-bottom:6px">Versão ${v.version} — ${new Date(v.saved_at).toLocaleString()}</div>
      <pre style="white-space:pre-wrap;font-size:12px;color:var(--text)">${esc(v.content)}</pre>
    </div>
  `).join("") || "<p style='color:var(--muted)'>Nenhuma versão salva.</p>";

  showModal("detailModal");
}

// ── Salvar prompt ──────────────────────────────────────────────────────────────
async function savePrompt() {
  const title    = document.getElementById("promptTitle").value.trim();
  const content  = document.getElementById("promptContent").value.trim();
  const desc     = document.getElementById("promptDesc").value.trim();
  const catId    = document.getElementById("promptCategory").value;

  if (!title || !content) { toast("Título e conteúdo são obrigatórios.", "error"); return; }

  const payload = {
    title, content,
    description: desc || null,
    category_id: catId ? parseInt(catId) : null,
    tag_ids: state.selectedTagIds,
  };

  if (state.editingPrompt) {
    await patch(`/prompts/${state.editingPrompt.id}`, payload);
    toast("Prompt atualizado!");
  } else {
    await post("/prompts/", payload);
    toast("Prompt criado!");
  }

  closeModal("promptModal");
  await loadAll();
}

// ── Deletar ────────────────────────────────────────────────────────────────────
function confirmDelete(id, title) {
  if (!confirm(`Excluir o prompt "${title}"?`)) return;
  del(`/prompts/${id}`).then(() => { toast("Prompt excluído.", "error"); loadAll(); });
}

// ── Favoritar ──────────────────────────────────────────────────────────────────
async function toggleFav(id) {
  await post(`/prompts/${id}/favorite`);
  state.prompts = await buildPromptsQuery() || [];
  renderAll();
}
async function toggleFavDetail(id) {
  const p = await post(`/prompts/${id}/favorite`);
  document.getElementById("detailFav").textContent = p.is_favorite ? "⭐ Favorito" : "☆ Favoritar";
  state.prompts = await buildPromptsQuery() || [];
  renderAll();
}

// ── Tags picker ────────────────────────────────────────────────────────────────
function renderTagsPicker() {
  const container = document.getElementById("tagsPicker");
  container.innerHTML = state.tags.map(t => `
    <span class="tag ${state.selectedTagIds.includes(t.id) ? 'selected' : ''}"
      onclick="toggleTagSelect(${t.id}, this)">${esc(t.name)}</span>
  `).join("") || "<span style='color:var(--muted);font-size:12px'>Nenhuma tag criada ainda.</span>";
}

function toggleTagSelect(id, el) {
  const idx = state.selectedTagIds.indexOf(id);
  if (idx === -1) { state.selectedTagIds.push(id); el.classList.add("selected"); }
  else            { state.selectedTagIds.splice(idx, 1); el.classList.remove("selected"); }
}

// ── Category select ────────────────────────────────────────────────────────────
function populateCategorySelect() {
  const sel = document.getElementById("promptCategory");
  sel.innerHTML = `<option value="">Sem categoria</option>` +
    state.categories.map(c => `<option value="${c.id}" ${state.editingPrompt?.category_id === c.id ? 'selected' : ''}>${esc(c.name)}</option>`).join("");
}

// ── Modal Categorias ───────────────────────────────────────────────────────────
function openCategoriesModal() {
  renderCategoriesList();
  showModal("categoriesModal");
}

function renderCategoriesList() {
  const list = document.getElementById("categoriesList");
  list.innerHTML = state.categories.map(c => `
    <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:var(--surface2);border-radius:7px">
      <div><strong>${esc(c.name)}</strong>${c.description ? `<span style="color:var(--muted);font-size:12px;margin-left:8px">${esc(c.description)}</span>` : ''}</div>
      <button class="btn btn-sm btn-danger" onclick="deleteCategory(${c.id})">🗑️</button>
    </div>
  `).join("") || "<p style='color:var(--muted)'>Nenhuma categoria criada.</p>";
}

async function createCategory() {
  const name = document.getElementById("catName").value.trim();
  const desc = document.getElementById("catDesc").value.trim();
  if (!name) { toast("Nome obrigatório.", "error"); return; }
  await post("/categories/", { name, description: desc || null });
  document.getElementById("catName").value = "";
  document.getElementById("catDesc").value = "";
  state.categories = await get("/categories/") || [];
  renderCategoriesList();
  populateCategorySelect();
  toast("Categoria criada!");
}

async function deleteCategory(id) {
  if (!confirm("Excluir esta categoria?")) return;
  await del(`/categories/${id}`);
  state.categories = await get("/categories/") || [];
  renderCategoriesList();
  toast("Categoria removida.", "error");
}

// ── Modal Tags ─────────────────────────────────────────────────────────────────
function openTagsModal() {
  renderTagsList();
  showModal("tagsModal");
}

function renderTagsList() {
  const list = document.getElementById("tagsList");
  list.innerHTML = state.tags.map(t => `
    <div style="display:flex;align-items:center;justify-content:space-between;padding:6px 12px;background:var(--surface2);border-radius:7px">
      <span class="tag">${esc(t.name)}</span>
      <button class="btn btn-sm btn-danger" onclick="deleteTag(${t.id})">🗑️</button>
    </div>
  `).join("") || "<p style='color:var(--muted)'>Nenhuma tag criada.</p>";
}

async function createTag() {
  const name = document.getElementById("tagName").value.trim();
  if (!name) { toast("Nome obrigatório.", "error"); return; }
  await post("/tags/", { name });
  document.getElementById("tagName").value = "";
  state.tags = await get("/tags/") || [];
  renderTagsList();
  toast("Tag criada!");
}

async function deleteTag(id) {
  if (!confirm("Excluir esta tag?")) return;
  await del(`/tags/${id}`);
  state.tags = await get("/tags/") || [];
  renderTagsList();
  toast("Tag removida.", "error");
}

// ── Copy to clipboard ──────────────────────────────────────────────────────────
function copyContent() {
  const content = document.getElementById("detailContent").value;
  navigator.clipboard.writeText(content).then(() => toast("Copiado para a área de transferência!"));
}

// ── Modal helpers ──────────────────────────────────────────────────────────────
function showModal(id) {
  const modal = document.getElementById(id);
  modal.classList.remove("hidden");
  // Popula select de categoria no modal de criação/edição
  if (id === "promptModal") populateCategorySelect();
}
function closeModal(id) { document.getElementById(id).classList.add("hidden"); }

// Fecha ao clicar no overlay
document.querySelectorAll(".modal-overlay").forEach(overlay => {
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.classList.add("hidden");
  });
});

// ── Utilitários ───────────────────────────────────────────────────────────────
function esc(str) {
  if (!str) return "";
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function debounce(fn, ms) {
  let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// ── Gerador de Prompt com IA ──────────────────────────────────────────────────
function openGenerator() {
  // Limpa o resultado anterior
  document.getElementById("genObjetivo").value  = "";
  document.getElementById("genPublico").value   = "";
  document.getElementById("genTom").value       = "formal";
  document.getElementById("genFormato").value   = "texto corrido";
  document.getElementById("genContexto").value  = "";
  document.getElementById("genResultBox").style.display = "none";
  document.getElementById("genSaveBtn").style.display   = "none";
  document.getElementById("genResult").value    = "";
  document.getElementById("genTokens").textContent = "";
  showModal("generatorModal");
}

async function runGenerate() {
  const objetivo = document.getElementById("genObjetivo").value.trim();
  const publico  = document.getElementById("genPublico").value.trim();
  const tom      = document.getElementById("genTom").value;
  const formato  = document.getElementById("genFormato").value;
  const contexto = document.getElementById("genContexto").value.trim();

  if (!objetivo || !publico) {
    toast("Preencha o objetivo e o público-alvo.", "error");
    return;
  }

  const btn = document.getElementById("genBtn");
  btn.disabled = true;
  btn.textContent = "⏳ Gerando...";

  try {
    const data = await post("/generate/", { objetivo, publico, tom, formato, contexto: contexto || null });

    document.getElementById("genResult").value = data.prompt;
    document.getElementById("genTokens").textContent = `· ${data.tokens_usados} tokens`;
    document.getElementById("genResultBox").style.display = "block";
    document.getElementById("genSaveBtn").style.display   = "inline-flex";
  } finally {
    btn.disabled = false;
    btn.textContent = "✨ Gerar novamente";
  }
}

function copyGenerated() {
  const content = document.getElementById("genResult").value;
  navigator.clipboard.writeText(content).then(() => toast("Prompt copiado!"));
}

function saveGenerated() {
  const prompt = document.getElementById("genResult").value;
  const objetivo = document.getElementById("genObjetivo").value.trim();

  // Pré-preenche o modal de criação com o prompt gerado
  state.editingPrompt  = null;
  state.selectedTagIds = [];
  document.getElementById("modalTitle").textContent  = "Novo Prompt";
  document.getElementById("promptTitle").value       = objetivo;
  document.getElementById("promptContent").value     = prompt;
  document.getElementById("promptDesc").value        = "";
  document.getElementById("promptCategory").value    = "";
  renderTagsPicker();

  closeModal("generatorModal");
  showModal("promptModal");
}

// ── Init ───────────────────────────────────────────────────────────────────────
loadAll();
