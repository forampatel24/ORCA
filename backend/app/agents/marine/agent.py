"""Marine Data Agent - docs 06 AI-011 + 15 PFZ scoring."""
from typing import Dict, Any
from app.tools.pfz import get_nearest_pfz
from app.tools.ocean import get_ocean
from app.analytics.pfz.scoring import score_pfz
from app.analytics.ocean.anomaly import sst_anomaly, chlorophyll_anomaly

class MarineAgent:
    name = "marine_agent"
    tools = ["get_nearest_pfz", "get_ocean", "score_pfz", "sst_anomaly"]

    async def run(self, lat: float = 19.076, lon: float = 72.877, radius_km: float = 50) -> Dict[str, Any]:
        from app.config.mumbai import point_within_mumbai, MUMBAI_POINT, MUMBAI_BBOX
        if not point_within_mumbai(lat, lon): lat, lon = MUMBAI_POINT
        pfz = get_nearest_pfz(lat, lon, radius_km)
        ocean = get_ocean(lat, lon)
        sst = ocean.get("sst")
        chl = ocean.get("chlorophyll")
        # No hardcoded 28.0/0.8 - handle missing authentic data explicitly
        if sst is None or chl is None:
            return {"pfz": pfz, "scored_pfz": [], "ocean": ocean, "anomalies": {"sst": sst_anomaly(sst or 0) if sst else {"flag":"MISSING"}, "chlorophyll": chlorophyll_anomaly(chl or 0) if chl else {"flag":"MISSING"}}, "count": len(pfz), "source": "mumbai_bbox_no_hardcoded", "bbox": MUMBAI_BBOX, "note": "No authentic ocean data for Mumbai bbox - ingest via OceanConnector first"}
        # Score top PFZ
        scored = []
        for p in pfz[:3]:
            s = score_pfz(sst, chl, p.get("distance_km", 20), "MODERATE")
            scored.append({**p, "pfz_score": s["pfz_score"], "safety_override": s["safety_override"]})
        return {
            "pfz": pfz, "scored_pfz": scored, "ocean": ocean,
            "anomalies": {"sst": sst_anomaly(sst), "chlorophyll": chlorophyll_anomaly(chl)},
            "count": len(pfz), "source": "pfz_observations + ocean_observations"
        }

marine_agent = MarineAgent()
