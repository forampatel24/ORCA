"""Health endpoints - docs 12_API_APEC, 18_MONITORING."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.deps import get_db
import time

router = APIRouter()
_started = time.time()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "orca-backend", "uptime_seconds": int(time.time() - _started)}


@router.get("/health/services")
async def health_services(db: Session = Depends(get_db)):
    status_dict = {
        "postgres": "unknown",
        "redis": "unknown",
        "qdrant": "unknown",
        "minio": "unknown",
    }
    
    # Check Postgres
    try:
        db.execute(text("SELECT 1"))
        status_dict["postgres"] = "healthy"
    except Exception as e:
        status_dict["postgres"] = f"error: {str(e)}"
        
    # Check Redis
    try:
        import redis
        from app.config.settings import settings
        r = redis.from_url(settings.redis_url)
        if r.ping():
            status_dict["redis"] = "healthy"
    except Exception as e:
        status_dict["redis"] = f"error: {str(e)}"

    # Check Qdrant
    try:
        from qdrant_client import QdrantClient
        from app.config.settings import settings
        client = QdrantClient(url=settings.qdrant_url)
        collections = client.get_collections()
        status_dict["qdrant"] = "healthy"
    except Exception as e:
        status_dict["qdrant"] = f"error: {str(e)}"

    # Check MinIO
    try:
        from minio import Minio
        from app.config.settings import settings
        client = Minio(settings.minio_endpoint, access_key=settings.minio_access_key, secret_key=settings.minio_secret_key, secure=settings.minio_secure)
        buckets = client.list_buckets()
        status_dict["minio"] = "healthy"
    except Exception as e:
        status_dict["minio"] = f"error: {str(e)}"
        
    return status_dict
