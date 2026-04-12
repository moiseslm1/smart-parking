# add_lot.py
from DataBase.database import add_lot

add_lot(
    lot_name    = "24 Hour Fitness",
    total_spots = 45,
    lat         = 33.8901,
    lng         = -118.1100,
    zip_code    = "90241",
    address     = "1234 Main St, Downey, CA"
)

print("Lot added!")