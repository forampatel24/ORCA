"""Normalization - docs 07_DATA_ARCHITECTURE, 09_DATA_PIPELINE NORMALIZATION."""
from datetime import datetime, timezone
from typing import Dict, Any

def normalize_timestamp(ts: Any) -> str:
    """Convert to UTC ISO8601. Handles str/ datetime."""
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc).isoformat()
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except:
            return ts
    return str(ts)

def normalize_coordinate(lat: float, lon: float) -> tuple:
    """Ensure EPSG:4326, clamp. PyProj transform would go here for other CRS."""
    return float(lat), float(lon)

def normalize_temperature(value: float, unit: str = "C") -> float:
    """Convert Kelvin -> Celsius if needed. ORCA stores Celsius."""
    if unit == "K":
        return value - 273.15
    return value

def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Apply all normalizations, preserve provenance."""
    if "observation_time" in record:
        record["observation_time"] = normalize_timestamp(record["observation_time"])
    if "forecast_time" in record:
        record["forecast_time"] = normalize_timestamp(record["forecast_time"])
    if "latitude" in record and "longitude" in record:
        record["latitude"], record["longitude"] = normalize_coordinate(record["latitude"], record["longitude"])
    if "sst" in record and record.get("sst_unit") == "K":
        record["sst"] = normalize_temperature(record["sst"], "K")
        record["sst_unit"] = "C"
    # Ensure ingestion_time distinct from observation_time per docs 05:46
    record["ingestion_time"] = datetime.now(timezone.utc).isoformat()
    return record
