
from parking_lot import ParkingLot
class ParkingManager:
    def __init__(self):
        self.lots = {}
    
    def add_lot(self, parking_lot):
        self.lots[parking_lot.lot_id] = parking_lot
    #creates a new lot basedon the parking lot ID and adds it to the lots dictionary
    def get_lot(self, lot_id):
        return self.lots.get(lot_id)
    #retrieves a lot based on the lot ID from the lots dictionary
    def get_all_lots(self):
        return list(self.lots.values())
    #get lot and get all lots will help with managing multiple parking lots
    def park_vehicle(self, lot_id, vehicle_info):
        lot = self.lots.get(lot_id)
        if not lot:
            return None
        return lot.park_vehicle_in_open(vehicle_info)
    #Checks if lot exists, if it does, it checks for the lot the vehicle is parking in and gets the vehicle info
    def leave_vehicle(self, lot_id, spot_id ):
        lot = self.lots.get(lot_id)
        if not lot:
            return False
        return lot.leaving_vehicle_from_spot(spot_id)
    #Checks if lot exists, if it does, it checks for the lot the vehicle is leaving from and gets the spot ID
    def get_lot_status(self, lot_id):
        lot = self.lots.get(lot_id)
        if not lot:
            return None
        return lot.spots
    #gives you back the number of spots in that lot, if the lot isn't found then nothing is returned 