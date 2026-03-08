#This tool called Flask is an open source micro web framwork, was suggested by ChatGPT to create a web applicatiuon and API's
#What it provides Core functionality like URL routing and handling requests, leaves decisions about tools for databases, from validation, and authentication to development 
#Built on top of other powerful libraries: Werkzeug (Web server gateway interface), Jinja(powerful templating engine, used to embed python logic and dynamic data into HTYML files),
#and click(Creating flasks command line interface trools)
from flask import Flask, jsonify, request, render_template
from model.parking_manager import ParkingManager
from model.parking_lot import ParkingLot

app = Flask(__name__)
manager = ParkingManager()

# Creation of Parking lots
manager.add_lot(ParkingLot(1, "Cerritos Mall", 10))
manager.add_lot(ParkingLot(2, "EOS Fitness", 20))
manager.add_lot(ParkingLot(3, "Stonewood Mall", 32))
manager.add_lot(ParkingLot(4, "LA Fitness", 15))

@app.route("/")
def home():
    lots = manager.get_all_lots()
    for lot in lots:
        lot.simulate_sensor_update()
    return render_template("index.html", lots=lots)

@app.route("/api/lots")                    # <-- renamed from /lots to /api/lots
def get_lots():
    data = []
    for lot in manager.get_all_lots():
        occupied  = len(lot.get_occupied_spots())
        available = len(lot.get_available_spots())
        pct       = round((occupied / lot.total_spots) * 100) if lot.total_spots else 0
        lot.simulate_sensor_update()       # <-- simulate on each poll so numbers actually change
        data.append({
            "lot_id":    lot.lot_id,
            "available": available,
            "occupied":  occupied,
            "total":     lot.total_spots,
            "pct":       pct,
        })
    return jsonify(data)

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
    app.run(host="0.0.0.0", port=5001, debug=True)