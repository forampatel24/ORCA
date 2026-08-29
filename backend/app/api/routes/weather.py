"""Weather routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from app.api.deps import get_db, get_current_user
from app.database.repositories.weather_repo import weather_repo
from app.schemas.weather import WeatherResponse

router = APIRouter()

@router.get("/", response_model=WeatherResponse)
async def get_weather(
    latitude: float,
    longitude: float,
    limit: int = 24,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    results = weather_repo.get_weather(db, latitude, longitude, limit)
    items = []
    for r in results:
        items.append({
            "id": str(r["id"]),
            "temperature": r["temperature"],
            "wind_speed": r["wind_speed"],
            "wind_direction": r["wind_direction"],
            "rainfall": r["rainfall"],
            "humidity": r["humidity"],
            "pressure": r["pressure"],
            "distance_km": r["distance_km"],
            "observation_time": r["observation_time"].isoformat() if r["observation_time"] else None,
            "forecast_time": r["forecast_time"].isoformat() if r["forecast_time"] else None
        })
    return {"items": items, "request_id": str(uuid.uuid4())}
