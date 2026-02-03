#This tool called Flask is an open source micro web framwork, was suggested by ChatGPT to create a web applicatiuon and API's
#What it provides Core functionality like URL routing and handling requests, leaves decisions about tools for databases, from validation, and authentication to development 
#Built on top of other powerful libraries: Werkzeug (Web server gateway interface), Jinja(powerful templating engine, used to embed python logic and dynamic data into HTYML files),
#and click(Creating flasks command line interface trools)
    
from flask import Flask, jsonify
app = Flask (__name__)

#Hardcoded data representing parking spots
parking_spots = [
    {"id":1, "occupied": False},
    {"id":2, "occupied": True},
    {"id":3, "occupied": False},
]

@app.route("/spots")
def get_spots():
    return jsonify(parking_spots)

@app.route("/")
def home():
    return "Welcome to QuickSpot Parking System"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)  #debug=True enables auto-reloading and better error messages
    
#variables
#parking lot
lot_id = 1
lot_name = "Cerritos Mall"
lot_updated = None
total_spots = 10
#parking spots
spot_id = None
lot_id
occupied_count = 0 
open_spots = None
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
#checks which spots are occupied and adds it to the count 
for spot in spots:
    if spot["occupied"]:
        occupied_count += 1
print("Occupied spots:", occupied_count)
open_spots = total_spots - occupied_count
print("Open spots:", open_spots)