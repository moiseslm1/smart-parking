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