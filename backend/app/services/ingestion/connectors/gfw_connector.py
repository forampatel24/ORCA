"""GFW - Global Fishing Watch for Mumbai bbox only via API, not global archive.
Per architecture: Real-time vessel data - API rather than downloading everything.
Uses bbox filter on GFW API, daily/monthly gridded products Mumbai slice.
"""
from typing import List, Dict, Any
import httpx, structlog, os
from datetime import datetime, timezone, timedelta
from app.services.ingestion.base import BaseConnector
from app.config.mumbai import MUMBAI_BBOX, MUMBAI_EXTENDED_BBOX
log = structlog.get_logger()

class GFWConnector(BaseConnector):
    def __init__(self, source_id: str):
        super().__init__(source_id, "gfw", "Global Fishing Watch")
    def validate_source(self) -> bool: return True
    def get_metadata(self):
        return {
            "coverage": f"Mumbai bbox {MUMBAI_BBOX} extended {MUMBAI_EXTENDED_BBOX}",
            "access": "API rather than downloading everything - daily/monthly gridded Mumbai slice",
            "official_link": "https://globalfishingwatch.org/our-apis/",
        }
    async def fetch(self, bbox: List[float] = None, start_date: str = None, end_date: str = None, **params) -> List[Dict[str, Any]]:
        bbox = bbox or MUMBAI_EXTENDED_BBOX
        token = os.getenv("GFW_API_TOKEN", "")
        if not token:
            log.warning("gfw_no_token_mumbai_bbox_only", bbox=bbox)
            return []  # No hardcoded mock - require authentic token for authentic data
        # Example GFW API: 4Wings raster / events with bbox - not global download
        try:
            # Use GFW 4Wings apparent fishing effort tiles? Use events as example
            url = f"{os.getenv('GFW_API','https://api.globalfishingwatch.org/v2')}/events"
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(url, params={
                    "datasets": "public-global-fishing-events:v20201001",
                    "bbox": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
                    "start-date": start_date or (datetime.now(timezone.utc)-timedelta(days=7)).date().isoformat(),
                    "end-date": end_date or datetime.now(timezone.utc).date().isoformat(),
                }, headers={"Authorization": f"Bearer {token}"})
                if r.status_code == 200:
                    data = r.json()
                    entries = data.get("entries", []) if isinstance(data, dict) else []
                    out = []
                    for e in entries[:50]:  # Mumbai slice - limit
                        out.append({
                            "latitude": e.get("position",{}).get("lat"),
                            "longitude": e.get("position",{}).get("lon"),
                            "observation_time": e.get("start") or e.get("timestamp"),
                            "vessel_id": e.get("vessel",{}).get("id"),
                            "type": e.get("type"),
                            "source": "gfw_api_mumbai_bbox",
                        })
                    log.info("gfw_mumbai_ok", count=len(out), bbox=bbox)
                    return out
        except Exception as e:
            log.warning("gfw_fetch_failed", error=str(e))
        return []
