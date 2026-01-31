#variables 
spots_available = 10
lot_name = "Main Parking Lot"
#lists and dictionaries 
parking_spots = [
    {"id": 1, "occupied": False},
    {"id": 2, "occupied": True}
]
#functions
def count_available(spots):
    count = 0
    for spot in spots:
        if not spot["occupied"]:
            count += 1
    return count
#if statements
if spot["occupied"]:
    print("Spot is taken")
else:
    print("Spot is available")
