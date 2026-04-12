#This tool called Flask is an open source micro web framwork, was suggested by ChatGPT to create a web applicatiuon and API's
#What it provides Core functionality like URL routing and handling requests, leaves decisions about tools for databases, from validation, and authentication to development 
#Built on top of other powerful libraries: Werkzeug (Web server gateway interface), Jinja(powerful templating engine, used to embed python logic and dynamic data into HTYML files),
#and click(Creating flasks command line interface trools)
from flask import Flask, jsonify, request, render_template, session
from model.parking_manager import ParkingManager
from model.parking_lot import ParkingLot
from DataBase.database import init_db, get_all_lots, get_lot_by_id
from auth import auth

app = Flask(__name__)
app.secret_key = 'change-this-to-a-random-secret-key'  

app.register_blueprint(auth)

init_db()

manager = ParkingManager()

def load_lots_from_db():
    """
    Reads all lots from the database and registers them with the manager.
    Call this once at startup. To add a new lot, use database.add_lot()
    and restart the app — it will be picked up automatically.
    """
    for row in get_all_lots():
        manager.add_lot(ParkingLot(
            lot_id      = row['lot_id'],
            lot_name    = row['lot_name'],
            total_spots = row['total_spots'],
        ))

load_lots_from_db()


def lot_to_dict(lot):
    """Merge live spot counts with static DB metadata."""
    row       = get_lot_by_id(lot.lot_id)
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
        "lat":       row['lat']     if row else None,
        "lng":       row['lng']     if row else None,
        "zip":       row['zip']     if row else "",
        "address":   row['address'] if row else "",
    }


@app.route("/")
def home():
    lots = manager.get_all_lots()
    return render_template("index.html", lots=lots)


@app.route("/api/lots")
def api_lots():
    data = []
    for lot in manager.get_all_lots():
        lot.simulate_sensor_update()
        data.append(lot_to_dict(lot))
    return jsonify(data)


@app.route("/api/search")
def search_lots():
    q = request.args.get("q", "").strip().lower()
    results = []
    for lot in manager.get_all_lots():
        row = get_lot_by_id(lot.lot_id)
        name_match = q in lot.lot_name.lower()
        zip_match  = row and q == row['zip']
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
        "spots": [{"spot_id": s.spot_id, "occupied": s.occupied} for s in lot.spots]
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
    lot  = manager.lots.get(lot_id)
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
    app.run(host="0.0.0.0", port=5001, debug=True)