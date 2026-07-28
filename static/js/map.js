(() => {
  "use strict";

  const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  });
  const imagery = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    maxZoom: 19,
    attribution: "Tiles &copy; Esri",
  });
  const map = L.map("map", { zoomControl: false, layers: [osm] }).setView([-3.47, 26.17], 4);
  const layerControl = L.control.layers({ "OpenStreetMap": osm, "World Imagery": imagery }, {}, { collapsed: false }).addTo(map);
  L.control.zoom({ position: "bottomright" }).addTo(map);
  L.control.scale({ imperial: false }).addTo(map);

  const panel = document.querySelector("#layer-panel");
  const openButton = document.querySelector("#panel-open");
  const closeButton = document.querySelector("#panel-close");
  const projectList = document.querySelector("#project-list");
  const loadMoreButton = document.querySelector("#load-more");
  const status = document.querySelector("#map-status");
  const projectLayers = new Map();
  const referenceLayers = new Map();
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
    return String(value ?? "—").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }
  function popupHtml(properties) {
    const entries = Object.entries(properties || {});
    if (!entries.length) return '<p class="text-sm">No attributes available.</p>';
    return `<table class="attribute-table text-sm"><tbody>${entries.map(([key, value]) => `<tr><td>${escapeHtml(key.replace(/_/g, " "))}</td><td>${escapeHtml(typeof value === "object" ? JSON.stringify(value) : value)}</td></tr>`).join("")}</tbody></table>`;
  }
  function layerStyle() { return { color: "#047857", weight: 2, fillColor: "#34d399", fillOpacity: 0.28 }; }
  function pointStyle(feature, latlng) { return L.circleMarker(latlng, { radius: 7, color: "#065f46", weight: 2, fillColor: "#34d399", fillOpacity: 0.9 }); }
  function makeGeoJson(geojson) {
    return L.geoJSON(geojson, { style: layerStyle, pointToLayer: pointStyle, onEachFeature(feature, featureLayer) { featureLayer.bindPopup(popupHtml(feature.properties)); } });
  }
  async function fetchGeojson(url) {
    const response = await fetch(url, { headers: { Accept: "application/geo+json, application/json" } });
    if (!response.ok) throw new Error(`The server returned ${response.status}.`);
    return response.json();
  }
  function fitLayer(layer) {
    const bounds = layer.getBounds();
    if (bounds.isValid()) map.fitBounds(bounds, { padding: [32, 32], maxZoom: 15 });
  }

  async function toggleProjectLayer(input) {
    const id = input.value;
    const name = input.dataset.layerName;
    if (!input.checked) {
      const existing = projectLayers.get(id);
      if (existing) map.removeLayer(existing);
      status.textContent = `${name} removed.`;
      return;
    }
    const existing = projectLayers.get(id);
    if (existing) {
      existing.addTo(map);
      fitLayer(existing);
      return;
    }
    input.disabled = true;
    status.textContent = `Loading ${name}…`;
    try {
      const geojson = await fetchGeojson(input.dataset.geojsonUrl);
      const layer = makeGeoJson(geojson).addTo(map);
      projectLayers.set(id, layer);
      fitLayer(layer);
      status.textContent = `${geojson.features.length.toLocaleString()} features in ${name}`;
    } catch (error) {
      input.checked = false;
      status.textContent = `Could not load ${name}: ${error.message}`;
    } finally { input.disabled = false; }
  }

  function appendProject(project) {
    const section = document.createElement("section");
    section.className = "mb-2 overflow-hidden rounded-xl border border-slate-200 bg-white";
    const layers = project.layers || [];
    section.innerHTML = `<div class="px-4 py-3"><h2 class="text-sm font-semibold text-slate-800">${escapeHtml(project.name)}</h2><p class="mt-0.5 text-xs text-slate-500">${escapeHtml(project.sigle)} · ${layers.length} layer${layers.length === 1 ? "" : "s"}</p></div><div class="border-t border-slate-100 px-3 py-2">${layers.length ? "" : '<p class="px-1 py-2 text-xs text-slate-500">No layers in this project.</p>'}</div>`;
    const layerContainer = section.lastElementChild;
    layers.forEach((layer) => {
      const label = document.createElement("label");
      label.className = "flex cursor-pointer items-center gap-3 rounded-lg px-2 py-2 text-sm hover:bg-emerald-50";
      label.innerHTML = `<input class="h-4 w-4 rounded accent-emerald-700" type="checkbox" value="${layer.id}"><span class="min-w-0 flex-1 truncate text-slate-700">${escapeHtml(layer.name)}</span><span class="text-xs text-slate-400">${Number(layer.feature_count).toLocaleString()}</span>`;
      const input = label.querySelector("input");
      input.dataset.geojsonUrl = layer.geojson_url;
      input.dataset.layerName = layer.name;
      input.addEventListener("change", () => toggleProjectLayer(input));
      layerContainer.appendChild(label);
    });
    projectList.appendChild(section);
  }

  async function fetchAllPages(url) {
    const results = [];
    while (url) {
      const response = await fetch(url, { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`The server returned ${response.status}.`);
      const page = await response.json();
      results.push(...page.results);
      url = page.next;
    }
    return results;
  }
  async function addReferenceLayers() {
    try {
      const layers = await fetchAllPages(window.GIS_API.unassignedLayers);
      layers.forEach((layer) => {
        const placeholder = L.layerGroup();
        referenceLayers.set(placeholder, { ...layer, loaded: false });
        layerControl.addOverlay(placeholder, layer.name);
      });
    } catch (error) { status.textContent = `Could not load reference layers: ${error.message}`; }
  }
  map.on("overlayadd", async ({ layer }) => {
    const entry = referenceLayers.get(layer);
    if (!entry || entry.loaded) return;
    status.textContent = `Loading ${entry.name}…`;
    try {
      const geojson = await fetchGeojson(entry.geojson_url);
      makeGeoJson(geojson).addTo(layer);
      entry.loaded = true;
      fitLayer(layer);
      status.textContent = `${entry.name} added.`;
    } catch (error) {
      map.removeLayer(layer);
      status.textContent = `Could not load ${entry.name}: ${error.message}`;
    }
  });

  async function loadProjects() {
    if (!nextProjectsUrl) return;
    loadMoreButton.disabled = true;
    try {
      const page = await fetch(nextProjectsUrl, { headers: { Accept: "application/json" } }).then((response) => { if (!response.ok) throw new Error(`The server returned ${response.status}.`); return response.json(); });
      page.results.forEach(appendProject);
      nextProjectsUrl = page.next;
      loadMoreButton.classList.toggle("hidden", !nextProjectsUrl);
      status.textContent = projectList.children.length ? "Select one or more project layers." : "No projects available.";
    } catch (error) {
      projectList.innerHTML = `<p class="p-3 text-sm text-red-700">Could not load projects: ${escapeHtml(error.message)}</p>`;
    } finally { loadMoreButton.disabled = false; }
  }
  loadMoreButton.addEventListener("click", loadProjects);
  addReferenceLayers();
  loadProjects();
})();
