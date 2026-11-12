const state = { apps: [] };
const $ = (id) => document.getElementById(id);
const PLATFORM_ICONS = { Android: "🤖", Linux: "🐧", Windows: "🪟", iOS: "🍎", macOS: "💻" };

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
  const category = $("category").value;
  const platform = $("platform").value;
  const filtered = state.apps.filter((app) => {
    const text = `${app.name} ${app.description} ${app.repository}`.toLocaleLowerCase();
    return (!query || text.includes(query))
      && (category === "all" || app.category === category)
      && (platform === "all" || app.platform === platform);
  });
  $("results-count").textContent = `${filtered.length} of ${state.apps.length} app/platform entries`;
  $("catalog-total").textContent = filtered.length;
  $("apps").innerHTML = filtered.map((app, index) => `
    <article class="app-card" data-app-index="${state.apps.indexOf(app)}" tabindex="0" role="button" aria-label="View ${escapeHtml(app.name)} details" style="--card-index:${Math.min(index, 11)}">
      <div class="card-glow"></div><div class="card-top"><span class="app-icon" aria-hidden="true">${escapeHtml(app.emoji || "📦")}</span><span class="platform">${PLATFORM_ICONS[app.platform] || "📦"} ${escapeHtml(app.platform)}</span></div>
      <div class="card-title-row"><h3>${escapeHtml(app.name)}</h3><span class="card-arrow" aria-hidden="true"></span></div>
      <p class="description">${escapeHtml(app.description || "No description available.")}</p>
      <div class="card-bottom"><span class="category-tag">${escapeHtml(app.category || "Other")}</span><span class="version-tag">v${escapeHtml(app.version || "—")}</span></div>
      <div class="card-hint"><span>View details & downloads</span><span aria-hidden="true">→</span></div>
    </article>`).join("");
  $("apps").setAttribute("aria-busy", "false");
  $("message").textContent = filtered.length ? "" : "No applications match your filters. Try another search.";
}

function openDetails(app) {
  if (!app) return;
  const downloads = Array.isArray(app.downloads) ? app.downloads : [];
  const repository = typeof app.repository === "string" && /^[\w.-]+\/[\w.-]+$/.test(app.repository) ? app.repository : "";
  $("dialog-content").innerHTML = `
    <div class="dialog-kicker">${PLATFORM_ICONS[app.platform] || "📦"} ${escapeHtml(app.platform)} · ${escapeHtml(app.category || "Other")}</div>
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
    for (const item of [...new Set(state.apps.map((app) => app.platform))].sort()) {
      $("platform").add(new Option(`${PLATFORM_ICONS[item] || "💻"} ${item}`, item));
      const count = new Set(state.apps.filter((app) => app.platform === item).map((app) => app.name)).size;
      const stat = document.createElement("div"), icon = document.createElement("span"), info = document.createElement("div");
      const total = document.createElement("strong"), label = document.createElement("span");
      stat.className = "platform-stat-item"; icon.className = "p-icon"; icon.setAttribute("aria-hidden", "true");
      icon.textContent = PLATFORM_ICONS[item] || "📦"; info.className = "p-info"; total.textContent = count; label.textContent = item;
      info.append(total, label); stat.append(icon, info); $("platform-stats").append(stat);
    }
    $("total-count").textContent = new Set(state.apps.map((app) => app.name)).size;
    render();
  } catch (error) {
    $("apps").setAttribute("aria-busy", "false"); $("results-count").textContent = "Catalog unavailable";
    $("message").textContent = `${error.message}. Please try again later.`;
  }
}
for (const id of ["search", "category", "platform"]) $(id).addEventListener(id === "search" ? "input" : "change", render);
initInteractions();
init();
