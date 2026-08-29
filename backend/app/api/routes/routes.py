"""Routes routes stub (M6 placeholder)."""
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.schemas.route import RouteResponse, RouteOption

router = APIRouter()

@router.post("/calculate", response_model=RouteResponse)
async def calculate_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    current_user = Depends(get_current_user)
):
    # Stub for M6 Route optimization engine
    return RouteResponse(
        routes=[
            RouteOption(
                route_id="stub-1",
                distance_km=42.3,
                duration="2h 15m",
                risk_score=0.24,
                geofence_violations=[],
                hazards=[]
            )
        ]
    )
