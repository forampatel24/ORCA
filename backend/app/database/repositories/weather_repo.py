"""Weather repository - docs 23."""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

class WeatherRepository:
    def get_weather(self, db: Session, latitude: float, longitude: float, limit: int = 24) -> List[Dict[str, Any]]:
        # Fetch nearest weather observations (usually we want the closest grid point)
        query = text("""
            SELECT 
                id, 
                observation_time,
                forecast_time,
                temperature,
                wind_speed,
                wind_direction,
                rainfall,
                humidity,
                pressure,
                ST_Distance(location, ST_GeographyFromText(:point)) / 1000.0 AS distance_km,
                metadata
            FROM weather_observations
            ORDER BY location <-> ST_GeographyFromText(:point), forecast_time ASC
            LIMIT :limit
        """)
        point_wkt = f"POINT({longitude} {latitude})"
        result = db.execute(query, {
            "point": point_wkt, 
            "limit": limit
        }).mappings().all()
        return [dict(r) for r in result]

weather_repo = WeatherRepository()
