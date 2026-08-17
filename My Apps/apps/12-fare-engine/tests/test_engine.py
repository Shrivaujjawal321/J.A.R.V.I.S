"""Unit tests for the pure fare engine (no network)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
import engine


def test_haversine_known_distance():
    # Connaught Place → IGI Airport (Delhi) straight line ≈ 13-16 km
    d = engine.haversine_km(28.6315, 77.2167, 28.5562, 77.1000)
    assert 13 < d < 16


def test_fallback_route_applies_circuity():
    r = engine.fallback_route(28.6315, 77.2167, 28.5562, 77.1000)
    straight = engine.haversine_km(28.6315, 77.2167, 28.5562, 77.1000)
    assert abs(r["distance_km"] - straight * config.CIRCUITY_FACTOR) < 0.01
    assert r["duration_min"] > 0
    assert r["source"] == "estimated"


def test_min_fare_clamp_short_ride():
    # 0.3 km bike ride must clamp to min fare, not base+per_km*0.3
    f = engine.vehicle_fare("bike", 0.3, 2, hour=14)
    assert f["available"]
    assert f["fare_point"] == round(config.RATE_CARDS["bike"]["min_fare"])


def test_normal_ride_formula():
    # 10 km, 30 min sedan at normal hour: 50 + 16*10 + 1.75*30 = 262.5
    f = engine.vehicle_fare("sedan", 10, 30, hour=14)
    assert f["fare_point"] == 262 or f["fare_point"] == 263
    assert f["multiplier"] == 1.0


def test_peak_multiplier_applied():
    normal = engine.vehicle_fare("cab", 10, 30, hour=14)
    peak = engine.vehicle_fare("cab", 10, 30, hour=9)
    assert peak["multiplier"] == 1.2
    assert peak["fare_point"] > normal["fare_point"]


def test_night_multiplier_applied():
    f = engine.vehicle_fare("auto", 5, 15, hour=23)
    assert f["multiplier"] == 1.1
    f2 = engine.vehicle_fare("auto", 5, 15, hour=2)
    assert f2["multiplier"] == 1.1


def test_bike_unavailable_beyond_cap():
    f = engine.vehicle_fare("bike", 45, 90, hour=14)
    assert not f["available"]
    f2 = engine.vehicle_fare("auto", 45, 90, hour=14)
    assert not f2["available"]
    f3 = engine.vehicle_fare("suv", 45, 90, hour=14)
    assert f3["available"]


def test_outstation_discount_beyond_threshold():
    # 60 km SUV: full per-km up to 50, 15% off for the last 10
    f = engine.vehicle_fare("suv", 60, 80, hour=14)
    card = config.RATE_CARDS["suv"]
    expected = (
        card["base_fare"]
        + card["per_km"] * 50
        + card["per_km"] * config.OUTSTATION_PER_KM_FACTOR * 10
        + card["per_min"] * 80
    )
    assert abs(f["fare_point"] - expected) <= 1


def test_range_band_around_point():
    f = engine.vehicle_fare("sedan", 10, 30, hour=14)
    assert f["fare_low"] < f["fare_point"] < f["fare_high"]
    assert f["fare_low"] == round(f["fare_point"] / 1.0 * 0.95) or f["fare_low"] > 0


def test_estimate_all_sorted_cheapest_first():
    results = engine.estimate_all(8, 25, hour=14)
    available = [r for r in results if r["available"]]
    prices = [r["fare_point"] for r in available]
    assert prices == sorted(prices)
    assert available[0]["vehicle"] == "bike"


def test_estimate_all_unavailable_last():
    results = engine.estimate_all(45, 90, hour=14)
    flags = [r["available"] for r in results]
    # once False starts, no True follows
    assert flags == sorted(flags, reverse=True)


def test_all_vehicles_present():
    results = engine.estimate_all(10, 30, hour=14)
    assert {r["vehicle"] for r in results} == set(config.RATE_CARDS.keys())
