#This tool called Flask is an open source micro web framwork, was suggested by ChatGPT to create a web applicatiuon and API's
#What it provides Core functionality like URL routing and handling requests, leaves decisions about tools for databases, from validation, and authentication to development 
#Built on top of other powerful libraries: Werkzeug (Web server gateway interface), Jinja(powerful templating engine, used to embed python logic and dynamic data into HTYML files),
#and click(Creating flasks command line interface trools)
from flask import Flask, jsonify, request, render_template, session
from model.parking_manager import ParkingManager
from model.parking_lot import ParkingLot
from DataBase.database import (
    init_db, get_all_lots, get_lot_by_id,
    save_parked_spot, get_parked_spot, clear_parked_spot
)
from auth import auth

app = Flask(__name__)
app.secret_key = 'change-this-to-a-random-secret-key'

app.register_blueprint(auth)
init_db()

# ── Load lots from DB ─────────────────────────────────────────────
manager = ParkingManager()

def load_lots_from_db():
    for row in get_all_lots():
        manager.add_lot(ParkingLot(
            lot_id      = row['lot_id'],
            lot_name    = row['lot_name'],
            total_spots = row['total_spots'],
        ))

load_lots_from_db()


# ── Helper ────────────────────────────────────────────────────────
def lot_to_dict(lot):
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


# ── Routes ────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html", lots=manager.get_all_lots())


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
        if q == "" or q in lot.lot_name.lower() or (row and q == row['zip']):
            results.append(lot_to_dict(lot))
    return jsonify(results)


@app.route("/api/lots/<int:lot_id>/spots")
def get_spots_api(lot_id):
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404
    lot.simulate_sensor_update()

    # Find which spot (if any) belongs to the current user
    user_spot_id = None
    if session.get('user_id'):
        record = get_parked_spot(session['user_id'])
        if record and record['lot_id'] == lot_id:
            user_spot_id = record['spot_id']

    return jsonify({
        "available":    len(lot.get_available_spots()),
        "occupied":     len(lot.get_occupied_spots()),
        "user_spot_id": user_spot_id,
        "spots": [
            {"spot_id": s.spot_id, "occupied": s.occupied}
            for s in lot.spots
        ]
    })


@app.route("/api/me/spot")
def my_spot():
    """Return the current user's active parked spot."""
    if not session.get('user_id'):
        return jsonify({"spot": None})
    record = get_parked_spot(session['user_id'])
    if not record:
        return jsonify({"spot": None})
    return jsonify({"spot": {
        "lot_id":  record['lot_id'],
        "spot_id": record['spot_id'],
    }})


@app.route("/lots/<int:lot_id>/spots")
def get_spots(lot_id):
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404
    lot.simulate_sensor_update()

    # Pass the user's current spot to the template for initial render
    user_spot_id = None
    if session.get('user_id'):
        record = get_parked_spot(session['user_id'])
        if record and record['lot_id'] == lot_id:
            user_spot_id = record['spot_id']

    return render_template(
        "spots.html",
        lot=lot,
        spots=lot.spots,
        user_spot_id=user_spot_id,
        logged_in=bool(session.get('user_id')),
        username=session.get('username', ''),
    )


@app.route("/lots/<int:lot_id>/park", methods=["POST"])
def park_vehicle(lot_id):
    # Must be logged in
    if not session.get('user_id'):
        return jsonify({"error": "Login required"}), 401

    data = request.get_json()
    lot  = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404

    spot_id    = data.get("spot_id")
    plate      = f"USER-{session['user_id']}"  # use user ID as plate

    # If user already has a spot, release it first
    existing = get_parked_spot(session['user_id'])
    if existing:
        prev_lot = manager.lots.get(existing['lot_id'])
        if prev_lot:
            prev_lot.leaving_vehicle_from_spot(existing['spot_id'])
        clear_parked_spot(session['user_id'])

    # Park in the requested spot
    if spot_id:
        # Park in a specific spot
        target_spot = next((s for s in lot.spots if s.spot_id == spot_id), None)
        if not target_spot:
            return jsonify({"error": "Spot not found"}), 404
        if target_spot.occupied:
            return jsonify({"error": "Spot already taken"}), 409
        from model.vehicle import Vehicle
        target_spot.park_vehicle(Vehicle(plate))
        actual_spot_id = spot_id
    else:
        # Fall back to first available
        actual_spot_id = lot.park_vehicle_in_open(plate)
        if actual_spot_id is None:
            return jsonify({"error": "Lot is full"}), 400

    # Save to DB
    save_parked_spot(session['user_id'], lot_id, actual_spot_id)

    return jsonify({
        "message": "Parked successfully",
        "lot_id":  lot_id,
        "spot_id": actual_spot_id,
    })


@app.route("/lots/<int:lot_id>/leave", methods=["POST"])
def leave_vehicle(lot_id):
    if not session.get('user_id'):
        return jsonify({"error": "Login required"}), 401

    record = get_parked_spot(session['user_id'])
    if not record or record['lot_id'] != lot_id:
        return jsonify({"error": "You are not parked here"}), 400

    lot = manager.lots.get(lot_id)
    if lot:
        lot.leaving_vehicle_from_spot(record['spot_id'])

    clear_parked_spot(session['user_id'])
    return jsonify({"message": "Left successfully"})


@app.route("/lots/<int:lot_id>/simulate", methods=["POST"])
def simulate(lot_id):
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404
    lot.simulate_sensor_update()
    return jsonify({"message": "Simulation complete"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)