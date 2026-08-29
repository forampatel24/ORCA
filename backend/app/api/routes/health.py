"""Health endpoints - docs 12_API_APEC, 18_MONITORING."""
from fastapi import APIRouter
import time

router = APIRouter()
_started = time.time()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "orca-backend", "uptime_seconds": int(time.time() - _started)}


@router.get("/health/services")
async def health_services():
    # Placeholder - will check DB/Redis/Qdrant/MinIO in M1
    return {
        "postgres": "unknown - check D:\\PostreSQL",
        "redis": "unknown",
        "qdrant": "unknown",
        "minio": "unknown",
    }
