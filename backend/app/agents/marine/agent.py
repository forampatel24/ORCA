"""Marine Data Agent - docs 06 AI-011 + 15 PFZ scoring."""
from typing import Dict, Any
from app.tools.pfz import get_nearest_pfz
from app.tools.ocean import get_ocean
from app.analytics.pfz.scoring import score_pfz
from app.analytics.ocean.anomaly import sst_anomaly, chlorophyll_anomaly

class MarineAgent:
    name = "marine_agent"
    tools = ["get_nearest_pfz", "get_ocean", "score_pfz", "sst_anomaly"]

    async def run(self, lat: float = 19.0, lon: float = 72.8, radius_km: float = 50) -> Dict[str, Any]:
        pfz = get_nearest_pfz(lat, lon, radius_km)
        ocean = get_ocean(lat, lon)
        sst = ocean.get("sst", 28.0)
        chl = ocean.get("chlorophyll", 0.8)
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
