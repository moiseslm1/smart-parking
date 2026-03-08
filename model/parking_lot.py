from model.parking_spot import ParkingSpot
from model.vehicle import Vehicle
from datetime import datetime
import random 
   


class ParkingLot:
    def __init__(self, lot_id, lot_name, total_spots, lot_updated=None):
        self.lot_id = lot_id           
        self.lot_name = lot_name             
        self.total_spots = total_spots       
        self.lot_updated = lot_updated or datetime.now()       
        self.spots = []                       

        # Initialize spots
        for i in range(1, total_spots + 1):
            self.spots.append(ParkingSpot(spot_id=i, lot_id=lot_id))

    def get_available_spots(self):
        return [spot for spot in self.spots if not spot.occupied]

    def get_occupied_spots(self):
        return [spot for spot in self.spots if spot.occupied]

    def park_vehicle_in_open(self, plate_number):
        available_spots = self.get_available_spots()
        
        if available_spots:
             spot = available_spots[0]
             vehicle = Vehicle(plate_number)

             spot.park_vehicle(vehicle)
             self.lot_updated = datetime.now()

             return spot.spot_id
        return None  # Lot is full

    def leaving_vehicle_from_spot(self, spot_id):
        for spot in self.spots:
            if spot.spot_id == spot_id:
                self.lot_updated = datetime.now()  # Update the lot's last updated time
                return spot.leave_vehicle()
        return False  # Spot not found

    def display_lot_info(self):
        print(f"Parking Lot: {self.lot_name} (ID: {self.lot_id})")
        print(f"Total Spots: {self.total_spots}")
        print(f"Occupied: {len(self.get_occupied_spots())}")
        print(f"Available: {len(self.get_available_spots())}")
        print("Spots Status:")
        for spot in self.spots:
            print(spot.display_info())
            
    def simulate_sensor_update(self):
        for spot in self.spots:
            if random.random() < 0.2:
                if spot.occupied:
                    spot.leave_vehicle()
                else:
                    fake_plate = f"SIM-{random.randint(100,999)}"
                    spot.park_vehicle(Vehicle(fake_plate))
        self.lot_updated = datetime.now()