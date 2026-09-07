"""Hazards routes - public reads for the Safety layers."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import uuid
from app.api.deps import get_db
from app.database.repositories.hazard_repo import hazard_repo

router = APIRouter()

@router.get("/")
async def get_hazards(
    latitude: float,
    longitude: float,
    radius: float = 100.0,
    db: Session = Depends(get_db),
):
    # Public read: Safety layers must not require login (see ocean/pfz).
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


@router.get("/live")
async def live_hazards():
    """Honest live hazard status: RSMC cyclone + wave threshold, no mocks."""
    from app.services.hazards.live_hazards import fetch_rsmc_cyclone, wave_threshold_hazards
    cyc = await fetch_rsmc_cyclone()
    wav = wave_threshold_hazards()
    # Do not auto-insert here - this endpoint is read-only and reflects what a
    # refresh would see. The DB route remains the history. Show live probe.
    return {"cyclone_items": cyc, "wave_items": wav, "count": len(cyc) + len(wav),
            "request_id": str(uuid.uuid4())}


@router.get("/lightning")
async def lightning_live(bbox: str = Query(default="71.8,15.5,74.5,20.5")):
    """Live lightning strikes in Maharashtra bbox (Blitzortung when reachable)."""
    from app.services.lightning_store import fetch_lightning_maharashtra, cape_thunderstorm_risk
    try:
        min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
    except Exception:
        min_lon, min_lat, max_lon, max_lat = 71.8, 15.5, 74.5, 20.5
    data = await fetch_lightning_maharashtra((min_lon, min_lat, max_lon, max_lat))
    risk = cape_thunderstorm_risk()
    return {"bbox": bbox, "strikes": data["strikes"], "strikes_count": len(data["strikes"]),
            "source": data.get("source"), "error": data.get("error"),
            "cape": risk, "request_id": str(uuid.uuid4())}
