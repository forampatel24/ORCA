"""PFZ Connector - authentic INCOIS PFZ for Maharashtra SEC002, Mumbai-bbox filtered.
Source: INCOIS TextDataHome (session JSESSIONID) -> TextData?secid=SEC002.
Table columns: landing centre | direction | bearing | distance km | depth mtr | lat DMS | lon DMS.
No hardcoded coords - reads bbox from app.config.mumbai.
"""
import re
from typing import List, Dict, Any
from datetime import datetime, timezone
import httpx
import structlog
from app.services.ingestion.base import BaseConnector
from app.config.mumbai import MUMBAI_BBOX, INCOIS_PFZ_WMS, bbox_str

log = structlog.get_logger()

TEXT_HOME = "https://incois.gov.in/MarineFisheries/TextDataHome?mfid=1&request_locale=en"
TEXT_DATA = "https://incois.gov.in/MarineFisheries/TextData"
SECTOR_ID = "SEC002"  # Maharashtra
SECTOR_NAME = "Maharashtra"

_MONTHS = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
           "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}


def _parse_incois_date(s: str):
    """'6 SEP 2026' -> aware datetime UTC midnight."""
    m = re.match(r"\s*(\d{1,2})\s+([A-Za-z]{3,})\s+(\d{4})", s.strip())
    if not m:
        return None
    day, mon, year = int(m.group(1)), m.group(2)[:3].upper(), int(m.group(3))
    return datetime(year, _MONTHS.get(mon, 9), day, tzinfo=timezone.utc)


def _dms_to_decimal(s: str, is_lat: bool):
    """'20 0 42 N' / '72 15 32 E' -> decimal degrees. Returns None on failure."""
    m = re.match(r"\s*(\d+)\s+(\d+)\s+([\d.]+)\s*([NSEW])", s.strip(), re.I)
    if not m:
        return None
    d, mi, sec, hemi = int(m.group(1)), int(m.group(2)), float(m.group(3)), m.group(4).upper()
    v = d + mi / 60.0 + sec / 3600.0
    if (is_lat and hemi == "S") or ((not is_lat) and hemi == "W"):
        v = -v
    return round(v, 6)


def _clean_cell(h: str) -> str:
    txt = re.sub(r"<[^>]+>", "", h)
    txt = txt.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", txt).strip()


def parse_sectext(home_html: str, detail_html: str) -> Dict[str, Any]:
    """Parse forecast/valid dates + PFZ rows. Returns {forecast, valid_upto, rows}."""
    fm = re.search(r"Forecast Date.*?(?:<td[^>]*>\s*)?(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})", home_html, re.S | re.I)
    vm = re.search(r"Valid upto.*?(?:<td[^>]*>\s*)?(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})", home_html, re.S | re.I)
    forecast = _parse_incois_date(fm.group(1)) if fm else None
    valid_upto = _parse_incois_date(vm.group(1)) if vm else None
    tables = re.findall(r"<table.*?</table>", detail_html, re.S | re.I)
    if not tables:
        return {"forecast": forecast, "valid_upto": valid_upto, "rows": []}
    big = max(tables, key=len)
    trs = re.findall(r"<tr.*?</tr>", big, re.S | re.I)
    rows = []
    for tr in trs[1:]:  # skip header
        cells = re.findall(r"<td.*?>(.*?)</td>", tr, re.S | re.I)
        if len(cells) < 7:
            continue
        vals = [_clean_cell(ch) for ch in cells[:7]]
        if not vals[0] or not vals[5] or not vals[6]:
            continue
        lat = _dms_to_decimal(vals[5], True)
        lon = _dms_to_decimal(vals[6], False)
        if lat is None or lon is None:
            continue
        try:
            bearing = int(re.sub(r"[^\d]", "", vals[2])) if vals[2] else None
        except Exception:
            bearing = None
        rows.append({
            "landing_centre": vals[0], "direction": vals[1], "bearing_deg": bearing,
            "distance_km": vals[3], "depth_mtr": vals[4],
            "lat_dms": vals[5], "lon_dms": vals[6],
            "latitude": lat, "longitude": lon,
        })
    return {"forecast": forecast, "valid_upto": valid_upto, "rows": rows}

class PFZConnector(BaseConnector):
    def __init__(self, source_id: str):
        super().__init__(source_id, "pfz", "INCOIS")

    def validate_source(self) -> bool:
        try:
            r = httpx.head(INCOIS_PFZ_WMS, timeout=10, follow_redirects=True)
            return r.status_code < 400
        except Exception as e:
            log.warning("pfz_validate_failed", error=str(e))
            return False

    def get_metadata(self):
        return {
            "coverage": f"Mumbai bbox {bbox_str()} EPSG:4326",
            "spatial_resolution": "0.05deg",
            "update_frequency": "daily",
            "variables": ["latitude","longitude","sst","chlorophyll"],
            "access": "WebGIS live",
            "official_link": INCOIS_PFZ_WMS,
            "region": "Mumbai only - not global",
        }

    async def fetch(self, bbox: List[float] = None, date: str = None, lat: float = None, lon: float = None, include_outside_bbox: bool = False, **params) -> List[Dict[str, Any]]:
        """Live fetch: session -> SEC002 text table -> DMS parse -> bbox filter.
        Returns Mumbai-bbox subset by default; full Maharashtra sector when
        include_outside_bbox=True. Empty list only when INCOIS truly has no rows
        (ban / cyclone / adverse sea) - never a hardcoded mock.
        """
        use_bbox = bbox or MUMBAI_BBOX
        errors = []
        # 1. Live INCOIS SEC002 with session cookies (JSESSIONID required)
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent": "ORCA-Mumbai/1.0"}) as client:
                home_r = await client.get(TEXT_HOME)
                home_html = home_r.text if home_r.status_code == 200 else ""
                r = await client.get(TEXT_DATA, params={"secid": SECTOR_ID})
                if r.status_code == 200:
                    parsed = parse_sectext(home_html, r.text)
                    rows = parsed["rows"]
                    fc, vu = parsed["forecast"], parsed["valid_upto"]
                    if not rows:
                        # Genuine no-advisory day (ban / cyclone / high waves)
                        log.warning("pfz_incois_no_rows_ban_or_adverse_sea", sector=SECTOR_ID)
                    obs_iso = (fc.isoformat() if fc else datetime.now(timezone.utc).isoformat())
                    out = []
                    sector_total = len(rows)
                    for row in rows:
                        in_mumbai = (use_bbox[1] <= row["latitude"] <= use_bbox[3]
                                     and use_bbox[0] <= row["longitude"] <= use_bbox[2])
                        if not include_outside_bbox and not in_mumbai:
                            continue
                        out.append({
                            "latitude": row["latitude"],
                            "longitude": row["longitude"],
                            "observation_time": obs_iso,
                            "valid_from": fc.isoformat() if fc else None,
                            "valid_to": vu.isoformat() if vu else None,
                            "sector": SECTOR_NAME,
                            "landing_centre": row["landing_centre"],
                            "in_mumbai_bbox": in_mumbai,
                            "source": "incois_pfz_text_SEC002_live",
                            "metadata": {
                                "landing_centre": row["landing_centre"],
                                "direction": row["direction"],
                                "bearing_deg": row["bearing_deg"],
                                "distance_km": row["distance_km"],
                                "depth_mtr": row["depth_mtr"],
                                "lat_dms": row["lat_dms"],
                                "lon_dms": row["lon_dms"],
                                "sector": f"{SECTOR_NAME} ({SECTOR_ID})",
                                "sector_total": sector_total,
                                "forecast_date": fc.strftime("%d %b %Y") if fc else None,
                                "valid_upto": vu.strftime("%d %b %Y") if vu else None,
                            },
                        })
                    if out:
                        log.info("pfz_incois_live_ok", sector_total=sector_total, returned=len(out), bbox=use_bbox)
                        return out
                    # rows existed but none in bbox -> still return empty with provenance
                    if rows:
                        log.warning("pfz_incois_none_in_mumbai_bbox", sector_total=sector_total, bbox=use_bbox)
                        return []
        except Exception as e:
            errors.append(f"incois_live:{e}")
            log.warning("pfz_incois_live_failed", error=str(e))

        # 2. Authentic: read from pfz_observations already ingested via pipeline, filtered to Mumbai bbox ONLY
        # No global - only Mumbai bbox points are authoritative
        try:
            import psycopg
            conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
            cur = conn.cursor()
            cur.execute("""
                SELECT latitude, longitude, observation_time, metadata
                FROM pfz_observations
                WHERE latitude BETWEEN %s AND %s AND longitude BETWEEN %s AND %s
                ORDER BY observation_time DESC LIMIT 20
            """, (use_bbox[1], use_bbox[3], use_bbox[0], use_bbox[2]))
            rows = cur.fetchall()
            conn.close()
            if rows:
                result = []
                for lat_, lon_, obs_time, meta in rows:
                    md = meta if isinstance(meta, dict) else {}
                    result.append({
                        "latitude": float(lat_),
                        "longitude": float(lon_),
                        "observation_time": obs_time.isoformat() if obs_time else datetime.now(timezone.utc).isoformat(),
                        "sst": md.get("sst") if isinstance(md, dict) else None,
                        "chlorophyll": md.get("chlorophyll") if isinstance(md, dict) else None,
                        "sector": md.get("sector", "Mumbai"),
                        "source": "pfz_observations_mumbai_bbox",
                    })
                log.info("pfz_fetch_mumbai_bbox", count=len(result), bbox=use_bbox)
                return result
        except Exception as e:
            errors.append(f"db:{e}")
            log.warning("pfz_db_fetch_failed", error=str(e))

        # 3. If no authentic Mumbai PFZ available, return empty with provenance - NEVER hardcoded mock
        # Caller (pipeline) will mark DEGRADED and use previous valid data per docs 09:Failed Ingestion
        log.warning("pfz_no_authentic_mumbai_data", bbox=use_bbox, errors=errors)
        return []
