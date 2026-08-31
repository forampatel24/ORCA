"""GEBCO Bathymetry - Mumbai bbox subset only, not 4GB/7GB global.
Per architecture: Large gridded - Download only required region/time, user-defined area.
Uses direct raster subset clipped to Mumbai bbox. No global dump to D:.
"""
from typing import List, Dict, Any
import structlog
from app.services.ingestion.base import BaseConnector
from app.config.mumbai import MUMBAI_BBOX, MUMBAI_EXTENDED_BBOX

log = structlog.get_logger()

class GEBCOConnector(BaseConnector):
    def __init__(self, source_id: str):
        super().__init__(source_id, "gebco", "GEBCO")

    def validate_source(self) -> bool: return True
    def get_metadata(self):
        return {
            "coverage": f"Mumbai bbox {MUMBAI_BBOX} extended {MUMBAI_EXTENDED_BBOX} - not global 4GB",
            "access": "Download only required region - user-defined geographic area per GEBCO",
            "format": "GeoTIFF NetCDF",
            "official_link": "https://www.gebco.net/data-products/gridded-bathymetry-data",
        }

    async def fetch(self, bbox: List[float] = None, **params) -> List[Dict[str, Any]]:
        bbox = bbox or MUMBAI_BBOX
        # Bathymetry is static - ingestion is via scripts/ingest_m7_mumbai.py which subsets GeoTIFF to bbox
        # This connector returns metadata only; actual raster is stored as MinIO orca-raster/bathymetry/mumbai_gebco_subset.tif
        log.info("gebco_mumbai_bbox_metadata", bbox=bbox)
        return [{
            "bbox": bbox,
            "source": "GEBCO_mumbai_subset",
            "note": "Raster stored in MinIO orca-raster/bathymetry/mumbai_gebco_subset.tif clipped to Mumbai bbox - not global 4GB",
            "latitude": (bbox[1]+bbox[3])/2,
            "longitude": (bbox[0]+bbox[2])/2,
            "observation_time": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        }]
