from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import QUrl

import time

class TelemetryMap(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.auto_center = True

        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        map_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src='http://localhost:9997/static/maplibre-gl.js'></script>
            <link href='http://localhost:9997/static/maplibre-gl.css' rel='stylesheet' />
            <style>
                body { margin: 0; padding: 0; }
                #map { position: absolute; top: 0; bottom: 0; width: 100%; background: #1e1e1e; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var isReady = false;
                var pointData = { "type": "FeatureCollection", "features": [] };
                var lineCoords = [];
                var popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

                var map = new maplibregl.Map({
                    container: 'map',
                    style: 'http://localhost:9997/style.json',
                    center: [22.01, 50.04],
                    zoom: 18,
                    pitch: 45
                });

                map.on('load', () => {
                    map.addSource('route', { 'type': 'geojson', 'data': { 'type': 'Feature', 'geometry': { 'type': 'LineString', 'coordinates': [] }}});
                    map.addLayer({ 'id': 'route-line', 'type': 'line', 'source': 'route', 'paint': { 'line-color': '#00d1ff', 'line-width': 4 }});

                    map.addSource('points', { 'type': 'geojson', 'data': pointData });
                    map.addLayer({ 'id': 'points-layer', 'type': 'circle', 'source': 'points', 'paint': { 'circle-radius': 4, 'circle-color': '#00d1ff', 'circle-opacity': 0.6 }});

                    map.addSource('current', { 'type': 'geojson', 'data': { 'type': 'Point', 'coordinates': [0, 0] }});
                    map.addLayer({ 'id': 'curr-dot', 'type': 'circle', 'source': 'current', 'paint': { 'circle-radius': 6, 'circle-color': '#ffcc00', 'circle-stroke-width': 2, 'circle-stroke-color': '#fff' }});

                    map.on('mouseenter', 'points-layer', function(e) {
                        map.getCanvas().style.cursor = 'pointer';
                        var props = e.features[0].properties;
                        var coords = e.features[0].geometry.coordinates;
                        popup.setLngLat(coords)
                             .setHTML('<div style="color:#000;font-size:13px;line-height:1.6">'
                                 + '<b>Speed:</b> ' + props.speed + ' km/h<br>'
                                 + '<b>RPM:</b> ' + props.rpm + '<br>'
                                 + '<b>TIME:</b> ' + props.time
                                 + '</div>')
                             .addTo(map);
                    });

                    map.on('mouseleave', 'points-layer', function() {
                        map.getCanvas().style.cursor = '';
                        popup.remove();
                    });

                    isReady = true;
                    console.log("MAP_LOADED");
                });

                function addPoint(lat, lng, rpm, speed, shouldSnap, time) {
                    if (!isReady) return;
                    var pos = [lng, lat];
                    lineCoords.push(pos);
                    pointData.features.push({
                        "type": "Feature",
                        "geometry": { "type": "Point", "coordinates": pos },
                        "properties": { "rpm": rpm, "speed": speed, "time": time }
                    });

                    map.getSource('route').setData({ 'type': 'Feature', 'geometry': { 'type': 'LineString', 'coordinates': lineCoords }});
                    map.getSource('current').setData({ 'type': 'Point', 'coordinates': pos });
                    map.getSource('points').setData(pointData);

                    if (shouldSnap) {
                        map.easeTo({ center: pos, duration: 500 });
                    }
                }
            </script>
        </body>
        </html>
        """

        self.setHtml(map_html, QUrl("http://localhost:9997/"))

    def update_position(self, lat, lng, rpm, speed):
        snap = "true" if self.auto_center else "false"

        fmt = time.localtime(time.time())
        strtime = time.strftime("%D %T", fmt)

        self.page().runJavaScript(f"addPoint({lat}, {lng}, {rpm}, {speed}, {snap}, '{strtime}')")
