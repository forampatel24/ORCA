"""Lightning live feed - Blitzortung public JSON + CAPE proxy fallback.

Blitzortung publishes a free public real-time lightning map feed used by
lightningmaps.org. The JSON endpoint requires no key and returns recent
strikes with lat/lon/time. Used directly when reachable; the response is
cached by the caller.

Fallback (no extra key): convective CAPE/precipitation from Open-Meteo Archive
for Mumbai gives a thunderstorm-risk flag without inventing strikes. Only real
strike positions are returned as 'strikes' - the fallback contributes a risk
flag instead of fake positions.

No mock strike positions are ever generated.
"""
import httpx
import re
from datetime import datetime, timezone
from typing import List, Dict, Any

BLITZORTUNG_CANDIDATES = [
    # Public JSON dumps used by lightningmaps.org - no key, try in order
    "https://data.blitzortung.org/Data_1/Protected/Strikes.json",
    "https://blitzortung.org/Data/Strikes.json",
]


async def fetch_lightning_maharashtra(bbox=(71.8, 15.5, 74.5, 20.5)) -> Dict[str, Any]:
    min_lon, min_lat, max_lon, max_lat = bbox
    strikes = []
    source = None
    last_error = None
    for url in BLITZORTUNG_CANDIDATES:
        try:
            async with httpx.AsyncClient(timeout=20, headers={"User-Agent": "ORCA-Mumbai/1.0"}) as c:
                r = await c.get(url)
                if r.status_code != 200 or len(r.content) < 100:
                    last_error = f"{r.status_code}"
                    continue
                text = r.text
                # File is concatenated JSON or JSON-lines; extract lat/lon pairs
                # Format variants: {"lat":..., "lon":..., "time":...} or [lon, lat, ...]
                for m in re.finditer(r'"lat"\s*:\s*([\d.-]+)[^}]*?"lon"\s*:\s*([\d.-]+)', text):
                    lat, lon = float(m.group(1)), float(m.group(2))
                    if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                        strikes.append({"lat": lat, "lon": lon})
                    if len(strikes) >= 50:
                        break
                if strikes:
                    source = url
                    break
                # Try array format [lon, lat]
                for m in re.finditer(r'\[\s*([\d.-]+)\s*,\s*([\d.-]+)\s*,', text):
                    lon, lat = float(m.group(1)), float(m.group(2))
                    if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                        strikes.append({"lat": lat, "lon": lon})
                    if len(strikes) >= 50:
                        break
                if strikes:
                    source = url
                    break
                last_error = "no strikes in bbox"
        except Exception as e:
            last_error = str(e)[:120]
            continue
    # If no strikes in window, do not invent any. Return honest empty + status.
    # Strikes outside the window are irrelevant to Maharashtra ops.
    return {"strikes": strikes[:50], "source": source, "error": last_error,
            "fetched_at": datetime.now(timezone.utc).isoformat()}


def cape_thunderstorm_risk() -> Dict[str, Any]:
    """Day's thunderstorm risk from real CAPE/precip at Mumbai (Open-Meteo)."""
    import httpx as _hx
    try:
        r = _hx.get("https://api.open-meteo.com/v1/forecast", timeout=15,
                     params={"latitude": 19.076, "longitude": 72.877,
                             "hourly": "cape,precipitation",
                             "forecast_days": 1, "timezone": "UTC"})
        j = r.json()
        capes = (j.get("hourly", {}) or {}).get("cape", []) or []
        precs = (j.get("hourly", {}) or {}).get("precipitation", []) or []
        max_cape = max([c for c in capes if c is not None], default=0)
        max_prec = max([p for p in precs if p is not None], default=0)
        level = "LOW"
        if max_cape > 1000 and max_prec > 2:
            level = "HIGH"
        elif max_cape > 600 or max_prec > 4:
            level = "MODERATE"
        return {"cape_max_jkg": round(float(max_cape), 1) if max_cape else 0,
                "precip_max_mm": round(float(max_prec), 2),
                "risk": level,
                "source": "Open-Meteo forecast cape+precip Mumbai"}
    except Exception as e:
        return {"risk": "UNKNOWN", "error": str(e)[:120]}
