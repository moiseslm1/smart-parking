class ParkingSpot:
    def __init__(self, spot_id, lot_id):
        self.spot_id = spot_id
        self.lot_id = lot_id
        self.occupied = False
        self.vehicle = None
    def park_vehicle(self, vehicle):
        if not self.occupied:
            self.vehicle = vehicle
            self.occupied = True
            return True
        return False #spot occupied
    def leave_vehicle(self):
        if self.occupied:
            self.vehicle = None
            self.occupied = False
            return True #spot free
        return False #spot already free
    def display_info(self):
        return {
            "spot_id": self.spot_id,
            "occupied": self.occupied,
            "vehicle": self.vehicle.to_dict() if self.vehicle else None
        }
    