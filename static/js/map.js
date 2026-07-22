(() => {
  "use strict";

  const map = L.map("map", { zoomControl: false }).setView([-3.47, 26.17], 4);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  L.control.zoom({ position: "bottomright" }).addTo(map);
  L.control.scale({ imperial: false }).addTo(map);

  const panel = document.querySelector("#layer-panel");
  const openButton = document.querySelector("#panel-open");
  const closeButton = document.querySelector("#panel-close");
  const projectList = document.querySelector("#project-list");
  const loadMoreButton = document.querySelector("#load-more");
  const status = document.querySelector("#map-status");
  let activeLayer = null;
  let nextProjectsUrl = window.GIS_API.projects;

  function setPanel(open) {
    panel.classList.toggle("-translate-x-[calc(100%+2rem)]", !open);
    openButton.classList.toggle("hidden", open);
    openButton.classList.toggle("flex", !open);
    openButton.setAttribute("aria-expanded", String(open));
    window.setTimeout(() => map.invalidateSize(), 320);
  }

  closeButton.addEventListener("click", () => setPanel(false));
  openButton.addEventListener("click", () => setPanel(true));

  function escapeHtml(value) {
    return String(value ?? "—")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function popupHtml(properties) {
    const entries = Object.entries(properties || {});
    if (!entries.length) return '<p class="text-sm">No attributes available.</p>';
    return `<table class="attribute-table text-sm"><tbody>${entries.map(([key, value]) =>
      `<tr><td>${escapeHtml(key.replace(/_/g, " "))}</td><td>${escapeHtml(
        typeof value === "object" ? JSON.stringify(value) : value,
      )}</td></tr>`,
    ).join("")}</tbody></table>`;
  }

  function layerStyle(feature) {
    return { color: "#047857", weight: 2, fillColor: "#34d399", fillOpacity: 0.28 };
  }

  function pointStyle(feature, latlng) {
    return L.circleMarker(latlng, { radius: 7, color: "#065f46", weight: 2, fillColor: "#34d399", fillOpacity: 0.9 });
  }

  async function showLayer(input) {
    const url = input.dataset.geojsonUrl;
    const name = input.dataset.layerName;
    status.textContent = `Loading ${name}…`;
    document.querySelectorAll("input[name='gis-layer']").forEach((radio) => { radio.disabled = true; });
    try {
      const response = await fetch(url, { headers: { Accept: "application/geo+json, application/json" } });
      if (!response.ok) throw new Error(`The server returned ${response.status}.`);
      const geojson = await response.json();
      if (activeLayer) map.removeLayer(activeLayer);
      activeLayer = L.geoJSON(geojson, {
        style: layerStyle,
        pointToLayer: pointStyle,
        onEachFeature(feature, leafletLayer) { leafletLayer.bindPopup(popupHtml(feature.properties)); },
      }).addTo(map);
      const bounds = activeLayer.getBounds();
      if (bounds.isValid()) map.fitBounds(bounds, { padding: [32, 32], maxZoom: 15 });
      status.textContent = `${geojson.features.length.toLocaleString()} features in ${name}`;
    } catch (error) {
      input.checked = false;
      status.textContent = `Could not load ${name}: ${error.message}`;
    } finally {
      document.querySelectorAll("input[name='gis-layer']").forEach((radio) => { radio.disabled = false; });
    }
  }

  function appendProject(project) {
    const section = document.createElement("section");
    section.className = "mb-2 overflow-hidden rounded-xl border border-slate-200 bg-white";
    const layers = project.layers || [];
    section.innerHTML = `
      <div class="px-4 py-3">
        <h2 class="text-sm font-semibold text-slate-800">${escapeHtml(project.name)}</h2>
        <p class="mt-0.5 text-xs text-slate-500">${escapeHtml(project.sigle)} · ${layers.length} layer${layers.length === 1 ? "" : "s"}</p>
      </div>
      <div class="border-t border-slate-100 px-3 py-2">${layers.length ? "" : '<p class="px-1 py-2 text-xs text-slate-500">No layers in this project.</p>'}</div>`;
    const layerContainer = section.lastElementChild;
    layers.forEach((layer) => {
      const label = document.createElement("label");
      label.className = "flex cursor-pointer items-center gap-3 rounded-lg px-2 py-2 text-sm hover:bg-emerald-50";
      label.innerHTML = `<input class="h-4 w-4 accent-emerald-700" type="radio" name="gis-layer" value="${layer.id}"><span class="min-w-0 flex-1 truncate text-slate-700">${escapeHtml(layer.name)}</span><span class="text-xs text-slate-400">${Number(layer.feature_count).toLocaleString()}</span>`;
      const input = label.querySelector("input");
      input.dataset.geojsonUrl = layer.geojson_url;
      input.dataset.layerName = layer.name;
      input.addEventListener("change", () => { if (input.checked) showLayer(input); });
      layerContainer.appendChild(label);
    });
    projectList.appendChild(section);
  }

  async function loadProjects() {
    if (!nextProjectsUrl) return;
    loadMoreButton.disabled = true;
    try {
      const response = await fetch(nextProjectsUrl, { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`The server returned ${response.status}.`);
      const page = await response.json();
      page.results.forEach(appendProject);
      nextProjectsUrl = page.next;
      loadMoreButton.classList.toggle("hidden", !nextProjectsUrl);
      status.textContent = projectList.children.length ? "Choose a layer to begin." : "No projects available.";
    } catch (error) {
      projectList.innerHTML = `<p class="p-3 text-sm text-red-700">Could not load projects: ${escapeHtml(error.message)}</p>`;
      status.textContent = "";
    } finally {
      loadMoreButton.disabled = false;
    }
  }

  loadMoreButton.addEventListener("click", loadProjects);
  loadProjects();
})();
