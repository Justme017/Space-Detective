// leaflet map init
var map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

var marker = null;

// click on map to choose coords
map.on('click', function(e) {
  var lat = e.latlng.lat.toFixed(4),
      lon = e.latlng.lng.toFixed(4);

  if (marker) marker.setLatLng(e.latlng);
  else marker = L.marker(e.latlng).addTo(map);

  document.getElementById('lat').value = lat;
  document.getElementById('lon').value = lon;
  document.getElementById('address').value = `Map (${lat}, ${lon})`;
});

// show/hide map
function showMap() {
  var c = document.getElementById('map-container');
  c.classList.toggle('hidden');
  setTimeout(() => map.invalidateSize(), 300);
}

// use browser GPS
function getGPS() {
  if (!navigator.geolocation) {
    return alert('GPS not supported');
  }
  navigator.geolocation.getCurrentPosition(function(pos) {
    var lat = pos.coords.latitude.toFixed(4),
        lon = pos.coords.longitude.toFixed(4);
    document.getElementById('lat').value = lat;
    document.getElementById('lon').value = lon;
    document.getElementById('address').value = `GPS (${lat}, ${lon})`;
    map.setView([lat, lon], 6);
    if (marker) marker.setLatLng([lat, lon]);
    else marker = L.marker([lat, lon]).addTo(map);
  }, function() { alert('Unable to fetch GPS'); });
}
