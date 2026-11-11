const state = { apps: [] };
const $ = (id) => document.getElementById(id);

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
  $("apps").innerHTML = filtered.map((app) => {
    const downloads = Array.isArray(app.downloads) ? app.downloads : [];
    const links = downloads.map((asset) => `
      <a class="download" href="${safeUrl(asset.url)}" target="_blank" rel="noopener noreferrer">
        ${escapeHtml(asset.name)} <span aria-hidden="true">↗</span>
      </a>`).join("");
    return `
      <article class="app-card">
        <div class="card-top"><span class="app-icon" aria-hidden="true">${escapeHtml(app.emoji)}</span><span class="platform">${escapeHtml(app.platform)}</span></div>
        <h2>${escapeHtml(app.name)}</h2>
        <p class="description">${escapeHtml(app.description || "No description available.")}</p>
        <div class="meta"><span>${escapeHtml(app.category)}</span><strong>${escapeHtml(app.version)}</strong></div>
        <div class="downloads">${links || '<span class="download unavailable">Not published yet</span>'}</div>
      </article>`;
  }).join("");
  $("apps").setAttribute("aria-busy", "false");
  $("message").textContent = filtered.length ? "" : "No applications match your filters.";
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}

function safeUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && url.hostname === "github.com" && url.pathname.includes("/releases/download/")
      ? escapeHtml(url.href)
      : "#";
  } catch {
    return "#";
  }
}

async function init() {
  try {
    const response = await fetch("data/apps.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Catalog request failed (${response.status})`);
    state.apps = await response.json();
    if (!Array.isArray(state.apps)) throw new Error("Catalog format is invalid");

    const categories = [...new Set(state.apps.map((app) => app.category))].sort();
    for (const item of categories) $("category").add(new Option(item, item));

    const platforms = [...new Set(state.apps.map((app) => app.platform))].sort();
    for (const item of platforms) {
      $("platform").add(new Option(item, item));
      const count = new Set(state.apps.filter((app) => app.platform === item).map((app) => app.name)).size;
      const stat = document.createElement("div");
      const total = document.createElement("strong");
      const label = document.createElement("span");
      total.textContent = count;
      label.textContent = item;
      stat.append(total, label);
      $("platform-stats").append(stat);
    }

    $("total-count").textContent = new Set(state.apps.map((app) => app.name)).size;
    render();
  } catch (error) {
    $("apps").setAttribute("aria-busy", "false");
    $("results-count").textContent = "Catalog unavailable";
    $("message").textContent = `${error.message}. Please try again later.`;
  }
}

for (const id of ["search", "category", "platform"]) {
  $(id).addEventListener(id === "search" ? "input" : "change", render);
}
init();
