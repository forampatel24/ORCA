"""INCOIS + RSMC hazard connectors -> marine_hazards.

Cyclone: RSMC New Delhi daily tropical outlook PDF (rsmc.pdf, always latest).
  Parsed via PyMuPDF. Stores geometry at reported Lat/Lon, Maharashtra-aware
  status (always stored; severity derived from system type / cyclogenesis prob).

Ocean State: INCOIS OSF forecast pages. Maritime-specific; high-wave / rough-sea
  advisory text when present is stored as hazard polygon (Maharashtra bbox) so
  the map can show it. This connector scrapes the Maharashtra region path when
  INCOIS publishes one — honest empty when there is no advisory.

Wave-threshold: deterministic auto-flags from local ocean_observations
  wave_height, without waiting for an upstream advisory.

No mocks — returns [] when there is no advisory / no threshold breach,
and the existing row is expired.
"""
import re
import httpx
import psycopg
import structlog
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from app.database.connection import psycopg_conninfo
from app.config.mumbai import MUMBAI_EXTENDED_BBOX

log = structlog.get_logger()

RSMC_PDF = "https://rsmcnewdelhi.imd.gov.in/images/bulletin/rsmc.pdf"
OSF_MAHARASHTRA_CANDIDATES = [
    "https://incois.gov.in/portals/osf/maharastra.html",
    "https://incois.gov.in/portals/osf/maharashtra.html",
    "https://incois.gov.in/oceanservices/osfforecast.jsp?region=MAHARASHTRA",
]

SYSTEM_RANK = {
    "low pressure area": 0, "well marked low pressure area": 1,
    "depression": 2, "deep depression": 3, "cyclonic storm": 4,
    "severe cyclonic storm": 5, "very severe cyclonic storm": 6,
    "extremely severe cyclonic storm": 7, "super cyclonic storm": 8,
}
SEVERITY = {0: "LOW", 1: "LOW", 2: "MODERATE", 3: "MODERATE", 4: "HIGH", 5: "HIGH", 6: "VERY_HIGH", 7: "VERY_HIGH", 8: "VERY_HIGH"}


def _parse_rsmc_pdf(pdf_bytes: bytes) -> Dict[str, Any]:
    import pymupdf
    import io as _io
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(p.get_text() for p in doc)
    dated = None
    m = re.search(r"DATED\s+([\d.]+)", text, re.I)
    if m:
        dated = m.group(1)
    # System lat/lon: "22.5°N and longitude 88.3°E"
    lat = lon = None
    mm = re.search(r"latitude\s*([\d.]+)\s*°N\s*and\s*longitude\s*([\d.]+)\s*°E", text, re.I)
    if mm:
        lat, lon = float(mm.group(1)), float(mm.group(2))
    # Pressure
    pressure = None
    pm = re.search(r"central pressure is\s*([\d.]+)\s*hPa", text, re.I)
    if pm:
        pressure = float(pm.group(1))
    # Max sustained wind
    wind_kt = None
    wm = re.search(r"maximum sustained wind speed is\s*([\d.]+)\s*kt", text, re.I)
    if wm:
        wind_kt = float(wm.group(1))
    # System phrase (use lowest matching phrase first by longest key)
    system = None
    low = text.lower()
    for k in sorted(SYSTEM_RANK, key=lambda s: -len(s)):
        if k in low:
            system = k
            break
    # Cyclogenesis probability row (pick highest non-NIL)
    prob = "NIL"
    pm2 = re.search(r"PROBABILITY OF CYCLOGENESIS[\s\S]{0,300}((?:NIL|LOW|MODERATE|HIGH)[\s\S]{0,120})", text, re.I)
    if pm2:
        chunk = pm2.group(1).upper()
        for kw in ("HIGH", "MODERATE", "LOW"):
            if kw in chunk:
                prob = kw
                break
    return {"dated": dated, "lat": lat, "lon": lon, "pressure_hpa": pressure,
            "wind_kt": wind_kt, "system": system, "prob_cyclogenesis": prob,
            "raw_snippet": text[:600].replace("\n", " ")}


def _severity_for_system(system: str, prob: str) -> str:
    if system:
        r = SYSTEM_RANK.get(system.lower(), 0)
        if r >= 4:
            return "HIGH" if r == 4 else "VERY_HIGH"
        if r >= 2:
            return "MODERATE"
    if prob == "HIGH":
        return "MODERATE"
    if prob == "MODERATE":
        return "LOW"
    return "LOW"


async def fetch_rsmc_cyclone() -> List[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=True,
                                     headers={"User-Agent": "ORCA-Mumbai/1.0"}) as c:
            r = await c.get(RSMC_PDF)
            r.raise_for_status()
            parsed = _parse_rsmc_pdf(r.content)
    except Exception as e:
        log.warning("rsmc_fetch_failed", error=str(e))
        return []
    # No depression/cyclonic system mentioned -> honest "no active system"
    # Still store nothing so the map stays empty (observed, not mocked).
    # Only store when a system is named or lat/lon + wind exists.
    if not parsed["system"] and parsed["lat"] is None:
        log.info("rsmc_no_system", dated=parsed["dated"], prob=parsed.get("prob_cyclogenesis"))
        return []
    sev = _severity_for_system(parsed.get("system") or "", parsed.get("prob_cyclogenesis") or "NIL")
    lat, lon = parsed["lat"], parsed["lon"]
    # Geometry only when coordinates exist; otherwise bbox-level advisory.
    geom_wkt = f"POINT({lon} {lat})" if lat is not None else None
    # Honor bulletin age - outlook valid 168h from DATED, not from now.
    # Stale bulletins (e.g. probe pdf dated 17 Aug) expire honestly so the map
    # stays empty instead of showing a 3-week-old depression forever.
    dated_dt = None
    if parsed.get("dated"):
        try:
            dated_dt = datetime.strptime(parsed["dated"], "%d.%m.%Y").replace(tzinfo=timezone.utc)
        except Exception:
            pass
    if dated_dt and (datetime.now(timezone.utc) - dated_dt) > timedelta(hours=168 + 24):
        log.info("rsmc_stale_bulletin_expired", dated=parsed.get("dated"))
        return []
    now = datetime.now(timezone.utc)
    valid_from = (dated_dt or now).isoformat()
    valid_to = ((dated_dt or now) + timedelta(hours=168)).isoformat() if dated_dt else (now + timedelta(hours=72)).isoformat()
    return [{
        "hazard_type": "cyclone",
        "severity": sev,
        "title": (parsed["system"] or "Tropical weather outlook").title() + (f" {parsed['dated']}" if parsed.get("dated") else ""),
        "description": parsed["raw_snippet"],
        "valid_from": valid_from,
        "valid_to": valid_to,
        "geometry_wkt": geom_wkt,
        "metadata": parsed,
        "source": "RSMC New Delhi tropical outlook (rsmc.pdf)",
    }]


async def fetch_incois_osf_maharashtra() -> List[Dict[str, Any]]:
    # INCOIS OSF regional pages are rendered client-side + session-gated, so
    # scraping is unreliable. We try the known candidates and store a hazard
    # only when the response actually contains a Maharashtra high-wave / rough-sea
    # advisory block. Honest empty otherwise — no mock polygon is invented.
    for url in OSF_MAHARASHTRA_CANDIDATES:
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True,
                                         headers={"User-Agent": "ORCA-Mumbai/1.0"}) as c:
                r = await c.get(url)
                if r.status_code != 200 or len(r.text) < 500:
                    continue
                low = r.text.lower()
                # Require a genuine warning phrase, not just site chrome containing
                # the word "Maharashtra" in a region dropdown.
                has_warning = any(kw in low for kw in ("high wave warning", "rough sea warning", "high wave alert", "rough sea alert"))
                if not has_warning:
                    continue
                snippet = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text)).strip()[:800]
                now = datetime.now(timezone.utc)
                min_lon, min_lat, max_lon, max_lat = MUMBAI_EXTENDED_BBOX
                return [{
                    "hazard_type": "high_wave",
                    "severity": "MODERATE" if "high wave" in low else "LOW",
                    "title": "INCOIS Ocean State Advisory — Maharashtra",
                    "description": snippet,
                    "valid_from": now.isoformat(),
                    "valid_to": (now + timedelta(hours=24)).isoformat(),
                    "geometry_wkt": f"POLYGON(({min_lon} {min_lat},{max_lon} {min_lat},{max_lon} {max_lat},{min_lon} {max_lat},{min_lon} {min_lat}))",
                    "metadata": {"scraped_url": url, "keywords_hit": [k for k in ("high wave", "rough sea", "warning") if k in low]},
                    "source": "INCOIS OSF (scraped Maharashtra region)",
                }]
        except Exception as e:
            log.warning("osf_scrape_failed", url=url, error=str(e))
    return []


def wave_threshold_hazards() -> List[Dict[str, Any]]:
    # Determined from local wave data, not from an upstream bulletin.
    try:
        conn = psycopg.connect(psycopg_conninfo())
        cur = conn.cursor()
        cur.execute("""
            SELECT wave_height, observation_time FROM ocean_observations
            WHERE ST_Within(location::geometry, ST_MakeEnvelope(72.2,18.5,73.2,19.5,4326))
              AND wave_height IS NOT NULL
            ORDER BY observation_time DESC LIMIT 1
        """)
        row = cur.fetchone()
        conn.close()
        if not row or row[0] is None:
            return []
        h, ot = float(row[0]), row[1]
        if h < 2.0:
            return []
        sev = "MODERATE" if h < 2.8 else "HIGH"
        min_lon, min_lat, max_lon, max_lat = MUMBAI_EXTENDED_BBOX
        now = datetime.now(timezone.utc)
        return [{
            "hazard_type": "high_wave",
            "severity": sev,
            "title": f"Elevated wave height {h:.1f} m (threshold 2.0 m)",
            "description": f"Latest Mumbai wave_height {h:.2f} m at {ot.isoformat() if ot else 'unknown'} exceeds operational threshold. Deterministic local flag, not a bulletin. Source: ocean_observations.",
            "valid_from": now.isoformat(),
            "valid_to": (now + timedelta(hours=12)).isoformat(),
            "geometry_wkt": f"POLYGON(({min_lon} {min_lat},{max_lon} {min_lat},{max_lon} {max_lat},{min_lon} {max_lat},{min_lon} {min_lat}))",
            "metadata": {"wave_height_m": h, "source_table": "ocean_observations", "threshold_m": 2.0},
            "source": "ORCA wave-threshold (computed from Mumbai wave_height)",
        }]
    except Exception as e:
        log.warning("wave_threshold_failed", error=str(e))
        return []


def upsert_hazards(items: List[Dict[str, Any]]) -> int:
    if not items:
        return 0
    conn = psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    n = 0
    for it in items:
        # dedupe by (hazard_type, title, valid_from::date)
        cur.execute("DELETE FROM marine_hazards WHERE hazard_type=%s AND title=%s AND valid_from::date = (%s::timestamptz)::date",
                    (it["hazard_type"], it["title"], it["valid_from"]))
        geom_sql = "ST_GeomFromText(%s,4326)" if it.get("geometry_wkt") else "NULL"
        cur.execute(f"""
            INSERT INTO marine_hazards (hazard_type, severity, title, description, valid_from, valid_to, geometry, metadata)
            VALUES (%s,%s,%s,%s,%s::timestamptz,%s::timestamptz,{geom_sql},%s::jsonb)
        """ + ("" if it.get("geometry_wkt") else ""),
                    ([it["hazard_type"], it["severity"], it["title"], it["description"],
                      it["valid_from"], it["valid_to"]] + ([it["geometry_wkt"]] if it.get("geometry_wkt") else []) + [__import__("json").dumps({"source": it.get("source"), **(it.get("metadata") or {})})]))
        n += 1
    conn.commit()
    conn.close()
    return n
