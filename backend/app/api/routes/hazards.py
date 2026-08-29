"""Hazards routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from app.api.deps import get_db, get_current_user
from app.database.repositories.hazard_repo import hazard_repo

router = APIRouter()

@router.get("/")
async def get_hazards(
    latitude: float,
    longitude: float,
    radius: float = 100.0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    results = hazard_repo.get_hazards(db, latitude, longitude, radius)
    items = []
    for r in results:
        items.append({
            "id": str(r["id"]),
            "hazard_type": r["hazard_type"],
            "severity": r["severity"],
            "description": r["description"],
            "distance_km": r["distance_km"],
            "valid_from": r["valid_from"].isoformat() if r["valid_from"] else None,
            "valid_to": r["valid_to"].isoformat() if r["valid_to"] else None
        })
    return {"count": len(items), "items": items, "request_id": str(uuid.uuid4())}
