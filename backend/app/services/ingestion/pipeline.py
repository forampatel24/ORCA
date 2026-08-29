"""Pipeline orchestrator - docs 09_DATA_PIPELINE full lifecycle."""
import json
import uuid
from typing import List, Dict, Any
from datetime import datetime, timezone
import structlog

from app.services.ingestion.validation import validate_record, VALID, INVALID
from app.services.ingestion.normalization import normalize_record

log = structlog.get_logger()

# TTL per docs 05:38 Redis TTL tiers
TTL_MAP = {
    "weather": 1800,  # 30m
    "pfz": 86400,  # 24h
    "ocean": 3600,
    "hazard": 600,  # 10m for lightning/cyclone
    "geospatial": 86400 * 7,  # static
}

class IngestionPipeline:
    """Raw MinIO -> Validation -> Normalization -> Structured PostGIS + Redis cache."""

    def __init__(self, minio_client=None, redis_client=None, db_session=None):
        self.minio = minio_client
        self.redis = redis_client
        self.db = db_session

    async def run(
        self,
        connector,
        schema: Dict[str, Any],
        params: Dict[str, Any] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        params = params or {}
        cache_key = f"orca:{connector.name}:{hash(json.dumps(params, sort_keys=True))}"
        # Redis hit
        if use_cache and self.redis:
            try:
                cached = self.redis.get(cache_key)
                if cached:
                    log.info("ingestion_cache_hit", source=connector.name)
                    return json.loads(cached)
            except: pass

        ingestion_id = str(uuid.uuid4())
        started = datetime.now(timezone.utc)
        log.info("ingestion_started", ingestion_id=ingestion_id, source=connector.name)

        # 1. Fetch
        raw = await connector.fetch(**params)
        # 2. Store raw to MinIO (bucket orca-raw-data)
        if self.minio:
            try:
                import io
                key = f"raw/{connector.name}/{started.date()}/{ingestion_id}.json"
                data = json.dumps(raw).encode()
                self.minio.put_object("orca-raw-data", key, io.BytesIO(data), len(data), content_type="application/json")
                log.info("raw_stored", bucket="orca-raw-data", key=key)
            except Exception as e:
                log.warning("minio_raw_failed", error=str(e))

        # 3. Validate + 4. Normalize + dedupe
        processed = []
        failed = 0
        seen = set()
        for r in raw:
            # dedupe key per docs 09: source+dataset+location+timestamp+variable (+forecast_time for forecasts)
            dk = (connector.source_id, r.get("latitude"), r.get("longitude"), r.get("observation_time"), r.get("forecast_time"), r.get("wind_speed"))
            if dk in seen:
                continue
            seen.add(dk)
            v = validate_record(r, schema)
            if v["_quality"] == INVALID:
                failed += 1
                continue
            v = normalize_record(v)
            v["source_id"] = connector.source_id
            v.update(connector.provenance())
            processed.append(v)

        result = {
            "ingestion_id": ingestion_id,
            "source": connector.name,
            "records_processed": len(raw),
            "records_inserted": len(processed),
            "records_failed": failed,
            "data": processed,
            "ingestion_time": started.isoformat(),
        }

        # 5. Cache
        if self.redis and processed:
            try:
                ttl = TTL_MAP.get(connector.name.split("_")[0], 3600)
                self.redis.setex(cache_key, ttl, json.dumps(result))
            except: pass

        log.info("ingestion_completed", ingestion_id=ingestion_id, inserted=len(processed), failed=failed)
        return result
