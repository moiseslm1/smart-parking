from DataBase.database import get_all_lots

lots = get_all_lots()

for lot in lots:
    print(dict(lot))