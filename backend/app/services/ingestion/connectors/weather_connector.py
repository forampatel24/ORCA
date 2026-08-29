"""Weather Connector - IMD/Open-Meteo mock."""
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from app.services.ingestion.base import BaseConnector

class WeatherConnector(BaseConnector):
    def __init__(self, source_id: str):
        super().__init__(source_id, "weather", "IMD")

    def validate_source(self) -> bool:
        return True

    def get_metadata(self):
        return {"update_frequency": "3h", "variables": ["wind_speed","temperature","rainfall","pressure"]}

    async def fetch(self, lat: float = 19.0, lon: float = 72.8, **params) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {"latitude": lat, "longitude": lon, "observation_time": now.isoformat(), "forecast_time": (now+timedelta(hours=6)).isoformat(), "wind_speed": 12.5, "wind_direction": 270, "temperature": 29.0, "rainfall": 0.2, "pressure": 1008},
            {"latitude": lat, "longitude": lon, "observation_time": now.isoformat(), "forecast_time": (now+timedelta(hours=24)).isoformat(), "wind_speed": 18.0, "wind_direction": 260, "temperature": 28.5, "rainfall": 2.1, "pressure": 1005},
        ]
