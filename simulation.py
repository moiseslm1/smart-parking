import random
from model.vehicle import Vehicle 

def simulate_arrival(lot):
    available_spots = [s for s in lot.spots if not s.is_occupied]
    
    if not available_spots:
        return None
    spot = random.choice(available_spots)
    vehicle = Vehicle()
    
    spot.assign_vehicle(vehicle)
    
def simulate_departure(lot):
    occupied_spots = [s for s in lot.spots if s.is_occupied]
    
    if not occupied_spots:
        return None
    spot = random.choice(occupied_spots)
    vehicle = spot.vehicle 
    spot.remove_vehicle()

def simulate_event(lot):
    event = random.choice(["arrival", "departure"])

    if event == "arrival":
        simulate_arrival(lot)
    else:
        simulate_departure(lot)
