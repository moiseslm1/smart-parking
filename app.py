#This tool called Flask is an open source micro web framwork, was suggested by ChatGPT to create a web applicatiuon and API's
#What it provides Core functionality like URL routing and handling requests, leaves decisions about tools for databases, from validation, and authentication to development 
#Built on top of other powerful libraries: Werkzeug (Web server gateway interface), Jinja(powerful templating engine, used to embed python logic and dynamic data into HTYML files),
#and click(Creating flasks command line interface trools)
from flask import Flask, jsonify, request, render_template, session
from model.parking_manager import ParkingManager
from model.parking_lot import ParkingLot
from datetime import date
from DataBase.database import (
    init_db, get_all_lots, get_lot_by_id, get_lots_by_category,
    save_parked_spot, get_parked_spot, clear_parked_spot,
    create_reservation, get_user_reservations, delete_reservation,
    get_lot_reservations, get_reserved_spot_ids
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


# ── Helpers ───────────────────────────────────────────────────────
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
        "lat":       row['lat']      if row else None,
        "lng":       row['lng']      if row else None,
        "zip":       row['zip']      if row else "",
        "address":   row['address']  if row else "",
        "category":  row['category'] if row else "other",
    }

def get_user_reserved_lot_ids():
    if not session.get('user_id'):
        return set()
    today = date.today().isoformat()
    rows = get_user_reservations(session['user_id'])
    return {r['lot_id'] for r in rows if r['date'] >= today}


# ── Page routes ───────────────────────────────────────────────────
@app.route("/")
def home():
    all_lots = manager.get_all_lots()
    # Sort by occupancy % descending, take top 6 for the homepage grid
    def occupancy_pct(lot):
        occupied = len(lot.get_occupied_spots())
        return (occupied / lot.total_spots) if lot.total_spots else 0

    popular_lots = sorted(all_lots, key=occupancy_pct, reverse=True)[:6]
    reserved_lot_ids = get_user_reserved_lot_ids()
    return render_template("index.html", lots=popular_lots, total_lots=len(all_lots), reserved_lot_ids=reserved_lot_ids)


@app.route("/my-reservations")
def my_reservations():
    if not session.get('user_id'):
        return render_template("login.html"), 401
    reservations = get_user_reservations(session['user_id'])
    today_str = date.today().isoformat()
    return render_template(
        "my_reservations.html",
        reservations=reservations,
        today_str=today_str,
    )


@app.route("/lots/<int:lot_id>/spots")
def get_spots(lot_id):
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404
    lot.simulate_sensor_update()

    # Current user's parked spot
    user_spot_id = None
    if session.get('user_id'):
        record = get_parked_spot(session['user_id'])
        if record and record['lot_id'] == lot_id:
            user_spot_id = record['spot_id']

    # All upcoming reservations for this lot: {spot_id: reservation_info}
    lot_reservations = get_lot_reservations(lot_id)

    # This user's reserved spot IDs in this lot
    user_reserved_spot_ids = set()
    if session.get('user_id'):
        user_reserved_spot_ids = get_reserved_spot_ids(lot_id, session['user_id'])

    return render_template(
        "spots.html",
        lot=lot,
        spots=lot.spots,
        user_spot_id=user_spot_id,
        logged_in=bool(session.get('user_id')),
        username=session.get('username', ''),
        lot_reservations=lot_reservations,
        user_reserved_spot_ids=user_reserved_spot_ids,
    )


# ── Lot API ───────────────────────────────────────────────────────
@app.route("/api/lots")
def api_lots():
    data = []
    for lot in manager.get_all_lots():
        lot.simulate_sensor_update()
        data.append(lot_to_dict(lot))
    return jsonify(data)


@app.route("/api/lots/category/<category>")
def api_lots_by_category(category):
    rows = get_lots_by_category(category.lower())
    data = []
    for row in rows:
        lot = manager.lots.get(row['lot_id'])
        if lot:
            data.append(lot_to_dict(lot))
        else:
            data.append({
                "lot_id":    row['lot_id'],  "lot_name":  row['lot_name'],
                "total":     row['total_spots'], "available": 0, "occupied": 0, "pct": 0,
                "lat":       row['lat'],     "lng":       row['lng'],
                "zip":       row['zip'],     "address":   row['address'],
                "category":  row['category'],
            })
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

    user_spot_id = None
    if session.get('user_id'):
        record = get_parked_spot(session['user_id'])
        if record and record['lot_id'] == lot_id:
            user_spot_id = record['spot_id']

    # Reserved spot IDs for this lot (any user)
    lot_reservations = get_lot_reservations(lot_id)
    reserved_spot_ids = list(lot_reservations.keys())

    # This user's reserved spots
    user_reserved_spot_ids = []
    if session.get('user_id'):
        user_reserved_spot_ids = list(get_reserved_spot_ids(lot_id, session['user_id']))

    return jsonify({
        "available":             len(lot.get_available_spots()),
        "occupied":              len(lot.get_occupied_spots()),
        "user_spot_id":          user_spot_id,
        "reserved_spot_ids":     reserved_spot_ids,
        "user_reserved_spot_ids": user_reserved_spot_ids,
        "spots": [
            {"spot_id": s.spot_id, "occupied": s.occupied}
            for s in lot.spots
        ]
    })


# ── Park / Leave ──────────────────────────────────────────────────
@app.route("/lots/<int:lot_id>/park", methods=["POST"])
def park_vehicle(lot_id):
    if not session.get('user_id'):
        return jsonify({"error": "Login required"}), 401

    data    = request.get_json()
    lot     = manager.lots.get(lot_id)
    spot_id = data.get("spot_id") if data else None

    if not lot:
        return jsonify({"error": "Lot not found"}), 404

    plate = f"USER-{session['user_id']}"

    existing = get_parked_spot(session['user_id'])
    if existing:
        prev_lot = manager.lots.get(existing['lot_id'])
        if prev_lot:
            prev_lot.leaving_vehicle_from_spot(existing['spot_id'])
        clear_parked_spot(session['user_id'])

    if spot_id:
        target = next((s for s in lot.spots if s.spot_id == spot_id), None)
        if not target:
            return jsonify({"error": "Spot not found"}), 404
        if target.occupied:
            return jsonify({"error": "Spot already taken"}), 409
        from model.vehicle import Vehicle
        target.park_vehicle(Vehicle(plate))
        actual_spot_id = spot_id
    else:
        actual_spot_id = lot.park_vehicle_in_open(plate)
        if actual_spot_id is None:
            return jsonify({"error": "Lot is full"}), 400

    save_parked_spot(session['user_id'], lot_id, actual_spot_id)
    return jsonify({"message": "Parked successfully", "lot_id": lot_id, "spot_id": actual_spot_id})


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


# ── Reservations ──────────────────────────────────────────────────
@app.route("/api/reservations", methods=["POST"])
def make_reservation():
    if not session.get('user_id'):
        return jsonify({"error": "Login required"}), 401

    data     = request.get_json()
    lot_id   = data.get("lot_id")
    spot_id  = data.get("spot_id")
    res_date = data.get("date")
    res_time = data.get("time")
    duration = data.get("duration", 60)

    if not all([lot_id, spot_id, res_date, res_time]):
        return jsonify({"error": "lot_id, spot_id, date, and time are required"}), 400

    row = get_lot_by_id(lot_id)
    if not row:
        return jsonify({"error": "Lot not found"}), 404

    reservation_id = create_reservation(
        session['user_id'], lot_id, spot_id, res_date, res_time, duration
    )
    return jsonify({
        "message":        "Reservation confirmed",
        "reservation_id": reservation_id,
        "lot_name":       row['lot_name'],
        "spot_id":        spot_id,
        "date":           res_date,
        "time":           res_time,
        "duration":       duration,
    })


@app.route("/api/reservations", methods=["GET"])
def get_reservations():
    if not session.get('user_id'):
        return jsonify({"error": "Login required"}), 401
    rows = get_user_reservations(session['user_id'])
    return jsonify([dict(r) for r in rows])


@app.route("/api/reservations/<int:reservation_id>", methods=["DELETE"])
def cancel_reservation(reservation_id):
    if not session.get('user_id'):
        return jsonify({"error": "Login required"}), 401
    delete_reservation(reservation_id, session['user_id'])
    return jsonify({"message": "Reservation cancelled"})


# ── Misc ──────────────────────────────────────────────────────────
@app.route("/lots/<int:lot_id>/simulate", methods=["POST"])
def simulate(lot_id):
    lot = manager.lots.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404
    lot.simulate_sensor_update()
    return jsonify({"message": "Simulation complete"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)