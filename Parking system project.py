lot_id = 123456
name = "Prking lot 1"
total_spots = 20
zip_code = 90255 

#parking spots

spot_id = None
occupied= None
lot_updated= None
#list of parking spots
parking_spots = [    
{"id": 1, "occupied": False},
{"id": 2, "occupied": True},
]
def count_available(spots):
    count = 0
    for spot in spots:
        if not spot["occupied"]:
            count +=1
    return count
if spot["occupied"]:
    print("Spot is occupied")
else:
    print("Spot is available")
    
