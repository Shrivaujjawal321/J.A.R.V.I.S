"""Fare Engine — FastAPI app.

Endpoints:
  GET /api/geocode?q=<text>          → place suggestions (Photon, India-biased)
  GET /api/estimate?from_lat=..&from_lon=..&to_lat=..&to_lon=..
                                     → route (OSRM) + fares for all 5 vehicles
  GET /                              → single-page UI (static/index.html)
  GET /api/health                    → liveness + upstream status

Run: uvicorn app:app --port 8100
"""

from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

import config
import engine

app = FastAPI(title="Fare Engine", version="1.0.0")

STATIC_DIR = Path(__file__).parent / "static"

# Photon/OSRM reject default python client UAs with 403 — identify properly.
HTTP_HEADERS = {"User-Agent": "FareEngine/1.0 (indicative-price estimator)"}

# Simple LRU route cache: same block-to-block query never hits OSRM twice.
_route_cache: OrderedDict[tuple, dict] = OrderedDict()


def _cache_key(from_lat, from_lon, to_lat, to_lon) -> tuple:
    d = config.CACHE_COORD_DECIMALS
    return (round(from_lat, d), round(from_lon, d), round(to_lat, d), round(to_lon, d))


async def _fetch_route(from_lat, from_lon, to_lat, to_lon) -> dict:
    """Road distance + duration via OSRM; haversine fallback if unreachable."""
    key = _cache_key(from_lat, from_lon, to_lat, to_lon)
    if key in _route_cache:
        _route_cache.move_to_end(key)
        return {**_route_cache[key], "cached": True}

    url = (
        f"{config.OSRM_BASE_URL}/route/v1/driving/"
        f"{from_lon},{from_lat};{to_lon},{to_lat}"
        "?overview=full&geometries=geojson"
    )
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT_SECONDS, headers=HTTP_HEADERS) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            raise ValueError(f"OSRM returned {data.get('code')}")
        route = data["routes"][0]
        result = {
            "distance_km": route["distance"] / 1000.0,
            "duration_min": route["duration"] / 60.0,
            "geometry": route["geometry"],
            "source": "osrm",
        }
    except Exception:
        result = engine.fallback_route(from_lat, from_lon, to_lat, to_lon)
        result["geometry"] = None

    _route_cache[key] = result
    if len(_route_cache) > config.CACHE_MAX_ENTRIES:
        _route_cache.popitem(last=False)
    return {**result, "cached": False}


@app.get("/api/geocode")
async def geocode(q: str = Query(..., min_length=2)):
    """Place autocomplete via Photon (free, no key). India-biased."""
    url = f"{config.PHOTON_BASE_URL}/api/"
    params = {"q": q, "limit": 6, "lang": "en"}
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT_SECONDS, headers=HTTP_HEADERS) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Geocoding service unreachable")

    results = []
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        coords = feat.get("geometry", {}).get("coordinates", [None, None])
        country_code = (props.get("countrycode") or "").lower()
        name = props.get("name") or ""
        parts = [name]
        for field in ("city", "state"):
            val = props.get(field)
            if val and val != name:
                parts.append(val)
        results.append({
            "name": name,
            "display": ", ".join(parts),
            "lat": coords[1],
            "lon": coords[0],
            "country": country_code,
        })

    # Bias: Indian results first, keep original relevance order within groups.
    bias = config.GEOCODE_COUNTRY_BIAS
    results.sort(key=lambda r: r["country"] != bias)
    return {"results": results[:6]}


@app.get("/api/estimate")
async def estimate(
    from_lat: float = Query(..., ge=-90, le=90),
    from_lon: float = Query(..., ge=-180, le=180),
    to_lat: float = Query(..., ge=-90, le=90),
    to_lon: float = Query(..., ge=-180, le=180),
    hour: int | None = Query(None, ge=0, le=23),
):
    """Route + indicative fares for all vehicle types."""
    if abs(from_lat - to_lat) < 1e-6 and abs(from_lon - to_lon) < 1e-6:
        raise HTTPException(status_code=400, detail="Pickup and drop are the same point")

    route = await _fetch_route(from_lat, from_lon, to_lat, to_lon)
    if hour is None:
        hour = datetime.now().hour

    fares = engine.estimate_all(route["distance_km"], route["duration_min"], hour)
    band = engine.time_multiplier(hour)

    return {
        "route": {
            "distance_km": round(route["distance_km"], 2),
            "duration_min": round(route["duration_min"], 1),
            "source": route["source"],
            "cached": route["cached"],
            "geometry": route.get("geometry"),
        },
        "time_band": band,
        "hour": hour,
        "fares": fares,
        "disclaimer": "Indicative prices only. Actual fares depend on live demand, traffic and operator.",
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "cache_entries": len(_route_cache)}


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8100)
