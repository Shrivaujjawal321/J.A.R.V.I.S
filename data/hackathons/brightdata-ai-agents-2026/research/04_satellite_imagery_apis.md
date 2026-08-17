# Satellite Imagery APIs for Alt-Data Investment Brief Agent

## Quick Answer
**Sentinel Hub on CDSE** is primary pick — OAuth2, 10m resolution, any lat/lon, Python SDK in 10 lines, free perpetual tier. Pair with **NASA FIRMS** (free, <60s industrial heat latency) and **NOAA VIIRS Night Lights via Google Earth Engine** (economic activity proxy). Zero-auth fallback: AWS Earth Search STAC.

---

## Decision Matrix

| API | Best For | Auth | Free? | Resolution | Latency | Verdict |
|-----|----------|------|-------|------------|---------|---------|
| **Sentinel Hub (CDSE)** | Cloud-free optical, any AOI | OAuth2 | Free perpetual | 10m (S2) | 3–8s | **Primary** |
| **Google Earth Engine** | NDVI, multi-temporal | Google + GCP | 150 EECU-hr/mo | 10m | 5–15s | Analysis layer |
| **AWS Earth Search STAC** | Raw COG access | None | Fully free | 10m | COG range-req | Zero-auth fallback |
| **Copernicus CDSE OData** | Bulk S2 download | OAuth2 | Free (quota) | 10m | Slow | Use SH instead |
| **Planet Labs** | 3m daily (parking) | API key | E&R: 3000 km²/mo | 3m | <2s | E&R if .edu |
| **NASA GIBS / MODIS** | Macro context | None | Free | 250m-1km | Fast CDN | Viz only |
| **VIIRS Night Lights** | Economic activity | EOG free | Free | 500m | Monthly | Strong China signal |
| **NASA FIRMS** | Industrial heat | Free MAP_KEY | Free | 375m | <60s URT | XOM signal |

---

## Sentinel Hub on CDSE — Primary

**Auth:** Register free at `dataspace.copernicus.eu`. Token URL: `https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token`

```python
from sentinelhub import SHConfig, SentinelHubRequest, DataCollection, MimeType, BBox, CRS, bbox_to_dimensions

config = SHConfig()
config.sh_client_id = "YOUR_CLIENT_ID"
config.sh_client_secret = "YOUR_CLIENT_SECRET"
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

# Cushing OK oil terminals
lat, lon, delta = 36.0, -96.77, 0.005
bbox = BBox(bbox=[lon-delta, lat-delta, lon+delta, lat+delta], crs=CRS.WGS84)
size = bbox_to_dimensions(bbox, resolution=10)

evalscript_rgb = """
//VERSION=3
function setup() { return { input:["B04","B03","B02"], output:{bands:3} }; }
function evaluatePixel(s) { return [3.5*s.B04, 3.5*s.B03, 3.5*s.B02]; }
"""

req = SentinelHubRequest(
    evalscript=evalscript_rgb,
    input_data=[SentinelHubRequest.input_data(
        data_collection=DataCollection.SENTINEL2_L2A.define_from(
            "s2l2a", service_url="https://sh.dataspace.copernicus.eu"),
        time_interval=("2025-01-01","2025-05-01"),
        mosaicking_order="leastCC",
    )],
    responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
    bbox=bbox, size=size, config=config,
)
img = req.get_data()[0]
```

`mosaicking_order="leastCC"` auto-picks most cloud-free scene.

---

## Google Earth Engine

```python
import ee
ee.Authenticate()
ee.Initialize(project="your-gcp-project-id")

aoi = ee.Geometry.Rectangle([-96.80, 35.98, -96.74, 36.02])

s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
      .filterBounds(aoi).filterDate("2025-01-01","2025-05-01")
      .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
      .sort("CLOUDY_PIXEL_PERCENTAGE").first())

ndvi = s2.normalizedDifference(["B8","B4"]).rename("NDVI")

viirs = (ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")
         .filterDate("2025-01-01","2025-04-01").select("avg_rad").median())
nl_stats = viirs.reduceRegion(ee.Reducer.mean(), aoi, scale=500)
```

**Key datasets:** `COPERNICUS/S2_SR_HARMONIZED`, `NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG`

**Pre-generate thumbnails for demo** — `getThumbURL` 5-15s latency unacceptable live.

---

## AWS Earth Search STAC — Zero-Auth

```python
from pystac_client import Client
import rioxarray

catalog = Client.open("https://earth-search.aws.element84.com/v1")
search = catalog.search(
    collections=["sentinel-2-c1-l2a"],
    bbox=[-96.80, 35.98, -96.74, 36.02],
    datetime="2025-01-01/2025-05-01",
    query={"eo:cloud_cover": {"lt": 20}},
    sortby=["-datetime"],
    max_items=3,
)
best = list(search.items())[0]
red = rioxarray.open_rasterio(best.assets["red"].href, overview_level=2)
# overview_level=2 → ~686×686px via range requests, ms not min
```

---

## NASA FIRMS — Industrial Heat / Flaring

VIIRS 375m thermal. **URT latency <60s** for US/Canada. ExxonMobil refineries, natural gas flaring, steel mills = persistent hotspots. `frp` (Fire Radiative Power, MW) = industrial intensity proxy.

```python
import requests, pandas as pd
from io import StringIO

def firms_area(map_key, bbox, source="VIIRS_SNPP_NRT", days=7):
    west, south, east, north = bbox
    url = (f"https://firms.modaps.eosdis.nasa.gov/api/area/csv"
           f"/{map_key}/{source}/{west},{south},{east},{north}/{days}")
    r = requests.get(url, timeout=30)
    return pd.read_csv(StringIO(r.text)) if r.text.strip() else pd.DataFrame()

# XOM Baytown TX refinery
df = firms_area(MAP_KEY, (-95.1, 29.6, -94.8, 29.9))
# frp drops to 0 on shutdown, spikes at full capacity
```

**Rate limit:** 5,000 transactions/10 min — no practical constraint.

---

## VIIRS Night Lights

Monthly cloud-free composites (~500m). Economic activity proxy. China industrial zones, port activity, oil terminals = radiance ∝ operational intensity.

**Via GEE:** `NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG`

**Typical benchmarks [unverified]:**
- Dark rural: 0–2 nW/cm²/sr
- Active oil terminal: 50–200+
- City core: 200–1000+

---

## Area-of-Interest Patterns

**Nominatim (OSM) geocoder:**
```python
def geocode(query):
    r = requests.get("https://nominatim.openstreetmap.org/search",
                     params={"q": query, "format": "json", "limit": 1},
                     headers={"User-Agent": "alt-data-agent/1.0"})
    hit = r.json()[0]
    return float(hit["lat"]), float(hit["lon"])
```

**Pre-built AOIs for demo:**

| Ticker | Site | Lat | Lon | Signal |
|--------|------|-----|-----|--------|
| XOM | Cushing OK tank farm | 36.00 | -96.77 | Tank shadow, NDVI≈0 |
| XOM | Baytown TX refinery | 29.75 | -94.98 | FIRMS FRP |
| WMT | Bentonville AR store | 36.37 | -94.21 | Parking lot density |
| WMT | DC Brooksville FL | 28.52 | -82.39 | Truck dock activity |
| VALE | Carajás mine Brazil | -6.08 | -50.17 | Excavation NDVI |
| China industry | Tangshan steel belt | 39.63 | 118.18 | VIIRS + FIRMS |

---

## Caching Strategy

**Never fetch live during judge demo.**

```python
import hashlib, json
from pathlib import Path

CACHE_DIR = Path("cache/satellite_tiles")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def tile_key(source, lat, lon, date):
    s = json.dumps({"s": source, "lat": lat, "lon": lon, "d": date}, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()[:16]

def get_tile(source, lat, lon, date, fetch_fn, **kw):
    p = CACHE_DIR / f"{source}_{tile_key(source,lat,lon,date)}.png"
    if p.exists(): return p.read_bytes()
    data = fetch_fn(lat, lon, date, **kw)
    p.write_bytes(data)
    return data
```

**Budget:** 10 AOIs × 3 dates × 3 sources × ~200KB ≈ 18MB total — trivially on disk.

**TTL:**
- Demo AOI: no TTL — pre-bake
- FIRMS NRT: 6h
- STAC search: 24h

---

## Sources

- [Sentinel Hub Process API](https://docs.sentinel-hub.com/api/latest/api/process/)
- [sentinelhub-py](https://sentinelhub-py.readthedocs.io/)
- [CDSE Sentinel Hub Notebook](https://documentation.dataspace.copernicus.eu/notebook-samples/sentinelhub/data_download_process_request.html)
- [GEE Auth Guide](https://developers.google.com/earth-engine/guides/auth)
- [GEE Noncommercial Tiers](https://developers.google.com/earth-engine/guides/noncommercial_tiers)
- [VIIRS DNB GEE Catalog](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG)
- [AWS STAC Sentinel-2 Tutorial](https://stacspec.org/en/tutorials/access-sentinel-2-data-aws/)
- [Element84 Earth Search](https://github.com/Element84/earth-search)
- [Planet E&R Program](https://www.planet.com/industries/education-and-research/)
- [NASA GIBS Docs](https://nasa-gibs.github.io/gibs-api-docs/python-usage/)
- [EOG Nighttime Light](https://eogdata.mines.edu/products/vnl/)
- [NASA FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/)

**Confidence: High** (auth + APIs) / **Medium** (exact quota numbers).
