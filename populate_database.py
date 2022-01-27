import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookings.settings")
import django
django.setup()

import json
from random import random
from core.models import Hotel, Photo

print("Populating database...")
f = open("hotels.json")
data = json.load(f)
f.close()

for name in data.keys():
    # accessing one hotel row
    hotel_row = data[name]
    coord = hotel_row[1]
    longitude, latitude = coord.split(",")
    longitude = float(longitude)
    latitude = float(latitude)
    price = hotel_row[2]

    # list of photo urls
    photo_urls = hotel_row[3]

    #pool, room, breakfast,
    # threshold for the facilities
    fac = [0.8, 0.6, 0.7, 0.5, 0.1, 0.5, 0.6, 0.2]

    # this will be filled with true, false
    choices = []

    for i in range(0, len(fac)):
        if fac[i] > random():
            choices.append(True)
        else:
            choices.append(False)

    h = Hotel(
        name=name, address=hotel_row[0], longitude=longitude, latitude=latitude, price=price)

    h.smoking_rooms, h.pool, h.gym, h.room_service, h.spa, h.breakfast, h.free_wifi, h.dry_cleaning = choices
    h.save()
    choices = []
    # traversing through the photo url list
    for photo in photo_urls:
        p = Photo(url=photo, hotel=h)
        p.save()
print("Done!")