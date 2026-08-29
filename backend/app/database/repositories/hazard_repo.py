"""Hazard repository - docs 26."""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

class HazardRepository:
    def get_hazards(self, db: Session, latitude: float, longitude: float, radius_km: float = 100.0) -> List[Dict[str, Any]]:
        # Note: geometry is GEOMETRY in marine_hazards, we cast to geography for distance
        query = text("""
            SELECT 
                id, 
                hazard_type,
                severity,
                valid_from,
                valid_to,
                description,
                ST_Distance(geometry::geography, ST_GeographyFromText(:point)) / 1000.0 AS distance_km
            FROM marine_hazards
            WHERE ST_DWithin(geometry::geography, ST_GeographyFromText(:point), :radius_m)
               AND (valid_to IS NULL OR valid_to >= NOW())
            ORDER BY distance_km ASC
        """)
        point_wkt = f"POINT({longitude} {latitude})"
        result = db.execute(query, {
            "point": point_wkt, 
            "radius_m": radius_km * 1000.0
        }).mappings().all()
        return [dict(r) for r in result]

hazard_repo = HazardRepository()
