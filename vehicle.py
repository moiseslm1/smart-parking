from datetime import datetime 
class Vehicle:
    def __init__(self, plate_number):
        self.plate_number = plate_number
        self.entry_time = datetime.now()
    def to_dict(self):
        return {
            "plate_number": self.plate_number,
            "entry_time": self.entry_time.isoformat()
        }
        
    def __str__(self):        
        return self.plate_number