# AIS & Maritime Data Sources for Alt-Data Investment Agent

## Quick Answer

Best zero-cost AIS stack: **AISstream.io** (free real-time WebSocket), **MarineCadastre/NOAA** (free US GeoParquet historical), **IMF PortWatch** (free global port congestion). Commercial Kpler (absorbed MarineTraffic + FleetMon + Spire 2023–2025) costs $50K–$200K+/yr [unverified] — their existence is the pitch framing, not implementation.

---

## Market Consolidation Context

Kpler acquired MarineTraffic, FleetMon, Spire Maritime between 2023–2025 [unverified — worldwideais.org]. Unified as "Kpler AIS" Sep 2025. MarineTraffic's API → enterprise-only. The "monopoly" framing makes a free-stack agent compelling.

---

## AISstream.io — Best Free Real-Time

Free globally-aggregated AIS WebSocket. GitHub OAuth signup, no credit card.

**Endpoint:** `wss://stream.aisstream.io/v0/stream`

```python
import asyncio, websockets, json

async def stream_tankers_la():
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ws:
        await ws.send(json.dumps({
            "APIKey": "<AISSTREAM_KEY>",
            "BoundingBoxes": [[[33.5, -118.5], [34.0, -117.8]]],  # LA/LB
            "FilterMessageTypes": ["PositionReport", "ShipStaticData"]
        }))
        async for raw in ws:
            msg = json.loads(raw)
            meta = msg.get("MetaData", {})
            if 80 <= meta.get("ShipType", 0) <= 89:
                print(f"TANKER | {meta['MMSI']} | {meta['latitude']:.4f},{meta['longitude']:.4f}")

asyncio.run(stream_tankers_la())
```

**Coverage:** Primarily terrestrial AIS — gaps in open ocean.

---

## MarineCadastre.gov (NOAA) — Best Free Historical

Free NOAA/BOEM. US coastal/EEZ only. GeoParquet 2024–2025 at Azure blob. No API key.

```python
import duckdb

conn = duckdb.connect()
df = conn.execute("""
    SELECT MMSI, VesselName, LAT, LON, SOG, BaseDateTime, Destination
    FROM read_parquet(
        'https://ocmgeodatastor1.blob.core.windows.net/marinecadastre/aistrack/AIS_2025_01.parquet'
    )
    WHERE VesselType BETWEEN 80 AND 89
      AND LAT BETWEEN 29.5 AND 30.0
      AND LON BETWEEN -95.2 AND -94.8    -- Houston Ship Channel
    ORDER BY BaseDateTime DESC LIMIT 1000
""").df()
```

Note: Cushing OK is landlocked. Proxy = tanker accumulation at Houston Ship Channel (29.7°N, 95.0°W) — primary feeder for Cushing-bound crude.

---

## IMF PortWatch — Best Free Port Congestion

Free at `portwatch.imf.org`. 2,065 ports, 28 chokepoints (Suez, Hormuz, Panama, Malacca). Daily port call counts + import/export tons. Updated weekly Tuesdays 9 AM ET. Based on UN Global Platform tracking 90,000 ships.

```python
import pandas as pd

PORT_URL = "https://portwatch.imf.org/datasets/75619cb86e5f4beeb7dab9629d861acf_0.geojson"
gdf = pd.read_json(PORT_URL)
la = gdf[gdf['portname'].str.contains('Los Angeles|Long Beach', na=False)]
# Columns: portname, iso3, date, calls_total, trade_import_ton_est, trade_export_ton_est
```

---

## Other Sources

**Global Fishing Watch** — Free non-commercial. 110M+ AIS messages/day, 70K vessels. APIs: 4Wings, Vessels, Events (port visits, AIS-off). `pip install gfwr`. Limit: ~96h delayed.

**AISHub** — Free but requires running your own NMEA AIS receiver (~$25 RTL-SDR hardware). Impractical for hackathon.

**Spire Maritime (now Kpler)** — Enterprise satellite AIS, open ocean coverage. $2K–10K/mo estimated [unverified].

**Datalastic** — Mid-tier paid. Trial €9 → €199/mo Starter (20K req) → €679/mo Unlimited. If AISstream gaps problem at demo, Starter is next step.

**BrightData Web Unlocker** — For MarineTraffic/VesselFinder anti-bot bypass. ~$3 per 1,000 successful responses.

---

## Investment Signal Map

| Equity Signal | Geofence | AIS Pattern | Source |
|--------------|----------|-------------|--------|
| XOM/CVX crude supply | Ras Tanura: 26.4-27.0°N, 49.8-50.5°E | VLCC accumulation | AISstream |
| XOM/CVX Cushing inventory | Houston: 29.5-30.0°N, 95.2-94.8°W | Tanker discharge rate | AISstream + MarineCadastre |
| FDX/UPS port congestion | LA/LB: 33.5-34.0°N, 118.5-117.8°W | Container anchor queue | AISstream + PortWatch |
| MAERSK Shanghai throughput | Yangshan: 30.5-30.7°N, 121.9-122.3°E | Container count + dwell | AISstream |
| Natural gas (Henry Hub) | Sabine Pass TX: 29.7°N, 93.9°W | LNG carrier (type 84) | AISstream |
| Geopolitical oil risk | Strait of Hormuz: 26.0-26.8°N, 56.0-57.0°E | Tanker transit drop | PortWatch |
| Sanctions evasion | Bering / STS zones | Dark vessel (AIS-off) | GFW Events |

---

## AIS Vessel Type Codes

```
70-79  = Cargo (containers)
80     = Tanker (general)
81-83  = Tanker, hazardous A/B/C
84     = Tanker (LNG carriers often here)
85-88  = Tanker (reserved)
89     = Tanker, other
```

---

## Recommended Hackathon Stack

**Phase 1 (zero API cost):**
- AISstream.io live tanker + container stream
- MarineCadastre GeoParquet via DuckDB
- IMF PortWatch CSV weekly

**Phase 2 (demo polish, minimal cost):**
- GFW Events API port visits
- BrightData Web Unlocker for vessel metadata (~$1.50/day)

**Phase 3 (pitch upgrade path):**
- Datalastic Starter (€199/mo)
- Kpler/Vortexa framing — "this is what you're replacing"

---

## Sources

- [MarineTraffic API](https://servicedocs.marinetraffic.com/)
- [AISstream.io Docs](https://aisstream.io/documentation)
- [MarineCadastre AccessAIS](https://marinecadastre.gov/accessais/)
- [IMF PortWatch](https://portwatch.imf.org/)
- [GFW APIs](https://globalfishingwatch.org/our-apis/)
- [worldwideais.org Provider Map](https://www.worldwideais.org/post/ais-data-providers-in-2026-who-s-independent-who-s-not-and-why-it-matters)
- [BrightData Web Unlocker](https://brightdata.com/products/web-unlocker)
- [Datalastic Pricing](https://datalastic.com/pricing/)
- [USCG AIS Guide](https://www.navcen.uscg.gov/sites/default/files/pdf/AIS/AISGuide.pdf)
- [Kpler Maritime](https://www.kpler.com/product/maritime/enterprise-plan)
- [Vortexa](https://www.vortexa.com/)

**Confidence: High** (free sources, official docs) / **Medium** (enterprise pricing estimates).
