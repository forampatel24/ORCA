# ORCA — Dataset Registry

**Project Name:** ORCA  
**Document:** Dataset Registry  
**Document ID:** ORCA-DATA-08  
**Version:** 1.0  
**Status:** FROZEN BASELINE  
**Scope:** External Data Sources, Dataset Mapping, Variables, Formats, Storage and Agent Usage

---

# 1. Purpose

This document defines the external datasets and data-source families used by ORCA.

The registry answers:

- What data does ORCA need?
- Which provider/source supplies it?
- What variables are available?
- Is the source static, historical, forecast or near-real-time?
- What format does the source provide?
- Where is the data stored?
- Which ORCA agent consumes it?
- What analytical capabilities does it enable?

---

# 2. Important Principle

ORCA does not depend on one dataset.

The platform integrates multiple independent sources:

```text
Marine
Weather
Ocean
Satellite
Geospatial
Hazards
Knowledge
        ↓
ORCA Data Layer
````

A source can be replaced by another compatible source without redesigning the entire application.

---

# 3. Source Categories

The ORCA registry contains:

| Category          | Primary Purpose                     |
| ----------------- | ----------------------------------- |
| PFZ               | Potential Fishing Zone intelligence |
| Ocean Colour      | Chlorophyll / productivity          |
| SST               | Sea Surface Temperature             |
| Waves             | Sea-state safety                    |
| Currents          | Ocean movement / routing            |
| Tides             | Tidal conditions                    |
| Weather           | Atmospheric conditions              |
| Lightning         | Lightning safety                    |
| Cyclones          | Severe-weather safety               |
| Marine Boundaries | Geofencing                          |
| Protected Areas   | Fishing restrictions                |
| Bathymetry        | Ocean depth                         |
| Ports             | Coastal infrastructure              |
| Advisories        | Official marine guidance            |
| Knowledge         | RAG and evidence                    |

---

# 4. PFZ Data

## Primary Purpose

Potential Fishing Zone identification.

PFZ information is a core ORCA capability.

---

## Required Information

```text
PFZ location
Date
Time
Geometry / coordinates
Zone information
Source
Observation period
```

---

## Primary Use

```text
Nearest PFZ
PFZ ranking
Fishing-zone recommendation
PFZ visualization
PFZ + ocean correlation
PFZ + weather correlation
```

---

## Consuming Agents

```text
Marine Data Agent
Geospatial Agent
Ocean Analytics Agent
Risk Agent
Routing Agent
Visualization Agent
```

---

# 5. Ocean Colour / Chlorophyll Data

## Purpose

Marine productivity intelligence.

Required variable:

```text
Chlorophyll-a
```

Potential source families include satellite ocean-colour products.

---

## Uses

```text
Productivity analysis
PFZ correlation
Historical comparison
Fishing-zone ranking
Marine ecosystem analysis
```

---

## Processing

Typical flow:

```text
Satellite Product
       ↓
Raw Raster
       ↓
Quality Filtering
       ↓
Spatial Extraction
       ↓
Chlorophyll Value
       ↓
ORCA Analytics
```

---

# 6. Sea Surface Temperature Data

## Purpose

SST-based marine intelligence.

Required variables:

```text
SST
Latitude
Longitude
Time
Quality / confidence information where available
```

---

## Uses

```text
Fishing-zone analysis
Ocean-condition analysis
Historical trends
SST anomaly detection
PFZ correlation
```

---

# 7. Wave Data

## Purpose

Marine safety and route analysis.

Required variables:

```text
Significant Wave Height
Wave Period
Wave Direction
Swell Height
Swell Direction
Timestamp
Location
```

---

## Uses

```text
Safety assessment
Route scoring
Hazard detection
Forecast comparison
```

---

# 8. Ocean Current Data

## Purpose

Oceanographic analysis and route optimization.

Required variables:

```text
Current speed
Current direction
Latitude
Longitude
Time
Depth where available
```

---

## Uses

```text
Route optimization
Marine-condition analysis
Ocean intelligence
Operational planning
```

---

# 9. Tide Data

## Purpose

Tidal intelligence.

Required:

```text
Tide height
High tide
Low tide
Prediction time
Location
```

---

## Uses

```text
Navigation context
Operational planning
Safety analysis
Route planning
```

---

# 10. Weather Data

Weather data is one of ORCA's most important operational sources.

Required variables may include:

```text
Temperature
Wind speed
Wind direction
Wind gust
Rainfall
Humidity
Pressure
Cloud cover
Visibility
Forecast timestamp
```

---

## Uses

```text
Marine safety
Route optimization
Weather forecasting
Hazard detection
Operational planning
```

---

# 11. Lightning Data

## Purpose

Lightning hazard detection.

Required information:

```text
Latitude
Longitude
Timestamp
Intensity where available
Confidence where available
```

---

## Uses

```text
Lightning proximity
Fishing-zone safety
Route safety
Proactive alerts
```

---

# 12. Cyclone Data

## Purpose

Cyclone monitoring and safety.

Required information:

```text
Cyclone name
Center position
Timestamp
Forecast position
Wind speed
Pressure
Category
Forecast track
Warning area
```

---

## Uses

```text
Cyclone alerts
Risk assessment
Route avoidance
Hazard visualization
Regional safety analysis
```

---

# 13. Marine Advisories

ORCA should ingest official marine and weather advisories where technically accessible.

Examples of information:

```text
Advisory type
Affected region
Issue time
Valid from
Valid until
Severity
Description
Source
```

---

## Uses

```text
Risk assessment
Safety recommendation
Alerts
RAG evidence
Final reporting
```

Official advisories should receive higher trust than unofficial information.

---

# 14. Maritime Boundary Data

## Purpose

Geofencing.

Required geometry:

```text
Polygon / MultiPolygon
```

Metadata:

```text
Boundary name
Boundary type
Source
Effective period
Description
```

---

## Uses

```text
Boundary proximity
Restricted-area detection
Route validation
Alerts
```

---

# 15. Marine Protected Area Data

## Purpose

Identify protected and environmentally sensitive areas.

Required:

```text
Area name
Geometry
Restriction type
Authority
Description
Effective period
```

---

## Uses

```text
Geofencing
Route restriction
Fishing restriction
Environmental awareness
```

---

# 16. Bathymetry Data

## Purpose

Ocean depth information.

Required:

```text
Latitude
Longitude
Depth
```

---

## Uses

```text
Navigation context
Route analysis
Marine intelligence
Fishing-zone context
```

Bathymetry is comparatively static and does not need the same refresh frequency as weather or hazards.

---

# 17. Ports and Coastal Infrastructure

Potential entities:

```text
Fishing harbours
Commercial ports
Emergency facilities
Lighthouses
Coastal settlements
```

Required:

```text
Name
Latitude
Longitude
Type
Operational information where available
```

---

## Uses

```text
Nearest harbour
Emergency planning
Route planning
Navigation context
```

---

# 18. Historical Datasets

ORCA should retain historical observations wherever available.

Examples:

```text
Historical PFZ
Historical SST
Historical Chlorophyll
Historical Weather
Historical Waves
Historical Currents
Historical Hazards
```

---

## Purpose

Historical data enables:

```text
Trend analysis
Anomaly detection
Seasonal analysis
Productivity analysis
Historical comparison
```

---

# 19. Scientific Knowledge Corpus

The RAG layer requires documents rather than only numerical datasets.

Potential document classes:

```text
Marine science documents
Fisheries research
Oceanographic documentation
Safety guidelines
Marine advisories
Government publications
Regulations
Technical documentation
Scientific papers
```

---

# 20. RAG Document Storage

The document pipeline is:

```text
Document
   ↓
MinIO
   ↓
Text Extraction
   ↓
Cleaning
   ↓
Chunking
   ↓
Embedding
   ↓
Qdrant
```

Metadata remains associated with the source document.

---

# 21. Dataset Format Registry

ORCA must support multiple formats.

```text
CSV
JSON
GeoJSON
GeoTIFF
NetCDF
HDF
Parquet
PDF
API JSON responses
```

---

# 22. Format-to-Storage Mapping

| Format       | Typical Destination                   |
| ------------ | ------------------------------------- |
| CSV          | PostgreSQL / MinIO                    |
| JSON         | PostgreSQL / MinIO                    |
| GeoJSON      | PostGIS / MinIO                       |
| GeoTIFF      | MinIO                                 |
| NetCDF       | MinIO                                 |
| HDF          | MinIO                                 |
| Parquet      | MinIO                                 |
| PDF          | MinIO                                 |
| API Response | PostgreSQL / Redis / processing layer |

---

# 23. Storage Mapping

```text
                 ORCA DATA
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
 PostgreSQL        MinIO         Qdrant
       │             │             │
    PostGIS       Raw Files     Embeddings
       │             │             │
       └─────────────┼─────────────┘
                     │
                   Redis
                  (Cache)
```

---

# 24. PostgreSQL Data

PostgreSQL stores structured operational data.

Examples:

```text
PFZ records
Weather observations
Ocean measurements
Hazard metadata
Dataset metadata
Source registry
Agent execution metadata
User data
Conversation data
Alert records
```

---

# 25. PostGIS Data

PostGIS stores spatially queryable information.

Examples:

```text
PFZ geometry
Hazard polygons
Protected areas
Maritime boundaries
Ports
Coastlines
Routes
Vessel locations
Spatial indexes
```

---

# 26. MinIO Data

MinIO stores large objects.

Examples:

```text
Satellite rasters
GeoTIFF
NetCDF
HDF
Parquet
Original PDFs
Original datasets
Processed files
Dataset snapshots
```

---

# 27. Qdrant Data

Qdrant stores vector embeddings for semantic retrieval.

Examples:

```text
Marine documents
Safety guidelines
Regulations
Scientific papers
Advisories
Technical documentation
```

Qdrant is not the primary storage for numerical marine observations.

---

# 28. Redis Data

Redis is a temporary/high-speed data layer.

Examples:

```text
API cache
Weather cache
Frequently requested PFZ results
Session state
Short-lived agent state
Rate limiting
Task coordination where required
```

Redis should not be treated as the permanent source of truth.

---

# 29. Dataset Registry Table

The backend should maintain a logical registry similar to:

```text
data_sources
```

Fields:

```text
id
name
provider
category
description
endpoint
format
variables
coverage
spatial_resolution
temporal_resolution
update_frequency
license
status
last_updated
```

---

# 30. Dataset Availability

Every source should expose a status.

```text
AVAILABLE
DEGRADED
UNAVAILABLE
STALE
```

The system should use this information when planning tasks.

---

# 31. Dataset Freshness

Example policy:

```text
Real-time sources
    ↓
Refresh frequently

Forecast sources
    ↓
Refresh according to forecast update cycle

Daily satellite/PFZ products
    ↓
Refresh daily

Static geospatial data
    ↓
Refresh periodically

Scientific documents
    ↓
Refresh when source corpus changes
```

---

# 32. Spatial Coverage

Every dataset should record:

```text
minimum latitude
maximum latitude
minimum longitude
maximum longitude
```

or equivalent geometry.

This allows ORCA to determine whether a source can answer a particular query.

---

# 33. Temporal Coverage

Every dataset should record:

```text
start_time
end_time
```

and, where applicable:

```text
forecast_start
forecast_end
```

---

# 34. Dataset Selection

The Orchestrator should select datasets based on:

```text
User intent
Location
Time
Required variables
Spatial coverage
Temporal coverage
Freshness
Availability
Source reliability
```

---

# 35. Example Dataset Selection

User:

> "Is it safe to fish tomorrow morning?"

Required:

```text
Weather forecast
Wind
Wave forecast
Lightning
Cyclone
Tide
Marine advisories
Geospatial restrictions
```

Not every available dataset needs to be queried.

---

# 36. Example PFZ Selection

User:

> "Where is the nearest PFZ today?"

Required:

```text
PFZ
User location
Geospatial boundaries
```

Optional supporting information:

```text
SST
Chlorophyll
Ocean conditions
```

---

# 37. Example Productivity Selection

User:

> "Why has productivity declined?"

Required:

```text
Historical PFZ
Historical chlorophyll
Historical SST
Ocean conditions
Historical observations
```

The system may add other relevant datasets depending on availability.

---

# 38. Data Correlation Keys

Cross-dataset correlation may use:

```text
Latitude
Longitude
Geometry
Timestamp
Forecast timestamp
Region
Dataset ID
Observation ID
```

The system should align observations spatially and temporally before comparison.

---

# 39. Spatial Correlation

Example:

```text
PFZ
  +
SST
  +
Chlorophyll
```

All observations are transformed into compatible spatial representations.

Then:

```text
Spatial Join
      ↓
Relevant Measurements
```

---

# 40. Temporal Correlation

Example:

```text
PFZ observation:
10:00

SST:
09:30

Weather:
10:00

Wave forecast:
10:00
```

ORCA should apply an explicit temporal matching policy rather than assuming all values are simultaneous.

---

# 41. Data Reliability

Source reliability should be represented explicitly.

Example:

```text
source_reliability
```

Possible levels:

```text
OFFICIAL
TRUSTED
SECONDARY
UNKNOWN
```

This should influence evidence presentation.

---

# 42. Data Provenance

Each analytical result should retain:

```text
Source
Dataset
Timestamp
Processing version
Spatial extent
Variable
```

This supports explainability.

---

# 43. Dataset Processing Pipeline

```text
External Source
      ↓
Source Connector
      ↓
Download / API Request
      ↓
Raw Validation
      ↓
Raw Storage
      ↓
Transformation
      ↓
Quality Control
      ↓
Normalization
      ↓
PostgreSQL / PostGIS
      ↓
Analytics
      ↓
Agent Tools
```

---

# 44. Satellite Processing Pipeline

```text
Satellite Product
       ↓
MinIO
       ↓
Raster / Scientific Data Reader
       ↓
Quality Filtering
       ↓
Coordinate Validation
       ↓
Spatial Processing
       ↓
Derived Layer
       ↓
PostGIS / Analytical Store
       ↓
Ocean Analytics Agent
```

---

# 45. Document Processing Pipeline

```text
PDF / Document
      ↓
MinIO
      ↓
Text Extraction
      ↓
Cleaning
      ↓
Chunking
      ↓
Metadata Association
      ↓
Embedding Model
      ↓
Qdrant
      ↓
RAG Agent
```

---

# 46. Data Update Architecture

```text
Scheduler
   ↓
Check Source
   ↓
New Data?
 ┌─┴─┐
No  Yes
│    │
│    ▼
│  Ingest
│    ↓
│ Validate
│    ↓
│ Process
│    ↓
└──> Store
```

---

# 47. Failed Ingestion

If ingestion fails:

```text
Source Error
     ↓
Retry
     ↓
Still Failed?
     ↓
Mark Source DEGRADED
     ↓
Use Previous Valid Data
     ↓
Reduce Confidence
     ↓
Inform Agent
```

The system must never silently treat stale data as current.

---

# 48. Dataset Versioning

Where practical, datasets should retain:

```text
Dataset Version
Ingestion Timestamp
Source Timestamp
Processing Version
```

This enables reproducibility.

---

# 49. Dataset-to-Agent Matrix

| Dataset         | Marine | Weather | Ocean | Geo | Risk | Routing | RAG | Alert |
| --------------- | -----: | ------: | ----: | --: | ---: | ------: | --: | ----: |
| PFZ             |      ✓ |         |     ✓ |   ✓ |    ✓ |       ✓ |     |       |
| Chlorophyll     |      ✓ |         |     ✓ |     |    ✓ |         |     |       |
| SST             |      ✓ |         |     ✓ |     |    ✓ |         |     |       |
| Waves           |        |         |     ✓ |     |    ✓ |       ✓ |     |     ✓ |
| Currents        |        |         |     ✓ |     |    ✓ |       ✓ |     |       |
| Tide            |        |         |     ✓ |     |    ✓ |       ✓ |     |     ✓ |
| Weather         |        |       ✓ |       |     |    ✓ |       ✓ |     |     ✓ |
| Lightning       |        |       ✓ |       |     |    ✓ |       ✓ |     |     ✓ |
| Cyclone         |        |       ✓ |       |   ✓ |    ✓ |       ✓ |     |     ✓ |
| Boundaries      |        |         |       |   ✓ |    ✓ |       ✓ |     |     ✓ |
| Protected Areas |        |         |       |   ✓ |    ✓ |       ✓ |     |     ✓ |
| Bathymetry      |        |         |     ✓ |   ✓ |    ✓ |       ✓ |     |       |
| Advisories      |        |       ✓ |     ✓ |     |    ✓ |       ✓ |   ✓ |     ✓ |
| Scientific Docs |        |         |     ✓ |     |      |         |   ✓ |       |
| Regulations     |        |         |       |   ✓ |    ✓ |       ✓ |   ✓ |       |

---

# 50. Minimum Viable Data Layer

The initial implementation should prioritize:

```text
1. PFZ
2. SST
3. Chlorophyll
4. Weather
5. Wind
6. Waves
7. Cyclone / hazard information
8. Maritime / protected-area boundaries
9. Marine advisories
10. Knowledge documents
```

These provide the strongest foundation for demonstrating ORCA's core intelligence.

---

# 51. Full Production Data Layer

The complete architecture supports:

```text
PFZ
SST
Chlorophyll
Waves
Currents
Tides
Weather
Wind
Rainfall
Lightning
Cyclones
Marine Hazards
Bathymetry
Maritime Boundaries
Protected Areas
Ports
Historical Observations
Marine Advisories
Scientific Documents
Safety Guidelines
Regulations
```

---

# 52. Important Separation

Datasets and databases are different things.

```text
DATABASES
─────────
PostgreSQL
PostGIS
Qdrant
Redis
MinIO
```

These are infrastructure components.

```text
DATASETS / SOURCES
──────────────────
PFZ
SST
Chlorophyll
Weather
Waves
Cyclones
Boundaries
Advisories
etc.
```

These are information sources consumed by ORCA.

---

# 53. Final Data Architecture

```text
                         DATA SOURCES
                              │
      ┌───────────┬───────────┼───────────┬───────────┐
      │           │           │           │           │
    MARINE      OCEAN      WEATHER    SATELLITE   GEOSPATIAL
      │           │           │           │           │
      └───────────┴───────────┼───────────┴───────────┘
                              │
                         INGESTION
                              │
                         VALIDATION
                              │
                        NORMALIZATION
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
       PostgreSQL           MinIO            Qdrant
            │                 │                 │
         PostGIS              │             RAG Data
            │                 │
            └─────────────────┘
                      │
                    Redis
                   (Cache)
                      │
                      ▼
                 AGENT TOOLS
                      │
                      ▼
                MULTI-AGENT ORCA
```

---

# 54. Frozen Dataset Principle

The architecture is frozen around **data capabilities**, not hard-coded dependence on a single provider.

Therefore:

```text
SOURCE CAN CHANGE
       ↓
CONNECTOR CHANGES
       ↓
NORMALIZED DATA MODEL REMAINS
       ↓
AGENTS REMAIN
       ↓
ORCA ARCHITECTURE REMAINS
```

This makes ORCA extensible and production-oriented.
