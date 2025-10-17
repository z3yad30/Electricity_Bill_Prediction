# Creating a realistic synthetic dataset for electricity bill prediction
# Schema requested by user:
# Governorate, Building type (Apartment, Villa, Office), Rooms, Season, Month, City, temperature, price_per_kwh, tax_rate, consumption_kwh, bill_amount
# Save CSV to /mnt/data and display first rows for preview.
import numpy as np
import pandas as pd
import random
from datetime import datetime
random.seed(42)
np.random.seed(42)

n = 30000  # number of rows

governorates = [
    "Cairo", "Giza", "Alexandria", "Sharqia", "Dakahlia", 
    "Beheira", "Minya", "Asyut", "Luxor", "Suez"
]
cities_by_gov = {
    "Cairo": ["Nasr City", "Heliopolis", "Maadi", "Dokki", "Zamalek", "Zaytoun", "New Cairo"],
    "Giza": ["6th of October", "Sheikh Zayed", "Giza City", "Imbaba", "Haram"],
    "Alexandria": ["Sidi Gaber", "Smouha", "Stanley"],
    "Sharqia": ["Zagazig", "Belbeis", "Abu Hammad", "10th of Ramadan"],
    "Dakahlia": ["Mansoura", "Talkha", "Mit Ghamr", "Sherbin"],
    "Beheira": ["Damanhour", "Kafr El Dawwar"],
    "Minya": ["Minya City", "Beni Mazar", "Maghagha"],
    "Asyut": ["Asyut City", "Manfalut", "Abnoub"],
    "Luxor": ["Luxor City", "El Qurna", "Esna"],
    "Suez": ["Suez City", "Ain Sokhna", "El Galala"]
}

building_types = ["Apartment", "Villa", "Office"]
months = list(range(1,13))

def season_from_month(m):
    if m in [12,1,2]: return "Winter"
    if m in [3,4,5]: return "Spring"
    if m in [6,7,8]: return "Summer"
    return "Autumn"

# base temperature per governorate (rough average) and seasonal swing
base_temp = {
    "Cairo": 25, "Giza": 25, "Alexandria": 22, "Sharqia": 24, "Dakahlia": 24,
    "Beheira": 23, "Minya": 27, "Asyut": 28, "Luxor": 30, "Suez": 29
}

# base price per kWh by governorate (EGP-like fictional values) and building type multiplier
base_price = {
    "Cairo": 0.85, "Giza": 0.82, "Alexandria": 0.80, "Sharqia": 0.78, "Dakahlia": 0.77,
    "Beheira": 0.76, "Minya": 0.75, "Asyut": 0.74, "Luxor": 0.73, "Suez": 0.79
}
building_price_multiplier = {"Apartment": 1.0, "Villa": 1.15, "Office": 1.25}

# tax_rate by governorate (example 0-20%)
tax_base = {
    "Cairo": 0.14, "Giza": 0.12, "Alexandria": 0.13, "Sharqia": 0.11, "Dakahlia": 0.10,
    "Beheira": 0.10, "Minya": 0.09, "Asyut": 0.08, "Luxor": 0.07, "Suez": 0.12
}

rows = []
for i in range(n):
    gov = random.choice(governorates)
    city = random.choice(cities_by_gov[gov])
    btype = random.choices(building_types, weights=[0.7, 0.15, 0.15])[0]  # more apartments
    # rooms: apartments typically 1-4, villas higher, offices variable
    if btype == "Apartment":
        rooms = np.random.choice(range(1,6), p=[0.25,0.35,0.25,0.10,0.05])
    elif btype == "Villa":
        rooms = np.random.choice(range(3,10), p=np.linspace(1,0.2,7)/np.linspace(1,0.2,7).sum())
    else:
        rooms = np.random.choice(range(1,8), p=np.linspace(0.4,0.1,7)/np.linspace(0.4,0.1,7).sum())
    month = random.choice(months)
    season = season_from_month(month)
    # temperature = base + seasonal + noise
    seasonal_adjust = {"Winter": -6, "Spring": 0, "Summer": 6, "Autumn": 0}[season]
    temp = base_temp[gov] + seasonal_adjust + np.random.normal(0,2)
    # price per kwh with some noise and building multiplier
    price = base_price[gov] * building_price_multiplier[btype] * (1 + np.random.normal(0,0.03))
    tax = tax_base[gov] * (1 + np.random.normal(0,0.05))
    # consumption_kwh: base by building type and rooms and temp/season effects
    # Apartments: base 200 kWh/month per room, villas higher, offices different pattern
    if btype == "Apartment":
        base_cons = 100 + 60*rooms
    elif btype == "Villa":
        base_cons = 250 + 90*rooms
    else:  # Office
        base_cons = 300 + 50*rooms
    # seasonal modifier: more in summer if hot, more in winter if cold (heating)
    if season == "Summer":
        season_factor = 1 + max(0, (temp - 28)) * 0.02
    elif season == "Winter":
        season_factor = 1 + max(0, (18 - temp)) * 0.02
    else:
        season_factor = 1.0
    # random household behavior noise
    consum = base_cons * season_factor * np.random.normal(1,0.12)
    consum = max(20, consum)  # floor
    # bill amount
    bill = consum * price * (1 + tax)
    rows.append({
        "governorate": gov,
        "building_type": btype,
        "rooms": int(rooms),
        "season": season,
        "month": int(month),
        "city": city,
        "temperature": round(float(temp),2),
        "price_per_kwh": round(float(price),4),
        "tax_rate": round(float(tax),4),
        "consumption_kwh": round(float(consum),2),
        "bill_amount": round(float(bill),2)
    })

df = pd.DataFrame(rows)
# Save CSV

for idx in df.index:
    if (idx + 1) % 300 == 0:
        df.at[idx, 'month'] = None
    if (idx + 1) % 120 == 0:
        df.at[idx, 'season'] = None
    if (idx + 1) % 1000 == 0:
        df.at[idx, 'temperature'] = None
    if (idx + 1) % 1500 == 0:
        df.at[idx, 'price_per_kwh'] = None
    if (idx + 1) % 200 == 0:
        df.at[idx, 'city'] = None
    if (idx + 1) % 70 == 0:
        df.at[idx, 'building_type'] = None
    if (idx + 1) % 500 == 0:
        df.at[idx, 'consumption_kwh'] = None

out_path = "Raw_Data.csv"
df.to_csv(out_path, index=False)

# Display top rows to user
print(df.head(10))

print(f"Saved synthetic CSV to: {out_path}")