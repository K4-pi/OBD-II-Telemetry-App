import sqlite3
from flask import Flask, Response, jsonify, send_from_directory
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

MBTILES_PATH = "src/map/telemetry_map.mbtiles"

def get_tile_from_db(z, x, y):
    try:
        tms_y = (1 << int(z)) - 1 - int(y)
        conn = sqlite3.connect(MBTILES_PATH)
        cur = conn.cursor()

        try:
            cur.execute("SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?", (z, x, tms_y))
        except sqlite3.OperationalError:
            cur.execute("SELECT tile_data FROM map WHERE zoom_level=? AND tile_column=? AND tile_row=?", (z, x, tms_y))

        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"SQL Error: {e}")
        return None

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/tiles/<z>/<x>/<y>.pbf')
def serve_tile(z, x, y):
    tile = get_tile_from_db(z, x, y)
    if tile:
        resp = Response(tile, mimetype='application/x-protobuf')
        resp.headers['Content-Encoding'] = 'gzip'
        return resp
    return '', 404

@app.route('/style.json')
def serve_style():
    return jsonify({
        "version": 8,
        "sources": {
            "data": {
                "type": "vector",
                "tiles": ["http://localhost:9997/tiles/{z}/{x}/{y}.pbf"],
                "minzoom": -2,
                "maxzoom": 14
            }
        },
        "layers": [
            {"id": "bg", "type": "background", "paint": {"background-color": "#1e1e1e"}},
            {"id": "land", "type": "fill", "source": "data", "source-layer": "land", "paint": {"fill-color": "#2a2a2a"}},
            {"id": "water-poly", "type": "fill", "source": "data", "source-layer": "water_polygons", "paint": {"fill-color": "#111"}},
            {"id": "water-line", "type": "line", "source": "data", "source-layer": "water_lines", "paint": {"line-color": "#111", "line-width": 1}},
            {"id": "streets", "type": "line", "source": "data", "source-layer": "streets", "paint": {"line-color": "#444", "line-width": 1}}
        ]
    })

def run():
    app.run(port=9997, debug=False, use_reloader=False)

def start_server():
    threading.Thread(target=run, daemon=True).start()
