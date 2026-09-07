"""GFW - Global Fishing Watch v3 for Maharashtra/Mumbai bbox via spatial POST.

API v2 (api.globalfishingwatch.org/v2) is DEPRECATED since 30 Apr 2024 and its
host no longer answers. Uses v3 gateway:
  POST https://gateway.api.globalfishingwatch.org/v3/events
  body: {datasets: ["public-global-fishing-events:latest"], geometry: Polygon,
         startDate, endDate}
Per architecture: API slice for our bbox, not global download.
"""
from typing import List, Dict, Any
import httpx
import structlog
import os
from datetime import datetime, timezone, timedelta
from app.services.ingestion.base import BaseConnector
from app.config.mumbai import MUMBAI_BBOX, MUMBAI_EXTENDED_BBOX

log = structlog.get_logger()

GFW_V3_DEFAULT = "https://gateway.api.globalfishingwatch.org/v3"
FISHING_DATASET = "public-global-fishing-events:latest"


def _bbox_polygon(bbox: List[float]) -> Dict[str, Any]:
    min_lon, min_lat, max_lon, max_lat = bbox
    return {"type": "Polygon", "coordinates": [[
        [min_lon, min_lat], [max_lon, min_lat], [max_lon, max_lat],
        [min_lon, max_lat], [min_lon, min_lat],
    ]]}


def _fnum(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None

class GFWConnector(BaseConnector):
    def __init__(self, source_id: str):
        super().__init__(source_id, "gfw", "Global Fishing Watch")
    def validate_source(self) -> bool: return True
    def get_metadata(self):
        return {
            "coverage": f"Mumbai bbox {MUMBAI_BBOX} extended {MUMBAI_EXTENDED_BBOX}",
            "access": "v3 Events POST with bbox polygon - Maharashtra slice, not global",
            "official_link": "https://globalfishingwatch.org/our-apis/",
            "api_version": "v3",
            "dataset": FISHING_DATASET,
        }

    async def fetch(self, bbox: List[float] = None, start_date: str = None, end_date: str = None, limit: int = 50, **params) -> List[Dict[str, Any]]:
        bbox = bbox or MUMBAI_EXTENDED_BBOX
        # Token from process env first, else backend/.env via settings (uvicorn
        # does not export .env into os.environ, so os.getenv alone is empty).
        token = (os.getenv("GFW_API_TOKEN", "") or "").strip()
        base = (os.getenv("GFW_API", "") or "").strip()
        if not token or not base:
            try:
                from app.config.settings import settings as _s
                if not token:
                    token = (_s.gfw_api_token or "").strip()
                if not base:
                    base = (_s.gfw_api or "").strip()
            except Exception:
                pass
        if not token:
            log.warning("gfw_no_token_mumbai_bbox_only", bbox=bbox)
            return []  # No hardcoded mock - require authentic token for authentic data
        base = (base or GFW_V3_DEFAULT).rstrip("/")
        if "/api/v3" in base or base.endswith("/v2"):
            # migrate stale v2 config to v3 gateway automatically
            base = GFW_V3_DEFAULT
        url = f"{base}/events"
        end_d = end_date or datetime.now(timezone.utc).date().isoformat()
        start_d = start_date or (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
        try:
            # Spatial POST can take 60s+ on GFW side for a 7-day window
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(url, params={"limit": limit, "offset": 0},
                                      json={"datasets": [FISHING_DATASET],
                                            "geometry": _bbox_polygon(bbox),
                                            "startDate": start_d, "endDate": end_d},
                                      headers={"Authorization": f"Bearer {token}"})
                if r.status_code in (200, 201):
                    data = r.json()
                    entries = data.get("entries", []) if isinstance(data, dict) else []
                    out = []
                    for e in entries[:limit]:
                        pos = e.get("position", {}) or {}
                        ves = e.get("vessel", {}) or {}
                        lat, lon = _fnum(pos.get("lat")), _fnum(pos.get("lon"))
                        if lat is None or lon is None:
                            continue
                        out.append({
                            "latitude": lat,
                            "longitude": lon,
                            "observation_time": e.get("start") or e.get("timestamp"),
                            "vessel_id": ves.get("id"),
                            "vessel_name": ves.get("name"),
                            "type": e.get("type"),
                            "source": "gfw_v3_events_maharashtra_bbox",
                            "metadata": {
                                "event_id": e.get("id"),
                                "end": e.get("end"),
                                "bounding_box": e.get("boundingBox"),
                                "regions_eez": (e.get("regions", {}) or {}).get("eez"),
                                "dataset": (data.get("metadata", {}) or {}).get("datasets"),
                                "bbox": bbox,
                            },
                        })
                    log.info("gfw_mumbai_ok", count=len(out), total=data.get("total"), bbox=bbox)
                    return out
                log.warning("gfw_non200", status=r.status_code, text=r.text[:300])
        except Exception as e:
            log.warning("gfw_fetch_failed", error=str(e))
        return []
