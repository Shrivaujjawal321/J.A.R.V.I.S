"""Fare Engine — all tunable numbers live here.

Rate cards are calibrated for Indian metro cities (2026).
Edit this file to re-calibrate for a specific city — nothing else changes.
"""

# Per-vehicle rate cards.
# fare = max(min_fare, base_fare + per_km * distance_km + per_min * duration_min)
RATE_CARDS = {
    "bike": {
        "label": "Bike",
        "icon": "🏍️",
        "seats": 1,
        "base_fare": 15.0,
        "min_fare": 25.0,
        "per_km": 7.0,
        "per_min": 0.75,
        "max_distance_km": 40.0,   # beyond this the vehicle is not offered
    },
    "auto": {
        "label": "Auto",
        "icon": "🛺",
        "seats": 3,
        "base_fare": 25.0,
        "min_fare": 35.0,
        "per_km": 11.0,
        "per_min": 1.0,
        "max_distance_km": 40.0,
    },
    "cab": {
        "label": "Cab (Mini)",
        "icon": "🚕",
        "seats": 4,
        "base_fare": 40.0,
        "min_fare": 60.0,
        "per_km": 13.0,
        "per_min": 1.5,
        "max_distance_km": None,
    },
    "sedan": {
        "label": "Sedan",
        "icon": "🚗",
        "seats": 4,
        "base_fare": 50.0,
        "min_fare": 80.0,
        "per_km": 16.0,
        "per_min": 1.75,
        "max_distance_km": None,
    },
    "suv": {
        "label": "SUV",
        "icon": "🚙",
        "seats": 6,
        "base_fare": 70.0,
        "min_fare": 110.0,
        "per_km": 20.0,
        "per_min": 2.0,
        "max_distance_km": None,
    },
}

# Time-of-day multipliers (24h local time, [start, end) ranges).
# First match wins; default 1.0.
TIME_MULTIPLIERS = [
    {"name": "morning_peak", "start": 8, "end": 11, "multiplier": 1.2},
    {"name": "evening_peak", "start": 17, "end": 21, "multiplier": 1.2},
    {"name": "night", "start": 23, "end": 24, "multiplier": 1.1},
    {"name": "late_night", "start": 0, "end": 5, "multiplier": 1.1},
]

# Indicative price band around the point estimate.
RANGE_LOW = 0.95
RANGE_HIGH = 1.15

# Rides longer than this get the outstation per-km discount.
OUTSTATION_THRESHOLD_KM = 50.0
OUTSTATION_PER_KM_FACTOR = 0.85  # per-km rate drops 15% beyond threshold

# Fallback estimation when the routing API is unreachable.
CIRCUITY_FACTOR = 1.3          # road distance ≈ haversine * this
CITY_AVG_SPEED_KMH = 22.0      # used to estimate duration in fallback mode

# External services (free, no API key).
OSRM_BASE_URL = "https://router.project-osrm.org"
PHOTON_BASE_URL = "https://photon.komoot.io"
GEOCODE_COUNTRY_BIAS = "in"    # bias autocomplete results toward India
HTTP_TIMEOUT_SECONDS = 6.0

# Route cache: coordinates rounded to this many decimals form the cache key
# (4 decimals ≈ 11 m — same block hits the same cache entry).
CACHE_COORD_DECIMALS = 4
CACHE_MAX_ENTRIES = 2000
