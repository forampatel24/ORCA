"""Validation - docs 09_DATA_PIPELINE VALIDATION step."""
from typing import Dict, Any, Tuple
from datetime import datetime

VALID = "VALID"
SUSPECT = "SUSPECT"
INVALID = "INVALID"

def validate_coordinate(lat: float, lon: float) -> Tuple[str, str]:
    if lat is None or lon is None:
        return INVALID, "missing coordinate"
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return INVALID, f"out of range lat={lat} lon={lon}"
    return VALID, ""

def validate_timestamp(ts: Any) -> Tuple[str, str]:
    if ts is None:
        return INVALID, "missing timestamp"
    try:
        if isinstance(ts, str):
            datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return VALID, ""
    except Exception as e:
        return INVALID, str(e)

def validate_range(value: float, min_v: float, max_v: float, name: str) -> Tuple[str, str]:
    if value is None:
        return SUSPECT, f"{name} missing"
    if not (min_v <= value <= max_v):
        return SUSPECT, f"{name} {value} outside [{min_v},{max_v}]"
    return VALID, ""

def validate_record(record: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate against schema, return enriched record with quality flag."""
    flags = []
    quality = VALID
    for field, rules in schema.items():
        if rules.get("required") and field not in record:
            quality = INVALID
            flags.append(f"missing {field}")
        if field in record and "range" in rules:
            q, msg = validate_range(record[field], *rules["range"], field)
            if q != VALID:
                quality = q if quality == VALID else quality
                flags.append(msg)
    record["_quality"] = quality
    record["_validation_flags"] = flags
    return record

# Example schemas per docs 08
PFZ_SCHEMA = {
    "latitude": {"required": True, "range": (-90, 90)},
    "longitude": {"required": True, "range": (-180, 180)},
    "observation_time": {"required": True},
}
WEATHER_SCHEMA = {
    "latitude": {"required": True, "range": (-90, 90)},
    "longitude": {"required": True, "range": (-180, 180)},
    "wind_speed": {"required": False, "range": (0, 100)},
    "temperature": {"required": False, "range": (-50, 60)},
}
