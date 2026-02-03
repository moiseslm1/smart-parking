#This tool called Flask is an open source micro web framwork, was suggested by ChatGPT to create a web applicatiuon and API's
#What it provides Core functionality like URL routing and handling requests, leaves decisions about tools for databases, from validation, and authentication to development 
#Built on top of other powerful libraries: Werkzeug (Web server gateway interface), Jinja(powerful templating engine, used to embed python logic and dynamic data into HTYML files),
#and click(Creating flasks command line interface trools)
    
from flask import Flask, jsonify
app = Flask (__name__)
#parking lot
lot_id = 1
lot_name = "Cerritos Mall"
lot_updated = None
total_spots = 10
#parking spots
spot_id = None
occupied_count = 0 
open_spots = 10
#list of parking spots in the lot
spots = [
    {"spot_id": 1, "occupied": False},
    {"spot_id": 2, "occupied": True},
    {"spot_id": 3, "occupied": False},
    {"spot_id": 4, "occupied": False},
    {"spot_id": 5, "occupied": True},
    {"spot_id": 6, "occupied": False},
    {"spot_id": 7, "occupied": False},
    {"spot_id": 8, "occupied": True},
    {"spot_id": 9, "occupied": False},
    {"spot_id": 10, "occupied": False},
]

#Hardcoded data representing parking spots
parking_spots = [
    {"id":1, "occupied": False},
    {"id":2, "occupied": True},
    {"id":3, "occupied": False},
]

@app.route("/spots")
def get_spots():
    occupied_count = sum(1 for spot in spots if spot["occupied"])
    open_spots = total_spots - occupied_count
    data = {
        "lot_id": lot_id,
        "lot_name": lot_name,
        "total_spots": total_spots,
        "occupied_spots": occupied_count,
        "open_spots": open_spots,
        "spots": spots
    }
    return jsonify(data)

@app.route("/")
def home():
    return "Welcome to QuickSpot Parking System"
    #occupied_count = sum(1 for spot in spots if spot["occupied"])
    #open_spots = total_spots - occupied_count
    #return jsonify({
        #"Welcome to QuickSpot Parking System": "",
        #"lot_id": lot_id,
        #"lot_name": lot_name,
        #"total_spots": total_spots,
        #"occupied_spots": occupied_count,
        #"open_spots": open_spots,
    #})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)  #debug=True enables auto-reloading and better error messages
    
    