#This tool called Flask is an open source micro web framwork, was suggested by ChatGPT to create a web applicatiuon and API's
#What it provides Core functionality like URL routing and handling requests, leaves decisions about tools for databases, from validation, and authentication to development 
#Built on top of other powerful libraries: Werkzeug (Web server gateway interface), Jinja(powerful templating engine, used to embed python logic and dynamic data into HTYML files),
#and click(Creating flasks command line interface trools)
from flask import Flask, jsonify, request
from parking_manager import ParkingManager
from parking_lot import ParkingLot
app = Flask (__name__)
lot = ParkingLot(lot_id=1, lot_name="Cerritos Mall", total_spots=10)
manager = ParkingManager()
#temporary
print(manager.__dict__)
#Creation of Parking lots
lot1 = ParkingLot(lot_id =1, lot_name = "Cerritos Mall", total_spots = 10)
lot2 = ParkingLot(lot_id = 2, lot_name = "EOS Fitness", total_spots = 20)
manager.add_lot(lot1)
manager.add_lot(lot2)

@app.route("/")
def home():
    return "Welcome to QuickSpot Parking System"

@app.route("/lots")
def get_lots():
    lots_data = []
    for lot in manager.get_all_lots():
        lots_data.append({
            "lot_id": lot.lot_id,
            "lot_name": lot.lot_name,
            "total_spots": lot.total_spots,
            "available_spots": len(lot.get_available_spots()),
            "occupied_spots": len(lot.get_occupied_spots())
        })
    return jsonify(lots_data)

@app.route("/lots/<int:lot_id>/spots")
def get_spots(lot_id):
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404
    spots = manager.get_lot_status(lot_id)
    if spots is None:
        return jsonify({"error": "Lot not found"}), 404
    
    spots_data = []
    for spot in lot.spots:
        spots_data.append({
            "spot_id": spot.spot_id,
            "occupied": spot.occupied,
            "vehicle": spot.vehicle.plate_number if spot.vehicle else None
        })
    return jsonify(spots_data)
    
@app.route("/lots/<int:lot_id>/park", methods=["POST"])
def park_vehicle(lot_id):
    data = request.get_json()
    plate_number = data.get("plate_number")
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "lot not found"}), 484
    if not data or "vehicle_info" not in data:
        return jsonify({"error": "vehicle_info required"}), 400
    spot_id = manager.park_vehicle(lot_id, data["vehicle_info"])
    if spot_id is None:
        return jsonify({"error": "Parking lot is full or not found"}), 400
    return jsonify({
        "message": "vehicle parked",
        "lot_id" : lot_id,
        "spot_id": spot_id
    })
    
@app.route("/lots/<int:lot_id>/leave", methods =["POST", "GET"])
def leave_vehicle(lot_id):
    data = request.get_json()
    if not data or "spot_id" not in data:
        return jsonify({"error": "spot_id required"}), 400
    success = manager.leave_vehicle(lot_id, data["spot_id"])
    
    if not success:
        return jsonify({"error": "Invalid lot or spot"}), 400
    return jsonify({
        "message": "Vehicle left",
        "lot_id": lot_id,
        "spot_id": data["spot_id"]
    })
    
@app.route("/lots/<int:lot_id>/simulate", methods=["POST"])
def simulate(lot_id): 
    if not lot:
        return jsonify({"error": "Lot not found"}), 404
    lot.simulate_sensor_update()
    return jsonify({"message": "Sensor simulation complete"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001,debug=True)  #debug=True enables auto-reloading and better error messages