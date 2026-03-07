import random
import string 
from datetime import datetime 
class Vehicle:
    def __init__(self, plate_number=None):
        if plate_number is None:
            self.plate_number = self.generate_plate()
        else:
            self.plate_number = plate_number

        self.entry_time = datetime.now()
        self.exit_time = None

    @staticmethod
    def generate_plate():
        letters = '',join(random.choices(string.ascii_uppercase, k=3))
        numbers = '',join(random.choices(string.digits, k=3))
        return f"{letters}-{numbers}"
    
    def leave(self):
        self.exit_time = datetime.now()
    
    def to_dict(self):
        