"""Geospatial routes stub."""
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/geofence/check")
async def check_geofence(
    latitude: float,
    longitude: float,
    current_user = Depends(get_current_user)
):
    # M7 Static GIS datasets placeholder
    return {
        "inside_restricted_area": False,
        "inside_marine_protected_area": False,
        "boundaries": []
    }
