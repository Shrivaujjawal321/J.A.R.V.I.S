# Fare Engine

**Indicative ride-price estimator — bike · auto · cab (mini) · sedan · SUV**

Give a pickup and a drop location, get an indicative price range for all five
vehicle types, with the route drawn on a map. No API keys, no accounts, no cost.

## 3-Command Install

```bash
make setup    # venv + dependencies
make test     # 12 unit tests on the fare engine
make run      # http://127.0.0.1:8100
```

## How it works

```
pickup / drop text
   → Photon geocoding (free, India-biased autocomplete)
   → OSRM routing (free) → road distance km + duration min
   → fare engine (config.py rate cards)
   → 5 vehicle cards with indicative price ranges
```

**Fare formula per vehicle:**

```
fare  = max( min_fare , base_fare + per_km × distance + per_min × duration )
fare  = fare × time_multiplier      # peak 1.2× · night 1.1× · normal 1.0×
range = [ fare × 0.95 , fare × 1.15 ]
```

## Built-in robustness

| Case | Behaviour |
|------|-----------|
| OSRM unreachable | Falls back to haversine × 1.3 circuity, duration from 22 km/h city speed. UI shows an "estimated" badge. |
| Very short ride | `min_fare` clamp per vehicle |
| Ride > 50 km | Outstation: per-km rate drops 15% beyond 50 km |
| Ride > 40 km | Bike and auto marked "Not available" (realistic) |
| Repeated route | LRU cache keyed on ~11 m coordinate blocks — OSRM hit once |
| Peak / night hours | 08–11 & 17–21 → ×1.2 · 23–05 → ×1.1 |

## Calibration

All numbers live in `config.py` — rate cards, multipliers, thresholds.
Recalibrating for another city means editing that one file.

## Stack

FastAPI + httpx backend · vanilla-JS single page UI · Leaflet map ·
Photon (geocoding) · OSRM (routing) · pytest.

## API

```
GET /api/geocode?q=<text>                          → place suggestions
GET /api/estimate?from_lat&from_lon&to_lat&to_lon  → route + 5 fares
GET /api/health                                    → liveness
```

> Prices are indicative only. Actual fares depend on live demand, traffic and operator.
