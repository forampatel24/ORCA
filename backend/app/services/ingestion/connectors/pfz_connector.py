"""PFZ Connector - INCOIS PFZ mock -> real via WebGIS swap."""
from typing import List, Dict, Any
from datetime import datetime, timezone
from app.services.ingestion.base import BaseConnector

class PFZConnector(BaseConnector):
    def __init__(self, source_id: str):
        super().__init__(source_id, "pfz", "INCOIS")

    def validate_source(self) -> bool:
        return True  # would HEAD INCOIS WMS

    def get_metadata(self):
        return {
            "coverage": "Indian EEZ",
            "spatial_resolution": "0.05deg",
            "update_frequency": "daily",
            "variables": ["latitude","longitude","sst","chlorophyll"],
        }

    async def fetch(self, **params) -> List[Dict[str, Any]]:
        # Mock 3 PFZ near Mumbai for M2 demo - swap to INCOIS API in production
        return [
            {"latitude": 19.1, "longitude": 72.5, "observation_time": datetime.now(timezone.utc).isoformat(), "sst": 28.2, "chlorophyll": 0.8, "sector": "Mumbai North"},
            {"latitude": 18.9, "longitude": 72.9, "observation_time": datetime.now(timezone.utc).isoformat(), "sst": 27.9, "chlorophyll": 1.1, "sector": "Mumbai South"},
            {"latitude": 19.3, "longitude": 71.9, "observation_time": datetime.now(timezone.utc).isoformat(), "sst": 28.5, "chlorophyll": 0.6, "sector": "Offshore"},
        ]
