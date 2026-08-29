"""PFZ repository - docs 21 nearest PFZ."""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

class PFZRepository:
    def get_nearest(self, db: Session, latitude: float, longitude: float, radius_km: float = 50.0, limit: int = 5) -> List[Dict[str, Any]]:
        # PostGIS ST_DWithin uses meters for geography type
        query = text("""
            SELECT 
                id, 
                observation_time, 
                valid_from, 
                latitude, 
                longitude,
                ST_Distance(geometry, ST_GeographyFromText(:point)) / 1000.0 AS distance_km,
                metadata
            FROM pfz_observations
            WHERE ST_DWithin(geometry, ST_GeographyFromText(:point), :radius_m)
            ORDER BY distance_km ASC
            LIMIT :limit
        """)
        point_wkt = f"POINT({longitude} {latitude})"
        result = db.execute(query, {
            "point": point_wkt, 
            "radius_m": radius_km * 1000.0, 
            "limit": limit
        }).mappings().all()
        return [dict(r) for r in result]

pfz_repo = PFZRepository()
