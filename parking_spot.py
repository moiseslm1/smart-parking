class ParkingSpot:
    def __init__(self, spot_id, lot_id):
        self.spot_id = spot_id
        self.lot_id = lot_id
        self.occupied = False
        self.vehicle_info = None
    def park_vehicle(self, vehicle_info):
        if not self.occupied:
            self.vehicle_info = vehicle_info
            self.occupied = True
            return True
        return False #spot occupied
    def leave_vehicle(self):
        if self.occupied:
            self.vehicle_info = None
            self.occupied = False
            return True #spot free
    def display_info(self):
        status = "Occupied" if self.occupied else "Available"
        return f"Spot {self.spot_id}: {status} | Vehicle: {self.vehicle_info or 'None'}"
    