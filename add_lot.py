# add_lot.py
from DataBase.database import add_lot

add_lot(
    lot_name    = "CSUDH Parking Lot 2",
    total_spots = 240,
    lat         = 33.86642,
    lng         = -118.2534,
    zip_code    = "90746",
    address     = "1000 E Victoria St, Carson, CA",
    category    = "other"
)

print("Lot added!")