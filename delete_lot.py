from DataBase.database import delete_lot

lot_id = int(input("Enter lot ID to delete: "))

confirm = input(f"Are you sure you want to delete lot {lot_id}? (y/n): ")

if confirm.lower() == "y":
    delete_lot(lot_id)
    print("Lot deleted!")
else:
    print("Deletion cancelled.")