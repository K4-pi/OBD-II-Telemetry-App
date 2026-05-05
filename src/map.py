from PyQt6.QtWebEngineWidgets import QWebEngineView

class TelemetryMap(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.auto_center = True  # Default to snapping

        map_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                #map { height: 100vh; width: 100%; margin: 0; padding: 0; background: #1e1e1e; }
                body { margin: 0; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map', {zoomControl: true}).setView([52.2297, 21.0122], 15);
                L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);
                var path = L.polyline([], {color: '#00d1ff', weight: 3}).addTo(map);

                function addPoint(lat, lng, rpm, speed, shouldSnap) {
                    var pos = [lat, lng];
                    path.addLatLng(pos);
                    var dot = L.circleMarker(pos, {radius: 4, color: '#ffcc00', fillOpacity: 0.8}).addTo(map);
                    dot.bindTooltip(`<b>${speed} km/h</b><br>${rpm} RPM`);

                    if (shouldSnap) {
                        map.panTo(pos);
                    }
                }
            </script>
        </body>
        </html>
        """
        self.setHtml(map_html)

    def update_position(self, lat, lng, rpm, speed):
        snap = "true" if self.auto_center else "false"
        self.page().runJavaScript(f"addPoint({lat}, {lng}, {rpm}, {speed}, {snap})")
