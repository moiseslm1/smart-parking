#This tool called Flask is an open source micro web framwork, was suggested by ChatGPT to create a web applicatiuon and API's
#What it provides Core functionality like URL routing and handling requests, leaves decisions about tools for databases, from validation, and authentication to development 
#Built on top of other powerful libraries: Werkzeug (Web server gateway interface), Jinja(powerful templating engine, used to embed python logic and dynamic data into HTYML files),
#and click(Creating flasks command line interface trools)
    
class ParkingSpot:
    def _init_ (self, spot_id, lot_id):
        self.spot_id = spot_id
        self.lot_id = lot_id
        self.occupied = False
        self.vehicle_info = None
    def park_vehivle(self, vehicle_info):
        if not self.occupied:
            self.vehicle_info = vehicle_info
            self.occupied = True
            return True
        return False
    def leave_vehicle(self):
        if self.occupied:
            self.vehicle_info = None
            self.occupied = False
            return True
    def display_info(self):
        status = "Occupied" if self.occupied else "Available"
        return f"Spot {self.spot_id}: {status} | Vehicle: {self.vehicle_info or "None"}"
    