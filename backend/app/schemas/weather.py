"""Weather schemas - docs 23."""
from pydantic import BaseModel
from typing import List, Optional

class WeatherObservation(BaseModel):
    id: str
    temperature: float | None = None
    wind_speed: float | None = None
    wind_direction: float | None = None
    rainfall: float | None = None
    humidity: float | None = None
    pressure: float | None = None
    distance_km: float | None = None
    observation_time: str | None = None
    forecast_time: str | None = None

class WeatherResponse(BaseModel):
    items: List[WeatherObservation]
    request_id: str
