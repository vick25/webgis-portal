var osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
});

var Esri_WorldImagery = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    attribution:
      "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
  },
);

var bounds = L.latLngBounds([
  [7.176292, 37.941236],
  [-15.126043, 6.607253],
]);

var map = L.map("map", {
  zoomControl: false,
  layers: [osm],
  minZoom: 4,
  maxBounds: bounds,
  maxBoundsViscosity: 1.0,
}).setView([-3.47, 26.177], 5);

var baseMaps = {
  OpenStreetMap: osm,
  "World Imagery": Esri_WorldImagery,
};

var layerControl = L.control
  .layers(baseMaps, null, {
    collapsed: false,
  })
  .addTo(map);

var scale = L.control
  .scale({
    metric: true,
    imperial: false,
  })
  .addTo(map);
L.control.zoom({ position: "bottomright" }).addTo(map);

function renderProperties(properties) {
  // Convert object to key-value pairs and map over them
  const rowsHtml = Object.entries(properties)
    .map(([key, value]) => {
      // Optional: Format key/value into something cleaner
      const cleanKey = key.replace(/_/g, " ");
      const cleanValue =
        typeof value === "number" ? value.toLocaleString() : value;

      return `
        <tr>
          <td><strong>${cleanKey}</strong></td>
          <td>${cleanValue ?? "N/A"}</td>
        </tr>
      `;
    })
    .join("");

  return `
    <table class="properties-table">
      <tbody>
        ${rowsHtml}
      </tbody>
    </table>
  `;
}
async function fetchData(url) {
  const response = await fetch(url);

  if (!response.ok) {
    const message = `An error has occured: ${response.status}`;
    throw new Error(message);
  }

  const data = await response.json();
  return data.results;
}

fetchData("").catch((error) => {
  error.message; // 'An error has occurred: 404'
});

(async () => {
  const shps_data = await fetchData("api/v1/features/");

  const geojson = L.geoJSON(shps_data, {
    style: function (feature) {
      return { color: "blue", weight: 2, fillOpacity: 0.5 };
    },
    onEachFeature: function (feature, layer) {
      feature.properties &&
        layer.bindPopup(renderProperties(feature.properties.properties));
    },
    filter: function (feature, layer) {
      // Filter features based on a specific property value
      return (
        feature.properties && feature.properties.geoshp === "Territoire_RDC" //'Territoire_RDC'
      );
    },
  }).addTo(map);
})();
