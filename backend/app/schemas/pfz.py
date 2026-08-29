from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PFZItem(BaseModel):
    id: str
    latitude: float
    longitude: float
    sector: Optional[str] = None
    sst: Optional[float] = None
    chlorophyll: Optional[float] = None
    distance_km: Optional[float] = None
    observation_time: Optional[str] = None

class PFZResponse(BaseModel):
    count: int
    items: List[PFZItem]
    request_id: str
