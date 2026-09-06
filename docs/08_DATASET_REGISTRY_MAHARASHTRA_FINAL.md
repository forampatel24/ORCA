# ORCA — Dataset Registry — Maharashtra Final (Frozen)

**Project:** ORCA  
**Document:** Dataset Registry — Maharashtra State (Mumbai + Maharashtra Coastline)  
**Document ID:** ORCA-DATA-08-MH  
**Version:** 2.0 — Maharashtra Final  
**Status:** FROZEN — Source of Truth for all M13+ implementation  
**Date:** 2026-09-06  
**Coverage:** Maharashtra State coastline — bbox `71.8,15.5,74.5,20.5` (extended) + Mumbai bbox `72.2,18.5,73.2,19.5` — all 8 categories below are filtered to this bbox. No global downloads.  
**Note:** IMD removed per owner decision. INCOIS is primary Indian marine source, Open-Meteo for weather, ISRO/MOSDAC, Copernicus, GEBCO, Marine Regions, GFW, FAO/OBIS as mapped. All links are public (no hard-coded secrets).

This document replaces the generic `08_DATASET_REGISTRY.md:4` for implementation. Every connector/tool must filter to Maharashtra bbox via `app/config/mumbai.py:22` `MUMBAI_BBOX / MUMBAI_EXTENDED_BBOX` (env override `MUMBAI_BBOX`, `MUMBAI_STATE=Maharashtra`).

---

## 1. Oceanographic Data

| Sub-domain | Data needed | Source | Link |
|---|---|---|---|
| SST | Current SST, SST anomaly, historical SST | INCOIS / Copernicus Marine | INCOIS OSF · Copernicus Marine |
| Chlorophyll-a | Concentration, anomaly, spatial distribution | INCOIS / ISRO MOSDAC / Copernicus | INCOIS OSF · ISRO MOSDAC |
| PFZ | PFZ coordinates, advisory, validity, fishing-zone information | INCOIS | INCOIS PFZ Advisory · INCOIS PFZ WebGIS |
| Ocean Currents | Speed, direction, surface/depth-wise currents | INCOIS / Copernicus | INCOIS OSF · Copernicus Marine |
| Waves | Significant height, direction, period, swell height/direction/period | INCOIS | INCOIS Wave Forecast |
| Tides | High/low tide, tide height, tidal current | INCOIS / Open-Meteo Marine | INCOIS Ocean Services · Open-Meteo Marine |
| Sea Level | Sea-surface height, anomaly, coastal water level | INCOIS / Copernicus | INCOIS General Circulation · Copernicus Marine |
| Salinity | Surface/depth-wise salinity | INCOIS / Copernicus | INCOIS General Circulation · Copernicus Marine |
| Bathymetry | Sea depth, seabed elevation, depth contours | GEBCO | GEBCO Bathymetry |
| Ocean Forecasts | Forecast SST, currents, waves, tides, etc. | INCOIS / Copernicus / Open-Meteo Marine | INCOIS OSF · Copernicus Marine · Open-Meteo Marine |
| Historical Ocean Data | Historical SST, chlorophyll, currents, waves, etc. | Copernicus / INCOIS / MOSDAC | Copernicus Marine · MOSDAC |
| Marine Ecosystem/Fisheries | Fish distribution, seasonality, historical fishing grounds/catch | FAO / OBIS / GFW | FAO Fisheries Statistics · Global Fishing Watch |

**Storage:** `PostgreSQL ocean_observations (sst, chlorophyll, wave_height…)` + `MinIO orca-raster/*.nc/*.tif` + `PostGIS geometry` — connector `backend/app/services/ingestion/connectors/ocean_connector.py:28` bbox filtered.

---

## 2. Weather & Atmospheric Data

| Sub-domain | Data needed | Source | Link |
|---|---|---|---|
| Wind | Wind speed, direction, gust | Open-Meteo | Open-Meteo Weather API |
| Rainfall | Intensity, probability, accumulation | Open-Meteo | Open-Meteo Weather API |
| Temperature | Air temperature, apparent/feels-like temperature | Open-Meteo | Open-Meteo Weather API |
| Humidity | Relative humidity | Open-Meteo | Open-Meteo Weather API |
| Pressure | Atmospheric/sea-level pressure | Open-Meteo | Open-Meteo Weather API |
| Visibility | Visibility distance, fog conditions | Open-Meteo | Open-Meteo Weather API |
| Clouds | Cloud cover, cloud conditions | Open-Meteo | Open-Meteo Weather API |
| Thunderstorm | Probability/forecast conditions | Open-Meteo | Open-Meteo Weather API |
| Lightning | Lightning probability/density where available | Open-Meteo / satellite products | Open-Meteo · MOSDAC |
| Cyclones | Location, track, intensity, category, forecast track, wind radius | RSMC New Delhi / INCOIS | RSMC New Delhi · INCOIS |
| Storm Surge | Surge height, affected coastal areas | INCOIS / ITEWC | INCOIS Tsunami & Storm Surge System |
| Weather Alerts | Active warnings, severity, region, validity | Official warning feeds / RSMC | RSMC New Delhi |
| Weather Forecast | Hourly/daily forecast | Open-Meteo | Open-Meteo Weather API |

**Storage:** `weather_observations` + `marine_hazards` — `weather_connector.py:46` point `19.076,72.877` `point_within_mumbai()`.

---

## 3. Marine Advisories & Safety

| Sub-domain | Data needed | Source | Link |
|---|---|---|---|
| Fisheries Advisories | Fishing advisories, recommended areas/times | INCOIS | INCOIS Marine Fisheries |
| PFZ Advisories | PFZ coordinates, advisory, validity | INCOIS | INCOIS PFZ Advisory |
| Weather Advisories | Weather/marine warnings | RSMC / official warning sources | RSMC New Delhi |
| Cyclone Advisories | Cyclone warnings, landfall, affected areas | RSMC New Delhi | RSMC New Delhi |
| High-Wave Alerts | High-wave warning, height, validity | INCOIS | INCOIS OSF |
| Rough-Sea Alerts | Dangerous sea-state information | INCOIS | INCOIS OSF |
| Thunderstorm/Lightning Alerts | Affected area, severity, timing | Open-Meteo + satellite/official feeds | Open-Meteo · MOSDAC |
| Tsunami Alerts | Warning, affected coastline, arrival time | INCOIS ITEWC | INCOIS Tsunami Warning System |
| Coastal Alerts | Flooding, surge, abnormal sea level | INCOIS / ITEWC | INCOIS ITEWS |
| Fishing Bans/Restrictions | Seasonal bans, prohibited periods | State/central fisheries departments | Official state fisheries portals |
| Navigation Warnings | Navigational hazards/restrictions | Indian maritime/port authorities | Official maritime/port notices |
| Safety Notices | Fishermen safety procedures | INCOIS / Government | INCOIS |
| Advisory Metadata | Source, issue/expiry, geography, severity | Same source | Store internally in ORCA |

**Storage:** Text advisories → `data/knowledge/marine_advisories/*.txt` → `Qdrant orca_knowledge` + `PostgreSQL alerts`. Example `data/knowledge/marine_advisories/incois_advisory_2026.txt:1`.

---

## 4. Geospatial / GIS

| Sub-domain | Data needed | Source | Link |
|---|---|---|---|
| User/Vessel Location | GPS lat/lon/time | Device GPS / AIS / GFW | Global Fishing Watch API |
| Marine Boundaries | EEZ, territorial waters, maritime boundaries | Marine Regions | Marine Regions Downloads |
| Coastline | Coastline geometry | OpenStreetMap / Natural Earth | OpenStreetMap · Natural Earth |
| Fishing Zones | PFZ polygons/points | INCOIS | INCOIS PFZ WebGIS |
| Restricted Zones | No-fishing/prohibited areas | Government fisheries / Marine Regions | Marine Regions |
| Marine Protected Areas | MPA boundaries | Protected Planet / WDPA | Protected Planet WDPA |
| Navigation Zones | Shipping lanes/corridors | OpenStreetMap / maritime authorities | OpenStreetMap |
| Ports | Port coordinates/boundaries | OpenStreetMap / official port data | OpenStreetMap |
| Islands | Locations/boundaries | Natural Earth / OSM | Natural Earth |
| Bathymetric Zones | Depth contours/seabed regions | GEBCO | GEBCO |
| Hazard Zones | Cyclone/wave/storm/flood polygons | INCOIS / official hazard products | INCOIS |
| Geofences | Safety/restricted boundaries | ORCA-generated from GIS data | — |
| Distance Data | Vessel–PFZ/port/hazard distance | ORCA + PostGIS | — |
| Spatial Relationships | Contains/intersects/overlaps/nearest | ORCA + PostGIS | — |
| Map Layers | Ocean/weather/hazard/boundary layers | Combination of above sources | — |

**Storage:** `PostGIS maritime_boundaries / protected_areas / geofences` `ST_Intersects(ST_MakeEnvelope(71.8,15.5,74.5,20.5,4326))` — `scripts/ingest_m7_mumbai.py:34` + `backend/app/tools/geospatial.py:13`.

---

## 5. Vessel / Fishing Activity

| Sub-domain | Data needed | Source | Link |
|---|---|---|---|
| Vessel Identity | Vessel ID, type, size/category | Global Fishing Watch | GFW API |
| Vessel Position | Lat/lon/timestamp | Global Fishing Watch / AIS | GFW API |
| Movement | Speed, heading, course | AIS / GFW | GFW API |
| Track History | Historical vessel routes | GFW | GFW API |
| Fishing Activity | Fishing location/duration/activity | GFW | GFW API |
| Trip Information | Departure/destination/duration | GFW / user-provided | GFW API |
| Fuel/Range | Fuel consumption/range | User-provided vessel data | — |
| Vessel Capability | Size, operating range, suitable conditions | User/fisheries registry | — |
| Historical Catch | Species, quantity, location, date | FAO / fisheries datasets | FAO Fishery Statistics |
| Fishing Effort | Time/area/trip fishing effort | Global Fishing Watch | GFW API |

**Storage:** `PostgreSQL vessel_tracks` (future) — `GFW_API=https://api.globalfishingwatch.org/v2` `app/config/mumbai.py:45` bbox filtered.

---

## 6. Fisheries / Biological Data

| Sub-domain | Data needed | Source | Link |
|---|---|---|---|
| Fish Species | Species, habitat, taxonomy | OBIS / FAO | OBIS · FAO Fisheries |
| Fish Distribution | Geographic distribution | OBIS | OBIS |
| Fish Seasonality | Seasonal availability/migration | FAO + scientific datasets | FAO Fisheries |
| Historical Catch | Species + location + time + quantity | FAO FishStat | FAO FishStat |
| Fishing Grounds | Known productive areas | INCOIS PFZ + GFW | INCOIS PFZ · GFW |
| Environmental Preferences | Preferred SST/depth/salinity/chlorophyll | Scientific literature + OBIS/FAO | OBIS |
| Species Migration | Migration routes/patterns | OBIS + research datasets | OBIS |
| Catch Trends | Historical productivity trends | FAO FishStat | FAO FishStat |

**Storage:** `cmfri_landings` `data/external/cmfri_landings.csv` + `RAG` for species docs — `Protected Planet WDPA` style.

---

## 7. Satellite / Earth Observation

| Sub-domain | Data needed | Source | Link |
|---|---|---|---|
| Satellite SST | SST imagery/products | ISRO EOS-06 / MOSDAC | MOSDAC EOS-06 |
| Ocean Colour | Ocean-colour reflectance | ISRO OCM-3 / MOSDAC | MOSDAC EOS-06 |
| Chlorophyll-a | Satellite chlorophyll | ISRO OCM-3 / INCOIS | MOSDAC EOS-06 |
| SAR | Vessel/ocean/coastal radar imagery | ISRO / external EO sources | MOSDAC |
| Optical Imagery | Coastal/ocean imagery | ISRO/MOSDAC | MOSDAC |
| Cloud Data | Cloud cover/masking | MOSDAC satellite products | MOSDAC |
| Remote Sensing Products | Derived ocean/geospatial parameters | MOSDAC / INCOIS | MOSDAC · INCOIS |
| Historical Imagery | Time-series satellite observations | MOSDAC / Copernicus | MOSDAC · Copernicus Marine |

**Storage:** `MinIO orca-satellite / orca-raster/*.tif` + `data/processed/bathymetry_mumbai_subset.tif` — Mumbai subset only, not 4GB global `ingest_m7_mumbai.py:82`.

---

## 8. Knowledge / Reference Data

| Sub-domain | Data needed | Source | Link |
|---|---|---|---|
| Marine Regulations | Fishing/maritime regulations | Government / FAO / IMO | FAO Fisheries · IMO |
| Fishing Regulations | Species/gear/season restrictions | Central & State Fisheries Departments | Official fisheries portals |
| Safety Guidelines | Fishermen safety procedures | INCOIS / Government | INCOIS |
| Navigation Rules | Maritime/navigation rules | IMO / Indian maritime authorities | IMO |
| Government Documents | Marine/fisheries documents | Government portals | Official portals |
| Scientific Literature | Marine/fisheries research | OpenAlex / Crossref / PubMed / papers | OpenAlex |
| Technical Documentation | Dataset/API/product documentation | Individual providers | Provider documentation |
| Historical Advisories | Previous warnings/advisories | INCOIS / official portals | INCOIS |
| Regional Knowledge | Region-specific fishing/marine knowledge | INCOIS + fisheries departments + research | INCOIS |

**Storage:** **RAG only** `data/knowledge/**` → `MaxIO orca-documents` → `PyMuPDF` → `chunk 700/100` → `FastEmbed BGE-small-en-v1.5 384` → `Qdrant orca_knowledge` → `knowledge_documents/chunks`. Current `4 docs 6 chunks`: `safety/*` + `marine_advisories/incois_advisory_2026.txt:1` + `pfz_advisory_2026.pdf`. Adding a file to `data/knowledge/` + `ingest_knowledge()` auto-indexes. Filter `region=mumbai` `backend/app/rag/ingestion.py:100`.

---

## 9. Implementation Rule — Maharashtra Only

All connectors must:

1. Read `MUMBAI_BBOX / MUMBAI_EXTENDED_BBOX / MUMBAI_STATE=Maharashtra` from `app/config/mumbai.py:22` (env `MUMBAI_BBOX=71.8,15.5,74.5,20.5`)
2. Validate `point_within_mumbai(lat,lon)` or `ST_Within / ST_Intersects(ST_MakeEnvelope(...))`
3. Store provenance `source/provider/bbox/timestamp` per `09_DATA_PIPELINE`
4. Never download global 4GB GEBCO/Copernicus — subset Mumbai/Maharashtra only via API bbox param.

Friend clone: `cp .env.example .env` + `cp .env.example backend/.env` already has `MUMBAI_BBOX=72.2,18.5,73.2,19.5` + `MUMBAI_EXTENDED_BBOX=71.8,15.5,74.5,20.5` + `MUMBAI_STATE=Maharashtra` — change to `71.8,15.5,74.5,20.5` in both files to expand to full Maharashtra coast without code change.

---

*End — This table is the frozen contract for ORCA Maharashtra. Any deviation requires owner approval.*
