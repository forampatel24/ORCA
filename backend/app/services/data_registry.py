"""Data registry - docs 08_DATASET_REGISTRY selection by intent/location/time."""
from typing import List, Dict, Any, Optional
import structlog

log = structlog.get_logger()

# Intent -> required sources per docs 08 MVP priority
INTENT_SOURCES = {
    "pfz_discovery": ["INCOIS PFZ", "pfz"],
    "safety": ["IMD Weather", "INCOIS OSF", "weather", "ocean"],
    "weather": ["IMD Weather"],
    "ocean": ["INCOIS OSF"],
    "hazard": ["IMD Cyclone", "weather"],
    "route": ["INCOIS OSF", "IMD Weather", "Marine Regions EEZ"],
    "geofence": ["Marine Regions EEZ", "WDPA"],
}

class DataRegistry:
    def __init__(self, db_session):
        self.db = db_session

    def list_sources(self) -> List[Dict[str, Any]]:
        from sqlalchemy import text
        rows = self.db.execute(text("SELECT id, name, provider, source_type, status, last_updated FROM data_sources ORDER BY name")).mappings().all()
        return [dict(r) for r in rows]

    def select_for_intent(self, intent: str, location: Optional[Dict]=None, time_range: Optional[Dict]=None) -> List[Dict[str, Any]]:
        """Provider-agnostic selection - docs 08."""
        needed = INTENT_SOURCES.get(intent, [])
        # For M2, simple: return all matching by name contains
        all_src = self.list_sources()
        selected = [s for s in all_src if any(n.lower() in s["name"].lower() for n in needed)]
        log.info("registry_select", intent=intent, needed=needed, selected=[s["name"] for s in selected])
        return selected

    def check_freshness(self, source: Dict[str, Any]) -> str:
        """FRESH/AGING/STALE/UNAVAILABLE per docs 08."""
        # M2 stub: if last_updated null -> AGING
        if not source.get("last_updated"):
            return "AGING"
        return "FRESH"
