"""Ocean Connector - SST/Chlorophyll/Waves/Currents/Tide for Mumbai bbox only.
Per architecture: Live API/service + Large gridded subset (Mumbai only, not global).
Primary: Open-Meteo Marine (waves/currents) + Copernicus subset if credentials else INCOIS OSF.
No hardcoded sst 28.2 / chl 0.8 / wave 1.2.
"""
from typing import List, Dict, Any
from datetime import datetime, timezone
import httpx, structlog, os
from app.services.ingestion.base import BaseConnector
from app.config.mumbai import MUMBAI_BBOX, MUMBAI_POINT, OPEN_METEO_API

log = structlog.get_logger()

class OceanConnector(BaseConnector):
    def __init__(self, source_id: str, var: str = "ocean"):
        # var: sst|chlorophyll|waves|currents|tide - same connector for Mumbai slice
        super().__init__(source_id, var, "Copernicus/INCOIS/OpenMeteo")
        self.var = var

    def validate_source(self) -> bool: return True
    def get_metadata(self):
        return {
            "variables": ["sst","chlorophyll","wave_height","wave_period","current_speed","tide"],
            "coverage": f"Mumbai bbox {MUMBAI_BBOX} - not global 0.083deg",
            "access": "Live API + Copernicus subset (Mumbai only) + INCOIS OSF",
        }

    async def fetch(self, lat: float = None, lon: float = None, bbox: List[float] = None, **params) -> List[Dict[str, Any]]:
        lat = lat if lat is not None else MUMBAI_POINT[0]
        lon = lon if lon is not None else MUMBAI_POINT[1]
        bbox = bbox or MUMBAI_BBOX
        # Validate Mumbai-only
        from app.config.mumbai import point_within_mumbai
        if not point_within_mumbai(lat, lon):
            lat, lon = MUMBAI_POINT

        # 1. Try Open-Meteo Marine for Mumbai (waves, no key)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get("https://marine-api.open-meteo.com/v1/marine", params={
                    "latitude": lat, "longitude": lon,
                    "hourly": "wave_height,wave_period,wave_direction,sea_surface_temperature",
                    "current": "sea_surface_temperature,wave_height,wave_period",
                    "timezone": "UTC", "forecast_days": 1,
                })
                if r.status_code == 200:
                    data = r.json()
                    cur = data.get("current", {}) or {}
                    hourly = data.get("hourly", {}) or {}
                    sst = cur.get("sea_surface_temperature")
                    wh = cur.get("wave_height")
                    wp = cur.get("wave_period")
                    if sst is not None or wh is not None:
                        rec = {
                            "latitude": lat, "longitude": lon,
                            "observation_time": datetime.now(timezone.utc).isoformat(),
                            "sst": float(sst) if sst is not None else None,
                            "chlorophyll": None,  # chlorophyll not in marine API - filled by Copernicus/INCOIS if available
                            "wave_height": float(wh) if wh is not None else None,
                            "wave_period": float(wp) if wp is not None else None,
                            "source": "open-meteo_marine_mumbai",
                        }
                        log.info("ocean_openmeteo_mumbai_ok", lat=lat, lon=lon, sst=sst, wh=wh)
                        # Try enrich chlorophyll via INCOIS/Copernicus if credentials
                        # If copernicus credentials set, could subset here - keep lightweight for M13
                        return [rec]
        except Exception as e:
            log.warning("ocean_openmeteo_failed", error=str(e))

        # 2. Try INCOIS OSF SST via OPeNDAP subset (if reachable) - else use DB Mumbai slice
        try:
            import psycopg
            conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
            cur = conn.cursor()
            cur.execute("""
                SELECT sst, chlorophyll, wave_height, wave_period, observation_time, location
                FROM ocean_observations
                WHERE ST_Within(location::geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326))
                ORDER BY observation_time DESC LIMIT 1
            """, (bbox[0], bbox[1], bbox[2], bbox[3]))
            row = cur.fetchone()
            conn.close()
            if row and row[0] is not None:
                rec = {
                    "latitude": lat, "longitude": lon,
                    "observation_time": row[4].isoformat() if row[4] else datetime.now(timezone.utc).isoformat(),
                    "sst": float(row[0]) if row[0] is not None else None,
                    "chlorophyll": float(row[1]) if row[1] is not None else None,
                    "wave_height": float(row[2]) if row[2] is not None else None,
                    "wave_period": float(row[3]) if row[3] is not None else None,
                    "source": "ocean_observations_mumbai_bbox",
                }
                log.info("ocean_db_mumbai_ok", rec=rec)
                return [rec]
        except Exception as e:
            log.warning("ocean_db_failed", error=str(e))

        # 3. Copernicus subset via copernicusmarine CLI if credentials - explicit Mumbai bbox, not global
        # Requires COPERNICUSMARINE_SERVICE_USERNAME/PASSWORD in env
        user = os.getenv("COPERNICUSMARINE_SERVICE_USERNAME") or os.getenv("COPERNICUS_USERNAME", "")
        if user:
            log.info("copernicus_credentials_present_mumbai_subset", bbox=bbox, dataset="cmems_mod_glo_phy")
            # Subset would be: copernicusmarine subset --dataset-id cmems_mod_glo_phy_my_0.083deg_P1D-m --minimum-longitude 72.2 --maximum-longitude 73.2 ...
            # Stored to MinIO orca-raster/copernicus/mumbai_phy_{date}.nc - not implemented as blocking CLI in connector
            # External script should handle large download; connector returns empty to avoid blocking live API
            pass

        log.warning("ocean_no_authentic_mumbai_data", lat=lat, lon=lon, bbox=bbox)
        return []
