import csv
import random
from faker import Faker

fake = Faker()

with open("sample_nndr.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "PropertyID", "Address", "Postcode", "RateableValue", "Description",
        "Latitude", "Longitude", "CurrentRatingStatus", "LastBilledDate"
    ])
    for i in range(1000):
        lat = 52.2 + random.uniform(-0.05, 0.05)  # Around Cambridge
        lon = 0.12 + random.uniform(-0.05, 0.05)
        writer.writerow([
            1000 + i,
            fake.street_address(),
            fake.postcode(),
            random.randint(10000, 50000),
            random.choice(["Shop", "Office", "Warehouse", "Restaurant"]),
            round(lat, 6),
            round(lon, 6),
            random.choice(["Rated", "Not Rated"]),
            fake.date_between(start_date="-2y", end_date="today")
        ])