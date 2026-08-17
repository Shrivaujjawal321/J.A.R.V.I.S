"""Core fare engine — pure functions, no I/O, fully unit-testable."""

import math

import config


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in km."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def fallback_route(lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
    """Estimate road distance + duration when the routing API is down."""
    dist = haversine_km(lat1, lon1, lat2, lon2) * config.CIRCUITY_FACTOR
    duration_min = dist / config.CITY_AVG_SPEED_KMH * 60.0
    return {"distance_km": dist, "duration_min": duration_min, "source": "estimated"}


def time_multiplier(hour: int) -> dict:
    """Return the multiplier band active at the given local hour."""
    for band in config.TIME_MULTIPLIERS:
        if band["start"] <= hour < band["end"]:
            return {"name": band["name"], "multiplier": band["multiplier"]}
    return {"name": "normal", "multiplier": 1.0}


def vehicle_fare(vehicle_key: str, distance_km: float, duration_min: float, hour: int) -> dict:
    """Fare for one vehicle type. Returns availability + price range."""
    card = config.RATE_CARDS[vehicle_key]

    if card["max_distance_km"] is not None and distance_km > card["max_distance_km"]:
        return {
            "vehicle": vehicle_key,
            "label": card["label"],
            "icon": card["icon"],
            "seats": card["seats"],
            "available": False,
            "reason": f"Not available beyond {card['max_distance_km']:.0f} km",
        }

    per_km = card["per_km"]
    if distance_km > config.OUTSTATION_THRESHOLD_KM:
        # Full rate up to the threshold, discounted rate beyond it.
        base_part = per_km * config.OUTSTATION_THRESHOLD_KM
        extra_part = per_km * config.OUTSTATION_PER_KM_FACTOR * (
            distance_km - config.OUTSTATION_THRESHOLD_KM
        )
        distance_charge = base_part + extra_part
    else:
        distance_charge = per_km * distance_km

    fare = card["base_fare"] + distance_charge + card["per_min"] * duration_min
    fare = max(card["min_fare"], fare)

    band = time_multiplier(hour)
    fare *= band["multiplier"]

    low = round(fare * config.RANGE_LOW)
    high = round(fare * config.RANGE_HIGH)

    return {
        "vehicle": vehicle_key,
        "label": card["label"],
        "icon": card["icon"],
        "seats": card["seats"],
        "available": True,
        "fare_point": round(fare),
        "fare_low": low,
        "fare_high": high,
        "time_band": band["name"],
        "multiplier": band["multiplier"],
    }


def estimate_all(distance_km: float, duration_min: float, hour: int) -> list[dict]:
    """Fares for every vehicle type, cheapest first (unavailable ones last)."""
    results = [vehicle_fare(k, distance_km, duration_min, hour) for k in config.RATE_CARDS]
    return sorted(results, key=lambda r: (not r["available"], r.get("fare_point", 0)))
