#This tool called Flask is an open source micro web framwork, was suggested by ChatGPT to create a web applicatiuon and API's
#What it provides Core functionality like URL routing and handling requests, leaves decisions about tools for databases, from validation, and authentication to development 
#Built on top of other powerful libraries: Werkzeug (Web server gateway interface), Jinja(powerful templating engine, used to embed python logic and dynamic data into HTYML files),
#and click(Creating flasks command line interface trools)
from flask import Flask, jsonify, request, render_template
from model.parking_manager import ParkingManager
from model.parking_lot import ParkingLot

app = Flask(__name__)
manager = ParkingManager()

# ── Lot definitions ──────────────────────────────────────────────
# When you add a database later, replace this list with a DB query.
# Each lot now carries lat, lng, zip, and address for map display.
LOT_META = {
    1: {"lat": 33.86260359286076, "lng": -118.09482494419677, "zip": "90703", "address": "239 Los Cerritos Center, Cerritos, CA"},
    2: {"lat": 33.83033980660525, "lng": -118.07367278827475, "zip": "90716", "address": "12120 E Carson St, Hawaiian Gardens, CA"},
    3: {"lat": 33.9000, "lng": -118.1006, "zip": "90242", "address": "251 Stonewood St, Downey, CA"},
    4: {"lat": 33.8850, "lng": -118.0920, "zip": "90242", "address": "8550 Florence Ave, Downey, CA"},
    5: {"lat": 33.86022798585085, "lng": -118.04965531404206, "zip": "90703", "address": "13233 South St, Cerritos, CA"},
}

# Creation of Parking lots
manager.add_lot(ParkingLot(1, "Los Cerritos Center", 150))
manager.add_lot(ParkingLot(2, "EOS Fitness", 20))
manager.add_lot(ParkingLot(3, "Stonewood Mall", 32))
manager.add_lot(ParkingLot(4, "LA Fitness", 15))
manager.add_lot(ParkingLot(5, "EOS Fitness", 100))

# ── helpers ──────────────────────────────────────────────────────
def lot_to_dict(lot):
    meta = LOT_META.get(lot.lot_id, {})
    available = len(lot.get_available_spots())
    occupied  = len(lot.get_occupied_spots())
    pct       = round((occupied / lot.total_spots) * 100) if lot.total_spots else 0
    return {
        "lot_id":    lot.lot_id,
        "lot_name":  lot.lot_name,
        "total":     lot.total_spots,
        "available": available,
        "occupied":  occupied,
        "pct":       pct,
        "lat":       meta.get("lat"),
        "lng":       meta.get("lng"),
        "zip":       meta.get("zip", ""),
        "address":   meta.get("address", ""),
    }

@app.route("/")
def home():
    lots = manager.get_all_lots()
    for lot in lots:
        lot.simulate_sensor_update()
    return render_template("index.html", lots=lots)

@app.route("/api/lots")
def get_lots():
    data = []
    for lot in manager.get_all_lots():
        lot.simulate_sensor_update()
        data.append(lot_to_dict(lot))
    return jsonify(data)

@app.route("/api/search")
def search_lots():
    """
    GET /api/search?q=<query>
    Matches lots by name (partial, case-insensitive) OR zip code.
    Ready to be swapped for a real DB query later.
    """
    q = request.args.get("q", "").strip().lower()
    results = []
    for lot in manager.get_all_lots():
        meta = LOT_META.get(lot.lot_id, {})
        name_match = q in lot.lot_name.lower()
        zip_match  = q == meta.get("zip", "")
        if q == "" or name_match or zip_match:
            results.append(lot_to_dict(lot))
    return jsonify(results)

@app.route("/api/lots/<int:lot_id>/spots")
def get_spots_api(lot_id):
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404
    lot.simulate_sensor_update()
    return jsonify({
        "available": len(lot.get_available_spots()),
        "occupied":  len(lot.get_occupied_spots()),
        "spots": [
            {"spot_id": s.spot_id, "occupied": s.occupied}
            for s in lot.spots
        ]
    })

@app.route("/lots/<int:lot_id>/spots")
def get_spots(lot_id):
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404
    lot.simulate_sensor_update()
    return render_template("spots.html", lot=lot, spots=lot.spots)

@app.route("/lots/<int:lot_id>/park", methods=["POST"])
def park_vehicle(lot_id):
    data = request.get_json()
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "lot not found"}), 404
    if not data or "plate_number" not in data:
        return jsonify({"error": "plate_number required"}), 400
    spot_id = manager.park_vehicle(lot_id, data["plate_number"])
    if spot_id is None:
        return jsonify({"error": "Parking lot is full or not found"}), 400
    return jsonify({"message": "vehicle parked", "lot_id": lot_id, "spot_id": spot_id})

@app.route("/lots/<int:lot_id>/leave", methods=["POST", "GET"])
def leave_vehicle(lot_id):
    data = request.get_json()
    if not data or "spot_id" not in data:
        return jsonify({"error": "spot_id required"}), 400
    success = manager.leave_vehicle(lot_id, data["spot_id"])
    if not success:
        return jsonify({"error": "Invalid lot or spot"}), 400
    return jsonify({"message": "Vehicle left", "lot_id": lot_id, "spot_id": data["spot_id"]})

@app.route("/lots/<int:lot_id>/simulate", methods=["POST"])
def simulate(lot_id):
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404
    lot.simulate_sensor_update()
    return jsonify({"message": "Sensor simulation complete"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)