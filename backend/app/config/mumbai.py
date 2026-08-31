"""Mumbai-only configuration - no hardcoded coords elsewhere.
Per AGENTS: centralized config, single source of truth for Mumbai region.
All coords/bbox come from env or this file, never hardcoded in connectors/tools/agents.
Docker data on D: (volumes), Docker Desktop binary on C: - verified via docker-compose.yml volumes.
"""
import os
from typing import Tuple, List

# Mumbai Region - env overrideable, no hardcoding in business logic
# bbox: [min_lon, min_lat, max_lon, max_lat] EPSG:4326 - Mumbai Metropolitan + Raigad coast
# Extended covers Maharashtra coastal belt for OSF/Waves/Currents
def _parse_bbox(env_val: str, default: List[float]) -> List[float]:
    if not env_val:
        return default
    try:
        parts = [float(x.strip()) for x in env_val.split(",")]
        if len(parts) == 4:
            return parts
    except: pass
    return default

MUMBAI_BBOX = _parse_bbox(os.getenv("MUMBAI_BBOX", ""), [72.2, 18.5, 73.2, 19.5])
MUMBAI_EXTENDED_BBOX = _parse_bbox(os.getenv("MUMBAI_EXTENDED_BBOX", ""), [71.8, 15.5, 74.5, 20.5])
MUMBAI_POINT: Tuple[float, float] = (19.076, 72.877)  # lat, lon - Gateway of India fallback
def _parse_point(env_val: str) -> Tuple[float, float]:
    if not env_val: return MUMBAI_POINT
    try:
        lat_s, lon_s = env_val.split(",")
        return (float(lat_s.strip()), float(lon_s.strip()))
    except: return MUMBAI_POINT
MUMBAI_POINT = _parse_point(os.getenv("MUMBAI_POINT", ""))

MUMBAI_STATE = os.getenv("MUMBAI_STATE", "Maharashtra")
MUMBAI_EEZ_FILTER = os.getenv("MUMBAI_GEO_FILTER", "Mumbai")  # for EEZ/WDPA API keyword

# Provider endpoints - env overrideable, no hardcoded URLs in connectors
INCOIS_PFZ_WMS = os.getenv("INCOIS_PFZ_WMS", "https://www.incois.gov.in/MarineFisheries/PfzWebGis")
INCOIS_OSF_API = os.getenv("INCOIS_OSF_API", "https://incois.gov.in/oceanservices/osfforecast.jsp")
INCOIS_GEO_PORTAL = os.getenv("INCOIS_GEO_PORTAL", "https://incois.gov.in/geoportal/MFASPFZ")
MARINE_REGIONS_WFS = os.getenv("MARINE_REGIONS_WFS", "https://marineregions.org/api")
WDPA_API = os.getenv("WDPA_API", "https://api.protectedplanet.net/v3/protected_areas")
GEBCO_WCS = os.getenv("GEBCO_WCS", "https://www.gebco.net/data-products/bathymetry")
COPERNICUS_DATASET_PHYS = os.getenv("COPERNICUS_DATASET_PHYS", "cmems_mod_glo_phy_my_0.083deg_P1D-m")
COPERNICUS_DATASET_WAVE = os.getenv("COPERNICUS_DATASET_WAVE", "cmems_mod_glo_wav_my_0.2deg_P3H")
GFW_API = os.getenv("GFW_API", "https://api.globalfishingwatch.org/v2")
IMD_API = os.getenv("IMD_API", "https://city.imd.gov.in/api")
OPEN_METEO_API = os.getenv("OPEN_METEO_API", "https://api.open-meteo.com/v1/forecast")

def point_within_mumbai(lat: float, lon: float) -> bool:
    return MUMBAI_BBOX[1] <= lat <= MUMBAI_BBOX[3] and MUMBAI_BBOX[0] <= lon <= MUMBAI_BBOX[2]

def bbox_str(bbox: List[float] = None) -> str:
    b = bbox or MUMBAI_BBOX
    return f"{b[0]},{b[1]},{b[2]},{b[3]}"
