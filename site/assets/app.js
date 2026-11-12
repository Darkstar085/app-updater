const state = { apps: [], category: "all", platforms: new Set() };
const $ = (id) => document.getElementById(id);
const PLATFORM_ICONS = {
 Android:'<svg viewBox="0 0 32 32" aria-hidden="true"><path fill="#8de45c" d="M8 11 6 7a.8.8 0 0 1 1.4-.8l2.3 4a13 13 0 0 1 12.6 0l2.3-4A.8.8 0 0 1 26 7l-2 4a10 10 0 0 1 5 9H3a10 10 0 0 1 5-9Zm0 11h16v3a2 2 0 0 1-2 2h-1v3a1.5 1.5 0 0 1-3 0v-3h-2v3a1.5 1.5 0 0 1-3 0v-3h-1a2 2 0 0 1-2-2Z"/></svg>',
 Linux:'<svg viewBox="0 0 32 32" aria-hidden="true"><path fill="#f3f5ff" d="M16 3c-5 0-7 5-7 10 0 3-3 6-3 10 0 3 3 5 7 4l3-2 3 2c4 1 7-1 7-4 0-4-3-7-3-10 0-5-2-10-7-10Z"/><path fill="#252b42" d="M11 13c1-2 3-2 5-1 2-1 4-1 5 1l-1 4-4 2-4-2Z"/><path fill="#f3b84d" d="m16 17 3 3-3 2-3-2Z"/></svg>',
 Windows:'<svg viewBox="0 0 32 32" aria-hidden="true"><path fill="#28a9f4" d="M3 6.5 14 5v10H3Zm13-1.8L29 3v12H16ZM3 17h11v10L3 25.5Zm13 0h13v12l-13-1.8Z"/></svg>',
 iOS:'<svg viewBox="0 0 32 32" aria-hidden="true"><path fill="#d77bfa" d="M22.7 17.1c0-3 2.4-4.5 2.5-4.6a5.4 5.4 0 0 0-4.3-2.3c-1.8-.2-3.5 1-4.4 1-.9 0-2.3-1-3.8-1a5.7 5.7 0 0 0-4.8 2.9c-2.1 3.6-.5 8.8 1.5 11.7 1 1.4 2.1 3 3.6 2.9 1.4-.1 2-1 3.8-1s2.3 1 3.8 1c1.6 0 2.5-1.4 3.5-2.8a12 12 0 0 0 1.6-3.3 5.1 5.1 0 0 1-3-4.5ZM19.8 8.3A5.3 5.3 0 0 0 21 4.5a5.5 5.5 0 0 0-3.5 1.8 5 5 0 0 0-1.2 3.6 4.6 4.6 0 0 0 3.5-1.6Z"/></svg>',
 macOS:'<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="3" y="4" width="26" height="24" rx="6" fill="#a9d7ff"/><path fill="#eaf6ff" d="M16 4h7a6 6 0 0 1 6 6v12a6 6 0 0 1-6 6h-7Z"/><path fill="#4386c9" d="M3 16h13v12H9a6 6 0 0 1-6-6Z"/><path fill="#fff" d="M10 10h2v2h-2Zm10 0h2v2h-2Zm-8 5h8v2h-8Zm-1 6h10v2H11Z"/></svg>'
};
const CATEGORY_ICONS = { Development:"⌘",Utilities:"◈",Downloads:"⇩","File sharing":"⇄",Security:"⬡",Browsers:"◎",Communication:"◌",Weather:"☼",Maps:"⌖",Photos:"▧",Personalization:"✧",Music:"♫",Productivity:"✎",Audio:"◖",Video:"▷",System:"⚙" };
const platformIcon = (name) => PLATFORM_ICONS[name] || '<span class="generic-platform-icon">▣</span>';

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}

function safeUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && url.hostname === "github.com" && url.pathname.includes("/releases/download/")
      ? url.href : "#";
  } catch { return "#"; }
}

function render() {
  const query = $("search").value.trim().toLocaleLowerCase();
  const filtered = state.apps.filter((app) => {
    const text = `${app.name} ${app.description} ${app.repository}`.toLocaleLowerCase();
    return (!query || text.includes(query))
      && (state.category === "all" || app.category === state.category)
      && (!state.platforms.size || state.platforms.has(app.platform));
  });
  $("results-count").textContent = `${filtered.length} of ${state.apps.length} app/platform entries`;
  $("catalog-total").textContent = filtered.length;
  $("apps").innerHTML = filtered.map((app, index) => `
    <article class="app-card" data-app-index="${state.apps.indexOf(app)}" tabindex="0" role="button" aria-label="View ${escapeHtml(app.name)} details" style="--card-index:${Math.min(index, 11)}">
      <div class="card-glow"></div><div class="card-top"><span class="app-icon" aria-hidden="true">${escapeHtml(app.emoji || "📦")}</span><span class="platform">${platformIcon(app.platform)} ${escapeHtml(app.platform)}</span></div>
      <div class="card-title-row"><h3>${escapeHtml(app.name)}</h3><span class="card-arrow" aria-hidden="true"></span></div>
      <p class="description">${escapeHtml(app.description || "No description available.")}</p>
      <div class="card-bottom"><span class="category-tag">${escapeHtml(app.category || "Other")}</span><span class="version-tag">v${escapeHtml(app.version || "—")}</span></div>
      <div class="card-hint"><span>View details & downloads</span><span aria-hidden="true">→</span></div>
    </article>`).join("");
  $("apps").setAttribute("aria-busy", "false");
  $("message").textContent = filtered.length ? "" : "No applications match your filters. Try another search.";
  updateFilterLabels();
}
function updateFilterLabels() {
  $("category-filter").querySelector(".filter-trigger-label").textContent = state.category === "all" ? "All categories" : state.category;
  const count = state.platforms.size;
  $("platform-filter").querySelector(".filter-trigger-label").textContent = count ? `${count} platform${count === 1 ? "" : "s"}` : "All platforms";
  $("platform-selected-count").textContent = count ? `${count} selected` : "All selected";
}
function renderFilterOptions() {
  const categories = [...new Set(state.apps.map((app) => app.category || "Other"))].sort();
  const platforms = [...new Set(state.apps.map((app) => app.platform))].sort();
  $("category-options").innerHTML = [
    `<button class="filter-option ${state.category === "all" ? "selected" : ""}" type="button" role="option" aria-selected="${state.category === "all"}" data-category="all"><span class="option-icon">▦</span><span>All categories</span><span class="option-check">✓</span></button>`,
    ...categories.map((category) => `<button class="filter-option ${state.category === category ? "selected" : ""}" type="button" role="option" aria-selected="${state.category === category}" data-category="${escapeHtml(category)}"><span class="option-icon">${CATEGORY_ICONS[category] || "◈"}</span><span>${escapeHtml(category)}</span><span class="option-check">✓</span></button>`)
  ].join("");
  $("platform-options").innerHTML = platforms.map((platform) => `<label class="platform-option"><input type="checkbox" value="${escapeHtml(platform)}" ${state.platforms.has(platform) ? "checked" : ""}><span class="platform-option-icon">${platformIcon(platform)}</span><span class="platform-option-name">${escapeHtml(platform)}</span><span class="custom-check" aria-hidden="true">✓</span></label>`).join("");
  updateFilterLabels();
}
function setDropdown(id, open) {
  const root = $(id), trigger = root.querySelector(".filter-trigger"), menu = root.querySelector(".filter-menu");
  menu.hidden = !open; trigger.setAttribute("aria-expanded", String(open)); root.classList.toggle("is-open", open);
  if (open && id === "category-filter") $("category-search").focus();
}
function closeDropdowns(except = "") {
  for (const id of ["category-filter", "platform-filter"]) if (id !== except) setDropdown(id, false);
}
function initFilters() {
  for (const id of ["category-filter", "platform-filter"]) {
    $(id).querySelector(".filter-trigger").addEventListener("click", () => {
      const open = $(id).querySelector(".filter-trigger").getAttribute("aria-expanded") === "true";
      closeDropdowns(id); setDropdown(id, !open);
    });
  }
  $("category-options").addEventListener("click", (event) => {
    const option = event.target.closest("[data-category]"); if (!option) return;
    state.category = option.dataset.category; renderFilterOptions(); render(); setDropdown("category-filter", false);
  });
  $("category-search").addEventListener("input", (event) => {
    const query = event.target.value.trim().toLocaleLowerCase();
    $("category-options").querySelectorAll("[data-category]").forEach((option) => {
      option.hidden = !option.textContent.toLocaleLowerCase().includes(query);
    });
  });
  $("platform-options").addEventListener("change", (event) => {
    const input = event.target.closest('input[type="checkbox"]'); if (!input) return;
    if (input.checked) state.platforms.add(input.value); else state.platforms.delete(input.value);
    updateFilterLabels(); render();
  });
  $("reset-filters").addEventListener("click", () => {
    state.category = "all"; state.platforms.clear(); $("search").value = ""; $("category-search").value = "";
    renderFilterOptions(); render(); closeDropdowns();
  });
  document.addEventListener("click", (event) => { if (!event.target.closest(".filter-dropdown")) closeDropdowns(); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeDropdowns(); });
}

function openDetails(app) {
  if (!app) return;
  const downloads = Array.isArray(app.downloads) ? app.downloads : [];
  const repository = typeof app.repository === "string" && /^[\w.-]+\/[\w.-]+$/.test(app.repository) ? app.repository : "";
  $("dialog-content").innerHTML = `
    <div class="dialog-kicker">${platformIcon(app.platform)} ${escapeHtml(app.platform)} · ${escapeHtml(app.category || "Other")}</div>
    <div class="dialog-app-icon">${escapeHtml(app.emoji || "📦")}</div><h2 id="dialog-title">${escapeHtml(app.name)}</h2>
    <p class="dialog-description">${escapeHtml(app.description || "No description available.")}</p>
    <div class="dialog-meta"><span>Latest version</span><strong>v${escapeHtml(app.version || "—")}</strong></div>
    <div class="dialog-download-heading"><h3>Available downloads</h3><span>${downloads.length} files</span></div>
    <div class="dialog-downloads">${downloads.map((asset) => {
      const url = safeUrl(asset.url);
      return url === "#" ? `<span class="dialog-download unavailable">${escapeHtml(asset.name)} <small>Unavailable</small></span>`
        : `<a class="dialog-download" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer"><span>⇩</span><span class="dialog-file-name">${escapeHtml(asset.name)}</span></a>`;
    }).join("") || '<p class="dialog-empty">No published downloads for this platform yet.</p>'}</div>
    ${repository ? `<a class="source-link" href="https://github.com/${escapeHtml(repository)}" target="_blank" rel="noopener noreferrer">View source repository</a>` : ""}`;
  if (!$("app-dialog").open) $("app-dialog").showModal();
}

function initInteractions() {
  const cards = $("apps");
  cards.addEventListener("click", (event) => {
    if (event.target.closest("a")) return;
    const card = event.target.closest(".app-card");
    if (card) openDetails(state.apps[Number(card.dataset.appIndex)]);
  });
  cards.addEventListener("keydown", (event) => {
    if ((event.key !== "Enter" && event.key !== " ") || !event.target.matches(".app-card")) return;
    event.preventDefault();
    openDetails(state.apps[Number(event.target.dataset.appIndex)]);
  });
  const dialog = $("app-dialog");
  document.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) {
      event.preventDefault(); $("search").focus();
    }
  });
  if (matchMedia("(hover: hover) and (pointer: fine)").matches && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    cards.addEventListener("pointermove", (event) => {
      const card = event.target.closest(".app-card");
      if (!card) return;
      const rect = card.getBoundingClientRect(), x = event.clientX - rect.left, y = event.clientY - rect.top;
      card.style.setProperty("--pointer-x", `${x}px`);
      card.style.setProperty("--pointer-y", `${y}px`);
      card.style.setProperty("--tilt-y", `${(((x / rect.width) - .5) * 5).toFixed(2)}deg`);
      card.style.setProperty("--tilt-x", `${(((.5 - y / rect.height)) * 5).toFixed(2)}deg`);
    });
    cards.addEventListener("pointerout", (event) => {
      const card = event.target.closest(".app-card");
      if (card && !card.contains(event.relatedTarget)) {
        card.style.setProperty("--tilt-x", "0deg"); card.style.setProperty("--tilt-y", "0deg");
      }
    });
  }
  const themeToggle = $("theme-toggle");
  try {
    const stored = localStorage.getItem("theme");
    if (stored === "light" || stored === "dark") document.documentElement.dataset.theme = stored;
  } catch { /* Storage may be unavailable. */ }
  const syncThemeButton = () => {
    const light = document.documentElement.dataset.theme === "light";
    themeToggle.textContent = light ? "☾" : "☼";
    themeToggle.setAttribute("aria-label", light ? "Switch to dark theme" : "Switch to light theme");
  };
  syncThemeButton();
  themeToggle.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch { /* Theme remains active for this view. */ }
    syncThemeButton();
  });
}

async function init() {
  try {
    const response = await fetch("data/apps.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Catalog request failed (${response.status})`);
    state.apps = await response.json();
    if (!Array.isArray(state.apps)) throw new Error("Catalog format is invalid");
    for (const item of [...new Set(state.apps.map((app) => app.category))].sort()) $("category").add(new Option(item, item));
    const platformOrder = ["Android", "Linux", "Windows", "iOS", "macOS"];
    for (const item of [...new Set(state.apps.map((app) => app.platform))].sort((a, b) => platformOrder.indexOf(a) - platformOrder.indexOf(b))) {
      const count = new Set(state.apps.filter((app) => app.platform === item).map((app) => app.name)).size;
      const stat = document.createElement("div"); stat.className = "platform-stat-item";
      stat.innerHTML = `<span class="p-icon">${platformIcon(item)}</span><div class="p-info"><strong>${count}</strong><span>${escapeHtml(item)}</span></div>`;
      $("platform-stats").append(stat);
    }
    renderFilterOptions(); initFilters();
    $("total-count").textContent = new Set(state.apps.map((app) => app.name)).size;
    render();
  } catch (error) {
    $("apps").setAttribute("aria-busy", "false"); $("results-count").textContent = "Catalog unavailable";
    $("message").textContent = `${error.message}. Please try again later.`;
  }
}
$("search").addEventListener("input", render);
initInteractions();
init();
