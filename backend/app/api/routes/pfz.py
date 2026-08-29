"""PFZ routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from app.api.deps import get_db, get_current_user
from app.database.repositories.pfz_repo import pfz_repo
from app.schemas.pfz import PFZResponse
from typing import List, Dict, Any

router = APIRouter()

@router.get("/nearest", response_model=PFZResponse)
async def get_nearest_pfz(
    latitude: float,
    longitude: float,
    radius: float = 50.0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    results = pfz_repo.get_nearest(db, latitude, longitude, radius)
    items = []
    for r in results:
        items.append({
            "id": str(r["id"]),
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "distance_km": r["distance_km"],
            "observation_time": r["observation_time"].isoformat() if r["observation_time"] else None,
            "sector": r["metadata"].get("sector") if r["metadata"] else None,
            "sst": r["metadata"].get("sst") if r["metadata"] else None
        })
    return {"count": len(items), "items": items, "request_id": str(uuid.uuid4())}
