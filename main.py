from fastapi import FastAPI
from datetime import datetime, timedelta
import random

app = FastAPI()

# Simulated bus data with stops
buses = [
    {
        "bus_id": 1,
        "route": "Gondia-Nagpur",
        "type": "AC",
        "stops": [
            {"name": "Gondia", "lat": 21.145, "lon": 79.088},
            {"name": "Amgaon", "lat": 21.146, "lon": 79.089},
            {"name": "Nagbhid", "lat": 21.147, "lon": 79.090},
            {"name": "Nagpur", "lat": 21.148, "lon": 79.091},
        ],
        "schedule": ["2025-10-15", "2025-10-16"],
        "departure": "08:00",
    },
    {
        "bus_id": 2,
        "route": "Gondia-Nagpur",
        "type": "Non-AC",
        "stops": [
            {"name": "Gondia", "lat": 21.146, "lon": 79.089},
            {"name": "Tumsar", "lat": 21.147, "lon": 79.090},
            {"name": "Nagpur", "lat": 21.148, "lon": 79.091},
        ],
        "schedule": ["2025-10-15", "2025-10-16"],
        "departure": "10:00",
    },
]

@app.get("/search_buses")
def search_buses(origin: str, destination: str, date: str):
    result = []
    for bus in buses:
        stop_names = [s["name"] for s in bus["stops"]]
        if origin in stop_names and destination in stop_names and stop_names.index(origin) < stop_names.index(destination):
            if date in bus["schedule"]:
                result.append({
                    "bus_id": bus["bus_id"],
                    "route": bus["route"],
                    "type": bus["type"],
                    "departure": bus["departure"],
                    "stops": stop_names
                })
    return {"buses": result}

@app.get("/bus_location")
def bus_location(bus_id: int = None):
    bus_locations = []
    for bus in buses:
        if bus_id is not None and bus["bus_id"] != bus_id:
            continue

        # Simulate movement
        bus["stops"][0]["lat"] += random.uniform(0.0001, 0.001)
        bus["stops"][0]["lon"] += random.uniform(0.0001, 0.001)
        lat = bus["stops"][0]["lat"]
        lon = bus["stops"][0]["lon"]

        # ETA
        dep_time = datetime.strptime(bus["departure"], "%H:%M")
        scheduled_arrival = datetime.combine(datetime.today(), dep_time.time())
        if scheduled_arrival < datetime.now():
            scheduled_arrival += timedelta(days=1)
        eta_minutes = int((scheduled_arrival - datetime.now()).total_seconds() / 60)

        status = f"🕒 Arriving in {eta_minutes} min" if eta_minutes >= 0 else f"🚨 Delayed by {-eta_minutes} min"

        # Next stop
        next_stop = bus["stops"][1]["name"] if len(bus["stops"]) > 1 else bus["stops"][0]["name"]

        bus_locations.append({
            "bus_id": bus["bus_id"],
            "route": bus["route"],
            "type": bus["type"],
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "eta": eta_minutes,
            "status": status,
            "next_stop": next_stop,
            "stops": bus["stops"]  # include all stops for route line
        })
    return {"bus_locations": bus_locations}

@app.get("/bus_stops")
def bus_stops(bus_id: int):
    for bus in buses:
        if bus["bus_id"] == bus_id:
            return {"bus_id": bus_id, "stops": [s["name"] for s in bus["stops"]]}
    return {"error": "Bus not found"}
