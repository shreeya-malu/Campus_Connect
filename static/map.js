const map = L.map('map').setView([18.48636, 73.81600], 18);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    
    const cumminsGeoJson = {
      "type": "Polygon",
        "coordinates": [
          [
            [
              73.8164168,
              18.4853467
            ],
            [
              73.8167004,
              18.4856872
            ],
            [
              73.8168962,
              18.4857316
            ],
            [
              73.8166861,
              18.4867995
            ],
            [
              73.8155602,
              18.4865789
            ],
            [
              73.8156214,
              18.4860528
            ],
            [
              73.8158294,
              18.4858168
            ],
            [
              73.8159865,
              18.4856717
            ],
            [
              73.816168,
              18.4855769
            ],
            [
              73.8162985,
              18.4853989
            ],
            [
              73.8164168,
              18.4853467
            ]
          ]
        ]
    };

    // 💡 Convert to Leaflet format (lat, lng)
    const cumminsLatLng = cumminsGeoJson.coordinates[0].map(coord => [coord[1], coord[0]]);

    // 🎯 Add Cummins boundary polygon
    const boundaryPolygon = L.polygon(cumminsLatLng, {
      color: 'blue',
      fillColor: 'green',
      fillOpacity: 0.1,
      weight: 2
    }).addTo(map);

    // 📍 Fit to view
    const bounds = boundaryPolygon.getBounds();
    map.fitBounds(bounds);
    map.setMaxBounds(bounds);
    map.on('drag', function () {
      map.panInsideBounds(bounds, { animate: true });
    });

    boundaryPolygon.bindPopup("<b>Cummins College of Engineering for Women</b>");

    // 🖤 Mask area outside the campus
    const world = [
      [-90, -180],
      [-90, 180],
      [90, 180],
      [90, -180],
      [-90, -180]
    ];

    const mask = L.polygon([world, cumminsLatLng], {
      stroke: false,
      color: '#000',
      fillColor: '#000',
      fillOpacity: 0.7
    }).addTo(map);

  fetch('/get-events')
  .then(response => response.json())
  .then(buildings => {
    let currentIndex = 0;
    let popupMarkers = [];

    buildings.forEach(building => {
      const marker = L.marker(building.coord).addTo(map);
      const popupContent = `
        <div class="popup-tile">
          <h3>${building.name}</h3>
          <ul>
            ${building.events.map(event => `<li>${event}</li>`).join('')}
          </ul>
        </div>
      `;
      marker.bindPopup(popupContent);
      marker.bindTooltip(building.name, {
        permanent: true,
        direction: 'top',
        className: 'building-label'
      });
      popupMarkers.push(marker);
    });

    // Cycle through popups
    function rotatePopups() {
      popupMarkers.forEach(marker => marker.closePopup());
      const marker = popupMarkers[currentIndex];
      marker.openPopup();
      map.panTo(marker.getLatLng());
      currentIndex = (currentIndex + 1) % popupMarkers.length;
    }

    rotatePopups();
    setInterval(rotatePopups, 3000);
  })
  .catch(error => console.error("Error fetching building events:", error));


  buildings.forEach(building => {
    const marker = L.marker(building.coord).addTo(map);
    marker.bindTooltip(building.name, {
      permanent: true,
      direction: 'top',
      className: 'building-label'
    });
  
    // ✨ Optional: Create a tile-style popup content
    const popupContent = `
      <div class="popup-tile">
        <h3>${building.name}</h3>
        <ul>
          ${building.events.map(event => `<li>${event}</li>`).join('')}
        </ul>
      </div>
    `;
    marker.bindPopup(popupContent);
  });
  
let currentIndex = 0;
let popupMarkers = [];

// Store markers with popups
buildings.forEach(building => {
  const marker = L.marker(building.coord).addTo(map);
  const popupContent = `
    <div class="popup-tile">
      <h3>${building.name}</h3>
      <ul>
        ${building.events.map(event => `<li>${event}</li>`).join('')}
      </ul>
    </div>
  `;
  marker.bindPopup(popupContent);
  popupMarkers.push(marker);
  marker.bindTooltip(building.name, {
    permanent: true,
    direction: 'top',
    className: 'building-label'
  });
});

// Function to cycle through popups
function rotatePopups() {
  // Close all popups
  popupMarkers.forEach(marker => marker.closePopup());

  // Open the current one
  const marker = popupMarkers[currentIndex];
  marker.openPopup();

  // Pan the map to marker (optional)
  map.panTo(marker.getLatLng());

  // Move to next
  currentIndex = (currentIndex + 1) % popupMarkers.length;
}

// Start auto-rotation every 5 seconds
rotatePopups(); // start with first one
setInterval(rotatePopups, 3000);
